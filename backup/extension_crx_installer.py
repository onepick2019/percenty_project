#!/usr/bin/env python3
"""
퍼센티 확장 프로그램 CRX 설치 도구

이 스크립트는 CRX 파일을 사용하여 퍼센티 확장 프로그램을 설치합니다.
"""

import os
import sys
import time
import logging
import traceback
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from browser_core import BrowserCore

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crx_install.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def install_crx_extension(driver, crx_path):
    """CRX 파일을 사용하여 확장 프로그램 설치"""
    logger.info("===== CRX 확장 프로그램 설치 시작 =====")
    
    try:
        # chrome://extensions/ 페이지로 이동
        driver.get("chrome://extensions/")
        time.sleep(3)
        
        # 개발자 모드 활성화
        try:
            dev_mode_toggle = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#devMode"))
            )
            if not dev_mode_toggle.is_selected():
                logger.info("개발자 모드 활성화 중...")
                dev_mode_toggle.click()
                time.sleep(2)
            else:
                logger.info("개발자 모드가 이미 활성화되어 있습니다.")
        except TimeoutException:
            logger.warning("개발자 모드 토글을 찾을 수 없습니다.")
        
        # CRX 파일을 드래그 앤 드롭으로 설치
        logger.info(f"CRX 파일 드래그 앤 드롭: {crx_path}")
        
        # 파일 입력 요소 찾기 (숨겨진 요소일 수 있음)
        try:
            # JavaScript를 사용하여 파일 드롭 시뮬레이션
            js_script = f"""
            var input = document.createElement('input');
            input.type = 'file';
            input.accept = '.crx';
            input.style.display = 'none';
            document.body.appendChild(input);
            
            var file = new File([''], '{os.path.basename(crx_path)}', {{type: 'application/x-chrome-extension'}});
            var dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            input.files = dataTransfer.files;
            
            var event = new Event('change', {{bubbles: true}});
            input.dispatchEvent(event);
            """
            
            driver.execute_script(js_script)
            time.sleep(3)
            
        except Exception as e:
            logger.warning(f"JavaScript 드롭 시뮬레이션 실패: {e}")
        
        # 수동 설치 안내
        logger.info("===== 수동 설치 안내 =====")
        logger.info("자동 설치가 실패했습니다. 다음 단계를 수동으로 진행해주세요:")
        logger.info(f"1. CRX 파일 경로: {crx_path}")
        logger.info("2. 파일 탐색기에서 위 CRX 파일을 찾아주세요")
        logger.info("3. CRX 파일을 chrome://extensions/ 페이지로 드래그 앤 드롭하세요")
        logger.info("4. '확장 프로그램 추가' 버튼을 클릭하세요")
        logger.info("")
        
        user_input = input("수동 설치가 완료되면 'y' 또는 'yes'를 입력하고 Enter를 눌러주세요: ")
        
        if user_input.lower() in ['y', 'yes']:
            # 설치 확인
            time.sleep(2)
            page_source = driver.page_source.lower()
            
            if '퍼센티' in page_source or 'percenty' in page_source:
                logger.info("✅ 퍼센티 확장 프로그램 설치 성공!")
                return True
            else:
                logger.warning("❌ 확장 프로그램이 설치되지 않았거나 인식되지 않습니다.")
                return False
        else:
            logger.info("설치가 취소되었습니다.")
            return False
            
    except Exception as e:
        logger.error(f"CRX 설치 중 오류: {e}")
        logger.error(traceback.format_exc())
        return False

def main():
    """메인 함수"""
    logger.info("===== 퍼센티 확장 프로그램 CRX 설치 시작 =====")
    
    # CRX 파일 경로 확인
    crx_path = os.path.join(os.path.dirname(__file__), "jlcdjppbpplpdgfeknhioedbhfceaben.crx")
    
    if not os.path.exists(crx_path):
        logger.error(f"❌ CRX 파일을 찾을 수 없습니다: {crx_path}")
        logger.error("다음 중 하나를 수행하세요:")
        logger.error("1. CRX 파일을 프로젝트 디렉토리에 복사하세요")
        logger.error("2. Chrome 웹 스토어에서 퍼센티 확장 프로그램을 수동으로 설치하세요")
        return False
    
    logger.info(f"CRX 파일 발견: {crx_path}")
    
    browser_core = None
    try:
        # BrowserCore 초기화 (확장 프로그램 자동 로드 비활성화)
        logger.info("BrowserCore 초기화 중...")
        browser_core = BrowserCore()
        
        # 브라우저 시작
        logger.info("브라우저 드라이버 설정 중...")
        if not browser_core.setup_driver(headless=False):
            logger.error("브라우저 드라이버 설정 실패")
            return False
        
        logger.info("브라우저 시작 완료")
        
        # CRX 확장 프로그램 설치
        success = install_crx_extension(browser_core.driver, crx_path)
        
        if success:
            logger.info("✅ 퍼센티 확장 프로그램 설치 완료!")
            logger.info("이제 퍼센티 자동화 스크립트를 실행할 수 있습니다.")
        else:
            logger.error("❌ 퍼센티 확장 프로그램 설치 실패")
        
        return success
        
    except Exception as e:
        logger.error(f"설치 중 오류 발생: {e}")
        logger.error(traceback.format_exc())
        return False
    
    finally:
        # 브라우저 종료 여부 확인
        if browser_core and browser_core.driver:
            user_input = input("\n브라우저를 종료하시겠습니까? (y/n): ")
            if user_input.lower() in ['y', 'yes']:
                logger.info("브라우저 종료 중...")
                try:
                    browser_core.driver.quit()
                    logger.info("브라우저 종료 완료")
                except Exception as e:
                    logger.error(f"브라우저 종료 중 오류: {e}")
            else:
                logger.info("브라우저를 열어둡니다. 수동으로 종료해주세요.")

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ 설치 성공: 퍼센티 확장 프로그램이 설치되었습니다.")
    else:
        print("\n❌ 설치 실패: 퍼센티 확장 프로그램 설치에 문제가 있습니다.")
        print("자세한 내용은 crx_install.log 파일을 확인하세요.")