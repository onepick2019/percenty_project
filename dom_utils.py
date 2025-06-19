# -*- coding: utf-8 -*-
"""
DOM 요소 조작 유틸리티

이 모듈은 DOM 기반 요소 선택 및 좌표 기반 선택을 모두 지원하는 하이브리드 접근 방식을 제공합니다.
"""
import logging
import time
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from timesleep import *
from ui_elements import KEYBOARD_ACTIONS

# 좌표 변환 모듈 임포트
from coordinates.coordinate_conversion import convert_coordinates as _original_convert_coordinates

# 좌표 변환 함수 오버라이드 - 모든 호출 형식을 한 가지로 통일
# 호환성을 위해 3개의 인자를 받는 경우와 4개의 인자를 받는 경우 모두 처리
def convert_coordinates(*args):
    """
    좌표 변환 함수 - 비선형 변환 적용
    인자 형식에 따라 적절한 변환 적용
    
    Args:
        x, y: 절대좌표
        inner_width, inner_height 또는 driver
    
    Returns:
        tuple: 변환된 (x, y) 좌표
    """
    # 인자 수에 따른 처리
    if len(args) == 3:  # (x, y, driver) 형식으로 호출된 경우
        x, y, driver = args
        inner_width = driver.execute_script("return window.innerWidth;")
        inner_height = driver.execute_script("return window.innerHeight;")
        logging.info(f"Driver로부터 브라우저 크기 가져옴: {inner_width}x{inner_height}")
    elif len(args) == 4:  # (x, y, inner_width, inner_height) 형식으로 호출된 경우
        x, y, inner_width, inner_height = args
    else:
        logging.error(f"지원하지 않는 인자 수: {len(args)}")
        return 0, 0
    
    # 원본 비선형 변환 함수 호출
    result = _original_convert_coordinates(x, y, inner_width, inner_height)
    logging.info(f"비선형 좌표 변환 적용: ({x}, {y}) -> {result} [브라우저: {inner_width}x{inner_height}]")
    return result

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 상수 정의
WAIT_TIMEOUT = 10  # DOM 요소 대기 시간(초)
ELEMENT_SCROLL_DELAY = INPUT_FIELD["AFTER_CLICK_VERYSHORT5"]  # 요소로 스크롤 후 대기 시간 (0.5초)

# 전역 변수 - 채널톡 상태 관리
CHANNEL_TALK_ALREADY_CLOSED = False

def sleep_with_logging(duration, message=None):
    """
    지정된 시간 동안 대기하며 로깅합니다.
    
    Args:
        duration: 대기 시간(초)
        message: 로깅할 메시지 (기본값: None)
    """
    if message:
        logging.info(f"{message} - {duration}초 대기")
    time.sleep(duration)

def convert_to_selenium_by(selector_type):
    """
    선택자 타입 문자열을 Selenium By 클래스 상수로 변환합니다.
    
    Args:
        selector_type: 'css', 'xpath', 'id', 'class' 등의 선택자 타입 문자열
    
    Returns:
        By 클래스 상수 (By.CSS_SELECTOR, By.XPATH 등)
    """
    if selector_type == 'css':
        return By.CSS_SELECTOR
    elif selector_type == 'xpath':
        return By.XPATH
    elif selector_type == 'id':
        return By.ID
    elif selector_type == 'class':
        return By.CLASS_NAME
    else:
        logging.error(f"지원되지 않는 선택자 타입: {selector_type}")
        return None

def smart_click(driver, element_info, element_name=None, browser_core=None, click_type=None, input_text=None):
    """
    DOM 선택자, 좌표 또는 키보드 액션을 사용하여 요소를 클릭하거나 키보드 액션을 수행합니다.
    필요에 따라 텍스트 입력도 지원합니다.
    
    Args:
        driver: Selenium WebDriver 인스턴스
        element_info: 디셔너리 타입으로 다음 중 하나를 포함해야 함:
            - 'coordinates': (x, y) 튜플 - 절대좌표
            - 'dom_selector': 선택자 문자열 - DOM 선택자
            - 'selector_type': 선택자 타입 (xpath, css, id 등)
        element_name: 요소의 이름 (로깅용, 선택 사항)
        browser_core: BrowserCore 인스턴스 (좌표 클릭에 사용, 선택 사항)
        click_type: 클릭 타입 ('click' 또는 'input', 기본값: 'click')
        input_text: 입력할 텍스트 (click_type이 'input'일 때 사용)
    
    Returns:
        dict: 결과 정보 (성공 여부, 사용된 방법, 오류 메시지 등)
    """
    # 기본 결과 설정
    result = {
        "success": False,
        "method": None,
        "error": None
    }
    
    # 기본값 설정
    if click_type is None:
        click_type = "click"
    
    # 요소 이름 설정 (로깅용)
    desc = element_name if element_name else element_info.get("description", "unknown element")
    
    try:
        # fallback_order가 있는지 확인
        fallback_order = element_info.get("fallback_order", [])
        
        # fallback_order가 없으면 기본 처리 순서 설정
        if not fallback_order:
            if "dom_selector" in element_info:
                fallback_order.append("dom")
            if "coordinates" in element_info:
                fallback_order.append("coordinates")
        
        # 각 방법 순서대로 시도
        for method in fallback_order:
            try:
                if method == "dom":
                    # DOM 선택자로 시도
                    if "dom_selector" in element_info and "selector_type" in element_info:
                        selector_type = element_info["selector_type"]
                        selector_value = element_info["dom_selector"]
                        
                        by = convert_to_selenium_by(selector_type)
                        if by is None:
                            continue  # 선택자 타입이 유효하지 않음
                        
                        # 요소 찾기
                        element = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((by, selector_value))
                        )
                        
                        if click_type == "click":
                            # 클릭 수행
                            element.click()
                            logging.info(f"{desc} - DOM 선택자로 클릭 성공")
                            result["success"] = True
                            result["method"] = "dom_click"
                            return result
                            
                        elif click_type == "input" and input_text is not None:
                            # 텍스트 입력
                            element.clear()
                            element.send_keys(input_text)
                            logging.info(f"{desc} - DOM 선택자로 텍스트 입력 성공: {input_text}")
                            result["success"] = True
                            result["method"] = "dom_input"
                            return result
                            
                elif method == "coordinates" and "coordinates" in element_info:
                    # 좌표 기반으로 시도
                    x, y = element_info["coordinates"]
                    
                    if browser_core is not None:
                        # browser_core를 사용한 클릭
                        if click_type == "click":
                            click_success = browser_core.click_at_coordinates(x, y, desc)
                            if click_success:
                                logging.info(f"{desc} - 좌표 기반 클릭 성공 (browser_core): ({x}, {y})")
                                result["success"] = True
                                result["method"] = "coordinates_click_browser_core"
                                return result
                        elif click_type == "input" and input_text is not None:
                            # 좌표 클릭 후 텍스트 입력
                            click_success = browser_core.click_at_coordinates(x, y, desc)
                            if click_success:
                                # 클릭 후 JavaScript로 텍스트 입력
                                active_element = driver.switch_to.active_element
                                active_element.clear()
                                active_element.send_keys(input_text)
                                logging.info(f"{desc} - 좌표 기반 클릭 후 텍스트 입력 성공: {input_text}")
                                result["success"] = True
                                result["method"] = "coordinates_input_browser_core"
                                return result
                    else:
                        # 기본 selenium 기반 좌표 클릭
                        if click_type == "click":
                            click_success = click_at_absolute_coordinates(driver, x, y, desc)
                            if click_success:
                                logging.info(f"{desc} - 좌표 기반 클릭 성공: ({x}, {y})")
                                result["success"] = True
                                result["method"] = "coordinates_click"
                                return result
                        elif click_type == "input" and input_text is not None:
                            # 좌표 클릭 후 텍스트 입력
                            click_success = click_at_absolute_coordinates(driver, x, y, desc)
                            if click_success:
                                # 클릭 후 JavaScript로 텍스트 입력
                                active_element = driver.switch_to.active_element
                                active_element.clear()
                                active_element.send_keys(input_text)
                                logging.info(f"{desc} - 좌표 기반 클릭 후 텍스트 입력 성공: {input_text}")
                                result["success"] = True
                                result["method"] = "coordinates_input"
                                return result
                            
            except Exception as method_error:
                logging.warning(f"{desc} - {method} 방식 시도 실패: {method_error}")
                continue
        
        # 모든 방법 실패
        error_msg = f"{desc} - 모든 방법이 실패했습니다 (fallback_order: {fallback_order})"
        logging.error(error_msg)
        result["error"] = error_msg
        return result
        
    except Exception as e:
        error_msg = f"{element_name or '알 수 없는 요소'} - smart_click 중 오류 발생: {e}"
        logging.error(error_msg)
        result["error"] = error_msg
        return result

def highlight_element(driver, element_info, duration=2):
    """
    DOM 요소 또는 좌표 위치를 강조 표시합니다(디버깅용)
    
    Args:
        driver: Selenium WebDriver 인스턴스
        element_info: 딕셔너리 타입으로 다음 중 하나를 포함해야 함:
            - 'coordinates': (x, y) 튜플 - 절대좌표
            - 'selector': (selector_type, selector_value) 튜플 - DOM 선택자
        duration: 강조 표시 지속 시간(초)
    """
    try:
        # 좌표 기반 강조 표시
        if 'coordinates' in element_info:
            x, y = element_info['coordinates']
            logging.info(f"좌표 위치 강조 표시: ({x}, {y})")
            
            # 브라우저 내부 크기 가져오기
            inner_width = driver.execute_script("return window.innerWidth")
            inner_height = driver.execute_script("return window.innerHeight")
            
            # 좌표 변환 (1920x1080 기준으로 상대 변환)
            relative_x, relative_y = convert_coordinates(x, y, driver)
            
            # 좌표 위치에 임시 요소 생성 및 강조 표시
            driver.execute_script(f"""
                const markerDiv = document.createElement('div');
                markerDiv.style.position = 'absolute';
                markerDiv.style.left = '{relative_x}px';
                markerDiv.style.top = '{relative_y}px';
                markerDiv.style.width = '20px';
                markerDiv.style.height = '20px';
                markerDiv.style.borderRadius = '50%';
                markerDiv.style.backgroundColor = 'red';
                markerDiv.style.zIndex = '9999';
                markerDiv.style.transform = 'translate(-50%, -50%)';
                document.body.appendChild(markerDiv);
                
                // 애니메이션 효과
                let opacity = 1;
                const fadeInterval = setInterval(() => {{
                    opacity -= 0.05;
                    markerDiv.style.opacity = opacity;
                    if (opacity <= 0) {{
                        clearInterval(fadeInterval);
                        document.body.removeChild(markerDiv);
                    }}
                }}, 100);
            """)
            
        # DOM 선택자 기반 강조 표시
        elif 'selector' in element_info:
            selector_type, selector_value = element_info['selector']
            logging.info(f"DOM 요소 강조 표시: {selector_type}={selector_value}")
            
            by_type = convert_to_selenium_by(selector_type)
            if not by_type:
                return
            
            try:
                element = WebDriverWait(driver, WAIT_TIMEOUT).until(
                    EC.presence_of_element_located((by_type, selector_value))
                )
                
                # 스크롤하여 요소가 보이게 함
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                time.sleep(ELEMENT_SCROLL_DELAY)
                
                # 요소 강조 표시
                original_style = driver.execute_script("return arguments[0].getAttribute('style');", element)
                driver.execute_script("""
                    arguments[0].setAttribute('style', arguments[1] + 'border: 2px solid red; background-color: rgba(255, 0, 0, 0.2);');
                """, element, original_style if original_style else "")
                
                # 지정된 시간 후 원래 스타일로 복원
                time.sleep(duration)
                if original_style:
                    driver.execute_script("arguments[0].setAttribute('style', arguments[1]);", element, original_style)
                else:
                    driver.execute_script("arguments[0].removeAttribute('style');", element)
                
            except TimeoutException:
                logging.warning(f"강조 표시할 요소를 찾을 수 없음: {selector_type}={selector_value}")
            except Exception as e:
                logging.error(f"DOM 요소 강조 표시 오류: {e}")
        
        else:
            logging.error(f"강조 표시 정보가 올바르지 않음: {element_info}")
            
    except Exception as e:
        logging.error(f"highlight_element 함수 오류: {e}")

def wait_for_element(driver, selector_type, selector_value, timeout=WAIT_TIMEOUT, visible=True):
    """
    DOM 요소가 존재하거나 보일 때까지 대기합니다.
    
    Args:
        driver: Selenium WebDriver 인스턴스
        selector_type: 'css', 'xpath', 'id', 'class' 등의 선택자 타입 문자열
        selector_value: 선택자 값
        timeout: 최대 대기 시간(초)
        visible: True면 요소가 보일 때까지 대기, False면 요소가 존재할 때까지만 대기
    
    Returns:
        존재하거나 보이는 요소 또는 None
    """
    by_type = convert_to_selenium_by(selector_type)
    if not by_type:
        return None
    
    try:
        if visible:
            element = WebDriverWait(driver, timeout).until(
                EC.visibility_of_element_located((by_type, selector_value))
            )
            logging.info(f"요소가 보임: {selector_type}={selector_value}")
        else:
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by_type, selector_value))
            )
            logging.info(f"요소가 존재함: {selector_type}={selector_value}")
        return element
    except TimeoutException:
        logging.warning(f"요소 대기 시간 초과: {selector_type}={selector_value}")
        return None
    except Exception as e:
        logging.error(f"요소 대기 중 오류 발생: {e}")
        return None

def is_element_present(driver, selector_type, selector_value, timeout=3):
    """
    DOM 요소가 존재하는지 확인합니다.
    
    Args:
        driver: Selenium WebDriver 인스턴스
        selector_type: 'css', 'xpath', 'id', 'class' 등의 선택자 타입 문자열
        selector_value: 선택자 값
        timeout: 최대 대기 시간(초)
    
    Returns:
        bool: 요소가 존재하면 True, 그렇지 않으면 False
    """
    element = wait_for_element(driver, selector_type, selector_value, timeout, visible=False)
    return element is not None

def is_element_visible(driver, selector_type, selector_value, timeout=3):
    """
    DOM 요소가 보이는지 확인합니다.
    
    Args:
        driver: Selenium WebDriver 인스턴스
        selector_type: 'css', 'xpath', 'id', 'class' 등의 선택자 타입 문자열
        selector_value: 선택자 값
        timeout: 최대 대기 시간(초)
    
    Returns:
        bool: 요소가 보이면 True, 그렇지 않으면 False
    """
    element = wait_for_element(driver, selector_type, selector_value, timeout, visible=True)
    return element is not None

def fill_input_field(driver, selector_type, selector_value, text, clear_first=True):
    """
    입력 필드에 텍스트를 입력합니다.
    
    Args:
        driver: Selenium WebDriver 인스턴스
        selector_type: 'css', 'xpath', 'id', 'class' 등의 선택자 타입 문자열
        selector_value: 선택자 값
        text: 입력할 텍스트
        clear_first: 입력 전에 필드를 지울지 여부
    
    Returns:
        bool: 입력 성공 여부
    """
    element = wait_for_element(driver, selector_type, selector_value)
    if not element:
        return False
    
    try:
        # 스크롤하여 요소가 보이게 함
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(ELEMENT_SCROLL_DELAY)
        
        # 입력 필드 클릭
        element.click()
        
        # 필요한 경우 기존 텍스트 지우기
        if clear_first:
            element.clear()
        
        # 텍스트 입력
        element.send_keys(text)
        logging.info(f"텍스트 입력 성공: {text}")
        
        # 입력 후 짧은 대기
        sleep_with_logging(INPUT_FIELD["AFTER_INPUT"], "텍스트 입력 후 대기")
        return True
    except Exception as e:
        logging.error(f"텍스트 입력 중 오류 발생: {e}")
        return False

def click_at_absolute_coordinates(driver, x, y, click_description=None):
    """
    절대 좌표를 사용하여 클릭합니다.
    
    Args:
        driver: Selenium WebDriver 인스턴스
        x: X 좌표 (절대)
        y: Y 좌표 (절대)
        click_description: 클릭 작업 설명 (로깅용)
    
    Returns:
        bool: 클릭 성공 여부
    """
    desc = click_description if click_description else f"좌표 ({x}, {y})"
    
    try:
        # 브라우저 내부 크기 가져오기
        inner_width = driver.execute_script("return window.innerWidth")
        inner_height = driver.execute_script("return window.innerHeight")
        
        # 좌표 변환 - 비선형 변환 적용
        relative_x, relative_y = convert_coordinates(x, y, inner_width, inner_height)
        logging.info(f"비선형 변환 함수 적용 - 위치별 가중치 배수 적용")
        
        logging.info(f"{desc} 절대좌표 클릭 시도: ({x}, {y}) -> 변환: ({relative_x}, {relative_y})")
        
        # JavaScript를 사용하여 강화된 클릭
        click_result = driver.execute_script("""
            const element = document.elementFromPoint(arguments[0], arguments[1]);
            if (element) {
                // 요소 정보 수집
                const elementInfo = {
                    tagName: element.tagName,
                    className: element.className || '',
                    id: element.id || '',
                    type: element.type || '',
                    checked: element.checked,
                    disabled: element.disabled
                };
                
                // 체크박스인 경우 특별 처리
                if (element.type === 'checkbox') {
                    const wasChecked = element.checked;
                    
                    // 1. 일반 클릭 시도
                    element.click();
                    
                    // 2. 상태가 변경되지 않았으면 강제로 변경
                    if (element.checked === wasChecked) {
                        element.checked = !wasChecked;
                        
                        // 3. 이벤트 발생시키기
                        const changeEvent = new Event('change', { bubbles: true });
                        const clickEvent = new Event('click', { bubbles: true });
                        element.dispatchEvent(changeEvent);
                        element.dispatchEvent(clickEvent);
                    }
                    
                    elementInfo.finalChecked = element.checked;
                    elementInfo.stateChanged = (element.checked !== wasChecked);
                } else {
                    // 일반 요소 클릭
                    element.click();
                    
                    // 클릭 이벤트 강제 발생
                    const clickEvent = new Event('click', { bubbles: true });
                    element.dispatchEvent(clickEvent);
                }
                
                return {
                    success: true,
                    ...elementInfo
                };
            } else {
                return { success: false };
            }
        """, relative_x, relative_y)
        
        if click_result and click_result.get('success'):
            element_info = f"태그: {click_result.get('tagName', 'unknown')}, 클래스: {click_result.get('className', 'none')}, ID: {click_result.get('id', 'none')}"
            
            # 체크박스인 경우 상태 변경 확인
            if click_result.get('type') == 'checkbox':
                state_changed = click_result.get('stateChanged', False)
                final_checked = click_result.get('finalChecked', False)
                logging.info(f"{desc} 체크박스 클릭 - 상태변경: {state_changed}, 최종상태: {final_checked}")
                
                if not state_changed:
                    logging.warning(f"{desc} 체크박스 클릭했지만 상태가 변경되지 않음")
            
            logging.info(f"{desc} 클릭 성공! 클릭된 요소: {element_info}")
            
            # 클릭 후 대기
            sleep_with_logging(BUTTON_CLICK["STANDARD"], f"{desc} 클릭 후 대기")
            return True
        else:
            logging.warning(f"{desc} 클릭 실패: 좌표에 요소가 없음")
            return False
            
    except Exception as e:
        logging.error(f"{desc} 클릭 중 오류 발생: {e}")
        return False

# 채널톡 관련 함수는 channel_talk_utils.py로 이동되었습니다.
# 이전 코드와의 호환성을 위해 임시로 함수 시그니처만 유지
def keyboard_action(driver, action_key, element_name=None):
    """
    키보드 액션을 실행합니다.
    
    Args:
        driver: Selenium WebDriver 인스턴스
        action_key: 액션 키 이름 ('escape_key', 'tab_key', 'enter_key' 등)
        element_name: 요소 이름 (로깅용, 선택 사항)
    
    Returns:
        bool: 키보드 액션 성공 여부
    """
    try:
        # UI_ELEMENTS에서 키보드 액션 정보 가져오기
        if action_key not in KEYBOARD_ACTIONS:
            logging.error(f"지원되지 않는 키보드 액션: {action_key}")
            return False
        
        key_info = KEYBOARD_ACTIONS[action_key]
        key = getattr(Keys, key_info["key"].upper())
        delay = key_info.get("delay", KEYBOARD_ACTION["AFTER_KEY"])
        
        # 요소 설명(로깅용)
        desc = element_name if element_name else key_info["description"]
        
        logging.info(f"{desc} - 키보드 액션 실행: {action_key}")
        
        # 활성화된 요소가 있는 경우 해당 요소에 키 전송
        try:
            active_element = driver.switch_to.active_element
            active_element.send_keys(key)
            logging.info(f"{desc} - 활성화된 요소에 키 전송 성공")
        except:
            # 활성화된 요소가 없는 경우 ActionChains 사용
            ActionChains(driver).send_keys(key).perform()
            logging.info(f"{desc} - ActionChains를 통한 키 전송 성공")
        
        # 키보드 액션 후 적절한 대기
        if action_key == "escape_key":
            wait_after_escape_key()
        elif action_key == "tab_key":
            wait_after_tab_key()
        elif action_key == "enter_key":
            wait_after_enter_key()
        else:
            # 기본 키보드 액션 대기
            wait_after_keyboard_action(key_info["description"])
            
        return True
        
    except Exception as e:
        logging.error(f"{element_name if element_name else action_key} - 키보드 액션 중 오류 발생: {e}")
        return False

def check_and_hide_channel_talk(driver, timeout=5):
    """
    channel_talk_utils.py로 이동된 함수입니다.
    이전 코드와의 호환성을 위해 임시로 유지합니다.
    
    Args:
        driver: Selenium WebDriver 인스턴스
        timeout: 최대 대기 시간(초)
    
    Returns:
        bool: 채널톡 숨김 성공 여부
    """
    global CHANNEL_TALK_ALREADY_CLOSED
    
    # 이미 닫혀 있는 경우 중복 실행 방지
    if CHANNEL_TALK_ALREADY_CLOSED:
        logging.info("채널톡이 이미 닫혀 있습니다. 추가 닫기 시도를 건너뛵니다.")
        return True
    
    logging.info("채널톡 처리 함수가 channel_talk_utils.py로 이동되었습니다. 해당 모듈을 임포트하세요.")
    # 이 함수를 channel_talk_utils에서 임포트하도록 코드를 수정하세요
    try:
        from channel_talk_utils import check_and_hide_channel_talk as new_check_and_hide_channel_talk
        return new_check_and_hide_channel_talk(driver, timeout)
    except ImportError:
        logging.error("channel_talk_utils.py 모듈을 찾을 수 없습니다.")
        return False
    except Exception as e:
        logging.error(f"채널톡 처리 중 오류: {e}")
        return False
