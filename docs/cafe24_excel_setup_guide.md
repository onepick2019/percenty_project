# 카페24 11번가 상품 가져오기 설정 가이드

## 개요
카페24 11번가 상품 가져오기 기능을 사용하기 위해서는 `percenty_id.xlsx` 파일에 필요한 설정 컬럼을 추가해야 합니다.

## 필요한 엑셀 컬럼 추가

### 1. 현재 엑셀 파일 구조
현재 `percenty_id.xlsx` 파일에는 다음 컬럼들이 있습니다:
- id (A열)
- password (B열)
- operator (C열)
- sheet_nickname (D열)
- suffixA1~D3 (E~P열)

### 2. 추가해야 할 컬럼들
다음 컬럼들을 엑셀 파일에 추가해야 합니다:

| 컬럼명 | 열 위치 | 설명 | 예시 |
|--------|---------|------|------|
| `cafe24_server` | Q열 | 카페24 서버 정보 | `https://yourstore.cafe24.com` |
| `cafe24_id` | R열 | 카페24 로그인 아이디 | `your_cafe24_id` |
| `cafe24_password` | S열 | 카페24 로그인 비밀번호 | `your_password` |
| `11store_id` | T열 | 11번가 스토어 ID | `your_11st_store_id` |

### 3. 엑셀 파일 수정 방법

1. **Excel에서 `percenty_id.xlsx` 파일 열기**
2. **Q열에 `cafe24_server` 헤더 추가**
3. **R열에 `cafe24_id` 헤더 추가**
4. **S열에 `cafe24_password` 헤더 추가**
5. **T열에 `11store_id` 헤더 추가**
6. **각 행에 해당하는 값들 입력**
7. **파일 저장**

### 4. 설정 값 입력 예시

```
| id | password | ... | cafe24_server | cafe24_id | cafe24_password | 11store_id |
|----|----------|-----|---------------|-----------|-----------------|------------|
| onepick2019@gmail.com | qnwkehlwk8* | ... | https://mystore.cafe24.com | mycafe24id | mypassword | mystoreid |
```

## 테스트 방법

### 1. 설정 확인
```bash
python check_excel_structure.py
```

### 2. 카페24 디버깅 테스트 실행
```bash
python cafe24_debug_test.py
```

### 3. 테스트 모드 선택
- **1번 (전체 테스트)**: 모든 단계를 자동으로 실행
- **2번 (단계별 테스트)**: 각 단계마다 사용자 확인 후 진행

## 주의사항

1. **보안**: 비밀번호 등 민감한 정보가 포함되므로 엑셀 파일 관리에 주의하세요.
2. **백업**: 설정 변경 전 기존 엑셀 파일을 백업하세요.
3. **검증**: 설정 입력 후 반드시 테스트를 통해 정상 동작을 확인하세요.

## 문제 해결

### 설정 정보 누락 오류
```
ERROR - 필수 설정 정보가 누락되었습니다
ERROR - 카페24 ID: 
ERROR - 카페24 PW: 없음
ERROR - 11번가 스토어 ID:
```

**해결 방법:**
1. 엑셀 파일에 필요한 컬럼이 추가되었는지 확인
2. 각 컬럼에 올바른 값이 입력되었는지 확인
3. 엑셀 파일이 저장되었는지 확인

### 컬럼명 확인
```bash
python check_excel_structure.py
```
위 명령으로 현재 엑셀 파일의 컬럼 구조를 확인할 수 있습니다.

## 관련 파일

- `cafe24_debug_test.py`: 카페24 디버깅 테스트 파일
- `market_manager_cafe24.py`: 카페24 마켓 매니저 클래스
- `product_editor_core6_1_dynamic.py`: 메인 업로드 워크플로우
- `check_excel_structure.py`: 엑셀 구조 확인 스크립트