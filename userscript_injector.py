#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
퍼센티 자동화 - 모달창 자동 숨김 스크립트 인젝터

이 모듈은 브라우저에 자동 모달창 숨김 기능을 영구적으로 적용하는 스크립트를 삽입합니다.
새 탭이나 페이지 로드, 새로고침 등 모든 상황에서 모달창이 자동으로 숨겨집니다.
"""

import logging
import json
import time

def inject_permanent_modal_hiding_script(driver):
    """
    브라우저에 모달창 자동 숨김 스크립트를 영구적으로 삽입합니다.
    
    이 스크립트는 새 탭이나 페이지 로드 시 자동으로 활성화되어 모든 모달창을 숨깁니다.
    
    Args:
        driver: Selenium WebDriver 인스턴스
    
    Returns:
        dict: 스크립트 삽입 결과
    """
    logging.info("영구적 모달창 숨김 스크립트 삽입 시작")
    
    # 영구 스크립트 삽입 - localStorage 사용
    script = """
    try {
        // 이미 실행 중인지 확인
        if (window._modalHiderInstalled) {
            return { success: true, message: '이미 모달창 숨김 스크립트가 실행 중입니다', method: 'already_running' };
        }
        
        // 영구 스크립트 설치 표시
        window._modalHiderInstalled = true;
        
        // 1. 즉시 적용할 스타일 추가
        let styleId = 'percenty-modal-hider-style';
        if (!document.getElementById(styleId)) {
            let style = document.createElement('style');
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
            console.log('[모달숨김] 스타일 적용됨');
        }
        
        // 2. 이벤트 등록 - 페이지 로드될 때마다 모달 요소 확인
        const applyModalHiding = () => {
            // 모달 관련 클래스 제거
            document.body.classList.remove('ant-modal-open');
            document.body.classList.remove('modal-open');
            
            // 로컬 스토리지에 모달 관련 플래그 설정
            try {
                localStorage.setItem('login_modal_shown', 'true');
                localStorage.setItem('login_prompt_dismissed', 'true');
                localStorage.setItem('dont_show_again', 'true');
                localStorage.setItem('modal_dismissed', 'true');
            } catch (e) {}
            
            // 모달창 직접 찾아서 스타일 적용
            const modals = document.querySelectorAll('div[role="dialog"], .ant-modal-wrap, .ant-modal');
            if (modals.length > 0) {
                console.log(`[모달숨김] ${modals.length}개 모달창 발견, 숨김 처리 적용`);
                modals.forEach(modal => {
                    try {
                        modal.style.display = 'none';
                        modal.style.visibility = 'hidden';
                        modal.style.opacity = '0';
                        modal.style.pointerEvents = 'none';
                        modal.style.zIndex = '-9999';
                    } catch(e) {}
                });
            }
        };
        
        // 3. 스크립트를 localStorage에 저장 (새 페이지, 새 탭에서도 실행되도록)
        try {
            // 현재 스크립트를 자동 실행 함수로 래핑하여 localStorage에 저장
            const autoExecScript = `
            // 퍼센티 모달창 자동 숨김 스크립트 (자동 실행)
            (function() {
                console.log('[모달숨김] 자동 실행 스크립트 시작');
                
                // 스타일 태그 생성 및 추가
                let styleId = 'percenty-modal-hider-style';
                if (!document.getElementById(styleId)) {
                    let style = document.createElement('style');
                    style.id = styleId;
                    style.textContent = \`
                        /* 모든 모달 관련 요소 숨기기 */
                        .ant-modal-root, .ant-modal-mask, .ant-modal-wrap, 
                        .ant-modal-centered, div.ant-modal, div[class*="ant-modal"],
                        .login-modal, .auth-modal, .modal-login,
                        div[role="dialog"],
                        div[tabindex="-1"][class="ant-modal-wrap ant-modal-centered"] {
                            display: none !important;
                            visibility: hidden !important;
                            opacity: 0 !important;
                            pointer-events: none !important;
                            z-index: -9999 !important;
                        }
                        
                        body.ant-modal-open {
                            overflow: auto !important;
                        }
                        
                        .ant-modal-mask, .modal-backdrop {
                            display: none !important;
                        }
                    \`;
                    document.head.appendChild(style);
                }
                
                // 모달 관련 클래스 제거
                document.body.classList.remove('ant-modal-open');
                document.body.classList.remove('modal-open');
                
                // 로컬 스토리지 값 설정
                try {
                    localStorage.setItem('login_modal_shown', 'true');
                    localStorage.setItem('login_prompt_dismissed', 'true');
                    localStorage.setItem('dont_show_again', 'true');
                    localStorage.setItem('modal_dismissed', 'true');
                } catch (e) {}
                
                // MutationObserver 설정
                const observer = new MutationObserver(function(mutations) {
                    document.body.classList.remove('ant-modal-open');
                    document.body.classList.remove('modal-open');
                    
                    // 모달창 찾아서 직접 숨기기
                    const modals = document.querySelectorAll('div[role="dialog"], .ant-modal-wrap, .ant-modal');
                    if (modals.length > 0) {
                        modals.forEach(modal => {
                            try {
                                modal.style.display = 'none';
                                modal.style.visibility = 'hidden';
                                modal.style.opacity = '0';
                                modal.style.pointerEvents = 'none';
                                modal.style.zIndex = '-9999';
                            } catch(e) {}
                        });
                    }
                });
                
                // 문서 변경 감시 시작
                observer.observe(document.documentElement, { 
                    childList: true, 
                    subtree: true, 
                    attributes: true
                });
            })();
            `;
            
            // localStorage에 스크립트 저장
            localStorage.setItem('percenty_modal_hider_script', autoExecScript);
            console.log('[모달숨김] 스크립트가 localStorage에 저장됨');
        } catch (e) {
            console.log('[모달숨김] localStorage 저장 실패:', e);
        }
        
        // 4. 페이지 로드 및 DOM 변경 이벤트 리스너 등록
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', applyModalHiding);
        } else {
            applyModalHiding();
        }
        
        window.addEventListener('load', applyModalHiding);
        
        // 5. MutationObserver 설정
        const observer = new MutationObserver(function(mutations) {
            applyModalHiding();
        });
        
        // 문서 변경 감시 시작
        observer.observe(document.documentElement, { 
            childList: true, 
            subtree: true, 
            attributes: true
        });
        
        // 6. 새 탭에서도 자동 실행되도록 설정
        try {
            const scriptTag = `
            <script>
                // 새 탭에서 자동 실행되는 모달창 숨김 스크립트
                document.addEventListener('DOMContentLoaded', function() {
                    // localStorage에서 스크립트 로드 및 실행
                    try {
                        const savedScript = localStorage.getItem('percenty_modal_hider_script');
                        if (savedScript) {
                            console.log('[모달숨김] localStorage에서 스크립트 로드');
                            eval(savedScript);
                        }
                    } catch (e) {
                        console.log('[모달숨김] 스크립트 실행 오류:', e);
                    }
                });
            </script>
            `;
            
            // 스크립트 태그 삽입
            document.head.insertAdjacentHTML('beforeend', scriptTag);
        } catch (e) {
            console.log('[모달숨김] 스크립트 태그 삽입 실패:', e);
        }
        
        return { 
            success: true, 
            message: '모달창 영구 숨김 스크립트 설치 완료',
            method: 'permanent_script_installed'
        };
    } catch (e) {
        return { 
            success: false, 
            message: '모달창 영구 숨김 스크립트 설치 실패: ' + e.toString(),
            error: e.toString()
        };
    }
    """
    
    try:
        # 스크립트 실행
        result = driver.execute_script(script)
        logging.info(f"영구적 모달창 숨김 스크립트 삽입 결과: {json.dumps(result, ensure_ascii=False)}")
        return result
    except Exception as e:
        logging.error(f"영구적 모달창 숨김 스크립트 삽입 실패: {e}")
        return {
            "success": False,
            "message": f"스크립트 삽입 오류: {str(e)}",
            "error": str(e)
        }

def inject_modal_hiding_to_all_tabs(driver):
    """
    현재 열린 모든 탭에 모달창 숨김 스크립트를 적용합니다.
    
    Args:
        driver: Selenium WebDriver 인스턴스
    """
    logging.info("모든 탭에 모달창 숨김 스크립트 적용 시작")
    
    try:
        # 현재 탭 핸들 저장
        current_handle = driver.current_window_handle
        
        # 모든 탭 핸들 가져오기
        all_handles = driver.window_handles
        
        # 각 탭에 스크립트 적용
        for handle in all_handles:
            try:
                # 해당 탭으로 전환
                driver.switch_to.window(handle)
                
                # 모달창 숨김 스크립트 삽입
                result = inject_permanent_modal_hiding_script(driver)
                logging.info(f"탭 {handle} 모달창 숨김 스크립트 적용 결과: {json.dumps(result, ensure_ascii=False)}")
                
                # 짧은 대기 (안정성을 위해)
                time.sleep(0.5)
            except Exception as tab_e:
                logging.error(f"탭 {handle} 모달창 숨김 스크립트 적용 실패: {tab_e}")
        
        # 원래 탭으로 복귀
        driver.switch_to.window(current_handle)
        logging.info("모든 탭에 모달창 숨김 스크립트 적용 완료")
        
    except Exception as e:
        logging.error(f"모든 탭에 모달창 숨김 스크립트 적용 중 오류: {e}")

def setup_browser_for_modal_hiding(driver):
    """
    브라우저에 모달창 자동 숨김 기능을 설정합니다.
    
    새 탭이 열리거나 페이지가 로드될 때마다 모달창이 자동으로 숨겨집니다.
    
    Args:
        driver: Selenium WebDriver 인스턴스
    """
    # 1. 현재 탭에 영구적 모달창 숨김 스크립트 삽입
    inject_permanent_modal_hiding_script(driver)
    
    # 2. 모든 탭에 적용 (여러 탭이 열려 있는 경우)
    inject_modal_hiding_to_all_tabs(driver)
    
    # 3. 자동 적용을 위한 스크립트 적용
    logging.info("새 탭 자동 모달창 숨김 설정 완료")
    
    return True

# 테스트 코드
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logging.info("모달창 자동 숨김 스크립트 테스트")
    
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
        
        # 모달창 숨김 스크립트 적용
        setup_browser_for_modal_hiding(driver)
        
        # 결과 대기
        logging.info("스크립트 적용 완료. 테스트를 위해 10초 동안 대기...")
        time.sleep(10)
        
        # 새 탭 열기 및 테스트
        driver.execute_script("window.open('https://www.percenty.co.kr/', '_blank');")
        
        # 결과 대기
        logging.info("새 탭에서 테스트 중. 20초 동안 대기...")
        time.sleep(20)
        
        # 브라우저 종료
        driver.quit()
        
    except Exception as e:
        logging.error(f"테스트 중 오류 발생: {e}")
