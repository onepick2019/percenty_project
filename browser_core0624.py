# -*- coding: utf-8 -*-
"""
브라우저 환경 설정 모듈

이 모듈은 퍼센티 자동화에 필요한 브라우저 환경을 설정합니다.
웹드라이버 초기화, 브라우저 창 크기 및 위치 조정, 전체화면 전환,
좌표 변환 등의 기능을 제공합니다.
"""

import os
import time
import logging
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
# webdriver_manager 제거 - Selenium 4.6+ 자동 드라이버 관리 사용
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

class BrowserCore:
    """브라우저 핵심 기능 클래스"""
    
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
        logging.info("===== 브라우저 설정 시작 =====")
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
            
            # 퍼센티 확장 프로그램 자동 로드 (CRX 파일 우선) - 주석처리됨
            # try:
            #     extension_dir = os.path.join(os.path.dirname(__file__), "percenty_extension")
            #     
            #     # 방법 1: CRX 파일 사용 (우선) - 정상적인 ID와 출처를 가짐
            #     extension_path = os.path.join(extension_dir, "percenty_extension_with_key.crx")
            #     if os.path.exists(extension_path):
            #         chrome_options.add_extension(extension_path)
            #         logging.info(f"퍼센티 확장 프로그램 로드 (CRX): {extension_path}")
            #     else:
            #         # 방법 2: 대체 CRX 파일 시도
            #         alt_extension_path = os.path.join(extension_dir, "percenty_webstore.crx")
            #         if os.path.exists(alt_extension_path):
            #             chrome_options.add_extension(alt_extension_path)
            #             logging.info(f"퍼센티 확장 프로그램 로드 (대체 CRX): {alt_extension_path}")
            #         else:
            #             # 방법 3: 압축 해제된 확장 프로그램 디렉토리 사용 (최후 수단)
            #             manifest_path = os.path.join(extension_dir, "manifest.json")
            #             if os.path.exists(manifest_path):
            #                 chrome_options.add_argument(f"--load-extension={extension_dir}")
            #                 logging.info(f"퍼센티 확장 프로그램 로드 (디렉토리): {extension_dir}")
            #                 logging.warning("압축 해제된 확장 프로그램을 사용합니다. ID 및 출처 문제가 발생할 수 있습니다.")
            #             else:
            #                 logging.warning("퍼센티 확장 프로그램을 찾을 수 없습니다. 확장 프로그램 없이 진행합니다.")
            # except Exception as e:
            #     logging.error(f"퍼센티 확장 프로그램 로드 실패: {e}")
            #     logging.warning("확장 프로그램 없이 브라우저를 시작합니다.")
            logging.info("퍼센티 확장 프로그램 자동 로드가 비활성화되었습니다. 수동 설치를 사용합니다.")
            
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
            
            # Selenium 4.6+ 자동 드라이버 관리 사용
            # Selenium Manager가 자동으로 chromedriver를 다운로드하고 관리함
            try:
                logging.info("Selenium Manager를 사용하여 Chrome 드라이버 자동 설정 시작")
                import time
                import signal
                
                start_time = time.time()
                
                # 타임아웃 설정 (30초)
                def timeout_handler(signum, frame):
                    raise TimeoutError("Chrome 드라이버 생성 타임아웃 (30초)")
                
                # Windows에서는 signal.alarm이 지원되지 않으므로 다른 방법 사용
                logging.info("Chrome 드라이버 생성 시도 중...")
                
                # Chrome 드라이버 생성 시도 (threading을 사용한 타임아웃)
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
                
                # 30초 타임아웃으로 대기 (GUI 모드에서 더 긴 시간 필요)
                driver_thread.join(timeout=30)
                
                if driver_thread.is_alive():
                    logging.error("Chrome 드라이버 생성이 30초 내에 완료되지 않았습니다.")
                    raise TimeoutError("Chrome 드라이버 생성 타임아웃 (30초) - Chrome이 설치되어 있는지 확인하세요")
                
                # 결과 확인
                if not exception_queue.empty():
                    raise exception_queue.get()
                
                if not result_queue.empty():
                    self.driver = result_queue.get()
                    creation_time = time.time() - start_time
                    logging.info(f"Chrome 드라이버 생성 완료 (소요시간: {creation_time:.2f}초)")
                else:
                    raise Exception("Chrome 드라이버 생성 실패: 알 수 없는 오류")
            except Exception as e:
                logging.warning(f"Selenium Manager 실패, 수동 경로 시도: {e}")
                # Selenium Manager 실패 시 수동으로 경로 지정
                import shutil
                chromedriver_path = shutil.which('chromedriver')
                if chromedriver_path:
                    logging.info(f"시스템 PATH에서 chromedriver 발견: {chromedriver_path}")
                    service = Service(chromedriver_path)
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                else:
                    # 일반적인 설치 경로들 시도
                    possible_paths = [
                        r"C:\Program Files\Google\Chrome\Application\chromedriver.exe",
                        r"C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe",
                        r"C:\Windows\System32\chromedriver.exe",
                        "chromedriver.exe"  # 현재 디렉토리
                    ]
                    
                    driver_found = False
                    for path in possible_paths:
                        try:
                            if os.path.exists(path):
                                logging.info(f"chromedriver 경로 시도: {path}")
                                service = Service(path)
                                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                                driver_found = True
                                break
                        except Exception as path_error:
                            logging.debug(f"경로 {path} 실패: {path_error}")
                            continue
                    
                    if not driver_found:
                        error_msg = (
                            "Chrome 드라이버를 찾을 수 없습니다.\n"
                            "해결 방법:\n"
                            "1. Chrome 브라우저가 설치되어 있는지 확인\n"
                            "2. 인터넷 연결 확인 (Selenium Manager가 자동 다운로드)\n"
                            "3. 방화벽/보안 프로그램이 차단하는지 확인\n"
                            "4. 관리자 권한으로 실행 시도"
                        )
                        logging.error(error_msg)
                        raise Exception(error_msg)
            
            # 초기 창 크기 및 위치 로깅
            logging.info("브라우저 창 크기 및 위치 정보 수집 시작")
            try:
                window_size = self.driver.get_window_size()
                window_position = self.driver.get_window_position()
                logging.info(f"초기 창 크기: {window_size['width']}x{window_size['height']}")
                logging.info(f"초기 창 위치: x={window_position['x']}, y={window_position['y']}")
            except Exception as e:
                logging.error(f"창 크기/위치 정보 수집 실패: {e}")
                raise
            
            # 브라우저 전체화면으로 전환 (헤드리스 모드 제외)
            if not headless:
                logging.info("브라우저 전체화면으로 전환 시도")
                try:
                    self.driver.maximize_window()
                    logging.info("maximize_window() 호출 완료")
                    time.sleep(1)  # 전체화면 전환 대기 (2초에서 1초로 단축)
                    logging.info("전체화면 전환 대기 완료")
                    
                    # 전체화면 후 창 크기 및 위치 로깅
                    window_size = self.driver.get_window_size()
                    window_position = self.driver.get_window_position()
                    logging.info(f"전체화면 후 창 크기: {window_size['width']}x{window_size['height']}")
                    logging.info(f"전체화면 후 창 위치: x={window_position['x']}, y={window_position['y']}")
                except Exception as e:
                    logging.warning(f"전체화면 전환 실패 (계속 진행): {e}")
                    # 전체화면 전환 실패해도 브라우저는 사용 가능하므로 계속 진행
            else:
                logging.info("헤드리스 모드: maximize_window() 건너뛰기 (설정된 크기 유지)")
            
            # JavaScript로 브라우저 내부 크기 가져오기
            logging.info("JavaScript를 사용하여 브라우저 내부 크기 측정 시작")
            try:
                self.inner_width = self.driver.execute_script("return window.innerWidth")
                logging.info(f"innerWidth 측정 완료: {self.inner_width}")
                
                self.inner_height = self.driver.execute_script("return window.innerHeight")
                logging.info(f"innerHeight 측정 완료: {self.inner_height}")
                
                logging.info(f"브라우저 내부 크기: {self.inner_width}x{self.inner_height}")
                
                # JavaScript 실행 가능 여부 확인
                js_enabled = self.driver.execute_script("return true")
                logging.info(f"JavaScript 실행 가능: {js_enabled}")
            except Exception as e:
                logging.error(f"JavaScript 실행 실패: {e}")
                raise
            
            logging.info("===== 브라우저 설정 완료 =====")
            return True
            
        except Exception as e:
            logging.error(f"브라우저 설정 중 오류 발생: {e}")
            logging.error(traceback.format_exc())
            if self.driver:
                self.driver.quit()
                self.driver = None
            return False
            
    def convert_to_relative_coordinates(self, absolute_x, absolute_y):
        """
        절대좌표를 해상도에 따른 상대좌표로 변환
        
        해상도와 관계없이 일관된 사용자 경험을 제공하기 위해 단일 변환 공식 사용:
        relative_x = int(inner_width * (absolute_x / 1920))
        relative_y = int(inner_height * (absolute_y / 1080))
        
        Args:
            absolute_x (int): 절대 X 좌표 (1920x1080 해상도 기준)
            absolute_y (int): 절대 Y 좌표 (1920x1080 해상도 기준)
            
        Returns:
            tuple: 현재 브라우저 상태에 맞는 (상대 X 좌표, 상대 Y 좌표)
        """
        if not self.inner_width or not self.inner_height:
            # 브라우저 내부 크기를 가져올 수 없는 경우, 원래 좌표 반환
            logging.warning("브라우저 내부 크기를 가져올 수 없어 원래 좌표를 사용합니다.")
            return (absolute_x, absolute_y)
            
        # 기본 변환 공식
        relative_x = int(self.inner_width * (absolute_x / ORIGINAL_WIDTH))
        relative_y = int(self.inner_height * (absolute_y / ORIGINAL_HEIGHT))
        
        logging.info(f"좌표 변환: ({absolute_x}, {absolute_y}) -> ({relative_x}, {relative_y})")
        return (relative_x, relative_y)
        
    def click_at_coordinates(self, x, y, coordinate_key=None):
        """
        지정된 좌표에서 클릭 수행 - JavaScript를 활용한 상대좌표 기반 클릭
        
        정확한 클릭을 위해 다음 순서로 진행됨:
        1. 좌표를 현재 브라우저 크기에 맞게 변환
        2. JavaScript를 사용하여 해당 위치에서 클릭 수행
        3. 클릭된 요소 정보 로깅
        
        Args:
            x (int): 클릭할 X 좌표 (절대좌표, 1920x1080 기준)
            y (int): 클릭할 Y 좌표 (절대좌표, 1920x1080 기준)
            coordinate_key (str): 좌표 임의 식별자 (로그 기록용, 기본값: None)
            
        Returns:
            bool: 클릭 성공 여부
        """
        try:
            # 좌표 출처 로깅 (식별자가 제공된 경우)
            if coordinate_key:
                logging.info(f"{coordinate_key} 좌표 클릭 시도: ({x}, {y})")
            
            # 좌표 변환
            rel_x, rel_y = self.convert_to_relative_coordinates(x, y)
            
            # JavaScript를 사용하여 클릭 수행
            js_click_script = """
                function simulateClick(x, y) {
                    var element = document.elementFromPoint(x, y);
                    if (element) {
                        var rect = element.getBoundingClientRect();
                        var evt = new MouseEvent('click', {
                            view: window,
                            bubbles: true,
                            cancelable: true,
                            clientX: x,
                            clientY: y
                        });
                        element.dispatchEvent(evt);
                        return {
                            tag: element.tagName,
                            text: element.textContent.trim(),
                            id: element.id,
                            class: element.className
                        };
                    }
                    return null;
                }
                return simulateClick(arguments[0], arguments[1]);
            """
            
            clicked_element = self.driver.execute_script(js_click_script, rel_x, rel_y)
            
            if clicked_element:
                logging.info(f"JavaScript로 클릭 성공: ({rel_x}, {rel_y})")
                logging.info(f"클릭된 요소: [{clicked_element['tag']}] '{clicked_element['text']}'" + 
                         (f" ID: {clicked_element['id']}" if clicked_element['id'] else "") + 
                         (f" CLASS: {clicked_element['class']}" if clicked_element['class'] else ""))
                return True
            else:
                logging.warning(f"지정된 좌표 ({rel_x}, {rel_y})에서 요소를 찾을 수 없습니다.")
                return False
                
        except Exception as e:
            logging.error(f"JavaScript 클릭 중 오류 발생: {e}")
            logging.error(traceback.format_exc())
            return False
            
    def create_browser(self, headless=False):
        """
        브라우저 생성 및 설정
        
        Args:
            headless (bool): 헤드리스 모드 사용 여부
            
        Returns:
            WebDriver: 생성된 웹드라이버 인스턴스
        """
        if self.setup_driver(headless=headless):
            return self.driver
        else:
            raise Exception("브라우저 생성에 실패했습니다.")
    
    def close_driver(self):
        """웹드라이버 종료"""
        if self.driver:
            try:
                self.driver.quit()
                logging.info("웹드라이버가 종료되었습니다.")
            except Exception as e:
                logging.error(f"웹드라이버 종료 중 오류 발생: {e}")

    def open_url(self, url, max_attempts=3, retry_delay=5):
        """
        URL 열기 (재시도 로직 포함)
        
        Args:
            url (str): 열려는 URL
            max_attempts (int): 최대 시도 횟수
            retry_delay (int): 재시도 전 대기 시간(초)
            
        Returns:
            bool: URL 열기 성공 여부
        """
        for attempt in range(1, max_attempts + 1):
            try:
                logging.info(f"{url} 열기 (시도 {attempt}/{max_attempts})")
                self.driver.get(url)
                return True
            except Exception as e:
                logging.error(f"URL 열기 실패 (시도 {attempt}/{max_attempts}): {e}")
                if attempt < max_attempts:
                    logging.info(f"{retry_delay}초 후 재시도합니다...")
                    time.sleep(retry_delay)
                else:
                    logging.error(f"최대 시도 횟수({max_attempts})를 초과했습니다. URL 열기를 중단합니다.")
                    return False
        return False
