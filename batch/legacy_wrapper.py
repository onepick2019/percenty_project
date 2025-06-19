#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
기존 batch_processor.py와의 호환성을 위한 래퍼
기존 코드가 새로운 아키텍처와 원활하게 작동하도록 지원
"""

import os
import sys
import logging
from typing import Optional, Dict, Any

# 루트 디렉토리를 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 새로운 배치 관리자 임포트
from batch.batch_manager import BatchManager

# 기존 모듈들 임포트 (호환성) - app 폴더 의존성 제거
# app 모듈이 백업으로 이동되었으므로 더미 클래스 사용
class BaseStepManager:
    """app 폴더 백업으로 인한 더미 클래스"""
    pass

class Step1Manager:
    """app 폴더 백업으로 인한 더미 클래스"""
    pass

logger = logging.getLogger(__name__)

class LegacyBatchProcessor:
    """
    기존 batch_processor.py와 호환되는 래퍼 클래스
    
    기존 코드:
    ```python
    from batch_processor import BatchProcessor
    processor = BatchProcessor()
    processor.run_batch(accounts, quantity)
    ```
    
    새로운 코드 (동일한 인터페이스):
    ```python
    from batch.legacy_wrapper import LegacyBatchProcessor as BatchProcessor
    processor = BatchProcessor()
    processor.run_batch(accounts, quantity)
    ```
    """
    
    def __init__(self, headless: bool = False, max_workers: int = 4):
        """
        초기화
        
        Args:
            headless: 헤드리스 모드 여부
            max_workers: 최대 워커 수
        """
        self.headless = headless
        self.max_workers = max_workers
        
        # 새로운 배치 관리자 초기화
        self.batch_manager = BatchManager()
        
        # 설정 업데이트
        self.batch_manager.config['browser']['headless'] = headless
        self.batch_manager.config['batch']['max_workers'] = max_workers
        self.batch_manager.max_workers = max_workers
        
        # 기존 호환성을 위한 속성들
        self.is_running = False
        self.current_account = None
        self.processed_count = 0
        self.failed_count = 0
        
        logger.info(f"LegacyBatchProcessor 초기화 완료 (headless={headless}, workers={max_workers})")
    
    def run_batch(self, accounts: list, quantity: int = 100, 
                 concurrent: bool = True) -> Dict[str, Any]:
        """
        배치 실행 (기존 인터페이스 호환)
        
        Args:
            accounts: 계정 목록 또는 계정 ID 문자열
            quantity: 처리할 수량
            concurrent: 동시 실행 여부
            
        Returns:
            Dict: 실행 결과
        """
        try:
            self.is_running = True
            
            # 계정 목록 정규화
            if isinstance(accounts, str):
                account_list = [accounts]
            elif isinstance(accounts, list):
                account_list = accounts
            else:
                raise ValueError("accounts는 문자열 또는 리스트여야 합니다.")
            
            logger.info(f"배치 실행 시작 - 계정: {len(account_list)}개, 수량: {quantity}")
            
            # 새로운 배치 관리자로 실행
            result = self.batch_manager.run_single_step(
                step=1,  # 기존 batch_processor는 1단계만 처리
                accounts=account_list,
                quantity=quantity,
                concurrent=concurrent
            )
            
            # 기존 형식으로 결과 변환
            legacy_result = self._convert_to_legacy_format(result)
            
            # 상태 업데이트
            self._update_legacy_status(legacy_result)
            
            logger.info(f"배치 실행 완료 - 성공: {legacy_result['success']}")
            
            return legacy_result
            
        except Exception as e:
            logger.error(f"배치 실행 중 오류: {e}")
            return {
                'success': False,
                'error': str(e),
                'processed': 0,
                'failed': len(account_list) if 'account_list' in locals() else 0,
                'results': {}
            }
        
        finally:
            self.is_running = False
    
    def _convert_to_legacy_format(self, result: Dict) -> Dict:
        """
        새로운 형식의 결과를 기존 형식으로 변환
        
        Args:
            result: 새로운 형식의 결과
            
        Returns:
            Dict: 기존 형식의 결과
        """
        legacy_result = {
            'success': result.get('success', False),
            'processed': 0,
            'failed': 0,
            'results': {},
            'task_id': result.get('task_id', ''),
            'duration': result.get('duration', 0)
        }
        
        # 계정별 결과 처리
        for account_id, account_result in result.get('results', {}).items():
            if account_result.get('success', False):
                legacy_result['processed'] += account_result.get('processed', 0)
            else:
                legacy_result['failed'] += 1
            
            legacy_result['results'][account_id] = account_result
        
        return legacy_result
    
    def _update_legacy_status(self, result: Dict):
        """
        기존 상태 변수들 업데이트
        
        Args:
            result: 실행 결과
        """
        self.processed_count = result.get('processed', 0)
        self.failed_count = result.get('failed', 0)
    
    def stop(self):
        """
        실행 중지 (기존 인터페이스 호환)
        """
        try:
            self.is_running = False
            # 향후 배치 관리자에 중지 기능이 구현되면 호출
            # self.batch_manager.stop_current_task()
            logger.info("배치 실행 중지 요청")
        except Exception as e:
            logger.error(f"배치 중지 중 오류: {e}")
    
    def get_status(self) -> Dict:
        """
        현재 상태 조회 (기존 인터페이스 호환)
        
        Returns:
            Dict: 현재 상태
        """
        return {
            'is_running': self.is_running,
            'current_account': self.current_account,
            'processed': self.processed_count,
            'failed': self.failed_count
        }
    
    def cleanup(self):
        """
        정리 작업 (기존 인터페이스 호환)
        """
        try:
            self.batch_manager.cleanup()
            self.is_running = False
            logger.info("LegacyBatchProcessor 정리 완료")
        except Exception as e:
            logger.error(f"정리 작업 중 오류: {e}")
    
    # 기존 코드에서 사용될 수 있는 추가 메서드들
    def interruptible_sleep(self, duration: float) -> bool:
        """
        중단 가능한 대기 (기존 호환성)
        
        Args:
            duration: 대기 시간 (초)
            
        Returns:
            bool: 중단되지 않고 완료되면 True
        """
        import time
        
        start_time = time.time()
        while time.time() - start_time < duration:
            if not self.is_running:
                return False
            time.sleep(0.1)
        return True
    
    def __enter__(self):
        """컨텍스트 매니저 진입"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        self.cleanup()

# 기존 코드와의 완전한 호환성을 위한 별칭
BatchProcessor = LegacyBatchProcessor

# 기존 함수들 호환성
def create_batch_processor(headless: bool = False, max_workers: int = 4) -> LegacyBatchProcessor:
    """
    배치 프로세서 생성 함수 (기존 호환성)
    
    Args:
        headless: 헤드리스 모드 여부
        max_workers: 최대 워커 수
        
    Returns:
        LegacyBatchProcessor: 배치 프로세서 인스턴스
    """
    return LegacyBatchProcessor(headless=headless, max_workers=max_workers)

def run_legacy_batch(accounts: list, quantity: int = 100, 
                    headless: bool = False, concurrent: bool = True) -> Dict:
    """
    기존 스타일의 배치 실행 함수
    
    Args:
        accounts: 계정 목록
        quantity: 수량
        headless: 헤드리스 모드
        concurrent: 동시 실행 여부
        
    Returns:
        Dict: 실행 결과
    """
    with LegacyBatchProcessor(headless=headless) as processor:
        return processor.run_batch(accounts, quantity, concurrent)

if __name__ == "__main__":
    # 테스트 코드
    print("Legacy Wrapper 테스트")
    
    # 기존 방식으로 사용 가능
    processor = BatchProcessor(headless=True)
    print(f"프로세서 상태: {processor.get_status()}")
    processor.cleanup()
    
    print("Legacy Wrapper 모듈이 로드되었습니다.")