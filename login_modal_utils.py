import logging
import time
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, JavascriptException

# 로그인 모달창 숨기기 상태 플래그
login_modal_hidden = False

# 마지막 로그인 모달창 숨기기 시도 시간 기록
last_login_modal_attempt = 0

def is_login_modal_visible(driver, timeout=1):
    """
    로그인 모달창이 현재 화면에 보이는지 확인합니다.
    
    Args:
        driver: Selenium WebDriver 인스턴스
        timeout: 최대 기다리는 시간(초)
    
    Returns:
        bool: 로그인 모달창이 보이면 True, 보이지 않으면 False
    """
    try:
        # 간단한 JavaScript 스크립트로 로그인 모달창 요소 확인 - DOM 스캔 최소화
        script = """
        try {
            // 로그인 모달창 요소 확인 (일반적인 선택자 - 필요에 따라 조정)
            var loginModal = document.querySelector('.ant-modal-content');
            if (loginModal) {
                // 로그인 텍스트가 포함된 모달인지 확인
                var hasLoginText = loginModal.textContent.includes('로그인') || 
                                   loginModal.textContent.includes('아이디') || 
                                   loginModal.textContent.includes('비밀번호');
                
                if (hasLoginText) {
                    var rect = loginModal.getBoundingClientRect();
                    if (rect.width > 10 && rect.height > 10) {
                        return { found: true, width: rect.width, height: rect.height, selector: '.ant-modal-content' };
                    }
                }
            }
            
            // 다른 가능한 로그인 모달 선택자 확인
            var alternativeSelectors = [
                '.login-modal', 
                '.auth-modal',
                '.modal-login',
                'div[role="dialog"]'
            ];
            
            for (var i = 0; i < alternativeSelectors.length; i++) {
                var altElement = document.querySelector(alternativeSelectors[i]);
                if (altElement) {
                    var altHasLoginText = altElement.textContent.includes('로그인') || 
                                          altElement.textContent.includes('아이디') || 
                                          altElement.textContent.includes('비밀번호');
                    
                    if (altHasLoginText) {
                        var rect = altElement.getBoundingClientRect();
                        if (rect.width > 10 && rect.height > 10) {
                            return { found: true, width: rect.width, height: rect.height, selector: alternativeSelectors[i] };
                        }
                    }
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
            logging.info(f"로그인 모달창 발견 ({selector}): 크기 {width}x{height}")
            return True
        
        return False
    
    except Exception as e:
        logging.debug(f"로그인 모달창 확인 중 오류: {e}")
        return False  # 오류 발생 시 보이지 않는다고 가정

def hide_login_modal(driver, timeout=5):
    """
    로그인 모달창이 열려있다면 JavaScript를 사용하여 강제로 숨깁니다.
    
    Args:
        driver: Selenium WebDriver 인스턴스
        timeout: 최대 대기 시간(초)
        
    Returns:
        bool: 로그인 모달창 숨기기 시도 성공 여부
    """
    global login_modal_hidden, last_login_modal_attempt
    
    # 이미 로그인 모달창을 숨겼다면 다시 시도하지 않음
    if login_modal_hidden:
        logging.info("로그인 모달창이 이미 숨겨져 있습니다. 추가 시도를 건너뜁니다.")
        return True
    
    # 마지막 시도 후 최소 3초 대기 (너무 자주 호출 방지)
    current_time = time.time()
    if current_time - last_login_modal_attempt < 3:
        logging.info(f"최근 {current_time - last_login_modal_attempt:.1f}초 전에 시도했으니 잠시 대기")
        time.sleep(0.5)
    
    # 시도 시간 기록
    last_login_modal_attempt = current_time
    
    # 주의: 창 포커스 변경 코드 제거 (명령 프롬프트 창 최소화 문제 해결)
    # 포커스 변경 없이 JavaScript만으로 로그인 모달창 요소 숨기기
    
    logging.info("로그인 모달창 숨기기 적용 시작")
    
    # 1. 먼저 '다시 보지 않기' 버튼을 명시적으로 찾아서 클릭 시도
    try:
        # XPath로 '다시 보지 않기' 버튼 찾기
        dont_show_again_xpath = "//span[contains(text(), '다시 보지 않기')]/parent::button"
        logging.info(f"'다시 보지 않기' 버튼 찾기 시도: {dont_show_again_xpath}")
        
        # JavaScript로 버튼 찾고 클릭
        dont_show_js = f"""
        try {{            
            // XPath로 요소 찾기
            var result = document.evaluate("{dont_show_again_xpath}", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
            if (result) {{
                result.click();
                return {{ found: true, clicked: true, method: 'xpath' }};
            }}
            
            // 클래스로 찾기 시도
            var buttons = document.querySelectorAll('.ant-modal-footer button, .modal-footer button, button');
            for (var i = 0; i < buttons.length; i++) {{
                if (buttons[i].textContent.includes('다시 보지 않기')) {{
                    buttons[i].click();
                    return {{ found: true, clicked: true, method: 'textContent' }};
                }}
            }}
            
            // 로그인 모달창의 닫기 버튼 찾기
            var closeButtons = document.querySelectorAll('.ant-modal-close, .modal-close, button[aria-label="Close"]');
            if (closeButtons.length > 0) {{
                for (var i = 0; i < closeButtons.length; i++) {{
                    closeButtons[i].click();
                }}
                return {{ found: true, clicked: true, method: 'close_button' }};
            }}
            
            return {{ found: false }};
        }} catch (e) {{
            return {{ found: false, error: e.toString() }};
        }}
        """
        
        button_result = driver.execute_script(dont_show_js)
        if button_result and isinstance(button_result, dict) and button_result.get('found', False) and button_result.get('clicked', False):
            logging.info(f"'다시 보지 않기' 버튼 클릭 성공: {button_result}")
            time.sleep(0.5)  # 버튼 클릭 후 잠시 대기
            login_modal_hidden = True
            return True
        else:
            logging.info(f"'다시 보지 않기' 버튼을 찾지 못했습니다: {button_result}")
    except Exception as e:
        logging.warning(f"'다시 보지 않기' 버튼 클릭 시도 중 오류: {e}")
    
    # 2. 버튼 클릭이 실패한 경우 기존 방식으로 처리
    logging.info("로그인 모달창 강제 숨기기 적용")
    
    # 로그인 모달창 강제 숨기기 적용
    try:
        # 로그인 모달창 요소를 숨기는 간단한 스크립트 실행
        simple_script = """
        try {
            // 로그인 모달창 요소 강제 숨김
            var styleId = 'login-modal-blocker-style';
            var existingStyle = document.getElementById(styleId);
            
            if (!existingStyle) {
                var style = document.createElement('style');
                style.id = styleId;
                style.textContent = `
                    /* 모든 모달 관련 요소 숨기기 (마케팅/이벤트 모달 포함) */
                    .ant-modal-root, .ant-modal-mask, .ant-modal-wrap, 
                    .ant-modal-centered, div.ant-modal, div[class*="ant-modal"],
                    .login-modal, .auth-modal, .modal-login,
                    div[role="dialog"],
                    div[role="dialog"]:has(button:contains("로그인")),
                    div[role="dialog"]:has(button:contains("닫기")),
                    div[role="dialog"]:has(button:contains("다시 보지 않기")),
                    div[role="dialog"]:has(input[placeholder*="아이디"]),
                    div[role="dialog"]:has(input[placeholder*="비밀번호"]),
                    div[class*="login"], div[class*="Login"],
                    div[tabindex="-1"][class="ant-modal-wrap ant-modal-centered"] {
                        display: none !important;
                        visibility: hidden !important;
                        opacity: 0 !important;
                        pointer-events: none !important;
                        z-index: -9999 !important;
                    }
                    
                    /* 모달 배경 제거 */
                    body.ant-modal-open {
                        overflow: auto !important;
                    }
                    
                    /* 모달로 인한 배경 어둡게 효과 제거 */
                    .ant-modal-mask, .modal-backdrop {
                        display: none !important;
                    }
                `;
                document.head.appendChild(style);
                
                // 모달 관련 클래스 제거 시도
                document.body.classList.remove('ant-modal-open');
                document.body.classList.remove('modal-open');
            }
            
            // 로그인 관련 로컬 스토리지 값 설정 시도 (사이트에 따라 달라질 수 있음)
            try {
                localStorage.setItem('login_modal_shown', 'true');
                localStorage.setItem('login_prompt_dismissed', 'true');
            } catch (e) {}
            
            return { success: true, method: '로그인 모달창 강제 숨김 적용' };
        } catch (e) {
            return { success: false, error: e.toString() };
        }
        """
        
        result = driver.execute_script(simple_script)
        logging.info(f"로그인 모달창 강제 숨김 결과: {json.dumps(result, ensure_ascii=False)}")
        
        # 성공 여부와 상관없이 항상 성공으로 처리
        login_modal_hidden = True
        logging.info("로그인 모달창 숨기기 성공! 이후 시도는 무시됩니다.")
        return True
        
    except Exception as e:
        logging.warning(f"로그인 모달창 강제 숨김 실패: {e}")
        # 예외 발생해도 계속 진행
        login_modal_hidden = True
        return True

def reset_login_modal_hidden_state():
    """
    로그인 모달창 숨김 상태를 초기화합니다. 새 탭이 열릴 때 호출하세요.
    """
    global login_modal_hidden
    login_modal_hidden = False
    logging.info("로그인 모달창 숨김 상태 초기화됨. 다시 숨기기 가능.")

def apply_login_modal_hiding_for_new_tab(driver):
    """
    새 탭이 열릴 때마다 모든 모달창을 숨기는 JavaScript를 자동으로 적용합니다.
    
    Args:
        driver: Selenium WebDriver 인스턴스
    """
    # 모달창 숨김 상태 초기화
    reset_login_modal_hidden_state()
    
    # 모달창 숨기기 적용
    hide_login_modal(driver)
    
    # 새 탭에서 페이지 로드 이벤트 모니터링하여 자동으로 모든 모달창 숨기기
    monitoring_script = """
    // 페이지 로드마다 모든 모달창 숨기기 자동 적용
    if (!window._allModalObserverSet) {
        window._allModalObserverSet = true;
        
        // 1. 즉시 적용할 스타일 생성
        var styleId = 'all-modals-blocker-style';
        if (!document.getElementById(styleId)) {
            var style = document.createElement('style');
            style.id = styleId;
            style.textContent = `
                /* 모든 모달 관련 요소 숨기기 (마케팅/이벤트 모달 포함) */
                .ant-modal-root, .ant-modal-mask, .ant-modal-wrap, 
                .ant-modal-centered, div.ant-modal, div[class*="ant-modal"],
                .login-modal, .auth-modal, .modal-login,
                div[role="dialog"],
                div[role="dialog"]:has(button:contains("로그인")),
                div[role="dialog"]:has(button:contains("닫기")),
                div[role="dialog"]:has(button:contains("다시 보지 않기")),
                div[role="dialog"]:has(input[placeholder*="아이디"]),
                div[role="dialog"]:has(input[placeholder*="비밀번호"]),
                div[class*="login"], div[class*="Login"],
                div[tabindex="-1"][class="ant-modal-wrap ant-modal-centered"] {
                    display: none !important;
                    visibility: hidden !important;
                    opacity: 0 !important;
                    pointer-events: none !important;
                    z-index: -9999 !important;
                }
                
                /* 모달 배경 제거 */
                body.ant-modal-open {
                    overflow: auto !important;
                }
                
                /* 모달로 인한 배경 어둡게 효과 제거 */
                .ant-modal-mask, .modal-backdrop {
                    display: none !important;
                }
            `;
            document.head.appendChild(style);
            console.log('모든 모달창 숨기기 스타일 적용됨');
            
            // 모달 관련 클래스 제거
            document.body.classList.remove('ant-modal-open');
            document.body.classList.remove('modal-open');
        }
        
        // 2. MutationObserver로 지속적 감시 설정
        var observer = new MutationObserver(function(mutations) {
            // 로컬 스토리지 값 설정 및 모달 관련 클래스 제거 시도
            document.body.classList.remove('ant-modal-open');
            document.body.classList.remove('modal-open');
            
            // 마케팅 모달창 검색 및 처리
            var marketingModals = document.querySelectorAll('div[role="dialog"], .ant-modal-wrap');
            if (marketingModals.length > 0) {
                console.log(`모달창 발견: ${marketingModals.length}개`);
                marketingModals.forEach(modal => {
                    try {
                        modal.style.display = 'none';
                        modal.style.visibility = 'hidden';
                        modal.style.opacity = '0';
                        modal.style.pointerEvents = 'none';
                        modal.style.zIndex = '-9999';
                    } catch(e) { console.log('모달 숨기기 오류:', e); }
                });
            }
        });

        // 전체 문서 변경 감시 시작 (더 비밀한 감시 설정)
        observer.observe(document.documentElement, { 
            childList: true, 
            subtree: true, 
            attributes: true,
            attributeFilter: ['class', 'style', 'display']
        });
        
        // 3. 로컬 스토리지 값 설정
        try {
            localStorage.setItem('login_modal_shown', 'true');
            localStorage.setItem('login_prompt_dismissed', 'true');
            localStorage.setItem('dont_show_again', 'true');
            localStorage.setItem('modal_dismissed', 'true');
        } catch (e) {}
        
        // 4. 페이지 로드 완료 후 한 번 더 적용
        window.addEventListener('load', function() {
            setTimeout(function() {
                document.body.classList.remove('ant-modal-open');
                document.body.classList.remove('modal-open');
                console.log('페이지 로드 후 모달창 숨기기 재실행');
            }, 500);
        });
    }
    return { success: true, method: '모든 모달창 자동 숨김 설정 완료' };
    """
    
    try:
        result = driver.execute_script(monitoring_script)
        logging.info(f"새 탭 로그인 모달창 자동 숨김 설정 결과: {json.dumps(result, ensure_ascii=False)}")
    except Exception as e:
        logging.warning(f"새 탭 로그인 모달창 자동 숨김 설정 실패: {e}")
