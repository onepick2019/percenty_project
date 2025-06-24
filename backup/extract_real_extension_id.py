#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
퍼센티 확장 프로그램의 실제 ID 추출 스크립트
압축 해제된 확장 프로그램의 Chrome 자동 생성 ID를 정확히 추출합니다.
"""

import logging
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def extract_extension_id():
    """
    퍼센티 확장 프로그램의 실제 ID를 추출합니다.
    """
    driver = None
    
    try:
        logger.info("============================================================")
        logger.info("🔍 퍼센티 확장 프로그램 실제 ID 추출 시작")
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
        
        logger.info(f"✅ 압축 해제된 확장 프로그램 로드: {extension_path}")
        logger.info("🚀 Chrome 브라우저 시작...")
        
        # WebDriver 시작
        driver = webdriver.Chrome(options=chrome_options)
        logger.info("✅ 브라우저 시작 성공")
        
        # 확장 프로그램 관리 페이지로 이동
        logger.info("📋 확장 프로그램 관리 페이지로 이동...")
        driver.get("chrome://extensions/")
        time.sleep(3)
        
        # 개발자 모드 활성화
        logger.info("🛠️ 개발자 모드 활성화 시도...")
        try:
            # 개발자 모드 토글 찾기 (여러 선택자 시도)
            dev_mode_selectors = [
                "#devMode",
                "[id='devMode']",
                "input[type='checkbox'][aria-label*='개발자']",
                "input[type='checkbox'][aria-label*='Developer']",
                "cr-toggle[aria-label*='개발자']",
                "cr-toggle[aria-label*='Developer']"
            ]
            
            dev_mode_enabled = False
            for selector in dev_mode_selectors:
                try:
                    dev_toggle = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    if not dev_toggle.is_selected():
                        dev_toggle.click()
                        logger.info("✅ 개발자 모드 활성화됨")
                    else:
                        logger.info("✅ 개발자 모드 이미 활성화됨")
                    dev_mode_enabled = True
                    break
                except TimeoutException:
                    continue
            
            if not dev_mode_enabled:
                logger.warning("⚠️ 개발자 모드 토글을 찾을 수 없음")
                
        except Exception as e:
            logger.warning(f"⚠️ 개발자 모드 활성화 실패: {e}")
        
        time.sleep(2)
        
        # JavaScript를 통한 확장 프로그램 정보 추출
        logger.info("🔍 JavaScript를 통한 확장 프로그램 정보 추출...")
        
        # 확장 프로그램 관리 API 접근
        extension_info_script = """
        function getExtensionInfo() {
            const results = {
                extensions: [],
                manager_found: false,
                total_count: 0,
                debug_info: []
            };
            
            try {
                // 확장 프로그램 관리 페이지 확인
                const extensionsManager = document.querySelector('extensions-manager');
                if (extensionsManager) {
                    results.manager_found = true;
                    results.debug_info.push('extensions-manager 요소 발견');
                    
                    // Shadow DOM 접근
                    const shadowRoot = extensionsManager.shadowRoot;
                    if (shadowRoot) {
                        results.debug_info.push('Shadow DOM 접근 성공');
                        
                        // 확장 프로그램 아이템 찾기
                        const extensionItems = shadowRoot.querySelectorAll('extensions-item');
                        results.total_count = extensionItems.length;
                        results.debug_info.push(`확장 프로그램 아이템 ${extensionItems.length}개 발견`);
                        
                        extensionItems.forEach((item, index) => {
                            try {
                                const itemShadow = item.shadowRoot;
                                if (itemShadow) {
                                    // 확장 프로그램 이름 추출
                                    const nameElement = itemShadow.querySelector('#name');
                                    const name = nameElement ? nameElement.textContent.trim() : '';
                                    
                                    // 확장 프로그램 ID 추출 (data-extension-id 속성에서)
                                    const extensionId = item.getAttribute('data-extension-id') || 
                                                      item.getAttribute('id') || 
                                                      item.dataset?.extensionId || '';
                                    
                                    // 활성화 상태 확인
                                    const toggleElement = itemShadow.querySelector('cr-toggle');
                                    const enabled = toggleElement ? toggleElement.checked : false;
                                    
                                    // 세부 정보 버튼에서 ID 추출 시도
                                    const detailsButton = itemShadow.querySelector('#detailsButton');
                                    let detailsId = '';
                                    if (detailsButton) {
                                        const href = detailsButton.getAttribute('href') || '';
                                        const match = href.match(/\/([a-z]{32})$/);
                                        if (match) {
                                            detailsId = match[1];
                                        }
                                    }
                                    
                                    // 모든 속성 수집
                                    const allAttributes = {};
                                    for (let attr of item.attributes) {
                                        allAttributes[attr.name] = attr.value;
                                    }
                                    
                                    const extensionInfo = {
                                        index: index,
                                        name: name,
                                        id: extensionId || detailsId,
                                        details_id: detailsId,
                                        enabled: enabled,
                                        element_id: item.id || '',
                                        all_attributes: allAttributes
                                    };
                                    
                                    results.extensions.push(extensionInfo);
                                    results.debug_info.push(`확장 프로그램 ${index}: ${name} (ID: ${extensionInfo.id})`);
                                }
                            } catch (itemError) {
                                results.debug_info.push(`확장 프로그램 ${index} 처리 오류: ${itemError.message}`);
                            }
                        });
                    } else {
                        results.debug_info.push('Shadow DOM 접근 실패');
                    }
                } else {
                    results.debug_info.push('extensions-manager 요소를 찾을 수 없음');
                }
                
                // URL에서 현재 확장 프로그램 ID 추출 시도
                const currentUrl = window.location.href;
                const urlMatch = currentUrl.match(/\/([a-z]{32})/);
                if (urlMatch) {
                    results.url_extension_id = urlMatch[1];
                    results.debug_info.push(`URL에서 추출된 ID: ${urlMatch[1]}`);
                }
                
            } catch (error) {
                results.debug_info.push(`전체 오류: ${error.message}`);
            }
            
            return results;
        }
        
        return getExtensionInfo();
        """
        
        extension_info = driver.execute_script(extension_info_script)
        
        logger.info("📊 확장 프로그램 정보 추출 결과:")
        logger.info(f"   - 관리자 페이지 발견: {extension_info.get('manager_found', False)}")
        logger.info(f"   - 총 확장 프로그램 수: {extension_info.get('total_count', 0)}")
        
        # 디버그 정보 출력
        for debug_msg in extension_info.get('debug_info', []):
            logger.info(f"   🐛 {debug_msg}")
        
        # 퍼센티 확장 프로그램 찾기
        percenty_extension = None
        for ext in extension_info.get('extensions', []):
            if '퍼센티' in ext.get('name', ''):
                percenty_extension = ext
                break
        
        if percenty_extension:
            logger.info("============================================================")
            logger.info("✅ 퍼센티 확장 프로그램 발견!")
            logger.info(f"   📛 이름: {percenty_extension.get('name', 'N/A')}")
            logger.info(f"   🆔 ID: {percenty_extension.get('id', 'N/A')}")
            logger.info(f"   🔗 세부정보 ID: {percenty_extension.get('details_id', 'N/A')}")
            logger.info(f"   ✅ 활성화: {percenty_extension.get('enabled', False)}")
            logger.info(f"   🏷️ 요소 ID: {percenty_extension.get('element_id', 'N/A')}")
            logger.info("   📋 모든 속성:")
            for attr_name, attr_value in percenty_extension.get('all_attributes', {}).items():
                logger.info(f"      {attr_name}: {attr_value}")
            logger.info("============================================================")
            
            # 결과를 JSON 파일로 저장
            result_data = {
                'percenty_extension': percenty_extension,
                'all_extensions': extension_info.get('extensions', []),
                'extraction_timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            with open('percenty_extension_id_result.json', 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)
            
            logger.info("💾 결과가 percenty_extension_id_result.json 파일에 저장되었습니다.")
            
            return True
        else:
            logger.error("❌ 퍼센티 확장 프로그램을 찾을 수 없습니다.")
            logger.info("📋 발견된 모든 확장 프로그램:")
            for ext in extension_info.get('extensions', []):
                logger.info(f"   - {ext.get('name', 'Unknown')} (ID: {ext.get('id', 'N/A')})")
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
    success = extract_extension_id()
    
    logger.info("============================================================")
    if success:
        logger.info("✅ 테스트 완료: 퍼센티 확장 프로그램 ID 추출 성공")
    else:
        logger.info("❌ 테스트 완료: 퍼센티 확장 프로그램 ID 추출 실패")
    logger.info("============================================================")