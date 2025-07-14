# -*- coding: utf-8 -*-
"""
주기적 실행 관리자

주기적 실행 기능의 핵심 로직을 담당하는 모듈
- 스케줄링 관리
- 순차 실행 워크플로우
- 계정별 독립 프로세스 실행
"""

import os
import sys
import time
import threading
import subprocess
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Callable

try:
    import schedule
except ImportError:
    print("Warning: schedule 라이브러리가 설치되지 않았습니다. 내장 스케줄러를 사용합니다.")
    schedule = None

# 내장 스케줄러 import
from .simple_scheduler import SimpleScheduler

# 계정 매핑 함수 import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from batch.batch_manager import get_real_account_id

# 로깅 설정
logger = logging.getLogger(__name__)

class ScheduleManager:
    """스케줄링 관리 클래스"""
    
    def __init__(self):
        self.scheduler_thread = None
        self.is_running = False
        self.callback_function = None
        self.is_callback_running = False  # 콜백 실행 상태 추적
        self.last_execution_time = None   # 마지막 실행 시간 추적
        
        # schedule 라이브러리가 없으면 내장 스케줄러 사용
        if schedule is None:
            self.simple_scheduler = SimpleScheduler()
        else:
            self.simple_scheduler = None
        
    def start_daily_schedule(self, time_str: str, callback: Callable):
        """매일 지정된 시간에 실행되는 스케줄 시작
        
        Args:
            time_str: 실행 시간 (예: "09:00")
            callback: 실행할 콜백 함수
        """
        try:
            # 안전한 콜백 래퍼 생성 (중복 실행 방지)
            def safe_callback():
                from datetime import datetime
                
                # 이미 실행 중인지 확인
                if self.is_callback_running:
                    logger.warning("이전 주기적 실행이 아직 진행 중입니다. 중복 실행을 방지합니다.")
                    return
                
                # 최근 실행 시간 확인 (1시간 이내 중복 실행 방지)
                current_time = datetime.now()
                if self.last_execution_time:
                    time_diff = current_time - self.last_execution_time
                    if time_diff.total_seconds() < 3600:  # 1시간
                        logger.warning(f"최근 실행 후 {time_diff.total_seconds():.0f}초 경과. 중복 실행을 방지합니다.")
                        return
                
                # 콜백 실행 상태 설정
                self.is_callback_running = True
                self.last_execution_time = current_time
                
                try:
                    logger.info(f"주기적 실행 시작: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
                    callback()
                    logger.info(f"주기적 실행 완료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                except Exception as e:
                    logger.error(f"주기적 실행 중 오류: {e}")
                finally:
                    # 실행 상태 해제
                    self.is_callback_running = False
            
            if schedule is not None:
                # schedule 라이브러리 사용
                # 기존 스케줄 정리
                schedule.clear()
                
                # 새 스케줄 등록 (안전한 콜백 사용)
                schedule.every().day.at(time_str).do(safe_callback)
                
                self.callback_function = callback
                self.is_running = True
                
                # 스케줄러 스레드 시작
                self.scheduler_thread = threading.Thread(
                    target=self._run_scheduler, 
                    daemon=True,
                    name="PeriodicScheduler"
                )
                self.scheduler_thread.start()
                
            else:
                # 내장 스케줄러 사용 (안전한 콜백 사용)
                self.simple_scheduler.schedule_daily(time_str, safe_callback)
                self.callback_function = callback
                self.is_running = True
            
            logger.info(f"매일 {time_str}에 실행되는 스케줄이 시작되었습니다.")
            
        except Exception as e:
            logger.error(f"스케줄 시작 중 오류: {e}")
            raise
    
    def stop_schedule(self):
        """스케줄 중지"""
        try:
            self.is_running = False
            
            if schedule is not None:
                schedule.clear()
            elif self.simple_scheduler is not None:
                self.simple_scheduler.stop()
            
            if self.scheduler_thread and self.scheduler_thread.is_alive():
                # 스레드가 자연스럽게 종료되도록 대기
                self.scheduler_thread.join(timeout=2.0)
            
            # 콜백 실행 상태 초기화
            self.callback_function = None
            self.is_callback_running = False
            self.last_execution_time = None
            
            logger.info("스케줄이 중지되었습니다.")
            
        except Exception as e:
            logger.error(f"스케줄 중지 중 오류: {e}")
            raise
    
    def _run_scheduler(self):
        """스케줄러 실행 (별도 스레드에서 실행)"""
        logger.info("스케줄러 스레드가 시작되었습니다.")
        
        while self.is_running:
            try:
                if schedule is not None:
                    schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                logger.error(f"스케줄러 실행 중 오류: {e}")
                time.sleep(5)  # 오류 발생 시 잠시 대기
        
        logger.info("스케줄러 스레드가 종료되었습니다.")
    
    def get_next_run_time(self) -> Optional[str]:
        """다음 실행 시간 반환"""
        if schedule and schedule.jobs:
            next_run = schedule.next_run()
            if next_run:
                return next_run.strftime("%Y-%m-%d %H:%M:%S")
        return None
    
    def is_schedule_running(self) -> bool:
        """스케줄이 실행 중인지 확인"""
        return self.is_running and self.scheduler_thread and self.scheduler_thread.is_alive()


class PeriodicExecutionManager:
    """주기적 실행 관리자"""
    
    def __init__(self, log_callback: Optional[Callable] = None):
        self.schedule_manager = ScheduleManager()
        self.log_callback = log_callback
        self.config = {}
        self.is_executing = False
        self.running_processes = []  # 실행 중인 프로세스 추적
        self.process_lock = threading.Lock()  # 프로세스 리스트 동기화
        
        # 단계 6-2의 48시간 주기 실행을 위한 추적
        self.step62_last_run = None  # 단계 6-2의 마지막 실행 시간
        self.step62_config_file = Path(__file__).parent.parent / "step62_last_run.json"
        self._load_step62_last_run()
        
        # 프로젝트 루트 경로
        self.project_root = Path(__file__).parent.parent
        
    def _load_step62_last_run(self):
        """단계 6-2의 마지막 실행 시간을 파일에서 로드"""
        try:
            if self.step62_config_file.exists():
                import json
                with open(self.step62_config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'last_run' in data:
                        from datetime import datetime
                        self.step62_last_run = datetime.fromisoformat(data['last_run'])
                        self._log(f"단계 6-2 마지막 실행 시간 로드: {self.step62_last_run}")
        except Exception as e:
            self._log(f"단계 6-2 마지막 실행 시간 로드 실패: {e}")
            self.step62_last_run = None
    
    def _save_step62_last_run(self):
        """단계 6-2의 마지막 실행 시간을 파일에 저장"""
        try:
            if self.step62_last_run:
                import json
                data = {'last_run': self.step62_last_run.isoformat()}
                with open(self.step62_config_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                self._log(f"단계 6-2 마지막 실행 시간 저장: {self.step62_last_run}")
        except Exception as e:
            self._log(f"단계 6-2 마지막 실행 시간 저장 실패: {e}")
    
    def _should_run_step62(self) -> bool:
        """단계 6-2를 실행해야 하는지 확인 (48시간 주기)"""
        if self.step62_last_run is None:
            return True  # 처음 실행
        
        from datetime import datetime, timedelta
        now = datetime.now()
        time_since_last_run = now - self.step62_last_run
        
        # 48시간(2일) 경과 확인
        return time_since_last_run >= timedelta(hours=48)
        
    def set_config(self, config: Dict):
        """주기적 실행 설정
        
        Args:
            config: {
                'step1_quantity': int,      # 1단계 전용 배치 수량
                'other_quantity': int,      # 나머지 단계 공통 배치 수량
                'step3_product_limit': int, # 3단계 상품 수량 제한
                'step3_image_limit': int,   # 3단계 이미지 번역 제한
                'selected_steps': List[str],
                'selected_accounts': List[str],
                'schedule_time': str,       # "HH:MM" 형식
                'step_interval': int        # 단계 간 대기 시간(초)
            }
        """
        self.config = config.copy()
        self._log(f"주기적 실행 설정이 업데이트되었습니다: {config}")
    
    def start_periodic_execution(self) -> bool:
        """주기적 실행 시작
        
        Returns:
            bool: 시작 성공 여부
        """
        try:
            if not self.config:
                raise ValueError("설정이 없습니다. set_config()를 먼저 호출하세요.")
            
            schedule_time = self.config.get('schedule_time')
            if not schedule_time:
                raise ValueError("실행 시간이 설정되지 않았습니다.")
            
            # 스케줄 시작
            self.schedule_manager.start_daily_schedule(
                schedule_time, 
                self._execute_periodic_batch
            )
            
            self._log(f"주기적 실행이 시작되었습니다. 매일 {schedule_time}에 실행됩니다.")
            return True
            
        except Exception as e:
            self._log(f"주기적 실행 시작 실패: {e}")
            return False
    
    def stop_periodic_execution(self):
        """주기적 실행 중지 및 실행 중인 프로세스 종료"""
        try:
            # 실행 중단 플래그 설정 (다중 배치 실행 중인 스레드들에게 중단 신호)
            self.is_executing = False
            
            # 스케줄 중지
            self.schedule_manager.stop_schedule()
            
            # 실행 중인 모든 프로세스 종료
            self._terminate_running_processes()
            
            self._log("주기적 실행이 중지되었습니다.")
        except Exception as e:
            self._log(f"주기적 실행 중지 실패: {e}")
    
    def _terminate_running_processes(self):
        """실행 중인 모든 프로세스 종료"""
        with self.process_lock:
            if not self.running_processes:
                self._log("종료할 실행 중인 프로세스가 없습니다.")
                return
            
            self._log(f"실행 중인 프로세스 {len(self.running_processes)}개를 종료합니다...")
            
            for process in self.running_processes[:]:
                try:
                    if process.poll() is None:  # 프로세스가 아직 실행 중인 경우
                        self._log(f"프로세스 PID {process.pid} 종료 중...")
                        process.terminate()
                        
                        # 프로세스가 정상적으로 종료되기를 3초 대기
                        try:
                            process.wait(timeout=3)
                            self._log(f"프로세스 PID {process.pid} 정상 종료됨")
                        except subprocess.TimeoutExpired:
                            # 강제 종료
                            self._log(f"프로세스 PID {process.pid} 강제 종료 중...")
                            process.kill()
                            process.wait()
                            self._log(f"프로세스 PID {process.pid} 강제 종료됨")
                    
                    self.running_processes.remove(process)
                    
                except Exception as e:
                    self._log(f"프로세스 종료 중 오류: {e}")
            
            self._log("모든 실행 중인 프로세스가 종료되었습니다.")
    
    def execute_immediate(self) -> bool:
        """즉시 실행 (테스트용)
        
        Returns:
            bool: 실행 성공 여부
        """
        try:
            if not self.config:
                raise ValueError("설정이 없습니다. set_config()를 먼저 호출하세요.")
            
            self._log("즉시 실행을 시작합니다...")
            return self._execute_periodic_batch()
            
        except Exception as e:
            self._log(f"즉시 실행 실패: {e}")
            return False
    
    def _execute_periodic_batch(self) -> bool:
        """주기적 배치 실행 (실제 실행 로직) - 계정별 동시 실행
        
        Returns:
            bool: 실행 성공 여부
        """
        if self.is_executing:
            self._log("이미 실행 중입니다. 중복 실행을 방지합니다.")
            return False
        
        # 실행 중인 프로세스가 있으면 중복 실행 방지
        with self.process_lock:
            if self.running_processes:
                active_processes = [p for p in self.running_processes if p.poll() is None]
                if active_processes:
                    self._log(f"실행 중인 프로세스 {len(active_processes)}개가 있습니다. 중복 실행을 방지합니다.")
                    return False
        
        self.is_executing = True
        
        try:
            # 단계별 배치수량 설정
            step1_quantity = self.config.get('step1_quantity', 300)
            other_quantity = self.config.get('other_quantity', 100)
            step3_product_limit = self.config.get('step3_product_limit', 200)
            step3_image_limit = self.config.get('step3_image_limit', 2000)
            selected_steps = self.config.get('selected_steps', [])
            selected_accounts = self.config.get('selected_accounts', [])
            step_interval = self.config.get('step_interval', 10)
            
            self._log(f"배치 실행 시작: 1단계={step1_quantity}개, 나머지단계={other_quantity}개, 3단계 상품제한={step3_product_limit}개, 3단계 이미지제한={step3_image_limit}개")
            self._log(f"단계={selected_steps}, 계정={len(selected_accounts)}개")
            self._log(f"각 계정은 독립적인 프로세스에서 동시 실행됩니다.")
            
            # 각 계정을 별도 스레드에서 동시 실행
            threads = []
            results = {}
            
            def execute_account_steps(account_id):
                """계정별 단계 실행 함수"""
                try:
                    self._log(f"계정 {account_id} 처리 시작 (독립 프로세스)")
                    account_success = True
                    
                    # 타임아웃에도 계속 진행할 스텝들 (상품 수량이 가변적인 스텝들)
                    continue_on_timeout_steps = ['21', '22', '23', '31', '32', '33', '311', '312', '313', '321', '322', '323', '331', '332', '333']
                    
                    # 선택된 단계들을 순차적으로 실행
                    for step in selected_steps:
                        # 실행 중단 확인
                        if not self.is_executing:
                            self._log(f"계정 {account_id}: 주기적 실행이 중단되어 처리를 종료합니다.")
                            results[account_id] = False
                            return
                        
                        # 단계 6-2의 48시간 주기 확인
                        if step == '62':
                            if not self._should_run_step62():
                                self._log(f"계정 {account_id}, 단계 6-2: 48시간이 경과하지 않아 건너뜁니다.")
                                continue
                            else:
                                self._log(f"계정 {account_id}, 단계 6-2: 48시간이 경과하여 실행합니다.")
                        
                        # 단계에 따라 배치수량 결정
                        current_batch_quantity = step1_quantity if step == '1' else other_quantity
                        success = self._execute_single_step(account_id, step, current_batch_quantity, step3_product_limit, step3_image_limit)
                        
                        # 단계 6-2 실행 성공 시 마지막 실행 시간 업데이트
                        if step == '62' and success:
                            from datetime import datetime
                            self.step62_last_run = datetime.now()
                            self._save_step62_last_run()
                        
                        if success:
                            self._log(f"계정 {account_id}, 단계 {step} 완료")
                        else:
                            self._log(f"계정 {account_id}, 단계 {step} 실패")
                            # 타임아웃에도 계속 진행할 스텝인지 확인
                            if step not in continue_on_timeout_steps:
                                account_success = False
                            else:
                                self._log(f"계정 {account_id}, 단계 {step}: 타임아웃/실패했지만 후속 단계 계속 진행")
                        
                        # 단계 간 대기 (중단 확인 포함)
                        if step != selected_steps[-1]:  # 마지막 단계가 아니면 대기
                            self._log(f"계정 {account_id}: 다음 단계까지 {step_interval}초 대기...")
                            # 1초씩 나누어 대기하면서 중단 확인
                            for i in range(step_interval):
                                if not self.is_executing:
                                    self._log(f"계정 {account_id}: 대기 중 주기적 실행이 중단되어 처리를 종료합니다.")
                                    results[account_id] = False
                                    return
                                time.sleep(1)
                    
                    results[account_id] = account_success
                    self._log(f"계정 {account_id} 처리 완료 ({'성공' if account_success else '실패'})")
                    
                except Exception as e:
                    self._log(f"계정 {account_id} 처리 중 오류: {e}")
                    results[account_id] = False
            
            # 각 계정별로 스레드 생성 및 시작 (5초 간격으로 실행)
            for i, account_id in enumerate(selected_accounts):
                thread = threading.Thread(
                    target=execute_account_steps,
                    args=(account_id,),
                    name=f"Account-{account_id}"
                )
                threads.append(thread)
                thread.start()
                self._log(f"계정 {account_id} 독립 프로세스 시작됨")
                
                # 다음 계정 실행 전 대기 (마지막 계정이 아닌 경우)
                if i < len(selected_accounts) - 1:
                    account_delay = self.config.get('account_delay', 5)  # 기본값 5초
                    self._log(f"다음 계정 실행까지 {account_delay}초 대기...")
                    time.sleep(account_delay)
            
            # 모든 스레드 완료 대기
            for thread in threads:
                thread.join()
            
            # 결과 집계
            success_count = sum(1 for success in results.values() if success)
            total_count = len(selected_accounts)
            
            self._log(f"모든 계정 처리 완료: 성공 {success_count}/{total_count}")
            return success_count > 0  # 하나라도 성공하면 전체 성공으로 간주
            
        except Exception as e:
            self._log(f"배치 실행 중 오류: {e}")
            return False
        finally:
            self.is_executing = False
    
    def _execute_single_step(self, account_id: str, step: str, quantity: int, step3_product_limit: int = 200, step3_image_limit: int = 2000) -> bool:
        """단일 단계 실행
        
        Args:
            account_id: 계정 ID
            step: 실행할 단계
            quantity: 배치 수량
            step3_product_limit: 3단계 상품 수량 제한
            step3_image_limit: 3단계 이미지 번역 제한
            
        Returns:
            bool: 실행 성공 여부
        """
        try:
            # 모든 단계는 CLI 배치 실행 명령 구성
            cli_script = self.project_root / "cli" / "batch_cli.py"
            
            if not cli_script.exists():
                self._log(f"CLI 스크립트를 찾을 수 없습니다: {cli_script}")
                return False
            
            # 청크 사이즈 가져오기
            chunk_sizes = self.config.get('chunk_sizes', {})
            
            # 61, 62, 63단계는 마켓 설정 기반으로 1회만 실행되어야 함
            if step in ['61', '62', '63']:
                chunk_size = 1  # 청크 사이즈를 1로 고정하여 1회만 실행
                self._log(f"단계 {step}는 마켓 설정 기반 단계로 청크 사이즈를 1로 설정")
            else:
                chunk_size = chunk_sizes.get(step, 10)  # 기본값 10
            
            # 가상 계정 ID를 실제 이메일로 변환
            real_account_id = get_real_account_id(account_id)
            self._log(f"계정 매핑: {account_id} -> {real_account_id}")
            
            # 명령어 구성 (CLI의 single 명령어 사용)
            cmd = [
                sys.executable,
                str(cli_script),
                "single",
                "--step", step,
                "--accounts", real_account_id,  # 실제 이메일 주소 사용
                "--quantity", str(quantity)
            ]
            
            # 모든 단계에 청크 사이즈 추가 (4단계 제외하지 않음)
            cmd.extend(["--chunk-size", str(chunk_size)])
            
            # 3단계 관련 단계들에 이중 제한 설정 추가
            step3_steps = ['31', '32', '33', '311', '312', '313', '321', '322', '323', '331', '332', '333']
            if step in step3_steps:
                cmd.extend(["--step3-product-limit", str(step3_product_limit)])
                cmd.extend(["--step3-image-limit", str(step3_image_limit)])
                self._log(f"3단계 이중 제한 적용: 상품 {step3_product_limit}개, 이미지 번역 {step3_image_limit}개")
            
            self._log(f"실행 명령: {' '.join(cmd)}")
            
            # 프로세스 실행 (새로운 콘솔 창에서 실행하여 디버깅 편의성 제공)
            process = subprocess.Popen(
                cmd,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                cwd=str(self.project_root)
            )
            
            # 실행 중인 프로세스 목록에 추가
            with self.process_lock:
                self.running_processes.append(process)
            
            self._log(f"프로세스 PID {process.pid} 시작됨 (계정 {account_id}, 단계 {step})")
            
            try:
                # 청크별 타임아웃 계산
                timeout = self._calculate_chunk_timeout(step, quantity, chunk_size)
                
                self._log(f"단계 {step} 전체 배치 타임아웃 설정: {timeout}초 ({timeout//3600}시간 {(timeout%3600)//60}분) - 총수량: {quantity}, 청크크기: {chunk_size}, 예상청크수: {(quantity + chunk_size - 1) // chunk_size}")
                
                # 프로세스 완료 대기 (스텝별 타임아웃)
                process.wait(timeout=timeout)
                
                # 완료된 프로세스를 목록에서 제거
                with self.process_lock:
                    if process in self.running_processes:
                        self.running_processes.remove(process)
                
                # 프로세스 완료 후 관련 브라우저 프로세스 정리 (정상 완료/실패 모두)
                self._cleanup_browser_processes(account_id)
                
                if process.returncode == 0:
                    self._log(f"단계 {step} 실행 성공 (계정 {account_id}, PID {process.pid}) - 브라우저 프로세스 정리 완료")
                    return True
                else:
                    self._log(f"단계 {step} 실행 실패 (계정 {account_id}, PID {process.pid}): 반환코드 {process.returncode} - 브라우저 프로세스 정리 완료")
                    return False
                    
            except subprocess.TimeoutExpired:
                # 타임아웃 시 프로세스 및 관련 리소스 완전 정리
                self._log(f"단계 {step} 실행 타임아웃 (계정 {account_id}, PID {process.pid}) - 프로세스 및 브라우저 정리 중...")
                
                # 1단계: 정상 종료 시도
                process.terminate()
                try:
                    process.wait(timeout=10)
                    self._log(f"프로세스 {process.pid} 정상 종료 완료")
                except subprocess.TimeoutExpired:
                    # 2단계: 강제 종료
                    self._log(f"프로세스 {process.pid} 정상 종료 실패, 강제 종료 시도")
                    process.kill()
                    process.wait()
                    self._log(f"프로세스 {process.pid} 강제 종료 완료")
                
                # 3단계: 관련 브라우저 프로세스 정리
                self._cleanup_browser_processes(account_id)
                
                # 타임아웃된 프로세스를 목록에서 제거
                with self.process_lock:
                    if process in self.running_processes:
                        self.running_processes.remove(process)
                
                return False
        except Exception as e:
            self._log(f"단계 {step} 실행 중 오류 (계정 {account_id}): {e}")
            # 예외 발생 시에도 브라우저 프로세스 정리
            try:
                self._cleanup_browser_processes(account_id)
            except Exception as cleanup_error:
                self._log(f"예외 처리 중 브라우저 정리 오류: {cleanup_error}")
            return False
    
    def _calculate_chunk_timeout(self, step: str, quantity: int, chunk_size: int) -> int:
        """전체 배치 타임아웃 계산 (청크별이 아닌 전체 프로세스 기준)
        
        Args:
            step: 실행 단계
            quantity: 총 수량
            chunk_size: 청크 크기
            
        Returns:
            int: 계산된 타임아웃 (초)
        """
        # 단계별 기본 타임아웃 (단일 아이템 처리 시간 기준) - 휴먼딜레이 반영
        base_timeouts_per_item = {
            '21': 270,   # 4.5분/아이템 (서버 처리 단계)
            '22': 270,   # 4.5분/아이템 (서버 처리 단계)
            '23': 270,   # 4.5분/아이템 (서버 처리 단계)
            '31': 540,   # 9분/아이템 (키워드 검색으로 시간 편차 큼)
            '32': 540,   # 9분/아이템 (키워드 검색으로 시간 편차 큼)
            '33': 540,   # 9분/아이템 (키워드 검색으로 시간 편차 큼)
            '311': 540,  # 9분/아이템 (3단계 세분화 - 서버1-1)
            '312': 540,  # 9분/아이템 (3단계 세분화 - 서버1-2)
            '313': 540,  # 9분/아이템 (3단계 세분화 - 서버1-3)
            '321': 540,  # 9분/아이템 (3단계 세분화 - 서버2-1)
            '322': 540,  # 9분/아이템 (3단계 세분화 - 서버2-2)
            '323': 540,  # 9분/아이템 (3단계 세분화 - 서버2-3)
            '331': 540,  # 9분/아이템 (3단계 세분화 - 서버3-1)
            '332': 540,  # 9분/아이템 (3단계 세분화 - 서버3-2)
            '333': 540,  # 9분/아이템 (3단계 세분화 - 서버3-3)
            '1': 195,    # 3.25분/아이템 (초기 데이터 처리 + 휴먼딜레이 45-60초)
            '4': 135,    # 2.25분/아이템 (번역 처리, 휴먼딜레이 미적용)
            '51': 285,   # 4.75분/아이템 (최종 처리 단계 + 휴먼딜레이 152-160초)
            '52': 315,   # 5.25분/아이템 (최종 처리 단계 + 휴먼딜레이 152-170초)
            '53': 345,   # 5.75분/아이템 (최종 처리 단계 + 휴먼딜레이 152-180초)
            '61': 12000,  # 200분/마켓설정 (동적 업로드 처리 - 마켓당 10회 업로드 * 20분)
            '62': 12000,  # 200분/마켓설정 (동적 업로드 처리 - 마켓당 10회 업로드 * 20분)
            '63': 12000   # 200분/마켓설정 (동적 업로드 처리 - 마켓당 10회 업로드 * 20분)
        }
        
        # 청크 수 계산
        # 61, 62, 63단계는 마켓 설정 기반으로 1회만 실행되므로 청크 수를 1로 설정
        if step in ['61', '62', '63']:
            total_chunks = 1
        else:
            total_chunks = (quantity + chunk_size - 1) // chunk_size
        
        # 단일 아이템 처리 시간
        base_time_per_item = base_timeouts_per_item.get(step, 90)  # 기본 1.5분/아이템
        
        # 전체 배치 타임아웃 계산
        if step in ['61', '62', '63']:
            # 61, 62, 63단계는 마켓 설정 기반으로 1회만 실행되므로 고정 타임아웃 사용
            # 마켓 설정당 200분 * 최대 20개 마켓 설정 = 최대 66.67시간 (240000초)
            total_timeout = base_time_per_item * 20  # 최대 20개 마켓 설정을 고려한 충분한 타임아웃
        else:
            # 다른 단계는 기존 로직 사용 (총 수량 * 아이템당 시간 + 청크별 오버헤드)
            total_timeout = quantity * base_time_per_item
            # 청크별 브라우저 재시작 오버헤드 추가 (청크당 5분)
            chunk_overhead = total_chunks * 300
            total_timeout += chunk_overhead
        
        # 최소 타임아웃 보장 (20분)
        min_timeout = 1200
        total_timeout = max(total_timeout, min_timeout)
        
        # 최대 타임아웃 제한 (72시간) - 61,62,63단계의 대용량 마켓 처리 지원
        max_timeout = 259200
        total_timeout = min(total_timeout, max_timeout)
        
        return total_timeout
    
    def _cleanup_browser_processes(self, account_id: str):
        """타임아웃 시 관련 브라우저 프로세스 정리
        
        Args:
            account_id: 계정 ID
        """
        try:
            import psutil
            import time
            
            self._log(f"계정 {account_id} 관련 브라우저 프로세스 정리 시작")
            
            # Chrome/Edge 프로세스 찾기 및 종료
            browser_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] and ('chrome' in proc.info['name'].lower() or 'msedge' in proc.info['name'].lower()):
                        cmdline = proc.info['cmdline'] or []
                        # 사용자 데이터 디렉토리에 계정 ID가 포함된 프로세스 찾기
                        if any(account_id in arg for arg in cmdline if arg):
                            browser_processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            # 브라우저 프로세스 종료
            for proc in browser_processes:
                try:
                    self._log(f"브라우저 프로세스 종료 시도: PID {proc.pid}")
                    proc.terminate()
                    proc.wait(timeout=5)
                    self._log(f"브라우저 프로세스 {proc.pid} 정상 종료")
                except psutil.TimeoutExpired:
                    try:
                        proc.kill()
                        self._log(f"브라우저 프로세스 {proc.pid} 강제 종료")
                    except:
                        pass
                except Exception as e:
                    self._log(f"브라우저 프로세스 {proc.pid} 종료 중 오류: {e}")
            
            # Python 프로세스 정리 (batch_cli.py 관련)
            python_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] and 'python' in proc.info['name'].lower():
                        cmdline = proc.info['cmdline'] or []
                        # batch_cli.py를 실행하고 해당 계정을 처리하는 프로세스 찾기
                        if any('batch_cli.py' in arg for arg in cmdline) and any(account_id in arg for arg in cmdline):
                            python_processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            # Python 프로세스 종료
            for proc in python_processes:
                try:
                    self._log(f"Python 프로세스 종료 시도: PID {proc.pid}")
                    proc.terminate()
                    proc.wait(timeout=5)
                    self._log(f"Python 프로세스 {proc.pid} 정상 종료")
                except psutil.TimeoutExpired:
                    try:
                        proc.kill()
                        self._log(f"Python 프로세스 {proc.pid} 강제 종료")
                    except:
                        pass
                except Exception as e:
                    self._log(f"Python 프로세스 {proc.pid} 종료 중 오류: {e}")
            
            self._log(f"계정 {account_id} 브라우저 프로세스 정리 완료")
            
        except ImportError:
            self._log("psutil 라이브러리가 없어 브라우저 프로세스 정리를 건너뜁니다")
        except Exception as e:
            self._log(f"브라우저 프로세스 정리 중 오류: {e}")
    
    def _log(self, message: str):
        """로그 메시지 출력"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        
        # 콘솔 로그
        logger.info(message)
        
        # GUI 콜백이 있으면 호출
        if self.log_callback:
            try:
                self.log_callback(log_message)
            except Exception as e:
                logger.error(f"로그 콜백 호출 실패: {e}")
    
    def get_status(self) -> Dict:
        """현재 상태 반환"""
        return {
            'is_schedule_running': self.schedule_manager.is_schedule_running(),
            'is_executing': self.is_executing,
            'next_run_time': self.schedule_manager.get_next_run_time(),
            'config': self.config.copy()
        }
    
    def save_config_to_file(self, file_path: str):
        """설정을 파일로 저장"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'periodic_config': self.config,
                    'saved_at': datetime.now().isoformat()
                }, f, indent=2, ensure_ascii=False)
            
            self._log(f"설정이 저장되었습니다: {file_path}")
        except Exception as e:
            self._log(f"설정 저장 실패: {e}")
    
    def load_config_from_file(self, file_path: str) -> bool:
        """파일에서 설정 로드
        
        Returns:
            bool: 로드 성공 여부
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'periodic_config' in data:
                self.config = data['periodic_config']
                self._log(f"설정이 로드되었습니다: {file_path}")
                return True
            else:
                self._log(f"올바르지 않은 설정 파일 형식: {file_path}")
                return False
                
        except Exception as e:
            self._log(f"설정 로드 실패: {e}")
            return False