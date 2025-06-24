#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
통합 드롭다운 관리자
모든 단계에서 사용할 중앙관리 드롭다운 유틸리티
스크롤 방식 기반의 고성능 드롭다운 처리

작성자: AI Assistant
생성일: 2025-01-20
목적: 모든 단계의 드롭다운 처리를 스크롤 방식으로 통일
"""

import logging
from selenium import webdriver
from dropdown_utils_common import CommonDropdownUtils, get_common_dropdown_utils

# 로깅 설정
logger = logging.getLogger(__name__)

class UnifiedDropdownManager:
    """
    통합 드롭다운 관리자
    모든 단계에서 사용할 수 있는 통일된 드롭다운 인터페이스 제공
    """
    
    def __init__(self, driver: webdriver.Chrome):
        """
        통합 드롭다운 관리자 초기화
        
        Args:
            driver: Chrome WebDriver 인스턴스
        """
        self.driver = driver
        self.common_utils = get_common_dropdown_utils(driver)
        logger.info("통합 드롭다운 관리자 초기화 완료")
    
    def select_group_with_verification(self, group_name: str, timeout: int = 8) -> bool:
        """
        그룹 선택 및 검증 (스크롤 방식)
        
        Args:
            group_name: 선택할 그룹명
            timeout: 타임아웃 (초)
            
        Returns:
            bool: 선택 성공 여부
        """
        logger.info(f"통합 관리자를 통한 그룹 '{group_name}' 선택 시작")
        return self.common_utils.select_group_with_verification(group_name, timeout)
    
    def select_items_per_page_with_verification(self, items_count: int, timeout: int = 5) -> bool:
        """
        페이지당 아이템 수 선택 및 검증
        
        Args:
            items_count: 선택할 아이템 수
            timeout: 타임아웃 (초)
            
        Returns:
            bool: 선택 성공 여부
        """
        logger.info(f"통합 관리자를 통한 페이지당 {items_count}개 아이템 선택 시작")
        return self.common_utils.select_items_per_page_with_verification(items_count, timeout)
    
    def get_total_product_count(self) -> int:
        """
        전체 상품 수 조회
        
        Returns:
            int: 전체 상품 수 (실패시 -1)
        """
        return self.common_utils.get_total_product_count()
    
    def log_all_available_options(self) -> None:
        """
        현재 화면의 모든 옵션 로깅
        """
        self.common_utils.log_all_available_options()

# 싱글톤 인스턴스 관리
_unified_dropdown_manager = None

def get_unified_dropdown_manager(driver: webdriver.Chrome) -> UnifiedDropdownManager:
    """
    통합 드롭다운 관리자 싱글톤 인스턴스 반환
    
    Args:
        driver: Chrome WebDriver 인스턴스
        
    Returns:
        UnifiedDropdownManager: 통합 드롭다운 관리자 인스턴스
    """
    global _unified_dropdown_manager
    if _unified_dropdown_manager is None or _unified_dropdown_manager.driver != driver:
        _unified_dropdown_manager = UnifiedDropdownManager(driver)
        logger.info("새로운 통합 드롭다운 관리자 인스턴스 생성")
    return _unified_dropdown_manager

# 호환성을 위한 별칭들
def get_dropdown_manager(driver: webdriver.Chrome) -> UnifiedDropdownManager:
    """
    드롭다운 관리자 반환 (호환성 유지)
    
    Args:
        driver: Chrome WebDriver 인스턴스
        
    Returns:
        UnifiedDropdownManager: 통합 드롭다운 관리자 인스턴스
    """
    return get_unified_dropdown_manager(driver)

def get_dropdown_helper(driver: webdriver.Chrome) -> UnifiedDropdownManager:
    """
    드롭다운 헬퍼 반환 (호환성 유지)
    
    Args:
        driver: Chrome WebDriver 인스턴스
        
    Returns:
        UnifiedDropdownManager: 통합 드롭다운 관리자 인스턴스
    """
    return get_unified_dropdown_manager(driver)

def get_common_dropdown_utils_unified(driver: webdriver.Chrome) -> UnifiedDropdownManager:
    """
    공통 드롭다운 유틸리티 반환 (호환성 유지)
    
    Args:
        driver: Chrome WebDriver 인스턴스
        
    Returns:
        UnifiedDropdownManager: 통합 드롭다운 관리자 인스턴스
    """
    return get_unified_dropdown_manager(driver)

# 모듈 정보 출력
if __name__ == "__main__":
    print("통합 드롭다운 관리자 모듈")
    print("사용법:")
    print("from dropdown_manager_unified import get_unified_dropdown_manager")
    print("또는")
    print("from dropdown_manager_unified import get_dropdown_manager  # 호환성")
    print("")
    print("특징:")
    print("- 스크롤 방식 기반 고성능 처리")
    print("- 모든 단계 통일된 인터페이스")
    print("- 상품 수 변경 검증")
    print("- 50개 그룹 환경 최적화")