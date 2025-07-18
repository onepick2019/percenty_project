import logging
import time
import re
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

class ImageTranslationHandler:
    """이미지 번역 처리를 위한 핸들러 클래스"""
    
    def __init__(self, driver):
        self.driver = driver
        self.logger = logging.getLogger(__name__)
        
    def image_translate(self, action_value):
        """이미지 번역 처리 메인 메서드 - 기존 액션 형식 지원 + 새로운 순차 처리"""
        try:
            self.logger.info(f"이미지 번역 시작: {action_value}")
            
            # 액션 파싱
            action_info = self._parse_image_translate_action(action_value)
            if not action_info:
                self.logger.error("이미지 번역 액션 파싱 실패")
                return False
            
            # 벌크 편집 모달 열기
            if not self._open_bulk_edit_modal():
                return False
                
            try:
                # 이미지 번역 액션 처리
                success = self._process_image_translate_action(action_info)
                
                if success:
                    self.logger.info("이미지 번역 완료")
                else:
                    self.logger.error("이미지 번역 실패")
                
                return success
                
            finally:
                # 벌크 편집 모달 닫기
                self._close_bulk_edit_modal()
                
        except Exception as e:
            self.logger.error(f"이미지 번역 중 오류: {e}")
            return False
            
    def _parse_image_translate_action(self, action_value):
        """이미지 번역 액션 값 파싱 (기존 방식 호환)"""
        try:
            if not action_value or action_value.strip() == "":
                self.logger.warning("이미지 번역 액션 값이 비어있음")
                return None
            
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
                # "last:숫자" 형식인 경우
                elif pos.startswith('last:'):
                    try:
                        num = int(pos.split(':')[1])
                        positions.append(num)
                        self.logger.info(f"last 형식 파싱: {pos} -> {num}")
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
                # "auto_detect_chinese" 형식인 경우 (중국어 이미지 자동 감지)
                elif pos == 'auto_detect_chinese':
                    self.logger.info("중국어 이미지 자동 감지 모드")
                    positions.append('auto_detect_chinese')
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
            
        except Exception as e:
            self.logger.error(f"이미지 번역 액션 파싱 오류: {e}")
            return None
            
    def _process_image_translate_action(self, action_info):
        """이미지 번역 액션 처리 - 기존 방식과 새로운 방식 통합"""
        try:
            positions = action_info.get('positions', [])
            self.logger.info(f"이미지 번역 처리 시작 - 위치: {positions}")
            
            # 중문글자 자동 감지 모드인 경우
            if 'auto_detect_chinese' in positions:
                self.logger.info("중문글자 자동 감지 모드 실행")
                detected_positions = self._detect_chinese_images_in_bulk_modal()
                if detected_positions:
                    # auto_detect_chinese를 실제 감지된 위치들로 교체
                    positions = [pos for pos in positions if pos != 'auto_detect_chinese'] + detected_positions
                    self.logger.info(f"중문글자 감지 완료 - 번역할 이미지 위치: {detected_positions}")
                    # 감지된 위치들을 개별 처리
                    return self._process_specific_positions(positions)
                else:
                    self.logger.info("중문글자가 있는 이미지를 찾지 못했습니다")
                    return True  # 번역할 이미지가 없어도 성공으로 처리
            # sequential_all 모드인 경우 새로운 순차 처리 방식 사용
            elif 'sequential_all' in positions:
                return self._process_all_images_sequentially()
            else:
                # 기존 방식: 개별 위치 처리
                return self._process_specific_positions(positions)
                
        except Exception as e:
            self.logger.error(f"이미지 번역 액션 처리 오류: {e}")
            return False
            
    def _detect_chinese_images_in_bulk_modal(self):
        """
        일괄편집 모달창에서 중문글자가 있는 이미지들을 자동으로 감지
        
        Returns:
            list: 중문글자가 있는 이미지의 위치 번호 리스트
        """
        try:
            self.logger.info("일괄편집 모달에서 중문글자 이미지 감지 시작")
            
            # 이미지 선택자들 (일괄편집 모달창 내부의 실제 이미지만 선택)
            image_selectors = [
                # 일괄편집 모달창(ant-drawer) 내부의 실제 이미지만 선택
                "//div[contains(@class, 'ant-drawer')]//div[contains(@class, 'sc-hCrRFl') and contains(@class, 'dVjKzV')]//img[contains(@class, 'sc-kyDlHK')]",
                # 일괄편집 모달창(ant-drawer) 내부의 bLXrEr 클래스가 있는 실제 이미지만
                "//div[contains(@class, 'ant-drawer')]//img[contains(@class, 'sc-kyDlHK') and contains(@class, 'bLXrEr')]",
                # 일괄편집 모달창(ant-drawer) 내부의 alicdn.com 도메인 이미지만 (percenty.co.kr 제외)
                "//div[contains(@class, 'ant-drawer')]//img[contains(@src, 'alicdn.com')]",
                # 마지막 대안: 일괄편집 모달창(ant-drawer) 내부의 draggable="false" 속성이 있는 실제 이미지
                "//div[contains(@class, 'ant-drawer')]//img[@draggable='false' and contains(@class, 'sc-kyDlHK')]",
                # 추가 대안: 일괄편집 모달창(ant-drawer) 내부의 모든 img 태그 (더 넓은 범위)
                "//div[contains(@class, 'ant-drawer')]//img[not(contains(@src, 'percenty.co.kr'))]"
            ]
            
            all_images = []
            seen_images = set()  # 중복 제거를 위한 집합 (src 기반)
            seen_elements = set()  # 요소 자체 중복 제거
            
            for i, selector in enumerate(image_selectors):
                try:
                    self.logger.debug(f"이미지 선택자 {i+1} 시도: {selector}")
                    images = self.driver.find_elements(By.XPATH, selector)
                    self.logger.debug(f"이미지 선택자 {i+1}에서 {len(images)}개 이미지 발견")
                    
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
                                        self.logger.debug(f"percenty.co.kr 도메인 이미지 제외: {src[:100]}...")
                                        continue
                                    seen_images.add(src)
                                    seen_elements.add(element_id)
                                    all_images.append(img)
                                    self.logger.debug(f"유효한 이미지 추가: {src[:100]}...")
                        except Exception as e:
                            self.logger.debug(f"개별 이미지 처리 중 오류: {e}")
                            continue
                except Exception as e:
                    self.logger.debug(f"이미지 선택자 {i+1} 실패: {e}")
            
            if not all_images:
                self.logger.warning("일괄편집 모달에서 이미지를 찾을 수 없습니다")
                return []
            
            self.logger.info(f"총 {len(all_images)}개의 유효한 이미지 발견 (중복 제거 후)")
            
            chinese_image_positions = []
            
            for i, img_element in enumerate(all_images, 1):
                try:
                    # 이미지가 화면에 보이는지 확인
                    if not img_element.is_displayed():
                        self.logger.debug(f"이미지 {i}: 화면에 표시되지 않음")
                        continue
                    
                    # 이미지 크기 확인 (너무 작은 이미지는 제외)
                    size = img_element.size
                    if size['width'] < 50 or size['height'] < 50:
                        self.logger.debug(f"이미지 {i}: 크기가 너무 작음 ({size['width']}x{size['height']})")
                        continue
                    
                    # 이미지 정보 로깅
                    src = img_element.get_attribute('src') or 'N/A'
                    alt = img_element.get_attribute('alt') or 'N/A'
                    self.logger.debug(f"이미지 {i} 분석 중: src={src[:50]}..., alt={alt}, 크기={size['width']}x{size['height']}")
                    
                    # 중문글자 감지 시도
                    has_chinese = self._check_image_for_chinese_text_in_bulk(img_element, i)
                    
                    if has_chinese:
                        chinese_image_positions.append(i)
                        self.logger.info(f"이미지 {i}: 중문글자 감지됨")
                    else:
                        self.logger.debug(f"이미지 {i}: 중문글자 없음")
                        
                except Exception as e:
                    self.logger.warning(f"이미지 {i} 처리 중 오류: {e}")
                    continue
            
            self.logger.info(f"중문글자 감지 완료 - 총 {len(chinese_image_positions)}개 이미지에서 중문글자 발견: {chinese_image_positions}")
            return chinese_image_positions
            
        except Exception as e:
            self.logger.error(f"중문글자 이미지 감지 오류: {e}")
            return []
            
    def _check_image_for_chinese_text_in_bulk(self, img_element, position):
        """
        일괄편집 모달에서 개별 이미지의 중문글자 존재 여부 확인
        
        Args:
            img_element: 이미지 웹 요소
            position (int): 이미지 위치 번호
            
        Returns:
            bool: 중문글자 존재 여부
        """
        try:
            self.logger.debug(f"이미지 {position}: 중문글자 검사 시작")
            
            # 중문글자 정규식 패턴
            chinese_pattern = r'[\u4e00-\u9fff]+'
            
            # 방법 1: 이미지 속성에서 중문글자 확인
            try:
                src = img_element.get_attribute('src') or ''
                alt = img_element.get_attribute('alt') or ''
                title = img_element.get_attribute('title') or ''
                
                # alt나 title 속성에서 중문글자 확인
                if re.search(chinese_pattern, alt) or re.search(chinese_pattern, title):
                    self.logger.info(f"이미지 {position}: 속성에서 중문글자 발견 (alt: {alt}, title: {title})")
                    return True
                    
                # 이미지 파일명에서 중문글자 확인
                if re.search(chinese_pattern, src):
                    self.logger.info(f"이미지 {position}: 파일명에서 중문글자 발견")
                    return True
            except Exception as e:
                self.logger.debug(f"이미지 {position} 속성 확인 중 오류: {e}")
            
            # 방법 2: 이미지 주변 텍스트에서 중문글자 확인
            try:
                # 이미지의 부모 요소에서 텍스트 확인
                parent = img_element.find_element(By.XPATH, "..")
                parent_text = parent.text or ''
                if re.search(chinese_pattern, parent_text):
                    self.logger.info(f"이미지 {position}: 부모 요소에서 중문글자 발견")
                    return True
                
                # 이미지의 data 속성들 확인
                for attr in ['data-original', 'data-src', 'data-lazy-src']:
                    data_value = img_element.get_attribute(attr) or ''
                    if re.search(chinese_pattern, data_value):
                        self.logger.info(f"이미지 {position}: {attr} 속성에서 중문글자 발견")
                        return True
            except Exception as e:
                self.logger.debug(f"이미지 {position} 주변 텍스트 확인 중 오류: {e}")
            
            # 방법 3: OCR을 사용한 이미지 텍스트 분석 (더 정확하지만 느림)
            if OCR_AVAILABLE:
                try:
                    self.logger.debug(f"이미지 {position}: OCR 검사 시작")
                    ocr_result = self._ocr_check_chinese_text_in_bulk(img_element, position)
                    self.logger.debug(f"이미지 {position}: OCR 검사 결과 - {ocr_result}")
                    return ocr_result
                except Exception as e:
                    self.logger.warning(f"이미지 {position} OCR 검사 중 오류: {e}")
            else:
                # OCR이 없는 경우 경고 메시지를 한 번만 출력
                if not hasattr(self, '_ocr_warning_shown'):
                    self.logger.warning("OCR이 설치되지 않아 이미지 내 텍스트 분석이 제한됩니다. 속성 기반 감지만 사용합니다.")
                    self._ocr_warning_shown = True
            
            self.logger.debug(f"이미지 {position}: 모든 검사 완료, 중문글자 없음")
            return False
            
        except Exception as e:
            self.logger.warning(f"이미지 {position} 중문글자 확인 중 오류: {e}")
            return False
            
    def _ocr_check_chinese_text_in_bulk(self, img_element, position):
        """
        일괄편집 모달에서 OCR을 사용하여 이미지 내 중문글자 확인
        
        Args:
            img_element: 이미지 웹 요소
            position (int): 이미지 위치 번호
            
        Returns:
            bool: 중문글자 존재 여부
        """
        try:
            import requests
            from PIL import Image
            import io
            
            # 이미지 URL 가져오기
            src = img_element.get_attribute('src')
            if not src:
                self.logger.debug(f"이미지 {position}: src 속성이 없음")
                return False
            
            # 이미지 다운로드 시도
            try:
                response = requests.get(src, timeout=10)
                response.raise_for_status()
                image = Image.open(io.BytesIO(response.content))
                self.logger.debug(f"이미지 {position}: 다운로드 성공")
            except Exception as e:
                self.logger.debug(f"이미지 {position}: 다운로드 실패 - {e}")
                return False
            
            # 이미지 크기 확인 및 조정
            width, height = image.size
            if width < 100 or height < 100:
                self.logger.debug(f"이미지 {position}: 크기가 너무 작음 ({width}x{height})")
                return False
            
            # 이미지가 너무 크면 리사이즈
            if width > 1000 or height > 1000:
                ratio = min(1000/width, 1000/height)
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                self.logger.debug(f"이미지 {position}: 리사이즈 {width}x{height} -> {new_width}x{new_height}")
            
            # 그레이스케일 변환
            if image.mode != 'L':
                image = image.convert('L')
            
            # NumPy 배열로 변환
            import numpy as np
            image_array = np.array(image)
            
            # EasyOCR로 텍스트 추출
            results = easyocr_reader.readtext(image_array, detail=0)
            
            if results:
                # 모든 텍스트를 하나로 합치기
                full_text = ' '.join(results)
                self.logger.debug(f"이미지 {position}: OCR 결과 - {full_text}")
                
                # 중문글자 패턴 확인
                chinese_pattern = r'[\u4e00-\u9fff]+'
                if re.search(chinese_pattern, full_text):
                    self.logger.info(f"이미지 {position}: OCR에서 중문글자 발견 - {full_text}")
                    return True
            
            self.logger.debug(f"이미지 {position}: OCR에서 중문글자 없음")
            return False
            
        except Exception as e:
            self.logger.warning(f"이미지 {position} OCR 검사 중 오류: {e}")
            return False
            
    def _process_specific_positions(self, positions):
        """개별 위치 처리 (기존 방식)"""
        try:
            success_count = 0
            total_count = len(positions)
            
            for position in positions:
                try:
                    self.logger.info(f"이미지 위치 {position} 번역 시작")
                    
                    # 편집 버튼 클릭
                    if not self._click_edit_button_by_position(position):
                        self.logger.error(f"이미지 위치 {position} 편집 버튼 클릭 실패")
                        continue
                    
                    # 이미지 번역 모달 대기
                    if not self._wait_for_image_translation_modal():
                        self.logger.error(f"이미지 위치 {position} 번역 모달 대기 실패")
                        continue
                    
                    # 현재 이미지 처리
                    if self._process_current_image():
                        success_count += 1
                        self.logger.info(f"이미지 위치 {position} 번역 성공")
                    
                    # 번역 모달 닫기
                    self._close_image_translation_modal()
                    time.sleep(1)
                    
                except Exception as e:
                    self.logger.error(f"이미지 위치 {position} 번역 오류: {e}")
                    continue
            
            # 변경사항 저장 (한 번만)
            if success_count > 0:
                self._save_changes()
            
            self.logger.info(f"개별 위치 처리 완료 - 성공: {success_count}/{total_count}")
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"개별 위치 처리 오류: {e}")
            return False
            
    def _process_all_images_sequentially(self):
        """모든 이미지 순차 처리 (새로운 방식)"""
        try:
            # 총 이미지 개수 확인
            total_images = self._get_total_image_count()
            if total_images == 0:
                self.logger.warning("이미지가 없습니다")
                return False
                
            self.logger.info(f"총 {total_images}개의 이미지 순차 처리 시작")
            
            # 첫 번째 편집 버튼 클릭
            if not self._click_first_edit_button():
                return False
                
            # 이미지 번역 모달 대기
            if not self._wait_for_image_translation_modal():
                return False
                
            # 모든 이미지 순차 처리
            processed_count = 0
            for i in range(total_images):
                self.logger.info(f"이미지 {i+1}/{total_images} 처리 중...")
                
                if self._process_current_image():
                    processed_count += 1
                    
                # 마지막 이미지가 아니면 TAB으로 다음 이미지로 이동
                if i < total_images - 1:
                    if not self._move_to_next_image():
                        self.logger.warning(f"이미지 {i+2}로 이동 실패")
                        break
                        
            # 변경사항 저장 (한 번만)
            if processed_count > 0:
                self._save_changes()
            
            # 모달 닫기
            self._close_image_translation_modal()
            
            self.logger.info(f"순차 처리 완료: {processed_count}/{total_images}개 처리됨")
            return processed_count > 0
            
        except Exception as e:
            self.logger.error(f"순차 처리 오류: {e}")
            return False
            
    def _click_edit_button_by_position(self, position):
        """위치별 편집 버튼 클릭 (기존 방식 호환)"""
        try:
            self.logger.info(f"이미지 위치 {position} 편집 버튼 클릭 시도")
            
            # 편집 버튼 선택자들 (다양한 형태 지원)
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
                            self.logger.info(f"이미지 위치 {position} 편집 버튼 클릭 성공 (일반 클릭)")
                        except Exception:
                            # JavaScript 클릭 시도
                            self.driver.execute_script("arguments[0].click();", edit_btn)
                            self.logger.info(f"이미지 위치 {position} 편집 버튼 클릭 성공 (JavaScript 클릭)")
                        
                        time.sleep(1.0)  # 모달 로딩 대기
                        return True
                except Exception as e:
                    self.logger.debug(f"편집 버튼 선택자 {selector} 실패: {e}")
                    continue
            
            self.logger.error(f"이미지 위치 {position} 편집 버튼을 찾을 수 없음")
            return False
            
        except Exception as e:
            self.logger.error(f"이미지 위치 {position} 편집 버튼 클릭 오류: {e}")
            return False
            
    def _open_bulk_edit_modal(self):
        """벌크 편집 모달 열기"""
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
                time.sleep(2)
                
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
            
    def _get_total_image_count(self):
        """총 이미지 개수 확인 - 모달창 내 cbu01.alicdn.com 이미지만 카운트"""
        try:
            # 먼저 모달창 요소를 찾음
            modal_selectors = [
                "//div[contains(@class, 'ant-drawer-content')]",
                "//div[contains(@class, 'ant-modal-content')]",
                "//div[contains(@class, 'ant-drawer')]",
                "//div[contains(@class, 'ant-modal')]"
            ]
            
            modal_element = None
            for modal_selector in modal_selectors:
                try:
                    modal_element = self.driver.find_element(By.XPATH, modal_selector)
                    if modal_element:
                        self.logger.info(f"모달창 요소 발견: {modal_selector}")
                        break
                except Exception:
                    continue
            
            if not modal_element:
                self.logger.warning("모달창을 찾을 수 없습니다")
                return 0
                
            # 모달창 내에서만 이미지 검색
            # 사용자 제공 DOM 구조: img class="sc-kpkpHi hJsbdH p_tooltip_image_editor_thumb" src="https://cbu01.alicdn.com/img/..."
            selectors = [
                ".//img[contains(@class, 'p_tooltip_image_editor_thumb') and contains(@src, 'https://cbu01.alicdn.com/img')]",
                ".//img[contains(@src, 'https://cbu01.alicdn.com/img')]"
            ]
            
            for selector in selectors:
                try:
                    # 모달창 내에서만 이미지 검색
                    images = modal_element.find_elements(By.XPATH, selector)
                    if images:
                        # cbu01.alicdn.com으로 시작하는 이미지만 필터링
                        valid_images = []
                        for img in images:
                            src = img.get_attribute('src')
                            if src and 'https://cbu01.alicdn.com/img' in src:
                                valid_images.append(img)
                        
                        if valid_images:
                            self.logger.info(f"모달창 내 유효한 이미지 {len(valid_images)}개 발견 (선택자: {selector})")
                            return len(valid_images)
                except Exception as e:
                    self.logger.debug(f"모달창 내 이미지 선택자 {selector} 실패: {e}")
                    continue
                    
            self.logger.warning("모달창 내 유효한 이미지를 찾을 수 없습니다")
            return 0
            
        except Exception as e:
            self.logger.error(f"이미지 개수 확인 실패: {e}")
            return 0
            
    def _click_first_edit_button(self):
        """첫 번째 편집 버튼 클릭 - 원본 파일의 정확한 선택자 사용"""
        try:
            # 편집 버튼 선택자들 (다양한 형태 지원)
            edit_button_selectors = [
                "(//button[contains(@class, 'ant-btn') and .//span[contains(text(), '편집')]])[1]",
                "(//button[.//span[contains(text(), '편집')]])[1]",
                "(//span[contains(text(), '편집')]/parent::button)[1]",
                "(//button[contains(text(), '편집')])[1]",
                "(//div[contains(@class, 'image-item')]//button[contains(@class, 'edit')])[1]",
                "(//div[contains(@class, 'image-container')]//button)[1]"
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
                            self.logger.info("첫 번째 편집 버튼 클릭 성공 (일반 클릭)")
                        except Exception:
                            # JavaScript 클릭 시도
                            self.driver.execute_script("arguments[0].click();", edit_btn)
                            self.logger.info("첫 번째 편집 버튼 클릭 성공 (JavaScript 클릭)")
                        
                        time.sleep(1.0)  # 모달 로딩 대기
                        return True
                except Exception as e:
                    self.logger.debug(f"편집 버튼 선택자 {selector} 실패: {e}")
                    continue
            
            self.logger.error("첫 번째 편집 버튼을 찾을 수 없습니다")
            return False
            
        except Exception as e:
            self.logger.error(f"첫 번째 편집 버튼 클릭 실패: {e}")
            return False
            
    def _wait_for_image_translation_modal(self):
        """이미지 번역 모달 대기"""
        try:
            selectors = [
                "#pCanvas",
                "canvas[id='pCanvas']",
                ".image-translation-modal",
                "[class*='translation'][class*='modal']"
            ]
            
            for selector in selectors:
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    time.sleep(2)
                    return True
                except:
                    continue
                    
            self.logger.error("이미지 번역 모달을 찾을 수 없습니다")
            return False
            
        except Exception as e:
            self.logger.error(f"이미지 번역 모달 대기 실패: {e}")
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
                return True
                
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
            return self._wait_for_translation_complete()
            
        except Exception as e:
            self.logger.error(f"번역 실행 실패: {e}")
            return False
            
    def _wait_for_translation_complete(self):
        """번역 완료 대기 - '원클릭 이미지 번역' 버튼 상태 변화 감지"""
        try:
            max_wait_time = 20  # 최대 20초 대기 (최적화)
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
                                time.sleep(1)  # 안정성을 위한 추가 대기 (단축)
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
                                time.sleep(1)  # 안정성을 위한 추가 대기 (단축)
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
            time.sleep(2)
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
                    time.sleep(2)
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
            time.sleep(2)
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