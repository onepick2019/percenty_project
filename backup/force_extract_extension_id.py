#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
퍼센티 확장 프로그램 ID 강제 추출 스크립트
다양한 방법을 통해 확장 프로그램 ID를 추출합니다.
"""

import logging
import time
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def force_extract_extension_id():
    """
    다양한 방법으로 퍼센티 확장 프로그램 ID를 강제 추출합니다.
    """
    driver = None
    
    try:
        logger.info("============================================================")
        logger.info("🔍 퍼센티 확장 프로그램 ID 강제 추출 시작")
        logger.info("============================================================")
        
        # Chrome 옵션 설정
        chrome_options = ChromeOptions()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        
        # Chrome 137+ 확장 프로그램 로드 지원을 위한 플래그 추가
        chrome_options.add_argument("--disable-features=DisableLoadExtensionCommandLineSwitch")
        
        # 압축 해제된 확장 프로그램 로드
        extension_path = r"C:\projects\percenty_project\percenty_extension"
        chrome_options.add_argument(f"--load-extension={extension_path}")
        
        # 개발자 모드 강제 활성화를 위한 추가 플래그
        chrome_options.add_argument("--enable-extensions")
        chrome_options.add_argument("--extensions-on-chrome-urls")
        
        logger.info(f"✅ 압축 해제된 확장 프로그램 로드: {extension_path}")
        logger.info("🚀 Chrome 브라우저 시작...")
        
        # WebDriver 시작
        driver = webdriver.Chrome(options=chrome_options)
        logger.info("✅ 브라우저 시작 성공")
        
        # 먼저 일반 페이지로 이동하여 확장 프로그램이 로드되었는지 확인
        logger.info("🌐 일반 페이지로 이동하여 확장 프로그램 확인...")
        driver.get("data:text/html,<html><body><h1>Extension Test Page</h1></body></html>")
        time.sleep(2)
        
        # 확장 프로그램 관리 페이지로 이동
        logger.info("📋 확장 프로그램 관리 페이지로 이동...")
        driver.get("chrome://extensions/")
        time.sleep(5)
        
        # 페이지 소스 확인
        logger.info("📄 페이지 소스 확인...")
        page_source = driver.page_source
        if "퍼센티" in page_source:
            logger.info("✅ 페이지 소스에서 '퍼센티' 발견")
        else:
            logger.warning("⚠️ 페이지 소스에서 '퍼센티'를 찾을 수 없음")
        
        # 개발자 모드 강제 활성화 시도
        logger.info("🛠️ 개발자 모드 강제 활성화 시도...")
        
        # 여러 방법으로 개발자 모드 토글 시도
        dev_mode_activated = False
        
        # 방법 1: JavaScript로 직접 활성화
        try:
            logger.info("   방법 1: JavaScript로 개발자 모드 활성화")
            activate_script = """
            const manager = document.querySelector('extensions-manager');
            if (manager && manager.shadowRoot) {
                const toolbar = manager.shadowRoot.querySelector('extensions-toolbar');
                if (toolbar && toolbar.shadowRoot) {
                    const toggle = toolbar.shadowRoot.querySelector('#devMode');
                    if (toggle) {
                        if (!toggle.checked) {
                            toggle.click();
                            return 'activated';
                        } else {
                            return 'already_active';
                        }
                    }
                }
            }
            return 'not_found';
            """
            
            result = driver.execute_script(activate_script)
            logger.info(f"   JavaScript 결과: {result}")
            
            if result in ['activated', 'already_active']:
                dev_mode_activated = True
                logger.info("   ✅ JavaScript로 개발자 모드 활성화 성공")
            
        except Exception as e:
            logger.warning(f"   ⚠️ JavaScript 방법 실패: {e}")
        
        # 방법 2: 키보드 단축키 시도
        if not dev_mode_activated:
            try:
                logger.info("   방법 2: 키보드 단축키로 개발자 모드 활성화")
                actions = ActionChains(driver)
                actions.key_down(Keys.CONTROL).send_keys('d').key_up(Keys.CONTROL).perform()
                time.sleep(2)
                logger.info("   키보드 단축키 시도 완료")
            except Exception as e:
                logger.warning(f"   ⚠️ 키보드 단축키 방법 실패: {e}")
        
        time.sleep(3)
        
        # 확장 프로그램 정보 추출 (더 강력한 방법)
        logger.info("🔍 강화된 확장 프로그램 정보 추출...")
        
        enhanced_extraction_script = """
        function enhancedExtensionExtraction() {
            const results = {
                extensions: [],
                manager_found: false,
                total_count: 0,
                debug_info: [],
                raw_data: {}
            };
            
            try {
                // 1. 기본 확장 프로그램 관리자 확인
                const extensionsManager = document.querySelector('extensions-manager');
                if (extensionsManager) {
                    results.manager_found = true;
                    results.debug_info.push('extensions-manager 요소 발견');
                    
                    const shadowRoot = extensionsManager.shadowRoot;
                    if (shadowRoot) {
                        results.debug_info.push('Shadow DOM 접근 성공');
                        
                        // 2. 모든 가능한 확장 프로그램 요소 찾기
                        const possibleSelectors = [
                            'extensions-item',
                            'extension-item',
                            '[data-extension-id]',
                            '[id*="extension"]',
                            '.extension-item',
                            '.extension-card'
                        ];
                        
                        let allItems = [];
                        possibleSelectors.forEach(selector => {
                            const items = shadowRoot.querySelectorAll(selector);
                            if (items.length > 0) {
                                results.debug_info.push(`${selector}로 ${items.length}개 요소 발견`);
                                allItems = [...allItems, ...Array.from(items)];
                            }
                        });
                        
                        // 중복 제거
                        const uniqueItems = [...new Set(allItems)];
                        results.total_count = uniqueItems.length;
                        
                        uniqueItems.forEach((item, index) => {
                            try {
                                const itemInfo = {
                                    index: index,
                                    tag_name: item.tagName,
                                    id: item.id || '',
                                    class_name: item.className || '',
                                    text_content: item.textContent ? item.textContent.substring(0, 100) : '',
                                    attributes: {}
                                };
                                
                                // 모든 속성 수집
                                for (let attr of item.attributes) {
                                    itemInfo.attributes[attr.name] = attr.value;
                                }
                                
                                // Shadow DOM이 있는 경우 내부 정보 추출
                                if (item.shadowRoot) {
                                    const shadow = item.shadowRoot;
                                    
                                    // 이름 찾기
                                    const nameSelectors = ['#name', '.name', '[data-name]', 'h2', 'h3'];
                                    for (let selector of nameSelectors) {
                                        const nameEl = shadow.querySelector(selector);
                                        if (nameEl && nameEl.textContent.trim()) {
                                            itemInfo.name = nameEl.textContent.trim();
                                            break;
                                        }
                                    }
                                    
                                    // ID 찾기
                                    const idSelectors = ['[data-extension-id]', '#extensionId', '.extension-id'];
                                    for (let selector of idSelectors) {
                                        const idEl = shadow.querySelector(selector);
                                        if (idEl) {
                                            itemInfo.extension_id = idEl.getAttribute('data-extension-id') || 
                                                                   idEl.textContent.trim() || 
                                                                   idEl.value;
                                            break;
                                        }
                                    }
                                    
                                    // 세부정보 버튼에서 ID 추출
                                    const detailsButton = shadow.querySelector('#detailsButton, .details-button, [href*="extension"]');
                                    if (detailsButton) {
                                        const href = detailsButton.getAttribute('href') || '';
                                        const match = href.match(/\/([a-z]{32})$/);
                                        if (match) {
                                            itemInfo.details_id = match[1];
                                        }
                                    }
                                    
                                    // 활성화 상태 확인
                                    const toggles = shadow.querySelectorAll('cr-toggle, input[type="checkbox"], .toggle');
                                    if (toggles.length > 0) {
                                        itemInfo.enabled = toggles[0].checked || toggles[0].hasAttribute('checked');
                                    }
                                }
                                
                                results.extensions.push(itemInfo);
                                
                            } catch (itemError) {
                                results.debug_info.push(`아이템 ${index} 처리 오류: ${itemError.message}`);
                            }
                        });
                        
                        // 3. 페이지 전체에서 '퍼센티' 텍스트 검색
                        const allText = shadowRoot.textContent || '';
                        if (allText.includes('퍼센티')) {
                            results.debug_info.push('Shadow DOM에서 퍼센티 텍스트 발견');
                            
                            // 퍼센티 주변 텍스트 추출
                            const persentyIndex = allText.indexOf('퍼센티');
                            const contextStart = Math.max(0, persentyIndex - 100);
                            const contextEnd = Math.min(allText.length, persentyIndex + 100);
                            results.raw_data.percenty_context = allText.substring(contextStart, contextEnd);
                        }
                        
                        // 4. 모든 링크에서 확장 프로그램 ID 패턴 찾기
                        const allLinks = shadowRoot.querySelectorAll('a[href*="extension"]');
                        allLinks.forEach((link, index) => {
                            const href = link.getAttribute('href') || '';
                            const match = href.match(/\/([a-z]{32})/);
                            if (match) {
                                results.debug_info.push(`링크 ${index}에서 ID 발견: ${match[1]}`);
                                results.raw_data[`link_${index}_id`] = match[1];
                                results.raw_data[`link_${index}_href`] = href;
                            }
                        });
                        
                    } else {
                        results.debug_info.push('Shadow DOM 접근 실패');
                    }
                } else {
                    results.debug_info.push('extensions-manager 요소를 찾을 수 없음');
                }
                
                // 5. 전체 문서에서 확장 프로그램 ID 패턴 검색
                const documentText = document.documentElement.outerHTML;
                const idMatches = documentText.match(/[a-z]{32}/g);
                if (idMatches) {
                    results.raw_data.potential_ids = [...new Set(idMatches)];
                    results.debug_info.push(`문서에서 ${results.raw_data.potential_ids.length}개의 잠재적 ID 발견`);
                }
                
            } catch (error) {
                results.debug_info.push(`전체 오류: ${error.message}`);
            }
            
            return results;
        }
        
        return enhancedExtensionExtraction();
        """
        
        extension_info = driver.execute_script(enhanced_extraction_script)
        
        logger.info("📊 강화된 확장 프로그램 정보 추출 결과:")
        logger.info(f"   - 관리자 페이지 발견: {extension_info.get('manager_found', False)}")
        logger.info(f"   - 총 확장 프로그램 수: {extension_info.get('total_count', 0)}")
        
        # 디버그 정보 출력
        for debug_msg in extension_info.get('debug_info', []):
            logger.info(f"   🐛 {debug_msg}")
        
        # Raw 데이터 출력
        raw_data = extension_info.get('raw_data', {})
        if raw_data:
            logger.info("📋 Raw 데이터:")
            for key, value in raw_data.items():
                logger.info(f"   {key}: {value}")
        
        # 퍼센티 확장 프로그램 찾기
        percenty_extension = None
        for ext in extension_info.get('extensions', []):
            name = ext.get('name', '')
            text_content = ext.get('text_content', '')
            if '퍼센티' in name or '퍼센티' in text_content:
                percenty_extension = ext
                break
        
        # 결과 저장
        result_data = {
            'extraction_method': 'enhanced_force_extraction',
            'extraction_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'percenty_extension': percenty_extension,
            'all_extensions': extension_info.get('extensions', []),
            'raw_data': raw_data,
            'debug_info': extension_info.get('debug_info', [])
        }
        
        with open('enhanced_extension_extraction_result.json', 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        logger.info("💾 결과가 enhanced_extension_extraction_result.json 파일에 저장되었습니다.")
        
        if percenty_extension:
            logger.info("============================================================")
            logger.info("✅ 퍼센티 확장 프로그램 발견!")
            logger.info(f"   📛 이름: {percenty_extension.get('name', 'N/A')}")
            logger.info(f"   🆔 확장 프로그램 ID: {percenty_extension.get('extension_id', 'N/A')}")
            logger.info(f"   🔗 세부정보 ID: {percenty_extension.get('details_id', 'N/A')}")
            logger.info(f"   ✅ 활성화: {percenty_extension.get('enabled', 'N/A')}")
            logger.info("============================================================")
            return True
        else:
            logger.error("❌ 퍼센티 확장 프로그램을 찾을 수 없습니다.")
            
            # 잠재적 ID들 출력
            potential_ids = raw_data.get('potential_ids', [])
            if potential_ids:
                logger.info(f"🔍 발견된 잠재적 ID들: {potential_ids}")
            
            return False
            
    except WebDriverException as e:
        logger.error(f"❌ WebDriver 오류: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ 예상치 못한 오류: {e}")
        return False
    finally:
        if driver:
            logger.info("🔚 브라우저 종료...")
            driver.quit()

if __name__ == "__main__":
    success = force_extract_extension_id()
    
    logger.info("============================================================")
    if success:
        logger.info("✅ 테스트 완료: 퍼센티 확장 프로그램 ID 추출 성공")
    else:
        logger.info("❌ 테스트 완료: 퍼센티 확장 프로그램 ID 추출 실패")
    logger.info("============================================================")