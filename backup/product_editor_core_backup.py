#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import logging
import pyautogui
import pyperclip
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# 프로젝트 내 모듈 임포트
from ui_elements import UI_ELEMENTS
from timesleep import sleep_with_logging, DELAY_VERY_SHORT2, DELAY_VERY_SHORT5, DELAY_VERY_SHORT
from keyboard_shortcuts import KeyboardShortcuts
from dom_utils import wait_for_element
from click_utils import click_at_coordinates, smart_click
from image_utils import PercentyImageManager
from product_name_editor import ProductNameEditor
from dropdown_utils import get_dropdown_helper
from dom_selectors import EDITGOODS_SELECTORS as dom_selectors

# 모든 지연 시간 상수는 timesleep.py에서 중앙 관리
from timesleep import *  # 모든 지연 상수 임포트

# 로깅 설정
logger = logging.getLogger(__name__)

class ProductEditorCore:
    """
    상품 수정의 핵심 로직(2번~24번)을 담당하는 클래스
    
    이 클래스는 다음 작업을 수행합니다:
    - 첫번째 상품 클릭하여 모달창 열기
    - 메모 편집
    - 상세페이지 편집 (HTML 삽입)
    - 이미지 최적화 (31번째 이후 삭제)
    - 상품정보고시 편집
    - 상품명 수정
    - 상품수정 모달창 나가기
    - 상품을 신규수집 그룹으로 이동
    """
    
    def __init__(self, driver, config=None, dropdown_manager=None):
        """
        상품 편집 코어 초기화
        
        Args:
            driver: Selenium WebDriver 인스턴스
            config: 설정 정보 딕셔너리 (선택사항)
            dropdown_manager: 드롭다운 관리자 인스턴스 (선택사항)
        """
        self.driver = driver
        # 상품명 접미사 인덱스 추가 (A에서 Z까지 순차적으로 사용하기 위해)
        self.suffix_index = 0
        self.config = config or {}
        
        # dropdown_utils.py에서 기존 함수 사용
        if dropdown_manager is None:
            from dropdown_utils import get_dropdown_manager
            self.dropdown_manager = get_dropdown_manager(driver)
        else:
            self.dropdown_manager = dropdown_manager
            
        self.keyboard = KeyboardShortcuts(self.driver)
        self.original_memo = ""  # 원본 메모 내용 저장용
        
        # 드롭다운 관리자가 제공되지 않은 경우 새로 생성
        if dropdown_manager is None:
            try:
                from dropdown_utils import get_dropdown_manager
                self.dropdown_manager = get_dropdown_manager(driver)
            except ImportError as ie:
                logger.error(f"dropdown_utils 모듈을 찾을 수 없습니다: {ie}")
                self.dropdown_manager = None
        else:
            self.dropdown_manager = dropdown_manager
        
    def _check_modal_open(self, max_wait=10, check_interval=0.5):
        """
        모달창이 열렸는지 확인하는 향상된 함수
        여러 가지 선택자와 방법을 사용하여 모달창 열림 여부 확인
        
        Args:
            max_wait (float): 최대 대기 시간(초)
            check_interval (float): 확인 간격(초)
            
        Returns:
            bool: 모달창 열림 여부
        """
        logger.info(f"모달창이 열렸는지 확인 시작 (향상된 방식)")
        
        # 확인에 사용할 모달 관련 선택자 목록
        modal_selectors = [
            "//div[@role='dialog']",
            "//div[contains(@class, 'ant-modal')]",
            "//div[contains(@class, 'ant-drawer-content')]",
            "//div[contains(@class, 'drawer-content')]",
            "//div[contains(@class, 'modal-content')]"
        ]
        
        start_time = time.time()
        success_count = 0
        
        # 최대 대기 시간 동안 확인 반복
        while time.time() - start_time < max_wait:
            try:
                # 각 선택자별로 모달창 요소 존재 여부 확인
                for selector in modal_selectors:
                    elements = wait_for_elements(self.driver, By.XPATH, selector, timeout=0.5, raise_exception=False)
                    if elements and len(elements) > 0:
                        elapsed = time.time() - start_time
                        logger.info(f"모달창 요소 발견: {selector}, 개수: {len(elements)} ({elapsed:.1f}초 소요)")
                        success_count += 1
                        
                # 일정 개수 이상의 선택자에서 모달창 요소가 확인되면 성공으로 간주
                if success_count >= 2:
                    logger.info(f"여러 모달 요소가 확인됨 ({success_count}개). 모달이 열린 것으로 판단")
                    return True
                    
                # 최소 하나의 모달창 요소가 확인되면 더 짧게 대기하며 추가 확인
                if success_count > 0:
                    logger.info(f"모달창 요소 일부 발견 ({success_count}개). 추가 검증 중...")
                    time.sleep(check_interval / 2)  # 더 짧게 대기
                    continue
                    
                # 아무것도 발견되지 않았으면 원래 간격으로 대기
                success_count = 0  # 카운터 리셋
                time.sleep(check_interval)
                
            except Exception as e:
                logger.debug(f"모달 확인 중 오류: {e}")
                time.sleep(check_interval)
        
        # 마지막 기회: 페이지에서 모달 관련 요소를 전체 검색
        try:
            # 모달 관련 키워드가 있는 요소 검색
            modal_keywords = ["modal", "drawer", "dialog", "overlay", "popup"]
            page_source = self.driver.page_source.lower()
            
            for keyword in modal_keywords:
                if keyword in page_source:
                    logger.info(f"페이지 소스에서 모달 관련 키워드 '{keyword}' 발견. 모달이 있을 가능성 있음")
                    # 최소한 페이지 소스에서 관련 키워드가 발견되면 부분 성공으로 간주
                    return True
        except Exception as e:
            logger.debug(f"페이지 소스 검색 중 오류: {e}")
            
        logger.warning(f"모달창 열림 확인 실패 (제한시간 {max_wait}초 초과)")
        return False
        
    def _click_first_product(self):
        """
        2. 첫번째 상품 클릭 시도 (UI_ELEMENTS의 PRODUCT_FIRST_GOODS 사용)
        
        Returns:
            bool: 성공 여부
        """
        logger.info("\n\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        logger.info("!!! 첫번째 상품 클릭 함수 실행 중 - UI_ELEMENTS 방식 !!!")
        logger.info("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n")
        
        logger.info("2. 첫번째 상품 클릭 시도 (UI_ELEMENTS PRODUCT_FIRST_GOODS 사용)")
        
        max_attempts = 3
        
        for attempt in range(max_attempts):
            try:
                logger.info(f"첫번째 상품 클릭 시도 ({attempt+1}/{max_attempts})")
                
                # UI_ELEMENTS의 PRODUCT_FIRST_GOODS 사용
                if "PRODUCT_FIRST_GOODS" in UI_ELEMENTS:
                    logger.info("UI_ELEMENTS의 PRODUCT_FIRST_GOODS로 클릭 시도")
                    if smart_click(self.driver, UI_ELEMENTS["PRODUCT_FIRST_GOODS"], delay=DELAY_SHORT):
                        # 클릭 후 모달창이 열렸는지 확인
                        if self._check_modal_open(max_wait=5):
                            logger.info("첫번째 상품 클릭 및 모달창 열림 확인 성공")
                            return True
                        else:
                            logger.warning(f"첫번째 상품 클릭했지만 모달창 열림 확인 실패 ({attempt+1}/{max_attempts})")
                    else:
                        logger.warning(f"첫번째 상품 클릭 실패 ({attempt+1}/{max_attempts})")
                else:
                    logger.error("UI_ELEMENTS에 PRODUCT_FIRST_GOODS가 정의되지 않음")
                    return False
                
                if attempt < max_attempts - 1:
                    logger.info("다음 시도 전 3초 대기")
                    time.sleep(DELAY_STANDARD)
                    
            except Exception as e:
                logger.error(f"첫번째 상품 클릭 중 오류: {e}")
                if attempt < max_attempts - 1:
                    time.sleep(1)
        
        logger.error("최대 시도 횟수 초과 - 첫번째 상품 클릭 실패")
        return False
        
    def wait_for_tab_active(self, tab_key, timeout=5):
        """
        탭이 활성화될 때까지 대기하는 기능
        
        Args:
            tab_key (str): UI_ELEMENTS의 탭 키 이름
            timeout (int): 최대 대기 시간(초)
            
        Returns:
            bool: 탭 활성화 성공 여부
        """
        try:
            if tab_key not in UI_ELEMENTS:
                logger.warning(f"알 수 없는 탭 키: {tab_key}")
                return False
                
            tab_info = UI_ELEMENTS[tab_key]
            if 'active_class' in tab_info:
                active_class = tab_info['active_class']
                selector = tab_info['dom_selector']
                
                # 탭이 활성화될 때까지 대기
                start_time = time.time()
                while time.time() - start_time < timeout:
                    try:
                        element = self.driver.find_element(By.XPATH, selector)
                        class_attr = element.get_attribute('class')
                        
                        if active_class in class_attr:
                            logger.info(f"{tab_key} 탭 활성화 확인")
                            return True
                    except Exception as e:
                        logger.debug(f"탭 상태 확인 중 오류: {e}")
                        
                    time.sleep(0.2)  # 약간의 대기 후 다시 확인
                    
                logger.warning(f"{tab_key} 탭 활성화 대기 시간 초과 ({timeout}초)")
                return False
            else:
                logger.info(f"{tab_key}에 active_class 정보가 없어 활성화 여부를 확인할 수 없음")
                time.sleep(1)  # 활성화 확인을 스킵하는 경우, 기본 대기 시간 적용
                return True
        except Exception as e:
            logger.error(f"탭 활성화 확인 중 오류: {e}")
            return False

    def _edit_product_memo(self):
        """
        4-8. 메모 편집 프로세스
        - 메모편집 모달창 열기
        - 메모 내용 확인 및 복사
        - 메모 내용 수정 (접미사 추가)
        - 메모 저장 및 모달창 닫기
        
        Returns:
            bool: 성공 여부
        """
        try:
            # 4. 메모편집 모달창 열기
            logger.info("4. 메모편집 모달창 열기")
            if not smart_click(self.driver, UI_ELEMENTS["MEMO_MODAL_OPEN"], DELAY_SHORT):
                logger.error("메모편집 모달창 열기 실패")
                return False
            
            # 5. 상품 목록에 메모 내용 노출하기 체크박스 상태 확인
            logger.info("5. 상품 목록에 메모 내용 노출하기 체크박스 상태 확인")
            try:
                # 체크박스 상태 확인 (이미 체크되어 있는지)
                checkbox = wait_for_element(self.driver, By.XPATH, 
                                            "//input[@type='checkbox'][contains(@class, 'ant-checkbox-input')]", 
                                            timeout=2, raise_exception=False)
                if checkbox and checkbox.is_selected():
                    logger.info("상품 목록에 메모 내용 노출하기가 이미 체크되어 있음. 클릭하지 않음")
                else:
                    # 체크되어 있지 않으면 클릭
                    logger.info("상품 목록에 메모 내용 노출하기 체크박스 클릭 시도")
                    checkbox_label = wait_for_element(self.driver, By.XPATH, 
                                                    "//label[contains(@class, 'ant-checkbox-wrapper')]", 
                                                    timeout=1, raise_exception=False)
                    if checkbox_label:
                        checkbox_label.click()
                        logger.info("상품 목록에 메모 내용 노출하기 체크박스 클릭 완료")
            except Exception as e:
                logger.warning(f"체크박스 상태 확인 및 클릭 중 오류: {e}")
                # 오류가 발생해도 계속 진행 (비필수 단계)
                
            # 6. 상품에 대한 메모 textarea 클릭
            logger.info("6. 상품에 대한 메모 textarea 클릭")
            if not smart_click(self.driver, UI_ELEMENTS["PRODUCT_MEMO_TEXTAREA"], DELAY_MEDIUM):
                logger.error("메모 텍스트 영역 클릭 실패")
                return False
                
            # 7. 메모 내용 가져오기 및 복사
            logger.info("7. 메모 내용 가져오기 및 복사")
            try:
                # 키보드 단축키 모듈 초기화
                # 전체 선택 (Ctrl+A)
                self.keyboard.select_all()
                # 복사 (Ctrl+C)
                self.keyboard.copy()
                
                # 클립보드에서 메모 내용 가져오기
                import pyperclip
                self.original_memo = pyperclip.paste().strip()
                logger.info(f"원본 메모 내용: {self.original_memo}")
                
                # 다시 전체 선택 후 메모 내용 수정 (접미사 -S 추가)
                self.keyboard.select_all()
                modified_memo = f"{self.original_memo}-S"
                self.keyboard.type_text(modified_memo)
                logger.info(f"수정된 메모 내용 입력 완료: {modified_memo}")
                
            except Exception as e:
                logger.error(f"메모 내용 처리 중 오류: {e}")
                return False
                
            # 8. 메모 저장 버튼 클릭
            logger.info("8. 메모 저장 버튼 클릭")
            if not smart_click(self.driver, UI_ELEMENTS["PRODUCT_MEMO_SAVE"], DELAY_MEDIUM):
                logger.error("메모 저장 버튼 클릭 실패")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"메모 편집 중 오류 발생: {e}")
            return False

    def process_single_product(self):
        """
        단일 상품에 대한 전체 수정 프로세스 실행 (2번~24번)
        모든 단계를 순차적으로 실행하고 결과 반환
        
        Returns:
            bool: 성공 여부
        """
        try:
            # 2. 첫번째 상품 클릭 시도 (재시도 로직 포함)
            max_attempts = 3
            success = False
            
            for attempt in range(max_attempts):
                try:
                    # _click_first_product 메소드 사용 - DOM 선택자 우선 시도 후 좌표 사용
                    logger.info(f"첫번째 상품 클릭 시도 ({attempt+1}/{max_attempts}) - DOM 선택자 우선")
                    if self._click_first_product():
                        # 클릭 후 모달창이 열렸는지 확인
                        if self._check_modal_open(max_wait=5):
                            logger.info("첫번째 상품 클릭 및 모달창 열림 확인 성공")
                            success = True
                            break
                        else:
                            logger.warning(f"첫번째 상품 클릭 후 모달창 열림 확인 실패 ({attempt+1}/{max_attempts})")
                    
                    # 성공하지 못한 경우
                    if not success:
                        logger.warning("DOM 선택자 및 좌표 클릭 실패 또는 모달창 열리지 않음")
                        time.sleep(1)  # 잠시 대기 후 재시도
                except Exception as e:
                    logger.error(f"첫번째 상품 클릭 중 오류 발생: {e} ({attempt+1}/{max_attempts})")
                    time.sleep(1)  # 오류 발생 시 대기 후 재시도
            
            if not success:
                logger.error("최대 시도 횟수 초과 - 첫번째 상품 클릭 또는 모달창 열림 확인 실패")
                # 페이지 소스 저장 (디버깅용)
                try:
                    with open("modal_failure_page.html", "w", encoding="utf-8") as f:
                        f.write(self.driver.page_source)
                    logger.info("페이지 소스를 modal_failure_page.html에 저장했습니다 (디버깅용)")
                except Exception as save_err:
                    logger.warning(f"페이지 소스 저장 실패: {save_err}")
                return False  # 전체 자동화 중단

            # 3. 상품목록에 메모내용 숨기기 클릭
            # logger.info("상품목록에 메모내용 숨기기 클릭")
            # 상품목록에 메모내용 숨기기 클릭 - 상대좌표 사용용
            # self.smart_click(UI_ELEMENTS["MEMO_MODAL_CLOSE"], DELAY_VERY_SHORT)
            
            # 4. 메모편집 모달창 열기
            logger.info("4. 메모편집 모달창 열기")
            # 메모편집 모달창 열기 클릭 - 하이브리드 방식 사용 (대기시간 최소화)
            smart_click(self.driver, UI_ELEMENTS["MEMO_MODAL_OPEN"], DELAY_VERY_SHORT2)

            # 5. 상품 목록에 메모 내용 노출하기 클릭 - 체크되지 않은 경우에만 클릭
            logger.info("5. 상품 목록에 메모 내용 노출하기 체크박스 상태 확인")
            try:
                # 체크박스 요소 찾기
                checkbox_selector = UI_ELEMENTS["MEMO_MODAL_CHECKBOX"]["dom_selector"]
                checkbox_element = self.driver.find_element(By.XPATH, checkbox_selector)
                
                # 부모 요소 찾기 (체크 상태가 부모 label 클래스에 표시됨)
                parent_element = checkbox_element.find_element(By.XPATH, "./ancestor::label")
                
                # 체크 상태 확인 (ant-checkbox-wrapper-checked 클래스가 있는지 확인)
                is_checked = "ant-checkbox-wrapper-checked" in parent_element.get_attribute("class")
                
                if is_checked:
                    logger.info("상품 목록에 메모 내용 노출하기가 이미 체크되어 있음. 클릭하지 않음")
                else:
                    logger.info("상품 목록에 메모 내용 노출하기가 체크되지 않음. 클릭 시도")
                    smart_click(self.driver, UI_ELEMENTS["MEMO_MODAL_CHECKBOX"], DELAY_VERY_SHORT2)
            except Exception as e:
                logger.warning(f"체크박스 상태 확인 중 오류 발생: {e}. 기본적으로 클릭 시도")
                # 오류 발생 시 일단 클릭 시도
                smart_click(self.driver, UI_ELEMENTS["MEMO_MODAL_CHECKBOX"], DELAY_VERY_SHORT2 if 'DELAY_VERY_SHORT2' in globals() else PEC_DELAY_SHORT)

            # 6. 상품에 대한 메모 textarea 클릭
            logger.info("6. 상품에 대한 메모 textarea 클릭")
            # 상품에 대한 메모 textarea 클릭 - 하이브리드 방식 사용
            smart_click(self.driver, UI_ELEMENTS["MEMO_MODAL_TEXTAREA"], DELAY_VERY_SHORT5)
            
            # 7. 메모 내용 가져오고 수정하기
            logger.info("7. 메모 내용 가져오기 및 복사")
            original_memo = ""
            try:
                # 키보드 단축키 클래스 초기화
                keyboard = KeyboardShortcuts(self.driver)
                
                # textarea 요소 찾기
                textarea_selector = UI_ELEMENTS["MEMO_MODAL_TEXTAREA"]["dom_selector"]
                textarea_element = self.driver.find_element(By.XPATH, textarea_selector)
                
                # 현재 textarea의 내용 가져오기
                original_memo = textarea_element.get_attribute("value")
                logger.info(f"원본 메모 내용: {original_memo}")
                
                # 텍스트 영역 클릭
                textarea_element.click()
                
                # 키보드 단축키를 사용하여 전체 선택 및 복사
                keyboard.select_all(delay=DELAY_VERY_SHORT2)
                keyboard.copy(delay=DELAY_VERY_SHORT2)
                
                logger.info("메모 내용이 클립보드에 복사되었습니다.")
                
                # 복사한 후 원본 메모에 -S 추가하기
                modified_memo = original_memo + "-S"
                
                # 텍스트 영역 클릭 후 전체 선택하고 바로 수정된 텍스트 입력
                textarea_element.click()
                keyboard.select_all(delay=DELAY_VERY_SHORT2)  # 전체 선택
                keyboard.press_keys(modified_memo, delay=DELAY_VERY_SHORT2)  # 수정된 텍스트 입력
                logger.info(f"수정된 메모 내용 입력 완료: {modified_memo}")
                
                # 클립보드에 원본 메모 저장 (다음 단계에서 사용)
                self.original_memo_text = original_memo
                
            except Exception as e:
                logger.warning(f"메모 내용 처리 중 오류 발생: {e}")
                # 오류 발생 시 기본값 설정
                self.original_memo_text = original_memo  # 가져온 값이 있다면 그것을 사용
            
            # 8. 메모 저장 버튼 클릭
            logger.info("8. 메모 저장 버튼 클릭")
            smart_click(self.driver, UI_ELEMENTS["MEMO_MODAL_SAVEBUTTON"], DELAY_VERY_SHORT)

            # 9. 상세페이지 탭 선택 (하이브리드방식)
            logger.info("9. 상세페이지 탭 선택")
            smart_click(self.driver, UI_ELEMENTS["PRODUCT_TAB_DETAIL"], DELAY_VERY_SHORT)
            # 탭이 활성화될 때까지 명시적 대기
            self.wait_for_tab_active("PRODUCT_TAB_DETAIL")

            # 10. HTML 삽입 버튼 클릭 (하이브리드방식)
            logger.info("10. HTML 삽입 버튼 클릭")
            smart_click(self.driver, UI_ELEMENTS["PRODUCT_HTMLSOURCE_OPEN"], DELAY_VERY_SHORT)

            # 11.  HTML 삽입 TEXTAREA 클릭 (하이브리드방식)
            logger.info("11.  HTML 삽입 TEXTAREA 클릭")
            smart_click(self.driver, UI_ELEMENTS["PRODUCT_HTMLSOURCE_TEXTAREA"], DELAY_VERY_SHORT5)

            # 12.  상품메모 복사한 original 을 붙여넣기
            logger.info("12. 상품메모 원본 내용 붙여넣기")
            try:
                # 키보드 단축키 클래스 초기화
                keyboard = KeyboardShortcuts(self.driver)
                
                # HTML 삽입 textarea 요소 찾기
                textarea_selector = UI_ELEMENTS["PRODUCT_HTMLSOURCE_TEXTAREA"]["dom_selector"]
                textarea_element = self.driver.find_element(By.XPATH, textarea_selector)
                
                # 텍스트 영역 클릭 후 전체 선택 (현재 내용을 지우기 위해)
                textarea_element.click()
                keyboard.select_all(delay=DELAY_VERY_SHORT2)  # 전체 선택
                
                # 클립보드에 저장된 원본 메모 붙여넣기
                keyboard.paste(delay=DELAY_VERY_SHORT2)
                logger.info(f"원본 메모 붙여넣기 완료: '{self.original_memo_text}'")
            except Exception as e:
                logger.warning(f"HTML 삽입 영역에 메모 붙여넣기 실패: {e}")
                if hasattr(self, 'original_memo_text') and self.original_memo_text:
                    # 오류 발생 시 직접 텍스트 입력 시도
                    try:
                        textarea_element.clear()
                        textarea_element.send_keys(self.original_memo_text)
                        logger.info(f"직접 입력 방식으로 원본 메모 입력 완료")
                    except Exception as sub_e:
                        logger.error(f"직접 입력 방식도 실패: {sub_e}")
            
            # 13.  HTML 삽입 저장 버튼 클릭 (좌표만 사용)
            logger.info("13.  HTML 삽입 저장 버튼 클릭")
            # DOM 선택자가 실패하는 경우가 있으므로 좌표만 사용
            smart_click(self.driver, UI_ELEMENTS["PRODUCT_HTMLSOURCE_SAVE"], DELAY_VERY_SHORT)

            # 14. 상세페이지의 이미지 수량이 30개 이상인 경우, 31번째 이미지부터 모두 삭제하기
            logger.info("14. 31번째 이후의 이미지 삭제")
            try:
                # image_utils.py에서 이미지 관리자 가져오기
                from image_utils import PercentyImageManager
                
                # 이미지 관리자 초기화
                image_manager = PercentyImageManager(self.driver)
                
                # 일괄편집 모달 창 열기
                if image_manager.open_bulk_edit_modal():
                    # 이미지 개수 확인
                    image_count = image_manager.get_image_count()
                    logger.info(f"현재 이미지 개수: {image_count}개")
                    
                    if image_count > 30:
                        # 30개 이상의 이미지는 삭제 (31번째 이미지부터 삭제)
                        result = image_manager.delete_images_beyond_limit(limit=30, timeout=10)
                        logger.info(f"31번째 이후 이미지 삭제 결과: {'성공' if result else '실패'}")
                    else:
                        logger.info(f"이미지 개수가 30개 이하({image_count}개)이므로 삭제하지 않음")
                    
                    # 일괄편집 모달 창 닫기 (ESC 키 사용)
                    # image_manager에 close_bulk_edit_modal 메서드가 없으므로 keyboard_shortcuts.py의 기능 사용
                    
                    # 키보드 단축키 객체 초기화 (파일 상단에서 임포트한 모듈 사용)
                    keyboard = KeyboardShortcuts(self.driver)
                    
                    # ESC 키를 누르면 모달창이 닫힙
                    keyboard.escape_key(use_selenium=True, delay=DELAY_SHORT)
                    logger.info("일괄편집 모달창 ESC 키로 닫기 성공")
                else:
                    logger.warning("일괄편집 모달 창을 열 수 없어 이미지 삭제 실패")
            except ImportError as ie:
                logger.error(f"image_utils.py 모듈을 찾을 수 없습니다: {ie}")
                # 오류가 발생해도 계속 진행
            except Exception as e:
                logger.error(f"상세페이지 이미지 삭제 중 오류 발생: {e}")
                # 오류가 발생해도 계속 진행
            
            # 잠시 대기
            time.sleep(DELAY_VERY_SHORT)

            # 15.  업로드 탭 선택 (하이브리드방식)
            logger.info("15.  업로드 탭 선택")
            smart_click(self.driver, UI_ELEMENTS["PRODUCT_TAB_UPLOAD"], DELAY_VERY_SHORT2)
            # 탭이 활성화될 때까지 명시적 대기
            self.wait_for_tab_active("PRODUCT_TAB_UPLOAD")

            # 16.  상품정보고시 섹션 클릭 (DOM 선택자 사용으로 개선)
            logger.info("16.  상품정보고시 섹션 클릭 (DOM 선택자 방식)")
            # 새로 추가한 DOM 선택자 기반 UI 요소 사용 (대기시간 소폭 최소화)
            smart_click(self.driver, UI_ELEMENTS["PRODUCT_INFO_DISCLOSURE"], DELAY_VERY_SHORT5)
            
            # 섹션이 열렸는지 동적 확인 (개선된 방식)
            section_opened = False
            max_attempts = 3
            
            for attempt in range(max_attempts):
                try:
                    # 섹션이 열렸는지 WebDriverWait로 확인
                    wait = WebDriverWait(self.driver, 2)  # 2초 대기
                    disclosure_opened = wait.until(
                        EC.presence_of_element_located((By.XPATH, dom_selectors["PRODUCT_INFO_DISCLOSURE_OPENED"]))
                    )
                    
                    if disclosure_opened:
                        logger.info(f"상품정보제공고시 섹션이 성공적으로 열렸습니다 (시도 {attempt+1}/{max_attempts})")
                        section_opened = True
                        break
                except TimeoutException:
                    logger.warning(f"상품정보제공고시 섹션이 열림 확인 실패 (시도 {attempt+1}/{max_attempts})")
                    
                    # 실패하면 다시 클릭 시도
                    if attempt < max_attempts - 1:
                        logger.info("상품정보제공고시 섹션 다시 클릭 시도")
                        self.smart_click(UI_ELEMENTS["PRODUCT_INFO_DISCLOSURE"], DELAY_VERY_SHORT5)
                        time.sleep(DELAY_VERY_SHORT)  # 잠시 대기
            
            # 모든 시도에도 실패했다면 좌표 클릭으로 시도
            if not section_opened:
                logger.warning("상품정보제공고시 섹션 DOM 선택자 방식 실패, 좌표 방식으로 재시도")
                # DOM 선택자 실패 시 좌표 클릭으로 폴백
                # UI_ELEMENTS에서 좌표 값 가져오기
                if "coordinates" in UI_ELEMENTS["PRODUCT_INFO_DISCLOSURE"]:
                    click_at_coordinates(self.driver, UI_ELEMENTS["PRODUCT_INFO_DISCLOSURE"]["coordinates"], DELAY_SHORT)
                else:
                    logger.warning("PRODUCT_INFO_DISCLOSURE에 좌표 정보가 없습니다.")
                time.sleep(DELAY_SHORT)  # 조금 더 긴 대기

            # 17. 정보고시 입력창 클릭 - 상세페이지 참조 플레이스홀더로 찾기
            logger.info("17. 정보고시 입력창 - 상세페이지 참조 입력창 접근")
            
            # DOM 선택자로 플레이스홀더 입력창 찾기
            js_focus = """
            var inputs = document.querySelectorAll('input[placeholder="상세페이지 참조"]');
            if (inputs.length > 1) {
                inputs[1].focus();
                inputs[1].click();
                return true;
            }
            return false;
            """
            
            # JavaScript로 포커스 설정 및 선택 시도
            result = self.driver.execute_script(js_focus)
            
            if result:
                logger.info("JavaScript로 상세페이지 참조 입력창 포커스 성공")
                
                # 입력창을 찾았으므로 JavaScript로 바로 전체 선택 시도
                js_select = """
                var inputs = document.querySelectorAll('input[placeholder="상세페이지 참조"]');
                if (inputs.length > 1) {
                    inputs[1].focus();
                    inputs[1].select();
                    return true;
                }
                return false;
                """
                select_result = self.driver.execute_script(js_select)
                if select_result:
                    logger.info("JavaScript로 입력창 전체 선택 성공")
            else:
                # JavaScript 실패 시에만 좌표 클릭 시도
                logger.warning("JavaScript 입력창 포커스 실패, 좌표 클릭 시도")
                smart_click(self.driver, UI_ELEMENTS["PRODUCT_UPLOADEDIT_2ndINPUT"], DELAY_VERY_SHORT)
                logger.info("정보고시 입력창 좌표 클릭 완료")
            
            time.sleep(DELAY_VERY_SHORT)  # 클릭 후 대기
            
            # 18. 원본 메모 입력 - JavaScript로 직접 입력
            logger.info("18. 원본 메모 입력 - JavaScript 직접 입력 방식")
            
            # 원본 메모 확인
            memo_text = ""
            if hasattr(self, 'original_memo_text') and self.original_memo_text:
                memo_text = self.original_memo_text
                logger.info(f"사용할 원본 메모: '{memo_text}'")
            else:
                logger.warning("원본 메모가 없습니다!")
                memo_text = "G64"  # 기본값 설정
            
            # Selenium 관련 키 상수 임포트
            from selenium.webdriver.common.keys import Keys
            
            try:
                # JavaScript+Selenium 조합 방식 - 가장 안정적인 입력 방식 (개선된 버전)
                logger.info(f"JavaScript+Selenium 개선된 조합 방식 시도: '{memo_text}'")
                
                # JavaScript로 모든 상세페이지 참조 입력창 요소 찾기
                js_find_all = """
                var inputs = Array.from(document.querySelectorAll('input[placeholder="상세페이지 참조"]'));
                return inputs.map(function(input) {
                    return {
                        element: input,
                        visible: !!(input.offsetWidth || input.offsetHeight || input.getClientRects().length),
                        position: input.getBoundingClientRect()
                    };
                });
                """
                elements = self.driver.execute_script(js_find_all)
                
                if elements and len(elements) > 0:
                    logger.info(f"상세페이지 참조 입력창 {len(elements)}개 발견")
                    
                    # 원하는 입력창 선택 (기본적으로 두 번째 요소 사용)
                    target_idx = 1 if len(elements) > 1 else 0
                    element = elements[target_idx]['element']
                    
                    # 요소가 보이는지 확인
                    is_visible = elements[target_idx]['visible']
                    if not is_visible:
                        logger.warning(f"선택한 입력창(인덱스 {target_idx})이 현재 화면에 보이지 않습니다. 스크롤 시도...")
                        # 요소가 보이지 않으면 스크롤로 보이게 하기
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                        time.sleep(DELAY_VERY_SHORT5)  # 스크롤 후 짧게 대기
                    
                    # 요소 클릭 및 기존 값 지우기
                    logger.info(f"입력창 클릭 및 기존 값 제거 시도")
                    self.driver.execute_script("arguments[0].click();", element)
                    self.driver.execute_script("arguments[0].value = '';", element)
                    time.sleep(DELAY_VERY_SHORT)  # 짧게 대기하여 안정성 향상
                    
                    # 값 입력 - 안정성을 위해 후속 작업 전에 실패 여부 확인 추가
                    try:
                        element.send_keys(memo_text)
                        logger.info(f"Selenium으로 입력 완료: '{memo_text}'")
                        time.sleep(DELAY_VERY_SHORT)  # 입력 후 짧게 대기
                        
                        # JavaScript로 blur 처리하여 포커스 이동 (키보드 입력 대체)
                        self.driver.execute_script("arguments[0].blur();", element)
                        logger.info("포커스 이동으로 입력 확정")
                        
                        # 입력값 확인 및 검증
                        for i in range(3):  # 최대 3회 반복 확인
                            current_value = self.driver.execute_script("return arguments[0].value;", element)
                            if current_value == memo_text:
                                logger.info(f"입력 성공 확인: '{current_value}'")
                                break
                            else:
                                logger.warning(f"입력 값이 예상과 다름 ({i+1}/3). 예상: '{memo_text}', 실제: '{current_value}'")
                                # 다시 시도
                                if i < 2:  # 마지막 시도가 아니면 재시도
                                    element.clear()
                                    time.sleep(DELAY_VERY_SHORT2)
                                    element.send_keys(memo_text)
                                    time.sleep(DELAY_VERY_SHORT2)
                                    self.driver.execute_script("arguments[0].blur();", element)
                    except Exception as input_err:
                        logger.error(f"입력 중 오류 발생: {input_err}")
                        raise
                else:
                    logger.warning("입력창 요소를 찾을 수 없습니다!")
                    raise Exception("정보고시 입력창 요소 찾기 실패")


                # 이미 위에서 값 확인을 완료했으므로 최소한의 대기만 적용
                time.sleep(DELAY_VERY_SHORT2)
                
                # 여기서 추가 입력 작업을 하지 않고 바로 19번으로 넘어감 (사용자 요청에 따름)
                # 18번 탭 클릭이 입력 확정 역할을 함
            except Exception as e:
                logger.warning(f"메모 붙여넣기 오류: {e}")
                # 오류 발생 시 백업 방식
                try:
                    import pyautogui
                    pyautogui.hotkey('ctrl', 'a')  # 전체 선택
                    time.sleep(DELAY_SHORT)
                    pyautogui.hotkey('ctrl', 'v')  # 붙여넣기
                    logger.info("백업 방법으로 붙여넣기 완료")
                except Exception as backup_error:
                    logger.error(f"백업 방법도 실패: {backup_error}")
            
            # 19.  상품명/카테고리 탭 선택 (하이브리드방식)   
            logger.info("19.  상품명/카테고리 탭 선택")
            smart_click(self.driver, UI_ELEMENTS["PRODUCT_TAB_BASIC"], DELAY_VERY_SHORT2)
            # 탭이 활성화될 때까지 명시적 대기
            self.wait_for_tab_active("PRODUCT_TAB_BASIC")

            # 20. 상품명 경고단어 및 중복단어 삭제 클릭 (함수)
            # 경고단어와 중복단어 수에 따라 '삭제하기' 버튼의 좌표가 다르므로, 아래의 DOM 선택자로 검색이 되면 클릭해주는 함수
            # DOM 구조 <div class="sc-eBMEME jgkSWq"><button type="button" class="ant-btn css-1li46mu ant-btn-link ant-btn-sm" style="color: rgba(0, 0, 0, 0.45);"><span>삭제하기</span></button></div>
            logger.info("20. 상품명 경고단어/중복단어 삭제하기 버튼 클릭 시도")
            try:
                # CSS 선택자로 삭제하기 버튼 찾기 시도
                delete_btn_css = "button.ant-btn-link span:contains('삭제하기')"
                
                # JavaScript로 삭제하기 버튼 찾기 및 몪든 버튼 클릭
                js_script = """
                // 모든 삭제하기 버튼 찾기
                var buttons = document.querySelectorAll('button.ant-btn-link');
                var deleteButtons = [];
                
                // 삭제하기 텍스트가 있는 모든 버튼 찾기
                for (var i = 0; i < buttons.length; i++) {
                    if (buttons[i].textContent.includes('삭제하기')) {
                        deleteButtons.push(buttons[i]);
                    }
                }
                
                // 발견된 버튼 개수 반환
                if (deleteButtons.length > 0) {
                    // 발견된 모든 버튼 클릭
                    for (var j = 0; j < deleteButtons.length; j++) {
                        deleteButtons[j].click();
                        // 클릭 후 약간의 지연
                        setTimeout(function() {}, 500);
                    }
                    return deleteButtons.length;
                }
                return 0;
                """
                
                button_count = self.driver.execute_script(js_script)
                if button_count > 0:
                    logger.info(f"{button_count}개의 삭제하기 버튼 클릭 성공")
                    # 삭제하기 버튼이 여러 개인 경우도 대기시간 최소화
                    time.sleep(DELAY_SHORT)  # 삭제 처리를 위한 최소한의 대기시간
                else:
                    logger.info("삭제하기 버튼 발견되지 않음, 삭제할 경고/중복 단어가 없을 수 있음")
                
                # 만약 JavaScript로 버튼을 모두 클릭했더라도, 시간차로 발생한 추가 버튼을 위해 XPath로 한번 더 시도
                try:
                    delete_btn_xpath = "//button[contains(@class, 'ant-btn-link')]//span[text()='삭제하기']"
                    delete_buttons = self.driver.find_elements(By.XPATH, delete_btn_xpath)
                    
                    if len(delete_buttons) > 0:
                        logger.info(f"XPath로 추가 {len(delete_buttons)}개의 삭제하기 버튼 발견, 클릭 시도")
                        for btn in delete_buttons:
                            btn.click()
                            time.sleep(DELAY_VERY_SHORT5)
                        logger.info("XPath로 모든 추가 삭제하기 버튼 클릭 완료")
                    else:
                        logger.info("XPath로도 삭제하기 버튼 발견되지 않음")
                except NoSuchElementException:
                    logger.info("XPath로도 삭제하기 버튼 발견되지 않음")
                except Exception as click_error:
                    logger.warning(f"XPath 버튼 클릭 중 오류: {click_error}")
            except Exception as e:
                logger.warning(f"삭제하기 버튼 처리 중 오류: {e}")
                # 오류 발생해도 계속 진행

            # 21. 상품명 TEXTAREA 클릭 (하이브리드방식) 
            logger.info("21. 상품명 TEXTAREA 클릭")
            smart_click(self.driver, UI_ELEMENTS["PRODUCT_NAMEEDIT_TEXTAREA"], DELAY_VERY_SHORT2)

            # 22. 기존의 상품명에 알파벳을 접미사로 순차적으로 붙여주는 함수
            logger.info("22. 상품명에 알파벳 접미사 추가 시작")
            try:
                # 현재 상품명 가져오기
                current_name = ""
                try:
                    # JavaScript로 현재 상품명 가져오기 - 여러 선택자 시도
                    js_script = """
                    // 여러 가지 가능한 선택자로 상품명 입력창 찾기
                    var nameInput = document.querySelector('input.ant-input[type="text"]') || 
                                    document.querySelector('textarea[placeholder="판매상품명을 입력하세요."]') ||
                                    document.querySelector('input.ant-input') ||
                                    document.querySelector('textarea.ant-input');
                    
                    // 페이지의 모든 input을 찾아서 값이 있는지 확인
                    if (!nameInput) {
                        var allInputs = document.querySelectorAll('input[type="text"]');
                        for (var i = 0; i < allInputs.length; i++) {
                            if (allInputs[i].value && allInputs[i].value.length > 5) {
                                nameInput = allInputs[i];
                                break;
                            }
                        }
                    }
                    
                    if (nameInput) {
                        return nameInput.value || "";
                    }
                    return "";
                    """
                    current_name = self.driver.execute_script(js_script)
                    
                    if not current_name:
                        # 다른 방법 시도 - DOM 탐색
                        selectors = [
                            "//input[contains(@class, 'ant-input')][@type='text']",
                            "//textarea[contains(@placeholder, '판매상품명')]",
                            "//input[@type='text'][contains(@class, 'ant-input')]",
                            "//textarea[contains(@class, 'ant-input')]"
                        ]
                        
                        for selector in selectors:
                            try:
                                elements = self.driver.find_elements(By.XPATH, selector)
                                for element in elements:
                                    value = element.get_attribute("value")
                                    if value and len(value) > 5:  # 유의미한 길이의 텍스트만 고려
                                        current_name = value
                                        logger.info(f"선택자 {selector}로 상품명 발견")
                                        break
                                if current_name:  # 값을 찾았으면 반복문 종료
                                    break
                            except Exception as selector_error:
                                logger.debug(f"선택자 {selector} 오류: {selector_error}")
                                continue
                    
                    logger.info(f"현재 상품명: {current_name}")
                except Exception as e:
                    logger.warning(f"상품명 가져오기 오류: {e}")
                
                if not current_name:
                    logger.warning("상품명을 가져올 수 없어 건너뛰기")
                else:
                    # 상품명 수정 시작 - product_name_editor.py 모듈만 사용
                    try:
                        # ProductNameEditor 클래스 임포트
                        from product_name_editor import ProductNameEditor
                        
                        # ProductNameEditor 인스턴스 생성
                        name_editor = ProductNameEditor(self.driver)
                        
                        # 상품명 수정 실행 - A에서 Z까지 순차적으로 접미사 부여
                        # suffix_index 전달하고 다음 상품을 위해 증가
                        result = name_editor.edit_product_name(self.suffix_index)
                        
                        # 순차적으로 A-Z 접미사 사용하기 위해 인덱스 증가
                        self.suffix_index = (self.suffix_index + 1) % 26
                        next_suffix = chr(65 + self.suffix_index)
                        logger.info(f"상품명 수정 결과: {'성공' if result else '실패'} (현재 인덱스: {self.suffix_index}, 다음 상품은 '{next_suffix}' 사용)")
                        
                        # 성공여부 기록
                        name_edit_success = result
                        
                        # 완료 후 대기 최소화
                        time.sleep(DELAY_VERY_SHORT5)
                        
                    except ImportError as ie:
                        logger.error(f"product_name_editor.py 모듈을 찾을 수 없습니다: {ie}")
                    except Exception as e:
                        logger.error(f"상품명 수정 중 오류 발생: {e}")
                    # 레가시 상품명 수정 제거 - 단일 방식으로 통합
                
            except Exception as e:
                logger.error(f"22번 단계 오류 발생: {e}")
                # 오류 발생해도 계속 진행

            # 23. 상품수정 모달창 나가기 (ESC 키로 나가기)            	
            logger.info("23. 상품수정 모달창 ESC 키로 나가기")
            # 파일 상단에서 임포트한 키보드 단축키 모듈 사용
            keyboard = KeyboardShortcuts(self.driver)
            keyboard.escape_key(use_selenium=True, delay=DELAY_VERY_SHORT5)
            logger.info("상품수정 모달창 ESC 키로 나가기 성공")
            time.sleep(DELAY_VERY_SHORT5)  # 모달창 닫힌 후 최소한의 대기만 적용

            # 24. 수정한 첫번째 상품을 신규수집 그룹으로 이동하기
            logger.info("24. 첫번째 상품을 신규수집 그룹으로 이동")
            try:
                # 드롭다운 관리자 가져오기 (생성자에서 초기화한 객체 사용)
                dropdown_manager = self.dropdown_manager
                
                # 기존 메서드를 사용하여 한번에 드롭박스 열고 그룹 선택 (원스텝)
                if dropdown_manager.select_product_group_by_name("신규수집", item_index=0):
                    logger.info("신규수집 그룹으로 이동 성공")
                else:
                    # 다른 접근 방식 시도 - 각 단계를 분리해서 진행
                    logger.warning("원스텝 방식 실패, 개별 드롭박스 열기 시도")
                    
                    # 1. 개별 드롭박스 열기
                    if dropdown_manager.open_product_item_dropdown(item_index=0):
                        logger.info("그룹 드롭박스 열기 성공")
                        time.sleep(DELAY_VERY_SHORT5)
                        
                        # 2. 신규수집 그룹 선택
                        if dropdown_manager.select_group_by_name("신규수집"):
                            logger.info("신규수집 그룹 선택 성공")
                        else:
                            # 3. 이름으로 선택이 실패할 경우 인덱스로 시도
                            logger.warning("이름으로 그룹 선택 실패, 인덱스로 시도")
                            # 신규수집은 대개 2번째 옆션 (0번은 그룹없음, 1번은 신규등록)
                            if dropdown_manager.select_group_by_index(2):
                                logger.info("인덱스로 그룹 선택 성공")
                            else:
                                logger.error("인덱스로도 그룹 선택 실패")
                    else:
                        logger.error("그룹 드롭박스 열기 실패")
                    
                # 변경사항이 반영될 수 있도록 대기 - 중요한 작업이지만 대기시간 최소화
                time.sleep(DELAY_VERY_SHORT5)
                
                # 그룹 이동 후 스크롤 위치를 최상단으로 초기화
                dropdown_manager.reset_scroll_position(delay=DELAY_VERY_SHORT2)
                
            except Exception as e:
                logger.error(f"상품 그룹 이동 중 오류 발생: {e}")
                # 오류가 발생해도 계속 진행
                
            logger.info("단일 상품 처리 완료")
            return True
            
        except Exception as e:
            logger.error(f"상품 처리 중 오류 발생: {e}")
            return False
