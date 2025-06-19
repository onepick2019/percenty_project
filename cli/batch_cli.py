#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
배치 관리자 CLI 인터페이스
명령줄에서 배치 작업을 실행하고 관리할 수 있는 도구
"""

import os
import sys
import argparse
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
import threading
import time

# 루트 디렉토리를 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 배치 관리자 임포트
from batch.batch_manager import BatchManager, run_step1_for_accounts, run_all_steps_for_account, get_real_account_id
from core.account.account_manager import CoreAccountManager

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BatchCLI:
    """
    배치 관리자 CLI 클래스 (통합 로그 관리 기능 포함)
    """
    
    def __init__(self):
        self.batch_manager = BatchManager()
        self.account_manager = CoreAccountManager()
        self.unified_log_session = None
        self.unified_log_lock = threading.Lock()
        self._setup_unified_logging()
    
    def _setup_unified_logging(self):
        """통합 로그 세션 설정"""
        self.unified_log_session = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.unified_log_dir = Path("logs") / "unified" / self.unified_log_session
        self.unified_log_dir.mkdir(parents=True, exist_ok=True)
        
        # 통합 로그 파일 설정
        self.unified_log_file = self.unified_log_dir / "batch_execution.log"
        self.unified_summary_file = self.unified_log_dir / "execution_summary.md"
        
        # 통합 로그 핸들러 설정
        self.unified_logger = logging.getLogger(f"unified_batch_{self.unified_log_session}")
        self.unified_logger.setLevel(logging.INFO)
        
        # 기존 핸들러 제거
        for handler in self.unified_logger.handlers[:]:
            self.unified_logger.removeHandler(handler)
        
        # 파일 핸들러 추가
        file_handler = logging.FileHandler(self.unified_log_file, encoding='utf-8')
        file_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        self.unified_logger.addHandler(file_handler)
        
        # 콘솔 핸들러 추가
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '%(asctime)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.unified_logger.addHandler(console_handler)
        
        self.unified_logger.propagate = False
        
        # 세션 시작 로그
        self._log_unified(f"🚀 통합 배치 세션 시작: {self.unified_log_session}")
    
    def _log_unified(self, message: str, level: str = "INFO"):
        """통합 로그 기록"""
        with self.unified_log_lock:
            if level == "ERROR":
                self.unified_logger.error(message)
            elif level == "WARNING":
                self.unified_logger.warning(message)
            else:
                self.unified_logger.info(message)
    
    def _create_unified_summary(self, all_results: List[Dict]):
        """통합 실행 요약 보고서 생성"""
        try:
            with open(self.unified_summary_file, 'w', encoding='utf-8') as f:
                f.write(f"# 통합 배치 실행 요약 보고서\n\n")
                f.write(f"**세션 ID:** {self.unified_log_session}\n")
                f.write(f"**실행 시간:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**총 배치 작업 수:** {len(all_results)}개\n\n")
                
                total_accounts = 0
                total_success_accounts = 0
                total_processed_items = 0
                total_failed_items = 0
                
                for i, result in enumerate(all_results, 1):
                    f.write(f"## 배치 작업 {i}\n")
                    f.write(f"- **작업 ID:** {result.get('task_id', 'N/A')}\n")
                    f.write(f"- **소요 시간:** {result.get('duration', 0):.2f}초\n")
                    f.write(f"- **전체 성공:** {'✅' if result.get('success', False) else '❌'}\n")
                    
                    account_results = result.get('results', {})
                    success_count = sum(1 for r in account_results.values() if r.get('success', False))
                    processed_count = sum(r.get('processed', 0) for r in account_results.values())
                    failed_count = sum(r.get('failed', 0) for r in account_results.values())
                    
                    f.write(f"- **계정 수:** {len(account_results)}개 (성공: {success_count}개)\n")
                    f.write(f"- **처리 완료:** {processed_count}개\n")
                    f.write(f"- **처리 실패:** {failed_count}개\n\n")
                    
                    total_accounts += len(account_results)
                    total_success_accounts += success_count
                    total_processed_items += processed_count
                    total_failed_items += failed_count
                
                # 전체 통계
                f.write(f"## 전체 통계\n\n")
                f.write(f"- **총 계정 수:** {total_accounts}개\n")
                f.write(f"- **성공한 계정:** {total_success_accounts}개\n")
                f.write(f"- **실패한 계정:** {total_accounts - total_success_accounts}개\n")
                f.write(f"- **총 처리 완료:** {total_processed_items}개\n")
                f.write(f"- **총 처리 실패:** {total_failed_items}개\n")
                
                overall_success_rate = (total_success_accounts / total_accounts * 100) if total_accounts > 0 else 0
                f.write(f"- **전체 성공률:** {overall_success_rate:.1f}%\n\n")
                
                # 로그 파일 위치
                f.write(f"## 로그 파일 위치\n\n")
                f.write(f"- **통합 로그:** `{self.unified_log_file}`\n")
                f.write(f"- **통합 요약:** `{self.unified_summary_file}`\n")
                
                for result in all_results:
                    start_time = result.get('start_time', '')
                    if start_time:
                        f.write(f"- **개별 로그 ({result.get('task_id', 'N/A')}):** `logs/accounts/{start_time}/`\n")
            
            self._log_unified(f"📊 통합 요약 보고서 생성 완료: {self.unified_summary_file}")
            
        except Exception as e:
            self._log_unified(f"❌ 통합 요약 보고서 생성 실패: {e}", "ERROR")
    
    def run_single_step(self, args):
        """
        단일 단계 실행 (통합 로그 기능 포함)
        
        Args:
            args: 명령줄 인수
        """
        all_results = []
        
        try:
            # 계정 ID를 올바른 형식으로 변환 (숫자 -> account_숫자)
            converted_accounts = []
            for account in args.accounts:
                if account.isdigit():
                    converted_accounts.append(f"account_{account}")
                else:
                    converted_accounts.append(account)
            
            # 가상 계정 ID를 실제 이메일로 변환
            real_accounts = []
            for account in converted_accounts:
                real_account = get_real_account_id(account)
                real_accounts.append(real_account)
                self._log_unified(f"🔄 계정 매핑: {account} -> {real_account}")
            
            # 통합 로그 기록
            self._log_unified(f"📋 {args.step}단계 배치 실행 시작")
            self._log_unified(f"📝 입력 계정: {args.accounts}")
            self._log_unified(f"🔄 변환된 계정: {converted_accounts}")
            self._log_unified(f"📧 실제 계정: {real_accounts}")
            self._log_unified(f"📦 수량: {args.quantity}")
            self._log_unified(f"⚡ 동시 실행: {args.concurrent}")
            self._log_unified(f"⏱️ 실행 간격: {args.interval}초")
            
            print(f"\n=== {args.step}단계 배치 실행 ===")
            print(f"입력 계정: {args.accounts}")
            print(f"변환된 계정: {converted_accounts}")
            print(f"실제 계정: {real_accounts}")
            print(f"수량: {args.quantity}")
            print(f"동시 실행: {args.concurrent}")
            print(f"실행 간격: {args.interval}초")
            print(f"통합 로그 세션: {self.unified_log_session}")
            print()
            
            start_time = time.time()
            
            result = self.batch_manager.run_single_step(
                step=args.step,
                accounts=real_accounts,  # 실제 이메일 주소 사용
                quantity=args.quantity,
                concurrent=args.concurrent,
                interval=args.interval,
                chunk_size=args.chunk_size
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            # 결과에 통합 로그 정보 추가
            result['unified_session'] = self.unified_log_session
            result['unified_log_file'] = str(self.unified_log_file)
            
            all_results.append(result)
            
            # 통합 로그 기록
            success_count = sum(1 for r in result.get('results', {}).values() if r.get('success', False))
            total_accounts = len(result.get('results', {}))
            total_processed = sum(r.get('processed', 0) for r in result.get('results', {}).values())
            
            self._log_unified(f"✅ 배치 실행 완료 - 성공: {success_count}/{total_accounts}개 계정, 처리: {total_processed}개")
            
            self._print_result(result)
            
            if args.output:
                self._save_result(result, args.output)
            
            # 통합 요약 보고서 생성
            self._create_unified_summary(all_results)
            
            # 통합 로그 파일 위치 안내
            print(f"\n📁 통합 로그 파일: {self.unified_log_file}")
            print(f"📊 통합 요약 보고서: {self.unified_summary_file}")
            
        except Exception as e:
            error_msg = f"오류 발생: {e}"
            print(error_msg)
            logger.error(f"단일 단계 실행 중 오류: {e}")
            self._log_unified(f"❌ 배치 실행 실패: {e}", "ERROR")
        
        finally:
            self.batch_manager.cleanup()
            self._log_unified(f"🏁 배치 세션 종료: {self.unified_log_session}")
    
    def run_multi_step(self, args):
        """
        다중 단계 실행 (통합 로그 기능 포함)
        
        Args:
            args: 명령줄 인수
        """
        all_results = []
        
        try:
            # 계정 ID를 올바른 형식으로 변환 (숫자 -> account_숫자)
            converted_account = args.account
            if args.account.isdigit():
                converted_account = f"account_{args.account}"
            
            # 가상 계정 ID를 실제 이메일로 변환
            real_account = get_real_account_id(converted_account)
            
            # 통합 로그 기록
            self._log_unified(f"📋 다중 단계 배치 실행 시작")
            self._log_unified(f"📝 입력 계정: {args.account}")
            self._log_unified(f"🔄 변환된 계정: {converted_account}")
            self._log_unified(f"📧 실제 계정: {real_account}")
            self._log_unified(f"📊 단계: {args.steps}")
            self._log_unified(f"📦 수량: {args.quantities}")
            self._log_unified(f"⚡ 동시 실행: {args.concurrent}")
            
            print(f"\n=== 다중 단계 배치 실행 ===")
            print(f"입력 계정: {args.account}")
            print(f"변환된 계정: {converted_account}")
            print(f"실제 계정: {real_account}")
            print(f"단계: {args.steps}")
            print(f"수량: {args.quantities}")
            print(f"동시 실행: {args.concurrent}")
            print(f"통합 로그 세션: {self.unified_log_session}")
            print()
            
            start_time = time.time()
            
            result = self.batch_manager.run_multi_step(
                account=real_account,  # 실제 이메일 주소 사용
                steps=args.steps,
                quantities=args.quantities,
                concurrent=args.concurrent
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            # 결과에 통합 로그 정보 추가
            result['unified_session'] = self.unified_log_session
            result['unified_log_file'] = str(self.unified_log_file)
            
            all_results.append(result)
            
            # 통합 로그 기록
            success_count = sum(1 for r in result.get('results', {}).values() if r.get('success', False))
            total_accounts = len(result.get('results', {}))
            total_processed = sum(r.get('processed', 0) for r in result.get('results', {}).values())
            
            self._log_unified(f"✅ 다중 단계 배치 실행 완료 - 성공: {success_count}/{total_accounts}개 계정, 처리: {total_processed}개")
            
            self._print_result(result)
            
            if args.output:
                self._save_result(result, args.output)
            
            # 통합 요약 보고서 생성
            self._create_unified_summary(all_results)
            
            # 통합 로그 파일 위치 안내
            print(f"\n📁 통합 로그 파일: {self.unified_log_file}")
            print(f"📊 통합 요약 보고서: {self.unified_summary_file}")
            
        except Exception as e:
            error_msg = f"오류 발생: {e}"
            print(error_msg)
            logger.error(f"다중 단계 실행 중 오류: {e}")
            self._log_unified(f"❌ 다중 단계 배치 실행 실패: {e}", "ERROR")
        
        finally:
            self.batch_manager.cleanup()
            self._log_unified(f"🏁 배치 세션 종료: {self.unified_log_session}")
    
    def list_accounts(self, args):
        """
        계정 목록 조회
        
        Args:
            args: 명령줄 인수
        """
        try:
            accounts = self.account_manager.get_all_accounts()
            
            print("\n=== 등록된 계정 목록 ===")
            if not accounts:
                print("등록된 계정이 없습니다.")
                return
            
            for i, account in enumerate(accounts, 1):
                status = "활성" if account.get('active', True) else "비활성"
                print(f"{i:2d}. {account['id']} ({account['email']}) - {status}")
            
            print(f"\n총 {len(accounts)}개 계정")
            
        except Exception as e:
            print(f"계정 목록 조회 중 오류: {e}")
            logger.error(f"계정 목록 조회 중 오류: {e}")
    
    def show_config(self, args):
        """
        설정 정보 표시
        
        Args:
            args: 명령줄 인수
        """
        try:
            print("\n=== 현재 설정 ===")
            
            if args.format == 'yaml':
                print(json.dumps(self.batch_manager.config, indent=2, ensure_ascii=False))
            else:
                print(json.dumps(self.batch_manager.config, indent=2, ensure_ascii=False))
            
        except Exception as e:
            print(f"설정 조회 중 오류: {e}")
            logger.error(f"설정 조회 중 오류: {e}")
    
    def run_multi_batch(self, args):
        """
        다중 배치 동시 실행 (통합 로그 관리)
        
        Args:
            args: 명령줄 인수
        """
        all_results = []
        
        try:
            # 계정 ID를 올바른 형식으로 변환
            converted_accounts = []
            for account in args.accounts:
                if account.isdigit():
                    converted_accounts.append(f"account_{account}")
                else:
                    converted_accounts.append(account)
            
            # 가상 계정 ID를 실제 이메일로 변환
            real_accounts = []
            for account in converted_accounts:
                real_account = get_real_account_id(account)
                real_accounts.append(real_account)
                self._log_unified(f"🔄 계정 매핑: {account} -> {real_account}")
            
            # 통합 로그 기록
            self._log_unified(f"🚀 다중 배치 동시 실행 시작")
            self._log_unified(f"📝 대상 계정: {args.accounts} -> {converted_accounts}")
            self._log_unified(f"📧 실제 계정: {real_accounts}")
            self._log_unified(f"📊 실행 단계: {args.step}")
            self._log_unified(f"📦 수량: {args.quantity}")
            self._log_unified(f"⏱️ 실행 간격: {args.interval}초")
            
            print(f"\n=== 다중 배치 동시 실행 ===")
            print(f"입력 계정: {args.accounts}")
            print(f"변환된 계정: {converted_accounts}")
            print(f"실제 계정: {real_accounts}")
            print(f"실행 단계: {args.step}")
            print(f"수량: {args.quantity}")
            print(f"실행 간격: {args.interval}초")
            print(f"통합 로그 세션: {self.unified_log_session}")
            print()
            
            start_time = time.time()
            
            # 각 계정별로 개별 배치 실행
            for i, (converted_account, real_account) in enumerate(zip(converted_accounts, real_accounts), 1):
                self._log_unified(f"📋 계정 {i}/{len(converted_accounts)} 시작: {converted_account} ({real_account})")
                print(f"\n--- 계정 {i}/{len(converted_accounts)}: {converted_account} ({real_account}) ---")
                
                # 기존 방식으로 실행
                self._execute_single_batch(real_account, args, i, all_results, converted_account)
                
                # 배치 간 간격
                if i < len(converted_accounts) and args.interval > 0:
                    self._log_unified(f"⏱️ 다음 계정까지 {args.interval}초 대기")
                    print(f"다음 계정까지 {args.interval}초 대기...")
                    time.sleep(args.interval)
            
            end_time = time.time()
            total_duration = end_time - start_time
            
            # 전체 결과 통계
            total_success = sum(1 for r in all_results if r.get('success', False))
            total_processed = sum(
                sum(ar.get('processed', 0) for ar in r.get('results', {}).values())
                for r in all_results
            )
            
            self._log_unified(f"🎉 다중 배치 실행 완료 - 총 {len(all_results)}개 배치, 성공: {total_success}개, 처리: {total_processed}개")
            self._log_unified(f"⏱️ 총 소요 시간: {total_duration:.2f}초")
            
            # 통합 결과 출력
            self._print_multi_batch_result(all_results, total_duration)
            
            # 통합 요약 보고서 생성
            self._create_unified_summary(all_results)
            
            # 통합 로그 파일 위치 안내
            print(f"\n📁 통합 로그 파일: {self.unified_log_file}")
            print(f"📊 통합 요약 보고서: {self.unified_summary_file}")
            
            if args.output:
                # 전체 결과를 하나의 파일로 저장
                combined_result = {
                    'unified_session': self.unified_log_session,
                    'total_batches': len(all_results),
                    'total_duration': total_duration,
                    'success_count': total_success,
                    'total_processed': total_processed,
                    'individual_results': all_results
                }
                self._save_result(combined_result, args.output)
            
        except Exception as e:
            error_msg = f"다중 배치 실행 중 오류: {e}"
            print(error_msg)
            logger.error(error_msg)
            self._log_unified(f"❌ 다중 배치 실행 실패: {e}", "ERROR")
        
        finally:
            self.batch_manager.cleanup()
            self._log_unified(f"🏁 다중 배치 세션 종료: {self.unified_log_session}")
    
    def _execute_single_batch(self, real_account: str, args, batch_index: int, all_results: list, converted_account: str = None):
        """일반 단계의 단일 배치 실행"""
        try:
            result = self.batch_manager.run_single_step(
                step=args.step,
                accounts=[real_account],
                quantity=args.quantity,
                concurrent=False,  # 다중 배치에서는 개별적으로 실행
                interval=0
            )
            
            # 결과에 통합 로그 정보 추가
            result['unified_session'] = self.unified_log_session
            result['unified_log_file'] = str(self.unified_log_file)
            result['batch_index'] = batch_index
            result['account'] = converted_account or real_account
            result['real_account'] = real_account
            
            all_results.append(result)
            
            # 개별 배치 결과 로그
            account_result = result.get('results', {}).get(real_account, {})
            success = account_result.get('success', False)
            processed = account_result.get('processed', 0)
            
            status = "✅ 성공" if success else "❌ 실패"
            display_account = converted_account or real_account
            self._log_unified(f"📋 배치 {batch_index} 완료: {display_account} - {status} (처리: {processed}개)")
            
            print(f"배치 {batch_index} 결과: {status} (처리: {processed}개)")
            
        except Exception as e:
            display_account = converted_account or real_account
            error_msg = f"배치 {batch_index} 실패: {display_account} - {e}"
            self._log_unified(error_msg, "ERROR")
            print(f"❌ {error_msg}")



    
    def _print_multi_batch_result(self, all_results: List[Dict], total_duration: float):
        """다중 배치 실행 결과 출력"""
        print("\n" + "="*60)
        print("🚀 다중 배치 실행 완료 - 통합 요약 보고서")
        print("="*60)
        
        # 전체 통계
        total_batches = len(all_results)
        total_success = sum(1 for r in all_results if r.get('success', False))
        total_processed = sum(
            sum(ar.get('processed', 0) for ar in r.get('results', {}).values())
            for r in all_results
        )
        total_failed = sum(
            sum(ar.get('failed', 0) for ar in r.get('results', {}).values())
            for r in all_results
        )
        
        print(f"📋 통합 세션 ID: {self.unified_log_session}")
        print(f"⏱️  총 소요 시간: {total_duration:.2f}초")
        print(f"🎯 전체 실행 결과: {'✅ 성공' if total_success == total_batches else '⚠️ 부분 성공' if total_success > 0 else '❌ 실패'}")
        
        # 배치별 상세 결과
        print("\n" + "-"*50)
        print("📊 배치별 상세 결과")
        print("-"*50)
        
        for i, result in enumerate(all_results, 1):
            account = result.get('account', 'N/A')
            success = result.get('success', False)
            duration = result.get('duration', 0)
            
            account_result = result.get('results', {}).get(account, {})
            processed = account_result.get('processed', 0)
            failed = account_result.get('failed', 0)
            
            status_icon = "✅" if success else "❌"
            print(f"\n{status_icon} 배치 {i}: {account}")
            print(f"   소요 시간: {duration:.2f}초")
            print(f"   처리 완료: {processed}개")
            print(f"   처리 실패: {failed}개")
            
            # 상품 수량 변화 정보
            before_count = account_result.get('product_count_before', -1)
            after_count = account_result.get('product_count_after', -1)
            
            if before_count >= 0 and after_count >= 0:
                actual_processed = before_count - after_count
                print(f"   실행 전 비그룹상품: {before_count}개")
                print(f"   실행 후 비그룹상품: {after_count}개")
                print(f"   실제 처리된 수량: {actual_processed}개")
                
                if actual_processed == processed:
                    print(f"   상태: ✅ 정상 처리 (누락 없음)")
                elif actual_processed > processed:
                    print(f"   상태: ⚠️ 실제 감소량이 더 많음 (+{actual_processed - processed})")
                elif actual_processed < processed:
                    print(f"   상태: ⚠️ 실제 감소량이 더 적음 (-{processed - actual_processed})")
            
            # 오류 정보
            if account_result.get('errors'):
                print(f"   오류 내용:")
                for error in account_result['errors']:
                    print(f"     - {error}")
        
        # 전체 통계 요약
        print("\n" + "="*50)
        print("📈 전체 통계 요약")
        print("="*50)
        print(f"🏢 총 배치 수: {total_batches}개")
        print(f"✅ 성공한 배치: {total_success}개")
        print(f"❌ 실패한 배치: {total_batches - total_success}개")
        print(f"📦 총 처리 완료: {total_processed}개")
        print(f"⚠️  총 처리 실패: {total_failed}개")
        
        success_rate = (total_success / total_batches * 100) if total_batches > 0 else 0
        print(f"🎯 성공률: {success_rate:.1f}%")
        
        print("\n" + "="*60)
        print("🎉 다중 배치 실행 완료!")
        print("="*60)
    
    def run_scenario(self, args):
        """
        사전 정의된 시나리오 실행
        
        Args:
            args: 명령줄 인수
        """
        try:
            scenarios = self.batch_manager.config.get('scenarios', {})
            
            if args.scenario not in scenarios:
                print(f"시나리오 '{args.scenario}'를 찾을 수 없습니다.")
                print(f"사용 가능한 시나리오: {list(scenarios.keys())}")
                return
            
            scenario = scenarios[args.scenario]
            print(f"\n=== 시나리오 실행: {args.scenario} ===")
            print(f"설명: {scenario.get('description', '설명 없음')}")
            print()
            
            if scenario['type'] == 'single_step':
                result = self.batch_manager.run_single_step(
                    step=scenario['step'],
                    accounts=scenario['accounts'],
                    quantity=scenario['quantity'],
                    concurrent=scenario.get('concurrent', True)
                )
            elif scenario['type'] == 'multi_step':
                result = self.batch_manager.run_multi_step(
                    account=scenario['accounts'][0],  # 첫 번째 계정 사용
                    steps=scenario['steps'],
                    quantities=scenario['quantities'],
                    concurrent=scenario.get('concurrent', False)
                )
            else:
                print(f"지원하지 않는 시나리오 타입: {scenario['type']}")
                return
            
            self._print_result(result)
            
            if args.output:
                self._save_result(result, args.output)
            
        except Exception as e:
            print(f"시나리오 실행 중 오류: {e}")
            logger.error(f"시나리오 실행 중 오류: {e}")
        
        finally:
            self.batch_manager.cleanup()
    
    def list_scenarios(self, args):
        """
        사용 가능한 시나리오 목록 표시
        
        Args:
            args: 명령줄 인수
        """
        try:
            scenarios = self.batch_manager.config.get('scenarios', {})
            
            print("\n=== 사용 가능한 시나리오 ===")
            if not scenarios:
                print("정의된 시나리오가 없습니다.")
                return
            
            for name, scenario in scenarios.items():
                print(f"\n{name}:")
                print(f"  설명: {scenario.get('description', '설명 없음')}")
                print(f"  타입: {scenario.get('type', '알 수 없음')}")
                
                if scenario.get('type') == 'single_step':
                    print(f"  단계: {scenario.get('step')}")
                    print(f"  계정: {scenario.get('accounts', [])}")
                    print(f"  수량: {scenario.get('quantity')}")
                elif scenario.get('type') == 'multi_step':
                    print(f"  단계: {scenario.get('steps', [])}")
                    print(f"  계정: {scenario.get('accounts', [])}")
                    print(f"  수량: {scenario.get('quantities', [])}")
            
        except Exception as e:
            print(f"시나리오 목록 조회 중 오류: {e}")
            logger.error(f"시나리오 목록 조회 중 오류: {e}")
    
    def _print_result(self, result: Dict):
        """
        실행 결과 출력 (통합 요약 포함)
        
        Args:
            result: 실행 결과
        """
        print("\n" + "="*60)
        print("🚀 배치 실행 완료 - 통합 요약 보고서")
        print("="*60)
        
        # 기본 정보
        print(f"📋 작업 ID: {result.get('task_id', 'N/A')}")
        print(f"⏱️  소요 시간: {result.get('duration', 0):.2f}초")
        print(f"📅 실행 시간: {result.get('start_time', 'N/A')}")
        
        # 전체 성공 여부
        overall_success = result.get('success', False)
        status_icon = "✅" if overall_success else "❌"
        print(f"🎯 전체 실행 결과: {status_icon} {'성공' if overall_success else '실패'}")
        
        if 'error' in result:
            print(f"⚠️  전체 오류: {result['error']}")
        
        # 계정별 상세 결과
        results = result.get('results', {})
        if results:
            print("\n" + "-"*50)
            print("📊 계정별 상세 결과")
            print("-"*50)
            
            total_processed = 0
            total_failed = 0
            success_count = 0
            total_accounts = len(results)
            
            for account_id, account_result in results.items():
                success = account_result.get('success', False)
                processed = account_result.get('processed', 0)
                failed = account_result.get('failed', 0)
                
                # 상품 수량 변화 정보
                before_count = account_result.get('product_count_before', -1)
                after_count = account_result.get('product_count_after', -1)
                
                status_icon = "✅" if success else "❌"
                print(f"\n{status_icon} {account_id}")
                print(f"   처리 완료: {processed}개")
                print(f"   처리 실패: {failed}개")
                
                # 상품 수량 비교 (Step 1의 경우)
                if before_count >= 0 and after_count >= 0:
                    actual_processed = before_count - after_count
                    print(f"   실행 전 비그룹상품: {before_count}개")
                    print(f"   실행 후 비그룹상품: {after_count}개")
                    print(f"   실제 처리된 수량: {actual_processed}개")
                    
                    if actual_processed == processed:
                        print(f"   상태: ✅ 정상 처리 (누락 없음)")
                    elif actual_processed > processed:
                        print(f"   상태: ⚠️ 실제 감소량이 더 많음 (+{actual_processed - processed})")
                    elif actual_processed < processed:
                        print(f"   상태: ⚠️ 실제 감소량이 더 적음 (-{processed - actual_processed})")
                
                total_processed += processed
                total_failed += failed
                if success:
                    success_count += 1
                
                # 오류 정보
                if account_result.get('errors'):
                    print(f"   오류 내용:")
                    for error in account_result['errors']:
                        print(f"     - {error}")
            
            # 전체 통계 요약
            print("\n" + "="*50)
            print("📈 전체 통계 요약")
            print("="*50)
            print(f"🏢 총 계정 수: {total_accounts}개")
            print(f"✅ 성공한 계정: {success_count}개")
            print(f"❌ 실패한 계정: {total_accounts - success_count}개")
            print(f"📦 총 처리 완료: {total_processed}개")
            print(f"⚠️  총 처리 실패: {total_failed}개")
            
            success_rate = (success_count / total_accounts * 100) if total_accounts > 0 else 0
            print(f"🎯 성공률: {success_rate:.1f}%")
            
            # 로그 파일 위치 안내
            start_time = result.get('start_time', '')
            if start_time:
                print("\n" + "-"*50)
                print("📁 상세 로그 파일 위치")
                print("-"*50)
                print(f"📋 계정별 로그: logs/accounts/{start_time}/")
                print(f"⚠️  에러 로그: logs/errors/{start_time}/")
                print(f"📊 보고서: logs/reports/{start_time}/")
        
        print("\n" + "="*60)
        print("🎉 배치 실행 완료!")
        print("="*60)
    
    def _save_result(self, result: Dict, output_file: str):
        """
        결과를 파일로 저장
        
        Args:
            result: 실행 결과
            output_file: 출력 파일 경로
        """
        try:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"\n결과가 저장되었습니다: {output_file}")
            
        except Exception as e:
            print(f"결과 저장 중 오류: {e}")
            logger.error(f"결과 저장 중 오류: {e}")

def create_parser():
    """
    명령줄 파서 생성
    
    Returns:
        argparse.ArgumentParser: 파서
    """
    parser = argparse.ArgumentParser(
        description='Percenty 배치 관리자 CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  # 1단계를 여러 계정에서 동시 실행
  python batch_cli.py single --step 1 --accounts account1 account2 --quantity 100 --concurrent
  
  # 하나의 계정으로 여러 단계 순차 실행
  python batch_cli.py multi --account account1 --steps 1 2 3 --quantities 100 50 30
  
  # 사전 정의된 시나리오 실행
  python batch_cli.py scenario --name step1_multi_account
  
  # 계정 목록 조회
  python batch_cli.py accounts
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='사용 가능한 명령어')
    
    # 단일 단계 실행
    single_parser = subparsers.add_parser('single', help='단일 단계 배치 실행')
    single_parser.add_argument('--step', type=int, required=True, choices=[1, 2, 3, 4, 5, 6, 21, 22, 23, 31, 32, 33, 51, 52, 53],
                              help='실행할 단계 번호 (Step 2 하위: 21=2_1, 22=2_2, 23=2_3, Step 3 하위: 31=3_1, 32=3_2, 33=3_3, Step 5 하위: 51=5_1, 52=5_2, 53=5_3)')
    single_parser.add_argument('--accounts', nargs='+', required=True,
                              help='계정 ID 목록')
    single_parser.add_argument('--quantity', type=int, default=100,
                              help='처리할 수량 (기본값: 100)')
    single_parser.add_argument('--concurrent', action='store_true',
                              help='동시 실행 여부')
    single_parser.add_argument('--output', type=str,
                              help='결과 저장 파일 경로')
    single_parser.add_argument('--interval', type=int, default=5,
                              help='계정 간 실행 간격(초) (기본값: 5)')
    single_parser.add_argument('--chunk-size', type=int, default=20,
                              help='청크 크기 (기본값: 20, 4단계에서는 무시됨)')
    
    # 다중 단계 실행
    multi_parser = subparsers.add_parser('multi', help='다중 단계 배치 실행')
    multi_parser.add_argument('--account', type=str, required=True,
                             help='계정 ID')
    multi_parser.add_argument('--steps', nargs='+', type=int, required=True,
                             help='실행할 단계 목록')
    multi_parser.add_argument('--quantities', nargs='+', type=int, required=True,
                             help='각 단계별 수량')
    multi_parser.add_argument('--concurrent', action='store_true',
                             help='동시 실행 여부')
    multi_parser.add_argument('--output', type=str,
                             help='결과 저장 파일 경로')
    multi_parser.add_argument('--interval', type=int, default=5,
                             help='계정 간 실행 간격(초) (기본값: 5)')
    
    # 다중 배치 실행
    multi_batch_parser = subparsers.add_parser('multi-batch', help='다중 배치 동시 실행')
    multi_batch_parser.add_argument('accounts', nargs='+',
                                    help='실행할 계정 ID 목록 (예: 1 2 3 또는 account_1 account_2)')
    multi_batch_parser.add_argument('-s', '--step', type=int, default=1,
                                    help='실행할 단계 (기본값: 1, Step 5 하위: 51=5_1, 52=5_2, 53=5_3)')
    multi_batch_parser.add_argument('-q', '--quantity', type=int, default=10,
                                    help='처리할 수량 (기본값: 10)')
    multi_batch_parser.add_argument('-i', '--interval', type=int, default=5,
                                    help='배치 간 실행 간격(초) (기본값: 5)')
    multi_batch_parser.add_argument('-o', '--output',
                                    help='결과 저장 파일 경로')
    
    # 시나리오 실행
    scenario_parser = subparsers.add_parser('scenario', help='사전 정의된 시나리오 실행')
    scenario_parser.add_argument('scenario_name',
                                help='시나리오 이름')
    scenario_parser.add_argument('-o', '--output',
                                help='결과 저장 파일 경로')
    
    # 계정 목록
    subparsers.add_parser('accounts', help='등록된 계정 목록 조회')
    
    # 시나리오 목록
    subparsers.add_parser('scenarios', help='사용 가능한 시나리오 목록 조회')
    
    # 설정 조회
    config_parser = subparsers.add_parser('config', help='현재 설정 조회')
    config_parser.add_argument('--format', choices=['json', 'yaml'], default='yaml',
                              help='출력 형식 (기본값: yaml)')
    
    return parser

def main():
    """
    메인 함수
    """
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = BatchCLI()
    
    try:
        if args.command == 'single':
            cli.run_single_step(args)
        elif args.command == 'multi':
            cli.run_multi_step(args)
        elif args.command == 'multi-batch':
            cli.run_multi_batch(args)
        elif args.command == 'scenario':
            cli.run_scenario(args)
        elif args.command == 'accounts':
            cli.list_accounts(args)
        elif args.command == 'scenarios':
            cli.list_scenarios(args)
        elif args.command == 'config':
            cli.show_config(args)
        else:
            print(f"알 수 없는 명령어: {args.command}")
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\n\n사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n예상치 못한 오류가 발생했습니다: {e}")
        logger.error(f"CLI 실행 중 오류: {e}")

if __name__ == "__main__":
    main()