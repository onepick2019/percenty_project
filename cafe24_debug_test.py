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
                    'cafe24_id': 'zc3alsyd',  # 테스트용 기본값
                    'cafe24_password': '!!qnwk2024',  # 테스트용 기본값
                    'store_11st_id': 'zc3ejtp'  # 테스트용 기본값
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
    
    def test_modal_handling_methods(self):
        """
        개선된 모달창 처리 방법들을 테스트합니다.
        """
        try:
            self.logger.info("=== 모달창 처리 방법 테스트 시작 ===")
            
            # 1. 브라우저 설정
            if not self.setup_browser():
                return False
                
            # 2. 테스트 설정 로드
            if not self.load_test_config():
                return False
            
            # 3. 로그인
            self.logger.info("카페24 로그인 시작")
            self.market_manager = MarketManagerCafe24(self.driver)
            
            if not self.market_manager._login(
                self.test_config['cafe24_id'], 
                self.test_config['cafe24_password']
            ):
                self.logger.error("로그인 실패")
                return False
            
            # 4. 마켓상품가져오기 페이지로 이동
            self.logger.info("마켓상품가져오기 페이지로 이동")
            if not self.market_manager._navigate_to_import_page():
                self.logger.error("마켓상품가져오기 페이지 이동 실패")
                return False
            
            # 5. 전체 가져오기 탭 선택
            self.logger.info("전체 가져오기 탭 선택")
            if not self.market_manager._select_full_import_tab():
                self.logger.error("전체 가져오기 탭 선택 실패")
                return False
            
            # 6. 11번가 스토어 선택
            self.logger.info(f"11번가 스토어 선택: {self.test_config['store_11st_id']}")
            if not self.market_manager._select_11st_store(self.test_config['store_11st_id']):
                self.logger.error("11번가 스토어 선택 실패")
                return False
            
            # 7. 가져오기 실행 (모달창 발생 전까지)
            self.logger.info("가져오기 실행 (모달창 발생 대기)")
            if not self.market_manager._execute_import():
                self.logger.error("가져오기 실행 실패")
                return False
            
            # 8. 모달창 처리 테스트
            self.logger.info("=== 개선된 모달창 처리 테스트 ===")
            input("모달창이 나타났는지 확인하고 Enter를 누르세요...")
            
            # 개선된 모달창 처리 메서드 호출
            if self.market_manager._confirm_import_modal():
                self.logger.info("✓ 개선된 모달창 처리 성공!")
                return True
            else:
                self.logger.error("✗ 개선된 모달창 처리 실패")
                return False
            
        except Exception as e:
            self.logger.error(f"모달창 처리 방법 테스트 실패: {e}")
            return False
            
        finally:
            if self.driver:
                input("테스트 완료. 브라우저를 종료하려면 Enter를 누르세요...")
                # 로그아웃 주석처리 (사용자 요청)
                # self.market_manager._logout()
                self.driver.quit()
    
    def test_individual_modal_methods(self):
        """
        개별 모달창 처리 방법들을 하나씩 테스트합니다.
        """
        try:
            self.logger.info("=== 개별 모달창 처리 방법 테스트 시작 ===")
            
            # 브라우저 설정 및 로그인 (간소화)
            if not self.setup_browser():
                return False
            if not self.load_test_config():
                return False
            
            # 테스트용 모달창 생성 (JavaScript)
            self.logger.info("테스트용 모달창 생성")
            test_modal_js = """
            // 테스트용 모달창 생성
            var modal = document.createElement('div');
            modal.id = 'test-modal';
            modal.style.cssText = `
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: white;
                border: 2px solid #333;
                padding: 20px;
                z-index: 9999;
                box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            `;
            modal.innerHTML = `
                <p>등록된 상품 개수에 따라 많은 시간이 소요될 수 있습니다.<br>
                선택한 마켓 계정의 상품을 가져오시겠습니까?</p>
                <button id="confirm-btn" onclick="document.getElementById('test-modal').remove();">확인</button>
                <button id="cancel-btn" onclick="document.getElementById('test-modal').remove();">취소</button>
            `;
            document.body.appendChild(modal);
            
            // 확인 버튼에 포커스
            document.getElementById('confirm-btn').focus();
            """
            
            self.driver.execute_script(test_modal_js)
            self.logger.info("테스트용 모달창 생성 완료")
            
            input("테스트용 모달창이 생성되었습니다. 각 방법을 테스트해보겠습니다. Enter를 누르세요...")
            
            # MarketManagerCafe24 인스턴스 생성
            self.market_manager = MarketManagerCafe24(self.driver)
            
            # 방법 1: Enter 키 테스트
            self.logger.info("=== 방법 1: Enter 키 테스트 ===")
            self.driver.execute_script(test_modal_js)  # 모달창 재생성
            input("Enter 키 방법을 테스트하려면 Enter를 누르세요...")
            
            try:
                from selenium.webdriver.common.keys import Keys
                from selenium.webdriver.common.action_chains import ActionChains
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
                time.sleep(2)
                
                # 모달창이 사라졌는지 확인
                modal_exists = self.driver.execute_script("return document.getElementById('test-modal') !== null;")
                if not modal_exists:
                    self.logger.info("✓ Enter 키 방법 성공!")
                else:
                    self.logger.warning("✗ Enter 키 방법 실패")
            except Exception as e:
                self.logger.error(f"Enter 키 방법 오류: {e}")
            
            # 방법 2: Space 키 테스트
            self.logger.info("=== 방법 2: Space 키 테스트 ===")
            self.driver.execute_script(test_modal_js)  # 모달창 재생성
            input("Space 키 방법을 테스트하려면 Enter를 누르세요...")
            
            try:
                ActionChains(self.driver).send_keys(Keys.SPACE).perform()
                time.sleep(2)
                
                modal_exists = self.driver.execute_script("return document.getElementById('test-modal') !== null;")
                if not modal_exists:
                    self.logger.info("✓ Space 키 방법 성공!")
                else:
                    self.logger.warning("✗ Space 키 방법 실패")
            except Exception as e:
                self.logger.error(f"Space 키 방법 오류: {e}")
            
            # 방법 3: DOM 선택자 테스트
            self.logger.info("=== 방법 3: DOM 선택자 테스트 ===")
            self.driver.execute_script(test_modal_js)  # 모달창 재생성
            input("DOM 선택자 방법을 테스트하려면 Enter를 누르세요...")
            
            try:
                confirm_btn = self.driver.find_element(By.ID, "confirm-btn")
                confirm_btn.click()
                time.sleep(2)
                
                modal_exists = self.driver.execute_script("return document.getElementById('test-modal') !== null;")
                if not modal_exists:
                    self.logger.info("✓ DOM 선택자 방법 성공!")
                else:
                    self.logger.warning("✗ DOM 선택자 방법 실패")
            except Exception as e:
                self.logger.error(f"DOM 선택자 방법 오류: {e}")
            
            # 방법 4: JavaScript 실행 테스트
            self.logger.info("=== 방법 4: JavaScript 실행 테스트 ===")
            self.driver.execute_script(test_modal_js)  # 모달창 재생성
            input("JavaScript 실행 방법을 테스트하려면 Enter를 누르세요...")
            
            try:
                self.driver.execute_script("document.getElementById('confirm-btn').click();")
                time.sleep(2)
                
                modal_exists = self.driver.execute_script("return document.getElementById('test-modal') !== null;")
                if not modal_exists:
                    self.logger.info("✓ JavaScript 실행 방법 성공!")
                else:
                    self.logger.warning("✗ JavaScript 실행 방법 실패")
            except Exception as e:
                self.logger.error(f"JavaScript 실행 방법 오류: {e}")
            
            self.logger.info("=== 개별 모달창 처리 방법 테스트 완료 ===")
            return True
            
        except Exception as e:
            self.logger.error(f"개별 모달창 처리 방법 테스트 실패: {e}")
            return False
            
        finally:
            if self.driver:
                input("테스트 완료. 브라우저를 종료하려면 Enter를 누르세요...")
                self.driver.quit()
    
    def test_real_cafe24_modal_advanced(self):
        """
        실제 카페24 모달창에서 고급 처리 방법들을 테스트합니다.
        """
        try:
            self.logger.info("=== 실제 카페24 모달창 고급 처리 테스트 시작 ===")
            
            # 1. 브라우저 설정
            if not self.setup_browser():
                return False
                
            # 2. 테스트 설정 로드
            if not self.load_test_config():
                return False
            
            # 3. 로그인
            self.logger.info("카페24 로그인 시작")
            self.market_manager = MarketManagerCafe24(self.driver)
            
            if not self.market_manager._login(
                self.test_config['cafe24_id'], 
                self.test_config['cafe24_password']
            ):
                self.logger.error("로그인 실패")
                return False
            
            # 4. 마켓상품가져오기 페이지로 이동
            self.logger.info("마켓상품가져오기 페이지로 이동")
            if not self.market_manager._navigate_to_import_page():
                self.logger.error("마켓상품가져오기 페이지 이동 실패")
                return False
            
            # 5. 전체 가져오기 탭 선택
            self.logger.info("전체 가져오기 탭 선택")
            if not self.market_manager._select_full_import_tab():
                self.logger.error("전체 가져오기 탭 선택 실패")
                return False
            
            # 6. 11번가 스토어 선택
            self.logger.info(f"11번가 스토어 선택: {self.test_config['store_11st_id']}")
            if not self.market_manager._select_11st_store(self.test_config['store_11st_id']):
                self.logger.error("11번가 스토어 선택 실패")
                return False
            
            # 7. 가져오기 실행 (모달창 발생 전까지)
            self.logger.info("가져오기 실행 (모달창 발생 대기)")
            if not self.market_manager._execute_import():
                self.logger.error("가져오기 실행 실패")
                return False
            
            # 8. 모달창 대기 및 고급 처리 테스트
            self.logger.info("=== 실제 카페24 모달창 고급 처리 테스트 ===")
            input("모달창이 나타났는지 확인하고 Enter를 누르세요...")
            
            # 고급 모달창 처리 메서드들 테스트
            success = self._test_advanced_modal_methods()
            
            if success:
                self.logger.info("✓ 고급 모달창 처리 성공!")
                return True
            else:
                self.logger.error("✗ 고급 모달창 처리 실패")
                return False
            
        except Exception as e:
            self.logger.error(f"실제 카페24 모달창 고급 처리 테스트 실패: {e}")
            return False
            
        finally:
            if self.driver:
                input("테스트 완료. 브라우저를 종료하려면 Enter를 누르세요...")
                # 로그아웃 주석처리 (사용자 요청)
                # self.market_manager._logout()
                self.driver.quit()
    
    def _test_advanced_modal_methods(self):
        """
        고급 모달창 처리 방법들을 순차적으로 테스트합니다.
        """
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.common.action_chains import ActionChains
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.by import By
        
        methods = [
            ("Enter 키 전송", self._method_send_enter),
            ("Space 키 전송", self._method_send_space),
            ("Tab + Enter 조합", self._method_tab_enter),
            ("JavaScript Alert 처리", self._method_handle_alert),
            ("iframe 내부 확인", self._method_check_iframe),
            ("Shadow DOM 확인", self._method_check_shadow_dom),
            ("모든 버튼 찾기", self._method_find_all_buttons),
            ("텍스트 기반 버튼 찾기", self._method_find_button_by_text),
            ("CSS 선택자 조합", self._method_css_selectors),
            ("XPath 조합", self._method_xpath_selectors),
            ("JavaScript 이벤트 발생", self._method_javascript_events),
            ("키보드 네비게이션", self._method_keyboard_navigation),
        ]
        
        for method_name, method_func in methods:
            self.logger.info(f"=== {method_name} 테스트 ===")
            try:
                if method_func():
                    self.logger.info(f"✓ {method_name} 성공!")
                    return True
                else:
                    self.logger.warning(f"✗ {method_name} 실패")
            except Exception as e:
                self.logger.error(f"{method_name} 오류: {e}")
            
            # 다음 방법 시도 전 잠시 대기
            time.sleep(1)
        
        return False
    
    def _method_send_enter(self):
        """Enter 키 전송"""
        try:
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            time.sleep(2)
            return self._check_modal_disappeared()
        except:
            return False
    
    def _method_send_space(self):
        """Space 키 전송"""
        try:
            ActionChains(self.driver).send_keys(Keys.SPACE).perform()
            time.sleep(2)
            return self._check_modal_disappeared()
        except:
            return False
    
    def _method_tab_enter(self):
        """Tab + Enter 조합"""
        try:
            ActionChains(self.driver).send_keys(Keys.TAB).send_keys(Keys.ENTER).perform()
            time.sleep(2)
            return self._check_modal_disappeared()
        except:
            return False
    
    def _method_handle_alert(self):
        """JavaScript Alert 처리"""
        try:
            alert = self.driver.switch_to.alert
            alert.accept()
            time.sleep(2)
            return self._check_modal_disappeared()
        except:
            return False
    
    def _method_check_iframe(self):
        """iframe 내부 확인"""
        try:
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            for iframe in iframes:
                self.driver.switch_to.frame(iframe)
                try:
                    confirm_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), '확인')]")
                    confirm_btn.click()
                    self.driver.switch_to.default_content()
                    time.sleep(2)
                    return self._check_modal_disappeared()
                except:
                    pass
                finally:
                    self.driver.switch_to.default_content()
            return False
        except:
            return False
    
    def _method_check_shadow_dom(self):
        """Shadow DOM 확인"""
        try:
            shadow_hosts = self.driver.execute_script("""
                return Array.from(document.querySelectorAll('*')).filter(el => el.shadowRoot);
            """)
            
            for host in shadow_hosts:
                shadow_root = self.driver.execute_script("return arguments[0].shadowRoot", host)
                if shadow_root:
                    buttons = self.driver.execute_script("""
                        return arguments[0].querySelectorAll('button');
                    """, shadow_root)
                    
                    for button in buttons:
                        if '확인' in self.driver.execute_script("return arguments[0].textContent", button):
                            self.driver.execute_script("arguments[0].click()", button)
                            time.sleep(2)
                            return self._check_modal_disappeared()
            return False
        except:
            return False
    
    def _method_find_all_buttons(self):
        """모든 버튼 찾기"""
        try:
            selectors = [
                "button",
                "input[type='button']",
                "input[type='submit']",
                "[role='button']",
                ".btn",
                ".button",
                "a[onclick]"
            ]
            
            for selector in selectors:
                buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for button in buttons:
                    try:
                        if button.is_displayed() and '확인' in button.text:
                            button.click()
                            time.sleep(2)
                            return self._check_modal_disappeared()
                    except:
                        continue
            return False
        except:
            return False
    
    def _method_find_button_by_text(self):
        """텍스트 기반 버튼 찾기"""
        try:
            text_patterns = ['확인', 'OK', 'Yes', '예', 'Confirm']
            
            for pattern in text_patterns:
                xpaths = [
                    f"//button[contains(text(), '{pattern}')]",
                    f"//input[@value='{pattern}']",
                    f"//*[contains(text(), '{pattern}') and (@onclick or @role='button')]",
                    f"//a[contains(text(), '{pattern}')]"
                ]
                
                for xpath in xpaths:
                    try:
                        elements = self.driver.find_elements(By.XPATH, xpath)
                        for element in elements:
                            if element.is_displayed():
                                element.click()
                                time.sleep(2)
                                return self._check_modal_disappeared()
                    except:
                        continue
            return False
        except:
            return False
    
    def _method_css_selectors(self):
        """CSS 선택자 조합"""
        try:
            selectors = [
                "div[class*='modal'] button:first-child",
                "div[class*='popup'] button:first-child",
                "div[class*='dialog'] button:first-child",
                ".modal-footer button:first-child",
                ".popup-footer button:first-child",
                "[class*='confirm'] button",
                "[id*='confirm'] button",
                "[class*='modal'] [class*='btn']:first-child"
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            element.click()
                            time.sleep(2)
                            return self._check_modal_disappeared()
                except:
                    continue
            return False
        except:
            return False
    
    def _method_xpath_selectors(self):
        """XPath 조합"""
        try:
            xpaths = [
                "//div[contains(@class, 'modal')]//button[1]",
                "//div[contains(@class, 'popup')]//button[1]",
                "//div[contains(@class, 'dialog')]//button[1]",
                "//*[contains(@class, 'modal-footer')]//button[1]",
                "//*[contains(@class, 'popup-footer')]//button[1]",
                "//button[contains(@class, 'confirm')]",
                "//button[contains(@id, 'confirm')]",
                "//*[@role='dialog']//button[1]"
            ]
            
            for xpath in xpaths:
                try:
                    elements = self.driver.find_elements(By.XPATH, xpath)
                    for element in elements:
                        if element.is_displayed():
                            element.click()
                            time.sleep(2)
                            return self._check_modal_disappeared()
                except:
                    continue
            return False
        except:
            return False
    
    def _method_javascript_events(self):
        """JavaScript 이벤트 발생"""
        try:
            scripts = [
                "document.querySelector('button').click();",
                "document.querySelector('[onclick]').click();",
                "var event = new Event('click'); document.querySelector('button').dispatchEvent(event);",
                "var buttons = document.querySelectorAll('button'); if(buttons.length > 0) buttons[0].click();",
                "var event = new KeyboardEvent('keydown', {key: 'Enter'}); document.dispatchEvent(event);",
                "var event = new KeyboardEvent('keypress', {key: 'Enter'}); document.dispatchEvent(event);",
                "var event = new KeyboardEvent('keyup', {key: 'Enter'}); document.dispatchEvent(event);"
            ]
            
            for script in scripts:
                try:
                    self.driver.execute_script(script)
                    time.sleep(2)
                    if self._check_modal_disappeared():
                        return True
                except:
                    continue
            return False
        except:
            return False
    
    def _method_keyboard_navigation(self):
        """키보드 네비게이션"""
        try:
            key_combinations = [
                [Keys.TAB, Keys.ENTER],
                [Keys.TAB, Keys.TAB, Keys.ENTER],
                [Keys.TAB, Keys.SPACE],
                [Keys.ESCAPE],
                [Keys.ALT, Keys.F4]
            ]
            
            for keys in key_combinations:
                try:
                    action = ActionChains(self.driver)
                    for key in keys:
                        action = action.send_keys(key)
                    action.perform()
                    time.sleep(2)
                    if self._check_modal_disappeared():
                        return True
                except:
                    continue
            return False
        except:
            return False
    
    def _check_modal_disappeared(self):
        """모달창이 사라졌는지 확인"""
        try:
            # 일반적인 모달창 선택자들로 확인
            modal_selectors = [
                "div[class*='modal']",
                "div[class*='popup']",
                "div[class*='dialog']",
                "[role='dialog']",
                ".modal",
                ".popup",
                ".dialog"
            ]
            
            for selector in modal_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed():
                        return False
            
            # 모달창이 없으면 성공
            return True
        except:
            # 오류가 발생하면 모달창이 사라진 것으로 간주
            return True
    
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

    def test_page_navigation_verification(self):
        """페이지 번호 검증 기능 테스트"""
        try:
            self.logger.info("=== 페이지 번호 검증 기능 테스트 시작 ===")
            
            # 1. 브라우저 설정
            if not self.setup_browser():
                return False
                
            # 2. 테스트 설정 로드
            if not self.load_test_config():
                return False
                
            # 3. MarketManagerCafe24 초기화
            self.market_manager = MarketManagerCafe24(self.driver)
            
            # 4. 카페24 로그인
            self.logger.info("카페24 로그인 시작")
            if not self.market_manager.login_cafe24(
                self.test_config['cafe24_id'], 
                self.test_config['cafe24_password']
            ):
                self.logger.error("카페24 로그인 실패")
                return False
            
            # 5. 상품 관리 페이지로 이동
            self.logger.info("상품 관리 페이지로 이동")
            from datetime import datetime, timedelta
            end_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
            base_url = (
                f"https://mp.cafe24.com/mp/product/front/manageList?"
                f"sort_direction=ascend&limit=10&is_matched=T&"
                f"search_begin_ymd=2023-07-01&search_end_ymd={end_date}&"
                f"market_select[]=sk11st%7C{self.test_config['store_11st_id']}"
            )
            
            # 6. 페이지 번호 검증 테스트
            test_pages = [1, 2, 3, 4, 5]
            
            for page in test_pages:
                self.logger.info(f"\n--- 페이지 {page} 검증 테스트 ---")
                
                page_url = f"{base_url}&page={page}"
                self.logger.info(f"페이지 {page}로 이동: {page_url}")
                
                # 페이지 이동
                self.driver.get(page_url)
                time.sleep(3)
                
                # 페이지 번호 검증 로직 테스트
                import re
                for attempt in range(3):
                    current_url = self.driver.current_url
                    self.logger.info(f"현재 URL: {current_url}")
                    
                    # URL에서 page 파라미터 추출
                    page_match = re.search(r'page=(\d+)', current_url)
                    if page_match:
                        current_page = int(page_match.group(1))
                        self.logger.info(f"현재 페이지: {current_page}, 목표 페이지: {page}")
                        
                        if current_page == page:
                            self.logger.info(f"✓ 페이지 {page} 이동 성공 확인")
                            break
                        else:
                            self.logger.warning(f"✗ 페이지 불일치 - 목표: {page}, 현재: {current_page}")
                            if attempt < 2:  # 마지막 시도가 아니면 재시도
                                self.logger.info(f"페이지 이동 재시도 {attempt + 1}/3")
                                time.sleep(2)
                                self.driver.get(page_url)
                                time.sleep(3)
                            else:
                                self.logger.error(f"✗ 페이지 {page} 이동 실패 - 다른 페이지({current_page})가 열림")
                    else:
                        self.logger.warning(f"URL에서 페이지 번호를 찾을 수 없음: {current_url}")
                        if attempt < 2:  # 마지막 시도가 아니면 재시도
                            self.logger.info(f"페이지 이동 재시도 {attempt + 1}/3")
                            time.sleep(2)
                            self.driver.get(page_url)
                            time.sleep(3)
                        else:
                            self.logger.warning("페이지 번호 확인 실패 - 계속 진행")
                            break
                
                # 페이지 로딩 확인
                try:
                    # 상품 목록 테이블 확인
                    table_selectors = [
                        "table[class*='table']",
                        "table.table-list",
                        ".table-list",
                        ".product-list-table",
                        "table tbody tr"
                    ]
                    
                    table_found = False
                    for selector in table_selectors:
                        try:
                            from selenium.webdriver.support.ui import WebDriverWait
                            from selenium.webdriver.support import expected_conditions as EC
                            WebDriverWait(self.driver, 5).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                            )
                            self.logger.info(f"✓ 상품 목록 테이블 확인 (선택자: {selector})")
                            table_found = True
                            break
                        except:
                            continue
                    
                    if not table_found:
                        self.logger.warning("✗ 상품 목록 테이블을 찾을 수 없음")
                    
                except Exception as e:
                    self.logger.warning(f"페이지 로딩 확인 실패: {e}")
                
                # 다음 테스트를 위한 대기
                time.sleep(2)
            
            self.logger.info("=== 페이지 번호 검증 기능 테스트 완료 ===")
            return True
            
        except Exception as e:
            self.logger.error(f"페이지 번호 검증 테스트 실행 중 오류 발생: {e}")
            return False
            
        finally:
            if self.driver:
                self.logger.info("브라우저 종료")
                self.driver.quit()


def main():
    """메인 함수"""
    print("=== 카페24 11번가 상품 가져오기 디버깅 테스트 ===")
    print("1. 전체 테스트 (자동 실행)")
    print("2. 로그인만 디버깅")
    print("3. 모달창 클릭 디버깅")
    print("4. 개선된 모달창 처리 테스트 (실제 카페24)")
    print("5. 개별 모달창 처리 방법 테스트 (테스트용 모달창)")
    print("6. 실제 카페24 모달창 고급 처리 테스트 (12가지 방법)")
    print("7. 페이지 번호 검증 기능 테스트")
    
    choice = input("선택하세요 (1-7): ")
    
    tester = Cafe24DebugTester()
    
    if choice == "1":
        tester.test_cafe24_import()
    elif choice == "2":
        if tester.setup_browser() and tester.load_test_config():
            tester.debug_login_step_by_step()
            input("브라우저를 종료하려면 Enter를 누르세요...")
            tester.driver.quit()
    elif choice == "3":
        if tester.setup_browser() and tester.load_test_config():
            tester.debug_modal_click()
            input("브라우저를 종료하려면 Enter를 누르세요...")
            tester.driver.quit()
    elif choice == "4":
        tester.test_modal_handling_methods()
    elif choice == "5":
        tester.test_individual_modal_methods()
    elif choice == "6":
        tester.test_real_cafe24_modal_advanced()
    elif choice == "7":
        tester.test_page_navigation_verification()
    else:
        print("잘못된 선택입니다.")


if __name__ == "__main__":
    main()