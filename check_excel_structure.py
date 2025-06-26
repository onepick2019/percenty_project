#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
엑셀 파일 구조 확인 스크립트
"""

import pandas as pd
import sys

def check_excel_structure():
    try:
        # percenty_id.xlsx 파일 읽기
        df = pd.read_excel('percenty_id.xlsx')
        
        print("=== 엑셀 파일 구조 분석 ===")
        print(f"총 행 수: {len(df)}")
        print(f"총 열 수: {len(df.columns)}")
        print("\n=== 컬럼명 목록 ===")
        for i, col in enumerate(df.columns):
            print(f"{i+1}. {col}")
            
        print("\n=== 첫 번째 행 데이터 ===")
        if not df.empty:
            first_row = df.iloc[0]
            for col in df.columns:
                value = first_row[col]
                if pd.isna(value):
                    value = "(비어있음)"
                print(f"{col}: {value}")
        else:
            print("데이터가 없습니다.")
            
        print("\n=== 카페24 관련 컬럼 검색 ===")
        cafe24_cols = [col for col in df.columns if 'cafe24' in col.lower() or '카페24' in col]
        if cafe24_cols:
            print("카페24 관련 컬럼:")
            for col in cafe24_cols:
                print(f"  - {col}")
        else:
            print("카페24 관련 컬럼을 찾을 수 없습니다.")
            
        print("\n=== 11번가 관련 컬럼 검색 ===")
        elevenst_cols = [col for col in df.columns if '11st' in col.lower() or '11번가' in col]
        if elevenst_cols:
            print("11번가 관련 컬럼:")
            for col in elevenst_cols:
                print(f"  - {col}")
        else:
            print("11번가 관련 컬럼을 찾을 수 없습니다.")
            
        print("\n=== ID/PW 관련 컬럼 검색 ===")
        id_pw_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['id', 'pw', 'password', '아이디', '비밀번호'])]
        if id_pw_cols:
            print("ID/PW 관련 컬럼:")
            for col in id_pw_cols:
                print(f"  - {col}")
        else:
            print("ID/PW 관련 컬럼을 찾을 수 없습니다.")
            
        return True
        
    except FileNotFoundError:
        print("오류: percenty_id.xlsx 파일을 찾을 수 없습니다.")
        return False
    except Exception as e:
        print(f"오류 발생: {e}")
        return False

if __name__ == "__main__":
    check_excel_structure()