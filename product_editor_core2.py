# -*- coding: utf-8 -*-
"""
상품 수정의 핵심 로직 2단계용 (product_editor_core2.py)
등록상품관리 화면에서의 상품명 입력창 선택 등의 기능을 담당하는 클래스
"""

import time
import logging
import pandas as pd
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# UI 요소 임포트
from ui_elements import UI_ELEMENTS

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
# coordinate_converter 모듈이 존재하지 않으므로 제거
# from coordinate_converter import convert_to_absolute_coordinates
from dropdown_utils2 import get_product_search_dropdown_manager

# 로깅 설정
logger = logging.getLogger(__name__)

class ProductEditorCore2:
    """
    상품 수정의 핵심 로직 2단계를 담당하는 클래스
    
    이 클래스는 다음 작업을 수행합니다:
    - 등록상품관리 화면에서 상품명 입력창 선택
    - 기타 2단계 관련 상품 편집 작업
    """
    
    def __init__(self, driver, config=None):
        """
        상품 편집 코어 2단계 초기화
        
        Args:
            driver: Selenium WebDriver 인스턴스
            config: 설정 정보 딕셔너리 (선택사항)
        """
        self.driver = driver
        self.config = config or {}
        
        logger.info("ProductEditorCore2 초기화 완료")
    
    def select_product_name_input(self):
        """
        등록상품관리 화면에서 상품명 입력창을 선택합니다.
        
        Returns:
            bool: 성공 여부
        """
        logger.info("상품명 입력창 선택 시작")
        
        try:
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
    
    def load_task_list_from_excel(self, account_id, step="step2", excel_path="percenty_id.xlsx"):
        """
        엑셀 파일에서 계정별 작업 목록 로드
        
        Args:
            account_id: 계정 ID (예: onepick2019@gmail.com)
            step: 작업 단계 (step2 또는 step3)
            excel_path: 엑셀 파일 경로
            
        Returns:
            list: 작업 목록 (provider_code, target_group 포함)
        """
        try:
            logging.info(f"계정 {account_id}의 {step} 작업 목록을 로드합니다.")
            
            # login_id 시트에서 계정과 연결된 시트명 찾기
            login_df = pd.read_excel(excel_path, sheet_name="login_id")
            account_row = login_df[login_df['id'] == account_id]
            
            if account_row.empty:
                logging.error(f"계정 {account_id}를 찾을 수 없습니다.")
                return []
            
            # 계정과 연결된 시트명 가져오기 (D열의 sheet_nickname 컬럼 사용)
            if 'sheet_nickname' in account_row.columns:
                sheet_name = account_row.iloc[0]['sheet_nickname']
            else:
                logging.error("계정과 연결된 시트명을 찾을 수 없습니다. (sheet_nickname 컬럼 필요)")
                return []
                
            logging.info(f"계정 {account_id}와 연결된 시트: {sheet_name}")
            
            # 연결된 시트에서 작업 목록 로드 (행 순서 보장)
            task_df = pd.read_excel(excel_path, sheet_name=sheet_name)
            # 원본 행 순서를 보장하기 위해 인덱스 리셋
            task_df = task_df.reset_index(drop=True)
            
            # 디버깅: 실제 컬럼명 확인
            logging.info(f"Excel 파일의 컬럼명: {list(task_df.columns)}")
            
            # step2 또는 step3에 해당하는 작업만 필터링
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
                # step이 포함된 컬럼 찾기
                step_columns = [col for col in task_df.columns if 'step' in col.lower()]
                step_column = step_columns[0]
                logging.info(f"step 관련 컬럼 발견: {step_columns}, 사용할 컬럼: {step_column}")
            
            if step_column:
                logging.info(f"'{step_column}' 컬럼을 사용하여 {step} 작업 필터링")
                step_tasks = task_df[task_df[step_column] == step]
                logging.info(f"필터링 전 총 행 수: {len(task_df)}, 필터링 후 행 수: {len(step_tasks)}")
            else:
                # step 컬럼이 없으면 모든 작업 반환
                step_tasks = task_df
                logging.warning(f"step 컬럼을 찾을 수 없어 모든 작업을 반환합니다.")
            
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
                
                if provider_code and target_group:
                    task = {
                        'provider_code': str(provider_code),
                        'target_group': str(target_group)
                    }
                    task_list.append(task)
                
            logging.info(f"{len(task_list)}개의 {step} 작업을 로드했습니다.")
            return task_list
            
        except Exception as e:
            logging.error(f"작업 목록 로드 중 오류: {e}")
            return []
    
    def load_task_list_from_excel_with_server_filter(self, account_id, step="step2", server_name=None, excel_path="percenty_id.xlsx"):
        """
        엑셀 파일에서 계정별 작업 목록 로드 (서버별 필터링 포함)
        
        Args:
            account_id: 계정 ID (예: onepick2019@gmail.com)
            step: 작업 단계 (step2 또는 step3)
            server_name: 서버명 (서버1, 서버2, 서버3)
            excel_path: 엑셀 파일 경로
            
        Returns:
            list: 작업 목록 (provider_code, target_group 포함)
        """
        try:
            logging.info(f"계정 {account_id}의 {step} 작업 목록을 로드합니다. (서버: {server_name})")
            
            # login_id 시트에서 계정과 연결된 시트명 찾기
            login_df = pd.read_excel(excel_path, sheet_name="login_id")
            account_row = login_df[login_df['id'] == account_id]
            
            if account_row.empty:
                logging.error(f"계정 {account_id}를 찾을 수 없습니다.")
                return []
            
            # 계정과 연결된 시트명 가져오기 (D열의 sheet_nickname 컬럼 사용)
            if 'sheet_nickname' in account_row.columns:
                sheet_name = account_row.iloc[0]['sheet_nickname']
            else:
                logging.error("계정과 연결된 시트명을 찾을 수 없습니다. (sheet_nickname 컬럼 필요)")
                return []
                
            logging.info(f"계정 {account_id}와 연결된 시트: {sheet_name}")
            
            # 연결된 시트에서 작업 목록 로드
            task_df = pd.read_excel(excel_path, sheet_name=sheet_name)
            
            # 디버깅: 실제 컬럼명 확인
            logging.info(f"Excel 파일의 컬럼명: {list(task_df.columns)}")
            
            # step2 또는 step3에 해당하는 작업만 필터링
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
                # step이 포함된 컬럼 찾기
                step_columns = [col for col in task_df.columns if 'step' in col.lower()]
                step_column = step_columns[0]
                logging.info(f"step 관련 컬럼 발견: {step_columns}, 사용할 컬럼: {step_column}")
            
            if step_column:
                logging.info(f"'{step_column}' 컬럼을 사용하여 {step} 작업 필터링")
                step_tasks = task_df[task_df[step_column] == step].reset_index(drop=True)
                logging.info(f"step 필터링 전 총 행 수: {len(task_df)}, 필터링 후 행 수: {len(step_tasks)}")
            else:
                # step 컬럼이 없으면 모든 작업 반환
                step_tasks = task_df.reset_index(drop=True)
                logging.warning(f"step 컬럼을 찾을 수 없어 모든 작업을 반환합니다.")
            
            # 서버별 필터링 (D열의 final_group 컬럼 사용)
            if server_name:
                server_column = None
                if 'final_group' in step_tasks.columns:
                    server_column = 'final_group'
                elif 'server' in step_tasks.columns:
                    server_column = 'server'
                elif 'Server' in step_tasks.columns:
                    server_column = 'Server'
                elif any('server' in col.lower() for col in step_tasks.columns):
                    # server가 포함된 컬럼 찾기
                    server_columns = [col for col in step_tasks.columns if 'server' in col.lower()]
                    server_column = server_columns[0]
                    logging.info(f"server 관련 컬럼 발견: {server_columns}, 사용할 컬럼: {server_column}")
                
                if server_column:
                    logging.info(f"'{server_column}' 컬럼을 사용하여 {server_name} 서버 필터링")
                    before_count = len(step_tasks)
                    step_tasks = step_tasks[step_tasks[server_column] == server_name].reset_index(drop=True)
                    after_count = len(step_tasks)
                    logging.info(f"서버 필터링 전 행 수: {before_count}, 필터링 후 행 수: {after_count}")
                else:
                    logging.warning(f"서버 필터링 컬럼을 찾을 수 없습니다. 모든 작업을 반환합니다.")
            
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
                
                if provider_code and target_group:
                    task = {
                        'provider_code': str(provider_code),
                        'target_group': str(target_group)
                    }
                    task_list.append(task)
                
            logging.info(f"{len(task_list)}개의 {step} 작업을 로드했습니다. (서버: {server_name})")
            return task_list
            
        except Exception as e:
            logging.error(f"서버별 작업 목록 로드 중 오류: {e}")
            return []
    
    def search_products_by_keyword(self, keyword):
        """
        키워드로 상품 검색
        
        Args:
            keyword: 검색할 키워드
            
        Returns:
            bool: 검색 성공 여부
        """
        try:
            logging.info(f"키워드 '{keyword}'로 상품 검색")
            
            # 상품명 입력창 찾기 (UI_ELEMENTS와 동일한 선택자 사용)
            input_selectors = [
                "//input[@placeholder='상품명 입력' and contains(@class, 'ant-input')]",
                "//input[@placeholder='상품명을 입력하세요']",
                "//input[contains(@class, 'ant-input') and @placeholder]",
                "//div[contains(@class, 'search')]//input[@type='text']"
            ]
            
            input_element = None
            for selector in input_selectors:
                try:
                    input_element = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except (TimeoutException, NoSuchElementException):
                    continue
                    
            if not input_element:
                logging.error("상품명 입력창을 찾을 수 없습니다.")
                return False
            
            # 입력창 클릭 후 전체 선택하여 기존 내용 삭제
            input_element.click()
            time.sleep(DELAY_SHORT)
            
            # Ctrl+A로 전체 선택 후 키워드 입력
            actions = ActionChains(self.driver)
            actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
            time.sleep(DELAY_SHORT)
            
            input_element.send_keys(keyword)
            time.sleep(DELAY_SHORT)
            
            # Enter 키로 검색 실행
            input_element.send_keys(Keys.ENTER)
            time.sleep(DELAY_MEDIUM)
            
            logging.info(f"키워드 '{keyword}' 검색 완료")
            return True
            
        except Exception as e:
            logging.error(f"상품 검색 중 오류: {e}")
            return False
    
    def get_product_count(self):
        """
        검색된 상품 개수 확인
        
        Returns:
            int: 상품 개수 (-1: 오류)
        """
        try:
            # 상품 개수 표시 요소 찾기
            count_selectors = [
                "//div[contains(@class, 'ant-pagination-total-text')]",
                "//span[contains(text(), '총') and contains(text(), '개')]",
                "//div[contains(text(), '총') and contains(text(), '건')]"
            ]
            
            for selector in count_selectors:
                try:
                    count_element = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    count_text = count_element.text
                    
                    # 숫자 추출
                    import re
                    numbers = re.findall(r'\d+', count_text)
                    if numbers:
                        count = int(numbers[0])
                        logging.info(f"검색된 상품 개수: {count}개")
                        return count
                        
                except (TimeoutException, NoSuchElementException):
                    continue
            
            logging.warning("상품 개수를 확인할 수 없습니다.")
            return -1
            
        except Exception as e:
            logging.error(f"상품 개수 확인 중 오류: {e}")
            return -1
    
    def process_keyword_search_and_move(self, keyword, target_group):
        """
        키워드로 검색하고 상품을 그룹으로 이동
        51개 이상일 경우 반복 처리
        
        Args:
            keyword: 검색 키워드
            target_group: 이동할 그룹명
            
        Returns:
            bool: 처리 성공 여부
        """
        try:
            logging.info(f"키워드 '{keyword}' 처리 시작, 대상 그룹: {target_group}")
            
            # dropdown_utils2 매니저 초기화
            dropdown_manager = get_product_search_dropdown_manager(self.driver)
            
            while True:
                # 상품명 입력창 선택 (키워드 검색 직전)
                if not self.select_product_name_input():
                    logging.error("상품명 입력창 선택 실패")
                    return False
                
                # 키워드로 상품 검색
                if not self.search_products_by_keyword(keyword):
                    logging.error(f"키워드 '{keyword}' 검색 실패")
                    return False
                
                # 상품 개수 확인
                product_count = self.get_product_count()
                
                if product_count == 0:
                    logging.info(f"키워드 '{keyword}'에 대한 상품이 없습니다. 다음 키워드로 진행합니다.")
                    return True
                elif product_count == -1:
                    logging.warning(f"키워드 '{keyword}'의 상품 개수를 확인할 수 없습니다. 그룹 이동을 시도합니다.")
                elif product_count >= 51:
                    logging.info(f"키워드 '{keyword}'의 상품이 {product_count}개입니다. 그룹 이동 후 재검색합니다.")
                else:
                    logging.info(f"키워드 '{keyword}'의 상품이 {product_count}개입니다. 그룹 이동을 진행합니다.")
                
                # 상품을 그룹으로 이동
                if dropdown_manager.move_products_to_group(target_group):
                    logging.info(f"키워드 '{keyword}'의 상품을 '{target_group}' 그룹으로 이동 완료")
                    
                    # 51개 이상이었다면 다시 검색하여 남은 상품 확인
                    if product_count >= 51:
                        logging.info(f"키워드 '{keyword}' 재검색을 진행합니다.")
                        continue
                    else:
                        return True
                else:
                    logging.error(f"키워드 '{keyword}'의 상품 그룹 이동 실패")
                    return False
                    
        except Exception as e:
            logging.error(f"키워드 '{keyword}' 처리 중 오류: {e}")
            return False
    
    def process_step2_tasks(self, account_id):
        """
        Step 2 작업 처리
        
        Args:
            account_id: 계정 ID
            
        Returns:
            bool: 작업 성공 여부
        """
        try:
            logging.info(f"계정 {account_id}의 Step 2 작업을 시작합니다.")
            
            # 엑셀에서 작업 목록 로드
            task_list = self.load_task_list_from_excel(account_id, "step2")
            if not task_list:
                logging.error("작업 목록을 로드할 수 없습니다.")
                return False
            
            # 각 작업 순차 처리
            success_count = 0
            for i, task in enumerate(task_list, 1):
                keyword = task['provider_code']
                target_group = task['target_group']
                
                logging.info(f"[{i}/{len(task_list)}] 키워드: {keyword}, 대상 그룹: {target_group}")
                
                if self.process_keyword_search_and_move(keyword, target_group):
                    success_count += 1
                    logging.info(f"작업 {i} 성공")
                else:
                    logging.error(f"작업 {i} 실패")
            
            logging.info(f"Step 2 작업 완료: {success_count}/{len(task_list)} 성공")
            return success_count > 0
            
        except Exception as e:
            logging.error(f"Step 2 작업 처리 중 오류: {e}")
            return False