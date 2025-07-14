# -*- coding: utf-8 -*-
"""
3단계_1_3 코어 로직 (서버1-3)
퍼센티 자동화 3단계 작업의 핵심 비즈니스 로직 - 서버1-3 전용
"""

import os
import sys
import time
import json
import logging
import traceback
from typing import Dict, List, Optional, Union, Tuple

# 루트 디렉토리를 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 기존 모듈들 임포트 (루트에서)
try:
    from product_editor_core3 import ProductEditorCore3
except ImportError:
    pass
from browser_core import BrowserCore
from login_percenty import PercentyLogin
from menu_clicks import MenuClicks
from coordinates.coordinates_all import MENU
from timesleep import DELAY_STANDARD, DELAY_SHORT
# from human_delay import HumanLikeDelay
from ui_elements import UI_ELEMENTS
from click_utils import smart_click

# 공통 함수들 임포트
from core.common.modal_handler import handle_post_login_modals, hide_channel_talk, close_modal_dialogs
from core.common.ui_handler import periodic_ui_cleanup, ensure_clean_ui_before_action
from core.common.batch_limit_manager import BatchLimitManager
from product_editor_screen import open_product_editor_screen

logger = logging.getLogger(__name__)

class Step3_1_3Core:
    """
    3단계_1_3 작업의 핵심 로직을 담당하는 클래스 (서버1-3 전용)
    등록상품에서 키워드별 상품 수정 및 그룹 이동 작업 수행
    """
    
    def __init__(self, driver=None, server_name="서버1-3", restart_browser_callback=None, step3_product_limit=None, step3_image_limit=None):
        """
        초기화
        
        Args:
            driver: Selenium WebDriver 인스턴스
            server_name: 서버 이름 (기본값: "서버1")
            restart_browser_callback: 브라우저 재시작 콜백 함수
            step3_product_limit: 3단계 상품 수량 제한 (기본값: 20)
            step3_image_limit: 3단계 이미지 번역 수량 제한 (기본값: 2000)
        """
        self.driver = driver
        self.server_name = server_name
        self.restart_browser_callback = restart_browser_callback
        self.step3_product_limit = step3_product_limit or 20  # None이면 기본값 20 사용
        self.step3_image_limit = step3_image_limit or 2000
        self.browser_core = None
        self.login_manager = None
        self.menu_clicks = None
        # self.delay = HumanLikeDelay()
        self.product_editor = None
        
        # 배치 제한 관리자 초기화
        self.batch_limit_manager = BatchLimitManager(
            product_limit=self.step3_product_limit,
            image_limit=self.step3_image_limit
        )
        
        logger.info(f"Step3_1_3Core 초기화 - 상품 제한: {self.step3_product_limit}, 이미지 제한: {self.step3_image_limit}")
        
        if driver:
            self.setup_managers()
    
    def setup_managers(self):
        """관리자 객체들 설정"""
        try:
            logger.info("BrowserCore 인스턴스 생성 시작")
            # BrowserCore는 driver를 매개변수로 받지 않으므로 인스턴스만 생성
            self.browser_core = BrowserCore()
            # driver를 별도로 설정
            self.browser_core.driver = self.driver
            logger.info("BrowserCore 인스턴스 생성 완료")
            
            logger.info("PercentyLogin 인스턴스 생성 시작")
            # 기존 driver를 전달하여 새로운 브라우저 생성 방지
            self.login_manager = PercentyLogin(driver=self.driver)
            logger.info("PercentyLogin 인스턴스 생성 완료")
            
            logger.info("MenuClicks 인스턴스 생성 시작")
            self.menu_clicks = MenuClicks(self.driver)
            logger.info("MenuClicks 인스턴스 생성 완료")
            
            logger.info("ProductEditorCore3 인스턴스 생성 시작")
            self.product_editor = ProductEditorCore3(self.driver, step3_product_limit=self.step3_product_limit, step3_image_limit=self.step3_image_limit)
            logger.info("ProductEditorCore3 인스턴스 생성 완료")
            
            logger.info(f"3단계_1_3 코어 관리자 객체들이 설정되었습니다. (서버: {self.server_name})")
        except Exception as e:
            logger.error(f"관리자 객체 설정 중 오류: {e}")
            logger.error(f"오류 상세: {traceback.format_exc()}")
            raise
    
    def update_driver_references(self, new_driver):
        """모든 관리자 객체들의 드라이버 참조 업데이트"""
        try:
            logger.info(f"드라이버 참조 업데이트 시작 - {self.server_name}")
            
            # 새 드라이버 연결 상태 검증
            try:
                new_driver.current_url
                logger.info(f"새 드라이버 연결 상태 정상 확인 - {self.server_name}")
            except Exception as e:
                logger.error(f"새 드라이버 연결 상태 오류 - {self.server_name}: {e}")
                raise
            
            # 메인 드라이버 참조 업데이트
            self.driver = new_driver
            
            # 각 관리자 객체의 드라이버 참조 업데이트
            if self.browser_core:
                self.browser_core.driver = new_driver
                logger.info("BrowserCore 드라이버 참조 업데이트 완료")
            
            if self.login_manager:
                self.login_manager.driver = new_driver
                logger.info("PercentyLogin 드라이버 참조 업데이트 완료")
            
            if self.menu_clicks:
                self.menu_clicks.driver = new_driver
                logger.info("MenuClicks 드라이버 참조 업데이트 완료")
            
            if self.product_editor:
                if hasattr(self.product_editor, 'update_driver_references'):
                    self.product_editor.update_driver_references(new_driver)
                else:
                    self.product_editor.driver = new_driver
                logger.info("ProductEditorCore3 드라이버 참조 업데이트 완료")
            
            # 업데이트 후 드라이버 연결 상태 재검증
            try:
                self.driver.current_url
                logger.info(f"업데이트된 드라이버 연결 상태 정상 확인 - {self.server_name}")
            except Exception as e:
                logger.error(f"업데이트된 드라이버 연결 상태 오류 - {self.server_name}: {e}")
                raise
            
            logger.info(f"모든 관리자 객체의 드라이버 참조 업데이트 완료 - {self.server_name}")
            
        except Exception as e:
            logger.error(f"드라이버 참조 업데이트 중 오류: {e} - {self.server_name}")
            logger.error(f"오류 상세: {traceback.format_exc()}")
            raise
    
    def execute_step3_1_3_with_browser_restart(self, provider_codes: List[str], chunk_size: int = 2, account_info: Dict = None) -> Dict:
        """
        3단계_1_3 작업 실행 (브라우저 재시작 방식)
        메모리 사용량 최적화를 위해 지정된 키워드 수마다 브라우저를 재시작
        
        Args:
            provider_codes: 처리할 키워드(provider_code) 목록
            chunk_size: 브라우저 재시작 간격 (기본값: 5)
            account_info: 계정 정보 (엑셀 파일에서 읽은 계정 정보)
            
        Returns:
            Dict: 실행 결과
        """
        total_result = {
            'success': False,
            'processed_keywords': 0,
            'failed_keywords': 0,
            'total_products_processed': 0,
            'errors': [],
            'chunks_completed': 0,
            'total_chunks': 0,
            'completed_keywords': [],
            'failed_keywords_list': []
        }
        
        try:
            # 총 청크 수 계산
            total_keywords = len(provider_codes)
            total_chunks = (total_keywords + chunk_size - 1) // chunk_size
            total_result['total_chunks'] = total_chunks
            
            logger.info(f"3단계_1_3 배치 작업 시작 (서버: {self.server_name}) - 총 {total_keywords}개 키워드를 {total_chunks}개 청크로 처리")
            
            # 진행 상황 저장을 위한 파일 경로
            progress_file = self._get_progress_file_path(account_info)
            
            # 기존 진행 상황 복구 (누적 카운터 포함)
            remaining_keywords, accumulated_products, accumulated_images = self._resume_from_progress(provider_codes, progress_file)
            if remaining_keywords != provider_codes:
                logger.info(f"진행 상황 복구됨 - 남은 키워드: {len(remaining_keywords)}개")
                provider_codes = remaining_keywords
                total_keywords = len(provider_codes)
                total_chunks = (total_keywords + chunk_size - 1) // chunk_size
                total_result['total_chunks'] = total_chunks
                
            # 배치 제한 관리자 상태 복구
            self.batch_limit_manager.set_accumulated_counts(accumulated_products, accumulated_images)
            self.batch_limit_manager.log_current_status("진행 상황 복구")
            
            # 이미 제한에 도달한 경우 조기 종료
            if self.batch_limit_manager.is_batch_limit_reached():
                logger.info("배치 제한에 이미 도달함 - 작업 종료")
                total_result['success'] = True
                total_result['limit_reached'] = True
                return total_result
                
            # ProductEditorCore3에 누적 카운터 설정
            if self.product_editor:
                self.product_editor.total_translated_images = accumulated_images
                self.product_editor.current_product_translated_images = accumulated_images
                logger.info(f"ProductEditorCore3에 누적 카운터 설정: 상품 {accumulated_products}개, 이미지 번역 {accumulated_images}개")
            
            # 키워드를 청크로 분할
            keyword_chunks = [provider_codes[i:i + chunk_size] for i in range(0, total_keywords, chunk_size)]
            
            for chunk_idx, keyword_chunk in enumerate(keyword_chunks):
                logger.info(f"청크 {chunk_idx + 1}/{total_chunks} 시작 - {len(keyword_chunk)}개 키워드 처리: {keyword_chunk}")
                
                try:
                    # 청크 실행
                    chunk_result = self.execute_step3_1_3(keyword_chunk, account_info)
                    
                    # 결과 누적
                    total_result['processed_keywords'] += chunk_result.get('processed_keywords', 0)
                    total_result['failed_keywords'] += chunk_result.get('failed_keywords', 0)
                    total_result['total_products_processed'] += chunk_result.get('total_products_processed', 0)
                    
                    if chunk_result.get('errors'):
                        total_result['errors'].extend(chunk_result['errors'])
                    
                    if chunk_result.get('completed_keywords'):
                        total_result['completed_keywords'].extend(chunk_result['completed_keywords'])
                    
                    if chunk_result.get('failed_keywords_list'):
                        total_result['failed_keywords_list'].extend(chunk_result['failed_keywords_list'])
                    
                    total_result['chunks_completed'] += 1
                    
                    # 진행 상황 저장 (누적 카운터 포함)
                    current_products = total_result['total_products_processed']
                    current_images = self.product_editor.total_translated_images if self.product_editor else 0
                    # batch_limit_manager와 동기화
                    self.batch_limit_manager.total_images_translated = current_images
                    self._save_progress(total_result['completed_keywords'], progress_file, account_info, current_products, current_images)
                    
                    logger.info(f"청크 {chunk_idx + 1} 완료 - 처리된 키워드: {chunk_result.get('processed_keywords', 0)}, 실패: {chunk_result.get('failed_keywords', 0)}, 처리된 상품: {chunk_result.get('total_products_processed', 0)}")
                    
                    # 마지막 청크가 아니면 브라우저 재시작
                    if chunk_idx < total_chunks - 1:
                        logger.info("다음 청크를 위해 브라우저 재시작")
                        self.cleanup()
                        # 브라우저 재시작 요청 - 상위 호출자에게 재시작 신호 전달
                        return {'restart_required': True, 'current_result': total_result}
                        
                except Exception as e:
                    error_msg = f"청크 {chunk_idx + 1} 실행 중 오류: {str(e)}"
                    logger.error(error_msg)
                    total_result['errors'].append(error_msg)
                    total_result['failed_keywords'] += len(keyword_chunk)
                    total_result['failed_keywords_list'].extend(keyword_chunk)
            
            # 전체 성공 여부 판단
            total_result['success'] = total_result['processed_keywords'] > 0 and total_result['failed_keywords'] == 0
            
            # 완료 시 진행 상황 파일 삭제
            if total_result['success'] and os.path.exists(progress_file):
                os.remove(progress_file)
                logger.info("작업 완료 - 진행 상황 파일 삭제됨")
            
            logger.info(f"3단계_1_3 배치 작업 완료 (서버: {self.server_name}) - 처리된 키워드: {total_result['processed_keywords']}, 실패: {total_result['failed_keywords']}, 총 처리된 상품: {total_result['total_products_processed']}")
            
        except Exception as e:
            error_msg = f"3단계_1_3 배치 작업 중 치명적 오류: {str(e)}"
            logger.error(error_msg)
            total_result['errors'].append(error_msg)
            total_result['success'] = False
        
        return total_result
    
    def execute_step3_1_3(self, provider_codes: List[str], account_info: Dict = None) -> Dict:
        """
        3단계_1_3 작업 실행
        
        Args:
            provider_codes: 처리할 키워드(provider_code) 목록
            account_info: 계정 정보 (엑셀 파일에서 읽은 계정 정보)
            
        Returns:
            Dict: 실행 결과
        """
        result = {
            'success': False,
            'processed_keywords': 0,
            'failed_keywords': 0,
            'total_products_processed': 0,
            'errors': [],
            'completed_keywords': [],
            'failed_keywords_list': [],
            'should_stop_batch': False  # 배치분할 중단 플래그
        }
        
        try:
            logger.info(f"3단계_1_3 작업 시작 (서버: {self.server_name}) - 처리 예정 키워드: {len(provider_codes)}개")
            
            # 1. 로그인 후 모달 처리
            if not self._handle_post_login_modals():
                logger.warning("로그인 후 모달 처리 실패 - 하지만 작업을 계속 진행합니다")
            
            # 2. 채널톡 숨기기
            if not self._hide_channel_talk():
                logger.warning("채널톡 숨기기 실패 - 계속 진행")
            
            # 3. 계정 일치 확인 (선택적)
            if account_info:
                try:
                    logger.info(f"계정 매핑 확인 시작 - 가상ID: {account_info.get('id', 'Unknown')}")
                    if not self._verify_account_match(account_info):
                        logger.warning("계정 일치 확인 실패 - 하지만 작업을 계속 진행합니다")
                except Exception as e:
                    logger.warning(f"계정 일치 확인 중 오류 발생 - 계속 진행합니다: {e}")
            
            # 4. 등록상품 메뉴로 이동
            if not self._navigate_to_registered_products():
                raise Exception("등록상품 메뉴 이동 실패")
            
            # 5. UI 초기 설정
            if not self._setup_initial_ui():
                logger.warning("UI 초기 설정 실패 - 하지만 작업을 계속 진행합니다")
            
            # 6. 엑셀에서 작업 목록 로드 (서버 필터링 포함)
            if not account_info:
                raise Exception("계정 정보가 필요합니다")
            
            account_id = account_info.get('id')
            if not account_id:
                raise Exception("계정 ID가 없습니다")
            
            # 가상 ID를 실제 이메일로 변환
            from batch.batch_manager import get_real_account_id
            real_account_id = get_real_account_id(account_id)
            logger.info(f"작업 목록 로드를 위한 계정 ID 변환: {account_id} -> {real_account_id}")
            
            # 진행 상황 파일에서 완료된 키워드 목록 및 누적 데이터 가져오기
            progress_file = self._get_progress_file_path(account_info)
            completed_keywords = []
            accumulated_products = 0
            accumulated_images = 0
            if os.path.exists(progress_file):
                try:
                    with open(progress_file, 'r', encoding='utf-8') as f:
                        progress_data = json.load(f)
                        completed_keywords = progress_data.get('completed_keywords', [])
                        accumulated_products = progress_data.get('total_products_processed', 0)
                        accumulated_images = progress_data.get('total_images_translated', 0)
                        logger.info(f"진행 상황에서 완료된 키워드 {len(completed_keywords)}개 확인: {completed_keywords}")
                        logger.info(f"진행 상황에서 누적 데이터 복구: 상품 {accumulated_products}개, 이미지 {accumulated_images}개")
                except Exception as e:
                    logger.warning(f"진행 상황 파일 읽기 실패: {e}")
            
            # 배치 제한 관리자에 누적 데이터 설정
            self.batch_limit_manager.set_accumulated_counts(accumulated_products, accumulated_images)
            self.batch_limit_manager.log_current_status("청크 시작 시 누적 데이터 복구")
            
            # ProductEditorCore3에도 누적 카운터 설정
            if self.product_editor:
                self.product_editor.total_translated_images = accumulated_images
                self.product_editor.current_product_translated_images = accumulated_images
                logger.info(f"ProductEditorCore3에 누적 카운터 설정: 상품 {accumulated_products}개, 이미지 번역 {accumulated_images}개")
            
            task_list = self.product_editor.load_task_list_from_excel_with_server_filter(
                account_id=real_account_id,
                step="step3",
                server_name=self.server_name,
                completed_keywords=completed_keywords
            )
            
            if not task_list:
                logger.warning(f"서버 {self.server_name}에 대한 작업 목록이 없습니다")
                result['success'] = True  # 작업할 것이 없는 것은 성공으로 간주
                return result
            
            logger.info(f"로드된 작업 목록: {len(task_list)}개")
            
            # 7. 키워드별 처리 (배치 제한 적용)
            for provider_code in provider_codes:
                try:
                    # provider_code가 문자열 형태의 리스트인 경우 처리
                    if isinstance(provider_code, str) and provider_code.startswith('[') and provider_code.endswith(']'):
                        # 문자열 형태의 리스트를 실제 리스트로 변환
                        import ast
                        try:
                            actual_codes = ast.literal_eval(provider_code)
                            if isinstance(actual_codes, list):
                                logger.warning(f"키워드가 문자열 형태의 리스트로 전달됨: {provider_code} -> {actual_codes}")
                                # 실제 키워드 리스트로 재귀 처리
                                for actual_code in actual_codes:
                                    # 배치 제한 확인
                                    if self.batch_limit_manager.is_batch_limit_reached():
                                        remaining_count = len(actual_codes) - actual_codes.index(actual_code)
                                        self.batch_limit_manager.log_current_status("배치 제한 달성")
                                        logger.info(f"배치 제한 달성으로 인한 조기 종료 - 남은 키워드 {remaining_count}개 처리 중단")
                                        result['should_stop_batch'] = True  # 배치분할 중단 플래그 설정
                                        break
                                    
                                    logger.info(f"===== 키워드 '{actual_code}' 처리 시작 =====")
                                    # 해당 키워드에 대한 작업 찾기
                                    matching_tasks = [task for task in task_list if task.get('provider_code') == actual_code]
                                    
                                    if not matching_tasks:
                                        logger.warning(f"키워드 '{actual_code}'에 대한 작업이 없습니다 - 처리 완료로 표시")
                                        result['processed_keywords'] += 1
                                        result['completed_keywords'].append(actual_code)
                                        continue
                                    
                                    # 키워드별 처리 (배치 제한 적용)
                                    start_time = time.time()
                                    success, products_processed = self._process_keyword_with_batch_limit(actual_code, matching_tasks)
                                    actual_process_time = time.time() - start_time
                                    
                                    if success:
                                        result['processed_keywords'] += 1
                                        result['total_products_processed'] += products_processed
                                        result['completed_keywords'].append(actual_code)
                                        
                                        # 배치 제한 관리자 업데이트는 ProductEditorCore3에서 처리됨
                                        
                                        logger.info(f"키워드 '{actual_code}' 처리 완료 (소요시간: {actual_process_time:.2f}초, 처리된 상품: {products_processed}개)")
                                        self.batch_limit_manager.log_current_status(f"키워드 '{actual_code}' 완료")
                                    else:
                                        result['failed_keywords'] += 1
                                        result['failed_keywords_list'].append(actual_code)
                                        logger.warning(f"키워드 '{actual_code}' 처리 실패")
                                continue
                        except (ValueError, SyntaxError) as e:
                            logger.error(f"키워드 문자열 파싱 실패: {provider_code}, 오류: {e}")
                    
                    # 배치 제한 확인
                    if self.batch_limit_manager.is_batch_limit_reached():
                        remaining_count = len(provider_codes) - provider_codes.index(provider_code)
                        self.batch_limit_manager.log_current_status("배치 제한 달성")
                        logger.info(f"배치 제한 달성으로 인한 조기 종료 - 남은 키워드 {remaining_count}개 처리 중단")
                        result['should_stop_batch'] = True  # 배치분할 중단 플래그 설정
                        break
                        
                    logger.info(f"===== 키워드 '{provider_code}' 처리 시작 =====")
                    
                    # 키워드 처리 전 드라이버 연결 상태 검증
                    try:
                        self.driver.current_url
                        logger.debug(f"키워드 '{provider_code}' 처리 전 드라이버 연결 상태 정상")
                    except Exception as conn_e:
                        logger.error(f"키워드 '{provider_code}' 처리 전 드라이버 연결 오류: {conn_e}")
                        # 브라우저 재시작 시도
                        if self.restart_browser_callback:
                            logger.info(f"키워드 '{provider_code}' 처리 전 브라우저 재시작 시도")
                            if self.restart_browser_callback():
                                logger.info(f"키워드 '{provider_code}' 처리 전 브라우저 재시작 성공")
                            else:
                                logger.error(f"키워드 '{provider_code}' 처리 전 브라우저 재시작 실패")
                                result['failed_keywords'] += 1
                                result['failed_keywords_list'].append(provider_code)
                                continue
                        else:
                            logger.error(f"키워드 '{provider_code}' 처리 전 브라우저 재시작 콜백 없음")
                            result['failed_keywords'] += 1
                            result['failed_keywords_list'].append(provider_code)
                            continue
                    
                    # 해당 키워드에 대한 작업 찾기
                    matching_tasks = [task for task in task_list if task.get('provider_code') == provider_code]
                    
                    if not matching_tasks:
                        logger.warning(f"키워드 '{provider_code}'에 대한 작업이 없습니다 - 처리 완료로 표시")
                        result['processed_keywords'] += 1
                        result['completed_keywords'].append(provider_code)
                        continue
                    
                    # 각 키워드마다 새로운 지연 전략 생성 (주석 처리 - 배치 작업에서 불필요)
                    # delay_strategy = HumanLikeDelay(min_total_delay=152, max_total_delay=160, current_speed=150, expected_actions=25)
                    
                    # 작업 시작 전 지연 (주석 처리 - 배치 작업에서 불필요)
                    # pre_action_delay = delay_strategy.get_delay('transition')
                    # logger.info(f"키워드 처리 시작 전 지연: {pre_action_delay:.2f}초")
                    # time.sleep(pre_action_delay)
                    
                    # 키워드별 처리 (배치 제한 적용)
                    start_time = time.time()
                    success, products_processed = self._process_keyword_with_batch_limit(provider_code, matching_tasks)
                    actual_process_time = time.time() - start_time
                    
                    if success:
                        result['processed_keywords'] += 1
                        result['total_products_processed'] += products_processed
                        result['completed_keywords'].append(provider_code)
                        
                        # 배치 제한 관리자 업데이트는 ProductEditorCore3에서 처리됨
                        
                        logger.info(f"키워드 '{provider_code}' 처리 완료 (소요시간: {actual_process_time:.2f}초, 처리된 상품: {products_processed}개)")
                        self.batch_limit_manager.log_current_status(f"키워드 '{provider_code}' 완료")
                        
                        # 작업 성공 후 지연 (주석 처리 - 배치 작업에서 불필요)
                        # post_action_delay = delay_strategy.get_delay('critical')
                        # logger.info(f"키워드 처리 완료 후 지연: {post_action_delay:.2f}초")
                        # time.sleep(post_action_delay)
                    else:
                        result['failed_keywords'] += 1
                        result['failed_keywords_list'].append(provider_code)
                        logger.warning(f"키워드 '{provider_code}' 처리 실패")
                    
                except Exception as e:
                    error_msg = f"키워드 '{provider_code}' 처리 중 오류: {str(e)}"
                    logger.error(error_msg)
                    result['errors'].append(error_msg)
                    result['failed_keywords'] += 1
                    result['failed_keywords_list'].append(provider_code)
            
            # 전체 성공 여부 판단
            result['success'] = result['processed_keywords'] > 0 and result['failed_keywords'] == 0
            
            logger.info(f"3단계_1_3 작업 완료 (서버: {self.server_name}) - 처리된 키워드: {result['processed_keywords']}, 실패: {result['failed_keywords']}, 총 처리된 상품: {result['total_products_processed']}")
            
        except Exception as e:
            error_msg = f"3단계_1_3 작업 중 치명적 오류: {str(e)}"
            logger.error(error_msg)
            logger.error(f"오류 상세: {traceback.format_exc()}")
            result['errors'].append(error_msg)
            result['success'] = False
        
        return result
    
    def _process_keyword_with_batch_limit(self, provider_code: str, matching_tasks: List[Dict]) -> Tuple[bool, int]:
        """
        배치 제한을 고려한 키워드 처리
        
        Args:
            provider_code: 처리할 키워드
            matching_tasks: 해당 키워드에 대한 작업 목록
            
        Returns:
            Tuple[bool, int]: (성공 여부, 처리된 상품 수)
        """
        try:
            # 첫 번째 작업에서 target_group 추출
            target_group = matching_tasks[0].get('target_group')
            if not target_group:
                logger.error(f"키워드 '{provider_code}'에 대한 target_group이 없습니다")
                return False, 0
            
            # 작업 데이터 준비 (첫 번째 작업의 H~M 열 데이터 사용)
            task_data = matching_tasks[0]
            
            # 배치 제한을 고려한 동적 제한 계산
            keyword_max_products, keyword_max_images = self.batch_limit_manager.calculate_keyword_limits(20)
            
            if keyword_max_products <= 0:
                logger.info(f"키워드 '{provider_code}' 처리 건너뜀 - 상품 제한 달성")
                return True, 0
                
            logger.info(f"키워드 '{provider_code}' 처리 시작 - 타겟 그룹: {target_group}, "
                       f"최대 상품: {keyword_max_products}개, 최대 이미지: {keyword_max_images}개")
            
            # ProductEditorCore3의 배치 제한 인식 처리 메서드 호출
            if hasattr(self.product_editor, 'process_keyword_with_batch_limits'):
                success, processed_count = self.product_editor.process_keyword_with_batch_limits(
                    keyword=provider_code,
                    target_group=target_group,
                    task_data=task_data,
                    max_products=keyword_max_products,
                    max_images=keyword_max_images,
                    batch_limit_manager=self.batch_limit_manager
                )
            else:
                # 기존 메서드 사용 (호환성)
                success, processed_count = self.product_editor.process_keyword_with_individual_modifications(
                    keyword=provider_code,
                    target_group=target_group,
                    task_data=task_data,
                    max_products=keyword_max_products,
                    step3_image_limit=keyword_max_images
                )
                
                # 기존 메서드 사용 시 수동으로 배치 제한 관리자 동기화
                if success:
                    self.batch_limit_manager.total_images_translated = self.product_editor.total_translated_images
            
            # 키워드 처리 후 배치 제한 관리자와 ProductEditorCore3 동기화
            if success:
                # ProductEditorCore3의 이미지 번역 수를 배치 제한 관리자에 동기화
                self.batch_limit_manager.total_images_translated = self.product_editor.total_translated_images
                logger.debug(f"키워드 '{provider_code}' 처리 후 이미지 번역 수 동기화: {self.product_editor.total_translated_images}개")
                return True, processed_count
            else:
                logger.warning(f"키워드 '{provider_code}' 처리 실패 - 브라우저 재시작 시도")
                # 키워드 처리 실패 시 브라우저 재시작 시도
                if hasattr(self, 'restart_browser_callback') and self.restart_browser_callback:
                    logger.info(f"키워드 '{provider_code}' 처리 실패로 인한 브라우저 재시작 시도")
                    if self.restart_browser_callback():
                        logger.info("브라우저 재시작 성공 - 키워드 처리 재시도")
                        # 재시작 후 다시 한 번 시도
                        try:
                            if hasattr(self.product_editor, 'process_keyword_with_batch_limits'):
                                success_retry, processed_count_retry = self.product_editor.process_keyword_with_batch_limits(
                                    keyword=provider_code,
                                    target_group=target_group,
                                    task_data=task_data,
                                    max_products=keyword_max_products,
                                    max_images=keyword_max_images,
                                    batch_limit_manager=self.batch_limit_manager
                                )
                            else:
                                success_retry, processed_count_retry = self.product_editor.process_keyword_with_individual_modifications(
                                    keyword=provider_code,
                                    target_group=target_group,
                                    task_data=task_data,
                                    max_products=keyword_max_products,
                                    step3_image_limit=keyword_max_images
                                )
                                
                                # 기존 메서드 사용 시 수동으로 배치 제한 관리자 동기화
                                if success_retry:
                                    self.batch_limit_manager.total_images_translated = self.product_editor.total_translated_images
                            
                            # 재시도 후에도 배치 제한 관리자와 ProductEditorCore3 동기화
                            if success_retry:
                                self.batch_limit_manager.total_images_translated = self.product_editor.total_translated_images
                                logger.debug(f"재시도 후 키워드 '{provider_code}' 처리 후 이미지 번역 수 동기화: {self.product_editor.total_translated_images}개")
                                logger.info(f"재시작 후 키워드 '{provider_code}' 처리 성공")
                                return True, processed_count_retry
                            else:
                                logger.error(f"재시작 후에도 키워드 '{provider_code}' 처리 실패")
                        except Exception as retry_e:
                            logger.error(f"재시작 후 키워드 '{provider_code}' 처리 중 오류: {retry_e}")
                    else:
                        logger.error("브라우저 재시작 실패")
                return False, 0
                
        except Exception as e:
            logger.error(f"키워드 '{provider_code}' 처리 중 오류: {e}")
            logger.error(f"오류 상세: {traceback.format_exc()}")
            return False, 0
    
    def _process_keyword(self, provider_code: str, matching_tasks: List[Dict]) -> Tuple[bool, int]:
        """
        개별 키워드 처리
        
        Args:
            provider_code: 처리할 키워드
            matching_tasks: 해당 키워드에 대한 작업 목록
            
        Returns:
            Tuple[bool, int]: (성공 여부, 처리된 상품 수)
        """
        try:
            # 첫 번째 작업에서 target_group 추출
            target_group = matching_tasks[0].get('target_group')
            if not target_group:
                logger.error(f"키워드 '{provider_code}'에 대한 target_group이 없습니다")
                return False, 0
            
            # 작업 데이터 준비 (첫 번째 작업의 H~M 열 데이터 사용)
            task_data = matching_tasks[0]
            
            logger.info(f"키워드 '{provider_code}' 처리 시작 - 타겟 그룹: {target_group}")
            
            # ProductEditorCore3의 키워드별 처리 메서드 호출
            success, processed_count = self.product_editor.process_keyword_with_individual_modifications(
                keyword=provider_code,
                target_group=target_group,
                task_data=task_data,
                max_products=self.step3_product_limit,
                step3_image_limit=self.step3_image_limit
            )
            
            if success:
                return True, processed_count
            else:
                logger.warning(f"키워드 '{provider_code}' 처리 실패 - 브라우저 재시작 시도")
                # 키워드 처리 실패 시 브라우저 재시작 시도
                if hasattr(self, 'restart_browser_callback') and self.restart_browser_callback:
                    logger.info(f"키워드 '{provider_code}' 처리 실패로 인한 브라우저 재시작 시도")
                    if self.restart_browser_callback():
                        logger.info("브라우저 재시작 성공 - 키워드 처리 재시도")
                        # 재시작 후 다시 한 번 시도
                        try:
                            success_retry, processed_count_retry = self.product_editor.process_keyword_with_individual_modifications(
                            keyword=provider_code,
                            target_group=target_group,
                            task_data=task_data,
                            max_products=self.step3_product_limit,
                            step3_image_limit=self.step3_image_limit
                        )
                            if success_retry:
                                logger.info(f"재시작 후 키워드 '{provider_code}' 처리 성공")
                                return True, processed_count_retry
                            else:
                                logger.error(f"재시작 후에도 키워드 '{provider_code}' 처리 실패")
                        except Exception as retry_e:
                            logger.error(f"재시작 후 키워드 '{provider_code}' 처리 중 오류: {retry_e}")
                    else:
                        logger.error("브라우저 재시작 실패")
                return False, 0
                
        except Exception as e:
            logger.error(f"키워드 '{provider_code}' 처리 중 오류: {e}")
            logger.error(f"오류 상세: {traceback.format_exc()}")
            return False, 0
    
    def _navigate_to_registered_products(self) -> bool:
        """
        등록상품 메뉴로 이동
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("등록상품 메뉴로 이동 시작")
            
            # 1. 추가 모달창 및 채널톡 숨기기 (안전장치)
            logger.info("추가 모달창 및 채널톡 숨기기 시작")
            try:
                close_modal_dialogs(self.driver)
                hide_channel_talk(self.driver)
                logger.info("추가 모달창 및 채널톡 숨기기 완료")
            except Exception as modal_error:
                logger.warning(f"추가 모달창 숨기기 중 오류 - 계속 진행: {modal_error}")
            
            # 2. 등록상품관리 화면 열기
            logger.info("등록상품관리 화면 열기 시작")
            if not open_product_editor_screen(self.driver):
                raise Exception("등록상품관리 화면 열기 실패")
            logger.info("등록상품관리 화면 열기 완료")
            
            logger.info("등록상품 메뉴로 이동 완료")
            return True
            
        except Exception as e:
            logger.error(f"등록상품 메뉴 이동 중 오류: {e}")
            return False
    
    def _setup_initial_ui(self) -> bool:
        """
        UI 초기 설정 (open_product_editor_screen에서 이미 처리되므로 생략)
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("UI 초기 설정 시작 (open_product_editor_screen에서 이미 처리됨)")
            
            # open_product_editor_screen 함수에서 이미 다음 작업들이 완료됨:
            # 1. 신규수집 그룹 선택
            # 2. 50개씩 보기 설정
            # 3. 화면 최상단으로 이동
            
            # 추가적인 화면 상단 스크롤만 수행 (안전장치)
            if not self._scroll_to_top():
                logger.warning("화면 상단 스크롤 실패 - 하지만 작업을 계속 진행합니다")
            
            logger.info("UI 초기 설정 완료")
            return True
            
        except Exception as e:
            logger.error(f"UI 초기 설정 중 오류: {e}")
            return True  # 실패해도 계속 진행
    
    def _change_to_new_collection(self) -> bool:
        """
        신규수집 그룹으로 변경
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("신규수집 그룹으로 변경 시작")
            
            # 드라이버 연결 상태 확인
            try:
                self.driver.current_url
                logger.info("드라이버 연결 상태 정상")
            except Exception as e:
                logger.error(f"드라이버 연결 오류 감지: {e}")
                return False
            
            from dropdown_utils2 import ProductSearchDropdownManager
            
            # ProductSearchDropdownManager 사용
            dropdown_manager = ProductSearchDropdownManager(self.driver)
            
            # 신규수집 그룹 선택 시도 (최대 3회 재시도)
            for attempt in range(3):
                try:
                    logger.info(f"신규수집 그룹 선택 시도 {attempt + 1}/3")
                    
                    # 상품검색용 드롭박스에서 신규수집 그룹 선택 (통합 메서드 사용)
                    if dropdown_manager.select_group_in_search_dropdown("신규수집"):
                        logger.info("신규수집 그룹 선택 성공")
                        
                        # 상품 목록 자동 로딩 대기
                        if dropdown_manager.verify_page_refresh():
                            logger.info("상품 목록 자동 로딩 완료")
                            return True
                        else:
                            logger.warning("상품 목록 로딩 확인 실패")
                    else:
                        logger.warning(f"신규수집 그룹 선택 실패 (시도 {attempt + 1}/3)")
                    
                    # 재시도 전 잠시 대기
                    if attempt < 2:  # 마지막 시도가 아닌 경우만
                        time.sleep(2)
                        
                except Exception as e:
                    logger.error(f"신규수집 그룹 선택 중 오류 (시도 {attempt + 1}/3): {e}")
                    if attempt < 2:  # 마지막 시도가 아닌 경우만
                        time.sleep(2)
            
            logger.warning("신규수집 그룹 변경 실패 - 브라우저 재시작 시도")
            # 신규수집 그룹 선택 실패 시 브라우저 재시작 시도
            if hasattr(self, 'restart_browser_callback') and self.restart_browser_callback:
                logger.info("신규수집 그룹 선택 실패로 인한 브라우저 재시작 시도")
                if self.restart_browser_callback():
                    logger.info("브라우저 재시작 성공 - 신규수집 그룹 선택 재시도")
                    # 재시작 후 다시 한 번 시도
                    try:
                        dropdown_manager = ProductSearchDropdownManager(self.driver)
                        if dropdown_manager.select_group_in_search_dropdown("신규수집"):
                            logger.info("재시작 후 신규수집 그룹 선택 성공")
                            return True
                    except Exception as retry_e:
                        logger.error(f"재시작 후 신규수집 그룹 선택 실패: {retry_e}")
                else:
                    logger.error("브라우저 재시작 실패")
            return False  # 실패 시 False 반환
            
        except Exception as e:
            logger.error(f"신규수집 그룹 변경 중 오류: {e}")
            # 오류 발생 시에도 브라우저 재시작 시도
            if hasattr(self, 'restart_browser_callback') and self.restart_browser_callback:
                logger.info("오류 발생으로 인한 브라우저 재시작 시도")
                if self.restart_browser_callback():
                    logger.info("브라우저 재시작 성공")
                    return True
            return False  # 실패 시 False 반환
    
    def _scroll_to_top(self) -> bool:
        """
        맨 위로 스크롤
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("맨 위로 스크롤 시작")
            
            from timesleep import DELAY_SHORT
            
            # JavaScript로 맨 위로 스크롤
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(DELAY_SHORT)
            
            # 페이지 상단 요소로 스크롤 (추가 보장)
            try:
                from selenium.webdriver.common.by import By
                header_selectors = [
                    "//header",
                    "//div[contains(@class, 'header')]",
                    "//nav",
                    "//div[contains(@class, 'navbar')]",
                    "//body"
                ]
                
                for selector in header_selectors:
                    try:
                        header_element = self.driver.find_element(By.XPATH, selector)
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", header_element)
                        break
                    except Exception as e:
                        logger.debug(f"헤더 요소 {selector} 스크롤 실패: {e}")
                        continue
                        
            except Exception as e:
                logger.debug(f"헤더 요소 스크롤 실패: {e}")
            
            time.sleep(DELAY_SHORT)
            logger.info("맨 위로 스크롤 완료")
            return True
            
        except Exception as e:
            logger.error(f"맨 위로 스크롤 중 오류: {e}")
            return True  # 실패해도 계속 진행
    
    def _handle_post_login_modals(self) -> bool:
        """
        로그인 후 모달 처리
        
        Returns:
            bool: 성공 여부
        """
        try:
            return handle_post_login_modals(self.driver)
        except Exception as e:
            logger.error(f"로그인 후 모달 처리 중 오류: {e}")
            return False
    
    def _hide_channel_talk(self) -> bool:
        """
        채널톡 숨기기
        
        Returns:
            bool: 성공 여부
        """
        try:
            return hide_channel_talk(self.driver)
        except Exception as e:
            logger.error(f"채널톡 숨기기 중 오류: {e}")
            return False
    
    def _verify_account_match(self, account_info: Dict) -> bool:
        """
        로그인한 계정과 엑셀 파일의 계정 일치 확인
        
        Args:
            account_info: 엑셀 파일에서 읽은 계정 정보
            
        Returns:
            bool: 계정 일치 여부
        """
        try:
            logger.info(f"계정 매핑 확인 시작 - 전달받은 account_info: {account_info}")
            
            # 현재 로그인된 계정 정보 가져오기
            current_account = self._get_current_logged_account()
            
            if not current_account:
                logger.warning("현재 로그인된 계정 정보를 가져올 수 없습니다 - 이는 페이지 로딩 지연이나 UI 변경으로 인한 일시적 문제일 수 있습니다")
                return True  # 계정 정보를 찾을 수 없는 경우 진행 허용
            
            # 계정 일치 확인 (엑셀에서 파싱된 정보는 'id' 키 사용)
            excel_account_virtual = account_info.get('id', '').strip()
            
            if not excel_account_virtual:
                logger.warning("엑셀에서 계정 ID를 찾을 수 없습니다 - account_info에 'id' 키가 없거나 비어있습니다")
                return True  # 계정 정보가 없는 경우 진행 허용
            
            # 가상 계정 ID를 실제 이메일로 변환
            from batch.batch_manager import get_real_account_id
            excel_account_real = get_real_account_id(excel_account_virtual)
            
            logger.info(f"계정 매핑 상세정보:")
            logger.info(f"  - 현재 로그인 계정: {current_account}")
            logger.info(f"  - 엑셀 가상 ID: {excel_account_virtual}")
            logger.info(f"  - 엑셀 실제 ID: {excel_account_real}")
            
            if current_account.lower() == excel_account_real.lower():
                logger.info(f"✅ 계정 일치 확인 완료: {current_account}")
                return True
            else:
                logger.warning(f"⚠️ 계정 불일치 감지:")
                logger.warning(f"  - 로그인된 계정: {current_account}")
                logger.warning(f"  - 엑셀 파일 계정(가상): {excel_account_virtual}")
                logger.warning(f"  - 엑셀 파일 계정(실제): {excel_account_real}")
                logger.warning(f"이는 다음 원인일 수 있습니다:")
                logger.warning(f"  1. 다른 계정으로 로그인됨")
                logger.warning(f"  2. 계정 정보 검색 실패 (일시적 UI 문제)")
                logger.warning(f"  3. 계정 매핑 테이블 불일치")
                return False
                
        except Exception as e:
            logger.error(f"계정 일치 확인 중 오류: {e}")
            return False
    
    def _get_current_logged_account(self) -> Optional[str]:
        """
        현재 로그인된 계정 정보 가져오기
        
        Returns:
            str: 현재 로그인된 계정 ID (이메일)
        """
        try:
            import re
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            logger.debug("현재 로그인된 계정 정보 검색 시작")
            
            # 1. 퍼센티 특화 셀렉터들로 검색
            percenty_selectors = [
                # 헤더 영역 사용자 정보
                ".ant-layout-header [class*='user']",
                ".ant-layout-header [class*='account']",
                ".ant-layout-header [class*='profile']",
                ".ant-layout-header .ant-dropdown-trigger",
                ".ant-layout-header .ant-avatar",
                
                # 사이드바 사용자 정보
                ".ant-layout-sider [class*='user']",
                ".ant-layout-sider [class*='account']",
                ".ant-layout-sider [class*='profile']",
                
                # 일반적인 사용자 정보 영역
                "[data-testid*='user']",
                "[data-testid*='account']",
                "[data-testid*='profile']",
                "[aria-label*='user']",
                "[aria-label*='account']",
                "[title*='@']",
                
                # 드롭다운 메뉴 관련
                ".ant-dropdown [class*='user']",
                ".ant-dropdown [class*='account']",
                ".ant-dropdown-menu-item",
                
                # 기존 셀렉터들
                "[data-testid='user-email']",
                ".user-email",
                "#user-email",
                ".account-info .email",
                ".user-info .email",
                "[class*='email']",
                "[id*='email']",
                ".header .user-info",
                ".navbar .user-info"
            ]
            
            # 짧은 대기 시간으로 빠른 검색
            for selector in percenty_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        # 텍스트 내용 확인
                        text = element.text.strip()
                        if text and '@' in text and '.' in text:
                            # 이메일 패턴 검증
                            email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
                            if email_match:
                                email = email_match.group()
                                logger.debug(f"셀렉터 '{selector}'에서 계정 발견: {email}")
                                return email
                        
                        # 속성값도 확인
                        for attr in ['title', 'data-user', 'data-account', 'aria-label', 'placeholder', 'value']:
                            attr_value = element.get_attribute(attr)
                            if attr_value and '@' in attr_value:
                                email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', attr_value)
                                if email_match:
                                    email = email_match.group()
                                    logger.debug(f"속성 '{attr}'에서 계정 발견: {email}")
                                    return email
                except Exception as e:
                    continue
            
            # 2. DOM 전체에서 이메일 패턴 검색
            try:
                logger.debug("DOM 전체에서 이메일 패턴 검색")
                all_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '@')]")
                email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
                
                for element in all_elements[:50]:  # 처음 50개만 검사
                    try:
                        text = element.text.strip()
                        if text:
                            emails = email_pattern.findall(text)
                            if emails:
                                email = emails[0]  # 첫 번째 이메일 사용
                                logger.debug(f"DOM 검색에서 계정 발견: {email}")
                                return email
                    except Exception as e:
                        continue
            except Exception as e:
                logger.debug(f"DOM 검색 실패: {e}")
            
            # 3. JavaScript로 계정 정보 찾기 시도
            try:
                logger.debug("JavaScript로 계정 정보 검색")
                js_scripts = [
                    # 일반적인 사용자 정보
                    "return window.user?.email || window.user;",
                    "return window.currentUser?.email || window.currentUser;",
                    "return window.userInfo?.email || window.userInfo;",
                    "return window.account?.email || window.account;",
                    "return window.accountInfo?.email || window.accountInfo;",
                    
                    # 로컬/세션 스토리지
                    "return localStorage.getItem('user') || localStorage.getItem('userInfo') || localStorage.getItem('account') || localStorage.getItem('email');",
                    "return sessionStorage.getItem('user') || sessionStorage.getItem('userInfo') || sessionStorage.getItem('account') || sessionStorage.getItem('email');",
                    
                    # DOM 검색
                    "return document.querySelector('[data-user-email]')?.getAttribute('data-user-email');",
                    "return [...document.querySelectorAll('*')].find(el => el.textContent && el.textContent.includes('@'))?.textContent;",
                    "return [...document.querySelectorAll('[title]')].find(el => el.title && el.title.includes('@'))?.title;"
                ]
                
                for script in js_scripts:
                    try:
                        result = self.driver.execute_script(script)
                        if result:
                            result_str = str(result).strip()
                            if '@' in result_str:
                                # JSON 파싱 시도
                                try:
                                    import json
                                    if result_str.startswith('{') or result_str.startswith('['):
                                        data = json.loads(result_str)
                                        if isinstance(data, dict):
                                            email = data.get('email') or data.get('user') or data.get('account')
                                            if email and '@' in str(email):
                                                logger.debug(f"JavaScript JSON에서 계정 발견: {email}")
                                                return str(email).strip()
                                except:
                                    pass
                                
                                # 직접 이메일 패턴 검색
                                email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', result_str)
                                if email_match:
                                    email = email_match.group()
                                    logger.debug(f"JavaScript에서 계정 발견: {email}")
                                    return email
                    except Exception as js_error:
                        continue
                        
            except Exception as e:
                logger.debug(f"JavaScript 계정 정보 추출 실패: {e}")
            
            # 4. 페이지 소스에서 검색 (최후의 수단)
            try:
                logger.debug("페이지 소스에서 이메일 패턴 검색")
                page_source = self.driver.page_source
                email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
                emails = email_pattern.findall(page_source)
                
                if emails:
                    # 가장 가능성 높은 이메일 선택 (중복 제거 후 첫 번째)
                    unique_emails = list(set(emails))
                    email = unique_emails[0]
                    logger.debug(f"페이지 소스에서 계정 발견: {email}")
                    return email
                    
            except Exception as e:
                logger.debug(f"페이지 소스 검색 실패: {e}")
            
            logger.debug("현재 로그인된 계정 정보를 찾을 수 없습니다")
            return None
            
        except Exception as e:
            logger.error(f"현재 로그인된 계정 정보 가져오기 중 오류: {e}")
            return None
    
    def _get_progress_file_path(self, account_info: Dict) -> str:
        """
        진행 상황 파일 경로 생성
        
        Args:
            account_info: 계정 정보
            
        Returns:
            str: 진행 상황 파일 경로
        """
        account_id = account_info.get('id', 'unknown') if account_info else 'unknown'
        return f"progress_{account_id}_step3_1_3_core.json"
    
    def _save_progress(self, completed_keywords: List[str], progress_file: str, account_info: Dict, total_products_processed: int = 0, total_images_translated: int = 0):
        """
        진행 상황 저장 (절대값으로 저장)
        
        Args:
            completed_keywords: 완료된 키워드 목록
            progress_file: 진행 상황 파일 경로
            account_info: 계정 정보
            total_products_processed: 현재까지 누적 처리된 상품 수 (절대값)
            total_images_translated: 현재까지 누적 번역된 이미지 수 (절대값)
        """
        try:
            # 배치 제한 관리자에서 현재 누적값 가져오기
            current_products = self.batch_limit_manager.total_products_processed
            current_images = self.batch_limit_manager.total_images_translated
            
            progress_data = {
                "account_id": account_info.get('id', 'unknown') if account_info else 'unknown',
                "server_name": self.server_name,
                "completed_keywords": completed_keywords,
                "total_products_processed": current_products,
                "total_images_translated": current_images,
                "last_updated": time.strftime("%Y-%m-%dT%H:%M:%S")
            }
            
            # 파일 접근 오류 방지를 위한 재시도 로직
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    with open(progress_file, 'w', encoding='utf-8') as f:
                        json.dump(progress_data, f, ensure_ascii=False, indent=2)
                    break
                except (PermissionError, OSError) as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"진행 상황 저장 시도 {attempt + 1} 실패, 재시도: {e}")
                        time.sleep(0.5)
                    else:
                        raise
                
            logger.info(f"진행 상황 저장됨: {len(completed_keywords)}개 키워드 완료, 누적 상품 {current_products}개, 누적 이미지 번역 {current_images}개")
            
        except Exception as e:
            logger.error(f"진행 상황 저장 중 오류: {e}")
    
    def _resume_from_progress(self, provider_codes: List[str], progress_file: str) -> Tuple[List[str], int, int]:
        """
        진행 상황에서 복구 (누적 카운터 포함)
        
        Args:
            provider_codes: 전체 키워드 목록
            progress_file: 진행 상황 파일 경로
            
        Returns:
            Tuple[List[str], int, int]: (남은 키워드 목록, 누적 처리된 상품 수, 누적 번역된 이미지 수)
        """
        try:
            if not os.path.exists(progress_file):
                return provider_codes, 0, 0
            
            with open(progress_file, 'r', encoding='utf-8') as f:
                progress_data = json.load(f)
            
            completed_keywords = progress_data.get('completed_keywords', [])
            remaining_keywords = [k for k in provider_codes if k not in completed_keywords]
            accumulated_products = progress_data.get('total_products_processed', 0)
            accumulated_images = progress_data.get('total_images_translated', 0)
            
            if len(remaining_keywords) < len(provider_codes):
                logger.info(f"진행 상황 복구: {len(completed_keywords)}개 키워드 이미 완료, {len(remaining_keywords)}개 키워드 남음")
                logger.info(f"누적 처리량 복구: 상품 {accumulated_products}개, 이미지 번역 {accumulated_images}개")
            
            return remaining_keywords, accumulated_products, accumulated_images
            
        except Exception as e:
            logger.error(f"진행 상황 복구 중 오류: {e}")
            return provider_codes, 0, 0
    
    def cleanup(self):
        """
        리소스 정리
        """
        try:
            logger.info("3단계_1_3 코어 리소스 정리 시작")
            
            # UI 정리 (한 번만 실행)
            if self.driver:
                periodic_ui_cleanup(self.driver, max_attempts=1)
            
            # 관리자 객체들 정리
            if self.product_editor:
                # ProductEditorCore3에 cleanup 메서드가 있다면 호출
                if hasattr(self.product_editor, 'cleanup'):
                    self.product_editor.cleanup()
            
            logger.info("3단계_1_3 코어 리소스 정리 완료")
            
        except Exception as e:
            logger.error(f"리소스 정리 중 오류: {e}")
    
    def get_status(self) -> Dict:
        """
        현재 상태 반환
        
        Returns:
            Dict: 상태 정보
        """
        return {
            'server_name': self.server_name,
            'driver_available': self.driver is not None,
            'managers_setup': all([
                self.browser_core is not None,
                self.login_manager is not None,
                self.menu_clicks is not None,
                self.product_editor is not None
            ])
        }