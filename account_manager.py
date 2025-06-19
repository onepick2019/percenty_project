# -*- coding: utf-8 -*-
"""
퍼센티 계정 관리 모듈

이 모듈은 percenty_id.xlsx 파일에서 계정 정보를 읽고 관리합니다.
"""

import os
import pandas as pd
import logging

class AccountManager:
    """퍼센티 계정 관리 클래스"""
    
    def __init__(self, excel_path="percenty_id.xlsx", sheet_name="login_id"):
        """
        초기화
        
        Args:
            excel_path (str): Excel 파일 경로
            sheet_name (str): 시트 이름
        """
        self.excel_path = excel_path
        self.sheet_name = sheet_name
        self.accounts = []
        self.selected_account = None
        
        # 로깅 설정
        logging.getLogger(__name__)
        
    def load_accounts(self):
        """
        Excel 파일에서 계정 정보 로드
        
        Returns:
            bool: 로드 성공 여부
        """
        try:
            if not os.path.exists(self.excel_path):
                logging.error(f"계정 파일을 찾을 수 없습니다: {self.excel_path}")
                return False
                
            # Excel 파일 읽기
            df = pd.read_excel(self.excel_path, sheet_name=self.sheet_name)
            
            # 필수 열 확인
            required_columns = ['id', 'password']
            for col in required_columns:
                if col not in df.columns:
                    logging.error(f"계정 파일에 필수 열이 없습니다: {col}")
                    return False
            
            # 계정 정보 저장
            self.accounts = []
            for idx, row in df.iterrows():
                account = {
                    'id': row['id'],
                    'password': row['password'],
                    'nickname': row.get('nickname', f"계정 {idx+1}"),
                    'operator': row.get('operator', ''),
                    'server': row.get('server', 'server1')  # 기본값으로 server1 설정
                }
                self.accounts.append(account)
                
            logging.info(f"총 {len(self.accounts)}개의 계정을 로드했습니다.")
            return True
            
        except Exception as e:
            logging.error(f"계정 정보 로드 중 오류 발생: {e}")
            return False
            
    def display_accounts(self):
        """
        사용 가능한 계정 목록 표시
        """
        if not self.accounts:
            print("로드된 계정이 없습니다.")
            return
            
        print("\n" + "=" * 50)
        print("퍼센티 계정 목록")
        print("=" * 50)
        
        for idx, account in enumerate(self.accounts):
            nickname = account.get('nickname', f"계정 {idx+1}")
            print(f"{idx+1}. {nickname} ({account['id']})")
            
        print("=" * 50)
        
    def select_account(self):
        """
        사용자가 계정을 선택하도록 함
        
        Returns:
            dict: 선택된 계정 정보 (취소 시 None)
        """
        if not self.accounts:
            print("선택 가능한 계정이 없습니다.")
            return None
            
        while True:
            self.display_accounts()
            selection = input("\n사용할 계정 번호를 입력하세요 (종료하려면 'q' 입력): ")
            
            if selection.lower() == 'q':
                return None
                
            try:
                idx = int(selection) - 1
                if 0 <= idx < len(self.accounts):
                    self.selected_account = self.accounts[idx]
                    print(f"\n'{self.selected_account.get('nickname')}' 계정을 선택했습니다.")
                    return self.selected_account
                else:
                    print(f"유효하지 않은 번호입니다. 1-{len(self.accounts)} 사이의 번호를 입력하세요.")
            except ValueError:
                print("숫자를 입력하세요.")
                
    def get_selected_account(self):
        """
        현재 선택된 계정 반환
        
        Returns:
            dict: 선택된 계정 정보
        """
        return self.selected_account
    
    def get_accounts(self):
        """
        모든 계정 목록 반환
        
        Returns:
            list: 계정 정보 리스트
        """
        # 계정이 로드되지 않았다면 자동으로 로드
        if not self.accounts:
            self.load_accounts()
        
        return self.accounts

# 직접 실행 시 테스트
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    manager = AccountManager()
    if manager.load_accounts():
        account = manager.select_account()
        if account:
            print(f"선택된 계정: {account['id']}")
        else:
            print("계정 선택이 취소되었습니다.")
    else:
        print("계정 정보를 로드할 수 없습니다.")
