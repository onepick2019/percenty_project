# -*- coding: utf-8 -*-
"""
통합된 드롭다운 선택자 유틸리티

DOM 분석을 바탕으로 한 통합된 드롭다운 선택자 관리 클래스
성능 최적화와 유지보수성 향상을 위한 통합 접근 방식
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config import DELAY_VERY_SHORT, DELAY_SHORT
import logging

logger = logging.getLogger(__name__)

class UnifiedDropdownSelector:
    """
    통합된 드롭다운 선택자 관리 클래스
    
    DOM 분석을 바탕으로 한 최적화된 선택자 순서와 타임아웃 관리
    """
    
    def __init__(self, driver):
        self.driver = driver
        
        # 개별 상품 드롭다운 선택자 (성공률 높은 순서)
        self.product_item_selectors = [
            # 1. 테이블 행 기반 (가장 안정적)
            "//tr[contains(@class, 'ant-table-row')]//div[contains(@class, 'ant-select-outlined') and contains(@class, 'ant-select-show-search')]",
            
            # 2. 위치 기반 (단순하고 빠름)
            "//div[contains(@class, 'ant-select-outlined') and contains(@class, 'ant-select-show-search')]",
            
            # 3. 컨테이너 기반
            "//div[contains(@class, 'ant-select-single') and not(contains(@class, 'ant-select-borderless'))]",
            
            # 4. 텍스트 기반 백업 (마지막 수단)
            "//div[contains(@class, 'ant-select-single')][.//span[contains(text(), '그룹 없음')]]"
        ]
        
        # 검색 드롭다운 선택자 (성공률 높은 순서)
        self.search_dropdown_selectors = [
            # 1. 테이블 기반 (가장 안정적)
            "//div[contains(@class, 'ant-table')]//div[contains(@class, 'ant-select-borderless') and contains(@class, 'ant-select-show-arrow')]",
            
            # 2. 위치 기반
            "//div[contains(@class, 'ant-select-borderless') and contains(@class, 'ant-select-show-arrow')]",
            
            # 3. 컨테이너 기반
            "//div[contains(@class, 'ant-select-single') and contains(@class, 'ant-select-borderless')]"
        ]
    
    def find_dropdown_element(self, dropdown_type, item_index=0, timeout_per_selector=1):
        """
        드롭다운 요소 찾기
        
        Args:
            dropdown_type: 'product_item' 또는 'search'
            item_index: 요소 인덱스 (기본값: 0)
            timeout_per_selector: 선택자당 타임아웃 (기본값: 1초)
            
        Returns:
            WebElement 또는 None
        """
        if dropdown_type == 'product_item':
            selectors = self.product_item_selectors
        elif dropdown_type == 'search':
            selectors = self.search_dropdown_selectors
        else:
            logger.error(f"지원하지 않는 드롭다운 타입: {dropdown_type}")
            return None
        
        for i, base_selector in enumerate(selectors):
            try:
                # 인덱스가 필요한 경우 추가
                if item_index > 0 or "[" not in base_selector:
                    selector = f"({base_selector})[{item_index + 1}]"
                else:
                    selector = base_selector
                
                logger.debug(f"선택자 {i+1}/{len(selectors)} 시도: {selector[:50]}...")
                
                element = WebDriverWait(self.driver, timeout_per_selector).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                
                logger.debug(f"선택자 {i+1} 성공")
                return element
                
            except (TimeoutException, NoSuchElementException):
                logger.debug(f"선택자 {i+1} 실패")
                continue
        
        logger.error(f"{dropdown_type} 드롭다운을 찾을 수 없습니다 (인덱스: {item_index})")
        return None
    
    def open_dropdown(self, dropdown_type, item_index=0, timeout_per_selector=1):
        """
        드롭다운 열기
        
        Args:
            dropdown_type: 'product_item' 또는 'search'
            item_index: 요소 인덱스 (기본값: 0)
            timeout_per_selector: 선택자당 타임아웃 (기본값: 1초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            element = self.find_dropdown_element(dropdown_type, item_index, timeout_per_selector)
            
            if not element:
                return False
            
            # 요소를 화면에 보이게 스크롤
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
                element
            )
            time.sleep(DELAY_VERY_SHORT)
            
            # 클릭하여 드롭다운 열기
            element.click()
            time.sleep(DELAY_VERY_SHORT)
            
            logger.info(f"{dropdown_type} 드롭다운이 열렸습니다 (인덱스: {item_index})")
            return True
            
        except Exception as e:
            logger.error(f"{dropdown_type} 드롭다운 열기 오류: {e}")
            return False
    
    def get_performance_stats(self):
        """
        성능 통계 반환 (향후 모니터링용)
        
        Returns:
            dict: 성능 통계
        """
        return {
            "total_selectors": {
                "product_item": len(self.product_item_selectors),
                "search": len(self.search_dropdown_selectors)
            },
            "timeout_per_selector": "1초 (최적화됨)",
            "expected_max_delay": "4초 (product_item), 3초 (search)"
        }