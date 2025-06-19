#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
브라우저 관리 모듈
기존 browser_core.py의 기능을 확장한 통합 브라우저 관리자
"""

import os
import sys
import logging
from typing import Dict, List, Optional, Union

# 루트 디렉토리를 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 기존 모듈들 임포트
from browser_core import BrowserCore
from login_percenty import PercentyLogin
from percenty_utils import hide_channel_talk_and_modals
from modal_blocker import close_modal_dialog, block_modals_on_page

logger = logging.getLogger(__name__)

class CoreBrowserManager:
    """
    통합 브라우저 관리자
    기존 BrowserCore의 기능을 확장하여 다중 브라우저 관리 지원
    """
    
    def __init__(self, headless: bool = False):
        """
        초기화
        
        Args:
            headless: 기본 헤드리스 모드 설정
        """
        self.browsers = {}  # 브라우저 인스턴스들
        self.active_browser = None
        self.browser_count = 0
        self.headless = headless  # 헤드리스 모드 설정
        
    def create_browser(self, browser_id: str = None, headless: bool = None) -> str:
        """
        새 브라우저 인스턴스 생성
        
        Args:
            browser_id: 브라우저 식별자 (None이면 자동 생성)
            headless: 헤드리스 모드 여부 (None이면 인스턴스 기본값 사용)
            
        Returns:
            str: 생성된 브라우저 ID
        """
        import traceback
        import time
        
        try:
            # headless 파라미터가 None이면 인스턴스 기본값 사용
            if headless is None:
                headless = self.headless
            
            logger.info(f"=== create_browser 시작: browser_id={browser_id}, headless={headless} (인스턴스 기본값: {self.headless}) ===")
            
            if browser_id is None:
                browser_id = f"browser_{self.browser_count + 1}"
                logger.info(f"브라우저 ID 자동 생성: {browser_id}")
            
            if browser_id in self.browsers:
                logger.warning(f"브라우저 ID '{browser_id}'가 이미 존재합니다.")
                return browser_id
            
            # 기존 BrowserCore 사용
            logger.info(f"BrowserCore 인스턴스 생성 시작")
            browser_core = BrowserCore()
            logger.info(f"BrowserCore 인스턴스 생성 완료")
            
            logger.info(f"브라우저 드라이버 생성 시작 (headless={headless})")
            logger.info(f"browser_core.create_browser 호출 전")
            start_time = time.time()
            
            try:
                driver = browser_core.create_browser(headless=headless)
                end_time = time.time()
                logger.info(f"browser_core.create_browser 호출 완료 (소요시간: {end_time - start_time:.2f}초)")
                logger.info(f"반환된 driver 타입: {type(driver)}")
            except Exception as create_error:
                end_time = time.time()
                logger.error(f"browser_core.create_browser 호출 실패 (소요시간: {end_time - start_time:.2f}초)")
                logger.error(f"create_browser 오류: {create_error}")
                raise
            
            if not driver:
                raise Exception("브라우저 드라이버 생성 실패: None 반환")
            
            logger.info(f"PercentyLogin 인스턴스 생성 시작")
            login_manager = PercentyLogin(driver)
            logger.info(f"PercentyLogin 인스턴스 생성 완료")
            
            self.browsers[browser_id] = {
                'core': browser_core,
                'driver': driver,
                'login_manager': login_manager,
                'active': True
            }
            
            self.browser_count += 1
            self.active_browser = browser_id
            
            logger.info(f"브라우저 '{browser_id}' 생성 완료")
            return browser_id
            
        except Exception as e:
            logger.error(f"=== create_browser 중 오류 발생 ===")
            logger.error(f"오류 메시지: {e}")
            logger.error(f"오류 상세: {traceback.format_exc()}")
            logger.error(f"=== create_browser 실패 ===")
            raise
    
    def get_browser(self, browser_id: str) -> Dict:
        """
        브라우저 인스턴스 반환
        
        Args:
            browser_id: 브라우저 식별자
            
        Returns:
            Dict: 브라우저 정보
        """
        if browser_id not in self.browsers:
            raise ValueError(f"브라우저 ID '{browser_id}'를 찾을 수 없습니다.")
        
        return self.browsers[browser_id]
    
    def get_driver(self, browser_id: str = None):
        """
        WebDriver 인스턴스 반환
        
        Args:
            browser_id: 브라우저 식별자 (None이면 활성 브라우저)
            
        Returns:
            WebDriver: Selenium WebDriver 인스턴스
        """
        if browser_id is None:
            browser_id = self.active_browser
        
        if browser_id is None:
            raise ValueError("활성 브라우저가 없습니다.")
        
        browser_info = self.get_browser(browser_id)
        return browser_info['driver']
    
    def login_browser(self, browser_id: str, email: str, password: str) -> bool:
        """브라우저에 로그인 수행 (DOM 선택자 사용)"""
        if browser_id not in self.browsers:
            logger.error(f"브라우저 '{browser_id}'를 찾을 수 없습니다")
            return False
        
        browser_info = self.browsers[browser_id]
        driver = browser_info.get('driver')
        
        if not driver:
            logger.error(f"브라우저 '{browser_id}'에 드라이버가 없습니다")
            return False
        
        try:
            from dom_selectors import LOGIN_SELECTORS
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            import time
            
            # 로그인 페이지로 이동
            logger.info(f"퍼센티 로그인 페이지 열기: https://www.percenty.co.kr/signin")
            driver.get("https://www.percenty.co.kr/signin")
            time.sleep(2)  # 페이지 로딩 대기
            
            # 아이디 입력
            logger.info("아이디 입력 중...")
            email_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, LOGIN_SELECTORS["USERNAME_FIELD"]))
            )
            email_field.clear()
            email_field.send_keys(email)
            time.sleep(0.5)
            
            # 비밀번호 입력
            logger.info("비밀번호 입력 중...")
            password_field = driver.find_element(By.XPATH, LOGIN_SELECTORS["PASSWORD_FIELD"])
            password_field.clear()
            password_field.send_keys(password)
            time.sleep(0.5)
            
            # 로그인 버튼 클릭
            logger.info("로그인 버튼 클릭 중...")
            login_button = driver.find_element(By.XPATH, LOGIN_SELECTORS["LOGIN_BUTTON"])
            login_button.click()
            
            # 로그인 성공 확인 (URL 변경 확인)
            logger.info("로그인 완료 확인 중...")
            WebDriverWait(driver, 30).until(
                lambda d: "/signin" not in d.current_url
            )
            logger.info(f"로그인 성공! 현재 URL: {driver.current_url}")
            time.sleep(2)  # 로그인 후 화면 로딩 대기
            
            return True
            
        except Exception as e:
            logger.error(f"브라우저 '{browser_id}' 로그인 중 오류: {e}")
            return False
    
    def close_browser(self, browser_id: str):
        """
        브라우저 종료
        
        Args:
            browser_id: 브라우저 식별자
        """
        try:
            if browser_id not in self.browsers:
                logger.warning(f"브라우저 ID '{browser_id}'를 찾을 수 없습니다.")
                return
            
            browser_info = self.browsers[browser_id]
            driver = browser_info['driver']
            
            if driver:
                driver.quit()
            
            del self.browsers[browser_id]
            
            if self.active_browser == browser_id:
                self.active_browser = None
                # 다른 활성 브라우저가 있으면 설정
                if self.browsers:
                    self.active_browser = list(self.browsers.keys())[0]
            
            logger.info(f"브라우저 '{browser_id}' 종료 완료")
            
        except Exception as e:
            logger.error(f"브라우저 '{browser_id}' 종료 중 오류: {e}")
    
    def close_all_browsers(self):
        """
        모든 브라우저 종료
        """
        try:
            browser_ids = list(self.browsers.keys())
            for browser_id in browser_ids:
                self.close_browser(browser_id)
            
            logger.info("모든 브라우저 종료 완료")
            
        except Exception as e:
            logger.error(f"모든 브라우저 종료 중 오류: {e}")
    
    def get_browser_list(self) -> List[str]:
        """
        브라우저 ID 목록 반환
        
        Returns:
            List[str]: 브라우저 ID 목록
        """
        return list(self.browsers.keys())
    
    def set_active_browser(self, browser_id: str):
        """
        활성 브라우저 설정
        
        Args:
            browser_id: 브라우저 식별자
        """
        if browser_id not in self.browsers:
            raise ValueError(f"브라우저 ID '{browser_id}'를 찾을 수 없습니다.")
        
        self.active_browser = browser_id
        logger.info(f"활성 브라우저를 '{browser_id}'로 설정")
    
    def cleanup(self):
        """
        정리 작업
        """
        try:
            self.close_all_browsers()
            logger.info("브라우저 관리자 정리 완료")
        except Exception as e:
            logger.error(f"브라우저 관리자 정리 중 오류: {e}")

# 하위 호환성을 위한 함수들
def create_browser_legacy(headless=False):
    """기존 코드와의 호환성을 위한 함수"""
    manager = CoreBrowserManager()
    browser_id = manager.create_browser(headless=headless)
    return manager.get_driver(browser_id)

if __name__ == "__main__":
    # 테스트 코드
    print("브라우저 관리자 모듈 테스트")
    logger.info("브라우저 관리자 모듈이 로드되었습니다.")