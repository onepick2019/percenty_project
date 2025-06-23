# 11번가 API 처리 중복 코드 제거

## 문제 상황

사용자가 제공한 로그에서 11번가 API KEY 입력 완료 후 불필요한 중복 로그가 발생하는 문제를 발견했습니다:

```
2025-06-22 23:11:04,933 - product_editor_core6_1_dynamic - INFO - 11번가-일반 API KEY 입력 완료: 2a59718824...
2025-06-22 23:11:05,933 - product_editor_core6_1_dynamic - INFO - 11번가 API KEY 입력 완료: 2a59718824...

>> 이미 11번가 탭이고 키 입력까지 마쳤는데, 아래 로그는 문제?
2025-06-22 23:11:05,957 - product_editor_core6_1_dynamic - INFO - 11번가-일반 탭이 이미 활성화되어 있음
2025-06-22 23:11:08,018 - product_editor_core6_1_dynamic - INFO - 11번가-일반 패널 로드 완료
```

## 원인 분석

### 1. API KEY 입력 과정에서의 중복

**호출 흐름:**
1. `_input_11st_api_key()` → `input_11st_general_api_key()` → `input_api_key()`
2. `input_api_key()` 메서드에서 `wait_for_market_panel_load()` 호출
3. 이미 탭 전환과 패널 로드가 완료된 상태에서 불필요한 중복 호출

### 2. API 검증 과정에서의 중복

**호출 흐름:**
1. API KEY 입력 완료 후 `perform_complete_11st_api_verification_workflow()` 호출
2. 이 메서드에서 다시 `switch_to_market('11st_general')` 및 `wait_for_market_panel_load('11st_general')` 호출
3. 이미 11번가-일반 탭이 활성화되고 패널이 로드된 상태에서 중복 처리

## 해결 방안

### 1. `input_api_key()` 메서드 수정

**파일:** `market_utils.py`

**수정 내용:**
- `input_api_key()` 메서드에서 불필요한 `wait_for_market_panel_load()` 호출 제거
- 이미 호출하는 쪽에서 탭 전환과 패널 로드가 완료된 상태이므로 중복 불필요

```python
# 수정 전
def input_api_key(self, market_key, api_key):
    """특정 마켓의 API KEY를 입력합니다."""
    try:
        market_name = self.market_names.get(market_key, market_key)
        self.logger.info(f"{market_name} API KEY 입력 시작")
        
        # 마켓 패널이 로드될 때까지 대기 ← 중복 호출
        if not self.wait_for_market_panel_load(market_key):
            self.logger.error(f"{market_name} 패널 로드 실패")
            return False
        
        # API KEY 입력창 찾기
        ...

# 수정 후
def input_api_key(self, market_key, api_key):
    """특정 마켓의 API KEY를 입력합니다."""
    try:
        market_name = self.market_names.get(market_key, market_key)
        self.logger.info(f"{market_name} API KEY 입력 시작")
        
        # API KEY 입력창 찾기 (패널 로드 대기 제거)
        ...
```

### 2. `perform_complete_11st_api_verification_workflow()` 메서드 수정

**파일:** `market_utils.py`

**수정 내용:**
- 불필요한 탭 전환 및 패널 로드 대기 제거
- 이미 API KEY 입력 단계에서 탭 활성화와 패널 로드가 완료된 상태

```python
# 수정 전
def perform_complete_11st_api_verification_workflow(self):
    """11번가 API 검증 전체 워크플로우를 수행합니다.
    
    1. 11번가 탭으로 전환
    2. API 검증 버튼 클릭
    3. API 검증 모달창 처리
    """
    try:
        # 1. 11번가-일반 탭으로 전환 ← 중복
        if not self.switch_to_market('11st_general'):
            return False
        
        # 2. 패널 로드 대기 ← 중복
        if not self.wait_for_market_panel_load('11st_general'):
            return False
        
        # 3. API 검증 버튼 클릭
        ...

# 수정 후
def perform_complete_11st_api_verification_workflow(self):
    """11번가 API 검증 전체 워크플로우를 수행합니다.
    
    1. API 검증 버튼 클릭
    2. API 검증 모달창 처리
    
    주의: 이 메서드는 이미 11번가-일반 탭이 활성화되고 패널이 로드된 상태에서 호출되어야 합니다.
    """
    try:
        # 1. API 검증 버튼 클릭
        if not self.click_api_validation_button():
            return False
        
        # 2. API 검증 모달창 처리
        return self.handle_11st_api_verification_modal()
```

## 주요 개선사항

### 1. 성능 향상
- 불필요한 탭 전환 및 패널 로드 대기 제거로 처리 속도 향상
- 중복 DOM 검색 및 대기 시간 단축

### 2. 로그 정리
- "탭이 이미 활성화되어 있음" 중복 로그 제거
- "패널 로드 완료" 중복 로그 제거
- 더 깔끔하고 명확한 로그 흐름

### 3. 코드 효율성
- 중복 코드 제거로 유지보수성 향상
- 메서드 간 책임 분리 명확화
- 호출 흐름 단순화

## 예상 결과

수정 후 로그 흐름:
```
2025-06-22 23:11:01,747 - product_editor_core6_1_dynamic - INFO - 11번가-일반 탭 클릭 완료
2025-06-22 23:11:02,747 - product_editor_core6_1_dynamic - INFO - 11번가 API KEY 입력 시작
2025-06-22 23:11:02,748 - product_editor_core6_1_dynamic - INFO - 11번가-일반 API KEY 입력 시작
2025-06-22 23:11:04,804 - product_editor_core6_1_dynamic - INFO - 11번가-일반 패널 로드 완료
2025-06-22 23:11:04,933 - product_editor_core6_1_dynamic - INFO - 11번가-일반 API KEY 입력 완료: 2a59718824...
2025-06-22 23:11:05,933 - product_editor_core6_1_dynamic - INFO - 11번가 API KEY 입력 완료: 2a59718824...
[API 검증 버튼 클릭 및 모달창 처리 로그]
```

**제거된 중복 로그:**
- ❌ "11번가-일반 탭이 이미 활성화되어 있음"
- ❌ "11번가-일반 패널 로드 완료" (두 번째)

## 테스트 권장사항

1. **기능 테스트**: 11번가 API KEY 입력 및 검증이 정상적으로 작동하는지 확인
2. **로그 확인**: 중복 로그가 제거되었는지 확인
3. **성능 테스트**: 처리 시간이 단축되었는지 확인
4. **다른 마켓**: 다른 마켓에서도 유사한 중복이 없는지 확인