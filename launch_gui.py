#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Percenty GUI 안전 실행 스크립트
"""

import sys
import os
import logging
import traceback
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """
    필수 의존성 확인
    """
    logger.info("=== 의존성 확인 ===")
    
    required_modules = [
        'tkinter',
        'selenium',
        'pathlib'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            logger.info(f"✅ {module} 모듈 확인")
        except ImportError:
            logger.error(f"❌ {module} 모듈 누락")
            missing_modules.append(module)
    
    if missing_modules:
        logger.error(f"누락된 모듈: {missing_modules}")
        return False
    
    return True

def check_project_structure():
    """
    프로젝트 구조 확인
    """
    logger.info("=== 프로젝트 구조 확인 ===")
    
    required_paths = [
        'app_new/main.py',
        'batch/batch_manager.py',
        'core/account/account_manager.py',
        'core/browser/browser_manager.py'
    ]
    
    missing_files = []
    
    for path in required_paths:
        full_path = project_root / path
        if full_path.exists():
            logger.info(f"✅ {path} 파일 확인")
        else:
            logger.error(f"❌ {path} 파일 누락")
            missing_files.append(path)
    
    if missing_files:
        logger.error(f"누락된 파일: {missing_files}")
        return False
    
    return True

def launch_gui():
    """
    GUI 애플리케이션 실행
    """
    logger.info("=== GUI 애플리케이션 실행 ===")
    
    try:
        # 현재 디렉토리를 프로젝트 루트로 설정
        os.chdir(project_root)
        logger.info(f"작업 디렉토리: {os.getcwd()}")
        
        # GUI 모듈 임포트
        logger.info("GUI 모듈 임포트 중...")
        from app_new.main import PercentyGUI
        logger.info("✅ GUI 모듈 임포트 성공")
        
        # GUI 인스턴스 생성
        logger.info("GUI 인스턴스 생성 중...")
        app = PercentyGUI()
        logger.info("✅ GUI 인스턴스 생성 성공")
        
        # GUI 실행
        logger.info("GUI 실행 시작...")
        logger.info("GUI 창이 나타날 때까지 잠시 기다려주세요.")
        app.run()
        
        logger.info("✅ GUI 애플리케이션이 정상적으로 종료되었습니다.")
        return True
        
    except ImportError as e:
        logger.error(f"❌ 모듈 임포트 오류: {e}")
        logger.error("필요한 모듈이 설치되어 있는지 확인해주세요.")
        return False
        
    except Exception as e:
        logger.error(f"❌ GUI 실행 중 오류: {e}")
        logger.error(f"상세 오류: {traceback.format_exc()}")
        return False

def main():
    """
    메인 함수
    """
    logger.info("=== Percenty GUI 안전 실행 스크립트 시작 ===")
    
    try:
        # 1. 의존성 확인
        if not check_dependencies():
            logger.error("의존성 확인 실패")
            return False
        
        # 2. 프로젝트 구조 확인
        if not check_project_structure():
            logger.error("프로젝트 구조 확인 실패")
            return False
        
        # 3. GUI 실행
        success = launch_gui()
        
        if success:
            logger.info("✅ 모든 작업이 성공적으로 완료되었습니다.")
        else:
            logger.error("❌ GUI 실행에 실패했습니다.")
        
        return success
        
    except KeyboardInterrupt:
        logger.info("사용자에 의해 중단되었습니다.")
        return False
        
    except Exception as e:
        logger.error(f"예상치 못한 오류: {e}")
        logger.error(f"상세 오류: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    try:
        success = main()
        
        if not success:
            print("\n문제 해결 방법:")
            print("1. Python 및 필수 모듈 설치 확인")
            print("2. 프로젝트 파일 구조 확인")
            print("3. 관리자 권한으로 실행 시도")
            print("4. 방화벽/보안 프로그램 설정 확인")
            
    except Exception as e:
        print(f"스크립트 실행 중 치명적 오류: {e}")
        
    input("\n아무 키나 누르면 종료됩니다...")