import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

# 로깅 설정
logger = logging.getLogger(__name__)

# 지연 시간 상수
DELAY_SHORT = 1
DELAY_MEDIUM = 2
DELAY_LONG = 3

# 탭 선택자 상수
TAB_DETAIL = "//div[contains(@class, 'ant-tabs-tab')][./div[text()='상세페이지']]"  # 상세페이지 탭
TAB_THUMBNAIL = "//div[contains(@class, 'ant-tabs-tab')][./div[text()='섬네일']]"    # 섬네일 탭
TAB_OPTIONS = "//div[contains(@class, 'ant-tabs-tab')][./div[text()='옵션']]"       # 옵션 탭

class PercentyImageManager:
    """
    퍼센티 이미지 관리 유틸리티
    - 상세페이지 이미지 관리
      - 이미지 개수 확인
      - 특정 이미지 삭제
      - 앞/뒤 이미지 일괄 삭제
      - 30개 초과 이미지 삭제
    - 섬네일 이미지 관리
      - 특정 섬네일 삭제
      - 섬네일 위치 변경
      - 옵션 이미지를 섬네일로 자동 추가
    """
    
    def __init__(self, driver):
        """
        초기화
        
        Args:
            driver: Selenium WebDriver 인스턴스
        """
        self.driver = driver
    
    def open_bulk_edit_modal(self, timeout=10):
        """
        상세페이지 탭에서 일괄편집 버튼을 클릭하여 이미지 관리 모달창 열기
        
        Args:
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("상세페이지 일괄편집 버튼 클릭")
            
            # 일괄편집 버튼 선택자
            bulk_edit_button_selector = "//button[contains(@class, 'ant-btn')][.//span[text()='일괄 편집']][.//span[@role='img' and @aria-label='form']]"
            
            try:
                bulk_edit_button = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((By.XPATH, bulk_edit_button_selector))
                )
                bulk_edit_button.click()
                time.sleep(DELAY_SHORT)
                
                # 모달창이 열렸는지 확인
                modal_title_selector = "//span[contains(@class, 'CharacterTitle85') and contains(text(), '상세페이지 이미지')]"
                WebDriverWait(self.driver, timeout).until(
                    EC.visibility_of_element_located((By.XPATH, modal_title_selector))
                )
                
                logger.info("상세페이지 이미지 모달창이 열렸습니다.")
                return True
                
            except (TimeoutException, NoSuchElementException) as e:
                logger.error(f"일괄편집 버튼을 찾을 수 없습니다: {e}")
                return False
                
        except Exception as e:
            logger.error(f"일괄편집 모달창 열기 오류: {e}")
            return False
    
    def get_image_count(self, timeout=10):
        """
        현재 상세페이지 이미지의 총 개수 확인
        
        Args:
            timeout: 최대 대기 시간(초)
            
        Returns:
            int: 이미지 개수 (실패 시 -1)
        """
        try:
            logger.info("상세페이지 이미지 개수 확인")
            
            # 이미지 개수 텍스트 선택자
            count_text_selector = "//span[contains(@class, 'CharacterTitle85') and contains(text(), '총') and contains(text(), '개의 이미지')]"
            
            try:
                count_element = WebDriverWait(self.driver, timeout).until(
                    EC.visibility_of_element_located((By.XPATH, count_text_selector))
                )
                
                # 텍스트에서 숫자만 추출 (예: "총 29개의 이미지" -> 29)
                count_text = count_element.text
                image_count = int(''.join(filter(str.isdigit, count_text)))
                
                logger.info(f"상세페이지 이미지 개수: {image_count}")
                return image_count
                
            except (TimeoutException, NoSuchElementException) as e:
                logger.error(f"이미지 개수 정보를 찾을 수 없습니다: {e}")
                return -1
                
        except Exception as e:
            logger.error(f"이미지 개수 확인 오류: {e}")
            return -1
    
    def delete_image_by_index(self, index, timeout=10):
        """
        특정 인덱스의 이미지 삭제 (0부터 시작)
        
        Args:
            index: 삭제할 이미지 인덱스 (0부터 시작)
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"{index+1}번째 이미지 삭제")
            
            # 해당 인덱스의 이미지 삭제 버튼 선택자
            # 더 안정적인 선택자 사용 (styled-components 클래스명 변경 대응)
            image_cards_selector = "//div[contains(@class, 'ant-col') and .//img and .//span[text()='삭제']]"
            
            try:
                # 모든 이미지 카드 찾기
                image_cards = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_all_elements_located((By.XPATH, image_cards_selector))
                )
                
                # 인덱스 범위 확인
                if index < 0 or index >= len(image_cards):
                    logger.error(f"유효하지 않은 이미지 인덱스입니다: {index} (총 이미지: {len(image_cards)})")
                    return False
                
                # 해당 카드의 삭제 버튼 찾기
                delete_button_selector = ".//span[text()='삭제']"
                delete_button = image_cards[index].find_element(By.XPATH, delete_button_selector)
                
                # 삭제 버튼 클릭
                delete_button.click()
                time.sleep(DELAY_SHORT)
                
                logger.info(f"{index+1}번째 이미지 삭제 완료")
                return True
                
            except (TimeoutException, NoSuchElementException) as e:
                logger.error(f"이미지 또는 삭제 버튼을 찾을 수 없습니다: {e}")
                return False
                
        except Exception as e:
            logger.error(f"이미지 삭제 오류: {e}")
            return False
    
    def delete_first_n_images(self, count, timeout=10):
        """
        앞에서부터 지정된 개수만큼 이미지 삭제
        
        Args:
            count: 삭제할 이미지 개수
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"앞에서부터 {count}개 이미지 삭제")
            
            if count <= 0:
                logger.warning("삭제할 이미지 개수는 1 이상이어야 합니다.")
                return False
            
            # 지정된 개수만큼 첫 번째 이미지 반복 삭제
            for i in range(count):
                # 항상 첫 번째(인덱스 0) 이미지를 삭제
                # 첫 번째 이미지 삭제 후에는 다음 이미지가 첫 번째로 이동하므로 계속 인덱스 0 사용
                if not self.delete_image_by_index(0, timeout):
                    logger.error(f"{i+1}번째 이미지 삭제 실패, 중단합니다.")
                    return False
                time.sleep(DELAY_SHORT)
            
            logger.info(f"앞에서부터 {count}개 이미지 삭제 완료")
            return True
            
        except Exception as e:
            logger.error(f"앞 이미지 삭제 오류: {e}")
            return False
    
    def delete_last_n_images(self, count, timeout=10):
        """
        뒤에서부터 지정된 개수만큼 이미지 삭제
        
        Args:
            count: 삭제할 이미지 개수
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"뒤에서부터 {count}개 이미지 삭제")
            
            if count <= 0:
                logger.warning("삭제할 이미지 개수는 1 이상이어야 합니다.")
                return False
            
            # 현재 이미지 총 개수 확인
            total_images = self.get_image_count(timeout)
            if total_images <= 0:
                logger.error("이미지 개수를 확인할 수 없습니다.")
                return False
            
            # 삭제할 개수가 전체 이미지보다 많은 경우 조정
            if count > total_images:
                logger.warning(f"삭제 요청된 이미지({count}개)가 전체 이미지({total_images}개)보다 많습니다. 전체 이미지를 삭제합니다.")
                count = total_images
            
            # 지정된 개수만큼 마지막 이미지 반복 삭제
            for i in range(count):
                # 현재 이미지 개수 다시 확인 (삭제 후 개수가 변경되므로)
                current_total = self.get_image_count(timeout)
                if current_total <= 0:
                    logger.error("이미지 개수를 확인할 수 없습니다.")
                    return False
                
                # 마지막 이미지 인덱스 계산
                last_index = current_total - 1
                
                # 마지막 이미지 삭제
                if not self.delete_image_by_index(last_index, timeout):
                    logger.error(f"{i+1}번째 마지막 이미지 삭제 실패, 중단합니다.")
                    return False
                
                time.sleep(DELAY_SHORT)
            
            logger.info(f"뒤에서부터 {count}개 이미지 삭제 완료")
            return True
            
        except Exception as e:
            logger.error(f"뒤 이미지 삭제 오류: {e}")
            return False
    
    def delete_images_beyond_limit(self, limit=30, timeout=10):
        """
        지정된 개수 이상의 이미지를 모두 삭제
        
        Args:
            limit: 유지할 이미지 개수 (초과분 삭제)
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"{limit}개 초과 이미지 삭제")
            
            # 현재 이미지 총 개수 확인
            total_images = self.get_image_count(timeout)
            if total_images <= 0:
                logger.error("이미지 개수를 확인할 수 없습니다.")
                return False
            
            # 제한 개수 초과 여부 확인
            if total_images <= limit:
                logger.info(f"현재 이미지 개수({total_images}개)가 제한({limit}개) 이하입니다. 삭제할 이미지가 없습니다.")
                return True
            
            # 삭제할 이미지 개수 계산
            images_to_delete = total_images - limit
            
            # 뒤에서부터 초과분 이미지 삭제
            return self.delete_last_n_images(images_to_delete, timeout)
            
        except Exception as e:
            logger.error(f"제한 초과 이미지 삭제 오류: {e}")
            return False

    def go_to_tab(self, tab_selector, timeout=10):
        """
        지정된 탭으로 이동
        
        Args:
            tab_selector: 이동할 탭의 XPath 선택자
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"탭으로 이동: {tab_selector}")
            
            tab = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, tab_selector))
            )
            tab.click()
            time.sleep(DELAY_SHORT)
            
            return True
            
        except Exception as e:
            logger.error(f"탭 이동 오류: {e}")
            return False
    
    def go_to_thumbnail_tab(self, timeout=10):
        """
        섬네일 탭으로 이동
        
        Args:
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        return self.go_to_tab(TAB_THUMBNAIL, timeout)
    
    def go_to_options_tab(self, timeout=10):
        """
        옵션 탭으로 이동
        
        Args:
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        return self.go_to_tab(TAB_OPTIONS, timeout)
    
    def go_to_detail_tab(self, timeout=10):
        """
        상세페이지 탭으로 이동
        
        Args:
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        return self.go_to_tab(TAB_DETAIL, timeout)
    
    def get_thumbnail_count(self, timeout=10):
        """
        현재 섬네일 이미지의 총 개수 확인
        
        Args:
            timeout: 최대 대기 시간(초)
            
        Returns:
            int: 섬네일 개수 (실패 시 -1)
        """
        try:
            # 섬네일 탭으로 이동
            if not self.go_to_thumbnail_tab(timeout):
                return -1
                
            logger.info("섬네일 이미지 개수 확인")
            
            # 섬네일 컨테이너 내의 이미지 요소들 가져오기
            thumbnail_items_selector = "//div[contains(@class, 'ant-tabs-tabpane-active')]//div[contains(@class, 'ant-image-preview')]"            
            try:
                # 5초 정도 대기하며 섬네일 이미지들이 로드되기를 기다림
                thumbnail_items = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_all_elements_located((By.XPATH, thumbnail_items_selector))
                )
                
                count = len(thumbnail_items)
                logger.info(f"섬네일 이미지 개수: {count}")
                return count
                
            except (TimeoutException, NoSuchElementException) as e:
                logger.error(f"섬네일 이미지 요소를 찾을 수 없습니다: {e}")
                return -1
                
        except Exception as e:
            logger.error(f"섬네일 개수 확인 오류: {e}")
            return -1
    
    def delete_thumbnail_by_index(self, index, timeout=10):
        """
        특정 인덱스의 섬네일 삭제 (0부터 시작)
        
        Args:
            index: 삭제할 섬네일 인덱스 (0부터 시작)
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            # 섬네일 탭으로 이동
            if not self.go_to_thumbnail_tab(timeout):
                return False
                
            logger.info(f"{index+1}번째 섬네일 삭제")
            
            # 삭제할 섬네일 요소 찾기
            thumbnail_items_selector = "//div[contains(@class, 'ant-tabs-tabpane-active')]//div[contains(@class, 'ant-image-preview')]"            
            thumbnail_items = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located((By.XPATH, thumbnail_items_selector))
            )
            
            if index < 0 or index >= len(thumbnail_items):
                logger.error(f"인덱스({index})가 유효하지 않습니다. 현재 섬네일 개수: {len(thumbnail_items)}")
                return False
            
            # 삭제할 섬네일 요소 선택
            target_thumbnail = thumbnail_items[index]
            
            # 마우스 오버하여 삭제 버튼 표시
            actions = ActionChains(self.driver)
            actions.move_to_element(target_thumbnail).perform()
            time.sleep(DELAY_SHORT)
            
            # 삭제 버튼 클릭
            delete_button_selector = f"(//div[contains(@class, 'ant-tabs-tabpane-active')]//div[contains(@class, 'ant-image-preview')])[{index+1}]//span[contains(@class, 'icon-delete')]"
            delete_button = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, delete_button_selector))
            )
            delete_button.click()
            time.sleep(DELAY_SHORT)
            
            # 삭제 확인 대화상자에서 확인 버튼 클릭
            confirm_button_selector = "//div[contains(@class, 'ant-modal-confirm-btns')]//button[contains(@class, 'ant-btn-primary')]"
            confirm_button = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, confirm_button_selector))
            )
            confirm_button.click()
            time.sleep(DELAY_SHORT)
            
            logger.info(f"{index+1}번째 섬네일 삭제 완료")
            return True
            
        except Exception as e:
            logger.error(f"섬네일 삭제 오류: {e}")
            return False
    
    def delete_multiple_thumbnails(self, indices, timeout=10):
        """
        여러 개의 섬네일을 삭제 (인덱스 목록 기준)
        
        Args:
            indices: 삭제할 섬네일 인덱스 목록 (0부터 시작)
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            # 섬네일 탭으로 이동
            if not self.go_to_thumbnail_tab(timeout):
                return False
                
            logger.info(f"여러 섬네일 삭제: {indices}")
            
            # 인덱스를 내림차순으로 정렬 (뒤에서부터 삭제해야 인덱스 변화 영향 없음)
            sorted_indices = sorted(indices, reverse=True)
            
            # 각 인덱스에 해당하는 섬네일 삭제
            for idx in sorted_indices:
                if not self.delete_thumbnail_by_index(idx, timeout):
                    logger.error(f"인덱스 {idx}의 섬네일 삭제 실패, 중단합니다.")
                    return False
                time.sleep(DELAY_SHORT)
            
            logger.info("여러 섬네일 삭제 완료")
            return True
            
        except Exception as e:
            logger.error(f"여러 섬네일 삭제 오류: {e}")
            return False
    
    def move_thumbnail_to_front(self, index, timeout=10):
        """
        특정 인덱스의 섬네일을 맨 앞으로 이동
        
        Args:
            index: 이동할 섬네일 인덱스 (0부터 시작)
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            # 섬네일 탭으로 이동
            if not self.go_to_thumbnail_tab(timeout):
                return False
                
            logger.info(f"{index+1}번째 섬네일을 맨 앞으로 이동")
            
            # 이동할 섬네일 요소 찾기
            thumbnail_items_selector = "//div[contains(@class, 'ant-tabs-tabpane-active')]//div[contains(@class, 'ant-image-preview')]"            
            thumbnail_items = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located((By.XPATH, thumbnail_items_selector))
            )
            
            if index < 0 or index >= len(thumbnail_items):
                logger.error(f"인덱스({index})가 유효하지 않습니다. 현재 섬네일 개수: {len(thumbnail_items)}")
                return False
            
            # 이미 맨 앞인 경우 처리
            if index == 0:
                logger.info("이미 맨 앞에 위치한 섬네일입니다. 이동 불필요.")
                return True
            
            # 이동할 섬네일 요소 선택
            target_thumbnail = thumbnail_items[index]
            
            # 마우스 오버하여 버튼 표시
            actions = ActionChains(self.driver)
            actions.move_to_element(target_thumbnail).perform()
            time.sleep(DELAY_SHORT)
            
            # 편집 버튼 클릭
            edit_button_selector = f"(//div[contains(@class, 'ant-tabs-tabpane-active')]//div[contains(@class, 'ant-image-preview')])[{index+1}]//span[contains(@class, 'icon-edit')]"
            edit_button = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, edit_button_selector))
            )
            edit_button.click()
            time.sleep(DELAY_SHORT)
            
            # 메인 이미지로 설정 (맨 앞으로 이동) 버튼 클릭
            main_image_button_selector = "//div[contains(@class, 'ant-modal-root')]//button[contains(., '메인 이미지로 설정')]"
            main_image_button = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, main_image_button_selector))
            )
            main_image_button.click()
            time.sleep(DELAY_SHORT)
            
            logger.info(f"{index+1}번째 섬네일을 맨 앞으로 이동 완료")
            return True
            
        except Exception as e:
            logger.error(f"섬네일 위치 이동 오류: {e}")
            return False
    
    def copy_image_from_options_to_thumbnail(self, option_index, timeout=10):
        """
        옵션 탭의 이미지를 섬네일로 복사
        
        Args:
            option_index: 복사할 옵션 이미지 인덱스 (0부터 시작)
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            # 옵션 탭으로 이동
            if not self.go_to_options_tab(timeout):
                return False
                
            logger.info(f"옵션 탭의 {option_index+1}번째 이미지를 섬네일로 복사")
            
            # 복사할 옵션 이미지 요소 찾기
            option_items_selector = "//div[contains(@class, 'ant-tabs-tabpane-active')]//div[contains(@class, 'ant-image-preview')]"            
            option_items = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located((By.XPATH, option_items_selector))
            )
            
            if option_index < 0 or option_index >= len(option_items):
                logger.error(f"인덱스({option_index})가 유효하지 않습니다. 현재 옵션 이미지 개수: {len(option_items)}")
                return False
            
            # 복사할 옵션 이미지 요소 선택
            target_option_image = option_items[option_index]
            
            # 마우스 오버하여 버튼 표시
            actions = ActionChains(self.driver)
            actions.move_to_element(target_option_image).perform()
            time.sleep(DELAY_SHORT)
            
            # 상세페이지로 복사 버튼 클릭
            copy_button_selector = f"(//div[contains(@class, 'ant-tabs-tabpane-active')]//div[contains(@class, 'ant-image-preview')])[{option_index+1}]//span[contains(@class, 'icon-copy')]"
            copy_button = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, copy_button_selector))
            )
            copy_button.click()
            time.sleep(DELAY_SHORT)
            
            logger.info(f"옵션 탭의 {option_index+1}번째 이미지를 섬네일로 복사 완료")
            return True
            
        except Exception as e:
            logger.error(f"옵션 이미지 복사 오류: {e}")
            return False
    
    def ensure_minimum_thumbnails(self, min_count=5, timeout=10):
        """
        최소 개수의 섬네일이 있는지 확인하고, 부족하면 옵션 이미지에서 자동으로 추가
        
        Args:
            min_count: 최소 섬네일 개수
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"최소 {min_count}개의 섬네일 확보")
            
            # 현재 섬네일 개수 확인
            current_thumbnails = self.get_thumbnail_count(timeout)
            if current_thumbnails < 0:
                logger.error("섬네일 개수를 확인할 수 없습니다.")
                return False
            
            # 이미 충분한 섬네일이 있는 경우
            if current_thumbnails >= min_count:
                logger.info(f"이미 충분한 섬네일이 있습니다. (현재: {current_thumbnails}개, 최소: {min_count}개)")
                return True
            
            # 추가해야 할 섬네일 개수
            thumbnails_to_add = min_count - current_thumbnails
            logger.info(f"추가 필요한 섬네일 개수: {thumbnails_to_add}개")
            
            # 옵션 탭으로 이동하여 이미지 개수 확인
            if not self.go_to_options_tab(timeout):
                return False
            
            option_items_selector = "//div[contains(@class, 'ant-tabs-tabpane-active')]//div[contains(@class, 'ant-image-preview')]"            
            option_items = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located((By.XPATH, option_items_selector))
            )
            
            option_image_count = len(option_items)
            
            if option_image_count <= 0:
                logger.warning("옵션 이미지가 없어 섬네일을 추가할 수 없습니다.")
                return False
            
            # 복사할 수 있는 최대 개수 계산
            max_available = min(thumbnails_to_add, option_image_count)
            
            # 옵션 이미지를 섬네일로 복사
            for i in range(max_available):
                if not self.copy_image_from_options_to_thumbnail(i, timeout):
                    logger.error(f"{i+1}번째 옵션 이미지 복사 실패, 중단합니다.")
                    return False
                time.sleep(DELAY_SHORT)
            
            # 섬네일 탭으로 돌아가기
            if not self.go_to_thumbnail_tab(timeout):
                return False
            
            # 최종 섬네일 개수 확인
            final_thumbnails = self.get_thumbnail_count(timeout)
            
            logger.info(f"섬네일 추가 완료: {current_thumbnails}개 → {final_thumbnails}개")
            return final_thumbnails >= current_thumbnails + max_available
            
        except Exception as e:
            logger.error(f"최소 섬네일 확보 오류: {e}")
            return False

    def close_bulk_edit_modal(self, timeout=8):
        """
        일괄편집 모달창 닫기
        
        Args:
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("일괄편집 모달창 닫기")
            
            # 먼저 모달창이 열려있는지 확인
            modal_selectors = [
                "//span[contains(@class, 'CharacterTitle85') and contains(text(), '상세페이지 이미지')]",
                "//div[contains(@class, 'ant-modal-content') and .//span[contains(text(), '상세페이지 이미지')]]",
                "//div[contains(@class, 'ant-modal') and contains(@class, 'ant-modal-open')]"
            ]
            
            modal_found = False
            for selector in modal_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements and elements[0].is_displayed():
                        modal_found = True
                        break
                except Exception:
                    continue
            
            if not modal_found:
                logger.info("일괄편집 모달창이 이미 닫혀있음")
                return True
            
            # 방법 1: ESC 키 사용
            try:
                logger.info("ESC 키로 모달창 닫기 시도")
                from selenium.webdriver.common.keys import Keys
                self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                time.sleep(2)
                
                # 모달창이 닫혔는지 확인
                modal_closed = True
                for selector in modal_selectors:
                    try:
                        elements = self.driver.find_elements(By.XPATH, selector)
                        if elements and elements[0].is_displayed():
                            modal_closed = False
                            break
                    except Exception:
                        continue
                
                if modal_closed:
                    logger.info("ESC 키로 일괄편집 모달창 닫기 성공")
                    return True
                else:
                    logger.warning("ESC 키로 모달창이 닫히지 않음, 추가 시도")
            except Exception as e:
                logger.warning(f"ESC 키 시도 중 오류: {e}")
            
            # 방법 2: 닫기 버튼 클릭
            close_selectors = [
                "//button[contains(@class, 'ant-modal-close')]",
                "//span[contains(@class, 'ant-modal-close-x')]",
                "//button[@aria-label='Close']",
                "//div[contains(@class, 'ant-modal-close')]"
            ]
            
            for selector in close_selectors:
                try:
                    logger.info(f"닫기 버튼 클릭 시도: {selector}")
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements and elements[0].is_displayed():
                        elements[0].click()
                        time.sleep(2)
                        
                        # 모달창이 닫혔는지 확인
                        modal_closed = True
                        for modal_selector in modal_selectors:
                            try:
                                modal_elements = self.driver.find_elements(By.XPATH, modal_selector)
                                if modal_elements and modal_elements[0].is_displayed():
                                    modal_closed = False
                                    break
                            except Exception:
                                continue
                        
                        if modal_closed:
                            logger.info("닫기 버튼으로 일괄편집 모달창 닫기 성공")
                            return True
                except Exception as e:
                    logger.debug(f"닫기 버튼 {selector} 클릭 실패: {e}")
                    continue
            
            logger.warning("모달창 닫기 실패")
            return False
                
        except Exception as e:
            logger.error(f"모달창 닫기 오류: {e}")
            return False

def get_image_manager(driver):
    """
    이미지 관리자 인스턴스 생성
    
    Args:
        driver: Selenium WebDriver 인스턴스
        
    Returns:
        PercentyImageManager: 이미지 관리자 인스턴스
    """
    return PercentyImageManager(driver)
