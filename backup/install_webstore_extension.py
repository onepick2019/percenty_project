#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
웹스토어에서 퍼센티 확장 프로그램을 직접 설치하는 스크립트

이 스크립트는 Chrome Web Store에서 퍼센티 확장 프로그램을 다운로드하고
설치하여 올바른 ID와 출처를 가지도록 합니다.
"""

import os
import sys
import time
import json
import logging
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class WebStoreExtensionInstaller:
    def __init__(self):
        self.driver = None
        self.extension_id = "jlcdjppbpplpdgfeknhioedbhfceaben"  # 퍼센티 확장 프로그램 ID
        self.extension_url = f"https://chrome.google.com/webstore/detail/{self.extension_id}"
        self.user_data_dir = os.path.join(os.getcwd(), "chrome_user_data_webstore")
        
    def setup_chrome_options(self):
        """Chrome 옵션 설정"""
        options = Options()
        
        # 사용자 데이터 디렉토리 설정
        options.add_argument(f"--user-data-dir={self.user_data_dir}")
        
        # 기본 Chrome 옵션
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # 확장 프로그램 설치를 위한 설정
        options.add_argument("--disable-extensions-file-access-check")
        options.add_argument("--disable-extensions-http-throttling")
        options.add_argument("--allow-running-insecure-content")
        
        return options
    
    def start_browser(self):
        """브라우저 시작"""
        try:
            logger.info("🚀 Chrome 브라우저 시작...")
            options = self.setup_chrome_options()
            self.driver = webdriver.Chrome(options=options)
            
            # 자동화 감지 방지
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("✅ 브라우저 시작 성공")
            return True
            
        except Exception as e:
            logger.error(f"❌ 브라우저 시작 실패: {e}")
            return False
    
    def install_extension_from_webstore(self):
        """웹스토어에서 확장 프로그램 설치"""
        try:
            logger.info("🌐 Chrome Web Store로 이동...")
            self.driver.get(self.extension_url)
            time.sleep(3)
            
            # 페이지 로드 확인
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            logger.info("📄 웹스토어 페이지 로드 완료")
            
            # "Chrome에 추가" 버튼 찾기 및 클릭
            try:
                # 다양한 선택자로 "Chrome에 추가" 버튼 찾기
                add_button_selectors = [
                    "div[role='button'][aria-label*='Chrome에 추가']",
                    "div[role='button'][aria-label*='Add to Chrome']",
                    "button[aria-label*='Chrome에 추가']",
                    "button[aria-label*='Add to Chrome']",
                    "div.webstore-test-button-label",
                    "div[jsaction*='click']"
                ]
                
                add_button = None
                for selector in add_button_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            text = element.get_attribute('textContent') or element.get_attribute('aria-label') or ''
                            if 'Chrome에 추가' in text or 'Add to Chrome' in text:
                                add_button = element
                                break
                        if add_button:
                            break
                    except:
                        continue
                
                if add_button:
                    logger.info("🔘 'Chrome에 추가' 버튼 발견")
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", add_button)
                    time.sleep(1)
                    
                    # 클릭 시도
                    try:
                        add_button.click()
                    except:
                        # JavaScript로 클릭 시도
                        self.driver.execute_script("arguments[0].click();", add_button)
                    
                    logger.info("✅ 'Chrome에 추가' 버튼 클릭 성공")
                    time.sleep(2)
                    
                    # 확인 대화상자 처리
                    try:
                        # "확장 프로그램 추가" 버튼 찾기
                        confirm_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '확장 프로그램 추가') or contains(text(), 'Add extension')]"))
                        )
                        confirm_button.click()
                        logger.info("✅ 확장 프로그램 추가 확인")
                        time.sleep(3)
                        
                    except:
                        logger.warning("⚠️ 확인 대화상자를 찾을 수 없음 (이미 설치되었을 수 있음)")
                    
                else:
                    logger.warning("⚠️ 'Chrome에 추가' 버튼을 찾을 수 없음 (이미 설치되었을 수 있음)")
                    
            except Exception as e:
                logger.warning(f"⚠️ 설치 버튼 처리 중 오류: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 웹스토어에서 확장 프로그램 설치 실패: {e}")
            return False
    
    def verify_extension_installation(self):
        """확장 프로그램 설치 확인"""
        try:
            logger.info("🔍 확장 프로그램 설치 확인...")
            
            # 확장 프로그램 관리 페이지로 이동
            self.driver.get("chrome://extensions/")
            time.sleep(3)
            
            # 개발자 모드 활성화
            try:
                dev_mode_js = """
                const toggleButton = document.querySelector('extensions-manager')
                    ?.shadowRoot?.querySelector('extensions-toolbar')
                    ?.shadowRoot?.querySelector('#devMode');
                if (toggleButton && !toggleButton.checked) {
                    toggleButton.click();
                    return 'activated';
                }
                return toggleButton?.checked ? 'already_active' : 'not_found';
                """
                
                result = self.driver.execute_script(dev_mode_js)
                logger.info(f"🛠️ 개발자 모드: {result}")
                time.sleep(2)
                
            except Exception as e:
                logger.warning(f"⚠️ 개발자 모드 활성화 실패: {e}")
            
            # 확장 프로그램 정보 추출
            extraction_js = """
            const manager = document.querySelector('extensions-manager');
            if (!manager || !manager.shadowRoot) {
                return {error: 'extensions-manager not found'};
            }
            
            const itemList = manager.shadowRoot.querySelector('extensions-item-list');
            if (!itemList || !itemList.shadowRoot) {
                return {error: 'extensions-item-list not found'};
            }
            
            const extensions = itemList.shadowRoot.querySelectorAll('extensions-item');
            const results = [];
            
            extensions.forEach(ext => {
                if (!ext.shadowRoot) return;
                
                const nameElement = ext.shadowRoot.querySelector('#name');
                const idElement = ext.shadowRoot.querySelector('#extension-id');
                const enableToggle = ext.shadowRoot.querySelector('#enableToggle');
                const detailsButton = ext.shadowRoot.querySelector('#detailsButton');
                
                const name = nameElement?.textContent?.trim() || '';
                const id = idElement?.textContent?.trim() || ext.id || '';
                const enabled = enableToggle?.checked || false;
                
                // 출처 정보 확인
                const sourceElement = ext.shadowRoot.querySelector('.source');
                const source = sourceElement?.textContent?.trim() || '';
                
                results.push({
                    name: name,
                    id: id,
                    enabled: enabled,
                    source: source
                });
            });
            
            return {
                total_extensions: results.length,
                extensions: results,
                percenty_extension: results.find(ext => 
                    ext.name.includes('퍼센티') || 
                    ext.id === 'jlcdjppbpplpdgfeknhioedbhfceaben'
                ) || null
            };
            """
            
            result = self.driver.execute_script(extraction_js)
            
            if result.get('error'):
                logger.error(f"❌ 확장 프로그램 정보 추출 실패: {result['error']}")
                return False
            
            logger.info(f"📊 총 확장 프로그램 수: {result['total_extensions']}")
            
            percenty_ext = result.get('percenty_extension')
            if percenty_ext:
                logger.info("✅ 퍼센티 확장 프로그램 발견:")
                logger.info(f"   - 이름: {percenty_ext['name']}")
                logger.info(f"   - ID: {percenty_ext['id']}")
                logger.info(f"   - 활성화: {percenty_ext['enabled']}")
                logger.info(f"   - 출처: {percenty_ext['source']}")
                
                # 결과 저장
                result_data = {
                    'extraction_method': 'webstore_installation',
                    'timestamp': datetime.now().isoformat(),
                    'percenty_extension': percenty_ext,
                    'all_extensions': result['extensions'],
                    'success': True
                }
                
                with open('webstore_extension_result.json', 'w', encoding='utf-8') as f:
                    json.dump(result_data, f, ensure_ascii=False, indent=2)
                
                logger.info("💾 결과가 webstore_extension_result.json 파일에 저장되었습니다.")
                return True
            else:
                logger.error("❌ 퍼센티 확장 프로그램을 찾을 수 없습니다.")
                
                # 디버그 정보 저장
                debug_data = {
                    'extraction_method': 'webstore_installation_debug',
                    'timestamp': datetime.now().isoformat(),
                    'all_extensions': result['extensions'],
                    'success': False
                }
                
                with open('webstore_extension_debug.json', 'w', encoding='utf-8') as f:
                    json.dump(debug_data, f, ensure_ascii=False, indent=2)
                
                return False
                
        except Exception as e:
            logger.error(f"❌ 확장 프로그램 설치 확인 실패: {e}")
            return False
    
    def cleanup(self):
        """정리 작업"""
        if self.driver:
            logger.info("🔚 브라우저 종료...")
            try:
                self.driver.quit()
            except:
                pass
            time.sleep(2)
    
    def run(self):
        """메인 실행 함수"""
        logger.info("=" * 60)
        logger.info("🌐 웹스토어에서 퍼센티 확장 프로그램 설치 시작")
        logger.info("=" * 60)
        
        try:
            # 브라우저 시작
            if not self.start_browser():
                return False
            
            # 웹스토어에서 확장 프로그램 설치
            if not self.install_extension_from_webstore():
                return False
            
            # 설치 확인
            success = self.verify_extension_installation()
            
            return success
            
        except Exception as e:
            logger.error(f"❌ 실행 중 오류 발생: {e}")
            return False
        
        finally:
            self.cleanup()

def main():
    """메인 함수"""
    installer = WebStoreExtensionInstaller()
    
    try:
        success = installer.run()
        
        logger.info("=" * 60)
        if success:
            logger.info("✅ 테스트 완료: 웹스토어 확장 프로그램 설치 성공")
        else:
            logger.info("❌ 테스트 완료: 웹스토어 확장 프로그램 설치 실패")
        logger.info("=" * 60)
        
        return success
        
    except KeyboardInterrupt:
        logger.info("\n⚠️ 사용자에 의해 중단됨")
        installer.cleanup()
        return False
    except Exception as e:
        logger.error(f"❌ 예상치 못한 오류: {e}")
        installer.cleanup()
        return False

if __name__ == "__main__":
    main()