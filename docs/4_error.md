PS C:\Projects\percenty_project> if ($env:TERM_PROGRAM -eq "vscode") { . "c:\Users\drmath7\AppData\Local\Programs\Trae\resources\app\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration.ps1" }; Write-Output "[Trae] Shell integration is not enabled, try to fix it now."
. : 이 시스템에서 스크립트를 실행할 수 없으므로 C:\Users\drmath7\AppData\Local\Programs\Trae
\resources\app\out\vs\workbench\c
PS C:\Projects\percenty_project>
PS C:\Projects\percenty_project>
PS C:\Projects\percenty_project>
PS C:\Projects\percenty_project> ^C
PS C:\Projects\percenty_project> python cli/batch_cli.py single --step 4 --accounts



                                 python cli/batch_cli.py single --step 4 --accounts wop31garam@gmail.com --quantity 1 --chunk-size 1
2025-06-17 14:45:48,684 - batch.batch_manager - INFO - 설정 파일 로드 완료: batch/config/batch_config.json
2025-06-17 14:45:48,875 - core.account.account_manager - INFO - 엑셀 파일 컬럼: ['id', 'password', 'operator', 'sheet_nickname', 'suffixA1', 'suffixA2', 'suffixA3', 'suffixB1', 'suffixB2', 'suffixB3', 'suffixC1', 'suffixC2', 'suffixC3', 'suffixD1', 'suffixD2', 'suffixD3']       
2025-06-17 14:45:48,875 - core.account.account_manager - INFO - 매핑된 컬럼: {'email': 'id', 'password': 'password'}
2025-06-17 14:45:48,876 - core.account.account_manager - INFO - 계정 14개 로드 완료 (활성: 7 개)
2025-06-17 14:45:48,876 - HumanDelay - INFO - 총 목표 지연: 12.86초 (현재 속도: 46초, 목표: 45-60초)
2025-06-17 14:45:48,923 - core.account.account_manager - INFO - 엑셀 파일 컬럼: ['id', 'password', 'operator', 'sheet_nickname', 'suffixA1', 'suffixA2', 'suffixA3', 'suffixB1', 'suffixB2', 'suffixB3', 'suffixC1', 'suffixC2', 'suffixC3', 'suffixD1', 'suffixD2', 'suffixD3']       
2025-06-17 14:45:48,924 - core.account.account_manager - INFO - 매핑된 컬럼: {'email': 'id', 'password': 'password'}
2025-06-17 14:45:48,924 - core.account.account_manager - INFO - 계정 14개 로드 완료 (활성: 7 개)
2025-06-17 14:45:48,925 - 🚀 통합 배치 세션 시작: 20250617_144548
2025-06-17 14:45:48,925 - 📋 4단계 배치 실행 시작
2025-06-17 14:45:48,926 - 📝 입력 계정: ['wop31garam@gmail.com']
2025-06-17 14:45:48,926 - 🔄 변환된 계정: ['wop31garam@gmail.com']
2025-06-17 14:45:48,926 - 📦 수량: 1
2025-06-17 14:45:48,926 - ⚡ 동시 실행: False
2025-06-17 14:45:48,926 - ⏱️ 실행 간격: 5초
2025-06-17 14:45:48,927 - 📦 청크 크기: 1

=== 4단계 배치 실행 ===
입력 계정: ['wop31garam@gmail.com']
변환된 계정: ['wop31garam@gmail.com']
수량: 1
동시 실행: False
실행 간격: 5초
청크 크기: 1
통합 로그 세션: 20250617_144548

2025-06-17 14:45:48,928 - batch.batch_manager - INFO - 단일 단계 배치 시작 - 단계: 4, 계정: 1개, 수량: 1
2025-06-17 14:45:48,928 - batch.batch_manager - INFO - 시작 시간: 2025-06-17 14:45:48        
2025-06-17 14:45:48,928 - batch.batch_manager - INFO - 로그 파일 구분자: 20250617_144548     
2025-06-17 14:45:48,928 - batch.batch_manager - INFO - 계정 간 실행 간격: 5초
2025-06-17 14:45:48,929 - batch.batch_manager - INFO - 순차 실행 모드로 단일 단계 실행 시작  
2025-06-17 14:45:48,929 - batch.batch_manager - INFO - _run_sequential_single_step 호출 전 시간: 2025-06-17 14:45:48
2025-06-17 14:45:48,930 - batch.batch_manager - INFO - === _run_sequential_single_step 시작: task_id=single_step_4_20250617_144548, step=4, accounts=['wop31garam@gmail.com'], quantity=1 ===
2025-06-17 14:45:48,930 - batch.batch_manager - INFO - 순차 실행 시작 시간: 2025-06-17 14:45:48
2025-06-17 14:45:48,930 - batch.batch_manager - INFO - 결과 딕셔너리 초기화 완료: {'task_id': 'single_step_4_20250617_144548', 'success': True, 'start_time': datetime.datetime(2025, 6, 17, 14, 45, 48, 930278), 'results': {}}
2025-06-17 14:45:48,930 - batch.batch_manager - INFO - 계정 목록 순회 시작: 1개 계정
2025-06-17 14:45:48,930 - batch.batch_manager - INFO - === 계정 1/1 처리 시작: 'wop31garam@gmail.com' ===
2025-06-17 14:45:48,930 - batch.batch_manager - INFO - 계정 wop31garam@gmail.com 처리 시작 시간: 2025-06-17 14:45:48
2025-06-17 14:45:48,930 - batch.batch_manager - INFO - _execute_step_for_account 호출 전: step=4, account_id=wop31garam@gmail.com, quantity=1
2025-06-17 14:45:51,491 - core.browser.browser_manager - INFO - === create_browser 시작: browser_id=wop31garam@gmail.com_browser, headless=False (인스턴스 기본값: False) ===
2025-06-17 14:45:51,491 - core.browser.browser_manager - INFO - BrowserCore 인스턴스 생성 시 작
2025-06-17 14:45:51,491 - core.browser.browser_manager - INFO - BrowserCore 인스턴스 생성 완 료
2025-06-17 14:45:51,492 - core.browser.browser_manager - INFO - 브라우저 드라이버 생성 시작 (headless=False)
2025-06-17 14:45:51,492 - core.browser.browser_manager - INFO - browser_core.create_browser  호출 전
2025-06-17 14:45:51,492 - root - INFO - ===== 브라우저 설정 시작 =====
2025-06-17 14:45:51,492 - root - INFO - 일반 모드로 브라우저 설정
2025-06-17 14:45:51,492 - root - INFO - GUI 모드: Windows 호환성 Chrome 옵션 적용
2025-06-17 14:45:51,493 - root - INFO - Selenium Manager를 사용하여 Chrome 드라이버 자동 설정 시작
2025-06-17 14:45:51,493 - root - INFO - Chrome 드라이버 생성 시도 중...
2025-06-17 14:45:51,494 - root - INFO - webdriver.Chrome() 호출 시작

DevTools listening on ws://127.0.0.1:55110/devtools/browser/51c16301-792a-4ae4-ac6c-02e75edcdcfd
2025-06-17 14:45:53,085 - root - INFO - webdriver.Chrome() 호출 완료
2025-06-17 14:45:53,085 - root - INFO - result_queue에 driver 저장 완료
2025-06-17 14:45:53,086 - root - INFO - Chrome 드라이버 생성 완료 (소요시간: 1.59초)
2025-06-17 14:45:53,086 - root - INFO - 브라우저 창 크기 및 위치 정보 수집 시작
2025-06-17 14:45:53,454 - root - INFO - 초기 창 크기: 1936x1048
2025-06-17 14:45:53,454 - root - INFO - 초기 창 위치: x=-8, y=-8
2025-06-17 14:45:53,455 - root - INFO - 브라우저 전체화면으로 전환 시도
2025-06-17 14:45:53,456 - root - INFO - maximize_window() 호출 완료
2025-06-17 14:45:54,456 - root - INFO - 전체화면 전환 대기 완료
2025-06-17 14:45:54,461 - root - INFO - 전체화면 후 창 크기: 1936x1048
2025-06-17 14:45:54,461 - root - INFO - 전체화면 후 창 위치: x=-8, y=-8
2025-06-17 14:45:54,461 - root - INFO - JavaScript를 사용하여 브라우저 내부 크기 측정 시작   
2025-06-17 14:45:54,465 - root - INFO - innerWidth 측정 완료: 1920
2025-06-17 14:45:54,468 - root - INFO - innerHeight 측정 완료: 945
2025-06-17 14:45:54,468 - root - INFO - 브라우저 내부 크기: 1920x945
2025-06-17 14:45:54,471 - root - INFO - JavaScript 실행 가능: True
2025-06-17 14:45:54,471 - root - INFO - ===== 브라우저 설정 완료 =====
2025-06-17 14:45:54,471 - core.browser.browser_manager - INFO - browser_core.create_browser  호출 완료 (소요시간: 2.98초)
2025-06-17 14:45:54,471 - core.browser.browser_manager - INFO - 반환된 driver 타입: <class 'selenium.webdriver.chrome.webdriver.WebDriver'>
2025-06-17 14:45:54,471 - core.browser.browser_manager - INFO - PercentyLogin 인스턴스 생성  시작
2025-06-17 14:45:54,584 - root - INFO - 화면 해상도: 1920x1080
2025-06-17 14:45:54,584 - root - INFO - 브라우저 창 크기: 1920x1080
2025-06-17 14:45:54,584 - root - INFO - 브라우저 창 위치: x=0, y=0
2025-06-17 14:45:54,585 - core.browser.browser_manager - INFO - PercentyLogin 인스턴스 생성  완료
2025-06-17 14:45:54,586 - core.browser.browser_manager - INFO - 브라우저 'wop31garam@gmail.com_browser' 생성 완료
2025-06-17 14:45:54,687 - core.browser.browser_manager - INFO - 퍼센티 로그인 페이지 열기: https://www.percenty.co.kr/signin
2025-06-17 14:46:04,909 - core.browser.browser_manager - INFO - 아이디 입력 중...
2025-06-17 14:46:05,634 - core.browser.browser_manager - INFO - 비밀번호 입력 중...
2025-06-17 14:46:06,285 - core.browser.browser_manager - INFO - 로그인 버튼 클릭 중...
2025-06-17 14:46:06,928 - core.browser.browser_manager - INFO - 로그인 완료 확인 중...
2025-06-17 14:46:22,756 - core.browser.browser_manager - INFO - 로그인 성공! 현재 URL: https://www.percenty.co.kr/
WARNING: All log messages before absl::InitializeLog() is called are written to STDERR
I0000 00:00:1750139182.977160   14168 voice_transcription.cc:58] Registering VoiceTranscriptionCapability
2025-06-17 14:46:24,821 - core.steps.step4_core - INFO - 계정 2에 대한 4단계 자동화 시작
2025-06-17 14:46:24,821 - core.steps.step4_core - INFO - Step4Core 초기화 - 계정: 2, 헤드리스: False
2025-06-17 14:46:24,821 - core.steps.step4_core - INFO - 4단계 자동화 초기화 시작
2025-06-17 14:46:24,869 - root - INFO - 총 7개의 계정을 로드했습니다.
2025-06-17 14:46:24,870 - core.steps.step4_core - INFO - 선택된 계정: 계정 2
2025-06-17 14:46:24,934 - root - INFO - 화면 해상도: 1920x1080
2025-06-17 14:46:24,935 - root - INFO - 브라우저 창 크기: 1920x1080
2025-06-17 14:46:24,935 - root - INFO - 브라우저 창 위치: x=0, y=0
2025-06-17 14:46:24,936 - root - INFO - ===== 브라우저 설정 시작 =====
2025-06-17 14:46:24,936 - root - INFO - 일반 모드로 브라우저 설정
2025-06-17 14:46:24,936 - root - INFO - GUI 모드: Windows 호환성 Chrome 옵션 적용
2025-06-17 14:46:24,936 - root - INFO - Selenium Manager를 사용하여 Chrome 드라이버 자동 설정 시작
2025-06-17 14:46:24,936 - root - INFO - Chrome 드라이버 생성 시도 중...
2025-06-17 14:46:24,937 - root - INFO - webdriver.Chrome() 호출 시작

DevTools listening on ws://127.0.0.1:55266/devtools/browser/6242df68-17a2-4651-8479-ca08cad86f00
2025-06-17 14:46:26,209 - root - INFO - webdriver.Chrome() 호출 완료
2025-06-17 14:46:26,212 - root - INFO - result_queue에 driver 저장 완료
2025-06-17 14:46:26,212 - root - INFO - Chrome 드라이버 생성 완료 (소요시간: 1.28초)
2025-06-17 14:46:26,212 - root - INFO - 브라우저 창 크기 및 위치 정보 수집 시작
2025-06-17 14:46:26,224 - root - INFO - 초기 창 크기: 1920x1080
2025-06-17 14:46:26,225 - root - INFO - 초기 창 위치: x=0, y=0
2025-06-17 14:46:26,225 - root - INFO - 브라우저 전체화면으로 전환 시도
2025-06-17 14:46:26,268 - root - INFO - maximize_window() 호출 완료
2025-06-17 14:46:27,268 - root - INFO - 전체화면 전환 대기 완료
2025-06-17 14:46:27,281 - root - INFO - 전체화면 후 창 크기: 1936x1048
2025-06-17 14:46:27,281 - root - INFO - 전체화면 후 창 위치: x=-8, y=-8
2025-06-17 14:46:27,281 - root - INFO - JavaScript를 사용하여 브라우저 내부 크기 측정 시작   
2025-06-17 14:46:27,288 - root - INFO - innerWidth 측정 완료: 1920
2025-06-17 14:46:27,294 - root - INFO - innerHeight 측정 완료: 945
2025-06-17 14:46:27,294 - root - INFO - 브라우저 내부 크기: 1920x945
2025-06-17 14:46:27,299 - root - INFO - JavaScript 실행 가능: True
2025-06-17 14:46:27,299 - root - INFO - ===== 브라우저 설정 완료 =====
2025-06-17 14:46:27,300 - root - INFO - 퍼센티 로그인 페이지 열기: https://www.percenty.co.kr/signin (시도 1/3)
2025-06-17 14:46:27,300 - root - INFO - https://www.percenty.co.kr/signin 열기 (시도 1/3)    
Created TensorFlow Lite XNNPACK delegate for CPU.
2025-06-17 14:46:32,240 - root - INFO - 시간 지연 5초 - 로그인 페이지 로드 대기
WARNING: All log messages before absl::InitializeLog() is called are written to STDERR
I0000 00:00:1750139194.368130   36992 voice_transcription.cc:58] Registering VoiceTranscriptionCapability
2025-06-17 14:46:37,240 - root - INFO - 시간 지연 완료 (5초) - 로그인 페이지 로드 대기
2025-06-17 14:46:37,246 - root - INFO - 표시된 알림이 없습니다.
2025-06-17 14:46:37,246 - root - INFO - 비밀번호 저장 모달창 확인 중...
2025-06-17 14:46:37,252 - root - INFO - 모달창 확인 결과: {'chromeModal': False, 'genericModal': False, 'visibleModal': False}
2025-06-17 14:46:37,252 - root - INFO - 표시된 비밀번호 저장 모달창이 없습니다.
2025-06-17 14:46:37,257 - root - INFO - 비밀번호 저장 관련 설정 적용 결과: {'storage': 'set', 'success': True}
2025-06-17 14:46:37,257 - root - INFO - 페이지 로딩 대기
2025-06-17 14:46:37,258 - root - INFO - 시간 지연 5초 - 페이지 로딩 대기
Created TensorFlow Lite XNNPACK delegate for CPU.
2025-06-17 14:46:42,258 - root - INFO - 시간 지연 완료 (5초) - 페이지 로딩 대기
2025-06-17 14:46:42,281 - root - INFO - 아이디 입력: wop31garam@gmail.com
2025-06-17 14:46:42,303 - root - WARNING - UI_ELEMENTS에서 LOGIN_EMAIL_FIELD를 찾을 수 없습니다. 수동으로 정의합니다.
2025-06-17 14:46:43,125 - root - INFO - unknown element - DOM 선택자로 텍스트 입력 성공: wop31garam@gmail.com
2025-06-17 14:46:43,137 - root - INFO - smart_click으로 아이디 필드 입력 성공: dom_input
2025-06-17 14:46:43,139 - root - INFO - 시간 지연 1초 - 텍스트 입력 후
2025-06-17 14:46:44,140 - root - INFO - 시간 지연 완료 (1초) - 텍스트 입력 후
2025-06-17 14:46:44,141 - root - INFO - 비밀번호 입력 시도
2025-06-17 14:46:44,141 - root - WARNING - UI_ELEMENTS에서 LOGIN_PASSWORD_FIELD를 찾을 수 없 습니다. 수동으로 정의합니다.
2025-06-17 14:46:44,256 - root - INFO - unknown element - DOM 선택자로 텍스트 입력 성공: qnwkehlwk8*
2025-06-17 14:46:44,256 - root - INFO - smart_click으로 비밀번호 필드 입력 성공: dom_input
2025-06-17 14:46:44,257 - root - INFO - 시간 지연 1초 - 텍스트 입력 후
2025-06-17 14:46:45,257 - root - INFO - 시간 지연 완료 (1초) - 텍스트 입력 후
2025-06-17 14:46:45,257 - root - INFO - 아이디 저장 체크박스 주석 처리됨 - 건너뚼
2025-06-17 14:46:45,258 - root - INFO - 로그인 버튼 클릭 시도 (smart_click 사용)
2025-06-17 14:46:45,258 - root - WARNING - UI_ELEMENTS에서 LOGIN_BUTTON을 찾을 수 없습니다.  수동으로 정의합니다.
2025-06-17 14:46:45,516 - root - INFO - unknown element - DOM 선택자로 클릭 성공
2025-06-17 14:46:45,517 - root - INFO - smart_click으로 로그인 버튼 클릭 성공
2025-06-17 14:46:45,517 - root - INFO - 로그인 버튼 클릭 후 대기 - 웹 서버 응답 및 로그인 처 리 기다리는 중
2025-06-17 14:46:45,517 - root - INFO - 시간 지연 2초 - 로그인 버튼 클릭 후 대기
2025-06-17 14:46:47,517 - root - INFO - 시간 지연 완료 (2초) - 로그인 버튼 클릭 후 대기
2025-06-17 14:46:47,545 - root - INFO - 로그인 완료! 현재 URL: https://www.percenty.co.kr/
2025-06-17 14:46:47,546 - root - INFO - 시간 지연 5초 - 로그인 후 페이지 로드 대기
2025-06-17 14:46:52,546 - root - INFO - 시간 지연 완료 (5초) - 로그인 후 페이지 로드 대기
2025-06-17 14:46:52,547 - root - INFO - 비밀번호 저장 모달창 닫기 시도
2025-06-17 14:46:52,547 - root - INFO - 비밀번호 저장 모달창은 이미 닫혔습니다. 중복 처리를  방지합니다.
2025-06-17 14:46:52,547 - root - INFO - 시간 지연 0.5초 - 비밀번호 저장 모달창 닫기 후       
2025-06-17 14:46:53,053 - root - INFO - 시간 지연 완료 (0.5초) - 비밀번호 저장 모달창 닫기 후
2025-06-17 14:46:53,055 - root - INFO - 다시 보지 않기 모달창 처리 시도
2025-06-17 14:46:53,061 - root - INFO - '다시 보지 않기' 버튼 클릭 시도
2025-06-17 14:46:53,480 - root - INFO - '다시 보지 않기' 버튼 DOM 클릭 성공
2025-06-17 14:46:53,480 - root - INFO - '다시 보지 않기' 버튼 클릭 성공: {'success': True, 'method': 'dom_click'}
2025-06-17 14:46:53,981 - root - INFO - 모달창 처리 완료 - 홈 버튼 클릭 준비 중
2025-06-17 14:46:53,981 - root - INFO - 시간 지연 0.5초 - 모달창 닫기 후
2025-06-17 14:46:54,482 - root - INFO - 시간 지연 완료 (0.5초) - 모달창 닫기 후
2025-06-17 14:46:54,482 - root - INFO - 홈 버튼 클릭 스킵 - 신규상품등록 메뉴 클릭 이슈 해결 를 위해 비활성화
2025-06-17 14:46:54,482 - root - INFO - 시간 지연 5초 - 로그인 후 페이지 로딩
2025-06-17 14:46:59,483 - root - INFO - 시간 지연 완료 (5초) - 로그인 후 페이지 로딩
2025-06-17 14:46:59,483 - core.steps.step4_core - INFO - 로그인 성공
2025-06-17 14:46:59,483 - percenty_new_step4 - INFO - ===== 퍼센티 상품 수정 자동화 스크립트 4단계 초기화 =====
2025-06-17 14:46:59,492 - percenty_new_step4 - INFO - 브라우저 내부 크기: 1920x945
2025-06-17 14:46:59,492 - dropdown_utils - INFO - 퍼센티 드롭박스 및 그룹 선택 유틸리티 초기 화
2025-06-17 14:46:59,492 - dropdown_utils4 - INFO - DropdownUtils4 초기화 완료
2025-06-17 14:46:59,492 - dropdown_utils - INFO - 퍼센티 드롭박스 및 그룹 선택 유틸리티 초기 화
2025-06-17 14:46:59,492 - product_editor_core4 - INFO - ProductEditorCore4 초기화 완료       
2025-06-17 14:46:59,492 - percenty_new_step4 - INFO - 상품 편집 코어 4단계 초기화 완료       
2025-06-17 14:46:59,492 - core.steps.step4_core - INFO - 4단계 자동화 초기화 완료
2025-06-17 14:46:59,492 - core.steps.step4_core - INFO - 4단계 자동화 실행 시작
2025-06-17 14:46:59,492 - percenty_new_step4 - INFO - ===== 퍼센티 상품 수정 자동화 4단계 시 작 =====
2025-06-17 14:46:59,493 - percenty_new_step4 - INFO - 신규상품등록 메뉴 클릭 시도 (하이브리드 방식)
2025-06-17 14:46:59,493 - root - ERROR - 강조 표시 정보가 올바르지 않음: xpath=//span[contains(@class, 'ant-menu-title-content')][contains(., '신규 상품')]
2025-06-17 14:46:59,493 - percenty_new_step4 - INFO - 신규상품등록 메뉴 DOM 선택자 기반 클릭 시도: xpath=//span[contains(@class, 'ant-menu-title-content')][contains(., '신규 상품')]     
2025-06-17 14:46:59,787 - percenty_new_step4 - INFO - 신규상품등록 메뉴 DOM 선택자 기반 클릭 성공
2025-06-17 14:46:59,787 - percenty_new_step4 - INFO - 신규상품등록 화면 로드 대기 - 5초
2025-06-17 14:47:04,802 - percenty_new_step4 - INFO - 스크롤 위치를 최상단으로 초기화했습니다
2025-06-17 14:47:04,802 - percenty_new_step4 - INFO - 신규상품등록 화면이 성공적으로 열렸습니다.
2025-06-17 14:47:04,802 - percenty_new_step4 - INFO - 일괄 번역 워크플로우 시작
2025-06-17 14:47:04,802 - product_editor_core4 - INFO -

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
2025-06-17 14:47:04,802 - product_editor_core4 - INFO - !!! 전체 일괄번역 워크플로우 시작 !!!
2025-06-17 14:47:04,803 - product_editor_core4 - INFO - !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


2025-06-17 14:47:04,803 - product_editor_core4 - INFO -

*** 사이클 1 시작 ***
2025-06-17 14:47:04,803 - product_editor_core4 - INFO -
=== 사이클 1, 1단계: 서버1 → 대기1 처리 시작 ===
2025-06-17 14:47:04,803 - product_editor_core4 - INFO - 서버1 → 대기1 워크플로우 시작        
2025-06-17 14:47:04,803 - product_editor_core4 - INFO - 상품검색용 드롭박스에서 '서버1' 그룹 선택
2025-06-17 14:47:04,803 - product_editor_core4 - INFO - 서버1 그룹 선택 시도 1/3
2025-06-17 14:47:04,803 - dropdown_utils4 - INFO - 상품검색 드롭박스에서 '서버1' 그룹 선택 시작
2025-06-17 14:47:04,804 - dropdown_utils4 - INFO - 상품검색 드롭박스 열기 시도
2025-06-17 14:47:04,804 - dropdown_utils4 - INFO - 선택자 1 시도: (//div[contains(@class, 'ant-select-single')])[1]
2025-06-17 14:47:06,463 - dropdown_utils4 - INFO - 상품검색 드롭박스 열기 성공 (선택자 1)
2025-06-17 14:47:06,463 - dropdown_utils4 - INFO - 그룹 '서버1' 선택 시도
2025-06-17 14:47:06,483 - dropdown_utils4 - INFO - 전체 상품 수 텍스트 발견: '총 41,644개 상 품'
2025-06-17 14:47:06,483 - dropdown_utils4 - INFO - 전체 상품 수 확인 성공: 41644개
2025-06-17 14:47:06,484 - dropdown_utils4 - INFO - 그룹 선택 전 전체 상품 수: 41644개        
2025-06-17 14:47:06,493 - dropdown_utils4 - INFO - 현재 화면에 20개의 옵션 발견
2025-06-17 14:47:06,500 - dropdown_utils4 - INFO - 옵션 1: '전체'
2025-06-17 14:47:06,506 - dropdown_utils4 - INFO - 옵션 2: '전체'
2025-06-17 14:47:06,513 - dropdown_utils4 - INFO - 옵션 3: '그룹 없음'
2025-06-17 14:47:06,519 - dropdown_utils4 - INFO - 옵션 4: '그룹 없음'
2025-06-17 14:47:06,525 - dropdown_utils4 - INFO - 옵션 5: '신규수집'
2025-06-17 14:47:06,530 - dropdown_utils4 - INFO - 옵션 6: '신규수집'
2025-06-17 14:47:06,536 - dropdown_utils4 - INFO - 옵션 7: '번역대기'
2025-06-17 14:47:06,543 - dropdown_utils4 - INFO - 옵션 8: '번역대기'
2025-06-17 14:47:06,568 - dropdown_utils4 - INFO - 옵션 9: '등록실행'
2025-06-17 14:47:06,575 - dropdown_utils4 - INFO - 옵션 10: '등록실행'
2025-06-17 14:47:06,586 - dropdown_utils4 - INFO - 옵션 11: '등록A'
2025-06-17 14:47:06,616 - dropdown_utils4 - INFO - 옵션 12: '등록A'
2025-06-17 14:47:06,624 - dropdown_utils4 - INFO - 옵션 13: '등록B'
2025-06-17 14:47:06,633 - dropdown_utils4 - INFO - 옵션 14: '등록B'
2025-06-17 14:47:06,645 - dropdown_utils4 - INFO - 옵션 15: '등록C'
2025-06-17 14:47:06,657 - dropdown_utils4 - INFO - 옵션 16: '등록C'
2025-06-17 14:47:06,678 - dropdown_utils4 - INFO - 옵션 17: ''
2025-06-17 14:47:06,708 - dropdown_utils4 - INFO - 옵션 18: ''
2025-06-17 14:47:06,716 - dropdown_utils4 - INFO - 옵션 19: ''
2025-06-17 14:47:06,724 - dropdown_utils4 - INFO - 옵션 20: ''
2025-06-17 14:47:06,724 - dropdown_utils4 - INFO - '서버1' 그룹이 현재 화면에 없어 스크롤 검 색 시작
2025-06-17 14:47:06,724 - dropdown_utils4 - INFO - 드롭다운 내에서 '서버1' 그룹 스크롤 검색 (최대 30회)
2025-06-17 14:47:06,759 - dropdown_utils4 - INFO - 드롭다운 컨테이너 발견: //div[contains(@class, 'rc-virtual-list-holder')]
2025-06-17 14:47:06,759 - dropdown_utils4 - INFO - 스크롤 1/30
2025-06-17 14:47:06,772 - dropdown_utils4 - INFO - 현재 화면에 20개의 옵션 발견
2025-06-17 14:47:06,781 - dropdown_utils4 - INFO - 옵션 1: '전체'
2025-06-17 14:47:06,789 - dropdown_utils4 - INFO - 옵션 2: '전체'
2025-06-17 14:47:06,797 - dropdown_utils4 - INFO - 옵션 3: '그룹 없음'
2025-06-17 14:47:06,803 - dropdown_utils4 - INFO - 옵션 4: '그룹 없음'
2025-06-17 14:47:06,811 - dropdown_utils4 - INFO - 옵션 5: '신규수집'
2025-06-17 14:47:06,820 - dropdown_utils4 - INFO - 옵션 6: '신규수집'
2025-06-17 14:47:06,827 - dropdown_utils4 - INFO - 옵션 7: '번역대기'
2025-06-17 14:47:06,835 - dropdown_utils4 - INFO - 옵션 8: '번역대기'
2025-06-17 14:47:06,844 - dropdown_utils4 - INFO - 옵션 9: '등록실행'
2025-06-17 14:47:06,853 - dropdown_utils4 - INFO - 옵션 10: '등록실행'
2025-06-17 14:47:06,864 - dropdown_utils4 - INFO - 옵션 11: '등록A'
2025-06-17 14:47:06,872 - dropdown_utils4 - INFO - 옵션 12: '등록A'
2025-06-17 14:47:06,950 - dropdown_utils4 - INFO - 옵션 13: '등록B'
2025-06-17 14:47:07,065 - dropdown_utils4 - INFO - 옵션 14: '등록B'
2025-06-17 14:47:07,103 - dropdown_utils4 - INFO - 옵션 15: '등록C'
2025-06-17 14:47:07,116 - dropdown_utils4 - INFO - 옵션 16: '등록C'
2025-06-17 14:47:07,178 - dropdown_utils4 - INFO - 옵션 17: ''
2025-06-17 14:47:07,222 - dropdown_utils4 - INFO - 옵션 18: ''
2025-06-17 14:47:07,231 - dropdown_utils4 - INFO - 옵션 19: ''
2025-06-17 14:47:07,241 - dropdown_utils4 - INFO - 옵션 20: ''
2025-06-17 14:47:07,582 - dropdown_utils4 - INFO - 스크롤 후 22개 옵션 확인
2025-06-17 14:47:07,582 - dropdown_utils4 - INFO - 스크롤 2/30
2025-06-17 14:47:07,591 - dropdown_utils4 - INFO - 현재 화면에 22개의 옵션 발견
2025-06-17 14:47:07,599 - dropdown_utils4 - INFO - 옵션 1: ''
2025-06-17 14:47:07,605 - dropdown_utils4 - INFO - 옵션 2: ''
2025-06-17 14:47:07,614 - dropdown_utils4 - INFO - 옵션 3: '등록D'
2025-06-17 14:47:07,621 - dropdown_utils4 - INFO - 옵션 4: '등록D'
2025-06-17 14:47:07,628 - dropdown_utils4 - INFO - 옵션 5: '쇼핑몰T'
2025-06-17 14:47:07,637 - dropdown_utils4 - INFO - 옵션 6: '쇼핑몰T'
2025-06-17 14:47:07,649 - dropdown_utils4 - INFO - 옵션 7: '쇼핑몰A1'
2025-06-17 14:47:07,655 - dropdown_utils4 - INFO - 옵션 8: '쇼핑몰A1'
2025-06-17 14:47:07,662 - dropdown_utils4 - INFO - 옵션 9: '쇼핑몰A2'
2025-06-17 14:47:07,669 - dropdown_utils4 - INFO - 옵션 10: '쇼핑몰A2'
2025-06-17 14:47:07,676 - dropdown_utils4 - INFO - 옵션 11: '쇼핑몰A3'
2025-06-17 14:47:07,684 - dropdown_utils4 - INFO - 옵션 12: '쇼핑몰A3'
2025-06-17 14:47:07,691 - dropdown_utils4 - INFO - 옵션 13: '쇼핑몰B1'
2025-06-17 14:47:07,699 - dropdown_utils4 - INFO - 옵션 14: '쇼핑몰B1'
2025-06-17 14:47:07,718 - dropdown_utils4 - INFO - 옵션 15: '쇼핑몰B2'
2025-06-17 14:47:07,725 - dropdown_utils4 - INFO - 옵션 16: '쇼핑몰B2'
2025-06-17 14:47:07,732 - dropdown_utils4 - INFO - 옵션 17: '쇼핑몰B3'
2025-06-17 14:47:07,739 - dropdown_utils4 - INFO - 옵션 18: '쇼핑몰B3'
2025-06-17 14:47:07,749 - dropdown_utils4 - INFO - 옵션 19: ''
2025-06-17 14:47:07,756 - dropdown_utils4 - INFO - 옵션 20: ''
2025-06-17 14:47:07,770 - dropdown_utils4 - INFO - 옵션 21: ''
2025-06-17 14:47:07,782 - dropdown_utils4 - INFO - 옵션 22: ''
2025-06-17 14:47:08,099 - dropdown_utils4 - INFO - 스크롤 후 22개 옵션 확인
2025-06-17 14:47:08,099 - dropdown_utils4 - INFO - 스크롤 3/30
2025-06-17 14:47:08,105 - dropdown_utils4 - INFO - 현재 화면에 22개의 옵션 발견
2025-06-17 14:47:08,110 - dropdown_utils4 - INFO - 옵션 1: ''
2025-06-17 14:47:08,115 - dropdown_utils4 - INFO - 옵션 2: ''
2025-06-17 14:47:08,120 - dropdown_utils4 - INFO - 옵션 3: '쇼핑몰C1'
2025-06-17 14:47:08,125 - dropdown_utils4 - INFO - 옵션 4: '쇼핑몰C1'
2025-06-17 14:47:08,131 - dropdown_utils4 - INFO - 옵션 5: '쇼핑몰C2'
2025-06-17 14:47:08,136 - dropdown_utils4 - INFO - 옵션 6: '쇼핑몰C2'
2025-06-17 14:47:08,141 - dropdown_utils4 - INFO - 옵션 7: '쇼핑몰C3'
2025-06-17 14:47:08,146 - dropdown_utils4 - INFO - 옵션 8: '쇼핑몰C3'
2025-06-17 14:47:08,152 - dropdown_utils4 - INFO - 옵션 9: '쇼핑몰D1'
2025-06-17 14:47:08,156 - dropdown_utils4 - INFO - 옵션 10: '쇼핑몰D1'
2025-06-17 14:47:08,161 - dropdown_utils4 - INFO - 옵션 11: '쇼핑몰D2'
2025-06-17 14:47:08,167 - dropdown_utils4 - INFO - 옵션 12: '쇼핑몰D2'
2025-06-17 14:47:08,172 - dropdown_utils4 - INFO - 옵션 13: '쇼핑몰D3'
2025-06-17 14:47:08,177 - dropdown_utils4 - INFO - 옵션 14: '쇼핑몰D3'
2025-06-17 14:47:08,183 - dropdown_utils4 - INFO - 옵션 15: '완료A1'
2025-06-17 14:47:08,189 - dropdown_utils4 - INFO - 옵션 16: '완료A1'
2025-06-17 14:47:08,194 - dropdown_utils4 - INFO - 옵션 17: '완료A2'
2025-06-17 14:47:08,200 - dropdown_utils4 - INFO - 옵션 18: '완료A2'
2025-06-17 14:47:08,206 - dropdown_utils4 - INFO - 옵션 19: ''
2025-06-17 14:47:08,211 - dropdown_utils4 - INFO - 옵션 20: ''
2025-06-17 14:47:08,217 - dropdown_utils4 - INFO - 옵션 21: ''
2025-06-17 14:47:08,222 - dropdown_utils4 - INFO - 옵션 22: ''
2025-06-17 14:47:08,533 - dropdown_utils4 - INFO - 스크롤 후 22개 옵션 확인
2025-06-17 14:47:08,533 - dropdown_utils4 - INFO - 스크롤 4/30
2025-06-17 14:47:08,539 - dropdown_utils4 - INFO - 현재 화면에 22개의 옵션 발견
2025-06-17 14:47:08,545 - dropdown_utils4 - INFO - 옵션 1: ''
2025-06-17 14:47:08,550 - dropdown_utils4 - INFO - 옵션 2: ''
2025-06-17 14:47:08,556 - dropdown_utils4 - INFO - 옵션 3: '완료A3'
2025-06-17 14:47:08,560 - dropdown_utils4 - INFO - 옵션 4: '완료A3'
2025-06-17 14:47:08,566 - dropdown_utils4 - INFO - 옵션 5: '완료B1'
2025-06-17 14:47:08,571 - dropdown_utils4 - INFO - 옵션 6: '완료B1'
2025-06-17 14:47:08,576 - dropdown_utils4 - INFO - 옵션 7: '완료B2'
2025-06-17 14:47:08,582 - dropdown_utils4 - INFO - 옵션 8: '완료B2'
2025-06-17 14:47:08,587 - dropdown_utils4 - INFO - 옵션 9: '완료B3'
2025-06-17 14:47:08,592 - dropdown_utils4 - INFO - 옵션 10: '완료B3'
2025-06-17 14:47:08,598 - dropdown_utils4 - INFO - 옵션 11: '완료C1'
2025-06-17 14:47:08,603 - dropdown_utils4 - INFO - 옵션 12: '완료C1'
2025-06-17 14:47:08,608 - dropdown_utils4 - INFO - 옵션 13: '완료C2'
2025-06-17 14:47:08,614 - dropdown_utils4 - INFO - 옵션 14: '완료C2'
2025-06-17 14:47:08,620 - dropdown_utils4 - INFO - 옵션 15: '완료C3'
2025-06-17 14:47:08,625 - dropdown_utils4 - INFO - 옵션 16: '완료C3'
2025-06-17 14:47:08,630 - dropdown_utils4 - INFO - 옵션 17: '완료D1'
2025-06-17 14:47:08,635 - dropdown_utils4 - INFO - 옵션 18: '완료D1'
2025-06-17 14:47:08,641 - dropdown_utils4 - INFO - 옵션 19: ''
2025-06-17 14:47:08,645 - dropdown_utils4 - INFO - 옵션 20: ''
2025-06-17 14:47:08,651 - dropdown_utils4 - INFO - 옵션 21: ''
2025-06-17 14:47:08,657 - dropdown_utils4 - INFO - 옵션 22: ''
2025-06-17 14:47:08,969 - dropdown_utils4 - INFO - 스크롤 후 22개 옵션 확인
2025-06-17 14:47:08,969 - dropdown_utils4 - INFO - 스크롤 5/30
2025-06-17 14:47:08,976 - dropdown_utils4 - INFO - 현재 화면에 22개의 옵션 발견
2025-06-17 14:47:08,982 - dropdown_utils4 - INFO - 옵션 1: ''
2025-06-17 14:47:08,986 - dropdown_utils4 - INFO - 옵션 2: ''
2025-06-17 14:47:08,991 - dropdown_utils4 - INFO - 옵션 3: '완료D2'
2025-06-17 14:47:08,997 - dropdown_utils4 - INFO - 옵션 4: '완료D2'
2025-06-17 14:47:09,003 - dropdown_utils4 - INFO - 옵션 5: '완료D3'
2025-06-17 14:47:09,008 - dropdown_utils4 - INFO - 옵션 6: '완료D3'
2025-06-17 14:47:09,014 - dropdown_utils4 - INFO - 옵션 7: '수동번역'
2025-06-17 14:47:09,018 - dropdown_utils4 - INFO - 옵션 8: '수동번역'
2025-06-17 14:47:09,023 - dropdown_utils4 - INFO - 옵션 9: '등록대기'
2025-06-17 14:47:09,029 - dropdown_utils4 - INFO - 옵션 10: '등록대기'
2025-06-17 14:47:09,034 - dropdown_utils4 - INFO - 옵션 11: '번역검수'
2025-06-17 14:47:09,040 - dropdown_utils4 - INFO - 옵션 12: '번역검수'
2025-06-17 14:47:09,044 - dropdown_utils4 - INFO - 옵션 13: '서버1'
2025-06-17 14:47:09,045 - dropdown_utils4 - INFO - 일치하는 그룹 발견: '서버1'
2025-06-17 14:47:10,093 - dropdown_utils4 - INFO - 그룹 '서버1' 선택 성공
2025-06-17 14:47:10,093 - dropdown_utils4 - INFO - 스크롤 5회 후 '서버1' 그룹을 찾았습니다.
2025-06-17 14:47:10,093 - dropdown_utils4 - INFO - 스크롤 후 '서버1' 그룹을 찾았습니다.      
2025-06-17 14:47:10,093 - dropdown_utils4 - INFO - 상품 수 변경 대기 시작 (초기: 41644개, 최 대 대기: 8초)
2025-06-17 14:47:10,106 - dropdown_utils4 - INFO - 전체 상품 수 텍스트 발견: '총 2,318개 상품'
2025-06-17 14:47:10,106 - dropdown_utils4 - INFO - 전체 상품 수 확인 성공: 2318개
2025-06-17 14:47:10,106 - dropdown_utils4 - INFO - 상품 수 변경 확인: 41644개 → 2318개       
2025-06-17 14:47:10,106 - dropdown_utils4 - INFO - 그룹 선택 확인됨: 상품 수 41644개 → 2318개로 감소
2025-06-17 14:47:10,106 - dropdown_utils4 - INFO - 상품검색 드롭박스에서 '서버1' 그룹 선택 완료
2025-06-17 14:47:10,107 - product_editor_core4 - INFO - 서버1 그룹 선택 성공
2025-06-17 14:47:10,107 - product_editor_core4 - INFO - 1-2. 50개씩 보기 설정
2025-06-17 14:47:10,107 - product_editor_core4 - INFO - 50개씩 보기 설정 시도 1/3
2025-06-17 14:47:10,107 - dropdown_utils4 - INFO - 페이지 크기 '50개씩 보기' 선택 시작       
2025-06-17 14:47:10,107 - dropdown_utils4 - INFO - 페이지 크기 드롭박스 열기 시도
2025-06-17 14:47:10,107 - dropdown_utils4 - INFO - 선택자 1 시도: (//div[contains(@class, 'ant-select-single')])[2]
2025-06-17 14:47:11,710 - dropdown_utils4 - INFO - 페이지 크기 드롭박스 열기 성공 (선택자 1)
2025-06-17 14:47:12,853 - dropdown_utils4 - INFO - 드롭박스 옵션 '50개씩 보기' 선택 성공
2025-06-17 14:47:12,854 - dropdown_utils4 - INFO - 페이지 크기 '50개씩 보기' 선택 완료
2025-06-17 14:47:12,854 - product_editor_core4 - INFO - 50개씩 보기 설정 성공
2025-06-17 14:47:14,879 - product_editor_core4 - INFO - 상품수 확인 중...
2025-06-17 14:47:15,273 - product_editor_core4 - INFO - 상품이 존재합니다
2025-06-17 14:47:15,274 - product_editor_core4 - INFO - 1-5. 전체 상품 선택
2025-06-17 14:47:15,274 - dropdown_utils4 - INFO - 전체선택 체크박스 클릭 시도
2025-06-17 14:47:15,274 - dropdown_utils4 - INFO - 체크박스 선택자 1 시도: //label[contains(@class, 'ant-checkbox-wrapper')]
2025-06-17 14:47:16,503 - dropdown_utils4 - INFO - 직접 클릭 성공
2025-06-17 14:47:16,503 - dropdown_utils4 - INFO - 전체선택 체크박스 클릭 성공 (선택자 1)
2025-06-17 14:47:16,504 - product_editor_core4 - INFO - 전체 상품 선택 완료
2025-06-17 14:47:16,505 - product_editor_core4 - INFO - 1-4. 일괄 번역 처리 시작
2025-06-17 14:47:16,505 - upload_utils - INFO - 일괄 번역 버튼 클릭 시도
2025-06-17 14:47:16,615 - upload_utils - INFO - 일괄 번역 버튼 클릭 성공: //button[.//span[text()='일괄 번역']]
2025-06-17 14:47:17,616 - upload_utils - INFO - 일괄 번역 모달창 처리 시작
2025-06-17 14:47:17,710 - upload_utils - INFO - 일괄 번역 모달창 감지됨: .ant-modal-content
2025-06-17 14:47:18,723 - upload_utils - INFO - 번역 횟수 텍스트 발견: '300회'
2025-06-17 14:47:18,723 - upload_utils - INFO - 추출된 번역 횟수: 300
2025-06-17 14:47:18,736 - upload_utils - INFO - 선택된 상품 텍스트: 선택 50개 상품
2025-06-17 14:47:18,737 - upload_utils - INFO - 선택된 상품 개수: 50개
2025-06-17 14:47:18,737 - upload_utils - INFO - 사용 가능한 번역 횟수: 300, 선택된 상품 수: 50
2025-06-17 14:47:18,737 - upload_utils - INFO - 번역 가능: 일괄 번역을 시작합니다
2025-06-17 14:47:18,737 - upload_utils - INFO - 일괄 번역 시작 버튼 클릭 시도
2025-06-17 14:47:18,808 - upload_utils - INFO - 일괄 번역 시작 버튼 클릭 성공: //div[contains(@class, 'ant-modal-content')]//button[.//span[text()='일괄 번역 시작']]
2025-06-17 14:47:19,809 - product_editor_core4 - INFO - 일괄 번역 처리 완료
2025-06-17 14:47:22,828 - product_editor_core4 - INFO - 일괄번역 후 3초 지연 완료
2025-06-17 14:47:22,834 - product_editor_core4 - INFO - 1-5. 전체 상품 선택
2025-06-17 14:47:22,835 - dropdown_utils4 - INFO - 전체선택 체크박스 클릭 시도
2025-06-17 14:47:22,837 - dropdown_utils4 - INFO - 체크박스 선택자 1 시도: //label[contains(@class, 'ant-checkbox-wrapper')]
2025-06-17 14:47:24,409 - dropdown_utils4 - INFO - 직접 클릭 성공
2025-06-17 14:47:24,409 - dropdown_utils4 - INFO - 전체선택 체크박스 클릭 성공 (선택자 1)
2025-06-17 14:47:24,409 - product_editor_core4 - INFO - 전체 상품 선택 완료
2025-06-17 14:47:24,410 - product_editor_core4 - INFO - 그룹지정 모달창을 열어서 '대기1' 그룹으로 이동
2025-06-17 14:47:24,410 - dropdown_utils4 - INFO - 그룹 지정 버튼 클릭
2025-06-17 14:47:24,410 - dropdown_utils4 - INFO - 그룹 지정 버튼 시도 1: //div[contains(@class, 'ant-btn-group')]//button[.//span[text()='그룹 지정']]
2025-06-17 14:47:26,079 - dropdown_utils4 - INFO - 그룹 이동 모달창이 열렸습니다.
2025-06-17 14:47:26,080 - product_editor_core4 - INFO - 그룹지정 모달창 열기 성공
2025-06-17 14:47:26,080 - dropdown_utils4 - INFO - 그룹 이동 모달창에서 '대기1' 그룹 선택    
2025-06-17 14:47:26,977 - dropdown_utils4 - INFO - '대기1' 그룹이 선택되었습니다.
2025-06-17 14:47:27,076 - dropdown_utils4 - INFO - 확인 버튼 클릭 완료
2025-06-17 14:47:29,222 - dropdown_utils4 - INFO - 그룹 이동 모달창이 정상적으로 닫혔습니다.
2025-06-17 14:47:29,222 - dropdown_utils4 - INFO - 그룹 이동 완료
2025-06-17 14:47:29,222 - product_editor_core4 - INFO - '대기1' 그룹으로 이동 완료
2025-06-17 14:47:29,222 - product_editor_core4 - INFO - 서버1 → 대기1 워크플로우 완료        
2025-06-17 14:47:29,223 - product_editor_core4 - INFO - === 사이클 1, 1단계: 서버1 → 대기1 처리 완료 ===

2025-06-17 14:47:29,223 - product_editor_core4 - INFO -
=== 사이클 1, 2단계: 서버2 → 대기2 처리 시작 ===
2025-06-17 14:47:29,223 - product_editor_core4 - INFO - 서버2 → 대기2 워크플로우 시작        
2025-06-17 14:47:29,223 - product_editor_core4 - INFO - 상품검색용 드롭박스에서 '서버2' 그룹 선택
2025-06-17 14:47:29,223 - product_editor_core4 - INFO - 서버2 그룹 선택 시도 1/3
2025-06-17 14:47:29,223 - dropdown_utils4 - INFO - 상품검색 드롭박스에서 '서버2' 그룹 선택 시작
2025-06-17 14:47:29,223 - dropdown_utils4 - INFO - 상품검색 드롭박스 열기 시도
2025-06-17 14:47:29,224 - dropdown_utils4 - INFO - 선택자 1 시도: (//div[contains(@class, 'ant-select-single')])[1]
2025-06-17 14:47:30,900 - dropdown_utils4 - INFO - 상품검색 드롭박스 열기 성공 (선택자 1)
2025-06-17 14:47:30,900 - dropdown_utils4 - INFO - 그룹 '서버2' 선택 시도
2025-06-17 14:47:30,914 - dropdown_utils4 - INFO - 전체 상품 수 텍스트 발견: '총 2,318개 상품'
2025-06-17 14:47:30,914 - dropdown_utils4 - INFO - 전체 상품 수 확인 성공: 2318개
2025-06-17 14:47:30,915 - dropdown_utils4 - INFO - 그룹 선택 전 전체 상품 수: 2318개
2025-06-17 14:47:30,924 - dropdown_utils4 - INFO - 현재 화면에 26개의 옵션 발견
2025-06-17 14:47:30,932 - dropdown_utils4 - INFO - 옵션 1: ''
2025-06-17 14:47:30,937 - dropdown_utils4 - INFO - 옵션 2: ''
2025-06-17 14:47:30,943 - dropdown_utils4 - INFO - 옵션 3: '완료D2'
2025-06-17 14:47:30,950 - dropdown_utils4 - INFO - 옵션 4: '완료D2'
2025-06-17 14:47:30,955 - dropdown_utils4 - INFO - 옵션 5: '완료D3'
2025-06-17 14:47:30,961 - dropdown_utils4 - INFO - 옵션 6: '완료D3'
2025-06-17 14:47:30,967 - dropdown_utils4 - INFO - 옵션 7: '수동번역'
2025-06-17 14:47:30,973 - dropdown_utils4 - INFO - 옵션 8: '수동번역'
2025-06-17 14:47:30,979 - dropdown_utils4 - INFO - 옵션 9: '등록대기'
2025-06-17 14:47:30,985 - dropdown_utils4 - INFO - 옵션 10: '등록대기'
2025-06-17 14:47:30,990 - dropdown_utils4 - INFO - 옵션 11: '번역검수'
2025-06-17 14:47:30,996 - dropdown_utils4 - INFO - 옵션 12: '번역검수'
2025-06-17 14:47:31,007 - dropdown_utils4 - INFO - 옵션 13: '서버1'
2025-06-17 14:47:31,045 - dropdown_utils4 - INFO - 옵션 14: '서버1'
2025-06-17 14:47:31,052 - dropdown_utils4 - INFO - 옵션 15: '서버2'
2025-06-17 14:47:31,052 - dropdown_utils4 - INFO - 일치하는 그룹 발견: '서버2'
2025-06-17 14:47:32,101 - dropdown_utils4 - INFO - 그룹 '서버2' 선택 성공
2025-06-17 14:47:32,101 - dropdown_utils4 - INFO - 그룹 '서버2' 선택 성공
2025-06-17 14:47:32,101 - dropdown_utils4 - INFO - 상품 수 변경 대기 시작 (초기: 2318개, 최대 대기: 8초)
2025-06-17 14:47:32,115 - dropdown_utils4 - INFO - 전체 상품 수 텍스트 발견: '총 1,388개 상품'
2025-06-17 14:47:32,115 - dropdown_utils4 - INFO - 전체 상품 수 확인 성공: 1388개
2025-06-17 14:47:32,115 - dropdown_utils4 - INFO - 상품 수 변경 확인: 2318개 → 1388개        
2025-06-17 14:47:32,115 - dropdown_utils4 - INFO - 그룹 선택 확인됨: 상품 수 2318개 → 1388개 로 감소
2025-06-17 14:47:32,115 - dropdown_utils4 - INFO - 상품검색 드롭박스에서 '서버2' 그룹 선택 완료
2025-06-17 14:47:32,116 - product_editor_core4 - INFO - 서버2 그룹 선택 성공
2025-06-17 14:47:32,116 - product_editor_core4 - INFO - 1-2. 50개씩 보기 설정
2025-06-17 14:47:32,116 - product_editor_core4 - INFO - 50개씩 보기 설정 시도 1/3
2025-06-17 14:47:32,116 - dropdown_utils4 - INFO - 페이지 크기 '50개씩 보기' 선택 시작       
2025-06-17 14:47:32,116 - dropdown_utils4 - INFO - 페이지 크기 드롭박스 열기 시도
2025-06-17 14:47:32,116 - dropdown_utils4 - INFO - 선택자 1 시도: (//div[contains(@class, 'ant-select-single')])[2]
2025-06-17 14:47:33,725 - dropdown_utils4 - INFO - 페이지 크기 드롭박스 열기 성공 (선택자 1)
2025-06-17 14:47:34,821 - dropdown_utils4 - INFO - 드롭박스 옵션 '50개씩 보기' 선택 성공
2025-06-17 14:47:34,821 - dropdown_utils4 - INFO - 페이지 크기 '50개씩 보기' 선택 완료
2025-06-17 14:47:34,821 - product_editor_core4 - INFO - 50개씩 보기 설정 성공
2025-06-17 14:47:36,824 - product_editor_core4 - INFO - 상품수 확인 중...
2025-06-17 14:47:37,102 - product_editor_core4 - INFO - 상품이 존재합니다
2025-06-17 14:47:37,103 - product_editor_core4 - INFO - 1-5. 전체 상품 선택
2025-06-17 14:47:37,103 - dropdown_utils4 - INFO - 전체선택 체크박스 클릭 시도
2025-06-17 14:47:37,103 - dropdown_utils4 - INFO - 체크박스 선택자 1 시도: //label[contains(@class, 'ant-checkbox-wrapper')]
2025-06-17 14:47:38,378 - dropdown_utils4 - INFO - 직접 클릭 성공
2025-06-17 14:47:38,378 - dropdown_utils4 - INFO - 전체선택 체크박스 클릭 성공 (선택자 1)
2025-06-17 14:47:38,379 - product_editor_core4 - INFO - 전체 상품 선택 완료
2025-06-17 14:47:38,380 - product_editor_core4 - INFO - 1-4. 일괄 번역 처리 시작
2025-06-17 14:47:38,381 - upload_utils - INFO - 일괄 번역 버튼 클릭 시도
2025-06-17 14:47:38,521 - upload_utils - INFO - 일괄 번역 버튼 클릭 성공: //button[.//span[text()='일괄 번역']]
2025-06-17 14:47:39,522 - upload_utils - INFO - 일괄 번역 모달창 처리 시작
2025-06-17 14:47:39,527 - upload_utils - INFO - 일괄 번역 모달창 감지됨: .ant-modal-content
2025-06-17 14:47:40,543 - upload_utils - INFO - 번역 횟수 텍스트 발견: '250회'
2025-06-17 14:47:40,543 - upload_utils - INFO - 추출된 번역 횟수: 250
2025-06-17 14:47:40,574 - upload_utils - INFO - 선택된 상품 텍스트: 선택 50개 상품
2025-06-17 14:47:40,574 - upload_utils - INFO - 선택된 상품 개수: 50개
2025-06-17 14:47:40,575 - upload_utils - INFO - 사용 가능한 번역 횟수: 250, 선택된 상품 수: 50
2025-06-17 14:47:40,575 - upload_utils - INFO - 번역 가능: 일괄 번역을 시작합니다
2025-06-17 14:47:40,575 - upload_utils - INFO - 일괄 번역 시작 버튼 클릭 시도
2025-06-17 14:47:40,690 - upload_utils - INFO - 일괄 번역 시작 버튼 클릭 성공: //div[contains(@class, 'ant-modal-content')]//button[.//span[text()='일괄 번역 시작']]
2025-06-17 14:47:41,691 - product_editor_core4 - INFO - 일괄 번역 처리 완료
2025-06-17 14:47:44,719 - product_editor_core4 - INFO - 일괄번역 후 3초 지연 완료
2025-06-17 14:47:44,770 - product_editor_core4 - INFO - 1-5. 전체 상품 선택
2025-06-17 14:47:44,785 - dropdown_utils4 - INFO - 전체선택 체크박스 클릭 시도
2025-06-17 14:47:44,802 - dropdown_utils4 - INFO - 체크박스 선택자 1 시도: //label[contains(@class, 'ant-checkbox-wrapper')]
2025-06-17 14:47:46,544 - dropdown_utils4 - INFO - 직접 클릭 성공
2025-06-17 14:47:46,545 - dropdown_utils4 - INFO - 전체선택 체크박스 클릭 성공 (선택자 1)
2025-06-17 14:47:46,545 - product_editor_core4 - INFO - 전체 상품 선택 완료
2025-06-17 14:47:46,546 - product_editor_core4 - INFO - 그룹지정 모달창을 열어서 '대기2' 그룹으로 이동
2025-06-17 14:47:46,546 - dropdown_utils4 - INFO - 그룹 지정 버튼 클릭
2025-06-17 14:47:46,546 - dropdown_utils4 - INFO - 그룹 지정 버튼 시도 1: //div[contains(@class, 'ant-btn-group')]//button[.//span[text()='그룹 지정']]
2025-06-17 14:47:48,542 - dropdown_utils4 - INFO - 그룹 이동 모달창이 열렸습니다.
2025-06-17 14:47:48,542 - product_editor_core4 - INFO - 그룹지정 모달창 열기 성공
2025-06-17 14:47:48,542 - dropdown_utils4 - INFO - 그룹 이동 모달창에서 '대기2' 그룹 선택
2025-06-17 14:47:49,286 - dropdown_utils4 - INFO - '대기2' 그룹이 선택되었습니다.
2025-06-17 14:47:49,344 - dropdown_utils4 - INFO - 확인 버튼 클릭 완료
2025-06-17 14:47:51,598 - dropdown_utils4 - INFO - 그룹 이동 모달창이 정상적으로 닫혔습니다.
2025-06-17 14:47:51,598 - dropdown_utils4 - INFO - 그룹 이동 완료
2025-06-17 14:47:51,599 - product_editor_core4 - INFO - '대기2' 그룹으로 이동 완료
2025-06-17 14:47:51,599 - product_editor_core4 - INFO - 서버2 → 대기2 워크플로우 완료        
2025-06-17 14:47:51,599 - product_editor_core4 - INFO - === 사이클 1, 2단계: 서버2 → 대기2 처리 완료 ===

2025-06-17 14:47:51,599 - product_editor_core4 - INFO -
=== 사이클 1, 3단계: 서버3 → 대기3 처리 시작 ===
2025-06-17 14:47:51,599 - product_editor_core4 - INFO - 서버3 → 대기3 워크플로우 시작        
2025-06-17 14:47:51,599 - product_editor_core4 - INFO - 상품검색용 드롭박스에서 '서버3' 그룹 선택
2025-06-17 14:47:51,600 - product_editor_core4 - INFO - 서버3 그룹 선택 시도 1/3
2025-06-17 14:47:51,600 - dropdown_utils4 - INFO - 상품검색 드롭박스에서 '서버3' 그룹 선택 시작
2025-06-17 14:47:51,600 - dropdown_utils4 - INFO - 상품검색 드롭박스 열기 시도
2025-06-17 14:47:51,600 - dropdown_utils4 - INFO - 선택자 1 시도: (//div[contains(@class, 'ant-select-single')])[1]
2025-06-17 14:47:53,216 - dropdown_utils4 - INFO - 상품검색 드롭박스 열기 성공 (선택자 1)
2025-06-17 14:47:53,216 - dropdown_utils4 - INFO - 그룹 '서버3' 선택 시도
2025-06-17 14:47:53,252 - dropdown_utils4 - INFO - 전체 상품 수 텍스트 발견: '총 1,388개 상품'
2025-06-17 14:47:53,252 - dropdown_utils4 - INFO - 전체 상품 수 확인 성공: 1388개
2025-06-17 14:47:53,252 - dropdown_utils4 - INFO - 그룹 선택 전 전체 상품 수: 1388개
2025-06-17 14:47:53,259 - dropdown_utils4 - INFO - 현재 화면에 26개의 옵션 발견
2025-06-17 14:47:53,265 - dropdown_utils4 - INFO - 옵션 1: ''
2025-06-17 14:47:53,270 - dropdown_utils4 - INFO - 옵션 2: ''
2025-06-17 14:47:53,275 - dropdown_utils4 - INFO - 옵션 3: '완료D2'
2025-06-17 14:47:53,284 - dropdown_utils4 - INFO - 옵션 4: '완료D2'
2025-06-17 14:47:53,289 - dropdown_utils4 - INFO - 옵션 5: '완료D3'
2025-06-17 14:47:53,293 - dropdown_utils4 - INFO - 옵션 6: '완료D3'
2025-06-17 14:47:53,300 - dropdown_utils4 - INFO - 옵션 7: '수동번역'
2025-06-17 14:47:53,305 - dropdown_utils4 - INFO - 옵션 8: '수동번역'
2025-06-17 14:47:53,310 - dropdown_utils4 - INFO - 옵션 9: '등록대기'
2025-06-17 14:47:53,316 - dropdown_utils4 - INFO - 옵션 10: '등록대기'
2025-06-17 14:47:53,322 - dropdown_utils4 - INFO - 옵션 11: '번역검수'
2025-06-17 14:47:53,333 - dropdown_utils4 - INFO - 옵션 12: '번역검수'
2025-06-17 14:47:53,356 - dropdown_utils4 - INFO - 옵션 13: '서버1'
2025-06-17 14:47:53,375 - dropdown_utils4 - INFO - 옵션 14: '서버1'
2025-06-17 14:47:53,406 - dropdown_utils4 - INFO - 옵션 15: '서버2'
2025-06-17 14:47:53,412 - dropdown_utils4 - INFO - 옵션 16: '서버2'
2025-06-17 14:47:53,428 - dropdown_utils4 - INFO - 옵션 17: '서버3'
2025-06-17 14:47:53,428 - dropdown_utils4 - INFO - 일치하는 그룹 발견: '서버3'
2025-06-17 14:47:54,504 - dropdown_utils4 - INFO - 그룹 '서버3' 선택 성공
2025-06-17 14:47:54,505 - dropdown_utils4 - INFO - 그룹 '서버3' 선택 성공
2025-06-17 14:47:54,505 - dropdown_utils4 - INFO - 상품 수 변경 대기 시작 (초기: 1388개, 최대 대기: 8초)
2025-06-17 14:47:54,518 - dropdown_utils4 - INFO - 전체 상품 수 텍스트 발견: '총 2,934개 상품'
2025-06-17 14:47:54,518 - dropdown_utils4 - INFO - 전체 상품 수 확인 성공: 2934개
2025-06-17 14:47:54,518 - dropdown_utils4 - INFO - 상품 수 변경 확인: 1388개 → 2934개        
2025-06-17 14:47:54,518 - dropdown_utils4 - WARNING - 상품 수가 예상과 다름: 1388개 → 2934개 
2025-06-17 14:47:54,518 - dropdown_utils4 - INFO - 상품검색 드롭박스에서 '서버3' 그룹 선택 완료
2025-06-17 14:47:54,519 - product_editor_core4 - INFO - 서버3 그룹 선택 성공
2025-06-17 14:47:54,519 - product_editor_core4 - INFO - 1-2. 50개씩 보기 설정
2025-06-17 14:47:54,519 - product_editor_core4 - INFO - 50개씩 보기 설정 시도 1/3
2025-06-17 14:47:54,519 - dropdown_utils4 - INFO - 페이지 크기 '50개씩 보기' 선택 시작       
2025-06-17 14:47:54,519 - dropdown_utils4 - INFO - 페이지 크기 드롭박스 열기 시도
2025-06-17 14:47:54,519 - dropdown_utils4 - INFO - 선택자 1 시도: (//div[contains(@class, 'ant-select-single')])[2]
2025-06-17 14:47:56,145 - dropdown_utils4 - INFO - 페이지 크기 드롭박스 열기 성공 (선택자 1)
2025-06-17 14:47:57,673 - dropdown_utils4 - INFO - 드롭박스 옵션 '50개씩 보기' 선택 성공
2025-06-17 14:47:57,673 - dropdown_utils4 - INFO - 페이지 크기 '50개씩 보기' 선택 완료
2025-06-17 14:47:57,673 - product_editor_core4 - INFO - 50개씩 보기 설정 성공
2025-06-17 14:47:59,673 - product_editor_core4 - INFO - 상품수 확인 중...
2025-06-17 14:47:59,697 - product_editor_core4 - INFO - 상품이 존재합니다
2025-06-17 14:47:59,698 - product_editor_core4 - INFO - 1-5. 전체 상품 선택
2025-06-17 14:47:59,698 - dropdown_utils4 - INFO - 전체선택 체크박스 클릭 시도
2025-06-17 14:47:59,698 - dropdown_utils4 - INFO - 체크박스 선택자 1 시도: //label[contains(@class, 'ant-checkbox-wrapper')]
2025-06-17 14:48:00,792 - dropdown_utils4 - INFO - 직접 클릭 성공
2025-06-17 14:48:00,793 - dropdown_utils4 - INFO - 전체선택 체크박스 클릭 성공 (선택자 1)
2025-06-17 14:48:00,793 - product_editor_core4 - INFO - 전체 상품 선택 완료
2025-06-17 14:48:00,794 - product_editor_core4 - INFO - 1-4. 일괄 번역 처리 시작
2025-06-17 14:48:00,794 - upload_utils - INFO - 일괄 번역 버튼 클릭 시도
2025-06-17 14:48:00,895 - upload_utils - INFO - 일괄 번역 버튼 클릭 성공: //button[.//span[text()='일괄 번역']]
2025-06-17 14:48:01,895 - upload_utils - INFO - 일괄 번역 모달창 처리 시작
2025-06-17 14:48:01,921 - upload_utils - INFO - 일괄 번역 모달창 감지됨: .ant-modal-content
2025-06-17 14:48:02,935 - upload_utils - INFO - 번역 횟수 텍스트 발견: '200회'
2025-06-17 14:48:02,935 - upload_utils - INFO - 추출된 번역 횟수: 200
2025-06-17 14:48:02,947 - upload_utils - INFO - 선택된 상품 텍스트: 선택 50개 상품
2025-06-17 14:48:02,948 - upload_utils - INFO - 선택된 상품 개수: 50개
2025-06-17 14:48:02,948 - upload_utils - INFO - 사용 가능한 번역 횟수: 200, 선택된 상품 수: 50
2025-06-17 14:48:02,948 - upload_utils - INFO - 번역 가능: 일괄 번역을 시작합니다
2025-06-17 14:48:02,948 - upload_utils - INFO - 일괄 번역 시작 버튼 클릭 시도
2025-06-17 14:48:03,021 - upload_utils - INFO - 일괄 번역 시작 버튼 클릭 성공: //div[contains(@class, 'ant-modal-content')]//button[.//span[text()='일괄 번역 시작']]
2025-06-17 14:48:04,022 - product_editor_core4 - INFO - 일괄 번역 처리 완료
2025-06-17 14:48:07,052 - product_editor_core4 - INFO - 일괄번역 후 3초 지연 완료
2025-06-17 14:48:07,060 - product_editor_core4 - INFO - 1-5. 전체 상품 선택
2025-06-17 14:48:07,099 - dropdown_utils4 - INFO - 전체선택 체크박스 클릭 시도
2025-06-17 14:48:07,114 - dropdown_utils4 - INFO - 체크박스 선택자 1 시도: //label[contains(@class, 'ant-checkbox-wrapper')]
2025-06-17 14:48:08,626 - dropdown_utils4 - INFO - 직접 클릭 성공
2025-06-17 14:48:08,626 - dropdown_utils4 - INFO - 전체선택 체크박스 클릭 성공 (선택자 1)
2025-06-17 14:48:08,626 - product_editor_core4 - INFO - 전체 상품 선택 완료
2025-06-17 14:48:08,627 - product_editor_core4 - INFO - 그룹지정 모달창을 열어서 '대기3' 그룹으로 이동
2025-06-17 14:48:08,627 - dropdown_utils4 - INFO - 그룹 지정 버튼 클릭
2025-06-17 14:48:08,627 - dropdown_utils4 - INFO - 그룹 지정 버튼 시도 1: //div[contains(@class, 'ant-btn-group')]//button[.//span[text()='그룹 지정']]
2025-06-17 14:48:10,719 - dropdown_utils4 - INFO - 그룹 이동 모달창이 열렸습니다.
2025-06-17 14:48:10,720 - product_editor_core4 - INFO - 그룹지정 모달창 열기 성공
2025-06-17 14:48:10,720 - dropdown_utils4 - INFO - 그룹 이동 모달창에서 '대기3' 그룹 선택    
2025-06-17 14:48:11,312 - dropdown_utils4 - INFO - '대기3' 그룹이 선택되었습니다.
2025-06-17 14:48:11,373 - dropdown_utils4 - INFO - 확인 버튼 클릭 완료
2025-06-17 14:48:13,541 - dropdown_utils4 - INFO - 그룹 이동 모달창이 정상적으로 닫혔습니다.
2025-06-17 14:48:13,541 - dropdown_utils4 - INFO - 그룹 이동 완료
2025-06-17 14:48:13,541 - product_editor_core4 - INFO - '대기3' 그룹으로 이동 완료
2025-06-17 14:48:13,542 - product_editor_core4 - INFO - 서버3 → 대기3 워크플로우 완료        
2025-06-17 14:48:13,542 - product_editor_core4 - INFO - === 사이클 1, 3단계: 서버3 → 대기3 처리 완료 ===

2025-06-17 14:48:13,542 - product_editor_core4 - INFO - *** 사이클 1 완료 ***
2025-06-17 14:48:13,542 - product_editor_core4 - INFO - 번역 가능 횟수 확인을 위해 일괄 번역 모달을 임시로 엽니다
2025-06-17 14:48:13,542 - product_editor_core4 - INFO - 1-5. 전체 상품 선택
2025-06-17 14:48:13,542 - dropdown_utils4 - INFO - 전체선택 체크박스 클릭 시도
2025-06-17 14:48:13,542 - dropdown_utils4 - INFO - 체크박스 선택자 1 시도: //label[contains(@class, 'ant-checkbox-wrapper')]
2025-06-17 14:48:14,638 - dropdown_utils4 - INFO - 직접 클릭 성공
2025-06-17 14:48:14,638 - dropdown_utils4 - INFO - 전체선택 체크박스 클릭 성공 (선택자 1)    
2025-06-17 14:48:14,638 - product_editor_core4 - INFO - 전체 상품 선택 완료
2025-06-17 14:48:14,639 - upload_utils - INFO - 일괄 번역 버튼 클릭 시도
2025-06-17 14:48:14,721 - upload_utils - INFO - 일괄 번역 버튼 클릭 성공: //button[.//span[text()='일괄 번역']]
2025-06-17 14:48:15,765 - upload_utils - ERROR - 번역 횟수를 찾을 수 없습니다
2025-06-17 14:48:15,765 - upload_utils - INFO - 일괄 번역 모달창 닫기 시도
2025-06-17 14:49:25,097 - upload_utils - INFO - 일괄 번역 모달 닫기 버튼 클릭 성공: //div[contains(@class, 'ant-modal-content')]//button[.//span[text()='닫기']]
2025-06-17 14:49:25,598 - product_editor_core4 - WARNING - 번역 가능 횟수 확인 실패
2025-06-17 14:49:25,617 - product_editor_core4 - WARNING - 번역 가능 횟수를 확인할 수 없어 워크플로우를 종료합니다
2025-06-17 14:49:25,631 - percenty_new_step4 - INFO - 4단계 자동화가 성공적으로 완료되었습니 다.
2025-06-17 14:49:25,704 - core.steps.step4_core - INFO - 4단계 자동화 성공
2025-06-17 14:49:25,775 - core.steps.step4_core - INFO - 계정 2 4단계 자동화 완료: 4단계 자동화가 성공적으로 완료되었습니다
2025-06-17 14:49:25,855 - core.steps.step4_core - INFO - 브라우저 드라이버 종료
2025-06-17 14:49:32,127 - core.browser.browser_manager - INFO - 브라우저 'wop31garam@gmail.com_browser' 종료 완료
2025-06-17 14:49:32,127 - batch.batch_manager - INFO - _execute_step_for_account 호출 후: result={'success': True, 'processed': 0, 'failed': 0, 'errors': [], 'should_stop_batch': True}
2025-06-17 14:49:32,127 - batch.batch_manager - INFO - 결과 저장 완료: account_id=wop31garam@gmail.com
2025-06-17 14:49:32,127 - batch.batch_manager - INFO - 계정 'wop31garam@gmail.com' 작업 완료: 0개 처리
2025-06-17 14:49:32,127 - batch.batch_manager - INFO - 계정 wop31garam@gmail.com 처리 완료 시간: 2025-06-17 14:49:32
2025-06-17 14:49:32,128 - batch.batch_manager - INFO - 순차 실행 완료 - 작업 ID: single_step_4_20250617_144548, 소요시간: 223.20초
2025-06-17 14:49:32,128 - batch.batch_manager - INFO - 순차 실행 완료 시간: 2025-06-17 14:49:32
2025-06-17 14:49:32,128 - batch.batch_manager - INFO - _run_sequential_single_step 호출 후 시간: 2025-06-17 14:49:32
2025-06-17 14:49:32,128 - batch.batch_manager - INFO -
2025-06-17 14:49:32,128 - batch.batch_manager - INFO - 📊 === 배치 실행 결과 상세 정보 ===   
2025-06-17 14:49:32,128 - batch.batch_manager - INFO -
2025-06-17 14:49:32,129 - batch.batch_manager - INFO - 📋 계정 wop31garam@gmail.com 결과:    
2025-06-17 14:49:32,129 - batch.batch_manager - INFO -    • ⚠️ 상품 수량 정보를 확인할 수 없  습니다
2025-06-17 14:49:32,129 - batch.batch_manager - INFO -    • 성공 여부: ✅ 성공
2025-06-17 14:49:32,129 - batch.batch_manager - INFO - 📊 === 배치 실행 결과 상세 정보 완료 ===
2025-06-17 14:49:32,129 - batch.batch_manager - INFO -
2025-06-17 14:49:32,129 - batch.batch_manager - INFO - 보고서 생성 시작 - task_id: single_step_4_20250617_144548
2025-06-17 14:49:32,129 - batch.batch_manager - INFO - 보고서 생성기 상태: <batch.batch_manager.BatchReportGenerator object at 0x0000011630F4B770>
2025-06-17 14:49:32,129 - batch.batch_manager - INFO - 보고서 디렉토리: logs\reports\20250617_144548
2025-06-17 14:49:32,130 - batch.batch_manager - INFO - 보고서 생성에 전달되는 result 데이터: {'task_id': 'single_step_4_20250617_144548', 'success': True, 'start_time': datetime.datetime(2025, 6, 17, 14, 45, 48, 930278), 'results': {'wop31garam@gmail.com': {'success': True, 'processed': 0, 'failed': 0, 'errors': [], 'should_stop_batch': True}}, 'end_time': datetime.datetime(2025, 6, 17, 14, 49, 32, 128124), 'duration': 223.197846}
2025-06-17 14:49:32,130 - batch.batch_manager - INFO - result 타입: <class 'dict'>
2025-06-17 14:49:32,130 - batch.batch_manager - INFO - result.get('results'): {'wop31garam@gmail.com': {'success': True, 'processed': 0, 'failed': 0, 'errors': [], 'should_stop_batch': True}}
2025-06-17 14:49:32,131 - batch.batch_manager - INFO - 배치 보고서 생성 완료: logs\reports\20250617_144548\batch_report_single_step_4_20250617_144548.md
2025-06-17 14:49:32,131 - ✅ 배치 실행 완료 - 성공: 1/1개 계정, 처리: 0개

============================================================
🚀 배치 실행 완료 - 통합 요약 보고서
============================================================
📋 작업 ID: single_step_4_20250617_144548
⏱️  소요 시간: 223.20초
📅 실행 시간: 2025-06-17 14:45:48.930278
🎯 전체 실행 결과: ✅ 성공

--------------------------------------------------
📊 계정별 상세 결과
--------------------------------------------------

✅ wop31garam@gmail.com
   처리 완료: 0개
   처리 실패: 0개

==================================================
📈 전체 통계 요약
==================================================
🏢 총 계정 수: 1개
✅ 성공한 계정: 1개
❌ 실패한 계정: 0개
📦 총 처리 완료: 0개
⚠️  총 처리 실패: 0개
🎯 성공률: 100.0%

--------------------------------------------------
📁 상세 로그 파일 위치
--------------------------------------------------
📋 계정별 로그: logs/accounts/2025-06-17 14:45:48.930278/
⚠️  에러 로그: logs/errors/2025-06-17 14:45:48.930278/
📊 보고서: logs/reports/2025-06-17 14:45:48.930278/

============================================================
🎉 배치 실행 완료!
============================================================
2025-06-17 14:49:32,135 - 📊 통합 요약 보고서 생성 완료: logs\unified\20250617_144548\execution_summary.md

📁 통합 로그 파일: logs\unified\20250617_144548\batch_execution.log
📊 통합 요약 보고서: logs\unified\20250617_144548\execution_summary.md
2025-06-17 14:49:32,136 - core.browser.browser_manager - INFO - 모든 브라우저 종료 완료      
2025-06-17 14:49:32,136 - core.browser.browser_manager - INFO - 브라우저 관리자 정리 완료    
2025-06-17 14:49:32,136 - batch.batch_manager - INFO - 배치 관리자 정리 완료
2025-06-17 14:49:32,136 - 🏁 배치 세션 종료: 20250617_144548
PS C:\Projects\percenty_project> 
PS C:\Projects\percenty_project>