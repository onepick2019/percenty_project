#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
개선된 주기적 실행 관리자
- GUI에서 동적 배치크기 인식
- 설정 가능한 청크 크기
- 모든 계정 지원
- 개선된 타임아웃 처리
"""

import os
import sys
import json
import subprocess
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# 프로젝트 루트를 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from account_manager import AccountManager

class ImprovedPeriodicExecutionManager:
    """
    개선된 주기적 실행 관리자
    """
    
    def __init__(self, config_file: str = "dynamic_batch_config.json"):
        self.project_root = Path(__file__).parent
        self.config_file = self.project_root / config_file
        self.config = {}
        self.running_processes = []
        self.process_lock = threading.Lock()
        self.account_manager = AccountManager()
        self.gui_batch_quantity = None  # GUI에서 설정한 배치 수량
        
        # 로그 설정
        self.log_file = self.project_root / "logs" / f"improved_periodic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.log_file.parent.mkdir(exist_ok=True)
        
        self._load_config()
    
    def _load_config(self):
        """설정 파일 로드"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.config = data.get('periodic_config', {})
                    self._log(f"설정 파일 로드 성공: {self.config_file}")
            else:
                self._log(f"설정 파일이 없습니다: {self.config_file}")
                self._create_default_config()
        except Exception as e:
            self._log(f"설정 파일 로드 실패: {e}")
            self._create_default_config()
    
    def _create_default_config(self):
        """기본 설정 생성"""
        self.config = {
            "batch_quantity": "dynamic",
            "chunk_size": 10,
            "selected_steps": ["1", "4", "51"],
            "selected_accounts": "all",
            "schedule_time": "00:00",
            "step_interval": 30,
            "continue_on_timeout_steps": ["21", "22", "23", "31", "32", "33"],
            "step_timeouts": {
                "21": 7200,
                "22": 7200,
                "23": 7200,
                "31": 7200,
                "32": 7200,
                "33": 7200,
                "1": 3600,
                "4": 3600,
                "51": 3600,
                "52": 3600,
                "53": 3600
            },
            "default_timeout": 1800
        }
    
    def _log(self, message: str):
        """로그 기록"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_message + "\n")
        except Exception as e:
            print(f"로그 기록 실패: {e}")
    
    def set_gui_batch_quantity(self, quantity: int):
        """GUI에서 설정한 배치 수량 저장"""
        self.gui_batch_quantity = quantity
        self._log(f"GUI 배치 수량 설정: {quantity}개")
    
    def get_effective_batch_quantity(self) -> int:
        """실제 사용할 배치 수량 반환"""
        if self.gui_batch_quantity is not None:
            return self.gui_batch_quantity
        
        config_quantity = self.config.get('batch_quantity', 100)
        if config_quantity == "dynamic":
            return 100  # 기본값
        return int(config_quantity)
    
    def get_chunk_size(self) -> int:
        """청크 크기 반환"""
        return self.config.get('chunk_size', 10)
    
    def get_selected_accounts(self) -> List[str]:
        """선택된 계정 목록 반환"""
        selected_accounts = self.config.get('selected_accounts', [])
        
        if selected_accounts == "all":
            # AccountManager를 통해 모든 계정 로드
            try:
                all_accounts = self.account_manager.get_accounts()
                account_ids = [acc['id'] for acc in all_accounts]
                self._log(f"모든 계정 로드됨: {len(account_ids)}개")
                return account_ids
            except Exception as e:
                self._log(f"계정 로드 실패: {e}")
                return []
        
        return selected_accounts if isinstance(selected_accounts, list) else []
    
    def execute_batch_with_dynamic_settings(self, gui_quantity: Optional[int] = None):
        """동적 설정으로 배치 실행"""
        if gui_quantity is not None:
            self.set_gui_batch_quantity(gui_quantity)
        
        try:
            batch_quantity = self.get_effective_batch_quantity()
            chunk_size = self.get_chunk_size()
            selected_steps = self.config.get('selected_steps', [])
            selected_accounts = self.get_selected_accounts()
            step_interval = self.config.get('step_interval', 30)
            
            self._log(f"동적 배치 실행 시작:")
            self._log(f"  - 배치 수량: {batch_quantity}개")
            self._log(f"  - 청크 크기: {chunk_size}개")
            self._log(f"  - 선택된 단계: {selected_steps}")
            self._log(f"  - 계정 수: {len(selected_accounts)}개")
            self._log(f"  - 단계 간격: {step_interval}초")
            
            if not selected_accounts:
                self._log("⚠️ 선택된 계정이 없습니다.")
                return False
            
            # 각 계정을 별도 스레드에서 동시 실행
            threads = []
            results = {}
            
            def execute_account_steps(account_id):
                """계정별 단계 실행 함수"""
                try:
                    self._log(f"계정 {account_id} 처리 시작 (배치수량: {batch_quantity}, 청크크기: {chunk_size})")
                    account_success = True
                    
                    # 타임아웃에도 계속 진행할 스텝들
                    continue_on_timeout_steps = self.config.get('continue_on_timeout_steps', [])
                    
                    # 선택된 단계들을 순차적으로 실행
                    for step in selected_steps:
                        success = self._execute_single_step_with_chunk(account_id, step, batch_quantity, chunk_size)
                        
                        if success:
                            self._log(f"계정 {account_id}, 단계 {step} 완료")
                        else:
                            self._log(f"계정 {account_id}, 단계 {step} 실패")
                            
                            # 타임아웃 시 계속 진행할 스텝인지 확인
                            if step in continue_on_timeout_steps:
                                self._log(f"단계 {step}는 타임아웃 시에도 후속 단계를 계속 진행합니다.")
                            else:
                                account_success = False
                                break
                        
                        # 단계 간 대기
                        if step != selected_steps[-1]:  # 마지막 단계가 아닌 경우
                            time.sleep(step_interval)
                    
                    results[account_id] = account_success
                    status = "성공" if account_success else "실패"
                    self._log(f"계정 {account_id} 처리 완료: {status}")
                    
                except Exception as e:
                    self._log(f"계정 {account_id} 처리 중 오류: {e}")
                    results[account_id] = False
            
            # 각 계정별로 스레드 생성 및 시작
            for account_id in selected_accounts:
                thread = threading.Thread(target=execute_account_steps, args=(account_id,))
                threads.append(thread)
                thread.start()
                
                # 계정 간 5초 간격으로 시작
                time.sleep(5)
            
            # 모든 스레드 완료 대기
            for thread in threads:
                thread.join()
            
            # 결과 요약
            successful_accounts = [acc for acc, success in results.items() if success]
            failed_accounts = [acc for acc, success in results.items() if not success]
            
            self._log(f"배치 실행 완료:")
            self._log(f"  - 성공: {len(successful_accounts)}개 계정")
            self._log(f"  - 실패: {len(failed_accounts)}개 계정")
            
            if failed_accounts:
                self._log(f"  - 실패한 계정: {failed_accounts}")
            
            return len(successful_accounts) > 0
            
        except Exception as e:
            self._log(f"배치 실행 중 오류: {e}")
            return False
    
    def _execute_single_step_with_chunk(self, account_id: str, step: str, quantity: int, chunk_size: int) -> bool:
        """
        청크 크기를 고려한 단일 단계 실행
        
        Args:
            account_id: 계정 ID
            step: 실행할 단계
            quantity: 총 배치 수량
            chunk_size: 청크 크기
            
        Returns:
            bool: 실행 성공 여부
        """
        try:
            # CLI 배치 실행 명령 구성
            cli_script = self.project_root / "cli" / "batch_cli.py"
            
            if not cli_script.exists():
                self._log(f"CLI 스크립트를 찾을 수 없습니다: {cli_script}")
                return False
            
            # 명령어 구성 (청크 크기 포함)
            cmd = [
                sys.executable,
                str(cli_script),
                "single",
                "--step", step,
                "--accounts", account_id,
                "--quantity", str(quantity)
            ]
            
            # 4단계가 아닌 경우에만 청크 사이즈 추가
            if step != "4":
                cmd.extend(["--chunk-size", str(chunk_size)])
            
            self._log(f"실행 명령: {' '.join(cmd)}")
            
            # 프로세스 실행
            process = subprocess.Popen(
                cmd,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                cwd=str(self.project_root)
            )
            
            # 실행 중인 프로세스 목록에 추가
            with self.process_lock:
                self.running_processes.append(process)
            
            self._log(f"프로세스 PID {process.pid} 시작됨 (계정 {account_id}, 단계 {step}, 수량 {quantity}, 청크 {chunk_size})")
            
            try:
                # 스텝별 타임아웃 설정
                step_timeouts = self.config.get('step_timeouts', {})
                timeout = step_timeouts.get(step, self.config.get('default_timeout', 1800))
                
                self._log(f"단계 {step} 타임아웃 설정: {timeout}초 ({timeout//3600}시간 {(timeout%3600)//60}분)")
                
                # 프로세스 완료 대기
                process.wait(timeout=timeout)
                
                if process.returncode == 0:
                    self._log(f"단계 {step} 성공 완료 (계정 {account_id})")
                    return True
                else:
                    self._log(f"단계 {step} 실패 (계정 {account_id}, 종료코드: {process.returncode})")
                    return False
                    
            except subprocess.TimeoutExpired:
                self._log(f"단계 {step} 타임아웃 발생 (계정 {account_id}, {timeout}초 초과)")
                
                # 프로세스 강제 종료
                try:
                    process.terminate()
                    time.sleep(5)
                    if process.poll() is None:
                        process.kill()
                        self._log(f"프로세스 PID {process.pid} 강제 종료됨")
                except Exception as e:
                    self._log(f"프로세스 종료 중 오류: {e}")
                
                return False
                
            finally:
                # 프로세스 목록에서 제거
                with self.process_lock:
                    if process in self.running_processes:
                        self.running_processes.remove(process)
                        
        except Exception as e:
            self._log(f"단계 {step} 실행 중 오류 (계정 {account_id}): {e}")
            return False
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """현재 설정 요약 반환"""
        return {
            "batch_quantity": self.get_effective_batch_quantity(),
            "chunk_size": self.get_chunk_size(),
            "selected_steps": self.config.get('selected_steps', []),
            "selected_accounts_count": len(self.get_selected_accounts()),
            "step_timeouts": self.config.get('step_timeouts', {}),
            "continue_on_timeout_steps": self.config.get('continue_on_timeout_steps', [])
        }

def main():
    """테스트 실행"""
    manager = ImprovedPeriodicExecutionManager()
    
    print("=== 개선된 주기적 실행 관리자 테스트 ===")
    print()
    
    # 설정 요약 출력
    config_summary = manager.get_configuration_summary()
    print("📋 현재 설정:")
    for key, value in config_summary.items():
        print(f"  - {key}: {value}")
    print()
    
    # GUI에서 배치 수량 설정 시뮬레이션
    gui_quantity = 50
    print(f"🖥️ GUI에서 배치 수량 설정: {gui_quantity}개")
    manager.set_gui_batch_quantity(gui_quantity)
    print(f"✅ 실제 사용할 배치 수량: {manager.get_effective_batch_quantity()}개")
    print(f"✅ 청크 크기: {manager.get_chunk_size()}개")
    print()
    
    # 계정 목록 확인
    accounts = manager.get_selected_accounts()
    print(f"👥 로드된 계정: {len(accounts)}개")
    for i, account in enumerate(accounts[:3], 1):  # 처음 3개만 표시
        print(f"  {i}. {account}")
    if len(accounts) > 3:
        print(f"  ... 외 {len(accounts) - 3}개")
    print()
    
    print("🚀 동적 배치 실행 준비 완료")
    print("실제 실행을 원하면 manager.execute_batch_with_dynamic_settings()를 호출하세요.")

if __name__ == "__main__":
    main()