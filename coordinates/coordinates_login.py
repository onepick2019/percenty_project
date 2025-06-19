# -*- coding: utf-8 -*-
"""
퍼센티 로그인 관련 좌표 정의 파일 (coordinates_login.py)
이 파일은 로그인 화면의 각종 요소(입력창, 버튼 등)의 좌표를 정의합니다.

# 좌표 변환 공식
relative_x = int(inner_width * (x / 1920))
relative_y = int(inner_height * (y / 1080))
"""

# 브라우저 UI 관련 상수 (윈도우 창 모드와 전체화면 모드의 차이)
BROWSER_UI_HEIGHT = 95  # 브라우저 상단 UI 높이 (픽셀)

# 알림 및 모달창 닫기 버튼 좌표
NOTIFICATION = {
    "CLOSE": (1118, 107),    # 자동화 알림창 닫기 버튼
    "LOGIN_MODAL_CLOSE": (1200, 150),  # 로그인 후 나타나는 모달창 닫기 버튼 (modal 좌표에서 가져옴)
    "PASSWORD_SAVE_MODAL_CLOSE": (1801, 110)  # 비밀번호를 저장하시겠습니까 모달창 닫기 버튼
}

# 로그인 관련 좌표 - 로그인 화면 요소
LOGIN = {
    # 로그인 입력 필드 (이메일/아이디)
    "USERNAME_FIELD": (940, 440),  # 이메일/아이디 입력 필드 - 기존 키 이름 유지
    
    # 비밀번호 입력 필드
    "PASSWORD_FIELD": (940, 525),  # 비밀번호 입력 필드 - 수정함
    
    # 로그인 버튼
    "LOGIN_BUTTON": (940, 615),     # 로그인 버튼 - 수정함
    
    # 아이디 저장 체크박스
    "SAVE_ID_CHECKBOX": (780, 563),     # 아이디 저장 체크박스 (알림 닫힌 상태)
}

# 로그인 후 모달창 관련 좌표
LOGIN_MODAL = {
    # 로그인 후 나오는 다시 보지 않기 모달창 좌표
    "DONT_SHOW_AGAIN": (810, 800),    
}
