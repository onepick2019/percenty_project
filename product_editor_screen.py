"""등록상품관리 화면 열기 모듈
퍼센티 자동화에서 등록상품관리 화면을 여는 공통 기능 제공
"""

import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# 기존 모듈들 임포트
from dom_utils import highlight_element
from click_utils import smart_click
from dropdown_utils2 import get_product_search_dropdown_manager
from ui_elements import UI_ELEMENTS
from coordinates.coordinate_conversion import convert_coordinates
from coordinates.coordinates_editgoods import (
    DELAY_VERY_SHORT,
    DELAY_SHORT,
    DELAY_MEDIUM,
    DELAY_LONG
)

logger = logging.getLogger(__name__)

def open_product_editor_screen(driver):
    """
    등록상품관리 화면을 열고 초기 설정을 수행하는 함수
    
    Args:
        driver: Selenium WebDriver 인스턴스
        
    Returns:
        bool: 성공 여부
    """
    try:
        logger.info("등록상품관리 화면 열기 시작")
        
        # 브라우저 내부 크기 확인
        inner_width = driver.execute_script("return window.innerWidth")
        inner_height = driver.execute_script("return window.innerHeight")
        logger.info(f"브라우저 내부 크기: {inner_width}x{inner_height}")
        
        # 1. 등록상품관리 메뉴 클릭 - 하이브리드 방식 적용
        logger.info("등록상품관리 메뉴 클릭 시도 (하이브리드 방식)")
        
        # 1.1 DOM 선택자 먼저 시도
        dom_success = False
        try:
            # UI_ELEMENTS에서 정보 가져오기
            element_info = UI_ELEMENTS["PRODUCT_MANAGE"]
            dom_selector = element_info["dom_selector"]
            selector_type = element_info["selector_type"]
            
            # DOM 요소 강조 표시 (선택적)
            try:
                highlight_element(driver, f"{selector_type}={dom_selector}")
            except:
                pass
            
            logger.info(f"등록상품관리 메뉴 DOM 선택자 기반 클릭 시도: {selector_type}={dom_selector}")
            
            # Selenium By 타입으로 변환
            by_type = By.XPATH if selector_type.lower() == "xpath" else By.CSS_SELECTOR
            
            # 요소 찾기 시도
            element = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((by_type, dom_selector))
            )
            
            # 요소가 발견되면 클릭
            element.click()
            logger.info("등록상품관리 메뉴 DOM 선택자 기반 클릭 성공")
            dom_success = True
            
        except Exception as dom_error:
            logger.warning(f"DOM 선택자를 사용한 클릭 실패: {dom_error}")
            dom_success = False
        
        # 1.2 DOM 선택자로 실패한 경우 좌표 기반 클릭 시도
        if not dom_success:
            try:
                logger.info("DOM 선택자로 클릭 실패, 좌표 기반 클릭으로 전환합니다.")
                # UI_ELEMENTS에서 좌표 가져오기
                product_manage_coords = UI_ELEMENTS["PRODUCT_MANAGE"]["coordinates"]
                logger.info(f"좌표 기반 클릭 시도: {product_manage_coords}")
                
                # 좌표 변환 및 클릭 실행
                rel_x, rel_y = convert_coordinates(
                    product_manage_coords[0], 
                    product_manage_coords[1], 
                    inner_width, 
                    inner_height
                )
                
                # JavaScript로 클릭 실행
                script = f"""
                try {{
                    var element = document.elementFromPoint({rel_x}, {rel_y});
                    if (element) {{
                        element.click();
                        return {{
                            success: true,
                            tagName: element.tagName,
                            className: element.className,
                            id: element.id || 'no-id',
                            text: element.textContent ? element.textContent.substring(0, 50) : ''
                        }};
                    }}
                    return {{ success: false, reason: 'no-element' }};
                }} catch(e) {{                
                    return {{ success: false, reason: 'error', message: e.toString() }};
                }}
                """
                result = driver.execute_script(script)
                logger.info(f"JavaScript 클릭 결과: {result}")
                
                if result.get('success', False):
                    logger.info("좌표 기반 클릭 성공")
                else:
                    logger.error("좌표 기반 클릭 실패")
                    return False
                    
            except Exception as coord_error:
                logger.error(f"좌표 기반 클릭 실패: {coord_error}")
                return False
        
        # 등록상품관리 화면 로드 대기 (5초)
        logger.info("등록상품관리 화면 로드 대기 - 5초")
        time.sleep(5)
        
        # 2. 상품검색용 드롭박스에서 '신규수집' 그룹 선택
        logger.info("신규수집 그룹으로 변경 시작")
        
        # 드라이버 연결 상태 검증
        try:
            driver.current_url
            logger.info("드라이버 연결 상태 정상")
        except Exception as e:
            logger.error(f"드라이버 연결 상태 오류: {e}")
            return False
        
        dropdown_manager = get_product_search_dropdown_manager(driver)
        
        # 신규수집 그룹 선택 시도 (최대 3회 재시도)
        group_selection_success = False
        for attempt in range(3):
            try:
                logger.info(f"신규수집 그룹 선택 시도 {attempt + 1}/3")
                
                # 상품검색용 드롭박스에서 신규수집 그룹 선택 (통합 메서드 사용)
                if dropdown_manager.select_group_in_search_dropdown("신규수집"):
                    logger.info("신규수집 그룹 선택 성공")
                    
                    # 상품 목록 자동 로딩 대기
                    if dropdown_manager.verify_page_refresh():
                        logger.info("상품 목록 자동 로딩 완료")
                        group_selection_success = True
                        break
                    else:
                        logger.warning("상품 목록 로딩 확인 실패")
                else:
                    logger.warning(f"신규수집 그룹 선택 실패 (시도 {attempt + 1}/3)")
                
                if attempt < 2:
                    time.sleep(DELAY_MEDIUM)
                    
            except Exception as e:
                logger.error(f"신규수집 그룹 선택 중 오류 (시도 {attempt + 1}/3): {e}")
                time.sleep(DELAY_MEDIUM)
        
        if not group_selection_success:
            logger.error("신규수집 그룹 선택에 실패했습니다.")
            return False
        
        # 그룹 선택 후 페이지 로드 대기
        time.sleep(DELAY_MEDIUM)
        
        # 3. 50개씩 보기 설정
        logger.info("50개씩 보기 설정 시작")
        
        # 50개씩 보기 설정 시도 (최대 3회 재시도)
        items_per_page_success = False
        for attempt in range(3):
            try:
                logger.info(f"50개씩 보기 설정 시도 {attempt + 1}/3")
                
                # 50개씩 보기 설정
                if dropdown_manager.select_items_per_page("50"):
                    logger.info("50개씩 보기 설정 성공")
                    items_per_page_success = True
                    break
                else:
                    logger.warning(f"50개씩 보기 설정 실패 (시도 {attempt + 1}/3)")
                
                if attempt < 2:
                    time.sleep(DELAY_MEDIUM)
                    
            except Exception as e:
                logger.error(f"50개씩 보기 설정 중 오류 (시도 {attempt + 1}/3): {e}")
                time.sleep(DELAY_MEDIUM)
        
        if not items_per_page_success:
            logger.warning("50개씩 보기 설정에 실패했지만 작업을 계속 진행합니다.")
        
        # 설정 완료 후 페이지 로드 대기
        time.sleep(DELAY_MEDIUM)
        
        # 4. 화면 최상단으로 이동
        logger.info("화면 최상단으로 이동")
        try:
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(DELAY_SHORT)
            logger.info("화면 최상단 이동 완료")
        except Exception as e:
            logger.warning(f"화면 최상단 이동 실패: {e}")
        
        logger.info("등록상품관리 화면 열기 및 초기 설정 완료")
        return True
        
    except Exception as e:
        logger.error(f"등록상품관리 화면 열기 중 오류: {e}")
        return False