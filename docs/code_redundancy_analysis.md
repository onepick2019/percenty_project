# 코드 중복성 분석 및 개선 방안

## 문제 상황

사용자가 지적한 대로, 현재 `market_utils.py`에는 불필요한 코드 중복이 존재합니다:

### 1. 중복된 API 연결 끊기 메서드들

**개별 마켓 메서드들 (필요한 메서드들):**
- `disconnect_coupang_api()`
- `disconnect_smartstore_api()`
- `disconnect_auction_gmarket_api()`

**불필요한 통합 메서드:**
- `perform_complete_api_disconnect_workflow(market_key, confirm=True)`
- `perform_market_setup_workflow(market_key, action='validate')`

### 2. 코드 중복 분석

각 개별 마켓 메서드들은 모두 동일한 패턴을 따릅니다:
```python
def disconnect_[market]_api(self):
    # 1. 마켓 탭으로 전환
    if not self.switch_to_market('[market]'):
        return False
    
    # 2. 패널 로드 대기
    if not self.wait_for_market_panel_load('[market]'):
        return False
    
    # 3. API 연결 끊기 버튼 클릭
    if not self.click_api_disconnect_button():
        return False
    
    # 4. 모달창 처리
    return self.handle_api_disconnect_modal(confirm=True)
```

`perform_complete_api_disconnect_workflow` 메서드도 정확히 동일한 로직을 수행합니다.

### 3. 현재 사용 현황

`perform_complete_api_disconnect_workflow`는 `product_editor_core6_1_dynamic.py`에서 한 곳에서만 사용됩니다:
```python
for market in markets_to_disconnect:
    self.market_utils.perform_complete_api_disconnect_workflow(market, confirm=True)
```

## 문제점

1. **코드 중복**: 동일한 로직이 여러 메서드에 반복됨
2. **유지보수성 저하**: 로직 변경 시 여러 곳을 수정해야 함
3. **불필요한 복잡성**: 단순한 작업에 과도한 추상화
4. **DRY 원칙 위반**: Don't Repeat Yourself 원칙에 어긋남

## 개선 방안

### 1. 즉시 개선 (권장)

**A. 불필요한 메서드 제거**
- `perform_complete_api_disconnect_workflow` 메서드 삭제
- `perform_market_setup_workflow` 메서드 검토 후 필요시 삭제

**B. 사용처 수정**
`product_editor_core6_1_dynamic.py`의 코드를 다음과 같이 수정:
```python
for market in markets_to_disconnect:
    try:
        logger.info(f"{market} API 연결 끊기 시도")
        if market == 'coupang':
            self.market_utils.disconnect_coupang_api()
        elif market == 'smartstore':
            self.market_utils.disconnect_smartstore_api()
        elif market == 'auction_gmarket':
            self.market_utils.disconnect_auction_gmarket_api()
        time.sleep(1)
    except Exception as e:
        logger.warning(f"{market} API 연결 끊기 중 오류 (무시하고 계속): {e}")
        continue
```

### 2. 장기적 개선 (선택사항)

만약 정말 통합 메서드가 필요하다면, 다음과 같이 단순화:
```python
def disconnect_market_api(self, market_key):
    """마켓별 API 연결 끊기 메서드를 호출합니다."""
    disconnect_methods = {
        'coupang': self.disconnect_coupang_api,
        'smartstore': self.disconnect_smartstore_api,
        'auction_gmarket': self.disconnect_auction_gmarket_api
    }
    
    if market_key in disconnect_methods:
        return disconnect_methods[market_key]()
    else:
        self.logger.error(f"지원하지 않는 마켓: {market_key}")
        return False
```

## 결론

사용자의 지적이 정확합니다. 현재 구조는 불필요한 복잡성을 추가하고 있으며, 각 마켓별 개별 메서드만으로도 충분히 기능을 수행할 수 있습니다. 

**권장사항:**
1. `perform_complete_api_disconnect_workflow` 메서드 삭제
2. 사용처에서 직접 개별 마켓 메서드 호출
3. 코드 단순화 및 유지보수성 향상

이러한 개선을 통해 코드의 가독성과 유지보수성을 크게 향상시킬 수 있습니다.