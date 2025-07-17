# -*- coding: utf-8 -*-
"""
중앙화된 설정 관리 클래스
프로젝트 전반의 설정을 일관성 있게 관리합니다.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class BatchLimits:
    """배치 작업 제한 설정"""
    max_products: int = 20
    max_images: int = 2000
    max_translation_per_product: int = 50
    timeout_seconds: int = 300

@dataclass
class BrowserSettings:
    """브라우저 관련 설정"""
    headless: bool = False
    window_width: int = 1920
    window_height: int = 1080
    user_agent: Optional[str] = None
    download_path: Optional[str] = None

@dataclass
class LoggingSettings:
    """로깅 관련 설정"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5

@dataclass
class PerformanceSettings:
    """성능 관련 설정"""
    enable_monitoring: bool = True
    slow_operation_threshold: float = 5.0  # 초
    memory_warning_threshold: int = 80  # 퍼센트
    cpu_warning_threshold: int = 90  # 퍼센트

class SettingsManager:
    """중앙화된 설정 관리자"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        설정 관리자 초기화
        
        Args:
            config_path: 설정 파일 경로 (None이면 기본 경로 사용)
        """
        self.config_path = config_path or self._get_default_config_path()
        self.batch_limits = BatchLimits()
        self.browser_settings = BrowserSettings()
        self.logging_settings = LoggingSettings()
        self.performance_settings = PerformanceSettings()
        
        # 설정 파일이 존재하면 로드
        if os.path.exists(self.config_path):
            self.load_from_file()
        else:
            logger.info(f"설정 파일이 없어 기본값 사용: {self.config_path}")
    
    def _get_default_config_path(self) -> str:
        """기본 설정 파일 경로 반환"""
        project_root = Path(__file__).parent.parent.parent
        return str(project_root / "config" / "settings.json")
    
    def load_from_file(self) -> None:
        """파일에서 설정 로드"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # 각 설정 섹션 업데이트
            if 'batch_limits' in config_data:
                self.batch_limits = BatchLimits(**config_data['batch_limits'])
            
            if 'browser_settings' in config_data:
                self.browser_settings = BrowserSettings(**config_data['browser_settings'])
            
            if 'logging_settings' in config_data:
                self.logging_settings = LoggingSettings(**config_data['logging_settings'])
            
            if 'performance_settings' in config_data:
                self.performance_settings = PerformanceSettings(**config_data['performance_settings'])
            
            logger.info(f"설정 파일 로드 완료: {self.config_path}")
            
        except Exception as e:
            logger.error(f"설정 파일 로드 실패: {e}")
            logger.info("기본 설정값 사용")
    
    def save_to_file(self) -> None:
        """현재 설정을 파일에 저장"""
        try:
            # 디렉토리 생성
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            config_data = {
                'batch_limits': asdict(self.batch_limits),
                'browser_settings': asdict(self.browser_settings),
                'logging_settings': asdict(self.logging_settings),
                'performance_settings': asdict(self.performance_settings)
            }
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"설정 파일 저장 완료: {self.config_path}")
            
        except Exception as e:
            logger.error(f"설정 파일 저장 실패: {e}")
    
    def get_batch_limit(self, limit_type: str) -> int:
        """배치 제한값 반환"""
        return getattr(self.batch_limits, limit_type, 0)
    
    def update_batch_limit(self, limit_type: str, value: int) -> None:
        """배치 제한값 업데이트"""
        if hasattr(self.batch_limits, limit_type):
            setattr(self.batch_limits, limit_type, value)
            logger.info(f"배치 제한값 업데이트: {limit_type} = {value}")
        else:
            logger.warning(f"알 수 없는 배치 제한 타입: {limit_type}")
    
    def is_performance_monitoring_enabled(self) -> bool:
        """성능 모니터링 활성화 여부 반환"""
        return self.performance_settings.enable_monitoring
    
    def get_slow_operation_threshold(self) -> float:
        """느린 작업 임계값 반환"""
        return self.performance_settings.slow_operation_threshold

# 전역 설정 인스턴스
settings = SettingsManager()