"""
퍼센티 상품 수정 자동화 스크립트 1단계 (신규 버전)
비그룹상품보기에 있는 상품을 수정한 후, 신규수집 그룹으로 이동하기
- 하이브리드 좌표 방식 적용
"""

import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# 하이브리드 좌표 시스템 임포트
from click_utils import hybrid_click, click_by_selector, click_at_coordinates, smart_click
# UI 요소와 좌표는 ui_elements.py에서 중앙화하여 가져오기
# DOM 선택자 임포트
from dom_selectors import MENU_SELECTORS, EDITGOODS_SELECTORS as dom_selectors, PAGE_LOAD_INDICATORS
from ui_elements import UI_ELEMENTS
# 키보드 단축키 유틸리티 임포트
from keyboard_shortcuts import KeyboardShortcuts
# from dom_selectors import MENU_SELECTORS

# 통합 유틸리티 모듈 임포트
from percenty_utils import hide_channel_talk_and_modals, periodic_ui_cleanup, ensure_clean_ui_before_action
# 새 탭에서의 로그인 모달창 숨기기 필요할 경우에만 사용
from login_modal_utils import apply_login_modal_hiding_for_new_tab

# 드롭다운 유틸리티 임포트
from dropdown_utils import get_dropdown_manager

# 상품 편집 코어 기능 임포트
from product_editor_core import ProductEditorCore

# 키보드 단축키 유틸리티 임포트
from keyboard_shortcuts import KeyboardShortcuts

# 시간 지연 상수 모듈에서 가져오기
from timesleep import (
    DELAY_VERY_SHORT2,
    DELAY_VERY_SHORT5,
    DELAY_VERY_SHORT,
    DELAY_SHORT,
    DELAY_MEDIUM,
    DELAY_STANDARD,  # 비그룹상품보기 토글 클릭 후 대기시간에 사용
    DELAY_LONG,
    DELAY_EXTRA_LONG as DELAY_VERY_LONG  # 이름 변경된 상수 매핑
)

# 로깅 설정
logger = logging.getLogger(__name__)

class PercentyNewStep1:
    def __init__(self, driver, browser_ui_height=95):
        """
        퍼센티 상품 수정 자동화 스크립트 1단계 초기화
        
        Args:
            driver: 셀레니움 웹드라이버 인스턴스
            browser_ui_height: 브라우저 UI 높이 (기본값: 95px)
        """
        self.driver = driver
        self.browser_ui_height = browser_ui_height
        logger.info("===== 퍼센티 상품 수정 자동화 스크립트 1단계 초기화 =====")
        
        # 브라우저 내부 크기 확인
        self.inner_width = self.driver.execute_script("return window.innerWidth")
        self.inner_height = self.driver.execute_script("return window.innerHeight")
        logger.info(f"브라우저 내부 크기: {self.inner_width}x{self.inner_height}")
        
        # 드롭다운 관리자 초기화
        self.dropdown_manager = get_dropdown_manager(driver)

    # 하이브리드 방식으로 변경됨 - 모든 좌표 변환은 click_utils.py에서 처리

    def click_at_coordinates(self, coords, delay_type=DELAY_SHORT, use_js=True):
        """
        주어진 좌표를 클릭 (하이브리드 방식으로 변경)
        
        Args:
            coords: (x, y) 좌표 튜플
            delay_type: 클릭 후 대기 시간
            use_js: JavaScript로 클릭할지 여부
        """
        # click_utils.py의 click_at_coordinates 함수 호출
        result = click_at_coordinates(self.driver, coords, delay_type)
        return result
        
    def smart_click(self, ui_element, delay_type=DELAY_SHORT):
        """
        DOM 선택자와 좌표를 함께 사용하는 하이브리드 클릭 방식
        ui_elements.py에 정의된 UI 요소를 사용하여 fallback_order 기반으로 시도
        
        Args:
            ui_element: ui_elements.py에 정의된 UI 요소 딕셔너리
            delay_type: 클릭 후 대기 시간
        
        Returns:
            bool: 클릭 성공 여부
        """
        # click_utils.py의 smart_click 함수 호출
        return smart_click(self.driver, ui_element, delay_type)
        
    def wait_for_tab_active(self, tab_name, max_wait=10, check_interval=0.5):
        """
        탭이 활성화될 때까지 대기하는 함수 - 향상된 버전
        여러 방식으로 탭 활성화 여부를 검증하여 안정성을 높임
        
        Args:
            tab_name: 탭 이름 ("PRODUCT_TAB_DETAIL", "PRODUCT_TAB_UPLOAD", "PRODUCT_TAB_BASIC" 등)
            max_wait: 최대 대기 시간(초)
            check_interval: 확인 간격(초)
            
        Returns:
            bool: 탭 활성화 성공 여부
        """
        logger.info(f"{tab_name} 탭이 활성화될 때까지 대기 (최대 {max_wait}초)")
        
        # 중앙 관리되는 PAGE_LOAD_INDICATORS에서 정확한 탭 활성화 확인 선택자 매핑
        tab_active_selectors = {
            "PRODUCT_TAB_BASIC": PAGE_LOAD_INDICATORS["PRODUCT_TAB_BASIC_ACTIVE"],
            "PRODUCT_TAB_OPTION": PAGE_LOAD_INDICATORS["PRODUCT_TAB_OPTION_ACTIVE"],
            "PRODUCT_TAB_PRICE": PAGE_LOAD_INDICATORS["PRODUCT_TAB_PRICE_ACTIVE"],
            "PRODUCT_TAB_IMAGE": PAGE_LOAD_INDICATORS["PRODUCT_TAB_THUMBNAIL_ACTIVE"],  # 이미지 탭은 썸네일 탭으로 매핑
            "PRODUCT_TAB_DETAIL": PAGE_LOAD_INDICATORS["PRODUCT_TAB_DETAIL_ACTIVE"],
            "PRODUCT_TAB_UPLOAD": PAGE_LOAD_INDICATORS["PRODUCT_TAB_UPLOAD_ACTIVE"],
            "PRODUCT_TAB_KEYWORD": PAGE_LOAD_INDICATORS["PRODUCT_TAB_KEYWORD_ACTIVE"]
            # CONFIG 탭은 없어서 제거함
        }
        
        # 탭에 맞는 활성화 확인 선택자 가져오기
        active_selector = tab_active_selectors.get(tab_name)
        if not active_selector:
            logger.warning(f"{tab_name}에 대한 활성화 확인 선택자가 없습니다. 기본 선택자를 사용합니다.")
            # 기본 CSS 선택자 사용 (모든 탭에 공통적으로 적용 가능한 선택자)
            indicators = [(By.CSS_SELECTOR, ".ant-tabs-tabpane-active")]
        else:
            indicators = [(By.XPATH, active_selector)]
            
        # 추가적인 공통 선택자 - 모든 탭에 적용 가능한 대체 선택자들 (백업용)
        common_indicators = [
            # 활성화된 탭 패널에 있는 폼 요소 검사
            (By.CSS_SELECTOR, ".ant-tabs-tabpane-active .ant-form-item"),
            # 활성화된 탭 패널에 있는 입력 필드 검사
            (By.CSS_SELECTOR, ".ant-tabs-tabpane-active input"),
            # 활성화된 탭 패널에 있는 버튼 검사
            (By.CSS_SELECTOR, ".ant-tabs-tabpane-active button"),
            # 활성화된 탭 패널 자체 검사
            (By.CSS_SELECTOR, ".ant-tabs-tabpane-active")
        ]
        
        # 시작 시간 기록
        start_time = time.time()
        logger.info(f"{tab_name} 탭 활성화 확인 시작")
        
        # 먼저 탭별 특화 선택자로 검사
        specific_result = self.wait_for_page_loaded(indicators, max_wait=max_wait/2, 
                                                  check_interval=check_interval, 
                                                  page_name=f"{tab_name} 탭 (특화 선택자)")
        
        # 성공하면 바로 반환
        if specific_result:
            return True
            
        # 실패하면 남은 시간 동안 공통 선택자로 시도
        elapsed = time.time() - start_time
        remaining_wait = max(0.1, max_wait - elapsed)  # 최소 0.1초는 남김
        
        logger.warning(f"{tab_name} 탭 특화 선택자 확인 실패, 공통 선택자로 {remaining_wait:.1f}초 동안 재시도")
        return self.wait_for_page_loaded(common_indicators, max_wait=remaining_wait, 
                                       check_interval=check_interval, 
                                       page_name=f"{tab_name} 탭 (공통 선택자)")


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
        start_time = time.time()
        page_loaded = False
        
        while time.time() - start_time < max_wait and not page_loaded:
            for selector_type, selector in indicators:
                try:
                    element = self.driver.find_element(selector_type, selector)
                    if element and element.is_displayed():
                        elapsed = time.time() - start_time
                        logger.info(f"{page_name} 로드 확인 성공 ({elapsed:.1f}초 소요)")
                        return True
                except (NoSuchElementException, TimeoutException):
                    # 실패할 경우 현재 DOM 구조 로깅 (디버깅용)
                    if time.time() - start_time > max_wait * 0.7:  # 시간의 70% 이상 소요된 경우에만 로깅
                        try:
                            page_source = self.driver.page_source[:500]
                            logger.debug(f"{page_name} 로드 확인 실패 중. 현재 DOM 구조: {page_source}...")
                        except Exception as e:
                            logger.debug(f"DOM 구조 확인 오류: {e}")
                    pass
            
            time.sleep(check_interval)
        
        logger.warning(f"{page_name} 로드 확인 실패 (제한시간: {max_wait}초)")
        return False
        
    def try_dom_selector_first(self, selector, selector_type=By.CSS_SELECTOR, fallback_coords=None, delay_type=DELAY_SHORT):
        """
        DOM 선택자로 클릭을 시도하고, 실패하면 좌표 클릭으로 대체 (하이브리드 방식으로 변경)
        
        Args:
            selector: DOM 선택자
            selector_type: 선택자 타입 (기본값: CSS_SELECTOR)
            fallback_coords: 실패시 사용할 좌표 튀플
            delay_type: 클릭 후 대기 시간
        """
        # click_utils.py의 하이브리드 클릭 함수 호출
        element_desc = selector if selector_type == By.XPATH else f"CSS:{selector}"
        
        try:
            success = click_by_selector(self.driver, selector, selector_type, delay_type)
            return success
        except Exception as e:
            logger.warning(f"DOM 선택자 '{element_desc}' 클릭 실패: {e}")
            
            if fallback_coords:
                logger.info(f"좌표 클릭으로 대체: {fallback_coords}")
                return click_at_coordinates(self.driver, fallback_coords, delay_type)
            else:
                logger.error(f"fallback_coords가 없어 클릭 실패")
                return False

    def open_nongroup_products_view(self, max_wait=10, check_interval=0.5):
        """비그룹상품보기 화면을 엽니다. 동적으로 상태 확인하여 기다립니다."""
        logger.info("비그룹상품보기 화면 열기 시도 - 상태 동적 확인 방식")
        
        # 스크롤을 상단으로 이동
        self.driver.execute_script("window.scrollTo(0, 0);")
        
        # 현재 화면 상태 확인 함수
        def check_current_view_state():
            try:
                # '그룹상품 보기' 텍스트 확인
                group_view_elements = self.driver.find_elements(By.XPATH, dom_selectors["PRODUCT_VIEW_GROUP_TEXT"])
                # '비그룹상품 보기' 텍스트 확인
                nongroup_view_elements = self.driver.find_elements(By.XPATH, dom_selectors["PRODUCT_VIEW_NONGROUP_TEXT"])
                
                if group_view_elements and len(group_view_elements) > 0:
                    return "group", group_view_elements[0]
                elif nongroup_view_elements and len(nongroup_view_elements) > 0:
                    return "nongroup", nongroup_view_elements[0]
                return None, None
            except Exception as e:
                logger.warning(f"화면 상태 확인 중 오류: {e}")
                return None, None
        
        # 토글 버튼 상태 확인
        def check_toggle_state():
            try:
                toggle_selector = UI_ELEMENTS["PRODUCT_VIEW_NOGROUP"]["dom_selector"]
                toggle_switch = self.driver.find_element(By.XPATH, toggle_selector)
                is_checked = 'ant-switch-checked' in toggle_switch.get_attribute('class')
                return toggle_switch, is_checked
            except Exception as e:
                logger.warning(f"토글 스위치 상태 확인 실패: {e}")
                return None, None
        
        # 현재 화면 상태 확인
        view_state, view_element = check_current_view_state()
        toggle_switch, is_checked = check_toggle_state()
        
        if view_state == "nongroup":
            logger.info("이미 비그룹상품 보기 상태임. 클릭하지 않고 유지")
            return True
        
        # 토글 버튼 클릭 (비그룹상품 보기로 전환)
        if toggle_switch:
            logger.info("smart_click을 사용하여 비그룹상품 토글 클릭 시도")
            if self.smart_click(UI_ELEMENTS["PRODUCT_VIEW_NOGROUP"], DELAY_SHORT):
                # 클릭 후 비그룹상품 보기 상태로 전환되었는지 확인
                start_time = time.time()
                while time.time() - start_time < max_wait:
                    view_state, _ = check_current_view_state()
                    if view_state == "nongroup":
                        elapsed = time.time() - start_time
                        logger.info(f"비그룹상품 보기 상태 확인 완료 ({elapsed:.1f}초 소요)")
                        return True
                    time.sleep(check_interval)
                
                logger.warning(f"비그룹상품 보기 상태로 전환 확인 실패 (제한시간 {max_wait}초 초과)")
        else:
            logger.error("토글 스위치를 찾을 수 없음")
        
        # 실패 시 디버깅 정보 저장
        try:
            with open("page_source.html", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            logger.info("페이지 소스를 page_source.html에 저장했습니다 (디버깅용)")
        except Exception as e:
                try:
                    page_source = self.driver.page_source
                    logger.debug(f"탭 활성화 확인 실패 중. 현재 DOM 구조: {page_source[:500]}...")
                except:
                    pass
        
        # 짧게 대기 후 다시 확인
        time.sleep(check_interval)
        
        logger.warning(f"{tab_name} 탭 활성화 확인 실패 (제한시간 {max_wait}초 초과)")
        # 실패 시 DOM 구조 로깅 (디버깅용)
        try:
            tabs_element = self.driver.find_element(By.CSS_SELECTOR, ".ant-tabs-nav-list")
            tabs_html = tabs_element.get_attribute('outerHTML')
            logger.debug(f"탭 구조: {tabs_html}")
        except:
            pass
        return False

    def run_step1_automation(self):
        """
        1단계 자동화 실행: 비그룹상품보기에 있는 상품을 수정한 후, 신규수집 그룹으로 이동
        """
        try:
            # UI_ELEMENTS 가져오기
            from ui_elements import UI_ELEMENTS
            from dom_selectors import PAGE_LOAD_INDICATORS
            
            # 초기화 및 상태 확인
            logger.info("===== 퍼센티 상품 수정 자동화 1단계 시작 =====")
            # 그룹상품관리 메뉴 클릭
            logger.info("그룹상품관리 메뉴 클릭 시도")
            # ui_elements.py에 이미 정의된 UI 요소 사용
            
            # smart_click 사용하여 하이브리드 방식으로 클릭
            if not self.smart_click(UI_ELEMENTS["PRODUCT_GROUP"], delay_type=DELAY_VERY_SHORT):
                logger.error("그룹상품관리 메뉴 클릭 실패")
                return False
                
            logger.info("그룹상품관리 메뉴 클릭 성공")
            
            # 그룹상품관리 화면 로드 확인
            group_indicators = [(By.XPATH, PAGE_LOAD_INDICATORS["PRODUCT_GROUP_LOADED"])]
            group_loaded = self.wait_for_page_loaded(
                group_indicators, 
                max_wait=10, 
                check_interval=0.5,
                page_name="그룹상품관리"
            )
            
            if not group_loaded:
                logger.error("그룹상품관리 화면 로드 확인 실패")
                return False
                
            # 스크롤 위치 초기화
            self.driver.execute_script("window.scrollTo(0, 0);")
            logger.info("스크롤 위치를 최상단으로 초기화했습니다")
            
            logger.info("그룹상품관리 메뉴 클릭 완료")
            
            # 1. 비그룹상품보기 화면 열기
            logger.info("1. 비그룹상품보기 화면 열기")
            
            # 비그룹상품보기 화면 열기 시도
            logger.info("비그룹상품보기 화면 열기 시도 - 상태 동적 확인 방식")
            
            # 비그룹상품보기 토글 버튼 클릭 - 동적으로 DOM 선택자를 사용하여 개선된 접근 방식 적용
            
            # UI_ELEMENTS의 PRODUCT_VIEW_NOGROUP 사용
            logger.info("비그룹상품 토글 버튼을 UI_ELEMENTS를 통해 클릭 시도")
            
            # UI_ELEMENTS에서 PRODUCT_VIEW_NOGROUP 가져오기
            if "PRODUCT_VIEW_NOGROUP" in UI_ELEMENTS:
                non_group_toggle_ui = UI_ELEMENTS["PRODUCT_VIEW_NOGROUP"]
                logger.info(f"PRODUCT_VIEW_NOGROUP UI 요소 찾음: {non_group_toggle_ui['name'] if 'name' in non_group_toggle_ui else '비그룹상품보기 토글'}")
            else:
                # 폴백 대체 UI 요소 정의 (메모리에 있는 정보 기반)
                logger.warning("UI_ELEMENTS에 PRODUCT_VIEW_NOGROUP이 없어 대체 요소 사용")
                non_group_toggle_ui = {
                    "name": "비그룹상품보기 토글",
                    "dom_selector": "//span[contains(@class, 'ant-radio-button-wrapper')][contains(., '비그룹상품')]",
                    "selector_type": "xpath",
                    "coordinates": (470, 320),  # coordinates_editgoods.py의 PRODUCT_VIEW_NOGROUP 좌표 사용
                    "fallback_order": ["dom", "coordinates"]
                }
            
            # smart_click으로 토글 버튼 클릭
            logger.info("smart_click을 사용하여 비그룹상품 토글 클릭 시도")
            if not self.smart_click(non_group_toggle_ui, delay_type=DELAY_STANDARD):
                logger.error("비그룹상품보기 토글 버튼 클릭 실패")
                return False
            
            # 비그룹상품보기 토글 클릭 후 충분한 시간 대기 (안정성 향상)
            logger.info("비그룹상품보기 토글 클릭 후 화면 안정화를 위해 3초 대기")
            time.sleep(DELAY_STANDARD)  # 3초 대기로 안정성 향상
            
            # 모달창 열림 확인 함수 정의 - 향상된 버전
            def check_modal_open(max_wait=10, check_interval=0.5):
                logger.info("모달창이 열렸는지 확인 시작 (향상된 방식)")
                start_time = time.time()
                
                # 모달창 관련 요소 확인을 위한 선택자들 - 더 다양한 선택자 추가
                modal_selectors = [
                    # 일반적인 모달 다이얼로그
                    "//div[@role='dialog']",
                    # Ant Design 드로어 컴포넌트
                    "//div[contains(@class, 'ant-drawer-content')]",
                    # 제품 모달 탭
                    dom_selectors["PRODUCT_MODAL_TABS"],
                    # 일반 모달 클래스
                    "//div[contains(@class, 'modal')]",
                    # Ant Design 모달
                    "//div[contains(@class, 'ant-modal')]",
                    # 모달 내용 컨테이너
                    "//div[contains(@class, 'ant-modal-content')]",
                    # 모달 헤더
                    "//div[contains(@class, 'ant-modal-header')]",
                    # 모달 본문
                    "//div[contains(@class, 'ant-modal-body')]"
                ]
                
                # 추가 검증용 CSS 선택자
                css_selectors = [
                    ".ant-modal",
                    ".ant-modal-content",
                    ".ant-drawer",
                    ".ant-drawer-content",
                    "[role='dialog']",
                    ".modal"
                ]
                
                # 성공 카운터 - 여러 선택자가 발견되었을 때 더 확실하게 검증
                success_count = 0
                required_success = 2  # 최소 2개 이상의 다른 선택자가 발견되어야 함
                
                while time.time() - start_time < max_wait:
                    # XPATH 선택자로 검색
                    for selector in modal_selectors:
                        try:
                            elements = self.driver.find_elements(By.XPATH, selector)
                            if elements and len(elements) > 0:
                                elapsed = time.time() - start_time
                                logger.info(f"모달창 요소 발견: {selector}, 개수: {len(elements)} ({elapsed:.1f}초 소요)")
                                success_count += 1
                                # 기준 수 이상 발견되면 성공으로 간주
                                if success_count >= required_success:
                                    logger.info(f"여러 모달 요소가 확인됨 ({success_count}개). 모달이 열린 것으로 판단")
                                    return True
                        except Exception as e:
                            pass
                    
                    # CSS 선택자로도 검색 (백업)
                    for selector in css_selectors:
                        try:
                            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            if elements and len(elements) > 0:
                                elapsed = time.time() - start_time
                                logger.info(f"모달창 요소 발견 (CSS): {selector}, 개수: {len(elements)} ({elapsed:.1f}초 소요)")
                                success_count += 1
                                if success_count >= required_success:
                                    logger.info(f"여러 모달 요소가 확인됨 ({success_count}개). 모달이 열린 것으로 판단")
                                    return True
                        except Exception as e:
                            pass
                    
                    # 특별히 탭 요소만 확인 (가장 중요한 지표)
                    try:
                        tabs = self.driver.find_elements(By.XPATH, dom_selectors["PRODUCT_MODAL_TABS"])
                        if tabs and len(tabs) > 0:
                            elapsed = time.time() - start_time
                            logger.info(f"모달창 내 탭 요소 확인 성공 ({elapsed:.1f}초 소요)")
                            # 탭이 있으면 다른 요소 검증 없이도 성공으로 간주
                            return True
                    except Exception as tab_err:
                        logger.debug(f"모달창 내 탭 요소 확인 실패: {tab_err}")
                    
                    # 한 번의 반복에서 성공 카운트가 1 이상이지만 기준에 미달이면 짧게 대기 후 재검증
                    if success_count > 0:
                        logger.info(f"모달창 요소 일부 발견 ({success_count}개). 추가 검증 중...")
                        time.sleep(check_interval / 2)  # 더 짧게 대기
                        continue
                        
                    # 아무것도 발견되지 않았으면 원래 간격으로 대기
                    success_count = 0  # 카운터 리셋
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
            

            # 2-24번 단계: ProductEditorCore 클래스를 사용하여 상품 편집 로직 실행
            logger.info("ProductEditorCore를 사용하여 상품 편집 프로세스 시작")
            try:
                # 드롭다운 매니저 초기화 (이미 self.dropdown_manager가 있을 수 있음)
                dropdown_manager = self.dropdown_manager if hasattr(self, 'dropdown_manager') else None
                
                # ProductEditorCore 인스턴스 생성
                editor_core = ProductEditorCore(self.driver, dropdown_manager=dropdown_manager)
                
                # 상품 편집 프로세스 실행
                if editor_core.process_single_product():
                    logger.info("상품 편집 프로세스 성공적으로 완료")
                else:
                    logger.error("상품 편집 프로세스 실패")
                    return False
            except Exception as core_error:
                logger.error(f"ProductEditorCore 실행 중 오류 발생: {core_error}")
                return False
                
            logger.info("모든 상품 편집 단계가 완료되었습니다.")
            
            return True
            
        except Exception as e:
            logger.error(f"상품 수정 자동화 실행 중 오류 발생: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return False

# 일반적으로 사용되는 모듈들
import sys

# 단독 실행 시 1단계 자동화 코드
if __name__ == "__main__":
    # 기본 로깅 설정 - 레벨을 DEBUG로 변경하여 더 많은 로그 확인
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 로깅 시스템 설정 확인
    logging.info("\n\n" + "=" * 60)
    logging.info("2025-05-27 18:10 - 로깅 시스템 설정 확인")
    logging.info("로그 레벨: DEBUG - 모든 로그 메시지 출력")
    logging.info("DOM 선택자 시도 과정 로깅 기능 활성화")
    logging.info("=" * 60 + "\n\n")
    
    try:
        # 순환 임포트 문제 해결을 위해 동적 임포트 사용
        from login_percenty import PercentyLogin
        from account_manager import AccountManager
        
        # 1. 계정 관리자 초기화
        account_manager = AccountManager()
        
        # 2. 계정 정보 로드
        if not account_manager.load_accounts():
            print("계정 정보를 로드할 수 없습니다. 프로그램을 종료합니다.")
            sys.exit(1)
        
        # 3. 계정 선택
        selected_account = account_manager.select_account()
        if not selected_account:
            print("계정을 선택하지 않았습니다. 프로그램을 종료합니다.")
            sys.exit(0)
        
        # 4. 선택한 계정으로 로그인 객체 생성
        login = PercentyLogin(account=selected_account)
        
        # 5. 로그인 시도
        print(f"\n선택한 계정으로 로그인을 시도합니다: {selected_account.get('nickname', selected_account['id'])}")
        
        # 로그인 실행
        if not login.setup_driver():
            print("웹드라이버 설정 실패")
            sys.exit(1)
        
        if not login.login():
            print("로그인 실패")
            sys.exit(1)
        
        # AI 소싱 메뉴 클릭
        if not login.click_product_aisourcing_button_improved():
            print("AI 소싱 메뉴 클릭 실패")
            sys.exit(1)
            
        # 채널톡 및 로그인 모달창 숨기기 적용 (통합 유틸리티 사용)
        print("\n채널톡 및 로그인 모달창 숨기기 적용 시작...")
        result = hide_channel_talk_and_modals(login.driver, log_prefix="메인 실행")
        print(f"채널톡 및 로그인 모달창 숨기기 결과: {result}")
        
        print("\n\n" + "=" * 50)
        print(f"로그인 성공! '{selected_account.get('nickname', '')}'")
        print("이제 1단계 자동화를 실행합니다...")
        print("=" * 50 + "\n")
        
        # 6. 상품 수정 1단계 자동화 실행
        step1_automation = PercentyNewStep1(login.driver)
        if step1_automation.run_step1_automation():
            print("\n\n" + "=" * 50)
            print("1단계 자동화 성공!")
            print("=" * 50 + "\n")
        else:
            print("\n\n" + "=" * 50)
            print("1단계 자동화 실패. 로그를 확인하세요.")
            print("=" * 50 + "\n")
        
        # 무한 대기 (사용자가 Ctrl+C를 누를 때까지)
        print("종료하려면 Ctrl+C를 누르세요.")
        try:
            # 무한 대기
            while True:
                time.sleep(10)  # 10초마다 한 번씩 체크
        except KeyboardInterrupt:
            print("\n\n" + "=" * 50)
            print("사용자가 스크립트를 종료했습니다.")
            print("=" * 50 + "\n")
    
    except ImportError as e:
        print(f"\n임포트 오류 발생: {e}")
        print("로그인 모듈을 임포트할 수 없습니다.")
        print("순환 임포트 문제가 발생했을 수 있습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n오류 발생: {e}")
    finally:
        # 종료 시 브라우저 닫기
        if 'login' in locals() and login.driver:
            login.close_driver()
