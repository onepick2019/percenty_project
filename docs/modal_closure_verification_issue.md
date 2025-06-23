# 모달창 닫힘 확인 문제 분석 및 해결방안

## 문제 상황

### 로그 분석
```
2025-06-22 16:14:53,041 - API 연결 끊기 모달창 확인 버튼 클릭 완료
2025-06-22 16:14:55,042 - smartstore API 연결 끊기 시도
2025-06-22 16:15:02,481 - API 연결 끊기 모달창 대기 시간 초과
2025-06-22 16:15:04,565 - 마켓 탭 클릭 중 오류 발생: element click intercepted: Other element would receive the click: <div tabindex="-1" class="ant-modal-wrap ant-modal-centered">...</div>
```

### 문제 분석
1. **쿠팡 모달창 확인 버튼 클릭 완료** 후 모달창이 완전히 닫히지 않음
2. **스마트스토어 탭 전환 시** 여전히 열려있는 모달창으로 인해 탭 클릭이 차단됨
3. **옥션/G마켓 탭 전환 시**도 동일한 모달창 차단 문제 발생

## 근본 원인

### 1. 모달창 닫힘 확인 로직 부재
- `click_api_disconnect_modal_confirm` 메서드에서 확인 버튼 클릭 후 모달창이 실제로 닫혔는지 확인하지 않음
- `time.sleep(1)` 만으로는 모달창 닫힘을 보장할 수 없음

### 2. 비동기 모달창 처리
- 모달창 확인 버튼 클릭 후 서버 응답 대기 시간이 필요할 수 있음
- 네트워크 지연이나 서버 처리 시간으로 인해 모달창이 즉시 닫히지 않을 수 있음

### 3. 마켓별 독립 메서드와 공통 메서드의 혼재
- `disconnect_coupang_api`, `disconnect_smartstore_api` 등 마켓별 독립 메서드 존재
- `perform_market_setup_workflow`에서는 공통 `handle_api_disconnect_modal` 사용
- 두 방식이 혼재되어 일관성 부족

## 해결방안

### 1. 모달창 닫힘 확인 로직 추가
```python
def click_api_disconnect_modal_confirm(self):
    """API 연결 끊기 모달창에서 확인 버튼을 클릭하고 모달창이 닫힐 때까지 대기합니다."""
    try:
        # 기존 확인 버튼 클릭 로직...
        
        # 모달창이 닫힐 때까지 대기
        self.wait_for_modal_to_close()
        
        return True
    except Exception as e:
        self.logger.error(f"모달창 확인 버튼 클릭 및 닫힘 대기 중 오류: {e}")
        return False

def wait_for_modal_to_close(self, timeout=10):
    """모달창이 완전히 닫힐 때까지 대기합니다."""
    try:
        # 모달창이 사라질 때까지 대기
        WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located((By.XPATH, "//div[contains(@class, 'ant-modal-wrap')]"))
        )
        self.logger.info("모달창 닫힘 확인 완료")
        return True
    except TimeoutException:
        self.logger.warning("모달창 닫힘 대기 시간 초과")
        return False
```

### 2. 강제 모달창 닫기 로직 추가
```python
def force_close_any_modal(self):
    """열려있는 모든 모달창을 강제로 닫습니다."""
    try:
        # ESC 키로 모달창 닫기
        self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
        time.sleep(0.5)
        
        # X 버튼으로 모달창 닫기
        close_buttons = self.driver.find_elements(By.XPATH, "//button[contains(@class, 'ant-modal-close')]")
        for button in close_buttons:
            if button.is_displayed():
                button.click()
                time.sleep(0.5)
                
        return True
    except Exception as e:
        self.logger.warning(f"강제 모달창 닫기 중 오류: {e}")
        return False
```

### 3. 마켓별 독립 메서드 통일화
- 모든 마켓이 동일한 플로우를 사용하도록 통일
- `perform_market_setup_workflow` 사용을 지양하고 마켓별 독립 메서드 사용 권장

## 권장 구현 순서

1. **모달창 닫힘 확인 로직 추가** (최우선)
2. **강제 모달창 닫기 로직 추가** (안전장치)
3. **마켓별 독립 메서드 통일화** (장기적 개선)

## 테스트 시나리오

1. 쿠팡 API 연결 끊기 → 모달창 완전 닫힘 확인
2. 스마트스토어 탭 전환 → 정상 클릭 확인
3. 옥션/G마켓 탭 전환 → 정상 클릭 확인
4. 연속 API 연결 끊기 작업 → 모든 단계 정상 동작 확인