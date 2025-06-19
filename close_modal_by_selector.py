import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotVisibleException, ElementNotInteractableException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

def close_modal_with_selectors(driver, timeout=10):
    """
    모달창을 선택자를 이용해 닫는 방법
    여러 선택자와 전략을 시도하여 모달을 안정적으로 닫습니다.
    """
    logging.info("선택자를 이용한 모달창 닫기 시도")
    
    # 시도할 전략 목록
    strategies = [
        {
            "name": "모달창 닫기 버튼 (텍스트: '닫기')",
            "script": """
                var closeButtons = document.querySelectorAll('.ant-modal-footer button span');
                for (var i = 0; i < closeButtons.length; i++) {
                    if (closeButtons[i].textContent.trim() === '닫기') {
                        closeButtons[i].click();
                        return '닫기 버튼 클릭됨';
                    }
                }
                return false;
            """
        },
        {
            "name": "ant-modal-close 클래스 버튼",
            "script": """
                var closeButtons = document.querySelectorAll('.ant-modal-close');
                if (closeButtons.length > 0) {
                    closeButtons[0].click();
                    return 'ant-modal-close 버튼 클릭됨';
                }
                return false;
            """
        },
        {
            "name": "모달 푸터의 모든 버튼",
            "script": """
                var footerButtons = document.querySelectorAll('.ant-modal-footer button');
                if (footerButtons.length > 0) {
                    footerButtons[footerButtons.length-1].click();
                    return '모달 푸터 버튼 클릭됨: ' + footerButtons[footerButtons.length-1].textContent;
                }
                return false;
            """
        },
        {
            "name": "사용자 제공 HTML 구조에 맞는 버튼",
            "script": """
                var targetButtons = document.querySelectorAll('.ant-modal-footer .ant-flex button');
                for (var i = 0; i < targetButtons.length; i++) {
                    var spans = targetButtons[i].querySelectorAll('span');
                    for (var j = 0; j < spans.length; j++) {
                        if (spans[j].textContent.trim() === '닫기') {
                            targetButtons[i].click();
                            return '사용자 제공 HTML 구조에서 닫기 버튼 클릭됨';
                        }
                    }
                }
                return false;
            """
        },
        {
            "name": "모달 배경 클릭",
            "script": """
                var modalMasks = document.querySelectorAll('.ant-modal-mask, .ant-modal-wrap');
                if (modalMasks.length > 0) {
                    modalMasks[0].click();
                    return '모달 배경 클릭됨';
                }
                return false;
            """
        },
        {
            "name": "ESC 키 시뮬레이션",
            "action": "keyboard"
        },
        {
            "name": "모든 버튼과 클릭 가능 요소 (최후의 수단)",
            "script": """
                var allClickables = document.querySelectorAll('button, [role="button"], a, .close, .btn');
                var clicked = false;
                for (var i = 0; i < allClickables.length; i++) {
                    var rect = allClickables[i].getBoundingClientRect();
                    if (rect.width > 0 && rect.height > 0) {
                        var style = window.getComputedStyle(allClickables[i]);
                        if (style.display !== 'none' && style.visibility !== 'hidden') {
                            allClickables[i].click();
                            clicked = true;
                            return '클릭 가능 요소 클릭됨: ' + allClickables[i].tagName + ' ' + 
                                   (allClickables[i].className || 'no-class') + ' ' + 
                                   (allClickables[i].textContent || 'no-text');
                        }
                    }
                }
                return clicked;
            """
        }
    ]
    
    # 각 전략 시도
    for index, strategy in enumerate(strategies):
        try:
            logging.info(f"전략 {index+1}: {strategy['name']} 시도")
            
            if strategy.get("action") == "keyboard":
                # 키보드 액션 수행
                actions = ActionChains(driver)
                actions.send_keys(Keys.ESCAPE).perform()
                logging.info(f"ESC 키 전송 완료")
            else:
                # 자바스크립트 실행
                result = driver.execute_script(strategy["script"])
                logging.info(f"전략 {index+1} 결과: {result}")
            
            # 전략 사이에 짧은 대기
            time.sleep(0.5)
            
            # 모달이 닫혔는지 확인
            modal_exists = driver.execute_script("""
                return document.querySelectorAll('.ant-modal, .ant-modal-root, .ant-modal-mask, .ant-modal-wrap').length > 0;
            """)
            
            if not modal_exists:
                logging.info(f"전략 {index+1}: {strategy['name']}(이)가 성공적으로 모달을 닫았습니다!")
                return True
                
        except Exception as e:
            logging.warning(f"전략 {index+1} 실행 중 오류 발생: {e}")
    
    # 모든 전략을 시도했지만 모달이 여전히 존재하는지 확인
    try:
        modal_exists = driver.execute_script("""
            return document.querySelectorAll('.ant-modal, .ant-modal-root, .ant-modal-mask, .ant-modal-wrap').length > 0;
        """)
        
        if not modal_exists:
            logging.info("모달이 성공적으로 닫혔습니다!")
            return True
        else:
            logging.warning("모든 전략을 시도했지만 모달이 여전히 존재합니다.")
            return False
    except Exception as e:
        logging.error(f"모달 존재 여부 확인 중 오류 발생: {e}")
        return False


def integrate_with_login_class(login_obj):
    """
    PercentyLogin 클래스 인스턴스를 받아 close_login_modal 메서드를 향상합니다.
    """
    result = close_modal_with_selectors(login_obj.driver)
    return result


# 테스트 코드
if __name__ == "__main__":
    # 테스트를 위한 간단한 실행 예제
    logging.basicConfig(level=logging.INFO, 
                      format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    try:
        # 웹드라이버 생성
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        driver = webdriver.Chrome(options=options)
        
        # 퍼센티 사이트 방문
        driver.get("https://percenty.com/user/signin")
        
        # 로그인 (테스트 목적으로만 - 실제 ID/PW는 입력하지 마세요)
        # 로그인 후 모달이 나타나면 닫기 시도
        input("로그인을 수동으로 완료한 후 Enter 키를 누르세요...")
        
        # 모달 닫기 시도
        close_modal_with_selectors(driver)
        
        input("테스트를 종료하려면 Enter 키를 누르세요...")
        
    except Exception as e:
        logging.error(f"테스트 중 오류 발생: {e}")
    finally:
        try:
            driver.quit()
        except:
            pass
