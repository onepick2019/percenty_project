# 모달창 클릭 간섭 문제 해결 보고서

## 문제 상황

### 발생한 오류 패턴
- **첫 번째 탭**: 항상 정상 동작 (스마트스토어 또는 쿠팡)
- **두 번째 탭**: 모달창 대기 시간 초과 오류
- **세 번째 탭**: `element click intercepted` 오류

### 핵심 오류 메시지
```
element click intercepted: Element <div role="tab"...> is not clickable at point (521, 266). 
Other element would receive the click: <div tabindex="-1" class="ant-modal-wrap ant-modal-centered">...</div>
```

## 근본 원인 분석

### 잘못된 초기 분석
- ❌ **이전 분석**: 모달창이 완전히 닫힐 때까지 기다리지 않아서 발생
- ❌ **실제 문제**: 모달창은 닫혔지만 DOM에서 모달창 요소가 완전히 제거되지 않음

### 실제 문제
1. **DOM 잔여 요소**: 이전 탭에서 처리한 모달창의 DOM 요소(`ant-modal-wrap`, `ant-modal-mask` 등)가 DOM에 남아있음
2. **클릭 가로채기**: 남아있는 모달창 요소가 다음 탭 클릭을 가로채서 `element click intercepted` 오류 발생
3. **순차 처리 특성**: 첫 번째 탭은 모달창 잔여 요소가 없어서 정상 동작, 두 번째 탭부터 간섭 발생

## 해결 방안

### 1. 탭 클릭 전 모달창 간섭 방지

#### `ensure_no_modal_interference()` 메서드 추가
```python
def ensure_no_modal_interference(self):
    """탭 클릭 전에 모달창 간섭을 방지합니다."""
    try:
        # 1. 모달창 래퍼가 DOM에 남아있는지 확인
        modal_wrappers = self.driver.find_elements(By.CSS_SELECTOR, ".ant-modal-wrap")
        if modal_wrappers:
            # 2. JavaScript로 강제 제거
            self.driver.execute_script("""
                var modals = document.querySelectorAll('.ant-modal-wrap, .ant-modal-mask, .ant-modal');
                modals.forEach(function(modal) {
                    if (modal.parentNode) {
                        modal.parentNode.removeChild(modal);
                    }
                });
            """)
            
            # 3. body의 overflow 스타일 복원
            self.driver.execute_script("document.body.style.overflow = 'auto';")
            
        # 4. 일반적인 모달창 닫기도 시도
        self.close_any_open_modal()
```

#### `click_market_tab()` 메서드 수정
```python
def click_market_tab(self, market_key):
    """특정 마켓 탭을 클릭합니다."""
    try:
        # 탭 클릭 전에 남아있는 모달창 확인 및 제거
        self.ensure_no_modal_interference()
        
        selector = self.get_market_tab_selector(market_key)
        element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
        element.click()
```

### 2. 해결 방안의 핵심 포인트

1. **DOM 요소 강제 제거**: JavaScript를 사용하여 남아있는 모달창 관련 DOM 요소를 강제로 제거
2. **스타일 복원**: 모달창이 설정했을 수 있는 `body` 스타일을 복원
3. **예방적 접근**: 탭 클릭 전에 미리 간섭 요소를 제거하여 문제 발생 방지
4. **이중 안전장치**: DOM 강제 제거 + 기존 모달창 닫기 로직 병행

## 예상 효과

### 해결될 문제
- ✅ 두 번째 탭에서 모달창 대기 시간 초과 해결
- ✅ 세 번째 탭에서 `element click intercepted` 오류 해결
- ✅ 모든 탭에서 안정적인 순차 처리 가능

### 개선 사항
- **안정성 향상**: DOM 간섭 요소 사전 제거로 클릭 실패 방지
- **로그 개선**: 모달창 잔여 요소 감지 및 제거 과정 로깅
- **예방적 처리**: 문제 발생 후 대응이 아닌 사전 방지

## 테스트 권장사항

### 1. 기본 시나리오 테스트
- 스마트스토어 → 쿠팡 → 옥션/지마켓 순서로 API 연결 끊기
- 쿠팡 → 스마트스토어 → 옥션/지마켓 순서로 API 연결 끊기
- 다양한 순서 조합으로 테스트

### 2. 확인 포인트
- 모든 탭에서 정상적인 탭 전환 확인
- 모달창 대기 시간 초과 오류 미발생 확인
- `element click intercepted` 오류 미발생 확인
- 로그에서 "모달창 DOM 요소 강제 제거" 메시지 확인

### 3. 추가 테스트
- 빠른 연속 탭 전환 테스트
- 네트워크 지연 상황에서의 안정성 테스트
- 다양한 브라우저 환경에서의 호환성 테스트

## 결론

이번 문제는 모달창의 "닫힘" 상태와 DOM에서의 "완전 제거" 상태가 다르다는 점을 보여주는 사례였습니다. 단순히 모달창이 보이지 않는다고 해서 DOM에서 완전히 제거된 것은 아니며, 이러한 잔여 요소들이 후속 UI 조작에 간섭을 일으킬 수 있습니다.

새로운 해결 방안은 이러한 DOM 간섭을 사전에 방지하여 안정적인 순차 처리를 보장합니다.