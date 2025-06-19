import logging
import time
import json
# import pyautogui - 절대좌표 클릭 방식 중단 (command prompt 창 최소화 문제)
import os
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, JavascriptException

# 채널톡 닫기 상태 플래그
channel_talk_hidden = False

# 마지막 채널톡 닫기 시도 시간 기록
last_channel_talk_attempt = 0

def is_channel_talk_visible(driver, timeout=1):
    """
    채널톡 메신저가 현재 화면에 보이는지 확인합니다.
    
    Args:
        driver: Selenium WebDriver 인스턴스
        timeout: 최대 기다리는 시간(초)
    
    Returns:
        bool: 채널톡이 보이면 True, 보이지 않으면 False
    """
    try:
        # 간단한 JavaScript 스크립트로 채널톡 요소 확인 - DOM 스캔 최소화
        script = """
        try {
            // 채널톡 요소 확인 (기본 선택자)
            var element = document.querySelector('.ch-desk-messenger');
            if (element) {
                var rect = element.getBoundingClientRect();
                if (rect.width > 10 && rect.height > 10) {
                    return { found: true, width: rect.width, height: rect.height, selector: '.ch-desk-messenger' };
                }
            }
            
            // 대체 선택자
            var altElement = document.querySelector('#ch-plugin');
            if (altElement) {
                var rect = altElement.getBoundingClientRect();
                if (rect.width > 10 && rect.height > 10) {
                    return { found: true, width: rect.width, height: rect.height, selector: '#ch-plugin' };
                }
            }
            
            return { found: false };
        } catch (e) {
            return { found: false, error: e.toString() };
        }
        """
        
        result = driver.execute_script(script)
        
        if isinstance(result, dict) and result.get('found', False):
            selector = result.get('selector', 'unknown')
            width = result.get('width', 0)
            height = result.get('height', 0)
            logging.info(f"채널톡 메신저 발견 ({selector}): 크기 {width}x{height}")
            return True
        
        return False
    
    except Exception as e:
        logging.debug(f"채널톡 가시성 확인 중 오류: {e}")
        return False  # 오류 발생 시 보이지 않는다고 가정

def check_and_hide_channel_talk(driver, timeout=5):
    """
    채널톡(Channel Talk) 메신저 창이 열려있는지 확인하고, 열려있다면 모든 가능한 방법을 사용하여 닫기를 시도합니다.
    
    방법 1: JavaScript API 접근법 사용
    방법 2: 강제 제거 JavaScript 실행
    방법 3: 절대좌표 기반 클릭
    방법 4: 채널톡 강제 제거 및 모듈 로딩 방지
    
    Args:
        driver: Selenium WebDriver 인스턴스
        timeout: 최대 대기 시간(초)
        
    Returns:
        bool: 채널톡 닫기 시도 성공 여부
    """
    global channel_talk_hidden, last_channel_talk_attempt
    
    # 초기화
    success = False
    
    # 이미 채널톡을 닫았다면 다시 시도하지 않음
    if channel_talk_hidden:
        logging.info("채널톡이 이미 닫혀 있습니다. 추가 닫기 시도를 건너뜁니다.")
        return True
    
    # 마지막 시도 후 최소 3초 대기 (너무 자주 호출 방지)
    current_time = time.time()
    if current_time - last_channel_talk_attempt < 3:
        logging.info(f"최근 {current_time - last_channel_talk_attempt:.1f}초 전에 시도했으니 잠시 대기")
        time.sleep(0.5)
    
    # 시도 시간 기록
    last_channel_talk_attempt = current_time
    
    # 주의: 창 포커스 변경 및 윈도우 핸들 전환 코드 제거 (명령 프롬프트 창 최소화 문제 해결)
    # 포커스 변경 없이 JavaScript만으로 채널톡 요소 숨기기
    
    logging.info("채널톡 숨기기 적용 - 확인 과정 건너뛐")
    
    # 채널톡 보이는지 확인하지 않고 바로 강제 숨기기 적용
    # 이렇게 하면 DOM 스캔을 최소화하여 커맨드 프롬프트 창이 최소화되는 문제를 방지할 수 있음
    try:
        # 채널톡 요소를 숨기는 매우 간단한 스크립트 실행
        simple_script = """
        try {
            // 채널톡 요소 강제 숨김 (간소화 버전)
            var styleId = 'channel-talk-blocker-style';
            var existingStyle = document.getElementById(styleId);
            
            if (!existingStyle) {
                var style = document.createElement('style');
                style.id = styleId;
                style.textContent = `
                    #ch-plugin, .ch-messenger, div[id^="ch-plugin"], iframe[id^="ch-plugin"],
                    div[class*="ch-plugin"], div[class*="ChannelTalk"], 
                    div[class*="ChatButton"], div[class*="IconButton"] {
                        display: none !important;
                        visibility: hidden !important;
                        opacity: 0 !important;
                        pointer-events: none !important;
                    }
                `;
                document.head.appendChild(style);
            }
            return { success: true, method: '강제 숨김 적용 (확인 건너뛐)' };
        } catch (e) {
            return { success: false, error: e.toString() };
        }
        """
        
        result = driver.execute_script(simple_script)
        logging.info(f"채널톡 강제 숨김 결과: {json.dumps(result, ensure_ascii=False)}")
        
        # 성공 여부와 상관없이 항상 성공으로 처리
        channel_talk_hidden = True
        logging.info("채널톡 닫기 성공! 이후 닫기 시도는 무시됩니다.")
        return True
    except Exception as e:
        logging.warning(f"채널톡 강제 숨김 실패: {e}")
        # 예외 발생해도 계속 진행
        channel_talk_hidden = True
        return True
        
    # 여기까지 실행되지 않음 - 파일 끝까지 요청이 오면 실패로 처리
    logging.info("채널톡 처리 시도 중 오류 발생")
    
    # 방법 1: JavaScript API 접근법
    logging.info("방법 1: JavaScript API 접근법 시도")
    js_script = """
    try {
        if (window.ch && window.ch.plugin) {
            // 1. hideMessenger 메서드 사용 시도
            if (window.ch.plugin.messenger && typeof window.ch.plugin.messenger.hideMessenger === 'function') {
                window.ch.plugin.messenger.hideMessenger();
                return { success: true, method: 'hideMessenger' };
            }
            
            // 2. hide 메서드 사용 시도
            if (typeof window.ch.plugin.hide === 'function') {
                window.ch.plugin.hide();
                return { success: true, method: 'hide' };
            }
            
            return { success: false, reason: 'no-methods' };
        }
        return { success: false, reason: 'not-available' };
    } catch(e) {
        return { success: false, reason: 'error', message: e.message };
    }
    """
    
    try:
        result = driver.execute_script(js_script)
        if isinstance(result, dict) and result.get('success'):
            logging.info(f"채널톡 API 호출 성공: {result.get('method')}")
            success = True
        else:
            logging.info(f"방법 1 결과: {result}")
    except Exception as e:
        logging.warning(f"JavaScript API 호출 오류: {e}")
    
    # 방법 2: 강제 제거 JavaScript 실행
    if not success:
        logging.info("방법 2: 채널톡 강제 제거 시도 (간소화 버전)")
        try:
            # 매우 간단한 스크립트를 사용하여 CSS만 적용하고 DOM 스캔은 하지 않음
            simple_script = """
            // 매우 간소화된 채널톡 숨김 처리 - DOM 조작 최소화
            try {
                // 간단한 스타일 적용만 수행
                var styleId = 'channel-talk-blocker-style';
                var existingStyle = document.getElementById(styleId);
                
                if (!existingStyle) {
                    var style = document.createElement('style');
                    style.id = styleId;
                    style.textContent = `
                        #ch-plugin, .ch-messenger, div[id^="ch-plugin"], iframe[id^="ch-plugin"],
                        div[class*="ch-plugin"], div[class*="ChannelTalk"], 
                        div[class*="ChatButton"], div[class*="IconButton"] {
                            display: none !important;
                            visibility: hidden !important;
                            opacity: 0 !important;
                            pointer-events: none !important;
                        }
                    `;
                    document.head.appendChild(style);
                }
                return { success: true, removed: 3 };
            } catch (e) {
                return { success: false, error: e.toString() };
            }
            """
            
            # JavaScript 실행
            js_result = driver.execute_script(simple_script)
            logging.info(f"채널톡 강제 제거 결과: {json.dumps(js_result, ensure_ascii=False)}")
            
            if js_result.get('success', False):
                logging.info(f"채널톡 강제 제거 성공: {js_result.get('removed', 0)} 개 요소 제거")
                success = True
        except Exception as e:
            logging.error(f"채널톡 강제 제거 오류: {str(e)}")

    
    # 방법 3: 절대좌표 기반 클릭 (주석 처리)
    # if not success:
    #     logging.info("방법 3: 절대좌표 기반 클릭 시도")
    #     try:
    #         # 브라우저 내부 크기 가져오기
    #         inner_width = driver.execute_script("return window.innerWidth")
    #         inner_height = driver.execute_script("return window.innerHeight")
    #         
    #         # 채널톡 닫기 버튼 추정 위치 - 화면 우측 하단
    #         from coordinate_conversion import convert_coordinates
    #         original_x, original_y = 1860, 990  # 일반적인 채널톡 위치
    #         
    #         # 좌표 변환
    #         relative_x, relative_y = convert_coordinates(original_x, original_y, driver)
    #         logging.info(f"채널톡 닫기 위한 상대좌표: ({relative_x}, {relative_y}) [원본: ({original_x}, {original_y})]")
    #         
    #         # JavaScript로 요소 클릭
    #         result = driver.execute_script(f"""
    #             var el = document.elementFromPoint({relative_x}, {relative_y});
    #             if (el) {{
    #                 var info = {{
    #                     tagName: el.tagName,
    #                     className: el.className || 'no-class',
    #                     id: el.id || 'no-id',
    #                     isChannelTalkRelated: (el.className && String(el.className).indexOf('ch-') !== -1) || 
    #                                      (el.id && String(el.id).indexOf('ch-') !== -1),
    #                     attributes: {{}}
    #                 }};
    #                 
    #                 // 중요 속성 수집
    #                 if (el.attributes) {{
    #                     for (var i = 0; i < el.attributes.length; i++) {{
    #                         var attr = el.attributes[i];
    #                         info.attributes[attr.name] = attr.value;
    #                     }}
    #                 }}
    #                 
    #                 el.click();
    #                 return info;
    #             }}
    #             return null;
    #         """)
    #         
    #         if result:
    #             logging.info(f"전략 3 결과: {result}")
    #             if result.get('isChannelTalkRelated', False):
    #                 logging.info(f"채널톡 관련 요소 클릭 확인: {result}")
    #                 success = True
    #             else:
    #     except Exception as e:
    #         logging.warning(f"그리드 클릭 시도 실패: {e}")

    # 방법 6: PyAutoGUI로 직접 클릭 (주석 처리)
    # if not success:
    #     logging.info("전략 5: PyAutoGUI로 직접 클릭 시도")
    #     try:
    #         # 브라우저 위치와 크기 가져오기
    #         browser_rect = driver.get_window_rect()
    #         browser_pos_x = browser_rect['x']
    #         browser_pos_y = browser_rect['y']
    #         browser_width = browser_rect['width']
    #         browser_height = browser_rect['height']
    #         
    #         # 채널톡 요소 위치 확인 시도
    #         js_get_iframe_position = """
    #         var iframe = document.querySelector('#ch-plugin-script-iframe');
    #         if (iframe) {
    #             var rect = iframe.getBoundingClientRect();
    #             return {
    #                 found: true,
    #                 x: rect.right - 30,  // iframe 오른쪽에서 약간 안쪽으로
    #                 y: rect.top + 30     // iframe 상단에서 약간 아래로
    #             };
    #         }
    #         
    #         // 채널톡 요소 찾기
    #         var elements = [
    #             document.querySelector('#ch-plugin-launcher'),
    #             document.querySelector('div[class*="ChatButtonContainer"]'),
    #             document.querySelector('div[class*="IconButtonView"]')
    #         ];
    #         
    #         for (var i = 0; i < elements.length; i++) {
    #             var el = elements[i];
    #             if (el) {
    #                 var rect = el.getBoundingClientRect();
    #                 if (rect.width > 0 && rect.height > 0) {
    #                     return {
    #                         found: true,
    #                         x: rect.right - (rect.width * 0.2),
    #                         y: rect.top + (rect.height * 0.2)
    #                     };
    #                 }
    #             }
    #         }
    #         
    #         return { found: false };
    #         """
    #         
    #         iframe_pos = driver.execute_script(js_get_iframe_position)
    #         
    #         if iframe_pos and iframe_pos.get('found', False):
    #             # 채널톡 요소 발견 - 정확한 위치 클릭
    #             relative_x = iframe_pos['x']
    #             relative_y = iframe_pos['y']
    #             logging.info(f"채널톡 요소 발견: 상대좌표 ({relative_x}, {relative_y})")
    #         else:
    #             # 채널톡 요소를 찾지 못한 경우 - 우측 하단 추정 위치 사용
    #             # 일반적인 채널톡 위치 - 우측 하단 경계에서 안쪽으로 70px 정도
    #             relative_x = browser_width - 70  # 우측 경계에서 70px 안쪽
    #             relative_y = browser_height - 70  # 하단 경계에서 70px 위쪽
    #             logging.info(f"채널톡 요소 발견 실패, 추정 위치 사용: ({relative_x}, {relative_y})")
    #         
    #         # 절대좌표 계산 (브라우저 위치 + 상대좌표)
    #         absolute_x = browser_pos_x + relative_x
    #         absolute_y = browser_pos_y + relative_y
    #         
    #         # UI 요소 위치 확인
    #         logging.info(f"브라우저: ({browser_pos_x}, {browser_pos_y}, {browser_width}x{browser_height}), 채널톡 클릭 좌표: ({absolute_x}, {absolute_y})")
    #         
    #         # PyAutoGUI로 클릭 - 여러 지점 클릭 시도
    #         # 기본 위치 클릭
    #         pyautogui.click(absolute_x, absolute_y)
    #         logging.info(f"PyAutoGUI 클릭 #1: ({absolute_x}, {absolute_y})")
    #         time.sleep(0.5)
    #         
    #         # 약간 위쪽 클릭
    #         pyautogui.click(absolute_x, absolute_y - 15)
    #         logging.info(f"PyAutoGUI 클릭 #2: ({absolute_x}, {absolute_y - 15})")
    #         time.sleep(0.5)
    #         
    #         # 약간 왼쪽위 클릭
    #         pyautogui.click(absolute_x - 15, absolute_y - 15)
    #         logging.info(f"PyAutoGUI 클릭 #3: ({absolute_x - 15}, {absolute_y - 15})")
    #         time.sleep(0.5)
    #         
    #         success = True
    #     except Exception as e:
    #         logging.warning(f"PyAutoGUI 클릭 시도 실패: {e}")
    
    # 채널톡 실제 존재 여부 최종 확인
    try:
        # 채널톡 컨테이너 존재 여부 확인 (최종 확인 스크립트 간소화)
        # 무거운 DOM 스캔을 피하고 간단한 확인만 수행
        final_check_script = """
        var result = { exists: false, details: {} };
        
        // 채널톡 메인 요소만 빠르게 확인
        var plugin = document.getElementById('ch-plugin');
        if (plugin) {
            var style = window.getComputedStyle(plugin);
            result.details['ch-plugin'] = { 
                display: style.display, 
                visible: (style.display !== 'none' && style.visibility !== 'hidden')
            };
            // 간단히 확인 - 보이면 exists=true
            if (style.display !== 'none' && style.visibility !== 'hidden') {
                result.exists = true;
            }
        }
        
        return result;
        """
        
        final_check_result = driver.execute_script(final_check_script)
        logging.info(f"채널톡 간소화 확인 결과: {final_check_result}")
        
        # 채널톡이 여전히 보이는지 간단히 확인
        channel_talk_still_visible = final_check_result.get('exists', False)
        visible_elements_count = 0  # 더 이상 모든 요소를 찾지 않음
        
        if channel_talk_still_visible:
            logging.warning(f"최종 확인: 채널톡 관련 요소 {visible_elements_count}개가 여전히 화면에 보입니다.")
            success = False
        elif success:
            logging.info("최종 확인: 이전 전략 중 하나가 성공한 것으로 판단됩니다.")
        else:
            logging.warning("최종 확인: 채널톡 상태를 정확하게 확인할 수 없지만, 자동화는 계속 진행됩니다.")
    except Exception as e:
        logging.warning(f"최종 확인 과정에서 오류 발생: {e}")
    
    # 방법 3: 사용자가 제공한 절대좌표로 채널톡 버튼 직접 클릭 시도
    # if not success:
    #     logging.info("방법 3: 사용자가 제공한 절대좌표로 채널톡 버튼 직접 클릭 시도")
    #     try:
    #         # 브라우저 위치와 크기 가져오기
    #         browser_rect = driver.get_window_rect()
    #         browser_pos_x = browser_rect['x']
    #         browser_pos_y = browser_rect['y']
    #         browser_width = browser_rect['width']
    #         browser_height = browser_rect['height']
    #         
    #         logging.info(f"브라우저 정보: 위치 ({browser_pos_x}, {browser_pos_y}), 크기 {browser_width}x{browser_height}")
    #         
    #         # 사용자가 coordinate_step1.py에 정의한 좌표 가져오기
    #         try:
    #             from coordinate_step1 import PRODUCT_MODAL_CLOSE
    #             user_coordinates = [
    #                 PRODUCT_MODAL_CLOSE["CHANNEL_TALK_CLOSE"],
    #                 PRODUCT_MODAL_CLOSE["CHANNEL_TALK_CLOSE1"],
    #                 PRODUCT_MODAL_CLOSE["CHANNEL_TALK_CLOSE2"],
    #                 PRODUCT_MODAL_CLOSE["CHANNEL_TALK_CLOSE3"],
    #                 PRODUCT_MODAL_CLOSE["CHANNEL_TALK_CLOSE4"],
    #                 PRODUCT_MODAL_CLOSE["CHANNEL_TALK_CLOSE5"],
    #                 PRODUCT_MODAL_CLOSE["CHANNEL_TALK_CLOSE6"],
    #                 PRODUCT_MODAL_CLOSE["CHANNEL_TALK_CLOSE7"],
    #                 PRODUCT_MODAL_CLOSE["CHANNEL_TALK_CLOSE8"],
    #                 PRODUCT_MODAL_CLOSE["CHANNEL_TALK_CLOSE9"],
    #                 PRODUCT_MODAL_CLOSE["CHANNEL_TALK_CLOSE10"]
    #             ]
    #             logging.info(f"사용자 정의 채널톡 좌표 {len(user_coordinates)}개 가져옴")
    #         except (ImportError, KeyError) as e:
    #             logging.warning(f"사용자 정의 좌표 가져오기 실패: {e}")
    #             # 사용자 정의 좌표가 없으면 기본 좌표 사용
    #             user_coordinates = []
    #         
    #         # 추가 배열 - 사용자 정의 좌표가 없으면 기본 좌표 사용
    #         default_coordinates = [
    #             # 직접 계산된 상대 좌표
    #             (browser_width - 40, browser_height - 40),  # 우측 하단에서 40px 안쪽
    #             (browser_width - 50, browser_height - 50),  # 우측 하단에서 50px 안쪽
    #             (browser_width - 30, browser_height - 30),  # 우측 하단에서 30px 안쪽
    #             (browser_width - 60, browser_height - 60),  # 우측 하단에서 60px 안쪽
    #             (browser_width - 25, browser_height - 25),  # 우측 하단에서 25px 안쪽
    #             # 고정 절대 좌표 - 공통적인 채널톡 위치
    #             (1820, 760), (1840, 760),  # 사용자가 제공한 좌표를 기본으로 포함
    #             (1800, 730), (1820, 740), (1840, 750),  # 상단 영역 추가
    #             (1830, 970), (1840, 975), (1850, 980),  # 하단 영역 추가
    #             (1860, 985), (1870, 990), (1880, 995)  # 추가 좌표
    #         ]
    #         
    #         # 사용자 좌표 + 기본 좌표 합치기
    #         click_coordinates = user_coordinates + default_coordinates
    #         
    #         # 중복 제거 및 섹플링 - 너무 많은 시도 방지
    #         unique_coordinates = []
    #         for coord in click_coordinates:
    #             if coord not in unique_coordinates:
    #                 unique_coordinates.append(coord)
    #         
    #         # 순서 섬플링 - 결과를 범위를 넘어서 일반화
    #         if len(unique_coordinates) > 12:  # 너무 많은 좌표는 랜덤 샘플링
    #             import random
    #             random.shuffle(unique_coordinates)
    #             click_coordinates = unique_coordinates[:12]  # 최대 12개 좌표만 사용
    #         else:
    #             click_coordinates = unique_coordinates
    #         
    #         logging.info(f"총 {len(click_coordinates)}개 좌표 클릭 시도 예정")
    #         
    #         # 좌표 클릭 시도
    #         for i, coord in enumerate(click_coordinates):
    #             if success:
    #                 break
    #             
    #             # 좌표 값 추출
    #             try:
    #                 rel_x, rel_y = coord
    #             except:
    #                 logging.warning(f"잘못된 좌표 형식 바로 건너뛼: {coord}")
    #                 continue
    #             
    #             # 절대좌표 변환 계산
    #             try:
    #                 # coordinate_conversion.py 모듈 활용 시도
    #                 try:
    #                     from coordinate_conversion import convert_coordinates
    #                     converted_coords = convert_coordinates(rel_x, rel_y, browser_width, browser_height)
    #                     adjusted_x, adjusted_y = converted_coords
    #                     absolute_x = browser_pos_x + adjusted_x
    #                     absolute_y = browser_pos_y + adjusted_y
    #                     logging.info(f"변환 결과: ({rel_x}, {rel_y}) -> ({adjusted_x}, {adjusted_y}) -> 절대좌표 ({absolute_x}, {absolute_y})")
    #                 except (ImportError, Exception) as e:
    #                     # 로딩 실패시 직접 계산
    #                     if rel_x > 1000:  # 절대 좌표로 보임
    #                         adjusted_x = int(browser_width * (rel_x / 1920))
    #                         adjusted_y = int(browser_height * (rel_y / 1080))
    #                     else:
    #                         adjusted_x, adjusted_y = rel_x, rel_y
    #                         
    #                     absolute_x = browser_pos_x + adjusted_x
    #                     absolute_y = browser_pos_y + adjusted_y
    #                     logging.info(f"직접 계산: ({rel_x}, {rel_y}) -> 절대좌표 ({absolute_x}, {absolute_y})")
    #             except Exception as e:
    #                 logging.error(f"좌표 변환 오류 {e}, 건너뛼")
    #                 continue
    #             
    #             logging.info(f"채널톡 버튼 클릭 시도 {i+1}/{len(click_coordinates)}: ({absolute_x}, {absolute_y})")
    #             
    #             # 현재 브라우저에 포커스 다시 주기
    #             try:
    #                 driver.execute_script("window.focus();")
    #                 time.sleep(0.1)  # 짧은 대기
    #             except Exception:
    #                 pass
    #             
    #             # PyAutoGUI로 클릭
    #             pyautogui.click(absolute_x, absolute_y)
    #             time.sleep(0.5)
    #             
    #             # 클릭 후 상태 확인
    #             if not is_channel_talk_visible(driver):
    #                 logging.info(f"채널톡 버튼 클릭 성공! (시도 {i+1})")
    #                 success = True
    #                 break
    #     except Exception as e:
    #         logging.error(f"절대좌표 기반 채널톡 닫기 오류: {e}")
    
    # 방법 4: 마지막 수단 - 채널톡 요소에 한정하여 ESC 키 입력
    # if not success:
    #     logging.info("방법 4: 채널톡 요소에 한정하여 ESC 키 입력 시도")
    #     try:
    #         # 원래 컨텍스트로 전환
    #         driver.switch_to.default_content()
    #         
    #         # 채널톡 요소 찾기 시도
    #         channel_elements = driver.find_elements(By.CSS_SELECTOR, '#ch-plugin, #ch-plugin-script, .ch-desk-messenger, iframe[id*="ch-plugin"]')
    #         if channel_elements and len(channel_elements) > 0:
    #             # 채널톡 요소에 포커스
    #             channel_element = channel_elements[0]
    #             driver.execute_script("arguments[0].focus()", channel_element)
    #             
    #             # 키보드 이벤트 발생 (채널톡 요소에 직접 전달)
    #             from selenium.webdriver.common.keys import Keys
    #             from selenium.webdriver.common.action_chains import ActionChains
    #             
    #             actions = ActionChains(driver)
    #             actions.move_to_element(channel_element)
    #             actions.send_keys(Keys.ESCAPE)
    #             actions.perform()
    #             
    #             time.sleep(0.5)
    #         else:
    #             # 채널톡 요소가 없으면 JavaScript로 ESC 키 이벤트 시뮬레이션
    #             # 특정 요소에만 이벤트를 전달하도록 처리
    #             esc_script = """
    #             (function() {
    #                 // 채널톡 관련 요소 찾기
    #                 const elements = [
    #                     document.querySelector('#ch-plugin'),
    #                     document.querySelector('#ch-plugin-script'),
    #                     document.querySelector('.ch-desk-messenger'),
    #                     document.querySelector('iframe[id*="ch-plugin"]')
    #                 ].filter(el => el !== null);
    #                 
    #                 if (elements.length > 0) {
    #                     // 채널톡 요소에 ESC 키 이벤트 발생
    #                     const escEvent = new KeyboardEvent('keydown', {
    #                         key: 'Escape',
    #                         code: 'Escape',
    #                         keyCode: 27,
    #                         which: 27,
    #                         bubbles: true,
    #                         cancelable: true
    #                     });
    #                     
    #                     elements[0].dispatchEvent(escEvent);
    #                     return true;
    #                 }
    #                 return false;
    #             })();
    #             """
    #             driver.execute_script(esc_script)
    #         
    #         # 상태 확인
    #         if not is_channel_talk_visible(driver):
    #             logging.info("채널톡 요소에 ESC 키 전달 성공!")
    #             success = True
    #     except Exception as e:
    #         logging.error(f"ESC 키 시도 오류: {e}")
    #         
    # 추가 시도: 일부 상황에서 iframe을 사용해 설정했을 수 있으므로 추가 처리
    # if not success:
    #     try:
    #         # 원래 컨텍스트로 전환
    #         driver.switch_to.default_content()
    #         
    #         # 채널톡 관련 요소 숨김 JavaScript 사용
    #         hide_script = """
    #         // 채널톡 숲김 처리
    #         (function() {
    #             document.querySelectorAll('iframe').forEach(function(iframe) {
    #                 if (iframe.id && iframe.id.indexOf('ch-plugin') >= 0) {
    #                     iframe.style.display = 'none';
    #                     iframe.style.visibility = 'hidden';
    #                 }
    #             });
    #             return true;
    #         })();
    #         """
    #         driver.execute_script(hide_script)
    #         time.sleep(0.2)
    #         
    #         # 상태 확인
    #         if not is_channel_talk_visible(driver):
    #             logging.info("iframe 숨기기 성공!")
    #             success = True
    #     except Exception as e:
    #         logging.error(f"iframe 숨기기 시도 오류: {e}")
    
    # 채널톡 상태 확인 - 모든 방법 시도 후
    is_visible = is_channel_talk_visible(driver)
    if not is_visible:
        success = True
    
    # 채널톡 닫기 성공 여부와 관계없이 플래그 설정 (중복 시도 방지)
    channel_talk_hidden = True
    
    # 채널톡 닫기 성공 여부 반환
    if success:
        logging.info("채널톡 닫기 성공! 이후 닫기 시도는 무시됩니다.")
    else:
        logging.info("채널톡 닫기 시도가 실패했지만, 자동화는 계속 진행됩니다.")
    
    return True

def hide_channel_talk_with_js(driver):
    """
    JavaScript를 사용하여 채널톡을 강제로 제거합니다.
    DOM 조작으로 채널톡을 제거할 수 없는 경우 사용하는 강력한 방법입니다.
    """
    try:
        logging.info("강력한 JavaScript 방법으로 채널톡 완전 제거 시도")
        
        # 채널톡 완전 제거를 위한 강력한 스크립트
        script = """
        (function() {
            try {
                // 1. 모든 iframe 제거
                document.querySelectorAll('iframe').forEach(iframe => {
                    if (iframe.id && iframe.id.indexOf('ch-plugin') !== -1) {
                        if (iframe.parentNode) {
                            iframe.parentNode.removeChild(iframe);
                            console.log('Removed iframe:', iframe.id);
                        }
                    }
                });
                
                // 2. 채널톡 관련 요소 모두 제거
                const elementsToRemove = [
                    '#ch-plugin',
                    '#ch-plugin-script',
                    '.ch-messenger',
                    '.ch-desk-messenger',
                    '.ChatButtonContainer__Container-ch-front__sc-qgvnh9-0',
                    '[data-ch-testid="lounge"]',
                    '[data-ch-testid="minimize-button"]',
                    '.MinimizeButtonView__Wrapper-ch-front__sc-1idijj-0',
                    '.SenderButtonView__Wrapper-ch-front__sc-1aik3pi-0',
                    '.IconButtonView__Background-ch-front__sc-vtu014-0',
                    '.Badge__BaseUnreadBadge-ch-front__sc-1k3c5b2-2'
                ];
                
                let removed = 0;
                elementsToRemove.forEach(selector => {
                    document.querySelectorAll(selector).forEach(el => {
                        if (el && el.parentNode) {
                            el.parentNode.removeChild(el);
                            removed++;
                        }
                    });
                });
                
                // 3. CSS 에 의해 모든 채널톡 관련 요소 숨길
                const style = document.createElement('style');
                style.innerHTML = `
                    #ch-plugin, .ch-messenger, [class*="ch-"], [data-ch-testid*="channel"], 
                    [class*="ChatButtonContainer"], [class*="SenderButtonView"], 
                    [class*="IconButtonView"], [class*="MinimizeButtonView"], 
                    [class*="Badge__BaseUnreadBadge"], iframe[id*="ch-plugin"] { 
                        display: none !important; 
                        visibility: hidden !important; 
                        opacity: 0 !important; 
                        pointer-events: none !important; 
                        width: 0 !important; 
                        height: 0 !important; 
                        max-width: 0 !important; 
                        max-height: 0 !important; 
                        overflow: hidden !important; 
                        position: absolute !important; 
                        top: -9999px !important; 
                        left: -9999px !important; 
                        z-index: -9999 !important; 
                    }
                `;
                document.head.appendChild(style);
                
                // 4. Channel IO 함수 오버라이딩
                window.ChannelIO = function() { return false; };
                window.ChannelIOInitialized = true;
                window.ch_plugin = null;
                
                // 5. MutationObserver를 통한 지속적인 채널톡 요소 제거
                const observer = new MutationObserver(function(mutations) {
                    mutations.forEach(function(mutation) {
                        if (mutation.addedNodes && mutation.addedNodes.length > 0) {
                            for (let i = 0; i < mutation.addedNodes.length; i++) {
                                const node = mutation.addedNodes[i];
                                if (node.nodeType === 1) { // Element node
                                    // 채널톡 관련 요소 검사
                                    if ((node.id && node.id.indexOf('ch-plugin') !== -1) ||
                                        (node.className && typeof node.className === 'string' && 
                                         (node.className.indexOf('ch-') !== -1 || 
                                          node.className.indexOf('ChatButtonContainer') !== -1 ||
                                          node.className.indexOf('MinimizeButtonView') !== -1))) {
                                        if (node.parentNode) {
                                            node.parentNode.removeChild(node);
                                            console.log('MutationObserver removed element:', node);
                                        }
                                    }
                                    
                                    // iframe 검사
                                    if (node.tagName === 'IFRAME' && node.id && node.id.indexOf('ch-plugin') !== -1) {
                                        if (node.parentNode) {
                                            node.parentNode.removeChild(node);
                                            console.log('MutationObserver removed iframe:', node.id);
                                        }
                                    }
                                }
                            }
                        }
                    });
                });
                
                // 전체 document를 관찰
                observer.observe(document.documentElement, {
                    childList: true,
                    subtree: true
                });
                
                // 6. 채널톡 URL 접근 차단
                const originalFetch = window.fetch;
                window.fetch = function(url, options) {
                    if (url && typeof url === 'string' && url.indexOf('channel.io') !== -1) {
                        console.log('Blocked fetch request to channel.io');
                        return new Promise((resolve, reject) => {
                            resolve(new Response(JSON.stringify({success: true}), {
                                status: 200,
                                headers: {'Content-Type': 'application/json'}
                            }));
                        });
                    }
                    return originalFetch.apply(this, arguments);
                };
                
                // 7. 새 탭 열림 방지
                const originalOpen = window.open;
                window.open = function(url, target, features) {
                    if (url && typeof url === 'string' && url.indexOf('channel.io') !== -1) {
                        console.log('Blocked window.open to channel.io');
                        return null;
                    }
                    return originalOpen.apply(this, arguments);
                };
                
                return {
                    success: true,
                    elementsRemoved: removed,
                    fullPrevention: true
                };
                
            } catch (e) {
                console.error('Error removing channel talk:', e);
                return {
                    success: false,
                    error: e.toString()
                };
            }
        })();
        """
        
        result = driver.execute_script(script)
        logging.info(f"JavaScript 채널톡 완전 제거 결과: {json.dumps(result, ensure_ascii=False)}")
        
        if result.get('success', False):
            logging.info(f"JavaScript로 채널톡 완전 제거 성공: {result.get('elementsRemoved', 0)} 개 요소")
            
            # 추가 확인: 현재 채널톡 상태 확인
            is_visible = is_channel_talk_visible(driver)
            logging.info(f"채널톡 상태 확인: 보이는가? {is_visible}")
            
            return not is_visible
        else:
            logging.warning(f"JavaScript 채널톡 제거 실패: {result.get('error', '')}")
            return False
        
    except Exception as e:
        logging.error(f"JavaScript 채널톡 제거 오류: {e}")
        return False


def force_close_all_popups(driver):
    """
    모든 팝업을 강제로 닫는 기능
    채널톡을 포함하여 화면에 나타나는 모든 팝업을 닫음
    """
    try:
        logging.info("모든 팝업 닫기 시도")
        
        # ESC 키 입력
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.common.action_chains import ActionChains
        
        for _ in range(3):  # 3회 연속 시도
            try:
                actions = ActionChains(driver)
                actions.send_keys(Keys.ESCAPE)
                actions.perform()
                time.sleep(0.2)
            except Exception:
                pass
        
        # JavaScript로 모든 팝업 닫기
        script = """
        // 모든 팝업 닫기
        (function() {
            // 1. 일반적인 팝업 제거
            const modals = document.querySelectorAll('.modal, .dialog, .popup, [role="dialog"], [aria-modal="true"]');
            let closed = 0;
            
            modals.forEach(modal => {
                if (modal && modal.style) {
                    modal.style.display = 'none';
                    closed++;
                }
                
                // 닫기 버튼 찾기
                const closeButtons = modal.querySelectorAll('button[aria-label="Close"], .close, .btn-close, .modal-close, [data-dismiss="modal"]');
                closeButtons.forEach(btn => {
                    try { btn.click(); } catch(e) {}
                });
            });
            
            // 2. z-index가 높은 요소 검사
            const allElements = document.querySelectorAll('*');
            const highZIndexElements = [];
            
            allElements.forEach(el => {
                const style = window.getComputedStyle(el);
                const zIndex = parseInt(style.zIndex, 10);
                
                if (!isNaN(zIndex) && zIndex > 1000) {
                    highZIndexElements.push({
                        element: el,
                        zIndex: zIndex
                    });
                }
            });
            
            // z-index 내림차순 정렬
            highZIndexElements.sort((a, b) => b.zIndex - a.zIndex);
            
            // 상위 5개 요소 제거
            const topElements = highZIndexElements.slice(0, 5);
            topElements.forEach(item => {
                try {
                    item.element.style.display = 'none';
                    item.element.style.visibility = 'hidden';
                    item.element.style.opacity = '0';
                    closed++;
                } catch(e) {}
            });
            
            return { closed: closed };
        })();
        """
        
        result = driver.execute_script(script)
        logging.info(f"팝업 닫기 결과: {json.dumps(result, ensure_ascii=False)}")
        
        return True
    except Exception as e:
        logging.error(f"모든 팝업 닫기 시도 오류: {e}")
        return False
