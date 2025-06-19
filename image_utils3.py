# -*- coding: utf-8 -*-
import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# 로깅 설정
logger = logging.getLogger(__name__)

# 지연 시간 상수
DELAY_SHORT = 0.5
DELAY_MEDIUM = 1.0
DELAY_LONG = 2.0

# 탭 선택자 상수
TAB_SELECTORS = {
    "상세페이지": "//div[contains(@class, 'ant-tabs-tab')][.//div[text()='상세페이지']]",
    "썸네일": "//div[contains(@class, 'ant-tabs-tab')][.//div[text()='썸네일']]",
    "상품명": "//div[contains(@class, 'ant-tabs-tab')][.//div[text()='상품명']]",
    "상품메모": "//div[contains(@class, 'ant-tabs-tab')][.//div[text()='상품메모']]"
}

class PercentyImageManager3:
    """
    퍼센티 상세페이지 이미지 관리 클래스 (3단계 버전)
    
    주요 기능:
    - image_delete: 이미지 삭제 (first, last, specific)
    - thumbnail_delete: 썸네일 삭제
    - option_image_copy: 옵션 이미지 복사
    - image_translate: 이미지 번역
    - image_tag_insert: 이미지 태그 삽입
    - html_update: HTML 업데이트
    """
    
    def __init__(self, driver):
        self.driver = driver
        logger.info("PercentyImageManager3 초기화 완료")
    
    def copy_option_images(self, count=1):
        """
        옵션 이미지 복사 - '썸네일로 복사' 버튼 클릭
        
        Args:
            count: 복사할 이미지 개수
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"옵션 이미지 {count}개 복사 시작")
            
            # 페이지 로딩 대기
            time.sleep(DELAY_MEDIUM)
            
            # '썸네일로 복사' 버튼 찾기 (제공된 HTML 구조 기반)
            copy_button_selectors = [
                "//div[contains(@class, 'sc-fYEEdK') and .//span[contains(@class, 'FootnoteDescription') and text()='썸네일로 복사']]",
                "//span[contains(@class, 'FootnoteDescription') and text()='썸네일로 복사']",
                "//div[contains(@class, 'sc-cNStcR')]//span[text()='썸네일로 복사']",
                "//span[text()='썸네일로 복사']"
            ]
            
            # 사용 가능한 '썸네일로 복사' 버튼 찾기
            copy_buttons = []
            for selector in copy_button_selectors:
                try:
                    buttons = self.driver.find_elements(By.XPATH, selector)
                    if buttons:
                        # 실제로 표시되는 버튼만 필터링
                        visible_buttons = [btn for btn in buttons if btn.is_displayed()]
                        if visible_buttons:
                            copy_buttons = visible_buttons
                            logger.info(f"'썸네일로 복사' 버튼 발견: {selector} ({len(visible_buttons)}개)")
                            break
                except Exception as e:
                    logger.debug(f"선택자 {selector} 실패: {e}")
                    continue
            
            if not copy_buttons:
                logger.warning("'썸네일로 복사' 버튼을 찾을 수 없습니다")
                return False
            
            # 요청한 개수만큼 복사 (중복 허용)
            actual_copy_count = count
            logger.info(f"실제 복사할 이미지 개수: {actual_copy_count} (요청: {count}, 사용가능: {len(copy_buttons)})")
            
            if len(copy_buttons) == 0:
                logger.warning("복사할 수 있는 버튼이 없습니다")
                return False
            
            copied_count = 0
            for i in range(actual_copy_count):
                try:
                    # 사용 가능한 버튼 중에서 순환하여 선택 (중복 허용)
                    button_index = i % len(copy_buttons)
                    copy_button = copy_buttons[button_index]
                    
                    # 버튼 클릭
                    try:
                        copy_button.click()
                        logger.info(f"{i + 1}번째 이미지 '썸네일로 복사' 버튼 클릭 성공 (버튼 인덱스: {button_index + 1})")
                    except ElementClickInterceptedException:
                        # JavaScript로 클릭 시도
                        self.driver.execute_script("arguments[0].click();", copy_button)
                        logger.info(f"{i + 1}번째 이미지 'JavaScript로 썸네일로 복사' 버튼 클릭 성공 (버튼 인덱스: {button_index + 1})")
                    
                    copied_count += 1
                    
                    # 복사 간 잠시 대기
                    time.sleep(DELAY_SHORT)
                    
                except Exception as e:
                    logger.warning(f"{i + 1}번째 이미지 '썸네일로 복사' 실패: {e}")
                    continue
            
            logger.info(f"옵션 이미지 복사 작업 완료: {copied_count}/{actual_copy_count}개 복사")
            return copied_count > 0
            
        except Exception as e:
            logger.error(f"옵션 이미지 복사 중 오류: {e}")
            return False
    
    def open_bulk_edit_modal(self, timeout=10):
        """
        상세페이지 일괄편집 모달창 열기 - UI 요소 기반 하이브리드 클릭 사용
        
        Args:
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            from click_utils import hybrid_click
            
            logger.info("상세페이지 일괄편집 모달창 열기 시작 - UI 요소 기반")
            
            # 페이지가 완전히 로드될 때까지 대기
            time.sleep(DELAY_MEDIUM)
            
            # UI 요소 기반 하이브리드 클릭으로 일괄편집 버튼 클릭
            click_success = hybrid_click(self.driver, "PRODUCT_DETAIL_OPENEDIT", delay=DELAY_LONG)
            
            if not click_success:
                logger.error("일괄편집 버튼 클릭 실패")
                return False
                
            logger.info("일괄편집 버튼 클릭 성공")
            
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
                logger.error("상세페이지 이미지 모달창을 열지 못했습니다.")
                return False
                
        except Exception as e:
            logger.error(f"상세페이지 일괄편집 모달창 열기 오류: {e}")
            return False
    
    def get_total_image_count(self, timeout=10):
        """
        총 이미지 개수 파악
        
        Args:
            timeout: 최대 대기 시간(초)
            
        Returns:
            int: 총 이미지 개수 (실패 시 0)
        """
        try:
            import time
            import re
            
            # 모달창이 완전히 로드될 때까지 잠시 대기
            time.sleep(DELAY_MEDIUM)
            
            # 총 이미지 개수 텍스트 찾기 (사용자가 제공한 정확한 선택자 사용)
            count_selectors = [
                "//span[contains(@class, 'sc-dLmyTH') and contains(@class, 'jOUQKU') and contains(@class, 'Body2Medium14') and contains(@class, 'CharacterTitle85') and contains(text(), '총') and contains(text(), '개의 이미지')]",
                "//span[contains(@class, 'sc-dLmyTH') and contains(@class, 'jOUQKU') and contains(text(), '총') and contains(text(), '개의 이미지')]",
                "//span[contains(text(), '총') and contains(text(), '개의 이미지')]",
                "//div[contains(text(), '총') and contains(text(), '개의 이미지')]"
            ]
            
            count_element = None
            for i, selector in enumerate(count_selectors):
                try:
                    logger.info(f"이미지 개수 텍스트 찾기 시도 {i+1}: {selector}")
                    count_element = WebDriverWait(self.driver, timeout).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    logger.info(f"이미지 개수 텍스트 요소 발견: {selector}")
                    break
                except (TimeoutException, NoSuchElementException) as e:
                    logger.warning(f"선택자 {i+1} 실패: {e}")
                    continue
                    
            if count_element:
                count_text = count_element.text.strip()
                logger.info(f"이미지 개수 텍스트: '{count_text}'")
                
                # 숫자 추출 (예: "총 13개의 이미지" -> 13)
                numbers = re.findall(r'\d+', count_text)
                if numbers:
                    total_count = int(numbers[0])
                    logger.info(f"총 이미지 개수 파악 성공: {total_count}개")
                    return total_count
                else:
                    logger.warning(f"이미지 개수 텍스트에서 숫자를 찾을 수 없습니다: '{count_text}'")
            else:
                logger.warning("총 이미지 개수 텍스트를 찾을 수 없습니다.")
                
            # 대체 방법: 모달창 내부의 실제 이미지 요소 개수 세기 (percenty.co.kr 도메인 제외)
            image_selectors = [
                # 모달창 내부의 실제 이미지만 선택 (sc-hCrRFl dVjKzV 클래스 조합으로 이미지 추가 버튼 제외)
                "//div[contains(@class, 'ant-modal-content')]//div[contains(@class, 'sc-hCrRFl') and contains(@class, 'dVjKzV')]//img[contains(@class, 'sc-kyDlHK')]",
                # 모달창 내부의 bLXrEr 클래스가 있는 실제 이미지만
                "//div[contains(@class, 'ant-modal-content')]//img[contains(@class, 'sc-kyDlHK') and contains(@class, 'bLXrEr')]",
                # 모달창 내부의 alicdn.com 도메인 이미지만 (percenty.co.kr 제외)
                "//div[contains(@class, 'ant-modal-content')]//img[contains(@src, 'alicdn.com')]",
                # 마지막 대안: 모달창 내부의 draggable="false" 속성이 있는 실제 이미지
                "//div[contains(@class, 'ant-modal-content')]//img[@draggable='false' and contains(@class, 'sc-kyDlHK')]"
            ]
            
            for i, selector in enumerate(image_selectors):
                try:
                    logger.info(f"이미지 요소 개수 세기 시도 {i+1}: {selector}")
                    image_elements = self.driver.find_elements(By.XPATH, selector)
                    if image_elements:
                        # percenty.co.kr 도메인 이미지 제외하여 카운트
                        filtered_count = 0
                        for img in image_elements:
                            src = img.get_attribute('src')
                            if src and 'percenty.co.kr' not in src:
                                filtered_count += 1
                            elif src and 'percenty.co.kr' in src:
                                logger.debug(f"percenty.co.kr 도메인 이미지 제외: {src[:100]}...")
                        
                        if filtered_count > 0:
                            logger.info(f"실제 이미지 요소 개수 발견: {filtered_count}개 (선택자 {i+1}, percenty.co.kr 제외)")
                            return filtered_count
                        else:
                            logger.warning(f"선택자 {i+1}로 유효한 이미지를 찾을 수 없습니다 (percenty.co.kr 제외 후).")
                    else:
                        logger.warning(f"선택자 {i+1}로 이미지 요소를 찾을 수 없습니다.")
                except Exception as e:
                    logger.warning(f"이미지 요소 개수 세기 실패 (선택자 {i+1}): {e}")
                    continue
                    
            logger.error("총 이미지 개수를 파악할 수 없습니다.")
            return 0
            
        except Exception as e:
            logger.error(f"총 이미지 개수 파악 오류: {e}")
            return 0
    
    def delete_image_by_position(self, position, total_count, timeout=10):
        """
        특정 위치의 이미지 삭제
        
        Args:
            position: 삭제할 이미지 위치 (1부터 시작)
            total_count: 총 이미지 개수
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            import time
            logger.info(f"위치 {position}의 이미지 삭제 시작 (총 {total_count}개 중)")
            
            # 이미지 컨테이너 찾기 (사용자가 제공한 DOM 구조 기반)
            container_selectors = [
                f"(//div[contains(@class, 'ant-col') and contains(@class, 'css-1li46mu')]//div[contains(@class, 'sc-hCrRFl') and contains(@class, 'dVjKzV')])[{position}]",
                f"(//div[contains(@class, 'sc-hCrRFl') and contains(@class, 'dVjKzV')])[{position}]",
                f"(//div[contains(@class, 'ant-col') and contains(@class, 'css-1li46mu')])[{position}]"
            ]
            
            image_container = None
            for i, selector in enumerate(container_selectors):
                try:
                    logger.info(f"이미지 컨테이너 찾기 시도 {i+1}: {selector}")
                    image_container = WebDriverWait(self.driver, timeout).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    logger.info(f"위치 {position}의 이미지 컨테이너 발견 (선택자 {i+1})")
                    break
                except (TimeoutException, NoSuchElementException) as e:
                    logger.warning(f"컨테이너 선택자 {i+1} 실패: {e}")
                    continue
                    
            if not image_container:
                logger.error(f"위치 {position}의 이미지 컨테이너를 찾을 수 없습니다.")
                return False
                
            # 삭제 버튼 찾기 (사용자가 제공한 DOM 구조 기반)
            delete_selectors = [
                ".//div[contains(@class, 'sc-bOTbmH') and contains(@class, 'iNrMOB')]//span[contains(text(), '삭제')]",
                ".//div[contains(@class, 'sc-bOTbmH')]//span[contains(text(), '삭제')]",
                ".//span[contains(text(), '삭제')]",
                ".//div[contains(@class, 'sc-bOTbmH') and contains(@class, 'iNrMOB')]"
            ]
            
            delete_button = None
            for i, selector in enumerate(delete_selectors):
                try:
                    logger.info(f"삭제 버튼 찾기 시도 {i+1}: {selector}")
                    delete_button = image_container.find_element(By.XPATH, selector)
                    if delete_button.is_displayed():
                        logger.info(f"위치 {position}의 삭제 버튼 발견 (선택자 {i+1})")
                        break
                    else:
                        logger.warning(f"삭제 버튼이 보이지 않음 (선택자 {i+1})")
                        delete_button = None
                except (NoSuchElementException) as e:
                    logger.warning(f"삭제 버튼 선택자 {i+1} 실패: {e}")
                    continue
                    
            if not delete_button:
                logger.error(f"위치 {position}의 삭제 버튼을 찾을 수 없습니다.")
                return False
                
            # 삭제 버튼 클릭
            try:
                # 스크롤하여 요소가 보이도록 함
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", delete_button)
                time.sleep(DELAY_SHORT)
                
                # 클릭 시도
                delete_button.click()
                logger.info(f"위치 {position}의 이미지 삭제 버튼 클릭 성공")
                
            except ElementClickInterceptedException:
                # JavaScript 클릭 시도
                logger.warning(f"일반 클릭 실패, JavaScript 클릭 시도")
                self.driver.execute_script("arguments[0].click();", delete_button)
                logger.info(f"위치 {position}의 이미지 JavaScript 클릭 성공")
                
            # 삭제 후 대기
            time.sleep(DELAY_MEDIUM)
            
            # 삭제 확인 (이미지 개수 변화 확인)
            logger.info(f"이미지 삭제 후 개수 확인 중...")
            new_count = self.get_total_image_count()
            
            if new_count == total_count - 1:
                logger.info(f"위치 {position}의 이미지 삭제 성공 (이전: {total_count}개 -> 현재: {new_count}개)")
                return True
            elif new_count < total_count:
                logger.info(f"이미지 삭제 성공 (예상과 다른 개수 변화: 이전 {total_count}개 -> 현재 {new_count}개)")
                return True
            else:
                logger.warning(f"이미지 삭제 후 개수 변화 없음 (이전: {total_count}개 -> 현재: {new_count}개)")
                return False
                
        except Exception as e:
            logger.error(f"위치 {position}의 이미지 삭제 오류: {e}")
            return False
    
    def delete_last_images(self, count, timeout=10):
        """
        마지막 N개 이미지 삭제
        
        Args:
            count: 삭제할 이미지 개수
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"마지막 {count}개 이미지 삭제 시작")
            
            # 총 이미지 개수 파악
            total_count = self.get_total_image_count()
            if total_count == 0:
                logger.error("총 이미지 개수를 파악할 수 없습니다.")
                return False
                
            if count > total_count:
                logger.warning(f"삭제할 이미지 개수({count})가 총 이미지 개수({total_count})보다 큽니다. 모든 이미지를 삭제합니다.")
                count = total_count
                
            success_count = 0
            
            # 마지막부터 역순으로 삭제
            for i in range(count):
                position = total_count - i  # 마지막부터 삭제
                current_total = total_count - success_count  # 현재 남은 이미지 개수
                
                if self.delete_image_by_position(position, current_total, timeout):
                    success_count += 1
                    logger.info(f"마지막 이미지 삭제 진행: {success_count}/{count}개 완료")
                else:
                    logger.warning(f"위치 {position}의 이미지 삭제 실패")
                    
                # 삭제 후 잠시 대기
                time.sleep(DELAY_SHORT)
                
            if success_count == count:
                logger.info(f"마지막 {count}개 이미지 삭제 완료")
                return True
            else:
                logger.warning(f"마지막 이미지 삭제 부분 성공: {success_count}/{count}개")
                return False
                
        except Exception as e:
            logger.error(f"마지막 이미지 삭제 오류: {e}")
            return False
    
    def delete_first_images(self, count, timeout=10):
        """
        처음 N개 이미지 삭제
        
        Args:
            count: 삭제할 이미지 개수
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"처음 {count}개 이미지 삭제 시작")
            
            # 총 이미지 개수 파악
            total_count = self.get_total_image_count()
            if total_count == 0:
                logger.error("총 이미지 개수를 파악할 수 없습니다.")
                return False
                
            if count > total_count:
                logger.warning(f"삭제할 이미지 개수({count})가 총 이미지 개수({total_count})보다 큽니다. 모든 이미지를 삭제합니다.")
                count = total_count
                
            success_count = 0
            
            # 첫 번째부터 순서대로 삭제 (항상 첫 번째 위치 삭제)
            for i in range(count):
                position = 1  # 항상 첫 번째 이미지 삭제 (삭제되면 다음 이미지가 첫 번째가 됨)
                current_total = total_count - success_count  # 현재 남은 이미지 개수
                
                if self.delete_image_by_position(position, current_total, timeout):
                    success_count += 1
                    logger.info(f"첫 번째 이미지 삭제 진행: {success_count}/{count}개 완료")
                else:
                    logger.warning(f"첫 번째 이미지 삭제 실패")
                    
                # 삭제 후 잠시 대기
                time.sleep(DELAY_SHORT)
                
            if success_count == count:
                logger.info(f"처음 {count}개 이미지 삭제 완료")
                return True
            else:
                logger.warning(f"첫 번째 이미지 삭제 부분 성공: {success_count}/{count}개")
                return False
                
        except Exception as e:
            logger.error(f"첫 번째 이미지 삭제 오류: {e}")
            return False
    
    def delete_specific_images(self, positions, timeout=10):
        """
        특정 위치의 이미지들 삭제
        
        Args:
            positions: 삭제할 이미지 위치 리스트 (1부터 시작)
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"특정 위치 이미지 삭제 시작: {positions}")
            
            # 총 이미지 개수 파악
            total_count = self.get_total_image_count()
            if total_count == 0:
                logger.error("총 이미지 개수를 파악할 수 없습니다.")
                return False
                
            # 위치 정렬 (큰 번호부터 삭제하여 인덱스 변화 방지)
            sorted_positions = sorted(positions, reverse=True)
            success_count = 0
            
            for position in sorted_positions:
                if position > total_count:
                    logger.warning(f"위치 {position}은 총 이미지 개수({total_count})를 초과합니다.")
                    continue
                    
                current_total = total_count - success_count  # 현재 남은 이미지 개수
                
                if self.delete_image_by_position(position, current_total, timeout):
                    success_count += 1
                    logger.info(f"특정 위치 이미지 삭제 진행: {success_count}/{len(positions)}개 완료")
                else:
                    logger.warning(f"위치 {position}의 이미지 삭제 실패")
                    
                # 삭제 후 잠시 대기
                time.sleep(DELAY_SHORT)
                
            if success_count == len(positions):
                logger.info(f"특정 위치 {len(positions)}개 이미지 삭제 완료")
                return True
            else:
                logger.warning(f"특정 위치 이미지 삭제 부분 성공: {success_count}/{len(positions)}개")
                return False
                
        except Exception as e:
            logger.error(f"특정 위치 이미지 삭제 오류: {e}")
            return False
    
    def close_modal(self, timeout=10):
        """
        모달창 닫기
        
        Args:
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            import time
            logger.info("모달창 닫기 시작")
            
            # 먼저 모달창이 열려있는지 확인
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
                        logger.info(f"모달창 발견 (선택자 {i+1}): {selector}")
                        modal_found = True
                        break
                except (NoSuchElementException):
                    continue
                    
            if not modal_found:
                logger.info("모달창이 이미 닫혀있습니다.")
                return True
            
            # 방법 1: ESC 키로 닫기 시도
            logger.info("ESC 키로 모달창 닫기 시도")
            try:
                ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
                time.sleep(DELAY_LONG)  # 더 긴 대기 시간
                
                # 모달창이 닫혔는지 확인
                modal_closed = True
                for selector in modal_selectors:
                    try:
                        element = self.driver.find_element(By.XPATH, selector)
                        if element.is_displayed():
                            modal_closed = False
                            break
                    except (NoSuchElementException):
                        continue
                        
                if modal_closed:
                    logger.info("ESC 키로 모달창 닫기 성공")
                    return True
            except Exception as e:
                logger.warning(f"ESC 키 닫기 실패: {e}")
            
            # 방법 2: 닫기 버튼으로 닫기 시도
            logger.warning("ESC 키로 모달창 닫기 실패, 닫기 버튼 시도")
            close_selectors = [
                "//div[contains(@class, 'ant-drawer-close')]",
                "//button[contains(@class, 'ant-modal-close')]",
                "//span[contains(@class, 'anticon-close')]",
                "//button[contains(@aria-label, 'Close')]",
                "//div[contains(@class, 'ant-drawer-header')]//button"
            ]
            
            for i, selector in enumerate(close_selectors):
                try:
                    logger.info(f"닫기 버튼 찾기 시도 {i+1}: {selector}")
                    close_button = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    close_button.click()
                    time.sleep(DELAY_LONG)
                    
                    # 모달창이 닫혔는지 확인
                    modal_closed = True
                    for modal_selector in modal_selectors:
                        try:
                            element = self.driver.find_element(By.XPATH, modal_selector)
                            if element.is_displayed():
                                modal_closed = False
                                break
                        except (NoSuchElementException):
                            continue
                            
                    if modal_closed:
                        logger.info(f"닫기 버튼으로 모달창 닫기 성공 (선택자 {i+1})")
                        return True
                    else:
                        logger.warning(f"닫기 버튼 클릭했지만 모달창이 여전히 열려있음 (선택자 {i+1})")
                        
                except (TimeoutException, NoSuchElementException) as e:
                    logger.warning(f"닫기 버튼 선택자 {i+1} 실패: {e}")
                    continue
            
            # 방법 3: 백그라운드 클릭으로 닫기 시도
            logger.warning("닫기 버튼으로도 실패, 백그라운드 클릭 시도")
            try:
                # 모달창 외부 영역 클릭
                body = self.driver.find_element(By.TAG_NAME, "body")
                ActionChains(self.driver).move_to_element_with_offset(body, 10, 10).click().perform()
                time.sleep(DELAY_LONG)
                
                # 모달창이 닫혔는지 확인
                modal_closed = True
                for selector in modal_selectors:
                    try:
                        element = self.driver.find_element(By.XPATH, selector)
                        if element.is_displayed():
                            modal_closed = False
                            break
                    except (NoSuchElementException):
                        continue
                        
                if modal_closed:
                    logger.info("백그라운드 클릭으로 모달창 닫기 성공")
                    return True
            except Exception as e:
                logger.warning(f"백그라운드 클릭 실패: {e}")
                
            logger.error("모든 방법으로 모달창 닫기 실패")
            return False
                
        except Exception as e:
            logger.error(f"모달창 닫기 오류: {e}")
            return False
    
    def thumbnail_delete(self, delete_command="first:1", timeout=10):
        """
        썸네일 삭제 기능
        
        Args:
            delete_command: 삭제 명령 (예: 'first:1', 'last:2', 'specific:3,4')
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            import time
            logger.info(f"썸네일 삭제 시작: {delete_command}")
            
            # 1. 썸네일 탭 선택
            if not self.select_tab("썸네일", timeout):
                logger.error("썸네일 탭 선택 실패")
                return False
                
            # 탭 전환 후 잠시 대기
            time.sleep(DELAY_MEDIUM)
            
            # 2. 총 썸네일 개수 확인
            total_count = self.get_total_thumbnail_count()
            if total_count == 0:
                logger.warning("삭제할 썸네일이 없습니다.")
                return True
                
            logger.info(f"총 {total_count}개의 썸네일 발견")
            
            # 3. 삭제 명령 파싱 및 실행
            if delete_command.startswith("first:"):
                count = int(delete_command.split(":")[1])
                return self.delete_first_thumbnails(count, total_count)
            elif delete_command.startswith("last:"):
                count = int(delete_command.split(":")[1])
                return self.delete_last_thumbnails(count, total_count)
            elif delete_command.startswith("specific:"):
                positions = [int(x.strip()) for x in delete_command.split(":")[1].split(",")]
                return self.delete_specific_thumbnails(positions, total_count)
            else:
                logger.error(f"지원하지 않는 삭제 명령: {delete_command}")
                return False
                
        except Exception as e:
            logger.error(f"썸네일 삭제 중 오류 발생: {e}")
            return False
    
    def select_tab(self, tab_name, timeout=10):
        """
        지정된 탭 선택
        
        Args:
            tab_name: 탭 이름 (예: '썸네일', '상세페이지')
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            if tab_name not in TAB_SELECTORS:
                logger.error(f"지원하지 않는 탭: {tab_name}")
                return False
                
            tab_selector = TAB_SELECTORS[tab_name]
            logger.info(f"{tab_name} 탭 선택 시도: {tab_selector}")
            
            tab_element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, tab_selector))
            )
            tab_element.click()
            
            # 탭 전환 확인
            time.sleep(DELAY_MEDIUM)
            
            logger.info(f"{tab_name} 탭 선택 성공")
            return True
            
        except Exception as e:
            logger.error(f"{tab_name} 탭 선택 실패: {e}")
            return False
    
    def get_total_thumbnail_count(self):
        """
        총 썸네일 개수 확인
        
        Returns:
            int: 썸네일 개수
        """
        try:
            logger.info("썸네일 개수 확인 시작")
            
            # 페이지 로딩 대기
            time.sleep(DELAY_MEDIUM)
            
            # '총 X개 썸네일' 텍스트에서 개수 추출
            count_selectors = [
                "//span[contains(text(), '총') and contains(text(), '개 썸네일')]",
                "//div[contains(text(), '총') and contains(text(), '개 썸네일')]",
                "//p[contains(text(), '총') and contains(text(), '개 썸네일')]",
                "//span[contains(text(), '썸네일') and contains(text(), '개')]",
                "//div[contains(text(), '썸네일') and contains(text(), '개')]"
            ]
            
            for i, selector in enumerate(count_selectors):
                try:
                    element = self.driver.find_element(By.XPATH, selector)
                    text = element.text
                    logger.info(f"썸네일 개수 텍스트 발견 (선택자 {i+1}): {text}")
                    
                    # 정규식으로 숫자 추출 (다양한 패턴 지원)
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
                            logger.info(f"총 썸네일 개수 (텍스트): {count}")
                            return count
                except (NoSuchElementException, ValueError) as e:
                    logger.debug(f"썸네일 개수 텍스트 선택자 {i+1} 실패: {e}")
                    continue
            
            # 텍스트로 개수를 찾을 수 없으면 실제 썸네일 요소 개수 확인
            thumbnail_selectors = [
                "//div[contains(@class, 'ant-upload-list-item') and not(contains(@class, 'ant-upload-list-item-uploading'))]",
                "//div[contains(@class, 'ant-upload-list-item-done')]",
                "//div[contains(@class, 'thumbnail-item')]",
                "//img[contains(@class, 'thumbnail')]",
                "//div[contains(@class, 'ant-upload-list')]//div[contains(@class, 'ant-upload-list-item')]",
                "//div[@class='ant-upload-list ant-upload-list-picture-card']//div[contains(@class, 'ant-upload-list-item')]"
            ]
            
            for i, selector in enumerate(thumbnail_selectors):
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements:
                        # 실제로 표시되는 요소만 카운트
                        visible_elements = [elem for elem in elements if elem.is_displayed()]
                        count = len(visible_elements)
                        logger.info(f"썸네일 요소 개수로 확인 (선택자 {i+1}): {count}개 (전체 {len(elements)}개 중 표시 {count}개)")
                        if count > 0:
                            return count
                except Exception as e:
                    logger.debug(f"썸네일 요소 선택자 {i+1} 실패: {e}")
                    continue
                    
            logger.warning("썸네일 개수를 확인할 수 없습니다.")
            return 0
            
        except Exception as e:
            logger.error(f"썸네일 개수 확인 중 오류: {e}")
            return 0
    
    def delete_thumbnail_by_position(self, position, timeout=5):
        """
        지정된 위치의 썸네일 삭제
        
        Args:
            position: 삭제할 썸네일 위치 (1부터 시작)
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"{position}번째 썸네일 삭제 시도")
            
            # 삭제 버튼 선택자들 (실제 HTML 구조에 맞게 수정)
            delete_selectors = [
                f"(//div[contains(@class, 'sc-leQnM') and .//span[contains(@class, 'FootnoteDescription') and text()='삭제']])[{position}]",
                f"(//div[contains(@class, 'sc-leQnM')]//span[contains(@class, 'FootnoteDescription') and text()='삭제'])[{position}]",
                f"(//span[contains(@class, 'FootnoteDescription') and text()='삭제'])[{position}]",
                f"(//span[text()='삭제'])[{position}]",
                f"(//button[contains(., '삭제')])[{position}]",
                f"(//div[contains(@class, 'ant-upload-list-item')][{position}]//span[text()='삭제'])"
            ]
            
            for i, selector in enumerate(delete_selectors):
                try:
                    logger.info(f"삭제 버튼 찾기 시도 {i+1}: {selector}")
                    delete_button = WebDriverWait(self.driver, timeout).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    
                    # 삭제 전 현재 썸네일 개수 확인
                    before_count = self.get_total_thumbnail_count()
                    
                    # 삭제 버튼 클릭
                    try:
                        delete_button.click()
                        logger.info(f"삭제 버튼 클릭 성공 (선택자 {i+1})")
                    except ElementClickInterceptedException:
                        # JavaScript로 클릭 시도
                        self.driver.execute_script("arguments[0].click();", delete_button)
                        logger.info(f"JavaScript로 삭제 버튼 클릭 성공 (선택자 {i+1})")
                    
                    # 삭제 완료 대기
                    time.sleep(DELAY_MEDIUM)
                    
                    # 삭제 확인
                    after_count = self.get_total_thumbnail_count()
                    if after_count < before_count:
                        logger.info(f"{position}번째 썸네일 삭제 성공 (개수: {before_count} -> {after_count})")
                        return True
                    else:
                        logger.warning(f"삭제 후에도 썸네일 개수가 변경되지 않음 (개수: {before_count})")
                        
                except (TimeoutException, NoSuchElementException) as e:
                    logger.warning(f"삭제 버튼 선택자 {i+1} 실패: {e}")
                    continue
            
            logger.error(f"{position}번째 썸네일 삭제 실패")
            return False
            
        except Exception as e:
            logger.error(f"{position}번째 썸네일 삭제 중 오류: {e}")
            return False
    
    def delete_first_thumbnails(self, count, total_count):
        """
        처음부터 지정된 개수의 썸네일 삭제
        
        Args:
            count: 삭제할 개수
            total_count: 총 썸네일 개수
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"처음 {count}개 썸네일 삭제 시작")
            
            if count > total_count:
                logger.warning(f"삭제할 개수({count})가 총 개수({total_count})보다 큽니다. 모든 썸네일을 삭제합니다.")
                count = total_count
            
            success_count = 0
            for i in range(count):
                # 항상 첫 번째 썸네일을 삭제 (삭제되면 다음 썸네일이 첫 번째가 됨)
                if self.delete_thumbnail_by_position(1):
                    success_count += 1
                    time.sleep(DELAY_SHORT)  # 삭제 간 잠시 대기
                else:
                    logger.error(f"{i+1}번째 썸네일 삭제 실패")
                    break
            
            logger.info(f"처음 썸네일 삭제 완료: {success_count}/{count}")
            return success_count == count
            
        except Exception as e:
            logger.error(f"처음 썸네일 삭제 중 오류: {e}")
            return False
    
    def delete_last_thumbnails(self, count, total_count):
        """
        마지막부터 지정된 개수의 썸네일 삭제
        
        Args:
            count: 삭제할 개수
            total_count: 총 썸네일 개수
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"마지막 {count}개 썸네일 삭제 시작")
            
            if count > total_count:
                logger.warning(f"삭제할 개수({count})가 총 개수({total_count})보다 큽니다. 모든 썸네일을 삭제합니다.")
                count = total_count
            
            success_count = 0
            # 마지막부터 삭제 (역순)
            for i in range(count):
                position = total_count - i  # 마지막 위치부터
                if self.delete_thumbnail_by_position(position):
                    success_count += 1
                    time.sleep(DELAY_SHORT)  # 삭제 간 잠시 대기
                else:
                    logger.error(f"{position}번째 썸네일 삭제 실패")
                    break
            
            logger.info(f"마지막 썸네일 삭제 완료: {success_count}/{count}")
            return success_count == count
            
        except Exception as e:
            logger.error(f"마지막 썸네일 삭제 중 오류: {e}")
            return False
    
    def delete_specific_thumbnails(self, positions, total_count):
        """
        특정 위치의 썸네일들 삭제
        
        Args:
            positions: 삭제할 위치 리스트 (1부터 시작)
            total_count: 총 썸네일 개수
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"특정 위치 썸네일 삭제 시작: {positions}")
            
            # 유효한 위치만 필터링
            valid_positions = [pos for pos in positions if 1 <= pos <= total_count]
            if len(valid_positions) != len(positions):
                invalid_positions = [pos for pos in positions if pos not in valid_positions]
                logger.warning(f"유효하지 않은 위치 제외: {invalid_positions}")
            
            if not valid_positions:
                logger.warning("삭제할 유효한 위치가 없습니다.")
                return True
            
            # 위치를 내림차순으로 정렬 (뒤에서부터 삭제)
            valid_positions.sort(reverse=True)
            logger.info(f"삭제 순서 (뒤에서부터): {valid_positions}")
            
            success_count = 0
            for position in valid_positions:
                if self.delete_thumbnail_by_position(position):
                    success_count += 1
                    time.sleep(DELAY_SHORT)  # 삭제 간 잠시 대기
                else:
                    logger.error(f"{position}번째 썸네일 삭제 실패")
                    # 실패해도 계속 진행
            
            logger.info(f"특정 위치 썸네일 삭제 완료: {success_count}/{len(valid_positions)}")
            return success_count == len(valid_positions)
            
        except Exception as e:
            logger.error(f"특정 위치 썸네일 삭제 중 오류: {e}")
            return False
    
    def delete_images_by_positions(self, positions, timeout=10):
        """
        특정 위치의 이미지들 삭제 (delete_specific_images의 별칭)
        
        Args:
            positions: 삭제할 이미지 위치 리스트 (1부터 시작)
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        return self.delete_specific_images(positions, timeout)
    
    def option_image_copy(self):
        """옵션 이미지 복사 기능 (추후 구현)"""
        logger.info("option_image_copy 메서드는 추후 구현 예정입니다.")
        return False
    
    def image_translate(self):
        """이미지 번역 기능 (추후 구현)"""
        logger.info("image_translate 메서드는 추후 구현 예정입니다.")
        return False
    
    def image_tag_insert(self):
        """이미지 태그 삽입 기능 (추후 구현)"""
        logger.info("image_tag_insert 메서드는 추후 구현 예정입니다.")
        return False
    
    def html_update(self):
        """HTML 업데이트 기능 (추후 구현)"""
        logger.info("html_update 메서드는 추후 구현 예정입니다.")
        return False