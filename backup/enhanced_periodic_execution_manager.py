#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
개선된 주기적 실행 관리자

이 모듈은 기존 periodic_execution_manager.py를 개선하여:
1. 동적 계정 관리 ("all" 키워드 지원)
2. 타임아웃 시 후속 스텝 계속 진행 로직
3. 계정별 개별 설정 지원
을 제공합니다.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from account_manager import AccountManager
import json
import logging
from datetime import datetime

class EnhancedPeriodicExecutionManager:
    """개선된 주기적 실행 관리자"""
    
    def __init__(self, config_path="periodic_config_enhanced.json"):
        """
        초기화
        
        Args:
            config_path (str): 설정 파일 경로
        """
        self.config_path = config_path
        self.config = {}
        self.account_manager = AccountManager()
        self.continue_on_timeout_steps = ['21', '22', '23', '31', '32', '33', '311', '312', '313', '321', '322', '323', '331', '332', '333']
        
        # 로깅 설정
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # 설정 로드
        self.load_config()
        
    def load_config(self):
        """설정 파일 로드"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                self.logger.info(f"설정 파일 로드 완료: {self.config_path}")
            else:
                self.logger.warning(f"설정 파일을 찾을 수 없습니다: {self.config_path}")
                self._create_default_config()
        except Exception as e:
            self.logger.error(f"설정 파일 로드 중 오류: {e}")
            self._create_default_config()
    
    def _create_default_config(self):
        """기본 설정 생성"""
        self.config = {
            "batch_quantity": 100,
            "selected_steps": ["1", "21", "22", "23", "31", "32", "33", "311", "312", "313", "321", "322", "323", "331", "332", "333", "4", "51", "52", "53"],
            "selected_accounts": "all",
            "schedule_time": "00:32",
            "step_interval": 30,
            "continue_on_timeout_steps": ["21", "22", "23", "31", "32", "33", "311", "312", "313", "321", "322", "323", "331", "332", "333"],
            "step_timeout_settings": {
                "21": 3600, "22": 3600, "23": 3600,
                "31": 3600, "32": 3600, "33": 3600,
                "311": 3600, "312": 3600, "313": 3600,
                "321": 3600, "322": 3600, "323": 3600,
                "331": 3600, "332": 3600, "333": 3600,
                "default": 1800
            }
        }
        self.logger.info("기본 설정을 생성했습니다.")
    
    def get_selected_accounts(self):
        """
        선택된 계정 목록 반환
        
        Returns:
            list: 계정 ID 목록
        """
        selected_accounts = self.config.get('selected_accounts', [])
        
        # "all" 키워드 처리
        if selected_accounts == "all":
            if not self.account_manager.load_accounts():
                self.logger.error("계정 정보를 로드할 수 없습니다.")
                return []
            
            all_accounts = self.account_manager.get_accounts()
            account_ids = [account['id'] for account in all_accounts]
            self.logger.info(f"모든 계정 로드 완료: {len(account_ids)}개")
            return account_ids
        
        # 리스트 형태의 계정 목록 처리
        elif isinstance(selected_accounts, list):
            return selected_accounts
        
        else:
            self.logger.warning(f"알 수 없는 계정 설정 형식: {selected_accounts}")
            return []
    
    def execute_account_steps_enhanced(self, account_id):
        """
        개선된 계정별 스텝 실행
        
        Args:
            account_id (str): 계정 ID
            
        Returns:
            bool: 실행 성공 여부
        """
        selected_steps = self.config.get('selected_steps', [])
        step_interval = self.config.get('step_interval', 30)
        continue_on_timeout_steps = self.config.get('continue_on_timeout_steps', self.continue_on_timeout_steps)
        
        self.logger.info(f"계정 {account_id}의 스텝 실행 시작")
        
        account_success = True
        executed_steps = []
        failed_steps = []
        timeout_steps = []
        
        for step in selected_steps:
            step_str = str(step)
            
            try:
                self.logger.info(f"계정 {account_id} - 스텝 {step_str} 실행 중...")
                
                # 스텝 실행 (실제 구현에서는 _execute_single_step 호출)
                success = self._simulate_step_execution(account_id, step_str)
                
                if success:
                    executed_steps.append(step_str)
                    self.logger.info(f"계정 {account_id} - 스텝 {step_str} 성공")
                else:
                    failed_steps.append(step_str)
                    
                    # 타임아웃 시 후속 스텝 계속 진행 로직
                    if step_str in continue_on_timeout_steps:
                        timeout_steps.append(step_str)
                        self.logger.warning(
                            f"계정 {account_id} - 스텝 {step_str} 실패/타임아웃 발생, "
                            f"하지만 후속 스텝을 계속 진행합니다."
                        )
                        # account_success는 False로 설정하지 않음
                    else:
                        account_success = False
                        self.logger.error(f"계정 {account_id} - 스텝 {step_str} 실패")
                
                # 스텝 간격 대기
                if step != selected_steps[-1]:  # 마지막 스텝이 아닌 경우
                    import time
                    time.sleep(step_interval)
                    
            except Exception as e:
                failed_steps.append(step_str)
                self.logger.error(f"계정 {account_id} - 스텝 {step_str} 실행 중 오류: {e}")
                
                # 타임아웃 시 후속 스텝 계속 진행 로직 적용
                if step_str not in continue_on_timeout_steps:
                    account_success = False
        
        # 실행 결과 요약
        self.logger.info(
            f"계정 {account_id} 실행 완료 - "
            f"성공: {len(executed_steps)}, 실패: {len(failed_steps)}, "
            f"타임아웃(계속진행): {len(timeout_steps)}"
        )
        
        return account_success
    
    def _simulate_step_execution(self, account_id, step):
        """
        스텝 실행 시뮬레이션 (테스트용)
        
        Args:
            account_id (str): 계정 ID
            step (str): 스텝 번호
            
        Returns:
            bool: 실행 성공 여부
        """
        # 실제 구현에서는 subprocess를 사용한 CLI 명령 실행
        # 여기서는 시뮬레이션을 위해 특정 스텝에서 실패 시뮬레이션
        
        import random
        
        # 타임아웃 대상 스텝에서 30% 확률로 실패 시뮬레이션
        if step in self.continue_on_timeout_steps:
            return random.random() > 0.3
        
        # 일반 스텝에서 10% 확률로 실패 시뮬레이션
        return random.random() > 0.1
    
    def execute_all_accounts(self):
        """
        모든 선택된 계정에 대해 스텝 실행
        
        Returns:
            dict: 실행 결과 요약
        """
        selected_accounts = self.get_selected_accounts()
        
        if not selected_accounts:
            self.logger.error("실행할 계정이 없습니다.")
            return {"success": False, "message": "실행할 계정이 없습니다."}
        
        self.logger.info(f"총 {len(selected_accounts)}개 계정에 대해 실행 시작")
        
        results = {
            "total_accounts": len(selected_accounts),
            "successful_accounts": 0,
            "failed_accounts": 0,
            "account_results": {},
            "start_time": datetime.now().isoformat(),
            "end_time": None
        }
        
        for account_id in selected_accounts:
            try:
                success = self.execute_account_steps_enhanced(account_id)
                results["account_results"][account_id] = {
                    "success": success,
                    "timestamp": datetime.now().isoformat()
                }
                
                if success:
                    results["successful_accounts"] += 1
                else:
                    results["failed_accounts"] += 1
                    
            except Exception as e:
                self.logger.error(f"계정 {account_id} 실행 중 오류: {e}")
                results["account_results"][account_id] = {
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                results["failed_accounts"] += 1
        
        results["end_time"] = datetime.now().isoformat()
        
        self.logger.info(
            f"모든 계정 실행 완료 - "
            f"성공: {results['successful_accounts']}, "
            f"실패: {results['failed_accounts']}"
        )
        
        return results
    
    def get_config_summary(self):
        """
        현재 설정 요약 반환
        
        Returns:
            dict: 설정 요약
        """
        selected_accounts = self.get_selected_accounts()
        
        return {
            "batch_quantity": self.config.get('batch_quantity'),
            "selected_steps": self.config.get('selected_steps'),
            "total_accounts": len(selected_accounts),
            "account_sample": selected_accounts[:3] if selected_accounts else [],
            "schedule_time": self.config.get('schedule_time'),
            "step_interval": self.config.get('step_interval'),
            "continue_on_timeout_steps": self.config.get('continue_on_timeout_steps', self.continue_on_timeout_steps)
        }

def main():
    """테스트 실행"""
    print("개선된 주기적 실행 관리자 테스트")
    print("=" * 50)
    
    # 관리자 초기화
    manager = EnhancedPeriodicExecutionManager()
    
    # 설정 요약 표시
    config_summary = manager.get_config_summary()
    print(f"\n📋 설정 요약:")
    for key, value in config_summary.items():
        print(f"  {key}: {value}")
    
    # 시뮬레이션 실행
    print(f"\n🚀 시뮬레이션 실행 시작...")
    results = manager.execute_all_accounts()
    
    # 결과 표시
    print(f"\n📊 실행 결과:")
    print(f"  총 계정 수: {results['total_accounts']}")
    print(f"  성공한 계정: {results['successful_accounts']}")
    print(f"  실패한 계정: {results['failed_accounts']}")
    print(f"  성공률: {results['successful_accounts']/results['total_accounts']*100:.1f}%")
    
    print(f"\n✅ 테스트 완료")

if __name__ == "__main__":
    main()