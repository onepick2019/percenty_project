# -*- coding: utf-8 -*-

import os
import sys

# 프로젝트 루트를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
import logging
# import pyautogui  # 멀티브라우저 간섭 방지를 위해 Selenium으로 대체
# import pyperclip  # 멀티브라우저 간섭 방지를 위해 Selenium으로 대체
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# 프로젝트 내 모듈 임포트
from ui_elements import UI_ELEMENTS
import timesleep
from timesleep import sleep_with_logging, DELAY_VERY_SHORT2, DELAY_VERY_SHORT5, DELAY_VERY_SHORT, DELAY_SHORT, DELAY_MEDIUM, DELAY_STANDARD, DELAY_LONG, DELAY_EXTRA_LONG
from keyboard_shortcuts import KeyboardShortcuts
from dom_utils import wait_for_element
from click_utils import click_at_coordinates, smart_click, smart_click_with_focus
from image_utils5 import PercentyImageManager
from product_name_editor import ProductNameEditor
from dropdown_utils5 import get_dropdown_helper
import dom_selectors
from human_delay import HumanLikeDelay


# 로깅 설정
logger = logging.getLogger(__name__)

class ProductEditorCore5_3:
    """
    상품 복제 및 최적화 로직을 담당하는 클래스 (코어5)
    
    이 클래스는 다음 작업을 수행합니다:
    - 대기3 그룹에서 상품 1개마다 복제상품 3개 생성 (총 4개)
    - 각 상품별로 접미사, 할인율, 썸네일 최적화
    - 쇼핑몰A3, B3, C3, D3으로 그룹 이동
    """
    
    # 클래스 변수로 전역 배치 카운터 추가
    global_batch_counter = 0
    
    def __init__(self, driver, config=None, dropdown_manager=None):
        """
        상품 편집 코어5 초기화
        
        Args:
            driver: Selenium WebDriver 인스턴스
            config: 설정 정보 딕셔너리 (선택사항)
            dropdown_manager: 드롭다운 관리자 인스턴스 (선택사항)
        """
        self.driver = driver
        self.config = config or {}
        
        # dropdown_utils.py에서 기존 함수 사용
        if dropdown_manager is None:
            from dropdown_utils5 import get_dropdown_manager
            self.dropdown_manager = get_dropdown_manager(driver)
        else:
            self.dropdown_manager = dropdown_manager
            
        # 멀티브라우저 간섭 방지를 위해 use_selenium=True 강제 설정
        self.keyboard = KeyboardShortcuts(self.driver, use_selenium=True)
        self.image_manager = PercentyImageManager(self.driver)
        
        # 할인율 순서 (10개 상품마다 반복)
        self.discount_rates = [2, 5, 10, 15, 20, 25, 30, 35, 40, 45]
        self.current_product_index = 0  # 현재 처리 중인 상품 인덱스
        self.suffix_index = 0  # A-Z 접미사 인덱스 초기화
        self.thumbnail_count = 0  # 원본 상품의 썸네일 개수 저장
        
        # Human Delay 초기화
        self.human_delay = HumanLikeDelay(min_total_delay=152, max_total_delay=180, current_speed=150)
        logger.info(f"Human Delay 초기화 완료 - 목표 총 지연시간: 150-180초, 예상 액션 수: {self.human_delay.action_count}")
        
        # 배치 종료 이유 추적용 속성 초기화
        self._last_termination_reason = None
        

        
    def _check_modal_open(self, max_wait=10, check_interval=0.5):
        """
        모달창이 열렸는지 확인하는 함수
        
        Args:
            max_wait (float): 최대 대기 시간(초)
            check_interval (float): 확인 간격(초)
            
        Returns:
            bool: 모달창 열림 여부
        """
        logger.info(f"모달창이 열렸는지 확인 시작")
        
        modal_selectors = [
            "//div[@role='dialog']",
            "//div[contains(@class, 'ant-modal')]",
            "//div[contains(@class, 'ant-drawer-content')]"
        ]
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                for selector in modal_selectors:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements and len(elements) > 0:
                        logger.info(f"모달창 요소 발견: {selector}")
                        return True
                        
                time.sleep(check_interval)
                
            except Exception as e:
                logger.debug(f"모달 확인 중 오류: {e}")
                time.sleep(check_interval)
        
        logger.warning(f"모달창 열림 확인 실패 (제한시간 {max_wait}초 초과)")
        return False
        
    def _click_first_product(self):
        """
        첫번째 상품 클릭 시도 (FIRST_PRODUCT_ITEM DOM 선택자 사용)
        
        Returns:
            bool: 성공 여부
        """
        logger.info("첫번째 상품 클릭해 수정화면 모달창 열기 (FIRST_PRODUCT_ITEM DOM 선택자 사용)")
        
        try:
            if smart_click(self.driver, UI_ELEMENTS["FIRST_PRODUCT_ITEM"], delay=DELAY_SHORT):
                logger.info("첫번째 상품 아이템 클릭 성공")
                
                # 고정 대기 제거하고 바로 모달창 감지
                if self._check_modal_open(max_wait=5):
                    logger.info("첫번째 상품 클릭 및 모달창 열림 확인 성공")
                    return True
                else:
                    logger.warning("첫번째 상품 클릭했지만 모달창 열림 확인 실패")
                    return False
            else:
                logger.error("첫번째 상품 아이템 클릭 실패")
                return False
                
        except Exception as e:
            logger.error(f"첫번째 상품 클릭 중 오류: {e}")
            return False
    
    def wait_for_tab_active(self, tab_key, timeout=5):
        """
        탭이 활성화될 때까지 대기
        
        Args:
            tab_key (str): UI_ELEMENTS의 탭 키 이름
            timeout (int): 최대 대기 시간(초)
            
        Returns:
            bool: 탭 활성화 성공 여부
        """
        try:
            # 특별한 경우 처리: PRODUCT_COPY_BUTTON은 탭이 아니므로 단순 대기
            if tab_key == "PRODUCT_COPY_BUTTON":
                logger.info(f"{tab_key} 버튼 클릭 후 대기")
                time.sleep(1)
                return True
            
            active_selectors = {
                "PRODUCT_TAB_BASIC": dom_selectors.PAGE_LOAD_INDICATORS["PRODUCT_TAB_BASIC_ACTIVE"],
                "PRODUCT_TAB_OPTION": dom_selectors.PAGE_LOAD_INDICATORS["PRODUCT_TAB_OPTION_ACTIVE"],
                "PRODUCT_TAB_PRICE": dom_selectors.PAGE_LOAD_INDICATORS["PRODUCT_TAB_PRICE_ACTIVE"],
                "PRODUCT_TAB_THUMBNAIL": dom_selectors.PAGE_LOAD_INDICATORS["PRODUCT_TAB_THUMBNAIL_ACTIVE"]
            }
            
            if tab_key not in active_selectors:
                logger.warning(f"알 수 없는 탭 키: {tab_key}")
                time.sleep(1)
                return True
                
            active_selector = active_selectors[tab_key]
            
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    element = self.driver.find_element(By.XPATH, active_selector)
                    if element.is_displayed():
                        logger.info(f"{tab_key} 탭 활성화 확인")
                        return True
                except Exception:
                    pass
                    
                time.sleep(0.2)
                
            logger.warning(f"{tab_key} 탭 활성화 대기 시간 초과 ({timeout}초)")
            return False
            
        except Exception as e:
            logger.error(f"탭 활성화 확인 중 오류: {e}")
            return False
    
    def _get_product_count_in_group(self, group_name, timeout=10):
        """
        특정 그룹의 상품 수를 확인하는 함수
        
        Args:
            group_name (str): 그룹명
            timeout (int): 최대 대기 시간 (초)
            
        Returns:
            int: 상품 수 (확인 실패 시 -1)
        """
        import time
        start_time = time.time()
        
        try:
            logger.info(f"{group_name} 그룹의 상품 수 확인 시작 (타임아웃: {timeout}초)")
            
            # 더 정확한 상품 수 표시 요소 찾기 (그룹상품관리 화면의 테이블 영역)
            count_selectors = [
                # 그룹상품관리 화면의 pagination 영역
                "//div[contains(@class, 'ant-pagination-total-text')]",
                # 테이블 하단의 상품 수 표시
                "//div[contains(@class, 'ant-table-pagination')]//span[contains(text(), '총')]",
                # 일반적인 상품 수 표시 (더 구체적으로)
                "//div[contains(@class, 'ant-table')]//span[contains(text(), '총') and contains(text(), '개')]",
                # 백업용 선택자
                "//span[contains(text(), '총') and contains(text(), '개 상품')]"
            ]
            
            import re
            for i, selector in enumerate(count_selectors):
                # 타임아웃 체크
                if time.time() - start_time > timeout:
                    logger.warning(f"상품 수 확인 타임아웃 ({timeout}초 초과)")
                    return -1
                    
                try:
                    count_elements = self.driver.find_elements(By.XPATH, selector)
                    logger.info(f"선택자 {i+1} ('{selector}')로 찾은 요소 수: {len(count_elements)}")
                    
                    for j, element in enumerate(count_elements):
                        # 각 요소 처리 시에도 타임아웃 체크
                        if time.time() - start_time > timeout:
                            logger.warning(f"상품 수 확인 타임아웃 (요소 처리 중)")
                            return -1
                        try:
                            # 요소 텍스트 가져오기에 타임아웃 추가
                            from selenium.webdriver.support.ui import WebDriverWait
                            from selenium.webdriver.support import expected_conditions as EC
                            
                            try:
                                # 요소가 표시될 때까지 최대 3초 대기
                                WebDriverWait(self.driver, 3).until(
                                    EC.visibility_of(element)
                                )
                                count_text = element.text.strip()
                            except Exception as timeout_e:
                                logger.warning(f"  요소 {j+1} 표시 대기 중 타임아웃: {timeout_e}")
                                # 타임아웃 시에도 텍스트 가져오기 시도
                                count_text = element.text.strip() if element else ""
                            
                            logger.info(f"  요소 {j+1} 텍스트: '{count_text}'")
                            
                            if count_text and ('총' in count_text or '개' in count_text):
                                # 콤마가 포함된 숫자 추출 (예: "4,253" -> 4253)
                                import re
                                # 콤마를 포함한 연속된 숫자 패턴 찾기
                                number_match = re.search(r'[\d,]+', count_text)
                                if number_match:
                                    # 콤마 제거 후 정수로 변환
                                    number_str = number_match.group().replace(',', '')
                                    count = int(number_str)
                                    logger.info(f"✅ {group_name} 그룹의 상품 수 확인 성공: {count}개 (선택자 {i+1}, 요소 {j+1}) (원본: '{count_text}')")
                                    return count
                        except Exception as e:
                            logger.warning(f"  요소 {j+1} 처리 중 오류: {e}")
                            continue
                            
                except Exception as e:
                    logger.warning(f"선택자 {i+1} 처리 중 오류: {e}")
                    continue
            
            # 모든 선택자가 실패한 경우, 테이블 행 수로 대체 계산
            # 최종 타임아웃 체크
            if time.time() - start_time > timeout:
                logger.warning(f"상품 수 확인 최종 타임아웃 ({timeout}초 초과)")
                return -1
                
            try:
                logger.info("상품 수 텍스트를 찾을 수 없어 테이블 행 수로 계산 시도")
                table_rows = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'ant-table-tbody')]//tr[contains(@class, 'ant-table-row')]")
                row_count = len(table_rows)
                logger.info(f"테이블 행 수: {row_count}개")
                
                if row_count == 0:
                    # 빈 테이블 확인
                    empty_elements = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'ant-empty') or contains(text(), '데이터가 없습니다')]")
                    if empty_elements:
                        logger.info(f"✅ {group_name} 그룹에 상품이 없음을 확인 (빈 테이블)")
                        return 0
                
                logger.info(f"✅ {group_name} 그룹의 상품 수 (테이블 행 기준): {row_count}개")
                return row_count
                
            except Exception as e:
                logger.error(f"테이블 행 수 계산 중 오류: {e}")
            
            elapsed_time = time.time() - start_time
            logger.warning(f"❌ {group_name} 그룹의 상품 수 확인 완전 실패 (경과 시간: {elapsed_time:.2f}초)")
            return -1
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"상품 수 확인 중 전체 오류: {e} (경과 시간: {elapsed_time:.2f}초)")
            return -1
    
    def _wait_for_product_in_group(self, group_name, expected_count=1, max_wait_time=15, refresh_group="등록실행"):
        """
        특정 그룹에 상품이 나타날 때까지 동적으로 대기하는 함수
        화면 새로고침 효과를 위해 다른 그룹을 선택했다가 다시 대상 그룹을 선택하는 방식 사용
        
        Args:
            group_name (str): 대상 그룹명
            expected_count (int): 예상 상품 수 (기본값: 1)
            max_wait_time (int): 최대 대기 시간(초) (기본값: 15)
            refresh_group (str): 새로고침용 그룹명 (기본값: "등록실행")
            
        Returns:
            int: 최종 상품 수 (시간 초과 시 -1)
        """
        start_time = time.time()
        attempt = 0
        max_attempts = 3  # 최대 3회 시도
        
        logger.info(f"{group_name} 그룹에 상품 {expected_count}개가 나타날 때까지 최대 {max_wait_time}초 대기 (새로고침 방식)")
        
        # 먼저 현재 상품 수를 확인
        initial_count = self._get_product_count_in_group(group_name)
        if initial_count >= expected_count:
            logger.info(f"{group_name} 그룹에 이미 상품 {initial_count}개가 있음 (즉시 반환)")
            return initial_count
        
        logger.info(f"{group_name} 그룹에 현재 상품 {initial_count}개, {expected_count}개까지 대기 필요")
        
        while time.time() - start_time < max_wait_time and attempt < max_attempts:
            attempt += 1
            logger.info(f"새로고침 시도 {attempt}/{max_attempts}: {refresh_group} -> {group_name}")
            
            # 1. 새로고침용 그룹 선택 (화면 새로고침 효과)
            if not self.dropdown_manager.select_group_in_management_screen(refresh_group):
                logger.warning(f"{refresh_group} 그룹 선택 실패 (시도 {attempt})")
                time.sleep(1)
                continue
            
            # 2. 1-2초 지연
            time.sleep(1.5)
            
            # 3. 대상 그룹 다시 선택
            if not self.dropdown_manager.select_group_in_management_screen(group_name):
                logger.warning(f"{group_name} 그룹 선택 실패 (시도 {attempt})")
                time.sleep(1)
                continue
            
            # 4. 상품 수 확인
            time.sleep(1)  # 그룹 선택 후 잠시 대기
            current_count = self._get_product_count_in_group(group_name)
            
            if current_count >= expected_count:
                elapsed_time = time.time() - start_time
                logger.info(f"{group_name} 그룹에 상품 {current_count}개 확인됨 (시도: {attempt}회, 소요시간: {elapsed_time:.1f}초)")
                return current_count
            elif current_count == 0:
                logger.info(f"{group_name} 그룹에 상품이 아직 없음 (시도: {attempt}회, 경과시간: {time.time() - start_time:.1f}초)")
            else:
                logger.info(f"{group_name} 그룹에 상품 {current_count}개 있음, {expected_count}개 대기 중 (시도: {attempt}회)")
            
            # 다음 시도 전 잠시 대기
            if attempt < max_attempts:
                time.sleep(2)
        
        # 최종 확인
        final_count = self._get_product_count_in_group(group_name)
        if attempt >= max_attempts:
            logger.warning(f"{group_name} 그룹 최대 시도 횟수 초과 ({max_attempts}회), 최종 상품 수: {final_count}개")
        else:
            logger.warning(f"{group_name} 그룹 대기 시간 초과 ({max_wait_time}초), 최종 상품 수: {final_count}개")
        
        return final_count if final_count > 0 else -1
    
    def _copy_product_with_count_check(self, expected_count):
        """
        상품 복사 후 상품 수 변화를 확인하는 함수
        
        Args:
            expected_count (int): 복사 후 예상되는 상품 수
            
        Returns:
            bool: 성공 여부
        """
        try:
            # 상품복사 버튼 클릭
            logger.info("상품복사 버튼 클릭")
            if not smart_click(self.driver, UI_ELEMENTS["PRODUCT_COPY_BUTTON"], DELAY_VERY_SHORT):
                logger.error("상품복사 버튼 클릭 실패")
                return False
            
            # 상품 수 변화 확인 (최대 10초 대기)
            max_wait = 10
            check_interval = 0.5
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                current_count = self._get_product_count_in_group("등록C")
                if current_count == expected_count:
                    logger.info(f"상품복사 완료 확인: 현재 상품 수 {current_count}개")
                    return True
                elif current_count > expected_count:
                    logger.warning(f"예상보다 많은 상품 수: 예상 {expected_count}개, 실제 {current_count}개")
                    return True
                
                time.sleep(check_interval)
            
            logger.error(f"상품복사 후 상품 수 변화 확인 실패: 예상 {expected_count}개")
            return False
            
        except Exception as e:
            logger.error(f"상품복사 중 오류: {e}")
            return False
    

    
    def _get_suffix_from_excel(self, column_name, account_id):
        """
        Excel 파일에서 접미사를 가져오는 함수
        
        Args:
            column_name (str): 열 이름 (예: 'suffixA3', 'suffixB3')
            account_id (str): 계정 ID
            
        Returns:
            str: 접미사 문자열
        """
        try:
            import pandas as pd
            import os
            
            # Excel 파일 경로 확인
            excel_path = 'percenty_id.xlsx'
            if not os.path.exists(excel_path):
                logger.error(f"Excel 파일을 찾을 수 없음: {excel_path}")
                return ""
            
            # 먼저 사용 가능한 시트 확인
            try:
                xl_file = pd.ExcelFile(excel_path)
                available_sheets = xl_file.sheet_names
                logger.info(f"사용 가능한 시트: {available_sheets}")
                
                # 시트 이름 결정 (우선순위: 'login_id' -> 첫 번째 시트)
                sheet_name = None
                if 'login_id' in available_sheets:
                    sheet_name = 'login_id'
                elif available_sheets:
                    sheet_name = available_sheets[0]
                    logger.info(f"'login_id' 시트가 없어서 첫 번째 시트 사용: {sheet_name}")
                else:
                    logger.error("Excel 파일에 시트가 없음")
                    return ""
                    
            except Exception as e:
                logger.error(f"Excel 파일 시트 확인 실패: {e}")
                return ""
            
            # Excel 파일 읽기
            df = pd.read_excel(excel_path, sheet_name=sheet_name)
            logger.info(f"Excel 파일 읽기 성공. 시트: {sheet_name}, 행 수: {len(df)}, 열: {list(df.columns)}")
            
            # id 열이 있는지 확인 (실제 Excel 파일에서는 'id' 열 사용)
            id_column = None
            if 'login_id' in df.columns:
                id_column = 'login_id'
            elif 'id' in df.columns:
                id_column = 'id'
            else:
                logger.error(f"Excel 파일에 'login_id' 또는 'id' 열이 없음. 사용 가능한 열: {list(df.columns)}")
                return ""
            
            logger.info(f"계정 ID 검색에 사용할 열: {id_column}")
            
            # 해당 계정의 행 찾기
            account_row = df[df[id_column] == account_id]
            if account_row.empty:
                logger.warning(f"계정 ID {account_id}를 찾을 수 없음. 사용 가능한 계정 ID: {df[id_column].tolist()}")
                return ""
            
            # 해당 열의 값 가져오기
            if column_name in df.columns:
                suffix_value = account_row[column_name].iloc[0]
                # NaN이나 None 값 처리
                if pd.isna(suffix_value) or suffix_value is None:
                    logger.info(f"Excel에서 {column_name} 값이 비어있음")
                    return ""
                suffix = str(suffix_value).strip()
                logger.info(f"Excel에서 {column_name} 접미사 가져옴: '{suffix}'")
                return suffix
            else:
                logger.warning(f"Excel에서 {column_name} 열을 찾을 수 없음. 사용 가능한 열: {list(df.columns)}")
                return ""
                
        except Exception as e:
            logger.error(f"Excel에서 접미사 가져오기 실패: {e}")
            import traceback
            logger.error(f"상세 오류: {traceback.format_exc()}")
            return ""
    
    def _add_suffix_to_product_name(self, suffix, remove_copy_suffix=False, copy_number=None):
        """
        상품명에 접미사를 추가하는 함수 (Selenium 우선, 폴백 지원)
        
        Args:
            suffix (str): 추가할 접미사
            remove_copy_suffix (bool): 복사 접미사 제거 여부
            copy_number (int): 제거할 복사 번호 (예: (3), (2), (1))
            
        Returns:
            bool: 성공 여부
        """
        try:
            # Selenium을 사용한 상품명 입력 시도
            product_name_element = UI_ELEMENTS["PRODUCT_NAMEEDIT_TEXTAREA"]
            dom_selector = product_name_element["dom_selector"]
            
            try:
                # 상품명 입력 필드 찾기
                product_name_field = self.driver.find_element(By.XPATH, dom_selector)
                
                if product_name_field:
                    # 현재 상품명 가져오기
                    current_name = product_name_field.get_attribute("value")
                    logger.info(f"현재 상품명: '{current_name}'")
                    
                    # 복사 접미사 제거가 필요한 경우
                    if remove_copy_suffix and copy_number:
                        logger.info(f"복사 접미사 ({copy_number}) 제거")
                        import re
                        # 복사 접미사 패턴 " (숫자)" 제거
                        current_name = re.sub(r'\s*\(\d+\)$', '', current_name)
                        logger.info(f"텍스트 정리 완료: '{current_name}'")
                    
                    # 기존 상품명에 이미 접미사가 포함되어 있는지 확인
                    if suffix in current_name:
                        # 이미 접미사가 포함된 경우, 접미사만 남기고 원본 상품명 부분 제거
                        # 예: "원본상품명원본상품명 접미사" -> "원본상품명 접미사"
                        suffix_index = current_name.find(suffix)
                        if suffix_index > 0:
                            # 접미사 앞부분에서 중복된 부분 찾기
                            before_suffix = current_name[:suffix_index].strip()
                            # 중복 제거: 앞부분이 반복되는 경우 절반만 사용
                            if len(before_suffix) > 0:
                                half_length = len(before_suffix) // 2
                                if before_suffix[:half_length] == before_suffix[half_length:]:
                                    new_name = before_suffix[:half_length] + " " + suffix
                                else:
                                    new_name = before_suffix + " " + suffix
                            else:
                                new_name = suffix
                        else:
                            new_name = current_name
                    else:
                        # 접미사가 없는 경우, 기존 이름에 접미사 추가
                        new_name = f"{current_name} {suffix}"
                    
                    logger.info(f"새로운 상품명: '{new_name}'")
                    
                    # Selenium으로 상품명 입력 (전체 선택 후 입력)
                    product_name_field.click()
                    time.sleep(0.1)
                    product_name_field.send_keys(Keys.CONTROL + "a")  # 전체 선택
                    time.sleep(0.1)
                    product_name_field.send_keys(new_name)
                    
                    # 변경사항 저장을 위한 포커스 이동 (Tab 키로 다음 필드로 이동)
                    product_name_field.send_keys(Keys.TAB)
                    time.sleep(0.3)
                    
                    # 추가 안전장치: 다시 상품명 필드로 돌아가서 Enter 키 입력
                    product_name_field.click()
                    time.sleep(0.1)
                    product_name_field.send_keys(Keys.ENTER)
                    time.sleep(0.2)
                    
                    logger.info(f"Selenium으로 접미사 '{suffix}' 추가 완료: '{new_name}'")
                    return True
                    
            except Exception as selenium_error:
                logger.error(f"상품명 입력 필드를 찾을 수 없습니다. 기존 방식으로 폴백")
                # 폴백: 기존 키보드 방식 사용
                return self._add_suffix_to_product_name_fallback(suffix, remove_copy_suffix, copy_number)
                
        except Exception as e:
            logger.error(f"접미사 추가 중 오류: {e}")
            return False
    
    def _add_suffix_to_product_name_fallback(self, suffix, remove_copy_suffix=False, copy_number=None):
        """
        상품명에 접미사를 추가하는 폴백 함수 (키보드 방식)
        
        Args:
            suffix (str): 추가할 접미사
            remove_copy_suffix (bool): 복사 접미사 제거 여부
            copy_number (int): 제거할 복사 번호 (예: (3), (2), (1))
            
        Returns:
            bool: 성공 여부
        """
        try:
            # 복사 접미사 제거가 필요한 경우
            if remove_copy_suffix and copy_number:
                logger.info(f"복사 접미사 ({copy_number}) 제거")
                # 텍스트 끝으로 이동
                self.keyboard.press_keys("End", use_selenium=False)
                time.sleep(0.1)
                
                # 복사 접미사 형태에 따라 적절한 수만큼 Backspace
                # " (숫자)" 형태: 공백 + 괄호 + 숫자 + 괄호 = 4글자
                # Selenium으로 안전한 백스페이스 처리 (pyautogui 대신)
                backspace_count = 4  # " (3)" 형태를 완전히 제거
                logger.info(f"Backspace {backspace_count}회 실행하여 복사 접미사 제거")
                try:
                    active_element = self.driver.switch_to.active_element
                    current_value = active_element.get_attribute('value') or ''
                    # 끝에서 4글자 제거
                    new_value = current_value[:-backspace_count] if len(current_value) >= backspace_count else ''
                    active_element.clear()
                    active_element.send_keys(new_value)
                    logger.info(f"복사 접미사 제거 완료: '{current_value}' -> '{new_value}'")
                except Exception as e:
                    logger.warning(f"Selenium 백스페이스 처리 실패: {e}")
                    # 백업: 키보드 단축키 사용
                    for _ in range(backspace_count):
                        self.keyboard.press_keys("BackSpace", use_selenium=False)
                        time.sleep(0.05)
                 
                # 추가 안전장치: 괄호가 남아있다면 추가로 제거
                # Ctrl+A로 전체 선택 후 현재 텍스트 확인
                self.keyboard.select_all()
                time.sleep(0.1)
                self.keyboard.copy()
                time.sleep(0.1)
                # Selenium으로 현재 텍스트 직접 가져오기 (pyperclip 대신)
                try:
                    active_element = self.driver.switch_to.active_element
                    current_text = active_element.get_attribute('value') or ''
                except Exception as e:
                    logger.warning(f"Selenium으로 텍스트 가져오기 실패: {e}")
                    current_text = ''
                 
                # 괄호가 포함되어 있다면 추가 처리
                if ')' in current_text:
                    logger.info(f"현재 텍스트에 괄호 발견: '{current_text}', 추가 정리 수행")
                    # 복사 접미사 패턴 " (숫자)" 만 제거
                    import re
                    # 공백 + 괄호 + 숫자 + 괄호 패턴을 찾아서 제거
                    clean_text = re.sub(r'\s*\(\d+\)$', '', current_text)
                    
                    # Selenium으로 정리된 텍스트 직접 입력 (pyperclip 대신)
                    try:
                        active_element = self.driver.switch_to.active_element
                        active_element.clear()
                        active_element.send_keys(clean_text)
                    except Exception as e:
                        logger.warning(f"Selenium 텍스트 입력 실패: {e}")
                        # 백업: 키보드 단축키 사용
                        self.keyboard.select_all()
                        self.keyboard.type_text(clean_text)
                    logger.info(f"텍스트 정리 완료: '{clean_text}'")
                else:
                    # 텍스트 끝으로 이동
                    self.keyboard.press_keys("End", use_selenium=False)
                 
                time.sleep(0.1)
            else:
                # 복사 접미사 제거가 아닌 경우, 기존 텍스트 끝으로 이동
                # End 키를 눌러 커서를 텍스트 끝으로 이동
                self.keyboard.press_keys("End", use_selenium=False)
                time.sleep(0.1)
            
            # Selenium으로 공백과 접미사 직접 추가 (pyperclip 대신)
            try:
                active_element = self.driver.switch_to.active_element
                current_value = active_element.get_attribute('value') or ''
                new_value = current_value + " " + suffix
                active_element.clear()
                active_element.send_keys(new_value)
                logger.info(f"접미사 추가 완료: '{current_value}' -> '{new_value}'")
            except Exception as e:
                logger.warning(f"Selenium 접미사 추가 실패: {e}")
                # 백업: 키보드 단축키 사용
                self.keyboard.type_text(" " + suffix)
            time.sleep(0.1)
            logger.info(f"접미사 '{suffix}' 추가 완료")
            
            return True
            
        except Exception as e:
            logger.error(f"접미사 추가 중 오류: {e}")
            return False
    
    def _modify_product_name_with_suffix(self):
        """
        ProductNameEditor를 사용하여 상품명을 수정합니다.
        """
        try:
            logger.info("ProductNameEditor를 사용한 상품명 수정 시작")
            
            # ProductNameEditor 인스턴스 생성
            name_editor = ProductNameEditor(self.driver)
            
            # 상품명 수정 실행 - A에서 Z까지 순차적으로 접미사 부여
            result = name_editor.edit_product_name(self.suffix_index)
            
            # 순차적으로 A-Z 접미사 사용하기 위해 인덱스 증가
            self.suffix_index = (self.suffix_index + 1) % 26
            next_suffix = chr(65 + self.suffix_index)
            logger.info(f"상품명 수정 결과: {'성공' if result else '실패'} (현재 인덱스: {self.suffix_index}, 다음 상품은 '{next_suffix}' 사용)")
            
            # 상품명 수정 후 DOM 안정화를 위한 충분한 대기
            time.sleep(2)
            
            return result
            
        except ImportError as ie:
            logger.error(f"product_name_editor.py 모듈을 찾을 수 없습니다: {ie}")
            return False
        except Exception as e:
            logger.error(f"상품명 수정 중 오류 발생: {e}")
            return False
    
    def _check_modal_closed(self):
        """
        모달창이 닫혔는지 확인합니다.
        
        Returns:
            bool: 모달창이 닫혔으면 True, 아니면 False
        """
        try:
            # 모달창 관련 요소들이 사라졌는지 확인
            modal_selectors = [
                "//div[contains(@class, 'ant-modal')]//div[contains(@class, 'ant-modal-content')]",
                "//div[contains(@class, 'ant-drawer')]//div[contains(@class, 'ant-drawer-content')]",
                "//div[@class='ant-modal-mask']",
                "//div[@class='ant-drawer-mask']"
            ]
            
            for selector in modal_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements:
                        # 요소가 존재하고 표시되는지 확인
                        for element in elements:
                            if element.is_displayed():
                                logger.info(f"모달창 요소가 여전히 표시됨: {selector}")
                                return False
                except Exception:
                    continue
            
            logger.info("모달창 관련 요소들이 모두 사라짐")
            return True
            
        except Exception as e:
            logger.error(f"모달창 닫힘 확인 중 오류: {e}")
            return False
    
    def _set_discount_rate(self, rate):
        """
        할인율을 설정하는 함수 (Selenium 우선, 폴백 지원)
        
        Args:
            rate (int): 설정할 할인율
            
        Returns:
            bool: 성공 여부
        """
        try:
            # Selenium을 사용한 할인율 입력 시도
            discount_element = UI_ELEMENTS["PRODUCT_PRICE_DISCOUNTRATE"]
            dom_selector = discount_element["dom_selector"]
            
            try:
                # 할인율 입력 필드 찾기
                discount_field = self.driver.find_element(By.XPATH, dom_selector)
                
                if discount_field:
                    # Selenium으로 할인율 입력 (전체 선택 후 입력)
                    discount_field.click()
                    time.sleep(0.1)
                    discount_field.send_keys(Keys.CONTROL + "a")  # 전체 선택
                    time.sleep(0.1)
                    discount_field.send_keys(str(rate))
                    
                    # 변경사항 저장을 위한 포커스 이동 (Tab 키로 다음 필드로 이동)
                    discount_field.send_keys(Keys.TAB)
                    time.sleep(0.3)
                    
                    # 추가 안전장치: 다시 할인율 필드로 돌아가서 Enter 키 입력
                    discount_field.click()
                    time.sleep(0.1)
                    discount_field.send_keys(Keys.ENTER)
                    time.sleep(0.2)
                    
                    logger.info(f"Selenium으로 할인율 {rate}% 설정 완료")
                    return True
                    
            except Exception as selenium_error:
                logger.error(f"할인율 입력 필드를 찾을 수 없습니다. 기존 방식으로 폴백")
                # 폴백: 기존 키보드 방식 사용
                return self._set_discount_rate_fallback(rate)
                
        except Exception as e:
            logger.error(f"할인율 설정 중 오류: {e}")
            return False
    
    def _set_discount_rate_fallback(self, rate):
        """
        할인율을 설정하는 폴백 함수 (키보드 방식)
        
        Args:
            rate (int): 설정할 할인율
            
        Returns:
            bool: 성공 여부
        """
        try:
            # 기존 할인율 전체 선택 후 새 할인율 입력
            self.keyboard.select_all()
            time.sleep(0.1)
            
            # Selenium으로 할인율 직접 입력 (pyperclip 대신)
            try:
                active_element = self.driver.switch_to.active_element
                active_element.clear()
                active_element.send_keys(str(rate))
            except Exception as e:
                logger.warning(f"Selenium 할인율 입력 실패: {e}")
                # 백업: 키보드 단축키 사용
                self.keyboard.type_text(str(rate))
            logger.info(f"할인율 {rate}% 설정 완료")
            
            return True
            
        except Exception as e:
            logger.error(f"할인율 설정 중 오류: {e}")
            return False
    
    def _get_discount_rate_for_product(self, product_index):
        """
        상품 인덱스에 따른 할인율 순차 입력
        각 상품별로 미리 정해진 순서대로 할인율을 입력:
        - 1번째 상품(원본): 2, 5, 10, 15, 20, 25, 30, 35, 40, 45
        - 2번째 상품(복사1): 15, 20, 25, 30, 35, 40, 45, 2, 5, 10
        - 3번째 상품(복사2): 25, 30, 35, 40, 45, 2, 5, 10, 15, 20
        - 4번째 상품(복사3): 35, 40, 45, 2, 5, 10, 15, 20, 25, 30
        
        Args:
            product_index (int): 상품 인덱스 (0부터 시작)
            
        Returns:
            int: 할인율
        """
        logger.info(f"할인율 순차 입력 시작 - product_index: {product_index}")
        
        # 각 상품별 할인율 순서 정의
        discount_sequences = {
            0: [2, 5, 10, 15, 20, 25, 30, 35, 40, 45],  # 1번째 상품(원본)
            1: [15, 20, 25, 30, 35, 40, 45, 2, 5, 10],  # 2번째 상품(복사1)
            2: [25, 30, 35, 40, 45, 2, 5, 10, 15, 20],  # 3번째 상품(복사2)
            3: [35, 40, 45, 2, 5, 10, 15, 20, 25, 30]   # 4번째 상품(복사3)
        }
        
        # 상품 타입 결정 (4개 상품마다 반복)
        product_type = product_index % 4
        
        # 해당 상품 타입의 할인율 순서 가져오기
        sequence = discount_sequences[product_type]
        
        # 각 상품 타입별로 몇 번째 할인율인지 계산
        # 전역 배치 카운터를 사용하여 배치가 반복될 때마다 할인율이 순차적으로 증가
        # 배치 카운터는 1부터 시작하므로 0부터 시작하도록 조정
        batch_offset = (ProductEditorCore5_3.global_batch_counter - 1) if ProductEditorCore5_3.global_batch_counter > 0 else 0
        type_occurrence = (product_index // 4) + batch_offset  # 해당 타입이 몇 번째로 처리되는지
        sequence_index = type_occurrence % len(sequence)
        
        # 할인율 선택
        selected_rate = sequence[sequence_index]
        
        product_names = ["원본", "복사1", "복사2", "복사3"]
        product_name = product_names[product_type]
        
        logger.info(f"할인율 순차 입력 완료 - {product_name}({product_index}): {selected_rate}% (sequence_index: {sequence_index}, batch: {ProductEditorCore5_3.global_batch_counter}, type_occurrence: {type_occurrence})")
        
        return selected_rate
    

    
    def _close_modal_with_esc(self):
        """
        ESC 키로 모달창 닫기
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("ESC 키로 상품수정 모달창 나가기")

            self.keyboard.escape_key()
            time.sleep(2)  # 모달창이 닫힐 때까지 대기
            
            # 모달창이 닫혔는지 확인
            modal_closed = self._check_modal_closed()
            if modal_closed:
                logger.info("상품수정 모달창이 성공적으로 닫혔습니다.")
                return True
            else:
                logger.warning("모달창이 완전히 닫히지 않았을 수 있습니다.")
                return False
            
        except Exception as e:
            logger.error(f"모달창 닫기 중 오류: {e}")
            return False
    
    def prepare_group_management_screen(self):
        """
        그룹상품관리 화면으로 이동하고 로딩을 대기하는 메서드
        배치 작업 시 한 번만 실행하면 되는 초기화 작업
        
        Returns:
            bool: 성공 여부
        """
        try:
            # 0. 그룹상품관리 화면으로 이동
            logger.info("0. 그룹상품관리 화면으로 이동")
            self._navigate_to_group_management()
            
            # 0-1. 그룹상품관리 화면 로딩 대기
            logger.info("0-1. 그룹상품관리 화면 로딩 대기")
            if not self._wait_for_group_management_loaded():
                logger.error("그룹상품관리 화면 로딩 실패")
                return False
                
            logger.info("그룹상품관리 화면 준비 완료")
            return True
            
        except Exception as e:
            logger.error(f"그룹상품관리 화면 준비 중 오류: {e}")
            return False
    
    def process_product_copy_and_optimization(self, account_id):
        """
        상품 복제 및 최적화 전체 프로세스
        
        Args:
            account_id (str): 계정 ID
            
        Returns:
            bool: 성공 여부
        """
        try:
            # 새로운 배치 시작 시 전역 카운터 증가
            ProductEditorCore5_3.global_batch_counter += 1
            
            # 새로운 상품 처리 시작 시 인덱스를 0으로 초기화
            self.current_product_index = 0
            logger.info(f"상품 복사 및 최적화 프로세스 시작 - current_product_index: {self.current_product_index}, global_batch: {ProductEditorCore5_3.global_batch_counter}")
            
            logger.info("\n\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            logger.info("!!! 상품 복사 및 최적화 프로세스 시작 !!!")
            logger.info("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n")

            # 1-0. 최적화 진행전에 등록C 상품 모두 복제X로 이동하기
            logger.info("1-0. 최적화 진행전에 등록C 상품 모두 복제X로 이동하기")
            
            # 등록C 그룹 선택하여 상품 수 확인
            if not self.dropdown_manager.select_group_in_management_screen("등록C"):
                logger.error("등록C 그룹 선택 실패")
                return False
            
            # 등록C 그룹의 총 상품수 확인
            registrationA_product_count = self._get_product_count_in_group("등록C")
            logger.info(f"등록C 그룹의 총 상품수: {registrationA_product_count}개")
            
            if registrationA_product_count == 0:
                logger.info("등록C 그룹에 상품이 없으므로 이동 작업을 스킵합니다.")
            elif registrationA_product_count >= 1:
                logger.info(f"등록C 그룹에 {registrationA_product_count}개 상품이 있으므로 모두 복제X 그룹으로 이동합니다.")
                
                # 전체선택 버튼 존재 여부 확인
                logger.info("복제X로 이동하기 전에 전체선택 버튼 존재 여부 확인")
                if self.dropdown_manager.select_all_products(timeout=5):
                    logger.info("전체선택 버튼이 존재하고 선택 성공, 복제X 그룹으로 이동 진행")
                    # 모든 상품을 복제X 그룹으로 이동
                    if self.dropdown_manager.move_products_to_group("복제X"):
                        logger.info("등록C의 모든 상품이 복제X 그룹으로 성공적으로 이동되었습니다.")
                    else:
                        logger.error("등록C의 상품을 복제X 그룹으로 이동하는데 실패했습니다.")
                        return False
                else:
                    logger.warning("전체선택 버튼이 없거나 선택 실패 - 실제로는 상품이 0개인 것으로 판단하여 이동 작업을 스킵합니다.")
                    logger.info("등록C 그룹에 실제로는 상품이 없으므로 이동 작업을 스킵합니다.")

            # 1-1. 대기3 그룹을 선택해 상품 검색
            logger.info("1-1. 대기3 그룹을 선택해 상품 검색")
            if not self.dropdown_manager.select_group_in_management_screen("대기3"):
                logger.error("대기3 그룹 선택 실패")
                return False
            
            # 1-1-1. 대기3 그룹의 상품 수 확인
            logger.info("1-1-1. 대기3 그룹의 상품 수 확인")
            daegi3_product_count = self._get_product_count_in_group("대기3")
            logger.info(f"대기3 그룹의 총 상품수: {daegi3_product_count}개")
            
            if daegi3_product_count <= 0:
                logger.info("대기3 그룹에 상품이 없으므로 배치 작업을 종료합니다.")
                # 종료 이유를 설정하여 상위 배치 루프에서 조기 종료할 수 있도록 함
                self._last_termination_reason = 'no_products_in_daegi3'
                return True  # 상품이 없는 것은 정상적인 상황이므로 True 반환
            
            logger.info(f"대기3 그룹에 {daegi3_product_count}개 상품이 있으므로 배치 작업을 진행합니다.")
            
            # 1-2. 첫번째 상품 등록C로 이동하기
            logger.info("1-2. 첫번째 상품 등록C로 이동하기")
            if not self.dropdown_manager.move_product_to_group("등록C", product_index=0):
                logger.error("첫번째 상품 등록C 이동 실패")
                return False
            
            # 상품 이동 후 UI 안정화를 위한 지연
            logger.info(f"상품 이동 후 UI 안정화 대기 ({timesleep.DELAY_MEDIUM}초)")
            time.sleep(timesleep.DELAY_MEDIUM)

            # 1-3. 등록C 그룹을 선택해 상품 검색 (동적 대기)
            logger.info("1-3. 등록C 그룹을 선택해 상품 검색 (동적 대기)")
            if not self.dropdown_manager.select_group_in_management_screen("등록C"):
                logger.error("등록C 그룹 선택 실패")
                return False
            
            # 등록C 그룹에 상품이 나타날 때까지 동적 대기
            logger.info("등록C 그룹에 상품이 나타날 때까지 동적 대기 시작")
            initial_product_count = self._wait_for_product_in_group("등록C", expected_count=1, max_wait_time=15)
            
            if initial_product_count == 1:
                logger.info(f"등록C 그룹의 총 상품수가 1개로 확인됨 (동적 대기 완료)")
            elif initial_product_count > 0:
                logger.warning(f"등록C 그룹의 총 상품수가 {initial_product_count}개임 (예상: 1개)")
            else:
                logger.error("등록C 그룹의 상품수 확인 실패 (동적 대기 시간 초과)")
                return False
            
            # 초기 상품수를 인스턴스 변수로 저장
            self.initial_product_count = initial_product_count
            
            # 1-4. 첫번째 상품 클릭해 수정화면 모달창 열기
            logger.info("1-4. 첫번째 상품 클릭해 수정화면 모달창 열기")

            if not self._click_first_product():
                logger.error("첫번째 상품 클릭 실패")
                return False
            
            # 1-5. 메모편집 모달창 열기
            logger.info("1-5. 메모편집 모달창 열기")

            if not smart_click(self.driver, UI_ELEMENTS["MEMO_MODAL_OPEN"], DELAY_SHORT):
                logger.error("메모편집 모달창 열기 실패")
                return False
            
            # 1-6. 상품 목록에 메모 내용 노출하기 체크박스 상태 확인
            logger.info("1-6. 상품 목록에 메모 내용 노출하기 체크박스 상태 확인")
            try:
                # 체크박스 요소 찾기
                checkbox_selector = UI_ELEMENTS["MEMO_MODAL_CHECKBOX"]["dom_selector"]
                checkbox_element = self.driver.find_element(By.XPATH, checkbox_selector)
                
                # 부모 요소 찾기 (체크 상태가 부모 label 클래스에 표시됨)
                parent_element = checkbox_element.find_element(By.XPATH, "./ancestor::label")
                
                # 체크 상태 확인 (ant-checkbox-wrapper-checked 클래스가 있는지 확인)
                is_checked = "ant-checkbox-wrapper-checked" in parent_element.get_attribute("class")
                
                if is_checked:
                    logger.info("상품 목록에 메모 내용 노출하기가 이미 체크되어 있음. 클릭하지 않음")
                else:
                    logger.info("상품 목록에 메모 내용 노출하기가 체크되지 않음. 클릭 시도")
                    smart_click(self.driver, UI_ELEMENTS["MEMO_MODAL_CHECKBOX"], DELAY_VERY_SHORT2)
            except Exception as e:
                logger.warning(f"체크박스 상태 확인 중 오류 발생: {e}. 기본적으로 클릭 시도")
                # 오류 발생 시 일단 클릭 시도
                smart_click(self.driver, UI_ELEMENTS["MEMO_MODAL_CHECKBOX"], DELAY_VERY_SHORT2)
            
            # 1-7. 메모 저장 버튼 클릭
            logger.info("1-7. 메모 저장 버튼 클릭")

            smart_click(self.driver, UI_ELEMENTS["MEMO_MODAL_SAVEBUTTON"], DELAY_VERY_SHORT)
            
            # 1-8. 옵션 탭 선택 (하이브리드방식)
            logger.info("1-8. 옵션 탭 선택 (하이브리드방식)")
            
            # HumanLikeDelay 적용 - 옵션 탭 선택 전 
            pre_tab_delay = HumanLikeDelay(min_total_delay=1.8, max_total_delay=3.8, current_speed=0.8) 
            applied_delay = pre_tab_delay.get_delay() 
            logger.info(f"옵션 탭 선택 전 Human Delay 적용: {applied_delay:.2f}초") 
            time.sleep(applied_delay)

            smart_click(self.driver, UI_ELEMENTS["PRODUCT_TAB_OPTION"], DELAY_MEDIUM)
            
            # 옵션 상품 여부를 먼저 확인
            is_option_product = self._check_if_option_product()
            
            # 옵션 상품인 경우에만 AI 옵션명 다듬기 버튼으로 탭 활성화 확인
            if is_option_product:
                self.wait_for_tab_active("PRODUCT_TAB_OPTION")
            else:
                # 단일 상품인 경우 간단히 대기
                logger.info("단일 상품 - 옵션 탭 활성화 대기 스킵")
                time.sleep(1)
            
            if is_option_product:
                # 1-9. AI 옵션명 다듬기 클릭 (옵션 상품인 경우에만)
                logger.info("1-9. AI 옵션명 다듬기 클릭 (하이브리드방식) - 옵션 상품 확인됨")
                
                # AI 옵션명 다듬기 전 휴먼 지연 적용
                ai_delay = HumanLikeDelay(min_total_delay=1.5, max_total_delay=3, current_speed=0.8)
                pre_ai_delay = ai_delay.get_delay('critical')
                logger.info(f"AI 옵션명 다듬기 전 휴먼 지연: {pre_ai_delay:.2f}초")
                time.sleep(pre_ai_delay)

                smart_click(self.driver, UI_ELEMENTS["PRODUCT_OPTION_AI"], DELAY_VERY_SHORT)
                
                # AI 옵션명 다듬기 완료 대기
                logger.info("AI 옵션명 다듬기 완료 대기 중...")
                self._wait_for_ai_option_processing_complete()

                # 1-10. 옵션명 접두어로 숫자 추가 버튼 클릭 (옵션 상품인 경우에만)
                logger.info("1-10. 옵션명 접두어로 숫자 추가 버튼 클릭 (하이브리드방식) - 옵션 상품 확인됨")

                smart_click(self.driver, UI_ELEMENTS["PRODUCT_OPTION_NUMBER"], DELAY_VERY_SHORT)
            else:
                logger.info("1-9, 1-10 단계 스킵 - 단일 상품으로 확인됨 (옵션 없음)")

            # 1-11. 상품복사하기 1회 진행
            logger.info("1-11. 상품복사하기 첫번째 진행")

            smart_click(self.driver, UI_ELEMENTS["PRODUCT_COPY_BUTTON"], DELAY_MEDIUM)
            self.wait_for_tab_active("PRODUCT_COPY_BUTTON")
                                         
            # 1-12. 상품명 탭 선택
            logger.info("1-12. 상품명 탭 선택 (하이브리드방식)")
            
            # 상품명 탭 선택 전 휴먼 지연 적용
            basic_tab_delay = HumanLikeDelay(min_total_delay=1.5, max_total_delay=3.5, current_speed=0.8)
            pre_basic_tab_delay = basic_tab_delay.get_delay('transition')
            logger.info(f"상품명 탭 선택 전 휴먼 지연: {pre_basic_tab_delay:.2f}초")
            time.sleep(pre_basic_tab_delay)

            smart_click(self.driver, UI_ELEMENTS["PRODUCT_TAB_BASIC"], DELAY_MEDIUM)
            self.wait_for_tab_active("PRODUCT_TAB_BASIC")
       
            # 1-13. 상품복사하기 1회 진행
            logger.info("1-13. 상품복사하기 두번째 진행")

            smart_click(self.driver, UI_ELEMENTS["PRODUCT_COPY_BUTTON"], DELAY_VERY_SHORT)
            self.wait_for_tab_active("PRODUCT_COPY_BUTTON")

            # 1-14. 상품명 TEXTAREA 클릭
            logger.info("1-14. 상품명 TEXTAREA 클릭 (하이브리드방식)")
            
            # 상품명 편집 전 휴먼 지연 적용
            name_edit_delay = HumanLikeDelay(min_total_delay=1, max_total_delay=2.5, current_speed=0.8)
            pre_name_edit_delay = name_edit_delay.get_delay('transition')
            logger.info(f"상품명 편집 전 휴먼 지연: {pre_name_edit_delay:.2f}초")
            time.sleep(pre_name_edit_delay)
            
            smart_click(self.driver, UI_ELEMENTS["PRODUCT_NAMEEDIT_TEXTAREA"], DELAY_VERY_SHORT)
            
            # 1-15. 기존의 상품명에 E열(suffixA3)의 접미사 추가
            logger.info("1-15. 기존의 상품명에 E열(suffixA3)의 접미사 추가")
            try:
                # Excel에서 접미사 가져오기
                suffix_a3 = self._get_suffix_from_excel('suffixA3', account_id)
                if suffix_a3:
                    # 첫 번째 원본 상품: 엑셀 접미사만 공백과 함께 추가
                    logger.info(f"첫 번째 원본 상품에 Excel 접미사 '{suffix_a3}' 추가")
                    self._add_suffix_to_product_name(suffix_a3, remove_copy_suffix=False)
                    logger.info(f"Excel 접미사 '{suffix_a3}' 추가 완료")
                else:
                    logger.warning("Excel에서 접미사를 가져올 수 없습니다. 첫 번째 원본 상품은 접미사 없이 진행합니다.")
            except Exception as e:
                logger.error(f"상품명 접미사 추가 중 오류: {e}")
                logger.warning("첫 번째 원본 상품은 접미사 없이 진행합니다.")

            # 1-16. 상품복사하기 1회 진행
            logger.info("1-16. 상품복사하기 세번째 진행")

            smart_click(self.driver, UI_ELEMENTS["PRODUCT_COPY_BUTTON"], DELAY_VERY_SHORT)
            self.wait_for_tab_active("PRODUCT_COPY_BUTTON")

            # 1-17. 가격 탭 선택
            logger.info("1-17. 가격 탭 선택 (하이브리드방식)")
            
            # 가격 탭 선택 전 휴먼 지연 적용
            price_tab_delay = HumanLikeDelay(min_total_delay=1.5, max_total_delay=3.5, current_speed=0.8)
            pre_price_tab_delay = price_tab_delay.get_delay('transition')
            logger.info(f"가격 탭 선택 전 휴먼 지연: {pre_price_tab_delay:.2f}초")
            time.sleep(pre_price_tab_delay)

            smart_click(self.driver, UI_ELEMENTS["PRODUCT_TAB_PRICE"], DELAY_MEDIUM)
            self.wait_for_tab_active("PRODUCT_TAB_PRICE")

            # 1-18. 마켓 표시 할인율 입력 입력창 선택
            logger.info("1-18. 마켓 표시 할인율 입력 입력창 선택")
            
            # 할인율 입력 전 휴먼 지연 적용
            discount_delay = HumanLikeDelay(min_total_delay=1, max_total_delay=2.5, current_speed=0.8)
            pre_discount_delay = discount_delay.get_delay('transition')
            logger.info(f"할인율 입력 전 휴먼 지연: {pre_discount_delay:.2f}초")
            time.sleep(pre_discount_delay)
            
            # smart_click(self.driver, UI_ELEMENTS["PRODUCT_PRICE_DISCOUNTRATE1"], DELAY_VERY_SHORT)
            smart_click_with_focus(self.driver, UI_ELEMENTS["PRODUCT_PRICE_DISCOUNTRATE"], DELAY_VERY_SHORT)
                       
            # 1-19. 새로운 할인율 입력
            logger.info("1-19. 새로운 할인율 입력 시작")
            discount_rate = self._get_discount_rate_for_product(self.current_product_index)
            self._set_discount_rate(discount_rate)

            # 1-19-1. 썸네일 탭 선택하여 썸네일 개수 확인 및 저장
            logger.info("1-19-1. 썸네일 탭 선택하여 썸네일 개수 확인")
            
            # 썸네일 탭 선택 전 휴먼 지연 적용
            thumbnail_tab_delay = HumanLikeDelay(min_total_delay=1.5, max_total_delay=3, current_speed=0.8)
            pre_thumbnail_tab_delay = thumbnail_tab_delay.get_delay('transition')
            logger.info(f"썸네일 탭 선택 전 휴먼 지연: {pre_thumbnail_tab_delay:.2f}초")
            time.sleep(pre_thumbnail_tab_delay)
            
            smart_click(self.driver, UI_ELEMENTS["PRODUCT_TAB_THUMBNAIL"], DELAY_MEDIUM)
            self.wait_for_tab_active("PRODUCT_TAB_THUMBNAIL")
            
            # 썸네일 개수 확인 및 저장
            self.thumbnail_count = self._get_thumbnail_count_from_tab()
            logger.info(f"원본 상품의 썸네일 개수: {self.thumbnail_count}개")
            
            # 1-19-2. TAB 키 디버깅용 추가 (Selenium 방식)
            logger.info("1-19-2. TAB 키 디버깅용 추가 (Selenium 방식)")
            try:
                # 현재 활성 요소에서 TAB 키 입력
                active_element = self.driver.switch_to.active_element
                active_element.send_keys(Keys.TAB)
                time.sleep(0.5)
                logger.info("Selenium TAB 키 입력 완료")
            except Exception as e:
                logger.error(f"Selenium TAB 키 입력 실패, 폴백 사용: {e}")
                self.keyboard.tab_key()
                time.sleep(0.5)
            
            # 1-20. 상품수정 모달창 나가기
            logger.info("1-20. 상품수정 모달창 나가기 (ESC 키로 나가기)")
            try:
                # 방법 1: body에 포커스를 주고 ESC 키 시도
                logger.info("body 요소에 포커스를 주고 ESC 키로 모달창 닫기 시도")
                self.driver.execute_script("document.body.focus();")
                time.sleep(0.5)
                self.keyboard.escape_key()
                time.sleep(2)
                
                # 모달창이 닫혔는지 확인
                modal_closed = self._check_modal_closed()
                if modal_closed:
                    logger.info("상품수정 모달창이 성공적으로 닫혔습니다.")
                else:
                    logger.warning("ESC 키로 모달창이 닫히지 않음, 모달창 바깥 영역 클릭 시도")
                    
                    # 방법 2: 모달창 바깥 영역 클릭
                    try:
                        # 모달창 바깥 영역 (화면 좌상단) 클릭
                        self.driver.execute_script("""
                            var event = new MouseEvent('click', {
                                view: window,
                                bubbles: true,
                                cancelable: true,
                                clientX: 50,
                                clientY: 50
                            });
                            document.body.dispatchEvent(event);
                        """)
                        time.sleep(1)
                        
                        # 다시 모달창 확인
                        modal_closed = self._check_modal_closed()
                        if modal_closed:
                            logger.info("모달창 바깥 영역 클릭으로 모달창이 닫혔습니다.")
                        else:
                            logger.warning("모달창 바깥 영역 클릭으로도 모달창이 닫히지 않음")
                            # 한 번 더 ESC 시도
                            self.keyboard.escape_key()
                            time.sleep(1)
                    except Exception as click_error:
                        logger.error(f"모달창 바깥 영역 클릭 중 오류: {click_error}")
                        
            except Exception as e:
                logger.error(f"모달창 닫기 중 오류: {e}")

            # 1-21. 등록실행 그룹을 선택해 상품 검색
            logger.info("1-19. 등록실행 그룹을 선택해 상품 검색")
            if not self.dropdown_manager.select_group_in_management_screen("등록실행"):
                logger.error("등록실행 그룹 선택 실패")
                return False
            
            # 1-22. 등록C 그룹 재선택하여 UI 새로고침
            logger.info("1-22. 등록C 그룹 재선택하여 UI 새로고침")
            if not self.dropdown_manager.select_group_in_management_screen("등록C"):
                logger.error("등록C 그룹 재선택 실패")
                return False
            
            # 1-23. 복사된 상품 수 확인 및 처리
            logger.info("1-23. 복사된 상품 수 확인 및 처리")
            if not self._verify_copied_products_count():
                logger.info("복사한 상품수가 부족해서 최적화작업을 중단하고, 다음 상품 최적화를 진행합니다")
                return False

            # 복사된 상품들 최적화
            self._optimize_copied_products(account_id)
            
            return True
            
        except Exception as e:
            logger.error(f"상품 복제 및 최적화 프로세스 중 오류: {e}")
            return False
    
    def _get_thumbnail_count_from_tab(self):
        """
        썸네일 탭에서 '총 X개의 썸네일' 텍스트를 읽어서 썸네일 개수 확인
        
        Returns:
            int: 썸네일 개수 (실패 시 0)
        """
        try:
            # '총 X개의 썸네일' 텍스트를 찾는 선택자
            thumbnail_count_selectors = [
                "//span[contains(text(), '총') and contains(text(), '개의 썸네일')]",
                "//div[contains(@class, 'ant-col')]//span[contains(text(), '썸네일')]",
                "//span[contains(@class, 'Body2Medium14') and contains(text(), '썸네일')]"
            ]
            
            for selector in thumbnail_count_selectors:
                try:
                    element = self.driver.find_element(By.XPATH, selector)
                    text = element.text
                    logger.info(f"썸네일 개수 텍스트 발견: '{text}'")
                    
                    # 텍스트에서 숫자 추출 (예: '총 5개의 썸네일' -> 5)
                    import re
                    match = re.search(r'총\s*(\d+)개의\s*썸네일', text)
                    if match:
                        count = int(match.group(1))
                        logger.info(f"썸네일 개수 추출 성공: {count}개")
                        return count
                except Exception as e:
                    logger.warning(f"선택자 '{selector}' 실패: {e}")
                    continue
            
            logger.warning("썸네일 개수 텍스트를 찾을 수 없습니다")
            return 0
            
        except Exception as e:
            logger.error(f"썸네일 개수 확인 중 오류: {e}")
            return 0
    
    def _verify_copied_products_count(self):
        """
        복사된 상품 수가 정확한지 확인하고 처리
        - 등록C 그룹의 상품 수가 초기 상품 수 + 3개인지 확인
        - 그렇지 않으면 모든 상품을 복제X 그룹으로 이동
        
        Returns:
            bool: 성공 여부
        """
        try:
            # 현재 등록C 그룹의 상품 수 확인
            current_count = self.dropdown_manager.get_product_count()
            expected_count = self.initial_product_count + 3
            
            logger.info(f"초기 상품 수: {self.initial_product_count}")
            logger.info(f"현재 상품 수: {current_count}")
            logger.info(f"예상 상품 수: {expected_count}")
            
            if current_count == 4:
                logger.info("상품 복사가 정상적으로 완료되었습니다. (3개 증가 확인)")
                return True
            else:
                logger.warning(f"상품 복사가 정상적으로 완료되지 않았습니다. 현재: {current_count}, 예상: 4개")
                logger.info("네트워크 등의 이유로 상품수가 4개가 되지 않았습니다. 모든 상품을 복제X 그룹으로 이동합니다.")
                
                # 모든 상품을 복제X 그룹으로 이동
                if self.dropdown_manager.move_products_to_group("복제X"):
                    logger.info("모든 상품이 복제X 그룹으로 성공적으로 이동되었습니다.")
                    return False  # 복사 실패로 처리하여 다음 단계 진행하지 않음
                else:
                    logger.error("상품을 복제X 그룹으로 이동하는데 실패했습니다.")
                    return False
                    
        except Exception as e:
            logger.error(f"복사된 상품 수 확인 중 오류: {e}")
            return False
    
    def _optimize_copied_products(self, account_id):
        """
        복사된 상품들을 최적화하는 함수
        
        Args:
            account_id (str): 계정 ID
        """
        # 복사상품 처리를 위해 인덱스를 1로 설정 (첫번째 복사상품)
        self.current_product_index = 1
        logger.info(f"복사상품 최적화 시작 - current_product_index: {self.current_product_index}")
        
        # 첫번째 복사상품 최적화
        self._optimize_first_copied_product(account_id)
        
        # 두번째 복사상품 최적화 - 인덱스 증가
        self.current_product_index = 2
        self._optimize_second_copied_product(account_id)
        
        # 세번째 복사상품 최적화 - 인덱스 증가
        self.current_product_index = 3
        self._optimize_third_copied_product(account_id)
        
        # 원본상품 그룹이동
        self._move_original_product_to_group()
    
    def _optimize_first_copied_product(self, account_id):
        """
        첫번째 복사상품 최적화
        
        Args:
            account_id (str): 계정 ID
        """
        logger.info("\n\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        logger.info("!!! 첫번째 복사상품 최적화하기 !!!")
        logger.info("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n")
        
        try:
            # 2-1. 첫번째 상품 클릭해 수정화면 모달창 열기
            logger.info("2-1. 첫번째 상품 클릭해 수정화면 모달창 열기")

            self._click_first_product()
            
            # 2-2. 상품명 TEXTAREA 클릭
            logger.info("2-2. 상품명 TEXTAREA 클릭 (하이브리드방식)")
            smart_click(self.driver, UI_ELEMENTS["PRODUCT_NAMEEDIT_TEXTAREA"], DELAY_VERY_SHORT)
            
            # 2-3. 기존의 상품명에 H열(suffixB3)의 접미사 추가
            logger.info("2-3. 기존의 상품명에 H열(suffixB3)의 접미사 추가")
            try:
                # Excel에서 접미사 가져오기
                suffix_b3 = self._get_suffix_from_excel('suffixB3', account_id)
                if suffix_b3:
                    # 첫 번째 복사 상품: 백스페이스 3번으로 " (1)" 제거 후 엑셀 접미사 추가
                    logger.info(f"첫 번째 복사 상품에 Excel 접미사 '{suffix_b3}' 추가 (복사 접미사 제거)")
                    self._add_suffix_to_product_name(suffix_b3, remove_copy_suffix=True, copy_number=1)
                    logger.info(f"Excel 접미사 '{suffix_b3}' 추가 완료")
                else:
                    logger.warning("Excel에서 suffixB3를 가져올 수 없습니다. 첫 번째 복사 상품은 접미사 없이 진행합니다.")
            except Exception as e:
                logger.error(f"첫 번째 복사 상품 접미사 추가 중 오류: {e}")
                logger.warning("첫 번째 복사 상품은 접미사 없이 진행합니다.")
            
            # 2-4. 가격 탭 선택
            logger.info("2-4. 가격 탭 선택 (하이브리드방식)")
            # HumanLikeDelay 적용 - 가격 탭 선택 전
            delay_strategy = HumanLikeDelay(min_total_delay=1.5, max_total_delay=3.0, current_speed=0.8)
            pre_action_delay = delay_strategy.get_delay('click')
            logger.info(f"가격 탭 선택 전 지연: {pre_action_delay:.2f}초")
            time.sleep(pre_action_delay)

            smart_click(self.driver, UI_ELEMENTS["PRODUCT_TAB_PRICE"], DELAY_MEDIUM)
            self.wait_for_tab_active("PRODUCT_TAB_PRICE")
            
            # 2-5. 마켓 표시 할인율 입력 입력창 선택
            logger.info("2-5. 마켓 표시 할인율 입력 입력창 선택")
            # HumanLikeDelay 적용 - 할인율 입력창 선택 전
            delay_strategy = HumanLikeDelay(min_total_delay=1.0, max_total_delay=2.5, current_speed=0.8)
            pre_action_delay = delay_strategy.get_delay('click')
            logger.info(f"할인율 입력창 선택 전 지연: {pre_action_delay:.2f}초")
            time.sleep(pre_action_delay)
            
            smart_click_with_focus(self.driver, UI_ELEMENTS["PRODUCT_PRICE_DISCOUNTRATE"], DELAY_VERY_SHORT)
            
            # 2-6. 새로운 할인율 입력
            logger.info("2-6. 새로운 할인율 입력 시작")
            discount_rate = self._get_discount_rate_for_product(self.current_product_index)
            self._set_discount_rate(discount_rate)
            
            # 2-7. 썸네일 개수 확인 후 썸네일 탭 선택 및 이동 작업 결정
            logger.info("2-7. 썸네일 개수 확인 후 썸네일 탭 선택 및 이동 작업 결정")
            # 원본 상품에서 미리 확인한 썸네일 개수 사용
            thumbnail_count = getattr(self, 'thumbnail_count', 0)
            logger.info(f"현재 썸네일 개수: {thumbnail_count}개 (원본 상품에서 확인됨)")
            
            if thumbnail_count >= 2:
                # 2-7-1. 썸네일 탭 선택
                logger.info("2-7-1. 썸네일 탭 선택 (하이브리드방식)")
                # HumanLikeDelay 적용 - 썸네일 탭 선택 전
                delay_strategy = HumanLikeDelay(min_total_delay=1.5, max_total_delay=3.0, current_speed=0.8)
                pre_action_delay = delay_strategy.get_delay('click')
                logger.info(f"썸네일 탭 선택 전 지연: {pre_action_delay:.2f}초")
                time.sleep(pre_action_delay)
                
                smart_click(self.driver, UI_ELEMENTS["PRODUCT_TAB_THUMBNAIL"], DELAY_MEDIUM)
                self.wait_for_tab_active("PRODUCT_TAB_THUMBNAIL")
                
                # 2-8. 두번째 썸네일을 맨 앞으로 이동하기
                logger.info("2-8. 두번째 썸네일을 맨 앞으로 이동하기")
                logger.info("두번째 썸네일을 맨 앞으로 이동 시도")
                thumbnail_moved = self.image_manager.move_thumbnail_to_front(1)  # 인덱스 1 = 두번째 썸네일
                if not thumbnail_moved:
                    logger.warning("두번째 썸네일 이동에 실패했습니다")
            else:
                logger.info(f"두번째 썸네일이 존재하지 않습니다 (총 {thumbnail_count}개). 썸네일 탭 선택 및 이동 작업을 모두 건너뜁니다")
            
            # 2-9. 상품수정 모달창 나가기
            logger.info("2-9. 상품수정 모달창 나가기 (ESC 키로 나가기)")
            self._close_modal_with_esc()
            
            # 2-10. 수정한 첫번째 상품을 쇼핑몰B3 그룹으로 이동하기
            logger.info("2-10. 수정한 첫번째 상품을 쇼핑몰B3 그룹으로 이동하기")
            self.dropdown_manager.move_product_to_group("쇼핑몰B3", product_index=0)
            
            # current_product_index는 _optimize_copied_products에서 관리
            
        except Exception as e:
            logger.error(f"첫번째 복사상품 최적화 중 오류: {e}")
    
    def _optimize_second_copied_product(self, account_id):
        """
        두번째 복사상품 최적화
        
        Args:
            account_id (str): 계정 ID
        """
        logger.info("\n\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        logger.info("!!! 두번째 복사상품 최적화하기 !!!")
        logger.info("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n")
        
        try:
            # 3-1. 첫번째 상품 클릭해 수정화면 모달창 열기
            logger.info("3-1. 첫번째 상품 클릭해 수정화면 모달창 열기")

            self._click_first_product()
            
            # 3-2. 상품명 TEXTAREA 클릭
            logger.info("3-2. 상품명 TEXTAREA 클릭 (하이브리드방식)")
            smart_click(self.driver, UI_ELEMENTS["PRODUCT_NAMEEDIT_TEXTAREA"], DELAY_VERY_SHORT)
            
            # 3-3. 기존의 상품명에 K열(suffixC3)의 접미사 추가
            logger.info("3-3. 기존의 상품명에 K열(suffixC3)의 접미사 추가")
            try:
                # Excel에서 접미사 가져오기
                suffix_c3 = self._get_suffix_from_excel('suffixC3', account_id)
                if suffix_c3:
                    # 두 번째 복사 상품: 백스페이스 3번으로 " (2)" 제거 후 엑셀 접미사 추가
                    logger.info(f"두 번째 복사 상품에 Excel 접미사 '{suffix_c3}' 추가 (복사 접미사 제거)")
                    self._add_suffix_to_product_name(suffix_c3, remove_copy_suffix=True, copy_number=2)
                    logger.info(f"Excel 접미사 '{suffix_c3}' 추가 완료")
                else:
                    logger.warning("Excel에서 suffixC3를 가져올 수 없습니다. 두 번째 복사 상품은 접미사 없이 진행합니다.")
            except Exception as e:
                logger.error(f"두 번째 복사 상품 접미사 추가 중 오류: {e}")
                logger.warning("두 번째 복사 상품은 접미사 없이 진행합니다.")
            
            # 3-4. 가격 탭 선택
            logger.info("3-4. 가격 탭 선택 (하이브리드방식)")
            # HumanLikeDelay 적용 - 가격 탭 선택 전
            delay_strategy = HumanLikeDelay(min_total_delay=1.5, max_total_delay=3.0, current_speed=0.8)
            pre_action_delay = delay_strategy.get_delay('click')
            logger.info(f"가격 탭 선택 전 지연: {pre_action_delay:.2f}초")
            time.sleep(pre_action_delay)

            smart_click(self.driver, UI_ELEMENTS["PRODUCT_TAB_PRICE"], DELAY_MEDIUM)
            self.wait_for_tab_active("PRODUCT_TAB_PRICE")
            
            # 3-5. 마켓 표시 할인율 입력 입력창 선택
            logger.info("3-5. 마켓 표시 할인율 입력 입력창 선택")
            # HumanLikeDelay 적용 - 할인율 입력창 선택 전
            delay_strategy = HumanLikeDelay(min_total_delay=1.0, max_total_delay=2.5, current_speed=0.8)
            pre_action_delay = delay_strategy.get_delay('click')
            logger.info(f"할인율 입력창 선택 전 지연: {pre_action_delay:.2f}초")
            time.sleep(pre_action_delay)
            
            smart_click_with_focus(self.driver, UI_ELEMENTS["PRODUCT_PRICE_DISCOUNTRATE"], DELAY_VERY_SHORT)
            
            # 3-6. 새로운 할인율 입력
            logger.info("3-6. 새로운 할인율 입력 시작")
            discount_rate = self._get_discount_rate_for_product(self.current_product_index)
            self._set_discount_rate(discount_rate)
            
            # 3-7. 썸네일 개수 확인 후 썸네일 탭 선택 및 이동 작업 결정
            logger.info("3-7. 썸네일 개수 확인 후 썸네일 탭 선택 및 이동 작업 결정")
            # 원본 상품에서 미리 확인한 썸네일 개수 사용
            thumbnail_count = getattr(self, 'thumbnail_count', 0)
            logger.info(f"현재 썸네일 개수: {thumbnail_count}개 (원본 상품에서 확인됨)")
            
            if thumbnail_count >= 3:
                # 3-7-1. 썸네일 탭 선택
                logger.info("3-7-1. 썸네일 탭 선택 (하이브리드방식)")
                # HumanLikeDelay 적용 - 썸네일 탭 선택 전
                delay_strategy = HumanLikeDelay(min_total_delay=1.5, max_total_delay=3.0, current_speed=0.8)
                pre_action_delay = delay_strategy.get_delay('click')
                logger.info(f"썸네일 탭 선택 전 지연: {pre_action_delay:.2f}초")
                time.sleep(pre_action_delay)
                
                smart_click(self.driver, UI_ELEMENTS["PRODUCT_TAB_THUMBNAIL"], DELAY_MEDIUM)
                self.wait_for_tab_active("PRODUCT_TAB_THUMBNAIL")
                
                # 3-8. 세번째 썸네일을 맨 앞으로 이동하기
                logger.info("3-8. 세번째 썸네일을 맨 앞으로 이동하기")
                logger.info("세번째 썸네일을 맨 앞으로 이동 시도")
                thumbnail_moved = self.image_manager.move_thumbnail_to_front(2)  # 인덱스 2 = 세번째 썸네일
                if not thumbnail_moved:
                    logger.warning("세번째 썸네일 이동에 실패했습니다")
            else:
                logger.info(f"세번째 썸네일이 존재하지 않습니다 (총 {thumbnail_count}개). 썸네일 탭 선택 및 이동 작업을 모두 건너뜁니다")

            # 3-8-1. 썸네일탭 중앙 클릭(포커스용) - 주석 처리
            # logger.info("3-8-1. 썸네일탭 중앙 클릭(포커스용)")
            # smart_click(self.driver, UI_ELEMENTS["THUMBNAIL_CLICK_CENTER"], DELAY_VERY_SHORT)


            # 3-9. 상품수정 모달창 나가기
            logger.info("3-9. 상품수정 모달창 나가기 (ESC 키로 나가기)")
            self._close_modal_with_esc()
            
            # 3-10. 수정한 첫번째 상품을 쇼핑몰C3 그룹으로 이동하기
            logger.info("3-10. 수정한 첫번째 상품을 쇼핑몰C3 그룹으로 이동하기")
            self.dropdown_manager.move_product_to_group("쇼핑몰C3", product_index=0)
            
            # current_product_index는 _optimize_copied_products에서 관리
            
        except Exception as e:
            logger.error(f"두번째 복사상품 최적화 중 오류: {e}")
    
    def _optimize_third_copied_product(self, account_id):
        """
        세번째 복사상품 최적화
        
        Args:
            account_id (str): 계정 ID
        """
        logger.info("\n\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        logger.info("!!! 세번째 복사상품 최적화하기 !!!")
        logger.info("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n")
        
        try:
            # 4-1. 첫번째 상품 클릭해 수정화면 모달창 열기
            logger.info("4-1. 첫번째 상품 클릭해 수정화면 모달창 열기")

            self._click_first_product()
            
            # 4-2. 상품명 TEXTAREA 클릭
            logger.info("4-2. 상품명 TEXTAREA 클릭 (하이브리드방식)")
            smart_click(self.driver, UI_ELEMENTS["PRODUCT_NAMEEDIT_TEXTAREA"], DELAY_VERY_SHORT)
            
            # 4-3. 기존의 상품명에 N열(suffixD3)의 접미사 추가
            logger.info("4-3. 기존의 상품명에 N열(suffixD3)의 접미사 추가")
            try:
                # Excel에서 접미사 가져오기
                suffix_d1 = self._get_suffix_from_excel('suffixD3', account_id)
                if suffix_d1:
                    # 세 번째 복사 상품: 백스페이스 3번으로 " (3)" 제거 후 엑셀 접미사 추가
                    logger.info(f"세 번째 복사 상품에 Excel 접미사 '{suffix_d1}' 추가 (복사 접미사 제거)")
                    self._add_suffix_to_product_name(suffix_d1, remove_copy_suffix=True, copy_number=3)
                    logger.info(f"Excel 접미사 '{suffix_d1}' 추가 완료")
                else:
                    logger.warning("Excel에서 suffixD3를 가져올 수 없습니다. 세 번째 복사 상품은 접미사 없이 진행합니다.")
            except Exception as e:
                logger.error(f"세 번째 복사 상품 접미사 추가 중 오류: {e}")
                logger.warning("세 번째 복사 상품은 접미사 없이 진행합니다.")
            
            # 4-4. 가격 탭 선택
            logger.info("4-4. 가격 탭 선택 (하이브리드방식)")
            # HumanLikeDelay 적용 - 가격 탭 선택 전
            delay_strategy = HumanLikeDelay(min_total_delay=1.5, max_total_delay=3.0, current_speed=0.8)
            pre_action_delay = delay_strategy.get_delay('click')
            logger.info(f"가격 탭 선택 전 지연: {pre_action_delay:.2f}초")
            time.sleep(pre_action_delay)

            smart_click(self.driver, UI_ELEMENTS["PRODUCT_TAB_PRICE"], DELAY_MEDIUM)
            self.wait_for_tab_active("PRODUCT_TAB_PRICE")
            
            # 4-5. 마켓 표시 할인율 입력 입력창 선택
            logger.info("4-5. 마켓 표시 할인율 입력 입력창 선택")
            # HumanLikeDelay 적용 - 할인율 입력창 선택 전
            delay_strategy = HumanLikeDelay(min_total_delay=1.0, max_total_delay=2.5, current_speed=0.8)
            pre_action_delay = delay_strategy.get_delay('click')
            logger.info(f"할인율 입력창 선택 전 지연: {pre_action_delay:.2f}초")
            time.sleep(pre_action_delay)
            
            smart_click_with_focus(self.driver, UI_ELEMENTS["PRODUCT_PRICE_DISCOUNTRATE"], DELAY_VERY_SHORT)
            
            # 4-6. 새로운 할인율 입력
            logger.info("4-6. 새로운 할인율 입력 시작")
            discount_rate = self._get_discount_rate_for_product(self.current_product_index)
            self._set_discount_rate(discount_rate)
            
            # 4-7. 썸네일 개수 확인 후 썸네일 탭 선택 및 이동 작업 결정
            logger.info("4-7. 썸네일 개수 확인 후 썸네일 탭 선택 및 이동 작업 결정")
            # 원본 상품에서 미리 확인한 썸네일 개수 사용
            thumbnail_count = getattr(self, 'thumbnail_count', 0)
            logger.info(f"현재 썸네일 개수: {thumbnail_count}개 (원본 상품에서 확인됨)")
            
            if thumbnail_count >= 4:
                # 4-7-1. 썸네일 탭 선택
                logger.info("4-7-1. 썸네일 탭 선택 (하이브리드방식)")
                # HumanLikeDelay 적용 - 썸네일 탭 선택 전
                delay_strategy = HumanLikeDelay(min_total_delay=1.5, max_total_delay=3.0, current_speed=0.8)
                pre_action_delay = delay_strategy.get_delay('click')
                logger.info(f"썸네일 탭 선택 전 지연: {pre_action_delay:.2f}초")
                time.sleep(pre_action_delay)
                
                smart_click(self.driver, UI_ELEMENTS["PRODUCT_TAB_THUMBNAIL"], DELAY_MEDIUM)
                self.wait_for_tab_active("PRODUCT_TAB_THUMBNAIL")
                
                # 4-8. 네번째 썸네일을 맨 앞으로 이동하기
                logger.info("4-8. 네번째 썸네일을 맨 앞으로 이동하기")
                logger.info("네번째 썸네일을 맨 앞으로 이동 시도")
                thumbnail_moved = self.image_manager.move_thumbnail_to_front(3)  # 인덱스 3 = 네번째 썸네일
                if not thumbnail_moved:
                    logger.warning("네번째 썸네일 이동에 실패했습니다")
            else:
                logger.info(f"네번째 썸네일이 존재하지 않습니다 (총 {thumbnail_count}개). 썸네일 탭 선택 및 이동 작업을 모두 건너뜁니다")
            
            # 4-9. 상품수정 모달창 나가기
            logger.info("4-9. 상품수정 모달창 나가기 (ESC 키로 나가기)")
            self._close_modal_with_esc()
            
            # 4-10. 수정한 첫번째 상품을 쇼핑몰D3 그룹으로 이동하기
            logger.info("4-10. 수정한 첫번째 상품을 쇼핑몰D3 그룹으로 이동하기")
            self.dropdown_manager.move_product_to_group("쇼핑몰D3", product_index=0)
            
            # current_product_index는 _optimize_copied_products에서 관리
            
        except Exception as e:
            logger.error(f"세번째 복사상품 최적화 중 오류: {e}")
    
    def _move_original_product_to_group(self):
        """
        원본 상품을 쇼핑몰A3 그룹으로 이동
        """
        logger.info("\n\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        logger.info("!!! 원본상품 그룹이동하기 !!!")
        logger.info("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n")
        
        try:
            # 5. 원본 상품을 쇼핑몰A3 그룹으로 이동하기
            logger.info("5. 원본 상품을 쇼핑몰A3 그룹으로 이동하기")
            self.dropdown_manager.move_product_to_group("쇼핑몰A3", product_index=0)
            
        except Exception as e:
            logger.error(f"원본상품 그룹이동 중 오류: {e}")
    
    def _navigate_to_group_management(self):
        """그룹상품관리 화면으로 이동"""
        try:
            logger.info("그룹상품관리 화면으로 이동 시도")
            
            # MenuClicks 클래스를 사용하여 그룹상품관리 메뉴 클릭
            from menu_clicks import MenuClicks
            menu_clicks = MenuClicks(self.driver)
            
            if menu_clicks.click_group_management():
                logger.info("그룹상품관리 메뉴 클릭 성공")
                # 화면 로딩 대기
                time.sleep(3.0)
                logger.info("그룹상품관리 화면 이동 완료")
            else:
                logger.error("그룹상품관리 메뉴 클릭 실패")
                return False
                
        except Exception as e:
            logger.error(f"그룹상품관리 화면 이동 중 오류: {e}")
            return False
    
    def _wait_for_group_management_loaded(self, max_retries=10):
        """
        그룹상품관리 화면이 완전히 로딩될 때까지 대기
        총상품수가 표시되는지 확인하여 로딩 완료 여부 판단
        
        Args:
            max_retries (int): 최대 재시도 횟수 (기본값: 10)
            
        Returns:
            bool: 로딩 성공 시 True, 실패 시 False
        """
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import TimeoutException
        
        # 총상품수 DOM 선택자 (스타일 속성으로 찾기)
        total_count_selector = "span[style*='padding-left: 16px']"
        
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"그룹상품관리 화면 로딩 확인 시도 {attempt}/{max_retries}")
                
                # 총상품수 요소가 나타날 때까지 최대 5초 대기
                wait = WebDriverWait(self.driver, 5)
                element = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, total_count_selector))
                )
                
                # 요소의 텍스트가 "총 X개 상품" 형태인지 확인
                element_text = element.text.strip()
                if "총" in element_text and "개 상품" in element_text:
                    logger.info(f"그룹상품관리 화면 로딩 완료 확인: {element_text}")
                    return True
                else:
                    logger.warning(f"총상품수 요소는 찾았지만 예상 형태가 아님: {element_text}")
                    
            except TimeoutException:
                logger.warning(f"시도 {attempt}: 총상품수 요소를 찾을 수 없음")
            except Exception as e:
                logger.warning(f"시도 {attempt}: 예외 발생 - {e}")
            
            # 마지막 시도가 아니면 화면 새로고침 후 재시도
            if attempt < max_retries:
                logger.info("화면 새로고침 후 재시도")
                try:
                    self.driver.refresh()
                    time.sleep(3)  # 새로고침 후 로딩 대기
                except Exception as e:
                    logger.error(f"화면 새로고침 중 오류: {e}")
        
        logger.error(f"그룹상품관리 화면 로딩 확인 실패 (최대 {max_retries}회 시도)")
        return False
    
    def _check_if_option_product(self):
        """
        현재 상품이 옵션 상품인지 확인하는 함수
        
        Returns:
            bool: 옵션 상품 여부 (True: 옵션 상품, False: 단일 상품)
        """
        try:
            # 옵션 상품등록 라벨에서 checked 상태인지 확인 (XPath 사용)
            option_product_xpath = "//label[.//span[contains(text(), '옵션 상품등록')]]//span[contains(@class, 'ant-radio-button-checked')]"
            
            option_elements = self.driver.find_elements(By.XPATH, option_product_xpath)
            
            if option_elements:
                logger.info("옵션 상품으로 확인됨 - AI 옵션명 다듬기 및 옵션명 접두어 추가 실행")
                return True
            else:
                logger.info("단일 상품으로 확인됨 - AI 옵션명 다듬기 및 옵션명 접두어 추가 스킵")
                return False
                
        except Exception as e:
            logger.warning(f"옵션 상품 여부 확인 중 오류: {e} - 기본값으로 옵션 상품으로 처리")
            return True  # 오류 시 안전하게 옵션 상품으로 처리
    
    def _wait_for_ai_option_processing_complete(self):
        """AI 옵션명 다듬기 처리 완료 대기"""
        max_wait_time = 30  # 최대 30초 대기
        check_interval = 0.5  # 0.5초마다 확인
        start_time = time.time()
        
        logger.info("AI 옵션명 다듬기 처리 완료 대기 시작")
        
        while time.time() - start_time < max_wait_time:
            try:
                # 처리 중 상태를 나타내는 div 요소 확인
                processing_div = self.driver.find_elements(By.CSS_SELECTOR, 
                    'button[class*="ant-btn"] div[style*="position: absolute"][style*="left: 0px"][style*="top:"]')
                
                if not processing_div:
                    # 처리 중 div가 사라지면 완료된 것으로 판단
                    logger.info("AI 옵션명 다듬기 처리 완료 감지")
                    time.sleep(0.5)  # 안정성을 위한 추가 대기
                    return True
                    
                logger.debug(f"AI 옵션명 다듬기 처리 중... (경과시간: {time.time() - start_time:.1f}초)")
                time.sleep(check_interval)
                
            except Exception as e:
                logger.warning(f"AI 옵션명 다듬기 상태 확인 중 오류: {e}")
                time.sleep(check_interval)
        
        # 타임아웃 발생
        logger.warning(f"AI 옵션명 다듬기 완료 대기 타임아웃 ({max_wait_time}초)")
        return False