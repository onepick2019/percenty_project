# -*- coding: utf-8 -*-
"""
6-1단계 동적 업로드 처리 코어 (market_id 시트 기반)

percenty_id.xlsx의 market_id 시트를 파싱하여 동적으로 업로드를 진행합니다.
- 로그인 아이디와 매핑되는 행들을 순차적으로 처리
- 11번가 마켓 설정 및 API 연동
- 동적 그룹 선택 및 업로드 진행
"""

import logging
import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from dropdown_utils4 import DropdownUtils4
from upload_utils import UploadUtils
from market_utils import MarketUtils

logger = logging.getLogger(__name__)

class ProductEditorCore6_1Dynamic:
    """6-1단계 동적 업로드 처리 코어 클래스"""
    
    def __init__(self, driver, account_id, excel_path="percenty_id.xlsx"):
        self.driver = driver
        self.account_id = account_id
        self.excel_path = excel_path
        self.wait = WebDriverWait(driver, 10)
        
        # 유틸리티 클래스 초기화
        self.dropdown_utils = DropdownUtils4(driver)
        self.upload_utils = UploadUtils(driver)
        self.market_utils = MarketUtils(driver, logger)
        
        logger.info(f"ProductEditorCore6_1Dynamic 초기화 완료 - 계정: {account_id}")
    
    def load_market_config_from_excel(self):
        """
        percenty_id.xlsx의 market_id 시트에서 로그인 아이디와 매핑되는 마켓 설정 정보를 로드합니다.
        
        Returns:
            list: 마켓 설정 정보 리스트 (각 행의 데이터)
        """
        try:
            logger.info(f"계정 {self.account_id}의 마켓 설정 정보를 로드합니다.")
            
            # market_id 시트에서 데이터 로드
            market_df = pd.read_excel(self.excel_path, sheet_name="market_id")
            
            # 로그인 아이디와 매핑되는 행들 필터링 (A열 id와 매칭)
            account_rows = market_df[market_df['id'] == self.account_id]
            
            if account_rows.empty:
                logger.error(f"계정 {self.account_id}에 대한 마켓 설정 정보를 찾을 수 없습니다.")
                return []
            
            # 행 순서대로 정렬하여 반환
            account_rows = account_rows.reset_index(drop=True)
            
            logger.info(f"계정 {self.account_id}에 대한 마켓 설정 {len(account_rows)}개 로드 완료")
            
            # 각 행의 데이터를 딕셔너리로 변환하여 리스트로 반환
            market_configs = []
            for idx, row in account_rows.iterrows():
                config = {
                    'id': row.get('id', ''),
                    'groupname': row.get('groupname', ''),  # B열
                    '11store_api': row.get('11store_api', ''),  # C열
                    'row_index': idx + 1  # 행 번호 (1부터 시작)
                }
                market_configs.append(config)
                logger.info(f"마켓 설정 {idx+1}: 그룹명={config['groupname']}, API키={config['11store_api'][:10]}...")
            
            return market_configs
            
        except Exception as e:
            logger.error(f"마켓 설정 정보 로드 중 오류 발생: {e}")
            return []
    
    def setup_market_configuration(self, market_config):
        """
        마켓 설정 화면에서 11번가 API 설정을 진행합니다.
        
        Args:
            market_config (dict): 마켓 설정 정보
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"마켓 설정 화면 정보 처리 시작 - 그룹: {market_config['groupname']}")
            
            # 1. 마켓설정 화면 열기
            if not self._open_market_settings():
                logger.error("마켓설정 화면 열기 실패")
                return False
            
            # 2. 모든 마켓 API 연결 끊기 (11번가만 사용하기 위해)
            if not self._disconnect_all_market_apis():
                logger.error("마켓 API 연결 끊기 실패")
                return False
            
            # 3. 11번가-일반 탭 선택
            if not self.market_utils.click_market_tab('11st_general'):
                logger.error("11번가-일반 탭 선택 실패")
                return False
            
            # 4. API KEY 입력
            if not self._input_11st_api_key(market_config['11store_api']):
                logger.error("11번가 API KEY 입력 실패")
                return False
            
            # 5. API 검증 진행
            if not self.market_utils.perform_complete_11st_api_verification_workflow():
                logger.error("11번가 API 검증 실패")
                return False
            
            logger.info("마켓 설정 화면 정보 처리 완료")
            return True
            
        except Exception as e:
            logger.error(f"마켓 설정 화면 정보 처리 중 오류 발생: {e}")
            return False
    
    def _open_market_settings(self):
        """
        마켓설정 화면을 엽니다.
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("마켓설정 메뉴 클릭 시도")
            
            # DOM 선택자 - span.ant-menu-title-content 중에서 '마켓 설정' 텍스트를 가진 요소
            market_settings_selectors = [
                "//span[@class='ant-menu-title-content' and text()='마켓 설정']",
                "//span[contains(@class, 'ant-menu-title-content')][contains(., '마켓 설정')]",
                "//li[contains(@data-menu-id, 'MARKET_SETTING')]//span[contains(@class, 'ant-menu-title-content')]"
            ]
            
            for selector in market_settings_selectors:
                try:
                    element = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    element.click()
                    logger.info("마켓설정 화면 열기 완료")
                    
                    # 마켓설정 화면 로드 대기
                    time.sleep(3)
                    
                    # 스크롤을 최상단으로 초기화
                    self.driver.execute_script("window.scrollTo(0, 0);")
                    logger.info("스크롤 위치를 최상단으로 초기화")
                    
                    return True
                except TimeoutException:
                    continue
            
            logger.error("마켓설정 화면 열기 실패 - 요소를 찾을 수 없음")
            return False
            
        except Exception as e:
            logger.error(f"마켓설정 화면 열기 중 오류 발생: {e}")
            return False
    
    def _disconnect_all_market_apis(self):
        """
        모든 마켓의 API 연결을 끊습니다.
        
        Returns:
            bool: 성공 여부
        """
        try:
            # 모든 마켓들의 API 연결 끊기
            markets_to_disconnect = [
                'smartstore', 'coupang', 'auction_gmarket', 
                '11st_general', '11st_global', 'lotteon', 'kakao'
            ]
            
            for market in markets_to_disconnect:
                try:
                    logger.info(f"{market} API 연결 끊기 시도")
                    
                    # 각 마켓별 개별 메서드 직접 호출 (처리 순서와 일치)
                    if market == 'smartstore':
                        success = self.market_utils.disconnect_smartstore_api()
                    elif market == 'coupang':
                        success = self.market_utils.disconnect_coupang_api()
                    elif market == 'auction_gmarket':
                        success = self.market_utils.disconnect_auction_gmarket_api()
                    elif market == '11st_general':
                        success = self.market_utils.disconnect_11st_general_api()
                    elif market == '11st_global':
                        success = self.market_utils.disconnect_11st_global_api()
                    elif market == 'lotteon':
                        success = self.market_utils.disconnect_lotteon_api()
                    elif market == 'kakao':
                        success = self.market_utils.disconnect_kakao_api()
                    else:
                        logger.warning(f"지원하지 않는 마켓: {market}")
                        continue
                    
                    if success:
                        logger.info(f"{market} API 연결 끊기 성공")
                    else:
                        logger.warning(f"{market} API 연결 끊기 실패")
                    
                    time.sleep(1)
                except Exception as e:
                    logger.warning(f"{market} API 연결 끊기 중 오류 (무시하고 계속): {e}")
                    continue
            
            logger.info("모든 마켓 API 연결 끊기 완료")
            return True
            
        except Exception as e:
            logger.error(f"마켓 API 연결 끊기 중 오류 발생: {e}")
            return False
    
    def _input_11st_api_key(self, api_key):
        """
        11번가 API KEY를 입력합니다.
        
        Args:
            api_key (str): API 키
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("11번가 API KEY 입력 시작")
            
            # market_utils의 메서드를 사용하여 API KEY 입력
            success = self.market_utils.input_11st_general_api_key(api_key)
            
            if success:
                logger.info(f"11번가 API KEY 입력 완료: {api_key[:10]}...")
                return True
            else:
                logger.error("11번가 API KEY 입력 실패")
                return False
                
        except Exception as e:
            logger.error(f"11번가 API KEY 입력 중 오류 발생: {e}")
            return False
    
    def _navigate_to_product_registration(self):
        """
        신규상품등록 화면으로 전환합니다.
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("신규상품등록 화면으로 전환 시작")
            
            # DOM 선택자 - span.ant-menu-title-content 중에서 '신규 상품 등록' 텍스트를 가진 요소
            selectors = [
                "//span[@class='ant-menu-title-content' and text()='신규 상품 등록']",
                "//span[contains(@class, 'ant-menu-title-content')][contains(., '신규 상품')]",
                "//li[contains(@data-menu-id, 'PRODUCT_REGISTER')]//span[contains(@class, 'ant-menu-title-content')]"
            ]
            
            for selector in selectors:
                try:
                    element = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    element.click()
                    logger.info("신규상품등록 메뉴 클릭 완료")
                    
                    # 신규상품등록 화면 로드 대기
                    time.sleep(5)
                    
                    # 스크롤을 최상단으로 초기화
                    self.driver.execute_script("window.scrollTo(0, 0);")
                    logger.info("스크롤 위치를 최상단으로 초기화")
                    
                    logger.info("신규상품등록 화면으로 전환 완료")
                    return True
                except TimeoutException:
                    continue
            
            logger.error("신규상품등록 화면 전환 실패 - 요소를 찾을 수 없음")
            return False
            
        except Exception as e:
            logger.error(f"신규상품등록 화면 전환 중 오류 발생: {e}")
            return False
    
    def _select_dynamic_group(self, group_name):
        """
        엑셀에서 파싱한 그룹명으로 동적으로 그룹을 선택합니다.
        
        Args:
            group_name (str): 선택할 그룹명
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"동적 그룹 선택 시작: {group_name}")
            
            # 상품검색 드롭박스에서 그룹 선택 (드롭박스 열기 + 그룹 선택 통합)
            if not self.dropdown_utils.select_group_in_search_dropdown(group_name):
                logger.error(f"그룹 선택 실패: {group_name}")
                return False
            
            logger.info(f"동적 그룹 선택 완료: {group_name}")
            return True
            
        except Exception as e:
            logger.error(f"동적 그룹 선택 중 오류 발생: {e}")
            return False
    
    def _execute_product_upload_workflow(self, group_name):
        """
        product_editor_core6_1의 상품 업로드 워크플로우를 실행합니다.
        
        Args:
            group_name (str): 업로드할 그룹명
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"상품 업로드 워크플로우 시작: {group_name}")
            
            # 1. 상품 수 확인 (0개인 경우 스킵)
            product_count = self._check_product_count()
            if product_count == 0:
                logger.info(f"그룹 '{group_name}'에 상품이 0개이므로 워크플로우를 스킵합니다")
                return True
            elif product_count == -1:
                logger.warning("상품 수 확인 실패, 계속 진행합니다")
            else:
                logger.info(f"확인된 상품 수: {product_count}개")
            
            # 2. 전체선택
            if not self._select_all_products():
                logger.error("전체선택 실패")
                return False
            
            # 3. 업로드 버튼 클릭해서 업로드 모달창 열고 선택 상품 일괄 업로드 클릭
            if not self._handle_bulk_upload():
                logger.error("일괄 업로드 처리 실패")
                return False
            
            # 4. 업로드 완료 대기 및 모달창 닫기
            if not self._wait_for_upload_completion():
                logger.warning("업로드 완료 대기 또는 모달창 닫기에 실패했지만 계속 진행합니다")
            
            logger.info(f"상품 업로드 워크플로우 완료: {group_name}")
            return True
            
        except Exception as e:
            logger.error(f"상품 업로드 워크플로우 실행 중 오류: {e}")
            return False
    
    def _check_product_count(self):
        """
        상품 수 확인
        
        Returns:
            int: 상품 수 (0개인 경우 0, 확인 실패 시 -1)
        """
        try:
            logger.info("상품 수 확인")
            
            # dropdown_utils4의 get_total_product_count 메서드 사용
            product_count = self.dropdown_utils.get_total_product_count()
            
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
            logger.info("전체 상품 선택")
            
            # dropdown_utils4의 select_all_products 메서드 사용
            if not self.dropdown_utils.select_all_products():
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
            logger.info("업로드 버튼 클릭해서 업로드 모달창 열고 선택 상품 일괄 업로드 클릭")
            
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
        업로드 완료를 대기하고 모달창을 닫습니다.
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("업로드 완료 대기 및 모달창 닫기")
            
            # upload_utils의 메서드를 사용하여 업로드 완료 대기 및 모달창 닫기
            if not self.upload_utils.wait_for_upload_completion_and_close():
                logger.error("업로드 완료 대기 또는 모달창 닫기 실패")
                return False
            
            logger.info("업로드 완료 대기 및 모달창 닫기 완료")
            return True
            
        except Exception as e:
            logger.error(f"업로드 완료 대기 중 오류: {e}")
            return False
    
    def execute_dynamic_upload_workflow(self):
        """
        동적 업로드 워크플로우를 실행합니다.
        percenty_id.xlsx의 market_id 시트를 기반으로 순차적으로 처리합니다.
        
        Returns:
            bool: 전체 워크플로우 성공 여부
        """
        try:
            logger.info("6-1단계 동적 업로드 워크플로우 시작")
            
            # 1. 마켓 설정 정보 로드
            market_configs = self.load_market_config_from_excel()
            if not market_configs:
                logger.error("마켓 설정 정보 로드 실패")
                return False
            
            # 2. 각 마켓 설정에 대해 순차적으로 처리
            for idx, market_config in enumerate(market_configs, 1):
                logger.info(f"=== 마켓 설정 {idx}/{len(market_configs)} 처리 시작 ===")
                logger.info(f"그룹명: {market_config['groupname']}, API키: {market_config['11store_api'][:10]}...")
                
                # 2-1. 마켓 설정 화면 정보 처리
                if not self.setup_market_configuration(market_config):
                    logger.error(f"마켓 설정 {idx} 처리 실패")
                    continue
                
                # 2-2. 신규상품등록 화면으로 전환
                if not self._navigate_to_product_registration():
                    logger.error(f"신규상품등록 화면 전환 실패")
                    continue
                
                # 2-3. 상품검색 드롭박스를 열고 동적 그룹 선택
                if not self._select_dynamic_group(market_config['groupname']):
                    logger.error(f"동적 그룹 선택 실패: {market_config['groupname']}")
                    continue
                
                # 2-4. 상품 업로드 워크플로우 실행 (product_editor_core6_1 기능 통합)
                if not self._execute_product_upload_workflow(market_config['groupname']):
                    logger.error(f"상품 업로드 워크플로우 실패: {market_config['groupname']}")
                    continue
                
                logger.info(f"=== 마켓 설정 {idx}/{len(market_configs)} 처리 완료 ===")
                
                # 다음 설정 처리를 위한 대기
                time.sleep(2)
            
            logger.info("6-1단계 동적 업로드 워크플로우 완료")
            return True
            
        except Exception as e:
            logger.error(f"동적 업로드 워크플로우 중 오류 발생: {e}")
            return False

# 사용 예시
if __name__ == "__main__":
    # 테스트용 코드
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # 실제 사용 시에는 WebDriver 인스턴스와 계정 ID를 전달
    # driver = webdriver.Chrome()
    # account_id = "test@example.com"
    # core = ProductEditorCore6_1Dynamic(driver, account_id)
    # result = core.execute_dynamic_upload_workflow()
    print("ProductEditorCore6_1Dynamic 모듈 로드 완료")