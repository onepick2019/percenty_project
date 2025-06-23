# 스마트스토어 모달창 시간 초과 문제 분석

## 로그 분석 결과

### 1. 쿠팡 처리 (정상)
```
16:56:33,504 - API 연결 끊기 버튼 클릭 완료
16:56:35,556 - API 연결 끊기 모달창 확인  ← 모달창이 정상적으로 열림
16:56:35,629 - API 연결 끊기 모달창 확인 버튼 클릭 완료
16:56:36,629 - coupang API 연결 끊기 성공
```

### 2. 스마트스토어 처리 (실패)
```
16:56:40,938 - API 연결 끊기 버튼 클릭 완료
16:56:45,078 - API 연결 끊기 모달창 대기 시간 초과  ← 모달창이 열리지 않음
16:56:45,079 - smartstore API 연결 끊기 실패
```

### 3. 후속 문제 (모달창 잔존으로 인한 클릭 차단)
```
16:56:47,179 - element click intercepted: Other element would receive the click: 
<div tabindex="-1" class="ant-modal-wrap ant-modal-centered">  ← 모달창이 화면을 가림
```

## 문제 분석

### 핵심 문제점
1. **스마트스토어 모달창 미생성**: API 연결 끊기 버튼 클릭 후 모달창이 4초 동안 나타나지 않음
2. **모달창 잔존**: 스마트스토어 처리 실패 후에도 모달창이 DOM에 남아있어 다른 탭 클릭을 차단
3. **연쇄 실패**: 모달창 차단으로 인해 옥션/G마켓 및 11번가 탭 접근 불가

### 쿠팡 vs 스마트스토어 차이점
- **쿠팡**: 버튼 클릭 → 2초 후 모달창 생성 → 정상 처리
- **스마트스토어**: 버튼 클릭 → 4초 대기 → 모달창 미생성 → 시간 초과

## 원인 추정

### 1. 스마트스토어 서버 응답 지연
- 네트워크 지연 또는 서버 처리 시간 증가
- API 연결 상태 확인 과정에서 지연 발생

### 2. JavaScript 비동기 처리 지연
- 스마트스토어 특정 로직에서 모달창 생성 지연
- 브라우저 렌더링 성능 이슈

### 3. 세션/인증 상태 문제
- 스마트스토어 세션 만료 또는 인증 토큰 갱신 지연
- API 연결 상태 검증 과정에서 추가 시간 소요

## 해결 방안

### 1. 즉시 적용 가능한 해결책

#### A. 모달창 대기 시간 증가
```python
def wait_for_api_disconnect_modal(self, timeout=15):  # 4초 → 15초로 증가
    """API 연결 끊기 모달창이 나타날 때까지 대기합니다."""
```

#### B. 스마트스토어 전용 재시도 로직
```python
def disconnect_smartstore_api(self):
    """스마트스토어 API 연결을 끊습니다."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # 기존 로직 수행
            if self.handle_api_disconnect_modal_with_retry():
                return True
        except Exception as e:
            if attempt < max_retries - 1:
                self.logger.warning(f"스마트스토어 API 연결 끊기 재시도 {attempt + 1}/{max_retries}")
                time.sleep(2)
            else:
                self.logger.error(f"스마트스토어 API 연결 끊기 최종 실패: {e}")
    return False
```

#### C. 모달창 강제 정리 로직
```python
def force_close_all_modals(self):
    """모든 잔존 모달창을 강제로 닫습니다."""
    try:
        # ESC 키로 모달창 닫기
        self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
        time.sleep(0.5)
        
        # 모달창 배경 클릭으로 닫기
        modal_backgrounds = self.driver.find_elements(By.CSS_SELECTOR, '.ant-modal-wrap')
        for bg in modal_backgrounds:
            try:
                bg.click()
                time.sleep(0.3)
            except:
                pass
                
        self.logger.info("모든 모달창 강제 정리 완료")
    except Exception as e:
        self.logger.warning(f"모달창 강제 정리 중 오류: {e}")
```

### 2. 장기적 개선 방안

#### A. 네트워크 상태 기반 동적 대기 시간
```python
def get_dynamic_timeout(self, market_key):
    """마켓별 네트워크 상태에 따른 동적 대기 시간을 반환합니다."""
    base_timeout = 4
    if market_key == 'smartstore':
        # 스마트스토어는 기본적으로 더 긴 대기 시간 적용
        return base_timeout * 3  # 12초
    return base_timeout
```

#### B. 모달창 상태 모니터링
```python
def monitor_modal_state(self, timeout=15):
    """모달창 상태를 지속적으로 모니터링합니다."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        # 모달창 존재 여부 확인
        if self.is_modal_present():
            return True
        # 에러 메시지 확인
        if self.check_for_error_messages():
            return False
        time.sleep(0.5)
    return False
```

## 구현 우선순위

### Phase 1 (즉시 적용)
1. 모달창 대기 시간을 4초에서 15초로 증가
2. 각 마켓 처리 후 모달창 강제 정리 로직 추가
3. 스마트스토어 전용 재시도 로직 구현

### Phase 2 (단기 개선)
1. 마켓별 동적 대기 시간 적용
2. 모달창 상태 모니터링 강화
3. 에러 상황별 세분화된 처리 로직

### Phase 3 (장기 개선)
1. 네트워크 상태 기반 적응형 대기 시간
2. 마켓별 특화된 처리 로직
3. 포괄적인 에러 복구 메커니즘

## 결론

스마트스토어에서 모달창이 생성되지 않는 문제는 서버 응답 지연이 주요 원인으로 추정됩니다. 즉시 적용 가능한 해결책으로 대기 시간 증가와 모달창 강제 정리 로직을 구현하여 문제를 해결할 수 있습니다.

특히 모달창 잔존으로 인한 후속 탭 클릭 차단 문제는 각 마켓 처리 후 모달창을 강제로 정리하는 로직을 추가하여 해결할 수 있습니다.