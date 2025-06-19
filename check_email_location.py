# -*- coding: utf-8 -*-
"""
Excel 파일에서 특정 이메일의 정확한 위치 확인
"""

import pandas as pd
import os

def check_email_location():
    """Excel 파일에서 wop32gsung@gmail.com의 정확한 위치 확인"""
    excel_path = "c:\\Projects\\percenty_project\\percenty_id.xlsx"
    target_email = "wop32gsung@gmail.com"
    
    if not os.path.exists(excel_path):
        print(f"Excel 파일을 찾을 수 없습니다: {excel_path}")
        return
    
    try:
        # Excel 파일의 모든 시트 확인
        excel_file = pd.ExcelFile(excel_path)
        print(f"=== Excel 파일 분석: {excel_path} ===")
        print(f"시트 목록: {excel_file.sheet_names}")
        
        for sheet_name in excel_file.sheet_names:
            print(f"\n=== 시트: {sheet_name} ===")
            
            try:
                # 시트 읽기
                df = pd.read_excel(excel_path, sheet_name=sheet_name)
                print(f"행 수: {len(df)} (헤더 포함)")
                print(f"열 수: {len(df.columns)}")
                print(f"컬럼명: {list(df.columns)}")
                
                # 전체 데이터에서 target_email 검색
                found_locations = []
                
                for col_idx, col_name in enumerate(df.columns):
                    for row_idx, value in df[col_name].items():
                        if pd.notna(value) and str(value).strip() == target_email:
                            # pandas의 row_idx는 0부터 시작하므로 Excel 행 번호는 +2 (헤더 포함)
                            excel_row = row_idx + 2
                            found_locations.append((col_name, excel_row, row_idx))
                            print(f"발견: 열 '{col_name}', Excel 행 {excel_row} (pandas 인덱스 {row_idx}), 값: '{value}'")
                
                if not found_locations:
                    print(f"'{target_email}'을 찾을 수 없습니다.")
                
                # 처음 5행의 데이터 표시 (디버깅용)
                print("\n처음 5행 데이터:")
                for i in range(min(5, len(df))):
                    row_data = df.iloc[i]
                    print(f"행 {i+2} (pandas 인덱스 {i}): {dict(row_data)}")
                    
            except Exception as e:
                print(f"시트 '{sheet_name}' 읽기 오류: {e}")
                
    except Exception as e:
        print(f"Excel 파일 읽기 오류: {e}")

if __name__ == "__main__":
    check_email_location()