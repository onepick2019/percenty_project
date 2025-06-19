# -*- coding: utf-8 -*-
"""
퍼센티 모달창 관련 좌표 정의 파일 (coordinates_modal.py)
이 파일은 각종 모달창의 버튼 및 요소 좌표를 정의합니다.

# 좌표 변환 공식
relative_x = int(inner_width * (x / 1920))
relative_y = int(inner_height * (y / 1080))
"""

# 일반 모달창 관련 공통 좌표
MODAL = {
    # 모달창 닫기 버튼 (일반적인 위치)
    "MODAL_CLOSE": (1200, 150),
    
    # ESC 키 대신 사용할 수 있는 모달창 바깥 영역
    "MODAL_OUTSIDE": (1500, 150),
    
    # 확인/취소 버튼 (일반적인 위치)
    "CONFIRM_BUTTON": (950, 550),
    "CANCEL_BUTTON": (850, 550)
}

# 경고 모달창 좌표
ALERT_MODAL = {
    # 경고창 확인 버튼
    "OK_BUTTON": (950, 550),
    
    # 경고창 닫기 버튼
    "CLOSE_BUTTON": (1200, 150)
}

# 상품 수정 모달창 좌표
PRODUCT_MODAL = {
    # 상품 수정 모달창 닫기 버튼
    "CLOSE_BUTTON": (1230, 130),
    
    # 모달창 하단 버튼
    "SAVE_BUTTON": (1100, 800),
    "CANCEL_BUTTON": (1000, 800)
}

# 그룹 관리 모달창 좌표
GROUP_MODAL = {
    # 그룹 추가/수정 모달창 닫기 버튼
    "CLOSE_BUTTON": (1200, 150),
    
    # 그룹 이동 확인 버튼
    "MOVE_CONFIRM": (600, 500)
}
