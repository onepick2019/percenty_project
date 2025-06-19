# -*- coding: utf-8 -*-
"""
간단한 스케줄러 구현

schedule 라이브러리가 없을 때 사용할 수 있는 기본 스케줄링 기능
"""

import time
import threading
import logging
from datetime import datetime, timedelta
from typing import Callable, Optional

logger = logging.getLogger(__name__)

class SimpleScheduler:
    """간단한 스케줄러 클래스"""
    
    def __init__(self):
        self.scheduler_thread = None
        self.is_running = False
        self.target_time = None  # "HH:MM" 형식
        self.callback_function = None
        self.last_run_date = None
        
    def schedule_daily(self, time_str: str, callback: Callable):
        """매일 지정된 시간에 실행되는 스케줄 설정
        
        Args:
            time_str: 실행 시간 (예: "09:00")
            callback: 실행할 콜백 함수
        """
        try:
            # 시간 형식 검증
            time_parts = time_str.split(':')
            if len(time_parts) != 2:
                raise ValueError("시간 형식이 올바르지 않습니다. HH:MM 형식으로 입력하세요.")
            
            hour = int(time_parts[0])
            minute = int(time_parts[1])
            
            if not (0 <= hour <= 23) or not (0 <= minute <= 59):
                raise ValueError("올바른 시간을 입력하세요. (시: 0-23, 분: 0-59)")
            
            self.target_time = time_str
            self.callback_function = callback
            self.last_run_date = None
            
            # 기존 스케줄러 중지
            self.stop()
            
            # 새 스케줄러 시작
            self.is_running = True
            self.scheduler_thread = threading.Thread(
                target=self._run_scheduler,
                daemon=True,
                name="SimpleScheduler"
            )
            self.scheduler_thread.start()
            
            logger.info(f"매일 {time_str}에 실행되는 스케줄이 설정되었습니다.")
            
        except Exception as e:
            logger.error(f"스케줄 설정 중 오류: {e}")
            raise
    
    def stop(self):
        """스케줄러 중지"""
        try:
            self.is_running = False
            
            if self.scheduler_thread and self.scheduler_thread.is_alive():
                # 스레드가 종료될 때까지 잠시 대기
                time.sleep(1)
            
            logger.info("스케줄러가 중지되었습니다.")
            
        except Exception as e:
            logger.error(f"스케줄러 중지 중 오류: {e}")
    
    def _run_scheduler(self):
        """스케줄러 실행 루프"""
        logger.info("간단한 스케줄러가 시작되었습니다.")
        
        while self.is_running:
            try:
                current_time = datetime.now()
                current_date = current_time.date()
                current_time_str = current_time.strftime("%H:%M")
                
                # 목표 시간과 현재 시간 비교
                if (self.target_time == current_time_str and 
                    self.last_run_date != current_date):
                    
                    logger.info(f"스케줄된 시간({self.target_time})에 도달했습니다. 콜백 실행...")
                    
                    try:
                        if self.callback_function:
                            self.callback_function()
                        self.last_run_date = current_date
                        logger.info("스케줄된 작업이 완료되었습니다.")
                    except Exception as e:
                        logger.error(f"스케줄된 작업 실행 중 오류: {e}")
                
                # 30초마다 체크 (더 정확한 시간 체크를 위해)
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"스케줄러 실행 중 오류: {e}")
                time.sleep(60)  # 오류 발생 시 1분 대기
        
        logger.info("간단한 스케줄러가 종료되었습니다.")
    
    def get_next_run_time(self) -> Optional[str]:
        """다음 실행 시간 반환"""
        if not self.target_time:
            return None
        
        try:
            current_time = datetime.now()
            current_date = current_time.date()
            
            # 목표 시간 파싱
            time_parts = self.target_time.split(':')
            target_hour = int(time_parts[0])
            target_minute = int(time_parts[1])
            
            # 오늘의 목표 시간
            today_target = datetime.combine(
                current_date, 
                datetime.min.time().replace(hour=target_hour, minute=target_minute)
            )
            
            # 이미 오늘 실행했거나 오늘의 목표 시간이 지났으면 내일로
            if (self.last_run_date == current_date or 
                current_time >= today_target):
                next_run = today_target + timedelta(days=1)
            else:
                next_run = today_target
            
            return next_run.strftime("%Y-%m-%d %H:%M:%S")
            
        except Exception as e:
            logger.error(f"다음 실행 시간 계산 중 오류: {e}")
            return None
    
    def is_schedule_running(self) -> bool:
        """스케줄러가 실행 중인지 확인"""
        return self.is_running and self.scheduler_thread and self.scheduler_thread.is_alive()
    
    def get_status(self) -> dict:
        """스케줄러 상태 반환"""
        return {
            'is_running': self.is_running,
            'target_time': self.target_time,
            'last_run_date': str(self.last_run_date) if self.last_run_date else None,
            'next_run_time': self.get_next_run_time(),
            'thread_alive': self.scheduler_thread.is_alive() if self.scheduler_thread else False
        }