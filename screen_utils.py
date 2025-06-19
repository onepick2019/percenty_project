# -*- coding: utf-8 -*-
"""
화면 크기 관련 유틸리티 함수
"""

import logging
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

def check_screen_size(driver, required_width=1920, required_height=1032, tolerance=50):
    """
    현재 브라우저 창 크기를 확인하고 필요한 경우 전체 화면 모드로 전환
    
    Args:
        driver: Selenium WebDriver 인스턴스
        required_width: 필요한 화면 너비 (기본값: 1920)
        required_height: 필요한 화면 높이 (기본값: 1080)
        tolerance: 허용 오차 (기본값: 50픽셀)
        
    Returns:
        bool: 화면 크기가 요구사항에 맞으면 True, 아니면 False
    """
    # 현재 창 크기 확인
    window_size = driver.get_window_size()
    current_width = window_size['width']
    current_height = window_size['height']
    
    logging.info(f"현재 브라우저 창 크기: {current_width}x{current_height}")
    
    # 화면 크기가 요구사항에 맞는지 확인
    width_ok = abs(current_width - required_width) <= tolerance
    height_ok = abs(current_height - required_height) <= tolerance
    
    if width_ok and height_ok:
        logging.info("브라우저 창 크기가 요구사항에 맞습니다.")
        return True
    
    # 화면 크기가 맞지 않으면 전체 화면 모드로 전환 시도
    logging.warning(f"브라우저 창 크기가 요구사항({required_width}x{required_height})과 다릅니다.")
    logging.info("전체 화면 모드로 전환을 시도합니다.")
    
    # 창 최대화
    driver.maximize_window()
    
    # F11 키를 전송하여 전체 화면 모드로 전환
    actions = ActionChains(driver)
    actions.send_keys(Keys.F11).perform()
    
    # 전체 화면 모드 적용을 위한 대기
    time.sleep(1)
    
    # 다시 창 크기 확인
    window_size = driver.get_window_size()
    current_width = window_size['width']
    current_height = window_size['height']
    
    logging.info(f"전체 화면 모드 적용 후 창 크기: {current_width}x{current_height}")
    
    # 화면 크기가 요구사항에 맞는지 다시 확인
    width_ok = abs(current_width - required_width) <= tolerance
    height_ok = abs(current_height - required_height) <= tolerance
    
    if width_ok and height_ok:
        logging.info("브라우저 창 크기가 요구사항에 맞게 조정되었습니다.")
        return True
    else:
        logging.warning("전체 화면 모드로 전환 후에도 창 크기가 요구사항과 다릅니다.")
        logging.warning("절대좌표가 정확하게 작동하지 않을 수 있습니다.")
        return False

def toggle_fullscreen(driver):
    """
    전체 화면 모드 전환 (켜기/끄기)
    
    Args:
        driver: Selenium WebDriver 인스턴스
    """
    actions = ActionChains(driver)
    actions.send_keys(Keys.F11).perform()
    time.sleep(0.5)  # 전환 대기
    
    # 현재 창 크기 로깅
    window_size = driver.get_window_size()
    logging.info(f"전체 화면 모드 전환 후 창 크기: {window_size['width']}x{window_size['height']}")
