#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
카페24 11번가 상품 가져오기 기능 디버깅 테스트 파일

이 파일은 업로드 워크플로우와 독립적으로 카페24 11번가 상품 가져오기 기능을 테스트하고 디버깅할 수 있습니다.
"""

import logging
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from market_manager_cafe24 import MarketManagerCafe24

class Cafe24DebugTester:
    def __init__(self):
        self.setup_logging()
        self.driver = None
        self.market_manager = None
        self.test_config = None
        
    def setup_logging(self):
        """로깅 설정"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('cafe24_debug.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_browser(self):
        """브라우저 설정 및 초기화"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.maximize_window()
            
            self.logger.info("브라우저 설정 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"브라우저 설정 실패: {e}")
            return False
            
    def load_test_config(self):
        """테스트 설정 로드 (percenty_id.xlsx에서)"""
        try:
            # percenty_id.xlsx 파일에서 설정 로드
            df = pd.read_excel('percenty_id.xlsx')
            
            if df.empty:
                self.logger.error("percenty_id.xlsx 파일이 비어있습니다")
                return False
                
            # 첫 번째 행의 데이터 사용
            row = df.iloc[0]
            
            # 실제 엑셀 파일의 컬럼명에 맞게 수정
            # 현재 엑셀에는 cafe24 관련 컬럼이 없으므로 임시로 기본값 설정
            self.test_config = {
                'cafe24_id': row.get('cafe24_id', ''),  # R열
                'cafe24_password': row.get('cafe24_password', ''),  # S열
                'store_11st_id': row.get('11store_id', '')  # T열 (11번가 스토어 ID)
            }
            
            # 엑셀 파일에 해당 컬럼이 없는 경우 기본값으로 테스트
            if not any([self.test_config['cafe24_id'], self.test_config['cafe24_password'], self.test_config['store_11st_id']]):
                self.logger.warning("엑셀 파일에 카페24/11번가 설정이 없습니다. 테스트용 기본값을 사용합니다.")
                self.test_config = {
                    'cafe24_id': 'test_cafe24_id',  # 테스트용 기본값
                    'cafe24_password': 'test_password',  # 테스트용 기본값
                    'store_11st_id': 'test_store_id'  # 테스트용 기본값
                }
            
            # 설정 검증
            if not all([self.test_config['cafe24_id'], 
                       self.test_config['cafe24_password'], 
                       self.test_config['store_11st_id']]):
                self.logger.error("필수 설정 정보가 누락되었습니다")
                self.logger.error(f"카페24 ID: {self.test_config['cafe24_id']}")
                self.logger.error(f"카페24 PW: {'*' * len(self.test_config['cafe24_password']) if self.test_config['cafe24_password'] else '없음'}")
                self.logger.error(f"11번가 스토어 ID: {self.test_config['store_11st_id']}")
                return False
                
            self.logger.info("테스트 설정 로드 완료")
            self.logger.info(f"카페24 ID: {self.test_config['cafe24_id']}")
            self.logger.info(f"11번가 스토어 ID: {self.test_config['store_11st_id']}")
            return True
            
        except Exception as e:
            self.logger.error(f"테스트 설정 로드 실패: {e}")
            return False
            
    def test_cafe24_import(self):
        """카페24 11번가 상품 가져오기 전체 테스트"""
        try:
            self.logger.info("=== 카페24 11번가 상품 가져오기 테스트 시작 ===")
            
            # 1. 브라우저 설정
            if not self.setup_browser():
                return False
                
            # 2. 테스트 설정 로드
            if not self.load_test_config():
                return False
                
            # 3. MarketManagerCafe24 초기화
            self.market_manager = MarketManagerCafe24(self.driver)
            
            # 4. 카페24 로그인 및 11번가 상품 가져오기 실행
            self.logger.info("카페24 로그인 시작")
            if not self.market_manager.login_and_import_11st_products(
                self.test_config['cafe24_id'], 
                self.test_config['cafe24_password'],
                self.test_config['store_11st_id']
            ):
                self.logger.error("카페24 로그인 및 11번가 상품 가져오기 실패")
                return False
                
            self.logger.info("=== 카페24 11번가 상품 가져오기 테스트 완료 ===")
            return True
            
        except Exception as e:
            self.logger.error(f"테스트 실행 중 오류 발생: {e}")
            return False
            
        finally:
            if self.driver:
                self.logger.info("브라우저 종료")
                self.driver.quit()
                
    def test_step_by_step(self):
        """단계별 디버깅 테스트"""
        try:
            self.logger.info("=== 단계별 디버깅 테스트 시작 ===")
            
            # 1. 브라우저 설정
            if not self.setup_browser():
                return False
                
            # 2. 테스트 설정 로드
            if not self.load_test_config():
                return False
                
            # 3. MarketManagerCafe24 초기화
            self.market_manager = MarketManagerCafe24(self.driver)
            
            # 단계별 실행 목록 (실제 사용 가능한 메서드만)
            steps = [
                ("카페24 로그인 및 11번가 상품 가져오기 전체 실행", lambda: self.market_manager.login_and_import_11st_products(
                    self.test_config['cafe24_id'], 
                    self.test_config['cafe24_password'],
                    self.test_config['store_11st_id']
                ))
            ]
            
            for step_name, step_func in steps:
                self.logger.info(f"단계 실행: {step_name}")
                
                # 사용자 입력 대기
                input(f"'{step_name}' 단계를 실행하려면 Enter를 누르세요...")
                
                try:
                    result = step_func()
                    if result:
                        self.logger.info(f"✓ {step_name} 성공")
                    else:
                        self.logger.error(f"✗ {step_name} 실패")
                        
                        # 실패 시 계속 진행할지 묻기
                        continue_test = input("계속 진행하시겠습니까? (y/n): ")
                        if continue_test.lower() != 'y':
                            break
                            
                except Exception as e:
                    self.logger.error(f"✗ {step_name} 오류: {e}")
                    
                    # 오류 시 계속 진행할지 묻기
                    continue_test = input("계속 진행하시겠습니까? (y/n): ")
                    if continue_test.lower() != 'y':
                        break
                        
                # 각 단계 후 잠시 대기
                time.sleep(2)
                
            self.logger.info("=== 단계별 디버깅 테스트 완료 ===")
            return True
            
        except Exception as e:
            self.logger.error(f"단계별 테스트 실행 중 오류 발생: {e}")
            return False
            
        finally:
            if self.driver:
                # 브라우저를 닫을지 묻기
                close_browser = input("브라우저를 닫으시겠습니까? (y/n): ")
                if close_browser.lower() == 'y':
                    self.logger.info("브라우저 종료")
                    self.driver.quit()
                else:
                    self.logger.info("브라우저를 열어둡니다. 수동으로 확인하세요.")

def main():
    """메인 함수"""
    tester = Cafe24DebugTester()
    
    print("카페24 11번가 상품 가져오기 디버깅 테스트")
    print("1. 전체 테스트 (자동 실행)")
    print("2. 단계별 테스트 (수동 진행)")
    
    choice = input("선택하세요 (1 또는 2): ")
    
    if choice == '1':
        success = tester.test_cafe24_import()
        if success:
            print("✓ 전체 테스트 성공")
        else:
            print("✗ 전체 테스트 실패")
            
    elif choice == '2':
        success = tester.test_step_by_step()
        if success:
            print("✓ 단계별 테스트 완료")
        else:
            print("✗ 단계별 테스트 실패")
            
    else:
        print("잘못된 선택입니다.")

if __name__ == "__main__":
    main()