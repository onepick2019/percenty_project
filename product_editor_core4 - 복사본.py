# -*- coding: utf-8 -*-
"""
퍼센티 상품 편집 코어 4단계
일괄 번역 기능을 위한 코어 모듈

주요 기능:
- 서버1 그룹 선택
- 50개씩 보기 설정
- 전체 상품 선택
- 일괄 번역 모달 처리 (사용량 확인 후 진행/중단 결정)
"""

import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# 유틸리티 모듈 임포트
from upload_utils import UploadUtils
from dropdown_utils4 import DropdownUtils4
from dropdown_utils import PercentyDropdown

# 로깅 설정
logger = logging.getLogger(__name__)

class ProductEditorCore4:
    """
    퍼센티 상품 편집 코어 4단계 클래스
    일괄 번역 기능을 담당
    """
    
    def __init__(self, driver, config=None):
        """
        ProductEditorCore4 초기화
        
        Args:
            driver: Selenium WebDriver 인스턴스
            config: 설정 딕셔너리 (선택사항)
        """
        self.driver = driver
        self.config = config or {}
        
        # 유틸리티 인스턴스 초기화
        self.upload_utils = UploadUtils(driver)
        self.dropdown_utils4 = DropdownUtils4(driver)  # Step4 전용 드롭다운 및 체크박스 유틸리티
        self.dropdown_utils = PercentyDropdown(driver)  # 기타 드롭다운용 (호환성 유지)
        
        logger.info("ProductEditorCore4 초기화 완료")
    
    def execute_bulk_translation_workflow(self):
        """
        전체 일괄 번역 워크플로우 실행 (서버1→대기1, 서버2→대기2, 서버3→대기3)
        서버3 완료 후 번역 가능 횟수가 50개 이상이면 다시 서버1부터 반복
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("\n\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            logger.info("!!! 전체 일괄번역 워크플로우 시작 !!!")
            logger.info("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n")
            
            # 서버별 처리 설정
            server_configs = [
                {"server": "서버1", "waiting_group": "대기1"},
                {"server": "서버2", "waiting_group": "대기2"},
                {"server": "서버3", "waiting_group": "대기3"}
            ]
            
            cycle_count = 0
            
            while True:
                cycle_count += 1
                logger.info(f"\n\n*** 사이클 {cycle_count} 시작 ***")
                
                # 각 서버별로 순차 처리
                for i, config in enumerate(server_configs, 1):
                    logger.info(f"\n=== 사이클 {cycle_count}, {i}단계: {config['server']} → {config['waiting_group']} 처리 시작 ===")
                    
                    if not self._execute_single_server_workflow(config['server'], config['waiting_group']):
                        logger.warning(f"{config['server']} → {config['waiting_group']} 처리 스킵: 번역 횟수 부족")
                        logger.info(f"사이클 {cycle_count} 중단: 번역 횟수 부족으로 전체 워크플로우 종료")
                        return False
                    
                    logger.info(f"=== 사이클 {cycle_count}, {i}단계: {config['server']} → {config['waiting_group']} 처리 완료 ===\n")
                
                logger.info(f"*** 사이클 {cycle_count} 완료 ***")
                
                # 서버3 완료 후 번역 가능 횟수 확인 (주석처리: 사이클 2 시작 방해)
                # available_translations = self._check_available_translations()
                # if available_translations is None:
                #     logger.warning("번역 가능 횟수를 확인할 수 없어 워크플로우를 종료합니다")
                #     return True
                # 
                # logger.info(f"현재 사용 가능한 번역 횟수: {available_translations}회")
                # 
                # if available_translations < 50:
                #     logger.info(f"번역 가능 횟수가 50개 미만({available_translations}회)이므로 워크플로우를 종료합니다")
                #     break
                # else:
                #     logger.info(f"번역 가능 횟수가 50개 이상({available_translations}회)이므로 다음 사이클을 시작합니다")
                #     time.sleep(2)  # 다음 사이클 시작 전 잠시 대기
                
                # 임시로 무한 루프 방지를 위해 최대 3사이클로 제한
                if cycle_count >= 3:
                    logger.info(f"최대 사이클 수({cycle_count})에 도달하여 워크플로우를 종료합니다")
                    break
                
                logger.info(f"사이클 {cycle_count} 완료, 다음 사이클을 시작합니다")
                time.sleep(2)  # 다음 사이클 시작 전 잠시 대기
            
            logger.info(f"전체 일괄 번역 워크플로우 완료 (총 {cycle_count}사이클 실행)")
            return True
            
        except Exception as e:
            logger.error(f"전체 일괄 번역 워크플로우 실행 중 오류: {e}")
            return False
    
    def _execute_single_server_workflow(self, server_name, waiting_group):
        """
        단일 서버에 대한 일괄 번역 워크플로우 실행
        
        Args:
            server_name (str): 서버 이름 (예: "서버1")
            waiting_group (str): 대기 그룹 이름 (예: "대기1")
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"{server_name} → {waiting_group} 워크플로우 시작")
            
            # 1. 상품검색 드롭박스를 열고 서버 그룹 선택
            if not self._select_server_group(server_name):
                logger.error(f"{server_name} 그룹 선택 실패")
                return False
            
            # 2. 50개씩 보기 설정 (디버깅용 주석처리)
            if not self._set_items_per_page_50():
                logger.error("50개씩 보기 설정 실패")
                return False
            
            # 3. 상품수 확인 (0개인 경우 스킵)
            if self._check_product_count_zero():
                logger.info(f"{server_name}에 상품이 없어 워크플로우를 스킵합니다")
                return True  # 스킵은 성공으로 처리
            
            # 4. 전체선택
            if not self._select_all_products():
                logger.error("전체 상품 선택 실패")
                return False
            
            # 5. 일괄 번역 처리
            if not self._handle_bulk_translation():
                logger.warning("일괄 번역 스킵: 번역 횟수 부족으로 해당 서버 처리 중단")
                return False
            
            # 6. 전체선택
            if not self._select_all_products():
                logger.error("전체선택 실패")
                return False
            
            # 7. 그룹지정 모달창 열어서 대기 그룹으로 이동
            if not self._move_to_waiting_group(waiting_group):
                logger.error(f"{waiting_group} 그룹으로 이동 실패")
                return False
            
            logger.info(f"{server_name} → {waiting_group} 워크플로우 완료")
            return True
            
        except Exception as e:
            logger.error(f"{server_name} → {waiting_group} 워크플로우 실행 중 오류: {e}")
            return False
    
    def _select_server_group(self, server_name):
        """
        상품검색 드롭박스를 열고 지정된 서버 그룹 선택
        
        Args:
            server_name (str): 선택할 서버 이름 (예: "서버1", "서버2", "서버3")
            
        Returns:
            bool: 성공 여부
        """
        logger.info(f"상품검색용 드롭박스에서 '{server_name}' 그룹 선택")
        
        # 서버 그룹 선택 시도 (최대 3회 재시도)
        group_selection_success = False
        for attempt in range(3):
            try:
                logger.info(f"{server_name} 그룹 선택 시도 {attempt + 1}/3")
                
                # 상품검색용 드롭박스에서 서버 그룹 선택
                if self.dropdown_utils4.select_group_in_search_dropdown(server_name):
                    logger.info(f"{server_name} 그룹 선택 성공")
                    group_selection_success = True
                    break
                else:
                    logger.warning(f"{server_name} 그룹 선택 실패 (시도 {attempt + 1}/3)")
                
                if attempt < 2:
                    time.sleep(2)  # DELAY_MEDIUM
                    
            except Exception as e:
                logger.error(f"{server_name} 그룹 선택 중 오류 (시도 {attempt + 1}/3): {e}")
                time.sleep(2)  # DELAY_MEDIUM
        
        if not group_selection_success:
            logger.error(f"{server_name} 그룹 선택에 실패했습니다.")
            return False
        
        return True
    
    def _set_items_per_page_50(self):
        """
        50개씩 보기 설정
        
        Returns:
            bool: 성공 여부
        """
        logger.info("1-2. 50개씩 보기 설정")
        
        # 50개씩 보기 설정 시도 (최대 3회 재시도)
        items_per_page_success = False
        for attempt in range(3):
            try:
                logger.info(f"50개씩 보기 설정 시도 {attempt + 1}/3")
                
                # 50개씩 보기 설정 (새로운 dropdown_utils4 사용)
                if self.dropdown_utils4.select_page_size("50"):
                    logger.info("50개씩 보기 설정 성공")
                    items_per_page_success = True
                    break
                else:
                    logger.warning(f"50개씩 보기 설정 실패 (시도 {attempt + 1}/3)")
                    time.sleep(2)  # DELAY_MEDIUM
                    
            except Exception as e:
                logger.error(f"50개씩 보기 설정 중 오류 (시도 {attempt + 1}/3): {e}")
                time.sleep(2)  # DELAY_MEDIUM
        
        if not items_per_page_success:
            logger.error("50개씩 보기 설정에 실패했습니다.")
            return False
        
        # 설정 완료 후 페이지 로드 대기
        time.sleep(2)  # DELAY_MEDIUM
        return True
    
    def _select_all_products(self):
        """
        전체 상품 선택
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("전체 상품 선택")
            
            # dropdown_utils4의 select_all_products 메서드 사용
            if not self.dropdown_utils4.select_all_products():
                logger.error("전체 상품 선택 실패")
                return False
            
            logger.info("전체 상품 선택 완료")
            return True
            
        except Exception as e:
            logger.error(f"전체 상품 선택 중 오류: {e}")
            return False
    
    def _handle_bulk_translation(self):
        """
        일괄 번역 처리 (모달 열기, 사용량 확인, 진행/중단 결정)
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("1-4. 일괄 번역 처리 시작")
            
            # 일괄 번역 버튼 클릭
            if not self.upload_utils.click_batch_translate_button():
                logger.error("일괄 번역 버튼 클릭 실패")
                return False
            
            # 일괄 번역 모달 처리 (사용량 확인 후 진행/중단 결정)
            if not self.upload_utils.handle_batch_translate_modal():
                logger.warning("일괄 번역 불가능: 사용 가능한 번역 횟수 부족으로 스킵")
                return False
            
            logger.info("일괄 번역 처리 완료")
            
            # 일괄번역 완료 후 안정성을 위한 강제 지연
            time.sleep(3)
            logger.info("일괄번역 후 3초 지연 완료")
            
            return True
            
        except Exception as e:
            logger.error(f"일괄 번역 처리 중 오류: {e}")
            return False
    
    def get_selected_product_count(self):
        """
        선택된 상품 수 조회
        
        Returns:
            int: 선택된 상품 수 (실패 시 0)
        """
        try:
            return self.upload_utils.get_selected_product_count()
        except Exception as e:
            logger.error(f"선택된 상품 수 조회 중 오류: {e}")
            return 0
    
    def perform_complete_bulk_translate_workflow(self):
        """
        완전한 일괄 번역 워크플로우 실행 (편의 메서드)
        upload_utils의 perform_complete_batch_translate_workflow 래핑
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("완전한 일괄 번역 워크플로우 실행")
            return self.upload_utils.perform_complete_batch_translate_workflow()
        except Exception as e:
            logger.error(f"완전한 일괄 번역 워크플로우 실행 중 오류: {e}")
            return False
    

    
    def _move_to_waiting_group(self, waiting_group):
        """
        그룹지정 모달창을 열어서 지정된 대기 그룹으로 이동
        
        Args:
            waiting_group (str): 이동할 대기 그룹 이름 (예: "대기1", "대기2", "대기3")
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"그룹지정 모달창을 열어서 '{waiting_group}' 그룹으로 이동")
            
            # 그룹지정 모달창 열기
            if not self.dropdown_utils4.open_group_assignment_modal():
                logger.error("그룹지정 모달창 열기 실패")
                return False
            
            logger.info("그룹지정 모달창 열기 성공")
            
            # 대기 그룹 선택
            if not self.dropdown_utils4.select_group_in_modal(waiting_group):
                logger.error(f"'{waiting_group}' 그룹 선택 실패")
                return False
            
            logger.info(f"'{waiting_group}' 그룹으로 이동 완료")
            return True
            
        except Exception as e:
            logger.error(f"{waiting_group} 그룹으로 이동 중 오류: {e}")
            return False
    
    def _check_available_translations(self):
        """
        현재 사용 가능한 번역 횟수를 확인
        
        Returns:
            int: 사용 가능한 번역 횟수, 확인 실패 시 None
        """
        try:
            logger.info("번역 가능 횟수 확인을 위해 일괄 번역 모달을 임시로 엽니다")
            
            # 임시로 상품 하나라도 선택되어 있는지 확인
            if not self._select_all_products():
                logger.error("번역 횟수 확인을 위한 상품 선택 실패")
                return None
            
            # 일괄 번역 버튼 클릭하여 모달 열기
            if not self.upload_utils.click_batch_translate_button():
                logger.error("번역 횟수 확인을 위한 일괄 번역 버튼 클릭 실패")
                return None
            
            # 모달에서 번역 가능 횟수 확인
            available_translations = self.upload_utils._get_available_translation_count()
            
            # 모달 닫기
            self.upload_utils.close_batch_translate_modal()
            
            if available_translations is not None:
                logger.info(f"번역 가능 횟수 확인 완료: {available_translations}회")
            else:
                logger.warning("번역 가능 횟수 확인 실패")
            
            return available_translations
            
        except Exception as e:
            logger.error(f"번역 가능 횟수 확인 중 오류: {e}")
            # 오류 발생 시 모달이 열려있을 수 있으므로 닫기 시도
            try:
                self.upload_utils.close_batch_translate_modal()
            except:
                pass
            return None
    
    def _check_product_count_zero(self):
        """
        상품수가 0개인지 확인
        
        Returns:
            bool: 상품수가 0개이면 True, 아니면 False
        """
        try:
            logger.info("상품수 확인 중...")
            
            # '총 0개 상품' 텍스트를 찾는 선택자들
            selectors = [
                "//span[contains(text(), '총 0개 상품')]",
                "//span[text()='총 0개 상품']",
                ".ant-checkbox-wrapper span:contains('총 0개 상품')",
                "span:contains('총 0개 상품')"
            ]
            
            for selector in selectors:
                try:
                    if selector.startswith('//'):
                        # XPath 선택자
                        element = self.driver.find_element(By.XPATH, selector)
                    else:
                        # CSS 선택자 (contains는 CSS에서 지원되지 않으므로 XPath로 변환)
                        if ':contains' in selector:
                            xpath_selector = f"//span[contains(text(), '총 0개 상품')]"
                            element = self.driver.find_element(By.XPATH, xpath_selector)
                        else:
                            element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if element and element.is_displayed():
                        logger.info("상품수가 0개임을 확인했습니다")
                        return True
                        
                except NoSuchElementException:
                    continue
                except Exception as e:
                    logger.debug(f"선택자 {selector} 확인 중 오류: {e}")
                    continue
            
            logger.info("상품이 존재합니다")
            return False
            
        except Exception as e:
            logger.error(f"상품수 확인 중 오류: {e}")
            return False  # 오류 시 안전하게 진행

# 편의 함수들
def batch_translate_products(driver, config=None):
    """
    일괄 번역 편의 함수
    
    Args:
        driver: Selenium WebDriver 인스턴스
        config: 설정 딕셔너리 (선택사항)
        
    Returns:
        bool: 성공 여부
    """
    core = ProductEditorCore4(driver, config)
    return core.execute_bulk_translation_workflow()