# -*- coding: utf-8 -*-
"""
카페24 11번가 상품 가져오기 기능 빠른 테스트 파일

기존 디버깅 파일에서 마켓정보 키입력과 업로드 부분을 제거하고
카페24 메서드만 바로 실행되도록 간소화한 버전입니다.
"""

import logging
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from market_manager_cafe24 import MarketManagerCafe24

class Cafe24QuickTester:
    def __init__(self):
        self.setup_logging()
        self.driver = None
        self.market_manager = None
        
    def setup_logging(self):
        """로깅 설정"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('cafe24_quick_test.log', encoding='utf-8'),
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
            
    def get_test_config(self):
        """테스트 설정 로드 (엑셀 파일 또는 기본값 사용)"""
        try:
            # 먼저 엑셀 파일에서 설정 시도 (market_id 시트의 Q열, R열 사용)
            try:
                df = pd.read_excel('percenty_id.xlsx', sheet_name='market_id')
                if not df.empty:
                    row = df.iloc[0]
                    
                    # market_id 시트에서 카페24 관련 컬럼 찾기
                    cafe24_id = ''
                    cafe24_password = ''
                    store_11st_id = ''
                    
                    # Q열(cafe24_id)과 R열(cafe24_password) 사용
                    if 'cafe24_id' in df.columns and 'cafe24_password' in df.columns:
                        cafe24_id = str(row['cafe24_id']) if pd.notna(row['cafe24_id']) else ''
                        cafe24_password = str(row['cafe24_password']) if pd.notna(row['cafe24_password']) else ''
                        
                        # 11store_id 컬럼도 있으면 사용
                        if '11store_id' in df.columns:
                            store_11st_id = str(row['11store_id']) if pd.notna(row['11store_id']) else 'test_store_id'
                        else:
                            store_11st_id = 'test_store_id'  # 임시 스토어 ID
                    
                    if all([cafe24_id, cafe24_password]):
                        config = {
                            'cafe24_id': cafe24_id,
                            'cafe24_password': cafe24_password,
                            'store_11st_id': store_11st_id
                        }
                        self.logger.info(f"엑셀에서 설정 로드 완료 - 카페24 ID: {cafe24_id}, 11번가 스토어 ID: {store_11st_id}")
                        return config
                        
            except Exception as e:
                self.logger.warning(f"엑셀 파일 로드 실패: {e}")
            
            # 엑셀에서 로드 실패 시 테스트용 기본값 사용
            self.logger.warning("엑셀에서 설정을 찾을 수 없습니다. 테스트용 기본값을 사용합니다.")
            self.logger.info("실제 테스트를 위해서는 다음 중 하나를 수행하세요:")
            self.logger.info("1. percenty_id.xlsx 파일에 cafe24_id, cafe24_password, 11store_id 컬럼 추가")
            self.logger.info("2. 아래 기본값을 실제 값으로 수정")
            
            config = {
                'cafe24_id': 'your_cafe24_id',  # 실제 카페24 ID로 변경
                'cafe24_password': 'your_cafe24_password',  # 실제 카페24 비밀번호로 변경
                'store_11st_id': 'your_11st_store_id'  # 실제 11번가 스토어 ID로 변경
            }
            
            self.logger.info(f"기본 설정 사용 - 카페24 ID: {config['cafe24_id']}, 11번가 스토어 ID: {config['store_11st_id']}")
            return config
            
        except Exception as e:
            self.logger.error(f"설정 로드 실패: {e}")
            return None
            
    def run_cafe24_test(self):
        """카페24 11번가 상품 가져오기 테스트 실행"""
        try:
            self.logger.info("=== 카페24 11번가 상품 가져오기 빠른 테스트 시작 ===")
            
            # 1. 브라우저 설정
            if not self.setup_browser():
                return False
                
            # 2. 테스트 설정 입력
            config = self.get_test_config()
            if not config:
                return False
                
            # 3. MarketManagerCafe24 초기화
            self.market_manager = MarketManagerCafe24(self.driver)
            
            # 4. 카페24 로그인 및 11번가 상품 가져오기 실행
            self.logger.info("카페24 로그인 및 상품 가져오기 시작")
            result = self.market_manager.login_and_import_11st_products(
                config['cafe24_id'], 
                config['cafe24_password'],
                config['store_11st_id']
            )
            
            if result:
                self.logger.info("✓ 카페24 11번가 상품 가져오기 성공")
            else:
                self.logger.error("✗ 카페24 11번가 상품 가져오기 실패")
                
            self.logger.info("=== 카페24 11번가 상품 가져오기 빠른 테스트 완료 ===")
            return result
            
        except Exception as e:
            self.logger.error(f"테스트 실행 중 오류 발생: {e}")
            return False
            
        finally:
            if self.driver:
                # 결과 확인을 위해 잠시 대기
                time.sleep(3)
                self.logger.info("브라우저 종료")
                self.driver.quit()

def main():
    """메인 함수"""
    tester = Cafe24QuickTester()
    
    print("카페24 11번가 상품 가져오기 빠른 테스트")
    print("이 테스트는 마켓정보 키입력과 업로드 과정을 건너뛰고")
    print("카페24 메서드만 바로 실행합니다.")
    print("자동으로 테스트를 시작합니다...")
    print()
    
    success = tester.run_cafe24_test()
    if success:
        print("\n✓ 테스트 성공")
    else:
        print("\n✗ 테스트 실패")

if __name__ == "__main__":
    main()