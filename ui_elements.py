"""
퍼센티 UI 요소 통합 정의 파일 (ui_elements.py)
DOM 선택자와 좌표를 함께 관리하여 하이브리드 접근 방식 지원
"""

# DOM 선택자와 좌표 모듈 가져오기
from dom_selectors import MENU_SELECTORS, EDITGOODS_SELECTORS, LOGIN_SELECTORS
# 좌표 변환 함수 임포트
from coordinates.coordinate_conversion import convert_coordinates
# 산선한 코드를 위해 일관된 변수명만 사용
# 이전에는 PRODUCT_EDIT_SELECTORS와 EDITGOODS_SELECTORS가 혼용되었지만, 현재는 EDITGOODS_SELECTORS만 사용하도록 통일
# 모든 좌표는 coordinates_all에서 중앙 관리
from coordinates.coordinates_all import (
    MENU,
    PRODUCT,
    GROUP,
    PRODUCT_FORM_ELEMENTS,
    MODAL,
    PRODUCT_OPTION_TAB,
    PRODUCT_PRICE_TAB,
    PRODUCT_MODAL_CLOSE,
    PRODUCT_DETAIL_EDIT,
    PRODUCT_MEMO_MODAL,
    PRODUCT_MODAL_TAB,
    PRODUCT_MODAL_EDIT1,
    PRODUCT_MODAL_EDIT2
)
# 등록상품관리 화면 좌표 가져오기
from coordinates.coordinates_editgoods import MANAGE_REGISTER_VIEW
# 로그인 관련 좌표 가져오기
from coordinates.coordinates_login import LOGIN, NOTIFICATION, LOGIN_MODAL
# 시간 지연 모듈 가져오기
from timesleep import (KEYBOARD_ACTION, DELAY_SHORT, DELAY_VERY_SHORT, DELAY_MEDIUM, 
                      DELAY_STANDARD, DELAY_LONG, DELAY_VERY_SHORT2, DELAY_VERY_SHORT5,
                      BUTTON_CLICK, MODAL, CHECKBOX)

# 키보드 액션 정의
KEYBOARD_ACTIONS = {
    "escape_key": {
        "key": "escape",
        "description": "모달창 닫기 (ESC 키)",
        "delay": KEYBOARD_ACTION["AFTER_ESC"]
    },
    "tab_key": {
        "key": "tab",
        "description": "다음 요소로 이동 (TAB 키)",
        "delay": KEYBOARD_ACTION["AFTER_TAB"]
    },
    "page_down_key": {
        "key": "page_down",
        "description": "페이지 아래로 스크롤 (PAGE DOWN 키)",
        "delay": KEYBOARD_ACTION["AFTER_KEY"]
    },
    "page_up_key": {
        "key": "page_up", 
        "description": "페이지 위로 스크롤 (PAGE UP 키)",
        "delay": KEYBOARD_ACTION["AFTER_KEY"]
    },
}

# 로그인 화면 UI 요소 정의 - DOM 선택자와 좌표 통합
LOGIN_UI_ELEMENTS = {
    # 아이디/이메일 입력 필드
    "USERNAME_FIELD": {
        "name": "이메일/아이디 입력 필드",
        "dom_selector": LOGIN_SELECTORS["USERNAME_FIELD"],
        "selector_type": "xpath",
        "coordinates": LOGIN["USERNAME_FIELD"],
        "fallback_order": ["dom", "coordinates"]
    },    
    # 비밀번호 입력 필드
    "PASSWORD_FIELD": {
        "name": "비밀번호 입력 필드",
        "dom_selector": LOGIN_SELECTORS["PASSWORD_FIELD"],
        "selector_type": "xpath",
        "coordinates": LOGIN["PASSWORD_FIELD"],
        "fallback_order": ["dom", "coordinates"]
    },  
    # 아이디 저장 체크박스
    "SAVE_ID_CHECKBOX": {
        "name": "아이디 저장 체크박스",
        "dom_selector": LOGIN_SELECTORS["SAVE_ID_CHECKBOX"],
        "selector_type": "xpath",
        "coordinates": LOGIN["SAVE_ID_CHECKBOX"],
        "fallback_order": ["dom", "coordinates"]
    },  
    # 로그인 버튼
    "LOGIN_BUTTON": {
        "name": "로그인 버튼",
        "dom_selector": LOGIN_SELECTORS["LOGIN_BUTTON"],
        "selector_type": "xpath",
        "coordinates": LOGIN["LOGIN_BUTTON"],
        "fallback_order": ["dom", "coordinates"]
    },  
    # 다시 보지 않기 버튼 (모달창)
    "DONT_SHOW_AGAIN": {
        "name": "다시 보지 않기 버튼 (모달창)",
        "dom_selector": LOGIN_SELECTORS["DONT_SHOW_AGAIN"],
        "selector_type": "xpath",
        "coordinates": LOGIN_MODAL["DONT_SHOW_AGAIN"],
        "fallback_order": ["dom", "coordinates"]
    },
    # 알림 닫기 버튼
    "NOTIFICATION_CLOSE": {
        "name": "알림 닫기 버튼",
        "dom_selector": "",  # DOM 선택자 없음
        "selector_type": "xpath",
        "coordinates": NOTIFICATION["CLOSE"],
        "fallback_order": ["coordinates"]
    }
}

# 모든 UI 요소를 통합한 딕셔너리
UI_ELEMENTS = {
    # ===== 로그인 화면 관련 요소 =====
    # 아이디/이메일 입력 필드
    "LOGIN_EMAIL_FIELD": LOGIN_UI_ELEMENTS["USERNAME_FIELD"],
    "LOGIN_USERNAME_FIELD": LOGIN_UI_ELEMENTS["USERNAME_FIELD"],
    
    # 비밀번호 입력 필드
    "LOGIN_PASSWORD_FIELD": LOGIN_UI_ELEMENTS["PASSWORD_FIELD"],
    
    # 아이디 저장 체크박스
    "LOGIN_SAVE_ID_CHECKBOX": LOGIN_UI_ELEMENTS["SAVE_ID_CHECKBOX"],
    
    # 로그인 버튼
    "LOGIN_BUTTON": LOGIN_UI_ELEMENTS["LOGIN_BUTTON"],
    
    # 다시 보지 않기 버튼
    "MODAL_DONT_SHOW_AGAIN": LOGIN_UI_ELEMENTS["DONT_SHOW_AGAIN"],
    
    # 알림창 닫기 버튼
    "NOTIFICATION_CLOSE": LOGIN_UI_ELEMENTS["NOTIFICATION_CLOSE"],
    
    # ===== 키보드 액션 관련 요소 =====
    "enter_key": {
        "key": "enter",
        "description": "확인/제출 (ENTER 키)",
        "delay": KEYBOARD_ACTION["AFTER_ENTER"]
    }
}

# 메뉴 관련 UI 요소 (DOM 선택자 + 좌표)
MENU_ELEMENTS = {
    # 퍼센티 홈 및 캘린더 메뉴
    "HOME": {
        "name": "퍼센티 홈",
        "dom_selector": MENU_SELECTORS["HOME"],
        "selector_type": "xpath",
        "coordinates": MENU["HOME"],
        "fallback_order": ["dom", "coordinates"]
    },
    "PRODUCT_CALENDAR": {
        "name": "셀러 캘린더",
        "dom_selector": MENU_SELECTORS["PRODUCT_CALENDAR"],
        "selector_type": "xpath",
        "coordinates": MENU["PRODUCT_CALENDAR"],
        "fallback_order": ["dom", "coordinates"]
    },
    
    # 상품 관리 서브 메뉴
    "PRODUCT_AISOURCING": {
        "name": "AI 소싱",
        "dom_selector": MENU_SELECTORS["PRODUCT_AISOURCING"],
        "selector_type": "xpath",
        "coordinates": MENU["PRODUCT_AISOURCING"],
        "fallback_order": ["dom", "coordinates"]
    },
    "PRODUCT_REGISTER": {
        "name": "신규상품등록",
        "dom_selector": MENU_SELECTORS["PRODUCT_REGISTER"],
        "selector_type": "xpath",
        "coordinates": MENU["PRODUCT_REGISTER"],
        "fallback_order": ["dom", "coordinates"]
    },
    "PRODUCT_MANAGE": {
        "name": "등록상품관리",
        "dom_selector": MENU_SELECTORS["PRODUCT_MANAGE"],
        "selector_type": "xpath",
        "coordinates": MENU["PRODUCT_MANAGE"],
        "fallback_order": ["dom", "coordinates"]
    },
    "PRODUCT_GROUP": {
        "name": "그룹상품관리",
        "dom_selector": MENU_SELECTORS["PRODUCT_GROUP"],
        "selector_type": "xpath",
        "coordinates": MENU["PRODUCT_GROUP"],
        "fallback_order": ["dom", "coordinates"]
    },
    
    # 주문관리 서브 메뉴
    "ORDER_MANAGE": {
        "name": "상품주문관리",
        "dom_selector": MENU_SELECTORS["ORDER_MANAGE"],
        "selector_type": "xpath",
        "coordinates": MENU["ORDER_MANAGE"],
        "fallback_order": ["dom", "coordinates"]
    },
    "ORDER_CUSTOMER": {
        "name": "고객문의관리",
        "dom_selector": MENU_SELECTORS["ORDER_CUSTOMER"],
        "selector_type": "xpath",
        "coordinates": MENU["ORDER_CUSTOMER"],
        "fallback_order": ["dom", "coordinates"]
    },
    "ORDER_CUSTOMS": {
        "name": "통관고유번호조회",
        "dom_selector": MENU_SELECTORS["ORDER_CUSTOMS"],
        "selector_type": "xpath",
        "coordinates": MENU["ORDER_CUSTOMS"],
        "fallback_order": ["dom", "coordinates"]
    },
    
    # 배송관리 및 통계 메뉴
    "DELIVERY_AGENCY": {
        "name": "배송대행지",
        "dom_selector": MENU_SELECTORS["DELIVERY_AGENCY"],
        "selector_type": "xpath",
        "coordinates": MENU["DELIVERY_AGENCY"],
        "fallback_order": ["dom", "coordinates"]
    },
    "PERCENTY_ANALYTICS": {
        "name": "퍼센티 애널리틱스",
        "dom_selector": MENU_SELECTORS["PERCENTY_ANALYTICS"],
        "selector_type": "xpath",
        "coordinates": MENU["PERCENTY_ANALYTICS"],
        "fallback_order": ["dom", "coordinates"]
    },
    "PURCHASE_LEDGER": {
        "name": "구매대행장부",
        "dom_selector": MENU_SELECTORS["PURCHASE_LEDGER"],
        "selector_type": "xpath",
        "coordinates": MENU["PURCHASE_LEDGER"],
        "fallback_order": ["dom", "coordinates"]
    },
    "PERCENTY_SCHOOL": {
        "name": "퍼센티 스쿨",
        "dom_selector": MENU_SELECTORS["PERCENTY_SCHOOL"],
        "selector_type": "xpath",
        "coordinates": MENU["PERCENTY_SCHOOL"],
        "fallback_order": ["dom", "coordinates"]
    }
}

# 상품 수정 모달창 UI 요소 정의
PRODUCT_EDIT_ELEMENTS = {
    # 모달창 탭 선택자
    "PRODUCT_TAB_BASIC": {
        "name": "상품명/카테고리 탭",
        "dom_selector": EDITGOODS_SELECTORS["PRODUCT_TAB_BASIC"],
        "selector_type": "xpath",
        "coordinates": PRODUCT_MODAL_TAB["PRODUCT_TAB_BASIC"],
        "fallback_order": ["dom", "coordinates"]
    },
    "PRODUCT_TAB_OPTION": {
        "name": "옵션 탭",
        "dom_selector": EDITGOODS_SELECTORS["PRODUCT_TAB_OPTION"],
        "selector_type": "xpath",
        "coordinates": PRODUCT_MODAL_TAB["PRODUCT_TAB_OPTION"],
        "fallback_order": ["dom", "coordinates"]
    },
    "PRODUCT_TAB_PRICE": {
        "name": "가격 탭",
        "dom_selector": EDITGOODS_SELECTORS["PRODUCT_TAB_PRICE"],
        "selector_type": "xpath",
        "coordinates": PRODUCT_MODAL_TAB["PRODUCT_TAB_PRICE"],
        "fallback_order": ["dom", "coordinates"]
    },
    "PRODUCT_TAB_KEYWORD": {
        "name": "키워드 탭",
        "dom_selector": EDITGOODS_SELECTORS["PRODUCT_TAB_KEYWORD"],
        "selector_type": "xpath",
        "coordinates": PRODUCT_MODAL_TAB["PRODUCT_TAB_KEYWORD"],
        "fallback_order": ["dom", "coordinates"]
    },
    "PRODUCT_TAB_THUMBNAIL": {
        "name": "썸네일 탭",
        "dom_selector": EDITGOODS_SELECTORS["PRODUCT_TAB_THUMBNAIL"],
        "selector_type": "xpath",
        "coordinates": PRODUCT_MODAL_TAB["PRODUCT_TAB_THUMBNAIL"],
        "fallback_order": ["dom", "coordinates"]
    },
    "PRODUCT_TAB_DETAIL": {
        "name": "상세페이지 탭",
        "dom_selector": EDITGOODS_SELECTORS["PRODUCT_TAB_DETAIL"],
        "selector_type": "xpath",
        "coordinates": PRODUCT_MODAL_TAB["PRODUCT_TAB_DETAIL"],
        "fallback_order": ["dom", "coordinates"]
    },
    "PRODUCT_TAB_UPLOAD": {
        "name": "업로드 탭",
        "dom_selector": EDITGOODS_SELECTORS["PRODUCT_TAB_UPLOAD"],
        "selector_type": "xpath",
        "coordinates": PRODUCT_MODAL_TAB["PRODUCT_TAB_UPLOAD"],
        "fallback_order": ["dom", "coordinates"],
        "active_class": "ant-tabs-tab-active"
    },
    
    # 옵션 탭 요소
    "PRODUCT_OPTION_AI": {
        "name": "옵션명 AI 다듬기 버튼",
        "dom_selector": EDITGOODS_SELECTORS["PRODUCT_OPTION_AI"],
        "selector_type": "xpath",
        "coordinates": PRODUCT_OPTION_TAB["PRODUCT_OPTION_AI"],
        "fallback_order": ["dom", "coordinates"]
    },
    "PRODUCT_OPTION_NUMBER": {
        "name": "옵션명 접두어로 숫자 추가 버튼",
        "dom_selector": EDITGOODS_SELECTORS["PRODUCT_OPTION_NUMBER"],
        "selector_type": "xpath",
        "coordinates": PRODUCT_OPTION_TAB["PRODUCT_OPTION_NUMBER"],
        "fallback_order": ["dom", "coordinates"]
    },

    "PRODUCT_PRICE_DISCOUNTRATE1": {
        "name": "옵션명 접두어로 숫자 추가 버튼",
        "dom_selector": EDITGOODS_SELECTORS["PRODUCT_PRICE_DISCOUNTRATE1"],
        "selector_type": "xpath",
        "coordinates": PRODUCT_PRICE_TAB["PRODUCT_PRICE_DISCOUNTRATE1"],
        "fallback_order": ["dom", "coordinates"]
    },

    # 가격 탭 요소 (상대좌표 적용)
    "PRODUCT_PRICE_DISCOUNTRATE": {
        "name": "마켓표기할인율 입력창",
        "dom_selector": EDITGOODS_SELECTORS["PRODUCT_PRICE_DISCOUNTRATE"],
        "selector_type": "xpath",
        "coordinates": convert_coordinates(PRODUCT_PRICE_TAB["PRODUCT_PRICE_DISCOUNTRATE"][0], PRODUCT_PRICE_TAB["PRODUCT_PRICE_DISCOUNTRATE"][1], 1903, 971),
        "fallback_order": ["dom", "coordinates"]
    },
    
    # 상품 수정 기본 요소
    "PRODUCT_SAVE_BUTTON": {
        "name": "상품수정 전체 저장 버튼",
        "dom_selector": EDITGOODS_SELECTORS["PRODUCT_SAVE_BUTTON"],
        "selector_type": "xpath",
        "coordinates": PRODUCT_MODAL_EDIT2["PRODUCT_SAVE_BUTTON"],
        "fallback_order": ["dom", "coordinates"]
    },
    "PRODUCT_NAMEEDIT_TEXTAREA": {
        "name": "상품명 TEXTAREA",
        "dom_selector": EDITGOODS_SELECTORS["PRODUCT_NAMEEDIT_TEXTAREA"],
        "selector_type": "xpath",
        "coordinates": PRODUCT_MODAL_EDIT2["PRODUCT_NAMEEDIT_TEXTAREA"],
        "fallback_order": ["dom", "coordinates"]
    },
    "PRODUCT_VIEW_NOGROUP": {
        "name": "비그룹상품보기 토글 버튼",
        "dom_selector": EDITGOODS_SELECTORS["PRODUCT_VIEW_NOGROUP"],
        "selector_type": "xpath",
        "coordinates": PRODUCT_MODAL_EDIT2["PRODUCT_VIEW_NOGROUP"],
        "fallback_order": ["dom", "coordinates"]
    },   
    "PRODUCT_FIRST_GOODS": {
        "name": "첫번째 상품 모달창 열기",
        "dom_selector": None,
        "selector_type": None,
        "coordinates": PRODUCT_MODAL_EDIT1["PRODUCT_FIRST_GOODS"],
        "fallback_order": ["coordinates"]
    },
    "MEMO_MODAL_CLOSE": {
        "name": "상품목록에 메모내용 숨기기",
        "dom_selector": None,  # DOM 선택자로는 타겟팅이 어려움
        "selector_type": None,
        "coordinates": PRODUCT_MODAL_EDIT1["MEMO_MODAL_CLOSE"],
        "fallback_order": ["coordinates"]  # 좌표만 사용
    },

    # HTML 소스 편집 요소
    "PRODUCT_HTMLSOURCE_OPEN": {
        "name": "HTML 삽입 버튼 클릭",
        "dom_selector": EDITGOODS_SELECTORS["PRODUCT_HTMLSOURCE_OPEN"],
        "selector_type": "xpath",
        "coordinates": PRODUCT_MODAL_EDIT2["PRODUCT_HTMLSOURCE_OPEN"],
        "fallback_order": ["dom", "coordinates"]
    },
    "PRODUCT_HTMLSOURCE_TEXTAREA": {
        "name": "HTML 삽입 TEXTAREA 클릭",
        "dom_selector": EDITGOODS_SELECTORS["PRODUCT_HTMLSOURCE_TEXTAREA"],
        "selector_type": "xpath",
        "coordinates": PRODUCT_MODAL_EDIT2["PRODUCT_HTMLSOURCE_TEXTAREA"],
        "fallback_order": ["dom", "coordinates"]
    },
    "PRODUCT_UPLOADEDIT_2ndINPUT": {
        "name": "상품정보고시 섹션 두번째 입력창",
        "dom_selector": None,  # DOM 선택자로는 타겟팅이 어려움
        "selector_type": None,
        "coordinates": PRODUCT_MODAL_EDIT2["PRODUCT_UPLOADEDIT_2ndINPUT"],
        "fallback_order": ["coordinates"]  # 좌표만 사용
    },
    "PRODUCT_INFO_DISCLOSURE": {
        "name": "상품정보제공고시 섹션",
        "dom_selector": EDITGOODS_SELECTORS["PRODUCT_INFO_DISCLOSURE"],
        "selector_type": "xpath",
        "coordinates": PRODUCT_MODAL_EDIT2["PRODUCT_INFO_DISCLOSURE"],
        "fallback_order": ["dom", "coordinates"]  # DOM 선택자 우선, 실패 시 좌표 사용
    }, 
    "PRODUCT_HTMLSOURCE_SAVE": {
        "name": "HTML 삽입 저장 버튼 클릭",
        "dom_selector": EDITGOODS_SELECTORS["PRODUCT_HTMLSOURCE_SAVE"],
        "selector_type": "xpath",
        "coordinates": PRODUCT_MODAL_EDIT2["PRODUCT_HTMLSOURCE_SAVE"],
        "fallback_order": ["dom", "coordinates"]  # DOM 선택자 우선, 실패 시 좌표 사용
    }, 
    # 모달창 닫기 요소
    "PRODUCT_MODAL_CLOSE": {
        "name": "상품수정 모달창 닫기",
        "dom_selector": EDITGOODS_SELECTORS["PRODUCT_MODAL_CLOSE"],
        "selector_type": "xpath",
        "coordinates": PRODUCT_MODAL_CLOSE["PRODUCT_MODAL_CLOSE"],
        "fallback_order": ["dom", "coordinates", "escape_key"]
    },
    "MEMO_MODAL_SAVEBUTTON": {
        "name": "메모편집 저장후 닫기",
        "dom_selector": EDITGOODS_SELECTORS["MEMO_MODAL_SAVEBUTTON"],
        "selector_type": "xpath",
        "coordinates": PRODUCT_DETAIL_EDIT["MEMO_MODAL_SAVEBUTTON"],
        "fallback_order": ["dom", "coordinates"]
    },
    "PRODUCT_DETAIL_CLOSEEDIT": {
        "name": "일괄편집 모달창 닫기",
        "dom_selector": EDITGOODS_SELECTORS["PRODUCT_DETAIL_CLOSEEDIT"],
        "selector_type": "xpath",
        "coordinates": PRODUCT_MODAL_CLOSE["PRODUCT_DETAIL_CLOSEEDIT"],
        "fallback_order": ["coordinates", "dom", "escape_key"]
    },
    
    # 상세페이지 편집 요소
    "PRODUCT_DETAIL_OPENEDIT": {
        "name": "일괄편집 모달창 열기",
        "dom_selector": EDITGOODS_SELECTORS["PRODUCT_DETAIL_OPENEDIT"],
        "selector_type": "xpath",
        "coordinates": PRODUCT_DETAIL_EDIT["PRODUCT_DETAIL_OPENEDIT"],
        "fallback_order": ["dom", "coordinates"]
    },
    "PRODUCT_SOURCE_BUTTON": {
        "name": "소스 편집 버튼",
        "dom_selector": EDITGOODS_SELECTORS["PRODUCT_SOURCE_BUTTON"],
        "selector_type": "xpath",
        "coordinates": PRODUCT_MODAL_EDIT2["PRODUCT_SOURCE_BUTTON"],
        "fallback_order": ["dom", "coordinates"]
    },
    "PRODUCT_DETAIL_EDITIMAGE_SAVE": {
        "name": "수정사항 저장, 이미지번역 모달창 닫기기",
        "dom_selector": EDITGOODS_SELECTORS["PRODUCT_DETAIL_EDITIMAGE_SAVE"],
        "selector_type": "xpath",
        "coordinates": PRODUCT_DETAIL_EDIT["PRODUCT_DETAIL_EDITIMAGE_SAVE"],
        "fallback_order": ["dom", "coordinates"]
    },
    
    # 메모편집 모달창 요소
    "MEMO_MODAL_OPEN": {
        "name": "메모편집 모달창 열기",
        "dom_selector": EDITGOODS_SELECTORS["MEMO_MODAL_OPEN"],
        "selector_type": "xpath",
        "coordinates": PRODUCT_MEMO_MODAL["MEMO_MODAL_OPEN"],
        "fallback_order": ["dom", "coordinates"]
    },
    # 상품복사 버튼
    "PRODUCT_COPY_BUTTON": {
        "name": "상품복사 버튼",
        "dom_selector": EDITGOODS_SELECTORS["PRODUCT_COPY_BUTTON"],
        "selector_type": "xpath",
        "coordinates": PRODUCT_MODAL_EDIT2["PRODUCT_COPY_ITEM"],
        "fallback_order": ["dom", "coordinates"]
    },
    
    "MEMO_MODAL_TEXTAREA": {
        "name": "메모편집 TEXTAREA",
        "dom_selector": EDITGOODS_SELECTORS["MEMO_MODAL_TEXTAREA"],
        "selector_type": "xpath",
        "coordinates": PRODUCT_MEMO_MODAL["MEMO_MODAL_TEXTAREA"],
        "fallback_order": ["dom", "coordinates"]
    },
    "MEMO_MODAL_CHECKBOX": {
        "name": "상품목록에 메모 내용 노출하기",
        "dom_selector": EDITGOODS_SELECTORS["MEMO_MODAL_CHECKBOX"],
        "selector_type": "xpath",
        "coordinates": PRODUCT_MEMO_MODAL["MEMO_MODAL_CHECKBOX"],
        "fallback_order": ["dom", "coordinates"]
    },
    
    # 비그룹상품보기 화면에서 첫번째 상품 관련 요소
    "FIRST_PRODUCT_NAME": {
        "name": "첫번째 상품명",
        "dom_selector": EDITGOODS_SELECTORS["FIRST_PRODUCT_NAME"],
        "selector_type": "xpath",
        "coordinates": PRODUCT_MODAL_EDIT1["PRODUCT_FIRST_GOODS"],  # coordinate_editgoods.py의 좌표 활용
        "fallback_order": ["dom", "coordinates"]
    },
    "FIRST_PRODUCT_ITEM": {
        "name": "첫번째 상품 아이템",
        "dom_selector": EDITGOODS_SELECTORS["FIRST_PRODUCT_ITEM"],
        "selector_type": "xpath",
        "coordinates": PRODUCT_MODAL_EDIT1["PRODUCT_FIRST_GOODS"],  # coordinate_editgoods.py의 좌표 활용
        "fallback_order": ["dom", "coordinates"]
    },
    "REGISTER_FIRST_PRODUCT_ITEM": {
        "name": "등록상품관리 첫번째 상품 아이템",
        "dom_selector": EDITGOODS_SELECTORS["REGISTER_FIRST_PRODUCT_ITEM"],
        "selector_type": "xpath",
        "coordinates": MANAGE_REGISTER_VIEW["REGISTER_FIRST_GOODS"],  # 등록상품관리 전용 좌표
        "fallback_order": ["dom", "coordinates"]
    },
    "FIRST_PRODUCT_PRICE": {
        "name": "첫번째 상품 판매가",
        "dom_selector": EDITGOODS_SELECTORS["FIRST_PRODUCT_PRICE"],
        "selector_type": "xpath",
        "coordinates": PRODUCT_MODAL_EDIT1["PRODUCT_FIRST_GOODS"],  # coordinate_editgoods.py의 좌표 활용
        "fallback_order": ["dom", "coordinates"]
    },
    "FIRST_PRODUCT_ORIGINAL_PRICE": {
        "name": "첫번째 상품 원가",
        "dom_selector": EDITGOODS_SELECTORS["FIRST_PRODUCT_ORIGINAL_PRICE"],
        "selector_type": "xpath",
        "coordinates": PRODUCT_MODAL_EDIT1["PRODUCT_FIRST_GOODS"],  # coordinate_editgoods.py의 좌표 활용
        "fallback_order": ["dom", "coordinates"]
    },
    "FIRST_PRODUCT_DELIVERY_FEE": {
        "name": "첫번째 상품 배송비",
        "dom_selector": EDITGOODS_SELECTORS["FIRST_PRODUCT_DELIVERY_FEE"],
        "selector_type": "xpath",
        "coordinates": PRODUCT_MODAL_EDIT1["PRODUCT_FIRST_GOODS"],  # coordinate_editgoods.py의 좌표 활용
        "fallback_order": ["dom", "coordinates"]
    },
    
    # 등록상품관리 화면 요소
    "PRODUCT_NAME_SEARCH_INPUT": {
        "name": "상품명 검색 입력창",
        "dom_selector": "//input[@placeholder='상품명 입력' and contains(@class, 'ant-input')]",
        "selector_type": "xpath",
        "coordinates": MANAGE_REGISTER_VIEW["SEARCH_NAME_INPUT"],
        "fallback_order": ["dom", "coordinates"]
    },

    "THUMBNAIL_CLICK_CENTER": {
        "name": "썸네일탭 중앙 클릭(포커스용)",
        "dom_selector": None,  # D썸네일탭 중앙 클릭(포커스용)
        "selector_type": None,
        "coordinates": MANAGE_REGISTER_VIEW["THUMBNAIL_CLICK_CENTER"],
        "fallback_order": ["coordinates"]  # 좌표만 사용
    },
    
    "SELECT_ALL_CHECKBOX": {
        "name": "전체선택 체크박스",
        "dom_selector": "//div[contains(@class, 'ant-table-selection')]//input[@aria-label='Select all']",
        "selector_type": "xpath",
        "coordinates": MANAGE_REGISTER_VIEW["SELECT_ALL_CHECKBOX"],
        "fallback_order": ["dom", "coordinates"]
    }
}

# 통합 UI 요소 정의 - 액션 요소들
UI_ELEMENTS = {
    # 메뉴 요소 추가
    **MENU_ELEMENTS,
    # 상품 수정 모달창 요소 추가
    **PRODUCT_EDIT_ELEMENTS,
    
    # 다른 카테고리 요소들도 추가 가능
    # **LOGIN_ELEMENTS,
    # **MODAL_ELEMENTS,
}
