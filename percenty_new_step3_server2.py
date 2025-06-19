#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
퍼센티 Step 3 전용 디버깅 스크립트
Step 2를 스킵하고 바로 Step 3 코어 기능만 테스트
"""

import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# 브라우저 설정 임포트
from browser_core import BrowserCore

# 계정 관리자 임포트
from account_manager import AccountManager

# Step 3 코어 기능 임포트
from product_editor_core3 import ProductEditorCore3

# 로그인 기능 임포트
from login_percenty import PercentyLogin

# 좌표 변환 공통 모듈 임포트
from coordinates.coordinate_conversion import convert_coordinates

# DOM 유틸리티 임포트
from dom_utils import highlight_element
# 클릭 유틸리티 임포트
from click_utils import smart_click
# 통합 유틸리티 모듈 임포트
from percenty_utils import hide_channel_talk_and_modals, periodic_ui_cleanup, ensure_clean_ui_before_action

# UI 요소 임포트
from ui_elements import UI_ELEMENTS

# 좌표 정보 임포트
from coordinates.coordinates_all import MENU

# 좌표 설정 파일 불러오기
from coordinates.coordinates_editgoods import (
    PRODUCT_MODAL_TAB,
    PRODUCT_MODAL_EDIT1,
    PRODUCT_MODAL_EDIT2,
    PRODUCT_PRICE_TAB,
    PRODUCT_MODAL_CLOSE,
    PRODUCT_DETAIL_EDIT,
    PRODUCT_MEMO_MODAL,
    DELAY_VERY_SHORT2,
    DELAY_VERY_SHORT5,
    DELAY_SHORT,
    DELAY_MEDIUM,
    DELAY_LONG
)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('percenty_new_step3.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PercentyNewStep3:
    def __init__(self):
        self.driver = None
        self.browser_core = None
        self.current_account_id = None
        
    def setup_browser(self):
        """브라우저 설정 및 초기화"""
        try:
            # PercentyLogin 클래스를 사용하여 브라우저 설정
            login_handler = PercentyLogin()
            if not login_handler.setup_driver():
                logging.error("브라우저 설정 실패")
                return False
            
            self.driver = login_handler.driver
            logging.info("브라우저 설정 완료")
            return True
            
        except Exception as e:
            logging.error(f"브라우저 설정 실패: {e}")
            return False
    
    def login_and_navigate(self, account_info):
        """로그인 및 등록상품관리 페이지로 이동"""
        try:
            logging.info(f"계정 {account_info['id']} 로그인 시작")
            
            # 로그인 수행
            login_handler = PercentyLogin(driver=self.driver, account=account_info)
            if not login_handler.login():
                logging.error("로그인 실패")
                return False
            
            logging.info("로그인 성공")
            
            # 등록상품관리 메뉴로 이동
            logging.info("등록상품관리 메뉴로 이동")
            
            # 등록상품관리 메뉴 클릭 (DOM 선택자 우선 사용)
            from ui_elements import UI_ELEMENTS
            from click_utils import smart_click
            
            product_manage_element = UI_ELEMENTS["PRODUCT_MANAGE"]
            success = smart_click(self.driver, product_manage_element, DELAY_MEDIUM)
            
            if not success:
                logging.warning("DOM 선택자로 등록상품관리 메뉴 클릭 실패, 좌표 방식으로 재시도")
                # 좌표 방식으로 폴백
                x, y = MENU["PRODUCT_MANAGE"]
                inner_width = self.driver.execute_script("return window.innerWidth;")
                inner_height = self.driver.execute_script("return window.innerHeight;")
                registered_product_coord = convert_coordinates(x, y, inner_width, inner_height)
                
                from selenium.webdriver.common.action_chains import ActionChains
                action = ActionChains(self.driver)
                action.move_to_element_with_offset(self.driver.find_element(By.TAG_NAME, "body"), registered_product_coord[0], registered_product_coord[1])
                action.click()
                action.perform()
                time.sleep(DELAY_MEDIUM)
            
            # 페이지 로딩 대기
            time.sleep(DELAY_LONG)
            
            # UI 정리
            hide_channel_talk_and_modals(self.driver)
            
            logging.info("등록상품관리 페이지 이동 완료")
            return True
            
        except Exception as e:
            logging.error(f"로그인 및 페이지 이동 중 오류: {e}")
            return False
    
    def run_step3_automation(self):
        """Step 3 자동화 실행"""
        try:
            logging.info("=== Step 3 자동화 시작 ===")
            
            # ProductEditorCore3 인스턴스 생성
            core3 = ProductEditorCore3(self.driver)
            
            # Step 3 작업 로드 (서버2 기준)
            server_name = "서버2"
            tasks = core3.load_task_list_from_excel_with_server_filter(
                account_id=self.current_account_id,
                step="step3",
                server_name=server_name
            )
            
            if not tasks:
                logging.warning(f"계정 {self.current_account_id}, 서버 {server_name}에 대한 Step 3 작업이 없습니다.")
                return True
            
            logging.info(f"Step 3 작업 {len(tasks)}개 발견")
            
            # UI 초기 설정
            logging.info("UI 초기 설정 시작")
            
            # 1. 드롭박스에서 신규수집 그룹 선택
            if not self._change_to_new_collection():
                logging.error("신규수집 그룹 선택 실패")
                return False
            
            # 2. 페이지당 50개 보기 설정 (주석처리 - 20개 처리로 변경)
            # if not self._set_items_per_page(50):
            #     logging.error("페이지당 50개 보기 설정 실패")
            #     return False
            
            # 3. 화면 상단으로 스크롤
            if not self._scroll_to_top():
                logging.error("화면 상단 스크롤 실패")
                return False
            
            logging.info("UI 초기 설정 완료")
            
            # 각 작업 처리
            for i, task in enumerate(tasks, 1):
                logging.info(f"=== Step 3 작업 {i}/{len(tasks)} 처리 시작 ===")
                logging.info(f"키워드: {task['provider_code']}, 타겟 그룹: {task['target_group']}")
                
                try:
                    # 개별 상품 수정 및 이동 처리
                    success = core3.process_keyword_with_individual_modifications(
                        keyword=task['provider_code'],
                        target_group=task['target_group'],
                        task_data=task
                    )
                    
                    if success:
                        logging.info(f"Step 3 작업 {i} 완료")
                    else:
                        logging.error(f"Step 3 작업 {i} 실패")
                        
                except Exception as e:
                    logging.error(f"Step 3 작업 {i} 처리 중 오류: {e}")
                    continue
            
            logging.info("=== Step 3 자동화 완료 ===")
            return True
            
        except Exception as e:
            logging.error(f"Step 3 자동화 중 오류: {e}")
            return False
    
    def _change_to_new_collection(self):
        """신규수집 그룹으로 변경"""
        try:
            logging.info("신규수집 그룹으로 변경 시작")
            
            from dropdown_utils2 import ProductSearchDropdownManager
            
            # ProductSearchDropdownManager 사용
            dropdown_manager = ProductSearchDropdownManager(self.driver)
            
            # 신규수집 그룹 선택 시도 (최대 3회 재시도)
            for attempt in range(3):
                try:
                    logging.info(f"신규수집 그룹 선택 시도 {attempt + 1}/3")
                    
                    # 상품검색용 드롭박스에서 신규수집 그룹 선택 (통합 메서드 사용)
                    if dropdown_manager.select_group_in_search_dropdown("신규수집"):
                        logging.info("신규수집 그룹 선택 성공")
                        
                        # 상품 목록 자동 로딩 대기
                        if dropdown_manager.verify_page_refresh():
                            logging.info("상품 목록 자동 로딩 완료")
                            return True
                        else:
                            logging.warning("상품 목록 로딩 확인 실패")
                    else:
                        logging.warning(f"신규수집 그룹 선택 실패 (시도 {attempt + 1}/3)")
                    
                    # 재시도 전 잠시 대기
                    if attempt < 2:  # 마지막 시도가 아닌 경우만
                        time.sleep(2)
                        
                except Exception as e:
                    logging.error(f"신규수집 그룹 선택 중 오류 (시도 {attempt + 1}/3): {e}")
                    if attempt < 2:  # 마지막 시도가 아닌 경우만
                        time.sleep(2)
            
            logging.warning("신규수집 그룹 변경 실패 - 기본값 유지")
            return True  # 실패해도 계속 진행
            
        except Exception as e:
            logging.error(f"신규수집 그룹 변경 중 오류: {e}")
            return True  # 실패해도 계속 진행
    
    def _set_items_per_page(self, count=50):
        """페이지당 아이템 수 설정"""
        try:
            logging.info(f"페이지당 {count}개 보기 설정 시작")
            
            from dropdown_utils2 import ProductSearchDropdownManager
            
            # ProductSearchDropdownManager 사용
            dropdown_manager = ProductSearchDropdownManager(self.driver)
            
            # 페이지 크기 설정 시도 (최대 3회 재시도)
            for attempt in range(3):
                try:
                    logging.info(f"페이지 크기 설정 시도 {attempt + 1}/3")
                    
                    # 페이지 크기 드롭박스에서 지정된 개수 선택
                    if dropdown_manager.select_items_per_page(str(count)):
                        logging.info(f"페이지당 {count}개 보기 설정 성공")
                        
                        # 상품 목록 자동 로딩 대기
                        if dropdown_manager.verify_page_refresh():
                            logging.info("상품 목록 자동 로딩 완료")
                            return True
                        else:
                            logging.warning("상품 목록 로딩 확인 실패")
                    else:
                        logging.warning(f"페이지 크기 설정 실패 (시도 {attempt + 1}/3)")
                    
                    # 재시도 전 잠시 대기
                    if attempt < 2:  # 마지막 시도가 아닌 경우만
                        time.sleep(2)
                        
                except Exception as e:
                    logging.error(f"페이지 크기 설정 중 오류 (시도 {attempt + 1}/3): {e}")
                    if attempt < 2:  # 마지막 시도가 아닌 경우만
                        time.sleep(2)
            
            logging.warning("페이지당 아이템 수 설정 실패 - 기본값 유지")
            return True  # 실패해도 계속 진행
            
        except Exception as e:
            logging.error(f"페이지당 아이템 수 설정 중 오류: {e}")
            return True  # 실패해도 계속 진행
    
    def _scroll_to_top(self):
        """맨 위로 스크롤"""
        try:
            logging.info("맨 위로 스크롤 시작")
            
            from timesleep import DELAY_SHORT
            
            # JavaScript로 맨 위로 스크롤
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(DELAY_SHORT)
            
            # 페이지 상단 요소로 스크롤 (추가 보장)
            try:
                from selenium.webdriver.common.by import By
                header_selectors = [
                    "//header",
                    "//div[contains(@class, 'header')]",
                    "//nav",
                    "//div[contains(@class, 'navbar')]",
                    "//body"
                ]
                
                for selector in header_selectors:
                    try:
                        header_element = self.driver.find_element(By.XPATH, selector)
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", header_element)
                        break
                    except Exception as e:
                        logging.debug(f"헤더 요소 {selector} 스크롤 실패: {e}")
                        continue
                        
            except Exception as e:
                logging.debug(f"헤더 요소 스크롤 실패: {e}")
            
            time.sleep(DELAY_SHORT)
            logging.info("맨 위로 스크롤 완료")
            return True
            
        except Exception as e:
            logging.error(f"맨 위로 스크롤 중 오류: {e}")
            return True  # 실패해도 계속 진행
    
    def cleanup(self):
        """정리 작업"""
        try:
            if self.driver:
                self.driver.quit()
                logging.info("브라우저 정리 완료")
        except Exception as e:
            logging.error(f"정리 작업 중 오류: {e}")

def main():
    """메인 실행 함수"""
    automation = None
    
    try:
        logging.info("=== Step 3 디버깅 스크립트 시작 ===")
        
        # 계정 관리자 초기화
        account_manager = AccountManager()
        if not account_manager.load_accounts():
            logging.error("계정 정보를 불러올 수 없습니다.")
            return
        
        accounts = account_manager.accounts
        if not accounts:
            logging.error("로드된 계정이 없습니다.")
            return
        
        # 계정 선택 (첫 번째 계정 사용 또는 사용자 선택)
        print("\n=== 사용 가능한 계정 목록 ===")
        for i, account in enumerate(accounts, 1):
            print(f"{i}. {account['id']} (서버: {account['server']})")
        
        while True:
            try:
                choice = input("\n테스트할 계정 번호를 선택하세요 (1-{}): ".format(len(accounts)))
                account_index = int(choice) - 1
                if 0 <= account_index < len(accounts):
                    selected_account = accounts[account_index]
                    break
                else:
                    print("올바른 번호를 입력하세요.")
            except ValueError:
                print("숫자를 입력하세요.")
        
        logging.info(f"선택된 계정: {selected_account['id']} (서버: {selected_account['server']})")
        
        # 자동화 인스턴스 생성
        automation = PercentyNewStep3()
        automation.current_account_id = selected_account['id']
        
        # 브라우저 설정
        if not automation.setup_browser():
            logging.error("브라우저 설정 실패")
            return
        
        # 로그인 및 페이지 이동
        if not automation.login_and_navigate(selected_account):
            logging.error("로그인 및 페이지 이동 실패")
            return
        
        # Step 3 자동화 실행
        step3_success = automation.run_step3_automation()
        
        if step3_success:
            print("\n=== Step 3 디버깅 완료 ===")
            logging.info("Step 3 디버깅 성공")
        else:
            print("\n=== Step 3 디버깅 실패 ===")
            logging.error("Step 3 디버깅 실패")
        
        # 결과 확인을 위한 대기
        input("\n결과를 확인한 후 Enter를 눌러 종료하세요...")
        
    except KeyboardInterrupt:
        logging.info("사용자에 의해 중단됨")
    except Exception as e:
        logging.error(f"메인 실행 중 오류: {e}")
    finally:
        if automation:
            automation.cleanup()

if __name__ == "__main__":
    main()