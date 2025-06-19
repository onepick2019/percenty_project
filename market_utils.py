import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

class MarketUtils:
    """마켓 설정 관련 유틸리티 클래스"""
    
    def __init__(self, driver, logger=None):
        self.driver = driver
        self.logger = logger or logging.getLogger(__name__)
        self.wait = WebDriverWait(driver, 10)
        
        # 마켓 탭 정의 (data-node-key 기반)
        self.market_tabs = {
            'coupang': 'cp',
            'smartstore': 'ss', 
            'auction_gmarket': 'esm',
            '11st_general': 'est',
            '11st_global': 'est_global',
            'lotteon': 'lotteon',
            'kakao': 'kakao',
            'interpark': 'ip',
            'wemakeprice': 'wmp'
        }
        
        # 마켓 한글명 매핑
        self.market_names = {
            'coupang': '쿠팡',
            'smartstore': '스마트스토어',
            'auction_gmarket': '옥션/G마켓 (ESM 2.0)',
            '11st_general': '11번가-일반',
            '11st_global': '11번가-글로벌',
            'lotteon': '롯데온',
            'kakao': '톡스토어',
            'interpark': '인터파크',
            'wemakeprice': '위메프'
        }
    
    def get_market_tab_selector(self, market_key):
        """특정 마켓 탭의 선택자를 반환합니다."""
        if market_key not in self.market_tabs:
            raise ValueError(f"지원하지 않는 마켓 키: {market_key}")
        
        node_key = self.market_tabs[market_key]
        return f'div[data-node-key="{node_key}"] .ant-tabs-tab-btn'
    
    def get_market_tab_by_text_selector(self, market_text):
        """마켓 텍스트로 탭 선택자를 반환합니다."""
        return f'.ant-tabs-tab-btn:contains("{market_text}")'
    
    def get_active_market_tab_selector(self):
        """현재 활성화된 마켓 탭의 선택자를 반환합니다."""
        return '.ant-tabs-tab.ant-tabs-tab-active .ant-tabs-tab-btn'
    
    def get_all_market_tabs_selector(self):
        """모든 마켓 탭의 선택자를 반환합니다."""
        return '.ant-tabs-tab .ant-tabs-tab-btn'
    
    def click_market_tab(self, market_key):
        """특정 마켓 탭을 클릭합니다."""
        try:
            selector = self.get_market_tab_selector(market_key)
            element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            element.click()
            
            market_name = self.market_names.get(market_key, market_key)
            self.logger.info(f"{market_name} 탭 클릭 완료")
            
            # 탭 전환 완료 대기
            time.sleep(1)
            return True
            
        except TimeoutException:
            self.logger.error(f"마켓 탭 클릭 실패 - 요소를 찾을 수 없음: {market_key}")
            return False
        except Exception as e:
            self.logger.error(f"마켓 탭 클릭 중 오류 발생: {e}")
            return False
    
    def click_market_tab_by_text(self, market_text):
        """마켓 텍스트로 탭을 클릭합니다."""
        try:
            # JavaScript를 사용하여 텍스트로 요소 찾기
            script = f"""
            var tabs = document.querySelectorAll('.ant-tabs-tab-btn');
            for (var i = 0; i < tabs.length; i++) {{
                if (tabs[i].textContent.trim() === '{market_text}') {{
                    tabs[i].click();
                    return true;
                }}
            }}
            return false;
            """
            
            result = self.driver.execute_script(script)
            if result:
                self.logger.info(f"{market_text} 탭 클릭 완료")
                time.sleep(1)
                return True
            else:
                self.logger.error(f"마켓 탭을 찾을 수 없음: {market_text}")
                return False
                
        except Exception as e:
            self.logger.error(f"마켓 탭 클릭 중 오류 발생: {e}")
            return False
    
    def get_current_active_market(self):
        """현재 활성화된 마켓 탭의 텍스트를 반환합니다."""
        try:
            selector = self.get_active_market_tab_selector()
            element = self.driver.find_element(By.CSS_SELECTOR, selector)
            return element.text.strip()
        except NoSuchElementException:
            self.logger.error("활성화된 마켓 탭을 찾을 수 없음")
            return None
        except Exception as e:
            self.logger.error(f"활성화된 마켓 탭 확인 중 오류 발생: {e}")
            return None
    
    def get_available_markets(self):
        """사용 가능한 모든 마켓 목록을 반환합니다."""
        try:
            selector = self.get_all_market_tabs_selector()
            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            return [element.text.strip() for element in elements]
        except Exception as e:
            self.logger.error(f"마켓 목록 조회 중 오류 발생: {e}")
            return []
    
    def is_market_tab_active(self, market_key):
        """특정 마켓 탭이 활성화되어 있는지 확인합니다."""
        try:
            current_market = self.get_current_active_market()
            expected_market = self.market_names.get(market_key, market_key)
            return current_market == expected_market
        except Exception as e:
            self.logger.error(f"마켓 탭 활성화 상태 확인 중 오류 발생: {e}")
            return False
    
    def switch_to_market(self, market_key):
        """특정 마켓으로 전환합니다 (이미 활성화되어 있으면 스킵)."""
        if self.is_market_tab_active(market_key):
            market_name = self.market_names.get(market_key, market_key)
            self.logger.info(f"{market_name} 탭이 이미 활성화되어 있음")
            return True
        
        return self.click_market_tab(market_key)
    
    def get_market_panel_selector(self, market_key):
        """특정 마켓의 패널 선택자를 반환합니다."""
        if market_key not in self.market_tabs:
            raise ValueError(f"지원하지 않는 마켓 키: {market_key}")
        
        node_key = self.market_tabs[market_key]
        return f'div[id="rc-tabs-0-panel-{node_key}"]'
    
    def wait_for_market_panel_load(self, market_key, timeout=10):
        """특정 마켓 패널이 로드될 때까지 대기합니다."""
        try:
            panel_selector = self.get_market_panel_selector(market_key)
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, panel_selector))
            )
            market_name = self.market_names.get(market_key, market_key)
            self.logger.info(f"{market_name} 패널 로드 완료")
            return True
        except TimeoutException:
            self.logger.error(f"마켓 패널 로드 시간 초과: {market_key}")
            return False
        except Exception as e:
            self.logger.error(f"마켓 패널 로드 대기 중 오류 발생: {e}")
            return False
    
    # ==================== 마켓 설정 버튼 관련 메서드 ====================
    
    def get_api_disconnect_button_selector(self):
        """API 연결 끊기 버튼 선택자를 반환합니다."""
        return '.ant-btn.ant-btn-default span:contains("API 연결 끊기")'
    
    def get_account_setting_button_selector(self):
        """업로드할 계정 설정하기 버튼 선택자를 반환합니다."""
        return '.ant-btn.ant-btn-primary.ant-btn-background-ghost span:contains("업로드할 계정 설정하기")'
    
    def get_api_validation_button_selector(self):
        """API 검증 버튼 선택자를 반환합니다."""
        return '.ant-btn.ant-btn-primary:not(.ant-btn-background-ghost) span:contains("API 검증")'
    
    def get_market_buttons_container_selector(self):
        """마켓 설정 버튼들의 컨테이너 선택자를 반환합니다."""
        return '.ant-row.css-1li46mu[style*="margin: 0px 0px 0px auto"]'
    
    def click_api_disconnect_button(self):
        """API 연결 끊기 버튼을 클릭합니다."""
        try:
            selector = self.get_api_disconnect_button_selector()
            element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            element.click()
            self.logger.info("API 연결 끊기 버튼 클릭 완료")
            time.sleep(1)
            return True
        except TimeoutException:
            self.logger.error("API 연결 끊기 버튼을 찾을 수 없음")
            return False
        except Exception as e:
            self.logger.error(f"API 연결 끊기 버튼 클릭 중 오류 발생: {e}")
            return False
    
    def click_account_setting_button(self):
        """업로드할 계정 설정하기 버튼을 클릭합니다."""
        try:
            selector = self.get_account_setting_button_selector()
            element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            element.click()
            self.logger.info("업로드할 계정 설정하기 버튼 클릭 완료")
            time.sleep(1)
            return True
        except TimeoutException:
            self.logger.error("업로드할 계정 설정하기 버튼을 찾을 수 없음")
            return False
        except Exception as e:
            self.logger.error(f"업로드할 계정 설정하기 버튼 클릭 중 오류 발생: {e}")
            return False
    
    def click_api_validation_button(self):
        """API 검증 버튼을 클릭합니다."""
        try:
            selector = self.get_api_validation_button_selector()
            element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            element.click()
            self.logger.info("API 검증 버튼 클릭 완료")
            time.sleep(1)
            return True
        except TimeoutException:
            self.logger.error("API 검증 버튼을 찾을 수 없음")
            return False
        except Exception as e:
            self.logger.error(f"API 검증 버튼 클릭 중 오류 발생: {e}")
            return False
    
    def click_button_by_text(self, button_text):
        """버튼 텍스트로 버튼을 클릭합니다."""
        try:
            # JavaScript를 사용하여 텍스트로 버튼 찾기
            script = f"""
            var buttons = document.querySelectorAll('.ant-btn span');
            for (var i = 0; i < buttons.length; i++) {{
                if (buttons[i].textContent.trim() === '{button_text}') {{
                    buttons[i].parentElement.click();
                    return true;
                }}
            }}
            return false;
            """
            
            result = self.driver.execute_script(script)
            if result:
                self.logger.info(f"{button_text} 버튼 클릭 완료")
                time.sleep(1)
                return True
            else:
                self.logger.error(f"버튼을 찾을 수 없음: {button_text}")
                return False
                
        except Exception as e:
            self.logger.error(f"버튼 클릭 중 오류 발생: {e}")
            return False
    
    def is_button_visible(self, button_text):
        """특정 버튼이 화면에 표시되는지 확인합니다."""
        try:
            script = f"""
            var buttons = document.querySelectorAll('.ant-btn span');
            for (var i = 0; i < buttons.length; i++) {{
                if (buttons[i].textContent.trim() === '{button_text}') {{
                    var rect = buttons[i].getBoundingClientRect();
                    return rect.width > 0 && rect.height > 0;
                }}
            }}
            return false;
            """
            
            return self.driver.execute_script(script)
        except Exception as e:
            self.logger.error(f"버튼 가시성 확인 중 오류 발생: {e}")
            return False
    
    def get_available_buttons(self):
        """현재 화면에서 사용 가능한 모든 버튼 텍스트를 반환합니다."""
        try:
            script = """
            var buttons = document.querySelectorAll('.ant-btn span');
            var buttonTexts = [];
            for (var i = 0; i < buttons.length; i++) {
                var text = buttons[i].textContent.trim();
                if (text && text.length > 0) {
                    buttonTexts.push(text);
                }
            }
            return buttonTexts;
            """
            
            return self.driver.execute_script(script)
        except Exception as e:
            self.logger.error(f"버튼 목록 조회 중 오류 발생: {e}")
            return []
    
    def perform_market_setup_workflow(self, market_key, action='validate'):
        """마켓 설정 워크플로우를 수행합니다.
        
        Args:
            market_key (str): 마켓 키
            action (str): 수행할 작업 ('validate', 'disconnect', 'setup')
        """
        try:
            # 1. 마켓 탭으로 전환
            if not self.switch_to_market(market_key):
                return False
            
            # 2. 패널 로드 대기
            if not self.wait_for_market_panel_load(market_key):
                return False
            
            # 3. 요청된 작업 수행
            if action == 'validate':
                return self.click_api_validation_button()
            elif action == 'disconnect':
                return self.click_api_disconnect_button()
            elif action == 'setup':
                return self.click_account_setting_button()
            else:
                self.logger.error(f"지원하지 않는 작업: {action}")
                return False
                
        except Exception as e:
             self.logger.error(f"마켓 설정 워크플로우 중 오류 발생: {e}")
             return False
    
    # ==================== API 연결 끊기 모달창 관련 메서드 ====================
    
    def get_api_disconnect_modal_selector(self):
        """API 연결 끊기 모달창 선택자를 반환합니다."""
        return '.ant-modal-content .ant-modal-title:contains("API 연결 끊기")'
    
    def get_api_disconnect_modal_close_button_selector(self):
        """API 연결 끊기 모달창 닫기(X) 버튼 선택자를 반환합니다."""
        return '.ant-modal-content .ant-modal-close'
    
    def get_api_disconnect_modal_cancel_button_selector(self):
        """API 연결 끊기 모달창 취소 버튼 선택자를 반환합니다."""
        return '.ant-modal-footer .ant-btn-default span:contains("취소")'
    
    def get_api_disconnect_modal_confirm_button_selector(self):
        """API 연결 끊기 모달창 확인 버튼 선택자를 반환합니다."""
        return '.ant-modal-footer .ant-btn-primary.ant-btn-dangerous span:contains("API 연결 끊기")'
    
    def get_api_disconnect_modal_error_alert_selector(self):
        """API 연결 끊기 모달창 에러 알림 선택자를 반환합니다."""
        return '.ant-modal-body .ant-alert-error .ant-alert-message'
    
    def get_api_disconnect_modal_warning_alert_selector(self):
        """API 연결 끊기 모달창 경고 알림 선택자를 반환합니다."""
        return '.ant-modal-body .ant-alert-warning .ant-alert-message'
    
    def wait_for_api_disconnect_modal(self, timeout=10):
        """API 연결 끊기 모달창이 나타날 때까지 대기합니다."""
        try:
            modal_selector = self.get_api_disconnect_modal_selector()
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, modal_selector))
            )
            self.logger.info("API 연결 끊기 모달창 확인")
            return True
        except TimeoutException:
            self.logger.error("API 연결 끊기 모달창 대기 시간 초과")
            return False
        except Exception as e:
            self.logger.error(f"API 연결 끊기 모달창 대기 중 오류 발생: {e}")
            return False
    
    def click_api_disconnect_modal_confirm(self):
        """API 연결 끊기 모달창에서 확인 버튼을 클릭합니다."""
        try:
            selector = self.get_api_disconnect_modal_confirm_button_selector()
            element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            element.click()
            self.logger.info("API 연결 끊기 모달창 확인 버튼 클릭 완료")
            time.sleep(1)
            return True
        except TimeoutException:
            self.logger.error("API 연결 끊기 모달창 확인 버튼을 찾을 수 없음")
            return False
        except Exception as e:
            self.logger.error(f"API 연결 끊기 모달창 확인 버튼 클릭 중 오류 발생: {e}")
            return False
    
    def click_api_disconnect_modal_cancel(self):
        """API 연결 끊기 모달창에서 취소 버튼을 클릭합니다."""
        try:
            selector = self.get_api_disconnect_modal_cancel_button_selector()
            element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            element.click()
            self.logger.info("API 연결 끊기 모달창 취소 버튼 클릭 완료")
            time.sleep(1)
            return True
        except TimeoutException:
            self.logger.error("API 연결 끊기 모달창 취소 버튼을 찾을 수 없음")
            return False
        except Exception as e:
            self.logger.error(f"API 연결 끊기 모달창 취소 버튼 클릭 중 오류 발생: {e}")
            return False
    
    def close_api_disconnect_modal(self):
        """API 연결 끊기 모달창을 닫습니다 (X 버튼 클릭)."""
        try:
            selector = self.get_api_disconnect_modal_close_button_selector()
            element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            element.click()
            self.logger.info("API 연결 끊기 모달창 닫기 버튼 클릭 완료")
            time.sleep(1)
            return True
        except TimeoutException:
            self.logger.error("API 연결 끊기 모달창 닫기 버튼을 찾을 수 없음")
            return False
        except Exception as e:
            self.logger.error(f"API 연결 끊기 모달창 닫기 버튼 클릭 중 오류 발생: {e}")
            return False
    
    def get_api_disconnect_modal_alert_messages(self):
        """API 연결 끊기 모달창의 알림 메시지들을 반환합니다."""
        try:
            messages = {}
            
            # 에러 알림 메시지
            try:
                error_element = self.driver.find_element(By.CSS_SELECTOR, self.get_api_disconnect_modal_error_alert_selector())
                messages['error'] = error_element.text.strip()
            except NoSuchElementException:
                messages['error'] = None
            
            # 경고 알림 메시지
            try:
                warning_element = self.driver.find_element(By.CSS_SELECTOR, self.get_api_disconnect_modal_warning_alert_selector())
                messages['warning'] = warning_element.text.strip()
            except NoSuchElementException:
                messages['warning'] = None
            
            return messages
        except Exception as e:
            self.logger.error(f"API 연결 끊기 모달창 알림 메시지 조회 중 오류 발생: {e}")
            return {'error': None, 'warning': None}
    
    def handle_api_disconnect_modal(self, confirm=True):
        """API 연결 끊기 모달창을 처리합니다.
        
        Args:
            confirm (bool): True면 확인, False면 취소
        """
        try:
            # 1. 모달창 대기
            if not self.wait_for_api_disconnect_modal():
                return False
            
            # 2. 알림 메시지 확인 (로깅용)
            messages = self.get_api_disconnect_modal_alert_messages()
            if messages['error']:
                self.logger.info(f"에러 알림: {messages['error']}")
            if messages['warning']:
                self.logger.info(f"경고 알림: {messages['warning']}")
            
            # 3. 사용자 선택에 따라 버튼 클릭
            if confirm:
                return self.click_api_disconnect_modal_confirm()
            else:
                return self.click_api_disconnect_modal_cancel()
                
        except Exception as e:
            self.logger.error(f"API 연결 끊기 모달창 처리 중 오류 발생: {e}")
            return False
    
    def perform_complete_api_disconnect_workflow(self, market_key, confirm=True):
        """API 연결 끊기 전체 워크플로우를 수행합니다.
        
        Args:
            market_key (str): 마켓 키
            confirm (bool): True면 확인, False면 취소
        """
        try:
            # 1. 마켓 탭으로 전환
            if not self.switch_to_market(market_key):
                return False
            
            # 2. 패널 로드 대기
            if not self.wait_for_market_panel_load(market_key):
                return False
            
            # 3. API 연결 끊기 버튼 클릭
            if not self.click_api_disconnect_button():
                return False
            
            # 4. 모달창 처리
            return self.handle_api_disconnect_modal(confirm)
            
        except Exception as e:
             self.logger.error(f"API 연결 끊기 전체 워크플로우 중 오류 발생: {e}")
             return False
    
    # ==================== 11번가 API 검증 모달창 관련 메서드 ====================
    
    def get_11st_api_verification_modal_selector(self):
        """11번가 API 검증 모달창(드로어) 선택자를 반환합니다."""
        return '.ant-drawer-content .ant-drawer-title:contains("11번가 배송 프로필 추가")'
    
    def get_11st_shipping_profile_create_button_selector(self):
        """11번가 배송프로필 만들기 버튼 선택자를 반환합니다."""
        return '.ant-drawer-extra .ant-btn-primary span:contains("배송프로필 만들기")'
    
    def get_11st_delivery_company_dropdown_selector(self):
        """11번가 출고 택배사 드롭다운 선택자를 반환합니다."""
        return '.ant-drawer-body .ant-select:has(.ant-select-selection-item[title*="택배"])'
    
    def get_11st_delivery_company_dropdown_arrow_selector(self):
        """11번가 출고 택배사 드롭다운 화살표 선택자를 반환합니다."""
        return '.ant-drawer-body .ant-select:has(.ant-select-selection-item[title*="택배"]) .ant-select-arrow'
    
    def get_11st_lotte_delivery_option_selector(self):
        """11번가 롯데(현대)택배 옵션 선택자를 반환합니다."""
        return '.ant-select-dropdown .ant-select-item-option[title="롯데(현대)택배"]'
    
    def wait_for_11st_api_verification_modal(self, timeout=10):
        """11번가 API 검증 모달창이 나타날 때까지 대기합니다."""
        try:
            modal_selector = self.get_11st_api_verification_modal_selector()
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, modal_selector))
            )
            self.logger.info("11번가 API 검증 모달창 확인")
            return True
        except TimeoutException:
            self.logger.error("11번가 API 검증 모달창 대기 시간 초과")
            return False
        except Exception as e:
            self.logger.error(f"11번가 API 검증 모달창 대기 중 오류 발생: {e}")
            return False
    
    def select_11st_lotte_delivery_company(self):
        """11번가 출고 택배사에서 롯데(현대)택배를 선택합니다."""
        try:
            # 1. 드롭다운 클릭하여 열기
            dropdown_selector = self.get_11st_delivery_company_dropdown_selector()
            dropdown_element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, dropdown_selector)))
            dropdown_element.click()
            self.logger.info("출고 택배사 드롭다운 클릭")
            time.sleep(1)
            
            # 2. 롯데(현대)택배 옵션 선택
            lotte_option_selector = self.get_11st_lotte_delivery_option_selector()
            lotte_option = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, lotte_option_selector)))
            lotte_option.click()
            self.logger.info("롯데(현대)택배 선택 완료")
            time.sleep(1)
            return True
            
        except TimeoutException:
            self.logger.error("롯데(현대)택배 선택 중 요소를 찾을 수 없음")
            return False
        except Exception as e:
            self.logger.error(f"롯데(현대)택배 선택 중 오류 발생: {e}")
            return False
    
    def click_11st_shipping_profile_create_button(self):
        """11번가 배송프로필 만들기 버튼을 클릭합니다."""
        try:
            selector = self.get_11st_shipping_profile_create_button_selector()
            element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            element.click()
            self.logger.info("11번가 배송프로필 만들기 버튼 클릭 완료")
            time.sleep(2)
            return True
        except TimeoutException:
            self.logger.error("11번가 배송프로필 만들기 버튼을 찾을 수 없음")
            return False
        except Exception as e:
            self.logger.error(f"11번가 배송프로필 만들기 버튼 클릭 중 오류 발생: {e}")
            return False
    
    def handle_11st_api_verification_modal(self):
        """11번가 API 검증 모달창을 처리합니다.
        
        1. 출고 택배사에서 롯데(현대)택배 선택
        2. 배송프로필 만들기 버튼 클릭
        """
        try:
            # 1. 모달창 대기
            if not self.wait_for_11st_api_verification_modal():
                return False
            
            # 2. 롯데(현대)택배 선택
            if not self.select_11st_lotte_delivery_company():
                return False
            
            # 3. 배송프로필 만들기 버튼 클릭
            if not self.click_11st_shipping_profile_create_button():
                return False
            
            self.logger.info("11번가 API 검증 모달창 처리 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"11번가 API 검증 모달창 처리 중 오류 발생: {e}")
            return False
    
    def perform_complete_11st_api_verification_workflow(self):
        """11번가 API 검증 전체 워크플로우를 수행합니다.
        
        1. 11번가 탭으로 전환
        2. API 검증 버튼 클릭
        3. API 검증 모달창 처리
        """
        try:
            # 1. 11번가 탭으로 전환
            if not self.switch_to_market('11st'):
                return False
            
            # 2. 패널 로드 대기
            if not self.wait_for_market_panel_load('11st'):
                return False
            
            # 3. API 검증 버튼 클릭
            if not self.click_api_validation_button():
                return False
            
            # 4. API 검증 모달창 처리
            return self.handle_11st_api_verification_modal()
            
        except Exception as e:
             self.logger.error(f"11번가 API 검증 전체 워크플로우 중 오류 발생: {e}")
             return False
    
    # ==================== 옥션/G마켓 API 검증 모달창 관련 메서드 ====================
    
    def get_auction_gmarket_api_verification_modal_selector(self):
        """옥션/G마켓 API 검증 모달창(드로어) 선택자를 반환합니다."""
        return '.ant-drawer-content .ant-drawer-title:contains("옥션/G마켓 배송 프로필 추가")'
    
    def get_auction_gmarket_shipping_profile_create_button_selector(self):
        """옥션/G마켓 배송프로필 만들기 버튼 선택자를 반환합니다."""
        return '.ant-drawer-extra .ant-btn-primary span:contains("배송프로필 만들기")'
    
    def get_auction_gmarket_delivery_company_dropdown_selector(self):
        """옥션/G마켓 택배사 드롭다운 선택자를 반환합니다."""
        return '.ant-drawer-body .ant-select:has(.ant-select-selection-item[title="롯데택배"])'
    
    def get_auction_gmarket_lotte_delivery_option_selector(self):
        """옥션/G마켓 롯데택배 옵션 선택자를 반환합니다."""
        return '.ant-select-dropdown .ant-select-item-option[title="롯데택배"]'
    
    def get_gmarket_site_discount_agree_button_selector(self):
        """G마켓 사이트할인 동의 버튼 선택자를 반환합니다."""
        return '.ant-drawer-body .ant-radio-group:has(.sc-fqgwrq:contains("G마켓 사이트할인 동의")) .ant-radio-button-wrapper:has(span:contains("동의"))'
    
    def get_auction_site_discount_agree_button_selector(self):
        """옥션 사이트할인 동의 버튼 선택자를 반환합니다."""
        return '.ant-drawer-body .ant-radio-group:has(.sc-fqgwrq:contains("옥션 사이트할인 동의")) .ant-radio-button-wrapper:has(span:contains("동의"))'
    
    def wait_for_auction_gmarket_api_verification_modal(self, timeout=10):
        """옥션/G마켓 API 검증 모달창이 나타날 때까지 대기합니다."""
        try:
            modal_selector = self.get_auction_gmarket_api_verification_modal_selector()
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, modal_selector))
            )
            self.logger.info("옥션/G마켓 API 검증 모달창 확인")
            return True
        except TimeoutException:
            self.logger.error("옥션/G마켓 API 검증 모달창 대기 시간 초과")
            return False
        except Exception as e:
            self.logger.error(f"옥션/G마켓 API 검증 모달창 대기 중 오류 발생: {e}")
            return False
    
    def select_auction_gmarket_lotte_delivery_company(self):
        """옥션/G마켓 택배사에서 롯데택배를 선택합니다."""
        try:
            # 1. 드롭다운 클릭하여 열기
            dropdown_selector = self.get_auction_gmarket_delivery_company_dropdown_selector()
            dropdown_element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, dropdown_selector)))
            dropdown_element.click()
            self.logger.info("택배사 드롭다운 클릭")
            time.sleep(1)
            
            # 2. 롯데택배 옵션 선택
            lotte_option_selector = self.get_auction_gmarket_lotte_delivery_option_selector()
            lotte_option = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, lotte_option_selector)))
            lotte_option.click()
            self.logger.info("롯데택배 선택 완료")
            time.sleep(1)
            return True
            
        except TimeoutException:
            self.logger.error("롯데택배 선택 중 요소를 찾을 수 없음")
            return False
        except Exception as e:
            self.logger.error(f"롯데택배 선택 중 오류 발생: {e}")
            return False
    
    def click_gmarket_site_discount_agree(self):
        """G마켓 사이트할인 동의 버튼을 클릭합니다."""
        try:
            selector = self.get_gmarket_site_discount_agree_button_selector()
            element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            element.click()
            self.logger.info("G마켓 사이트할인 동의 버튼 클릭 완료")
            time.sleep(1)
            return True
        except TimeoutException:
            self.logger.error("G마켓 사이트할인 동의 버튼을 찾을 수 없음")
            return False
        except Exception as e:
            self.logger.error(f"G마켓 사이트할인 동의 버튼 클릭 중 오류 발생: {e}")
            return False
    
    def click_auction_site_discount_agree(self):
        """옥션 사이트할인 동의 버튼을 클릭합니다."""
        try:
            selector = self.get_auction_site_discount_agree_button_selector()
            element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            element.click()
            self.logger.info("옥션 사이트할인 동의 버튼 클릭 완료")
            time.sleep(1)
            return True
        except TimeoutException:
            self.logger.error("옥션 사이트할인 동의 버튼을 찾을 수 없음")
            return False
        except Exception as e:
            self.logger.error(f"옥션 사이트할인 동의 버튼 클릭 중 오류 발생: {e}")
            return False
    
    def click_auction_gmarket_shipping_profile_create_button(self):
        """옥션/G마켓 배송프로필 만들기 버튼을 클릭합니다."""
        try:
            selector = self.get_auction_gmarket_shipping_profile_create_button_selector()
            element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            element.click()
            self.logger.info("옥션/G마켓 배송프로필 만들기 버튼 클릭 완료")
            time.sleep(2)
            return True
        except TimeoutException:
            self.logger.error("옥션/G마켓 배송프로필 만들기 버튼을 찾을 수 없음")
            return False
        except Exception as e:
            self.logger.error(f"옥션/G마켓 배송프로필 만들기 버튼 클릭 중 오류 발생: {e}")
            return False
    
    def handle_auction_gmarket_api_verification_modal(self):
        """옥션/G마켓 API 검증 모달창을 처리합니다.
        
        1. 택배사에서 롯데택배 선택
        2. G마켓 사이트할인 동의
        3. 옥션 사이트할인 동의
        4. 배송프로필 만들기 버튼 클릭
        """
        try:
            # 1. 모달창 대기
            if not self.wait_for_auction_gmarket_api_verification_modal():
                return False
            
            # 2. 롯데택배 선택
            if not self.select_auction_gmarket_lotte_delivery_company():
                return False
            
            # 3. G마켓 사이트할인 동의
            if not self.click_gmarket_site_discount_agree():
                return False
            
            # 4. 옥션 사이트할인 동의
            if not self.click_auction_site_discount_agree():
                return False
            
            # 5. 배송프로필 만들기 버튼 클릭
            if not self.click_auction_gmarket_shipping_profile_create_button():
                return False
            
            self.logger.info("옥션/G마켓 API 검증 모달창 처리 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"옥션/G마켓 API 검증 모달창 처리 중 오류 발생: {e}")
            return False
    
    def perform_complete_auction_gmarket_api_verification_workflow(self, market_key):
        """옥션/G마켓 API 검증 전체 워크플로우를 수행합니다.
        
        Args:
            market_key (str): 'auction' 또는 'gmarket'
        """
        try:
            # 1. 해당 마켓 탭으로 전환
            if not self.switch_to_market(market_key):
                return False
            
            # 2. 패널 로드 대기
            if not self.wait_for_market_panel_load(market_key):
                return False
            
            # 3. API 검증 버튼 클릭
            if not self.click_api_validation_button():
                return False
            
            # 4. API 검증 모달창 처리
            return self.handle_auction_gmarket_api_verification_modal()
            
        except Exception as e:
            self.logger.error(f"옥션/G마켓 API 검증 전체 워크플로우 중 오류 발생: {e}")
            return False