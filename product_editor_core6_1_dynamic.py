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
                # 안전한 값 추출 함수
                def safe_get(value):
                    if pd.isna(value) or value is None:
                        return ''
                    return str(value).strip()
                
                config = {
                    'id': safe_get(row.get('id', '')),
                    'groupname': safe_get(row.get('groupname', '')),  # B열
                    '11store_api': safe_get(row.get('11store_api', '')),  # C열
                    '11global_api': safe_get(row.get('11global_api', '')),  # D열
                    'auction_id': safe_get(row.get('auction_id', '')),  # E열
                    'gmarket_id': safe_get(row.get('gmarket_id', '')),  # F열
                    'talkstore_api': safe_get(row.get('talkstore_api', '')),  # G열
                    'talkstore_url': safe_get(row.get('talkstore_url', '')),  # H열
                    'smartstore_api': safe_get(row.get('smartstore_api', '')),  # I열
                    'smartstore_id': safe_get(row.get('smartstore_id', '')),  # J열
                    'coupang_id': safe_get(row.get('coupang_id', '')),  # K열
                    'coupang_code': safe_get(row.get('coupang_code', '')),  # L열
                    'coupang_access': safe_get(row.get('coupang_access', '')),  # M열
                    'coupang_secret': safe_get(row.get('coupang_secret', '')),  # N열
                    'row_index': idx + 1  # 행 번호 (1부터 시작)
                }
                market_configs.append(config)
                # 모든 API 키 정보를 로그에 출력
                api_info = []
                if config['11store_api']:
                    api_info.append(f"11번가일반API={config['11store_api'][:10]}...")
                if config['11global_api']:
                    api_info.append(f"11번가글로벌API={config['11global_api'][:10]}...")
                if config['auction_id']:
                    api_info.append(f"옥션ID={config['auction_id']}")
                if config['gmarket_id']:
                    api_info.append(f"지마켓ID={config['gmarket_id']}")
                if config['talkstore_api']:
                    api_info.append(f"톡스토어API={config['talkstore_api'][:10]}...")
                if config['talkstore_url']:
                    api_info.append(f"톡스토어URL={config['talkstore_url'][:30]}...")
                if config['smartstore_api']:
                    api_info.append(f"스마트스토어API={config['smartstore_api']}")
                if config['smartstore_id']:
                    api_info.append(f"스마트스토어ID={config['smartstore_id']}")
                if config['coupang_id']:
                    api_info.append(f"쿠팡ID={config['coupang_id']}")
                if config['coupang_access']:
                    api_info.append(f"쿠팡ACCESS={config['coupang_access'][:10]}...")
                
                api_info_str = ", ".join(api_info) if api_info else "API 키 없음"
                logger.info(f"마켓 설정 {idx+1}: 그룹명={config['groupname']}, {api_info_str}")
            
            return market_configs
            
        except Exception as e:
            logger.error(f"마켓 설정 정보 로드 중 오류 발생: {e}")
            return []
    
    def setup_market_configuration(self, market_config):
        """
        마켓 설정 화면에서 모든 마켓 API 설정을 진행합니다.
        
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
            
            # 2. 모든 마켓 API 연결 끊기
            if not self._disconnect_all_market_apis():
                logger.error("마켓 API 연결 끊기 실패")
                return False
            
            # 3. 각 마켓별 API 키 입력 (키값이 있는 경우에만)
            api_setup_success = False
            
            # 3-1. 11번가 API KEY 입력
            api_key_11st = market_config.get('11store_api', '')
            if api_key_11st:
                if self._input_11st_api_key(api_key_11st):
                    logger.info("11번가 API KEY 입력 성공")
                    api_setup_success = True
                else:
                    logger.error("11번가 API KEY 입력 실패")
            
            # 3-2. 톡스토어 API KEY 입력
            talkstore_api_key = market_config.get('talkstore_api', '')
            talkstore_store_url = market_config.get('talkstore_url', '')
            logger.info(f"톡스토어 API 키 확인: API키={talkstore_api_key[:10] if talkstore_api_key else 'N/A'}..., URL={talkstore_store_url[:30] if talkstore_store_url else 'N/A'}...")
            
            if talkstore_api_key and talkstore_store_url:
                logger.info("톡스토어 API 키 입력 시도 시작")
                if self._input_talkstore_api_keys(talkstore_api_key, talkstore_store_url):
                    logger.info("톡스토어 API 키 입력 성공")
                    api_setup_success = True
                else:
                    logger.error("톡스토어 API 키 입력 실패")
            else:
                logger.info("톡스토어 API 키 또는 URL이 없어서 입력을 건너뜁니다.")
            
            # 11번가-글로벌 API 키 입력
            global_11st_api_key = market_config.get('11global_api', '')
            logger.info(f"11번가-글로벌 API 키 확인: {global_11st_api_key[:10] if global_11st_api_key else 'N/A'}...")
            
            if global_11st_api_key:
                logger.info("11번가-글로벌 API 키 입력 시도 시작")
                if self._input_11st_global_api_key(global_11st_api_key):
                    logger.info("11번가-글로벌 API 키 입력 성공")
                    api_setup_success = True
                else:
                    logger.error("11번가-글로벌 API 키 입력 실패")
            else:
                logger.info("11번가-글로벌 API 키가 없어서 입력을 건너뜁니다.")
            
            # 옥션/G마켓 API 키 입력
            auction_api_key = market_config.get('auction_id', '')
            gmarket_api_key = market_config.get('gmarket_id', '')
            logger.info(f"옥션/G마켓 API 키 확인: 옥션={auction_api_key[:10] if auction_api_key else 'N/A'}..., G마켓={gmarket_api_key[:10] if gmarket_api_key else 'N/A'}...")
            
            if auction_api_key and gmarket_api_key:
                logger.info("옥션/G마켓 API 키 입력 시도 시작")
                if self._input_auction_gmarket_api_keys(auction_api_key, gmarket_api_key):
                    logger.info("옥션/G마켓 API 키 입력 성공")
                    api_setup_success = True
                else:
                    logger.error("옥션/G마켓 API 키 입력 실패")
            else:
                logger.info("옥션/G마켓 API 키가 없어서 입력을 건너뜁니다.")
            
            # API 키가 하나도 설정되지 않은 경우
            if not api_setup_success:
                logger.warning("설정된 API 키가 없습니다.")
                return False
            
            logger.info(f"마켓 설정 화면 정보 처리 완료 - 그룹: {market_config['groupname']}")
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
                    
                    # 마켓 간 DOM 안정화를 위한 대기 시간 증가
                    time.sleep(2)
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
            
            # 1. 11번가-일반 탭으로 전환
            if not self.market_utils.switch_to_market('11st_general'):
                logger.error("11번가-일반 탭 전환 실패")
                return False
            
            # 2. 11번가 패널 로드 대기
            if not self.market_utils.wait_for_market_panel_load('11st_general'):
                logger.error("11번가 패널 로드 실패")
                return False
            
            # 3. API KEY 입력
            if self.market_utils.input_11st_general_api_key(api_key):
                logger.info("11번가 API KEY 입력 성공")
                
                # 4. API 검증 진행
                if self.market_utils.perform_complete_11st_api_verification_workflow():
                    logger.info("11번가 API 검증 성공")
                    return True
                else:
                    logger.error("11번가 API 검증 실패")
                    return False
            else:
                logger.error("11번가 API KEY 입력 실패")
                return False
                
        except Exception as e:
            logger.error(f"11번가 API KEY 입력 중 오류 발생: {e}")
            return False
    
    def _input_talkstore_api_keys(self, api_key, store_url):
        """
        톡스토어 API KEY와 스토어 URL을 입력합니다.
        
        Args:
            api_key (str): 톡스토어 API KEY (G열)
            store_url (str): 톡스토어 주소 (H열)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("톡스토어 API 키 입력 시작")
            
            # 1. 톡스토어 탭으로 전환
            if not self.market_utils.switch_to_market('kakao'):
                logger.error("톡스토어 탭 전환 실패")
                return False
            
            # 2. 톡스토어 패널 로드 대기
            if not self.market_utils.wait_for_market_panel_load('kakao'):
                logger.error("톡스토어 패널 로드 실패")
                return False
            
            # 3. API Key 입력 (첫 번째 입력창)
            try:
                api_key_selector = 'div[id="rc-tabs-0-panel-kakao"] input[placeholder="미설정"]:first-of-type'
                api_key_element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, api_key_selector)))
                
                if not api_key_element.is_displayed() or not api_key_element.is_enabled():
                    logger.error("톡스토어 API Key 입력창이 비활성화됨")
                    return False
                
                api_key_element.clear()
                api_key_element.send_keys(api_key)
                logger.info(f"톡스토어 API Key 입력 완료: {api_key[:10]}...")
                
            except Exception as e:
                logger.error(f"톡스토어 API Key 입력 실패: {e}")
                return False
            
            # 4. 톡스토어 주소 입력 (두 번째 입력창)
            try:
                store_url_selector = 'div[id="rc-tabs-0-panel-kakao"] input[placeholder*="https://store.kakao.com"]'
                store_url_element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, store_url_selector)))
                
                if not store_url_element.is_displayed() or not store_url_element.is_enabled():
                    logger.error("톡스토어 주소 입력창이 비활성화됨")
                    return False
                
                store_url_element.clear()
                store_url_element.send_keys(store_url)
                logger.info(f"톡스토어 주소 입력 완료: {store_url}")
                
            except Exception as e:
                logger.error(f"톡스토어 주소 입력 실패: {e}")
                return False
            
            # 5. API 검증 버튼 클릭
            if self.market_utils.click_api_validation_button():
                logger.info("톡스토어 API 검증 성공")
                time.sleep(2)  # 검증 완료 대기
                return True
            else:
                logger.error("톡스토어 API 검증 실패")
                return False
                
        except Exception as e:
            logger.error(f"톡스토어 API 키 입력 중 오류 발생: {e}")
            return False
    
    def _input_11st_global_api_key(self, api_key):
        """
        11번가-글로벌 API KEY를 입력합니다.
        
        Args:
            api_key (str): API 키
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("11번가-글로벌 API KEY 입력 시작")
            
            # 1. 11번가-글로벌 탭으로 전환
            if not self.market_utils.switch_to_market('11st_global'):
                logger.error("11번가-글로벌 탭 전환 실패")
                return False
            
            # 2. 11번가-글로벌 패널 로드 대기
            if not self.market_utils.wait_for_market_panel_load('11st_global'):
                logger.error("11번가-글로벌 패널 로드 실패")
                return False
            
            # 3. API KEY 입력
            if self.market_utils.input_11st_global_api_key(api_key):
                logger.info("11번가-글로벌 API KEY 입력 성공")
                
                # 4. API 검증 진행
                if self.market_utils.click_api_validation_button():
                    logger.info("11번가-글로벌 API 검증 성공")
                    time.sleep(2)  # 검증 완료 대기
                    return True
                else:
                    logger.error("11번가-글로벌 API 검증 실패")
                    return False
            else:
                logger.error("11번가-글로벌 API KEY 입력 실패")
                return False
                
        except Exception as e:
            logger.error(f"11번가-글로벌 API KEY 입력 중 오류 발생: {e}")
            return False
    
    def _input_auction_gmarket_api_keys(self, auction_api_key, gmarket_api_key):
        """
        옥션/G마켓 API KEY를 입력합니다.
        
        Args:
            auction_api_key (str): 옥션 API 키
            gmarket_api_key (str): G마켓 API 키
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("옥션/G마켓 API KEY 입력 시작")
            
            # API KEY 입력 (탭 전환과 패널 로드는 input_auction_gmarket_api_keys 메서드에서 처리)
            if self.market_utils.input_auction_gmarket_api_keys(auction_api_key, gmarket_api_key):
                logger.info("옥션/G마켓 API KEY 입력 성공")
                
                # 4. API 검증 진행 (옥션/G마켓은 하나의 검증 프로세스로 처리)
                if self.market_utils.click_api_validation_button():
                    logger.info("옥션/G마켓 API 검증 버튼 클릭 성공")
                    
                    # 5. API 검증 모달창 처리
                    if self.market_utils.handle_auction_gmarket_api_verification_modal():
                        logger.info("옥션/G마켓 API 검증 성공")
                        return True
                    else:
                        logger.error("옥션/G마켓 API 검증 모달창 처리 실패")
                        return False
                else:
                    logger.error("옥션/G마켓 API 검증 버튼 클릭 실패")
                    return False
            else:
                logger.error("옥션/G마켓 API KEY 입력 실패")
                return False
                
        except Exception as e:
            logger.error(f"옥션/G마켓 API KEY 입력 중 오류 발생: {e}")
            return False
    
    def _navigate_to_product_registration(self):
        """
        신규상품등록 화면으로 전환합니다.
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("신규상품등록 화면으로 전환 시작")
            
            # 마켓설정 화면에서 DOM 간섭을 방지하기 위해 페이지 새로고침
            logger.info("DOM 간섭 방지를 위한 페이지 새로고침 실행")
            self.driver.refresh()
            time.sleep(3)  # 새로고침 후 대기
            logger.info("페이지 새로고침 완료")
            
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
            
            # 그룹 선택 시도 (최대 3회 재시도)
            group_selection_success = False
            for attempt in range(3):
                try:
                    logger.info(f"{group_name} 그룹 선택 시도 {attempt + 1}/3")
                    
                    # 상품검색용 드롭박스에서 그룹 선택
                    if self.dropdown_utils.select_group_in_search_dropdown(group_name):
                        logger.info(f"{group_name} 그룹 선택 성공")
                        group_selection_success = True
                        break
                    else:
                        logger.warning(f"{group_name} 그룹 선택 실패 (시도 {attempt + 1}/3)")
                    
                    if attempt < 2:
                        time.sleep(2)  # 재시도 전 대기
                        
                except Exception as e:
                    logger.error(f"{group_name} 그룹 선택 중 오류 (시도 {attempt + 1}/3): {e}")
                    time.sleep(2)  # 재시도 전 대기
            
            if not group_selection_success:
                logger.error(f"{group_name} 그룹 선택에 실패했습니다.")
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
                
                # 두 번째 마켓부터 DOM 간섭 방지를 위한 페이지 새로고침
                if idx > 1:
                    logger.info("이전 마켓 설정 DOM 간섭 방지를 위해 페이지 새로고침")
                    self.driver.refresh()
                    time.sleep(5)  # 페이지 로드 대기
                
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