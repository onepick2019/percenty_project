#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chrome 엔터프라이즈 정책을 통한 퍼센티 확장 프로그램 강제 설치

Chrome의 엔터프라이즈 정책을 사용하여 확장 프로그램을 자동으로 설치하고
올바른 ID와 출처를 확인하는 스크립트입니다.
"""

import os
import json
import time
import winreg
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ChromeEnterpriseInstaller:
    def __init__(self):
        self.extension_id = "jlcdjppbpplpdgfeknhioedbhfceaben"  # 퍼센티 확장 프로그램 ID
        self.extension_name = "퍼센티"
        self.chrome_user_data = os.path.abspath("chrome_user_data_enterprise")
        self.result_file = "enterprise_extension_result.json"
        self.debug_file = "enterprise_extension_debug.json"
        
    def create_enterprise_policy(self):
        """Chrome 엔터프라이즈 정책을 레지스트리에 설정"""
        try:
            logger.info("Chrome 엔터프라이즈 정책 설정 시작")
            
            # Chrome 정책 레지스트리 키 경로
            policy_key_path = r"SOFTWARE\Policies\Google\Chrome"
            
            # 레지스트리 키 생성/열기
            try:
                key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, policy_key_path)
            except PermissionError:
                logger.warning("관리자 권한이 필요합니다. HKEY_CURRENT_USER로 시도합니다.")
                key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, policy_key_path)
            
            # ExtensionInstallForcelist 정책 설정
            # 형식: "확장프로그램ID;업데이트URL"
            extension_policy = f"{self.extension_id};https://clients2.google.com/service/update2/crx"
            
            # 정책 값 설정
            winreg.SetValueEx(key, "ExtensionInstallForcelist", 0, winreg.REG_MULTI_SZ, [extension_policy])
            
            # 확장 프로그램 설치 허용 정책
            winreg.SetValueEx(key, "ExtensionInstallAllowlist", 0, winreg.REG_MULTI_SZ, [self.extension_id])
            
            winreg.CloseKey(key)
            logger.info("엔터프라이즈 정책 설정 완료")
            return True
            
        except Exception as e:
            logger.error(f"엔터프라이즈 정책 설정 실패: {e}")
            return False
    
    def remove_enterprise_policy(self):
        """Chrome 엔터프라이즈 정책 제거"""
        try:
            logger.info("Chrome 엔터프라이즈 정책 제거 시작")
            
            policy_key_path = r"SOFTWARE\Policies\Google\Chrome"
            
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, policy_key_path, 0, winreg.KEY_SET_VALUE)
            except (FileNotFoundError, PermissionError):
                try:
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, policy_key_path, 0, winreg.KEY_SET_VALUE)
                except FileNotFoundError:
                    logger.info("제거할 정책이 없습니다.")
                    return True
            
            # 정책 값 제거
            try:
                winreg.DeleteValue(key, "ExtensionInstallForcelist")
                logger.info("ExtensionInstallForcelist 정책 제거됨")
            except FileNotFoundError:
                pass
                
            try:
                winreg.DeleteValue(key, "ExtensionInstallAllowlist")
                logger.info("ExtensionInstallAllowlist 정책 제거됨")
            except FileNotFoundError:
                pass
            
            winreg.CloseKey(key)
            logger.info("엔터프라이즈 정책 제거 완료")
            return True
            
        except Exception as e:
            logger.error(f"엔터프라이즈 정책 제거 실패: {e}")
            return False
    
    def setup_chrome_options(self):
        """Chrome 옵션 설정"""
        options = Options()
        options.add_argument(f"--user-data-dir={self.chrome_user_data}")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # 정책 강제 적용을 위한 추가 옵션
        options.add_argument("--force-device-scale-factor=1")
        options.add_argument("--disable-extensions-except")
        
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
                    
                    extensions.push({
                        name: name,
                        id: id,
                        enabled: enabled,
                        source: 'chrome_web_store'  // 엔터프라이즈 정책으로 설치된 경우
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
                logger.info(f"확장 프로그램: {ext['name']} (ID: {ext['id']})")
                if self.extension_name in ext['name'] or ext['id'] == self.extension_id:
                    percenty_extension = ext
                    logger.info(f"퍼센티 확장 프로그램 발견: {ext}")
                    break
            
            result = {
                "extraction_method": "enterprise_policy",
                "success": percenty_extension is not None,
                "percenty_extension": percenty_extension,
                "all_extensions": all_extensions,
                "total_extensions": len(all_extensions)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"확장 프로그램 정보 추출 실패: {e}")
            return {
                "extraction_method": "enterprise_policy_debug",
                "success": False,
                "error": str(e),
                "all_extensions": [],
                "total_extensions": 0
            }
    
    def run_installation(self):
        """엔터프라이즈 정책을 통한 확장 프로그램 설치 및 확인"""
        driver = None
        try:
            logger.info("=== Chrome 엔터프라이즈 정책 설치 시작 ===")
            
            # 1. 엔터프라이즈 정책 설정
            if not self.create_enterprise_policy():
                raise Exception("엔터프라이즈 정책 설정 실패")
            
            # 2. Chrome 옵션 설정
            options = self.setup_chrome_options()
            
            # 3. Chrome 브라우저 시작
            logger.info("Chrome 브라우저 시작")
            driver = webdriver.Chrome(options=options)
            
            # 4. 정책 적용을 위한 대기 시간
            logger.info("정책 적용을 위해 대기 중...")
            time.sleep(10)
            
            # 5. 확장 프로그램 정보 추출
            result = self.extract_extension_info(driver)
            
            # 6. 결과 저장
            with open(self.result_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            if result['success']:
                logger.info("=== 엔터프라이즈 정책 설치 성공 ===")
                logger.info(f"퍼센티 확장 프로그램 정보: {result['percenty_extension']}")
            else:
                logger.error("=== 엔터프라이즈 정책 설치 실패 ===")
                # 디버그 정보 저장
                with open(self.debug_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
            
            return result['success']
            
        except Exception as e:
            logger.error(f"엔터프라이즈 정책 설치 중 오류: {e}")
            
            # 오류 정보 저장
            error_result = {
                "extraction_method": "enterprise_policy_error",
                "success": False,
                "error": str(e),
                "all_extensions": [],
                "total_extensions": 0
            }
            
            with open(self.debug_file, 'w', encoding='utf-8') as f:
                json.dump(error_result, f, ensure_ascii=False, indent=2)
            
            return False
            
        finally:
            # 7. 브라우저 종료
            if driver:
                try:
                    driver.quit()
                    logger.info("브라우저 종료됨")
                except:
                    pass
            
            # 8. 정책 정리 (선택사항)
            # self.remove_enterprise_policy()

def main():
    """메인 실행 함수"""
    installer = ChromeEnterpriseInstaller()
    
    try:
        success = installer.run_installation()
        
        if success:
            print("\n=== 성공: 엔터프라이즈 정책을 통한 퍼센티 확장 프로그램 설치 완료 ===")
            print(f"결과 파일: {installer.result_file}")
        else:
            print("\n=== 실패: 엔터프라이즈 정책을 통한 퍼센티 확장 프로그램 설치 실패 ===")
            print(f"디버그 파일: {installer.debug_file}")
            
    except KeyboardInterrupt:
        print("\n사용자에 의해 중단됨")
    except Exception as e:
        print(f"\n예상치 못한 오류: {e}")
    finally:
        # 정책 정리 옵션
        cleanup = input("\n엔터프라이즈 정책을 제거하시겠습니까? (y/N): ")
        if cleanup.lower() == 'y':
            installer.remove_enterprise_policy()
            print("엔터프라이즈 정책이 제거되었습니다.")

if __name__ == "__main__":
    main()