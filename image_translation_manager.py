# -*- coding: utf-8 -*-
import logging
import time
import random
from image_translation_handler_new import ImageTranslationHandler as NewImageTranslationHandler
from image_translation_handler_specific import ImageTranslationHandler as SpecificImageTranslationHandler

logger = logging.getLogger(__name__)

class HumanLikeDelay:
    """
    인간과 유사한 지연 시간을 제공하는 클래스
    """
    
    @staticmethod
    def short_delay():
        """짧은 지연 (0.5-1.5초)"""
        delay = random.uniform(0.5, 1.5)
        logger.debug(f"짧은 지연: {delay:.2f}초")
        time.sleep(delay)
    
    @staticmethod
    def medium_delay():
        """중간 지연 (1.0-3.0초)"""
        delay = random.uniform(1.0, 3.0)
        logger.debug(f"중간 지연: {delay:.2f}초")
        time.sleep(delay)
    
    @staticmethod
    def long_delay():
        """긴 지연 (2.0-5.0초)"""
        delay = random.uniform(2.0, 5.0)
        logger.debug(f"긴 지연: {delay:.2f}초")
        time.sleep(delay)
    
    @staticmethod
    def custom_delay(min_seconds, max_seconds):
        """사용자 정의 지연"""
        delay = random.uniform(min_seconds, max_seconds)
        logger.debug(f"사용자 정의 지연: {delay:.2f}초")
        time.sleep(delay)

class ImageTranslationManager:
    """
    하이브리드 이미지 번역 매니저
    액션 타입에 따라 최적의 핸들러를 선택하여 사용
    """
    
    def __init__(self, driver):
        self.driver = driver
        self.new_handler = NewImageTranslationHandler(driver)
        self.specific_handler = SpecificImageTranslationHandler(driver)
        self.human_delay = HumanLikeDelay()
    
    def image_translate(self, action_value, context='detail'):
        """
        이미지 번역 처리 메인 메서드
        액션 타입에 따라 최적의 핸들러를 선택
        
        Args:
            action_value (str): 액션 값 (예: "1,2,3", "specific:all", "auto_detect_chinese")
            context (str): 처리 컨텍스트 ('detail', 'thumbnail', 'option')
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"하이브리드 이미지 번역 시작: {action_value}")
            
            # 인간과 유사한 지연 추가
            self.human_delay.short_delay()
            
            # 핸들러 선택
            handler = self._select_handler(action_value)
            
            if handler is None:
                logger.error(f"지원되지 않는 액션 값: {action_value}")
                return False
            
            # 선택된 핸들러로 번역 실행
            logger.info(f"선택된 핸들러: {handler.__class__.__name__}")
            
            # 번역 전 중간 지연
            self.human_delay.medium_delay()
            
            success = handler.image_translate(action_value, context)
            
            if success:
                logger.info("하이브리드 이미지 번역 완료")
                # 성공 후 짧은 지연
                self.human_delay.short_delay()
            else:
                logger.error("하이브리드 이미지 번역 실패")
            
            return success
            
        except Exception as e:
            logger.error(f"하이브리드 이미지 번역 오류: {e}")
            return False
    
    def _select_handler(self, action_value):
        """
        액션 값에 따라 최적의 핸들러를 선택
        
        Args:
            action_value (str): 액션 값
            
        Returns:
            ImageTranslationHandler: 선택된 핸들러 또는 None
        """
        try:
            action_value = action_value.strip().lower()
            
            # 모든 케이스에서 통합 방식을 사용하는 NewImageTranslationHandler 사용
            # specific:all의 경우
            if action_value == "specific:all":
                logger.info("specific:all 감지 - NewImageTranslationHandler 사용 (통합 순차 처리)")
                return self.new_handler
            
            # auto_detect_chinese의 경우도 통합 방식 사용
            if action_value == "auto_detect_chinese":
                logger.info("auto_detect_chinese 감지 - NewImageTranslationHandler 사용 (통합 처리)")
                return self.new_handler
            
            # first:N, last:N 패턴의 경우도 통합 방식 사용
            if action_value.startswith(("first:", "last:")):
                logger.info(f"{action_value} 감지 - NewImageTranslationHandler 사용 (통합 처리)")
                return self.new_handler
            
            # specific:N,N,N 패턴의 경우도 통합 방식 사용
            if action_value.startswith("specific:") and "," in action_value:
                logger.info(f"{action_value} 감지 - NewImageTranslationHandler 사용 (통합 처리)")
                return self.new_handler
            
            # 숫자 리스트 (1,2,3 등)의 경우도 통합 방식 사용
            if self._is_position_list(action_value):
                logger.info(f"{action_value} 감지 - NewImageTranslationHandler 사용 (통합 처리)")
                return self.new_handler
            
            # 기본값: 통합 방식을 사용하는 NewImageTranslationHandler 사용
            logger.warning(f"알 수 없는 액션 패턴: {action_value} - NewImageTranslationHandler 기본 사용 (통합 처리)")
            return self.new_handler
            
        except Exception as e:
            logger.error(f"핸들러 선택 오류: {e}")
            return None
    
    def _is_position_list(self, action_value):
        """
        액션 값이 위치 리스트인지 확인 (예: "1,2,3")
        
        Args:
            action_value (str): 액션 값
            
        Returns:
            bool: 위치 리스트 여부
        """
        try:
            # 쉼표로 분리하여 모든 요소가 숫자인지 확인
            parts = [part.strip() for part in action_value.split(",")]
            return all(part.isdigit() for part in parts if part)
        except:
            return False
    
    def get_handler_info(self, action_value):
        """
        주어진 액션 값에 대해 선택될 핸들러 정보를 반환 (디버깅용)
        
        Args:
            action_value (str): 액션 값
            
        Returns:
            dict: 핸들러 정보
        """
        handler = self._select_handler(action_value)
        
        if handler is None:
            return {
                "handler": None,
                "handler_name": "None",
                "reason": "지원되지 않는 액션 값"
            }
        
        handler_name = handler.__class__.__name__
        
        if handler == self.new_handler:
            reason = "순차 처리 최적화 (specific:all)"
        else:
            reason = "개별/특정 위치 처리 최적화"
        
        return {
            "handler": handler,
            "handler_name": handler_name,
            "reason": reason
        }