# -*- coding: utf-8 -*-
"""
모달 처리 공통 함수들
로그인 후 모달창 처리, 채널톡 숨기기 등의 공통 기능
"""

import logging
import time
from typing import Optional
from selenium.webdriver.remote.webdriver import WebDriver

logger = logging.getLogger(__name__)

def handle_post_login_modals(driver: WebDriver) -> bool:
    """
    로그인 후 모달창 처리
    
    Args:
        driver: Selenium WebDriver 인스턴스
        
    Returns:
        bool: 처리 성공 여부
    """
    try:
        logger.info("로그인 후 모달창 처리 시작...")
        
        # 로그인 모달창 처리
        try:
            from percenty_utils import hide_login_modal
            hide_login_modal(driver)
            logger.info("로그인 모달창 처리 성공")
        except Exception as e:
            logger.warning(f"로그인 모달창 처리 중 오류: {e}")
        
        # 모달창 차단 스크립트 적용
        try:
            from modal_blocker import block_modals_on_page
            block_modals_on_page(driver)
            logger.info("모달창 차단 스크립트 적용 완료")
        except Exception as e:
            logger.warning(f"모달창 차단 스크립트 적용 중 오류: {e}")
        
        # 모달창 처리 후 대기
        time.sleep(1.0)
        logger.info("모달창 처리 완료")
        return True
        
    except Exception as e:
        logger.error(f"모달창 처리 중 전체 오류: {e}")
        return False

def hide_channel_talk(driver: WebDriver) -> bool:
    """
    채널톡 숨기기
    
    Args:
        driver: Selenium WebDriver 인스턴스
        
    Returns:
        bool: 처리 성공 여부
    """
    try:
        from channel_talk_utils import check_and_hide_channel_talk
        return check_and_hide_channel_talk(driver)
    except Exception as e:
        logger.error(f"채널톡 숨기기 중 오류: {e}")
        return False

def close_modal_dialogs(driver: WebDriver) -> bool:
    """
    일반 모달 대화상자 닫기
    
    Args:
        driver: Selenium WebDriver 인스턴스
        
    Returns:
        bool: 처리 성공 여부
    """
    try:
        from modal_blocker import close_modal_dialog
        result = close_modal_dialog(driver)
        return result.get('success', True) if isinstance(result, dict) else True
    except Exception as e:
        logger.error(f"모달 대화상자 닫기 중 오류: {e}")
        return False