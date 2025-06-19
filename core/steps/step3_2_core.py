# -*- coding: utf-8 -*-
"""
3단계_2 코어 로직 (서버2)
퍼센티 자동화 3단계 작업의 핵심 비즈니스 로직 - 서버2 전용
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
from product_editor_screen import open_product_editor_screen

logger = logging.getLogger(__name__)

class Step3_2Core:
    """
    3단계_2 작업의 핵심 로직을 담당하는 클래스 (서버2 전용)
    등록상품에서 키워드별 상품 수정 및 그룹 이동 작업 수행
    """
    
    def __init__(self, driver=None, server_name="서버2", restart_browser_callback=None):
        """
        초기화
        
        Args:
            driver: Selenium WebDriver 인스턴스
            server_name: 서버 이름 (기본값: "서버2")
            restart_browser_callback: 브라우저 재시작 콜백 함수
        """
        self.driver = driver
        self.server_name = server_name
        self.browser_core = None
        self.login_manager = None
        self.menu_clicks = None
        # self.delay = HumanLikeDelay()
        self.product_editor = None
        self.restart_browser_callback = restart_browser_callback
        
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
            self.product_editor = ProductEditorCore3(self.driver)
            logger.info("ProductEditorCore3 인스턴스 생성 완료")
            
            logger.info(f"3단계_2 코어 관리자 객체들이 설정되었습니다. (서버: {self.server_name})")
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
                logger.error(f"새 드라이버 연결 상태 오류: {e} - {self.server_name}")
                raise
            
            # 메인 드라이버 참조 업데이트
            old_driver = self.driver
            self.driver = new_driver
            logger.info(f"메인 드라이버 참조 업데이트 완료 - {self.server_name}")
            
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
            
            # 드라이버 참조 업데이트 후 연결 상태 재검증
            try:
                self.driver.current_url
                logger.info(f"업데이트된 드라이버 연결 상태 정상 확인 - {self.server_name}")
            except Exception as e:
                logger.error(f"업데이트된 드라이버 연결 상태 오류: {e} - {self.server_name}")
                raise
            
            logger.info(f"모든 관리자 객체의 드라이버 참조 업데이트 완료 - {self.server_name}")
            
        except Exception as e:
            logger.error(f"드라이버 참조 업데이트 중 오류: {e} - {self.server_name}")
            logger.error(f"오류 상세: {traceback.format_exc()}")
            raise
    
    def execute_step3_2_with_browser_restart(self, provider_codes: List[str], chunk_size: int = 2, account_info: Dict = None) -> Dict:
        """
        3단계_2 작업 실행 (브라우저 재시작 방식)
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
            
            logger.info(f"3단계_2 배치 작업 시작 (서버: {self.server_name}) - 총 {total_keywords}개 키워드를 {total_chunks}개 청크로 처리")
            
            # 진행 상황 저장을 위한 파일 경로
            progress_file = self._get_progress_file_path(account_info)
            
            # 기존 진행 상황 복구
            remaining_keywords = self._resume_from_progress(provider_codes, progress_file)
            if remaining_keywords != provider_codes:
                logger.info(f"진행 상황 복구됨 - 남은 키워드: {len(remaining_keywords)}개")
                provider_codes = remaining_keywords
                total_keywords = len(provider_codes)
                total_chunks = (total_keywords + chunk_size - 1) // chunk_size
                total_result['total_chunks'] = total_chunks
            
            # 키워드를 청크로 분할
            keyword_chunks = [provider_codes[i:i + chunk_size] for i in range(0, total_keywords, chunk_size)]
            
            for chunk_idx, keyword_chunk in enumerate(keyword_chunks):
                logger.info(f"청크 {chunk_idx + 1}/{total_chunks} 시작 - {len(keyword_chunk)}개 키워드 처리: {keyword_chunk}")
                
                try:
                    # 청크 실행
                    chunk_result = self.execute_step3_2(keyword_chunk, account_info)
                    
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
                    
                    # 진행 상황 저장
                    self._save_progress(total_result['completed_keywords'], progress_file, account_info)
                    
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
            
            logger.info(f"3단계_2 배치 작업 완료 (서버: {self.server_name}) - 처리된 키워드: {total_result['processed_keywords']}, 실패: {total_result['failed_keywords']}, 총 처리된 상품: {total_result['total_products_processed']}")
            
        except Exception as e:
            error_msg = f"3단계_2 배치 작업 중 치명적 오류: {str(e)}"
            logger.error(error_msg)
            total_result['errors'].append(error_msg)
            total_result['success'] = False
        
        return total_result
    
    def execute_step3_2(self, provider_codes: List[str], account_info: Dict = None) -> Dict:
        """
        3단계_2 작업 실행
        
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
            'failed_keywords_list': []
        }
        
        try:
            logger.info(f"3단계_2 작업 시작 (서버: {self.server_name}) - 처리 예정 키워드: {len(provider_codes)}개")
            
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
            
            task_list = self.product_editor.load_task_list_from_excel_with_server_filter(
                account_id=real_account_id,
                step="step3",
                server_name=self.server_name
            )
            
            if not task_list:
                logger.warning(f"서버 {self.server_name}에 대한 작업 목록이 없습니다")
                result['success'] = True  # 작업할 것이 없는 것은 성공으로 간주
                return result
            
            logger.info(f"로드된 작업 목록: {len(task_list)}개")
            
            # 7. 키워드별 처리
            for provider_code in provider_codes:
                try:
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
                        logger.warning(f"키워드 '{provider_code}'에 대한 작업이 없습니다")
                        continue
                    
                    # 각 키워드마다 새로운 지연 전략 생성 (주석 처리 - 배치 작업에서 불필요)
                    # delay_strategy = HumanLikeDelay(min_total_delay=152, max_total_delay=160, current_speed=150, expected_actions=25)
                    
                    # 작업 시작 전 지연 (주석 처리 - 배치 작업에서 불필요)
                    # pre_action_delay = delay_strategy.get_delay('transition')
                    # logger.info(f"키워드 처리 시작 전 지연: {pre_action_delay:.2f}초")
                    # time.sleep(pre_action_delay)
                    
                    # 키워드별 처리
                    start_time = time.time()
                    success, products_processed = self._process_keyword(provider_code, matching_tasks)
                    actual_process_time = time.time() - start_time
                    
                    if success:
                        result['processed_keywords'] += 1
                        result['total_products_processed'] += products_processed
                        result['completed_keywords'].append(provider_code)
                        logger.info(f"키워드 '{provider_code}' 처리 완료 (소요시간: {actual_process_time:.2f}초, 처리된 상품: {products_processed}개)")
                        
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
            
            logger.info(f"3단계_2 작업 완료 (서버: {self.server_name}) - 처리된 키워드: {result['processed_keywords']}, 실패: {result['failed_keywords']}, 총 처리된 상품: {result['total_products_processed']}")
            
        except Exception as e:
            error_msg = f"3단계_2 작업 중 치명적 오류: {str(e)}"
            logger.error(error_msg)
            logger.error(f"오류 상세: {traceback.format_exc()}")
            result['errors'].append(error_msg)
            result['success'] = False
        
        return result
    
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
                task_data=task_data
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
                                task_data=task_data
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
            
            # 추가 모달 처리
            handle_post_login_modals(self.browser_core.driver)
            
            # 채널톡 숨기기
            hide_channel_talk(self.browser_core.driver)
            
            # 등록상품 관리 화면 열기
            open_product_editor_screen(self.browser_core.driver)
            
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
        계정 일치 확인
        
        Args:
            account_info: 계정 정보
            
        Returns:
            bool: 일치 여부
        """
        try:
            # 계정 일치 확인 로직 (기존 코드 참조)
            # 실제 구현은 필요에 따라 추가
            return True
        except Exception as e:
            logger.error(f"계정 일치 확인 중 오류: {e}")
            return False
    
    def _get_progress_file_path(self, account_info: Dict) -> str:
        """
        진행 상황 파일 경로 생성
        
        Args:
            account_info: 계정 정보
            
        Returns:
            str: 진행 상황 파일 경로
        """
        account_id = account_info.get('id', 'unknown') if account_info else 'unknown'
        return f"progress_{account_id}_step3_{self.server_name}.json"
    
    def _save_progress(self, completed_keywords: List[str], progress_file: str, account_info: Dict):
        """
        진행 상황 저장
        
        Args:
            completed_keywords: 완료된 키워드 목록
            progress_file: 진행 상황 파일 경로
            account_info: 계정 정보
        """
        try:
            progress_data = {
                "account_id": account_info.get('id', 'unknown') if account_info else 'unknown',
                "server_name": self.server_name,
                "completed_keywords": completed_keywords,
                "last_updated": time.strftime("%Y-%m-%dT%H:%M:%S")
            }
            
            with open(progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress_data, f, ensure_ascii=False, indent=2)
                
            logger.info(f"진행 상황 저장됨: {len(completed_keywords)}개 키워드 완료")
            
        except Exception as e:
            logger.error(f"진행 상황 저장 중 오류: {e}")
    
    def _resume_from_progress(self, provider_codes: List[str], progress_file: str) -> List[str]:
        """
        진행 상황에서 복구
        
        Args:
            provider_codes: 전체 키워드 목록
            progress_file: 진행 상황 파일 경로
            
        Returns:
            List[str]: 남은 키워드 목록
        """
        try:
            if not os.path.exists(progress_file):
                return provider_codes
            
            with open(progress_file, 'r', encoding='utf-8') as f:
                progress_data = json.load(f)
            
            completed_keywords = progress_data.get('completed_keywords', [])
            remaining_keywords = [k for k in provider_codes if k not in completed_keywords]
            
            if len(remaining_keywords) < len(provider_codes):
                logger.info(f"진행 상황 복구: {len(completed_keywords)}개 키워드 이미 완료, {len(remaining_keywords)}개 키워드 남음")
            
            return remaining_keywords
            
        except Exception as e:
            logger.error(f"진행 상황 복구 중 오류: {e}")
            return provider_codes
    
    def cleanup(self):
        """
        리소스 정리
        """
        try:
            logger.info("3단계_2 코어 리소스 정리 시작")
            
            # UI 정리 (한 번만 실행)
            if self.driver:
                periodic_ui_cleanup(self.driver, max_attempts=1)
            
            # 관리자 객체들 정리
            if self.product_editor:
                # ProductEditorCore3에 cleanup 메서드가 있다면 호출
                if hasattr(self.product_editor, 'cleanup'):
                    self.product_editor.cleanup()
            
            logger.info("3단계_2 코어 리소스 정리 완료")
            
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