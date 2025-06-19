# -*- coding: utf-8 -*-
"""
퍼센티 플랫폼의 드롭박스 처리를 위한 유틸리티 모듈 (코어5 전용)

다양한 화면(등록상품관리, 그룹상품관리, 신규상품등록)에서 드롭박스를 통해
특정 그룹을 선택하거나 검색하는 기능을 제공합니다.
"""

import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

# 로깅 설정
logger = logging.getLogger(__name__)

# 대기 시간 설정
DELAY_VERY_SHORT = 0.5
DELAY_SHORT = 1
DELAY_MEDIUM = 2
DELAY_LONG = 3

# 하드코딩된 그룹 목록 (성능 최적화용)


class PercentyDropdown:
    """퍼센티 드롭박스 및 그룹 선택 처리를 위한 클래스 (코어5 전용)"""
    
    def __init__(self, driver):
        """
        드롭박스 및 그룹 선택 처리 클래스 초기화
        
        Args:
            driver: 셀레니움 웹드라이버 인스턴스
        """
        self.driver = driver
        logger.info("퍼센티 드롭박스 및 그룹 선택 유틸리티 초기화 (코어5 전용)")
    
    # =============================================================================
    # 상품 전체 선택 및 그룹 이동 메서드
    # =============================================================================
    
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
                        
                        # JavaScript 직접 클릭 시도
                        try:
                            logger.info(f"'direct_click' 방법으로 'Select all' 체크박스 클릭 시도")
                            success = self._js_direct_click(select_all_index)
                            if success:
                                logger.info(f"'direct_click' 방법으로 'Select all' 체크박스 클릭 성공!")
                                
                                # 실제 선택 확인: 그룹 지정 버튼이 활성화되었는지 확인
                                time.sleep(1)  # 상태 변경 대기
                                if self._verify_products_selected():
                                    logger.info("전체선택 성공: 상품이 실제로 선택되었습니다.")
                                    return True
                                else:
                                    logger.warning("전체선택 클릭했지만 상품이 실제로 선택되지 않았습니다. 다른 방법 시도")
                            else:
                                logger.warning(f"'direct_click' 방법 실패")
                        except Exception as method_error:
                            logger.warning(f"'direct_click' 방법 실행 중 오류: {method_error}")
                        
                        logger.warning("JavaScript 클릭 방법 실패")
                    else:
                        logger.warning("'Select all' 라벨을 가진 체크박스를 찾을 수 없음")
                        
            except Exception as e:
                logger.warning(f"JavaScript 'Select all' 체크박스 클릭 시도 중 오류: {e}")
            
            # 1단계: 확장된 XPath 선택자 시도 (디버깅을 위해 첫 번째만 활성화)
            selectors = [
                # 정확한 DOM 구조 기반 선택자들
                "//th[@class='ant-table-cell ant-table-selection-column']//input[@aria-label='Select all']",
                # 디버깅을 위해 나머지 선택자들 주석처리
                # "//div[@class='ant-table-selection']//input[@aria-label='Select all']",
                # "//label[@class='ant-checkbox-wrapper css-1li46mu']//input[@aria-label='Select all']",
                # "//span[@class='ant-checkbox ant-wave-target css-1li46mu']//input[@aria-label='Select all']",
                
                # 기존 선택자들 (개선된 순서) - 주석처리
                # "//thead[contains(@class, 'ant-table-thead')]//input[@aria-label='Select all']",
                # "//th[contains(@class, 'ant-table-selection-column')]//input[@type='checkbox']",
                # "//div[contains(@class, 'ant-table-selection')]//input[@type='checkbox']",
                # "//input[@aria-label='Select all' and @type='checkbox']",
                # "//input[contains(@aria-label, 'Select all')]",
                # "//thead//input[@type='checkbox']",
                
                # 확장 선택자들 - 주석처리
                # "//input[@type='checkbox'][1]",
                # "//table//input[@type='checkbox'][1]",
                # "//input[contains(@class, 'ant-checkbox-input')][1]",
                # "//span[contains(@class, 'ant-checkbox')]//input[@type='checkbox']",
                # "//label[contains(@class, 'ant-checkbox-wrapper')]//input[@type='checkbox']",
                # "//div[contains(@class, 'ant-table-selection-col')]//input[@type='checkbox']",
                # "//th[@class='ant-table-selection-column']//input[@type='checkbox']",
                # "//div[contains(@class, 'ant-table-thead')]//input[@type='checkbox']",
                # "//tr[contains(@class, 'ant-table-thead')]//input[@type='checkbox']",
                # "//input[@role='checkbox']",
                # "//input[@type='checkbox' and contains(@class, 'ant-checkbox-input')]",
                # "//div[contains(@class, 'ant-table')]//input[@type='checkbox'][1]",
                # "//thead/tr/th[1]//input[@type='checkbox']",
                # "//thead/tr/th[contains(@class, 'selection')]//input[@type='checkbox']",
                # "//div[@role='table']//input[@type='checkbox'][1]",
                # "//div[contains(@class, 'table')]//input[@type='checkbox'][1]",
                
                # 기존 선택자들 (호환성) - 주석처리
                # "//label[contains(@class, 'ant-checkbox-wrapper')]//span[contains(@class, 'ant-checkbox')]//input[@type='checkbox']",
                # "//th[contains(@class, 'ant-table-selection-column')]//span[contains(@class, 'ant-checkbox')]//input[@type='checkbox']",
                # "//div[contains(@class, 'ant-table-header')]//span[contains(@class, 'ant-checkbox')]//input[@type='checkbox']"
            ]
            
            checkbox_element = None
            
            # XPath 선택자 시도
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
            
            # 2단계: CSS 선택자 시도 (디버깅을 위해 주석처리)
            if not checkbox_element:
                logger.info("XPath 선택자 실패, CSS 선택자는 디버깅을 위해 비활성화됨")
                # css_selectors = [
                #     "th.ant-table-cell.ant-table-selection-column input[aria-label='Select all']",
                #     ".ant-table-selection input[aria-label='Select all']",
                #     "label.ant-checkbox-wrapper input[aria-label='Select all']",
                #     "span.ant-checkbox input[aria-label='Select all']",
                #     "input[type='checkbox'][aria-label*='Select all']",
                #     "input[type='checkbox']:first-of-type",
                #     ".ant-table-selection input[type='checkbox']",
                #     ".ant-table-thead input[type='checkbox']",
                #     ".ant-checkbox-input",
                #     "thead input[type='checkbox']",
                #     "table input[type='checkbox']:first-child",
                #     "th.ant-table-selection-column input",
                #     "input[type='checkbox']"
                # ]
                
                # CSS 선택자 루프 주석처리 (디버깅용)
                # for i, css_selector in enumerate(css_selectors, 1):
                #     try:
                #         logger.info(f"CSS 선택자 {i} 시도: {css_selector}")
                #         elements = self.driver.find_elements(By.CSS_SELECTOR, css_selector)
                #         if elements:
                #             logger.info(f"CSS 선택자 {i}로 {len(elements)}개 요소 발견")
                #             checkbox_element = WebDriverWait(self.driver, 5).until(
                #                 EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
                #             )
                #             logger.info(f"CSS 선택자 {i} 성공: {css_selector}")
                #             break
                #         else:
                #             logger.warning(f"CSS 선택자 {i}로 요소를 찾을 수 없음: {css_selector}")
                #     except (TimeoutException, NoSuchElementException) as e:
                #         logger.warning(f"CSS 선택자 {i} 실패: {css_selector} - {str(e)}")
                #         continue
                    
            # DOM 요소로 클릭 성공한 경우 - 다양한 클릭 방식 시도
            if checkbox_element:
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
                        
                        # 2. 다양한 클릭 방법 시도
                        click_methods = [
                            ("label_wrapper_click", lambda: self._label_wrapper_click(checkbox_element)),
                            ("span_wrapper_click", lambda: self._span_wrapper_click(checkbox_element)),
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
                            ("label_click", lambda: self._label_click(checkbox_element))
                        ]
                        
                        for method_name, click_method in click_methods:
                            try:
                                logger.info(f"클릭 방법 시도: {method_name}")
                                click_method()
                                time.sleep(0.5)
                                
                                # 상태 변경 확인
                                if checkbox_element.is_selected():
                                    logger.info(f"{method_name} 클릭 성공 - 체크박스가 선택됨")
                                    # 실제 상품 선택 확인
                                    if self._verify_products_selected():
                                        logger.info(f"{method_name} 성공: 상품이 실제로 선택되었습니다.")
                                        return True
                                    else:
                                        logger.warning(f"{method_name} 체크박스는 선택되었지만 상품이 실제로 선택되지 않았습니다.")
                                else:
                                    logger.warning(f"{method_name} 클릭했지만 상태가 변경되지 않음")
                                    
                            except Exception as click_error:
                                logger.warning(f"{method_name} 클릭 실패: {click_error}")
                                continue
                        
                        # 모든 클릭 방법 실패
                        logger.warning("모든 클릭 방법 실패")
                        
                    else:
                        logger.info("이미 상품이 전체 선택되어 있습니다.")
                        return True
                         
                except Exception as dom_click_error:
                    logger.error(f"DOM 요소 클릭 처리 중 오류: {dom_click_error}")
            
            # 모든 방법 실패 - 개별 상품 체크박스 직접 선택 시도
            logger.warning("전체 선택 체크박스 클릭이 모두 실패했습니다. 개별 상품 체크박스 직접 선택을 시도합니다.")
            return self._select_individual_products()
                
        except Exception as e:
            logger.error(f"상품 전체 선택 오류: {e}")
            return False
    
    def _js_direct_click(self, checkbox_index):
        """
        JavaScript를 사용한 직접 클릭 (안정적이고 검증된 핵심 체크박스 클릭 방법)
        'Select all' 및 Ant Design 체크박스에 대해 작동
        """
        try:
            result = self.driver.execute_script(f"""
                const checkboxes = Array.from(document.querySelectorAll('input[type="checkbox"]'))
                    .filter(el => {{
                        const rect = el.getBoundingClientRect();
                        return el.offsetParent !== null && 
                               !el.disabled && 
                               rect.width > 0 && 
                               rect.height > 0 &&
                               rect.top >= 0 &&
                               rect.left >= 0;
                    }});
                
                if (checkboxes.length > {checkbox_index}) {{
                    const checkbox = checkboxes[{checkbox_index}];
                    
                    // 클릭 이벤트 시뮬레이션
                    const clickEvent = new MouseEvent('click', {{
                        view: window,
                        bubbles: true,
                        cancelable: true,
                        clientX: checkbox.getBoundingClientRect().left + checkbox.getBoundingClientRect().width / 2,
                        clientY: checkbox.getBoundingClientRect().top + checkbox.getBoundingClientRect().height / 2
                    }});
                    
                    // 다양한 이벤트 디스패치
                    checkbox.dispatchEvent(new Event('focus', {{ bubbles: true }}));
                    checkbox.dispatchEvent(new MouseEvent('mousedown', {{ bubbles: true }}));
                    checkbox.dispatchEvent(clickEvent);
                    checkbox.dispatchEvent(new MouseEvent('mouseup', {{ bubbles: true }}));
                    checkbox.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    
                    return {{
                        success: true,
                        checked: checkbox.checked,
                        ariaLabel: checkbox.getAttribute('aria-label')
                    }};
                }} else {{
                    return {{
                        success: false,
                        error: 'Checkbox index out of range'
                    }};
                }}
            """)
            
            if result and result.get('success'):
                logger.info(f"JavaScript 직접 클릭 성공, 체크박스 상태: {result.get('checked')}")
                return True
            else:
                logger.warning(f"JavaScript 직접 클릭 실패: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            logger.error(f"JavaScript 직접 클릭 중 오류: {e}")
            return False
    
    def _verify_products_selected(self, timeout=3):
        """
        상품이 실제로 선택되었는지 확인 (그룹 지정 버튼 활성화 상태로 판단)
        
        Returns:
            bool: 상품이 선택되었으면 True, 아니면 False
        """
        try:
            # 그룹 지정 버튼이 활성화되었는지 확인
            group_assign_selectors = [
                "//button[contains(@class, 'ant-btn')][.//span[text()='그룹 지정']]",
                "//div[contains(@class, 'ant-btn-group')]//button[.//span[text()='그룹 지정']]",
                "//div[contains(@class, 'ant-flex')]//button[.//span[text()='그룹 지정']]"
            ]
            
            for selector in group_assign_selectors:
                try:
                    button_elements = self.driver.find_elements(By.XPATH, selector)
                    for button in button_elements:
                        if button.is_displayed():
                            is_disabled = button.get_attribute("disabled")
                            if not is_disabled:  # disabled 속성이 없으면 활성화된 것
                                logger.info("그룹 지정 버튼이 활성화되어 있음 - 상품이 선택된 상태")
                                return True
                            else:
                                logger.info("그룹 지정 버튼이 비활성화되어 있음 - 상품이 선택되지 않은 상태")
                                return False
                except Exception:
                    continue
            
            # 대안: 개별 상품 체크박스가 선택되었는지 확인
            try:
                selected_checkboxes = self.driver.execute_script("""
                    return Array.from(document.querySelectorAll('input[type="checkbox"]'))
                        .filter(cb => cb.checked && cb.getAttribute('aria-label') !== 'Select all')
                        .length;
                """)
                
                if selected_checkboxes > 0:
                    logger.info(f"개별 상품 체크박스 {selected_checkboxes}개가 선택됨")
                    return True
                else:
                    logger.info("선택된 개별 상품 체크박스가 없음")
                    return False
                    
            except Exception as js_error:
                logger.warning(f"JavaScript로 체크박스 상태 확인 실패: {js_error}")
                return False
                
        except Exception as e:
             logger.error(f"상품 선택 상태 확인 중 오류: {e}")
             return False
    
    def _select_individual_products(self, timeout=10):
        """
        개별 상품 체크박스를 직접 선택하는 대안 방법
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("개별 상품 체크박스 직접 선택 시작")
            
            # 개별 상품 체크박스 찾기 (Select all 제외)
            individual_checkbox_selectors = [
                # 테이블 본문의 개별 상품 체크박스
                "//tbody[contains(@class, 'ant-table-tbody')]//input[@type='checkbox']",
                "//tr[contains(@class, 'ant-table-row')]//input[@type='checkbox']",
                "//td[contains(@class, 'ant-table-selection-column')]//input[@type='checkbox']",
                # 더 구체적인 선택자
                "//div[contains(@class, 'ant-table-body')]//input[@type='checkbox'][not(@aria-label='Select all')]",
                "//input[@type='checkbox'][not(@aria-label='Select all')][not(ancestor::thead)]"
            ]
            
            selected_count = 0
            
            for selector in individual_checkbox_selectors:
                try:
                    checkboxes = self.driver.find_elements(By.XPATH, selector)
                    logger.info(f"선택자 '{selector}'로 {len(checkboxes)}개의 개별 체크박스 발견")
                    
                    for i, checkbox in enumerate(checkboxes):
                        try:
                            if checkbox.is_displayed() and checkbox.is_enabled():
                                # 이미 선택된 체크박스는 건너뛰기
                                if checkbox.is_selected():
                                    selected_count += 1
                                    continue
                                
                                # 체크박스 클릭
                                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
                                time.sleep(0.2)
                                
                                # JavaScript 클릭 시도
                                self.driver.execute_script("""
                                    const checkbox = arguments[0];
                                    const clickEvent = new MouseEvent('click', {
                                        view: window,
                                        bubbles: true,
                                        cancelable: true
                                    });
                                    checkbox.dispatchEvent(clickEvent);
                                """, checkbox)
                                
                                time.sleep(0.3)
                                
                                if checkbox.is_selected():
                                    selected_count += 1
                                    logger.info(f"개별 체크박스 {i+1} 선택 성공")
                                else:
                                    logger.warning(f"개별 체크박스 {i+1} 선택 실패")
                                    
                        except Exception as checkbox_error:
                            logger.warning(f"개별 체크박스 {i+1} 클릭 중 오류: {checkbox_error}")
                            continue
                    
                    # 선택된 체크박스가 있으면 성공으로 간주
                    if selected_count > 0:
                        logger.info(f"개별 상품 체크박스 {selected_count}개 선택 완료")
                        
                        # 실제 선택 확인
                        if self._verify_products_selected():
                            logger.info("개별 선택 성공: 상품이 실제로 선택되었습니다.")
                            return True
                        else:
                            logger.warning("개별 체크박스는 선택되었지만 상품이 실제로 선택되지 않았습니다.")
                    
                except Exception as selector_error:
                    logger.warning(f"선택자 '{selector}' 처리 중 오류: {selector_error}")
                    continue
            
            if selected_count == 0:
                logger.error("개별 상품 체크박스를 찾을 수 없거나 선택할 수 없습니다.")
                return False
            else:
                logger.warning(f"{selected_count}개의 체크박스를 선택했지만 상품 선택이 완전히 작동하지 않았습니다.")
                return False
                
        except Exception as e:
            logger.error(f"개별 상품 체크박스 선택 중 오류: {e}")
            return False
    
    def _label_wrapper_click(self, checkbox_element):
        """라벨 래퍼 클릭 시도"""
        try:
            label_wrapper = checkbox_element.find_element(By.XPATH, "./ancestor::label[contains(@class, 'ant-checkbox-wrapper')]")
            label_wrapper.click()
            logger.info("라벨 래퍼 클릭 성공")
        except Exception as e:
            logger.warning(f"라벨 래퍼 클릭 실패: {e}")
            raise
    
    def _span_wrapper_click(self, checkbox_element):
        """스팬 래퍼 클릭 시도"""
        try:
            span_wrapper = checkbox_element.find_element(By.XPATH, "./ancestor::span[contains(@class, 'ant-checkbox')]")
            span_wrapper.click()
            logger.info("스팬 래퍼 클릭 성공")
        except Exception as e:
            logger.warning(f"스팬 래퍼 클릭 실패: {e}")
            raise
    
    def _action_chains_click(self, checkbox_element):
        """ActionChains를 사용한 클릭"""
        try:
            from selenium.webdriver.common.action_chains import ActionChains
            actions = ActionChains(self.driver)
            actions.move_to_element(checkbox_element).click().perform()
            logger.info("ActionChains 클릭 성공")
        except Exception as e:
            logger.warning(f"ActionChains 클릭 실패: {e}")
            raise
    
    def _parent_element_click(self, checkbox_element):
        """부모 요소 클릭 시도"""
        try:
            parent = checkbox_element.find_element(By.XPATH, "./..")
            parent.click()
            logger.info("부모 요소 클릭 성공")
        except Exception as e:
            logger.warning(f"부모 요소 클릭 실패: {e}")
            raise
    
    def _label_click(self, checkbox_element):
        """연관된 라벨 클릭 시도"""
        try:
            checkbox_id = checkbox_element.get_attribute('id')
            if checkbox_id:
                label = self.driver.find_element(By.XPATH, f"//label[@for='{checkbox_id}']")
                label.click()
                logger.info("연관된 라벨 클릭 성공")
            else:
                raise Exception("체크박스에 ID가 없음")
        except Exception as e:
            logger.warning(f"연관된 라벨 클릭 실패: {e}")
            raise
    
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
                    logger.error("모달창이 닫히지 않았습니다. 그룹 이동이 실패했을 수 있습니다.")
                    return False
                
            except (TimeoutException, NoSuchElementException):
                logger.error(f"'{group_name}' 그룹을 찾을 수 없습니다.")
                return False
                
        except Exception as e:
            logger.error(f"그룹 이동 모달창에서 그룹 선택 오류: {e}")
            return False
    
    def move_products_to_group(self, group_name, items_per_page=20, timeout=10):
        """
        선택된 상품을 특정 그룹으로 이동 (안정적인 백업 구조 적용)
        - 상품 개수 설정 (선택사항)
        - 전체 상품 선택
        - 그룹 이동 모달 열기
        - 그룹 선택 및 이동 확인
        
        Args:
            group_name: 이동할 그룹 이름
            items_per_page: 페이지당 표시할 상품 개수 (20 또는 50)
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"상품을 '{group_name}' 그룹으로 이동 시작 (안정적인 백업 구조)")
            
            # 1. 상품 개수 설정 (선택사항)
            try:
                if hasattr(self, 'select_items_per_page'):
                    if not self.select_items_per_page(items_per_page, timeout):
                        logger.warning(f"{items_per_page}개씩 보기 설정 실패, 계속 진행합니다.")
                else:
                    logger.info("상품 개수 설정 메서드가 없어 건너뜁니다.")
            except Exception as e:
                logger.warning(f"상품 개수 설정 중 오류 (계속 진행): {e}")
            
            # 2. 상품 선택 상태 확인 (이미 선택된 상태라고 가정)
            logger.info("상품이 이미 선택된 상태로 가정하고 그룹 이동을 진행합니다.")
            
            # 3. 그룹 이동 모달 열기
            if not self.open_group_assignment_modal(timeout):
                logger.error("그룹 이동 모달창 열기 실패, 그룹 이동을 중단합니다.")
                return False
            
            # 4. 그룹 선택 및 이동
            if not self.select_group_in_modal(group_name, timeout):
                logger.error(f"'{group_name}' 그룹 선택 실패, 그룹 이동을 중단합니다.")
                return False
            
            logger.info(f"상품이 '{group_name}' 그룹으로 성공적으로 이동되었습니다.")
            return True
            
        except Exception as e:
            logger.error(f"상품 그룹 이동 오류: {e}")
            return False
    
    # =============================================================================
    # 유형별 드롭박스 열기 메서드
    # =============================================================================
    
    def open_product_item_dropdown(self, item_index=0, timeout=2):
        """
        개별 상품 아이템의 그룹 드롭박스 열기
        (비그룹 상품보기에서 선택한 상품의 드롭박스)
        
        Args:
            item_index: 여러 상품이 있을 경우 상품 인덱스 (기본값: 0, 첫 번째 상품)
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"상품 아이템({item_index})의 그룹 드롭박스 열기")
            
            # 개별 상품의 드롭박스 선택자 - 더 정확한 선택자 사용
            selectors = [
                # '그룹 없음' 텍스트가 포함된 드롭박스 선택
                "//div[contains(@class, 'ant-select-single')][.//span[contains(text(), '그룹 없음')]]",
                
                # sc-dkmUuB 클래스가 포함된 드롭박스 선택 (상품 그룹 드롭박스에만 있는 클래스)
                "//div[contains(@class, 'ant-select-single')][.//span[contains(@class, 'sc-dkmUuB')]]",
                
                # 순서 기반 배열 선택자 (대체 수단으로만 사용)
                f"(//div[contains(@class, 'ant-select-single') and not(contains(@class, 'ant-select-borderless'))])[position()={item_index + 1}]",
                
                # 그룹상품관리 화면 (대체 선택자)
                f"(//div[contains(@class, 'sc-gwZKzw')]//div[contains(@class, 'ant-select-single')])[position()={item_index + 1}]"
            ]
            
            # JavaScript로 서술적 접근 시도 (선택자가 실패할 경우를 대비)
            js_script = """
            try {
                // 그룹 드롭박스 찾기 (그룹 없음 텍스트 포함 또는 sc-dkmUuB 클래스 포함)
                const groupDropdowns = Array.from(document.querySelectorAll('div.ant-select-single')).filter(el => {
                    return el.textContent.includes('그룹 없음') || 
                           el.querySelector('.sc-dkmUuB') !== null;
                });
                
                if (groupDropdowns.length > 0) {
                    const found = groupDropdowns[0];
                    found.scrollIntoView({behavior: 'smooth', block: 'center'});
                    return true;
                }
                return false;
            } catch (e) {
                return false;
            }
            """
            
            # 먼저 JavaScript로 요소를 화면 중앙에 보이게 하기
            self.driver.execute_script(js_script)
            time.sleep(DELAY_VERY_SHORT)  # 스크롤링 대기
            
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
                logger.error(f"상품 아이템({item_index})의 그룹 드롭박스를 찾을 수 없습니다.")
                return False
                    
            # 드롭박스 클릭하여 열기
            dropdown_element.click()
            time.sleep(DELAY_SHORT)
            logger.info(f"상품 아이템({item_index})의 그룹 드롭박스가 열렸습니다.")
            return True
            
        except Exception as e:
            logger.error(f"상품 아이템 그룹 드롭박스 열기 오류: {e}")
            return False
    
    def select_group_by_name(self, group_name, timeout=10):
        """
        열린 드롭다운 메뉴에서 이름으로 그룹 선택 (dropdown_utils3 방식 적용)
        
        Args:
            group_name: 선택할 그룹의 이름 (예: "등록B", "완료D3")
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"드롭다운 메뉴에서 '{group_name}' 그룹 선택")
            
            # 그룹명으로 아이템 선택자 (dropdown_utils3와 동일)
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
    
    def select_group_in_management_screen(self, group_name, timeout=5):
        """
        그룹상품관리 화면에서 라디오 버튼으로 그룹 선택
        
        Args:
            group_name: 선택할 그룹의 이름 (예: "대기1", "쇼핑몰T")
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"그룹상품관리 화면에서 '{group_name}' 그룹 선택")
            
            # 라디오 버튼 선택자
            selectors = [
                f"//div[contains(@class, 'ant-radio-group')]//label[contains(@class, 'ant-radio-wrapper')][./span[contains(text(), '{group_name}')]]",
                f"//label[contains(@class, 'ant-radio-wrapper')][./span[contains(text(), '{group_name}')]]"
            ]
            
            group_element = None
            for selector in selectors:
                try:
                    group_element = WebDriverWait(self.driver, timeout).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except (TimeoutException, NoSuchElementException):
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
            logger.error(f"그룹상품관리 화면 그룹 선택 오류: {e}")
            return False
    

    
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
        
        # 드롭다운이 열린 후 옵션들이 로드될 시간을 기다림
        time.sleep(DELAY_SHORT)
        
        return self.select_group_by_name(group_name)
    
    def move_product_to_group(self, group_name, product_index=0, timeout=5):
        """
        개별 상품을 특정 그룹으로 이동 (코어5 전용 - 안정적인 백업 구조)
        3단계 백업 구조: 1차(드롭다운+이름) -> 2차(원스텝) -> 3차(모달 방식)
        
        Args:
            group_name: 이동할 그룹 이름
            product_index: 상품 인덱스 (기본값: 0, 첫 번째 상품)
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"상품 {product_index}를 '{group_name}' 그룹으로 이동 시작 (3단계 백업 구조)")
            
            # 1차 시도: 정상적인 드롭다운 열기 방식 (코어3과 동일)
            logger.info("1차 시도: 정상적인 드롭다운 열기 방식")
            try:
                if self.open_product_item_dropdown(item_index=product_index, timeout=timeout):
                    logger.info("드롭다운 열기 성공")
                    if self.select_group_by_name(group_name):
                        logger.info(f"1차 시도 성공: 정상적인 방식으로 '{group_name}' 그룹 이동 완료")
                        return True
                    else:
                        logger.warning(f"드롭다운에서 '{group_name}' 그룹 선택 실패")
                else:
                    logger.warning("드롭다운 열기 실패")
            except Exception as dropdown_error:
                logger.error(f"1차 시도 중 오류 발생: {dropdown_error}")
            
            # 2차 시도: 기본 방식 (원스텝)
            logger.warning("1차 시도 실패, 2차 시도: 기본 방식 (원스텝)")
            success = self.select_product_group_by_name(group_name, item_index=product_index)
            
            if success:
                logger.info(f"2차 시도 성공: 기본 방식으로 '{group_name}' 그룹 이동 완료")
                return True
            
            # 3차 시도: 그룹지정 모달 방식 (최종 백업)
            logger.warning("2차 시도 실패, 3차 시도: 그룹지정 모달 방식 (최종 백업)")
            try:
                # 1. 첫번째 상품의 체크박스 선택
                if self.select_first_product():
                    logger.info("첫번째 상품 체크박스 선택 성공")
                    
                    # 2. 그룹지정 모달 열기
                    if self.open_group_assignment_modal():
                        logger.info("그룹지정 모달 열기 성공")
                        
                        # 3. 모달에서 대상 그룹 선택
                        if self.select_group_in_modal(group_name):
                            logger.info(f"3차 시도 성공: 모달에서 '{group_name}' 그룹 선택 완료")
                            return True
                        else:
                            logger.error(f"모달에서 '{group_name}' 그룹 선택 실패")
                    else:
                        logger.error("그룹지정 모달 열기 실패")
                else:
                    logger.error("첫번째 상품 체크박스 선택 실패")
                    
            except Exception as modal_error:
                logger.error(f"3차 시도 중 오류 발생: {modal_error}")
            
            # 모든 시도 실패
            logger.error(f"모든 시도 실패: 상품을 '{group_name}' 그룹으로 이동할 수 없습니다.")
            return False
            
        except Exception as e:
            logger.error(f"상품 그룹 이동 중 오류: {e}")
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
            
            # 모달창이 열렸는지 먼저 확인
            modal_body_selector = "//div[contains(@class, 'ant-modal-body')]"
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, modal_body_selector))
                )
                logger.info("모달창 확인됨")
            except TimeoutException:
                logger.error("모달창을 찾을 수 없습니다.")
                return False
            
            # 여러 가지 그룹 라디오 버튼 선택자 시도 (대소문자 구분 없이)
            group_name_lower = group_name.lower()
            radio_selectors = [
                # 기본 선택자 (대소문자 구분 없음)
                f"//div[contains(@class, 'ant-modal-body')]//label[contains(@class, 'ant-radio-wrapper')][./span[translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='{group_name_lower}']]",
                # 더 포괄적인 선택자 (대소문자 구분 없음)
                f"//div[contains(@class, 'ant-modal-body')]//label[contains(@class, 'ant-radio-wrapper')][.//span[translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='{group_name_lower}']]",
                # span 직접 선택 후 부모 label 찾기 (대소문자 구분 없음)
                f"//div[contains(@class, 'ant-modal-body')]//span[translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='{group_name_lower}']/ancestor::label[contains(@class, 'ant-radio-wrapper')]",
                # 더 간단한 선택자 (대소문자 구분 없음)
                f"//label[contains(@class, 'ant-radio-wrapper')][.//span[translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='{group_name_lower}']]",
                # 텍스트만으로 찾기 (대소문자 구분 없음)
                f"//span[translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='{group_name_lower}']/parent::label"
            ]
            
            radio_element = None
            used_selector = None
            
            for i, selector in enumerate(radio_selectors):
                try:
                    logger.info(f"선택자 {i+1} 시도: {selector}")
                    radio_element = WebDriverWait(self.driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    used_selector = selector
                    logger.info(f"선택자 {i+1}로 '{group_name}' 그룹 요소 발견")
                    break
                except (TimeoutException, NoSuchElementException):
                    logger.warning(f"선택자 {i+1} 실패")
                    continue
            
            if radio_element is None:
                # 모든 라디오 버튼 목록 출력해서 디버깅
                try:
                    all_radios = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'ant-modal-body')]//label[contains(@class, 'ant-radio-wrapper')]")
                    logger.info(f"모달창에서 발견된 라디오 버튼 수: {len(all_radios)}")
                    for i, radio in enumerate(all_radios):  # 모든 라디오 버튼 출력
                        try:
                            text = radio.text.strip()
                            logger.info(f"라디오 버튼 {i+1}: '{text}'")
                        except:
                            logger.info(f"라디오 버튼 {i+1}: 텍스트 읽기 실패")
                except Exception as e:
                    logger.error(f"라디오 버튼 목록 확인 실패: {e}")
                
                logger.error(f"'{group_name}' 그룹을 찾을 수 없습니다.")
                self._close_modal_if_open()
                return False
            
            # 그룹 선택
            try:
                radio_element.click()
                time.sleep(0.5)
                logger.info(f"'{group_name}' 그룹이 선택되었습니다. (사용된 선택자: {used_selector})")
            except Exception as e:
                logger.error(f"그룹 클릭 실패: {e}")
                self._close_modal_if_open()
                return False
                
            # 확인 버튼 클릭
            confirm_button_selectors = [
                "//div[contains(@class, 'ant-modal-footer')]//button[contains(@class, 'ant-btn-primary')][.//span[text()='확인']]",
                "//div[contains(@class, 'ant-modal-footer')]//button[contains(@class, 'ant-btn-primary')]",
                "//button[contains(@class, 'ant-btn-primary')][.//span[text()='확인']]",
                "//button[.//span[text()='확인']]"
            ]
            
            confirm_button = None
            for selector in confirm_button_selectors:
                try:
                    confirm_button = WebDriverWait(self.driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except (TimeoutException, NoSuchElementException):
                    continue
            
            if confirm_button is None:
                logger.error("확인 버튼을 찾을 수 없습니다.")
                self._close_modal_if_open()
                return False
            
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
    
    def _scroll_and_search_for_group(self, group_name):
        """
        드롭다운 컨테이너 내에서 스크롤하며 그룹 검색 (dropdown_utils3에서 가져옴)
        
        Args:
            group_name: 찾을 그룹 이름
        """
        try:
            # 드롭다운 컨테이너 찾기
            dropdown_container = self.driver.find_element(By.CSS_SELECTOR, ".ant-select-dropdown .rc-virtual-list-holder")
            
            max_scrolls = 10
            scroll_count = 0
            
            while scroll_count < max_scrolls:
                # 현재 보이는 그룹 요소들 확인
                visible_groups = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'ant-select-item-option')]")
                
                for group in visible_groups:
                    try:
                        group_text = group.get_attribute('textContent') or group.text
                        if group_name in group_text:
                            logger.info(f"스크롤 중 '{group_name}' 그룹 발견")
                            return
                    except StaleElementReferenceException:
                        continue
                
                # 아래로 스크롤
                self.driver.execute_script("arguments[0].scrollTop += 200;", dropdown_container)
                time.sleep(0.2)
                scroll_count += 1
                
            logger.warning(f"스크롤 완료했지만 '{group_name}' 그룹을 찾지 못했습니다.")
            
        except Exception as e:
            logger.error(f"스크롤 검색 중 오류: {e}")
    
    def get_product_count(self):
        """
        검색된 상품 개수 확인
        
        Returns:
            int: 상품 개수 (-1: 오류)
        """
        try:
            # 상품 개수 표시 요소 찾기
            count_selectors = [
                "//div[contains(@class, 'ant-pagination-total-text')]",
                "//span[contains(text(), '총') and contains(text(), '개')]",
                "//div[contains(text(), '총') and contains(text(), '건')]"
            ]
            
            for selector in count_selectors:
                try:
                    count_element = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    count_text = count_element.text
                    
                    # 숫자 추출
                    import re
                    numbers = re.findall(r'\d+', count_text)
                    if numbers:
                        count = int(numbers[0])
                        logger.info(f"검색된 상품 개수: {count}개")
                        return count
                        
                except (TimeoutException, NoSuchElementException):
                    continue
            
            logger.warning("상품 개수를 확인할 수 없습니다.")
            return -1
            
        except Exception as e:
            logger.error(f"상품 개수 확인 중 오류: {e}")
            return -1

# 싱글톤 패턴으로 드롭다운 헬퍼 인스턴스 관리
_dropdown_helper_instance = None

def get_dropdown_helper(driver=None):
    """
    드롭다운 및 그룹 선택 헬퍼 인스턴스 가져오기 (싱글톤 패턴)
    
    Args:
        driver: 셀레니움 웹드라이버 (선택 사항)
        
    Returns:
        PercentyDropdown: 드롭다운 및 그룹 선택 헬퍼 인스턴스
    """
    global _dropdown_helper_instance
    
    if _dropdown_helper_instance is None or driver is not None:
        if driver is None:
            raise ValueError("첫 번째 호출 시 driver 매개변수가 필요합니다.")
        _dropdown_helper_instance = PercentyDropdown(driver)
        logger.info("새로운 드롭다운 헬퍼 인스턴스가 생성되었습니다.")
    
    return _dropdown_helper_instance

# get_dropdown_manager를 get_dropdown_helper의 별칭으로 추가 (이전 코드와의 호환성 유지)
def get_dropdown_manager(driver=None):
    """
    get_dropdown_helper의 별칭 함수 - 이전 코드와의 호환성을 위해 제공 (코어5 전용)
    
    Args:
        driver: 셀레니움 웹드라이버 (선택 사항)
        
    Returns:
        PercentyDropdown: 드롭다운 및 그룹 선택 헬퍼 인스턴스
    """
    return get_dropdown_helper(driver)