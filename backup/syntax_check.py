#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
문법 검사 스크립트
"""

import ast
import sys

def check_syntax(file_path):
    """파일의 Python 문법을 검사합니다."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # AST로 파싱하여 문법 검사
        ast.parse(source_code)
        print(f"✅ {file_path}: 문법 검사 통과")
        return True
        
    except SyntaxError as e:
        print(f"❌ {file_path}: 문법 오류 발견")
        print(f"   라인 {e.lineno}: {e.text.strip() if e.text else ''}")
        print(f"   오류: {e.msg}")
        return False
        
    except Exception as e:
        print(f"❌ {file_path}: 파일 읽기 오류 - {e}")
        return False

if __name__ == "__main__":
    print("=== Python 문법 검사 시작 ===")
    
    # 검사할 파일들
    files_to_check = [
        "cli/batch_cli.py",
        "product_editor_core5_2.py",
        "core/steps/step5_2_core.py"
    ]
    
    all_passed = True
    
    for file_path in files_to_check:
        if not check_syntax(file_path):
            all_passed = False
    
    print("\n=== 문법 검사 완료 ===")
    if all_passed:
        print("✅ 모든 파일의 문법이 올바릅니다.")
    else:
        print("❌ 일부 파일에 문법 오류가 있습니다.")
        sys.exit(1)