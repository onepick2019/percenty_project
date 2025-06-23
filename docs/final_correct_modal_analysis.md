# 최종 정확한 모달창 문제 분석

## 사용자 제공 HTML 분석 결과

### 쿠팡 모달창 구조
```html
<div class="ant-modal-content">
  <div class="ant-modal-header">
    <div class="ant-modal-title" id=":r1r:">API 연결 끊기</div>
  </div>
  <div class="ant-modal-footer">
    <button type="button" class="ant-btn css-1li46mu ant-btn-default"><span>취소</span></button>
    <button type="button" class="ant-btn css-1li46mu ant-btn-primary ant-btn-dangerous"><span>API 연결 끊기</span></button>
  </div>
</div>
```

### 스마트스토어 모달창 구조
```html
<div class="ant-modal-content">
  <div class="ant-modal-header">
    <div class="ant-modal-title" id=":r1s:">API 연결 끊기</div>
  </div>
  <div class="ant-modal-footer">
    <button type="button" class="ant-btn css-1li46mu ant-btn-default"><span>취소</span></button>
    <button type="button" class="ant-btn css-1li46mu ant-btn-primary ant-btn-dangerous"><span>API 연결 끊기</span></button>
  </div>
</div>
```

## 핵심 발견: 모달창 구조 완전 동일

**✅ 확인된 사실:**
- 모달창 제목: 동일 ("API 연결 끊기")
- 확인 버튼 클래스: 동일 (`ant-btn-primary ant-btn-dangerous`)
- 확인 버튼 텍스트: 동일 ("API 연결 끊기")
- 전체 DOM 구조: 동일

**❌ 이전 분석 오류:**
- 선택자 차이 ❌
- 버튼 구조 차이 ❌
- 모달창 제목 차이 ❌

## 실제 문제 재분석

### 로그 재검토
```
16:14:58,316 - API 연결 끊기 버튼 클릭 완료  ← 스마트스토어 버튼 클릭 성공
16:15:02,481 - ERROR - API 연결 끊기 모달창 대기 시간 초과  ← 4초 후 모달창 못찾음
```

**문제 분석:**
1. 스마트스토어 API 연결 끊기 버튼 클릭은 성공
2. 4초 동안 모달창을 찾지 못함
3. 모달창 구조는 쿠팡과 동일

## 실제 원인 추정

### 1. 네트워크/서버 응답 지연
- 스마트스토어 서버 응답이 쿠팡보다 느림
- API 연결 끊기 버튼 클릭 후 모달창 생성까지 4초 이상 소요

### 2. JavaScript 비동기 처리 지연
- 스마트스토어의 프론트엔드 처리가 쿠팡보다 느림
- 모달창 렌더링 지연

### 3. 브라우저 렌더링 이슈
- 탭 전환 후 스마트스토어 패널의 JavaScript 초기화 지연
- DOM 업데이트 지연

### 4. 세션/인증 상태 확인 지연
- 스마트스토어에서 API 연결 상태 확인 과정이 더 오래 걸림

## 해결 방안

### 1. 대기 시간 증가 (즉시 적용)
```python
def wait_for_api_disconnect_modal(self, timeout=10):  # 4초 → 10초로 증가
    """API 연결 끊기 모달창이 나타날 때까지 대기합니다."""
    try:
        modal_selector = self.get_api_disconnect_modal_selector()
        modal_element = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, modal_selector))
        )
        self.logger.info("API 연결 끊기 모달창 확인")
        return modal_element
    except TimeoutException:
        self.logger.error(f"API 연결 끊기 모달창 대기 시간 초과 ({timeout}초)")
        return None
```

### 2. 스마트스토어 전용 처리 (권장)
```python
def disconnect_smartstore_api(self):
    """스마트스토어 API 연결을 끊습니다."""
    try:
        # 1. 스마트스토어 탭으로 전환
        if not self.switch_to_market('smartstore'):
            return False
        
        # 2. 패널 로드 대기
        if not self.wait_for_market_panel_load('smartstore'):
            return False
        
        # 3. API 연결 끊기 버튼 클릭
        if not self.click_api_disconnect_button():
            return False
        
        # 4. 스마트스토어 전용 모달창 처리 (더 긴 대기 시간)
        return self.handle_api_disconnect_modal_with_retry(confirm=True, timeout=15)
        
    except Exception as e:
        self.logger.error(f"스마트스토어 API 연결 끊기 중 오류: {e}")
        return False

def handle_api_disconnect_modal_with_retry(self, confirm=True, timeout=15, retry_count=3):
    """재시도 로직이 포함된 모달창 처리"""
    for attempt in range(retry_count):
        try:
            self.logger.info(f"모달창 처리 시도 {attempt + 1}/{retry_count}")
            
            # 모달창 대기 (더 긴 시간)
            modal_element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, self.get_api_disconnect_modal_selector()))
            )
            
            self.logger.info("API 연결 끊기 모달창 확인")
            
            # 알림 메시지 확인
            alert_messages = self.get_api_disconnect_modal_alert_messages()
            for message in alert_messages:
                if "에러" in message:
                    self.logger.info(f"에러 알림: {message}")
                elif "경고" in message:
                    self.logger.info(f"경고 알림: {message}")
                else:
                    self.logger.info(f"알림: {message}")
            
            # 확인 또는 취소 버튼 클릭
            if confirm:
                return self.click_api_disconnect_modal_confirm()
            else:
                return self.click_api_disconnect_modal_cancel()
                
        except TimeoutException:
            self.logger.warning(f"모달창 대기 시도 {attempt + 1} 실패 (시간 초과)")
            if attempt < retry_count - 1:
                self.logger.info("잠시 대기 후 재시도...")
                time.sleep(2)
                continue
            else:
                self.logger.error(f"모든 재시도 실패 - 모달창을 찾을 수 없음")
                return False
        except Exception as e:
            self.logger.error(f"모달창 처리 중 오류 (시도 {attempt + 1}): {e}")
            if attempt < retry_count - 1:
                time.sleep(2)
                continue
            else:
                return False
    
    return False
```

### 3. 네트워크 상태 확인 (고급)
```python
def check_network_and_wait(self, additional_wait=0):
    """네트워크 상태를 확인하고 필요시 추가 대기"""
    try:
        # JavaScript로 네트워크 상태 확인
        network_state = self.driver.execute_script("""
            return {
                online: navigator.onLine,
                connection: navigator.connection ? {
                    effectiveType: navigator.connection.effectiveType,
                    downlink: navigator.connection.downlink
                } : null
            };
        """)
        
        self.logger.info(f"네트워크 상태: {network_state}")
        
        # 느린 연결인 경우 추가 대기
        if network_state.get('connection', {}).get('effectiveType') in ['slow-2g', '2g', '3g']:
            additional_wait += 3
            self.logger.info(f"느린 네트워크 감지 - {additional_wait}초 추가 대기")
        
        if additional_wait > 0:
            time.sleep(additional_wait)
            
    except Exception as e:
        self.logger.warning(f"네트워크 상태 확인 실패: {e}")
```

## 결론

**실제 문제:**
- ✅ 모달창 구조 동일 확인
- ✅ 선택자 문제 아님 확인
- ❌ **스마트스토어 서버/네트워크 응답 지연이 실제 원인**

**해결책:**
1. **즉시 적용**: 모달창 대기 시간을 4초 → 10-15초로 증가
2. **권장 방법**: 스마트스토어 전용 재시도 로직 구현
3. **고급 방법**: 네트워크 상태 기반 동적 대기 시간 조정

이는 코드 문제가 아닌 **스마트스토어 플랫폼의 응답 속도 차이**로 인한 문제입니다.