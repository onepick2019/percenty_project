#!/usr/bin/env python3
"""
GUI 애플리케이션 안전 실행기 (브라우저 문제 해결 버전)

GUI에서 브라우저가 열리지 않는 문제를 해결하기 위한 개선된 실행기
"""

import sys
import os
import logging
import traceback
import time
from pathlib import Path

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('gui_launch.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """필수 의존성 확인"""
    logger.info("필수 의존성 확인 중...")
    
    try:
        import tkinter
        logger.info("✅ tkinter 사용 가능")
    except ImportError as e:
        logger.error(f"❌ tkinter 없음: {e}")
        return False
    
    try:
        import selenium
        logger.info(f"✅ selenium 버전: {selenium.__version__}")
    except ImportError as e:
        logger.error(f"❌ selenium 없음: {e}")
        return False
    
    try:
        from pathlib import Path
        logger.info("✅ pathlib 사용 가능")
    except ImportError as e:
        logger.error(f"❌ pathlib 없음: {e}")
        return False
    
    return True

def check_project_structure():
    """프로젝트 구조 확인"""
    logger.info("프로젝트 구조 확인 중...")
    
    current_dir = Path.cwd()
    logger.info(f"현재 디렉토리: {current_dir}")
    
    # 필수 파일들 확인
    required_files = [
        'app_new/main.py',
        'browser_core.py'
    ]
    
    for file_path in required_files:
        full_path = current_dir / file_path
        if full_path.exists():
            logger.info(f"✅ {file_path} 존재")
        else:
            logger.error(f"❌ {file_path} 없음")
            return False
    
    return True

def test_browser_creation():
    """브라우저 생성 테스트"""
    logger.info("브라우저 생성 테스트 시작...")
    
    try:
        from browser_core import BrowserCore
        
        # 헤드리스 모드로 간단한 테스트
        browser_core = BrowserCore()
        logger.info("BrowserCore 인스턴스 생성 성공")
        
        success = browser_core.setup_driver(headless=True)
        
        if success and browser_core.driver:
            logger.info("✅ 브라우저 생성 테스트 성공")
            browser_core.driver.quit()
            return True
        else:
            logger.error("❌ 브라우저 생성 실패")
            return False
            
    except Exception as e:
        logger.error(f"❌ 브라우저 테스트 중 오류: {e}")
        logger.error(traceback.format_exc())
        return False

def launch_gui_safe():
    """안전한 GUI 실행"""
    logger.info("GUI 애플리케이션 실행 시작...")
    
    try:
        # app_new 디렉토리를 sys.path에 추가
        app_new_path = str(Path.cwd() / 'app_new')
        if app_new_path not in sys.path:
            sys.path.insert(0, app_new_path)
            logger.info(f"sys.path에 추가: {app_new_path}")
        
        # 프로젝트 루트를 sys.path에 추가
        project_root = str(Path.cwd())
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
            logger.info(f"sys.path에 추가: {project_root}")
        
        # main 모듈 임포트
        logger.info("main 모듈 임포트 중...")
        from main import PercentyGUI
        logger.info("PercentyGUI 클래스 임포트 성공")
        
        # GUI 애플리케이션 인스턴스 생성
        logger.info("PercentyGUI 인스턴스 생성 중...")
        app = PercentyGUI()
        logger.info("PercentyGUI 인스턴스 생성 성공")
        
        # GUI 실행
        logger.info("GUI 애플리케이션 실행 중...")
        app.run()
        
        logger.info("GUI 애플리케이션 정상 종료")
        return True
        
    except ImportError as e:
        logger.error(f"❌ 모듈 임포트 오류: {e}")
        logger.error("app_new/main.py 파일이나 PercentyGUI 클래스를 찾을 수 없습니다.")
        logger.error(traceback.format_exc())
        return False
        
    except Exception as e:
        logger.error(f"❌ GUI 실행 중 오류: {e}")
        logger.error(traceback.format_exc())
        return False

def main():
    """메인 함수"""
    logger.info("=== GUI 애플리케이션 안전 실행기 시작 ===")
    
    # 1. 의존성 확인
    if not check_dependencies():
        logger.error("필수 의존성이 부족합니다.")
        input("엔터를 눌러 종료하세요...")
        return False
    
    # 2. 프로젝트 구조 확인
    if not check_project_structure():
        logger.error("프로젝트 구조에 문제가 있습니다.")
        input("엔터를 눌러 종료하세요...")
        return False
    
    # 3. 브라우저 생성 테스트
    if not test_browser_creation():
        logger.error("브라우저 생성에 문제가 있습니다.")
        logger.info("브라우저 문제가 있지만 GUI 실행을 시도합니다...")
    
    # 4. GUI 실행
    success = launch_gui_safe()
    
    if success:
        logger.info("✅ GUI 애플리케이션이 성공적으로 실행되었습니다.")
    else:
        logger.error("❌ GUI 애플리케이션 실행에 실패했습니다.")
        
        # 문제 해결 제안
        logger.info("\n=== 문제 해결 제안 ===")
        logger.info("1. Chrome 브라우저가 설치되어 있는지 확인하세요.")
        logger.info("2. 관리자 권한으로 실행해보세요.")
        logger.info("3. 방화벽이나 보안 프로그램을 일시적으로 비활성화해보세요.")
        logger.info("4. 인터넷 연결을 확인하세요.")
        logger.info("5. test_browser_restore.py를 실행하여 브라우저 설정을 확인하세요.")
        
        input("엔터를 눌러 종료하세요...")
    
    return success

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("사용자에 의해 중단되었습니다.")
    except Exception as e:
        logger.error(f"예상치 못한 오류: {e}")
        logger.error(traceback.format_exc())
        input("엔터를 눌러 종료하세요...")