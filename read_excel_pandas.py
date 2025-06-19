#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pandas를 사용한 Excel 파일 읽기 스크립트
"""

import pandas as pd
import os

def read_excel_with_pandas():
    """pandas를 사용해서 Excel 파일 읽기"""
    excel_path = "c:\\Projects\\percenty_project\\percenty_id.xlsx"
    
    if not os.path.exists(excel_path):
        print(f"Excel 파일을 찾을 수 없습니다: {excel_path}")
        return
    
    try:
        # Excel 파일의 모든 시트명 확인
        excel_file = pd.ExcelFile(excel_path)
        print(f"=== Excel 파일 분석: {excel_path} ===")
        print(f"시트 목록: {excel_file.sheet_names}")
        
        # 각 시트 분석
        for sheet_name in excel_file.sheet_names:
            print(f"\n=== 시트: {sheet_name} ===")
            
            try:
                df = pd.read_excel(excel_path, sheet_name=sheet_name)
                print(f"행 수: {len(df)}")
                print(f"열 수: {len(df.columns)}")
                print(f"컬럼명: {list(df.columns)}")
                
                # 처음 3행 데이터 표시
                if len(df) > 0:
                    print("\n처음 3행 데이터:")
                    print(df.head(3).to_string())
                
                # 슬래시 포함 데이터 찾기
                slash_data = []
                for col in df.columns:
                    for idx, value in df[col].items():
                        if pd.notna(value) and isinstance(value, str) and '/' in value:
                            slash_data.append((f"{col}[{idx}]", value))
                
                if slash_data:
                    print(f"\n슬래시(/) 포함 데이터 {len(slash_data)}개:")
                    for location, value in slash_data[:5]:  # 처음 5개만 표시
                        print(f"  {location}: {value}")
                    if len(slash_data) > 5:
                        print(f"  ... 및 {len(slash_data) - 5}개 더")
                
                # H, I, J 열이 있다면 특별히 분석
                image_cols = ['H', 'I', 'J']
                for col in image_cols:
                    if col in df.columns:
                        print(f"\n{col}열 고유값:")
                        unique_vals = df[col].dropna().unique()
                        print(f"  {list(unique_vals)[:10]}")
                        if len(unique_vals) > 10:
                            print(f"  ... 및 {len(unique_vals) - 10}개 더")
                
            except Exception as e:
                print(f"시트 '{sheet_name}' 읽기 오류: {e}")
        
    except Exception as e:
        print(f"Excel 파일 읽기 중 오류: {e}")

if __name__ == "__main__":
    read_excel_with_pandas()