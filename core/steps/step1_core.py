#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
1단계 코어 로직
퍼센티 자동화 1단계 작업의 핵심 비즈니스 로직
"""

import os
import sys
import logging
from typing import Dict, List, Optional, Union, Tuple

# 루트 디렉토리를 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 기존 모듈들 임포트 (루트에서)
try:
    from percenty_new_step1 import *
except ImportError:
    pass
try:
    from product_editor_core import *
except ImportError:
    pass
from browser_core import BrowserCore
from login_percenty import PercentyLogin
from menu_clicks import MenuClicks
from coordinates.coordinates_all import MENU
from timesleep import DELAY_STANDARD, DELAY_SHORT
from human_delay import HumanLikeDelay
from ui_elements import UI_ELEMENTS
from click_utils import smart_click

# 공통 함수들 임포트
from core.common.modal_handler import handle_post_login_modals, hide_channel_talk, close_modal_dialogs
from core.common.navigation_handler import navigate_to_ai_sourcing, navigate_to_group_management, switch_to_non_group_view
from core.common.product_handler import check_product_count, check_toggle_state, toggle_product_view
from core.common.ui_handler import periodic_ui_cleanup, ensure_clean_ui_before_action

logger = logging.getLogger(__name__)

class Step1Core:
    """
    1단계 작업의 핵심 로직을 담당하는 클래스
    기존 코드의 기능을 유지하면서 모듈화
    """
    
    def __init__(self, driver=None):
        """
        초기화
        
        Args:
            driver: Selenium WebDriver 인스턴스
        """
        self.driver = driver
        self.browser_core = None
        self.login_manager = None
        self.menu_clicks = None
        self.delay = HumanLikeDelay()
        
        if driver:
            self.setup_managers()
    
    def setup_managers(self):
        """관리자 객체들 설정"""
        try:
            # BrowserCore는 driver를 매개변수로 받지 않으므로 인스턴스만 생성
            self.browser_core = BrowserCore()
            # driver를 별도로 설정
            self.browser_core.driver = self.driver
            
            self.login_manager = PercentyLogin(self.driver)
            self.menu_clicks = MenuClicks(self.driver)
            logger.info("1단계 코어 관리자 객체들이 설정되었습니다.")
        except Exception as e:
            logger.error(f"관리자 객체 설정 중 오류: {e}")
            raise
    
    def execute_step1_with_browser_restart(self, quantity: int = 1, chunk_size: int = 10) -> Dict:
        """
        1단계 작업 실행 (브라우저 재시작 방식)
        메모리 사용량 최적화를 위해 지정된 수량마다 브라우저를 재시작
        
        Args:
            quantity: 처리할 상품 수량
            chunk_size: 브라우저 재시작 간격 (기본값: 20)
            
        Returns:
            Dict: 실행 결과
        """
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
            
            logger.info(f"브라우저 재시작 방식으로 1단계 작업 시작")
            logger.info(f"총 수량: {quantity}, 청크 크기: {chunk_size}, 총 청크 수: {total_chunks}")
            
            for chunk_idx in range(total_chunks):
                start_idx = chunk_idx * chunk_size
                end_idx = min(start_idx + chunk_size, quantity)
                current_chunk_size = end_idx - start_idx
                
                logger.info(f"===== 청크 {chunk_idx + 1}/{total_chunks} 시작 (상품 {start_idx + 1}-{end_idx}) =====")
                
                try:
                    # 현재 청크 실행
                    chunk_result = self.execute_step1(current_chunk_size)
                    
                    # 결과 누적
                    total_result['processed'] += chunk_result['processed']
                    total_result['failed'] += chunk_result['failed']
                    total_result['errors'].extend(chunk_result['errors'])
                    total_result['chunks_completed'] += 1
                    
                    logger.info(f"청크 {chunk_idx + 1} 완료: 처리 {chunk_result['processed']}개, 실패 {chunk_result['failed']}개")
                    
                    # 마지막 청크가 아니면 브라우저 재시작
                    if chunk_idx < total_chunks - 1:
                        logger.info(f"청크 {chunk_idx + 1} 완료 후 브라우저 재시작")
                        self._restart_browser()
                        
                        # 재시작 후 초기화 대기
                        import time
                        time.sleep(3)
                        
                except Exception as chunk_error:
                    logger.error(f"청크 {chunk_idx + 1} 실행 중 오류: {chunk_error}")
                    total_result['errors'].append(f"청크 {chunk_idx + 1}: {str(chunk_error)}")
                    
                    # 오류 발생 시에도 브라우저 재시작 시도
                    if chunk_idx < total_chunks - 1:
                        try:
                            logger.info(f"오류 발생 후 브라우저 재시작 시도")
                            self._restart_browser()
                            import time
                            time.sleep(3)
                        except Exception as restart_error:
                            logger.error(f"브라우저 재시작 실패: {restart_error}")
                            break
            
            # 전체 결과 평가
            if total_result['processed'] > 0:
                total_result['success'] = True
                
            logger.info(f"브라우저 재시작 방식 작업 완료")
            logger.info(f"총 처리: {total_result['processed']}개, 총 실패: {total_result['failed']}개")
            logger.info(f"완료된 청크: {total_result['chunks_completed']}/{total_result['total_chunks']}")
            
            return total_result
            
        except Exception as e:
            logger.error(f"브라우저 재시작 방식 작업 중 전체 오류: {e}")
            total_result['errors'].append(f"전체 작업 오류: {str(e)}")
            return total_result
    
    def _restart_browser(self):
        """
        브라우저 재시작
        현재 브라우저를 종료하고 새로운 브라우저를 시작
        """
        try:
            logger.info("브라우저 재시작 시작")
            
            # 현재 브라우저 종료
            if self.driver:
                try:
                    self.driver.quit()
                    logger.info("기존 브라우저 종료 완료")
                except Exception as quit_error:
                    logger.warning(f"브라우저 종료 중 오류 (무시): {quit_error}")
            
            # 새 브라우저 시작 (batch_manager에서 처리되어야 함)
            # 여기서는 driver가 외부에서 새로 설정될 것으로 가정
            logger.info("새 브라우저 시작 대기 중...")
            
        except Exception as e:
            logger.error(f"브라우저 재시작 중 오류: {e}")
            raise
    
    def execute_step1(self, quantity: int = 1) -> Dict:
        """
        1단계 작업 실행 (기존 방식)
        
        Args:
            quantity: 처리할 상품 수량
            
        Returns:
            Dict: 실행 결과
        """
        result = {
            'success': False,
            'processed': 0,
            'failed': 0,
            'errors': [],
            'product_count_before': 0,
            'product_count_after': 0,
            'should_stop_batch': False  # 배치분할 중단 플래그
        }
        
        try:
            logger.info(f"1단계 작업 시작 - 목표 수량: {quantity}")
            
            # 로그인 후 필수 이벤트 처리
            # 1. 모달창 처리 (로그인 모달, 비밀번호 저장 모달 등)
            self._handle_post_login_modals()
            
            # 2. 채널톡 숨기기
            self._hide_channel_talk()
            
            # 3. AI 소싱 메뉴 클릭
            self._navigate_to_ai_sourcing()
            
            # 4. 그룹상품관리 화면으로 이동
            self._navigate_to_group_management()
            
            # 5. 비그룹상품보기 클릭
            self._switch_to_non_group_view()
            
            # 6. 실행 전 상품 개수 확인
            available_products = self._check_product_count()
            result['product_count_before'] = available_products
            logger.info(f"📊 실행 전 비그룹상품 수량: {available_products}개")
            
            if available_products == 0:
                logger.error("비그룹상품 목록이 비어있습니다.")
                result['errors'].append("비그룹상품 목록이 비어있습니다.")
                result['should_stop_batch'] = True  # 배치분할 중단 플래그 설정
                return result
            
            # 7. 수량 조정
            if available_products < quantity:
                logger.warning(f"요청 수량({quantity})보다 적은 상품({available_products})이 있습니다.")
                quantity = available_products
                logger.info(f"작업 수량을 {quantity}개로 조정했습니다.")
            
            # 8. 상품 처리 루프
            for i in range(1, quantity + 1):
                # 토글 실행 플래그 (같은 상품에서 중복 토글 방지)
                toggle_executed = False
                
                try:
                    logger.info(f"===== 상품 {i}/{quantity} 작업 시작 =====")
                    
                    # 각 상품마다 새로운 지연 전략 생성
                    delay_strategy = HumanLikeDelay(min_total_delay=45, max_total_delay=60, current_speed=46)
                    
                    # 20개 작업마다 토글 2회 실행 (브라우저 재시작 방식에서는 비활성화)
                    # 브라우저 재시작 방식을 사용할 때는 이 로직이 필요없음
                    # if i > 1 and (i - 1) % 20 == 0:
                    #     logger.info(f"20개 작업 완료 후 토글 2회 실행으로 목록 새로고침")
                    #     current_products = self._toggle_product_view()
                    #     toggle_executed = True
                    #     
                    #     # 토글 후 총상품수 확인 - 처리 가능한 상품이 있는지만 확인
                    #     if current_products == 0:
                    #         logger.warning(f"토글 후 상품이 없습니다. 작업을 중단합니다.")
                    #         logger.info(f"현재까지 처리된 상품: {result['processed']}개")
                    #         break
                    #     elif current_products < i:
                    #         logger.warning(f"토글 후 상품수({current_products})가 현재 처리 중인 상품 번호({i})보다 적습니다.")
                    #         logger.info(f"가능한 상품까지만 처리합니다. 현재까지 처리된 상품: {result['processed']}개")
                    #         # 남은 상품까지만 처리하록 quantity 조정
                    #         quantity = min(quantity, current_products)
                    #         logger.info(f"처리 목표를 {quantity}개로 조정합니다.")
                    #     else:
                    #         logger.info(f"토글 후 상품수: {current_products}개, 계속 진행합니다.")
                    
                    # 작업 시작 전 지연
                    import time
                    pre_action_delay = delay_strategy.get_delay('transition')
                    logger.info(f"작업 시작 전 지연: {pre_action_delay:.2f}초")
                    time.sleep(pre_action_delay)
                    
                    # 개별 상품 처리
                    start_time = time.time()
                    success = self._process_single_product(i)
                    actual_process_time = time.time() - start_time
                    
                    if success:
                        result['processed'] += 1
                        logger.info(f"상품 {i} 처리 완료 (소요시간: {actual_process_time:.2f}초, 누적: {result['processed']}/{quantity})")
                        
                        # 작업 성공 후 지연
                        post_action_delay = delay_strategy.get_delay('critical')
                        logger.info(f"작업 완료 후 지연: {post_action_delay:.2f}초")
                        time.sleep(post_action_delay)
                    else:
                        result['failed'] += 1
                        logger.warning(f"상품 {i} 처리 실패 (실패 누적: {result['failed']})")
                        
                        # 오류 발생 시 토글 2회 실행 시도 (이미 토글이 실행되지 않은 경우에만)
                        if not toggle_executed:
                            logger.info("작업 실패 후 토글 새로고침 시도")
                            try:
                                self._toggle_product_view()
                                toggle_executed = True
                            except Exception as refresh_error:
                                logger.error(f"새로고침 중 추가 예외 발생: {refresh_error}")
                        else:
                            logger.info("이미 토글이 실행되어 추가 토글을 건너뜁니다.")
                        
                except Exception as e:
                    result['failed'] += 1
                    result['errors'].append(f"상품 {i}: {str(e)}")
                    logger.error(f"상품 {i} 처리 중 예외 발생: {e}")
                    
                    # 예외 발생 시 토글 2회 실행 시도 (이미 토글이 실행되지 않은 경우에만)
                    if not toggle_executed:
                        logger.info("예외 발생 후 토글 새로고침 시도")
                        try:
                            self._toggle_product_view()
                            toggle_executed = True
                        except Exception as refresh_error:
                            logger.error(f"새로고침 중 추가 예외 발생: {refresh_error}")
                    else:
                        logger.info("이미 토글이 실행되어 추가 토글을 건너뜁니다.")
                
                # 남은 지연 적용 (목표 시간에 맞추기 위함)
                remaining_delay = delay_strategy.get_remaining_delay()
                if remaining_delay > 0:
                    logger.info(f"추가 지연 적용: {remaining_delay:.2f}초")
                    time.sleep(remaining_delay)
                
                # 상태 출력
                print(f"진행 상황: {i}/{quantity} (성공: {result['processed']}, 실패: {result['failed']})")
            
            # 9. 실행 후 상품 개수 확인
            try:
                # 배치 완료 후 이미 비그룹상품보기 상태이므로 바로 상품 수 확인
                import time
                time.sleep(2)  # 페이지 로딩 대기
                
                final_products = self._check_product_count()
                result['product_count_after'] = final_products
                logger.info(f"📊 실행 후 비그룹상품 수량: {final_products}개")
                
                # 비그룹상품이 0개가 되면 배치분할 중단 플래그 설정
                if final_products == 0:
                    result['should_stop_batch'] = True
                    logger.warning("⚠️ 비그룹상품이 0개가 되었습니다. 후속 배치분할을 중단합니다.")
                
                # 상품 수 변화 상세 로깅
                processed_difference = result['product_count_before'] - result['product_count_after']
                
                logger.info(f"📊 배치 실행 전 비그룹상품 수량: {result['product_count_before']}개")
                logger.info(f"📊 배치 완료 후 비그룹상품 수량: {result['product_count_after']}개")
                logger.info(f"📊 실제 처리된 상품 수량: {processed_difference}개 (감소량 기준)")
                logger.info(f"📊 요청 처리 수량: {result['processed']}개")
                logger.info(f"📈 상품 수 변화: {result['product_count_before']}개 → {result['product_count_after']}개")
                
                # 처리 결과 분석
                if processed_difference == result['processed']:
                    logger.info(f"✅ 누락 없이 정상 처리 (처리량과 감소량 일치)")
                elif processed_difference > result['processed']:
                    logger.warning(f"⚠️ 예상보다 많은 상품이 처리됨 (차이: +{processed_difference - result['processed']}개)")
                elif processed_difference < result['processed']:
                    logger.warning(f"⚠️ 일부 상품이 누락되었을 수 있음 (차이: -{result['processed'] - processed_difference}개)")
                else:
                    logger.info(f"📊 처리 수량: {result['processed']}개, 실제 감소량: {processed_difference}개")
                    
            except Exception as final_check_error:
                logger.error(f"실행 후 상품 수 확인 중 오류: {final_check_error}")
                result['product_count_after'] = -1  # 확인 실패 표시
            
            result['success'] = result['processed'] > 0
            logger.info(f"1단계 작업 완료 - 성공: {result['processed']}, 실패: {result['failed']}")
            
        except Exception as e:
            result['errors'].append(f"전체 작업 오류: {str(e)}")
            logger.error(f"1단계 작업 중 전체 오류: {e}")
        
        return result
    
    def _handle_post_login_modals(self):
        """로그인 후 모달창 처리"""
        handle_post_login_modals(self.driver)
    
    def _hide_channel_talk(self):
        """채널톡 숨기기"""
        hide_channel_talk(self.driver)
    
    def _navigate_to_ai_sourcing(self):
        """AI 소싱 메뉴로 이동"""
        navigate_to_ai_sourcing(self.driver, self.menu_clicks)
    
    def _navigate_to_group_management(self):
        """그룹상품관리 화면으로 이동"""
        navigate_to_group_management(self.driver, self.menu_clicks)
    
    def _switch_to_non_group_view(self):
        """비그룹상품보기로 전환"""
        switch_to_non_group_view(self.driver, self.menu_clicks)
    
    def _check_toggle_state(self) -> str:
        """현재 토글 상태를 확인
        
        Returns:
            str: "비그룹상품보기", "그룹상품보기", 또는 "알 수 없음"
        """
        return check_toggle_state(self.driver)
    
    def _check_product_count(self) -> int:
        """현재 상품 목록의 상품 개수를 확인
        
        Returns:
            int: 현재 상품 목록의 상품 개수. 실패시 0 반환
        """
        return check_product_count(self.driver)
    
    def _toggle_product_view(self):
        """상품 목록 새로고침을 위한 토글 2회 클릭 기능
        
        Returns:
            int: 현재 목록에 있는 상품 개수. 실패시 0 반환
        """
        return toggle_product_view(self.driver)
    
    def _process_single_product(self, index: int) -> bool:
        """
        개별 상품 처리
        
        Args:
            index: 상품 인덱스
            
        Returns:
            bool: 처리 성공 여부
        """
        try:
            logger.debug(f"상품 {index} 처리 시작")
            
            # ProductEditorCore 초기화 및 사용
            if not hasattr(self, 'product_editor') or self.product_editor is None:
                from product_editor_core import ProductEditorCore
                self.product_editor = ProductEditorCore(self.driver)
                logger.debug("ProductEditorCore 초기화")
            
            # 모달창 처리
            try:
                from modal_blocker import close_modal_dialog
                from percenty_utils import hide_channel_talk_and_modals
                close_modal_dialog(self.driver)
                hide_channel_talk_and_modals(self.driver, log_prefix="상품 처리")
            except Exception as e:
                logger.warning(f"모달창 처리 중 오류: {e}")
            
            # 실제 상품 처리
            success = self.product_editor.process_single_product()
            
            if success:
                logger.debug(f"상품 {index} 처리 성공")
            else:
                logger.warning(f"상품 {index} 처리 실패")
            
            return success
            
        except Exception as e:
            logger.error(f"상품 {index} 처리 중 오류: {e}")
            return False
    
    def cleanup(self):
        """정리 작업"""
        try:
            if self.browser_core:
                # 브라우저 정리 작업
                pass
            logger.info("1단계 코어 정리 완료")
        except Exception as e:
            logger.error(f"정리 작업 중 오류: {e}")

# 하위 호환성을 위한 함수들
def execute_step1_legacy(driver, quantity=1):
    """기존 코드와의 호환성을 위한 함수"""
    core = Step1Core(driver)
    return core.execute_step1(quantity)

if __name__ == "__main__":
    # 테스트 코드
    print("1단계 코어 모듈 테스트")
    logger.info("1단계 코어 모듈이 로드되었습니다.")