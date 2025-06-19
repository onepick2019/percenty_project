# -*- coding: utf-8 -*-
"""
퍼센티 메뉴 클릭 기능 모듈

이 모듈은 퍼센티의 각종 메뉴를 클릭하는 기능을 제공합니다.
PercentyLogin 클래스에서 사용됩니다.
"""

import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

# 신규 좌표 관리 시스템 가져오기
from coordinates.coordinates_all import *
# 시간 지연 관리 모듈 추가
from timesleep import *

def click_at_absolute_coordinates(driver, x, y, delay=1.0):
    """
    절대 좌표로 클릭하는 함수
    
    Args:
        driver: 웹드라이버
        x: X 좌표
        y: Y 좌표
        delay: 클릭 후 대기 시간(초)
        
    Returns:
        bool: 클릭 성공 여부
    """
    try:
        logging.info(f"절대 좌표 클릭 시도: ({x}, {y})")
        
        # JavaScript로 클릭
        click_script = """
            var elem = document.elementFromPoint(arguments[0], arguments[1]);
            if (elem) {
                var tagName = elem.tagName;
                var elementText = elem.textContent || '';
                var elementId = elem.id || '';
                var elementClass = elem.className || '';
                elem.click();
                return {
                    clicked: true,
                    tagName: tagName,
                    text: elementText.trim(),
                    id: elementId,
                    class: elementClass
                };
            }
            return { clicked: false };
        """
        
        result = driver.execute_script(click_script, x, y)
        
        if result.get('clicked', False):
            elem_info = f"[{result.get('tagName', '')}] '{result.get('text', '')}'"
            if result.get('id'):
                elem_info += f" ID: {result.get('id')}"
            if result.get('class'):
                elem_info += f" CLASS: {result.get('class')}"
                
            logging.info(f"JavaScript로 절대 좌표 클릭 성공: ({x}, {y})")
            logging.info(f"클릭된 요소: {elem_info}")
            
            time.sleep(delay)  # 지정된 시간만큼 대기
            return True
        else:
            logging.warning(f"JavaScript 클릭 실패, ActionChains 시도")
            
            # ActionChains로 클릭 시도
            try:
                actions = ActionChains(driver)
                actions.move_to_element_with_offset(driver.find_element(By.TAG_NAME, "body"), x, y)
                actions.click().perform()
                logging.info(f"ActionChains로 절대 좌표 클릭 성공: ({x}, {y})")
                
                time.sleep(delay)  # 지정된 시간만큼 대기
                return True
            except Exception as action_error:
                logging.warning(f"ActionChains 클릭 실패: {action_error}")
                return False
    except Exception as e:
        logging.error(f"절대 좌표 클릭 시도 중 오류: {e}")
        return False

class MenuClicks:
    """퍼센티 메뉴 클릭 기능 클래스"""
    
    def __init__(self, driver):
        """초기화"""
        self.driver = driver
        self.logger = logging.getLogger("MenuClicks")
    
    def go_to_home(self):
        """퍼센티 홈으로 이동"""
        try:
            from coordinates.coordinates_all import MENU
            # MENU는 튜플로 저장되어 있음 (x, y)
            menu_x, menu_y = MENU["HOME"]
            if click_menu_using_relative_coordinates(self.driver, "퍼센티 홈", menu_x, menu_y):
                self.logger.info("퍼센티 홈으로 이동 성공")
                from timesleep import wait_after_menu_click
                wait_after_menu_click("퍼센티 홈")
                return True
            return False
        except Exception as e:
            self.logger.error(f"퍼센티 홈으로 이동 중 오류: {e}")
            return False
    
    def click_ai_sourcing(self):
        """AI 소싱 메뉴 클릭 - 하이브리드 방식 (DOM 우선, 좌표 백업)"""
        try:
            from ui_elements import UI_ELEMENTS
            from dom_utils import smart_click
            
            # UI_ELEMENTS의 PRODUCT_AISOURCING 사용 (하이브리드 방식)
            result = smart_click(self.driver, UI_ELEMENTS["PRODUCT_AISOURCING"], "AI 소싱 메뉴")
            
            if result.get("success", False):
                self.logger.info(f"AI 소싱 메뉴 클릭 성공 (방법: {result.get('method', 'unknown')})")
                from timesleep import wait_after_menu_click
                wait_after_menu_click("AI 소싱")
                return True
            else:
                self.logger.error(f"AI 소싱 메뉴 클릭 실패: {result.get('error', 'unknown')}")
                return False
        except Exception as e:
            self.logger.error(f"AI 소싱 메뉴 클릭 중 오류: {e}")
            return False
    
    def click_group_management(self):
        """그룹상품관리 메뉴 클릭 - 하이브리드 방식 (DOM 우선, 좌표 백업)"""
        try:
            from ui_elements import UI_ELEMENTS
            from dom_utils import smart_click
            
            # UI_ELEMENTS의 PRODUCT_GROUP 사용 (하이브리드 방식)
            result = smart_click(self.driver, UI_ELEMENTS["PRODUCT_GROUP"], "그룹상품관리 메뉴")
            
            if result.get("success", False):
                self.logger.info(f"그룹상품관리 메뉴 클릭 성공 (방법: {result.get('method', 'unknown')})")
                from timesleep import wait_after_menu_click
                wait_after_menu_click("그룹상품관리")
                return True
            else:
                self.logger.error(f"그룹상품관리 메뉴 클릭 실패: {result.get('error', 'unknown')}")
                return False
        except Exception as e:
            self.logger.error(f"그룹상품관리 메뉴 클릭 중 오류: {e}")
            return False
    
    def click_non_group_toggle(self):
        """비그룹상품 토글 클릭 - UI_ELEMENTS의 PRODUCT_VIEW_NOGROUP 사용"""
        try:
            # UI_ELEMENTS에서 PRODUCT_VIEW_NOGROUP 정보 가져오기
            from ui_elements import UI_ELEMENTS
            from selenium.webdriver.common.by import By
            
            # 로깅 시작
            self.logger.info("비그룹상품 토글 클릭 시도 (PRODUCT_VIEW_NOGROUP 사용)")
            
            # UI 요소가 존재하는지 확인
            if "PRODUCT_VIEW_NOGROUP" not in UI_ELEMENTS:
                self.logger.error("UI_ELEMENTS에 PRODUCT_VIEW_NOGROUP이 정의되어 있지 않음")
                return False
            
            product_view_element = UI_ELEMENTS["PRODUCT_VIEW_NOGROUP"]
            success = False
            
            # DOM 선택자로 시도 (fallback_order에 따라 DOM 먼저 시도)
            if "dom_selector" in product_view_element and product_view_element["dom_selector"]:
                try:
                    self.logger.info(f"DOM 선택자로 비그룹상품 토글 찾기 시도: {product_view_element['dom_selector']}")
                    toggle = self.driver.find_element(By.XPATH, product_view_element["dom_selector"])
                    toggle.click()
                    self.logger.info("비그룹상품 토글 클릭 성공 (DOM 선택자)")
                    return True
                except Exception as dom_error:
                    self.logger.warning(f"DOM 선택자로 비그룹상품 토글 찾기 실패: {dom_error}")
            
            # JavaScript로 시도
            try:
                self.logger.info("JavaScript로 비그룹상품 토글 클릭 시도")
                js_script = """
                    const buttons = Array.from(document.querySelectorAll('span, label, div'));
                    const nonGroupButton = buttons.find(el => el.textContent && el.textContent.includes('비그룹상품'));
                    if (nonGroupButton) { nonGroupButton.click(); return true; }
                    return false;
                """
                result = self.driver.execute_script(js_script)
                if result:
                    self.logger.info("JavaScript로 비그룹상품 토글 클릭 성공")
                    return True
                else:
                    self.logger.warning("JavaScript로 비그룹상품 토글 요소를 찾지 못함")
            except Exception as js_error:
                self.logger.error(f"JavaScript 실행 오류: {js_error}")
            
            # 좌표 클릭 시도
            if "coordinates" in product_view_element and product_view_element["coordinates"]:
                self.logger.info("좌표 기반으로 비그룹상품 토글 클릭 시도")
                # UI_ELEMENTS에서 정의된 좌표 사용
                toggle_x, toggle_y = product_view_element["coordinates"]
                if click_at_absolute_coordinates(self.driver, toggle_x, toggle_y):
                    self.logger.info(f"좌표({toggle_x}, {toggle_y})로 비그룹상품 토글 클릭 성공")
                    return True
            
            self.logger.error("모든 방법으로 비그룹상품 토글 클릭 실패")
            return False
        except Exception as e:
            self.logger.error(f"비그룹상품 토글 클릭 중 오류: {e}")
            return False
    
    def go_to_new_collection(self):
        """신규수집 메뉴로 이동"""
        try:
            from coordinates.coordinates_all import MENU
            # MENU는 튜플로 저장되어 있음 (x, y)
            menu_x, menu_y = MENU["PRODUCT_AISOURCING"]
            if click_menu_using_relative_coordinates(self.driver, "신규수집", menu_x, menu_y):
                self.logger.info("신규수집 메뉴로 이동 성공")
                from timesleep import wait_after_menu_click
                wait_after_menu_click("신규수집")
                return True
            return False
        except Exception as e:
            self.logger.error(f"신규수집 메뉴로 이동 중 오류: {e}")
            return False
    
    def go_to_product_registration(self):
        """상품등록 메뉴로 이동"""
        try:
            from coordinates.coordinates_all import MENU
            # MENU는 튜플로 저장되어 있음 (x, y)
            menu_x, menu_y = MENU["PRODUCT_REGISTER"]
            if click_menu_using_relative_coordinates(self.driver, "상품등록", menu_x, menu_y):
                self.logger.info("상품등록 메뉴로 이동 성공")
                from timesleep import wait_after_menu_click
                wait_after_menu_click("상품등록")
                return True
            return False
        except Exception as e:
            self.logger.error(f"상품등록 메뉴로 이동 중 오류: {e}")
            return False

def click_menu_using_relative_coordinates(driver, menu_name, menu_x, menu_y):
    """
    특별좌표(상대좌표) 방식으로 메뉴 클릭
    
    Args:
        driver: 웹드라이버
        menu_name: 메뉴 이름
        menu_x: 메뉴 X 좌표
        menu_y: 메뉴 Y 좌표
        
    Returns:
        tuple: (클릭 성공 여부, 실제 클릭된 좌표 (x, y))
    """
    try:
        logging.info(f"{menu_name} 클릭 시도 (특별좌표 사용)")
        
        # 브라우저 내부 크기 가져오기
        inner_width = driver.execute_script("return window.innerWidth;")
        inner_height = driver.execute_script("return window.innerHeight;")
        logging.info(f"브라우저 내부 크기: {inner_width}x{inner_height}")
        
        # 메뉴 기본 좌표 로깅
        logging.info(f"{menu_name} 설정 좌표: ({menu_x}, {menu_y})")
        
        # 특별좌표(상대좌표) 계산
        # 좌표 변환 공식을 상세히 로깅
        logging.info(f"좌표 변환 공식: 개선된 비선형 변환 적용 - 화면 위치별 보정")
        
        # 계산된 상대 X 좌표 - X축은 일반적인 비율 계산 유지
        relative_x = int(inner_width * (menu_x / 1920))
        
        # 계산된 상대 Y 좌표 - 더 세분화된 비선형 변환 적용
        # 사용자가 제공한 분석 데이터에 따라 5개 구간으로 세분화

        # 구간 1: Y 0-210 (최상단 영역)
        if menu_y <= 210:
            correction = 0.67
            relative_y = int(inner_height * (menu_y / 1080) * correction)
            logging.info(f"최상단 영역 보정 계수 적용 ({correction})")

        # 구간 2: Y 211-255 (상단 영역)
        elif menu_y <= 300:
            correction = 0.86
            relative_y = int(inner_height * (menu_y / 1080) * correction)
            logging.info(f"상단 영역 보정 계수 적용 ({correction})")

        # 구간 3: Y 256-435 (중상단 영역)
        elif menu_y <= 435:
            correction = 0.90
            relative_y = int(inner_height * (menu_y / 1080) * correction)
            logging.info(f"중상단 영역 보정 계수 적용 ({correction})")

        # 구간 4: Y 436-845 (중앙 영역)
        elif menu_y <= 845:
            correction = 1.00
            relative_y = int(inner_height * (menu_y / 1080) * correction)
            logging.info(f"중앙 영역 연산 적용 ({correction})")

        # 구간 5: Y 846-975+ (하단 영역)
        else:
            # 846~975 구간은 점진적으로 보정계수 증가
            if menu_y <= 890:
                correction = 1.01
            elif menu_y <= 935:
                correction = 1.03
            else:  # 936 이상
                correction = 1.04
            
            relative_y = int(inner_height * (menu_y / 1080) * correction)
            logging.info(f"하단 영역 보정 계수 적용 ({correction})")
            if menu_y > 975:
                logging.info(f"고해상도 하단 영역 - 보정계수 확인 필요")
        
        logging.info(f"상대좌표 변환 완료: ({menu_x}, {menu_y}) -> ({relative_x}, {relative_y})")
        
        # 디버깅용 - 좌표 계산 과정 상세히 표시
        logging.info(f"변환 상세 정보 - 브라우저 크기: {inner_width}x{inner_height}, 참조 크기: 1920x1080")
        logging.info(f"X축 계산: int({inner_width} * ({menu_x} / 1920)) = {relative_x}")
        if menu_y <= 210:
            logging.info(f"Y축 계산(최상단): int({inner_height} * ({menu_y} / 1080) * 0.67) = {relative_y}")
        elif menu_y <= 255:
            logging.info(f"Y축 계산(상단): int({inner_height} * ({menu_y} / 1080) * 0.86) = {relative_y}")
        elif menu_y <= 435:
            logging.info(f"Y축 계산(중상단): int({inner_height} * ({menu_y} / 1080) * 0.90) = {relative_y}")
        elif menu_y <= 845:
            logging.info(f"Y축 계산(중앙): int({inner_height} * ({menu_y} / 1080)) = {relative_y}")
        else:
            correction_value = "1.01, 1.03, 또는 1.04 (구간별)"
            logging.info(f"Y축 계산(하단): int({inner_height} * ({menu_y} / 1080) * {correction_value}) = {relative_y}")
        
        # 좌표가 브라우저 내부 크기를 벗어나지 않도록 보정
        relative_x = max(0, min(relative_x, inner_width - 1))
        relative_y = max(0, min(relative_y, inner_height - 1))
        
        # 좌표 로깅 제거 (불필요한 로그 출력 방지)
        
        # JavaScript로 메뉴 클릭
        click_script = """
            var elem = document.elementFromPoint(arguments[0], arguments[1]);
            if (elem) {
                var tagName = elem.tagName;
                var elementText = elem.textContent || '';
                var elementId = elem.id || '';
                var elementClass = elem.className || '';
                elem.click();
                return {
                    clicked: true,
                    tagName: tagName,
                    text: elementText.trim(),
                    id: elementId,
                    class: elementClass
                };
            }
            return { clicked: false };
        """
        
        result = driver.execute_script(click_script, relative_x, relative_y)
        
        if result.get('clicked', False):
            elem_info = f"[{result.get('tagName', '')}] '{result.get('text', '')}'" 
            if result.get('id'):
                elem_info += f" ID: {result.get('id')}"
            if result.get('class'):
                elem_info += f" CLASS: {result.get('class')}"
                
            logging.info(f"JavaScript로 {menu_name} 클릭 성공: ({relative_x}, {relative_y})")
            logging.info(f"클릭된 요소: {elem_info}")
            
            wait_after_menu_click(menu_name)  # 반응 대기
            logging.info(f"{menu_name} 클릭 완료")
            return True, (relative_x, relative_y)
        else:
            logging.warning(f"JavaScript 클릭 실패, ActionChains 시도")
            
            # ActionChains로 클릭 시도
            try:
                actions = ActionChains(driver)
                actions.move_to_element_with_offset(driver.find_element(By.TAG_NAME, "body"), relative_x, relative_y)
                actions.click().perform()
                logging.info(f"ActionChains로 {menu_name} 클릭 성공: ({relative_x}, {relative_y})")
                
                wait_after_menu_click(menu_name)  # 반응 대기
                logging.info(f"{menu_name} 클릭 완료")
                return True, (relative_x, relative_y)
            except Exception as action_error:
                logging.warning(f"ActionChains 클릭 실패: {action_error}")
                return False, (relative_x, relative_y)
    except Exception as e:
        logging.error(f"{menu_name} 클릭 시도 중 오류: {e}")
        return False, (0, 0)
