# 마켓별 API KEY 입력 메서드 추가

## 개요

`market_utils.py`에 모든 마켓의 API KEY 입력을 처리하는 통합 메서드들을 추가했습니다. 제공된 DOM 구조를 기반으로 정확한 선택자를 사용하여 안정적인 API KEY 입력 기능을 구현했습니다.

## 추가된 메서드

### 1. 핵심 메서드

#### `get_api_key_input_selector(market_key)`
- **목적**: 마켓별 API KEY 입력창의 정확한 CSS 선택자 반환
- **선택자 패턴**: `div[id="rc-tabs-0-panel-{node_key}"] input[placeholder="미설정"]`
- **특징**: 각 마켓의 탭 패널 내부에서 "미설정" placeholder를 가진 입력창을 정확히 타겟팅

#### `input_api_key(market_key, api_key)`
- **목적**: 모든 마켓에 공통으로 사용되는 API KEY 입력 로직
- **기능**:
  - 마켓 패널 로드 대기
  - 입력창 존재 확인
  - 요소 가시성 및 활성화 상태 검증
  - API KEY 입력 및 로깅

### 2. 마켓별 전용 메서드

| 메서드명 | 대상 마켓 | 마켓 키 |
|---------|-----------|----------|
| `input_11st_general_api_key()` | 11번가-일반 | `11st_general` |
| `input_11st_global_api_key()` | 11번가-글로벌 | `11st_global` |
| `input_coupang_api_key()` | 쿠팡 | `coupang` |
| `input_smartstore_api_key()` | 스마트스토어 | `smartstore` |
| `input_auction_gmarket_api_key()` | 옥션/G마켓 | `auction_gmarket` |
| `input_lotteon_api_key()` | 롯데온 | `lotteon` |
| `input_kakao_api_key()` | 톡스토어 | `kakao` |
| `input_interpark_api_key()` | 인터파크 | `interpark` |
| `input_wemakeprice_api_key()` | 위메프 | `wemakeprice` |

## DOM 구조 분석

제공된 DOM에서 확인된 11번가 API KEY 입력창 구조:

```html
<div class="ant-collapse-content ant-collapse-content-active">
  <div class="ant-collapse-content-box">
    <div class="sc-jDiiQP iMaEUT">
      <div>
        <div class="sc-iJpgEM iTpVtw Body3Regular14 CharacterTitle85">API KEY</div>
        <input placeholder="미설정" class="ant-input css-1li46mu ant-input-outlined sc-gHZEoh fTZxGW Body3Regular14 CharacterTitle85" type="text" value="">
      </div>
    </div>
  </div>
</div>
```

**핵심 식별 요소**:
- `placeholder="미설정"` 속성
- 각 마켓 탭 패널 내부에 위치 (`rc-tabs-0-panel-{market_key}`)
- `type="text"` 속성

## 기존 코드 개선

### `product_editor_core6_1_dynamic.py` 수정

기존의 복잡한 `_input_11st_api_key` 메서드를 단순화:

**Before (58줄)**:
```python
def _input_11st_api_key(self, api_key):
    # 복잡한 선택자 배열과 반복문
    selectors = [9개의 선택자]
    for selector in selectors:
        # 복잡한 시도/오류 처리
```

**After (16줄)**:
```python
def _input_11st_api_key(self, api_key):
    # market_utils의 메서드 활용
    success = self.market_utils.input_11st_general_api_key(api_key)
    return success
```

## 장점

### 1. 코드 재사용성
- 모든 마켓에 동일한 로직 적용
- 중복 코드 제거
- 유지보수 용이성 향상

### 2. 정확성
- DOM 구조 기반의 정확한 선택자
- 마켓별 탭 패널 구분
- 요소 상태 검증 로직

### 3. 안정성
- 패널 로드 대기
- 요소 가시성 확인
- 활성화 상태 검증
- 상세한 오류 로깅

### 4. 확장성
- 새로운 마켓 추가 시 쉬운 확장
- 일관된 인터페이스
- 표준화된 오류 처리

## 사용 예시

```python
# MarketUtils 인스턴스를 통한 사용
market_utils = MarketUtils(driver, wait, logger)

# 11번가 일반 API KEY 입력
success = market_utils.input_11st_general_api_key("your_api_key_here")

# 쿠팡 API KEY 입력
success = market_utils.input_coupang_api_key("your_coupang_api_key")

# 스마트스토어 API KEY 입력
success = market_utils.input_smartstore_api_key("your_smartstore_api_key")
```

## 테스트 권장사항

1. **각 마켓별 테스트**
   - 모든 마켓 탭에서 API KEY 입력 테스트
   - 유효/무효 API KEY로 테스트

2. **오류 상황 테스트**
   - 패널이 로드되지 않은 상태
   - 입력창이 비활성화된 상태
   - 네트워크 지연 상황

3. **통합 테스트**
   - 마켓 설정 전체 워크플로우
   - API 검증과의 연동

## 향후 개선 방향

1. **동적 선택자 지원**
   - DOM 구조 변경에 대응하는 fallback 선택자
   - 자동 선택자 탐지 기능

2. **배치 처리**
   - 여러 마켓 API KEY 일괄 입력
   - 설정 파일 기반 자동 입력

3. **검증 강화**
   - API KEY 형식 검증
   - 실시간 유효성 확인

---

**작성일**: 2024년
**작성자**: AI Assistant
**관련 파일**: 
- `market_utils.py`
- `product_editor_core6_1_dynamic.py`