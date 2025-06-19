"""
퍼센티 상품 수정 자동화 스크립트 5단계 (신규 버전)
비그룹상품보기에 있는 상품을 수정한 후, 신규수집 그룹으로 이동하기
"""

import time
import sys
import logging
# import pyautogui  # 절대좌표 클릭 방식 중단 (command prompt 창 최소화 문제)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# 좌표 변환 공통 모듈 임포트
from coordinates.coordinate_conversion import convert_coordinates

# DOM 유틸리티 임포트
from dom_utils import highlight_element
# 클릭 유틸리티 임포트
from click_utils import smart_click
# 통합 유틸리티 모듈 임포트
from percenty_utils import hide_channel_talk_and_modals, periodic_ui_cleanup, ensure_clean_ui_before_action
# 새 탭에서의 로그인 모달창 숨기기 필요할 경우에만 사용
from login_modal_utils import apply_login_modal_hiding_for_new_tab

# 드롭다운 유틸리티 임포트
from dropdown_utils5 import get_dropdown_manager

# UI 요소 임포트
from ui_elements import UI_ELEMENTS

# 상품 편집 코어5 임포트
from product_editor_core5_3 import ProductEditorCore5_3

# 좌표 정보 임포트
from coordinates.coordinates_all import MENU

def get_batch_count_input():
    """
    사용자로부터 배치 수량을 입력받는 함수
    
    Returns:
        int: 배치 수량 (기본값: 20)
    """
    while True:
        try:
            print("\n" + "=" * 50)
            print("배치 작업 설정")
            print("=" * 50)
            batch_input = input("배치 수량을 입력하세요 (기본값: 20): ").strip()
            
            if not batch_input:  # 빈 입력시 기본값 사용
                batch_count = 20
            else:
                batch_count = int(batch_input)
                
            if batch_count <= 0:
                print("배치 수량은 1 이상이어야 합니다.")
                continue
                
            print(f"\n설정된 배치 수량: {batch_count}개")
            print("=" * 50 + "\n")
            return batch_count
            
        except ValueError:
            print("올바른 숫자를 입력해주세요.")
        except KeyboardInterrupt:
            print("\n\n배치 작업이 취소되었습니다.")
            sys.exit(0)

# 좌표 설정 파일 불러오기
from coordinates.coordinates_editgoods import (
    PRODUCT_MODAL_TAB,
    PRODUCT_MODAL_EDIT1,
    PRODUCT_MODAL_EDIT2,
    PRODUCT_PRICE_TAB,
    PRODUCT_MODAL_CLOSE,
    PRODUCT_DETAIL_EDIT,
    PRODUCT_MEMO_MODAL,
    DELAY_VERY_SHORT2,
    DELAY_VERY_SHORT5,
    DELAY_VERY_SHORT,
    DELAY_SHORT,
    DELAY_MEDIUM,
    DELAY_LONG,
    DELAY_VERY_LONG
)

# 로깅 설정
logger = logging.getLogger(__name__)

class PercentyNewStep1:
    def __init__(self, driver, browser_ui_height=95):
        """
        퍼센티 상품 수정 자동화 스크립트 5단계 초기화
        
        Args:
            driver: 셀레니움 웹드라이버 인스턴스
            browser_ui_height: 브라우저 UI 높이 (기본값: 95px)
        """
        self.driver = driver
        self.browser_ui_height = browser_ui_height
        logger.info("===== 퍼센티 상품 수정 자동화 스크립트 5단계 초기화 =====")
        
        # 브라우저 내부 크기 확인
        self.inner_width = self.driver.execute_script("return window.innerWidth")
        self.inner_height = self.driver.execute_script("return window.innerHeight")
        logger.info(f"브라우저 내부 크기: {self.inner_width}x{self.inner_height}")
        
        # 드롭다운 관리자 초기화
        self.dropdown_manager = get_dropdown_manager(driver)
        
        # 상품 편집 코어5 초기화
        self.product_editor_core5_3 = ProductEditorCore5_3(driver, dropdown_manager=self.dropdown_manager)

    def convert_coordinates(self, x, y):
        """
        절대좌표를 상대좌표로 변환
        
        Args:
            x: X 좌표 (절대값)
            y: Y 좌표 (절대값)
        
        Returns:
            tuple: 변환된 (x, y) 좌표
        """
        # 공통 좌표 변환 모듈을 호출하여 상대좌표 계산
        return convert_coordinates(x, y, self.inner_width, self.inner_height)

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
                # JavaScript를 이용한 대체 클릭 방식 (pyautogui 대신)
                logger.info(f"JavaScript 대체 클릭 방식 사용: ({rel_x}, {rel_y})")
                script = f"""
                try {{                
                    var element = document.elementFromPoint({rel_x}, {rel_y});
                    if (element) {{                    
                        // 클릭 이벤트 생성 및 발생
                        var clickEvent = new MouseEvent('click', {{                    
                            view: window,
                            bubbles: true,
                            cancelable: true,
                            clientX: {rel_x},
                            clientY: {rel_y}
                        }});
                        element.dispatchEvent(clickEvent);
                        
                        // 상세 정보 반환
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
                result = self.driver.execute_script(script)
                logger.info(f"JavaScript 대체 클릭 결과: {result}")
                
                # 실패 시 fallback으로 더 간단한 click 실행
                if not result.get('success', False):
                    fallback_script = f"document.elementFromPoint({rel_x}, {rel_y}).click();"
                    try:
                        self.driver.execute_script(fallback_script)
                        logger.info("Fallback 클릭 성공")
                    except Exception as inner_e:
                        logger.warning(f"Fallback 클릭도 실패: {inner_e}")
                else:
                    logger.info(f"클릭된 요소: {result.get('tagName')} {result.get('text')} ID: {result.get('id')} CLASS: {result.get('className')}")
                                                
                logger.info(f"JavaScript 대체 클릭 완료: ({rel_x}, {rel_y})")
            
            # 클릭 후 대기
            time.sleep(delay_type)
            return True
            
        except Exception as e:
            logger.error(f"좌표 클릭 중 오류 발생: {e}")
            return False

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
            element = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((selector_type, selector))
            )
            element.click()
            logger.info(f"DOM 선택자 클릭 성공: {selector}")
            time.sleep(delay_type)
            return True
        except (TimeoutException, NoSuchElementException) as e:
            if fallback_coords:
                logger.warning(f"DOM 선택자 클릭 실패, 좌표 클릭으로 대체: {e}")
                return self.click_at_coordinates(fallback_coords, delay_type)
            else:
                logger.error(f"DOM 선택자 클릭 실패, 대체 좌표 없음: {e}")
                return False

    def open_nongroup_products_view(self, attempts=3):
        """비그룹상품보기 화면을 엽니다."""
        logger.info("비그룹상품보기 화면 열기 시도")
        
        # 페이지가 완전히 로드될 때까지 충분히 대기
        time.sleep(DELAY_MEDIUM)
        
        # 스크롤을 상단으로 이동
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(DELAY_SHORT)
        
        # 1. 먼저 정확한 DOM 선택자로 시도 (주어진 HTML 구조 기반)
        try:
            logger.info("그룹상품 보기 텍스트와 토글 스위치 찾기 시도")
            
            # 전략 1: 그룹상품 보기 텍스트 찾기
            group_text_selector = "//span[contains(text(), '그룹상품 보기')]"               
            group_text = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, group_text_selector))
            )
            
            logger.info("그룹상품 보기 텍스트 찾기 성공")
            
            # 해당 텍스트의 부모 div 요소 찾기
            parent_div = group_text.find_element(By.XPATH, "..")
            
            # 부모 div 내에서 토글 스위치 찾기
            toggle_switch = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, ".//button[@role='switch']"))
            )
            
            # 토글 스위치 상태 확인
            is_checked = 'ant-switch-checked' in toggle_switch.get_attribute('class')
            logger.info(f"현재 토글 스위치 상태: {'그룹상품 보기' if is_checked else '비그룹상품 보기'}")
            
            # 그룹상품 보기인 경우에만 클릭하여 비그룹상품 보기로 전환
            if is_checked:
                logger.info("현재 그룹상품 보기 상태임. 토글 스위치 클릭하여 비그룹상품 보기로 전환")
                toggle_switch.click()
            else:
                logger.info("이미 비그룹상품 보기 상태임. 클릭하지 않고 유지")
            
            logger.info("그룹상품/비그룹상품 토글 스위치 조작 성공")
            time.sleep(DELAY_MEDIUM)
            return True
            
        except Exception as e:
            logger.warning(f"DOM 선택자로 토글 스위치 조작 실패: {e}")
            logger.info("전략 2: 좌표 기반 방식으로 전환")
            
        # 2. 전략 2: 직접 토글 스위치 XPath로 찾기 시도
        try:
            logger.info("직접 토글 스위치 선택자로 찾기 시도")
            toggle_selector = "//button[@role='switch' and contains(@class, 'ant-switch')]"               
            toggle_switch = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, toggle_selector))
            )
            
            # 토글 스위치 상태 확인
            is_checked = 'ant-switch-checked' in toggle_switch.get_attribute('class')
            logger.info(f"직접 찾은 토글 스위치 상태: {'그룹상품 보기' if is_checked else '비그룹상품 보기'}")
            
            # 그룹상품 보기인 경우에만 클릭하여 비그룹상품 보기로 전환
            if is_checked:
                logger.info("현재 그룹상품 보기 상태임. 토글 스위치 클릭하여 비그룹상품 보기로 전환")
                toggle_switch.click()
            else:
                logger.info("이미 비그룹상품 보기 상태임. 클릭하지 않고 유지")
            
            logger.info("직접 토글 스위치 조작 성공")
            time.sleep(DELAY_MEDIUM)
            return True
            
        except Exception as e:
            logger.warning(f"직접 토글 스위치 선택자로 조작 실패: {e}")
            logger.info("전략 3: 좌표 기반 방식으로 전환")
        
        # 3. DOM 선택자 실패시 coordinates_editgoods.py에 정의된 좌표 사용
        logger.info("coordinates_editgoods.py에 정의된 PRODUCT_VIEW_NOGROUP 좌표 사용")
        # PRODUCT_MODAL_EDIT["PRODUCT_VIEW_NOGROUP"] = (470, 320) 좌표 사용
        nogroup_button_coords = PRODUCT_MODAL_EDIT["PRODUCT_VIEW_NOGROUP"]
        logger.info(f"비그룹상품보기 버튼 좌표: {nogroup_button_coords}")
        
        if self.click_at_coordinates(nogroup_button_coords, DELAY_MEDIUM):
            logger.info(f"비그룹상품보기 버튼 좌표 클릭 성공: {nogroup_button_coords}")
            time.sleep(DELAY_MEDIUM)
            return True
        else:
            # 좌표 기반 클릭도 실패했을 경우 상태를 저장하고 비디오 확인을 위해 페이지 소스 저장
            logger.error("비그룹상품보기 버튼 좌표 클릭 실패")
            # 페이지 소스 저장 (디버깅용)
            with open("page_source.html", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            logger.info("페이지 소스를 page_source.html에 저장했습니다 (디버깅용)")
            return False
            
    def click_product_group(self):
        """
        그룹상품관리 메뉴 클릭 - 하이브리드 방식 (DOM 선택자 + 좌표)
        
        DOM 선택자를 먼저 시도하고, 실패할 경우 좌표 기반 클릭을 시도하는
        하이브리드 방식을 구현합니다.
        """
        try:
            logger.info("그룹상품관리 메뉴 클릭 시도 (하이브리드 방식)")
            
            # 1. DOM 선택자 먼저 시도
            dom_success = False
            try:
                # UI_ELEMENTS에서 정보 가져오기
                element_info = UI_ELEMENTS["PRODUCT_GROUP"]
                dom_selector = element_info["dom_selector"]
                selector_type = element_info["selector_type"]
                
                # DOM 요소 강조 표시 (선택적)
                try:
                    highlight_element(self.driver, f"{selector_type}={dom_selector}")
                except:
                    pass
                
                logger.info(f"그룹상품관리 메뉴 DOM 선택자 기반 클릭 시도: {selector_type}={dom_selector}")
                
                # Selenium By 타입으로 변환
                by_type = By.XPATH if selector_type.lower() == "xpath" else By.CSS_SELECTOR
                
                # 요소 찾기 시도
                element = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((by_type, dom_selector))
                )
                
                # 요소가 발견되면 클릭
                element.click()
                logger.info("그룹상품관리 메뉴 DOM 선택자 기반 클릭 성공")
                dom_success = True
                
            except Exception as dom_error:
                logger.warning(f"DOM 선택자를 사용한 클릭 실패: {dom_error}")
                dom_success = False
            
            # 2. DOM 선택자로 실패한 경우 좌표 기반 클릭 시도
            if not dom_success:
                logger.info("DOM 선택자로 클릭 실패, 좌표 기반 클릭으로 전환합니다.")
                try:
                    # UI_ELEMENTS에서 좌표 가져오기
                    product_group_coords = UI_ELEMENTS["PRODUCT_GROUP"]["coordinates"]
                    logger.info(f"좌표 기반 클릭 시도: {product_group_coords}")
                    
                    # 좌표 클릭 실행
                    self.click_at_coordinates(product_group_coords, delay_type=DELAY_SHORT)
                    logger.info("좌표 기반 클릭 성공")
                    
                except Exception as coord_error:
                    logger.error(f"좌표 기반 클릭 실패: {coord_error}")
                    return False
            
            # 그룹상품관리 화면 로드 대기 (5초)
            logger.info("그룹상품관리 화면 로드 대기 - 5초")
            time.sleep(5)
            
            # 스크롤 위치 초기화
            self.driver.execute_script("window.scrollTo(0, 0);")
            logger.info("스크롤 위치를 최상단으로 초기화했습니다")
            
            return True
            
        except Exception as e:
            logger.error(f"그룹상품관리 메뉴 클릭 중 오류 발생: {e}")
            return False
    
    def run_step1_automation(self):
        """
        5단계 자동화 실행: 그룹상품관리 화면 열기
        """
        try:
            logger.info("===== 퍼센티 상품 수정 자동화 5단계 시작 =====")
            
            # 그룹상품관리 메뉴 클릭
            logger.info("그룹상품관리 메뉴 클릭 시도")
            if not self.click_product_group():
                logger.error("그룹상품관리 메뉴 클릭 실패, 자동화를 중단합니다.")
                return False
            logger.info("그룹상품관리 메뉴 클릭 완료")
            
            # 로직은 여기서 계속 구현될 예정
            logger.info("그룹상품관리 화면이 열렸습니다.")
            logger.info("다음 단계 작업을 위한 준비가 완료되었습니다.")
            
            return True
            
        except Exception as e:
            logger.error(f"상품 수정 자동화 실행 중 오류 발생: {e}")
            return False

# 일반적으로 사용되는 모듈들
import sys

# 단독 실행 시 5단계 자동화 코드
if __name__ == "__main__":
    # 기본 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # 순환 임포트 문제 해결을 위해 동적 임포트 사용
        from login_percenty import PercentyLogin
        from account_manager import AccountManager
        
        # 1. 계정 관리자 초기화
        account_manager = AccountManager()
        
        # 2. 계정 정보 로드
        if not account_manager.load_accounts():
            print("계정 정보를 로드할 수 없습니다. 프로그램을 종료합니다.")
            sys.exit(1)
        
        # 3. 계정 선택
        selected_account = account_manager.select_account()
        if not selected_account:
            print("계정을 선택하지 않았습니다. 프로그램을 종료합니다.")
            sys.exit(0)
        
        # 4. 배치 수량 입력 받기
        batch_count = get_batch_count_input()
        
        # 5. 선택한 계정으로 로그인 객체 생성
        login = PercentyLogin(account=selected_account)
        
        # 6. 로그인 시도
        print(f"\n선택한 계정으로 로그인을 시도합니다: {selected_account.get('nickname', selected_account['id'])}")
        
        # 로그인 실행
        if not login.setup_driver():
            print("웹드라이버 설정 실패")
            sys.exit(1)
        
        if not login.login():
            print("로그인 실패")
            sys.exit(1)
        
        # AI 소싱 메뉴 클릭
        if not login.click_product_aisourcing_button_improved():
            print("AI 소싱 메뉴 클릭 실패")
            sys.exit(1)
            
        # 채널톡 및 로그인 모달창 숨기기 적용 (통합 유틸리티 사용)
        print("\n채널톡 및 로그인 모달창 숨기기 적용 시작...")
        result = hide_channel_talk_and_modals(login.driver, log_prefix="메인 실행")
        print(f"채널톡 및 로그인 모달창 숨기기 결과: {result}")
        
        print("\n\n" + "=" * 50)
        print(f"로그인 성공! '{selected_account.get('nickname', '')}'") 
        print("이제 5단계 자동화를 실행합니다...")
        print("=" * 50 + "\n")
        
        # 6. 상품 수정 5단계 자동화 실행
        step5_automation = PercentyNewStep1(login.driver)
        
        # 계정 ID 가져오기
        account_id = selected_account.get('id', '')
        
        # 그룹상품관리 화면 준비 (배치 작업 시 한 번만 실행)
        print("\n그룹상품관리 화면을 준비합니다...")
        if not step5_automation.product_editor_core5_3.prepare_group_management_screen():
            print("\n\n" + "=" * 50)
            print("그룹상품관리 화면 준비 실패. 로그를 확인하세요.")
            print("=" * 50 + "\n")
            sys.exit(1)
        
        # 배치 작업 실행
        success_count = 0
        batch_terminated_early = False
        
        for i in range(batch_count):
            print(f"\n\n{'='*60}")
            print(f"배치 작업 진행: {i+1}/{batch_count}")
            print(f"{'='*60}")
            
            # 코어5 프로세스 실행
            result = step5_automation.product_editor_core5_3.process_product_copy_and_optimization(account_id)
            if result:
                success_count += 1
                print(f"\n배치 {i+1} 성공! (성공: {success_count}/{i+1})")
                
                # 대기3 그룹에 상품이 없어서 종료된 경우 나머지 배치 중단
                if hasattr(step5_automation.product_editor_core5_3, '_last_termination_reason') and \
                   step5_automation.product_editor_core5_3._last_termination_reason == 'no_products_in_daegi3':
                    print(f"\n⚠️  대기3 그룹에 상품이 없어서 배치 작업을 조기 종료합니다.")
                    print(f"남은 배치 {batch_count - (i+1)}개는 실행되지 않습니다.")
                    batch_terminated_early = True
                    break
            else:
                print(f"\n배치 {i+1} 실패. (성공: {success_count}/{i+1})")
                
        # 최종 결과 출력
        print("\n\n" + "=" * 60)
        if batch_terminated_early:
            actual_batches = success_count  # 조기 종료 시 실제 실행된 배치 수
            print(f"배치 작업 조기 종료!")
            print(f"실행된 배치: {actual_batches}개 (계획: {batch_count}개)")
            print(f"성공한 배치: {success_count}개")
            if actual_batches > 0:
                print(f"성공률: {(success_count/actual_batches)*100:.1f}%")
        else:
            print(f"배치 작업 완료!")
            print(f"총 {batch_count}개 중 {success_count}개 성공")
            print(f"성공률: {(success_count/batch_count)*100:.1f}%")
        print("=" * 60 + "\n")
        
        # 무한 대기 (사용자가 Ctrl+C를 누를 때까지)
        print("종료하려면 Ctrl+C를 누르세요.")
        try:
            # 무한 대기
            while True:
                time.sleep(10)  # 10초마다 한 번씩 체크
        except KeyboardInterrupt:
            print("\n\n" + "=" * 50)
            print("사용자가 스크립트를 종료했습니다.")
            print("=" * 50 + "\n")
    
    except ImportError as e:
        print(f"\n임포트 오류 발생: {e}")
        print("로그인 모듈을 임포트할 수 없습니다.")
        print("순환 임포트 문제가 발생했을 수 있습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n오류 발생: {e}")
    finally:
        # 종료 시 브라우저 닫기
        if 'login' in locals() and login.driver:
            login.close_driver()
