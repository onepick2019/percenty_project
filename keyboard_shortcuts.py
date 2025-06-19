"""
퍼센티 자동화에 필요한 단축키 기능을 제공하는 유틸리티 모듈

여러 단축키 기능을 섹션별로 관리하고 쉽게 호출할 수 있는 함수들을 제공합니다.
"""

import time
import logging
import pyautogui
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from login_modal_utils import apply_login_modal_hiding_for_new_tab

# 로깅 설정
logger = logging.getLogger(__name__)

# 대기 시간 설정 (필요에 따라 조정 가능)
DELAY_VERY_SHORT = 0.3
DELAY_SHORT = 0.5
DELAY_MEDIUM = 1
DELAY_LONG = 2
DELAY_VERY_LONG = 3

class KeyboardShortcuts:
    """키보드 단축키 기능을 제공하는 클래스"""
    
    def __init__(self, driver=None, use_selenium=True):
        """
        단축키 클래스 초기화
        
        Args:
            driver: 셀레니움 웹드라이버 (선택 사항, Selenium 관련 단축키에 필요)
            use_selenium: 기본적으로 Selenium을 사용할지 여부 (멀티브라우저 간섭 방지)
        """
        self.driver = driver
        self.default_use_selenium = use_selenium
        logger.info(f"키보드 단축키 모듈 초기화 (기본 Selenium 사용: {use_selenium})")
    
    def set_driver(self, driver):
        """
        드라이버 설정/변경
        
        Args:
            driver: 셀레니움 웹드라이버 인스턴스
        """
        self.driver = driver
        logger.info("단축키 모듈에 드라이버 설정됨")
    
    # =============================================================================
    # 1. 텍스트 편집 단축키 (복사, 붙여넣기, 전체 선택)
    # =============================================================================
    
    def select_all(self, use_selenium=True, delay=DELAY_SHORT):
        """
        전체 선택 (Ctrl+A)
        
        Args:
            use_selenium: Selenium을 사용할지 여부 (아니면 pyautogui 사용)
            delay: 실행 후 대기 시간
        """
        logger.info(f"단축키 실행: 전체 선택 (Ctrl+A) - Selenium 사용: {use_selenium}")
        if use_selenium and self.driver:
            actions = ActionChains(self.driver)
            actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
        else:
            pyautogui.hotkey('ctrl', 'a')
        time.sleep(delay)
    
    def copy(self, use_selenium=True, delay=DELAY_SHORT):
        """
        복사 (Ctrl+C)
        
        Args:
            use_selenium: Selenium을 사용할지 여부 (아니면 pyautogui 사용)
            delay: 실행 후 대기 시간
        """
        logger.info(f"단축키 실행: 복사 (Ctrl+C) - Selenium 사용: {use_selenium}")
        if use_selenium and self.driver:
            actions = ActionChains(self.driver)
            actions.key_down(Keys.CONTROL).send_keys('c').key_up(Keys.CONTROL).perform()
        else:
            pyautogui.hotkey('ctrl', 'c')
        time.sleep(delay)
    
    def paste(self, use_selenium=True, delay=DELAY_SHORT):
        """
        붙여넣기 (Ctrl+V)
        
        Args:
            use_selenium: Selenium을 사용할지 여부 (아니면 pyautogui 사용)
            delay: 실행 후 대기 시간
        """
        logger.info(f"단축키 실행: 붙여넣기 (Ctrl+V) - Selenium 사용: {use_selenium}")
        if use_selenium and self.driver:
            actions = ActionChains(self.driver)
            actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
        else:
            pyautogui.hotkey('ctrl', 'v')
        time.sleep(delay)
    
    def cut(self, use_selenium=True, delay=DELAY_SHORT):
        """
        잘라내기 (Ctrl+X)
        
        Args:
            use_selenium: Selenium을 사용할지 여부 (아니면 pyautogui 사용)
            delay: 실행 후 대기 시간
        """
        logger.info(f"단축키 실행: 잘라내기 (Ctrl+X) - Selenium 사용: {use_selenium}")
        if use_selenium and self.driver:
            actions = ActionChains(self.driver)
            actions.key_down(Keys.CONTROL).send_keys('x').key_up(Keys.CONTROL).perform()
        else:
            pyautogui.hotkey('ctrl', 'x')
        time.sleep(delay)
    
    # =============================================================================
    # 2. 모달창 탭 바로가기 (Alt+숫자)
    # =============================================================================
    
    def switch_to_tab(self, tab_number, use_selenium=True, delay=DELAY_SHORT):
        """
        모달창 탭 바로가기 (Alt+숫자)
        
        Args:
            tab_number: 탭 번호 (1~7)
            use_selenium: Selenium을 사용할지 여부 (아니면 pyautogui 사용)
            delay: 실행 후 대기 시간
        """
        if not 1 <= tab_number <= 7:
            logger.warning(f"지원하지 않는 탭 번호입니다: {tab_number}. 1~7만 지원됩니다.")
            return
            
        logger.info(f"단축키 실행: 탭 바로가기 (Alt+{tab_number}) - Selenium 사용: {use_selenium}")
        if use_selenium and self.driver:
            actions = ActionChains(self.driver)
            actions.key_down(Keys.ALT).send_keys(str(tab_number)).key_up(Keys.ALT).perform()
        else:
            pyautogui.hotkey('alt', str(tab_number))
        time.sleep(delay)
    
    def tab_key(self, count=1, use_selenium=True, delay=DELAY_SHORT):
        """
        탭 키 입력
        
        Args:
            count: 입력 횟수
            use_selenium: Selenium을 사용할지 여부 (아니면 pyautogui 사용)
            delay: 실행 후 대기 시간
        """
        logger.info(f"단축키 실행: 탭 키 {count}회 입력 - Selenium 사용: {use_selenium}")
        if use_selenium and self.driver:
            actions = ActionChains(self.driver)
            for _ in range(count):
                actions.send_keys(Keys.TAB).perform()
                time.sleep(0.1)
        else:
            for _ in range(count):
                pyautogui.press('tab')
                time.sleep(0.1)
        time.sleep(delay)
    
    def escape_key(self, use_selenium=True, delay=DELAY_SHORT):
        """
        ESC 키 입력
        
        Args:
            use_selenium: Selenium을 사용할지 여부 (아니면 pyautogui 사용)
            delay: 실행 후 대기 시간
        """
        logger.info(f"단축키 실행: ESC 키 입력 - Selenium 사용: {use_selenium}")
        if use_selenium and self.driver:
            actions = ActionChains(self.driver)
            actions.send_keys(Keys.ESCAPE).perform()
        else:
            pyautogui.press('esc')
        time.sleep(delay)
    
    # =============================================================================
    # 3. 브라우저 제어 단축키
    # =============================================================================
    
    def new_tab(self, use_selenium=True, delay=DELAY_SHORT):
        """
        새 탭 열기 (Ctrl+T) 및 로그인 모달창 자동 숨김 적용
        
        Args:
            use_selenium: Selenium을 사용할지 여부 (아니면 pyautogui 사용)
            delay: 실행 후 대기 시간
        """
        logger.info("단축키 실행: 새 탭 열기 (Ctrl+T)")
        if use_selenium and self.driver:
            actions = ActionChains(self.driver)
            actions.key_down(Keys.CONTROL).send_keys('t').key_up(Keys.CONTROL).perform()
            
            # 새 탭으로 전환 (1초 대기 후 전환 시도)
            time.sleep(1)
            try:
                # 새 탭은 일반적으로 가장 마지막 탭이미
                self.driver.switch_to.window(self.driver.window_handles[-1])
                
                # 로그인 모달창 자동 숨김 적용
                logger.info("새 탭에 로그인 모달창 자동 숨김 적용")
                apply_login_modal_hiding_for_new_tab(self.driver)
            except Exception as e:
                logger.warning(f"새 탭 전환 또는 로그인 모달창 숨김 오류: {e}")
        else:
            pyautogui.hotkey('ctrl', 't')
        time.sleep(delay)
    
    def switch_to_browser_tab(self, tab_number, use_selenium=True, delay=DELAY_SHORT):
        """
        크롬 탭 바로가기 (Ctrl+숫자)
        
        Args:
            tab_number: 탭 번호 (1~9)
            use_selenium: Selenium을 사용할지 여부 (아니면 pyautogui 사용)
            delay: 실행 후 대기 시간
        """
        if not 1 <= tab_number <= 9:
            logger.warning(f"지원하지 않는 탭 번호입니다: {tab_number}. 1~9만 지원됩니다.")
            return
            
        logger.info(f"단축키 실행: 브라우저 탭 바로가기 (Ctrl+{tab_number})")
        if use_selenium and self.driver:
            actions = ActionChains(self.driver)
            actions.key_down(Keys.CONTROL).send_keys(str(tab_number)).key_up(Keys.CONTROL).perform()
        else:
            pyautogui.hotkey('ctrl', str(tab_number))
        time.sleep(delay)
    
    def close_tab(self, use_selenium=True, delay=DELAY_SHORT):
        """
        현재 탭 닫기 (Ctrl+W)
        
        Args:
            use_selenium: Selenium을 사용할지 여부 (아니면 pyautogui 사용)
            delay: 실행 후 대기 시간
        """
        logger.info("단축키 실행: 현재 탭 닫기 (Ctrl+W)")
        if use_selenium and self.driver:
            actions = ActionChains(self.driver)
            actions.key_down(Keys.CONTROL).send_keys('w').key_up(Keys.CONTROL).perform()
        else:
            pyautogui.hotkey('ctrl', 'w')
        time.sleep(delay)
            
    def close_other_tabs(self, delay=DELAY_SHORT):
        """
        현재 탭을 제외한 모든 탭 닫기
        단축키가 없으나 Selenium을 통해 구현
        
        Args:
            delay: 실행 후 대기 시간
        
        Returns:
            bool: 성공 여부
        """
        if not self.driver:
            logger.warning("다른 탭 닫기는 Selenium 드라이버가 필요합니다.")
            return False
            
        try:
            logger.info("다른 탭 닫기 실행")
            
            # 현재 탭 핸들 및 모든 탭 핸들 가져오기
            current_handle = self.driver.current_window_handle
            all_handles = self.driver.window_handles
            
            # 현재 탭을 제외한 모든 탭 닫기
            for handle in all_handles:
                if handle != current_handle:
                    self.driver.switch_to.window(handle)
                    self.driver.close()
                    time.sleep(0.2)  # 약간의 지연 추가
            
            # 다시 처음 탭으로 이동
            self.driver.switch_to.window(current_handle)
            logger.info("다른 모든 탭이 닫혔습니다.")
            return True
            
        except Exception as e:
            logger.error(f"다른 탭 닫기 오류: {e}")
            return False
        finally:
            time.sleep(delay)
    
    def close_tabs_to_right(self, delay=DELAY_SHORT):
        """
        현재 탭 오른쪽에 있는 모든 탭 닫기
        단축키가 없으나 Selenium을 통해 구현
        
        Args:
            delay: 실행 후 대기 시간
            
        Returns:
            bool: 성공 여부
        """
        if not self.driver:
            logger.warning("우측 탭 닫기는 Selenium 드라이버가 필요합니다.")
            return False
            
        try:
            logger.info("우측 탭 닫기 실행")
            
            # 현재 탭 핸들 및 모든 탭 핸들 가져오기
            current_handle = self.driver.current_window_handle
            all_handles = self.driver.window_handles
            
            # 현재 탭 위치 찾기
            current_index = all_handles.index(current_handle)
            
            # 현재 탭 오른쪽의 탭들 닫기
            for handle in all_handles[current_index+1:]:
                self.driver.switch_to.window(handle)
                self.driver.close()
                time.sleep(0.2)  # 약간의 지연 추가
            
            # 다시 현재 탭으로 이동
            self.driver.switch_to.window(current_handle)
            logger.info("우측의 모든 탭이 닫혔습니다.")
            return True
            
        except Exception as e:
            logger.error(f"우측 탭 닫기 오류: {e}")
            return False
        finally:
            time.sleep(delay)
    
    def refresh_page(self, use_selenium=True, delay=DELAY_SHORT):
        """
        페이지 새로고침 (F5 또는 Ctrl+R)
        
        Args:
            use_selenium: Selenium을 사용할지 여부 (아니면 pyautogui 사용)
            delay: 실행 후 대기 시간
        """
        logger.info("단축키 실행: 페이지 새로고침 (F5)")
        if use_selenium and self.driver:
            actions = ActionChains(self.driver)
            actions.send_keys(Keys.F5).perform()
        else:
            pyautogui.press('f5')
        time.sleep(delay)
    
    # =============================================================================
    # 4. 모달 조작 및 폼 제출 관련 단축키
    # =============================================================================
    
    def submit_form(self, use_selenium=True, delay=DELAY_SHORT):
        """
        폼 제출 (Enter)
        
        Args:
            use_selenium: Selenium을 사용할지 여부 (아니면 pyautogui 사용)
            delay: 실행 후 대기 시간
        """
        logger.info("단축키 실행: 폼 제출 (Enter)")
        if use_selenium and self.driver:
            actions = ActionChains(self.driver)
            actions.send_keys(Keys.ENTER).perform()
        else:
            pyautogui.press('enter')
        time.sleep(delay)
    
    def tab_and_escape(self, tab_count=1, use_selenium=True, delay=DELAY_SHORT):
        """
        탭 후 ESC 키 입력 (모달창 처리에 유용)
        
        Args:
            tab_count: 탭 키 입력 횟수
            use_selenium: Selenium을 사용할지 여부 (아니면 pyautogui 사용)
            delay: 실행 후 대기 시간
        """
        logger.info(f"단축키 실행: 탭 {tab_count}회 후 ESC")
        self.tab_key(count=tab_count, use_selenium=use_selenium, delay=0.1)
        self.escape_key(use_selenium=use_selenium, delay=delay)
    
    # =============================================================================
    # 5. 커스텀 단축키 조합 실행
    # =============================================================================
    
    def press_keys(self, keys, use_selenium=True, delay=DELAY_SHORT):
        """
        일반 키 입력
        
        Args:
            keys: 입력할 키 (예: 'hello')
            use_selenium: Selenium을 사용할지 여부 (아니면 pyautogui 사용)
            delay: 실행 후 대기 시간
        """
        logger.info(f"단축키 실행: 키 입력 '{keys}' - Selenium 사용: {use_selenium}")
        if use_selenium and self.driver:
            actions = ActionChains(self.driver)
            actions.send_keys(keys).perform()
        else:
            pyautogui.write(keys)
        time.sleep(delay)
    
    def type_text(self, text, use_selenium=True, delay=DELAY_SHORT):
        """
        텍스트 입력 (press_keys와 동일한 기능)
        
        Args:
            text: 입력할 텍스트
            use_selenium: Selenium을 사용할지 여부 (아니면 pyautogui 사용)
            delay: 실행 후 대기 시간
        """
        logger.info(f"텍스트 입력: '{text}' - Selenium 사용: {use_selenium}")
        if use_selenium and self.driver:
            actions = ActionChains(self.driver)
            actions.send_keys(text).perform()
        else:
            pyautogui.write(text)
        time.sleep(delay)
    
    def custom_hotkey(self, *args, use_selenium=True, delay=DELAY_SHORT):
        """
        사용자 정의 단축키 조합 입력
        
        Args:
            *args: 단축키 조합 (예: 'ctrl', 'shift', 'n')
            use_selenium: Selenium을 사용할지 여부 (아니면 pyautogui 사용)
            delay: 실행 후 대기 시간
        """
        keys_str = '+'.join(args)
        logger.info(f"단축키 실행: 사용자 정의 단축키 ({keys_str}) - Selenium 사용: {use_selenium}")
        
        # Selenium으로 복잡한 조합 처리는 복잡하므로 pyautogui 사용 권장
        if not use_selenium or not self.driver:
            pyautogui.hotkey(*args)
        else:
            actions = ActionChains(self.driver)
            # 첫 번째 키를 제외한 모든 키를 누름
            for key in args[:-1]:
                if key.lower() == 'ctrl':
                    actions.key_down(Keys.CONTROL)
                elif key.lower() == 'shift':
                    actions.key_down(Keys.SHIFT)
                elif key.lower() == 'alt':
                    actions.key_down(Keys.ALT)
                else:
                    # 다른 특수 키는 필요에 따라 추가
                    actions.key_down(key)
            
            # 마지막 키 누름
            actions.send_keys(args[-1])
            
            # 모든 키 해제
            for key in reversed(args[:-1]):
                if key.lower() == 'ctrl':
                    actions.key_up(Keys.CONTROL)
                elif key.lower() == 'shift':
                    actions.key_up(Keys.SHIFT)
                elif key.lower() == 'alt':
                    actions.key_up(Keys.ALT)
                else:
                    actions.key_up(key)
            
            actions.perform()
        
        time.sleep(delay)


# 싱글턴 인스턴스 생성
keyboard = KeyboardShortcuts()

# 사용 예시
if __name__ == "__main__":
    # 기본 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 드라이버 없이 PyAutoGUI로 테스트
    print("키보드 단축키 테스트")
    print("---------------------")
    print("3초 후 단축키 테스트가 시작됩니다...")
    time.sleep(3)
    
    # 단축키 테스트
    keyboard.select_all(use_selenium=False)
    keyboard.copy(use_selenium=False)
    keyboard.paste(use_selenium=False)
    keyboard.tab_key(count=2, use_selenium=False)
    keyboard.escape_key(use_selenium=False)
    
    print("테스트 완료!")
