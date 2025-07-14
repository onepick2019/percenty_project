#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
카페24 11번가 상품 가져오기 기능 디버깅 테스트 파일

이 파일은 업로드 워크플로우와 독립적으로 카페24 11번가 상품 가져오기 기능을 테스트하고 디버깅할 수 있습니다.
개선된 디버깅 기능으로 로그인 실패와 모달창 클릭 문제를 해결합니다.
"""

import logging
import time
import pandas as pd
import pyautogui
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from market_manager_cafe24 import MarketManagerCafe24

class Cafe24DebugTester:
    def __init__(self):
        self.setup_logging()
        self.driver = None
        self.market_manager = None
        self.test_config = None
        self.wait = None
        
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
            self.wait = WebDriverWait(self.driver, 10)
            
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
                    'cafe24_id': 'withop',  # 테스트용 기본값
                    'cafe24_password': 'dnjsvlr2019',  # 테스트용 기본값
                    'store_11st_id': 'onepicktaerim3'  # 테스트용 기본값
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
    
    def debug_login_step_by_step(self):
        """로그인 단계별 디버깅 (강제 로그인 페이지 문제 해결 포함)"""
        try:
            self.logger.info("=== 로그인 단계별 디버깅 시작 ===")
            
            # 0. 세션 초기화
            self.logger.info("0단계: 세션 초기화")
            self.logger.info("카페24 메인 페이지로 이동하여 세션 초기화")
            self.driver.get("https://www.cafe24.com")
            time.sleep(2)
            
            # 쿠키 및 세션 정리
            self.driver.delete_all_cookies()
            time.sleep(1)
            self.logger.info("쿠키 및 세션 정리 완료")
            
            # 1. 카페24 로그인 페이지 열기
            self.logger.info("1단계: 카페24 로그인 페이지 열기")
            self.driver.get("https://eclogin.cafe24.com/Shop/?mode=mp")
            time.sleep(5)
            
            # 현재 URL 확인
            current_url = self.driver.current_url
            self.logger.info(f"로그인 페이지 로드 후 URL: {current_url}")
            
            # 강제 로그인 페이지 확인 및 처리
            if "comForce" in current_url:
                self.logger.warning("강제 로그인 페이지 감지. 다른 방법으로 접근 시도")
                
                # 직접 로그인 페이지로 이동
                self.driver.get("https://eclogin.cafe24.com/Shop/")
                time.sleep(3)
                
                current_url = self.driver.current_url
                self.logger.info(f"재시도 후 URL: {current_url}")
                
                # 여전히 강제 로그인 페이지인 경우
                if "comForce" in current_url:
                    self.logger.error("강제 로그인 페이지 우회 실패")
                    self.logger.error("해결 방법: 1) 다른 브라우저 사용 2) 시간을 두고 재시도 3) 카페24 고객센터 문의")
                    return False
            
            # 페이지 소스에서 로그인 요소 확인
            try:
                id_input = self.driver.find_element(By.ID, "mall_id")
                password_input = self.driver.find_element(By.ID, "userpasswd")
                login_button = self.driver.find_element(By.CSS_SELECTOR, "button.btnStrong.large")
                self.logger.info("✓ 로그인 요소들이 정상적으로 발견됨")
            except Exception as e:
                self.logger.error(f"✗ 로그인 요소 찾기 실패: {e}")
                
                # 페이지 소스 일부 확인
                page_source = self.driver.page_source[:1000]
                self.logger.error(f"페이지 소스 일부: {page_source}")
                return False
            
            input("로그인 페이지 확인 완료. 계속하려면 Enter를 누르세요...")
            
            # 2. 로그인 정보 입력
            self.logger.info("2단계: 로그인 정보 입력")
            id_input.clear()
            id_input.send_keys(self.test_config['cafe24_id'])
            self.logger.info(f"아이디 입력 완료: {self.test_config['cafe24_id']}")
            
            password_input.clear()
            password_input.send_keys(self.test_config['cafe24_password'])
            self.logger.info("비밀번호 입력 완료")
            
            input("로그인 정보 입력 완료. 로그인 버튼을 클릭하려면 Enter를 누르세요...")
            
            # 3. 로그인 버튼 클릭
            self.logger.info("3단계: 로그인 버튼 클릭")
            login_button.click()
            self.logger.info("로그인 버튼 클릭 완료")
            
            # 4. 로그인 처리 대기 및 결과 확인
            self.logger.info("4단계: 로그인 처리 대기 (15초)")
            for i in range(15):
                time.sleep(1)
                current_url = self.driver.current_url
                self.logger.info(f"대기 중... {i+1}/15초 - 현재 URL: {current_url}")
                
                # 강제 로그인 페이지로 리다이렉트 확인
                if "comForce" in current_url:
                    self.logger.error(f"강제 로그인 페이지로 리다이렉트됨: {current_url}")
                    self.logger.error("로그인 정보가 잘못되었거나 계정에 문제가 있을 수 있습니다.")
                    return False
                
                # 로그인 성공 확인
                if "mp.cafe24.com" in current_url:
                    self.logger.info(f"✓ 로그인 성공! 최종 URL: {current_url}")
                    return True
            
            # 로그인 실패
            final_url = self.driver.current_url
            self.logger.error(f"✗ 로그인 실패 - 최종 URL: {final_url}")
            
            # 에러 메시지 확인
            try:
                error_elements = self.driver.find_elements(By.CSS_SELECTOR, ".error, .alert, .warning, .msg")
                for element in error_elements:
                    if element.is_displayed() and element.text.strip():
                        self.logger.error(f"에러 메시지: {element.text}")
            except Exception:
                pass
            
            return False
            
        except Exception as e:
            self.logger.error(f"로그인 단계별 디버깅 실패: {e}")
            return False
    
    def debug_modal_click(self):
        """모달창 클릭 디버깅"""
        try:
            self.logger.info("=== 모달창 클릭 디버깅 시작 ===")
            
            # 현재 화면 스크린샷
            screenshot_path = f"modal_debug_{int(time.time())}.png"
            self.driver.save_screenshot(screenshot_path)
            self.logger.info(f"현재 화면 스크린샷 저장: {screenshot_path}")
            
            # 모달창 요소 찾기 시도
            modal_selectors = [
                "button[onclick*='confirm']",
                "button.btn-confirm",
                "button.confirm",
                "input[type='button'][value*='확인']",
                "button:contains('확인')",
                ".modal button",
                ".popup button"
            ]
            
            for selector in modal_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        for i, element in enumerate(elements):
                            if element.is_displayed():
                                self.logger.info(f"발견된 모달 버튼 {i+1}: {selector} - 텍스트: {element.text}")
                                
                                # 버튼 클릭 시도
                                input(f"'{element.text}' 버튼을 클릭하려면 Enter를 누르세요...")
                                try:
                                    element.click()
                                    self.logger.info(f"✓ 버튼 클릭 성공: {element.text}")
                                    time.sleep(3)
                                    return True
                                except Exception as click_error:
                                    self.logger.warning(f"버튼 클릭 실패: {click_error}")
                except Exception:
                    continue
            
            # Selenium으로 찾지 못한 경우 pyautogui 사용
            self.logger.info("Selenium으로 모달 버튼을 찾지 못함. pyautogui 사용")
            
            # 현재 마우스 위치 확인
            current_x, current_y = pyautogui.position()
            self.logger.info(f"현재 마우스 위치: ({current_x}, {current_y})")
            
            # 기본 좌표로 클릭 시도
            click_positions = [
                (1060, 205),  # 기존 좌표
                (960, 400),   # 화면 중앙 근처
                (800, 300),   # 좌측 중앙
                (1200, 300)   # 우측 중앙
            ]
            
            for x, y in click_positions:
                input(f"좌표 ({x}, {y})를 클릭하려면 Enter를 누르세요...")
                try:
                    pyautogui.click(x, y)
                    self.logger.info(f"✓ 좌표 ({x}, {y}) 클릭 완료")
                    time.sleep(3)
                    
                    # Alert 확인
                    try:
                        alert = self.driver.switch_to.alert
                        alert_text = alert.text
                        self.logger.info(f"Alert 발견: {alert_text}")
                        alert.accept()
                        self.logger.info("Alert 수락 완료")
                        return True
                    except Exception:
                        self.logger.info("Alert 없음")
                        
                except Exception as e:
                    self.logger.warning(f"좌표 ({x}, {y}) 클릭 실패: {e}")
            
            return False
            
        except Exception as e:
            self.logger.error(f"모달창 클릭 디버깅 실패: {e}")
            return False
    
    def test_full_workflow_with_debug(self):
        """전체 워크플로우 디버깅 테스트"""
        try:
            self.logger.info("=== 전체 워크플로우 디버깅 테스트 시작 ===")
            
            # 1. 브라우저 설정
            if not self.setup_browser():
                return False
                
            # 2. 테스트 설정 로드
            if not self.load_test_config():
                return False
            
            # 3. 로그인 단계별 디버깅
            if not self.debug_login_step_by_step():
                self.logger.error("로그인 실패로 테스트 중단")
                return False
            
            # 4. MarketManagerCafe24 초기화
            self.market_manager = MarketManagerCafe24(self.driver)
            
            # 5. 마켓상품가져오기 페이지로 이동
            input("마켓상품가져오기 페이지로 이동하려면 Enter를 누르세요...")
            if not self.market_manager._navigate_to_import_page():
                self.logger.error("마켓상품가져오기 페이지 이동 실패")
                return False
            
            # 6. 전체 가져오기 탭 선택
            input("전체 가져오기 탭을 선택하려면 Enter를 누르세요...")
            if not self.market_manager._select_full_import_tab():
                self.logger.error("전체 가져오기 탭 선택 실패")
                return False
            
            # 7. 11번가 스토어 선택
            input(f"11번가 스토어 ({self.test_config['store_11st_id']})를 선택하려면 Enter를 누르세요...")
            if not self.market_manager._select_11st_store(self.test_config['store_11st_id']):
                self.logger.error("11번가 스토어 선택 실패")
                return False
            
            # 8. 가져오기 실행
            input("가져오기를 실행하려면 Enter를 누르세요...")
            if not self.market_manager._execute_import():
                self.logger.error("가져오기 실행 실패")
                return False
            
            # 9. 모달창 확인 디버깅
            input("모달창 확인 디버깅을 시작하려면 Enter를 누르세요...")
            if not self.debug_modal_click():
                self.logger.error("모달창 확인 실패")
                return False
            
            self.logger.info("=== 전체 워크플로우 디버깅 테스트 완료 ===")
            return True
            
        except Exception as e:
            self.logger.error(f"전체 워크플로우 디버깅 테스트 실패: {e}")
            return False
            
        finally:
            if self.driver:
                input("브라우저를 종료하려면 Enter를 누르세요...")
                self.driver.quit()
    
    def test_cafe24_import(self):
        """카페24 11번가 상품 가져오기 전체 테스트 (기존 방식)"""
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

def main():
    """메인 함수"""
    print("카페24 11번가 상품 가져오기 디버깅 테스트")
    print("1. 전체 테스트 (자동 실행)")
    print("2. 단계별 디버깅 테스트 (수동 진행)")
    print("3. 로그인만 디버깅")
    
    choice = input("선택하세요 (1, 2, 또는 3): ")
    
    tester = Cafe24DebugTester()
    
    if choice == "1":
        tester.test_cafe24_import()
    elif choice == "2":
        tester.test_full_workflow_with_debug()
    elif choice == "3":
        if tester.setup_browser() and tester.load_test_config():
            tester.debug_login_step_by_step()
            input("브라우저를 종료하려면 Enter를 누르세요...")
            tester.driver.quit()
    else:
        print("잘못된 선택입니다.")

if __name__ == "__main__":
    main()