#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
브라우저 관리자 (GUI 수정 버전)

GUI에서 브라우저가 생성되지 않는 문제를 해결한 버전
"""

import os
import time
import logging
import tempfile
import threading
import queue
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

logger = logging.getLogger(__name__)

class BrowserManagerFixed:
    """GUI에서 안정적으로 작동하는 브라우저 관리자"""
    
    def __init__(self):
        """초기화"""
        self.drivers = {}  # 계정 ID를 키로 하는 드라이버 딕셔너리
        self.creation_lock = threading.Lock()  # 브라우저 생성 락
    
    def create_browser(self, account_id=None, headless=False, window_size=(1920, 1080)):
        """
        새 브라우저 인스턴스 생성 (GUI 최적화)
        
        Args:
            account_id (str, optional): 계정 ID
            headless (bool): 헤드리스 모드 사용 여부
            window_size (tuple): 창 크기
        
        Returns:
            webdriver: 생성된 웹드라이버 인스턴스
        """
        with self.creation_lock:
            try:
                # 계정 ID가 없으면 임시 ID 생성
                if not account_id:
                    account_id = f"temp_{int(time.time())}"
                
                # 이미 해당 계정의 드라이버가 있으면 반환
                if account_id in self.drivers and self.drivers[account_id]["driver"] is not None:
                    try:
                        # 드라이버가 살아있는지 확인
                        self.drivers[account_id]["driver"].current_url
                        logger.info(f"기존 브라우저 인스턴스 재사용: {account_id}")
                        return self.drivers[account_id]["driver"]
                    except:
                        # 드라이버가 죽었으면 제거
                        logger.warning(f"기존 드라이버가 비활성화됨, 새로 생성: {account_id}")
                        del self.drivers[account_id]
                
                logger.info(f"새 브라우저 인스턴스 생성 시작: {account_id}")
                
                # Chrome 옵션 설정 (GUI 최적화)
                chrome_options = Options()
                
                if headless:
                    chrome_options.add_argument("--headless")
                    chrome_options.add_argument("--disable-gpu")
                    chrome_options.add_argument("--no-sandbox")
                    chrome_options.add_argument("--disable-dev-shm-usage")
                else:
                    # GUI 모드 최적화 옵션
                    chrome_options.add_argument("--no-first-run")
                    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
                    chrome_options.add_experimental_option("detach", True)  # 프로세스 분리
                    chrome_options.add_argument("--disable-web-security")
                    chrome_options.add_argument("--allow-running-insecure-content")
                
                # 공통 옵션
                chrome_options.add_argument("--disable-notifications")
                chrome_options.add_argument("--disable-popup-blocking")
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chrome_options.add_experimental_option("useAutomationExtension", False)
                
                # 창 크기 설정
                if window_size:
                    chrome_options.add_argument(f"--window-size={window_size[0]},{window_size[1]}")
                
                # 기본 설정
                chrome_options.add_experimental_option("prefs", {
                    "credentials_enable_service": False,
                    "profile.password_manager_enabled": False,
                    "profile.default_content_setting_values.notifications": 2
                })
                
                # 브라우저 생성 (타임아웃 적용)
                driver = self._create_driver_with_timeout(chrome_options, timeout=30)
                
                if driver is None:
                    raise Exception("브라우저 드라이버 생성 실패")
                
                # 초기 설정
                if not headless:
                    try:
                        driver.maximize_window()
                        time.sleep(1)  # 창 최대화 대기
                    except Exception as e:
                        logger.warning(f"창 최대화 실패 (계속 진행): {e}")
                
                # 드라이버 정보 저장
                self.drivers[account_id] = {
                    "driver": driver,
                    "created_at": time.time(),
                    "account_id": account_id
                }
                
                logger.info(f"브라우저 인스턴스 생성 완료: {account_id}")
                return driver
                
            except Exception as e:
                logger.error(f"브라우저 인스턴스 생성 중 오류: {str(e)}")
                return None
    
    def _create_driver_with_timeout(self, chrome_options, timeout=30):
        """
        타임아웃을 적용하여 드라이버 생성
        
        Args:
            chrome_options: Chrome 옵션
            timeout: 타임아웃 (초)
        
        Returns:
            webdriver: 생성된 드라이버 또는 None
        """
        result_queue = queue.Queue()
        exception_queue = queue.Queue()
        
        def create_driver():
            try:
                logger.info("webdriver.Chrome() 호출 시작")
                driver = webdriver.Chrome(options=chrome_options)
                logger.info("webdriver.Chrome() 호출 완료")
                result_queue.put(driver)
            except Exception as e:
                logger.error(f"webdriver.Chrome() 호출 중 오류: {e}")
                exception_queue.put(e)
        
        # 별도 스레드에서 드라이버 생성
        thread = threading.Thread(target=create_driver)
        thread.daemon = True
        thread.start()
        
        # 타임아웃 대기
        thread.join(timeout=timeout)
        
        if thread.is_alive():
            logger.error(f"브라우저 생성 타임아웃 ({timeout}초)")
            return None
        
        # 예외 확인
        if not exception_queue.empty():
            exception = exception_queue.get()
            logger.error(f"브라우저 생성 중 예외: {exception}")
            return None
        
        # 결과 확인
        if not result_queue.empty():
            return result_queue.get()
        else:
            logger.error("브라우저 생성 실패: 알 수 없는 오류")
            return None
    
    def close_browser(self, account_id):
        """
        브라우저 인스턴스 종료
        
        Args:
            account_id (str): 계정 ID
        
        Returns:
            bool: 종료 성공 여부
        """
        try:
            if account_id not in self.drivers:
                logger.warning(f"계정 ID에 해당하는 브라우저 인스턴스가 없습니다: {account_id}")
                return False
            
            driver_info = self.drivers[account_id]
            driver = driver_info["driver"]
            
            if driver:
                driver.quit()
                logger.info(f"브라우저 인스턴스 종료: {account_id}")
            
            # 딕셔너리에서 제거
            del self.drivers[account_id]
            return True
            
        except Exception as e:
            logger.error(f"브라우저 인스턴스 종료 중 오류: {str(e)}")
            return False
    
    def close_all_browsers(self):
        """
        모든 브라우저 인스턴스 종료
        
        Returns:
            bool: 종료 성공 여부
        """
        try:
            account_ids = list(self.drivers.keys())
            
            for account_id in account_ids:
                self.close_browser(account_id)
            
            logger.info("모든 브라우저 인스턴스 종료 완료")
            return True
            
        except Exception as e:
            logger.error(f"모든 브라우저 인스턴스 종료 중 오류: {str(e)}")
            return False
    
    def get_browser(self, account_id):
        """
        브라우저 인스턴스 가져오기
        
        Args:
            account_id (str): 계정 ID
        
        Returns:
            webdriver: 브라우저 인스턴스 또는 None
        """
        if account_id in self.drivers:
            return self.drivers[account_id]["driver"]
        return None
    
    def get_all_browsers(self):
        """
        모든 브라우저 인스턴스 정보 가져오기
        
        Returns:
            dict: 브라우저 인스턴스 정보 딕셔너리
        """
        return self.drivers.copy()
    
    def is_browser_active(self, account_id):
        """
        브라우저가 활성 상태인지 확인
        
        Args:
            account_id (str): 계정 ID
        
        Returns:
            bool: 활성 상태 여부
        """
        try:
            if account_id not in self.drivers:
                return False
            
            driver = self.drivers[account_id]["driver"]
            if driver is None:
                return False
            
            # 드라이버가 살아있는지 확인
            driver.current_url
            return True
            
        except:
            return False

# 기존 BrowserManager와 호환성을 위한 별칭
BrowserManager = BrowserManagerFixed