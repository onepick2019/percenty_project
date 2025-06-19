#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
퍼센티 모달창 자동 닫기 모듈

이 모듈은 퍼센티 사이트의 마케팅/이벤트 모달창을 자동으로 "다시 보지 않기" 버튼을 클릭하여
영구적으로 닫아줍니다.
"""

import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

# 모달창 처리 간격을 추적하기 위한 변수
last_modal_close_time = 0
MODAL_PROCESS_INTERVAL = 5  # 5초 내에 중복 처리 방지

def click_dont_show_again_button(driver):
    """
    모달창의 "다시 보지 않기" 버튼을 클릭합니다.
    
    Args:
        driver: Selenium WebDriver 인스턴스
    
    Returns:
        bool: 버튼 클릭 성공 여부
    """
    try:
        # 여러 가지 방법으로 "다시 보지 않기" 버튼 찾기 시도
        selectors = [
            # 1. 텍스트로 찾기
            "//button[contains(text(), '다시 보지 않기')]",
            "//span[contains(text(), '다시 보지 않기')]/parent::button",
            
            # 2. 클래스와 텍스트 조합으로 찾기
            "//button[contains(@class, 'ant-btn')]/span[contains(text(), '다시 보지 않기')]/..",
            
            # 3. 모달 푸터 내 버튼 찾기
            "//div[contains(@class, 'ant-modal-footer')]//button[contains(text(), '다시 보지 않기')]",
            "//div[contains(@class, 'ant-modal-footer')]//button/span[contains(text(), '다시 보지 않기')]/.."
        ]
        
        for selector in selectors:
            try:
                button = driver.find_element(By.XPATH, selector)
                logging.info(f"'다시 보지 않기' 버튼을 찾았습니다: {selector}")
                button.click()
                logging.info("'다시 보지 않기' 버튼 클릭 성공")
                time.sleep(0.5)  # 클릭 후 짧은 대기
                return True
            except NoSuchElementException:
                continue
        
        # JavaScript로 시도
        script = """
        // 다시 보지 않기 버튼 찾기
        var buttons = Array.from(document.querySelectorAll('button'));
        var dontShowButton = buttons.find(btn => {
            var text = btn.textContent.trim();
            return text === '다시 보지 않기' || text.includes('다시 보지 않기');
        });
        
        if (dontShowButton) {
            dontShowButton.click();
            return { success: true, method: 'js_click' };
        }
        
        return { success: false, error: 'button_not_found' };
        """
        
        result = driver.execute_script(script)
        if result.get('success', False):
            logging.info(f"JavaScript로 '다시 보지 않기' 버튼 클릭 성공: {result}")
            time.sleep(0.5)  # 클릭 후 짧은 대기
            return True
            
        # 버튼을 찾지 못한 경우, 닫기 버튼이라도 클릭
        close_selectors = [
            "//button[contains(text(), '닫기')]",
            "//span[contains(text(), '닫기')]/parent::button",
            "//div[contains(@class, 'ant-modal-footer')]//button[contains(text(), '닫기')]",
            "//div[contains(@class, 'ant-modal-close')]",
            "//span[contains(@class, 'ant-modal-close-x')]"
        ]
        
        for selector in close_selectors:
            try:
                button = driver.find_element(By.XPATH, selector)
                logging.info(f"'닫기' 버튼을 찾았습니다: {selector}")
                button.click()
                logging.info("'닫기' 버튼 클릭 성공")
                time.sleep(0.5)  # 클릭 후 짧은 대기
                return True
            except NoSuchElementException:
                continue
        
        logging.warning("'다시 보지 않기' 또는 '닫기' 버튼을 찾지 못했습니다.")
        return False
    
    except Exception as e:
        logging.error(f"모달창 버튼 클릭 중 오류 발생: {e}")
        return False

def press_escape_key(driver):
    """
    ESC 키를 눌러 모달창을 닫습니다.
    
    Args:
        driver: Selenium WebDriver 인스턴스
    """
    try:
        # 1. ActionChains 사용
        actions = ActionChains(driver)
        actions.send_keys(Keys.ESCAPE)
        actions.perform()
        logging.info("ActionChains로 ESC 키 전송 완료")
        
        # 2. JavaScript 사용
        script = """
        document.dispatchEvent(new KeyboardEvent('keydown', {
            'key': 'Escape',
            'code': 'Escape',
            'keyCode': 27,
            'which': 27,
            'bubbles': true,
            'cancelable': true
        }));
        return true;
        """
        driver.execute_script(script)
        logging.info("JavaScript로 ESC 키 이벤트 전송 완료")
        
        return True
    except Exception as e:
        logging.error(f"ESC 키 전송 중 오류 발생: {e}")
        return False

def set_modal_cookies_and_storage(driver):
    """
    모달창 관련 쿠키와 localStorage 설정하여 다시 표시되지 않도록 합니다.
    
    Args:
        driver: Selenium WebDriver 인스턴스
    """
    try:
        script = """
        // 쿠키 설정
        function setCookie(name, value, days) {
            var expires = "";
            if (days) {
                var date = new Date();
                date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
                expires = "; expires=" + date.toUTCString();
            }
            document.cookie = name + "=" + (value || "") + expires + "; path=/";
        }
        
        // 마케팅/이벤트 모달창 관련 쿠키 설정
        setCookie("modal_shown", "true", 30);
        setCookie("modal_dismissed", "true", 30);
        setCookie("dont_show_again", "true", 30);
        setCookie("percenty_modal_blocked", "true", 30);
        
        // localStorage 설정
        try {
            localStorage.setItem('modal_shown', 'true');
            localStorage.setItem('modal_dismissed', 'true');
            localStorage.setItem('dont_show_again', 'true');
            localStorage.setItem('percenty_modal_blocked', 'true');
            localStorage.setItem('percenty_modal_timestamp', Date.now().toString());
            return { success: true, storage: 'set' };
        } catch(e) {
            return { success: false, error: e.toString() };
        }
        """
        
        result = driver.execute_script(script)
        logging.info(f"모달창 관련 쿠키 및 localStorage 설정 결과: {result}")
        return result
    except Exception as e:
        logging.error(f"쿠키 및 localStorage 설정 중 오류 발생: {e}")
        return {"success": False, "error": str(e)}

def is_modal_visible(driver):
    """
    현재 페이지에 모달창이 표시되고 있는지 확인합니다.
    
    Args:
        driver: Selenium WebDriver 인스턴스
    
    Returns:
        bool: 모달창 표시 여부
    """
    try:
        # 여러 모달창 선택자 확인
        modal_selectors = [
            "div.ant-modal",
            "div.ant-modal-root",
            "div.ant-modal-wrap",
            "div[role='dialog']"
        ]
        
        for selector in modal_selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for element in elements:
                if element.is_displayed():
                    # 프롬프트나 알림 등의 중요 UI는 제외
                    classes = element.get_attribute("class") or ""
                    if any(cls in classes for cls in ["notification", "message", "alert", "toast"]):
                        continue
                    
                    # 이미지가 있거나 모달 푸터가 있으면 마케팅/이벤트 모달창으로 간주
                    try:
                        element.find_element(By.CSS_SELECTOR, "img")
                        logging.info("이미지가 포함된 모달창 발견")
                        return True
                    except NoSuchElementException:
                        pass
                    
                    try:
                        element.find_element(By.CSS_SELECTOR, ".ant-modal-footer")
                        logging.info("푸터가 있는 모달창 발견")
                        return True
                    except NoSuchElementException:
                        pass
                    
                    # "다시 보지 않기" 버튼이 있는지 확인
                    try:
                        btn_text = element.text.lower()
                        if "다시 보지 않기" in btn_text or "닫기" in btn_text:
                            logging.info("'다시 보지 않기' 또는 '닫기' 텍스트가 있는 모달창 발견")
                            return True
                    except:
                        pass
        
        return False
    except Exception as e:
        logging.error(f"모달창 확인 중 오류 발생: {e}")
        return False

def close_modal_dialog(driver):
    """
    모달창을 감지하고 "다시 보지 않기" 버튼을 클릭하여 닫습니다.
    새로고침이나 새 탭 열기 등에서도 모달창이 표시되지 않도록 합니다.
    
    Args:
        driver: Selenium WebDriver 인스턴스
    
    Returns:
        dict: 처리 결과
    """
    global last_modal_close_time
    
    current_time = time.time()
    if current_time - last_modal_close_time < MODAL_PROCESS_INTERVAL:
        logging.info("모달창 처리 요청이 너무 빈번합니다. 이전 설정이 적용 중입니다.")
        return {"success": True, "method": "skipped_due_to_interval"}
    
    last_modal_close_time = current_time
    
    try:
        # 모달창이 표시되는지 확인
        if not is_modal_visible(driver):
            logging.info("표시된 모달창이 없습니다.")
            
            # 모달창이 없어도 쿠키와 로컬 스토리지 설정은 진행
            set_modal_cookies_and_storage(driver)
            return {"success": True, "method": "no_modal_found"}
        
        logging.info("모달창이 감지되었습니다. 닫기 처리를 시작합니다.")
        
        # 1. "다시 보지 않기" 버튼 클릭 시도
        button_clicked = click_dont_show_again_button(driver)
        
        # 2. 쿠키와 localStorage 설정
        storage_result = set_modal_cookies_and_storage(driver)
        
        # 3. 버튼 클릭에 실패한 경우 ESC 키 전송 시도
        if not button_clicked:
            logging.info("버튼 클릭에 실패했습니다. ESC 키를 시도합니다.")
            press_escape_key(driver)
        
        # 4. 다시 확인하여 모달창이 여전히 표시되는지 확인
        time.sleep(0.5)
        if is_modal_visible(driver):
            logging.warning("모달창이 여전히 표시됩니다. 추가 시도가 필요할 수 있습니다.")
            # 한 번 더 ESC 키 시도
            press_escape_key(driver)
        else:
            logging.info("모달창이 성공적으로 닫혔습니다.")
        
        return {
            "success": True, 
            "button_clicked": button_clicked,
            "storage_set": storage_result.get("success", False),
            "method": "modal_close_complete"
        }
        
    except Exception as e:
        logging.error(f"모달창 처리 중 오류 발생: {e}")
        return {"success": False, "error": str(e)}

def block_modals_on_page(driver, url=None):
    """
    현재 페이지에서 모달창을 감지하고 "다시 보지 않기" 버튼을 클릭하여 닫습니다.
    
    Args:
        driver: Selenium WebDriver 인스턴스
        url: 선택적으로 이동할 URL (기본값: None, 현재 페이지 유지)
    
    Returns:
        bool: 처리 성공 여부
    """
    try:
        # URL이 지정된 경우에만 해당 URL로 이동
        if url and url != driver.current_url:
            current_url = driver.current_url
            logging.info(f"현재 URL: {current_url}, 이동 URL: {url}")
            driver.get(url)
            logging.info(f"URL로 이동 완료: {url}")
            time.sleep(1)  # 페이지 로드 대기
        
        # 모달창 닫기 처리
        result = close_modal_dialog(driver)
        logging.info(f"모달창 처리 결과: {result}")
        
        return result.get("success", False)
    
    except Exception as e:
        logging.error(f"페이지에서 모달창 처리 중 오류 발생: {e}")
        return False

# 기존 함수명 호환성 유지
def block_modals_on_new_tab(driver, url=None):
    """
    기존 호환성을 위한 별칭 함수 - block_modals_on_page를 호출합니다.
    
    Args:
        driver: Selenium WebDriver 인스턴스
        url: 선택적으로 이동할 URL
    
    Returns:
        bool: 설정 성공 여부
    """
    logging.info("주의: block_modals_on_new_tab 함수는 이제 block_modals_on_page로 대체되었습니다.")
    return block_modals_on_page(driver, url)

# 테스트 코드
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logging.info("모달창 자동 닫기 모듈 테스트")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        # Chrome 옵션 설정
        options = Options()
        options.add_argument("--start-maximized")
        
        # 브라우저 실행
        driver = webdriver.Chrome(options=options)
        
        # 테스트 URL 열기
        driver.get("https://www.percenty.co.kr/")
        
        # 모달창 닫기 기능 설정
        close_modal_dialog(driver)
        
        # 새 탭에서 테스트
        driver.execute_script("window.open('https://www.percenty.co.kr/')")
        driver.switch_to.window(driver.window_handles[-1])
        close_modal_dialog(driver)
        
        # 결과 대기
        logging.info("테스트 완료. 브라우저를 확인하세요.")
        time.sleep(30)
        
        # 브라우저 종료
        driver.quit()
        
    except Exception as e:
        logging.error(f"테스트 중 오류 발생: {e}")
