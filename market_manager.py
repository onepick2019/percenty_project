import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)

class MarketManager:
    """
    마켓별 특수 작업을 처리하는 매니저 클래스
    스마트스토어, 쿠팡 등의 마켓에서 로그인 후 처리해야 할 작업들을 담당
    """
    
    def __init__(self, driver, wait=None):
        """
        MarketManager 초기화
        
        Args:
            driver: Selenium WebDriver 인스턴스
            wait: WebDriverWait 인스턴스 (선택사항)
        """
        self.driver = driver
        self.wait = wait if wait else WebDriverWait(driver, 10)
    
    def update_smartstore_delivery_info(self):
        """
        스마트스토어 배송정보 변경 작업을 수행합니다.
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("스마트스토어 배송정보 변경 시작")
            
            # 1. 새탭에서 스마트스토어 상품 목록 페이지 열기
            if not self._open_smartstore_product_list():
                logger.error("스마트스토어 상품 목록 페이지 열기 실패")
                return False
            
            # 2. 전체선택 체크박스 선택
            if not self._select_all_products():
                logger.error("전체선택 체크박스 선택 실패")
                return False
            
            # 3. 배송변경 드롭박스에서 배송정보 선택
            if not self._select_delivery_change_option():
                logger.error("배송변경 옵션 선택 실패")
                return False
            
            # 4. 배송비 템플릿 버튼 클릭
            if not self._click_delivery_template_button():
                logger.error("배송비 템플릿 버튼 클릭 실패")
                return False
            
            # 5. 배송비 템플릿 모달에서 '선택' 클릭
            if not self._select_delivery_template():
                logger.error("배송비 템플릿 선택 실패")
                return False
            
            # 6. '주문확인 후 제작' 체크박스 선택
            if not self._select_custom_product_checkbox():
                logger.error("주문확인 후 제작 체크박스 선택 실패")
                return False
            
            # 7. 발송예정일 7일 선택
            if not self._select_delivery_period():
                logger.error("발송예정일 선택 실패")
                return False
            
            # 8. 변경 버튼 클릭
            if not self._click_change_button():
                logger.error("변경 버튼 클릭 실패")
                return False
            
            # 9. 변경 완료 대기 및 모달창 닫기
            if not self._wait_for_change_completion():
                logger.error("변경 완료 대기 실패")
                return False
            
            # 10. 모달창 닫기
            if not self._close_delivery_modal():
                logger.error("모달창 닫기 실패")
                return False
            
            # 11. 스마트스토어 로그아웃
            if not self._logout_smartstore():
                logger.error("스마트스토어 로그아웃 실패")
                return False
            
            # 12. 새탭 닫기
            if not self._close_smartstore_tab():
                logger.error("스마트스토어 탭 닫기 실패")
                return False
            
            logger.info("스마트스토어 배송정보 변경 완료")
            return True
            
        except Exception as e:
            logger.error(f"스마트스토어 배송정보 변경 중 오류 발생: {e}")
            # 오류 발생 시 새탭 닫기 시도
            try:
                self._close_smartstore_tab()
            except:
                pass
            return False
    
    def _open_smartstore_product_list(self):
        """
        새탭에서 스마트스토어 상품 목록 페이지를 엽니다.
        
        Returns:
            bool: 성공 여부
        """
        try:
            # 현재 탭 저장
            self.original_window = self.driver.current_window_handle
            
            # 새탭에서 스마트스토어 상품 목록 페이지 열기
            self.driver.execute_script("window.open('https://sell.smartstore.naver.com/#/products/origin-list', '_blank');")
            
            # 새 탭으로 전환
            all_windows = self.driver.window_handles
            self.smartstore_window = [window for window in all_windows if window != self.original_window][0]
            self.driver.switch_to.window(self.smartstore_window)
            
            logger.info("스마트스토어 상품 목록 페이지 새탭 열기 완료")
            time.sleep(5)  # 페이지 로드 대기
            
            return True
            
        except Exception as e:
            logger.error(f"스마트스토어 상품 목록 페이지 열기 실패: {e}")
            return False
    
    def _select_all_products(self):
        """
        전체선택 체크박스를 선택합니다.
        
        Returns:
            bool: 성공 여부
        """
        try:
            # 페이지 다운으로 화면을 아래로 이동하여 전체선택 체크박스가 보이도록 함
            self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
            time.sleep(1)  # 스크롤 완료 대기
            
            # 전체선택 체크박스 선택자
            select_all_selector = 'input.ag-selection-checkbox[data-nclicks-code="itg.allcheck"]'
            
            select_all_checkbox = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, select_all_selector))
            )
            
            # 체크박스가 이미 선택되어 있지 않은 경우에만 클릭
            if not select_all_checkbox.is_selected():
                # JavaScript를 사용하여 클릭 (element click intercepted 오류 방지)
                self.driver.execute_script("arguments[0].click();", select_all_checkbox)
                logger.info("전체선택 체크박스 선택 완료")
            else:
                logger.info("전체선택 체크박스가 이미 선택되어 있음")
            
            time.sleep(2)  # 선택 완료 대기
            return True
            
        except Exception as e:
            logger.error(f"전체선택 체크박스 선택 실패: {e}")
            return False
    
    def _select_delivery_change_option(self):
        """
        배송변경 드롭박스에서 배송정보를 선택합니다.
        
        Returns:
            bool: 성공 여부
        """
        try:
            # 배송변경 드롭박스 클릭
            dropdown_selector = '.selectize-input.items.full.has-options.has-items'
            dropdown = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, dropdown_selector))
            )
            self.driver.execute_script("arguments[0].click();", dropdown)
            logger.info("배송변경 드롭박스 클릭 완료")
            
            time.sleep(1)
            
            # 배송정보 옵션 선택
            delivery_option_selector = '.option[data-value="DELIVERY"]'
            delivery_option = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, delivery_option_selector))
            )
            self.driver.execute_script("arguments[0].click();", delivery_option)
            logger.info("배송정보 옵션 선택 완료")
            
            time.sleep(2)
            return True
            
        except Exception as e:
            logger.error(f"배송변경 옵션 선택 실패: {e}")
            return False
    
    def _click_delivery_template_button(self):
        """
        배송비 템플릿 버튼을 클릭합니다.
        
        Returns:
            bool: 성공 여부
        """
        try:
            template_button_selector = 'button.btn.btn-single.btn-block'
            template_button = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, template_button_selector))
            )
            
            # 버튼 텍스트 확인
            if "배송비 템플릿" in template_button.text:
                self.driver.execute_script("arguments[0].click();", template_button)
                logger.info("배송비 템플릿 버튼 클릭 완료")
                time.sleep(3)  # 모달 로드 대기
                return True
            else:
                logger.error("배송비 템플릿 버튼을 찾을 수 없음")
                return False
            
        except Exception as e:
            logger.error(f"배송비 템플릿 버튼 클릭 실패: {e}")
            return False
    
    def _select_delivery_template(self):
        """
        배송비 템플릿 모달에서 '선택' 버튼을 클릭합니다.
        
        Returns:
            bool: 성공 여부
        """
        try:
            # 템플릿 선택 버튼 클릭
            select_button_selector = 'button.btn.btn-primary'
            select_buttons = self.driver.find_elements(By.CSS_SELECTOR, select_button_selector)
            
            # '선택' 텍스트가 있는 버튼 찾기
            for button in select_buttons:
                if "선택" in button.text:
                    self.driver.execute_script("arguments[0].click();", button)
                    logger.info("배송비 템플릿 선택 완료")
                    time.sleep(2)
                    return True
            
            logger.error("배송비 템플릿 선택 버튼을 찾을 수 없음")
            return False
            
        except Exception as e:
            logger.error(f"배송비 템플릿 선택 실패: {e}")
            return False
    
    def _select_custom_product_checkbox(self):
        """
        '주문확인 후 제작' 체크박스를 선택합니다.
        
        Returns:
            bool: 성공 여부
        """
        try:
            # 주문확인 후 제작 체크박스 선택자 (세번째 체크박스)
            custom_product_selector = 'input[ng-model="vm.modelData.customProductAfterOrderYn"][data-nclicks-code="atb.order"]'
            
            custom_checkbox = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, custom_product_selector))
            )
            
            # 체크박스가 선택되어 있지 않은 경우에만 클릭
            if not custom_checkbox.is_selected():
                # JavaScript를 사용하여 클릭 (element click intercepted 오류 방지)
                self.driver.execute_script("arguments[0].click();", custom_checkbox)
                logger.info("주문확인 후 제작 체크박스 선택 완료")
            else:
                logger.info("주문확인 후 제작 체크박스가 이미 선택되어 있음")
            
            time.sleep(2)
            return True
            
        except Exception as e:
            logger.error(f"주문확인 후 제작 체크박스 선택 실패: {e}")
            return False
    
    def _select_delivery_period(self):
        """
        발송예정일을 7일로 선택합니다.
        
        Returns:
            bool: 성공 여부
        """
        try:
            # 발송예정일 드롭박스 클릭
            period_dropdown_selector = '.selectize-input.items.not-full input[placeholder="일자를 선택해 주세요."]'
            period_dropdown = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, period_dropdown_selector))
            )
            self.driver.execute_script("arguments[0].click();", period_dropdown)
            logger.info("발송예정일 드롭박스 클릭 완료")
            
            time.sleep(1)
            
            # 7일 옵션 선택
            seven_days_selector = '.option[data-value="SEVEN"]'
            seven_days_option = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, seven_days_selector))
            )
            self.driver.execute_script("arguments[0].click();", seven_days_option)
            logger.info("발송예정일 7일 선택 완료")
            
            time.sleep(2)
            return True
            
        except Exception as e:
            logger.error(f"발송예정일 선택 실패: {e}")
            return False
    
    def _click_change_button(self):
        """
        모달창에서 '변경' 버튼을 클릭합니다.
        
        Returns:
            bool: 성공 여부
        """
        try:
            # 모달창 하단으로 스크롤
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            
            # 변경 버튼 클릭
            change_button_selector = 'button.btn.btn-primary.progress-button .content'
            change_buttons = self.driver.find_elements(By.CSS_SELECTOR, change_button_selector)
            
            for button in change_buttons:
                if "변경" in button.text:
                    # 부모 버튼 요소 클릭
                    parent_button = button.find_element(By.XPATH, '..')
                    self.driver.execute_script("arguments[0].click();", parent_button)
                    logger.info("변경 버튼 클릭 완료")
                    time.sleep(3)
                    return True
            
            logger.error("변경 버튼을 찾을 수 없음")
            return False
            
        except Exception as e:
            logger.error(f"변경 버튼 클릭 실패: {e}")
            return False
    
    def _wait_for_change_completion(self):
        """
        변경 작업 완료를 대기합니다.
        
        Returns:
            bool: 성공 여부
        """
        try:
            # 변경 완료 메시지 대기 (최대 60초)
            completion_message_selector = 'p.sub-text.pull-left'
            
            for i in range(60):  # 60초 대기
                try:
                    completion_elements = self.driver.find_elements(By.CSS_SELECTOR, completion_message_selector)
                    for element in completion_elements:
                        if "개 상품의 상품정보가 변경되었습니다" in element.text:
                            logger.info(f"변경 완료 확인: {element.text}")
                            time.sleep(2)
                            return True
                except:
                    pass
                
                time.sleep(1)
            
            logger.warning("변경 완료 메시지를 찾을 수 없지만 계속 진행")
            return True
            
        except Exception as e:
            logger.error(f"변경 완료 대기 실패: {e}")
            return False
    
    def _close_delivery_modal(self):
        """
        배송정보 변경 모달창을 닫습니다.
        
        Returns:
            bool: 성공 여부
        """
        try:
            # X 버튼으로 모달 닫기 시도
            close_x_selector = 'button.close span[aria-hidden="true"]'
            try:
                close_x_button = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, close_x_selector))
                )
                self.driver.execute_script("arguments[0].click();", close_x_button)
                logger.info("모달창 X 버튼으로 닫기 완료")
                time.sleep(2)
                return True
            except:
                pass
            
            # 닫기 버튼으로 모달 닫기 시도
            close_button_selector = 'button.btn.btn-default'
            close_buttons = self.driver.find_elements(By.CSS_SELECTOR, close_button_selector)
            
            for button in close_buttons:
                if "닫기" in button.text:
                    self.driver.execute_script("arguments[0].click();", button)
                    logger.info("모달창 닫기 버튼으로 닫기 완료")
                    time.sleep(2)
                    return True
            
            logger.warning("모달창 닫기 버튼을 찾을 수 없지만 계속 진행")
            return True
            
        except Exception as e:
            logger.error(f"모달창 닫기 실패: {e}")
            return False
    
    def _logout_smartstore(self):
        """
        스마트스토어에서 로그아웃합니다.
        
        Returns:
            bool: 성공 여부
        """
        try:
            # 로그아웃 링크 클릭
            logout_selector = 'a[data-action-location-id="logout"]'
            logout_link = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, logout_selector))
            )
            self.driver.execute_script("arguments[0].click();", logout_link)
            logger.info("스마트스토어 로그아웃 완료")
            
            time.sleep(3)  # 로그아웃 처리 대기
            return True
            
        except Exception as e:
            logger.error(f"스마트스토어 로그아웃 실패: {e}")
            return False
    
    def _close_smartstore_tab(self):
        """
        스마트스토어 탭을 닫고 원래 탭으로 돌아갑니다.
        
        Returns:
            bool: 성공 여부
        """
        try:
            # 현재 탭(스마트스토어) 닫기
            self.driver.close()
            
            # 원래 탭으로 돌아가기
            self.driver.switch_to.window(self.original_window)
            logger.info("스마트스토어 탭 닫기 및 원래 탭 복귀 완료")
            
            return True
            
        except Exception as e:
            logger.error(f"스마트스토어 탭 닫기 실패: {e}")
            # 원래 탭으로 돌아가기 시도
            try:
                self.driver.switch_to.window(self.original_window)
            except:
                pass
            return False