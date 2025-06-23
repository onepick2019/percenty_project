# 11번가 API 검증 플로우 선택자 수정

## 문제 상황
사용자가 11번가 API 검증을 시도했을 때 다음과 같은 오류가 발생했습니다:
```
2025-06-22 18:35:06,968 - product_editor_core6_1_dynamic - ERROR - API 검증 버튼 클릭 중 오류 발생: Message: invalid selector: An invalid or illegal selector was specified
```

## 원인 분석
기존 선택자들이 CSS에서 지원되지 않는 가상 선택자를 사용하고 있었습니다:
- `:contains()` - jQuery 전용 선택자
- `:has()` - 일부 브라우저에서만 지원

## DOM 구조 분석
사용자가 제공한 11번가 배송프로필 모달창의 DOM 구조:
```html
<div class="ant-drawer-content-wrapper" style="width: 378px;">
  <div class="ant-drawer-content" aria-modal="true" role="dialog">
    <div class="ant-drawer-header">
      <div class="ant-drawer-title">11번가 배송 프로필 추가</div>
      <div class="ant-drawer-extra">
        <button type="button" class="ant-btn css-1li46mu ant-btn-primary">
          <span>배송프로필 만들기</span>
        </button>
      </div>
    </div>
    <div class="ant-drawer-body">
      <!-- 출고 택배사 드롭다운 (4번째 .ant-select) -->
      <div class="ant-select ant-select-outlined css-1li46mu ant-select-single ant-select-show-arrow">
        <div class="ant-select-selector">
          <span class="ant-select-selection-item" title="CJ대한통운">CJ대한통운</span>
        </div>
        <span class="ant-select-arrow">...</span>
      </div>
    </div>
  </div>
</div>
```

## 수정된 선택자들

### 1. API 검증 버튼 선택자
**변경 전**:
```css
.ant-btn.ant-btn-primary:not(.ant-btn-background-ghost) span:contains("API 검증")
```

**변경 후**:
```css
button.ant-btn.ant-btn-primary span
```

### 2. 11번가 API 검증 모달창 선택자
**변경 전**:
```css
.ant-drawer-content .ant-drawer-title:contains("11번가 배송 프로필 추가")
```

**변경 후**:
```css
.ant-drawer-content-wrapper
```

### 3. 배송프로필 만들기 버튼 선택자
**변경 전**:
```css
.ant-drawer-extra .ant-btn-primary span:contains("배송프로필 만들기")
```

**변경 후**:
```css
.ant-drawer-extra button.ant-btn.ant-btn-primary
```

### 4. 출고 택배사 드롭다운 선택자
**변경 전**:
```css
.ant-drawer-body .ant-select:has(.ant-select-selection-item[title*="택배"])
```

**변경 후**:
```css
.ant-drawer-body .ant-select:nth-of-type(4) .ant-select-selector
```

### 5. 출고 택배사 드롭다운 화살표 선택자
**변경 전**:
```css
.ant-drawer-body .ant-select:has(.ant-select-selection-item[title*="택배"]) .ant-select-arrow
```

**변경 후**:
```css
.ant-drawer-body .ant-select:nth-of-type(4) .ant-select-arrow
```

### 6. 롯데택배 옵션 선택자 (유지)
```css
.ant-select-dropdown .ant-select-item-option[title="롯데(현대)택배"]
```

## 수정된 메서드들

### market_utils.py
- `get_api_validation_button_selector()`
- `get_11st_api_verification_modal_selector()`
- `get_11st_shipping_profile_create_button_selector()`
- `get_11st_delivery_company_dropdown_selector()`
- `get_11st_delivery_company_dropdown_arrow_selector()`

## 11번가 API 검증 워크플로우

### 현재 구현된 순서
1. **11번가-일반 탭으로 전환** (`switch_to_market('11st_general')`)
2. **패널 로드 대기** (`wait_for_market_panel_load('11st_general')`)
3. **API 검증 버튼 클릭** (`click_api_validation_button()`)
4. **API 검증 모달창 처리** (`handle_11st_api_verification_modal()`)
   - 모달창 대기 (`wait_for_11st_api_verification_modal()`)
   - 롯데(현대)택배 선택 (`select_11st_lotte_delivery_company()`)
   - 배송프로필 만들기 버튼 클릭 (`click_11st_shipping_profile_create_button()`)

## 주요 개선사항

### 1. CSS 표준 준수
- `:contains()`, `:has()` 등 비표준 선택자 제거
- 모든 브라우저에서 지원되는 표준 CSS 선택자 사용

### 2. 정확한 요소 타겟팅
- DOM 구조 분석을 통한 정확한 선택자 작성
- `nth-of-type()` 사용으로 특정 드롭다운 정확히 선택

### 3. 안정성 향상
- 선택자 오류로 인한 실행 중단 방지
- 더 구체적이고 안정적인 선택자 사용

## 예상 결과
이제 11번가 API 검증 플로우가 다음과 같이 정상 동작할 것입니다:
1. ✅ API 검증 버튼 클릭 성공
2. ✅ 배송프로필 모달창 열림 감지
3. ✅ 출고 택배사 드롭다운에서 롯데택배 선택
4. ✅ 배송프로필 만들기 버튼 클릭으로 모달창 닫힘

## 테스트 권장사항
1. **기본 플로우 테스트**: API KEY 입력 → API 검증 → 택배사 선택 → 배송프로필 생성
2. **선택자 검증**: 각 단계별 요소 존재 여부 확인
3. **오류 처리**: 타임아웃 및 예외 상황 테스트

## 향후 개선 방향
1. **동적 선택자**: DOM 변경에 더 유연하게 대응할 수 있는 선택자 전략
2. **요소 대기**: 더 정교한 요소 로드 대기 로직
3. **오류 복구**: 선택자 실패 시 대체 선택자 시도