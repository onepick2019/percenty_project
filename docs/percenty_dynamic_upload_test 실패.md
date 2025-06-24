PS C:\Projects\percenty_project> python percenty_dynamic_upload_test.py

============================================================
퍼센티 동적 업로드 테스트 시작
============================================================
2025-06-23 10:40:40,652 - coordinates.coordinate_conversion - INFO - 좌표 변환 공식: 개선된 비선형 변환 적용 - X축/Y축 화면 위치별 보정
2025-06-23 10:40:40,652 - coordinates.coordinate_conversion - INFO - X축 좌측 영역(321-750) 보정 계수 적용 (0.99)
2025-06-23 10:40:40,652 - coordinates.coordinate_conversion - INFO - Y축 중앙 영역(491-540) 보정 계수 적용 (0.94)
2025-06-23 10:40:40,652 - coordinates.coordinate_conversion - INFO - 변환 상세 정보 - 브라우저 크기: 1903x971, 참조 크기: 1920x1080
2025-06-23 10:40:40,652 - coordinates.coordinate_conversion - INFO - X축 계산: int(1903 * (410 / 1920) * 0.99) = 402
2025-06-23 10:40:40,652 - coordinates.coordinate_conversion - INFO - Y축 계산: int(971 * (495 / 1080) * 0.94) = 418
2025-06-23 10:40:40,653 - coordinates.coordinate_conversion - INFO - 좌표 변환: (410, 495) -> (402, 418)
2025-06-23 10:40:40,654 - coordinates.coordinate_conversion - INFO - 좌표 변환 공식: 개선된 비선형 변환 적용 - X축/Y축 화면 위치별 보정
2025-06-23 10:40:40,655 - coordinates.coordinate_conversion - INFO - X축 좌측 영역(321-750) 보정 계수 적용 (0.99)
2025-06-23 10:40:40,655 - coordinates.coordinate_conversion - INFO - Y축 중상단 영역(331-440) 보정 계수 적용 (0.89)
2025-06-23 10:40:40,655 - coordinates.coordinate_conversion - INFO - 변환 상세 정보 - 브라우저 크기: 1903x971, 참조 크기: 1920x1080
2025-06-23 10:40:40,655 - coordinates.coordinate_conversion - INFO - X축 계산: int(1903 * (402 / 1920) * 0.99) = 394
2025-06-23 10:40:40,655 - coordinates.coordinate_conversion - INFO - Y축 계산: int(971 * (418 / 1080) * 0.89) = 334
2025-06-23 10:40:40,655 - coordinates.coordinate_conversion - INFO - 좌표 변환: (402, 418) -> (394, 334)

1. 계정 관리자 초기화...
2. 계정 정보 로드...
2025-06-23 10:40:41,139 - root - INFO - 총 7개의 계정을 로드했습니다.
3. 계정 선택...

==================================================
퍼센티 계정 목록
==================================================
1. 계정 1 (onepick2019@gmail.com)
2. 계정 2 (wop31garam@gmail.com)
3. 계정 3 (wop32gsung@gmail.com)
4. 계정 4 (wop33gogos@gmail.com)
5. 계정 5 (wop34goyos@gmail.com)
6. 계정 6 (wop35goens@gmail.com)
7. 계정 7 (wop36gurum@gmail.com)
==================================================

사용할 계정 번호를 입력하세요 (종료하려면 'q' 입력): 1

'계정 1' 계정을 선택했습니다.

4. 로그인 객체 생성...
   선택한 계정: 계정 1
2025-06-23 10:40:42,635 - root - INFO - === PercentyLogin __init__ 시작 ===
2025-06-23 10:40:42,635 - root - INFO - 전달받은 driver: False
2025-06-23 10:40:42,636 - root - INFO - 전달받은 account: {'id': 'onepick2019@gmail.com', 'password': 'qnwkehlwk8*', 'nickname': '계정 1', 'operator': '김기한', 'server': 'server1'}
2025-06-23 10:40:42,636 - root - INFO - 기본 속성 설정 완료
2025-06-23 10:40:42,636 - root - INFO - 화면 해상도 확인 시작
2025-06-23 10:40:42,636 - root - INFO - tkinter import 시작
2025-06-23 10:40:42,636 - root - INFO - tkinter import 완료
2025-06-23 10:40:42,636 - root - INFO - tkinter root 생성 시작
2025-06-23 10:40:42,699 - root - INFO - tkinter root 생성 완료
2025-06-23 10:40:42,699 - root - INFO - tkinter root withdraw 시작
2025-06-23 10:40:42,699 - root - INFO - tkinter root withdraw 완료
2025-06-23 10:40:42,700 - root - INFO - 화면 크기 측정 시작
2025-06-23 10:40:42,700 - root - INFO - 화면 크기 측정 완료: 1920x1080
2025-06-23 10:40:42,700 - root - INFO - tkinter root destroy 시작
2025-06-23 10:40:42,703 - root - INFO - tkinter root destroy 완료
2025-06-23 10:40:42,704 - root - INFO - tkinter로 화면 해상도 확인 성공: 1920x1080
2025-06-23 10:40:42,704 - root - INFO - 창 크기 및 위치 설정 시작
2025-06-23 10:40:42,704 - root - INFO - 화면 해상도: 1920x1080
2025-06-23 10:40:42,704 - root - INFO - 브라우저 창 크기: 1920x1080
2025-06-23 10:40:42,704 - root - INFO - 브라우저 창 위치: x=0, y=0
2025-06-23 10:40:42,704 - root - INFO - 브라우저 코어 및 모달 코어 초기화 시작
2025-06-23 10:40:42,704 - root - INFO - 기본 코어 속성 설정 완료
2025-06-23 10:40:42,704 - root - INFO - === PercentyLogin __init__ 완료 ===
5. 웹드라이버 설정...
2025-06-23 10:40:42,706 - root - INFO - ===== 브라우저 설정 시작 =====
2025-06-23 10:40:42,707 - root - INFO - 일반 모드로 브라우저 설정
2025-06-23 10:40:42,707 - root - INFO - GUI 모드: Windows 호환성 Chrome 옵션 적용
2025-06-23 10:40:42,707 - root - INFO - Selenium Manager를 사용하여 Chrome 드라이버 자동 설정 시작
2025-06-23 10:40:42,707 - root - INFO - Chrome 드라이버 생성 시도 중...
2025-06-23 10:40:42,707 - root - INFO - webdriver.Chrome() 호출 시작

DevTools listening on ws://127.0.0.1:56763/devtools/browser/b7aa7e4b-8aa3-43e0-8583-2c2814961bdd
2025-06-23 10:40:44,008 - root - INFO - webdriver.Chrome() 호출 완료
2025-06-23 10:40:44,008 - root - INFO - result_queue에 driver 저장 완료
2025-06-23 10:40:44,009 - root - INFO - Chrome 드라이버 생성 완료 (소요시간: 1.30초)
2025-06-23 10:40:44,009 - root - INFO - 브라우저 창 크기 및 위치 정보 수집 시작
2025-06-23 10:40:44,013 - root - INFO - 초기 창 크기: 1920x1080
2025-06-23 10:40:44,014 - root - INFO - 초기 창 위치: x=0, y=0
2025-06-23 10:40:44,014 - root - INFO - 브라우저 전체화면으로 전환 시도
2025-06-23 10:40:44,044 - root - INFO - maximize_window() 호출 완료
2025-06-23 10:40:45,045 - root - INFO - 전체화면 전환 대기 완료
2025-06-23 10:40:45,061 - root - INFO - 전체화면 후 창 크기: 1936x1048
2025-06-23 10:40:45,061 - root - INFO - 전체화면 후 창 위치: x=-8, y=-8
2025-06-23 10:40:45,062 - root - INFO - JavaScript를 사용하여 브라우저 내부 크기 측정 시작
2025-06-23 10:40:45,067 - root - INFO - innerWidth 측정 완료: 1920
2025-06-23 10:40:45,071 - root - INFO - innerHeight 측정 완료: 945
2025-06-23 10:40:45,072 - root - INFO - 브라우저 내부 크기: 1920x945
2025-06-23 10:40:45,074 - root - INFO - JavaScript 실행 가능: True
2025-06-23 10:40:45,075 - root - INFO - ===== 브라우저 설정 완료 =====
6. 로그인 시도...
2025-06-23 10:40:45,077 - root - INFO - 퍼센티 로그인 페이지 열기: https://www.percenty.co.kr/signin (시도 1/3)
2025-06-23 10:40:45,077 - root - INFO - https://www.percenty.co.kr/signin 열기 (시도 1/3)
2025-06-23 10:40:48,730 - root - INFO - 시간 지연 5초 - 로그인 페이지 로드 대기
WARNING: All log messages before absl::InitializeLog() is called are written to STDERR
I0000 00:00:1750642850.751473   21716 voice_transcription.cc:58] Registering VoiceTranscriptionCapability
2025-06-23 10:40:53,731 - root - INFO - 시간 지연 완료 (5초) - 로그인 페이지 로드 대기
2025-06-23 10:40:53,737 - root - INFO - 표시된 알림이 없습니다.
2025-06-23 10:40:53,737 - root - INFO - 비밀번호 저장 모달창 확인 중...
2025-06-23 10:40:53,743 - root - INFO - 모달창 확인 결과: {'chromeModal': False, 'genericModal': False, 'visibleModal': False}
2025-06-23 10:40:53,743 - root - INFO - 표시된 비밀번호 저장 모달창이 없습니다.
2025-06-23 10:40:53,748 - root - INFO - 비밀번호 저장 관련 설정 적용 결과: {'storage': 'set', 'success': True}
2025-06-23 10:40:53,748 - root - INFO - 페이지 로딩 대기
2025-06-23 10:40:53,748 - root - INFO - 시간 지연 5초 - 페이지 로딩 대기
Created TensorFlow Lite XNNPACK delegate for CPU.
2025-06-23 10:40:58,748 - root - INFO - 시간 지연 완료 (5초) - 페이지 로딩 대기
2025-06-23 10:40:58,748 - root - INFO - 아이디 입력: onepick2019@gmail.com
2025-06-23 10:40:58,748 - root - WARNING - UI_ELEMENTS에서 LOGIN_EMAIL_FIELD를 찾을 수 없습니다. 수동으로 정의합니다.
2025-06-23 10:40:58,897 - root - INFO - unknown element - DOM 선택자로 텍스트 입력 성공: onepick2019@gmail.com
2025-06-23 10:40:58,897 - root - INFO - smart_click으로 아이디 필드 입력 성공: dom_input
2025-06-23 10:40:58,897 - root - INFO - 시간 지연 1초 - 텍스트 입력 후
2025-06-23 10:40:59,897 - root - INFO - 시간 지연 완료 (1초) - 텍스트 입력 후
2025-06-23 10:40:59,898 - root - INFO - 비밀번호 입력 시도
2025-06-23 10:40:59,898 - root - WARNING - UI_ELEMENTS에서 LOGIN_PASSWORD_FIELD를 찾을 수 없습니다. 수동으로 정의합니다.
2025-06-23 10:40:59,991 - root - INFO - unknown element - DOM 선택자로 텍스트 입력 성공: qnwkehlwk8*
2025-06-23 10:40:59,992 - root - INFO - smart_click으로 비밀번호 필드 입력 성공: dom_input
2025-06-23 10:40:59,992 - root - INFO - 시간 지연 1초 - 텍스트 입력 후
2025-06-23 10:41:00,993 - root - INFO - 시간 지연 완료 (1초) - 텍스트 입력 후
2025-06-23 10:41:00,993 - root - INFO - 아이디 저장 체크박스 주석 처리됨 - 건너뚼
2025-06-23 10:41:00,993 - root - INFO - 로그인 버튼 클릭 시도 (smart_click 사용)
2025-06-23 10:41:00,994 - root - WARNING - UI_ELEMENTS에서 LOGIN_BUTTON을 찾을 수 없습니다. 수동으로 정의합니다.
2025-06-23 10:41:01,069 - root - INFO - unknown element - DOM 선택자로 클릭 성공
2025-06-23 10:41:01,069 - root - INFO - smart_click으로 로그인 버튼 클릭 성공
2025-06-23 10:41:01,069 - root - INFO - 로그인 버튼 클릭 후 대기 - 웹 서버 응답 및 로그인 처리 기다리는 중
2025-06-23 10:41:01,069 - root - INFO - 시간 지연 2초 - 로그인 버튼 클릭 후 대기
2025-06-23 10:41:03,070 - root - INFO - 시간 지연 완료 (2초) - 로그인 버튼 클릭 후 대기
2025-06-23 10:41:03,111 - root - INFO - 로그인 완료! 현재 URL: https://www.percenty.co.kr/
2025-06-23 10:41:03,111 - root - INFO - 시간 지연 5초 - 로그인 후 페이지 로드 대기
2025-06-23 10:41:08,112 - root - INFO - 시간 지연 완료 (5초) - 로그인 후 페이지 로드 대기
2025-06-23 10:41:08,112 - root - INFO - 비밀번호 저장 모달창 닫기 시도
2025-06-23 10:41:08,113 - root - INFO - 비밀번호 저장 모달창은 이미 닫혔습니다. 중복 처리를 방지합니다.
2025-06-23 10:41:08,114 - root - INFO - 시간 지연 0.5초 - 비밀번호 저장 모달창 닫기 후
2025-06-23 10:41:08,615 - root - INFO - 시간 지연 완료 (0.5초) - 비밀번호 저장 모달창 닫기 후
2025-06-23 10:41:08,616 - root - INFO - 다시 보지 않기 모달창 처리 시도
2025-06-23 10:41:08,616 - root - INFO - '다시 보지 않기' 버튼 클릭 시도
2025-06-23 10:41:08,708 - root - INFO - '다시 보지 않기' 버튼 DOM 클릭 성공
2025-06-23 10:41:08,708 - root - INFO - '다시 보지 않기' 버튼 클릭 성공: {'success': True, 'method': 'dom_click'}
2025-06-23 10:41:09,209 - root - INFO - 모달창 처리 완료 - 홈 버튼 클릭 준비 중
2025-06-23 10:41:09,210 - root - INFO - 시간 지연 0.5초 - 모달창 닫기 후
2025-06-23 10:41:09,710 - root - INFO - 시간 지연 완료 (0.5초) - 모달창 닫기 후
2025-06-23 10:41:09,711 - root - INFO - 홈 버튼 클릭 스킵 - 신규상품등록 메뉴 클릭 이슈 해결를 위해 비활성화
2025-06-23 10:41:09,711 - root - INFO - 시간 지연 5초 - 로그인 후 페이지 로딩
2025-06-23 10:41:14,712 - root - INFO - 시간 지연 완료 (5초) - 로그인 후 페이지 로딩
✅ 로그인 성공!
7. AI 소싱 메뉴 클릭...
2025-06-23 10:41:14,713 - root - INFO - AI 소싱 메뉴 클릭 시도 (하이브리드 방식)
2025-06-23 10:41:14,888 - root - INFO - AI 소싱 메뉴 - DOM 선택자로 클릭 성공
2025-06-23 10:41:14,888 - root - INFO - AI 소싱 메뉴 클릭 성공 (방법: dom_click)
2025-06-23 10:41:14,888 - root - INFO - 메뉴 전환 후 페이지 로딩 대기 - 3초 대기
✅ AI 소싱 메뉴 클릭 성공!
8. 채널톡 및 로그인 모달창 숨기기...
2025-06-23 10:41:17,889 - percenty_utils - INFO - 동적 업로드 테스트 채널톡 숨기기 적용 시작
2025-06-23 10:41:17,889 - root - INFO - 채널톡 숨기기 적용 - 확인 과정 건너뛐
2025-06-23 10:41:17,898 - root - INFO - 채널톡 강제 숨김 결과: {"method": "강제 숨김 적용 (확인 건너뛐)", "success": true}
2025-06-23 10:41:17,898 - root - INFO - 채널톡 닫기 성공! 이후 닫기 시도는 무시됩니다.
2025-06-23 10:41:17,898 - percenty_utils - INFO - 동적 업로드 테스트 채널톡 숨기기 결과: True
2025-06-23 10:41:17,899 - percenty_utils - INFO - 동적 업로드 테스트 로그인 모달창 숨기기 적용 시작
2025-06-23 10:41:17,899 - root - INFO - 로그인 모달창 숨기기 적용 시작
2025-06-23 10:41:17,899 - root - INFO - '다시 보지 않기' 버튼 찾기 시도: //span[contains(text(), '다시 보지 않기')]/parent::button
2025-06-23 10:41:17,903 - root - INFO - '다시 보지 않기' 버튼을 찾지 못했습니다: {'found': False}
2025-06-23 10:41:17,903 - root - INFO - 로그인 모달창 강제 숨기기 적용
2025-06-23 10:41:17,909 - root - INFO - 로그인 모달창 강제 숨김 결과: {"method": "로그인 모달창 강제 숨김 적용", "success": true}
2025-06-23 10:41:17,909 - root - INFO - 로그인 모달창 숨기기 성공! 이후 시도는 무시됩니다.
2025-06-23 10:41:17,909 - percenty_utils - INFO - 동적 업로드 테스트 로그인 모달창 숨기기 결과: True
✅ 채널톡 및 로그인 모달창 숨기기 결과: True

9. 동적 업로드 코어 초기화...
   계정 ID: onepick2019@gmail.com
2025-06-23 10:41:17,909 - dropdown_utils4 - INFO - DropdownUtils4 초기화 완료
2025-06-23 10:41:17,909 - product_editor_core6_1_dynamic - INFO - ProductEditorCore6_1Dynamic 초기화 완료 - 계정: onepick2019@gmail.com

10. 신규상품등록 화면으로 전환...
2025-06-23 10:41:17,909 - root - INFO - DOM 요소 강조 표시: xpath=//span[@class='ant-menu-title-content' and text()='신규 상품 등록']
2025-06-23 10:41:19,251 - root - INFO - 신규상품등록 메뉴 DOM 기반 클릭 시도
2025-06-23 10:41:19,251 - root - ERROR - 신규상품등록 메뉴 - 모든 방법이 실패했습니다 (fallback_order: [])
2025-06-23 10:41:19,251 - root - INFO - 시간 지연 3초 - 신규상품등록 메뉴 클릭 후 대기
2025-06-23 10:41:22,252 - root - INFO - 시간 지연 완료 (3초) - 신규상품등록 메뉴 클릭 후 대기
2025-06-23 10:41:22,258 - root - INFO - 스크롤 위치를 최상단으로 초기화했습니다
✅ 신규상품등록 화면 전환 성공!

11. 동적 업로드 워크플로우 실행...
    percenty_id.xlsx의 market_id 시트를 기반으로 12번 순환 업로드를 진행합니다.
    각 설정별로 마켓 설정 → 그룹 선택 → 상품 업로드 과정을 반복합니다.
2025-06-23 10:41:22,259 - product_editor_core6_1_dynamic - INFO - 6-1단계 동적 업로드 워크플로우 시작
2025-06-23 10:41:22,259 - product_editor_core6_1_dynamic - INFO - 계정 onepick2019@gmail.com의 마켓 설정 정보를 로드합니다.
2025-06-23 10:41:22,298 - product_editor_core6_1_dynamic - INFO - 계정 onepick2019@gmail.com에 대한 마켓 설정 12개 로드 완료
2025-06-23 10:41:22,299 - product_editor_core6_1_dynamic - INFO - 마켓 설정 1: 그룹명=쇼핑몰A1, API키=2a59718824...
2025-06-23 10:41:22,299 - product_editor_core6_1_dynamic - INFO - 마켓 설정 2: 그룹명=쇼핑몰A2, API키=c05ae0a14f...
2025-06-23 10:41:22,299 - product_editor_core6_1_dynamic - INFO - 마켓 설정 3: 그룹명=쇼핑몰A3, API키=4ba61316a9...
2025-06-23 10:41:22,299 - product_editor_core6_1_dynamic - INFO - 마켓 설정 4: 그룹명=쇼핑몰B1, API키=988957da32...
2025-06-23 10:41:22,300 - product_editor_core6_1_dynamic - INFO - 마켓 설정 5: 그룹명=쇼핑몰B2, API키=1cb239c934...
2025-06-23 10:41:22,300 - product_editor_core6_1_dynamic - INFO - 마켓 설정 6: 그룹명=쇼핑몰B3, API키=09e86ca976...
2025-06-23 10:41:22,300 - product_editor_core6_1_dynamic - INFO - 마켓 설정 7: 그룹명=쇼핑몰C1, API키=bd2e25601b...
2025-06-23 10:41:22,301 - product_editor_core6_1_dynamic - INFO - 마켓 설정 8: 그룹명=쇼핑몰C2, API키=43c2ffacf8...
2025-06-23 10:41:22,301 - product_editor_core6_1_dynamic - INFO - 마켓 설정 9: 그룹명=쇼핑몰C3, API키=400f09ed23...
2025-06-23 10:41:22,301 - product_editor_core6_1_dynamic - INFO - 마켓 설정 10: 그룹명=쇼핑몰D1, API키=4b0c943510...
2025-06-23 10:41:22,301 - product_editor_core6_1_dynamic - INFO - 마켓 설정 11: 그룹명=쇼핑몰D2, API키=1b929aebe3...
2025-06-23 10:41:22,302 - product_editor_core6_1_dynamic - INFO - 마켓 설정 12: 그룹명=쇼핑몰D3, API키=d497952156...
2025-06-23 10:41:22,302 - product_editor_core6_1_dynamic - INFO - === 마켓 설정 1/12 처리 시작 ===
2025-06-23 10:41:22,302 - product_editor_core6_1_dynamic - INFO - 그룹명: 쇼핑몰A1, API키: 2a59718824...
2025-06-23 10:41:22,302 - product_editor_core6_1_dynamic - INFO - 마켓 설정 화면 정보 처리 시작 - 그룹: 쇼핑몰A1
2025-06-23 10:41:22,302 - product_editor_core6_1_dynamic - INFO - 마켓설정 메뉴 클릭 시도
2025-06-23 10:41:22,464 - product_editor_core6_1_dynamic - INFO - 마켓설정 화면 열기 완료
2025-06-23 10:41:25,469 - product_editor_core6_1_dynamic - INFO - 스크롤 위치를 최상단으로 초기화
2025-06-23 10:41:25,469 - product_editor_core6_1_dynamic - INFO - smartstore API 연결 끊기 시도
2025-06-23 10:41:25,469 - product_editor_core6_1_dynamic - INFO - smartstore API 연결 끊기 시도
2025-06-23 10:41:26,066 - product_editor_core6_1_dynamic - INFO - ESC 키로 모달창 닫기 시도
2025-06-23 10:41:26,146 - product_editor_core6_1_dynamic - INFO - 스마트스토어 탭 클릭 완료
2025-06-23 10:41:29,203 - product_editor_core6_1_dynamic - INFO - 스마트스토어 패널 로드 완료
2025-06-23 10:41:29,212 - product_editor_core6_1_dynamic - INFO - API 연결 끊기 버튼 찾기 시도 1/3
2025-06-23 10:41:29,286 - product_editor_core6_1_dynamic - INFO - API 연결 끊기 버튼 클릭 완료
2025-06-23 10:41:31,334 - product_editor_core6_1_dynamic - INFO - API 연결 끊기 모달창 확인
2025-06-23 10:41:31,362 - product_editor_core6_1_dynamic - INFO - 에러 알림: API 연결 끊기 시 해당 마켓의 API 연동이 제거됩니다.
2025-06-23 10:41:31,362 - product_editor_core6_1_dynamic - INFO - 경고 알림: API 연결을 끊어도 기존에 업로드된 상품에 영향이 가지 않습니다.
연결 끊기 후 다른 API를 연동하면 연동된 마켓에 상품이 업로드됩니다.
2025-06-23 10:41:31,362 - product_editor_core6_1_dynamic - INFO - 모달창 확인 버튼 찾기 시도 1/3
2025-06-23 10:41:31,417 - product_editor_core6_1_dynamic - INFO - API 연결 끊기 모달창 확인 버튼 클릭 완료
2025-06-23 10:41:32,418 - product_editor_core6_1_dynamic - INFO - 모달창이 완전히 사라질 때까지 대기 중...
2025-06-23 10:41:33,438 - product_editor_core6_1_dynamic - INFO - 모달창이 완전히 사라짐
2025-06-23 10:41:33,439 - product_editor_core6_1_dynamic - INFO - smartstore API 연결 끊기 성공
2025-06-23 10:41:34,440 - product_editor_core6_1_dynamic - INFO - coupang API 연결 끊기 시도
2025-06-23 10:41:34,440 - product_editor_core6_1_dynamic - INFO - coupang API 연결 끊기 시도
2025-06-23 10:41:34,458 - product_editor_core6_1_dynamic - INFO - DOM에 1개의 모달창 래퍼가 남아있음, 제거 시도
2025-06-23 10:41:34,965 - product_editor_core6_1_dynamic - INFO - 모달창 DOM 요소 강제 제거 완료
2025-06-23 10:41:35,519 - product_editor_core6_1_dynamic - INFO - ESC 키로 모달창 닫기 시도
2025-06-23 10:41:35,583 - product_editor_core6_1_dynamic - INFO - 쿠팡 탭 클릭 완료
2025-06-23 10:41:38,642 - product_editor_core6_1_dynamic - INFO - 쿠팡 패널 로드 완료
2025-06-23 10:41:38,653 - product_editor_core6_1_dynamic - INFO - API 연결 끊기 버튼 찾기 시도 1/3
2025-06-23 10:41:38,743 - product_editor_core6_1_dynamic - INFO - API 연결 끊기 버튼 클릭 완료
2025-06-23 10:41:40,779 - product_editor_core6_1_dynamic - INFO - API 연결 끊기 모달창 확인
2025-06-23 10:41:40,799 - product_editor_core6_1_dynamic - INFO - 에러 알림: API 연결 끊기 시 해당 마켓의 API 연동이 제거됩니다.
2025-06-23 10:41:40,799 - product_editor_core6_1_dynamic - INFO - 경고 알림: API 연결을 끊어도 기존에 업로드된 상품에 영향이 가지 않습니다.
연결 끊기 후 다른 API를 연동하면 연동된 마켓에 상품이 업로드됩니다.
2025-06-23 10:41:40,799 - product_editor_core6_1_dynamic - INFO - 모달창 확인 버튼 찾기 시도 1/3
2025-06-23 10:41:40,852 - product_editor_core6_1_dynamic - INFO - API 연결 끊기 모달창 확인 버튼 클릭 완료
2025-06-23 10:41:41,852 - product_editor_core6_1_dynamic - INFO - 모달창이 완전히 사라질 때까지 대기 중...
2025-06-23 10:41:42,865 - product_editor_core6_1_dynamic - INFO - 모달창이 완전히 사라짐
2025-06-23 10:41:42,866 - product_editor_core6_1_dynamic - INFO - coupang API 연결 끊기 성공
2025-06-23 10:41:43,866 - product_editor_core6_1_dynamic - INFO - auction_gmarket API 연결 끊기 시도
2025-06-23 10:41:43,866 - product_editor_core6_1_dynamic - INFO - auction_gmarket API 연결 끊기 시도
2025-06-23 10:41:43,884 - product_editor_core6_1_dynamic - INFO - DOM에 1개의 모달창 래퍼가 남아있음, 제거 시도
2025-06-23 10:41:44,390 - product_editor_core6_1_dynamic - INFO - 모달창 DOM 요소 강제 제거 완료
2025-06-23 10:41:44,981 - product_editor_core6_1_dynamic - INFO - ESC 키로 모달창 닫기 시도
2025-06-23 10:41:45,065 - product_editor_core6_1_dynamic - INFO - 옥션/G마켓 (ESM 2.0) 탭 클릭 완료
2025-06-23 10:41:48,164 - product_editor_core6_1_dynamic - INFO - 옥션/G마켓 (ESM 2.0) 패널 로드 완료
2025-06-23 10:41:48,227 - product_editor_core6_1_dynamic - INFO - API 연결 끊기 버튼 찾기 시도 1/3
2025-06-23 10:41:48,300 - product_editor_core6_1_dynamic - INFO - API 연결 끊기 버튼 클릭 완료
2025-06-23 10:41:50,376 - product_editor_core6_1_dynamic - INFO - API 연결 끊기 모달창 확인
2025-06-23 10:41:50,396 - product_editor_core6_1_dynamic - INFO - 에러 알림: API 연결 끊기 시 해당 마켓의 API 연동이 제거됩니다.
2025-06-23 10:41:50,396 - product_editor_core6_1_dynamic - INFO - 경고 알림: API 연결을 끊어도 기존에 업로드된 상품에 영향이 가지 않습니다.
연결 끊기 후 다른 API를 연동하면 연동된 마켓에 상품이 업로드됩니다.
2025-06-23 10:41:50,396 - product_editor_core6_1_dynamic - INFO - 모달창 확인 버튼 찾기 시도 1/3
2025-06-23 10:41:50,443 - product_editor_core6_1_dynamic - INFO - API 연결 끊기 모달창 확인 버튼 클릭 완료
2025-06-23 10:41:51,444 - product_editor_core6_1_dynamic - INFO - 모달창이 완전히 사라질 때까지 대기 중...
2025-06-23 10:41:52,472 - product_editor_core6_1_dynamic - INFO - 모달창이 완전히 사라짐
2025-06-23 10:41:52,473 - product_editor_core6_1_dynamic - INFO - auction_gmarket API 연결 끊기 성공
2025-06-23 10:41:53,473 - product_editor_core6_1_dynamic - INFO - 11st_general API 연결 끊기 시도
2025-06-23 10:41:53,473 - product_editor_core6_1_dynamic - INFO - 11st_general API 연결 끊기 시도
2025-06-23 10:41:53,490 - product_editor_core6_1_dynamic - INFO - DOM에 1개의 모달창 래퍼가 남아있음, 제거 시도
2025-06-23 10:41:53,995 - product_editor_core6_1_dynamic - INFO - 모달창 DOM 요소 강제 제거 완료
2025-06-23 10:41:54,598 - product_editor_core6_1_dynamic - INFO - ESC 키로 모달창 닫기 시도
2025-06-23 10:41:54,687 - product_editor_core6_1_dynamic - INFO - 11번가-일반 탭 클릭 완료
2025-06-23 10:41:57,722 - product_editor_core6_1_dynamic - INFO - 11번가-일반 패널 로드 완료
2025-06-23 10:41:57,732 - product_editor_core6_1_dynamic - INFO - API 연결 끊기 버튼 찾기 시도 1/3
2025-06-23 10:41:57,795 - product_editor_core6_1_dynamic - INFO - API 연결 끊기 버튼 클릭 완료
2025-06-23 10:41:59,830 - product_editor_core6_1_dynamic - INFO - API 연결 끊기 모달창 확인
2025-06-23 10:41:59,848 - product_editor_core6_1_dynamic - INFO - 에러 알림: API 연결 끊기 시 해당 마켓의 API 연동이 제거됩니다.
2025-06-23 10:41:59,848 - product_editor_core6_1_dynamic - INFO - 경고 알림: API 연결을 끊어도 기존에 업로드된 상품에 영향이 가지 않습니다.
연결 끊기 후 다른 API를 연동하면 연동된 마켓에 상품이 업로드됩니다.
2025-06-23 10:41:59,849 - product_editor_core6_1_dynamic - INFO - 모달창 확인 버튼 찾기 시도 1/3
2025-06-23 10:41:59,894 - product_editor_core6_1_dynamic - INFO - API 연결 끊기 모달창 확인 버튼 클릭 완료
2025-06-23 10:42:00,894 - product_editor_core6_1_dynamic - INFO - 모달창이 완전히 사라질 때까지 대기 중...
2025-06-23 10:42:01,908 - product_editor_core6_1_dynamic - INFO - 모달창이 완전히 사라짐
2025-06-23 10:42:01,908 - product_editor_core6_1_dynamic - INFO - 11st_general API 연결 끊기 성공
2025-06-23 10:42:02,908 - product_editor_core6_1_dynamic - INFO - 11st_global API 연결 끊기 시도
2025-06-23 10:42:02,909 - product_editor_core6_1_dynamic - INFO - 11st_global API 연결 끊기 시도
2025-06-23 10:42:02,927 - product_editor_core6_1_dynamic - INFO - DOM에 1개의 모달창 래퍼가 남아있음, 제거 시도
2025-06-23 10:42:03,431 - product_editor_core6_1_dynamic - INFO - 모달창 DOM 요소 강제 제거 완료
2025-06-23 10:42:03,996 - product_editor_core6_1_dynamic - INFO - ESC 키로 모달창 닫기 시도
2025-06-23 10:42:04,096 - product_editor_core6_1_dynamic - INFO - 11번가-글로벌 탭 클릭 완료
2025-06-23 10:42:07,163 - product_editor_core6_1_dynamic - INFO - 11번가-글로벌 패널 로드 완료
2025-06-23 10:42:07,236 - product_editor_core6_1_dynamic - INFO - API 연결 끊기 버튼 찾기 시도 1/3
2025-06-23 10:42:07,308 - product_editor_core6_1_dynamic - INFO - API 연결 끊기 버튼 클릭 완료
2025-06-23 10:42:09,345 - product_editor_core6_1_dynamic - INFO - API 연결 끊기 모달창 확인
2025-06-23 10:42:09,362 - product_editor_core6_1_dynamic - INFO - 에러 알림: API 연결 끊기 시 해당 마켓의 API 연동이 제거됩니다.
2025-06-23 10:42:09,363 - product_editor_core6_1_dynamic - INFO - 경고 알림: API 연결을 끊어도 기존에 업로드된 상품에 영향이 가지 않습니다.
연결 끊기 후 다른 API를 연동하면 연동된 마켓에 상품이 업로드됩니다.
2025-06-23 10:42:09,363 - product_editor_core6_1_dynamic - INFO - 모달창 확인 버튼 찾기 시도 1/3
2025-06-23 10:42:09,411 - product_editor_core6_1_dynamic - INFO - API 연결 끊기 모달창 확인 버튼 클릭 완료
2025-06-23 10:42:10,412 - product_editor_core6_1_dynamic - INFO - 모달창이 완전히 사라질 때까지 대기 중...
2025-06-23 10:42:11,437 - product_editor_core6_1_dynamic - INFO - 모달창이 완전히 사라짐
2025-06-23 10:42:11,438 - product_editor_core6_1_dynamic - INFO - 11st_global API 연결 끊기 성공
2025-06-23 10:42:12,438 - product_editor_core6_1_dynamic - INFO - lotteon API 연결 끊기 시도
2025-06-23 10:42:12,439 - product_editor_core6_1_dynamic - INFO - lotteon API 연결 끊기 시도
2025-06-23 10:42:12,482 - product_editor_core6_1_dynamic - INFO - DOM에 1개의 모달창 래퍼가 남아있음, 제거 시도
2025-06-23 10:42:12,989 - product_editor_core6_1_dynamic - INFO - 모달창 DOM 요소 강제 제거 완료
2025-06-23 10:42:13,562 - product_editor_core6_1_dynamic - INFO - ESC 키로 모달창 닫기 시도
2025-06-23 10:42:13,649 - product_editor_core6_1_dynamic - INFO - 롯데온 탭 클릭 완료
2025-06-23 10:42:16,714 - product_editor_core6_1_dynamic - INFO - 롯데온 패널 로드 완료
2025-06-23 10:42:16,725 - product_editor_core6_1_dynamic - INFO - API 연결 끊기 버튼 찾기 시도 1/3
2025-06-23 10:42:16,792 - product_editor_core6_1_dynamic - INFO - API 연결 끊기 버튼 클릭 완료
2025-06-23 10:42:18,835 - product_editor_core6_1_dynamic - INFO - API 연결 끊기 모달창 확인
2025-06-23 10:42:18,852 - product_editor_core6_1_dynamic - INFO - 에러 알림: API 연결 끊기 시 해당 마켓의 API 연동이 제거됩니다.
2025-06-23 10:42:18,853 - product_editor_core6_1_dynamic - INFO - 경고 알림: API 연결을 끊어도 기존에 업로드된 상품에 영향이 가지 않습니다.
연결 끊기 후 다른 API를 연동하면 연동된 마켓에 상품이 업로드됩니다.
2025-06-23 10:42:18,853 - product_editor_core6_1_dynamic - INFO - 모달창 확인 버튼 찾기 시도 1/3
2025-06-23 10:42:18,898 - product_editor_core6_1_dynamic - INFO - API 연결 끊기 모달창 확인 버튼 클릭 완료
2025-06-23 10:42:19,899 - product_editor_core6_1_dynamic - INFO - 모달창이 완전히 사라질 때까지 대기 중...
2025-06-23 10:42:20,911 - product_editor_core6_1_dynamic - INFO - 모달창이 완전히 사라짐
2025-06-23 10:42:20,912 - product_editor_core6_1_dynamic - INFO - lotteon API 연결 끊기 성공
2025-06-23 10:42:21,912 - product_editor_core6_1_dynamic - INFO - kakao API 연결 끊기 시도
2025-06-23 10:42:21,913 - product_editor_core6_1_dynamic - INFO - kakao API 연결 끊기 시도
2025-06-23 10:42:21,976 - product_editor_core6_1_dynamic - INFO - DOM에 1개의 모달창 래퍼가 남아있음, 제거 시도
2025-06-23 10:42:22,484 - product_editor_core6_1_dynamic - INFO - 모달창 DOM 요소 강제 제거 완료
2025-06-23 10:42:23,060 - product_editor_core6_1_dynamic - INFO - ESC 키로 모달창 닫기 시도
2025-06-23 10:42:23,139 - product_editor_core6_1_dynamic - INFO - 톡스토어 탭 클릭 완료
2025-06-23 10:42:26,187 - product_editor_core6_1_dynamic - INFO - 톡스토어 패널 로드 완료
2025-06-23 10:42:26,196 - product_editor_core6_1_dynamic - INFO - API 연결 끊기 버튼 찾기 시도 1/3
2025-06-23 10:42:26,260 - product_editor_core6_1_dynamic - INFO - API 연결 끊기 버튼 클릭 완료
2025-06-23 10:42:28,341 - product_editor_core6_1_dynamic - INFO - API 연결 끊기 모달창 확인
2025-06-23 10:42:28,375 - product_editor_core6_1_dynamic - INFO - 에러 알림: API 연결 끊기 시 해당 마켓의 API 연동이 제거됩니다.
2025-06-23 10:42:28,375 - product_editor_core6_1_dynamic - INFO - 경고 알림: API 연결을 끊어도 기존에 업로드된 상품에 영향이 가지 않습니다.
연결 끊기 후 다른 API를 연동하면 연동된 마켓에 상품이 업로드됩니다.
2025-06-23 10:42:28,375 - product_editor_core6_1_dynamic - INFO - 모달창 확인 버튼 찾기 시도 1/3
2025-06-23 10:42:28,422 - product_editor_core6_1_dynamic - INFO - API 연결 끊기 모달창 확인 버튼 클릭 완료
2025-06-23 10:42:29,422 - product_editor_core6_1_dynamic - INFO - 모달창이 완전히 사라질 때까지 대기 중...
2025-06-23 10:42:30,435 - product_editor_core6_1_dynamic - INFO - 모달창이 완전히 사라짐
2025-06-23 10:42:30,435 - product_editor_core6_1_dynamic - INFO - kakao API 연결 끊기 성공
2025-06-23 10:42:31,436 - product_editor_core6_1_dynamic - INFO - 모든 마켓 API 연결 끊기 완료
2025-06-23 10:42:31,458 - product_editor_core6_1_dynamic - INFO - DOM에 1개의 모달창 래퍼가 남아있음, 제거 시도
2025-06-23 10:42:31,967 - product_editor_core6_1_dynamic - INFO - 모달창 DOM 요소 강제 제거 완료
2025-06-23 10:42:32,546 - product_editor_core6_1_dynamic - INFO - ESC 키로 모달창 닫기 시도
2025-06-23 10:42:32,608 - product_editor_core6_1_dynamic - INFO - 11번가-일반 탭 클릭 완료
2025-06-23 10:42:33,608 - product_editor_core6_1_dynamic - INFO - 11번가 API KEY 입력 시작
2025-06-23 10:42:33,608 - product_editor_core6_1_dynamic - INFO - 11번가-일반 API KEY 입력 시작
2025-06-23 10:42:33,768 - product_editor_core6_1_dynamic - INFO - 11번가-일반 API KEY 입력 완료: 2a59718824...
2025-06-23 10:42:33,782 - product_editor_core6_1_dynamic - INFO - 11번가-일반 API KEY 입력 후 포커스 이동 (TAB 키 전송)
2025-06-23 10:42:35,284 - product_editor_core6_1_dynamic - INFO - 11번가 API KEY 입력 완료: 2a59718824...
2025-06-23 10:42:35,284 - product_editor_core6_1_dynamic - INFO - API 검증 버튼 찾기 시도 - XPath: //div[contains(@class, "ant-tabs-tabpane-active")]//div[contains(@class, "ant-row")]//button[contains(@class, "ant-btn-primary") and .//span[text()="API 검증"]]
2025-06-23 10:42:36,376 - product_editor_core6_1_dynamic - INFO - API 검증 버튼 클릭 완료
2025-06-23 10:42:38,386 - product_editor_core6_1_dynamic - INFO - 11번가 API 검증 모달창 확인
2025-06-23 10:42:38,403 - product_editor_core6_1_dynamic - INFO - 출고 택배사 드롭다운을 라벨 기준으로 찾음
2025-06-23 10:42:38,458 - product_editor_core6_1_dynamic - INFO - 출고 택배사 드롭다운 클릭
2025-06-23 10:42:40,541 - product_editor_core6_1_dynamic - INFO - 롯데택배 선택 완료
2025-06-23 10:42:41,598 - product_editor_core6_1_dynamic - INFO - 11번가 배송프로필 만들기 버튼 클릭 완료
2025-06-23 10:42:43,599 - product_editor_core6_1_dynamic - INFO - 11번가 API 검증 모달창 처리 완료
2025-06-23 10:42:43,600 - product_editor_core6_1_dynamic - INFO - 마켓 설정 화면 정보 처리 완료
2025-06-23 10:42:43,600 - product_editor_core6_1_dynamic - INFO - 신규상품등록 화면으로 전환 시작
2025-06-23 10:42:43,839 - product_editor_core6_1_dynamic - INFO - 신규상품등록 메뉴 클릭 완료
2025-06-23 10:42:48,844 - product_editor_core6_1_dynamic - INFO - 스크롤 위치를 최상단으로 초기화
2025-06-23 10:42:48,844 - product_editor_core6_1_dynamic - INFO - 신규상품등록 화면으로 전환 완료
2025-06-23 10:42:48,844 - product_editor_core6_1_dynamic - INFO - 동적 그룹 선택 시작: 쇼핑몰A1
2025-06-23 10:42:48,845 - dropdown_utils4 - INFO - 상품검색 드롭박스에서 '쇼핑몰A1' 그룹 선택 시작
2025-06-23 10:42:48,845 - dropdown_utils4 - INFO - 상품검색 드롭박스 열기 시도
2025-06-23 10:42:48,845 - dropdown_utils4 - INFO - 선택자 1 시도: (//div[contains(@class, 'ant-select-single')])[1]
2025-06-23 10:42:50,436 - dropdown_utils4 - INFO - 상품검색 드롭박스 열기 성공 (선택자 1)
2025-06-23 10:42:50,436 - dropdown_utils4 - INFO - 그룹 '쇼핑몰A1' 선택 시도
2025-06-23 10:42:50,452 - dropdown_utils4 - INFO - 전체 상품 수 텍스트 발견: '총 29,506개 상품'
2025-06-23 10:42:50,452 - dropdown_utils4 - INFO - 전체 상품 수 확인 성공: 29506개
2025-06-23 10:42:50,452 - dropdown_utils4 - INFO - 그룹 선택 전 전체 상품 수: 29506개
2025-06-23 10:42:50,463 - dropdown_utils4 - INFO - 현재 화면에 40개의 옵션 발견
2025-06-23 10:42:50,469 - dropdown_utils4 - INFO - 옵션 1: ''
2025-06-23 10:42:50,475 - dropdown_utils4 - INFO - 옵션 2: ''
2025-06-23 10:42:50,479 - dropdown_utils4 - INFO - 옵션 3: ''
2025-06-23 10:42:50,484 - dropdown_utils4 - INFO - 옵션 4: ''
2025-06-23 10:42:50,489 - dropdown_utils4 - INFO - 옵션 5: ''
2025-06-23 10:42:50,494 - dropdown_utils4 - INFO - 옵션 6: ''
2025-06-23 10:42:50,499 - dropdown_utils4 - INFO - 옵션 7: ''
2025-06-23 10:42:50,503 - dropdown_utils4 - INFO - 옵션 8: ''
2025-06-23 10:42:50,509 - dropdown_utils4 - INFO - 옵션 9: ''
2025-06-23 10:42:50,513 - dropdown_utils4 - INFO - 옵션 10: ''
2025-06-23 10:42:50,518 - dropdown_utils4 - INFO - 옵션 11: ''
2025-06-23 10:42:50,523 - dropdown_utils4 - INFO - 옵션 12: ''
2025-06-23 10:42:50,528 - dropdown_utils4 - INFO - 옵션 13: ''
2025-06-23 10:42:50,532 - dropdown_utils4 - INFO - 옵션 14: ''
2025-06-23 10:42:50,537 - dropdown_utils4 - INFO - 옵션 15: ''
2025-06-23 10:42:50,542 - dropdown_utils4 - INFO - 옵션 16: ''
2025-06-23 10:42:50,549 - dropdown_utils4 - INFO - 옵션 17: ''
2025-06-23 10:42:50,561 - dropdown_utils4 - INFO - 옵션 18: ''
2025-06-23 10:42:50,568 - dropdown_utils4 - INFO - 옵션 19: ''
2025-06-23 10:42:50,585 - dropdown_utils4 - INFO - 옵션 20: ''
2025-06-23 10:42:50,592 - dropdown_utils4 - INFO - 옵션 21: '전체'
2025-06-23 10:42:50,597 - dropdown_utils4 - INFO - 옵션 22: '전체'
2025-06-23 10:42:50,602 - dropdown_utils4 - INFO - 옵션 23: '그룹 없음'
2025-06-23 10:42:50,607 - dropdown_utils4 - INFO - 옵션 24: '그룹 없음'
2025-06-23 10:42:50,612 - dropdown_utils4 - INFO - 옵션 25: '신규수집'
2025-06-23 10:42:50,616 - dropdown_utils4 - INFO - 옵션 26: '신규수집'
2025-06-23 10:42:50,621 - dropdown_utils4 - INFO - 옵션 27: '번역대기'
2025-06-23 10:42:50,626 - dropdown_utils4 - INFO - 옵션 28: '번역대기'
2025-06-23 10:42:50,631 - dropdown_utils4 - INFO - 옵션 29: '등록실행'
2025-06-23 10:42:50,636 - dropdown_utils4 - INFO - 옵션 30: '등록실행'
2025-06-23 10:42:50,641 - dropdown_utils4 - INFO - 옵션 31: '등록A'
2025-06-23 10:42:50,645 - dropdown_utils4 - INFO - 옵션 32: '등록A'
2025-06-23 10:42:50,650 - dropdown_utils4 - INFO - 옵션 33: '등록B'
2025-06-23 10:42:50,656 - dropdown_utils4 - INFO - 옵션 34: '등록B'
2025-06-23 10:42:50,661 - dropdown_utils4 - INFO - 옵션 35: '등록C'
2025-06-23 10:42:50,666 - dropdown_utils4 - INFO - 옵션 36: '등록C'
2025-06-23 10:42:50,671 - dropdown_utils4 - INFO - 옵션 37: ''
2025-06-23 10:42:50,676 - dropdown_utils4 - INFO - 옵션 38: ''
2025-06-23 10:42:50,681 - dropdown_utils4 - INFO - 옵션 39: ''
2025-06-23 10:42:50,686 - dropdown_utils4 - INFO - 옵션 40: ''
2025-06-23 10:42:50,686 - dropdown_utils4 - INFO - '쇼핑몰A1' 그룹이 현재 화면에 없어 스크롤 검색 시작
2025-06-23 10:42:50,686 - dropdown_utils4 - INFO - 드롭다운 내에서 '쇼핑몰A1' 그룹 스크롤 검색 (최대 30회)
2025-06-23 10:42:50,694 - dropdown_utils4 - INFO - 드롭다운 컨테이너 발견: //div[contains(@class, 'rc-virtual-list-holder')]
2025-06-23 10:42:50,694 - dropdown_utils4 - INFO - 스크롤 1/30
2025-06-23 10:42:50,700 - dropdown_utils4 - INFO - 현재 화면에 40개의 옵션 발견
2025-06-23 10:42:50,705 - dropdown_utils4 - INFO - 옵션 1: ''
2025-06-23 10:42:50,710 - dropdown_utils4 - INFO - 옵션 2: ''
2025-06-23 10:42:50,715 - dropdown_utils4 - INFO - 옵션 3: ''
2025-06-23 10:42:50,719 - dropdown_utils4 - INFO - 옵션 4: ''
2025-06-23 10:42:50,725 - dropdown_utils4 - INFO - 옵션 5: ''
2025-06-23 10:42:50,729 - dropdown_utils4 - INFO - 옵션 6: ''
2025-06-23 10:42:50,733 - dropdown_utils4 - INFO - 옵션 7: ''
2025-06-23 10:42:50,738 - dropdown_utils4 - INFO - 옵션 8: ''
2025-06-23 10:42:50,743 - dropdown_utils4 - INFO - 옵션 9: ''
2025-06-23 10:42:50,748 - dropdown_utils4 - INFO - 옵션 10: ''
2025-06-23 10:42:50,752 - dropdown_utils4 - INFO - 옵션 11: ''
2025-06-23 10:42:50,757 - dropdown_utils4 - INFO - 옵션 12: ''
2025-06-23 10:42:50,762 - dropdown_utils4 - INFO - 옵션 13: ''
2025-06-23 10:42:50,766 - dropdown_utils4 - INFO - 옵션 14: ''
2025-06-23 10:42:50,771 - dropdown_utils4 - INFO - 옵션 15: ''
2025-06-23 10:42:50,776 - dropdown_utils4 - INFO - 옵션 16: ''
2025-06-23 10:42:50,780 - dropdown_utils4 - INFO - 옵션 17: ''
2025-06-23 10:42:50,785 - dropdown_utils4 - INFO - 옵션 18: ''
2025-06-23 10:42:50,790 - dropdown_utils4 - INFO - 옵션 19: ''
2025-06-23 10:42:50,795 - dropdown_utils4 - INFO - 옵션 20: ''
2025-06-23 10:42:50,800 - dropdown_utils4 - INFO - 옵션 21: '전체'
2025-06-23 10:42:50,805 - dropdown_utils4 - INFO - 옵션 22: '전체'
2025-06-23 10:42:50,810 - dropdown_utils4 - INFO - 옵션 23: '그룹 없음'
2025-06-23 10:42:50,815 - dropdown_utils4 - INFO - 옵션 24: '그룹 없음'
2025-06-23 10:42:50,821 - dropdown_utils4 - INFO - 옵션 25: '신규수집'
2025-06-23 10:42:50,826 - dropdown_utils4 - INFO - 옵션 26: '신규수집'
2025-06-23 10:42:50,831 - dropdown_utils4 - INFO - 옵션 27: '번역대기'
2025-06-23 10:42:50,836 - dropdown_utils4 - INFO - 옵션 28: '번역대기'
2025-06-23 10:42:50,841 - dropdown_utils4 - INFO - 옵션 29: '등록실행'
2025-06-23 10:42:50,846 - dropdown_utils4 - INFO - 옵션 30: '등록실행'
2025-06-23 10:42:50,851 - dropdown_utils4 - INFO - 옵션 31: '등록A'
2025-06-23 10:42:50,857 - dropdown_utils4 - INFO - 옵션 32: '등록A'
2025-06-23 10:42:50,862 - dropdown_utils4 - INFO - 옵션 33: '등록B'
2025-06-23 10:42:50,867 - dropdown_utils4 - INFO - 옵션 34: '등록B'
2025-06-23 10:42:50,872 - dropdown_utils4 - INFO - 옵션 35: '등록C'
2025-06-23 10:42:50,877 - dropdown_utils4 - INFO - 옵션 36: '등록C'
2025-06-23 10:42:50,882 - dropdown_utils4 - INFO - 옵션 37: ''
2025-06-23 10:42:50,887 - dropdown_utils4 - INFO - 옵션 38: ''
2025-06-23 10:42:50,892 - dropdown_utils4 - INFO - 옵션 39: ''
2025-06-23 10:42:50,897 - dropdown_utils4 - INFO - 옵션 40: ''
2025-06-23 10:42:51,207 - dropdown_utils4 - INFO - 스크롤 후 40개 옵션 확인
2025-06-23 10:42:51,207 - dropdown_utils4 - INFO - 스크롤 2/30
2025-06-23 10:42:51,213 - dropdown_utils4 - INFO - 현재 화면에 40개의 옵션 발견
2025-06-23 10:42:51,218 - dropdown_utils4 - INFO - 옵션 1: ''
2025-06-23 10:42:51,223 - dropdown_utils4 - INFO - 옵션 2: ''
2025-06-23 10:42:51,228 - dropdown_utils4 - INFO - 옵션 3: ''
2025-06-23 10:42:51,232 - dropdown_utils4 - INFO - 옵션 4: ''
2025-06-23 10:42:51,236 - dropdown_utils4 - INFO - 옵션 5: ''
2025-06-23 10:42:51,241 - dropdown_utils4 - INFO - 옵션 6: ''
2025-06-23 10:42:51,245 - dropdown_utils4 - INFO - 옵션 7: ''
2025-06-23 10:42:51,249 - dropdown_utils4 - INFO - 옵션 8: ''
2025-06-23 10:42:51,254 - dropdown_utils4 - INFO - 옵션 9: ''
2025-06-23 10:42:51,258 - dropdown_utils4 - INFO - 옵션 10: ''
2025-06-23 10:42:51,263 - dropdown_utils4 - INFO - 옵션 11: ''
2025-06-23 10:42:51,267 - dropdown_utils4 - INFO - 옵션 12: ''
2025-06-23 10:42:51,271 - dropdown_utils4 - INFO - 옵션 13: ''
2025-06-23 10:42:51,276 - dropdown_utils4 - INFO - 옵션 14: ''
2025-06-23 10:42:51,280 - dropdown_utils4 - INFO - 옵션 15: ''
2025-06-23 10:42:51,284 - dropdown_utils4 - INFO - 옵션 16: ''
2025-06-23 10:42:51,288 - dropdown_utils4 - INFO - 옵션 17: ''
2025-06-23 10:42:51,293 - dropdown_utils4 - INFO - 옵션 18: ''
2025-06-23 10:42:51,297 - dropdown_utils4 - INFO - 옵션 19: ''
2025-06-23 10:42:51,301 - dropdown_utils4 - INFO - 옵션 20: ''
2025-06-23 10:42:51,306 - dropdown_utils4 - INFO - 옵션 21: '전체'
2025-06-23 10:42:51,310 - dropdown_utils4 - INFO - 옵션 22: '전체'
2025-06-23 10:42:51,315 - dropdown_utils4 - INFO - 옵션 23: '그룹 없음'
2025-06-23 10:42:51,319 - dropdown_utils4 - INFO - 옵션 24: '그룹 없음'
2025-06-23 10:42:51,324 - dropdown_utils4 - INFO - 옵션 25: '신규수집'
2025-06-23 10:42:51,329 - dropdown_utils4 - INFO - 옵션 26: '신규수집'
2025-06-23 10:42:51,333 - dropdown_utils4 - INFO - 옵션 27: '번역대기'
2025-06-23 10:42:51,338 - dropdown_utils4 - INFO - 옵션 28: '번역대기'
2025-06-23 10:42:51,343 - dropdown_utils4 - INFO - 옵션 29: '등록실행'
2025-06-23 10:42:51,347 - dropdown_utils4 - INFO - 옵션 30: '등록실행'
2025-06-23 10:42:51,352 - dropdown_utils4 - INFO - 옵션 31: '등록A'
2025-06-23 10:42:51,357 - dropdown_utils4 - INFO - 옵션 32: '등록A'
2025-06-23 10:42:51,362 - dropdown_utils4 - INFO - 옵션 33: '등록B'
2025-06-23 10:42:51,366 - dropdown_utils4 - INFO - 옵션 34: '등록B'
2025-06-23 10:42:51,371 - dropdown_utils4 - INFO - 옵션 35: '등록C'
2025-06-23 10:42:51,375 - dropdown_utils4 - INFO - 옵션 36: '등록C'
2025-06-23 10:42:51,380 - dropdown_utils4 - INFO - 옵션 37: ''
2025-06-23 10:42:51,384 - dropdown_utils4 - INFO - 옵션 38: ''
2025-06-23 10:42:51,389 - dropdown_utils4 - INFO - 옵션 39: ''
2025-06-23 10:42:51,393 - dropdown_utils4 - INFO - 옵션 40: ''
2025-06-23 10:42:51,706 - dropdown_utils4 - INFO - 스크롤 후 40개 옵션 확인
2025-06-23 10:42:51,706 - dropdown_utils4 - INFO - 스크롤 3/30
2025-06-23 10:42:51,713 - dropdown_utils4 - INFO - 현재 화면에 40개의 옵션 발견
2025-06-23 10:42:51,718 - dropdown_utils4 - INFO - 옵션 1: ''
2025-06-23 10:42:51,724 - dropdown_utils4 - INFO - 옵션 2: ''
2025-06-23 10:42:51,729 - dropdown_utils4 - INFO - 옵션 3: ''
2025-06-23 10:42:51,734 - dropdown_utils4 - INFO - 옵션 4: ''
2025-06-23 10:42:51,739 - dropdown_utils4 - INFO - 옵션 5: ''
2025-06-23 10:42:51,744 - dropdown_utils4 - INFO - 옵션 6: ''
2025-06-23 10:42:51,749 - dropdown_utils4 - INFO - 옵션 7: ''
2025-06-23 10:42:51,755 - dropdown_utils4 - INFO - 옵션 8: ''
2025-06-23 10:42:51,760 - dropdown_utils4 - INFO - 옵션 9: ''
2025-06-23 10:42:51,765 - dropdown_utils4 - INFO - 옵션 10: ''
2025-06-23 10:42:51,770 - dropdown_utils4 - INFO - 옵션 11: ''
2025-06-23 10:42:51,774 - dropdown_utils4 - INFO - 옵션 12: ''
2025-06-23 10:42:51,778 - dropdown_utils4 - INFO - 옵션 13: ''
2025-06-23 10:42:51,783 - dropdown_utils4 - INFO - 옵션 14: ''
2025-06-23 10:42:51,787 - dropdown_utils4 - INFO - 옵션 15: ''
2025-06-23 10:42:51,792 - dropdown_utils4 - INFO - 옵션 16: ''
2025-06-23 10:42:51,796 - dropdown_utils4 - INFO - 옵션 17: ''
2025-06-23 10:42:51,800 - dropdown_utils4 - INFO - 옵션 18: ''
2025-06-23 10:42:51,804 - dropdown_utils4 - INFO - 옵션 19: ''
2025-06-23 10:42:51,809 - dropdown_utils4 - INFO - 옵션 20: ''
2025-06-23 10:42:51,814 - dropdown_utils4 - INFO - 옵션 21: '전체'
2025-06-23 10:42:51,818 - dropdown_utils4 - INFO - 옵션 22: '전체'
2025-06-23 10:42:51,824 - dropdown_utils4 - INFO - 옵션 23: '그룹 없음'
2025-06-23 10:42:51,829 - dropdown_utils4 - INFO - 옵션 24: '그룹 없음'
2025-06-23 10:42:51,833 - dropdown_utils4 - INFO - 옵션 25: '신규수집'
2025-06-23 10:42:51,838 - dropdown_utils4 - INFO - 옵션 26: '신규수집'
2025-06-23 10:42:51,843 - dropdown_utils4 - INFO - 옵션 27: '번역대기'
2025-06-23 10:42:51,848 - dropdown_utils4 - INFO - 옵션 28: '번역대기'
2025-06-23 10:42:51,852 - dropdown_utils4 - INFO - 옵션 29: '등록실행'
2025-06-23 10:42:51,857 - dropdown_utils4 - INFO - 옵션 30: '등록실행'
2025-06-23 10:42:51,861 - dropdown_utils4 - INFO - 옵션 31: '등록A'
2025-06-23 10:42:51,866 - dropdown_utils4 - INFO - 옵션 32: '등록A'
2025-06-23 10:42:51,871 - dropdown_utils4 - INFO - 옵션 33: '등록B'
2025-06-23 10:42:51,876 - dropdown_utils4 - INFO - 옵션 34: '등록B'
2025-06-23 10:42:51,880 - dropdown_utils4 - INFO - 옵션 35: '등록C'
2025-06-23 10:42:51,884 - dropdown_utils4 - INFO - 옵션 36: '등록C'
2025-06-23 10:42:51,890 - dropdown_utils4 - INFO - 옵션 37: ''
2025-06-23 10:42:51,894 - dropdown_utils4 - INFO - 옵션 38: ''
2025-06-23 10:42:51,899 - dropdown_utils4 - INFO - 옵션 39: ''
2025-06-23 10:42:51,903 - dropdown_utils4 - INFO - 옵션 40: ''
2025-06-23 10:42:52,229 - dropdown_utils4 - INFO - 스크롤 후 40개 옵션 확인
2025-06-23 10:42:52,229 - dropdown_utils4 - INFO - 스크롤 4/30
2025-06-23 10:42:52,238 - dropdown_utils4 - INFO - 현재 화면에 40개의 옵션 발견
2025-06-23 10:42:52,244 - dropdown_utils4 - INFO - 옵션 1: ''
2025-06-23 10:42:52,249 - dropdown_utils4 - INFO - 옵션 2: ''
2025-06-23 10:42:52,254 - dropdown_utils4 - INFO - 옵션 3: ''
2025-06-23 10:42:52,258 - dropdown_utils4 - INFO - 옵션 4: ''
2025-06-23 10:42:52,263 - dropdown_utils4 - INFO - 옵션 5: ''
2025-06-23 10:42:52,267 - dropdown_utils4 - INFO - 옵션 6: ''
2025-06-23 10:42:52,271 - dropdown_utils4 - INFO - 옵션 7: ''
2025-06-23 10:42:52,276 - dropdown_utils4 - INFO - 옵션 8: ''
2025-06-23 10:42:52,280 - dropdown_utils4 - INFO - 옵션 9: ''
2025-06-23 10:42:52,284 - dropdown_utils4 - INFO - 옵션 10: ''
2025-06-23 10:42:52,288 - dropdown_utils4 - INFO - 옵션 11: ''
2025-06-23 10:42:52,293 - dropdown_utils4 - INFO - 옵션 12: ''
2025-06-23 10:42:52,297 - dropdown_utils4 - INFO - 옵션 13: ''
2025-06-23 10:42:52,301 - dropdown_utils4 - INFO - 옵션 14: ''
2025-06-23 10:42:52,306 - dropdown_utils4 - INFO - 옵션 15: ''
2025-06-23 10:42:52,310 - dropdown_utils4 - INFO - 옵션 16: ''
2025-06-23 10:42:52,315 - dropdown_utils4 - INFO - 옵션 17: ''
2025-06-23 10:42:52,319 - dropdown_utils4 - INFO - 옵션 18: ''
2025-06-23 10:42:52,323 - dropdown_utils4 - INFO - 옵션 19: ''
2025-06-23 10:42:52,328 - dropdown_utils4 - INFO - 옵션 20: ''
2025-06-23 10:42:52,332 - dropdown_utils4 - INFO - 옵션 21: '전체'
2025-06-23 10:42:52,337 - dropdown_utils4 - INFO - 옵션 22: '전체'
2025-06-23 10:42:52,342 - dropdown_utils4 - INFO - 옵션 23: '그룹 없음'
2025-06-23 10:42:52,346 - dropdown_utils4 - INFO - 옵션 24: '그룹 없음'
2025-06-23 10:42:52,351 - dropdown_utils4 - INFO - 옵션 25: '신규수집'
2025-06-23 10:42:52,356 - dropdown_utils4 - INFO - 옵션 26: '신규수집'
2025-06-23 10:42:52,360 - dropdown_utils4 - INFO - 옵션 27: '번역대기'
2025-06-23 10:42:52,364 - dropdown_utils4 - INFO - 옵션 28: '번역대기'
2025-06-23 10:42:52,369 - dropdown_utils4 - INFO - 옵션 29: '등록실행'
2025-06-23 10:42:52,374 - dropdown_utils4 - INFO - 옵션 30: '등록실행'
2025-06-23 10:42:52,378 - dropdown_utils4 - INFO - 옵션 31: '등록A'
2025-06-23 10:42:52,383 - dropdown_utils4 - INFO - 옵션 32: '등록A'
2025-06-23 10:42:52,387 - dropdown_utils4 - INFO - 옵션 33: '등록B'
2025-06-23 10:42:52,392 - dropdown_utils4 - INFO - 옵션 34: '등록B'
2025-06-23 10:42:52,397 - dropdown_utils4 - INFO - 옵션 35: '등록C'
2025-06-23 10:42:52,401 - dropdown_utils4 - INFO - 옵션 36: '등록C'
2025-06-23 10:42:52,406 - dropdown_utils4 - INFO - 옵션 37: ''
2025-06-23 10:42:52,411 - dropdown_utils4 - INFO - 옵션 38: ''
2025-06-23 10:42:52,415 - dropdown_utils4 - INFO - 옵션 39: ''
2025-06-23 10:42:52,420 - dropdown_utils4 - INFO - 옵션 40: ''
2025-06-23 10:42:52,732 - dropdown_utils4 - INFO - 스크롤 후 40개 옵션 확인
2025-06-23 10:42:52,732 - dropdown_utils4 - INFO - 스크롤 5/30
2025-06-23 10:42:52,740 - dropdown_utils4 - INFO - 현재 화면에 40개의 옵션 발견
2025-06-23 10:42:52,746 - dropdown_utils4 - INFO - 옵션 1: ''
2025-06-23 10:42:52,751 - dropdown_utils4 - INFO - 옵션 2: ''
2025-06-23 10:42:52,756 - dropdown_utils4 - INFO - 옵션 3: ''
2025-06-23 10:42:52,760 - dropdown_utils4 - INFO - 옵션 4: ''
2025-06-23 10:42:52,765 - dropdown_utils4 - INFO - 옵션 5: ''
2025-06-23 10:42:52,769 - dropdown_utils4 - INFO - 옵션 6: ''
2025-06-23 10:42:52,774 - dropdown_utils4 - INFO - 옵션 7: ''
2025-06-23 10:42:52,778 - dropdown_utils4 - INFO - 옵션 8: ''
2025-06-23 10:42:52,782 - dropdown_utils4 - INFO - 옵션 9: ''
2025-06-23 10:42:52,786 - dropdown_utils4 - INFO - 옵션 10: ''
2025-06-23 10:42:52,791 - dropdown_utils4 - INFO - 옵션 11: ''
2025-06-23 10:42:52,795 - dropdown_utils4 - INFO - 옵션 12: ''
2025-06-23 10:42:52,799 - dropdown_utils4 - INFO - 옵션 13: ''
2025-06-23 10:42:52,804 - dropdown_utils4 - INFO - 옵션 14: ''
2025-06-23 10:42:52,808 - dropdown_utils4 - INFO - 옵션 15: ''
2025-06-23 10:42:52,815 - dropdown_utils4 - INFO - 옵션 16: ''
2025-06-23 10:42:52,820 - dropdown_utils4 - INFO - 옵션 17: ''
2025-06-23 10:42:52,825 - dropdown_utils4 - INFO - 옵션 18: ''
2025-06-23 10:42:52,830 - dropdown_utils4 - INFO - 옵션 19: ''
2025-06-23 10:42:52,834 - dropdown_utils4 - INFO - 옵션 20: ''
2025-06-23 10:42:52,839 - dropdown_utils4 - INFO - 옵션 21: '전체'
2025-06-23 10:42:52,843 - dropdown_utils4 - INFO - 옵션 22: '전체'
2025-06-23 10:42:52,848 - dropdown_utils4 - INFO - 옵션 23: '그룹 없음'
2025-06-23 10:42:52,852 - dropdown_utils4 - INFO - 옵션 24: '그룹 없음'
2025-06-23 10:42:52,857 - dropdown_utils4 - INFO - 옵션 25: '신규수집'
2025-06-23 10:42:52,861 - dropdown_utils4 - INFO - 옵션 26: '신규수집'
2025-06-23 10:42:52,866 - dropdown_utils4 - INFO - 옵션 27: '번역대기'
2025-06-23 10:42:52,870 - dropdown_utils4 - INFO - 옵션 28: '번역대기'
2025-06-23 10:42:52,875 - dropdown_utils4 - INFO - 옵션 29: '등록실행'
2025-06-23 10:42:52,880 - dropdown_utils4 - INFO - 옵션 30: '등록실행'
2025-06-23 10:42:52,884 - dropdown_utils4 - INFO - 옵션 31: '등록A'
2025-06-23 10:42:52,889 - dropdown_utils4 - INFO - 옵션 32: '등록A'
2025-06-23 10:42:52,894 - dropdown_utils4 - INFO - 옵션 33: '등록B'
2025-06-23 10:42:52,898 - dropdown_utils4 - INFO - 옵션 34: '등록B'
2025-06-23 10:42:52,902 - dropdown_utils4 - INFO - 옵션 35: '등록C'
2025-06-23 10:42:52,907 - dropdown_utils4 - INFO - 옵션 36: '등록C'
2025-06-23 10:42:52,912 - dropdown_utils4 - INFO - 옵션 37: ''
2025-06-23 10:42:52,916 - dropdown_utils4 - INFO - 옵션 38: ''
2025-06-23 10:42:52,921 - dropdown_utils4 - INFO - 옵션 39: ''
2025-06-23 10:42:52,926 - dropdown_utils4 - INFO - 옵션 40: ''
2025-06-23 10:42:53,237 - dropdown_utils4 - INFO - 스크롤 후 40개 옵션 확인
2025-06-23 10:42:53,237 - dropdown_utils4 - INFO - 스크롤 6/30
2025-06-23 10:42:53,245 - dropdown_utils4 - INFO - 현재 화면에 40개의 옵션 발견
2025-06-23 10:42:53,250 - dropdown_utils4 - INFO - 옵션 1: ''
2025-06-23 10:42:53,254 - dropdown_utils4 - INFO - 옵션 2: ''
2025-06-23 10:42:53,259 - dropdown_utils4 - INFO - 옵션 3: ''
2025-06-23 10:42:53,264 - dropdown_utils4 - INFO - 옵션 4: ''
2025-06-23 10:42:53,269 - dropdown_utils4 - INFO - 옵션 5: ''
2025-06-23 10:42:53,274 - dropdown_utils4 - INFO - 옵션 6: ''
2025-06-23 10:42:53,279 - dropdown_utils4 - INFO - 옵션 7: ''
2025-06-23 10:42:53,284 - dropdown_utils4 - INFO - 옵션 8: ''
2025-06-23 10:42:53,289 - dropdown_utils4 - INFO - 옵션 9: ''
2025-06-23 10:42:53,294 - dropdown_utils4 - INFO - 옵션 10: ''
2025-06-23 10:42:53,299 - dropdown_utils4 - INFO - 옵션 11: ''
2025-06-23 10:42:53,304 - dropdown_utils4 - INFO - 옵션 12: ''
2025-06-23 10:42:53,310 - dropdown_utils4 - INFO - 옵션 13: ''
2025-06-23 10:42:53,327 - dropdown_utils4 - INFO - 옵션 14: ''
2025-06-23 10:42:53,335 - dropdown_utils4 - INFO - 옵션 15: ''
2025-06-23 10:42:53,347 - dropdown_utils4 - INFO - 옵션 16: ''
2025-06-23 10:42:53,352 - dropdown_utils4 - INFO - 옵션 17: ''
2025-06-23 10:42:53,356 - dropdown_utils4 - INFO - 옵션 18: ''
2025-06-23 10:42:53,361 - dropdown_utils4 - INFO - 옵션 19: ''
2025-06-23 10:42:53,365 - dropdown_utils4 - INFO - 옵션 20: ''
2025-06-23 10:42:53,370 - dropdown_utils4 - INFO - 옵션 21: '전체'
2025-06-23 10:42:53,375 - dropdown_utils4 - INFO - 옵션 22: '전체'
2025-06-23 10:42:53,380 - dropdown_utils4 - INFO - 옵션 23: '그룹 없음'
2025-06-23 10:42:53,384 - dropdown_utils4 - INFO - 옵션 24: '그룹 없음'
2025-06-23 10:42:53,389 - dropdown_utils4 - INFO - 옵션 25: '신규수집'
2025-06-23 10:42:53,394 - dropdown_utils4 - INFO - 옵션 26: '신규수집'
2025-06-23 10:42:53,399 - dropdown_utils4 - INFO - 옵션 27: '번역대기'
2025-06-23 10:42:53,404 - dropdown_utils4 - INFO - 옵션 28: '번역대기'
2025-06-23 10:42:53,409 - dropdown_utils4 - INFO - 옵션 29: '등록실행'
2025-06-23 10:42:53,413 - dropdown_utils4 - INFO - 옵션 30: '등록실행'
2025-06-23 10:42:53,418 - dropdown_utils4 - INFO - 옵션 31: '등록A'
2025-06-23 10:42:53,423 - dropdown_utils4 - INFO - 옵션 32: '등록A'
2025-06-23 10:42:53,429 - dropdown_utils4 - INFO - 옵션 33: '등록B'
2025-06-23 10:42:53,433 - dropdown_utils4 - INFO - 옵션 34: '등록B'
2025-06-23 10:42:53,438 - dropdown_utils4 - INFO - 옵션 35: '등록C'
2025-06-23 10:42:53,443 - dropdown_utils4 - INFO - 옵션 36: '등록C'
2025-06-23 10:42:53,448 - dropdown_utils4 - INFO - 옵션 37: ''
2025-06-23 10:42:53,453 - dropdown_utils4 - INFO - 옵션 38: ''
2025-06-23 10:42:53,459 - dropdown_utils4 - INFO - 옵션 39: ''
2025-06-23 10:42:53,463 - dropdown_utils4 - INFO - 옵션 40: ''
2025-06-23 10:42:53,775 - dropdown_utils4 - INFO - 스크롤 후 40개 옵션 확인
2025-06-23 10:42:53,775 - dropdown_utils4 - INFO - 스크롤 7/30
2025-06-23 10:42:53,782 - dropdown_utils4 - INFO - 현재 화면에 40개의 옵션 발견
2025-06-23 10:42:53,787 - dropdown_utils4 - INFO - 옵션 1: ''
2025-06-23 10:42:53,792 - dropdown_utils4 - INFO - 옵션 2: ''
2025-06-23 10:42:53,797 - dropdown_utils4 - INFO - 옵션 3: ''
2025-06-23 10:42:53,801 - dropdown_utils4 - INFO - 옵션 4: ''
2025-06-23 10:42:53,806 - dropdown_utils4 - INFO - 옵션 5: ''
2025-06-23 10:42:53,812 - dropdown_utils4 - INFO - 옵션 6: ''
2025-06-23 10:42:53,817 - dropdown_utils4 - INFO - 옵션 7: ''
2025-06-23 10:42:53,821 - dropdown_utils4 - INFO - 옵션 8: ''
2025-06-23 10:42:53,826 - dropdown_utils4 - INFO - 옵션 9: ''
2025-06-23 10:42:53,831 - dropdown_utils4 - INFO - 옵션 10: ''
2025-06-23 10:42:53,835 - dropdown_utils4 - INFO - 옵션 11: ''
2025-06-23 10:42:53,840 - dropdown_utils4 - INFO - 옵션 12: ''
2025-06-23 10:42:53,845 - dropdown_utils4 - INFO - 옵션 13: ''
2025-06-23 10:42:53,850 - dropdown_utils4 - INFO - 옵션 14: ''
2025-06-23 10:42:53,855 - dropdown_utils4 - INFO - 옵션 15: ''
2025-06-23 10:42:53,860 - dropdown_utils4 - INFO - 옵션 16: ''
2025-06-23 10:42:53,864 - dropdown_utils4 - INFO - 옵션 17: ''
2025-06-23 10:42:53,869 - dropdown_utils4 - INFO - 옵션 18: ''
2025-06-23 10:42:53,875 - dropdown_utils4 - INFO - 옵션 19: ''
2025-06-23 10:42:53,879 - dropdown_utils4 - INFO - 옵션 20: ''
2025-06-23 10:42:53,884 - dropdown_utils4 - INFO - 옵션 21: '전체'
2025-06-23 10:42:53,890 - dropdown_utils4 - INFO - 옵션 22: '전체'
2025-06-23 10:42:53,895 - dropdown_utils4 - INFO - 옵션 23: '그룹 없음'
2025-06-23 10:42:53,899 - dropdown_utils4 - INFO - 옵션 24: '그룹 없음'
2025-06-23 10:42:53,905 - dropdown_utils4 - INFO - 옵션 25: '신규수집'
2025-06-23 10:42:53,910 - dropdown_utils4 - INFO - 옵션 26: '신규수집'
2025-06-23 10:42:53,915 - dropdown_utils4 - INFO - 옵션 27: '번역대기'
2025-06-23 10:42:53,920 - dropdown_utils4 - INFO - 옵션 28: '번역대기'
2025-06-23 10:42:53,925 - dropdown_utils4 - INFO - 옵션 29: '등록실행'
2025-06-23 10:42:53,930 - dropdown_utils4 - INFO - 옵션 30: '등록실행'
2025-06-23 10:42:53,935 - dropdown_utils4 - INFO - 옵션 31: '등록A'
2025-06-23 10:42:53,940 - dropdown_utils4 - INFO - 옵션 32: '등록A'
2025-06-23 10:42:53,945 - dropdown_utils4 - INFO - 옵션 33: '등록B'
2025-06-23 10:42:53,950 - dropdown_utils4 - INFO - 옵션 34: '등록B'
2025-06-23 10:42:53,955 - dropdown_utils4 - INFO - 옵션 35: '등록C'
2025-06-23 10:42:53,960 - dropdown_utils4 - INFO - 옵션 36: '등록C'
2025-06-23 10:42:53,964 - dropdown_utils4 - INFO - 옵션 37: ''
2025-06-23 10:42:53,969 - dropdown_utils4 - INFO - 옵션 38: ''
2025-06-23 10:42:53,974 - dropdown_utils4 - INFO - 옵션 39: ''
2025-06-23 10:42:53,979 - dropdown_utils4 - INFO - 옵션 40: ''
2025-06-23 10:42:54,291 - dropdown_utils4 - INFO - 스크롤 후 40개 옵션 확인
2025-06-23 10:42:54,291 - dropdown_utils4 - INFO - 스크롤 8/30
2025-06-23 10:42:54,298 - dropdown_utils4 - INFO - 현재 화면에 40개의 옵션 발견
2025-06-23 10:42:54,303 - dropdown_utils4 - INFO - 옵션 1: ''
2025-06-23 10:42:54,308 - dropdown_utils4 - INFO - 옵션 2: ''
2025-06-23 10:42:54,313 - dropdown_utils4 - INFO - 옵션 3: ''
2025-06-23 10:42:54,317 - dropdown_utils4 - INFO - 옵션 4: ''
2025-06-23 10:42:54,322 - dropdown_utils4 - INFO - 옵션 5: ''
2025-06-23 10:42:54,326 - dropdown_utils4 - INFO - 옵션 6: ''
2025-06-23 10:42:54,330 - dropdown_utils4 - INFO - 옵션 7: ''
2025-06-23 10:42:54,334 - dropdown_utils4 - INFO - 옵션 8: ''
2025-06-23 10:42:54,339 - dropdown_utils4 - INFO - 옵션 9: ''
2025-06-23 10:42:54,343 - dropdown_utils4 - INFO - 옵션 10: ''
2025-06-23 10:42:54,348 - dropdown_utils4 - INFO - 옵션 11: ''
2025-06-23 10:42:54,352 - dropdown_utils4 - INFO - 옵션 12: ''
2025-06-23 10:42:54,356 - dropdown_utils4 - INFO - 옵션 13: ''
2025-06-23 10:42:54,360 - dropdown_utils4 - INFO - 옵션 14: ''
2025-06-23 10:42:54,365 - dropdown_utils4 - INFO - 옵션 15: ''
2025-06-23 10:42:54,369 - dropdown_utils4 - INFO - 옵션 16: ''
2025-06-23 10:42:54,373 - dropdown_utils4 - INFO - 옵션 17: ''
2025-06-23 10:42:54,378 - dropdown_utils4 - INFO - 옵션 18: ''
2025-06-23 10:42:54,382 - dropdown_utils4 - INFO - 옵션 19: ''
2025-06-23 10:42:54,386 - dropdown_utils4 - INFO - 옵션 20: ''
2025-06-23 10:42:54,391 - dropdown_utils4 - INFO - 옵션 21: '전체'
2025-06-23 10:42:54,396 - dropdown_utils4 - INFO - 옵션 22: '전체'
2025-06-23 10:42:54,400 - dropdown_utils4 - INFO - 옵션 23: '그룹 없음'
2025-06-23 10:42:54,405 - dropdown_utils4 - INFO - 옵션 24: '그룹 없음'
2025-06-23 10:42:54,410 - dropdown_utils4 - INFO - 옵션 25: '신규수집'
2025-06-23 10:42:54,414 - dropdown_utils4 - INFO - 옵션 26: '신규수집'
2025-06-23 10:42:54,419 - dropdown_utils4 - INFO - 옵션 27: '번역대기'
2025-06-23 10:42:54,424 - dropdown_utils4 - INFO - 옵션 28: '번역대기'
2025-06-23 10:42:54,428 - dropdown_utils4 - INFO - 옵션 29: '등록실행'
2025-06-23 10:42:54,433 - dropdown_utils4 - INFO - 옵션 30: '등록실행'
2025-06-23 10:42:54,438 - dropdown_utils4 - INFO - 옵션 31: '등록A'
2025-06-23 10:42:54,442 - dropdown_utils4 - INFO - 옵션 32: '등록A'
2025-06-23 10:42:54,447 - dropdown_utils4 - INFO - 옵션 33: '등록B'
2025-06-23 10:42:54,451 - dropdown_utils4 - INFO - 옵션 34: '등록B'
2025-06-23 10:42:54,456 - dropdown_utils4 - INFO - 옵션 35: '등록C'
2025-06-23 10:42:54,461 - dropdown_utils4 - INFO - 옵션 36: '등록C'
2025-06-23 10:42:54,465 - dropdown_utils4 - INFO - 옵션 37: ''
2025-06-23 10:42:54,469 - dropdown_utils4 - INFO - 옵션 38: ''
2025-06-23 10:42:54,474 - dropdown_utils4 - INFO - 옵션 39: ''
2025-06-23 10:42:54,479 - dropdown_utils4 - INFO - 옵션 40: ''
2025-06-23 10:42:54,805 - dropdown_utils4 - INFO - 스크롤 후 40개 옵션 확인
2025-06-23 10:42:54,805 - dropdown_utils4 - INFO - 스크롤 9/30
2025-06-23 10:42:54,815 - dropdown_utils4 - INFO - 현재 화면에 40개의 옵션 발견
2025-06-23 10:42:54,821 - dropdown_utils4 - INFO - 옵션 1: ''
2025-06-23 10:42:54,825 - dropdown_utils4 - INFO - 옵션 2: ''
2025-06-23 10:42:54,830 - dropdown_utils4 - INFO - 옵션 3: ''
2025-06-23 10:42:54,834 - dropdown_utils4 - INFO - 옵션 4: ''
2025-06-23 10:42:54,839 - dropdown_utils4 - INFO - 옵션 5: ''
2025-06-23 10:42:54,843 - dropdown_utils4 - INFO - 옵션 6: ''
2025-06-23 10:42:54,848 - dropdown_utils4 - INFO - 옵션 7: ''
2025-06-23 10:42:54,852 - dropdown_utils4 - INFO - 옵션 8: ''
2025-06-23 10:42:54,856 - dropdown_utils4 - INFO - 옵션 9: ''
2025-06-23 10:42:54,861 - dropdown_utils4 - INFO - 옵션 10: ''
2025-06-23 10:42:54,865 - dropdown_utils4 - INFO - 옵션 11: ''
2025-06-23 10:42:54,869 - dropdown_utils4 - INFO - 옵션 12: ''
2025-06-23 10:42:54,874 - dropdown_utils4 - INFO - 옵션 13: ''
2025-06-23 10:42:54,879 - dropdown_utils4 - INFO - 옵션 14: ''
2025-06-23 10:42:54,883 - dropdown_utils4 - INFO - 옵션 15: ''
2025-06-23 10:42:54,887 - dropdown_utils4 - INFO - 옵션 16: ''
2025-06-23 10:42:54,892 - dropdown_utils4 - INFO - 옵션 17: ''
2025-06-23 10:42:54,896 - dropdown_utils4 - INFO - 옵션 18: ''
2025-06-23 10:42:54,900 - dropdown_utils4 - INFO - 옵션 19: ''
2025-06-23 10:42:54,904 - dropdown_utils4 - INFO - 옵션 20: ''
2025-06-23 10:42:54,909 - dropdown_utils4 - INFO - 옵션 21: '전체'
2025-06-23 10:42:54,913 - dropdown_utils4 - INFO - 옵션 22: '전체'
2025-06-23 10:42:54,918 - dropdown_utils4 - INFO - 옵션 23: '그룹 없음'
2025-06-23 10:42:54,923 - dropdown_utils4 - INFO - 옵션 24: '그룹 없음'
2025-06-23 10:42:54,928 - dropdown_utils4 - INFO - 옵션 25: '신규수집'
2025-06-23 10:42:54,932 - dropdown_utils4 - INFO - 옵션 26: '신규수집'
2025-06-23 10:42:54,937 - dropdown_utils4 - INFO - 옵션 27: '번역대기'
2025-06-23 10:42:54,942 - dropdown_utils4 - INFO - 옵션 28: '번역대기'
2025-06-23 10:42:54,947 - dropdown_utils4 - INFO - 옵션 29: '등록실행'
2025-06-23 10:42:54,951 - dropdown_utils4 - INFO - 옵션 30: '등록실행'
2025-06-23 10:42:54,956 - dropdown_utils4 - INFO - 옵션 31: '등록A'
2025-06-23 10:42:54,961 - dropdown_utils4 - INFO - 옵션 32: '등록A'
2025-06-23 10:42:54,966 - dropdown_utils4 - INFO - 옵션 33: '등록B'
2025-06-23 10:42:54,970 - dropdown_utils4 - INFO - 옵션 34: '등록B'
2025-06-23 10:42:54,975 - dropdown_utils4 - INFO - 옵션 35: '등록C'
2025-06-23 10:42:54,979 - dropdown_utils4 - INFO - 옵션 36: '등록C'
2025-06-23 10:42:54,984 - dropdown_utils4 - INFO - 옵션 37: ''
2025-06-23 10:42:54,988 - dropdown_utils4 - INFO - 옵션 38: ''
2025-06-23 10:42:54,993 - dropdown_utils4 - INFO - 옵션 39: ''
2025-06-23 10:42:54,998 - dropdown_utils4 - INFO - 옵션 40: ''
2025-06-23 10:42:55,335 - dropdown_utils4 - INFO - 스크롤 후 40개 옵션 확인
2025-06-23 10:42:55,335 - dropdown_utils4 - INFO - 스크롤 10/30
2025-06-23 10:42:55,343 - dropdown_utils4 - INFO - 현재 화면에 40개의 옵션 발견
2025-06-23 10:42:55,349 - dropdown_utils4 - INFO - 옵션 1: ''
2025-06-23 10:42:55,354 - dropdown_utils4 - INFO - 옵션 2: ''
2025-06-23 10:42:55,360 - dropdown_utils4 - INFO - 옵션 3: ''
2025-06-23 10:42:55,365 - dropdown_utils4 - INFO - 옵션 4: ''
2025-06-23 10:42:55,369 - dropdown_utils4 - INFO - 옵션 5: ''
2025-06-23 10:42:55,374 - dropdown_utils4 - INFO - 옵션 6: ''
2025-06-23 10:42:55,379 - dropdown_utils4 - INFO - 옵션 7: ''
2025-06-23 10:42:55,383 - dropdown_utils4 - INFO - 옵션 8: ''
2025-06-23 10:42:55,388 - dropdown_utils4 - INFO - 옵션 9: ''
2025-06-23 10:42:55,392 - dropdown_utils4 - INFO - 옵션 10: ''
2025-06-23 10:42:55,396 - dropdown_utils4 - INFO - 옵션 11: ''
2025-06-23 10:42:55,400 - dropdown_utils4 - INFO - 옵션 12: ''
2025-06-23 10:42:55,405 - dropdown_utils4 - INFO - 옵션 13: ''
2025-06-23 10:42:55,409 - dropdown_utils4 - INFO - 옵션 14: ''
2025-06-23 10:42:55,413 - dropdown_utils4 - INFO - 옵션 15: ''
2025-06-23 10:42:55,417 - dropdown_utils4 - INFO - 옵션 16: ''
2025-06-23 10:42:55,422 - dropdown_utils4 - INFO - 옵션 17: ''
2025-06-23 10:42:55,426 - dropdown_utils4 - INFO - 옵션 18: ''
2025-06-23 10:42:55,430 - dropdown_utils4 - INFO - 옵션 19: ''
2025-06-23 10:42:55,434 - dropdown_utils4 - INFO - 옵션 20: ''
2025-06-23 10:42:55,439 - dropdown_utils4 - INFO - 옵션 21: '전체'
2025-06-23 10:42:55,444 - dropdown_utils4 - INFO - 옵션 22: '전체'
2025-06-23 10:42:55,448 - dropdown_utils4 - INFO - 옵션 23: '그룹 없음'
2025-06-23 10:42:55,453 - dropdown_utils4 - INFO - 옵션 24: '그룹 없음'
2025-06-23 10:42:55,458 - dropdown_utils4 - INFO - 옵션 25: '신규수집'
2025-06-23 10:42:55,462 - dropdown_utils4 - INFO - 옵션 26: '신규수집'
2025-06-23 10:42:55,467 - dropdown_utils4 - INFO - 옵션 27: '번역대기'
2025-06-23 10:42:55,472 - dropdown_utils4 - INFO - 옵션 28: '번역대기'
2025-06-23 10:42:55,477 - dropdown_utils4 - INFO - 옵션 29: '등록실행'
2025-06-23 10:42:55,481 - dropdown_utils4 - INFO - 옵션 30: '등록실행'
2025-06-23 10:42:55,486 - dropdown_utils4 - INFO - 옵션 31: '등록A'
2025-06-23 10:42:55,491 - dropdown_utils4 - INFO - 옵션 32: '등록A'
2025-06-23 10:42:55,495 - dropdown_utils4 - INFO - 옵션 33: '등록B'
2025-06-23 10:42:55,500 - dropdown_utils4 - INFO - 옵션 34: '등록B'
2025-06-23 10:42:55,504 - dropdown_utils4 - INFO - 옵션 35: '등록C'
2025-06-23 10:42:55,509 - dropdown_utils4 - INFO - 옵션 36: '등록C'
2025-06-23 10:42:55,513 - dropdown_utils4 - INFO - 옵션 37: ''
2025-06-23 10:42:55,518 - dropdown_utils4 - INFO - 옵션 38: ''
2025-06-23 10:42:55,522 - dropdown_utils4 - INFO - 옵션 39: ''
2025-06-23 10:42:55,527 - dropdown_utils4 - INFO - 옵션 40: ''
2025-06-23 10:42:55,838 - dropdown_utils4 - INFO - 스크롤 후 40개 옵션 확인
2025-06-23 10:42:55,839 - dropdown_utils4 - INFO - 스크롤 11/30
2025-06-23 10:42:55,846 - dropdown_utils4 - INFO - 현재 화면에 40개의 옵션 발견
2025-06-23 10:42:55,851 - dropdown_utils4 - INFO - 옵션 1: ''
2025-06-23 10:42:55,856 - dropdown_utils4 - INFO - 옵션 2: ''
2025-06-23 10:42:55,862 - dropdown_utils4 - INFO - 옵션 3: ''
2025-06-23 10:42:55,866 - dropdown_utils4 - INFO - 옵션 4: ''
2025-06-23 10:42:55,870 - dropdown_utils4 - INFO - 옵션 5: ''
2025-06-23 10:42:55,875 - dropdown_utils4 - INFO - 옵션 6: ''
2025-06-23 10:42:55,879 - dropdown_utils4 - INFO - 옵션 7: ''
2025-06-23 10:42:55,883 - dropdown_utils4 - INFO - 옵션 8: ''
2025-06-23 10:42:55,888 - dropdown_utils4 - INFO - 옵션 9: ''
2025-06-23 10:42:55,892 - dropdown_utils4 - INFO - 옵션 10: ''
2025-06-23 10:42:55,896 - dropdown_utils4 - INFO - 옵션 11: ''
2025-06-23 10:42:55,903 - dropdown_utils4 - INFO - 옵션 12: ''
2025-06-23 10:42:55,907 - dropdown_utils4 - INFO - 옵션 13: ''
2025-06-23 10:42:55,912 - dropdown_utils4 - INFO - 옵션 14: ''
2025-06-23 10:42:55,916 - dropdown_utils4 - INFO - 옵션 15: ''
2025-06-23 10:42:55,921 - dropdown_utils4 - INFO - 옵션 16: ''
2025-06-23 10:42:55,925 - dropdown_utils4 - INFO - 옵션 17: ''
2025-06-23 10:42:55,929 - dropdown_utils4 - INFO - 옵션 18: ''
2025-06-23 10:42:55,934 - dropdown_utils4 - INFO - 옵션 19: ''
2025-06-23 10:42:55,938 - dropdown_utils4 - INFO - 옵션 20: ''
2025-06-23 10:42:55,943 - dropdown_utils4 - INFO - 옵션 21: '전체'
2025-06-23 10:42:55,947 - dropdown_utils4 - INFO - 옵션 22: '전체'
2025-06-23 10:42:55,952 - dropdown_utils4 - INFO - 옵션 23: '그룹 없음'
2025-06-23 10:42:55,956 - dropdown_utils4 - INFO - 옵션 24: '그룹 없음'
2025-06-23 10:42:55,961 - dropdown_utils4 - INFO - 옵션 25: '신규수집'
2025-06-23 10:42:55,965 - dropdown_utils4 - INFO - 옵션 26: '신규수집'
2025-06-23 10:42:55,970 - dropdown_utils4 - INFO - 옵션 27: '번역대기'
2025-06-23 10:42:55,975 - dropdown_utils4 - INFO - 옵션 28: '번역대기'
2025-06-23 10:42:55,979 - dropdown_utils4 - INFO - 옵션 29: '등록실행'
2025-06-23 10:42:55,984 - dropdown_utils4 - INFO - 옵션 30: '등록실행'
2025-06-23 10:42:55,988 - dropdown_utils4 - INFO - 옵션 31: '등록A'
2025-06-23 10:42:55,993 - dropdown_utils4 - INFO - 옵션 32: '등록A'
2025-06-23 10:42:55,997 - dropdown_utils4 - INFO - 옵션 33: '등록B'
2025-06-23 10:42:56,002 - dropdown_utils4 - INFO - 옵션 34: '등록B'
2025-06-23 10:42:56,007 - dropdown_utils4 - INFO - 옵션 35: '등록C'
2025-06-23 10:42:56,011 - dropdown_utils4 - INFO - 옵션 36: '등록C'
2025-06-23 10:42:56,016 - dropdown_utils4 - INFO - 옵션 37: ''
2025-06-23 10:42:56,020 - dropdown_utils4 - INFO - 옵션 38: ''
2025-06-23 10:42:56,025 - dropdown_utils4 - INFO - 옵션 39: ''
2025-06-23 10:42:56,029 - dropdown_utils4 - INFO - 옵션 40: ''
2025-06-23 10:42:56,342 - dropdown_utils4 - INFO - 스크롤 후 40개 옵션 확인
2025-06-23 10:42:56,342 - dropdown_utils4 - INFO - 스크롤 12/30
2025-06-23 10:42:56,349 - dropdown_utils4 - INFO - 현재 화면에 40개의 옵션 발견
2025-06-23 10:42:56,354 - dropdown_utils4 - INFO - 옵션 1: ''
2025-06-23 10:42:56,359 - dropdown_utils4 - INFO - 옵션 2: ''
2025-06-23 10:42:56,365 - dropdown_utils4 - INFO - 옵션 3: ''
2025-06-23 10:42:56,370 - dropdown_utils4 - INFO - 옵션 4: ''
2025-06-23 10:42:56,376 - dropdown_utils4 - INFO - 옵션 5: ''
2025-06-23 10:42:56,381 - dropdown_utils4 - INFO - 옵션 6: ''
2025-06-23 10:42:56,386 - dropdown_utils4 - INFO - 옵션 7: ''
2025-06-23 10:42:56,391 - dropdown_utils4 - INFO - 옵션 8: ''
2025-06-23 10:42:56,395 - dropdown_utils4 - INFO - 옵션 9: ''
2025-06-23 10:42:56,400 - dropdown_utils4 - INFO - 옵션 10: ''
2025-06-23 10:42:56,405 - dropdown_utils4 - INFO - 옵션 11: ''
2025-06-23 10:42:56,409 - dropdown_utils4 - INFO - 옵션 12: ''
2025-06-23 10:42:56,414 - dropdown_utils4 - INFO - 옵션 13: ''
2025-06-23 10:42:56,418 - dropdown_utils4 - INFO - 옵션 14: ''
2025-06-23 10:42:56,422 - dropdown_utils4 - INFO - 옵션 15: ''
2025-06-23 10:42:56,427 - dropdown_utils4 - INFO - 옵션 16: ''
2025-06-23 10:42:56,431 - dropdown_utils4 - INFO - 옵션 17: ''
2025-06-23 10:42:56,436 - dropdown_utils4 - INFO - 옵션 18: ''
2025-06-23 10:42:56,441 - dropdown_utils4 - INFO - 옵션 19: ''
2025-06-23 10:42:56,445 - dropdown_utils4 - INFO - 옵션 20: ''
2025-06-23 10:42:56,450 - dropdown_utils4 - INFO - 옵션 21: '전체'
2025-06-23 10:42:56,455 - dropdown_utils4 - INFO - 옵션 22: '전체'
2025-06-23 10:42:56,460 - dropdown_utils4 - INFO - 옵션 23: '그룹 없음'
2025-06-23 10:42:56,465 - dropdown_utils4 - INFO - 옵션 24: '그룹 없음'
2025-06-23 10:42:56,470 - dropdown_utils4 - INFO - 옵션 25: '신규수집'
2025-06-23 10:42:56,475 - dropdown_utils4 - INFO - 옵션 26: '신규수집'
2025-06-23 10:42:56,480 - dropdown_utils4 - INFO - 옵션 27: '번역대기'
2025-06-23 10:42:56,485 - dropdown_utils4 - INFO - 옵션 28: '번역대기'
2025-06-23 10:42:56,490 - dropdown_utils4 - INFO - 옵션 29: '등록실행'
2025-06-23 10:42:56,495 - dropdown_utils4 - INFO - 옵션 30: '등록실행'
2025-06-23 10:42:56,500 - dropdown_utils4 - INFO - 옵션 31: '등록A'
2025-06-23 10:42:56,505 - dropdown_utils4 - INFO - 옵션 32: '등록A'
2025-06-23 10:42:56,510 - dropdown_utils4 - INFO - 옵션 33: '등록B'
2025-06-23 10:42:56,515 - dropdown_utils4 - INFO - 옵션 34: '등록B'
2025-06-23 10:42:56,520 - dropdown_utils4 - INFO - 옵션 35: '등록C'
2025-06-23 10:42:56,526 - dropdown_utils4 - INFO - 옵션 36: '등록C'
2025-06-23 10:42:56,531 - dropdown_utils4 - INFO - 옵션 37: ''
2025-06-23 10:42:56,537 - dropdown_utils4 - INFO - 옵션 38: ''
2025-06-23 10:42:56,543 - dropdown_utils4 - INFO - 옵션 39: ''
2025-06-23 10:42:56,548 - dropdown_utils4 - INFO - 옵션 40: ''
2025-06-23 10:42:56,859 - dropdown_utils4 - INFO - 스크롤 후 40개 옵션 확인
2025-06-23 10:42:56,860 - dropdown_utils4 - INFO - 스크롤 13/30
2025-06-23 10:42:56,867 - dropdown_utils4 - INFO - 현재 화면에 40개의 옵션 발견
2025-06-23 10:42:56,873 - dropdown_utils4 - INFO - 옵션 1: ''
2025-06-23 10:42:56,878 - dropdown_utils4 - INFO - 옵션 2: ''
2025-06-23 10:42:56,883 - dropdown_utils4 - INFO - 옵션 3: ''
2025-06-23 10:42:56,888 - dropdown_utils4 - INFO - 옵션 4: ''
2025-06-23 10:42:56,893 - dropdown_utils4 - INFO - 옵션 5: ''
2025-06-23 10:42:56,897 - dropdown_utils4 - INFO - 옵션 6: ''
2025-06-23 10:42:56,902 - dropdown_utils4 - INFO - 옵션 7: ''
2025-06-23 10:42:56,907 - dropdown_utils4 - INFO - 옵션 8: ''
2025-06-23 10:42:56,911 - dropdown_utils4 - INFO - 옵션 9: ''
2025-06-23 10:42:56,916 - dropdown_utils4 - INFO - 옵션 10: ''
2025-06-23 10:42:56,920 - dropdown_utils4 - INFO - 옵션 11: ''
2025-06-23 10:42:56,926 - dropdown_utils4 - INFO - 옵션 12: ''
2025-06-23 10:42:56,930 - dropdown_utils4 - INFO - 옵션 13: ''
2025-06-23 10:42:56,935 - dropdown_utils4 - INFO - 옵션 14: ''
2025-06-23 10:42:56,940 - dropdown_utils4 - INFO - 옵션 15: ''
2025-06-23 10:42:56,945 - dropdown_utils4 - INFO - 옵션 16: ''
2025-06-23 10:42:56,949 - dropdown_utils4 - INFO - 옵션 17: ''
2025-06-23 10:42:56,954 - dropdown_utils4 - INFO - 옵션 18: ''
2025-06-23 10:42:56,959 - dropdown_utils4 - INFO - 옵션 19: ''
2025-06-23 10:42:56,963 - dropdown_utils4 - INFO - 옵션 20: ''
2025-06-23 10:42:56,968 - dropdown_utils4 - INFO - 옵션 21: '전체'
2025-06-23 10:42:56,973 - dropdown_utils4 - INFO - 옵션 22: '전체'
2025-06-23 10:42:56,978 - dropdown_utils4 - INFO - 옵션 23: '그룹 없음'
2025-06-23 10:42:56,983 - dropdown_utils4 - INFO - 옵션 24: '그룹 없음'
2025-06-23 10:42:56,989 - dropdown_utils4 - INFO - 옵션 25: '신규수집'
2025-06-23 10:42:56,993 - dropdown_utils4 - INFO - 옵션 26: '신규수집'
2025-06-23 10:42:56,998 - dropdown_utils4 - INFO - 옵션 27: '번역대기'
2025-06-23 10:42:57,003 - dropdown_utils4 - INFO - 옵션 28: '번역대기'
2025-06-23 10:42:57,009 - dropdown_utils4 - INFO - 옵션 29: '등록실행'
2025-06-23 10:42:57,013 - dropdown_utils4 - INFO - 옵션 30: '등록실행'
2025-06-23 10:42:57,018 - dropdown_utils4 - INFO - 옵션 31: '등록A'
2025-06-23 10:42:57,023 - dropdown_utils4 - INFO - 옵션 32: '등록A'
2025-06-23 10:42:57,029 - dropdown_utils4 - INFO - 옵션 33: '등록B'
2025-06-23 10:42:57,033 - dropdown_utils4 - INFO - 옵션 34: '등록B'
2025-06-23 10:42:57,039 - dropdown_utils4 - INFO - 옵션 35: '등록C'
2025-06-23 10:42:57,044 - dropdown_utils4 - INFO - 옵션 36: '등록C'
2025-06-23 10:42:57,049 - dropdown_utils4 - INFO - 옵션 37: ''
2025-06-23 10:42:57,054 - dropdown_utils4 - INFO - 옵션 38: ''
2025-06-23 10:42:57,059 - dropdown_utils4 - INFO - 옵션 39: ''
2025-06-23 10:42:57,064 - dropdown_utils4 - INFO - 옵션 40: ''
2025-06-23 10:42:57,399 - dropdown_utils4 - INFO - 스크롤 후 40개 옵션 확인
2025-06-23 10:42:57,400 - dropdown_utils4 - INFO - 스크롤 14/30
2025-06-23 10:42:57,429 - dropdown_utils4 - INFO - 현재 화면에 40개의 옵션 발견
2025-06-23 10:42:57,439 - dropdown_utils4 - INFO - 옵션 1: ''
2025-06-23 10:42:57,444 - dropdown_utils4 - INFO - 옵션 2: ''
2025-06-23 10:42:57,449 - dropdown_utils4 - INFO - 옵션 3: ''
2025-06-23 10:42:57,453 - dropdown_utils4 - INFO - 옵션 4: ''
2025-06-23 10:42:57,458 - dropdown_utils4 - INFO - 옵션 5: ''
2025-06-23 10:42:57,462 - dropdown_utils4 - INFO - 옵션 6: ''
2025-06-23 10:42:57,466 - dropdown_utils4 - INFO - 옵션 7: ''
2025-06-23 10:42:57,471 - dropdown_utils4 - INFO - 옵션 8: ''
2025-06-23 10:42:57,475 - dropdown_utils4 - INFO - 옵션 9: ''
2025-06-23 10:42:57,479 - dropdown_utils4 - INFO - 옵션 10: ''
2025-06-23 10:42:57,484 - dropdown_utils4 - INFO - 옵션 11: ''
2025-06-23 10:42:57,488 - dropdown_utils4 - INFO - 옵션 12: ''
2025-06-23 10:42:57,493 - dropdown_utils4 - INFO - 옵션 13: ''
2025-06-23 10:42:57,497 - dropdown_utils4 - INFO - 옵션 14: ''
2025-06-23 10:42:57,501 - dropdown_utils4 - INFO - 옵션 15: ''
2025-06-23 10:42:57,506 - dropdown_utils4 - INFO - 옵션 16: ''
2025-06-23 10:42:57,511 - dropdown_utils4 - INFO - 옵션 17: ''
2025-06-23 10:42:57,515 - dropdown_utils4 - INFO - 옵션 18: ''
2025-06-23 10:42:57,519 - dropdown_utils4 - INFO - 옵션 19: ''
2025-06-23 10:42:57,524 - dropdown_utils4 - INFO - 옵션 20: ''
2025-06-23 10:42:57,529 - dropdown_utils4 - INFO - 옵션 21: '전체'
2025-06-23 10:42:57,534 - dropdown_utils4 - INFO - 옵션 22: '전체'
2025-06-23 10:42:57,539 - dropdown_utils4 - INFO - 옵션 23: '그룹 없음'
2025-06-23 10:42:57,544 - dropdown_utils4 - INFO - 옵션 24: '그룹 없음'
2025-06-23 10:42:57,549 - dropdown_utils4 - INFO - 옵션 25: '신규수집'
2025-06-23 10:42:57,553 - dropdown_utils4 - INFO - 옵션 26: '신규수집'
2025-06-23 10:42:57,558 - dropdown_utils4 - INFO - 옵션 27: '번역대기'
2025-06-23 10:42:57,563 - dropdown_utils4 - INFO - 옵션 28: '번역대기'
2025-06-23 10:42:57,568 - dropdown_utils4 - INFO - 옵션 29: '등록실행'
2025-06-23 10:42:57,572 - dropdown_utils4 - INFO - 옵션 30: '등록실행'
2025-06-23 10:42:57,577 - dropdown_utils4 - INFO - 옵션 31: '등록A'
2025-06-23 10:42:57,582 - dropdown_utils4 - INFO - 옵션 32: '등록A'
2025-06-23 10:42:57,586 - dropdown_utils4 - INFO - 옵션 33: '등록B'
2025-06-23 10:42:57,591 - dropdown_utils4 - INFO - 옵션 34: '등록B'
2025-06-23 10:42:57,596 - dropdown_utils4 - INFO - 옵션 35: '등록C'
2025-06-23 10:42:57,600 - dropdown_utils4 - INFO - 옵션 36: '등록C'
2025-06-23 10:42:57,605 - dropdown_utils4 - INFO - 옵션 37: ''
2025-06-23 10:42:57,609 - dropdown_utils4 - INFO - 옵션 38: ''
2025-06-23 10:42:57,614 - dropdown_utils4 - INFO - 옵션 39: ''
2025-06-23 10:42:57,618 - dropdown_utils4 - INFO - 옵션 40: ''
2025-06-23 10:42:57,951 - dropdown_utils4 - INFO - 스크롤 후 40개 옵션 확인
2025-06-23 10:42:57,951 - dropdown_utils4 - INFO - 스크롤 15/30
2025-06-23 10:42:57,990 - dropdown_utils4 - INFO - 현재 화면에 40개의 옵션 발견
2025-06-23 10:42:58,003 - dropdown_utils4 - INFO - 옵션 1: ''
2025-06-23 10:42:58,013 - dropdown_utils4 - INFO - 옵션 2: ''
2025-06-23 10:42:58,025 - dropdown_utils4 - INFO - 옵션 3: ''
2025-06-23 10:42:58,030 - dropdown_utils4 - INFO - 옵션 4: ''
2025-06-23 10:42:58,034 - dropdown_utils4 - INFO - 옵션 5: ''
2025-06-23 10:42:58,039 - dropdown_utils4 - INFO - 옵션 6: ''
2025-06-23 10:42:58,044 - dropdown_utils4 - INFO - 옵션 7: ''
2025-06-23 10:42:58,048 - dropdown_utils4 - INFO - 옵션 8: ''
2025-06-23 10:42:58,052 - dropdown_utils4 - INFO - 옵션 9: ''
2025-06-23 10:42:58,056 - dropdown_utils4 - INFO - 옵션 10: ''
2025-06-23 10:42:58,061 - dropdown_utils4 - INFO - 옵션 11: ''
2025-06-23 10:42:58,065 - dropdown_utils4 - INFO - 옵션 12: ''
2025-06-23 10:42:58,069 - dropdown_utils4 - INFO - 옵션 13: ''
2025-06-23 10:42:58,074 - dropdown_utils4 - INFO - 옵션 14: ''
2025-06-23 10:42:58,078 - dropdown_utils4 - INFO - 옵션 15: ''
2025-06-23 10:42:58,082 - dropdown_utils4 - INFO - 옵션 16: ''
2025-06-23 10:42:58,086 - dropdown_utils4 - INFO - 옵션 17: ''
2025-06-23 10:42:58,091 - dropdown_utils4 - INFO - 옵션 18: ''
2025-06-23 10:42:58,096 - dropdown_utils4 - INFO - 옵션 19: ''
2025-06-23 10:42:58,100 - dropdown_utils4 - INFO - 옵션 20: ''
2025-06-23 10:42:58,105 - dropdown_utils4 - INFO - 옵션 21: '전체'
2025-06-23 10:42:58,110 - dropdown_utils4 - INFO - 옵션 22: '전체'
2025-06-23 10:42:58,115 - dropdown_utils4 - INFO - 옵션 23: '그룹 없음'
2025-06-23 10:42:58,119 - dropdown_utils4 - INFO - 옵션 24: '그룹 없음'
2025-06-23 10:42:58,125 - dropdown_utils4 - INFO - 옵션 25: '신규수집'
2025-06-23 10:42:58,129 - dropdown_utils4 - INFO - 옵션 26: '신규수집'
2025-06-23 10:42:58,134 - dropdown_utils4 - INFO - 옵션 27: '번역대기'
2025-06-23 10:42:58,138 - dropdown_utils4 - INFO - 옵션 28: '번역대기'
2025-06-23 10:42:58,143 - dropdown_utils4 - INFO - 옵션 29: '등록실행'
2025-06-23 10:42:58,148 - dropdown_utils4 - INFO - 옵션 30: '등록실행'
2025-06-23 10:42:58,152 - dropdown_utils4 - INFO - 옵션 31: '등록A'
2025-06-23 10:42:58,157 - dropdown_utils4 - INFO - 옵션 32: '등록A'
2025-06-23 10:42:58,162 - dropdown_utils4 - INFO - 옵션 33: '등록B'
2025-06-23 10:42:58,166 - dropdown_utils4 - INFO - 옵션 34: '등록B'
2025-06-23 10:42:58,171 - dropdown_utils4 - INFO - 옵션 35: '등록C'
2025-06-23 10:42:58,176 - dropdown_utils4 - INFO - 옵션 36: '등록C'
2025-06-23 10:42:58,180 - dropdown_utils4 - INFO - 옵션 37: ''
2025-06-23 10:42:58,185 - dropdown_utils4 - INFO - 옵션 38: ''
2025-06-23 10:42:58,190 - dropdown_utils4 - INFO - 옵션 39: ''
2025-06-23 10:42:58,195 - dropdown_utils4 - INFO - 옵션 40: ''
2025-06-23 10:42:58,520 - dropdown_utils4 - INFO - 스크롤 후 40개 옵션 확인
2025-06-23 10:42:58,521 - dropdown_utils4 - INFO - 스크롤 16/30
2025-06-23 10:42:58,528 - dropdown_utils4 - INFO - 현재 화면에 40개의 옵션 발견
2025-06-23 10:42:58,533 - dropdown_utils4 - INFO - 옵션 1: ''
2025-06-23 10:42:58,538 - dropdown_utils4 - INFO - 옵션 2: ''
2025-06-23 10:42:58,543 - dropdown_utils4 - INFO - 옵션 3: ''
2025-06-23 10:42:58,547 - dropdown_utils4 - INFO - 옵션 4: ''
2025-06-23 10:42:58,552 - dropdown_utils4 - INFO - 옵션 5: ''
2025-06-23 10:42:58,557 - dropdown_utils4 - INFO - 옵션 6: ''
2025-06-23 10:42:58,561 - dropdown_utils4 - INFO - 옵션 7: ''
2025-06-23 10:42:58,565 - dropdown_utils4 - INFO - 옵션 8: ''
2025-06-23 10:42:58,569 - dropdown_utils4 - INFO - 옵션 9: ''
2025-06-23 10:42:58,574 - dropdown_utils4 - INFO - 옵션 10: ''
2025-06-23 10:42:58,578 - dropdown_utils4 - INFO - 옵션 11: ''
2025-06-23 10:42:58,582 - dropdown_utils4 - INFO - 옵션 12: ''
2025-06-23 10:42:58,586 - dropdown_utils4 - INFO - 옵션 13: ''
2025-06-23 10:42:58,591 - dropdown_utils4 - INFO - 옵션 14: ''
2025-06-23 10:42:58,595 - dropdown_utils4 - INFO - 옵션 15: ''
2025-06-23 10:42:58,600 - dropdown_utils4 - INFO - 옵션 16: ''
2025-06-23 10:42:58,604 - dropdown_utils4 - INFO - 옵션 17: ''
2025-06-23 10:42:58,609 - dropdown_utils4 - INFO - 옵션 18: ''
2025-06-23 10:42:58,613 - dropdown_utils4 - INFO - 옵션 19: ''
2025-06-23 10:42:58,617 - dropdown_utils4 - INFO - 옵션 20: ''
2025-06-23 10:42:58,622 - dropdown_utils4 - INFO - 옵션 21: '전체'
2025-06-23 10:42:58,626 - dropdown_utils4 - INFO - 옵션 22: '전체'
2025-06-23 10:42:58,631 - dropdown_utils4 - INFO - 옵션 23: '그룹 없음'
2025-06-23 10:42:58,635 - dropdown_utils4 - INFO - 옵션 24: '그룹 없음'
2025-06-23 10:42:58,640 - dropdown_utils4 - INFO - 옵션 25: '신규수집'
2025-06-23 10:42:58,645 - dropdown_utils4 - INFO - 옵션 26: '신규수집'
2025-06-23 10:42:58,649 - dropdown_utils4 - INFO - 옵션 27: '번역대기'
2025-06-23 10:42:58,654 - dropdown_utils4 - INFO - 옵션 28: '번역대기'
2025-06-23 10:42:58,659 - dropdown_utils4 - INFO - 옵션 29: '등록실행'
2025-06-23 10:42:58,663 - dropdown_utils4 - INFO - 옵션 30: '등록실행'
2025-06-23 10:42:58,668 - dropdown_utils4 - INFO - 옵션 31: '등록A'
2025-06-23 10:42:58,672 - dropdown_utils4 - INFO - 옵션 32: '등록A'
2025-06-23 10:42:58,677 - dropdown_utils4 - INFO - 옵션 33: '등록B'
2025-06-23 10:42:58,681 - dropdown_utils4 - INFO - 옵션 34: '등록B'
2025-06-23 10:42:58,686 - dropdown_utils4 - INFO - 옵션 35: '등록C'
2025-06-23 10:42:58,691 - dropdown_utils4 - INFO - 옵션 36: '등록C'
2025-06-23 10:42:58,696 - dropdown_utils4 - INFO - 옵션 37: ''
2025-06-23 10:42:58,700 - dropdown_utils4 - INFO - 옵션 38: ''
2025-06-23 10:42:58,705 - dropdown_utils4 - INFO - 옵션 39: ''
2025-06-23 10:42:58,710 - dropdown_utils4 - INFO - 옵션 40: ''
2025-06-23 10:42:59,036 - dropdown_utils4 - INFO - 스크롤 후 40개 옵션 확인
2025-06-23 10:42:59,036 - dropdown_utils4 - INFO - 스크롤 17/30
2025-06-23 10:42:59,044 - dropdown_utils4 - INFO - 현재 화면에 40개의 옵션 발견
2025-06-23 10:42:59,049 - dropdown_utils4 - INFO - 옵션 1: ''
2025-06-23 10:42:59,053 - dropdown_utils4 - INFO - 옵션 2: ''
2025-06-23 10:42:59,058 - dropdown_utils4 - INFO - 옵션 3: ''
2025-06-23 10:42:59,063 - dropdown_utils4 - INFO - 옵션 4: ''
2025-06-23 10:42:59,068 - dropdown_utils4 - INFO - 옵션 5: ''
2025-06-23 10:42:59,072 - dropdown_utils4 - INFO - 옵션 6: ''
2025-06-23 10:42:59,077 - dropdown_utils4 - INFO - 옵션 7: ''
2025-06-23 10:42:59,081 - dropdown_utils4 - INFO - 옵션 8: ''
2025-06-23 10:42:59,085 - dropdown_utils4 - INFO - 옵션 9: ''
2025-06-23 10:42:59,090 - dropdown_utils4 - INFO - 옵션 10: ''
2025-06-23 10:42:59,094 - dropdown_utils4 - INFO - 옵션 11: ''
2025-06-23 10:42:59,098 - dropdown_utils4 - INFO - 옵션 12: ''
2025-06-23 10:42:59,102 - dropdown_utils4 - INFO - 옵션 13: ''
2025-06-23 10:42:59,107 - dropdown_utils4 - INFO - 옵션 14: ''
2025-06-23 10:42:59,111 - dropdown_utils4 - INFO - 옵션 15: ''
2025-06-23 10:42:59,116 - dropdown_utils4 - INFO - 옵션 16: ''
2025-06-23 10:42:59,120 - dropdown_utils4 - INFO - 옵션 17: ''
2025-06-23 10:42:59,124 - dropdown_utils4 - INFO - 옵션 18: ''
2025-06-23 10:42:59,129 - dropdown_utils4 - INFO - 옵션 19: ''
2025-06-23 10:42:59,133 - dropdown_utils4 - INFO - 옵션 20: ''
2025-06-23 10:42:59,138 - dropdown_utils4 - INFO - 옵션 21: '전체'
2025-06-23 10:42:59,143 - dropdown_utils4 - INFO - 옵션 22: '전체'
2025-06-23 10:42:59,147 - dropdown_utils4 - INFO - 옵션 23: '그룹 없음'
2025-06-23 10:42:59,151 - dropdown_utils4 - INFO - 옵션 24: '그룹 없음'
2025-06-23 10:42:59,156 - dropdown_utils4 - INFO - 옵션 25: '신규수집'
2025-06-23 10:42:59,161 - dropdown_utils4 - INFO - 옵션 26: '신규수집'
2025-06-23 10:42:59,165 - dropdown_utils4 - INFO - 옵션 27: '번역대기'
2025-06-23 10:42:59,170 - dropdown_utils4 - INFO - 옵션 28: '번역대기'
2025-06-23 10:42:59,175 - dropdown_utils4 - INFO - 옵션 29: '등록실행'
2025-06-23 10:42:59,179 - dropdown_utils4 - INFO - 옵션 30: '등록실행'
2025-06-23 10:42:59,184 - dropdown_utils4 - INFO - 옵션 31: '등록A'
2025-06-23 10:42:59,188 - dropdown_utils4 - INFO - 옵션 32: '등록A'
2025-06-23 10:42:59,193 - dropdown_utils4 - INFO - 옵션 33: '등록B'
2025-06-23 10:42:59,197 - dropdown_utils4 - INFO - 옵션 34: '등록B'
2025-06-23 10:42:59,202 - dropdown_utils4 - INFO - 옵션 35: '등록C'
2025-06-23 10:42:59,206 - dropdown_utils4 - INFO - 옵션 36: '등록C'
2025-06-23 10:42:59,211 - dropdown_utils4 - INFO - 옵션 37: ''
2025-06-23 10:42:59,215 - dropdown_utils4 - INFO - 옵션 38: ''
2025-06-23 10:42:59,220 - dropdown_utils4 - INFO - 옵션 39: ''
2025-06-23 10:42:59,225 - dropdown_utils4 - INFO - 옵션 40: ''
2025-06-23 10:42:59,537 - dropdown_utils4 - INFO - 스크롤 후 40개 옵션 확인
2025-06-23 10:42:59,537 - dropdown_utils4 - INFO - 스크롤 18/30
2025-06-23 10:42:59,546 - dropdown_utils4 - INFO - 현재 화면에 40개의 옵션 발견
2025-06-23 10:42:59,551 - dropdown_utils4 - INFO - 옵션 1: ''
2025-06-23 10:42:59,556 - dropdown_utils4 - INFO - 옵션 2: ''
2025-06-23 10:42:59,561 - dropdown_utils4 - INFO - 옵션 3: ''
2025-06-23 10:42:59,565 - dropdown_utils4 - INFO - 옵션 4: ''
2025-06-23 10:42:59,570 - dropdown_utils4 - INFO - 옵션 5: ''
2025-06-23 10:42:59,575 - dropdown_utils4 - INFO - 옵션 6: ''
2025-06-23 10:42:59,580 - dropdown_utils4 - INFO - 옵션 7: ''
2025-06-23 10:42:59,585 - dropdown_utils4 - INFO - 옵션 8: ''
2025-06-23 10:42:59,590 - dropdown_utils4 - INFO - 옵션 9: ''
2025-06-23 10:42:59,596 - dropdown_utils4 - INFO - 옵션 10: ''
2025-06-23 10:42:59,601 - dropdown_utils4 - INFO - 옵션 11: ''
2025-06-23 10:42:59,606 - dropdown_utils4 - INFO - 옵션 12: ''
2025-06-23 10:42:59,612 - dropdown_utils4 - INFO - 옵션 13: ''
2025-06-23 10:42:59,616 - dropdown_utils4 - INFO - 옵션 14: ''
2025-06-23 10:42:59,622 - dropdown_utils4 - INFO - 옵션 15: ''
2025-06-23 10:42:59,628 - dropdown_utils4 - INFO - 옵션 16: ''
2025-06-23 10:42:59,632 - dropdown_utils4 - INFO - 옵션 17: ''
2025-06-23 10:42:59,637 - dropdown_utils4 - INFO - 옵션 18: ''
2025-06-23 10:42:59,643 - dropdown_utils4 - INFO - 옵션 19: ''
2025-06-23 10:42:59,647 - dropdown_utils4 - INFO - 옵션 20: ''
2025-06-23 10:42:59,652 - dropdown_utils4 - INFO - 옵션 21: '전체'
2025-06-23 10:42:59,658 - dropdown_utils4 - INFO - 옵션 22: '전체'
2025-06-23 10:42:59,663 - dropdown_utils4 - INFO - 옵션 23: '그룹 없음'
2025-06-23 10:42:59,668 - dropdown_utils4 - INFO - 옵션 24: '그룹 없음'
2025-06-23 10:42:59,673 - dropdown_utils4 - INFO - 옵션 25: '신규수집'
2025-06-23 10:42:59,678 - dropdown_utils4 - INFO - 옵션 26: '신규수집'
2025-06-23 10:42:59,683 - dropdown_utils4 - INFO - 옵션 27: '번역대기'
2025-06-23 10:42:59,688 - dropdown_utils4 - INFO - 옵션 28: '번역대기'
2025-06-23 10:42:59,695 - dropdown_utils4 - INFO - 옵션 29: '등록실행'
2025-06-23 10:42:59,699 - dropdown_utils4 - INFO - 옵션 30: '등록실행'
2025-06-23 10:42:59,705 - dropdown_utils4 - INFO - 옵션 31: '등록A'
2025-06-23 10:42:59,710 - dropdown_utils4 - INFO - 옵션 32: '등록A'
2025-06-23 10:42:59,714 - dropdown_utils4 - INFO - 옵션 33: '등록B'
2025-06-23 10:42:59,719 - dropdown_utils4 - INFO - 옵션 34: '등록B'
2025-06-23 10:42:59,725 - dropdown_utils4 - INFO - 옵션 35: '등록C'
2025-06-23 10:42:59,729 - dropdown_utils4 - INFO - 옵션 36: '등록C'
2025-06-23 10:42:59,734 - dropdown_utils4 - INFO - 옵션 37: ''
2025-06-23 10:42:59,739 - dropdown_utils4 - INFO - 옵션 38: ''
2025-06-23 10:42:59,744 - dropdown_utils4 - INFO - 옵션 39: ''
2025-06-23 10:42:59,749 - dropdown_utils4 - INFO - 옵션 40: ''
2025-06-23 10:43:00,060 - dropdown_utils4 - INFO - 스크롤 후 40개 옵션 확인
2025-06-23 10:43:00,061 - dropdown_utils4 - INFO - 스크롤 19/30
2025-06-23 10:43:00,070 - dropdown_utils4 - INFO - 현재 화면에 40개의 옵션 발견
2025-06-23 10:43:00,076 - dropdown_utils4 - INFO - 옵션 1: ''
2025-06-23 10:43:00,080 - dropdown_utils4 - INFO - 옵션 2: ''
2025-06-23 10:43:00,085 - dropdown_utils4 - INFO - 옵션 3: ''
2025-06-23 10:43:00,090 - dropdown_utils4 - INFO - 옵션 4: ''
2025-06-23 10:43:00,094 - dropdown_utils4 - INFO - 옵션 5: ''
2025-06-23 10:43:00,099 - dropdown_utils4 - INFO - 옵션 6: ''
2025-06-23 10:43:00,104 - dropdown_utils4 - INFO - 옵션 7: ''
2025-06-23 10:43:00,108 - dropdown_utils4 - INFO - 옵션 8: ''
2025-06-23 10:43:00,113 - dropdown_utils4 - INFO - 옵션 9: ''
2025-06-23 10:43:00,117 - dropdown_utils4 - INFO - 옵션 10: ''
2025-06-23 10:43:00,123 - dropdown_utils4 - INFO - 옵션 11: ''
2025-06-23 10:43:00,127 - dropdown_utils4 - INFO - 옵션 12: ''
2025-06-23 10:43:00,132 - dropdown_utils4 - INFO - 옵션 13: ''
2025-06-23 10:43:00,137 - dropdown_utils4 - INFO - 옵션 14: ''
2025-06-23 10:43:00,142 - dropdown_utils4 - INFO - 옵션 15: ''
2025-06-23 10:43:00,147 - dropdown_utils4 - INFO - 옵션 16: ''
2025-06-23 10:43:00,152 - dropdown_utils4 - INFO - 옵션 17: ''
2025-06-23 10:43:00,158 - dropdown_utils4 - INFO - 옵션 18: ''
2025-06-23 10:43:00,163 - dropdown_utils4 - INFO - 옵션 19: ''
2025-06-23 10:43:00,168 - dropdown_utils4 - INFO - 옵션 20: ''
2025-06-23 10:43:00,174 - dropdown_utils4 - INFO - 옵션 21: '전체'
2025-06-23 10:43:00,179 - dropdown_utils4 - INFO - 옵션 22: '전체'
2025-06-23 10:43:00,184 - dropdown_utils4 - INFO - 옵션 23: '그룹 없음'
2025-06-23 10:43:00,190 - dropdown_utils4 - INFO - 옵션 24: '그룹 없음'
2025-06-23 10:43:00,195 - dropdown_utils4 - INFO - 옵션 25: '신규수집'
2025-06-23 10:43:00,201 - dropdown_utils4 - INFO - 옵션 26: '신규수집'
2025-06-23 10:43:00,207 - dropdown_utils4 - INFO - 옵션 27: '번역대기'
2025-06-23 10:43:00,211 - dropdown_utils4 - INFO - 옵션 28: '번역대기'
2025-06-23 10:43:00,216 - dropdown_utils4 - INFO - 옵션 29: '등록실행'
2025-06-23 10:43:00,222 - dropdown_utils4 - INFO - 옵션 30: '등록실행'
2025-06-23 10:43:00,227 - dropdown_utils4 - INFO - 옵션 31: '등록A'
2025-06-23 10:43:00,231 - dropdown_utils4 - INFO - 옵션 32: '등록A'
2025-06-23 10:43:00,237 - dropdown_utils4 - INFO - 옵션 33: '등록B'
2025-06-23 10:43:00,243 - dropdown_utils4 - INFO - 옵션 34: '등록B'
2025-06-23 10:43:00,248 - dropdown_utils4 - INFO - 옵션 35: '등록C'
2025-06-23 10:43:00,253 - dropdown_utils4 - INFO - 옵션 36: '등록C'
2025-06-23 10:43:00,259 - dropdown_utils4 - INFO - 옵션 37: ''
2025-06-23 10:43:00,264 - dropdown_utils4 - INFO - 옵션 38: ''
2025-06-23 10:43:00,270 - dropdown_utils4 - INFO - 옵션 39: ''
2025-06-23 10:43:00,276 - dropdown_utils4 - INFO - 옵션 40: ''
2025-06-23 10:43:00,604 - dropdown_utils4 - INFO - 스크롤 후 40개 옵션 확인
2025-06-23 10:43:00,604 - dropdown_utils4 - INFO - 스크롤 20/30
2025-06-23 10:43:00,612 - dropdown_utils4 - INFO - 현재 화면에 40개의 옵션 발견
2025-06-23 10:43:00,618 - dropdown_utils4 - INFO - 옵션 1: ''
2025-06-23 10:43:00,624 - dropdown_utils4 - INFO - 옵션 2: ''
2025-06-23 10:43:00,629 - dropdown_utils4 - INFO - 옵션 3: ''
2025-06-23 10:43:00,633 - dropdown_utils4 - INFO - 옵션 4: ''
2025-06-23 10:43:00,638 - dropdown_utils4 - INFO - 옵션 5: ''
2025-06-23 10:43:00,642 - dropdown_utils4 - INFO - 옵션 6: ''
2025-06-23 10:43:00,647 - dropdown_utils4 - INFO - 옵션 7: ''
2025-06-23 10:43:00,651 - dropdown_utils4 - INFO - 옵션 8: ''
2025-06-23 10:43:00,655 - dropdown_utils4 - INFO - 옵션 9: ''
2025-06-23 10:43:00,660 - dropdown_utils4 - INFO - 옵션 10: ''
2025-06-23 10:43:00,664 - dropdown_utils4 - INFO - 옵션 11: ''
2025-06-23 10:43:00,668 - dropdown_utils4 - INFO - 옵션 12: ''
2025-06-23 10:43:00,673 - dropdown_utils4 - INFO - 옵션 13: ''
2025-06-23 10:43:00,677 - dropdown_utils4 - INFO - 옵션 14: ''
2025-06-23 10:43:00,682 - dropdown_utils4 - INFO - 옵션 15: ''
2025-06-23 10:43:00,686 - dropdown_utils4 - INFO - 옵션 16: ''
2025-06-23 10:43:00,691 - dropdown_utils4 - INFO - 옵션 17: ''
2025-06-23 10:43:00,696 - dropdown_utils4 - INFO - 옵션 18: ''
2025-06-23 10:43:00,700 - dropdown_utils4 - INFO - 옵션 19: ''
2025-06-23 10:43:00,705 - dropdown_utils4 - INFO - 옵션 20: ''
2025-06-23 10:43:00,710 - dropdown_utils4 - INFO - 옵션 21: '전체'
2025-06-23 10:43:00,714 - dropdown_utils4 - INFO - 옵션 22: '전체'
2025-06-23 10:43:00,719 - dropdown_utils4 - INFO - 옵션 23: '그룹 없음'
2025-06-23 10:43:00,724 - dropdown_utils4 - INFO - 옵션 24: '그룹 없음'
2025-06-23 10:43:00,729 - dropdown_utils4 - INFO - 옵션 25: '신규수집'
2025-06-23 10:43:00,733 - dropdown_utils4 - INFO - 옵션 26: '신규수집'
2025-06-23 10:43:00,738 - dropdown_utils4 - INFO - 옵션 27: '번역대기'
2025-06-23 10:43:00,743 - dropdown_utils4 - INFO - 옵션 28: '번역대기'
2025-06-23 10:43:00,747 - dropdown_utils4 - INFO - 옵션 29: '등록실행'
2025-06-23 10:43:00,752 - dropdown_utils4 - INFO - 옵션 30: '등록실행'
2025-06-23 10:43:00,757 - dropdown_utils4 - INFO - 옵션 31: '등록A'
2025-06-23 10:43:00,762 - dropdown_utils4 - INFO - 옵션 32: '등록A'
2025-06-23 10:43:00,766 - dropdown_utils4 - INFO - 옵션 33: '등록B'
2025-06-23 10:43:00,771 - dropdown_utils4 - INFO - 옵션 34: '등록B'
2025-06-23 10:43:00,776 - dropdown_utils4 - INFO - 옵션 35: '등록C'
2025-06-23 10:43:00,780 - dropdown_utils4 - INFO - 옵션 36: '등록C'
2025-06-23 10:43:00,784 - dropdown_utils4 - INFO - 옵션 37: ''
2025-06-23 10:43:00,789 - dropdown_utils4 - INFO - 옵션 38: ''
2025-06-23 10:43:00,794 - dropdown_utils4 - INFO - 옵션 39: ''
2025-06-23 10:43:00,798 - dropdown_utils4 - INFO - 옵션 40: ''
2025-06-23 10:43:01,110 - dropdown_utils4 - INFO - 스크롤 후 40개 옵션 확인
2025-06-23 10:43:01,111 - dropdown_utils4 - INFO - 스크롤 21/30
2025-06-23 10:43:01,119 - dropdown_utils4 - INFO - 현재 화면에 40개의 옵션 발견
2025-06-23 10:43:01,125 - dropdown_utils4 - INFO - 옵션 1: ''
2025-06-23 10:43:01,130 - dropdown_utils4 - INFO - 옵션 2: ''
2025-06-23 10:43:01,135 - dropdown_utils4 - INFO - 옵션 3: ''
2025-06-23 10:43:01,139 - dropdown_utils4 - INFO - 옵션 4: ''
2025-06-23 10:43:01,144 - dropdown_utils4 - INFO - 옵션 5: ''
2025-06-23 10:43:01,148 - dropdown_utils4 - INFO - 옵션 6: ''
2025-06-23 10:43:01,153 - dropdown_utils4 - INFO - 옵션 7: ''
2025-06-23 10:43:01,157 - dropdown_utils4 - INFO - 옵션 8: ''
2025-06-23 10:43:01,162 - dropdown_utils4 - INFO - 옵션 9: ''
2025-06-23 10:43:01,166 - dropdown_utils4 - INFO - 옵션 10: ''
2025-06-23 10:43:01,170 - dropdown_utils4 - INFO - 옵션 11: ''
2025-06-23 10:43:01,175 - dropdown_utils4 - INFO - 옵션 12: ''
2025-06-23 10:43:01,179 - dropdown_utils4 - INFO - 옵션 13: ''
2025-06-23 10:43:01,183 - dropdown_utils4 - INFO - 옵션 14: ''
2025-06-23 10:43:01,187 - dropdown_utils4 - INFO - 옵션 15: ''
2025-06-23 10:43:01,192 - dropdown_utils4 - INFO - 옵션 16: ''
2025-06-23 10:43:01,196 - dropdown_utils4 - INFO - 옵션 17: ''
2025-06-23 10:43:01,200 - dropdown_utils4 - INFO - 옵션 18: ''
2025-06-23 10:43:01,205 - dropdown_utils4 - INFO - 옵션 19: ''
2025-06-23 10:43:01,209 - dropdown_utils4 - INFO - 옵션 20: ''
2025-06-23 10:43:01,214 - dropdown_utils4 - INFO - 옵션 21: '전체'
2025-06-23 10:43:01,218 - dropdown_utils4 - INFO - 옵션 22: '전체'
2025-06-23 10:43:01,223 - dropdown_utils4 - INFO - 옵션 23: '그룹 없음'
2025-06-23 10:43:01,228 - dropdown_utils4 - INFO - 옵션 24: '그룹 없음'
2025-06-23 10:43:01,232 - dropdown_utils4 - INFO - 옵션 25: '신규수집'
2025-06-23 10:43:01,237 - dropdown_utils4 - INFO - 옵션 26: '신규수집'
2025-06-23 10:43:01,242 - dropdown_utils4 - INFO - 옵션 27: '번역대기'
2025-06-23 10:43:01,246 - dropdown_utils4 - INFO - 옵션 28: '번역대기'
2025-06-23 10:43:01,250 - dropdown_utils4 - INFO - 옵션 29: '등록실행'
2025-06-23 10:43:01,255 - dropdown_utils4 - INFO - 옵션 30: '등록실행'
2025-06-23 10:43:01,260 - dropdown_utils4 - INFO - 옵션 31: '등록A'
2025-06-23 10:43:01,264 - dropdown_utils4 - INFO - 옵션 32: '등록A'
2025-06-23 10:43:01,268 - dropdown_utils4 - INFO - 옵션 33: '등록B'
2025-06-23 10:43:01,273 - dropdown_utils4 - INFO - 옵션 34: '등록B'
2025-06-23 10:43:01,278 - dropdown_utils4 - INFO - 옵션 35: '등록C'
2025-06-23 10:43:01,282 - dropdown_utils4 - INFO - 옵션 36: '등록C'
2025-06-23 10:43:01,287 - dropdown_utils4 - INFO - 옵션 37: ''
2025-06-23 10:43:01,291 - dropdown_utils4 - INFO - 옵션 38: ''
2025-06-23 10:43:01,296 - dropdown_utils4 - INFO - 옵션 39: ''
2025-06-23 10:43:01,300 - dropdown_utils4 - INFO - 옵션 40: ''
2025-06-23 10:43:01,627 - dropdown_utils4 - INFO - 스크롤 후 40개 옵션 확인
2025-06-23 10:43:01,627 - dropdown_utils4 - INFO - 스크롤 22/30
2025-06-23 10:43:01,635 - dropdown_utils4 - INFO - 현재 화면에 40개의 옵션 발견
2025-06-23 10:43:01,642 - dropdown_utils4 - INFO - 옵션 1: ''
2025-06-23 10:43:01,647 - dropdown_utils4 - INFO - 옵션 2: ''
2025-06-23 10:43:01,651 - dropdown_utils4 - INFO - 옵션 3: ''
2025-06-23 10:43:01,656 - dropdown_utils4 - INFO - 옵션 4: ''
2025-06-23 10:43:01,661 - dropdown_utils4 - INFO - 옵션 5: ''
2025-06-23 10:43:01,665 - dropdown_utils4 - INFO - 옵션 6: ''
2025-06-23 10:43:01,669 - dropdown_utils4 - INFO - 옵션 7: ''
2025-06-23 10:43:01,673 - dropdown_utils4 - INFO - 옵션 8: ''
2025-06-23 10:43:01,678 - dropdown_utils4 - INFO - 옵션 9: ''
2025-06-23 10:43:01,682 - dropdown_utils4 - INFO - 옵션 10: ''
2025-06-23 10:43:01,687 - dropdown_utils4 - INFO - 옵션 11: ''
2025-06-23 10:43:01,691 - dropdown_utils4 - INFO - 옵션 12: ''
2025-06-23 10:43:01,696 - dropdown_utils4 - INFO - 옵션 13: ''
2025-06-23 10:43:01,700 - dropdown_utils4 - INFO - 옵션 14: ''
2025-06-23 10:43:01,704 - dropdown_utils4 - INFO - 옵션 15: ''
2025-06-23 10:43:01,708 - dropdown_utils4 - INFO - 옵션 16: ''
2025-06-23 10:43:01,713 - dropdown_utils4 - INFO - 옵션 17: ''
2025-06-23 10:43:01,717 - dropdown_utils4 - INFO - 옵션 18: ''
2025-06-23 10:43:01,721 - dropdown_utils4 - INFO - 옵션 19: ''
2025-06-23 10:43:01,726 - dropdown_utils4 - INFO - 옵션 20: ''
2025-06-23 10:43:01,730 - dropdown_utils4 - INFO - 옵션 21: '전체'
2025-06-23 10:43:01,735 - dropdown_utils4 - INFO - 옵션 22: '전체'
2025-06-23 10:43:01,740 - dropdown_utils4 - INFO - 옵션 23: '그룹 없음'
2025-06-23 10:43:01,744 - dropdown_utils4 - INFO - 옵션 24: '그룹 없음'
2025-06-23 10:43:01,748 - dropdown_utils4 - INFO - 옵션 25: '신규수집'
2025-06-23 10:43:01,753 - dropdown_utils4 - INFO - 옵션 26: '신규수집'
2025-06-23 10:43:01,758 - dropdown_utils4 - INFO - 옵션 27: '번역대기'
2025-06-23 10:43:01,762 - dropdown_utils4 - INFO - 옵션 28: '번역대기'
2025-06-23 10:43:01,767 - dropdown_utils4 - INFO - 옵션 29: '등록실행'
2025-06-23 10:43:01,772 - dropdown_utils4 - INFO - 옵션 30: '등록실행'
2025-06-23 10:43:01,777 - dropdown_utils4 - INFO - 옵션 31: '등록A'
2025-06-23 10:43:01,782 - dropdown_utils4 - INFO - 옵션 32: '등록A'
2025-06-23 10:43:01,788 - dropdown_utils4 - INFO - 옵션 33: '등록B'
2025-06-23 10:43:01,793 - dropdown_utils4 - INFO - 옵션 34: '등록B'
2025-06-23 10:43:01,799 - dropdown_utils4 - INFO - 옵션 35: '등록C'
2025-06-23 10:43:01,804 - dropdown_utils4 - INFO - 옵션 36: '등록C'
2025-06-23 10:43:01,810 - dropdown_utils4 - INFO - 옵션 37: ''
2025-06-23 10:43:01,816 - dropdown_utils4 - INFO - 옵션 38: ''
2025-06-23 10:43:01,821 - dropdown_utils4 - INFO - 옵션 39: ''
2025-06-23 10:43:01,826 - dropdown_utils4 - INFO - 옵션 40: ''
2025-06-23 10:43:02,153 - dropdown_utils4 - INFO - 스크롤 후 40개 옵션 확인
2025-06-23 10:43:02,153 - dropdown_utils4 - INFO - 스크롤 23/30
2025-06-23 10:43:02,164 - dropdown_utils4 - INFO - 현재 화면에 40개의 옵션 발견
2025-06-23 10:43:02,170 - dropdown_utils4 - INFO - 옵션 1: ''
2025-06-23 10:43:02,178 - dropdown_utils4 - INFO - 옵션 2: ''
2025-06-23 10:43:02,190 - dropdown_utils4 - INFO - 옵션 3: ''
2025-06-23 10:43:02,197 - dropdown_utils4 - INFO - 옵션 4: ''
2025-06-23 10:43:02,203 - dropdown_utils4 - INFO - 옵션 5: ''
2025-06-23 10:43:02,208 - dropdown_utils4 - INFO - 옵션 6: ''
2025-06-23 10:43:02,213 - dropdown_utils4 - INFO - 옵션 7: ''
2025-06-23 10:43:02,218 - dropdown_utils4 - INFO - 옵션 8: ''
2025-06-23 10:43:02,223 - dropdown_utils4 - INFO - 옵션 9: ''
2025-06-23 10:43:02,227 - dropdown_utils4 - INFO - 옵션 10: ''
2025-06-23 10:43:02,231 - dropdown_utils4 - INFO - 옵션 11: ''
2025-06-23 10:43:02,235 - dropdown_utils4 - INFO - 옵션 12: ''
2025-06-23 10:43:02,240 - dropdown_utils4 - INFO - 옵션 13: ''
2025-06-23 10:43:02,244 - dropdown_utils4 - INFO - 옵션 14: ''
2025-06-23 10:43:02,249 - dropdown_utils4 - INFO - 옵션 15: ''
2025-06-23 10:43:02,253 - dropdown_utils4 - INFO - 옵션 16: ''
2025-06-23 10:43:02,258 - dropdown_utils4 - INFO - 옵션 17: ''
2025-06-23 10:43:02,262 - dropdown_utils4 - INFO - 옵션 18: ''
2025-06-23 10:43:02,266 - dropdown_utils4 - INFO - 옵션 19: ''
2025-06-23 10:43:02,271 - dropdown_utils4 - INFO - 옵션 20: ''
2025-06-23 10:43:02,275 - dropdown_utils4 - INFO - 옵션 21: '전체'
2025-06-23 10:43:02,280 - dropdown_utils4 - INFO - 옵션 22: '전체'
2025-06-23 10:43:02,284 - dropdown_utils4 - INFO - 옵션 23: '그룹 없음'
2025-06-23 10:43:02,289 - dropdown_utils4 - INFO - 옵션 24: '그룹 없음'
2025-06-23 10:43:02,294 - dropdown_utils4 - INFO - 옵션 25: '신규수집'
2025-06-23 10:43:02,298 - dropdown_utils4 - INFO - 옵션 26: '신규수집'
2025-06-23 10:43:02,303 - dropdown_utils4 - INFO - 옵션 27: '번역대기'
2025-06-23 10:43:02,308 - dropdown_utils4 - INFO - 옵션 28: '번역대기'
2025-06-23 10:43:02,312 - dropdown_utils4 - INFO - 옵션 29: '등록실행'
2025-06-23 10:43:02,317 - dropdown_utils4 - INFO - 옵션 30: '등록실행'
2025-06-23 10:43:02,322 - dropdown_utils4 - INFO - 옵션 31: '등록A'
2025-06-23 10:43:02,327 - dropdown_utils4 - INFO - 옵션 32: '등록A'
2025-06-23 10:43:02,331 - dropdown_utils4 - INFO - 옵션 33: '등록B'
2025-06-23 10:43:02,335 - dropdown_utils4 - INFO - 옵션 34: '등록B'
2025-06-23 10:43:02,340 - dropdown_utils4 - INFO - 옵션 35: '등록C'
2025-06-23 10:43:02,345 - dropdown_utils4 - INFO - 옵션 36: '등록C'
2025-06-23 10:43:02,349 - dropdown_utils4 - INFO - 옵션 37: ''
2025-06-23 10:43:02,354 - dropdown_utils4 - INFO - 옵션 38: ''
2025-06-23 10:43:02,359 - dropdown_utils4 - INFO - 옵션 39: ''
2025-06-23 10:43:02,363 - dropdown_utils4 - INFO - 옵션 40: ''
2025-06-23 10:43:02,675 - dropdown_utils4 - INFO - 스크롤 후 40개 옵션 확인
2025-06-23 10:43:02,675 - dropdown_utils4 - INFO - 스크롤 24/30
2025-06-23 10:43:02,682 - dropdown_utils4 - INFO - 현재 화면에 40개의 옵션 발견
2025-06-23 10:43:02,688 - dropdown_utils4 - INFO - 옵션 1: ''
2025-06-23 10:43:02,694 - dropdown_utils4 - INFO - 옵션 2: ''
2025-06-23 10:43:02,699 - dropdown_utils4 - INFO - 옵션 3: ''
2025-06-23 10:43:02,704 - dropdown_utils4 - INFO - 옵션 4: ''
2025-06-23 10:43:02,710 - dropdown_utils4 - INFO - 옵션 5: ''
2025-06-23 10:43:02,715 - dropdown_utils4 - INFO - 옵션 6: ''
2025-06-23 10:43:02,720 - dropdown_utils4 - INFO - 옵션 7: ''
2025-06-23 10:43:02,725 - dropdown_utils4 - INFO - 옵션 8: ''
2025-06-23 10:43:02,731 - dropdown_utils4 - INFO - 옵션 9: ''
2025-06-23 10:43:02,736 - dropdown_utils4 - INFO - 옵션 10: ''
2025-06-23 10:43:02,741 - dropdown_utils4 - INFO - 옵션 11: ''
2025-06-23 10:43:02,746 - dropdown_utils4 - INFO - 옵션 12: ''
2025-06-23 10:43:02,751 - dropdown_utils4 - INFO - 옵션 13: ''
2025-06-23 10:43:02,756 - dropdown_utils4 - INFO - 옵션 14: ''
2025-06-23 10:43:02,760 - dropdown_utils4 - INFO - 옵션 15: ''
2025-06-23 10:43:02,765 - dropdown_utils4 - INFO - 옵션 16: ''
2025-06-23 10:43:02,769 - dropdown_utils4 - INFO - 옵션 17: ''
2025-06-23 10:43:02,774 - dropdown_utils4 - INFO - 옵션 18: ''
2025-06-23 10:43:02,780 - dropdown_utils4 - INFO - 옵션 19: ''
2025-06-23 10:43:02,784 - dropdown_utils4 - INFO - 옵션 20: ''
2025-06-23 10:43:02,790 - dropdown_utils4 - INFO - 옵션 21: '전체'
2025-06-23 10:43:02,795 - dropdown_utils4 - INFO - 옵션 22: '전체'
2025-06-23 10:43:02,799 - dropdown_utils4 - INFO - 옵션 23: '그룹 없음'
2025-06-23 10:43:02,805 - dropdown_utils4 - INFO - 옵션 24: '그룹 없음'
2025-06-23 10:43:02,810 - dropdown_utils4 - INFO - 옵션 25: '신규수집'
2025-06-23 10:43:02,815 - dropdown_utils4 - INFO - 옵션 26: '신규수집'
2025-06-23 10:43:02,821 - dropdown_utils4 - INFO - 옵션 27: '번역대기'
2025-06-23 10:43:02,826 - dropdown_utils4 - INFO - 옵션 28: '번역대기'
2025-06-23 10:43:02,831 - dropdown_utils4 - INFO - 옵션 29: '등록실행'
2025-06-23 10:43:02,836 - dropdown_utils4 - INFO - 옵션 30: '등록실행'
2025-06-23 10:43:02,841 - dropdown_utils4 - INFO - 옵션 31: '등록A'
2025-06-23 10:43:02,846 - dropdown_utils4 - INFO - 옵션 32: '등록A'
2025-06-23 10:43:02,851 - dropdown_utils4 - INFO - 옵션 33: '등록B'
2025-06-23 10:43:02,857 - dropdown_utils4 - INFO - 옵션 34: '등록B'
2025-06-23 10:43:02,862 - dropdown_utils4 - INFO - 옵션 35: '등록C'
2025-06-23 10:43:02,867 - dropdown_utils4 - INFO - 옵션 36: '등록C'
2025-06-23 10:43:02,872 - dropdown_utils4 - INFO - 옵션 37: ''
2025-06-23 10:43:02,877 - dropdown_utils4 - INFO - 옵션 38: ''
2025-06-23 10:43:02,882 - dropdown_utils4 - INFO - 옵션 39: ''
2025-06-23 10:43:02,887 - dropdown_utils4 - INFO - 옵션 40: ''
2025-06-23 10:43:03,199 - dropdown_utils4 - INFO - 스크롤 후 40개 옵션 확인
2025-06-23 10:43:03,199 - dropdown_utils4 - INFO - 스크롤 25/30
2025-06-23 10:43:03,207 - dropdown_utils4 - INFO - 현재 화면에 40개의 옵션 발견
2025-06-23 10:43:03,213 - dropdown_utils4 - INFO - 옵션 1: ''
2025-06-23 10:43:03,217 - dropdown_utils4 - INFO - 옵션 2: ''
2025-06-23 10:43:03,222 - dropdown_utils4 - INFO - 옵션 3: ''
2025-06-23 10:43:03,227 - dropdown_utils4 - INFO - 옵션 4: ''
2025-06-23 10:43:03,232 - dropdown_utils4 - INFO - 옵션 5: ''
2025-06-23 10:43:03,237 - dropdown_utils4 - INFO - 옵션 6: ''
2025-06-23 10:43:03,243 - dropdown_utils4 - INFO - 옵션 7: ''
2025-06-23 10:43:03,248 - dropdown_utils4 - INFO - 옵션 8: ''
2025-06-23 10:43:03,252 - dropdown_utils4 - INFO - 옵션 9: ''
2025-06-23 10:43:03,257 - dropdown_utils4 - INFO - 옵션 10: ''
2025-06-23 10:43:03,262 - dropdown_utils4 - INFO - 옵션 11: ''
2025-06-23 10:43:03,266 - dropdown_utils4 - INFO - 옵션 12: ''
2025-06-23 10:43:03,271 - dropdown_utils4 - INFO - 옵션 13: ''
2025-06-23 10:43:03,276 - dropdown_utils4 - INFO - 옵션 14: ''
2025-06-23 10:43:03,281 - dropdown_utils4 - INFO - 옵션 15: ''
2025-06-23 10:43:03,285 - dropdown_utils4 - INFO - 옵션 16: ''
2025-06-23 10:43:03,290 - dropdown_utils4 - INFO - 옵션 17: ''
2025-06-23 10:43:03,295 - dropdown_utils4 - INFO - 옵션 18: ''
2025-06-23 10:43:03,299 - dropdown_utils4 - INFO - 옵션 19: ''
2025-06-23 10:43:03,304 - dropdown_utils4 - INFO - 옵션 20: ''
2025-06-23 10:43:03,310 - dropdown_utils4 - INFO - 옵션 21: '전체'
2025-06-23 10:43:03,315 - dropdown_utils4 - INFO - 옵션 22: '전체'
2025-06-23 10:43:03,320 - dropdown_utils4 - INFO - 옵션 23: '그룹 없음'
2025-06-23 10:43:03,325 - dropdown_utils4 - INFO - 옵션 24: '그룹 없음'
2025-06-23 10:43:03,330 - dropdown_utils4 - INFO - 옵션 25: '신규수집'
2025-06-23 10:43:03,335 - dropdown_utils4 - INFO - 옵션 26: '신규수집'
2025-06-23 10:43:03,340 - dropdown_utils4 - INFO - 옵션 27: '번역대기'
2025-06-23 10:43:03,344 - dropdown_utils4 - INFO - 옵션 28: '번역대기'
2025-06-23 10:43:03,349 - dropdown_utils4 - INFO - 옵션 29: '등록실행'
2025-06-23 10:43:03,354 - dropdown_utils4 - INFO - 옵션 30: '등록실행'
2025-06-23 10:43:03,360 - dropdown_utils4 - INFO - 옵션 31: '등록A'
2025-06-23 10:43:03,365 - dropdown_utils4 - INFO - 옵션 32: '등록A'
2025-06-23 10:43:03,370 - dropdown_utils4 - INFO - 옵션 33: '등록B'
2025-06-23 10:43:03,375 - dropdown_utils4 - INFO - 옵션 34: '등록B'
2025-06-23 10:43:03,381 - dropdown_utils4 - INFO - 옵션 35: '등록C'
2025-06-23 10:43:03,386 - dropdown_utils4 - INFO - 옵션 36: '등록C'
2025-06-23 10:43:03,392 - dropdown_utils4 - INFO - 옵션 37: ''
2025-06-23 10:43:03,397 - dropdown_utils4 - INFO - 옵션 38: ''
2025-06-23 10:43:03,403 - dropdown_utils4 - INFO - 옵션 39: ''
2025-06-23 10:43:03,408 - dropdown_utils4 - INFO - 옵션 40: ''
2025-06-23 10:43:03,735 - dropdown_utils4 - INFO - 스크롤 후 40개 옵션 확인
2025-06-23 10:43:03,735 - dropdown_utils4 - INFO - 스크롤 26/30
2025-06-23 10:43:03,743 - dropdown_utils4 - INFO - 현재 화면에 40개의 옵션 발견
2025-06-23 10:43:03,749 - dropdown_utils4 - INFO - 옵션 1: ''
2025-06-23 10:43:03,754 - dropdown_utils4 - INFO - 옵션 2: ''
2025-06-23 10:43:03,759 - dropdown_utils4 - INFO - 옵션 3: ''
2025-06-23 10:43:03,763 - dropdown_utils4 - INFO - 옵션 4: ''
2025-06-23 10:43:03,768 - dropdown_utils4 - INFO - 옵션 5: ''
2025-06-23 10:43:03,773 - dropdown_utils4 - INFO - 옵션 6: ''
2025-06-23 10:43:03,778 - dropdown_utils4 - INFO - 옵션 7: ''
2025-06-23 10:43:03,782 - dropdown_utils4 - INFO - 옵션 8: ''
2025-06-23 10:43:03,786 - dropdown_utils4 - INFO - 옵션 9: ''
2025-06-23 10:43:03,791 - dropdown_utils4 - INFO - 옵션 10: ''
2025-06-23 10:43:03,795 - dropdown_utils4 - INFO - 옵션 11: ''
2025-06-23 10:43:03,800 - dropdown_utils4 - INFO - 옵션 12: ''
2025-06-23 10:43:03,804 - dropdown_utils4 - INFO - 옵션 13: ''
2025-06-23 10:43:03,809 - dropdown_utils4 - INFO - 옵션 14: ''
2025-06-23 10:43:03,813 - dropdown_utils4 - INFO - 옵션 15: ''
2025-06-23 10:43:03,818 - dropdown_utils4 - INFO - 옵션 16: ''
2025-06-23 10:43:03,823 - dropdown_utils4 - INFO - 옵션 17: ''
2025-06-23 10:43:03,827 - dropdown_utils4 - INFO - 옵션 18: ''
2025-06-23 10:43:03,832 - dropdown_utils4 - INFO - 옵션 19: ''
2025-06-23 10:43:03,836 - dropdown_utils4 - INFO - 옵션 20: ''
2025-06-23 10:43:03,841 - dropdown_utils4 - INFO - 옵션 21: '전체'
2025-06-23 10:43:03,845 - dropdown_utils4 - INFO - 옵션 22: '전체'
2025-06-23 10:43:03,850 - dropdown_utils4 - INFO - 옵션 23: '그룹 없음'
2025-06-23 10:43:03,855 - dropdown_utils4 - INFO - 옵션 24: '그룹 없음'
2025-06-23 10:43:03,860 - dropdown_utils4 - INFO - 옵션 25: '신규수집'
2025-06-23 10:43:03,865 - dropdown_utils4 - INFO - 옵션 26: '신규수집'
2025-06-23 10:43:03,869 - dropdown_utils4 - INFO - 옵션 27: '번역대기'
2025-06-23 10:43:03,874 - dropdown_utils4 - INFO - 옵션 28: '번역대기'
2025-06-23 10:43:03,879 - dropdown_utils4 - INFO - 옵션 29: '등록실행'
2025-06-23 10:43:03,883 - dropdown_utils4 - INFO - 옵션 30: '등록실행'
2025-06-23 10:43:03,888 - dropdown_utils4 - INFO - 옵션 31: '등록A'
2025-06-23 10:43:03,893 - dropdown_utils4 - INFO - 옵션 32: '등록A'
2025-06-23 10:43:03,898 - dropdown_utils4 - INFO - 옵션 33: '등록B'
2025-06-23 10:43:03,902 - dropdown_utils4 - INFO - 옵션 34: '등록B'
2025-06-23 10:43:03,907 - dropdown_utils4 - INFO - 옵션 35: '등록C'
2025-06-23 10:43:03,911 - dropdown_utils4 - INFO - 옵션 36: '등록C'
2025-06-23 10:43:03,916 - dropdown_utils4 - INFO - 옵션 37: ''
2025-06-23 10:43:03,920 - dropdown_utils4 - INFO - 옵션 38: ''
2025-06-23 10:43:03,925 - dropdown_utils4 - INFO - 옵션 39: ''
2025-06-23 10:43:03,929 - dropdown_utils4 - INFO - 옵션 40: ''
2025-06-23 10:43:04,245 - dropdown_utils4 - INFO - 스크롤 후 40개 옵션 확인
2025-06-23 10:43:04,245 - dropdown_utils4 - INFO - 스크롤 27/30
2025-06-23 10:43:04,253 - dropdown_utils4 - INFO - 현재 화면에 40개의 옵션 발견
2025-06-23 10:43:04,260 - dropdown_utils4 - INFO - 옵션 1: ''
2025-06-23 10:43:04,266 - dropdown_utils4 - INFO - 옵션 2: ''
2025-06-23 10:43:04,272 - dropdown_utils4 - INFO - 옵션 3: ''
2025-06-23 10:43:04,276 - dropdown_utils4 - INFO - 옵션 4: ''
2025-06-23 10:43:04,281 - dropdown_utils4 - INFO - 옵션 5: ''
2025-06-23 10:43:04,285 - dropdown_utils4 - INFO - 옵션 6: ''
2025-06-23 10:43:04,289 - dropdown_utils4 - INFO - 옵션 7: ''
2025-06-23 10:43:04,294 - dropdown_utils4 - INFO - 옵션 8: ''
2025-06-23 10:43:04,298 - dropdown_utils4 - INFO - 옵션 9: ''
2025-06-23 10:43:04,302 - dropdown_utils4 - INFO - 옵션 10: ''
2025-06-23 10:43:04,307 - dropdown_utils4 - INFO - 옵션 11: ''
2025-06-23 10:43:04,311 - dropdown_utils4 - INFO - 옵션 12: ''
2025-06-23 10:43:04,315 - dropdown_utils4 - INFO - 옵션 13: ''
2025-06-23 10:43:04,319 - dropdown_utils4 - INFO - 옵션 14: ''
2025-06-23 10:43:04,324 - dropdown_utils4 - INFO - 옵션 15: ''
2025-06-23 10:43:04,329 - dropdown_utils4 - INFO - 옵션 16: ''
2025-06-23 10:43:04,333 - dropdown_utils4 - INFO - 옵션 17: ''
2025-06-23 10:43:04,337 - dropdown_utils4 - INFO - 옵션 18: ''
2025-06-23 10:43:04,342 - dropdown_utils4 - INFO - 옵션 19: ''
2025-06-23 10:43:04,346 - dropdown_utils4 - INFO - 옵션 20: ''
2025-06-23 10:43:04,350 - dropdown_utils4 - INFO - 옵션 21: '전체'
2025-06-23 10:43:04,355 - dropdown_utils4 - INFO - 옵션 22: '전체'
2025-06-23 10:43:04,360 - dropdown_utils4 - INFO - 옵션 23: '그룹 없음'
2025-06-23 10:43:04,364 - dropdown_utils4 - INFO - 옵션 24: '그룹 없음'
2025-06-23 10:43:04,369 - dropdown_utils4 - INFO - 옵션 25: '신규수집'
2025-06-23 10:43:04,374 - dropdown_utils4 - INFO - 옵션 26: '신규수집'
2025-06-23 10:43:04,379 - dropdown_utils4 - INFO - 옵션 27: '번역대기'
2025-06-23 10:43:04,383 - dropdown_utils4 - INFO - 옵션 28: '번역대기'
2025-06-23 10:43:04,388 - dropdown_utils4 - INFO - 옵션 29: '등록실행'
2025-06-23 10:43:04,392 - dropdown_utils4 - INFO - 옵션 30: '등록실행'
2025-06-23 10:43:04,397 - dropdown_utils4 - INFO - 옵션 31: '등록A'
2025-06-23 10:43:04,402 - dropdown_utils4 - INFO - 옵션 32: '등록A'
2025-06-23 10:43:04,407 - dropdown_utils4 - INFO - 옵션 33: '등록B'
2025-06-23 10:43:04,411 - dropdown_utils4 - INFO - 옵션 34: '등록B'
2025-06-23 10:43:04,416 - dropdown_utils4 - INFO - 옵션 35: '등록C'
2025-06-23 10:43:04,420 - dropdown_utils4 - INFO - 옵션 36: '등록C'
2025-06-23 10:43:04,425 - dropdown_utils4 - INFO - 옵션 37: ''
2025-06-23 10:43:04,429 - dropdown_utils4 - INFO - 옵션 38: ''
2025-06-23 10:43:04,434 - dropdown_utils4 - INFO - 옵션 39: ''
2025-06-23 10:43:04,439 - dropdown_utils4 - INFO - 옵션 40: ''
2025-06-23 10:43:04,766 - dropdown_utils4 - INFO - 스크롤 후 40개 옵션 확인
2025-06-23 10:43:04,767 - dropdown_utils4 - INFO - 스크롤 28/30
2025-06-23 10:43:04,776 - dropdown_utils4 - INFO - 현재 화면에 40개의 옵션 발견
2025-06-23 10:43:04,781 - dropdown_utils4 - INFO - 옵션 1: ''
2025-06-23 10:43:04,787 - dropdown_utils4 - INFO - 옵션 2: ''
2025-06-23 10:43:04,792 - dropdown_utils4 - INFO - 옵션 3: ''
2025-06-23 10:43:04,796 - dropdown_utils4 - INFO - 옵션 4: ''
2025-06-23 10:43:04,800 - dropdown_utils4 - INFO - 옵션 5: ''
2025-06-23 10:43:04,805 - dropdown_utils4 - INFO - 옵션 6: ''
2025-06-23 10:43:04,809 - dropdown_utils4 - INFO - 옵션 7: ''
2025-06-23 10:43:04,814 - dropdown_utils4 - INFO - 옵션 8: ''
2025-06-23 10:43:04,818 - dropdown_utils4 - INFO - 옵션 9: ''
2025-06-23 10:43:04,823 - dropdown_utils4 - INFO - 옵션 10: ''
2025-06-23 10:43:04,827 - dropdown_utils4 - INFO - 옵션 11: ''
2025-06-23 10:43:04,832 - dropdown_utils4 - INFO - 옵션 12: ''
2025-06-23 10:43:04,836 - dropdown_utils4 - INFO - 옵션 13: ''
2025-06-23 10:43:04,840 - dropdown_utils4 - INFO - 옵션 14: ''
2025-06-23 10:43:04,845 - dropdown_utils4 - INFO - 옵션 15: ''
2025-06-23 10:43:04,849 - dropdown_utils4 - INFO - 옵션 16: ''
2025-06-23 10:43:04,853 - dropdown_utils4 - INFO - 옵션 17: ''
2025-06-23 10:43:04,858 - dropdown_utils4 - INFO - 옵션 18: ''
2025-06-23 10:43:04,862 - dropdown_utils4 - INFO - 옵션 19: ''
2025-06-23 10:43:04,866 - dropdown_utils4 - INFO - 옵션 20: ''
2025-06-23 10:43:04,871 - dropdown_utils4 - INFO - 옵션 21: '전체'
2025-06-23 10:43:04,876 - dropdown_utils4 - INFO - 옵션 22: '전체'
2025-06-23 10:43:04,880 - dropdown_utils4 - INFO - 옵션 23: '그룹 없음'
2025-06-23 10:43:04,885 - dropdown_utils4 - INFO - 옵션 24: '그룹 없음'
2025-06-23 10:43:04,890 - dropdown_utils4 - INFO - 옵션 25: '신규수집'
2025-06-23 10:43:04,894 - dropdown_utils4 - INFO - 옵션 26: '신규수집'
2025-06-23 10:43:04,899 - dropdown_utils4 - INFO - 옵션 27: '번역대기'
2025-06-23 10:43:04,904 - dropdown_utils4 - INFO - 옵션 28: '번역대기'
2025-06-23 10:43:04,908 - dropdown_utils4 - INFO - 옵션 29: '등록실행'
2025-06-23 10:43:04,913 - dropdown_utils4 - INFO - 옵션 30: '등록실행'
2025-06-23 10:43:04,917 - dropdown_utils4 - INFO - 옵션 31: '등록A'
2025-06-23 10:43:04,922 - dropdown_utils4 - INFO - 옵션 32: '등록A'
2025-06-23 10:43:04,927 - dropdown_utils4 - INFO - 옵션 33: '등록B'
2025-06-23 10:43:04,931 - dropdown_utils4 - INFO - 옵션 34: '등록B'
2025-06-23 10:43:04,936 - dropdown_utils4 - INFO - 옵션 35: '등록C'
2025-06-23 10:43:04,941 - dropdown_utils4 - INFO - 옵션 36: '등록C'
2025-06-23 10:43:04,945 - dropdown_utils4 - INFO - 옵션 37: ''
2025-06-23 10:43:04,949 - dropdown_utils4 - INFO - 옵션 38: ''
2025-06-23 10:43:04,954 - dropdown_utils4 - INFO - 옵션 39: ''
2025-06-23 10:43:04,959 - dropdown_utils4 - INFO - 옵션 40: ''
2025-06-23 10:43:05,285 - dropdown_utils4 - INFO - 스크롤 후 40개 옵션 확인
2025-06-23 10:43:05,285 - dropdown_utils4 - INFO - 스크롤 29/30
2025-06-23 10:43:05,293 - dropdown_utils4 - INFO - 현재 화면에 40개의 옵션 발견
2025-06-23 10:43:05,299 - dropdown_utils4 - INFO - 옵션 1: ''
2025-06-23 10:43:05,304 - dropdown_utils4 - INFO - 옵션 2: ''
2025-06-23 10:43:05,309 - dropdown_utils4 - INFO - 옵션 3: ''
2025-06-23 10:43:05,313 - dropdown_utils4 - INFO - 옵션 4: ''
2025-06-23 10:43:05,317 - dropdown_utils4 - INFO - 옵션 5: ''
2025-06-23 10:43:05,322 - dropdown_utils4 - INFO - 옵션 6: ''
2025-06-23 10:43:05,327 - dropdown_utils4 - INFO - 옵션 7: ''
2025-06-23 10:43:05,331 - dropdown_utils4 - INFO - 옵션 8: ''
2025-06-23 10:43:05,335 - dropdown_utils4 - INFO - 옵션 9: ''
2025-06-23 10:43:05,339 - dropdown_utils4 - INFO - 옵션 10: ''
2025-06-23 10:43:05,344 - dropdown_utils4 - INFO - 옵션 11: ''
2025-06-23 10:43:05,348 - dropdown_utils4 - INFO - 옵션 12: ''
2025-06-23 10:43:05,352 - dropdown_utils4 - INFO - 옵션 13: ''
2025-06-23 10:43:05,357 - dropdown_utils4 - INFO - 옵션 14: ''
2025-06-23 10:43:05,361 - dropdown_utils4 - INFO - 옵션 15: ''
2025-06-23 10:43:05,366 - dropdown_utils4 - INFO - 옵션 16: ''
2025-06-23 10:43:05,370 - dropdown_utils4 - INFO - 옵션 17: ''
2025-06-23 10:43:05,374 - dropdown_utils4 - INFO - 옵션 18: ''
2025-06-23 10:43:05,379 - dropdown_utils4 - INFO - 옵션 19: ''
2025-06-23 10:43:05,383 - dropdown_utils4 - INFO - 옵션 20: ''
2025-06-23 10:43:05,387 - dropdown_utils4 - INFO - 옵션 21: '전체'
2025-06-23 10:43:05,392 - dropdown_utils4 - INFO - 옵션 22: '전체'
2025-06-23 10:43:05,396 - dropdown_utils4 - INFO - 옵션 23: '그룹 없음'
2025-06-23 10:43:05,401 - dropdown_utils4 - INFO - 옵션 24: '그룹 없음'
2025-06-23 10:43:05,406 - dropdown_utils4 - INFO - 옵션 25: '신규수집'
2025-06-23 10:43:05,410 - dropdown_utils4 - INFO - 옵션 26: '신규수집'
2025-06-23 10:43:05,415 - dropdown_utils4 - INFO - 옵션 27: '번역대기'
2025-06-23 10:43:05,420 - dropdown_utils4 - INFO - 옵션 28: '번역대기'
2025-06-23 10:43:05,425 - dropdown_utils4 - INFO - 옵션 29: '등록실행'
2025-06-23 10:43:05,430 - dropdown_utils4 - INFO - 옵션 30: '등록실행'
2025-06-23 10:43:05,435 - dropdown_utils4 - INFO - 옵션 31: '등록A'
2025-06-23 10:43:05,440 - dropdown_utils4 - INFO - 옵션 32: '등록A'
2025-06-23 10:43:05,445 - dropdown_utils4 - INFO - 옵션 33: '등록B'
2025-06-23 10:43:05,450 - dropdown_utils4 - INFO - 옵션 34: '등록B'
2025-06-23 10:43:05,455 - dropdown_utils4 - INFO - 옵션 35: '등록C'
2025-06-23 10:43:05,460 - dropdown_utils4 - INFO - 옵션 36: '등록C'
2025-06-23 10:43:05,465 - dropdown_utils4 - INFO - 옵션 37: ''
2025-06-23 10:43:05,470 - dropdown_utils4 - INFO - 옵션 38: ''
2025-06-23 10:43:05,475 - dropdown_utils4 - INFO - 옵션 39: ''
2025-06-23 10:43:05,480 - dropdown_utils4 - INFO - 옵션 40: ''
2025-06-23 10:43:05,791 - dropdown_utils4 - INFO - 스크롤 후 40개 옵션 확인
2025-06-23 10:43:05,791 - dropdown_utils4 - INFO - 스크롤 30/30
2025-06-23 10:43:05,798 - dropdown_utils4 - INFO - 현재 화면에 40개의 옵션 발견
2025-06-23 10:43:05,804 - dropdown_utils4 - INFO - 옵션 1: ''
2025-06-23 10:43:05,809 - dropdown_utils4 - INFO - 옵션 2: ''
2025-06-23 10:43:05,814 - dropdown_utils4 - INFO - 옵션 3: ''
2025-06-23 10:43:05,819 - dropdown_utils4 - INFO - 옵션 4: ''
2025-06-23 10:43:05,824 - dropdown_utils4 - INFO - 옵션 5: ''
2025-06-23 10:43:05,829 - dropdown_utils4 - INFO - 옵션 6: ''
2025-06-23 10:43:05,834 - dropdown_utils4 - INFO - 옵션 7: ''
2025-06-23 10:43:05,839 - dropdown_utils4 - INFO - 옵션 8: ''
2025-06-23 10:43:05,843 - dropdown_utils4 - INFO - 옵션 9: ''
2025-06-23 10:43:05,848 - dropdown_utils4 - INFO - 옵션 10: ''
2025-06-23 10:43:05,852 - dropdown_utils4 - INFO - 옵션 11: ''
2025-06-23 10:43:05,858 - dropdown_utils4 - INFO - 옵션 12: ''
2025-06-23 10:43:05,863 - dropdown_utils4 - INFO - 옵션 13: ''
2025-06-23 10:43:05,868 - dropdown_utils4 - INFO - 옵션 14: ''
2025-06-23 10:43:05,874 - dropdown_utils4 - INFO - 옵션 15: ''
2025-06-23 10:43:05,879 - dropdown_utils4 - INFO - 옵션 16: ''
2025-06-23 10:43:05,884 - dropdown_utils4 - INFO - 옵션 17: ''
2025-06-23 10:43:05,889 - dropdown_utils4 - INFO - 옵션 18: ''
2025-06-23 10:43:05,894 - dropdown_utils4 - INFO - 옵션 19: ''
2025-06-23 10:43:05,901 - dropdown_utils4 - INFO - 옵션 20: ''
2025-06-23 10:43:05,907 - dropdown_utils4 - INFO - 옵션 21: '전체'
2025-06-23 10:43:05,912 - dropdown_utils4 - INFO - 옵션 22: '전체'
2025-06-23 10:43:05,917 - dropdown_utils4 - INFO - 옵션 23: '그룹 없음'
2025-06-23 10:43:05,922 - dropdown_utils4 - INFO - 옵션 24: '그룹 없음'
2025-06-23 10:43:05,927 - dropdown_utils4 - INFO - 옵션 25: '신규수집'
2025-06-23 10:43:05,932 - dropdown_utils4 - INFO - 옵션 26: '신규수집'
2025-06-23 10:43:05,937 - dropdown_utils4 - INFO - 옵션 27: '번역대기'
2025-06-23 10:43:05,942 - dropdown_utils4 - INFO - 옵션 28: '번역대기'
2025-06-23 10:43:05,947 - dropdown_utils4 - INFO - 옵션 29: '등록실행'
2025-06-23 10:43:05,952 - dropdown_utils4 - INFO - 옵션 30: '등록실행'
2025-06-23 10:43:05,957 - dropdown_utils4 - INFO - 옵션 31: '등록A'
2025-06-23 10:43:05,965 - dropdown_utils4 - INFO - 옵션 32: '등록A'
2025-06-23 10:43:05,974 - dropdown_utils4 - INFO - 옵션 33: '등록B'
2025-06-23 10:43:05,982 - dropdown_utils4 - INFO - 옵션 34: '등록B'
2025-06-23 10:43:05,995 - dropdown_utils4 - INFO - 옵션 35: '등록C'
2025-06-23 10:43:05,999 - dropdown_utils4 - INFO - 옵션 36: '등록C'
2025-06-23 10:43:06,005 - dropdown_utils4 - INFO - 옵션 37: ''
2025-06-23 10:43:06,010 - dropdown_utils4 - INFO - 옵션 38: ''
2025-06-23 10:43:06,015 - dropdown_utils4 - INFO - 옵션 39: ''
2025-06-23 10:43:06,019 - dropdown_utils4 - INFO - 옵션 40: ''
2025-06-23 10:43:06,330 - dropdown_utils4 - INFO - 스크롤 후 40개 옵션 확인
2025-06-23 10:43:06,330 - dropdown_utils4 - WARNING - 최대 스크롤 횟수(30)에 도달했지만 '쇼핑몰A1' 그룹을 찾지 못했습니다.
2025-06-23 10:43:06,330 - dropdown_utils4 - INFO - === 현재 사용 가능한 모든 옵션들 ===
2025-06-23 10:43:06,343 - dropdown_utils4 - INFO - 사용 가능한 옵션 1: ''
2025-06-23 10:43:06,348 - dropdown_utils4 - INFO - 사용 가능한 옵션 2: ''
2025-06-23 10:43:06,353 - dropdown_utils4 - INFO - 사용 가능한 옵션 3: ''
2025-06-23 10:43:06,358 - dropdown_utils4 - INFO - 사용 가능한 옵션 4: ''
2025-06-23 10:43:06,363 - dropdown_utils4 - INFO - 사용 가능한 옵션 5: ''
2025-06-23 10:43:06,368 - dropdown_utils4 - INFO - 사용 가능한 옵션 6: ''
2025-06-23 10:43:06,373 - dropdown_utils4 - INFO - 사용 가능한 옵션 7: ''
2025-06-23 10:43:06,378 - dropdown_utils4 - INFO - 사용 가능한 옵션 8: ''
2025-06-23 10:43:06,383 - dropdown_utils4 - INFO - 사용 가능한 옵션 9: ''
2025-06-23 10:43:06,388 - dropdown_utils4 - INFO - 사용 가능한 옵션 10: ''
2025-06-23 10:43:06,393 - dropdown_utils4 - INFO - 사용 가능한 옵션 11: ''
2025-06-23 10:43:06,398 - dropdown_utils4 - INFO - 사용 가능한 옵션 12: ''
2025-06-23 10:43:06,403 - dropdown_utils4 - INFO - 사용 가능한 옵션 13: ''
2025-06-23 10:43:06,408 - dropdown_utils4 - INFO - 사용 가능한 옵션 14: ''
2025-06-23 10:43:06,414 - dropdown_utils4 - INFO - 사용 가능한 옵션 15: ''
2025-06-23 10:43:06,419 - dropdown_utils4 - INFO - 사용 가능한 옵션 16: ''
2025-06-23 10:43:06,424 - dropdown_utils4 - INFO - 사용 가능한 옵션 17: ''
2025-06-23 10:43:06,429 - dropdown_utils4 - INFO - 사용 가능한 옵션 18: ''
2025-06-23 10:43:06,434 - dropdown_utils4 - INFO - 사용 가능한 옵션 19: ''
2025-06-23 10:43:06,440 - dropdown_utils4 - INFO - 사용 가능한 옵션 20: ''
2025-06-23 10:43:06,446 - dropdown_utils4 - INFO - 사용 가능한 옵션 21: '전체'
2025-06-23 10:43:06,450 - dropdown_utils4 - INFO - 사용 가능한 옵션 22: '전체'
2025-06-23 10:43:06,455 - dropdown_utils4 - INFO - 사용 가능한 옵션 23: '그룹 없음'
2025-06-23 10:43:06,460 - dropdown_utils4 - INFO - 사용 가능한 옵션 24: '그룹 없음'
2025-06-23 10:43:06,465 - dropdown_utils4 - INFO - 사용 가능한 옵션 25: '신규수집'
2025-06-23 10:43:06,469 - dropdown_utils4 - INFO - 사용 가능한 옵션 26: '신규수집'
2025-06-23 10:43:06,474 - dropdown_utils4 - INFO - 사용 가능한 옵션 27: '번역대기'
2025-06-23 10:43:06,479 - dropdown_utils4 - INFO - 사용 가능한 옵션 28: '번역대기'
2025-06-23 10:43:06,483 - dropdown_utils4 - INFO - 사용 가능한 옵션 29: '등록실행'
2025-06-23 10:43:06,488 - dropdown_utils4 - INFO - 사용 가능한 옵션 30: '등록실행'
2025-06-23 10:43:06,493 - dropdown_utils4 - INFO - 사용 가능한 옵션 31: '등록A'
2025-06-23 10:43:06,497 - dropdown_utils4 - INFO - 사용 가능한 옵션 32: '등록A'
2025-06-23 10:43:06,501 - dropdown_utils4 - INFO - 사용 가능한 옵션 33: '등록B'
2025-06-23 10:43:06,506 - dropdown_utils4 - INFO - 사용 가능한 옵션 34: '등록B'
2025-06-23 10:43:06,511 - dropdown_utils4 - INFO - 사용 가능한 옵션 35: '등록C'
2025-06-23 10:43:06,515 - dropdown_utils4 - INFO - 사용 가능한 옵션 36: '등록C'
2025-06-23 10:43:06,520 - dropdown_utils4 - INFO - 사용 가능한 옵션 37: ''
2025-06-23 10:43:06,525 - dropdown_utils4 - INFO - 사용 가능한 옵션 38: ''
2025-06-23 10:43:06,529 - dropdown_utils4 - INFO - 사용 가능한 옵션 39: ''
2025-06-23 10:43:06,533 - dropdown_utils4 - INFO - 사용 가능한 옵션 40: ''
2025-06-23 10:43:06,533 - dropdown_utils4 - INFO - === 총 40개의 옵션 ===
2025-06-23 10:43:06,533 - dropdown_utils4 - ERROR - 그룹 '쇼핑몰A1'을 찾을 수 없습니다
2025-06-23 10:43:06,534 - dropdown_utils4 - ERROR - 그룹 '쇼핑몰A1' 선택 실패
2025-06-23 10:43:06,534 - product_editor_core6_1_dynamic - ERROR - 그룹 선택 실패: 쇼핑몰A1
2025-06-23 10:43:06,534 - product_editor_core6_1_dynamic - ERROR - 동적 그룹 선택 실패: 쇼핑몰A1
2025-06-23 10:43:06,534 - product_editor_core6_1_dynamic - INFO - === 마켓 설정 2/12 처리 시작 ===
2025-06-23 10:43:06,534 - product_editor_core6_1_dynamic - INFO - 그룹명: 쇼핑몰A2, API키: c05ae0a14f...
2025-06-23 10:43:06,534 - product_editor_core6_1_dynamic - INFO - 마켓 설정 화면 정보 처리 시작 - 그룹: 쇼핑몰A2
2025-06-23 10:43:06,534 - product_editor_core6_1_dynamic - INFO - 마켓설정 메뉴 클릭 시도
2025-06-23 10:43:06,682 - product_editor_core6_1_dynamic - INFO - 마켓설정 화면 열기 완료
2025-06-23 10:43:09,691 - product_editor_core6_1_dynamic - INFO - 스크롤 위치를 최상단으로 초기화
2025-06-23 10:43:09,691 - product_editor_core6_1_dynamic - INFO - smartstore API 연결 끊기 시도
2025-06-23 10:43:09,691 - product_editor_core6_1_dynamic - INFO - smartstore API 연결 끊기 시도
2025-06-23 10:43:10,292 - product_editor_core6_1_dynamic - INFO - ESC 키로 모달창 닫기 시도
2025-06-23 10:43:10,386 - product_editor_core6_1_dynamic - INFO - 스마트스토어 탭 클릭 완료
2025-06-23 10:43:21,641 - product_editor_core6_1_dynamic - ERROR - 마켓 패널 로드 시간 초과: smartstore
2025-06-23 10:43:21,641 - product_editor_core6_1_dynamic - WARNING - smartstore API 연결 끊기 실패
2025-06-23 10:43:22,642 - product_editor_core6_1_dynamic - INFO - coupang API 연결 끊기 시도
2025-06-23 10:43:22,642 - product_editor_core6_1_dynamic - INFO - coupang API 연결 끊기 시도
2025-06-23 10:43:23,214 - product_editor_core6_1_dynamic - INFO - ESC 키로 모달창 닫기 시도
2025-06-23 10:43:23,315 - product_editor_core6_1_dynamic - INFO - 쿠팡 탭 클릭 완료