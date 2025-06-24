"""브라우저 환경 설정 모듈 (수동 확장 프로그램 설치 지원)

이 모듈은 개발자 모드를 활성화하고 퍼센티 확장 프로그램을 수동으로 설치할 수 있도록 지원합니다.
"""

import os
import time
import logging
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    ElementNotInteractableException, 
    StaleElementReferenceException
)

# 로깅 설정
logger = logging.getLogger(__name__)

# 상수 정의
ORIGINAL_WIDTH = 1920
ORIGINAL_HEIGHT = 1080
PERCENTY_EXTENSION_PATH = r"c:\Projects\percenty_project\percenty_extension"

class BrowserCoreWithManualExtension:
    """브라우저 핵심 기능 클래스 (수동 확장 프로그램 설치 지원)"""
    
    def __init__(self, window_width=None, window_height=None, window_x=None, window_y=None):
        """
        초기화
        
        Args:
            window_width (int): 브라우저 창 너비 (기본값: 화면 너비의 절반)
            window_height (int): 브라우저 창 높이 (기본값: 화면 높이)
            window_x (int): 브라우저 창 X 위치 (기본값: 화면 오른쪽 절반)
            window_y (int): 브라우저 창 Y 위치 (기본값: 0)
        """
        self.window_width = window_width
        self.window_height = window_height
        self.window_x = window_x
        self.window_y = window_y
        self.driver = None
        self.inner_width = None
        self.inner_height = None
        
    def setup_driver(self, headless=False):
        """
        웹드라이버 설정 및 초기화
        
        Args:
            headless (bool): 헤드리스 모드 사용 여부
            
        Returns:
            bool: 설정 성공 여부
        """
        logging.info("===== 브라우저 설정 시작 (수동 확장 프로그램 설치 지원) =====")
        try:
            # Chrome 옵션 설정
            chrome_options = Options()
            
            # 헤드리스 모드 설정
            if headless:
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--window-size=1920,1080")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                logging.info("헤드리스 모드로 브라우저 설정")
            else:
                logging.info("일반 모드로 브라우저 설정")
            
            # 창 크기 설정
            if self.window_width and self.window_height:
                chrome_options.add_argument(f"--window-size={self.window_width},{self.window_height}")
            else:
                chrome_options.add_argument("--start-maximized")
            
            # 창 위치 설정
            if self.window_x is not None and self.window_y is not None:
                chrome_options.add_argument(f"--window-position={self.window_x},{self.window_y}")
            
            # 자동화 표시줄 제거
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option("useAutomationExtension", False)
            
            # 알림 권한 요청 비활성화
            chrome_options.add_argument("--disable-notifications")
            
            # 기본 설정
            chrome_options.add_experimental_option("prefs", {
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
                "profile.default_content_setting_values.notifications": 2
            })
            
            # GUI 안정성을 위한 옵션 추가
            if not headless:
                chrome_options.add_argument("--no-first-run")
                chrome_options.add_argument("--disable-blink-features=AutomationControlled")
                chrome_options.add_experimental_option("detach", True)
                logging.info("GUI 모드: Windows 호환성 Chrome 옵션 적용")
            
            # Chrome 드라이버 생성
            try:
                logging.info("Chrome 드라이버 생성 시작")
                import threading
                import queue
                
                result_queue = queue.Queue()
                exception_queue = queue.Queue()
                
                def create_driver():
                    try:
                        logging.info("webdriver.Chrome() 호출 시작")
                        driver = webdriver.Chrome(options=chrome_options)
                        logging.info("webdriver.Chrome() 호출 완료")
                        result_queue.put(driver)
                        logging.info("result_queue에 driver 저장 완료")
                    except Exception as e:
                        logging.error(f"webdriver.Chrome() 호출 중 오류: {e}")
                        exception_queue.put(e)
                
                # 드라이버 생성을 별도 스레드에서 실행
                driver_thread = threading.Thread(target=create_driver)
                driver_thread.daemon = True
                driver_thread.start()
                
                # 30초 타임아웃으로 대기
                driver_thread.join(timeout=30)
                
                if driver_thread.is_alive():
                    logging.error("Chrome 드라이버 생성이 30초 내에 완료되지 않았습니다.")
                    raise TimeoutError("Chrome 드라이버 생성 타임아웃 (30초)")
                
                # 결과 확인
                if not exception_queue.empty():
                    raise exception_queue.get()
                
                if not result_queue.empty():
                    self.driver = result_queue.get()
                    logging.info("Chrome 드라이버 생성 완료")
                else:
                    raise Exception("Chrome 드라이버 생성 실패: 알 수 없는 오류")
                    
            except Exception as e:
                logging.error(f"Chrome 드라이버 생성 실패: {e}")
                return False
            
            # 브라우저 창 설정
            if not headless:
                self._setup_window()
            
            logging.info("===== 브라우저 설정 완료 =====")
            return True
            
        except Exception as e:
            logging.error(f"브라우저 설정 중 오류 발생: {e}")
            logging.error(traceback.format_exc())
            return False
    
    def _setup_window(self):
        """브라우저 창 크기 및 위치 설정"""
        try:
            if self.window_width and self.window_height:
                self.driver.set_window_size(self.window_width, self.window_height)
                logging.info(f"브라우저 창 크기 설정: {self.window_width}x{self.window_height}")
            
            if self.window_x is not None and self.window_y is not None:
                self.driver.set_window_position(self.window_x, self.window_y)
                logging.info(f"브라우저 창 위치 설정: ({self.window_x}, {self.window_y})")
                
        except Exception as e:
            logging.warning(f"브라우저 창 설정 중 오류: {e}")
    
    def enable_developer_mode_and_install_extension(self):
        """
        개발자 모드를 활성화하고 퍼센티 확장 프로그램 설치를 안내합니다.
        
        Returns:
            bool: 성공 여부
        """
        try:
            logging.info("개발자 모드 활성화 및 확장 프로그램 설치 프로세스 시작")
            
            # Chrome 확장 프로그램 관리 페이지로 이동
            logging.info("Chrome 확장 프로그램 관리 페이지로 이동")
            self.driver.get("chrome://extensions/")
            time.sleep(3)
            
            # 개발자 모드 활성화 시도
            developer_mode_enabled = self._enable_developer_mode()
            
            if developer_mode_enabled:
                logging.info("✅ 개발자 모드 활성화 성공")
                
                # 확장 프로그램 설치 안내
                self._guide_extension_installation()
                return True
            else:
                logging.warning("❌ 개발자 모드 자동 활성화 실패")
                
                # 수동 설치 안내
                self._guide_manual_installation()
                return False
                
        except Exception as e:
            logging.error(f"개발자 모드 활성화 및 확장 프로그램 설치 중 오류: {e}")
            return False
    
    def _enable_developer_mode(self):
        """
        개발자 모드를 자동으로 활성화합니다.
        
        Returns:
            bool: 활성화 성공 여부
        """
        try:
            logging.info("개발자 모드 자동 활성화 시도")
            
            # 페이지 소스 확인
            page_source = self.driver.page_source
            is_korean = "개발자 모드" in page_source
            is_english = "Developer mode" in page_source
            
            logging.info(f"페이지 언어 감지 - 한국어: {is_korean}, 영어: {is_english}")
            
            # 1. 텍스트 기반 XPath 시도
            if is_korean:
                korean_xpaths = [
                    "//span[text()='개발자 모드']/following-sibling::cr-toggle",
                    "//span[contains(text(), '개발자 모드')]/parent::*/cr-toggle",
                    "//div[contains(@class, 'more-actions')]//span[text()='개발자 모드']/following-sibling::cr-toggle"
                ]
                
                for xpath in korean_xpaths:
                    if self._try_toggle_by_xpath(xpath, f"한국어 XPath: {xpath}"):
                        return True
            
            if is_english:
                english_xpaths = [
                    "//span[text()='Developer mode']/following-sibling::cr-toggle",
                    "//span[contains(text(), 'Developer mode')]/parent::*/cr-toggle",
                    "//div[contains(@class, 'more-actions')]//span[text()='Developer mode']/following-sibling::cr-toggle"
                ]
                
                for xpath in english_xpaths:
                    if self._try_toggle_by_xpath(xpath, f"영어 XPath: {xpath}"):
                        return True
            
            # 2. CSS 선택자 시도
            css_selectors = [
                "#devMode",
                "cr-toggle[id='devMode']",
                "cr-toggle[aria-labelledby*='dev']"
            ]
            
            for selector in css_selectors:
                if self._try_toggle_by_css(selector, f"CSS: {selector}"):
                    return True
            
            # 3. Shadow DOM 접근 시도
            if self._try_shadow_dom_toggle():
                return True
            
            # 4. 모든 cr-toggle 요소 검사
            if self._try_all_toggles():
                return True
            
            logging.warning("모든 방법으로 개발자 모드 자동 활성화 실패")
            return False
            
        except Exception as e:
            logging.error(f"개발자 모드 활성화 중 오류: {e}")
            return False
    
    def _try_toggle_by_xpath(self, xpath, description):
        """XPath로 토글 시도"""
        try:
            element = self.driver.find_element(By.XPATH, xpath)
            return self._toggle_element(element, description)
        except NoSuchElementException:
            logging.debug(f"{description}: 요소를 찾을 수 없음")
            return False
        except Exception as e:
            logging.debug(f"{description}: 오류 - {e}")
            return False
    
    def _try_toggle_by_css(self, selector, description):
        """CSS 선택자로 토글 시도"""
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, selector)
            return self._toggle_element(element, description)
        except NoSuchElementException:
            logging.debug(f"{description}: 요소를 찾을 수 없음")
            return False
        except Exception as e:
            logging.debug(f"{description}: 오류 - {e}")
            return False
    
    def _try_shadow_dom_toggle(self):
        """Shadow DOM을 통한 토글 시도"""
        try:
            logging.info("Shadow DOM을 통한 개발자 모드 토글 시도")
            
            result = self.driver.execute_script("""
                // Shadow DOM 내부에서 개발자 모드 토글 찾기
                function findDeveloperModeToggle() {
                    // 모든 extensions-manager 요소 찾기
                    const managers = document.querySelectorAll('extensions-manager');
                    
                    for (let manager of managers) {
                        if (manager.shadowRoot) {
                            // extensions-toolbar 찾기
                            const toolbar = manager.shadowRoot.querySelector('extensions-toolbar');
                            if (toolbar && toolbar.shadowRoot) {
                                // cr-toggle 요소들 찾기
                                const toggles = toolbar.shadowRoot.querySelectorAll('cr-toggle');
                                
                                for (let i = 0; i < toggles.length; i++) {
                                    const toggle = toggles[i];
                                    const id = toggle.id || '';
                                    const ariaLabelledby = toggle.getAttribute('aria-labelledby') || '';
                                    
                                    // 개발자 모드 토글인지 확인
                                    if (id.toLowerCase().includes('dev') || 
                                        ariaLabelledby.toLowerCase().includes('dev')) {
                                        
                                        const isPressed = toggle.getAttribute('aria-pressed') === 'true';
                                        
                                        if (isPressed) {
                                            return {success: true, message: '개발자 모드가 이미 활성화됨', alreadyEnabled: true};
                                        } else {
                                            // 토글 클릭
                                            toggle.click();
                                            return {success: true, message: '개발자 모드 토글 클릭 완료'};
                                        }
                                    }
                                }
                            }
                        }
                    }
                    
                    return {success: false, message: '개발자 모드 토글을 찾을 수 없음'};
                }
                
                return findDeveloperModeToggle();
            """)
            
            if result['success']:
                if result.get('alreadyEnabled'):
                    logging.info("Shadow DOM: 개발자 모드가 이미 활성화됨")
                else:
                    logging.info("Shadow DOM: 개발자 모드 토글 클릭 완료")
                    time.sleep(2)  # 토글 상태 변경 대기
                
                return True
            else:
                logging.debug(f"Shadow DOM: {result['message']}")
                return False
                
        except Exception as e:
            logging.debug(f"Shadow DOM 토글 시도 중 오류: {e}")
            return False
    
    def _try_all_toggles(self):
        """모든 cr-toggle 요소 검사"""
        try:
            logging.info("모든 cr-toggle 요소 검사")
            
            toggles = self.driver.find_elements(By.TAG_NAME, "cr-toggle")
            
            for i, toggle in enumerate(toggles):
                try:
                    toggle_id = toggle.get_attribute("id") or ""
                    aria_labelledby = toggle.get_attribute("aria-labelledby") or ""
                    
                    # 개발자 모드와 관련된 토글인지 확인
                    if ("dev" in toggle_id.lower() or 
                        "dev" in aria_labelledby.lower()):
                        
                        logging.info(f"개발자 모드 토글 후보 발견 (인덱스 {i}): id={toggle_id}, aria-labelledby={aria_labelledby}")
                        
                        if self._toggle_element(toggle, f"전체 검사 토글 {i}"):
                            return True
                            
                except Exception as e:
                    logging.debug(f"토글 {i} 검사 중 오류: {e}")
                    continue
            
            logging.debug("개발자 모드 토글을 찾을 수 없음")
            return False
            
        except Exception as e:
            logging.debug(f"전체 토글 검사 중 오류: {e}")
            return False
    
    def _toggle_element(self, element, description):
        """토글 요소 클릭"""
        try:
            # 현재 상태 확인
            aria_pressed = element.get_attribute("aria-pressed")
            
            if aria_pressed == "true":
                logging.info(f"{description}: 개발자 모드가 이미 활성화됨")
                return True
            
            # 토글 클릭
            element.click()
            time.sleep(2)  # 토글 상태 변경 대기
            
            # 상태 재확인
            aria_pressed_after = element.get_attribute("aria-pressed")
            
            if aria_pressed_after == "true":
                logging.info(f"{description}: 개발자 모드 활성화 성공")
                return True
            else:
                logging.debug(f"{description}: 토글 클릭했으나 활성화 확인 실패")
                return False
                
        except Exception as e:
            logging.debug(f"{description}: 토글 클릭 중 오류 - {e}")
            return False
    
    def _guide_extension_installation(self):
        """확장 프로그램 설치 안내"""
        logging.info("\n" + "="*60)
        logging.info("퍼센티 확장 프로그램 설치 안내")
        logging.info("="*60)
        logging.info("개발자 모드가 활성화되었습니다!")
        logging.info("")
        logging.info("다음 단계를 수행하세요:")
        logging.info("1. '압축해제된 확장 프로그램을 로드합니다' 버튼을 클릭하세요")
        logging.info(f"2. 다음 폴더를 선택하세요: {PERCENTY_EXTENSION_PATH}")
        logging.info("3. '폴더 선택' 버튼을 클릭하세요")
        logging.info("")
        logging.info("설치가 완료되면 퍼센티 확장 프로그램이 목록에 나타납니다.")
        logging.info("="*60)
        
        # 사용자 입력 대기
        input("\n확장 프로그램 설치를 완료한 후 Enter 키를 눌러주세요...")
    
    def _guide_manual_installation(self):
        """수동 설치 안내"""
        logging.info("\n" + "="*60)
        logging.info("수동 설치 안내")
        logging.info("="*60)
        logging.info("개발자 모드 자동 활성화에 실패했습니다.")
        logging.info("")
        logging.info("다음 단계를 수동으로 수행하세요:")
        logging.info("1. Chrome 확장 프로그램 관리 페이지에서 '개발자 모드' 토글을 활성화하세요")
        logging.info("2. '압축해제된 확장 프로그램을 로드합니다' 버튼을 클릭하세요")
        logging.info(f"3. 다음 폴더를 선택하세요: {PERCENTY_EXTENSION_PATH}")
        logging.info("4. '폴더 선택' 버튼을 클릭하세요")
        logging.info("")
        logging.info("설치가 완료되면 퍼센티 확장 프로그램이 목록에 나타납니다.")
        logging.info("="*60)
        
        # 사용자 입력 대기
        input("\n확장 프로그램 설치를 완료한 후 Enter 키를 눌러주세요...")
    
    def verify_extension_installed(self):
        """
        퍼센티 확장 프로그램이 설치되었는지 확인합니다.
        
        Returns:
            bool: 설치 확인 여부
        """
        try:
            logging.info("퍼센티 확장 프로그램 설치 확인")
            
            # 페이지 새로고침
            self.driver.refresh()
            time.sleep(3)
            
            # 페이지 소스에서 퍼센티 확장 프로그램 확인
            page_source = self.driver.page_source
            
            # 퍼센티 확장 프로그램 관련 텍스트 확인
            percenty_indicators = [
                "퍼센티",
                "Percenty", 
                "percenty"
            ]
            
            found_indicators = []
            for indicator in percenty_indicators:
                if indicator in page_source:
                    found_indicators.append(indicator)
            
            if found_indicators:
                logging.info(f"✅ 퍼센티 확장 프로그램 설치 확인됨: {found_indicators}")
                return True
            else:
                logging.warning("❌ 퍼센티 확장 프로그램을 찾을 수 없습니다.")
                return False
                
        except Exception as e:
            logging.error(f"확장 프로그램 설치 확인 중 오류: {e}")
            return False
    
    def get_driver(self):
        """웹드라이버 인스턴스 반환"""
        return self.driver
    
    def close(self):
        """브라우저 종료"""
        if self.driver:
            try:
                self.driver.quit()
                logging.info("브라우저 종료 완료")
            except Exception as e:
                logging.error(f"브라우저 종료 중 오류: {e}")
            finally:
                self.driver = None

# 편의 함수
def create_browser_with_manual_extension(window_width=None, window_height=None, 
                                        window_x=None, window_y=None, headless=False):
    """
    수동 확장 프로그램 설치를 지원하는 브라우저 생성
    
    Args:
        window_width (int): 브라우저 창 너비
        window_height (int): 브라우저 창 높이
        window_x (int): 브라우저 창 X 위치
        window_y (int): 브라우저 창 Y 위치
        headless (bool): 헤드리스 모드 사용 여부
        
    Returns:
        BrowserCoreWithManualExtension: 설정된 브라우저 인스턴스 (실패 시 None)
    """
    browser_core = BrowserCoreWithManualExtension(window_width, window_height, window_x, window_y)
    
    if browser_core.setup_driver(headless=headless):
        return browser_core
    else:
        return None

if __name__ == "__main__":
    # 테스트 코드
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    print("수동 확장 프로그램 설치 지원 브라우저 테스트 시작")
    
    # 브라우저 생성
    browser_core = create_browser_with_manual_extension()
    
    if browser_core:
        print("브라우저 생성 성공!")
        
        # 개발자 모드 활성화 및 확장 프로그램 설치 안내
        browser_core.enable_developer_mode_and_install_extension()
        
        # 확장 프로그램 설치 확인
        if browser_core.verify_extension_installed():
            print("✅ 퍼센티 확장 프로그램 설치 완료!")
        else:
            print("❌ 퍼센티 확장 프로그램 설치 확인 실패")
        
        print("10초 후 브라우저를 종료합니다...")
        time.sleep(10)
        browser_core.close()
    else:
        print("브라우저 생성 실패")