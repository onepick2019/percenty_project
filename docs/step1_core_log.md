2025-06-10 15:43:27,489 - batch.batch_manager - INFO - 설정 파일 로드 완료: batch/config/batch_config.json
2025-06-10 15:43:27,655 - core.account.account_manager - INFO - 엑셀 파일 컬럼: ['id', 'password', 'operator', 'sheet_nickname', 'suffixA1', 'suffixA2', 'suffixA3', 'suffixB1', 'suffixB2', 'suffixB3', 'suffixC1', 'suffixC2', 'suffixC3', 'suffixD1', 'suffixD2', 'suffixD3']
2025-06-10 15:43:27,655 - core.account.account_manager - INFO - 매핑된 컬럼: {'email': 'id', 'password': 'password'}
2025-06-10 15:43:27,655 - core.account.account_manager - INFO - 계정 7개 로드 완료 (활성: 7개)
2025-06-10 15:43:27,655 - HumanDelay - INFO - 총 목표 지연: 9.68초 (현재 속도: 46초, 목표: 45-60초)
2025-06-10 15:43:27,688 - core.account.account_manager - INFO - 엑셀 파일 컬럼: ['id', 'password', 'operator', 'sheet_nickname', 'suffixA1', 'suffixA2', 'suffixA3', 'suffixB1', 'suffixB2', 'suffixB3', 'suffixC1', 'suffixC2', 'suffixC3', 'suffixD1', 'suffixD2', 'suffixD3']
2025-06-10 15:43:27,688 - core.account.account_manager - INFO - 매핑된 컬럼: {'email': 'id', 'password': 'password'}
2025-06-10 15:43:27,688 - core.account.account_manager - INFO - 계정 7개 로드 완료 (활성: 7개)
2025-06-10 15:43:27,689 - 🚀 통합 배치 세션 시작: 20250610_154327
2025-06-10 15:43:27,689 - 📋 1단계 배치 실행 시작
2025-06-10 15:43:27,690 - 📝 입력 계정: ['1']
2025-06-10 15:43:27,690 - 🔄 변환된 계정: ['account_1']
2025-06-10 15:43:27,690 - 📦 수량: 25
2025-06-10 15:43:27,690 - ⚡ 동시 실행: False
2025-06-10 15:43:27,690 - ⏱️ 실행 간격: 5초

=== 1단계 배치 실행 ===
입력 계정: ['1']
변환된 계정: ['account_1']
수량: 25
동시 실행: False
실행 간격: 5초
통합 로그 세션: 20250610_154327

2025-06-10 15:43:27,691 - batch.batch_manager - INFO - 단일 단계 배치 시작 - 단계: 1, 계정: 1개, 수량: 25
2025-06-10 15:43:27,691 - batch.batch_manager - INFO - 시작 시간: 2025-06-10 15:43:27
2025-06-10 15:43:27,691 - batch.batch_manager - INFO - 로그 파일 구분자: 20250610_154327
2025-06-10 15:43:27,691 - batch.batch_manager - INFO - 계정 간 실행 간격: 5초
2025-06-10 15:43:27,692 - batch.batch_manager - INFO - 순차 실행 모드로 단일 단계 실행 시작
2025-06-10 15:43:27,692 - batch.batch_manager - INFO - _run_sequential_single_step 호출 전 시간: 2025-06-10 15:43:27
2025-06-10 15:43:27,692 - batch.batch_manager - INFO - === _run_sequential_single_step 시작: task_id=single_step_1_20250610_154327, step=1, accounts=['account_1'], quantity=25 ===
2025-06-10 15:43:27,692 - batch.batch_manager - INFO - 순차 실행 시작 시간: 2025-06-10 15:43:27
2025-06-10 15:43:27,692 - batch.batch_manager - INFO - 결과 딕셔너리 초기화 완료: {'task_id': 'single_step_1_20250610_154327', 'success': True, 'start_time': datetime.datetime(2025, 6, 10, 15, 43, 27, 692365), 'results': {}}
2025-06-10 15:43:27,692 - batch.batch_manager - INFO - 계정 목록 순회 시작: 1개 계정
2025-06-10 15:43:27,692 - batch.batch_manager - INFO - === 계정 1/1 처리 시작: 'account_1' ===
2025-06-10 15:43:27,692 - batch.batch_manager - INFO - 계정 account_1 처리 시작 시간: 2025-06-10 15:43:27
2025-06-10 15:43:27,692 - batch.batch_manager - INFO - _execute_step_for_account 호출 전: step=1, account_id=account_1, quantity=25
2025-06-10 15:43:30,244 - core.browser.browser_manager - INFO - === create_browser 시작: browser_id=account_1_browser, headless=False (인스턴스 기본값: False) ===
2025-06-10 15:43:30,244 - core.browser.browser_manager - INFO - BrowserCore 인스턴스 생성 시작
2025-06-10 15:43:30,244 - core.browser.browser_manager - INFO - BrowserCore 인스턴스 생성 완료
2025-06-10 15:43:30,244 - core.browser.browser_manager - INFO - 브라우저 드라이버 생성 시작 (headless=False)
2025-06-10 15:43:30,244 - core.browser.browser_manager - INFO - browser_core.create_browser 호출 전
2025-06-10 15:43:30,244 - root - INFO - ===== 브라우저 설정 시작 =====
2025-06-10 15:43:30,244 - root - INFO - 일반 모드로 브라우저 설정
2025-06-10 15:43:30,245 - root - INFO - GUI 모드: Windows 호환성 Chrome 옵션 적용
2025-06-10 15:43:30,245 - root - INFO - Selenium Manager를 사용하여 Chrome 드라이버 자동 설정 시작
2025-06-10 15:43:30,245 - root - INFO - Chrome 드라이버 생성 시도 중...
2025-06-10 15:43:30,245 - root - INFO - webdriver.Chrome() 호출 시작

DevTools listening on ws://127.0.0.1:60192/devtools/browser/622ed21d-0d48-45a3-80e3-7aa1920a5927
2025-06-10 15:43:31,439 - root - INFO - webdriver.Chrome() 호출 완료
2025-06-10 15:43:31,440 - root - INFO - result_queue에 driver 저장 완료
2025-06-10 15:43:31,440 - root - INFO - Chrome 드라이버 생성 완료 (소요시간: 1.20초)
2025-06-10 15:43:31,440 - root - INFO - 브라우저 창 크기 및 위치 정보 수집 시작
2025-06-10 15:43:31,444 - root - INFO - 초기 창 크기: 1936x1048
2025-06-10 15:43:31,444 - root - INFO - 초기 창 위치: x=-8, y=-8
2025-06-10 15:43:31,444 - root - INFO - 브라우저 전체화면으로 전환 시도
2025-06-10 15:43:31,446 - root - INFO - maximize_window() 호출 완료
2025-06-10 15:43:32,447 - root - INFO - 전체화면 전환 대기 완료
2025-06-10 15:43:32,452 - root - INFO - 전체화면 후 창 크기: 1936x1048
2025-06-10 15:43:32,452 - root - INFO - 전체화면 후 창 위치: x=-8, y=-8
2025-06-10 15:43:32,452 - root - INFO - JavaScript를 사용하여 브라우저 내부 크기 측정 시작
2025-06-10 15:43:32,456 - root - INFO - innerWidth 측정 완료: 1920
2025-06-10 15:43:32,459 - root - INFO - innerHeight 측정 완료: 945
2025-06-10 15:43:32,459 - root - INFO - 브라우저 내부 크기: 1920x945
2025-06-10 15:43:32,462 - root - INFO - JavaScript 실행 가능: True
2025-06-10 15:43:32,463 - root - INFO - ===== 브라우저 설정 완료 =====
2025-06-10 15:43:32,463 - core.browser.browser_manager - INFO - browser_core.create_browser 호출 완료 (소요시간: 2.22초)
2025-06-10 15:43:32,463 - core.browser.browser_manager - INFO - 반환된 driver 타입: <class 'selenium.webdriver.chrome.webdriver.WebDriver'>
2025-06-10 15:43:32,463 - core.browser.browser_manager - INFO - PercentyLogin 인스턴스 생성 시작
2025-06-10 15:43:32,532 - root - INFO - 화면 해상도: 1920x1080
2025-06-10 15:43:32,533 - root - INFO - 브라우저 창 크기: 1920x1080
2025-06-10 15:43:32,533 - root - INFO - 브라우저 창 위치: x=0, y=0
2025-06-10 15:43:32,534 - core.browser.browser_manager - INFO - PercentyLogin 인스턴스 생성 완료
2025-06-10 15:43:32,534 - core.browser.browser_manager - INFO - 브라우저 'account_1_browser' 생성 완료
2025-06-10 15:43:32,635 - core.browser.browser_manager - INFO - 퍼센티 로그인 페이지 열기: https://www.percenty.co.kr/signin
2025-06-10 15:43:38,084 - core.browser.browser_manager - INFO - 아이디 입력 중...
WARNING: All log messages before absl::InitializeLog() is called are written to STDERR
I0000 00:00:1749537818.520053   30400 voice_transcription.cc:58] Registering VoiceTranscriptionCapability
2025-06-10 15:43:38,803 - core.browser.browser_manager - INFO - 비밀번호 입력 중...
2025-06-10 15:43:39,420 - core.browser.browser_manager - INFO - 로그인 버튼 클릭 중...
2025-06-10 15:43:39,478 - core.browser.browser_manager - INFO - 로그인 완료 확인 중...
2025-06-10 15:43:41,171 - core.browser.browser_manager - INFO - 로그인 성공! 현재 URL: https://www.percenty.co.kr/
2025-06-10 15:43:43,222 - HumanDelay - INFO - 총 목표 지연: 9.01초 (현재 속도: 46초, 목표: 45-60초)
2025-06-10 15:43:43,364 - root - INFO - 화면 해상도: 1920x1080
2025-06-10 15:43:43,365 - root - INFO - 브라우저 창 크기: 1920x1080
2025-06-10 15:43:43,365 - root - INFO - 브라우저 창 위치: x=0, y=0
2025-06-10 15:43:43,368 - core.steps.step1_core - INFO - 1단계 코어 관리자 객체들이 설정되었습니다.
2025-06-10 15:43:43,368 - HumanDelay - INFO - 총 목표 지연: 2.77초 (현재 속도: 46초, 목표: 45-60초)
2025-06-10 15:43:43,500 - root - INFO - 화면 해상도: 1920x1080
2025-06-10 15:43:43,500 - root - INFO - 브라우저 창 크기: 1920x1080
2025-06-10 15:43:43,500 - root - INFO - 브라우저 창 위치: x=0, y=0
2025-06-10 15:43:43,502 - core.steps.step1_core - INFO - 1단계 코어 관리자 객체들이 설정되었습니다.
2025-06-10 15:43:43,502 - core.steps.step1_core - INFO - 1단계 작업 시작 - 목표 수량: 20
2025-06-10 15:43:43,502 - core.common.modal_handler - INFO - 로그인 후 모달창 처리 시작...
2025-06-10 15:43:43,502 - root - INFO - 로그인 모달창 숨기기 적용 시작
2025-06-10 15:43:43,502 - root - INFO - '다시 보지 않기' 버튼 찾기 시도: //span[contains(text(), '다시 보지 않기')]/parent::button
2025-06-10 15:43:43,537 - root - INFO - '다시 보지 않기' 버튼 클릭 성공: {'clicked': True, 'found': True, 'method': 'xpath'}
Created TensorFlow Lite XNNPACK delegate for CPU.
2025-06-10 15:43:44,037 - core.common.modal_handler - INFO - 로그인 모달창 처리 성공
2025-06-10 15:43:44,083 - root - INFO - 표시된 모달창이 없습니다.
2025-06-10 15:43:44,090 - root - INFO - 모달창 관련 쿠키 및 localStorage 설정 결과: {'storage': 'set', 'success': True}
2025-06-10 15:43:44,090 - root - INFO - 모달창 처리 결과: {'success': True, 'method': 'no_modal_found'}
2025-06-10 15:43:44,090 - core.common.modal_handler - INFO - 모달창 차단 스크립트 적용 완료
2025-06-10 15:43:45,091 - core.common.modal_handler - INFO - 모달창 처리 완료
2025-06-10 15:43:45,091 - core.common.modal_handler - INFO - 채널톡 숨기기 시작...
2025-06-10 15:43:45,091 - percenty_utils - INFO - 메뉴클릭전 채널톡 숨기기 적용 시작
2025-06-10 15:43:45,091 - root - INFO - 채널톡 숨기기 적용 - 확인 과정 건너뛐
2025-06-10 15:43:45,098 - root - INFO - 채널톡 강제 숨김 결과: {"method": "강제 숨김 적용 (확인 건너뛐)", "success": true}
2025-06-10 15:43:45,098 - root - INFO - 채널톡 닫기 성공! 이후 닫기 시도는 무시됩니다.
2025-06-10 15:43:45,098 - percenty_utils - INFO - 메뉴클릭전 채널톡 숨기기 결과: True
2025-06-10 15:43:45,098 - percenty_utils - INFO - 메뉴클릭전 로그인 모달창 숨기기 적용 시작
2025-06-10 15:43:45,099 - root - INFO - 로그인 모달창이 이미 숨겨져 있습니다. 추가 시도를 건너뜁니다.
2025-06-10 15:43:45,099 - percenty_utils - INFO - 메뉴클릭전 로그인 모달창 숨기기 결과: True
2025-06-10 15:43:45,099 - core.common.modal_handler - INFO - 채널톡 숨기기 완료
2025-06-10 15:43:45,099 - core.common.navigation_handler - INFO - AI 소싱 메뉴 클릭 시도...
2025-06-10 15:43:45,257 - root - INFO - AI 소싱 메뉴 - DOM 선택자로 클릭 성공
2025-06-10 15:43:45,258 - MenuClicks - INFO - AI 소싱 메뉴 클릭 성공 (방법: dom_click)
2025-06-10 15:43:45,258 - root - INFO - 시간 지연 3초 - AI 소싱 메뉴 클릭 후
2025-06-10 15:43:48,258 - root - INFO - 시간 지연 완료 (3초) - AI 소싱 메뉴 클릭 후
2025-06-10 15:43:51,259 - core.common.navigation_handler - INFO - AI 소싱 메뉴 클릭 완료
2025-06-10 15:43:51,259 - core.common.navigation_handler - INFO - 그룹상품관리 화면으로 이동 시도
2025-06-10 15:43:51,434 - root - INFO - 그룹상품관리 메뉴 - DOM 선택자로 클릭 성공
2025-06-10 15:43:51,434 - MenuClicks - INFO - 그룹상품관리 메뉴 클릭 성공 (방법: dom_click)
2025-06-10 15:43:51,435 - root - INFO - 시간 지연 3초 - 그룹상품관리 메뉴 클릭 후
2025-06-10 15:43:54,435 - root - INFO - 시간 지연 완료 (3초) - 그룹상품관리 메뉴 클릭 후
2025-06-10 15:43:57,435 - core.common.navigation_handler - INFO - 그룹상품관리 화면 이동 완료
2025-06-10 15:43:57,436 - core.common.navigation_handler - INFO - 비그룹상품보기 전환 시작
2025-06-10 15:43:57,436 - MenuClicks - INFO - 비그룹상품 토글 클릭 시도 (PRODUCT_VIEW_NOGROUP 사용)
2025-06-10 15:43:57,436 - MenuClicks - INFO - DOM 선택자로 비그룹상품 토글 찾기 시도: //button[@role='switch' and contains(@class, 'ant-switch')]
2025-06-10 15:43:57,524 - MenuClicks - INFO - 비그룹상품 토글 클릭 성공 (DOM 선택자)
2025-06-10 15:44:00,525 - core.common.navigation_handler - INFO - 비그룹상품보기 전환 완료
2025-06-10 15:44:00,571 - core.common.product_handler - INFO - 상품 개수 텍스트 발견: '총 40개 상품'
2025-06-10 15:44:00,571 - core.common.product_handler - INFO - 화면에 표시된 상품 개수: 40개
2025-06-10 15:44:00,571 - core.steps.step1_core - INFO - 📊 실행 전 비그룹상품 수량: 40개
2025-06-10 15:44:00,572 - core.steps.step1_core - INFO - ===== 상품 1/20 작업 시작 =====
2025-06-10 15:44:00,572 - HumanDelay - INFO - 총 목표 지연: 0.63초 (현재 속도: 46초, 목표: 45-60초)
2025-06-10 15:44:00,572 - core.steps.step1_core - INFO - 작업 시작 전 지연: 0.05초
2025-06-10 15:44:00,617 - dropdown_utils - INFO - 퍼센티 드롭박스 및 그룹 선택 유틸리티 초기화
2025-06-10 15:44:00,617 - keyboard_shortcuts - INFO - 키보드 단축키 모듈 초기화
2025-06-10 15:44:00,639 - root - INFO - 표시된 모달창이 없습니다.
2025-06-10 15:44:00,644 - root - INFO - 모달창 관련 쿠키 및 localStorage 설정 결과: {'storage': 'set', 'success': True}
2025-06-10 15:44:00,644 - percenty_utils - INFO - 상품 처리 채널톡 숨기기 적용 시작
2025-06-10 15:44:00,644 - root - INFO - 채널톡이 이미 닫혀 있습니다. 추가 닫기 시도를 건너뜁니다.
2025-06-10 15:44:00,644 - percenty_utils - INFO - 상품 처리 채널톡 숨기기 결과: True
2025-06-10 15:44:00,644 - percenty_utils - INFO - 상품 처리 로그인 모달창 숨기기 적용 시작
2025-06-10 15:44:00,644 - root - INFO - 로그인 모달창이 이미 숨겨져 있습니다. 추가 시도를 건너뜁니다.
2025-06-10 15:44:00,644 - percenty_utils - INFO - 상품 처리 로그인 모달창 숨기기 결과: True
2025-06-10 15:44:00,644 - product_editor_core - INFO - 첫번째 상품 클릭 시도 (1/3) - DOM 선택자 우선
2025-06-10 15:44:00,645 - product_editor_core - INFO -

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
2025-06-10 15:44:00,645 - product_editor_core - INFO - !!! 첫번째 상품 클릭 함수 실행 중 - DOM 선택자 방식 !!!
2025-06-10 15:44:00,645 - product_editor_core - INFO - !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


2025-06-10 15:44:00,645 - product_editor_core - INFO - 2. 첫번째 상품 클릭 시도 (FIRST_PRODUCT_ITEM DOM 선택자 사용)
2025-06-10 15:44:00,645 - click_utils - INFO -

====== 첫번째 상품 아이템 요소 클릭 시도 - 하이브리드 방식 ======
2025-06-10 15:44:00,645 - click_utils - INFO - UI 요소 정보: 첫번째 상품 아이템
2025-06-10 15:44:00,645 - click_utils - INFO - DOM 선택자: //div[contains(@class, 'sc-gwZKzw') and contains(@class, 'sc-etlCFv')][1]
2025-06-10 15:44:00,645 - click_utils - INFO - 좌표: (700, 660)