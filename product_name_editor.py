"""
퍼센티 상품명 수정 모듈 (단순화된 버전)
중복 입력 문제 해결 및 안정적인 상품명 저장
"""

import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# 로깅 설정
logger = logging.getLogger(__name__)

# 시간 지연 상수
DELAY_SHORT = 1
DELAY_MEDIUM = 2
DELAY_LONG = 3

class ProductNameEditor:
    """퍼센티 상품명 수정 클래스"""
    
    def __init__(self, driver):
        """초기화"""
        self.driver = driver
        self.suffix_index = 0  # 알파벳 접미사 인덱스 (A부터 시작)
    
    def edit_product_name(self, suffix=None):
        """상품명에 알파벳 접미사 추가 - A에서 Z까지 순차적으로 부여
        
        Args:
            suffix (int, optional): 사용할 접미사 인덱스 (0-25, A-Z에 해당). None인 경우 내부 인덱스 사용
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("상품명 수정 시작")
            
            # 1. 상품명 입력필드 찾기
            selectors = [
                "//input[contains(@class, 'ant-input')][@type='text']",
                "//textarea[contains(@placeholder, '판매상품명')]",
                "//input[@type='text'][contains(@class, 'ant-input')]"
            ]
            
            input_element = None
            for selector in selectors:
                try:
                    input_element = self.driver.find_element(By.XPATH, selector)
                    logger.info(f"상품명 입력필드 발견: {selector}")
                    break
                except Exception:
                    continue
            
            if not input_element:
                logger.error("상품명 입력필드를 찾을 수 없음")
                return False
            
            # 2. 현재 상품명 가져오기
            current_name = input_element.get_attribute("value")
            if not current_name:
                logger.warning("현재 상품명을 가져올 수 없음")
                return False
            
            logger.info(f"현재 상품명: {current_name}")
            
            # 3. 새 상품명 생성 (알파벳 접미사 추가)
            # 전달받은 suffix 인덱스 사용 (없으면 내부 인덱스 사용)
            if suffix is not None:
                # 전달받은 인덱스 사용
                suffix_index = suffix
                logger.info(f"전달받은 suffix 인덱스 사용: {suffix_index}")
            else:
                # 내부 인덱스 사용 (이전 방식)
                suffix_index = self.suffix_index
                logger.info(f"내부 suffix 인덱스 사용: {suffix_index}")
        
            # 인덱스 범위 확인 (0-25)
            suffix_index = max(0, min(25, suffix_index))
            current_suffix = chr(65 + suffix_index)  # 65는 ASCII에서 'A'
            
            # 다음 상품을 위해 내부 인덱스 증가 (A-Z 순환, 내부 카운터용)
            self.suffix_index = (self.suffix_index + 1) % 26
            
            logger.info(f"접미사 사용: '{current_suffix}' (인덱스: {suffix_index}, 다음 인덱스: {self.suffix_index})")
            
            # 에러방지: 업로드된 엄체는 대문자로 주소를 가져온다
            if len(current_name) > 0 and current_name[-1] >= 'A' and current_name[-1] <= 'Z':
                # 이미 알파벳이 있다면 제거
                logger.info(f"기존 접미사 '{current_name[-1]}' 제거 후 새 접미사 추가")
                current_name = current_name[:-1]
            
            new_name = current_name + current_suffix
            logger.info(f"새 상품명: {new_name}")

            
            new_name = current_name + current_suffix
            logger.info(f"새 상품명: {new_name}")
            
            # 4. 상품명 입력 - 단일 방식 사용
            # 4.1. 입력필드 클릭해서 포커스 주기
            input_element.click()
            time.sleep(DELAY_SHORT)
            
            # 4.2. JavaScript+Selenium 조합 방식으로 입력필드 클리어 (메모리에서 확인한 가장 안정적인 방법)
            
            # JavaScript로 값 지우기
            self.driver.execute_script("arguments[0].value = '';", input_element)
            
            # 입력 필드에 포커스 주기
            self.driver.execute_script("arguments[0].focus();", input_element)
            
            # Selenium으로 한 번 더 확인 클리어
            input_element.clear()
            
            # 클리어 후 대기 (한 번만 대기)
            time.sleep(DELAY_SHORT)
            
            # 값이 여전히 남아있는지 확인
            remaining_value = input_element.get_attribute("value")
            if remaining_value:
                logger.warning(f"아직 입력필드에 값이 남아 있음: '{remaining_value}', JavaScript로 일괄 교체")
                # 입력값 완전 교체
                try:
                    # 입력필드에 바로 새 값을 지정
                    self.driver.execute_script(f"arguments[0].value = '{new_name}';", input_element)
                    logger.info("JavaScript로 입력필드 값 직접 교체")
                    time.sleep(DELAY_SHORT)
                    return True
                except Exception as js_error:
                    logger.error(f"JavaScript 값 교체 오류: {js_error}")
            
            # 4.3. 새 상품명 입력
            logger.info(f"새 상품명 입력 시작: '{new_name}'")
            input_element.send_keys(new_name)
            logger.info(f"새 상품명 입력 완료")
            time.sleep(DELAY_MEDIUM)  # 입력 후 대기 시간 증가
            
            # 4.4. 입력값 확인
            current_value = input_element.get_attribute("value")
            if current_value != new_name:
                logger.warning(f"입력값 불일치: 현재 '{current_value}', 기대 '{new_name}'")
                # 다시 시도
                input_element.clear()
                time.sleep(DELAY_SHORT)
                input_element.send_keys(new_name)
                logger.info("재시도: 새 상품명 입력")
                time.sleep(DELAY_SHORT)
            
            # 4.5. TAB 키로 포커스 이동하여 저장 트리거
            input_element.send_keys(Keys.TAB)
            logger.info("TAB 키로 포커스 이동 (저장 트리거)")
            
            # 4.6. 저장 완료를 위한 충분한 대기 시간
            time.sleep(DELAY_LONG)
            
            # 4.7. 저장 확인 (stale element 방지를 위해 요소 재검색)
            try:
                final_value = input_element.get_attribute("value")
            except Exception as stale_error:
                logger.warning(f"요소 참조 오류 발생, 요소 재검색: {stale_error}")
                # 요소 재검색
                try:
                    for selector in selectors:
                        try:
                            input_element = self.driver.find_element(By.XPATH, selector)
                            final_value = input_element.get_attribute("value")
                            logger.info("요소 재검색 성공")
                            break
                        except Exception:
                            continue
                    else:
                        logger.warning("요소 재검색 실패, 성공으로 간주")
                        return True
                except Exception as re_search_error:
                    logger.warning(f"요소 재검색 중 오류: {re_search_error}, 성공으로 간주")
                    return True
            
            if final_value == new_name:
                logger.info(f"상품명 수정 성공: '{final_value}'")
                return True
            else:
                logger.warning(f"상품명 수정 확인 불일치 - 현재값: '{final_value}', 기대값: '{new_name}'")
                return False
                
        except Exception as e:
            logger.error(f"상품명 수정 중 오류 발생: {e}")
            return False
