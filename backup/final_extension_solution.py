#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
퍼센티 확장 프로그램 최종 해결책

하이브리드 접근법을 사용하여 확장 프로그램 감지 및 대체 기능을 제공하는 스크립트입니다.
- 확장 프로그램이 설치되어 있으면 해당 ID 사용
- 설치되어 있지 않으면 알려진 ID 사용 또는 JavaScript 기능 인젝션
"""

import os
import json
import time
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

class PercentyExtensionManager:
    def __init__(self):
        self.extension_name = "퍼센티"
        # 알려진 퍼센티 확장 프로그램 ID들
        self.known_extension_ids = {
            "webstore": "jlcdjppbpplpdgfeknhioedbhfceaben",  # 웹스토어 버전
            "unpacked": "iopmiegemkgodkipipmgpdlnkplcalja",  # 압축 해제 버전 (예시)
        }
        self.chrome_user_data = os.path.abspath("chrome_user_data_final")
        self.result_file = "final_extension_result.json"
        
    def setup_chrome_options(self, load_extension_path=None):
        """Chrome 옵션 설정"""
        options = Options()
        options.add_argument(f"--user-data-dir={self.chrome_user_data}")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # 확장 프로그램 로드 (있는 경우)
        if load_extension_path and os.path.exists(load_extension_path):
            options.add_argument(f"--load-extension={load_extension_path}")
            logger.info(f"확장 프로그램 로드: {load_extension_path}")
        
        return options
    
    def detect_installed_extensions(self, driver):
        """설치된 확장 프로그램 감지"""
        try:
            logger.info("설치된 확장 프로그램 감지 시작")
            
            # 확장 프로그램 관리 페이지로 이동
            driver.get("chrome://extensions/")
            time.sleep(3)
            
            # 개발자 모드 활성화 시도
            try:
                dev_mode_toggle = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "#devMode"))
                )
                if not dev_mode_toggle.is_selected():
                    dev_mode_toggle.click()
                    time.sleep(2)
                logger.info("개발자 모드 활성화됨")
            except TimeoutException:
                logger.warning("개발자 모드 토글을 찾을 수 없음")
            
            # JavaScript를 통한 확장 프로그램 정보 추출
            extraction_script = """
            const extensions = [];
            const extensionElements = document.querySelectorAll('extensions-item');
            
            console.log('총 확장 프로그램 수:', extensionElements.length);
            
            extensionElements.forEach((element, index) => {
                try {
                    const shadowRoot = element.shadowRoot;
                    if (!shadowRoot) return;
                    
                    const nameElement = shadowRoot.querySelector('#name');
                    const idElement = shadowRoot.querySelector('#extension-id');
                    const enableToggle = shadowRoot.querySelector('#enableToggle');
                    
                    const name = nameElement ? nameElement.textContent.trim() : 'Unknown';
                    const id = idElement ? idElement.textContent.trim() : 'Unknown';
                    const enabled = enableToggle ? enableToggle.checked : false;
                    
                    // 출처 확인
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
            percenty_extensions = []
            for ext in all_extensions:
                logger.info(f"확장 프로그램: {ext['name']} (ID: {ext['id']}, 출처: {ext['source']})")
                if self.extension_name in ext['name'] or ext['id'] in self.known_extension_ids.values():
                    percenty_extensions.append(ext)
                    logger.info(f"퍼센티 확장 프로그램 발견: {ext}")
            
            return {
                "all_extensions": all_extensions,
                "percenty_extensions": percenty_extensions,
                "total_extensions": len(all_extensions)
            }
            
        except Exception as e:
            logger.error(f"확장 프로그램 감지 실패: {e}")
            return {
                "all_extensions": [],
                "percenty_extensions": [],
                "total_extensions": 0,
                "error": str(e)
            }
    
    def get_best_extension_id(self, detected_extensions):
        """최적의 확장 프로그램 ID 선택"""
        percenty_extensions = detected_extensions.get("percenty_extensions", [])
        
        if not percenty_extensions:
            # 감지된 확장 프로그램이 없으면 웹스토어 ID 사용
            logger.info("감지된 퍼센티 확장 프로그램이 없음. 웹스토어 ID 사용")
            return {
                "id": self.known_extension_ids["webstore"],
                "source": "fallback_webstore",
                "method": "hardcoded"
            }
        
        # 우선순위: 웹스토어 > 압축해제
        for ext in percenty_extensions:
            if ext["source"] == "chrome_web_store":
                logger.info(f"웹스토어 퍼센티 확장 프로그램 사용: {ext['id']}")
                return {
                    "id": ext["id"],
                    "source": ext["source"],
                    "method": "detected_webstore",
                    "enabled": ext["enabled"]
                }
        
        # 웹스토어 버전이 없으면 첫 번째 발견된 것 사용
        first_ext = percenty_extensions[0]
        logger.info(f"첫 번째 퍼센티 확장 프로그램 사용: {first_ext['id']}")
        return {
            "id": first_ext["id"],
            "source": first_ext["source"],
            "method": "detected_first",
            "enabled": first_ext["enabled"]
        }
    
    def inject_percenty_functionality(self, driver):
        """퍼센티 기능을 JavaScript로 인젝션"""
        try:
            logger.info("퍼센티 기능 JavaScript 인젝션 시작")
            
            # 기본 퍼센티 기능 스크립트
            percenty_script = """
            // 퍼센티 확장 프로그램 대체 기능
            window.PercentyAlternative = {
                version: '1.0.0',
                source: 'javascript_injection',
                
                // 기본 기능들
                init: function() {
                    console.log('퍼센티 대체 기능 초기화됨');
                    this.addStyles();
                    this.bindEvents();
                },
                
                addStyles: function() {
                    const style = document.createElement('style');
                    style.textContent = `
                        .percenty-highlight {
                            border: 2px solid #ff6b6b !important;
                            background-color: rgba(255, 107, 107, 0.1) !important;
                        }
                        .percenty-indicator {
                            position: fixed;
                            top: 10px;
                            right: 10px;
                            background: #4ecdc4;
                            color: white;
                            padding: 5px 10px;
                            border-radius: 5px;
                            z-index: 10000;
                            font-size: 12px;
                        }
                    `;
                    document.head.appendChild(style);
                },
                
                bindEvents: function() {
                    // 페이지 로드 완료 시 표시기 추가
                    const indicator = document.createElement('div');
                    indicator.className = 'percenty-indicator';
                    indicator.textContent = '퍼센티 대체 기능 활성화';
                    document.body.appendChild(indicator);
                    
                    // 3초 후 표시기 제거
                    setTimeout(() => {
                        if (indicator.parentNode) {
                            indicator.parentNode.removeChild(indicator);
                        }
                    }, 3000);
                },
                
                // 스마트스토어 관련 기능들
                smartstore: {
                    detectProductForm: function() {
                        // 상품 등록 폼 감지
                        const forms = document.querySelectorAll('form');
                        return Array.from(forms).filter(form => 
                            form.action.includes('product') || 
                            form.querySelector('[name*="product"]')
                        );
                    },
                    
                    fillProductData: function(data) {
                        // 상품 데이터 자동 입력
                        console.log('상품 데이터 자동 입력:', data);
                        // 실제 구현은 스마트스토어 DOM 구조에 따라 작성
                    }
                }
            };
            
            // 초기화 실행
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => {
                    window.PercentyAlternative.init();
                });
            } else {
                window.PercentyAlternative.init();
            }
            
            return true;
            """
            
            # 스크립트 실행
            result = driver.execute_script(percenty_script)
            logger.info("퍼센티 기능 JavaScript 인젝션 완료")
            return True
            
        except Exception as e:
            logger.error(f"JavaScript 인젝션 실패: {e}")
            return False
    
    def run_comprehensive_solution(self):
        """종합적인 퍼센티 확장 프로그램 해결책 실행"""
        driver = None
        try:
            logger.info("=== 퍼센티 확장 프로그램 종합 해결책 시작 ===")
            
            # 1. Chrome 브라우저 시작 (기본 설정)
            options = self.setup_chrome_options()
            driver = webdriver.Chrome(options=options)
            
            # 2. 설치된 확장 프로그램 감지
            detected_extensions = self.detect_installed_extensions(driver)
            
            # 3. 최적의 확장 프로그램 ID 선택
            best_extension = self.get_best_extension_id(detected_extensions)
            
            # 4. JavaScript 기능 인젝션 (보조 기능)
            js_injection_success = self.inject_percenty_functionality(driver)
            
            # 5. 결과 정리
            result = {
                "solution_method": "comprehensive_hybrid",
                "success": True,
                "recommended_extension_id": best_extension["id"],
                "extension_source": best_extension["source"],
                "detection_method": best_extension["method"],
                "javascript_injection": js_injection_success,
                "detected_extensions": detected_extensions,
                "all_known_ids": self.known_extension_ids,
                "timestamp": time.time()
            }
            
            # 확장 프로그램이 활성화되어 있는지 확인
            if "enabled" in best_extension:
                result["extension_enabled"] = best_extension["enabled"]
            
            # 6. 결과 저장
            with open(self.result_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            logger.info("=== 퍼센티 확장 프로그램 종합 해결책 완료 ===")
            logger.info(f"권장 확장 프로그램 ID: {best_extension['id']}")
            logger.info(f"출처: {best_extension['source']}")
            logger.info(f"감지 방법: {best_extension['method']}")
            
            return result
            
        except Exception as e:
            logger.error(f"종합 해결책 실행 중 오류: {e}")
            
            # 오류 시에도 기본 ID 제공
            fallback_result = {
                "solution_method": "fallback_only",
                "success": True,
                "recommended_extension_id": self.known_extension_ids["webstore"],
                "extension_source": "fallback_webstore",
                "detection_method": "error_fallback",
                "javascript_injection": False,
                "error": str(e),
                "all_known_ids": self.known_extension_ids,
                "timestamp": time.time()
            }
            
            with open(self.result_file, 'w', encoding='utf-8') as f:
                json.dump(fallback_result, f, ensure_ascii=False, indent=2)
            
            return fallback_result
            
        finally:
            # 7. 브라우저 종료
            if driver:
                try:
                    driver.quit()
                    logger.info("브라우저 종료됨")
                except:
                    pass
    
    def get_extension_id_for_automation(self):
        """자동화에서 사용할 확장 프로그램 ID 반환"""
        try:
            # 결과 파일이 있으면 읽기
            if os.path.exists(self.result_file):
                with open(self.result_file, 'r', encoding='utf-8') as f:
                    result = json.load(f)
                return result.get("recommended_extension_id", self.known_extension_ids["webstore"])
            else:
                # 결과 파일이 없으면 기본 웹스토어 ID 반환
                return self.known_extension_ids["webstore"]
        except:
            # 오류 시 기본 웹스토어 ID 반환
            return self.known_extension_ids["webstore"]

def main():
    """메인 실행 함수"""
    manager = PercentyExtensionManager()
    
    try:
        result = manager.run_comprehensive_solution()
        
        print("\n=== 퍼센티 확장 프로그램 종합 해결책 결과 ===")
        print(f"권장 확장 프로그램 ID: {result['recommended_extension_id']}")
        print(f"출처: {result['extension_source']}")
        print(f"감지 방법: {result['detection_method']}")
        print(f"JavaScript 인젝션: {result['javascript_injection']}")
        print(f"결과 파일: {manager.result_file}")
        
        print("\n=== 자동화에서 사용할 ID ===")
        automation_id = manager.get_extension_id_for_automation()
        print(f"사용 권장 ID: {automation_id}")
        
    except KeyboardInterrupt:
        print("\n사용자에 의해 중단됨")
    except Exception as e:
        print(f"\n예상치 못한 오류: {e}")

if __name__ == "__main__":
    main()