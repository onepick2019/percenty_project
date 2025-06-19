"""
퍼센티 상품 수정 자동화 스크립트 1단계
로그인 후 상품 수정 작업 자동화
"""

import time
import logging
import pyautogui
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# 좌표 설정 파일 불러오기
from coordinate_step1 import (
    PRODUCT_MODAL_TAB,
    PRODUCT_MODAL_EDIT, 
    PRODUCT_MODAL_CLOSE,
    PRODUCT_DETAIL_EDIT,
    PRODUCT_MEMO_MODAL,
    DELAY_VERY_SHORT2,
    DELAY_VERY_SHORT,
    DELAY_SHORT,
    DELAY_MEDIUM,
    DELAY_LONG,
    DELAY_VERY_LONG
)

# 로깅 설정
logger = logging.getLogger(__name__)

class PercentyStep1:
    def __init__(self, driver, browser_ui_height=95):
        """
        퍼센티 상품 수정 자동화 스크립트 1단계 초기화
        
        Args:
            driver: 셀레니움 웹드라이버 인스턴스
            browser_ui_height: 브라우저 UI 높이 (기본값: 95px)
        """
        self.driver = driver
        self.browser_ui_height = browser_ui_height
        logger.info("===== 퍼센티 상품 수정 자동화 스크립트 1단계 초기화 =====")
        
        # 브라우저 내부 크기 확인
        self.inner_width = self.driver.execute_script("return window.innerWidth")
        self.inner_height = self.driver.execute_script("return window.innerHeight")
        logger.info(f"브라우저 내부 크기: {self.inner_width}x{self.inner_height}")

    def convert_coordinates(self, x, y):
        """
        절대좌표를 상대좌표로 변환
        
        Args:
            x: X 좌표 (절대값)
            y: Y 좌표 (절대값)
        
        Returns:
            tuple: 변환된 (x, y) 좌표
        """
        # 좌표 변환 공식 로깅
        logger.info(f"좌표 변환 공식: 개선된 비선형 변환 적용 - X축/Y축 화면 위치별 보정")
        
        # X축 보정계수 적용 (5구간으로 나누어 보정)
        # 구간 1: X 0-320 (최좌측 영역)
        if x <= 320:
            x_correction = 0.98
            logger.info(f"X축 최좌측 영역(0-320) 보정 계수 적용 ({x_correction})")
        # 구간 2: X 321-640 (좌측 영역)
        elif x <= 640:
            x_correction = 0.99
            logger.info(f"X축 좌측 영역(321-640) 보정 계수 적용 ({x_correction})")
        # 구간 3: X 641-1280 (중앙 영역)
        elif x <= 1280:
            x_correction = 1.00
            logger.info(f"X축 중앙 영역(641-1280) 보정 계수 적용 ({x_correction})")
        # 구간 4: X 1281-1600 (우측 영역)
        elif x <= 1600:
            x_correction = 1.01
            logger.info(f"X축 우측 영역(1281-1600) 보정 계수 적용 ({x_correction})")
        # 구간 5: X 1601-1920 (최우측 영역)
        else:
            x_correction = 1.02
            logger.info(f"X축 최우측 영역(1601-1920) 보정 계수 적용 ({x_correction})")
            
        # 보정된 X축 계산
        rel_x = int(self.inner_width * (x / 1920) * x_correction)
        
        # Y축 보정계수 적용 (5구간으로 나누어 보정)
        # 구간 1: Y 0-210 (최상단 영역)
        if y <= 210:
            y_correction = 0.67
            logger.info(f"Y축 최상단 영역(0-210) 보정 계수 적용 ({y_correction})")
            
        # 구간 2: Y 211-300 (상단 영역)
        elif y <= 300:
            y_correction = 0.86
            logger.info(f"Y축 상단 영역(211-300) 보정 계수 적용 ({y_correction})")
            
        # 구간 3: Y 301-435 (중상단 영역)
        elif y <= 435:
            y_correction = 0.90
            logger.info(f"Y축 중상단 영역(301-435) 보정 계수 적용 ({y_correction})")
            
        # 구간 4: Y 436-845 (중앙 영역)
        elif y <= 845:
            y_correction = 1.00
            logger.info(f"Y축 중앙 영역(436-845) 보정 계수 적용 ({y_correction})")
            
        # 구간 5: Y 846+ (하단 영역)
        else:
            # 846~975 구간은 점진적으로 보정계수 증가
            if y <= 890:
                y_correction = 1.01
                logger.info(f"Y축 하단 영역(846-890) 보정 계수 적용 ({y_correction})")
            elif y <= 935:
                y_correction = 1.03
                logger.info(f"Y축 하단 영역(891-935) 보정 계수 적용 ({y_correction})")
            else:  # 936 이상
                y_correction = 1.04
                logger.info(f"Y축 하단 영역(936+) 보정 계수 적용 ({y_correction})")
                
        # 보정된 Y축 계산
        rel_y = int(self.inner_height * (y / 1080) * y_correction)
        
        # 변환 상세 정보 추가 로깅
        logger.info(f"변환 상세 정보 - 브라우저 크기: {self.inner_width}x{self.inner_height}, 참조 크기: 1920x1080")
        logger.info(f"X축 계산: int({self.inner_width} * ({x} / 1920) * {x_correction:.2f}) = {rel_x}")
        logger.info(f"Y축 계산: int({self.inner_height} * ({y} / 1080) * {y_correction:.2f}) = {rel_y}")
        
        logger.info(f"좌표 변환: {(x, y)} -> {(rel_x, rel_y)}")
        return rel_x, rel_y

    def click_at_coordinates(self, coords, delay_type=DELAY_SHORT, use_js=True):
        """
        주어진 좌표를 클릭
        
        Args:
            coords: (x, y) 좌표 튜플
            delay_type: 클릭 후 대기 시간
            use_js: JavaScript로 클릭할지 여부
        """
        x, y = coords
        rel_x, rel_y = self.convert_coordinates(x, y)
        
        try:
            if use_js:
                # JavaScript를 이용한 클릭
                script = f"""
                var element = document.elementFromPoint({rel_x}, {rel_y});
                if (element) {{
                    var rect = element.getBoundingClientRect();
                    var clickEvent = new MouseEvent('click', {{
                        bubbles: true,
                        cancelable: true,
                        view: window,
                        clientX: {rel_x},
                        clientY: {rel_y}
                    }});
                    element.dispatchEvent(clickEvent);
                    return element.tagName + ' ' + element.textContent + ' ' + (element.id ? 'ID: ' + element.id : '') + ' CLASS: ' + element.className;
                }}
                return 'No element found at position';
                """
                result = self.driver.execute_script(script)
                logger.info(f"JavaScript로 클릭 성공: ({rel_x}, {rel_y})")
                logger.info(f"클릭된 요소: {result}")
            else:
                # pyautogui를 이용한 절대좌표 클릭
                window_pos = self.driver.get_window_position()
                browser_x = window_pos['x']
                browser_y = window_pos['y']
                
                # 브라우저 내부에서의 상대 좌표를 화면 절대 좌표로 변환
                screen_x = browser_x + rel_x
                screen_y = browser_y + rel_y
                
                pyautogui.click(x=screen_x, y=screen_y)
                logger.info(f"PyAutoGUI로 클릭 성공: ({screen_x}, {screen_y})")
            
            # 딜레이 적용
            logger.info(f"시간 지연 {delay_type}초 - 클릭 후 대기")
            time.sleep(delay_type)
            logger.info(f"시간 지연 완료 ({delay_type}초)")
            
        except Exception as e:
            logger.error(f"좌표 클릭 중 오류 발생: {e}")

    def try_dom_selector_first(self, selector, selector_type=By.CSS_SELECTOR, fallback_coords=None, delay_type=DELAY_SHORT):
        """
        DOM 선택자로 클릭을 시도하고, 실패하면 좌표 클릭으로 대체
        
        Args:
            selector: DOM 선택자
            selector_type: 선택자 타입 (기본값: CSS_SELECTOR)
            fallback_coords: 실패시 사용할 좌표 튜플
            delay_type: 클릭 후 대기 시간
        """
        try:
            logger.info(f"DOM 선택자 기반 클릭 시도: {selector}")
            element = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((selector_type, selector))
            )
            element.click()
            logger.info(f"DOM 선택자 클릭 성공: {selector}")
            time.sleep(delay_type)
            return True
        except (TimeoutException, NoSuchElementException) as e:
            logger.warning(f"DOM 선택자 클릭 실패: {e}, 대체 좌표 클릭으로 진행")
            if fallback_coords:
                self.click_at_coordinates(fallback_coords, delay_type)
            return False

    def run_step1_automation(self):
        """
        1단계 자동화 실행: 상품 수정 작업
        """
        logger.info("===== 퍼센티 상품 수정 자동화 1단계 시작 =====")
        
        try:
            # 1. 비그룹상품보기 토글 클릭
            logger.info("1. 비그룹상품보기 토글 클릭")
            self.click_at_coordinates(PRODUCT_MODAL_EDIT["PRODUCT_VIEW_NOGROUP"], DELAY_MEDIUM)

            # 2. 첫번째 상품 클릭
            logger.info("2. 첫번째 상품 모달창 열기")
            self.click_at_coordinates(PRODUCT_MODAL_EDIT["PRODUCT_FIRST_GOODS"], DELAY_MEDIUM)

            # 3. 메모편집 클릭
            logger.info("3. 메모편집")
            # 메모 내용 숨기기 클릭
            self.click_at_coordinates(PRODUCT_MEMO_MODAL["MEMO_MODAL_CLOSE"], DELAY_VERY_SHORT)
            
            # 메모편집 모달창 열기
            self.click_at_coordinates(PRODUCT_MEMO_MODAL["MEMO_MODAL_OPEN"], DELAY_SHORT)
            
            # 상품목록에 메모내용 노출하기 체크박스
            self.click_at_coordinates(PRODUCT_MEMO_MODAL["MEMO_MODAL_CHECKBOX"], DELAY_VERY_SHORT)
            
            # 메모편집 TEXTAREA 선택
            self.click_at_coordinates(PRODUCT_MEMO_MODAL["MEMO_MODAL_TEXTAREA"], DELAY_VERY_SHORT)
            
            # TODO: 여기서 메모 내용 조작 함수 추가 예정
            # TEXTAREA 선택후, Ctral+A 로 메모내용 전체선택후 Ctrl+C로 복사
            
            # 메모편집 저장후 닫기
            self.click_at_coordinates(PRODUCT_MEMO_MODAL["MEMO_MODAL_SAVEBUTTON"], DELAY_SHORT)
            
            # 4. 상세페이지 편집
            logger.info("4. 상세페이지 편집")
            # 상세페이지 탭 클릭
            self.click_at_coordinates(PRODUCT_MODAL_TAB["PRODUCT_TAB_DETAIL"], DELAY_MEDIUM)
            
            # HTML 삽입 버튼 클릭
            self.click_at_coordinates(PRODUCT_MODAL_EDIT["PRODUCT_HTMLSOURCE_OPEN"], DELAY_SHORT)
            
            # HTML 삽입 TEXTAREA 클릭
            self.click_at_coordinates(PRODUCT_MODAL_EDIT["PRODUCT_HTMLSOURCE_TEXTAREA"], DELAY_VERY_SHORT)
            
            # HTML 삽입 저장 버튼 클릭
            self.click_at_coordinates(PRODUCT_MODAL_EDIT["PRODUCT_HTMLSOURCE_SAVE"], DELAY_SHORT)
            
            # 5. 업로드 편집
            logger.info("5. 업로드 편집")
            # 업로드 탭 클릭
            self.click_at_coordinates(PRODUCT_MODAL_TAB["PRODUCT_TAB_UPLOAD"], DELAY_MEDIUM)
            
            # 상품정보고시 섹션 클릭
            self.click_at_coordinates(PRODUCT_MODAL_EDIT["PRODUCT_UPLOADEDIT_SELECT"], DELAY_SHORT)
            
            # 상품정보고시 두번째 입력창 선택
            self.click_at_coordinates(PRODUCT_MODAL_EDIT["PRODUCT_UPLOADEDIT_2ndINPUT"], DELAY_VERY_SHORT)
            
            # TODO: 여기서 입력 내용 붙여넣기 함수 추가 예정
            # INPUT 창 선택후, Ctrl+V로 붙여넣기
            
            # 상품정보고시 섹션 닫기 클릭
            self.click_at_coordinates(PRODUCT_MODAL_EDIT["PRODUCT_UPLOADEDIT_SELECT"], DELAY_VERY_SHORT)
            
            # 6. 상품명 편집
            logger.info("6. 상품명 편집")
            # 상품명/카테고리 탭 클릭
            self.click_at_coordinates(PRODUCT_MODAL_TAB["PRODUCT_TAB_BASIC"], DELAY_MEDIUM)
            
            # 경고단어 및 중복단어 삭제 (5개 연속 클릭)
            logger.info("경고단어 및 중복단어 삭제 시도")
            self.click_at_coordinates(PRODUCT_MODAL_EDIT["PRODUCT_ALERTWORDS_DEL1"], DELAY_VERY_SHORT2)
            self.click_at_coordinates(PRODUCT_MODAL_EDIT["PRODUCT_ALERTWORDS_DEL2"], DELAY_VERY_SHORT2)
            self.click_at_coordinates(PRODUCT_MODAL_EDIT["PRODUCT_ALERTWORDS_DEL3"], DELAY_VERY_SHORT2)
            self.click_at_coordinates(PRODUCT_MODAL_EDIT["PRODUCT_ALERTWORDS_DEL4"], DELAY_VERY_SHORT2)
            self.click_at_coordinates(PRODUCT_MODAL_EDIT["PRODUCT_ALERTWORDS_DEL5"], DELAY_VERY_SHORT2)
            
            # 상품명 TEXTAREA 클릭
            self.click_at_coordinates(PRODUCT_MODAL_EDIT["PRODUCT_NAMEEDIT_TEXTAREA"], DELAY_VERY_SHORT)
            
            # TODO: 여기서 상품명 수정 함수 추가 예정
            # 알파벳을 이용해, 기존 상품명에 접미사로 A부터 Z까지 순차적으로 붙여주는 함수
            
            # 7. 상세페이지 이미지 삭제
            logger.info("7. 상세페이지 이미지 삭제")
            # 상세페이지 탭 클릭
            self.click_at_coordinates(PRODUCT_MODAL_TAB["PRODUCT_TAB_DETAIL"], DELAY_MEDIUM)
            
            # 일괄편집 모달창 열기
            self.click_at_coordinates(PRODUCT_DETAIL_EDIT["PRODUCT_DETAIL_OPENEDIT"], DELAY_MEDIUM)
            
            # 첫번째 이미지 삭제
            self.click_at_coordinates(PRODUCT_DETAIL_EDIT["PRODUCT_DETAIL_DELIMAGE_1"], DELAY_VERY_SHORT2)
            
            # 일괄편집 모달창 PAGEDOWN
            self.click_at_coordinates(PRODUCT_DETAIL_EDIT["PRODUCT_DETAIL_PAGEDOWN"], DELAY_VERY_SHORT)
            
            # TODO: 이미지 개수 파악 및 삭제 함수 추가 예정
            # 총 이미지수가 31개 이상일 경우, 32번째 이후의 이미지 모두 삭제하기
            
            # 일괄편집 모달창 PAGEUP
            self.click_at_coordinates(PRODUCT_DETAIL_EDIT["PRODUCT_DETAIL_PAGEUP"], DELAY_VERY_SHORT)
            
            # 일괄편집 모달창 닫기
            self.click_at_coordinates(PRODUCT_DETAIL_EDIT["PRODUCT_DETAIL_CLOSEEDIT"], DELAY_VERY_SHORT)
            
            # 8. 상품수정 모달창 닫기
            logger.info("8. 상품수정 모달창 닫기")
            # 상품수정 전체 저장 버튼
            self.click_at_coordinates(PRODUCT_MODAL_EDIT["PRODUCT_SAVE_BUTTON"], DELAY_VERY_SHORT)
            
            # 상품수정 모달창 닫기 버튼
            self.click_at_coordinates(PRODUCT_MODAL_EDIT["PRODUCT_MODAL_CLOSE"], DELAY_MEDIUM)
            
            logger.info("===== 퍼센티 상품 수정 자동화 1단계 완료 =====")
            return True
            
        except Exception as e:
            logger.error(f"상품 수정 자동화 실행 중 오류 발생: {e}")
            return False

# 단독 실행 시 테스트 코드
if __name__ == "__main__":
    # 기본 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("이 파일은 login_step1.py에서 임포트하여 사용해야 합니다.")
    print("단독 실행 시에는 웹드라이버가 초기화되지 않았으므로 실행할 수 없습니다.")
