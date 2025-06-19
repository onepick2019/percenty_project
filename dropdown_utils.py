"""
퍼센티 플랫폼의 드롭박스 처리를 위한 유틸리티 모듈

다양한 화면(등록상품관리, 그룹상품관리, 신규상품등록)에서 드롭박스를 통해
특정 그룹을 선택하거나 검색하는 기능을 제공합니다.
"""

import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

# 로깅 설정
logger = logging.getLogger(__name__)

# 대기 시간 설정
DELAY_VERY_SHORT = 0.5
DELAY_SHORT = 1
DELAY_MEDIUM = 2
DELAY_LONG = 3

class PercentyDropdown:
    """퍼센티 드롭박스 및 그룹 선택 처리를 위한 클래스"""
    
    def __init__(self, driver):
        """
        드롭박스 및 그룹 선택 처리 클래스 초기화
        
        Args:
            driver: 셀레니움 웹드라이버 인스턴스
        """
        self.driver = driver
        logger.info("퍼센티 드롭박스 및 그룹 선택 유틸리티 초기화")
    
    # =============================================================================
    # 유형별 드롭박스 열기 메서드
    # =============================================================================
    
    def open_product_item_dropdown(self, item_index=0, timeout=2):
        """
        개별 상품 아이템의 그룹 드롭박스 열기
        (비그룹 상품보기에서 선택한 상품의 드롭박스)
        
        Args:
            item_index: 여러 상품이 있을 경우 상품 인덱스 (기본값: 0, 첫 번째 상품)
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"상품 아이템({item_index})의 그룹 드롭박스 열기")
            
            # 개별 상품의 드롭박스 선택자 - 더 정확한 선택자 사용
            selectors = [
                # '그룹 없음' 텍스트가 포함된 드롭박스 선택
                "//div[contains(@class, 'ant-select-single')][.//span[contains(text(), '그룹 없음')]]",
                
                # sc-dkmUuB 클래스가 포함된 드롭박스 선택 (상품 그룹 드롭박스에만 있는 클래스)
                "//div[contains(@class, 'ant-select-single')][.//span[contains(@class, 'sc-dkmUuB')]]",
                
                # 순서 기반 배열 선택자 (대체 수단으로만 사용)
                f"(//div[contains(@class, 'ant-select-single') and not(contains(@class, 'ant-select-borderless'))])[position()={item_index + 1}]",
                
                # 그룹상품관리 화면 (대체 선택자)
                f"(//div[contains(@class, 'sc-gwZKzw')]//div[contains(@class, 'ant-select-single')])[position()={item_index + 1}]"
            ]
            
            # JavaScript로 서술적 접근 시도 (선택자가 실패할 경우를 대비)
            js_script = """
            try {
                // 그룹 드롭박스 찾기 (그룹 없음 텍스트 포함 또는 sc-dkmUuB 클래스 포함)
                const groupDropdowns = Array.from(document.querySelectorAll('div.ant-select-single')).filter(el => {
                    return el.textContent.includes('그룹 없음') || 
                           el.querySelector('.sc-dkmUuB') !== null;
                });
                
                if (groupDropdowns.length > 0) {
                    const found = groupDropdowns[0];
                    found.scrollIntoView({behavior: 'smooth', block: 'center'});
                    return true;
                }
                return false;
            } catch (e) {
                return false;
            }
            """
            
            # 먼저 JavaScript로 요소를 화면 중앙에 보이게 하기
            self.driver.execute_script(js_script)
            time.sleep(DELAY_VERY_SHORT)  # 스크롤링 대기
            
            dropdown_element = None
            for selector in selectors:
                try:
                    dropdown_element = WebDriverWait(self.driver, timeout).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except (TimeoutException, NoSuchElementException):
                    continue
                    
            if not dropdown_element:
                # XPath 선택자가 실패하면 JavaScript로 직접 요소 클릭
                js_click_script = """
                try {
                    const groupDropdowns = Array.from(document.querySelectorAll('div.ant-select-single')).filter(el => {
                        return el.textContent.includes('그룹 없음') || 
                               el.querySelector('.sc-dkmUuB') !== null;
                    });
                    
                    if (groupDropdowns.length > 0) {
                        groupDropdowns[0].click();
                        return true;
                    }
                    return false;
                } catch (e) {
                    return false;
                }
                """
                
                clicked = self.driver.execute_script(js_click_script)
                if clicked:
                    logger.info("JavaScript를 사용해 그룹 드롭박스 클릭 성공")
                    time.sleep(DELAY_SHORT)
                    return True
                else:
                    logger.error("상품 아이템의 그룹 드롭박스를 찾을 수 없습니다.")
                    return False
                
            # 드롭박스 클릭
            dropdown_element.click()
            time.sleep(DELAY_SHORT)
            logger.info("드롭박스가 열렸습니다.")
            return True
            
        except Exception as e:
            logger.error(f"드롭박스 열기 오류: {e}")
            return False
    
    def open_group_search_dropdown(self, timeout=2):
        """
        그룹 검색용 드롭박스 열기
        (등록상품관리, 신규상품등록 화면의 상단에 있는 그룹 검색 드롭박스)
        
        Args:
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("그룹 검색용 드롭박스 열기")
            
            # 그룹 검색 드롭박스 선택자
            selectors = [
                # 신규상품등록, 등록상품관리 화면 그룹 검색 드롭박스
                "//div[contains(@class, 'ant-select-single')][.//span[contains(@class, 'ant-select-selection-item') and contains(text(), '전체')]]",
                # 대체 선택자
                "//div[contains(@class, 'ant-select-borderless')][.//span[contains(@class, 'ant-select-selection-item') and contains(text(), '전체')]]"
            ]
            
            dropdown_element = None
            for selector in selectors:
                try:
                    dropdown_element = WebDriverWait(self.driver, timeout).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except (TimeoutException, NoSuchElementException):
                    continue
                    
            if not dropdown_element:
                logger.error("그룹 검색 드롭박스를 찾을 수 없습니다.")
                return False
                    
            # 드롭박스 클릭
            dropdown_element.click()
            time.sleep(DELAY_SHORT)
            logger.info("그룹 검색 드롭박스가 열렸습니다.")
            return True
                
        except Exception as e:
            logger.error(f"그룹 검색 드롭박스 열기 오류: {e}")
            return False

    def select_items_per_page(self, count=20, timeout=2):
        """
        페이지당 표시할 상품 개수 선택 (20개씩 보기 또는 50개씩 보기)
        
        Args:
            count: 표시할 상품 개수 (20 또는 50)
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            if count not in [20, 50]:
                logger.error(f"지원되지 않는 상품 개수입니다: {count} (20 또는 50만 지원)")
                return False
                
            logger.info(f"{count}개씩 보기 설정")
            
            # 페이지당 상품 개수 드롭박스 선택자
            selectors = [
                # 상품 개수 선택 드롭박스 (20개씩 보기 또는 50개씩 보기)
                f"//div[contains(@class, 'ant-select-single')][.//span[contains(@class, 'ant-select-selection-item') and contains(text(), '개씩 보기')]]",
                # 대체 선택자
                f"//div[contains(@class, 'ant-select-borderless')][.//span[contains(@class, 'ant-select-selection-item') and contains(text(), '개씩 보기')]]"
            ]
            
            dropdown_element = None
            for selector in selectors:
                try:
                    dropdown_element = WebDriverWait(self.driver, timeout).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except (TimeoutException, NoSuchElementException):
                    continue
                    
            if not dropdown_element:
                logger.error("페이지당 상품 개수 드롭박스를 찾을 수 없습니다.")
                return False
                    
            # 현재 선택된 값 확인
            current_text = dropdown_element.text
            current_count = 20  # 기본값
            
            if "20개씩 보기" in current_text:
                current_count = 20
            elif "50개씩 보기" in current_text:
                current_count = 50
                
            # 이미 선택된 값이면 건너뛰기
            if current_count == count:
                logger.info(f"이미 {count}개씩 보기가 선택되어 있습니다.")
                return True
                    
            # 드롭박스 클릭하여 열기
            dropdown_element.click()
            time.sleep(DELAY_SHORT)
            
            # 원하는 개수 옵션 선택
            option_selector = f"//div[contains(@class, 'ant-select-item-option')][.//span[text()='{count}개씩 보기'] or .//div[text()='{count}개씩 보기']]"           
            try:
                option_element = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((By.XPATH, option_selector))
                )
                option_element.click()
                time.sleep(DELAY_SHORT)
                logger.info(f"{count}개씩 보기로 설정되었습니다.")
                return True
            except (TimeoutException, NoSuchElementException):
                logger.error(f"{count}개씩 보기 옵션을 찾을 수 없습니다.")
                return False
                
        except Exception as e:
            logger.error(f"페이지당 상품 개수 설정 오류: {e}")
            return False
    
    def select_all_products(self, timeout=2):
        """
        상품 전체 선택 체크박스 클릭
        
        Args:
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("상품 전체 선택")
            
            # 전체 선택 체크박스 선택자 (메뉴별로 다른 선택자를 시도)
            selectors = [
                # 신규상품등록, 등록상품관리 화면 전체선택 체크박스
                "//label[contains(@class, 'ant-checkbox-wrapper')]//span[contains(@class, 'ant-checkbox')]//input[@type='checkbox']",
                # 그룹상품관리 화면 전체선택 체크박스
                "//th[contains(@class, 'ant-table-selection-column')]//span[contains(@class, 'ant-checkbox')]//input[@type='checkbox']",
                # 대체 선택자
                "//div[contains(@class, 'ant-table-header')]//span[contains(@class, 'ant-checkbox')]//input[@type='checkbox']"
            ]
            
            checkbox_element = None
            for selector in selectors:
                try:
                    checkbox_element = WebDriverWait(self.driver, timeout).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except (TimeoutException, NoSuchElementException):
                    continue
                    
            if not checkbox_element:
                logger.error("전체 선택 체크박스를 찾을 수 없습니다.")
                return False
                    
            # 이미 선택되어 있는지 확인
            is_checked = checkbox_element.is_selected()
            
            # 선택되어 있지 않으면 클릭
            if not is_checked:
                checkbox_element.click()
                time.sleep(DELAY_SHORT)
                logger.info("상품 전체 선택되었습니다.")
            else:
                logger.info("이미 상품이 전체 선택되어 있습니다.")
                
            return True
                
        except Exception as e:
            logger.error(f"상품 전체 선택 오류: {e}")
            return False
    
    def select_first_product(self, timeout=2):
        """
        첫번째 상품의 체크박스 선택
        
        Args:
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("첫번째 상품 체크박스 선택")
            
            # 첫번째 상품의 체크박스 선택자들 (Select all 체크박스 제외)
            selectors = [
                # 테이블의 첫번째 행의 체크박스 (Select all 제외)
                "//tbody[contains(@class, 'ant-table-tbody')]//tr[1]//td[contains(@class, 'ant-table-selection-column')]//input[@type='checkbox' and not(@aria-label)]",
                # 첫번째 상품 행의 체크박스 (대체 선택자, Select all 제외)
                "//tr[contains(@class, 'ant-table-row')][1]//span[contains(@class, 'ant-checkbox')]//input[@type='checkbox' and not(@aria-label)]",
                # 더 구체적인 선택자 (Select all 제외)
                "//div[contains(@class, 'ant-table-body')]//tr[1]//label[contains(@class, 'ant-checkbox-wrapper')]//input[@type='checkbox' and not(@aria-label)]"
            ]
            
            checkbox_element = None
            for selector in selectors:
                try:
                    checkbox_element = WebDriverWait(self.driver, timeout).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except (TimeoutException, NoSuchElementException):
                    continue
                    
            if not checkbox_element:
                logger.error("첫번째 상품의 체크박스를 찾을 수 없습니다.")
                return False
                    
            # 이미 선택되어 있는지 확인
            is_checked = checkbox_element.is_selected()
            
            # 선택되어 있지 않으면 클릭
            if not is_checked:
                checkbox_element.click()
                time.sleep(DELAY_SHORT)
                logger.info("첫번째 상품이 선택되었습니다.")
            else:
                logger.info("첫번째 상품이 이미 선택되어 있습니다.")
                
            return True
                
        except Exception as e:
            logger.error(f"첫번째 상품 선택 오류: {e}")
            return False
    
    def open_group_assignment_modal(self, timeout=2):
        """
        그룹 지정 버튼을 클릭하여 그룹 이동 모달창 열기
        
        Args:
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("그룹 지정 버튼 클릭")
            
            # 그룹 지정 버튼 선택자
            selectors = [
                # 신규상품등록 화면 그룹 지정 버튼
                "//button[contains(@class, 'ant-btn')][.//span[text()='그룹 지정']]",
                # 등록상품관리 화면 그룹 지정 버튼
                "//div[contains(@class, 'ant-btn-group')]//button[.//span[text()='그룹 지정']]",
                # 그룹상품관리 화면 그룹 지정 버튼
                "//div[contains(@class, 'ant-flex')]//button[.//span[text()='그룹 지정']]"
            ]
            
            button_element = None
            for selector in selectors:
                try:
                    button_element = WebDriverWait(self.driver, timeout).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except (TimeoutException, NoSuchElementException):
                    continue
                    
            if not button_element:
                logger.error("그룹 지정 버튼을 찾을 수 없습니다.")
                return False
                    
            # 버튼이 비활성화되어 있는지 확인
            is_disabled = button_element.get_attribute("disabled")
            
            if is_disabled:
                logger.error("그룹 지정 버튼이 비활성화되어 있습니다. 먼저 상품을 선택해주세요.")
                return False
                    
            # 그룹 지정 버튼 클릭
            button_element.click()
            time.sleep(DELAY_SHORT)
            
            # 모달창이 열렸는지 확인
            modal_selector = "//div[contains(@class, 'ant-modal')]//span[contains(text(), '상품 그룹핑') or contains(text(), '그룹 지정')]"
            try:
                WebDriverWait(self.driver, timeout).until(
                    EC.visibility_of_element_located((By.XPATH, modal_selector))
                )
                logger.info("그룹 이동 모달창이 열렸습니다.")
                return True
            except (TimeoutException, NoSuchElementException):
                logger.error("그룹 이동 모달창을 열지 못했습니다.")
                return False
                
        except Exception as e:
            logger.error(f"그룹 이동 모달창 열기 오류: {e}")
            return False
    
    def select_group_in_modal(self, group_name, timeout=2):
        """
        그룹 이동 모달창에서 특정 그룹 선택
        
        Args:
            group_name: 선택할 그룹 이름
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"그룹 이동 모달창에서 '{group_name}' 그룹 선택")
            
            # 그룹 라디오 버튼 선택자
            radio_selector = f"//div[contains(@class, 'ant-modal-body')]//label[contains(@class, 'ant-radio-wrapper')][./span[contains(text(), '{group_name}')]]"
            
            try:
                radio_element = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((By.XPATH, radio_selector))
                )
                radio_element.click()
                time.sleep(DELAY_SHORT)
                logger.info(f"'{group_name}' 그룹이 선택되었습니다.")
                
                # 확인 버튼 클릭
                confirm_button_selector = "//div[contains(@class, 'ant-modal-footer')]//button[contains(@class, 'ant-btn-primary')][.//span[text()='확인']]"
                confirm_button = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((By.XPATH, confirm_button_selector))
                )
                confirm_button.click()
                logger.info("확인 버튼 클릭 완료")
                
                # 모달창이 닫혔는지 확인
                modal_selector = "//div[contains(@class, 'ant-modal')]//span[contains(text(), '상품 그룹핑') or contains(text(), '그룹 지정')]"
                try:
                    # 모달창이 사라질 때까지 대기 (최대 10초)
                    WebDriverWait(self.driver, 10).until(
                        EC.invisibility_of_element_located((By.XPATH, modal_selector))
                    )
                    logger.info("그룹 이동 모달창이 정상적으로 닫혔습니다.")
                    logger.info("그룹 이동 완료")
                    return True
                except TimeoutException:
                    logger.error("모달창이 닫히지 않았습니다. 그룹 이동이 실패했을 수 있습니다.")
                    return False
                
            except (TimeoutException, NoSuchElementException):
                logger.error(f"'{group_name}' 그룹을 찾을 수 없습니다.")
                # 그룹을 찾지 못한 경우에도 모달창이 열려있을 수 있으므로 닫기 시도
                self._close_modal_if_open()
                return False
                
        except Exception as e:
            logger.error(f"그룹 이동 모달창에서 그룹 선택 오류: {e}")
            # 오류 발생 시에도 모달창이 열려있을 수 있으므로 닫기 시도
            self._close_modal_if_open()
            return False
    
    def _close_modal_if_open(self, timeout=5):
        """
        모달창이 열려있으면 강제로 닫기
        
        Args:
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            # 모달창이 열려있는지 확인
            modal_selector = "//div[contains(@class, 'ant-modal')]//span[contains(text(), '상품 그룹핑') or contains(text(), '그룹 지정')]"
            modal_element = self.driver.find_element(By.XPATH, modal_selector)
            
            if modal_element.is_displayed():
                logger.info("열려있는 모달창을 강제로 닫습니다.")
                
                # 취소 버튼 또는 X 버튼 클릭 시도
                close_selectors = [
                    "//div[contains(@class, 'ant-modal-footer')]//button[contains(@class, 'ant-btn-default')][.//span[text()='취소']]",
                    "//div[contains(@class, 'ant-modal-header')]//button[contains(@class, 'ant-modal-close')]",
                    "//div[contains(@class, 'ant-modal')]//button[@aria-label='Close']"
                ]
                
                for close_selector in close_selectors:
                    try:
                        close_button = WebDriverWait(self.driver, 2).until(
                            EC.element_to_be_clickable((By.XPATH, close_selector))
                        )
                        close_button.click()
                        time.sleep(1)
                        
                        # 모달창이 닫혔는지 확인
                        try:
                            WebDriverWait(self.driver, 3).until(
                                EC.invisibility_of_element_located((By.XPATH, modal_selector))
                            )
                            logger.info("모달창이 성공적으로 닫혔습니다.")
                            return True
                        except TimeoutException:
                            continue
                            
                    except (TimeoutException, NoSuchElementException):
                        continue
                
                # 버튼 클릭으로 닫지 못한 경우 ESC 키 시도
                logger.info("버튼 클릭으로 모달창을 닫지 못했습니다. ESC 키를 시도합니다.")
                try:
                    from selenium.webdriver.common.keys import Keys
                    # body 요소에 ESC 키 전송
                    body = self.driver.find_element(By.TAG_NAME, "body")
                    body.send_keys(Keys.ESCAPE)
                    time.sleep(1)
                    
                    # 모달창이 닫혔는지 확인
                    try:
                        WebDriverWait(self.driver, 3).until(
                            EC.invisibility_of_element_located((By.XPATH, modal_selector))
                        )
                        logger.info("ESC 키로 모달창이 성공적으로 닫혔습니다.")
                        return True
                    except TimeoutException:
                        logger.error("ESC 키로도 모달창을 닫지 못했습니다.")
                        return False
                        
                except Exception as e:
                    logger.error(f"ESC 키 전송 오류: {e}")
                    return False
            else:
                logger.info("모달창이 이미 닫혀있습니다.")
                return True
                
        except NoSuchElementException:
            logger.info("모달창이 존재하지 않습니다.")
            return True
        except Exception as e:
            logger.error(f"모달창 닫기 오류: {e}")
            return False
    
    def move_products_to_group(self, group_name, items_per_page=20, timeout=2):
        """
        선택된 상품을 특정 그룹으로 이동
        - 상품 개수 설정
        - 전체 상품 선택
        - 그룹 이동 모달 열기
        - 그룹 선택 및 이동 확인
        
        Args:
            group_name: 이동할 그룹 이름
            items_per_page: 페이지당 표시할 상품 개수 (20 또는 50)
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"상품을 '{group_name}' 그룹으로 이동 시작")
            
            # 1. 상품 개수 설정
            if not self.select_items_per_page(items_per_page, timeout):
                logger.warning(f"{items_per_page}개씩 보기 설정 실패, 계속 진행합니다.")
            
            # 2. 전체 상품 선택
            if not self.select_all_products(timeout):
                logger.error("상품 전체 선택 실패, 그룹 이동을 중단합니다.")
                return False
            
            # 3. 그룹 이동 모달 열기
            if not self.open_group_assignment_modal(timeout):
                logger.error("그룹 이동 모달창 열기 실패, 그룹 이동을 중단합니다.")
                return False
            
            # 4. 그룹 선택 및 이동
            if not self.select_group_in_modal(group_name, timeout):
                logger.error(f"'{group_name}' 그룹 선택 실패, 그룹 이동을 중단합니다.")
                return False
            
            logger.info(f"상품이 '{group_name}' 그룹으로 성공적으로 이동되었습니다.")
            return True
            
        except Exception as e:
            logger.error(f"상품 그룹 이동 오류: {e}")
            return False
            
        except Exception as e:
            logger.error(f"그룹 검색 드롭박스 열기 오류: {e}")
            return False
    
    # =============================================================================
    # 드롭다운 메뉴에서 그룹 선택
    # =============================================================================
    
    def select_group_by_index(self, group_index, timeout=2):
        """
        열린 드롭다운 메뉴에서 인덱스로 그룹 선택
        (드롭다운 메뉴가 이미 열려있어야 함)
        
        Args:
            group_index: 선택할 그룹의 인덱스 (0부터 시작, 0은 '그룹없음')
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"드롭다운 메뉴에서 {group_index}번 그룹 선택")
            
            # 그룹 없음을 포함하여 인덱스 계산 (0은 '그룹없음')
            actual_index = group_index + 1
            
            # 드롭다운 메뉴 아이템 선택자
            selectors = [
                f"(//div[contains(@class, 'ant-select-dropdown')]//div[@class='ant-select-item-option-content'])[{actual_index}]",
                f"(//div[contains(@class, 'ant-select-item') and contains(@class, 'ant-select-item-option')])[{actual_index}]",
                # 대체 선택자
                f"(//div[@class='rc-virtual-list-holder-inner']//div[contains(@class, 'ant-select-item')])[{actual_index}]"
            ]
            
            # 드롭다운이 열린 후 스크롤을 위한 대기
            time.sleep(DELAY_SHORT)
            
            group_element = None
            for selector in selectors:
                try:
                    # 먼저 요소가 있는지 확인
                    group_elements = self.driver.find_elements(By.XPATH, selector.replace(f"[{actual_index}]", ""))
                    
                    # 인덱스가 범위를 벗어나는지 확인
                    if len(group_elements) <= group_index:
                        # 필요한 만큼 스크롤 다운
                        self._scroll_to_group(group_index)
                    
                    # 이제 해당 요소 선택
                    group_element = WebDriverWait(self.driver, timeout).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except (TimeoutException, NoSuchElementException, StaleElementReferenceException):
                    continue
                    
            if not group_element:
                logger.error(f"{group_index}번 그룹을 찾을 수 없습니다. 스크롤링이 필요하거나 잘못된 인덱스일 수 있습니다.")
                return False
                
            # 그룹 클릭
            group_element.click()
            time.sleep(DELAY_SHORT)
            logger.info(f"{group_index}번 그룹이 선택되었습니다.")
            return True
            
        except Exception as e:
            logger.error(f"그룹 선택 오류: {e}")
            return False
    
    def select_group_by_name(self, group_name, timeout=2):
        """
        열린 드롭다운 메뉴에서 이름으로 그룹 선택
        (드롭다운 메뉴가 이미 열려있어야 함)
        
        Args:
            group_name: 선택할 그룹의 이름 (예: "등록B", "완료D3")
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"드롭다운 메뉴에서 '{group_name}' 그룹 선택")
            
            # 그룹명으로 아이템 선택자
            selectors = [
                f"//div[contains(@class, 'ant-select-dropdown')]//div[@class='ant-select-item-option-content' and contains(text(), '{group_name}')]",
                f"//div[contains(@class, 'ant-select-item') and contains(@class, 'ant-select-item-option') and contains(., '{group_name}')]",
                # 대체 선택자
                f"//div[contains(@class, 'sc-dkmUuB') and text()='{group_name}']/ancestor::div[contains(@class, 'ant-select-item')]"
            ]
            
            # 드롭다운이 열린 후 스크롤 및 검색을 위한 대기
            time.sleep(DELAY_SHORT)
            
            # 검색 필드에 그룹명 입력 (검색을 지원하는 드롭다운인 경우)
            try:
                search_input = self.driver.find_element(By.CSS_SELECTOR, "input.ant-select-selection-search-input:not([readonly])")
                search_input.clear()
                search_input.send_keys(group_name)
                time.sleep(DELAY_SHORT)
                logger.info(f"검색 필드에 '{group_name}' 입력됨")
            except (NoSuchElementException, StaleElementReferenceException):
                logger.warning("검색 가능한 드롭다운이 아니거나 검색 필드를 찾을 수 없습니다. 스크롤로 찾습니다.")
                # 전체 목록을 스크롤하며 검색
                self._scroll_and_search_for_group(group_name)
            
            group_element = None
            for selector in selectors:
                try:
                    group_element = WebDriverWait(self.driver, timeout).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except (TimeoutException, NoSuchElementException, StaleElementReferenceException):
                    continue
                    
            if not group_element:
                logger.error(f"'{group_name}' 그룹을 찾을 수 없습니다.")
                return False
                
            # 그룹 클릭
            group_element.click()
            time.sleep(DELAY_SHORT)
            logger.info(f"'{group_name}' 그룹이 선택되었습니다.")
            return True
            
        except Exception as e:
            logger.error(f"그룹 선택 오류: {e}")
            return False
    
    # =============================================================================
    # 편의 메서드: 드롭박스 열고 그룹 선택 (원스텝)
    # =============================================================================
    
    def select_product_group_by_index(self, group_index, item_index=0):
        """
        상품 아이템의 드롭박스를 열고 인덱스로 그룹 선택 (원스텝)
        
        Args:
            group_index: 선택할 그룹의 인덱스 (0부터 시작, 0은 '그룹없음')
            item_index: 여러 상품이 있을 경우 상품 인덱스 (기본값: 0, 첫 번째 상품)
            
        Returns:
            bool: 성공 여부
        """
        if not self.open_product_item_dropdown(item_index):
            return False
        return self.select_group_by_index(group_index)
    
    def select_product_group_by_name(self, group_name, item_index=0):
        """
        상품 아이템의 드롭박스를 열고 이름으로 그룹 선택 (원스텝)
        
        Args:
            group_name: 선택할 그룹의 이름 (예: "등록B", "완료D3")
            item_index: 여러 상품이 있을 경우 상품 인덱스 (기본값: 0, 첫 번째 상품)
            
        Returns:
            bool: 성공 여부
        """
        if not self.open_product_item_dropdown(item_index):
            return False
        return self.select_group_by_name(group_name)
    
    def select_search_group_by_index(self, group_index):
        """
        그룹 검색용 드롭박스를 열고 인덱스로 그룹 선택 (원스텝)
        
        Args:
            group_index: 선택할 그룹의 인덱스 (0부터 시작, 0은 '전체')
            
        Returns:
            bool: 성공 여부
        """
        if not self.open_group_search_dropdown():
            return False
        return self.select_group_by_index(group_index)
    
    def select_search_group_by_name(self, group_name):
        """
        그룹 검색용 드롭박스를 열고 이름으로 그룹 선택 (원스텝)
        
        Args:
            group_name: 선택할 그룹의 이름 (예: "등록B", "완료D3")
            
        Returns:
            bool: 성공 여부
        """
        if not self.open_group_search_dropdown():
            return False
        return self.select_group_by_name(group_name)
    
    def select_search_group_by_name_specific(self, group_name, timeout=30):
        """
        상품검색용 드롭박스에서만 그룹을 선택하는 전용 메서드
        개별상품용 드롭박스와 명확히 구분하여 선택
        
        Args:
            group_name: 선택할 그룹의 이름 (예: "신규수집")
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"상품검색용 드롭박스에서 '{group_name}' 그룹 선택")
            
            # 1. 상품검색용 드롭박스가 열려있는지 확인
            search_dropdown_open = False
            try:
                # 상품검색용 드롭박스가 열린 상태인지 확인
                search_dropdown_selectors = [
                    "//div[contains(@class, 'ant-select-dropdown') and not(contains(@style, 'display: none'))]//div[contains(@class, 'ant-select-item-option-content')]",
                    "//div[contains(@class, 'ant-select-dropdown') and contains(@class, 'ant-select-dropdown-placement-bottomLeft')]//div[contains(@class, 'ant-select-item')]"
                ]
                
                for selector in search_dropdown_selectors:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements:
                        search_dropdown_open = True
                        break
                        
            except Exception as e:
                logger.warning(f"드롭박스 상태 확인 중 오류: {e}")
                
            if not search_dropdown_open:
                logger.error("상품검색용 드롭박스가 열려있지 않습니다.")
                return False
                
            # 2. 검색 필드에 그룹명 입력 (상품검색용 드롭박스는 검색을 지원함)
            try:
                # 상품검색용 드롭박스의 검색 입력 필드 찾기
                search_input_selectors = [
                    "input.ant-select-selection-search-input:not([readonly])",
                    "//div[contains(@class, 'ant-select-dropdown')]//input[contains(@class, 'ant-select-selection-search-input')]",
                    "//input[contains(@class, 'ant-select-selection-search-input') and not(@readonly)]"
                ]
                
                search_input = None
                for selector in search_input_selectors:
                    try:
                        if selector.startswith('//'):
                            search_input = self.driver.find_element(By.XPATH, selector)
                        else:
                            search_input = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if search_input and search_input.is_displayed():
                            break
                    except:
                        continue
                        
                if search_input:
                    search_input.clear()
                    search_input.send_keys(group_name)
                    time.sleep(1)  # 검색 결과 로딩 대기
                    logger.info(f"상품검색용 드롭박스 검색 필드에 '{group_name}' 입력됨")
                else:
                    logger.warning("상품검색용 드롭박스의 검색 필드를 찾을 수 없습니다.")
                    
            except Exception as e:
                logger.warning(f"검색 필드 입력 중 오류: {e}")
                
            # 3. 상품검색용 드롭박스에서만 그룹 선택 (더 구체적인 선택자 사용)
            search_specific_selectors = [
                # 상품검색용 드롭박스의 특정 구조를 타겟팅
                f"//div[contains(@class, 'ant-select-dropdown') and not(ancestor::tr)]//div[contains(@class, 'ant-select-item-option-content') and contains(text(), '{group_name}')]",
                f"//div[contains(@class, 'ant-select-dropdown') and contains(@class, 'ant-select-dropdown-placement-bottomLeft')]//div[contains(@class, 'ant-select-item-option-content') and contains(text(), '{group_name}')]",
                # 페이지 상단의 드롭박스만 타겟팅 (개별 상품 행이 아닌)
                f"//div[contains(@class, 'ant-select-dropdown')]//div[contains(@class, 'ant-select-item') and contains(@class, 'ant-select-item-option') and contains(., '{group_name}') and not(ancestor::tr)]",
                # 백업 선택자
                f"//div[contains(@class, 'ant-select-dropdown')]//div[@class='ant-select-item-option-content' and text()='{group_name}']"
            ]
            
            group_element = None
            for selector in search_specific_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    # 여러 요소가 있을 경우 첫 번째 요소 선택 (상품검색용이 먼저 나타남)
                    if elements:
                        group_element = elements[0]
                        logger.info(f"상품검색용 드롭박스에서 '{group_name}' 그룹 요소를 찾았습니다. (선택자: {selector})")
                        break
                except Exception as e:
                    logger.debug(f"선택자 {selector} 시도 중 오류: {e}")
                    continue
                    
            if not group_element:
                logger.error(f"상품검색용 드롭박스에서 '{group_name}' 그룹을 찾을 수 없습니다.")
                return False
                
            # 4. 그룹 클릭
            try:
                # 요소가 보이는지 확인하고 스크롤
                self.driver.execute_script("arguments[0].scrollIntoView(true);", group_element)
                time.sleep(0.5)
                
                # 클릭 시도
                group_element.click()
                time.sleep(1)
                logger.info(f"상품검색용 드롭박스에서 '{group_name}' 그룹이 선택되었습니다.")
                return True
                
            except Exception as e:
                logger.error(f"그룹 클릭 중 오류: {e}")
                # JavaScript 클릭 시도
                try:
                    self.driver.execute_script("arguments[0].click();", group_element)
                    time.sleep(1)
                    logger.info(f"JavaScript로 '{group_name}' 그룹이 선택되었습니다.")
                    return True
                except Exception as js_e:
                    logger.error(f"JavaScript 클릭도 실패: {js_e}")
                    return False
                
        except Exception as e:
            logger.error(f"상품검색용 그룹 선택 오류: {e}")
            return False
    
    # =============================================================================
    # 내부 도우미 메서드
    # =============================================================================
    
    def _scroll_to_group(self, target_index, max_scrolls=10):
        """
        드롭다운 내에서 스크롤하여 원하는 인덱스의 그룹을 보이게 함
        
        Args:
            target_index: 찾을 그룹 인덱스
            max_scrolls: 최대 스크롤 횟수
        """
        try:
            # 드롭다운 컨테이너 찾기
            scroller_selectors = [
                "//div[contains(@class, 'rc-virtual-list-holder')]",
                "//div[contains(@class, 'ant-select-dropdown')]//div[contains(@class, 'ant-select-item-empty')]/..",
                "//div[contains(@class, 'ant-select-dropdown')]"
            ]
            
            scroller = None
            for selector in scroller_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements:
                        scroller = elements[0]
                        break
                except Exception:
                    continue
                    
            if not scroller:
                logger.warning("스크롤 컨테이너를 찾을 수 없습니다.")
                return
                
            # 대략적으로 필요한 스크롤 계산
            # 한 화면에 보통 7개 정도 표시된다고 가정
            items_per_view = 7
            scroll_needed = target_index // items_per_view
            
            # 스크롤 실행
            for i in range(min(scroll_needed, max_scrolls)):
                self.driver.execute_script("arguments[0].scrollTop += arguments[0].clientHeight", scroller)
                time.sleep(0.2)  # 스크롤 후 약간의 지연
                
        except Exception as e:
            logger.warning(f"스크롤 중 오류 발생: {e}")
    
    def _scroll_and_search_for_group(self, group_name, max_scrolls=20):
        """
        드롭다운 내에서 스크롤하며 특정 이름의 그룹을 검색
        
        Args:
            group_name: 검색할 그룹 이름
            max_scrolls: 최대 스크롤 횟수
        """
        try:
            # 드롭다운 컨테이너 찾기
            scroller_selectors = [
                "//div[contains(@class, 'rc-virtual-list-holder')]",
                "//div[contains(@class, 'ant-select-dropdown')]//div[contains(@class, 'ant-select-item-empty')]/..",
                "//div[contains(@class, 'ant-select-dropdown')]"
            ]
            
            scroller = None
            for selector in scroller_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements:
                        scroller = elements[0]
                        break
                except Exception:
                    continue
                    
            if not scroller:
                logger.warning("스크롤 컨테이너를 찾을 수 없습니다.")
                return
                
            # 그룹 이름 검색 선택자
            group_selectors = [
                f"//div[contains(@class, 'ant-select-dropdown')]//div[@class='ant-select-item-option-content' and contains(text(), '{group_name}')]",
                f"//div[contains(@class, 'ant-select-item') and contains(@class, 'ant-select-item-option') and contains(., '{group_name}')]",
                f"//div[contains(@class, 'sc-dkmUuB') and text()='{group_name}']/ancestor::div[contains(@class, 'ant-select-item')]"
            ]
            
            # 스크롤하며 검색
            for i in range(max_scrolls):
                # 현재 화면에서 그룹 이름 검색
                for selector in group_selectors:
                    if self.driver.find_elements(By.XPATH, selector):
                        logger.info(f"'{group_name}' 그룹을 찾았습니다.")
                        return True
                
                # 스크롤 다운
                self.driver.execute_script("arguments[0].scrollTop += arguments[0].clientHeight", scroller)
                time.sleep(0.2)  # 스크롤 후 약간의 지연
                
            logger.warning(f"최대 스크롤 횟수({max_scrolls})에 도달했으나 '{group_name}' 그룹을 찾지 못했습니다.")
            return False
                
        except Exception as e:
            logger.warning(f"스크롤 검색 중 오류 발생: {e}")
            return False


    # =============================================================================
    # 그룹상품관리 화면의 라디오 버튼 그룹 선택
    # =============================================================================
    
    def select_group_in_management_screen(self, group_name, timeout=2):
        """
        그룹상품관리 화면에서 라디오 버튼으로 그룹 선택
        
        Args:
            group_name: 선택할 그룹의 이름 (예: "등록B", "완료D3") 또는 "전체"
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"그룹상품관리 화면에서 '{group_name}' 그룹 선택")
            
            # 라디오 버튼 선택자
            selectors = [
                # 그룹명으로 바로 선택
                f"//div[contains(@class, 'ant-radio-group')]//span[text()='{group_name}']/preceding-sibling::span",
                # 대체 선택자 1
                f"//label[contains(@class, 'ant-radio-wrapper')]//span[contains(text(), '{group_name}')]/preceding-sibling::span[contains(@class, 'ant-radio')]",
                # 대체 선택자 2
                f"//label[contains(@class, 'ant-radio-wrapper')]//span[text()='{group_name}']"
            ]
            
            group_element = None
            for selector in selectors:
                try:
                    group_element = WebDriverWait(self.driver, timeout).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except (TimeoutException, NoSuchElementException, StaleElementReferenceException):
                    continue
                    
            if not group_element:
                logger.error(f"'{group_name}' 그룹을 찾을 수 없습니다.")
                return False
                
            # 그룹 클릭
            group_element.click()
            time.sleep(DELAY_SHORT)
            logger.info(f"'{group_name}' 그룹이 선택되었습니다.")
            return True
            
        except Exception as e:
            logger.error(f"그룹상품관리 화면 그룹 선택 오류: {e}")
            return False
    
    def select_group_in_management_by_index(self, index, timeout=2):
        """
        그룹상품관리 화면에서 인덱스로 그룹 선택
        
        Args:
            index: 선택할 그룹의 인덱스 (0부터 시작, 0은 '전체')
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"그룹상품관리 화면에서 {index}번 그룹 선택")
            
            # 라디오 버튼 인덱스 선택자
            selectors = [
                f"(//div[contains(@class, 'ant-radio-group')]//label[contains(@class, 'ant-radio-wrapper')])[{index + 1}]",
                f"(//div[contains(@class, 'ant-radio-group')]//span[contains(@class, 'ant-radio')])[{index + 1}]"
            ]
            
            group_element = None
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, 
                                         selector.replace(f"[{index + 1}]", ""))
                    
                    # 인덱스가 범위를 벗어나는지 확인
                    if len(elements) <= index:
                        logger.warning(f"유효하지 않은 그룹 인덱스: {index}, 최대 값: {len(elements) - 1}")
                        return False
                    
                    group_element = WebDriverWait(self.driver, timeout).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except (TimeoutException, NoSuchElementException, StaleElementReferenceException):
                    continue
                    
            if not group_element:
                logger.error(f"{index}번 그룹을 찾을 수 없습니다.")
                return False
                
            # 그룹 클릭
            group_element.click()
            time.sleep(DELAY_SHORT)
            logger.info(f"{index}번 그룹이 선택되었습니다.")
            return True
            
        except Exception as e:
            logger.error(f"그룹상품관리 화면 그룹 인덱스 선택 오류: {e}")
            return False
    
    def toggle_group_product_view(self, enable=True, timeout=2):
        """
        그룹상품 보기 토글 스위치 제어
        
        Args:
            enable: True면 그룹상품 보기 활성화, False면 비활성화
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            # 현재 상태 확인
            switch_selectors = [
                "//span[contains(text(), '그룹상품 보기')]/following::button[contains(@class, 'ant-switch')]",
                "//button[contains(@class, 'ant-switch') and @role='switch']"
            ]
            
            switch_element = None
            for selector in switch_selectors:
                try:
                    switch_element = WebDriverWait(self.driver, timeout).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    break
                except (TimeoutException, NoSuchElementException):
                    continue
                    
            if not switch_element:
                logger.error("그룹상품 보기 토글 스위치를 찾을 수 없습니다.")
                return False
                
            # 현재 상태 확인
            is_checked = "ant-switch-checked" in switch_element.get_attribute("class")
            
            # 원하는 상태와 현재 상태가 다를 때만 클릭
            if enable != is_checked:
                logger.info(f"그룹상품 보기 토글 {'활성화' if enable else '비활성화'}로 변경")
                switch_element.click()
                time.sleep(DELAY_SHORT)
            else:
                logger.info(f"그룹상품 보기 토글이 이미 {'활성화' if enable else '비활성화'} 상태입니다.")
                
            return True
            
        except Exception as e:
            logger.error(f"그룹상품 보기 토글 오류: {e}")
            return False
    
    def reset_scroll_position(self, delay=DELAY_SHORT):
        """
        스크롤 위치를 최상단으로 초기화
        
        Args:
            delay: 스크롤 후 대기 시간
            
        Returns:
            bool: 성공 여부
        """
        try:
            # JavaScript를 사용하여 스크롤 위치를 최상단으로 이동
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(delay)  # 스크롤 이동 대기
            logger.info("스크롤 위치를 최상단으로 초기화했습니다")
            return True
        except Exception as e:
            logger.error(f"스크롤 위치 초기화 오류: {e}")
            return False
            
    def click_group_management_button(self, timeout=2):
        """
        그룹 관리하기 버튼 클릭
        
        Args:
            timeout: 최대 대기 시간(초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("그룹 관리하기 버튼 클릭")
            
            # 그룹 관리하기 버튼 선택자
            selectors = [
                "//span[text()='그룹 관리하기']",
                "//button[contains(@class, 'ant-btn-primary')]/span[text()='그룹 관리하기']",
                "//button[contains(@class, 'ant-btn-primary')]"
            ]
            
            button_element = None
            for selector in selectors:
                try:
                    button_element = WebDriverWait(self.driver, timeout).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except (TimeoutException, NoSuchElementException):
                    continue
                    
            if not button_element:
                logger.error("그룹 관리하기 버튼을 찾을 수 없습니다.")
                return False
                
            # 버튼 클릭
            button_element.click()
            time.sleep(DELAY_MEDIUM)  # 그룹 관리 팝업이 뿐려질 때까지 조금 더 긴 대기
            logger.info("그룹 관리하기 버튼이 클릭되었습니다.")
            return True
            
        except Exception as e:
            logger.error(f"그룹 관리하기 버튼 클릭 오류: {e}")
            return False


# 싱글톤 인스턴스 생성을 위한 함수
def get_dropdown_helper(driver=None):
    """
    드롭다운 및 그룹 선택 헬퍼 인스턴스 반환
    
    Args:
        driver: 셀레니움 웹드라이버 (선택 사항)
        
    Returns:
        PercentyDropdown: 드롭다운 및 그룹 선택 헬퍼 인스턴스
    """
    if not hasattr(get_dropdown_helper, '_instance') or get_dropdown_helper._instance is None:
        get_dropdown_helper._instance = PercentyDropdown(driver)
    elif driver is not None:
        get_dropdown_helper._instance.driver = driver
    
    return get_dropdown_helper._instance


# 사용 예시
if __name__ == "__main__":
    # 기본 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("퍼센티 드롭다운 및 그룹 선택 유틸리티를 실행하려면 드라이버가 필요합니다.")
    print("percenty_step1.py 또는 percenty_step2.py에서 다음과 같이 사용하세요:")
    print("from dropdown_utils import get_dropdown_helper")
    print("dropdown = get_dropdown_helper(driver)")
    print("# 드롭다운 그룹 선택")
    print("dropdown.select_product_group_by_name('등록B')")
    print("# 그룹상품관리 화면에서 그룹 선택")
    print("dropdown.select_group_in_management_screen('완료D3')")
    print("# 또는 인덱스로 선택 (0은 전체)")
    print("dropdown.select_group_in_management_by_index(5)  # 5번째 그룹 선택")


# get_dropdown_manager를 get_dropdown_helper의 별칭으로 추가 (이전 코드와의 호환성 유지)
def get_dropdown_manager(driver=None):
    """
    get_dropdown_helper의 별칭 함수 - 이전 코드와의 호환성을 위해 제공
    
    Args:
        driver: 셀레니움 웹드라이버 (선택 사항)
        
    Returns:
        PercentyDropdown: 드롭다운 및 그룹 선택 헬퍼 인스턴스
    """
    return get_dropdown_helper(driver)
