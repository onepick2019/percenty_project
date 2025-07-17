# -*- coding: utf-8 -*-
"""
카페24 마켓 관리자

카페24 로그인 및 11번가 상품 가져오기 기능을 제공합니다.
"""

import logging
import time
import pyautogui
from datetime import datetime
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
        self.start_time = None
        self.step_times = {}
    
    def _log_step_time(self, step_name):
        """
        단계별 실행 시간을 기록합니다.
        
        Args:
            step_name (str): 단계 이름
        """
        current_time = datetime.now()
        if self.start_time is None:
            self.start_time = current_time
            
        if hasattr(self, 'last_step_time') and hasattr(self, 'last_step_name'):
            step_duration = (current_time - self.last_step_time).total_seconds()
            self.step_times[self.last_step_name] = step_duration
            logger.info(f"⏱️ {self.last_step_name} 완료 (소요시간: {step_duration:.2f}초)")
        
        logger.info(f"🚀 {step_name} 시작")
        self.last_step_time = current_time
        self.last_step_name = step_name
    
    def _log_total_time(self):
        """
        전체 실행 시간을 기록합니다.
        """
        if self.start_time:
            current_time = datetime.now()
            
            # 마지막 단계 완료 시간 기록
            if hasattr(self, 'last_step_time') and hasattr(self, 'last_step_name'):
                step_duration = (current_time - self.last_step_time).total_seconds()
                self.step_times[self.last_step_name] = step_duration
                logger.info(f"⏱️ {self.last_step_name} 완료 (소요시간: {step_duration:.2f}초)")
            
            total_duration = (current_time - self.start_time).total_seconds()
            logger.info(f"📊 전체 실행 시간: {total_duration:.2f}초")
            
            # 단계별 시간 요약
            if self.step_times:
                logger.info("📈 단계별 실행 시간:")
                for step, duration in self.step_times.items():
                    logger.info(f"  - {step}: {duration:.2f}초")

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
            self._log_step_time("카페24 로그인 및 11번가 상품 가져오기")
            
            # 1. 새 탭에서 카페24 로그인 페이지 열기
            self._log_step_time("로그인 페이지 열기")
            if not self._open_cafe24_login_page():
                return False
            
            # 2. 로그인 수행
            self._log_step_time("로그인 수행")
            if not self._perform_login(cafe24_id, cafe24_password):
                return False
            
            # 3. 로그인 후 처리 (비밀번호 변경 화면 등)
            self._log_step_time("로그인 후 처리")
            if not self._handle_post_login():
                return False
            
            # 4. 마켓상품가져오기 페이지로 이동
            self._log_step_time("마켓상품가져오기 페이지 이동")
            if not self._navigate_to_import_page():
                return False
            
            # 5. 전체 가져오기 탭 선택
            self._log_step_time("전체 가져오기 탭 선택")
            if not self._select_full_import_tab():
                return False
            
            # 6. 11번가 스토어 ID로 체크박스 선택
            self._log_step_time("11번가 스토어 선택")
            if not self._select_11st_store(store_id_11st):
                return False
            
            # 7. 직접 등록 체크박스 선택 및 가져오기 실행
            self._log_step_time("가져오기 실행")
            if not self._execute_import():
                return False
            
            # 8. 모달창 확인 클릭
            self._log_step_time("모달창 처리")
            if not self._confirm_import_modal():
                return False
            
            # 가져오기 완료 후 5초 대기
            logger.info("가져오기 완료 후 5초 대기")
            time.sleep(5)

            # 9. 11번가 연동해제 (500개 이상인 경우에만)
            self._log_step_time("11번가 연동해제")
            if not self._disconnect_11st_products(store_id_11st):
                logger.warning("11번가 연동해제에 실패했지만 계속 진행합니다")
            
            # 10. 로그아웃
            self._log_step_time("로그아웃")
            if not self._logout():
                logger.warning("로그아웃에 실패했지만 계속 진행합니다")
            
            # 11. 카페24 탭 닫기 (현재 탭만 닫고 메인 탭으로 복귀는 호출하는 쪽에서 처리)
            self._log_step_time("탭 정리")
            try:
                self.driver.close()
                logger.info("카페24 탭 닫기 완료")
            except Exception as e:
                logger.warning(f"카페24 탭 닫기 실패: {e}")
            
            # 전체 실행 시간 로그
            self._log_total_time()
            logger.info("카페24 11번가 상품 가져오기 완료")
            return True
            
        except Exception as e:
            logger.error(f"카페24 11번가 상품 가져오기 중 오류 발생: {e}")
            self._log_total_time()
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
        로그인 페이지 상태를 확인하고 필요시 로그아웃을 먼저 수행합니다.
        
        Args:
            cafe24_id (str): 카페24 아이디
            cafe24_password (str): 카페24 비밀번호
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"카페24 로그인 시도: {cafe24_id}")
            
            # 로그인 페이지 상태 확인 및 필요시 로그아웃 수행
            if not self._check_and_prepare_login_page():
                logger.error("로그인 페이지 준비 실패")
                return False
            
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
        11번가 스토어 ID에 해당하는 체크박스를 정확하게 선택합니다.
        괄호 안의 store_id를 정확히 매칭하여 잘못된 선택을 방지합니다.
        
        Args:
            store_id_11st (str): 11번가 스토어 ID
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"11번가 스토어 선택: {store_id_11st}")
            
            # 11번가 스토어 ID가 포함된 span 요소 찾기
            store_spans = self.driver.find_elements(
                By.CSS_SELECTOR, 
                "span.shop-label"
            )
            
            # 정확한 매칭을 위한 후보 목록
            exact_matches = []
            partial_matches = []
            
            for span in store_spans:
                span_text = span.text
                
                # 11번가가 포함된 텍스트만 처리
                if "11번가" in span_text:
                    # 괄호 안의 정확한 store_id 매칭: 11번가(store_id_11st) 형태
                    import re
                    exact_pattern = rf'11번가\({re.escape(store_id_11st)}\)'
                    
                    if re.search(exact_pattern, span_text):
                        exact_matches.append((span, span_text))
                        logger.info(f"정확한 매칭 발견: {span_text}")
                    elif store_id_11st in span_text:
                        partial_matches.append((span, span_text))
                        logger.info(f"부분 매칭 발견: {span_text}")
            
            # 정확한 매칭 우선 선택
            target_matches = exact_matches if exact_matches else partial_matches
            
            if not target_matches:
                logger.error(f"11번가 스토어 ID '{store_id_11st}'를 찾을 수 없습니다")
                return False
            
            # 여러 매칭이 있는 경우 경고 로그
            if len(target_matches) > 1:
                match_texts = [text for _, text in target_matches]
                logger.warning(f"여러 매칭 발견: {match_texts}")
                logger.info(f"첫 번째 매칭 선택: {target_matches[0][1]}")
            
            # 선택 실행
            span, span_text = target_matches[0]
            logger.info(f"11번가 스토어 선택 시도: {span_text}")
            
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
        카페24의 11번가 상품 가져오기는 JavaScript Alert를 사용합니다.
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("가져오기 모달창 확인 클릭 시작")
            
            # 모달창 대기
            time.sleep(2)
            
            # JavaScript Alert 처리 (카페24 11번가 상품 가져오기의 실제 구현 방식)
            logger.info("JavaScript Alert 처리 시도")
            
            # Alert 처리 재시도 로직 (최대 3회)
            for attempt in range(3):
                try:
                    alert = self.driver.switch_to.alert
                    alert_text = alert.text
                    logger.info(f"Alert 발견 (시도 {attempt + 1}/3): {alert_text}")
                    alert.accept()
                    time.sleep(2)
                    
                    logger.info("✓ JavaScript Alert 수락 성공")
                    return True
                    
                except Exception as e:
                    if attempt < 2:  # 마지막 시도가 아닌 경우
                        logger.warning(f"JavaScript Alert 처리 실패 (시도 {attempt + 1}/3): {e} - 재시도 중...")
                        time.sleep(1)
                        continue
                    else:
                        logger.warning(f"JavaScript Alert 처리 최종 실패: {e}")
                        break
            
            # Alert가 없는 경우를 위한 폴백: 좌표 기반 클릭
            logger.info("Alert가 없어 좌표 기반 클릭으로 폴백")
            try:
                # 화면 해상도 확인 로그
                screen_size = pyautogui.size()
                logger.info(f"현재 화면 해상도: {screen_size}")
                
                pyautogui.click(1060, 205)
                time.sleep(2)
                logger.info("✓ 좌표 기반 클릭 완료")
                return True
                
            except Exception as click_error:
                logger.error(f"좌표 기반 클릭도 실패: {click_error}")
                
                # 최후의 수단: 키보드 Enter 시도
                logger.info("최후의 수단으로 Enter 키 시도")
                try:
                    pyautogui.press('enter')
                    time.sleep(2)
                    logger.info("✓ Enter 키 처리 완료")
                    return True
                except Exception as key_error:
                    logger.error(f"Enter 키 처리도 실패: {key_error}")
                    return False
            
        except Exception as e:
                logger.error(f"가져오기 모달창 확인 실패: {e}")
                return False
    
    def _disconnect_11st_products(self, store_id_11st):
        """
        11번가 연동 상품을 해제합니다.
        
        Args:
            store_id_11st (str): 11번가 스토어 ID
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"11번가 연동해제 시작 - 스토어 ID: {store_id_11st}")
            
            # 1. 연동해제 페이지로 이동
            if not self._navigate_to_disconnect_page(store_id_11st):
                return False
            
            # 2. 총 상품수 확인
            total_products = self._get_total_product_count()
            if total_products is None:
                logger.error("총 상품수 확인 실패")
                return False
            
            logger.info(f"총 상품수: {total_products}개")
            
            # 3. 500개 이상인 경우에만 연동해제 진행
            if total_products < 500:
                logger.info(f"총 상품수가 {total_products}개로 500개 미만이므로 연동해제를 건너뜁니다")
                return True
            
            # 4. 페이지별 연동해제 실행 (5페이지부터 1페이지까지)
            max_pages = min(5, (total_products + 99) // 100)  # 최대 5페이지, 100개씩
            
            for page in range(max_pages, 0, -1):  # 5, 4, 3, 2, 1 순서
                logger.info(f"페이지 {page} 연동해제 시작")
                
                if not self._disconnect_page_products(store_id_11st, page):
                    logger.error(f"페이지 {page} 연동해제 실패")
                    return False
                
                logger.info(f"페이지 {page} 연동해제 완료")
                
                # 다음 페이지 시작 전 극강화 안정화 대기 (로딩 시간 편차 대응)
                if page > 1:  # 마지막 페이지가 아닌 경우에만
                    logger.info(f"페이지 {page-1} 시작 전 극강화 안정화 대기")
                    self._enhanced_inter_page_stabilization_wait()
            
            logger.info("11번가 연동해제 완료")
            return True
            
        except Exception as e:
            logger.error(f"11번가 연동해제 실패: {e}")
            return False
    
    def _navigate_to_disconnect_page(self, store_id_11st):
        """
        연동해제를 위한 상품 관리 페이지로 이동합니다.
        
        Args:
            store_id_11st (str): 11번가 스토어 ID
            
        Returns:
            bool: 성공 여부
        """
        try:
            from datetime import datetime, timedelta
            
            # 오늘보다 2일 전 날짜 계산
            end_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
            
            # 연동해제 페이지 URL 생성 (첫 페이지는 page=1)
            disconnect_url = (
                f"https://mp.cafe24.com/mp/product/front/manageList?"
                f"sort_direction=ascend&limit=100&is_matched=T&"
                f"search_begin_ymd=2023-07-01&search_end_ymd={end_date}&"
                f"page=1&market_select[]=sk11st%7C{store_id_11st}"
            )
            
            logger.info(f"연동해제 페이지로 이동: {disconnect_url}")
            self.driver.get(disconnect_url)
            
            # 페이지 로드 대기
            time.sleep(3)
            
            logger.info("연동해제 페이지 이동 완료")
            return True
            
        except Exception as e:
            logger.error(f"연동해제 페이지 이동 실패: {e}")
            return False
    
    def _get_total_product_count(self):
        """
        총 상품수를 확인합니다.
        
        Returns:
            int: 총 상품수, 실패 시 None
        """
        try:
            # 총 상품수 요소 찾기
            total_element = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.top-txt-inline span.txt-inline strong"))
            )
            
            total_text = total_element.text.strip()
            # 콤마 제거 후 정수 변환
            total_count = int(total_text.replace(',', ''))
            
            logger.info(f"총 상품수 확인: {total_count}개")
            return total_count
            
        except Exception as e:
            logger.error(f"총 상품수 확인 실패: {e}")
            return None
    
    def _disconnect_page_products(self, store_id_11st, page):
        """
        특정 페이지의 상품들을 연동해제합니다.
        
        Args:
            store_id_11st (str): 11번가 스토어 ID
            page (int): 페이지 번호
            
        Returns:
            bool: 성공 여부
        """
        try:
            from datetime import datetime, timedelta
            
            # 페이지 이동 전 창 상태 확인 및 복구
            if not self._ensure_valid_window():
                logger.error(f"페이지 {page} 이동 전 창 상태 복구 실패")
                return False

            # 현재 작업 창 핸들 저장
            current_work_window = self.driver.current_window_handle
            logger.info(f"페이지 {page} 이동 전 작업 창 핸들: {current_work_window}")

            # 해당 페이지로 이동
            end_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
            page_url = (
                f"https://mp.cafe24.com/mp/product/front/manageList?"
                f"sort_direction=ascend&limit=100&is_matched=T&"
                f"search_begin_ymd=2023-07-01&search_end_ymd={end_date}&"
                f"page={page}&market_select[]=sk11st%7C{store_id_11st}"
            )

            logger.info(f"페이지 {page}로 이동: {page_url}")

            # 현재 창에서 안전한 페이지 이동
            try:
                # 현재 창이 여전히 유효한지 확인
                self.driver.switch_to.window(current_work_window)
                logger.info(f"작업 창 {current_work_window}에서 페이지 이동 시작")
                
                # 현재 창에서 페이지 이동
                self.driver.get(page_url)
                
                # 페이지 이동 후 창 핸들 확인
                after_move_window = self.driver.current_window_handle
                logger.info(f"페이지 이동 후 창 핸들: {after_move_window}")
                
                # 창 핸들이 변경되었다면 원래 창으로 복귀 시도
                if after_move_window != current_work_window:
                    logger.warning(f"창 핸들 변경 감지: {current_work_window} -> {after_move_window}")
                    try:
                        # 원래 창이 여전히 존재하는지 확인
                        available_windows = self.driver.window_handles
                        if current_work_window in available_windows:
                            self.driver.switch_to.window(current_work_window)
                            logger.info(f"원래 작업 창 {current_work_window}으로 복귀")
                            # 원래 창에서 다시 페이지 이동
                            self.driver.get(page_url)
                            logger.info("원래 창에서 페이지 이동 완료")
                        else:
                            logger.warning(f"원래 창 {current_work_window}이 닫혔음 - 현재 창에서 계속 진행")
                    except Exception as switch_e:
                        logger.warning(f"창 전환 실패: {switch_e} - 현재 창에서 계속 진행")
                        
            except Exception as e:
                logger.error(f"페이지 이동 실패: {e}")
                # 창 상태 복구 시도
                if self._ensure_valid_window():
                    logger.info("창 상태 복구 후 페이지 이동 재시도")
                    try:
                        # 복구된 창에서 페이지 이동
                        self.driver.get(page_url)
                        logger.info("창 복구 후 페이지 이동 완료")
                    except Exception as retry_e:
                        logger.error(f"페이지 이동 재시도 실패: {retry_e}")
                        return False
                else:
                    return False
            
            # 기본 페이지 로드 대기
            time.sleep(3)
            
            # 페이지 번호 검증 (최대 3회 재시도)
            for attempt in range(3):
                current_url = self.driver.current_url
                logger.info(f"현재 URL: {current_url}")
                
                # URL에서 page 파라미터 추출
                import re
                page_match = re.search(r'page=(\d+)', current_url)
                if page_match:
                    current_page = int(page_match.group(1))
                    logger.info(f"현재 페이지: {current_page}, 목표 페이지: {page}")
                    
                    if current_page == page:
                        logger.info(f"페이지 {page} 이동 성공 확인")
                        break
                    else:
                        logger.warning(f"페이지 불일치 - 목표: {page}, 현재: {current_page}")
                        if attempt < 2:  # 마지막 시도가 아니면 재시도
                            logger.info(f"페이지 이동 재시도 {attempt + 1}/3")
                            time.sleep(2)
                            self.driver.get(page_url)
                            time.sleep(3)
                        else:
                            logger.error(f"페이지 {page} 이동 실패 - 다른 페이지({current_page})가 열림")
                            return False
                else:
                    logger.warning(f"URL에서 페이지 번호를 찾을 수 없음: {current_url}")
                    if attempt < 2:  # 마지막 시도가 아니면 재시도
                        logger.info(f"페이지 이동 재시도 {attempt + 1}/3")
                        time.sleep(2)
                        self.driver.get(page_url)
                        time.sleep(3)
                    else:
                        logger.warning("페이지 번호 확인 실패 - 계속 진행")
                        break
            
            # 창 상태 재확인
            try:
                current_window = self.driver.current_window_handle
                logger.info(f"현재 창 핸들 확인: {current_window}")
            except Exception as e:
                logger.error(f"창 상태 확인 실패: {e}")
                # 창 상태 복구 시도
                if not self._ensure_valid_window():
                    return False
            
            # 상품 목록 테이블이 로드될 때까지 대기 (성공률 높은 선택자 우선)
            table_loaded = False
            table_selectors = [
                "table[class*='table']",  # 가장 성공률이 높은 선택자를 첫 번째로
                "table.table-list",
                ".table-list",
                ".product-list-table",
                "table tbody tr"
            ]
            
            for selector in table_selectors:
                try:
                    logger.info(f"테이블 로드 확인 선택자 시도: {selector}")
                    WebDriverWait(self.driver, 10).until(  # 대기 시간을 5초에서 10초로 증가
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    logger.info(f"상품 목록 테이블 로드 완료 (선택자: {selector})")
                    table_loaded = True
                    break
                except Exception as e:
                    logger.warning(f"테이블 로드 확인 실패 (선택자: {selector}): {e}")
                    continue
            
            if not table_loaded:
                logger.warning("상품 목록 테이블 로드 확인 실패 - 계속 진행")
            
            # 극강화 페이지 안정화 대기 (로딩 시간 편차 대응 - 최대 75초)
            self._enhanced_page_stabilization_wait()
            
            # JavaScript 실행 완료 대기 (적응형)
            self._adaptive_javascript_load_wait()
            
            # 배치 작업 후 극강화 안정화 대기 (30초+ 로딩 시간 편차 대응)
            self._enhanced_batch_completion_stabilization_wait()
            
            # 1. 전체 선택 체크박스 클릭
            if not self._select_all_products():
                return False
            
            # 2. 판매관리 드롭다운 클릭
            if not self._click_sales_management_dropdown():
                return False
            
            # 3. 연동해제 메뉴 클릭
            if not self._click_disconnect_menu():
                return False
            
            # 4. 첫 번째 JavaScript Alert 확인
            if not self._handle_disconnect_alert():
                return False
            
            # 5. 팝업창에서 전송 버튼 클릭 (Alert 처리 포함)
            if not self._click_send_button_in_popup():
                return False
            
            logger.info(f"페이지 {page} 연동해제 완료")
            return True
            
        except Exception as e:
            logger.error(f"페이지 {page} 연동해제 실패: {e}")
            return False
    
    def _select_all_products(self):
        """
        전체 상품을 선택합니다.
        페이지별 DOM 구조 차이에 대응하는 강화된 로직을 사용합니다.
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("전체 상품 선택")
            
            # 페이지 완전 로드 대기
            self._wait_for_page_load()
            
            # 1단계: 페이지 상태 분석
            page_analysis = self._analyze_page_state()
            logger.info(f"페이지 분석 결과: {page_analysis}")
            
            # 2단계: 적응형 전체 선택 시도
            if self._adaptive_select_all(page_analysis):
                return True
            
            # 3단계: 개별 상품 체크박스 직접 선택 (폴백)
            logger.warning("전체 선택 실패 - 개별 체크박스 직접 선택 시도")
            return self._select_individual_products()
            
        except Exception as e:
            logger.error(f"전체 상품 선택 실패: {e}")
            return False

    def _analyze_page_state(self):
        """
        현재 페이지의 DOM 구조와 상태를 분석합니다.
        
        Returns:
            dict: 페이지 분석 결과
        """
        try:
            analysis = {
                'total_products': 0,
                'all_checkbox_selector': None,
                'product_checkbox_count': 0,
                'page_ready': False,
                'dom_structure': 'unknown'
            }
            
            # 상품 체크박스 수 확인
            product_selectors = [
                'input.rowCk',
                'input[name="idx[]"]',
                'tbody input[type="checkbox"]'
            ]
            
            for selector in product_selectors:
                try:
                    count = self.driver.execute_script(f"""
                        return document.querySelectorAll('{selector}').length;
                    """)
                    if count > 0:
                        analysis['product_checkbox_count'] = count
                        analysis['total_products'] = count
                        logger.info(f"상품 체크박스 발견: {count}개 (선택자: {selector})")
                        break
                except Exception:
                    continue
            
            # 전체 선택 체크박스 찾기
            all_checkbox_selectors = [
                'input.allCk',
                'input[class*="allCk"]',
                'th input[type="checkbox"]',
                'thead input[type="checkbox"]'
            ]
            
            for selector in all_checkbox_selectors:
                try:
                    element_exists = self.driver.execute_script(f"""
                        return document.querySelector('{selector}') !== null;
                    """)
                    if element_exists:
                        analysis['all_checkbox_selector'] = selector
                        logger.info(f"전체 선택 체크박스 발견: {selector}")
                        break
                except Exception:
                    continue
            
            # 페이지 준비 상태 확인
            try:
                ready_state = self.driver.execute_script("return document.readyState;")
                jquery_ready = self.driver.execute_script("return typeof jQuery !== 'undefined' && jQuery.isReady;")
                analysis['page_ready'] = ready_state == 'complete' and jquery_ready
            except Exception:
                analysis['page_ready'] = False
            
            return analysis
            
        except Exception as e:
            logger.error(f"페이지 상태 분석 실패: {e}")
            return {'total_products': 0, 'all_checkbox_selector': None, 'page_ready': False}

    def _adaptive_select_all(self, page_analysis):
        """
        페이지 분석 결과에 따른 적응형 전체 선택을 수행합니다.
        
        Args:
            page_analysis (dict): 페이지 분석 결과
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("적응형 전체 선택 시도")
            
            # 페이지가 준비되지 않은 경우 추가 대기
            if not page_analysis['page_ready']:
                logger.info("페이지 준비 대기 중...")
                time.sleep(3)
                # jQuery 이벤트 완료 대기
                try:
                    self.driver.execute_script("""
                        if (typeof jQuery !== 'undefined') {
                            jQuery(document).ready(function() {
                                console.log('jQuery ready');
                            });
                        }
                    """)
                    time.sleep(2)
                except Exception:
                    pass
            
            # 전체 선택 체크박스가 있는 경우
            if page_analysis['all_checkbox_selector']:
                success = self._try_all_checkbox_selection(page_analysis['all_checkbox_selector'])
                if success:
                    return True
            
            # 전체 선택 체크박스가 없거나 실패한 경우 대안 방법 시도
            logger.info("대안 전체 선택 방법 시도")
            alternative_methods = [
                # jQuery 기반 선택
                """
                if (typeof jQuery !== 'undefined') {
                    jQuery('input.allCk, input[class*="allCk"], th input[type="checkbox"]').first().trigger('click');
                }
                """,
                # 이벤트 기반 클릭
                """
                var checkbox = document.querySelector('input.allCk, input[class*="allCk"], th input[type="checkbox"]');
                if (checkbox) {
                    var event = new MouseEvent('click', { bubbles: true, cancelable: true });
                    checkbox.dispatchEvent(event);
                }
                """,
                # 직접 체크 상태 변경
                """
                var allCheckbox = document.querySelector('input.allCk, input[class*="allCk"], th input[type="checkbox"]');
                var productCheckboxes = document.querySelectorAll('input.rowCk, input[name="idx[]"]');
                if (allCheckbox && productCheckboxes.length > 0) {
                    allCheckbox.checked = true;
                    productCheckboxes.forEach(function(cb) { cb.checked = true; });
                }
                """
            ]
            
            for method in alternative_methods:
                try:
                    logger.info("대안 방법 시도 중...")
                    self.driver.execute_script(method)
                    time.sleep(2)
                    
                    # 결과 확인
                    if self._verify_selection_success(page_analysis['total_products']):
                        logger.info("대안 방법으로 전체 선택 성공")
                        return True
                        
                except Exception as e:
                    logger.warning(f"대안 방법 실패: {e}")
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"적응형 전체 선택 실패: {e}")
            return False

    def _try_all_checkbox_selection(self, selector):
        """
        전체 선택 체크박스를 클릭하여 선택을 시도합니다.
        
        Args:
            selector (str): 전체 선택 체크박스 선택자
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"전체 선택 체크박스 클릭 시도: {selector}")
            
            # 여러 방법으로 클릭 시도
            click_methods = [
                f"document.querySelector('{selector}').click();",
                f"""
                var checkbox = document.querySelector('{selector}');
                if (checkbox) {{
                    checkbox.checked = !checkbox.checked;
                    var event = new Event('change', {{ bubbles: true }});
                    checkbox.dispatchEvent(event);
                }}
                """,
                f"""
                var checkbox = document.querySelector('{selector}');
                if (checkbox) {{
                    var event = new MouseEvent('click', {{ bubbles: true, cancelable: true }});
                    checkbox.dispatchEvent(event);
                }}
                """
            ]
            
            for method in click_methods:
                try:
                    self.driver.execute_script(method)
                    time.sleep(1.5)
                    
                    # 선택 결과 확인
                    product_checked = self.driver.execute_script("""
                        return document.querySelectorAll('input.rowCk:checked, input[name="idx[]"]:checked').length;
                    """)
                    
                    if product_checked > 0:
                        logger.info(f"전체 선택 성공: {product_checked}개 상품 선택됨")
                        return True
                        
                except Exception as e:
                    logger.warning(f"클릭 방법 실패: {e}")
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"전체 선택 체크박스 클릭 실패: {e}")
            return False

    def _select_individual_products(self):
        """
        개별 상품 체크박스를 직접 선택합니다 (폴백 방법).
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("개별 상품 체크박스 직접 선택 시도")
            
            # 모든 상품 체크박스 선택
            success = self.driver.execute_script("""
                var productCheckboxes = document.querySelectorAll('input.rowCk, input[name="idx[]"], tbody input[type="checkbox"]');
                var selectedCount = 0;
                
                productCheckboxes.forEach(function(checkbox) {
                    if (!checkbox.checked) {
                        checkbox.checked = true;
                        selectedCount++;
                        
                        // change 이벤트 발생
                        var event = new Event('change', { bubbles: true });
                        checkbox.dispatchEvent(event);
                    }
                });
                
                return selectedCount;
            """)
            
            if success > 0:
                logger.info(f"개별 선택 성공: {success}개 상품 체크박스 선택됨")
                time.sleep(1)
                return True
            else:
                logger.error("개별 선택 실패: 선택된 체크박스 없음")
                return False
                
        except Exception as e:
            logger.error(f"개별 상품 선택 실패: {e}")
            return False

    def _verify_selection_success(self, expected_count):
        """
        선택 성공 여부를 확인합니다.
        
        Args:
            expected_count (int): 예상 선택 개수
            
        Returns:
            bool: 성공 여부
        """
        try:
            # 상품 체크박스 선택 확인
            selected_count = self.driver.execute_script("""
                return document.querySelectorAll('input.rowCk:checked, input[name="idx[]"]:checked').length;
            """)
            
            total_count = self.driver.execute_script("""
                return document.querySelectorAll('input.rowCk, input[name="idx[]"]').length;
            """)
            
            logger.info(f"선택 확인: {selected_count}/{total_count}개 (예상: {expected_count}개)")
            
            # 최소 1개 이상 선택되었고, 전체 개수와 일치하면 성공
            return selected_count > 0 and (selected_count == total_count or selected_count == expected_count)
            
        except Exception as e:
            logger.error(f"선택 확인 실패: {e}")
            return False

    def _wait_for_page_load(self):
        """
        페이지 로딩 완료를 대기합니다.
        창 상태 확인을 포함하여 안정성을 강화했습니다.
        """
        try:
            # 창 상태 확인
            try:
                current_window = self.driver.current_window_handle
                available_windows = self.driver.window_handles
                logger.info(f"창 상태 확인 - 현재: {current_window}, 사용가능: {len(available_windows)}개")
                
                if current_window not in available_windows:
                    logger.error("현재 창이 닫혀있음 - 사용가능한 창으로 전환")
                    if available_windows:
                        self.driver.switch_to.window(available_windows[-1])
                    else:
                        logger.error("사용가능한 창이 없음")
                        return
                        
            except Exception as e:
                logger.error(f"창 상태 확인 실패: {e}")
                return
            
            # 상품 목록 테이블 로드 대기
            table_selectors = [
                "table[class*='table']",
                "table.table-list", 
                ".table-list"
            ]
            
            table_found = False
            for selector in table_selectors:
                try:
                    logger.info(f"테이블 로드 확인 선택자 시도: {selector}")
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    logger.info(f"상품 목록 테이블 로드 완료 (선택자: {selector})")
                    table_found = True
                    break
                except TimeoutException:
                    logger.warning(f"테이블 로드 확인 실패 (선택자: {selector})")
                    continue
                except Exception as e:
                    logger.warning(f"테이블 로드 확인 중 오류 (선택자: {selector}): {e}")
                    continue
            
            if not table_found:
                logger.warning("모든 테이블 선택자로 테이블을 찾을 수 없음")
            
            # JavaScript 로드 완료 대기
            time.sleep(3)
            try:
                ready_state = self.driver.execute_script("return document.readyState")
                if ready_state == "complete":
                    logger.info("페이지 JavaScript 로드 완료")
                else:
                    logger.warning(f"페이지 로드 상태: {ready_state}")
            except Exception as e:
                logger.warning(f"JavaScript 상태 확인 실패: {e}")
            
            # 추가 안정화 대기
            time.sleep(2)
            
        except Exception as e:
            logger.warning(f"페이지 로드 대기 중 오류: {e}")
    
    def _click_sales_management_dropdown(self):
        """
        판매관리 드롭다운을 클릭합니다.
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("판매관리 드롭다운 클릭")
            
            # 판매관리 버튼 클릭
            sales_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '판매관리')]"))
            )
            sales_button.click()
            
            time.sleep(1)
            logger.info("판매관리 드롭다운 클릭 완료")
            return True
            
        except Exception as e:
            logger.error(f"판매관리 드롭다운 클릭 실패: {e}")
            return False
    
    def _click_disconnect_menu(self):
        """
        연동해제 메뉴를 클릭합니다.
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("연동해제 메뉴 클릭")
            
            # 연동해제 메뉴 클릭
            disconnect_menu = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "li[data-cmd='saleDelete'] a"))
            )
            disconnect_menu.click()
            
            time.sleep(1)
            logger.info("연동해제 메뉴 클릭 완료")
            return True
            
        except Exception as e:
            logger.error(f"연동해제 메뉴 클릭 실패: {e}")
            return False
    
    def _handle_disconnect_alert(self):
        """
        연동해제 확인 JavaScript Alert을 처리합니다.
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("연동해제 확인 Alert 처리")
            
            # Alert 대기 및 확인
            alert = WebDriverWait(self.driver, 10).until(EC.alert_is_present())
            alert_text = alert.text
            logger.info(f"Alert 내용: {alert_text}")
            
            # 확인 버튼 클릭
            alert.accept()
            
            time.sleep(2)
            logger.info("연동해제 확인 Alert 처리 완료")
            return True
            
        except Exception as e:
            logger.error(f"연동해제 확인 Alert 처리 실패: {e}")
            return False
    
    def _click_send_button_in_popup(self):
        """
        팝업창에서 전송 버튼을 클릭합니다.
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("팝업창 전송 버튼 클릭")
            
            # 현재 작업 창 핸들 저장 (작업 중인 탭)
            current_work_window = self.driver.current_window_handle
            logger.info(f"현재 작업 창 핸들: {current_work_window}")
            
            # 팝업창 대기
            WebDriverWait(self.driver, 10).until(lambda d: len(d.window_handles) > len(self.driver.window_handles) - 1)
            time.sleep(2)  # 팝업창 완전 로드 대기
            
            # 창 핸들 조사 최적화 - 화면 깜박거림 완전 제거
            all_windows = self.driver.window_handles
            logger.info(f"현재 열린 창 수: {len(all_windows)}")
            logger.info(f"모든 창 핸들: {all_windows}")
            
            # 팝업창 식별 - URL 확인 없이 마지막 창을 팝업창으로 추정
            popup_window = None
            if len(all_windows) > 1:
                # 현재 창이 아닌 마지막 창을 팝업창으로 추정
                for window in reversed(all_windows):
                    if window != current_work_window:
                        popup_window = window
                        break
                
                if popup_window:
                    logger.info(f"팝업창 핸들: {popup_window}")
                else:
                    logger.warning("팝업창을 찾을 수 없음")
            
            # URL 확인 과정 제거 - 깜박거림 완전 방지
            # sendrequest 팝업창은 연동해제 메뉴 클릭 후 바로 열리므로 
            # 마지막 창이 팝업창일 확률이 매우 높음
            
            if popup_window:
                self.driver.switch_to.window(popup_window)
                logger.info("팝업창으로 전환 완료")
                
                # 팝업창 URL 확인
                popup_url = self.driver.current_url
                logger.info(f"팝업창 URL: {popup_url}")
                
                # 팝업창 완전 로드 대기 - 안정적인 로드 확인
                logger.info("팝업창 완전 로드 대기 중...")
                try:
                    # 1. DOM 로드 완료 대기
                    WebDriverWait(self.driver, 10).until(
                        lambda driver: driver.execute_script("return document.readyState") == "complete"
                    )
                    
                    # 2. 전송 버튼이 로드되고 클릭 가능할 때까지 대기
                    WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.sendRequestSubmit, .sendRequestSubmit, button[class*='sendRequestSubmit']"))
                    )
                    logger.info("팝업창 로드 완료 확인")
                    
                    # 최소한의 안정화 대기만 유지
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.warning(f"팝업창 로드 확인 실패: {e}")
                    # 폴백으로 짧은 대기만 수행
                    time.sleep(1)
                
                # 전송 버튼 클릭 시도
                send_button_selectors = [
                    "button.btn.btn-lg.btn-point.sendRequestSubmit",
                    "button.sendRequestSubmit",
                    "button[class*='sendRequestSubmit']",
                    ".sendRequestSubmit"
                ]
                
                button_clicked = False
                for selector in send_button_selectors:
                    try:
                        logger.info(f"전송 버튼 선택자 시도: {selector}")
                        send_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                        send_button.click()
                        logger.info(f"전송 버튼 클릭 성공 (선택자: {selector})")
                        button_clicked = True
                        break
                    except Exception as e:
                        logger.warning(f"전송 버튼 선택자 실패 ({selector}): {e}")
                        continue
                
                if not button_clicked:
                    # JavaScript로 클릭 시도
                    logger.info("JavaScript로 전송 버튼 클릭 시도")
                    js_commands = [
                        "document.querySelector('button.sendRequestSubmit').click();",
                        "document.querySelector('.sendRequestSubmit').click();",
                        "document.querySelector('button[class*=\"sendRequestSubmit\"]').click();"
                    ]
                    
                    for js_command in js_commands:
                        try:
                            self.driver.execute_script(js_command)
                            logger.info("JavaScript로 전송 버튼 클릭 성공")
                            button_clicked = True
                            break
                        except Exception as e:
                            logger.warning(f"JavaScript 클릭 실패: {e}")
                            continue
                
                if button_clicked:
                    logger.info("팝업창 전송 버튼 클릭 완료")
                    
                    # 팝업창에서 직접 Alert 처리
                    alert_handled = self._handle_popup_alert()
                    
                    if alert_handled:
                        logger.info("팝업창에서 Alert 처리 완료 - 원래 작업 창으로 복귀")
                        # Alert 처리 후 원래 작업 창으로 확실히 복귀
                        try:
                            # 원래 작업 창이 여전히 존재하는지 확인
                            available_windows = self.driver.window_handles
                            if current_work_window in available_windows:
                                self.driver.switch_to.window(current_work_window)
                                logger.info(f"원래 작업 창 {current_work_window}으로 복귀 완료")
                            else:
                                logger.warning(f"원래 작업 창 {current_work_window}이 닫혔음 - 사용 가능한 창으로 전환")
                                if available_windows:
                                    # 첫 번째 사용 가능한 창으로 전환
                                    self.driver.switch_to.window(available_windows[0])
                                    logger.info(f"사용 가능한 창 {available_windows[0]}으로 전환")
                        except Exception as switch_e:
                            logger.warning(f"작업 창 복귀 실패: {switch_e}")
                        return True
                    else:
                        logger.warning("팝업창 Alert 처리 실패 - 원래 작업 창으로 복귀")
                        # Alert 처리 실패 시에도 원래 작업 창으로 복귀
                        try:
                            available_windows = self.driver.window_handles
                            if current_work_window in available_windows:
                                self.driver.switch_to.window(current_work_window)
                                logger.info(f"Alert 처리 실패 후 원래 작업 창 {current_work_window}으로 복귀")
                            else:
                                logger.warning(f"원래 작업 창 {current_work_window}이 닫혔음")
                                if available_windows:
                                    self.driver.switch_to.window(available_windows[0])
                                    logger.info(f"사용 가능한 창 {available_windows[0]}으로 전환")
                        except Exception as e:
                            logger.warning(f"작업 창 복귀 실패: {e}")
                        return False
                else:
                    logger.error("모든 방법으로 전송 버튼 클릭 실패")
                    # 원래 작업 창으로 다시 전환
                    try:
                        available_windows = self.driver.window_handles
                        if current_work_window in available_windows:
                            self.driver.switch_to.window(current_work_window)
                            logger.info(f"전송 버튼 클릭 실패 후 원래 작업 창 {current_work_window}으로 복귀")
                        else:
                            logger.warning(f"원래 작업 창 {current_work_window}이 닫혔음")
                            if available_windows:
                                self.driver.switch_to.window(available_windows[0])
                                logger.info(f"사용 가능한 창 {available_windows[0]}으로 전환")
                    except Exception as e:
                        logger.warning(f"작업 창 복귀 실패: {e}")
                    return False
            else:
                logger.error("팝업창을 찾을 수 없음")
                return False
            
        except Exception as e:
            logger.error(f"팝업창 전송 버튼 클릭 실패: {e}")
            # 오류 발생 시 원래 작업 창으로 복귀 시도
            try:
                if hasattr(self, 'driver') and self.driver.window_handles:
                    # 원래 작업 창으로 복귀 시도
                    available_windows = self.driver.window_handles
                    if hasattr(self, 'current_work_window') and self.current_work_window in available_windows:
                        self.driver.switch_to.window(self.current_work_window)
                        logger.info(f"오류 발생 후 원래 작업 창으로 복귀")
                    elif len(available_windows) > 1:
                        # 두 번째 탭이 작업 탭인 경우가 많음
                        work_window = available_windows[1]
                        self.driver.switch_to.window(work_window)
                        logger.info(f"오류 발생 후 작업 창 {work_window}으로 복귀")
                    else:
                        self.driver.switch_to.window(available_windows[0])
                        logger.info(f"오류 발생 후 첫 번째 창으로 복귀")
            except Exception as recovery_error:
                logger.warning(f"창 복귀 실패: {recovery_error}")
            return False
    
    def _handle_popup_alert(self):
        """
        팝업창에서 전송 완료 Alert을 직접 처리합니다.
        Alert 처리 성공 시 자동으로 메인 창으로 복귀됩니다.
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("팝업창에서 전송 완료 Alert 처리 시작")
            
            # Alert 창이 완전히 열릴 때까지 충분한 대기 시간 확보
            try:
                # Alert 대기 시간을 늘리고 안정성 확보
                logger.info("Alert 창 완전 로드 대기 중...")
                alert = WebDriverWait(self.driver, 20).until(EC.alert_is_present())
                
                # Alert 창이 완전히 렌더링될 때까지 충분한 대기
                logger.info("Alert 창 렌더링 완료 대기...")
                time.sleep(2.5)
                
                alert_text = alert.text
                logger.info(f"팝업창 Alert 발견: {alert_text}")
                
                # Alert 확인 버튼 클릭 전 추가 안정화 대기
                logger.info("Alert 확인 버튼 클릭 준비...")
                time.sleep(1.0)
                
                # Alert 확인 버튼 클릭
                alert.accept()
                logger.info("Alert 확인 버튼 클릭 완료")
                
                # Alert 처리 완료 후 자동 복귀 대기
                time.sleep(2)
                
                logger.info("팝업창 Alert 처리 완료 - 자동으로 메인 창으로 복귀됨")
                return True
                
            except TimeoutException:
                logger.warning("팝업창에서 Alert를 찾을 수 없음 (15초 대기)")
                return False
                
        except Exception as e:
            logger.error(f"팝업창 Alert 처리 실패: {e}")
            return False
    
    def _handle_completion_alert(self):
        """
        전송 완료 JavaScript Alert을 처리합니다.
        현재 창에서만 Alert 처리를 시도하며, 실패 시 간단한 재시도만 수행합니다.
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("전송 완료 Alert 처리")
            
            # 현재 창에서 Alert 처리 시도 (최대 2회)
            for attempt in range(2):
                try:
                    wait_time = 5 + (attempt * 3)  # 5초, 8초
                    logger.info(f"Alert 대기 중 (시도 {attempt + 1}/2, 대기시간: {wait_time}초)")
                    
                    alert = WebDriverWait(self.driver, wait_time).until(EC.alert_is_present())
                    alert_text = alert.text
                    logger.info(f"Alert 발견: {alert_text}")
                    
                    # 확인 버튼 클릭
                    alert.accept()
                    time.sleep(2)
                    
                    logger.info("전송 완료 Alert 처리 완료")
                    return True
                    
                except Exception as e:
                    logger.warning(f"Alert 처리 실패 (시도 {attempt + 1}/2): {e}")
                    if attempt < 1:  # 마지막 시도가 아닌 경우
                        time.sleep(2)
                        continue
            
            # 모든 시도 실패 시
            logger.warning("Alert 처리 실패 - 작업 계속 진행")
            return False
            
        except Exception as e:
            logger.error(f"전송 완료 Alert 처리 실패: {e}")
            return False
    
    def _logout(self):
        """
        카페24에서 로그아웃합니다. 로그아웃 성공 여부를 확인하며, 실패 시 최대 2회 재시도합니다.
        
        Returns:
            bool: 성공 여부
        """
        for attempt in range(2):  # 최대 2회 시도
            try:
                logger.info(f"카페24 로그아웃 (시도 {attempt + 1}/2)")
                
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
                time.sleep(3)
                
                # 로그아웃 성공 여부 확인
                if self._check_logout_success():
                    logger.info(f"카페24 로그아웃 성공 (시도 {attempt + 1}/2)")
                    return True
                else:
                    logger.warning(f"로그아웃 후 상태 확인 실패 (시도 {attempt + 1}/2)")
                    if attempt < 1:  # 마지막 시도가 아닌 경우
                        logger.info("로그아웃 재시도 준비 중...")
                        time.sleep(2)
                        continue
                
            except Exception as e:
                logger.error(f"카페24 로그아웃 실패 (시도 {attempt + 1}/2): {e}")
                if attempt < 1:  # 마지막 시도가 아닌 경우
                    logger.info("로그아웃 재시도 준비 중...")
                    time.sleep(2)
                    continue
        
        logger.error("카페24 로그아웃 2회 시도 모두 실패")
        return False
    
    def _check_logout_success(self):
        """
        로그아웃 성공 여부를 확인합니다.
        
        Returns:
            bool: 로그아웃 성공 여부
        """
        try:
            current_url = self.driver.current_url
            logger.info(f"로그아웃 후 현재 URL: {current_url}")
            
            # 로그인 페이지로 리다이렉트되었는지 확인
            if "eclogin.cafe24.com" in current_url or "login" in current_url.lower():
                logger.info("로그아웃 성공 확인 - 로그인 페이지로 이동됨")
                return True
            else:
                logger.warning(f"로그아웃 실패 - 여전히 로그인 상태: {current_url}")
                return False
                
        except Exception as e:
            logger.error(f"로그아웃 성공 확인 실패: {e}")
            return False
    
    def _check_and_prepare_login_page(self):
        """
        로그인 페이지 상태를 확인하고 필요시 로그아웃을 수행합니다.
        
        Returns:
            bool: 로그인 페이지 준비 성공 여부
        """
        try:
            logger.info("로그인 페이지 상태 확인")
            
            # 현재 페이지에서 로그인 입력창 존재 여부 확인
            try:
                # 아이디 입력창 확인 (3초 대기)
                id_input = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.ID, "mall_id"))
                )
                
                # 비밀번호 입력창 확인
                password_input = self.driver.find_element(By.ID, "userpasswd")
                
                # 로그인 버튼 확인
                login_button = self.driver.find_element(By.CSS_SELECTOR, "button.btnStrong.large")
                
                # 모든 요소가 표시되는지 확인
                if (id_input.is_displayed() and password_input.is_displayed() and 
                    login_button.is_displayed()):
                    logger.info("정상적인 로그인 페이지 확인 - 로그인 진행")
                    return True
                else:
                    logger.warning("로그인 요소들이 표시되지 않음 - 로그아웃 후 재시도")
                    return self._force_logout_and_retry()
                    
            except (TimeoutException, NoSuchElementException):
                logger.warning("로그인 입력창을 찾을 수 없음 - 이미 로그인된 상태일 가능성")
                return self._force_logout_and_retry()
                
        except Exception as e:
            logger.error(f"로그인 페이지 상태 확인 실패: {e}")
            return False
    
    def _force_logout_and_retry(self):
        """
        강제 로그아웃을 수행하고 로그인 페이지로 이동합니다.
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("강제 로그아웃 및 로그인 페이지 재로드 시도")
            
            # 현재 URL 확인
            current_url = self.driver.current_url
            logger.info(f"현재 URL: {current_url}")
            
            # 이미 로그인된 상태인지 확인 (카페24 관리자 페이지에 있는 경우)
            if "mp.cafe24.com" in current_url:
                logger.info("카페24 관리자 페이지에서 로그아웃 시도")
                if self._logout():
                    logger.info("로그아웃 성공 - 로그인 페이지로 이동")
                    # 로그인 페이지로 직접 이동
                    self.driver.get("https://eclogin.cafe24.com/Shop/?mode=mp")
                    time.sleep(3)
                else:
                    logger.warning("로그아웃 실패 - 로그인 페이지로 강제 이동")
                    # 로그아웃 실패 시에도 로그인 페이지로 강제 이동
                    self.driver.get("https://eclogin.cafe24.com/Shop/?mode=mp")
                    time.sleep(3)
            else:
                logger.info("로그인 페이지로 직접 이동")
                # 로그인 페이지로 이동
                self.driver.get("https://eclogin.cafe24.com/Shop/?mode=mp")
                time.sleep(3)
            
            # 로그인 페이지 요소 재확인
            try:
                id_input = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.ID, "mall_id"))
                )
                password_input = self.driver.find_element(By.ID, "userpasswd")
                login_button = self.driver.find_element(By.CSS_SELECTOR, "button.btnStrong.large")
                
                if (id_input.is_displayed() and password_input.is_displayed() and 
                    login_button.is_displayed()):
                    logger.info("로그인 페이지 준비 완료")
                    return True
                else:
                    logger.error("로그인 페이지 요소들이 여전히 표시되지 않음")
                    return False
                    
            except (TimeoutException, NoSuchElementException) as e:
                logger.error(f"로그인 페이지 요소 재확인 실패: {e}")
                return False
                
        except Exception as e:
            logger.error(f"강제 로그아웃 및 재시도 실패: {e}")
            return False
    
    def _enhanced_page_stabilization_wait(self):
        """
        극강화된 페이지 안정화 대기.
        30초 이상의 극심한 로딩 시간 편차에도 대응합니다.
        사용자 트래픽 증가, 서버 부하 등 모든 상황을 고려한 안정화 로직입니다.
        """
        try:
            logger.info("🔄 극강화 페이지 안정화 대기 시작 (최대 75초)")
            max_wait_time = 75  # 최대 75초 대기 (극심한 로딩 시간 대응)
            check_interval = 2  # 2초마다 확인
            start_time = time.time()
            
            # 초기 페이지 로딩 시간 확보
            logger.info("⏳ 초기 페이지 로딩 대기 (8초)")
            time.sleep(8)
            
            # 안정화 상태 추적 변수
            consecutive_failures = 0
            server_overload_detected = False
            network_instability_detected = False
            extreme_load_detected = False
            dom_instability_detected = False
            
            # 다단계 안정화 체크포인트
            stability_checkpoints = {
                'document_ready': False,
                'jquery_ready': False,
                'table_loaded': False,
                'checkboxes_loaded': False,
                'interactive_elements': False,
                'network_stable': False,
                'browser_responsive': False,
                'no_active_requests': False
            }
            
            while time.time() - start_time < max_wait_time:
                try:
                    elapsed_time = time.time() - start_time
                    
                    # 1. 기본 문서 상태 확인
                    document_status = self.driver.execute_script("""
                        try {
                            return {
                                readyState: document.readyState,
                                documentReady: document.readyState === 'complete',
                                visibilityState: document.visibilityState,
                                hasFocus: document.hasFocus(),
                                url: window.location.href
                            };
                        } catch(e) {
                            return {readyState: 'loading', documentReady: false, visibilityState: 'visible', hasFocus: true, url: ''};
                        }
                    """)
                    
                    stability_checkpoints['document_ready'] = document_status.get('documentReady', False)
                    
                    # 2. jQuery 및 JavaScript 상태 확인
                    js_status = self.driver.execute_script("""
                        try {
                            var jsCheck = {
                                jqueryExists: typeof jQuery !== 'undefined',
                                jqueryReady: false,
                                ajaxComplete: false,
                                noActiveAjax: true,
                                scriptsLoaded: true
                            };
                            
                            if (typeof jQuery !== 'undefined') {
                                jsCheck.jqueryReady = jQuery.isReady;
                                if (jQuery.active !== undefined) {
                                    jsCheck.ajaxComplete = jQuery.active === 0;
                                    jsCheck.noActiveAjax = jQuery.active === 0;
                                } else {
                                    jsCheck.ajaxComplete = true;
                                    jsCheck.noActiveAjax = true;
                                }
                            } else {
                                jsCheck.jqueryReady = true; // jQuery가 없으면 통과
                                jsCheck.ajaxComplete = true;
                            }
                            
                            // 스크립트 로딩 상태
                            var scripts = document.querySelectorAll('script');
                            jsCheck.scriptsLoaded = scripts.length > 0;
                            
                            return jsCheck;
                        } catch(e) {
                            return {jqueryExists: false, jqueryReady: true, ajaxComplete: true, noActiveAjax: true, scriptsLoaded: true};
                        }
                    """)
                    
                    stability_checkpoints['jquery_ready'] = js_status.get('jqueryReady', True) and js_status.get('ajaxComplete', True)
                    stability_checkpoints['no_active_requests'] = js_status.get('noActiveAjax', True)
                    
                    # 3. 테이블 및 상품 목록 확인 (강화된 버전)
                    table_status = self.driver.execute_script("""
                        try {
                            var tableCheck = {
                                hasTable: false,
                                tableRowCount: 0,
                                hasProductRows: false,
                                tableVisible: false,
                                tableComplete: false
                            };
                            
                            // 다양한 테이블 선택자로 확인
                            var tables = document.querySelectorAll('table[class*="table"], .table-list, table, .product-list-table');
                            tableCheck.hasTable = tables.length > 0;
                            
                            if (tables.length > 0) {
                                var mainTable = tables[0];
                                var rows = mainTable.querySelectorAll('tbody tr, tr');
                                tableCheck.tableRowCount = rows.length;
                                tableCheck.hasProductRows = rows.length > 0;
                                
                                // 테이블 가시성 확인
                                var style = window.getComputedStyle(mainTable);
                                tableCheck.tableVisible = style.display !== 'none' && style.visibility !== 'hidden';
                                
                                // 테이블 완성도 확인 (최소 1개 이상의 행)
                                tableCheck.tableComplete = rows.length > 0 && tableCheck.tableVisible;
                            }
                            
                            return tableCheck;
                        } catch(e) {
                            return {hasTable: false, tableRowCount: 0, hasProductRows: false, tableVisible: false, tableComplete: false};
                        }
                    """)
                    
                    stability_checkpoints['table_loaded'] = table_status.get('tableComplete', False)
                    
                    # 4. 체크박스 및 인터랙티브 요소 확인
                    checkbox_status = self.driver.execute_script("""
                        try {
                            var checkboxCheck = {
                                productCheckboxes: 0,
                                allCheckbox: false,
                                checkboxesVisible: false,
                                checkboxesInteractive: false
                            };
                            
                            // 상품 체크박스 확인
                            var productCbs = document.querySelectorAll('input.rowCk, input[name="idx[]"], tbody input[type="checkbox"]');
                            checkboxCheck.productCheckboxes = productCbs.length;
                            
                            // 전체 선택 체크박스 확인
                            var allCb = document.querySelector('input.allCk, input[class*="allCk"], th input[type="checkbox"], thead input[type="checkbox"]');
                            checkboxCheck.allCheckbox = allCb !== null;
                            
                            // 체크박스 가시성 및 상호작용 가능성 확인
                            if (productCbs.length > 0) {
                                var firstCb = productCbs[0];
                                var style = window.getComputedStyle(firstCb);
                                checkboxCheck.checkboxesVisible = style.display !== 'none' && style.visibility !== 'hidden';
                                checkboxCheck.checkboxesInteractive = !firstCb.disabled;
                            }
                            
                            return checkboxCheck;
                        } catch(e) {
                            return {productCheckboxes: 0, allCheckbox: false, checkboxesVisible: false, checkboxesInteractive: false};
                        }
                    """)
                    
                    stability_checkpoints['checkboxes_loaded'] = (
                        checkbox_status.get('productCheckboxes', 0) > 0 and 
                        checkbox_status.get('checkboxesVisible', False) and 
                        checkbox_status.get('checkboxesInteractive', False)
                    )
                    
                    # 5. 인터랙티브 요소 및 컨트롤 확인
                    interactive_status = self.driver.execute_script("""
                        try {
                            var interactiveCheck = {
                                buttons: 0,
                                dropdowns: 0,
                                links: 0,
                                totalInteractive: 0,
                                navigationExists: false,
                                controlsReady: false
                            };
                            
                            // 버튼 확인
                            var buttons = document.querySelectorAll('button, input[type="button"], input[type="submit"], [class*="btn"]');
                            interactiveCheck.buttons = buttons.length;
                            
                            // 드롭다운 확인
                            var dropdowns = document.querySelectorAll('select, .dropdown, [class*="dropdown"]');
                            interactiveCheck.dropdowns = dropdowns.length;
                            
                            // 링크 확인
                            var links = document.querySelectorAll('a[href]');
                            interactiveCheck.links = links.length;
                            
                            interactiveCheck.totalInteractive = buttons.length + dropdowns.length + links.length;
                            
                            // 페이지네이션 확인
                            var pagination = document.querySelectorAll('.pagination, .paging, [class*="page"]');
                            interactiveCheck.navigationExists = pagination.length > 0;
                            
                            // 전체적인 컨트롤 준비 상태
                            interactiveCheck.controlsReady = interactiveCheck.totalInteractive > 5 && interactiveCheck.navigationExists;
                            
                            return interactiveCheck;
                        } catch(e) {
                            return {buttons: 0, dropdowns: 0, links: 0, totalInteractive: 0, navigationExists: false, controlsReady: false};
                        }
                    """)
                    
                    stability_checkpoints['interactive_elements'] = interactive_status.get('controlsReady', False)
                    
                    # 6. 네트워크 및 브라우저 응답성 확인
                    performance_status = self.driver.execute_script("""
                        try {
                            var perfStart = performance.now();
                            
                            // DOM 조작 테스트
                            var testDiv = document.createElement('div');
                            testDiv.id = 'enhanced_stability_test_' + Date.now();
                            testDiv.style.display = 'none';
                            document.body.appendChild(testDiv);
                            
                            // 스타일 조작 테스트
                            testDiv.style.color = 'red';
                            testDiv.style.backgroundColor = 'blue';
                            
                            // 요소 검색 테스트
                            var found = document.getElementById(testDiv.id);
                            
                            // 정리
                            document.body.removeChild(testDiv);
                            
                            var perfEnd = performance.now();
                            var responseTime = perfEnd - perfStart;
                            
                            // 네트워크 상태
                            var networkInfo = {
                                online: navigator.onLine,
                                connectionType: 'unknown'
                            };
                            
                            if ('connection' in navigator) {
                                var conn = navigator.connection;
                                networkInfo.connectionType = conn.effectiveType || 'unknown';
                                networkInfo.downlink = conn.downlink || 0;
                                networkInfo.rtt = conn.rtt || 0;
                            }
                            
                            return {
                                responseTime: responseTime,
                                performanceGood: responseTime < 100,
                                domManipulationSuccess: found !== null,
                                network: networkInfo
                            };
                        } catch(e) {
                            return {responseTime: 9999, performanceGood: false, domManipulationSuccess: false, network: {online: true}};
                        }
                    """)
                    
                    stability_checkpoints['browser_responsive'] = performance_status.get('domManipulationSuccess', False)
                    stability_checkpoints['network_stable'] = performance_status.get('network', {}).get('online', True)
                    
                    # 7. 서버 부하 및 성능 이슈 감지
                    response_time = performance_status.get('responseTime', 0)
                    performance_good = performance_status.get('performanceGood', True)
                    
                    if not performance_good or response_time > 300:
                        consecutive_failures += 1
                        if consecutive_failures >= 3:
                            server_overload_detected = True
                            logger.warning(f"🚨 서버 과부하 감지됨 (응답시간: {response_time:.1f}ms, 연속실패: {consecutive_failures}회)")
                    else:
                        consecutive_failures = max(0, consecutive_failures - 1)
                    
                    # 네트워크 불안정 감지
                    network_rtt = performance_status.get('network', {}).get('rtt', 0)
                    if network_rtt > 800:  # 800ms 이상 RTT
                        network_instability_detected = True
                        logger.warning(f"🌐 네트워크 불안정 감지됨 (RTT: {network_rtt}ms)")
                    
                    # 극심한 부하 감지
                    if consecutive_failures >= 5 or response_time > 1500:
                        extreme_load_detected = True
                        logger.warning(f"⚠️ 극심한 서버 부하 감지됨 (응답시간: {response_time:.1f}ms)")
                    
                    # DOM 불안정 감지
                    table_count = table_status.get('tableRowCount', 0)
                    checkbox_count = checkbox_status.get('productCheckboxes', 0)
                    if table_count == 0 or checkbox_count == 0:
                        dom_instability_detected = True
                    
                    # 8. 안정화 완료 조건 확인
                    stability_score = sum(stability_checkpoints.values())
                    total_checkpoints = len(stability_checkpoints)
                    
                    logger.info(f"🔍 극강화 페이지 안정화 상태 (경과: {elapsed_time:.1f}초): "
                              f"체크포인트 {stability_score}/{total_checkpoints} "
                              f"(문서: {stability_checkpoints['document_ready']}, "
                              f"jQuery: {stability_checkpoints['jquery_ready']}, "
                              f"테이블: {stability_checkpoints['table_loaded']}, "
                              f"체크박스: {stability_checkpoints['checkboxes_loaded']}, "
                              f"인터랙션: {stability_checkpoints['interactive_elements']}, "
                              f"네트워크: {stability_checkpoints['network_stable']}, "
                              f"브라우저: {stability_checkpoints['browser_responsive']}, "
                              f"요청: {stability_checkpoints['no_active_requests']}) "
                              f"응답시간: {response_time:.1f}ms")
                    
                    # 9. 안정화 완료 판정 (엄격한 기준)
                    if stability_score >= total_checkpoints - 1:  # 최소 7/8 체크포인트 통과
                        logger.info(f"✅ 극강화 페이지 안정화 성공 (소요시간: {elapsed_time:.1f}초, 점수: {stability_score}/{total_checkpoints})")
                        
                        # 서버 부하 상황에 따른 추가 대기
                        if extreme_load_detected:
                            logger.info("⏰ 극심한 부하 감지로 인한 추가 안정화 대기 (6초)")
                            time.sleep(6)
                        elif server_overload_detected:
                            logger.info("⏰ 서버 과부하 감지로 인한 추가 안정화 대기 (4초)")
                            time.sleep(4)
                        elif network_instability_detected:
                            logger.info("⏰ 네트워크 불안정으로 인한 추가 안정화 대기 (3초)")
                            time.sleep(3)
                        elif dom_instability_detected:
                            logger.info("⏰ DOM 불안정으로 인한 추가 안정화 대기 (2초)")
                            time.sleep(2)
                        else:
                            time.sleep(1.5)  # 기본 최종 안정화
                        return
                    
                    # 10. 적응형 대기 간격 조정
                    if extreme_load_detected:
                        adaptive_interval = min(check_interval * 3, 6)  # 최대 6초
                        logger.info(f"🐌 극심한 부하 - 적응형 대기 간격: {adaptive_interval}초")
                        time.sleep(adaptive_interval)
                    elif server_overload_detected:
                        adaptive_interval = min(check_interval * 2.5, 5)  # 최대 5초
                        logger.info(f"🐌 서버 과부하 - 적응형 대기 간격: {adaptive_interval}초")
                        time.sleep(adaptive_interval)
                    elif network_instability_detected or dom_instability_detected:
                        adaptive_interval = min(check_interval * 2, 4)  # 최대 4초
                        logger.info(f"🐌 네트워크/DOM 불안정 - 적응형 대기 간격: {adaptive_interval}초")
                        time.sleep(adaptive_interval)
                    else:
                        time.sleep(check_interval)
                    
                except Exception as e:
                    logger.warning(f"⚠️ 극강화 페이지 안정화 상태 확인 중 오류: {e}")
                    consecutive_failures += 1
                    time.sleep(check_interval)
                    continue
            
            # 최대 대기 시간 초과
            elapsed_total = time.time() - start_time
            logger.warning(f"⏰ 극강화 페이지 안정화 최대 대기 시간 초과 ({elapsed_total:.1f}초/{max_wait_time}초)")
            
            # 상황별 최종 대기
            if extreme_load_detected:
                logger.warning("🚨 극심한 부하 상황에서 최대 대기 시간 초과 - 최종 안정화 대기 (12초)")
                time.sleep(12)
            elif server_overload_detected:
                logger.warning("🚨 서버 과부하 상황에서 최대 대기 시간 초과 - 최종 안정화 대기 (8초)")
                time.sleep(8)
            elif network_instability_detected:
                logger.warning("🚨 네트워크 불안정 상황에서 최대 대기 시간 초과 - 최종 안정화 대기 (6초)")
                time.sleep(6)
            elif dom_instability_detected:
                logger.warning("🚨 DOM 불안정 상황에서 최대 대기 시간 초과 - 최종 안정화 대기 (5초)")
                time.sleep(5)
            else:
                time.sleep(4)  # 기본 최종 안정화 대기
            
        except Exception as e:
            logger.error(f"❌ 극강화 페이지 안정화 대기 실패: {e}")
            time.sleep(10)  # 폴백 대기 (더 긴 시간)

    def _adaptive_page_stabilization_wait(self):
        """
        페이지 로딩 안정화를 위한 적응형 대기.
        로딩 시간 편차에 대응하여 최대 60초까지 대기합니다.
        30초 이상의 긴 로딩 시간에도 대응합니다.
        """
        try:
            logger.info("적응형 페이지 안정화 대기 시작 (강화된 버전)")
            max_wait_time = 60  # 최대 60초 대기 (30초 이상 대응)
            check_interval = 2  # 2초마다 확인
            start_time = time.time()
            
            # 서버 부하 감지 변수
            consecutive_failures = 0
            server_load_detected = False
            
            while time.time() - start_time < max_wait_time:
                try:
                    elapsed_time = time.time() - start_time
                    
                    # 1. 기본 페이지 상태 확인
                    ready_state = self.driver.execute_script("return document.readyState")
                    page_ready = ready_state == "complete"
                    
                    # 2. 브라우저 응답성 확인 (강화된 버전)
                    browser_responsive = self.driver.execute_script("""
                        try {
                            // DOM 조작 테스트
                            var testDiv = document.createElement('div');
                            testDiv.id = 'page_stability_test_' + Date.now();
                            document.body.appendChild(testDiv);
                            var found = document.getElementById(testDiv.id);
                            document.body.removeChild(testDiv);
                            
                            // 스크롤 테스트 (페이지 인터랙션 확인)
                            var currentScroll = window.pageYOffset;
                            window.scrollTo(0, currentScroll + 1);
                            window.scrollTo(0, currentScroll);
                            
                            return found !== null;
                        } catch(e) {
                            return false;
                        }
                    """)
                    
                    # 3. 테이블 및 핵심 요소 존재 확인
                    table_exists = self.driver.execute_script("""
                        return document.querySelector('table[class*="table"], .table-list') !== null;
                    """)
                    
                    # 4. 상품 체크박스 존재 확인
                    checkbox_count = self.driver.execute_script("""
                        return document.querySelectorAll('input.rowCk, input[name="idx[]"]').length;
                    """)
                    
                    # 5. 네트워크 및 로딩 상태 확인
                    network_status = self.driver.execute_script("""
                        try {
                            var networkOnline = navigator.onLine;
                            var loadComplete = document.readyState === 'complete';
                            
                            // 이미지 로딩 상태 확인
                            var images = document.querySelectorAll('img');
                            var imagesLoaded = true;
                            for (var i = 0; i < Math.min(images.length, 5); i++) {
                                if (!images[i].complete) {
                                    imagesLoaded = false;
                                    break;
                                }
                            }
                            
                            return {
                                online: networkOnline,
                                loadComplete: loadComplete,
                                imagesLoaded: imagesLoaded
                            };
                        } catch(e) {
                            return {online: true, loadComplete: true, imagesLoaded: true};
                        }
                    """)
                    
                    # 6. URL 안정성 확인
                    current_url = self.driver.current_url
                    url_stable = "cafe24.com" in current_url
                    
                    # 7. 창 상태 확인
                    window_stable = True
                    try:
                        current_window = self.driver.current_window_handle
                        available_windows = self.driver.window_handles
                        window_stable = current_window in available_windows
                    except Exception:
                        window_stable = False
                    
                    # 8. 서버 부하 감지
                    if not browser_responsive or not network_status.get('online', True):
                        consecutive_failures += 1
                        if consecutive_failures >= 3:
                            server_load_detected = True
                            logger.warning(f"페이지 로딩 중 서버 부하 감지됨 (연속 실패: {consecutive_failures}회)")
                    else:
                        consecutive_failures = 0
                    
                    # 9. 안정화 완료 조건 확인
                    stability_conditions = [
                        page_ready,
                        browser_responsive,
                        table_exists,
                        checkbox_count > 0,
                        network_status.get('online', True),
                        network_status.get('loadComplete', True),
                        url_stable,
                        window_stable
                    ]
                    
                    stability_score = sum(stability_conditions)
                    total_conditions = len(stability_conditions)
                    
                    logger.info(f"페이지 안정화 상태 (경과: {elapsed_time:.1f}초): "
                              f"안정성 점수 {stability_score}/{total_conditions} "
                              f"(페이지준비: {page_ready}, 브라우저응답: {browser_responsive}, "
                              f"테이블: {table_exists}, 체크박스: {checkbox_count}개, "
                              f"네트워크: {network_status.get('online')}, URL안정: {url_stable}, 창안정: {window_stable})")
                    
                    # 10. 안정화 완료 판정
                    if stability_score >= total_conditions - 1:  # 최소 7/8 조건 만족
                        logger.info(f"페이지 안정화 완료 (소요시간: {elapsed_time:.1f}초, 점수: {stability_score}/{total_conditions})")
                        
                        # 서버 부하가 감지된 경우 추가 대기
                        if server_load_detected:
                            logger.info("서버 부하 감지로 인한 추가 안정화 대기 (3초)")
                            time.sleep(3)
                        else:
                            time.sleep(1)  # 기본 최종 안정화
                        return
                    
                    # 11. 서버 부하 상황에서의 적응형 대기
                    if server_load_detected:
                        adaptive_interval = min(check_interval * 1.5, 4)  # 최대 4초
                        logger.info(f"서버 부하 상황 - 적응형 대기 간격: {adaptive_interval}초")
                        time.sleep(adaptive_interval)
                    else:
                        time.sleep(check_interval)
                    
                except Exception as e:
                    logger.warning(f"페이지 안정화 상태 확인 중 오류: {e}")
                    consecutive_failures += 1
                    time.sleep(check_interval)
                    continue
            
            # 최대 대기 시간 초과
            elapsed_total = time.time() - start_time
            logger.warning(f"페이지 안정화 최대 대기 시간 초과 ({elapsed_total:.1f}초/{max_wait_time}초)")
            
            # 서버 부하가 심한 경우 추가 대기
            if server_load_detected:
                logger.warning("서버 부하 상황에서 최대 대기 시간 초과 - 추가 안정화 대기 (5초)")
                time.sleep(5)
            else:
                time.sleep(2)  # 기본 안정화 대기
            
        except Exception as e:
            logger.error(f"적응형 페이지 안정화 대기 실패: {e}")
            time.sleep(5)  # 폴백 대기

    def _adaptive_javascript_load_wait(self):
        """
        JavaScript 로딩 완료를 위한 적응형 대기.
        jQuery 및 페이지 스크립트 로딩을 확인합니다.
        """
        try:
            logger.info("적응형 JavaScript 로딩 대기 시작")
            max_wait_time = 30  # 최대 30초 대기
            check_interval = 1.5  # 1.5초마다 확인
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                try:
                    # jQuery 로딩 확인
                    jquery_ready = self.driver.execute_script("""
                        return typeof jQuery !== 'undefined' && jQuery.isReady;
                    """)
                    
                    # DOM 완전 로딩 확인
                    dom_ready = self.driver.execute_script("return document.readyState === 'complete'")
                    
                    # 페이지 내 스크립트 실행 완료 확인
                    scripts_loaded = self.driver.execute_script("""
                        return document.querySelectorAll('script').length > 0;
                    """)
                    
                    elapsed_time = time.time() - start_time
                    
                    if jquery_ready and dom_ready and scripts_loaded:
                        logger.info(f"JavaScript 로딩 완료 (소요시간: {elapsed_time:.1f}초)")
                        time.sleep(0.5)  # 추가 안정화
                        return
                    
                    logger.info(f"JavaScript 로딩 대기 중... (경과: {elapsed_time:.1f}초, jQuery: {jquery_ready}, DOM: {dom_ready})")
                    time.sleep(check_interval)
                    
                except Exception as e:
                    logger.warning(f"JavaScript 상태 확인 중 오류: {e}")
                    time.sleep(check_interval)
                    continue
            
            # 최대 대기 시간 초과
            logger.warning(f"JavaScript 로딩 최대 대기 시간 초과 ({max_wait_time}초)")
            time.sleep(1)  # 기본 안정화 대기
            
        except Exception as e:
            logger.error(f"적응형 JavaScript 로딩 대기 실패: {e}")
            time.sleep(2)  # 폴백 대기

    def _enhanced_batch_completion_stabilization_wait(self):
        """
        배치 작업 완료 후 극도로 강화된 안정화 대기.
        30초 이상의 극심한 로딩 시간 편차에도 대응합니다.
        서버 부하, 네트워크 지연, 대용량 데이터 처리 등 모든 상황을 고려합니다.
        """
        try:
            logger.info("🔄 극강화 배치 완료 안정화 대기 시작 (최대 120초)")
            max_wait_time = 120  # 최대 120초 대기 (극심한 로딩 시간 대응)
            check_interval = 3  # 3초마다 확인 (더 안정적인 모니터링)
            start_time = time.time()
            
            # 초기 서버 처리 시간 확보 (더 긴 대기)
            logger.info("⏳ 서버 배치 처리 완료 대기 (초기 10초)")
            time.sleep(10)
            
            # 서버 상태 모니터링 변수
            consecutive_failures = 0
            server_overload_detected = False
            network_instability_detected = False
            extreme_load_detected = False
            
            # 안정화 단계별 체크포인트
            stability_checkpoints = {
                'basic_response': False,
                'network_stable': False,
                'dom_ready': False,
                'ui_elements_loaded': False,
                'javascript_ready': False,
                'server_responsive': False
            }
            
            while time.time() - start_time < max_wait_time:
                try:
                    elapsed_time = time.time() - start_time
                    
                    # 1. 기본 브라우저 응답성 확인 (강화된 버전)
                    browser_response = self.driver.execute_script("""
                        try {
                            // 복합적인 브라우저 응답성 테스트
                            var startTime = performance.now();
                            
                            // DOM 조작 테스트
                            var testDiv = document.createElement('div');
                            testDiv.id = 'extreme_stability_test_' + Date.now();
                            testDiv.style.display = 'none';
                            document.body.appendChild(testDiv);
                            
                            // 요소 검색 테스트
                            var found = document.getElementById(testDiv.id);
                            
                            // 스타일 조작 테스트
                            if (found) {
                                found.style.color = 'red';
                                found.style.color = 'blue';
                            }
                            
                            // 정리
                            document.body.removeChild(testDiv);
                            
                            var endTime = performance.now();
                            var responseTime = endTime - startTime;
                            
                            return {
                                success: found !== null,
                                responseTime: responseTime,
                                performanceGood: responseTime < 100
                            };
                        } catch(e) {
                            return {success: false, responseTime: 9999, performanceGood: false};
                        }
                    """)
                    
                    stability_checkpoints['basic_response'] = browser_response.get('success', False)
                    
                    # 2. 네트워크 상태 및 연결 안정성 확인
                    network_status = self.driver.execute_script("""
                        try {
                            var networkInfo = {
                                online: navigator.onLine,
                                connectionType: 'unknown',
                                effectiveType: 'unknown',
                                downlink: 0,
                                rtt: 0
                            };
                            
                            // 네트워크 정보 수집 (가능한 경우)
                            if ('connection' in navigator) {
                                var conn = navigator.connection;
                                networkInfo.connectionType = conn.type || 'unknown';
                                networkInfo.effectiveType = conn.effectiveType || 'unknown';
                                networkInfo.downlink = conn.downlink || 0;
                                networkInfo.rtt = conn.rtt || 0;
                            }
                            
                            // 페이지 로딩 상태
                            var loadingInfo = {
                                readyState: document.readyState,
                                loadComplete: document.readyState === 'complete',
                                visibilityState: document.visibilityState
                            };
                            
                            // 활성 네트워크 요청 확인
                            var hasActiveRequests = false;
                            if (typeof performance !== 'undefined' && performance.getEntriesByType) {
                                var navEntries = performance.getEntriesByType('navigation');
                                if (navEntries.length > 0) {
                                    var navEntry = navEntries[0];
                                    hasActiveRequests = navEntry.loadEventEnd === 0;
                                }
                            }
                            
                            return {
                                network: networkInfo,
                                loading: loadingInfo,
                                hasActiveRequests: hasActiveRequests
                            };
                        } catch(e) {
                            return {
                                network: {online: true},
                                loading: {readyState: 'complete', loadComplete: true},
                                hasActiveRequests: false
                            };
                        }
                    """)
                    
                    stability_checkpoints['network_stable'] = network_status.get('network', {}).get('online', True)
                    stability_checkpoints['dom_ready'] = network_status.get('loading', {}).get('loadComplete', True)
                    
                    # 3. UI 요소 및 페이지 구조 확인 (극강화)
                    ui_elements_status = self.driver.execute_script("""
                        try {
                            var uiCheck = {
                                hasTable: false,
                                hasCheckboxes: false,
                                hasControls: false,
                                tableRowCount: 0,
                                checkboxCount: 0,
                                interactiveElements: 0
                            };
                            
                            // 테이블 구조 확인
                            var tables = document.querySelectorAll('table[class*="table"], .table-list, table');
                            uiCheck.hasTable = tables.length > 0;
                            
                            if (tables.length > 0) {
                                var rows = tables[0].querySelectorAll('tbody tr, tr');
                                uiCheck.tableRowCount = rows.length;
                            }
                            
                            // 체크박스 확인
                            var checkboxes = document.querySelectorAll('input[type="checkbox"], input.rowCk, input[name="idx[]"]');
                            uiCheck.hasCheckboxes = checkboxes.length > 0;
                            uiCheck.checkboxCount = checkboxes.length;
                            
                            // 페이지 컨트롤 확인
                            var controls = document.querySelectorAll('.pagination, .paging, [class*="page"], button, select');
                            uiCheck.hasControls = controls.length > 0;
                            
                            // 인터랙티브 요소 확인
                            var interactive = document.querySelectorAll('button, input, select, a[href], [onclick], [class*="btn"]');
                            uiCheck.interactiveElements = interactive.length;
                            
                            return uiCheck;
                        } catch(e) {
                            return {hasTable: false, hasCheckboxes: false, hasControls: false};
                        }
                    """)
                    
                    stability_checkpoints['ui_elements_loaded'] = (
                        ui_elements_status.get('hasTable', False) and 
                        ui_elements_status.get('checkboxCount', 0) > 0
                    )
                    
                    # 4. JavaScript 및 이벤트 시스템 확인
                    js_status = self.driver.execute_script("""
                        try {
                            var jsCheck = {
                                jqueryReady: false,
                                eventsWorking: false,
                                ajaxComplete: false,
                                scriptsLoaded: false
                            };
                            
                            // jQuery 상태 확인
                            if (typeof jQuery !== 'undefined') {
                                jsCheck.jqueryReady = jQuery.isReady;
                                
                                // AJAX 완료 상태 확인
                                if (jQuery.active !== undefined) {
                                    jsCheck.ajaxComplete = jQuery.active === 0;
                                } else {
                                    jsCheck.ajaxComplete = true;
                                }
                            } else {
                                jsCheck.jqueryReady = true; // jQuery가 없으면 통과
                                jsCheck.ajaxComplete = true;
                            }
                            
                            // 이벤트 시스템 테스트
                            try {
                                var testEvent = new Event('test');
                                var testElement = document.createElement('div');
                                testElement.addEventListener('test', function() {
                                    jsCheck.eventsWorking = true;
                                });
                                testElement.dispatchEvent(testEvent);
                            } catch(e) {
                                jsCheck.eventsWorking = false;
                            }
                            
                            // 스크립트 로딩 상태
                            var scripts = document.querySelectorAll('script');
                            jsCheck.scriptsLoaded = scripts.length > 0;
                            
                            return jsCheck;
                        } catch(e) {
                            return {jqueryReady: true, eventsWorking: true, ajaxComplete: true, scriptsLoaded: true};
                        }
                    """)
                    
                    stability_checkpoints['javascript_ready'] = (
                        js_status.get('jqueryReady', True) and 
                        js_status.get('ajaxComplete', True)
                    )
                    
                    # 5. 서버 응답성 및 페이지 안정성 확인
                    current_url = self.driver.current_url
                    url_stable = "cafe24.com" in current_url and "manageList" in current_url
                    
                    # 창 상태 확인
                    window_stable = True
                    try:
                        current_window = self.driver.current_window_handle
                        available_windows = self.driver.window_handles
                        window_stable = current_window in available_windows
                    except Exception:
                        window_stable = False
                    
                    stability_checkpoints['server_responsive'] = url_stable and window_stable
                    
                    # 6. 서버 부하 및 네트워크 불안정 감지
                    response_time = browser_response.get('responseTime', 0)
                    performance_good = browser_response.get('performanceGood', True)
                    
                    if not performance_good or response_time > 500:
                        consecutive_failures += 1
                        if consecutive_failures >= 3:
                            server_overload_detected = True
                            logger.warning(f"🚨 서버 과부하 감지됨 (응답시간: {response_time:.1f}ms, 연속실패: {consecutive_failures}회)")
                    else:
                        consecutive_failures = max(0, consecutive_failures - 1)
                    
                    # 네트워크 불안정 감지
                    network_rtt = network_status.get('network', {}).get('rtt', 0)
                    if network_rtt > 1000:  # 1초 이상 RTT
                        network_instability_detected = True
                        logger.warning(f"🌐 네트워크 불안정 감지됨 (RTT: {network_rtt}ms)")
                    
                    # 극심한 부하 감지
                    if consecutive_failures >= 5 or response_time > 2000:
                        extreme_load_detected = True
                        logger.warning(f"⚠️ 극심한 서버 부하 감지됨 (응답시간: {response_time:.1f}ms)")
                    
                    # 7. 안정화 완료 조건 확인
                    stability_score = sum(stability_checkpoints.values())
                    total_checkpoints = len(stability_checkpoints)
                    
                    logger.info(f"🔍 극강화 안정화 상태 (경과: {elapsed_time:.1f}초): "
                              f"체크포인트 {stability_score}/{total_checkpoints} "
                              f"(응답: {stability_checkpoints['basic_response']}, "
                              f"네트워크: {stability_checkpoints['network_stable']}, "
                              f"DOM: {stability_checkpoints['dom_ready']}, "
                              f"UI: {stability_checkpoints['ui_elements_loaded']}, "
                              f"JS: {stability_checkpoints['javascript_ready']}, "
                              f"서버: {stability_checkpoints['server_responsive']}) "
                              f"응답시간: {response_time:.1f}ms")
                    
                    # 8. 안정화 완료 판정 (더 엄격한 기준)
                    if stability_score >= total_checkpoints - 1:  # 최소 5/6 체크포인트 통과
                        logger.info(f"✅ 극강화 배치 완료 안정화 성공 (소요시간: {elapsed_time:.1f}초, 점수: {stability_score}/{total_checkpoints})")
                        
                        # 서버 부하 상황에 따른 추가 대기
                        if extreme_load_detected:
                            logger.info("⏰ 극심한 부하 감지로 인한 추가 안정화 대기 (8초)")
                            time.sleep(8)
                        elif server_overload_detected:
                            logger.info("⏰ 서버 과부하 감지로 인한 추가 안정화 대기 (5초)")
                            time.sleep(5)
                        elif network_instability_detected:
                            logger.info("⏰ 네트워크 불안정으로 인한 추가 안정화 대기 (3초)")
                            time.sleep(3)
                        else:
                            time.sleep(2)  # 기본 최종 안정화
                        return
                    
                    # 9. 적응형 대기 간격 조정
                    if extreme_load_detected:
                        adaptive_interval = min(check_interval * 3, 8)  # 최대 8초
                        logger.info(f"🐌 극심한 부하 - 적응형 대기 간격: {adaptive_interval}초")
                        time.sleep(adaptive_interval)
                    elif server_overload_detected:
                        adaptive_interval = min(check_interval * 2, 6)  # 최대 6초
                        logger.info(f"🐌 서버 과부하 - 적응형 대기 간격: {adaptive_interval}초")
                        time.sleep(adaptive_interval)
                    elif network_instability_detected:
                        adaptive_interval = min(check_interval * 1.5, 5)  # 최대 5초
                        logger.info(f"🐌 네트워크 불안정 - 적응형 대기 간격: {adaptive_interval}초")
                        time.sleep(adaptive_interval)
                    else:
                        time.sleep(check_interval)
                    
                except Exception as e:
                    logger.warning(f"⚠️ 극강화 안정화 상태 확인 중 오류: {e}")
                    consecutive_failures += 1
                    time.sleep(check_interval)
                    continue
            
            # 최대 대기 시간 초과
            elapsed_total = time.time() - start_time
            logger.warning(f"⏰ 극강화 배치 완료 안정화 최대 대기 시간 초과 ({elapsed_total:.1f}초/{max_wait_time}초)")
            
            # 상황별 최종 대기
            if extreme_load_detected:
                logger.warning("🚨 극심한 부하 상황에서 최대 대기 시간 초과 - 최종 안정화 대기 (15초)")
                time.sleep(15)
            elif server_overload_detected:
                logger.warning("🚨 서버 과부하 상황에서 최대 대기 시간 초과 - 최종 안정화 대기 (10초)")
                time.sleep(10)
            elif network_instability_detected:
                logger.warning("🚨 네트워크 불안정 상황에서 최대 대기 시간 초과 - 최종 안정화 대기 (8초)")
                time.sleep(8)
            else:
                time.sleep(5)  # 기본 최종 안정화 대기
            
        except Exception as e:
            logger.error(f"❌ 극강화 배치 완료 안정화 대기 실패: {e}")
            time.sleep(12)  # 폴백 대기 (더 긴 시간)
        """
        배치 작업 후 페이지 안정화를 위한 적응형 대기.
        100개 연동해제 후 서버 응답 시간 편차에 대응합니다.
        30초 이상의 긴 로딩 시간에도 대응합니다.
        """
        try:
            logger.info("배치 후 적응형 안정화 대기 시작 (강화된 버전)")
            max_wait_time = 90  # 최대 90초 대기 (30초 이상 대응 강화)
            check_interval = 2.5  # 2.5초마다 확인 (더 세밀한 모니터링)
            start_time = time.time()
            
            # 초기 기본 대기 (서버 처리 시간 확보)
            logger.info("서버 처리 시간 확보를 위한 초기 대기 (7초)")
            time.sleep(7)
            
            # 서버 부하 상태 감지 변수
            consecutive_failures = 0
            server_load_detected = False
            
            while time.time() - start_time < max_wait_time:
                try:
                    elapsed_time = time.time() - start_time
                    
                    # 1. 페이지 응답성 확인 (강화된 버전)
                    page_responsive = self.driver.execute_script("""
                        try {
                            // 페이지가 응답하는지 확인
                            var testElement = document.createElement('div');
                            testElement.id = 'stability_test_' + Date.now();
                            document.body.appendChild(testElement);
                            var found = document.getElementById(testElement.id);
                            document.body.removeChild(testElement);
                            
                            // DOM 조작이 정상적으로 작동하는지 확인
                            return found !== null;
                        } catch(e) {
                            return false;
                        }
                    """)
                    
                    # 2. 네트워크 상태 및 로딩 상태 확인
                    network_status = self.driver.execute_script("""
                        try {
                            // 네트워크 상태 확인
                            var networkState = navigator.onLine;
                            
                            // 페이지 로딩 상태 확인
                            var loadingState = document.readyState;
                            
                            // 활성 요청 확인 (가능한 경우)
                            var hasActiveRequests = false;
                            if (typeof performance !== 'undefined' && performance.getEntriesByType) {
                                var entries = performance.getEntriesByType('navigation');
                                if (entries.length > 0) {
                                    var navEntry = entries[0];
                                    hasActiveRequests = navEntry.loadEventEnd === 0;
                                }
                            }
                            
                            return {
                                online: networkState,
                                readyState: loadingState,
                                hasActiveRequests: hasActiveRequests
                            };
                        } catch(e) {
                            return {online: true, readyState: 'complete', hasActiveRequests: false};
                        }
                    """)
                    
                    # 3. URL 안정성 및 페이지 구조 확인
                    current_url = self.driver.current_url
                    url_stable = "cafe24.com" in current_url and "manageList" in current_url
                    
                    # 4. 페이지 내 핵심 요소 로딩 확인
                    essential_elements_loaded = self.driver.execute_script("""
                        try {
                            // 상품 목록 테이블 확인
                            var hasTable = document.querySelector('table[class*="table"], .table-list') !== null;
                            
                            // 페이지네이션 또는 페이지 컨트롤 확인
                            var hasPageControl = document.querySelector('.pagination, .paging, [class*="page"]') !== null;
                            
                            // 기본 UI 요소 확인
                            var hasBasicUI = document.querySelector('body') !== null && 
                                            document.querySelector('head') !== null;
                            
                            return hasTable && hasBasicUI;
                        } catch(e) {
                            return false;
                        }
                    """)
                    
                    # 5. 서버 부하 감지
                    if not page_responsive or not network_status.get('online', True):
                        consecutive_failures += 1
                        if consecutive_failures >= 3:
                            server_load_detected = True
                            logger.warning(f"서버 부하 감지됨 (연속 실패: {consecutive_failures}회)")
                    else:
                        consecutive_failures = 0
                    
                    # 6. 안정화 완료 조건 확인
                    stability_conditions = [
                        page_responsive,
                        network_status.get('readyState') == 'complete',
                        not network_status.get('hasActiveRequests', True),
                        url_stable,
                        essential_elements_loaded
                    ]
                    
                    stability_score = sum(stability_conditions)
                    total_conditions = len(stability_conditions)
                    
                    logger.info(f"배치 후 안정화 상태 (경과: {elapsed_time:.1f}초): "
                              f"안정성 점수 {stability_score}/{total_conditions} "
                              f"(응답성: {page_responsive}, 네트워크: {network_status.get('online')}, "
                              f"로딩완료: {network_status.get('readyState')}, URL안정: {url_stable}, "
                              f"핵심요소: {essential_elements_loaded})")
                    
                    # 7. 안정화 완료 판정
                    if stability_score >= total_conditions - 1:  # 최소 4/5 조건 만족
                        logger.info(f"배치 후 안정화 완료 (소요시간: {elapsed_time:.1f}초, 점수: {stability_score}/{total_conditions})")
                        
                        # 서버 부하가 감지된 경우 추가 대기
                        if server_load_detected:
                            logger.info("서버 부하 감지로 인한 추가 안정화 대기 (5초)")
                            time.sleep(5)
                        else:
                            time.sleep(2)  # 기본 최종 안정화
                        return
                    
                    # 8. 서버 부하 상황에서의 적응형 대기
                    if server_load_detected:
                        adaptive_interval = min(check_interval * 2, 5)  # 최대 5초
                        logger.info(f"서버 부하 상황 - 적응형 대기 간격: {adaptive_interval}초")
                        time.sleep(adaptive_interval)
                    else:
                        time.sleep(check_interval)
                    
                except Exception as e:
                    logger.warning(f"배치 후 상태 확인 중 오류: {e}")
                    consecutive_failures += 1
                    time.sleep(check_interval)
                    continue
            
            # 최대 대기 시간 초과
            elapsed_total = time.time() - start_time
            logger.warning(f"배치 후 안정화 최대 대기 시간 초과 ({elapsed_total:.1f}초/{max_wait_time}초)")
            
            # 서버 부하가 심한 경우 추가 대기
            if server_load_detected:
                logger.warning("서버 부하 상황에서 최대 대기 시간 초과 - 추가 안정화 대기 (10초)")
                time.sleep(10)
            else:
                time.sleep(3)  # 기본 안정화 대기
            
        except Exception as e:
            logger.error(f"배치 후 적응형 안정화 대기 실패: {e}")
            time.sleep(8)  # 폴백 대기 (증가)

    def _enhanced_inter_page_stabilization_wait(self):
        """
        페이지 간 이동 시 극강화된 안정화 대기.
        페이지 이동 후 로딩 시간 편차에 강력하게 대응합니다.
        """
        try:
            logger.info("🔄 극강화 페이지 간 이동 안정화 대기 시작 (최대 60초)")
            max_wait_time = 60  # 최대 60초 대기
            check_interval = 2.5  # 2.5초마다 확인
            start_time = time.time()
            
            # 초기 페이지 이동 처리 시간 확보
            logger.info("⏳ 페이지 이동 처리 대기 (초기 5초)")
            time.sleep(5)
            
            # 안정화 상태 추적
            consecutive_failures = 0
            page_load_issues = False
            
            while time.time() - start_time < max_wait_time:
                try:
                    elapsed_time = time.time() - start_time
                    
                    # 1. 브라우저 기본 응답성 확인
                    browser_responsive = self.driver.execute_script("""
                        try {
                            var testStart = performance.now();
                            var testElement = document.createElement('span');
                            testElement.textContent = 'test';
                            document.body.appendChild(testElement);
                            document.body.removeChild(testElement);
                            var testEnd = performance.now();
                            return {
                                responsive: true,
                                responseTime: testEnd - testStart,
                                performanceGood: (testEnd - testStart) < 50
                            };
                        } catch(e) {
                            return {responsive: false, responseTime: 9999, performanceGood: false};
                        }
                    """)
                    
                    # 2. 페이지 로딩 및 네트워크 상태 확인
                    page_status = self.driver.execute_script("""
                        try {
                            var status = {
                                readyState: document.readyState,
                                loadComplete: document.readyState === 'complete',
                                visibilityState: document.visibilityState,
                                hasActiveRequests: false
                            };
                            
                            // 활성 네트워크 요청 확인
                            if (typeof performance !== 'undefined' && performance.getEntriesByType) {
                                var navEntries = performance.getEntriesByType('navigation');
                                if (navEntries.length > 0) {
                                    var navEntry = navEntries[0];
                                    status.hasActiveRequests = navEntry.loadEventEnd === 0;
                                }
                            }
                            
                            // jQuery AJAX 상태 확인
                            if (typeof jQuery !== 'undefined' && jQuery.active !== undefined) {
                                status.hasActiveAjax = jQuery.active > 0;
                            } else {
                                status.hasActiveAjax = false;
                            }
                            
                            return status;
                        } catch(e) {
                            return {readyState: 'complete', loadComplete: true, hasActiveRequests: false, hasActiveAjax: false};
                        }
                    """)
                    
                    # 3. URL 안정성 확인
                    current_url = self.driver.current_url
                    url_stable = "cafe24.com" in current_url and "manageList" in current_url
                    
                    # 4. 창 상태 확인
                    window_stable = True
                    try:
                        current_window = self.driver.current_window_handle
                        available_windows = self.driver.window_handles
                        window_stable = current_window in available_windows
                    except Exception:
                        window_stable = False
                    
                    # 5. 페이지 핵심 요소 확인
                    essential_elements = self.driver.execute_script("""
                        try {
                            var elements = {
                                hasTable: document.querySelectorAll('table').length > 0,
                                hasCheckboxes: document.querySelectorAll('input[type="checkbox"]').length > 0,
                                hasNavigation: document.querySelectorAll('.pagination, .paging, [class*="page"]').length > 0,
                                hasControls: document.querySelectorAll('button, select').length > 0
                            };
                            
                            elements.essentialCount = Object.values(elements).filter(Boolean).length;
                            return elements;
                        } catch(e) {
                            return {hasTable: false, hasCheckboxes: false, hasNavigation: false, hasControls: false, essentialCount: 0};
                        }
                    """)
                    
                    # 안정화 조건 평가
                    conditions = {
                        'browser_responsive': browser_responsive.get('responsive', False),
                        'page_loaded': page_status.get('loadComplete', False),
                        'no_active_requests': not page_status.get('hasActiveRequests', True),
                        'no_active_ajax': not page_status.get('hasActiveAjax', True),
                        'url_stable': url_stable,
                        'window_stable': window_stable,
                        'essential_elements': essential_elements.get('essentialCount', 0) >= 2
                    }
                    
                    # 성능 이슈 감지
                    response_time = browser_responsive.get('responseTime', 0)
                    performance_good = browser_responsive.get('performanceGood', True)
                    
                    if not performance_good or response_time > 200:
                        consecutive_failures += 1
                        if consecutive_failures >= 3:
                            page_load_issues = True
                            logger.warning(f"🚨 페이지 로딩 성능 이슈 감지 (응답시간: {response_time:.1f}ms, 연속실패: {consecutive_failures}회)")
                    else:
                        consecutive_failures = max(0, consecutive_failures - 1)
                    
                    # 안정화 점수 계산
                    stability_score = sum(conditions.values())
                    total_conditions = len(conditions)
                    
                    logger.info(f"🔍 극강화 페이지 간 안정화 상태 (경과: {elapsed_time:.1f}초): "
                              f"조건 {stability_score}/{total_conditions} "
                              f"(브라우저: {conditions['browser_responsive']}, "
                              f"로딩: {conditions['page_loaded']}, "
                              f"요청: {conditions['no_active_requests']}, "
                              f"AJAX: {conditions['no_active_ajax']}, "
                              f"URL: {conditions['url_stable']}, "
                              f"창: {conditions['window_stable']}, "
                              f"요소: {conditions['essential_elements']}) "
                              f"응답시간: {response_time:.1f}ms")
                    
                    # 안정화 완료 판정
                    if stability_score >= total_conditions - 1:  # 최소 6/7 조건 만족
                        logger.info(f"✅ 극강화 페이지 간 이동 안정화 성공 (소요시간: {elapsed_time:.1f}초, 점수: {stability_score}/{total_conditions})")
                        
                        # 성능 이슈가 있었다면 추가 대기
                        if page_load_issues:
                            logger.info("⏰ 페이지 로딩 성능 이슈로 인한 추가 안정화 대기 (4초)")
                            time.sleep(4)
                        else:
                            time.sleep(1.5)  # 기본 최종 안정화
                        return
                    
                    # 적응형 대기 간격
                    if page_load_issues:
                        adaptive_interval = min(check_interval * 2, 5)  # 최대 5초
                        logger.info(f"🐌 페이지 로딩 이슈 - 적응형 대기 간격: {adaptive_interval}초")
                        time.sleep(adaptive_interval)
                    else:
                        time.sleep(check_interval)
                    
                except Exception as e:
                    logger.warning(f"⚠️ 극강화 페이지 간 안정화 상태 확인 중 오류: {e}")
                    consecutive_failures += 1
                    time.sleep(check_interval)
                    continue
            
            # 최대 대기 시간 초과
            elapsed_total = time.time() - start_time
            logger.warning(f"⏰ 극강화 페이지 간 이동 안정화 최대 대기 시간 초과 ({elapsed_total:.1f}초/{max_wait_time}초)")
            
            # 상황별 최종 대기
            if page_load_issues:
                logger.warning("🚨 페이지 로딩 이슈 상황에서 최대 대기 시간 초과 - 최종 안정화 대기 (8초)")
                time.sleep(8)
            else:
                time.sleep(4)  # 기본 최종 안정화 대기
            
        except Exception as e:
            logger.error(f"❌ 극강화 페이지 간 이동 안정화 대기 실패: {e}")
            time.sleep(6)  # 폴백 대기

    def _adaptive_inter_page_stabilization_wait(self):
        """
        페이지 간 이동 시 적응형 안정화 대기.
        이전 배치 작업의 서버 처리 완료를 기다립니다.
        """
        try:
            logger.info("페이지 간 이동 적응형 안정화 대기 시작")
            max_wait_time = 40  # 최대 40초 대기
            check_interval = 2.5  # 2.5초마다 확인
            start_time = time.time()
            
            # 초기 기본 대기 (서버 처리 시간 확보)
            time.sleep(3)
            
            while time.time() - start_time < max_wait_time:
                try:
                    # 브라우저 응답성 확인
                    browser_responsive = self.driver.execute_script("""
                        try {
                            return document.readyState === 'complete';
                        } catch(e) {
                            return false;
                        }
                    """)
                    
                    # 현재 URL 안정성 확인
                    current_url = self.driver.current_url
                    url_stable = "cafe24.com" in current_url
                    
                    # 창 상태 확인
                    window_stable = True
                    try:
                        current_window = self.driver.current_window_handle
                        available_windows = self.driver.window_handles
                        window_stable = current_window in available_windows
                    except Exception:
                        window_stable = False
                    
                    elapsed_time = time.time() - start_time
                    
                    if browser_responsive and url_stable and window_stable:
                        logger.info(f"페이지 간 이동 안정화 완료 (소요시간: {elapsed_time:.1f}초)")
                        time.sleep(1.5)  # 최종 안정화
                        return
                    
                    logger.info(f"페이지 간 이동 안정화 대기 중... (경과: {elapsed_time:.1f}초, 브라우저: {browser_responsive}, URL: {url_stable}, 창: {window_stable})")
                    time.sleep(check_interval)
                    
                except Exception as e:
                    logger.warning(f"페이지 간 이동 상태 확인 중 오류: {e}")
                    time.sleep(check_interval)
                    continue
            
            # 최대 대기 시간 초과
            logger.warning(f"페이지 간 이동 안정화 최대 대기 시간 초과 ({max_wait_time}초)")
            time.sleep(2)  # 기본 안정화 대기
            
        except Exception as e:
            logger.error(f"페이지 간 이동 적응형 안정화 대기 실패: {e}")
            time.sleep(5)  # 폴백 대기

    def _ensure_valid_window(self):
        """
        현재 창 상태를 확인하고 필요시 복구합니다.
        작업 창을 우선적으로 선택하여 일관성을 유지합니다.
        
        Returns:
            bool: 창 상태 복구 성공 여부
        """
        try:
            # 현재 창 핸들 확인 시도
            current_handle = self.driver.current_window_handle
            logger.info(f"현재 창 핸들 확인 성공: {current_handle}")
            
            # 창이 유효한지 확인 (간단한 작업 수행)
            self.driver.execute_script("return document.readyState;")
            logger.info("창 상태 정상 확인")
            return True
            
        except Exception as e:
            logger.warning(f"창 상태 확인 실패: {e}")
            
            # 사용 가능한 창 핸들 목록 확인
            try:
                available_handles = self.driver.window_handles
                logger.info(f"사용 가능한 창 핸들: {len(available_handles)}개")
                
                if available_handles:
                    # 작업 창 우선 선택 로직
                    target_window = None
                    
                    # 1. 두 번째 창이 있으면 작업 창으로 간주 (첫 번째는 보통 메인 탭)
                    if len(available_handles) > 1:
                        target_window = available_handles[1]
                        logger.info(f"작업 창으로 추정되는 두 번째 창 선택: {target_window}")
                    else:
                        # 2. 창이 하나뿐이면 그것을 사용
                        target_window = available_handles[0]
                        logger.info(f"유일한 창 선택: {target_window}")
                    
                    # 선택된 창으로 전환
                    self.driver.switch_to.window(target_window)
                    logger.info(f"창 전환 완료: {target_window}")
                    
                    # 전환된 창이 유효한지 확인
                    self.driver.execute_script("return document.readyState;")
                    
                    # 전환된 창이 카페24 관련 페이지인지 확인
                    current_url = self.driver.current_url
                    if "cafe24.com" in current_url:
                        logger.info(f"카페24 관련 페이지 확인: {current_url}")
                        logger.info("창 복구 성공")
                        return True
                    else:
                        logger.warning(f"카페24 관련 페이지가 아님: {current_url}")
                        # 다른 창들도 확인해보기
                        for handle in available_handles:
                            if handle != target_window:
                                try:
                                    self.driver.switch_to.window(handle)
                                    check_url = self.driver.current_url
                                    if "cafe24.com" in check_url:
                                        logger.info(f"카페24 관련 창 발견: {handle}, URL: {check_url}")
                                        logger.info("창 복구 성공")
                                        return True
                                except Exception as check_e:
                                    logger.warning(f"창 {handle} 확인 실패: {check_e}")
                                    continue
                        
                        # 카페24 관련 창을 찾지 못한 경우에도 복구 성공으로 처리
                        logger.warning("카페24 관련 창을 찾지 못했지만 창 복구는 성공")
                        return True
                        
                else:
                    logger.error("사용 가능한 창이 없음")
                    return False
                    
            except Exception as recovery_error:
                logger.error(f"창 복구 실패: {recovery_error}")
                return False