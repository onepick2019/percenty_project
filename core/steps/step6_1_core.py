# -*- coding: utf-8 -*-
"""
6-1단계 코어 로직
퍼센티 자동화 6-1단계 작업의 핵심 비즈니스 로직

percenty_id.xlsx의 market_id 시트를 파싱하여 동적으로 업로드를 진행합니다.
- 로그인 아이디와 매핑되는 행들을 순차적으로 처리
- 11번가 마켓 설정 및 API 연동
- 신규상품등록에서 동적 그룹 선택 및 업로드 진행
"""

import os
import sys
import time
import logging
from typing import Dict, List, Optional, Union, Tuple

# 루트 디렉토리를 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 기존 모듈들 임포트 (루트에서)
from product_editor_core6_dynamic_1 import ProductEditorCore6_Dynamic1

from browser_core import BrowserCore
from login_percenty import PercentyLogin
from menu_clicks import MenuClicks
from coordinates.coordinates_all import MENU
from timesleep import DELAY_STANDARD, DELAY_SHORT
from human_delay import HumanLikeDelay
from ui_elements import UI_ELEMENTS
from click_utils import smart_click
from account_manager import AccountManager

# 공통 함수들 임포트
from core.common.modal_handler import handle_post_login_modals, hide_channel_talk, close_modal_dialogs
from core.common.navigation_handler import navigate_to_ai_sourcing, navigate_to_group_management, switch_to_non_group_view
from core.common.product_handler import check_product_count, check_toggle_state, toggle_product_view
from core.common.ui_handler import periodic_ui_cleanup, ensure_clean_ui_before_action

logger = logging.getLogger(__name__)

class Step6_1Core:
    """
    6-1단계 작업의 핵심 로직을 담당하는 클래스
    기존 코드의 기능을 유지하면서 모듈화
    """
    
    def __init__(self, driver=None):
        """
        초기화
        
        Args:
            driver: 웹드라이버 인스턴스 (선택적)
        """
        self.driver = driver
        self.browser_core = None
        self.login_handler = None
        self.menu_handler = None
        self.delay = HumanLikeDelay()
        
        # 실행 상태 추적
        self.is_running = False
        self.current_account = None
        
        logger.info("Step6_1Core 초기화 완료")
    
    def initialize_browser(self, headless: bool = False) -> bool:
        """
        브라우저 초기화
        
        Args:
            headless: 헤드리스 모드 여부
            
        Returns:
            bool: 초기화 성공 여부
        """
        try:
            if not self.driver:
                self.browser_core = BrowserCore()
                if not self.browser_core.setup_driver(headless=headless):
                    logger.error("브라우저 드라이버 설정 실패")
                    return False
                self.driver = self.browser_core.driver
                
                if not self.driver:
                    logger.error("브라우저 초기화 실패")
                    return False
            
            # 핸들러들 초기화
            self.login_handler = PercentyLogin(self.driver)
            self.menu_handler = MenuClicks(self.driver)
            
            logger.info("브라우저 초기화 완료")
            return True
            
        except Exception as e:
            logger.error(f"브라우저 초기화 중 오류: {e}")
            return False
    
    def cleanup_browser(self):
        """
        브라우저 정리
        """
        try:
            if self.browser_core:
                self.browser_core.close_driver()
                self.browser_core = None
                self.driver = None
                logger.info("브라우저 정리 완료")
        except Exception as e:
            logger.error(f"브라우저 정리 중 오류: {e}")
    
    def execute_step(self, account_id: str, quantity: int = 100, **kwargs) -> Dict[str, Union[bool, str, int]]:
        """
        6-1단계 실행
        
        Args:
            account_id: 계정 ID
            quantity: 처리할 수량
            **kwargs: 추가 옵션
            
        Returns:
            Dict: 실행 결과
        """
        result = {
            'success': False,
            'account_id': account_id,
            'processed_count': 0,
            'error_message': '',
            'step': '6-1'
        }
        
        try:
            self.is_running = True
            self.current_account = account_id
            
            logger.info(f"6-1단계 시작 - 계정: {account_id}, 수량: {quantity}")
            
            # 브라우저 초기화 (필요한 경우에만)
            if not self.driver:
                logger.info("브라우저가 없어서 새로 초기화합니다")
                if not self.initialize_browser(kwargs.get('headless', False)):
                    result['error_message'] = '브라우저 초기화 실패'
                    return result
            else:
                logger.info("기존 브라우저를 재사용합니다")
                # 기존 브라우저 사용 시에도 핸들러들 초기화
                if not self.login_handler:
                    self.login_handler = PercentyLogin(self.driver)
                if not self.menu_handler:
                    self.menu_handler = MenuClicks(self.driver)
                logger.info("기존 브라우저용 핸들러 초기화 완료")
            
            # 로그인
            if not self._login(account_id):
                result['error_message'] = '로그인 실패'
                return result
            
            # 모달 처리
            self._handle_modals()
            
            # 6-1단계 핵심 로직 실행
            processed_count = self._execute_core_logic(account_id, quantity)
            
            result['success'] = True
            result['processed_count'] = processed_count
            
            logger.info(f"6-1단계 완료 - 계정: {account_id}, 처리된 수량: {processed_count}")
            
        except Exception as e:
            logger.error(f"6-1단계 실행 중 오류: {e}")
            result['error_message'] = str(e)
            
        finally:
            self.is_running = False
            self.current_account = None
            
        return result
    
    def _login(self, account_id: str) -> bool:
        """
        퍼센티 로그인 처리
        
        Args:
            account_id: 로그인할 계정 ID
            
        Returns:
            bool: 로그인 성공 여부
        """
        try:
            if not self.login_handler:
                logger.error("로그인 핸들러가 초기화되지 않았습니다")
                return False
            
            # AccountManager를 사용하여 실제 계정 정보 조회
            account_manager = AccountManager()
            if not account_manager.load_accounts():
                logger.error("계정 정보를 로드할 수 없습니다")
                return False
            
            # 계정 ID로 해당 계정 정보 찾기
            accounts = account_manager.get_accounts()
            target_account = None
            for account in accounts:
                if account['id'] == account_id:
                    target_account = account
                    break
            
            if not target_account:
                logger.error(f"계정 정보를 찾을 수 없습니다: {account_id}")
                return False
            
            # 퍼센티 로그인
            account_info = {'email': target_account['id'], 'password': target_account['password']}
            success = self.login_handler.login_percenty(account_info)
            
            if success:
                logger.info(f"로그인 성공: {account_id}")
                delay_time = self.delay.get_delay('normal')
                time.sleep(delay_time)
                return True
            else:
                logger.error(f"로그인 실패: {account_id}")
                return False
                
        except Exception as e:
            logger.error(f"로그인 처리 중 오류: {e}")
            return False
    
    def _handle_modals(self):
        """
        모달 처리
        """
        try:
            # 로그인 후 모달 처리
            handle_post_login_modals(self.driver)
            
            # 채널톡 숨기기
            hide_channel_talk(self.driver)
            
            # 기타 모달 닫기
            close_modal_dialogs(self.driver)
            
            logger.info("모달 처리 완료")
            
        except Exception as e:
            logger.error(f"모달 처리 중 오류: {e}")
    
    def _execute_core_logic(self, account_id: str, quantity: int) -> int:
        """
        6-1단계 핵심 로직 실행
        
        Args:
            account_id: 계정 ID
            quantity: 처리할 수량
            
        Returns:
            int: 처리된 수량
        """
        try:
            # ProductEditorCore6_Dynamic1 인스턴스 생성
            core_processor = ProductEditorCore6_Dynamic1(self.driver, account_id)
            
            # 마켓 설정 로드
            market_configs = core_processor.load_market_config_from_excel()
            
            if not market_configs:
                logger.warning(f"계정 {account_id}에 대한 마켓 설정이 없습니다")
                return 0
            
            processed_count = 0
            
            # 각 마켓 설정에 대해 처리
            for config in market_configs:
                try:
                    # 그룹명 확인
                    group_name = config.get('groupname', '')
                    if not group_name:
                        logger.warning("그룹명이 없는 설정을 건너뜁니다")
                        continue
                    
                    logger.info(f"그룹 '{group_name}' 처리 시작")
                    
                    # 동적 업로드 처리 실행
                    result = core_processor.execute_dynamic_upload_workflow()
                    
                    if result.get('success', False):
                        processed_count += result.get('processed_count', 0)
                        logger.info(f"그룹 '{group_name}' 처리 완료: {result.get('processed_count', 0)}개")
                    else:
                        logger.error(f"그룹 '{group_name}' 처리 실패: {result.get('error_message', '')}")
                    
                    # 다음 그룹 처리 전 대기
                    delay_time = self.delay.get_delay('medium')
                    time.sleep(delay_time)
                    
                except Exception as e:
                    logger.error(f"그룹 처리 중 오류: {e}")
                    continue
            
            return processed_count
            
        except Exception as e:
            logger.error(f"6-1단계 핵심 로직 실행 중 오류: {e}")
            return 0
    
    def stop_execution(self):
        """
        실행 중지
        """
        try:
            self.is_running = False
            logger.info("6-1단계 실행 중지 요청")
        except Exception as e:
            logger.error(f"실행 중지 중 오류: {e}")
    
    def get_status(self) -> Dict[str, Union[bool, str]]:
        """
        현재 상태 반환
        
        Returns:
            Dict: 상태 정보
        """
        return {
            'is_running': self.is_running,
            'current_account': self.current_account,
            'step': '6-1'
        }

# 하위 호환성을 위한 함수들
def execute_step6_1(account_id: str, quantity: int = 100, headless: bool = False, driver=None, **kwargs) -> Dict[str, Union[bool, str, int]]:
    """
    6-1단계 실행 함수 (하위 호환성)
    
    Args:
        account_id: 계정 ID
        quantity: 처리할 수량
        headless: 헤드리스 모드 여부
        driver: 기존 브라우저 드라이버 (제공되면 재사용, 없으면 새로 생성)
        **kwargs: 추가 옵션
        
    Returns:
        Dict: 실행 결과
    """
    # 기존 드라이버가 제공된 경우 재사용, 없으면 새로 생성
    if driver:
        logger.info("기존 브라우저 드라이버 재사용")
        step_core = Step6_1Core(driver)
        
        # 6-1단계 실행 (기존 드라이버 사용)
        result = step_core.execute_step(account_id, quantity, headless=headless, **kwargs)
        
        # 기존 드라이버 사용 시에는 cleanup하지 않음
        logger.info(f"계정 {account_id} 6-1단계 완료")
        return result
    else:
        logger.info("새 브라우저 드라이버 생성")
        step_core = Step6_1Core()
        
        try:
            # 브라우저 초기화
            if not step_core.initialize_browser(headless):
                return {
                    'success': False,
                    'account_id': account_id,
                    'processed_count': 0,
                    'error_message': '브라우저 초기화 실패',
                    'step': '6-1'
                }
            
            # 6-1단계 실행 (브라우저가 이미 초기화되었으므로 headless 옵션 전달)
            result = step_core.execute_step(account_id, quantity, headless=headless, **kwargs)
            
            return result
            
        finally:
            # 브라우저 정리
            step_core.cleanup_browser()

def get_step_info() -> Dict[str, Union[str, int]]:
    """
    단계 정보 반환
    
    Returns:
        Dict: 단계 정보
    """
    return {
        'step_number': '6-1',
        'step_name': '6-1단계 동적 업로드',
        'description': 'market_id 시트 기반 동적 업로드 처리',
        'default_quantity': 100,
        'supports_chunk': False
    }

def main():
    """
    메인 함수 - CLI에서 직접 실행할 때 사용
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='6-1단계 동적 업로드 실행')
    parser.add_argument('account_id', type=str, help='계정 ID')
    parser.add_argument('quantity', type=int, help='처리할 수량')
    parser.add_argument('--headless', action='store_true', help='헤드리스 모드 실행')
    
    args = parser.parse_args()
    
    # 6-1단계 실행
    result = execute_step6_1(
        account_id=args.account_id,
        quantity=args.quantity,
        headless=args.headless
    )
    
    # 결과 출력
    print(f"\n=== 6-1단계 동적 업로드 결과 ===")
    print(f"성공: {result['success']}")
    print(f"계정: {result['account_id']}")
    print(f"처리된 수량: {result['processed_count']}")
    if not result['success']:
        print(f"오류 메시지: {result['error_message']}")
    
    # 종료 코드 설정
    if result['success']:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()