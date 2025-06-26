#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import os
from pathlib import Path
import json

def analyze_excel_file():
    """카페24 최적화.xlsm 파일을 분석합니다."""
    
    # 파일 경로 설정
    file_path = Path(r'c:\Projects\percenty_project\docs\카페24 최적화.xlsm')
    
    print(f"=== 엑셀 파일 분석 시작 ===")
    print(f"파일 경로: {file_path}")
    print(f"파일 존재: {file_path.exists()}")
    
    if not file_path.exists():
        print("파일이 존재하지 않습니다.")
        return
    
    print(f"파일 크기: {file_path.stat().st_size:,} bytes")
    
    analysis_result = {
        "file_info": {
            "path": str(file_path),
            "size": file_path.stat().st_size,
            "exists": True
        },
        "sheets": {}
    }
    
    try:
        # 엑셀 파일의 모든 시트 이름 확인
        xl_file = pd.ExcelFile(file_path, engine='openpyxl')
        sheet_names = xl_file.sheet_names
        
        print(f"\n=== 시트 목록 ({len(sheet_names)}개) ===")
        for i, sheet_name in enumerate(sheet_names, 1):
            print(f"{i}. {sheet_name}")
        
        # 각 시트의 기본 정보 분석
        for sheet_name in sheet_names:
            print(f"\n=== 시트 '{sheet_name}' 분석 ===")
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')
                
                sheet_info = {
                    "rows": len(df),
                    "columns": len(df.columns),
                    "column_names": list(df.columns),
                    "sample_data": []
                }
                
                print(f"행 수: {len(df)}")
                print(f"열 수: {len(df.columns)}")
                
                if len(df.columns) > 0:
                    print(f"컬럼 목록:")
                    for i, col in enumerate(df.columns, 1):
                        print(f"  {i:2d}. {col}")
                
                # 샘플 데이터 (처음 5행, 중요 컬럼만)
                if len(df) > 0:
                    print(f"\n샘플 데이터 (처음 5행):")
                    sample_df = df.head(5)
                    
                    # 중요해 보이는 컬럼들만 선택
                    important_cols = []
                    for col in df.columns:
                        col_str = str(col).lower()
                        if any(keyword in col_str for keyword in ['상품', '코드', '가격', '판매', '원가', '이름', '제목']):
                            important_cols.append(col)
                    
                    if important_cols:
                        print(f"\n중요 컬럼 데이터:")
                        for col in important_cols[:10]:  # 최대 10개 컬럼
                            print(f"\n[{col}]")
                            values = sample_df[col].dropna().head(3)
                            for idx, val in values.items():
                                print(f"  {idx}: {val}")
                    
                    # 분석 결과에 샘플 데이터 저장
                    sheet_info["sample_data"] = sample_df.head(3).to_dict('records')
                
                analysis_result["sheets"][sheet_name] = sheet_info
                
            except Exception as e:
                print(f"시트 '{sheet_name}' 읽기 오류: {str(e)}")
                analysis_result["sheets"][sheet_name] = {"error": str(e)}
        
        # 분석 결과를 JSON 파일로 저장
        result_file = Path(r'c:\Projects\percenty_project\excel_analysis_result.json')
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n분석 결과가 {result_file}에 저장되었습니다.")
        
    except Exception as e:
        print(f"파일 분석 중 오류 발생: {str(e)}")
    
    print(f"\n=== 분석 완료 ===")

if __name__ == "__main__":
    analyze_excel_file()