# human_delay.py
import random
import time
import logging

logger = logging.getLogger("HumanDelay")

class HumanLikeDelay:
    """인간과 유사한 지연 패턴을 생성하는 클래스"""
    
    def __init__(self, min_total_delay=45, max_total_delay=60, current_speed=46, expected_actions=None):
        """
        인간과 유사한 지연을 생성하는 클래스 초기화
        
        Args:
            min_total_delay (int): 목표 최소 총 지연 시간 (초)
            max_total_delay (int): 목표 최대 총 지연 시간 (초)
            current_speed (int): 현재 자동화된 실행 시간 (초)
            expected_actions (int): 예상 액션 수 (None이면 자동 추정)
        """
        self.min_total_delay = min_total_delay
        self.max_total_delay = max_total_delay
        self.current_speed = current_speed
        self.expected_actions = expected_actions
        
        # 목표 추가 지연 시간 계산
        self.target_additional_delay = random.uniform(
            min_total_delay - current_speed, 
            max_total_delay - current_speed
        )
        self.remaining_delay = self.target_additional_delay
        
        # 예상 액션 수 설정
        self.action_count = self._estimate_action_count()
        
        logger.info(f"총 목표 지연: {self.target_additional_delay:.2f}초 (현재 속도: {current_speed}초, 목표: {min_total_delay}-{max_total_delay}초)")
    
    def _estimate_action_count(self):
        """작업에서 예상되는 액션 수 추정"""
        if self.expected_actions is not None:
            return self.expected_actions
        # 일반적인 1단계 작업에서의 예상 액션 수 (기본값)
        return 12
    
    def get_delay(self, action_type='normal'):
        """
        액션 유형에 따른 적절한 지연 반환
        
        Args:
            action_type (str): 액션 유형 ('critical', 'transition', 'waiting', 'normal')
        
        Returns:
            float: 적용할 지연 시간 (초)
        """
        if self.remaining_delay <= 0:
            return 0
            
        # 액션당 평균 추가 지연
        avg_delay_per_action = self.remaining_delay / max(1, self.action_count)
        
        # 액션 유형별 가중치 적용
        if action_type == 'critical':
            # 중요 액션 (예: 저장 버튼 클릭)
            delay = random.uniform(avg_delay_per_action * 0.8, 
                                  avg_delay_per_action * 2.0)
        elif action_type == 'transition':
            # 전환 액션 (예: 메뉴 이동)
            delay = random.uniform(avg_delay_per_action * 0.5, 
                                  avg_delay_per_action * 1.5)
        elif action_type == 'waiting':
            # 대기 액션 (예: 로딩 기다림)
            delay = random.uniform(avg_delay_per_action * 0.2, 
                                  avg_delay_per_action * 0.8)
        else:  # 'normal'
            # 일반 액션
            delay = random.uniform(avg_delay_per_action * 0.6, 
                                  avg_delay_per_action * 1.2)
        
        # 생각하는 시간 추가 (5% 확률)
        if random.random() < 0.05:
            thinking_time = random.uniform(1, 3)
            delay += thinking_time
            logger.info(f"생각하는 시간 추가: +{thinking_time:.2f}초")
        
        # 남은 지연 시간 및 액션 수 업데이트
        self.remaining_delay -= delay
        self.action_count -= 1
        
        return delay
    
    def get_remaining_delay(self):
        """남은 지연 시간 반환"""
        return max(0, self.remaining_delay)
    
    def apply_thinking_time(self):
        """인간의 '생각하는 시간' 시뮬레이션"""
        thinking_time = random.uniform(2, 5)
        logger.info(f"생각하는 시간: {thinking_time:.2f}초")
        time.sleep(thinking_time)
        return thinking_time
    
    def random_delay(self, min_seconds=None, max_seconds=None):
        """기존 코드와의 호환성을 위한 random_delay 메서드"""
        if min_seconds is None or max_seconds is None:
            # 기본값으로 get_delay 사용
            delay_time = self.get_delay('normal')
        else:
            # 지정된 범위에서 랜덤 지연
            delay_time = random.uniform(min_seconds, max_seconds)
        
        time.sleep(delay_time)
        return delay_time
