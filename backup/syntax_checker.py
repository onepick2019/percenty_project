#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
구문 오류 검사 스크립트
터미널 타임아웃 문제를 우회하여 Python 파일의 구문을 검사합니다.
"""

import ast
import sys
import os
from pathlib import Path

def check_syntax(file_path):
    """
    Python 파일의 구문을 검사합니다.
    
    Args:
        file_path: 검사할 파일 경로
        
    Returns:
        tuple: (성공 여부, 오류 메시지)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # AST 파싱으로 구문 검사
        ast.parse(source_code, filename=file_path)
        return True, "구문 오류 없음"
        
    except SyntaxError as e:
        error_msg = f"구문 오류 발견:\n"
        error_msg += f"  파일: {file_path}\n"
        error_msg += f"  라인: {e.lineno}\n"
        error_msg += f"  컬럼: {e.offset}\n"
        error_msg += f"  오류: {e.msg}\n"
        if e.text:
            error_msg += f"  코드: {e.text.strip()}\n"
        return False, error_msg
        
    except Exception as e:
        return False, f"파일 읽기 오류: {e}"

def main():
    """메인 함수"""
    # 검사할 파일 목록
    files_to_check = [
        "core/periodic_execution_manager.py",
        "percenty_gui_advanced.py"
    ]
    
    print("=== Python 구문 검사 시작 ===")
    print()
    
    all_passed = True
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"검사 중: {file_path}")
            success, message = check_syntax(file_path)
            
            if success:
                print(f"✓ {message}")
            else:
                print(f"✗ {message}")
                all_passed = False
        else:
            print(f"✗ 파일을 찾을 수 없음: {file_path}")
            all_passed = False
        
        print()
    
    if all_passed:
        print("🎉 모든 파일이 구문 검사를 통과했습니다!")
    else:
        print("❌ 일부 파일에서 구문 오류가 발견되었습니다.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())