#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
개선된 확장 프로그램 검색 시스템

이 모듈은 Chrome 확장 프로그램의 설치 및 검색을 위한 강화된 로직을 제공합니다.
Shadow DOM, Chrome Extension API, 매니페스트 기반 검색 등 다양한 전략을 사용합니다.
"""

import time
import json
import logging
import os
from typing import List, Optional, Tuple, Dict, Any
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

logger = logging.getLogger(__name__)

class ExtensionSearchStrategy:
    """확장 프로그램 검색 전략 기본 클래스"""
    
    def __init__(self, name: str):
        self.name = name
    
    def search(self, driver: WebDriver, extension_name: str = "퍼센티") -> bool:
        """확장 프로그램 검색 수행
        
        Args:
            driver: Selenium WebDriver 인스턴스
            extension_name: 검색할 확장 프로그램 이름
            
        Returns:
            확장 프로그램 발견 여부
        """
        raise NotImplementedError

class ShadowDOMSearchStrategy(ExtensionSearchStrategy):
    """Shadow DOM 기반 확장 프로그램 검색"""
    
    def __init__(self):
        super().__init__("Shadow DOM 검색")
    
    def search(self, driver: WebDriver, extension_name: str = "퍼센티") -> bool:
        """Shadow DOM을 통한 확장 프로그램 검색"""
        try:
            logger.info(f"{self.name} 시작")
            
            # 개선된 Shadow DOM 검색 JavaScript
            search_script = """
            function searchExtensionsInShadowDOM() {
                const results = {
                    found: false,
                    extensions: [],
                    searchDetails: []
                };
                
                try {
                    // extensions-manager 요소 찾기
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
                        '[id*="extension"]'
                    ];
                    
                    let totalFound = 0;
                    
                    for (const selector of selectors) {
                        const elements = extensionsManager.shadowRoot.querySelectorAll(selector);
                        results.searchDetails.push(`선택자 '${selector}': ${elements.length}개 발견`);
                        
                        elements.forEach((element, index) => {
                            try {
                                // 확장 프로그램 이름 추출 시도
                                let extensionName = '';
                                
                                // 다양한 방법으로 이름 추출
                                const nameSelectors = [
                                    '.extension-name',
                                    '.name',
                                    '[slot="name"]',
                                    'h3',
                                    '.title'
                                ];
                                
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
                        
                        totalFound += elements.length;
                    }
                    
                    // 중첩된 shadowRoot 검색
                    const nestedElements = extensionsManager.shadowRoot.querySelectorAll('*');
                    nestedElements.forEach(element => {
                        if (element.shadowRoot) {
                            results.searchDetails.push(`중첩 shadowRoot 발견: ${element.tagName}`);
                            
                            const nestedExtensions = element.shadowRoot.querySelectorAll('extensions-item, .extension-item');
                            nestedExtensions.forEach(nestedExt => {
                                const nameText = nestedExt.textContent?.trim();
                                if (nameText && (nameText.includes('퍼센티') || nameText.includes('Percenty'))) {
                                    results.found = true;
                                    results.searchDetails.push(`중첩 shadowRoot에서 퍼센티 발견: ${nameText}`);
                                }
                            });
                        }
                    });
                    
                    results.searchDetails.push(`총 ${totalFound}개 요소 검색 완료`);
                    
                } catch (error) {
                    results.searchDetails.push(`검색 오류: ${error.message}`);
                }
                
                return results;
            }
            
            return searchExtensionsInShadowDOM();
            """
            
            result = driver.execute_script(search_script)
            
            # 검색 결과 로깅
            logger.info(f"{self.name} 결과:")
            for detail in result.get('searchDetails', []):
                logger.info(f"  - {detail}")
            
            if result.get('extensions'):
                logger.info(f"발견된 확장프로그램 목록:")
                for ext in result['extensions']:
                    logger.info(f"  - {ext['name']} (선택자: {ext['selector']})")
            
            return result.get('found', False)
            
        except Exception as e:
            logger.error(f"{self.name} 오류: {e}")
            return False

class ChromeAPISearchStrategy(ExtensionSearchStrategy):
    """Chrome Extension API 기반 검색"""
    
    def __init__(self):
        super().__init__("Chrome API 검색")
    
    def search(self, driver: WebDriver, extension_name: str = "퍼센티") -> bool:
        """Chrome Extension API를 통한 검색"""
        try:
            logger.info(f"{self.name} 시작")
            
            # Chrome Extension Management API 사용
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
            
            result = driver.execute_async_script(api_script)
            
            if result.get('error'):
                logger.warning(f"{self.name} 제한: {result['error']}")
                return False
            
            logger.info(f"{self.name} 결과: {len(result.get('extensions', []))}개 확장프로그램 발견")
            
            for ext in result.get('extensions', []):
                logger.info(f"  - {ext['name']} (ID: {ext['id']}, 활성화: {ext['enabled']})")
            
            return result.get('found', False)
            
        except Exception as e:
            logger.error(f"{self.name} 오류: {e}")
            return False

class DOMTextSearchStrategy(ExtensionSearchStrategy):
    """DOM 텍스트 기반 검색"""
    
    def __init__(self):
        super().__init__("DOM 텍스트 검색")
    
    def search(self, driver: WebDriver, extension_name: str = "퍼센티") -> bool:
        """페이지 텍스트에서 확장 프로그램 검색"""
        try:
            logger.info(f"{self.name} 시작")
            
            # 페이지 전체 텍스트에서 검색
            page_text = driver.find_element(By.TAG_NAME, "body").text
            
            # 퍼센티 관련 키워드 검색
            keywords = ["퍼센티", "Percenty", "percent", "PERCENTY"]
            found_keywords = []
            
            for keyword in keywords:
                if keyword in page_text:
                    found_keywords.append(keyword)
            
            if found_keywords:
                logger.info(f"{self.name} 결과: 발견된 키워드 - {', '.join(found_keywords)}")
                return True
            else:
                logger.info(f"{self.name} 결과: 퍼센티 관련 텍스트 없음")
                return False
                
        except Exception as e:
            logger.error(f"{self.name} 오류: {e}")
            return False

class ElementAttributeSearchStrategy(ExtensionSearchStrategy):
    """요소 속성 기반 검색"""
    
    def __init__(self):
        super().__init__("요소 속성 검색")
    
    def search(self, driver: WebDriver, extension_name: str = "퍼센티") -> bool:
        """요소의 속성에서 확장 프로그램 검색"""
        try:
            logger.info(f"{self.name} 시작")
            
            # 다양한 속성에서 퍼센티 검색
            search_script = """
            const results = {
                found: false,
                matches: []
            };
            
            // 모든 요소 검색
            const allElements = document.querySelectorAll('*');
            
            allElements.forEach((element, index) => {
                // 속성 검사
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
            
            result = driver.execute_script(search_script)
            
            if result.get('matches'):
                logger.info(f"{self.name} 결과: {len(result['matches'])}개 매치 발견")
                for match in result['matches']:
                    logger.info(f"  - {match['tagName']}.{match['attribute']}: {match['value']}")
            else:
                logger.info(f"{self.name} 결과: 속성에서 퍼센티 관련 내용 없음")
            
            return result.get('found', False)
            
        except Exception as e:
            logger.error(f"{self.name} 오류: {e}")
            return False

class EnhancedExtensionSearcher:
    """개선된 확장 프로그램 검색 시스템"""
    
    def __init__(self, max_wait_time: int = 60, check_interval: int = 3):
        self.max_wait_time = max_wait_time
        self.check_interval = check_interval
        
        # 검색 전략 목록 (우선순위 순)
        self.strategies = [
            ShadowDOMSearchStrategy(),
            ChromeAPISearchStrategy(),
            DOMTextSearchStrategy(),
            ElementAttributeSearchStrategy()
        ]
    
    def search_with_multiple_strategies(self, driver: WebDriver, extension_name: str = "퍼센티") -> Tuple[bool, List[str]]:
        """다중 전략을 사용한 확장 프로그램 검색
        
        Args:
            driver: Selenium WebDriver 인스턴스
            extension_name: 검색할 확장 프로그램 이름
            
        Returns:
            (발견 여부, 성공한 전략 목록)
        """
        successful_strategies = []
        
        logger.info("=== 다중 전략 확장 프로그램 검색 시작 ===")
        
        for strategy in self.strategies:
            try:
                if strategy.search(driver, extension_name):
                    successful_strategies.append(strategy.name)
                    logger.info(f"✅ {strategy.name}에서 확장 프로그램 발견!")
                else:
                    logger.info(f"❌ {strategy.name}에서 확장 프로그램 미발견")
            except Exception as e:
                logger.error(f"❌ {strategy.name} 실행 오류: {e}")
        
        found = len(successful_strategies) > 0
        
        logger.info(f"=== 검색 완료: {'성공' if found else '실패'} ===")
        if successful_strategies:
            logger.info(f"성공한 전략: {', '.join(successful_strategies)}")
        
        return found, successful_strategies
    
    def search_with_adaptive_wait(self, driver: WebDriver, extension_name: str = "퍼센티") -> Tuple[bool, Dict[str, Any]]:
        """적응형 대기를 포함한 확장 프로그램 검색
        
        Args:
            driver: Selenium WebDriver 인스턴스
            extension_name: 검색할 확장 프로그램 이름
            
        Returns:
            (발견 여부, 검색 결과 상세 정보)
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
        
        logger.info(f"적응형 대기 검색 시작 (최대 {self.max_wait_time}초)")
        
        while time.time() - start_time < self.max_wait_time:
            attempt_count += 1
            search_results['total_attempts'] = attempt_count
            
            logger.info(f"\n--- 검색 시도 #{attempt_count} ---")
            
            # 다중 전략 검색 수행
            found, strategies = self.search_with_multiple_strategies(driver, extension_name)
            
            if found:
                search_results['found'] = True
                search_results['successful_strategies'] = strategies
                search_results['total_duration'] = time.time() - start_time
                logger.info(f"🎉 확장 프로그램 발견! (시도 #{attempt_count}, {search_results['total_duration']:.1f}초)")
                return True, search_results
            
            # 10초마다 페이지 새로고침
            if attempt_count % 3 == 0 and attempt_count > 0:
                logger.info("📄 페이지 새로고침 후 재검색")
                try:
                    driver.refresh()
                    time.sleep(3)
                    search_results['refresh_count'] += 1
                except Exception as e:
                    logger.warning(f"페이지 새로고침 실패: {e}")
            
            logger.info(f"⏳ {self.check_interval}초 대기 후 재시도...")
            time.sleep(self.check_interval)
        
        search_results['total_duration'] = time.time() - start_time
        logger.warning(f"⏰ 검색 시간 초과 ({search_results['total_duration']:.1f}초, {attempt_count}회 시도)")
        
        return False, search_results
    
    def debug_extension_environment(self, driver: WebDriver) -> Dict[str, Any]:
        """확장 프로그램 환경 디버깅 정보 수집"""
        debug_info = {
            'page_info': {},
            'chrome_info': {},
            'dom_info': {},
            'errors': []
        }
        
        try:
            # 페이지 정보
            debug_info['page_info'] = {
                'url': driver.current_url,
                'title': driver.title,
                'ready_state': driver.execute_script("return document.readyState")
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
            
            debug_info['chrome_info'] = driver.execute_script(chrome_info_script)
            
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
            
            debug_info['dom_info'] = driver.execute_script(dom_info_script)
            
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

# 사용 예제
if __name__ == "__main__":
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 사용 예제 (실제 WebDriver 인스턴스 필요)
    """
    from selenium import webdriver
    
    # WebDriver 생성
    driver = webdriver.Chrome()
    
    try:
        # Chrome 확장 프로그램 페이지로 이동
        driver.get("chrome://extensions/")
        time.sleep(3)
        
        # 개선된 검색 시스템 사용
        searcher = EnhancedExtensionSearcher(max_wait_time=30, check_interval=5)
        
        # 환경 디버깅
        debug_info = searcher.debug_extension_environment(driver)
        
        # 적응형 검색 수행
        found, results = searcher.search_with_adaptive_wait(driver, "퍼센티")
        
        if found:
            print("✅ 퍼센티 확장 프로그램을 찾았습니다!")
            print(f"성공한 전략: {results['successful_strategies']}")
        else:
            print("❌ 퍼센티 확장 프로그램을 찾지 못했습니다.")
            print(f"총 {results['total_attempts']}회 시도, {results['total_duration']:.1f}초 소요")
    
    finally:
        driver.quit()
    """
    
    print("개선된 확장 프로그램 검색 시스템이 준비되었습니다.")
    print("실제 사용을 위해서는 Selenium WebDriver 인스턴스가 필요합니다.")