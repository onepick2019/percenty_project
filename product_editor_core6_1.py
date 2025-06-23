# -*- coding: utf-8 -*-
"""
퍼센티 상품 편집 코어 모듈 6-1단계
비그룹상품보기에 있는 상품을 수정한 후, 신규수집 그룹으로 이동하기
"""

import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# 유틸리티 모듈 임포트
from market_utils import MarketUtils
from upload_utils import UploadUtils
from dropdown_utils4 import DropdownUtils4


# 로깅 설정
logger = logging.getLogger(__name__)

class ProductEditorCore6_1:
    """
    6-1단계 상품 업로드 코어 클래스
    신규상품등록에서 쇼핑몰별로 업로드하기
    """
    
    def __init__(self, driver):
        """
        ProductEditorCore6_1 초기화
        
        Args:
            driver: WebDriver 인스턴스
        """
        self.driver = driver
        self.market_utils = MarketUtils(driver)
        self.upload_utils = UploadUtils(driver)
        self.dropdown_utils4 = DropdownUtils4(driver)
        logger.info("ProductEditorCore6_1 초기화 완료")
    
    def execute_step6_1_workflow(self):
        """
        6-1단계 워크플로우 실행
        1. 상품검색 드롭박스를 열고 쇼핑몰A1 그룹 선택
        2. 50개씩 보기 설정
        3. 상품수 확인 (0개인 경우 스킵)
        4. 전체선택
        5. 업로드 버튼 클릭해서 업로드 모달창 열고 선택 상품 일괄 업로드 클릭
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("6-1단계 워크플로우 시작")

            # 0. 마켓설정 화면 정보 처리
            logger.info("마켓설정 화면 정보 처리")

            # 1. 상품검색 드롭박스를 열고 쇼핑몰A1 그룹 선택
            if not self._select_shopping_mall_a1_group():
                logger.error("쇼핑몰A1 그룹 선택 실패")
                return False
            
            # 2. 50개씩 보기 설정
            # if not self._set_items_per_page_50():
            #    logger.error("50개씩 보기 설정 실패")
            #    return False
            
            # 3. 상품수 확인 (0개인 경우 스킵)
            product_count = self._check_product_count()
            if product_count == 0:
                logger.info("상품이 0개이므로 워크플로우를 스킵합니다")
                return True
            elif product_count == -1:
                logger.warning("상품 수 확인 실패, 계속 진행합니다")
            else:
                logger.info(f"확인된 상품 수: {product_count}개")
            
            # 4. 전체선택
            if not self._select_all_products():
                logger.error("전체선택 실패")
                return False
            
            # 5. 업로드 버튼 클릭해서 업로드 모달창 열고 선택 상품 일괄 업로드 클릭
            if not self._handle_bulk_upload():
                logger.error("일괄 업로드 처리 실패")
                return False
            
            # 6. 업로드 완료 대기 및 모달창 닫기
            if not self._wait_for_upload_completion():
                logger.warning("업로드 완료 대기 또는 모달창 닫기에 실패했지만 계속 진행합니다")
            
            logger.info("6-1단계 워크플로우 완료")
            return True
            
        except Exception as e:
            logger.error(f"6-1단계 워크플로우 실행 중 오류: {e}")
            return False
    
    def _select_shopping_mall_a1_group(self):
        """
        상품검색 드롭박스를 열고 쇼핑몰A1 그룹 선택
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("1. 상품검색 드롭박스를 열고 쇼핑몰A1 그룹 선택")
            
            # 쇼핑몰A1 그룹 선택 시도 (최대 3회 재시도)
            group_selection_success = False
            for attempt in range(3):
                try:
                    logger.info(f"쇼핑몰A1 그룹 선택 시도 {attempt + 1}/3")
                    
                    # 상품검색용 드롭박스에서 쇼핑몰A1 그룹 선택
                    if self.dropdown_utils4.select_group_in_search_dropdown("쇼핑몰A1"):
                        logger.info("쇼핑몰A1 그룹 선택 성공")
                        group_selection_success = True
                        break
                    else:
                        logger.warning(f"쇼핑몰A1 그룹 선택 실패 (시도 {attempt + 1}/3)")
                    
                    if attempt < 2:
                        time.sleep(2)  # 재시도 전 대기
                        
                except Exception as e:
                    logger.error(f"쇼핑몰A1 그룹 선택 중 오류 (시도 {attempt + 1}/3): {e}")
                    time.sleep(2)  # 재시도 전 대기
            
            if not group_selection_success:
                logger.error("쇼핑몰A1 그룹 선택에 실패했습니다.")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"쇼핑몰A1 그룹 선택 중 오류: {e}")
            return False
    
    def _set_items_per_page_50(self):
        """
        50개씩 보기 설정
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("2. 50개씩 보기 설정")
            
            # 50개씩 보기 설정 시도 (최대 3회 재시도)
            items_per_page_success = False
            for attempt in range(3):
                try:
                    logger.info(f"50개씩 보기 설정 시도 {attempt + 1}/3")
                    
                    # 50개씩 보기 설정
                    if self.dropdown_utils4.select_page_size("50"):
                        logger.info("50개씩 보기 설정 성공")
                        items_per_page_success = True
                        break
                    else:
                        logger.warning(f"50개씩 보기 설정 실패 (시도 {attempt + 1}/3)")
                        time.sleep(2)  # 재시도 전 대기
                        
                except Exception as e:
                    logger.error(f"50개씩 보기 설정 중 오류 (시도 {attempt + 1}/3): {e}")
                    time.sleep(2)  # 재시도 전 대기
            
            if not items_per_page_success:
                logger.error("50개씩 보기 설정에 실패했습니다.")
                return False
            
            # 설정 완료 후 페이지 로드 대기
            time.sleep(2)
            return True
            
        except Exception as e:
            logger.error(f"50개씩 보기 설정 중 오류: {e}")
            return False
    
    def _check_product_count(self):
        """
        상품 수 확인
        
        Returns:
            int: 상품 수 (0개인 경우 0, 확인 실패 시 -1)
        """
        try:
            logger.info("3. 상품 수 확인")
            
            # dropdown_utils4의 get_total_product_count 메서드 사용
            product_count = self.dropdown_utils4.get_total_product_count()
            
            if product_count == -1:
                logger.warning("상품 수 확인 실패")
                return -1
            elif product_count == 0:
                logger.info("상품이 0개입니다")
                return 0
            else:
                logger.info(f"확인된 상품 수: {product_count}개")
                return product_count
            
        except Exception as e:
            logger.error(f"상품 수 확인 중 오류: {e}")
            return -1
    
    def _select_all_products(self):
        """
        전체 상품 선택
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("4. 전체 상품 선택")
            
            # dropdown_utils4의 select_all_products 메서드 사용
            if not self.dropdown_utils4.select_all_products():
                logger.error("전체 상품 선택 실패")
                return False
            
            logger.info("전체 상품 선택 완료")
            return True
            
        except Exception as e:
            logger.error(f"전체 상품 선택 중 오류: {e}")
            return False
    
    def _handle_bulk_upload(self):
        """
        업로드 버튼 클릭해서 업로드 모달창 열고 선택 상품 일괄 업로드 클릭
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("5. 업로드 버튼 클릭해서 업로드 모달창 열고 선택 상품 일괄 업로드 클릭")
            
            # 업로드 버튼 클릭
            if not self.upload_utils.click_upload_button():
                logger.error("업로드 버튼 클릭 실패")
                return False
            
            logger.info("업로드 버튼 클릭 성공")
            
            # 업로드 모달창 처리 (선택 상품 일괄 업로드)
            if not self.upload_utils.handle_upload_modal():
                logger.error("업로드 모달창 처리 실패")
                return False
            
            logger.info("일괄 업로드 처리 완료")
            return True
            
        except Exception as e:
            logger.error(f"일괄 업로드 처리 중 오류: {e}")
            return False
    
    def _wait_for_upload_completion(self):
        """
        업로드 완료 대기 및 모달창 닫기
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("6. 업로드 완료 대기 및 모달창 닫기")
            
            # upload_utils의 메서드를 사용하여 업로드 완료 대기 및 모달창 닫기
            if not self.upload_utils.wait_for_upload_completion_and_close():
                logger.error("업로드 완료 대기 또는 모달창 닫기 실패")
                return False
            
            logger.info("업로드 완료 대기 및 모달창 닫기 완료")
            return True
            
        except Exception as e:
            logger.error(f"업로드 완료 대기 중 오류: {e}")
            return False
    
    def modify_products_in_non_group_view(self):
        """
        비그룹상품보기에서 상품 수정
        
        Returns:
            bool: 상품 수정 성공 여부
        """
        try:
            logger.info("비그룹상품보기에서 상품 수정 시작")
            
            # TODO: 상품 수정 로직 구현
            
            logger.info("비그룹상품보기에서 상품 수정 완료")
            return True
            
        except Exception as e:
            logger.error(f"상품 수정 중 오류 발생: {e}")
            return False
    
    def move_to_new_collection_group(self):
        """
        신규수집 그룹으로 이동
        
        Returns:
            bool: 그룹 이동 성공 여부
        """
        try:
            logger.info("신규수집 그룹으로 이동 시작")
            
            # TODO: 신규수집 그룹 이동 로직 구현
            
            logger.info("신규수집 그룹으로 이동 완료")
            return True
            
        except Exception as e:
            logger.error(f"신규수집 그룹 이동 중 오류 발생: {e}")
            return False