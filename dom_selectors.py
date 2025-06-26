"""
퍼센티 자동화에 필요한 DOM 선택자 정의 파일 (dom_selectors.py)
좌표 기반 클릭과 함께 사용할 DOM 선택자를 중앙에서 관리합니다.
"""

# 메뉴 관련 DOM 선택자 - 동적 작동을 위한 개선된 버전
MENU_SELECTORS = {
    # 퍼센티 홈 및 캘린더 메뉴 - 기본 메뉴
    "HOME": "//span[contains(@class, 'ant-menu-title-content')][contains(., '퍼센티 홈')]",
    "PRODUCT_CALENDAR": "//span[contains(@class, 'ant-menu-title-content')][contains(., '셀러 캘린더')]",
    
    # 상품 관리 카테고리 메뉴 - 대분류
    "PRODUCT_CATEGORY": "//span[contains(@class, 'ant-menu-title-content')][contains(., '상품 관리')]",
    
    # 상품 관리 서브 메뉴 - 중요한 상품 관리 기능
    "PRODUCT_AISOURCING": "//span[contains(@class, 'ant-menu-title-content')][contains(., 'AI 소싱')]",
    "PRODUCT_REGISTER": "//span[contains(@class, 'ant-menu-title-content')][contains(., '신규 상품')]",
    "PRODUCT_MANAGE": "//span[contains(@class, 'ant-menu-title-content')][contains(., '등록 상품')]",
    "PRODUCT_GROUP": "//span[contains(@class, 'ant-menu-title-content')][contains(., '그룹 상품')]",
    
    # 주문관리 카테고리 메뉴 - 대분류
    "ORDER_CATEGORY": "//span[contains(@class, 'ant-menu-title-content')][contains(., '주문 관리')]",
    
    # 주문관리 서브 메뉴 - 주문 관리 기능
    "ORDER_MANAGE": "//span[contains(@class, 'ant-menu-title-content')][contains(., '상품 주문')]",
    "ORDER_CUSTOMER": "//span[contains(@class, 'ant-menu-title-content')][contains(., '고객 문의')]",
    "ORDER_CUSTOMS": "//span[contains(@class, 'ant-menu-title-content')][contains(., '통관고유부호')]",
    
    # 배송관리 및 통계 메뉴 - 기타 기능
    "DELIVERY_AGENCY": "//span[contains(@class, 'ant-menu-title-content')][contains(., '배송대행지')]",
    "PERCENTY_ANALYTICS": "//span[contains(@class, 'ant-menu-title-content')][contains(., '퍼센티 애널리틱스')]",
    "PURCHASE_LEDGER": "//span[contains(@class, 'ant-menu-title-content')][contains(., '구매대행 장부')]",
    "PERCENTY_SCHOOL": "//span[contains(@class, 'ant-menu-title-content')][contains(., '퍼센티 스쿨')]",
    
    # 업로드 설정 카테고리 메뉴 - 대분류
    "SETTING_UPLOAD_CATEGORY": "//span[contains(@class, 'ant-menu-title-content')][contains(., '업로드 설정')]",
    
    # 업로드 설정 서브 메뉴 - 설정 관련 기능
    "BASIC_SETTING": "//span[contains(@class, 'ant-menu-title-content')][contains(., '기본 업로드')]",
    "MARKET_SETTING": "//span[contains(@class, 'ant-menu-title-content')][contains(., '마켓 설정')]",
    "PROHIBIT_WORD": "//span[contains(@class, 'ant-menu-title-content')][contains(., '키워드')]",
    
    # 기타 메뉴 - 무관하게 검색할 수 있는 메뉴 항목
    "NOTICE_LIST": "//span[contains(@class, 'ant-menu-title-content')][contains(., '공지사항')]",
    "SETTINGS_CATEGORY": "//span[contains(@class, 'ant-menu-title-content')][contains(., '설정')]",
    "USER_SETTINGS": "//span[@class='ant-menu-title-content' and text()='이용정보 / 설정']",
    "EMPLOYEE_MANAGE": "//span[@class='ant-menu-title-content' and text()='관리자/직원 계정 설정']",
    "UNLIMITED_PLAN": "//span[@class='ant-menu-title-content' and text()='무제한 플랜 결제']",
    "EVENT_CATEGORY": "//span[@class='ant-menu-title-content' and text()='진행중 이벤트']",
    "USER_GUIDE": "//span[@class='ant-menu-title-content' and text()='퍼센티 사용자 가이드']"
}

# 상품수정 모달창 관련 DOM 선택자
EDITGOODS_SELECTORS = {
    # 메모 모달창 관련 선택자 - 상품목록에 메모내용 숨기기 버튼
    # 사용하지 않도록 주석처리
    "MEMO_MODAL_CLOSE": None,  # DOM 선택자로는 정확한 타겟팅이 어려움
    
    # 메모편집 모달창 열기 버튼
    "MEMO_MODAL_OPEN": "//button[contains(text(), '메모') or contains(text(), '메모편집') or contains(@class, 'memo-button')]",
    # 모달창 탭 선택자 - 더 정확한 선택자로 개선
    "PRODUCT_TAB_BASIC": "//div[contains(@class, 'ant-tabs-nav-list')]/div[@data-node-key='0']//div[@role='tab']/span[text()='상품명 / 카테고리']",
    "PRODUCT_TAB_OPTION": "//div[contains(@class, 'ant-tabs-nav-list')]/div[@data-node-key='1']//div[@role='tab']/span[text()='옵션']",
    "PRODUCT_TAB_PRICE": "//div[contains(@class, 'ant-tabs-nav-list')]/div[@data-node-key='2']//div[@role='tab']/span[text()='가격']",
    "PRODUCT_TAB_KEYWORD": "//div[contains(@class, 'ant-tabs-nav-list')]/div[@data-node-key='3']//div[@role='tab']/span[text()='키워드']",
    "PRODUCT_TAB_THUMBNAIL": "//div[contains(@class, 'ant-tabs-nav-list')]/div[@data-node-key='4']//div[@role='tab']/span[text()='썸네일']",
    "PRODUCT_TAB_DETAIL": "//div[contains(@class, 'ant-tabs-nav-list')]/div[@data-node-key='5']//div[@role='tab']/span[text()='상세페이지']",
    "PRODUCT_TAB_UPLOAD": "//div[contains(@class, 'ant-tabs-nav-list')]/div[@data-node-key='6']//div[@role='tab']/span[text()='업로드']",
    
    
    # 상품수정 요소 선택자
    "PRODUCT_SAVE_BUTTON": "//button[contains(@class, 'ant-btn-primary')]/span[text()='저장하기']",
    "PRODUCT_HTMLSOURCE_OPEN": "//button[contains(@class, 'ck-button')][.//span[contains(text(), 'HTML 삽입')]]",
    "PRODUCT_HTMLSOURCE_TEXTAREA": "//textarea[contains(@class, 'raw-html-embed__source')]",
    "PRODUCT_HTMLSOURCE_SAVE": "//button[contains(@class, 'raw-html-embed__save-button')]",
    "PRODUCT_UPLOADEDIT_2ndINPUT": "(//span[contains(@class, 'CharacterTitle85')])[2]/following-sibling::input",
    "PRODUCT_INFO_DISCLOSURE": "//div[@class='ant-collapse-header'][.//span[contains(@class, 'CharacterTitle85') and text()='상품정보제공고시']]",
    
    # 상품정보제공고시 섹션이 열렸는지 확인하기 위한 선택자
    "PRODUCT_INFO_DISCLOSURE_OPENED": "//div[contains(@class, 'ant-row')]/span[contains(@class, 'CharacterTitle85') and text()='고시정보 선택']",
    
    # 정보고시 입력창 관련 개선된 선택자들
    "PRODUCT_INFO_MATERIAL_INPUT": "//span[contains(@class, 'CharacterTitle85') and text()='제품 소재']/parent::div//input[contains(@placeholder, '상세페이지 참조')]",
    "PRODUCT_INFO_SIZE_INPUT": "//span[contains(@class, 'CharacterTitle85') and text()='치수']/parent::div//input[contains(@placeholder, '상세페이지 참조')]",
    "PRODUCT_INFO_WASH_INPUT": "//span[contains(@class, 'CharacterTitle85') and text()='세탁방법 및 취급시 주의사항']/parent::div//input[contains(@placeholder, '상세페이지 참조')]",
    "PRODUCT_INFO_MANUFACTURE_INPUT": "//span[contains(@class, 'CharacterTitle85') and text()='제조연월']/parent::div//input[contains(@placeholder, '상세페이지 참조')]",
    "PRODUCT_INFO_WARRANTY_INPUT": "//span[contains(@class, 'CharacterTitle85') and text()='품질보증기준']/parent::div//input[contains(@placeholder, '상세페이지 참조')]",
    "PRODUCT_INFO_DELIVERY_INPUT": "//span[contains(@class, 'CharacterTitle85') and text()='주문후 예상 배송기간']/parent::div//input[contains(@placeholder, '상세페이지 참조')]",
    "PRODUCT_NAMEEDIT_TEXTAREA": "//input[contains(@class, 'ant-input') and @type='text' and not(@readonly)]",
    "PRODUCT_VIEW_NOGROUP": "//button[@role='switch' and contains(@class, 'ant-switch')]",
    "PRODUCT_VIEW_GROUP_TEXT": "//span[contains(@class, 'CharacterTitle85')][text()='그룹상품 보기']",
    "PRODUCT_VIEW_NONGROUP_TEXT": "//span[contains(@class, 'CharacterTitle85')][text()='비그룹상품 보기']",
    "PRODUCT_MODAL_TABS": "//div[contains(@class, 'ant-tabs-nav-list')]",
    "PRODUCT_MODAL_DETAIL_TAB": "//div[contains(@class, 'ant-tabs-nav-list')]/div[@data-node-key='5']",
    
    # 옵션탭 요소 선택자
    "PRODUCT_OPTION_AI": "//button[.//span[contains(text(), 'AI 옵션명 다듬기')]]",
    "PRODUCT_OPTION_NUMBER": "//button[.//span[text()='1-99']]",
    
    # 가격탭 요소 선택자 (정확한 할인율 필드 선택자로 복원)
    "PRODUCT_PRICE_DISCOUNTRATE": "//input[@role='spinbutton' and @aria-valuenow='30']",
    "PRODUCT_PRICE_DISCOUNTRATE1": "//input[@role='spinbutton' and @aria-valuenow='30']",

    # 모달창 닫기 관련 선택자
    "PRODUCT_MODAL_CLOSE": "//button[contains(@class, 'ant-modal-close')]",
    "MEMO_MODAL_SAVEBUTTON": "//button[contains(@class, 'ant-btn') and contains(@class, 'css-1li46mu') and contains(@class, 'ant-btn-primary')]/span[contains(text(), '저장 후 닫기 ctrl+enter')]",
    "PRODUCT_DETAIL_CLOSEEDIT": "//div[contains(@class, 'ant-col') and contains(@class, 'css-1li46mu')]//span[@role='img' and @aria-label='close' and contains(@class, 'anticon-close')]",
    
    # 상세페이지 편집 요소 선택자
    "PRODUCT_DETAIL_OPENEDIT": "//button[@type='button' and contains(@class, 'ant-btn') and contains(@class, 'ant-btn-default') and contains(@class, 'sc-knefzF')][.//span[text()='일괄 편집']]",
    "PRODUCT_SOURCE_BUTTON": "//button[contains(@class, 'ck-source-editing-button')]",
    "PRODUCT_DETAIL_EDITIMAGE_SAVE": "//button[@type='button' and contains(@class, 'ant-btn') and contains(@class, 'ant-btn-primary')][.//span[text()='수정사항 저장']]",
    
    # 메모편집 요소 선택자
    "MEMO_MODAL_OPEN": "//button[contains(@class, 'ant-float-btn')][.//span[contains(@class, 'anticon-file-text')]]",
    "MEMO_MODAL_TEXTAREA": "//textarea[contains(@placeholder, '상품에 대한 메모')]",
    "MEMO_MODAL_CHECKBOX": "//label[contains(@class, 'ant-checkbox-wrapper')]/span[contains(text(), '상품 목록에 메모 내용 노출하기')]",
    
    # 상품복사 버튼 선택자
    "PRODUCT_COPY_BUTTON": "//button[@type='button' and contains(@class, 'ant-btn') and contains(@class, 'ant-btn-default')][.//span[contains(@class, 'anticon-copy')] and .//span[text()='상품 복사']]",
    
    # 상품목록 첫번째 상품 선택자 (비그룹상품보기 화면)
    "FIRST_PRODUCT_NAME": "//span[contains(@class, 'sc-inyXkq') and contains(@class, 'sc-fremEr')][1]",  # 첫번째 상품명
    "FIRST_PRODUCT_ITEM": "//div[contains(@class, 'sc-gwZKzw') and contains(@class, 'sc-etlCFv')][1]",  # 첫번째 상품 아이템 전체 컨테이너
    
    # 등록상품관리 화면용 첫번째 상품 선택자
    # "REGISTER_FIRST_PRODUCT_ITEM": "//div[contains(@class, 'ant-flex') and contains(@class, 'css-1li46mu') and contains(@class, 'ant-flex-align-stretch') and contains(@class, 'ant-flex-vertical')][1]",  # 등록상품관리에서 첫번째 상품 아이템
    "REGISTER_FIRST_PRODUCT_ITEM": "//div[contains(@class, 'sc-gwZKzw') and contains(@class, 'sc-etlCFv')][1]",  # 등록상품관리에서 첫번째 상품 아이템


    # 첫번째 상품의 가격 관련 요소
    "FIRST_PRODUCT_PRICE": "//div[contains(@class, 'sc-fremEr')][1]//div[contains(@class, 'sc-kYbjgn')][1]",  # 판매가 영역
    "FIRST_PRODUCT_ORIGINAL_PRICE": "//div[contains(@class, 'sc-fremEr')][1]//div[contains(@class, 'sc-kYbjgn')][2]",  # 원가 영역
    "FIRST_PRODUCT_DELIVERY_FEE": "//div[contains(@class, 'sc-fremEr')][1]//div[contains(text(), '외국배송비')]",  # 외국배송비 표시 영역
    
    # 배포저려 사용하지 않음
    "FIRST_PRODUCT_IMAGE": "//div[contains(@class, 'sc-bStcSt')]//img[1]"
}

# PRODUCT_EDIT_SELECTORS는 EDITGOODS_SELECTORS의 별칭입니다 (호환성을 위해 추가)
PRODUCT_EDIT_SELECTORS = EDITGOODS_SELECTORS

# 화면별 동적 요소 선택자 - 화면 로딩 확인을 위한 선택자
PAGE_LOAD_INDICATORS = {
    # 등록상품관리 화면 - 상품검색 관련
    "PRODUCT_MANAGE_LOADED": "//button[@id='filter_search_button_id']/span[contains(text(), '상품 검색')]",
    "PRODUCT_SEARCH_BUTTON": "//button[contains(@class, 'ant-btn') and contains(@class, 'ant-input-search-button')]",
    "PRODUCT_NAME_SEARCH_INPUT": "//input[@placeholder='상품명 입력' and contains(@class, 'ant-input')]",
    
    # 등록상품관리 전체선택 체크박스 - 정확한 DOM 구조 기반
    "SELECT_ALL_CHECKBOX": "//div[contains(@class, 'ant-table-selection')]//input[@aria-label='Select all']",
    "SELECT_ALL_CHECKBOX_ALT1": "//div[contains(@class, 'ant-table-selection')]//label[contains(@class, 'ant-checkbox-wrapper')]//input[@type='checkbox']",
    "SELECT_ALL_CHECKBOX_ALT2": "//input[@aria-label='Select all' and @type='checkbox']",
    
    # 신규상품등록 화면 - 수집하기 버튼
    "PRODUCT_REGISTER_LOADED": "//button[contains(@class, 'ant-btn')]/span[contains(text(), '수집하기')]",
    
    # 그룹상품관리 화면 - 그룹 관리하기 버튼
    "PRODUCT_GROUP_LOADED": "//button[contains(@class, 'ant-btn-primary')]/span[text()='그룹 관리하기']",
    
    # AI 소싱 화면 - AI 상품 추천받기 버튼
    "PRODUCT_AISOURCING_LOADED": "//button[contains(@class, 'ant-btn-primary')]/div[contains(text(), 'AI 상품 추천받기')]",
    
    # 마켓 설정 화면 - API 검증 버튼
    "MARKET_SETTING_LOADED": "//button[contains(@class, 'ant-btn-primary')]/span[text()='API 검증']",
    
    # 비그룹상품보기 토글 버튼은 ui_elements.py의 PRODUCT_VIEW_NOGROUP으로 대체됨
    
    # 모달창 탭 활성화 여부 확인을 위한 선택자 - 각 탭에 고유한 버튼 요소 사용 (정확한 로딩 지표)
    "PRODUCT_TAB_BASIC_ACTIVE": "//button[contains(@class, 'ant-btn')]/span[text()='카테고리 추천 받기']",
    "PRODUCT_TAB_OPTION_ACTIVE": "//button[contains(@class, 'ant-btn')]/span[text()='AI 옵션명 다듬기']",
    "PRODUCT_TAB_PRICE_ACTIVE": "//button[contains(@class, 'ant-btn')]/span[text()='배송비용 계산기']",
    "PRODUCT_TAB_KEYWORD_ACTIVE": "//button[contains(@class, 'ant-btn')]/span[text()='키워드 추가 enter']",
    "PRODUCT_TAB_THUMBNAIL_ACTIVE": "//button[contains(@class, 'ant-btn')]/span[text()='썸네일 되돌리기']",
    "PRODUCT_TAB_DETAIL_ACTIVE": "//button[contains(@class, 'ant-btn')]/span[text()='일괄 편집']",
    "PRODUCT_TAB_UPLOAD_ACTIVE": "//button[contains(@class, 'ant-btn')]/span[text()='쿠팡 개별 업로드']",
    
    # 모달창 관련 로딩 지표
    "MEMO_MODAL_LOADED": "//textarea[contains(@placeholder, '상품에 대한 메모')]",  # 메모편집 모달창
    "HTML_INSERT_MODAL_LOADED": "//textarea[contains(@class, 'raw-html-embed__source')]",  # HTML 삽입 모달창
    "IMAGE_MODAL_LOADED": "//div[contains(@class, 'ant-modal-body')]//div[contains(@class, 'ant-upload')]"  # 이미지 일괄편집 모달창
}

# 로그인 관련 DOM 선택자
LOGIN_SELECTORS = {
    # 아이디/이메일 입력 필드
    "EMAIL_FIELD": "//input[@id='email']",
    "USERNAME_FIELD": "//input[@id='email']",  # EMAIL_FIELD와 동일한 선택자를 사용하여 일관성 유지
    
    # 비밀번호 입력 필드
    "PASSWORD_FIELD": "//input[@id='password']",
    
    # 아이디 저장 체크박스
    "SAVE_ID_CHECKBOX": "//input[@id='saveId']",
    
    # 로그인 버튼
    "LOGIN_BUTTON": "//button[contains(@class, 'ant-btn-primary') and contains(., '이메일 로그인')]",
    
    # 로그인 페이지 로딩 확인 지표
    "LOGIN_PAGE_LOADED": "//div[contains(@class, 'login-container')]",
    
    # 다시 보지 않기 버튼 (모달창)
    "DONT_SHOW_AGAIN": "//span[contains(text(), '다시 보지 않기')]/parent::button"
}

# 모달창 관련 DOM 선택자
MODAL_SELECTORS = {
    # 일반 모달창 닫기 버튼
    "MODAL_CLOSE": "//button[contains(@class, 'ant-modal-close')]",
    
    # 이미지가 포함된 모달창 (프로모션 등)
    "IMAGE_MODAL": "//div[contains(@class, 'ant-modal-body')]//img",
    
    # 다시 보지 않기 버튼이 있는 모달창
    "MODAL_WITH_DONT_SHOW": "//span[contains(text(), '다시 보지 않기')]/parent::button"
}

# 추가 ACTION 선택자도 필요하다면 정의할 수 있습니다
# ACTION_SELECTORS = { ... }
