# -*- coding: utf-8 -*-
"""6-1단계 동적 업로드 처리 코어 (market_id 시트 기반)

percenty_id.xlsx의 market_id 시트를 파싱하여 동적으로 업로드를 진행합니다.
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

class ProductEditorCore6_Dynamic3:
    """6-1단계 동적 업로드 처리 코어 클래스"""
    
    def __init__(self, driver, account_id, excel_path="percenty_id.xlsx"):
        self.driver = driver
        self.account_id = account_id
        self.excel_path = excel_path
        self.wait = WebDriverWait(driver, 10)
        
        # 유틸리티 클래스 초기화
        self.dropdown_utils = get_product_search_dropdown_manager(driver)
        self.upload_utils = UploadUtils(driver)
        self.market_utils = MarketUtils(driver, logger)
        self.market_manager = MarketManager(driver)
        
        # 스마트스토어 API 키 설정 상태 추적
        self.smartstore_api_configured = False
        
        logger.info(f"ProductEditorCore6_Dynamic3 초기화 완료 - 계정: {account_id}")
    
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
            
            # 3-3. 11번가-글로벌 API 키 입력
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
            
            # 3-4. 옥션/G마켓 API 키 입력
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
            
            # 3-5. 스마트스토어 API 키 입력
            smartstore_api_key = market_config.get('smartstore_api', '')
            logger.info(f"스마트스토어 API 키 확인: {smartstore_api_key[:10] if smartstore_api_key else 'N/A'}...")
            
            if smartstore_api_key:
                logger.info("스마트스토어 API 키 입력 시도 시작")
                if self._input_smartstore_api_key(smartstore_api_key):
                    logger.info("스마트스토어 API 키 입력 성공")
                    api_setup_success = True
                    self.smartstore_api_configured = True  # 스마트스토어 API 키 설정 완료 표시
                else:
                    logger.error("스마트스토어 API 키 입력 실패")
            else:
                logger.info("스마트스토어 API 키가 없어서 입력을 건너뜁니다.")
                self.smartstore_api_configured = False  # 스마트스토어 API 키 미설정 표시
            
            """
            # 3-6. 쿠팡 API 키 입력
            coupang_id = market_config.get('coupang_id', '')
            coupang_code = market_config.get('coupang_code', '')
            coupang_access = market_config.get('coupang_access', '')
            coupang_secret = market_config.get('coupang_secret', '')
            
            logger.info(f"쿠팡 API 키 확인: ID={coupang_id[:10] if coupang_id else 'N/A'}..., Code={coupang_code[:10] if coupang_code else 'N/A'}..., Access={coupang_access[:10] if coupang_access else 'N/A'}..., Secret={coupang_secret[:10] if coupang_secret else 'N/A'}...")
            
            if coupang_id and coupang_code and coupang_access and coupang_secret:
                logger.info("쿠팡 API 키 입력 시도 시작")
                if self._input_coupang_api_keys(coupang_id, coupang_code, coupang_access, coupang_secret):
                    logger.info("쿠팡 API 키 입력 성공")
                    api_setup_success = True
                    self.coupang_api_configured = True  # 쿠팡 API 키 설정 완료 표시
                else:
                    logger.error("쿠팡 API 키 입력 실패")
            else:
                logger.info("쿠팡 API 키가 불완전하여 입력을 건너뜁니다.")
                self.coupang_api_configured = False  # 쿠팡 API 키 미설정 표시
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
    
    def _install_percenty_extension(self):
        """
        퍼센티 확장프로그램을 설치합니다.
        새 탭으로 Chrome 웹 스토어를 열고 '크롬에 추가' 버튼을 클릭한 후
        모달창에서 절대좌표 (1000, 240)를 클릭하여 확장프로그램을 설치합니다.
        
        Returns:
            bool: 성공 여부
        """
        try:
            import pyautogui
            import time
            
            logger.info("퍼센티 확장프로그램 설치 시작")
            
            # 현재 탭 핸들 저장
            original_window = self.driver.current_window_handle
            
            # 새 탭으로 퍼센티 확장프로그램 페이지 열기
            percenty_extension_url = "https://chromewebstore.google.com/detail/%ED%8D%BC%EC%84%BC%ED%8B%B0/jlcdjppbpplpdgfeknhioedbhfceaben?hl=ko&authuser=0"
            self.driver.execute_script(f"window.open('{percenty_extension_url}', '_blank');")
            
            # 새 탭으로 전환
            self.driver.switch_to.window(self.driver.window_handles[-1])
            logger.info("퍼센티 확장프로그램 페이지를 새 탭에서 열었습니다")
            
            # 페이지 로드 대기
            time.sleep(3)
            
            # '크롬에 추가' 버튼 클릭
            try:
                add_to_chrome_selectors = [
                    # 실제 Chrome 웹 스토어 DOM 구조 기반 선택자들 (우선순위 높음)
                    "//button[contains(@class, 'UywwFc-LgbsSe') and contains(.//span[@class='UywwFc-vQzf8d'], 'Chrome에 추가')]",
                    "//button[contains(@class, 'UywwFc-LgbsSe') and contains(.//span[@class='UywwFc-vQzf8d'], '크롬에 추가')]",
                    "//button[contains(@class, 'UywwFc-LgbsSe') and contains(.//span[@class='UywwFc-vQzf8d'], 'Add to Chrome')]",
                    "//span[@class='UywwFc-vQzf8d' and (text()='Chrome에 추가' or text()='크롬에 추가' or text()='Add to Chrome')]/parent::button",
                    "//button[@jsname='wQO0od']",
                    "//button[contains(@class, 'UywwFc-LgbsSe')]",
                    
                    # 기본 버튼 선택자들
                    "//button[contains(text(), '크롬에 추가')]",
                    "//button[contains(text(), 'Chrome에 추가')]",
                    "//button[contains(text(), 'Add to Chrome')]",
                    
                    # 웹스토어 특정 클래스 선택자들
                    "//div[contains(@class, 'webstore-test-button-label') and contains(text(), '크롬에 추가')]",
                    "//div[contains(@class, 'webstore-test-button-label') and contains(text(), 'Chrome에 추가')]",
                    "//div[contains(@class, 'webstore-test-button-label') and contains(text(), 'Add to Chrome')]",
                    
                    # 일반적인 div 선택자들
                    "//div[contains(text(), '크롬에 추가')]",
                    "//div[contains(text(), 'Chrome에 추가')]",
                    "//div[contains(text(), 'Add to Chrome')]",
                    
                    # 역할 기반 선택자들
                    "//div[@role='button' and contains(text(), '크롬에 추가')]",
                    "//div[@role='button' and contains(text(), 'Chrome에 추가')]",
                    "//div[@role='button' and contains(text(), 'Add to Chrome')]",
                    
                    # 클래스 기반 선택자들 (더 포괄적)
                    "//button[contains(@class, 'webstore') and contains(text(), '추가')]",
                    "//div[contains(@class, 'webstore') and contains(text(), '추가')]",
                    "//button[contains(@class, 'install') or contains(@class, 'add')]"
                ]
                
                button_clicked = False
                
                # 먼저 XPath 선택자들 시도
                xpath_selectors = [sel for sel in add_to_chrome_selectors if sel.startswith('//')]
                for selector in xpath_selectors:
                    try:
                        button = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                        button.click()
                        logger.info(f"'크롬에 추가' 버튼 클릭 완료 (선택자: {selector})")
                        button_clicked = True
                        break
                    except TimeoutException:
                        continue
                
                # XPath로 찾지 못한 경우 JavaScript로 직접 검색 및 클릭 시도
                if not button_clicked:
                    try:
                        js_script = """
                        var buttons = document.querySelectorAll('button, div[role="button"], div');
                        for (var i = 0; i < buttons.length; i++) {
                            var text = buttons[i].textContent || buttons[i].innerText;
                            if (text && (text.includes('크롬에 추가') || text.includes('Chrome에 추가') || text.includes('Add to Chrome'))) {
                                buttons[i].click();
                                return true;
                            }
                        }
                        return false;
                        """
                        result = self.driver.execute_script(js_script)
                        if result:
                            logger.info("'크롬에 추가' 버튼 클릭 완료 (JavaScript 방식)")
                            button_clicked = True
                    except Exception as e:
                        logger.warning(f"JavaScript 방식 클릭 실패: {e}")
                
                if not button_clicked:
                    logger.error("'크롬에 추가' 버튼을 찾을 수 없습니다")
                    self.driver.close()
                    self.driver.switch_to.window(original_window)
                    return False
                
                # 모달창이 나타날 때까지 잠시 대기
                time.sleep(2)
                
                # PyAutoGUI를 사용하여 절대좌표 (1000, 240) 클릭
                logger.info("PyAutoGUI로 좌표 (1000, 240) 클릭 시도...")
                pyautogui.click(1000, 240)
                logger.info("PyAutoGUI 클릭 완료: (1000, 240)")
                
                # 확장프로그램 설치 완료 대기
                time.sleep(3)
                
                logger.info("퍼센티 확장프로그램 설치 완료")
                
            except Exception as e:
                logger.error(f"확장프로그램 설치 중 오류: {e}")
            
            # 새 탭 닫기
            self.driver.close()
            
            # 원래 탭으로 돌아가기
            self.driver.switch_to.window(original_window)
            logger.info("원래 탭으로 돌아갔습니다")
            
            return True
            
        except Exception as e:
            logger.error(f"퍼센티 확장프로그램 설치 중 오류 발생: {e}")
            # 오류 발생 시에도 원래 탭으로 돌아가기 시도
            try:
                if len(self.driver.window_handles) > 1:
                    self.driver.close()
                    self.driver.switch_to.window(original_window)
            except:
                pass
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
            
            # 5. API 검증 버튼 클릭 (안정화된 선택자 사용)
            try:
                if not self.market_utils.click_api_validation_button():
                    logger.warning("기본 API 검증 버튼 클릭 실패, 대체 선택자 시도")
                    
                    # 11번가, 스마트스토어, 옥션 등에서 검증된 안정화된 선택자들 사용
                    api_validation_selectors = [
                        # 활성 탭 패널 내 ant-row 컨테이너의 API 검증 버튼 (가장 안정적)
                        '//div[contains(@class, "ant-tabs-tabpane-active")]//div[contains(@class, "ant-row")]//button[contains(@class, "ant-btn-primary") and .//span[text()="API 검증"]]',
                        # 톡스토어 패널 특정 선택자
                        '//div[@id="rc-tabs-0-panel-kakao"]//button[contains(@class, "ant-btn-primary") and .//span[text()="API 검증"]]',
                        # 일반적인 API 검증 버튼 선택자
                        '//button[contains(@class, "ant-btn-primary") and .//span[text()="API 검증"]]'
                    ]
                    
                    api_validation_success = False
                    for i, selector in enumerate(api_validation_selectors, 1):
                        try:
                            logger.info(f"API 검증 버튼 찾기 시도 {i} - XPath: {selector}")
                            element = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                            
                            # 포커스 이동 및 스크롤
                            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                            time.sleep(0.5)
                            self.driver.execute_script("arguments[0].focus();", element)
                            time.sleep(0.5)
                            
                            element.click()
                            logger.info(f"API 검증 버튼 클릭 성공 (선택자 {i})")
                            api_validation_success = True
                            break
                            
                        except Exception as e:
                            logger.warning(f"선택자 {i} 실패: {e}")
                            continue
                    
                    if not api_validation_success:
                        logger.error("모든 API 검증 버튼 선택자 실패")
                        return False
                else:
                    logger.info("기본 API 검증 버튼 클릭 성공")
                
                logger.info("톡스토어 API 검증 성공")
                time.sleep(3)  # 검증 완료 대기 시간 증가
                return True
                
            except Exception as e:
                logger.error(f"톡스토어 API 검증 중 오류: {e}")
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
                try:
                    if not self.market_utils.click_api_validation_button():
                        logger.warning("기본 API 검증 버튼 클릭 실패, 대체 선택자 시도")
                        
                        # 11번가, 스마트스토어, 톡스토어 등에서 검증된 안정화된 선택자들 사용
                        api_validation_selectors = [
                            # 활성 탭 패널 내 ant-row 컨테이너의 API 검증 버튼 (가장 안정적)
                            '//div[contains(@class, "ant-tabs-tabpane-active")]//div[contains(@class, "ant-row")]//button[contains(@class, "ant-btn-primary") and .//span[text()="API 검증"]]',
                            # 옥션/G마켓 패널 특정 선택자
                            '//div[@id="rc-tabs-0-panel-esm"]//button[contains(@class, "ant-btn-primary") and .//span[text()="API 검증"]]',
                            # 일반적인 API 검증 버튼 선택자
                            '//button[contains(@class, "ant-btn-primary") and .//span[text()="API 검증"]]'
                        ]
                        
                        api_validation_success = False
                        for i, selector in enumerate(api_validation_selectors, 1):
                            try:
                                logger.info(f"API 검증 버튼 찾기 시도 {i} - XPath: {selector}")
                                element = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                                
                                # 포커스 이동 및 스크롤
                                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                                time.sleep(0.5)
                                self.driver.execute_script("arguments[0].focus();", element)
                                time.sleep(0.5)
                                
                                element.click()
                                logger.info(f"API 검증 버튼 클릭 성공 (선택자 {i})")
                                api_validation_success = True
                                break
                                
                            except Exception as e:
                                logger.warning(f"선택자 {i} 실패: {e}")
                                continue
                        
                        if not api_validation_success:
                            logger.error("모든 API 검증 버튼 선택자 실패")
                            return False
                    else:
                        logger.info("기본 API 검증 버튼 클릭 성공")
                    
                    logger.info("옥션/G마켓 API 검증 버튼 클릭 성공")
                    time.sleep(1)  # 잠시 대기
                    
                    # 5. API 검증 모달창 처리
                    if self.market_utils.handle_auction_gmarket_api_verification_modal():
                        logger.info("옥션/G마켓 API 검증 성공")
                        return True
                    else:
                        logger.error("옥션/G마켓 API 검증 모달창 처리 실패")
                        return False
                        
                except Exception as e:
                    logger.error(f"옥션/G마켓 API 검증 중 오류: {e}")
                    return False
            else:
                logger.error("옥션/G마켓 API KEY 입력 실패")
                return False
                
        except Exception as e:
            logger.error(f"옥션/G마켓 API KEY 입력 중 오류 발생: {e}")
            return False
    
    def _input_smartstore_api_key(self, api_key):
        """
        스마트스토어 API KEY를 입력합니다.
        
        Args:
            api_key (str): 스마트스토어 API 키
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("스마트스토어 API KEY 입력 시작")
            
            # 1. 스마트스토어 탭 선택
            if not self.market_utils.switch_to_market('smartstore'):
                logger.error("스마트스토어 탭 전환 실패")
                return False
            
            # 2. 스마트스토어 패널 로드 대기
            if not self.market_utils.wait_for_market_panel_load('smartstore'):
                logger.error("스마트스토어 패널 로드 실패")
                return False
            
            # 3. API 키 입력
            try:
                # 스마트스토어 API 키 입력창 선택자들 (두 번째 입력창 - API 연동용 판매자 ID)
                # 성공률이 높은 선택자를 우선순위로 배치
                api_key_selectors = [
                    # 가장 성공률이 높은 선택자 (활성 탭의 비활성화되지 않은 입력창)
                    '.ant-tabs-tabpane-active input[placeholder="미설정"]:not([disabled])',
                    # 스마트스토어 패널의 특정 입력창
                    'div[id="rc-tabs-0-panel-smartstore"] input[placeholder="미설정"]:not([disabled])',
                    # 활성 탭의 두 번째 입력창
                    '.ant-tabs-tabpane-active div:nth-child(2) input[placeholder="미설정"]',
                    # 스마트스토어 패널의 두 번째 입력창
                    'div[id="rc-tabs-0-panel-smartstore"] div:nth-child(2) input[placeholder="미설정"]',
                    # 일반적인 텍스트 입력창
                    'div[id="rc-tabs-0-panel-smartstore"] input[type="text"]:not([disabled])'
                ]
                
                api_key_element = None
                for i, selector in enumerate(api_key_selectors):
                    try:
                        logger.info(f"스마트스토어 API 키 입력창 찾기 시도 {i+1}/{len(api_key_selectors)}")
                        api_key_element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                        
                        # 요소가 보이고 활성화되어 있는지 확인
                        if api_key_element.is_displayed() and api_key_element.is_enabled():
                            logger.info(f"스마트스토어 API 키 입력창 발견 (선택자 {i+1})")
                            break
                        else:
                            logger.warning(f"선택자 {i+1}: 요소가 비활성화되어 있음")
                            api_key_element = None
                            continue
                            
                    except Exception as e:
                        logger.warning(f"선택자 {i+1} 실패: {e}")
                        continue
                
                if not api_key_element:
                    logger.error("스마트스토어 API 키 입력창을 찾을 수 없음")
                    return False
                
                # 입력창에 포커스 설정
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", api_key_element)
                time.sleep(0.5)
                self.driver.execute_script("arguments[0].focus();", api_key_element)
                time.sleep(0.5)
                
                # 기존 값 삭제 후 새 값 입력
                api_key_element.clear()
                time.sleep(0.3)
                api_key_element.send_keys(api_key)
                logger.info(f"스마트스토어 API 키 입력 완료: {api_key[:10]}...")
                
            except Exception as e:
                logger.error(f"스마트스토어 API 키 입력 실패: {e}")
                return False
            
            # 4. API 검증 버튼 클릭 (안정화된 선택자 사용)
            try:
                if not self.market_utils.click_api_validation_button():
                    logger.warning("기본 API 검증 버튼 클릭 실패, 대체 선택자 시도")
                    
                    # 11번가, 톡스토어, 옥션 등에서 검증된 안정화된 선택자들 사용
                    api_validation_selectors = [
                        # 활성 탭 패널 내 ant-row 컨테이너의 API 검증 버튼 (가장 안정적)
                        '//div[contains(@class, "ant-tabs-tabpane-active")]//div[contains(@class, "ant-row")]//button[contains(@class, "ant-btn-primary") and .//span[text()="API 검증"]]',
                        # 스마트스토어 패널 특정 선택자
                        '//div[@id="rc-tabs-0-panel-smartstore"]//button[contains(@class, "ant-btn-primary") and .//span[text()="API 검증"]]',
                        # 일반적인 API 검증 버튼 선택자
                        '//button[contains(@class, "ant-btn-primary") and .//span[text()="API 검증"]]'
                    ]
                    
                    api_validation_success = False
                    for i, selector in enumerate(api_validation_selectors, 1):
                        try:
                            logger.info(f"API 검증 버튼 찾기 시도 {i} - XPath: {selector}")
                            element = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                            
                            # 포커스 이동 및 스크롤
                            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                            time.sleep(0.5)
                            self.driver.execute_script("arguments[0].focus();", element)
                            time.sleep(0.5)
                            
                            element.click()
                            logger.info(f"API 검증 버튼 클릭 성공 (선택자 {i})")
                            api_validation_success = True
                            break
                            
                        except Exception as e:
                            logger.warning(f"선택자 {i} 실패: {e}")
                            continue
                    
                    if not api_validation_success:
                        logger.error("모든 API 검증 버튼 선택자 실패")
                        return False
                else:
                    logger.info("기본 API 검증 버튼 클릭 성공")
                
                time.sleep(3)  # 검증 완료 대기 시간 증가
                
            except Exception as e:
                logger.error(f"API 검증 버튼 클릭 중 오류: {e}")
                return False
            
            # 5. 배송프로필 추가 클릭해서 배송프로필 만들기 모달창 열기
            if not self._add_smartstore_delivery_profile():
                logger.error("스마트스토어 배송프로필 추가 실패")
                return False
            
            # 6. 스마트스토어 로그인 실행
            if not self._login_smartstore():
                logger.error("스마트스토어 로그인 실패")
                return False
            
            logger.info("스마트스토어 API 키 입력, 배송프로필 설정 및 로그인 완료")
            return True
                
        except Exception as e:
            logger.error(f"스마트스토어 API KEY 입력 중 오류 발생: {e}")
            return False
    
    def _add_smartstore_delivery_profile(self):
        """
        스마트스토어 배송프로필을 추가합니다.
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("스마트스토어 배송프로필 추가 시작")
            
            # 1. 배송프로필 추가 버튼 클릭
            try:
                add_profile_selector = 'button[class*="ant-btn"][class*="ant-btn-primary"][class*="ant-btn-background-ghost"] span:contains("배송 프로필 추가")'
                # CSS 선택자로 다시 시도
                add_profile_selector = 'button.ant-btn.ant-btn-primary.ant-btn-background-ghost'
                add_profile_elements = self.driver.find_elements(By.CSS_SELECTOR, add_profile_selector)
                
                # 텍스트로 필터링
                add_profile_button = None
                for element in add_profile_elements:
                    if "배송 프로필 추가" in element.text:
                        add_profile_button = element
                        break
                
                if not add_profile_button:
                    logger.error("배송프로필 추가 버튼을 찾을 수 없음")
                    return False
                
                add_profile_button.click()
                logger.info("배송프로필 추가 버튼 클릭 완료")
                time.sleep(2)  # 모달창 로드 대기
                
            except Exception as e:
                logger.error(f"배송프로필 추가 버튼 클릭 실패: {e}")
                return False
            
            # 2. 택배사 드롭박스에서 롯데택배 선택
            try:
                # 드롭다운 클릭
                dropdown_selector = '.ant-select-selector'
                dropdown_element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, dropdown_selector)))
                dropdown_element.click()
                logger.info("택배사 드롭다운 클릭 완료")
                time.sleep(1)
                
                # 롯데택배 옵션 선택
                lotte_option_selector = '.ant-select-item-option[title="롯데택배"]'
                lotte_option = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, lotte_option_selector)))
                lotte_option.click()
                logger.info("롯데택배 선택 완료")
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"롯데택배 선택 실패: {e}")
                return False
            
            # 3. 배송프로필 만들기 버튼 클릭해서 모달창 닫기
            try:
                create_profile_selector = 'button.ant-btn.ant-btn-primary'
                create_profile_elements = self.driver.find_elements(By.CSS_SELECTOR, create_profile_selector)
                
                # 텍스트로 필터링
                create_profile_button = None
                for element in create_profile_elements:
                    if "배송프로필 만들기" in element.text:
                        create_profile_button = element
                        break
                
                if not create_profile_button:
                    logger.error("배송프로필 만들기 버튼을 찾을 수 없음")
                    return False
                
                create_profile_button.click()
                logger.info("배송프로필 만들기 버튼 클릭 완료")
                time.sleep(2)  # 모달창 닫기 대기
                
            except Exception as e:
                logger.error(f"배송프로필 만들기 버튼 클릭 실패: {e}")
                return False
            
            logger.info("스마트스토어 배송프로필 추가 완료")
            return True
            
        except Exception as e:
            logger.error(f"스마트스토어 배송프로필 추가 중 오류 발생: {e}")
            return False
    
    def _login_smartstore(self):
        """
        스마트스토어 로그인을 수행합니다.
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("스마트스토어 로그인 시작")
            
            # 현재 설정된 마켓 설정에서 스마트스토어 로그인 정보 가져오기
            if not hasattr(self, 'current_market_config') or not self.current_market_config:
                logger.error("마켓 설정 정보가 없습니다")
                return False
            
            smartstore_id = self.current_market_config.get('smartstore_id', '')
            smartstore_password = self.current_market_config.get('smartstore_password', '')
            
            if not smartstore_id or not smartstore_password:
                logger.error("스마트스토어 로그인 정보가 없습니다")
                return False
            
            logger.info(f"스마트스토어 로그인 정보 확인 - ID: {smartstore_id}")
            
            # 1. 새탭에서 스마트스토어 열기
            original_window = self.driver.current_window_handle
            self.driver.execute_script("window.open('https://sell.smartstore.naver.com/', '_blank');")
            
            # 새 탭으로 전환
            all_windows = self.driver.window_handles
            new_window = [window for window in all_windows if window != original_window][0]
            self.driver.switch_to.window(new_window)
            logger.info("스마트스토어 새탭 열기 완료")
            
            time.sleep(8)  # 페이지 로드 대기 (충분히 증가)
             
            # 페이지가 완전히 로드될 때까지 대기
            try:
                self.wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
                logger.info("페이지 로드 완료 확인")
                time.sleep(3)  # 추가 안정화 대기
            except Exception as e:
                logger.warning(f"페이지 로드 상태 확인 실패: {e}")
             
            # 2. 로그인하기 버튼 클릭 (실제 DOM 구조 기반)
            try:
                # 실제 DOM 구조에 맞는 정확한 선택자
                login_button_selector = 'button.btn.btn-login.nlog-click[click-area="main.sellerlogin"]'
                logger.info(f"로그인 버튼 선택자 시도: {login_button_selector}")
                login_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, login_button_selector)))
                login_button.click()
                logger.info("로그인하기 버튼 클릭 완료")
                time.sleep(5)  # 로그인 화면 로드 대기 (충분히 증가)
                 
            except Exception as e:
                 logger.error(f"로그인하기 버튼 클릭 실패: {e}")
                 # 대안 선택자 시도
                 try:
                     logger.info("대안 선택자로 재시도")
                     alternative_selector = 'button.btn-login[ng-click="vm.login()"]'
                     login_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, alternative_selector)))
                     login_button.click()
                     logger.info("대안 선택자로 로그인 버튼 클릭 완료")
                     time.sleep(5)
                 except Exception as e2:
                     logger.error(f"대안 선택자도 실패: {e2}")
                     # 페이지 소스 일부 로깅 (디버깅용)
                     try:
                         page_source = self.driver.page_source[:2000]
                         logger.debug(f"페이지 소스 일부: {page_source}")
                     except:
                         pass
                     self.driver.close()
                     self.driver.switch_to.window(original_window)
                     return False
            
            # 3. 아이디와 비밀번호 입력
            try:
                # 아이디 입력
                id_input_selector = 'input.Login_ipt__6a-x7[type="text"][placeholder="아이디 또는 이메일 주소"]'
                id_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, id_input_selector)))
                id_input.clear()
                id_input.send_keys(smartstore_id)
                logger.info("아이디 입력 완료")
                
                # 비밀번호 입력
                password_input_selector = 'input.Login_ipt__6a-x7[type="password"][placeholder="비밀번호"]'
                password_input = self.driver.find_element(By.CSS_SELECTOR, password_input_selector)
                password_input.clear()
                password_input.send_keys(smartstore_password)
                logger.info("비밀번호 입력 완료")
                
                time.sleep(1)  # 입력 완료 대기
                
            except Exception as e:
                logger.error(f"아이디/비밀번호 입력 실패: {e}")
                self.driver.close()
                self.driver.switch_to.window(original_window)
                return False
            
            # 4. 로그인 버튼 클릭
            try:
                login_submit_selector = 'button.Button_btn__wNWXt.Button_btn_plain__vwFfm'
                login_submit_button = self.driver.find_element(By.CSS_SELECTOR, login_submit_selector)
                
                # 버튼 텍스트 확인
                if "로그인" in login_submit_button.text:
                    login_submit_button.click()
                    logger.info("로그인 버튼 클릭 완료")
                    time.sleep(5)  # 로그인 처리 대기
                else:
                    logger.error("로그인 버튼을 찾을 수 없음")
                    self.driver.close()
                    self.driver.switch_to.window(original_window)
                    return False
                
            except Exception as e:
                logger.error(f"로그인 버튼 클릭 실패: {e}")
                self.driver.close()
                self.driver.switch_to.window(original_window)
                return False
            
            # 5. 로그인 성공 확인 (간단한 URL 체크)
            try:
                # 로그인 후 URL 변화 확인
                current_url = self.driver.current_url
                if "sell.smartstore.naver.com" in current_url and "login" not in current_url:
                    logger.info("스마트스토어 로그인 성공 확인")
                else:
                    logger.warning(f"로그인 상태 불확실 - 현재 URL: {current_url}")
                
            except Exception as e:
                logger.warning(f"로그인 상태 확인 중 오류: {e}")
            
            # 6. 새탭 닫기
            try:
                self.driver.close()
                self.driver.switch_to.window(original_window)
                logger.info("스마트스토어 로그인 탭 닫기 완료")
                
            except Exception as e:
                logger.error(f"탭 닫기 실패: {e}")
                # 원래 탭으로 돌아가기 시도
                try:
                    self.driver.switch_to.window(original_window)
                except:
                    pass
            
            logger.info("스마트스토어 로그인 완료")
            return True
            
        except Exception as e:
            logger.error(f"스마트스토어 로그인 중 오류 발생: {e}")
            # 오류 발생 시 원래 탭으로 돌아가기 시도
            try:
                if hasattr(self, 'driver') and self.driver:
                    current_handles = self.driver.window_handles
                    if len(current_handles) > 1:
                        self.driver.close()
                    if original_window in current_handles:
                        self.driver.switch_to.window(original_window)
            except:
                pass
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
        쿠팡을 포함한 미업로드 상품을 처리합니다.
        
        Args:
            group_name (str): 업로드할 그룹명
            market_config (dict): 마켓 설정 정보
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"상품 업로드 워크플로우 시작: {group_name}")
            
            # 1-4단계를 2회 반복
            for round_num in range(1, 3):  # 1회차, 2회차
                logger.info(f"업로드 {round_num}회차 시작")
                
                # 1. 상품 수 확인 (0개인 경우 스킵)
                product_count = self._check_product_count()
                if product_count == 0:
                    logger.info(f"그룹 '{group_name}'에 상품이 0개이므로 워크플로우를 스킵합니다")
                    return True
                elif product_count == -1:
                    logger.warning(f"{round_num}회차 상품 수 확인 실패, 계속 진행합니다")
                else:
                    logger.info(f"{round_num}회차 확인된 상품 수: {product_count}개")
                
                # 2. 50개씩 보기 설정 
                # if not self._set_items_per_page_50(): 
                #    logger.error("50개씩 보기 설정 실패") 
                #    return False
                
                # 3. 전체선택
                if not self._select_all_products():
                    logger.error(f"{round_num}회차 전체선택 실패")
                    return False
                
                # 4. 업로드 버튼 클릭해서 업로드 모달창 열고 선택 상품 일괄 업로드 클릭
                if not self._handle_bulk_upload():
                    logger.error(f"{round_num}회차 일괄 업로드 처리 실패")
                    return False
                
                # 5. 업로드 완료 대기 및 모달창 닫기
                if not self._wait_for_upload_completion():
                    logger.warning(f"{round_num}회차 업로드 완료 대기 또는 모달창 닫기에 실패했지만 계속 진행합니다")
                
                # 모달창 닫기 후 안정성을 위한 대기
                time.sleep(5)
                
                # 2회차가 아닌 경우에만 새로고침 버튼 클릭
                if round_num < 2:
                    logger.info(f"{round_num}회차 완료, 새로고침 버튼 클릭 후 다음 회차 진행")
                    try:
                        # 새로고침 버튼 클릭
                        refresh_button = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'ant-btn-primary') and contains(@class, 'ant-btn-background-ghost')]//span[text()='새로고침']/parent::button"))
                        )
                        refresh_button.click()
                        logger.info("새로고침 버튼 클릭 완료")
                        time.sleep(3)  # 새로고침 후 대기
                    except Exception as e:
                        logger.error(f"새로고침 버튼 클릭 실패: {e}")
                        # 화면 새로고침은 선택된 그룹이 유지되지 않으므로 사용하지 않음
            
            # 6. 스마트스토어 배송정보 변경 (2회 업로드 완료 후)
            if not self._update_smartstore_delivery_info():
                logger.warning("스마트스토어 배송정보 변경에 실패했지만 계속 진행합니다")
            
            # 7. 카페24 로그인해서 11번가 등록자료 가져오기
            if not self._import_11st_products_from_cafe24():
                logger.warning("카페24 11번가 상품 가져오기에 실패했지만 계속 진행합니다")
            
            # 8. 쿠팡 API 연동업체를 '넥스트엔진'으로 변경
            coupang_id = market_config.get('coupang_id', '')
            coupang_password = market_config.get('coupang_password', '')
            
            if coupang_id and coupang_password:
                logger.info("쿠팡 API 연동업체를 '넥스트엔진'으로 변경 시작")
                try:
                    coupang_manager = CoupangMarketManager(self.driver, self.wait)
                    if coupang_manager.change_api_integrator_to_nextengine(market_config):
                        logger.info("쿠팡 API 연동업체를 '넥스트엔진'으로 변경 완료")
                    else:
                        logger.warning("쿠팡 API 연동업체 '넥스트엔진' 변경에 실패했지만 계속 진행합니다")
                except Exception as e:
                    logger.error(f"쿠팡 API 연동업체 변경 중 오류 발생: {str(e)}")
            else:
                logger.info("쿠팡 로그인 정보가 없어 연동업체 변경을 건너뜁니다")
            
            # 9. 쿠팡 로그아웃
            if coupang_id and coupang_password:
                logger.info("쿠팡 로그아웃 시작")
                try:
                    coupang_manager = CoupangMarketManager(self.driver, self.wait)
                    if coupang_manager.logout_coupang():
                        logger.info("쿠팡 로그아웃 완료")
                    else:
                        logger.warning("쿠팡 로그아웃에 실패했지만 계속 진행합니다")
                except Exception as e:
                    logger.error(f"쿠팡 로그아웃 중 오류 발생: {str(e)}")
            else:
                logger.info("쿠팡 로그인 정보가 없어 로그아웃을 건너뜁니다")
            
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
            
            # dropdown_utils2의 select_all_products 메서드 사용
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
                
                # 각 마켓 설정 처리 시작 시 스마트스토어 API 설정 상태 초기화
                self.smartstore_api_configured = False
                
                # 두 번째 마켓부터 DOM 간섭 방지를 위한 페이지 새로고침
                if idx > 1:
                    logger.info("이전 마켓 설정 DOM 간섭 방지를 위해 페이지 새로고침")
                    self.driver.refresh()
                    time.sleep(5)  # 페이지 로드 대기
                
                # 2-1. 마켓 설정 화면 정보 처리
                if not self.setup_market_configuration(market_config):
                    logger.error(f"마켓 설정 {idx} 처리 실패")
                    self._ensure_main_tab_focus()
                    continue
                
                # 2-2. 등록상품관리 화면으로 전환
                if not self._navigate_to_product_management():
                    logger.error(f"등록상품관리 화면 전환 실패")
                    self._ensure_main_tab_focus()
                    continue
                
                # 2-3. 상품검색 드롭박스를 열고 동적 그룹 선택
                if not self._select_dynamic_group(market_config['groupname']):
                    logger.error(f"동적 그룹 선택 실패: {market_config['groupname']}")
                    continue
                
                # 2-4. 미업로드 상품 검색 워크플로우
                if not self._search_unuploaded_products():
                    logger.error("미업로드 상품 검색 실패")
                    continue
                
                # 2-5. 상품 업로드 워크플로우 실행 (product_editor_core6_1 기능 통합)
                if not self._execute_product_upload_workflow(market_config['groupname'], market_config):
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
    
    def _update_smartstore_delivery_info(self):
        """
        스마트스토어 배송정보 변경을 수행합니다.
        스마트스토어 API 키가 설정되지 않은 경우 건너뜁니다.
        
        Returns:
            bool: 성공 시 True, 실패 시 False
        """
        try:
            # 스마트스토어 API 키 설정 여부 확인
            if not self.smartstore_api_configured:
                logger.info("스마트스토어 API 키가 설정되지 않아 배송정보 변경을 건너뜁니다")
                return True  # 건너뛰는 것은 성공으로 처리
            
            logger.info("스마트스토어 배송정보 변경을 시작합니다")
            
            # MarketManager를 통해 스마트스토어 배송정보 변경 실행
            result = self.market_manager.update_smartstore_delivery_info()
            
            if result:
                logger.info("스마트스토어 배송정보 변경이 완료되었습니다")
            else:
                logger.warning("스마트스토어 배송정보 변경에 실패했습니다")
            
            return result
            
        except Exception as e:
            logger.error(f"스마트스토어 배송정보 변경 중 오류 발생: {e}")
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
    
    def _input_coupang_api_keys(self, coupang_id, coupang_code, coupang_access, coupang_secret):
        """
        쿠팡 API 키 정보를 입력합니다.
        
        Args:
            coupang_id (str): 쿠팡 ID
            coupang_code (str): 업체 코드
            coupang_access (str): Access Key
            coupang_secret (str): Secret Key
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("쿠팡 API 키 입력 시작")
            
            # 1. 쿠팡 탭 선택
            logger.info("쿠팡 탭 선택 시도")
            coupang_tab_selectors = [
                "//div[contains(@class, 'ant-tabs-tab') and contains(., '쿠팡')]",
                "//div[@role='tab' and contains(., '쿠팡')]",
                "//div[contains(@class, 'ant-tabs-tab-btn') and contains(., '쿠팡')]"
            ]
            
            tab_clicked = False
            for selector in coupang_tab_selectors:
                try:
                    tab_element = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    tab_element.click()
                    logger.info(f"쿠팡 탭 클릭 성공: {selector}")
                    tab_clicked = True
                    time.sleep(1)
                    break
                except Exception as e:
                    logger.debug(f"쿠팡 탭 선택자 실패: {selector} - {e}")
                    continue
            
            if not tab_clicked:
                logger.error("쿠팡 탭 선택 실패")
                return False
            
            # 2. 입력창들 찾기 및 입력
            input_data = [
                ("쿠팡 ID", coupang_id),
                ("업체 코드", coupang_code),
                ("Access Key", coupang_access),
                ("Secret Key", coupang_secret)
            ]
            
            # 쿠팡 섹션의 입력창들 선택자
            input_selectors = [
                "//div[contains(@class, 'ant-collapse-content-box')]//input[@placeholder='미설정']",
                "//div[contains(., '쿠팡')]//input[contains(@class, 'ant-input')]",
                "//input[contains(@class, 'ant-input') and @placeholder='미설정']"
            ]
            
            inputs_found = False
            for base_selector in input_selectors:
                try:
                    # 모든 입력창 찾기
                    input_elements = self.driver.find_elements(By.XPATH, base_selector)
                    
                    if len(input_elements) >= 4:
                        logger.info(f"쿠팡 입력창 {len(input_elements)}개 발견")
                        
                        # 각 입력창에 데이터 입력
                        for i, (field_name, value) in enumerate(input_data):
                            if i < len(input_elements):
                                try:
                                    input_element = input_elements[i]
                                    
                                    # 입력창 클리어 및 입력
                                    input_element.clear()
                                    input_element.send_keys(value)
                                    logger.info(f"{field_name} 입력 완료")
                                    time.sleep(0.5)
                                    
                                except Exception as e:
                                    logger.error(f"{field_name} 입력 실패: {e}")
                                    return False
                        
                        inputs_found = True
                        break
                        
                except Exception as e:
                    logger.debug(f"입력창 선택자 실패: {base_selector} - {e}")
                    continue
            
            if not inputs_found:
                logger.error("쿠팡 API 키 입력창들을 찾을 수 없습니다")
                return False
            
            # 3. API 검증 버튼 클릭 및 동적 감지
            logger.info("API 검증 버튼 클릭 및 배송 프로필 감지 시작")
            
            # API 검증 버튼 선택자
            api_verify_selectors = [
                "//button[contains(@class, 'ant-btn-primary') and contains(., 'API 검증')]",
                "//button[contains(., 'API 검증')]",
                "//span[text()='API 검증']/parent::button"
            ]
            
            # 배송 프로필 감지 선택자 (출고지, 반품지, 출고택배사 포함)
            shipping_profile_selectors = [
                "//div[contains(text(), '출고지:')]",
                "//div[contains(text(), '반품지:')]", 
                "//div[contains(text(), '출고택배사:')]",
                "//div[contains(@class, 'Body3Regular14') and contains(text(), '출고지')]",
                "//div[contains(@class, 'Body3Regular14') and contains(text(), '반품지')]",
                "//div[contains(@class, 'Body3Regular14') and contains(text(), '출고택배사')]"
            ]
            
            # 최대 20회 시도
            max_attempts = 20
            profile_detected = False
            
            for attempt in range(max_attempts):
                logger.info(f"API 검증 시도 {attempt + 1}/{max_attempts}")
                
                # API 검증 버튼 클릭
                verify_clicked = False
                for selector in api_verify_selectors:
                    try:
                        verify_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        verify_button.click()
                        logger.info(f"API 검증 버튼 클릭 성공: {selector}")
                        verify_clicked = True
                        break
                    except Exception as e:
                        logger.debug(f"API 검증 버튼 선택자 실패: {selector} - {e}")
                        continue
                
                if not verify_clicked:
                    logger.warning(f"API 검증 버튼 클릭 실패 (시도 {attempt + 1})")
                    time.sleep(60)  # 60초 대기 후 재시도
                    continue
                
                # 검증 처리 대기
                time.sleep(10)
                
                # 배송 프로필 선택자 감지 확인
                for profile_selector in shipping_profile_selectors:
                    try:
                        profile_element = self.driver.find_element(By.XPATH, profile_selector)
                        if profile_element.is_displayed():
                            logger.info(f"배송 프로필 감지 성공: {profile_selector}")
                            profile_detected = True
                            break
                    except Exception:
                        continue
                
                if profile_detected:
                    logger.info(f"배송 프로필 감지 완료 (시도 {attempt + 1}/{max_attempts})")
                    break
                else:
                    logger.info(f"배송 프로필 미감지, 재시도 대기 중... (시도 {attempt + 1}/{max_attempts})")
                    time.sleep(60)  # 60초 대기 후 재시도
            
            if not profile_detected:
                logger.warning(f"최대 {max_attempts}회 시도 후에도 배송 프로필을 감지하지 못했습니다. 다음 단계로 진행합니다.")
            else:
                logger.info("쿠팡 API 검증 및 배송 프로필 감지 완료")
            
            logger.info("쿠팡 API 키 입력 완료")
            return True
            
        except Exception as e:
            logger.error(f"쿠팡 API 키 입력 중 오류 발생: {e}")
            return False
    
    def _search_unuploaded_products(self):
        """
        미업로드 상품 검색 워크플로우를 실행합니다.
        1. 상태 드롭박스에서 '미업로드' 선택
        2. 마켓에서 '쿠팡' 선택
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
            
            # 2. 마켓에서 '쿠팡' 선택
            if not self._select_coupang_market():
                logger.error("쿠팡 마켓 선택 실패")
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
    
    def _select_status_dropdown(self):
        """
        상태 드롭박스를 열고 '미업로드'를 선택합니다.
        
        Returns:
            bool: 성공 시 True, 실패 시 False
        """
        try:
            logger.info("상태 드롭박스에서 '미업로드' 선택 시작")
            
            # 상태 드롭박스 클릭하여 열기
            status_dropdown_selectors = [
                "//div[contains(@class, 'ant-select') and .//span[contains(text(), '상태 검색')]]",
                "//div[contains(@class, 'ant-select-selector') and .//span[contains(text(), '상태 검색')]]",
                "//span[contains(text(), '상태 검색')]/ancestor::div[contains(@class, 'ant-select')]"
            ]
            
            dropdown_clicked = False
            for selector in status_dropdown_selectors:
                try:
                    dropdown_element = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    dropdown_element.click()
                    time.sleep(1)
                    dropdown_clicked = True
                    logger.info("상태 드롭박스 클릭 성공")
                    break
                except (TimeoutException, NoSuchElementException):
                    continue
            
            if not dropdown_clicked:
                logger.error("상태 드롭박스를 찾을 수 없습니다")
                return False
            
            # '미업로드' 옵션 선택
            unuploaded_option_selectors = [
                "//div[contains(@class, 'ant-select-item') and contains(text(), '미업로드')]",
                "//div[contains(@class, 'rc-virtual-list-holder')]//div[contains(text(), '미업로드')]",
                "//div[@role='option' and contains(text(), '미업로드')]"
            ]
            
            for selector in unuploaded_option_selectors:
                try:
                    option_element = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    option_element.click()
                    time.sleep(1)
                    logger.info("'미업로드' 옵션 선택 성공")
                    return True
                except (TimeoutException, NoSuchElementException):
                    continue
            
            logger.error("'미업로드' 옵션을 찾을 수 없습니다")
            return False
            
        except Exception as e:
            logger.error(f"상태 드롭박스 선택 중 오류 발생: {e}")
            return False
    
    def _select_coupang_market(self):
        """
        마켓 선택 영역에서 '쿠팡' 체크박스를 선택합니다.
        
        Returns:
            bool: 성공 시 True, 실패 시 False
        """
        try:
            logger.info("마켓에서 '쿠팡' 선택 시작")
            
            # 쿠팡 체크박스 선택자들
            coupang_selectors = [
                "//label[contains(@class, 'ant-checkbox-wrapper') and .//span[text()='쿠팡']]",
                "//span[text()='쿠팡']/ancestor::label[contains(@class, 'ant-checkbox-wrapper')]",
                "//span[text()='쿠팡']/preceding-sibling::span[contains(@class, 'ant-checkbox')]",
                "//span[text()='쿠팡']"
            ]
            
            for selector in coupang_selectors:
                try:
                    coupang_element = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    coupang_element.click()
                    time.sleep(1)
                    logger.info("'쿠팡' 마켓 선택 성공")
                    return True
                except (TimeoutException, NoSuchElementException):
                    continue
            
            logger.error("'쿠팡' 마켓 체크박스를 찾을 수 없습니다")
            return False
            
        except Exception as e:
            logger.error(f"쿠팡 마켓 선택 중 오류 발생: {e}")
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