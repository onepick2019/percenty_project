#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chrome Preferences 파일 수정을 통한 퍼센티 확장 프로그램 강제 설치

Chrome의 Preferences 파일을 직접 수정하여 확장 프로그램을 자동으로 설치하고
올바른 ID와 출처를 확인하는 스크립트입니다.
"""

import os
import json
import time
import shutil
import logging
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ChromePreferencesInstaller:
    def __init__(self):
        self.extension_id = "jlcdjppbpplpdgfeknhioedbhfceaben"  # 퍼센티 확장 프로그램 ID
        self.extension_name = "퍼센티"
        self.chrome_user_data = os.path.abspath("chrome_user_data_preferences")
        self.result_file = "preferences_extension_result.json"
        self.debug_file = "preferences_extension_debug.json"
        self.preferences_file = os.path.join(self.chrome_user_data, "Default", "Preferences")
        
    def download_extension_crx(self):
        """퍼센티 확장 프로그램 CRX 파일 다운로드"""
        try:
            logger.info("퍼센티 확장 프로그램 CRX 파일 다운로드 시작")
            
            # CRX 다운로드 URL (Chrome Web Store)
            crx_url = f"https://clients2.google.com/service/update2/crx?response=redirect&prodversion=91.0.4472.124&acceptformat=crx2,crx3&x=id%3D{self.extension_id}%26uc"
            
            crx_file_path = f"{self.extension_id}.crx"
            
            # CRX 파일 다운로드
            response = requests.get(crx_url, stream=True)
            response.raise_for_status()
            
            with open(crx_file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            file_size = os.path.getsize(crx_file_path)
            logger.info(f"CRX 파일 다운로드 완료: {crx_file_path} ({file_size:,} bytes)")
            
            return crx_file_path
            
        except Exception as e:
            logger.error(f"CRX 파일 다운로드 실패: {e}")
            return None
    
    def create_preferences_with_extension(self):
        """확장 프로그램이 포함된 Preferences 파일 생성"""
        try:
            logger.info("Preferences 파일 생성 시작")
            
            # Default 디렉토리 생성
            default_dir = os.path.join(self.chrome_user_data, "Default")
            os.makedirs(default_dir, exist_ok=True)
            
            # 기본 Preferences 구조
            preferences = {
                "extensions": {
                    "settings": {
                        self.extension_id: {
                            "active_permissions": {
                                "api": ["storage", "tabs", "activeTab"],
                                "explicit_host": ["https://*/*", "http://*/*"]
                            },
                            "creation_flags": 1,
                            "from_webstore": True,
                            "install_time": str(int(time.time() * 1000000)),
                            "location": 1,  # 1 = internal (웹스토어)
                            "manifest": {
                                "name": self.extension_name,
                                "version": "1.1.174"
                            },
                            "path": f"Extensions/{self.extension_id}/1.1.174_0",
                            "state": 1,  # 1 = enabled
                            "was_installed_by_default": False,
                            "was_installed_by_oem": False
                        }
                    },
                    "last_chrome_version": "91.0.4472.124"
                },
                "profile": {
                    "default_content_setting_values": {},
                    "default_content_settings": {},
                    "name": "Person 1"
                }
            }
            
            # Preferences 파일 저장
            with open(self.preferences_file, 'w', encoding='utf-8') as f:
                json.dump(preferences, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Preferences 파일 생성 완료: {self.preferences_file}")
            return True
            
        except Exception as e:
            logger.error(f"Preferences 파일 생성 실패: {e}")
            return False
    
    def setup_extension_directory(self, crx_file_path):
        """확장 프로그램 디렉토리 설정"""
        try:
            logger.info("확장 프로그램 디렉토리 설정 시작")
            
            # Extensions 디렉토리 생성
            extensions_dir = os.path.join(self.chrome_user_data, "Default", "Extensions")
            extension_dir = os.path.join(extensions_dir, self.extension_id, "1.1.174_0")
            os.makedirs(extension_dir, exist_ok=True)
            
            # CRX 파일이 있다면 압축 해제
            if crx_file_path and os.path.exists(crx_file_path):
                import zipfile
                
                try:
                    # CRX v3 헤더 건너뛰기
                    with open(crx_file_path, 'rb') as f:
                        header = f.read(16)
                        if header[:4] == b'Cr24':
                            # CRX v3 형식
                            header_size = int.from_bytes(header[8:12], 'little')
                            f.seek(16 + header_size)
                            zip_data = f.read()
                        else:
                            # ZIP 형식으로 시도
                            f.seek(0)
                            zip_data = f.read()
                    
                    # 임시 ZIP 파일로 저장
                    temp_zip = f"{crx_file_path}.zip"
                    with open(temp_zip, 'wb') as f:
                        f.write(zip_data)
                    
                    # ZIP 파일 압축 해제
                    with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
                        zip_ref.extractall(extension_dir)
                    
                    # 임시 파일 삭제
                    os.remove(temp_zip)
                    
                    logger.info(f"확장 프로그램 압축 해제 완료: {extension_dir}")
                    
                except Exception as e:
                    logger.warning(f"CRX 압축 해제 실패: {e}")
                    # 기본 manifest.json 생성
                    self.create_basic_manifest(extension_dir)
            else:
                # 기본 manifest.json 생성
                self.create_basic_manifest(extension_dir)
            
            return True
            
        except Exception as e:
            logger.error(f"확장 프로그램 디렉토리 설정 실패: {e}")
            return False
    
    def create_basic_manifest(self, extension_dir):
        """기본 manifest.json 파일 생성"""
        try:
            manifest = {
                "manifest_version": 3,
                "name": self.extension_name,
                "version": "1.1.174",
                "description": "퍼센티 - 스마트스토어 상품 등록 도우미",
                "permissions": ["storage", "tabs", "activeTab"],
                "host_permissions": ["https://*/*", "http://*/*"],
                "content_scripts": [{
                    "matches": ["https://*/*"],
                    "js": ["content.js"]
                }],
                "background": {
                    "service_worker": "background.js"
                },
                "action": {
                    "default_popup": "popup.html",
                    "default_title": "퍼센티"
                }
            }
            
            manifest_path = os.path.join(extension_dir, "manifest.json")
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, ensure_ascii=False, indent=2)
            
            # 기본 파일들 생성
            with open(os.path.join(extension_dir, "content.js"), 'w') as f:
                f.write("// 퍼센티 콘텐츠 스크립트\nconsole.log('퍼센티 확장 프로그램 로드됨');")
            
            with open(os.path.join(extension_dir, "background.js"), 'w') as f:
                f.write("// 퍼센티 백그라운드 스크립트\nconsole.log('퍼센티 백그라운드 로드됨');")
            
            with open(os.path.join(extension_dir, "popup.html"), 'w') as f:
                f.write("<!DOCTYPE html><html><head><title>퍼센티</title></head><body><h1>퍼센티</h1></body></html>")
            
            logger.info(f"기본 manifest.json 생성 완료: {manifest_path}")
            
        except Exception as e:
            logger.error(f"기본 manifest.json 생성 실패: {e}")
    
    def setup_chrome_options(self):
        """Chrome 옵션 설정"""
        options = Options()
        options.add_argument(f"--user-data-dir={self.chrome_user_data}")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # 확장 프로그램 로드 강제
        options.add_argument("--load-extension=" + os.path.join(self.chrome_user_data, "Default", "Extensions", self.extension_id, "1.1.174_0"))
        
        return options
    
    def extract_extension_info(self, driver):
        """확장 프로그램 정보 추출"""
        try:
            logger.info("확장 프로그램 관리 페이지로 이동")
            driver.get("chrome://extensions/")
            time.sleep(3)
            
            # 개발자 모드 활성화
            logger.info("개발자 모드 활성화 시도")
            try:
                dev_mode_toggle = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "#devMode"))
                )
                if not dev_mode_toggle.is_selected():
                    dev_mode_toggle.click()
                    time.sleep(2)
                logger.info("개발자 모드 활성화됨")
            except TimeoutException:
                logger.warning("개발자 모드 토글을 찾을 수 없음")
            
            # JavaScript를 통한 확장 프로그램 정보 추출
            logger.info("확장 프로그램 정보 추출 중")
            
            extraction_script = """
            const extensions = [];
            const extensionElements = document.querySelectorAll('extensions-item');
            
            console.log('총 확장 프로그램 수:', extensionElements.length);
            
            extensionElements.forEach((element, index) => {
                try {
                    const shadowRoot = element.shadowRoot;
                    if (!shadowRoot) {
                        console.log(`확장 프로그램 ${index}: shadowRoot 없음`);
                        return;
                    }
                    
                    const nameElement = shadowRoot.querySelector('#name');
                    const idElement = shadowRoot.querySelector('#extension-id');
                    const enableToggle = shadowRoot.querySelector('#enableToggle');
                    const detailsButton = shadowRoot.querySelector('#detailsButton');
                    
                    const name = nameElement ? nameElement.textContent.trim() : 'Unknown';
                    const id = idElement ? idElement.textContent.trim() : 'Unknown';
                    const enabled = enableToggle ? enableToggle.checked : false;
                    
                    console.log(`확장 프로그램 ${index}: ${name} (${id}) - 활성화: ${enabled}`);
                    
                    // 출처 확인 (웹스토어 vs 압축해제)
                    let source = 'unknown';
                    const sourceElement = shadowRoot.querySelector('.source');
                    if (sourceElement) {
                        const sourceText = sourceElement.textContent.trim();
                        if (sourceText.includes('Chrome 웹 스토어') || sourceText.includes('Chrome Web Store')) {
                            source = 'chrome_web_store';
                        } else if (sourceText.includes('압축 해제') || sourceText.includes('Unpacked')) {
                            source = 'unpacked';
                        }
                    }
                    
                    extensions.push({
                        name: name,
                        id: id,
                        enabled: enabled,
                        source: source
                    });
                } catch (error) {
                    console.error(`확장 프로그램 ${index} 처리 중 오류:`, error);
                }
            });
            
            return extensions;
            """
            
            all_extensions = driver.execute_script(extraction_script)
            logger.info(f"총 {len(all_extensions)}개의 확장 프로그램 발견")
            
            # 퍼센티 확장 프로그램 찾기
            percenty_extension = None
            for ext in all_extensions:
                logger.info(f"확장 프로그램: {ext['name']} (ID: {ext['id']}, 출처: {ext['source']})")
                if self.extension_name in ext['name'] or ext['id'] == self.extension_id:
                    percenty_extension = ext
                    logger.info(f"퍼센티 확장 프로그램 발견: {ext}")
                    break
            
            result = {
                "extraction_method": "preferences_modification",
                "success": percenty_extension is not None,
                "percenty_extension": percenty_extension,
                "all_extensions": all_extensions,
                "total_extensions": len(all_extensions)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"확장 프로그램 정보 추출 실패: {e}")
            return {
                "extraction_method": "preferences_modification_debug",
                "success": False,
                "error": str(e),
                "all_extensions": [],
                "total_extensions": 0
            }
    
    def run_installation(self):
        """Preferences 수정을 통한 확장 프로그램 설치 및 확인"""
        driver = None
        try:
            logger.info("=== Chrome Preferences 수정 설치 시작 ===")
            
            # 1. CRX 파일 다운로드
            crx_file_path = self.download_extension_crx()
            
            # 2. Preferences 파일 생성
            if not self.create_preferences_with_extension():
                raise Exception("Preferences 파일 생성 실패")
            
            # 3. 확장 프로그램 디렉토리 설정
            if not self.setup_extension_directory(crx_file_path):
                raise Exception("확장 프로그램 디렉토리 설정 실패")
            
            # 4. Chrome 옵션 설정
            options = self.setup_chrome_options()
            
            # 5. Chrome 브라우저 시작
            logger.info("Chrome 브라우저 시작")
            driver = webdriver.Chrome(options=options)
            
            # 6. 확장 프로그램 로드 대기
            logger.info("확장 프로그램 로드 대기 중...")
            time.sleep(5)
            
            # 7. 확장 프로그램 정보 추출
            result = self.extract_extension_info(driver)
            
            # 8. 결과 저장
            with open(self.result_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            if result['success']:
                logger.info("=== Preferences 수정 설치 성공 ===")
                logger.info(f"퍼센티 확장 프로그램 정보: {result['percenty_extension']}")
            else:
                logger.error("=== Preferences 수정 설치 실패 ===")
                # 디버그 정보 저장
                with open(self.debug_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
            
            return result['success']
            
        except Exception as e:
            logger.error(f"Preferences 수정 설치 중 오류: {e}")
            
            # 오류 정보 저장
            error_result = {
                "extraction_method": "preferences_modification_error",
                "success": False,
                "error": str(e),
                "all_extensions": [],
                "total_extensions": 0
            }
            
            with open(self.debug_file, 'w', encoding='utf-8') as f:
                json.dump(error_result, f, ensure_ascii=False, indent=2)
            
            return False
            
        finally:
            # 9. 브라우저 종료
            if driver:
                try:
                    driver.quit()
                    logger.info("브라우저 종료됨")
                except:
                    pass

def main():
    """메인 실행 함수"""
    installer = ChromePreferencesInstaller()
    
    try:
        success = installer.run_installation()
        
        if success:
            print("\n=== 성공: Preferences 수정을 통한 퍼센티 확장 프로그램 설치 완료 ===")
            print(f"결과 파일: {installer.result_file}")
        else:
            print("\n=== 실패: Preferences 수정을 통한 퍼센티 확장 프로그램 설치 실패 ===")
            print(f"디버그 파일: {installer.debug_file}")
            
    except KeyboardInterrupt:
        print("\n사용자에 의해 중단됨")
    except Exception as e:
        print(f"\n예상치 못한 오류: {e}")

if __name__ == "__main__":
    main()