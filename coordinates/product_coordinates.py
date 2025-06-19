# -*- coding: utf-8 -*-
"""
product_coordinates.py 파일에서는
절대좌표를 아래의 공식으로 상대좌표로 변경할 좌표를 관리한다.

relative_x = int(inner_width * (menu_x / 1920))
relative_y = int(inner_height * (menu_y / 1080))

퍼센티 상품 수정 관련 좌표 정의 파일
이 파일은 상품 목록 화면과 상품 수정 모달창의 각종 요소(탭, 버튼 등)의 좌표를 정의합니다.
"""

# 그룹상품관리 화면의 상품 목록 좌표
PRODUCT_LIST = {
    "FIRST_PRODUCT": (640, 645),       # 첫 번째 상품 위치
    "PRODUCT_EDIT_BUTTON": (800, 250), # 상품 편집 버튼 위치
    "SECOND_PRODUCT": (500, 300),      # 두 번째 상품 위치
    "CONTEXT_MENU_EDIT": (550, 200),   # 컨텍스트 메뉴의 편집 옵션
    "GROUP_VIEW_TOGGLE": (470, 320),   # 그룹상품 보기/비그룹상품 보기 토글 버튼
    "SEARCH_BOX": (600, 150),          # 검색창
    "SEARCH_BUTTON": (700, 150)        # 검색 버튼
}

# 상품 수정 모달창 좌표
PRODUCT_MODAL = {
    "MODAL_CLOSE": (1200, 150),  # 모달창 닫기 버튼
    "TAB_BASIC": (350, 200),     # 기본정보 탭
    "TAB_OPTION": (450, 200),    # 옵션 탭
    "TAB_PRICE": (550, 200),     # 가격 탭
    "TAB_KEYWORD": (650, 200),   # 키워드 탭
    "TAB_THUMBNAIL": (750, 200), # 썸네일 탭
    "TAB_DETAIL": (850, 200),    # 상세페이지 탭
    "TAB_UPLOAD": (950, 200),    # 업로드 탭
    "TAB_MEMO": (1050, 200),     # 메모 탭
    "SAVE_BUTTON": (1000, 700)   # 저장 버튼
}

# 기본정보 탭 내부 요소 좌표
BASIC_INFO_TAB = {
    "PRODUCT_NAME": (500, 250),   # 상품명 입력 필드
    "CATEGORY1": (400, 350),      # 카테고리 1 선택
    "CATEGORY2": (500, 350),      # 카테고리 2 선택
    "CATEGORY3": (600, 350)       # 카테고리 3 선택
}

# 메모 탭 내부 요소 좌표
MEMO_TAB = {
    "MEMO_FIELD": (500, 350),     # 메모 입력 필드
    "ADD_MEMO_BUTTON": (600, 450) # 메모 추가 버튼
}

# 그룹 이동 관련 좌표
GROUP_MOVE = {
    "MOVE_BUTTON": (900, 150),     # 그룹 이동 버튼
    "GROUP_DROPDOWN": (500, 300),  # 그룹 선택 드롭다운
    "FIRST_GROUP": (500, 350),     # 첫 번째 그룹 
    "CONFIRM_BUTTON": (800, 500)   # 확인 버튼
}
