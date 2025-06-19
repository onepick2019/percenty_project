"""
토글 2회 클릭으로 상품 목록 새로고침하는 함수
"""
import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from human_delay import HumanLikeDelay
from timesleep import DELAY_STANDARD

logger = logging.getLogger("BatchProcessor")

def toggle_product_view(self):
    """상품 목록 새로고침을 위한 토글 2회 클릭 기능
    
    Returns:
        int: 현재 목록에 있는 상품 개수. 실패시 0 반환
    """
    logger.info("상품 목록 새로고침 (토글 2회 클릭 방식)")
    
    # 인간 같은 지연 적용
    delay = HumanLikeDelay(min_total_delay=3, max_total_delay=6, current_speed=0)
    
    # DOM 선택자 가져오기 - 동일한 DOM 선택자를 2회 사용
    from dom_selectors import EDITGOODS_SELECTORS
    selector = EDITGOODS_SELECTORS.get("PRODUCT_VIEW_NOGROUP", "//button[@role='switch' and contains(@class, 'ant-switch')]")
    
    # 첫번째 클릭 - 그룹상품보기
    logger.info("그룹상품보기 토글 클릭 시도 (1번째 클릭)")
    success = False
    
    try:
        logger.info(f"DOM 선택자로 토글 찾기 시도: {selector}")
        toggle_button = self.step_manager.driver.find_element(By.XPATH, selector)
        logger.info("토글 버튼 요소 찾음")
        toggle_button.click()
        logger.info("첫번째 토글 클릭 성공 (DOM 선택자)")
        success = True
    except Exception as e:
        logger.warning(f"DOM 선택자로 첫번째 토글 클릭 실패: {str(e)[:100]}...")
        
        # JavaScript 실행 시도
        try:
            logger.info("JavaScript로 토글 클릭 시도 (1번째)")
            js_script = """
                // 토글 버튼 찾기
                const toggleSwitch = document.querySelector('button[role="switch"][class*="ant-switch"]');
                if (toggleSwitch) {
                    toggleSwitch.click();
                    return true;
                }
                return false;
            """
            result = self.step_manager.driver.execute_script(js_script)
            if result:
                logger.info("JavaScript로 첫번째 토글 클릭 성공")
                success = True
            else:
                logger.warning("JavaScript로 토글 요소를 찾지 못함")
        except Exception as js_error:
            logger.error(f"JavaScript 실행 오류: {js_error}")
    
    # 첫번째 클릭 후 2초 고정 지연 추가 (사용자 요청)
    logger.info("첫번째 클릭 후 2초 고정 지연 적용")
    time.sleep(2.0)  # 고정 2초 지연
    
    # 추가 지연 - 화면 전환 기다리기
    time.sleep(delay.get_delay('transition'))
    
    # 두번째 클릭 - 비그룹상품보기
    logger.info("비그룹상품보기 토글 클릭 시도 (2번째 클릭)")
    success = False
    
    try:
        # 동일한 DOM 선택자 사용
        logger.info(f"DOM 선택자로 토글 찾기 시도: {selector}")
        toggle_button = self.step_manager.driver.find_element(By.XPATH, selector)
        logger.info("토글 버튼 요소 찾음")
        toggle_button.click()
        logger.info("두번째 토글 클릭 성공 (DOM 선택자)")
        success = True
    except Exception as e:
        logger.warning(f"DOM 선택자로 두번째 토글 클릭 실패: {str(e)[:100]}...")
        
        # JavaScript 실행 시도
        try:
            logger.info("JavaScript로 토글 클릭 시도 (2번째)")
            js_script = """
                // 토글 버튼 찾기
                const toggleSwitch = document.querySelector('button[role="switch"][class*="ant-switch"]');
                if (toggleSwitch) {
                    toggleSwitch.click();
                    return true;
                }
                return false;
            """
            result = self.step_manager.driver.execute_script(js_script)
            if result:
                logger.info("JavaScript로 두번째 토글 클릭 성공")
                success = True
            else:
                logger.warning("JavaScript로 토글 요소를 찾지 못함")
        except Exception as js_error:
            logger.error(f"JavaScript 실행 오류: {js_error}")
    
    # 두번째 클릭 후 5초 고정 지연 추가 (사용자 요청)
    logger.info("두번째 클릭 후 5초 고정 지연 적용")
    time.sleep(5.0)  # 고정 5초 지연
    
    # 기존 지연도 유지 (추가적인 안정성을 위해)
    wait_time = delay.get_delay('waiting') + DELAY_STANDARD
    logger.info(f"상품 목록 로딩 대기 - {wait_time}초")
    time.sleep(wait_time)
    
    # 페이지 로딩 확인
    try:
        logger.info("상품 목록 로딩 확인 시도...")
        WebDriverWait(self.step_manager.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'ant-table-tbody')]//tr"))
        )
        logger.info("상품 목록 로딩 확인됨")
    except Exception as e:
        logger.warning(f"상품 목록 로딩 확인 실패: {e}")
    
    # 상품 개수 확인
    try:
        product_count = self._check_product_count()
        logger.info(f"현재 비그룹상품 목록에 {product_count}개의 상품이 있습니다.")
    except Exception as e:
        logger.error(f"상품 개수 확인 중 오류: {e}")
        product_count = 0
    
    # 성공 여부와 관계없이 상품 개수 반환
    logger.info("상품 목록 새로고침 완료 및 화면 로딩 확인")
    return product_count
