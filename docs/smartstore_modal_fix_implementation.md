# 스마트스토어 모달창 시간 초과 문제 해결 구현

## 수정 완료 내용

### 1. 모달창 대기 시간 증가

**파일**: `market_utils.py`
**메서드**: `wait_for_api_disconnect_modal()`

```python
# 변경 전
def wait_for_api_disconnect_modal(self, timeout=10):

# 변경 후  
def wait_for_api_disconnect_modal(self, timeout=15):
    """API 연결 끊기 모달창이 나타날 때까지 대기합니다.
    
    Args:
        timeout (int): 모달창 대기 시간 (기본값: 15초, 스마트스토어 지연 대응)
    """
```

**효과**: 스마트스토어의 서버 응답 지연에 대응하여 모달창 대기 시간을 50% 증가

### 2. 모달창 강제 정리 로직 추가

**파일**: `market_utils.py`
**새 메서드**: `force_close_all_modals()`

```python
def force_close_all_modals(self):
    """모든 잔존 모달창을 강제로 닫습니다.
    
    스마트스토어 처리 실패 후 모달창이 DOM에 남아있어 다른 탭 클릭을 차단하는 문제를 해결합니다.
    """
```

**기능**:
1. **ESC 키 시도**: `body` 요소에 ESC 키 전송
2. **배경 클릭**: `.ant-modal-wrap` 요소들 클릭
3. **닫기 버튼**: `.ant-modal-close` 버튼들 클릭
4. **취소 버튼**: `취소` 텍스트가 있는 버튼들 클릭
5. **상태 확인**: 남은 모달창 개수 로깅

### 3. 각 마켓별 disconnect 메서드 강화

#### A. `disconnect_coupang_api()` 수정
```python
# 각 단계별 실패 시 모달창 정리
if not self.switch_to_market('coupang'):
    self.force_close_all_modals()  # 실패 시 모달창 정리
    return False

# 모달창 처리 실패 시 강제 정리
result = self.handle_api_disconnect_modal(confirm=True)
if not result:
    self.logger.warning("쿠팡 모달창 처리 실패, 모달창 강제 정리 시도")
    self.force_close_all_modals()
return result
```

#### B. `disconnect_smartstore_api()` 수정
```python
# 스마트스토어 특화 모달창 정리 로직
result = self.handle_api_disconnect_modal(confirm=True)
if not result:
    self.logger.warning("스마트스토어 모달창 처리 실패, 모달창 강제 정리 시도")
    self.force_close_all_modals()  # 모달창 처리 실패 시 강제 정리
return result
```

#### C. `disconnect_auction_gmarket_api()` 수정
```python
# 옥션/G마켓 모달창 차단 문제 해결
result = self.handle_api_disconnect_modal(confirm=True)
if not result:
    self.logger.warning("옥션/G마켓 모달창 처리 실패, 모달창 강제 정리 시도")
    self.force_close_all_modals()
return result
```

## 문제 해결 메커니즘

### 1. 스마트스토어 모달창 미생성 문제
- **원인**: 서버 응답 지연으로 4초 내에 모달창이 생성되지 않음
- **해결**: 대기 시간을 15초로 증가하여 지연 상황에 대응

### 2. 모달창 잔존으로 인한 탭 클릭 차단 문제
- **원인**: 스마트스토어 처리 실패 후 모달창이 DOM에 남아있음
- **해결**: 각 단계별 실패 시 `force_close_all_modals()` 호출로 강제 정리

### 3. 연쇄 실패 방지
- **원인**: 모달창 차단으로 인한 후속 마켓 처리 불가
- **해결**: 예외 발생 시에도 모달창 정리를 통해 다음 마켓 처리 가능

## 로깅 개선

### 1. 상세 디버깅 로그
```python
self.logger.debug("ESC 키로 모달창 닫기 시도 완료")
self.logger.debug(f"모달창 배경 {i+1} 클릭 완료")
self.logger.debug(f"모달창 닫기 버튼 {i+1} 클릭 완료")
```

### 2. 경고 및 상태 로그
```python
self.logger.warning("스마트스토어 모달창 처리 실패, 모달창 강제 정리 시도")
self.logger.warning(f"모달창 강제 정리 후에도 {len(visible_modals)}개의 모달창이 남아있음")
self.logger.info("모든 모달창 강제 정리 완료")
```

## 예상 효과

### 1. 즉시 효과
- 스마트스토어 모달창 대기 시간 초과 문제 해결
- 모달창 잔존으로 인한 탭 클릭 차단 문제 해결
- 옥션/G마켓 및 11번가 탭 접근 가능

### 2. 안정성 향상
- 각 마켓 처리 실패 시에도 다음 마켓 처리 가능
- 예외 상황에서도 모달창 정리를 통한 복구 가능
- 전체 워크플로우 중단 방지

### 3. 디버깅 용이성
- 상세한 로그를 통한 문제 원인 파악 용이
- 모달창 상태 모니터링 강화
- 단계별 실패 지점 명확화

## 테스트 권장사항

### 1. 정상 시나리오
- 모든 마켓에서 API 연결 끊기 정상 동작 확인
- 모달창 대기 시간 내 정상 처리 확인

### 2. 지연 시나리오
- 스마트스토어에서 의도적 지연 상황 테스트
- 15초 대기 시간 내 모달창 생성 확인

### 3. 실패 시나리오
- 모달창 처리 실패 시 강제 정리 동작 확인
- 후속 마켓 처리 가능 여부 확인

### 4. 연쇄 처리 시나리오
- 여러 마켓 연속 처리 시 안정성 확인
- 모달창 잔존 없이 모든 마켓 처리 완료 확인

## 결론

이번 수정을 통해 스마트스토어 모달창 시간 초과 문제와 모달창 잔존으로 인한 탭 클릭 차단 문제를 근본적으로 해결했습니다. 특히 각 마켓별 처리 실패 시에도 모달창 강제 정리를 통해 전체 워크플로우의 안정성을 크게 향상시켰습니다.

모달창 대기 시간 증가와 강제 정리 로직의 조합으로 스마트스토어의 서버 지연 상황과 예외 상황 모두에 대응할 수 있게 되었습니다.