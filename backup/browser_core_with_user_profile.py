"""브라우저 환경 설정 모듈 (사용자 프로필 기반 퍼센티 확장 프로그램 설치)

이 모듈은 Chrome 사용자 프로필을 사용하여 퍼센티 확장 프로그램을 설치합니다.
사용자 프로필에 확장 프로그램을 미리 설치하여 자동화 시 바로 사용할 수 있도록 합니다.
"""

import os
import time
import logging
import traceback
import tempfile
import shutil
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
USER_DATA_DIR = r"c:\Projects\percenty_project\chrome_user_data"

class BrowserCoreWithUserProfile:
    """브라우저 핵심 기능 클래스 (사용자 프로필 기반 확장 프로그램 설치)"""
    
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
        self.user_data_dir = USER_DATA_DIR
        
    def setup_user_profile_with_extension(self):
        """
        퍼센티 확장 프로그램이 설치된 Chrome 사용자 프로필을 생성합니다.
        
        Returns:
            bool: 프로필 생성 성공 여부
        """
        try:
            logging.info("퍼센티 확장 프로그램이 포함된 Chrome 사용자 프로필 생성 시작")
            
            # 사용자 데이터 디렉토리 생성
            if not os.path.exists(self.user_data_dir):
                os.makedirs(self.user_data_dir)
                logging.info(f"사용자 데이터 디렉토리 생성: {self.user_data_dir}")
            
            # 임시 브라우저로 확장 프로그램 설치
            temp_driver = None
            try:
                logging.info("임시 브라우저를 사용하여 확장 프로그램 설치")
                
                # Chrome 옵션 설정 (확장 프로그램 설치용)
                chrome_options = Options()
                chrome_options.add_argument(f"--user-data-dir={self.user_data_dir}")
                chrome_options.add_argument(f"--load-extension={PERCENTY_EXTENSION_PATH}")
                chrome_options.add_argument("--no-first-run")
                chrome_options.add_argument("--disable-default-apps")
                chrome_options.add_argument("--disable-extensions-file-access-check")
                chrome_options.add_argument("--enable-extensions")
                
                # 임시 브라우저 생성
                temp_driver = webdriver.Chrome(options=chrome_options)
                
                # 확장 프로그램 로드 대기
                time.sleep(5)
                
                # Chrome 확장 프로그램 관리 페이지에서 확인
                temp_driver.get("chrome://extensions/")
                time.sleep(3)
                
                page_source = temp_driver.page_source
                if "퍼센티" in page_source or "Percenty" in page_source:
                    logging.info("✅ 퍼센티 확장 프로그램이 사용자 프로필에 설치되었습니다.")
                    
                    # 브라우저 종료 (프로필 저장)
                    temp_driver.quit()
                    time.sleep(2)
                    
                    return True
                else:
                    logging.warning("❌ 퍼센티 확장 프로그램 설치 확인 실패")
                    return False
                    
            except Exception as e:
                logging.error(f"임시 브라우저를 통한 확장 프로그램 설치 실패: {e}")
                return False
                
            finally:
                if temp_driver:
                    try:
                        temp_driver.quit()
                    except:
                        pass
                        
        except Exception as e:
            logging.error(f"사용자 프로필 생성 중 오류: {e}")
            return False
    
    def setup_driver(self, headless=False, use_existing_profile=True):
        """
        웹드라이버 설정 및 초기화 (사용자 프로필 사용)
        
        Args:
            headless (bool): 헤드리스 모드 사용 여부
            use_existing_profile (bool): 기존 프로필 사용 여부
            
        Returns:
            bool: 설정 성공 여부
        """
        logging.info("===== 브라우저 설정 시작 (사용자 프로필 기반) =====")
        try:
            # 사용자 프로필 설정 (필요한 경우)
            if use_existing_profile:
                if not os.path.exists(self.user_data_dir) or not self._check_profile_has_extension():
                    logging.info("사용자 프로필이 없거나 확장 프로그램이 설치되지 않음. 새로 생성합니다.")
                    if not self.setup_user_profile_with_extension():
                        logging.error("사용자 프로필 생성 실패")
                        return False
            
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
            
            # 사용자 프로필 사용
            if use_existing_profile:
                chrome_options.add_argument(f"--user-data-dir={self.user_data_dir}")
                logging.info(f"사용자 프로필 사용: {self.user_data_dir}")
            
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
                chrome_options.add_argument("--disable-web-security")
                chrome_options.add_argument("--allow-running-insecure-content")
                chrome_options.add_argument("--disable-features=VizDisplayCompositor")
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
            
            # 확장 프로그램 설치 확인
            if use_existing_profile:
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
    
    def _check_profile_has_extension(self):
        """
        사용자 프로필에 퍼센티 확장 프로그램이 설치되어 있는지 확인
        
        Returns:
            bool: 확장 프로그램 설치 여부
        """
        try:
            # 확장 프로그램 관련 파일 확인
            extensions_dir = os.path.join(self.user_data_dir, "Default", "Extensions")
            if os.path.exists(extensions_dir):
                # 확장 프로그램 폴더 확인
                for ext_folder in os.listdir(extensions_dir):
                    ext_path = os.path.join(extensions_dir, ext_folder)
                    if os.path.isdir(ext_path):
                        # manifest.json 확인
                        for version_folder in os.listdir(ext_path):
                            manifest_path = os.path.join(ext_path, version_folder, "manifest.json")
                            if os.path.exists(manifest_path):
                                try:
                                    import json
                                    with open(manifest_path, 'r', encoding='utf-8') as f:
                                        manifest = json.load(f)
                                    
                                    name = manifest.get('name', '')
                                    if '퍼센티' in name or 'Percenty' in name.lower():
                                        logging.info(f"사용자 프로필에서 퍼센티 확장 프로그램 발견: {name}")
                                        return True
                                except:
                                    continue
            
            return False
            
        except Exception as e:
            logging.error(f"프로필 확장 프로그램 확인 중 오류: {e}")
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
            
            # Chrome 확장 프로그램 관리 페이지로 이동
            original_url = self.driver.current_url
            self.driver.get("chrome://extensions/")
            time.sleep(2)
            
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
                logging.info(f"퍼센티 확장 프로그램 로드 확인됨: {found_indicators}")
                # 원래 URL로 돌아가기
                if original_url and original_url != "data:,":
                    self.driver.get(original_url)
                return True
            else:
                logging.warning("퍼센티 확장 프로그램을 찾을 수 없습니다.")
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
def create_browser_with_user_profile(window_width=None, window_height=None, 
                                    window_x=None, window_y=None, headless=False):
    """
    사용자 프로필을 사용하여 퍼센티 확장 프로그램이 설치된 브라우저 생성
    
    Args:
        window_width (int): 브라우저 창 너비
        window_height (int): 브라우저 창 높이
        window_x (int): 브라우저 창 X 위치
        window_y (int): 브라우저 창 Y 위치
        headless (bool): 헤드리스 모드 사용 여부
        
    Returns:
        webdriver.Chrome: 설정된 Chrome 드라이버 (실패 시 None)
    """
    browser_core = BrowserCoreWithUserProfile(window_width, window_height, window_x, window_y)
    
    if browser_core.setup_driver(headless=headless, use_existing_profile=True):
        return browser_core.get_driver()
    else:
        return None

if __name__ == "__main__":
    # 테스트 코드
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    print("사용자 프로필 기반 퍼센티 확장 프로그램 설치 테스트 시작")
    
    # 브라우저 생성 (사용자 프로필 사용)
    driver = create_browser_with_user_profile()
    
    if driver:
        print("브라우저 생성 성공! 퍼센티 확장 프로그램이 설치되었습니다.")
        print("10초 후 브라우저를 종료합니다...")
        time.sleep(10)
        driver.quit()
    else:
        print("브라우저 생성 실패")