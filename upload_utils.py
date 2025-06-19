# -*- coding: utf-8 -*-
"""
업로드 관련 유틸리티 함수들

이 모듈은 상품 업로드, 일괄번역, 삭제 등의 기능을 제공합니다.
"""

import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)

class UploadUtils:
    """
    업로드 관련 유틸리티 클래스
    """
    
    def __init__(self, driver):
        """
        초기화
        
        Args:
            driver: Selenium WebDriver 인스턴스
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
    
    def select_all_products(self) -> bool:
        """
        모든 상품 선택 체크박스 클릭
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("모든 상품 선택 체크박스 클릭 시도")
            
            # 체크박스 선택자들 (우선순위 순)
            selectors = [
                "input.ant-checkbox-input[type='checkbox']",
                ".ant-checkbox-input",
                "input[type='checkbox']"
            ]
            
            for selector in selectors:
                try:
                    checkbox = self.wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    checkbox.click()
                    logger.info(f"체크박스 클릭 성공: {selector}")
                    time.sleep(0.5)
                    return True
                except TimeoutException:
                    continue
            
            logger.error("모든 상품 선택 체크박스를 찾을 수 없습니다")
            return False
            
        except Exception as e:
            logger.error(f"상품 선택 중 오류: {e}")
            return False
    
    def click_upload_button(self) -> bool:
        """
        업로드 버튼 클릭
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("업로드 버튼 클릭 시도")
            
            # 업로드 버튼 선택자들 (XPath 우선 사용)
            selectors = [
                "//button[.//span[text()='업로드']]",
                "//button[contains(text(), '업로드')]",
                "//button[.//span[contains(text(), '업로드')]]",
                "button.ant-btn"
            ]
            
            for selector in selectors:
                try:
                    if selector.startswith('//'):
                        # XPath 선택자
                        button = self.wait.until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    else:
                        # CSS 선택자
                        button = self.wait.until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    
                    button.click()
                    logger.info(f"업로드 버튼 클릭 성공: {selector}")
                    time.sleep(1)
                    return True
                except TimeoutException:
                    continue
            
            logger.error("업로드 버튼을 찾을 수 없습니다")
            return False
            
        except Exception as e:
            logger.error(f"업로드 버튼 클릭 중 오류: {e}")
            return False
    
    def click_batch_translate_button(self) -> bool:
        """
        일괄 번역 버튼 클릭
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("일괄 번역 버튼 클릭 시도")
            
            # 일괄 번역 버튼 선택자들 (XPath 우선 사용)
            selectors = [
                "//button[.//span[text()='일괄 번역']]",
                "//button[contains(text(), '일괄 번역')]",
                "//button[.//span[contains(text(), '일괄 번역')]]",
                "button.ant-btn"
            ]
            
            for selector in selectors:
                try:
                    if selector.startswith('//'):
                        # XPath 선택자
                        button = self.wait.until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    else:
                        # CSS 선택자
                        button = self.wait.until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    
                    button.click()
                    logger.info(f"일괄 번역 버튼 클릭 성공: {selector}")
                    time.sleep(1)
                    return True
                except TimeoutException:
                    continue
            
            logger.error("일괄 번역 버튼을 찾을 수 없습니다")
            return False
            
        except Exception as e:
            logger.error(f"일괄 번역 버튼 클릭 중 오류: {e}")
            return False
    
    def click_delete_button(self) -> bool:
        """
        삭제 버튼 클릭
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("삭제 버튼 클릭 시도")
            
            # 삭제 버튼 선택자들 (XPath 우선 사용)
            selectors = [
                "//button[.//span[text()='삭제']]",
                "//button[contains(text(), '삭제')]",
                "//button[.//span[contains(text(), '삭제')]]",
                "//button[@style and contains(@style, 'color: rgb(255, 77, 79)')][.//span[contains(text(), '삭제')]]",
                "button.ant-btn"
            ]
            
            for selector in selectors:
                try:
                    if selector.startswith('//'):
                        # XPath 선택자
                        button = self.wait.until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    else:
                        # CSS 선택자
                        button = self.wait.until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    
                    button.click()
                    logger.info(f"삭제 버튼 클릭 성공: {selector}")
                    time.sleep(1)
                    return True
                except TimeoutException:
                    continue
            
            logger.error("삭제 버튼을 찾을 수 없습니다")
            return False
            
        except Exception as e:
            logger.error(f"삭제 버튼 클릭 중 오류: {e}")
            return False
    
    def click_batch_edit_button(self) -> bool:
        """
        일괄 편집 버튼 클릭
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("일괄 편집 버튼 클릭 시도")
            
            # 일괄 편집 버튼 선택자들 (XPath 우선 사용)
            selectors = [
                "//button[.//span[text()='일괄 편집']]",
                "//button[contains(text(), '일괄 편집')]",
                "//button[.//span[contains(text(), '일괄 편집')]]",
                "button.ant-btn"
            ]
            
            for selector in selectors:
                try:
                    if selector.startswith('//'):
                        # XPath 선택자
                        button = self.wait.until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    else:
                        # CSS 선택자
                        button = self.wait.until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    
                    button.click()
                    logger.info(f"일괄 편집 버튼 클릭 성공: {selector}")
                    time.sleep(1)
                    return True
                except TimeoutException:
                    continue
            
            logger.error("일괄 편집 버튼을 찾을 수 없습니다")
            return False
            
        except Exception as e:
            logger.error(f"일괄 편집 버튼 클릭 중 오류: {e}")
            return False
    
    def get_selected_product_count(self) -> int:
        """
        선택된 상품 개수 확인
        
        Returns:
            int: 선택된 상품 개수 (확인 실패 시 0)
        """
        try:
            # 선택된 상품 개수 텍스트 찾기 (XPath 우선 사용)
            selectors = [
                "//span[contains(text(), '선택')]",
                "//span[contains(text(), '개 선택')]",
                ".ant-checkbox-wrapper span",
                "span"
            ]
            
            for selector in selectors:
                try:
                    if selector.startswith('//'):
                        # XPath 선택자
                        element = self.driver.find_element(By.XPATH, selector)
                    else:
                        # CSS 선택자 (contains는 XPath에서만 지원되므로 다른 방법 사용)
                        elements = self.driver.find_elements(By.CSS_SELECTOR, "span")
                        element = None
                        for elem in elements:
                            if "선택" in elem.text:
                                element = elem
                                break
                        if not element:
                            continue
                    
                    text = element.text
                    logger.info(f"선택된 상품 텍스트: {text}")
                    
                    # 숫자 추출 (예: "선택 20개 상품" -> 20)
                    import re
                    numbers = re.findall(r'\d+', text)
                    if numbers:
                        count = int(numbers[0])
                        logger.info(f"선택된 상품 개수: {count}개")
                        return count
                        
                except (NoSuchElementException, ValueError):
                    continue
            
            logger.warning("선택된 상품 개수를 확인할 수 없습니다")
            return 0
            
        except Exception as e:
            logger.error(f"선택된 상품 개수 확인 중 오류: {e}")
            return 0
    
    def perform_upload_workflow(self) -> bool:
        """
        업로드 워크플로우 실행 (선택 + 업로드)
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("업로드 워크플로우 시작")
            
            # 1. 모든 상품 선택
            if not self.select_all_products():
                logger.error("상품 선택 실패")
                return False
            
            # 2. 선택된 상품 개수 확인
            count = self.get_selected_product_count()
            if count > 0:
                logger.info(f"{count}개 상품이 선택되었습니다")
            
            # 3. 업로드 버튼 클릭
            if not self.click_upload_button():
                logger.error("업로드 버튼 클릭 실패")
                return False
            
            logger.info("업로드 워크플로우 완료")
            return True
            
        except Exception as e:
            logger.error(f"업로드 워크플로우 중 오류: {e}")
            return False
    
    def perform_batch_translate_workflow(self) -> bool:
        """
        일괄 번역 워크플로우 실행 (선택 + 일괄번역)
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("일괄 번역 워크플로우 시작")
            
            # 1. 모든 상품 선택
            if not self.select_all_products():
                logger.error("상품 선택 실패")
                return False
            
            # 2. 선택된 상품 개수 확인
            count = self.get_selected_product_count()
            if count > 0:
                logger.info(f"{count}개 상품이 선택되었습니다")
            
            # 3. 일괄 번역 버튼 클릭
            if not self.click_batch_translate_button():
                logger.error("일괄 번역 버튼 클릭 실패")
                return False
            
            logger.info("일괄 번역 워크플로우 완료")
            return True
            
        except Exception as e:
            logger.error(f"일괄 번역 워크플로우 중 오류: {e}")
            return False
    
    def perform_delete_workflow(self) -> bool:
        """
        삭제 워크플로우 실행 (선택 + 삭제)
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("삭제 워크플로우 시작")
            
            # 1. 모든 상품 선택
            if not self.select_all_products():
                logger.error("상품 선택 실패")
                return False
            
            # 2. 선택된 상품 개수 확인
            count = self.get_selected_product_count()
            if count > 0:
                logger.info(f"{count}개 상품이 선택되었습니다")
            
            # 3. 삭제 버튼 클릭
            if not self.click_delete_button():
                logger.error("삭제 버튼 클릭 실패")
                return False
            
            logger.info("삭제 워크플로우 완료")
            return True
            
        except Exception as e:
            logger.error(f"삭제 워크플로우 중 오류: {e}")
            return False
    
    def handle_upload_modal(self, markets_to_select=None) -> bool:
        """
        업로드 모달창 처리
        
        Args:
            markets_to_select (list, optional): 선택할 마켓 ID 리스트
                                              None이면 기본 선택된 마켓 사용
                                              예: ['cp', 'ss', 'esm', 'est', 'est_global', 'lotteon', 'ip', 'wmp', 'kakao']
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("업로드 모달창 처리 시작")
            
            # 모달창이 열릴 때까지 대기
            modal_selectors = [
                ".ant-modal-content",
                "div[class*='ant-modal-content']"
            ]
            
            modal_found = False
            for selector in modal_selectors:
                try:
                    self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    logger.info(f"업로드 모달창 감지됨: {selector}")
                    modal_found = True
                    break
                except TimeoutException:
                    continue
            
            if not modal_found:
                logger.error("업로드 모달창을 찾을 수 없습니다")
                return False
            
            time.sleep(1)  # 모달창 로딩 대기
            
            # 마켓 선택 처리
            if markets_to_select is not None:
                if not self._select_markets_in_modal(markets_to_select):
                    logger.warning("마켓 선택에 실패했지만 계속 진행합니다")
            
            # '선택 상품 일괄 업로드' 버튼 클릭
            if not self.click_modal_upload_button():
                logger.error("모달 업로드 버튼 클릭 실패")
                return False
            
            logger.info("업로드 모달창 처리 완료")
            return True
            
        except Exception as e:
            logger.error(f"업로드 모달창 처리 중 오류: {e}")
            return False
    
    def click_modal_upload_button(self) -> bool:
        """
        모달창 내 '선택 상품 일괄 업로드' 버튼 클릭
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("모달 업로드 버튼 클릭 시도")
            
            # 모달 내 업로드 버튼 선택자들 (XPath 우선 사용)
            selectors = [
                "//div[contains(@class, 'ant-modal-content')]//button[.//span[text()='선택 상품 일괄 업로드']]",
                "//button[.//span[text()='선택 상품 일괄 업로드']]",
                "//div[contains(@class, 'ant-modal-content')]//button[.//span[contains(text(), '일괄 업로드')]]",
                "//button[.//span[contains(text(), '일괄 업로드')]]",
                ".ant-modal-content button.ant-btn-primary"
            ]
            
            for selector in selectors:
                try:
                    if selector.startswith('//'):
                        # XPath 선택자
                        button = self.wait.until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    else:
                        # CSS 선택자
                        button = self.wait.until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    
                    button.click()
                    logger.info(f"모달 업로드 버튼 클릭 성공: {selector}")
                    time.sleep(1)
                    return True
                except TimeoutException:
                    continue
            
            logger.error("모달 업로드 버튼을 찾을 수 없습니다")
            return False
            
        except Exception as e:
            logger.error(f"모달 업로드 버튼 클릭 중 오류: {e}")
            return False
    
    def _select_markets_in_modal(self, markets_to_select) -> bool:
        """
        모달창 내에서 특정 마켓들 선택
        
        Args:
            markets_to_select (list): 선택할 마켓 ID 리스트
                                    예: ['cp', 'ss', 'esm', 'est', 'est_global', 'lotteon', 'ip', 'wmp', 'kakao']
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"마켓 선택 시작: {markets_to_select}")
            
            success_count = 0
            
            for market_id in markets_to_select:
                try:
                    # 마켓별 체크박스 선택자들
                    selectors = [
                        f".ant-modal-content input#{market_id}.ant-checkbox-input",
                        f"input#{market_id}.ant-checkbox-input",
                        f"input[id='{market_id}'][type='checkbox']"
                    ]
                    
                    checkbox_found = False
                    for selector in selectors:
                        try:
                            checkbox = self.driver.find_element(By.CSS_SELECTOR, selector)
                            
                            # 체크박스가 이미 선택되어 있는지 확인
                            if not checkbox.is_selected():
                                # 체크박스의 부모 label 클릭 (더 안정적)
                                label = checkbox.find_element(By.XPATH, "./ancestor::label[1]")
                                label.click()
                                logger.info(f"마켓 {market_id} 선택됨")
                            else:
                                logger.info(f"마켓 {market_id}는 이미 선택되어 있음")
                            
                            success_count += 1
                            checkbox_found = True
                            time.sleep(0.3)
                            break
                            
                        except NoSuchElementException:
                            continue
                    
                    if not checkbox_found:
                        logger.warning(f"마켓 {market_id}의 체크박스를 찾을 수 없습니다")
                        
                except Exception as e:
                    logger.warning(f"마켓 {market_id} 선택 중 오류: {e}")
                    continue
            
            logger.info(f"마켓 선택 완료: {success_count}/{len(markets_to_select)}개 성공")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"마켓 선택 중 오류: {e}")
            return False
    
    def close_upload_modal(self) -> bool:
        """
        업로드 모달창 닫기
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("업로드 모달창 닫기 시도")
            
            # 모달 닫기 버튼 선택자들
            selectors = [
                ".ant-modal-content .ant-modal-close",
                ".ant-modal-close",
                "button[aria-label='Close']",
                "//button[@aria-label='Close']"
            ]
            
            for selector in selectors:
                try:
                    if selector.startswith('//'):
                        # XPath 선택자
                        close_button = self.wait.until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    else:
                        # CSS 선택자
                        close_button = self.wait.until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    
                    close_button.click()
                    logger.info(f"모달 닫기 버튼 클릭 성공: {selector}")
                    time.sleep(0.5)
                    return True
                except TimeoutException:
                    continue
            
            logger.error("모달 닫기 버튼을 찾을 수 없습니다")
            return False
            
        except Exception as e:
            logger.error(f"모달 닫기 중 오류: {e}")
            return False
    
    def perform_complete_upload_workflow(self, markets_to_select=None) -> bool:
        """
        완전한 업로드 워크플로우 실행 (선택 + 업로드 버튼 + 모달 처리)
        
        Args:
            markets_to_select (list, optional): 선택할 마켓 ID 리스트
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("완전한 업로드 워크플로우 시작")
            
            # 1. 기본 업로드 워크플로우 (상품 선택 + 업로드 버튼 클릭)
            if not self.perform_upload_workflow():
                logger.error("기본 업로드 워크플로우 실패")
                return False
            
            # 2. 업로드 모달창 처리
            if not self.handle_upload_modal(markets_to_select):
                logger.error("업로드 모달창 처리 실패")
                return False
            
            logger.info("완전한 업로드 워크플로우 완료")
            return True
            
        except Exception as e:
            logger.error(f"완전한 업로드 워크플로우 중 오류: {e}")
            return False
    
    def handle_delete_modal(self, delete_option=None) -> bool:
        """
        삭제 모달창 처리
        
        Args:
            delete_option (str, optional): 삭제 옵션 선택
                                         None이면 기본 선택된 옵션 사용
                                         예: "1. 퍼센티 및 모든 마켓에서 상품 삭제",
                                             "2. 퍼센티에서만 상품 삭제",
                                             "3. 선택한 마켓에서만 상품 삭제"
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("삭제 모달창 처리 시작")
            
            # 모달창이 열릴 때까지 대기
            modal_selectors = [
                ".ant-modal-content",
                "div[class*='ant-modal-content']"
            ]
            
            modal_found = False
            for selector in modal_selectors:
                try:
                    self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    logger.info(f"삭제 모달창 감지됨: {selector}")
                    modal_found = True
                    break
                except TimeoutException:
                    continue
            
            if not modal_found:
                logger.error("삭제 모달창을 찾을 수 없습니다")
                return False
            
            time.sleep(1)  # 모달창 로딩 대기
            
            # 삭제 옵션 선택 처리
            if delete_option is not None:
                if not self._select_delete_option_in_modal(delete_option):
                    logger.warning("삭제 옵션 선택에 실패했지만 계속 진행합니다")
            
            # '선택 상품 일괄 삭제' 버튼 클릭
            if not self.click_modal_delete_button():
                logger.error("모달 삭제 버튼 클릭 실패")
                return False
            
            logger.info("삭제 모달창 처리 완료")
            return True
            
        except Exception as e:
            logger.error(f"삭제 모달창 처리 중 오류: {e}")
            return False
    
    def click_modal_delete_button(self) -> bool:
        """
        모달창 내 '선택 상품 일괄 삭제' 버튼 클릭
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("모달 삭제 버튼 클릭 시도")
            
            # 모달 내 삭제 버튼 선택자들 (XPath 우선 사용)
            selectors = [
                "//div[contains(@class, 'ant-modal-content')]//button[.//span[text()='선택 상품 일괄 삭제']]",
                "//button[.//span[text()='선택 상품 일괄 삭제']]",
                "//div[contains(@class, 'ant-modal-content')]//button[.//span[contains(text(), '일괄 삭제')]]",
                "//button[.//span[contains(text(), '일괄 삭제')]]",
                "//div[contains(@class, 'ant-modal-content')]//button[contains(@class, 'ant-btn-dangerous')]",
                ".ant-modal-content button.ant-btn-dangerous"
            ]
            
            for selector in selectors:
                try:
                    if selector.startswith('//'):
                        # XPath 선택자
                        button = self.wait.until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    else:
                        # CSS 선택자
                        button = self.wait.until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    
                    button.click()
                    logger.info(f"모달 삭제 버튼 클릭 성공: {selector}")
                    time.sleep(1)
                    return True
                except TimeoutException:
                    continue
            
            logger.error("모달 삭제 버튼을 찾을 수 없습니다")
            return False
            
        except Exception as e:
            logger.error(f"모달 삭제 버튼 클릭 중 오류: {e}")
            return False
    
    def _select_delete_option_in_modal(self, delete_option) -> bool:
        """
        모달창 내에서 삭제 옵션 선택
        
        Args:
            delete_option (str): 선택할 삭제 옵션
                               예: "1. 퍼센티 및 모든 마켓에서 상품 삭제",
                                   "2. 퍼센티에서만 상품 삭제",
                                   "3. 선택한 마켓에서만 상품 삭제"
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"삭제 옵션 선택 시작: {delete_option}")
            
            # 드롭다운 선택자들
            dropdown_selectors = [
                ".ant-modal-content .ant-select",
                ".ant-select",
                "div[class*='ant-select']"
            ]
            
            dropdown_found = False
            dropdown_element = None
            
            for selector in dropdown_selectors:
                try:
                    dropdown_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    dropdown_found = True
                    logger.info(f"드롭다운 요소 찾음: {selector}")
                    break
                except NoSuchElementException:
                    continue
            
            if not dropdown_found:
                logger.error("삭제 옵션 드롭다운을 찾을 수 없습니다")
                return False
            
            # 드롭다운 클릭하여 옵션 목록 열기
            dropdown_element.click()
            time.sleep(0.5)
            
            # 옵션 선택 (XPath 우선 사용)
            option_selectors = [
                f"//div[contains(@class, 'ant-select-item')]//div[contains(text(), '{delete_option}')]",
                f"//div[contains(@class, 'ant-select-item')][contains(text(), '{delete_option}')]",
                f"//li[contains(text(), '{delete_option}')]",
                f"//div[contains(@class, 'ant-select-item')]//*[contains(text(), '{delete_option}')]"
            ]
            
            for selector in option_selectors:
                try:
                    if selector.startswith('//'):
                        # XPath 선택자
                        option = self.wait.until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    else:
                        # CSS 선택자
                        option = self.wait.until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    
                    option.click()
                    logger.info(f"삭제 옵션 선택 성공: {delete_option}")
                    time.sleep(0.5)
                    return True
                except TimeoutException:
                    continue
            
            logger.warning(f"삭제 옵션 '{delete_option}'을 찾을 수 없습니다")
            return False
            
        except Exception as e:
            logger.error(f"삭제 옵션 선택 중 오류: {e}")
            return False
    
    def close_delete_modal(self) -> bool:
        """
        삭제 모달창 닫기
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("삭제 모달창 닫기 시도")
            
            # 모달 닫기 버튼 선택자들
            selectors = [
                ".ant-modal-content .ant-modal-close",
                ".ant-modal-close",
                "button[aria-label='Close']",
                "//button[@aria-label='Close']"
            ]
            
            for selector in selectors:
                try:
                    if selector.startswith('//'):
                        # XPath 선택자
                        close_button = self.wait.until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    else:
                        # CSS 선택자
                        close_button = self.wait.until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    
                    close_button.click()
                    logger.info(f"삭제 모달 닫기 버튼 클릭 성공: {selector}")
                    time.sleep(0.5)
                    return True
                except TimeoutException:
                    continue
            
            logger.error("삭제 모달 닫기 버튼을 찾을 수 없습니다")
            return False
            
        except Exception as e:
            logger.error(f"삭제 모달 닫기 중 오류: {e}")
            return False
    
    def perform_complete_delete_workflow(self, delete_option=None) -> bool:
        """
        완전한 삭제 워크플로우 실행 (선택 + 삭제 버튼 + 모달 처리)
        
        Args:
            delete_option (str, optional): 삭제 옵션 선택
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("완전한 삭제 워크플로우 시작")
            
            # 1. 기본 삭제 워크플로우 (상품 선택 + 삭제 버튼 클릭)
            if not self.perform_delete_workflow():
                logger.error("기본 삭제 워크플로우 실패")
                return False
            
            # 2. 삭제 모달창 처리
            if not self.handle_delete_modal(delete_option):
                logger.error("삭제 모달창 처리 실패")
                return False
            
            logger.info("완전한 삭제 워크플로우 완료")
            return True
            
        except Exception as e:
            logger.error(f"완전한 삭제 워크플로우 중 오류: {e}")
            return False
    
    def handle_batch_translate_modal(self) -> bool:
        """
        일괄 번역 모달창 처리
        
        사용 가능한 번역 횟수와 선택된 상품 수를 비교하여
        자동으로 진행 여부를 결정합니다.
        
        Returns:
            bool: 성공 여부 (번역 시작 또는 안전한 닫기)
        """
        try:
            logger.info("일괄 번역 모달창 처리 시작")
            
            # 모달창이 열릴 때까지 대기
            modal_selectors = [
                ".ant-modal-content",
                "div[class*='ant-modal-content']",
                "div[role='dialog'][aria-labelledby]"
            ]
            
            modal_found = False
            for selector in modal_selectors:
                try:
                    self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    logger.info(f"일괄 번역 모달창 감지됨: {selector}")
                    modal_found = True
                    break
                except TimeoutException:
                    continue
            
            if not modal_found:
                logger.error("일괄 번역 모달창을 찾을 수 없습니다")
                return False
            
            time.sleep(1)  # 모달창 로딩 대기
            
            # 사용 가능한 번역 횟수 확인
            available_translations = self._get_available_translation_count()
            if available_translations is None:
                logger.warning("번역 횟수를 확인할 수 없어 안전하게 모달을 닫습니다")
                self.close_batch_translate_modal()
                return False
            
            # 선택된 상품 수 확인
            selected_count = self.get_selected_product_count()
            if selected_count == 0:
                logger.warning("선택된 상품이 없어 안전하게 모달을 닫습니다")
                self.close_batch_translate_modal()
                return False
            
            logger.info(f"사용 가능한 번역 횟수: {available_translations}, 선택된 상품 수: {selected_count}")
            
            # 번역 가능 여부 판단
            if available_translations >= selected_count:
                logger.info("번역 가능: 일괄 번역을 시작합니다")
                return self.click_batch_translate_start_button()
            else:
                logger.info("번역 불가능: 사용 가능한 횟수가 부족하여 모달을 닫습니다")
                # 모달을 닫고 False를 반환하여 워크플로우 중단
                self.close_batch_translate_modal()
                return False
            
        except Exception as e:
            logger.error(f"일괄 번역 모달창 처리 중 오류: {e}")
            # 오류 발생 시 안전하게 모달 닫고 False 반환
            self.close_batch_translate_modal()
            return False
    
    def _get_available_translation_count(self) -> int:
        """
        모달창에서 사용 가능한 번역 횟수를 추출합니다.
        
        Returns:
            int: 사용 가능한 번역 횟수, 실패 시 None
        """
        try:
            # 번역 횟수 텍스트를 찾는 선택자들
            selectors = [
                ".ant-alert-message .PrimaryColorPrimary",
                ".ant-alert-content .H5Medium16",
                "span.PrimaryColorPrimary",
                "//span[contains(@class, 'PrimaryColorPrimary')]",
                "//div[contains(@class, 'ant-alert-message')]//span[contains(text(), '회')]"
            ]
            
            for selector in selectors:
                try:
                    if selector.startswith('//'):
                        # XPath 선택자
                        element = self.driver.find_element(By.XPATH, selector)
                    else:
                        # CSS 선택자
                        element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    text = element.text.strip()
                    logger.info(f"번역 횟수 텍스트 발견: '{text}'")
                    
                    # 숫자 추출 (예: "300회" -> 300)
                    import re
                    numbers = re.findall(r'\d+', text)
                    if numbers:
                        count = int(numbers[0])
                        logger.info(f"추출된 번역 횟수: {count}")
                        return count
                        
                except (NoSuchElementException, ValueError):
                    continue
            
            logger.error("번역 횟수를 찾을 수 없습니다")
            return None
            
        except Exception as e:
            logger.error(f"번역 횟수 추출 중 오류: {e}")
            return None
    
    def click_batch_translate_start_button(self) -> bool:
        """
        '일괄 번역 시작' 버튼을 클릭합니다.
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("일괄 번역 시작 버튼 클릭 시도")
            
            # 일괄 번역 시작 버튼 선택자들 (XPath 우선 사용)
            selectors = [
                "//div[contains(@class, 'ant-modal-content')]//button[.//span[text()='일괄 번역 시작']]",
                "//button[.//span[text()='일괄 번역 시작']]",
                "//div[contains(@class, 'ant-modal-content')]//button[.//span[contains(text(), '일괄 번역')]]",
                "//button[.//span[contains(text(), '일괄 번역')]]",
                ".ant-modal-footer button.ant-btn-primary"
            ]
            
            for selector in selectors:
                try:
                    if selector.startswith('//'):
                        # XPath 선택자
                        button = self.wait.until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    else:
                        # CSS 선택자
                        button = self.wait.until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    
                    button.click()
                    logger.info(f"일괄 번역 시작 버튼 클릭 성공: {selector}")
                    time.sleep(1)
                    return True
                except TimeoutException:
                    continue
            
            logger.error("일괄 번역 시작 버튼을 찾을 수 없습니다")
            return False
            
        except Exception as e:
            logger.error(f"일괄 번역 시작 버튼 클릭 중 오류: {e}")
            return False
    
    def close_batch_translate_modal(self) -> bool:
        """
        일괄 번역 모달창을 닫습니다.
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("일괄 번역 모달창 닫기 시도")
            
            # 닫기 버튼 선택자들 (DOM 구조에 맞게 우선순위 조정)
            selectors = [
                # 모달 헤더의 X 버튼 (가장 확실한 선택자)
                "button.ant-modal-close",
                ".ant-modal-close",
                "//button[@type='button'][@aria-label='Close']",
                "//button[contains(@class, 'ant-modal-close')]",
                # 모달 푸터의 닫기 버튼
                "//div[contains(@class, 'ant-modal-footer')]//button[.//span[text()='닫기']]",
                "//button[.//span[text()='닫기']]",
                "//div[contains(@class, 'ant-modal-content')]//button[.//span[text()='닫기']]",
                # 백업 선택자들
                "//div[contains(@class, 'ant-modal-content')]//button[.//span[contains(text(), '닫기')]]",
                "//button[.//span[contains(text(), '닫기')]]"
            ]
            
            for selector in selectors:
                try:
                    if selector.startswith('//'):
                        # XPath 선택자
                        button = self.wait.until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    else:
                        # CSS 선택자
                        button = self.wait.until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    
                    button.click()
                    logger.info(f"일괄 번역 모달 닫기 버튼 클릭 성공: {selector}")
                    time.sleep(0.5)
                    return True
                except TimeoutException:
                    continue
            
            logger.error("일괄 번역 모달 닫기 버튼을 찾을 수 없습니다")
            return False
            
        except Exception as e:
            logger.error(f"일괄 번역 모달 닫기 중 오류: {e}")
            return False
    
    def perform_complete_batch_translate_workflow(self) -> bool:
        """
        완전한 일괄 번역 워크플로우 실행 (선택 + 번역 버튼 + 모달 처리)
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("완전한 일괄 번역 워크플로우 시작")
            
            # 1. 기본 일괄 번역 워크플로우 (상품 선택 + 번역 버튼 클릭)
            if not self.perform_batch_translate_workflow():
                logger.error("기본 일괄 번역 워크플로우 실패")
                return False
            
            # 2. 일괄 번역 모달창 처리
            if not self.handle_batch_translate_modal():
                logger.error("일괄 번역 모달창 처리 실패")
                return False
            
            logger.info("완전한 일괄 번역 워크플로우 완료")
            return True
            
        except Exception as e:
            logger.error(f"완전한 일괄 번역 워크플로우 중 오류: {e}")
            return False


# 편의 함수들
def upload_products(driver) -> bool:
    """
    상품 업로드 실행
    
    Args:
        driver: Selenium WebDriver 인스턴스
        
    Returns:
        bool: 성공 여부
    """
    upload_utils = UploadUtils(driver)
    return upload_utils.perform_upload_workflow()


def batch_translate_products(driver) -> bool:
    """
    상품 일괄 번역 실행
    
    Args:
        driver: Selenium WebDriver 인스턴스
        
    Returns:
        bool: 성공 여부
    """
    upload_utils = UploadUtils(driver)
    return upload_utils.perform_batch_translate_workflow()


def delete_products(driver) -> bool:
    """
    상품 삭제 실행
    
    Args:
        driver: Selenium WebDriver 인스턴스
        
    Returns:
        bool: 성공 여부
    """
    upload_utils = UploadUtils(driver)
    return upload_utils.perform_delete_workflow()


def upload_products_with_modal(driver, markets_to_select=None) -> bool:
    """
    모달창 처리를 포함한 완전한 상품 업로드 실행
    
    Args:
        driver: Selenium WebDriver 인스턴스
        markets_to_select (list, optional): 선택할 마켓 ID 리스트
                                          예: ['cp', 'ss', 'est'] 
        
    Returns:
        bool: 성공 여부
    """
    upload_utils = UploadUtils(driver)
    return upload_utils.perform_complete_upload_workflow(markets_to_select)


def handle_upload_modal_only(driver, markets_to_select=None) -> bool:
    """
    업로드 모달창만 처리 (이미 모달이 열린 상태에서 사용)
    
    Args:
        driver: Selenium WebDriver 인스턴스
        markets_to_select (list, optional): 선택할 마켓 ID 리스트
        
    Returns:
        bool: 성공 여부
    """
    upload_utils = UploadUtils(driver)
    return upload_utils.handle_upload_modal(markets_to_select)


def close_upload_modal(driver) -> bool:
    """
    업로드 모달창 닫기
    
    Args:
        driver: Selenium WebDriver 인스턴스
        
    Returns:
        bool: 성공 여부
    """
    upload_utils = UploadUtils(driver)
    return upload_utils.close_upload_modal()