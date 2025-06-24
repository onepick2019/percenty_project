# -*- coding: utf-8 -*-
"""
market_id 시트의 구조를 확인하는 스크립트
"""

import pandas as pd
import os

def check_market_id_sheet():
    """market_id 시트의 구조 확인"""
    excel_path = "c:\\Projects\\percenty_project\\percenty_id.xlsx"
    
    if not os.path.exists(excel_path):
        print(f"Excel 파일을 찾을 수 없습니다: {excel_path}")
        return
    
    try:
        # Excel 파일의 모든 시트명 확인
        excel_file = pd.ExcelFile(excel_path)
        print(f"=== Excel 파일 분석: {excel_path} ===")
        print(f"시트 목록: {excel_file.sheet_names}")
        
        # market_id 시트가 있는지 확인
        if 'market_id' not in excel_file.sheet_names:
            print("❌ 'market_id' 시트가 없습니다.")
            return
        
        # market_id 시트 읽기
        df = pd.read_excel(excel_path, sheet_name='market_id')
        print(f"\n=== market_id 시트 분석 ===")
        print(f"행 수: {len(df)}")
        print(f"열 수: {len(df.columns)}")
        print(f"컬럼명: {list(df.columns)}")
        
        # 처음 5행 데이터 표시
        print("\n=== 처음 5행 데이터 ===")
        print(df.head(5).to_string())
        
        # onepick2019@gmail.com 계정의 데이터만 필터링
        account_id = 'onepick2019@gmail.com'
        account_rows = df[df['id'] == account_id]
        
        if not account_rows.empty:
            print(f"\n=== {account_id} 계정 데이터 ({len(account_rows)}개 행) ===")
            for idx, row in account_rows.iterrows():
                print(f"\n--- 행 {idx+2} (Excel 행 번호) ---")
                for col in df.columns:
                    value = row[col]
                    if pd.notna(value) and str(value).strip():
                        print(f"{col}: {value}")
                    else:
                        print(f"{col}: (빈값)")
        else:
            print(f"\n❌ {account_id} 계정 데이터를 찾을 수 없습니다.")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_market_id_sheet()