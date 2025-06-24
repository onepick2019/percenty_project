#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
퍼센티 확장프로그램 설치 테스트 스크립트

이 스크립트는 Chrome 웹스토어에서 퍼센티 확장프로그램을 설치할 때
나타나는 모달창의 '확장 프로그램 추가' 버튼을 다양한 방법으로 클릭하는 테스트를 수행합니다.

절대좌표: (1000, 240)
"""

import time
import sys
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# OS 레벨 마우스 클릭 라이브러리들
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    print("PyAutoGUI를 설치하려면: pip install pyautogui")

try:
    from pynput.mouse import Button, Listener as MouseListener
    from pynput import mouse
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    print("pynput을 설치하려면: pip install pynput")

try:
    import win32api
    import win32con
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False
    print("pywin32를 설치하려면: pip install pywin32")

# 퍼센티 확장프로그램 URL
PERCENTY_EXTENSION_URL = "https://chromewebstore.google.com/detail/%ED%8D%BC%EC%84%BC%ED%8B%B0/jlcdjppbpplpdgfeknhioedbhfceaben?hl=ko&authuser=0"

# 클릭할 절대좌표
CLICK_X = 1000
CLICK_Y = 240

class ExtensionInstallTester:
    def __init__(self):
        self.driver = None
        self.setup_browser()
    
    def setup_browser(self):
        """브라우저 설정 및 초기화"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # 퍼센티 확장프로그램 강제 로딩 부분 주석처리
            # chrome_options.add_argument("--load-extension=path/to/percenty/extension")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print("브라우저가 성공적으로 초기화되었습니다.")
            
        except Exception as e:
            print(f"브라우저 초기화 실패: {e}")
            raise
    
    def navigate_to_extension_page(self):
        """퍼센티 확장프로그램 페이지로 이동"""
        try:
            print(f"퍼센티 확장프로그램 페이지로 이동: {PERCENTY_EXTENSION_URL}")
            self.driver.get(PERCENTY_EXTENSION_URL)
            time.sleep(3)
            
            # 페이지 로딩 확인
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            print("페이지 로딩 완료")
            
        except Exception as e:
            print(f"페이지 이동 실패: {e}")
            raise
    
    def click_add_to_chrome_button(self):
        """'Chrome에 추가' 버튼 클릭"""
        try:
            print("'Chrome에 추가' 버튼을 찾는 중...")
            
            # 다양한 셀렉터로 버튼 찾기 시도
            selectors = [
                "button[data-test-id='install-button']",
                "button[aria-label*='Chrome에 추가']",
                "button[aria-label*='Add to Chrome']",
                "div[role='button'][aria-label*='Chrome에 추가']",
                "div[role='button'][aria-label*='Add to Chrome']",
                "button:contains('Chrome에 추가')",
                "button:contains('Add to Chrome')"
            ]
            
            button = None
            for selector in selectors:
                try:
                    if ":contains" in selector:
                        # JavaScript로 텍스트 기반 검색
                        button = self.driver.execute_script(f"""
                            return Array.from(document.querySelectorAll('button')).find(
                                el => el.textContent.includes('Chrome에 추가') || el.textContent.includes('Add to Chrome')
                            );
                        """)
                    else:
                        button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if button:
                        print(f"버튼을 찾았습니다: {selector}")
                        break
                except:
                    continue
            
            if not button:
                print("'Chrome에 추가' 버튼을 찾을 수 없습니다.")
                return False
            
            # 버튼 클릭
            self.driver.execute_script("arguments[0].click();", button)
            print("'Chrome에 추가' 버튼을 클릭했습니다.")
            
            # 모달창이 나타날 때까지 대기
            time.sleep(2)
            return True
            
        except Exception as e:
            print(f"'Chrome에 추가' 버튼 클릭 실패: {e}")
            return False
    
    def test_pyautogui_click(self):
        """PyAutoGUI를 사용한 클릭 테스트"""
        if not PYAUTOGUI_AVAILABLE:
            print("PyAutoGUI가 설치되지 않았습니다.")
            return False
        
        try:
            print(f"PyAutoGUI로 좌표 ({CLICK_X}, {CLICK_Y}) 클릭 시도...")
            
            # 안전장치 설정
            pyautogui.FAILSAFE = True
            pyautogui.PAUSE = 0.5
            
            # 현재 마우스 위치 저장
            original_pos = pyautogui.position()
            print(f"현재 마우스 위치: {original_pos}")
            
            # 클릭 실행
            pyautogui.click(CLICK_X, CLICK_Y)
            print(f"PyAutoGUI 클릭 완료: ({CLICK_X}, {CLICK_Y})")
            
            time.sleep(1)
            return True
            
        except Exception as e:
            print(f"PyAutoGUI 클릭 실패: {e}")
            return False
    
    def test_pynput_click(self):
        """pynput을 사용한 클릭 테스트"""
        if not PYNPUT_AVAILABLE:
            print("pynput이 설치되지 않았습니다.")
            return False
        
        try:
            print(f"pynput으로 좌표 ({CLICK_X}, {CLICK_Y}) 클릭 시도...")
            
            # 마우스 컨트롤러 생성
            mouse_controller = mouse.Controller()
            
            # 현재 마우스 위치 저장
            original_pos = mouse_controller.position
            print(f"현재 마우스 위치: {original_pos}")
            
            # 마우스 이동 및 클릭
            mouse_controller.position = (CLICK_X, CLICK_Y)
            time.sleep(0.1)
            mouse_controller.click(Button.left, 1)
            
            print(f"pynput 클릭 완료: ({CLICK_X}, {CLICK_Y})")
            
            time.sleep(1)
            return True
            
        except Exception as e:
            print(f"pynput 클릭 실패: {e}")
            return False
    
    def test_win32_click(self):
        """Windows API를 사용한 클릭 테스트"""
        if not WIN32_AVAILABLE:
            print("pywin32가 설치되지 않았습니다.")
            return False
        
        try:
            print(f"Windows API로 좌표 ({CLICK_X}, {CLICK_Y}) 클릭 시도...")
            
            # 현재 마우스 위치 저장
            original_pos = win32api.GetCursorPos()
            print(f"현재 마우스 위치: {original_pos}")
            
            # 마우스 이동
            win32api.SetCursorPos((CLICK_X, CLICK_Y))
            time.sleep(0.1)
            
            # 마우스 클릭 (왼쪽 버튼 다운 -> 업)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, CLICK_X, CLICK_Y, 0, 0)
            time.sleep(0.05)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, CLICK_X, CLICK_Y, 0, 0)
            
            print(f"Windows API 클릭 완료: ({CLICK_X}, {CLICK_Y})")
            
            time.sleep(1)
            return True
            
        except Exception as e:
            print(f"Windows API 클릭 실패: {e}")
            return False
    
    def check_modal_appeared(self):
        """모달창이 나타났는지 확인"""
        try:
            # Chrome 확장프로그램 설치 확인 대화상자 감지 시도
            # 실제로는 Selenium으로 감지할 수 없지만, 페이지 변화를 확인
            
            time.sleep(2)
            
            # 페이지 제목이나 URL 변화 확인
            current_url = self.driver.current_url
            page_title = self.driver.title
            
            print(f"현재 URL: {current_url}")
            print(f"페이지 제목: {page_title}")
            
            # 확장프로그램이 설치되었는지 확인하는 방법
            # (실제로는 Chrome의 네이티브 대화상자이므로 직접 감지 불가)
            
            return True
            
        except Exception as e:
            print(f"모달창 확인 실패: {e}")
            return False
    
    def run_test(self):
        """전체 테스트 실행"""
        try:
            print("=" * 60)
            print("퍼센티 확장프로그램 설치 테스트 시작")
            print("=" * 60)
            
            # 1. 퍼센티 확장프로그램 페이지로 이동
            self.navigate_to_extension_page()
            
            # 2. 'Chrome에 추가' 버튼 클릭
            if not self.click_add_to_chrome_button():
                print("'Chrome에 추가' 버튼 클릭에 실패했습니다.")
                return
            
            print("\n모달창이 나타날 때까지 5초 대기...")
            time.sleep(5)
            
            print("\n다양한 방법으로 절대좌표 클릭 테스트 시작")
            print("-" * 40)
            
            # 3. 다양한 방법으로 클릭 테스트
            methods = [
                ("PyAutoGUI", self.test_pyautogui_click),
                ("pynput", self.test_pynput_click),
                ("Windows API", self.test_win32_click)
            ]
            
            for method_name, method_func in methods:
                print(f"\n[{method_name}] 테스트 시작")
                try:
                    success = method_func()
                    if success:
                        print(f"[{method_name}] 클릭 성공")
                        
                        # 모달창 상태 확인
                        self.check_modal_appeared()
                        
                        # 다음 테스트를 위해 잠시 대기
                        time.sleep(3)
                    else:
                        print(f"[{method_name}] 클릭 실패")
                        
                except Exception as e:
                    print(f"[{method_name}] 테스트 중 오류: {e}")
                    traceback.print_exc()
            
            print("\n=" * 60)
            print("테스트 완료")
            print("=" * 60)
            
        except Exception as e:
            print(f"테스트 실행 중 오류: {e}")
            traceback.print_exc()
        
        finally:
            # 브라우저 종료는 수동으로 하도록 함 (결과 확인을 위해)
            print("\n브라우저를 수동으로 종료하세요.")
            input("Enter 키를 눌러 브라우저를 종료하세요...")
            if self.driver:
                self.driver.quit()

def main():
    """메인 함수"""
    print("퍼센티 확장프로그램 설치 테스트")
    print(f"클릭 좌표: ({CLICK_X}, {CLICK_Y})")
    print()
    
    # 사용 가능한 라이브러리 확인
    print("사용 가능한 라이브러리:")
    print(f"- PyAutoGUI: {'✓' if PYAUTOGUI_AVAILABLE else '✗'}")
    print(f"- pynput: {'✓' if PYNPUT_AVAILABLE else '✗'}")
    print(f"- pywin32: {'✓' if WIN32_AVAILABLE else '✗'}")
    print()
    
    if not any([PYAUTOGUI_AVAILABLE, PYNPUT_AVAILABLE, WIN32_AVAILABLE]):
        print("클릭 테스트를 위한 라이브러리가 설치되지 않았습니다.")
        print("다음 명령어로 설치하세요:")
        print("pip install pyautogui pynput pywin32")
        return
    
    # 테스트 실행
    tester = ExtensionInstallTester()
    tester.run_test()

if __name__ == "__main__":
    main()