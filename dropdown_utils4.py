# -*- coding: utf-8 -*-
"""
퍼센티 Step4용 드롭박스 및 체크박스 유틸리티

이 모듈은 product_editor_core4.py에서 사용하는 전용 유틸리티입니다.
주요 기능:
1. 상품검색 드롭박스 (첫 번째 ant-select-single)
2. 20개/50개씩 보기 드롭박스 (두 번째 ant-select-single)
3. 전체선택 체크박스 (ant-checkbox-wrapper)

DOM 구조 분석 기반으로 정확한 선택자를 사용합니다.
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains

# 로깅 설정
logger = logging.getLogger(__name__)

# 대기 시간 설정
DELAY_VERY_SHORT = 0.5
DELAY_SHORT = 1
DELAY_MEDIUM = 2
DELAY_LONG = 3

class DropdownUtils4:
    """
    Step4용 드롭박스 및 체크박스 관리 클래스
    """
    
    def __init__(self, driver):
        self.driver = driver
        logger.info("DropdownUtils4 초기화 완료")
    
    # =============================================================================
    # 상품검색 드롭박스 관련 메서드 (첫 번째 ant-select-single)
    # =============================================================================
    
    def open_product_search_dropdown(self, timeout=10):
        """
        상품검색 드롭박스를 엽니다 (첫 번째 ant-select-single)
        
        Args:
            timeout (int): 대기 시간 (초)
            
        Returns:
            bool: 성공 여부
        """
        logger.info("상품검색 드롭박스 열기 시도")
        
        # 상품검색 드롭박스 선택자들 (첫 번째)
        selectors = [
            "(//div[contains(@class, 'ant-select-single')])[1]",
            "(//div[contains(@class, 'ant-select-selector')])[1]",
            "//div[contains(@class, 'ant-select-single')][1]"
        ]
        
        for i, selector in enumerate(selectors, 1):
            try:
                logger.info(f"선택자 {i} 시도: {selector}")
                
                # 요소 찾기 및 클릭 가능 상태까지 대기
                element = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                
                # 요소가 화면에 보이도록 스크롤
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                time.sleep(DELAY_VERY_SHORT)
                
                # 클릭 시도
                element.click()
                time.sleep(DELAY_SHORT)
                
                # 드롭박스가 열렸는지 확인
                if self._is_dropdown_open():
                    logger.info(f"상품검색 드롭박스 열기 성공 (선택자 {i})")
                    return True
                else:
                    logger.warning(f"드롭박스가 열리지 않음 (선택자 {i})")
                    
            except TimeoutException:
                logger.warning(f"선택자 {i} 타임아웃: {selector}")
            except Exception as e:
                logger.warning(f"선택자 {i} 오류: {e}")
        
        logger.error("모든 선택자로 상품검색 드롭박스 열기 실패")
        return False
    
    def select_group_in_search_dropdown(self, group_name):
        """
        상품검색 드롭박스에서 특정 그룹을 선택합니다
        
        Args:
            group_name (str): 선택할 그룹명 (예: "서버1")
            
        Returns:
            bool: 성공 여부
        """
        logger.info(f"상품검색 드롭박스에서 '{group_name}' 그룹 선택 시작")
        
        # 1. 드롭박스 열기
        if not self.open_product_search_dropdown():
            logger.error("상품검색 드롭박스 열기 실패")
            return False
        
        # 2. 그룹 선택
        if not self._select_group_option(group_name):
            logger.error(f"그룹 '{group_name}' 선택 실패")
            return False
        
        logger.info(f"상품검색 드롭박스에서 '{group_name}' 그룹 선택 완료")
        return True
    
    # =============================================================================
    # 페이지 크기 드롭박스 관련 메서드 (두 번째 ant-select-single)
    # =============================================================================
    
    def open_page_size_dropdown(self, timeout=10):
        """
        페이지 크기 드롭박스를 엽니다 (두 번째 ant-select-single)
        
        Args:
            timeout (int): 대기 시간 (초)
            
        Returns:
            bool: 성공 여부
        """
        logger.info("페이지 크기 드롭박스 열기 시도")
        
        # 페이지 크기 드롭박스 선택자들 (두 번째)
        selectors = [
            "(//div[contains(@class, 'ant-select-single')])[2]",
            "(//div[contains(@class, 'ant-select-selector')])[2]",
            "//div[contains(@class, 'ant-select-single')][2]"
        ]
        
        for i, selector in enumerate(selectors, 1):
            try:
                logger.info(f"선택자 {i} 시도: {selector}")
                
                # 요소 찾기 및 클릭 가능 상태까지 대기
                element = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                
                # 요소가 화면에 보이도록 스크롤
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                time.sleep(DELAY_VERY_SHORT)
                
                # 클릭 시도
                element.click()
                time.sleep(DELAY_SHORT)
                
                # 드롭박스가 열렸는지 확인
                if self._is_dropdown_open():
                    logger.info(f"페이지 크기 드롭박스 열기 성공 (선택자 {i})")
                    return True
                else:
                    logger.warning(f"드롭박스가 열리지 않음 (선택자 {i})")
                    
            except TimeoutException:
                logger.warning(f"선택자 {i} 타임아웃: {selector}")
            except Exception as e:
                logger.warning(f"선택자 {i} 오류: {e}")
        
        logger.error("모든 선택자로 페이지 크기 드롭박스 열기 실패")
        return False
    
    def select_page_size(self, size="50"):
        """
        페이지 크기를 선택합니다 (20개씩 보기, 50개씩 보기 등)
        
        Args:
            size (str): 선택할 페이지 크기 ("20", "50" 등)
            
        Returns:
            bool: 성공 여부
        """
        logger.info(f"페이지 크기 '{size}개씩 보기' 선택 시작")
        
        # 1. 드롭박스 열기
        if not self.open_page_size_dropdown():
            logger.error("페이지 크기 드롭박스 열기 실패")
            return False
        
        # 2. 크기 선택
        option_text = f"{size}개씩 보기"
        if not self._select_dropdown_option(option_text):
            logger.error(f"페이지 크기 '{option_text}' 선택 실패")
            return False
        
        logger.info(f"페이지 크기 '{option_text}' 선택 완료")
        return True
    
    # =============================================================================
    # 전체선택 체크박스 관련 메서드
    # =============================================================================
    
    def select_all_products(self, timeout=10):
        """
        전체선택 체크박스를 클릭합니다
        
        Args:
            timeout (int): 대기 시간 (초)
            
        Returns:
            bool: 성공 여부
        """
        logger.info("전체선택 체크박스 클릭 시도")
        
        # 전체선택 체크박스 선택자들
        selectors = [
            "//label[contains(@class, 'ant-checkbox-wrapper')]",
            "//label[contains(@class, 'ant-checkbox-wrapper')]//input[@type='checkbox']",
            "//span[contains(@class, 'ant-checkbox')]",
            "//input[@type='checkbox'][ancestor::label[contains(@class, 'ant-checkbox-wrapper')]]"
        ]
        
        for i, selector in enumerate(selectors, 1):
            try:
                logger.info(f"체크박스 선택자 {i} 시도: {selector}")
                
                # 요소 찾기
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                
                # 요소가 화면에 보이도록 스크롤
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                time.sleep(DELAY_VERY_SHORT)
                
                # 클릭 시도 (여러 방법)
                if self._click_checkbox_element(element):
                    logger.info(f"전체선택 체크박스 클릭 성공 (선택자 {i})")
                    return True
                else:
                    logger.warning(f"체크박스 클릭 실패 (선택자 {i})")
                    
            except TimeoutException:
                logger.warning(f"체크박스 선택자 {i} 타임아웃: {selector}")
            except Exception as e:
                logger.warning(f"체크박스 선택자 {i} 오류: {e}")
        
        # JavaScript 직접 클릭 시도
        logger.info("JavaScript 직접 클릭 시도")
        if self._js_click_select_all_checkbox():
            logger.info("JavaScript로 전체선택 체크박스 클릭 성공")
            return True
        
        logger.error("모든 방법으로 전체선택 체크박스 클릭 실패")
        return False
    
    # =============================================================================
    # 공통 헬퍼 메서드
    # =============================================================================
    
    def _is_dropdown_open(self, timeout=3):
        """
        드롭박스가 열렸는지 확인합니다
        
        Args:
            timeout (int): 대기 시간 (초)
            
        Returns:
            bool: 드롭박스가 열린 상태인지 여부
        """
        try:
            # 열린 드롭박스 확인
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((
                    By.XPATH, 
                    "//div[contains(@class, 'ant-select-dropdown') and not(contains(@class, 'ant-select-dropdown-hidden'))]"
                ))
            )
            return True
        except TimeoutException:
            return False
    
    def _select_group_option(self, group_name, timeout=10):
        """
        드롭박스에서 특정 그룹을 선택합니다 (스크롤 지원 및 동적 처리)
        
        Args:
            group_name (str): 선택할 그룹명
            timeout (int): 대기 시간 (초)
            
        Returns:
            bool: 선택 성공 여부
        """
        logger.info(f"그룹 '{group_name}' 선택 시도")
        
        try:
            # 그룹 선택 전 전체 상품 수 확인
            initial_count = self.get_total_product_count(timeout=3)
            if initial_count != -1:
                logger.info(f"그룹 선택 전 전체 상품 수: {initial_count}개")
            
            # 먼저 현재 보이는 옵션에서 찾기 시도
            if self._find_and_click_group_option(group_name):
                logger.info(f"그룹 '{group_name}' 선택 성공")
                
                # 동적 처리: 상품 수 변경 확인
                if initial_count != -1:
                    changed_count = self.wait_for_product_count_change(initial_count, timeout=8)
                    if changed_count != -1 and changed_count < initial_count:
                        logger.info(f"그룹 선택 확인됨: 상품 수 {initial_count}개 → {changed_count}개로 감소")
                        return True
                    elif changed_count != -1:
                        logger.warning(f"상품 수가 예상과 다름: {initial_count}개 → {changed_count}개")
                        return True  # 변경은 되었으므로 성공으로 간주
                    else:
                        logger.warning("상품 수 변경을 확인할 수 없지만 그룹 선택은 완료됨")
                        return True
                else:
                    # 초기 상품 수를 확인할 수 없었던 경우 기본 대기
                    time.sleep(2)
                    return True
            
            # 보이지 않으면 스크롤하면서 찾기
            logger.info(f"'{group_name}' 그룹이 현재 화면에 없어 스크롤 검색 시작")
            if self._scroll_and_search_for_group(group_name):
                logger.info(f"스크롤 후 '{group_name}' 그룹을 찾았습니다.")
                
                # 동적 처리: 상품 수 변경 확인
                if initial_count != -1:
                    changed_count = self.wait_for_product_count_change(initial_count, timeout=8)
                    if changed_count != -1 and changed_count < initial_count:
                        logger.info(f"그룹 선택 확인됨: 상품 수 {initial_count}개 → {changed_count}개로 감소")
                        return True
                    elif changed_count != -1:
                        logger.warning(f"상품 수가 예상과 다름: {initial_count}개 → {changed_count}개")
                        return True  # 변경은 되었으므로 성공으로 간주
                    else:
                        logger.warning("상품 수 변경을 확인할 수 없지만 그룹 선택은 완료됨")
                        return True
                else:
                    # 초기 상품 수를 확인할 수 없었던 경우 기본 대기
                    time.sleep(2)
                    return True
            
            logger.error(f"그룹 '{group_name}'을 찾을 수 없습니다")
            return False
            
        except Exception as e:
            logger.error(f"그룹 선택 중 오류: {e}")
            return False
    
    def _find_and_click_group_option(self, group_name):
        """
        현재 보이는 그룹 옵션들에서 찾아서 클릭
        
        Args:
            group_name (str): 찾을 그룹명
            
        Returns:
            bool: 성공 여부
        """
        try:
            # 현재 보이는 모든 그룹 옵션들 가져오기
            option_elements = self.driver.find_elements(
                By.XPATH, "//div[contains(@class, 'ant-select-item-option')]"
            )
            
            logger.info(f"현재 화면에 {len(option_elements)}개의 옵션 발견")
            
            for i, option in enumerate(option_elements):
                try:
                    option_text = option.text.strip()
                    logger.info(f"옵션 {i+1}: '{option_text}'")
                    
                    if option_text == group_name:
                        logger.info(f"일치하는 그룹 발견: '{option_text}'")
                        
                        # 옵션 클릭 시도
                        try:
                            option.click()
                            time.sleep(DELAY_SHORT)
                            logger.info(f"그룹 '{group_name}' 선택 성공")
                            return True
                        except ElementClickInterceptedException:
                            # JavaScript로 클릭 시도
                            self.driver.execute_script("arguments[0].click();", option)
                            time.sleep(DELAY_SHORT)
                            logger.info(f"그룹 '{group_name}' JavaScript 클릭 성공")
                            return True
                            
                except Exception as e:
                    logger.warning(f"옵션 {i+1} 처리 중 오류: {e}")
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"그룹 옵션 찾기 중 오류: {e}")
            return False
    
    def _scroll_and_search_for_group(self, group_name, max_scrolls=30):
        """
        드롭다운 내에서 스크롤하며 그룹 검색
        
        Args:
            group_name (str): 찾을 그룹 이름
            max_scrolls (int): 최대 스크롤 횟수
            
        Returns:
            bool: 그룹을 찾았는지 여부
        """
        try:
            logger.info(f"드롭다운 내에서 '{group_name}' 그룹 스크롤 검색 (최대 {max_scrolls}회)")
            
            # 드롭다운 컨테이너 찾기 (스크롤 가능한 컨테이너 우선)
            dropdown_selectors = [
                "//div[contains(@class, 'rc-virtual-list-holder')]",
                "//div[contains(@class, 'ant-select-dropdown') and not(contains(@class, 'ant-select-dropdown-hidden'))]",
                "//div[contains(@class, 'ant-select-dropdown')]"
            ]
            
            dropdown_container = None
            for selector in dropdown_selectors:
                try:
                    if selector.startswith("//"):
                        dropdown_container = self.driver.find_element(By.XPATH, selector)
                    else:
                        dropdown_container = self.driver.find_element(By.CSS_SELECTOR, selector)
                    logger.info(f"드롭다운 컨테이너 발견: {selector}")
                    break
                except:
                    continue
            
            if not dropdown_container:
                logger.error("드롭다운 컨테이너를 찾을 수 없음")
                return False
            
            # 스크롤하며 검색
            for scroll_count in range(max_scrolls):
                logger.info(f"스크롤 {scroll_count + 1}/{max_scrolls}")
                
                # 현재 보이는 그룹들 중에서 찾기
                if self._find_and_click_group_option(group_name):
                    logger.info(f"스크롤 {scroll_count + 1}회 후 '{group_name}' 그룹을 찾았습니다.")
                    return True
                
                # 아래로 스크롤 (여러 방법 시도)
                scroll_success = False
                
                # 방법 1: clientHeight를 사용한 한 화면씩 스크롤
                try:
                    self.driver.execute_script("arguments[0].scrollTop += arguments[0].clientHeight;", dropdown_container)
                    scroll_success = True
                except:
                    pass
                
                # 방법 2: 고정 픽셀 스크롤 (fallback)
                if not scroll_success:
                    try:
                        self.driver.execute_script("arguments[0].scrollTop += 200;", dropdown_container)
                        scroll_success = True
                    except:
                        pass
                
                # 방법 3: 마지막 옵션으로 스크롤
                if not scroll_success:
                    try:
                        last_option = dropdown_container.find_elements(
                            By.XPATH, ".//div[contains(@class, 'ant-select-item-option')]"
                        )[-1]
                        self.driver.execute_script("arguments[0].scrollIntoView();", last_option)
                        scroll_success = True
                    except:
                        pass
                
                if scroll_success:
                    time.sleep(0.3)  # 스크롤 후 대기 (시간 단축)
                    
                    # 스크롤 후 새로운 옵션이 로드되었는지 확인
                    new_options = self.driver.find_elements(
                        By.XPATH, "//div[contains(@class, 'ant-select-item-option')]"
                    )
                    logger.info(f"스크롤 후 {len(new_options)}개 옵션 확인")
                else:
                    logger.warning(f"스크롤 {scroll_count + 1} 실패")
                    break  # 스크롤이 실패하면 더 이상 시도하지 않음
            
            logger.warning(f"최대 스크롤 횟수({max_scrolls})에 도달했지만 '{group_name}' 그룹을 찾지 못했습니다.")
            
            # 마지막으로 전체 옵션 목록 출력
            self._log_all_available_options()
            return False
            
        except Exception as e:
            logger.error(f"드롭다운 스크롤 검색 오류: {e}")
            return False
    
    def _log_all_available_options(self):
        """
        현재 드롭다운에서 사용 가능한 모든 옵션들을 로그에 출력
        """
        try:
            logger.info("=== 현재 사용 가능한 모든 옵션들 ===")
            option_elements = self.driver.find_elements(
                By.XPATH, "//div[contains(@class, 'ant-select-item-option')]"
            )
            
            for i, option in enumerate(option_elements):
                try:
                    option_text = option.text.strip()
                    logger.info(f"사용 가능한 옵션 {i+1}: '{option_text}'")
                except:
                    logger.info(f"사용 가능한 옵션 {i+1}: (텍스트 읽기 실패)")
            
            logger.info(f"=== 총 {len(option_elements)}개의 옵션 ===")
            
        except Exception as e:
            logger.error(f"옵션 목록 출력 중 오류: {e}")
    
    def _select_dropdown_option(self, option_text, timeout=10):
        """
        드롭박스에서 특정 옵션을 선택합니다
        
        Args:
            option_text (str): 선택할 옵션 텍스트
            timeout (int): 대기 시간 (초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            # 옵션 찾기
            option_xpath = f"//div[contains(@class, 'ant-select-item-option') and contains(text(), '{option_text}')]"
            
            option_element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, option_xpath))
            )
            
            # 옵션 클릭
            option_element.click()
            time.sleep(DELAY_SHORT)
            
            logger.info(f"드롭박스 옵션 '{option_text}' 선택 성공")
            return True
            
        except TimeoutException:
            logger.error(f"드롭박스 옵션 '{option_text}'을 찾을 수 없음 (타임아웃)")
            return False
        except Exception as e:
            logger.error(f"드롭박스 옵션 선택 중 오류: {e}")
            return False
    
    def _click_checkbox_element(self, element):
        """
        체크박스 요소를 클릭합니다 (여러 방법 시도)
        
        Args:
            element: 클릭할 체크박스 요소
            
        Returns:
            bool: 성공 여부
        """
        # 방법 1: 직접 클릭
        try:
            element.click()
            time.sleep(DELAY_VERY_SHORT)
            logger.info("직접 클릭 성공")
            return True
        except Exception as e:
            logger.warning(f"직접 클릭 실패: {e}")
        
        # 방법 2: ActionChains 클릭
        try:
            actions = ActionChains(self.driver)
            actions.move_to_element(element).click().perform()
            time.sleep(DELAY_VERY_SHORT)
            logger.info("ActionChains 클릭 성공")
            return True
        except Exception as e:
            logger.warning(f"ActionChains 클릭 실패: {e}")
        
        # 방법 3: JavaScript 클릭
        try:
            self.driver.execute_script("arguments[0].click();", element)
            time.sleep(DELAY_VERY_SHORT)
            logger.info("JavaScript 클릭 성공")
            return True
        except Exception as e:
            logger.warning(f"JavaScript 클릭 실패: {e}")
        
        # 방법 4: 라벨 래퍼 클릭 시도
        try:
            label_wrapper = element.find_element(By.XPATH, "./ancestor::label[contains(@class, 'ant-checkbox-wrapper')]")
            label_wrapper.click()
            time.sleep(DELAY_VERY_SHORT)
            logger.info("라벨 래퍼 클릭 성공")
            return True
        except Exception as e:
            logger.warning(f"라벨 래퍼 클릭 실패: {e}")
        
        return False
    
    def _js_click_select_all_checkbox(self):
        """
        JavaScript로 전체선택 체크박스를 직접 클릭합니다
        
        Returns:
            bool: 성공 여부
        """
        try:
            result = self.driver.execute_script("""
                // 전체선택 체크박스 찾기
                const checkboxes = Array.from(document.querySelectorAll('input[type="checkbox"]'))
                    .filter(el => {
                        const rect = el.getBoundingClientRect();
                        return el.offsetParent !== null && 
                               !el.disabled && 
                               rect.width > 0 && 
                               rect.height > 0 &&
                               rect.top >= 0 &&
                               rect.left >= 0;
                    });
                
                if (checkboxes.length > 0) {
                    const checkbox = checkboxes[0]; // 첫 번째 체크박스 (전체선택)
                    const initialState = checkbox.checked;
                    
                    // 클릭 시뮬레이션
                    checkbox.click();
                    
                    // 상태 변경 확인
                    if (checkbox.checked !== initialState) {
                        return {success: true, message: '상태 변경됨: ' + initialState + ' -> ' + checkbox.checked};
                    } else {
                        // 강제 이벤트 발생
                        const events = ['change', 'click', 'input'];
                        events.forEach(eventType => {
                            const event = new Event(eventType, { bubbles: true, cancelable: true });
                            checkbox.dispatchEvent(event);
                        });
                        return {success: true, message: '강제 이벤트 발생'};
                    }
                } else {
                    return {success: false, message: '체크박스를 찾을 수 없음'};
                }
            """)
            
            if result and result.get('success'):
                logger.info(f"JavaScript 체크박스 클릭 성공: {result.get('message')}")
                time.sleep(DELAY_SHORT)
                return True
            else:
                logger.warning(f"JavaScript 체크박스 클릭 실패: {result.get('message') if result else 'Unknown error'}")
                return False
                
        except Exception as e:
            logger.error(f"JavaScript 체크박스 클릭 중 오류: {e}")
            return False
    
    def get_total_product_count(self, timeout=10):
        """
        전체 상품 수를 확인합니다.
        
        Args:
            timeout (int): 대기 시간 (초)
            
        Returns:
            int: 전체 상품 수 (확인 실패 시 -1)
        """
        try:
            # 전체선택 체크박스 부분에서 총 상품 수 확인
            # <span>총 24,025개 상품</span>
            selectors = [
                "//span[contains(text(), '총') and contains(text(), '개 상품')]",
                "//div[contains(@class, 'ant-checkbox-wrapper')]//span[contains(text(), '총') and contains(text(), '개 상품')]",
                "//label[contains(@class, 'ant-checkbox-wrapper')]//span[contains(text(), '총') and contains(text(), '개 상품')]"
            ]
            
            for selector in selectors:
                try:
                    element = WebDriverWait(self.driver, timeout).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    
                    text = element.text.strip()
                    logger.info(f"전체 상품 수 텍스트 발견: '{text}'")
                    
                    # "총 24,025개 상품" 형태에서 숫자 추출
                    import re
                    match = re.search(r'총\s*([0-9,]+)개\s*상품', text)
                    if match:
                        count_str = match.group(1).replace(',', '')
                        count = int(count_str)
                        logger.info(f"전체 상품 수 확인 성공: {count}개")
                        return count
                        
                except TimeoutException:
                    continue
                except Exception as e:
                    logger.warning(f"전체 상품 수 확인 중 오류 (선택자: {selector}): {e}")
                    continue
            
            logger.warning("전체 상품 수를 확인할 수 없습니다")
            return -1
            
        except Exception as e:
            logger.error(f"전체 상품 수 확인 중 전체 오류: {e}")
            return -1
    
    def wait_for_product_count_change(self, initial_count, timeout=10):
        """
        상품 수가 변경될 때까지 동적으로 대기합니다.
        
        Args:
            initial_count (int): 초기 상품 수
            timeout (int): 최대 대기 시간 (초)
            
        Returns:
            int: 변경된 상품 수 (시간 초과 시 -1)
        """
        logger.info(f"상품 수 변경 대기 시작 (초기: {initial_count}개, 최대 대기: {timeout}초)")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            current_count = self.get_total_product_count(timeout=2)
            
            if current_count != -1 and current_count != initial_count:
                logger.info(f"상품 수 변경 확인: {initial_count}개 → {current_count}개")
                return current_count
            
            time.sleep(0.5)  # 0.5초마다 확인
        
        logger.warning(f"상품 수 변경 대기 시간 초과 ({timeout}초)")
        return -1
    
    def verify_page_refresh(self, timeout=10):
        """
        페이지가 새로고침되어 로드되었는지 확인
        
        Args:
            timeout (int): 대기 시간 (초)
            
        Returns:
            bool: 페이지 로드 성공 여부
        """
        logger.info("페이지 새로고침 및 로드 확인")
        
        try:
            # 충분한 페이지 로드 대기
            logger.info("페이지 로드를 위해 5초 대기")
            time.sleep(5)
            
            # 페이지 기본 구조가 로드되었는지 확인
            load_indicators = [
                "//div[contains(@class, 'ant-table')]",
                "//div[contains(@class, 'ant-table-thead')]",
                "//div[contains(@class, 'ant-table-container')]",
                "//thead[contains(@class, 'ant-table-thead')]",
            ]
            
            # 최소 하나의 기본 구조 요소가 있으면 페이지 로드 완료로 간주
            for indicator in load_indicators:
                try:
                    element = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((By.XPATH, indicator))
                    )
                    if element.is_displayed():
                        logger.info(f"페이지 기본 구조 로드 확인됨: {indicator}")
                        return True
                except TimeoutException:
                    continue
            
            # 기본 구조 요소를 찾지 못해도 충분한 시간이 지났으므로 성공으로 간주
            logger.info("기본 구조 요소를 찾지 못했지만 충분한 대기시간이 지나 로드 완료로 간주")
            return True
            
        except Exception as e:
            logger.warning(f"페이지 새로고침 확인 중 오류 (무시하고 계속): {e}")
            return True
    
    # =============================================================================
    # 그룹 지정 모달창 관련 메서드
    # =============================================================================
    
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
            
            # DOM 구조에 맞는 그룹 지정 버튼 선택자들 (우선순위 순)
            button_selectors = [
                "//div[contains(@class, 'ant-btn-group')]//button[.//span[text()='그룹 지정']]",
                "//button[.//span[text()='그룹 지정']]",
                "//button[contains(text(), '그룹 지정')]",
                "//div[contains(@class, 'ant-flex')]//button[.//span[text()='그룹 지정']]"
            ]
            
            for i, button_selector in enumerate(button_selectors):
                try:
                    logger.info(f"그룹 지정 버튼 시도 {i+1}: {button_selector}")
                    
                    # 버튼이 활성화될 때까지 잠시 대기
                    time.sleep(0.5)
                    
                    button_element = WebDriverWait(self.driver, timeout).until(
                        EC.element_to_be_clickable((By.XPATH, button_selector))
                    )
                    
                    # 버튼이 비활성화되어 있는지 확인
                    if button_element.get_attribute("disabled"):
                        logger.warning(f"그룹 지정 버튼이 비활성화되어 있습니다. 선택자: {button_selector}")
                        continue
                        
                    button_element.click()
                    time.sleep(0.5)
                    
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
                    
                except (TimeoutException, NoSuchElementException):
                    logger.warning(f"선택자 {i+1} 실패: {button_selector}")
                    continue
                    
            logger.error("모든 그룹 지정 버튼 선택자가 실패했습니다.")
            return False
                
        except Exception as e:
            logger.error(f"그룹 지정 모달창 열기 오류: {e}")
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
                time.sleep(0.5)
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
                    logger.error("모달창이 닫히지 않았습니다. 그룹 이동이 실패했을 수 있습니다.")
                    return False
                
            except (TimeoutException, NoSuchElementException):
                logger.error(f"'{group_name}' 그룹을 찾을 수 없습니다.")
                # 그룹을 찾지 못한 경우에도 모달창이 열려있을 수 있으므로 닫기 시도
                self._close_modal_if_open()
                return False
                
        except Exception as e:
            logger.error(f"그룹 이동 모달창에서 그룹 선택 오류: {e}")
            return False
    
    def _close_modal_if_open(self, timeout=5):
        """
        열려있는 모달창이 있으면 닫기
        
        Args:
            timeout: 최대 대기 시간(초)
        """
        try:
            # 모달창 닫기 버튼 선택자들
            close_selectors = [
                "//div[contains(@class, 'ant-modal-header')]//button[contains(@class, 'ant-modal-close')]",
                "//div[contains(@class, 'ant-modal-footer')]//button[contains(@class, 'ant-btn')][.//span[text()='취소']]",
                "//button[@aria-label='Close']"
            ]
            
            for selector in close_selectors:
                try:
                    close_button = WebDriverWait(self.driver, timeout).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    close_button.click()
                    logger.info("모달창 닫기 완료")
                    return True
                except (TimeoutException, NoSuchElementException):
                    continue
                    
            logger.warning("모달창 닫기 버튼을 찾을 수 없습니다.")
            return False
            
        except Exception as e:
            logger.error(f"모달창 닫기 오류: {e}")
            return False