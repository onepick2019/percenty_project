#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 확장 프로그램 로드 테스트

Chrome 137에서 CRX 파일 로드가 정상적으로 작동하는지 확인합니다.
"""

import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_extension_load():
    """
    확장 프로그램 로드 테스트
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
        
        # 퍼센티 확장 프로그램 로드
        extension_dir = os.path.join(os.path.dirname(__file__), "percenty_extension")
        extension_path = os.path.join(extension_dir, "percenty_extension_with_key.crx")
        
        if os.path.exists(extension_path):
            chrome_options.add_extension(extension_path)
            logging.info(f"✅ CRX 파일 로드: {extension_path}")
        else:
            logging.error(f"❌ CRX 파일을 찾을 수 없습니다: {extension_path}")
            return False
        
        # 브라우저 시작
        logging.info("🚀 Chrome 브라우저 시작...")
        driver = webdriver.Chrome(options=chrome_options)
        logging.info("✅ 브라우저 시작 성공")
        
        # 확장 프로그램 페이지로 이동
        logging.info("📋 확장 프로그램 관리 페이지로 이동...")
        driver.get("chrome://extensions/")
        time.sleep(3)
        
        # 페이지 소스 확인
        page_source = driver.page_source
        logging.info(f"📄 페이지 소스 길이: {len(page_source)}")
        
        # 퍼센티 확장 프로그램 ID 확인
        percenty_id = "jlcdjppbpplpdgfeknhioedbhfceaben"
        if percenty_id in page_source:
            logging.info(f"✅ 퍼센티 확장 프로그램 ID 발견: {percenty_id}")
            return True
        else:
            logging.warning(f"⚠️ 퍼센티 확장 프로그램 ID를 찾을 수 없습니다: {percenty_id}")
        
        # 일반적인 확장 프로그램 키워드 확인
        extension_keywords = ["extension", "확장", "percenty", "Percenty"]
        found_keywords = []
        
        for keyword in extension_keywords:
            if keyword.lower() in page_source.lower():
                found_keywords.append(keyword)
        
        if found_keywords:
            logging.info(f"🔍 발견된 확장 프로그램 관련 키워드: {found_keywords}")
        else:
            logging.warning("⚠️ 확장 프로그램 관련 키워드를 찾을 수 없습니다.")
        
        # JavaScript로 확장 프로그램 정보 확인
        try:
            extension_info = driver.execute_script("""
                // 확장 프로그램 관리 API 확인
                if (typeof chrome !== 'undefined' && chrome.management) {
                    return {
                        management_available: true,
                        page_url: window.location.href,
                        page_title: document.title
                    };
                } else {
                    return {
                        management_available: false,
                        page_url: window.location.href,
                        page_title: document.title
                    };
                }
            """)
            
            logging.info(f"🔧 JavaScript 확장 프로그램 정보: {extension_info}")
            
        except Exception as e:
            logging.error(f"❌ JavaScript 실행 오류: {e}")
        
        # 개발자 모드 확인
        try:
            dev_mode_elements = driver.find_elements("css selector", "[id*='dev'], [class*='dev'], [data-test-id*='dev']")
            logging.info(f"🛠️ 개발자 모드 관련 요소 개수: {len(dev_mode_elements)}")
            
            if dev_mode_elements:
                for i, element in enumerate(dev_mode_elements[:3]):  # 처음 3개만 확인
                    try:
                        logging.info(f"   요소 {i+1}: {element.tag_name} - {element.get_attribute('id')} - {element.get_attribute('class')}")
                    except:
                        pass
        except Exception as e:
            logging.error(f"❌ 개발자 모드 요소 확인 오류: {e}")
        
        return len(found_keywords) > 0
        
    except Exception as e:
        logging.error(f"❌ 테스트 중 오류 발생: {e}")
        return False
        
    finally:
        if driver:
            logging.info("🔚 브라우저 종료...")
            time.sleep(2)
            driver.quit()

if __name__ == "__main__":
    logging.info("=" * 60)
    logging.info("🧪 간단한 확장 프로그램 로드 테스트 시작")
    logging.info("=" * 60)
    
    success = test_extension_load()
    
    logging.info("=" * 60)
    if success:
        logging.info("✅ 테스트 완료: 확장 프로그램 로드가 감지되었습니다.")
    else:
        logging.info("❌ 테스트 완료: 확장 프로그램 로드에 문제가 있습니다.")
    logging.info("=" * 60)