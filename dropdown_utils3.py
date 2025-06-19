# -*- coding: utf-8 -*-
"""
퍼센티 3단계 개별 상품 그룹 이동 유틸리티

이 모듈은 3단계 코어 개발을 위한 개별 상품 그룹 이동 기능을 제공합니다.
dropdown_utils.py (1단계)와 dropdown_utils2.py (2단계)와 구분하여 사용합니다.

주요 기능:
- 개별 상품의 그룹 드롭박스 열기
- 그룹 선택 (인덱스/이름)
- 이미지 삭제 관련 기능
- 스크롤 관리
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    StaleElementReferenceException,
    ElementClickInterceptedException
)

# 프로젝트 내부 모듈 임포트
from timesleep import DELAY_SHORT, DELAY_MEDIUM, DELAY_LONG
from ui_elements import UI_ELEMENTS
from coordinates.coordinates_editgoods import PRODUCT_DETAIL_EDIT

# 탭 선택자 상수
TAB_THUMBNAIL = "//div[contains(@class, 'ant-tabs-tab') and contains(., '썸네일')]"
TAB_OPTIONS = "//div[contains(@class, 'ant-tabs-tab') and contains(., '옵션')]"
TAB_DETAIL = "//div[contains(@class, 'ant-tabs-tab') and contains(., '상세페이지')]"

# 로거 설정
logger = logging.getLogger(__name__)

class PercentyDropdown3:
    """
    퍼센티 3단계 개별 상품 그룹 이동 관리 클래스
    
    이 클래스는 3단계 코어 개발을 위한 개별 상품 그룹 이동 기능을 제공합니다.
    dropdown_utils.py (1단계)와 dropdown_utils2.py (2단계)와 구분하여 사용합니다.
    """
    
    def __init__(self, driver):
        """
        초기화
        
        Args:
            driver: Selenium WebDriver 인스턴스
        """
        self.driver = driver
        logger.info("퍼센티 3단계 드롭다운 관리자 초기화 완료")
    
    # =============================================================================
    # 개별 상품 그룹 이동 메서드들
    # =============================================================================
    
    def open_product_item_dropdown(self, item_index=0, timeout=10):
        """
        개별 상품 아이템의 그룹 드롭박스 열기
        
        Args:
            item_index: 여러 상품이 있을 경우 상품 인덱스 (기본값: 0, 첫 번째 상품)
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"{item_index + 1}번째 상품의 그룹 드롭박스 열기")
            
            # 상품 행의 그룹 드롭박스 선택자들 (더 정확한 선택자 추가)
            selectors = [
                f"(//tr[contains(@class, 'ant-table-row')])[{item_index + 1}]//div[contains(@class, 'ant-select-selector')]",
                f"(//tbody//tr)[{item_index + 1}]//div[contains(@class, 'ant-select-selector')]",
                f"(//tr[contains(@class, 'ant-table-row')])[{item_index + 1}]//span[contains(@class, 'ant-select-selection-item')]/parent::div",
                # 더 구체적인 선택자들
                f"(//tr[contains(@class, 'ant-table-row')])[{item_index + 1}]//td[last()]//div[contains(@class, 'ant-select-selector')]",
                f"(//tr[contains(@class, 'ant-table-row')])[{item_index + 1}]//td[position()=last()]//div[contains(@class, 'ant-select')]",
                f"(//tbody//tr)[{item_index + 1}]//td[last()]//div[contains(@class, 'ant-select-selector')]",
                # 백업 선택자
                f"(//div[contains(@class, 'ant-select') and contains(@class, 'ant-select-single')])[{item_index + 1}]//div[contains(@class, 'ant-select-selector')]"
            ]
            
            dropdown_element = None
            for selector in selectors:
                try:
                    dropdown_element = WebDriverWait(self.driver, timeout).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except (TimeoutException, NoSuchElementException):
                    continue
                    
            if not dropdown_element:
                logger.error(f"{item_index + 1}번째 상품의 그룹 드롭박스를 찾을 수 없습니다.")
                return False
                
            # 드롭박스가 화면에 보이도록 스크롤
            try:
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", dropdown_element)
                time.sleep(0.5)
            except Exception as e:
                logger.warning(f"스크롤 중 오류: {e}")
                
            # 드롭박스 클릭
            dropdown_element.click()
            time.sleep(DELAY_SHORT)
            
            # 드롭다운이 열렸는지 확인
            dropdown_open_selector = "//div[contains(@class, 'ant-select-dropdown') and not(contains(@style, 'display: none'))]"
            try:
                WebDriverWait(self.driver, timeout).until(
                    EC.visibility_of_element_located((By.XPATH, dropdown_open_selector))
                )
                logger.info(f"{item_index + 1}번째 상품의 그룹 드롭박스가 열렸습니다.")
                return True
            except (TimeoutException, NoSuchElementException):
                logger.error(f"{item_index + 1}번째 상품의 그룹 드롭박스가 열리지 않았습니다.")
                return False
                
        except Exception as e:
            logger.error(f"상품 그룹 드롭박스 열기 오류: {e}")
            return False
    
    def select_group_by_index(self, group_index, timeout=10):
        """
        열린 드롭다운 메뉴에서 인덱스로 그룹 선택
        
        Args:
            group_index: 선택할 그룹의 인덱스 (0부터 시작, 0은 '그룹없음' 또는 '전체')
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"드롭다운 메뉴에서 {group_index}번째 그룹 선택")
            
            # 드롭다운 아이템들 선택자
            items_selector = "//div[contains(@class, 'ant-select-dropdown')]//div[contains(@class, 'ant-select-item-option')]"
            
            items = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located((By.XPATH, items_selector))
            )
            
            if group_index < 0 or group_index >= len(items):
                logger.error(f"유효하지 않은 그룹 인덱스입니다: {group_index} (총 그룹: {len(items)})")
                return False
                
            # 해당 인덱스의 그룹 클릭
            target_item = items[group_index]
            target_item.click()
            time.sleep(DELAY_SHORT)
            logger.info(f"{group_index}번째 그룹이 선택되었습니다.")
            return True
            
        except Exception as e:
            logger.error(f"그룹 인덱스 선택 오류: {e}")
            return False
    
    def select_group_by_name(self, group_name, timeout=10):
        """
        열린 드롭다운 메뉴에서 이름으로 그룹 선택
        
        Args:
            group_name: 선택할 그룹의 이름 (예: "등록B", "완료D3")
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"드롭다운 메뉴에서 '{group_name}' 그룹 선택")
            
            # 그룹명으로 아이템 선택자
            selectors = [
                f"//div[contains(@class, 'ant-select-dropdown')]//div[@class='ant-select-item-option-content' and contains(text(), '{group_name}')]",
                f"//div[contains(@class, 'ant-select-item') and contains(@class, 'ant-select-item-option') and contains(., '{group_name}')]",
                # 대체 선택자
                f"//div[contains(@class, 'sc-dkmUuB') and text()='{group_name}']/ancestor::div[contains(@class, 'ant-select-item')]"
            ]
            
            # 드롭다운이 열린 후 스크롤 및 검색을 위한 대기
            time.sleep(DELAY_SHORT)
            
            # 검색 필드에 그룹명 입력 (검색을 지원하는 드롭다운인 경우)
            try:
                search_input = self.driver.find_element(By.CSS_SELECTOR, "input.ant-select-selection-search-input:not([readonly])")
                search_input.clear()
                search_input.send_keys(group_name)
                time.sleep(DELAY_SHORT)
                logger.info(f"검색 필드에 '{group_name}' 입력됨")
            except (NoSuchElementException, StaleElementReferenceException):
                logger.warning("검색 가능한 드롭다운이 아니거나 검색 필드를 찾을 수 없습니다. 스크롤로 찾습니다.")
                # 전체 목록을 스크롤하며 검색
                self._scroll_and_search_for_group(group_name)
            
            group_element = None
            for selector in selectors:
                try:
                    group_element = WebDriverWait(self.driver, timeout).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except (TimeoutException, NoSuchElementException, StaleElementReferenceException):
                    continue
                    
            if not group_element:
                logger.error(f"'{group_name}' 그룹을 찾을 수 없습니다.")
                return False
                
            # 그룹 클릭
            group_element.click()
            time.sleep(DELAY_SHORT)
            logger.info(f"'{group_name}' 그룹이 선택되었습니다.")
            return True
            
        except Exception as e:
            logger.error(f"그룹 선택 오류: {e}")
            return False
    
    def _scroll_and_search_for_group(self, group_name, max_scrolls=10):
        """
        드롭다운 내에서 스크롤하며 그룹 검색
        
        Args:
            group_name: 찾을 그룹 이름
            max_scrolls: 최대 스크롤 횟수
            
        Returns:
            bool: 그룹을 찾았는지 여부
        """
        try:
            logger.info(f"드롭다운 내에서 '{group_name}' 그룹 스크롤 검색")
            
            # 드롭다운 컨테이너 찾기
            dropdown_container = self.driver.find_element(By.XPATH, "//div[contains(@class, 'ant-select-dropdown')]")
            
            for scroll_count in range(max_scrolls):
                # 현재 보이는 그룹들 중에서 찾기
                group_elements = dropdown_container.find_elements(By.XPATH, ".//div[contains(@class, 'ant-select-item-option-content')]")
                
                for element in group_elements:
                    if group_name in element.text:
                        logger.info(f"스크롤 {scroll_count + 1}회 후 '{group_name}' 그룹을 찾았습니다.")
                        return True
                
                # 아래로 스크롤
                self.driver.execute_script("arguments[0].scrollTop += 100;", dropdown_container)
                time.sleep(0.3)
            
            logger.warning(f"최대 스크롤 횟수({max_scrolls})에 도달했지만 '{group_name}' 그룹을 찾지 못했습니다.")
            return False
            
        except Exception as e:
            logger.error(f"드롭다운 스크롤 검색 오류: {e}")
            return False
    
    def select_product_group_by_index(self, group_index, item_index=0):
        """
        상품 아이템의 드롭박스를 열고 인덱스로 그룹 선택 (원스텝)
        
        Args:
            group_index: 선택할 그룹의 인덱스 (0부터 시작, 0은 '그룹없음')
            item_index: 여러 상품이 있을 경우 상품 인덱스 (기본값: 0, 첫 번째 상품)
            
        Returns:
            bool: 성공 여부
        """
        if not self.open_product_item_dropdown(item_index):
            return False
        return self.select_group_by_index(group_index)
    
    def select_product_group_by_name(self, group_name, item_index=0):
        """
        상품 아이템의 드롭박스를 열고 이름으로 그룹 선택 (원스텝)
        
        Args:
            group_name: 선택할 그룹의 이름 (예: "등록B", "완료D3")
            item_index: 여러 상품이 있을 경우 상품 인덱스 (기본값: 0, 첫 번째 상품)
            
        Returns:
            bool: 성공 여부
        """
        if not self.open_product_item_dropdown(item_index):
            return False
        return self.select_group_by_name(group_name)
    
    def reset_scroll_position(self, delay=0.5):
        """
        스크롤 위치를 최상단으로 초기화
        
        Args:
            delay: 스크롤 후 대기 시간
            
        Returns:
            bool: 성공 여부
        """
        try:
            # JavaScript를 사용하여 스크롤 위치를 최상단으로 이동
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(delay)  # 스크롤 이동 대기
            logger.info("스크롤 위치를 최상단으로 초기화했습니다")
            return True
        except Exception as e:
            logger.error(f"스크롤 위치 초기화 오류: {e}")
            return False
    
    def go_to_tab(self, tab_selector, timeout=10):
        """
        지정된 탭으로 이동
        
        Args:
            tab_selector: 이동할 탭의 XPath 선택자
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"탭으로 이동: {tab_selector}")
            
            tab = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, tab_selector))
            )
            tab.click()
            time.sleep(DELAY_SHORT)
            
            return True
            
        except Exception as e:
            logger.error(f"탭 이동 오류: {e}")
            return False
    
    def go_to_thumbnail_tab(self, timeout=10):
        """
        섬네일 탭으로 이동
        
        Args:
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        return self.go_to_tab(TAB_THUMBNAIL, timeout)
    
    def go_to_options_tab(self, timeout=10):
        """
        옵션 탭으로 이동
        
        Args:
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        return self.go_to_tab(TAB_OPTIONS, timeout)
    
    def go_to_detail_tab(self, timeout=10):
        """
        상세페이지 탭으로 이동
        
        Args:
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        return self.go_to_tab(TAB_DETAIL, timeout)
    
    # =============================================================================
    # 이미지 삭제 관련 메서드들 (image_utils에서 가져온 메서드들)
    # =============================================================================
    
    def delete_image_by_index(self, index, timeout=10):
        """
        특정 인덱스의 이미지 삭제 (0부터 시작)
        
        Args:
            index: 삭제할 이미지 인덱스 (0부터 시작)
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"{index+1}번째 이미지 삭제")
            
            # 해당 인덱스의 이미지 삭제 버튼 선택자
            # 모든 이미지 카드를 찾고 인덱스 위치의 삭제 버튼 클릭
            # 동적 CSS 클래스명 대신 더 안정적인 XPath 선택자 사용
            image_cards_selector = "//div[contains(@class, 'ant-col') and .//img and .//span[text()='삭제']]"
            
            try:
                # 모든 이미지 카드 찾기
                image_cards = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_all_elements_located((By.XPATH, image_cards_selector))
                )
                
                # 인덱스 범위 확인
                if index < 0 or index >= len(image_cards):
                    logger.error(f"유효하지 않은 이미지 인덱스입니다: {index} (총 이미지: {len(image_cards)})")
                    return False
                
                # 해당 카드의 삭제 버튼 찾기
                delete_button_selector = ".//span[text()='삭제']"
                delete_button = image_cards[index].find_element(By.XPATH, delete_button_selector)
                
                # 삭제 버튼 클릭
                delete_button.click()
                time.sleep(DELAY_SHORT)
                
                logger.info(f"{index+1}번째 이미지 삭제 완료")
                return True
                
            except (TimeoutException, NoSuchElementException) as e:
                logger.error(f"이미지 또는 삭제 버튼을 찾을 수 없습니다: {e}")
                return False
                
        except Exception as e:
            logger.error(f"이미지 삭제 오류: {e}")
            return False
    
    def open_bulk_edit_modal(self, timeout=10):
        """
        상세페이지 탭에서 일괄편집 버튼을 클릭하여 이미지 관리 모달창 열기
        
        Args:
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("상세페이지 일괄편집 버튼 클릭")
            
            # 일괄편집 버튼 선택자
            bulk_edit_button_selector = "//button[contains(@class, 'ant-btn')][.//span[text()='일괄 편집']][.//span[@role='img' and @aria-label='form']]"
            
            try:
                bulk_edit_button = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((By.XPATH, bulk_edit_button_selector))
                )
                bulk_edit_button.click()
                time.sleep(DELAY_MEDIUM)
                
                # 모달창이 열렸는지 확인
                modal_selector = "//div[contains(@class, 'ant-modal-body')]//div[contains(@class, 'ant-upload')]"
                WebDriverWait(self.driver, timeout).until(
                    EC.visibility_of_element_located((By.XPATH, modal_selector))
                )
                
                logger.info("일괄편집 모달창이 성공적으로 열렸습니다.")
                return True
                
            except (TimeoutException, NoSuchElementException) as e:
                logger.error(f"일괄편집 버튼을 찾을 수 없습니다: {e}")
                return False
                
        except Exception as e:
            logger.error(f"일괄편집 모달창 열기 오류: {e}")
            return False
    
    def close_bulk_edit_modal(self, timeout=8):
        """
        일괄편집 모달창 닫기
        
        Args:
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("일괄편집 모달창 닫기")
            
            # 모달창이 열려있는지 먼저 확인
            modal_selector = "//div[contains(@class, 'ant-modal') and contains(@class, 'ant-modal-root')]"
            
            try:
                modal_element = self.driver.find_element(By.XPATH, modal_selector)
                if not modal_element.is_displayed():
                    logger.info("일괄편집 모달창이 이미 닫혀있음")
                    return True
            except NoSuchElementException:
                logger.info("일괄편집 모달창이 존재하지 않음")
                return True
            
            # 방법 1: ESC 키로 닫기 시도
            try:
                body = self.driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.ESCAPE)
                time.sleep(1)
                
                # 모달창이 닫혔는지 확인
                try:
                    modal_element = self.driver.find_element(By.XPATH, modal_selector)
                    if not modal_element.is_displayed():
                        logger.info("ESC 키로 일괄편집 모달창 닫기 성공")
                        return True
                except NoSuchElementException:
                    logger.info("ESC 키로 일괄편집 모달창 닫기 성공")
                    return True
                    
            except Exception as e:
                logger.warning(f"ESC 키로 모달창 닫기 실패: {e}")
            
            # 방법 2: 닫기 버튼 클릭 시도
            close_button_selectors = [
                "//div[contains(@class, 'ant-modal-header')]//button[contains(@class, 'ant-modal-close')]",
                "//button[@aria-label='Close']",
                "//span[contains(@class, 'ant-modal-close-x')]"
            ]
            
            for selector in close_button_selectors:
                try:
                    close_button = WebDriverWait(self.driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    close_button.click()
                    time.sleep(1)
                    
                    # 모달창이 닫혔는지 확인
                    try:
                        modal_element = self.driver.find_element(By.XPATH, modal_selector)
                        if not modal_element.is_displayed():
                            logger.info("닫기 버튼으로 일괄편집 모달창 닫기 성공")
                            return True
                    except NoSuchElementException:
                        logger.info("닫기 버튼으로 일괄편집 모달창 닫기 성공")
                        return True
                        
                except (TimeoutException, NoSuchElementException):
                    continue
            
            logger.error("일괄편집 모달창을 닫을 수 없습니다.")
            return False
            
        except Exception as e:
            logger.error(f"일괄편집 모달창 닫기 오류: {e}")
            return False
    
    def select_first_product(self, timeout=10):
        """
        첫번째 상품의 체크박스 선택
        
        Args:
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("첫번째 상품 체크박스 선택")
            
            # 첫번째 상품의 체크박스 선택자들 (Select all 체크박스 제외)
            selectors = [
                # 테이블의 첫번째 행의 체크박스 (Select all 제외)
                "//tbody[contains(@class, 'ant-table-tbody')]//tr[1]//td[contains(@class, 'ant-table-selection-column')]//input[@type='checkbox' and not(@aria-label)]",
                # 첫번째 상품 행의 체크박스 (대체 선택자, Select all 제외)
                "//tr[contains(@class, 'ant-table-row')][1]//span[contains(@class, 'ant-checkbox')]//input[@type='checkbox' and not(@aria-label)]",
                # 더 구체적인 선택자 (Select all 제외)
                "//div[contains(@class, 'ant-table-body')]//tr[1]//label[contains(@class, 'ant-checkbox-wrapper')]//input[@type='checkbox' and not(@aria-label)]"
            ]
            
            checkbox_element = None
            for selector in selectors:
                try:
                    checkbox_element = WebDriverWait(self.driver, timeout).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except (TimeoutException, NoSuchElementException):
                    continue
                    
            if not checkbox_element:
                logger.error("첫번째 상품의 체크박스를 찾을 수 없습니다.")
                return False
                    
            # 이미 선택되어 있는지 확인
            is_checked = checkbox_element.is_selected()
            
            # 선택되어 있지 않으면 클릭
            if not is_checked:
                checkbox_element.click()
                time.sleep(DELAY_SHORT)
                logger.info("첫번째 상품이 선택되었습니다.")
            else:
                logger.info("첫번째 상품이 이미 선택되어 있습니다.")
                
            return True
                
        except Exception as e:
            logger.error(f"첫번째 상품 선택 오류: {e}")
            return False
    
    def open_group_assignment_modal(self, timeout=10):
        """
        그룹 지정 버튼을 클릭하여 그룹 이동 모달창 열기
        
        Args:
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("그룹 지정 버튼 클릭")
            
            # 그룹 지정 버튼 선택자
            selectors = [
                # 신규상품등록 화면 그룹 지정 버튼
                "//button[contains(@class, 'ant-btn')][.//span[text()='그룹 지정']]",
                # 등록상품관리 화면 그룹 지정 버튼
                "//div[contains(@class, 'ant-btn-group')]//button[.//span[text()='그룹 지정']]",
                # 그룹상품관리 화면 그룹 지정 버튼
                "//div[contains(@class, 'ant-flex')]//button[.//span[text()='그룹 지정']]"
            ]
            
            button_element = None
            for selector in selectors:
                try:
                    button_element = WebDriverWait(self.driver, timeout).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except (TimeoutException, NoSuchElementException):
                    continue
                    
            if not button_element:
                logger.error("그룹 지정 버튼을 찾을 수 없습니다.")
                return False
                    
            # 버튼이 비활성화되어 있는지 확인
            is_disabled = button_element.get_attribute("disabled")
            
            if is_disabled:
                logger.error("그룹 지정 버튼이 비활성화되어 있습니다. 먼저 상품을 선택해주세요.")
                return False
                    
            # 그룹 지정 버튼 클릭
            button_element.click()
            time.sleep(DELAY_SHORT)
            
            # 모달창이 열렸는지 확인
            modal_selector = "//div[contains(@class, 'ant-modal')]//span[contains(text(), '상품 그룹핑') or contains(text(), '그룹 지정')]"
            try:
                WebDriverWait(self.driver, timeout).until(
                    EC.visibility_of_element_located((By.XPATH, modal_selector))
                )
                logger.info("그룹 이동 모달창이 열렸습니다.")
                return True
            except (TimeoutException, NoSuchElementException):
                logger.error("그룹 이동 모달창을 열지 못했습니다.")
                return False
                
        except Exception as e:
            logger.error(f"그룹 이동 모달창 열기 오류: {e}")
            return False
    
    def select_group_in_modal(self, group_name, timeout=10):
        """
        그룹 이동 모달창에서 특정 그룹 선택
        
        Args:
            group_name: 선택할 그룹 이름
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"그룹 이동 모달창에서 '{group_name}' 그룹 선택")
            
            # 그룹 라디오 버튼 선택자
            radio_selector = f"//div[contains(@class, 'ant-modal-body')]//label[contains(@class, 'ant-radio-wrapper')][./span[contains(text(), '{group_name}')]]"
            
            try:
                radio_element = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((By.XPATH, radio_selector))
                )
                radio_element.click()
                time.sleep(DELAY_SHORT)
                logger.info(f"'{group_name}' 그룹이 선택되었습니다.")
                
                # 확인 버튼 클릭
                confirm_button_selector = "//div[contains(@class, 'ant-modal-footer')]//button[contains(@class, 'ant-btn-primary')][.//span[text()='확인']]"
                confirm_button = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((By.XPATH, confirm_button_selector))
                )
                confirm_button.click()
                logger.info("확인 버튼 클릭 완료")
                
                # 모달창이 닫혔는지 확인
                modal_selector = "//div[contains(@class, 'ant-modal')]//span[contains(text(), '상품 그룹핑') or contains(text(), '그룹 지정')]"
                try:
                    # 모달창이 사라질 때까지 대기 (최대 10초)
                    WebDriverWait(self.driver, 10).until(
                        EC.invisibility_of_element_located((By.XPATH, modal_selector))
                    )
                    logger.info("그룹 이동 모달창이 정상적으로 닫혔습니다.")
                    logger.info("그룹 이동 완료")
                    return True
                except TimeoutException:
                    logger.warning("그룹 이동 모달창이 닫히지 않았지만 그룹 이동은 완료되었을 수 있습니다.")
                    return True
                    
            except (TimeoutException, NoSuchElementException):
                logger.error(f"'{group_name}' 그룹을 찾을 수 없습니다.")
                return False
                
        except Exception as e:
            logger.error(f"그룹 선택 오류: {e}")
            return False
    
    def process_image_delete(self, delete_command, timeout=10):
        """
        이미지 삭제 명령 처리 (엑셀 H열의 first:1 등)
        
        Args:
            delete_command: 삭제 명령 (예: "first:1", "first:2")
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"이미지 삭제 명령 처리: {delete_command}")
            
            if not delete_command or delete_command.strip() == '':
                logger.warning("삭제 명령이 비어있습니다.")
                return False
            
            # 명령 파싱 (예: "first:1" -> 첫 번째 이미지 삭제)
            if delete_command.startswith("first:"):
                try:
                    count = int(delete_command.split(":")[1])
                    logger.info(f"첫 번째부터 {count}개 이미지 삭제")
                    
                    # 일괄편집 모달창 열기
                    if not self.open_bulk_edit_modal(timeout):
                        logger.error("일괄편집 모달창 열기 실패")
                        return False
                    
                    # 지정된 개수만큼 이미지 삭제
                    success = True
                    for i in range(count):
                        if not self.delete_image_by_index(0, timeout):  # 항상 첫 번째 이미지 삭제 (삭제되면 다음이 첫 번째가 됨)
                            logger.error(f"{i+1}번째 이미지 삭제 실패")
                            success = False
                            break
                        time.sleep(DELAY_SHORT)
                    
                    # 일괄편집 모달창 닫기
                    if not self.close_bulk_edit_modal(timeout):
                        logger.warning("일괄편집 모달창 닫기 실패")
                    
                    if success:
                        logger.info(f"이미지 삭제 명령 처리 완료: {delete_command}")
                    return success
                    
                except (ValueError, IndexError) as e:
                    logger.error(f"삭제 명령 파싱 오류: {e}")
                    return False
            else:
                logger.error(f"지원하지 않는 삭제 명령: {delete_command}")
                return False
                
        except Exception as e:
            logger.error(f"이미지 삭제 명령 처리 오류: {e}")
            return False


def get_dropdown_helper3(driver):
    """
    PercentyDropdown3 인스턴스 생성 함수
    
    Args:
        driver: Selenium WebDriver 인스턴스
        
    Returns:
        PercentyDropdown3: 3단계 드롭다운 관리자 인스턴스
    """
    return PercentyDropdown3(driver)


# 사용 예시
if __name__ == "__main__":
    # 기본 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("퍼센티 3단계 드롭다운 및 이미지 삭제 유틸리티를 실행하려면 드라이버가 필요합니다.")
    print("percenty_step3.py에서 다음과 같이 사용하세요:")
    print("from dropdown_utils3 import get_dropdown_helper3")
    print("dropdown = get_dropdown_helper3(driver)")
    print("# 개별 상품 그룹 선택")
    print("dropdown.select_product_group_by_name('등록B')")
    print("# 이미지 삭제")
    print("dropdown.process_image_delete('first:1')")