# -*- coding: utf-8 -*-
"""6-1단계 동적 업로드 처리 코어 (cafe24_upload 시트 기반)

percenty_id.xlsx의 cafe24_upload 시트를 파싱하여 동적으로 업로드를 진행합니다.
- 로그인 아이디와 매핑되는 행들을 순차적으로 처리
- 11번가 마켓 설정 및 API 연동
- 등록상품관리에서 동적 그룹 선택 및 업로드 진행
"""

import logging
import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from dropdown_utils2 import get_product_search_dropdown_manager
from upload_utils import UploadUtils
from market_manager import MarketManager
from market_utils import MarketUtils
from market_manager_cafe24 import MarketManagerCafe24
from market_manager_coupang import CoupangMarketManager

logger = logging.getLogger(__name__)

class ProductEditorCore6_Dynamic4:
    """6-1단계 동적 업로드 처리 코어 클래스"""
    
    def __init__(self, driver, account_id, excel_path="percenty_id.xlsx"):
        self.driver = driver
        self.account_id = account_id
        self.excel_path = excel_path
        self.wait = WebDriverWait(driver, 10)
        
        # 유틸리티 클래스 초기화
        self.dropdown_utils = get_product_search_dropdown_manager(driver)
        self.dropdown_manager = get_product_search_dropdown_manager(driver)  # 최적화된 메서드용
        self.upload_utils = UploadUtils(driver)
        self.market_utils = MarketUtils(driver, logger)
        self.market_manager = MarketManager(driver)
        
        # 스마트스토어 API 키 설정 상태 추적
        self.smartstore_api_configured = False
        
        logger.info(f"ProductEditorCore6_Dynamic4 초기화 완료 - 계정: {account_id}")
    
    def load_market_config_from_excel(self):
        """
        percenty_id.xlsx의 cafe24_upload 시트에서 로그인 아이디와 매핑되는 마켓 설정 정보를 로드합니다.
        
        Returns:
            list: 마켓 설정 정보 리스트 (각 행의 데이터)
        """
        try:
            logger.info(f"계정 {self.account_id}의 마켓 설정 정보를 로드합니다.")
            
            # cafe24_upload 시트에서 데이터 로드
            market_df = pd.read_excel(self.excel_path, sheet_name="cafe24_upload")
            
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
                    'smartstore_password': safe_get(row.get('smartstore_password', '')),  # K열                    
                    'coupang_id': safe_get(row.get('coupang_id', '')),  # L열
                    'coupang_code': safe_get(row.get('coupang_code', '')),  # M열
                    'coupang_access': safe_get(row.get('coupang_access', '')),  # N열
                    'coupang_secret': safe_get(row.get('coupang_secret', '')),  # O열
                    'coupang_password': safe_get(row.get('coupang_password', '')),  # P열
                    'cafe24_server': safe_get(row.get('cafe24_server', '')),  # Q열
                    'cafe24_id': safe_get(row.get('cafe24_id', '')),  # R열
                    'cafe24_password': safe_get(row.get('cafe24_password', '')),  # S열
                    '11store_id': safe_get(row.get('11store_id', '')),  # T열
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
                if config['smartstore_password']:
                    api_info.append(f"스마트스토어PW={config['smartstore_password'][:5]}...")
                if config['coupang_id']:
                    api_info.append(f"쿠팡ID={config['coupang_id']}")
                if config['coupang_code']:
                    api_info.append(f"쿠팡CODE={config['coupang_code']}")
                if config['coupang_access']:
                    api_info.append(f"쿠팡ACCESS={config['coupang_access'][:10]}...")
                if config['coupang_secret']:
                    api_info.append(f"쿠팡SECRET={config['coupang_secret'][:10]}...")
                if config['coupang_password']:
                    api_info.append(f"쿠팡PW={config['coupang_password'][:5]}...")
                if config['cafe24_server']:
                    api_info.append(f"카페24서버={config['cafe24_server']}")
                if config['cafe24_id']:
                    api_info.append(f"카페24ID={config['cafe24_id']}")
                if config['cafe24_password']:
                    api_info.append(f"카페24PW={config['cafe24_password'][:5]}...")
                if config['11store_id']:
                    api_info.append(f"11번가ID={config['11store_id']}")
                
                api_info_str = ", ".join(api_info) if api_info else "API 키 없음"
                logger.info(f"마켓 설정 {idx+1}: 그룹명={config['groupname']}, {api_info_str}")
            
            return market_configs
            
        except Exception as e:
            logger.error(f"마켓 설정 정보 로드 중 오류 발생: {e}")
            return []
    
    def _set_items_per_page_50(self):
        """
        50개씩 보기 설정을 수행합니다.
        
        Returns:
            bool: 설정 성공 여부
        """
        DELAY_MEDIUM = 2
        
        items_per_page_success = False
        for attempt in range(3):
            try:
                logger.info(f"50개씩 보기 설정 시도 {attempt + 1}/3")
                
                # 50개씩 보기 설정
                if self.dropdown_manager.select_items_per_page("50"):
                    logger.info("50개씩 보기 설정 성공")
                    items_per_page_success = True
                    break
                else:
                    logger.warning(f"50개씩 보기 설정 실패 (시도 {attempt + 1}/3)")
                
                if attempt < 2:
                    time.sleep(DELAY_MEDIUM)
                    
            except Exception as e:
                logger.error(f"50개씩 보기 설정 중 오류 (시도 {attempt + 1}/3): {e}")
                time.sleep(DELAY_MEDIUM)
        
        if not items_per_page_success:
            logger.warning("50개씩 보기 설정에 실패했지만 작업을 계속 진행합니다.")
        
        return items_per_page_success
    
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
            
            # 현재 마켓 설정 정보 저장 (다른 메서드에서 사용하기 위해)
            self.current_market_config = market_config
            
            """
            # 0. 쿠팡 API 연동업체를 '퍼센티'로 변경
            coupang_id = market_config.get('coupang_id', '')
            coupang_password = market_config.get('coupang_password', '')
            
            if coupang_id and coupang_password:
                logger.info("쿠팡 API 연동업체를 '퍼센티'로 변경 시작")
                try:
                    coupang_manager = CoupangMarketManager(self.driver, self.wait)
                    if coupang_manager.change_api_integrator_to_percenty(market_config):
                        logger.info("쿠팡 API 연동업체를 '퍼센티'로 변경 완료")
                    else:
                        logger.warning("쿠팡 API 연동업체 '퍼센티' 변경에 실패했지만 계속 진행합니다")
                except Exception as e:
                    logger.error(f"쿠팡 API 연동업체 변경 중 오류 발생: {str(e)}")
            else:
                logger.info("쿠팡 로그인 정보가 없어 연동업체 변경을 건너뜁니다")
            """

            # 1. 마켓설정 화면 열기
            if not self._open_market_settings():
                logger.error("마켓설정 화면 열기 실패")
                self._ensure_main_tab_focus()
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
            
            """
            11번가 이외의 모든 마켓에 대한 메서드 삭제하고 실행 코드도 모두 삭제함

            """
            
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
            self._ensure_main_tab_focus()
            return False
            
        except Exception as e:
            logger.error(f"마켓설정 화면 열기 중 오류 발생: {e}")
            self._ensure_main_tab_focus()
            return False

    
    def _detect_and_close_modal(self):
        """
        퍼센티 상담 모달창을 감지하고 닫습니다.
        
        Returns:
            bool: 모달창을 감지하고 닫았는지 여부
        """
        try:
            # 채널톡 팝업 모달창 감지 및 닫기 시도
            if self._detect_and_close_channel_talk_popup():
                return True
                
            # 기존 모달창 감지 (퍼센티 상담 팝업)
            modal_selectors = [
                "div[class*='PCFullscreenPopupContent']",
                "div[role='button'][class*='PCFullscreenPopupContent']",
                "button[class*='PopupCloseBtn__CloseButton']"
            ]
            
            for selector in modal_selectors:
                try:
                    modal_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if modal_element and modal_element.is_displayed():
                        logger.info("퍼센티 상담 모달창 감지됨")
                        
                        # 닫기 버튼 찾기 및 클릭
                        close_button = self.driver.find_element(By.CSS_SELECTOR, "button[class*='PopupCloseBtn__CloseButton']")
                        if close_button and close_button.is_displayed():
                            close_button.click()
                            logger.info("모달창 닫기 버튼 클릭 완료")
                            time.sleep(1)  # 모달창 닫힘 대기
                            return True
                        break
                except Exception as e:
                    # 해당 셀렉터로 요소를 찾지 못한 경우 다음 셀렉터 시도
                    continue
            
            return False
            
        except Exception as e:
            logger.debug(f"모달창 감지 중 오류 (무시하고 계속): {e}")
            return False
    
    def _detect_and_close_channel_talk_popup(self):
        """
        채널톡 팝업 모달창을 감지하고 닫습니다.
        퍼센티 확장프로그램 설치 후 나타나는 채널톡 팝업을 처리합니다.
        
        Returns:
            bool: 채널톡 팝업을 감지하고 닫았는지 여부
        """
        try:
            # 채널톡 팝업 모달창 감지 선택자들
            popup_selectors = [
                "div[class*='PCFullscreenPopupContentstyled__BaseWrapper-ch-front']",
                "div[class*='ch-front'][class*='PCFullscreenPopup']",
                "div.PCFullscreenPopupContentstyled__BaseWrapper-ch-front__sc-1he3s01-0"
            ]
            
            # 닫기 버튼 선택자들
            close_button_selectors = [
                "button[class*='PopupCloseBtn__CloseButton-ch-front']",
                "button.PopupCloseBtn__CloseButton-ch-front__sc-14jjsiy-1",
                "div[class*='PopupCloseBtn__CloseButtonArea'] button",
                "button[class*='CloseButton'][class*='ch-front']"
            ]
            
            # 팝업 모달창 감지
            popup_found = False
            for selector in popup_selectors:
                try:
                    popup_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if popup_element and popup_element.is_displayed():
                        logger.info("채널톡 팝업 모달창 감지됨")
                        popup_found = True
                        break
                except:
                    continue
            
            if not popup_found:
                return False
            
            # 닫기 버튼 찾기 및 클릭
            for close_selector in close_button_selectors:
                try:
                    close_button = self.driver.find_element(By.CSS_SELECTOR, close_selector)
                    if close_button and close_button.is_displayed():
                        close_button.click()
                        logger.info("채널톡 팝업 닫기 버튼 클릭 완료")
                        time.sleep(1.5)  # 팝업 닫힘 대기
                        return True
                except:
                    continue
            
            # 닫기 버튼을 찾지 못한 경우 ESC 키 시도
            try:
                from selenium.webdriver.common.keys import Keys
                self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                logger.info("채널톡 팝업 ESC 키로 닫기 시도")
                time.sleep(1)
                return True
            except:
                pass
            
            logger.warning("채널톡 팝업 닫기 실패")
            return False
            
        except Exception as e:
            logger.debug(f"채널톡 팝업 감지 중 오류 (무시하고 계속): {e}")
            return False
    
    def _disconnect_all_market_apis(self):
        """
        모든 마켓의 API 연결을 끊습니다.
        
        Returns:
            bool: 성공 여부
        """
        try:
            # API 연결 끊기 전 모달창 감지 및 닫기
            self._detect_and_close_modal()
            
            # 모든 마켓들의 API 연결 끊기
            markets_to_disconnect = [
                'smartstore', 'coupang', 'auction_gmarket', 
                '11st_general', '11st_global', 'lotteon', 'kakao'
            ]
            
            for market in markets_to_disconnect:
                try:
                    logger.info(f"{market} API 연결 끊기 시도")
                    
                    # 각 마켓 API 연결 끊기 전 채널톡 팝업 및 모달창 확인
                    self._detect_and_close_modal()
                    
                    # 각 마켓별 개별 메서드 직접 호출 (처리 순서와 일치)
                    if market == 'smartstore':
                        success = self.market_utils.disconnect_smartstore_api()
                    elif market == '11st_general':
                        success = self.market_utils.disconnect_coupang_api()
                    elif market == 'coupang':
                        success = self.market_utils.disconnect_11st_general_api()
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
    

    
    def _navigate_to_product_management(self):
        """
        등록상품관리 화면으로 전환합니다.
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("등록상품관리 화면으로 전환 시작")
            
            # 마켓설정 화면에서 DOM 간섭을 방지하기 위해 페이지 새로고침
            logger.info("DOM 간섭 방지를 위한 페이지 새로고침 실행")
            self.driver.refresh()
            time.sleep(3)  # 새로고침 후 대기
            logger.info("페이지 새로고침 완료")
            
            # DOM 선택자 - span.ant-menu-title-content 중에서 '등록 상품 관리' 텍스트를 가진 요소
            selectors = [
                "//span[@class='ant-menu-title-content' and text()='등록 상품 관리']",
                "//span[contains(@class, 'ant-menu-title-content')][contains(., '등록 상품')]",
                "//li[contains(@data-menu-id, 'PRODUCT_MANAGE')]//span[contains(@class, 'ant-menu-title-content')]"
            ]
            
            for selector in selectors:
                try:
                    element = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    element.click()
                    logger.info("등록상품관리 메뉴 클릭 완료")
                    
                    # 등록상품관리 화면 로드 대기
                    time.sleep(5)
                    
                    # 스크롤을 최상단으로 초기화
                    self.driver.execute_script("window.scrollTo(0, 0);")
                    logger.info("스크롤 위치를 최상단으로 초기화")
                    
                    logger.info("등록상품관리 화면으로 전환 완료")
                    return True
                except TimeoutException:
                    continue
            
            logger.error("등록상품관리 화면 전환 실패 - 요소를 찾을 수 없음")
            return False
            
        except Exception as e:
            logger.error(f"등록상품관리 화면 전환 중 오류 발생: {e}")
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
    
    def _execute_product_upload_workflow(self, group_name, market_config):
        """
        product_editor_core6_1의 상품 업로드 워크플로우를 실행합니다.
        11번가 미업로드 상품을 처리합니다.

           
        #1 상태검색> 판매중 메뉴 선택
        #2 11번가 선택후 상품검색 클릭
        #3 전체선택
        #4 삭제 메서드 실행, 상품수가 0개가 될떄가지 반복

        #5 상태검색> 미업로드 메뉴 선택
        #6 11번가 선택후 상품검색 클릭
        #7 전체선택
        #8 업로드 실행, 상품수가 0개가 될떄가지 반복

        엑셀에서 파싱한 쇼핑몰A1의 키워드를 순환해서 작업후, 더 이상 쇼핑몰A1 키워드 처리할 경우가 없으면
        #9 상태검색> 판매중 메뉴 선택
        #10 전체선택
        #11 그룹지정 모달창을 열고 완료A1그룹으로 이동

        이어서 쇼핑몰A2와 쇼핑몰A3도 같은 플로우로 진행.
         

        Args:
            group_name (str): 업로드할 그룹명
            market_config (dict): 마켓 설정 정보
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"상품 업로드 워크플로우 시작: {group_name}")

            
            # 1. 상태검색>판매중인 상품 모두 삭제 메서드 진행
            """
            #1 상태검색> 판매중 메뉴 선택
            #2 11번가 선택후 상품검색 클릭
            """


            # 2-1 ~ 2-5 단계를 2회 반복
            # 삭제 메서드 실행, 상품수가 0개가 될때까지 반복     
            for round_num in range(1, 11):  # 최대 10회차까지 반복
                logger.info(f"삭제 {round_num}회차 시작")
                
                # 2-1. 상품 수 확인 (0개인 경우 해당 회차 스킵)
                product_count = self._check_product_count()
                if product_count == 0:
                    logger.info(f"{round_num}회차: 상품이 0개이므로 삭제 완료")
                    # 1회차에서 상품이 0개면 전체 워크플로우 종료
                    if round_num == 1:
                        logger.info(f"상품이 0개이므로 삭제 워크플로우를 스킵합니다")
                        return True
                    # 2회차 이후에서 상품이 0개면 삭제 완료
                    else:
                        logger.info(f"{round_num}회차 삭제 완료, 모든 상품이 삭제되었습니다")
                        break
                elif product_count == -1:
                    logger.warning(f"{round_num}회차 상품 수 확인 실패, 계속 진행합니다")
                else:
                    logger.info(f"{round_num}회차 확인된 상품 수: {product_count}개")
                
                # 2-2. 50개씩 보기 설정 
                if not self._set_items_per_page_50(): 
                   logger.error("50개씩 보기 설정 실패") 
                   return False
                
                # 2-3. 전체선택
                if not self._select_all_products():
                    logger.error(f"{round_num}회차 전체선택 실패")
                    return False
                
                # 2-4. 삭제 버튼 클릭해서 삭제 모달창 열고 선택 상품 삭제 진행
                if not self._handle_bulk_delete(round_num):
                    logger.error(f"{round_num}회차 일괄 삭제 처리 실패")
                    return False
                
                # 2-5. 삭제 완료 대기 및 모달창 닫기
                if not self._wait_for_delete_completion():
                    logger.error(f"{round_num}회차 삭제 완료 대기 실패")
                    return False

                # 모달창 닫기 후 안정성을 위한 대기 (단축)
                time.sleep(3)
                
                # 마지막 회차가 아닌 경우에만 상품 검색 버튼 클릭
                if round_num < 11:
                    logger.info(f"{round_num}회차 완료, 상품 검색 버튼 클릭 후 다음 회차 진행")
                    if not self._click_product_search_button():
                        logger.warning("상품 검색 버튼 클릭 실패, 다음 회차 계속 진행")
                        continue
                else:
                    logger.info(f"최대 회차({round_num})에 도달했습니다")

            # 2. 상태검색>미업로드 메뉴 선택
            """
            #5 상태검색> 미업로드 메뉴 선택
            #6 11번가 선택후 상품검색 클릭
            """

            if not self._search_unuploaded_products():
                logger.error("미업로드 상품 검색 실패")
                return False

            # 3-1 ~ 3-5 단계를 2회 반복
            for round_num in range(1, 11):  # 1회차, 2회차
                logger.info(f"업로드 {round_num}회차 시작")
                
                # 3-1. 상품 수 확인 (0개인 경우 해당 회차 스킵)
                product_count = self._check_product_count()
                if product_count == 0:
                    logger.info(f"{round_num}회차: 상품이 0개이므로 이번 회차 업로드를 스킵합니다")
                    # 1회차에서 상품이 0개면 전체 워크플로우 종료
                    if round_num == 1:
                        logger.info(f"그룹 '{group_name}'에 상품이 0개이므로 워크플로우를 스킵합니다")
                        return True
                    # 2회차에서 상품이 0개면 해당 회차만 스킵하고 다음 플로우로 진행
                    else:
                        logger.info(f"{round_num}회차 업로드 스킵 완료, 다음 플로우로 진행합니다")
                        break
                elif product_count == -1:
                    logger.warning(f"{round_num}회차 상품 수 확인 실패, 계속 진행합니다")
                else:
                    logger.info(f"{round_num}회차 확인된 상품 수: {product_count}개")
                
                # 3-2. 50개씩 보기 설정 
                if not self._set_items_per_page_50(): 
                   logger.error("50개씩 보기 설정 실패") 
                   return False
                
                # 3-3. 전체선택
                if not self._select_all_products():
                    logger.error(f"{round_num}회차 전체선택 실패")
                    return False
                
                # 3-4. 업로드 버튼 클릭해서 업로드 모달창 열고 선택 상품 일괄 업로드 클릭
                if not self._handle_bulk_upload():
                    logger.error(f"{round_num}회차 일괄 업로드 처리 실패")
                    return False
                
                # 3-5. 업로드 완료 대기 및 모달창 닫기
                if not self._wait_for_upload_completion():
                    logger.warning(f"{round_num}회차 업로드 완료 대기 또는 모달창 닫기에 실패했지만 계속 진행합니다")
                
                # 모달창 닫기 후 안정성을 위한 대기
                time.sleep(5)
                
                # 2회차가 아닌 경우에만 상품 검색 버튼 클릭
                if round_num < 11:
                    logger.info(f"{round_num}회차 완료, 상품 검색 버튼 클릭 후 다음 회차 진행")
                    if not self._click_product_search_button():
                        logger.warning("상품 검색 버튼 클릭 실패, 다음 회차 계속 진행")
            

            # 4. 카페24 로그인해서 11번가 등록자료 가져오기
            if not self._import_11st_products_from_cafe24():
                logger.warning("카페24 11번가 상품 가져오기에 실패했지만 계속 진행합니다")
            
            # 5. 상태검색> 판매중인 상품 그룹이동
            """
            앞에서 동적으로 선택한 groupname이  쇼핑몰A1인 경우, 여러개의 쇼핑몰A1중에서 마지막 쇼핑몰A1인 경우에 플로우 진행
            앞에서 동적으로 선택한 groupname이  쇼핑몰A2인 경우, 여러개의 쇼핑몰A1중에서 마지막 쇼핑몰A2인 경우에 플로우 진행
            앞에서 동적으로 선택한 groupname이  쇼핑몰A3인 경우, 여러개의 쇼핑몰A1중에서 마지막 쇼핑몰A3인 경우에 플로우 진행

            #9 상태검색> 판매중 메뉴 선택
            #10 전체선택
            #11 그룹지정 모달창을 열고 groupname이 쇼핑몰A1이면 완료A1그룹으로 이동, groupname이 쇼핑몰A2이면 완료A2그룹으로 이동, groupname이 쇼핑몰A3이면 완료A3그룹으로 이동, 
            """

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
            
            # dropdown_utils2의 get_total_product_count 메서드 사용
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
            
            # dropdown_utils의 select_all_products 메서드 사용 (안정적인 방식)
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
    
    def _handle_bulk_delete(self, round_num=1):
        """
        삭제 버튼 클릭해서 삭제 모달창 열고 선택 상품 일괄 삭제 처리
        
        Args:
            round_num (int): 현재 회차 번호 (1회차는 드롭박스/11번가 선택, 2회차 이후는 바로 삭제)
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("삭제 버튼 클릭해서 삭제 모달창 열고 선택 상품 일괄 삭제 처리")
            
            # 1. 삭제 버튼 클릭
            if not self._click_delete_button():
                logger.error("삭제 버튼 클릭 실패")
                return False
            
            logger.info("삭제 버튼 클릭 성공")
            
            # 2. 삭제 모달창 처리 (회차별 로직 분리)
            if not self._handle_delete_modal(round_num):
                logger.error("삭제 모달창 처리 실패")
                return False
            
            logger.info("일괄 삭제 처리 완료")
            return True
            
        except Exception as e:
            logger.error(f"일괄 삭제 처리 중 오류: {e}")
            return False
    
    def _wait_for_delete_completion(self):
        """
        삭제 완료를 대기하고 모달창을 닫습니다.
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("삭제 완료 대기 및 모달창 닫기")
            
            # 3초 간격으로 삭제 상태 확인
            max_wait_time = 300  # 최대 5분 대기
            check_interval = 3   # 3초 간격
            elapsed_time = 0
            
            while elapsed_time < max_wait_time:
                try:
                    # 삭제 완료 상태 확인 (예: "2/2 삭제 완료")
                    completion_selectors = [
                        "//span[contains(@class, 'Font_Gray900Bold14') and contains(text(), '삭제 완료')]",
                        "//span[contains(text(), '삭제 완료')]",
                        "//div[contains(text(), '모든 상품 삭제가 완료됐습니다')]"
                    ]
                    
                    for selector in completion_selectors:
                        try:
                            element = self.driver.find_element(By.XPATH, selector)
                            if element.is_displayed():
                                logger.info(f"삭제 완료 확인: {element.text}")
                                # 삭제 완료 즉시 모달창 닫기 (불필요한 대기 제거)
                                
                                # 모달창 닫기 (X 버튼 클릭)
                                if self._close_delete_modal():
                                    logger.info("삭제 완료 대기 및 모달창 닫기 완료")
                                    return True
                                else:
                                    logger.warning("모달창 닫기 실패했지만 삭제는 완료됨")
                                    return True
                        except:
                            continue
                    
                    # 진행 상태 로그 출력
                    try:
                        progress_element = self.driver.find_element(By.XPATH, "//span[contains(@class, 'Font_Gray900Bold14')]")
                        if progress_element.is_displayed():
                            logger.info(f"삭제 진행 상태: {progress_element.text}")
                    except:
                        pass
                    
                    time.sleep(check_interval)
                    elapsed_time += check_interval
                    
                except Exception as e:
                    logger.warning(f"삭제 상태 확인 중 오류: {e}")
                    time.sleep(check_interval)
                    elapsed_time += check_interval
            
            logger.warning(f"삭제 완료 대기 시간 초과 ({max_wait_time}초), 강제로 모달창 닫기 시도")
            self._close_delete_modal()
            return False
            
        except Exception as e:
            logger.error(f"삭제 완료 대기 중 오류: {e}")
            return False
     
    def _click_delete_button(self):
        """
        삭제 버튼을 클릭합니다.
         
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("삭제 버튼 클릭 시도")
             
            # 삭제 버튼 선택자들
            delete_button_selectors = [
                "//button[contains(@class, 'Button_Button') and contains(., '삭제')]",
                "//button[contains(text(), '삭제')]",
                "//span[text()='삭제']/parent::button",
                "//button[@class='Button_Button__1QZ7B Button_Outline__3QDMB Button_Medium__1C9xh Button_Gray__2kWKs']"
            ]
             
            for selector in delete_button_selectors:
                try:
                    delete_button = self.driver.find_element(By.XPATH, selector)
                    if delete_button.is_displayed() and delete_button.is_enabled():
                        self.driver.execute_script("arguments[0].click();", delete_button)
                        logger.info(f"삭제 버튼 클릭 성공: {selector}")
                        time.sleep(2)  # 모달창 로딩 대기
                        return True
                except Exception as e:
                    logger.debug(f"삭제 버튼 선택자 실패: {selector}, 오류: {e}")
                    continue
             
            logger.error("모든 삭제 버튼 선택자 실패")
            return False
             
        except Exception as e:
            logger.error(f"삭제 버튼 클릭 중 오류: {e}")
            return False
     
    def _handle_delete_modal(self, round_num=1):
        """
        삭제 모달창에서 세번째 메뉴 선택 및 11번가-일반 선택 후 일괄 삭제 버튼 클릭
        
        Args:
            round_num (int): 현재 회차 번호 (1회차는 드롭박스와 11번가 선택, 2회차 이후는 건너뛰기)
         
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"삭제 모달창 처리 시작 (회차: {round_num})")
             
            # 모달창 로딩 대기
            time.sleep(1)
            
            # 2회차 이후에는 드롭박스와 11번가 선택을 건너뛰고 바로 삭제 버튼 클릭
            if round_num > 1:
                logger.info(f"{round_num}회차: 드롭박스와 11번가 선택 건너뛰고 바로 삭제 버튼 클릭")
            else:
                logger.info("1회차: 드롭박스와 11번가 선택 진행")
                
                # 1. 드롭박스 클릭 (세번째 메뉴 선택)
                # 실제 DOM 구조에 맞춘 선택자 업데이트
                dropdown_selectors = [
                    "//div[@class='ant-select ant-select-outlined css-1li46mu ant-select-single ant-select-show-arrow']//div[@class='ant-select-selector']",
                    "//span[@class='ant-select-selection-item' and @title='1. 퍼센티 및 모든 마켓에서 상품 삭제']/parent::div",
                    "//div[contains(@class, 'ant-select') and contains(@class, 'ant-select-single')]//div[@class='ant-select-selector']",
                    "//div[@class='ant-select-selector']",
                    "//div[contains(@class, 'ant-select-selector')]"
                ]
                 
                dropdown_clicked = False
                for selector in dropdown_selectors:
                    try:
                        dropdown_element = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                        dropdown_element.click()
                        logger.info(f"드롭박스 클릭 성공: {selector}")
                        dropdown_clicked = True
                        break
                    except TimeoutException:
                        logger.debug(f"드롭박스 선택자 시도: {selector}")
                        continue
                    except Exception as e:
                        logger.debug(f"드롭박스 선택자 실패: {selector}, 오류: {e}")
                        continue
                 
                if not dropdown_clicked:
                    logger.error("모든 선택자로 드롭박스를 찾을 수 없음")
                    return False
                 
                # 2. 세번째 메뉴 선택 (3. 퍼센티에서 해당 마켓 업로드 정보만 삭제하기)
                # 상태 검색 메서드와 동일한 패턴으로 개선
                time.sleep(1)  # 드롭다운 옵션이 로드될 시간 확보
                
                third_option_selectors = [
                    "//div[contains(@class, 'ant-select-item') and .//div[contains(@class, 'ant-select-item-option-content') and contains(text(), '3. 퍼센티에서 해당 마켓 업로드 정보만 삭제하기')]]",
                    "//div[contains(@class, 'ant-select-item') and contains(text(), '3. 퍼센티에서 해당 마켓 업로드 정보만 삭제하기')]",
                    "//div[@class='ant-select-item-option-content' and contains(text(), '3. 퍼센티에서 해당 마켓 업로드 정보만 삭제하기')]",
                    "//div[@role='option' and .//div[contains(text(), '3. 퍼센티에서 해당 마켓 업로드 정보만 삭제하기')]]",
                    "//div[contains(@class, 'ant-select-item-option') and contains(., '퍼센티에서 해당 마켓 업로드 정보만 삭제')]",
                    "//div[text()='3. 퍼센티에서 해당 마켓 업로드 정보만 삭제하기']"
                ]
                 
                option_selected = False
                for selector in third_option_selectors:
                    try:
                        option_element = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                        option_element.click()
                        logger.info(f"3. 퍼센티에서 해당 마켓 업로드 정보만 삭제하기 옵션 선택 성공: {selector}")
                        option_selected = True
                        break
                    except TimeoutException:
                        logger.debug(f"3. 퍼센티에서 해당 마켓 업로드 정보만 삭제하기 옵션 선택자 시도: {selector}")
                        continue
                    except Exception as e:
                        logger.debug(f"3. 퍼센티에서 해당 마켓 업로드 정보만 삭제하기 옵션 선택자 실패: {selector}, 오류: {e}")
                        continue
                 
                if not option_selected:
                    logger.error("모든 선택자로 '3. 퍼센티에서 해당 마켓 업로드 정보만 삭제하기' 옵션을 찾을 수 없음")
                    return False
                 
                # 3. 모달창이 업데이트될 때까지 충분히 대기
                time.sleep(1)
                
                # 체크박스 그룹이 로드될 때까지 대기 (타임아웃 단축)
                try:
                    WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.XPATH, "//div[@class='ant-checkbox-group']")))
                    logger.info("체크박스 그룹 로드 완료")
                except TimeoutException:
                    logger.warning("체크박스 그룹 로드 대기 시간 초과 (1초)")
                    # 체크박스 그룹이 없어도 계속 진행
                 
                # 4. 11번가 - 일반 메뉴 선택 (텍스트 클릭 방식)
                eleventh_street_selectors = [
                    "//span[text()='11번가 - 일반']",
                    "//label[contains(@class, 'ant-checkbox-group-item')]//span[text()='11번가 - 일반']",
                    "//div[@class='ant-checkbox-group']//label[contains(., '11번가 - 일반')]",
                    "//label[contains(@class, 'ant-checkbox-wrapper') and contains(@class, 'ant-checkbox-group-item') and contains(., '11번가 - 일반')]",
                    "//*[contains(text(), '11번가 - 일반')]"
                ]
                 
                eleventh_street_selected = False
                for selector in eleventh_street_selectors:
                    try:
                        # 타임아웃을 2초로 단축
                        text_element = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, selector)))
                        
                        # 해당 텍스트나 라벨이 이미 선택되어 있는지 확인
                        is_checked = False
                        try:
                            # 방법 1: 라벨 내의 체크박스 input 요소 확인
                            checkbox_input = text_element.find_element(By.XPATH, ".//input[@type='checkbox']")
                            is_checked = checkbox_input.is_selected()
                        except:
                            try:
                                # 방법 2: 부모/형제 요소에서 체크박스 찾기
                                checkbox_input = text_element.find_element(By.XPATH, "./preceding-sibling::span//input[@type='checkbox'] | ./following-sibling::span//input[@type='checkbox'] | ./parent::label//input[@type='checkbox']")
                                is_checked = checkbox_input.is_selected()
                            except:
                                try:
                                    # 방법 3: 부모 요소의 클래스로 확인
                                    parent_element = text_element.find_element(By.XPATH, "./ancestor::label[contains(@class, 'ant-checkbox')]")
                                    is_checked = 'ant-checkbox-checked' in parent_element.get_attribute('class')
                                except:
                                    # 방법 4: 기본적으로 선택되지 않은 것으로 간주
                                    is_checked = False
                         
                        if not is_checked:
                            text_element.click()
                            logger.info(f"11번가 - 일반 텍스트 클릭 성공: {selector}")
                        else:
                            logger.info("11번가 - 일반 체크박스가 이미 선택되어 있음")
                        eleventh_street_selected = True
                        break
                    except TimeoutException:
                        logger.debug(f"11번가 - 일반 텍스트 선택자 시도: {selector}")
                        continue
                    except Exception as e:
                        logger.debug(f"11번가 - 일반 텍스트 선택자 실패: {selector}, 오류: {e}")
                        continue
                  
                if not eleventh_street_selected:
                    # 디버깅: 현재 페이지에 있는 모든 체크박스 확인
                    try:
                        all_checkboxes = self.driver.find_elements(By.XPATH, "//input[@type='checkbox']")
                        logger.error(f"현재 페이지의 체크박스 개수: {len(all_checkboxes)}")
                         
                        # value 속성이 있는 체크박스들 확인
                        value_checkboxes = self.driver.find_elements(By.XPATH, "//input[@type='checkbox' and @value]")
                        for cb in value_checkboxes:
                            value = cb.get_attribute('value')
                            logger.error(f"체크박스 value: {value}")
                         
                        # 11번가 관련 텍스트가 있는 요소들 확인
                        eleventh_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '11번가')]")
                        for elem in eleventh_elements:
                            logger.error(f"11번가 관련 요소: {elem.text}")
                             
                    except Exception as debug_e:
                        logger.error(f"디버깅 중 오류: {debug_e}")
                     
                    logger.error("모든 선택자로 '11번가 - 일반' 텍스트를 찾을 수 없음")
                    return False
             
            # 5. '선택 상품 일괄 삭제' 버튼 클릭 (타임아웃 단축)
            bulk_delete_selectors = [
                "//button[contains(@class, 'Button_Button') and contains(., '선택 상품 일괄 삭제')]",
                "//button[contains(text(), '선택 상품 일괄 삭제')]",
                "//span[text()='선택 상품 일괄 삭제']/parent::button"
            ]
             
            button_clicked = False
            for selector in bulk_delete_selectors:
                try:
                    # 타임아웃을 2초로 단축
                    button_element = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, selector)))
                    button_element.click()
                    logger.info(f"선택 상품 일괄 삭제 버튼 클릭 성공: {selector}")
                    button_clicked = True
                    break
                except TimeoutException:
                    logger.debug(f"일괄 삭제 버튼 선택자 시도: {selector}")
                    continue
                except Exception as e:
                    logger.debug(f"일괄 삭제 버튼 선택자 실패: {selector}, 오류: {e}")
                    continue
             
            if not button_clicked:
                logger.error("모든 선택자로 '선택 상품 일괄 삭제' 버튼을 찾을 수 없음")
                return False
                
            time.sleep(3)
            return True
             
        except Exception as e:
            logger.error(f"삭제 모달창 처리 중 오류: {e}")
            return False
     
    def _close_delete_modal(self):
        """
        삭제 모달창을 닫습니다.
         
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("삭제 모달창 닫기 시도")
             
            # X 버튼 선택자들
            close_button_selectors = [
                "//button[@type='button' and @aria-label='Close' and @class='ant-modal-close']",
                "//button[contains(@class, 'ant-modal-close')]",
                "//span[contains(@class, 'ant-modal-close-x')]/parent::button",
                "//button[@aria-label='Close']"
            ]
             
            for selector in close_button_selectors:
                try:
                    close_button = self.driver.find_element(By.XPATH, selector)
                    if close_button.is_displayed():
                        self.driver.execute_script("arguments[0].click();", close_button)
                        logger.info(f"모달창 닫기 성공: {selector}")
                        time.sleep(0.5)  # 모달창 닫기 대기 시간 단축
                        return True
                except Exception as e:
                    logger.debug(f"모달창 닫기 선택자 실패: {selector}, 오류: {e}")
                    continue
             
            logger.warning("모달창 닫기 실패")
            return False
             
        except Exception as e:
            logger.error(f"모달창 닫기 중 오류: {e}")
            return False
     
    def execute_dynamic_delete_workflow(self):
        """
        동적 삭제 워크플로우를 실행합니다.
         
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("동적 삭제 워크플로우 시작")
             
            # 1. 모든 상품 선택
            if not self.upload_utils.select_all_products():
                logger.error("모든 상품 선택 실패")
                return False
             
            # 2. 삭제 버튼 클릭 및 모달창 처리
            if not self._handle_bulk_delete():
                logger.error("일괄 삭제 처리 실패")
                return False
             
            # 3. 삭제 완료 대기 및 모달창 닫기
            if not self._wait_for_delete_completion():
                logger.error("삭제 완료 대기 실패")
                return False
            
            # 모달창 닫기 후 3초 대기
            # time.sleep(3)
            # logger.info("모달창 닫기 후 3초 대기 완료")
             
            logger.info("동적 삭제 워크플로우 완료")
            return True
             
        except Exception as e:
            logger.error(f"동적 삭제 워크플로우 중 오류: {e}")
            return False
     
    def execute_dynamic_upload_workflow(self):
        """
        동적 업로드 워크플로우를 실행합니다.
        percenty_id.xlsx의 cafe24_upload 시트를 기반으로 순차적으로 처리합니다.
        
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
            
            # 2. 그룹별로 마켓 설정들을 그룹화
            grouped_configs = self._group_configs_by_groupname(market_configs)
            
            # 3. 각 그룹에 대해 순차적으로 처리
            for group_name, group_configs in grouped_configs.items():
                logger.info(f"=== 그룹 '{group_name}' 처리 시작 ({len(group_configs)}개 설정) ===")
                
                # 3-1. 그룹 내 각 마켓 설정 처리
                for idx, market_config in enumerate(group_configs, 1):
                    logger.info(f"--- 그룹 '{group_name}' 내 설정 {idx}/{len(group_configs)} 처리 시작 ---")
                    logger.info(f"API키: {market_config['11store_api'][:10]}...")
                    
                    # 각 마켓 설정 처리 시작 시 스마트스토어 API 설정 상태 초기화
                    self.smartstore_api_configured = False
                    
                    # 두 번째 설정부터 DOM 간섭 방지를 위한 페이지 새로고침
                    if idx > 1:
                        logger.info("이전 마켓 설정 DOM 간섭 방지를 위해 페이지 새로고침")
                        self.driver.refresh()
                        time.sleep(5)  # 페이지 로드 대기
                    
                    # 마켓 설정 화면 정보 처리
                    if not self.setup_market_configuration(market_config):
                        logger.error(f"마켓 설정 {idx} 처리 실패")
                        self._ensure_main_tab_focus()
                        continue
                    
                    # 등록상품관리 화면으로 전환
                    if not self._navigate_to_product_management():
                        logger.error(f"등록상품관리 화면 전환 실패")
                        self._ensure_main_tab_focus()
                        continue
                    
                    # 상품검색 드롭박스를 열고 동적 그룹 선택
                    if not self._select_dynamic_group(market_config['groupname']):
                        logger.error(f"동적 그룹 선택 실패: {market_config['groupname']}")
                        continue
                    
                    # 판매중 상품 검색 워크플로우
                    if not self._search_selling_products():
                        logger.error("판매중 상품 검색 실패")
                        continue
                    
                    # 상품 업로드 워크플로우 실행 (product_editor_core6_1 기능 통합)
                    if not self._execute_product_upload_workflow(market_config['groupname'], market_config):
                        logger.error(f"상품 업로드 워크플로우 실패: {market_config['groupname']}")
                        continue
                    
                    logger.info(f"--- 그룹 '{group_name}' 내 설정 {idx}/{len(group_configs)} 처리 완료 ---")
                    
                    # 다음 설정 처리를 위한 대기
                    time.sleep(2)
                
                # 3-2. 그룹 내 모든 설정 처리 완료 후 상품을 완료 그룹으로 이동
                logger.info(f"그룹 '{group_name}' 모든 설정 처리 완료, 상품을 완료 그룹으로 이동 시작")
                if not self._move_products_to_completion_group(group_name):
                    logger.warning(f"그룹 '{group_name}' 상품 이동 실패, 계속 진행합니다")
                
                logger.info(f"=== 그룹 '{group_name}' 처리 완료 ===")
            
            logger.info("6-1단계 동적 업로드 워크플로우 완료")
            return True
            
        except Exception as e:
            logger.error(f"동적 업로드 워크플로우 중 오류 발생: {e}")
            return False
    
    def _group_configs_by_groupname(self, market_configs):
        """
        마켓 설정들을 groupname별로 그룹화합니다.
        
        Args:
            market_configs (list): 마켓 설정 리스트
            
        Returns:
            dict: groupname을 키로 하는 설정 그룹 딕셔너리
        """
        try:
            grouped = {}
            for config in market_configs:
                group_name = config['groupname']
                if group_name not in grouped:
                    grouped[group_name] = []
                grouped[group_name].append(config)
            
            logger.info(f"그룹화 완료: {list(grouped.keys())}")
            for group_name, configs in grouped.items():
                logger.info(f"그룹 '{group_name}': {len(configs)}개 설정")
            
            return grouped
            
        except Exception as e:
            logger.error(f"마켓 설정 그룹화 중 오류: {e}")
            return {}
    
    def _move_products_to_completion_group(self, group_name):
        """
        판매중인 모든 상품을 완료 그룹으로 이동합니다.
        
        Args:
            group_name (str): 현재 그룹명 (예: '쇼핑몰A1', '쇼핑몰A2', '쇼핑몰A3')
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"그룹 '{group_name}' 상품을 완료 그룹으로 이동 시작")
            
            # 완료 그룹명 결정
            completion_group = self._get_completion_group_name(group_name)
            if not completion_group:
                logger.error(f"그룹 '{group_name}'에 대한 완료 그룹명을 결정할 수 없습니다")
                return False
            
            logger.info(f"목표 완료 그룹: {completion_group}")
            
            # 초기 설정 (1회만 실행)
            # 1. 등록상품관리 화면으로 이동
            if not self._navigate_to_product_management():
                logger.error("등록상품관리 화면 이동 실패")
                return False
            
            # 2. 현재 그룹 선택
            if not self._select_dynamic_group(group_name):
                logger.error(f"그룹 '{group_name}' 선택 실패")
                return False
            
            # 3. 상태검색 > 판매중 메뉴 선택
            if not self._search_selling_products():
                logger.error("판매중 상품 검색 실패")
                return False
            
            # 상품 이동을 위한 반복 처리 (상품수가 0개가 될 때까지)
            for round_num in range(1, 11):  # 최대 10회차까지 반복
                logger.info(f"상품 이동 {round_num}회차 시작")
                
                # 4. 상품 수 확인
                product_count = self._check_product_count()
                if product_count == 0:
                    logger.info(f"{round_num}회차: 상품이 0개이므로 이동 완료")
                    if round_num == 1:
                        logger.info(f"그룹 '{group_name}'에 이동할 상품이 없습니다")
                    else:
                        logger.info(f"그룹 '{group_name}' 모든 상품 이동 완료")
                    break
                elif product_count == -1:
                    logger.warning(f"{round_num}회차 상품 수 확인 실패, 계속 진행합니다")
                else:
                    logger.info(f"{round_num}회차 확인된 상품 수: {product_count}개")
                
                # 5. 전체선택
                if not self._select_all_products():
                    logger.error(f"{round_num}회차 전체선택 실패")
                    return False
                
                # 6. 그룹지정 모달창을 열고 완료 그룹으로 이동
                if not self._handle_group_assignment(completion_group):
                    logger.error(f"{round_num}회차 그룹 지정 실패")
                    return False
                
                logger.info(f"{round_num}회차 상품 이동 완료")
                
                # 그룹 이동 후 상품검색 버튼 클릭하여 상품 수 갱신
                logger.info("그룹 이동 후 상품검색 버튼 클릭")
                if not self._click_product_search_button():
                    logger.warning("상품검색 버튼 클릭 실패, 계속 진행")
                
                # 다음 회차를 위한 대기
                time.sleep(2)
            
            logger.info(f"그룹 '{group_name}' 상품을 '{completion_group}'으로 이동 완료")
            return True
            
        except Exception as e:
            logger.error(f"상품 그룹 이동 중 오류: {e}")
            return False
    
    def _get_completion_group_name(self, group_name):
        """
        현재 그룹명에 따른 완료 그룹명을 반환합니다.
        
        Args:
            group_name (str): 현재 그룹명
            
        Returns:
            str: 완료 그룹명
        """
        try:
            # 그룹명에 따른 완료 그룹 매핑
            completion_mapping = {
                '쇼핑몰A1': '완료A1',
                '쇼핑몰A2': '완료A2', 
                '쇼핑몰A3': '완료A3'
            }
            
            completion_group = completion_mapping.get(group_name)
            if completion_group:
                logger.info(f"그룹 '{group_name}' -> 완료 그룹 '{completion_group}'")
                return completion_group
            else:
                logger.warning(f"그룹 '{group_name}'에 대한 완료 그룹 매핑을 찾을 수 없습니다")
                return None
                
        except Exception as e:
            logger.error(f"완료 그룹명 결정 중 오류: {e}")
            return None
    
    def _handle_group_assignment(self, target_group):
        """
        그룹지정 모달창을 열고 대상 그룹으로 상품을 이동합니다.
        dropdown_utils2의 안정적인 방식을 사용합니다.
        
        Args:
            target_group (str): 이동할 대상 그룹명
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"그룹지정 모달창을 열고 '{target_group}' 그룹으로 이동")
            
            # dropdown_utils2의 안정적인 그룹 이동 방식 사용
            from dropdown_utils2 import get_product_search_dropdown_manager
            dropdown_manager = get_product_search_dropdown_manager(self.driver)
            
            # 1. 그룹 이동 모달 열기
            if not dropdown_manager.open_group_assignment_modal():
                logger.error("그룹 이동 모달창 열기 실패")
                return False
            
            # 2. 그룹 선택 및 이동
            if not dropdown_manager.select_group_in_modal(target_group):
                logger.error(f"'{target_group}' 그룹 선택 실패")
                return False
            
            logger.info(f"'{target_group}' 그룹으로 이동 완료")
            return True
            
        except Exception as e:
            logger.error(f"그룹지정 처리 중 오류: {e}")
            return False
    

    


    
    def _ensure_main_tab_focus(self):
        """
        메인 퍼센티 탭으로 확실히 복귀하고 불필요한 탭들을 정리합니다.
        
        Returns:
            bool: 성공 여부
        """
        try:
            # 현재 열린 모든 탭 확인
            all_windows = self.driver.window_handles
            logger.info(f"현재 열린 탭 수: {len(all_windows)}")
            
            main_window = None
            
            # 퍼센티 메인 탭 찾기 (URL 기준)
            for window in all_windows:
                try:
                    self.driver.switch_to.window(window)
                    current_url = self.driver.current_url
                    logger.info(f"탭 URL 확인: {current_url}")
                    
                    if "percenty.com" in current_url:
                        main_window = window
                        logger.info(f"퍼센티 메인 탭 발견: {window}")
                        break
                except Exception as e:
                    logger.warning(f"탭 확인 중 오류: {e}")
                    continue
            
            # 메인 탭을 찾지 못한 경우 첫 번째 탭을 메인으로 간주
            if main_window is None:
                main_window = all_windows[0]
                logger.warning("퍼센티 메인 탭을 찾지 못해 첫 번째 탭을 메인으로 설정")
            
            # 다른 탭들 모두 닫기
            for window in all_windows:
                if window != main_window:
                    try:
                        self.driver.switch_to.window(window)
                        self.driver.close()
                        logger.info(f"불필요한 탭 닫기 완료: {window}")
                    except Exception as e:
                        logger.warning(f"탭 닫기 실패: {e}")
                        continue
            
            # 메인 탭으로 최종 복귀
            self.driver.switch_to.window(main_window)
            final_url = self.driver.current_url
            logger.info(f"메인 탭 복귀 완료 - 현재 URL: {final_url}")
            
            # 최종 탭 수 확인
            final_tab_count = len(self.driver.window_handles)
            logger.info(f"탭 정리 완료 - 최종 탭 수: {final_tab_count}")
            
            return True
            
        except Exception as e:
            logger.error(f"메인 탭 복귀 실패: {e}")
            # 최소한 첫 번째 탭으로라도 복귀 시도
            try:
                all_windows = self.driver.window_handles
                if all_windows:
                    self.driver.switch_to.window(all_windows[0])
                    logger.info("첫 번째 탭으로 복귀 완료")
            except:
                logger.error("첫 번째 탭으로 복귀도 실패")
            return False
    
    def _import_11st_products_from_cafe24(self):
        """
        카페24에 로그인하여 11번가 상품을 가져옵니다.
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("카페24 11번가 상품 가져오기 시작")
            
            # 현재 행의 카페24 정보 가져오기
            current_row = self.current_market_config
            cafe24_id = current_row.get('cafe24_id', '')
            cafe24_password = current_row.get('cafe24_password', '')
            store_id_11st = current_row.get('11store_id', '')
            
            # 필수 정보 확인
            if not cafe24_id or not cafe24_password or not store_id_11st:
                logger.warning(f"카페24 정보 부족 - ID: {cafe24_id}, 11번가 스토어 ID: {store_id_11st}")
                return False
            
            logger.info(f"카페24 정보 - ID: {cafe24_id}, 11번가 스토어 ID: {store_id_11st}")
            
            # MarketManagerCafe24 인스턴스 생성
            cafe24_manager = MarketManagerCafe24(self.driver)
            
            # 카페24 로그인 및 11번가 상품 가져오기 실행
            result = cafe24_manager.login_and_import_11st_products(
                cafe24_id=cafe24_id,
                cafe24_password=cafe24_password,
                store_id_11st=store_id_11st
            )
            
            if result:
                logger.info("카페24 11번가 상품 가져오기 성공")
            else:
                logger.error("카페24 11번가 상품 가져오기 실패")
            
            # 카페24 탭 정리 및 퍼센티 메인 탭으로 복귀
            self._cleanup_cafe24_tabs_and_return_to_main()
            
            return result
            
        except Exception as e:
            logger.error(f"카페24 11번가 상품 가져오기 중 오류 발생: {e}")
            # 오류 발생 시에도 탭 정리 시도
            try:
                self._cleanup_cafe24_tabs_and_return_to_main()
            except:
                pass
            return False
    
    def _cleanup_cafe24_tabs_and_return_to_main(self):
        """
        카페24 관련 탭들을 정리하고 퍼센티 메인 탭으로 복귀합니다.
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("카페24 탭 정리 및 퍼센티 메인 탭으로 복귀 시작")
            
            # 현재 열린 모든 탭 확인
            all_windows = self.driver.window_handles
            logger.info(f"현재 열린 탭 수: {len(all_windows)}")
            
            # 퍼센티 메인 탭 찾기 (첫 번째 탭이 보통 메인 탭)
            main_tab = all_windows[0] if all_windows else None
            
            if len(all_windows) > 1:
                # 카페24 탭들 닫기 (메인 탭 제외)
                for i in range(len(all_windows) - 1, 0, -1):  # 뒤에서부터 닫기
                    try:
                        self.driver.switch_to.window(all_windows[i])
                        current_url = self.driver.current_url
                        
                        # 카페24 관련 탭인지 확인
                        if 'cafe24' in current_url.lower() or 'eclogin' in current_url.lower():
                            logger.info(f"카페24 탭 닫기: {current_url}")
                            self.driver.close()
                        else:
                            logger.info(f"카페24가 아닌 탭 유지: {current_url}")
                    except Exception as e:
                        logger.warning(f"탭 {i} 닫기 실패: {e}")
                        continue
            
            # 메인 탭으로 복귀
            if main_tab:
                self.driver.switch_to.window(main_tab)
                logger.info("퍼센티 메인 탭으로 복귀 완료")
                
                # 메인 탭이 퍼센티인지 확인
                try:
                    current_url = self.driver.current_url
                    if 'percenty' in current_url.lower():
                        logger.info(f"퍼센티 메인 탭 확인: {current_url}")
                    else:
                        logger.warning(f"메인 탭이 퍼센티가 아님: {current_url}")
                except:
                    pass
            
            # 탭 정리 후 최종 탭 수 확인
            final_windows = self.driver.window_handles
            logger.info(f"탭 정리 완료 - 최종 탭 수: {len(final_windows)}")
            
            return True
            
        except Exception as e:
            logger.error(f"카페24 탭 정리 및 메인 탭 복귀 중 오류 발생: {e}")
            return False

    
    def _search_unuploaded_products(self):
        """
        미업로드 상품 검색 워크플로우를 실행합니다.
        1. 상태 드롭박스에서 '미업로드' 선택
        2. 마켓에서 '11번가' 선택
        3. 상품 검색 버튼 클릭
        
        Returns:
            bool: 성공 시 True, 실패 시 False
        """
        try:
            logger.info("미업로드 상품 검색 워크플로우 시작")
            
            # 1. 상태 드롭박스에서 '미업로드' 선택
            if not self._select_status_dropdown():
                logger.error("상태 드롭박스 선택 실패")
                return False
            
            # 2. 마켓에서 '11번가' 선택
            if not self._select_11st_market():
                logger.error("11번가 마켓 선택 실패")
                return False
            
            # 3. 상품 검색 버튼 클릭
            if not self._click_product_search_button():
                logger.error("상품 검색 버튼 클릭 실패")
                return False
            
            logger.info("미업로드 상품 검색 워크플로우 완료")
            return True
            
        except Exception as e:
            logger.error(f"미업로드 상품 검색 워크플로우 중 오류 발생: {e}")
            return False
    
    def _search_selling_products(self):
        """
        판매중 상품 검색 워크플로우를 실행합니다.
        1. 상태 드롭박스에서 '판매중' 선택
        2. 마켓에서 '11번가' 선택
        3. 상품 검색 버튼 클릭
        
        Returns:
            bool: 성공 시 True, 실패 시 False
        """
        try:
            logger.info("판매중 상품 검색 워크플로우 시작")
            
            # 1. 상태 드롭박스에서 '판매중' 선택
            if not self._select_status_dropdown("판매중"):
                logger.error("상태 드롭박스 선택 실패")
                return False
            
            # 2. 마켓에서 '11번가' 선택
            if not self._select_11st_market():
                logger.error("11번가 마켓 선택 실패")
                return False
            
            # 3. 상품 검색 버튼 클릭
            if not self._click_product_search_button():
                logger.error("상품 검색 버튼 클릭 실패")
                return False
            
            logger.info("판매중 상품 검색 워크플로우 완료")
            return True
            
        except Exception as e:
            logger.error(f"판매중 상품 검색 워크플로우 중 오류 발생: {e}")
            return False
    
    def _select_status_dropdown(self, status_text="미업로드"):
        """
        상태 드롭박스를 열고 지정된 상태를 선택합니다.
        
        Args:
            status_text (str): 선택할 상태 텍스트 (예: '미업로드', '판매중', '품절' 등)
        
        Returns:
            bool: 성공 시 True, 실패 시 False
        """
        try:
            logger.info(f"상태 드롭박스에서 '{status_text}' 선택 시작")
            
            # 1. 상태 드롭박스 클릭하여 열기 (이미 선택된 상태도 고려한 선택자)
            dropdown_selectors = [
                "//div[contains(@class, 'ant-select') and .//span[contains(text(), '상태 검색')]]",  # 초기 상태
                "//div[contains(@class, 'ant-select') and .//div[contains(@class, 'sc-ciQpPG') and contains(text(), '판매중')]]",  # 판매중 선택된 상태
                "//div[contains(@class, 'ant-select') and .//div[contains(@class, 'sc-ciQpPG') and contains(text(), '미업로드')]]",  # 미업로드 선택된 상태
                "//div[contains(@class, 'ant-select') and .//div[contains(@class, 'sc-ciQpPG')]]",  # 일반적인 선택된 상태
                "//div[contains(@class, 'ant-select') and contains(@style, 'width: 128px')]",  # 스타일 기반 선택
                "//div[contains(@class, 'ant-select-selector')]/parent::div[contains(@class, 'ant-select')]",  # 셀렉터 기반
            ]
            
            dropdown_clicked = False
            for selector in dropdown_selectors:
                try:
                    dropdown_element = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    dropdown_element.click()
                    logger.info(f"상태 드롭박스 클릭 (선택자: {selector})")
                    dropdown_clicked = True
                    break
                except TimeoutException:
                    continue
            
            if not dropdown_clicked:
                logger.error("상태 드롭박스를 찾을 수 없음")
                return False
                
            time.sleep(2)  # 드롭다운 옵션이 로드될 시간 확보
            
            # 2. 지정된 상태 옵션 선택 (실제 DOM 구조 기반 선택자)
            option_selectors = [
                f"//div[contains(@class, 'ant-select-item') and .//div[contains(@class, 'sc-kBRoID') and contains(text(), '{status_text}')]]",
                f"//div[contains(@class, 'ant-select-item') and contains(text(), '{status_text}')]",
                f"//div[contains(@class, 'sc-kBRoID') and contains(text(), '{status_text}')]",
                f"//div[@role='option' and .//div[contains(text(), '{status_text}')]]",
                f"//div[contains(@class, 'ant-select-item') and text()='{status_text}']",
                f"//div[@role='option' and text()='{status_text}']"
            ]
            
            option_clicked = False
            for selector in option_selectors:
                try:
                    option_element = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    option_element.click()
                    logger.info(f"'{status_text}' 옵션 선택 완료 (선택자: {selector})")
                    option_clicked = True
                    break
                except TimeoutException:
                    continue
            
            if not option_clicked:
                logger.error(f"모든 선택자로 '{status_text}' 옵션을 찾을 수 없음")
                return False
                
            time.sleep(1)
            return True
            
        except TimeoutException:
            logger.error(f"상태 드롭박스 또는 '{status_text}' 옵션을 찾을 수 없음")
            return False
        except Exception as e:
            logger.error(f"상태 드롭박스 선택 중 오류 발생: {e}")
            return False
    
    def select_unuploaded_status(self):
        """
        '미업로드' 상태를 선택하는 편의 메서드
        
        Returns:
            bool: 성공 시 True, 실패 시 False
        """
        return self._select_status_dropdown("미업로드")
    
    def select_selling_status(self):
        """
        '판매중' 상태를 선택하는 편의 메서드
        
        Returns:
            bool: 성공 시 True, 실패 시 False
        """
        return self._select_status_dropdown("판매중")
    
    def select_soldout_status(self):
        """
        '품절' 상태를 선택하는 편의 메서드
        
        Returns:
            bool: 성공 시 True, 실패 시 False
        """
        return self._select_status_dropdown("품절")
    
    def _select_11st_market(self):
        """
        마켓 선택 영역에서 '11번가' 체크박스를 선택합니다.
        
        Returns:
            bool: 성공 시 True, 실패 시 False
        """
        try:
            logger.info("마켓에서 '11번가' 선택 시작")
            
            # 쿠팡 체크박스 선택자들
            coupang_selectors = [
                "//label[contains(@class, 'ant-checkbox-wrapper') and .//span[text()='11번가']]",
                "//span[text()='11번가']/ancestor::label[contains(@class, 'ant-checkbox-wrapper')]",
                "//span[text()='11번가']/preceding-sibling::span[contains(@class, 'ant-checkbox')]",
                "//span[text()='11번가']"
            ]
            
            for selector in coupang_selectors:
                try:
                    coupang_element = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    coupang_element.click()
                    time.sleep(1)
                    logger.info("'11번가' 마켓 선택 성공")
                    return True
                except (TimeoutException, NoSuchElementException):
                    continue
            
            logger.error("'11번가' 마켓 체크박스를 찾을 수 없습니다")
            return False
            
        except Exception as e:
            logger.error(f"11번가 마켓 선택 중 오류 발생: {e}")
            return False

    def _click_product_search_button(self):
        """
        상품 검색 버튼을 클릭합니다.
        
        Returns:
            bool: 성공 시 True, 실패 시 False
        """
        try:
            logger.info("상품 검색 버튼 클릭 시작")
            
            # 상품 검색 버튼 선택자들
            search_button_selectors = [
                "//button[@id='filter_search_button_id']",
                "//button[contains(@class, 'ant-btn-primary') and .//span[text()='상품 검색']]",
                "//button[.//span[text()='상품 검색']]",
                "//span[text()='상품 검색']/ancestor::button"
            ]
            
            for selector in search_button_selectors:
                try:
                    search_button = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    search_button.click()
                    time.sleep(2)  # 검색 결과 로딩 대기
                    logger.info("상품 검색 버튼 클릭 성공")
                    return True
                except (TimeoutException, NoSuchElementException):
                    continue
            
            logger.error("상품 검색 버튼을 찾을 수 없습니다")
            return False
            
        except Exception as e:
            logger.error(f"상품 검색 버튼 클릭 중 오류 발생: {e}")
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