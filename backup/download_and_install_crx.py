#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
웹스토어에서 퍼센티 확장 프로그램 CRX 파일을 다운로드하고 설치하는 스크립트

이 스크립트는 Chrome Web Store에서 퍼센티 확장 프로그램의 CRX 파일을
직접 다운로드하고 설치하여 올바른 ID와 출처를 확인합니다.
"""

import os
import sys
import time
import json
import logging
import requests
import shutil
import zipfile
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class CRXDownloadInstaller:
    def __init__(self):
        self.driver = None
        self.extension_id = "jlcdjppbpplpdgfeknhioedbhfceaben"  # 퍼센티 확장 프로그램 ID
        self.crx_file_path = f"{self.extension_id}.crx"
        self.user_data_dir = os.path.join(os.getcwd(), "chrome_user_data_download")
        
    def download_crx_file(self):
        """CRX 파일 다운로드"""
        try:
            logger.info("📥 CRX 파일 다운로드 시작...")
            
            # Chrome Web Store CRX 다운로드 URL
            # 이 URL은 공식적이지 않으므로 대안 방법을 사용
            crx_url = f"https://clients2.google.com/service/update2/crx?response=redirect&prodversion=91.0.4472.124&acceptformat=crx2,crx3&x=id%3D{self.extension_id}%26uc"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            logger.info(f"🌐 다운로드 URL: {crx_url}")
            
            response = requests.get(crx_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                with open(self.crx_file_path, 'wb') as f:
                    f.write(response.content)
                
                file_size = len(response.content)
                logger.info(f"✅ CRX 파일 다운로드 완료: {file_size:,} bytes")
                
                # 파일 헤더 확인
                if response.content[:4] == b'Cr24':
                    logger.info("📋 CRX v3 형식 확인")
                elif response.content[:2] == b'PK':
                    logger.info("📋 ZIP 형식 확인")
                else:
                    logger.warning(f"⚠️ 알 수 없는 파일 형식: {response.content[:10]}")
                
                return True
            else:
                logger.error(f"❌ CRX 파일 다운로드 실패: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ CRX 파일 다운로드 중 오류: {e}")
            return False
    
    def extract_crx_file(self):
        """CRX 파일 압축 해제"""
        try:
            if not os.path.exists(self.crx_file_path):
                logger.error(f"❌ CRX 파일을 찾을 수 없습니다: {self.crx_file_path}")
                return False
            
            extract_dir = f"{self.extension_id}_extracted"
            if os.path.exists(extract_dir):
                shutil.rmtree(extract_dir)
            
            os.makedirs(extract_dir, exist_ok=True)
            
            with open(self.crx_file_path, 'rb') as crx_file:
                crx_data = crx_file.read()
                
                # CRX 헤더 처리
                if crx_data[:4] == b'Cr24':
                    # CRX v3 형식
                    version = int.from_bytes(crx_data[4:8], 'little')
                    logger.info(f"📋 CRX 버전: {version}")
                    
                    if version == 3:
                        header_size = int.from_bytes(crx_data[8:12], 'little')
                        zip_start = 12 + header_size
                        zip_data = crx_data[zip_start:]
                        logger.info(f"📋 헤더 크기: {header_size}, ZIP 시작: {zip_start}")
                    else:
                        logger.error(f"❌ 지원하지 않는 CRX 버전: {version}")
                        return False
                elif crx_data[:2] == b'PK':
                    # 이미 ZIP 형식
                    zip_data = crx_data
                    logger.info("📋 ZIP 형식으로 직접 처리")
                else:
                    logger.error(f"❌ 알 수 없는 파일 형식: {crx_data[:10]}")
                    return False
                
                # ZIP 데이터를 임시 파일로 저장하고 압축 해제
                temp_zip_path = "temp_extension.zip"
                with open(temp_zip_path, 'wb') as temp_zip:
                    temp_zip.write(zip_data)
                
                # ZIP 파일 압축 해제
                with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                
                # 임시 파일 제거
                os.remove(temp_zip_path)
                
                logger.info(f"✅ CRX 파일 압축 해제 완료: {extract_dir}")
                
                # manifest.json 확인
                manifest_path = os.path.join(extract_dir, "manifest.json")
                if os.path.exists(manifest_path):
                    with open(manifest_path, 'r', encoding='utf-8') as f:
                        manifest = json.load(f)
                        logger.info(f"📋 확장 프로그램 이름: {manifest.get('name', 'Unknown')}")
                        logger.info(f"📋 확장 프로그램 버전: {manifest.get('version', 'Unknown')}")
                        logger.info(f"📋 매니페스트 버전: {manifest.get('manifest_version', 'Unknown')}")
                
                return extract_dir
                
        except Exception as e:
            logger.error(f"❌ CRX 파일 압축 해제 실패: {e}")
            return None
    
    def setup_chrome_options(self, extension_dir=None):
        """Chrome 옵션 설정"""
        options = Options()
        
        # 사용자 데이터 디렉토리 설정
        options.add_argument(f"--user-data-dir={self.user_data_dir}")
        
        # 압축 해제된 확장 프로그램 로드
        if extension_dir and os.path.exists(extension_dir):
            options.add_argument(f"--load-extension={os.path.abspath(extension_dir)}")
            logger.info(f"✅ 압축 해제된 확장 프로그램 로드: {extension_dir}")
        
        # 기본 Chrome 옵션
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # 확장 프로그램 관련 설정
        options.add_argument("--disable-extensions-file-access-check")
        options.add_argument("--disable-extensions-http-throttling")
        options.add_argument("--allow-running-insecure-content")
        
        return options
    
    def start_browser(self, extension_dir=None):
        """브라우저 시작"""
        try:
            logger.info("🚀 Chrome 브라우저 시작...")
            options = self.setup_chrome_options(extension_dir)
            self.driver = webdriver.Chrome(options=options)
            
            # 자동화 감지 방지
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("✅ 브라우저 시작 성공")
            return True
            
        except Exception as e:
            logger.error(f"❌ 브라우저 시작 실패: {e}")
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
                
                const name = nameElement?.textContent?.trim() || '';
                const id = idElement?.textContent?.trim() || ext.id || '';
                const enabled = enableToggle?.checked || false;
                
                // 출처 정보 확인
                let source = '';
                const sourceSelectors = ['.source', '.location', '.install-location', '.install-source'];
                for (const selector of sourceSelectors) {
                    const sourceElement = ext.shadowRoot.querySelector(selector);
                    if (sourceElement) {
                        source = sourceElement.textContent?.trim() || '';
                        break;
                    }
                }
                
                // 세부 정보에서 추가 정보 확인
                const detailsButton = ext.shadowRoot.querySelector('#detailsButton');
                
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
                    ext.id === arguments[0] ||
                    ext.name.includes('구매대행')
                ) || null
            };
            """
            
            result = self.driver.execute_script(extraction_js, self.extension_id)
            
            if result.get('error'):
                logger.error(f"❌ 확장 프로그램 정보 추출 실패: {result['error']}")
                return False
            
            logger.info(f"📊 총 확장 프로그램 수: {result['total_extensions']}")
            
            # 모든 확장 프로그램 정보 출력
            for ext in result['extensions']:
                logger.info(f"   - {ext['name']} (ID: {ext['id']}, 활성화: {ext['enabled']}, 출처: {ext['source']})")
            
            percenty_ext = result.get('percenty_extension')
            if percenty_ext:
                logger.info("✅ 퍼센티 확장 프로그램 발견:")
                logger.info(f"   - 이름: {percenty_ext['name']}")
                logger.info(f"   - ID: {percenty_ext['id']}")
                logger.info(f"   - 활성화: {percenty_ext['enabled']}")
                logger.info(f"   - 출처: {percenty_ext['source']}")
                
                # 결과 저장
                result_data = {
                    'extraction_method': 'downloaded_crx_installation',
                    'timestamp': datetime.now().isoformat(),
                    'expected_id': self.extension_id,
                    'percenty_extension': percenty_ext,
                    'all_extensions': result['extensions'],
                    'success': True
                }
                
                with open('downloaded_crx_result.json', 'w', encoding='utf-8') as f:
                    json.dump(result_data, f, ensure_ascii=False, indent=2)
                
                logger.info("💾 결과가 downloaded_crx_result.json 파일에 저장되었습니다.")
                return True
            else:
                logger.error("❌ 퍼센티 확장 프로그램을 찾을 수 없습니다.")
                
                # 디버그 정보 저장
                debug_data = {
                    'extraction_method': 'downloaded_crx_debug',
                    'timestamp': datetime.now().isoformat(),
                    'expected_id': self.extension_id,
                    'all_extensions': result['extensions'],
                    'success': False
                }
                
                with open('downloaded_crx_debug.json', 'w', encoding='utf-8') as f:
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
        logger.info("📥 CRX 파일 다운로드 및 설치 시작")
        logger.info("=" * 60)
        
        try:
            # CRX 파일 다운로드
            if not self.download_crx_file():
                return False
            
            # CRX 파일 압축 해제
            extract_dir = self.extract_crx_file()
            if not extract_dir:
                return False
            
            # 브라우저 시작 (압축 해제된 확장 프로그램과 함께)
            if not self.start_browser(extract_dir):
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
    installer = CRXDownloadInstaller()
    
    try:
        success = installer.run()
        
        logger.info("=" * 60)
        if success:
            logger.info("✅ 테스트 완료: CRX 다운로드 및 설치 성공")
        else:
            logger.info("❌ 테스트 완료: CRX 다운로드 및 설치 실패")
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