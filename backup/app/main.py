# -*- coding: utf-8 -*-
"""
퍼센티 자동화 앱 메인 모듈

앱의 진입점으로, GUI를 초기화하고 필요한 관리자 객체들을 생성합니다.
"""

import os
import sys
import logging
import tkinter as tk
from tkinter import messagebox

# 현재 디렉토리를 경로에 추가 (상대 임포트를 위해)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 관리자 클래스 임포트
from app.utils.account_manager import AccountManager
from app.utils.task_manager import TaskManager
from app.utils.browser_manager import BrowserManager

# GUI 임포트
from app.ui.app_gui import AppGUI

def setup_logging():
    """로깅 설정"""
    # 로그 디렉토리 생성
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # 로그 파일 경로
    log_file = os.path.join(log_dir, "percenty_app.log")
    
    # 한글 인코딩 설정
    import codecs
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    # 로거 설정
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # 기존 핸들러 제거 (중복 방지)
    for handler in logger.handlers[:]:  
        logger.removeHandler(handler)
    
    # 파일 핸들러
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    logger.addHandler(file_handler)
    
    # 콘솔 핸들러 - 인코딩 명시
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    logger.addHandler(console_handler)
    
    return logger

def main():
    """앱 메인 함수"""
    # 로깅 설정
    logger = setup_logging()
    logger.info("퍼센티 자동화 앱 시작")
    
    try:
        # 루트 윈도우 생성
        root = tk.Tk()
        root.title("퍼센티 자동화")
        root.geometry("800x600")
        
        # 관리자 객체 생성
        logger.info("관리자 객체 초기화")
        account_manager = AccountManager()
        task_manager = TaskManager()
        browser_manager = BrowserManager()
        
        # GUI 초기화
        logger.info("GUI 초기화")
        app_gui = AppGUI(root, account_manager, task_manager, browser_manager)
        
        # 종료 이벤트 핸들러 설정
        root.protocol("WM_DELETE_WINDOW", app_gui.on_closing)
        
        # 애플리케이션 실행
        logger.info("메인 루프 시작")
        root.mainloop()
        
    except Exception as e:
        logger.error(f"애플리케이션 실행 중 오류: {str(e)}")
        messagebox.showerror("오류", f"애플리케이션 실행 중 오류가 발생했습니다:\n{str(e)}")
    finally:
        logger.info("퍼센티 자동화 앱 종료")

if __name__ == "__main__":
    main()
