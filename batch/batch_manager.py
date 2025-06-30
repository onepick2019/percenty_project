#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
통합 배치 관리자
다중 계정, 다중 단계 배치 작업을 관리하는 핵심 모듈
"""

import os
import sys
import time
import logging
import threading
import json
import math
from typing import Dict, List, Optional, Union, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
import pandas as pd

# 루트 디렉토리를 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 코어 모듈들 임포트
from core.steps.step1_core import Step1Core
from core.steps.step5_1_core import Step5_1Core
from core.steps.step5_2_core import Step5_2Core
from core.steps.step5_3_core import Step5_3Core
from core.browser.browser_manager import CoreBrowserManager
from core.account.account_manager import CoreAccountManager
from product_editor_screen import open_product_editor_screen

# 기존 모듈들 임포트 (호환성)
from timesleep import DELAY_STANDARD, DELAY_SHORT
from human_delay import HumanLikeDelay

logger = logging.getLogger(__name__)

# 계정 매핑 캐시
_account_mapping_cache = None
_account_mapping_cache_time = None
_cache_lock = threading.Lock()

def load_account_mapping_from_excel(excel_path: str = "percenty_id.xlsx") -> Dict[str, str]:
    """
    Excel 파일에서 계정 매핑 정보를 로드
    
    Args:
        excel_path: Excel 파일 경로
        
    Returns:
        Dict[str, str]: 가상 ID -> 실제 이메일 매핑
    """
    global _account_mapping_cache, _account_mapping_cache_time
    
    with _cache_lock:
        # 캐시가 있고 5분 이내라면 캐시 사용
        if (_account_mapping_cache is not None and 
            _account_mapping_cache_time is not None and 
            (datetime.now() - _account_mapping_cache_time).seconds < 300):
            return _account_mapping_cache.copy()
        
        try:
            # Excel 파일에서 login_id 시트 읽기
            if not os.path.exists(excel_path):
                logger.warning(f"Excel 파일을 찾을 수 없습니다: {excel_path}")
                return {}
            
            df = pd.read_excel(excel_path, sheet_name='login_id')
            
            # A열(첫 번째 컬럼)이 이메일 주소라고 가정
            mapping = {}
            for index, row in df.iterrows():
                if len(row) > 0 and not pd.isna(row.iloc[0]):
                    email = str(row.iloc[0]).strip()
                    if email and '@' in email:  # 유효한 이메일인지 간단 체크
                        virtual_id = f"account_{index + 1}"
                        mapping[virtual_id] = email
            
            # 캐시 업데이트
            _account_mapping_cache = mapping
            _account_mapping_cache_time = datetime.now()
            
            logger.info(f"Excel에서 계정 매핑 로드 완료: {len(mapping)}개 계정")
            return mapping.copy()
            
        except Exception as e:
            logger.error(f"Excel에서 계정 매핑 로드 실패: {e}")
            # 기본 매핑 반환 (하위 호환성)
            default_mapping = {
                'account_1': 'onepick2019@gmail.com',
                'account_2': 'wop31garam@gmail.com', 
                'account_3': 'wop32gsung@gmail.com',
                'account_4': 'wop33gogos@gmail.com',
                'account_5': 'wop34goyos@gmail.com',
                'account_6': 'wop35goens@gmail.com',
                'account_7': 'wop36gurum@gmail.com'
            }
            return default_mapping

def get_real_account_id(virtual_id: str) -> str:
    """
    가상 계정 ID를 실제 이메일로 변환
    
    Args:
        virtual_id: 가상 계정 ID (예: account_1)
        
    Returns:
        str: 실제 이메일 주소
    """
    mapping = load_account_mapping_from_excel()
    return mapping.get(virtual_id, virtual_id)

class AccountLogger:
    """계정별 로거 관리 클래스"""
    
    def __init__(self, account_id: str, start_time: str, log_dir: str = "logs"):
        self.account_id = account_id
        self.start_time = start_time
        self.log_dir = Path(log_dir)
        self.account_log_dir = self.log_dir / "accounts" / start_time
        self.error_log_dir = self.log_dir / "errors" / start_time
        
        # 디렉토리 생성
        self.account_log_dir.mkdir(parents=True, exist_ok=True)
        self.error_log_dir.mkdir(parents=True, exist_ok=True)
        
        # 로거 설정
        self.logger = logging.getLogger(f"account_{account_id}_{start_time}")
        self.logger.setLevel(logging.INFO)
        
        # 기존 핸들러 제거
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # 계정별 로그 파일 핸들러
        account_log_file = self.account_log_dir / f"{account_id}.log"
        account_handler = logging.FileHandler(account_log_file, encoding='utf-8')
        account_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        account_handler.setFormatter(account_formatter)
        self.logger.addHandler(account_handler)
        
        # 에러 전용 로그 파일 핸들러
        error_log_file = self.error_log_dir / f"{account_id}_errors.log"
        error_handler = logging.FileHandler(error_log_file, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_formatter = logging.Formatter(
            '%(asctime)s - ERROR - %(message)s'
        )
        error_handler.setFormatter(error_formatter)
        self.logger.addHandler(error_handler)
        
        # 전파 방지 (중복 로그 방지)
        self.logger.propagate = False
    
    def info(self, message: str):
        """정보 로그"""
        self.logger.info(f"[{self.account_id}] {message}")
    
    def error(self, message: str):
        """에러 로그"""
        self.logger.error(f"[{self.account_id}] {message}")
    
    def warning(self, message: str):
        """경고 로그"""
        self.logger.warning(f"[{self.account_id}] {message}")
    
    def debug(self, message: str):
        """디버그 로그"""
        self.logger.debug(f"[{self.account_id}] {message}")

class BatchReportGenerator:
    """배치 결과 보고서 생성 클래스"""
    
    def __init__(self, start_time: str, log_dir: str = "logs"):
        self.start_time = start_time
        self.log_dir = Path(log_dir)
        self.report_dir = self.log_dir / "reports" / start_time
        self.report_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_batch_report(self, task_id: str, results: Dict) -> str:
        """배치 실행 결과 보고서 생성"""
        report_file = self.report_dir / f"batch_report_{task_id}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"# 배치 실행 보고서\n\n")
            f.write(f"**작업 ID:** {task_id}\n")
            f.write(f"**시작 시간:** {self.start_time}\n")
            f.write(f"**실행 시간:** {results.get('start_time', 'N/A')}\n")
            f.write(f"**완료 시간:** {results.get('end_time', 'N/A')}\n")
            f.write(f"**소요 시간:** {results.get('duration', 0):.2f}초\n")
            f.write(f"**전체 성공 여부:** {'✅ 성공' if results.get('success', False) else '❌ 실패'}\n\n")
            
            # 계정별 결과
            f.write("## 계정별 실행 결과\n\n")
            account_results = results.get('results', {})
            
            total_processed = 0
            total_failed = 0
            success_count = 0
            
            for account_id, result in account_results.items():
                processed = result.get('processed', 0)
                failed = result.get('failed', 0)
                success = result.get('success', False)
                errors = result.get('errors', [])
                product_count_before = result.get('product_count_before', -1)
                product_count_after = result.get('product_count_after', -1)
                
                total_processed += processed
                total_failed += failed
                if success:
                    success_count += 1
                
                status_icon = "✅" if success else "❌"
                f.write(f"### {status_icon} {account_id}\n")
                f.write(f"- **처리 완료:** {processed}개\n")
                f.write(f"- **처리 실패:** {failed}개\n")
                f.write(f"- **성공 여부:** {'성공' if success else '실패'}\n")
                
                # 상품 수 비교 정보 추가
                if product_count_before >= 0 and product_count_after >= 0:
                    processed_difference = product_count_before - product_count_after
                    f.write(f"- **실행 전 비그룹상품 수량:** {product_count_before}개\n")
                    f.write(f"- **실행 후 비그룹상품 수량:** {product_count_after}개\n")
                    f.write(f"- **처리된 상품 수량:** {processed_difference}개\n")
                    
                    # 처리 수량과 실제 감소량 비교
                    if processed_difference == processed:
                        f.write(f"- **상태:** ✅ 누락 없이 정상 처리 (처리량과 감소량 일치)\n")
                    elif processed_difference > processed:
                        f.write(f"- **상태:** ⚠️ 실제 감소량({processed_difference}개)이 처리 수량({processed}개)보다 많음\n")
                    elif processed_difference < processed:
                        f.write(f"- **상태:** ⚠️ 실제 감소량({processed_difference}개)이 처리 수량({processed}개)보다 적음\n")
                
                if errors:
                    f.write(f"- **오류 내용:**\n")
                    for error in errors:
                        f.write(f"  - {error}\n")
                f.write("\n")
            
            # 전체 요약
            f.write("## 전체 요약\n\n")
            f.write(f"- **총 계정 수:** {len(account_results)}개\n")
            f.write(f"- **성공한 계정:** {success_count}개\n")
            f.write(f"- **실패한 계정:** {len(account_results) - success_count}개\n")
            f.write(f"- **총 처리 완료:** {total_processed}개\n")
            f.write(f"- **총 처리 실패:** {total_failed}개\n")
            f.write(f"- **성공률:** {(success_count / len(account_results) * 100):.1f}%\n\n")
            
            # 로그 파일 위치
            f.write("## 상세 로그 파일\n\n")
            f.write(f"- **계정별 로그:** `logs/accounts/{self.start_time}/`\n")
            f.write(f"- **에러 로그:** `logs/errors/{self.start_time}/`\n")
            f.write(f"- **보고서:** `logs/reports/{self.start_time}/`\n")
        
        return str(report_file)
    
    def generate_summary_report(self, all_results: List[Dict]) -> str:
        """여러 배치 작업의 종합 보고서 생성"""
        summary_file = self.report_dir / f"summary_report_{self.start_time}.md"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"# 배치 작업 종합 보고서\n\n")
            f.write(f"**보고서 생성 시간:** {self.start_time}\n")
            f.write(f"**총 배치 작업 수:** {len(all_results)}개\n\n")
            
            total_accounts = 0
            total_success_accounts = 0
            total_processed_items = 0
            
            for i, result in enumerate(all_results, 1):
                f.write(f"## 배치 작업 {i}\n")
                f.write(f"- **작업 ID:** {result.get('task_id', 'N/A')}\n")
                f.write(f"- **소요 시간:** {result.get('duration', 0):.2f}초\n")
                
                account_results = result.get('results', {})
                success_count = sum(1 for r in account_results.values() if r.get('success', False))
                processed_count = sum(r.get('processed', 0) for r in account_results.values())
                
                total_accounts += len(account_results)
                total_success_accounts += success_count
                total_processed_items += processed_count
                
                f.write(f"- **계정 수:** {len(account_results)}개\n")
                f.write(f"- **성공 계정:** {success_count}개\n")
                f.write(f"- **처리 항목:** {processed_count}개\n\n")
            
            f.write("## 전체 통계\n\n")
            f.write(f"- **총 처리 계정:** {total_accounts}개\n")
            f.write(f"- **총 성공 계정:** {total_success_accounts}개\n")
            f.write(f"- **총 처리 항목:** {total_processed_items}개\n")
            if total_accounts > 0:
                f.write(f"- **전체 성공률:** {(total_success_accounts / total_accounts * 100):.1f}%\n")
        
        return str(summary_file)

class BatchManager:
    """
    통합 배치 관리자
    
    주요 기능:
    - 다중 계정 동시 실행
    - 다중 단계 순차/병렬 실행
    - 설정 기반 배치 작업
    - 진행상황 모니터링
    - 스케줄링 지원
    """
    
    def __init__(self, config_file: str = None):
        """
        초기화
        
        Args:
            config_file: 설정 파일 경로
        """
        self.config_file = config_file or "batch/config/batch_config.json"
        self.config = {}
        
        # 시작 시간 설정 (파일명 구분용)
        self.start_time = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 설정 먼저 로드
        self.load_config()
        
        # 관리자들 (설정 로드 후 초기화)
        self.account_manager = CoreAccountManager()
        # 설정에서 헤드리스 모드 확인 (기본값: True - 안정성을 위해)
        browser_headless = self.config.get('browser', {}).get('headless', True)
        self.browser_manager = CoreBrowserManager(headless=browser_headless)
        
        # 브라우저 생성 락 (동시 생성 방지)
        self.browser_creation_lock = threading.Lock()
        
        # 실행 상태
        self.running_tasks = {}
        self.task_results = {}
        self.is_running = False
        
        # 스레드 풀
        self.executor = None
        self.max_workers = 4
        
        # 지연 관리
        self.delay = HumanLikeDelay()
        
        # 계정별 로거 관리
        self.account_loggers = {}
        
        # 보고서 생성기
        self.report_generator = BatchReportGenerator(self.start_time)
        
        # 배치 결과 저장 (보고서용)
        self.batch_results = []
    
    def load_config(self):
        """
        설정 파일 로드
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                    logger.info(f"설정 파일 로드 완료: {self.config_file}")
            else:
                # 기본 설정 생성
                self.config = self._create_default_config()
                self.save_config()
                logger.info("기본 설정 파일 생성")
        except Exception as e:
            logger.error(f"설정 파일 로드 중 오류: {e}")
            self.config = self._create_default_config()
    
    def _create_default_config(self) -> Dict:
        """
        기본 설정 생성
        
        Returns:
            Dict: 기본 설정
        """
        return {
            'batch': {
                'max_workers': 4,
                'default_quantity': 100,
                'retry_count': 3,
                'delay_between_tasks': 1.0
            },
            'browser': {
                'headless': False,
                'window_size': [1920, 1080],
                'timeout': 30
            },
            'logging': {
                'level': 'INFO',
                'file': 'logs/batch_manager.log'
            }
        }
    
    def save_config(self):
        """
        설정 파일 저장
        """
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logger.info(f"설정 파일 저장 완료: {self.config_file}")
        except Exception as e:
            logger.error(f"설정 파일 저장 중 오류: {e}")
    
    def execute_single_step(self, account_id: str, step: str, quantity: int) -> bool:
        """
        단일 계정, 단일 단계 실행 (GUI 호환용)
        
        Args:
            account_id: 계정 ID
            step: 단계 (예: 'step1')
            quantity: 수량
            
        Returns:
            bool: 실행 성공 여부
        """
        import traceback
        import time
        
        try:
            logger.info(f"=== execute_single_step 시작: account_id={account_id}, step={step}, quantity={quantity} ===")
            logger.info(f"브라우저 매니저 상태: {type(self.browser_manager)}")
            logger.info(f"계정 매니저 상태: {type(self.account_manager)}")
            logger.info(f"설정 상태: {type(self.config)}")
            
            # step을 숫자로 변환 (문자열 또는 숫자 모두 처리)
            if isinstance(step, str):
                # "step" 제거 후 "_"를 ""로 변환 (예: "2_1" -> "21")
                step_str = step.replace('step', '').replace('_', '')
                step_num = int(step_str)
            else:
                step_num = int(step)
            
            # 작은 지연으로 UI 응답성 확보
            time.sleep(0.05)
            
            # 단일 계정으로 배치 실행
            logger.info(f"run_single_step 호출 전: step_num={step_num}, accounts=[{account_id}], quantity={quantity}, concurrent=False")
            logger.info(f"현재 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            result = self.run_single_step(step_num, [account_id], quantity, concurrent=False)
            
            logger.info(f"run_single_step 호출 후: 결과={result}")
            logger.info(f"완료 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            success = result.get('success', False)
            logger.info(f"=== execute_single_step 완료: 성공={success} ===")
            return success
            
        except Exception as e:
            logger.error(f"=== execute_single_step 중 오류 발생 ===")
            logger.error(f"오류 메시지: {e}")
            logger.error(f"오류 상세: {traceback.format_exc()}")
            logger.error(f"=== execute_single_step 실패 ===")
            return False
    
    def run_single_step(self, step: int, accounts: List[str], quantity: int,
                        concurrent: bool = True, interval: int = None, chunk_size: int = 20) -> Dict:
        """
        단일 단계 배치 실행
        
        Args:
            step: 실행할 단계 번호
            accounts: 계정 ID 목록
            quantity: 각 계정당 처리할 수량
            concurrent: 동시 실행 여부
            interval: 계정 간 실행 간격(초)
            
        Returns:
            Dict: 실행 결과
        """
        import time
        task_id = f"single_step_{step}_{self.start_time}"
        
        logger.info(f"단일 단계 배치 시작 - 단계: {step}, 계정: {len(accounts)}개, 수량: {quantity}")
        logger.info(f"시작 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"로그 파일 구분자: {self.start_time}")
        if interval is not None:
            logger.info(f"계정 간 실행 간격: {interval}초")
        
        # 계정별 로거 초기화
        for account_id in accounts:
            if account_id not in self.account_loggers:
                self.account_loggers[account_id] = AccountLogger(account_id, self.start_time)
        
        try:
            if concurrent and len(accounts) > 1:
                logger.info("동시 실행 모드로 단일 단계 실행")
                result = self._run_concurrent_single_step(task_id, step, accounts, quantity, chunk_size)
            else:
                logger.info("순차 실행 모드로 단일 단계 실행 시작")
                logger.info(f"_run_sequential_single_step 호출 전 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                result = self._run_sequential_single_step(task_id, step, accounts, quantity, interval, chunk_size)
                logger.info(f"_run_sequential_single_step 호출 후 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 배치 결과 저장
            self.batch_results.append(result)
            
            # 상세 실행 결과 로그 출력
            self._log_detailed_results(result)
            
            # 보고서 생성
            try:
                logger.info(f"보고서 생성 시작 - task_id: {task_id}")
                logger.info(f"보고서 생성기 상태: {self.report_generator}")
                logger.info(f"보고서 디렉토리: {self.report_generator.report_dir}")
                logger.info(f"보고서 생성에 전달되는 result 데이터: {result}")
                logger.info(f"result 타입: {type(result)}")
                logger.info(f"result.get('results'): {result.get('results', {})}")
                report_file = self.report_generator.generate_batch_report(task_id, result)
                logger.info(f"배치 보고서 생성 완료: {report_file}")
            except Exception as report_error:
                logger.error(f"보고서 생성 중 오류: {report_error}")
                logger.error(f"보고서 생성 오류 상세: {str(report_error)}")
                import traceback
                logger.error(f"보고서 생성 오류 트레이스백: {traceback.format_exc()}")
            
            return result
        
        except Exception as e:
            logger.error(f"단일 단계 배치 실행 중 오류: {e}")
            error_result = {
                'task_id': task_id,
                'success': False,
                'error': str(e),
                'results': {},
                'start_time': datetime.now(),
                'end_time': datetime.now(),
                'duration': 0
            }
            
            # 에러 결과도 저장
            self.batch_results.append(error_result)
            
            return error_result
    
    def _log_detailed_results(self, result: Dict):
        """상세 실행 결과를 로그로 출력"""
        logger = logging.getLogger(__name__)
        
        logger.info("")
        logger.info("📊 === 배치 실행 결과 상세 정보 ===")
        
        account_results = result.get('results', {})
        total_before = 0
        total_after = 0
        total_processed = 0
        
        for account_id, account_result in account_results.items():
            product_count_before = account_result.get('product_count_before', -1)
            product_count_after = account_result.get('product_count_after', -1)
            processed = account_result.get('processed', 0)
            success = account_result.get('success', False)
            
            logger.info(f"")
            logger.info(f"📋 계정 {account_id} 결과:")
            
            if product_count_before >= 0 and product_count_after >= 0:
                processed_difference = product_count_before - product_count_after
                
                logger.info(f"   • 실행 전 비그룹상품 수량: {product_count_before}개")
                logger.info(f"   • 실행 후 비그룹상품 수량: {product_count_after}개")
                logger.info(f"   • 요청 처리 수량: {processed}개")
                logger.info(f"   • 실제 처리된 수량: {processed_difference}개")
                logger.info(f"   • 상품 수 변화: {product_count_before}개 → {product_count_after}개")
                
                # 처리 결과 분석
                if processed_difference == processed:
                    logger.info(f"   • ✅ 상태: 누락 없이 정상 처리 (처리량과 감소량 일치)")
                elif processed_difference > processed:
                    logger.info(f"   • ⚠️ 상태: 실제 감소량({processed_difference}개)이 처리량({processed}개)보다 많음")
                elif processed_difference < processed:
                    logger.info(f"   • ⚠️ 상태: 실제 감소량({processed_difference}개)이 처리량({processed}개)보다 적음")
                
                total_before += product_count_before
                total_after += product_count_after
                total_processed += processed
            else:
                logger.info(f"   • ⚠️ 상품 수량 정보를 확인할 수 없습니다")
            
            logger.info(f"   • 성공 여부: {'✅ 성공' if success else '❌ 실패'}")
        
        # 전체 요약
        if len(account_results) > 1 and total_before > 0:
            logger.info(f"")
            logger.info(f"📈 전체 요약:")
            logger.info(f"   • 총 실행 전 비그룹상품: {total_before}개")
            logger.info(f"   • 총 실행 후 비그룹상품: {total_after}개")
            logger.info(f"   • 총 요청 처리 수량: {total_processed}개")
            
            total_actual_decrease = total_before - total_after
            logger.info(f"   • 총 실제 처리된 수량: {total_actual_decrease}개")
            
            if total_actual_decrease == total_processed:
                logger.info(f"   • ✅ 전체 상태: 누락 없이 정상 처리")
            elif total_actual_decrease > total_processed:
                logger.info(f"   • ⚠️ 전체 상태: 실제 감소량이 처리량보다 많음")
            elif total_actual_decrease < total_processed:
                logger.info(f"   • ⚠️ 전체 상태: 실제 감소량이 처리량보다 적음")
        
        logger.info("📊 === 배치 실행 결과 상세 정보 완료 ===")
        logger.info("")
    
    def _run_concurrent_single_step(self, task_id: str, step: int,
                                     accounts: List[str], quantity: int, chunk_size: int = 20) -> Dict:
        """
        동시 실행 단일 단계
        
        Args:
            task_id: 작업 ID
            step: 단계 번호
            accounts: 계정 목록
            quantity: 수량
            
        Returns:
            Dict: 실행 결과
        """
        results = {
            'task_id': task_id,
            'success': True,
            'start_time': datetime.now(),
            'results': {}
        }
        
        self.executor = ThreadPoolExecutor(max_workers=min(len(accounts), self.max_workers))
        
        try:
            # 각 계정에 대해 스레드 실행
            future_to_account = {}
            
            for account_id in accounts:
                future = self.executor.submit(
                    self._execute_step_for_account, 
                    step, account_id, quantity, chunk_size
                )
                future_to_account[future] = account_id
            
            # 결과 수집
            for future in as_completed(future_to_account):
                account_id = future_to_account[future]
                try:
                    result = future.result()
                    results['results'][account_id] = result
                    
                    if not result['success']:
                        results['success'] = False
                    
                    logger.info(f"계정 '{account_id}' 작업 완료: {result['processed']}개 처리")
                    
                except Exception as e:
                    logger.error(f"계정 '{account_id}' 작업 중 오류: {e}")
                results['results'][account_id] = {
                    'success': False,
                    'error': str(e),
                    'processed': 0
                }
                results['success'] = False
        
        finally:
            self.executor.shutdown(wait=True)
            self.executor = None
        
        results['end_time'] = datetime.now()
        results['duration'] = (results['end_time'] - results['start_time']).total_seconds()
        
        logger.info(f"동시 실행 완료 - 작업 ID: {task_id}, 소요시간: {results['duration']:.2f}초")
        
        return results
    
    def _run_sequential_single_step(self, task_id: str, step: int,
                                   accounts: List[str], quantity: int, interval: int = None, chunk_size: int = 20) -> Dict:
        """
        순차 실행 단일 단계
        
        Args:
            task_id: 작업 ID
            step: 단계 번호
            accounts: 계정 목록
            quantity: 수량
            interval: 계정 간 실행 간격(초)
            
        Returns:
            Dict: 실행 결과
        """
        import traceback
        import time
        
        logger.info(f"=== _run_sequential_single_step 시작: task_id={task_id}, step={step}, accounts={accounts}, quantity={quantity} ===")
        logger.info(f"순차 실행 시작 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        results = {
            'task_id': task_id,
            'success': True,
            'start_time': datetime.now(),
            'results': {}
        }
        
        logger.info(f"결과 딕셔너리 초기화 완료: {results}")
        
        try:
            logger.info(f"계정 목록 순회 시작: {len(accounts)}개 계정")
            
            for i, account_id in enumerate(accounts):
                logger.info(f"=== 계정 {i+1}/{len(accounts)} 처리 시작: '{account_id}' ===")
                logger.info(f"계정 {account_id} 처리 시작 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                
                logger.info(f"_execute_step_for_account 호출 전: step={step}, account_id={account_id}, quantity={quantity}, chunk_size={chunk_size}")
                result = self._execute_step_for_account(step, account_id, quantity, chunk_size)
                logger.info(f"_execute_step_for_account 호출 후: result={result}")
                
                results['results'][account_id] = result
                logger.info(f"결과 저장 완료: account_id={account_id}")
                
                if not result['success']:
                    results['success'] = False
                
                logger.info(f"계정 '{account_id}' 작업 완료: {result['processed']}개 처리")
                logger.info(f"계정 {account_id} 처리 완료 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # 계정 간 지연
                if account_id != accounts[-1]:  # 마지막 계정이 아니면
                    if interval is not None:
                        delay_time = interval
                        logger.info(f"사용자 설정 실행 간격 적용: {delay_time}초")
                    else:
                        delay_time = self.config.get('batch', {}).get('delay_between_tasks', 1.0)
                        logger.info(f"기본 설정 간격 적용: {delay_time}초")
                    time.sleep(delay_time)
        
        except Exception as e:
            logger.error(f"순차 실행 중 오류: {e}")
            logger.error(f"오류 발생 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            results['success'] = False
            results['error'] = str(e)
        
        results['end_time'] = datetime.now()
        results['duration'] = (results['end_time'] - results['start_time']).total_seconds()
        
        logger.info(f"순차 실행 완료 - 작업 ID: {task_id}, 소요시간: {results['duration']:.2f}초")
        logger.info(f"순차 실행 완료 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return results
    
    def _execute_step_for_account(self, step: int, account_id: str, quantity: int, chunk_size: int = 20) -> Dict:
        """
        특정 계정에 대해 단계 실행
        
        Args:
            step: 단계 번호
            account_id: 계정 ID
            quantity: 수량
            
        Returns:
            Dict: 실행 결과
        """
        import traceback
        import time
        
        # 계정별 로거 사용
        account_logger = self.account_loggers.get(account_id)
        if not account_logger:
            account_logger = AccountLogger(account_id, self.start_time)
            self.account_loggers[account_id] = account_logger
        
        account_logger.info(f"=== {step}단계 실행 시작: 수량={quantity} ===")
        
        result = {
            'success': False,
            'processed': 0,
            'failed': 0,
            'errors': []
        }
        
        account_logger.info(f"결과 딕셔너리 초기화: {result}")
        
        browser_id = None
        
        try:
            account_logger.info(f"=== {step}단계 실행 시작 ===")
            
            # 브라우저 생성 전 상태 확인
            account_logger.info(f"브라우저 매니저 상태: {type(self.browser_manager)}")
            account_logger.info(f"설정 정보: headless={self.config.get('browser', {}).get('headless', False)}")
            time.sleep(0.05)  # UI 응답성을 위한 지연
            
            # 브라우저 생성 (락 사용하여 동시 생성 방지)
            account_logger.info(f"브라우저 생성 시작: {account_id}_browser")
            account_logger.info(f"브라우저 생성 시작 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            with self.browser_creation_lock:
                account_logger.info(f"브라우저 생성 락 획득 완료")
                time.sleep(2.5)  # 브라우저 생성 전 지연 (안정성을 위해 2.5초로 증가)
                
                try:
                    account_logger.info(f"browser_manager.create_browser 호출 직전")
                    account_logger.info(f"browser_manager 타입: {type(self.browser_manager)}")
                    account_logger.info(f"browser_manager 메서드 확인: {hasattr(self.browser_manager, 'create_browser')}")
                    account_logger.info(f"호출 파라미터: browser_id={account_id}_browser, headless={self.config.get('browser', {}).get('headless', False)}")
                    
                    browser_id = self.browser_manager.create_browser(
                        browser_id=f"{account_id}_browser",
                        headless=self.config.get('browser', {}).get('headless', False)
                    )
                    account_logger.info(f"create_browser 호출 완료, 반환값: {browser_id}")
                    account_logger.info(f"브라우저 생성 완료 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                except Exception as browser_create_error:
                    account_logger.error(f"브라우저 생성 중 예외 발생: {browser_create_error}")
                    account_logger.error(f"브라우저 생성 예외 상세: {traceback.format_exc()}")
                    account_logger.error(f"브라우저 생성 실패 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                    raise
                
                account_logger.info(f"브라우저 생성 락 해제")
            
            if not browser_id:
                raise Exception(f"브라우저 생성 실패: {account_id}_browser (반환값이 None 또는 False)")
            
            account_logger.info(f"브라우저 생성 성공: {browser_id}")
            time.sleep(0.05)  # UI 응답성을 위한 지연
            
            # 브라우저 상태 확인
            try:
                driver = self.browser_manager.get_driver(browser_id)
                account_logger.info(f"드라이버 획득 성공: {type(driver)}")
            except Exception as driver_error:
                account_logger.warning(f"드라이버 획득 실패: {driver_error}")
            
            time.sleep(0.05)  # UI 응답성을 위한 지연
            
            # 로그인
            account_logger.info(f"로그인 시도")
            try:
                real_account_id = get_real_account_id(account_id)
                email, password = self.account_manager.get_account_credentials(real_account_id)
                account_logger.info(f"계정 정보 획득: {email} (원본 ID: {account_id}, 실제 ID: {real_account_id})")
                
                login_success = self.browser_manager.login_browser(browser_id, email, password)
                account_logger.info(f"로그인 시도 완료, 결과: {login_success}")
            except Exception as login_error:
                account_logger.error(f"로그인 중 예외 발생: {login_error}")
                account_logger.error(f"로그인 예외 상세: {traceback.format_exc()}")
                raise
            
            if not login_success:
                raise Exception("로그인 실패")
            
            account_logger.info(f"로그인 성공")
            time.sleep(0.05)  # UI 응답성을 위한 지연
            
            # 단계별 실행
            if step == 1:
                account_logger.info(f"1단계 실행 시작 - 수량: {quantity}")
                try:
                    driver = self.browser_manager.get_driver(browser_id)
                    step_core = Step1Core(driver)
                    account_logger.info(f"Step1Core 인스턴스 생성 완료")
                    
                    # 청크 사이즈가 설정되어 있으면 브라우저 재시작 방식 사용
                    if chunk_size and chunk_size > 0:
                        account_logger.info(f"브라우저 재시작 방식으로 1단계 실행 (수량: {quantity}, 청크 크기: {chunk_size})")
                        step_result = self._execute_step1_with_browser_restart(account_id, browser_id, quantity, chunk_size)
                    else:
                        account_logger.info(f"기존 방식으로 1단계 실행 (수량: {quantity})")
                        step_result = step_core.execute_step1(quantity)
                    
                    account_logger.info(f"Step1Core 실행 완료, 결과: {step_result}")
                    
                    result.update(step_result)
                    # step_result에서 success 값을 명시적으로 설정
                    if 'success' in step_result:
                        result['success'] = step_result['success']
                    account_logger.info(f"1단계 실행 완료 - 처리: {result.get('processed', 0)}, 실패: {result.get('failed', 0)}, 성공: {result.get('success', False)}")
                except Exception as step_error:
                    account_logger.error(f"Step1Core 실행 중 예외 발생: {step_error}")
                    account_logger.error(f"Step1Core 예외 상세: {traceback.format_exc()}")
                    raise
                    
            elif step == 51:
                account_logger.info(f"51단계 실행 시작 - 수량: {quantity}")
                try:
                    account_logger.info(f"브라우저 드라이버 가져오기 시작: {browser_id}")
                    driver = self.browser_manager.get_driver(browser_id)
                    account_logger.info(f"브라우저 드라이버 가져오기 완료: {type(driver)}")
                    
                    account_logger.info(f"Step5_1Core 인스턴스 생성 시작")
                    step_core = Step5_1Core(driver)
                    account_logger.info(f"Step5_1Core 인스턴스 생성 완료")
                    
                    # 계정 정보 가져오기 (가상 ID를 실제 이메일로 변환)
                    real_account_id = get_real_account_id(account_id)
                    account_info = self.account_manager.get_account(real_account_id)
                    account_logger.info(f"계정 정보 획득: {account_info.get('id', 'N/A')} (원본 ID: {account_id}, 실제 ID: {real_account_id})")
                    
                    # 청크 사이즈가 설정되어 있으면 브라우저 재시작 방식 사용
                    if chunk_size and chunk_size > 0:
                        account_logger.info(f"브라우저 재시작 방식으로 51단계 실행 (수량: {quantity}, 청크 크기: {chunk_size})")
                        step_result = self._execute_step5_1_with_browser_restart(account_id, browser_id, quantity, account_info, chunk_size)
                    else:
                        account_logger.info(f"기존 방식으로 51단계 실행 (수량: {quantity})")
                        step_result = step_core.execute_step5_1(quantity, account_info)
                    
                    account_logger.info(f"Step5_1Core 실행 완료, 결과: {step_result}")
                    
                    result.update(step_result)
                    if 'success' in step_result:
                        result['success'] = step_result['success']
                    account_logger.info(f"51단계 실행 완료 - 처리: {result.get('processed', 0)}, 실패: {result.get('failed', 0)}, 성공: {result.get('success', False)}")
                except Exception as step_error:
                    account_logger.error(f"Step5_1Core 실행 중 예외 발생: {step_error}")
                    account_logger.error(f"Step5_1Core 예외 상세: {traceback.format_exc()}")
                    raise
                    
            elif step == 52:
                account_logger.info(f"52단계 실행 시작 - 수량: {quantity}")
                try:
                    driver = self.browser_manager.get_driver(browser_id)
                    step_core = Step5_2Core(driver)
                    account_logger.info(f"Step5_2Core 인스턴스 생성 완료")
                    
                    # 계정 정보 가져오기 (가상 ID를 실제 이메일로 변환)
                    real_account_id = get_real_account_id(account_id)
                    account_info = self.account_manager.get_account(real_account_id)
                    account_logger.info(f"계정 정보 획득: {account_info.get('id', 'N/A')} (원본 ID: {account_id}, 실제 ID: {real_account_id})")
                    
                    # 청크 사이즈가 설정되어 있으면 브라우저 재시작 방식 사용
                    if chunk_size and chunk_size > 0:
                        account_logger.info(f"브라우저 재시작 방식으로 52단계 실행 (수량: {quantity}, 청크 크기: {chunk_size})")
                        step_result = self._execute_step5_2_with_browser_restart(account_id, browser_id, quantity, chunk_size, account_info)
                    else:
                        account_logger.info(f"기존 방식으로 52단계 실행 (수량: {quantity})")
                        step_result = step_core.execute_step5_2(quantity, account_info)
                    
                    account_logger.info(f"Step5_2Core 실행 완료, 결과: {step_result}")
                    
                    result.update(step_result)
                    if 'success' in step_result:
                        result['success'] = step_result['success']
                    account_logger.info(f"52단계 실행 완료 - 처리: {result.get('processed', 0)}, 실패: {result.get('failed', 0)}, 성공: {result.get('success', False)}")
                except Exception as step_error:
                    account_logger.error(f"Step5_2Core 실행 중 예외 발생: {step_error}")
                    account_logger.error(f"Step5_2Core 예외 상세: {traceback.format_exc()}")
                    raise
                    
            elif step == 53:
                account_logger.info(f"53단계 실행 시작 - 수량: {quantity}")
                try:
                    driver = self.browser_manager.get_driver(browser_id)
                    step_core = Step5_3Core(driver)
                    account_logger.info(f"Step5_3Core 인스턴스 생성 완료")
                    
                    # 계정 정보 가져오기 (가상 ID를 실제 이메일로 변환)
                    real_account_id = get_real_account_id(account_id)
                    account_info = self.account_manager.get_account(real_account_id)
                    account_logger.info(f"계정 정보 획득: {account_info.get('id', 'N/A')} (원본 ID: {account_id}, 실제 ID: {real_account_id})")
                    
                    # 청크 사이즈가 설정되어 있으면 브라우저 재시작 방식 사용
                    if chunk_size and chunk_size > 0:
                        account_logger.info(f"브라우저 재시작 방식으로 53단계 실행 (수량: {quantity}, 청크 크기: {chunk_size})")
                        step_result = self._execute_step5_3_with_browser_restart(account_id, browser_id, quantity, chunk_size, account_info)
                    else:
                        account_logger.info(f"기존 방식으로 53단계 실행 (수량: {quantity})")
                        step_result = step_core.execute_step5_3(quantity, account_info)
                    
                    account_logger.info(f"Step5_3Core 실행 완료, 결과: {step_result}")
                    
                    result.update(step_result)
                    if 'success' in step_result:
                        result['success'] = step_result['success']
                    account_logger.info(f"53단계 실행 완료 - 처리: {result.get('processed', 0)}, 실패: {result.get('failed', 0)}, 성공: {result.get('success', False)}")
                except Exception as step_error:
                    account_logger.error(f"Step5_3Core 실행 중 예외 발생: {step_error}")
                    account_logger.error(f"Step5_3Core 예외 상세: {traceback.format_exc()}")
                    raise
                    
            elif step == 61:
                account_logger.info(f"61단계 실행 시작 - 수량: {quantity}")
                try:
                    # Step6_1Core 동적 임포트
                    from core.steps.step6_1_core import execute_step6_1
                    
                    # 기존 브라우저 재사용
                    driver = self.browser_manager.get_driver(browser_id)
                    
                    # 계정 정보 가져오기 (가상 ID를 실제 이메일로 변환)
                    real_account_id = get_real_account_id(account_id)
                    account_logger.info(f"계정 정보: 원본 ID: {account_id}, 실제 ID: {real_account_id}")
                    
                    # Step6_1 실행 (기존 브라우저 사용)
                    step_result = execute_step6_1(
                        account_id=real_account_id,
                        quantity=quantity,
                        headless=self.config.get('browser', {}).get('headless', False),
                        driver=driver  # 기존 드라이버 전달
                    )
                    
                    account_logger.info(f"Step6_1Core 실행 완료, 결과: {step_result}")
                    
                    result.update(step_result)
                    if 'success' in step_result:
                        result['success'] = step_result['success']
                    account_logger.info(f"61단계 실행 완료 - 처리: {result.get('processed', 0)}, 실패: {result.get('failed', 0)}, 성공: {result.get('success', False)}")
                except Exception as step_error:
                    account_logger.error(f"Step6_1Core 실행 중 예외 발생: {step_error}")
                    account_logger.error(f"Step6_1Core 예외 상세: {traceback.format_exc()}")
                    raise
                    
            elif step == 62:
                account_logger.info(f"62단계 실행 시작 - 수량: {quantity}")
                try:
                    # Step6_2Core 동적 임포트
                    from core.steps.step6_2_core import execute_step6_2
                    
                    # 기존 브라우저 재사용
                    driver = self.browser_manager.get_driver(browser_id)
                    
                    # 계정 정보 가져오기 (가상 ID를 실제 이메일로 변환)
                    real_account_id = get_real_account_id(account_id)
                    account_logger.info(f"계정 정보: 원본 ID: {account_id}, 실제 ID: {real_account_id}")
                    
                    # Step6_2 실행 (기존 브라우저 사용)
                    step_result = execute_step6_2(
                        account_id=real_account_id,
                        quantity=quantity,
                        headless=self.config.get('browser', {}).get('headless', False),
                        driver=driver  # 기존 드라이버 전달
                    )
                    
                    account_logger.info(f"Step6_2Core 실행 완료, 결과: {step_result}")
                    
                    result.update(step_result)
                    if 'success' in step_result:
                        result['success'] = step_result['success']
                    account_logger.info(f"62단계 실행 완료 - 처리: {result.get('processed', 0)}, 실패: {result.get('failed', 0)}, 성공: {result.get('success', False)}")
                except Exception as step_error:
                    account_logger.error(f"Step6_2Core 실행 중 예외 발생: {step_error}")
                    account_logger.error(f"Step6_2Core 예외 상세: {traceback.format_exc()}")
                    raise
                    
            elif step == 63:
                account_logger.info(f"63단계 실행 시작 - 수량: {quantity}")
                try:
                    # Step6_3Core 동적 임포트
                    from core.steps.step6_3_core import execute_step6_3
                    
                    # 기존 브라우저 재사용
                    driver = self.browser_manager.get_driver(browser_id)
                    
                    # 계정 정보 가져오기 (가상 ID를 실제 이메일로 변환)
                    real_account_id = get_real_account_id(account_id)
                    account_logger.info(f"계정 정보: 원본 ID: {account_id}, 실제 ID: {real_account_id}")
                    
                    # Step6_3 실행 (기존 브라우저 사용)
                    step_result = execute_step6_3(
                        account_id=real_account_id,
                        quantity=quantity,
                        headless=self.config.get('browser', {}).get('headless', False),
                        driver=driver  # 기존 드라이버 전달
                    )
                    
                    account_logger.info(f"Step6_3Core 실행 완료, 결과: {step_result}")
                    
                    result.update(step_result)
                    if 'success' in step_result:
                        result['success'] = step_result['success']
                    account_logger.info(f"63단계 실행 완료 - 처리: {result.get('processed', 0)}, 실패: {result.get('failed', 0)}, 성공: {result.get('success', False)}")
                except Exception as step_error:
                    account_logger.error(f"Step6_3Core 실행 중 예외 발생: {step_error}")
                    account_logger.error(f"Step6_3Core 예외 상세: {traceback.format_exc()}")
                    raise
                    
            elif step == 4:
                account_logger.info(f"4단계 실행 시작 - 수량: {quantity}")
                try:
                    # step4_core.py의 run_step4_for_account 함수 사용
                    from core.steps.step4_core import run_step4_for_account
                    
                    # 계정 정보 가져오기 (가상 ID를 실제 이메일로 변환)
                    real_account_id = get_real_account_id(account_id)
                    account_logger.info(f"계정 정보: 원본 ID: {account_id}, 실제 ID: {real_account_id}")
                    
                    # 수량이 20개 이상이면 브라우저 재시작 방식 사용
                    if quantity >= 20:
                        account_logger.info(f"브라우저 재시작 방식으로 4단계 실행 (수량: {quantity})")
                        step_result = self._execute_step4_with_browser_restart(account_id, browser_id, quantity, real_account_id)
                    else:
                        account_logger.info(f"기존 방식으로 4단계 실행 (수량: {quantity})")
                        # 기존 브라우저 재사용하여 4단계 실행
                        driver = self.browser_manager.get_driver(browser_id)
                        step_result = run_step4_for_account(
                            account_id=real_account_id,
                            quantity=quantity,
                            headless=self.config.get('browser', {}).get('headless', False),
                            driver=driver  # 기존 드라이버 전달
                        )
                    
                    account_logger.info(f"Step4Core 실행 완료, 결과: {step_result}")
                    
                    # 결과 변환 (step4_core의 결과 형식을 batch_manager 형식으로 변환)
                    if step_result.get('success', False):
                        if step_result.get('skipped', False):
                            # 스킵된 경우 - 번역 가능한 상품 부족
                            result['success'] = True
                            result['processed'] = 0
                            result['failed'] = 0
                            result['should_stop_batch'] = True  # 배치분할 중단 플래그 설정
                            account_logger.warning("⚠️ 번역 가능한 상품이 부족하여 4단계가 스킵되었습니다. 후속 배치분할을 중단합니다.")
                        else:
                            # 정상 완료된 경우
                            result['success'] = True
                            result['processed'] = step_result.get('processed_count', quantity)
                            result['failed'] = 0
                            
                            # 처리된 수량이 요청 수량보다 적으면 배치분할 중단
                            if result['processed'] < quantity:
                                result['should_stop_batch'] = True
                                account_logger.warning(f"⚠️ 처리된 수량({result['processed']})이 요청 수량({quantity})보다 적습니다. 후속 배치분할을 중단합니다.")
                    else:
                        # 실패한 경우
                        result['success'] = False
                        result['processed'] = 0
                        result['failed'] = quantity
                        result['errors'].append(step_result.get('message', '4단계 실행 실패'))
                    
                    account_logger.info(f"4단계 실행 완료 - 처리: {result.get('processed', 0)}, 실패: {result.get('failed', 0)}, 성공: {result.get('success', False)}")
                    
                except Exception as step_error:
                    account_logger.error(f"Step4Core 실행 중 예외 발생: {step_error}")
                    account_logger.error(f"Step4Core 예외 상세: {traceback.format_exc()}")
                    raise
                    
            elif step == 21:
                account_logger.info(f"21단계 실행 시작 - 수량: {quantity}")
                try:
                    # Step2_1Core 동적 임포트
                    from core.steps.step2_1_core import Step2_1Core
                    
                    driver = self.browser_manager.get_driver(browser_id)
                    # 브라우저 재시작 콜백 함수 정의
                    def restart_browser_callback():
                        account_logger.info("브라우저 재시작 콜백 호출됨")
                        try:
                            # 기존 브라우저 종료
                            if driver:
                                driver.quit()
                        except Exception as e:
                            account_logger.warning(f"기존 브라우저 종료 중 오류: {e}")
                        
                        # 새 브라우저 생성
                        new_driver = self.browser_manager.create_browser(account_id)
                        if new_driver:
                            account_logger.info("브라우저 재시작 성공")
                            return new_driver
                        else:
                            account_logger.error("브라우저 재시작 실패")
                            return None
                    
                    step_core = Step2_1Core(driver=driver, server_name="서버1", restart_browser_callback=restart_browser_callback)
                    account_logger.info(f"Step2_1Core 인스턴스 생성 완료 (server_name=서버1, restart_browser_callback 설정됨)")
                    
                    # 계정 정보 가져오기 (가상 ID를 실제 이메일로 변환)
                    real_account_id = get_real_account_id(account_id)
                    account_info = self.account_manager.get_account(real_account_id)
                    account_logger.info(f"계정 정보 획득: {account_info.get('id', 'N/A')} (원본 ID: {account_id}, 실제 ID: {real_account_id})")
                    
                    # Excel에서 작업 목록을 먼저 로드하여 provider_codes 추출
                    from product_editor_core2 import ProductEditorCore2
                    product_editor = ProductEditorCore2(driver)
                    task_list = product_editor.load_task_list_from_excel_with_server_filter(
                        account_id=real_account_id,
                        step="step2",
                        server_name="서버1"
                    )
                    
                    # task_list에서 provider_codes 추출
                    provider_codes = list(set([task['provider_code'] for task in task_list if task.get('provider_code')]))
                    account_logger.info(f"추출된 provider_codes: {provider_codes}")
                    
                    if not provider_codes:
                        account_logger.warning("처리할 provider_code가 없습니다")
                        result['success'] = True  # 작업할 것이 없는 것은 성공으로 간주
                        return result
                    
                    # 청크 사이즈에 따른 처리 방식 결정
                    if len(provider_codes) > chunk_size:
                        account_logger.info(f"브라우저 재시작 방식으로 21단계 실행 (키워드 수: {len(provider_codes)}, 청크 크기: {chunk_size})")
                        step_result = self._execute_step21_with_browser_restart(account_id, browser_id, provider_codes, chunk_size, account_info)
                    else:
                        account_logger.info(f"기존 방식으로 21단계 실행 (키워드 수: {len(provider_codes)})")
                        # Step2_1Core 실행 (등록상품관리 화면 열기는 내부에서 처리)
                        step_result = step_core.execute_step2_1(provider_codes, account_info)
                    
                    account_logger.info(f"Step2_1Core 실행 완료, 결과: {step_result}")
                    
                    result.update(step_result)
                    if 'success' in step_result:
                        result['success'] = step_result['success']
                    account_logger.info(f"21단계 실행 완료 - 처리: {result.get('processed', 0)}, 실패: {result.get('failed', 0)}, 성공: {result.get('success', False)}")
                except Exception as step_error:
                    account_logger.error(f"Step2_1Core 실행 중 예외 발생: {step_error}")
                    account_logger.error(f"Step2_1Core 예외 상세: {traceback.format_exc()}")
                    raise
                    
            elif step == 22:
                account_logger.info(f"22단계 실행 시작 - 수량: {quantity}")
                try:
                    # Step2_2Core 동적 임포트
                    from core.steps.step2_2_core import Step2_2Core
                    
                    driver = self.browser_manager.get_driver(browser_id)
                    step_core = Step2_2Core(driver)
                    account_logger.info(f"Step2_2Core 인스턴스 생성 완료")
                    
                    # 계정 정보 가져오기 (가상 ID를 실제 이메일로 변환)
                    real_account_id = get_real_account_id(account_id)
                    account_info = self.account_manager.get_account(real_account_id)
                    account_logger.info(f"계정 정보 획득: {account_info.get('id', 'N/A')} (원본 ID: {account_id}, 실제 ID: {real_account_id})")
                    
                    # Excel에서 작업 목록을 먼저 로드하여 provider_codes 추출
                    from product_editor_core2 import ProductEditorCore2
                    product_editor = ProductEditorCore2(driver)
                    task_list = product_editor.load_task_list_from_excel_with_server_filter(
                        account_id=real_account_id,
                        step="step2",
                        server_name="서버2"
                    )
                    
                    # task_list에서 provider_codes 추출
                    provider_codes = list(set([task['provider_code'] for task in task_list if task.get('provider_code')]))
                    account_logger.info(f"추출된 provider_codes: {provider_codes}")
                    
                    if not provider_codes:
                        account_logger.warning("처리할 provider_code가 없습니다")
                        result['success'] = True  # 작업할 것이 없는 것은 성공으로 간주
                        return result
                    
                    # 청크 사이즈에 따른 처리 방식 결정
                    if len(provider_codes) > chunk_size:
                        account_logger.info(f"브라우저 재시작 방식으로 22단계 실행 (키워드 수: {len(provider_codes)}, 청크 크기: {chunk_size})")
                        step_result = self._execute_step22_with_browser_restart(account_id, browser_id, provider_codes, chunk_size, account_info)
                    else:
                        account_logger.info(f"기존 방식으로 22단계 실행 (키워드 수: {len(provider_codes)})")
                        # Step2_2Core 실행 (등록상품관리 화면 열기는 내부에서 처리)
                        step_result = step_core.execute_step2_2(provider_codes, account_info)
                    
                    account_logger.info(f"Step2_2Core 실행 완료, 결과: {step_result}")
                    
                    result.update(step_result)
                    if 'success' in step_result:
                        result['success'] = step_result['success']
                    account_logger.info(f"22단계 실행 완료 - 처리: {result.get('processed', 0)}, 실패: {result.get('failed', 0)}, 성공: {result.get('success', False)}")
                except Exception as step_error:
                    account_logger.error(f"Step2_2Core 실행 중 예외 발생: {step_error}")
                    account_logger.error(f"Step2_2Core 예외 상세: {traceback.format_exc()}")
                    raise
                    
            elif step == 23:
                account_logger.info(f"23단계 실행 시작 - 수량: {quantity}")
                try:
                    # Step2_3Core 동적 임포트
                    from core.steps.step2_3_core import Step2_3Core
                    
                    driver = self.browser_manager.get_driver(browser_id)
                    step_core = Step2_3Core(driver)
                    account_logger.info(f"Step2_3Core 인스턴스 생성 완료")
                    
                    # 계정 정보 가져오기 (가상 ID를 실제 이메일로 변환)
                    real_account_id = get_real_account_id(account_id)
                    account_info = self.account_manager.get_account(real_account_id)
                    account_logger.info(f"계정 정보 획득: {account_info.get('id', 'N/A')} (원본 ID: {account_id}, 실제 ID: {real_account_id})")
                    
                    # Excel에서 작업 목록을 먼저 로드하여 provider_codes 추출
                    from product_editor_core2 import ProductEditorCore2
                    product_editor = ProductEditorCore2(driver)
                    task_list = product_editor.load_task_list_from_excel_with_server_filter(
                        account_id=real_account_id,
                        step="step2",
                        server_name="서버3"
                    )
                    
                    # task_list에서 provider_codes 추출
                    provider_codes = list(set([task['provider_code'] for task in task_list if task.get('provider_code')]))
                    account_logger.info(f"추출된 provider_codes: {provider_codes}")
                    
                    if not provider_codes:
                        account_logger.warning("처리할 provider_code가 없습니다")
                        result['success'] = True  # 작업할 것이 없는 것은 성공으로 간주
                        return result
                    
                    # 청크 사이즈에 따른 처리 방식 결정
                    if len(provider_codes) > chunk_size:
                        account_logger.info(f"브라우저 재시작 방식으로 23단계 실행 (키워드 수: {len(provider_codes)}, 청크 크기: {chunk_size})")
                        step_result = self._execute_step23_with_browser_restart(account_id, browser_id, provider_codes, chunk_size, account_info)
                    else:
                        account_logger.info(f"기존 방식으로 23단계 실행 (키워드 수: {len(provider_codes)})")
                        # Step2_3Core 실행 (등록상품관리 화면 열기는 내부에서 처리)
                        step_result = step_core.execute_step2_3(provider_codes, account_info)
                    
                    account_logger.info(f"Step2_3Core 실행 완료, 결과: {step_result}")
                    
                    result.update(step_result)
                    if 'success' in step_result:
                        result['success'] = step_result['success']
                    account_logger.info(f"23단계 실행 완료 - 처리: {result.get('processed', 0)}, 실패: {result.get('failed', 0)}, 성공: {result.get('success', False)}")
                except Exception as step_error:
                    account_logger.error(f"Step2_3Core 실행 중 예외 발생: {step_error}")
                    account_logger.error(f"Step2_3Core 예외 상세: {traceback.format_exc()}")
                    raise
                    
            elif step == 31:
                account_logger.info(f"31단계 실행 시작 - 수량: {quantity}")
                try:
                    # Step3_1Core 동적 임포트
                    from core.steps.step3_1_core import Step3_1Core
                    
                    driver = self.browser_manager.get_driver(browser_id)
                    step_core = Step3_1Core(driver)
                    account_logger.info(f"Step3_1Core 인스턴스 생성 완료")
                    
                    # 계정 정보 가져오기 (가상 ID를 실제 이메일로 변환)
                    real_account_id = get_real_account_id(account_id)
                    account_info = self.account_manager.get_account(real_account_id)
                    account_logger.info(f"계정 정보 획득: {account_info.get('id', 'N/A')} (원본 ID: {account_id}, 실제 ID: {real_account_id})")
                    
                    # Excel에서 작업 목록을 먼저 로드하여 provider_codes 추출
                    from product_editor_core3 import ProductEditorCore3
                    product_editor = ProductEditorCore3(driver)
                    task_list = product_editor.load_task_list_from_excel_with_server_filter(
                        account_id=real_account_id,
                        step="step3",
                        server_name="서버1"
                    )
                    
                    # task_list에서 provider_codes 추출
                    provider_codes = list(set([task['provider_code'] for task in task_list if task.get('provider_code')]))
                    account_logger.info(f"추출된 provider_codes: {provider_codes}")
                    
                    if not provider_codes:
                        account_logger.warning("처리할 provider_code가 없습니다")
                        result['success'] = True  # 작업할 것이 없는 것은 성공으로 간주
                        return result
                    
                    # 청크 사이즈에 따른 처리 방식 결정
                    if len(provider_codes) > chunk_size:
                        account_logger.info(f"브라우저 재시작 방식으로 31단계 실행 (키워드 수: {len(provider_codes)}, 청크 크기: {chunk_size})")
                        step_result = self._execute_step31_with_browser_restart(account_id, browser_id, provider_codes, chunk_size, account_info)
                    else:
                        account_logger.info(f"기존 방식으로 31단계 실행 (키워드 수: {len(provider_codes)})")
                        # Step3_1Core 실행 (등록상품관리 화면 열기는 내부에서 처리)
                        step_result = step_core.execute_step3_1(provider_codes, account_info)
                    
                    account_logger.info(f"Step3_1Core 실행 완료, 결과: {step_result}")
                    
                    result.update(step_result)
                    if 'success' in step_result:
                        result['success'] = step_result['success']
                    account_logger.info(f"31단계 실행 완료 - 처리: {result.get('processed', 0)}, 실패: {result.get('failed', 0)}, 성공: {result.get('success', False)}")
                except Exception as step_error:
                    account_logger.error(f"Step3_1Core 실행 중 예외 발생: {step_error}")
                    account_logger.error(f"Step3_1Core 예외 상세: {traceback.format_exc()}")
                    raise
                    
            elif step == 32:
                account_logger.info(f"32단계 실행 시작 - 수량: {quantity}")
                try:
                    # Step3_2Core 동적 임포트
                    from core.steps.step3_2_core import Step3_2Core
                    
                    driver = self.browser_manager.get_driver(browser_id)
                    step_core = Step3_2Core(driver)
                    account_logger.info(f"Step3_2Core 인스턴스 생성 완료")
                    
                    # 계정 정보 가져오기 (가상 ID를 실제 이메일로 변환)
                    real_account_id = get_real_account_id(account_id)
                    account_info = self.account_manager.get_account(real_account_id)
                    account_logger.info(f"계정 정보 획득: {account_info.get('id', 'N/A')} (원본 ID: {account_id}, 실제 ID: {real_account_id})")
                    
                    # Excel에서 작업 목록을 먼저 로드하여 provider_codes 추출
                    from product_editor_core3 import ProductEditorCore3
                    product_editor = ProductEditorCore3(driver)
                    task_list = product_editor.load_task_list_from_excel_with_server_filter(
                        account_id=real_account_id,
                        step="step3",
                        server_name="서버2"
                    )
                    
                    # task_list에서 provider_codes 추출
                    provider_codes = list(set([task['provider_code'] for task in task_list if task.get('provider_code')]))
                    account_logger.info(f"추출된 provider_codes: {provider_codes}")
                    
                    if not provider_codes:
                        account_logger.warning("처리할 provider_code가 없습니다")
                        result['success'] = True  # 작업할 것이 없는 것은 성공으로 간주
                        return result
                    
                    # 청크 사이즈에 따른 처리 방식 결정
                    if len(provider_codes) > chunk_size:
                        account_logger.info(f"브라우저 재시작 방식으로 32단계 실행 (키워드 수: {len(provider_codes)}, 청크 크기: {chunk_size})")
                        step_result = self._execute_step32_with_browser_restart(account_id, browser_id, provider_codes, chunk_size, account_info)
                    else:
                        account_logger.info(f"기존 방식으로 32단계 실행 (키워드 수: {len(provider_codes)})")
                        # Step3_2Core 실행
                        step_result = step_core.execute_step3_2(provider_codes, account_info)
                    
                    account_logger.info(f"Step3_2Core 실행 완료, 결과: {step_result}")
                    
                    result.update(step_result)
                    if 'success' in step_result:
                        result['success'] = step_result['success']
                    account_logger.info(f"32단계 실행 완료 - 처리: {result.get('processed', 0)}, 실패: {result.get('failed', 0)}, 성공: {result.get('success', False)}")
                except Exception as step_error:
                    account_logger.error(f"Step3_2Core 실행 중 예외 발생: {step_error}")
                    account_logger.error(f"Step3_2Core 예외 상세: {traceback.format_exc()}")
                    raise
                    
            elif step == 33:
                account_logger.info(f"33단계 실행 시작 - 수량: {quantity}")
                try:
                    # Step3_3Core 동적 임포트
                    from core.steps.step3_3_core import Step3_3Core
                    
                    driver = self.browser_manager.get_driver(browser_id)
                    step_core = Step3_3Core(driver)
                    account_logger.info(f"Step3_3Core 인스턴스 생성 완료")
                    
                    # 계정 정보 가져오기 (가상 ID를 실제 이메일로 변환)
                    real_account_id = get_real_account_id(account_id)
                    account_info = self.account_manager.get_account(real_account_id)
                    account_logger.info(f"계정 정보 획득: {account_info.get('id', 'N/A')} (원본 ID: {account_id}, 실제 ID: {real_account_id})")
                    
                    # Excel에서 작업 목록을 먼저 로드하여 provider_codes 추출
                    from product_editor_core3 import ProductEditorCore3
                    product_editor = ProductEditorCore3(driver)
                    task_list = product_editor.load_task_list_from_excel_with_server_filter(
                        account_id=real_account_id,
                        step="step3",
                        server_name="서버3"
                    )
                    
                    # task_list에서 provider_codes 추출
                    provider_codes = list(set([task['provider_code'] for task in task_list if task.get('provider_code')]))
                    account_logger.info(f"추출된 provider_codes: {provider_codes}")
                    
                    if not provider_codes:
                        account_logger.warning("처리할 provider_code가 없습니다")
                        result['success'] = True  # 작업할 것이 없는 것은 성공으로 간주
                        return result
                    
                    # 청크 사이즈에 따른 처리 방식 결정
                    if len(provider_codes) > chunk_size:
                        account_logger.info(f"브라우저 재시작 방식으로 33단계 실행 (키워드 수: {len(provider_codes)}, 청크 크기: {chunk_size})")
                        step_result = self._execute_step33_with_browser_restart(account_id, browser_id, provider_codes, chunk_size, account_info)
                    else:
                        account_logger.info(f"기존 방식으로 33단계 실행 (키워드 수: {len(provider_codes)})")
                        # Step3_3Core 실행
                        step_result = step_core.execute_step3_3(provider_codes, account_info)
                    
                    account_logger.info(f"Step3_3Core 실행 완료, 결과: {step_result}")
                    
                    result.update(step_result)
                    if 'success' in step_result:
                        result['success'] = step_result['success']
                    account_logger.info(f"33단계 실행 완료 - 처리: {result.get('processed', 0)}, 실패: {result.get('failed', 0)}, 성공: {result.get('success', False)}")
                except Exception as step_error:
                    account_logger.error(f"Step3_3Core 실행 중 예외 발생: {step_error}")
                    account_logger.error(f"Step3_3Core 예외 상세: {traceback.format_exc()}")
                    raise
                    
            else:
                # 6단계는 향후 구현
                raise NotImplementedError(f"{step}단계는 아직 구현되지 않았습니다.")
        
        except Exception as e:
            account_logger.error(f"=== {step}단계 실행 중 오류 ===")
            account_logger.error(f"오류 메시지: {e}")
            account_logger.error(f"오류 상세: {traceback.format_exc()}")
            result['errors'].append(str(e))
        
        finally:
            # 브라우저 정리
            try:
                if browser_id:
                    account_logger.info(f"브라우저 정리 시작: {browser_id}")
                    self.browser_manager.close_browser(browser_id)
            except Exception as cleanup_error:
                account_logger.error(f"브라우저 정리 중 오류: {cleanup_error}")
        
        account_logger.info(f"=== {step}단계 실행 완료 ===")
        return result
    
    def _execute_step1_with_browser_restart(self, account_id: str, initial_browser_id: str, quantity: int, chunk_size: int = 20) -> Dict:
        """
        브라우저 재시작 방식으로 1단계 실행
        
        Args:
            account_id: 계정 ID
            initial_browser_id: 초기 브라우저 ID
            quantity: 총 처리할 수량
            chunk_size: 청크 크기 (기본값: 20)
            
        Returns:
            Dict: 실행 결과
        """
        account_logger = self.account_loggers.get(account_id)
        if not account_logger:
            account_logger = AccountLogger(account_id, self.start_time)
            self.account_loggers[account_id] = account_logger
        
        total_result = {
            'success': False,
            'processed': 0,
            'failed': 0,
            'errors': [],
            'chunks_completed': 0,
            'total_chunks': 0
        }
        
        try:
            # 총 청크 수 계산
            total_chunks = (quantity + chunk_size - 1) // chunk_size
            total_result['total_chunks'] = total_chunks
            
            account_logger.info(f"브라우저 재시작 방식으로 1단계 작업 시작")
            account_logger.info(f"총 수량: {quantity}, 청크 크기: {chunk_size}, 총 청크 수: {total_chunks}")
            
            current_browser_id = initial_browser_id
            
            for chunk_idx in range(total_chunks):
                start_idx = chunk_idx * chunk_size
                end_idx = min(start_idx + chunk_size, quantity)
                current_chunk_size = end_idx - start_idx
                
                account_logger.info(f"===== 청크 {chunk_idx + 1}/{total_chunks} 시작 (상품 {start_idx + 1}-{end_idx}) =====")
                
                try:
                    # 현재 청크 실행
                    driver = self.browser_manager.get_driver(current_browser_id)
                    step_core = Step1Core(driver)
                    
                    chunk_result = step_core.execute_step1(current_chunk_size)
                    
                    # 결과 누적
                    total_result['processed'] += chunk_result['processed']
                    total_result['failed'] += chunk_result['failed']
                    total_result['errors'].extend(chunk_result['errors'])
                    total_result['chunks_completed'] += 1
                    
                    account_logger.info(f"청크 {chunk_idx + 1} 완료: 처리 {chunk_result['processed']}개, 실패 {chunk_result['failed']}개")
                    
                    # 배치분할 중단 플래그 확인
                    if chunk_result.get('should_stop_batch', False):
                        account_logger.warning(f"⚠️ 청크 {chunk_idx + 1}에서 비그룹상품이 0개가 되어 후속 배치분할을 중단합니다.")
                        account_logger.info(f"총 {chunk_idx + 1}/{total_chunks} 청크 완료 후 중단")
                        # 현재 브라우저 종료 후 루프 탈출
                        self.browser_manager.close_browser(current_browser_id)
                        break
                    
                    # 마지막 청크가 아니면 브라우저 재시작
                    if chunk_idx < total_chunks - 1:
                        account_logger.info(f"청크 {chunk_idx + 1} 완료 후 브라우저 재시작")
                        
                        # 현재 브라우저 종료
                        self.browser_manager.close_browser(current_browser_id)
                        
                        # 새 브라우저 생성 및 로그인
                        import time
                        time.sleep(2)  # 브라우저 종료 대기
                        
                        new_browser_id = self.browser_manager.create_browser(account_id)
                        real_account_id = get_real_account_id(account_id)
                        email, password = self.account_manager.get_account_credentials(real_account_id)
                        login_success = self.browser_manager.login_browser(new_browser_id, email, password)
                        
                        if not login_success:
                            raise Exception(f"청크 {chunk_idx + 1} 후 재로그인 실패")
                        
                        current_browser_id = new_browser_id
                        account_logger.info(f"브라우저 재시작 및 로그인 완료: {current_browser_id}")
                        
                        time.sleep(3)  # 재시작 후 초기화 대기
                    else:
                        # 마지막 청크인 경우 브라우저 종료
                        self.browser_manager.close_browser(current_browser_id)
                        
                except Exception as chunk_error:
                    account_logger.error(f"청크 {chunk_idx + 1} 실행 중 오류: {chunk_error}")
                    
                    # 청크별 재시도 로직
                    retry_success = self._retry_failed_chunk(
                        account_id, chunk_idx + 1, current_chunk_size, 
                        current_browser_id, account_logger
                    )
                    
                    if retry_success:
                        account_logger.info(f"청크 {chunk_idx + 1} 재시도 성공")
                        total_result['processed'] += current_chunk_size
                        total_result['chunks_completed'] += 1
                    else:
                        account_logger.error(f"청크 {chunk_idx + 1} 재시도 실패")
                        total_result['failed'] += current_chunk_size
                        total_result['errors'].append(f"청크 {chunk_idx + 1}: {str(chunk_error)}")
                    
                # 오류 발생 시에도 브라우저 재시작 시도
                if chunk_idx < total_chunks - 1:
                    try:
                        account_logger.info(f"오류 발생 후 브라우저 재시작 시도")
                        
                        # 현재 브라우저 종료
                        try:
                            self.browser_manager.close_browser(current_browser_id)
                        except:
                            pass
                        
                        # 새 브라우저 생성 및 로그인
                        import time
                        time.sleep(2)
                        
                        new_browser_id = self.browser_manager.create_browser(account_id)
                        real_account_id = get_real_account_id(account_id)
                        email, password = self.account_manager.get_account_credentials(real_account_id)
                        login_success = self.browser_manager.login_browser(new_browser_id, email, password)
                        
                        if login_success:
                            current_browser_id = new_browser_id
                            account_logger.info(f"오류 후 브라우저 재시작 성공: {current_browser_id}")
                            time.sleep(3)
                        else:
                            account_logger.error(f"오류 후 재로그인 실패")
                            break
                            
                    except Exception as restart_error:
                        account_logger.error(f"브라우저 재시작 실패: {restart_error}")
                        break
            
            # 전체 결과 평가
            if total_result['processed'] > 0:
                total_result['success'] = True
                
            account_logger.info(f"브라우저 재시작 방식 작업 완료")
            account_logger.info(f"총 처리: {total_result['processed']}개, 총 실패: {total_result['failed']}개")
            account_logger.info(f"완료된 청크: {total_result['chunks_completed']}/{total_result['total_chunks']}")
            
            return total_result
            
        except Exception as e:
            account_logger.error(f"브라우저 재시작 방식 작업 중 전체 오류: {e}")
            total_result['errors'].append(f"전체 작업 오류: {str(e)}")
            return total_result
    
    def _retry_failed_chunk(self, account_id: str, chunk_number: int, chunk_size: int, 
                           browser_id: str, account_logger) -> bool:
        """실패한 청크 재시도
        
        Args:
            account_id: 계정 ID
            chunk_number: 청크 번호
            chunk_size: 청크 크기
            browser_id: 브라우저 ID
            account_logger: 계정별 로거
            
        Returns:
            bool: 재시도 성공 여부
        """
        max_retries = 2  # 최대 2회 재시도
        retry_delay = 30  # 재시도 간격 (초)
        
        for retry_attempt in range(1, max_retries + 1):
            try:
                account_logger.info(f"청크 {chunk_number} 재시도 {retry_attempt}/{max_retries} 시작")
                
                # 재시도 전 대기
                import time
                time.sleep(retry_delay)
                
                # 브라우저 상태 확인 및 복구
                if not self._recover_browser_for_retry(account_id, browser_id, account_logger):
                    account_logger.warning(f"청크 {chunk_number} 재시도 {retry_attempt}: 브라우저 복구 실패")
                    continue
                
                # 청크 재실행
                driver = self.browser_manager.get_driver(browser_id)
                if not driver:
                    account_logger.warning(f"청크 {chunk_number} 재시도 {retry_attempt}: 드라이버 없음")
                    continue
                
                step_core = Step1Core(driver)
                chunk_result = step_core.execute_step1(chunk_size)
                
                # 재시도 성공 조건 확인
                if chunk_result.get('processed', 0) > 0:
                    account_logger.info(f"청크 {chunk_number} 재시도 {retry_attempt} 성공: {chunk_result['processed']}개 처리")
                    return True
                else:
                    account_logger.warning(f"청크 {chunk_number} 재시도 {retry_attempt} 실패: 처리된 항목 없음")
                    
            except Exception as retry_error:
                account_logger.error(f"청크 {chunk_number} 재시도 {retry_attempt} 중 오류: {retry_error}")
                
        account_logger.error(f"청크 {chunk_number} 모든 재시도 실패")
        return False
    
    def _recover_browser_for_retry(self, account_id: str, browser_id: str, account_logger) -> bool:
        """재시도를 위한 브라우저 복구
        
        Args:
            account_id: 계정 ID
            browser_id: 브라우저 ID
            account_logger: 계정별 로거
            
        Returns:
            bool: 복구 성공 여부
        """
        try:
            # 현재 브라우저 상태 확인
            driver = self.browser_manager.get_driver(browser_id)
            if driver:
                try:
                    # 간단한 상태 확인 (페이지 제목 가져오기)
                    driver.title
                    account_logger.info("브라우저 상태 정상 - 복구 불필요")
                    return True
                except:
                    account_logger.info("브라우저 응답 없음 - 재시작 필요")
            
            # 브라우저 재시작
            account_logger.info("브라우저 재시작 시도")
            
            # 기존 브라우저 종료
            try:
                self.browser_manager.close_browser(browser_id)
            except:
                pass
            
            # 새 브라우저 생성 및 로그인
            import time
            time.sleep(3)
            
            new_browser_id = self.browser_manager.create_browser(account_id)
            real_account_id = get_real_account_id(account_id)
            email, password = self.account_manager.get_account_credentials(real_account_id)
            login_success = self.browser_manager.login_browser(new_browser_id, email, password)
            
            if login_success:
                account_logger.info(f"브라우저 복구 성공: {new_browser_id}")
                # 브라우저 ID 업데이트 (실제로는 매니저에서 처리되어야 함)
                return True
            else:
                account_logger.error("브라우저 복구 실패: 로그인 실패")
                return False
                
        except Exception as e:
            account_logger.error(f"브라우저 복구 중 오류: {e}")
            return False
    
    def _retry_failed_chunk_step4(self, account_id: str, chunk_number: int, chunk_size: int, 
                                 browser_id: str, account_logger, driver) -> bool:
        """Step4 실패한 청크 재시도
        
        Args:
            account_id: 계정 ID
            chunk_number: 청크 번호
            chunk_size: 청크 크기
            browser_id: 브라우저 ID
            account_logger: 계정별 로거
            driver: 기존 드라이버
            
        Returns:
            bool: 재시도 성공 여부
        """
        max_retries = 2  # 최대 2회 재시도
        retry_delay = 30  # 재시도 간격 (초)
        
        for retry_attempt in range(1, max_retries + 1):
            try:
                account_logger.info(f"청크 {chunk_number} 재시도 {retry_attempt}/{max_retries} 시작")
                
                # 재시도 전 대기
                import time
                time.sleep(retry_delay)
                
                # 브라우저 상태 확인
                try:
                    driver.title  # 간단한 상태 확인
                except:
                    account_logger.warning(f"청크 {chunk_number} 재시도 {retry_attempt}: 브라우저 응답 없음")
                    continue
                
                # Step4 재실행
                from core.steps.step4_core import run_step4_for_account
                chunk_result = run_step4_for_account(
                    account_id=account_id,
                    quantity=chunk_size,
                    headless=self.config.get('browser', {}).get('headless', False),
                    driver=driver
                )
                
                # 재시도 성공 조건 확인
                if chunk_result.get('success', False) and not chunk_result.get('skipped', False):
                    processed_count = chunk_result.get('processed_count', 0)
                    if processed_count > 0:
                        account_logger.info(f"청크 {chunk_number} 재시도 {retry_attempt} 성공: {processed_count}개 처리")
                        return True
                
                account_logger.warning(f"청크 {chunk_number} 재시도 {retry_attempt} 실패: {chunk_result.get('message', '처리된 항목 없음')}")
                    
            except Exception as retry_error:
                account_logger.error(f"청크 {chunk_number} 재시도 {retry_attempt} 중 오류: {retry_error}")
                
        account_logger.error(f"청크 {chunk_number} 모든 재시도 실패")
        return False
     
    def _execute_step4_with_browser_restart(self, account_id: str, initial_browser_id: str, quantity: int, real_account_id: str, chunk_size: int = 20) -> Dict:
        """
        브라우저 재사용 방식으로 4단계 실행 (브라우저 중복 생성 방지)
        
        Args:
            account_id: 계정 ID
            initial_browser_id: 초기 브라우저 ID
            quantity: 총 처리할 수량
            real_account_id: 실제 계정 ID
            chunk_size: 청크 크기 (기본값: 20)
            
        Returns:
            Dict: 실행 결과
        """
        account_logger = self.account_loggers.get(account_id)
        if not account_logger:
            account_logger = AccountLogger(account_id, self.start_time)
            self.account_loggers[account_id] = account_logger
        
        total_result = {
            'success': False,
            'processed': 0,
            'failed': 0,
            'errors': [],
            'chunks_completed': 0,
            'total_chunks': 0,
            'skipped': False,
            'should_stop_batch': False
        }
        
        driver = None
        try:
            from core.steps.step4_core import run_step4_for_account
            
            # 총 청크 수 계산
            total_chunks = (quantity + chunk_size - 1) // chunk_size
            total_result['total_chunks'] = total_chunks
            
            account_logger.info(f"브라우저 재사용 방식으로 4단계 작업 시작")
            account_logger.info(f"총 수량: {quantity}, 청크 크기: {chunk_size}, 총 청크 수: {total_chunks}")
            
            # 브라우저 한 번만 생성하고 재사용
            driver = self.browser_manager.get_driver(initial_browser_id)
            if not driver:
                account_logger.error(f"브라우저 {initial_browser_id}를 찾을 수 없습니다")
                total_result['errors'].append(f"브라우저 {initial_browser_id}를 찾을 수 없음")
                return total_result
            
            account_logger.info(f"기존 브라우저 재사용: {initial_browser_id}")
            
            for chunk_idx in range(total_chunks):
                start_idx = chunk_idx * chunk_size
                end_idx = min(start_idx + chunk_size, quantity)
                current_chunk_size = end_idx - start_idx
                
                account_logger.info(f"===== 청크 {chunk_idx + 1}/{total_chunks} 시작 (수량: {current_chunk_size}) =====")
                
                try:
                    # 기존 브라우저 드라이버를 재사용하여 4단계 실행
                    chunk_result = run_step4_for_account(
                        account_id=real_account_id,
                        quantity=current_chunk_size,
                        headless=self.config.get('browser', {}).get('headless', False),
                        driver=driver  # 기존 드라이버 전달
                    )
                    
                    account_logger.info(f"청크 {chunk_idx + 1} 실행 결과: {chunk_result}")
                    
                    # 결과 누적
                    if chunk_result.get('success', False):
                        if chunk_result.get('skipped', False):
                            # 스킵된 경우 - 번역 가능한 상품 부족
                            account_logger.warning(f"⚠️ 청크 {chunk_idx + 1}에서 번역 가능한 상품이 부족하여 스킵되었습니다. 후속 배치분할을 중단합니다.")
                            total_result['should_stop_batch'] = True
                            total_result['skipped'] = True
                            break
                        else:
                            # 정상 완료
                            processed_count = chunk_result.get('processed_count', current_chunk_size)
                            total_result['processed'] += processed_count
                            
                            # 처리된 수량이 요청 수량보다 적으면 배치분할 중단
                            if processed_count < current_chunk_size:
                                account_logger.warning(f"⚠️ 청크 {chunk_idx + 1}에서 처리된 수량({processed_count})이 요청 수량({current_chunk_size})보다 적습니다. 후속 배치분할을 중단합니다.")
                                total_result['should_stop_batch'] = True
                                break
                    else:
                        # 실패한 경우
                        total_result['failed'] += current_chunk_size
                        total_result['errors'].append(f"청크 {chunk_idx + 1}: {chunk_result.get('message', '실행 실패')}")
                    
                    total_result['chunks_completed'] += 1
                    account_logger.info(f"청크 {chunk_idx + 1} 완료: 처리 {total_result['processed']}개, 실패 {total_result['failed']}개")
                    
                    # 마지막 청크가 아니면 잠시 대기
                    if chunk_idx < total_chunks - 1 and not total_result['should_stop_batch']:
                        import time
                        time.sleep(3)  # 청크 간 대기
                        
                except Exception as chunk_error:
                    account_logger.error(f"청크 {chunk_idx + 1} 실행 중 오류: {chunk_error}")
                    
                    # 청크별 재시도 로직 (Step4용)
                    retry_success = self._retry_failed_chunk_step4(
                        real_account_id, chunk_idx + 1, current_chunk_size, 
                        initial_browser_id, account_logger, driver
                    )
                    
                    if retry_success:
                        account_logger.info(f"청크 {chunk_idx + 1} 재시도 성공")
                        total_result['processed'] += current_chunk_size
                        total_result['chunks_completed'] += 1
                    else:
                        account_logger.error(f"청크 {chunk_idx + 1} 재시도 실패")
                        total_result['failed'] += current_chunk_size
                        total_result['errors'].append(f"청크 {chunk_idx + 1}: {str(chunk_error)}")
            
            # 최종 결과 설정
            if total_result['processed'] > 0 or total_result['skipped']:
                total_result['success'] = True
                
            account_logger.info(f"브라우저 재시작 방식 4단계 작업 완료")
            account_logger.info(f"총 처리: {total_result['processed']}개, 총 실패: {total_result['failed']}개")
            account_logger.info(f"완료된 청크: {total_result['chunks_completed']}/{total_result['total_chunks']}")
            account_logger.info(f"스킵 여부: {total_result['skipped']}, 배치분할 중단: {total_result['should_stop_batch']}")
            
            return total_result
            
        except Exception as e:
            account_logger.error(f"브라우저 재시작 방식 4단계 작업 중 전체 오류: {e}")
            total_result['errors'].append(f"전체 작업 오류: {str(e)}")
            return total_result
    
    def _execute_step5_1_with_browser_restart(self, account_id: str, initial_browser_id: str, quantity: int, account_info: Dict = None, chunk_size: int = 20) -> Dict:
        """브라우저 재시작 방식으로 5_1단계 실행"""
        account_logger = self.account_loggers.get(account_id)
        if not account_logger:
            account_logger = AccountLogger(account_id, self.start_time)
            self.account_loggers[account_id] = account_logger
        
        total_result = {
            'success': False,
            'processed': 0,
            'failed': 0,
            'errors': [],
            'chunks_completed': 0,
            'total_chunks': 0
        }
        
        try:
            total_chunks = (quantity + chunk_size - 1) // chunk_size
            total_result['total_chunks'] = total_chunks
            
            account_logger.info(f"브라우저 재시작 방식으로 5_1단계 작업 시작")
            account_logger.info(f"총 수량: {quantity}, 청크 크기: {chunk_size}, 총 청크 수: {total_chunks}")
            
            current_browser_id = initial_browser_id
            
            for chunk_idx in range(total_chunks):
                start_idx = chunk_idx * chunk_size
                end_idx = min(start_idx + chunk_size, quantity)
                current_chunk_size = end_idx - start_idx
                
                account_logger.info(f"===== 청크 {chunk_idx + 1}/{total_chunks} 시작 (상품 {start_idx + 1}-{end_idx}) =====")
                
                try:
                    driver = self.browser_manager.get_driver(current_browser_id)
                    step_core = Step5_1Core(driver)
                    
                    chunk_result = step_core.execute_step5_1(current_chunk_size, account_info)
                    
                    total_result['processed'] += chunk_result['processed']
                    total_result['failed'] += chunk_result['failed']
                    total_result['errors'].extend(chunk_result['errors'])
                    total_result['chunks_completed'] += 1
                    
                    account_logger.info(f"청크 {chunk_idx + 1} 완료: 처리 {chunk_result['processed']}개, 실패 {chunk_result['failed']}개")
                    
                    if chunk_result.get('should_stop_batch', False):
                        account_logger.warning(f"⚠️ 청크 {chunk_idx + 1}에서 비그룹상품이 0개가 되어 후속 배치분할을 중단합니다.")
                        account_logger.info(f"총 {chunk_idx + 1}/{total_chunks} 청크 완료 후 중단")
                        self.browser_manager.close_browser(current_browser_id)
                        break
                    
                    if chunk_idx < total_chunks - 1:
                        account_logger.info(f"청크 {chunk_idx + 1} 완료 후 브라우저 재시작")
                        
                        self.browser_manager.close_browser(current_browser_id)
                        
                        import time
                        time.sleep(2)
                        
                        new_browser_id = self.browser_manager.create_browser(account_id)
                        real_account_id = get_real_account_id(account_id)
                        email, password = self.account_manager.get_account_credentials(real_account_id)
                        login_success = self.browser_manager.login_browser(new_browser_id, email, password)
                        
                        if not login_success:
                            raise Exception(f"청크 {chunk_idx + 1} 후 재로그인 실패")
                        
                        current_browser_id = new_browser_id
                        account_logger.info(f"브라우저 재시작 및 로그인 완료: {current_browser_id}")
                        
                        time.sleep(3)
                    else:
                        self.browser_manager.close_browser(current_browser_id)
                        
                except Exception as chunk_error:
                    account_logger.error(f"청크 {chunk_idx + 1} 실행 중 오류: {chunk_error}")
                    total_result['errors'].append(f"청크 {chunk_idx + 1}: {str(chunk_error)}")
            
            if total_result['processed'] > 0:
                total_result['success'] = True
                
            account_logger.info(f"브라우저 재시작 방식 5_1단계 작업 완료")
            account_logger.info(f"총 처리: {total_result['processed']}개, 총 실패: {total_result['failed']}개")
            account_logger.info(f"완료된 청크: {total_result['chunks_completed']}/{total_result['total_chunks']}")
            
            return total_result
            
        except Exception as e:
            account_logger.error(f"브라우저 재시작 방식 5_1단계 작업 중 전체 오류: {e}")
            total_result['errors'].append(f"전체 작업 오류: {str(e)}")
            return total_result
    
    def _execute_step5_2_with_browser_restart(self, account_id: str, initial_browser_id: str, quantity: int, chunk_size: int = 20, account_info: Dict = None) -> Dict:
        """브라우저 재시작 방식으로 5_2단계 실행"""
        account_logger = self.account_loggers.get(account_id)
        if not account_logger:
            account_logger = AccountLogger(account_id, self.start_time)
            self.account_loggers[account_id] = account_logger
        
        total_result = {
            'success': False,
            'processed': 0,
            'failed': 0,
            'errors': [],
            'chunks_completed': 0,
            'total_chunks': 0
        }
        
        try:
            total_chunks = (quantity + chunk_size - 1) // chunk_size
            total_result['total_chunks'] = total_chunks
            
            account_logger.info(f"브라우저 재시작 방식으로 5_2단계 작업 시작")
            account_logger.info(f"총 수량: {quantity}, 청크 크기: {chunk_size}, 총 청크 수: {total_chunks}")
            
            current_browser_id = initial_browser_id
            
            for chunk_idx in range(total_chunks):
                start_idx = chunk_idx * chunk_size
                end_idx = min(start_idx + chunk_size, quantity)
                current_chunk_size = end_idx - start_idx
                
                account_logger.info(f"===== 청크 {chunk_idx + 1}/{total_chunks} 시작 (상품 {start_idx + 1}-{end_idx}) =====")
                
                try:
                    driver = self.browser_manager.get_driver(current_browser_id)
                    step_core = Step5_2Core(driver)
                    
                    chunk_result = step_core.execute_step5_2(current_chunk_size, account_info)
                    
                    total_result['processed'] += chunk_result['processed']
                    total_result['failed'] += chunk_result['failed']
                    total_result['errors'].extend(chunk_result['errors'])
                    total_result['chunks_completed'] += 1
                    
                    account_logger.info(f"청크 {chunk_idx + 1} 완료: 처리 {chunk_result['processed']}개, 실패 {chunk_result['failed']}개")
                    
                    if chunk_result.get('should_stop_batch', False):
                        account_logger.warning(f"⚠️ 청크 {chunk_idx + 1}에서 비그룹상품이 0개가 되어 후속 배치분할을 중단합니다.")
                        account_logger.info(f"총 {chunk_idx + 1}/{total_chunks} 청크 완료 후 중단")
                        self.browser_manager.close_browser(current_browser_id)
                        break
                    
                    if chunk_idx < total_chunks - 1:
                        account_logger.info(f"청크 {chunk_idx + 1} 완료 후 브라우저 재시작")
                        
                        self.browser_manager.close_browser(current_browser_id)
                        
                        import time
                        time.sleep(2)
                        
                        new_browser_id = self.browser_manager.create_browser(account_id)
                        real_account_id = get_real_account_id(account_id)
                        email, password = self.account_manager.get_account_credentials(real_account_id)
                        login_success = self.browser_manager.login_browser(new_browser_id, email, password)
                        
                        if not login_success:
                            raise Exception(f"청크 {chunk_idx + 1} 후 재로그인 실패")
                        
                        current_browser_id = new_browser_id
                        account_logger.info(f"브라우저 재시작 및 로그인 완료: {current_browser_id}")
                        
                        time.sleep(3)
                    else:
                        self.browser_manager.close_browser(current_browser_id)
                        
                except Exception as chunk_error:
                    account_logger.error(f"청크 {chunk_idx + 1} 실행 중 오류: {chunk_error}")
                    total_result['errors'].append(f"청크 {chunk_idx + 1}: {str(chunk_error)}")
            
            if total_result['processed'] > 0:
                total_result['success'] = True
                
            account_logger.info(f"브라우저 재시작 방식 5_2단계 작업 완료")
            account_logger.info(f"총 처리: {total_result['processed']}개, 총 실패: {total_result['failed']}개")
            account_logger.info(f"완료된 청크: {total_result['chunks_completed']}/{total_result['total_chunks']}")
            
            return total_result
            
        except Exception as e:
            account_logger.error(f"브라우저 재시작 방식 5_2단계 작업 중 전체 오류: {e}")
            total_result['errors'].append(f"전체 작업 오류: {str(e)}")
            return total_result
    
    def _execute_step5_3_with_browser_restart(self, account_id: str, initial_browser_id: str, quantity: int, chunk_size: int = 20, account_info: Dict = None) -> Dict:
        """브라우저 재시작 방식으로 5_3단계 실행"""
        account_logger = self.account_loggers.get(account_id)
        if not account_logger:
            account_logger = AccountLogger(account_id, self.start_time)
            self.account_loggers[account_id] = account_logger
        
        total_result = {
            'success': False,
            'processed': 0,
            'failed': 0,
            'errors': [],
            'chunks_completed': 0,
            'total_chunks': 0
        }
        
        try:
            total_chunks = (quantity + chunk_size - 1) // chunk_size
            total_result['total_chunks'] = total_chunks
            
            account_logger.info(f"브라우저 재시작 방식으로 5_3단계 작업 시작")
            account_logger.info(f"총 수량: {quantity}, 청크 크기: {chunk_size}, 총 청크 수: {total_chunks}")
            
            current_browser_id = initial_browser_id
            
            for chunk_idx in range(total_chunks):
                start_idx = chunk_idx * chunk_size
                end_idx = min(start_idx + chunk_size, quantity)
                current_chunk_size = end_idx - start_idx
                
                account_logger.info(f"===== 청크 {chunk_idx + 1}/{total_chunks} 시작 (상품 {start_idx + 1}-{end_idx}) =====")
                
                try:
                    driver = self.browser_manager.get_driver(current_browser_id)
                    step_core = Step5_3Core(driver)
                    
                    chunk_result = step_core.execute_step5_3(current_chunk_size, account_info)
                    
                    total_result['processed'] += chunk_result['processed']
                    total_result['failed'] += chunk_result['failed']
                    total_result['errors'].extend(chunk_result['errors'])
                    total_result['chunks_completed'] += 1
                    
                    account_logger.info(f"청크 {chunk_idx + 1} 완료: 처리 {chunk_result['processed']}개, 실패 {chunk_result['failed']}개")
                    
                    if chunk_result.get('should_stop_batch', False):
                        account_logger.warning(f"⚠️ 청크 {chunk_idx + 1}에서 비그룹상품이 0개가 되어 후속 배치분할을 중단합니다.")
                        account_logger.info(f"총 {chunk_idx + 1}/{total_chunks} 청크 완료 후 중단")
                        self.browser_manager.close_browser(current_browser_id)
                        break
                    
                    if chunk_idx < total_chunks - 1:
                        account_logger.info(f"청크 {chunk_idx + 1} 완료 후 브라우저 재시작")
                        
                        self.browser_manager.close_browser(current_browser_id)
                        
                        import time
                        time.sleep(2)
                        
                        new_browser_id = self.browser_manager.create_browser(account_id)
                        real_account_id = get_real_account_id(account_id)
                        email, password = self.account_manager.get_account_credentials(real_account_id)
                        login_success = self.browser_manager.login_browser(new_browser_id, email, password)
                        
                        if not login_success:
                            raise Exception(f"청크 {chunk_idx + 1} 후 재로그인 실패")
                        
                        current_browser_id = new_browser_id
                        account_logger.info(f"브라우저 재시작 및 로그인 완료: {current_browser_id}")
                        
                        time.sleep(3)
                    else:
                        self.browser_manager.close_browser(current_browser_id)
                        
                except Exception as chunk_error:
                    account_logger.error(f"청크 {chunk_idx + 1} 실행 중 오류: {chunk_error}")
                    total_result['errors'].append(f"청크 {chunk_idx + 1}: {str(chunk_error)}")
            
            if total_result['processed'] > 0:
                total_result['success'] = True
                
            account_logger.info(f"브라우저 재시작 방식 5_3단계 작업 완료")
            account_logger.info(f"총 처리: {total_result['processed']}개, 총 실패: {total_result['failed']}개")
            account_logger.info(f"완료된 청크: {total_result['chunks_completed']}/{total_result['total_chunks']}")
            
            return total_result
            
        except Exception as e:
            account_logger.error(f"브라우저 재시작 방식 5_3단계 작업 중 전체 오류: {e}")
            total_result['errors'].append(f"전체 작업 오류: {str(e)}")
            return total_result
    
    def run_multi_step(self, account: str, steps: List[int], 
                      quantities: List[int], concurrent: bool = False) -> Dict:
        """
        다중 단계 배치 실행
        
        Args:
            account: 계정 ID
            steps: 실행할 단계 목록
            quantities: 각 단계별 수량
            concurrent: 동시 실행 여부 (False면 순차 실행)
            
        Returns:
            Dict: 실행 결과
        """
        task_id = f"multi_step_{account}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"다중 단계 배치 시작 - 계정: {account}, 단계: {steps}")
        
        if len(steps) != len(quantities):
            raise ValueError("단계 수와 수량 수가 일치하지 않습니다.")
        
        results = {
            'task_id': task_id,
            'success': True,
            'start_time': datetime.now(),
            'results': {}
        }
        
        try:
            if concurrent:
                # 동시 실행 (각 단계를 별도 브라우저에서)
                return self._run_concurrent_multi_step(task_id, account, steps, quantities)
            else:
                # 순차 실행 (하나의 브라우저에서)
                return self._run_sequential_multi_step(task_id, account, steps, quantities)
        
        except Exception as e:
            logger.error(f"다중 단계 배치 실행 중 오류: {e}")
            results['success'] = False
            results['error'] = str(e)
            return results
    
    def run_from_config(self, config_name: str) -> Dict:
        """
        설정 파일 기반 배치 실행
        
        Args:
            config_name: 설정 이름
            
        Returns:
            Dict: 실행 결과
        """
        # 향후 구현
        pass
    
    def generate_summary_report(self) -> str:
        """
        모든 배치 작업의 종합 보고서 생성
        
        Returns:
            str: 보고서 파일 경로
        """
        if not self.batch_results:
            logger.warning("생성할 배치 결과가 없습니다.")
            return ""
        
        summary_file = self.report_generator.generate_summary_report(self.batch_results)
        logger.info(f"종합 보고서 생성 완료: {summary_file}")
        return summary_file
    
    def get_task_status(self, task_id: str) -> Dict:
        """
        작업 상태 조회
        
        Args:
            task_id: 작업 ID
            
        Returns:
            Dict: 작업 상태
        """
        if task_id in self.task_results:
            return self.task_results[task_id]
        elif task_id in self.running_tasks:
            return {
                'task_id': task_id,
                'status': 'running',
                'start_time': self.running_tasks[task_id]
            }
        else:
            return {
                'task_id': task_id,
                'status': 'not_found'
            }
    
    def _execute_step31_with_browser_restart(self, account_id: str, initial_browser_id: str, provider_codes: List[str], chunk_size: int = 2, account_info: Dict = None) -> Dict:
        """
        브라우저 재시작 방식으로 31단계 실행
        
        Args:
            account_id: 계정 ID
            initial_browser_id: 초기 브라우저 ID
            provider_codes: 처리할 키워드(provider_code) 목록
            chunk_size: 청크 크기 (기본값: 2)
            account_info: 계정 정보
            
        Returns:
            Dict: 실행 결과
        """
        account_logger = self.account_loggers.get(account_id)
        if not account_logger:
            account_logger = AccountLogger(account_id, self.start_time)
            self.account_loggers[account_id] = account_logger
        
        total_result = {
            'success': False,
            'processed_keywords': 0,
            'failed_keywords': 0,
            'total_products_processed': 0,
            'errors': [],
            'completed_keywords': [],
            'failed_keywords_list': [],
            'chunks_completed': 0,
            'total_chunks': 0
        }
        
        try:
            # 총 청크 수 계산
            total_chunks = (len(provider_codes) + chunk_size - 1) // chunk_size
            total_result['total_chunks'] = total_chunks
            
            account_logger.info(f"브라우저 재시작 방식으로 31단계 작업 시작")
            account_logger.info(f"총 키워드 수: {len(provider_codes)}, 청크 크기: {chunk_size}, 총 청크 수: {total_chunks}")
            
            current_browser_id = initial_browser_id
            
            for chunk_idx in range(total_chunks):
                start_idx = chunk_idx * chunk_size
                end_idx = min(start_idx + chunk_size, len(provider_codes))
                chunk_provider_codes = provider_codes[start_idx:end_idx]
                
                account_logger.info(f"===== 청크 {chunk_idx + 1}/{total_chunks} 시작 (키워드 {start_idx + 1}-{end_idx}) =====")
                account_logger.info(f"처리할 키워드: {chunk_provider_codes}")
                
                try:
                    # 현재 청크 실행
                    driver = self.browser_manager.get_driver(current_browser_id)
                    
                    # Step3_1Core 동적 임포트
                    from core.steps.step3_1_core import Step3_1Core
                    step_core = Step3_1Core(driver)
                    
                    chunk_result = step_core.execute_step3_1(chunk_provider_codes, account_info)
                    
                    # 결과 누적
                    total_result['processed_keywords'] += chunk_result.get('processed_keywords', 0)
                    total_result['failed_keywords'] += chunk_result.get('failed_keywords', 0)
                    total_result['total_products_processed'] += chunk_result.get('total_products_processed', 0)
                    total_result['errors'].extend(chunk_result.get('errors', []))
                    total_result['completed_keywords'].extend(chunk_result.get('completed_keywords', []))
                    total_result['failed_keywords_list'].extend(chunk_result.get('failed_keywords_list', []))
                    total_result['chunks_completed'] += 1
                    
                    account_logger.info(f"청크 {chunk_idx + 1} 완료: 처리 키워드 {chunk_result.get('processed_keywords', 0)}개, 실패 키워드 {chunk_result.get('failed_keywords', 0)}개")
                    
                    # 배치분할 중단 플래그 확인
                    if chunk_result.get('should_stop_batch', False):
                        account_logger.warning(f"청크 {chunk_idx + 1}에서 배치분할 중단 플래그 감지 - 후속 청크 처리를 중단합니다")
                        break
                    
                    # 마지막 청크가 아니면 브라우저 재시작
                    if chunk_idx < total_chunks - 1:
                        account_logger.info(f"청크 {chunk_idx + 1} 완료 후 브라우저 재시작")
                        
                        # 기존 브라우저 종료
                        try:
                            self.browser_manager.close_browser(current_browser_id)
                            account_logger.info(f"기존 브라우저 {current_browser_id} 종료 완료")
                        except Exception as close_error:
                            account_logger.warning(f"기존 브라우저 종료 중 오류: {close_error}")
                        
                        # 새 브라우저 생성
                        import time
                        time.sleep(3)  # 브라우저 종료 후 대기
                        
                        new_browser_id = f"{account_id}_browser_chunk_{chunk_idx + 2}"
                        current_browser_id = self.browser_manager.create_browser(
                            browser_id=new_browser_id,
                            headless=self.config.get('browser', {}).get('headless', False)
                        )
                        
                        if not current_browser_id:
                            raise Exception(f"청크 {chunk_idx + 2}용 브라우저 생성 실패")
                        
                        account_logger.info(f"새 브라우저 생성 완료: {current_browser_id}")
                        
                        # 새 브라우저에서 로그인
                        real_account_id = get_real_account_id(account_id)
                        email, password = self.account_manager.get_account_credentials(real_account_id)
                        
                        login_success = self.browser_manager.login_browser(current_browser_id, email, password)
                        if not login_success:
                            raise Exception(f"청크 {chunk_idx + 2}용 브라우저 로그인 실패")
                        
                        account_logger.info(f"새 브라우저 로그인 완료")
                        time.sleep(2)  # 로그인 후 안정화 대기
                
                except Exception as chunk_error:
                    account_logger.error(f"청크 {chunk_idx + 1} 실행 중 오류: {chunk_error}")
                    total_result['errors'].append(f"청크 {chunk_idx + 1}: {str(chunk_error)}")
                    # 청크 실패 시에도 다음 청크 계속 진행
                    continue
            
            # 전체 성공 여부 결정
            total_result['success'] = total_result['chunks_completed'] > 0
            
            # 결과 매핑 (기존 Step3_1Core 결과 형식에 맞춤)
            total_result['processed'] = total_result['processed_keywords']
            total_result['failed'] = total_result['failed_keywords']
            
            account_logger.info(f"31단계 브라우저 재시작 방식 완료")
            account_logger.info(f"총 처리 키워드: {total_result['processed_keywords']}개")
            account_logger.info(f"총 실패 키워드: {total_result['failed_keywords']}개")
            account_logger.info(f"완료된 청크: {total_result['chunks_completed']}/{total_result['total_chunks']}개")
            
            return total_result
            
        except Exception as e:
            account_logger.error(f"31단계 브라우저 재시작 방식 실행 중 오류: {e}")
            total_result['success'] = False
            total_result['errors'].append(str(e))
            return total_result
    
    def _execute_step32_with_browser_restart(self, account_id, browser_id, provider_codes, chunk_size, account_info):
        """32단계를 청크 단위로 브라우저 재시작하며 실행"""
        account_logger = self.account_loggers.get(account_id)
        if not account_logger:
            account_logger = AccountLogger(account_id, self.start_time)
            self.account_loggers[account_id] = account_logger
        
        # 총 청크 수 계산
        total_chunks = math.ceil(len(provider_codes) / chunk_size)
        account_logger.info(f"총 {len(provider_codes)}개 키워드를 {total_chunks}개 청크로 분할하여 처리 (청크 크기: {chunk_size})")
        
        accumulated_result = {
            'success': True,
            'processed': 0,
            'failed': 0,
            'errors': []
        }
        
        for chunk_index in range(total_chunks):
            start_idx = chunk_index * chunk_size
            end_idx = min(start_idx + chunk_size, len(provider_codes))
            current_chunk = provider_codes[start_idx:end_idx]
            
            account_logger.info(f"청크 {chunk_index + 1}/{total_chunks} 처리 시작 (키워드 {len(current_chunk)}개)")
            
            try:
                # 브라우저 드라이버 가져오기
                driver = self.browser_manager.get_driver(browser_id)
                
                # Step3_2Core 동적 임포트 및 실행
                from core.steps.step3_2_core import Step3_2Core
                step_core = Step3_2Core(driver)
                
                # 현재 청크 실행
                chunk_result = step_core.execute_step3_2(current_chunk, account_info)
                
                # 결과 누적
                if chunk_result.get('success', False):
                    accumulated_result['processed'] += chunk_result.get('processed', 0)
                    accumulated_result['failed'] += chunk_result.get('failed', 0)
                else:
                    accumulated_result['success'] = False
                    if 'error' in chunk_result:
                        accumulated_result['errors'].append(chunk_result['error'])
                
                account_logger.info(f"청크 {chunk_index + 1}/{total_chunks} 완료 - 처리: {chunk_result.get('processed', 0)}, 실패: {chunk_result.get('failed', 0)}")
                
                # 배치 분할 중단 플래그 확인
                if hasattr(self, 'stop_batch_splitting') and self.stop_batch_splitting:
                    account_logger.warning(f"배치 분할 중단 플래그가 설정되어 청크 {chunk_index + 1}에서 중단합니다")
                    break
                
                # 마지막 청크가 아니면 브라우저 재시작
                if chunk_index < total_chunks - 1:
                    account_logger.info(f"청크 {chunk_index + 1} 완료 후 브라우저 재시작")
                    
                    # 기존 브라우저 종료
                    try:
                        self.browser_manager.close_browser(browser_id)
                        account_logger.info(f"기존 브라우저 {browser_id} 종료 완료")
                    except Exception as close_error:
                        account_logger.warning(f"기존 브라우저 종료 중 오류: {close_error}")
                    
                    # 새 브라우저 생성
                    import time
                    time.sleep(3)  # 브라우저 종료 후 대기
                    
                    new_browser_id = f"{account_id}_browser_chunk_{chunk_index + 2}"
                    browser_id = self.browser_manager.create_browser(
                        browser_id=new_browser_id,
                        headless=self.config.get('browser', {}).get('headless', False)
                    )
                    
                    if not browser_id:
                        raise Exception(f"청크 {chunk_index + 2}용 브라우저 생성 실패")
                    
                    account_logger.info(f"새 브라우저 생성 완료: {browser_id}")
                    
                    # 새 브라우저에서 로그인
                    real_account_id = get_real_account_id(account_id)
                    email, password = self.account_manager.get_account_credentials(real_account_id)
                    
                    login_success = self.browser_manager.login_browser(browser_id, email, password)
                    if not login_success:
                        raise Exception(f"청크 {chunk_index + 2}용 브라우저 로그인 실패")
                    
                    account_logger.info(f"새 브라우저 로그인 완료")
                    time.sleep(2)  # 로그인 후 안정화 대기
                    
            except Exception as e:
                account_logger.error(f"청크 {chunk_index + 1} 처리 중 오류: {e}")
                accumulated_result['success'] = False
                accumulated_result['errors'].append(str(e))
                
                # 오류 발생 시에도 브라우저 재시작 시도
                if chunk_index < total_chunks - 1:
                    try:
                        # 기존 브라우저 종료
                        self.browser_manager.close_browser(browser_id)
                        account_logger.info(f"오류 후 기존 브라우저 {browser_id} 종료 완료")
                        
                        # 새 브라우저 생성
                        import time
                        time.sleep(3)  # 브라우저 종료 후 대기
                        
                        new_browser_id = f"{account_id}_browser_chunk_{chunk_index + 2}"
                        browser_id = self.browser_manager.create_browser(
                            browser_id=new_browser_id,
                            headless=self.config.get('browser', {}).get('headless', False)
                        )
                        
                        if browser_id:
                            # 새 브라우저에서 로그인
                            real_account_id = get_real_account_id(account_id)
                            email, password = self.account_manager.get_account_credentials(real_account_id)
                            
                            login_success = self.browser_manager.login_browser(browser_id, email, password)
                            if login_success:
                                account_logger.info(f"오류 후 새 브라우저 로그인 완료")
                                time.sleep(2)
                            else:
                                account_logger.error(f"오류 후 새 브라우저 로그인 실패")
                        else:
                            account_logger.error(f"오류 후 새 브라우저 생성 실패")
                            
                    except Exception as restart_error:
                        account_logger.error(f"브라우저 재시작 실패: {restart_error}")
        
        account_logger.info(f"32단계 청크 처리 완료 - 총 처리: {accumulated_result['processed']}, 총 실패: {accumulated_result['failed']}")
        return accumulated_result
    
    def _execute_step33_with_browser_restart(self, account_id, browser_id, provider_codes, chunk_size, account_info):
        """33단계를 청크 단위로 브라우저 재시작하며 실행"""
        account_logger = self.account_loggers.get(account_id)
        if not account_logger:
            account_logger = AccountLogger(account_id, self.start_time)
            self.account_loggers[account_id] = account_logger
        
        # 총 청크 수 계산
        total_chunks = math.ceil(len(provider_codes) / chunk_size)
        account_logger.info(f"총 {len(provider_codes)}개 키워드를 {total_chunks}개 청크로 분할하여 처리 (청크 크기: {chunk_size})")
        
        accumulated_result = {
            'success': True,
            'processed': 0,
            'failed': 0,
            'errors': []
        }
        
        for chunk_index in range(total_chunks):
            start_idx = chunk_index * chunk_size
            end_idx = min(start_idx + chunk_size, len(provider_codes))
            current_chunk = provider_codes[start_idx:end_idx]
            
            account_logger.info(f"청크 {chunk_index + 1}/{total_chunks} 처리 시작 (키워드 {len(current_chunk)}개)")
            
            try:
                # 브라우저 드라이버 가져오기
                driver = self.browser_manager.get_driver(browser_id)
                
                # Step3_3Core 동적 임포트 및 실행
                from core.steps.step3_3_core import Step3_3Core
                step_core = Step3_3Core(driver)
                
                # 현재 청크 실행
                chunk_result = step_core.execute_step3_3(current_chunk, account_info)
                
                # 결과 누적
                if chunk_result.get('success', False):
                    accumulated_result['processed'] += chunk_result.get('processed', 0)
                    accumulated_result['failed'] += chunk_result.get('failed', 0)
                else:
                    accumulated_result['success'] = False
                    if 'error' in chunk_result:
                        accumulated_result['errors'].append(chunk_result['error'])
                
                account_logger.info(f"청크 {chunk_index + 1}/{total_chunks} 완료 - 처리: {chunk_result.get('processed', 0)}, 실패: {chunk_result.get('failed', 0)}")
                
                # 배치 분할 중단 플래그 확인
                if hasattr(self, 'stop_batch_splitting') and self.stop_batch_splitting:
                    account_logger.warning(f"배치 분할 중단 플래그가 설정되어 청크 {chunk_index + 1}에서 중단합니다")
                    break
                
                # 마지막 청크가 아니면 브라우저 재시작
                if chunk_index < total_chunks - 1:
                    account_logger.info(f"청크 {chunk_index + 1} 완료 후 브라우저 재시작")
                    
                    # 기존 브라우저 종료
                    try:
                        self.browser_manager.close_browser(browser_id)
                        account_logger.info(f"기존 브라우저 {browser_id} 종료 완료")
                    except Exception as close_error:
                        account_logger.warning(f"기존 브라우저 종료 중 오류: {close_error}")
                    
                    # 새 브라우저 생성
                    import time
                    time.sleep(3)  # 브라우저 종료 후 대기
                    
                    new_browser_id = f"{account_id}_browser_chunk_{chunk_index + 2}"
                    browser_id = self.browser_manager.create_browser(
                        browser_id=new_browser_id,
                        headless=self.config.get('browser', {}).get('headless', False)
                    )
                    
                    if not browser_id:
                        raise Exception(f"청크 {chunk_index + 2}용 브라우저 생성 실패")
                    
                    account_logger.info(f"새 브라우저 생성 완료: {browser_id}")
                    
                    # 새 브라우저에서 로그인
                    real_account_id = get_real_account_id(account_id)
                    email, password = self.account_manager.get_account_credentials(real_account_id)
                    
                    login_success = self.browser_manager.login_browser(browser_id, email, password)
                    if not login_success:
                        raise Exception(f"청크 {chunk_index + 2}용 브라우저 로그인 실패")
                    
                    account_logger.info(f"새 브라우저 로그인 완료")
                    time.sleep(2)  # 로그인 후 안정화 대기
                    
            except Exception as e:
                account_logger.error(f"청크 {chunk_index + 1} 처리 중 오류: {e}")
                accumulated_result['success'] = False
                accumulated_result['errors'].append(str(e))
                
                # 오류 발생 시에도 브라우저 재시작 시도
                if chunk_index < total_chunks - 1:
                    try:
                        # 기존 브라우저 종료
                        self.browser_manager.close_browser(browser_id)
                        account_logger.info(f"오류 후 기존 브라우저 {browser_id} 종료 완료")
                        
                        # 새 브라우저 생성
                        import time
                        time.sleep(3)  # 브라우저 종료 후 대기
                        
                        new_browser_id = f"{account_id}_browser_chunk_{chunk_index + 2}"
                        browser_id = self.browser_manager.create_browser(
                            browser_id=new_browser_id,
                            headless=self.config.get('browser', {}).get('headless', False)
                        )
                        
                        if browser_id:
                            # 새 브라우저에서 로그인
                            real_account_id = get_real_account_id(account_id)
                            email, password = self.account_manager.get_account_credentials(real_account_id)
                            
                            login_success = self.browser_manager.login_browser(browser_id, email, password)
                            if login_success:
                                account_logger.info(f"오류 후 새 브라우저 로그인 완료")
                                time.sleep(2)
                            else:
                                account_logger.error(f"오류 후 새 브라우저 로그인 실패")
                        else:
                            account_logger.error(f"오류 후 새 브라우저 생성 실패")
                            
                    except Exception as restart_error:
                        account_logger.error(f"브라우저 재시작 실패: {restart_error}")
        
        account_logger.info(f"33단계 청크 처리 완료 - 총 처리: {accumulated_result['processed']}, 총 실패: {accumulated_result['failed']}")
        return accumulated_result
    
    def _execute_step21_with_browser_restart(self, account_id, browser_id, provider_codes, chunk_size, account_info):
        """21단계를 청크 단위로 브라우저 재시작하며 실행"""
        account_logger = self.account_loggers.get(account_id)
        if not account_logger:
            account_logger = AccountLogger(account_id, self.start_time)
            self.account_loggers[account_id] = account_logger
        
        # 총 청크 수 계산
        total_chunks = math.ceil(len(provider_codes) / chunk_size)
        account_logger.info(f"총 {len(provider_codes)}개 키워드를 {total_chunks}개 청크로 분할하여 처리 (청크 크기: {chunk_size})")
        
        accumulated_result = {
            'success': True,
            'processed': 0,
            'failed': 0,
            'errors': []
        }
        
        for chunk_index in range(total_chunks):
            start_idx = chunk_index * chunk_size
            end_idx = min(start_idx + chunk_size, len(provider_codes))
            current_chunk = provider_codes[start_idx:end_idx]
            
            account_logger.info(f"청크 {chunk_index + 1}/{total_chunks} 처리 시작 (키워드 {len(current_chunk)}개)")
            
            try:
                # 브라우저 드라이버 가져오기
                driver = self.browser_manager.get_driver(browser_id)
                
                # Step2_1Core 동적 임포트 및 실행
                from core.steps.step2_1_core import Step2_1Core
                step_core = Step2_1Core(driver)
                
                # 현재 청크 실행
                chunk_result = step_core.execute_step2_1(current_chunk, account_info)
                
                # 결과 누적
                if chunk_result.get('success', False):
                    accumulated_result['processed'] += chunk_result.get('processed', 0)
                    accumulated_result['failed'] += chunk_result.get('failed', 0)
                else:
                    accumulated_result['success'] = False
                    if 'error' in chunk_result:
                        accumulated_result['errors'].append(chunk_result['error'])
                
                account_logger.info(f"청크 {chunk_index + 1}/{total_chunks} 완료 - 처리: {chunk_result.get('processed', 0)}, 실패: {chunk_result.get('failed', 0)}")
                
                # 배치 분할 중단 플래그 확인
                if hasattr(self, 'stop_batch_splitting') and self.stop_batch_splitting:
                    account_logger.warning(f"배치 분할 중단 플래그가 설정되어 청크 {chunk_index + 1}에서 중단합니다")
                    break
                
                # 마지막 청크가 아니면 브라우저 재시작
                if chunk_index < total_chunks - 1:
                    account_logger.info(f"청크 {chunk_index + 1} 완료 후 브라우저 재시작")
                    
                    # 기존 브라우저 종료
                    try:
                        self.browser_manager.close_browser(browser_id)
                        account_logger.info(f"기존 브라우저 {browser_id} 종료 완료")
                    except Exception as close_error:
                        account_logger.warning(f"기존 브라우저 종료 중 오류: {close_error}")
                    
                    # 새 브라우저 생성
                    import time
                    time.sleep(3)  # 브라우저 종료 후 대기
                    
                    new_browser_id = f"{account_id}_browser_chunk_{chunk_index + 2}"
                    browser_id = self.browser_manager.create_browser(
                        browser_id=new_browser_id,
                        headless=self.config.get('browser', {}).get('headless', False)
                    )
                    
                    if not browser_id:
                        raise Exception(f"청크 {chunk_index + 2}용 브라우저 생성 실패")
                    
                    account_logger.info(f"새 브라우저 생성 완료: {browser_id}")
                    
                    # 새 브라우저에서 로그인
                    real_account_id = get_real_account_id(account_id)
                    email, password = self.account_manager.get_account_credentials(real_account_id)
                    
                    login_success = self.browser_manager.login_browser(browser_id, email, password)
                    if not login_success:
                        raise Exception(f"청크 {chunk_index + 2}용 브라우저 로그인 실패")
                    
                    account_logger.info(f"새 브라우저 로그인 완료")
                    time.sleep(2)  # 로그인 후 안정화 대기
                    
            except Exception as e:
                account_logger.error(f"청크 {chunk_index + 1} 처리 중 오류: {e}")
                accumulated_result['success'] = False
                accumulated_result['errors'].append(str(e))
                
                # 오류 발생 시에도 브라우저 재시작 시도
                if chunk_index < total_chunks - 1:
                    try:
                        # 기존 브라우저 종료
                        self.browser_manager.close_browser(browser_id)
                        account_logger.info(f"오류 후 기존 브라우저 {browser_id} 종료 완료")
                        
                        # 새 브라우저 생성
                        import time
                        time.sleep(3)  # 브라우저 종료 후 대기
                        
                        new_browser_id = f"{account_id}_browser_chunk_{chunk_index + 2}"
                        browser_id = self.browser_manager.create_browser(
                            browser_id=new_browser_id,
                            headless=self.config.get('browser', {}).get('headless', False)
                        )
                        
                        if browser_id:
                            # 새 브라우저에서 로그인
                            real_account_id = get_real_account_id(account_id)
                            email, password = self.account_manager.get_account_credentials(real_account_id)
                            
                            login_success = self.browser_manager.login_browser(browser_id, email, password)
                            if login_success:
                                account_logger.info(f"오류 후 새 브라우저 로그인 완료")
                                time.sleep(2)
                            else:
                                account_logger.error(f"오류 후 새 브라우저 로그인 실패")
                        else:
                            account_logger.error(f"오류 후 새 브라우저 생성 실패")
                            
                    except Exception as restart_error:
                        account_logger.error(f"브라우저 재시작 실패: {restart_error}")
        
        account_logger.info(f"21단계 청크 처리 완료 - 총 처리: {accumulated_result['processed']}, 총 실패: {accumulated_result['failed']}")
        return accumulated_result
    
    def _execute_step22_with_browser_restart(self, account_id, browser_id, provider_codes, chunk_size, account_info):
        """22단계를 청크 단위로 브라우저 재시작하며 실행"""
        account_logger = self.account_loggers.get(account_id)
        if not account_logger:
            account_logger = AccountLogger(account_id, self.start_time)
            self.account_loggers[account_id] = account_logger
        
        # 총 청크 수 계산
        total_chunks = math.ceil(len(provider_codes) / chunk_size)
        account_logger.info(f"총 {len(provider_codes)}개 키워드를 {total_chunks}개 청크로 분할하여 처리 (청크 크기: {chunk_size})")
        
        accumulated_result = {
            'success': True,
            'processed': 0,
            'failed': 0,
            'errors': []
        }
        
        for chunk_index in range(total_chunks):
            start_idx = chunk_index * chunk_size
            end_idx = min(start_idx + chunk_size, len(provider_codes))
            current_chunk = provider_codes[start_idx:end_idx]
            
            account_logger.info(f"청크 {chunk_index + 1}/{total_chunks} 처리 시작 (키워드 {len(current_chunk)}개)")
            
            try:
                # 브라우저 드라이버 가져오기
                driver = self.browser_manager.get_driver(browser_id)
                
                # Step2_2Core 동적 임포트 및 실행
                from core.steps.step2_2_core import Step2_2Core
                step_core = Step2_2Core(driver)
                
                # 현재 청크 실행
                chunk_result = step_core.execute_step2_2(current_chunk, account_info)
                
                # 결과 누적
                if chunk_result.get('success', False):
                    accumulated_result['processed'] += chunk_result.get('processed', 0)
                    accumulated_result['failed'] += chunk_result.get('failed', 0)
                else:
                    accumulated_result['success'] = False
                    if 'error' in chunk_result:
                        accumulated_result['errors'].append(chunk_result['error'])
                
                account_logger.info(f"청크 {chunk_index + 1}/{total_chunks} 완료 - 처리: {chunk_result.get('processed', 0)}, 실패: {chunk_result.get('failed', 0)}")
                
                # 배치 분할 중단 플래그 확인
                if hasattr(self, 'stop_batch_splitting') and self.stop_batch_splitting:
                    account_logger.warning(f"배치 분할 중단 플래그가 설정되어 청크 {chunk_index + 1}에서 중단합니다")
                    break
                
                # 마지막 청크가 아니면 브라우저 재시작
                if chunk_index < total_chunks - 1:
                    account_logger.info(f"청크 {chunk_index + 1} 완료 후 브라우저 재시작")
                    
                    # 기존 브라우저 종료
                    try:
                        self.browser_manager.close_browser(browser_id)
                        account_logger.info(f"기존 브라우저 {browser_id} 종료 완료")
                    except Exception as close_error:
                        account_logger.warning(f"기존 브라우저 종료 중 오류: {close_error}")
                    
                    # 새 브라우저 생성
                    import time
                    time.sleep(3)  # 브라우저 종료 후 대기
                    
                    new_browser_id = f"{account_id}_browser_chunk_{chunk_index + 2}"
                    browser_id = self.browser_manager.create_browser(
                        browser_id=new_browser_id,
                        headless=self.config.get('browser', {}).get('headless', False)
                    )
                    
                    if not browser_id:
                        raise Exception(f"청크 {chunk_index + 2}용 브라우저 생성 실패")
                    
                    account_logger.info(f"새 브라우저 생성 완료: {browser_id}")
                    
                    # 새 브라우저에서 로그인
                    real_account_id = get_real_account_id(account_id)
                    email, password = self.account_manager.get_account_credentials(real_account_id)
                    
                    login_success = self.browser_manager.login_browser(browser_id, email, password)
                    if not login_success:
                        raise Exception(f"청크 {chunk_index + 2}용 브라우저 로그인 실패")
                    
                    account_logger.info(f"새 브라우저 로그인 완료")
                    time.sleep(2)  # 로그인 후 안정화 대기
                    
            except Exception as e:
                account_logger.error(f"청크 {chunk_index + 1} 처리 중 오류: {e}")
                accumulated_result['success'] = False
                accumulated_result['errors'].append(str(e))
                
                # 오류 발생 시에도 브라우저 재시작 시도
                if chunk_index < total_chunks - 1:
                    try:
                        # 기존 브라우저 종료
                        self.browser_manager.close_browser(browser_id)
                        account_logger.info(f"오류 후 기존 브라우저 {browser_id} 종료 완료")
                        
                        # 새 브라우저 생성
                        import time
                        time.sleep(3)  # 브라우저 종료 후 대기
                        
                        new_browser_id = f"{account_id}_browser_chunk_{chunk_index + 2}"
                        browser_id = self.browser_manager.create_browser(
                            browser_id=new_browser_id,
                            headless=self.config.get('browser', {}).get('headless', False)
                        )
                        
                        if browser_id:
                            # 새 브라우저에서 로그인
                            real_account_id = get_real_account_id(account_id)
                            email, password = self.account_manager.get_account_credentials(real_account_id)
                            
                            login_success = self.browser_manager.login_browser(browser_id, email, password)
                            if login_success:
                                account_logger.info(f"오류 후 새 브라우저 로그인 완료")
                                time.sleep(2)
                            else:
                                account_logger.error(f"오류 후 새 브라우저 로그인 실패")
                        else:
                            account_logger.error(f"오류 후 새 브라우저 생성 실패")
                            
                    except Exception as restart_error:
                        account_logger.error(f"브라우저 재시작 실패: {restart_error}")
        
        account_logger.info(f"22단계 청크 처리 완료 - 총 처리: {accumulated_result['processed']}, 총 실패: {accumulated_result['failed']}")
        return accumulated_result
    
    def _execute_step23_with_browser_restart(self, account_id, browser_id, provider_codes, chunk_size, account_info):
        """23단계를 청크 단위로 브라우저 재시작하며 실행"""
        account_logger = self.account_loggers.get(account_id)
        if not account_logger:
            account_logger = AccountLogger(account_id, self.start_time)
            self.account_loggers[account_id] = account_logger
        
        # 총 청크 수 계산
        total_chunks = math.ceil(len(provider_codes) / chunk_size)
        account_logger.info(f"총 {len(provider_codes)}개 키워드를 {total_chunks}개 청크로 분할하여 처리 (청크 크기: {chunk_size})")
        
        accumulated_result = {
            'success': True,
            'processed': 0,
            'failed': 0,
            'errors': []
        }
        
        for chunk_index in range(total_chunks):
            start_idx = chunk_index * chunk_size
            end_idx = min(start_idx + chunk_size, len(provider_codes))
            current_chunk = provider_codes[start_idx:end_idx]
            
            account_logger.info(f"청크 {chunk_index + 1}/{total_chunks} 처리 시작 (키워드 {len(current_chunk)}개)")
            
            try:
                # 브라우저 드라이버 가져오기
                driver = self.browser_manager.get_driver(browser_id)
                
                # Step2_3Core 동적 임포트 및 실행
                from core.steps.step2_3_core import Step2_3Core
                step_core = Step2_3Core(driver)
                
                # 현재 청크 실행
                chunk_result = step_core.execute_step2_3(current_chunk, account_info)
                
                # 결과 누적
                if chunk_result.get('success', False):
                    accumulated_result['processed'] += chunk_result.get('processed', 0)
                    accumulated_result['failed'] += chunk_result.get('failed', 0)
                else:
                    accumulated_result['success'] = False
                    if 'error' in chunk_result:
                        accumulated_result['errors'].append(chunk_result['error'])
                
                account_logger.info(f"청크 {chunk_index + 1}/{total_chunks} 완료 - 처리: {chunk_result.get('processed', 0)}, 실패: {chunk_result.get('failed', 0)}")
                
                # 배치 분할 중단 플래그 확인
                if hasattr(self, 'stop_batch_splitting') and self.stop_batch_splitting:
                    account_logger.warning(f"배치 분할 중단 플래그가 설정되어 청크 {chunk_index + 1}에서 중단합니다")
                    break
                
                # 마지막 청크가 아니면 브라우저 재시작
                if chunk_index < total_chunks - 1:
                    account_logger.info(f"청크 {chunk_index + 1} 완료 후 브라우저 재시작")
                    
                    # 기존 브라우저 종료
                    try:
                        self.browser_manager.close_browser(browser_id)
                        account_logger.info(f"기존 브라우저 {browser_id} 종료 완료")
                    except Exception as close_error:
                        account_logger.warning(f"기존 브라우저 종료 중 오류: {close_error}")
                    
                    # 새 브라우저 생성
                    import time
                    time.sleep(3)  # 브라우저 종료 후 대기
                    
                    new_browser_id = f"{account_id}_browser_chunk_{chunk_index + 2}"
                    browser_id = self.browser_manager.create_browser(
                        browser_id=new_browser_id,
                        headless=self.config.get('browser', {}).get('headless', False)
                    )
                    
                    if not browser_id:
                        raise Exception(f"청크 {chunk_index + 2}용 브라우저 생성 실패")
                    
                    account_logger.info(f"새 브라우저 생성 완료: {browser_id}")
                    
                    # 새 브라우저에서 로그인
                    real_account_id = get_real_account_id(account_id)
                    email, password = self.account_manager.get_account_credentials(real_account_id)
                    
                    login_success = self.browser_manager.login_browser(browser_id, email, password)
                    if not login_success:
                        raise Exception(f"청크 {chunk_index + 2}용 브라우저 로그인 실패")
                    
                    account_logger.info(f"새 브라우저 로그인 완료")
                    time.sleep(2)  # 로그인 후 안정화 대기
                    
            except Exception as e:
                account_logger.error(f"청크 {chunk_index + 1} 처리 중 오류: {e}")
                accumulated_result['success'] = False
                accumulated_result['errors'].append(str(e))
                
                # 오류 발생 시에도 브라우저 재시작 시도
                if chunk_index < total_chunks - 1:
                    try:
                        # 기존 브라우저 종료
                        self.browser_manager.close_browser(browser_id)
                        account_logger.info(f"오류 후 기존 브라우저 {browser_id} 종료 완료")
                        
                        # 새 브라우저 생성
                        import time
                        time.sleep(3)  # 브라우저 종료 후 대기
                        
                        new_browser_id = f"{account_id}_browser_chunk_{chunk_index + 2}"
                        browser_id = self.browser_manager.create_browser(
                            browser_id=new_browser_id,
                            headless=self.config.get('browser', {}).get('headless', False)
                        )
                        
                        if browser_id:
                            # 새 브라우저에서 로그인
                            real_account_id = get_real_account_id(account_id)
                            email, password = self.account_manager.get_account_credentials(real_account_id)
                            
                            login_success = self.browser_manager.login_browser(browser_id, email, password)
                            if login_success:
                                account_logger.info(f"오류 후 새 브라우저 로그인 완료")
                                time.sleep(2)
                            else:
                                account_logger.error(f"오류 후 새 브라우저 로그인 실패")
                        else:
                            account_logger.error(f"오류 후 새 브라우저 생성 실패")
                            
                    except Exception as restart_error:
                        account_logger.error(f"브라우저 재시작 실패: {restart_error}")
        
        account_logger.info(f"23단계 청크 처리 완료 - 총 처리: {accumulated_result['processed']}, 총 실패: {accumulated_result['failed']}")
        return accumulated_result
    
    def stop_task(self, task_id: str) -> bool:
        """
        작업 중지
        
        Args:
            task_id: 작업 ID
            
        Returns:
            bool: 중지 성공 여부
        """
        # 향후 구현
        pass
    
    def get_execution_summary(self) -> Dict:
        """
        실행 요약 정보를 반환합니다.
        
        Returns:
            Dict: 실행 요약 정보
        """
        return {
            'total_accounts': len(self.account_manager.get_all_accounts()),
            'available_steps': list(range(1, 7)),  # 1-6단계
            'current_config': self.config,
            'browser_headless': self.browser_manager.headless if self.browser_manager else False
        }
    
    def get_status(self) -> Dict:
        """
        현재 배치 매니저 상태를 반환합니다.
        
        Returns:
            Dict: 상태 정보
        """
        try:
            accounts = self.account_manager.get_all_accounts() if self.account_manager else []
            return {
                'initialized': True,
                'account_count': len(accounts),
                'browser_manager_ready': self.browser_manager is not None,
                'config_loaded': self.config is not None,
                'available_steps': list(range(1, 7)),
                'headless_mode': self.browser_manager.headless if self.browser_manager else False,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"상태 조회 중 오류: {e}")
            return {
                'initialized': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def cleanup(self):
        """
        정리 작업
        """
        try:
            if self.executor:
                self.executor.shutdown(wait=True)
            
            self.browser_manager.cleanup()
            
            logger.info("배치 관리자 정리 완료")
        except Exception as e:
            logger.error(f"배치 관리자 정리 중 오류: {e}")

# 편의 함수들
def run_step1_for_accounts(accounts: List[str], quantity: int = 100, 
                          concurrent: bool = True) -> Dict:
    """
    1단계를 여러 계정에서 실행하는 편의 함수
    
    Args:
        accounts: 계정 ID 목록
        quantity: 수량
        concurrent: 동시 실행 여부
        
    Returns:
        Dict: 실행 결과
    """
    manager = BatchManager()
    try:
        return manager.run_single_step(1, accounts, quantity, concurrent)
    finally:
        manager.cleanup()

def run_all_steps_for_account(account: str, quantities: List[int] = None) -> Dict:
    """
    모든 단계를 하나의 계정에서 실행하는 편의 함수
    
    Args:
        account: 계정 ID
        quantities: 각 단계별 수량 (기본값: [100, 50, 30, 20, 10, 5])
        
    Returns:
        Dict: 실행 결과
    """
    if quantities is None:
        quantities = [100, 50, 30, 20, 10, 5]
    
    manager = BatchManager()
    try:
        return manager.run_multi_step(account, [1, 2, 3, 4, 5, 6], quantities)
    finally:
        manager.cleanup()

if __name__ == "__main__":
    # 테스트 코드
    print("배치 관리자 모듈 테스트")
    logger.info("배치 관리자 모듈이 로드되었습니다.")