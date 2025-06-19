# -*- coding: utf-8 -*-
"""
5단계_1 코어 로직
퍼센티 자동화 5단계_1 작업의 핵심 비즈니스 로직
"""

import os
import sys
import time
import logging
import traceback
from typing import Dict, List, Optional, Union, Tuple

# 루트 디렉토리를 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 기존 모듈들 임포트 (루트에서)
try:
    from product_editor_core5_1 import ProductEditorCore5_1
except ImportError as e:
    logging.error(f"ProductEditorCore5_1 import 실패: {e}")
    ProductEditorCore5_1 = None
from browser_core import BrowserCore
from login_percenty import PercentyLogin
from menu_clicks import MenuClicks
from coordinates.coordinates_all import MENU
from timesleep import DELAY_STANDARD, DELAY_SHORT
from human_delay import HumanLikeDelay
from ui_elements import UI_ELEMENTS
from click_utils import smart_click

# 공통 함수들 임포트
from core.common.modal_handler import handle_post_login_modals, hide_channel_talk, close_modal_dialogs
from core.common.navigation_handler import navigate_to_ai_sourcing, navigate_to_group_management5
from core.common.product_handler import check_toggle_state, toggle_product_view
from core.common.ui_handler import periodic_ui_cleanup, ensure_clean_ui_before_action

logger = logging.getLogger(__name__)

class Step5_1Core:
    """
    5단계_1 작업의 핵심 로직을 담당하는 클래스
    대기1 그룹에서 상품 복제 및 최적화 작업 수행
    """
    
    def __init__(self, driver=None):
        """
        초기화
        
        Args:
            driver: Selenium WebDriver 인스턴스
        """
        self.driver = driver
        self.browser_core = None
        self.login_manager = None
        self.menu_clicks = None
        self.delay = HumanLikeDelay()
        self.product_editor = None
        
        if driver:
            self.setup_managers()
    
    def setup_managers(self):
        """관리자 객체들 설정"""
        try:
            logger.info("BrowserCore 인스턴스 생성 시작")
            # BrowserCore는 driver를 매개변수로 받지 않으므로 인스턴스만 생성
            self.browser_core = BrowserCore()
            # driver를 별도로 설정
            self.browser_core.driver = self.driver
            logger.info("BrowserCore 인스턴스 생성 완료")
            
            logger.info("PercentyLogin 인스턴스 생성 시작")
            self.login_manager = PercentyLogin(self.driver)
            logger.info("PercentyLogin 인스턴스 생성 완료")
            
            logger.info("MenuClicks 인스턴스 생성 시작")
            self.menu_clicks = MenuClicks(self.driver)
            logger.info("MenuClicks 인스턴스 생성 완료")
            
            logger.info("5단계_1 코어 관리자 객체들이 설정되었습니다.")
        except Exception as e:
            logger.error(f"관리자 객체 설정 중 오류: {e}")
            logger.error(f"오류 상세: {traceback.format_exc()}")
            raise
    
    def execute_step5_1_with_browser_restart(self, quantity: int = 1, chunk_size: int = 10, account_info: Dict = None) -> Dict:
        """
        5단계_1 작업 실행 (브라우저 재시작 방식)
        메모리 사용량 최적화를 위해 지정된 수량마다 브라우저를 재시작
        
        Args:
            quantity: 처리할 상품 수량
            chunk_size: 브라우저 재시작 간격 (기본값: 20)
            account_info: 계정 정보 (엑셀 파일에서 읽은 계정 정보)
            
        Returns:
            Dict: 실행 결과
        """
        total_result = {
            'success': False,
            'processed': 0,
            'failed': 0,
            'errors': [],
            'chunks_completed': 0,
            'total_chunks': 0
        }
        
        try:
            # 총 청크 수 계산
            total_chunks = (quantity + chunk_size - 1) // chunk_size
            total_result['total_chunks'] = total_chunks
            
            logger.info(f"5단계_1 배치 작업 시작 - 총 {quantity}개 상품을 {total_chunks}개 청크로 처리")
            
            remaining_quantity = quantity
            
            for chunk_idx in range(total_chunks):
                current_chunk_size = min(chunk_size, remaining_quantity)
                
                logger.info(f"청크 {chunk_idx + 1}/{total_chunks} 시작 - {current_chunk_size}개 상품 처리")
                
                try:
                    # 청크 실행
                    chunk_result = self.execute_step5_1(current_chunk_size, account_info)
                    
                    # 결과 누적
                    total_result['processed'] += chunk_result.get('processed', 0)
                    total_result['failed'] += chunk_result.get('failed', 0)
                    if chunk_result.get('errors'):
                        total_result['errors'].extend(chunk_result['errors'])
                    
                    total_result['chunks_completed'] += 1
                    
                    logger.info(f"청크 {chunk_idx + 1} 완료 - 처리: {chunk_result.get('processed', 0)}, 실패: {chunk_result.get('failed', 0)}")
                    
                    # 마지막 청크가 아니면 브라우저 재시작
                    if chunk_idx < total_chunks - 1:
                        logger.info("다음 청크를 위해 브라우저 재시작")
                        self.cleanup()
                        # 여기서 브라우저 재시작 로직이 상위에서 처리됨
                        
                except Exception as e:
                    error_msg = f"청크 {chunk_idx + 1} 실행 중 오류: {str(e)}"
                    logger.error(error_msg)
                    total_result['errors'].append(error_msg)
                    total_result['failed'] += current_chunk_size
                
                remaining_quantity -= current_chunk_size
            
            # 전체 성공 여부 판단
            total_result['success'] = total_result['processed'] > 0 and total_result['failed'] == 0
            
            logger.info(f"5단계_1 배치 작업 완료 - 총 처리: {total_result['processed']}, 실패: {total_result['failed']}")
            
        except Exception as e:
            error_msg = f"5단계_1 배치 작업 중 치명적 오류: {str(e)}"
            logger.error(error_msg)
            total_result['errors'].append(error_msg)
            total_result['success'] = False
        
        return total_result
    
    def execute_step5_1(self, quantity: int = 1, account_info: Dict = None) -> Dict:
        """
        5단계_1 작업 실행
        
        Args:
            quantity: 처리할 상품 수량
            account_info: 계정 정보 (엑셀 파일에서 읽은 계정 정보)
            
        Returns:
            Dict: 실행 결과
        """
        result = {
            'success': False,
            'processed': 0,
            'failed': 0,
            'errors': [],
            'initial_count': 0,
            'final_count': 0
        }
        
        try:
            logger.info(f"5단계_1 작업 시작 - 처리 예정 수량: {quantity}")
            
            # 1. 로그인 후 모달 처리
            if not self._handle_post_login_modals():
                logger.warning("로그인 후 모달 처리 실패 - 하지만 작업을 계속 진행합니다")
            
            # 2. 채널톡 숨기기
            if not self._hide_channel_talk():
                logger.warning("채널톡 숨기기 실패 - 계속 진행")
            
            # 3. 계정 일치 확인 (5단계_1 특별 요구사항) - 선택적 확인
            if account_info:
                try:
                    logger.info(f"계정 매핑 확인 시작 - 가상ID: {account_info.get('id', 'Unknown')}")
                    if not self._verify_account_match(account_info):
                        logger.warning("계정 일치 확인 실패 - 하지만 작업을 계속 진행합니다")
                        logger.warning("이는 정상적인 동작일 수 있습니다 (계정 정보 검색 실패 등)")
                except Exception as e:
                    logger.warning(f"계정 일치 확인 중 오류 발생 - 계속 진행합니다: {e}")
                    logger.warning("이 오류는 작업 진행에 영향을 주지 않습니다")
            
            # 4. AI 소싱 메뉴로 이동
            if not navigate_to_ai_sourcing(self.driver, self.menu_clicks):
                raise Exception("AI 소싱 메뉴 이동 실패")
            
            # 5. 그룹상품관리로 이동
            if not navigate_to_group_management5(self.driver, self.menu_clicks):
                raise Exception("그룹상품관리 이동 실패")
            
            # 6. 대기1 그룹으로 이동 및 상품 확인
            logger.info("대기1 그룹으로 이동하여 상품 확인")
            # 실제 그룹 이동 로직은 ProductEditorCore5_1에서 처리
            
            # 7. 상품 처리 루프
            processed_count = 0
            failed_count = 0
            
            for i in range(quantity):
                try:
                    logger.info(f"===== 상품 {i+1}/{quantity} 작업 시작 =====")
                    
                    # 각 상품마다 새로운 지연 전략 생성 (step1_core.py와 동일한 방식)
                    delay_strategy = HumanLikeDelay(min_total_delay=152, max_total_delay=160, current_speed=150, expected_actions=25)
                    
                    # 작업 시작 전 지연
                    pre_action_delay = delay_strategy.get_delay('transition')
                    logger.info(f"작업 시작 전 지연: {pre_action_delay:.2f}초")
                    time.sleep(pre_action_delay)
                    
                    # 개별 상품 처리
                    start_time = time.time()
                    success = self._process_single_product(i, account_info)
                    actual_process_time = time.time() - start_time
                    
                    if success:
                        processed_count += 1
                        logger.info(f"상품 {i} 처리 완료 (소요시간: {actual_process_time:.2f}초, 누적: {processed_count}/{quantity})")
                        
                        # 작업 성공 후 지연
                        post_action_delay = delay_strategy.get_delay('critical')
                        logger.info(f"작업 완료 후 지연: {post_action_delay:.2f}초")
                        time.sleep(post_action_delay)
                    else:
                        failed_count += 1
                        logger.warning(f"상품 {i+1} 처리 실패 (실패 누적: {failed_count})")
                        
                        # 대기1 그룹에 상품이 없어서 실패한 경우 배치 중단
                        if hasattr(self, 'product_editor') and self.product_editor and \
                           hasattr(self.product_editor, '_last_termination_reason') and \
                           self.product_editor._last_termination_reason == 'no_products_in_daegi1':
                            logger.warning("대기1 그룹에 상품이 없어 배치 처리를 중단합니다.")
                            result['should_stop_batch'] = True
                            break
                    
                except Exception as e:
                    failed_count += 1
                    error_msg = f"상품 {i+1} 처리 중 예외 발생: {str(e)}"
                    logger.error(error_msg)
                    result['errors'].append(error_msg)
                    
                    # 오류 발생 시에도 계속 진행
                    continue
                
                # 남은 지연 적용 (목표 시간에 맞추기 위함)
                remaining_delay = delay_strategy.get_remaining_delay()
                if remaining_delay > 0:
                    logger.info(f"추가 지연 적용: {remaining_delay:.2f}초")
                    time.sleep(remaining_delay)
                
                # 상태 출력
                print(f"진행 상황: {i+1}/{quantity} (성공: {processed_count}, 실패: {failed_count})")
            
            # 9. 결과 분석 및 로깅
            result['processed'] = processed_count
            result['failed'] = failed_count
            result['success'] = processed_count > 0
            
            logger.info(f"5단계_1 작업 완료 - 처리: {processed_count}, 실패: {failed_count}")
            
        except Exception as e:
            error_msg = f"5단계_1 작업 실행 중 오류: {str(e)}"
            logger.error(error_msg)
            result['errors'].append(error_msg)
            result['success'] = False
        
        return result
    
    def _handle_post_login_modals(self) -> bool:
        """로그인 후 모달 처리"""
        try:
            return handle_post_login_modals(self.driver)
        except Exception as e:
            logger.error(f"로그인 후 모달 처리 중 오류: {e}")
            return False
    
    def _hide_channel_talk(self) -> bool:
        """채널톡 숨기기"""
        try:
            return hide_channel_talk(self.driver)
        except Exception as e:
            logger.error(f"채널톡 숨기기 중 오류: {e}")
            return False
    
    def _verify_account_match(self, account_info: Dict) -> bool:
        """
        로그인한 계정과 엑셀 파일의 계정 일치 확인
        
        Args:
            account_info: 엑셀 파일에서 읽은 계정 정보
            
        Returns:
            bool: 계정 일치 여부
        """
        try:
            logger.info(f"계정 매핑 확인 시작 - 전달받은 account_info: {account_info}")
            
            # 현재 로그인된 계정 정보 가져오기
            current_account = self._get_current_logged_account()
            
            if not current_account:
                logger.warning("현재 로그인된 계정 정보를 가져올 수 없습니다 - 이는 페이지 로딩 지연이나 UI 변경으로 인한 일시적 문제일 수 있습니다")
                return False
            
            # 계정 일치 확인 (엑셀에서 파싱된 정보는 'id' 키 사용)
            excel_account_virtual = account_info.get('id', '').strip()
            
            if not excel_account_virtual:
                logger.warning("엑셀에서 계정 ID를 찾을 수 없습니다 - account_info에 'id' 키가 없거나 비어있습니다")
                return False
            
            # 가상 계정 ID를 실제 이메일로 변환
            from batch.batch_manager import get_real_account_id
            excel_account_real = get_real_account_id(excel_account_virtual)
            
            logger.info(f"계정 매핑 상세정보:")
            logger.info(f"  - 현재 로그인 계정: {current_account}")
            logger.info(f"  - 엑셀 가상 ID: {excel_account_virtual}")
            logger.info(f"  - 엑셀 실제 ID: {excel_account_real}")
            
            if current_account.lower() == excel_account_real.lower():
                logger.info(f"✅ 계정 일치 확인 완료: {current_account}")
                return True
            else:
                logger.warning(f"⚠️ 계정 불일치 감지:")
                logger.warning(f"  - 로그인된 계정: {current_account}")
                logger.warning(f"  - 엑셀 파일 계정(가상): {excel_account_virtual}")
                logger.warning(f"  - 엑셀 파일 계정(실제): {excel_account_real}")
                logger.warning(f"이는 다음 원인일 수 있습니다:")
                logger.warning(f"  1. 다른 계정으로 로그인됨")
                logger.warning(f"  2. 계정 정보 검색 실패 (일시적 UI 문제)")
                logger.warning(f"  3. 계정 매핑 테이블 불일치")
                return False
                
        except Exception as e:
            logger.error(f"계정 일치 확인 중 오류: {e}")
            return False
    
    def _get_current_logged_account(self) -> Optional[str]:
        """
        현재 로그인된 계정 정보 가져오기 - 개선된 버전
        
        Returns:
            str: 현재 로그인된 계정 ID (이메일)
        """
        try:
            import re
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            logger.info("현재 로그인된 계정 정보 검색 시작")
            
            # 1. 퍼센티 특화 셀렉터들로 검색
            percenty_selectors = [
                # 헤더 영역 사용자 정보
                ".ant-layout-header [class*='user']",
                ".ant-layout-header [class*='account']",
                ".ant-layout-header [class*='profile']",
                ".ant-layout-header .ant-dropdown-trigger",
                ".ant-layout-header .ant-avatar",
                
                # 사이드바 사용자 정보
                ".ant-layout-sider [class*='user']",
                ".ant-layout-sider [class*='account']",
                ".ant-layout-sider [class*='profile']",
                
                # 일반적인 사용자 정보 영역
                "[data-testid*='user']",
                "[data-testid*='account']",
                "[data-testid*='profile']",
                "[aria-label*='user']",
                "[aria-label*='account']",
                "[title*='@']",
                
                # 드롭다운 메뉴 관련
                ".ant-dropdown [class*='user']",
                ".ant-dropdown [class*='account']",
                ".ant-dropdown-menu-item",
                
                # 기존 셀렉터들
                "[data-testid='user-email']",
                ".user-email",
                "#user-email",
                ".account-info .email",
                ".user-info .email",
                "[class*='email']",
                "[id*='email']",
                ".header .user-info",
                ".navbar .user-info"
            ]
            
            # 짧은 대기 시간으로 빠른 검색
            wait = WebDriverWait(self.driver, 2)
            
            for selector in percenty_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        # 텍스트 내용 확인
                        text = element.text.strip()
                        if text and '@' in text and '.' in text:
                            # 이메일 패턴 검증
                            email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
                            if email_match:
                                email = email_match.group()
                                logger.info(f"셀렉터 '{selector}'에서 계정 발견: {email}")
                                return email
                        
                        # 속성값도 확인
                        for attr in ['title', 'data-user', 'data-account', 'aria-label', 'placeholder', 'value']:
                            attr_value = element.get_attribute(attr)
                            if attr_value and '@' in attr_value:
                                email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', attr_value)
                                if email_match:
                                    email = email_match.group()
                                    logger.info(f"속성 '{attr}'에서 계정 발견: {email}")
                                    return email
                except Exception as e:
                    continue
            
            # 2. DOM 전체에서 이메일 패턴 검색
            try:
                logger.debug("DOM 전체에서 이메일 패턴 검색")
                all_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '@')]")
                email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
                
                for element in all_elements[:50]:  # 처음 50개만 검사
                    try:
                        text = element.text.strip()
                        if text:
                            emails = email_pattern.findall(text)
                            if emails:
                                email = emails[0]  # 첫 번째 이메일 사용
                                logger.info(f"DOM 검색에서 계정 발견: {email}")
                                return email
                    except Exception as e:
                        continue
            except Exception as e:
                logger.debug(f"DOM 검색 실패: {e}")
            
            # 3. JavaScript로 계정 정보 찾기 시도
            try:
                logger.debug("JavaScript로 계정 정보 검색")
                js_scripts = [
                    # 일반적인 사용자 정보
                    "return window.user?.email || window.user;",
                    "return window.currentUser?.email || window.currentUser;",
                    "return window.userInfo?.email || window.userInfo;",
                    "return window.account?.email || window.account;",
                    "return window.accountInfo?.email || window.accountInfo;",
                    
                    # 로컬/세션 스토리지
                    "return localStorage.getItem('user') || localStorage.getItem('userInfo') || localStorage.getItem('account') || localStorage.getItem('email');",
                    "return sessionStorage.getItem('user') || sessionStorage.getItem('userInfo') || sessionStorage.getItem('account') || sessionStorage.getItem('email');",
                    
                    # DOM 검색
                    "return document.querySelector('[data-user-email]')?.getAttribute('data-user-email');",
                    "return [...document.querySelectorAll('*')].find(el => el.textContent && el.textContent.includes('@'))?.textContent;",
                    "return [...document.querySelectorAll('[title]')].find(el => el.title && el.title.includes('@'))?.title;"
                ]
                
                for script in js_scripts:
                    try:
                        result = self.driver.execute_script(script)
                        if result:
                            result_str = str(result).strip()
                            if '@' in result_str:
                                # JSON 파싱 시도
                                try:
                                    import json
                                    if result_str.startswith('{') or result_str.startswith('['):
                                        data = json.loads(result_str)
                                        if isinstance(data, dict):
                                            email = data.get('email') or data.get('user') or data.get('account')
                                            if email and '@' in str(email):
                                                logger.info(f"JavaScript JSON에서 계정 발견: {email}")
                                                return str(email).strip()
                                except:
                                    pass
                                
                                # 직접 이메일 패턴 검색
                                email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', result_str)
                                if email_match:
                                    email = email_match.group()
                                    logger.info(f"JavaScript에서 계정 발견: {email}")
                                    return email
                    except Exception as js_error:
                        continue
                        
            except Exception as e:
                logger.debug(f"JavaScript 계정 정보 추출 실패: {e}")
            
            # 4. 페이지 소스에서 검색 (최후의 수단)
            try:
                logger.debug("페이지 소스에서 이메일 패턴 검색")
                page_source = self.driver.page_source
                email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
                emails = email_pattern.findall(page_source)
                
                if emails:
                    # 가장 가능성 높은 이메일 선택 (중복 제거 후 첫 번째)
                    unique_emails = list(set(emails))
                    email = unique_emails[0]
                    logger.info(f"페이지 소스에서 계정 발견: {email}")
                    return email
                    
            except Exception as e:
                logger.debug(f"페이지 소스 검색 실패: {e}")
            
            logger.warning("현재 로그인된 계정 정보를 찾을 수 없습니다")
            return None
            
        except Exception as e:
            logger.error(f"현재 로그인된 계정 정보 가져오기 중 오류: {e}")
            return None
    

    
    def _process_single_product(self, index: int, account_info: Dict = None) -> bool:
        """
        단일 상품 처리 (5단계_1 전용)
        product_editor_core5_1.py의 배치 처리 방식을 사용
        
        Args:
            index: 상품 인덱스 (step1_core.py와 동일한 방식)
            account_info: 계정 정보 (엑셀에서 파싱된 정보)
            
        Returns:
            bool: 처리 성공 여부
        """
        try:
            logger.info(f"단일 상품 {index} 처리 시작 (코어5 배치 방식)")
            
            # ProductEditorCore5_1 인스턴스 생성 (필요시)
            if not self.product_editor:
                if ProductEditorCore5_1 is None:
                    raise ImportError("ProductEditorCore5_1 클래스를 import할 수 없습니다. product_editor_core5_1.py 파일을 확인하세요.")
                self.product_editor = ProductEditorCore5_1(self.driver)
            
            # 계정 정보에서 account_id 추출
            # account_info는 엑셀에서 파싱된 정보이므로 'id' 키를 사용
            account_id_virtual = account_info.get('id', '') if account_info else ''
            if not account_id_virtual:
                logger.error("계정 ID가 없습니다")
                return False
            
            # 가상 계정 ID를 실제 이메일로 변환
            from batch.batch_manager import get_real_account_id
            account_id = get_real_account_id(account_id_virtual)
            
            logger.info(f"계정 ID: {account_id_virtual} -> {account_id}로 상품 복제 및 최적화 시작")
            
            # 코어5의 전체 배치 처리 프로세스 실행:
            # - 등록A 상품 모두 복제X로 이동
            # - 대기1 그룹에서 첫번째 상품을 등록A로 이동
            # - 상품 복사 3회 (1개 -> 4개)
            # - 각 복사된 상품 최적화 (접미사, 할인율, 썸네일)
            # - 원본 상품 최적화 및 그룹 이동
            success = self.product_editor.process_product_copy_and_optimization(account_id)
            
            # 대기1 그룹에 상품이 없어서 배치가 중단된 경우 체크
            if hasattr(self.product_editor, '_last_termination_reason') and \
               self.product_editor._last_termination_reason == 'no_products_in_daegi1':
                logger.warning("대기1 그룹에 상품이 없어 배치 처리를 중단합니다.")
                return False
            
            if success:
                logger.info("단일 상품 처리 완료 (코어5 배치 방식)")
                return True
            else:
                logger.error("단일 상품 처리 실패 (코어5 배치 방식)")
                return False
                
        except Exception as e:
            logger.error(f"단일 상품 처리 중 오류: {e}")
            
            # 오류 발생 시 모달창 닫기 시도
            try:
                close_modal_dialogs(self.driver)
            except:
                pass
                
            return False
    
    def cleanup(self):
        """정리 작업"""
        try:
            if self.product_editor:
                # ProductEditorCore5_1에 cleanup 메서드가 있다면 호출
                if hasattr(self.product_editor, 'cleanup'):
                    self.product_editor.cleanup()
            
            logger.info("5단계_1 코어 정리 작업 완료")
        except Exception as e:
            logger.error(f"정리 작업 중 오류: {e}")

# 레거시 호환성을 위한 함수
def execute_step5_1_legacy(driver, quantity: int = 1) -> Dict:
    """
    레거시 호환성을 위한 5단계_1 실행 함수
    
    Args:
        driver: Selenium WebDriver 인스턴스
        quantity: 처리할 상품 수량
        
    Returns:
        Dict: 실행 결과
    """
    step5_1_core = Step5_1Core(driver)
    return step5_1_core.execute_step5_1(quantity)

# 테스트용 메인 실행 블록
if __name__ == "__main__":
    # 테스트 실행
    print("Step5_1Core 테스트 실행")
    # 실제 테스트 코드는 별도 테스트 파일에서 구현