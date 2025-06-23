# 모달창 문제 즉시 해결 방안

## 문제 확인

### 현재 모달창 선택자 (전역)
```python
def get_api_disconnect_modal_selector(self):
    return "//div[@class='ant-modal-content']//div[@class='ant-modal-title' and text()='API 연결 끊기']"
```

### 마켓별 패널 구조
```python
self.market_tabs = {
    'coupang': 'cp',
    'smartstore': 'ss', 
    'auction_gmarket': 'esm',
    # ...
}

# 패널 선택자: div[id="rc-tabs-0-panel-{node_key}"]
# 쿠팡: rc-tabs-0-panel-cp
# 스마트스토어: rc-tabs-0-panel-ss
# 옥션/G마켓: rc-tabs-0-panel-esm
```

## 즉시 적용 해결책

### 1. 마켓별 모달창 선택자 구현

**market_utils.py에 추가할 메서드:**

```python
def get_market_specific_modal_selector(self, market_key):
    """마켓별 API 연결 끊기 모달창 선택자를 반환합니다."""
    if market_key not in self.market_tabs:
        # 기존 전역 선택자 사용 (하위 호환성)
        return "//div[@class='ant-modal-content']//div[@class='ant-modal-title' and text()='API 연결 끊기']"
    
    node_key = self.market_tabs[market_key]
    # 특정 마켓 패널 내의 모달창만 선택
    return f"//div[@id='rc-tabs-0-panel-{node_key}']//div[@class='ant-modal-content']//div[@class='ant-modal-title' and text()='API 연결 끊기']"

def force_close_all_modals(self):
    """모든 열린 모달창을 강제로 닫습니다."""
    try:
        # 모든 모달창의 닫기 버튼 찾기
        close_buttons = self.driver.find_elements(By.XPATH, "//div[@class='ant-modal-content']//button[@class='ant-modal-close']")
        
        for button in close_buttons:
            try:
                if button.is_displayed():
                    button.click()
                    time.sleep(0.5)
            except Exception:
                continue
                
        # ESC 키로 모달창 닫기 시도
        try:
            self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
            time.sleep(0.5)
        except Exception:
            pass
            
        self.logger.info("모든 모달창 강제 닫기 완료")
        return True
        
    except Exception as e:
        self.logger.warning(f"모달창 강제 닫기 중 오류: {e}")
        return False

def wait_for_modal_to_disappear(self, market_key=None, timeout=5):
    """모달창이 완전히 사라질 때까지 대기합니다."""
    try:
        if market_key:
            modal_selector = self.get_market_specific_modal_selector(market_key)
        else:
            modal_selector = self.get_api_disconnect_modal_selector()
            
        # 모달창이 사라질 때까지 대기
        WebDriverWait(self.driver, timeout).until_not(
            EC.presence_of_element_located((By.XPATH, modal_selector))
        )
        
        self.logger.info(f"모달창 닫힘 확인 완료 (마켓: {market_key or '전역'})")
        return True
        
    except TimeoutException:
        self.logger.warning(f"모달창 닫힘 대기 시간 초과 (마켓: {market_key or '전역'})")
        return False
    except Exception as e:
        self.logger.error(f"모달창 닫힘 확인 중 오류: {e}")
        return False
```

### 2. 기존 메서드 수정

**handle_api_disconnect_modal 메서드 수정:**

```python
def handle_api_disconnect_modal(self, confirm=True, market_key=None):
    """API 연결 끊기 모달창을 처리합니다."""
    try:
        # 마켓별 모달창 선택자 사용
        if market_key:
            modal_selector = self.get_market_specific_modal_selector(market_key)
        else:
            modal_selector = self.get_api_disconnect_modal_selector()
            
        # 모달창 대기
        modal_element = WebDriverWait(self.driver, 4).until(
            EC.presence_of_element_located((By.XPATH, modal_selector))
        )
        
        self.logger.info(f"API 연결 끊기 모달창 확인 (마켓: {market_key or '전역'})")
        
        # 알림 메시지 확인
        alert_messages = self.get_api_disconnect_modal_alert_messages()
        for message in alert_messages:
            self.logger.info(f"알림: {message}")
        
        # 확인 또는 취소 버튼 클릭
        if confirm:
            success = self.click_api_disconnect_modal_confirm()
            if success:
                # 모달창이 실제로 닫힐 때까지 대기
                self.wait_for_modal_to_disappear(market_key)
            return success
        else:
            return self.click_api_disconnect_modal_cancel()
            
    except TimeoutException:
        self.logger.error(f"API 연결 끊기 모달창 대기 시간 초과 (마켓: {market_key or '전역'})")
        return False
    except Exception as e:
        self.logger.error(f"API 연결 끊기 모달창 처리 중 오류: {e}")
        return False
```

### 3. 마켓별 API 연결 끊기 메서드 수정

**각 마켓의 disconnect 메서드 시작 부분에 추가:**

```python
def disconnect_coupang_api(self):
    """쿠팡 API 연결을 끊습니다."""
    try:
        # 0. 기존 모든 모달창 강제 닫기
        self.force_close_all_modals()
        
        # 1. 쿠팡 탭으로 전환
        if not self.switch_to_market('coupang'):
            return False
        
        # 2. 패널 로드 대기
        if not self.wait_for_market_panel_load('coupang'):
            return False
        
        # 3. API 연결 끊기 버튼 클릭
        if not self.click_api_disconnect_button():
            return False
        
        # 4. 마켓별 모달창 처리
        return self.handle_api_disconnect_modal(confirm=True, market_key='coupang')
        
    except Exception as e:
        self.logger.error(f"쿠팡 API 연결 끊기 중 오류: {e}")
        return False

def disconnect_smartstore_api(self):
    """스마트스토어 API 연결을 끊습니다."""
    try:
        # 0. 기존 모든 모달창 강제 닫기
        self.force_close_all_modals()
        
        # 1. 스마트스토어 탭으로 전환
        if not self.switch_to_market('smartstore'):
            return False
        
        # 2. 패널 로드 대기
        if not self.wait_for_market_panel_load('smartstore'):
            return False
        
        # 3. API 연결 끊기 버튼 클릭
        if not self.click_api_disconnect_button():
            return False
        
        # 4. 마켓별 모달창 처리
        return self.handle_api_disconnect_modal(confirm=True, market_key='smartstore')
        
    except Exception as e:
        self.logger.error(f"스마트스토어 API 연결 끊기 중 오류: {e}")
        return False

def disconnect_auction_gmarket_api(self):
    """옥션/G마켓 API 연결을 끊습니다."""
    try:
        # 0. 기존 모든 모달창 강제 닫기
        self.force_close_all_modals()
        
        # 1. 옥션/G마켓 탭으로 전환
        if not self.switch_to_market('auction_gmarket'):
            return False
        
        # 2. 패널 로드 대기
        if not self.wait_for_market_panel_load('auction_gmarket'):
            return False
        
        # 3. API 연결 끊기 버튼 클릭
        if not self.click_api_disconnect_button():
            return False
        
        # 4. 마켓별 모달창 처리
        return self.handle_api_disconnect_modal(confirm=True, market_key='auction_gmarket')
        
    except Exception as e:
        self.logger.error(f"옥션/G마켓 API 연결 끊기 중 오류: {e}")
        return False
```

## 구현 우선순위

### 1단계: 긴급 수정 (즉시 적용)
1. `force_close_all_modals()` 메서드 추가
2. 각 마켓 disconnect 메서드 시작 시 모달창 정리
3. `wait_for_modal_to_disappear()` 메서드 추가

### 2단계: 선택자 개선 (1-2일 내)
1. `get_market_specific_modal_selector()` 메서드 추가
2. `handle_api_disconnect_modal()` 메서드에 market_key 파라미터 추가
3. 각 마켓별 메서드에서 마켓별 선택자 사용

### 3단계: 검증 및 최적화 (1주일 내)
1. 통합 테스트 실행
2. 로그 분석을 통한 성능 확인
3. 필요시 추가 최적화

## 예상 효과

1. **즉시 해결**: 쿠팡 모달창이 스마트스토어/옥션G마켓에 영향을 주지 않음
2. **안정성 향상**: 각 마켓의 모달창이 독립적으로 처리됨
3. **디버깅 용이**: 마켓별 로그로 문제 추적 가능
4. **유지보수성**: 마켓별 독립적인 처리로 코드 이해도 향상

이 해결책은 기존 코드 구조를 최대한 유지하면서 핵심 문제만 해결하는 최소 침습적 접근법입니다.