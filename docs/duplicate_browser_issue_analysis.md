# GUI 주기적 실행 중복 브라우저 문제 분석

## 문제 상황
- GUI 주기적 실행 탭에서 1단계와 모든 계정을 선택하여 실행
- 처음에는 정상적으로 순차적인 배치 작업이 진행됨
- 3단계 9개 스텝(311, 312, 313, 321, 322, 323, 331, 332, 333)을 추가로 연동한 이후
- 배치 작업 시작 후 얼마 지나지 않아 새로운 브라우저가 열리고 동일한 배치 작업이 다시 진행되는 오류 발생

## 원인 분석

### 1. 스케줄러 중복 등록 문제
**위치**: `core/periodic_execution_manager.py` - `ScheduleManager.start_daily_schedule()`

```python
def start_daily_schedule(self, time_str: str, callback: Callable):
    try:
        if schedule is not None:
            # schedule 라이브러리 사용
            # 기존 스케줄 정리
            schedule.clear()  # ✅ 정상적으로 기존 스케줄 정리
            
            # 새 스케줄 등록
            schedule.every().day.at(time_str).do(callback)
```

**문제점**: schedule 라이브러리를 사용하는 경우 `schedule.clear()`로 기존 스케줄을 정리하지만, SimpleScheduler를 사용하는 경우에는 다른 로직을 사용합니다.

### 2. SimpleScheduler의 중복 실행 방지 로직
**위치**: `core/simple_scheduler.py` - `schedule_daily()`

```python
def schedule_daily(self, time_str: str, callback: Callable):
    # ...
    # 기존 스케줄러 중지
    self.stop()  # ✅ 기존 스케줄러 중지
    
    # 새 스케줄러 시작
    self.is_running = True
```

**분석**: SimpleScheduler는 `self.stop()`으로 기존 스케줄러를 중지하므로 중복 등록 문제는 없어 보입니다.

### 3. 실제 문제: 스케줄러 스레드 관리 문제
**위치**: `core/periodic_execution_manager.py` - `ScheduleManager._run_scheduler()`

```python
def _run_scheduler(self):
    logger.info("스케줄러 스레드가 시작되었습니다.")
    
    while self.is_running:
        try:
            if schedule is not None:
                schedule.run_pending()  # ⚠️ 여기서 중복 실행 가능
            time.sleep(1)
        except Exception as e:
            logger.error(f"스케줄러 실행 중 오류: {e}")
            time.sleep(5)
```

**문제점**: 
1. `schedule.run_pending()`이 1초마다 호출되면서 동일한 시간에 여러 번 실행될 수 있음
2. `schedule.every().day.at(time_str).do(callback)`에서 콜백이 중복 등록될 가능성

### 4. 핵심 문제: 배치 실행 중복 방지 로직 부족
**위치**: `core/periodic_execution_manager.py` - `_execute_periodic_batch()`

```python
def _execute_periodic_batch(self) -> bool:
    if self.is_executing:
        self._log("이미 실행 중입니다. 중복 실행을 방지합니다.")
        return False
    
    self.is_executing = True  # ✅ 중복 실행 방지 플래그
```

**분석**: 중복 실행 방지 로직이 있지만, 스케줄러 레벨에서 중복 호출이 발생할 수 있습니다.

### 5. 3단계 9개 스텝 추가 후 문제 발생 원인

**가능한 원인들**:
1. **타임아웃 계산 문제**: 3단계 스텝들의 타임아웃이 길어져서 첫 번째 실행이 완료되기 전에 두 번째 실행이 시작
2. **청크 사이즈 문제**: 3단계 스텝들의 청크 사이즈가 작아서(기본값 2) 브라우저 재시작이 빈번하게 발생
3. **프로세스 정리 문제**: 타임아웃 발생 시 프로세스 정리가 완전하지 않아서 중복 실행으로 인식되지 않음

## 예상 시나리오

1. 사용자가 주기적 실행을 시작
2. 스케줄러가 정해진 시간에 `_execute_periodic_batch()` 호출
3. 3단계 9개 스텝 실행으로 인해 전체 실행 시간이 길어짐
4. 첫 번째 배치 실행이 완료되기 전에 스케줄러가 다시 실행 시간에 도달
5. `is_executing` 플래그가 여전히 `True`이지만, 어떤 이유로 중복 실행이 발생
6. 새로운 브라우저 프로세스가 시작되어 동일한 작업을 중복 수행

## 해결 방안

### 1. 스케줄러 레벨 중복 방지 강화
```python
def _run_scheduler(self):
    while self.is_running:
        try:
            if schedule is not None:
                # 실행 중인 작업이 있으면 스케줄 실행 건너뛰기
                if not hasattr(self, 'callback_function') or not self.callback_function:
                    schedule.run_pending()
                elif not getattr(self, 'is_callback_running', False):
                    schedule.run_pending()
            time.sleep(1)
```

### 2. 콜백 실행 상태 추적
```python
def start_daily_schedule(self, time_str: str, callback: Callable):
    def safe_callback():
        if getattr(self, 'is_callback_running', False):
            logger.warning("이전 실행이 아직 진행 중입니다. 중복 실행을 방지합니다.")
            return
        
        self.is_callback_running = True
        try:
            callback()
        finally:
            self.is_callback_running = False
    
    # safe_callback을 스케줄에 등록
    schedule.every().day.at(time_str).do(safe_callback)
```

### 3. 실행 시간 기반 중복 방지
```python
def _execute_periodic_batch(self) -> bool:
    # 현재 시간 기반 중복 실행 방지
    current_time = datetime.now()
    if hasattr(self, 'last_execution_time'):
        time_diff = current_time - self.last_execution_time
        if time_diff.total_seconds() < 3600:  # 1시간 이내 중복 실행 방지
            self._log(f"최근 실행 후 {time_diff.total_seconds()}초 경과. 중복 실행을 방지합니다.")
            return False
    
    self.last_execution_time = current_time
```

### 4. 프로세스 상태 기반 중복 방지
```python
def _execute_periodic_batch(self) -> bool:
    # 실행 중인 프로세스가 있으면 중복 실행 방지
    with self.process_lock:
        if self.running_processes:
            active_processes = [p for p in self.running_processes if p.poll() is None]
            if active_processes:
                self._log(f"실행 중인 프로세스 {len(active_processes)}개가 있습니다. 중복 실행을 방지합니다.")
                return False
```

## 권장 해결책

1. **즉시 적용**: 콜백 실행 상태 추적을 통한 스케줄러 레벨 중복 방지
2. **중기 적용**: 실행 시간 기반 중복 방지 로직 추가
3. **장기 적용**: 프로세스 상태 모니터링을 통한 완전한 중복 방지 시스템

## 테스트 방법

1. 3단계 9개 스텝을 포함한 주기적 실행 설정
2. 짧은 간격(예: 1분)으로 스케줄 설정하여 중복 실행 테스트
3. 로그 모니터링을 통해 중복 실행 방지 로직 동작 확인
4. 프로세스 모니터링을 통해 중복 브라우저 실행 여부 확인