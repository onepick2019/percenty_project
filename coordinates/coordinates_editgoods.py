"""
상품 수정 모달창에서 사용하는 절대좌표 정의 파일
좌표 값은 ui_elements.py에서 하이브리드 방식으로 사용됩니다.
"""

# 딜레이 시간 상수를 timesleep.py에서 임포트
from timesleep import (
    DELAY_VERY_SHORT2,
    DELAY_VERY_SHORT5,
    DELAY_VERY_SHORT,
    DELAY_SHORT,
    DELAY_MEDIUM,
    DELAY_LONG,
    DELAY_EXTRA_LONG as DELAY_VERY_LONG  # 이름 변경된 상수 매핑
)

# 좌표 변환 함수 임포트
from .coordinate_conversion import convert_coordinates

# 1. 상품수정 모달창 탭 좌표
PRODUCT_MODAL_TAB = {
    "PRODUCT_TAB_BASIC": (400, 120),     # 상품명/카테고리 탭
    "PRODUCT_TAB_OPTION": (490, 120),    # 옵션 탭
    "PRODUCT_TAB_PRICE": (545, 120),     # 가격 탭
    "PRODUCT_TAB_KEYWORD": (610, 120),   # 키워드 탭
    "PRODUCT_TAB_THUMBNAIL": (680, 120), # 썸네일 탭
    "PRODUCT_TAB_DETAIL": (760, 120),    # 상세페이지 탭
    "PRODUCT_TAB_UPLOAD": (845, 120)     # 업로드 탭
}

# 2. 상품수정시 사용하는 좌표(상대좌표 사용)
PRODUCT_MODAL_EDIT1 = {
    "PRODUCT_FIRST_GOODS": (700, 660),  # 그룹상품관리에서 첫번째 상품 모달창 열기
    "MEMO_MODAL_CLOSE": (1560, 167),     # 상품목록에 메모내용 숨기기        
    "PRODUCT_ALERTWORDS_DEL1": (820, 395),   # 상품명 경고단어 및 중복단어 삭제 클릭    
    "PRODUCT_ALERTWORDS_DEL2": (770, 395),   # 상품명 경고단어 및 중복단어 삭제 클릭
    "PRODUCT_ALERTWORDS_DEL3": (740, 395),   # 상품명 경고단어 및 중복단어 삭제 클릭
    "PRODUCT_ALERTWORDS_DEL4": (710, 395),   # 상품명 경고단어 및 중복단어 삭제 클릭 
    "PRODUCT_ALERTWORDS_DEL5": (680, 395),   # 상품명 경고단어 및 중복단어 삭제 클릭 
    "PRODUCT_ALERTWORDS_DEL6": (640, 395)   # 상품명 경고단어 및 중복단어 삭제 클릭 
}

# 3. 상품수정시 사용하는 좌표(하이브리드 사용)
PRODUCT_MODAL_EDIT2 = {
    "PRODUCT_SAVE_BUTTON": (1550, 990),   # 상품수정 전체 저장 버튼
    "PRODUCT_HTMLSOURCE_OPEN": (1080, 385),  # HTML 삽입 버튼 클릭
    "PRODUCT_HTMLSOURCE_TEXTAREA": (900, 500),  # HTML 삽입 TEXTAREA 클릭    
    "PRODUCT_HTMLSOURCE_SAVE": (1225, 460),  # HTML 삽입 저장 버튼 클릭       
    "PRODUCT_SOURCE_BUTTON": (1130, 390),  # 소스 버튼 클릭       
    "PRODUCT_INFO_DISCLOSURE": (800, 430),  # 상품정보고시 섹션 클릭, 열기 및 닫기 공용    
    "PRODUCT_UPLOADEDIT_2ndINPUT": (680, 710),  # 상품정보고시 섹션에서 두번째 입력창 선택     
    "PRODUCT_NAMEEDIT_TEXTAREA": (1100, 320),   # 상품명 TEXTAREA 클릭
    "PRODUCT_COPY_ITEM": (855, 990),   # 상품복사하기    
    "PRODUCT_VIEW_NOGROUP": (470, 320)   # 비그룹상품보기 토글
}

# 4. 상품수정 옵션탭 좌표
PRODUCT_OPTION_TAB = {
    "PRODUCT_OPTION_AI": (940, 297),   # 옵션명 AI 다듬기 클릭
    "PRODUCT_OPTION_NUMBER": (482, 488)   # 옵션명 접두어로 숫자 추가 클릭
}

# 5. 상품수정 가격탭 좌표 (상대좌표 적용)
# 기준 해상도: 1920x1080, 브라우저 내부 크기: 1903x971
_base_coords = convert_coordinates(410, 495, 1903, 971)
PRODUCT_PRICE_TAB = {
    "PRODUCT_PRICE_DISCOUNTRATE1": (410, 495),   # 옵션명 접두어로 숫자 추가 클릭    
    "PRODUCT_PRICE_DISCOUNTRATE": _base_coords   # 마켓표기할인율 TEXTAREA 클릭 (상대좌표)
}

# 6. 상품수정 모달창 닫기 좌표(Esc 키로 닫기)
# 상품수정의 모든 모달창 닫기는 Esc 키로 닫기 가능함
PRODUCT_MODAL_CLOSE = {
    "PRODUCT_MODAL_CLOSE": (1580, 120),     # 상품수정 모달창 닫기
    "PRODUCT_DETAIL_CLOSEEDIT": (1400, 110)     # 일괄편집 모달창 닫기 좌표        
}

# 7. 상세페이지 편집 좌표(상대좌표 사용)
# image_utils.py 에서 정의한 DOM 선택자를 이용하므로, 참고용으로 좌표를 남겨둘
PRODUCT_DETAIL_EDIT = {
    "PRODUCT_DETAIL_OPENEDIT": (500, 250),     # 일괄편집 모달창 열기 좌표
    "MEMO_MODAL_SAVEBUTTON": (1255, 785),     # 메모편집 저장후 닫기        
    "PRODUCT_DETAIL_DELIMAGE_1": (562, 503),     # 첫번째 이미지 삭제 좌표
    "PRODUCT_DETAIL_DELIMAGE_2": (1071, 958),     # 마지막 이미지 삭제 좌표
    "PRODUCT_DETAIL_PAGEDOWN": (1430, 960),     # 일관편집 모달창 PAGEDOWN(정확하지 않음)
    "PRODUCT_DETAIL_PAGEUP": (1430, 170),     # 일관편집 모달창 PAGEUP(정확하지 않음)
    "PRODUCT_DETAIL_EDITIMAGE": (650, 503),     # 일관편집 이미지 편집 모달창 열기    
    "PRODUCT_DETAIL_EDITIMAGE_SAVE": (1737, 116)     # 일관편집 이미지번역 모달창 닫기        
}

# 8.메모편집 모달창 좌표
PRODUCT_MEMO_MODAL = {    
    "MEMO_MODAL_OPEN": (1560, 910),     # 메모편집 모달창 열기
    "MEMO_MODAL_TEXTAREA": (935, 520),     # 메모편집 TEXTAREA 선택
    "MEMO_MODAL_CHECKBOX": (580, 745)     # 상품목록에 메모 내용 노출하기(CHECKBOX)
}

# 9. 등록상품관리 필요한 좌표표
MANAGE_REGISTER_VIEW = {
    "REGISTER_FIRST_GOODS": (700, 940),  # 등록상품관리에서 첫번째 상품 모달창 열기
    "SEARCH_NAME_INPUT": (1140, 700),   # 등록상품관리 상품명 인풋창
    "SELECT_ALL_CHECKBOX": (312, 862),    # 등록상품관리 전체선택 체크박스
    "THUMBNAIL_CLICK_CENTER": (930, 650)    # 썸네일탭 중앙 클릭(포커스용)   
}