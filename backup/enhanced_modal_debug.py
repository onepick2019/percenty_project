#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
개선된 모달창 처리 디버깅 스크립트

분석 결과를 바탕으로 모달창 처리 문제를 해결하기 위한 개선된 디버깅을 수행합니다.
"""

import sys
import os
import logging
import time
import traceback
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 로깅 설정
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_modal_debug.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_browser_health(driver):
    """
    브라우저 상태를 확인합니다.
    """
    try:
        logger.info("=== 브라우저 상태 확인 시작 ===")
        
        # 1. 드라이버 연결 상태 확인
        current_url = driver.current_url
        logger.info(f"현재 URL: {current_url}")
        
        # 2. 페이지 로드 상태 확인
        ready_state = driver.execute_script("return document.readyState")
        logger.info(f"페이지 로드 상태: {ready_state}")
        
        # 3. JavaScript 실행 가능 여부 확인
        js_test = driver.execute_script("return 'JavaScript 실행 가능'")
        logger.info(f"JavaScript 테스트: {js_test}")
        
        # 4. 페이지 제목 확인
        title = driver.title
        logger.info(f"페이지 제목: {title}")
        
        # 5. 브라우저 창 크기 확인
        window_size = driver.get_window_size()
        logger.info(f"브라우저 창 크기: {window_size}")
        
        logger.info("=== 브라우저 상태 확인 완료 - 정상 ===")
        return True
        
    except Exception as e:
        logger.error(f"브라우저 상태 확인 중 오류: {e}")
        logger.error(f"상세 오류: {traceback.format_exc()}")
        return False

def check_modal_elements(driver):
    """
    모달창 관련 요소들을 확인합니다.
    """
    try:
        logger.info("=== 모달창 요소 확인 시작 ===")
        
        # 1. 로그인 모달 관련 요소 확인
        login_modal_selectors = [
            "div[class*='modal']",
            "div[class*='popup']",
            "div[class*='dialog']",
            "div[id*='modal']",
            "div[id*='popup']",
            "div[id*='login']",
            "button[class*='close']",
            "button[class*='cancel']",
            "span[class*='close']",
            "a[class*='close']"
        ]
        
        found_elements = []
        for selector in login_modal_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    logger.info(f"발견된 요소 ({selector}): {len(elements)}개")
                    for i, element in enumerate(elements[:3]):  # 최대 3개까지만 로깅
                        try:
                            tag_name = element.tag_name
                            class_name = element.get_attribute('class') or 'None'
                            id_attr = element.get_attribute('id') or 'None'
                            text = element.text[:50] if element.text else 'None'
                            is_displayed = element.is_displayed()
                            logger.info(f"  요소 {i+1}: {tag_name}, class='{class_name}', id='{id_attr}', text='{text}', displayed={is_displayed}")
                            found_elements.append({
                                'selector': selector,
                                'element': element,
                                'tag_name': tag_name,
                                'class': class_name,
                                'id': id_attr,
                                'text': text,
                                'displayed': is_displayed
                            })
                        except Exception as elem_e:
                            logger.warning(f"  요소 {i+1} 정보 확인 중 오류: {elem_e}")
            except Exception as e:
                logger.debug(f"선택자 '{selector}' 확인 중 오류: {e}")
        
        # 2. 채널톡 관련 요소 확인
        channel_talk_selectors = [
            "div[id*='channel']",
            "div[class*='channel']",
            "iframe[src*='channel']",
            "div[id*='chat']",
            "div[class*='chat']"
        ]
        
        for selector in channel_talk_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    logger.info(f"채널톡 요소 발견 ({selector}): {len(elements)}개")
                    for i, element in enumerate(elements[:2]):  # 최대 2개까지만 로깅
                        try:
                            tag_name = element.tag_name
                            class_name = element.get_attribute('class') or 'None'
                            id_attr = element.get_attribute('id') or 'None'
                            is_displayed = element.is_displayed()
                            logger.info(f"  채널톡 요소 {i+1}: {tag_name}, class='{class_name}', id='{id_attr}', displayed={is_displayed}")
                        except Exception as elem_e:
                            logger.warning(f"  채널톡 요소 {i+1} 정보 확인 중 오류: {elem_e}")
            except Exception as e:
                logger.debug(f"채널톡 선택자 '{selector}' 확인 중 오류: {e}")
        
        # 3. "다시 보지 않기" 버튼 확인
        dont_show_selectors = [
            "//button[contains(text(), '다시 보지 않기')]",
            "//span[contains(text(), '다시 보지 않기')]",
            "//a[contains(text(), '다시 보지 않기')]",
            "//div[contains(text(), '다시 보지 않기')]",
            "//button[contains(text(), '닫기')]",
            "//span[contains(text(), '닫기')]",
            "//button[contains(text(), '확인')]"
        ]
        
        for xpath in dont_show_selectors:
            try:
                elements = driver.find_elements(By.XPATH, xpath)
                if elements:
                    logger.info(f"'다시 보지 않기' 관련 요소 발견 ({xpath}): {len(elements)}개")
                    for i, element in enumerate(elements[:2]):
                        try:
                            tag_name = element.tag_name
                            text = element.text[:30] if element.text else 'None'
                            is_displayed = element.is_displayed()
                            is_enabled = element.is_enabled()
                            logger.info(f"  버튼 요소 {i+1}: {tag_name}, text='{text}', displayed={is_displayed}, enabled={is_enabled}")
                        except Exception as elem_e:
                            logger.warning(f"  버튼 요소 {i+1} 정보 확인 중 오류: {elem_e}")
            except Exception as e:
                logger.debug(f"XPath '{xpath}' 확인 중 오류: {e}")
        
        logger.info(f"=== 모달창 요소 확인 완료 - 총 {len(found_elements)}개 요소 발견 ===")
        return found_elements
        
    except Exception as e:
        logger.error(f"모달창 요소 확인 중 오류: {e}")
        logger.error(f"상세 오류: {traceback.format_exc()}")
        return []

def test_modal_hiding_with_detailed_logging(driver):
    """
    상세한 로깅과 함께 모달창 숨기기를 테스트합니다.
    """
    try:
        logger.info("=== 상세 로깅과 함께 모달창 숨기기 테스트 시작 ===")
        
        # 1. 브라우저 상태 확인
        if not check_browser_health(driver):
            logger.error("브라우저 상태가 비정상입니다")
            return False
        
        # 2. 모달창 요소 확인
        modal_elements = check_modal_elements(driver)
        
        # 3. hide_login_modal 함수 테스트
        logger.info("=== hide_login_modal 함수 테스트 시작 ===")
        try:
            from login_modal_utils import hide_login_modal, login_modal_hidden, last_login_modal_attempt
            
            logger.info(f"테스트 전 상태 - login_modal_hidden: {login_modal_hidden}, last_login_modal_attempt: {last_login_modal_attempt}")
            
            # 함수 실행 전 시간 기록
            start_time = time.time()
            
            # hide_login_modal 실행
            result = hide_login_modal(driver)
            
            # 실행 시간 계산
            execution_time = time.time() - start_time
            
            logger.info(f"hide_login_modal 실행 결과: {result}, 실행 시간: {execution_time:.2f}초")
            
            # 실행 후 상태 확인
            from login_modal_utils import login_modal_hidden as post_hidden, last_login_modal_attempt as post_attempt
            logger.info(f"테스트 후 상태 - login_modal_hidden: {post_hidden}, last_login_modal_attempt: {post_attempt}")
            
        except Exception as e:
            logger.error(f"hide_login_modal 테스트 중 오류: {e}")
            logger.error(f"상세 오류: {traceback.format_exc()}")
        
        # 4. handle_post_login_modals 함수 테스트
        logger.info("=== handle_post_login_modals 함수 테스트 시작 ===")
        try:
            from core.common.modal_handler import handle_post_login_modals
            
            # 함수 실행 전 시간 기록
            start_time = time.time()
            
            # handle_post_login_modals 실행
            result = handle_post_login_modals(driver)
            
            # 실행 시간 계산
            execution_time = time.time() - start_time
            
            logger.info(f"handle_post_login_modals 실행 결과: {result}, 실행 시간: {execution_time:.2f}초")
            
        except Exception as e:
            logger.error(f"handle_post_login_modals 테스트 중 오류: {e}")
            logger.error(f"상세 오류: {traceback.format_exc()}")
        
        # 5. 테스트 후 모달창 요소 재확인
        logger.info("=== 테스트 후 모달창 요소 재확인 ===")
        post_modal_elements = check_modal_elements(driver)
        
        # 6. 변화 비교
        logger.info(f"모달창 요소 변화: 이전 {len(modal_elements)}개 -> 이후 {len(post_modal_elements)}개")
        
        logger.info("=== 상세 로깅과 함께 모달창 숨기기 테스트 완료 ===")
        return True
        
    except Exception as e:
        logger.error(f"모달창 숨기기 테스트 중 오류: {e}")
        logger.error(f"상세 오류: {traceback.format_exc()}")
        return False

def test_enhanced_modal_debugging():
    """
    개선된 모달창 디버깅을 수행합니다.
    """
    logger.info("=== 개선된 모달창 디버깅 시작 ===")
    
    driver = None
    try:
        # 1. 브라우저 초기화
        logger.info("1. 브라우저 초기화 시작")
        from browser_core import BrowserCore
        
        browser_core = BrowserCore()
        browser_core.setup_driver()
        driver = browser_core.driver
        
        if not driver:
            logger.error("브라우저 드라이버 초기화 실패")
            return False
        
        logger.info("브라우저 드라이버 초기화 성공")
        
        # 2. 충분한 대기 시간 추가
        logger.info("2. 브라우저 안정화를 위한 대기 (5초)")
        time.sleep(5)
        
        # 3. 테스트 페이지로 이동 (로컬 HTML 파일)
        logger.info("3. 테스트 페이지로 이동")
        test_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>모달창 테스트 페이지</title>
            <style>
                .modal { display: block; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.5); }
                .modal-content { background-color: white; margin: 15% auto; padding: 20px; border: 1px solid #888; width: 300px; }
                .close { color: #aaa; float: right; font-size: 28px; font-weight: bold; cursor: pointer; }
            </style>
        </head>
        <body>
            <h1>모달창 테스트 페이지</h1>
            
            <!-- 로그인 모달 -->
            <div id="loginModal" class="modal">
                <div class="modal-content">
                    <span class="close" onclick="closeModal()">&times;</span>
                    <h2>로그인 모달</h2>
                    <p>이것은 테스트용 로그인 모달입니다.</p>
                    <button onclick="closeModal()">다시 보지 않기</button>
                    <button onclick="closeModal()">닫기</button>
                </div>
            </div>
            
            <!-- 채널톡 시뮬레이션 -->
            <div id="channelTalk" style="position: fixed; bottom: 20px; right: 20px; width: 60px; height: 60px; background-color: blue; border-radius: 50%; z-index: 999;">
                <span style="color: white; line-height: 60px; text-align: center; display: block;">Chat</span>
            </div>
            
            <script>
                function closeModal() {
                    document.getElementById('loginModal').style.display = 'none';
                    console.log('모달창이 닫혔습니다');
                }
                
                // 페이지 로드 완료 표시
                document.addEventListener('DOMContentLoaded', function() {
                    console.log('테스트 페이지 로드 완료');
                });
            </script>
        </body>
        </html>
        """
        
        # HTML 파일을 data URL로 로드
        import base64
        encoded_html = base64.b64encode(test_html.encode('utf-8')).decode('utf-8')
        data_url = f"data:text/html;base64,{encoded_html}"
        
        driver.get(data_url)
        logger.info("테스트 페이지 로드 완료")
        
        # 4. 페이지 로드 완료 대기
        logger.info("4. 페이지 로드 완료 대기")
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        logger.info("페이지 로드 완료 확인")
        
        # 5. 추가 안정화 대기
        logger.info("5. 추가 안정화 대기 (3초)")
        time.sleep(3)
        
        # 6. 모달창 숨기기 테스트 실행
        logger.info("6. 모달창 숨기기 테스트 실행")
        test_result = test_modal_hiding_with_detailed_logging(driver)
        
        if test_result:
            logger.info("모달창 숨기기 테스트 성공")
        else:
            logger.warning("모달창 숨기기 테스트에서 문제 발견")
        
        # 7. 실제 percenty 사이트 테스트 (네트워크 연결이 가능한 경우)
        logger.info("7. 실제 percenty 사이트 테스트 시도")
        try:
            driver.get("https://www.percenty.com/login")
            logger.info("percenty 사이트 접속 성공")
            
            # 페이지 로드 대기
            WebDriverWait(driver, 15).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            # 추가 대기 (모달창 로드 시간 고려)
            time.sleep(5)
            
            # 실제 사이트에서 모달창 테스트
            real_site_result = test_modal_hiding_with_detailed_logging(driver)
            
            if real_site_result:
                logger.info("실제 사이트에서 모달창 테스트 성공")
            else:
                logger.warning("실제 사이트에서 모달창 테스트 문제 발견")
                
        except Exception as e:
            logger.warning(f"실제 사이트 테스트 중 오류 (네트워크 문제일 수 있음): {e}")
        
        logger.info("=== 개선된 모달창 디버깅 완료 ===")
        return True
        
    except Exception as e:
        logger.error(f"개선된 모달창 디버깅 중 오류: {e}")
        logger.error(f"상세 오류: {traceback.format_exc()}")
        return False
        
    finally:
        # 브라우저 정리
        if driver:
            try:
                logger.info("브라우저 정리 중...")
                driver.quit()
                logger.info("브라우저 정리 완료")
            except Exception as e:
                logger.warning(f"브라우저 정리 중 오류: {e}")

if __name__ == "__main__":
    print("개선된 모달창 처리 디버깅 스크립트")
    print("상세한 로깅과 함께 모달창 처리 문제를 분석합니다.")
    
    success = test_enhanced_modal_debugging()
    
    if success:
        print("\n디버깅 완료. 로그 파일 'enhanced_modal_debug.log'를 확인하세요.")
    else:
        print("\n디버깅 중 오류 발생. 로그 파일을 확인하세요.")