# -*- coding: utf-8 -*-
"""
퍼센티 로그인 자동화 모듈

이 모듈은 퍼센티 웹사이트 로그인을 자동화합니다.
사용자가 Excel 파일에서 계정을 선택하고 자동으로 로그인합니다.
핵심 브라우저 설정 및 모달창 처리를 위해 browser_core와 modal_core 모듈을 활용합니다.
"""

import os
import time
import logging
import traceback
import sys
import tkinter as tk
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    ElementNotInteractableException, 
    StaleElementReferenceException
)

# 계정 관리자 가져오기
from account_manager import AccountManager

# 좌표 관리 시스템 가져오기
from coordinates.coordinates_all import *

# DOM 선택자 가져오기
from dom_selectors import LOGIN_SELECTORS

# 시간 지연 관련 모듈 가져오기
from timesleep import (
    PAGE_LOAD, BUTTON_CLICK, MODAL, CHECKBOX,
    sleep_with_logging, wait_after_typing, wait_after_modal_close, wait_after_login, wait_after_error
)

# 메뉴 클릭 및 모달창 관리 모듈
from menu_clicks import click_menu_using_relative_coordinates
from close_modal_by_selector import close_modal_with_selectors

# 시간 지연 관리 모듈
from timesleep import *

# DOM 관련 모듈
from dom_selectors import LOGIN_SELECTORS, MODAL_SELECTORS
from dom_utils import smart_click, highlight_element

# 퍼센티 유틸리티 모듈
from percenty_utils import hide_channel_talk_and_modals

# UI 요소 가져오기
from ui_elements import UI_ELEMENTS

# 핵심 코어 모듈 가져오기
from browser_core import BrowserCore
from modal_core import ModalCore

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 상수 정의
PERCENTY_URL = "https://www.percenty.co.kr/signin"
MAX_LOGIN_ATTEMPTS = 3
RETRY_DELAY = EXTERNAL["RETRY_DELAY"]  # 재시도 전 대기 시간

class PercentyLogin:
    """퍼센티 로그인 클래스 (창 모드)"""
    
    def __init__(self, driver=None, account=None, window_width=None, window_height=None, window_x=None, window_y=None):
        """
        초기화
        
        Args:
            driver: WebDriver 인스턴스 (새로운 아키텍처 호환용)
            account (dict): 로그인할 계정 정보
            window_width (int): 브라우저 창 너비 (기본값: 화면 너비의 절반)
            window_height (int): 브라우저 창 높이 (기본값: 화면 높이)
            window_x (int): 브라우저 창 X 위치 (기본값: 화면 오른쪽 절반)
            window_y (int): 브라우저 창 Y 위치 (기본값: 0)
        """
        logging.info("=== PercentyLogin __init__ 시작 ===")
        logging.info(f"전달받은 driver: {driver is not None}")
        logging.info(f"전달받은 account: {account}")
        
        # 계정 정보 설정
        self.account = account
        self.driver = driver
        logging.info("기본 속성 설정 완료")
        
        # 화면 해상도 확인 (안전한 방법 사용)
        logging.info("화면 해상도 확인 시작")
        try:
            logging.info("tkinter import 시작")
            import tkinter as tk
            logging.info("tkinter import 완료")
            
            logging.info("tkinter root 생성 시작")
            root = tk.Tk()
            logging.info("tkinter root 생성 완료")
            
            logging.info("tkinter root withdraw 시작")
            root.withdraw()  # 창을 숨김
            logging.info("tkinter root withdraw 완료")
            
            logging.info("화면 크기 측정 시작")
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            logging.info(f"화면 크기 측정 완료: {screen_width}x{screen_height}")
            
            logging.info("tkinter root destroy 시작")
            root.destroy()
            logging.info("tkinter root destroy 완료")
            
            logging.info(f"tkinter로 화면 해상도 확인 성공: {screen_width}x{screen_height}")
        except Exception as e:
            logging.warning(f"tkinter 화면 해상도 확인 실패, 기본값 사용: {e}")
            # 기본값 사용
            screen_width = 1920
            screen_height = 1080
        
        # 기본 창 크기 및 위치 설정 (전체 화면 너비 사용)
        logging.info("창 크기 및 위치 설정 시작")
        self.window_width = window_width if window_width else 1920
        self.window_height = window_height if window_height else screen_height
        self.window_x = window_x if window_x is not None else 0
        self.window_y = window_y if window_y is not None else 0
        
        logging.info(f"화면 해상도: {screen_width}x{screen_height}")
        logging.info(f"브라우저 창 크기: {self.window_width}x{self.window_height}")
        logging.info(f"브라우저 창 위치: x={self.window_x}, y={self.window_y}")
        
        # 브라우저 코어 및 모달 코어 초기화
        logging.info("브라우저 코어 및 모달 코어 초기화 시작")
        self.browser_core = None
        self.modal_core = None
        logging.info("기본 코어 속성 설정 완료")
        
        # 외부에서 driver가 전달된 경우 모달 코어 초기화
        if self.driver:
            logging.info("driver가 전달되어 ModalCore 초기화 시작")
            from modal_core import ModalCore
            logging.info("ModalCore import 완료")
            self.modal_core = ModalCore(self.driver)
            logging.info("ModalCore 초기화 완료")
        
        logging.info("=== PercentyLogin __init__ 완료 ===")
    
    def setup_driver(self):
        """
        웹드라이버 설정 및 브라우저 창 전체화면 전환
        
        Returns:
            bool: 설정 성공 여부
        """
        try:
            # BrowserCore 코어 모듈 초기화
            self.browser_core = BrowserCore(
                window_width=self.window_width,
                window_height=self.window_height,
                window_x=self.window_x,
                window_y=self.window_y
            )
            
            # 브라우저 코어 설정
            if not self.browser_core.setup_driver():
                logging.error("브라우저 코어 설정 실패")
                return False
                
            # 드라이버 참조 저장
            self.driver = self.browser_core.driver
            
            # 모달 코어 모듈 초기화
            self.modal_core = ModalCore(self.driver)
            
            return True
        except Exception as e:
            logging.error(f"웹드라이버 설정 중 오류 발생: {e}")
            logging.error(traceback.format_exc())
            return False
    
    def convert_to_relative_coordinates(self, absolute_x, absolute_y):
        """
        절대좌표를 해상도에 따른 상대좌표로 변환
        
        해상도와 관계없이 일관된 사용자 경험을 제공하기 위해 단일 변환 공식 사용:
        relative_x = int(inner_width * (absolute_x / 1920))
        relative_y = int(inner_height * (absolute_y / 1080))
        
        일부 UI 요소(비밀번호 저장 모달창 닫기 버튼 등)는 특별 처리가 필요합니다.
        
        Args:
            absolute_x (int): 1920x1080 해상도 기준 절대 X 좌표
            absolute_y (int): 1920x1080 해상도 기준 절대 Y 좌표
            
        Returns:
            tuple: 현재 브라우저 상태에 맞는 (상대 X 좌표, 상대 Y 좌표)
        """
        try:
            # 브라우저 내부 크기 가져오기
            inner_width = self.driver.execute_script("return window.innerWidth;")
            inner_height = self.driver.execute_script("return window.innerHeight;")
            
            # 통일된 상대 좌표 계산 공식 - 모든 좌표 변환에 적용
            relative_x = int(inner_width * (absolute_x / 1920))  # 기준 해상도 1920 기준 계산
            relative_y = int(inner_height * (absolute_y / 1080))  # 기준 해상도 1080 기준 계산
            
            logging.info(f"좌표 변환: ({absolute_x}, {absolute_y}) -> ({relative_x}, {relative_y})")
            
            # 비밀번호 저장 모달창 닫기 버튼은 예외 처리 (크롬 시스템 UI 영역에 있어 특별좌표 변환이 되지 않음)
            # 비밀번호 저장 모달창 닫기 버튼 좌표: (1801, 110)
            password_save_modal_close_x, password_save_modal_close_y = NOTIFICATION["PASSWORD_SAVE_MODAL_CLOSE"]
            if absolute_x == password_save_modal_close_x and absolute_y == password_save_modal_close_y:
                logging.info("비밀번호 저장 모달창 닫기 버튼은 원래 절대좌표 그대로 사용")
                # 원래 절대좌표 그대로 반환
                return absolute_x, absolute_y
            
            # 나머지 모든 좌표는 특별 좌표 처리
            
            # 이메일 입력 필드
            if absolute_x == LOGIN["USERNAME_FIELD"][0] and absolute_y == LOGIN["USERNAME_FIELD"][1]:
                logging.info("이메일 입력 필드에 대한 특별 좌표 변환 적용")
                # 이메일 필드는 중앙에 위치하도록 조정
                relative_x = int(inner_width / 2)
                relative_y = int(inner_height * 0.38)  # 화면 높이의 약 38% 위치
                logging.info(f"이메일 필드 원래 좌표: ({absolute_x}, {absolute_y}) -> ({relative_x}, {relative_y})")
                return relative_x, relative_y
            
            # 비밀번호 입력 필드
            if absolute_x == LOGIN["PASSWORD_FIELD"][0] and absolute_y == LOGIN["PASSWORD_FIELD"][1]:
                logging.info("비밀번호 입력 필드에 대한 특별 좌표 변환 적용")
                # 비밀번호 필드는 중앙에 위치하도록 조정
                relative_x = int(inner_width / 2)
                relative_y = int(inner_height * 0.48)  # 화면 높이의 약 48% 위치
                logging.info(f"비밀번호 필드 원래 좌표: ({absolute_x}, {absolute_y}) -> ({relative_x}, {relative_y})")
                return relative_x, relative_y
                
            # 로그인 버튼
            if absolute_x == LOGIN["LOGIN_BUTTON"][0] and absolute_y == LOGIN["LOGIN_BUTTON"][1]:
                logging.info("로그인 버튼에 대한 특별 좌표 변환 적용")
                # 로그인 버튼은 중앙에 위치하도록 조정
                relative_x = int(inner_width / 2)
                relative_y = int(inner_height * 0.58)  # 화면 높이의 약 58% 위치
                logging.info(f"로그인 버튼 원래 좌표: ({absolute_x}, {absolute_y}) -> ({relative_x}, {relative_y})")
                return relative_x, relative_y
            
            # 로그인 모달창 닫기 버튼 (원래 좌표: 811, 795)
            login_modal_close_x, login_modal_close_y = NOTIFICATION["LOGIN_MODAL_CLOSE"]
            if absolute_x == login_modal_close_x and absolute_y == login_modal_close_y:
                logging.info("로그인 모달창 닫기 버튼에 대한 특별 좌표 변환 적용")
                # 화면 중앙 하단에 위치
                relative_x = int(inner_width / 2)
                relative_y = int(inner_height * 0.74)  # 브라우저 높이의 74% 위치
                logging.info(f"로그인 모달창 닫기 버튼 원래 좌표: ({absolute_x}, {absolute_y}) -> ({relative_x}, {relative_y})")
                return relative_x, relative_y
            
            # 자동화 알림 닫기 버튼 (원래 좌표: 1118, 107)
            notification_close_x, notification_close_y = NOTIFICATION["CLOSE"]
            if absolute_x == notification_close_x and absolute_y == notification_close_y:
                logging.info("자동화 알림 닫기 버튼에 대한 특별 좌표 변환 적용")
                # 화면 오른쪽 상단에 위치
                relative_x = int(inner_width / 2)
                relative_y = int(inner_height * 0.10)  # 브라우저 높이의 10% 위치
                logging.info(f"자동화 알림 닫기 버튼 원래 좌표: ({absolute_x}, {absolute_y}) -> ({relative_x}, {relative_y})")
                return relative_x, relative_y
            
            # 퍼센티 홈 버튼 (정확한 좌표만 일치하도록 확인)
            home_x, home_y = MENU["HOME"]
            if absolute_x == home_x and absolute_y == home_y:
                logging.info("퍼센티 홈 버튼에 대한 특별 좌표 변환 적용")
                # 화면 좌측 AI 소싱 메뉴 위치로 조정
                relative_x = int(inner_width * 0.05)  # 브라우저 너비의 5% 위치
                relative_y = int(inner_height * 0.3)  # 브라우저 높이의 30% 위치
                logging.info(f"퍼센티 홈 버튼 원래 좌표: ({absolute_x}, {absolute_y}) -> ({relative_x}, {relative_y})")
                return relative_x, relative_y
            
            # 그 외 모든 좌표도 특별 좌표 처리 (비율 기반으로 화면 중앙에 배치)
            # 아이디 저장 체크박스 좌표 (테스트로 발견한 최적 변환 공식 적용)
            saveid_x, saveid_y = LOGIN["LOGIN_SAVEID"]
            if absolute_x == saveid_x and absolute_y == saveid_y:
                logging.info("아이디 저장 체크박스에 대한 최적 변환 공식 적용")
                # 테스트 결과 얻은 최적 변환 공식 적용
                relative_x = int(inner_width * 0.4057)  # 테스트로 발견한 최적 비율
                relative_y = int(inner_height * 0.5053)  # 테스트로 발견한 최적 비율
                logging.info(f"체크박스 원래 좌표: ({absolute_x}, {absolute_y}) -> ({relative_x}, {relative_y})")
                return relative_x, relative_y
            
            # X 좌표는 화면 비율에 따라 적절히 조정
            x_percent = absolute_x / ORIGINAL_WIDTH
            relative_x = int(inner_width * x_percent)
            
            # Y 좌표는 화면 비율에 따라 적절히 조정
            y_percent = absolute_y / ORIGINAL_HEIGHT
            relative_y = int(inner_height * y_percent)
            
            logging.info(f"좌표 ({absolute_x}, {absolute_y})를 특별좌표 ({relative_x}, {relative_y})로 변환 (비율: {x_percent:.3f}x{y_percent:.3f})")
            
            return relative_x, relative_y
        except Exception as e:
            logging.error(f"상대좌표 변환 중 오류 발생: {e}")
            # 오류 발생 시 원래 좌표 반환
            return absolute_x, absolute_y
    
    def click_at_coordinates(self, x, y, coordinate_key=None):
        """
        지정된 좌표에서 클릭 수행 - JavaScript를 활용한 상대좌표 기반 클릭
        
        정확한 클릭을 위해 다음 순서로 진행됨:
        1. 절대좌표를 상대좌표로 변환 (convert_to_relative_coordinates 함수 활용)
        2. 해당 요소에 대한 특별 좌표 변환이 필요한 경우 추가 조정
        3. JavaScript를 통해 해당 위치를 클릭
        4. 클릭된 요소의 정보를 로그로 기록
        
        Args:
            x (int): 1920x1080 해상도 기준 절대 X 좌표
            y (int): 1920x1080 해상도 기준 절대 Y 좌표
            coordinate_key (str): 좌표 임의 식별자 (로그 기록용, 기본값: None)
            
        Returns:
            bool: 클릭 성공 여부
        """
        try:
            # 클릭할 좌표 로깅
            if coordinate_key:
                logging.info(f"{coordinate_key} 좌표 클릭 시도: ({x}, {y})")
            else:
                logging.info(f"좌표 클릭 시도: ({x}, {y})")
                
            # 통일된 좌표 변환 공식 사용
            relative_x, relative_y = self.convert_to_relative_coordinates(x, y)
            
            # JavaScript를 사용하여 좌표 클릭
            click_script = """
                try {
                    var elem = document.elementFromPoint(arguments[0], arguments[1]);
                    if (elem) {
                        elem.click();
                        return {
                            clicked: true,
                            tagName: elem.tagName,
                            text: elem.textContent.trim(),
                            id: elem.id || '',
                            class: elem.className || ''
                        };
                    }
                    return { clicked: false };
                } catch(e) {
                    return { clicked: false, error: e.message };
                }
            """
            
            # JavaScript로 클릭 실행
            result = self.driver.execute_script(click_script, relative_x, relative_y)
            
            if result.get('clicked', False):
                elem_info = f"[{result.get('tagName', '')}] '{result.get('text', '')}'" 
                if result.get('id'):
                    elem_info += f" ID: {result.get('id')}"
                if result.get('class'):
                    elem_info += f" CLASS: {result.get('class')}"
                    
                logging.info(f"JavaScript로 클릭 성공: ({relative_x}, {relative_y})")
                logging.info(f"클릭된 요소: {elem_info}")
                return True
            else:
                logging.warning("JavaScript 클릭 실패, ActionChains 시도")
                
                # JavaScript 실패 시 ActionChains 사용
                try:
                    actions = ActionChains(self.driver)
                    actions.move_to_element_with_offset(self.driver.find_element(By.TAG_NAME, "body"), relative_x, relative_y)
                    actions.click().perform()
                    logging.info(f"ActionChains로 클릭 성공: ({relative_x}, {relative_y})")
                    return True
                except Exception as action_error:
                    logging.error(f"ActionChains 클릭 실패: {action_error}")
                    return False
                    
        except Exception as e:
            logging.error(f"클릭 중 예외 발생: {e}")
            return False
    
    def close_notification(self):
        """
        자동화 알림 닫기 - ModalCore 모듈 활용
        
        Returns:
            bool: 알림 닫기 성공 여부
        """
        # ModalCore의 close_notification 메서드 활용
        return self.modal_core.close_notification()
    
    def close_password_save_modal(self):
        """
        비밀번호를 저장하시겠습니까 모달창 닫기 - ModalCore 모듈 활용
        
        Returns:
            dict: 처리 결과 정보
        """
        # ModalCore의 close_password_save_modal 메서드 활용
        return self.modal_core.close_password_save_modal()
    
    def close_login_modal(self):
        """
        로그인 후 나타나는 모달창 차단 - ModalCore 모듈 활용
        
        Returns:
            dict: 처리 결과 정보
        """
        # ModalCore의 close_login_modal 메서드 활용
        return self.modal_core.close_login_modal()

    def login_percenty(self, account_info):
        """
        퍼센티 로그인 수행 (새로운 아키텍처 호환)
        
        Args:
            account_info (dict): 계정 정보 {'email': str, 'password': str}
            
        Returns:
            bool: 로그인 성공 여부
        """
        # 계정 정보 설정
        self.account = {
            'id': account_info.get('email', ''),
            'password': account_info.get('password', '')
        }
        
        # 기존 login 메서드 호출
        return self.login()
    
    def login(self, attempt=1):
        """
        로그인 수행 - 핵심 코어 모듈 활용

        Args:
            attempt (int): 현재 시도 횟수 (기본값: 1)

        Returns:
            bool: 로그인 성공 여부
        """
        try:
            # 최대 시도 횟수 초과 시 종료
            if attempt > MAX_LOGIN_ATTEMPTS:
                logging.error(f"최대 시도 횟수({MAX_LOGIN_ATTEMPTS}회)를 초과하여 로그인을 중단합니다.")
                return False
            
            # 로그인 상태 체크 - 이미 로그인된 경우 모달창 처리만 수행
            try:
                current_url = self.driver.current_url
                if "/signin" not in current_url and "percenty.co.kr" in current_url:
                    logging.info(f"이미 로그인된 상태입니다. 현재 URL: {current_url}")
                    logging.info("모달창 처리만 수행합니다.")
                    
                    # 모달창 처리만 수행
                    self.modal_core.close_notification()
                    self.modal_core.close_password_save_modal()
                    sleep_with_logging(0.5, "비밀번호 저장 모달창 닫기 후")
                    self.modal_core.close_login_modal()
                    wait_after_modal_close()
                    
                    logging.info("로그인 상태 확인 및 모달창 처리 완료")
                    return True
            except Exception as e:
                logging.warning(f"로그인 상태 체크 중 오류 (계속 진행): {e}")
                
            # 퍼센티 로그인 페이지 열기
            logging.info(f"퍼센티 로그인 페이지 열기: {PERCENTY_URL} (시도 {attempt}/{MAX_LOGIN_ATTEMPTS})")
            
            # 브라우저 코어가 있으면 사용, 없으면 직접 driver 사용
            if self.browser_core:
                if not self.browser_core.open_url(PERCENTY_URL):
                    logging.error("퍼센티 로그인 페이지 열기 실패")
                    return False
            elif self.driver:
                try:
                    self.driver.get(PERCENTY_URL)
                    logging.info(f"직접 driver로 페이지 열기 성공: {PERCENTY_URL}")
                except Exception as e:
                    logging.error(f"직접 driver로 페이지 열기 실패: {e}")
                    return False
            else:
                logging.error("브라우저 코어와 driver 모두 없습니다")
                return False
            
            # 페이지 로드 대기
            sleep_with_logging(PAGE_LOAD["INITIAL"], "로그인 페이지 로드 대기")
            
            # 모달 코어를 활용하여 자동화 알림 닫기
            self.modal_core.close_notification()
            
            # 비밀번호 저장 모달창 처리
            self.modal_core.close_password_save_modal()

            # 페이지 로딩 대기
            logging.info("페이지 로딩 대기")
            wait_for_page_load()

            # 아이디 입력 - smart_click 사용
            logging.info(f"아이디 입력: {self.account['id']}")
            
            # UI 요소와 smart_click 함수를 사용하여 하이브리드 방식 적용
            username_field_element = UI_ELEMENTS.get("LOGIN_EMAIL_FIELD")  # USERNAME_FIELD 대신 LOGIN_EMAIL_FIELD 사용
            
            # 요소가 None인 경우 수동으로 정의
            if username_field_element is None:
                logging.warning("UI_ELEMENTS에서 LOGIN_EMAIL_FIELD를 찾을 수 없습니다. 수동으로 정의합니다.")
                username_field_element = {
                    "name": "이메일/아이디 입력 필드",
                    "dom_selector": "//input[@id='email']",
                    "selector_type": "xpath",
                    "coordinates": LOGIN["USERNAME_FIELD"],
                    "fallback_order": ["dom", "coordinates"]
                }
            
            email_result = smart_click(
                self.driver, 
                element_info=username_field_element, 
                browser_core=self.browser_core,
                click_type="input",
                input_text=self.account['id']
            )
            
            if email_result.get("success"):
                logging.info(f"smart_click으로 아이디 필드 입력 성공: {email_result.get('method', 'unknown')}")
            else:
                # 실패 시 기존 방법으로 폴백
                logging.warning(f"smart_click 실패, 기존 방법으로 시도: {email_result.get('error', 'unknown')}")
                try:
                    username_field = self.driver.find_element(By.CSS_SELECTOR, "input[type='text']")
                    username_field.clear()
                    username_field.send_keys(self.account['id'])
                    logging.info("CSS 선택자로 아이디 필드를 찾아 직접 입력했습니다.")
                except Exception as e2:
                    logging.warning(f"CSS 선택자로도 아이디 필드를 찾지 못했습니다: {e2}")
                    # 좌표 기반 클릭
                    username_field_x, username_field_y = LOGIN["USERNAME_FIELD"]
                    self.browser_core.click_at_coordinates(username_field_x, username_field_y, "USERNAME_FIELD")
                    self.driver.execute_script(f"document.querySelector('input[type=\"text\"]').value = '{self.account['id']}';")
                    logging.info("좌표 클릭 및 JavaScript를 사용하여 아이디 입력")

            wait_after_typing()  # 텍스트 입력 후 대기

            # 비밀번호 입력 - smart_click 사용
            logging.info("비밀번호 입력 시도")
            
            # UI 요소와 smart_click 함수를 사용하여 하이브리드 방식 적용
            password_field_element = UI_ELEMENTS.get("LOGIN_PASSWORD_FIELD")
            
            # 요소가 None인 경우 수동으로 정의
            if password_field_element is None:
                logging.warning("UI_ELEMENTS에서 LOGIN_PASSWORD_FIELD를 찾을 수 없습니다. 수동으로 정의합니다.")
                password_field_element = {
                    "name": "비밀번호 입력 필드",
                    "dom_selector": "//input[@id='password']",
                    "selector_type": "xpath",
                    "coordinates": LOGIN["PASSWORD_FIELD"],
                    "fallback_order": ["dom", "coordinates"]
                }
            
            password_result = smart_click(
                self.driver, 
                element_info=password_field_element, 
                browser_core=self.browser_core,
                click_type="input",
                input_text=self.account['password']
            )
            
            if password_result.get("success"):
                logging.info(f"smart_click으로 비밀번호 필드 입력 성공: {password_result.get('method', 'unknown')}")
            else:
                # 실패 시 기존 방법으로 폴백
                logging.warning(f"smart_click 실패, 기존 방법으로 시도: {password_result.get('error', 'unknown')}")
                try:
                    # 1. ID로 요소 찾아서 입력
                    password_field = WebDriverWait(self.driver, DELAY_STANDARD).until(
                        EC.presence_of_element_located((By.ID, "password"))
                    )
                    password_field.clear()
                    password_field.send_keys(self.account['password'])
                    logging.info("ID 선택자로 비밀번호 입력 완료")
                except Exception as e:
                    logging.warning(f"ID로 비밀번호 필드를 찾지 못했습니다: {e}")
                    # 2. JavaScript 메서드로 입력
                    js_script = f"document.querySelector('input[type=\"password\"]').value = '{self.account['password']}';" 
                    js_script += "document.querySelector('input[type=\"password\"]').dispatchEvent(new Event('input', { bubbles: true }));"
                    js_script += "document.querySelector('input[type=\"password\"]').dispatchEvent(new Event('change', { bubbles: true }));"
                    self.driver.execute_script(js_script)
                    logging.info("JavaScript를 사용하여 비밀번호 입력 및 이벤트 발생")

            wait_after_typing()  # 텍스트 입력 후 잠시 대기

            # 아이디 저장 체크박스 주석 처리됨 - 건너뚼
            logging.info("아이디 저장 체크박스 주석 처리됨 - 건너뚼")
            
            # 로그인 버튼 클릭 - smart_click 사용
            logging.info("로그인 버튼 클릭 시도 (smart_click 사용)")
            
            # UI 요소와 smart_click 함수를 사용하여 하이브리드 방식 적용
            login_button_element = UI_ELEMENTS.get("LOGIN_BUTTON")
            
            # 요소가 None인 경우 수동으로 정의
            if login_button_element is None:
                logging.warning("UI_ELEMENTS에서 LOGIN_BUTTON을 찾을 수 없습니다. 수동으로 정의합니다.")
                login_button_element = {
                    "name": "로그인 버튼",
                    "dom_selector": "//button[contains(@class, 'ant-btn-primary') and contains(., '이메일 로그인')]",
                    "selector_type": "xpath",
                    "coordinates": LOGIN["LOGIN_BUTTON"],
                    "fallback_order": ["dom", "coordinates"]
                }
                
            login_result = smart_click(
                self.driver, 
                element_info=login_button_element, 
                browser_core=self.browser_core,
                click_type="click"
            )
            
            login_success = login_result.get('success', False)
            
            if login_success:
                logging.info("smart_click으로 로그인 버튼 클릭 성공")
            else:
                logging.warning(f"smart_click으로 로그인 버튼 클릭 실패: {login_result.get('error', '알 수 없는 오류')}")
                # 실패 시 대체 방법 시도 (JavaScript)
                try:
                    # 퍼센티 로그인 버튼을 정확히 찾기 위한 개선된 JavaScript
                    js_result = self.driver.execute_script("""
                        // 퍼센티 로그인 버튼 클릭
                        var loginButton = document.querySelector('button[type="submit"]');
                        if (loginButton) {
                            loginButton.click();
                            return true;
                        }
                        // 페이지에 따라 다른 선택자로 시도
                        loginButton = document.querySelector('.signin-form__submit');
                        if (loginButton) {
                            loginButton.click();
                            return true;
                        }
                        return false;
                    """)
                    if js_result:
                        logging.info("JavaScript를 사용하여 로그인 버튼 클릭 성공")
                        login_success = True
                    else:
                        logging.warning("JavaScript로 로그인 버튼을 찾지 못했습니다")
                except Exception as js_error:
                    logging.warning(f"JavaScript로 로그인 버튼 클릭 실패: {js_error}")
                    
                # 3. 좌표 기반 클릭 - 브라우저 코어 활용
                if not login_success:
                    login_button_x, login_button_y = LOGIN["LOGIN_BUTTON"]
                    self.browser_core.click_at_coordinates(login_button_x, login_button_y, "LOGIN_BUTTON")
                    logging.info("브라우저 코어를 사용하여 로그인 버튼 클릭")
                    login_success = True
            
            # 로그인 버튼 클릭 후 대기 (응답을 위해)
            logging.info("로그인 버튼 클릭 후 대기 - 웹 서버 응답 및 로그인 처리 기다리는 중")
            sleep_with_logging(BUTTON_CLICK["LOGIN"], "로그인 버튼 클릭 후 대기")
            
            # 로그인 성공 여부 확인
            if not login_success:
                logging.error("로그인 버튼 클릭이 실패했습니다.")
                return False
            
            # 로그인 완료 대기 (URL이 변경될 때까지)
            wait = WebDriverWait(self.driver, timeout=60)
            wait.until(lambda driver: "/signin" not in driver.current_url)
            
            logging.info("로그인 완료! 현재 URL: " + self.driver.current_url)
            
            # 페이지 로드 대기
            sleep_with_logging(PAGE_LOAD["AFTER_LOGIN"], "로그인 후 페이지 로드 대기")
            
            # 1. 먼저 비밀번호 저장 모달창 닫기 (비밀번호를 저장하시겠습니까?)
            logging.info("비밀번호 저장 모달창 닫기 시도")
            self.modal_core.close_password_save_modal()
            sleep_with_logging(0.5, "비밀번호 저장 모달창 닫기 후")
            
            # 2. 다시 보지 않기 모달창 처리
            logging.info("다시 보지 않기 모달창 처리 시도")
            self.modal_core.close_login_modal()

            # 모달창 닫기 후 추가 대기 시간
            logging.info("모달창 처리 완료 - 홈 버튼 클릭 준비 중")
            wait_after_modal_close()

            # 퍼센티 홈 클릭 - 임시 주석 처리 (신규상품등록 메뉴를 클릭하는 문제 해결)
            try:
                # 홈 버튼 클릭 기능 임시 비활성화 - 추후 정확한 좌표로 수정 필요
                logging.info("홈 버튼 클릭 스킵 - 신규상품등록 메뉴 클릭 이슈 해결를 위해 비활성화")
                
                # 로그인 성공 확인
                wait_after_login()
                
                # 성공 후 화면 저장 (로그 없이) - 주석처리
                # self.browser_core.save_screenshot(f"login_success_{attempt}.png")
                
                return True
                
            except Exception as e:
                logging.error(f"홈 화면 이동 시 오류 발생: {e}")
                # 홈 화면 이동 실패해도 로그인은 성공했으므로 계속 진행
                return True
        except Exception as e:
            logging.error(f"로그인 중 오류 발생: {e}")
            # 오류로 인한 재시도
            wait_after_error()
            return self.login(attempt + 1)
    
    def click_product_aisourcing_button_improved(self):
        """
        AI 소싱 메뉴 클릭 - 하이브리드 방식 (DOM 선택자 + 좌표)
        
        DOM 선택자를 먼저 시도하고, 실패할 경우 좌표 기반 클릭을 시도하는
        진정한 하이브리드 접근 방식을 구현합니다.
        
        이전 방식: 구식 DOM/좌표 분리 방식
        개선된 방식: UI_ELEMENTS와 dom_utils.smart_click 사용
        """
        try:
            logging.info("AI 소싱 메뉴 클릭 시도 (하이브리드 방식)")
            
            # UI_ELEMENTS의 PRODUCT_AISOURCING 사용 (하이브리드 방식)
            result = smart_click(self.driver, UI_ELEMENTS["PRODUCT_AISOURCING"], "AI 소싱 메뉴")
            
            if result.get("success", False):
                logging.info(f"AI 소싱 메뉴 클릭 성공 (방법: {result.get('method', 'unknown')})")
                logging.info(f"메뉴 전환 후 페이지 로딩 대기 - {PAGE_LOAD['MENU_CHANGE']}초 대기")
                time.sleep(PAGE_LOAD["MENU_CHANGE"])  # 메뉴 클릭 후 페이지 로딩을 위해 5초 대기
                return True
            else:
                logging.error(f"AI 소싱 메뉴 클릭 실패: {result.get('error', 'unknown')}")
                return False
                
        except Exception as e:
            logging.error(f"AI 소싱 메뉴 클릭 중 오류 발생: {e}")
            traceback.print_exc()
            return False
    
    def click_product_register(self):
        """
        신규상품등록 메뉴 클릭 - DOM 선택자 기반으로 변경
        
        이전: 좌표 기반 클릭 (coordinates_menu.py)
        변경: DOM 선택자 기반 클릭 (span.ant-menu-title-content)
        """
        try:
            # 기존 좌표 값 (폴백용)
            coords_info = {'coordinates': MENU["PRODUCT_REGISTER"]}
            
            # DOM 선택자 - span.ant-menu-title-content 중에서 '신규 상품 등록' 텍스트를 가진 요소
            dom_info = {'selector': ('xpath', "//span[@class='ant-menu-title-content' and text()='신규 상품 등록']")} 
            
            # 디버깅용 강조 표시 (요소 찾기 확인)
            try:
                highlight_element(self.driver, dom_info, 1)
            except:
                logging.warning("신규상품등록 메뉴 요소 강조 표시 실패")
            
            # DOM 기반 클릭 시도
            logging.info("신규상품등록 메뉴 DOM 기반 클릭 시도")
            result = smart_click(self.driver, dom_info, "신규상품등록 메뉴")
            
            # DOM 클릭 실패 시 좌표 기반으로 폴백
            if not result:
                logging.warning("DOM 기반 클릭 실패, 좌표 기반 클릭으로 대체합니다")
                result = smart_click(self.driver, coords_info, "신규상품등록 메뉴(좌표)")
            
            sleep_with_logging(MENU_NAVIGATION["PRODUCT_REGISTER"], "신규상품등록 메뉴 클릭 후 대기")
            
            # 스크롤을 최상단으로 초기화
            self.driver.execute_script("window.scrollTo(0, 0);")
            logging.info("스크롤 위치를 최상단으로 초기화했습니다")
            
            return result
        except Exception as e:
            logging.error(f"신규상품등록 메뉴 클릭 중 오류 발생: {e}")
            return False
            
    def click_product_manage(self):
        """
        등록상품관리 메뉴 클릭 - DOM 선택자 기반으로 변경
        
        이전: 좌표 기반 클릭 (coordinates_menu.py)
        변경: DOM 선택자 기반 클릭 (span.ant-menu-title-content)
        """
        try:
            # 기존 좌표 값 (폴백용)
            coords_info = {'coordinates': MENU["PRODUCT_MANAGE"]}
            
            # DOM 선택자 - span.ant-menu-title-content 중에서 '등록 상품 관리' 텍스트를 가진 요소
            dom_info = {'selector': ('xpath', "//span[@class='ant-menu-title-content' and text()='등록 상품 관리']")} 
            
            # 디버깅용 강조 표시 (요소 찾기 확인)
            try:
                highlight_element(self.driver, dom_info, 1)
            except:
                logging.warning("등록상품관리 메뉴 요소 강조 표시 실패")
            
            # DOM 기반 클릭 시도
            logging.info("등록상품관리 메뉴 DOM 기반 클릭 시도")
            result = smart_click(self.driver, dom_info, "등록상품관리 메뉴")
            
            # DOM 클릭 실패 시 좌표 기반으로 폴백
            if not result:
                logging.warning("DOM 기반 클릭 실패, 좌표 기반 클릭으로 대체합니다")
                result = smart_click(self.driver, coords_info, "등록상품관리 메뉴(좌표)")
            
            sleep_with_logging(MENU_NAVIGATION["PRODUCT_MANAGE"], "등록상품관리 메뉴 클릭 후 대기")
            
            # 스크롤을 최상단으로 초기화
            self.driver.execute_script("window.scrollTo(0, 0);")
            logging.info("스크롤 위치를 최상단으로 초기화했습니다")
            
            return result
        except Exception as e:
            logging.error(f"등록상품관리 메뉴 클릭 중 오류 발생: {e}")
            return False
            
    def click_product_group(self):
        """
        그룹상품관리 메뉴 클릭 - 하이브리드 방식 (DOM 선택자 + 좌표)
        
        DOM 선택자를 먼저 시도하고, 실패할 경우 좌표 기반 클릭을 시도하는
        진정한 하이브리드 접근 방식을 구현합니다.
        
        이전 방식: 구식 smart_click 함수 사용
        개선된 방식: UI_ELEMENTS와 dom_utils.smart_click 사용
        """
        try:
            logging.info("그룹상품관리 메뉴 클릭 시도 (하이브리드 방식)")
            
            # UI_ELEMENTS의 PRODUCT_GROUP 사용 (하이브리드 방식)
            result = smart_click(self.driver, UI_ELEMENTS["PRODUCT_GROUP"], "그룹상품관리 메뉴")
            
            if result.get("success", False):
                logging.info(f"그룹상품관리 메뉴 클릭 성공 (방법: {result.get('method', 'unknown')})")
                sleep_with_logging(MENU_NAVIGATION["PRODUCT_GROUP"], "그룹상품관리 메뉴 클릭 후 대기")
                
                # 스크롤을 최상단으로 초기화
                self.driver.execute_script("window.scrollTo(0, 0);")
                logging.info("스크롤 위치를 최상단으로 초기화했습니다")
                
                return True
            else:
                logging.error(f"그룹상품관리 메뉴 클릭 실패: {result.get('error', 'unknown')}")
                return False
                
        except Exception as e:
            logging.error(f"그룹상품관리 메뉴 클릭 중 오류 발생: {e}")
            return False
            
    def click_setting_marketid(self):
        """
        마켓설정 메뉴 클릭 - DOM 선택자 기반으로 변경
        
        이전: 좌표 기반 클릭 (coordinates_menu.py)
        변경: DOM 선택자 기반 클릭 (span.ant-menu-title-content)
        """
        try:
            # 기존 좌표 값 (폴백용)
            coords_info = {'coordinates': MENU["SETTING_MARKETID"]}
            
            # DOM 선택자 - span.ant-menu-title-content 중에서 '마켓 설정' 텍스트를 가진 요소
            dom_info = {'selector': ('xpath', "//span[@class='ant-menu-title-content' and text()='마켓 설정']")} 
            
            # 디버깅용 강조 표시 (요소 찾기 확인)
            try:
                highlight_element(self.driver, dom_info, 1)
            except:
                logging.warning("마켓설정 메뉴 요소 강조 표시 실패")
            
            # DOM 기반 클릭 시도
            logging.info("마켓설정 메뉴 DOM 기반 클릭 시도")
            result = smart_click(self.driver, dom_info, "마켓설정 메뉴")
            
            # DOM 클릭 실패 시 좌표 기반으로 폴백
            if not result:
                logging.warning("DOM 기반 클릭 실패, 좌표 기반 클릭으로 대체합니다")
                result = smart_click(self.driver, coords_info, "마켓설정 메뉴(좌표)")
            
            sleep_with_logging(MENU_NAVIGATION["MARKET_SETTING"], "마켓설정 메뉴 클릭 후 대기")
            
            # 스크롤을 최상단으로 초기화
            self.driver.execute_script("window.scrollTo(0, 0);")
            logging.info("스크롤 위치를 최상단으로 초기화했습니다")
            
            return result
        except Exception as e:
            logging.error(f"마켓설정 메뉴 클릭 중 오류 발생: {e}")
            return False
            
    def click_saveid_checkbox(self, checkbox_x, checkbox_y):
        """
        아이디 저장 체크박스 클릭 - 특별 좌표 변환 적용
{{ ... }}
        
        체크박스는 일반 요소보다 더 정확한 클릭이 필요하여 추가 조정이 적용됩니다:
        
        표준 변환: relative_x = int(inner_width * (checkbox_x / 1920))
                relative_y = int(inner_height * (checkbox_y / 1080))
        
        체크박스 특화 변환: (778, 477) 으로 조정
        
        로그 예시: '체크박스 원래 좌표: (780, 563) -> (778, 477)'
        
        JavaScript elementFromPoint를 활용해 정확한 클릭을 수행하고, 체크박스의 상태 변화를 확인합니다.
        """
        try:
            logging.info("아이디 저장 체크박스 클릭 시도 (특별좌표 사용)")
            
            # 브라우저 내부 크기 가져오기
            inner_width = self.driver.execute_script("return window.innerWidth;")
            inner_height = self.driver.execute_script("return window.innerHeight;")
            
            # 클릭할 좌표 로깅
            logging.info(f"체크박스 설정 좌표: ({checkbox_x}, {checkbox_y})")
            
            # 통일된 좌표 변환 공식 사용
            relative_x, relative_y = self.convert_to_relative_coordinates(checkbox_x, checkbox_y)
            
            # JavaScript로 체크박스 클릭
            click_script = """
                var elem = document.elementFromPoint(arguments[0], arguments[1]);
                if (elem) {
                    var tagName = elem.tagName;
                    var elementText = elem.textContent || '';
                    var elementId = elem.id || '';
                    var elementClass = elem.className || '';
                    
                    // 체크박스 관련 요소인지 확인
                    var isCheckbox = elem.id === 'saveId' || 
                                 elem.querySelector('#saveId') || 
                                 (elem.closest('label') && elem.closest('label').querySelector('#saveId'));
                                 
                    // 클릭 수행
                    elem.click();
                    
                    // 체크박스 상태 확인
                    var checkbox = document.querySelector('input#saveId');
                    
                    return {
                        clicked: true,
                        tagName: tagName,
                        text: elementText.trim(),
                        id: elementId,
                        class: elementClass,
                        isCheckbox: isCheckbox,
                        checked: checkbox ? checkbox.checked : false
                    };
                }
                return { clicked: false };
            """
            
            result = self.driver.execute_script(click_script, relative_x, relative_y)
            
            if result.get('clicked', False):
                elem_info = f"[{result.get('tagName', '')}] '{result.get('text', '')}'"
                if result.get('id'):
                    elem_info += f" ID: {result.get('id')}"
                if result.get('class'):
                    elem_info += f" CLASS: {result.get('class')}"
                    
                logging.info(f"JavaScript로 체크박스 클릭 성공: ({relative_x}, {relative_y})")
                logging.info(f"클릭된 요소: {elem_info}")
                
                if result.get('checked', False):
                    logging.info("체크박스가 성공적으로 체크되었습니다!")
                else:
                    logging.warning("체크박스 클릭은 성공했지만 체크는 되지 않았습니다.")
                
                return result.get('checked', False), (relative_x, relative_y)
            else:
                logging.warning(f"JavaScript 클릭 실패")
                return False, (relative_x, relative_y)
                
        except Exception as e:
            logging.error(f"체크박스 클릭 시도 중 오류: {e}")
            
            return result.get('checked', False), (relative_x, relative_y)
        else:
            logging.warning(f"JavaScript 클릭 실패")
            return False, (relative_x, relative_y)


    def run(self):
        """로그인 및 AI 소싱 메뉴 접근 실행"""
        try:
            # 1. 웹드라이버 설정
            if not self.setup_driver():
                logging.error("웹드라이버 설정 실패로 로그인을 중단합니다.")
                return False
            
            # 2. 로그인 수행
            if not self.login():
                logging.error("로그인 실패")
                return False
                
            # 3. AI 소싱 메뉴 클릭
            # 로그인 후 대기는 login() 함수에서 수행됩니다
            
            if not self.click_product_aisourcing_button_improved():
                logging.error("AI 소싱 메뉴 클릭 실패")
                return False
            
            logging.info("AI 소싱 메뉴 클릭 완료")
            
            # 메뉴 클릭 함수 내에서 이미 PAGE_LOAD["MENU_CHANGE"] 대기를 수행하므로 추가 대기는 제거
            # wait_after_menu_change()
            
            # 채널톡 및 로그인 모달창 숨기기 적용 (통합 유틸리티 사용)
            logging.info("채널톡 및 로그인 모달창 숨기기 적용 시작")
            result = hide_channel_talk_and_modals(self.driver, log_prefix="로그인 과정")
            logging.info(f"채널톡 및 로그인 모달창 숨기기 결과: {result}")
            
            logging.info("퍼센티 로그인 및 AI 소싱 메뉴 접근이 완료되었습니다.")
            
            # 로그인 및 메뉴 접근 성공
            return True
        except Exception as e:
            logging.error(f"로그인 중 오류 발생: {e}")
            return False
    
    def close_driver(self):
        """웹드라이버 종료"""
        if self.driver:
            try:
                self.driver.quit()
                logging.info("웹드라이버가 종료되었습니다.")
            except Exception as e:
                logging.error(f"웹드라이버 종료 중 오류 발생: {e}")

# 직접 실행 시 로그인 실행
if __name__ == "__main__":
    # 계정 관리자 초기화
    account_manager = AccountManager()
    
    # 계정 정보 로드
    if not account_manager.load_accounts():
        print("계정 정보를 로드할 수 없습니다. 프로그램을 종료합니다.")
        sys.exit(1)
    
    # 계정 선택
    selected_account = account_manager.select_account()
    if not selected_account:
        print("계정을 선택하지 않았습니다. 프로그램을 종료합니다.")
        sys.exit(0)
    
    # 선택한 계정으로 로그인 객체 생성
    login = PercentyLogin(account=selected_account)
    
    # 로그인 시도
    print(f"\n선택한 계정으로 로그인을 시도합니다: {selected_account.get('nickname', selected_account['id'])}")
    result = login.run()
    
    if result:
        print("\n\n" + "=" * 50)
        print(f"로그인 성공! '{selected_account.get('nickname', '')}' 계정으로 로그인되었습니다.")
        print("브라우저가 열려 있습니다.")
        print("이제 다른 작업을 하면서도 자동화 프로그램이 실행됩니다.")
        print("종료하려면 Ctrl+C를 누르세요.")
        print("=" * 50 + "\n")
        
        try:
            # 무한 대기 (사용자가 Ctrl+C를 누를 때까지)
            while True:
                sleep_with_logging(DELAY_LONG, "무한 대기 체크")  # 10초마다 한 번씩 체크
        except KeyboardInterrupt:
            print("\n\n" + "=" * 50)
            print("사용자가 스크립트를 종료했습니다.")
            print("=" * 50 + "\n")
            
            # 사용자가 스크립트를 종료할 때 브라우저도 닫기
            login.close_driver()
        except Exception as e:
            print(f"오류 발생: {e}")
            # 오류 발생 시 브라우저 닫기
            login.close_driver()
    else:
        print("\n\n" + "=" * 50)
        print("로그인 실패! 자세한 내용은 로그를 확인하세요.")
        print("=" * 50 + "\n")
        login.close_driver()
