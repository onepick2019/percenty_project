#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
4단계 자동화 코어 모듈

GUI에서 사용할 4단계 자동화 기능을 제공합니다.
percenty_new_step4.py의 기능을 래핑하여 GUI 환경에서 안전하게 실행할 수 있도록 합니다.

주요 기능:
- 일괄 번역 워크플로우 실행
- 번역 가능한 상품 부족 시 자동 스킵
- 배치 설정과 관계없이 안전한 종료
- GUI 환경에 최적화된 로깅
"""

import logging
import sys
import os
from typing import Optional, Dict, Any
from datetime import datetime

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 필요한 모듈들 임포트
try:
    from percenty_new_step4 import PercentyNewStep4
    from login_percenty import PercentyLogin
    from account_manager import AccountManager
except ImportError as e:
    print(f"필수 모듈 임포트 실패: {e}")
    sys.exit(1)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Step4Core:
    """
    4단계 자동화 코어 클래스
    
    GUI에서 사용할 4단계 자동화 기능을 제공합니다.
    percenty_new_step4.py의 기능을 래핑하여 안전하고 효율적으로 실행합니다.
    """
    
    def __init__(self, account_id: str, headless: bool = False, existing_driver=None):
        """
        Step4Core 초기화
        
        Args:
            account_id (str): 실행할 계정 ID (1, 2, 3, 4 등)
            headless (bool): 헤드리스 모드 실행 여부
            existing_driver: 기존 브라우저 드라이버 (재사용할 경우)
        """
        self.account_id = account_id
        self.headless = headless
        self.existing_driver = existing_driver
        self.account_manager = AccountManager()
        self.login_manager = None
        self.step4_automation = None
        
        logger.info(f"Step4Core 초기화 - 계정: {account_id}, 헤드리스: {headless}, 기존드라이버: {'있음' if existing_driver else '없음'}")
    
    def initialize(self) -> bool:
        """
        4단계 자동화 초기화
        
        Returns:
            bool: 초기화 성공 여부
        """
        try:
            logger.info("4단계 자동화 초기화 시작")
            
            # 계정 정보 로드
            if not self.account_manager.load_accounts():
                logger.error("계정 정보 로드 실패")
                return False
            
            # 계정 선택 - 이메일 주소 또는 인덱스로 찾기
            account_info = None
            
            # 먼저 이메일 주소로 찾기 시도
            for account in self.account_manager.accounts:
                if account.get('id') == self.account_id or account.get('email') == self.account_id:
                    account_info = account
                    break
            
            # 이메일로 찾지 못했으면 숫자 인덱스로 시도
            if account_info is None:
                try:
                    account_index = int(self.account_id) - 1
                    if 0 <= account_index < len(self.account_manager.accounts):
                        account_info = self.account_manager.accounts[account_index]
                except ValueError:
                    pass
            
            if account_info is None:
                logger.error(f"계정 {self.account_id}를 찾을 수 없습니다 (총 {len(self.account_manager.accounts)}개 계정 중)")
                return False
            
            logger.info(f"선택된 계정: {account_info.get('nickname', 'Unknown')}")
            
            # 로그인 매니저 초기화
            self.login_manager = PercentyLogin(
                driver=None,
                account=account_info
            )
            
            # 브라우저 드라이버 설정 (기존 드라이버가 없는 경우에만)
            if self.existing_driver is None:
                logger.info("브라우저 드라이버 설정 시작")
                if not self.login_manager.setup_driver():
                    logger.error("브라우저 드라이버 설정 실패")
                    return False
                logger.info("브라우저 드라이버 설정 완료")
            else:
                logger.info("기존 브라우저 드라이버 사용")
                self.login_manager.driver = self.existing_driver
            
            # 로그인 실행
            logger.info("로그인 시작")
            if not self.login_manager.login():
                logger.error("로그인 실패")
                return False
            
            logger.info("로그인 성공")
            
            # 4단계 자동화 객체 초기화
            self.step4_automation = PercentyNewStep4(self.login_manager.driver)
            
            logger.info("4단계 자동화 초기화 완료")
            return True
            
        except Exception as e:
            logger.error(f"4단계 자동화 초기화 중 오류: {e}")
            return False
    
    def run_automation(self, quantity: int = None) -> Dict[str, Any]:
        """
        4단계 자동화 실행
        
        Args:
            quantity (int, optional): 배치 설정 수량 (사용되지 않음 - 번역 가능한 수량에 따라 자동 결정)
        
        Returns:
            Dict[str, Any]: 실행 결과
                - success (bool): 성공 여부
                - message (str): 결과 메시지
                - skipped (bool): 스킵 여부
                - reason (str): 스킵 이유 (스킵된 경우)
                - processed_count (int): 처리된 상품 수 (성공한 경우)
        """
        result = {
            'success': False,
            'message': '',
            'skipped': False,
            'reason': '',
            'processed_count': 0
        }
        
        try:
            if not self.step4_automation:
                result['message'] = "4단계 자동화가 초기화되지 않았습니다"
                return result
            
            logger.info("4단계 자동화 실행 시작")
            
            # 4단계 자동화 실행
            # percenty_new_step4.py의 run_step4_automation() 메서드 호출
            automation_result = self.step4_automation.run_step4_automation()
            
            if automation_result:
                # 성공
                result['success'] = True
                result['message'] = "4단계 자동화가 성공적으로 완료되었습니다"
                logger.info("4단계 자동화 성공")
            else:
                # 실패 또는 스킵
                # percenty_new_step4.py에서 False를 반환하는 경우는
                # 번역 가능한 상품이 부족하여 스킵된 경우입니다
                result['skipped'] = True
                result['success'] = True  # 스킵도 정상적인 완료로 간주
                result['message'] = "4단계 자동화가 스킵되었습니다"
                result['reason'] = "번역 가능한 상품 수량 부족"
                logger.info("4단계 자동화 스킵: 번역 가능한 상품 수량 부족")
            
            return result
            
        except Exception as e:
            logger.error(f"4단계 자동화 실행 중 오류: {e}")
            result['message'] = f"4단계 자동화 실행 중 오류: {str(e)}"
            return result
    
    def initialize_with_existing_driver(self) -> bool:
        """
        기존 드라이버를 사용하여 4단계 자동화 초기화
        
        Returns:
            bool: 초기화 성공 여부
        """
        try:
            logger.info("기존 드라이버로 4단계 자동화 초기화 시작")
            
            # 계정 정보 로드
            if not self.account_manager.load_accounts():
                logger.error("계정 정보 로드 실패")
                return False
            
            # 계정 선택
            account_info = None
            
            # 먼저 이메일 주소로 찾기 시도
            for account in self.account_manager.accounts:
                if account.get('id') == self.account_id or account.get('email') == self.account_id:
                    account_info = account
                    break
            
            # 이메일로 찾지 못했으면 숫자 인덱스로 시도
            if account_info is None:
                try:
                    account_index = int(self.account_id) - 1
                    if 0 <= account_index < len(self.account_manager.accounts):
                        account_info = self.account_manager.accounts[account_index]
                except ValueError:
                    pass
            
            if account_info is None:
                logger.error(f"계정 {self.account_id}를 찾을 수 없습니다")
                return False
            
            logger.info(f"선택된 계정: {account_info.get('nickname', 'Unknown')}")
            
            # 로그인 매니저 초기화 (기존 드라이버 사용)
            self.login_manager = PercentyLogin(
                driver=self.existing_driver,
                account=account_info
            )
            
            # 로그인 상태 확인 및 필요시 재로그인
            logger.info("로그인 상태 확인 및 모달창 처리 시작")
            if not self.login_manager.login():
                logger.error("로그인 실패")
                return False
            
            logger.info("로그인 상태 확인 및 모달창 처리 완료")
            
            # 4단계 자동화 객체 초기화 (기존 드라이버 사용)
            self.step4_automation = PercentyNewStep4(self.existing_driver)
            
            logger.info("기존 드라이버로 4단계 자동화 초기화 완료")
            return True
            
        except Exception as e:
            logger.error(f"기존 드라이버로 4단계 자동화 초기화 중 오류: {e}")
            return False
    
    def cleanup(self):
        """
        리소스 정리
        """
        try:
            # 기존 드라이버를 사용한 경우에는 종료하지 않음
            if self.existing_driver is None and self.login_manager and hasattr(self.login_manager, 'driver'):
                logger.info("브라우저 드라이버 종료")
                self.login_manager.driver.quit()
        except Exception as e:
            logger.error(f"리소스 정리 중 오류: {e}")
    
    def __enter__(self):
        """컨텍스트 매니저 진입"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        self.cleanup()

def run_step4_for_account(account_id: str, quantity: int = None, headless: bool = False, driver=None) -> Dict[str, Any]:
    """
    특정 계정에 대해 4단계 자동화 실행
    
    Args:
        account_id (str): 계정 ID (1, 2, 3, 4 등)
        quantity (int, optional): 배치 설정 수량 (사용되지 않음)
        headless (bool): 헤드리스 모드 실행 여부
        driver: 기존 브라우저 드라이버 (제공되면 재사용, 없으면 새로 생성)
    
    Returns:
        Dict[str, Any]: 실행 결과
    """
    logger.info(f"계정 {account_id}에 대한 4단계 자동화 시작")
    
    # 기존 드라이버가 제공된 경우 재사용, 없으면 새로 생성
    if driver:
        logger.info("기존 브라우저 드라이버 재사용")
        core = Step4Core(account_id, headless, existing_driver=driver)
        
        # 초기화 (브라우저 생성 없이)
        if not core.initialize_with_existing_driver():
            return {
                'success': False,
                'message': '4단계 자동화 초기화 실패 (기존 드라이버)',
                'skipped': False,
                'reason': '',
                'processed_count': 0
            }
        
        # 자동화 실행
        result = core.run_automation(quantity)
        
        # 기존 드라이버 사용 시에는 cleanup하지 않음
        logger.info(f"계정 {account_id} 4단계 자동화 완료: {result['message']}")
        return result
    else:
        logger.info("새 브라우저 드라이버 생성")
        with Step4Core(account_id, headless) as core:
            # 초기화
            if not core.initialize():
                return {
                    'success': False,
                    'message': '4단계 자동화 초기화 실패',
                    'skipped': False,
                    'reason': '',
                    'processed_count': 0
                }
            
            # 자동화 실행
            result = core.run_automation(quantity)
            
            logger.info(f"계정 {account_id} 4단계 자동화 완료: {result['message']}")
            return result

def main():
    """
    메인 함수 - CLI에서 직접 실행할 때 사용
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='4단계 자동화 실행')
    parser.add_argument('--account', type=str, required=True, help='계정 ID (1, 2, 3, 4 등)')
    parser.add_argument('--quantity', type=int, help='배치 설정 수량 (사용되지 않음)')
    parser.add_argument('--headless', action='store_true', help='헤드리스 모드 실행')
    
    args = parser.parse_args()
    
    # 4단계 자동화 실행
    result = run_step4_for_account(
        account_id=args.account,
        quantity=args.quantity or 10,  # 기본값 10 설정
        headless=args.headless
    )
    
    # 결과 출력
    print(f"\n=== 4단계 자동화 결과 ===")
    print(f"성공: {result['success']}")
    print(f"메시지: {result['message']}")
    if result['skipped']:
        print(f"스킵 이유: {result['reason']}")
    if result['processed_count'] > 0:
        print(f"처리된 상품 수: {result['processed_count']}")
    
    # 종료 코드 설정
    if result['success']:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()