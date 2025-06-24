#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRX 파일을 직접 설치하여 퍼센티 확장 프로그램의 올바른 ID를 확인하는 스크립트

이 스크립트는 기존에 다운로드된 CRX 파일을 사용하여 확장 프로그램을 설치하고
웹스토어 버전과 동일한 ID와 출처를 가지도록 합니다.
"""

import os
import sys
import time
import json
import logging
import shutil
import zipfile
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

class CRXExtensionInstaller:
    def __init__(self):
        self.driver = None
        self.crx_file_path = "jlcdjppbpplpdgfeknhioedbhfceaben.crx"
        self.user_data_dir = os.path.join(os.getcwd(), "chrome_user_data_crx")
        self.extensions_dir = os.path.join(self.user_data_dir, "Default", "Extensions")
        
    def check_crx_file(self):
        """CRX 파일 존재 확인"""
        if not os.path.exists(self.crx_file_path):
            logger.error(f"❌ CRX 파일을 찾을 수 없습니다: {self.crx_file_path}")
            return False
        
        logger.info(f"✅ CRX 파일 발견: {self.crx_file_path}")
        file_size = os.path.getsize(self.crx_file_path)
        logger.info(f"📁 파일 크기: {file_size:,} bytes")
        return True
    
    def extract_crx_to_extensions_dir(self):
        """CRX 파일을 Chrome 확장 프로그램 디렉토리에 추출"""
        try:
            # 확장 프로그램 디렉토리 생성
            os.makedirs(self.extensions_dir, exist_ok=True)
            
            # CRX 파일의 실제 ID 추출 (파일명에서)
            extension_id = os.path.splitext(os.path.basename(self.crx_file_path))[0]
            logger.info(f"🆔 확장 프로그램 ID: {extension_id}")
            
            # 확장 프로그램 설치 디렉토리
            extension_install_dir = os.path.join(self.extensions_dir, extension_id)
            
            # 기존 설치 제거
            if os.path.exists(extension_install_dir):
                shutil.rmtree(extension_install_dir)
                logger.info("🗑️ 기존 확장 프로그램 제거")
            
            # 버전 디렉토리 생성 (임시로 1.0.0 사용)
            version_dir = os.path.join(extension_install_dir, "1.0.0")
            os.makedirs(version_dir, exist_ok=True)
            
            # CRX 파일을 ZIP으로 처리하여 압축 해제
            # CRX 파일은 헤더를 제거하고 ZIP 형태로 압축 해제해야 함
            with open(self.crx_file_path, 'rb') as crx_file:
                # CRX 헤더 건너뛰기
                crx_data = crx_file.read()
                
                # CRX v3 헤더 확인 및 건너뛰기
                if crx_data[:4] == b'Cr24':
                    # CRX v3 형식
                    version = int.from_bytes(crx_data[4:8], 'little')
                    if version == 3:
                        header_size = int.from_bytes(crx_data[8:12], 'little')
                        zip_start = 12 + header_size
                        zip_data = crx_data[zip_start:]
                    else:
                        logger.error(f"❌ 지원하지 않는 CRX 버전: {version}")
                        return False
                else:
                    # 일반 ZIP 파일로 시도
                    zip_data = crx_data
                
                # ZIP 데이터를 임시 파일로 저장하고 압축 해제
                temp_zip_path = "temp_extension.zip"
                with open(temp_zip_path, 'wb') as temp_zip:
                    temp_zip.write(zip_data)
                
                # ZIP 파일 압축 해제
                with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                    zip_ref.extractall(version_dir)
                
                # 임시 파일 제거
                os.remove(temp_zip_path)
                
                logger.info(f"✅ CRX 파일 압축 해제 완료: {version_dir}")
                
                # manifest.json 확인
                manifest_path = os.path.join(version_dir, "manifest.json")
                if os.path.exists(manifest_path):
                    with open(manifest_path, 'r', encoding='utf-8') as f:
                        manifest = json.load(f)
                        logger.info(f"📋 확장 프로그램 이름: {manifest.get('name', 'Unknown')}")
                        logger.info(f"📋 확장 프로그램 버전: {manifest.get('version', 'Unknown')}")
                
                return extension_id
                
        except Exception as e:
            logger.error(f"❌ CRX 파일 압축 해제 실패: {e}")
            return None
    
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
        
        # 확장 프로그램 관련 설정
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
    
    def verify_extension_installation(self, expected_id):
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
                
                // 출처 정보 확인 (다양한 선택자 시도)
                let source = '';
                const sourceSelectors = ['.source', '.location', '.install-location'];
                for (const selector of sourceSelectors) {
                    const sourceElement = ext.shadowRoot.querySelector(selector);
                    if (sourceElement) {
                        source = sourceElement.textContent?.trim() || '';
                        break;
                    }
                }
                
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
                    ext.id.includes('jlcdjppbpplpdgfeknhioedbhfceaben')
                ) || null
            };
            """
            
            result = self.driver.execute_script(extraction_js, expected_id)
            
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
                    'extraction_method': 'crx_installation',
                    'timestamp': datetime.now().isoformat(),
                    'expected_id': expected_id,
                    'percenty_extension': percenty_ext,
                    'all_extensions': result['extensions'],
                    'success': True
                }
                
                with open('crx_extension_result.json', 'w', encoding='utf-8') as f:
                    json.dump(result_data, f, ensure_ascii=False, indent=2)
                
                logger.info("💾 결과가 crx_extension_result.json 파일에 저장되었습니다.")
                return True
            else:
                logger.error("❌ 퍼센티 확장 프로그램을 찾을 수 없습니다.")
                
                # 디버그 정보 저장
                debug_data = {
                    'extraction_method': 'crx_installation_debug',
                    'timestamp': datetime.now().isoformat(),
                    'expected_id': expected_id,
                    'all_extensions': result['extensions'],
                    'success': False
                }
                
                with open('crx_extension_debug.json', 'w', encoding='utf-8') as f:
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
        logger.info("📦 CRX 파일로 퍼센티 확장 프로그램 설치 시작")
        logger.info("=" * 60)
        
        try:
            # CRX 파일 확인
            if not self.check_crx_file():
                return False
            
            # CRX 파일을 확장 프로그램 디렉토리에 추출
            extension_id = self.extract_crx_to_extensions_dir()
            if not extension_id:
                return False
            
            # 브라우저 시작
            if not self.start_browser():
                return False
            
            # 설치 확인
            success = self.verify_extension_installation(extension_id)
            
            return success
            
        except Exception as e:
            logger.error(f"❌ 실행 중 오류 발생: {e}")
            return False
        
        finally:
            self.cleanup()

def main():
    """메인 함수"""
    installer = CRXExtensionInstaller()
    
    try:
        success = installer.run()
        
        logger.info("=" * 60)
        if success:
            logger.info("✅ 테스트 완료: CRX 확장 프로그램 설치 성공")
        else:
            logger.info("❌ 테스트 완료: CRX 확장 프로그램 설치 실패")
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