# -*- coding: utf-8 -*-
"""
카페24 11번가 상품 가져오기 간단 테스트
기존 product_editor_core6_1_dynamic.py의 카페24 기능을 활용한 테스트
"""

import logging
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class SimpleCafe24Test:
    def __init__(self):
        self.setup_logging()
        self.driver = None
        self.product_editor = None
        
    def setup_logging(self):
        """로깅 설정"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('cafe24_simple_test.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_browser(self):
        """브라우저 설정"""
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
    
    def load_config_from_excel(self):
        """엑셀에서 카페24 설정 로드"""
        try:
            # percenty_id.xlsx 파일에서 설정 로드
            df = pd.read_excel('percenty_id.xlsx')
            
            if df.empty:
                self.logger.error("percenty_id.xlsx 파일이 비어있습니다")
                return None
                
            # 첫 번째 행의 데이터 사용
            row = df.iloc[0]
            
            # 카페24 관련 컬럼 검색
            cafe24_id_col = None
            cafe24_pw_col = None
            store_11st_col = None
            
            for col in df.columns:
                col_lower = str(col).lower()
                if 'cafe24' in col_lower and ('id' in col_lower or 'server' in col_lower):
                    cafe24_id_col = col
                elif 'cafe24' in col_lower and ('pw' in col_lower or 'password' in col_lower):
                    cafe24_pw_col = col
                elif '11st' in col_lower or '11store' in col_lower:
                    store_11st_col = col
            
            # 설정 구성
            config = {
                'cafe24_id': row.get(cafe24_id_col, '') if cafe24_id_col else '',
                'cafe24_password': row.get(cafe24_pw_col, '') if cafe24_pw_col else '',
                '11store_id': row.get(store_11st_col, '') if store_11st_col else ''
            }
            
            # 엑셀에 설정이 없는 경우 사용자 입력
            if not any([config['cafe24_id'], config['cafe24_password'], config['11store_id']]):
                self.logger.warning("엑셀 파일에 카페24/11번가 설정이 없습니다.")
                self.logger.info("실제 테스트를 위해 다음 정보를 입력하세요:")
                
                cafe24_id = input("카페24 아이디를 입력하세요: ").strip()
                cafe24_password = input("카페24 비밀번호를 입력하세요: ").strip()
                store_11st_id = input("11번가 스토어 ID를 입력하세요: ").strip()
                
                if cafe24_id and cafe24_password and store_11st_id:
                    config = {
                        'cafe24_id': cafe24_id,
                        'cafe24_password': cafe24_password,
                        '11store_id': store_11st_id
                    }
                else:
                    self.logger.error("필수 정보가 입력되지 않았습니다.")
                    return None
            
            self.logger.info(f"카페24 설정 로드 완료 - ID: {config['cafe24_id']}, 11번가 스토어 ID: {config['11store_id']}")
            return config
            
        except Exception as e:
            self.logger.error(f"설정 로드 실패: {e}")
            return None
    
    def test_cafe24_import(self):
        """카페24 11번가 상품 가져오기 테스트"""
        try:
            self.logger.info("=== 카페24 11번가 상품 가져오기 테스트 시작 ===")
            
            # 1. 브라우저 설정
            if not self.setup_browser():
                return False
            
            # 2. 설정 로드
            config = self.load_config_from_excel()
            if not config:
                return False
            
            # 3. MarketManagerCafe24 인스턴스 생성 및 직접 실행
            from market_manager_cafe24 import MarketManagerCafe24
            cafe24_manager = MarketManagerCafe24(self.driver)
            
            # 4. 카페24 11번가 상품 가져오기 실행
            self.logger.info("카페24 11번가 상품 가져오기 실행")
            result = cafe24_manager.login_and_import_11st_products(
                cafe24_id=config['cafe24_id'],
                cafe24_password=config['cafe24_password'],
                store_id_11st=config['11store_id']
            )
            
            if result:
                self.logger.info("✓ 카페24 11번가 상품 가져오기 성공")
            else:
                self.logger.error("✗ 카페24 11번가 상품 가져오기 실패")
            
            return result
            
        except Exception as e:
            self.logger.error(f"테스트 실행 중 오류 발생: {e}")
            return False
        finally:
            if self.driver:
                self.logger.info("브라우저 종료")
                self.driver.quit()

def main():
    """메인 실행 함수"""
    tester = SimpleCafe24Test()
    success = tester.test_cafe24_import()
    
    if success:
        print("\n✓ 테스트 성공")
    else:
        print("\n✗ 테스트 실패")

if __name__ == "__main__":
    main()