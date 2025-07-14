# -*- coding: utf-8 -*-
"""
상품 수정의 핵심 로직 3단계용 (product_editor_core3.py)
개별 상품 수정 후 target_group으로 이동하는 기능을 담당하는 클래스
"""

import time
import logging
import pandas as pd
import os
import random

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# UI 요소 임포트
from ui_elements import UI_ELEMENTS

# 이미지 번역 매니저 임포트
from image_translation_manager import ImageTranslationManager

# 시간 지연 상수 임포트
from coordinates.coordinates_editgoods import (
    DELAY_VERY_SHORT2,
    DELAY_VERY_SHORT5,
    DELAY_VERY_SHORT,
    DELAY_SHORT,
    DELAY_MEDIUM,
    DELAY_LONG,
    DELAY_VERY_LONG
)

# 유틸리티 모듈 임포트
from dropdown_utils2 import get_product_search_dropdown_manager
from dropdown_utils import PercentyDropdown  # 안정된 dropdown_utils 사용
from click_utils import smart_click, hybrid_click
from keyboard_shortcuts import KeyboardShortcuts
from image_utils3 import PercentyImageManager3  # 안정된 image_utils 사용
from core.common.batch_limit_manager import BatchLimitManager

# 로깅 설정
logger = logging.getLogger(__name__)

class ProductEditorCore3:
    """
    상품 수정의 핵심 로직 3단계를 담당하는 클래스
    
    이 클래스는 다음 작업을 수행합니다:
    - step3 데이터만 처리
    - 개별 상품 수정 모달창 열기
    - H열~L열 수정 작업 수행
    - 수정 완료 후 target_group으로 이동
    - 모든 상품 처리 완료까지 반복
    """
    
    # 각 열별로 열어야 할 탭 매핑
    COLUMN_TAB_MAPPING = {
        'H': 'PRODUCT_TAB_DETAIL',      # H열: 이미지 삭제 -> 상세페이지 탭
        'I': 'PRODUCT_TAB_THUMBNAIL',   # I열: 썸네일 삭제 -> 썸네일 탭
        'J': 'PRODUCT_TAB_OPTION',      # J열: 옵션 이미지 복사 -> 옵션션 탭
        'K': 'PRODUCT_TAB_DETAIL',      # K열: 이미지 번역 -> 상세페이지 탭
        'L': 'PRODUCT_TAB_DETAIL',      # L열: 이미지 태그 삽입 -> 상세페이지 탭
        'M': 'PRODUCT_TAB_DETAIL',      # M열: HTML 업데이트 -> 상세페이지 탭
        'N': 'PRODUCT_TAB_THUMBNAIL',   # N열: 썸네일 번역 -> 썸네일 탭
        'O': 'PRODUCT_TAB_OPTION'       # O열: 옵션 이미지 번역 -> 옵션 탭
    }
    
    def __init__(self, driver, config=None, step3_product_limit=20, step3_image_limit=2000):
        """
        상품 편집 코어 3단계 초기화
        
        Args:
            driver: Selenium WebDriver 인스턴스 (None 허용)
            config: 설정 정보 딕셔너리 (선택사항)
            step3_product_limit: 3단계 상품 수량 제한 (기본값: 20)
            step3_image_limit: 3단계 이미지 번역 수량 제한 (기본값: 2000)
        """
        self.driver = driver
        self.config = config or {}
        self.step3_product_limit = step3_product_limit
        self.step3_image_limit = step3_image_limit
        
        # 이미지 번역 수 추적 변수
        self.total_translated_images = 0
        self.current_product_translated_images = 0
        
        # driver가 None이 아닐 때만 드라이버 의존 객체들 초기화
        if self.driver is not None:
            # 멀티브라우저 간섭 방지를 위해 use_selenium=True 강제 설정
            self.keyboard = KeyboardShortcuts(self.driver, use_selenium=True)
            self.image_manager = PercentyImageManager3(self.driver)
            self.image_translation_handler = ImageTranslationManager(self.driver)
        else:
            self.keyboard = None
            self.image_manager = None
            self.image_translation_handler = None
        
        logger.info(f"ProductEditorCore3 초기화 완료 (driver: {'있음' if driver else '없음'}, 상품제한: {step3_product_limit}, 이미지번역제한: {step3_image_limit})")
    
    def select_product_name_input(self):
        """
        등록상품관리 화면에서 상품명 입력창을 선택합니다.
        
        Returns:
            bool: 성공 여부
        """
        logger.info("상품명 입력창 선택 시작")
        
        try:
            # 드라이버 연결 상태 검증
            try:
                self.driver.current_url
                logger.debug("상품명 입력창 선택 전 드라이버 연결 상태 정상")
            except Exception as conn_e:
                logger.error(f"상품명 입력창 선택 전 드라이버 연결 오류: {conn_e}")
                raise Exception(f"드라이버 연결 실패로 상품명 입력창 선택 불가: {conn_e}")
            # UI_ELEMENTS에서 상품명 입력창 정보 가져오기
            product_name_input_element = UI_ELEMENTS["PRODUCT_NAME_SEARCH_INPUT"]
            dom_selector = product_name_input_element["dom_selector"]
            selector_type = product_name_input_element["selector_type"]
            
            logger.info(f"상품명 입력창 DOM 선택자: {dom_selector}")
            
            # DOM 선택자로 요소 찾기 시도
            by_type = By.XPATH if selector_type.lower() == "xpath" else By.CSS_SELECTOR
            element = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((by_type, dom_selector))
            )
            
            # 요소 클릭
            element.click()
            logger.info("상품명 입력창 DOM 선택자 기반 클릭 성공")
            
            # 클릭 후 잠시 대기
            time.sleep(DELAY_SHORT)
            
            return True
            
        except Exception as e:
            logger.warning(f"상품명 입력창 DOM 선택자 클릭 실패: {e}")
            
            # DOM 선택자 실패 시 좌표 기반 클릭 시도
            try:
                logger.info("DOM 선택자 실패, 좌표 기반 클릭으로 전환")
                coords = UI_ELEMENTS["PRODUCT_NAME_SEARCH_INPUT"]["coordinates"]
                logger.info(f"좌표 기반 클릭 시도: {coords}")
                
                # 좌표 클릭 실행
                self._click_at_coordinates(coords, delay_type=DELAY_SHORT)
                logger.info("상품명 입력창 좌표 기반 클릭 성공")
                
                return True
                
            except Exception as coord_error:
                logger.error(f"상품명 입력창 좌표 기반 클릭도 실패: {coord_error}")
                return False
    
    def _click_at_coordinates(self, coords, delay_type=DELAY_SHORT):
        """
        주어진 좌표를 클릭
        
        Args:
            coords: (x, y) 좌표 튜플
            delay_type: 클릭 후 대기 시간
        """
        x, y = coords
        
        # 브라우저 내부 크기 확인
        inner_width = self.driver.execute_script("return window.innerWidth")
        inner_height = self.driver.execute_script("return window.innerHeight")
        
        # 좌표 변환 (절대좌표를 상대좌표로)
        from coordinates.coordinate_conversion import convert_coordinates
        relative_x, relative_y = convert_coordinates(x, y, inner_width, inner_height)
        
        # JavaScript로 클릭 실행
        click_script = f"""
        var element = document.elementFromPoint({relative_x}, {relative_y});
        if (element) {{
            element.click();
            return true;
        }}
        return false;
        """
        
        result = self.driver.execute_script(click_script)
        
        if result:
            logger.info(f"좌표 ({x}, {y}) -> 상대좌표 ({relative_x}, {relative_y}) 클릭 성공")
        else:
            logger.warning(f"좌표 ({x}, {y}) -> 상대좌표 ({relative_x}, {relative_y}) 클릭 실패")
        
        # 클릭 후 대기
        time.sleep(delay_type)
        
        return result
    
    def load_task_list_from_excel_with_server_filter(self, account_id, step="step3", server_name=None, excel_path="percenty_id.xlsx", completed_keywords=None):
        """
        엑셀 파일에서 계정별 step3 작업 목록 로드 (서버 필터링 포함)
        
        Args:
            account_id: 계정 ID (예: onepick2019@gmail.com)
            step: 작업 단계 (step3 고정)
            server_name: 서버명 (서버1, 서버2, 서버3)
            excel_path: 엑셀 파일 경로
            completed_keywords: 이미 완료된 키워드 목록 (제외할 키워드들)
            
        Returns:
            list: 작업 목록 (provider_code, target_group, H~L열 데이터 포함)
        """
        try:
            logger.info(f"계정 {account_id}의 {step} 작업 목록을 로드합니다. (서버: {server_name})")
            
            # login_id 시트에서 계정과 연결된 시트명 찾기
            login_df = pd.read_excel(excel_path, sheet_name="login_id")
            account_row = login_df[login_df['id'] == account_id]
            
            if account_row.empty:
                logger.error(f"계정 {account_id}를 찾을 수 없습니다.")
                return []
            
            # 계정과 연결된 시트명 가져오기
            if 'sheet_nickname' in account_row.columns:
                sheet_name = account_row.iloc[0]['sheet_nickname']
            else:
                logger.error("계정과 연결된 시트명을 찾을 수 없습니다. (sheet_nickname 컬럼 필요)")
                return []
                
            logger.info(f"계정 {account_id}와 연결된 시트: {sheet_name}")
            
            # 연결된 시트에서 작업 목록 로드 (행 순서 보장)
            task_df = pd.read_excel(excel_path, sheet_name=sheet_name)
            # 원본 행 순서를 보장하기 위해 인덱스 리셋
            task_df = task_df.reset_index(drop=True)
            
            # 디버깅: 실제 컬럼명 확인
            logger.info(f"Excel 파일의 컬럼명: {list(task_df.columns)}")
            
            # step3에 해당하는 작업만 필터링
            step_column = None
            if 'step' in task_df.columns:
                step_column = 'step'
            elif 'Step' in task_df.columns:
                step_column = 'Step'
            elif 'STEP' in task_df.columns:
                step_column = 'STEP'
            elif 'step2_or_step3' in task_df.columns:
                step_column = 'step2_or_step3'
            elif any('step' in col.lower() for col in task_df.columns):
                step_columns = [col for col in task_df.columns if 'step' in col.lower()]
                step_column = step_columns[0]
                logger.info(f"step 관련 컬럼 발견: {step_columns}, 사용할 컬럼: {step_column}")
            
            if step_column:
                logger.info(f"'{step_column}' 컬럼을 사용하여 {step} 작업 필터링")
                step_tasks = task_df[task_df[step_column] == step].reset_index(drop=True)
                logger.info(f"필터링 전 총 행 수: {len(task_df)}, step3 필터링 후 행 수: {len(step_tasks)}")
            else:
                logger.warning(f"step 컬럼을 찾을 수 없어 모든 작업을 반환합니다.")
                step_tasks = task_df.reset_index(drop=True)
            
            # 서버명으로 추가 필터링
            if server_name:
                server_column = None
                if 'final_group' in step_tasks.columns:
                    server_column = 'final_group'
                elif 'server' in step_tasks.columns:
                    server_column = 'server'
                elif 'server_name' in step_tasks.columns:
                    server_column = 'server_name'
                elif any('server' in col.lower() for col in step_tasks.columns):
                    server_columns = [col for col in step_tasks.columns if 'server' in col.lower()]
                    server_column = server_columns[0]
                    logger.info(f"server 관련 컬럼 발견: {server_columns}, 사용할 컬럼: {server_column}")
                
                if server_column:
                    logger.info(f"'{server_column}' 컬럼을 사용하여 {server_name} 서버 필터링")
                    step_tasks = step_tasks[step_tasks[server_column] == server_name].reset_index(drop=True)
                    logger.info(f"서버 필터링 후 행 수: {len(step_tasks)}")
                else:
                    logger.warning(f"서버 관련 컬럼을 찾을 수 없어 서버 필터링을 건너뜁니다.")
            
            task_list = []
            for _, row in step_tasks.iterrows():
                # provider_code와 target_group 컬럼 찾기
                provider_code = None
                target_group = None
                
                # 가능한 컬럼명들 확인
                if 'provider_code' in row:
                    provider_code = row['provider_code']
                elif 'keyword' in row:
                    provider_code = row['keyword']
                elif 'search_keyword' in row:
                    provider_code = row['search_keyword']
                    
                if 'target_group' in row:
                    target_group = row['target_group']
                elif 'group' in row:
                    target_group = row['group']
                elif 'group_name' in row:
                    target_group = row['group_name']
                
                # H~O열 데이터 추출 (엑셀의 H, I, J, K, L, M, N, O 컬럼)
                h_data = row.iloc[7] if len(row) > 7 else None  # H열 (8번째 컬럼, 0-based index 7)
                i_data = row.iloc[8] if len(row) > 8 else None  # I열
                j_data = row.iloc[9] if len(row) > 9 else None  # J열
                k_data = row.iloc[10] if len(row) > 10 else None  # K열
                l_data = row.iloc[11] if len(row) > 11 else None  # L열
                m_data = row.iloc[12] if len(row) > 12 else None  # M열 (13번째 컬럼, 0-based index 12)
                n_data = row.iloc[13] if len(row) > 13 else None  # N열 (14번째 컬럼, 0-based index 13)
                o_data = row.iloc[14] if len(row) > 14 else None  # O열 (15번째 컬럼, 0-based index 14)
                
                if provider_code and target_group:
                    task = {
                        'provider_code': str(provider_code),
                        'target_group': str(target_group),
                        'h_data': str(h_data) if pd.notna(h_data) else None,
                        'i_data': str(i_data) if pd.notna(i_data) else None,
                        'j_data': str(j_data) if pd.notna(j_data) else None,
                        'k_data': str(k_data) if pd.notna(k_data) else None,
                        'l_data': str(l_data) if pd.notna(l_data) else None,
                        'm_data': str(m_data) if pd.notna(m_data) else None,
                        'n_data': str(n_data) if pd.notna(n_data) else None,
                        'o_data': str(o_data) if pd.notna(o_data) else None
                    }
                    task_list.append(task)
            
            # 이미 완료된 키워드 제외
            if completed_keywords:
                original_count = len(task_list)
                task_list = [task for task in task_list if task['provider_code'] not in completed_keywords]
                excluded_count = original_count - len(task_list)
                if excluded_count > 0:
                    logger.info(f"이미 완료된 키워드 {excluded_count}개 제외됨: {completed_keywords}")
            
            # 키워드 순서를 랜덤하게 섞기
            if task_list:
                random.shuffle(task_list)
                logger.info(f"키워드 순서를 랜덤하게 섞었습니다.")
                
            logger.info(f"{len(task_list)}개의 {step} 작업을 로드했습니다.")
            return task_list
            
        except Exception as e:
            logger.error(f"작업 목록 로드 중 오류: {e}")
            return []
    
    def search_products_by_keyword(self, keyword, max_products=20):
        """
        키워드로 상품 검색 (상품 수 제한 기능 포함)
        
        Args:
            keyword: 검색할 키워드 (provider_code)
            max_products: 최대 상품 수 제한 (기본값: 20, None이면 제한 없음)
            
        Returns:
            int: 검색된 상품 수
        """
        try:
            # max_products가 None인 경우 기본값 설정
            if max_products is None:
                max_products = self.step3_product_limit or 20
            
            logger.info(f"키워드 '{keyword}'로 상품 검색 시작 (최대 {max_products}개 제한)")
            
            # 드라이버 연결 상태 검증
            try:
                self.driver.current_url
                logger.info("드라이버 연결 상태 정상 확인")
            except Exception as e:
                logger.error(f"드라이버 연결 오류 감지: {e}")
                raise Exception(f"드라이버 연결 실패: {e}")
            
            # 상품명 검색 입력창 클릭
            search_input_element = UI_ELEMENTS["PRODUCT_NAME_SEARCH_INPUT"]
            dom_selector = search_input_element["dom_selector"]
            selector_type = search_input_element["selector_type"]
            
            by_type = By.XPATH if selector_type.lower() == "xpath" else By.CSS_SELECTOR
            search_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((by_type, dom_selector))
            )
            
            # 검색창 클릭 및 기존 내용 삭제
            search_input.click()
            time.sleep(DELAY_VERY_SHORT)
            
            # 기존 내용 전체 선택 후 삭제
            self.keyboard.select_all(delay=DELAY_VERY_SHORT2)
            search_input.send_keys(Keys.DELETE)
            time.sleep(DELAY_VERY_SHORT)
            
            # 새 키워드 입력
            search_input.send_keys(keyword)
            time.sleep(DELAY_SHORT)
            
            # 검색 버튼 클릭 또는 Enter 키 입력
            search_input.send_keys(Keys.ENTER)
            time.sleep(DELAY_MEDIUM)
            
            # 검색 결과 로딩 대기 - 동적 대기로 최적화
            max_wait = 5
            wait_interval = 0.2
            for _ in range(int(max_wait / wait_interval)):
                try:
                    result_count = self._get_search_result_count()
                    if result_count > 0:
                        break
                except:
                    pass
                time.sleep(wait_interval)
            time.sleep(DELAY_VERY_SHORT)  # 안정화를 위한 최소 대기
            
            # 검색된 상품 수 확인
            product_count = self._get_search_result_count()
            logger.info(f"키워드 '{keyword}' 검색 결과: {product_count}개 상품")
            
            # 상품 수 제한 처리 (max_products가 설정되고 검색 결과가 초과하는 경우에만)
            if max_products and product_count > max_products:
                logger.info(f"검색 결과가 {max_products}개를 초과합니다. 상품 수를 제한합니다.")
                limited_count = self._limit_search_results(max_products)
                logger.info(f"상품 수 제한 완료: {limited_count}개로 제한됨")
                return min(limited_count, max_products)  # 최대값으로 제한
            
            logger.info(f"검색된 상품 수({product_count})가 제한값({max_products}) 이하이므로 그대로 반환합니다.")
            return product_count
            
        except Exception as e:
            logger.error(f"상품 검색 중 오류: {e}")
            return 0
    
    def _get_search_result_count(self):
        """
        검색 결과 상품 수를 확인
        
        Returns:
            int: 검색된 상품 수
        """
        try:
            # 상품 목록에서 실제 상품 행 수 계산
            product_rows = self.driver.find_elements(By.XPATH, "//tbody//tr[contains(@class, 'ant-table-row')]")
            return len(product_rows)
            
        except Exception as e:
            logger.warning(f"상품 수 확인 중 오류: {e}")
            return 0
    
    def _limit_search_results(self, max_products):
        """
        검색 결과를 지정된 개수로 제한
        
        Args:
            max_products: 최대 상품 수
            
        Returns:
            int: 제한된 상품 수
        """
        try:
            logger.info(f"상품 수를 {max_products}개로 제한 시작")
            
            # 현재 상품 행들 가져오기
            product_rows = self.driver.find_elements(By.XPATH, "//tbody//tr[contains(@class, 'ant-table-row')]")
            current_count = len(product_rows)
            
            if current_count <= max_products:
                logger.info(f"현재 상품 수({current_count})가 제한 수({max_products}) 이하입니다.")
                return current_count
            
            # 초과하는 상품들을 숨기거나 제거
            excess_count = current_count - max_products
            logger.info(f"초과 상품 {excess_count}개를 제한합니다.")
            
            # 페이지 크기 조정을 통한 제한 (가능한 경우)
            try:
                # 페이지 크기 드롭다운 찾기
                page_size_selectors = [
                    ".ant-pagination-options-size-changer",
                    ".ant-select-selection-item",
                    "[title*='페이지당']",
                    ".pagination-size-changer"
                ]
                
                page_size_dropdown = None
                for selector in page_size_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            if element.is_displayed() and ('페이지' in element.text or 'page' in element.text.lower()):
                                page_size_dropdown = element
                                break
                        if page_size_dropdown:
                            break
                    except:
                        continue
                
                if page_size_dropdown:
                    # 페이지 크기를 20으로 설정
                    self.driver.execute_script("arguments[0].click();", page_size_dropdown)
                    time.sleep(DELAY_SHORT)
                    
                    # 20개 옵션 선택
                    size_options = self.driver.find_elements(By.CSS_SELECTOR, ".ant-select-item-option")
                    for option in size_options:
                        if "20" in option.text:
                            self.driver.execute_script("arguments[0].click();", option)
                            time.sleep(DELAY_MEDIUM)
                            break
                    
                    # 변경 후 상품 수 재확인
                    time.sleep(DELAY_MEDIUM)
                    new_product_rows = self.driver.find_elements(By.XPATH, "//tbody//tr[contains(@class, 'ant-table-row')]")
                    limited_count = len(new_product_rows)
                    
                    logger.info(f"페이지 크기 조정으로 상품 수 제한 완료: {limited_count}개")
                    return min(limited_count, max_products)
                
            except Exception as e:
                logger.warning(f"페이지 크기 조정 실패: {e}")
            
            # 페이지 크기 조정이 불가능한 경우, 제한된 상품 수 반환
            logger.info(f"페이지 크기 조정이 불가능하므로 제한된 상품 수({max_products})를 반환합니다.")
            return max_products  # 실제 제한값 반환
            
        except Exception as e:
             logger.error(f"상품 수 제한 중 오류: {e}")
             return max_products
    
    def open_first_product_modal(self):
        """
        첫 번째 상품의 수정 모달창 열기 (등록상품관리용 UI 요소 사용)
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("첫 번째 상품 수정 모달창 열기 시작")
            
            # 등록상품관리용 UI 요소를 사용하여 첫 번째 상품 클릭
            if smart_click(self.driver, UI_ELEMENTS["REGISTER_FIRST_PRODUCT_ITEM"]):
                logger.info("첫 번째 상품 클릭 성공")
                
                # 고정 대기 제거하고 바로 모달창 감지
                modal_opened = self._check_modal_open(max_wait=5)
                if modal_opened:
                    logger.info("첫 번째 상품 수정 모달창 열기 성공")
                    return True
                else:
                    logger.error("첫 번째 상품 수정 모달창 열기 실패")
                    return False
            else:
                logger.error("첫 번째 상품 클릭 실패")
                return False
                
        except Exception as e:
            logger.error(f"첫 번째 상품 모달창 열기 중 오류: {e}")
            return False
    
    def _check_modal_open(self, max_wait=10, check_interval=0.5):
        """
        모달창이 열렸는지 확인
        
        Args:
            max_wait: 최대 대기 시간(초)
            check_interval: 확인 간격(초)
            
        Returns:
            bool: 모달창 열림 여부
        """
        logger.info("모달창 열림 확인 시작")
        
        modal_selectors = [
            "//div[@role='dialog']",
            "//div[contains(@class, 'ant-modal')]",
            "//div[contains(@class, 'ant-drawer-content')]",
            "//div[contains(@class, 'modal-content')]"
        ]
        
        start_time = time.time()
        while time.time() - start_time < max_wait:
            for selector in modal_selectors:
                try:
                    modal_elements = self.driver.find_elements(By.XPATH, selector)
                    if modal_elements:
                        # 모달이 실제로 보이는지 확인
                        for modal in modal_elements:
                            if modal.is_displayed():
                                logger.info(f"모달창 열림 확인됨: {selector}")
                                return True
                except Exception as e:
                    logger.debug(f"모달 확인 중 오류: {e}")
                    continue
            
            time.sleep(check_interval)
        
        logger.warning(f"{max_wait}초 동안 모달창을 찾을 수 없습니다.")
        return False
    
    def process_product_modifications(self, task_data):
        """
        상품 수정 작업 수행 (H~N열 데이터 기반)
        
        Args:
            task_data: 작업 데이터 딕셔너리 (h_data, i_data, j_data, k_data, l_data, m_data, n_data 포함)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("상품 수정 작업 시작")
            
            # M열 데이터를 인스턴스 변수로 저장 (L열에서 참조용)
            self.current_m_data = task_data.get('m_data')
            
            # H열 데이터 처리 (이미지 삭제)
            if task_data.get('h_data'):
                logger.info("H열 데이터 처리 시작 (이미지 삭제)")
                if not self._process_h_data(task_data['h_data']):
                    logger.warning("H열 데이터 처리 실패")
            
            # I열 데이터 처리 (썸네일 삭제)
            if task_data.get('i_data'):
                logger.info("I열 데이터 처리 시작 (썸네일 삭제)")
                if not self._process_i_data(task_data['i_data']):
                    logger.warning("I열 데이터 처리 실패")
            
            # J열 데이터 처리 (옵션 이미지 복사)
            if task_data.get('j_data'):
                logger.info("J열 데이터 처리 시작 (옵션 이미지 복사)")
                if not self._process_j_data(task_data['j_data']):
                    logger.warning("J열 데이터 처리 실패")
            
            # K열 데이터 처리 (이미지 번역)
            if task_data.get('k_data'):
                logger.info("K열 데이터 처리 시작 (이미지 번역)")
                if not self._process_k_data(task_data['k_data']):
                    logger.warning("K열 데이터 처리 실패")
            
            # L열 데이터 처리 (이미지 태그 삽입)
            if task_data.get('l_data'):
                logger.info("L열 데이터 처리 시작 (이미지 태그 삽입)")
                if not self._process_l_data(task_data['l_data']):
                    logger.warning("L열 데이터 처리 실패")
            
            # M열 데이터 처리 (HTML 업데이트)
            if task_data.get('m_data'):
                logger.info("M열 데이터 처리 시작 (HTML 업데이트)")
                if not self._process_m_data(task_data['m_data']):
                    logger.warning("M열 데이터 처리 실패")
            
            # N열 데이터 처리 (썸네일 번역)
            if task_data.get('n_data'):
                logger.info("N열 데이터 처리 시작 (썸네일 번역)")
                if not self._process_n_data(task_data['n_data']):
                    logger.warning("N열 데이터 처리 실패")
            
            # O열 데이터 처리 (옵션 이미지 번역)
            if task_data.get('o_data'):
                logger.info("O열 데이터 처리 시작 (옵션 이미지 번역)")
                if not self._process_o_data(task_data['o_data']):
                    logger.warning("O열 데이터 처리 실패")
            
            # K, N, O열 처리 완료 후 모달창 닫기
            logger.info("K, N, O열 처리 완료 - 수정화면 모달창 닫기 시작")
            
            # 여러 번 ESC 키 시도
            for esc_attempt in range(3):
                ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
                time.sleep(DELAY_MEDIUM)
                
                # 모달창 닫힘 확인
                modal_elements = self.driver.find_elements(By.CSS_SELECTOR, ".ant-modal, .ant-drawer")
                visible_modals = [modal for modal in modal_elements if modal.is_displayed()]
                
                if not visible_modals:
                    logger.info(f"수정화면 모달창 닫기 성공 (시도 {esc_attempt + 1}/3)")
                    break
                else:
                    logger.warning(f"수정화면 모달창 아직 열려있음 (시도 {esc_attempt + 1}/3)")
            
            # 최종 모달창 상태 확인
            try:
                time.sleep(DELAY_SHORT)  # 모달창 완전 닫힘 대기
                
                modal_elements = self.driver.find_elements(By.CSS_SELECTOR, ".ant-modal, .ant-drawer")
                visible_modals = [modal for modal in modal_elements if modal.is_displayed()]
                
                if visible_modals:
                    logger.error("수정화면 모달창이 완전히 닫히지 않음 - 그룹이동 실패 가능성 높음")
                    # 추가 강제 닫기 시도
                    for modal in visible_modals:
                        try:
                            close_btn = modal.find_element(By.CSS_SELECTOR, ".ant-modal-close, .ant-drawer-close")
                            close_btn.click()
                            time.sleep(DELAY_VERY_SHORT)
                        except:
                            pass
                else:
                    logger.info("그룹이동 시작 전 모달창 닫힘 확인 완료")
            except Exception as final_modal_check_error:
                logger.error(f"그룹이동 전 모달창 상태 최종 확인 중 오류: {final_modal_check_error}")
            
            logger.info("상품 수정 작업 완료")
            return True
            
        except Exception as e:
            logger.error(f"상품 수정 작업 중 오류: {e}")
            return False
        finally:
            # M열 데이터 참조 정리
            self.current_m_data = None
    
    def _parse_action_command(self, data):
        """
        액션 명령어 파싱 (YES/NO 또는 구조화된 명령어)
        
        Args:
            data: 파싱할 데이터 (예: "YES", "last:2", "first:3", "specific:1,3", "copy:5", "first:1/last:1")
            
        Returns:
            dict: 파싱된 액션 정보
                - action: 'yes', 'no', 'last', 'first', 'specific', 'copy', 'combined'
                - count: 숫자 (last, first, copy용)
                - positions: 리스트 (specific용)
                - actions: 리스트 (combined용 - 복합 명령어)
        """
        if not data:
            return {'action': 'no'}
        
        data_str = str(data).strip()
        
        # 빈 문자열 또는 NO 처리
        if not data_str or data_str.upper() == 'NO':
            return {'action': 'no'}
        
        # YES 처리
        if data_str.upper() == 'YES':
            return {'action': 'yes'}
        
        # 슬래시로 구분된 복합 명령어 처리 (예: "first:1/last:1")
        if '/' in data_str:
            try:
                parts = data_str.split('/')
                combined_actions = []
                
                for part in parts:
                    part = part.strip()
                    if not part:
                        continue
                    
                    # 각 부분을 개별적으로 파싱
                    parsed_part = self._parse_single_action_command(part)
                    if parsed_part['action'] != 'no':
                        combined_actions.append(parsed_part)
                
                if combined_actions:
                    logger.info(f"복합 명령어 파싱 완료: {data_str} -> {len(combined_actions)}개 액션")
                    return {'action': 'combined', 'actions': combined_actions}
                else:
                    logger.warning(f"복합 명령어에서 유효한 액션을 찾을 수 없음: {data_str}")
                    return {'action': 'no'}
                    
            except Exception as e:
                logger.warning(f"복합 명령어 파싱 중 오류: {data_str}, 오류: {e}")
                return {'action': 'no'}
        
        # 단일 명령어 파싱
        return self._parse_single_action_command(data_str)
    
    def _parse_single_action_command(self, data_str):
        """
        단일 액션 명령어 파싱
        
        Args:
            data_str: 파싱할 단일 명령어 문자열
            
        Returns:
            dict: 파싱된 액션 정보
        """
        # 구조화된 명령어 파싱
        if ':' in data_str:
            try:
                prefix, value = data_str.split(':', 1)
                prefix = prefix.strip().lower()
                value = value.strip()
                
                if not value:
                    logger.warning(f"빈 값이 제공됨: {data_str}")
                    return {'action': 'no'}
                
                if prefix in ['last', 'first', 'copy']:
                    try:
                        count = int(value)
                        if count <= 0:
                            logger.warning(f"잘못된 카운트 값 (0 이하): {count}")
                            return {'action': 'no'}
                        return {'action': prefix, 'count': count}
                    except ValueError:
                        logger.warning(f"잘못된 숫자 형식: {value}")
                        return {'action': 'no'}
                
                elif prefix == 'specific':
                    try:
                        # 'all' 값 특별 처리
                        if value.strip().lower() == 'all':
                            logger.info("specific:all 형식 - 중문글자 이미지 자동 감지 모드")
                            return {'action': 'specific', 'positions': ['all']}
                        
                        positions = []
                        for pos_str in value.split(','):
                            pos_str = pos_str.strip()
                            if pos_str.lower() == 'all':
                                positions.append('all')
                            else:
                                pos = int(pos_str)
                                if pos <= 0:
                                    logger.warning(f"잘못된 위치 값 (0 이하): {pos}")
                                    return {'action': 'no'}
                                positions.append(pos)
                        
                        if not positions:
                            logger.warning(f"빈 위치 리스트: {value}")
                            return {'action': 'no'}
                        
                        return {'action': 'specific', 'positions': positions}
                    except ValueError:
                        logger.warning(f"잘못된 위치 형식: {value}")
                        return {'action': 'no'}
                
                elif prefix == 'special':
                    try:
                        max_position = int(value)
                        if max_position <= 0:
                            logger.warning(f"잘못된 special 값 (0 이하): {max_position}")
                            return {'action': 'no'}
                        logger.info(f"special:{max_position} 형식 - 최대 {max_position}번째까지 스캔")
                        return {'action': 'special', 'max_position': max_position}
                    except ValueError:
                        logger.warning(f"잘못된 special 형식: {value}")
                        return {'action': 'no'}
                
                else:
                    logger.warning(f"알 수 없는 명령어 접두사: {prefix}")
                    return {'action': 'no'}
                    
            except ValueError:
                logger.warning(f"잘못된 명령어 형식: {data_str}")
                return {'action': 'no'}
        
        # 구조화되지 않은 명령어는 기본적으로 YES로 처리
        logger.info(f"구조화되지 않은 명령어를 YES로 처리: {data_str}")
        return {'action': 'yes'}
    
    def _delete_images_by_position(self, action_info):
        """
        위치 기반 이미지 삭제
        
        Args:
            action_info: 파싱된 액션 정보
            
        Returns:
            bool: 성공 여부
        """
        try:
            action = action_info.get('action')
            
            if action == 'no':
                logger.info("이미지 삭제 작업 건너뜀")
                return True
            
            # 일괄편집 모달창 열기 (1단계 코어와 동일한 방식 사용)
            logger.info("일괄편집 모달창 열기 시작")
            try:
                # image_utils.py에서 이미지 관리자 가져오기
                from image_utils3 import PercentyImageManager3
                 
                 # 이미지 관리자 초기화
                image_manager = PercentyImageManager3(self.driver)
                
                # 일괄편집 모달 창 열기
                if image_manager.open_bulk_edit_modal():
                    logger.info("일괄편집 모달창 열기 성공")
                else:
                    logger.error("일괄편집 모달창 열기 실패")
                    return False
                    
            except Exception as e:
                logger.error(f"일괄편집 모달창 열기 실패: {e}")
                return False
            
            # image_manager를 우선 사용하되, 실패 시 직접 구현 사용
            try:
                if action == 'combined':
                    # 복합 명령어 처리 (예: first:1/last:1)
                    actions = action_info.get('actions', [])
                    logger.info(f"복합 이미지 삭제 시작: {len(actions)}개 액션")
                    
                    all_success = True
                    for i, sub_action in enumerate(actions):
                        logger.info(f"복합 액션 {i+1}/{len(actions)} 실행: {sub_action}")
                        # 복합 액션에서는 모달창을 다시 열지 않고 직접 이미지 삭제 작업만 수행
                        success = self._execute_single_image_action(sub_action)
                        if not success:
                            logger.warning(f"복합 액션 {i+1} 실패: {sub_action}")
                            all_success = False
                    
                    return all_success
                
                elif action == 'last':
                    count = action_info.get('count', 1)
                    logger.info(f"마지막 {count}개 이미지 삭제 시작")
                    return self.image_manager.delete_last_images(count)
                
                elif action == 'first':
                    count = action_info.get('count', 1)
                    logger.info(f"처음 {count}개 이미지 삭제 시작")
                    return self.image_manager.delete_first_images(count)
                
                elif action == 'specific':
                    positions = action_info.get('positions', [])
                    logger.info(f"특정 위치 이미지 삭제 시작: {positions}")
                    return self.image_manager.delete_images_by_positions(positions)
                
                elif action == 'yes':
                    # 기본 동작: 마지막 1개 이미지 삭제
                    logger.info("기본 이미지 삭제 (마지막 1개)")
                    return self.image_manager.delete_last_images(1)
                    
            except Exception as e:
                logger.warning(f"image_manager 사용 실패, 직접 구현으로 전환: {e}")
                return self._delete_images_direct(action_info)
            
            return True
            
        except Exception as e:
            logger.error(f"위치 기반 이미지 삭제 중 오류: {e}")
            return False
    
    def _execute_single_image_action(self, action_info):
        """
        모달창을 다시 열지 않고 단일 이미지 액션만 실행 (복합 액션용)
        
        Args:
            action_info: 파싱된 액션 정보
            
        Returns:
            bool: 성공 여부
        """
        try:
            action = action_info.get('action')
            
            if action == 'no':
                logger.info("이미지 삭제 작업 건너뜀")
                return True
            
            # image_manager를 사용하여 이미지 삭제 작업만 수행
            try:
                if action == 'last':
                    count = action_info.get('count', 1)
                    logger.info(f"마지막 {count}개 이미지 삭제 시작")
                    return self.image_manager.delete_last_images(count)
                
                elif action == 'first':
                    count = action_info.get('count', 1)
                    logger.info(f"처음 {count}개 이미지 삭제 시작")
                    return self.image_manager.delete_first_images(count)
                
                elif action == 'specific':
                    positions = action_info.get('positions', [])
                    logger.info(f"특정 위치 이미지 삭제 시작: {positions}")
                    return self.image_manager.delete_images_by_positions(positions)
                
                elif action == 'yes':
                    # 기본 동작: 마지막 1개 이미지 삭제
                    logger.info("기본 이미지 삭제 (마지막 1개)")
                    return self.image_manager.delete_last_images(1)
                    
            except Exception as e:
                logger.warning(f"image_manager 사용 실패, 직접 구현으로 전환: {e}")
                return self._delete_images_direct(action_info)
            
            return True
            
        except Exception as e:
            logger.error(f"단일 이미지 액션 실행 중 오류: {e}")
            return False
    
    def _delete_images_direct(self, action_info):
        """
        직접 구현을 통한 이미지 삭제 (image_manager 실패 시 백업)
        
        Args:
            action_info: 파싱된 액션 정보
            
        Returns:
            bool: 성공 여부
        """
        try:
            action = action_info.get('action')
            
            # 페이지 로딩 대기 최적화
            time.sleep(0.1)
            
            # 이미지 목록 가져오기 (다양한 셀렉터 시도)
            image_selectors = [
                ".image-item img",
                ".product-image img", 
                "img[src*='product']",
                ".image-list img",
                ".gallery img",
                "img[alt*='상품']",
                ".upload-image img"
            ]
            
            image_elements = []
            for selector in image_selectors:
                image_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if image_elements:
                    logger.info(f"이미지 요소 발견: {selector} ({len(image_elements)}개)")
                    break
            
            if not image_elements:
                logger.warning("삭제할 이미지가 없습니다")
                return True
            
            total_images = len(image_elements)
            logger.info(f"총 {total_images}개의 이미지 발견")
            
            # 삭제할 이미지 인덱스 결정
            delete_indices = []
            
            if action == 'yes':
                # 기본: 마지막 이미지 삭제
                delete_indices = [total_images - 1]
            elif action == 'last':
                count = min(action_info.get('count', 1), total_images)
                delete_indices = list(range(total_images - count, total_images))
            elif action == 'first':
                count = min(action_info.get('count', 1), total_images)
                delete_indices = list(range(count))
            elif action == 'specific':
                positions = action_info.get('positions', [])
                delete_indices = [pos - 1 for pos in positions if 1 <= pos <= total_images]
            
            if not delete_indices:
                logger.warning("삭제할 유효한 이미지 인덱스가 없습니다")
                return True
            
            # 중복 제거 및 역순 정렬 (인덱스 변경 방지)
            delete_indices = sorted(list(set(delete_indices)), reverse=True)
            logger.info(f"삭제할 이미지 인덱스: {[idx + 1 for idx in delete_indices]}")
            
            deleted_count = 0
            for idx in delete_indices:
                try:
                    if 0 <= idx < len(image_elements):
                        image_element = image_elements[idx]
                        
                        # 이미지 요소가 여전히 유효한지 확인
                        if not image_element.is_displayed():
                            logger.warning(f"이미지 {idx + 1}이 더 이상 표시되지 않음")
                            continue
                        
                        # 이미지 선택 (클릭 또는 체크박스)
                        try:
                            # 체크박스가 있는지 확인
                            checkbox = image_element.find_element(By.XPATH, "./ancestor::*[contains(@class, 'image-item')]//input[@type='checkbox']")
                            if not checkbox.is_selected():
                                self.driver.execute_script("arguments[0].click();", checkbox)
                        except:
                            # 체크박스가 없으면 이미지 직접 클릭
                            self.driver.execute_script("arguments[0].click();", image_element)
                        
                        time.sleep(0.2)
                        
                        # 삭제 버튼 찾기 및 클릭
                        delete_selectors = [
                            ".delete-btn",
                            ".remove-btn", 
                            "button[onclick*='delete']",
                            "button[title*='삭제']",
                            ".btn-delete",
                            "[data-action='delete']"
                        ]
                        
                        delete_btn = None
                        for selector in delete_selectors:
                            try:
                                delete_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                                if delete_btn.is_displayed():
                                    break
                            except:
                                continue
                        
                        if not delete_btn:
                            logger.warning(f"이미지 {idx + 1}의 삭제 버튼을 찾을 수 없음")
                            continue
                        
                        self.driver.execute_script("arguments[0].click();", delete_btn)
                        time.sleep(0.2)
                        
                        # 확인 대화상자 처리
                        confirmation_handled = False
                        
                        # 모달 확인 버튼 시도
                        confirm_selectors = [
                            ".confirm-btn",
                            ".ok-btn", 
                            "button[onclick*='confirm']",
                            ".btn-confirm",
                            "button:contains('확인')",
                            "button:contains('삭제')"
                        ]
                        
                        for selector in confirm_selectors:
                            try:
                                confirm_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                                if confirm_btn.is_displayed():
                                    self.driver.execute_script("arguments[0].click();", confirm_btn)
                                    confirmation_handled = True
                                    break
                            except:
                                continue
                        
                        # Alert 처리
                        if not confirmation_handled:
                            try:
                                alert = self.driver.switch_to.alert
                                alert.accept()
                                confirmation_handled = True
                            except:
                                pass
                        
                        time.sleep(0.3)
                        deleted_count += 1
                        logger.info(f"이미지 {idx + 1} 삭제 완료")
                        
                except Exception as e:
                    logger.warning(f"이미지 {idx + 1} 삭제 실패: {e}")
                    continue
            
            logger.info(f"직접 이미지 삭제 작업 완료: {deleted_count}/{len(delete_indices)}개 삭제")
            return deleted_count > 0
            
        except Exception as e:
            logger.error(f"직접 이미지 삭제 중 오류: {e}")
            return False
    
    def _process_h_data(self, h_data):
        """
        H열 데이터 처리 (이미지 삭제)
        
        Args:
            h_data: H열 데이터 (예: "YES", "last:2", "first:3", "specific:1,3")
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"H열 데이터 처리 (이미지 삭제): {h_data}")
            
            # 명령어 파싱
            action_info = self._parse_action_command(h_data)
            
            if action_info['action'] == 'no':
                logger.info("H열: 이미지 삭제 작업 없음")
                return True
            
            # 상세페이지 탭으로 이동 (H열은 이미지 삭제 작업)
            tab_key = self.COLUMN_TAB_MAPPING.get('H', 'PRODUCT_TAB_DETAIL')
            smart_click(self.driver, UI_ELEMENTS[tab_key], DELAY_VERY_SHORT)
            time.sleep(DELAY_SHORT)
            
            # 위치 기반 이미지 삭제 실행
            success = self._delete_images_by_position(action_info)
            
            if success:
                logger.info("H열: 이미지 삭제 완료")
                
                # 이미지편집 모달창 닫기
                try:
                    logger.info("H열: 이미지편집 모달창 닫기 시작")
                    # ESC 키로 간단하게 모달창 닫기
                    ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
                    time.sleep(DELAY_MEDIUM)
                    logger.info("H열: 이미지편집 모달창 닫기 완료")
                except Exception as modal_error:
                    logger.error(f"H열: 이미지편집 모달창 닫기 중 오류: {modal_error}")
            else:
                logger.warning("H열: 이미지 삭제 실패")
            
            return success
            
        except Exception as e:
            logger.error(f"H열 데이터 처리 중 오류: {e}")
            return False
    
    def _process_i_data(self, i_data):
        """
        I열 데이터 처리 (썸네일 삭제)
        
        Args:
            i_data: I열 데이터 (예: "YES", "last:2", "first:3", "specific:1,3")
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"I열 데이터 처리 (썸네일 삭제): {i_data}")
            
            # 명령어 파싱
            action_info = self._parse_action_command(i_data)
            
            if action_info['action'] == 'no':
                logger.info("I열: 썸네일 삭제 작업 없음")
                return True
            
            # H열에서 이미 이미지편집 모달창을 닫았으므로 별도 확인 불필요
            logger.info("I열: 썸네일 탭 접근 준비")
            time.sleep(DELAY_MEDIUM)  # 기본 대기 시간
            
            # 썸네일 탭으로 이동 (I열은 썸네일 삭제 작업)
            logger.info("I열: 썸네일 탭으로 이동 시작")
            tab_key = self.COLUMN_TAB_MAPPING.get('I', 'PRODUCT_TAB_THUMBNAIL')
            
            # 탭 요소가 존재하는지 먼저 확인
            tab_element_found = False
            max_retries = 5
            for retry in range(max_retries):
                try:
                    from ui_elements import UI_ELEMENTS
                    tab_info = UI_ELEMENTS[tab_key]
                    dom_selector = tab_info.get('dom_selector')
                    
                    if dom_selector:
                        element = self.driver.find_element(By.XPATH, dom_selector)
                        if element.is_displayed():
                            logger.info(f"I열: 썸네일 탭 요소 발견 (재시도 {retry + 1}/{max_retries})")
                            tab_element_found = True
                            break
                except Exception as e:
                    logger.warning(f"I열: 썸네일 탭 요소 확인 실패 (재시도 {retry + 1}/{max_retries}): {e}")
                    time.sleep(DELAY_MEDIUM)
            
            if not tab_element_found:
                logger.error("I열: 썸네일 탭 요소를 찾을 수 없음, 좌표 클릭으로 시도")
            
            smart_click(self.driver, UI_ELEMENTS[tab_key], DELAY_VERY_SHORT)
            time.sleep(DELAY_LONG)  # 탭 전환 대기 시간 증가
            
            # 썸네일 삭제 실행
            success = self._delete_thumbnails_by_position(action_info)
            
            if success:
                logger.info("I열: 썸네일 삭제 완료")
            else:
                logger.warning("I열: 썸네일 삭제 실패")
            
            return success
            
        except Exception as e:
            logger.error(f"I열 데이터 처리 중 오류: {e}")
            return False
    
    def _delete_thumbnails_by_position(self, action_info):
        """
        위치 기반 썸네일 삭제
        
        Args:
            action_info: 파싱된 액션 정보
            
        Returns:
            bool: 성공 여부
        """
        try:
            action = action_info.get('action')
            
            if action == 'no':
                logger.info("썸네일 삭제 작업 건너뜀")
                return True
            
            # image_manager를 우선 사용하되, 실패 시 직접 구현 사용
            try:
                if action == 'combined':
                    # 복합 명령어 처리 (예: first:1/last:1)
                    actions = action_info.get('actions', [])
                    logger.info(f"복합 썸네일 삭제 시작: {len(actions)}개 액션")
                    
                    all_success = True
                    for i, sub_action in enumerate(actions):
                        logger.info(f"복합 액션 {i+1}/{len(actions)} 실행: {sub_action}")
                        success = self._delete_thumbnails_by_position(sub_action)
                        if not success:
                            logger.warning(f"복합 액션 {i+1} 실패: {sub_action}")
                            all_success = False
                    
                    return all_success
                
                elif action == 'last':
                    count = action_info.get('count', 1)
                    logger.info(f"마지막 {count}개 썸네일 삭제 시작")
                    total_count = self.image_manager.get_total_thumbnail_count()
                    if total_count > 0:
                        return self.image_manager.delete_last_thumbnails(count, total_count)
                    else:
                        logger.warning("썸네일이 없어 삭제 작업을 건너뜁니다.")
                        return True
                
                elif action == 'first':
                    count = action_info.get('count', 1)
                    logger.info(f"처음 {count}개 썸네일 삭제 시작")
                    total_count = self.image_manager.get_total_thumbnail_count()
                    if total_count > 0:
                        return self.image_manager.delete_first_thumbnails(count, total_count)
                    else:
                        logger.warning("썸네일이 없어 삭제 작업을 건너뜁니다.")
                        return True
                
                elif action == 'specific':
                    positions = action_info.get('positions', [])
                    logger.info(f"특정 위치 썸네일 삭제 시작: {positions}")
                    # 총 썸네일 개수를 먼저 확인해야 함
                    total_count = self.image_manager.get_total_thumbnail_count()
                    if total_count > 0:
                        return self.image_manager.delete_specific_thumbnails(positions, total_count)
                    else:
                        logger.warning("썸네일이 없어 삭제 작업을 건너뜁니다.")
                        return True
                
                elif action == 'yes':
                    # 기본 동작: 마지막 1개 썸네일 삭제
                    logger.info("기본 썸네일 삭제 (마지막 1개)")
                    total_count = self.image_manager.get_total_thumbnail_count()
                    if total_count > 0:
                        return self.image_manager.delete_last_thumbnails(1, total_count)
                    else:
                        logger.warning("썸네일이 없어 삭제 작업을 건너뜁니다.")
                        return True
                    
            except Exception as e:
                logger.warning(f"image_manager 썸네일 삭제 실패, 직접 구현으로 전환: {e}")
                return self._delete_thumbnails_direct(action_info)
            
            return True
            
        except Exception as e:
            logger.error(f"위치 기반 썸네일 삭제 중 오류: {e}")
            return False
    
    def _delete_thumbnails_direct(self, action_info):
        """
        직접 구현을 통한 썸네일 삭제 (image_manager 실패 시 백업)
        
        Args:
            action_info: 파싱된 액션 정보
            
        Returns:
            bool: 성공 여부
        """
        try:
            action = action_info.get('action')
            
            # 페이지 로딩 대기 최적화
            time.sleep(0.1)
            
            # 썸네일 목록 가져오기 (다양한 셀렉터 시도)
            thumbnail_selectors = [
                ".thumbnail-item img",
                ".thumb-image img", 
                "img[src*='thumb']",
                ".thumbnail-list img",
                ".thumb-gallery img",
                "img[alt*='썸네일']",
                ".small-image img",
                ".preview-image img"
            ]
            
            thumbnail_elements = []
            for selector in thumbnail_selectors:
                thumbnail_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if thumbnail_elements:
                    logger.info(f"썸네일 요소 발견: {selector} ({len(thumbnail_elements)}개)")
                    break
            
            if not thumbnail_elements:
                logger.warning("삭제할 썸네일이 없습니다")
                return True
            
            total_thumbnails = len(thumbnail_elements)
            logger.info(f"총 {total_thumbnails}개의 썸네일 발견")
            
            # 삭제할 썸네일 인덱스 결정
            delete_indices = []
            
            if action == 'yes':
                # 기본: 마지막 썸네일 삭제
                delete_indices = [total_thumbnails - 1]
            elif action == 'last':
                count = min(action_info.get('count', 1), total_thumbnails)
                delete_indices = list(range(total_thumbnails - count, total_thumbnails))
            elif action == 'first':
                count = min(action_info.get('count', 1), total_thumbnails)
                delete_indices = list(range(count))
            elif action == 'specific':
                positions = action_info.get('positions', [])
                delete_indices = [pos - 1 for pos in positions if 1 <= pos <= total_thumbnails]
            
            if not delete_indices:
                logger.warning("삭제할 유효한 썸네일 인덱스가 없습니다")
                return True
            
            # 중복 제거 및 역순 정렬 (인덱스 변경 방지)
            delete_indices = sorted(list(set(delete_indices)), reverse=True)
            logger.info(f"삭제할 썸네일 인덱스: {[idx + 1 for idx in delete_indices]}")
            
            deleted_count = 0
            for idx in delete_indices:
                try:
                    if 0 <= idx < len(thumbnail_elements):
                        thumbnail_element = thumbnail_elements[idx]
                        
                        # 썸네일 요소가 여전히 유효한지 확인
                        if not thumbnail_element.is_displayed():
                            logger.warning(f"썸네일 {idx + 1}이 더 이상 표시되지 않음")
                            continue
                        
                        # 썸네일 선택 (클릭 또는 체크박스)
                        try:
                            # 체크박스가 있는지 확인
                            checkbox = thumbnail_element.find_element(By.XPATH, "./ancestor::*[contains(@class, 'thumbnail-item')]//input[@type='checkbox']")
                            if not checkbox.is_selected():
                                self.driver.execute_script("arguments[0].click();", checkbox)
                        except:
                            # 체크박스가 없으면 썸네일 직접 클릭
                            self.driver.execute_script("arguments[0].click();", thumbnail_element)
                        
                        time.sleep(0.2)
                        
                        # 삭제 버튼 찾기 및 클릭
                        delete_selectors = [
                            ".delete-thumbnail",
                            ".remove-thumb", 
                            "button[onclick*='deleteThumbnail']",
                            "button[title*='썸네일 삭제']",
                            ".btn-delete-thumb",
                            "[data-action='delete-thumbnail']"
                        ]
                        
                        delete_btn = None
                        for selector in delete_selectors:
                            try:
                                delete_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                                if delete_btn.is_displayed():
                                    break
                            except:
                                continue
                        
                        if not delete_btn:
                            logger.warning(f"썸네일 {idx + 1}의 삭제 버튼을 찾을 수 없음")
                            continue
                        
                        self.driver.execute_script("arguments[0].click();", delete_btn)
                        time.sleep(0.2)
                        
                        # 확인 대화상자 처리
                        confirmation_handled = False
                        
                        # 모달 확인 버튼 시도
                        confirm_selectors = [
                            ".confirm-btn",
                            ".ok-btn", 
                            "button[onclick*='confirm']",
                            ".btn-confirm",
                            "button:contains('확인')",
                            "button:contains('삭제')"
                        ]
                        
                        for selector in confirm_selectors:
                            try:
                                confirm_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                                if confirm_btn.is_displayed():
                                    self.driver.execute_script("arguments[0].click();", confirm_btn)
                                    confirmation_handled = True
                                    break
                            except:
                                continue
                        
                        # Alert 처리
                        if not confirmation_handled:
                            try:
                                alert = self.driver.switch_to.alert
                                alert.accept()
                                confirmation_handled = True
                            except:
                                pass
                        
                        time.sleep(0.3)
                        deleted_count += 1
                        logger.info(f"썸네일 {idx + 1} 삭제 완료")
                        
                except Exception as e:
                    logger.warning(f"썸네일 {idx + 1} 삭제 실패: {e}")
                    continue
            
            logger.info(f"직접 썸네일 삭제 작업 완료: {deleted_count}/{len(delete_indices)}개 삭제")
            return deleted_count > 0
            
        except Exception as e:
            logger.error(f"직접 썸네일 삭제 중 오류: {e}")
            return False
    
    def _process_j_data(self, j_data):
        """
        J열 데이터 처리 (옵션 이미지 복사)
        
        Args:
            j_data: J열 데이터 (예: "YES", "copy:2", "copy:5")
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"J열 데이터 처리 (옵션 이미지 복사): {j_data}")
            
            # 명령어 파싱
            action_info = self._parse_action_command(j_data)
            
            if action_info['action'] == 'no':
                logger.info("J열: 옵션 이미지 복사 작업 없음")
                return True
            
            # 옵션 탭으로 이동 (J열은 옵션 이미지 복사 작업)
            logger.info("J열: 옵션 탭으로 이동 시작")
            tab_key = self.COLUMN_TAB_MAPPING.get('J', 'PRODUCT_TAB_OPTION')
            
            # 탭 요소가 존재하는지 먼저 확인
            tab_element_found = False
            max_retries = 5
            for retry in range(max_retries):
                try:
                    from ui_elements import UI_ELEMENTS
                    tab_info = UI_ELEMENTS[tab_key]
                    dom_selector = tab_info.get('dom_selector')
                    
                    if dom_selector:
                        element = self.driver.find_element(By.XPATH, dom_selector)
                        if element.is_displayed():
                            logger.info(f"J열: 옵션 탭 요소 발견 (재시도 {retry + 1}/{max_retries})")
                            tab_element_found = True
                            break
                except Exception as e:
                    logger.warning(f"J열: 옵션 탭 요소 확인 실패 (재시도 {retry + 1}/{max_retries}): {e}")
                    time.sleep(DELAY_MEDIUM)
            
            if not tab_element_found:
                logger.error("J열: 옵션 탭 요소를 찾을 수 없음, 좌표 클릭으로 시도")
            
            smart_click(self.driver, UI_ELEMENTS[tab_key], DELAY_VERY_SHORT)
            time.sleep(DELAY_LONG)  # 탭 전환 대기 시간 증가
            
            # 옵션 이미지 복사 실행
            success = self._copy_option_images(action_info)
            
            if success:
                logger.info("J열: 옵션 이미지 복사 완료")
            else:
                logger.warning("J열: 옵션 이미지 복사 실패")
            
            return success
            
        except Exception as e:
            logger.error(f"J열 데이터 처리 중 오류: {e}")
            return False
    
    def _copy_option_images(self, action_info):
        """
        옵션 이미지 복사
        
        Args:
            action_info: 파싱된 액션 정보
            
        Returns:
            bool: 성공 여부
        """
        try:
            action = action_info.get('action')
            
            if action == 'no':
                logger.info("옵션 이미지 복사 작업 건너뜀")
                return True
            
            # image_manager를 우선 사용하되, 실패 시 직접 구현 사용
            try:
                if action == 'combined':
                    # 복합 명령어 처리 (예: copy:1/copy:2)
                    actions = action_info.get('actions', [])
                    logger.info(f"복합 옵션 이미지 복사 시작: {len(actions)}개 액션")
                    
                    all_success = True
                    for i, sub_action in enumerate(actions):
                        logger.info(f"복합 액션 {i+1}/{len(actions)} 실행: {sub_action}")
                        success = self._copy_option_images(sub_action)
                        if not success:
                            logger.warning(f"복합 액션 {i+1} 실패: {sub_action}")
                            all_success = False
                    
                    return all_success
                
                elif action == 'copy':
                    count = action_info.get('count', 1)
                    logger.info(f"{count}개 옵션 이미지 복사 시작")
                    return self.image_manager.copy_option_images(count)
                
                elif action == 'yes':
                    # 기본 동작: 1개 옵션 이미지 복사
                    logger.info("기본 옵션 이미지 복사 (1개)")
                    return self.image_manager.copy_option_images(1)
                    
            except Exception as e:
                logger.warning(f"image_manager 옵션 이미지 복사 실패, 직접 구현으로 전환: {e}")
                return self._copy_option_images_direct(action_info)
            
            return True
            
        except Exception as e:
            logger.error(f"옵션 이미지 복사 중 오류: {e}")
            return False
    
    def _copy_option_images_direct(self, action_info):
        """
        직접 구현을 통한 옵션 이미지 복사 (image_manager 실패 시 백업)
        
        Args:
            action_info: 파싱된 액션 정보
            
        Returns:
            bool: 성공 여부
        """
        try:
            action = action_info.get('action')
            
            # 복사할 개수 결정
            if action == 'copy':
                copy_count = action_info.get('count', 1)
            elif action == 'yes':
                copy_count = 1
            else:
                return True
            
            logger.info(f"직접 구현으로 {copy_count}개 옵션 이미지 복사 시작")
            
            # 페이지 로딩 대기 최적화
            time.sleep(0.1)
            
            # 옵션 탭으로 이동
            option_tab_selectors = [
                "a[href*='option']",
                ".tab-option",
                "button[data-tab='option']",
                "[role='tab']:contains('옵션')"
            ]
            
            option_tab_clicked = False
            for selector in option_tab_selectors:
                try:
                    option_tab = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if option_tab.is_displayed():
                        self.driver.execute_script("arguments[0].click();", option_tab)
                        option_tab_clicked = True
                        break
                except:
                    continue
            
            if not option_tab_clicked:
                logger.warning("옵션 탭을 찾을 수 없음")
                return False
            
            time.sleep(2)
            
            # 기존 이미지 목록 가져오기
            image_selectors = [
                ".product-image img",
                ".main-image img", 
                "img[src*='product']",
                ".image-list img",
                ".gallery img"
            ]
            
            source_images = []
            for selector in image_selectors:
                source_images = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if source_images:
                    logger.info(f"소스 이미지 발견: {selector} ({len(source_images)}개)")
                    break
            
            if not source_images:
                logger.warning("복사할 소스 이미지가 없습니다")
                return False
            
            # 복사할 이미지 개수 제한
            actual_copy_count = min(copy_count, len(source_images))
            logger.info(f"실제 복사할 이미지 개수: {actual_copy_count}")
            
            copied_count = 0
            for i in range(actual_copy_count):
                try:
                    source_image = source_images[i]
                    
                    # 이미지 URL 가져오기
                    image_src = source_image.get_attribute('src')
                    if not image_src:
                        logger.warning(f"이미지 {i + 1}의 src 속성을 가져올 수 없음")
                        continue
                    
                    # 옵션 이미지 추가 버튼 찾기
                    add_option_selectors = [
                        ".add-option-image",
                        ".btn-add-option",
                        "button[onclick*='addOption']",
                        "[data-action='add-option-image']",
                        ".option-image-add"
                    ]
                    
                    add_btn = None
                    for selector in add_option_selectors:
                        try:
                            add_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                            if add_btn.is_displayed():
                                break
                        except:
                            continue
                    
                    if not add_btn:
                        logger.warning("옵션 이미지 추가 버튼을 찾을 수 없음")
                        break
                    
                    # 추가 버튼 클릭
                    self.driver.execute_script("arguments[0].click();", add_btn)
                    time.sleep(1)
                    
                    # 이미지 URL 입력 또는 파일 업로드
                    url_input_selectors = [
                        "input[name*='image_url']",
                        "input[placeholder*='이미지']",
                        ".image-url-input",
                        "input[type='url']"
                    ]
                    
                    url_input = None
                    for selector in url_input_selectors:
                        try:
                            url_input = self.driver.find_element(By.CSS_SELECTOR, selector)
                            if url_input.is_displayed():
                                break
                        except:
                            continue
                    
                    if url_input:
                        # URL 입력 방식
                        url_input.clear()
                        url_input.send_keys(image_src)
                        time.sleep(0.2)
                        
                        # 확인 버튼 클릭
                        confirm_selectors = [
                            ".confirm-btn",
                            ".ok-btn",
                            "button[type='submit']",
                            ".btn-confirm"
                        ]
                        
                        for selector in confirm_selectors:
                            try:
                                confirm_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                                if confirm_btn.is_displayed():
                                    self.driver.execute_script("arguments[0].click();", confirm_btn)
                                    break
                            except:
                                continue
                    
                    time.sleep(1)
                    copied_count += 1
                    logger.info(f"옵션 이미지 {i + 1} 복사 완료")
                    
                except Exception as e:
                    logger.warning(f"옵션 이미지 {i + 1} 복사 실패: {e}")
                    continue
            
            logger.info(f"직접 옵션 이미지 복사 작업 완료: {copied_count}/{actual_copy_count}개 복사")
            return copied_count > 0
            
        except Exception as e:
            logger.error(f"직접 옵션 이미지 복사 중 오류: {e}")
            return False
    
    def _process_k_data(self, k_data):
        """
        K열 데이터 처리 (이미지 번역)
        
        Args:
            k_data: K열 데이터 (예: "YES", "last:2", "first:3", "specific:1,3")
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"K열 데이터 처리 (이미지 번역): {k_data}")
            
            # 명령어 파싱
            action_info = self._parse_action_command(k_data)
            
            if action_info['action'] == 'no':
                logger.info("K열: 이미지 번역 작업 없음")
                return True
            
            # 상세페이지 탭으로 이동 전 모달창 상태 안정화
            logger.info("K열: 상세페이지 탭 클릭 전 모달창 상태 확인")
            time.sleep(DELAY_SHORT)  # 모달창 안정화 대기
            
            # 모달창이 완전히 로드되었는지 확인
            try:
                modal_elements = self.driver.find_elements(By.CSS_SELECTOR, ".ant-modal, .ant-drawer")
                visible_modals = [modal for modal in modal_elements if modal.is_displayed()]
                
                if visible_modals:
                    logger.info("K열: 모달창 확인됨 - 상세페이지 탭 클릭 진행")
                else:
                    logger.warning("K열: 모달창이 감지되지 않음 - 탭 클릭 시도")
            except Exception as modal_check_error:
                logger.warning(f"K열: 모달창 상태 확인 중 오류: {modal_check_error}")
            
            # 상세페이지 탭으로 이동 (K열은 이미지 번역 작업)
            tab_key = self.COLUMN_TAB_MAPPING.get('K', 'PRODUCT_TAB_DETAIL')
            logger.info(f"K열: 상세페이지 탭 클릭 시도 - {tab_key}")
            
            try:
                smart_click(self.driver, UI_ELEMENTS[tab_key], DELAY_VERY_SHORT)
                time.sleep(DELAY_SHORT)
                logger.info("K열: 상세페이지 탭 클릭 성공")
            except Exception as tab_click_error:
                logger.error(f"K열: 상세페이지 탭 클릭 실패: {tab_click_error}")
                # 탭 클릭 실패 시 재시도
                try:
                    logger.info("K열: 상세페이지 탭 클릭 재시도")
                    time.sleep(DELAY_SHORT)
                    smart_click(self.driver, UI_ELEMENTS[tab_key], DELAY_VERY_SHORT)
                    time.sleep(DELAY_SHORT)
                    logger.info("K열: 상세페이지 탭 클릭 재시도 성공")
                except Exception as retry_error:
                    logger.error(f"K열: 상세페이지 탭 클릭 재시도 실패: {retry_error}")
                    return False
            
            # 복합 명령어 처리
            if action_info['action'] == 'combined':
                # 복합 명령어 처리 (예: first:1/last:1)
                actions = action_info.get('actions', [])
                logger.info(f"복합 이미지 번역 시작: {len(actions)}개 액션")
                
                # 복합 액션은 통합 처리 방식 사용 (모달창 한 번만 열기)
                success = self._execute_combined_translate_actions(actions)
            elif action_info['action'] == 'special':
                # special 액션 처리
                max_position = action_info.get('max_position', 10)
                logger.info(f"제한된 스캔 이미지 번역 시작: special:{max_position}")
                success = self.image_translate(f"special:{max_position}")
            else:
                # 단일 명령어 처리
                success = self.image_translate(k_data)

            if success:
                logger.info("K열: 이미지 번역 완료")
            else:
                logger.warning("K열: 이미지 번역 실패")
            
            return success
            
        except Exception as e:
            logger.error(f"K열 데이터 처리 중 오류: {e}")
            return False
    
    def _execute_combined_translate_actions(self, actions):
        """
        복합 이미지 번역 액션들을 순차 처리 (각 액션을 개별적으로 실행)
        
        Args:
            actions: 파싱된 액션 정보 리스트
            
        Returns:
            bool: 성공 여부
        """
        try:
            success_count = 0
            total_actions = len(actions)
            
            for i, action_info in enumerate(actions):
                logger.info(f"복합 액션 {i+1}/{total_actions} 실행: {action_info}")
                action = action_info.get('action')
                
                # 각 액션을 개별적으로 처리
                action_success = False
                
                if action == 'first':
                    count = action_info.get('count', 1)
                    # first:n 형태로 처리
                    command = f"first:{count}"
                    logger.info(f"처음 {count}개 이미지 번역 실행: {command}")
                    action_success = self.image_translate(command)
                    
                elif action == 'last':
                    count = action_info.get('count', 1)
                    # last:n 형태로 처리
                    command = f"last:{count}"
                    logger.info(f"마지막 {count}개 이미지 번역 실행: {command}")
                    action_success = self.image_translate(command)
                    
                elif action == 'specific':
                    positions = action_info.get('positions', [])
                    # 위치들을 쉼표로 연결하여 처리
                    command = ','.join(str(pos) for pos in positions)
                    logger.info(f"특정 위치 이미지 번역 실행: {command}")
                    action_success = self.image_translate(command)
                    
                elif action == 'special':
                    max_position = action_info.get('max_position', 10)
                    # special:n 형태로 처리
                    command = f"special:{max_position}"
                    logger.info(f"제한된 스캔 이미지 번역 실행: {command}")
                    action_success = self.image_translate(command)
                    
                elif action == 'yes':
                    # 기본 동작: 모든 이미지 번역
                    command = "specific:all"
                    logger.info(f"모든 이미지 번역 실행: {command}")
                    action_success = self.image_translate(command)
                
                if action_success:
                    success_count += 1
                    logger.info(f"복합 액션 {i+1}/{total_actions} 성공")
                else:
                    logger.warning(f"복합 액션 {i+1}/{total_actions} 실패")
            
            # 전체 결과 평가
            if success_count > 0:
                logger.info(f"복합 이미지 번역 완료: {success_count}/{total_actions} 성공")
                return True
            else:
                logger.warning(f"복합 이미지 번역 실패: 모든 액션 실패 (0/{total_actions})")
                return False
                
        except Exception as e:
            logger.error(f"복합 이미지 번역 액션 처리 오류: {e}")
            return False
    
    def _execute_single_translate_action(self, action_info):
        """
        단일 이미지 번역 액션 실행 (복합 액션용) - 더 이상 사용하지 않음
        
        Args:
            action_info: 파싱된 단일 액션 정보
            
        Returns:
            bool: 성공 여부
        """
        try:
            action = action_info.get('action')
            
            if action == 'last':
                count = action_info.get('count', 1)
                # last:n을 specific:n 형식으로 변환하여 처리
                translate_command = f"last:{count}"
                logger.info(f"마지막 {count}개 이미지 번역 실행: {translate_command}")
                return self.image_translate(translate_command)
            
            elif action == 'first':
                count = action_info.get('count', 1)
                # first:n을 1,2,...,n 형식으로 변환하여 처리
                positions = ','.join(str(i) for i in range(1, count + 1))
                logger.info(f"처음 {count}개 이미지 번역 실행: {positions}")
                return self.image_translate(positions)
            
            elif action == 'specific':
                positions = action_info.get('positions', [])
                # specific 위치들을 쉼표로 연결하여 처리
                if 'all' in positions:
                    translate_command = "specific:all"
                else:
                    translate_command = ','.join(str(pos) for pos in positions)
                logger.info(f"특정 위치 이미지 번역 실행: {translate_command}")
                return self.image_translate(translate_command)
            
            elif action == 'yes':
                # 기본 동작: 모든 이미지 번역
                logger.info("기본 이미지 번역 (모든 이미지)")
                return self.image_translate("specific:all")
            
            else:
                logger.warning(f"지원되지 않는 액션: {action}")
                return False
                
        except Exception as e:
            logger.error(f"단일 번역 액션 실행 중 오류: {e}")
            return False
    
    def _translate_images_by_position(self, action_info):
        """
        위치 기반 이미지 번역
        
        Args:
            action_info: 파싱된 액션 정보
            
        Returns:
            bool: 성공 여부
        """
        try:
            action = action_info.get('action')
            
            if action == 'no':
                logger.info("이미지 번역 작업 건너뜀")
                return True
            
            # image_manager를 우선 사용하되, 실패 시 직접 구현 사용
            try:
                if action == 'last':
                    count = action_info.get('count', 1)
                    logger.info(f"마지막 {count}개 이미지 번역 시작")
                    return self.image_manager.translate_last_images(count)
                
                elif action == 'first':
                    count = action_info.get('count', 1)
                    logger.info(f"처음 {count}개 이미지 번역 시작")
                    return self.image_manager.translate_first_images(count)
                
                elif action == 'specific':
                    positions = action_info.get('positions', [])
                    logger.info(f"특정 위치 이미지 번역 시작: {positions}")
                    return self.image_manager.translate_images_by_positions(positions)
                
                elif action == 'yes':
                    # 기본 동작: 모든 이미지 번역
                    logger.info("기본 이미지 번역 (모든 이미지)")
                    return self.image_manager.translate_all_images()
                    
            except Exception as e:
                logger.warning(f"image_manager 이미지 번역 실패, 직접 구현으로 전환: {e}")
                return self._translate_images_direct(action_info)
            
            return True
            
        except Exception as e:
            logger.error(f"위치 기반 이미지 번역 중 오류: {e}")
            return False
    

    def _translate_images_direct(self, action_info):
        """
        직접 구현을 통한 이미지 번역 (image_manager 실패 시 백업)
        
        Args:
            action_info: 파싱된 액션 정보
            
        Returns:
            bool: 성공 여부
        """
        try:
            action = action_info.get('action')
            
            logger.info(f"직접 구현으로 이미지 번역 시작: {action}")
            
            # 페이지 로딩 대기 최적화
            time.sleep(0.1)
            
            # 이미지 요소들 찾기
            image_selectors = [
                ".product-image img",
                ".image-item img",
                ".gallery-item img",
                "img[src*='product']",
                ".image-list img"
            ]
            
            images = []
            for selector in image_selectors:
                images = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if images:
                    logger.info(f"이미지 발견: {selector} ({len(images)}개)")
                    break
            
            if not images:
                logger.warning("번역할 이미지가 없습니다")
                return False
            
            # 번역할 이미지 인덱스 결정
            translate_indices = []
            
            if action == 'last':
                count = action_info.get('count', 1)
                count = min(count, len(images))
                translate_indices = list(range(len(images) - count, len(images)))
            
            elif action == 'first':
                count = action_info.get('count', 1)
                count = min(count, len(images))
                translate_indices = list(range(count))
            
            elif action == 'specific':
                positions = action_info.get('positions', [])
                translate_indices = [pos - 1 for pos in positions if 1 <= pos <= len(images)]
            
            elif action == 'yes':
                # 모든 이미지
                translate_indices = list(range(len(images)))
            
            if not translate_indices:
                logger.warning("번역할 이미지 인덱스가 없습니다")
                return False
            
            logger.info(f"번역할 이미지 인덱스: {translate_indices}")
            
            translated_count = 0
            for index in translate_indices:
                try:
                    image = images[index]
                    
                    # 이미지 클릭하여 선택
                    self.driver.execute_script("arguments[0].click();", image)
                    time.sleep(0.2)
                    
                    # 번역 버튼 찾기
                    translate_btn_selectors = [
                        ".translate-btn",
                        "button[onclick*='translate']",
                        "[data-action='translate']",
                        ".btn-translate",
                        "button:contains('번역')"
                    ]
                    
                    translate_btn = None
                    for selector in translate_btn_selectors:
                        try:
                            translate_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                            if translate_btn.is_displayed():
                                break
                        except:
                            continue
                    
                    if translate_btn:
                        # 번역 버튼 클릭
                        self.driver.execute_script("arguments[0].click();", translate_btn)
                        time.sleep(1)  # 번역 처리 대기 최적화
                        
                        # 번역 완료 확인
                        try:
                            # 번역 완료 메시지나 상태 확인
                            success_indicators = [
                                ".translate-success",
                                ".success-message",
                                "[data-status='translated']"
                            ]
                            
                            for indicator in success_indicators:
                                if self.driver.find_elements(By.CSS_SELECTOR, indicator):
                                    break
                        except:
                            pass
                        
                        translated_count += 1
                        logger.info(f"이미지 {index + 1} 번역 완료")
                    else:
                        logger.warning(f"이미지 {index + 1}의 번역 버튼을 찾을 수 없음")
                    
                except Exception as e:
                    logger.warning(f"이미지 {index + 1} 번역 실패: {e}")
                    continue
            
            logger.info(f"직접 이미지 번역 작업 완료: {translated_count}/{len(translate_indices)}개 번역")
            return translated_count > 0
            
        except Exception as e:
            logger.error(f"직접 이미지 번역 중 오류: {e}")
            return False
    
    def _process_l_data(self, l_data):
        """
        L열 데이터 처리 (이미지 태그 삽입)
        
        Args:
            l_data: L열 데이터 (예: "YES", "NO")
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"L열 데이터 처리 (이미지 태그 삽입): {l_data}")
            
            # 명령어 파싱
            action_info = self._parse_action_command(l_data)
            
            if action_info['action'] == 'no':
                logger.info("L열: 이미지 태그 삽입 작업 없음")
                return True
            
            # 상세페이지 탭으로 이동 (이미지 태그는 상세페이지에 삽입)
            smart_click(self.driver, UI_ELEMENTS["PRODUCT_TAB_DETAIL"], DELAY_VERY_SHORT)
            time.sleep(DELAY_SHORT)
            
            # 이미지 태그 삽입 실행 (M열 데이터 사용)
            success = self._insert_image_tag_from_m_data()
            
            if success:
                logger.info("L열: 이미지 태그 삽입 완료")
            else:
                logger.warning("L열: 이미지 태그 삽입 실패")
            
            return success
            
        except Exception as e:
            logger.error(f"L열 데이터 처리 중 오류: {e}")
            return False
    
    def _insert_image_tag_from_m_data(self):
        """
        M열 데이터를 사용하여 이미지 태그 삽입
        
        Returns:
            bool: 성공 여부
        """
        try:
            # M열 데이터는 process_product_modifications에서 전달받아야 함
            # 현재는 기본 이미지 태그 삽입 로직만 구현
            logger.info("이미지 태그 삽입 시작")
            
            # HTML 편집기 찾기 및 태그 삽입
            html_editor_selectors = [
                "//div[contains(@class, 'ql-editor')]",  # Quill 에디터
                "//div[contains(@class, 'DraftEditor-root')]",  # Draft.js 에디터
                "//iframe[contains(@title, 'editor')]",  # iframe 에디터
                "//div[contains(@contenteditable, 'true')]",  # contenteditable div
                "//textarea[contains(@class, 'editor')]"
            ]
            
            for editor_selector in html_editor_selectors:
                try:
                    if "iframe" in editor_selector:
                        # iframe 에디터의 경우
                        iframe = self.driver.find_element(By.XPATH, editor_selector)
                        self.driver.switch_to.frame(iframe)
                        editor = self.driver.find_element(By.TAG_NAME, "body")
                    else:
                        editor = self.driver.find_element(By.XPATH, editor_selector)
                    
                    if editor.is_displayed():
                        editor.click()
                        time.sleep(DELAY_VERY_SHORT)
                        
                        # 기본 이미지 태그 삽입
                        default_img_tag = '<img src="" alt="상품이미지" />'
                        self.driver.execute_script("arguments[0].innerHTML += arguments[1];", editor, default_img_tag)
                        
                        if "iframe" in editor_selector:
                            self.driver.switch_to.default_content()
                        
                        logger.info("HTML 에디터에 이미지 태그 삽입 완료")
                        return True
                        
                except Exception as e:
                    logger.debug(f"HTML 에디터 {editor_selector} 사용 실패: {e}")
                    if "iframe" in editor_selector:
                        try:
                            self.driver.switch_to.default_content()
                        except:
                            pass
                    continue
            
            logger.warning("이미지 태그 삽입 방법을 찾을 수 없습니다")
            return False
            
        except Exception as e:
            logger.error(f"이미지 태그 삽입 중 오류: {e}")
            return False
    
    def _process_m_data(self, m_data):
        """
        M열 데이터 처리 (HTML 업데이트)
        
        Args:
            m_data: M열 데이터 (HTML 내용)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"M열 데이터 처리 (HTML 업데이트): {m_data}")
            
            # M열 데이터가 없으면 작업 없음
            if not m_data or pd.isna(m_data) or str(m_data).strip() == '':
                logger.info("M열: HTML 업데이트 작업 없음")
                return True
            
            # 상세페이지 탭 선택
            smart_click(self.driver, UI_ELEMENTS["PRODUCT_TAB_DETAIL"], DELAY_VERY_SHORT)
            time.sleep(DELAY_SHORT)
            
            # 소스 버튼 클릭(버튼 눌러서 입력상태 만들기)
            smart_click(self.driver, UI_ELEMENTS["PRODUCT_SOURCE_BUTTON"], DELAY_VERY_SHORT)
            time.sleep(DELAY_SHORT)
            
            # M열에서 가져온 값 붙여넣기 (멀티브라우저 간섭 방지를 위해 Selenium 사용)
            # 소스 편집 상태에서 커서가 맨 앞에 위치하므로 바로 붙여넣기
            self.driver.switch_to.active_element.send_keys(str(m_data))
            time.sleep(DELAY_SHORT)

            
            # 소스 버튼 클릭(다시 버튼 눌러서 저장하기기)
            smart_click(self.driver, UI_ELEMENTS["PRODUCT_SOURCE_BUTTON"], DELAY_VERY_SHORT)
            time.sleep(DELAY_SHORT)
            
            logger.info("M열: HTML 업데이트 완료")
            return True
            
        except Exception as e:
            logger.error(f"M열 데이터 처리 중 오류: {e}")
            return False
    
    def _process_n_data(self, n_data):
        """
        N열 데이터 처리 (썸네일 번역)
        
        Args:
            n_data: N열 데이터 (썸네일 번역 명령어)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"N열 데이터 처리 (썸네일 번역): {n_data}")
            
            # 명령어 파싱
            action_info = self._parse_action_command(n_data)
            
            if action_info['action'] == 'no':
                logger.info("N열: 썸네일 번역 작업 없음")
                return True
            
            # 썸네일 탭으로 이동 전 모달창 상태 안정화
            logger.info("N열: 썸네일 탭 클릭 전 모달창 상태 확인")
            time.sleep(DELAY_SHORT)  # 모달창 안정화 대기
            
            # 모달창이 완전히 로드되었는지 확인
            try:
                modal_elements = self.driver.find_elements(By.CSS_SELECTOR, ".ant-modal, .ant-drawer")
                visible_modals = [modal for modal in modal_elements if modal.is_displayed()]
                
                if visible_modals:
                    logger.info("N열: 모달창 확인됨 - 썸네일 탭 클릭 진행")
                else:
                    logger.warning("N열: 모달창이 감지되지 않음 - 탭 클릭 시도")
            except Exception as modal_check_error:
                logger.warning(f"N열: 모달창 상태 확인 중 오류: {modal_check_error}")
            
            # 썸네일 탭으로 이동 (N열은 썸네일 번역 작업)
            tab_key = self.COLUMN_TAB_MAPPING.get('N', 'PRODUCT_TAB_THUMBNAIL')
            logger.info(f"N열: 썸네일 탭 클릭 시도 - {tab_key}")
            
            try:
                smart_click(self.driver, UI_ELEMENTS[tab_key], DELAY_VERY_SHORT)
                time.sleep(DELAY_SHORT)
                logger.info("N열: 썸네일 탭 클릭 성공")
            except Exception as tab_click_error:
                logger.error(f"N열: 썸네일 탭 클릭 실패: {tab_click_error}")
                # 탭 클릭 실패 시 재시도
                try:
                    logger.info("N열: 썸네일 탭 클릭 재시도")
                    time.sleep(DELAY_SHORT)
                    smart_click(self.driver, UI_ELEMENTS[tab_key], DELAY_VERY_SHORT)
                    time.sleep(DELAY_SHORT)
                    logger.info("N열: 썸네일 탭 클릭 재시도 성공")
                except Exception as retry_error:
                    logger.error(f"N열: 썸네일 탭 클릭 재시도 실패: {retry_error}")
                    return False
            
            # 복합 명령어 처리
            if action_info['action'] == 'combined':
                # 복합 명령어 처리 (예: first:1/last:1)
                actions = action_info.get('actions', [])
                logger.info(f"복합 썸네일 번역 시작: {len(actions)}개 액션")
                
                # 복합 액션은 통합 처리 방식 사용 (모달창 한 번만 열기)
                success = self._execute_combined_translate_actions(actions)
            else:
                # 단일 명령어 처리 - N열 썸네일 이미지 번역 메서드 사용
                success = self.thumbnailimage_translate(n_data)

            if success:
                logger.info("N열: 썸네일 번역 완료")
            else:
                logger.warning("N열: 썸네일 번역 실패")
            
            return success
            
        except Exception as e:
            logger.error(f"N열 데이터 처리 중 오류: {e}")
            return False
    
    def _process_o_data(self, o_data):
        """
        O열 데이터 처리 (옵션 이미지 번역)
        
        Args:
            o_data: O열 데이터 (옵션 이미지 번역 명령어)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"O열 데이터 처리 (옵션 이미지 번역): {o_data}")
            
            # 명령어 파싱
            action_info = self._parse_action_command(o_data)
            
            if action_info['action'] == 'no':
                logger.info("O열: 옵션 이미지 번역 작업 없음")
                return True
            
            # 옵션 탭으로 이동 전 모달창 상태 안정화
            logger.info("O열: 옵션 탭 클릭 전 모달창 상태 확인")
            time.sleep(DELAY_SHORT)  # 모달창 안정화 대기
            
            # 모달창이 완전히 로드되었는지 확인
            try:
                modal_elements = self.driver.find_elements(By.CSS_SELECTOR, ".ant-modal, .ant-drawer")
                visible_modals = [modal for modal in modal_elements if modal.is_displayed()]
                
                if visible_modals:
                    logger.info("O열: 모달창 확인됨 - 옵션 탭 클릭 진행")
                else:
                    logger.warning("O열: 모달창이 감지되지 않음 - 탭 클릭 시도")
            except Exception as modal_check_error:
                logger.warning(f"O열: 모달창 상태 확인 중 오류: {modal_check_error}")
            
            # 옵션 탭으로 이동 (O열은 옵션 이미지 번역 작업)
            tab_key = self.COLUMN_TAB_MAPPING.get('O', 'PRODUCT_TAB_OPTION')
            logger.info(f"O열: 옵션 탭 클릭 시도 - {tab_key}")
            
            try:
                smart_click(self.driver, UI_ELEMENTS[tab_key], DELAY_VERY_SHORT)
                time.sleep(DELAY_SHORT)
                logger.info("O열: 옵션 탭 클릭 성공")
            except Exception as tab_click_error:
                logger.error(f"O열: 옵션 탭 클릭 실패: {tab_click_error}")
                # 탭 클릭 실패 시 재시도
                try:
                    logger.info("O열: 옵션 탭 클릭 재시도")
                    time.sleep(DELAY_SHORT)
                    smart_click(self.driver, UI_ELEMENTS[tab_key], DELAY_VERY_SHORT)
                    time.sleep(DELAY_SHORT)
                    logger.info("O열: 옵션 탭 클릭 재시도 성공")
                except Exception as retry_error:
                    logger.error(f"O열: 옵션 탭 클릭 재시도 실패: {retry_error}")
                    return False
            
            # 복합 명령어 처리
            if action_info['action'] == 'combined':
                # 복합 명령어 처리 (예: first:1/last:1)
                actions = action_info.get('actions', [])
                logger.info(f"복합 옵션 이미지 번역 시작: {len(actions)}개 액션")
                
                # 복합 액션은 통합 처리 방식 사용 (모달창 한 번만 열기)
                success = self._execute_combined_translate_actions(actions)
            else:
                # 단일 명령어 처리 - optionimage_translate 메서드 사용
                success = self.optionimage_translate(o_data)

            if success:
                logger.info("O열: 옵션 이미지 번역 완료")
            else:
                logger.warning("O열: 옵션 이미지 번역 실패")
            
            return success
            
        except Exception as e:
            logger.error(f"O열 데이터 처리 중 오류: {e}")
            return False
    
    def close_modal(self):
        """
        수정 모달창 닫기 (재시도 로직 포함)
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("수정 모달창 닫기 시작")
            
            max_attempts = 3
            for attempt in range(max_attempts):
                # ESC 키로 닫기 시도
                logger.info(f"ESC 키로 모달창 닫기 시도 ({attempt + 1}/{max_attempts})")
                ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
                time.sleep(DELAY_MEDIUM)
                
                # 모달창 닫힘 확인
                if self._check_modal_closed(max_wait=3):
                    logger.info(f"ESC 키로 모달창 닫기 성공 (시도 {attempt + 1}/{max_attempts})")
                    return True
                else:
                    logger.warning(f"모달창이 아직 열려있음 (시도 {attempt + 1}/{max_attempts})")
                    
                    # 마지막 시도가 아니면 추가 대기
                    if attempt < max_attempts - 1:
                        time.sleep(DELAY_SHORT)
            
            # 모든 ESC 시도 실패 시 닫기 버튼 클릭 시도
            logger.warning("ESC 키로 모달창 닫기 실패, 닫기 버튼 클릭 시도")
            try:
                close_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".ant-modal-close, .ant-drawer-close")
                for close_btn in close_buttons:
                    if close_btn.is_displayed():
                        close_btn.click()
                        time.sleep(DELAY_SHORT)
                        if self._check_modal_closed(max_wait=2):
                            logger.info("닫기 버튼 클릭으로 모달창 닫기 성공")
                            return True
            except Exception as btn_error:
                logger.debug(f"닫기 버튼 클릭 시도 중 오류: {btn_error}")
            
            logger.error("모든 방법으로 모달창 닫기 실패")
            return False
            
        except Exception as e:
            logger.error(f"모달창 닫기 중 오류: {e}")
            return False
    
    def _check_modal_closed(self, max_wait=5):
        """
        모달창이 닫혔는지 확인
        
        Args:
            max_wait: 최대 대기 시간(초)
            
        Returns:
            bool: 모달창 닫힘 여부
        """
        start_time = time.time()
        while time.time() - start_time < max_wait:
            try:
                modal_elements = self.driver.find_elements(By.XPATH, "//div[@role='dialog' and contains(@style, 'display: none')] | //div[contains(@class, 'ant-modal') and not(contains(@style, 'display: block'))]")
                visible_modals = self.driver.find_elements(By.XPATH, "//div[@role='dialog' and not(contains(@style, 'display: none'))] | //div[contains(@class, 'ant-modal') and contains(@style, 'display: block')]")
                
                if not visible_modals:
                    return True
                    
            except Exception as e:
                logger.debug(f"모달 닫힘 확인 중 오류: {e}")
            
            time.sleep(0.1)
        
        return False
    
    def move_product_to_target_group(self, target_group):
        """
        상품을 target_group으로 이동
        
        Args:
            target_group: 이동할 그룹명
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"상품을 '{target_group}' 그룹으로 이동 시작")
            
            # 드라이버 연결 상태 검증
            try:
                self.driver.current_url
                logger.debug(f"상품 그룹 이동 전 드라이버 연결 상태 정상")
            except Exception as conn_e:
                logger.error(f"상품 그룹 이동 전 드라이버 연결 오류: {conn_e}")
                raise Exception(f"드라이버 연결 실패로 상품 그룹 이동 불가: {conn_e}")
            
            # 3단계 개별 상품 그룹 이동 드롭다운 관리자 가져오기 (싱글톤 패턴)
            from dropdown_utils import get_dropdown_manager
            dropdown_manager3 = get_dropdown_manager(self.driver)
            
            # 1차 시도: 기본 방식
            success = dropdown_manager3.select_product_group_by_name(target_group, item_index=0)
            
            if success:
                logger.info(f"기본 방식으로 '{target_group}' 그룹 이동 성공")
            else:
                logger.warning(f"기본 방식 실패, 그룹지정 모달 방식 시도")
                
                # 2차 시도: 그룹지정 모달 방식 (1단계 코어와 동일)
                try:
                    # 1. 첫번째 상품의 체크박스 선택
                    if dropdown_manager3.select_first_product():
                        logger.info("첫번째 상품 체크박스 선택 성공")
                        
                        # 2. 그룹지정 모달 열기
                        if dropdown_manager3.open_group_assignment_modal():
                            logger.info("그룹지정 모달 열기 성공")
                            
                            # 3. 모달에서 대상 그룹 선택
                            if dropdown_manager3.select_group_in_modal(target_group):
                                logger.info(f"모달에서 '{target_group}' 그룹 선택 성공")
                                success = True
                            else:
                                logger.error(f"모달에서 '{target_group}' 그룹 선택 실패")
                        else:
                            logger.error("그룹지정 모달 열기 실패")
                    else:
                        logger.error("첫번째 상품 체크박스 선택 실패")
                        
                except Exception as modal_error:
                    logger.error(f"그룹지정 모달 방식 중 오류 발생: {modal_error}")
            
            if success:
                logger.info(f"상품을 '{target_group}' 그룹으로 이동 성공")
                # 그룹 이동 후 화면 최상단으로 이동
                logger.info("그룹 이동 후 화면 최상단으로 이동")
                self.driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(DELAY_SHORT)  # 코어1과 동일한 지연시간 적용
                return True
            else:
                logger.error(f"상품을 '{target_group}' 그룹으로 이동 실패")
                return False
                
        except Exception as e:
            logger.error(f"상품 그룹 이동 중 오류: {e}")
            return False
    
    def process_keyword_with_individual_modifications(self, keyword, target_group, task_data, max_products=20, step3_image_limit=None):
        """
        키워드로 검색된 모든 상품을 개별적으로 수정 후 target_group으로 이동
        
        Args:
            keyword: 검색 키워드
            target_group: 이동할 그룹명
            task_data: H~L열 수정 데이터
            max_products: 최대 처리할 상품 수 (기본값: 20)
            step3_image_limit: 이미지 번역 수량 제한 (None이면 기본값 사용)
            
        Returns:
            tuple: (성공 여부, 처리된 상품 수)
        """
        try:
            # max_products가 None이면 self.step3_product_limit 사용
            if max_products is None:
                max_products = self.step3_product_limit or 20
            
            # step3_image_limit 파라미터 처리 (None이 아닐 때만 변경)
            original_limit = None
            if step3_image_limit is not None and step3_image_limit != self.step3_image_limit:
                original_limit = self.step3_image_limit
                self.step3_image_limit = step3_image_limit
                logger.info(f"이미지 번역 수량 제한을 {original_limit}에서 {step3_image_limit}로 임시 변경")
            
            logger.info(f"키워드 '{keyword}' 상품들의 개별 수정 및 이동 시작 (상품 제한: {max_products}개, 이미지 제한: {self.step3_image_limit}개)")
            
            # 드라이버 연결 상태 검증
            try:
                self.driver.current_url
                logger.info("드라이버 연결 상태 정상 확인")
            except Exception as e:
                logger.error(f"드라이버 연결 오류 감지: {e}")
                raise Exception(f"드라이버 연결 실패: {e}")
            
            total_processed = 0
            
            # 키워드로 상품 검색 (상품 수 제한)
            product_count = self.search_products_by_keyword(keyword, max_products=max_products)
            
            if product_count == 0:
                logger.info(f"키워드 '{keyword}'로 검색된 상품이 없습니다. 작업 완료.")
                return True, 0
            
            # 실제 처리할 상품 수를 max_products로 제한
            actual_products_to_process = min(product_count, max_products)
            logger.info(f"현재 페이지에 {product_count}개 상품 발견, 실제 처리할 상품: {actual_products_to_process}개 (최대 {max_products}개로 제한됨)")
            
            # 현재 페이지의 제한된 상품만 처리
            for i in range(actual_products_to_process):  # 제한된 상품 수만큼 처리
                    logger.info(f"상품 {i+1}/{actual_products_to_process} 처리 중")
                    
                    # 두 번째 상품부터는 화면 최상단으로 이동
                    if i > 0:
                        logger.info(f"상품 {i+1} 처리 전 화면 최상단으로 이동")
                        self.driver.execute_script("window.scrollTo(0, 0);")
                        time.sleep(DELAY_SHORT)
                    
                    # 첫 번째 상품 모달창 열기
                    if not self.open_first_product_modal():
                        logger.error(f"상품 {i+1} 모달창 열기 실패")
                        continue
                    
                    # 상품별 번역 이미지 수 초기화
                    self.reset_current_product_translation_count()
                    
                    # H~L열 수정 작업 수행
                    if not self.process_product_modifications(task_data):
                        logger.warning(f"상품 {i+1} 수정 작업 실패")
                    else:
                        # 상품 수정 완료 후 번역 이미지 수 로그
                        product_translated = self.get_current_product_translation_count()
                        if product_translated > 0:
                            logger.info(f"상품 {i+1} 수정 완료 - 이번 상품에서 번역된 이미지: {product_translated}개")
                    
                    # 상품을 target_group으로 이동
                    if not self.move_product_to_target_group(target_group):
                        logger.error(f"상품 {i+1} 그룹 이동 실패")
                    
                    total_processed += 1
                    
                    # 이미지 번역 수 제한 확인
                    if self.is_translation_limit_reached():
                        logger.warning(f"이미지 번역 수 제한 달성! 총 {self.get_total_translation_count()}/{self.step3_image_limit}개 번역 완료")
                        logger.info(f"키워드 '{keyword}' 처리 중단 - 이미지 번역 제한 달성으로 인한 조기 종료")
                        break
                    
                    # 작업 간 대기
                    time.sleep(DELAY_SHORT)
            
            # 키워드 처리 완료 로그
            total_translated = self.get_total_translation_count()
            logger.info(f"키워드 '{keyword}' 총 {total_processed}개 상품 처리 완료 - 총 번역 이미지: {total_translated}/{self.step3_image_limit}개")
            
            # step3_image_limit 원래 값으로 복원
            if original_limit is not None:
                self.step3_image_limit = original_limit
                logger.info(f"이미지 번역 수량 제한을 원래 값 {original_limit}로 복원")
            
            return True, total_processed
            
        except Exception as e:
            logger.error(f"키워드 '{keyword}' 처리 중 오류: {e}")
            
            # 예외 발생 시에도 step3_image_limit 원래 값으로 복원
            if original_limit is not None:
                self.step3_image_limit = original_limit
                logger.info(f"예외 발생으로 인한 이미지 번역 수량 제한 복원: {original_limit}")
            
            return False, 0
    
    def image_translate(self, action_value):
        """
        K열, N열, O열 이미지 번역 액션을 처리하는 메서드
        
        Args:
            action_value (str): 액션 값 (예: "first:1", "first:2", "specific:2", "specific:2,3")
            
        Returns:
            bool: 성공 여부
        """
        # 이미지 번역 수 제한 확인
        # 배치 제한 관리자가 있으면 해당 제한을 사용, 없으면 기존 제한 사용
        if hasattr(self, 'batch_limit_manager') and self.batch_limit_manager:
            image_limit = self.batch_limit_manager.image_limit
        else:
            image_limit = self.step3_image_limit
            
        if self.total_translated_images >= image_limit:
            logger.warning(f"이미지 번역 수 제한 달성 ({self.total_translated_images}/{image_limit}). 번역을 건너뜁니다.")
            return True  # 제한 달성 시 성공으로 처리하여 작업 계속 진행
        
        # 번역 전 개수 기록
        before_count = self.total_translated_images
        
        # 실제 번역 수행 - 실제 번역된 개수 반환
        translated_count = self.image_translation_handler.image_translate(action_value, 'detail')
        
        if translated_count > 0:
            # 실제 번역된 이미지 수 사용
            self.total_translated_images += translated_count
            self.current_product_translated_images += translated_count
            # 배치 제한 관리자가 있으면 해당 값을 업데이트하고 사용
            if hasattr(self, 'batch_limit_manager') and self.batch_limit_manager:
                self.batch_limit_manager.add_translated_images(translated_count)
                current_chunk_images = self.batch_limit_manager.get_current_chunk_images_translated()
                logger.info(f"상세 이미지 번역 완료: +{translated_count}개 (총 {current_chunk_images}/{self.step3_image_limit})")
            else:
                logger.info(f"상세 이미지 번역 완료: +{translated_count}개 (총 {self.total_translated_images}/{self.step3_image_limit})")
            return True
        else:
            # 배치 제한 관리자가 있으면 해당 값을 사용, 없으면 기존 방식 사용
            if hasattr(self, 'batch_limit_manager') and self.batch_limit_manager:
                current_chunk_images = self.batch_limit_manager.get_current_chunk_images_translated()
                logger.info(f"상세 이미지 번역 대상 없음: +0개 (총 {current_chunk_images}/{self.step3_image_limit})")
            else:
                logger.info(f"상세 이미지 번역 대상 없음: +0개 (총 {self.total_translated_images}/{self.step3_image_limit})")
            return True  # 번역할 이미지가 없는 것은 실패가 아니므로 True 반환
        
    def thumbnailimage_translate(self, action_value):
        """
        N열 썸네일 이미지 번역 액션을 처리하는 메서드
        
        Args:
            action_value (str): 액션 값
            
        Returns:
            bool: 성공 여부
        """
        # 이미지 번역 수 제한 확인
        # 배치 제한 관리자가 있으면 해당 제한을 사용, 없으면 기존 제한 사용
        if hasattr(self, 'batch_limit_manager') and self.batch_limit_manager:
            image_limit = self.batch_limit_manager.image_limit
        else:
            image_limit = self.step3_image_limit
            
        if self.total_translated_images >= image_limit:
            logger.warning(f"이미지 번역 수 제한 달성 ({self.total_translated_images}/{image_limit}). 번역을 건너뜁니다.")
            return True  # 제한 달성 시 성공으로 처리하여 작업 계속 진행
        
        # 번역 전 개수 기록
        before_count = self.total_translated_images
        
        # 실제 번역 수행 - 실제 번역된 개수 반환
        translated_count = self.image_translation_handler.image_translate(action_value, 'thumbnail')
        
        if translated_count > 0:
            # 실제 번역된 이미지 수 사용
            self.total_translated_images += translated_count
            self.current_product_translated_images += translated_count
            # 배치 제한 관리자가 있으면 해당 값을 업데이트하고 사용
            if hasattr(self, 'batch_limit_manager') and self.batch_limit_manager:
                self.batch_limit_manager.add_translated_images(translated_count)
                current_chunk_images = self.batch_limit_manager.get_current_chunk_images_translated()
                logger.info(f"썸네일 이미지 번역 완료: +{translated_count}개 (총 {current_chunk_images}/{self.step3_image_limit})")
            else:
                logger.info(f"썸네일 이미지 번역 완료: +{translated_count}개 (총 {self.total_translated_images}/{self.step3_image_limit})")
            return True
        else:
            # 배치 제한 관리자가 있으면 해당 값을 사용, 없으면 기존 방식 사용
            if hasattr(self, 'batch_limit_manager') and self.batch_limit_manager:
                current_chunk_images = self.batch_limit_manager.get_current_chunk_images_translated()
                logger.info(f"썸네일 이미지 번역 대상 없음: +0개 (총 {current_chunk_images}/{self.step3_image_limit})")
            else:
                logger.info(f"썸네일 이미지 번역 대상 없음: +0개 (총 {self.total_translated_images}/{self.step3_image_limit})")
            return True  # 번역할 이미지가 없는 것은 실패가 아니므로 True 반환
        
    def optionimage_translate(self, action_value):
        """
        O열 옵션 이미지 번역 액션을 처리하는 메서드
        
        Args:
            action_value (str): 액션 값
            
        Returns:
            bool: 성공 여부
        """
        # 이미지 번역 수 제한 확인
        # 배치 제한 관리자가 있으면 해당 제한을 사용, 없으면 기존 제한 사용
        if hasattr(self, 'batch_limit_manager') and self.batch_limit_manager:
            image_limit = self.batch_limit_manager.image_limit
        else:
            image_limit = self.step3_image_limit
            
        if self.total_translated_images >= image_limit:
            logger.warning(f"이미지 번역 수 제한 달성 ({self.total_translated_images}/{image_limit}). 번역을 건너뜁니다.")
            return True  # 제한 달성 시 성공으로 처리하여 작업 계속 진행
        
        # 번역 전 개수 기록
        before_count = self.total_translated_images
        
        # 실제 번역 수행 - 실제 번역된 개수 반환
        translated_count = self.image_translation_handler.image_translate(action_value, 'option')
        
        if translated_count > 0:
            # 실제 번역된 이미지 수 사용
            self.total_translated_images += translated_count
            self.current_product_translated_images += translated_count
            # 배치 제한 관리자가 있으면 해당 값을 업데이트하고 사용
            if hasattr(self, 'batch_limit_manager') and self.batch_limit_manager:
                self.batch_limit_manager.add_translated_images(translated_count)
                current_chunk_images = self.batch_limit_manager.get_current_chunk_images_translated()
                logger.info(f"옵션 이미지 번역 완료: +{translated_count}개 (총 {current_chunk_images}/{self.step3_image_limit})")
            else:
                logger.info(f"옵션 이미지 번역 완료: +{translated_count}개 (총 {self.total_translated_images}/{self.step3_image_limit})")
            return True
        else:
            # 배치 제한 관리자가 있으면 해당 값을 사용, 없으면 기존 방식 사용
            if hasattr(self, 'batch_limit_manager') and self.batch_limit_manager:
                current_chunk_images = self.batch_limit_manager.get_current_chunk_images_translated()
                logger.info(f"옵션 이미지 번역 대상 없음: +0개 (총 {current_chunk_images}/{self.step3_image_limit})")
            else:
                logger.info(f"옵션 이미지 번역 대상 없음: +0개 (총 {self.total_translated_images}/{self.step3_image_limit})")
            return True  # 번역할 이미지가 없는 것은 실패가 아니므로 True 반환
    
    def _estimate_translated_count(self, action_value):
        """
        액션 값을 파싱하여 번역될 이미지 수를 추정
        
        Args:
            action_value (str): 액션 값 (예: "first:1", "first:2", "specific:2", "specific:2,3")
            
        Returns:
            int: 추정 번역 이미지 수
        """
        try:
            if not action_value or action_value.strip() == "":
                return 0
            
            # "first:N" 형태 처리
            if action_value.startswith("first:"):
                count_str = action_value.split(":")[1]
                return int(count_str)
            
            # "specific:N" 또는 "specific:N,M,L" 형태 처리
            elif action_value.startswith("specific:"):
                positions_str = action_value.split(":")[1]
                positions = positions_str.split(",")
                return len(positions)
            
            # "all" 형태 처리 (기본값 5개로 추정)
            elif action_value == "all":
                return 5
            
            # 숫자만 있는 경우
            elif action_value.isdigit():
                return int(action_value)
            
            # 기타 경우 기본값 1개
            else:
                return 1
                
        except Exception as e:
            logger.warning(f"번역 이미지 수 추정 실패 ({action_value}): {e}. 기본값 1개로 설정")
            return 1
    
    def reset_current_product_translation_count(self):
        """
        현재 상품의 번역 이미지 수 초기화
        """
        self.current_product_translated_images = 0
        logger.debug("현재 상품 번역 이미지 수 초기화")
    
    def get_current_product_translation_count(self):
        """
        현재 상품에서 번역된 이미지 수 반환
        
        Returns:
            int: 현재 상품 번역 이미지 수
        """
        return self.current_product_translated_images
    
    def get_total_translation_count(self):
        """
        총 번역된 이미지 수 반환
        
        Returns:
            int: 총 번역 이미지 수
        """
        return self.total_translated_images
    
    def is_translation_limit_reached(self):
        """
        이미지 번역 수 제한 달성 여부 확인
        
        Returns:
            bool: 제한 달성 여부
        """
        return self.total_translated_images >= self.step3_image_limit
    
    def update_driver_references(self, new_driver):
        """
        브라우저 재시작 후 드라이버 참조 업데이트
        
        Args:
            new_driver: 새로운 WebDriver 인스턴스
        """
        try:
            logger.info("ProductEditorCore3 드라이버 참조 업데이트 시작")
            
            # 새 드라이버 연결 상태 검증
            try:
                new_driver.current_url
                logger.info("새 드라이버 연결 상태 정상 확인")
            except Exception as e:
                logger.error(f"새 드라이버 연결 상태 오류: {e}")
                raise
            
            # 메인 드라이버 참조 업데이트
            old_driver = self.driver
            self.driver = new_driver
            logger.info("메인 드라이버 참조 업데이트 완료")
            
            # 내부 객체들의 드라이버 참조 업데이트
            if hasattr(self, 'keyboard') and self.keyboard:
                self.keyboard.driver = new_driver
                # KeyboardShortcuts 내부 객체도 업데이트
                if hasattr(self.keyboard, 'action_chains'):
                    self.keyboard.action_chains = ActionChains(new_driver)
                logger.info("KeyboardShortcuts 드라이버 참조 업데이트")
            
            if hasattr(self, 'image_manager') and self.image_manager:
                self.image_manager.driver = new_driver
                # PercentyImageManager3 내부 객체도 업데이트
                if hasattr(self.image_manager, 'wait'):
                    self.image_manager.wait = WebDriverWait(new_driver, 10)
                logger.info("PercentyImageManager3 드라이버 참조 업데이트")
            
            if hasattr(self, 'image_translation_handler') and self.image_translation_handler:
                self.image_translation_handler.driver = new_driver
                # ImageTranslationManager 내부 객체도 업데이트
                if hasattr(self.image_translation_handler, 'wait'):
                    self.image_translation_handler.wait = WebDriverWait(new_driver, 10)
                logger.info("ImageTranslationManager 드라이버 참조 업데이트")
            
            # 드라이버 참조 업데이트 후 연결 상태 재검증
            try:
                self.driver.current_url
                logger.info("업데이트된 드라이버 연결 상태 정상 확인")
            except Exception as e:
                logger.error(f"업데이트된 드라이버 연결 상태 오류: {e}")
                raise
            
            logger.info("ProductEditorCore3 드라이버 참조 업데이트 완료")
            
        except Exception as e:
            logger.error(f"ProductEditorCore3 드라이버 참조 업데이트 중 오류: {e}")
            raise
    
    def verify_driver_connection(self, raise_on_error=True):
        """
        드라이버 연결 상태 검증
        
        Args:
            raise_on_error: 오류 시 예외 발생 여부
            
        Returns:
            bool: 연결 상태 (정상: True, 오류: False)
        """
        try:
            # 드라이버 연결 상태 확인
            current_url = self.driver.current_url
            logger.debug(f"드라이버 연결 상태 정상 - 현재 URL: {current_url}")
            return True
        except Exception as e:
            logger.error(f"드라이버 연결 상태 오류: {e}")
            if raise_on_error:
                raise Exception(f"드라이버 연결 실패: {e}")
            return False
    
    def safe_driver_operation(self, operation_func, *args, **kwargs):
        """
        드라이버 연결 상태를 검증한 후 안전하게 작업 수행
        
        Args:
            operation_func: 실행할 함수
            *args: 함수 인자
            **kwargs: 함수 키워드 인자
            
        Returns:
            작업 결과 또는 None (실패 시)
        """
        try:
            # 드라이버 연결 상태 검증
            self.verify_driver_connection(raise_on_error=True)
            
            # 작업 수행
            return operation_func(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"안전한 드라이버 작업 실행 중 오류: {e}")
            raise
    
    def process_keyword_with_batch_limits(self, keyword, target_group, task_data, max_products=20, max_images=2000, batch_limit_manager=None):
        """
        배치 제한을 고려한 키워드 처리 (새로운 메서드)
        
        Args:
            keyword: 처리할 키워드
            target_group: 타겟 그룹
            task_data: 작업 데이터 딕셔너리
            max_products: 최대 상품 수
            max_images: 최대 이미지 번역 수
            batch_limit_manager: 배치 제한 관리자
            
        Returns:
            Tuple[bool, int]: (성공 여부, 처리된 상품 수)
        """
        try:
            logger.info(f"배치 제한 인식 키워드 처리 시작: '{keyword}' (최대 상품: {max_products}개, 최대 이미지: {max_images}개)")
            
            # 배치 제한 관리자가 있으면 설정하고 현재 번역 수 동기화
            self.batch_limit_manager = batch_limit_manager
            if batch_limit_manager:
                batch_limit_manager.total_images_translated = self.total_translated_images
                logger.info(f"배치 제한 관리자 초기화: 기존 번역 이미지 수 {self.total_translated_images}개 동기화")
            
            # 기존 제한값 백업 및 새 제한값 설정
            original_product_limit = self.step3_product_limit
            original_image_limit = self.step3_image_limit
            
            self.step3_product_limit = max_products
            self.step3_image_limit = max_images
            
            try:
                # 기존 메서드 호출
                success, processed_count = self.process_keyword_with_individual_modifications(
                    keyword=keyword,
                    target_group=target_group,
                    task_data=task_data,
                    max_products=max_products,
                    step3_image_limit=max_images
                )
                
                # 배치 제한 관리자에 결과 반영
                if batch_limit_manager and success:
                    batch_limit_manager.add_processed_products(processed_count)
                    batch_limit_manager.total_images_translated = self.total_translated_images
                    
                    logger.info(f"배치 제한 관리자 업데이트: 상품 +{processed_count}개, 이미지 총 {self.total_translated_images}개")
                
                return success, processed_count
                
            finally:
                # 원래 제한값 복원
                self.step3_product_limit = original_product_limit
                self.step3_image_limit = original_image_limit
                
        except Exception as e:
            logger.error(f"배치 제한 인식 키워드 처리 중 오류: {e}")
            return False, 0