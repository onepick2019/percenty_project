#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
안전한 애플리케이션 실행 스크립트
브라우저 생성 문제를 진단하고 해결하는 스크립트
"""

import sys
import os
import logging
import traceback
import subprocess
import time

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_chrome_installation():
    """
    Chrome 설치 상태 확인
    """
    logger.info("=== Chrome 설치 상태 확인 ===")
    
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    
    for path in chrome_paths:
        if os.path.exists(path):
            logger.info(f"✅ Chrome 발견: {path}")
            return True
    
    logger.error("❌ Chrome이 설치되지 않았습니다.")
    return False

def check_selenium_installation():
    """
    Selenium 설치 상태 확인
    """
    logger.info("=== Selenium 설치 상태 확인 ===")
    
    try:
        import selenium
        logger.info(f"✅ Selenium 버전: {selenium.__version__}")
        return True
    except ImportError:
        logger.error("❌ Selenium이 설치되지 않았습니다.")
        return False

def test_simple_browser_creation():
    """
    간단한 브라우저 생성 테스트
    """
    logger.info("=== 간단한 브라우저 생성 테스트 ===")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        
        logger.info("Chrome 드라이버 생성 시도...")
        start_time = time.time()
        
        driver = webdriver.Chrome(options=chrome_options)
        
        creation_time = time.time() - start_time
        logger.info(f"✅ Chrome 드라이버 생성 성공! (소요시간: {creation_time:.2f}초)")
        
        driver.quit()
        logger.info("✅ 드라이버 종료 완료")
        return True
        
    except Exception as e:
        logger.error(f"❌ 브라우저 생성 실패: {e}")
        logger.error(f"상세 오류: {traceback.format_exc()}")
        return False

def test_batch_manager_browser():
    """
    BatchManager의 브라우저 생성 테스트
    """
    logger.info("=== BatchManager 브라우저 생성 테스트 ===")
    
    try:
        # 프로젝트 경로 설정
        project_root = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, project_root)
        sys.path.insert(0, os.path.join(project_root, 'core'))
        sys.path.insert(0, os.path.join(project_root, 'batch'))
        
        logger.info("BatchManager 임포트 시도...")
        from batch_manager import BatchManager
        logger.info("✅ BatchManager 임포트 성공")
        
        logger.info("BatchManager 인스턴스 생성 시도...")
        batch_manager = BatchManager()
        logger.info(f"✅ BatchManager 생성 성공: {type(batch_manager)}")
        
        logger.info("browser_manager 상태 확인...")
        logger.info(f"browser_manager 타입: {type(batch_manager.browser_manager)}")
        logger.info(f"create_browser 메서드 존재: {hasattr(batch_manager.browser_manager, 'create_browser')}")
        
        logger.info("브라우저 생성 직접 테스트...")
        browser_id = batch_manager.browser_manager.create_browser(
            browser_id="test_browser_safe",
            headless=True  # 헤드리스 모드로 테스트
        )
        logger.info(f"브라우저 생성 결과: {browser_id}")
        
        if browser_id:
            logger.info("✅ 브라우저 생성 성공!")
            # 브라우저 종료
            batch_manager.browser_manager.close_browser(browser_id)
            logger.info("✅ 브라우저 종료 완료")
            return True
        else:
            logger.error("❌ 브라우저 생성 실패 (None 반환)")
            return False
            
    except Exception as e:
        logger.error(f"❌ BatchManager 브라우저 테스트 실패: {e}")
        logger.error(f"상세 오류: {traceback.format_exc()}")
        return False

def run_main_app():
    """
    메인 애플리케이션 실행
    """
    logger.info("=== 메인 애플리케이션 실행 ===")
    
    try:
        # 현재 디렉토리를 프로젝트 루트로 설정
        project_root = os.path.dirname(os.path.abspath(__file__))
        os.chdir(project_root)
        
        # 메인 애플리케이션 실행
        logger.info("app_new/main.py 실행 시도...")
        
        # GUI 애플리케이션을 별도 프로세스로 실행 (capture_output=False로 GUI 표시 허용)
        logger.info("GUI 애플리케이션을 시작합니다...")
        
        # GUI 애플리케이션은 백그라운드에서 실행되도록 함
        process = subprocess.Popen(
            [sys.executable, "app_new/main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        logger.info(f"✅ 애플리케이션이 시작되었습니다 (PID: {process.pid})")
        logger.info("GUI 창이 나타날 때까지 잠시 기다려주세요...")
        
        # 3초 후 프로세스 상태 확인
        import time
        time.sleep(3)
        
        if process.poll() is None:
            logger.info("✅ 애플리케이션이 정상적으로 실행 중입니다.")
        else:
            stdout, stderr = process.communicate()
            logger.error(f"❌ 애플리케이션이 종료되었습니다 (종료 코드: {process.returncode})")
            if stdout:
                logger.error(f"출력: {stdout}")
            if stderr:
                logger.error(f"오류: {stderr}")
            
    except Exception as e:
        logger.error(f"❌ 애플리케이션 실행 중 오류: {e}")
        logger.error(f"상세 오류: {traceback.format_exc()}")

def main():
    """
    메인 함수
    """
    logger.info("=== 안전한 애플리케이션 실행 스크립트 시작 ===")
    
    # 1. Chrome 설치 확인
    if not check_chrome_installation():
        logger.error("Chrome을 먼저 설치해주세요.")
        return False
    
    # 2. Selenium 설치 확인
    if not check_selenium_installation():
        logger.error("pip install selenium 명령으로 Selenium을 설치해주세요.")
        return False
    
    # 3. 간단한 브라우저 생성 테스트
    if not test_simple_browser_creation():
        logger.error("브라우저 생성에 문제가 있습니다. 다음을 확인해주세요:")
        logger.error("- 인터넷 연결 상태")
        logger.error("- 방화벽/보안 프로그램 설정")
        logger.error("- 관리자 권한으로 실행")
        return False
    
    # 4. BatchManager 브라우저 생성 테스트
    if not test_batch_manager_browser():
        logger.error("BatchManager 브라우저 생성에 문제가 있습니다.")
        logger.error("이것이 GUI에서 브라우저가 열리지 않는 원인일 수 있습니다.")
        return False
    
    # 5. 메인 애플리케이션 실행
    logger.info("모든 테스트를 통과했습니다. 메인 애플리케이션을 실행합니다.")
    run_main_app()
    
    logger.info("=== 스크립트 완료 ===")
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            logger.info("✅ 모든 검사를 통과했습니다.")
        else:
            logger.error("❌ 일부 검사에서 문제가 발견되었습니다.")
    except KeyboardInterrupt:
        logger.info("사용자에 의해 중단되었습니다.")
    except Exception as e:
        logger.error(f"예상치 못한 오류: {e}")
        logger.error(f"상세 오류: {traceback.format_exc()}")