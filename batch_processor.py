# batch_processor.py
import os
import sys
import time
import logging
from typing import Dict, List, Optional, Union, Tuple

# 새로운 아키텍처 사용 여부 설정
USE_NEW_ARCHITECTURE = os.getenv('USE_NEW_ARCHITECTURE', 'false').lower() == 'true'

if USE_NEW_ARCHITECTURE:
    # 새로운 아키텍처 사용
    try:
        from batch.legacy_wrapper import LegacyBatchProcessor as NewBatchProcessor
        print("✅ 새로운 아키텍처를 사용합니다.")
        NEW_ARCH_AVAILABLE = True
    except ImportError as e:
        print(f"⚠️  새로운 아키텍처 로드 실패: {e}")
        print("기존 아키텍처를 사용합니다.")
        NEW_ARCH_AVAILABLE = False
else:
    NEW_ARCH_AVAILABLE = False

# 계정 관리자 모듈 추가
from account_manager import AccountManager

# 기존 코드 가져오기 (코어 파일은 수정하지 않음)
from app.steps.base_step_manager import BaseStepManager
from app.steps.step1_manager import Step1Manager
from menu_clicks import MenuClicks, click_at_absolute_coordinates
from coordinates.coordinates_all import MENU
from coordinates.coordinates_action import PRODUCT, GROUP, PRODUCT_FORM_ELEMENTS
# 시간 지연 관리 모듈 추가
from timesleep import DELAY_STANDARD, DELAY_SHORT
from ui_elements import UI_ELEMENTS
from human_delay import HumanLikeDelay
# 브라우저 초기화를 위한 모듈 추가
from browser_core import BrowserCore
# DOM 선택자 가져오기
from dom_selectors import LOGIN_SELECTORS, MENU_SELECTORS
# Selenium 웨이팅 기능 추가
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
# 채널톡 및 모달창 처리 기능 추가
from percenty_utils import hide_channel_talk_and_modals
# 모달창 처리 함수
from modal_blocker import close_modal_dialog, block_modals_on_page
# 로그인 파일의 기능 활용
from login_percenty import PercentyLogin
# 화면 로딩 대기 관련 상수
from login_percenty import PAGE_LOAD
# 로그인 파일의 유틸리티 함수
from login_percenty import sleep_with_logging, wait_after_modal_close, wait_after_login

# utils.common 대체 함수
def click_at_coordinates(driver, coords, delay=DELAY_SHORT):
    """좌표 사전 또는 튜플로 클릭"""
    if isinstance(coords, dict):
        x, y = coords.get('x', 0), coords.get('y', 0)
    elif isinstance(coords, (list, tuple)) and len(coords) >= 2:
        x, y = coords[0], coords[1]
    else:
        logger.error(f"알 수 없는 좌표 형식: {type(coords)}")
        return False
    
    return click_at_absolute_coordinates(driver, x, y, delay)

def smart_click(driver, element_info, delay=DELAY_SHORT, just_check=False):
    """DOM 선택자 또는 좌표로 클릭 (UI_ELEMENTS 형식)"""
    try:
        # 좌표가 있는 경우 좌표로 클릭
        if element_info.get('coordinates'):
            if just_check:
                # 확인만 하는 경우
                return True
            return click_at_coordinates(driver, element_info['coordinates'], delay)
        
        # DOM 선택자가 있는 경우 DOM으로 클릭 (여기서는 기본 false 반환)
        logger.warning("DOM 선택자 지원 코드가 없습니다.")
        return False
    except Exception as e:
        logger.error(f"smart_click 중 오류: {e}")
        return False

# 시작 시간 기반 로그 파일명 생성
start_time = time.strftime('%Y%m%d_%H%M%S')
log_filename = f"logs/batch_processor_{start_time}.log"

# 로그 디렉토리 생성
os.makedirs("logs", exist_ok=True)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_filename, encoding='utf-8')
    ]
)
logger = logging.getLogger("BatchProcessor")
logger.info(f"배치 프로세서 시작 - 로그 파일: {log_filename}")
logger.info(f"시작 시간: {start_time}")

class BatchProcessor:
    """퍼센티 자동화 배치 작업 처리 클래스"""
    
    # 계정 관리자 초기화 (엑셀 파일에서 계정 정보를 불러옴)
    account_manager = AccountManager()
    
    # 수량 프리셋
    QUANTITY_PRESETS = [100, 200, 300, 400, 500]
    
    def __init__(self, headless: bool = False, max_workers: int = 4):
        """배치 프로세서 초기화"""
        # 새로운 아키텍처 사용 가능한 경우 위임
        if NEW_ARCH_AVAILABLE:
            self._new_processor = NewBatchProcessor(headless=headless, max_workers=max_workers)
            self._use_new_arch = True
            logger.info("새로운 아키텍처 기반 BatchProcessor 초기화")
        else:
            self._use_new_arch = False
            logger.info("기존 아키텍처 기반 BatchProcessor 초기화")
        
        # 기존 속성들
        self.step_manager = None
        self.menu_clicks = None
        self.account_id = None
        self.quantity = 0
        self.processed_count = 0
        self.failed_count = 0
        self.headless = headless
        self.max_workers = max_workers
    
    def initialize(self):
        """배치 작업 초기화"""
        self._select_account()
        self._select_quantity()
        
        # 계정 정보 가져오기 (id -> email 키 이름 매핑)
        account_info = {
            "email": self.account_id.get("id"),  # Excel에서는 id 열에 이메일 주소가 저장됨
            "password": self.account_id.get("password")
        }
        
        try:
            # BrowserCore를 사용하여 브라우저 초기화
            logger.info("BrowserCore를 사용하여 브라우저 초기화 중...")
            browser_core = BrowserCore()
            logger.info("브라우저 설정 시작...")
            browser_core.setup_driver()
            
            # 이제 driver가 있으므로 Step1Manager 초기화 가능
            logger.info("Step1Manager 초기화 중...")
            self.step_manager = Step1Manager(browser_core.driver)
            
            # browser_core의 driver를 Step1Manager로 옮긴 후 삭제 방지 (메모리 누수 방지)
            browser_core.driver = None
            
            # 로그인 정보 설정
            logger.info(f"로그인 정보 설정 중: {account_info['email']}")
            
            try:
                # DOM 선택자를 사용한 로그인 과정 구현
                logger.info("로그인 페이지로 이동 중...")
                self.step_manager.driver.get("https://www.percenty.co.kr/signin")
                time.sleep(DELAY_STANDARD)  # 페이지 로딩 대기
                
                # 아이디 입력
                logger.info("아이디 입력 중...")
                email_field = self.step_manager.driver.find_element("xpath", LOGIN_SELECTORS["USERNAME_FIELD"])
                email_field.clear()
                email_field.send_keys(account_info["email"])
                time.sleep(DELAY_SHORT)
                
                # 비밀번호 입력
                logger.info("비밀번호 입력 중...")
                password_field = self.step_manager.driver.find_element("xpath", LOGIN_SELECTORS["PASSWORD_FIELD"])
                password_field.clear()
                password_field.send_keys(account_info["password"])
                time.sleep(DELAY_SHORT)
                
                # 로그인 버튼 클릭
                logger.info("로그인 버튼 클릭 중...")
                login_button = self.step_manager.driver.find_element("xpath", LOGIN_SELECTORS["LOGIN_BUTTON"])
                login_button.click()
                
                # 로그인 성공 확인
                logger.info("로그인 완료 확인 중...")
                WebDriverWait(self.step_manager.driver, 30).until(
                    lambda driver: "/signin" not in driver.current_url
                )
                logger.info(f"로그인 성공! 현재 URL: {self.step_manager.driver.current_url}")
                time.sleep(DELAY_STANDARD)  # 로그인 후 화면 로딩 대기
                
                # 메뉴 클릭 초기화
                logger.info("MenuClicks 초기화 중...")
                self.menu_clicks = MenuClicks(self.step_manager.driver)
            except Exception as e:
                logger.error(f"로그인 중 오류 발생: {e}")
                return False
            
            # MenuClicks는 이미 로그인 성공 후 초기화되었음
            
            logger.info(f"초기화 완료: {account_info['email']} 계정으로 {self.quantity}개 상품 작업 준비")
            return True
        except Exception as e:
            logger.error(f"초기화 중 오류 발생: {e}")
            return False
    
    def _select_account(self):
        """계정 선택 인터페이스"""
        # 계정 정보 로드
        if not self.account_manager.load_accounts():
            logger.error("계정 정보를 로드할 수 없습니다. 프로그램을 종료합니다.")
            sys.exit(1)
            
        # 계정 선택 (계정 목록은 AccountManager가 표시함)
        selected_account = self.account_manager.select_account()
        if not selected_account:
            logger.error("계정 선택이 취소되었습니다.")
            sys.exit(0)
            
        # 선택된 계정 정보 저장
        self.account_id = selected_account
    
    def _select_quantity(self):
        """작업 수량 선택 인터페이스"""
        print("\n1단계에서 수정할 상품수량을 입력하거나 선택하세요.")
        print("> 작업할 수량 직접 입력: (숫자만 입력)")
        print(f"> 작업할 수량 선택: {', '.join([f'{q}개' for q in self.QUANTITY_PRESETS])}")
        
        while True:
            choice = input("수량 입력 또는 선택: ")
            
            try:
                quantity = int(choice)
                if quantity > 0:
                    self.quantity = quantity
                    print(f"작업 수량: {quantity}개")
                    break
                else:
                    print("1 이상의 숫자를 입력해주세요.")
            except ValueError:
                print("유효한 숫자를 입력해주세요.")
    
    def toggle_product_view(self):
        """상품 목록 새로고침을 위한 토글 2회 클릭 기능
        
        Returns:
            int: 현재 목록에 있는 상품 개수. 실패시 0 반환
        """
        logger.info("상품 목록 새로고침 (토글 2회 클릭 방식)")
        
        # 인간 같은 지연 적용
        delay = HumanLikeDelay(min_total_delay=3, max_total_delay=6, current_speed=0)
        
        # DOM 선택자 가져오기 - 동일한 DOM 선택자를 2회 사용
        from dom_selectors import EDITGOODS_SELECTORS
        selector = EDITGOODS_SELECTORS.get("PRODUCT_VIEW_NOGROUP", "//button[@role='switch' and contains(@class, 'ant-switch')]")
        
        # 첫번째 클릭 - 그룹상품보기
        logger.info("그룹상품보기 토글 클릭 시도 (1번째 클릭)")
        success = False
        
        try:
            logger.info(f"DOM 선택자로 토글 찾기 시도: {selector}")
            toggle_button = self.step_manager.driver.find_element(By.XPATH, selector)
            logger.info("토글 버튼 요소 찾음")
            toggle_button.click()
            logger.info("첫번째 토글 클릭 성공 (DOM 선택자)")
            success = True
        except Exception as e:
            logger.warning(f"DOM 선택자로 첫번째 토글 클릭 실패: {str(e)[:100]}...")
            
            # JavaScript 실행 시도
            try:
                logger.info("JavaScript로 토글 클릭 시도 (1번째)")
                js_script = """
                    // 토글 버튼 찾기
                    const toggleSwitch = document.querySelector('button[role="switch"][class*="ant-switch"]');
                    if (toggleSwitch) {
                        toggleSwitch.click();
                        return true;
                    }
                    return false;
                """
                result = self.step_manager.driver.execute_script(js_script)
                if result:
                    logger.info("JavaScript로 첫번째 토글 클릭 성공")
                    success = True
                else:
                    logger.warning("JavaScript로 토글 요소를 찾지 못함")
            except Exception as js_error:
                logger.error(f"JavaScript 실행 오류: {js_error}")
        
        # 첫번째 클릭 후 2초 고정 지연 추가 (사용자 요청)
        logger.info("첫번째 클릭 후 2초 고정 지연 적용")
        time.sleep(2.0)  # 고정 2초 지연
        
        # 추가 지연 - 화면 전환 기다리기
        time.sleep(delay.get_delay('transition'))
        
        # 두번째 클릭 - 비그룹상품보기
        logger.info("비그룹상품보기 토글 클릭 시도 (2번째 클릭)")
        success = False
        
        try:
            # 동일한 DOM 선택자 사용
            logger.info(f"DOM 선택자로 토글 찾기 시도: {selector}")
            toggle_button = self.step_manager.driver.find_element(By.XPATH, selector)
            logger.info("토글 버튼 요소 찾음")
            toggle_button.click()
            logger.info("두번째 토글 클릭 성공 (DOM 선택자)")
            success = True
        except Exception as e:
            logger.warning(f"DOM 선택자로 두번째 토글 클릭 실패: {str(e)[:100]}...")
            
            # JavaScript 실행 시도
            try:
                logger.info("JavaScript로 토글 클릭 시도 (2번째)")
                js_script = """
                    // 토글 버튼 찾기
                    const toggleSwitch = document.querySelector('button[role="switch"][class*="ant-switch"]');
                    if (toggleSwitch) {
                        toggleSwitch.click();
                        return true;
                    }
                    return false;
                """
                result = self.step_manager.driver.execute_script(js_script)
                if result:
                    logger.info("JavaScript로 두번째 토글 클릭 성공")
                    success = True
                else:
                    logger.warning("JavaScript로 토글 요소를 찾지 못함")
            except Exception as js_error:
                logger.error(f"JavaScript 실행 오류: {js_error}")
                
        # 두번째 클릭 후 5초 고정 지연 추가 (사용자 요청)
        logger.info("두번째 클릭 후 5초 고정 지연 적용")
        time.sleep(5.0)  # 고정 5초 지연
        
        # 기존 방식으로 시도 (하위 호환성 유지)
        if not success:
            # 여러 XPath 선택자 시도
            selectors = [
                "//span[contains(@class, 'ant-radio-button-wrapper')][contains(., '비그룹상품')]",
                "//label[contains(@class, 'ant-radio-button-wrapper')][contains(., '비그룹상품')]",
                "//div[contains(@class, 'radio-group')]//span[contains(text(), '비그룹상품')]",
                "//div[contains(@class, 'radio-group')]//label[contains(text(), '비그룹상품')]"
            ]
            for selector in selectors:
                if success:
                    break
                    
                try:
                    logger.info(f"XPath 선택자 시도: {selector}")
                    non_group_toggle = self.step_manager.driver.find_element(By.XPATH, selector)
                    logger.info(f"비그룹상품보기 토글 요소 찾음")
                    non_group_toggle.click()
                    logger.info("비그룹상품보기 토글 클릭 성공")
                    success = True
                except Exception as e:
                    logger.warning(f"선택자 {selector}로 토글 클릭 실패: {str(e)[:100]}...")
            
            # JavaScript 실행 시도
            if not success:
                try:
                    logger.info("JavaScript로 비그룹상품 토글 클릭 시도")
                    js_script = """
                        const buttons = Array.from(document.querySelectorAll('span, label, div'));
                        const nonGroupButton = buttons.find(el => el.textContent && el.textContent.includes('비그룹상품'));
                        if (nonGroupButton) { nonGroupButton.click(); return true; }
                        return false;
                    """
                    result = self.step_manager.driver.execute_script(js_script)
                    if result:
                        logger.info("JavaScript로 비그룹상품 토글 클릭 성공")
                        success = True
                    else:
                        logger.warning("JavaScript로 비그룹상품 토글 요소를 찾지 못함")
                except Exception as e:
                    logger.error(f"JavaScript 실행 오류: {e}")
                    
        # 좌표 클릭 시도 (UI_ELEMENTS에서 좌표 정보가 있는 경우)
        if not success and "PRODUCT_VIEW_NOGROUP" in UI_ELEMENTS and "coordinates" in UI_ELEMENTS["PRODUCT_VIEW_NOGROUP"]:
            try:
                logger.info("UI_ELEMENTS의 좌표로 비그룹상품 토글 클릭 시도")
                toggle_x, toggle_y = UI_ELEMENTS["PRODUCT_VIEW_NOGROUP"]["coordinates"]
                # utils 모듈을 사용하지 않고 직접 클릭 함수 호출
                if self.step_manager.driver.execute_script(f"return {{result: document.elementFromPoint({toggle_x}, {toggle_y}).click(), x: {toggle_x}, y: {toggle_y}}}"):
                    logger.info(f"좌표({toggle_x}, {toggle_y})로 비그룹상품 토글 클릭 성공")
                    success = True
            except Exception as coord_error:
                logger.error(f"좌표 클릭 시도 중 오류: {coord_error}")
        
        # 상품 목록 로딩 대기
        logger.info(f"상품 목록 로딩 대기 - {delay.get_delay('waiting') + DELAY_STANDARD}초")
        time.sleep(delay.get_delay('waiting') + DELAY_STANDARD)
        
        # 페이지 로딩 확인 - '총 X개 상품' 텍스트를 찾는 방식으로 변경
        try:
            logger.info("상품 목록 로딩 확인 시도 ('총 X개 상품' 텍스트 검색)...")
            WebDriverWait(self.step_manager.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//span[contains(text(), '총') and contains(text(), '개 상품')]"))
            )
            logger.info("상품 목록 로딩 확인됨 ('총 X개 상품' 텍스트 찾음)")
        except Exception as e:
            logger.warning(f"상품 목록 로딩 확인 실패: {e}")
        
        # 상품 개수 확인
        product_count = self._check_product_count()
        logger.info(f"현재 비그룹상품 목록에 {product_count}개의 상품이 있습니다.")
        
        # 성공 여부와 관계없이 상품 개수 반환
        logger.info("상품 목록 새로고침 완료 및 화면 로딩 확인")
        return product_count
    
    def _check_product_count(self):
        """현재 상품 목록의 상품 개수를 확인
        
        Returns:
            int: 현재 상품 목록의 상품 개수. 실패시 0 반환
        """
        try:
            # 방법 1: "총 X개 상품" 텍스트를 확인하는 방법 (가장 정확한 방법)
            try:
                # "총 X개 상품" 표시 텍스트 찾기
                total_text_xpath = "//span[contains(text(), '총') and contains(text(), '개 상품')]"
                total_element = self.step_manager.driver.find_element(By.XPATH, total_text_xpath)
                if total_element:
                    total_text = total_element.text.strip()
                    logger.info(f"상품 개수 텍스트 발견: '{total_text}'")
                    
                    # "총 3,536개 상품" 형식에서 숫자만 추출
                    import re
                    numbers = re.findall(r'\d+,?\d*', total_text)
                    if numbers:
                        # 콤마 제거 후 정수로 변환
                        product_count = int(numbers[0].replace(',', ''))
                        logger.info(f"화면에 표시된 상품 개수: {product_count}개")
                        return product_count
            except Exception as text_error:
                logger.info(f"총 상품 개수 텍스트 추출 시도 실패: {text_error}")
            
            # JavaScript로 총 상품 개수 텍스트 확인 시도
            try:
                js_text = """
                const totalText = Array.from(document.querySelectorAll('span')).find(el => 
                    el.textContent && el.textContent.includes('총') && el.textContent.includes('개 상품'))?.textContent;
                if (totalText) {
                    const match = totalText.match(/\d+,?\d*/g);
                    return match ? match[0].replace(/,/g, '') : null;
                }
                return null;
                """
                js_count = self.step_manager.driver.execute_script(js_text)
                if js_count:
                    product_count = int(js_count)
                    logger.info(f"JavaScript로 추출한 총 상품 개수: {product_count}개")
                    return product_count
            except Exception as js_text_error:
                logger.info(f"JavaScript 텍스트 추출 시도 실패: {js_text_error}")
            
            # 방법 2: 상품 아이템 개수 확인
            # JavaScript로 상품 개수 확인 시도
            js_code = """
            return {
                productItems: document.querySelectorAll('div.sc-fremEr').length,
                productNames: document.querySelectorAll('span.sc-cQCQeq.sc-inyXkq').length
            };
            """
            js_result = self.step_manager.driver.execute_script(js_code)
            if js_result and isinstance(js_result, dict):
                product_items = js_result.get('productItems', 0)
                product_names = js_result.get('productNames', 0)
                logger.info(f"JavaScript 결과 - 상품아이템: {product_items}, 상품명: {product_names}")
                if product_items > 0:
                    return product_items
                if product_names > 0:
                    return product_names
            
            # 방법 3: Selenium 선택자로 상품 요소 개수 확인
            methods = [
                # 상품 아이템 개수 확인
                lambda: len(self.step_manager.driver.find_elements(By.XPATH, "//div[contains(@class, 'sc-fremEr')]")),
                # 상품명 개수 확인
                lambda: len(self.step_manager.driver.find_elements(By.XPATH, "//span[contains(@class, 'sc-cQCQeq') and contains(@class, 'sc-inyXkq')]"))
            ]
            
            # JavaScript 실패 시 일반 Selenium 방법 시도
            for method in methods:
                try:
                    count = method()
                    if count > 0:
                        return count
                except Exception:
                    continue
            
            # 모든 방법 실패 시 0 반환
            logger.warning("상품 개수를 확인할 수 없습니다.")
            return 0
        except Exception as e:
            logger.error(f"상품 개수 확인 중 오류: {e}")
            return 0
        
        # DOM 선택자로 화면이 제대로 로딩되었는지 확인
        product_loaded = False
        max_attempts = 5
        attempts = 0
        
        while attempts < max_attempts and not product_loaded:
            try:
                # UI_ELEMENTS에서 상품 목록 확인 관련 선택자 사용
                product_selector_keys = ["PRODUCT_FIRST_GOODS", "PRODUCT_LIST_ITEM", "PRODUCT_TABLE"]
                
                for key in product_selector_keys:
                    if key in UI_ELEMENTS and smart_click(self.step_manager.driver, UI_ELEMENTS[key], 0, just_check=True):
                        product_loaded = True
                        logger.info(f"상품 목록 로딩 확인됨 (선택자: {key})")
                        break
                
                if not product_loaded:
                    attempts += 1
                    time.sleep(1)
            except Exception as e:
                logger.warning(f"상품 목록 로딩 확인 중 오류: {e}")
                attempts += 1
                time.sleep(1)
        
        # 생각하는 시간 추가
        delay.apply_thinking_time()
        
        if product_loaded:
            logger.info("상품 목록 새로고침 완료 및 화면 로딩 확인")
        else:
            logger.warning("상품 목록 새로고침 후 화면 로딩 확인 실패, 계속 진행")
    
    def run_batch(self, accounts=None, quantity=None):
        """배치 작업 실행"""
        # 새로운 아키텍처 사용 가능한 경우 위임
        if self._use_new_arch and accounts is not None:
            logger.info("새로운 아키텍처로 배치 작업 실행")
            return self._new_processor.run_batch(accounts, quantity or 100)
        
        # 기존 방식 실행
        if quantity is not None:
            self.quantity = quantity
        
        logger.info(f"총 {self.quantity}개 상품 작업 시작 (기존 아키텍처)")
        
        # 로그인 후 모달창 처리 - 정리하고 중독 코드 제거
        try:
            logger.info("로그인 후 모달창 처리 시작...")
            
            # 다시 보지 않기 모달창 처리 - percenty_utils에서 가져온 안정화된 함수 사용
            logger.info("다시 보지 않기 모달창 처리 시도")
            from percenty_utils import hide_login_modal
            hide_login_modal(self.step_manager.driver)
            logger.info("로그인 모달창 처리 성공")
            
            # 모달창 닫기 후 추가 대기 시간
            logger.info("모달창 처리 완료 - AI 소싱 메뉴 클릭 준비 중")
            wait_after_modal_close()
            
            # 모달창 차단 스크립트 적용 - 다른 모달창도 추가로 차단
            block_modals_on_page(self.step_manager.driver)
        except Exception as e:
            logger.warning(f"모달창 처리 중 오류: {e}")

        # 채널톡 숨기기 - 먼저 처리하여 메뉴 클릭이 원활하게 동작하도록 함
        try:
            logger.info("채널톡 숨기기 시작...")
            hide_channel_talk_and_modals(self.step_manager.driver, log_prefix="메뉴클릭전")
            logger.info("채널톡 숨기기 완료")
        except Exception as e:
            logger.warning(f"채널톡 처리 중 오류: {e}")
            
        # AI 소싱 메뉴 클릭
        try:
            logger.info("AI 소싱 메뉴 클릭 시도...")
            self.menu_clicks.click_ai_sourcing()
            logger.info("AI 소싱 메뉴 클릭 후 화면 로딩 대기 - 3.0초")
            time.sleep(3.0)
            logger.info("AI 소싱 메뉴 클릭 작업 완료")
        except Exception as e:
            logger.error(f"AI 소싱 메뉴 클릭 시 오류: {e}")
            
            # 실패시 DOM 선택자로 재시도
            try:
                logger.info("DOM 선택자로 AI 소싱 메뉴 클릭 재시도...")
                element_info = UI_ELEMENTS["PRODUCT_AISOURCING"]
                # 좌표는 사용하지 않고 DOM 선택자만 사용
                modified_element_info = element_info.copy()
                modified_element_info["fallback_order"] = ["dom"]
                
                success = smart_click(self.step_manager.driver, modified_element_info, delay=DELAY_SHORT)
                
                if success:
                    logger.info("AI 소싱 메뉴 smart_click(DOM만) 성공")
                    interruptible_sleep(3.0)
            except Exception as inner_e:
                logger.error(f"DOM 선택자로 메뉴 클릭 재시도 시 오류: {inner_e}")
                
        
        # 그룹상품관리 화면으로 이동
        try:
            logger.info("그룹상품관리 화면으로 이동 시도")
            self.menu_clicks.click_group_management()
            logger.info("그룹상품관리 화면 로딩 대기 - 3.0초")
            interruptible_sleep(3.0)
            logger.info("그룹상품관리 화면 이동 성공")
        except Exception as e:
            logger.error(f"그룹상품관리 화면 이동 중 오류: {e}")
        
        # 비그룹상품보기 클릭
        try:
            logger.info("비그룹상품보기 클릭 시도")
            self.menu_clicks.click_non_group_toggle()
            logger.info("비그룹상품보기 전환 완료")
            
            # 상품 목록 로딩 대기
            interruptible_sleep(DELAY_STANDARD * 2)
            
            # 상품 개수 확인
            available_products = self._check_product_count()
            logger.info(f"처리 가능한 상품 개수: {available_products}개")
            
            if available_products == 0:
                logger.error("비그룹상품 목록이 비어있습니다. 작업을 중단합니다.")
                print("\n" + "=" * 50)
                print("비그룹상품 목록이 비어있습니다. 작업을 중단합니다.")
                print("=" * 50)
                return False
            
            if available_products < self.quantity:
                logger.warning(f"요청한 작업수량({self.quantity}개)보다 적은 상품({available_products}개)이 있습니다.")
                print(f"\n요청한 작업수량({self.quantity}개)보다 적은 상품({available_products}개)이 있습니다.")
                print("상품 수량에 맞춰서 작업을 진행합니다.")
                
                # 작업 수량 자동 조정
                self.quantity = available_products
                logger.info(f"작업 수량이 {self.quantity}개로 자동 조정되었습니다.")
                print(f"작업 수량이 {self.quantity}개로 자동 조정되었습니다.")
            
        except Exception as e:
            logger.error(f"비그룹상품보기 및 상품 수량 확인 중 오류: {e}")
            print(f"\n상품 수량 확인 중 오류 발생: {e}")
            print("계속 진행합니다...")
        
        # 초기 화면 초기화 토글 2회 클릭 제거 - 실제 상품 처리 후에만 호출되도록 수정
        # 이 부분은 상품 처리 후에 호출되도록 이동했음
        
        # 화면 로딩 대기
        time.sleep(DELAY_STANDARD)
        
        # 작업 수량만큼 반복
        for i in range(1, self.quantity + 1):
            logger.info(f"===== 상품 {i}/{self.quantity} 작업 시작 =====")
            
            # 각 상품마다 새로운 지연 전략 생성
            delay_strategy = HumanLikeDelay(min_total_delay=45, max_total_delay=60, current_speed=46)
            
            # 20개 작업마다 토글 2회 실행 (21번째 상품부터 적용)
            if i > 1 and (i - 1) % 3 == 0:
                logger.info(f"20개 작업 완료 후 토글 2회 실행으로 목록 새로고침")
                self.toggle_product_view()
            
            # 작업 시작 전 지연
            pre_action_delay = delay_strategy.get_delay('transition')
            logger.info(f"작업 시작 전 지연: {pre_action_delay:.2f}초")
            interruptible_sleep(pre_action_delay)
            
            try:
                # 1단계 상품 수정 실행 (프로덕트 에디터 초기화 및 사용)
                # Step1Manager는 process_single_product 메서드가 없고, ProductEditorCore에 있음
                start_time = time.time()
                
                # ProductEditorCore 초기화
                if not hasattr(self, 'product_editor') or self.product_editor is None:
                    from product_editor_core import ProductEditorCore
                    self.product_editor = ProductEditorCore(self.step_manager.driver)
                    logger.info("ProductEditorCore 초기화")
                
                # 모달창 재확인 및 처리
                try:
                    from modal_blocker import close_modal_dialog
                    close_modal_dialog(self.step_manager.driver)
                    
                    # 채널톡 및 모달창 통합 처리
                    hide_channel_talk_and_modals(self.step_manager.driver, log_prefix="상품 처리")
                except Exception as e:
                    logger.warning(f"모달창 및 채널톡 재처리 중 오류: {e}")
                
                # 상품 처리 실행
                success = self.product_editor.process_single_product()
                actual_process_time = time.time() - start_time
                
                if success:
                    self.processed_count += 1
                    logger.info(f"상품 {i} 작업 성공 (소요시간: {actual_process_time:.2f}초, 누적: {self.processed_count}/{self.quantity})")
                    
                    # 작업 성공 후 지연
                    post_action_delay = delay_strategy.get_delay('critical')
                    logger.info(f"작업 완료 후 지연: {post_action_delay:.2f}초")
                    interruptible_sleep(post_action_delay)
                else:
                    self.failed_count += 1
                    logger.error(f"상품 {i} 작업 실패 (실패 누적: {self.failed_count})")
                    
                    # 오류 발생 시 토글 2회 실행 시도
                    logger.info("작업 실패 후 토글 새로고침 시도")
                    self.toggle_product_view()
            except Exception as e:
                self.failed_count += 1
                logger.error(f"상품 {i} 작업 중 예외 발생: {e}")
                
                # 예외 발생 시 토글 2회 실행 시도
                logger.info("예외 발생 후 토글 새로고침 시도")
                try:
                    self.toggle_product_view()
                except Exception as refresh_error:
                    logger.error(f"새로고침 중 추가 예외 발생: {refresh_error}")
            
            # 남은 지연 적용 (목표 시간에 맞추기 위함)
            remaining_delay = delay_strategy.get_remaining_delay()
            if remaining_delay > 0:
                logger.info(f"추가 지연 적용: {remaining_delay:.2f}초")
                interruptible_sleep(remaining_delay)
            
            # 상태 출력
            print(f"진행 상황: {i}/{self.quantity} (성공: {self.processed_count}, 실패: {self.failed_count})")
        
        logger.info(f"배치 작업 완료: 총 {self.processed_count}/{self.quantity} 개 상품 처리됨 (실패: {self.failed_count})")
    
    def cleanup(self):
        """자원 정리"""
        self.close_browser()
        
    def close_browser(self):
        """브라우저 종료"""
        logger.info("브라우저 종료 중...")
        try:
            if self.step_manager and self.step_manager.driver:
                self.step_manager.driver.quit()
            logger.info("브라우저가 종료되었습니다.")
        except Exception as e:
            logger.error(f"브라우저 종료 중 오류: {e}")

# 인터럽트 가능한 sleep 함수 추가
def interruptible_sleep(seconds):
    """Ctrl+C로 중단 가능한 sleep 함수"""
    try:
        # 작은 단위로 쪼개서 sleep 실행 (최대 0.5초 단위)
        chunk_size = 0.5
        for _ in range(int(seconds / chunk_size)):
            time.sleep(chunk_size)
        # 남은 시간 처리
        remainder = seconds % chunk_size
        if remainder > 0:
            time.sleep(remainder)
        return True
    except KeyboardInterrupt:
        logger.info("사용자가 Ctrl+C로 sleep을 중단했습니다.")
        raise

def main():
    """메인 실행 함수"""
    print("=" * 50)
    print("퍼센티 자동화 배치 작업 도구")
    if NEW_ARCH_AVAILABLE:
        print("(새로운 아키텍처 지원)")
    print("=" * 50)
    print("이 도구는 퍼센티 사이트에서 1단계 상품 수정 작업을 원하는 수량만큼 자동으로 수행합니다.")
    if not NEW_ARCH_AVAILABLE:
        print("\n💡 새로운 기능을 사용하려면:")
        print("   python batch_processor_new.py")
        print("   또는 환경변수 USE_NEW_ARCHITECTURE=true 설정")
    print("=" * 50)
    
    batch = BatchProcessor()
    
    try:
        if batch.initialize():
            print("\n초기화 완료! 작업을 시작합니다...")
            print("(Ctrl+C를 누르면 언제든지 작업을 중단할 수 있습니다)")
            print("=" * 50)
            
            batch.run_batch()
            
            print("\n" + "=" * 50)
            print(f"작업 완료: 총 {batch.processed_count}/{batch.quantity} 개 상품 처리됨 (실패: {batch.failed_count})")
            print("=" * 50)
        else:
            print("\n초기화 실패! 로그를 확인하세요.")
    except KeyboardInterrupt:
        print("\n" + "=" * 50)
        print("사용자에 의해 작업이 중단되었습니다.")
        print("=" * 50)
        logger.info("사용자에 의해 작업이 중단되었습니다.")
    except Exception as e:
        print(f"\n오류 발생: {e}")
        logger.error(f"예상치 못한 오류 발생: {e}")
    finally:
        batch.cleanup()
        print("\n프로그램을 종료합니다.")

if __name__ == "__main__":
    main()
