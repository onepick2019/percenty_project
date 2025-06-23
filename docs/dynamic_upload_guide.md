# 퍼센티 동적 업로드 가이드

## 개요

`ProductEditorCore6_1Dynamic` 클래스는 `percenty_id.xlsx` 파일의 `market_id` 시트를 기반으로 동적으로 업로드를 진행하는 기능을 제공합니다.

## 주요 기능

### 1. 엑셀 기반 동적 설정
- `percenty_id.xlsx` 파일의 `market_id` 시트에서 설정 정보를 읽어옵니다
- A열의 로그인 ID와 매핑되는 행들을 순차적으로 처리합니다
- B열의 `groupname`을 사용하여 동적으로 그룹을 선택합니다
- C열의 `11store_api`를 사용하여 11번가 API 키를 설정합니다

### 2. 마켓 설정 자동화
- 마켓설정 화면을 자동으로 엽니다
- 모든 마켓의 API 연결을 끊습니다 (11번가만 사용하기 위해)
- 11번가-일반 탭을 선택하고 API 키를 입력합니다
- API 검증을 자동으로 수행합니다

### 3. 업로드 워크플로우
- 동적으로 선택된 그룹의 상품들을 업로드합니다
- 업로드 완료를 대기하고 모달창을 자동으로 닫습니다
- 여러 설정에 대해 순차적으로 처리합니다

## 파일 구조

### 필수 파일
- `percenty_id.xlsx`: 계정 정보와 마켓 설정이 포함된 엑셀 파일
- `product_editor_core6_1_dynamic.py`: 동적 업로드 핵심 클래스
- `test_dynamic_upload.py`: 테스트 실행 스크립트

### 의존성 파일
- `market_utils.py`: 마켓 설정 관련 유틸리티
- `dropdown_utils4.py`: 드롭다운 관련 유틸리티
- `upload_utils.py`: 업로드 관련 유틸리티
- `login_percenty.py`: 퍼센티 로그인 관리

## 엑셀 파일 구조

### `market_id` 시트 구조
```
A열 (id)        | B열 (groupname) | C열 (11store_api)
---------------|----------------|------------------
test@email.com | 쇼핑몰A1        | your_api_key_here
test@email.com | 쇼핑몰B2        | your_api_key_here
```

- **A열 (id)**: 퍼센티 로그인 계정 ID
- **B열 (groupname)**: 업로드할 상품 그룹명
- **C열 (11store_api)**: 11번가 API 키

## 사용법

### 1. 기본 사용법

```python
from product_editor_core6_1_dynamic import ProductEditorCore6_1Dynamic

# WebDriver와 계정 ID로 인스턴스 생성
core = ProductEditorCore6_1Dynamic(driver, account_id)

# 동적 업로드 워크플로우 실행
result = core.execute_dynamic_upload_workflow()
```

### 2. 테스트 스크립트 실행

```bash
python test_dynamic_upload.py
```

실행 시 계정 ID와 비밀번호를 입력하라는 프롬프트가 나타납니다.

### 3. 개별 기능 사용

```python
# 마켓 설정 정보 로드
market_configs = core.load_market_config_from_excel()

# 특정 마켓 설정 처리
core.setup_market_configuration(market_config)

# 동적 그룹 선택
core._select_dynamic_group("쇼핑몰A1")
```

## 주요 메서드

### `load_market_config_from_excel()`
- `percenty_id.xlsx`의 `market_id` 시트에서 설정 정보를 로드합니다
- 현재 계정 ID와 매핑되는 행들만 반환합니다

### `setup_market_configuration(market_config)`
- 마켓설정 화면을 열고 11번가 API를 설정합니다
- 모든 마켓 API 연결을 끊고 11번가만 활성화합니다

### `execute_dynamic_upload_workflow()`
- 전체 동적 업로드 워크플로우를 실행합니다
- 엑셀의 모든 설정에 대해 순차적으로 처리합니다

## 로그 및 디버깅

### 로그 파일
- `dynamic_upload_test.log`: 테스트 실행 시 생성되는 로그 파일
- 모든 작업 과정이 상세히 기록됩니다

### 주요 로그 메시지
```
마켓 설정 정보 로드 완료: 2개 설정 발견
=== 마켓 설정 1/2 처리 시작 ===
그룹명: 쇼핑몰A1, API키: abcd1234...
마켓설정 화면 열기 완료
모든 마켓 API 연결 끊기 완료
11번가 탭 선택 완료
11번가 API KEY 입력 완료
API 검증 완료
동적 그룹 선택 완료: 쇼핑몰A1
업로드 완료
=== 마켓 설정 1/2 처리 완료 ===
```

## 오류 처리

### 일반적인 오류와 해결방법

1. **엑셀 파일을 찾을 수 없음**
   - `percenty_id.xlsx` 파일이 프로젝트 루트에 있는지 확인
   - 파일 권한 확인

2. **마켓설정 화면 열기 실패**
   - 퍼센티 로그인 상태 확인
   - 네트워크 연결 상태 확인

3. **그룹 선택 실패**
   - 엑셀의 그룹명이 실제 퍼센티 화면의 그룹명과 일치하는지 확인
   - 대소문자 및 공백 확인

4. **API 검증 실패**
   - 11번가 API 키가 유효한지 확인
   - API 키 형식 확인

## 확장 가능성

### 다른 마켓 지원
현재는 11번가만 지원하지만, 다음과 같이 확장 가능합니다:

```python
# 쿠팡 지원 추가 예시
def setup_coupang_configuration(self, market_config):
    # 쿠팡 탭 선택
    self.market_utils.click_market_tab('coupang')
    # 쿠팡 API 설정
    # ...
```

### 배치 처리
여러 계정에 대해 동시에 처리하는 기능도 추가 가능합니다.

## 보안 고려사항

- API 키는 로그에 일부만 표시됩니다 (보안을 위해)
- 엑셀 파일에 민감한 정보가 포함되므로 접근 권한을 적절히 관리해야 합니다
- 테스트 시에는 실제 운영 계정이 아닌 테스트 계정을 사용하는 것을 권장합니다

## 문제 해결

문제가 발생할 경우:
1. 로그 파일을 확인하여 구체적인 오류 메시지를 파악
2. 엑셀 파일의 데이터 형식 확인
3. 퍼센티 웹사이트의 UI 변경 여부 확인
4. 네트워크 연결 및 브라우저 설정 확인