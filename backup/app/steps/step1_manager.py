# -*- coding: utf-8 -*-
"""
퍼센티 1단계 관리자: 신규상품수정

이 모듈은 퍼센티 자동화의 1단계(신규상품수정) 작업을 관리합니다.
"""

import logging
import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 기본 단계 관리자 임포트
from app.steps.base_step_manager import BaseStepManager

# 경로 설정
import sys
import os

# 프로젝트 루트 경로를 sys.path에 추가
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if root_path not in sys.path:
    sys.path.append(root_path)

# 기존 모듈 임포트
from product_editor_core import ProductEditorCore
from timesleep import *

# 유틸리티 함수 임포트
from click_utils import smart_click, click_by_selector
from menu_clicks import click_at_absolute_coordinates
from percenty_utils import hide_channel_talk_and_modals

# UI 요소 추가
from ui_elements import UI_ELEMENTS

# 페이지 로드 인디케이터 임포트
from dom_selectors import MENU_SELECTORS, EDITGOODS_SELECTORS as dom_selectors, PAGE_LOAD_INDICATORS

# 좌표계 시스템 임포트
from coordinates.coordinates_all import *  # 통합 좌표 시스템 사용

# 모달창 처리 함수 임포트
from modal_blocker import set_modal_cookies_and_storage, close_modal_dialog, press_escape_key, block_modals_on_page, is_modal_visible

logger = logging.getLogger(__name__)

class Step1Manager(BaseStepManager):
    """1단계 자동화 작업을 관리하는 클래스"""
    
    def __init__(self, driver):
        """
        초기화
        
        Args:
            driver: Selenium WebDriver 인스턴스
        """
        super().__init__(driver, "1단계: 신규상품수정", 1)
        self.product_editor = None
    
    def navigate_to_group_management(self):
        """
        그룹상품관리 화면으로 이동
        
        Returns:
            bool: 성공 여부
        """
        try:
            # 그룹상품관리 메뉴 클릭
            logger.info(f"{self.step_name} - 그룹상품관리 메뉴 클릭 시도")
            
            # 모달창 및 채널톡 숨기기 실행
            hide_channel_talk_and_modals(self.driver, log_prefix=self.step_name)
            
            # 모달창 처리
            try:
                # 모달창 다단계 처리 프로세스 적용
                logger.info(f"{self.step_name} - 모달창 강화된 처리 시작")
                
                # 1. 쿠키 및 로컬 스토리지 설정으로 모달창 미리 방지
                logger.info(f"{self.step_name} - 모달창 쿠키 및 스토리지 설정")
                storage_result = set_modal_cookies_and_storage(self.driver)
                logger.info(f"{self.step_name} - 모달창 쿠키 설정 결과: {storage_result}")
                
                # 2. 포괄적인 모달창 닫기 함수 사용
                logger.info(f"{self.step_name} - 모달창 닫기 전용 함수 호출")
                modal_result = close_modal_dialog(self.driver)
                logger.info(f"{self.step_name} - 모달창 닫기 결과: {modal_result}")
                
                # 3. 채널톡 숨기기 및 모달창 추가 처리
                logger.info(f"{self.step_name} - 채널톡 및 모달창 통합 처리 시작")
                chat_modal_result = hide_channel_talk_and_modals(self.driver, log_prefix=self.step_name)
                logger.info(f"{self.step_name} - 채널톡 및 모달창 통합 처리 결과: {chat_modal_result}")
                
                # 4. block_modals_on_page 함수로 최종 처리
                logger.info(f"{self.step_name} - block_modals_on_page 함수로 최종 모달창 처리")
                block_result = block_modals_on_page(self.driver)
                logger.info(f"{self.step_name} - block_modals_on_page 결과: {block_result}")
                
                # 5. ESC 키 입력
                logger.info(f"{self.step_name} - ESC 키를 눌러 모달창 닫기 시도")
                press_escape_key(self.driver)
                time.sleep(DELAY_SHORT)
                
                # 6. 모달 코어 사용
                self.modal_core.close_all_modals_and_popups()
                
            except Exception as modal_err:
                logger.warning(f"{self.step_name} - 모달창 처리 중 오류 (계속 진행): {str(modal_err)}")
            
            # 모달창 처리 후 그룹상품관리 메뉴 클릭
            logger.info(f"{self.step_name} - 그룹상품관리 메뉴 클릭 시도 (DOM + 좌표)")
            
            # DOM 선택자로 시도
            try:
                group_menu_selector = MENU_SELECTORS.get('group_product_management')
                if group_menu_selector:
                    menu_element = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, group_menu_selector))
                    )
                    menu_element.click()
                    logger.info(f"{self.step_name} - DOM 선택자로 그룹상품관리 메뉴 클릭 성공")
                    time.sleep(DELAY_MEDIUM)
                else:
                    logger.warning(f"{self.step_name} - 그룹상품관리 메뉴 선택자가 설정되지 않음")
            except Exception as dom_err:
                logger.warning(f"{self.step_name} - DOM 선택자로 그룹상품관리 메뉴 클릭 실패: {str(dom_err)}")
                
                # 좌표 기반 클릭 시도
                try:
                    from coordinates.coordinates_all import MENU
                    if 'GROUP_PRODUCT_MANAGEMENT' in MENU:
                        logger.info(f"{self.step_name} - 좌표 기반 그룹상품관리 메뉴 클릭 시도")
                        coords = MENU['GROUP_PRODUCT_MANAGEMENT']
                        click_at_absolute_coordinates(self.driver, coords[0], coords[1])
                        logger.info(f"{self.step_name} - 좌표 클릭 ({coords[0]}, {coords[1]}) 완료")
                        time.sleep(DELAY_MEDIUM)
                    else:
                        # 직접 URL 이동 시도
                        logger.warning(f"{self.step_name} - 그룹상품관리 메뉴 좌표가 설정되지 않음, URL 직접 이동 시도")
                        self.driver.get("https://www.percenty.co.kr/ai/group-products")
                        logger.info(f"{self.step_name} - 그룹상품관리 URL 이동 시도 완료")
                        time.sleep(DELAY_MEDIUM)
                except Exception as coord_err:
                    logger.warning(f"{self.step_name} - 좌표 기반 그룹상품관리 메뉴 클릭 실패: {str(coord_err)}")
                    
                    # 직접 URL 이동 시도
                    try:
                        logger.info(f"{self.step_name} - URL 직접 이동 시도")
                        self.driver.get("https://www.percenty.co.kr/ai/group-products")
                        logger.info(f"{self.step_name} - 그룹상품관리 URL 이동 시도 완료")
                        time.sleep(DELAY_MEDIUM)
                    except Exception as url_err:
                        logger.error(f"{self.step_name} - URL 직접 이동 실패: {str(url_err)}")
                        return False
            
            # 그룹상품관리 화면 로딩 확인
            try:
                # 페이지 로드 확인 인디케이터 사용
                page_indicators = PAGE_LOAD_INDICATORS.get('group_management_page', [])
                if not page_indicators:
                    # 기본 인디케이터 설정
                    page_indicators = [
                        (By.CSS_SELECTOR, "div.group-products"),
                        (By.CSS_SELECTOR, "button.non-group-btn")
                    ]
                
                logger.info(f"{self.step_name} - 그룹상품관리 화면 로드 확인 중...")
                load_success = self.wait_for_page_loaded(
                    page_indicators, 
                    max_wait=15, 
                    page_name="그룹상품관리"
                )
                
                if load_success:
                    logger.info(f"{self.step_name} - 그룹상품관리 화면 로드 확인 완료")
                    return True
                else:
                    logger.warning(f"{self.step_name} - 그룹상품관리 화면 로드 확인 실패. URL 확인 시도...")
                    
                    # URL 기반으로 추가 확인
                    current_url = self.driver.current_url
                    if "group-products" in current_url:
                        logger.info(f"{self.step_name} - URL 확인으로 그룹상품관리 화면 접근 확인됨: {current_url}")
                        time.sleep(DELAY_MEDIUM)  # 추가 대기
                        return True
                    else:
                        logger.error(f"{self.step_name} - 그룹상품관리 화면 URL 확인 실패: {current_url}")
                        return False
                
            except Exception as load_err:
                logger.error(f"{self.step_name} - 그룹상품관리 화면 로드 확인 중 오류: {str(load_err)}")
                return False
                
        except Exception as e:
            logger.error(f"{self.step_name} - 그룹상품관리 화면 이동 중 오류: {str(e)}")
            return False
    
    def wait_for_page_loaded(self, indicators, max_wait=10, check_interval=0.5, page_name="페이지"):
        """
        특정 화면이 로드되었는지 동적으로 확인하는 일반화된 메소드
        
        Args:
            indicators: 화면 로드 확인을 위한 선택자 목록 [(선택자타입, 선택자), ...]
            max_wait: 최대 대기 시간(초)
            check_interval: 확인 간격(초)
            page_name: 화면 이름 (로깅용)
            
        Returns:
            bool: 화면 로드 확인 성공 여부
        """
        try:
            logger.info(f"{self.step_name} - {page_name} 로드 확인 시작 (최대 {max_wait}초 대기)")
            
            start_time = time.time()
            while time.time() - start_time < max_wait:
                for indicator_type, indicator_value in indicators:
                    try:
                        element = self.driver.find_element(indicator_type, indicator_value)
                        if element.is_displayed():
                            logger.info(f"{self.step_name} - {page_name} 로드 확인됨 (인디케이터: {indicator_value})")
                            return True
                    except Exception:
                        # 이 인디케이터는 아직 로드되지 않음, 다른 인디케이터 확인
                        pass
                
                # 잠시 대기 후 다시 확인
                time.sleep(check_interval)
            
            # 최대 대기 시간 초과
            logger.warning(f"{self.step_name} - {page_name} 로드 확인 실패 (시간 초과: {max_wait}초)")
            return False
            
        except Exception as e:
            logger.error(f"{self.step_name} - {page_name} 로드 확인 중 오류: {str(e)}")
            return False
    
    def open_non_group_products(self, max_wait=10, check_interval=0.5):
        """
        비그룹상품보기 화면을 엽니다. 동적으로 상태 확인하여 기다립니다.
        
        Args:
            max_wait: 최대 대기 시간(초)
            check_interval: 확인 간격(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"{self.step_name} - 비그룹상품보기 열기 시도")
            
            # 현재 토글 상태 확인 함수
            def check_current_view_state():
                try:
                    # 버튼 텍스트로 확인
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, "button.non-group-btn")
                    for button in buttons:
                        if "비그룹상품보기" in button.text:
                            return "grouped"  # 현재 그룹상품보기 상태, 비그룹상품보기 버튼이 보임
                        elif "그룹상품보기" in button.text:
                            return "non_grouped"  # 현재 비그룹상품보기 상태, 그룹상품보기 버튼이 보임
                    
                    # URL로 보조 확인
                    current_url = self.driver.current_url
                    if "non-grouped=true" in current_url:
                        return "non_grouped"
                    elif "non-grouped=false" in current_url or "non-grouped" not in current_url:
                        return "grouped"
                    
                    return None  # 상태 확인 불가
                except Exception as e:
                    logger.warning(f"{self.step_name} - 현재 뷰 상태 확인 중 오류: {str(e)}")
                    return None
            
            # 토글 상태 확인 및 클릭 함수
            def check_toggle_state():
                # 현재 상태 확인
                current_state = check_current_view_state()
                logger.info(f"{self.step_name} - 현재 상태: {current_state}")
                
                # 비그룹상품보기로 전환 필요한 경우
                if current_state == "grouped" or current_state is None:
                    return False  # 클릭 필요
                else:
                    return True  # 이미 비그룹상품보기 상태
            
            # 현재 토글 상태 확인
            is_non_grouped = check_toggle_state()
            
            # 비그룹상품보기 토글 필요한 경우
            if not is_non_grouped:
                logger.info(f"{self.step_name} - 비그룹상품보기 토글 클릭 필요")
                
                # DOM 선택자로 시도
                try:
                    toggle_selector = "button.non-group-btn"
                    toggle_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, toggle_selector))
                    )
                    toggle_button.click()
                    logger.info(f"{self.step_name} - DOM 선택자로 비그룹상품보기 토글 클릭 성공")
                    time.sleep(DELAY_MEDIUM)
                except Exception as dom_err:
                    logger.warning(f"{self.step_name} - DOM 선택자로 비그룹상품보기 토글 클릭 실패: {str(dom_err)}")
                    
                    # 좌표 기반 클릭 시도
                    try:
                        # UI_ELEMENTS의 PRODUCT_VIEW_NOGROUP 사용
                        try:
                            from ui_elements import UI_ELEMENTS
                            
                            if "PRODUCT_VIEW_NOGROUP" in UI_ELEMENTS and "coordinates" in UI_ELEMENTS["PRODUCT_VIEW_NOGROUP"]:
                                logger.info(f"{self.step_name} - UI_ELEMENTS의 PRODUCT_VIEW_NOGROUP 좌표 기반 클릭 시도")
                                coords = UI_ELEMENTS["PRODUCT_VIEW_NOGROUP"]["coordinates"]
                                click_at_absolute_coordinates(self.driver, coords[0], coords[1])
                                logger.info(f"{self.step_name} - 좌표 클릭 ({coords[0]}, {coords[1]}) 완료")
                                time.sleep(DELAY_MEDIUM)
                            else:
                                # 이전 방식(레거시 지원) - coordinates_all에서 가져오기
                                from coordinates.coordinates_all import ACTION
                                if 'PRODUCT_VIEW_NOGROUP' in ACTION:
                                    logger.info(f"{self.step_name} - ACTION에서 PRODUCT_VIEW_NOGROUP 좌표 기반 클릭 시도")
                                    coords = ACTION['PRODUCT_VIEW_NOGROUP']
                                    click_at_absolute_coordinates(self.driver, coords[0], coords[1])
                                    logger.info(f"{self.step_name} - 좌표 클릭 ({coords[0]}, {coords[1]}) 완료")
                                    time.sleep(DELAY_MEDIUM)
                                else:
                                    # 마지막 수단 - coordinates_editgoods에서 가져오기
                                    from coordinates_editgoods import PRODUCT_MODAL_EDIT2
                                    if 'PRODUCT_VIEW_NOGROUP' in PRODUCT_MODAL_EDIT2:
                                        logger.info(f"{self.step_name} - PRODUCT_MODAL_EDIT2에서 PRODUCT_VIEW_NOGROUP 좌표 기반 클릭 시도")
                                        coords = PRODUCT_MODAL_EDIT2['PRODUCT_VIEW_NOGROUP']
                                        click_at_absolute_coordinates(self.driver, coords[0], coords[1])
                                        logger.info(f"{self.step_name} - 좌표 클릭 ({coords[0]}, {coords[1]}) 완료")
                                        time.sleep(DELAY_MEDIUM)
                                    else:
                                        logger.warning(f"{self.step_name} - 비그룹상품보기 토글 좌표가 어디서도 찾을 수 없음")
                        except ImportError as import_err:
                            logger.warning(f"{self.step_name} - 라이브러리 임포트 실패: {str(import_err)}")
                            # 예전 방식으로 시도(ACTION 젬표 폴백)
                            from coordinates.coordinates_all import ACTION
                            if 'NON_GROUP_TOGGLE' in ACTION:  # 이전 키 이름 호환성 유지
                                logger.info(f"{self.step_name} - 레거시 ACTION['NON_GROUP_TOGGLE'] 좌표 사용")
                                coords = ACTION['NON_GROUP_TOGGLE']
                                click_at_absolute_coordinates(self.driver, coords[0], coords[1])
                                logger.info(f"{self.step_name} - 좌표 클릭 ({coords[0]}, {coords[1]}) 완료")
                                time.sleep(DELAY_MEDIUM)
                            else:
                                logger.warning(f"{self.step_name} - 비그룹상품보기 토글 좌표가 설정되지 않음")
                    except Exception as coord_err:
                        logger.warning(f"{self.step_name} - 좌표 기반 비그룹상품보기 토글 클릭 실패: {str(coord_err)}")
                
                # 토글 클릭 후 상태 확인
                start_time = time.time()
                while time.time() - start_time < max_wait:
                    current_state = check_current_view_state()
                    if current_state == "non_grouped":
                        logger.info(f"{self.step_name} - 비그룹상품보기 전환 확인됨")
                        break
                    time.sleep(check_interval)
                
                # 여전히 비그룹상품보기 상태가 아닌 경우
                if check_current_view_state() != "non_grouped":
                    logger.warning(f"{self.step_name} - 비그룹상품보기 전환 확인 실패")
                    # URL 직접 변경 시도
                    try:
                        current_url = self.driver.current_url
                        if "non-grouped=true" not in current_url:
                            if "?" in current_url:
                                non_grouped_url = current_url + "&non-grouped=true"
                            else:
                                non_grouped_url = current_url + "?non-grouped=true"
                            
                            logger.info(f"{self.step_name} - URL로 비그룹상품보기 전환 시도: {non_grouped_url}")
                            self.driver.get(non_grouped_url)
                            time.sleep(DELAY_MEDIUM)
                    except Exception as url_err:
                        logger.warning(f"{self.step_name} - URL로 비그룹상품보기 전환 실패: {str(url_err)}")
                        return False
            else:
                logger.info(f"{self.step_name} - 이미 비그룹상품보기 상태입니다")
            
            # 비그룹상품보기 로딩 확인
            time.sleep(DELAY_MEDIUM)
            if check_current_view_state() == "non_grouped":
                logger.info(f"{self.step_name} - 비그룹상품보기 화면 로드 확인 완료")
                return True
            else:
                logger.warning(f"{self.step_name} - 비그룹상품보기 화면 로드 확인 실패")
                return False
                
        except Exception as e:
            logger.error(f"{self.step_name} - 비그룹상품보기 열기 중 오류: {str(e)}")
            return False
    
    def get_total_product_count(self):
        """
        비그룹상품보기 화면에서 총 상품 수량 확인
        
        Returns:
            int: 총 상품 수량
        """
        try:
            logger.info(f"{self.step_name} - 총 상품 수량 확인 시도")
            
            # DOM 선택자로 시도
            try:
                count_selector = "span.total-count"
                count_element = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, count_selector))
                )
                count_text = count_element.text.strip()
                
                # 텍스트에서 숫자 추출 (예: "총 2,150개 상품" -> 2150)
                import re
                count_match = re.search(r'(\d[\d,]*)', count_text)
                if count_match:
                    count_str = count_match.group(1).replace(',', '')
                    total_count = int(count_str)
                    logger.info(f"{self.step_name} - 총 상품 수량: {total_count}개")
                    return total_count
                else:
                    logger.warning(f"{self.step_name} - 상품 수량 텍스트 파싱 실패: '{count_text}'")
                    return 0
            except Exception as e:
                logger.warning(f"{self.step_name} - 총 상품 수량 확인 실패: {str(e)}")
                return 0
        except Exception as e:
            logger.error(f"{self.step_name} - 총 상품 수량 확인 중 오류: {str(e)}")
            return 0
    
    def run_automation(self):
        """
        1단계 자동화 실행
        
        Returns:
            bool: 성공 여부
        """
        if not self.batch_info or not self.batch_info.get('quantity'):
            logger.error("배치 정보가 설정되지 않았습니다. 자동화를 중단합니다.")
            return False
        
        self.is_running = True
        processed = 0
        
        # 배치 ID를 가져옴
        batch_id = self.batch_info['batch_id']
        
        try:
            # 로그인
            login_success = self.login_percenty()
            if not login_success:
                logger.error("로그인 실패. 자동화를 중단합니다.")
                # 실패 상태는 반환만
                return False
            
            # 그룹상품관리로 이동
            success = self.navigate_to_group_management()
            if not success:
                logger.error("그룹상품관리 화면으로 이동 실패. 자동화를 중단합니다.")
                # 실패 상태는 반환만
                return False
            
            # 비그룹상품보기 열기
            success = self.open_non_group_products()
            if not success:
                logger.error("비그룹상품보기 열기 실패. 자동화를 중단합니다.")
                # 실패 상태는 반환만
                return False
            
            # 총 상품 수량 확인 (배치 시작 전)
            initial_product_count = self.get_total_product_count()
            if initial_product_count <= 0:
                logger.error("처리할 상품이 없습니다. 자동화를 중단합니다.")
                # 실패 상태는 반환만
                return False
            
            # 배치 시작 전 상품 수량 저장
            self.initial_product_count = initial_product_count
            
            # 실제 처리할 수량 결정 (가용 상품과 요청 수량 중 작은 값)
            process_count = min(self.batch_info['quantity'], initial_product_count)
            logger.info(f"총 {initial_product_count}개 상품 중 {process_count}개 처리 예정")
            logger.info(f"📊 배치 시작 전 비그룹상품 수량: {initial_product_count}개")
            
            # 상품 편집기 초기화
            self.product_editor = ProductEditorCore(self.driver)
            
            # 배치 작업 시작
            while processed < process_count and self.is_running:
                # 20개마다 화면 새로고침
                if processed > 0 and processed % 20 == 0:
                    logger.info(f"{processed}개 처리 완료. 화면 새로고침을 실행합니다.")
                    self.refresh_page()
                    
                    # 새로고침 후 비그룹상품보기 다시 확인
                    success = self.open_non_group_products()
                    if not success:
                        logger.error("새로고침 후 비그룹상품보기 열기 실패. 자동화를 중단합니다.")
                        # 실패 상태는 반환만
                        return False
                    
                    # 잠시 대기
                    time.sleep(DELAY_SHORT)
                
                # 단일 상품 처리
                success = self.product_editor.process_single_product()
                
                if success:
                    processed += 1
                    # 배치 업데이트는 반환값으로 처리하고 여기서는 기록만
                    logger.info(f"처리 진행중: {processed}/{process_count}")
                    logger.info(f"상품 처리 완료: {processed}/{process_count} (총 진행률: {processed/process_count*100:.1f}%)")
                else:
                    # 실패 시 로그만 남기고 계속 진행
                    logger.warning("상품 처리 실패. 다음 상품으로 넘어갑니다.")
                
                # 잠시 대기
                time.sleep(random.uniform(DELAY_SHORT, DELAY_MEDIUM))
            
            # 배치 완료 후 상품 수량 확인 및 비교
            try:
                final_product_count = self.get_total_product_count()
                actual_processed = initial_product_count - final_product_count
                
                # 배치 완료 후 상품 수량 정보 저장
                self.final_product_count = final_product_count
                self.processed_count = processed
                self.actual_processed_count = actual_processed
                
                logger.info(f"📊 배치 완료 후 비그룹상품 수량: {final_product_count}개")
                logger.info(f"📊 실제 처리된 상품 수량: {actual_processed}개 (감소량 기준)")
                logger.info(f"📊 요청 처리 수량: {processed}개")
                
                # 처리 결과 분석
                if actual_processed == processed:
                    logger.info(f"✅ 누락 없이 정상 처리 (처리량과 감소량 일치)")
                elif actual_processed > processed:
                    logger.warning(f"⚠️ 예상보다 많은 상품이 처리됨 (차이: +{actual_processed - processed}개)")
                elif actual_processed < processed:
                    logger.warning(f"⚠️ 일부 상품이 누락되었을 수 있음 (차이: -{processed - actual_processed}개)")
                    
            except Exception as count_error:
                logger.warning(f"배치 완료 후 상품 수량 확인 실패: {str(count_error)}")
                # 오류 시 기본값 설정
                self.final_product_count = None
                self.actual_processed_count = None
            
            # 작업 완료 상태 기록
            if processed >= process_count:
                logger.info(f"1단계 자동화 완료. 총 {processed}개 상품 처리됨.")
                return True
            else:
                logger.info(f"1단계 자동화 중단됨. {processed}개 상품 처리됨.")
                return False
                
        except Exception as e:
            logger.error(f"1단계 자동화 중 오류 발생: {str(e)}")
            return False
        finally:
            self.is_running = False
