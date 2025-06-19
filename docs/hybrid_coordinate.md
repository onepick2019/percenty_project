# 퍼센티 자동화: 하이브리드 좌표 접근법 가이드

## 개요

퍼센티 자동화 프로젝트는 DOM 선택자와 절대좌표를 함께 사용하는 하이브리드 방식으로 UI 요소와 상호작용합니다. 이 문서는 두 방식을 효과적으로 통합하는 방법을 설명합니다.

## 구조 및 파일 구성

### 1. DOM 선택자 중앙화 (`dom_selectors.py`)

모든 DOM 선택자를 한 곳에서 관리하여 일관성을 유지합니다.

```python
"""
퍼센티 자동화에 필요한 DOM 선택자 정의 파일
"""

# 메뉴 관련 선택자
MENU_SELECTORS = {
    "AI_SOURCING": "//span[contains(text(), 'AI 소싱')]/ancestor::li",
    "GROUP_PRODUCT_MANAGEMENT": "//span[@class='ant-menu-title-content' and text()='그룹 상품 관리']",
    "REGISTERED_PRODUCT_MANAGEMENT": "//span[@class='ant-menu-title-content' and text()='등록 상품 관리']",
    "NEW_PRODUCT_REGISTRATION": "//span[@class='ant-menu-title-content' and text()='신규 상품 등록']",
}

# 그룹 상품 화면 관련 선택자
GROUP_VIEW_SELECTORS = {
    "GROUP_TOGGLE_TEXT": "//span[contains(text(), '그룹상품 보기')]",
    "GROUP_TOGGLE_SWITCH": ".//button[@role='switch']",
    "GROUP_TOGGLE_DIRECT": "//button[@role='switch' and contains(@class, 'ant-switch')]",
}

# 더 많은 선택자 카테고리를 추가할 수 있음
```

### 2. 좌표 정의 (`coordinate_step1.py` - 기존 파일)

절대좌표는 기존 파일을 계속 사용합니다:

```python
# 이미 정의된 좌표 파일을 그대로 활용
PRODUCT_MODAL_EDIT = {
    "PRODUCT_SAVE_BUTTON": (1550, 990),
    "PRODUCT_VIEW_NOGROUP": (470, 320),
    # ...기타 좌표들
}
```

### 3. UI 요소 통합 (`ui_elements.py`)

DOM 선택자와 좌표를 매핑하여 통합 관리합니다:

```python
"""
퍼센티 UI 요소 통합 정의 파일 - DOM 선택자와 좌표를 함께 관리
"""
from dom_selectors import MENU_SELECTORS, GROUP_VIEW_SELECTORS
from coordinate_step1 import PRODUCT_MODAL_EDIT, PRODUCT_SELECT_GROUP

# 그룹 상품 관리 관련 UI 요소
GROUP_PRODUCT_MANAGEMENT = {
    "name": "그룹상품관리",
    "dom_selector": MENU_SELECTORS["GROUP_PRODUCT_MANAGEMENT"],
    "selector_type": "xpath",
    "coordinates": PRODUCT_SELECT_GROUP["PRODUCT_SELECT_GROUP1"],
    "fallback_order": ["dom", "coordinates"]  # 시도 순서
}

# 비그룹 상품 보기 토글 관련 UI 요소
NONGROUP_PRODUCT_TOGGLE = {
    "name": "비그룹상품보기 토글",
    "dom_selector": GROUP_VIEW_SELECTORS["NONGROUP_TOGGLE"],
    "selector_type": "xpath",
    "coordinates": PRODUCT_MODAL_EDIT["PRODUCT_VIEW_NOGROUP"],
    "fallback_order": ["dom", "coordinates"]
}

# UI 요소 매핑 사전
UI_ELEMENTS = {
    "GROUP_PRODUCT_MANAGEMENT": GROUP_PRODUCT_MANAGEMENT,
    "NONGROUP_PRODUCT_TOGGLE": NONGROUP_PRODUCT_TOGGLE,
    # 더 많은 요소 추가
}
```

### 4. 하이브리드 클릭 유틸리티 (`click_utils.py`)

DOM 선택자와 좌표 클릭을 통합 관리하는 함수를 구현합니다:

```python
"""
하이브리드 클릭 유틸리티 - DOM 선택자와 좌표 기반 클릭을 순차적으로 시도
"""
import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from coordinate_conversion import convert_coordinates

logger = logging.getLogger(__name__)

def hybrid_click(driver, element_key, delay=2.0, browser_ui_height=95):
    """
    UI 요소를 클릭하는 하이브리드 함수 - DOM 선택자와 좌표를 순차적으로 시도
    
    Args:
        driver: Selenium WebDriver 인스턴스
        element_key: ui_elements.py에 정의된 UI 요소 키
        delay: 클릭 후 대기 시간(초)
        browser_ui_height: 브라우저 UI 높이 보정값
    
    Returns:
        bool: 클릭 성공 여부
    """
    from ui_elements import UI_ELEMENTS
    
    # UI 요소 정보 가져오기
    if element_key not in UI_ELEMENTS:
        logger.error(f"정의되지 않은 UI 요소: {element_key}")
        return False
    
    element_info = UI_ELEMENTS[element_key]
    element_name = element_info["name"]
    fallback_order = element_info.get("fallback_order", ["dom", "coordinates"])
    
    logger.info(f"{element_name} 요소 클릭 시도 - 하이브리드 방식")
    
    # 시도 순서에 따라 클릭 방식 적용
    for method in fallback_order:
        if method == "dom":
            # DOM 선택자 방식 시도
            dom_selector = element_info.get("dom_selector")
            selector_type = element_info.get("selector_type", "xpath")
            
            if not dom_selector:
                logger.info(f"{element_name} 요소에 DOM 선택자가 정의되지 않음, 다음 방식 시도")
                continue
                
            try:
                logger.info(f"{element_name} DOM 선택자 클릭 시도: {dom_selector}")
                
                # 선택자 타입 매핑
                by_mapping = {
                    "xpath": By.XPATH,
                    "css": By.CSS_SELECTOR,
                    "id": By.ID,
                    "name": By.NAME,
                    "class": By.CLASS_NAME,
                }
                by_type = by_mapping.get(selector_type.lower(), By.XPATH)
                
                # 요소 찾기 및 클릭
                element = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((by_type, dom_selector))
                )
                element.click()
                
                logger.info(f"{element_name} DOM 선택자 클릭 성공")
                time.sleep(delay)
                return True
                
            except Exception as e:
                logger.warning(f"{element_name} DOM 선택자 클릭 실패: {e}")
                logger.info("좌표 기반 방식으로 시도합니다.")
        
        elif method == "coordinates":
            # 좌표 기반 방식 시도
            coordinates = element_info.get("coordinates")
            
            if not coordinates:
                logger.info(f"{element_name} 요소에 좌표가 정의되지 않음, 다음 방식 시도")
                continue
                
            try:
                logger.info(f"{element_name} 좌표 클릭 시도: {coordinates}")
                
                # 좌표 변환 (절대좌표 -> 상대좌표)
                inner_width = driver.execute_script("return window.innerWidth")
                inner_height = driver.execute_script("return window.innerHeight")
                rel_x, rel_y = convert_coordinates(coordinates[0], coordinates[1], inner_width, inner_height)
                
                # JavaScript로 클릭 (pyautogui 대신)
                script = f"""
                try {{
                    var element = document.elementFromPoint({rel_x}, {rel_y});
                    if (element) {{
                        element.click();
                        return true;
                    }}
                    return false;
                }} catch(e) {{
                    return false;
                }}
                """
                result = driver.execute_script(script)
                
                if result:
                    logger.info(f"{element_name} 좌표 클릭 성공: ({rel_x}, {rel_y})")
                    time.sleep(delay)
                    return True
                else:
                    logger.warning(f"{element_name} 좌표 클릭 실패")
                    
            except Exception as e:
                logger.error(f"{element_name} 좌표 클릭 중 오류: {e}")
    
    # 모든 방식 실패
    logger.error(f"{element_name} 요소 클릭 실패 - 모든 방식 시도 후")
    return False
```

## 사용 방법

### 단계별 구현 방법

1. **DOM 선택자 중앙화**: `coordinate_step1.py`에서 정의하고 있는 절대좌표들의 DOM 선택자를 찾아 `dom_selectors.py` 파일에 정의합니다.
2. **UI 요소 통합**: `ui_elements.py` 파일을 만들어 DOM 선택자와 좌표를 매핑합니다.
3. **하이브리드 클릭 함수 구현**: `click_utils.py` 파일에 `hybrid_click` 함수를 구현합니다.

### 단계별 파일에서 사용 예시

```python
# percenty_new_step6.py에서 사용 예시
def click_product_group(self):
    """
    그룹상품관리 메뉴 클릭 - 하이브리드 방식
    """
    try:
        from click_utils import hybrid_click
        
        if hybrid_click(self.driver, "GROUP_PRODUCT_MANAGEMENT", delay=DELAY_MEDIUM):
            logger.info("그룹상품관리 메뉴 클릭 성공")
            
            # 스크롤 위치 초기화
            self.driver.execute_script("window.scrollTo(0, 0);")
            logger.info("스크롤 위치를 최상단으로 초기화했습니다")
            
            return True
        else:
            logger.error("그룹상품관리 메뉴 클릭 실패")
            return False
            
    except Exception as e:
        logger.error(f"그룹상품관리 메뉴 클릭 중 오류 발생: {e}")
        return False
```

## 유연한 호출 방식

1. **하이브리드 접근 필요시**:
   ```python
   hybrid_click(driver, "GROUP_PRODUCT_MANAGEMENT")
   ```

2. **DOM 선택자만 필요시**:
   ```python
   from dom_utils import click_by_selector
   click_by_selector(driver, "MENU.GROUP_PRODUCT_MANAGEMENT")
   ```

3. **좌표만 필요시**:
   ```python
   from coordinate_step1 import PRODUCT_SELECT_GROUP
   click_at_coordinates(driver, PRODUCT_SELECT_GROUP["PRODUCT_SELECT_GROUP1"])
   ```

## 장점

1. **유지보수 용이성**: UI 변경 시 한 파일만 수정하면 됨
2. **일관성 보장**: 모든 단계 파일이 동일한 선택자와 좌표를 사용
3. **코드 중복 제거**: 동일 선택자가 여러 파일에 하드코딩되는 문제 해결
4. **하이브리드 접근 일관성**: 좌표와 DOM 선택자 모두 중앙에서 관리
5. **점진적 마이그레이션**: DOM 구조 파악이 어려운 요소는 계속해서 좌표 기반으로 유지하고, 점차적으로 DOM 선택자를 추가하며 시스템 안정성 향상

## 구현 순서 및 전략

1. DOM 선택자 중앙화 파일 (`dom_selectors.py`) 생성
2. 통합 UI 요소 파일 (`ui_elements.py`) 생성
3. 하이브리드 클릭 유틸리티 (`click_utils.py`) 구현
4. 기존 코드를 점진적으로 새 방식으로 마이그레이션
5. DOM 구조 파악이 어려운 부분은 좌표 방식을 계속 유지

이 접근법은 기존 코드와의 호환성을 유지하면서 점진적으로 시스템을 개선할 수 있게 해줍니다.
