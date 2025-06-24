import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import logging

class MarketUtils:
    """마켓 설정 관련 유틸리티 클래스"""
    
    def __init__(self, driver, logger=None):
        self.driver = driver
        self.logger = logger or logging.getLogger(__name__)
        self.wait = WebDriverWait(driver, 10)
        
        # 마켓 탭 정의 (data-node-key 기반)
        self.market_tabs = {
            'coupang': 'cp',
            'smartstore': 'ss', 
            'auction_gmarket': 'esm',
            '11st_general': 'est',
            '11st_global': 'est_global',
            'lotteon': 'lotteon',
            'kakao': 'kakao',
            'interpark': 'ip',
            'wemakeprice': 'wmp'
        }
        
        # 마켓 한글명 매핑
        self.market_names = {
            'coupang': '쿠팡',
            'smartstore': '스마트스토어',
            'auction_gmarket': '옥션/G마켓 (ESM 2.0)',
            '11st_general': '11번가-일반',
            '11st_global': '11번가-글로벌',
            'lotteon': '롯데온',
            'kakao': '톡스토어',
            'interpark': '인터파크',
            'wemakeprice': '위메프'
        }
    
    def get_market_tab_selector(self, market_key):
        """특정 마켓 탭의 선택자를 반환합니다."""
        if market_key not in self.market_tabs:
            raise ValueError(f"지원하지 않는 마켓 키: {market_key}")
        
        node_key = self.market_tabs[market_key]
        return f'div[data-node-key="{node_key}"] .ant-tabs-tab-btn'
    
    def get_market_tab_by_text_selector(self, market_text):
        """마켓 텍스트로 탭 선택자를 반환합니다."""
        return f'//button[contains(@class, "ant-tabs-tab-btn") and contains(text(), "{market_text}")]'
    
    def get_active_market_tab_selector(self):
        """현재 활성화된 마켓 탭의 선택자를 반환합니다."""
        return '.ant-tabs-tab.ant-tabs-tab-active .ant-tabs-tab-btn'
    
    def get_all_market_tabs_selector(self):
        """모든 마켓 탭의 선택자를 반환합니다."""
        return '.ant-tabs-tab .ant-tabs-tab-btn'
    
    def click_market_tab(self, market_key):
        """특정 마켓 탭을 클릭합니다."""
        try:
            # 탭 클릭 전에 남아있는 모달창 확인 및 제거
            self.ensure_no_modal_interference()
            
            selector = self.get_market_tab_selector(market_key)
            element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            element.click()
            
            market_name = self.market_names.get(market_key, market_key)
            self.logger.info(f"{market_name} 탭 클릭 완료")
            
            # 탭 전환 완료 대기
            time.sleep(1)
            return True
            
        except TimeoutException:
            self.logger.error(f"마켓 탭 클릭 실패 - 요소를 찾을 수 없음: {market_key}")
            return False
        except Exception as e:
            self.logger.error(f"마켓 탭 클릭 중 오류 발생: {e}")
            return False
    
    def click_market_tab_by_text(self, market_text):
        """마켓 텍스트로 탭을 클릭합니다."""
        try:
            # 탭 클릭 전에 모달창이 열려있는지 확인하고 닫기
            self.close_any_open_modal()
            
            # JavaScript를 사용하여 텍스트로 요소 찾기
            script = f"""
            var tabs = document.querySelectorAll('.ant-tabs-tab-btn');
            for (var i = 0; i < tabs.length; i++) {{
                if (tabs[i].textContent.trim() === '{market_text}') {{
                    tabs[i].click();
                    return true;
                }}
            }}
            return false;
            """
            
            result = self.driver.execute_script(script)
            if result:
                self.logger.info(f"{market_text} 탭 클릭 완료")
                # 탭 전환 후 DOM 업데이트를 위한 충분한 대기
                time.sleep(2)
                
                # 탭이 실제로 활성화되었는지 확인
                max_retries = 5
                for retry in range(max_retries):
                    current_active = self.get_current_active_market()
                    if current_active == market_text:
                        self.logger.info(f"{market_text} 탭 활성화 확인됨")
                        return True
                    time.sleep(0.5)
                
                self.logger.warning(f"{market_text} 탭 클릭했지만 활성화 확인 실패")
                return True  # 클릭은 성공했으므로 True 반환
            else:
                self.logger.error(f"마켓 탭을 찾을 수 없음: {market_text}")
                return False
                
        except Exception as e:
            self.logger.error(f"마켓 탭 클릭 중 오류 발생: {e}")
            return False
    
    def get_current_active_market(self):
        """현재 활성화된 마켓 탭의 텍스트를 반환합니다."""
        try:
            selector = self.get_active_market_tab_selector()
            element = self.driver.find_element(By.CSS_SELECTOR, selector)
            return element.text.strip()
        except NoSuchElementException:
            self.logger.error("활성화된 마켓 탭을 찾을 수 없음")
            return None
        except Exception as e:
            self.logger.error(f"활성화된 마켓 탭 확인 중 오류 발생: {e}")
            return None
    
    def get_available_markets(self):
        """사용 가능한 모든 마켓 목록을 반환합니다."""
        try:
            selector = self.get_all_market_tabs_selector()
            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            return [element.text.strip() for element in elements]
        except Exception as e:
            self.logger.error(f"마켓 목록 조회 중 오류 발생: {e}")
            return []
    
    def is_market_tab_active(self, market_key):
        """특정 마켓 탭이 활성화되어 있는지 확인합니다."""
        try:
            current_market = self.get_current_active_market()
            expected_market = self.market_names.get(market_key, market_key)
            return current_market == expected_market
        except Exception as e:
            self.logger.error(f"마켓 탭 활성화 상태 확인 중 오류 발생: {e}")
            return False
    
    def switch_to_market(self, market_key):
        """특정 마켓으로 전환합니다 (이미 활성화되어 있으면 스킵)."""
        if self.is_market_tab_active(market_key):
            market_name = self.market_names.get(market_key, market_key)
            self.logger.info(f"{market_name} 탭이 이미 활성화되어 있음")
            return True
        
        return self.click_market_tab(market_key)
    
    def get_market_panel_selector(self, market_key):
        """특정 마켓의 패널 선택자를 반환합니다."""
        if market_key not in self.market_tabs:
            raise ValueError(f"지원하지 않는 마켓 키: {market_key}")
        
        node_key = self.market_tabs[market_key]
        return f'div[id="rc-tabs-0-panel-{node_key}"]'
    
    def wait_for_market_panel_load(self, market_key, timeout=15):
        """특정 마켓 패널이 로드될 때까지 대기합니다."""
        try:
            panel_selector = self.get_market_panel_selector(market_key)
            # 1. 패널 존재 확인
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, panel_selector))
            )
            
            # 2. 패널이 보이는지 확인
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, panel_selector))
            )
            
            # 3. 패널 내부 콘텐츠 로드 대기 (버튼이나 폼 요소가 나타날 때까지)
            time.sleep(2)  # DOM 렌더링 완료를 위한 추가 대기
            
            # 4. 패널 내부에 버튼이 있는지 확인
            try:
                panel_element = self.driver.find_element(By.CSS_SELECTOR, panel_selector)
                buttons = panel_element.find_elements(By.TAG_NAME, "button")
                if len(buttons) == 0:
                    self.logger.warning(f"{market_key} 패널에 버튼이 없음, 추가 대기")
                    time.sleep(3)
            except:
                pass
            
            market_name = self.market_names.get(market_key, market_key)
            self.logger.info(f"{market_name} 패널 로드 완료")
            return True
        except TimeoutException:
            self.logger.error(f"마켓 패널 로드 시간 초과: {market_key}")
            return False
        except Exception as e:
            self.logger.error(f"마켓 패널 로드 대기 중 오류 발생: {e}")
            return False
    
    # ==================== 마켓 설정 버튼 관련 메서드 ====================
    
    def get_api_disconnect_button_selector(self):
        """API 연결 끊기 버튼 선택자를 반환합니다."""
        # 탭 화면의 API 연결 끊기 버튼은 ant-btn-default 클래스를 가짐
        return "//button[contains(@class, 'ant-btn-default')]//span[text()='API 연결 끊기']"
    
    def get_account_setting_button_selector(self):
        """업로드할 계정 설정하기 버튼 선택자를 반환합니다."""
        return '//button[contains(@class, "ant-btn-primary") and contains(@class, "ant-btn-background-ghost")]//span[contains(text(), "업로드할 계정 설정하기")]'
    
    def get_api_validation_button_selector(self):
        """API 검증 버튼 선택자를 반환합니다."""
        # 활성화된 탭 패널 내의 ant-row 컨테이너에서 API 검증 버튼 찾기
        return '//div[contains(@class, "ant-tabs-tabpane-active")]//div[contains(@class, "ant-row")]//button[contains(@class, "ant-btn-primary") and .//span[text()="API 검증"]]'
    
    def get_market_buttons_container_selector(self):
        """마켓 설정 버튼들의 컨테이너 선택자를 반환합니다."""
        return '.ant-row.css-1li46mu[style*="margin: 0px 0px 0px auto"]'
    
    def click_api_disconnect_button(self):
        """API 연결 끊기 버튼을 클릭합니다."""
        try:
            # 현재 활성화된 마켓 탭 패널 내에서만 버튼 찾기
            current_market = self.get_current_active_market()
            if not current_market:
                self.logger.error("현재 활성화된 마켓을 확인할 수 없음")
                return False
            
            # 현재 마켓의 키를 찾기
            current_market_key = None
            for key, name in self.market_names.items():
                if name == current_market:
                    current_market_key = key
                    break
            
            # 가장 정확하고 성공률이 높은 선택자만 사용 (쿠팡에서 검증됨)
            selectors = []
            
            # 현재 마켓의 패널 ID를 사용한 선택자 (가장 정확함)
            if current_market_key:
                try:
                    panel_selector = self.get_market_panel_selector(current_market_key)
                    panel_id = panel_selector.split('"')[1]  # div[id="rc-tabs-0-panel-xxx"]에서 ID 추출
                    selectors.append(f"//div[@id='{panel_id}']//button[contains(@class, 'ant-btn-default')]//span[text()='API 연결 끊기']")
                except:
                    pass
            
            # 전역 정확한 클래스 조합 (패널 ID가 없을 때 사용)
            selectors.append("//button[contains(@class, 'ant-btn-default')]//span[text()='API 연결 끊기']")
            
            # 활성 패널 기반 (추가 안전장치)
            selectors.append("//div[contains(@class, 'ant-tabs-tabpane-active')]//button[contains(@class, 'ant-btn-default')]//span[text()='API 연결 끊기']")
            
            for i, selector in enumerate(selectors):
                try:
                    self.logger.info(f"API 연결 끊기 버튼 찾기 시도 {i+1}/{len(selectors)}")
                    self.logger.debug(f"사용 중인 선택자: {selector}")
                    element = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    element.click()
                    self.logger.info("API 연결 끊기 버튼 클릭 완료")
                    time.sleep(1)
                    return True
                except TimeoutException:
                    self.logger.warning(f"선택자 {i+1} 실패, 다음 선택자 시도")
                    continue
                except Exception as e:
                    self.logger.warning(f"선택자 {i+1} 오류: {e}, 다음 선택자 시도")
                    continue
            
            self.logger.error("모든 선택자로 API 연결 끊기 버튼을 찾을 수 없음")
            return False
            
        except Exception as e:
            self.logger.error(f"API 연결 끊기 버튼 클릭 중 전체 오류: {e}")
            return False
    
    def click_account_setting_button(self):
        """업로드할 계정 설정하기 버튼을 클릭합니다."""
        try:
            selector = self.get_account_setting_button_selector()
            element = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
            element.click()
            self.logger.info("업로드할 계정 설정하기 버튼 클릭 완료")
            time.sleep(1)
            return True
        except TimeoutException:
            self.logger.error("업로드할 계정 설정하기 버튼을 찾을 수 없음")
            return False
        except Exception as e:
            self.logger.error(f"업로드할 계정 설정하기 버튼 클릭 중 오류 발생: {e}")
            return False
    
    def click_api_validation_button(self):
        """API 검증 버튼을 클릭합니다."""
        try:
            xpath = self.get_api_validation_button_selector()
            self.logger.info(f"API 검증 버튼 찾기 시도 - XPath: {xpath}")
            
            # 탭 활성화 상태 확인 코드 제거 (사용자 요청)
            
            # API 검증 버튼 찾기
            element = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            
            # 포커스 이동 및 스크롤
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            time.sleep(0.5)
            
            # 포커스 설정
            self.driver.execute_script("arguments[0].focus();", element)
            time.sleep(0.5)
            
            element.click()
            self.logger.info("API 검증 버튼 클릭 완료")
            time.sleep(2)  # 모달창 로딩 대기 시간 증가
            return True
        except TimeoutException:
            self.logger.error("API 검증 버튼을 찾을 수 없음")
            # 현재 페이지의 모든 버튼 요소 확인
            try:
                buttons = self.driver.find_elements(By.XPATH, "//button[contains(@class, 'ant-btn')]")
                self.logger.info(f"페이지에서 발견된 ant-btn 버튼 수: {len(buttons)}")
                for i, btn in enumerate(buttons[:5]):  # 처음 5개만 로깅
                    try:
                        btn_text = btn.text.strip()
                        btn_class = btn.get_attribute('class')
                        self.logger.info(f"버튼 {i+1}: 텍스트='{btn_text}', 클래스='{btn_class}'")
                    except Exception:
                        pass
            except Exception as debug_e:
                self.logger.error(f"디버깅 정보 수집 중 오류: {debug_e}")
            return False
        except Exception as e:
            self.logger.error(f"API 검증 버튼 클릭 중 오류 발생: {e}")
            return False
    
    # ==================== 마켓별 API KEY 입력 메서드 ====================
    
    def get_api_key_input_selector(self, market_key):
        """마켓별 API KEY 입력창 선택자를 반환합니다."""
        if market_key not in self.market_tabs:
            raise ValueError(f"지원하지 않는 마켓 키: {market_key}")
        
        node_key = self.market_tabs[market_key]
        # 특정 마켓 패널 내부의 API KEY 입력창
        return f'div[id="rc-tabs-0-panel-{node_key}"] input[placeholder="미설정"]'
    
    def input_api_key(self, market_key, api_key):
        """특정 마켓의 API KEY를 입력합니다."""
        try:
            market_name = self.market_names.get(market_key, market_key)
            self.logger.info(f"{market_name} API KEY 입력 시작")
            
            # API KEY 입력창 찾기
            selector = self.get_api_key_input_selector(market_key)
            
            try:
                element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                
                # 요소가 보이는지 확인
                if not element.is_displayed():
                    self.logger.error(f"{market_name} API KEY 입력창이 보이지 않음")
                    return False
                
                # 요소가 활성화되어 있는지 확인
                if not element.is_enabled():
                    self.logger.error(f"{market_name} API KEY 입력창이 비활성화됨")
                    return False
                
                # API KEY 입력
                element.clear()
                element.send_keys(api_key)
                
                self.logger.info(f"{market_name} API KEY 입력 완료: {api_key[:10]}...")
                
                # 포커스를 다른 곳으로 이동 (Enter 키 또는 Tab 키)
                element.send_keys(Keys.TAB)
                self.logger.info(f"{market_name} API KEY 입력 후 포커스 이동 (TAB 키 전송)")
                time.sleep(0.5)
                
                # 입력 확인을 위한 짧은 대기
                time.sleep(1)
                return True
                
            except TimeoutException:
                self.logger.error(f"{market_name} API KEY 입력창을 찾을 수 없음")
                return False
                
        except Exception as e:
            market_name = self.market_names.get(market_key, market_key)
            self.logger.error(f"{market_name} API KEY 입력 중 오류 발생: {e}")
            return False
    
    def input_11st_general_api_key(self, api_key):
        """11번가-일반 API KEY를 입력합니다."""
        return self.input_api_key('11st_general', api_key)
    
    def input_11st_global_api_key(self, api_key):
        """11번가-글로벌 API KEY를 입력합니다."""
        return self.input_api_key('11st_global', api_key)
    
    def input_coupang_api_key(self, api_key):
        """쿠팡 API KEY를 입력합니다."""
        return self.input_api_key('coupang', api_key)
    
    def input_smartstore_api_key(self, api_key):
        """스마트스토어 API KEY를 입력합니다."""
        return self.input_api_key('smartstore', api_key)
    
    def input_auction_gmarket_api_key(self, api_key):
        """옥션/G마켓 API KEY를 입력합니다."""
        return self.input_api_key('auction_gmarket', api_key)
    
    def input_auction_gmarket_api_keys(self, auction_api_key, gmarket_api_key):
        """옥션/G마켓 두 개의 API KEY를 입력합니다.
        
        Args:
            auction_api_key (str): 옥션 API 키 (첫 번째 입력창)
            gmarket_api_key (str): G마켓 API 키 (두 번째 입력창)
            
        Returns:
            bool: 입력 성공 여부
        """
        try:
            self.logger.info("옥션/G마켓 API 키 입력 시작")
            
            # 옥션/G마켓 탭으로 전환
            if not self.switch_to_market('auction_gmarket'):
                return False
            
            # 패널 로드 대기
            if not self.wait_for_market_panel_load('auction_gmarket'):
                return False
            
            # 첫 번째 입력창 (옥션 ID) 찾기 및 입력
            try:
                # XPath를 사용하여 '옥션 ID' 텍스트 다음의 입력창 찾기
                auction_input_xpath = "//div[contains(text(), '옥션 ID')]/following-sibling::input[@placeholder='미설정'] | //div[contains(text(), '옥션 ID')]/..//input[@placeholder='미설정']"
                auction_input = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, auction_input_xpath))
                )
                auction_input.clear()
                auction_input.send_keys(auction_api_key)
                self.logger.info("옥션 API 키 입력 완료")
            except TimeoutException:
                # 대체 선택자 시도 - 순서대로 입력창 찾기
                try:
                    auction_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[placeholder='미설정']")
                    if len(auction_inputs) >= 2:
                        auction_inputs[0].clear()
                        auction_inputs[0].send_keys(auction_api_key)
                        self.logger.info("옥션 API 키 입력 완료 (대체 선택자)")
                    else:
                        self.logger.error("옥션 API 키 입력창을 찾을 수 없습니다")
                        return False
                except Exception as e:
                    self.logger.error(f"옥션 API 키 입력 중 오류: {e}")
                    return False
            
            # 두 번째 입력창 (G마켓 ID) 찾기 및 입력
            try:
                # XPath를 사용하여 'G마켓 ID' 텍스트 다음의 입력창 찾기
                gmarket_input_xpath = "//div[contains(text(), 'G마켓 ID')]/following-sibling::input[@placeholder='미설정'] | //div[contains(text(), 'G마켓 ID')]/..//input[@placeholder='미설정']"
                gmarket_input = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, gmarket_input_xpath))
                )
                gmarket_input.clear()
                gmarket_input.send_keys(gmarket_api_key)
                self.logger.info("G마켓 API 키 입력 완료")
            except TimeoutException:
                # 대체 선택자 시도 - 순서대로 입력창 찾기
                try:
                    gmarket_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[placeholder='미설정']")
                    if len(gmarket_inputs) >= 2:
                        gmarket_inputs[1].clear()
                        gmarket_inputs[1].send_keys(gmarket_api_key)
                        self.logger.info("G마켓 API 키 입력 완료 (대체 선택자)")
                    else:
                        self.logger.error("G마켓 API 키 입력창을 찾을 수 없습니다")
                        return False
                except Exception as e:
                    self.logger.error(f"G마켓 API 키 입력 중 오류: {e}")
                    return False
            
            self.logger.info("옥션/G마켓 API 키 입력 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"옥션/G마켓 API 키 입력 중 오류 발생: {e}")
            return False
    
    def input_lotteon_api_key(self, api_key):
        """롯데온 API KEY를 입력합니다."""
        return self.input_api_key('lotteon', api_key)
    
    def input_kakao_api_key(self, api_key):
        """톡스토어 API KEY를 입력합니다."""
        return self.input_api_key('kakao', api_key)
    
    def input_interpark_api_key(self, api_key):
        """인터파크 API KEY를 입력합니다."""
        return self.input_api_key('interpark', api_key)
    
    def input_wemakeprice_api_key(self, api_key):
        """위메프 API KEY를 입력합니다."""
        return self.input_api_key('wemakeprice', api_key)
    
    def click_button_by_text(self, button_text):
        """버튼 텍스트로 버튼을 클릭합니다."""
        try:
            # JavaScript를 사용하여 텍스트로 버튼 찾기
            script = f"""
            var buttons = document.querySelectorAll('.ant-btn span');
            for (var i = 0; i < buttons.length; i++) {{
                if (buttons[i].textContent.trim() === '{button_text}') {{
                    buttons[i].parentElement.click();
                    return true;
                }}
            }}
            return false;
            """
            
            result = self.driver.execute_script(script)
            if result:
                self.logger.info(f"{button_text} 버튼 클릭 완료")
                time.sleep(1)
                return True
            else:
                self.logger.error(f"버튼을 찾을 수 없음: {button_text}")
                return False
                
        except Exception as e:
            self.logger.error(f"버튼 클릭 중 오류 발생: {e}")
            return False
    
    def is_button_visible(self, button_text):
        """특정 버튼이 화면에 표시되는지 확인합니다."""
        try:
            script = f"""
            var buttons = document.querySelectorAll('.ant-btn span');
            for (var i = 0; i < buttons.length; i++) {{
                if (buttons[i].textContent.trim() === '{button_text}') {{
                    var rect = buttons[i].getBoundingClientRect();
                    return rect.width > 0 && rect.height > 0;
                }}
            }}
            return false;
            """
            
            return self.driver.execute_script(script)
        except Exception as e:
            self.logger.error(f"버튼 가시성 확인 중 오류 발생: {e}")
            return False
    
    def get_available_buttons(self):
        """현재 화면에서 사용 가능한 모든 버튼 텍스트를 반환합니다."""
        try:
            script = """
            var buttons = document.querySelectorAll('.ant-btn span');
            var buttonTexts = [];
            for (var i = 0; i < buttons.length; i++) {
                var text = buttons[i].textContent.trim();
                if (text && text.length > 0) {
                    buttonTexts.push(text);
                }
            }
            return buttonTexts;
            """
            
            return self.driver.execute_script(script)
        except Exception as e:
            self.logger.error(f"버튼 목록 조회 중 오류 발생: {e}")
            return []
    
    # 불필요한 perform_market_setup_workflow 메서드 제거됨
    # 다음 개별 메서드들을 직접 사용하세요:
    # - API 검증: switch_to_market() + wait_for_market_panel_load() + click_api_validation_button()
    # - API 연결 끊기: disconnect_[market]_api() 메서드 사용
    # - 계정 설정: switch_to_market() + wait_for_market_panel_load() + click_account_setting_button()
    
    # ==================== API 연결 끊기 모달창 관련 메서드 ====================
    
    def get_api_disconnect_modal_selector(self):
        """API 연결 끊기 모달창 선택자를 반환합니다."""
        return "//div[@class='ant-modal-content']//div[@class='ant-modal-title' and text()='API 연결 끊기']"
    
    def get_api_disconnect_modal_close_button_selector(self):
        """API 연결 끊기 모달창 닫기(X) 버튼 선택자를 반환합니다."""
        return "//div[@class='ant-modal-content']//button[@class='ant-modal-close']"
    
    def get_api_disconnect_modal_cancel_button_selector(self):
        """API 연결 끊기 모달창 취소 버튼 선택자를 반환합니다."""
        return "//div[@class='ant-modal-footer']//button[contains(@class, 'ant-btn-default')]//span[text()='취소']"
    
    def get_api_disconnect_modal_confirm_button_selector(self):
        """API 연결 끊기 모달창 확인 버튼 선택자를 반환합니다."""
        # 모달창의 확인 버튼은 ant-btn-primary ant-btn-dangerous 클래스를 가짐
        return "//button[contains(@class, 'ant-btn-primary') and contains(@class, 'ant-btn-dangerous')]//span[text()='API 연결 끊기']"
    
    def get_api_disconnect_modal_error_alert_selector(self):
        """API 연결 끊기 모달창 에러 알림 선택자를 반환합니다."""
        return "//div[@class='ant-modal-body']//div[contains(@class, 'ant-alert-error')]//div[@class='ant-alert-message']"
    
    def get_api_disconnect_modal_warning_alert_selector(self):
        """API 연결 끊기 모달창 경고 알림 선택자를 반환합니다."""
        return "//div[@class='ant-modal-body']//div[contains(@class, 'ant-alert-warning')]//div[@class='ant-alert-message']"
    
    def wait_for_api_disconnect_modal(self, timeout=10):
        """API 연결 끊기 모달창이 나타날 때까지 대기합니다."""
        try:
            modal_selector = self.get_api_disconnect_modal_selector()
            # 1. 모달창 존재 확인
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, modal_selector))
            )
            
            # 2. 모달창이 완전히 표시될 때까지 대기
            WebDriverWait(self.driver, 3).until(
                EC.visibility_of_element_located((By.XPATH, modal_selector))
            )
            
            # 3. 모달창 내용 로드를 위한 추가 대기
            time.sleep(1)
            
            # 4. 확인 버튼이 클릭 가능할 때까지 대기 (간소화된 선택자)
            confirm_selectors = [
                "//button[contains(@class, 'ant-btn-primary') and contains(@class, 'ant-btn-dangerous')]//span[text()='API 연결 끊기']",
                "//button[contains(@class, 'ant-btn-dangerous')]//span[text()='API 연결 끊기']",
                "//button//span[text()='API 연결 끊기']"
            ]
            
            for selector in confirm_selectors:
                try:
                    WebDriverWait(self.driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except TimeoutException:
                    continue
            
            self.logger.info("API 연결 끊기 모달창 확인")
            return True
        except TimeoutException:
            self.logger.error("API 연결 끊기 모달창 대기 시간 초과")
            return False
        except Exception as e:
            self.logger.error(f"API 연결 끊기 모달창 대기 중 오류 발생: {e}")
            return False
    
    def debug_api_disconnect_modal(self):
        """API 연결 끊기 모달창의 구조를 디버깅합니다."""
        try:
            self.logger.info("=== API 연결 끊기 모달창 디버깅 시작 ===")
            
            # 모달창 찾기
            modals = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'ant-modal')]")
            self.logger.info(f"발견된 모달창 개수: {len(modals)}")
            
            for i, modal in enumerate(modals):
                if modal.is_displayed():
                    self.logger.info(f"모달창 {i+1} 표시됨")
                    
                    # 모달창 내 모든 버튼 찾기
                    modal_buttons = modal.find_elements(By.TAG_NAME, "button")
                    self.logger.info(f"모달창 {i+1} 내 버튼 개수: {len(modal_buttons)}")
                    
                    for j, button in enumerate(modal_buttons):
                        try:
                            text = button.text.strip()
                            classes = button.get_attribute("class")
                            is_displayed = button.is_displayed()
                            is_enabled = button.is_enabled()
                            self.logger.info(f"모달창 버튼 {j+1}: 텍스트='{text}', 표시={is_displayed}, 활성={is_enabled}, 클래스='{classes}'")
                        except Exception as btn_e:
                            self.logger.warning(f"모달창 버튼 {j+1} 정보 수집 실패: {btn_e}")
                    
                    # 모달창 HTML 구조 일부 출력
                    modal_html = modal.get_attribute('outerHTML')[:1000]
                    self.logger.info(f"모달창 {i+1} HTML 일부: {modal_html}")
            
            self.logger.info("=== API 연결 끊기 모달창 디버깅 완료 ===")
            
        except Exception as e:
            self.logger.error(f"API 연결 끊기 모달창 디버깅 중 오류 발생: {e}")
    
    def click_api_disconnect_modal_confirm(self):
        """API 연결 끊기 모달창에서 확인 버튼을 클릭합니다."""
        try:
            # 가장 정확하고 성공률이 높은 선택자만 사용 (쿠팡에서 검증됨)
            selectors = [
                # 1순위: 정확한 클래스 조합 (ant-btn-primary + ant-btn-dangerous)
                "//button[contains(@class, 'ant-btn-primary') and contains(@class, 'ant-btn-dangerous')]//span[text()='API 연결 끊기']",
                
                # 2순위: 개별 클래스 기반 (안전장치)
                "//button[contains(@class, 'ant-btn-dangerous')]//span[text()='API 연결 끊기']",
                
                # 3순위: 전역 텍스트 기반 (최후 수단)
                "//button//span[text()='API 연결 끊기']"
            ]
            
            for i, selector in enumerate(selectors):
                try:
                    self.logger.info(f"모달창 확인 버튼 찾기 시도 {i+1}/{len(selectors)}")
                    # 각 선택자에 대해 짧은 대기 시간 사용
                    element = WebDriverWait(self.driver, 1).until(EC.element_to_be_clickable((By.XPATH, selector)))
                    element.click()
                    self.logger.info("API 연결 끊기 모달창 확인 버튼 클릭 완료")
                    time.sleep(1)
                    return True
                except TimeoutException:
                    self.logger.warning(f"모달창 확인 버튼 선택자 {i+1} 실패, 다음 선택자 시도")
                    continue
                except Exception as e:
                    self.logger.warning(f"모달창 확인 버튼 선택자 {i+1} 오류: {e}, 다음 선택자 시도")
                    continue
            
            # 모든 선택자 실패 시 디버깅 수행
            self.logger.error("모든 선택자로 API 연결 끊기 모달창 확인 버튼을 찾을 수 없음")
            self.debug_api_disconnect_modal()
            return False
            
        except Exception as e:
            self.logger.error(f"API 연결 끊기 모달창 확인 버튼 클릭 중 전체 오류: {e}")
            return False
    
    def click_api_disconnect_modal_cancel(self):
        """API 연결 끊기 모달창에서 취소 버튼을 클릭합니다."""
        try:
            selector = self.get_api_disconnect_modal_cancel_button_selector()
            element = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
            element.click()
            self.logger.info("API 연결 끊기 모달창 취소 버튼 클릭 완료")
            time.sleep(1)
            return True
        except TimeoutException:
            self.logger.error("API 연결 끊기 모달창 취소 버튼을 찾을 수 없음")
            return False
        except Exception as e:
            self.logger.error(f"API 연결 끊기 모달창 취소 버튼 클릭 중 오류 발생: {e}")
            return False
    
    def close_api_disconnect_modal(self):
        """API 연결 끊기 모달창을 닫습니다 (X 버튼 클릭)."""
        try:
            selector = self.get_api_disconnect_modal_close_button_selector()
            element = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
            element.click()
            self.logger.info("API 연결 끊기 모달창 닫기 버튼 클릭 완료")
            time.sleep(1)
            return True
        except TimeoutException:
            self.logger.error("API 연결 끊기 모달창 닫기 버튼을 찾을 수 없음")
            return False
        except Exception as e:
            self.logger.error(f"API 연결 끊기 모달창 닫기 버튼 클릭 중 오류 발생: {e}")
            return False
    
    def get_api_disconnect_modal_alert_messages(self):
        """API 연결 끊기 모달창의 알림 메시지들을 반환합니다."""
        try:
            messages = {}
            
            # 에러 알림 메시지
            try:
                error_element = self.driver.find_element(By.XPATH, self.get_api_disconnect_modal_error_alert_selector())
                messages['error'] = error_element.text.strip()
            except NoSuchElementException:
                messages['error'] = None
            
            # 경고 알림 메시지
            try:
                warning_element = self.driver.find_element(By.XPATH, self.get_api_disconnect_modal_warning_alert_selector())
                messages['warning'] = warning_element.text.strip()
            except NoSuchElementException:
                messages['warning'] = None
            
            return messages
        except Exception as e:
            self.logger.error(f"API 연결 끊기 모달창 알림 메시지 조회 중 오류 발생: {e}")
            return {'error': None, 'warning': None}
    
    def handle_api_disconnect_modal(self, confirm=True):
        """API 연결 끊기 모달창을 처리합니다.
        
        Args:
            confirm (bool): True면 확인, False면 취소
        """
        try:
            # 1. 모달창 대기
            if not self.wait_for_api_disconnect_modal():
                return False
            
            # 2. 알림 메시지 확인 (로깅용)
            messages = self.get_api_disconnect_modal_alert_messages()
            if messages['error']:
                self.logger.info(f"에러 알림: {messages['error']}")
            if messages['warning']:
                self.logger.info(f"경고 알림: {messages['warning']}")
            
            # 3. 사용자 선택에 따라 버튼 클릭
            button_clicked = False
            if confirm:
                button_clicked = self.click_api_disconnect_modal_confirm()
            else:
                button_clicked = self.click_api_disconnect_modal_cancel()
            
            # 4. 버튼 클릭이 성공했다면 모달창이 완전히 사라질 때까지 대기
            if button_clicked:
                self.wait_for_modal_to_disappear()
            
            return button_clicked
                
        except Exception as e:
            self.logger.error(f"API 연결 끊기 모달창 처리 중 오류 발생: {e}")
            return False
    
    def wait_for_modal_to_disappear(self, timeout=10):
        """모달창이 완전히 사라질 때까지 대기합니다."""
        try:
            self.logger.info("모달창이 완전히 사라질 때까지 대기 중...")
            
            # 모달창이 사라질 때까지 대기
            WebDriverWait(self.driver, timeout).until(
                EC.invisibility_of_element_located((By.XPATH, "//div[contains(@class, 'ant-modal-wrap')]"))
            )
            
            # 추가 안전 대기 (DOM 정리 시간)
            time.sleep(1)
            
            self.logger.info("모달창이 완전히 사라짐")
            return True
            
        except TimeoutException:
            self.logger.warning(f"모달창 사라짐 대기 시간 초과 ({timeout}초)")
            # 강제로 모달창 닫기 시도
            try:
                self.driver.execute_script("""
                    var modals = document.querySelectorAll('.ant-modal-wrap');
                    modals.forEach(function(modal) {
                        if (modal.style.display !== 'none') {
                            modal.style.display = 'none';
                        }
                    });
                """)
                self.logger.info("JavaScript로 모달창 강제 제거 완료")
                time.sleep(1)
            except Exception as js_e:
                self.logger.warning(f"JavaScript 모달창 제거 실패: {js_e}")
            return False
            
        except Exception as e:
            self.logger.error(f"모달창 사라짐 대기 중 오류 발생: {e}")
            return False
    
    def debug_current_panel_buttons(self):
        """현재 패널의 모든 버튼과 API 관련 요소를 디버깅합니다."""
        try:
            self.logger.info("=== 현재 패널 디버깅 시작 ===")
            
            # 현재 활성 마켓 확인
            current_market = self.get_current_active_market()
            self.logger.info(f"현재 활성 마켓: {current_market}")
            
            # 활성 탭 패널 확인
            try:
                active_panels = self.driver.find_elements(By.CSS_SELECTOR, "div[class*='ant-tabs-tabpane-active']")
                self.logger.info(f"활성 패널 개수: {len(active_panels)}")
                
                if active_panels:
                    active_panel = active_panels[0]
                    panel_html = active_panel.get_attribute('outerHTML')[:500]  # 처음 500자만
                    self.logger.info(f"활성 패널 HTML 일부: {panel_html}")
                    
                    # 활성 패널 내의 모든 버튼 찾기
                    panel_buttons = active_panel.find_elements(By.TAG_NAME, "button")
                    self.logger.info(f"활성 패널 내 버튼 개수: {len(panel_buttons)}")
                    
                    for i, button in enumerate(panel_buttons):
                        try:
                            text = button.text.strip()
                            classes = button.get_attribute("class")
                            is_displayed = button.is_displayed()
                            is_enabled = button.is_enabled()
                            self.logger.info(f"패널 버튼 {i+1}: 텍스트='{text}', 표시={is_displayed}, 활성={is_enabled}, 클래스='{classes}'")
                        except Exception as btn_e:
                            self.logger.warning(f"버튼 {i+1} 정보 수집 실패: {btn_e}")
                    
                    # 활성 패널 내 API 관련 요소 찾기
                    api_elements = active_panel.find_elements(By.XPATH, ".//*[contains(text(), 'API')]")
                    self.logger.info(f"활성 패널 내 API 관련 요소 개수: {len(api_elements)}")
                    
                    for i, element in enumerate(api_elements):
                        try:
                            text = element.text.strip()
                            tag = element.tag_name
                            self.logger.info(f"패널 API 요소 {i+1}: 태그={tag}, 텍스트='{text}'")
                        except:
                            pass
                            
            except Exception as panel_e:
                self.logger.error(f"활성 패널 분석 실패: {panel_e}")
            
            # 전체 페이지에서 버튼 찾기 (백업)
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            self.logger.info(f"전체 페이지 버튼 개수: {len(buttons)}")
            
            api_disconnect_buttons = []
            for button in buttons:
                try:
                    text = button.text.strip()
                    if "API" in text and "연결" in text:
                        api_disconnect_buttons.append(button)
                        is_displayed = button.is_displayed()
                        is_enabled = button.is_enabled()
                        classes = button.get_attribute("class")
                        self.logger.info(f"API 연결 관련 버튼 발견: 텍스트='{text}', 표시={is_displayed}, 활성={is_enabled}, 클래스='{classes}'")
                except:
                    pass
            
            self.logger.info(f"API 연결 관련 버튼 총 개수: {len(api_disconnect_buttons)}")
            self.logger.info("=== 현재 패널 디버깅 완료 ===")
            
        except Exception as e:
            self.logger.error(f"패널 디버깅 중 오류: {e}")
    
    # 불필요한 perform_complete_api_disconnect_workflow 메서드 제거됨
    # 각 마켓별 개별 메서드(disconnect_coupang_api, disconnect_smartstore_api, disconnect_auction_gmarket_api)를 직접 사용하세요
    
    # ==================== 11번가 API 검증 모달창 관련 메서드 ====================
    
    def get_11st_api_verification_modal_selector(self):
        """11번가 API 검증 모달창(드로어) 선택자를 반환합니다."""
        return '.ant-drawer-content-wrapper'
    
    def get_11st_shipping_profile_create_button_selector(self):
        """11번가 배송프로필 만들기 버튼 선택자를 반환합니다."""
        return '.ant-drawer-extra button.ant-btn.ant-btn-primary'
    
    def get_11st_delivery_company_dropdown_selector(self):
        """11번가 출고 택배사 드롭다운 선택자를 반환합니다."""
        return '.ant-drawer-body .ant-select .ant-select-selector'
    
    def get_11st_delivery_company_dropdown_arrow_selector(self):
        """11번가 출고 택배사 드롭다운 화살표 선택자를 반환합니다."""
        return '.ant-drawer-body .ant-select .ant-select-arrow'
    
    def get_11st_lotte_delivery_option_selector(self):
        """11번가 롯데택배 옵션 선택자를 반환합니다."""
        return '.ant-select-dropdown .ant-select-item-option[title*="롯데"]'
    
    def wait_for_11st_api_verification_modal(self, timeout=10):
        """11번가 API 검증 모달창이 나타날 때까지 대기합니다."""
        try:
            modal_selector = self.get_11st_api_verification_modal_selector()
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, modal_selector))
            )
            self.logger.info("11번가 API 검증 모달창 확인")
            return True
        except TimeoutException:
            self.logger.error("11번가 API 검증 모달창 대기 시간 초과")
            return False
        except Exception as e:
            self.logger.error(f"11번가 API 검증 모달창 대기 중 오류 발생: {e}")
            return False
    
    def select_11st_lotte_delivery_company(self):
        """11번가 출고 택배사에서 롯데택배를 선택합니다."""
        try:
            # 1. 출고 택배사 드롭다운 찾기 (더 구체적인 선택자 사용)
            delivery_company_dropdown = None
            
            # 출고 택배사 라벨 다음의 드롭다운 찾기
            try:
                # 출고 택배사 텍스트가 포함된 요소 찾기
                delivery_labels = self.driver.find_elements(By.XPATH, "//div[contains(text(), '출고 택배사')]")
                if delivery_labels:
                    # 해당 라벨의 부모 또는 다음 형제에서 드롭다운 찾기
                    parent = delivery_labels[0].find_element(By.XPATH, "./following-sibling::div//div[@class='ant-select-selector']")
                    delivery_company_dropdown = parent
                    self.logger.info("출고 택배사 드롭다운을 라벨 기준으로 찾음")
            except:
                # 대안: 모든 드롭다운 중에서 CJ대한통운이 선택된 것 찾기
                dropdowns = self.driver.find_elements(By.CSS_SELECTOR, ".ant-drawer-body .ant-select .ant-select-selector")
                for dropdown in dropdowns:
                    try:
                        selected_text = dropdown.find_element(By.CSS_SELECTOR, ".ant-select-selection-item").get_attribute("title")
                        if "CJ" in selected_text or "택배" in selected_text:
                            delivery_company_dropdown = dropdown
                            self.logger.info(f"출고 택배사 드롭다운을 선택된 값 기준으로 찾음: {selected_text}")
                            break
                    except:
                        continue
            
            if not delivery_company_dropdown:
                self.logger.error("출고 택배사 드롭다운을 찾을 수 없음")
                return False
            
            # 2. 드롭다운 클릭하여 열기
            delivery_company_dropdown.click()
            self.logger.info("출고 택배사 드롭다운 클릭")
            time.sleep(2)
            
            # 3. 롯데택배 옵션 선택
            lotte_option_selector = self.get_11st_lotte_delivery_option_selector()
            lotte_option = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, lotte_option_selector)))
            lotte_option.click()
            self.logger.info("롯데택배 선택 완료")
            time.sleep(1)
            return True
            
        except TimeoutException:
            self.logger.error("롯데택배 선택 중 요소를 찾을 수 없음")
            return False
        except Exception as e:
            self.logger.error(f"롯데택배 선택 중 오류 발생: {e}")
            return False
    
    def click_11st_shipping_profile_create_button(self):
        """11번가 배송프로필 만들기 버튼을 클릭합니다."""
        try:
            selector = self.get_11st_shipping_profile_create_button_selector()
            element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            element.click()
            self.logger.info("11번가 배송프로필 만들기 버튼 클릭 완료")
            time.sleep(2)
            return True
        except TimeoutException:
            self.logger.error("11번가 배송프로필 만들기 버튼을 찾을 수 없음")
            return False
        except Exception as e:
            self.logger.error(f"11번가 배송프로필 만들기 버튼 클릭 중 오류 발생: {e}")
            return False
    
    def handle_11st_api_verification_modal(self):
        """11번가 API 검증 모달창을 처리합니다.
        
        1. 출고 택배사에서 롯데택배 선택
        2. 배송프로필 만들기 버튼 클릭
        """
        try:
            # 1. 모달창 대기
            if not self.wait_for_11st_api_verification_modal():
                return False
            
            # 2. 롯데택배 선택
            if not self.select_11st_lotte_delivery_company():
                return False
            
            # 3. 배송프로필 만들기 버튼 클릭
            if not self.click_11st_shipping_profile_create_button():
                return False

            # 4. 화면 새로고침
            self.logger.info("11번가 배송프로필 만들기 완료 후 화면 새로고침 시작")
            self.driver.refresh()
            time.sleep(3)  # 새로고침 후 페이지 로드 대기
            self.logger.info("화면 새로고침 완료")

            self.logger.info("11번가 API 검증 모달창 처리 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"11번가 API 검증 모달창 처리 중 오류 발생: {e}")
            return False
    
    def perform_complete_11st_api_verification_workflow(self):
        """11번가 API 검증 전체 워크플로우를 수행합니다.
        
        1. API 검증 버튼 클릭
        2. API 검증 모달창 처리
        
        주의: 이 메서드는 이미 11번가-일반 탭이 활성화되고 패널이 로드된 상태에서 호출되어야 합니다.
        """
        try:
            # 1. API 검증 버튼 클릭
            if not self.click_api_validation_button():
                return False
            
            # 2. API 검증 모달창 처리
            return self.handle_11st_api_verification_modal()
            
        except Exception as e:
             self.logger.error(f"11번가 API 검증 전체 워크플로우 중 오류 발생: {e}")
             return False
    
    # ==================== 옥션/G마켓 API 검증 모달창 관련 메서드 ====================
    
    def get_auction_gmarket_api_verification_modal_selector(self):
        """옥션/G마켓 API 검증 모달창(드로어) 선택자를 반환합니다."""
        return '//div[contains(@class, "ant-drawer-title") and contains(text(), "옥션/G마켓 배송 프로필 추가")]'
    
    def get_auction_gmarket_shipping_profile_create_button_selector(self):
        """옥션/G마켓 배송프로필 만들기 버튼 선택자를 반환합니다."""
        return '.ant-drawer-extra button.ant-btn.ant-btn-primary'
    
    def get_auction_gmarket_delivery_company_dropdown_selector(self):
        """옥션/G마켓 택배사 드롭다운 선택자를 반환합니다."""
        return '.ant-drawer-body .ant-select:has(.ant-select-selection-item[title="롯데택배"])'
    
    def get_auction_gmarket_lotte_delivery_option_selector(self):
        """옥션/G마켓 롯데택배 옵션 선택자를 반환합니다."""
        return '.ant-select-dropdown .ant-select-item-option[title="롯데택배"]'
    
    def get_gmarket_site_discount_agree_button_selector(self):
        """G마켓 사이트할인 동의 버튼 선택자를 반환합니다."""
        return '//div[contains(@class, "ant-drawer-body")]//div[contains(@class, "ant-radio-group") and .//div[contains(text(), "G마켓 사이트할인 동의")]]//label[contains(@class, "ant-radio-button-wrapper") and .//span[contains(text(), "동의")]]'
    
    def get_auction_site_discount_agree_button_selector(self):
        """옥션 사이트할인 동의 버튼 선택자를 반환합니다."""
        return '//div[contains(@class, "ant-drawer-body")]//div[contains(@class, "ant-radio-group") and .//div[contains(text(), "옥션 사이트할인 동의")]]//label[contains(@class, "ant-radio-button-wrapper") and .//span[contains(text(), "동의")]]'
    
    def wait_for_auction_gmarket_api_verification_modal(self, timeout=10):
        """옥션/G마켓 API 검증 모달창이 나타날 때까지 대기합니다."""
        try:
            modal_selector = self.get_auction_gmarket_api_verification_modal_selector()
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, modal_selector))
            )
            self.logger.info("옥션/G마켓 API 검증 모달창 확인")
            return True
        except TimeoutException:
            self.logger.error("옥션/G마켓 API 검증 모달창 대기 시간 초과")
            return False
        except Exception as e:
            self.logger.error(f"옥션/G마켓 API 검증 모달창 대기 중 오류 발생: {e}")
            return False
    
    def select_auction_gmarket_lotte_delivery_company(self):
        """옥션/G마켓 택배사에서 롯데택배를 선택합니다."""
        try:
            # 1. 드롭다운 클릭하여 열기
            dropdown_selector = self.get_auction_gmarket_delivery_company_dropdown_selector()
            dropdown_element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, dropdown_selector)))
            dropdown_element.click()
            self.logger.info("택배사 드롭다운 클릭")
            time.sleep(1)
            
            # 2. 롯데택배 옵션 선택
            lotte_option_selector = self.get_auction_gmarket_lotte_delivery_option_selector()
            lotte_option = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, lotte_option_selector)))
            lotte_option.click()
            self.logger.info("롯데택배 선택 완료")
            time.sleep(1)
            return True
            
        except TimeoutException:
            self.logger.error("롯데택배 선택 중 요소를 찾을 수 없음")
            return False
        except Exception as e:
            self.logger.error(f"롯데택배 선택 중 오류 발생: {e}")
            return False
    
    def click_gmarket_site_discount_agree(self):
        """G마켓 사이트할인 동의 버튼을 클릭합니다."""
        try:
            selector = self.get_gmarket_site_discount_agree_button_selector()
            element = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
            element.click()
            self.logger.info("G마켓 사이트할인 동의 버튼 클릭 완료")
            time.sleep(1)
            return True
        except TimeoutException:
            self.logger.error("G마켓 사이트할인 동의 버튼을 찾을 수 없음")
            return False
        except Exception as e:
            self.logger.error(f"G마켓 사이트할인 동의 버튼 클릭 중 오류 발생: {e}")
            return False
    
    def click_auction_site_discount_agree(self):
        """옥션 사이트할인 동의 버튼을 클릭합니다."""
        try:
            selector = self.get_auction_site_discount_agree_button_selector()
            element = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
            element.click()
            self.logger.info("옥션 사이트할인 동의 버튼 클릭 완료")
            time.sleep(1)
            return True
        except TimeoutException:
            self.logger.error("옥션 사이트할인 동의 버튼을 찾을 수 없음")
            return False
        except Exception as e:
            self.logger.error(f"옥션 사이트할인 동의 버튼 클릭 중 오류 발생: {e}")
            return False
    
    def click_auction_gmarket_shipping_profile_create_button(self):
        """옥션/G마켓 배송프로필 만들기 버튼을 클릭합니다."""
        try:
            selector = self.get_auction_gmarket_shipping_profile_create_button_selector()
            element = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
            element.click()
            self.logger.info("옥션/G마켓 배송프로필 만들기 버튼 클릭 완료")
            time.sleep(2)
            return True
        except TimeoutException:
            self.logger.error("옥션/G마켓 배송프로필 만들기 버튼을 찾을 수 없음")
            return False
        except Exception as e:
            self.logger.error(f"옥션/G마켓 배송프로필 만들기 버튼 클릭 중 오류 발생: {e}")
            return False
    
    def close_any_open_modal(self):
        """열려있는 모든 모달창을 닫습니다."""
        try:
            # 일반적인 모달창 닫기 버튼들을 시도
            close_selectors = [
                "//div[contains(@class, 'ant-modal')]//button[contains(@class, 'ant-modal-close')]",
                "//div[contains(@class, 'ant-modal')]//span[contains(@class, 'ant-modal-close-x')]",
                "//div[contains(@class, 'ant-modal')]//button[contains(@aria-label, 'Close')]",
                "//div[contains(@class, 'ant-modal')]//button[contains(., '취소')]",
                "//div[contains(@class, 'ant-modal')]//button[contains(., '닫기')]",
                "//button[contains(@class, 'ant-modal-close')]"
            ]
            
            for selector in close_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            element.click()
                            self.logger.info("열려있는 모달창을 닫았습니다")
                            time.sleep(0.5)
                            return True
                except Exception:
                    continue
            
            # ESC 키로 모달창 닫기 시도
            try:
                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                time.sleep(0.5)
                self.logger.info("ESC 키로 모달창 닫기 시도")
            except Exception:
                pass
                
            return True
            
        except Exception as e:
            self.logger.warning(f"모달창 닫기 중 오류 발생: {e}")
            return True  # 오류가 있어도 계속 진행
    
    def ensure_no_modal_interference(self):
        """탭 클릭 전에 모달창 간섭을 방지합니다."""
        try:
            # 1. 모달창 래퍼가 DOM에 남아있는지 확인
            modal_wrappers = self.driver.find_elements(By.CSS_SELECTOR, ".ant-modal-wrap")
            if modal_wrappers:
                self.logger.info(f"DOM에 {len(modal_wrappers)}개의 모달창 래퍼가 남아있음, 제거 시도")
                
                # 2. JavaScript로 강제 제거
                self.driver.execute_script("""
                    var modals = document.querySelectorAll('.ant-modal-wrap, .ant-modal-mask, .ant-modal');
                    modals.forEach(function(modal) {
                        if (modal.parentNode) {
                            modal.parentNode.removeChild(modal);
                        }
                    });
                """)
                
                # 3. body의 overflow 스타일 복원 (모달창이 설정했을 수 있음)
                self.driver.execute_script("document.body.style.overflow = 'auto';")
                
                # 4. DOM 업데이트 대기
                time.sleep(0.5)
                
                self.logger.info("모달창 DOM 요소 강제 제거 완료")
            
            # 5. 일반적인 모달창 닫기도 시도
            self.close_any_open_modal()
            
        except Exception as e:
            self.logger.warning(f"모달창 간섭 방지 중 오류 발생: {e}")
    
    def handle_auction_gmarket_api_verification_modal(self):
        """옥션/G마켓 API 검증 모달창을 처리합니다.
        
        1. 택배사에서 롯데택배 선택
        2. G마켓 사이트할인 동의
        3. 옥션 사이트할인 동의
        4. 배송프로필 만들기 버튼 클릭
        """
        try:
            # 1. 모달창 대기
            if not self.wait_for_auction_gmarket_api_verification_modal():
                return False
            
            # 2. 롯데택배 선택
            if not self.select_auction_gmarket_lotte_delivery_company():
                return False
            
            # 3. G마켓 사이트할인 동의
            if not self.click_gmarket_site_discount_agree():
                return False
            
            # 4. 옥션 사이트할인 동의
            if not self.click_auction_site_discount_agree():
                return False
            
            # 5. 배송프로필 만들기 버튼 클릭
            if not self.click_auction_gmarket_shipping_profile_create_button():
                return False
            
            self.logger.info("옥션/G마켓 API 검증 모달창 처리 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"옥션/G마켓 API 검증 모달창 처리 중 오류 발생: {e}")
            return False
    
    def disconnect_coupang_api(self):
        """쿠팡 API 연결을 끊습니다."""
        try:
            self.logger.info("coupang API 연결 끊기 시도")
            
            # 1. 쿠팡 탭으로 전환
            if not self.switch_to_market('coupang'):
                return False
            
            # 2. 패널 로드 대기
            if not self.wait_for_market_panel_load('coupang'):
                return False
            
            # 3. API 연결 끊기 버튼 클릭
            if not self.click_api_disconnect_button():
                return False
            
            # 4. 모달창 처리
            return self.handle_api_disconnect_modal(confirm=True)
            
        except Exception as e:
            self.logger.error(f"쿠팡 API 연결 끊기 중 오류 발생: {e}")
            return False
    
    def disconnect_smartstore_api(self):
        """스마트스토어 API 연결을 끊습니다."""
        try:
            self.logger.info("smartstore API 연결 끊기 시도")
            
            # 1. 스마트스토어 탭으로 전환
            if not self.switch_to_market('smartstore'):
                return False
            
            # 2. 패널 로드 대기
            if not self.wait_for_market_panel_load('smartstore'):
                return False
            
            # 3. API 연결 끊기 버튼 클릭
            if not self.click_api_disconnect_button():
                return False
            
            # 4. 모달창 처리
            return self.handle_api_disconnect_modal(confirm=True)
            
        except Exception as e:
            self.logger.error(f"스마트스토어 API 연결 끊기 중 오류 발생: {e}")
            return False
    
    def disconnect_auction_gmarket_api(self):
        """옥션/G마켓 API 연결을 끊습니다."""
        try:
            self.logger.info("auction_gmarket API 연결 끊기 시도")
            
            # 1. 옥션/G마켓 탭으로 전환
            if not self.switch_to_market('auction_gmarket'):
                return False
            
            # 2. 패널 로드 대기
            if not self.wait_for_market_panel_load('auction_gmarket'):
                return False
            
            # 3. API 연결 끊기 버튼 클릭
            if not self.click_api_disconnect_button():
                return False
            
            # 4. 모달창 처리
            return self.handle_api_disconnect_modal(confirm=True)
            
        except Exception as e:
            self.logger.error(f"옥션/G마켓 API 연결 끊기 중 오류 발생: {e}")
            return False
    
    def disconnect_11st_general_api(self):
        """11번가-일반 API 연결을 끊습니다."""
        try:
            self.logger.info("11st_general API 연결 끊기 시도")
            
            # 1. 11번가-일반 탭으로 전환
            if not self.switch_to_market('11st_general'):
                return False
            
            # 2. 패널 로드 대기
            if not self.wait_for_market_panel_load('11st_general'):
                return False
            
            # 3. API 연결 끊기 버튼 클릭
            if not self.click_api_disconnect_button():
                return False
            
            # 4. 모달창 처리
            return self.handle_api_disconnect_modal(confirm=True)
            
        except Exception as e:
            self.logger.error(f"11번가-일반 API 연결 끊기 중 오류 발생: {e}")
            return False
    
    def disconnect_11st_global_api(self):
        """11번가-글로벌 API 연결을 끊습니다."""
        try:
            self.logger.info("11st_global API 연결 끊기 시도")
            
            # 1. 11번가-글로벌 탭으로 전환
            if not self.switch_to_market('11st_global'):
                return False
            
            # 2. 패널 로드 대기
            if not self.wait_for_market_panel_load('11st_global'):
                return False
            
            # 3. API 연결 끊기 버튼 클릭
            if not self.click_api_disconnect_button():
                return False
            
            # 4. 모달창 처리
            return self.handle_api_disconnect_modal(confirm=True)
            
        except Exception as e:
            self.logger.error(f"11번가-글로벌 API 연결 끊기 중 오류 발생: {e}")
            return False
    
    def disconnect_lotteon_api(self):
        """롯데온 API 연결을 끊습니다."""
        try:
            self.logger.info("lotteon API 연결 끊기 시도")
            
            # 1. 롯데온 탭으로 전환
            if not self.switch_to_market('lotteon'):
                return False
            
            # 2. 패널 로드 대기
            if not self.wait_for_market_panel_load('lotteon'):
                return False
            
            # 3. API 연결 끊기 버튼 클릭
            if not self.click_api_disconnect_button():
                return False
            
            # 4. 모달창 처리
            return self.handle_api_disconnect_modal(confirm=True)
            
        except Exception as e:
            self.logger.error(f"롯데온 API 연결 끊기 중 오류 발생: {e}")
            return False
    
    def disconnect_kakao_api(self):
        """톡스토어 API 연결을 끊습니다."""
        try:
            self.logger.info("kakao API 연결 끊기 시도")
            
            # 1. 톡스토어 탭으로 전환
            if not self.switch_to_market('kakao'):
                return False
            
            # 2. 패널 로드 대기
            if not self.wait_for_market_panel_load('kakao'):
                return False
            
            # 3. API 연결 끊기 버튼 클릭
            if not self.click_api_disconnect_button():
                return False
            
            # 4. 모달창 처리
            return self.handle_api_disconnect_modal(confirm=True)
            
        except Exception as e:
            self.logger.error(f"톡스토어 API 연결 끊기 중 오류 발생: {e}")
            return False
    
    def perform_complete_auction_gmarket_api_verification_workflow(self, market_key):
        """옥션/G마켓 API 검증 전체 워크플로우를 수행합니다.
        
        Args:
            market_key (str): 'auction' 또는 'gmarket'
        """
        try:
            # 1. 해당 마켓 탭으로 전환
            if not self.switch_to_market(market_key):
                return False
            
            # 2. 패널 로드 대기
            if not self.wait_for_market_panel_load(market_key):
                return False
            
            # 3. API 검증 버튼 클릭
            if not self.click_api_validation_button():
                return False
            
            # 4. API 검증 모달창 처리
            return self.handle_auction_gmarket_api_verification_modal()
            
        except Exception as e:
            self.logger.error(f"옥션/G마켓 API 검증 전체 워크플로우 중 오류 발생: {e}")
            return False
    
    def handle_auction_gmarket_api_verification_modal(self):
        """옥션/G마켓 API 검증 모달창을 처리합니다.
        
        처리 항목:
        1. 택배사를 대한통운에서 롯데택배(5번째)로 변경
        2. G마켓 사이트할인 동의를 '동의'로 변경
        3. 옥션 사이트할인 동의를 '동의'로 변경
        4. 배송프로필 만들기 버튼 클릭
        
        Returns:
            bool: 처리 성공 여부
        """
        try:
            self.logger.info("옥션/G마켓 API 검증 모달창 처리 시작")
            
            # 모달창이 열릴 때까지 대기
            modal_selector = ".ant-drawer-content-wrapper"
            try:
                self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, modal_selector))
                )
                self.logger.info("옥션/G마켓 배송 프로필 모달창 감지됨")
                time.sleep(2)  # 모달창 완전 로드 대기
            except TimeoutException:
                self.logger.error("옥션/G마켓 배송 프로필 모달창을 찾을 수 없습니다")
                return False
            
            # 1. 택배사 변경 (대한통운 -> 롯데택배)
            if not self._change_auction_gmarket_delivery_company():
                return False
            
            # 2. G마켓 사이트할인 동의 변경
            if not self._change_gmarket_site_discount_agreement():
                return False
            
            # 3. 옥션 사이트할인 동의 변경
            if not self._change_auction_site_discount_agreement():
                return False
            
            # 4. 배송프로필 만들기 버튼 클릭
            if not self._click_auction_gmarket_shipping_profile_create_button():
                return False
            
            # 5. 화면 새로고침
            self.logger.info("옥션/G마켓 배송 프로필 만들기 완료 후 화면 새로고침 시작")
            self.driver.refresh()
            time.sleep(3)  # 새로고침 후 페이지 로드 대기
            self.logger.info("옥션/G마켓 화면 새로고침 완료")
            
            self.logger.info("옥션/G마켓 API 검증 모달창 처리 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"옥션/G마켓 API 검증 모달창 처리 중 오류 발생: {e}")
            return False
    
    def _change_auction_gmarket_delivery_company(self):
        """옥션/G마켓 택배사를 대한통운에서 롯데택배로 변경합니다."""
        try:
            self.logger.info("택배사 변경 시작 (대한통운 -> 롯데택배)")
            
            # 택배사 드롭다운 클릭
            try:
                # XPath를 사용하여 택배사 드롭다운 찾기
                delivery_dropdown = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), '택배사')]/following-sibling::div//div[@class='ant-select-selector']"))
                )
                delivery_dropdown.click()
                time.sleep(1)
                self.logger.info("택배사 드롭다운 클릭 완료")
            except TimeoutException:
                # 대체 선택자 시도
                try:
                    delivery_dropdown = self.driver.find_element(
                        By.XPATH, "//div[contains(text(), '택배사')]/..//div[contains(@class, 'ant-select-selector')]"
                    )
                    delivery_dropdown.click()
                    time.sleep(1)
                    self.logger.info("택배사 드롭다운 클릭 완료 (대체 선택자)")
                except Exception as e:
                    self.logger.error(f"택배사 드롭다운 클릭 실패: {e}")
                    return False
            
            # 롯데택배 선택 (5번째 옵션)
            try:
                # 드롭다운 옵션들이 나타날 때까지 대기
                time.sleep(1)
                
                # 롯데택배 옵션 클릭 (여러 방법 시도)
                lotte_options = [
                    "//div[@class='ant-select-item-option-content'][contains(text(), '롯데')]",
                    "//div[contains(@class, 'ant-select-item')][contains(text(), '롯데')]",
                    "//div[contains(@class, 'ant-select-item')][5]",  # 5번째 옵션
                ]
                
                success = False
                for option_xpath in lotte_options:
                    try:
                        lotte_option = self.driver.find_element(By.XPATH, option_xpath)
                        lotte_option.click()
                        self.logger.info("롯데택배 선택 완료")
                        success = True
                        break
                    except:
                        continue
                
                if not success:
                    self.logger.error("롯데택배 옵션을 찾을 수 없습니다")
                    return False
                
                time.sleep(1)
                return True
                
            except Exception as e:
                self.logger.error(f"롯데택배 선택 중 오류: {e}")
                return False
                
        except Exception as e:
            self.logger.error(f"택배사 변경 중 오류 발생: {e}")
            return False
    
    def _change_gmarket_site_discount_agreement(self):
        """G마켓 사이트할인 동의를 '동의'로 변경합니다."""
        try:
            self.logger.info("G마켓 사이트할인 동의 변경 시작")
            
            # G마켓 사이트할인 동의의 '동의' 라디오 버튼 클릭
            gmarket_agree_selectors = [
                "//div[contains(text(), 'G마켓 사이트할인 동의')]/following-sibling::div//label[contains(., '동의') and not(contains(., '동의하지 않음'))]",
                "//div[contains(text(), 'G마켓 사이트할인 동의')]/following-sibling::div//span[text()='동의']/parent::label",
                "//div[contains(text(), 'G마켓 사이트할인 동의')]/following-sibling::div//input[@value='true']/parent::span/parent::label"
            ]
            
            success = False
            for selector in gmarket_agree_selectors:
                try:
                    gmarket_agree_button = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    gmarket_agree_button.click()
                    self.logger.info("G마켓 사이트할인 '동의' 선택 완료")
                    success = True
                    break
                except TimeoutException:
                    continue
            
            if not success:
                self.logger.error("G마켓 사이트할인 동의 버튼을 찾을 수 없습니다")
                return False
            
            time.sleep(0.5)
            return True
            
        except Exception as e:
            self.logger.error(f"G마켓 사이트할인 동의 변경 중 오류 발생: {e}")
            return False
    
    def _change_auction_site_discount_agreement(self):
        """옥션 사이트할인 동의를 '동의'로 변경합니다."""
        try:
            self.logger.info("옥션 사이트할인 동의 변경 시작")
            
            # 옥션 사이트할인 동의의 '동의' 라디오 버튼 클릭
            auction_agree_selectors = [
                "//div[contains(text(), '옥션 사이트할인 동의')]/following-sibling::div//label[contains(., '동의') and not(contains(., '동의하지 않음'))]",
                "//div[contains(text(), '옥션 사이트할인 동의')]/following-sibling::div//span[text()='동의']/parent::label",
                "//div[contains(text(), '옥션 사이트할인 동의')]/following-sibling::div//input[@value='true']/parent::span/parent::label"
            ]
            
            success = False
            for selector in auction_agree_selectors:
                try:
                    auction_agree_button = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    auction_agree_button.click()
                    self.logger.info("옥션 사이트할인 '동의' 선택 완료")
                    success = True
                    break
                except TimeoutException:
                    continue
            
            if not success:
                self.logger.error("옥션 사이트할인 동의 버튼을 찾을 수 없습니다")
                return False
            
            time.sleep(0.5)
            return True
            
        except Exception as e:
            self.logger.error(f"옥션 사이트할인 동의 변경 중 오류 발생: {e}")
            return False
    
    def _click_auction_gmarket_shipping_profile_create_button(self):
        """옥션/G마켓 배송프로필 만들기 버튼을 클릭합니다."""
        try:
            self.logger.info("옥션/G마켓 배송프로필 만들기 버튼 클릭 시작")
            
            # 배송프로필 만들기 버튼 클릭 (11번가와 동일한 선택자 사용)
            create_button_selectors = [
                ".ant-drawer-extra button.ant-btn.ant-btn-primary",
                "//button[contains(., '배송프로필 만들기')]",
                ".ant-drawer-extra .ant-btn-primary"
            ]
            
            success = False
            for selector in create_button_selectors:
                try:
                    if selector.startswith('//'):
                        create_button = self.wait.until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    else:
                        create_button = self.wait.until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    create_button.click()
                    self.logger.info("옥션/G마켓 배송프로필 만들기 버튼 클릭 완료")
                    success = True
                    break
                except TimeoutException:
                    continue
            
            if not success:
                self.logger.error("옥션/G마켓 배송프로필 만들기 버튼을 찾을 수 없습니다")
                return False
            
            # 모달창이 닫힐 때까지 대기
            try:
                self.wait.until(
                    EC.invisibility_of_element_located((By.CSS_SELECTOR, ".ant-drawer-content-wrapper"))
                )
                self.logger.info("옥션/G마켓 배송 프로필 모달창 닫힘 확인")
            except TimeoutException:
                self.logger.warning("모달창 닫힘 확인 실패, 계속 진행")
            
            time.sleep(2)
            return True
            
        except Exception as e:
            self.logger.error(f"옥션/G마켓 배송프로필 만들기 버튼 클릭 중 오류 발생: {e}")
            return False