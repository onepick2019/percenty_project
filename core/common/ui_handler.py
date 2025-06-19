# -*- coding: utf-8 -*-
"""
UI 정리 및 관리 공통 함수들
주기적 UI 정리, 액션 전 UI 정리 등의 공통 기능
"""

import logging
import time
from typing import Optional
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)

def periodic_ui_cleanup(driver: WebDriver, max_attempts: Optional[int] = None) -> None:
    """
    주기적 UI 정리 작업
    모달, 팝업, 채널톡 등을 정리
    
    Args:
        driver: Selenium WebDriver 인스턴스
        max_attempts: 최대 시도 횟수 (호환성을 위한 파라미터, 현재는 무시됨)
    """
    try:
        logger.debug("주기적 UI 정리 시작")
        
        # 채널톡 숨기기
        from .modal_handler import hide_channel_talk
        hide_channel_talk(driver)
        
        # 모달 다이얼로그 닫기
        from .modal_handler import close_modal_dialogs
        close_modal_dialogs(driver)
        
        # 기타 팝업 정리
        _cleanup_popups(driver)
        
        logger.debug("주기적 UI 정리 완료")
        
    except Exception as e:
        logger.warning(f"주기적 UI 정리 중 오류: {e}")

def ensure_clean_ui_before_action(driver: WebDriver) -> None:
    """
    액션 실행 전 UI 정리
    중요한 액션 전에 UI를 깨끗하게 정리
    
    Args:
        driver: Selenium WebDriver 인스턴스
    """
    try:
        logger.debug("액션 전 UI 정리 시작")
        
        # 모든 모달과 팝업 정리
        from .modal_handler import handle_post_login_modals, hide_channel_talk, close_modal_dialogs
        
        # 로그인 후 모달 처리
        handle_post_login_modals(driver)
        
        # 채널톡 숨기기
        hide_channel_talk(driver)
        
        # 모달 다이얼로그 닫기
        close_modal_dialogs(driver)
        
        # 기타 팝업 정리
        _cleanup_popups(driver)
        
        # 짧은 대기 시간
        time.sleep(0.5)
        
        logger.debug("액션 전 UI 정리 완료")
        
    except Exception as e:
        logger.warning(f"액션 전 UI 정리 중 오류: {e}")

def _cleanup_popups(driver: WebDriver) -> None:
    """
    기타 팝업 정리
    
    Args:
        driver: Selenium WebDriver 인스턴스
    """
    try:
        # 일반적인 팝업 닫기 버튼들
        popup_close_selectors = [
            "//button[contains(@class, 'close')]",
            "//button[contains(@class, 'ant-modal-close')]",
            "//span[contains(@class, 'ant-modal-close-x')]",
            "//button[@aria-label='Close']",
            "//button[contains(text(), '닫기')]",
            "//button[contains(text(), '취소')]",
            "//div[contains(@class, 'modal')]//button[contains(@class, 'close')]"
        ]
        
        for selector in popup_close_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        element.click()
                        logger.debug(f"팝업 닫기 버튼 클릭: {selector}")
                        time.sleep(0.2)
            except Exception:
                continue
                
        # JavaScript로 모달 오버레이 제거
        try:
            js_script = """
            // 모달 오버레이 제거
            const overlays = document.querySelectorAll('.ant-modal-mask, .modal-backdrop, .overlay');
            overlays.forEach(overlay => {
                if (overlay.style) {
                    overlay.style.display = 'none';
                }
            });
            
            // 숨겨진 모달들 제거
            const modals = document.querySelectorAll('.ant-modal, .modal, [role="dialog"]');
            modals.forEach(modal => {
                if (modal.style && !modal.querySelector('.ant-modal-content:not([style*="display: none"])')) {
                    modal.style.display = 'none';
                }
            });
            """
            driver.execute_script(js_script)
            logger.debug("JavaScript로 모달 오버레이 정리 완료")
        except Exception as js_error:
            logger.debug(f"JavaScript 모달 정리 실패: {js_error}")
            
    except Exception as e:
        logger.debug(f"팝업 정리 중 오류: {e}")

def wait_for_page_load(driver: WebDriver, timeout: int = 10) -> bool:
    """
    페이지 로딩 완료 대기
    
    Args:
        driver: Selenium WebDriver 인스턴스
        timeout: 대기 시간 (초)
        
    Returns:
        bool: 로딩 완료 여부
    """
    try:
        # JavaScript로 페이지 로딩 상태 확인
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        # 추가로 jQuery가 있다면 jQuery 로딩도 확인
        try:
            WebDriverWait(driver, 2).until(
                lambda d: d.execute_script("return typeof jQuery !== 'undefined' ? jQuery.active == 0 : true")
            )
        except Exception:
            pass  # jQuery가 없는 경우 무시
            
        logger.debug("페이지 로딩 완료")
        return True
        
    except Exception as e:
        logger.warning(f"페이지 로딩 대기 중 타임아웃: {e}")
        return False

def scroll_to_element(driver: WebDriver, element) -> bool:
    """
    요소까지 스크롤
    
    Args:
        driver: Selenium WebDriver 인스턴스
        element: 스크롤할 대상 요소
        
    Returns:
        bool: 스크롤 성공 여부
    """
    try:
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        time.sleep(0.5)  # 스크롤 완료 대기
        logger.debug("요소까지 스크롤 완료")
        return True
    except Exception as e:
        logger.warning(f"요소 스크롤 실패: {e}")
        return False

def highlight_element(driver: WebDriver, element, duration: float = 1.0) -> None:
    """
    요소 하이라이트 (디버깅용)
    
    Args:
        driver: Selenium WebDriver 인스턴스
        element: 하이라이트할 요소
        duration: 하이라이트 지속 시간 (초)
    """
    try:
        # 원래 스타일 저장
        original_style = element.get_attribute("style")
        
        # 하이라이트 스타일 적용
        driver.execute_script(
            "arguments[0].style.border = '3px solid red'; arguments[0].style.backgroundColor = 'yellow';",
            element
        )
        
        # 지정된 시간만큼 대기
        time.sleep(duration)
        
        # 원래 스타일 복원
        if original_style:
            driver.execute_script(f"arguments[0].style = '{original_style}';", element)
        else:
            driver.execute_script("arguments[0].removeAttribute('style');", element)
            
        logger.debug(f"요소 하이라이트 완료 ({duration}초)")
        
    except Exception as e:
        logger.debug(f"요소 하이라이트 실패: {e}")