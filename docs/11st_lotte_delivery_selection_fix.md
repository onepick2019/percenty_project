# 11번가 롯데택배 선택 오류 해결 방안

## 문제 상황
```
2025-06-22 22:44:00,601 - product_editor_core6_1_dynamic - ERROR - 롯데(현대)택배 선택 중 요소를 찾을 수 없음
2025-06-22 22:44:00,601 - product_editor_core6_1_dynamic - ERROR - 11번가 API 검증 실패
```

## 원인 분석

### 1. 드롭다운 선택자 문제
- 기존: `nth-of-type(4)` 사용으로 부정확한 드롭다운 선택
- 문제: DOM 구조 변경 시 잘못된 드롭다운을 선택할 가능성

### 2. 롯데택배 옵션 이름 불일치
- 기존: `title="롯데(현대)택배"` 정확한 매칭
- 문제: 실제 옵션 이름이 다를 수 있음

### 3. DOM 구조 분석
11번가 배송프로필 모달창의 드롭다운 구조:
- 지역 구분 (전국)
- 발송 예정일 템플릿
- **출고 택배사** (CJ대한통운 → 롯데택배로 변경 필요)
- 출고지
- 반품/교환지

## 해결 방안

### 1. 드롭다운 선택자 개선

#### 기존 코드
```python
def get_11st_delivery_company_dropdown_selector(self):
    return '.ant-drawer-body .ant-select:nth-of-type(4) .ant-select-selector'
```

#### 수정된 코드
```python
def get_11st_delivery_company_dropdown_selector(self):
    return '.ant-drawer-body .ant-select .ant-select-selector'
```

### 2. 롯데택배 옵션 선택자 유연화

#### 기존 코드
```python
def get_11st_lotte_delivery_option_selector(self):
    return '.ant-select-dropdown .ant-select-item-option[title="롯데(현대)택배"]'
```

#### 수정된 코드
```python
def get_11st_lotte_delivery_option_selector(self):
    return '.ant-select-dropdown .ant-select-item-option[title*="롯데"]'
```

### 3. 드롭다운 찾기 로직 개선

#### 새로운 접근 방식
1. **라벨 기반 검색**: "출고 택배사" 텍스트를 찾아 해당 드롭다운 식별
2. **선택된 값 기반 검색**: CJ대한통운이나 택배 관련 텍스트가 포함된 드롭다운 찾기
3. **대기 시간 증가**: 드롭다운 클릭 후 2초 대기로 안정성 향상

#### 구현 코드
```python
def select_11st_lotte_delivery_company(self):
    try:
        # 1. 출고 택배사 드롭다운 찾기
        delivery_company_dropdown = None
        
        # 출고 택배사 라벨 다음의 드롭다운 찾기
        try:
            delivery_labels = self.driver.find_elements(By.XPATH, "//div[contains(text(), '출고 택배사')]")
            if delivery_labels:
                parent = delivery_labels[0].find_element(By.XPATH, "./following-sibling::div//div[@class='ant-select-selector']")
                delivery_company_dropdown = parent
        except:
            # 대안: 선택된 값 기준으로 찾기
            dropdowns = self.driver.find_elements(By.CSS_SELECTOR, ".ant-drawer-body .ant-select .ant-select-selector")
            for dropdown in dropdowns:
                try:
                    selected_text = dropdown.find_element(By.CSS_SELECTOR, ".ant-select-selection-item").get_attribute("title")
                    if "CJ" in selected_text or "택배" in selected_text:
                        delivery_company_dropdown = dropdown
                        break
                except:
                    continue
        
        # 2. 드롭다운 클릭 및 옵션 선택
        if delivery_company_dropdown:
            delivery_company_dropdown.click()
            time.sleep(2)  # 대기 시간 증가
            
            lotte_option = self.wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '.ant-select-dropdown .ant-select-item-option[title*="롯데"]')
            ))
            lotte_option.click()
            return True
            
    except Exception as e:
        self.logger.error(f"롯데택배 선택 중 오류 발생: {e}")
        return False
```

## 수정된 메서드 목록

### 1. `get_11st_delivery_company_dropdown_selector()`
- nth-of-type 제거하여 더 일반적인 선택자 사용

### 2. `get_11st_delivery_company_dropdown_arrow_selector()`
- nth-of-type 제거하여 일관성 유지

### 3. `get_11st_lotte_delivery_option_selector()`
- 정확한 매칭에서 부분 매칭(`title*="롯데"`)으로 변경

### 4. `select_11st_lotte_delivery_company()`
- 라벨 기반 드롭다운 찾기 로직 추가
- 선택된 값 기반 대안 로직 추가
- 대기 시간 증가 (1초 → 2초)
- 로그 메시지 개선

### 5. `handle_11st_api_verification_modal()`
- 주석 업데이트: "롯데(현대)택배" → "롯데택배"

## 주요 개선사항

### 1. 안정성 향상
- 다중 검색 전략으로 드롭다운 찾기 성공률 증가
- 대기 시간 증가로 DOM 로딩 완료 보장

### 2. 유연성 증가
- 부분 매칭으로 다양한 롯데택배 옵션 이름 지원
- DOM 구조 변경에 덜 민감한 선택자 사용

### 3. 디버깅 개선
- 상세한 로그 메시지로 문제 진단 용이
- 각 단계별 성공/실패 상태 추적

## 예상 결과

### 성공 시나리오
```
2025-06-22 22:43:49,264 - product_editor_core6_1_dynamic - INFO - API 검증 버튼 클릭 완료
2025-06-22 22:43:50,289 - product_editor_core6_1_dynamic - INFO - 11번가 API 검증 모달창 확인
2025-06-22 22:43:51,300 - product_editor_core6_1_dynamic - INFO - 출고 택배사 드롭다운을 라벨 기준으로 찾음
2025-06-22 22:43:52,350 - product_editor_core6_1_dynamic - INFO - 출고 택배사 드롭다운 클릭
2025-06-22 22:43:54,400 - product_editor_core6_1_dynamic - INFO - 롯데택배 선택 완료
2025-06-22 22:43:55,450 - product_editor_core6_1_dynamic - INFO - 11번가 배송프로필 만들기 버튼 클릭 완료
2025-06-22 22:43:56,500 - product_editor_core6_1_dynamic - INFO - 11번가 API 검증 모달창 처리 완료
```

## 테스트 권장사항

1. **다양한 브라우저 환경에서 테스트**
   - Chrome, Edge, Firefox 등

2. **네트워크 속도별 테스트**
   - 느린 네트워크에서 DOM 로딩 시간 확인

3. **반복 테스트**
   - 연속 실행 시 안정성 확인

4. **오류 시나리오 테스트**
   - 롯데택배 옵션이 없는 경우
   - 드롭다운이 로딩되지 않는 경우

## 관련 파일

- `market_utils.py`: 메인 수정 파일
- `docs/11번가 배송프로필만들기 DOM.md`: DOM 구조 참조
- `docs/11st_api_verification_selector_fix.md`: 이전 선택자 수정 내역