"""
하이브리드 클릭 유틸리티 (click_utils.py)
DOM 선택자와 좌표 기반 클릭을 순차적으로 시도하는 통합 함수 제공
"""
import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException
from coordinates.coordinates_all import get_converted_coordinates
from timesleep import sleep_with_logging

# 로그 레벨 설정 - DOM 선택자 시도 로그가 항상 기록되도록 INFO 레벨로 설정

logger = logging.getLogger(__name__)

def hybrid_click(driver, element_key, delay=2.0, browser_ui_height=95):
    """
    UI 요소를 클릭하는 하이브리드 함수 - DOM 선택자와 좌표를 순차적으로 시도
    
    Args:
        driver: Selenium WebDriver 인스턴스
        element_key: ui_elements.py에 정의된 UI 요소 키
        delay: 클릭 후 대기 시간(초)
        browser_ui_height: 브라우저 UI 높이 보정값
    
    Returns:
        bool: 클릭 성공 여부
    """
    from ui_elements import UI_ELEMENTS
    
    # UI 요소 정보 가져오기
    if element_key not in UI_ELEMENTS:
        logger.error(f"정의되지 않은 UI 요소: {element_key}")
        return False
    
    element_info = UI_ELEMENTS[element_key]
    element_name = element_info["name"]
    fallback_order = element_info.get("fallback_order", ["dom", "coordinates"])
    
    logger.info(f"{element_name} 요소 클릭 시도 - 하이브리드 방식")
    
    # 시도 순서에 따라 클릭 방식 적용
    for method in fallback_order:
        if method == "dom":
            # DOM 선택자 방식 시도
            dom_selector = element_info.get("dom_selector")
            selector_type = element_info.get("selector_type", "xpath")
            
            if not dom_selector:
                logger.info(f"{element_name} 요소에 DOM 선택자가 정의되지 않음, 다음 방식 시도")
                continue
                
            try:
                logger.info(f"{element_name} DOM 선택자 클릭 시도: {dom_selector}")
                

                
                # 선택자 타입 매핑
                by_mapping = {
                    "xpath": By.XPATH,
                    "css": By.CSS_SELECTOR,
                    "id": By.ID,
                    "name": By.NAME,
                    "class": By.CLASS_NAME,
                }
                by_type = by_mapping.get(selector_type.lower(), By.XPATH)
                
                # 요소 찾기 및 클릭
                element = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((by_type, dom_selector))
                )
                
                # JavaScript로 강제 클릭 시도 (element click intercepted 문제 해결)
                try:
                    driver.execute_script("arguments[0].click();", element)
                    logger.info(f"{element_name} DOM 선택자 JavaScript 클릭 성공")
                except Exception as js_e:
                    logger.warning(f"JavaScript 클릭 실패, 일반 클릭 시도: {js_e}")
                    element.click()
                
                logger.info(f"{element_name} DOM 선택자 클릭 성공")
                sleep_with_logging(delay, f"{element_name} 클릭 후 대기")
                return True
                
            except Exception as e:
                logger.warning(f"{element_name} DOM 선택자 클릭 실패: {e}")
                logger.info("좌표 기반 방식으로 시도합니다.")
        
        elif method == "coordinates":
            # 좌표 기반 방식 시도
            coordinates = element_info.get("coordinates")
            
            if not coordinates:
                logger.info(f"{element_name} 요소에 좌표가 정의되지 않음, 다음 방식 시도")
                continue
                
            try:
                logger.info(f"{element_name} 좌표 클릭 시도: {coordinates}")
                
                # 좌표 변환 (절대좌표 -> 상대좌표)
                # coordinate_conversion.py의 비선형 변환 함수 사용
                inner_width = driver.execute_script("return window.innerWidth")
                inner_height = driver.execute_script("return window.innerHeight")
                rel_x, rel_y = get_converted_coordinates(
                    coordinates[0], coordinates[1], inner_width, inner_height
                )
                logger.info(f"비선형 변환 적용된 좌표: ({rel_x}, {rel_y}) - 원본 좌표: {coordinates}")
                
                # JavaScript로 클릭 (pyautogui 대신)
                script = f"""
                try {{
                    var element = document.elementFromPoint({rel_x}, {rel_y});
                    if (element) {{
                        element.click();
                        return {{ 
                            success: true, 
                            tagName: element.tagName,
                            className: element.className,
                            id: element.id || 'no-id',
                            text: element.textContent ? element.textContent.substring(0, 50) : ''
                        }};
                    }}
                    return {{ success: false, reason: 'no-element' }};
                }} catch(e) {{
                    return {{ success: false, reason: 'error', message: e.toString() }};
                }}
                """
                result = driver.execute_script(script)
                
                if result.get('success', False):
                    logger.info(f"{element_name} 좌표 클릭 성공: ({rel_x}, {rel_y})")
                    logger.info(f"클릭된 요소: {result.get('tagName')} {result.get('text')} ID: {result.get('id')} CLASS: {result.get('className')}")
                    time.sleep(delay)
                    return True
                else:
                    logger.warning(f"{element_name} 좌표 클릭 실패: {result.get('reason')}")
                    
                    # 실패 시 fallback으로 더 간단한 click 실행
                    fallback_script = f"document.elementFromPoint({rel_x}, {rel_y}).click();"
                    try:
                        driver.execute_script(fallback_script)
                        logger.info("Fallback 클릭 성공")
                        time.sleep(delay)
                        return True
                    except Exception as inner_e:
                        logger.warning(f"Fallback 클릭도 실패: {inner_e}")
                    
            except Exception as e:
                logger.error(f"{element_name} 좌표 클릭 중 오류: {e}")
    
    # 모든 방식 실패
    logger.error(f"{element_name} 요소 클릭 실패 - 모든 방식 시도 후")
    return False

# DOM 선택자만 사용하는 클릭 함수
def click_by_selector(driver, selector_key, delay=2.0):
    """
    DOM 선택자만 사용하여 요소 클릭
    
    Args:
        driver: Selenium WebDriver 인스턴스
        selector_key: dom_selectors.py에 정의된 선택자 키 또는 직접 선택자 문자열
        delay: 클릭 후 대기 시간(초)
    
    Returns:
        bool: 클릭 성공 여부
    """
    try:
        # 선택자 키가 카테고리.이름 형식인지 확인
        if "." in selector_key:
            category, key = selector_key.split(".")
            
            # 카테고리에 따른 선택자 맵 선택
            selector_map = None
            if category == "MENU":
                from dom_selectors import MENU_SELECTORS
                selector_map = MENU_SELECTORS
            # 다른 카테고리도 추가 가능
            
            if not selector_map or key not in selector_map:
                logger.error(f"알 수 없는 선택자 키: {selector_key}")
                return False
                
            selector = selector_map[key]
        else:
            # 직접 선택자 문자열이 전달된 경우
            selector = selector_key
        
        # XPATH 가정 (필요시 타입 구분 로직 추가)
        element = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, selector))
        )
        element.click()
        logger.info(f"DOM 선택자 클릭 성공: {selector_key}")
        time.sleep(delay)
        return True
        
    except Exception as e:
        logger.error(f"DOM 선택자 클릭 실패: {selector_key} - {e}")
        return False

# 좌표만 사용하는 클릭 함수
def click_at_coordinates(driver, coordinates, delay=2.0, browser_ui_height=0):
    """
    좌표만 사용하여 요소 클릭
    
    Args:
        driver: Selenium WebDriver 인스턴스
        coordinates: 클릭할 절대좌표 튜플 (x, y)
        delay: 클릭 후 대기 시간(초)
        browser_ui_height: 해당 파라미터는 사용하지 않음. coordinate_conversion.py의 비선형 변환 함수가 자동으로 적절한 보정을 적용함
    
    Returns:
        bool: 클릭 성공 여부
    """
    try:
        # 좌표 변환 (절대좌표 -> 상대좌표)
        # coordinate_conversion.py의 비선형 변환 함수를 사용함
        inner_width = driver.execute_script("return window.innerWidth;")
        inner_height = driver.execute_script("return window.innerHeight;")
        
        # 이제 get_converted_coordinates는 coordinate_conversion.py의 convert_coordinates 함수를 호출함
        # 이 함수는 위치별 가중치를 적용한 비선형 변환을 수행함
        rel_x, rel_y = get_converted_coordinates(
            coordinates[0], coordinates[1], inner_width, inner_height
        )
        
        # 브라우저 UI 높이 고려하여 Y 좌표 보정이 필요없음
        # coordinate_conversion.py의 비선형 변환 함수가 이미 모든 위치별 보정을 적용함
        logger.info(f"비선형 변환 적용된 좌표: ({rel_x}, {rel_y}) - 원본 좌표: {coordinates}")
        
        # JavaScript로 클릭 - 안전한 방식 추가
        safe_script = f"""
            var element = document.elementFromPoint({rel_x}, {rel_y});
            if (element) {{ 
                try {{ 
                    element.click(); 
                    return true;
                }} catch (e) {{ 
                    // 요소가 클릭 가능하지 않은 경우 클릭 이벤트 디스패치
                    var clickEvent = new MouseEvent('click', {{
                        'view': window,
                        'bubbles': true,
                        'cancelable': true,
                        'clientX': {rel_x},
                        'clientY': {rel_y}
                    }});
                    element.dispatchEvent(clickEvent);
                    return true;
                }}
            }} else {{ 
                // 요소가 없으면 문서에 직접 클릭 이벤트 발생
                var clickEvent = new MouseEvent('click', {{
                    'view': window,
                    'bubbles': true,
                    'cancelable': true,
                    'clientX': {rel_x},
                    'clientY': {rel_y}
                }});
                document.elementFromPoint({rel_x}, {rel_y}) || document.body.dispatchEvent(clickEvent);
                return true;
            }}
        """
        driver.execute_script(safe_script)
        logger.info(f"좌표 클릭 성공: {coordinates} -> ({rel_x}, {rel_y})")
        sleep_with_logging(delay, f"좌표 클릭 후 대기")
        return True
        
    except Exception as e:
        logger.error(f"좌표 클릭 실패: {coordinates} - {e}")
        return False


def smart_click(driver, ui_element, delay=2.0, max_retries=2):
    """
    DOM 선택자와 좌표를 함께 사용하는 하이브리드 클릭 방식
    ui_elements.py에 정의된 UI 요소를 사용하여 fallback_order 기반으로 시도
    
    Args:
        driver: 셀레니움 웹드라이버 인스턴스
        ui_element: ui_elements.py에 정의된 UI 요소 딕셔너리
        delay: 클릭 후 대기 시간
        max_retries: 스테일 요소 참조 오류 시 최대 재시도 횟수
    
    Returns:
        bool: 클릭 성공 여부
    """
    # 상품복사 버튼 클릭 시 최소 지연시간 보장 (복사상품 생성 안정성 확보)
    element_name = ui_element.get("name", "")
    if "PRODUCT_COPY_BUTTON" in element_name or "상품복사" in element_name:
        from timesleep import DELAY_MEDIUM
        if delay < DELAY_MEDIUM:
            logger.info(f"상품복사 버튼 클릭 - 최소 지연시간 보장: {delay}초 -> {DELAY_MEDIUM}초")
            delay = DELAY_MEDIUM
    # UI 요소 정보 로깅
    try:
        element_name = ui_element.get("name", "알 수 없는 요소")
        dom_selector = ui_element.get("dom_selector", "없음")
        coords = ui_element.get("coordinates", (0, 0))
        fallback_order = ui_element.get("fallback_order", ["dom", "coordinates"])
        
        logger.info(f"\n\n====== {element_name} 요소 클릭 시도 - 하이브리드 방식 ======")
        logger.info(f"UI 요소 정보: {element_name}")
        logger.info(f"DOM 선택자: {dom_selector}")
        logger.info(f"좌표: {coords}")
        logger.info(f"fallback 순서: {fallback_order}")
        
        # 2025-05-27 18:15 - 스테일 요소 참조 오류 처리 추가
        logger.info("=== DOM 선택자 시도 과정 상세 디버깅 정보 (2025-05-27 18:15 업데이트) ====")
    except Exception as e:
        logger.warning(f"UI 요소 정보 로깅 중 오류: {e}")
    
    for method in fallback_order:
        if method == "dom" and ui_element.get("dom_selector"):
            # DOM 선택자로 클릭 시도 (스테일 요소 재시도 포함)
            selector_type = ui_element.get("selector_type", By.XPATH)
            dom_selector = ui_element.get("dom_selector")
            logger.info(f"\n>>> 시도 1: {element_name} DOM 선택자 클릭 시도 ({selector_type}): {dom_selector}")
            
            # 스테일 요소 재시도 로직 추가
            for retry in range(max_retries + 1):  # 원래 시도 + 재시도 횟수
                try:
                    # JavaScript로 요소 존재 여부 먼저 검사
                    try:
                        js_check = """
                        var xpath_result = [];
                        if (arguments[0].startsWith('//')) {
                            // XPath 처리
                            var xpathResult = document.evaluate(arguments[0], document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                            var exists = xpathResult.snapshotLength > 0;
                            var count = xpathResult.snapshotLength;
                            var tag = exists ? xpathResult.snapshotItem(0).tagName : 'None';
                            return {exists: exists, count: count, tagName: tag};
                        } else {
                            // CSS 선택자 처리
                            var elements = document.querySelectorAll(arguments[0]);
                            var exists = elements.length > 0;
                            var count = elements.length;
                            var tag = exists ? elements[0].tagName : 'None';
                            return {exists: exists, count: count, tagName: tag};
                        }
                        """
                        js_result = driver.execute_script(js_check, dom_selector)
                        js_exists = js_result.get('exists', False)
                        js_count = js_result.get('count', 0)
                        js_tag = js_result.get('tagName', 'Unknown')
                        logger.info(f"[JS 확인] DOM 요소 존재: {js_exists}, 개수: {js_count}, 태그: {js_tag}")
                        
                        # JS로 요소가 없다고 판단되면 재시도 중단
                        if not js_exists and retry < max_retries:
                            logger.warning(f"[재시도 {retry+1}/{max_retries}] 요소가 DOM에 없음. 잠시 대기 후 재시도...")
                            time.sleep(0.5)  # 짧은 대기 후 재시도
                            continue
                        elif not js_exists:
                            # 모든 재시도 실패 시 다음 방법으로
                            logger.warning("모든 JS 확인 재시도 실패. 다음 방법으로 진행")
                            break
                    except Exception as js_error:
                        logger.warning(f"JavaScript 요소 확인 중 오류: {js_error}")
                    
                    # 요소 존재 확인 및 클릭 시도
                    try:
                        # 요소가 클릭 가능할 때까지 명시적 대기 (탭 변경 시 안정성 향상)
                        wait = WebDriverWait(driver, 2)
                        element = wait.until(EC.element_to_be_clickable((selector_type, dom_selector)))
                        
                        logger.info(f"DOM 선택자 요소 발견: tag={element.tag_name}, displayed={element.is_displayed()}, enabled={element.is_enabled()}")
                        
                        # JavaScript로 클릭 시도 (더 안정적인 방법)
                        logger.info(f"[Selenium] JavaScript로 DOM 요소 클릭 시도...")
                        driver.execute_script("arguments[0].click();", element)
                        
                        # 성공 로깅
                        logger.info(f"{element_name} DOM 선택자 클릭 성공 (JavaScript)")
                        # 상품복사 버튼 클릭 시 최소 지연시간 재확인
                        if "PRODUCT_COPY_BUTTON" in element_name or "상품복사" in element_name:
                            from timesleep import DELAY_MEDIUM
                            if delay < DELAY_MEDIUM:
                                logger.info(f"상품복사 성공 후 최소 지연시간 적용: {DELAY_MEDIUM}초")
                                delay = DELAY_MEDIUM
                        time.sleep(delay)
                        return True
                    except Exception as click_error:
                        # 일반 클릭 방식으로 시도
                        try:
                            logger.info(f"[Selenium] 일반 DOM 요소 클릭 시도...")
                            element = driver.find_element(selector_type, dom_selector)
                            element.click()
                            logger.info(f"{element_name} DOM 선택자 클릭 성공 (일반)")
                            # 상품복사 버튼 클릭 시 최소 지연시간 재확인
                            if "PRODUCT_COPY_BUTTON" in element_name or "상품복사" in element_name:
                                from timesleep import DELAY_MEDIUM
                                if delay < DELAY_MEDIUM:
                                    logger.info(f"상품복사 성공 후 최소 지연시간 적용: {DELAY_MEDIUM}초")
                                    delay = DELAY_MEDIUM
                            time.sleep(delay)
                            return True
                        except Exception as e:
                            if "stale element reference" in str(e).lower() and retry < max_retries:
                                logger.warning(f"[재시도 {retry+1}/{max_retries}] 스테일 요소 참조 오류 발생: {e}")
                                time.sleep(0.5)  # 잠시 대기 후 재시도
                                continue
                            else:
                                logger.warning(f"일반 클릭 실패: {e}")
                                # 마지막 재시도이거나 다른 오류면 다음 방법으로
                                if retry >= max_retries:
                                    break
                except StaleElementReferenceException as stale_error:
                    if retry < max_retries:
                        logger.warning(f"[재시도 {retry+1}/{max_retries}] 스테일 요소 참조 오류 발생: {stale_error}")
                        time.sleep(0.5)  # 잠시 대기 후 재시도
                        continue
                    else:
                        logger.warning(f"최대 재시도 횟수 초과. 스테일 요소 오류: {stale_error}")
                        break
                except Exception as e:
                    logger.warning(f"DOM 선택자 시도 중 오류: {e}")
                    if retry < max_retries:
                        logger.warning(f"[재시도 {retry+1}/{max_retries}] 잠시 대기 후 재시도...")
                        time.sleep(0.5)
                        continue
                    else:
                        logger.warning("모든 재시도 실패. 다음 방법으로 진행")
                        break
        elif method == "coordinates" and ui_element.get("coordinates"):
            # 좌표로 클릭 시도
            try:
                logger.info(f"\n>>> 시도 2: {element_name} 좌표 클릭 시도: {ui_element['coordinates']}")
                # 상품복사 버튼 좌표 클릭 시 최소 지연시간 보장
                coord_delay = delay
                if "PRODUCT_COPY_BUTTON" in element_name or "상품복사" in element_name:
                    from timesleep import DELAY_MEDIUM
                    if coord_delay < DELAY_MEDIUM:
                        logger.info(f"상품복사 좌표 클릭 - 최소 지연시간 보장: {coord_delay}초 -> {DELAY_MEDIUM}초")
                        coord_delay = DELAY_MEDIUM
                if click_at_coordinates(driver, ui_element["coordinates"], coord_delay):
                    logger.info(f"{element_name} 좌표 클릭 성공")
                    return True
            except Exception as e:
                logger.warning(f"{element_name} 좌표 클릭 실패: {e}")
                
    logger.error(f"\n>>> {element_name} 클릭 실패 - 모든 방법 시도 후")
    return False

def smart_click_with_focus(driver, element_info, delay=0.5):
    """
    옵션 탭 입력창을 위한 특별한 클릭 함수
    smart_click 시도 후 항상 JavaScript로 포커스 및 선택 처리
    """
    element_name = element_info.get("name", "알 수 없는 요소")
    logger.info(f"\n====== {element_name} 포커스 클릭 시도 ======")
    
    # 먼저 일반적인 smart_click 시도
    result = smart_click(driver, element_info, delay)
    
    # smart_click 결과와 관계없이 JavaScript로 포커스 및 선택 처리 시도
    try:
        # DOM 선택자가 있으면 해당 요소에 직접 포커스
        if "dom_selector" in element_info:
            dom_selector = element_info["dom_selector"]
            logger.info(f"DOM 선택자로 JavaScript 포커스 시도: {dom_selector}")
            js_focus_script = f"""
            var element = document.evaluate("{dom_selector}", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
            console.log('Element found by DOM selector:', element);
            if (element && (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA')) {{
                console.log('Focusing element:', element);
                element.focus();
                element.select();
                element.click();
                return true;
            }}
            return false;
            """
            focus_result = driver.execute_script(js_focus_script)
            if focus_result:
                logger.info("DOM 선택자 JavaScript 포커스 및 선택 성공")
                time.sleep(delay)
                return True
            else:
                logger.warning("DOM 선택자 JavaScript 포커스 실패")
        
        # DOM 선택자가 실패하거나 없으면 좌표로 시도
        if "coordinates" in element_info:
            x, y = element_info["coordinates"]
            
            # 브라우저 크기 가져오기
            inner_width = driver.execute_script("return window.innerWidth;")
            inner_height = driver.execute_script("return window.innerHeight;")
            
            # 좌표 변환 적용
            converted_x, converted_y = get_converted_coordinates(x, y, inner_width, inner_height)
            
            logger.info(f"원본 좌표: ({x}, {y}) -> 변환된 좌표: ({converted_x}, {converted_y})")
            logger.info(f"브라우저 크기: {inner_width}x{inner_height}")
            
            js_focus_script = f"""
            var element = document.elementFromPoint({converted_x}, {converted_y});
            console.log('Element at converted coordinates:', element);
            if (element && (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA')) {{
                console.log('Focusing element:', element);
                element.focus();
                element.select();
                element.click();
                return true;
            }}
            return false;
            """
            focus_result = driver.execute_script(js_focus_script)
            if focus_result:
                logger.info("변환된 좌표 JavaScript 포커스 및 선택 성공")
                time.sleep(delay)
                return True
            else:
                logger.warning("변환된 좌표 JavaScript 포커스 실패 - 해당 좌표에 input/textarea 요소 없음")
    except Exception as e:
        logger.warning(f"JavaScript 포커스 처리 실패: {e}")
    
    return result
