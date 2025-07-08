import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains

try:
    import pyperclip
except ImportError:
    pyperclip = None

logger = logging.getLogger(__name__)

class CoupangMarketManager:
    """
    쿠팡 마켓 전용 관리 클래스
    쿠팡 로그인, 연동업체 변경, 로그아웃 등의 작업을 담당
    """
    
    def __init__(self, driver, wait=None):
        """
        CoupangMarketManager 초기화
        
        Args:
            driver: Selenium WebDriver 인스턴스
            wait: WebDriverWait 인스턴스 (선택사항)
        """
        self.driver = driver
        self.wait = wait if wait else WebDriverWait(driver, 10)
        self.coupang_tab = None
    
    def change_api_integrator_to_percenty(self, market_config):
        """
        쿠팡 API 연동업체를 '퍼센티'로 변경합니다.
        
        Args:
            market_config: 마켓 설정 정보 (coupang_id, coupang_password 포함)
            
        Returns:
            bool: 성공 여부
        """
        max_attempts = 3
        
        for attempt in range(max_attempts):
            try:
                logger.info(f"쿠팡 API 연동업체를 '퍼센티'로 변경 시작 (시도 {attempt + 1}/{max_attempts})")
                
                # 1. 쿠팡 로그인
                if not self._login_coupang(market_config):
                    logger.error(f"쿠팡 로그인 실패 (시도 {attempt + 1}/{max_attempts})")
                    if attempt < max_attempts - 1:
                        time.sleep(2)
                        continue
                    return False
                
                # 2. 추가판매정보 페이지로 이동 및 로그인
                if not self._login_additional_sales_info(market_config):
                    logger.error(f"추가판매정보 로그인 실패 (시도 {attempt + 1}/{max_attempts})")
                    if attempt < max_attempts - 1:
                        time.sleep(2)
                        continue
                    return False
                
                # 3. 연동업체를 '퍼센티'로 변경 (재시도 로직 포함)
                if not self._change_integrator("퍼센티"):
                    logger.error(f"연동업체 변경 실패 (시도 {attempt + 1}/{max_attempts})")
                    if attempt < max_attempts - 1:
                        logger.info("[수정] 버튼부터 다시 시작합니다...")
                        time.sleep(3)  # 재시도 전 대기
                        continue
                    return False
                
                logger.info(f"쿠팡 API 연동업체를 '퍼센티'로 변경 완료 (시도 {attempt + 1}/{max_attempts})")
                
                # 로그아웃 없이 탭만 닫고 메인탭으로 돌아가기
                try:
                    self.driver.close()
                    if len(self.driver.window_handles) > 0:
                        self.driver.switch_to.window(self.driver.window_handles[0])
                    logger.info("퍼센티 변경 완료 - 로그아웃 없이 메인탭으로 복귀")
                except Exception as close_error:
                    logger.error(f"탭 닫기 실패: {close_error}")
                
                return True
                
            except Exception as e:
                logger.error(f"쿠팡 API 연동업체 '퍼센티' 변경 중 오류 발생 (시도 {attempt + 1}/{max_attempts}): {str(e)}")
                if attempt < max_attempts - 1:
                    time.sleep(3)
                    continue
                return False
            finally:
                # 재시도 로직에서 탭 정리는 성공 시에만 수행하므로 finally에서는 제거
                pass
        
        return False
    
    def change_api_integrator_to_nextengine(self, market_config):
        """
        쿠팡 API 연동업체를 '넥스트엔진'으로 변경합니다.
        (퍼센티 변경 후 이미 로그인된 상태에서 진행)
        
        Args:
            market_config: 마켓 설정 정보 (coupang_id, coupang_password 포함)
            
        Returns:
            bool: 성공 여부
        """
        max_attempts = 3
        
        for attempt in range(max_attempts):
            try:
                logger.info(f"쿠팡 API 연동업체를 '넥스트엔진'으로 변경 시작 (시도 {attempt + 1}/{max_attempts})")
                
                # 새 탭 열기
                self.driver.execute_script("window.open('', '_blank');")
                self.driver.switch_to.window(self.driver.window_handles[-1])
                
                # 1. 추가판매정보 페이지로 이동 및 로그인 (이미 로그인된 상태에서 진행)
                if not self._login_additional_sales_info(market_config):
                    logger.error(f"추가판매정보 로그인 실패 (시도 {attempt + 1}/{max_attempts})")
                    if attempt < max_attempts - 1:
                        time.sleep(2)
                        continue
                    return False
                
                # 2. 연동업체를 '넥스트엔진'으로 변경 (재시도 로직 포함)
                if not self._change_integrator("넥스트엔진"):
                    logger.error(f"연동업체 변경 실패 (시도 {attempt + 1}/{max_attempts})")
                    if attempt < max_attempts - 1:
                        logger.info("[수정] 버튼부터 다시 시작합니다...")
                        time.sleep(3)  # 재시도 전 대기
                        continue
                    return False
                
                logger.info(f"쿠팡 API 연동업체를 '넥스트엔진'으로 변경 완료 (시도 {attempt + 1}/{max_attempts})")
                
                # 3. 로그아웃 및 탭 정리
                try:
                    # 로그아웃 시도
                    if not self.logout_coupang():
                        logger.warning("쿠팡 로그아웃 실패, 탭만 닫고 진행")
                        # 로그아웃 실패 시에도 탭은 닫기
                        try:
                            self.driver.close()
                            if len(self.driver.window_handles) > 0:
                                self.driver.switch_to.window(self.driver.window_handles[0])
                            logger.info("로그아웃 실패했지만 탭 닫기 완료")
                        except Exception as close_error:
                            logger.error(f"탭 닫기 실패: {close_error}")
                    else:
                        # 로그아웃 성공 시 탭 닫기 및 메인 탭으로 복귀
                        try:
                            self.driver.close()
                            if len(self.driver.window_handles) > 0:
                                self.driver.switch_to.window(self.driver.window_handles[0])
                            logger.info("로그아웃 및 탭 정리 완료")
                        except Exception as close_error:
                            logger.error(f"로그아웃 후 탭 닫기 실패: {close_error}")
                except Exception as logout_error:
                    logger.error(f"로그아웃 및 탭 정리 중 오류: {logout_error}")
                    # 오류 발생 시에도 탭 닫기 시도
                    try:
                        self.driver.close()
                        if len(self.driver.window_handles) > 0:
                            self.driver.switch_to.window(self.driver.window_handles[0])
                        logger.info("오류 발생했지만 탭 닫기 완료")
                    except Exception as close_error:
                        logger.error(f"오류 후 탭 닫기 실패: {close_error}")
                
                return True
                
            except Exception as e:
                logger.error(f"쿠팡 API 연동업체 '넥스트엔진' 변경 중 오류 발생 (시도 {attempt + 1}/{max_attempts}): {str(e)}")
                if attempt < max_attempts - 1:
                    time.sleep(3)
                    continue
                return False
            finally:
                # 재시도 로직에서 탭 정리는 성공 시에만 수행하므로 finally에서는 제거
                pass
        
        return False
    
    def logout_coupang(self):
        """
        쿠팡에서 로그아웃합니다.
        최대 10회까지 반복 시도하여 성공률을 높입니다.
        
        Returns:
            bool: 성공 여부
        """
        max_attempts = 10
        
        # 먼저 현재 상태 확인 - 이미 로그아웃된 상태인지 체크
        try:
            current_url = self.driver.current_url
            if "xauth.coupang.com" in current_url or "login" in current_url.lower():
                logger.info(f"이미 로그아웃된 상태입니다 - 현재 URL: {current_url}")
                # 탭 닫기는 호출자가 처리하도록 수정
                return True
        except Exception as e:
            logger.debug(f"현재 URL 확인 중 오류: {e}")
        
        for attempt in range(max_attempts):
            try:
                logger.info(f"쿠팡 로그아웃 시작 (시도 {attempt + 1}/{max_attempts})")
                
                # 1. 사용자 메뉴 클릭
                if not self._click_user_menu():
                    logger.warning(f"사용자 메뉴 클릭 실패 (시도 {attempt + 1}/{max_attempts})")
                    if attempt < max_attempts - 1:
                        time.sleep(2)  # 재시도 전 대기
                        continue
                    else:
                        logger.error("사용자 메뉴 클릭 최종 실패")
                        return False
                
                # 2. 로그아웃 버튼 클릭 및 로그아웃 성공 확인
                if not self._click_logout_button_with_verification():
                    logger.warning(f"로그아웃 버튼 클릭 또는 로그아웃 확인 실패 (시도 {attempt + 1}/{max_attempts})")
                    if attempt < max_attempts - 1:
                        time.sleep(2)  # 재시도 전 대기
                        # 페이지 새로고침 후 재시도
                        try:
                            self.driver.refresh()
                            time.sleep(3)
                        except Exception as refresh_error:
                            logger.debug(f"페이지 새로고침 실패: {refresh_error}")
                        continue
                    else:
                        logger.error("로그아웃 최종 실패")
                        return False
                
                logger.info(f"쿠팡 로그아웃 성공 (시도 {attempt + 1}/{max_attempts})")
                # 로그아웃 성공 후 탭 닫기는 호출자가 처리하도록 수정
                # 탭 닫기를 여기서 하면 중복 닫기가 발생할 수 있음
                return True
                
            except Exception as e:
                logger.warning(f"쿠팡 로그아웃 중 오류 발생 (시도 {attempt + 1}/{max_attempts}): {str(e)}")
                if attempt < max_attempts - 1:
                    time.sleep(2)  # 재시도 전 대기
                    continue
                else:
                    logger.error(f"쿠팡 로그아웃 최종 실패: {str(e)}")
                    return False
        
        return False
    
    def _login_coupang(self, market_config):
        """
        쿠팡에 로그인합니다.
        이미 로그인된 상태인 경우 먼저 로그아웃을 시도합니다.
        
        Args:
            market_config: 마켓 설정 정보
            
        Returns:
            bool: 성공 여부
        """
        try:
            # 브라우저 세션 상태 확인
            try:
                self.driver.current_url
            except WebDriverException as e:
                logger.error(f"브라우저 세션이 유효하지 않습니다: {str(e)}")
                return False
            
            # 새 탭 열기
            self.driver.execute_script("window.open('');")
            self.coupang_tab = self.driver.window_handles[-1]
            self.driver.switch_to.window(self.coupang_tab)
            
            # 쿠팡 로그인 페이지로 이동
            self.driver.get("https://wing.coupang.com")
            time.sleep(3)
            
            # 로그인 상태 확인 및 처리
            max_login_attempts = 2
            for attempt in range(max_login_attempts):
                try:
                    # 아이디 입력창이 있는지 확인
                    username_input = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.ID, "username"))
                    )
                    
                    # 로그인 폼이 있는 경우 정상 로그인 진행
                    logger.info(f"로그인 폼 발견, 로그인 진행 (시도 {attempt + 1}/{max_login_attempts})")
                    
                    username_input.clear()
                    username_input.send_keys(market_config.get('coupang_id', ''))
                    time.sleep(1)
                    
                    # 비밀번호 입력
                    password_input = self.driver.find_element(By.ID, "password")
                    password_input.clear()
                    password_input.send_keys(market_config.get('coupang_password', ''))
                    time.sleep(1)
                    
                    # 로그인 버튼 클릭
                    login_button = self.driver.find_element(By.ID, "kc-login")
                    login_button.click()
                    time.sleep(5)
                    
                    logger.info("쿠팡 로그인 완료")
                    return True
                    
                except TimeoutException:
                    # 로그인 폼이 없는 경우 (이미 로그인된 상태)
                    logger.info(f"로그인 폼이 없음 - 이미 로그인된 상태로 판단 (시도 {attempt + 1}/{max_login_attempts})")
                    
                    if attempt == 0:
                        # 첫 번째 시도에서 로그인 폼이 없으면 로그아웃 시도
                        logger.info("기존 로그인 세션 감지, 로그아웃 후 재로그인 시도")
                        
                        # 현재 URL 확인
                        current_url = self.driver.current_url
                        logger.info(f"현재 URL: {current_url}")
                        
                        # 이미 메인 페이지에 있는 경우 로그아웃 시도
                        if "wing.coupang.com" in current_url and "login" not in current_url.lower():
                            try:
                                # 로그아웃 시도
                                if self._click_user_menu():
                                    if self._click_logout_button_with_verification():
                                        logger.info("기존 세션 로그아웃 성공")
                                        time.sleep(2)
                                        # 로그인 페이지로 다시 이동
                                        self.driver.get("https://wing.coupang.com")
                                        time.sleep(3)
                                        continue  # 다시 로그인 시도
                                    else:
                                        logger.warning("로그아웃 실패, 강제로 로그인 페이지 이동")
                                else:
                                    logger.warning("사용자 메뉴 클릭 실패, 강제로 로그인 페이지 이동")
                            except Exception as logout_error:
                                logger.warning(f"로그아웃 시도 중 오류: {logout_error}")
                        
                        # 로그아웃이 실패하거나 다른 상황인 경우 강제로 로그인 페이지 이동
                        logger.info("강제로 로그인 페이지 이동")
                        self.driver.get("https://wing.coupang.com/auth/login")
                        time.sleep(3)
                        continue  # 다시 로그인 시도
                    else:
                        # 두 번째 시도에서도 로그인 폼이 없으면 이미 로그인된 것으로 간주
                        logger.info("로그인 폼이 여전히 없음 - 이미 로그인된 상태로 간주")
                        return True
                        
                except Exception as login_error:
                    logger.error(f"로그인 시도 {attempt + 1} 중 오류: {login_error}")
                    if attempt == max_login_attempts - 1:
                        raise login_error
                    time.sleep(2)
            
            logger.error("최대 로그인 시도 횟수 초과")
            return False
            
        except Exception as e:
            logger.error(f"쿠팡 로그인 중 오류 발생: {str(e)}")
            return False
    
    def _login_additional_sales_info(self, market_config):
        """
        추가판매정보 페이지로 이동하여 비밀번호를 입력합니다.
        
        Args:
            market_config: 마켓 설정 정보
            
        Returns:
            bool: 성공 여부
        """
        try:
            # 추가판매정보 URL로 이동
            additional_sales_url = "https://wing.coupang.com/tenants/wing-account/vendor/confirm-password?to=/tenants/wing-account/vendor/salesinfo&isTARegion=false"
            self.driver.get(additional_sales_url)
            time.sleep(3)
            
            # 비밀번호 입력
            password_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "password"))
            )
            password_input.clear()
            password_input.send_keys(market_config.get('coupang_password', ''))
            time.sleep(1)
            
            # 확인 버튼 클릭
            confirm_button = self.driver.find_element(By.ID, "confirm-btn")
            confirm_button.click()
            time.sleep(5)
            
            logger.info("추가판매정보 로그인 완료")
            return True
            
        except Exception as e:
            logger.error(f"추가판매정보 로그인 중 오류 발생: {str(e)}")
            return False
    
    def _change_integrator(self, integrator_name):
        """
        연동업체를 변경합니다.
        
        Args:
            integrator_name: 변경할 연동업체명 ('퍼센티' 또는 '넥스트엔진')
            
        Returns:
            bool: 성공 여부
        """
        try:
            # 페이지 하단으로 스크롤
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # 연동 정보 수정 버튼 클릭
            update_button = self.wait.until(
                EC.element_to_be_clickable((By.ID, "updateIntegratorBtn"))
            )
            update_button.click()
            logger.info("연동 정보 수정 버튼 클릭 완료")
            
            # 모달창이 열린 후 DOM 구조 분석 및 입력창 감지
            try:
                # 잠시 대기 후 DOM 구조 분석
                time.sleep(2)
                
                # 실제 표시되는 모달창 찾기
                modal_container = None
                modal_selectors = [
                     ".go-to-market-modal:not(.layout-wuic-hide)",
                     "[class*='modal']:not([class*='hide']):not([style*='display: none'])",
                     "[class*='dialog']:not([class*='hide']):not([style*='display: none'])",
                     "[role='dialog']",
                     ".layout-wuic-modal:not(.layout-wuic-hide)"
                 ]
                 
                for selector in modal_selectors:
                    try:
                        modals = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for modal in modals:
                            if modal.is_displayed():
                                modal_container = modal
                                logger.info(f"표시되는 모달창 발견: {selector}")
                                break
                        if modal_container:
                             break
                    except Exception as e:
                         logger.warning(f"모달창 선택자 '{selector}' 시도 실패: {e}")
                 
                if not modal_container:
                    # 모달창을 찾지 못한 경우 전체 페이지에서 검색 (로그 레벨을 debug로 변경)
                    logger.debug("표시되는 모달창을 찾을 수 없음, 전체 페이지에서 검색")
                    modal_container = self.driver
                else:
                    logger.info(f"모달창 컨테이너 클래스: {modal_container.get_attribute('class')}")
                 
                # 모달창 내부에서 입력창 찾기
                integrator_input = None
                 
                # 방법 1: 모달창 내부에서 ID로 찾기
                try:
                    integrator_input = modal_container.find_element(By.ID, "integrator")
                    if integrator_input.is_displayed():
                        logger.info("모달창 내부에서 ID 'integrator'로 입력창 발견")
                    else:
                        integrator_input = None
                        logger.debug("ID 'integrator' 입력창이 보이지 않음")
                except Exception as e:
                    logger.warning(f"모달창 내부 ID 검색 실패: {e}")
                 
                # 방법 2: 모달창 내부에서 다양한 선택자로 찾기
                if not integrator_input:
                    selectors = [
                        "input[placeholder*='업체']",
                        "input[class*='autocomplete']",
                        "input[type='text']:not([readonly]):not([disabled])"
                    ]
                     
                    for selector in selectors:
                        try:
                            inputs = modal_container.find_elements(By.CSS_SELECTOR, selector)
                            for inp in inputs:
                                if inp.is_displayed():
                                    integrator_input = inp
                                    logger.info(f"모달창 내부에서 선택자 '{selector}'로 입력창 발견")
                                    break
                            if integrator_input:
                                break
                        except Exception as e:
                            logger.warning(f"모달창 내부 선택자 '{selector}' 시도 실패: {e}")
                 
                if not integrator_input:
                    logger.error("모달창 내부에서 입력창을 찾을 수 없습니다")
                    return False
                        
            except Exception as e:
                logger.error(f"DOM 분석 중 오류 발생: {e}")
                return False
            
            # 입력창이 정상적으로 찾아졌는지 확인
            if integrator_input is None:
                logger.error("입력창을 찾을 수 없습니다")
                return False
            
            # 입력창 정보 출력
            try:
                inp_id = integrator_input.get_attribute("id") or "없음"
                inp_class = integrator_input.get_attribute("class") or "없음"
                inp_placeholder = integrator_input.get_attribute("placeholder") or "없음"
                logger.info(f"선택된 입력창 정보: id='{inp_id}', class='{inp_class}', placeholder='{inp_placeholder}'")
            except Exception as e:
                logger.warning(f"입력창 정보 출력 실패: {e}")
            
            # 입력창 클릭 및 포커스 설정 (DOM 기반 정확한 방법만 사용)
            focus_success = False
            
            # 방법 1: 절대 좌표를 이용한 클릭
            try:
                # 요소의 위치와 크기 정보 가져오기
                location = integrator_input.location
                size = integrator_input.size
                
                # 요소의 중앙 좌표 계산
                center_x = location['x'] + size['width'] // 2
                center_y = location['y'] + size['height'] // 2
                
                logger.info(f"입력창 위치: x={location['x']}, y={location['y']}, 크기: w={size['width']}, h={size['height']}")
                logger.info(f"클릭할 중앙 좌표: x={center_x}, y={center_y}")
                
                # 스크롤하여 요소를 화면에 표시
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", integrator_input)
                time.sleep(0.5)
                
                # 절대 좌표로 클릭
                actions = ActionChains(self.driver)
                actions.move_to_element_with_offset(integrator_input, 0, 0).click().perform()
                time.sleep(0.5)
                
                logger.info("절대 좌표 클릭 성공")
                focus_success = True
            except Exception as e:
                logger.warning(f"절대 좌표 클릭 실패: {e}")
            
            # 방법 2: JavaScript 클릭 및 포커스
            if not focus_success:
                try:
                    self.driver.execute_script("""
                        arguments[0].scrollIntoView({block: 'center'});
                        arguments[0].click();
                        arguments[0].focus();
                    """, integrator_input)
                    time.sleep(0.5)
                    logger.info("JavaScript 클릭 및 포커스 성공")
                    focus_success = True
                except Exception as e:
                    logger.warning(f"JavaScript 클릭 실패: {e}")
            
            if not focus_success:
                logger.error("모든 입력창 포커스 방법 실패")
                return False
            
            # 기존 텍스트 삭제 및 새 텍스트 입력 (DOM 기반 정확한 방법만 사용)
            input_success = False
            
            # 방법 1: JavaScript 직접 값 설정
            try:
                self.driver.execute_script("""
                    var element = arguments[0];
                    var value = arguments[1];
                    
                    // 기존 값 삭제
                    element.value = '';
                    element.focus();
                    
                    // 새 값 설정
                    element.value = value;
                    
                    // 다양한 이벤트 트리거
                    var events = ['input', 'change', 'keyup', 'keydown', 'blur', 'focus'];
                    events.forEach(function(eventType) {
                        var event = new Event(eventType, {bubbles: true});
                        element.dispatchEvent(event);
                    });
                """, integrator_input, integrator_name)
                time.sleep(0.5)
                logger.info(f"JavaScript로 '{integrator_name}' 입력 완료")
                input_success = True
            except Exception as e:
                logger.warning(f"JavaScript 입력 실패: {e}")
            
            # 방법 2: 키보드 입력 (기존 텍스트 삭제 후)
            if not input_success:
                try:
                    # 모든 텍스트 선택 후 삭제
                    integrator_input.send_keys(Keys.CONTROL + "a")
                    time.sleep(0.1)
                    integrator_input.send_keys(Keys.DELETE)
                    time.sleep(0.1)
                    
                    # 새 텍스트 입력
                    integrator_input.send_keys(integrator_name)
                    time.sleep(0.5)
                    logger.info(f"키보드로 '{integrator_name}' 입력 완료")
                    input_success = True
                except Exception as e:
                    logger.warning(f"키보드 입력 실패: {e}")
            
            if not input_success:
                logger.error("모든 텍스트 입력 방법 실패")
                return False
            
            # 입력 완료 후 잠시 대기
            time.sleep(1)
            
            # 입력된 값 확인
            try:
                current_value = integrator_input.get_attribute("value")
                logger.info(f"현재 입력창 값: '{current_value}'")
                if current_value != integrator_name:
                    logger.warning(f"입력값 불일치: 예상='{integrator_name}', 실제='{current_value}'")
            except Exception as e:
                logger.warning(f"입력값 확인 실패: {e}")
            
            time.sleep(3)  # 자동완성 목록이 나타날 시간 대기
            
            # 자동완성 목록에서 해당 업체명 선택 (정확한 텍스트 매칭 강화)
            autocomplete_selected = False
            
            # 정확한 키워드 매핑 설정
            keyword_mapping = {
                '퍼센티': ['퍼센티', '타입비', 'TYPEB'],
                '넥스트엔진': ['넥스트엔진', '하미글로벌', 'NEXT ENGINE']
            }
            
            search_keywords = keyword_mapping.get(integrator_name, [integrator_name])
            logger.info(f"'{integrator_name}' 검색 키워드: {search_keywords}")
            
            # 방법 1: 자동완성 목록에서 정확한 텍스트 매칭으로 찾기
            try:
                # 자동완성 목록 대기
                autocomplete_list = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".ui-autocomplete"))
                )
                logger.info("자동완성 목록 발견")
                
                # 자동완성 목록의 모든 항목 가져오기
                autocomplete_items = self.driver.find_elements(By.CSS_SELECTOR, ".ui-autocomplete li")
                logger.info(f"자동완성 항목 수: {len(autocomplete_items)}")
                
                # 각 항목의 텍스트 로깅
                for i, item in enumerate(autocomplete_items):
                    try:
                        item_text = item.text.strip()
                        logger.info(f"자동완성 항목 {i+1}: '{item_text}'")
                    except Exception as e:
                        logger.warning(f"자동완성 항목 {i+1} 텍스트 읽기 실패: {e}")
                
                # 정확한 키워드로 매칭하여 선택
                target_item = None
                for keyword in search_keywords:
                    for item in autocomplete_items:
                        try:
                            item_text = item.text.strip()
                            # 정확한 매칭 또는 포함 관계 확인
                            if (keyword.lower() in item_text.lower() or 
                                item_text.lower() in keyword.lower()):
                                target_item = item
                                logger.info(f"매칭된 항목 발견: '{item_text}' (키워드: '{keyword}')")
                                break
                        except Exception as e:
                            logger.warning(f"항목 텍스트 확인 실패: {e}")
                    
                    if target_item:
                        break
                
                if target_item and target_item.is_displayed():
                    # JavaScript 클릭으로 안정적 선택
                    self.driver.execute_script("arguments[0].click();", target_item)
                    logger.info(f"자동완성에서 '{target_item.text.strip()}' 선택 완료")
                    autocomplete_selected = True
                else:
                    logger.warning(f"'{integrator_name}' 키워드와 매칭되는 항목을 찾을 수 없음")
                        
            except Exception as e:
                logger.warning(f"자동완성 목록에서 '{integrator_name}' 찾기 실패: {e}")
            
            # 방법 2: 키워드 재입력 후 정확한 선택
            if not autocomplete_selected:
                try:
                    logger.info("키워드 재입력 후 정확한 선택 시도")
                    
                    # 입력창 다시 포커스
                    integrator_input.click()
                    time.sleep(0.5)
                    
                    # 기존 텍스트 삭제
                    integrator_input.send_keys(Keys.CONTROL + "a")
                    integrator_input.send_keys(Keys.DELETE)
                    time.sleep(0.3)
                    
                    # 더 구체적인 키워드로 재입력
                    if integrator_name == '넥스트엔진':
                        search_text = '넥스트엔진'
                    elif integrator_name == '퍼센티':
                        search_text = '퍼센티'
                    else:
                        search_text = integrator_name
                    
                    integrator_input.send_keys(search_text)
                    time.sleep(2)  # 자동완성 목록 업데이트 대기
                    
                    # 다시 자동완성 목록에서 선택 시도
                    autocomplete_items = self.driver.find_elements(By.CSS_SELECTOR, ".ui-autocomplete li")
                    for item in autocomplete_items:
                        try:
                            item_text = item.text.strip()
                            if any(keyword.lower() in item_text.lower() for keyword in search_keywords):
                                self.driver.execute_script("arguments[0].click();", item)
                                logger.info(f"재시도로 '{item_text}' 선택 완료")
                                autocomplete_selected = True
                                break
                        except Exception as e:
                            logger.warning(f"재시도 항목 선택 실패: {e}")
                            
                except Exception as e:
                    logger.warning(f"키워드 재입력 선택 실패: {e}")
            
            if not autocomplete_selected:
                 logger.warning("자동완성 선택 실패 - 전체 프로세스 재시도 필요")
                 return False  # 재시도를 위해 False 반환
            
            # 선택 후 입력창 값 재확인
            try:
                time.sleep(1)
                final_value = integrator_input.get_attribute("value")
                logger.info(f"최종 입력창 값: '{final_value}'")
                
                # 선택된 값이 예상과 다른 경우 경고
                if final_value and not any(keyword.lower() in final_value.lower() for keyword in search_keywords):
                    logger.warning(f"선택된 값이 예상과 다름: '{final_value}' (예상 키워드: {search_keywords})")
                    
            except Exception as e:
                logger.warning(f"최종 값 확인 실패: {e}")
            
            # 자동완성 선택 후 충분한 대기 시간 (UI 업데이트 완료 대기)
            logger.info("자동완성 선택 후 UI 업데이트 대기 중...")
            time.sleep(3)  # 3초 대기로 증가
            
            # 탭키로 포커스 이동하여 UI 상태 안정화 (요소가 상호작용 가능한 경우에만)
            try:
                integrator_input = self.driver.find_element(By.ID, "integrator")
                if integrator_input.is_displayed() and integrator_input.is_enabled():
                    integrator_input.send_keys(Keys.TAB)
                    logger.info("탭키로 포커스 이동 완료")
                    time.sleep(1)  # 포커스 이동 후 추가 대기
                else:
                    logger.debug("입력창이 상호작용 불가능한 상태, 탭키 이동 생략")
            except Exception as e:
                logger.debug(f"탭키 포커스 이동 실패 (정상적인 경우일 수 있음): {e}")
            
            # 확인 버튼 클릭 (DOM 기반 정확한 선택자만 사용)
            confirm_clicked = False
            
            # 방법 1: 기본 ID로 확인 버튼 찾기
            try:
                confirm_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.ID, "hmacIntegratorUpdateSelectPopupConfirmBtn"))
                )
                confirm_button.click()
                logger.info("확인 버튼 클릭 성공 (ID: hmacIntegratorUpdateSelectPopupConfirmBtn)")
                confirm_clicked = True
            except Exception as e:
                logger.warning(f"ID로 확인 버튼 찾기 실패: {e}")
            
            # 방법 2: 모달창 내부에서 submit 버튼 찾기
            if not confirm_clicked:
                try:
                    # 모달창 컨테이너 찾기
                    modal_container = self.driver.find_element(By.CSS_SELECTOR, ".go-to-market-modal")
                    if modal_container.is_displayed():
                        # 모달창 내부에서 submit 버튼 찾기
                        confirm_button = modal_container.find_element(By.CSS_SELECTOR, "button[type='submit']")
                        if confirm_button.is_displayed() and confirm_button.is_enabled():
                            confirm_button.click()
                            logger.info("모달창 내 submit 버튼 클릭 성공")
                            confirm_clicked = True
                except Exception as e:
                    logger.warning(f"모달창 내 submit 버튼 찾기 실패: {e}")
            
            # 방법 3: 텍스트 기반으로 확인 버튼 찾기
            if not confirm_clicked:
                try:
                    confirm_button = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '확인')]"))
                    )
                    confirm_button.click()
                    logger.info("텍스트 기반 확인 버튼 클릭 성공")
                    confirm_clicked = True
                except Exception as e:
                    logger.warning(f"텍스트 기반 확인 버튼 찾기 실패: {e}")
            
            if not confirm_clicked:
                logger.error("모든 확인 버튼 클릭 방법 실패")
                return False
            
            # 수정 완료 모달창의 확인 버튼 클릭 (6단계)
            # 첫 번째 모달창이 닫힌 후 수정 완료 모달창이 나타날 때까지 대기
            time.sleep(2)
            logger.info("수정 완료 모달창의 확인 버튼 클릭 시도...")
            completion_clicked = False
            
            # 방법 1: 모달창 내부의 모든 확인 버튼 중 마지막 것 선택 (가장 성공률 높음)
            try:
                confirm_buttons = WebDriverWait(self.driver, 8).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//button[contains(text(), '확인')]"))
                )
                # 표시되고 클릭 가능한 마지막 확인 버튼 선택
                for button in reversed(confirm_buttons):
                    if button.is_displayed() and button.is_enabled():
                        button.click()
                        logger.info("수정 완료 확인 버튼 클릭 성공 (마지막 확인 버튼)")
                        completion_clicked = True
                        break
            except Exception as e:
                logger.debug(f"마지막 확인 버튼 찾기 실패: {e}")
            
            # 방법 2: data-wuic-action="dismiss" 속성으로 찾기
            if not completion_clicked:
                try:
                    completion_confirm_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-wuic-action='dismiss']"))
                    )
                    completion_confirm_button.click()
                    logger.info("수정 완료 확인 버튼 클릭 성공 (data-wuic-action='dismiss')")
                    completion_clicked = True
                except Exception as e:
                    logger.debug(f"data-wuic-action 확인 버튼 찾기 실패: {e}")
            
            # 방법 3: 모달창 footer 내부의 확인 버튼 찾기
            if not completion_clicked:
                try:
                    completion_confirm_button = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, "//div[@data-wuic-partial='foot']//button[contains(text(), '확인')]"))
                    )
                    completion_confirm_button.click()
                    logger.info("수정 완료 확인 버튼 클릭 성공 (footer XPath)")
                    completion_clicked = True
                except Exception as e:
                    logger.debug(f"footer XPath 확인 버튼 찾기 실패: {e}")
            
            # 방법 4: ESC 키로 모달창 닫기 (최후의 수단)
            if not completion_clicked:
                try:
                    self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                    logger.info("ESC 키로 수정 완료 모달창 닫기 시도")
                    completion_clicked = True
                    time.sleep(1)
                except Exception as e:
                    logger.debug(f"ESC 키 모달창 닫기 실패: {e}")
            
            if completion_clicked:
                logger.info("수정 완료 모달창 처리 완료")
                time.sleep(2)  # 모달창 닫힘 대기
            else:
                logger.warning("수정 완료 모달창 확인 버튼 클릭 실패 - 자동으로 닫힐 수 있음")
            
            # 변경 완료 확인 (모달창 닫힘 확인)
            time.sleep(2)  # 변경 처리 시간 대기
            
            change_success = False
            
            # 모달창이 닫혔는지 확인 (최대 30초 대기)
            for i in range(30):
                try:
                    modal = self.driver.find_element(By.CSS_SELECTOR, ".go-to-market-modal")
                    if not modal.is_displayed():
                        logger.info("모달창이 닫혔습니다. 변경이 완료되었습니다.")
                        change_success = True
                        break
                except Exception:
                    # 모달창을 찾을 수 없으면 닫힌 것으로 판단
                    logger.info("모달창을 찾을 수 없습니다. 변경이 완료되었습니다.")
                    change_success = True
                    break
                
                time.sleep(1)
                logger.debug(f"모달창 닫힘 대기 중... ({i+1}/30초)")
            
            # 에러 메시지 확인
            try:
                error_element = self.driver.find_element(By.CSS_SELECTOR, ".alert-error, .error-message")
                if error_element.is_displayed():
                    logger.error(f"에러 메시지 발견: {error_element.text}")
                    change_success = False
            except Exception:
                pass  # 에러 메시지가 없으면 정상
                        
            except Exception as e:
                logger.debug(f"에러 메시지 확인 실패: {e}")
            
            if change_success:
                logger.info(f"연동업체 '{integrator_name}' 변경이 완료되었습니다.")
                return True
            else:
                logger.warning(f"연동업체 '{integrator_name}' 변경 완료를 확인할 수 없습니다.")
                return False
            
        except Exception as e:
            logger.error(f"연동업체 변경 중 오류 발생: {str(e)}")
            return False
    
    def _click_user_menu(self):
        """
        사용자 메뉴를 클릭합니다.
        
        Returns:
            bool: 성공 여부
        """
        try:
            # 브라우저 세션 상태 확인
            try:
                self.driver.current_url
            except WebDriverException as e:
                logger.error(f"브라우저 세션이 유효하지 않습니다: {str(e)}")
                return False
            
            user_menu = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".my-user-menu-wrapper"))
            )
            user_menu.click()
            time.sleep(2)
            
            logger.info("사용자 메뉴 클릭 완료")
            return True
            
        except Exception as e:
            logger.error(f"사용자 메뉴 클릭 중 오류 발생: {str(e)}")
            return False
    
    def _click_logout_button_with_verification(self):
        """
        로그아웃 버튼을 클릭하고 URL 변경을 확인합니다.
        stale element reference 오류 방지를 위해 1회 클릭으로 수정하고 URL 변경을 확인합니다.
        
        Returns:
            bool: 성공 여부
        """
        try:
            # 현재 URL 저장
            current_url = self.driver.current_url
            logger.info(f"로그아웃 전 현재 URL: {current_url}")
            
            # 로그아웃 버튼 선택자들 (우선순위 순)
            logout_selectors = [
                "span.my-user-menu-logout-trigger",  # span 태그에 클래스가 있음
                ".my-user-menu-logout-trigger",      # 기존 선택자
                "//span[contains(@class, 'my-user-menu-logout-trigger')]",  # XPath
                "//span[text()='로그아웃']",  # 텍스트 기반
                ".my-user-menu-bottom span"  # 부모 요소 기반
            ]
            
            logout_button = None
            for selector in logout_selectors:
                try:
                    if selector.startswith('//'):
                        logout_button = self.wait.until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    else:
                        logout_button = self.wait.until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    logger.info(f"로그아웃 버튼 발견 (선택자: {selector})")
                    break
                except:
                    continue
            
            if not logout_button:
                logger.error("로그아웃 버튼을 찾을 수 없습니다")
                return False
            
            # 1회 클릭으로 수정 (stale element reference 오류 방지)
            logger.info("로그아웃 버튼 클릭")
            logout_button.click()
            time.sleep(2)
            
            # 로그아웃 성공 확인 (URL 변경 확인)
            for i in range(10):  # 최대 10초 대기
                try:
                    new_url = self.driver.current_url
                    if "xauth.coupang.com" in new_url or "login" in new_url.lower():
                        logger.info(f"로그아웃 성공 확인 - 새 URL: {new_url}")
                        return True
                    time.sleep(1)
                except Exception as e:
                    logger.debug(f"URL 확인 중 오류 (시도 {i+1}/10): {e}")
                    time.sleep(1)
            
            # 로그아웃 실패
            try:
                final_url = self.driver.current_url
                logger.warning(f"로그아웃 실패 - 최종 URL: {final_url}")
            except:
                logger.warning("로그아웃 실패 - URL 확인 불가")
            
            return False
            
        except Exception as e:
            logger.error(f"로그아웃 버튼 클릭 중 오류 발생: {str(e)}")
            return False
    
    def _click_logout_button(self):
        """
        로그아웃 버튼을 클릭하고 로그아웃 성공 여부를 URL로 확인합니다.
        stale element reference 오류 방지를 위해 1회 클릭으로 수정하고 URL 변경을 확인합니다.
        
        Returns:
            bool: 성공 여부
        """
        try:
            # 현재 URL 저장
            current_url = self.driver.current_url
            logger.info(f"로그아웃 전 현재 URL: {current_url}")
            
            # 로그아웃 버튼 선택자들 (우선순위 순)
            logout_selectors = [
                "span.my-user-menu-logout-trigger",  # span 태그에 클래스가 있음
                ".my-user-menu-logout-trigger",      # 기존 선택자
                "//span[contains(@class, 'my-user-menu-logout-trigger')]",  # XPath
                "//span[text()='로그아웃']",  # 텍스트 기반
                ".my-user-menu-bottom span"  # 부모 요소 기반
            ]
            
            logout_button = None
            for selector in logout_selectors:
                try:
                    if selector.startswith('//'):
                        logout_button = self.wait.until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    else:
                        logout_button = self.wait.until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    logger.info(f"로그아웃 버튼 발견 (선택자: {selector})")
                    break
                except:
                    continue
            
            if not logout_button:
                logger.error("로그아웃 버튼을 찾을 수 없습니다")
                return False
            
            # 1회 클릭으로 수정 (stale element reference 오류 방지)
            logger.info("로그아웃 버튼 클릭")
            logout_button.click()
            time.sleep(2)
            
            # 로그아웃 성공 확인 (URL 변경 확인)
            for i in range(10):  # 최대 10초 대기
                try:
                    new_url = self.driver.current_url
                    if "xauth.coupang.com" in new_url or "login" in new_url.lower():
                        logger.info(f"로그아웃 성공 확인 - 새 URL: {new_url}")
                        return True
                    time.sleep(1)
                except Exception as e:
                    logger.debug(f"URL 확인 중 오류 (시도 {i+1}/10): {e}")
                    time.sleep(1)
            
            # 로그아웃 실패
            try:
                final_url = self.driver.current_url
                logger.warning(f"로그아웃 실패 - 최종 URL: {final_url}")
            except:
                logger.warning("로그아웃 실패 - URL 확인 불가")
            
            return False
            
        except Exception as e:
            logger.error(f"로그아웃 버튼 클릭 중 오류 발생: {str(e)}")
            return False
    
    def _close_coupang_tab(self):
        """
        현재 쿠팡 탭을 닫고 메인 탭으로 돌아갑니다.
        """
        try:
            # 현재 열린 탭 수 확인
            all_windows = self.driver.window_handles
            logger.info(f"현재 열린 탭 수: {len(all_windows)}")
            
            if len(all_windows) > 1:
                # 현재 탭 닫기
                self.driver.close()
                logger.info("쿠팡 탭 닫기 완료")
                
                # 메인 탭으로 돌아가기 (첫 번째 탭)
                remaining_windows = self.driver.window_handles
                if remaining_windows:
                    self.driver.switch_to.window(remaining_windows[0])
                    logger.info("메인 탭으로 복귀 완료")
                else:
                    logger.warning("복귀할 탭이 없습니다")
            else:
                logger.info("현재 탭이 유일한 탭이므로 닫지 않습니다")
                
        except Exception as e:
            logger.error(f"쿠팡 탭 닫기 중 오류 발생: {str(e)}")