# -*- coding: utf-8 -*-
"""
퍼센티 계정 관리자

여러 계정 정보를 관리하고 선택할 수 있는 기능을 제공합니다.
"""

import os
import json
import logging
import pandas as pd
import time

logger = logging.getLogger(__name__)

class AccountManager:
    """퍼센티 계정 정보를 관리하는 클래스"""
    
    def __init__(self, accounts_file=None):
        """
        초기화
        
        Args:
            accounts_file (str, optional): 계정 정보가 저장된 파일 경로
                                         기본값은 None이며, 이 경우 내장된 계정 정보를 사용합니다.
        """
        self.accounts = {}
        self.accounts_file = accounts_file
        
        # 계정 정보 로드
        self._load_accounts()
    
    def _load_accounts(self):
        """계정 정보 로드"""
        try:
            # 파일에서 계정 정보 로드 시도
            if self.accounts_file and os.path.exists(self.accounts_file):
                try:
                    with open(self.accounts_file, 'r', encoding='utf-8') as f:
                        self.accounts = json.load(f)
                    logger.info(f"계정 정보를 파일에서 로드했습니다: {len(self.accounts)}개 계정")
                except Exception as e:
                    logger.error(f"계정 정보 파일 로드 중 오류: {str(e)}")
                    self._use_default_accounts()
            else:
                # 파일이 없으면 기본 계정 사용
                self._use_default_accounts()
            
            # Excel 파일에서 비밀번호 로드
            self._load_passwords_from_excel()
            
        except Exception as e:
            logger.error(f"계정 정보 로드 중 오류: {str(e)}")
            self._use_default_accounts()
    
    def _use_default_accounts(self):
        """기본 계정 정보 설정"""
        # 기본 계정 정보
        self.accounts = {
            "1": {
                "name": "계정 1",
                "id": "onepick2019@gmail.com",
                "password": "",  # Excel 파일에서 로드될 예정
                "description": "퍼센티 기본 계정"
            },
            "2": {
                "name": "계정 2",
                "id": "wop31garam@gmail.com",
                "password": "",
                "description": "추가 계정 1"
            },
            "3": {
                "name": "계정 3",
                "id": "wop32gsung@gmail.com",
                "password": "",
                "description": "추가 계정 2"
            },
            "4": {
                "name": "계정 4",
                "id": "wop33gogos@gmail.com",
                "password": "",
                "description": "추가 계정 3"
            }
        }
        logger.info("기본 계정 정보를 사용합니다.")
        
        # Excel 파일에서 비밀번호 로드
        self._load_passwords_from_excel()
    
    def save_accounts(self, file_path=None):
        """
        계정 정보 저장
        
        Args:
            file_path (str, optional): 저장할 파일 경로. 기본값은 None이며, 
                                      이 경우 초기화 시 설정한 파일 경로를 사용합니다.
        
        Returns:
            bool: 저장 성공 여부
        """
        try:
            save_path = file_path or self.accounts_file
            if not save_path:
                logger.warning("저장할 파일 경로가 지정되지 않았습니다.")
                return False
            
            # 디렉토리 확인 및 생성
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(self.accounts, f, ensure_ascii=False, indent=4)
            
            logger.info(f"계정 정보를 파일에 저장했습니다: {save_path}")
            return True
        except Exception as e:
            logger.error(f"계정 정보 저장 중 오류: {str(e)}")
            return False
    
    def get_account_list(self):
        """
        계정 목록 반환
        
        Returns:
            list: (계정ID, 계정정보) 튜플의 리스트
        """
        return [(account_id, account_info) for account_id, account_info in self.accounts.items()]
    
    def get_account(self, account_id):
        """
        계정 정보 반환
        
        Args:
            account_id (str): 계정 ID
        
        Returns:
            dict: 계정 정보 (없으면 None)
        """
        return self.accounts.get(account_id)
    
    def add_account(self, account_info):
        """
        계정 추가
        
        Args:
            account_info (dict): 계정 정보
        
        Returns:
            str: 추가된 계정의 ID
        """
        try:
            # 새 계정 ID 생성
            new_id = str(len(self.accounts) + 1)
            while new_id in self.accounts:
                new_id = str(int(new_id) + 1)
            
            # 계정 정보 유효성 검사
            if not account_info.get("id") or not account_info.get("password"):
                logger.error("계정 정보가 유효하지 않습니다: ID와 비밀번호는 필수입니다.")
                return None
            
            # 계정 추가
            self.accounts[new_id] = account_info
            logger.info(f"새 계정이 추가되었습니다: {account_info.get('name') or account_info.get('id')}")
            
            return new_id
        except Exception as e:
            logger.error(f"계정 추가 중 오류: {str(e)}")
            return None
    
    def update_account(self, account_id, account_info):
        """
        계정 정보 업데이트
        
        Args:
            account_id (str): 계정 ID
            account_info (dict): 업데이트할 계정 정보
        
        Returns:
            bool: 업데이트 성공 여부
        """
        try:
            if account_id not in self.accounts:
                logger.error(f"계정 ID가 존재하지 않습니다: {account_id}")
                return False
            
            # 계정 정보 업데이트
            self.accounts[account_id].update(account_info)
            logger.info(f"계정 정보가 업데이트되었습니다: {self.accounts[account_id].get('name') or self.accounts[account_id].get('id')}")
            
            return True
        except Exception as e:
            logger.error(f"계정 정보 업데이트 중 오류: {str(e)}")
            return False
    
    def delete_account(self, account_id):
        """
        계정 삭제
        
        Args:
            account_id (str): 계정 ID
        
        Returns:
            bool: 삭제 성공 여부
        """
        try:
            if account_id not in self.accounts:
                logger.error(f"계정 ID가 존재하지 않습니다: {account_id}")
                return False
            
            # 계정 삭제
            account_info = self.accounts.pop(account_id)
            logger.info(f"계정이 삭제되었습니다: {account_info.get('name') or account_info.get('id')}")
            
            return True
        except Exception as e:
            logger.error(f"계정 삭제 중 오류: {str(e)}")
            return False
            
    def _load_passwords_from_excel(self):
        """
        Excel 파일에서 계정 비밀번호 로드
        
        percenty_id.xlsx 파일에서 계정 이메일(A열)과 비밀번호(B열) 정보를 읽어와 계정 정보 업데이트
        """
        try:
            # Excel 파일 경로
            excel_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "percenty_id.xlsx")
            
            if not os.path.exists(excel_path):
                logger.warning(f"계정 정보 Excel 파일이 존재하지 않습니다: {excel_path}")
                return
            
            # Excel 파일 읽기
            df = pd.read_excel(excel_path, engine='openpyxl')
            
            if len(df) == 0:
                logger.warning("Excel 파일에 계정 정보가 없습니다.")
                return
                
            # 로그 출력
            logger.info(f"Excel 파일에서 {len(df)}개의 계정 정보를 읽었습니다.")
            
            # 이메일과 비밀번호 열 이름 추출
            # 기본적으로 A열, B열 사용
            email_col = df.columns[0] if len(df.columns) > 0 else None
            password_col = df.columns[1] if len(df.columns) > 1 else None
            
            if email_col is None or password_col is None:
                logger.error("Excel 파일 형식이 올바르지 않습니다. 첫 번째 열은 이메일, 두 번째 열은 비밀번호여야 합니다.")
                return
            
            # 각 행의 이메일과 비밀번호로 계정 정보 업데이트
            updated_count = 0
            for _, row in df.iterrows():
                email = str(row[email_col]).strip()
                password = str(row[password_col]).strip()
                
                # 계정 ID 찾기
                account_id, account_info = self.get_account_by_email(email)
                
                if account_id and account_info:
                    # 계정 비밀번호 업데이트
                    self.accounts[account_id]["password"] = password
                    updated_count += 1
                    logger.info(f"계정 비밀번호가 업데이트되었습니다: {email}")
            
            logger.info(f"총 {updated_count}개 계정의 비밀번호가 업데이트되었습니다.")
            
        except Exception as e:
            logger.error(f"Excel 파일에서 비밀번호 로드 중 오류: {str(e)}")
            # 디버깅용 상세 오류 정보
            import traceback
            logger.error(traceback.format_exc())
    
    def get_formatted_account_list(self):
        """
        포맷된 계정 목록 문자열 반환
        
        Returns:
            str: 포맷된 계정 목록 문자열
        """
        account_list = ["=" * 50, "퍼센티 계정 목록", "=" * 50]
        
        for account_id, account_info in self.accounts.items():
            account_name = account_info.get("name", "")
            account_email = account_info.get("id", "")
            account_list.append(f"{account_id}. {account_name} ({account_email})")
        
        account_list.append("=" * 50)
        return "\n".join(account_list)
    
    def get_account_by_email(self, email):
        """
        이메일로 계정 정보 검색
        
        Args:
            email (str): 이메일
        
        Returns:
            tuple: (계정ID, 계정정보) 튜플 (없으면 (None, None))
        """
        for account_id, account_info in self.accounts.items():
            if account_info.get("id") == email:
                return account_id, account_info
        
        return None, None
