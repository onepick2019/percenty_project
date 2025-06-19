#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
새로운 아키텍처 기반 배치 프로세서
기존 batch_processor.py와 동일한 인터페이스를 제공하면서 새로운 아키텍처 사용

사용법:
    python batch_processor_new.py
    
또는 기존 코드에서:
    from batch_processor_new import BatchProcessor
    processor = BatchProcessor()
    processor.run_batch(['account1', 'account2'], 100)
"""

import os
import sys
import time
import logging
import signal
from typing import List, Dict, Optional, Union

# 루트 디렉토리를 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 새로운 아키텍처 모듈들 임포트
from batch.legacy_wrapper import LegacyBatchProcessor
from batch.batch_manager import BatchManager
from core.account.account_manager import CoreAccountManager

# 기존 모듈들 임포트 (호환성)
from timesleep import DELAY_STANDARD, DELAY_SHORT
from human_delay import HumanLikeDelay

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/batch_processor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BatchProcessor:
    """
    새로운 아키텍처 기반 배치 프로세서
    기존 batch_processor.py와 완전히 호환되는 인터페이스 제공
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
        
        # 새로운 아키텍처 사용
        self.legacy_processor = LegacyBatchProcessor(headless=headless, max_workers=max_workers)
        
        # 기존 호환성을 위한 속성들
        self.is_running = False
        self.interrupt_requested = False
        
        # 지연 관리
        self.delay = HumanLikeDelay()
        
        # 시그널 핸들러 설정
        signal.signal(signal.SIGINT, self._signal_handler)
        
        logger.info(f"BatchProcessor 초기화 완료 (새로운 아키텍처 사용)")
        logger.info(f"설정: headless={headless}, max_workers={max_workers}")
    
    def _signal_handler(self, signum, frame):
        """
        시그널 핸들러 (Ctrl+C 등)
        
        Args:
            signum: 시그널 번호
            frame: 프레임
        """
        logger.info("중단 신호를 받았습니다. 안전하게 종료 중...")
        self.interrupt_requested = True
        self.is_running = False
    
    def run_batch(self, accounts: Union[str, List[str]], quantity: int = 100, 
                 concurrent: bool = True) -> Dict:
        """
        배치 실행 (기존 인터페이스 완전 호환)
        
        Args:
            accounts: 계정 목록 또는 단일 계정
            quantity: 처리할 수량
            concurrent: 동시 실행 여부
            
        Returns:
            Dict: 실행 결과
        """
        try:
            self.is_running = True
            self.interrupt_requested = False
            
            print("\n" + "="*60)
            print("    Percenty 자동화 배치 프로세서 (새로운 아키텍처)")
            print("="*60)
            
            # 계정 정보 출력
            if isinstance(accounts, str):
                account_list = [accounts]
            else:
                account_list = list(accounts)
            
            print(f"\n📋 실행 정보:")
            print(f"   • 계정 수: {len(account_list)}개")
            print(f"   • 처리 수량: {quantity}개 (계정당)")
            print(f"   • 실행 모드: {'동시 실행' if concurrent else '순차 실행'}")
            print(f"   • 브라우저: {'헤드리스' if self.headless else '일반'} 모드")
            
            print(f"\n🚀 배치 작업을 시작합니다...")
            print(f"   계정 목록: {', '.join(account_list)}")
            print()
            
            # 새로운 아키텍처로 실행
            result = self.legacy_processor.run_batch(
                accounts=account_list,
                quantity=quantity,
                concurrent=concurrent
            )
            
            # 결과 출력
            self._print_completion_message(result)
            
            return result
            
        except KeyboardInterrupt:
            logger.info("사용자에 의해 중단되었습니다.")
            print("\n⚠️  사용자에 의해 중단되었습니다.")
            return {
                'success': False,
                'error': '사용자 중단',
                'processed': 0,
                'failed': len(account_list) if 'account_list' in locals() else 0
            }
        
        except Exception as e:
            logger.error(f"배치 실행 중 오류: {e}")
            print(f"\n❌ 오류 발생: {e}")
            return {
                'success': False,
                'error': str(e),
                'processed': 0,
                'failed': len(account_list) if 'account_list' in locals() else 0
            }
        
        finally:
            self.is_running = False
    
    def _print_completion_message(self, result: Dict):
        """
        완료 메시지 출력
        
        Args:
            result: 실행 결과
        """
        print("\n" + "="*60)
        
        if result.get('success', False):
            print("✅ 배치 작업이 성공적으로 완료되었습니다!")
        else:
            print("❌ 배치 작업이 실패했습니다.")
        
        print("="*60)
        
        # 통계 정보
        total_processed = result.get('processed', 0)
        total_failed = result.get('failed', 0)
        duration = result.get('duration', 0)
        
        print(f"\n📊 실행 결과:")
        print(f"   • 총 처리: {total_processed}개")
        print(f"   • 총 실패: {total_failed}개")
        
        if duration > 0:
            print(f"   • 소요 시간: {duration:.2f}초")
            if total_processed > 0:
                print(f"   • 평균 처리 속도: {total_processed/duration:.2f}개/초")
        
        # 계정별 상세 결과
        account_results = result.get('results', {})
        if account_results:
            print(f"\n📋 계정별 결과:")
            for account_id, account_result in account_results.items():
                success = account_result.get('success', False)
                processed = account_result.get('processed', 0)
                failed = account_result.get('failed', 0)
                
                status_icon = "✅" if success else "❌"
                print(f"   {status_icon} {account_id}: 처리 {processed}개, 실패 {failed}개")
                
                # 오류 정보
                errors = account_result.get('errors', [])
                if errors:
                    for error in errors[:3]:  # 최대 3개까지만 표시
                        print(f"      ⚠️  {error}")
                    if len(errors) > 3:
                        print(f"      ... 외 {len(errors)-3}개 오류")
        
        if result.get('error'):
            print(f"\n❌ 오류: {result['error']}")
        
        print()
    
    def interruptible_sleep(self, duration: float) -> bool:
        """
        중단 가능한 대기 (기존 호환성)
        
        Args:
            duration: 대기 시간 (초)
            
        Returns:
            bool: 중단되지 않고 완료되면 True
        """
        return self.legacy_processor.interruptible_sleep(duration)
    
    def cleanup(self):
        """
        정리 작업 (기존 호환성)
        """
        try:
            self.legacy_processor.cleanup()
            self.is_running = False
            logger.info("BatchProcessor 정리 완료")
        except Exception as e:
            logger.error(f"정리 작업 중 오류: {e}")
    
    def get_status(self) -> Dict:
        """
        현재 상태 조회 (기존 호환성)
        
        Returns:
            Dict: 현재 상태
        """
        legacy_status = self.legacy_processor.get_status()
        legacy_status['interrupt_requested'] = self.interrupt_requested
        return legacy_status
    
    def stop(self):
        """
        실행 중지 (기존 호환성)
        """
        self.interrupt_requested = True
        self.is_running = False
        self.legacy_processor.stop()
        logger.info("배치 실행 중지 요청")
    
    def __enter__(self):
        """컨텍스트 매니저 진입"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        self.cleanup()

def get_account_input() -> List[str]:
    """
    사용자로부터 계정 입력 받기
    
    Returns:
        List[str]: 계정 목록
    """
    try:
        # 계정 관리자로 사용 가능한 계정 조회
        account_manager = CoreAccountManager()
        available_accounts = account_manager.get_all_accounts()
        
        if not available_accounts:
            print("❌ 등록된 계정이 없습니다.")
            print("   계정을 먼저 등록해주세요.")
            return []
        
        print("\n📋 사용 가능한 계정:")
        for i, account in enumerate(available_accounts, 1):
            status = "활성" if account.get('active', True) else "비활성"
            print(f"   {i}. {account['id']} ({account['email']}) - {status}")
        
        print("\n계정 선택 방법:")
        print("   • 번호로 선택: 1,2,3 또는 1-3")
        print("   • 계정 ID로 선택: account1,account2")
        print("   • 모든 계정: all")
        
        user_input = input("\n사용할 계정을 선택하세요: ").strip()
        
        if not user_input:
            return []
        
        if user_input.lower() == 'all':
            return [acc['id'] for acc in available_accounts if acc.get('active', True)]
        
        # 번호 범위 처리 (예: 1-3)
        if '-' in user_input and user_input.replace('-', '').replace(',', '').isdigit():
            parts = user_input.split('-')
            if len(parts) == 2:
                start, end = int(parts[0]), int(parts[1])
                if 1 <= start <= len(available_accounts) and 1 <= end <= len(available_accounts):
                    return [available_accounts[i-1]['id'] for i in range(start, end+1)]
        
        # 번호 또는 ID 목록 처리
        selected = []
        for item in user_input.split(','):
            item = item.strip()
            
            # 번호인 경우
            if item.isdigit():
                idx = int(item) - 1
                if 0 <= idx < len(available_accounts):
                    selected.append(available_accounts[idx]['id'])
            else:
                # 계정 ID인 경우
                if any(acc['id'] == item for acc in available_accounts):
                    selected.append(item)
        
        return selected
        
    except Exception as e:
        logger.error(f"계정 입력 처리 중 오류: {e}")
        return []

def get_quantity_input() -> int:
    """
    사용자로부터 수량 입력 받기
    
    Returns:
        int: 처리할 수량
    """
    try:
        while True:
            user_input = input("처리할 수량을 입력하세요 (기본값: 100): ").strip()
            
            if not user_input:
                return 100
            
            if user_input.isdigit():
                quantity = int(user_input)
                if 1 <= quantity <= 1000:
                    return quantity
                else:
                    print("❌ 수량은 1-1000 사이여야 합니다.")
            else:
                print("❌ 올바른 숫자를 입력해주세요.")
    
    except Exception as e:
        logger.error(f"수량 입력 처리 중 오류: {e}")
        return 100

def main():
    """
    메인 함수 (기존 batch_processor.py와 동일한 동작)
    """
    try:
        print("\n" + "="*60)
        print("    Percenty 자동화 배치 프로세서 (새로운 아키텍처)")
        print("    기존 batch_processor.py와 완전 호환")
        print("="*60)
        
        # 계정 선택
        accounts = get_account_input()
        if not accounts:
            print("\n❌ 선택된 계정이 없습니다. 프로그램을 종료합니다.")
            return
        
        # 수량 입력
        quantity = get_quantity_input()
        
        # 실행 모드 선택
        print("\n실행 모드:")
        print("   1. 동시 실행 (빠름, 리소스 많이 사용)")
        print("   2. 순차 실행 (안정적, 리소스 적게 사용)")
        
        mode_input = input("실행 모드를 선택하세요 (1 또는 2, 기본값: 1): ").strip()
        concurrent = mode_input != '2'
        
        # 브라우저 모드 선택
        print("\n브라우저 모드:")
        print("   1. 일반 모드 (브라우저 창 표시)")
        print("   2. 헤드리스 모드 (백그라운드 실행)")
        
        browser_input = input("브라우저 모드를 선택하세요 (1 또는 2, 기본값: 1): ").strip()
        headless = browser_input == '2'
        
        # 배치 프로세서 생성 및 실행
        with BatchProcessor(headless=headless) as processor:
            result = processor.run_batch(accounts, quantity, concurrent)
            
            # 결과에 따른 종료 코드 설정
            if result.get('success', False):
                print("\n🎉 모든 작업이 성공적으로 완료되었습니다!")
                sys.exit(0)
            else:
                print("\n⚠️  일부 작업이 실패했습니다. 로그를 확인해주세요.")
                sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  사용자에 의해 중단되었습니다.")
        sys.exit(130)
    
    except Exception as e:
        logger.error(f"메인 함수 실행 중 오류: {e}")
        print(f"\n❌ 예상치 못한 오류가 발생했습니다: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # 로그 디렉토리 생성
    os.makedirs('logs', exist_ok=True)
    
    # 메인 함수 실행
    main()