# 톡스토어 API 키 입력 기능 구현

## 개요

엑셀 시트의 G열과 H열에 있는 톡스토어 API 정보를 파싱하여 퍼센티 마켓 설정에서 톡스토어 API 키를 자동으로 입력하는 기능을 구현했습니다.

## 구현 내용

### 1. 엑셀 파싱 확장

`product_editor_core6_1_dynamic.py`의 `load_market_config_from_excel()` 메서드를 수정하여 D열부터 J열까지 모든 마켓 API 키를 파싱하도록 확장했습니다.

```python
config = {
    'id': row.get('id', ''),
    'groupname': row.get('groupname', ''),  # B열
    '11store_api': row.get('11store_api', ''),  # C열
    'smartstore_api': row.get('smartstore_api', ''),  # D열
    'coupang_api': row.get('coupang_api', ''),  # E열
    'auction_gmarket_api': row.get('auction_gmarket_api', ''),  # F열
    'talkstore_api_key': row.get('talkstore_api_key', ''),  # G열
    'talkstore_store_url': row.get('talkstore_store_url', ''),  # H열
    'interpark_api': row.get('interpark_api', ''),  # I열
    'wemakeprice_api': row.get('wemakeprice_api', ''),  # J열
    'row_index': idx + 1
}
```

### 2. 톡스토어 API 키 입력 메서드 추가

`_input_talkstore_api_keys()` 메서드를 새로 구현했습니다:

#### 주요 기능
1. **톡스토어 탭 전환**: `kakao` 마켓으로 탭 전환
2. **패널 로드 대기**: 톡스토어 패널이 완전히 로드될 때까지 대기
3. **API Key 입력**: 첫 번째 입력창에 G열 값 입력
4. **스토어 URL 입력**: 두 번째 입력창에 H열 값 입력
5. **API 검증**: API 검증 버튼 클릭

#### 선택자 정보
- **API Key 입력창**: `div[id="rc-tabs-0-panel-kakao"] input[placeholder="미설정"]:first-of-type`
- **스토어 URL 입력창**: `div[id="rc-tabs-0-panel-kakao"] input[placeholder*="https://store.kakao.com"]`

### 3. 마켓 설정 워크플로우 수정

`setup_market_configuration()` 메서드를 수정하여 다중 마켓 API 키 입력을 지원하도록 했습니다:

```python
# 3. 각 마켓별 API 키 입력 (키값이 있는 경우에만)
api_setup_success = False

# 3-1. 11번가 API KEY 입력
api_key_11st = market_config.get('11store_api', '')
if api_key_11st:
    if self._input_11st_api_key(api_key_11st):
        logger.info("11번가 API KEY 입력 성공")
        api_setup_success = True

# 3-2. 톡스토어 API KEY 입력
talkstore_api_key = market_config.get('talkstore_api_key', '')
talkstore_store_url = market_config.get('talkstore_store_url', '')
if talkstore_api_key and talkstore_store_url:
    if self._input_talkstore_api_keys(talkstore_api_key, talkstore_store_url):
        logger.info("톡스토어 API 키 입력 성공")
        api_setup_success = True
```

### 4. 11번가 API 키 입력 메서드 개선

11번가 API 키 입력 메서드도 톡스토어와 동일한 패턴으로 수정했습니다:
- 탭 전환 및 패널 로드 대기 추가
- API 검증 워크플로우 포함

## 테스트
2025-06-23 12:01:12,941 - root - INFO - 스크롤 위치를 최상단으로 초기화했습니다
✅ 신규상품등록 화면 전환 성공!

11. 테스트 모드 선택...
    1. 전체 동적 업로드 워크플로우 실행
    2. 톡스토어 API 키 입력 테스트만 실행
    3. 마켓 설정 화면만 열기 (수동 테스트용)

선택하세요 (1-3): 2

=== 톡스토어 API 키 입력 테스트 ===
마켓 설정 화면을 여는 중...
2025-06-23 12:01:51,935 - product_editor_core6_1_dynamic - INFO - 마켓설정 메뉴 클릭 시도
2025-06-23 12:01:52,113 - product_editor_core6_1_dynamic - INFO - 마켓설정 화면 열기 완료
2025-06-23 12:01:55,122 - product_editor_core6_1_dynamic - INFO - 스크롤 위치를 최상단으로 초기화
✅ 마켓 설정 화면 열기 성공

톡스토어 API 정보를 입력하세요:
API Key (G열): ba505582197d4c3916f36c7248779651
스토어 URL (H열): https://store.kakao.com/1day1pick

입력된 정보:
  API Key: ba50558219...
  스토어 URL: https://store.kakao.com/1day1pick

톡스토어 API 키 입력 테스트 시작...
2025-06-23 12:02:23,018 - product_editor_core6_1_dynamic - INFO - 톡스토어 API 키 입력 시작
2025-06-23 12:02:23,618 - product_editor_core6_1_dynamic - INFO - ESC 키로 모달창 닫기 시도
2025-06-23 12:02:23,690 - product_editor_core6_1_dynamic - INFO - 톡스토어 탭 클릭 완료
2025-06-23 12:02:26,767 - product_editor_core6_1_dynamic - INFO - 톡스토어 패널 로드 완료
2025-06-23 12:02:26,908 - product_editor_core6_1_dynamic - INFO - 톡스토어 API Key 입력 완료: ba50558219...
2025-06-23 12:02:27,049 - product_editor_core6_1_dynamic - INFO - 톡스토어 주소 입력 완료: https://store.kakao.com/1day1pick
2025-06-23 12:02:27,049 - product_editor_core6_1_dynamic - INFO - API 검증 버튼 찾기 시도 - XPath: //div[contains(@class, "ant-tabs-tabpane-active")]//div[contains(@class, "ant-row")]//button[contains(@class, "ant-btn-primary") and .//span[text()="API 검증"]]
2025-06-23 12:02:28,141 - product_editor_core6_1_dynamic - INFO - API 검증 버튼 클릭 완료
2025-06-23 12:02:30,142 - product_editor_core6_1_dynamic - INFO - 톡스토어 API 검증 성공

🎉 톡스토어 API 키 입력 테스트 성공!
    API 키와 스토어 URL이 성공적으로 입력되었습니다.

종료하려면 Ctrl+C를 누르세요.
### 통합 테스트 스크립트

`percenty_dynamic_upload_test.py` 파일에 톡스토어 API 키 입력 테스트 기능이 통합되어 있습니다.

#### 테스트 실행 방법

```bash
python percenty_dynamic_upload_test.py
```

#### 테스트 모드 선택

스크립트 실행 후 다음 3가지 모드 중 선택할 수 있습니다:

1. **전체 동적 업로드 워크플로우 실행**: 기존 기능 (12번 순환 업로드)
2. **톡스토어 API 키 입력 테스트만 실행**: 톡스토어 디버깅 전용
3. **마켓 설정 화면만 열기**: 수동 테스트용

#### 톡스토어 테스트 시나리오 (모드 2)

1. 계정 선택 및 로그인
2. AI 소싱 메뉴 접속
3. 신규상품등록 화면 전환
4. 마켓 설정 화면 열기
5. 사용자가 직접 API Key와 스토어 URL 입력
6. 톡스토어 API 키 입력 테스트 실행
7. 결과 확인

#### 수동 테스트 시나리오 (모드 3)

1. 계정 선택 및 로그인
2. AI 소싱 메뉴 접속
3. 신규상품등록 화면 전환
4. 마켓 설정 화면 열기
5. 사용자가 브라우저에서 직접 테스트

### 테스트 데이터 예시

```
API Key (G열): your_talkstore_api_key_here
스토어 URL (H열): https://store.kakao.com/your-store-name
```

## 엑셀 시트 구조

| 열 | 필드명 | 설명 |
|---|---|---|
| A | id | 로그인 아이디 |
| B | groupname | 그룹명 |
| C | 11store_api | 11번가 API 키 |
| D | smartstore_api | 스마트스토어 API 키 |
| E | coupang_api | 쿠팡 API 키 |
| F | auction_gmarket_api | 옥션/G마켓 API 키 |
| G | talkstore_api_key | 톡스토어 API 키 |
| H | talkstore_store_url | 톡스토어 주소 |
| I | interpark_api | 인터파크 API 키 |
| J | wemakeprice_api | 위메프 API 키 |

## 향후 확장 계획

1. **스마트스토어 API 키 입력 메서드** 추가 (D열)
2. **쿠팡 API 키 입력 메서드** 추가 (E열)
3. **옥션/G마켓 API 키 입력 메서드** 추가 (F열)
4. **인터파크 API 키 입력 메서드** 추가 (I열)
5. **위메프 API 키 입력 메서드** 추가 (J열)

## 주의사항

1. **톡스토어 입력창 구조**: 톡스토어는 다른 마켓과 달리 2개의 입력창이 있습니다.
   - 첫 번째: API Key
   - 두 번째: 스토어 URL

2. **API 검증**: 톡스토어는 11번가와 달리 배송 프로필 모달창이 열리지 않고 API 검증 버튼만 클릭하면 됩니다.

3. **선택자 안정성**: 현재 구현된 선택자는 퍼센티 UI 구조에 의존하므로, UI 변경 시 업데이트가 필요할 수 있습니다.

## 로그 예시

```
2025-01-XX XX:XX:XX - product_editor_core6_1_dynamic - INFO - 톡스토어 API 키 입력 시작
2025-01-XX XX:XX:XX - product_editor_core6_1_dynamic - INFO - 톡스토어 탭 클릭 완료
2025-01-XX XX:XX:XX - product_editor_core6_1_dynamic - INFO - 톡스토어 패널 로드 완료
2025-01-XX XX:XX:XX - product_editor_core6_1_dynamic - INFO - 톡스토어 API Key 입력 완료: test_api_k...
2025-01-XX XX:XX:XX - product_editor_core6_1_dynamic - INFO - 톡스토어 주소 입력 완료: https://store.kakao.com/test-store
2025-01-XX XX:XX:XX - product_editor_core6_1_dynamic - INFO - 톡스토어 API 검증 성공
```