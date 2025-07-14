# GUI 주기적 실행 중복 브라우저 문제 해결 구현

## 문제 요약
- GUI 주기적 실행에서 3단계 9개 스텝 추가 후 중복 브라우저 실행 발생
- 배치 작업 시작 후 얼마 지나지 않아 새로운 브라우저가 열리고 동일한 작업이 중복 수행

## 구현된 해결 방안

### 1. 스케줄러 레벨 중복 실행 방지 강화

**파일**: `core/periodic_execution_manager.py` - `ScheduleManager` 클래스

#### 추가된 속성
```python
class ScheduleManager:
    def __init__(self):
        # ...
        self.is_callback_running = False  # 콜백 실행 상태 추적
        self.last_execution_time = None   # 마지막 실행 시간 추적
```

#### 안전한 콜백 래퍼 구현
```python
def start_daily_schedule(self, time_str: str, callback: Callable):
    # 안전한 콜백 래퍼 생성 (중복 실행 방지)
    def safe_callback():
        # 1. 이미 실행 중인지 확인
        if self.is_callback_running:
            logger.warning("이전 주기적 실행이 아직 진행 중입니다. 중복 실행을 방지합니다.")
            return
        
        # 2. 최근 실행 시간 확인 (1시간 이내 중복 실행 방지)
        current_time = datetime.now()
        if self.last_execution_time:
            time_diff = current_time - self.last_execution_time
            if time_diff.total_seconds() < 3600:  # 1시간
                logger.warning(f"최근 실행 후 {time_diff.total_seconds():.0f}초 경과. 중복 실행을 방지합니다.")
                return
        
        # 3. 콜백 실행 상태 설정 및 실행
        self.is_callback_running = True
        self.last_execution_time = current_time
        
        try:
            logger.info(f"주기적 실행 시작: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
            callback()
            logger.info(f"주기적 실행 완료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as e:
            logger.error(f"주기적 실행 중 오류: {e}")
        finally:
            # 실행 상태 해제
            self.is_callback_running = False
```

**효과**:
- 스케줄러가 동일한 시간에 여러 번 콜백을 호출하더라도 중복 실행 방지
- 1시간 이내 중복 실행 완전 차단
- 실행 상태 추적을 통한 안전한 동시성 제어

### 2. 프로세스 상태 기반 중복 실행 방지

**파일**: `core/periodic_execution_manager.py` - `_execute_periodic_batch` 메서드

```python
def _execute_periodic_batch(self) -> bool:
    if self.is_executing:
        self._log("이미 실행 중입니다. 중복 실행을 방지합니다.")
        return False
    
    # 실행 중인 프로세스가 있으면 중복 실행 방지
    with self.process_lock:
        if self.running_processes:
            active_processes = [p for p in self.running_processes if p.poll() is None]
            if active_processes:
                self._log(f"실행 중인 프로세스 {len(active_processes)}개가 있습니다. 중복 실행을 방지합니다.")
                return False
    
    self.is_executing = True
```

**효과**:
- 실제 실행 중인 프로세스 존재 시 새로운 실행 차단
- 프로세스 레벨에서의 이중 안전장치 제공
- 타임아웃으로 인한 좀비 프로세스 상황에서도 중복 실행 방지

### 3. 스케줄 중지 시 상태 초기화

**파일**: `core/periodic_execution_manager.py` - `stop_schedule` 메서드

```python
def stop_schedule(self):
    # ...
    # 콜백 실행 상태 초기화
    self.callback_function = None
    self.is_callback_running = False
    self.last_execution_time = None
```

**효과**:
- 스케줄 중지 시 모든 실행 상태 완전 초기화
- 재시작 시 깨끗한 상태에서 시작 보장

## 중복 실행 방지 메커니즘 계층

### 1단계: 스케줄러 레벨 (최우선)
- `is_callback_running` 플래그로 콜백 실행 상태 추적
- `last_execution_time`으로 시간 기반 중복 방지 (1시간)

### 2단계: 배치 실행 레벨
- `is_executing` 플래그로 배치 실행 상태 추적
- 기존 로직 유지

### 3단계: 프로세스 레벨 (추가 안전장치)
- `running_processes` 리스트로 실제 실행 중인 프로세스 확인
- 활성 프로세스 존재 시 새로운 실행 차단

## 예상 효과

### 1. 중복 실행 완전 방지
- 3단계 9개 스텝 추가 후에도 중복 브라우저 실행 없음
- 스케줄러, 배치, 프로세스 레벨의 삼중 안전장치

### 2. 리소스 최적화
- 불필요한 중복 프로세스 생성 방지
- 시스템 리소스 효율적 사용

### 3. 안정성 향상
- 예외 상황에서도 안전한 실행 보장
- 로그를 통한 명확한 상태 추적

### 4. 디버깅 편의성
- 중복 실행 방지 로그 메시지로 문제 상황 즉시 파악
- 실행 시작/완료 시간 로깅으로 성능 모니터링 가능

## 테스트 방법

### 1. 기본 기능 테스트
```
1. GUI 주기적 실행 탭에서 1단계 + 3단계 9개 스텝 선택
2. 모든 계정 선택
3. 짧은 간격(예: 1분 후)으로 스케줄 설정
4. 주기적 실행 시작
5. 로그 모니터링하여 중복 실행 방지 메시지 확인
```

### 2. 중복 실행 방지 테스트
```
1. 주기적 실행 시작 후 즉시 "즉시 실행" 버튼 클릭
2. 로그에서 "이미 실행 중입니다" 메시지 확인
3. 프로세스 매니저에서 중복 브라우저 프로세스 없음 확인
```

### 3. 장시간 실행 테스트
```
1. 3단계 9개 스텝을 포함한 전체 배치 실행
2. 실행 시간이 1시간을 넘는 경우 테스트
3. 실행 중 새로운 스케줄 시간 도달 시 중복 실행 방지 확인
```

### 4. 예외 상황 테스트
```
1. 실행 중 강제 종료 후 재시작
2. 네트워크 오류 발생 시 복구 테스트
3. 시스템 재부팅 후 정상 동작 확인
```

## 로그 모니터링 포인트

### 정상 실행 로그
```
주기적 실행 시작: 2024-01-15 09:00:00
배치 실행 시작: 1단계=300개, 나머지단계=100개, 단계=['1', '311', '312', ...]
주기적 실행 완료: 2024-01-15 12:30:00
```

### 중복 실행 방지 로그
```
이전 주기적 실행이 아직 진행 중입니다. 중복 실행을 방지합니다.
최근 실행 후 1800초 경과. 중복 실행을 방지합니다.
실행 중인 프로세스 5개가 있습니다. 중복 실행을 방지합니다.
```

## 주의사항

1. **1시간 제한**: 정상적인 실행이 1시간을 넘는 경우 시간 제한 조정 필요
2. **프로세스 정리**: 비정상 종료 시 좀비 프로세스가 남을 수 있으므로 주기적 확인 필요
3. **로그 모니터링**: 중복 실행 방지 로그가 지속적으로 발생하면 설정 재검토 필요

## 향후 개선 방안

1. **동적 시간 제한**: 실행 단계 수에 따른 동적 시간 제한 계산
2. **프로세스 헬스체크**: 주기적인 프로세스 상태 확인 및 정리
3. **실행 통계**: 실행 시간, 성공률 등 통계 정보 수집
4. **알림 시스템**: 중복 실행 방지 상황 발생 시 사용자 알림