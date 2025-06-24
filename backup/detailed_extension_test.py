#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
상세한 확장 프로그램 정보 추출 테스트

확장 프로그램이 로드되었지만 ID가 인식되지 않는 문제를 해결하기 위해
더 상세한 정보를 추출합니다.
"""

import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_detailed_extension_info():
    """
    상세한 확장 프로그램 정보 추출 테스트
    """
    driver = None
    
    try:
        # Chrome 옵션 설정
        chrome_options = ChromeOptions()
        
        # 기본 설정
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        
        # Chrome 137+ 확장 프로그램 로드 지원을 위한 플래그 추가
        chrome_options.add_argument("--disable-features=DisableLoadExtensionCommandLineSwitch")
        
        # 압축 해제된 확장 프로그램 디렉토리 로드
        extension_dir = os.path.join(os.path.dirname(__file__), "percenty_extension")
        
        if os.path.exists(extension_dir):
            chrome_options.add_argument(f"--load-extension={extension_dir}")
            logging.info(f"✅ 압축 해제된 확장 프로그램 로드: {extension_dir}")
        else:
            logging.error(f"❌ 확장 프로그램 디렉토리를 찾을 수 없습니다: {extension_dir}")
            return False
        
        # 브라우저 시작
        logging.info("🚀 Chrome 브라우저 시작...")
        driver = webdriver.Chrome(options=chrome_options)
        logging.info("✅ 브라우저 시작 성공")
        
        # 확장 프로그램 페이지로 이동
        logging.info("📋 확장 프로그램 관리 페이지로 이동...")
        driver.get("chrome://extensions/")
        time.sleep(3)
        
        # 개발자 모드 활성화
        try:
            logging.info("🛠️ 개발자 모드 활성화 시도...")
            
            # 개발자 모드 토글 찾기 (여러 방법 시도)
            dev_mode_selectors = [
                "#devMode",
                "[id='devMode']",
                "cr-toggle#devMode",
                "extensions-toggle-row#devMode cr-toggle",
                "[aria-label*='개발자']",
                "[aria-label*='Developer']"
            ]
            
            dev_mode_toggle = None
            for selector in dev_mode_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        dev_mode_toggle = elements[0]
                        logging.info(f"✅ 개발자 모드 토글 발견: {selector}")
                        break
                except:
                    continue
            
            if dev_mode_toggle:
                # 토글이 비활성화되어 있으면 클릭
                is_checked = driver.execute_script("""
                    var toggle = arguments[0];
                    if (toggle.tagName.toLowerCase() === 'cr-toggle') {
                        return toggle.checked;
                    }
                    return toggle.checked || toggle.getAttribute('aria-pressed') === 'true';
                """, dev_mode_toggle)
                
                if not is_checked:
                    dev_mode_toggle.click()
                    logging.info("✅ 개발자 모드 활성화됨")
                    time.sleep(2)
                else:
                    logging.info("ℹ️ 개발자 모드가 이미 활성화되어 있음")
            else:
                logging.warning("⚠️ 개발자 모드 토글을 찾을 수 없음")
                
        except Exception as e:
            logging.error(f"❌ 개발자 모드 활성화 오류: {e}")
        
        # 페이지 새로고침
        driver.refresh()
        time.sleep(3)
        
        # 확장 프로그램 카드 찾기
        logging.info("🔍 확장 프로그램 카드 검색...")
        
        # Shadow DOM을 통한 확장 프로그램 정보 추출
        extension_info = driver.execute_script("""
            function findExtensions() {
                var results = [];
                
                // extensions-manager 요소 찾기
                var extensionsManager = document.querySelector('extensions-manager');
                if (!extensionsManager || !extensionsManager.shadowRoot) {
                    return {error: 'extensions-manager not found or no shadowRoot'};
                }
                
                // extensions-item-list 찾기
                var itemList = extensionsManager.shadowRoot.querySelector('extensions-item-list');
                if (!itemList || !itemList.shadowRoot) {
                    return {error: 'extensions-item-list not found or no shadowRoot'};
                }
                
                // 모든 extensions-item 찾기
                var extensionItems = itemList.shadowRoot.querySelectorAll('extensions-item');
                
                for (var i = 0; i < extensionItems.length; i++) {
                    var item = extensionItems[i];
                    if (!item.shadowRoot) continue;
                    
                    var nameElement = item.shadowRoot.querySelector('#name');
                    var idElement = item.shadowRoot.querySelector('#extension-id');
                    var enableToggle = item.shadowRoot.querySelector('#enableToggle');
                    
                    var extensionData = {
                        name: nameElement ? nameElement.textContent.trim() : 'Unknown',
                        id: idElement ? idElement.textContent.trim() : item.id || 'No ID',
                        enabled: enableToggle ? enableToggle.checked : false,
                        element_id: item.id || 'no-element-id'
                    };
                    
                    results.push(extensionData);
                }
                
                return {
                    extensions: results,
                    total_count: results.length,
                    manager_found: true
                };
            }
            
            return findExtensions();
        """)
        
        logging.info(f"📊 확장 프로그램 정보: {extension_info}")
        
        # 퍼센티 확장 프로그램 찾기
        percenty_found = False
        if 'extensions' in extension_info:
            for ext in extension_info['extensions']:
                name = ext.get('name', '').lower()
                if 'percenty' in name or 'percent' in name:
                    logging.info(f"✅ 퍼센티 확장 프로그램 발견: {ext}")
                    percenty_found = True
                else:
                    logging.info(f"ℹ️ 다른 확장 프로그램: {ext}")
        
        if not percenty_found:
            logging.warning("⚠️ 퍼센티 확장 프로그램을 찾을 수 없습니다.")
            
            # 대체 방법: 모든 확장 프로그램 요소 검사
            logging.info("🔍 대체 방법으로 확장 프로그램 검색...")
            
            all_extensions = driver.execute_script("""
                var allElements = document.querySelectorAll('*');
                var results = [];
                
                for (var i = 0; i < allElements.length; i++) {
                    var element = allElements[i];
                    var text = element.textContent || '';
                    var id = element.id || '';
                    var className = element.className || '';
                    
                    if (text.toLowerCase().includes('percenty') || 
                        id.toLowerCase().includes('percenty') ||
                        className.toLowerCase().includes('percenty')) {
                        results.push({
                            tag: element.tagName,
                            id: id,
                            className: className,
                            text: text.substring(0, 100)
                        });
                    }
                }
                
                return results;
            """)
            
            if all_extensions:
                logging.info(f"🎯 퍼센티 관련 요소들: {all_extensions}")
            else:
                logging.warning("⚠️ 퍼센티 관련 요소를 전혀 찾을 수 없습니다.")
        
        # manifest.json 정보 확인
        manifest_path = os.path.join(extension_dir, "manifest.json")
        if os.path.exists(manifest_path):
            try:
                import json
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest_data = json.load(f)
                logging.info(f"📋 Manifest 정보: {manifest_data.get('name', 'Unknown')} v{manifest_data.get('version', 'Unknown')}")
            except Exception as e:
                logging.error(f"❌ Manifest 읽기 오류: {e}")
        
        return len(extension_info.get('extensions', [])) > 0
        
    except Exception as e:
        logging.error(f"❌ 테스트 중 오류 발생: {e}")
        return False
        
    finally:
        if driver:
            logging.info("🔚 브라우저 종료...")
            time.sleep(3)  # 더 긴 대기 시간
            driver.quit()

if __name__ == "__main__":
    logging.info("=" * 60)
    logging.info("🧪 상세한 확장 프로그램 정보 추출 테스트 시작")
    logging.info("=" * 60)
    
    success = test_detailed_extension_info()
    
    logging.info("=" * 60)
    if success:
        logging.info("✅ 테스트 완료: 확장 프로그램 정보를 성공적으로 추출했습니다.")
    else:
        logging.info("❌ 테스트 완료: 확장 프로그램 정보 추출에 실패했습니다.")
    logging.info("=" * 60)