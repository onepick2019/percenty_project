# 드롭다운 선택자 방식 비교 분석

## 개요
5단계에서 7초 지연이 발생하는 반면, 21~33단계에서는 1초 내에 드롭박스를 찾는 이유를 분석하기 위해 각 단계별 dropdown utils의 선택자 방식을 비교했습니다.

## 각 단계별 선택자 방식 비교

### 1. dropdown_utils2.py (21~33단계 상품검색)
**특징**: 매우 단순하고 직접적인 선택자
```python
search_dropdown_selectors = [
    "(//div[contains(@class, 'ant-select-single')])[3]",  # 3번째 드롭박스
    "(//div[contains(@class, 'ant-select-selector')])[3]",
    "//div[contains(@class, 'ant-select-single')][3]"
]
```
- **timeout**: 5초
- **선택자 수**: 3개
- **방식**: 순서 기반 직접 선택
- **성공률**: 높음 (페이지 구조가 일정함)

### 2. dropdown_utils3.py (3단계 개별상품)
**특징**: 테이블 행 기반 정확한 선택자
```python
selectors = [
    f"(//tr[contains(@class, 'ant-table-row')])[{item_index + 1}]//div[contains(@class, 'ant-select-selector')]",
    f"(//tbody//tr)[{item_index + 1}]//div[contains(@class, 'ant-select-selector')]",
    f"(//tr[contains(@class, 'ant-table-row')])[{item_index + 1}]//span[contains(@class, 'ant-select-selection-item')]/parent::div",
    # ... 더 구체적인 선택자들
]
```
- **timeout**: 10초 (하지만 첫 번째 선택자가 대부분 성공)
- **선택자 수**: 7개
- **방식**: 테이블 행 기반 + 위치 지정
- **성공률**: 매우 높음 (테이블 구조가 안정적)

### 3. dropdown_utils4.py (4단계 상품검색)
**특징**: 단순한 순서 기반 선택자
```python
selectors = [
    "(//div[contains(@class, 'ant-select-single')])[1]",  # 1번째 드롭박스
    "(//div[contains(@class, 'ant-select-selector')])[1]",
    "//div[contains(@class, 'ant-select-single')][1]"
]
```
- **timeout**: 10초
- **선택자 수**: 3개
- **방식**: 순서 기반 직접 선택
- **성공률**: 높음

### 4. dropdown_utils5.py (5단계 개별상품) ⚠️ 문제 발생
**특징**: 복잡한 텍스트/클래스 기반 선택자
```python
selectors = [
    "//div[contains(@class, 'ant-select-single')][.//span[contains(text(), '그룹 없음')]]",  # 텍스트 기반
    "//div[contains(@class, 'ant-select-single')][.//span[contains(@class, 'sc-dkmUuB')]]",  # 특정 클래스 기반
    f"(//div[contains(@class, 'ant-select-single') and not(contains(@class, 'ant-select-borderless'))])[position()={item_index + 1}]",
    f"(//div[contains(@class, 'sc-gwZKzw')]//div[contains(@class, 'ant-select-single')])[position()={item_index + 1}]"
]
```
- **timeout**: 2초 (각 선택자당)
- **선택자 수**: 4개
- **방식**: 텍스트/클래스 조건 기반
- **성공률**: 낮음 (복잡한 조건으로 인한 실패)

## 지연 시간 발생 원인 분석

### 1. 선택자 복잡도
- **21~33단계**: 단순한 순서 기반 선택자 → 빠른 탐색
- **5단계**: 복잡한 텍스트/클래스 조건 → 느린 탐색

### 2. 실패 패턴
**5단계에서 발생하는 지연**:
1. 첫 번째 선택자 (텍스트 '그룹 없음' 기반) → 2초 대기 후 실패
2. 두 번째 선택자 (클래스 'sc-dkmUuB' 기반) → 2초 대기 후 실패
3. 세 번째 선택자 (순서 기반) → 약 2.7초 후 성공

**총 지연 시간**: 2 + 2 + 2.7 = 약 6.7초

### 3. 페이지 구조 차이
- **상품검색 드롭박스**: 페이지 로드 시 즉시 사용 가능, 구조 일정
- **개별상품 드롭박스**: 동적 로딩, 텍스트 내용 변동 가능

## 개선 방안

### 1. 즉시 적용 가능한 개선
```python
# 성공률이 높은 선택자를 앞으로 이동
selectors = [
    # 순서 기반 선택자를 첫 번째로
    f"(//div[contains(@class, 'ant-select-single') and not(contains(@class, 'ant-select-borderless'))])[position()={item_index + 1}]",
    # 테이블 행 기반 선택자 추가
    f"(//tr[contains(@class, 'ant-table-row')])[{item_index + 1}]//div[contains(@class, 'ant-select-selector')]",
    # 기존 텍스트 기반 선택자들
    "//div[contains(@class, 'ant-select-single')][.//span[contains(text(), '그룹 없음')]]",
    "//div[contains(@class, 'ant-select-single')][.//span[contains(@class, 'sc-dkmUuB')]]"
]
```

### 2. timeout 조정
```python
# 각 선택자당 timeout을 1초로 단축
for selector in selectors:
    try:
        dropdown_element = WebDriverWait(self.driver, 1).until(  # 2초 → 1초
            EC.element_to_be_clickable((By.XPATH, selector))
        )
        break
    except (TimeoutException, NoSuchElementException):
        continue
```

### 3. 3단계 방식 적용
5단계에서도 3단계처럼 테이블 행 기반 선택자를 우선 사용:
```python
# 3단계에서 성공적으로 사용하는 방식
f"(//tr[contains(@class, 'ant-table-row')])[{item_index + 1}]//div[contains(@class, 'ant-select-selector')]"
```

## 결론

5단계의 7초 지연은 **복잡한 텍스트/클래스 기반 선택자**가 실패하면서 발생하는 것으로, 21~33단계에서 사용하는 **단순한 순서 기반 선택자**나 3단계의 **테이블 행 기반 선택자**를 우선 사용하면 지연 시간을 1초 내로 단축할 수 있습니다.

**핵심 개선점**:
1. 성공률이 높은 선택자를 앞으로 이동
2. 각 선택자당 timeout을 1초로 단축
3. 테이블 행 기반 선택자 우선 사용
4. 텍스트 기반 선택자는 백업으로만 사용