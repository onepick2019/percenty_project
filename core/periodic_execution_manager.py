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
            if schedule is not None:
                # schedule 라이브러리 사용
                # 기존 스케줄 정리
                schedule.clear()
                
                # 새 스케줄 등록
                schedule.every().day.at(time_str).do(callback)
                
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
                # 내장 스케줄러 사용
                self.simple_scheduler.schedule_daily(time_str, callback)
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
            
            self.callback_function = None
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
        
        # 프로젝트 루트 경로
        self.project_root = Path(__file__).parent.parent
        
    def set_config(self, config: Dict):
        """주기적 실행 설정
        
        Args:
            config: {
                'batch_quantity': int,
                'selected_steps': List[str],
                'selected_accounts': List[str],
                'schedule_time': str,  # "HH:MM" 형식
                'step_interval': int   # 단계 간 대기 시간(초)
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
        
        self.is_executing = True
        
        try:
            batch_quantity = self.config.get('batch_quantity', 100)
            selected_steps = self.config.get('selected_steps', [])
            selected_accounts = self.config.get('selected_accounts', [])
            step_interval = self.config.get('step_interval', 15)
            
            self._log(f"배치 실행 시작: 수량={batch_quantity}, 단계={selected_steps}, 계정={len(selected_accounts)}개")
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
                    continue_on_timeout_steps = ['21', '22', '23', '31', '32', '33']
                    
                    # 선택된 단계들을 순차적으로 실행
                    for step in selected_steps:
                        # 실행 중단 확인
                        if not self.is_executing:
                            self._log(f"계정 {account_id}: 주기적 실행이 중단되어 처리를 종료합니다.")
                            results[account_id] = False
                            return
                        
                        success = self._execute_single_step(account_id, step, batch_quantity)
                        
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
                
                # 다음 계정 실행 전 5초 대기 (마지막 계정이 아닌 경우)
                if i < len(selected_accounts) - 1:
                    self._log(f"다음 계정 실행까지 5초 대기...")
                    time.sleep(5)
            
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
    
    def _execute_single_step(self, account_id: str, step: str, quantity: int) -> bool:
        """단일 단계 실행
        
        Args:
            account_id: 계정 ID
            step: 실행할 단계
            quantity: 배치 수량
            
        Returns:
            bool: 실행 성공 여부
        """
        try:
            # CLI 배치 실행 명령 구성
            cli_script = self.project_root / "cli" / "batch_cli.py"
            
            if not cli_script.exists():
                self._log(f"CLI 스크립트를 찾을 수 없습니다: {cli_script}")
                return False
            
            # 청크 사이즈 가져오기
            chunk_sizes = self.config.get('chunk_sizes', {})
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
                
                self._log(f"단계 {step} 청크별 타임아웃 설정: {timeout}초 ({timeout//3600}시간 {(timeout%3600)//60}분) - 수량: {quantity}, 청크크기: {chunk_size}")
                
                # 프로세스 완료 대기 (스텝별 타임아웃)
                process.wait(timeout=timeout)
                
                # 완료된 프로세스를 목록에서 제거
                with self.process_lock:
                    if process in self.running_processes:
                        self.running_processes.remove(process)
                
                if process.returncode == 0:
                    self._log(f"단계 {step} 실행 성공 (계정 {account_id}, PID {process.pid})")
                    return True
                else:
                    self._log(f"단계 {step} 실행 실패 (계정 {account_id}, PID {process.pid}): 반환코드 {process.returncode}")
                    return False
                    
            except subprocess.TimeoutExpired:
                # 타임아웃 시 프로세스 종료
                self._log(f"단계 {step} 실행 타임아웃 (계정 {account_id}, PID {process.pid}) - 프로세스 종료 중...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                
                # 타임아웃된 프로세스를 목록에서 제거
                with self.process_lock:
                    if process in self.running_processes:
                        self.running_processes.remove(process)
                
                return False
        except Exception as e:
            self._log(f"단계 {step} 실행 중 오류 (계정 {account_id}): {e}")
            return False
    
    def _calculate_chunk_timeout(self, step: str, quantity: int, chunk_size: int) -> int:
        """청크별 타임아웃 계산
        
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
            '1': 195,    # 3.25분/아이템 (초기 데이터 처리 + 휴먼딜레이 45-60초)
            '4': 135,    # 2.25분/아이템 (번역 처리, 휴먼딜레이 미적용)
            '51': 285,   # 4.75분/아이템 (최종 처리 단계 + 휴먼딜레이 152-160초)
            '52': 315,   # 5.25분/아이템 (최종 처리 단계 + 휴먼딜레이 152-170초)
            '53': 345    # 5.75분/아이템 (최종 처리 단계 + 휴먼딜레이 152-180초)
        }
        
        # 청크 수 계산
        total_chunks = (quantity + chunk_size - 1) // chunk_size
        
        # 단일 아이템 처리 시간
        base_time_per_item = base_timeouts_per_item.get(step, 90)  # 기본 1.5분/아이템
        
        # 청크별 타임아웃 계산 (청크 크기 * 아이템당 시간 + 오버헤드)
        chunk_timeout = chunk_size * base_time_per_item
        
        # 브라우저 재시작 및 초기화 오버헤드 추가 (청크당 5분)
        overhead = 300
        chunk_timeout += overhead
        
        # 최소 타임아웃 보장 (10분)
        min_timeout = 600
        chunk_timeout = max(chunk_timeout, min_timeout)
        
        # 최대 타임아웃 제한 (2시간)
        max_timeout = 7200
        chunk_timeout = min(chunk_timeout, max_timeout)
        
        return chunk_timeout
    
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