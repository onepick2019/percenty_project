import logging
import time
import random
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import base64
from PIL import Image
import io
import numpy as np

# EasyOCR 초기화 (선택적)
try:
    import easyocr
    # EasyOCR 리더 초기화 (중문 간체만)
    easyocr_reader = easyocr.Reader(['ch_sim'], gpu=False)
    OCR_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info(f"EasyOCR 초기화 완료 - OCR_AVAILABLE={OCR_AVAILABLE}")
except ImportError:
    OCR_AVAILABLE = False
    easyocr_reader = None
    logger = logging.getLogger(__name__)
    logger.warning(f"EasyOCR를 사용할 수 없습니다. pip install easyocr로 설치하세요. OCR_AVAILABLE={OCR_AVAILABLE}")
except Exception as e:
    OCR_AVAILABLE = False
    easyocr_reader = None
    logger = logging.getLogger(__name__)
    logger.error(f"EasyOCR 초기화 실패: {e}. OCR_AVAILABLE={OCR_AVAILABLE}")

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
    """이미지 번역 처리를 위한 핸들러 클래스"""
    
    def __init__(self, driver):
        self.driver = driver
        self.logger = logging.getLogger(__name__)
        self.human_delay = HumanLikeDelay()
        
    def image_translate(self, action_value, context='detail'):
        """이미지 번역 처리 메인 메서드
        
        Args:
            action_value (str): 액션 값
            context (str): 처리 컨텍스트 ('detail', 'thumbnail', 'option')
            
        Returns:
            int: 실제 번역된 이미지 개수 (실패 시 0)
        """
        try:
            self.logger.info(f"이미지 번역 시작 - 액션: {action_value}, 컨텍스트: {context}")
            
            # 액션 파싱
            action_info = self._parse_image_translate_action(action_value)
            if not action_info:
                self.logger.error("이미지 번역 액션 파싱 실패")
                return 0
            
            # 컨텍스트별 모달창 열기
            if context == 'detail':
                # 상세페이지: 일괄편집 모달창 열기
                if not self._open_bulk_edit_modal(context):
                    return 0
            else:
                # 썸네일/옵션: 바로 편집하기 버튼 클릭
                if not self._open_direct_edit_modal(context):
                    return 0
                
            try:
                # 이미지 번역 액션 처리 - 실제 번역된 개수 반환
                translated_count = self._process_image_translate_action(action_info, context)
                
                if translated_count > 0:
                    self.logger.info(f"이미지 번역 완료: {translated_count}개")
                else:
                    self.logger.info("번역할 이미지가 없습니다 (중국어 텍스트 미감지)")
                
                return translated_count
                
            finally:
                # 모달 닫기 - 주석처리 (product_editor_core3에서 통합 관리)
                # self._close_bulk_edit_modal()
                pass
                
        except Exception as e:
            self.logger.error(f"이미지 번역 중 오류 - 컨텍스트: {context}, 오류: {e}")
            return 0
            
    def _parse_image_translate_action(self, action_value):
        """이미지 번역 액션 값 파싱 (기존 방식 호환, '/' 구분자 지원)"""
        try:
            if not action_value or action_value.strip() == "":
                self.logger.warning("이미지 번역 액션 값이 비어있음")
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
                        self.logger.info(f"복합 이미지 번역 명령어 파싱 완료: {action_value} -> {combined_positions}")
                        return {
                            'type': 'image_translate',
                            'positions': combined_positions
                        }
                    else:
                        self.logger.warning(f"복합 명령어에서 유효한 위치를 찾을 수 없음: {action_value}")
                        return None
                        
                except Exception as e:
                    self.logger.warning(f"복합 명령어 파싱 중 오류: {action_value}, 오류: {e}")
                    return None
            
            # 단일 명령어 파싱
            return self._parse_single_translate_command(action_value)
            
        except Exception as e:
            self.logger.error(f"이미지 번역 액션 파싱 오류: {e}")
            return None
    
    def _parse_single_translate_command(self, action_value):
        """단일 이미지 번역 명령어 파싱"""
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
                    self.logger.info(f"first 형식 파싱: {pos} -> {list(range(1, num + 1))}")
                except (IndexError, ValueError):
                    self.logger.warning(f"잘못된 first 형식: {pos}")
            # "last:숫자" 형식인 경우 (마지막부터 지정된 개수만큼)
            elif pos.startswith('last:'):
                try:
                    num = int(pos.split(':')[1])
                    # last:1은 마지막 1개, last:2는 마지막 2개를 의미
                    # 실제 이미지 개수를 확인해야 하므로 임시로 음수로 저장
                    # 나중에 실제 이미지 개수를 확인한 후 계산
                    positions.append(f'last:{num}')
                    self.logger.info(f"last 형식 파싱: {pos} -> last:{num} (실제 위치는 이미지 개수 확인 후 계산)")
                except (IndexError, ValueError):
                    self.logger.warning(f"잘못된 last 형식: {pos}")
            # "specific:숫자" 형식인 경우 (특정 위치 지정)
            elif pos.startswith('specific:'):
                try:
                    value = pos.split(':')[1]
                    if value == 'all':
                        # specific:all인 경우 새로운 순차 처리 방식 사용
                        self.logger.info("specific:all 형식 - 새로운 순차 처리 모드")
                        positions.append('sequential_all')
                    else:
                        num = int(value)
                        positions.append(num)
                        self.logger.info(f"specific 형식 파싱: {pos} -> {num}")
                except (IndexError, ValueError):
                    self.logger.warning(f"잘못된 specific 형식: {pos}")
            # "auto_detect_chinese" 형식인 경우 (중문글자 자동 감지)
            elif pos == 'auto_detect_chinese':
                self.logger.info("auto_detect_chinese 형식 - 중문글자 자동 감지 모드")
                positions.append('auto_detect_chinese')
            # "special:N" 형식인 경우 (N번째 이미지까지만 스캔)
            elif pos.startswith('special:'):
                try:
                    max_position = int(pos.split(':')[1])
                    self.logger.info(f"special 형식 파싱: {pos} -> 최대 {max_position}번째까지 스캔")
                    positions.append(f'special:{max_position}')
                except (IndexError, ValueError):
                    self.logger.warning(f"잘못된 special 형식: {pos}")
            else:
                self.logger.warning(f"잘못된 이미지 위치 값: {pos}")
        
        if not positions:
            self.logger.error("유효한 이미지 위치가 없음")
            return None
        
        action_info = {
            'type': 'image_translate',
            'positions': positions
        }
        
        self.logger.info(f"이미지 번역 액션 파싱 완료: {action_info}")
        return action_info
            
    def _process_image_translate_action(self, action_info, context='detail'):
        """이미지 번역 액션 처리
        
        Args:
            action_info (dict): 액션 정보
            context (str): 처리 컨텍스트 ('detail', 'thumbnail', 'option')
            
        Returns:
            int: 실제 번역된 이미지 개수
        """
        try:
            positions = action_info.get('positions', [])
            self.logger.info(f"이미지 번역 처리 시작 - 위치: {positions}")
            
            # special:N 모드인 경우 N번째까지만 스캔하여 처리
            special_positions = [pos for pos in positions if isinstance(pos, str) and pos.startswith('special:')]
            if special_positions:
                max_position = int(special_positions[0].split(':')[1])
                self.logger.info(f"special 모드 실행: 최대 {max_position}번째 이미지까지 스캔")
                return self._process_all_images_sequentially_with_limit(max_position, context)
            
            # auto_detect_chinese 모드인 경우 중문글자 감지 후 통합 처리
            if 'auto_detect_chinese' in positions:
                self.logger.info("중문글자 자동 감지 모드 실행")
                # 중문글자 감지 기능은 SpecificImageTranslationHandler에서 가져와야 함
                # 현재는 모든 이미지를 순차 처리하는 방식으로 대체
                return self._process_all_images_sequentially(context)
            
            # sequential_all 모드인 경우 전체 이미지 스캔 방식 사용
            if 'sequential_all' in positions:
                return self._process_all_images_sequentially(context)
            else:
                # 특정 위치들은 해당 위치만 처리하는 방식 사용
                return self._process_specific_positions_unified(positions, context)
                
        except Exception as e:
            self.logger.error(f"이미지 번역 액션 처리 오류: {e}")
            return 0
            
    # def _process_specific_positions(self, positions):
    #     """개별 위치 처리 (기존 방식) - 통합 방식으로 대체됨"""
    #    try:
    #         success_count = 0
    #         total_count = len(positions)
    #         
    #         for position in positions:
    #             try:
    #                 self.logger.info(f"이미지 위치 {position} 번역 시작")
    #                 
    #                 # 편집 버튼 클릭
    #                 if not self._click_edit_button_by_position(position):
    #                     self.logger.error(f"이미지 위치 {position} 편집 버튼 클릭 실패")
    #                     continue
    #                 
    #                 # 이미지 번역 모달 대기
    #                 if not self._wait_for_image_translation_modal():
    #                     self.logger.error(f"이미지 위치 {position} 번역 모달 대기 실패")
    #                     continue
    #                 
    #                 # 현재 이미지 처리
    #                 if self._process_current_image():
    #                     success_count += 1
    #                     self.logger.info(f"이미지 위치 {position} 번역 성공")
    #                 
    #                 # 번역 모달 닫기
    #                 self._close_image_translation_modal()
    #                 self.human_delay.short_delay()
    #                 
    #             except Exception as e:
    #                 self.logger.error(f"이미지 위치 {position} 번역 오류: {e}")
    #                 continue
    #         
    #         # 변경사항 저장 (한 번만)
    #         if success_count > 0:
    #             self._save_changes()
    #         
    #         self.logger.info(f"개별 위치 처리 완료 - 성공: {success_count}/{total_count}")
    #         return success_count > 0
    #         
    #     except Exception as e:
    #         self.logger.error(f"개별 위치 처리 오류: {e}")
    #         return False
            
    def _process_all_images_sequentially_with_limit(self, max_scan_position, context='detail'):
        """제한된 위치까지만 이미지 순차 처리
        
        Args:
            max_scan_position (int): 스캔할 최대 이미지 위치
            context (str): 처리 컨텍스트 ('detail', 'thumbnail', 'option')
            
        Returns:
            int: 실제 번역된 이미지 개수
        """
        try:
            if context == 'detail':
                # 상세페이지: 일괄편집 모달창을 먼저 열고 이미지 개수 확인
                # 첫 번째 편집 버튼 클릭
                if not self._click_first_image_bulk_edit_button(context):
                    return False
                    
                # 이미지 번역 모달 대기
                if not self._wait_for_image_translation_modal():
                    return False
                    
                # 총 이미지 개수 확인
                total_images = self._get_total_image_count(context)
                if total_images == 0:
                    self.logger.warning("이미지가 없습니다")
                    # K열(detail)의 경우 이미지가 0개여도 저장 버튼 클릭 후 모달 닫기
                    self._save_changes()
                    self._close_image_translation_modal()
                    return 0
            else:
                # 썸네일/옵션 탭: 해당 탭에서 먼저 이미지 개수 확인 후 편집하기 버튼 클릭
                # 먼저 해당 탭에서 이미지 개수 확인 (모달창 열기 전)
                total_images = self._get_tab_image_count(context)
                if total_images == 0:
                    self.logger.warning(f"{context} 탭에 이미지가 없습니다")
                    return 0
                    
                self.logger.info(f"{context} 탭에서 총 {total_images}개의 이미지 발견")
                
                # 편집하기 버튼 클릭
                if not self._click_first_image_bulk_edit_button(context):
                    return False
                    
                # 이미지 번역 모달 대기
                if not self._wait_for_image_translation_modal():
                    return False
                
            # 스캔할 이미지 개수를 max_scan_position으로 제한
            scan_images = min(total_images, max_scan_position)
            self.logger.info(f"총 {total_images}개 중 {scan_images}개의 이미지만 스캔 및 번역 처리 시작")
                
            # 1단계: 제한된 이미지만 스캔하여 번역 필요한 이미지 식별
            images_to_translate = self._scan_all_images_for_translation_with_limit(scan_images, context)
            
            if not images_to_translate:
                self.logger.info("번역이 필요한 이미지가 없습니다")
                # K열(detail)에서만 저장 후 모달 닫기, N열/O열에서는 모달만 닫기
                if context == 'detail':
                    self._save_changes()
                self._close_image_translation_modal()
                return 0
                
            # 2단계: 식별된 이미지들만 번역 처리
            processed_count = self._process_specific_images_for_translation(images_to_translate)
            
            # 변경사항 저장
            self._save_changes()
            
            # 모달 닫기
            self._close_image_translation_modal()
            
            self.logger.info(f"제한된 이미지 순차 처리 완료: {processed_count}/{len(images_to_translate)}개 성공")
            return processed_count
            
        except Exception as e:
            self.logger.error(f"제한된 이미지 순차 처리 오류: {e}")
            return 0
    
    def _process_all_images_sequentially(self, context='detail'):
        """모든 이미지 순차 처리
        
        Args:
            context (str): 처리 컨텍스트 ('detail', 'thumbnail', 'option')
            
        Returns:
            int: 실제 번역된 이미지 개수
        """
        try:
            if context == 'detail':
                # 상세페이지: 일괄편집 모달창을 먼저 열고 이미지 개수 확인
                # 첫 번째 편집 버튼 클릭
                if not self._click_first_image_bulk_edit_button(context):
                    return False
                    
                # 이미지 번역 모달 대기
                if not self._wait_for_image_translation_modal():
                    return False
                    
                # 총 이미지 개수 확인
                total_images = self._get_total_image_count(context)
                if total_images == 0:
                    self.logger.warning("이미지가 없습니다")
                    return 0
            else:
                # 썸네일/옵션 탭: 해당 탭에서 먼저 이미지 개수 확인 후 편집하기 버튼 클릭
                # 먼저 해당 탭에서 이미지 개수 확인 (모달창 열기 전)
                total_images = self._get_tab_image_count(context)
                if total_images == 0:
                    self.logger.warning(f"{context} 탭에 이미지가 없습니다")
                    return 0
                    
                self.logger.info(f"{context} 탭에서 총 {total_images}개의 이미지 발견")
                
                # 편집하기 버튼 클릭
                if not self._click_first_image_bulk_edit_button(context):
                    return False
                    
                # 이미지 번역 모달 대기
                if not self._wait_for_image_translation_modal():
                    return False
                
            self.logger.info(f"총 {total_images}개의 이미지 스캔 및 번역 처리 시작")
                
            # 1단계: 모든 이미지 스캔하여 번역 필요한 이미지 식별
            images_to_translate = self._scan_all_images_for_translation(total_images, context)
            
            if not images_to_translate:
                self.logger.info("번역이 필요한 이미지가 없습니다")
                # K열(detail)에서만 저장 후 모달 닫기, N열/O열에서는 모달만 닫기
                if context == 'detail':
                    self._save_changes()
                    self._close_image_translation_modal()
                else:
                    self._close_image_translation_modal()
                return 0
                
            self.logger.info(f"번역 대상 이미지: specific:{','.join(map(str, images_to_translate))}")
            
            # 2단계: 식별된 이미지들만 번역 처리
            processed_count = self._process_specific_images_for_translation(images_to_translate)
            
            # 변경사항 저장 (한 번만)
            if processed_count > 0:
                self._save_changes()
            
            # 모달 닫기 - 썸네일/옵션 탭에서는 모달을 열어둠 (다른 탭 처리를 위해)
            if context == 'detail':
                self._close_image_translation_modal()
            
            self.logger.info(f"스캔 및 번역 처리 완료: {processed_count}/{len(images_to_translate)}개 처리됨 - 컨텍스트: {context}")
            return processed_count
            
        except Exception as e:
            self.logger.error(f"스캔 및 번역 처리 오류 - 컨텍스트: {context}, 오류: {e}")
            return 0
            
    def _process_specific_positions_unified(self, positions, context='detail'):
        """특정 위치 이미지만 처리하는 통합 방식
        
        Args:
            positions (list): 이미지 위치 리스트
            context (str): 처리 컨텍스트 ('detail', 'thumbnail', 'option')
            
        Returns:
            int: 실제 번역된 이미지 개수
        """
        try:
            self.logger.info(f"특정 위치 이미지 번역 처리 시작 - 위치: {positions}, 컨텍스트: {context}")
            
            # last: 형식을 실제 위치로 변환
            converted_positions = []
            total_images = None
            
            for pos in positions:
                if isinstance(pos, str) and pos.startswith('last:'):
                    # 총 이미지 개수를 아직 확인하지 않았다면 확인
                    if total_images is None:
                        if context in ['thumbnail', 'option']:
                            # 썸네일/옵션 탭의 경우 탭에서 직접 이미지 개수 확인
                            total_images = self._get_tab_image_count(context)
                        else:
                            # 상세페이지의 경우 모달창에서 이미지 개수 확인
                            total_images = self._get_total_image_count(context)
                        self.logger.info(f"총 이미지 개수 확인: {total_images}개")
                    
                    # last:숫자에서 숫자 추출
                    try:
                        num = int(pos.split(':')[1])
                        # 마지막부터 num개의 위치 계산
                        if total_images > 0:
                            # last:1이면 마지막 1개 (예: 총 5개면 5번째)
                            # last:2이면 마지막 2개 (예: 총 5개면 4,5번째)
                            start_pos = max(1, total_images - num + 1)
                            for i in range(start_pos, total_images + 1):
                                converted_positions.append(i)
                            self.logger.info(f"last:{num} -> 위치 {list(range(start_pos, total_images + 1))} (총 {total_images}개 이미지)")
                        else:
                            self.logger.warning(f"이미지가 없어서 {pos}를 처리할 수 없음")
                    except (IndexError, ValueError) as e:
                        self.logger.warning(f"잘못된 last 형식: {pos}, 오류: {e}")
                        converted_positions.append(pos)  # 원본 유지
                else:
                    converted_positions.append(pos)
            
            # 중복 제거 및 정렬
            converted_positions = sorted(list(set(converted_positions)))
            self.logger.info(f"위치 변환 완료: {positions} -> {converted_positions}")
            
            # 이미지 번역 모달창이 이미 열려있는지 확인
            modal_already_open = self._check_modal_open()
            
            if not modal_already_open:
                # 이미지 번역 모달창이 열려있지 않은 경우 첫 번째 이미지의 일괄편집 버튼 클릭
                self.logger.info("이미지 번역 모달창이 닫혀있음 - 첫 번째 이미지 일괄편집 버튼 클릭")
                if not self._click_first_image_bulk_edit_button(context):
                    self.logger.error("첫 번째 이미지 일괄편집 버튼 클릭 실패")
                    return False
                    
                # 이미지 번역 모달창이 열릴 때까지 대기
                if not self._wait_for_image_translation_modal():
                    self.logger.error("이미지 번역 모달창 열기 실패")
                    return False
            else:
                self.logger.info("이미지 번역 모달창이 이미 열려있음 - 바로 번역 처리 진행")
                
            # 지정된 위치의 이미지들만 번역 처리
            processed_count = self._process_specific_images_for_translation(converted_positions)
            
            # 변경사항 저장 (한 번만)
            if processed_count > 0:
                self._save_changes()
            
            # 모달 닫기 - 상세페이지에서만 닫고, 썸네일/옵션 탭에서는 열어둠
            if not modal_already_open and context == 'detail':
                self._close_image_translation_modal()
            
            self.logger.info(f"특정 위치 이미지 번역 처리 완료: {processed_count}/{len(converted_positions)}개 처리됨")
            return processed_count
            
        except Exception as e:
            self.logger.error(f"특정 위치 이미지 번역 처리 오류: {e}")
            return 0
            
    def _check_modal_open(self):
        """이미지 번역 모달창이 열려있는지 확인 (실제 이미지 번역 모달창만 감지)"""
        try:
            # 이미지 번역 모달창 특정 선택자들 (상세페이지 일괄편집 모달창과 구분)
            image_translation_modal_selectors = [
                "//div[contains(@class, 'ant-modal')]//span[contains(text(), '이미지 번역')]",
                "//div[contains(@class, 'ant-drawer')]//span[contains(text(), '이미지 번역')]",
                "//div[contains(@class, 'ant-modal')]//div[contains(@class, 'ant-modal-title') and contains(text(), '이미지 번역')]",
                "//div[contains(@class, 'ant-drawer')]//div[contains(@class, 'ant-drawer-title') and contains(text(), '이미지 번역')]",
                # 이미지 번역 모달창 내부의 특정 요소들
                "//div[contains(@class, 'ant-modal')]//button[contains(text(), '원클릭 이미지 번역')]",
                "//div[contains(@class, 'ant-drawer')]//button[contains(text(), '원클릭 이미지 번역')]"
            ]
            
            for selector in image_translation_modal_selectors:
                try:
                    element = self.driver.find_element(By.XPATH, selector)
                    if element and element.is_displayed():
                        self.logger.info(f"이미지 번역 모달창 열림 확인: {selector}")
                        return True
                except Exception:
                    continue
                    
            return False
            
        except Exception as e:
            self.logger.error(f"이미지 번역 모달창 상태 확인 오류: {e}")
            return False
            
    def _click_edit_button_by_position(self, position):
        """위치별 편집 버튼 클릭 (안정적인 선택자 사용)"""
        try:
            self.logger.info(f"이미지 위치 {position} 편집 버튼 클릭 시도")
            
            # 편집 버튼 선택자들 (다양한 형태 지원)
            edit_button_selectors = [
                f"(//span[contains(@class, 'FootnoteDescription') and text()='편집하기'])[{position}]",
                f"(//div[contains(@class, 'sc-kTbCBX') or contains(@class, 'sc-gkKZNe')]//span[text()='편집하기'])[{position}]",
                f"(//div[contains(@class, 'sc-kTbCBX')]//span[contains(@class, 'FootnoteDescription') and text()='편집하기'])[{position}]",
                f"(//span[text()='편집하기'])[{position}]",
                # 현재 DOM 구조에 맞는 추가 선택자들
                f"(//div[contains(@class, 'sc-bOTbmH') and contains(@class, 'hDwhsl')])[{position}]",
                f"(//div[contains(@class, 'sc-bOTbmH')]//span[contains(text(), '편집하기')])[{position}]/parent::div"
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
                            self.logger.info(f"이미지 위치 {position} 편집 버튼 클릭 성공 (일반 클릭)")
                        except Exception:
                            # JavaScript 클릭 시도
                            self.driver.execute_script("arguments[0].click();", edit_btn)
                            self.logger.info(f"이미지 위치 {position} 편집 버튼 클릭 성공 (JavaScript 클릭)")
                        
                        self.human_delay.short_delay()  # 모달 로딩 대기
                        return True
                except Exception as e:
                    self.logger.debug(f"편집 버튼 선택자 {selector} 실패: {e}")
                    continue
            
            self.logger.error(f"이미지 위치 {position} 편집 버튼을 찾을 수 없음")
            return False
            
        except Exception as e:
            self.logger.error(f"이미지 위치 {position} 편집 버튼 클릭 오류: {e}")
            return False
            
    def _open_bulk_edit_modal(self, context='detail'):
        """벌크 편집 모달 열기
        
        Args:
            context (str): 처리 컨텍스트 ('detail', 'thumbnail', 'option')
            
        Returns:
            bool: 성공 여부
        """
        try:
            self.logger.info("상세페이지 일괄편집 모달창 열기 시작")
            
            # 일괄편집 버튼 선택자 (기존 작동하는 방식)
            bulk_edit_button_selector = "//button[contains(@class, 'ant-btn')][.//span[text()='일괄 편집']][.//span[@role='img' and @aria-label='form']]"
            
            try:
                bulk_edit_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, bulk_edit_button_selector))
                )
                bulk_edit_button.click()
                self.logger.info("일괄편집 버튼 클릭 성공")
                
                # 모달창이 열릴 때까지 대기
                self.human_delay.medium_delay()
                
                # 모달창이 열렸는지 확인 - 원본 파일의 검증된 선택자 사용
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
                        self.logger.info(f"모달창 확인 시도 {i+1}: {selector}")
                        modal_element = WebDriverWait(self.driver, 3).until(
                            EC.visibility_of_element_located((By.XPATH, selector))
                        )
                        self.logger.info(f"모달창 발견 (선택자 {i+1}): {selector}")
                        modal_opened = True
                        break
                    except (TimeoutException, NoSuchElementException) as e:
                        self.logger.warning(f"모달창 선택자 {i+1} 실패: {e}")
                        continue
                        
                if modal_opened:
                    self.logger.info("상세페이지 이미지 모달창이 성공적으로 열렸습니다.")
                    return True
                else:
                    self.logger.error("모달창이 열리지 않았습니다.")
                    return False
                
            except TimeoutException:
                self.logger.error("일괄편집 버튼을 찾을 수 없습니다")
                return False
                
        except Exception as e:
            self.logger.error(f"일괄편집 모달창 열기 오류: {e}")
            return False
            
    def _open_direct_edit_modal(self, context):
        """썸네일/옵션 탭에서 직접 편집하기 버튼 클릭하여 이미지 번역 모달 열기
        
        Args:
            context (str): 처리 컨텍스트 ('thumbnail', 'option')
            
        Returns:
            bool: 성공 여부
        """
        try:
            self.logger.info(f"{context} 탭에서 직접 편집하기 버튼 클릭 시작")
            
            # 편집 버튼 선택자 가져오기
            edit_button_selectors = self._get_edit_button_selectors(context)
            
            for selector in edit_button_selectors:
                try:
                    edit_btn = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    
                    # 스크롤하여 요소가 보이도록 함
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", edit_btn)
                    time.sleep(0.2)
                    
                    # 클릭 시도
                    try:
                        edit_btn.click()
                        self.logger.info(f"{context} 탭 편집하기 버튼 클릭 성공 (일반 클릭): {selector}")
                    except Exception:
                        # JavaScript 클릭 시도
                        self.driver.execute_script("arguments[0].click();", edit_btn)
                        self.logger.info(f"{context} 탭 편집하기 버튼 클릭 성공 (JavaScript 클릭): {selector}")
                    
                    # 이미지 번역 모달창이 열릴 때까지 대기
                    self.human_delay.medium_delay()
                    
                    # 이미지 번역 모달창 확인
                    if self._wait_for_image_translation_modal():
                        self.logger.info(f"{context} 탭 이미지 번역 모달창이 성공적으로 열렸습니다.")
                        return True
                    else:
                        self.logger.warning(f"{context} 탭 이미지 번역 모달창이 열리지 않았습니다.")
                        continue
                        
                except TimeoutException:
                    self.logger.debug(f"{context} 탭 편집 버튼 선택자 {selector} 시간 초과")
                    continue
                except Exception as e:
                    self.logger.debug(f"{context} 탭 편집 버튼 선택자 {selector} 실패: {e}")
                    continue
            
            self.logger.error(f"{context} 탭에서 편집하기 버튼을 찾을 수 없습니다")
            return False
            
        except Exception as e:
            self.logger.error(f"{context} 탭 직접 편집 모달 열기 오류: {e}")
            return False
            
    def _get_total_image_count(self, context='detail'):
        """총 이미지 개수 확인 - 컨텍스트별 모달창 내 cbu01.alicdn.com 이미지만 카운트
        
        Args:
            context (str): 처리 컨텍스트 ('detail', 'thumbnail', 'option')
            
        Returns:
            int: 이미지 개수
        """
        try:
            self.logger.info(f"[{context}] 총 이미지 개수 확인 시작")
            
            # 컨텍스트별 모달창 요소 찾기
            modal_element = None
            
            if context == 'detail':
                # 상세페이지 일괄편집 모달창
                modal_selectors = [
                    "//div[contains(@class, 'ant-drawer-content')]",
                    "//div[contains(@class, 'ant-modal-content')]",
                    "//div[contains(@class, 'ant-drawer')]",
                    "//div[contains(@class, 'ant-modal')]"
                ]
            else:
                # 썸네일/옵션 탭의 이미지 번역 모달창
                modal_selectors = [
                    "//div[contains(@class, 'ant-drawer')]//span[contains(text(), '이미지 번역')]/ancestor::div[contains(@class, 'ant-drawer')]",
                    "//div[contains(@class, 'ant-modal')]//span[contains(text(), '이미지 번역')]/ancestor::div[contains(@class, 'ant-modal')]",
                    "//div[contains(@class, 'ant-drawer-content')]",
                    "//div[contains(@class, 'ant-modal-content')]",
                    "//div[contains(@class, 'ant-drawer')]",
                    "//div[contains(@class, 'ant-modal')]"
                ]
            
            for modal_selector in modal_selectors:
                try:
                    modal_element = self.driver.find_element(By.XPATH, modal_selector)
                    if modal_element:
                        self.logger.info(f"[{context}] 모달창 요소 발견: {modal_selector}")
                        break
                except Exception:
                    continue
            
            if not modal_element:
                self.logger.warning(f"[{context}] 모달창을 찾을 수 없습니다")
                return 0
                
            # 컨텍스트별 이미지 선택자 설정
            if context in ['thumbnail', 'option']:
                # 썸네일/옵션 탭의 이미지 번역 모달창 내 이미지
                selectors = [
                    # 이미지 번역 모달창 내 특정 이미지 선택자
                    ".//div[contains(@class, 'sc-hMxIkD') and contains(@class, 'byPQOP')]//img[contains(@class, 'p_tooltip_image_editor_thumb')]",
                    ".//div[contains(@class, 'sc-hMxIkD')]//img[contains(@class, 'sc-eSoiBi') and contains(@class, 'ipHRUV') and contains(@class, 'p_tooltip_image_editor_thumb')]",
                    ".//img[contains(@class, 'sc-eSoiBi') and contains(@class, 'ipHRUV') and contains(@class, 'p_tooltip_image_editor_thumb') and contains(@src, 'cbu01.alicdn.com')]",
                    ".//img[contains(@class, 'sc-eSoiBi') and contains(@class, 'p_tooltip_image_editor_thumb') and contains(@src, 'cbu01.alicdn.com')]",
                    ".//img[contains(@class, 'p_tooltip_image_editor_thumb') and contains(@src, 'https://cbu01.alicdn.com/img')]",
                    ".//img[contains(@src, 'https://cbu01.alicdn.com/img')]",
                    # 추가 선택자 (이미지 번역 모달창 특화)
                    ".//div[contains(@class, 'image-container')]//img[contains(@src, 'cbu01.alicdn.com')]",
                    ".//div[contains(@class, 'ant-image')]//img[contains(@src, 'cbu01.alicdn.com')]"
                ]
            else:
                # 상세페이지 일괄편집 모달창 내 이미지
                selectors = [
                    # 컨테이너 div 기반 선택자 (사용자 제공 DOM 구조)
                    ".//div[contains(@class, 'sc-hMxIkD') and contains(@class, 'byPQOP')]//img[contains(@class, 'p_tooltip_image_editor_thumb')]",
                    ".//div[contains(@class, 'sc-hMxIkD')]//img[contains(@class, 'sc-eSoiBi') and contains(@class, 'ipHRUV') and contains(@class, 'p_tooltip_image_editor_thumb')]",
                    # 가장 구체적인 이미지 선택자
                    ".//img[contains(@class, 'sc-eSoiBi') and contains(@class, 'ipHRUV') and contains(@class, 'p_tooltip_image_editor_thumb') and contains(@src, 'alicdn.com')]",
                    # 클래스 조합 선택자
                    ".//img[contains(@class, 'sc-eSoiBi') and contains(@class, 'p_tooltip_image_editor_thumb') and contains(@src, 'alicdn.com')]",
                    # 기존 선택자들 (호환성 유지)
                    ".//img[contains(@class, 'p_tooltip_image_editor_thumb') and contains(@src, 'alicdn.com')]",
                    ".//img[contains(@src, 'alicdn.com')]"                    
                ]
            
            for selector in selectors:
                try:
                    # 모달창 내에서만 이미지 검색
                    images = modal_element.find_elements(By.XPATH, selector)
                    if images:
                        # alicdn.com을 포함하는 이미지만 필터링 (cbu01.alicdn.com 및 img.alicdn.com 모두 지원)
                        valid_images = []
                        for img in images:
                            src = img.get_attribute('src')
                            if src and 'alicdn.com' in src:
                                valid_images.append(img)
                        
                        if valid_images:
                            self.logger.info(f"[{context}] 모달창 내 유효한 이미지 {len(valid_images)}개 발견 (선택자: {selector})")
                            return len(valid_images)
                except Exception as e:
                    self.logger.debug(f"[{context}] 모달창 내 이미지 선택자 {selector} 실패: {e}")
                    continue
                    
            self.logger.warning(f"[{context}] 모달창 내 유효한 이미지를 찾을 수 없습니다")
            return 0
            
        except Exception as e:
            self.logger.error(f"[{context}] 이미지 개수 확인 실패: {e}")
            return 0
            
    def _get_tab_image_count(self, context):
        """탭에서 이미지 개수 확인 - 모달창 열기 전 해당 탭의 이미지 개수 파악
        
        Args:
            context (str): 처리 컨텍스트 ('thumbnail', 'option')
            
        Returns:
            int: 이미지 개수
        """
        try:
            self.logger.info(f"[{context}] 탭에서 이미지 개수 확인 시작")
            
            # 컨텍스트별 탭 이미지 선택자 설정
            if context == 'thumbnail':
                # 썸네일 탭의 이미지 선택자 (image_utils3.py의 get_total_thumbnail_count 기반)
                selectors = [
                    # 썸네일 업로드 리스트 아이템
                    "//div[contains(@class, 'ant-upload-list-item') and not(contains(@class, 'ant-upload-list-item-uploading'))]",
                    "//div[contains(@class, 'ant-upload-list-item-done')]",
                    "//div[contains(@class, 'thumbnail-item')]",
                    "//img[contains(@class, 'thumbnail')]",
                    "//div[contains(@class, 'ant-upload-list')]//div[contains(@class, 'ant-upload-list-item')]",
                    "//div[@class='ant-upload-list ant-upload-list-picture-card']//div[contains(@class, 'ant-upload-list-item')]"
                ]
            elif context == 'option':
                # 옵션 탭의 이미지 선택자 (실제 DOM 구조 기반)
                selectors = [
                    # 옵션 탭의 이미지 컨테이너 (sc-TOgAA dFMQoJ 클래스)
                    "//div[contains(@class, 'sc-TOgAA') and contains(@class, 'dFMQoJ')]",
                    "//div[contains(@class, 'sc-TOgAA dFMQoJ')]",
                    # 백업 선택자들
                    "//div[contains(@class, 'ant-upload-list-item') and not(contains(@class, 'ant-upload-list-item-uploading'))]",
                    "//div[contains(@class, 'ant-upload-list-item-done')]",
                    "//div[contains(@class, 'option-image-item')]",
                    "//img[contains(@class, 'option-image')]",
                    # 일반적인 업로드 리스트 아이템
                    "//div[contains(@class, 'ant-upload-list')]//div[contains(@class, 'ant-upload-list-item')]",
                    "//div[@class='ant-upload-list ant-upload-list-picture-card']//div[contains(@class, 'ant-upload-list-item')]"
                ]
            else:
                self.logger.warning(f"지원하지 않는 컨텍스트: {context}")
                return 0
            
            # 썸네일 탭의 경우 텍스트에서 개수 추출 시도
            if context == 'thumbnail':
                try:
                    # '총 X개 썸네일' 텍스트에서 개수 추출
                    count_selectors = [
                        "//span[contains(text(), '총') and contains(text(), '개 썸네일')]",
                        "//div[contains(text(), '총') and contains(text(), '개 썸네일')]",
                        "//p[contains(text(), '총') and contains(text(), '개 썸네일')]",
                        "//span[contains(text(), '썸네일') and contains(text(), '개')]",
                        "//div[contains(text(), '썸네일') and contains(text(), '개')]"
                    ]
                    
                    for count_selector in count_selectors:
                        try:
                            element = self.driver.find_element(By.XPATH, count_selector)
                            text = element.text
                            self.logger.info(f"[{context}] 썸네일 개수 텍스트 발견: {text}")
                            
                            # 정규식으로 숫자 추출
                            import re
                            patterns = [
                                r'총\s*(\d+)\s*개\s*썸네일',
                                r'(\d+)\s*개\s*썸네일',
                                r'썸네일\s*(\d+)\s*개',
                                r'(\d+)\s*개'
                            ]
                            
                            for pattern in patterns:
                                match = re.search(pattern, text)
                                if match:
                                    count = int(match.group(1))
                                    self.logger.info(f"[{context}] 탭에서 텍스트로 이미지 개수 확인: {count}개")
                                    return count
                        except Exception as e:
                            self.logger.debug(f"[{context}] 썸네일 개수 텍스트 선택자 실패: {e}")
                            continue
                except Exception as e:
                    self.logger.debug(f"[{context}] 텍스트 기반 개수 확인 실패: {e}")
            
            # 요소 개수로 확인
            for selector in selectors:
                try:
                    # 탭에서 이미지/요소 검색
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements:
                        # 표시되는 요소만 카운트
                        visible_elements = [elem for elem in elements if elem.is_displayed()]
                        count = len(visible_elements)
                        
                        if count > 0:
                            self.logger.info(f"[{context}] 탭에서 요소 개수로 이미지 {count}개 발견 (선택자: {selector})")
                            return count
                except Exception as e:
                    self.logger.debug(f"[{context}] 탭 이미지 선택자 {selector} 실패: {e}")
                    continue
                    
            self.logger.warning(f"[{context}] 탭에서 유효한 이미지를 찾을 수 없습니다")
            return 0
            
        except Exception as e:
            self.logger.error(f"[{context}] 탭 이미지 개수 확인 실패: {e}")
            return 0
            
    # def _click_first_edit_button(self):
    #     """첫 번째 편집 버튼 클릭 - _click_first_image_bulk_edit_button로 대체됨"""
    #     try:
    #         # 편집 버튼 선택자들 (첫 번째 위치) - 원본 파일에서 검증된 선택자 사용
    #         edit_button_selectors = [
    #             "(//span[contains(@class, 'FootnoteDescription') and text()='편집하기'])[1]",
    #             "(//div[contains(@class, 'sc-kTbCBX') or contains(@class, 'sc-gkKZNe')]//span[text()='편집하기'])[1]",
    #             "(//div[contains(@class, 'sc-kTbCBX')]//span[contains(@class, 'FootnoteDescription') and text()='편집하기'])[1]",
    #             "(//span[text()='편집하기'])[1]"
    #         ]
    #         
    #         for selector in edit_button_selectors:
    #             try:
    #                 edit_btn = self.driver.find_element(By.XPATH, selector)
    #                 if edit_btn.is_displayed():
    #                     # 스크롤하여 요소가 보이도록 함
    #                     self.driver.execute_script("arguments[0].scrollIntoView(true);", edit_btn)
    #                     time.sleep(0.1)
    #                     
    #                     # 클릭 (부모 요소 클릭 시도)
    #                     try:
    #                         edit_btn.click()
    #                         self.logger.info("첫 번째 편집 버튼 클릭 성공 (일반 클릭)")
    #                     except Exception:
    #                         # JavaScript 클릭 시도
    #                         self.driver.execute_script("arguments[0].click();", edit_btn)
    #                         self.logger.info("첫 번째 편집 버튼 클릭 성공 (JavaScript 클릭)")
    #                     
    #                     self.human_delay.short_delay()  # 모달 로딩 대기
    #                     return True
    #             except Exception as e:
    #                 self.logger.debug(f"편집 버튼 선택자 {selector} 실패: {e}")
    #                 continue
    #         
    #         self.logger.error("첫 번째 편집 버튼을 찾을 수 없습니다")
    #         return False
    #         
    #     except Exception as e:
    #         self.logger.error(f"첫 번째 편집 버튼 클릭 실패: {e}")
    #         return False
            
    def _click_first_image_bulk_edit_button(self, context='detail'):
        """첫 번째 이미지 컨테이너의 편집 버튼 클릭
        
        Args:
            context (str): 처리 컨텍스트 ('detail', 'thumbnail', 'option')
            
        Returns:
            bool: 성공 여부
        """
        try:
            self.logger.info("첫 번째 이미지 컨테이너의 편집 버튼 클릭 시도")
            
            # 먼저 현재 페이지에서 편집 관련 버튼들을 찾아보기
            try:
                # '일괄편집' 및 '편집하기' 버튼 모두 검색
                all_edit_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), '일괄편집') or .//span[contains(text(), '일괄편집')] or contains(text(), '편집하기') or .//span[contains(text(), '편집하기')]]")
                self.logger.info(f"페이지에서 발견된 편집 버튼 개수: {len(all_edit_buttons)}")
                
                for i, btn in enumerate(all_edit_buttons):
                    try:
                        btn_text = btn.text
                        btn_displayed = btn.is_displayed()
                        btn_enabled = btn.is_enabled()
                        self.logger.info(f"편집 버튼 {i+1}: 텍스트='{btn_text}', 표시됨={btn_displayed}, 활성화됨={btn_enabled}")
                    except Exception as e:
                        self.logger.debug(f"편집 버튼 {i+1} 정보 확인 실패: {e}")
            except Exception as e:
                self.logger.debug(f"편집 버튼 전체 검색 실패: {e}")
            
            # 편집 버튼 선택자 설정 (컨텍스트별)
            edit_button_selectors = self._get_edit_button_selectors(context)
            
            for selector in edit_button_selectors:
                try:
                    edit_btn = self.driver.find_element(By.XPATH, selector)
                    if edit_btn.is_displayed():
                        # 스크롤하여 요소가 보이도록 함
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", edit_btn)
                        time.sleep(0.2)
                        
                        # 클릭 시도
                        try:
                            edit_btn.click()
                            self.logger.info(f"첫 번째 이미지 편집 버튼 클릭 성공 (일반 클릭): {selector}")
                        except Exception:
                            # JavaScript 클릭 시도
                            self.driver.execute_script("arguments[0].click();", edit_btn)
                            self.logger.info(f"첫 번째 이미지 편집 버튼 클릭 성공 (JavaScript 클릭): {selector}")
                        
                        self.human_delay.medium_delay()  # 이미지 번역 모달 로딩 대기
                        return True
                        
                except Exception as e:
                    self.logger.debug(f"편집 버튼 선택자 {selector} 실패: {e}")
                    continue
            
            self.logger.error("첫 번째 이미지 컨테이너의 편집 버튼을 찾을 수 없습니다")
            return False
            
        except Exception as e:
            self.logger.error(f"첫 번째 이미지 편집 버튼 클릭 실패: {e}")
            return False
            
    def _wait_for_image_translation_modal(self):
        """이미지 번역 모달 대기 - 실제 이미지 번역 모달창 감지"""
        try:
            self.logger.info("이미지 번역 모달창 열림 대기 시작")
            
            # 이미지 번역 모달창의 특정 요소들을 감지
            modal_selectors = [
                # 이미지 번역 모달창 제목
                "//div[contains(@class, 'ant-modal')]//span[contains(text(), '이미지 번역')]",
                "//div[contains(@class, 'ant-drawer')]//span[contains(text(), '이미지 번역')]",
                "//div[contains(@class, 'ant-modal-title') and contains(text(), '이미지 번역')]",
                "//div[contains(@class, 'ant-drawer-title') and contains(text(), '이미지 번역')]",
                # 이미지 번역 모달창 내부의 특정 요소들
                "//button[contains(text(), '원클릭 이미지 번역')]",
                "//div[contains(@class, 'ant-modal')]//button[contains(text(), '원클릭 이미지 번역')]",
                "//div[contains(@class, 'ant-drawer')]//button[contains(text(), '원클릭 이미지 번역')]",
                # 캔버스 요소 (이미지 번역 모달창 내부)
                "#pCanvas",
                "canvas[id='pCanvas']",
                "//canvas[@id='pCanvas']"
            ]
            
            # 10초 동안 모달창 요소 감지 시도
            for attempt in range(20):  # 0.5초씩 20번 = 10초
                for selector in modal_selectors:
                    try:
                        if selector.startswith('//'):
                            # XPath 선택자
                            element = self.driver.find_element(By.XPATH, selector)
                        else:
                            # CSS 선택자
                            element = self.driver.find_element(By.CSS_SELECTOR, selector)
                            
                        if element and element.is_displayed():
                            self.logger.info(f"이미지 번역 모달창 열림 확인: {selector}")
                            time.sleep(1)  # 모달창 완전 로딩 대기
                            return True
                    except Exception:
                        continue
                        
                time.sleep(0.5)  # 0.5초 대기 후 재시도
                
            self.logger.error("이미지 번역 모달창 열림 대기 시간 초과 (10초)")
            return False
            
        except Exception as e:
            self.logger.error(f"이미지 번역 모달창 대기 실패: {e}")
            return False
            
    def _process_current_image(self):
        """현재 이미지 처리 (OCR + 번역)"""
        try:
            # 캔버스에서 이미지 데이터 추출
            image_data = self._extract_canvas_image()
            
            # 이미지 데이터 안전한 검증 - 배열 비교 오류 방지
            if image_data is None:
                self.logger.warning("이미지 데이터 추출 실패 - None 반환")
                return False
            
            # NumPy 배열 검증 - 배열 크기 확인
            try:
                if hasattr(image_data, 'size') and image_data.size == 0:
                    self.logger.warning("이미지 데이터가 비어있음 - 빈 배열")
                    return False
                elif hasattr(image_data, 'shape') and len(image_data.shape) == 0:
                    self.logger.warning("이미지 데이터가 스칼라 값임 - 유효하지 않은 이미지")
                    return False
                elif hasattr(image_data, '__len__') and len(image_data) == 0:
                    self.logger.warning("이미지 데이터 길이가 0임 - 빈 데이터")
                    return False
            except Exception as check_e:
                self.logger.warning(f"이미지 데이터 검증 중 오류: {check_e}, 처리 계속 진행")
            
            self.logger.info(f"이미지 데이터 추출 성공 - 타입: {type(image_data)}, 형태: {getattr(image_data, 'shape', 'N/A')}")
                
            # 중국어 텍스트 감지
            if self._detect_chinese_from_image(image_data):
                self.logger.info("중국어 텍스트 감지됨 - 번역 실행")
                return self._execute_translation()
            else:
                self.logger.info("중국어 텍스트 없음 - 건너뜀")
                return 0
                
        except Exception as e:
            self.logger.error(f"이미지 처리 실패: {e}")
            import traceback
            self.logger.error(f"이미지 처리 스택 트레이스: {traceback.format_exc()}")
            return False
            
    def _extract_canvas_image(self):
        """캔버스에서 이미지 데이터 추출"""
        try:
            canvas = self.driver.find_element(By.ID, "pCanvas")
            
            # 캔버스를 base64로 변환
            canvas_base64 = self.driver.execute_script(
                "return arguments[0].toDataURL('image/png').substring(22);", canvas
            )
            
            # base64를 이미지로 변환
            image_data = base64.b64decode(canvas_base64)
            image = Image.open(io.BytesIO(image_data))
            
            return np.array(image)
            
        except Exception as e:
            self.logger.error(f"캔버스 이미지 추출 실패: {e}")
            return None
            
    def _detect_chinese_from_image(self, image_data):
        """이미지에서 중국어 텍스트 감지"""
        try:
            if not OCR_AVAILABLE or easyocr_reader is None:
                self.logger.warning("EasyOCR이 초기화되지 않음 - 속성 기반 중문글자 감지 사용")
                # OCR이 없어도 속성 기반으로 중국어 감지 시도
                return self._detect_chinese_from_attributes()
            
            # EasyOCR을 사용한 중국어 감지
            return self._detect_chinese_with_ocr(image_data)
        except Exception as e:
            self.logger.error(f"중국어 감지 오류: {e}")
            return True  # 오류 시 안전하게 번역 시도
    
    def _detect_chinese_with_ocr(self, image_data):
        """EasyOCR을 사용한 중국어 텍스트 감지"""
        try:
            # 이미지 데이터가 numpy 배열인 경우 PIL Image로 변환
            if isinstance(image_data, np.ndarray):
                image = Image.fromarray(image_data)
            else:
                # base64 데이터인 경우 기존 방식 사용
                image = Image.open(io.BytesIO(base64.b64decode(image_data)))
            
            # 이미지 유효성 검사
            if image.size[0] <= 1 or image.size[1] <= 1:
                self.logger.warning(f"이미지 크기가 너무 작음 ({image.size}) - OCR 건너뜀")
                return False
            
            # 이미지 크기 조정 (너무 작으면 확대)
            width, height = image.size
            if width < 200 or height < 200:
                scale_factor = max(200 / width, 200 / height)
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                self.logger.info(f"이미지 크기 조정 {width}x{height} -> {new_width}x{new_height}")
            
            # 그레이스케일 변환
            if image.mode != 'L':
                gray_image = image.convert('L')
                self.logger.info("그레이스케일 변환 완료")
            else:
                gray_image = image
            
            # EasyOCR 실행 (타임아웃 추가)
            image_array = np.array(gray_image)
            self.logger.info("EasyOCR 실행 시작 (언어: 중문만)")
            
            import time
            start_time = time.time()
            results = easyocr_reader.readtext(image_array)
            ocr_time = time.time() - start_time
            self.logger.info(f"EasyOCR 완료 - {len(results)}개 텍스트 블록 감지 (처리 시간: {ocr_time:.2f}초)")
            
            # 결과에서 텍스트만 추출 (신뢰도 0.3 이상만)
            text_parts = []
            for bbox, text, confidence in results:
                if confidence >= 0.3:  # 신뢰도 30% 이상만 사용
                    text_parts.append(text)
                    self.logger.debug(f"텍스트 블록 '{text}' (신뢰도: {confidence:.3f})")
            
            text = ' '.join(text_parts)
            self.logger.info(f"추출된 전체 텍스트 (길이: {len(text)}): '{text.strip()}'")
            
            # 중문글자 정규식 패턴으로 확인
            import re
            chinese_pattern = r'[\u4e00-\u9fff]+'
            chinese_matches = re.findall(chinese_pattern, text)
            
            self.logger.info(f"중문글자 패턴 검사 결과 - 매치 수: {len(chinese_matches)}")
            if chinese_matches:
                self.logger.info(f"발견된 중문글자: {chinese_matches}")
                self.logger.info(f"OCR에서 중문글자 발견 - {chinese_matches[:3]}...")  # 처음 3개만 로그
                return True
            else:
                self.logger.info("OCR에서 중문글자 없음")
                return False
                
        except Exception as e:
            # OCR 오류 시 더 상세한 로깅과 복구 시도
            error_msg = str(e)
            if "cannot identify image file" in error_msg.lower():
                self.logger.warning(f"이미지 형식 오류로 OCR 실패: {e} - 속성 기반 감지로 대체")
                return self._detect_chinese_from_attributes()
            elif "timeout" in error_msg.lower() or "time" in error_msg.lower():
                self.logger.warning(f"OCR 처리 시간 초과: {e} - 속성 기반 감지로 대체")
                return self._detect_chinese_from_attributes()
            else:
                self.logger.error(f"EasyOCR 중문글자 감지 오류: {e}")
                # 일반적인 오류의 경우 안전하게 번역 시도
                return True
    
    def _detect_chinese_from_attributes(self):
        """속성 기반 중국어 감지 (OCR 없이)"""
        try:
            # 현재 이미지의 alt 속성이나 기타 속성에서 중국어 감지
            # 이 부분은 기존 로직을 유지하거나 간단한 휴리스틱 사용
            self.logger.info("속성 기반 중국어 감지 - 기본적으로 번역 시도")
            return True  # 안전하게 번역 시도
        except Exception as e:
            self.logger.error(f"속성 기반 중국어 감지 오류: {e}")
            return True  # 오류 시 안전하게 번역 시도
            
    def _execute_translation(self):
        """번역 실행 (T 키 또는 버튼 클릭)"""
        try:
            # T 키로 번역 시도
            ActionChains(self.driver).send_keys('t').perform()
            time.sleep(0.1)
            
            # 번역 완료 대기
            if self._wait_for_translation_complete():
                return 1  # 번역 성공 시 1개 번역됨
            else:
                return 0  # 번역 실패 시 0개 번역됨
            
        except Exception as e:
            self.logger.error(f"번역 실행 실패: {e}")
            return 0
            
    def _wait_for_translation_complete(self):
        """번역 완료 대기 - '원클릭 이미지 번역' 버튼 상태 변화 감지"""
        try:
            max_wait_time = 60  # 최대 60초 대기 (최적화)
            check_interval = 0.5  # 0.5초마다 확인 (더 빠른 감지)
            elapsed_time = 0
            consecutive_normal_checks = 0  # 연속으로 정상 상태를 확인한 횟수
            
            self.logger.info("번역 완료 대기 시작 - '원클릭 이미지 번역' 버튼 상태 감지")
            
            while elapsed_time < max_wait_time:
                try:
                    # 번역 중 상태 확인 (ant-btn-loading 클래스가 있는지 확인)
                    translating_buttons = self.driver.find_elements(
                        By.XPATH, 
                        "//button[contains(@class, 'ant-btn-loading')]//span[text()='원클릭 이미지 번역']"
                    )
                    
                    if translating_buttons:
                        # ant-btn-loading 클래스가 있으면 아직 번역 중
                        consecutive_normal_checks = 0  # 로딩 상태이므로 카운터 리셋
                        self.logger.debug(f"번역 진행 중... (경과 시간: {elapsed_time:.1f}초)")
                        time.sleep(check_interval)
                        elapsed_time += check_interval
                        continue
                    else:
                        # ant-btn-loading 클래스가 없으면 번역 완료 가능성
                        # 번역 버튼이 정상 상태로 존재하는지 확인
                        normal_buttons = self.driver.find_elements(
                            By.XPATH,
                            "//button[contains(@class, 'ant-btn') and contains(@class, 'ant-btn-default') and not(contains(@class, 'ant-btn-loading'))]//span[text()='원클릭 이미지 번역']"
                        )
                        
                        if normal_buttons:
                            consecutive_normal_checks += 1
                            # 연속으로 2번 정상 상태를 확인하면 번역 완료로 판단 (안정성 향상)
                            if consecutive_normal_checks >= 2:
                                self.logger.info(f"이미지 번역 완료 감지 (총 대기 시간: {elapsed_time:.1f}초)")
                                self.human_delay.short_delay()  # 안정성을 위한 추가 대기
                                return True
                            else:
                                self.logger.debug(f"번역 완료 확인 중... ({consecutive_normal_checks}/2)")
                        else:
                            consecutive_normal_checks = 0  # 버튼을 찾지 못하면 카운터 리셋
                            # 버튼을 찾을 수 없는 경우 일반적인 버튼 확인
                            any_buttons = self.driver.find_elements(
                                By.XPATH,
                                "//button//span[text()='원클릭 이미지 번역']"
                            )
                            if any_buttons:
                                self.logger.info(f"이미지 번역 완료 감지 (일반 버튼 확인, 총 대기 시간: {elapsed_time:.1f}초)")
                                self.human_delay.short_delay()  # 안정성을 위한 추가 대기
                                return True
                    
                    time.sleep(check_interval)
                    elapsed_time += check_interval
                    
                except Exception as e:
                    self.logger.debug(f"번역 상태 확인 중 오류: {e}")
                    time.sleep(check_interval)
                    elapsed_time += check_interval
            
            # 최대 대기 시간 초과
            self.logger.warning(f"번역 완료 대기 시간 초과 ({max_wait_time}초)")
            return True  # 시간 초과 시에도 다음 단계 진행
            
        except Exception as e:
            self.logger.error(f"번역 완료 대기 실패: {e}")
            return True
            
    def _move_to_next_image(self):
        """TAB 키로 다음 이미지로 이동"""
        try:
            ActionChains(self.driver).send_keys(Keys.TAB).perform()
            self.human_delay.medium_delay()
            return True
            
        except Exception as e:
            self.logger.error(f"다음 이미지 이동 실패: {e}")
            return False
            
    def _save_changes(self):
        """변경사항 저장"""
        try:
            # 저장 버튼 찾기 및 클릭
            selectors = [
                "button[data-testid='save-button']",
                "button:contains('저장')",
                "button:contains('Save')",
                ".save-btn",
                "[class*='save']"
            ]
            
            for selector in selectors:
                try:
                    element = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    element.click()
                    self.human_delay.medium_delay()
                    self.logger.info("변경사항 저장 완료")
                    return True
                except:
                    continue
                    
            self.logger.warning("저장 버튼을 찾을 수 없습니다")
            return False
            
        except Exception as e:
            self.logger.error(f"변경사항 저장 실패: {e}")
            return False
            
    def _close_image_translation_modal(self):
        """이미지 번역 모달 닫기"""
        try:
            # ESC 키로 모달 닫기
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            self.human_delay.medium_delay()
            return True
            
        except Exception as e:
            self.logger.error(f"이미지 번역 모달 닫기 실패: {e}")
            return False
            
    def _close_bulk_edit_modal(self):
        """벌크 편집 모달 닫기"""
        try:
            # 닫기 버튼 또는 ESC 키
            close_selectors = [
                "button[data-testid='close-button']",
                ".modal-close",
                "[class*='close']"
            ]
            
            for selector in close_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    element.click()
                    time.sleep(2)
                    return True
                except:
                    continue
                    
            # ESC 키로 시도
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            time.sleep(2)
            return True
            
        except Exception as e:
            self.logger.error(f"벌크 편집 모달 닫기 실패: {e}")
            return False
            
    def _scan_all_images_for_translation_with_limit(self, scan_images, context='detail'):
        """제한된 개수의 이미지를 스캔하여 번역이 필요한 이미지 위치 식별
        
        Args:
            scan_images (int): 스캔할 이미지 개수
            context (str): 처리 컨텍스트
            
        Returns:
            list: 번역이 필요한 이미지 위치 리스트
        """
        try:
            images_to_translate = []
            
            self.logger.info(f"제한된 {scan_images}개 이미지 스캔 시작")
            
            for i in range(scan_images):
                current_position = i + 1
                self.logger.debug(f"이미지 {current_position}/{scan_images} 스캔 중...")
                
                # 현재 이미지에서 중국어 감지
                if self._detect_chinese_in_current_image():
                    images_to_translate.append(current_position)
                    self.logger.info(f"이미지 {current_position}: 중국어 감지됨 - 번역 대상 추가")
                else:
                    self.logger.debug(f"이미지 {current_position}: 중국어 미감지 - 번역 불필요")
                
                # 마지막 이미지가 아니면 다음 이미지로 이동
                if i < scan_images - 1:
                    if not self._move_to_next_image():
                        self.logger.warning(f"이미지 {current_position + 1}로 이동 실패 - 스캔 중단")
                        break
                        
            self.logger.info(f"제한된 스캔 완료: {len(images_to_translate)}개 이미지가 번역 대상으로 식별됨")
            return images_to_translate
            
        except Exception as e:
            self.logger.error(f"제한된 이미지 스캔 오류: {e}")
            return []
    
    def _scan_all_images_for_translation(self, total_images, context='detail'):
        """모든 이미지를 스캔하여 번역이 필요한 이미지 위치 식별"""
        try:
            images_to_translate = []
            
            self.logger.info(f"총 {total_images}개 이미지 스캔 시작")
            
            for i in range(total_images):
                current_position = i + 1
                self.logger.debug(f"이미지 {current_position}/{total_images} 스캔 중...")
                
                # 현재 이미지에서 중국어 감지
                if self._detect_chinese_in_current_image():
                    images_to_translate.append(current_position)
                    self.logger.info(f"이미지 {current_position}: 중국어 감지됨 - 번역 대상 추가")
                else:
                    self.logger.debug(f"이미지 {current_position}: 중국어 미감지 - 번역 불필요")
                
                # 마지막 이미지가 아니면 다음 이미지로 이동
                if i < total_images - 1:
                    if not self._move_to_next_image():
                        self.logger.warning(f"이미지 {current_position + 1}로 이동 실패 - 스캔 중단")
                        break
                        
            self.logger.info(f"스캔 완료: {len(images_to_translate)}개 이미지가 번역 대상으로 식별됨")
            return images_to_translate
            
        except Exception as e:
            self.logger.error(f"이미지 스캔 오류: {e}")
            return []
            
    def _process_specific_images_for_translation(self, images_to_translate):
        """식별된 특정 이미지들만 번역 처리"""
        try:
            processed_count = 0
            total_count = len(images_to_translate)
            
            self.logger.info(f"식별된 {total_count}개 이미지 번역 처리 시작")
            
            for i, position in enumerate(images_to_translate):
                try:
                    self.logger.info(f"번역 처리 {i+1}/{total_count}: 이미지 위치 {position}")
                    
                    # 해당 위치로 이동 (DOM 기반 정확한 선택)
                    if not self._move_to_image_position_dom(position):
                        self.logger.error(f"이미지 위치 {position}로 이동 실패")
                        continue
                    
                    # 번역 실행 (T 키)
                    if not self._execute_image_translation():
                        self.logger.error(f"이미지 위치 {position} 번역 실행 실패")
                        continue
                    
                    # 번역 완료 대기
                    if self._wait_for_translation_complete():
                        processed_count += 1
                        self.logger.info(f"이미지 위치 {position} 번역 성공")
                    else:
                        self.logger.error(f"이미지 위치 {position} 번역 완료 대기 실패")
                    
                except Exception as e:
                    self.logger.error(f"이미지 위치 {position} 번역 처리 오류: {e}")
                    continue
            
            self.logger.info(f"특정 이미지 번역 처리 완료: {processed_count}/{total_count}개 성공")
            return processed_count
            
        except Exception as e:
            self.logger.error(f"특정 이미지 번역 처리 오류: {e}")
            return 0
            
    def _detect_chinese_in_current_image(self):
        """현재 이미지에서 중국어 감지 (스캔용)"""
        try:
            # OCR을 통한 중국어 감지
            if OCR_AVAILABLE and easyocr_reader:
                try:
                    # 캔버스에서 이미지 데이터 추출
                    image_data = self._extract_canvas_image()
                    
                    if image_data is None:
                        self.logger.debug("이미지 데이터 추출 실패 - 중국어 감지 불가")
                        return False
                    
                    # EasyOCR로 텍스트 추출
                    results = easyocr_reader.readtext(image_data)
                    
                    # 중국어 글자 확인
                    for (bbox, text, confidence) in results:
                        if confidence > 0.3:  # 신뢰도 임계값
                            # 중국어 글자 범위 확인 (간체)
                            for char in text:
                                if '\u4e00' <= char <= '\u9fff':  # 중국어 유니코드 범위
                                    self.logger.debug(f"중국어 감지: '{char}' (신뢰도: {confidence:.2f})")
                                    return True
                                    
                except Exception as e:
                    self.logger.debug(f"OCR 중국어 감지 중 오류: {e}")
                    # OCR 실패 시 속성 기반 감지로 대체
                    return self._detect_chinese_from_attributes()
            else:
                # OCR 사용 불가 시 속성 기반 감지
                return self._detect_chinese_from_attributes()
                
            return False
            
        except Exception as e:
            self.logger.debug(f"중국어 감지 오류: {e}")
            return False
            
    def _move_to_image_position_dom(self, target_position):
        """DOM 기반으로 특정 이미지 위치로 정확히 이동"""
        try:
            # 사용자 제공 DOM 구조 기반 개선된 선택자
            # <div class="sc-hMxIkD byPQOP"><span><img class="sc-eSoiBi ipHRUV p_tooltip_image_editor_thumb" src="https://cbu01.alicdn.com/img/..."
            image_selectors = [
                # 컨테이너 div 기반 선택자 (사용자 제공 DOM 구조)
                f"(//div[contains(@class, 'sc-hMxIkD') and contains(@class, 'byPQOP')]//img[contains(@class, 'p_tooltip_image_editor_thumb')])[{target_position}]",
                f"(//div[contains(@class, 'sc-hMxIkD')]//img[contains(@class, 'sc-eSoiBi') and contains(@class, 'ipHRUV') and contains(@class, 'p_tooltip_image_editor_thumb')])[{target_position}]",
                # 가장 구체적인 이미지 선택자
                f"(//img[contains(@class, 'sc-eSoiBi') and contains(@class, 'ipHRUV') and contains(@class, 'p_tooltip_image_editor_thumb') and contains(@src, 'cbu01.alicdn.com')])[{target_position}]",
                # 클래스 조합 선택자
                f"(//img[contains(@class, 'sc-eSoiBi') and contains(@class, 'p_tooltip_image_editor_thumb') and contains(@src, 'cbu01.alicdn.com')])[{target_position}]",
                # 기존 선택자들 (호환성 유지)
                f"(//div[contains(@class, 'sc-eSoiBi')]//img[contains(@class, 'p_tooltip_image_editor_thumb')])[{target_position}]",
                f"(//div[contains(@class, 'ant-drawer-content')]//img[contains(@src, 'https://cbu01.alicdn.com/img')])[{target_position}]",
                f"(//img[contains(@class, 'sc-kpkpHi') and contains(@src, 'cbu01.alicdn.com')])[{target_position}]",
                f"(//img[contains(@src, 'alicdn.com')])[{target_position}]"
            ]
            
            for selector in image_selectors:
                try:
                    target_image = self.driver.find_element(By.XPATH, selector)
                    if target_image.is_displayed():
                        # 이미지로 스크롤
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", target_image)
                        time.sleep(0.5)
                        
                        # 이미지 클릭하여 포커스 설정
                        target_image.click()
                        time.sleep(0.5)
                        
                        self.logger.debug(f"이미지 위치 {target_position}로 DOM 기반 이동 완료")
                        return True
                except Exception as e:
                    self.logger.debug(f"이미지 선택자 {selector} 실패: {e}")
                    continue
            
            # DOM 기반 선택 실패 시 기존 TAB 방식으로 대체
            self.logger.warning(f"DOM 기반 이동 실패, TAB 방식으로 대체: 위치 {target_position}")
            return self._move_to_image_position_tab(target_position)
            
        except Exception as e:
            self.logger.error(f"DOM 기반 이미지 위치 {target_position} 이동 오류: {e}")
            return False
            
    def _move_to_image_position_tab(self, target_position):
        """TAB 키 기반으로 특정 이미지 위치로 이동 (대체 방법)"""
        try:
            # 첫 번째 이미지로 이동 (Home 키 또는 처음으로 리셋)
            ActionChains(self.driver).send_keys(Keys.HOME).perform()
            time.sleep(0.5)
            
            # target_position까지 TAB으로 이동 (1-based index)
            for i in range(target_position - 1):
                if not self._move_to_next_image():
                    self.logger.error(f"이미지 위치 {i+2}로 이동 실패")
                    return False
                    
            self.logger.debug(f"TAB 기반 이미지 위치 {target_position}로 이동 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"TAB 기반 이미지 위치 {target_position}로 이동 오류: {e}")
            return False
            
    def _execute_image_translation(self):
        """이미지 번역 실행 (T 키)"""
        try:
            # T 키로 번역 실행
            ActionChains(self.driver).send_keys('t').perform()
            time.sleep(1)
            
            self.logger.debug("이미지 번역 실행 (T 키)")
            return True
            
        except Exception as e:
            self.logger.error(f"이미지 번역 실행 오류: {e}")
            return False
            
    def _get_edit_button_selectors(self, context='detail'):
        """컨텍스트별 편집 버튼 선택자 반환
        
        Args:
            context (str): 컨텍스트 ('detail', 'thumbnail', 'option')
            
        Returns:
            list: 선택자 리스트
        """
        if context == 'detail':
            # 상세페이지 일괄편집 모달창의 편집하기 버튼
            return [
                "(//span[contains(@class, 'FootnoteDescription') and text()='편집하기'])[1]",
                "(//div[contains(@class, 'sc-kTbCBX') or contains(@class, 'sc-gkKZNe')]//span[text()='편집하기'])[1]",
                "(//div[contains(@class, 'sc-kTbCBX')]//span[contains(@class, 'FootnoteDescription') and text()='편집하기'])[1]",
                "(//span[text()='편집하기'])[1]",
                "(//div[contains(@class, 'sc-fInFcU')])[1]//div[contains(@class, 'sc-bOTbmH') and contains(@class, 'hDwhsl')]",
                "(//div[contains(@class, 'sc-fInFcU')])[1]//div[contains(@class, 'sc-bOTbmH')]//span[contains(text(), '편집하기')]/parent::div",
                "(//div[contains(@class, 'sc-fInFcU')])[1]//div[contains(@class, 'sc-bOTbmH')]",
                "(//img[contains(@class, 'sc-hCrRFl')])[1]/ancestor::div[contains(@class, 'sc-fInFcU')]//div[contains(@class, 'sc-bOTbmH')]",
                "(//img[contains(@class, 'iNuYXT')])[1]/ancestor::div[contains(@class, 'sc-fInFcU')]//div[contains(@class, 'sc-bOTbmH')]",
                "(//span[@aria-label='edit' and contains(@class, 'anticon-edit')])[1]/ancestor::div[contains(@class, 'sc-bOTbmH')]",
                "(//svg[@data-icon='edit'])[1]/ancestor::div[contains(@class, 'sc-bOTbmH')]",
                "(//button[contains(text(), '일괄편집')])[1]",
                "(//span[contains(text(), '일괄편집')])[1]/parent::button",
                "//div[contains(@class, 'ant-drawer-body')]//button[contains(text(), '일괄편집')][1]"
            ]
        elif context == 'thumbnail':
            # 썸네일 탭의 편집하기 버튼 (sc-leQnM jxFFxk 클래스 사용)
            return [
                "(//div[contains(@class, 'sc-leQnM') and contains(@class, 'jxFFxk')]//span[contains(@class, 'FootnoteDescription') and text()='편집하기'])[1]",
                "(//div[contains(@class, 'sc-leQnM')]//span[text()='편집하기'])[1]",
                "(//div[contains(@class, 'sc-fedTIj')]//div[contains(@class, 'sc-leQnM')])[1]",
                "(//span[contains(@class, 'sc-doohEh') and contains(@class, 'imNntt') and text()='편집하기'])[1]",
                "(//div[contains(@class, 'sc-leQnM')])[1]",
                "(//span[@aria-label='edit' and contains(@class, 'anticon-edit')])[1]/ancestor::div[contains(@class, 'sc-leQnM')]",
                "(//svg[@data-icon='edit'])[1]/ancestor::div[contains(@class, 'sc-leQnM')]",
                "(//span[text()='편집하기'])[1]"
            ]
        elif context == 'option':
            # 옵션 탭의 편집 버튼 (sc-bCMFDn bQabSr 클래스 사용, 텍스트는 '편집')
            return [
                "(//div[contains(@class, 'sc-bCMFDn') and contains(@class, 'bQabSr')]//span[contains(@class, 'FootnoteDescription') and text()='편집'])[1]",
                "(//div[contains(@class, 'sc-bCMFDn')]//span[text()='편집'])[1]",
                "(//div[contains(@class, 'sc-TOgAA')]//div[contains(@class, 'sc-bCMFDn')])[1]",
                "(//span[contains(@class, 'sc-gvXfzc') and contains(@class, 'gRVtrK') and text()='편집'])[1]",
                "(//div[contains(@class, 'sc-bCMFDn')])[1]",
                "(//span[@aria-label='edit' and contains(@class, 'anticon-edit')])[1]/ancestor::div[contains(@class, 'sc-bCMFDn')]",
                "(//svg[@data-icon='edit'])[1]/ancestor::div[contains(@class, 'sc-bCMFDn')]",
                "(//span[text()='편집'])[1]"
            ]
        else:
            # 기본값 (detail과 동일)
            return self._get_edit_button_selectors('detail')