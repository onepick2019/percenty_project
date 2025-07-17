# -*- coding: utf-8 -*-
"""
통합 에러 처리 시스템
표준화된 에러 처리, 재시도 로직, 복구 메커니즘을 제공
"""

import time
import logging
import functools
import traceback
from typing import Callable, Any, Optional, Dict, List
from enum import Enum

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """에러 심각도"""
    LOW = "LOW"           # 재시도로 해결 가능
    MEDIUM = "MEDIUM"     # 대안 방법 필요
    HIGH = "HIGH"         # 즉시 중단 필요
    CRITICAL = "CRITICAL" # 시스템 전체 중단

class RecoveryStrategy(Enum):
    """복구 전략"""
    RETRY = "RETRY"                    # 단순 재시도
    ALTERNATIVE_METHOD = "ALTERNATIVE" # 대안 방법 시도
    FALLBACK = "FALLBACK"             # 폴백 로직 실행
    ABORT = "ABORT"                   # 작업 중단

class UnifiedErrorHandler:
    """통합 에러 처리 시스템"""
    
    def __init__(self):
        self.error_history = []
        self.recovery_strategies = {}
        self.error_patterns = {}
        
    def register_recovery_strategy(self, error_type: type, strategy: RecoveryStrategy, 
                                 recovery_func: Optional[Callable] = None):
        """복구 전략 등록"""
        self.recovery_strategies[error_type] = {
            'strategy': strategy,
            'recovery_func': recovery_func
        }
    
    def handle_with_recovery(self, func: Callable, *args, 
                           max_retries: int = 3,
                           retry_delay: float = 1.0,
                           fallback_func: Optional[Callable] = None,
                           operation_name: str = "작업",
                           **kwargs) -> Any:
        """
        복구 메커니즘이 포함된 에러 처리
        
        Args:
            func: 실행할 함수
            max_retries: 최대 재시도 횟수
            retry_delay: 재시도 간격 (초)
            fallback_func: 폴백 함수
            operation_name: 작업 이름
            
        Returns:
            함수 실행 결과
        """
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    logger.info(f"🔄 재시도 {attempt}/{max_retries}: {operation_name}")
                
                result = func(*args, **kwargs)
                
                if attempt > 0:
                    logger.info(f"✅ 재시도 성공: {operation_name} (시도 {attempt + 1})")
                
                return result
                
            except Exception as e:
                last_exception = e
                error_info = self._analyze_error(e, operation_name, attempt)
                
                # 에러 기록
                self._record_error(error_info)
                
                # 심각도에 따른 처리
                if error_info['severity'] == ErrorSeverity.CRITICAL:
                    logger.critical(f"🚨 치명적 에러 발생: {operation_name} - {e}")
                    raise e
                
                # 마지막 시도인 경우
                if attempt == max_retries:
                    if fallback_func:
                        logger.warning(f"🔄 폴백 함수 실행: {operation_name}")
                        try:
                            return fallback_func(*args, **kwargs)
                        except Exception as fallback_error:
                            logger.error(f"❌ 폴백 함수도 실패: {fallback_error}")
                    
                    logger.error(f"❌ 최대 재시도 횟수 초과: {operation_name} - {e}")
                    raise e
                
                # 복구 전략 실행
                recovery_result = self._execute_recovery_strategy(e, error_info)
                if recovery_result == 'abort':
                    logger.error(f"🛑 복구 불가능한 에러: {operation_name} - {e}")
                    raise e
                
                # 재시도 전 대기
                if attempt < max_retries:
                    adjusted_delay = retry_delay * (1.5 ** attempt)  # 지수 백오프
                    logger.debug(f"⏳ {adjusted_delay:.1f}초 대기 후 재시도...")
                    time.sleep(adjusted_delay)
        
        # 여기에 도달하면 안 됨
        raise last_exception
    
    def _analyze_error(self, error: Exception, operation: str, attempt: int) -> Dict:
        """에러 분석 및 분류"""
        error_type = type(error).__name__
        error_message = str(error)
        
        # 에러 심각도 판단
        severity = self._determine_severity(error, error_message)
        
        # 복구 가능성 판단
        recoverable = self._is_recoverable(error, error_message)
        
        error_info = {
            'timestamp': time.time(),
            'operation': operation,
            'attempt': attempt,
            'error_type': error_type,
            'error_message': error_message,
            'severity': severity,
            'recoverable': recoverable,
            'traceback': traceback.format_exc()
        }
        
        return error_info
    
    def _determine_severity(self, error: Exception, message: str) -> ErrorSeverity:
        """에러 심각도 판단"""
        error_type = type(error).__name__
        
        # 치명적 에러 패턴
        critical_patterns = [
            'MemoryError',
            'SystemExit',
            'KeyboardInterrupt',
            'OutOfMemoryError'
        ]
        
        # 높은 심각도 에러 패턴
        high_patterns = [
            'WebDriverException',
            'SessionNotCreatedException',
            'InvalidSessionIdException'
        ]
        
        # 중간 심각도 에러 패턴
        medium_patterns = [
            'TimeoutException',
            'NoSuchElementException',
            'ElementNotInteractableException'
        ]
        
        if any(pattern in error_type for pattern in critical_patterns):
            return ErrorSeverity.CRITICAL
        elif any(pattern in error_type for pattern in high_patterns):
            return ErrorSeverity.HIGH
        elif any(pattern in error_type for pattern in medium_patterns):
            return ErrorSeverity.MEDIUM
        else:
            return ErrorSeverity.LOW
    
    def _is_recoverable(self, error: Exception, message: str) -> bool:
        """복구 가능성 판단"""
        error_type = type(error).__name__
        
        # 복구 불가능한 에러들
        unrecoverable_patterns = [
            'MemoryError',
            'SystemExit',
            'KeyboardInterrupt',
            'InvalidArgumentException'
        ]
        
        return not any(pattern in error_type for pattern in unrecoverable_patterns)
    
    def _execute_recovery_strategy(self, error: Exception, error_info: Dict) -> str:
        """복구 전략 실행"""
        error_type = type(error)
        
        if error_type in self.recovery_strategies:
            strategy_info = self.recovery_strategies[error_type]
            strategy = strategy_info['strategy']
            recovery_func = strategy_info['recovery_func']
            
            logger.info(f"🔧 복구 전략 실행: {strategy.value}")
            
            if strategy == RecoveryStrategy.ALTERNATIVE_METHOD and recovery_func:
                try:
                    recovery_func()
                    return 'recovered'
                except Exception as recovery_error:
                    logger.warning(f"복구 함수 실패: {recovery_error}")
                    return 'continue'
            
            elif strategy == RecoveryStrategy.ABORT:
                return 'abort'
        
        return 'continue'
    
    def _record_error(self, error_info: Dict):
        """에러 기록"""
        self.error_history.append(error_info)
        
        # 최근 1000개 기록만 유지
        if len(self.error_history) > 1000:
            self.error_history = self.error_history[-1000:]
        
        # 로그 출력
        severity = error_info['severity']
        operation = error_info['operation']
        error_type = error_info['error_type']
        error_message = error_info['error_message']
        
        if severity == ErrorSeverity.CRITICAL:
            logger.critical(f"🚨 {operation}: {error_type} - {error_message}")
        elif severity == ErrorSeverity.HIGH:
            logger.error(f"🔴 {operation}: {error_type} - {error_message}")
        elif severity == ErrorSeverity.MEDIUM:
            logger.warning(f"🟡 {operation}: {error_type} - {error_message}")
        else:
            logger.info(f"🔵 {operation}: {error_type} - {error_message}")
    
    def get_error_statistics(self) -> Dict:
        """에러 통계 정보 반환"""
        if not self.error_history:
            return {"message": "에러 기록 없음"}
        
        total_errors = len(self.error_history)
        error_types = {}
        severity_counts = {}
        
        for error in self.error_history:
            error_type = error['error_type']
            severity = error['severity']
            
            error_types[error_type] = error_types.get(error_type, 0) + 1
            severity_counts[severity.value] = severity_counts.get(severity.value, 0) + 1
        
        return {
            "total_errors": total_errors,
            "error_types": error_types,
            "severity_distribution": severity_counts,
            "most_common_error": max(error_types.items(), key=lambda x: x[1]) if error_types else None
        }

# 데코레이터 함수들
def with_error_handling(max_retries: int = 3, retry_delay: float = 1.0, 
                       operation_name: str = None):
    """에러 처리 데코레이터"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            handler = UnifiedErrorHandler()
            op_name = operation_name or func.__name__
            return handler.handle_with_recovery(
                func, *args, 
                max_retries=max_retries,
                retry_delay=retry_delay,
                operation_name=op_name,
                **kwargs
            )
        return wrapper
    return decorator

def with_fallback(fallback_func: Callable):
    """폴백 함수가 있는 에러 처리 데코레이터"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            handler = UnifiedErrorHandler()
            return handler.handle_with_recovery(
                func, *args,
                fallback_func=fallback_func,
                operation_name=func.__name__,
                **kwargs
            )
        return wrapper
    return decorator