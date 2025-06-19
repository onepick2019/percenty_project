# -*- coding: utf-8 -*-
"""
퍼센티 시간 지연 관리 파일 (timesleep.py)
이 파일은 프로그램의 다양한 이벤트에 대한 시간 지연(time.sleep)을 중앙에서 관리합니다.
시간 지연을 이벤트 유형별로 그룹화하여 관리할 수 있도록 합니다.
"""

import time
import logging
import random
from selenium.webdriver.common.keys import Keys

# 기본 지연 시간 상수 (초 단위) - 동적 요소 처리에 맞게 최적화
DELAY_VERY_SHORT2 = 0.1   # 매우 짧은 지연 (경고단어삭제, 이미제삭제 등)
DELAY_VERY_SHORT5 = 0.3   # 매우 짧은 지연 (동일화면 단순순 클릭 등)
DELAY_VERY_SHORT = 0.5   # 매우 짧은 지연 (즉각적인 UI 변화 기다릴 때)
DELAY_SHORT = 1        # 짧은 지연 (작은 요소 클릭 후)
DELAY_MEDIUM = 2       # 중간 지연 (일반적인 요소 클릭 후)
DELAY_STANDARD = 3     # 표준 지연 (메뉴 항목 클릭 후)
DELAY_LONG = 5         # 긴 지연 (페이지 로딩 대기)
DELAY_EXTRA_LONG = 10  # 매우 긴 지연 (무거운 작업 대기)
DELAY_MAXIMUM = 15     # 최대 지연 (매우 무거운 작업 대기)

# 인간 행동 시뮬레이션을 위한 변수
HUMAN_MODE = True  # 인간 행동 시뮬레이션 활성화 여부

# ======================== 이벤트별 지연 시간 그룹 ========================

# === 1. 페이지 로딩 관련 지연 시간 ===
PAGE_LOAD = {
    "INITIAL": DELAY_LONG,         # 초기 페이지 로딩 (10초)
    "AFTER_LOGIN": DELAY_LONG,     # 로그인 후 페이지 로딩 (10초)
    "MENU_CHANGE": DELAY_STANDARD, # 메뉴 변경 후 페이지 로딩 (5초)
    "REFRESH": DELAY_MEDIUM,       # 페이지 새로고침 후 (3초)
}

# === 2. 입력 필드 관련 지연 시간 ===
INPUT_FIELD = {
    "AFTER_CLICK_VERYSHORT2": DELAY_VERY_SHORT2,    # 경고단어삭제, 이미제삭제 등 (0.2초)
    "AFTER_CLICK_VERYSHORT5": DELAY_VERY_SHORT5,    # 동일화면 단순순 클릭 등 (0.5초)
    "AFTER_CLICK_VERYSHORT": DELAY_VERY_SHORT,    # 같은 화면에서 입력 필드 클릭 후 (1초)
    "AFTER_CLICK": DELAY_SHORT,    # 입력 필드 클릭 후 (2초)
    "AFTER_TYPE": DELAY_SHORT,     # 텍스트 입력 후 (2초)
    "AFTER_CLEAR": DELAY_SHORT,    # 필드 내용 지우기 후 (2초)
    "AFTER_INPUT": DELAY_SHORT,    # 입력 후 (2초)
}

# === 3. 버튼 클릭 관련 지연 시간 ===
BUTTON_CLICK = {
    "STANDARD": DELAY_SHORT,       # 일반 버튼 클릭 후 (2초)
    "SUBMIT": DELAY_MEDIUM,        # 제출/저장 버튼 클릭 후 (3초)
    "LOGIN": DELAY_MEDIUM,         # 로그인 버튼 클릭 후 (3초)
}

# === 4. 모달창 관련 지연 시간 ===
MODAL = {
    "BEFORE_CLOSE": DELAY_SHORT,   # 모달창 닫기 전 (2초)
    "AFTER_CLOSE": DELAY_VERY_SHORT, # 모달창 닫기 후 (1초)
    "WAIT_APPEAR": DELAY_MEDIUM,   # 모달창 나타날 때까지 대기 (3초)
    "PASSWORD_SAVE": DELAY_MEDIUM, # 비밀번호 저장 모달 관련 (3초)
}

# === 5. 메뉴 탐색 관련 지연 시간 ===
MENU_NAVIGATION = {
    "AFTER_CLICK": DELAY_STANDARD, # 메뉴 클릭 후 (5초)
    "SUBMENU_OPEN": DELAY_SHORT,   # 서브메뉴 열림 대기 (2초)
    "PRODUCT_AISOURCING": DELAY_STANDARD,  # AI 소싱 메뉴 클릭 후 (5초)
    "PRODUCT_REGISTER": DELAY_STANDARD, # 신규상품등록 메뉴 클릭 후 (5초)
    "PRODUCT_MANAGE": DELAY_STANDARD,   # 등록상품관리 메뉴 클릭 후 (5초)
    "PRODUCT_GROUP": DELAY_STANDARD,    # 그룹상품관리 메뉴 클릭 후 (5초)
    "MARKET_SETTING": DELAY_STANDARD,   # 마켓설정 메뉴 클릭 후 (5초)
}

# === 6. 체크박스 관련 지연 시간 ===
CHECKBOX = {
    "AFTER_CLICK": DELAY_VERY_SHORT, # 체크박스 클릭 후 (1초)
    "SAVE_ID": DELAY_VERY_SHORT,     # 아이디 저장 체크박스 클릭 후 (1초)
}

# === 7. 외부 이벤트 대기 ===
EXTERNAL = {
    "RETRY_DELAY": DELAY_SHORT,    # 재시도 전 대기 (2초)
    "ERROR_RECOVERY": DELAY_MEDIUM, # 오류 발생 후 복구 대기 (3초)
}

# === 8. 키보드 액션 관련 지연 시간 ===
KEYBOARD_ACTION = {
    "AFTER_KEY": DELAY_SHORT,      # 키보드 액션 후 (2초)
    "AFTER_ESC": DELAY_SHORT,      # ESC 키 누른 후 (2초)
    "AFTER_TAB": DELAY_VERY_SHORT, # TAB 키 누른 후 (1초)
    "AFTER_ENTER": DELAY_SHORT,    # ENTER 키 누른 후 (2초)
}

# ======================== 도우미 함수 ========================

def sleep_with_logging(seconds, event_description=None):
    """
    지정된 시간(초) 동안 대기하며 로그를 남깁니다.
    
    Args:
        seconds (int): 대기할 시간(초)
        event_description (str, optional): 이벤트 설명. 제공되면 로그에 포함됩니다.
    """
    if event_description:
        logging.info(f"시간 지연 {seconds}초 - {event_description}")
    else:
        logging.info(f"시간 지연 {seconds}초")
    
    time.sleep(seconds)
    
    if event_description:
        logging.info(f"시간 지연 완료 ({seconds}초) - {event_description}")

def wait_for(seconds):
    """지정된 시간만큼 대기합니다."""
    time.sleep(seconds)

def human_delay(min_seconds=0.5, max_seconds=2.0, gaussian=False):
    """인간적인 랜덤 지연 시간을 생성합니다.
    
    Args:
        min_seconds: 최소 지연 시간(초)
        max_seconds: 최대 지연 시간(초)
        gaussian: True인 경우 가우시안 분포 사용, False인 경우 균일 분포 사용
    
    Returns:
        실제 적용된 지연 시간(초)
    """
    if not HUMAN_MODE:
        time.sleep(min_seconds)
        return min_seconds
        
    if gaussian:
        # 가우시안 분포 사용 (더 인간적인 분포)
        mean = (min_seconds + max_seconds) / 2
        std_dev = (max_seconds - min_seconds) / 6  # 3 표준편차가 범위의 반을 차지
        delay = random.gauss(mean, std_dev)
        # 범위 내로 제한
        delay = max(min_seconds, min(max_seconds, delay))
    else:
        # 균일 분포 사용
        delay = min_seconds + (max_seconds - min_seconds) * random.random()
    
    time.sleep(delay)
    return delay

def human_typing(driver, element, text, min_delay=0.05, max_delay=0.25):
    """인간처럼 타이핑하는 효과를 시뮬레이션합니다.
    
    Args:
        driver: Selenium WebDriver 인스턴스
        element: 텍스트를 입력할 WebElement
        text: 입력할 텍스트
        min_delay: 키 입력 사이의 최소 지연 시간(초)
        max_delay: 키 입력 사이의 최대 지연 시간(초)
    """
    if not HUMAN_MODE:
        element.send_keys(text)
        return
        
    # 가끔 오타를 만들고 수정하는 함수
    def make_typo(char):
        # 5% 확률로 오타 발생
        if random.random() < 0.05:
            wrong_char = chr(ord(char) + random.randint(-1, 1))
            element.send_keys(wrong_char)
            human_delay(0.2, 0.5)
            element.send_keys(Keys.BACKSPACE)  # 백스페이스로 오타 수정
            human_delay(0.1, 0.3)
            return True
        return False
    
    for char in text:
        # 오타 만들기 시도
        if not make_typo(char):
            element.send_keys(char)
        
        # 문자 사이의 지연 시간 (가우시안 분포 사용)
        human_delay(min_delay, max_delay, gaussian=True)
        
        # 가끔 긴 일시 중지 (생각하는 것처럼)
        if random.random() < 0.03:  # 3% 확률
            human_delay(0.5, 1.5)

def human_scroll(driver, direction='down', pixels=None, random_range=True):
    """인간적인 스크롤 행동을 시뮬레이션합니다.
    
    Args:
        driver: Selenium WebDriver 인스턴스
        direction: 스크롤 방향 ('up' 또는 'down')
        pixels: 스크롤할 픽셀 수, None인 경우 랜덤하게 결정
        random_range: 픽셀 수에 랜덤성 추가 여부
    """
    if not HUMAN_MODE:
        if pixels is None:
            pixels = 300
        scroll_script = f"window.scrollBy(0, {pixels if direction == 'down' else -pixels});"
        driver.execute_script(scroll_script)
        return
    
    # 픽셀 수가 지정되지 않은 경우 랜덤하게 결정
    if pixels is None:
        pixels = random.randint(100, 500)
    
    # 랜덤 범위 적용
    if random_range:
        variation = pixels * 0.2  # 20% 변동
        pixels = int(pixels + random.uniform(-variation, variation))
    
    # 방향에 따라 픽셀 값 조정
    if direction == 'up':
        pixels = -pixels
    
    # 스크롤 스크립트 실행
    scroll_script = f"window.scrollBy(0, {pixels});"
    driver.execute_script(scroll_script)
    
    # 스크롤 후 잠시 대기 (페이지 로딩 및 인간 행동 시뮬레이션)
    human_delay(0.5, 1.5, gaussian=True)

def set_human_mode(enable=True):
    """인간 행동 시뮬레이션 모드를 설정합니다.
    
    Args:
        enable: True이면 인간 행동 시뮬레이션 활성화, False이면 비활성화
    """
    global HUMAN_MODE
    HUMAN_MODE = enable

# ======================== 이벤트별 지연 함수 ========================

# === 1. 페이지 로딩 관련 지연 함수 ===
def wait_for_page_load():
    """초기 페이지 로딩 대기 (10초)"""
    sleep_with_logging(PAGE_LOAD["INITIAL"], "페이지 로딩 대기")

def wait_after_login():
    """로그인 후 페이지 로딩 대기 (10초)"""
    sleep_with_logging(PAGE_LOAD["AFTER_LOGIN"], "로그인 후 페이지 로딩")

def wait_after_menu_change():
    """메뉴 변경 후 페이지 로딩 대기 (5초)"""
    sleep_with_logging(PAGE_LOAD["MENU_CHANGE"], "메뉴 변경 후 페이지 로딩")

# === 2. 입력 필드 관련 지연 함수 ===
def wait_after_field_click():
    """입력 필드 클릭 후 대기 (2초)"""
    sleep_with_logging(INPUT_FIELD["AFTER_CLICK"], "입력 필드 클릭 후")

def wait_after_typing():
    """텍스트 입력 후 대기 (2초)"""
    sleep_with_logging(INPUT_FIELD["AFTER_TYPE"], "텍스트 입력 후")

# === 3. 버튼 클릭 관련 지연 함수 ===
def wait_after_button_click():
    """일반 버튼 클릭 후 대기 (2초)"""
    sleep_with_logging(BUTTON_CLICK["STANDARD"], "버튼 클릭 후")

def wait_after_login_button():
    """로그인 버튼 클릭 후 대기 (3초)"""
    sleep_with_logging(BUTTON_CLICK["LOGIN"], "로그인 버튼 클릭 후")

# === 4. 모달창 관련 지연 함수 ===
def wait_before_modal_close():
    """모달창 닫기 전 대기 (2초)"""
    sleep_with_logging(MODAL["BEFORE_CLOSE"], "모달창 닫기 전")

def wait_after_modal_close():
    """모달창 닫기 후 대기 (1초)"""
    sleep_with_logging(MODAL["AFTER_CLOSE"], "모달창 닫기 후")

def wait_password_save_modal():
    """비밀번호 저장 모달 관련 대기 (3초)"""
    sleep_with_logging(MODAL["PASSWORD_SAVE"], "비밀번호 저장 모달 처리")

# === 5. 메뉴 탐색 관련 지연 함수 ===
def wait_after_menu_click(menu_name=None):
    """메뉴 클릭 후 대기 (5초)"""
    description = f"{menu_name} 메뉴 클릭 후" if menu_name else "메뉴 클릭 후"
    sleep_with_logging(MENU_NAVIGATION["AFTER_CLICK"], description)

def wait_after_home_menu():
    """AI 소싱 메뉴 클릭 후 대기 (5초)"""
    sleep_with_logging(MENU_NAVIGATION["PRODUCT_AISOURCING"], "AI 소싱 메뉴 클릭 후")

def wait_after_product_register_menu():
    """신규상품등록 메뉴 클릭 후 대기 (5초)"""
    sleep_with_logging(MENU_NAVIGATION["PRODUCT_REGISTER"], "신규상품등록 메뉴 클릭 후")

def wait_after_product_manage_menu():
    """등록상품관리 메뉴 클릭 후 대기 (5초)"""
    sleep_with_logging(MENU_NAVIGATION["PRODUCT_MANAGE"], "등록상품관리 메뉴 클릭 후")

def wait_after_product_group_menu():
    """그룹상품관리 메뉴 클릭 후 대기 (5초)"""
    sleep_with_logging(MENU_NAVIGATION["PRODUCT_GROUP"], "그룹상품관리 메뉴 클릭 후")

def wait_after_market_setting_menu():
    """마켓설정 메뉴 클릭 후 대기 (5초)"""
    sleep_with_logging(MENU_NAVIGATION["MARKET_SETTING"], "마켓설정 메뉴 클릭 후")

# === 6. 체크박스 관련 지연 함수 ===
def wait_after_checkbox_click():
    """체크박스 클릭 후 대기 (1초)"""
    sleep_with_logging(CHECKBOX["AFTER_CLICK"], "체크박스 클릭 후")

def wait_after_save_id_checkbox():
    """아이디 저장 체크박스 클릭 후 대기 (1초)"""
    sleep_with_logging(CHECKBOX["SAVE_ID"], "아이디 저장 체크박스 클릭 후")

# === 7. 외부 이벤트 대기 ===
def wait_before_retry():
    """재시도 전 대기 (2초)"""
    sleep_with_logging(EXTERNAL["RETRY_DELAY"], "재시도 전 대기")

def wait_after_error():
    """오류 발생 후 복구 대기 (3초)"""
    sleep_with_logging(EXTERNAL["ERROR_RECOVERY"], "오류 발생 후 복구 대기")

# === 8. 키보드 액션 관련 지연 함수 ===
def wait_after_keyboard_action(key_name=None):
    """키보드 액션 후 대기 (2초)"""
    description = f"{key_name} 키 액션 후" if key_name else "키보드 액션 후"
    sleep_with_logging(KEYBOARD_ACTION["AFTER_KEY"], description)

def wait_after_escape_key():
    """ESC 키 누른 후 대기 (2초)"""
    sleep_with_logging(KEYBOARD_ACTION["AFTER_ESC"], "ESC 키 누른 후")

def wait_after_tab_key():
    """TAB 키 누른 후 대기 (1초)"""
    sleep_with_logging(KEYBOARD_ACTION["AFTER_TAB"], "TAB 키 누른 후")

def wait_after_enter_key():
    """ENTER 키 누른 후 대기 (2초)"""
    sleep_with_logging(KEYBOARD_ACTION["AFTER_ENTER"], "ENTER 키 누른 후")
