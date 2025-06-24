import logging
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from dropdown_utils4 import DropdownUtils4
from upload_utils import UploadUtils
from market_utils import MarketUtils

# 퍼센티 확장프로그램 경로
PERCENTY_EXTENSION_PATH = r"c:\Projects\percenty_project\percenty_extension"

# 로거 설정
logger = logging.getLogger(__name__)

class ProductEditorCore6_1Enhanced:
    """
    개선된 퍼센티 확장 프로그램 검색 로직을 포함한 상품 편집기 코어 클래스
    
    주요 개선사항:
    - 다중 전략 확장 프로그램 검색
    - 적응형 대기 시스템
    - 포괄적인 디버깅 및 로깅
    - Shadow DOM 기반 고급 검색
    """
    
    def __init__(self, driver, account_id):
        """
        ProductEditorCore6_1Enhanced 초기화
        
        Args:
            driver: Selenium WebDriver 인스턴스
            account_id: 계정 ID
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.account_id = account_id
        
        # 유틸리티 클래스 초기화
        self.dropdown_utils = DropdownUtils4(driver)
        self.upload_utils = UploadUtils(driver)
        self.market_utils = MarketUtils(driver)
        
        logger.info(f"ProductEditorCore6_1Enhanced 초기화 완료 - 계정 ID: {account_id}")
    
    def verify_extension_installed(self):
        """
        퍼센티 확장프로그램이 설치되었는지 확인합니다.
        개선된 다중 전략 검색과 적응형 대기 시스템을 사용합니다.
        
        Returns:
            bool: 확장프로그램 설치 여부
        """
        try:
            logger.info("퍼센티 확장프로그램 설치 확인 시작")
            
            # Chrome 확장 프로그램 페이지로 이동
            self.driver.get("chrome://extensions/")
            time.sleep(3)
            
            # 적응형 대기를 포함한 다중 전략 검색
            found, search_results = self._search_with_adaptive_wait()
            
            if found:
                logger.info(f"✅ 퍼센티 확장프로그램 발견! 성공한 전략: {', '.join(search_results.get('successful_strategies', []))}")
                logger.info(f"검색 소요 시간: {search_results.get('total_duration', 0):.1f}초")
                return True
            else:
                logger.warning("❌ 퍼센티 확장프로그램을 찾을 수 없습니다")
                logger.info(f"총 {search_results.get('total_attempts', 0)}회 시도, {search_results.get('total_duration', 0):.1f}초 소요")
                
                # 상세 디버깅 정보 수집
                self._debug_extension_environment()
                self._log_all_extensions_detailed()
                
                return False
            
        except Exception as e:
            logger.error(f"확장프로그램 확인 중 오류 발생: {e}")
            return False
    
    def _search_with_adaptive_wait(self, max_wait_time=60, check_interval=5):
        """
        적응형 대기를 포함한 다중 전략 확장 프로그램 검색
        
        Args:
            max_wait_time: 최대 대기 시간 (초)
            check_interval: 검색 간격 (초)
            
        Returns:
            tuple: (발견 여부, 검색 결과 상세 정보)
        """
        start_time = time.time()
        attempt_count = 0
        search_results = {
            'found': False,
            'total_attempts': 0,
            'successful_strategies': [],
            'total_duration': 0,
            'refresh_count': 0
        }
        
        logger.info(f"적응형 대기 검색 시작 (최대 {max_wait_time}초)")
        
        while time.time() - start_time < max_wait_time:
            attempt_count += 1
            search_results['total_attempts'] = attempt_count
            
            logger.info(f"\n--- 검색 시도 #{attempt_count} ---")
            
            # 다중 전략 검색 수행
            found, strategies = self._search_with_multiple_strategies()
            
            if found:
                search_results['found'] = True
                search_results['successful_strategies'] = strategies
                search_results['total_duration'] = time.time() - start_time
                logger.info(f"🎉 확장 프로그램 발견! (시도 #{attempt_count}, {search_results['total_duration']:.1f}초)")
                return True, search_results
            
            # 3번째 시도마다 페이지 새로고침
            if attempt_count % 3 == 0 and attempt_count > 0:
                logger.info("📄 페이지 새로고침 후 재검색")
                try:
                    self.driver.refresh()
                    time.sleep(3)
                    search_results['refresh_count'] += 1
                except Exception as e:
                    logger.warning(f"페이지 새로고침 실패: {e}")
            
            logger.info(f"⏳ {check_interval}초 대기 후 재시도...")
            time.sleep(check_interval)
        
        search_results['total_duration'] = time.time() - start_time
        logger.warning(f"⏰ 검색 시간 초과 ({search_results['total_duration']:.1f}초, {attempt_count}회 시도)")
        
        return False, search_results
    
    def _search_with_multiple_strategies(self):
        """
        다중 전략을 사용한 확장 프로그램 검색
        
        Returns:
            tuple: (발견 여부, 성공한 전략 목록)
        """
        successful_strategies = []
        
        # 전략 1: 개선된 Shadow DOM 검색
        try:
            if self._enhanced_shadow_dom_search():
                successful_strategies.append("Enhanced Shadow DOM")
                logger.info("✅ Enhanced Shadow DOM에서 확장 프로그램 발견!")
        except Exception as e:
            logger.error(f"❌ Enhanced Shadow DOM 검색 오류: {e}")
        
        # 전략 2: Chrome Extension API 검색
        try:
            if self._chrome_api_search():
                successful_strategies.append("Chrome API")
                logger.info("✅ Chrome API에서 확장 프로그램 발견!")
        except Exception as e:
            logger.error(f"❌ Chrome API 검색 오류: {e}")
        
        # 전략 3: 기존 Shadow DOM 검색
        try:
            if self._search_extensions_in_shadow_dom():
                successful_strategies.append("Original Shadow DOM")
                logger.info("✅ Original Shadow DOM에서 확장 프로그램 발견!")
        except Exception as e:
            logger.error(f"❌ Original Shadow DOM 검색 오류: {e}")
        
        # 전략 4: DOM 텍스트 검색
        try:
            if self._dom_text_search():
                successful_strategies.append("DOM Text Search")
                logger.info("✅ DOM Text Search에서 확장 프로그램 발견!")
        except Exception as e:
            logger.error(f"❌ DOM Text Search 오류: {e}")
        
        # 전략 5: 요소 속성 검색
        try:
            if self._element_attribute_search():
                successful_strategies.append("Element Attribute Search")
                logger.info("✅ Element Attribute Search에서 확장 프로그램 발견!")
        except Exception as e:
            logger.error(f"❌ Element Attribute Search 오류: {e}")
        
        found = len(successful_strategies) > 0
        return found, successful_strategies
    
    def _enhanced_shadow_dom_search(self):
        """
        개선된 Shadow DOM 기반 확장 프로그램 검색
        
        Returns:
            bool: 확장 프로그램 발견 여부
        """
        try:
            search_script = """
            function searchExtensionsInShadowDOM() {
                const results = {
                    found: false,
                    extensions: [],
                    searchDetails: []
                };
                
                try {
                    const extensionsManager = document.querySelector('extensions-manager');
                    if (!extensionsManager || !extensionsManager.shadowRoot) {
                        results.searchDetails.push('extensions-manager shadowRoot 접근 실패');
                        return results;
                    }
                    
                    results.searchDetails.push('extensions-manager shadowRoot 접근 성공');
                    
                    // 다양한 선택자로 확장 프로그램 검색
                    const selectors = [
                        'extensions-item',
                        'extensions-detail-view',
                        '[slot="item"]',
                        '.extension-item',
                        '[id*="extension"]',
                        '*[data-extension-id]',
                        '.extension-name',
                        '.name'
                    ];
                    
                    for (const selector of selectors) {
                        const elements = extensionsManager.shadowRoot.querySelectorAll(selector);
                        results.searchDetails.push(`선택자 '${selector}': ${elements.length}개 발견`);
                        
                        elements.forEach((element, index) => {
                            try {
                                let extensionName = '';
                                
                                // 다양한 방법으로 이름 추출
                                const nameSelectors = ['.extension-name', '.name', '[slot="name"]', 'h3', '.title'];
                                
                                for (const nameSelector of nameSelectors) {
                                    const nameElement = element.querySelector(nameSelector);
                                    if (nameElement && nameElement.textContent.trim()) {
                                        extensionName = nameElement.textContent.trim();
                                        break;
                                    }
                                }
                                
                                // 텍스트 콘텐츠에서 직접 추출
                                if (!extensionName && element.textContent) {
                                    const text = element.textContent.trim();
                                    if (text.length > 0 && text.length < 100) {
                                        extensionName = text;
                                    }
                                }
                                
                                if (extensionName) {
                                    results.extensions.push({
                                        name: extensionName,
                                        selector: selector,
                                        index: index
                                    });
                                    
                                    // 퍼센티 확장 프로그램 확인
                                    if (extensionName.includes('퍼센티') || 
                                        extensionName.includes('Percenty') ||
                                        extensionName.toLowerCase().includes('percent')) {
                                        results.found = true;
                                        results.searchDetails.push(`퍼센티 확장프로그램 발견: ${extensionName}`);
                                    }
                                }
                            } catch (e) {
                                results.searchDetails.push(`요소 처리 오류: ${e.message}`);
                            }
                        });
                    }
                    
                    // 중첩된 shadowRoot 검색
                    const nestedElements = extensionsManager.shadowRoot.querySelectorAll('*');
                    nestedElements.forEach(element => {
                        if (element.shadowRoot) {
                            results.searchDetails.push(`중첩 shadowRoot 발견: ${element.tagName}`);
                            
                            const nestedExtensions = element.shadowRoot.querySelectorAll('extensions-item, .extension-item, *[data-extension-id]');
                            nestedExtensions.forEach(nestedExt => {
                                const nameText = nestedExt.textContent?.trim();
                                if (nameText && (nameText.includes('퍼센티') || nameText.includes('Percenty'))) {
                                    results.found = true;
                                    results.searchDetails.push(`중첩 shadowRoot에서 퍼센티 발견: ${nameText}`);
                                }
                            });
                        }
                    });
                    
                } catch (error) {
                    results.searchDetails.push(`검색 오류: ${error.message}`);
                }
                
                return results;
            }
            
            return searchExtensionsInShadowDOM();
            """
            
            result = self.driver.execute_script(search_script)
            
            # 검색 결과 로깅
            logger.info("Enhanced Shadow DOM 검색 결과:")
            for detail in result.get('searchDetails', []):
                logger.info(f"  - {detail}")
            
            if result.get('extensions'):
                logger.info(f"발견된 확장프로그램 목록:")
                for ext in result['extensions']:
                    logger.info(f"  - {ext['name']} (선택자: {ext['selector']})")
            
            return result.get('found', False)
            
        except Exception as e:
            logger.error(f"Enhanced Shadow DOM 검색 오류: {e}")
            return False
    
    def _chrome_api_search(self):
        """
        Chrome Extension API를 통한 확장 프로그램 검색
        
        Returns:
            bool: 확장 프로그램 발견 여부
        """
        try:
            api_script = """
            return new Promise((resolve) => {
                try {
                    if (typeof chrome !== 'undefined' && chrome.management) {
                        chrome.management.getAll((extensions) => {
                            const result = {
                                found: false,
                                extensions: [],
                                error: null
                            };
                            
                            extensions.forEach(ext => {
                                result.extensions.push({
                                    id: ext.id,
                                    name: ext.name,
                                    enabled: ext.enabled,
                                    type: ext.type
                                });
                                
                                if (ext.name.includes('퍼센티') || 
                                    ext.name.includes('Percenty') ||
                                    ext.name.toLowerCase().includes('percent')) {
                                    result.found = true;
                                }
                            });
                            
                            resolve(result);
                        });
                    } else {
                        resolve({
                            found: false,
                            extensions: [],
                            error: 'Chrome Management API 사용 불가'
                        });
                    }
                } catch (error) {
                    resolve({
                        found: false,
                        extensions: [],
                        error: error.message
                    });
                }
            });
            """
            
            result = self.driver.execute_async_script(api_script)
            
            if result.get('error'):
                logger.warning(f"Chrome API 제한: {result['error']}")
                return False
            
            logger.info(f"Chrome API 결과: {len(result.get('extensions', []))}개 확장프로그램 발견")
            
            for ext in result.get('extensions', []):
                logger.info(f"  - {ext['name']} (ID: {ext['id']}, 활성화: {ext['enabled']})")
            
            return result.get('found', False)
            
        except Exception as e:
            logger.error(f"Chrome API 검색 오류: {e}")
            return False
    
    def _search_extensions_in_shadow_dom(self):
        """
        기존 Shadow DOM을 통해 확장프로그램을 검색합니다.
        
        Returns:
            bool: 퍼센티 확장프로그램 발견 여부
        """
        try:
            logger.info("Shadow DOM에서 확장프로그램 검색 시작")
            
            js_code = """
                function searchExtensionsInShadowDOM() {
                    try {
                        const results = [];
                        let foundPercenty = false;
                        
                        // extensions-manager 요소 찾기
                        const extensionsManager = document.querySelector('extensions-manager');
                        if (!extensionsManager || !extensionsManager.shadowRoot) {
                            results.push('extensions-manager 또는 shadowRoot를 찾을 수 없음');
                            return {found: false, results: results};
                        }
                        
                        results.push('extensions-manager shadowRoot 접근 성공');
                        
                        // Shadow DOM 내에서 모든 extensions-item 검색
                        const shadowRoot = extensionsManager.shadowRoot;
                        const extensionItems = shadowRoot.querySelectorAll('extensions-item');
                        results.push(`Shadow DOM에서 발견된 확장프로그램: ${extensionItems.length}개`);
                        
                        // 각 확장프로그램 아이템 검사
                        for (let i = 0; i < extensionItems.length; i++) {
                            const item = extensionItems[i];
                            const itemShadowRoot = item.shadowRoot;
                            
                            if (itemShadowRoot) {
                                // 확장프로그램 이름 검색
                                const nameElement = itemShadowRoot.querySelector('#name');
                                if (nameElement) {
                                    const extensionName = nameElement.textContent || nameElement.innerText || '';
                                    results.push(`확장프로그램 ${i+1}: ${extensionName}`);
                                    
                                    // 퍼센티 확장프로그램 확인
                                    if (extensionName.toLowerCase().includes('percenty') || 
                                        extensionName.includes('퍼센티')) {
                                        results.push(`✅ 퍼센티 확장프로그램 발견: ${extensionName}`);
                                        foundPercenty = true;
                                    }
                                } else {
                                    results.push(`확장프로그램 ${i+1}: 이름 요소를 찾을 수 없음`);
                                }
                            } else {
                                results.push(`확장프로그램 ${i+1}: shadowRoot 접근 불가`);
                            }
                        }
                        
                        return {found: foundPercenty, results: results};
                        
                    } catch (error) {
                        return {found: false, results: ['Shadow DOM 검색 중 오류: ' + error.message]};
                    }
                }
                
                return searchExtensionsInShadowDOM();
                """
            
            result = self.driver.execute_script(js_code)
            
            # 검색 결과 로깅
            if result and 'results' in result:
                logger.info("Shadow DOM 검색 결과:")
                for search_result in result['results']:
                    logger.info(f"  - {search_result}")
            
            return result.get('found', False) if result else False
            
        except Exception as e:
            logger.error(f"Shadow DOM 검색 중 오류: {e}")
            return False
    
    def _dom_text_search(self):
        """
        DOM 텍스트 기반 확장 프로그램 검색
        
        Returns:
            bool: 확장 프로그램 발견 여부
        """
        try:
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            keywords = ["퍼센티", "Percenty", "percent", "PERCENTY"]
            found_keywords = []
            
            for keyword in keywords:
                if keyword in page_text:
                    found_keywords.append(keyword)
            
            if found_keywords:
                logger.info(f"DOM 텍스트 검색 결과: 발견된 키워드 - {', '.join(found_keywords)}")
                return True
            else:
                logger.info("DOM 텍스트 검색 결과: 퍼센티 관련 텍스트 없음")
                return False
                
        except Exception as e:
            logger.error(f"DOM 텍스트 검색 오류: {e}")
            return False
    
    def _element_attribute_search(self):
        """
        요소 속성 기반 확장 프로그램 검색
        
        Returns:
            bool: 확장 프로그램 발견 여부
        """
        try:
            search_script = """
            const results = {
                found: false,
                matches: []
            };
            
            const allElements = document.querySelectorAll('*');
            
            allElements.forEach((element, index) => {
                const attributes = ['id', 'class', 'data-extension-id', 'data-name', 'title', 'alt'];
                
                attributes.forEach(attr => {
                    const value = element.getAttribute(attr);
                    if (value && (value.includes('퍼센티') || 
                                 value.includes('Percenty') ||
                                 value.toLowerCase().includes('percent'))) {
                        results.found = true;
                        results.matches.push({
                            tagName: element.tagName,
                            attribute: attr,
                            value: value,
                            index: index
                        });
                    }
                });
            });
            
            return results;
            """
            
            result = self.driver.execute_script(search_script)
            
            if result.get('matches'):
                logger.info(f"요소 속성 검색 결과: {len(result['matches'])}개 매치 발견")
                for match in result['matches']:
                    logger.info(f"  - {match['tagName']}.{match['attribute']}: {match['value']}")
            else:
                logger.info("요소 속성 검색 결과: 속성에서 퍼센티 관련 내용 없음")
            
            return result.get('found', False)
            
        except Exception as e:
            logger.error(f"요소 속성 검색 오류: {e}")
            return False
    
    def _debug_extension_environment(self):
        """
        확장 프로그램 환경 디버깅 정보 수집
        
        Returns:
            dict: 디버깅 정보
        """
        debug_info = {
            'page_info': {},
            'chrome_info': {},
            'dom_info': {},
            'errors': []
        }
        
        try:
            # 페이지 정보
            debug_info['page_info'] = {
                'url': self.driver.current_url,
                'title': self.driver.title,
                'ready_state': self.driver.execute_script("return document.readyState")
            }
            
            # Chrome 정보
            chrome_info_script = """
            return {
                'userAgent': navigator.userAgent,
                'chromeVersion': navigator.userAgent.match(/Chrome\/(\d+)/)?.[1] || 'unknown',
                'hasExtensionAPI': typeof chrome !== 'undefined' && !!chrome.extension,
                'hasManagementAPI': typeof chrome !== 'undefined' && !!chrome.management,
                'extensionsPageActive': window.location.href.includes('chrome://extensions/')
            };
            """
            
            debug_info['chrome_info'] = self.driver.execute_script(chrome_info_script)
            
            # DOM 구조 정보
            dom_info_script = """
            const extensionsManager = document.querySelector('extensions-manager');
            return {
                'hasExtensionsManager': !!extensionsManager,
                'hasShadowRoot': !!(extensionsManager && extensionsManager.shadowRoot),
                'totalElements': document.querySelectorAll('*').length,
                'bodyText': document.body ? document.body.textContent.substring(0, 500) : 'no body'
            };
            """
            
            debug_info['dom_info'] = self.driver.execute_script(dom_info_script)
            
        except Exception as e:
            debug_info['errors'].append(f"디버깅 정보 수집 오류: {e}")
        
        # 디버깅 정보 로깅
        logger.info("=== 확장 프로그램 환경 디버깅 정보 ===")
        logger.info(f"페이지: {debug_info['page_info']}")
        logger.info(f"Chrome: {debug_info['chrome_info']}")
        logger.info(f"DOM: {debug_info['dom_info']}")
        
        if debug_info['errors']:
            logger.warning(f"오류: {debug_info['errors']}")
        
        return debug_info
    
    def _log_all_extensions_detailed(self):
        """
        설치된 모든 확장프로그램의 상세 정보를 로그에 출력합니다.
        """
        try:
            # 일반 DOM에서 확장프로그램 검색
            all_extensions = self.driver.find_elements(By.CSS_SELECTOR, "extensions-item")
            logger.info(f"일반 DOM에서 발견된 확장프로그램: {len(all_extensions)}개")
            
            for i, ext in enumerate(all_extensions[:10]):  # 최대 10개까지 로그 출력
                try:
                    ext_name = ext.find_element(By.CSS_SELECTOR, "#name").text
                    logger.info(f"  확장프로그램 {i+1}: {ext_name}")
                except:
                    logger.info(f"  확장프로그램 {i+1}: 이름 확인 불가")
            
            # JavaScript를 통한 추가 정보 수집
            js_code = """
                const allExtensions = document.querySelectorAll('extensions-item');
                const extensionInfo = [];
                
                for (let i = 0; i < Math.min(allExtensions.length, 10); i++) {
                    const ext = allExtensions[i];
                    const id = ext.getAttribute('id') || 'ID 없음';
                    const dataId = ext.getAttribute('data-extension-id') || 'data-extension-id 없음';
                    
                    extensionInfo.push({
                        index: i + 1,
                        id: id,
                        dataId: dataId,
                        tagName: ext.tagName
                    });
                }
                
                return extensionInfo;
                """
            
            extension_info = self.driver.execute_script(js_code)
            if extension_info:
                logger.info("JavaScript를 통한 확장프로그램 정보:")
                for info in extension_info:
                    logger.info(f"  {info['index']}. ID: {info['id']}, Data-ID: {info['dataId']}")
            
        except Exception as e:
            logger.debug(f"확장프로그램 상세 정보 수집 중 오류: {e}")

# 테스트 함수
def test_enhanced_extension_search():
    """
    개선된 확장 프로그램 검색 시스템 테스트
    """
    import logging
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('enhanced_extension_test.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("=== 개선된 확장 프로그램 검색 테스트 시작 ===")
        
        # Chrome 옵션 설정
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # 퍼센티 확장 프로그램 로드
        if PERCENTY_EXTENSION_PATH:
            chrome_options.add_argument(f"--load-extension={PERCENTY_EXTENSION_PATH}")
            logger.info(f"퍼센티 확장 프로그램 로드: {PERCENTY_EXTENSION_PATH}")
        
        # WebDriver 생성
        driver = webdriver.Chrome(options=chrome_options)
        logger.info("Chrome 드라이버 생성 완료")
        
        # ProductEditorCore6_1Enhanced 인스턴스 생성
        core = ProductEditorCore6_1Enhanced(driver, "test_account")
        logger.info("ProductEditorCore6_1Enhanced 인스턴스 생성 완료")
        
        # 확장 프로그램 검색 테스트
        result = core.verify_extension_installed()
        
        if result:
            logger.info("🎉 테스트 성공: 퍼센티 확장 프로그램이 발견되었습니다!")
        else:
            logger.warning("⚠️ 테스트 부분 성공: 퍼센티 확장 프로그램을 찾지 못했습니다.")
        
        # 10초 대기 후 브라우저 종료
        logger.info("10초 후 브라우저를 종료합니다...")
        time.sleep(10)
        
        driver.quit()
        logger.info("브라우저 종료 완료")
        
        logger.info("=== 테스트 완료 ===")
        return result
        
    except Exception as e:
        logger.error(f"테스트 중 오류 발생: {e}")
        try:
            driver.quit()
        except:
            pass
        return False

if __name__ == "__main__":
    test_enhanced_extension_search()