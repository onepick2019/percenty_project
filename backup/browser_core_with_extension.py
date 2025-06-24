"""브라우저 환경 설정 모듈 (퍼센티 확장 프로그램 자동 설치 포함)

이 모듈은 퍼센티 자동화에 필요한 브라우저 환경을 설정하며,
퍼센티 확장 프로그램을 자동으로 설치합니다.
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

class BrowserCoreWithExtension:
    """브라우저 핵심 기능 클래스 (퍼센티 확장 프로그램 자동 설치 포함)"""
    
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
        
    def setup_driver(self, headless=False, install_percenty_extension=True):
        """
        웹드라이버 설정 및 초기화 (퍼센티 확장 프로그램 자동 설치 포함)
        
        Args:
            headless (bool): 헤드리스 모드 사용 여부
            install_percenty_extension (bool): 퍼센티 확장 프로그램 설치 여부
            
        Returns:
            bool: 설정 성공 여부
        """
        logging.info("===== 브라우저 설정 시작 (퍼센티 확장 프로그램 자동 설치 포함) =====")
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
            
            # Chrome 137+ 확장 프로그램 로드 지원을 위한 플래그 추가
            chrome_options.add_argument("--disable-features=DisableLoadExtensionCommandLineSwitch")
            
            # GUI 안정성을 위한 옵션 추가
            if not headless:
                # Windows GUI 모드에서 안정적인 옵션들
                chrome_options.add_argument("--no-first-run")
                chrome_options.add_argument("--disable-blink-features=AutomationControlled")
                chrome_options.add_experimental_option("detach", True)  # GUI 모드에서 프로세스 분리
                chrome_options.add_argument("--disable-web-security")
                chrome_options.add_argument("--allow-running-insecure-content")
                chrome_options.add_argument("--disable-features=VizDisplayCompositor")
                logging.info("GUI 모드: Windows 호환성 Chrome 옵션 적용")
            
            # 퍼센티 확장 프로그램 자동 설치 설정
            if install_percenty_extension:
                # 퍼센티 확장 프로그램 로드 (CRX 파일 우선)
                try:
                    # 방법 1: CRX 파일 사용 (우선) - 정상적인 ID와 출처를 가짐
                    extension_path = os.path.join(PERCENTY_EXTENSION_PATH, "percenty_extension_with_key.crx")
                    if os.path.exists(extension_path):
                        chrome_options.add_extension(extension_path)
                        logging.info(f"퍼센티 확장 프로그램 로드 (CRX): {extension_path}")
                    else:
                        # 방법 2: 대체 CRX 파일 시도
                        alt_extension_path = os.path.join(PERCENTY_EXTENSION_PATH, "percenty_webstore.crx")
                        if os.path.exists(alt_extension_path):
                            chrome_options.add_extension(alt_extension_path)
                            logging.info(f"퍼센티 확장 프로그램 로드 (대체 CRX): {alt_extension_path}")
                        else:
                            # 방법 3: 압축 해제된 확장 프로그램 디렉토리 사용 (최후 수단)
                            manifest_path = os.path.join(PERCENTY_EXTENSION_PATH, "manifest.json")
                            if os.path.exists(manifest_path):
                                chrome_options.add_argument(f"--load-extension={PERCENTY_EXTENSION_PATH}")
                                logging.info(f"퍼센티 확장 프로그램 로드 (디렉토리): {PERCENTY_EXTENSION_PATH}")
                                logging.warning("압축 해제된 확장 프로그램을 사용합니다. ID 및 출처 문제가 발생할 수 있습니다.")
                            else:
                                logging.warning("퍼센티 확장 프로그램을 찾을 수 없습니다. 확장 프로그램 없이 진행합니다.")
                except Exception as e:
                    logging.error(f"퍼센티 확장 프로그램 로드 실패: {e}")
                    logging.warning("확장 프로그램 없이 브라우저를 시작합니다.")
                
                # 확장 프로그램 관련 보안 정책 완화
                chrome_options.add_argument("--disable-extensions-file-access-check")
                chrome_options.add_argument("--disable-extensions-http-throttling")
                chrome_options.add_argument("--allow-running-insecure-content")
                chrome_options.add_argument("--disable-web-security")
                chrome_options.add_argument("--disable-features=VizDisplayCompositor")
                # 개발자 모드 관련 설정
                chrome_options.add_argument("--enable-extensions")
                # 자동화 감지 방지
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chrome_options.add_experimental_option("useAutomationExtension", False)
            
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
            
            # 확장 프로그램 설치 확인
            if install_percenty_extension:
                time.sleep(3)  # 확장 프로그램 로드 대기
                if self._verify_percenty_extension_loaded():
                    logging.info("퍼센티 확장 프로그램 로드 확인 완료")
                else:
                    logging.warning("퍼센티 확장 프로그램 로드 확인 실패")
            
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
    
    def _verify_percenty_extension_loaded(self):
        """
        퍼센티 확장 프로그램이 정상적으로 로드되었는지 확인
        
        Returns:
            bool: 로드 확인 여부
        """
        try:
            logging.info("퍼센티 확장 프로그램 로드 확인 시작")
            
            # chrome://extensions 페이지로 이동
            original_url = self.driver.current_url
            self.driver.get("chrome://extensions")
            time.sleep(5)  # 페이지 로드 대기 시간 증가
            
            # 개발자 모드 활성화 확인 및 활성화
            try:
                dev_mode_toggle = self.driver.find_element("css selector", "#devMode")
                if not dev_mode_toggle.is_selected():
                    dev_mode_toggle.click()
                    time.sleep(2)
                    logging.info("개발자 모드 활성화됨")
                else:
                    logging.info("개발자 모드 이미 활성화됨")
            except Exception as dev_error:
                logging.warning(f"개발자 모드 토글 확인/활성화 실패: {dev_error}")
            
            # 페이지 소스 가져오기
            page_source = self.driver.page_source
            
            # 디버깅을 위한 페이지 소스 일부 출력
            logging.info(f"chrome://extensions 페이지 소스 길이: {len(page_source)}")
            
            # 확장 프로그램 관련 키워드들을 더 포괄적으로 검색
            extension_keywords = [
                "퍼센티",
                "Percenty", 
                "percenty",
                "manifest.json",
                "압축해제된 확장 프로그램",
                "Unpacked extension",
                "percenty_extension",
                "jlcdjppbpplpdgfeknhioedbhfceaben",  # 하드코딩된 ID
                "extension-item",  # DOM 요소
                "extensions-item",  # DOM 요소
                PERCENTY_EXTENSION_PATH.replace("\\", "/")  # 경로 확인
            ]
            
            found_indicators = []
            for keyword in extension_keywords:
                if keyword.lower() in page_source.lower():
                    found_indicators.append(keyword)
                    logging.info(f"키워드 발견: {keyword}")
            
            # 확장 프로그램 DOM 요소 직접 검색
            extension_elements_found = False
            try:
                # 다양한 선택자로 확장 프로그램 요소 찾기
                selectors = [
                    "extensions-item",
                    "extension-item", 
                    "[id*='extension']",
                    "[class*='extension']",
                    "cr-toggle"
                ]
                
                for selector in selectors:
                    try:
                        elements = self.driver.find_elements("css selector", selector)
                        if elements:
                            extension_elements_found = True
                            logging.info(f"선택자 '{selector}'로 {len(elements)}개 요소 발견")
                            
                            # 각 요소의 텍스트 확인
                            for i, element in enumerate(elements[:5]):  # 최대 5개만 확인
                                try:
                                    element_text = element.text
                                    if element_text and len(element_text) > 0:
                                        logging.info(f"요소 {i+1} 텍스트: {element_text[:200]}...")
                                        if any(keyword in element_text.lower() for keyword in ["퍼센티", "percenty"]):
                                            found_indicators.append(f"dom_element_text_{keyword}")
                                            logging.info(f"퍼센티 관련 텍스트 발견: {element_text[:100]}...")
                                except Exception as text_error:
                                    logging.warning(f"요소 텍스트 추출 실패: {text_error}")
                    except Exception as selector_error:
                        logging.warning(f"선택자 '{selector}' 검색 실패: {selector_error}")
                        
            except Exception as dom_error:
                logging.warning(f"DOM 요소 검색 실패: {dom_error}")
            
            # JavaScript로 확장 프로그램 정보 확인
            try:
                extension_info = self.driver.execute_script("""
                    var result = {
                        'management_available': typeof chrome !== 'undefined' && typeof chrome.management !== 'undefined',
                        'runtime_available': typeof chrome !== 'undefined' && typeof chrome.runtime !== 'undefined',
                        'extensions_page': window.location.href.includes('chrome://extensions'),
                        'page_title': document.title,
                        'extension_elements': document.querySelectorAll('extensions-item, extension-item').length
                    };
                    
                    // 가능한 경우 확장 프로그램 목록 가져오기
                    if (result.management_available) {
                        try {
                            chrome.management.getAll(function(extensions) {
                                console.log('Extensions found:', extensions);
                            });
                        } catch(e) {
                            console.log('Management API error:', e);
                        }
                    }
                    
                    return result;
                """)
                logging.info(f"JavaScript 확장 프로그램 정보: {extension_info}")
                        
            except Exception as js_error:
                logging.warning(f"JavaScript 확장 프로그램 확인 실패: {js_error}")
            
            # 결과 분석 및 반환
            if found_indicators or extension_elements_found:
                logging.info(f"퍼센티 확장 프로그램 로드 확인됨! 발견된 지표: {found_indicators}")
                logging.info(f"확장 프로그램 DOM 요소 발견 여부: {extension_elements_found}")
                
                # 원래 URL로 돌아가기
                if original_url and original_url != "data:,":
                    self.driver.get(original_url)
                return True
            else:
                logging.warning("퍼센티 확장 프로그램을 찾을 수 없습니다.")
                logging.warning("확장 프로그램이 로드되지 않았거나 인식되지 않았습니다.")
                
                # 추가 디버깅 정보 출력
                logging.info("=== 디버깅 정보 ====")
                logging.info(f"확장 프로그램 경로: {PERCENTY_EXTENSION_PATH}")
                logging.info(f"경로 존재 여부: {os.path.exists(PERCENTY_EXTENSION_PATH)}")
                
                # manifest.json 파일 확인
                manifest_path = os.path.join(PERCENTY_EXTENSION_PATH, 'manifest.json')
                if os.path.exists(manifest_path):
                    logging.info(f"manifest.json 파일 존재: {manifest_path}")
                    try:
                        with open(manifest_path, 'r', encoding='utf-8') as f:
                            manifest_content = f.read()[:500]  # 처음 500자만
                            logging.info(f"manifest.json 내용 (일부): {manifest_content}...")
                    except Exception as manifest_error:
                        logging.warning(f"manifest.json 읽기 실패: {manifest_error}")
                else:
                    logging.warning(f"manifest.json 파일이 없습니다: {manifest_path}")
                
                # 원래 URL로 돌아가기
                if original_url and original_url != "data:,":
                    self.driver.get(original_url)
                return False
                
        except Exception as e:
            logging.error(f"퍼센티 확장 프로그램 로드 확인 중 오류: {e}")
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
def create_browser_with_percenty_extension(window_width=None, window_height=None, 
                                         window_x=None, window_y=None, headless=False):
    """
    퍼센티 확장 프로그램이 설치된 브라우저 생성
    
    Args:
        window_width (int): 브라우저 창 너비
        window_height (int): 브라우저 창 높이
        window_x (int): 브라우저 창 X 위치
        window_y (int): 브라우저 창 Y 위치
        headless (bool): 헤드리스 모드 사용 여부
        
    Returns:
        webdriver.Chrome: 설정된 Chrome 드라이버 (실패 시 None)
    """
    browser_core = BrowserCoreWithExtension(window_width, window_height, window_x, window_y)
    
    if browser_core.setup_driver(headless=headless, install_percenty_extension=True):
        return browser_core.get_driver()
    else:
        return None

if __name__ == "__main__":
    # 테스트 코드
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    print("퍼센티 확장 프로그램 자동 설치 테스트 시작")
    
    # 브라우저 생성 (퍼센티 확장 프로그램 자동 설치)
    driver = create_browser_with_percenty_extension()
    
    if driver:
        print("브라우저 생성 성공! 퍼센티 확장 프로그램이 설치되었습니다.")
        print("30초 후 브라우저를 종료합니다...")
        time.sleep(30)
        driver.quit()
    else:
        print("브라우저 생성 실패")