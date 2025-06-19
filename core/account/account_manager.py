#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
계정 관리 모듈
기존 account_manager.py의 기능을 확장한 통합 계정 관리자
"""

import os
import sys
import logging
import pandas as pd
from typing import Dict, List, Optional, Union

# 루트 디렉토리를 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 기존 모듈들 임포트
from account_manager import AccountManager as LegacyAccountManager

logger = logging.getLogger(__name__)

class CoreAccountManager:
    """
    통합 계정 관리자
    기존 AccountManager의 기능을 확장하여 다중 계정 관리 지원
    """
    
    def __init__(self, excel_file: str = None):
        """
        초기화
        
        Args:
            excel_file: 계정 정보가 담긴 엑셀 파일 경로
        """
        self.excel_file = excel_file or "percenty_id.xlsx"
        self.accounts = {}
        self.active_accounts = []
        
        # 기존 AccountManager와의 호환성
        self.legacy_manager = None
        
        self.load_accounts()
    
    def load_accounts(self):
        """
        엑셀 파일에서 계정 정보 로드
        """
        try:
            if not os.path.exists(self.excel_file):
                logger.warning(f"계정 파일을 찾을 수 없습니다: {self.excel_file}")
                return
            
            # 기존 AccountManager 사용
            self.legacy_manager = LegacyAccountManager(self.excel_file)
            
            # 엑셀 파일 직접 읽기
            df = pd.read_excel(self.excel_file)
            
            # 컬럼명 매핑 (다양한 컬럼명 지원)
            column_mapping = {
                'email': ['email', 'Email', 'EMAIL', '이메일', 'id', 'ID'],
                'password': ['password', 'Password', 'PASSWORD', '비밀번호', 'pwd', 'PWD'],
                'name': ['name', 'Name', 'NAME', '이름', 'username', 'Username'],
                'active': ['active', 'Active', 'ACTIVE', '활성', 'enabled', 'Enabled']
            }
            
            # 실제 컬럼명 찾기
            actual_columns = {}
            for key, possible_names in column_mapping.items():
                for col_name in possible_names:
                    if col_name in df.columns:
                        actual_columns[key] = col_name
                        break
            
            logger.info(f"엑셀 파일 컬럼: {df.columns.tolist()}")
            logger.info(f"매핑된 컬럼: {actual_columns}")
            
            for index, row in df.iterrows():
                account_id = f"account_{index + 1}"
                
                # 이메일 (필수)
                email = ''
                if 'email' in actual_columns:
                    email = str(row.get(actual_columns['email'], '')).strip()
                elif len(df.columns) > 0:
                    # 첫 번째 컬럼을 이메일로 사용
                    email = str(row.iloc[0]).strip() if not pd.isna(row.iloc[0]) else ''
                
                # 비밀번호 (필수)
                password = ''
                if 'password' in actual_columns:
                    password = str(row.get(actual_columns['password'], '')).strip()
                elif len(df.columns) > 1:
                    # 두 번째 컬럼을 비밀번호로 사용
                    password = str(row.iloc[1]).strip() if not pd.isna(row.iloc[1]) else ''
                
                # 이름 (선택)
                name = f'계정 {index + 1}'
                if 'name' in actual_columns:
                    name_value = row.get(actual_columns['name'], '')
                    if not pd.isna(name_value) and str(name_value).strip():
                        name = str(name_value).strip()
                
                # 활성 상태 (선택)
                active = True
                if 'active' in actual_columns:
                    active_value = row.get(actual_columns['active'], True)
                    if not pd.isna(active_value):
                        active = bool(active_value)
                
                # 빈 이메일이나 비밀번호는 건너뛰기
                if not email or not password or email == 'nan' or password == 'nan':
                    logger.warning(f"행 {index + 1}: 이메일 또는 비밀번호가 비어있어 건너뜁니다. (email: '{email}', password: '{password}')")
                    continue
                
                account_info = {
                    'id': account_id,
                    'email': email,
                    'password': password,
                    'name': name,
                    'active': active,
                    'last_used': None,
                    'status': 'ready'
                }
                
                self.accounts[account_id] = account_info
                # 이메일 주소로도 접근 가능하도록 추가 저장 (중복 방지)
                if email != account_id:
                    self.accounts[email] = account_info
                
                if account_info['active']:
                    self.active_accounts.append(account_id)
            
            logger.info(f"계정 {len(self.accounts)}개 로드 완료 (활성: {len(self.active_accounts)}개)")
            
        except Exception as e:
            logger.error(f"계정 로드 중 오류: {e}")
            import traceback
            logger.error(f"상세 오류: {traceback.format_exc()}")
            raise
    
    def get_account(self, account_id: str) -> Dict:
        """
        계정 정보 반환
        
        Args:
            account_id: 계정 식별자
            
        Returns:
            Dict: 계정 정보
        """
        if account_id not in self.accounts:
            raise ValueError(f"계정 ID '{account_id}'를 찾을 수 없습니다.")
        
        return self.accounts[account_id].copy()
    
    def get_account_credentials(self, account_id: str) -> tuple:
        """
        계정 로그인 정보 반환
        
        Args:
            account_id: 계정 식별자
            
        Returns:
            tuple: (email, password)
        """
        account = self.get_account(account_id)
        return account['email'], account['password']
    
    def get_active_accounts(self) -> List[str]:
        """
        활성 계정 목록 반환
        
        Returns:
            List[str]: 활성 계정 ID 목록
        """
        return self.active_accounts.copy()
    
    def get_all_accounts(self) -> List[Dict]:
        """
        전체 계정 목록 반환
        
        Returns:
            List[Dict]: 전체 계정 정보 목록
        """
        return list(self.accounts.values())
    
    def set_account_status(self, account_id: str, status: str):
        """
        계정 상태 설정
        
        Args:
            account_id: 계정 식별자
            status: 상태 ('ready', 'running', 'error', 'completed')
        """
        if account_id not in self.accounts:
            raise ValueError(f"계정 ID '{account_id}'를 찾을 수 없습니다.")
        
        self.accounts[account_id]['status'] = status
        logger.debug(f"계정 '{account_id}' 상태를 '{status}'로 설정")
    
    def get_account_status(self, account_id: str) -> str:
        """
        계정 상태 반환
        
        Args:
            account_id: 계정 식별자
            
        Returns:
            str: 계정 상태
        """
        account = self.get_account(account_id)
        return account['status']
    
    def activate_account(self, account_id: str):
        """
        계정 활성화
        
        Args:
            account_id: 계정 식별자
        """
        if account_id not in self.accounts:
            raise ValueError(f"계정 ID '{account_id}'를 찾을 수 없습니다.")
        
        self.accounts[account_id]['active'] = True
        
        if account_id not in self.active_accounts:
            self.active_accounts.append(account_id)
        
        logger.info(f"계정 '{account_id}' 활성화")
    
    def deactivate_account(self, account_id: str):
        """
        계정 비활성화
        
        Args:
            account_id: 계정 식별자
        """
        if account_id not in self.accounts:
            raise ValueError(f"계정 ID '{account_id}'를 찾을 수 없습니다.")
        
        self.accounts[account_id]['active'] = False
        
        if account_id in self.active_accounts:
            self.active_accounts.remove(account_id)
        
        logger.info(f"계정 '{account_id}' 비활성화")
    
    def get_account_by_email(self, email: str) -> Optional[str]:
        """
        이메일로 계정 ID 찾기
        
        Args:
            email: 이메일 주소
            
        Returns:
            Optional[str]: 계정 ID (없으면 None)
        """
        for account_id, account_info in self.accounts.items():
            if account_info['email'] == email:
                return account_id
        return None
    
    def update_password(self, account_id: str, new_password: str):
        """
        계정 비밀번호 업데이트
        
        Args:
            account_id: 계정 식별자
            new_password: 새 비밀번호
        """
        if account_id not in self.accounts:
            raise ValueError(f"계정 ID '{account_id}'를 찾을 수 없습니다.")
        
        self.accounts[account_id]['password'] = new_password
        logger.info(f"계정 '{account_id}' 비밀번호 업데이트")
    
    def get_legacy_manager(self):
        """
        기존 AccountManager 인스턴스 반환 (호환성)
        
        Returns:
            AccountManager: 기존 AccountManager 인스턴스
        """
        return self.legacy_manager
    
    def get_account_summary(self) -> Dict:
        """
        계정 요약 정보 반환
        
        Returns:
            Dict: 계정 요약 정보
        """
        summary = {
            'total': len(self.accounts),
            'active': len(self.active_accounts),
            'inactive': len(self.accounts) - len(self.active_accounts),
            'status_counts': {}
        }
        
        # 상태별 카운트
        for account_info in self.accounts.values():
            status = account_info['status']
            summary['status_counts'][status] = summary['status_counts'].get(status, 0) + 1
        
        return summary
    
    def reload_accounts(self):
        """
        계정 정보 다시 로드
        """
        self.accounts.clear()
        self.active_accounts.clear()
        self.load_accounts()
        logger.info("계정 정보 다시 로드 완료")

# 하위 호환성을 위한 함수들
def get_account_manager_legacy(excel_file=None):
    """기존 코드와의 호환성을 위한 함수"""
    manager = CoreAccountManager(excel_file)
    return manager.get_legacy_manager()

if __name__ == "__main__":
    # 테스트 코드
    print("계정 관리자 모듈 테스트")
    logger.info("계정 관리자 모듈이 로드되었습니다.")