"""
상품 수정에 필요한 절대좌표 정의 파일
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

# 상품수정시 사용하는 좌표
PRODUCT_MODAL_EDIT = {
    "PRODUCT_SAVE_BUTTON": (1550, 990),   # 상품수정 전체 저장 버튼
    "PRODUCT_VIEW_NOGROUP": (470, 320),  # 비그룹상품보기/그룹상품보기 토글 버튼
    "PRODUCT_FIRST_GOODS": (700, 650),  # 첫번째 상품 모달창 열기
    "PRODUCT_FIRST_GOODS_CHECKBOX": (312, 682),  # 첫번째 상품 CHECKBOX 클릭
    "PRODUCT_SELECT_GOODS_ALL": (312, 565),  # 전체상품 CHECKBOX 클릭    
    "PRODUCT_HTMLSOURCE_OPEN": (1080, 385),  # HTML 삽입 버튼 클릭
    "PRODUCT_HTMLSOURCE_TEXTAREA": (900, 500),  # HTML 삽입 TEXTAREA 클릭
    "PRODUCT_HTMLSOURCE_SAVE": (1225, 460),  # HTML 삽입 저장 버튼 클릭        
    "PRODUCT_UPLOADEDIT_SELECT": (800, 430),  # 상품정보고시 섹션 클릭, 열기 및 닫기 공용
    "PRODUCT_UPLOADEDIT_2ndINPUT": (760, 718),  # 상품정보고시 섹션에서 두번째 입력창 선택
    "PRODUCT_ALERTWORDS_DEL1": (820, 395),   # 상품명 경고단어 및 중복단어 삭제 클릭    
    "PRODUCT_ALERTWORDS_DEL2": (770, 395),   # 상품명 경고단어 및 중복단어 삭제 클릭
    "PRODUCT_ALERTWORDS_DEL3": (740, 395),   # 상품명 경고단어 및 중복단어 삭제 클릭
    "PRODUCT_ALERTWORDS_DEL4": (710, 395),   # 상품명 경고단어 및 중복단어 삭제 클릭 
    "PRODUCT_ALERTWORDS_DEL5": (680, 395),   # 상품명 경고단어 및 중복단어 삭제 클릭 
    "PRODUCT_ALERTWORDS_DEL6": (640, 395),   # 상품명 경고단어 및 중복단어 삭제 클릭 
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

# 그룹 선택 좌표
PRODUCT_SELECT_GROUP = {
    "PRODUCT_SELECT_GROUP1": (680, 320),     # 그룹상품관리에서 선택 그룹1 신규수집
    "PRODUCT_SELECT_GROUP2": (775, 320),     # 그룹상품관리에서 선택 그룹2 번역대기
    "PRODUCT_SELECT_GROUP3": (880, 320),     # 그룹상품관리에서 선택 그룹3 등록실행
    "PRODUCT_SELECT_GROUP4": (960, 320),     # 그룹상품관리에서 선택 그룹4 등록A
    "PRODUCT_SELECT_GROUP5": (1050, 320),     # 그룹상품관리에서 선택 그룹5 등록B   
    "PRODUCT_SELECT_GROUP6": (1125, 320),     # 그룹상품관리에서 선택 그룹6 등록C
    "PRODUCT_SELECT_GROUP7": (1205, 320),     # 그룹상품관리에서 선택 그룹7 등록D
    "PRODUCT_SELECT_GROUP8": (1300, 320),     # 그룹상품관리에서 선택 그룹8 쇼핑몰T
    "PRODUCT_SELECT_GROUP9": (1395, 320),     # 그룹상품관리에서 선택 그룹9 쇼핑몰A1 
    "PRODUCT_SELECT_GROUP10": (1490, 320),     # 그룹상품관리에서 선택 그룹10 쇼핑몰A2
    "PRODUCT_SELECT_GROUP11": (1595, 320),     # 그룹상품관리에서 선택 그룹11 쇼핑몰A3
    "PRODUCT_SELECT_GROUP12": (1695, 320),     # 그룹상품관리에서 선택 그룹12 쇼핑몰B1
    "PRODUCT_SELECT_GROUP13": (1788, 320),     # 그룹상품관리에서 선택 그룹13 쇼핑몰B2
    "PRODUCT_SELECT_GROUP14": (610, 353),     # 그룹상품관리에서 선택 그룹14 쇼핑몰B3
    "PRODUCT_SELECT_GROUP15": (715, 353),     # 그룹상품관리에서 선택 그룹15 쇼핑몰C1
    "PRODUCT_SELECT_GROUP16": (817, 353),     # 그룹상품관리에서 선택 그룹16 쇼핑몰C2
    "PRODUCT_SELECT_GROUP17": (924, 353),     # 그룹상품관리에서 선택 그룹17 쇼핑몰C3
    "PRODUCT_SELECT_GROUP18": (1020, 353),     # 그룹상품관리에서 선택 그룹18 쇼핑몰D1   
    "PRODUCT_SELECT_GROUP19": (1120, 353),     # 그룹상품관리에서 선택 그룹19 쇼핑몰D2
    "PRODUCT_SELECT_GROUP20": (1225, 353),     # 그룹상품관리에서 선택 그룹20 쇼핑몰D3
    "PRODUCT_SELECT_GROUP21": (1320, 353),     # 그룹상품관리에서 선택 그룹21 완료A1
    "PRODUCT_SELECT_GROUP22": (1410, 353),     # 그룹상품관리에서 선택 그룹22 완료A2 
    "PRODUCT_SELECT_GROUP23": (1496, 353),     # 그룹상품관리에서 선택 그룹23 완료A3
    "PRODUCT_SELECT_GROUP24": (1590, 353),     # 그룹상품관리에서 선택 그룹24 완료B1
    "PRODUCT_SELECT_GROUP25": (1672, 353),     # 그룹상품관리에서 선택 그룹25 완료B2
    "PRODUCT_SELECT_GROUP26": (1767, 353),     # 그룹상품관리에서 선택 그룹26 완료B3    
    "PRODUCT_SELECT_GROUP27": (610, 381),     # 그룹상품관리에서 선택 그룹27 완료C1
    "PRODUCT_SELECT_GROUP28": (695, 381),     # 그룹상품관리에서 선택 그룹28 완료C2
    "PRODUCT_SELECT_GROUP29": (784, 381),     # 그룹상품관리에서 선택 그룹29 완료C3
    "PRODUCT_SELECT_GROUP30": (878, 381),     # 그룹상품관리에서 선택 그룹30 완료D1   
    "PRODUCT_SELECT_GROUP31": (966, 381),     # 그룹상품관리에서 선택 그룹31 완료D2
    "PRODUCT_SELECT_GROUP32": (1050, 381),     # 그룹상품관리에서 선택 그룹32 완료D3
    "PRODUCT_SELECT_GROUP33": (1150, 381),     # 그룹상품관리에서 선택 그룹33 수동번역
    "PRODUCT_SELECT_GROUP34": (1245, 381),     # 그룹상품관리에서 선택 그룹34 등록대기 
    "PRODUCT_SELECT_GROUP35": (1340, 381),     # 그룹상품관리에서 선택 그룹35 번역검수
    "PRODUCT_SELECT_GROUP36": (1425, 381),     # 그룹상품관리에서 선택 그룹36 서버1
    "PRODUCT_SELECT_GROUP37": (1508, 381),     # 그룹상품관리에서 선택 그룹37 서버2
    "PRODUCT_SELECT_GROUP38": (1584, 381),     # 그룹상품관리에서 선택 그룹38 서버3    
    "PRODUCT_SELECT_GROUP39": (1670, 381),     # 그룹상품관리에서 선택 그룹39 대기1    
    "PRODUCT_SELECT_GROUP40": (1750, 381),     # 그룹상품관리에서 선택 그룹40 대기2     
    "PRODUCT_SELECT_GROUP41": (606, 413),     # 그룹상품관리에서 선택 그룹41 대기3
    "PRODUCT_SELECT_GROUP42": (683, 413),     # 그룹상품관리에서 선택 그룹42 수동1
    "PRODUCT_SELECT_GROUP43": (765, 413),     # 그룹상품관리에서 선택 그룹43 수동2
    "PRODUCT_SELECT_GROUP44": (843, 413),     # 그룹상품관리에서 선택 그룹44 수동3   
    "PRODUCT_SELECT_GROUP45": (920, 413),     # 그룹상품관리에서 선택 그룹45 검수1
    "PRODUCT_SELECT_GROUP46": (1003, 413),     # 그룹상품관리에서 선택 그룹46 검수2
    "PRODUCT_SELECT_GROUP47": (1081, 413),     # 그룹상품관리에서 선택 그룹47 검수3
    "PRODUCT_SELECT_GROUP48": (1157, 413),     # 그룹상품관리에서 선택 그룹48 복제X 
    "PRODUCT_SELECT_GROUP49": (1234, 413),     # 그룹상품관리에서 선택 그룹49 삭제X
    "PRODUCT_SELECT_GROUP50": (1323, 413),     # 그룹상품관리에서 선택 그룹50 중복X          
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
