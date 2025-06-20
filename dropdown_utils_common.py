# -*- coding: utf-8 -*-
"""
공통 드롭다운 유틸리티 (dropdown_utils_common.py)

4단계의 안정적인 스크롤 방식을 기반으로 한 통합 드롭다운 관리 유틸리티
5단계의 불안정한 상품 이동 문제 해결을 위해 개발

주요 기능:
- 안정적인 스크롤 기반 그룹 검색
- 상품 수 변경을 통한 그룹 선택 확인
- 상세한 로깅 및 디버깅 지원
- 다중 백업 전략 지원
"""

import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, ElementClickInterceptedException,
    StaleElementReferenceException
)
from selenium.webdriver.common.action_chains import ActionChains
import re

# 로거 설정
logger = logging.getLogger(__name__)

# 지연 시간 상수
DELAY_VERY_SHORT = 0.5
DELAY_SHORT = 1
DELAY_MEDIUM = 2
DELAY_LONG = 3

class CommonDropdownUtils:
    """
    공통 드롭다운 유틸리티 클래스
    4단계의 안정적인 방식을 기반으로 한 통합 드롭다운 관리
    """
    
    def __init__(self, driver):
        """
        초기화
        
        Args:
            driver: 셀레니움 웹드라이버
        """
        self.driver = driver
        logger.info("공통 드롭다운 유틸리티 초기화 완료")
    
    def advanced_scroll_and_search_for_group(self, group_name, max_scrolls=30):
        """
        드롭다운 내에서 고급 스크롤하며 그룹 검색 (4단계 방식 기반)
        
        Args:
            group_name (str): 찾을 그룹 이름
            max_scrolls (int): 최대 스크롤 횟수
            
        Returns:
            bool: 그룹을 찾았는지 여부
        """
        try:
            logger.info(f"드롭다운 내에서 '{group_name}' 그룹 고급 스크롤 검색 (최대 {max_scrolls}회)")
            
            # 드롭다운 컨테이너 찾기 (스크롤 가능한 컨테이너 우선)
            dropdown_selectors = [
                "//div[contains(@class, 'rc-virtual-list-holder')]",
                "//div[contains(@class, 'ant-select-dropdown') and not(contains(@class, 'ant-select-dropdown-hidden'))]",
                "//div[contains(@class, 'ant-select-dropdown')]"
            ]
            
            dropdown_container = None
            for selector in dropdown_selectors:
                try:
                    dropdown_container = self.driver.find_element(By.XPATH, selector)
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
                    time.sleep(0.3)  # 스크롤 후 대기
                    
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
            self.log_all_available_options()
            return False
            
        except Exception as e:
            logger.error(f"드롭다운 고급 스크롤 검색 오류: {e}")
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
    
    def log_all_available_options(self):
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
    
    def get_total_product_count(self, timeout=5):
        """
        전체 상품 수 확인 (최적화된 방식)
        
        Args:
            timeout (int): 대기 시간 (초)
            
        Returns:
            int: 상품 수 (-1: 오류)
        """
        try:
            # 상품 수 표시 요소 찾기 (성공률 높은 순서로 재배치)
            count_selectors = [
                # 1순위: 실제로 성공하는 선택자들 (로그 분석 기반)
                "//span[contains(text(), '총') and contains(text(), '상품')]",
                "//span[contains(text(), '총') and contains(text(), '개')]",
                
                # 2순위: 백업 선택자들
                "//div[contains(text(), '총') and contains(text(), '건')]",
                "//div[contains(@class, 'ant-pagination-total-text')]"
            ]
            
            for i, selector in enumerate(count_selectors, 1):
                try:
                    # 각 선택자마다 1초씩만 대기 (기존 3-5초에서 단축)
                    count_element = WebDriverWait(self.driver, 1).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    count_text = count_element.text
                    logger.debug(f"선택자 {i} 성공: '{count_text}'")
                    
                    # 숫자 추출 (쉼표 제거 후)
                    numbers = re.findall(r'[\d,]+', count_text)
                    if numbers:
                        # 쉼표 제거 후 숫자로 변환
                        count_str = numbers[0].replace(',', '')
                        count = int(count_str)
                        logger.info(f"전체 상품 수 확인 성공: {count}개")
                        return count
                        
                except (TimeoutException, NoSuchElementException, ValueError):
                    logger.debug(f"선택자 {i} 실패")
                    continue
            
            logger.warning("전체 상품 수를 확인할 수 없습니다.")
            return -1
            
        except Exception as e:
            logger.error(f"전체 상품 수 확인 중 오류: {e}")
            return -1
    
    def wait_for_product_count_change(self, initial_count, timeout=8):
        """
        상품 수 변경을 기다림 (최적화된 방식)
        
        Args:
            initial_count (int): 초기 상품 수
            timeout (int): 최대 대기 시간 (초)
            
        Returns:
            int: 변경된 상품 수 (-1: 변경 없음 또는 오류)
        """
        try:
            logger.info(f"상품 수 변경 대기 (초기: {initial_count}개, 최대 {timeout}초)")
            
            start_time = time.time()
            check_interval = 0.3  # 더 빠른 체크 간격
            
            while time.time() - start_time < timeout:
                # 타임아웃을 1초로 단축하여 빠른 응답
                current_count = self.get_total_product_count(timeout=1)
                
                if current_count != -1 and current_count != initial_count:
                    logger.info(f"상품 수 변경 감지: {initial_count}개 → {current_count}개")
                    return current_count
                
                # 첫 번째 체크에서 실패하면 간격을 늘려서 재시도
                if time.time() - start_time > 1:
                    check_interval = 0.5
                    
                time.sleep(check_interval)
            
            logger.warning(f"상품 수 변경이 감지되지 않았습니다 (대기시간: {timeout}초)")
            return -1
            
        except Exception as e:
            logger.error(f"상품 수 변경 대기 중 오류: {e}")
            return -1
    
    def select_group_with_verification(self, group_name, timeout=10):
        """
        그룹 선택 및 상품 수 변경 확인 (4단계 방식)
        
        Args:
            group_name (str): 선택할 그룹명
            timeout (int): 대기 시간 (초)
            
        Returns:
            bool: 선택 성공 여부
        """
        try:
            logger.info(f"그룹 '{group_name}' 선택 및 확인 시작")
            
            # 그룹 선택 전 전체 상품 수 확인 (빠른 응답을 위해 1초 타임아웃)
            initial_count = self.get_total_product_count(timeout=1)
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
            if self.advanced_scroll_and_search_for_group(group_name):
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
    
    def select_items_per_page_with_verification(self, items_count, timeout=5):
        """
        페이지당 항목 수 선택 및 확인
        
        Args:
            items_count (str): 선택할 항목 수 (예: "50")
            timeout (int): 대기 시간 (초)
            
        Returns:
            bool: 선택 성공 여부
        """
        try:
            logger.info(f"페이지당 {items_count}개 항목 설정 시작")
            
            # 페이지당 항목 수 드롭다운 선택자들 (우선순위 순)
            dropdown_selectors = [
                "//div[contains(@class, 'ant-pagination-options-size-changer')]//div[contains(@class, 'ant-select-selector')]",
                "//div[contains(@class, 'ant-select-single') and contains(@title, '개씩')]",
                "//div[contains(@class, 'ant-select') and .//span[contains(text(), '개씩')]]"
            ]
            
            # 드롭다운 열기
            dropdown_opened = False
            for selector in dropdown_selectors:
                try:
                    dropdown = WebDriverWait(self.driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    dropdown.click()
                    time.sleep(DELAY_SHORT)
                    logger.info(f"페이지당 항목 수 드롭다운 열기 성공: {selector}")
                    dropdown_opened = True
                    break
                except:
                    continue
            
            if not dropdown_opened:
                logger.error("페이지당 항목 수 드롭다운을 열 수 없습니다")
                return False
            
            # 옵션 선택
            option_selectors = [
                f"//div[contains(@class, 'ant-select-item-option') and contains(text(), '{items_count}')]",
                f"//div[contains(@class, 'ant-select-item-option') and .//span[contains(text(), '{items_count}')]]"
            ]
            
            option_selected = False
            for selector in option_selectors:
                try:
                    option = WebDriverWait(self.driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    option.click()
                    time.sleep(DELAY_SHORT)
                    logger.info(f"페이지당 {items_count}개 항목 선택 성공")
                    option_selected = True
                    break
                except:
                    continue
            
            if not option_selected:
                logger.error(f"페이지당 {items_count}개 항목 옵션을 찾을 수 없습니다")
                return False
            
            # 페이지 로드 대기
            time.sleep(DELAY_MEDIUM)
            
            # 설정 확인 (페이지 새로고침 확인)
            try:
                # 테이블이 다시 로드되었는지 확인
                WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'ant-table')]"))
                )
                logger.info(f"페이지당 {items_count}개 항목 설정 확인 완료")
                return True
            except TimeoutException:
                logger.warning(f"페이지당 {items_count}개 항목 설정 확인 실패 (타임아웃)")
                return False
            
        except Exception as e:
            logger.error(f"페이지당 항목 수 설정 중 오류: {e}")
            return False
    
    def click_element_with_multiple_methods(self, element):
        """
        요소를 여러 방법으로 클릭 시도 (4단계 방식)
        
        Args:
            element: 클릭할 요소
            
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
        
        logger.error("모든 클릭 방법 실패")
        return False

# 싱글톤 패턴으로 공통 드롭다운 유틸리티 인스턴스 관리
_common_dropdown_instance = None

def get_common_dropdown_utils(driver=None):
    """
    공통 드롭다운 유틸리티 인스턴스 가져오기 (싱글톤 패턴)
    
    Args:
        driver: 셀레니움 웹드라이버 (선택 사항)
        
    Returns:
        CommonDropdownUtils: 공통 드롭다운 유틸리티 인스턴스
    """
    global _common_dropdown_instance
    
    if _common_dropdown_instance is None or driver is not None:
        if driver is None:
            raise ValueError("첫 번째 호출 시 driver 매개변수가 필요합니다.")
        _common_dropdown_instance = CommonDropdownUtils(driver)
        logger.info("새로운 공통 드롭다운 유틸리티 인스턴스가 생성되었습니다.")
    
    return _common_dropdown_instance

if __name__ == "__main__":
    print("공통 드롭다운 유틸리티 모듈")
    print("사용법:")
    print("from dropdown_utils_common import get_common_dropdown_utils")
    print("common_utils = get_common_dropdown_utils(driver)")
    print("common_utils.select_group_with_verification('그룹명')")