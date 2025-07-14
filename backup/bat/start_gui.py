#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 GUI 시작 스크립트
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    try:
        print("Percenty 자동화 GUI를 시작합니다...")
        
        # 현재 디렉토리를 프로젝트 루트로 설정
        os.chdir(project_root)
        
        # GUI 애플리케이션 직접 임포트 및 실행
        from app_new.main import PercentyGUI
        
        print("GUI 클래스를 로드했습니다.")
        
        # GUI 인스턴스 생성 및 실행
        app = PercentyGUI()
        print("GUI 인스턴스를 생성했습니다.")
        
        print("GUI를 시작합니다...")
        app.run()
        
    except ImportError as e:
        print(f"모듈 임포트 오류: {e}")
        print("필요한 모듈이 설치되어 있는지 확인해주세요.")
    except Exception as e:
        print(f"GUI 시작 중 오류 발생: {e}")
        import traceback
        print(f"상세 오류: {traceback.format_exc()}")
    
    input("아무 키나 누르면 종료됩니다...")