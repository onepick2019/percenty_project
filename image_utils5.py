import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException, ElementNotInteractableException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

# 로깅 설정
logger = logging.getLogger(__name__)

# 지연 시간 상수
DELAY_SHORT = 1
DELAY_MEDIUM = 2
DELAY_LONG = 3

# 탭 선택자 상수 - 7.md의 HTML 구조를 기반으로 개선된 선택자
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
            logger.info("일괄편집 버튼 클릭 시도")
            
            # 일괄편집 버튼 찾기 및 클릭
            bulk_edit_button = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '일괄편집')]"))
            )
            bulk_edit_button.click()
            
            # 모달창이 열릴 때까지 대기
            time.sleep(DELAY_MEDIUM)
            
            logger.info("일괄편집 모달창이 성공적으로 열렸습니다")
            return True
            
        except Exception as e:
            logger.error(f"일괄편집 모달창 열기 실패: {e}")
            return False
    
    def close_bulk_edit_modal(self, timeout=10):
        """
        일괄편집 모달창 닫기
        
        Args:
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("일괄편집 모달창 닫기 시도")
            
            # 닫기 버튼 찾기 및 클릭
            close_button = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'ant-modal-close')]"))
            )
            close_button.click()
            
            # 모달창이 닫힐 때까지 대기
            time.sleep(DELAY_MEDIUM)
            
            logger.info("일괄편집 모달창이 성공적으로 닫혔습니다")
            return True
            
        except Exception as e:
            logger.error(f"일괄편집 모달창 닫기 실패: {e}")
            return False
    
    def get_image_count(self, timeout=10):
        """
        현재 상세페이지의 이미지 개수 확인
        
        Args:
            timeout: 최대 대기 시간(초)
            
        Returns:
            int: 이미지 개수 (실패 시 -1)
        """
        try:
            logger.info("이미지 개수 확인 중...")
            
            # 이미지 요소들 찾기
            images = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'image-item')]"))
            )
            
            count = len(images)
            logger.info(f"현재 이미지 개수: {count}개")
            return count
            
        except Exception as e:
            logger.error(f"이미지 개수 확인 실패: {e}")
            return -1
    
    def delete_image_by_index(self, index, timeout=10):
        """
        특정 인덱스의 이미지 삭제
        
        Args:
            index: 삭제할 이미지의 인덱스 (0부터 시작)
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"{index + 1}번째 이미지 삭제 시도")
            
            # 특정 인덱스의 이미지 삭제 버튼 찾기
            delete_button = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, f"(//div[contains(@class, 'image-item')])[{index + 1}]//button[contains(@class, 'delete-btn')]"))
            )
            delete_button.click()
            
            # 삭제 확인 대기
            time.sleep(DELAY_SHORT)
            
            logger.info(f"{index + 1}번째 이미지가 성공적으로 삭제되었습니다")
            return True
            
        except Exception as e:
            logger.error(f"{index + 1}번째 이미지 삭제 실패: {e}")
            return False
    
    def delete_first_n_images(self, n, timeout=10):
        """
        앞에서부터 n개의 이미지 삭제
        
        Args:
            n: 삭제할 이미지 개수
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"앞에서부터 {n}개 이미지 삭제 시작")
            
            for i in range(n):
                # 항상 첫 번째 이미지를 삭제 (삭제 후 인덱스가 재정렬되므로)
                if not self.delete_image_by_index(0, timeout):
                    logger.error(f"{i + 1}번째 이미지 삭제 실패")
                    return False
                
                # 각 삭제 후 잠시 대기
                time.sleep(DELAY_SHORT)
            
            logger.info(f"앞에서부터 {n}개 이미지 삭제 완료")
            return True
            
        except Exception as e:
            logger.error(f"앞에서부터 {n}개 이미지 삭제 실패: {e}")
            return False
    
    def delete_last_n_images(self, n, timeout=10):
        """
        뒤에서부터 n개의 이미지 삭제
        
        Args:
            n: 삭제할 이미지 개수
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"뒤에서부터 {n}개 이미지 삭제 시작")
            
            # 현재 이미지 개수 확인
            total_count = self.get_image_count(timeout)
            if total_count == -1:
                logger.error("이미지 개수 확인 실패")
                return False
            
            # 뒤에서부터 삭제
            for i in range(n):
                last_index = total_count - 1 - i
                if not self.delete_image_by_index(last_index, timeout):
                    logger.error(f"뒤에서 {i + 1}번째 이미지 삭제 실패")
                    return False
                
                # 각 삭제 후 잠시 대기
                time.sleep(DELAY_SHORT)
            
            logger.info(f"뒤에서부터 {n}개 이미지 삭제 완료")
            return True
            
        except Exception as e:
            logger.error(f"뒤에서부터 {n}개 이미지 삭제 실패: {e}")
            return False
    
    def delete_excess_images(self, max_count=30, timeout=10):
        """
        최대 개수를 초과하는 이미지들을 뒤에서부터 삭제
        
        Args:
            max_count: 최대 허용 이미지 개수 (기본값: 30)
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"최대 {max_count}개 초과 이미지 삭제 시작")
            
            # 현재 이미지 개수 확인
            current_count = self.get_image_count(timeout)
            if current_count == -1:
                logger.error("이미지 개수 확인 실패")
                return False
            
            if current_count <= max_count:
                logger.info(f"현재 이미지 개수({current_count})가 최대 개수({max_count}) 이하입니다")
                return True
            
            # 초과하는 개수만큼 뒤에서부터 삭제
            excess_count = current_count - max_count
            logger.info(f"초과 이미지 {excess_count}개를 뒤에서부터 삭제합니다")
            
            return self.delete_last_n_images(excess_count, timeout)
            
        except Exception as e:
            logger.error(f"초과 이미지 삭제 실패: {e}")
            return False

    def go_to_tab(self, tab_selector, timeout=10):
        """
        지정된 탭으로 이동 - 개선된 버전
        
        Args:
            tab_selector: 이동할 탭의 XPath 선택자
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"탭으로 이동: {tab_selector}")
            
            # 탭 이름 추출 (섬네일, 상세페이지, 옵션)
            tab_name = "섬네일"  # 기본값
            if "상세페이지" in tab_selector:
                tab_name = "상세페이지"
            elif "옵션" in tab_selector:
                tab_name = "옵션"
            
            # product_editor.py에서 검증된 선택자들을 사용
            selectors_to_try = [
                # 가장 정확한 탭 선택자 - ant-tabs-tab 클래스와 텍스트 매칭
                f"//div[contains(@class, 'ant-tabs-tab')]//div[contains(@class, 'ant-tabs-tab-btn') and contains(text(), '{tab_name}')]",
                f"//div[contains(@class, 'ant-tabs-tab')]//div[contains(@class, 'ant-tabs-tab-btn')]/span[text()='{tab_name}']",
                f"//div[contains(@class, 'ant-tabs-tab')]//div[contains(@class, 'ant-tabs-tab-btn')]/span[contains(text(), '{tab_name}')]",
                
                # role="tab" 기반 선택자
                f"//div[@role='tab']//div[contains(text(), '{tab_name}')]",
                f"//div[@role='tab' and contains(@aria-selected, 'false')]//div[contains(text(), '{tab_name}')]",
                
                # 단순한 선택자들
                f"//div[contains(@class, 'ant-tabs-tab-btn') and contains(text(), '{tab_name}')]",
                
                # 네비게이션 리스트 기반
                f"//div[contains(@class, 'ant-tabs-nav-list')]//div[contains(@class, 'ant-tabs-tab')]//span[text()='{tab_name}']",
                f"//div[contains(@class, 'ant-tabs-nav-list')]//div[contains(@class, 'ant-tabs-tab')]//span[contains(text(), '{tab_name}')]",
                
                # 기존 선택자
                tab_selector,
                f"//div[contains(@class, 'ant-tabs-tab')]//span[text()='{tab_name}']",
                f"//div[contains(@class, 'ant-tabs-tab') and contains(text(), '{tab_name}')]",
                f"//div[@role='tab' and contains(text(), '{tab_name}')]",
                f"//span[text()='{tab_name}']/parent::div[contains(@class, 'ant-tabs-tab')]"
            ]
            
            for selector in selectors_to_try:
                try:
                    logger.info(f"선택자 시도: {selector}")
                    tab = WebDriverWait(self.driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    
                    # 스크롤하여 요소가 보이도록 함
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", tab)
                    time.sleep(0.3)
                    
                    # 클릭 시도
                    tab.click()
                    time.sleep(DELAY_SHORT)
                    
                    logger.info(f"탭 이동 성공: {selector}")
                    return True
                    
                except Exception as e:
                    logger.warning(f"선택자 {selector} 실패: {e}")
                    continue
            
            # 모든 선택자 실패 시 JavaScript 클릭 시도
            logger.info(f"JavaScript 클릭 시도 - {tab_name}")
            js_script = f"""
            var tabs = document.querySelectorAll('.ant-tabs-tab, [role="tab"]');
            for (var i = 0; i < tabs.length; i++) {{
                if (tabs[i].textContent.includes('{tab_name}')) {{
                    tabs[i].click();
                    return true;
                }}
            }}
            
            // 더 구체적인 검색
            var tabBtns = document.querySelectorAll('.ant-tabs-tab-btn');
            for (var i = 0; i < tabBtns.length; i++) {{
                if (tabBtns[i].textContent.includes('{tab_name}')) {{
                    tabBtns[i].click();
                    return true;
                }}
            }}
            
            return false;
            """
            
            result = self.driver.execute_script(js_script)
            if result:
                logger.info(f"JavaScript 클릭 성공 - {tab_name}")
                time.sleep(DELAY_SHORT)
                return True
            
            logger.error(f"모든 탭 이동 시도 실패 - {tab_name}")
            return False
            
        except TimeoutException:
            logger.error(f"탭 요소를 찾을 수 없습니다: {tab_selector}")
            return False
        except NoSuchElementException:
            logger.error(f"탭 요소가 존재하지 않습니다: {tab_selector}")
            return False
        except ElementNotInteractableException:
            logger.error(f"탭 요소와 상호작용할 수 없습니다: {tab_selector}")
            return False
        except WebDriverException as e:
            logger.error(f"WebDriver 오류: {tab_selector}, {e}")
            return False
        except Exception as e:
            logger.error(f"탭 이동 오류: {tab_selector}, {e}")
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
        현재 섬네일 개수 확인
        
        Args:
            timeout: 최대 대기 시간(초)
            
        Returns:
            int: 섬네일 개수 (실패 시 0)
        """
        try:
            # 7.md의 HTML 구조를 기반으로 한 선택자
            thumbnail_selectors = [
                "//div[contains(@class, 'sc-APcvf')]//img[contains(@class, 'sc-eWHaVC')]",
                "//div[contains(@class, 'ant-col')]//img[contains(@src, 'percenty.co.kr')]",
                "//div[contains(@class, 'ant-row')]//img[contains(@class, 'sc-eWHaVC')]"
            ]
            
            for selector in thumbnail_selectors:
                try:
                    thumbnails = self.driver.find_elements(By.XPATH, selector)
                    if thumbnails:
                        return len(thumbnails)
                except Exception:
                    continue
            
            return 0
            
        except Exception as e:
            logger.error(f"섬네일 개수 확인 실패: {e}")
            return 0
    
    def delete_thumbnail_by_index(self, index, timeout=10):
        """
        특정 인덱스의 섬네일 삭제
        
        Args:
            index: 삭제할 섬네일의 인덱스 (0부터 시작)
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"{index + 1}번째 섬네일 삭제 시도")
            
            # 7.md의 HTML 구조를 기반으로 한 삭제 버튼 선택자
            delete_selectors = [
                f"(//div[contains(@class, 'sc-APcvf')])[{index + 1}]//span[text()='삭제']",
                f"(//div[contains(@class, 'sc-leQnM')])[{index + 1}]//span[text()='삭제']",
                f"(//div[contains(@class, 'ant-col')]//img[contains(@src, 'percenty.co.kr')])[{index + 1}]/ancestor::div[contains(@class, 'ant-col')]//span[text()='삭제']"
            ]
            
            for selector in delete_selectors:
                try:
                    delete_button = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    
                    # 스크롤하여 요소가 보이도록 함
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", delete_button)
                    time.sleep(0.5)
                    
                    delete_button.click()
                    time.sleep(DELAY_SHORT)
                    
                    logger.info(f"{index + 1}번째 섬네일이 성공적으로 삭제되었습니다")
                    return True
                    
                except Exception as e:
                    logger.warning(f"삭제 선택자 {selector} 실패: {e}")
                    continue
            
            logger.error(f"{index + 1}번째 섬네일 삭제 실패 - 삭제 버튼을 찾을 수 없습니다")
            return False
            
        except Exception as e:
            logger.error(f"{index + 1}번째 섬네일 삭제 실패: {e}")
            return False
    
    def move_thumbnail_to_front(self, index, timeout=10):
        """
        특정 인덱스의 섬네일을 맨 앞으로 이동
        
        Args:
            index: 이동할 섬네일의 인덱스 (0부터 시작)
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"{index + 1}번째 섬네일을 맨 앞으로 이동 시도")
            
            # 7.md의 HTML 구조를 기반으로 한 드래그 가능한 요소 선택자
            # cursor: move 스타일이 있는 요소가 실제 드래그 가능한 영역
            drag_selectors = [
                f"(//div[contains(@class, 'ant-row') and contains(@style, 'cursor: move')])[{index + 1}]",
                f"(//div[contains(@class, 'sc-APcvf')])[{index + 1}]//div[contains(@style, 'cursor: move')]",
                f"(//div[contains(@class, 'sc-APcvf')])[{index + 1}]",
                f"(//div[contains(@class, 'ant-col')]//img[contains(@src, 'percenty.co.kr')])[{index + 1}]/ancestor::div[contains(@class, 'sc-APcvf')]",
                f"(//div[contains(@class, 'ant-col')]//img[contains(@class, 'sc-eWHaVC')])[{index + 1}]/ancestor::div[contains(@class, 'sc-APcvf')]"
            ]
            
            source_element = None
            for selector in drag_selectors:
                try:
                    source_element = WebDriverWait(self.driver, 2).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    logger.info(f"드래그 소스 요소 찾음: {selector}")
                    break
                except Exception as e:
                    logger.warning(f"드래그 선택자 {selector} 실패: {e}")
                    continue
            
            if not source_element:
                logger.error("드래그할 섬네일 요소를 찾을 수 없습니다")
                return False
            
            # 첫 번째 섬네일 위치 찾기 (드롭 타겟)
            target_selectors = [
                "(//div[contains(@class, 'ant-row') and contains(@style, 'cursor: move')])[1]",
                "(//div[contains(@class, 'sc-APcvf')])[1]//div[contains(@style, 'cursor: move')]",
                "(//div[contains(@class, 'sc-APcvf')])[1]",
                "(//div[contains(@class, 'ant-col')]//img[contains(@src, 'percenty.co.kr')])[1]/ancestor::div[contains(@class, 'sc-APcvf')]"
            ]
            
            target_element = None
            for selector in target_selectors:
                try:
                    target_element = self.driver.find_element(By.XPATH, selector)
                    logger.info(f"드롭 타겟 요소 찾음: {selector}")
                    break
                except Exception as e:
                    logger.warning(f"타겟 선택자 {selector} 실패: {e}")
                    continue
            
            if not target_element:
                logger.error("드롭할 위치를 찾을 수 없습니다")
                return False
            
            # 같은 요소인 경우 이동할 필요 없음
            if source_element == target_element:
                logger.info(f"{index + 1}번째 섬네일이 이미 맨 앞에 있습니다")
                return True
            
            # 스크롤하여 요소들이 보이도록 함
            self.driver.execute_script("arguments[0].scrollIntoView(true);", source_element)
            time.sleep(0.5)
            
            # 여러 방법으로 드래그 앤 드롭 시도
            methods = [
                self._drag_and_drop_with_actions,
                self._drag_and_drop_with_javascript,
                self._drag_and_drop_with_offset
            ]
            
            for method in methods:
                try:
                    if method(source_element, target_element):
                        logger.info(f"{index + 1}번째 섬네일이 성공적으로 맨 앞으로 이동되었습니다")
                        return True
                except Exception as e:
                    logger.warning(f"드래그 방법 {method.__name__} 실패: {e}")
                    continue
            
            logger.error(f"{index + 1}번째 섬네일 이동 실패 - 모든 방법 시도 완료")
            return False
            
        except Exception as e:
            logger.error(f"{index + 1}번째 섬네일 이동 실패: {e}")
            return False
    
    def _drag_and_drop_with_actions(self, source, target):
        """ActionChains를 사용한 드래그 앤 드롭"""
        logger.info("ActionChains 드래그 앤 드롭 시도")
        actions = ActionChains(self.driver)
        actions.drag_and_drop(source, target).perform()
        time.sleep(DELAY_MEDIUM)
        return True
    
    def _drag_and_drop_with_javascript(self, source, target):
        """JavaScript를 사용한 드래그 앤 드롭"""
        logger.info("JavaScript 드래그 앤 드롭 시도")
        js_script = """
        function simulateDragDrop(sourceNode, targetNode) {
            var EVENT_TYPES = {
                DRAG_END: 'dragend',
                DRAG_START: 'dragstart',
                DROP: 'drop'
            }
            
            function createCustomEvent(type) {
                var event = new CustomEvent("CustomEvent")
                event.initCustomEvent(type, true, true, null)
                event.dataTransfer = {
                    data: {},
                    setData: function(type, val) {
                        this.data[type] = val
                    },
                    getData: function(type) {
                        return this.data[type]
                    }
                }
                return event
            }
            
            var dragStartEvent = createCustomEvent(EVENT_TYPES.DRAG_START)
            sourceNode.dispatchEvent(dragStartEvent)
            
            var dropEvent = createCustomEvent(EVENT_TYPES.DROP)
            targetNode.dispatchEvent(dropEvent)
            
            var dragEndEvent = createCustomEvent(EVENT_TYPES.DRAG_END)
            sourceNode.dispatchEvent(dragEndEvent)
        }
        
        simulateDragDrop(arguments[0], arguments[1]);
        """
        
        self.driver.execute_script(js_script, source, target)
        time.sleep(DELAY_MEDIUM)
        return True
    
    def _drag_and_drop_with_offset(self, source, target):
        """오프셋을 사용한 드래그 앤 드롭"""
        logger.info("오프셋 드래그 앤 드롭 시도")
        actions = ActionChains(self.driver)
        
        # 소스와 타겟의 위치 계산
        source_location = source.location
        target_location = target.location
        
        offset_x = target_location['x'] - source_location['x']
        offset_y = target_location['y'] - source_location['y']
        
        actions.click_and_hold(source).move_by_offset(offset_x, offset_y).release().perform()
        time.sleep(DELAY_MEDIUM)
        return True
    
    def add_option_images_to_thumbnails(self, timeout=10):
        """
        옵션 탭의 이미지들을 섬네일로 자동 추가
        
        Args:
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("옵션 이미지를 섬네일로 추가 시작")
            
            # 옵션 탭으로 이동
            if not self.go_to_options_tab(timeout):
                logger.error("옵션 탭으로 이동 실패")
                return False
            
            # 옵션 이미지들 찾기
            option_images = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'option-image')]"))
            )
            
            if not option_images:
                logger.info("추가할 옵션 이미지가 없습니다")
                return True
            
            logger.info(f"{len(option_images)}개의 옵션 이미지를 섬네일로 추가합니다")
            
            # 각 옵션 이미지에 대해 섬네일 추가 버튼 클릭
            for i, image in enumerate(option_images):
                try:
                    # 섬네일 추가 버튼 찾기
                    add_button = image.find_element(By.XPATH, ".//button[contains(text(), '섬네일 추가')]")
                    add_button.click()
                    
                    time.sleep(DELAY_SHORT)
                    logger.info(f"{i + 1}번째 옵션 이미지를 섬네일로 추가했습니다")
                    
                except Exception as e:
                    logger.warning(f"{i + 1}번째 옵션 이미지 추가 실패: {e}")
                    continue
            
            # 섬네일 탭으로 돌아가기
            if not self.go_to_thumbnail_tab(timeout):
                logger.error("섬네일 탭으로 돌아가기 실패")
                return False
            
            logger.info("옵션 이미지를 섬네일로 추가 완료")
            return True
            
        except Exception as e:
            logger.error(f"옵션 이미지를 섬네일로 추가 실패: {e}")
            return False
    
    def optimize_thumbnails(self, max_thumbnails=5, timeout=10):
        """
        섬네일 최적화 (개수 조정 및 순서 정리)
        
        Args:
            max_thumbnails: 최대 섬네일 개수 (기본값: 5)
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"섬네일 최적화 시작 (최대 {max_thumbnails}개)")
            
            # 섬네일 탭으로 이동
            if not self.go_to_thumbnail_tab(timeout):
                logger.error("섬네일 탭으로 이동 실패")
                return False
            
            # 현재 섬네일 개수 확인
            current_count = self.get_thumbnail_count(timeout)
            if current_count == -1:
                logger.error("섬네일 개수 확인 실패")
                return False
            
            logger.info(f"현재 섬네일 개수: {current_count}개")
            
            # 섬네일이 부족한 경우 옵션 이미지에서 추가
            if current_count < max_thumbnails:
                logger.info(f"섬네일이 부족합니다. 옵션 이미지에서 추가를 시도합니다")
                self.add_option_images_to_thumbnails(timeout)
                
                # 추가 후 다시 개수 확인
                current_count = self.get_thumbnail_count(timeout)
                logger.info(f"추가 후 섬네일 개수: {current_count}개")
            
            # 섬네일이 너무 많은 경우 뒤에서부터 삭제
            if current_count > max_thumbnails:
                excess_count = current_count - max_thumbnails
                logger.info(f"초과 섬네일 {excess_count}개를 뒤에서부터 삭제합니다")
                
                for i in range(excess_count):
                    # 항상 마지막 섬네일 삭제
                    last_index = current_count - 1 - i
                    if not self.delete_thumbnail_by_index(last_index, timeout):
                        logger.warning(f"마지막 섬네일 삭제 실패")
                    else:
                        time.sleep(DELAY_SHORT)
            
            logger.info("섬네일 최적화 완료")
            return True
            
        except Exception as e:
            logger.error(f"섬네일 최적화 실패: {e}")
            return False