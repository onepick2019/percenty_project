# -*- coding: utf-8 -*-
"""
퍼센티 자동화 기본 단계 관리자

모든 단계 관리자의 기본 클래스를 정의합니다.
"""

import os
import time
import random
import logging
import traceback
from abc import ABC, abstractmethod
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException, StaleElementReferenceException

# 경로 설정
import sys
import os

# 프로젝트 루트 경로를 sys.path에 추가
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if root_path not in sys.path:
    sys.path.append(root_path)

# 코어 모듈 임포트
from browser_core import BrowserCore
from modal_core import ModalCore

# 신규 좌표 관리 시스템 가져오기
from coordinates.coordinates_all import *
# 메뉴 클릭 기능 추가
from menu_clicks import click_menu_using_relative_coordinates, click_at_absolute_coordinates
# 모달창 닫기 기능 추가
from close_modal_by_selector import close_modal_with_selectors
# 시간 지연 관리 모듈 추가
from timesleep import *
# DOM 선택자 가져오기
from dom_selectors import LOGIN_SELECTORS, MODAL_SELECTORS
# 모달창 자동 차단 모듈 추가
from modal_blocker import block_modals_on_page, press_escape_key, close_modal_dialog, set_modal_cookies_and_storage
from dom_utils import smart_click, highlight_element
# 채널톡 및 로그인 모달창 유틸리티 임포트
from channel_talk_utils import check_and_hide_channel_talk
from login_modal_utils import hide_login_modal
# 통합 유틸리티 모듈 임포트
from percenty_utils import hide_channel_talk_and_modals

logger = logging.getLogger(__name__)

class BaseStepManager:
    """모든 단계 관리자의 기본 클래스"""
    
    def __init__(self, driver, step_name, step_number):
        """
        초기화
        
        Args:
            driver: Selenium WebDriver 인스턴스
            step_name (str): 단계 이름
            step_number (int): 단계 번호
        """
        self.driver = driver
        self.step_name = step_name
        self.step_number = step_number
        self.email = None
        self.password = None
        self.batch_info = None
        self.is_running = False
        
        # 코어 모듈 초기화
        self.modal_core = ModalCore(driver)
    
    def set_account_info(self, account_info):
        """
        계정 정보 설정
        
        Args:
            account_info (dict): 계정 정보
        """
        self.email = account_info.get("id") or account_info.get("email")
        self.password = account_info.get("password")
        logger.info(f"{self.step_name} - 계정 정보 설정: {self.email}")
    
    def set_batch_info(self, batch_info):
        """
        배치 작업 정보 설정
        
        Args:
            batch_info (dict): 배치 정보
        """
        self.batch_info = batch_info
        logger.info(f"{self.step_name} - 배치 정보 설정: 수량 {batch_info['quantity']}개")
    
    def login_percenty(self):
        """
        퍼센티 로그인 수행 (모든 단계에서 공통으로 사용)
        
        Returns:
            bool: 로그인 성공 여부
        """
        try:
            if not self.email or not self.password:
                logger.error(f"{self.step_name} - 로그인 정보가 설정되지 않았습니다.")
                return False
            
            # 재시도 횟수 관리
            attempt = 1
            max_attempts = 3
            
            # 브라우저 전체화면으로 전환 (좌표 일관성 확보)
            logger.info(f"{self.step_name} - 브라우저 전체화면으로 전환 시도")
            try:
                actions = ActionChains(self.driver)
                actions.send_keys(Keys.F11).perform()
                time.sleep(2)  # 전체화면 전환 대기
                
                # 전체화면 후 창 크기 확인
                fullscreen_window_size = self.driver.get_window_size()
                logger.info(f"{self.step_name} - 전체화면 창 크기: {fullscreen_window_size}")
            except Exception as e:
                logger.warning(f"{self.step_name} - 전체화면 전환 실패 (무시함): {str(e)}")
                
            # 퍼센티 로그인 페이지 접속
            logger.info(f"{self.step_name} - 로그인 페이지 접속 시도")
            try:
                login_url = "https://www.percenty.co.kr/signin"
                self.driver.get(login_url)
                
                # 페이지 로드 대기
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                logger.info(f"{self.step_name} - 로그인 페이지 로드 완료")
                time.sleep(DELAY_SHORT)
                
                # 알림창 닫기 시도
                try:
                    self.modal_core.close_all_modals_and_popups()
                    logger.info(f"{self.step_name} - 알림창 닫기 시도 완료")
                except Exception as modal_err:
                    logger.warning(f"{self.step_name} - 알림창 닫기 중 오류 (무시함): {str(modal_err)}")
            except Exception as nav_err:
                logger.error(f"{self.step_name} - 로그인 페이지 접속 실패: {str(nav_err)}")
                return False
                
            # 로그인 실행
            while attempt <= max_attempts:
                logger.info(f"{self.step_name} - 로그인 시도 ({attempt}/{max_attempts})")
                
                try:
                    # 아이디 입력
                    logger.info(f"{self.step_name} - 아이디 입력 시도")
                    email_input = None
                    
                    # DOM 선택자로 시도
                    try:
                        email_selector = LOGIN_SELECTORS['email_input']
                        email_input = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, email_selector))
                        )
                        logger.info(f"{self.step_name} - DOM 선택자로 아이디 입력창 찾기 성공")
                    except Exception as dom_err:
                        logger.warning(f"{self.step_name} - DOM 선택자로 아이디 입력창 찾기 실패: {str(dom_err)}")
                        
                        # 좌표 기반 클릭 시도
                        try:
                            from coordinates.coordinates_all import LOGIN
                            if 'USERNAME_FIELD' in LOGIN:
                                logger.info(f"{self.step_name} - 좌표 기반 아이디 입력창 클릭 시도")
                                coords = LOGIN['USERNAME_FIELD']
                                click_at_absolute_coordinates(self.driver, coords[0], coords[1])
                                logger.info(f"{self.step_name} - 좌표 클릭 ({coords[0]}, {coords[1]}) 완료")
                                time.sleep(DELAY_SHORT)
                        except Exception as coord_err:
                            logger.warning(f"{self.step_name} - 좌표 기반 아이디 입력창 클릭 실패: {str(coord_err)}")
                    
                    # 입력 수행
                    actions = ActionChains(self.driver)
                    actions.send_keys(self.email)
                    actions.perform()
                    logger.info(f"{self.step_name} - 아이디 입력 완료: {self.email}")
                    time.sleep(DELAY_SHORT)
                    
                    # 비밀번호 입력
                    logger.info(f"{self.step_name} - 비밀번호 입력 시도")
                    password_input = None
                    
                    # DOM 선택자로 시도
                    try:
                        password_selector = LOGIN_SELECTORS['password_input']
                        password_input = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, password_selector))
                        )
                        password_input.click()
                        logger.info(f"{self.step_name} - DOM 선택자로 비밀번호 입력창 찾기 성공")
                    except Exception as dom_err:
                        logger.warning(f"{self.step_name} - DOM 선택자로 비밀번호 입력창 찾기 실패: {str(dom_err)}")
                        
                        # 좌표 기반 클릭 시도
                        try:
                            from coordinates.coordinates_all import LOGIN
                            if 'PASSWORD_FIELD' in LOGIN:
                                logger.info(f"{self.step_name} - 좌표 기반 비밀번호 입력창 클릭 시도")
                                coords = LOGIN['PASSWORD_FIELD']
                                click_at_absolute_coordinates(self.driver, coords[0], coords[1])
                                logger.info(f"{self.step_name} - 좌표 클릭 ({coords[0]}, {coords[1]}) 완료")
                                time.sleep(DELAY_SHORT)
                        except Exception as coord_err:
                            logger.warning(f"{self.step_name} - 좌표 기반 비밀번호 입력창 클릭 실패: {str(coord_err)}")
                    
                    # 입력 수행
                    actions = ActionChains(self.driver)
                    actions.send_keys(self.password)
                    actions.perform()
                    logger.info(f"{self.step_name} - 비밀번호 입력 완료")
                    time.sleep(DELAY_SHORT)
                    
                    # 로그인 버튼 클릭
                    logger.info(f"{self.step_name} - 로그인 버튼 클릭 시도")
                    login_button = None
                    
                    # DOM 선택자로 시도
                    try:
                        login_selector = LOGIN_SELECTORS['login_button']
                        login_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, login_selector))
                        )
                        login_button.click()
                        logger.info(f"{self.step_name} - DOM 선택자로 로그인 버튼 클릭 성공")
                    except Exception as dom_err:
                        logger.warning(f"{self.step_name} - DOM 선택자로 로그인 버튼 클릭 실패: {str(dom_err)}")
                        
                        # 좌표 기반 클릭 시도
                        try:
                            from coordinates.coordinates_all import LOGIN
                            if 'LOGIN_BUTTON' in LOGIN:
                                logger.info(f"{self.step_name} - 좌표 기반 로그인 버튼 클릭 시도")
                                coords = LOGIN['LOGIN_BUTTON']
                                click_at_absolute_coordinates(self.driver, coords[0], coords[1])
                                logger.info(f"{self.step_name} - 좌표 클릭 ({coords[0]}, {coords[1]}) 완료")
                                time.sleep(DELAY_SHORT)
                        except Exception as coord_err:
                            logger.warning(f"{self.step_name} - 좌표 기반 로그인 버튼 클릭 실패: {str(coord_err)}")
                    
                    # 로그인 성공 여부 확인을 위해 대기
                    logger.info(f"{self.step_name} - 로그인 버튼 클릭 후 대기 중...")
                    time.sleep(3)  # 대기 시간을 3초로 줄임
                    
                    # 비밀번호 저장 모달창 닫기
                    logger.info(f"{self.step_name} - 비밀번호 저장 모달창 닫기 시도")
                    try:
                        self.modal_core.close_password_save_modal()
                        logger.info(f"{self.step_name} - 비밀번호 저장 모달창 닫기 성공")
                    except Exception as modal_err:
                        logger.warning(f"{self.step_name} - 비밀번호 저장 모달창 닫기 중 오류 (무시함): {str(modal_err)}")
                    
                    # 로그인 후 추가 모달창 닫기
                    logger.info(f"{self.step_name} - 로그인 후 모달창 닫기 시도")
                    try:
                        self.modal_core.close_login_modal()
                        logger.info(f"{self.step_name} - 로그인 후 모달창 닫기 성공")
                    except Exception as modal_err:
                        logger.warning(f"{self.step_name} - 로그인 후 모달창 닫기 중 오류 (무시함): {str(modal_err)}")
                    
                    # 채널톡 및 기타 모달창 숨기기
                    logger.info(f"{self.step_name} - 채널톡 및 기타 모달창 숨기기 시도")
                    try:
                        hide_channel_talk_and_modals(self.driver, log_prefix=self.step_name)
                        logger.info(f"{self.step_name} - 채널톡 및 기타 모달창 숨기기 성공")
                    except Exception as modal_err:
                        logger.warning(f"{self.step_name} - 채널톡 및 기타 모달창 숨기기 중 오류 (무시함): {str(modal_err)}")
                    
                    # 로그인 성공
                    break
                except Exception as e:
                    logger.error(f"{self.step_name} - 로그인 시도 중 오류: {str(e)}")
                    attempt += 1
                    if attempt <= max_attempts:
                        logger.info(f"{self.step_name} - 로그인 재시도 ({attempt}/{max_attempts})")
                        time.sleep(DELAY_MEDIUM)  # 재시도 전 대기
                    else:
                        logger.error(f"{self.step_name} - 최대 로그인 시도 횟수 초과. 로그인 실패.")
                        return False
            
            # 로그인 완료 대기 (URL이 변경될 때까지)
            try:
                logger.info(f"{self.step_name} - 로그인 완료 확인 중...")
                logger.info(f"{self.step_name} - 현재 URL: {self.driver.current_url}")
                
                # 타임아웃을 15초로 더 줄임
                wait = WebDriverWait(self.driver, timeout=15)
                
                def check_login_success(driver):
                    current_url = driver.current_url
                    logger.info(f"{self.step_name} - URL 체크: {current_url}")
                    return "/signin" not in current_url
                
                try:
                    wait.until(check_login_success)
                    logger.info(f"{self.step_name} - 로그인 완료! 현재 URL: {self.driver.current_url}")
                except TimeoutException:
                    logger.error(f"{self.step_name} - 로그인 완료 확인 타임아웃. 현재 URL: {self.driver.current_url}")
                    return False
                
                # 페이지 로드 대기를 2초로 더 줄임
                time.sleep(2)  # 로그인 후 페이지 로드를 위해 2초 대기
                
                # AI소싱 메뉴 클릭
                logger.info(f"{self.step_name} - AI소싱 메뉴 클릭 시도")
                try:
                    # 좌표 기반 AI소싱 메뉴 클릭
                    try:
                        from coordinates.coordinates_all import MENU
                        if 'AI_SOURCING' in MENU:
                            logger.info(f"{self.step_name} - 좌표 기반 AI소싱 메뉴 클릭 시도")
                            coords = MENU['AI_SOURCING']
                            click_at_absolute_coordinates(self.driver, coords['x'], coords['y'])
                            logger.info(f"{self.step_name} - 좌표 클릭 ({coords['x']}, {coords['y']}) 완료")
                            time.sleep(DELAY_MEDIUM)
                            # AI소싱 페이지 로드 확인
                            if "ai" in self.driver.current_url:
                                logger.info(f"{self.step_name} - AI소싱 화면 이동 성공: {self.driver.current_url}")
                            else:
                                logger.warning(f"{self.step_name} - AI소싱 화면 이동 확인 실패: {self.driver.current_url}")
                    except Exception as menu_err:
                        logger.warning(f"{self.step_name} - AI소싱 메뉴 클릭 시도 오류: {str(menu_err)}")
                        # URL 직접 이동
                        self.driver.get("https://www.percenty.co.kr/ai")
                        logger.info(f"{self.step_name} - AI소싱 URL 이동 시도 완료")
                except Exception as ai_err:
                    logger.warning(f"{self.step_name} - AI소싱 메뉴 접근 중 오류 (무시함): {str(ai_err)}")
                
                return True
            except Exception as login_err:
                logger.error(f"{self.step_name} - 로그인 성공 확인 중 오류 발생: {str(login_err)}")
                logger.error(f"{self.step_name} - 현재 URL: {self.driver.current_url}")
                return False
                
        except Exception as e:
            logger.error(f"{self.step_name} - 로그인 중 오류 발생: {str(e)}")
            logger.error(f"{self.step_name} - 오류 세부 정보: {traceback.format_exc()}")
            return False
    
    def refresh_page(self):
        """
        현재 페이지 새로고침
        
        Returns:
            bool: 성공 여부
        """
        try:
            self.driver.refresh()
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            logger.info(f"{self.step_name} - 페이지 새로고침 완료")
            return True
        except Exception as e:
            logger.error(f"{self.step_name} - 페이지 새로고침 실패: {str(e)}")
            return False
    
    def run_automation(self):
        """
        자동화 실행 (상속 클래스에서 구현)
        
        Returns:
            bool: 성공 여부
        """
        raise NotImplementedError("이 메서드는 상속 클래스에서 구현해야 합니다.")
    
    def stop_automation(self):
        """
        자동화 중지
        
        Returns:
            bool: 성공 여부
        """
        self.is_running = False
        logger.info(f"{self.step_name} - 자동화 중지 요청됨")
        return True
