# -*- coding: utf-8 -*-
"""
퍼센티 상품 수정 자동화 스크립트 2단계 (신규 버전) - 서버3 전용
등록상품관리 화면을 열어 상품 목록을 확인하기
"""

import time
import logging
# import pyautogui  # 절대좌표 클릭 방식 중단 (command prompt 창 최소화 문제)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# 좌표 변환 공통 모듈 임포트
from coordinates.coordinate_conversion import convert_coordinates

# DOM 유틸리티 임포트
from dom_utils import highlight_element
# 클릭 유틸리티 임포트
from click_utils import smart_click
# 통합 유틸리티 모듈 임포트
from percenty_utils import hide_channel_talk_and_modals, periodic_ui_cleanup, ensure_clean_ui_before_action
# 새 탭에서의 로그인 모달창 숨기기 필요할 경우에만 사용
from login_modal_utils import apply_login_modal_hiding_for_new_tab

# 최적화된 드롭다운 유틸리티 임포트
from dropdown_utils_common import get_common_dropdown_utils
from dropdown_utils2 import get_product_search_dropdown_manager  # 호환성 유지

# UI 요소 임포트
from ui_elements import UI_ELEMENTS

# 상품 편집 코어 2단계 기능 임포트 (서버3 전용 수정)
from product_editor_core2 import ProductEditorCore2
# from product_editor_core3 import ProductEditorCore3

# 좌표 정보 임포트
from coordinates.coordinates_all import MENU

# 좌표 설정 파일 불러오기
from coordinates.coordinates_editgoods import (
    PRODUCT_MODAL_TAB,
    PRODUCT_MODAL_EDIT1,
    PRODUCT_MODAL_EDIT2,
    PRODUCT_PRICE_TAB,
    PRODUCT_MODAL_CLOSE,
    PRODUCT_DETAIL_EDIT,
    PRODUCT_MEMO_MODAL,
    DELAY_VERY_SHORT2,
    DELAY_VERY_SHORT5,
    DELAY_VERY_SHORT,
    DELAY_SHORT,
    DELAY_MEDIUM,
    DELAY_LONG,
    DELAY_VERY_LONG
)

# 로깅 설정
logger = logging.getLogger(__name__)

class PercentyNewStep2Server3:
    def __init__(self, driver, browser_ui_height=95):
        """
        퍼센티 상품 수정 자동화 스크립트 2단계 초기화 - 서버3 전용
        
        Args:
            driver: 셀레니움 웹드라이버 인스턴스
            browser_ui_height: 브라우저 UI 높이 (기본값: 95px)
        """
        self.driver = driver
        self.browser_ui_height = browser_ui_height
        self.server_name = "서버3"  # 서버3 전용 설정
        logger.info(f"===== 퍼센티 상품 수정 자동화 스크립트 2단계 초기화 - {self.server_name} 전용 =====")
        
        # 브라우저 내부 크기 확인
        self.inner_width = self.driver.execute_script("return window.innerWidth")
        self.inner_height = self.driver.execute_script("return window.innerHeight")
        logger.info(f"브라우저 내부 크기: {self.inner_width}x{self.inner_height}")
        
        # 2단계 전용 드롭다운 관리자 초기화
        self.dropdown_manager = get_product_search_dropdown_manager(driver)
        
        # 최적화된 공통 드롭다운 유틸리티 초기화
        self.common_dropdown = get_common_dropdown_utils(driver)
        
        # 성능 모니터링 초기화
        self.performance_metrics = {
            'group_selection_time': [],
            'items_per_page_time': [],
            'total_operations': 0,
            'successful_operations': 0
        }

    def convert_coordinates(self, x, y):
        """
        절대좌표를 상대좌표로 변환
        
        Args:
            x: X 좌표 (절대값)
            y: Y 좌표 (절대값)
        
        Returns:
            tuple: 변환된 (x, y) 좌표
        """
        # 공통 좌표 변환 모듈을 호출하여 상대좌표 계산
        return convert_coordinates(x, y, self.inner_width, self.inner_height)

    def click_at_coordinates(self, coords, delay_type=DELAY_SHORT, use_js=True):
        """
        주어진 좌표를 클릭
        
        Args:
            coords: (x, y) 좌표 튜플
            delay_type: 클릭 후 대기 시간
            use_js: JavaScript로 클릭할지 여부
        """
        x, y = coords
        rel_x, rel_y = self.convert_coordinates(x, y)
        
        try:
            if use_js:
                # JavaScript를 이용한 클릭
                script = f"""
                var element = document.elementFromPoint({rel_x}, {rel_y});
                if (element) {{
                    var rect = element.getBoundingClientRect();
                    var clickEvent = new MouseEvent('click', {{
                        bubbles: true,
                        cancelable: true,
                        view: window,
                        clientX: {rel_x},
                        clientY: {rel_y}
                    }});
                    element.dispatchEvent(clickEvent);
                    return element.tagName + ' ' + element.textContent + ' ' + (element.id ? 'ID: ' + element.id : '') + ' CLASS: ' + element.className;
                }}
                return 'No element found at position';
                """
                result = self.driver.execute_script(script)
                logger.info(f"JavaScript로 클릭 성공: ({rel_x}, {rel_y})")
                logger.info(f"클릭된 요소: {result}")
            else:
                # JavaScript를 이용한 대체 클릭 방식 (pyautogui 대신)
                logger.info(f"JavaScript 대체 클릭 방식 사용: ({rel_x}, {rel_y})")
                script = f"""
                try {{                
                    var element = document.elementFromPoint({rel_x}, {rel_y});
                    if (element) {{                    
                        // 클릭 이벤트 생성 및 발생
                        var clickEvent = new MouseEvent('click', {{                    
                            view: window,
                            bubbles: true,
                            cancelable: true,
                            clientX: {rel_x},
                            clientY: {rel_y}
                        }});
                        element.dispatchEvent(clickEvent);
                        
                        // 상세 정보 반환
                        return {{ 
                            success: true, 
                            tagName: element.tagName,
                            className: element.className,
                            id: element.id || 'no-id',
                            text: element.textContent ? element.textContent.substring(0, 50) : ''
                        }};
                    }}
                    return {{ success: false, reason: 'no-element' }};
                }} catch(e) {{                
                    return {{ success: false, reason: 'error', message: e.toString() }};
                }}
                """
                result = self.driver.execute_script(script)
                logger.info(f"JavaScript 대체 클릭 결과: {result}")
                
                # 실패 시 fallback으로 더 간단한 click 실행
                if not result.get('success', False):
                    fallback_script = f"document.elementFromPoint({rel_x}, {rel_y}).click();"
                    try:
                        self.driver.execute_script(fallback_script)
                        logger.info("Fallback 클릭 성공")
                    except Exception as inner_e:
                        logger.warning(f"Fallback 클릭도 실패: {inner_e}")
                else:
                    logger.info(f"클릭된 요소: {result.get('tagName')} {result.get('text')} ID: {result.get('id')} CLASS: {result.get('className')}")
                                                
                logger.info(f"JavaScript 대체 클릭 완료: ({rel_x}, {rel_y})")
            
            # 클릭 후 대기
            time.sleep(delay_type)
            return True
            
        except Exception as e:
            logger.error(f"좌표 클릭 중 오류 발생: {e}")
            return False

    def run_step2_automation(self):
        """
        서버3 전용 2단계 자동화 실행: 등록상품관리 화면을 열어 상품 목록 확인
        """
        try:
            logger.info(f"===== {self.server_name} 전용 2단계 자동화 시작 =====")
            
            # 1. 등록상품관리 메뉴 클릭 - 하이브리드 방식 적용
            logger.info("등록상품관리 메뉴 클릭 시도 (하이브리드 방식)")
            
            # 1.1 DOM 선택자 먼저 시도
            dom_success = False
            try:
                # UI_ELEMENTS에서 정보 가져오기
                element_info = UI_ELEMENTS["PRODUCT_MANAGE"]
                dom_selector = element_info["dom_selector"]
                selector_type = element_info["selector_type"]
                
                # DOM 요소 강조 표시 (선택적)
                try:
                    highlight_element(self.driver, f"{selector_type}={dom_selector}")
                except:
                    pass
                
                logger.info(f"등록상품관리 메뉴 DOM 선택자 기반 클릭 시도: {selector_type}={dom_selector}")
                
                # Selenium By 타입으로 변환
                by_type = By.XPATH if selector_type.lower() == "xpath" else By.CSS_SELECTOR
                
                # 요소 찾기 시도
                element = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((by_type, dom_selector))
                )
                
                # 요소가 발견되면 클릭
                element.click()
                logger.info("등록상품관리 메뉴 DOM 선택자 기반 클릭 성공")
                dom_success = True
                
            except Exception as dom_error:
                logger.warning(f"DOM 선택자를 사용한 클릭 실패: {dom_error}")
                dom_success = False
            
            # 1.2 DOM 선택자로 실패한 경우 좌표 기반 클릭 시도
            if not dom_success:
                try:
                    logger.info("DOM 선택자로 클릭 실패, 좌표 기반 클릭으로 전환합니다.")
                    # UI_ELEMENTS에서 좌표 가져오기
                    product_manage_coords = UI_ELEMENTS["PRODUCT_MANAGE"]["coordinates"]
                    logger.info(f"좌표 기반 클릭 시도: {product_manage_coords}")
                    
                    # 좌표 클릭 실행
                    self.click_at_coordinates(product_manage_coords, delay_type=DELAY_SHORT)
                    logger.info("좌표 기반 클릭 성공")
                except Exception as coord_error:
                    logger.error(f"좌표 기반 클릭 실패: {coord_error}")
                    return False
            
            # 등록상품관리 화면 로드 대기 (5초)
            logger.info("등록상품관리 화면 로드 대기 - 5초")
            time.sleep(5)
            
            # 2. 상품검색용 드롭박스에서 '신규수집' 그룹 선택 (최적화된 방식)
            logger.info("2. 상품검색용 드롭박스에서 '신규수집' 그룹 선택 (최적화)")
            
            # 성능 추적 시작
            group_start_time = time.time()
            group_selection_success = False
            
            try:
                # 최적화된 그룹 선택 시도 (5초 타임아웃)
                group_selection_success = self.common_dropdown.select_group_with_verification(
                    "신규수집", timeout=5
                )
                
                if group_selection_success:
                    logger.info("최적화된 신규수집 그룹 선택 성공")
                else:
                    logger.warning("최적화된 그룹 선택 실패, 기존 방식으로 재시도")
                    
                    # 기존 방식으로 폴백
                    dropdown_manager = get_product_search_dropdown_manager(self.driver)
                    for attempt in range(3):
                        try:
                            logger.info(f"기존 방식 신규수집 그룹 선택 시도 {attempt + 1}/3")
                            
                            if dropdown_manager.select_group_in_search_dropdown("신규수집"):
                                if dropdown_manager.verify_page_refresh():
                                    logger.info("기존 방식 신규수집 그룹 선택 성공")
                                    group_selection_success = True
                                    break
                            
                            if attempt < 2:
                                time.sleep(DELAY_MEDIUM)
                                
                        except Exception as e:
                            logger.error(f"기존 방식 그룹 선택 중 오류 (시도 {attempt + 1}/3): {e}")
                            time.sleep(DELAY_MEDIUM)
                            
            except Exception as e:
                logger.error(f"그룹 선택 중 오류: {e}")
            
            # 성능 추적 종료
            group_end_time = time.time()
            group_duration = group_end_time - group_start_time
            self.performance_metrics['group_selection_time'].append(group_duration)
            logger.info(f"그룹 선택 소요 시간: {group_duration:.2f}초")
            
            if not group_selection_success:
                logger.error("신규수집 그룹 선택에 실패했습니다.")
                return False
            
            # 그룹 선택 후 페이지 로드 대기
            time.sleep(DELAY_MEDIUM)
            
            # 3. 50개씩 보기 설정 (최적화된 방식)
            logger.info("3. 50개씩 보기 설정 (최적화)")
            
            # 성능 추적 시작
            items_start_time = time.time()
            items_per_page_success = False
            
            try:
                # 최적화된 50개씩 보기 설정 시도 (3초 타임아웃)
                items_per_page_success = self.common_dropdown.select_items_per_page_with_verification(
                    "50", timeout=3
                )
                
                if items_per_page_success:
                    logger.info("최적화된 50개씩 보기 설정 성공")
                else:
                    logger.warning("최적화된 50개씩 보기 설정 실패, 기존 방식으로 재시도")
                    
                    # 기존 방식으로 폴백
                    dropdown_manager = get_product_search_dropdown_manager(self.driver)
                    for attempt in range(3):
                        try:
                            logger.info(f"기존 방식 50개씩 보기 설정 시도 {attempt + 1}/3")
                            
                            if dropdown_manager.select_items_per_page("50"):
                                logger.info("기존 방식 50개씩 보기 설정 성공")
                                items_per_page_success = True
                                break
                            else:
                                logger.warning(f"기존 방식 50개씩 보기 설정 실패 (시도 {attempt + 1}/3)")
                                time.sleep(DELAY_MEDIUM)
                                
                        except Exception as e:
                            logger.error(f"기존 방식 50개씩 보기 설정 중 오류 (시도 {attempt + 1}/3): {e}")
                            time.sleep(DELAY_MEDIUM)
                            
            except Exception as e:
                logger.error(f"50개씩 보기 설정 중 오류: {e}")
            
            # 성능 추적 종료
            items_end_time = time.time()
            items_duration = items_end_time - items_start_time
            self.performance_metrics['items_per_page_time'].append(items_duration)
            logger.info(f"50개씩 보기 설정 소요 시간: {items_duration:.2f}초")
            
            if not items_per_page_success:
                logger.error("50개씩 보기 설정에 실패했습니다.")
                return False
            
            # 설정 완료 후 페이지 로드 대기
            time.sleep(DELAY_MEDIUM)
            
            # 4. 화면을 최상단으로 이동
            logger.info("4. 화면을 최상단으로 이동")
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(DELAY_SHORT)
            
            # 5. ProductEditorCore2를 사용하여 Step 2 작업 처리
            logger.info("5. ProductEditorCore2를 사용하여 Step 2 작업 처리")
            try:
                # ProductEditorCore2 인스턴스 생성
                editor_core2 = ProductEditorCore2(self.driver)
                
                # 현재 로그인된 계정 ID 가져오기
                if hasattr(self, 'logged_in_account_id') and self.logged_in_account_id:
                    current_account_id = self.logged_in_account_id
                    logger.info(f"로그인된 계정 사용: {current_account_id}")
                else:
                    logger.error("로그인된 계정 ID를 찾을 수 없습니다.")
                    return False
                
                logger.info(f"계정 ID: {current_account_id}, 서버: {self.server_name}")
                
                # 서버3 전용 작업 목록 로드 (F열=step2, D열=서버3)
                tasks = editor_core2.load_task_list_from_excel_with_server_filter(
                    account_id=current_account_id, 
                    step="step2", 
                    server_name=self.server_name
                )
                
                if not tasks:
                    logger.warning(f"{self.server_name}에 대한 step2 작업이 없습니다.")
                    return True
                
                logger.info(f"{self.server_name}에 대한 {len(tasks)}개의 작업을 처리합니다.")
                
                # 각 작업 처리
                for i, task in enumerate(tasks, 1):
                    logger.info(f"[{i}/{len(tasks)}] 작업 처리 중: {task}")
                    
                    # 키워드 검색 및 그룹 이동 처리
                    success = editor_core2.process_keyword_search_and_move(
                        keyword=task['provider_code'],
                        target_group=task['target_group']
                    )
                    
                    if success:
                        logger.info(f"작업 {i} 성공: {task['provider_code']} -> {task['target_group']}")
                    else:
                        logger.error(f"작업 {i} 실패: {task['provider_code']} -> {task['target_group']}")
                    
                    # 작업 간 대기
                    time.sleep(DELAY_SHORT)
                
                logger.info("등록상품관리 화면이 성공적으로 열렸습니다.")
                
                # 성능 요약 로깅
                self.log_performance_summary()
                
                logger.info(f"===== {self.server_name} 전용 2단계 자동화 완료 =====")
                return True
                
            except Exception as e:
                logger.error(f"ProductEditorCore2 작업 처리 중 오류: {e}")
                # 오류 발생 시에도 성능 요약 로깅
                self.log_performance_summary()
                return False
        
        except Exception as e:
            logger.error(f"{self.server_name} 2단계 자동화 중 오류 발생: {e}")
            # 오류 발생 시에도 성능 요약 로깅
            self.log_performance_summary()
            return False
    
    def _track_performance(self, operation_name, duration, success=True):
        """
        성능 추적 헬퍼 메서드
        
        Args:
            operation_name: 작업 이름
            duration: 소요 시간 (초)
            success: 성공 여부
        """
        self.performance_metrics['total_operations'] += 1
        if success:
            self.performance_metrics['successful_operations'] += 1
        
        logger.info(f"[성능] {operation_name}: {duration:.2f}초 ({'성공' if success else '실패'})")
    
    def get_performance_summary(self):
        """
        성능 요약 정보 반환
        
        Returns:
            dict: 성능 요약 정보
        """
        metrics = self.performance_metrics
        
        summary = {
            'total_operations': metrics['total_operations'],
            'successful_operations': metrics['successful_operations'],
            'success_rate': (metrics['successful_operations'] / max(metrics['total_operations'], 1)) * 100
        }
        
        if metrics['group_selection_time']:
            summary['avg_group_selection_time'] = sum(metrics['group_selection_time']) / len(metrics['group_selection_time'])
            summary['total_group_selections'] = len(metrics['group_selection_time'])
        
        if metrics['items_per_page_time']:
            summary['avg_items_per_page_time'] = sum(metrics['items_per_page_time']) / len(metrics['items_per_page_time'])
            summary['total_items_per_page_operations'] = len(metrics['items_per_page_time'])
        
        return summary
    
    def log_performance_summary(self):
        """
        성능 요약 로깅
        """
        summary = self.get_performance_summary()
        
        logger.info("===== 성능 요약 =====")
        logger.info(f"총 작업 수: {summary['total_operations']}")
        logger.info(f"성공한 작업 수: {summary['successful_operations']}")
        logger.info(f"성공률: {summary['success_rate']:.1f}%")
        
        if 'avg_group_selection_time' in summary:
            logger.info(f"평균 그룹 선택 시간: {summary['avg_group_selection_time']:.2f}초 ({summary['total_group_selections']}회)")
        
        if 'avg_items_per_page_time' in summary:
            logger.info(f"평균 페이지당 항목 설정 시간: {summary['avg_items_per_page_time']:.2f}초 ({summary['total_items_per_page_operations']}회)")
        
        logger.info("===================")

    # def run_step3_automation(self):
    #     """
    #     Step 3 자동화 실행 (개별 상품 수정 후 target_group 이동)
    #     
    #     Returns:
    #         bool: 성공 여부
    #     """
    #     try:
    #         logger.info("서버3 Step 3 자동화 시작")
    #         
    #         # ProductEditorCore3 인스턴스 생성
    #         core3 = ProductEditorCore3(self.driver)
    #         
    #         # 계정 ID 가져오기 (현재 로그인된 계정)
    #         account_id = getattr(self, 'logged_in_account_id', None)
    #         if not account_id:
    #             logger.error("계정 ID를 찾을 수 없습니다.")
    #             return False
    #         
    #         # Step 3 작업 목록 로드
    #         task_list = core3.load_task_list_from_excel_with_server_filter(
    #             account_id=account_id,
    #             step="step3",
    #             server_name=self.server_name
    #         )
    #         
    #         if not task_list:
    #             logger.info("Step 3 처리할 작업이 없습니다.")
    #             return True
    #         
    #         logger.info(f"Step 3 총 {len(task_list)}개 작업 처리 시작")
    #         
    #         # 각 작업 처리
    #         for i, task in enumerate(task_list, 1):
    #             logger.info(f"Step 3 작업 {i}/{len(task_list)} 처리 중: {task['provider_code']} -> {task['target_group']}")
    #             
    #             try:
    #                 # 개별 상품 수정 및 이동 처리
    #                 success = core3.process_keyword_with_individual_modifications(
    #                     keyword=task['provider_code'],
    #                     target_group=task['target_group'],
    #                     task_data=task
    #                 )
    #                 
    #                 if success:
    #                     logger.info(f"Step 3 작업 {i} 완료: {task['provider_code']}")
    #                 else:
    #                     logger.warning(f"Step 3 작업 {i} 실패: {task['provider_code']}")
    #                     
    #             except Exception as task_error:
    #                 logger.error(f"Step 3 작업 {i} 처리 중 오류: {task_error}")
    #                 continue
    #             
    #             # 작업 간 대기
    #             time.sleep(2)
    #         
    #         logger.info("서버3 Step 3 자동화 완료")
    #         return True
    #         
    #     except Exception as e:
    #         logger.error(f"Step 3 자동화 실행 중 오류: {e}")
    #         return False


if __name__ == "__main__":
    import sys
    import pandas as pd
    
    try:
        # 로그인 모듈 임포트 (순환 임포트 방지를 위해 여기서 임포트)
        from login_percenty import PercentyLogin
        
        # 1. 계정 목록 로드
        try:
            df = pd.read_excel("percenty_id.xlsx", sheet_name="login_id")
            accounts = df.to_dict('records')
        except Exception as e:
            print(f"Excel 파일 로드 실패: {e}")
            sys.exit(1)
        
        # 2. 계정 선택 UI
        print("\n사용 가능한 계정 목록:")
        for i, account in enumerate(accounts, 1):
            nickname = account.get('nickname', account['id'])
            print(f"{i}. {nickname} ({account['id']})")
        
        while True:
            try:
                choice = int(input("\n사용할 계정 번호를 선택하세요: ")) - 1
                if 0 <= choice < len(accounts):
                    selected_account = accounts[choice]
                    break
                else:
                    print("올바른 번호를 입력하세요.")
            except ValueError:
                print("숫자를 입력하세요.")
        
        # 3. 선택한 계정 정보 출력
        print(f"\n선택된 계정: {selected_account.get('nickname', selected_account['id'])}")
        print(f"계정 ID: {selected_account['id']}")
        print(f"서버: 서버3 (전용)")
        
        # 4. 선택한 계정으로 로그인 객체 생성
        login = PercentyLogin(account=selected_account)
        
        # 5. 로그인 시도
        print(f"\n선택한 계정으로 로그인을 시도합니다: {selected_account.get('nickname', selected_account['id'])}")
        
        # 로그인 실행
        if not login.setup_driver():
            print("웹드라이버 설정 실패")
            sys.exit(1)
        
        if not login.login():
            print("로그인 실패")
            sys.exit(1)
        
        # AI 소싱 메뉴 클릭
        if not login.click_product_aisourcing_button_improved():
            print("AI 소싱 메뉴 클릭 실패")
            sys.exit(1)
            
        # 채널톡 및 로그인 모달창 숨기기 적용 (통합 유틸리티 사용)
        print("\n채널톡 및 로그인 모달창 숨기기 적용 시작...")
        result = hide_channel_talk_and_modals(login.driver, log_prefix="메인 실행")
        print(f"채널톡 및 로그인 모달창 숨기기 결과: {result}")
        
        print("\n\n" + "=" * 50)
        print(f"로그인 성공! '{selected_account.get('nickname', '')}' - 서버3 전용")
        print("이제 서버3 전용 2단계 자동화를 실행합니다...")
        print("=" * 50 + "\n")
        
        # 6. 서버3 전용 2단계 자동화 실행
        automation = PercentyNewStep2Server3(login.driver)
        # 로그인된 계정 정보를 자동화 객체에 저장
        automation.logged_in_account_id = selected_account['id']
        automation.current_account_id = selected_account['id']
        success = automation.run_step2_automation()
        if success:
            print("\n\n" + "=" * 50)
            print("서버3 전용 2단계 자동화 성공!")
            print("=" * 50 + "\n")
        else:
            print("\n\n" + "=" * 50)
            print("서버3 전용 2단계 자동화 실패. 로그를 확인하세요.")
            print("=" * 50 + "\n")
        
        # 7. 서버3 전용 3단계 자동화 실행
        step3_success = automation.run_step3_automation()
        if step3_success:
            print("\n\n" + "=" * 50)
            print("서버3 전용 3단계 자동화 성공!")
            print("=" * 50 + "\n")
        else:
            print("\n\n" + "=" * 50)
            print("서버3 전용 3단계 자동화 실패. 로그를 확인하세요.")
            print("=" * 50 + "\n")
        
        # 무한 대기 (사용자가 Ctrl+C를 누를 때까지)
        print("종료하려면 Ctrl+C를 누르세요.")
        try:
            # 무한 대기
            while True:
                time.sleep(10)  # 10초마다 한 번씩 체크
        except KeyboardInterrupt:
            print("\n\n" + "=" * 50)
            print("사용자가 스크립트를 종료했습니다.")
            print("=" * 50 + "\n")
    
    except ImportError as e:
        print(f"\n임포트 오류 발생: {e}")
        print("로그인 모듈을 임포트할 수 없습니다.")
        print("순환 임포트 문제가 발생했을 수 있습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n오류 발생: {e}")
    finally:
        # 종료 시 브라우저 닫기
        if 'login' in locals() and login.driver:
            login.close_driver()