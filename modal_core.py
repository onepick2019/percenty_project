# -*- coding: utf-8 -*-
"""
모달창 처리 핵심 모듈

이 모듈은 퍼센티 사이트 이용 시 발생하는 다양한 모달창을 처리합니다.
- 크롬 비밀번호 저장 모달창 처리
- 로그인 모달창 숨기기
- 채널톡 숨기기
등의 기능을 통합적으로 제공합니다.
"""

import time
import logging
import traceback
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    ElementNotInteractableException, 
    StaleElementReferenceException
)

# 좌표 정보 가져오기
from coordinates.coordinates_all import *
# 모달창 관련 DOM 선택자 가져오기
from dom_selectors import MODAL_SELECTORS
# 기존 모듈 임포트
from modal_blocker import block_modals_on_page, press_escape_key, close_modal_dialog, set_modal_cookies_and_storage
from channel_talk_utils import check_and_hide_channel_talk
from login_modal_utils import hide_login_modal

# 로깅 설정
logger = logging.getLogger(__name__)

class ModalCore:
    """모달창 처리 핵심 클래스"""
    
    def __init__(self, driver):
        """
        초기화
        
        Args:
            driver: Selenium WebDriver 인스턴스
        """
        self.driver = driver
        self.password_save_modal_closed = False
        self.login_modal_closed = False
        self.channel_talk_hidden = False
        
    def close_notification(self):
        """
        자동화 알림 닫기 - 절대좌표 사용
        
        Returns:
            bool: 알림 닫기 성공 여부
        """
        try:
            # 알림이 존재하는지 확인
            notification_exists = self.driver.execute_script("""
                return document.querySelector('.ant-notification-notice') !== null;
            """)
            
            if notification_exists:
                logging.info("자동화 알림 닫기 시도")
                close_x, close_y = NOTIFICATION["CLOSE"]
                
                # JavaScript로 클릭 시도
                js_click_script = """
                    var element = document.elementFromPoint(arguments[0], arguments[1]);
                    if (element) {
                        element.click();
                        return true;
                    }
                    return false;
                """
                
                # 좌표 변환
                x_rel = int(self.driver.execute_script("return window.innerWidth") * (close_x / 1920))
                y_rel = int(self.driver.execute_script("return window.innerHeight") * (close_y / 1080))
                
                result = self.driver.execute_script(js_click_script, x_rel, y_rel)
                if result:
                    logging.info("자동화 알림을 성공적으로 닫았습니다.")
                    return True
                else:
                    logging.warning("알림 닫기 버튼을 클릭할 수 없습니다.")
                    return False
            else:
                logging.info("표시된 알림이 없습니다.")
                return True
                
        except Exception as e:
            logging.error(f"알림 닫기 중 오류 발생: {e}")
            return False
            
    def close_password_save_modal(self):
        """
        비밀번호를 저장하시겠습니까 모달창 닫기 - 순수 JavaScript 방식으로 변경
        
        Returns:
            dict: 처리 결과 정보
        """
        # 이미 처리된 경우 중복 처리 방지
        if self.password_save_modal_closed:
            logging.info("비밀번호 저장 모달창은 이미 닫혔습니다. 중복 처리를 방지합니다.")
            return {"success": True, "method": "already_closed"}
            
        try:
            # 1. 비밀번호 저장 관련 모달창 확인 - 여러 방법 시도
            logging.info("비밀번호 저장 모달창 확인 중...")
            
            # JavaScript로 모달창 감지 (다양한 선택자 활용)
            modal_check_script = """
                return {
                    chromeModal: document.querySelector('div[id^="chrome-"]') !== null || 
                                 document.querySelector('.enable-password-saving') !== null,
                    genericModal: document.querySelector('div[role="dialog"]') !== null,
                    visibleModal: Array.from(document.querySelectorAll('div')).some(
                        div => div.style.zIndex > 1000 && 
                              div.style.position === 'fixed' && 
                              div.style.display !== 'none' && 
                              div.offsetWidth > 0 && 
                              div.offsetHeight > 0 && 
                              window.getComputedStyle(div).visibility !== 'hidden' &&
                              div.textContent.includes('비밀번호')
                    )
                };
            """
            
            modal_check_result = self.driver.execute_script(modal_check_script)
            logging.info(f"모달창 확인 결과: {modal_check_result}")
            
            modal_exists = (
                modal_check_result.get("chromeModal", False) or 
                modal_check_result.get("genericModal", False) or 
                modal_check_result.get("visibleModal", False)
            )
            
            if not modal_exists:
                logging.info("표시된 비밀번호 저장 모달창이 없습니다.")
                
                # 모달창이 없어도 설정은 적용 (쿠키 및 localStorage 설정)
                storage_result = self.set_password_save_preferences()
                
                self.password_save_modal_closed = True
                return {
                    "success": True, 
                    "modal_found": False,
                    "storage": storage_result.get("storage", "not_set"),
                    "storage_success": storage_result.get("success", False),
                    "method": "no_modal_found"
                }
            
            # 2. 모달창이 감지된 경우 닫기 시도
            logging.info("비밀번호 저장 모달창이 감지되었습니다. 닫기 처리를 시작합니다.")
            
            # 2.1 ESC 키 시도
            logging.info("ESC 키를 사용하여 모달창 닫기 시도")
            self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
            time.sleep(0.5)
            
            # 2.2 "나중에" 또는 "취소" 버튼 클릭 시도
            try:
                # 다양한 선택자로 버튼 시도
                for selector in [
                    "//button[contains(text(), '나중에')]",
                    "//button[contains(text(), '취소')]",
                    "//button[contains(text(), '아니오')]",
                    "//button[contains(@class, 'negative')]",
                    "//button[contains(@class, 'secondary')]"
                ]:
                    try:
                        button = WebDriverWait(self.driver, 1).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        button.click()
                        logging.info(f"'{selector}' 버튼 클릭 성공")
                        time.sleep(0.5)
                        break
                    except:
                        continue
            except Exception as e:
                logging.warning(f"버튼 클릭 실패: {e}")
            
            # 2.3 절대좌표 기반 클릭 시도 (마지막 수단)
            logging.info("절대좌표를 사용하여 모달창 닫기 시도")
            close_x, close_y = NOTIFICATION["PASSWORD_SAVE_MODAL_CLOSE"]
            
            # JavaScript로 클릭 시도
            js_click_script = """
                var element = document.elementFromPoint(arguments[0], arguments[1]);
                if (element) {
                    element.click();
                    return {
                        tag: element.tagName,
                        text: element.textContent.trim(),
                        id: element.id,
                        class: element.className
                    };
                }
                return null;
            """
            
            # 좌표 변환
            x_rel = int(self.driver.execute_script("return window.innerWidth") * (close_x / 1920))
            y_rel = int(self.driver.execute_script("return window.innerHeight") * (close_y / 1080))
            
            clicked_element = self.driver.execute_script(js_click_script, x_rel, y_rel)
            if clicked_element:
                logging.info(f"절대좌표 클릭 성공: ({x_rel}, {y_rel})")
                logging.info(f"클릭된 요소: [{clicked_element['tag']}] '{clicked_element['text']}'" + 
                         (f" ID: {clicked_element['id']}" if clicked_element['id'] else "") + 
                         (f" CLASS: {clicked_element['class']}" if clicked_element['class'] else ""))
            else:
                logging.warning(f"지정된 좌표 ({x_rel}, {y_rel})에서 요소를 찾을 수 없습니다.")
            
            # 3. 설정 적용 (localStorage, 쿠키 등)
            storage_result = self.set_password_save_preferences()
            
            # 4. 모달창 재확인
            time.sleep(0.5)
            modal_check_result_after = self.driver.execute_script(modal_check_script)
            modal_exists_after = (
                modal_check_result_after.get("chromeModal", False) or 
                modal_check_result_after.get("genericModal", False) or 
                modal_check_result_after.get("visibleModal", False)
            )
            
            if not modal_exists_after:
                logging.info("비밀번호 저장 모달창이 성공적으로 닫혔습니다.")
                success = True
            else:
                logging.warning("비밀번호 저장 모달창이 여전히 표시되고 있습니다.")
                success = False
            
            self.password_save_modal_closed = True
            return {
                "success": success,
                "modal_found": True,
                "modal_closed": not modal_exists_after,
                "storage": storage_result.get("storage", "not_set"),
                "storage_success": storage_result.get("success", False),
                "method": "modal_close_attempt"
            }
            
        except Exception as e:
            logging.error(f"비밀번호 저장 모달창 처리 중 오류 발생: {e}")
            logging.error(traceback.format_exc())
            return {"success": False, "error": str(e), "method": "error"}
            
    def set_password_save_preferences(self):
        """
        비밀번호 저장 관련 브라우저 설정 적용
        
        Returns:
            dict: 설정 적용 결과
        """
        try:
            # localStorage 및 쿠키 설정
            js_script = """
                try {
                    // 비밀번호 저장 관련 설정
                    localStorage.setItem('passwordSavePreference', 'denied');
                    localStorage.setItem('chrome_pwm_visible', 'false');
                    
                    // 쿠키 설정
                    document.cookie = "passwordSavePreference=denied; path=/; max-age=31536000";
                    document.cookie = "pwm_dismiss=true; path=/; max-age=31536000";
                    
                    return { storage: 'set', success: true };
                } catch (e) {
                    return { storage: 'error', success: false, error: e.toString() };
                }
            """
            
            result = self.driver.execute_script(js_script)
            logging.info(f"비밀번호 저장 관련 설정 적용 결과: {result}")
            return result
            
        except Exception as e:
            logging.error(f"비밀번호 저장 설정 적용 중 오류 발생: {e}")
            return {"storage": "exception", "success": False, "error": str(e)}
            
    def close_login_modal(self):
        """
        로그인 후 나타나는 모달창 차단 - 강화된 종합적 차단 방식 적용
        '다시 보지 않기' 버튼을 smart_click으로 처리하고, 실패 시 hide_login_modal 활용
        
        Returns:
            dict: 처리 결과 정보
        """
        # 이미 처리된 경우 중복 처리 방지
        if self.login_modal_closed:
            logging.info("로그인 모달창은 이미 닫혔습니다. 중복 처리를 방지합니다.")
            return {"success": True, "method": "already_closed"}
            
        try:
            from ui_elements import LOGIN_UI_ELEMENTS
            from selenium.webdriver.common.by import By
            from selenium.common.exceptions import NoSuchElementException, TimeoutException
            
            # 1. '다시 보지 않기' 버튼 직접 클릭 시도
            logging.info("'다시 보지 않기' 버튼 클릭 시도")
            dont_show_again_element = LOGIN_UI_ELEMENTS["DONT_SHOW_AGAIN"]
            
            # 직접 DOM 선택자로 시도
            try:
                xpath = dont_show_again_element["dom_selector"]
                button = self.driver.find_element(By.XPATH, xpath)
                button.click()
                click_result = {'success': True, 'method': 'dom_click'}
                logging.info(f"'다시 보지 않기' 버튼 DOM 클릭 성공")
            except (NoSuchElementException, TimeoutException) as e:
                logging.warning(f"'다시 보지 않기' 버튼 DOM 클릭 실패: {e}")
                
                # 좌표로 시도
                try:
                    coords = dont_show_again_element["coordinates"]
                    logging.info(f"'다시 보지 않기' 버튼 좌표 클릭 시도: {coords}")
                    
                    js_script = f"""
                    var el = document.elementFromPoint({coords[0]}, {coords[1]});
                    if (el) {{
                        el.click();
                        return {{
                            clicked: true,
                            tagName: el.tagName,
                            textContent: el.textContent,
                            className: el.className
                        }};
                    }} else {{
                        return {{ clicked: false }};
                    }}
                    """
                    
                    click_result = self.driver.execute_script(js_script)
                    if click_result and click_result.get('clicked', False):
                        logging.info(f"'다시 보지 않기' 버튼 좌표 클릭 성공: {{clicked: {click_result}}}")
                        click_result['success'] = True
                        click_result['method'] = 'coord_click'
                    else:
                        logging.warning(f"'다시 보지 않기' 버튼 좌표 클릭 실패")
                        click_result = {'success': False, 'method': 'coord_click_failed'}
                except Exception as e:
                    logging.warning(f"'다시 보지 않기' 버튼 좌표 클릭 오류: {e}")
                    click_result = {'success': False, 'method': 'error', 'error': str(e)}
            except Exception as e:
                logging.warning(f"'다시 보지 않기' 버튼 클릭 중 오류: {e}")
                click_result = {'success': False, 'method': 'error', 'error': str(e)}
            
            if click_result.get("success", False):
                logging.info(f"'다시 보지 않기' 버튼 클릭 성공: {click_result}")
                time.sleep(0.5)  # 클릭 후 잠시 대기
                self.login_modal_closed = True
                return {"success": True, "method": click_result.get("method", "click"), "details": click_result}
            else:
                logging.warning(f"'다시 보지 않기' 버튼 클릭 실패: {click_result}")
            
            # 2. smart_click 실패 시 기존 방식 사용 (hide_login_modal)
            logging.info("hide_login_modal 함수로 대체 시도")
            result = hide_login_modal(self.driver)
            
            # 성공 여부에 관계없이 플래그 설정 (중복 호출 방지)
            self.login_modal_closed = True
            
            return result
            
        except Exception as e:
            logging.error(f"로그인 모달창 처리 중 오류 발생: {e}")
            logging.error(traceback.format_exc())
            return {"success": False, "error": str(e), "method": "error"}
            
    def hide_channel_talk(self):
        """
        채널톡 숨기기 적용
        
        Returns:
            dict: 처리 결과 정보
        """
        # 이미 처리된 경우 중복 처리 방지
        if self.channel_talk_hidden:
            logging.info("채널톡은 이미 숨겨졌습니다. 중복 처리를 방지합니다.")
            return {"success": True, "method": "already_hidden"}
            
        try:
            # 기존 모듈 활용 (check_and_hide_channel_talk)
            logging.info("채널톡 숨기기 적용 - 확인 과정 포함")
            result = check_and_hide_channel_talk(self.driver)
            
            # 성공 여부에 관계없이 플래그 설정 (중복 호출 방지)
            self.channel_talk_hidden = True
            
            return result
            
        except Exception as e:
            logging.error(f"채널톡 숨기기 중 오류 발생: {e}")
            logging.error(traceback.format_exc())
            return {"success": False, "error": str(e), "method": "error"}
            


    def handle_all_modals(self):
        """
        모든 모달창 처리 - 통합 처리 함수
        
        Returns:
            dict: 전체 처리 결과 정보
        """
        results = {}
        
        # 1. 비밀번호 저장 모달창 처리
        password_modal_result = self.close_password_save_modal()
        results["password_modal"] = password_modal_result
        
        # 2. 로그인 모달창 처리
        login_modal_result = self.close_login_modal()
        results["login_modal"] = login_modal_result
        
        # 3. 채널톡 숨기기
        channel_talk_result = self.hide_channel_talk()
        results["channel_talk"] = channel_talk_result
        
        # 전체 성공 여부 확인
        overall_success = (
            password_modal_result.get("success", False) and
            login_modal_result.get("success", False) and
            channel_talk_result.get("success", False)
        )
        
        results["overall_success"] = overall_success
        
        logging.info(f"모든 모달창 처리 완료: {overall_success}")
        return results
        

