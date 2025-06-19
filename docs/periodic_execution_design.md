# 주기적 실행 기능 설계 문서

## 1. 요구사항 분석

### 1.1 핵심 요구사항
- **주기적 실행 탭 추가**: 기본 설정 탭 앞에 '주기적 실행' 탭 추가
- **배치 수량 선택**: 100, 200, 300개 중 라디오버튼으로 선택
- **순차 실행**: 동일 계정에 대해 선택된 단계들을 순차적으로 실행
- **계정별 독립 실행**: 7개 계정 선택 시 7개의 독립적인 프로세스로 실행
- **스케줄링**: 매일 지정된 시간(예: 오전 9시, 10시)에 자동 실행

### 1.2 현재 시스템 분석
- **현재 구조**: 기본 설정, 고급 설정, 실행 모니터링 3개 탭
- **현재 실행 방식**: 계정별 × 단계별 = 모든 조합을 동시 실행
- **기존 배치 파일들**: step2_batch_runner.py, step3_batch_runner.py, step4_core.py 등

## 2. 설계 방안

### 2.1 아키텍처 선택

#### 방안 A: 기존 GUI 확장 (권장)
**장점:**
- 기존 코드 재사용 가능
- 사용자 경험 일관성 유지
- 개발 시간 단축
- 기존 배치 로직 그대로 활용

**단점:**
- 기존 코드에 일부 영향 가능성
- 복잡도 증가

#### 방안 B: 별도 GUI 개발
**장점:**
- 기존 시스템에 영향 없음
- 독립적인 기능 개발

**단점:**
- 코드 중복
- 유지보수 부담 증가
- 사용자 혼란 가능성

### 2.2 권장 방안: 기존 GUI 확장

기존 `percenty_gui_advanced.py`에 주기적 실행 탭을 추가하되, 기존 기능과 완전히 분리된 독립적인 모듈로 구현

## 3. 상세 설계

### 3.1 UI 구조 변경

```
기존: [기본 설정] [고급 설정] [실행 모니터링]
변경: [주기적 실행] [기본 설정] [고급 설정] [실행 모니터링]
```

### 3.2 주기적 실행 탭 구성

#### 3.2.1 배치 수량 설정
```python
# 라디오버튼 그룹
○ 100개
○ 200개  
○ 300개
```

#### 3.2.2 단계 선택
```python
# 체크박스 (기존과 동일)
☐ 단계 1
☐ 단계 2-1 (서버1)  ☐ 단계 2-2 (서버2)  ☐ 단계 2-3 (서버3)
☐ 단계 3-1 (서버1)  ☐ 단계 3-2 (서버2)  ☐ 단계 3-3 (서버3)
☐ 단계 4
☐ 단계 5-1          ☐ 단계 5-2          ☐ 단계 5-3
☐ 단계 6
```

#### 3.2.3 계정 선택
```python
# 체크박스 (기존과 동일)
☐ 계정 1  ☐ 계정 2  ☐ 계정 3
☐ 계정 4  ☐ 계정 5  ☐ 계정 6
☐ 계정 7
```

#### 3.2.4 스케줄링 설정
```python
# 시간 선택
실행 시간: [09] : [00]  (시간:분 스핀박스)

# 스케줄 상태
○ 일회성 실행
○ 매일 반복 실행

# 제어 버튼
[스케줄 시작] [스케줄 중지] [즉시 실행]
```

### 3.3 핵심 로직 설계

#### 3.3.1 순차 실행 로직
```python
class PeriodicExecutionManager:
    def execute_account_workflow(self, account, selected_steps, quantity):
        """단일 계정에 대해 선택된 단계들을 순차 실행"""
        for step in selected_steps:
            success = self.execute_single_step(account, step, quantity)
            if not success:
                self.log_error(f"계정 {account} 단계 {step} 실행 실패")
                break
            
            # 단계 간 대기 시간
            time.sleep(self.step_interval)
    
    def execute_multi_account_workflow(self, accounts, selected_steps, quantity):
        """여러 계정에 대해 병렬로 순차 실행"""
        processes = []
        
        for account in accounts:
            # 각 계정별로 독립적인 프로세스 생성
            process = subprocess.Popen([
                sys.executable,
                "periodic_workflow_runner.py",
                "--account", account,
                "--steps", ",".join(selected_steps),
                "--quantity", str(quantity)
            ])
            processes.append(process)
        
        return processes
```

#### 3.3.2 스케줄링 로직
```python
import schedule
import threading

class ScheduleManager:
    def __init__(self):
        self.scheduler_thread = None
        self.is_running = False
    
    def start_daily_schedule(self, time_str, callback):
        """매일 지정된 시간에 실행되는 스케줄 시작"""
        schedule.clear()
        schedule.every().day.at(time_str).do(callback)
        
        self.is_running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
    
    def _run_scheduler(self):
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # 1분마다 체크
```

### 3.4 새로운 파일 구조

```
core/
├── periodic/
│   ├── __init__.py
│   ├── periodic_execution_manager.py  # 주기적 실행 관리자
│   ├── schedule_manager.py            # 스케줄링 관리자
│   └── workflow_runner.py             # 순차 실행 워크플로우
├── steps/
│   └── (기존 step 파일들)
└── ...
```

### 3.5 기존 코드 영향 최소화 방안

1. **독립적인 모듈 구조**: 주기적 실행 기능을 별도 모듈로 분리
2. **기존 배치 파일 재사용**: step2_batch_runner.py, step3_batch_runner.py 등 그대로 활용
3. **설정 분리**: 주기적 실행 설정을 별도 파일로 관리
4. **UI 탭 분리**: 기존 탭들과 완전히 독립적인 탭으로 구현

## 4. 구현 계획

### 4.1 1단계: 기본 UI 구조 (1일)
- 주기적 실행 탭 추가
- 배치 수량 라디오버튼
- 단계/계정 선택 UI
- 기본 제어 버튼

### 4.2 2단계: 순차 실행 로직 (2일)
- PeriodicExecutionManager 클래스 구현
- 순차 실행 워크플로우 구현
- 계정별 독립 프로세스 실행

### 4.3 3단계: 스케줄링 기능 (1일)
- ScheduleManager 클래스 구현
- 시간 설정 UI
- 매일 반복 실행 기능

### 4.4 4단계: 통합 및 테스트 (1일)
- 전체 기능 통합
- 오류 처리 및 로깅
- 사용자 테스트

## 5. 기술적 고려사항

### 5.1 의존성 추가
```python
# requirements.txt에 추가
schedule>=1.2.0  # 스케줄링 라이브러리
```

### 5.2 설정 파일 구조
```json
{
  "periodic_config": {
    "batch_quantity": 100,
    "selected_steps": ["1", "21", "22", "23"],
    "selected_accounts": ["1", "2", "3"],
    "schedule_time": "09:00",
    "is_daily_repeat": true,
    "step_interval": 30
  }
}
```

### 5.3 로깅 전략
- 주기적 실행 전용 로그 파일
- 계정별/단계별 상세 로그
- 스케줄 실행 이력 관리

## 6. 결론

**권장 방안**: 기존 `percenty_gui_advanced.py`에 주기적 실행 탭을 추가하되, 완전히 독립적인 모듈로 구현

**핵심 장점**:
1. 기존 안정화된 배치 파일들을 그대로 활용
2. 사용자 경험의 일관성 유지
3. 개발 시간 최소화
4. 기존 기능에 영향 없음

**구현 우선순위**:
1. UI 구조 변경 (주기적 실행 탭 추가)
2. 순차 실행 로직 구현
3. 스케줄링 기능 추가
4. 통합 테스트 및 최적화

이 설계를 통해 사용자가 원하는 모든 기능을 안전하고 효율적으로 구현할 수 있습니다.