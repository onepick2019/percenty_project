# -*- coding: utf-8 -*-
"""
퍼센티 액션 요소 관련 좌표 정의 파일 (coordinates_action.py)
이 파일은 각 화면에서 사용되는 버튼, 체크박스 등 사용자 액션 요소의 좌표를 정의합니다.

# 좌표 변환 공식
relative_x = int(inner_width * (x / 1920))
relative_y = int(inner_height * (y / 1080))
"""

# 상품 관리 관련 좌표
PRODUCT = {
    # 첫번째 상품 수정화면 열기 위한 좌표
    "FIRST_PRODUCT_EDIT": (600, 600),  # 전체 화면 모드에 맞게 조정
    
    # 상품 수정 모달창 내 탭 좌표
    "TAB": {
        "BASIC": (600, 200),       # 기본정보 탭
        "OPTION": (700, 200),      # 옵션정보 탭
        "DETAIL": (800, 200),      # 상세정보 탭
        "DELIVERY": (900, 200),    # 배송정보 탭
        "MEMO": (1000, 200),       # 메모 탭
        "UPLOAD": (1100, 200),     # 업로드 탭
    }
}

# 그룹 상품 관리 화면 관련 좌표
GROUP = {
    # 비그룹상품보기 버튼
    "NON_GROUP_VIEW": (312, 564),
    
    # 그룹상품보기 버튼
    "GROUP_VIEW": (300, 250),
    
    # 그룹 이동 관련
    "SELECT_ALL": (100, 300),        # 전체 선택 체크박스
    "GROUP_MOVE_BUTTON": (300, 350), # 그룹이동 버튼
    "GROUP_DROPDOWN": (500, 400),    # 그룹 선택 드롭다운
    "FIRST_GROUP": (500, 450),       # 첫번째 그룹
    "CONFIRM_MOVE": (600, 500),      # 이동 확인 버튼
}

# 상품 수정 모달창 내 각 탭별 요소 좌표
PRODUCT_FORM_ELEMENTS = {
    # 기본정보 탭 요소
    "BASIC": {
        "PRODUCT_NAME": (600, 300),   # 상품명 입력필드
        "PRICE": (600, 400),          # 가격 입력필드
        "SAVE_BUTTON": (1100, 800)    # 저장 버튼
    },
    
    # 옵션정보 탭 요소
    "OPTION": {
        "ADD_OPTION": (800, 400),     # 옵션 추가 버튼
        "FIRST_OPTION_NAME": (600, 500), # 첫번째 옵션명 입력필드
        "SAVE_BUTTON": (1100, 800)    # 저장 버튼
    }
}
