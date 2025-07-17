# -*- coding: utf-8 -*-
"""
스마트 대기 시스템
시스템 상태와 조건에 따라 동적으로 대기 시간을 조정하는 유틸리티
"""

import time
import psutil
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

logger = logging.getLogger(__name__)

class SmartWaitSystem:
    """스마트 대기 시스템"""
    
    def __init__(self, driver):
        self.driver = driver
        self.performance_history = []
        self.system_load_factor = 1.0
        
    def adaptive_wait(self, condition_func, base_timeout=5, max_timeout=15, description="조건 대기"):
        """
        시스템 상태에 따라 동적으로 대기 시간을 조정하는 스마트 대기
        
        Args:
            condition_func: 대기할 조건 함수
            base_timeout: 기본 타임아웃 (초)
            max_timeout: 최대 타임아웃 (초)
            description: 대기 조건 설명
            
        Returns:
            bool: 조건 만족 여부
        """
        start_time = time.time()
        
        # 시스템 부하 확인
        system_load = self._get_system_load()
        adjusted_timeout = min(base_timeout * system_load, max_timeout)
        
        logger.info(f"🧠 스마트 대기 시작: {description} (조정된 타임아웃: {adjusted_timeout:.1f}초)")
        
        try:
            # 조건 확인 루프
            while time.time() - start_time < adjusted_timeout:
                if condition_func():
                    elapsed = time.time() - start_time
                    logger.info(f"✅ 조건 만족: {description} (소요시간: {elapsed:.2f}초)")
                    self._record_performance(description, elapsed, True)
                    return True
                
                # 동적 대기 간격 (시스템 부하에 따라 조정)
                wait_interval = 0.1 * system_load
                time.sleep(wait_interval)
            
            # 타임아웃 발생
            elapsed = time.time() - start_time
            logger.warning(f"⏰ 타임아웃: {description} (소요시간: {elapsed:.2f}초)")
            self._record_performance(description, elapsed, False)
            return False
            
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"❌ 대기 중 오류: {description} - {e} (소요시간: {elapsed:.2f}초)")
            self._record_performance(description, elapsed, False)
            return False
    
    def smart_element_wait(self, locator, timeout=10, description="요소 대기"):
        """
        요소 대기를 위한 스마트 대기
        
        Args:
            locator: (By, value) 튜플
            timeout: 타임아웃 (초)
            description: 대기 설명
            
        Returns:
            WebElement or None
        """
        def element_condition():
            try:
                element = self.driver.find_element(*locator)
                return element.is_displayed() and element.is_enabled()
            except:
                return False
        
        if self.adaptive_wait(element_condition, timeout, timeout * 1.5, f"요소 대기: {description}"):
            try:
                return self.driver.find_element(*locator)
            except:
                return None
        return None
    
    def smart_modal_wait(self, modal_selector=None, timeout=10):
        """
        모달창 대기를 위한 스마트 대기
        
        Args:
            modal_selector: 모달창 선택자 (없으면 JavaScript Alert 확인)
            timeout: 타임아웃 (초)
            
        Returns:
            str: 'alert', 'modal', 'none'
        """
        def check_modal_conditions():
            # JavaScript Alert 확인
            try:
                alert = self.driver.switch_to.alert
                if alert:
                    return 'alert'
            except:
                pass
            
            # HTML 모달 확인
            if modal_selector:
                try:
                    modal = self.driver.find_element(By.CSS_SELECTOR, modal_selector)
                    if modal.is_displayed():
                        return 'modal'
                except:
                    pass
            
            return None
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            result = check_modal_conditions()
            if result:
                logger.info(f"🎯 모달 감지: {result}")
                return result
            time.sleep(0.2)
        
        logger.info("📭 모달 없음")
        return 'none'
    
    def _get_system_load(self):
        """시스템 부하 확인 및 조정 팩터 계산"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory_percent = psutil.virtual_memory().percent
            
            # 부하 팩터 계산 (1.0 = 정상, 1.5 = 높은 부하)
            load_factor = 1.0
            
            if cpu_percent > 80:
                load_factor += 0.3
            elif cpu_percent > 60:
                load_factor += 0.2
            
            if memory_percent > 85:
                load_factor += 0.2
            elif memory_percent > 70:
                load_factor += 0.1
            
            self.system_load_factor = min(load_factor, 2.0)  # 최대 2배까지
            
            if load_factor > 1.2:
                logger.debug(f"🔥 높은 시스템 부하 감지 (CPU: {cpu_percent}%, RAM: {memory_percent}%, 팩터: {load_factor:.1f})")
            
            return self.system_load_factor
            
        except Exception as e:
            logger.debug(f"시스템 부하 확인 실패: {e}")
            return 1.0
    
    def _record_performance(self, operation, duration, success):
        """성능 기록"""
        record = {
            'timestamp': time.time(),
            'operation': operation,
            'duration': duration,
            'success': success,
            'system_load': self.system_load_factor
        }
        
        self.performance_history.append(record)
        
        # 최근 100개 기록만 유지
        if len(self.performance_history) > 100:
            self.performance_history = self.performance_history[-100:]
    
    def get_performance_summary(self):
        """성능 요약 정보 반환"""
        if not self.performance_history:
            return "성능 기록 없음"
        
        total_operations = len(self.performance_history)
        successful_operations = sum(1 for r in self.performance_history if r['success'])
        success_rate = (successful_operations / total_operations) * 100
        
        durations = [r['duration'] for r in self.performance_history]
        avg_duration = sum(durations) / len(durations)
        
        return f"성능 요약: 성공률 {success_rate:.1f}% ({successful_operations}/{total_operations}), 평균 소요시간 {avg_duration:.2f}초"