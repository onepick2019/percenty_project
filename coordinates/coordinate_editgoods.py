"""
상품 수정 모달창에서 사용하는 절대좌표 정의 파일
"""

# 딜레이 시간 상수 정의
DELAY_VERY_SHORT2 = 0.2  # 경고단어 삭제와 같은 빠른 작업용 (0.2초)
DELAY_VERY_SHORT5 = 0.5  # 같은 화면에서 입력 필드 클릭용 (0.5초)
DELAY_VERY_SHORT = 1.0   # 같은 화면에서 입력 필드 클릭용 (1초)
DELAY_SHORT = 2.0        # 일반 버튼 클릭용 (2초)
DELAY_MEDIUM = 3.0       # 제출/저장 버튼 클릭 후 (3초)
DELAY_LONG = 5.0         # 페이지 이동 후 (5초)
DELAY_VERY_LONG = 10.0   # 로딩 시간이 긴 경우 (10초)

# 상품수정 모달창 탭 좌표
PRODUCT_MODAL_TAB = {
    "PRODUCT_TAB_BASIC": (400, 120),     # 상품명/카테고리 탭
    "PRODUCT_TAB_OPTION": (490, 120),    # 옵션 탭
    "PRODUCT_TAB_PRICE": (545, 120),     # 가격 탭
    "PRODUCT_TAB_KEYWORD": (610, 120),   # 키워드 탭
    "PRODUCT_TAB_THUMBNAIL": (680, 120), # 썸네일 탭
    "PRODUCT_TAB_DETAIL": (760, 120),    # 상세페이지 탭
    "PRODUCT_TAB_UPLOAD": (845, 120),    # 업로드 탭
}

# 상품수정시 사용하는 좌표(상대좌표 사용)
# coordinate_conversion.py 의 구간별 적용
PRODUCT_MODAL_EDIT1 = {
    "PRODUCT_FIRST_GOODS": (700, 650),  # 첫번째 상품 모달창 열기
    "PRODUCT_UPLOADEDIT_SELECT": (800, 430),  # 상품정보고시 섹션 클릭, 열기 및 닫기 공용
    "PRODUCT_ALERTWORDS_DEL1": (820, 395),   # 상품명 경고단어 및 중복단어 삭제 클릭    
    "PRODUCT_ALERTWORDS_DEL2": (770, 395),   # 상품명 경고단어 및 중복단어 삭제 클릭
    "PRODUCT_ALERTWORDS_DEL3": (740, 395),   # 상품명 경고단어 및 중복단어 삭제 클릭
    "PRODUCT_ALERTWORDS_DEL4": (710, 395),   # 상품명 경고단어 및 중복단어 삭제 클릭 
    "PRODUCT_ALERTWORDS_DEL5": (680, 395),   # 상품명 경고단어 및 중복단어 삭제 클릭 
    "PRODUCT_ALERTWORDS_DEL6": (640, 395),   # 상품명 경고단어 및 중복단어 삭제 클릭 
}

# 상품수정시 사용하는 좌표(하이브리드 사용)
PRODUCT_MODAL_EDIT2 = {
    "PRODUCT_SAVE_BUTTON": (1550, 990),   # 상품수정 전체 저장 버튼
    "PRODUCT_HTMLSOURCE_OPEN": (1080, 385),  # HTML 삽입 버튼 클릭
    "PRODUCT_HTMLSOURCE_TEXTAREA": (900, 500),  # HTML 삽입 TEXTAREA 클릭    
    "PRODUCT_HTMLSOURCE_SAVE": (1225, 460),  # HTML 삽입 저장 버튼 클릭       
    "PRODUCT_UPLOADEDIT_2ndINPUT": (680, 710),  # 상품정보고시 섹션에서 두번째 입력창 선택     
    "PRODUCT_NAMEEDIT_TEXTAREA": (1100, 320)   # 상품명 TEXTAREA 클릭    
}

# 상품수정 가격탭 좌표
PRODUCT_PRICE_TAB = {
    "PRODUCT_PRICE_DISCOUNTRATE": (410, 495)   # 마켓표기할인율 TEXTAREA 클릭
}

# 상품수정 모달창 닫기 좌표
PRODUCT_MODAL_CLOSE = {
    "PRODUCT_MODAL_CLOSE": (1580, 120),     # 상품수정 모달창 닫기
}

# 상세페이지 편집 좌표
PRODUCT_DETAIL_EDIT = {
    "PRODUCT_DETAIL_OPENEDIT": (500, 250),     # 일괄편집 모달창 열기 좌표
    "PRODUCT_DETAIL_DELIMAGE_1": (562, 503),     # 첫번째 이미지 삭제 좌표
    "PRODUCT_DETAIL_DELIMAGE_2": (1071, 958),     # 마지막 이미지 삭제 좌표
    "PRODUCT_DETAIL_PAGEDOWN": (1430, 960),     # 일관편집 모달창 PAGEDOWN
    "PRODUCT_DETAIL_PAGEUP": (1430, 170),     # 일관편집 모달창 PAGEUP
    "PRODUCT_DETAIL_EDITIMAGE": (650, 503),     # 일관편집 이미지 편집 모달창 열기    
    "PRODUCT_DETAIL_EDITIMAGE_SAVE": (1737, 116),     # 일관편집 이미지 편집 저장        
    "PRODUCT_DETAIL_CLOSEEDIT": (1400, 110),     # 일괄편집 모달창 닫기 좌표    
}

# 메모편집 모달창 좌표
PRODUCT_MEMO_MODAL = {    
    "MEMO_MODAL_CLOSE": (1560, 167),     # 상품목록에 메모내용 숨기기
    "MEMO_MODAL_OPEN": (1560, 910),     # 메모편집 모달창 열기
    "MEMO_MODAL_TEXTAREA": (935, 520),     # 메모편집 TEXTAREA 선택
    "MEMO_MODAL_CHECKBOX": (580, 745),     # 상품목록에 메모내용 노출하기
    "MEMO_MODAL_SAVEBUTTON": (1255, 785),     # 메모편집 저장후 닫기
}
