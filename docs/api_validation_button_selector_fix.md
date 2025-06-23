# API 검증 버튼 선택자 수정 및 포커스 개선

## 문제 상황

API 검증 버튼을 클릭하려고 했으나 "API 검증 버튼을 찾을 수 없음" 오류가 발생했습니다.

### 로그 분석
```
2025-06-22 23:02:31,464 - product_editor_core6_1_dynamic - INFO - 11번가 API KEY 입력 완료: 2a59718824...
2025-06-22 23:02:31,517 - product_editor_core6_1_dynamic - INFO - 11번가-일반 탭이 이미 활성화되어 있음
2025-06-22 23:02:33,548 - product_editor_core6_1_dynamic - INFO - 11번가-일반 패널 로드 완료
2025-06-22 23:02:43,722 - product_editor_core6_1_dynamic - ERROR - API 검증 버튼을 찾을 수 없음
2025-06-22 23:02:43,723 - product_editor_core6_1_dynamic - ERROR - 11번가 API 검증 실패
```

### 화면 전체 구조 분석 (API검증.md)

11번가-일반 탭의 실제 DOM 구조:
```html
<div class="ant-row css-1li46mu" style="gap: 1rem; margin: 0px 0px 0px auto;">
  <button type="button" class="ant-btn css-1li46mu ant-btn-default">
    <span>API 연결 끊기</span>
  </button>
  <button type="button" class="ant-btn css-1li46mu ant-btn-primary">
    <span>API 검증</span>
  </button>
</div>
```

## 원인 분석

1. **선택자 부정확성**: 기존 선택자가 너무 일반적이어서 정확한 위치의 API 검증 버튼을 찾지 못함
2. **포커스 문제**: API KEY 입력 후 포커스가 버튼 영역으로 이동하지 않아 클릭 실패 가능성
3. **DOM 로딩 타이밍**: 패널 로드 완료 후 버튼이 완전히 렌더링되기까지 추가 시간 필요

## 해결 방안

### 1. 선택자 정확성 개선

**기존 선택자:**
```python
def get_api_validation_button_selector(self):
    """API 검증 버튼 선택자를 반환합니다."""
    return '//button[contains(@class, "ant-btn-primary")]/span[text()="API 검증"]'
```

**개선된 선택자:**
```python
def get_api_validation_button_selector(self):
    """API 검증 버튼 선택자를 반환합니다."""
    return '//div[@class="ant-row css-1li46mu" and contains(@style, "margin: 0px 0px 0px auto")]//button[contains(@class, "ant-btn-primary")]/span[text()="API 검증"]'
```

### 2. 포커스 이동 및 스크롤 개선

**기존 클릭 메서드:**
```python
def click_api_validation_button(self):
    """API 검증 버튼을 클릭합니다."""
    try:
        xpath = self.get_api_validation_button_selector()
        element = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        element.click()
        self.logger.info("API 검증 버튼 클릭 완료")
        time.sleep(1)
        return True
    except TimeoutException:
        self.logger.error("API 검증 버튼을 찾을 수 없음")
        return False
    except Exception as e:
        self.logger.error(f"API 검증 버튼 클릭 중 오류 발생: {e}")
        return False
```

**개선된 클릭 메서드:**
```python
def click_api_validation_button(self):
    """API 검증 버튼을 클릭합니다."""
    try:
        xpath = self.get_api_validation_button_selector()
        element = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        
        # 포커스 이동 및 스크롤
        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        time.sleep(0.5)
        
        # 포커스 설정
        self.driver.execute_script("arguments[0].focus();", element)
        time.sleep(0.5)
        
        element.click()
        self.logger.info("API 검증 버튼 클릭 완료")
        time.sleep(2)  # 모달창 로딩 대기 시간 증가
        return True
    except TimeoutException:
        self.logger.error("API 검증 버튼을 찾을 수 없음")
        return False
    except Exception as e:
        self.logger.error(f"API 검증 버튼 클릭 중 오류 발생: {e}")
        return False
```

## 주요 개선사항

1. **정확한 컨테이너 지정**: `ant-row` 컨테이너의 `margin: 0px 0px 0px auto` 스타일을 포함하여 정확한 위치의 버튼 선택
2. **스크롤 및 포커스**: `scrollIntoView`로 버튼을 화면 중앙으로 이동하고 `focus()` 설정
3. **대기 시간 증가**: 모달창 로딩을 위한 대기 시간을 1초에서 2초로 증가
4. **단계별 대기**: 스크롤과 포커스 설정 사이에 0.5초씩 대기하여 안정성 확보

## 선택자 구체성 분석

### 기존 문제점
- 페이지에 여러 개의 `ant-btn-primary` 버튼이 존재할 수 있음
- "퍼센티에 마켓 연동하기" 버튼도 `ant-btn-primary` 클래스를 사용

### 개선된 접근법
- 특정 컨테이너(`ant-row` with `margin: 0px 0px 0px auto`) 내부의 버튼만 선택
- 이 컨테이너는 "API 연결 끊기"와 "API 검증" 버튼만 포함

## 예상 결과

1. **정확한 버튼 선택**: 11번가-일반 탭의 올바른 API 검증 버튼 클릭
2. **포커스 문제 해결**: API KEY 입력 후 포커스 이동으로 인한 클릭 실패 방지
3. **안정성 향상**: 스크롤, 포커스, 대기 시간 개선으로 클릭 성공률 증가

## 테스트 권장사항

1. **기본 플로우**: API KEY 입력 → API 검증 버튼 클릭 → 모달창 확인
2. **포커스 테스트**: API KEY 입력 후 즉시 API 검증 버튼 클릭 테스트
3. **다른 탭 테스트**: 다른 마켓 탭에서도 동일한 패턴이 적용되는지 확인
4. **전체 워크플로우**: API 검증 → 택배사 선택 → 배송프로필 생성까지 전체 플로우 확인

---

**수정 파일**: `market_utils.py`
**수정 메서드**: 
- `get_api_validation_button_selector()`: 선택자 정확성 개선
- `click_api_validation_button()`: 포커스 이동 및 안정성 개선

**관련 이슈**: API 검증 버튼 선택자 오류 및 포커스 이동 문제