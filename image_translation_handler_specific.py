import logging
import time
import re
import base64
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# logger를 먼저 정의
logger = logging.getLogger(__name__)

try:
    from PIL import Image
    import io
    import easyocr
    import numpy as np
    import os
    
    # EasyOCR 초기화 시도
    try:
        # EasyOCR 리더 초기화 (중문 간체만)
        easyocr_reader = easyocr.Reader(['ch_sim'], gpu=False)
        OCR_AVAILABLE = True
        logger.info(f"EasyOCR 초기화 완료 - OCR_AVAILABLE={OCR_AVAILABLE}")
    except Exception as e:
        OCR_AVAILABLE = False
        logger.warning(f"EasyOCR 초기화 실패: {e}. 속성 기반 중문글자 감지만 사용됩니다. OCR_AVAILABLE={OCR_AVAILABLE}")
        
except ImportError as e:
    OCR_AVAILABLE = False
    logger.warning(f"OCR 라이브러리가 설치되지 않음 (PIL, easyocr, numpy). 중문글자 감지 기능이 제한됩니다. OCR_AVAILABLE={OCR_AVAILABLE}")

class HumanLikeDelay:
    """
    인간과 유사한 지연 시간을 제공하는 클래스
    """
    
    @staticmethod
    def short_delay():
        """짧은 지연 (0.5-1.5초)"""
        delay = random.uniform(0.5, 1.5)
        time.sleep(delay)
    
    @staticmethod
    def medium_delay():
        """중간 지연 (1.0-3.0초)"""
        delay = random.uniform(1.0, 3.0)
        time.sleep(delay)
    
    @staticmethod
    def long_delay():
        """긴 지연 (2.0-5.0초)"""
        delay = random.uniform(2.0, 5.0)
        time.sleep(delay)
    
    @staticmethod
    def custom_delay(min_seconds, max_seconds):
        """사용자 정의 지연"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)

class ImageTranslationHandler:
    """
    이미지 번역 처리를 담당하는 클래스
    K열 처리와 관련된 모든 메서드들을 포함
    """
    
    def __init__(self, driver):
        self.driver = driver
        self.human_delay = HumanLikeDelay()
    
    def image_translate(self, action_value):
        """
        이미지 번역 처리 메인 메서드
        
        Args:
            action_value (str): 액션 값 (예: "1,2,3")
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"이미지 번역 시작: {action_value}")
            
            # 액션 파싱
            action_info = self._parse_image_translate_action(action_value)
            if not action_info:
                logger.error("이미지 번역 액션 파싱 실패")
                return False
            
            # 일괄편집 모달창 열기
            if not self._open_bulk_edit_modal():
                logger.error("일괄편집 모달창 열기 실패")
                return False
            
            try:
                # 이미지 번역 액션 처리
                success = self._process_image_translate_action(action_info)
                
                if success:
                    logger.info("이미지 번역 완료")
                else:
                    logger.error("이미지 번역 실패")
                
                return success
                
            finally:
                # 일괄편집 모달창 닫기
                self._close_bulk_edit_modal()
                
        except Exception as e:
            logger.error(f"이미지 번역 오류: {e}")
            return False
    
    def _parse_image_translate_action(self, action_value):
        """
        이미지 번역 액션 값 파싱
        
        Args:
            action_value (str): 액션 값 (예: "1,2,3" 또는 "first:1/last:1")
            
        Returns:
            dict: 파싱된 액션 정보
        """
        try:
            if not action_value or action_value.strip() == "":
                logger.warning("이미지 번역 액션 값이 비어있음")
                return None
            
            # '/' 구분자로 복합 명령어 처리
            if '/' in action_value:
                try:
                    parts = action_value.split('/')
                    combined_positions = []
                    
                    for part in parts:
                        part = part.strip()
                        if not part:
                            continue
                        
                        # 각 부분을 개별적으로 파싱
                        parsed_part = self._parse_single_translate_command(part)
                        if parsed_part and parsed_part.get('positions'):
                            combined_positions.extend(parsed_part['positions'])
                    
                    if combined_positions:
                        logger.info(f"복합 이미지 번역 명령어 파싱 완료: {action_value} -> {combined_positions}")
                        return {
                            'type': 'image_translate',
                            'positions': combined_positions
                        }
                    else:
                        logger.warning(f"복합 명령어에서 유효한 위치를 찾을 수 없음: {action_value}")
                        return None
                        
                except Exception as e:
                    logger.warning(f"복합 명령어 파싱 중 오류: {action_value}, 오류: {e}")
                    return None
            
            # 단일 명령어 파싱
            return self._parse_single_translate_command(action_value)
            
        except Exception as e:
            logger.error(f"이미지 번역 액션 파싱 오류: {e}")
            return None
    
    def _parse_single_translate_command(self, action_value):
        """
        단일 이미지 번역 명령어 파싱
        
        Args:
            action_value (str): 단일 액션 값
            
        Returns:
            dict: 파싱된 액션 정보
        """
        # 쉼표로 분리하여 이미지 위치 목록 생성
        positions = []
        for pos in action_value.split(','):
            pos = pos.strip()
            
            # 숫자인 경우
            if pos.isdigit():
                positions.append(int(pos))
            # "first:숫자" 형식인 경우 (첫 번째부터 지정된 번째까지)
            elif pos.startswith('first:'):
                try:
                    num = int(pos.split(':')[1])
                    # first:2는 1,2를 의미 (첫 번째부터 두 번째까지)
                    for i in range(1, num + 1):
                        positions.append(i)
                    logger.info(f"first 형식 파싱: {pos} -> {list(range(1, num + 1))}")
                except (IndexError, ValueError):
                    logger.warning(f"잘못된 first 형식: {pos}")
            # "last:숫자" 형식인 경우
            elif pos.startswith('last:'):
                try:
                    num = int(pos.split(':')[1])
                    positions.append(num)
                    logger.info(f"last 형식 파싱: {pos} -> {num}")
                except (IndexError, ValueError):
                    logger.warning(f"잘못된 last 형식: {pos}")
            # "specific:숫자" 형식인 경우 (특정 위치 지정)
            elif pos.startswith('specific:'):
                try:
                    value = pos.split(':')[1]
                    if value == 'all':
                        # specific:all인 경우 중문글자가 있는 이미지 자동 감지
                        logger.info("specific:all 형식 - 중문글자 이미지 자동 감지 모드")
                        positions.append('auto_detect_chinese')
                    else:
                        num = int(value)
                        positions.append(num)
                        logger.info(f"specific 형식 파싱: {pos} -> {num}")
                except (IndexError, ValueError):
                    logger.warning(f"잘못된 specific 형식: {pos}")
            else:
                logger.warning(f"잘못된 이미지 위치 값: {pos}")
        
        if not positions:
            logger.error("유효한 이미지 위치가 없음")
            return None
        
        action_info = {
            'type': 'image_translate',
            'positions': positions
        }
        
        logger.info(f"이미지 번역 액션 파싱 완료: {action_info}")
        return action_info
    
    def _process_image_translate_action(self, action_info):
        """
        이미지 번역 액션 처리
        
        Args:
            action_info (dict): 액션 정보
            
        Returns:
            bool: 성공 여부
        """
        try:
            positions = action_info.get('positions', [])
            logger.info(f"이미지 번역 처리 시작 - 위치: {positions}")
            
            # 중문글자 자동 감지 모드인 경우
            if 'auto_detect_chinese' in positions:
                logger.info("중문글자 자동 감지 모드 실행")
                detected_positions = self._detect_chinese_images()
                if detected_positions:
                    # auto_detect_chinese를 실제 감지된 위치들로 교체
                    positions = [pos for pos in positions if pos != 'auto_detect_chinese'] + detected_positions
                    logger.info(f"중문글자 감지 완료 - 번역할 이미지 위치: {detected_positions}")
                else:
                    logger.info("중문글자가 있는 이미지를 찾지 못했습니다")
                    positions = [pos for pos in positions if pos != 'auto_detect_chinese']
            
            success_count = 0
            total_count = len(positions)
            
            for position in positions:
                try:
                    logger.info(f"이미지 위치 {position} 번역 시작")
                    
                    # 편집 버튼 클릭
                    if not self._click_edit_button_by_position(position):
                        logger.error(f"이미지 위치 {position} 편집 버튼 클릭 실패")
                        continue
                    
                    # 이미지 번역 실행
                    if not self._execute_image_translation():
                        logger.error(f"이미지 위치 {position} 번역 실행 실패")
                        continue
                    
                    # 번역 완료 대기
                    if not self._wait_for_translation_complete():
                        logger.error(f"이미지 위치 {position} 번역 완료 대기 실패")
                        continue
                    
                    # 수정사항 저장
                    if not self._save_translation_changes():
                        logger.error(f"이미지 위치 {position} 수정사항 저장 실패")
                        continue
                    
                    success_count += 1
                    logger.info(f"이미지 위치 {position} 번역 성공")
                    
                except Exception as e:
                    logger.error(f"이미지 위치 {position} 번역 오류: {e}")
                    continue
            
            logger.info(f"이미지 번역 처리 완료 - 성공: {success_count}/{total_count}")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"이미지 번역 액션 처리 오류: {e}")
            return False
    
    def _click_edit_button_by_position(self, position):
        """
        위치별 편집 버튼 클릭
        
        Args:
            position (int): 이미지 위치
            
        Returns:
            bool: 성공 여부
        """
        try:
            # 편집 버튼 선택자들 (위치별) - 문서에서 확인한 정확한 DOM 구조 사용
            edit_button_selectors = [
                f"(//span[contains(@class, 'FootnoteDescription') and text()='편집하기'])[{position}]",
                f"(//div[contains(@class, 'sc-kTbCBX') or contains(@class, 'sc-gkKZNe')]//span[text()='편집하기'])[{position}]",
                f"(//div[contains(@class, 'sc-kTbCBX')]//span[contains(@class, 'FootnoteDescription') and text()='편집하기'])[{position}]",
                f"(//span[text()='편집하기'])[{position}]"
            ]
            
            for selector in edit_button_selectors:
                try:
                    edit_btn = self.driver.find_element(By.XPATH, selector)
                    if edit_btn.is_displayed():
                        # 스크롤하여 요소가 보이도록 함
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", edit_btn)
                        time.sleep(0.1)
                        
                        # 클릭 (부모 요소 클릭 시도)
                        try:
                            edit_btn.click()
                            logger.info(f"이미지 위치 {position} 편집 버튼 클릭 성공 (일반 클릭)")
                        except Exception:
                            # JavaScript 클릭 시도
                            self.driver.execute_script("arguments[0].click();", edit_btn)
                            logger.info(f"이미지 위치 {position} 편집 버튼 클릭 성공 (JavaScript 클릭)")
                        
                        self.human_delay.short_delay()  # 모달 로딩 대기
                        return True
                except Exception as e:
                    logger.debug(f"편집 버튼 선택자 {selector} 실패: {e}")
                    continue
            
            logger.error(f"이미지 위치 {position} 편집 버튼을 찾을 수 없음")
            return False
            
        except Exception as e:
            logger.error(f"이미지 위치 {position} 편집 버튼 클릭 오류: {e}")
            return False
    
    def _execute_image_translation(self):
        """
        이미지 번역 실행 (T 키 또는 버튼 클릭)
        
        Returns:
            bool: 성공 여부
        """
        try:
            # 먼저 T 키로 시도
            logger.info("T 키로 이미지 번역 시도")
            self.driver.find_element(By.TAG_NAME, "body").send_keys("t")
            self.human_delay.custom_delay(0.3, 0.7)
            
            # 번역 버튼 클릭 시도 (T 키가 작동하지 않을 경우)
            translate_button_selectors = [
                "//button//span[text()='원클릭 이미지 번역']",
                "//button[contains(@class, 'ant-btn')]//span[text()='원클릭 이미지 번역']",
                "//span[text()='원클릭 이미지 번역']/parent::button"
            ]
            
            for selector in translate_button_selectors:
                try:
                    translate_btn = self.driver.find_element(By.XPATH, selector)
                    if translate_btn.is_displayed():
                        # 스크롤하여 요소가 보이도록 함
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", translate_btn)
                        self.human_delay.custom_delay(0.1, 0.2)
                        
                        # 클릭
                        self.driver.execute_script("arguments[0].click();", translate_btn)
                        logger.info("원클릭 이미지 번역 버튼 클릭 성공")
                        return True
                except:
                    continue
            
            # T 키가 성공적으로 작동했다고 가정
            logger.info("T 키로 이미지 번역 실행")
            return True
            
        except Exception as e:
            logger.error(f"이미지 번역 실행 오류: {e}")
            return False
    
    def _wait_for_translation_complete(self):
        """
        이미지 번역 완료 대기 (동적 대기)
        최소 3초 대기 후 번역 버튼의 클래스 변화를 감지하여 번역 완료 확인
        ant-btn-loading 클래스가 있으면 번역 중, 없으면 번역 완료
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("이미지 번역 완료 대기 시작")
            
            # 최소 3초 대기 (필수)
            min_wait_time = 3.0
            logger.info(f"최소 대기 시간 {min_wait_time}초 시작")
            self.human_delay.custom_delay(2.5, 3.5)
            logger.info(f"최소 대기 시간 완료")
            
            # 번역 진행 상태를 나타내는 클래스 확인
            max_wait_time = 30  # 최대 30초 대기 (최소 대기 시간 포함)
            check_interval = 0.5  # 0.5초마다 확인
            elapsed_time = min_wait_time  # 이미 3초 대기했으므로
            
            logger.info("번역 완료 상태 동적 감지 시작")
            
            while elapsed_time < max_wait_time:
                try:
                    # 번역 중 상태 확인 (ant-btn-loading 클래스가 있는지 확인)
                    translating_buttons = self.driver.find_elements(
                        By.XPATH, 
                        "//button[contains(@class, 'ant-btn-loading')]//span[text()='원클릭 이미지 번역']"
                    )
                    
                    if translating_buttons:
                        # ant-btn-loading 클래스가 있으면 아직 번역 중
                        logger.debug(f"번역 진행 중... (경과 시간: {elapsed_time}초)")
                        self.human_delay.custom_delay(0.4, 0.6)
                        elapsed_time += check_interval
                        continue
                    else:
                        # ant-btn-loading 클래스가 없으면 번역 완료
                        # 번역 버튼이 존재하는지 확인
                        normal_buttons = self.driver.find_elements(
                            By.XPATH,
                            "//button[contains(@class, 'ant-btn') and contains(@class, 'ant-btn-default') and not(contains(@class, 'ant-btn-loading'))]//span[text()='원클릭 이미지 번역']"
                        )
                        
                        if normal_buttons:
                            logger.info(f"이미지 번역 완료 감지 (총 대기 시간: {elapsed_time}초)")
                            return True
                        else:
                            # 버튼을 찾을 수 없는 경우 일반적인 버튼 확인
                            any_buttons = self.driver.find_elements(
                                By.XPATH,
                                "//button//span[text()='원클릭 이미지 번역']"
                            )
                            if any_buttons:
                                logger.info(f"이미지 번역 완료 감지 (일반 버튼 확인, 총 대기 시간: {elapsed_time}초)")
                                return True
                    
                    self.human_delay.custom_delay(0.4, 0.6)
                    elapsed_time += check_interval
                    
                except Exception as e:
                    logger.debug(f"번역 상태 확인 중 오류: {e}")
                    self.human_delay.custom_delay(0.4, 0.6)
                    elapsed_time += check_interval
            
            # 최대 대기 시간 초과
            logger.warning(f"이미지 번역 완료 대기 시간 초과 ({max_wait_time}초)")
            return True  # 시간 초과 시에도 다음 단계 진행
            
        except Exception as e:
            logger.error(f"이미지 번역 완료 대기 오류: {e}")
            return False
    
    def _save_translation_changes(self):
        """
        수정사항 저장 버튼 클릭하여 이미지 번역 모달창 닫기
        
        Returns:
            bool: 성공 여부
        """
        try:
            # 수정사항 저장 버튼 선택자들
            save_button_selectors = [
                "//button[contains(@class, 'ant-btn-primary')]//span[text()='수정사항 저장']",
                "//button[contains(@class, 'ant-btn') and contains(@class, 'ant-btn-primary')][.//span[text()='수정사항 저장']]",
                "//span[text()='수정사항 저장']/parent::button",
                "//button[contains(@class, 'ant-btn')]//span[text()='수정사항 저장']"
            ]
            
            for selector in save_button_selectors:
                try:
                    save_btn = self.driver.find_element(By.XPATH, selector)
                    if save_btn.is_displayed():
                        # 스크롤하여 요소가 보이도록 함
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", save_btn)
                        self.human_delay.custom_delay(0.1, 0.2)
                        
                        # 동적 요소를 찾은 후 1초 지연
                        logger.info("수정사항 저장 버튼 발견, 1초 대기 후 클릭")
                        self.human_delay.short_delay()
                        
                        # 클릭
                        self.driver.execute_script("arguments[0].click();", save_btn)
                        logger.info("수정사항 저장 버튼 클릭 성공")
                        
                        # 클릭 후 1초 지연
                        logger.info("수정사항 저장 버튼 클릭 후 1초 대기")
                        self.human_delay.short_delay()
                        
                        logger.info("수정사항 저장 완료")
                        
                        return True
                except Exception as e:
                    logger.debug(f"수정사항 저장 버튼 선택자 {selector} 실패: {e}")
                    continue
            
            logger.error("수정사항 저장 버튼을 찾을 수 없음")
            return False
                
        except Exception as e:
            logger.error(f"수정사항 저장 오류: {e}")
            return False
    
    def _open_bulk_edit_modal(self):
        """
        일괄편집 모달창 열기 - PercentyImageManager3 사용 (H열과 동일한 방식)
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("상세페이지 일괄편집 모달창 열기 시작 - PercentyImageManager3 사용")
            
            # 페이지가 완전히 로드될 때까지 대기
            self.human_delay.medium_delay()
            
            # PercentyImageManager3를 사용하여 일괄편집 모달창 열기 (H열과 동일한 방식)
            try:
                from image_utils3 import PercentyImageManager3
                
                # 이미지 관리자 초기화
                image_manager = PercentyImageManager3(self.driver)
                
                # 일괄편집 모달창 열기
                if image_manager.open_bulk_edit_modal():
                    logger.info("일괄편집 모달창 열기 성공")
                else:
                    logger.error("일괄편집 모달창 열기 실패")
                    return False
                    
            except Exception as e:
                logger.error(f"PercentyImageManager3 사용 실패: {e}")
                return False
            
            # 모달창이 열렸는지 확인
            modal_selectors = [
                "//div[contains(@class, 'ant-drawer')]//span[contains(text(), '상세페이지')]",
                "//div[contains(@class, 'ant-modal')]//span[contains(text(), '상세페이지')]",
                "//div[contains(@class, 'ant-drawer-content')]",
                "//div[contains(@class, 'ant-modal-content')]",
                "//div[contains(@class, 'ant-drawer')]",
                "//div[contains(@class, 'ant-modal')]"
            ]
            
            modal_opened = False
            for i, selector in enumerate(modal_selectors):
                try:
                    logger.info(f"모달창 확인 시도 {i+1}: {selector}")
                    modal_element = WebDriverWait(self.driver, 3).until(
                        EC.visibility_of_element_located((By.XPATH, selector))
                    )
                    logger.info(f"모달창 발견 (선택자 {i+1}): {selector}")
                    modal_opened = True
                    break
                except (TimeoutException, NoSuchElementException) as e:
                    logger.warning(f"모달창 선택자 {i+1} 실패: {e}")
                    continue
                    
            if modal_opened:
                logger.info("상세페이지 이미지 모달창이 성공적으로 열렸습니다.")
                return True
            else:
                logger.error("모달창이 열리지 않았습니다.")
                return False
                
        except Exception as e:
            logger.error(f"일괄편집 모달창 열기 오류: {e}")
            return False
    
    def _close_bulk_edit_modal(self):
        """
        일괄편집 모달창 닫기 (H열과 동일한 방식 사용)
        
        Returns:
            bool: 성공 여부
        """
        try:
            import time
            from selenium.webdriver.common.action_chains import ActionChains
            from selenium.webdriver.common.keys import Keys
            
            logger.info("일괄편집 모달창 닫기 시작 - ESC 키 사용")
            
            # ESC 키로 모달창 닫기 (H열과 동일한 방식)
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            time.sleep(2.0)  # DELAY_MEDIUM과 동일
            
            logger.info("ESC 키로 모달창 닫기 완료")
            
            # 모달창이 닫혔는지 확인
            modal_selectors = [
                "//div[contains(@class, 'ant-drawer')]//span[contains(text(), '상세페이지')]",
                "//div[contains(@class, 'ant-modal')]//span[contains(text(), '상세페이지')]",
                "//div[contains(@class, 'ant-drawer-content')]",
                "//div[contains(@class, 'ant-modal-content')]"
            ]
            
            modal_found = False
            for i, selector in enumerate(modal_selectors):
                try:
                    element = self.driver.find_element(By.XPATH, selector)
                    if element.is_displayed():
                        logger.warning(f"모달창이 여전히 열려있음 (선택자 {i+1}): {selector}")
                        modal_found = True
                        break
                except (NoSuchElementException):
                    continue
                    
            if not modal_found:
                logger.info("일괄편집 모달창이 성공적으로 닫혔습니다")
                return True
            else:
                logger.warning("일괄편집 모달창이 여전히 열려있습니다")
                return False
            
        except Exception as e:
            logger.error(f"일괄편집 모달창 닫기 오류: {e}")
            return False
    
    def _detect_chinese_images(self):
        """
        모달창에서 중문글자가 있는 이미지들을 자동으로 감지
        
        Returns:
            list: 중문글자가 있는 이미지의 위치 번호 리스트
        """
        try:
            logger.info("중문글자 이미지 감지 시작")
            
            # 이미지 선택자들 (모달창/드로어 내부의 실제 이미지만 선택, percenty.co.kr 도메인 제외)
            image_selectors = [
                # 모달창/드로어 내부의 실제 이미지만 선택 (sc-hCrRFl dVjKzV 클래스 조합으로 이미지 추가 버튼 제외)
                "//div[contains(@class, 'ant-modal-content') or contains(@class, 'ant-drawer-content')]//div[contains(@class, 'sc-hCrRFl') and contains(@class, 'dVjKzV')]//img[contains(@class, 'sc-kyDlHK')]",
                # 모달창/드로어 내부의 bLXrEr 클래스가 있는 실제 이미지만
                "//div[contains(@class, 'ant-modal-content') or contains(@class, 'ant-drawer-content')]//img[contains(@class, 'sc-kyDlHK') and contains(@class, 'bLXrEr')]",
                # 모달창/드로어 내부의 alicdn.com 도메인 이미지만 (percenty.co.kr 제외)
                "//div[contains(@class, 'ant-modal-content') or contains(@class, 'ant-drawer-content')]//img[contains(@src, 'alicdn.com')]",
                # 마지막 대안: 모달창/드로어 내부의 draggable="false" 속성이 있는 실제 이미지
                "//div[contains(@class, 'ant-modal-content') or contains(@class, 'ant-drawer-content')]//img[@draggable='false' and contains(@class, 'sc-kyDlHK')]"
            ]
            
            all_images = []
            seen_images = set()  # 중복 제거를 위한 집합 (src 기반)
            seen_elements = set()  # 요소 자체 중복 제거
            
            for i, selector in enumerate(image_selectors):
                try:
                    logger.debug(f"이미지 선택자 {i+1} 시도: {selector}")
                    images = self.driver.find_elements(By.XPATH, selector)
                    logger.debug(f"이미지 선택자 {i+1}에서 {len(images)}개 이미지 발견")
                    
                    for img in images:
                        try:
                            # 이미지가 실제로 보이는지 확인
                            if img.is_displayed():
                                # 요소 자체 중복 확인 (동일한 DOM 요소)
                                element_id = id(img)
                                if element_id in seen_elements:
                                    continue
                                    
                                # src 속성으로 중복 제거 및 percenty.co.kr 도메인 제외
                                src = img.get_attribute('src')
                                if src and src not in seen_images:
                                    # percenty.co.kr 도메인 이미지 제외 (모달창 밖의 대표이미지)
                                    if 'percenty.co.kr' in src:
                                        logger.debug(f"percenty.co.kr 도메인 이미지 제외: {src[:100]}...")
                                        continue
                                    seen_images.add(src)
                                    seen_elements.add(element_id)
                                    all_images.append(img)
                                    logger.debug(f"유효한 이미지 추가: {src[:100]}...")
                        except Exception as e:
                            logger.debug(f"개별 이미지 처리 중 오류: {e}")
                            continue
                except Exception as e:
                    logger.debug(f"이미지 선택자 {i+1} 실패: {e}")
            
            if not all_images:
                logger.warning("모달창에서 이미지를 찾을 수 없습니다")
                # 디버깅을 위해 현재 페이지의 모든 이미지 개수 확인
                try:
                    all_page_images = self.driver.find_elements(By.TAG_NAME, "img")
                    visible_page_images = [img for img in all_page_images if img.is_displayed()]
                    logger.info(f"페이지 전체 이미지: {len(all_page_images)}개, 보이는 이미지: {len(visible_page_images)}개")
                except Exception as e:
                    logger.debug(f"전체 이미지 개수 확인 중 오류: {e}")
                return []
            
            logger.info(f"총 {len(all_images)}개의 유효한 이미지 발견 (중복 제거 후)")
            logger.debug(f"이미지 감지 상세 정보 - 고유 src: {len(seen_images)}개, 고유 요소: {len(seen_elements)}개")
            
            chinese_image_positions = []
            
            for i, img_element in enumerate(all_images, 1):
                try:
                    # 이미지가 화면에 보이는지 확인
                    if not img_element.is_displayed():
                        logger.debug(f"이미지 {i}: 화면에 표시되지 않음")
                        continue
                    
                    # 이미지 크기 확인 (너무 작은 이미지는 제외)
                    size = img_element.size
                    if size['width'] < 50 or size['height'] < 50:
                        logger.debug(f"이미지 {i}: 크기가 너무 작음 ({size['width']}x{size['height']})")
                        continue
                    
                    # 이미지 정보 로깅
                    src = img_element.get_attribute('src') or 'N/A'
                    alt = img_element.get_attribute('alt') or 'N/A'
                    logger.debug(f"이미지 {i} 분석 중: src={src[:50]}..., alt={alt}, 크기={size['width']}x{size['height']}")
                    
                    # 중문글자 감지 시도
                    has_chinese = self._check_image_for_chinese_text(img_element, i)
                    
                    if has_chinese:
                        chinese_image_positions.append(i)
                        logger.info(f"이미지 {i}: 중문글자 감지됨")
                    else:
                        logger.debug(f"이미지 {i}: 중문글자 없음")
                        
                except Exception as e:
                    logger.warning(f"이미지 {i} 처리 중 오류: {e}")
                    continue
            
            logger.info(f"중문글자 감지 완료 - 총 {len(chinese_image_positions)}개 이미지에서 중문글자 발견: {chinese_image_positions}")
            return chinese_image_positions
            
        except Exception as e:
            logger.error(f"중문글자 이미지 감지 오류: {e}")
            return []
    
    def _check_image_for_chinese_text(self, img_element, position):
        """
        개별 이미지에서 중문글자 존재 여부 확인
        
        Args:
            img_element: 이미지 웹 요소
            position (int): 이미지 위치 번호
            
        Returns:
            bool: 중문글자 존재 여부
        """
        try:
            logger.info(f"이미지 {position}: 중문글자 검사 시작")
            
            # 방법 1: 이미지 src 속성에서 중문글자 확인 (빠른 방법) - 주석처리됨
            # 실제로 속성에서 중문글자를 찾을 일이 없어서 주석처리
            # src = img_element.get_attribute('src')
            # alt = img_element.get_attribute('alt') or ''
            # title = img_element.get_attribute('title') or ''
            # 
            # logger.info(f"이미지 {position}: 속성 확인 - src={src}, alt='{alt}', title='{title}'")
            # 
            # # 중문글자 정규식 패턴
            # chinese_pattern = r'[\u4e00-\u9fff]+'
            # 
            # # alt나 title 속성에서 중문글자 확인
            # if re.search(chinese_pattern, alt) or re.search(chinese_pattern, title):
            #     logger.info(f"이미지 {position}: 속성에서 중문글자 발견 (alt: {alt}, title: {title})")
            #     return True
            # else:
            #     logger.info(f"이미지 {position}: 속성에서 중문글자 없음")
            
            # 중문글자 정규식 패턴 (다른 부분에서 사용)
            chinese_pattern = r'[\u4e00-\u9fff]+'
            src = img_element.get_attribute('src')  # OCR 부분에서 필요
            
            # 방법 2: 이미지 주변 텍스트에서 중문글자 확인
            try:
                # 이미지의 부모 요소에서 텍스트 확인
                parent = img_element.find_element(By.XPATH, "..")
                parent_text = parent.text or ''
                if re.search(chinese_pattern, parent_text):
                    logger.info(f"이미지 {position}: 부모 요소에서 중문글자 발견")
                    return True
                
                # 이미지의 data 속성들 확인
                for attr in ['data-original', 'data-src', 'data-lazy-src']:
                    data_value = img_element.get_attribute(attr) or ''
                    if re.search(chinese_pattern, data_value):
                        logger.info(f"이미지 {position}: {attr} 속성에서 중문글자 발견")
                        return True
            except Exception as e:
                logger.info(f"이미지 {position} 주변 텍스트 확인 중 오류: {e}")
            
            # 방법 3: OCR을 사용한 이미지 텍스트 분석 (더 정확하지만 느림)
            if OCR_AVAILABLE:
                logger.info(f"이미지 {position}: OCR 검사 시작")
                ocr_result = self._ocr_check_chinese_text(img_element, position)
                logger.info(f"이미지 {position}: OCR 검사 결과 - {ocr_result}")
                return ocr_result
            else:
                logger.info(f"이미지 {position}: OCR 사용 불가, 파일명 검사")
                # OCR이 없는 경우 이미지 파일명에서 중문글자 확인
                if src and re.search(chinese_pattern, src):
                    logger.info(f"이미지 {position}: 파일명에서 중문글자 발견")
                    return True
                
                # OCR이 없는 경우 경고 메시지를 한 번만 출력
                if not hasattr(self, '_ocr_warning_shown'):
                    logger.warning("OCR이 설치되지 않아 이미지 내 텍스트 분석이 제한됩니다. 속성 기반 감지만 사용합니다.")
                    self._ocr_warning_shown = True
                
                logger.info(f"이미지 {position}: 모든 검사 완료, 중문글자 없음")
            
            return False
            
        except Exception as e:
            logger.warning(f"이미지 {position} 중문글자 확인 중 오류: {e}")
            return False
    
    def _ocr_check_chinese_text(self, img_element, position):
        """
        OCR을 사용하여 이미지에서 중문글자 감지 (원본 이미지 다운로드 방식)
        
        Args:
            img_element: 이미지 웹 요소
            position (int): 이미지 위치 번호
            
        Returns:
            bool: 중문글자 존재 여부
        """
        try:
            logger.debug(f"이미지 {position}: OCR 중문글자 감지 시작")
            
            # 이미지 요소의 기본 정보 확인
            img_src = img_element.get_attribute('src')
            img_visible = img_element.is_displayed()
            img_size = img_element.size
            logger.info(f"이미지 {position}: 요소 정보 - 표시됨: {img_visible}, 크기: {img_size}, src: {img_src[:100]}...")
            
            # 원본 이미지 URL에서 직접 다운로드
            if not img_src or img_src.startswith('data:'):
                logger.warning(f"이미지 {position}: 유효하지 않은 이미지 URL - 스크린샷으로 대체")
                # 스크린샷으로 대체
                screenshot = img_element.screenshot_as_png
                image = Image.open(io.BytesIO(screenshot))
                logger.info(f"이미지 {position}: 스크린샷 사용 - 크기: {image.size}")
            else:
                # 원본 이미지 다운로드
                import requests
                try:
                    response = requests.get(img_src, timeout=10)
                    response.raise_for_status()
                    image = Image.open(io.BytesIO(response.content))
                    logger.info(f"이미지 {position}: 원본 이미지 다운로드 완료 - 크기: {image.size}, 모드: {image.mode}")
                except Exception as download_error:
                    logger.warning(f"이미지 {position}: 원본 다운로드 실패 ({download_error}) - 스크린샷으로 대체")
                    screenshot = img_element.screenshot_as_png
                    image = Image.open(io.BytesIO(screenshot))
                    logger.info(f"이미지 {position}: 스크린샷 사용 - 크기: {image.size}")
            
            original_size = image.size
            
            # 이미지가 너무 작거나 비어있는지 확인
            if original_size[0] <= 1 or original_size[1] <= 1:
                logger.warning(f"이미지 {position}: 이미지 크기가 너무 작음 ({original_size}) - OCR 건너뜀")
                return False
            
            # 이미지 크기가 너무 작으면 확대
            width, height = image.size
            if width < 200 or height < 200:
                scale_factor = max(200 / width, 200 / height)
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                logger.info(f"이미지 {position}: 크기 조정 {width}x{height} -> {new_width}x{new_height}")
            
            # 이미지 전처리 - 그레이스케일 변환
            if image.mode != 'L':
                gray_image = image.convert('L')
                logger.info(f"이미지 {position}: 그레이스케일 변환 완료")
            else:
                gray_image = image
            
            # EasyOCR 실행
            try:
                # 이미지를 numpy 배열로 변환
                image_array = np.array(gray_image)
                logger.info(f"이미지 {position}: EasyOCR 실행 시작 (언어: 중문만)")
                
                # EasyOCR로 텍스트 추출
                results = easyocr_reader.readtext(image_array)
                logger.info(f"이미지 {position}: EasyOCR 완료 - {len(results)}개 텍스트 블록 감지")
                
                # 결과에서 텍스트만 추출 (신뢰도 0.3 이상만)
                text_parts = []
                for bbox, text, confidence in results:
                    if confidence >= 0.3:  # 신뢰도 30% 이상만 사용
                        text_parts.append(text)
                        logger.debug(f"이미지 {position}: 텍스트 블록 '{text}' (신뢰도: {confidence:.3f})")
                
                text = ' '.join(text_parts)
                logger.info(f"이미지 {position}: 추출된 전체 텍스트 (길이: {len(text)}): '{text.strip()}'")
                        
            except Exception as ocr_error:
                # EasyOCR 오류 처리
                logger.warning(f"이미지 {position}: EasyOCR 실패 - {ocr_error}")
                return False
            
            # 중문글자 정규식 패턴으로 확인
            chinese_pattern = r'[\u4e00-\u9fff]+'
            chinese_matches = re.findall(chinese_pattern, text)
            
            logger.info(f"이미지 {position}: 중문글자 패턴 검사 결과 - 매치 수: {len(chinese_matches)}")
            if chinese_matches:
                logger.info(f"이미지 {position}: 발견된 중문글자: {chinese_matches}")
            
            # 텍스트의 각 문자를 유니코드로 확인
            if text.strip():
                char_analysis = []
                for char in text.strip()[:20]:  # 처음 20자만 분석
                    unicode_val = ord(char)
                    is_chinese = 0x4e00 <= unicode_val <= 0x9fff
                    char_analysis.append(f"'{char}'(U+{unicode_val:04X}, 중문:{is_chinese})")
                logger.info(f"이미지 {position}: 문자 분석: {', '.join(char_analysis)}")
            else:
                logger.warning(f"이미지 {position}: OCR 결과가 완전히 비어있음")
            
            if chinese_matches:
                logger.info(f"이미지 {position}: OCR에서 중문글자 발견 - {chinese_matches[:3]}...")  # 처음 3개만 로그
                return True
            else:
                logger.info(f"이미지 {position}: OCR에서 중문글자 없음")
                return False
                
        except Exception as e:
            # OCR 관련 오류는 디버그 레벨로 처리 (반복 메시지 방지)
            if "easyocr" in str(e).lower() or "reader" in str(e).lower():
                logger.debug(f"이미지 {position} EasyOCR 중문글자 감지 오류: {e}")
                # EasyOCR 설치 안내 메시지를 한 번만 출력
                if not hasattr(self, '_easyocr_error_shown'):
                    logger.warning("EasyOCR이 제대로 초기화되지 않았습니다. 속성 기반 중문글자 감지만 사용됩니다.")
                    self._easyocr_error_shown = True
            else:
                logger.warning(f"이미지 {position} EasyOCR 중문글자 감지 오류: {e}")
            return False
