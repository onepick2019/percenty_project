"""
퍼센티 자동화 공통 유틸리티 모듈

이 모듈은 여러 자동화 스크립트에서 공통으로 사용되는 유틸리티 함수들을 제공합니다.
주로 채널톡 상담창, 로그인 모달창 등 UI 요소를 처리하는 기능을 포함합니다.
"""

import logging
import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# 채널톡 관련 유틸리티 임포트
from channel_talk_utils import check_and_hide_channel_talk
# 로그인 모달창 관련 유틸리티 임포트
from login_modal_utils import hide_login_modal

# 로깅 설정
logger = logging.getLogger(__name__)

def hide_channel_talk_and_modals(driver, log_prefix=""):
    """
    채널톡 상담창과 로그인 모달창을 숨기는 통합 함수
    
    작업 중 주기적으로 호출하여 UI 요소가 자동화를 방해하지 않도록 합니다.
    
    Args:
        driver: Selenium WebDriver 인스턴스
        log_prefix: 로그 메시지 앞에 추가할 접두사 (선택사항)
    
    Returns:
        bool: 모든 숨기기 작업이 성공적으로 완료되었는지 여부
    """
    prefix = f"{log_prefix} " if log_prefix else ""
    
    # 채널톡 숨기기
    logger.info(f"{prefix}채널톡 숨기기 적용 시작")
    channel_result = check_and_hide_channel_talk(driver)
    logger.info(f"{prefix}채널톡 숨기기 결과: {channel_result}")
    
    # 로그인 모달창 숨기기
    logger.info(f"{prefix}로그인 모달창 숨기기 적용 시작")
    modal_result = hide_login_modal(driver)
    logger.info(f"{prefix}로그인 모달창 숨기기 결과: {modal_result}")
    
    return channel_result and modal_result

def periodic_ui_cleanup(driver, interval=60, max_attempts=None):
    """
    주기적으로 UI 요소를 정리하는 함수
    
    백그라운드에서 일정 간격으로 채널톡과 모달창을 숨깁니다.
    
    Args:
        driver: Selenium WebDriver 인스턴스
        interval: 정리 작업 간의 대기 시간(초)
        max_attempts: 최대 시도 횟수 (None이면 무제한)
    
    사용 예:
        # 메인 스레드에서 1분마다 UI 정리 작업 수행
        periodic_ui_cleanup(driver, interval=60)
        # cleanup 시 한 번만 실행
        periodic_ui_cleanup(driver, max_attempts=1)
    """
    attempt = 0
    while max_attempts is None or attempt < max_attempts:
        attempt += 1
        logger.info(f"주기적 UI 정리 작업 실행 (시도 {attempt})")
        
        try:
            hide_channel_talk_and_modals(driver, log_prefix="주기적")
        except Exception as e:
            logger.error(f"주기적 UI 정리 중 오류 발생: {e}")
        
        # max_attempts가 1이면 대기하지 않고 즉시 종료
        if max_attempts == 1:
            break
            
        # 다음 정리 작업까지 대기
        time.sleep(interval)

def ensure_clean_ui_before_action(driver, action_name="작업"):
    """
    중요 작업 수행 전에 UI를 정리하는 함수
    
    중요한 클릭이나 입력 작업 전에 호출하여 UI 요소가 방해하지 않도록 합니다.
    
    Args:
        driver: Selenium WebDriver 인스턴스
        action_name: 수행할 작업의 이름 (로깅용)
    
    Returns:
        bool: UI 정리 성공 여부
    
    사용 예:
        # 중요 버튼 클릭 전에 UI 정리
        ensure_clean_ui_before_action(driver, "상품 수정 버튼 클릭")
        button.click()
    """
    logger.info(f"{action_name} 전 UI 정리 시작")
    result = hide_channel_talk_and_modals(driver, log_prefix=f"{action_name} 전")
    logger.info(f"{action_name} 전 UI 정리 완료: {'성공' if result else '일부 실패'}")
    return result
