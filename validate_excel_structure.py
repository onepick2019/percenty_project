#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel 파일 구조 검증 및 슬래시 명령어 확인
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from product_editor_core3 import ProductEditorCore3
import pandas as pd

def validate_excel_structure():
    """Excel 파일 구조 검증"""
    excel_path = "c:\\Projects\\percenty_project\\percenty_id.xlsx"
    
    print("=== Excel 파일 구조 검증 ===")
    
    if not os.path.exists(excel_path):
        print(f"❌ Excel 파일을 찾을 수 없습니다: {excel_path}")
        return False
    
    try:
        # Excel 파일 읽기
        excel_file = pd.ExcelFile(excel_path)
        print(f"✅ Excel 파일 로드 성공: {excel_path}")
        print(f"📋 시트 목록: {excel_file.sheet_names}")
        
        # login_id 시트 확인
        if 'login_id' not in excel_file.sheet_names:
            print("❌ 'login_id' 시트가 없습니다.")
            return False
        
        login_df = pd.read_excel(excel_path, sheet_name='login_id')
        print(f"✅ login_id 시트 로드 성공 (행: {len(login_df)}, 열: {len(login_df.columns)})")
        print(f"📋 login_id 컬럼: {list(login_df.columns)}")
        
        # 각 데이터 시트 확인
        data_sheets = [sheet for sheet in excel_file.sheet_names if sheet != 'login_id']
        print(f"\n📊 데이터 시트 목록: {data_sheets}")
        
        slash_commands_found = []
        
        for sheet_name in data_sheets:
            print(f"\n=== 시트 '{sheet_name}' 분석 ===")
            
            try:
                df = pd.read_excel(excel_path, sheet_name=sheet_name)
                print(f"✅ 시트 로드 성공 (행: {len(df)}, 열: {len(df.columns)})")
                print(f"📋 컬럼: {list(df.columns)}")
                
                # H, I, J 열 확인 (이미지 관련)
                image_columns = ['H', 'I', 'J']
                for col in image_columns:
                    if col in df.columns:
                        print(f"\n🖼️ {col}열 데이터 분석:")
                        
                        # 슬래시 포함 데이터 찾기
                        slash_data = []
                        for idx, value in df[col].items():
                            if pd.notna(value) and isinstance(value, str) and '/' in value:
                                slash_data.append((f"{sheet_name}.{col}[{idx+2}]", value))  # +2는 Excel 행 번호 (헤더 포함)
                                slash_commands_found.append((sheet_name, col, idx+2, value))
                        
                        if slash_data:
                            print(f"  🔍 슬래시 명령어 {len(slash_data)}개 발견:")
                            for location, value in slash_data:
                                print(f"    {location}: {value}")
                        
                        # 고유값 확인
                        unique_vals = df[col].dropna().unique()
                        print(f"  📊 고유값 ({len(unique_vals)}개): {list(unique_vals)[:10]}")
                        if len(unique_vals) > 10:
                            print(f"    ... 및 {len(unique_vals) - 10}개 더")
                
            except Exception as e:
                print(f"❌ 시트 '{sheet_name}' 읽기 오류: {e}")
        
        # 슬래시 명령어 종합 분석
        print(f"\n=== 슬래시 명령어 종합 분석 ===")
        if slash_commands_found:
            print(f"✅ 총 {len(slash_commands_found)}개의 슬래시 명령어 발견")
            
            # 명령어 패턴 분석
            patterns = {}
            for sheet, col, row, value in slash_commands_found:
                if value not in patterns:
                    patterns[value] = []
                patterns[value].append(f"{sheet}.{col}[{row}]")
            
            print("📋 명령어 패턴별 분류:")
            for pattern, locations in patterns.items():
                print(f"  '{pattern}': {len(locations)}개 위치")
                for loc in locations[:3]:  # 처음 3개만 표시
                    print(f"    - {loc}")
                if len(locations) > 3:
                    print(f"    - ... 및 {len(locations) - 3}개 더")
        else:
            print("⚠️ 슬래시 명령어가 발견되지 않았습니다.")
        
        return True
        
    except Exception as e:
        print(f"❌ Excel 파일 분석 중 오류: {e}")
        return False

def test_slash_parsing():
    """슬래시 명령어 파싱 테스트"""
    print("\n=== 슬래시 명령어 파싱 테스트 ===")
    
    # ProductEditorCore3 인스턴스 생성
    core = ProductEditorCore3(None)
    
    # 테스트 케이스
    test_cases = [
        "first:1/last:1",
        "last:2/first:1", 
        "copy:3/copy:1",
        "specific:1,2/last:1",
        "first:2",  # 단일 명령어
        "YES",      # 기본 명령어
        "NO"        # 거부 명령어
    ]
    
    for test_case in test_cases:
        try:
            result = core._parse_action_command(test_case)
            print(f"✅ '{test_case}' -> {result}")
        except Exception as e:
            print(f"❌ '{test_case}' -> 오류: {e}")

if __name__ == "__main__":
    # Excel 구조 검증
    success = validate_excel_structure()
    
    if success:
        # 슬래시 파싱 테스트
        test_slash_parsing()
    
    print("\n=== 검증 완료 ===")