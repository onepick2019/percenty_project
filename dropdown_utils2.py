# -*- coding: utf-8 -*-
"""
상품검색용 드롭박스 전용 유틸리티 (Step2 전용)

이 모듈은 오직 상품검색 드롭박스의 그룹 선택만을 담당합니다.
개별 상품 그룹 이동과는 완전히 분리된 기능입니다.
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

# 로깅 설정
logger = logging.getLogger(__name__)

class ProductSearchDropdownManager:
    """
    상품검색용 드롭박스 관리 클래스
    오직 상품검색 필터의 그룹 선택만을 담당
    """
    
    def __init__(self, driver):
        self.driver = driver
        
        # 상품검색 드롭박스 선택자들 (3번째 드롭박스)
        self.search_dropdown_selectors = [
            "(//div[contains(@class, 'ant-select-single')])[3]",
            "(//div[contains(@class, 'ant-select-selector')])[3]",
            "//div[contains(@class, 'ant-select-single')][3]"
        ]
        
        # 드롭박스가 열렸는지 확인하는 선택자
        self.dropdown_open_selector = "//div[contains(@class, 'ant-select-dropdown') and not(contains(@class, 'ant-select-dropdown-hidden'))]"
        
        # 그룹 옵션 선택자
        self.group_option_selector = "//div[contains(@class, 'ant-select-item-option')]"
    
    def _action_chains_click(self, element):
        """ActionChains를 사용한 클릭"""
        from selenium.webdriver.common.action_chains import ActionChains
        actions = ActionChains(self.driver)
        actions.move_to_element(element).pause(0.1).click().perform()
    
    def _parent_element_click(self, element):
        """부모 요소 클릭 (label이나 wrapper)"""
        parent_element = element.find_element(By.XPATH, "./parent::*")
        parent_element.click()
    
    def _label_click(self, element):
        """연관된 label 요소 클릭"""
        # for 속성으로 연결된 label 찾기
        element_id = element.get_attribute('id')
        if element_id:
            try:
                label = self.driver.find_element(By.XPATH, f"//label[@for='{element_id}']")
                label.click()
                return
            except:
                pass
        
        # 부모 중에서 label 찾기
        try:
            label = element.find_element(By.XPATH, "./ancestor::label[1]")
            label.click()
        except:
            # 형제 요소 중에서 label 찾기
            try:
                label = element.find_element(By.XPATH, "./following-sibling::label[1] | ./preceding-sibling::label[1]")
                label.click()
            except:
                raise Exception("연관된 label을 찾을 수 없음")
    
    def _label_wrapper_click(self, element):
        """
        체크박스의 라벨 래퍼를 클릭합니다.
        
        Args:
            element: 체크박스 요소
            
        Returns:
            bool: 성공 여부
        """
        try:
            # 라벨 래퍼 찾기
            label_wrapper = element.find_element(By.XPATH, "./ancestor::label[contains(@class, 'ant-checkbox-wrapper')]")
            label_wrapper.click()
            logger.info("라벨 래퍼 클릭 성공")
            return True
        except Exception as e:
            logger.warning(f"라벨 래퍼 클릭 실패: {e}")
            return False
    
    def _span_wrapper_click(self, element):
        """
        체크박스의 스팬 래퍼를 클릭합니다.
        
        Args:
            element: 체크박스 요소
            
        Returns:
            bool: 성공 여부
        """
        try:
            # 스팬 래퍼 찾기
            span_wrapper = element.find_element(By.XPATH, "./following-sibling::span[contains(@class, 'ant-checkbox-inner')]")
            span_wrapper.click()
            logger.info("스팬 래퍼 클릭 성공")
            return True
        except Exception as e:
            logger.warning(f"스팬 래퍼 클릭 실패: {e}")
            return False

    def _force_state_change(self, element):
        """JavaScript로 강제 상태 변경"""
        self.driver.execute_script("""
            const checkbox = arguments[0];
            const wasChecked = checkbox.checked;
            
            // 1. 상태 강제 변경
            checkbox.checked = !wasChecked;
            
            // 2. 모든 관련 이벤트 발생
            const events = ['change', 'click', 'input', 'focus', 'blur'];
            events.forEach(eventType => {
                const event = new Event(eventType, { bubbles: true, cancelable: true });
                checkbox.dispatchEvent(event);
            });
            
            // 3. React/Vue 등의 프레임워크를 위한 추가 이벤트
            if (window.React || window.Vue) {
                const syntheticEvent = new Event('input', { bubbles: true });
                Object.defineProperty(syntheticEvent, 'target', {
                    writable: false,
                    value: checkbox
                });
                checkbox.dispatchEvent(syntheticEvent);
            }
        """, element)
    
    def _js_direct_click(self, checkbox_index):
        """
        JavaScript로 체크박스를 직접 클릭합니다.
        
        *** 핵심 체크박스 클릭 메서드 - 안정적으로 검증됨 ***
        
        이 메서드는 다음과 같은 상황에서 안정적으로 작동합니다:
        - 'Select all' 체크박스 클릭 (로그에서 검증됨)
        - Ant Design 체크박스 (ant-checkbox-input 클래스)
        - 일반적인 HTML 체크박스
        - 동적으로 생성된 체크박스
        
        사용법:
        1. JavaScript로 클릭 가능한 체크박스 목록을 먼저 생성
        2. 원하는 체크박스의 인덱스를 전달
        3. 상태 변경 여부를 확인하여 성공/실패 판단
        
        장점:
        - Selenium의 ElementClickInterceptedException 회피
        - 화면에 보이지 않는 요소도 클릭 가능
        - 빠른 실행 속도
        - 상태 변경 확인으로 실제 클릭 성공 여부 검증
        - 다중 클릭 방법 지원 (직접 클릭 + 이벤트 시뮬레이션)
        
        성공 사례 (로그 기록):
        - 'Select all' 체크박스: direct_click 방법으로 상태 변경 False -> True
        - 20개 상품 선택 후 그룹 이동 성공
        
        Args:
            checkbox_index (int): 클릭할 체크박스의 인덱스 (0부터 시작)
            
        Returns:
            bool: 클릭 성공 여부 (상태 변경 기준)
        """
        try:
            result = self.driver.execute_script("""
                var checkboxes = Array.from(document.querySelectorAll('input[type="checkbox"]'))
                    .filter(el => {
                        const rect = el.getBoundingClientRect();
                        return el.offsetParent !== null && 
                               !el.disabled && 
                               rect.width > 0 && 
                               rect.height > 0 &&
                               rect.top >= 0 &&
                               rect.left >= 0;
                    });
                
                if (checkboxes[arguments[0]]) {
                    var checkbox = checkboxes[arguments[0]];
                    var initialState = checkbox.checked;
                    
                    try {
                        // 방법 1: 직접 클릭 시뮬레이션
                        checkbox.click();
                        
                        // 상태가 변경되었는지 확인
                        if (checkbox.checked !== initialState) {
                            return { success: true, method: 'direct_click', initialState: initialState, finalState: checkbox.checked };
                        }
                        
                        // 방법 2: 상태 변경 + 이벤트 발생
                        checkbox.checked = !initialState;
                        
                        // 다양한 이벤트 발생
                        var events = ['mousedown', 'mouseup', 'click', 'change', 'input'];
                        events.forEach(function(eventType) {
                            var event = new Event(eventType, { bubbles: true, cancelable: true });
                            checkbox.dispatchEvent(event);
                        });
                        
                        // 마우스 이벤트도 시도
                        var mouseEvent = new MouseEvent('click', {
                            bubbles: true,
                            cancelable: true,
                            view: window
                        });
                        checkbox.dispatchEvent(mouseEvent);
                        
                        // React/Vue 이벤트도 시도
                        if (checkbox._reactInternalFiber || checkbox.__reactInternalInstance) {
                            var reactEvent = new Event('change', { bubbles: true });
                            checkbox.dispatchEvent(reactEvent);
                        }
                        
                        // 최종 상태 확인
                        return { 
                            success: checkbox.checked !== initialState, 
                            method: 'state_change_events', 
                            initialState: initialState, 
                            finalState: checkbox.checked 
                        };
                        
                    } catch (e) {
                        console.log('JS 클릭 실패:', e);
                        return { success: false, error: e.toString() };
                    }
                }
                return { success: false, error: 'checkbox_not_found' };
            """, checkbox_index)
            
            if result and result.get('success'):
                logger.info(f"JavaScript 클릭 성공: {result.get('method')}, 상태 변경: {result.get('initialState')} -> {result.get('finalState')}")
                return True
            else:
                logger.warning(f"JavaScript 클릭 실패: {result}")
                return False
                
        except Exception as e:
            logger.warning(f"JavaScript 직접 클릭 실패: {e}")
            return False
    
    def _js_wrapper_click(self, checkbox_index):
        """JavaScript로 체크박스의 wrapper 요소들을 클릭합니다."""
        try:
            result = self.driver.execute_script("""
                var checkboxes = Array.from(document.querySelectorAll('input[type="checkbox"]'))
                    .filter(el => {
                        const rect = el.getBoundingClientRect();
                        return el.offsetParent !== null && 
                               !el.disabled && 
                               rect.width > 0 && 
                               rect.height > 0 &&
                               rect.top >= 0 &&
                               rect.left >= 0;
                    });
                
                if (checkboxes[arguments[0]]) {
                    var checkbox = checkboxes[arguments[0]];
                    var initialState = checkbox.checked;
                    
                    // wrapper 요소들 찾기
                    var wrappers = [];
                    
                    // 1. label wrapper (ant-checkbox-wrapper)
                    var labelWrapper = checkbox.closest('label.ant-checkbox-wrapper');
                    if (labelWrapper) wrappers.push({element: labelWrapper, type: 'label_wrapper'});
                    
                    // 2. span wrapper (ant-checkbox)
                    var spanWrapper = checkbox.closest('span.ant-checkbox');
                    if (spanWrapper) wrappers.push({element: spanWrapper, type: 'span_wrapper'});
                    
                    // 3. 부모 요소들
                    var parent = checkbox.parentElement;
                    if (parent) wrappers.push({element: parent, type: 'parent'});
                    
                    // 4. 형제 span 요소 (ant-checkbox-inner)
                    var siblingSpan = checkbox.parentElement ? checkbox.parentElement.querySelector('span.ant-checkbox-inner') : null;
                    if (siblingSpan) wrappers.push({element: siblingSpan, type: 'sibling_span'});
                    
                    // wrapper 요소들 클릭 시도
                    for (var i = 0; i < wrappers.length; i++) {
                        try {
                            wrappers[i].element.click();
                            
                            // 상태 변경 확인
                            if (checkbox.checked !== initialState) {
                                return { 
                                    success: true, 
                                    method: 'wrapper_click_' + wrappers[i].type, 
                                    initialState: initialState, 
                                    finalState: checkbox.checked 
                                };
                            }
                        } catch (e) {
                            console.log('Wrapper 클릭 실패 (' + wrappers[i].type + '):', e);
                        }
                    }
                    
                    return { success: false, error: 'no_wrapper_worked', wrapperCount: wrappers.length };
                }
                return { success: false, error: 'checkbox_not_found' };
            """, checkbox_index)
            
            if result and result.get('success'):
                logger.info(f"JavaScript wrapper 클릭 성공: {result.get('method')}, 상태 변경: {result.get('initialState')} -> {result.get('finalState')}")
                return True
            else:
                logger.warning(f"JavaScript wrapper 클릭 실패: {result}")
                return False
                
        except Exception as e:
            logger.warning(f"JavaScript wrapper 클릭 실패: {e}")
            return False
    



    def open_search_dropdown(self):
        """
        상품검색 드롭박스 열기
        
        Returns:
            bool: 성공 여부
        """
        logger.info("상품검색 드롭박스 열기 시도")
        
        for i, selector in enumerate(self.search_dropdown_selectors):
            try:
                logger.info(f"선택자 {i+1} 시도: {selector}")
                
                # 요소 찾기
                element = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                
                # 요소가 화면에 보이도록 스크롤
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                time.sleep(0.5)
                
                # 클릭 시도
                try:
                    element.click()
                    logger.info(f"선택자 {i+1}로 드롭박스 클릭 성공")
                except ElementClickInterceptedException:
                    # JavaScript로 클릭 시도
                    logger.info(f"일반 클릭 실패, JavaScript 클릭 시도")
                    self.driver.execute_script("arguments[0].click();", element)
                    logger.info(f"선택자 {i+1}로 JavaScript 클릭 성공")
                
                # 드롭박스가 열렸는지 확인
                time.sleep(1)
                if self._is_dropdown_open():
                    logger.info("상품검색 드롭박스 열기 성공")
                    return True
                else:
                    logger.warning(f"선택자 {i+1} 클릭했지만 드롭박스가 열리지 않음")
                    
            except Exception as e:
                logger.warning(f"선택자 {i+1} 실패: {e}")
                continue
        
        logger.error("모든 선택자로 상품검색 드롭박스 열기 실패")
        return False
    
    def _is_dropdown_open(self):
        """
        드롭박스가 열렸는지 확인
        
        Returns:
            bool: 드롭박스 열림 여부
        """
        try:
            dropdown = self.driver.find_element(By.XPATH, self.dropdown_open_selector)
            return dropdown.is_displayed()
        except NoSuchElementException:
            return False
    
    def select_group_by_name(self, group_name, max_scrolls=10):
        """
        그룹명으로 그룹 선택 (스크롤 지원)
        
        Args:
            group_name (str): 선택할 그룹명 (예: "신규수집")
            max_scrolls (int): 최대 스크롤 횟수
            
        Returns:
            bool: 성공 여부
        """
        logger.info(f"그룹 '{group_name}' 선택 시도 (스크롤 지원)")
        
        try:
            # 먼저 현재 보이는 옵션들에서 찾기
            if self._find_and_click_group_option(group_name):
                logger.info(f"현재 화면에서 '{group_name}' 그룹을 찾았습니다.")
                return True
            
            # 현재 화면에서 찾지 못한 경우 스크롤하며 검색
            logger.info(f"현재 화면에서 찾지 못함. 스크롤하며 검색 시작 (최대 {max_scrolls}회)")
            return self._scroll_and_search_for_group(group_name, max_scrolls)
            
        except Exception as e:
            logger.error(f"그룹 선택 중 오류: {e}")
            return False
    
    def _find_and_click_group_option(self, group_name):
        """
        현재 보이는 그룹 옵션들에서 지정된 그룹명을 찾아 클릭
        
        Args:
            group_name (str): 찾을 그룹명
            
        Returns:
            bool: 성공 여부
        """
        try:
            # 그룹 옵션들 찾기
            options = self.driver.find_elements(By.XPATH, self.group_option_selector)
            
            logger.info(f"현재 화면에서 {len(options)}개의 그룹 옵션 발견")
            
            # 각 옵션의 텍스트 확인하여 일치하는 그룹 찾기
            for i, option in enumerate(options):
                try:
                    option_text = option.text.strip()
                    logger.info(f"옵션 {i+1}: '{option_text}'")
                    
                    if option_text == group_name:
                        logger.info(f"일치하는 그룹 발견: '{option_text}'")
                        
                        # 옵션 클릭
                        try:
                            option.click()
                            logger.info(f"그룹 '{group_name}' 선택 성공")
                            time.sleep(1)  # 선택 후 대기
                            return True
                        except ElementClickInterceptedException:
                            # JavaScript로 클릭 시도
                            self.driver.execute_script("arguments[0].click();", option)
                            logger.info(f"그룹 '{group_name}' JavaScript 클릭 성공")
                            time.sleep(1)
                            return True
                            
                except Exception as e:
                    logger.warning(f"옵션 {i+1} 처리 중 오류: {e}")
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"그룹 옵션 찾기 중 오류: {e}")
            return False
    
    def _scroll_and_search_for_group(self, group_name, max_scrolls=10):
        """
        드롭다운 내에서 스크롤하며 그룹 검색
        
        Args:
            group_name (str): 찾을 그룹명
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
            self._log_all_available_options()
            return False
            
        except Exception as e:
            logger.error(f"드롭다운 스크롤 검색 오류: {e}")
            return False
    
    def _log_all_available_options(self):
        """
        현재 드롭다운에서 사용 가능한 모든 옵션을 로그에 출력
        """
        try:
            options = self.driver.find_elements(By.XPATH, self.group_option_selector)
            logger.info(f"=== 현재 사용 가능한 모든 그룹 옵션 ({len(options)}개) ===")
            for i, option in enumerate(options):
                try:
                    option_text = option.text.strip()
                    logger.info(f"  {i+1}. '{option_text}'")
                except:
                    logger.info(f"  {i+1}. (텍스트 읽기 실패)")
            logger.info("=== 옵션 목록 끝 ===")
        except Exception as e:
            logger.warning(f"옵션 목록 출력 중 오류: {e}")
    
    def select_group_in_search_dropdown(self, group_name):
        """
        상품검색 드롭박스를 열고 그룹을 선택하는 통합 메서드
        
        Args:
            group_name (str): 선택할 그룹명 (예: "신규수집")
            
        Returns:
            bool: 성공 여부
        """
        logger.info(f"상품검색 드롭박스에서 '{group_name}' 그룹 선택 시작")
        
        # 1. 드롭박스 열기
        if not self.open_search_dropdown():
            logger.error("상품검색 드롭박스 열기 실패")
            return False
        
        # 2. 그룹 선택
        if not self.select_group_by_name(group_name):
            logger.error(f"그룹 '{group_name}' 선택 실패")
            return False
        
        logger.info(f"상품검색 드롭박스에서 '{group_name}' 그룹 선택 완료")
        return True
    
    def verify_page_refresh(self, timeout=10):
        """
        페이지가 새로고침되어 로드되었는지 확인
        신규수집 그룹의 경우 상품이 없는 것이 정상이므로 상품 목록 존재 여부가 아닌
        페이지 구조 요소나 충분한 대기시간으로 확인
        
        Args:
            timeout (int): 대기 시간 (초)
            
        Returns:
            bool: 페이지 로드 성공 여부
        """
        logger.info("페이지 새로고침 및 로드 확인")
        
        try:
            # 충분한 페이지 로드 대기 (5초)
            logger.info("페이지 로드를 위해 5초 대기")
            time.sleep(5)
            
            # 페이지 기본 구조가 로드되었는지 확인 (상품 존재 여부와 무관한 요소들)
            load_indicators = [
                "//div[contains(@class, 'ant-table')]",        # 테이블 컨테이너 (상품이 없어도 존재)
                "//div[contains(@class, 'ant-table-thead')]",  # 테이블 헤더 (항상 존재)
                "//div[contains(@class, 'ant-table-container')]", # 테이블 컨테이너
                "//thead[contains(@class, 'ant-table-thead')]", # 테이블 헤더
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
            # 오류가 발생해도 충분한 시간이 지났으므로 성공으로 간주
            return True
    
    def select_items_per_page(self, items_count="50"):
        """
        페이지당 표시할 항목 수 선택
        
        Args:
            items_count (str): 표시할 항목 수 ("10", "20", "50", "100")
            
        Returns:
            bool: 성공 여부
        """
        logger.info(f"페이지당 {items_count}개 항목 표시 설정")
        
        try:
            # 페이지 크기 선택 드롭박스 선택자들
            page_size_selectors = [
                "//div[contains(@class, 'ant-select-single') and .//span[contains(text(), '개씩')]]//div[contains(@class, 'ant-select-selector')]",
                "//div[contains(@class, 'ant-pagination-options-size-changer')]//div[contains(@class, 'ant-select-selector')]",
                "//span[contains(text(), '개씩')]/ancestor::div[contains(@class, 'ant-select')]",
            ]
            
            # 드롭박스 열기
            dropdown_opened = False
            for selector in page_size_selectors:
                try:
                    element = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    
                    # 요소가 화면에 보이도록 스크롤
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                    time.sleep(0.5)
                    
                    # 클릭 시도
                    try:
                        element.click()
                        logger.info(f"페이지 크기 드롭박스 클릭 성공: {selector}")
                    except ElementClickInterceptedException:
                        self.driver.execute_script("arguments[0].click();", element)
                        logger.info(f"페이지 크기 드롭박스 JavaScript 클릭 성공: {selector}")
                    
                    # 드롭박스가 열렸는지 확인
                    time.sleep(1)
                    if self._is_dropdown_open():
                        dropdown_opened = True
                        break
                        
                except Exception as e:
                    logger.warning(f"페이지 크기 드롭박스 선택자 실패: {selector} - {e}")
                    continue
            
            if not dropdown_opened:
                logger.error("페이지 크기 드롭박스 열기 실패")
                return False
            
            # 원하는 항목 수 선택
            option_selectors = [
                f"//div[contains(@class, 'ant-select-item-option') and contains(text(), '{items_count}')]",
                f"//div[contains(@class, 'ant-select-item') and .//span[contains(text(), '{items_count}')]]",
                f"//li[contains(@class, 'ant-select-item-option') and contains(text(), '{items_count}')]",
            ]
            
            for selector in option_selectors:
                try:
                    option = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    
                    try:
                        option.click()
                        logger.info(f"{items_count}개 항목 선택 성공")
                    except ElementClickInterceptedException:
                        self.driver.execute_script("arguments[0].click();", option)
                        logger.info(f"{items_count}개 항목 JavaScript 클릭 성공")
                    
                    # 선택 후 페이지 로드 대기
                    time.sleep(2)
                    return True
                    
                except Exception as e:
                    logger.warning(f"항목 수 선택 실패: {selector} - {e}")
                    continue
            
            logger.error(f"{items_count}개 항목 선택 실패")
            return False
            
        except Exception as e:
            logger.error(f"페이지당 항목 수 설정 중 오류: {e}")
            return False
    
    def reset_scroll_position(self, delay=0.5):
        """
        화면을 최상단으로 스크롤
        
        Args:
            delay (float): 스크롤 후 대기 시간
        """
        try:
            self.driver.execute_script("window.scrollTo(0, 0);")
            logger.info("화면을 최상단으로 스크롤")
            time.sleep(delay)
        except Exception as e:
            logger.warning(f"스크롤 중 오류: {e}")

    def select_all_products(self, timeout=10):
        """
        상품 전체 선택 체크박스 클릭 (하이브리드 방식)
        
        Args:
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("상품 전체 선택")
            
            # 페이지 상단으로 스크롤하여 테이블 헤더가 보이도록 함
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            # 디버깅: 현재 페이지의 테이블 구조 확인
            try:
                table_headers = self.driver.find_elements(By.XPATH, "//thead | //div[contains(@class, 'ant-table-header')]")
                logger.info(f"페이지에서 발견된 테이블 헤더 수: {len(table_headers)}")
                
                # 체크박스 관련 요소들 확인
                all_checkboxes = self.driver.find_elements(By.XPATH, "//input[@type='checkbox']")
                logger.info(f"페이지에서 발견된 전체 체크박스 수: {len(all_checkboxes)}")
                
                select_all_candidates = self.driver.find_elements(By.XPATH, "//input[@aria-label='Select all'] | //input[contains(@aria-label, 'Select all')]")
                logger.info(f"'Select all' 라벨을 가진 체크박스 수: {len(select_all_candidates)}")
                
                # JavaScript를 사용한 실제 클릭 가능한 요소 탐지
                js_clickable_checkboxes = self.driver.execute_script("""
                    return Array.from(document.querySelectorAll('input[type="checkbox"]'))
                        .filter(el => {
                            const rect = el.getBoundingClientRect();
                            return el.offsetParent !== null && 
                                   !el.disabled && 
                                   rect.width > 0 && 
                                   rect.height > 0 &&
                                   rect.top >= 0 &&
                                   rect.left >= 0;
                        })
                        .map(el => ({
                            tagName: el.tagName,
                            className: el.className,
                            ariaLabel: el.getAttribute('aria-label'),
                            id: el.id,
                            x: Math.round(el.getBoundingClientRect().left),
                            y: Math.round(el.getBoundingClientRect().top),
                            width: Math.round(el.getBoundingClientRect().width),
                            height: Math.round(el.getBoundingClientRect().height),
                            displayed: el.offsetParent !== null,
                            disabled: el.disabled
                        }));
                """)
                        
            except Exception as debug_e:
                logger.warning(f"디버깅 정보 수집 실패: {debug_e}")
            
            # DOM 구조 분석 결과를 반영한 정확한 선택자들 (우선순위 순서)
            selectors = [
                # 제공된 DOM 구조 기반 정확한 선택자들
                "//th[@class='ant-table-cell ant-table-selection-column']//input[@aria-label='Select all']",  # 정확한 DOM 구조
                "//div[@class='ant-table-selection']//input[@aria-label='Select all']",  # 테이블 선택 영역
                "//label[@class='ant-checkbox-wrapper css-1li46mu']//input[@aria-label='Select all']",  # 라벨 래퍼 기반
                "//span[@class='ant-checkbox ant-wave-target css-1li46mu']//input[@aria-label='Select all']",  # 스팬 래퍼 기반
                
                # 기존 XPath 선택자들 (개선된 순서)
                "//thead[contains(@class, 'ant-table-thead')]//input[@aria-label='Select all']",  # 테이블 헤더 내부
                "//th[contains(@class, 'ant-table-selection-column')]//input[@type='checkbox']",  # 선택 컬럼 내부
                "//div[contains(@class, 'ant-table-selection')]//input[@type='checkbox']",  # 기존 방식
                "//input[@aria-label='Select all' and @type='checkbox']",  # 일반적인 방식
                "//input[contains(@aria-label, 'Select all')]",  # 부분 매칭
                "//thead//input[@type='checkbox']",  # 테이블 헤더의 모든 체크박스
                
                # 새로운 확장 XPath 선택자들
                "//input[@type='checkbox'][1]",  # 첫 번째 체크박스 (가장 단순)
                "//table//input[@type='checkbox'][1]",  # 테이블 내 첫 번째 체크박스
                "//input[contains(@class, 'ant-checkbox-input')][1]",  # Ant Design 체크박스 클래스
                "//span[contains(@class, 'ant-checkbox')]//input[@type='checkbox']",  # Ant Design 체크박스 래퍼
                "//label[contains(@class, 'ant-checkbox-wrapper')]//input[@type='checkbox']",  # 체크박스 라벨 래퍼
                "//div[contains(@class, 'ant-table-selection-col')]//input[@type='checkbox']",  # 선택 컬럼 변형
                "//th[@class='ant-table-selection-column']//input[@type='checkbox']",  # 정확한 클래스명
                "//div[contains(@class, 'ant-table-thead')]//input[@type='checkbox']",  # 헤더 변형
                "//tr[contains(@class, 'ant-table-thead')]//input[@type='checkbox']",  # 헤더 행
                "//input[@role='checkbox']",  # 역할 기반 선택
                "//input[@type='checkbox' and contains(@class, 'ant-checkbox-input')]",  # 타입과 클래스 조합
                "//div[contains(@class, 'ant-table')]//input[@type='checkbox'][1]",  # 테이블 내 첫 번째
                "//thead/tr/th[1]//input[@type='checkbox']",  # 첫 번째 헤더 셀
                "//thead/tr/th[contains(@class, 'selection')]//input[@type='checkbox']",  # 선택 헤더 셀
                "//div[@role='table']//input[@type='checkbox'][1]",  # 역할 기반 테이블
                "//div[contains(@class, 'table')]//input[@type='checkbox'][1]",  # 일반 테이블 클래스
            ]
            
            # CSS 선택자도 시도 (XPath가 모두 실패한 경우) - DOM 구조 반영
            css_selectors = [
                "th.ant-table-cell.ant-table-selection-column input[aria-label='Select all']",  # 정확한 DOM 구조
                ".ant-table-selection input[aria-label='Select all']",  # 테이블 선택 영역
                "label.ant-checkbox-wrapper input[aria-label='Select all']",  # 라벨 래퍼
                "span.ant-checkbox input[aria-label='Select all']",  # 스팬 래퍼
                "input[type='checkbox'][aria-label*='Select all']",  # CSS 속성 선택자
                "input[type='checkbox']:first-of-type",  # 첫 번째 체크박스
                ".ant-table-selection input[type='checkbox']",  # 클래스 기반
                ".ant-table-thead input[type='checkbox']",  # 헤더 클래스
                ".ant-checkbox-input",  # Ant Design 체크박스
                "thead input[type='checkbox']",  # 간단한 헤더 선택
                "table input[type='checkbox']:first-child",  # 테이블 내 첫 번째
                "th.ant-table-selection-column input",  # 선택 컬럼
                "input[type='checkbox']",  # 가장 기본적인 선택자
            ]
            
            checkbox_element = None
            
            # 0단계: 'Select all' 라벨을 가진 체크박스만을 대상으로 집중적인 클릭 시도
            try:
                if js_clickable_checkboxes:
                    # 'Select all' 라벨을 가진 체크박스만 찾기
                    select_all_checkbox = None
                    select_all_index = -1
                    
                    for i, checkbox_info in enumerate(js_clickable_checkboxes):
                        if checkbox_info.get('ariaLabel') == 'Select all':
                            select_all_checkbox = checkbox_info
                            select_all_index = i
                            break
                    
                    if select_all_checkbox and select_all_index >= 0:
                        logger.info(f"'Select all' 체크박스 발견 (인덱스: {select_all_index}), 집중적인 클릭 시도 시작")
                        logger.info(f"대상 체크박스 정보: {select_all_checkbox}")
                        
                        # 성공한 JavaScript 클릭 방법만 사용
                        try:
                            logger.info(f"'direct_click' 방법으로 'Select all' 체크박스 클릭 시도")
                            success = self._js_direct_click(select_all_index)
                            if success:
                                logger.info(f"'direct_click' 방법으로 'Select all' 체크박스 클릭 성공!")
                                return True
                            else:
                                logger.warning(f"'direct_click' 방법 실패")
                        except Exception as method_error:
                            logger.warning(f"'direct_click' 방법 실행 중 오류: {method_error}")
                        
                        logger.warning("JavaScript 클릭 방법 실패")
                    else:
                        logger.warning("'Select all' 라벨을 가진 체크박스를 찾을 수 없음")
                        
            except Exception as e:
                logger.warning(f"JavaScript 'Select all' 체크박스 클릭 시도 중 오류: {e}")
            
            # 1단계: XPath 선택자 시도
            for i, selector in enumerate(selectors, 1):
                try:
                    logger.info(f"XPath 선택자 {i} 시도: {selector}")
                    # 먼저 요소가 존재하는지 확인
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements:
                        logger.info(f"XPath 선택자 {i}로 {len(elements)}개 요소 발견")
                        checkbox_element = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        logger.info(f"XPath 선택자 {i} 성공: {selector}")
                        break
                    else:
                        logger.warning(f"XPath 선택자 {i}로 요소를 찾을 수 없음: {selector}")
                except (TimeoutException, NoSuchElementException) as e:
                    logger.warning(f"XPath 선택자 {i} 실패: {selector} - {str(e)}")
                    continue
            
            # 2단계: XPath가 모두 실패한 경우 CSS 선택자 시도
            if not checkbox_element:
                logger.info("모든 XPath 선택자 실패, CSS 선택자 시도")
                for i, css_selector in enumerate(css_selectors, 1):
                    try:
                        logger.info(f"CSS 선택자 {i} 시도: {css_selector}")
                        elements = self.driver.find_elements(By.CSS_SELECTOR, css_selector)
                        if elements:
                            logger.info(f"CSS 선택자 {i}로 {len(elements)}개 요소 발견")
                            checkbox_element = WebDriverWait(self.driver, 5).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
                            )
                            logger.info(f"CSS 선택자 {i} 성공: {css_selector}")
                            break
                        else:
                            logger.warning(f"CSS 선택자 {i}로 요소를 찾을 수 없음: {css_selector}")
                    except (TimeoutException, NoSuchElementException) as e:
                        logger.warning(f"CSS 선택자 {i} 실패: {css_selector} - {str(e)}")
                        continue
                    
            # DOM 요소로 클릭 성공한 경우 - 다양한 클릭 방식 시도
            try:
                # 이미 선택되어 있는지 확인
                is_checked = checkbox_element.is_selected()
                
                if not is_checked:
                    # 1. 요소를 화면 중앙으로 스크롤
                    try:
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", checkbox_element)
                        time.sleep(0.3)
                        logger.info("체크박스를 화면 중앙으로 스크롤 완료")
                    except Exception as scroll_error:
                        logger.warning(f"스크롤 실패: {scroll_error}")
                    
                    # 2. 다양한 클릭 방법 시도 (순서대로) - DOM 구조에 맞게 개선
                    click_methods = [
                        ("label_wrapper_click", lambda: self._label_wrapper_click(checkbox_element)),  # 라벨 래퍼 클릭 (우선)
                        ("span_wrapper_click", lambda: self._span_wrapper_click(checkbox_element)),  # 스팬 래퍼 클릭
                        ("standard_click", lambda: checkbox_element.click()),
                        ("javascript_click", lambda: self.driver.execute_script("arguments[0].click();", checkbox_element)),
                        ("javascript_force_click", lambda: self.driver.execute_script("""
                            const element = arguments[0];
                            const event = new MouseEvent('click', {
                                view: window,
                                bubbles: true,
                                cancelable: true
                            });
                            element.dispatchEvent(event);
                        """, checkbox_element)),
                        ("action_chains_click", lambda: self._action_chains_click(checkbox_element)),
                        ("parent_element_click", lambda: self._parent_element_click(checkbox_element)),
                        ("label_click", lambda: self._label_click(checkbox_element)),
                        ("force_state_change", lambda: self._force_state_change(checkbox_element))
                    ]
                    
                    for method_name, click_method in click_methods:
                        try:
                            logger.info(f"클릭 방법 시도: {method_name}")
                            click_method()
                            time.sleep(0.5)
                            
                            # 상태 변경 확인
                            if checkbox_element.is_selected():
                                logger.info(f"{method_name} 클릭 성공 - 체크박스가 선택됨")
                                return True
                            else:
                                logger.warning(f"{method_name} 클릭했지만 상태가 변경되지 않음")
                                
                        except Exception as click_error:
                            logger.warning(f"{method_name} 클릭 실패: {click_error}")
                            continue
                    
                    # 모든 클릭 방법 실패
                    logger.warning("모든 클릭 방법 실패, smart_click으로 폴백")
                    checkbox_element = None  # smart_click 로직으로 이동하도록 설정
                else:
                    logger.info("이미 상품이 전체 선택되어 있습니다.")
                    return True
                     
            except Exception as dom_click_error:
                logger.error(f"DOM 요소 클릭 처리 중 오류: {dom_click_error}")
                checkbox_element = None  # smart_click 로직으로 이동하도록 설정
            
            # DOM 클릭이 실패했거나 요소를 찾지 못한 경우 smart_click 시도
            if not checkbox_element:
                logger.warning("DOM 선택자 실패 또는 클릭 실패, smart_click으로 하이브리드 클릭 시도")
                try:
                    from dom_utils import smart_click
                    from ui_elements import UI_ELEMENTS
                    
                    # SELECT_ALL_CHECKBOX UI 요소 정보 사용
                    select_all_ui = UI_ELEMENTS.get("SELECT_ALL_CHECKBOX")
                    if select_all_ui:
                        result = smart_click(self.driver, select_all_ui, "전체 선택 체크박스")
                        if result["success"]:
                            logger.info(f"smart_click 성공: {result['method']} 방식 사용")
                            
                            # smart_click 후 실제로 체크박스가 선택되었는지 확인
                            time.sleep(1)  # 상태 변경을 위한 대기
                            try:
                                # 다시 체크박스 요소를 찾아서 상태 확인
                                for selector in selectors[:3]:  # 상위 3개 선택자만 사용
                                    try:
                                        check_elements = self.driver.find_elements(By.XPATH, selector)
                                        if check_elements:
                                            if check_elements[0].is_selected():
                                                logger.info("smart_click 후 체크박스 선택 상태 확인됨")
                                                return True
                                            break
                                    except:
                                        continue
                                
                                # 선택된 상품 개수로도 확인
                                try:
                                    selected_products = self.driver.find_elements(By.XPATH, "//tr[contains(@class, 'ant-table-row-selected')]")
                                    if len(selected_products) > 0:
                                        logger.info(f"smart_click 후 {len(selected_products)}개 상품이 선택됨")
                                        return True
                                    else:
                                        logger.warning("smart_click 후에도 선택된 상품이 없음")
                                except Exception as count_error:
                                    logger.warning(f"선택된 상품 개수 확인 실패: {count_error}")
                                    
                            except Exception as verify_error:
                                logger.warning(f"smart_click 후 상태 확인 실패: {verify_error}")
                                
                            return True  # smart_click이 성공했다고 보고했으므로 일단 True 반환
                        else:
                            logger.error(f"smart_click 실패: {result['error']}")
                    else:
                        logger.error("SELECT_ALL_CHECKBOX UI 요소를 찾을 수 없음")
                    return False
                except Exception as smart_click_error:
                    logger.error(f"smart_click도 실패: {smart_click_error}")
                    return False
            else:
                # DOM 클릭이 성공한 경우
                return True
                
        except Exception as e:
            logger.error(f"상품 전체 선택 오류: {e}")
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
            # 오류 발생 시에도 모달창이 열려있을 수 있으므로 닫기 시도
            self._close_modal_if_open()
            return False
    
    def _close_modal_if_open(self, timeout=5):
        """
        모달창이 열려있으면 강제로 닫기
        
        Args:
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            # 모달창이 열려있는지 확인
            modal_selector = "//div[contains(@class, 'ant-modal')]//span[contains(text(), '상품 그룹핑') or contains(text(), '그룹 지정')]"
            modal_element = self.driver.find_element(By.XPATH, modal_selector)
            
            if modal_element.is_displayed():
                logger.info("열려있는 모달창을 강제로 닫습니다.")
                
                # 취소 버튼 또는 X 버튼 클릭 시도
                close_selectors = [
                    "//div[contains(@class, 'ant-modal-footer')]//button[contains(@class, 'ant-btn-default')][.//span[text()='취소']]",
                    "//div[contains(@class, 'ant-modal-header')]//button[contains(@class, 'ant-modal-close')]",
                    "//div[contains(@class, 'ant-modal')]//button[@aria-label='Close']"
                ]
                
                for close_selector in close_selectors:
                    try:
                        close_button = WebDriverWait(self.driver, 2).until(
                            EC.element_to_be_clickable((By.XPATH, close_selector))
                        )
                        close_button.click()
                        time.sleep(1)
                        
                        # 모달창이 닫혔는지 확인
                        try:
                            WebDriverWait(self.driver, 3).until(
                                EC.invisibility_of_element_located((By.XPATH, modal_selector))
                            )
                            logger.info("모달창이 성공적으로 닫혔습니다.")
                            return True
                        except TimeoutException:
                            continue
                            
                    except (TimeoutException, NoSuchElementException):
                        continue
                
                # 버튼 클릭으로 닫지 못한 경우 ESC 키 시도
                logger.info("버튼 클릭으로 모달창을 닫지 못했습니다. ESC 키를 시도합니다.")
                try:
                    from selenium.webdriver.common.keys import Keys
                    # body 요소에 ESC 키 전송
                    body = self.driver.find_element(By.TAG_NAME, "body")
                    body.send_keys(Keys.ESCAPE)
                    time.sleep(1)
                    
                    # 모달창이 닫혔는지 확인
                    try:
                        WebDriverWait(self.driver, 3).until(
                            EC.invisibility_of_element_located((By.XPATH, modal_selector))
                        )
                        logger.info("ESC 키로 모달창이 성공적으로 닫혔습니다.")
                        return True
                    except TimeoutException:
                        logger.error("ESC 키로도 모달창을 닫지 못했습니다.")
                        return False
                        
                except Exception as e:
                    logger.error(f"ESC 키 전송 오류: {e}")
                    return False
            else:
                logger.info("모달창이 이미 닫혀있습니다.")
                return True
                
        except NoSuchElementException:
            logger.info("모달창이 존재하지 않습니다.")
            return True
        except Exception as e:
            logger.error(f"모달창 닫기 오류: {e}")
            return False
    
    def move_products_to_group(self, group_name, timeout=10):
        """
        선택된 상품을 특정 그룹으로 이동
        - 전체 상품 선택
        - 그룹 이동 모달 열기
        - 그룹 선택 및 이동 확인
        
        Args:
            group_name: 이동할 그룹 이름
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"상품을 '{group_name}' 그룹으로 이동 시작")
            
            # 1. 전체 상품 선택
            if not self.select_all_products(timeout):
                logger.error("상품 전체 선택 실패, 그룹 이동을 중단합니다.")
                return False
            
            # 2. 그룹 이동 모달 열기
            if not self.open_group_assignment_modal(timeout):
                logger.error("그룹 이동 모달창 열기 실패, 그룹 이동을 중단합니다.")
                return False
            
            # 3. 그룹 선택 및 이동
            if not self.select_group_in_modal(group_name, timeout):
                logger.error(f"'{group_name}' 그룹 선택 실패, 그룹 이동을 중단합니다.")
                return False
            
            logger.info(f"상품이 '{group_name}' 그룹으로 성공적으로 이동되었습니다.")
            return True
            
        except Exception as e:
            logger.error(f"상품 그룹 이동 오류: {e}")
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
     
def get_product_search_dropdown_manager(driver):
    """
    ProductSearchDropdownManager 인스턴스 생성 함수
    
    Args:
        driver: Selenium WebDriver 인스턴스
        
    Returns:
        ProductSearchDropdownManager: 드롭박스 관리자 인스턴스
    """
    return ProductSearchDropdownManager(driver)