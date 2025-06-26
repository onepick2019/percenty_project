# -*- coding: utf-8 -*-
"""
카페24 마켓 관리자

카페24 로그인 및 11번가 상품 가져오기 기능을 제공합니다.
"""

import logging
import time
import pyautogui
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)

class MarketManagerCafe24:
    """
    카페24 마켓 관리 클래스
    """
    
    def __init__(self, driver):
        """
        초기화
        
        Args:
            driver: Selenium WebDriver 인스턴스
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
    
    def login_and_import_11st_products(self, cafe24_id, cafe24_password, store_id_11st):
        """
        카페24에 로그인하고 11번가 상품을 가져옵니다.
        
        Args:
            cafe24_id (str): 카페24 아이디 (R열)
            cafe24_password (str): 카페24 비밀번호 (S열)
            store_id_11st (str): 11번가 스토어 ID (T열)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("카페24 로그인 및 11번가 상품 가져오기 시작")
            
            # 1. 새 탭에서 카페24 로그인 페이지 열기
            if not self._open_cafe24_login_page():
                return False
            
            # 2. 로그인 수행
            if not self._perform_login(cafe24_id, cafe24_password):
                return False
            
            # 3. 로그인 후 처리 (비밀번호 변경 화면 등)
            if not self._handle_post_login():
                return False
            
            # 4. 마켓상품가져오기 페이지로 이동
            if not self._navigate_to_import_page():
                return False
            
            # 5. 전체 가져오기 탭 선택
            if not self._select_full_import_tab():
                return False
            
            # 6. 11번가 스토어 ID로 체크박스 선택
            if not self._select_11st_store(store_id_11st):
                return False
            
            # 7. 직접 등록 체크박스 선택 및 가져오기 실행
            if not self._execute_import():
                return False
            
            # 8. 모달창 확인 클릭
            if not self._confirm_import_modal():
                return False
            
            # 9. 로그아웃
            if not self._logout():
                logger.warning("로그아웃에 실패했지만 계속 진행합니다")
            
            # 9. 카페24 탭 닫기 (현재 탭만 닫고 메인 탭으로 복귀는 호출하는 쪽에서 처리)
            try:
                self.driver.close()
                logger.info("카페24 탭 닫기 완료")
            except Exception as e:
                logger.warning(f"카페24 탭 닫기 실패: {e}")
            
            logger.info("카페24 11번가 상품 가져오기 완료")
            return True
            
        except Exception as e:
            logger.error(f"카페24 11번가 상품 가져오기 중 오류 발생: {e}")
            return False
    
    def _open_cafe24_login_page(self):
        """
        새 탭에서 카페24 로그인 페이지를 엽니다.
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("카페24 로그인 페이지 열기")
            
            # 새 탭 열기
            self.driver.execute_script("window.open('', '_blank');")
            
            # 새 탭으로 전환
            self.driver.switch_to.window(self.driver.window_handles[-1])
            
            # 카페24 로그인 페이지로 이동
            self.driver.get("https://eclogin.cafe24.com/Shop/?mode=mp")
            
            # 페이지 로드 대기
            time.sleep(3)
            
            logger.info("카페24 로그인 페이지 열기 완료")
            return True
            
        except Exception as e:
            logger.error(f"카페24 로그인 페이지 열기 실패: {e}")
            return False
    
    def _perform_login(self, cafe24_id, cafe24_password):
        """
        카페24 로그인을 수행합니다.
        
        Args:
            cafe24_id (str): 카페24 아이디
            cafe24_password (str): 카페24 비밀번호
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"카페24 로그인 시도: {cafe24_id}")
            
            # 아이디 입력
            id_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "mall_id"))
            )
            id_input.clear()
            id_input.send_keys(cafe24_id)
            
            # 비밀번호 입력
            password_input = self.driver.find_element(By.ID, "userpasswd")
            password_input.clear()
            password_input.send_keys(cafe24_password)
            
            # 로그인 버튼 클릭
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button.btnStrong.large")
            login_button.click()
            
            # 로그인 처리 대기
            time.sleep(3)
            
            logger.info("카페24 로그인 완료")
            return True
            
        except Exception as e:
            logger.error(f"카페24 로그인 실패: {e}")
            return False
    
    def _handle_post_login(self):
        """
        로그인 후 처리를 수행합니다 (비밀번호 변경 화면 등).
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("로그인 후 처리 확인")
            
            # 비밀번호 변경 화면 확인
            try:
                next_time_button = self.driver.find_element(By.ID, "iptBtnEm")
                if next_time_button.is_displayed():
                    logger.info("비밀번호 변경 화면 감지 - '다음에 변경하기' 클릭")
                    next_time_button.click()
                    time.sleep(2)
            except NoSuchElementException:
                logger.info("비밀번호 변경 화면 없음")
            
            # 로그인 성공 확인 (메인 페이지 URL 확인)
            current_url = self.driver.current_url
            if "mp.cafe24.com/mp/main/front/service" in current_url:
                logger.info("카페24 메인 페이지 로그인 확인 완료")
                return True
            else:
                # URL이 다른 경우 잠시 대기 후 재확인
                time.sleep(3)
                current_url = self.driver.current_url
                if "mp.cafe24.com" in current_url:
                    logger.info("카페24 로그인 확인 완료")
                    return True
                else:
                    logger.error(f"로그인 실패 - 현재 URL: {current_url}")
                    return False
            
        except Exception as e:
            logger.error(f"로그인 후 처리 실패: {e}")
            return False
    
    def _navigate_to_import_page(self):
        """
        마켓상품가져오기 페이지로 이동합니다.
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("마켓상품가져오기 페이지로 이동")
            
            # 마켓상품가져오기 페이지로 이동
            self.driver.get("https://mp.cafe24.com/mp/product/front/import")
            
            # 페이지 로드 대기
            time.sleep(3)
            
            logger.info("마켓상품가져오기 페이지 이동 완료")
            return True
            
        except Exception as e:
            logger.error(f"마켓상품가져오기 페이지 이동 실패: {e}")
            return False
    
    def _select_full_import_tab(self):
        """
        '전체 가져오기' 탭을 선택합니다.
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("'전체 가져오기' 탭 선택")
            
            # 전체 가져오기 탭 클릭
            full_import_tab = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "li[data-tab='PA'] a"))
            )
            full_import_tab.click()
            
            # 탭 전환 대기
            time.sleep(2)
            
            logger.info("'전체 가져오기' 탭 선택 완료")
            return True
            
        except Exception as e:
            logger.error(f"'전체 가져오기' 탭 선택 실패: {e}")
            return False
    
    def _select_11st_store(self, store_id_11st):
        """
        11번가 스토어 ID에 해당하는 체크박스를 선택합니다.
        
        Args:
            store_id_11st (str): 11번가 스토어 ID
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"11번가 스토어 선택: {store_id_11st}")
            
            # 11번가 스토어 ID가 포함된 span 요소 찾기 (체크박스 대신 span 클릭)
            store_spans = self.driver.find_elements(
                By.CSS_SELECTOR, 
                "span.shop-label"
            )
            
            for span in store_spans:
                span_text = span.text
                
                if store_id_11st in span_text and "11번가" in span_text:
                    logger.info(f"11번가 스토어 찾음: {span_text}")
                    
                    # span 요소 클릭 (체크박스가 자동으로 선택됨)
                    try:
                        span.click()
                        time.sleep(1)
                        logger.info("11번가 스토어 span 클릭으로 선택 완료")
                        return True
                    except Exception as click_error:
                        logger.warning(f"span 클릭 실패, JavaScript 클릭 시도: {click_error}")
                        # JavaScript 클릭 시도
                        try:
                            self.driver.execute_script("arguments[0].click();", span)
                            time.sleep(1)
                            logger.info("11번가 스토어 JavaScript 클릭으로 선택 완료")
                            return True
                        except Exception as js_error:
                            logger.error(f"JavaScript 클릭도 실패: {js_error}")
                            continue
            
            logger.error(f"11번가 스토어 ID '{store_id_11st}'를 찾을 수 없습니다")
            return False
            
        except Exception as e:
            logger.error(f"11번가 스토어 선택 실패: {e}")
            return False
    
    def _execute_import(self):
        """
        직접 등록 체크박스를 선택하고 가져오기를 실행합니다.
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("직접 등록 체크박스 선택 및 가져오기 실행")
            
            # 직접 등록 체크박스 선택 (span 요소 클릭 방식)
            try:
                # 먼저 체크박스 상태 확인
                direct_register_checkbox = self.driver.find_element(By.ID, "is_direct_register")
                if not direct_register_checkbox.is_selected():
                    # span 요소를 클릭하여 체크박스 선택
                    span_element = self.driver.find_element(
                        By.XPATH, 
                        "//span[contains(text(), '마켓상품 가져오기 후 새로운 상품으로 바로 등록합니다.')]"
                    )
                    span_element.click()
                    time.sleep(1)
                    logger.info("직접 등록 체크박스 span 클릭으로 선택 완료")
                else:
                    logger.info("직접 등록 체크박스가 이미 선택되어 있음")
            except Exception as checkbox_error:
                logger.warning(f"span 클릭 방식 실패, 체크박스 직접 클릭 시도: {checkbox_error}")
                # 백업: 체크박스 직접 클릭
                direct_register_checkbox = self.driver.find_element(By.ID, "is_direct_register")
                if not direct_register_checkbox.is_selected():
                    direct_register_checkbox.click()
                    time.sleep(1)
            
            # 가져오기 버튼 클릭
            import_button = self.driver.find_element(
                By.CSS_SELECTOR, 
                "button.btn.btn-lg.btn-point.btnSubmit"
            )
            import_button.click()
            
            # 가져오기 처리 대기
            time.sleep(2)
            
            logger.info("가져오기 실행 완료")
            return True
            
        except Exception as e:
            logger.error(f"가져오기 실행 실패: {e}")
            return False
    
    def _confirm_import_modal(self):
        """
        가져오기 모달창에서 확인을 클릭합니다.
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("가져오기 모달창 확인 클릭")
            
            # 모달창 대기
            time.sleep(2)
            
            # pyautogui를 사용하여 확인 버튼 클릭 (좌표 기반)
            pyautogui.click(1060, 205)
            
            # 모달창 처리 대기
            time.sleep(3)
            
            logger.info("가져오기 모달창 확인 완료")
            return True
            
        except Exception as e:
            logger.error(f"가져오기 모달창 확인 실패: {e}")
            return False
    
    def _logout(self):
        """
        카페24에서 로그아웃합니다.
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("카페24 로그아웃")
            
            # 내정보 버튼 클릭
            my_info_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.mkbtn-image.mkbtn-func-member"))
            )
            my_info_button.click()
            
            # 드롭다운 메뉴가 나타날 때까지 대기
            time.sleep(1)
            
            # 로그아웃 버튼 클릭
            logout_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-logout.btnHeaderSubMenu[data-link_type='logout']"))
            )
            logout_button.click()
            
            # 로그아웃 처리 대기
            time.sleep(2)
            
            logger.info("카페24 로그아웃 완료")
            return True
            
        except Exception as e:
            logger.error(f"카페24 로그아웃 실패: {e}")
            return False