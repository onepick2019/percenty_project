# -*- coding: utf-8 -*-
"""
네비게이션 처리 공통 함수들
AI 소싱 메뉴 이동, 그룹상품관리 이동 등의 공통 기능
"""

import logging
import time
from typing import Optional
from selenium.webdriver.remote.webdriver import WebDriver

logger = logging.getLogger(__name__)

def navigate_to_ai_sourcing(driver: WebDriver, menu_clicks_instance=None) -> bool:
    """
    AI 소싱 메뉴로 이동 (중앙집중식 관리)
    
    Args:
        driver: Selenium WebDriver 인스턴스
        menu_clicks_instance: MenuClicks 인스턴스 (선택사항)
        
    Returns:
        bool: 성공 여부
    """
    try:
        logger.info("AI 소싱 메뉴 클릭 시도...")
        
        # MenuClicks 인스턴스가 있으면 사용
        if menu_clicks_instance:
            success = menu_clicks_instance.click_ai_sourcing()
        else:
            # 직접 클릭 시도
            from menu_clicks import MenuClicks
            menu_clicks = MenuClicks(driver)
            success = menu_clicks.click_ai_sourcing()
        
        if success:
            time.sleep(3.0)
            logger.info("AI 소싱 메뉴 클릭 완료")
            return True
        else:
            logger.warning("MenuClicks를 통한 AI 소싱 메뉴 클릭 실패, DOM 직접 접근 시도")
            raise Exception("MenuClicks 실패")
        
    except Exception as e:
        logger.error(f"AI 소싱 메뉴 클릭 중 오류: {e}")
        
        # 실패시 DOM 선택자로 재시도
        try:
            logger.info("DOM 선택자로 AI 소싱 메뉴 클릭 재시도...")
            from ui_elements import UI_ELEMENTS
            from click_utils import smart_click
            from timesleep import DELAY_SHORT
            
            element_info = UI_ELEMENTS["PRODUCT_AISOURCING"]
            # 좌표는 사용하지 않고 DOM 선택자만 사용
            modified_element_info = element_info.copy()
            modified_element_info["fallback_order"] = ["dom"]
            
            success = smart_click(driver, modified_element_info, delay=DELAY_SHORT)
            
            if success:
                logger.info("AI 소싱 메뉴 smart_click(DOM만) 성공")
                time.sleep(3.0)
                return True
            else:
                logger.error("DOM 선택자로 AI 소싱 메뉴 클릭 실패")
                return False
        except Exception as inner_e:
            logger.error(f"DOM 선택자로 메뉴 클릭 재시도 시 오류: {inner_e}")
            return False

def navigate_to_group_management(driver: WebDriver, menu_clicks_instance=None) -> None:
    """
    그룹상품관리 화면으로 이동
    
    Args:
        driver: Selenium WebDriver 인스턴스
        menu_clicks_instance: MenuClicks 인스턴스 (선택사항)
    """
    try:
        logger.info("그룹상품관리 화면으로 이동 시도")
        
        # MenuClicks 인스턴스가 있으면 사용
        if menu_clicks_instance:
            menu_clicks_instance.click_group_management()
        else:
            # 직접 클릭 시도
            from menu_clicks import MenuClicks
            menu_clicks = MenuClicks(driver)
            menu_clicks.click_group_management()
        
        time.sleep(3.0)
        logger.info("그룹상품관리 화면 이동 완료")
        
    except Exception as e:
        logger.error(f"그룹상품관리 화면 이동 중 오류: {e}")
        raise

def navigate_to_group_management5(driver: WebDriver, menu_clicks_instance=None) -> bool:
    """
    5단계 전용: 그룹상품관리 화면으로만 이동 (비그룹상품보기 전환 없음)
    
    Args:
        driver: Selenium WebDriver 인스턴스
        menu_clicks_instance: MenuClicks 인스턴스 (선택사항)
        
    Returns:
        bool: 성공 여부
    """
    try:
        logger.info("그룹상품관리 화면으로 이동 시도 (5단계 전용)")
        
        # MenuClicks 인스턴스가 있으면 사용
        if menu_clicks_instance:
            success = menu_clicks_instance.click_group_management()
        else:
            # 직접 클릭 시도
            from menu_clicks import MenuClicks
            menu_clicks = MenuClicks(driver)
            success = menu_clicks.click_group_management()
        
        if success:
            time.sleep(3.0)
            logger.info("그룹상품관리 화면 이동 완료 (5단계 전용)")
            return True
        else:
            logger.error("그룹상품관리 화면 이동 실패 (5단계 전용)")
            return False
        
    except Exception as e:
        logger.error(f"그룹상품관리 화면 이동 중 오류 (5단계 전용): {e}")
        return False

def switch_to_non_group_view(driver: WebDriver, menu_clicks_instance=None) -> None:
    """
    비그룹상품보기로 전환
    
    Args:
        driver: Selenium WebDriver 인스턴스
        menu_clicks_instance: MenuClicks 인스턴스 (선택사항)
    """
    try:
        logger.info("비그룹상품보기 전환 시작")
        
        # MenuClicks 인스턴스가 있으면 사용
        if menu_clicks_instance:
            menu_clicks_instance.click_non_group_toggle()
        else:
            # 직접 클릭 시도
            from menu_clicks import MenuClicks
            menu_clicks = MenuClicks(driver)
            menu_clicks.click_non_group_toggle()
        
        from timesleep import DELAY_STANDARD
        time.sleep(DELAY_STANDARD)
        
        logger.info("비그룹상품보기 전환 완료")
        
    except Exception as e:
        logger.error(f"비그룹상품보기 전환 중 오류: {e}")
        raise