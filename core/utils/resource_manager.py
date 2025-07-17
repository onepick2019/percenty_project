# -*- coding: utf-8 -*-
"""
리소스 관리 유틸리티
메모리, CPU, 브라우저 리소스를 효율적으로 관리합니다.
"""

import gc
import psutil
import logging
import threading
import time
from typing import Optional, Callable
from contextlib import contextmanager
from selenium.webdriver.remote.webdriver import WebDriver

logger = logging.getLogger(__name__)

class ResourceMonitor:
    """시스템 리소스 모니터링 클래스"""
    
    def __init__(self, warning_memory_percent: int = 80, warning_cpu_percent: int = 90):
        """
        리소스 모니터 초기화
        
        Args:
            warning_memory_percent: 메모리 사용률 경고 임계값 (%)
            warning_cpu_percent: CPU 사용률 경고 임계값 (%)
        """
        self.warning_memory_percent = warning_memory_percent
        self.warning_cpu_percent = warning_cpu_percent
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
    
    def get_memory_usage(self) -> dict:
        """현재 메모리 사용량 반환"""
        memory = psutil.virtual_memory()
        return {
            'total': memory.total,
            'available': memory.available,
            'percent': memory.percent,
            'used': memory.used,
            'free': memory.free
        }
    
    def get_cpu_usage(self) -> float:
        """현재 CPU 사용률 반환"""
        return psutil.cpu_percent(interval=1)
    
    def check_resource_health(self) -> dict:
        """리소스 상태 확인"""
        memory_info = self.get_memory_usage()
        cpu_percent = self.get_cpu_usage()
        
        warnings = []
        
        if memory_info['percent'] > self.warning_memory_percent:
            warnings.append(f"메모리 사용률 높음: {memory_info['percent']:.1f}%")
        
        if cpu_percent > self.warning_cpu_percent:
            warnings.append(f"CPU 사용률 높음: {cpu_percent:.1f}%")
        
        return {
            'memory': memory_info,
            'cpu_percent': cpu_percent,
            'warnings': warnings,
            'healthy': len(warnings) == 0
        }
    
    def start_monitoring(self, interval: int = 30, callback: Optional[Callable] = None):
        """리소스 모니터링 시작"""
        if self._monitoring:
            logger.warning("리소스 모니터링이 이미 실행 중입니다")
            return
        
        self._monitoring = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval, callback),
            daemon=True
        )
        self._monitor_thread.start()
        logger.info(f"리소스 모니터링 시작 (간격: {interval}초)")
    
    def stop_monitoring(self):
        """리소스 모니터링 중지"""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        logger.info("리소스 모니터링 중지")
    
    def _monitor_loop(self, interval: int, callback: Optional[Callable]):
        """모니터링 루프"""
        while self._monitoring:
            try:
                health_info = self.check_resource_health()
                
                if not health_info['healthy']:
                    for warning in health_info['warnings']:
                        logger.warning(f"🚨 리소스 경고: {warning}")
                
                if callback:
                    callback(health_info)
                
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"리소스 모니터링 중 오류: {e}")
                time.sleep(interval)

class BrowserResourceManager:
    """브라우저 리소스 관리 클래스"""
    
    def __init__(self, driver: WebDriver):
        """
        브라우저 리소스 관리자 초기화
        
        Args:
            driver: Selenium WebDriver 인스턴스
        """
        self.driver = driver
    
    def clear_browser_cache(self):
        """브라우저 캐시 정리"""
        try:
            # 브라우저 캐시 정리
            self.driver.execute_script("window.localStorage.clear();")
            self.driver.execute_script("window.sessionStorage.clear();")
            logger.info("브라우저 캐시 정리 완료")
        except Exception as e:
            logger.warning(f"브라우저 캐시 정리 실패: {e}")
    
    def close_unused_tabs(self, keep_current: bool = True):
        """사용하지 않는 탭 정리"""
        try:
            current_handle = self.driver.current_window_handle
            all_handles = self.driver.window_handles
            
            closed_count = 0
            for handle in all_handles:
                if keep_current and handle == current_handle:
                    continue
                
                self.driver.switch_to.window(handle)
                self.driver.close()
                closed_count += 1
            
            # 현재 탭으로 돌아가기
            if keep_current and current_handle in self.driver.window_handles:
                self.driver.switch_to.window(current_handle)
            
            logger.info(f"사용하지 않는 탭 {closed_count}개 정리 완료")
            
        except Exception as e:
            logger.warning(f"탭 정리 실패: {e}")
    
    def optimize_browser_memory(self):
        """브라우저 메모리 최적화"""
        try:
            # JavaScript 가비지 컬렉션 실행
            self.driver.execute_script("if (window.gc) { window.gc(); }")
            
            # 브라우저 캐시 정리
            self.clear_browser_cache()
            
            # 사용하지 않는 탭 정리
            self.close_unused_tabs()
            
            logger.info("브라우저 메모리 최적화 완료")
            
        except Exception as e:
            logger.warning(f"브라우저 메모리 최적화 실패: {e}")

@contextmanager
def resource_cleanup():
    """리소스 정리를 위한 컨텍스트 매니저"""
    try:
        yield
    finally:
        # 가비지 컬렉션 실행
        gc.collect()
        logger.debug("리소스 정리 완료")

def force_garbage_collection():
    """강제 가비지 컬렉션 실행"""
    before = len(gc.get_objects())
    gc.collect()
    after = len(gc.get_objects())
    freed = before - after
    
    if freed > 0:
        logger.info(f"가비지 컬렉션으로 {freed}개 객체 정리")
    
    return freed

# 전역 리소스 모니터 인스턴스
resource_monitor = ResourceMonitor()