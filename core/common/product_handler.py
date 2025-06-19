# -*- coding: utf-8 -*-
"""
상품 처리 공통 함수들
상품 개수 확인, 토글 처리 등의 공통 기능
"""

import logging
import time
import re
from typing import Optional
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)

def check_product_count(driver: WebDriver) -> int:
    """
    현재 상품 목록의 상품 개수를 확인
    
    Args:
        driver: Selenium WebDriver 인스턴스
        
    Returns:
        int: 현재 상품 목록의 상품 개수. 실패시 0 반환
    """
    try:
        # 방법 1: "총 X개 상품" 텍스트를 확인하는 방법 (가장 정확한 방법)
        try:
            # "총 X개 상품" 표시 텍스트 찾기
            total_text_xpath = "//span[contains(text(), '총') and contains(text(), '개 상품')]"
            total_element = driver.find_element(By.XPATH, total_text_xpath)
            if total_element:
                total_text = total_element.text.strip()
                logger.info(f"상품 개수 텍스트 발견: '{total_text}'")
                
                # "총 3,536개 상품" 형식에서 숫자만 추출
                numbers = re.findall(r'\d+,?\d*', total_text)
                if numbers:
                    # 콤마 제거 후 정수로 변환
                    product_count = int(numbers[0].replace(',', ''))
                    logger.info(f"화면에 표시된 상품 개수: {product_count}개")
                    return product_count
        except Exception as text_error:
            logger.info(f"총 상품 개수 텍스트 추출 시도 실패: {text_error}")
        
        # JavaScript로 총 상품 개수 텍스트 확인 시도
        try:
            js_text = """
            const totalText = Array.from(document.querySelectorAll('span')).find(el => 
                el.textContent && el.textContent.includes('총') && el.textContent.includes('개 상품'))?.textContent;
            if (totalText) {
                const match = totalText.match(/\\d+,?\\d*/g);
                return match ? match[0].replace(/,/g, '') : null;
            }
            return null;
            """
            js_count = driver.execute_script(js_text)
            if js_count:
                product_count = int(js_count)
                logger.info(f"JavaScript로 추출한 총 상품 개수: {product_count}개")
                return product_count
        except Exception as js_text_error:
            logger.info(f"JavaScript 텍스트 추출 시도 실패: {js_text_error}")
        
        # 방법 2: 상품 아이템 개수 확인
        # JavaScript로 상품 개수 확인 시도
        js_code = """
        return {
            productItems: document.querySelectorAll('div.sc-fremEr').length,
            productNames: document.querySelectorAll('span.sc-cQCQeq.sc-inyXkq').length
        };
        """
        js_result = driver.execute_script(js_code)
        if js_result and isinstance(js_result, dict):
            product_items = js_result.get('productItems', 0)
            product_names = js_result.get('productNames', 0)
            logger.info(f"JavaScript 결과 - 상품아이템: {product_items}, 상품명: {product_names}")
            if product_items > 0:
                return product_items
            if product_names > 0:
                return product_names
        
        # 방법 3: Selenium 선택자로 상품 요소 개수 확인
        methods = [
            # 상품 아이템 개수 확인
            lambda: len(driver.find_elements(By.XPATH, "//div[contains(@class, 'sc-fremEr')]")),
            # 상품명 개수 확인
            lambda: len(driver.find_elements(By.XPATH, "//span[contains(@class, 'sc-cQCQeq') and contains(@class, 'sc-inyXkq')]"))
        ]
        
        # JavaScript 실패 시 일반 Selenium 방법 시도
        for method in methods:
            try:
                count = method()
                if count > 0:
                    return count
            except Exception:
                continue
        
        # 모든 방법 실패 시 0 반환
        logger.warning("상품 개수를 확인할 수 없습니다.")
        return 0
        
    except Exception as e:
        logger.error(f"상품 개수 확인 중 오류: {e}")
        return 0

def check_toggle_state(driver: WebDriver) -> str:
    """
    현재 토글 상태를 확인
    
    Args:
        driver: Selenium WebDriver 인스턴스
        
    Returns:
        str: "비그룹상품보기", "그룹상품보기", 또는 "알 수 없음"
    """
    try:
        # 방법 1: 상품 수로 우선 판단 (가장 신뢰할 수 있는 방법)
        try:
            current_count = check_product_count(driver)
            logger.debug(f"현재 상품 수: {current_count}개")
            
            if current_count > 50000:  # 매우 큰 수치면 그룹상품보기일 가능성이 높음
                logger.debug(f"상품 수({current_count}개)가 50,000개 이상이므로 그룹상품보기로 판단")
                return "그룹상품보기"
            elif current_count > 0 and current_count < 10000:  # 적당한 수치면 비그룹상품보기일 가능성이 높음
                logger.debug(f"상품 수({current_count}개)가 10,000개 미만이므로 비그룹상품보기로 판단")
                return "비그룹상품보기"
        except Exception as count_error:
            logger.debug(f"상품 수 확인 실패: {count_error}")
        
        # 방법 2: DOM 선택자로 토글 찾기
        toggle_element = None
        try:
            from dom_selectors import EDITGOODS_SELECTORS
            selector = EDITGOODS_SELECTORS.get("PRODUCT_VIEW_NOGROUP", "//button[@role='switch' and contains(@class, 'ant-switch')]")
            toggle_element = driver.find_element(By.XPATH, selector)
            logger.debug(f"DOM 선택자로 토글 요소 찾음: {selector}")
        except Exception as dom_error:
            logger.debug(f"DOM 선택자로 토글 찾기 실패: {dom_error}")
        
        # 방법 3: JavaScript로 토글 찾기
        if not toggle_element:
            try:
                js_script = """
                    const buttons = Array.from(document.querySelectorAll('button[role="switch"]'));
                    return buttons.find(el => el.className && el.className.includes('ant-switch'));
                """
                toggle_element = driver.execute_script(js_script)
                if toggle_element:
                    logger.debug("JavaScript로 토글 요소 찾음")
            except Exception as js_error:
                logger.debug(f"JavaScript로 토글 찾기 실패: {js_error}")
        
        if toggle_element:
            # 토글 상태 확인 (aria-checked 속성 또는 클래스명으로 판단)
            try:
                # aria-checked 속성 확인
                aria_checked = toggle_element.get_attribute("aria-checked")
                if aria_checked:
                    if aria_checked.lower() == "true":
                        logger.debug("토글 aria-checked=true이므로 비그룹상품보기로 판단")
                        return "비그룹상품보기"
                    else:
                        logger.debug("토글 aria-checked=false이므로 그룹상품보기로 판단")
                        return "그룹상품보기"
                
                # 클래스명으로 확인
                class_name = toggle_element.get_attribute("class") or ""
                if "ant-switch-checked" in class_name:
                    logger.debug("토글 클래스에 ant-switch-checked가 있으므로 비그룹상품보기로 판단")
                    return "비그룹상품보기"
                else:
                    logger.debug("토글 클래스에 ant-switch-checked가 없으므로 그룹상품보기로 판단")
                    return "그룹상품보기"
                    
            except Exception as attr_error:
                logger.debug(f"토글 속성 확인 실패: {attr_error}")
        
        # 방법 4: 페이지 텍스트로 판단
        try:
            page_source = driver.page_source
            if "비그룹상품" in page_source and "그룹상품" in page_source:
                # 현재 활성화된 텍스트 확인
                js_script = """
                    const elements = Array.from(document.querySelectorAll('*'));
                    const textElements = elements.filter(el => 
                        el.textContent && 
                        (el.textContent.includes('비그룹상품') || el.textContent.includes('그룹상품'))
                    );
                    return textElements.map(el => el.textContent.trim()).join(' ');
                """
                text_content = driver.execute_script(js_script)
                logger.debug(f"페이지 텍스트 내용: {text_content}")
                    
        except Exception as text_error:
            logger.debug(f"페이지 텍스트 확인 실패: {text_error}")
        
        logger.warning("토글 상태를 확인할 수 없습니다")
        return "알 수 없음"
        
    except Exception as e:
        logger.error(f"토글 상태 확인 중 오류: {e}")
        return "알 수 없음"

def toggle_product_view(driver: WebDriver) -> int:
    """
    상품 목록 새로고침을 위한 토글 2회 클릭 기능
    
    Args:
        driver: Selenium WebDriver 인스턴스
        
    Returns:
        int: 현재 목록에 있는 상품 개수. 실패시 0 반환
    """
    logger.info("상품 목록 새로고침 (토글 2회 클릭 방식)")
    
    # 인간 같은 지연 적용
    from human_delay import HumanLikeDelay
    delay = HumanLikeDelay(min_total_delay=3, max_total_delay=6, current_speed=0)
    
    # DOM 선택자 가져오기 - 동일한 DOM 선택자를 2회 사용
    from dom_selectors import EDITGOODS_SELECTORS
    selector = EDITGOODS_SELECTORS.get("PRODUCT_VIEW_NOGROUP", "//button[@role='switch' and contains(@class, 'ant-switch')]")
    
    # 첫번째 클릭 - 그룹상품보기
    logger.info("그룹상품보기 토글 클릭 시도 (1번째 클릭)")
    success = False
    
    try:
        logger.info(f"DOM 선택자로 토글 찾기 시도: {selector}")
        toggle_button = driver.find_element(By.XPATH, selector)
        logger.info("토글 버튼 요소 찾음")
        toggle_button.click()
        logger.info("첫번째 토글 클릭 성공 (DOM 선택자)")
        success = True
    except Exception as e:
        logger.warning(f"DOM 선택자로 첫번째 토글 클릭 실패: {str(e)[:100]}...")
        
        # JavaScript 실행 시도
        try:
            logger.info("JavaScript로 토글 클릭 시도 (1번째)")
            js_script = """
                // 토글 버튼 찾기
                const toggleSwitch = document.querySelector('button[role="switch"][class*="ant-switch"]');
                if (toggleSwitch) {
                    toggleSwitch.click();
                    return true;
                }
                return false;
            """
            result = driver.execute_script(js_script)
            if result:
                logger.info("첫번째 토글 클릭 성공 (JavaScript)")
                success = True
            else:
                logger.warning("JavaScript로 첫번째 토글 클릭 실패")
        except Exception as js_e:
            logger.warning(f"JavaScript 첫번째 토글 클릭 실패: {str(js_e)[:100]}...")
    
    # 첫번째 클릭 후 2초 고정 지연 추가
    logger.info("첫번째 클릭 후 2초 고정 지연 적용")
    time.sleep(2.0)  # 고정 2초 지연
    
    # 추가 지연 - 화면 전환 기다리기
    time.sleep(delay.get_delay('transition'))
    
    # 두번째 클릭 - 비그룹상품보기 (원래 상태로 복귀)
    logger.info("비그룹상품보기 토글 클릭 시도 (2번째 클릭)")
    
    try:
        logger.info(f"DOM 선택자로 토글 찾기 시도: {selector}")
        toggle_button = driver.find_element(By.XPATH, selector)
        logger.info("토글 버튼 요소 찾음")
        toggle_button.click()
        logger.info("두번째 토글 클릭 성공 (DOM 선택자)")
        success = True
    except Exception as e:
        logger.warning(f"DOM 선택자로 두번째 토글 클릭 실패: {str(e)[:100]}...")
        
        # JavaScript 실행 시도
        try:
            logger.info("JavaScript로 토글 클릭 시도 (2번째)")
            js_script = """
                // 토글 버튼 찾기
                const toggleSwitch = document.querySelector('button[role="switch"][class*="ant-switch"]');
                if (toggleSwitch) {
                    toggleSwitch.click();
                    return true;
                }
                return false;
            """
            result = driver.execute_script(js_script)
            if result:
                logger.info("두번째 토글 클릭 성공 (JavaScript)")
                success = True
            else:
                logger.warning("JavaScript로 두번째 토글 클릭 실패")
        except Exception as js_e:
            logger.warning(f"JavaScript 두번째 토글 클릭 실패: {str(js_e)[:100]}...")
    
    # 두번째 클릭 후 5초 고정 지연 추가
    logger.info("두번째 클릭 후 5초 고정 지연 적용")
    time.sleep(5.0)  # 고정 5초 지연
    
    # 상품 목록 로딩 대기
    from timesleep import DELAY_STANDARD
    logger.info(f"상품 목록 로딩 대기 - {delay.get_delay('waiting') + DELAY_STANDARD}초")
    time.sleep(delay.get_delay('waiting') + DELAY_STANDARD)
    
    # 페이지 로딩 확인 - '총 X개 상품' 텍스트를 찾는 방식으로 변경
    try:
        logger.info("상품 목록 로딩 확인 시도 ('총 X개 상품' 텍스트 검색)...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(text(), '총') and contains(text(), '개 상품')]"))
        )
        logger.info("상품 목록 로딩 확인됨 ('총 X개 상품' 텍스트 찾음)")
    except Exception as e:
        logger.warning(f"상품 목록 로딩 확인 실패: {e}")
    
    # 상품 개수 확인
    product_count = check_product_count(driver)
    logger.info(f"현재 비그룹상품 목록에 {product_count}개의 상품이 있습니다.")
    
    # 성공 여부와 관계없이 상품 개수 반환
    logger.info("상품 목록 새로고침 완료 및 화면 로딩 확인")
    return product_count