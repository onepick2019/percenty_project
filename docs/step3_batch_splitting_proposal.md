# Step3 배치분할 구현 제안서

## 1. 현재 상황 분석

### 1.1 코어3의 특징
- **처리 방식**: 엑셀 F열이 "step3"인 항목들을 B열 provider_code별로 순차 처리
- **상품 수량**: provider_code마다 검색되는 상품 수가 다름 (미리 알 수 없음)
- **처리 단위**: 각 provider_code별로 모든 상품을 완전히 처리한 후 다음으로 이동
- **메모리 이슈**: 크롬 브라우저 장시간 사용으로 인한 메모리 부하

### 1.2 기존 배치분할과의 차이점
- **코어1/코어5**: 고정된 총 수량을 미리 알고 있어 균등 분할 가능
- **코어3**: 각 provider_code별 상품 수를 미리 알 수 없음

## 2. 배치분할 구현 방안

### 2.1 제안 방식: "작업 단위 기반 배치분할"

#### 핵심 아이디어
- **분할 기준**: 고정 수량이 아닌 "처리된 provider_code 개수" 기준
- **재시작 지점**: 마지막으로 완료된 provider_code 다음부터 시작
- **상태 저장**: 진행 상황을 파일로 저장하여 중단점 추적

#### 구체적 구현 방법

##### A. 진행 상태 추적 시스템
```python
# progress_tracker.json 예시
{
    "account_id": "onepick2019@gmail.com",
    "server_name": "서버1",
    "last_completed_provider_code": "ABC123",
    "completed_provider_codes": ["XYZ789", "ABC123"],
    "current_batch_start_time": "2024-01-15 10:30:00",
    "total_processed_items": 25
}
```

##### B. 배치분할 로직
1. **배치 크기**: provider_code 개수 기준 (예: 5개씩)
2. **재시작 로직**: 이전 배치에서 완료된 provider_code 다음부터 시작
3. **브라우저 재시작**: 각 배치 완료 후 메모리 정리

### 2.2 구현 단계

#### 단계 1: Step3Core 클래스 생성
```python
class Step3Core:
    def __init__(self, driver, account_info, batch_size=5):
        self.driver = driver
        self.account_info = account_info
        self.batch_size = batch_size
        self.progress_tracker = ProgressTracker(account_info['id'])
    
    def execute_step3_batch(self, provider_codes_batch):
        """배치 단위로 provider_code들 처리"""
        processed = 0
        failed = 0
        errors = []
        
        for provider_code in provider_codes_batch:
            try:
                # 기존 process_keyword_with_individual_modifications 호출
                success = self.core3.process_keyword_with_individual_modifications(
                    provider_code, target_group, task_data
                )
                if success:
                    processed += 1
                    self.progress_tracker.mark_completed(provider_code)
                else:
                    failed += 1
            except Exception as e:
                failed += 1
                errors.append(f"{provider_code}: {str(e)}")
        
        return {
            'processed': processed,
            'failed': failed,
            'errors': errors,
            'should_stop_batch': False  # step3는 중단 조건이 다름
        }
```

#### 단계 2: ProgressTracker 클래스
```python
class ProgressTracker:
    def __init__(self, account_id):
        self.account_id = account_id
        self.progress_file = f"progress_{account_id}_step3.json"
        self.load_progress()
    
    def load_progress(self):
        """이전 진행 상황 로드"""
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                self.progress = json.load(f)
        else:
            self.progress = {
                'completed_provider_codes': [],
                'last_completed_provider_code': None,
                'total_processed_items': 0
            }
    
    def get_remaining_provider_codes(self, all_provider_codes):
        """완료되지 않은 provider_code 목록 반환"""
        completed = set(self.progress['completed_provider_codes'])
        return [code for code in all_provider_codes if code not in completed]
    
    def mark_completed(self, provider_code):
        """완료된 provider_code 기록"""
        if provider_code not in self.progress['completed_provider_codes']:
            self.progress['completed_provider_codes'].append(provider_code)
            self.progress['last_completed_provider_code'] = provider_code
            self.save_progress()
```

#### 단계 3: BatchManager에 Step3 처리 추가
```python
def _execute_step3_with_browser_restart(self, account_id: str, initial_browser_id: str, 
                                       chunk_size: int = 5, account_info: Dict = None) -> Dict:
    """브라우저 재시작 방식으로 step3 실행"""
    
    # 1. 전체 step3 작업 목록 로드
    all_tasks = self._load_step3_tasks(account_id, account_info)
    
    # 2. 진행 상황 추적기 초기화
    progress_tracker = ProgressTracker(account_id)
    
    # 3. 남은 작업 목록 계산
    remaining_tasks = progress_tracker.get_remaining_tasks(all_tasks)
    
    # 4. 배치별로 처리
    total_batches = (len(remaining_tasks) + chunk_size - 1) // chunk_size
    
    for batch_idx in range(total_batches):
        start_idx = batch_idx * chunk_size
        end_idx = min(start_idx + chunk_size, len(remaining_tasks))
        current_batch = remaining_tasks[start_idx:end_idx]
        
        # 배치 처리
        batch_result = self._process_step3_batch(current_batch, current_browser_id)
        
        # 브라우저 재시작 (마지막 배치가 아닌 경우)
        if batch_idx < total_batches - 1:
            current_browser_id = self._restart_browser(account_id)
```

### 2.3 장점

1. **메모리 효율성**: 정기적인 브라우저 재시작으로 메모리 정리
2. **중단점 복구**: 어느 지점에서 중단되어도 이어서 실행 가능
3. **진행 상황 추적**: 실시간으로 진행 상황 파악 가능
4. **유연한 배치 크기**: provider_code 개수에 따라 배치 크기 조정 가능

### 2.4 코어2와의 분리

현재 코어2 → 코어3 연속 실행 구조를 다음과 같이 분리:

#### 기존 구조
```python
# percenty_new_step3_server1.py
def run_step3_automation(self):
    # 코어2 실행
    core2_result = core2.process_all_tasks()
    
    # 코어3 실행 (연속)
    core3_result = core3.process_all_tasks()
```

#### 분리 후 구조
```python
# 코어2 전용 실행
def run_step2_automation(self):
    return core2.process_all_tasks()

# 코어3 전용 실행 (배치분할 지원)
def run_step3_automation(self):
    return self._execute_step3_with_batch_splitting()
```

## 3. 구현 우선순위

### Phase 1: 기본 구조 구축
1. Step3Core 클래스 생성
2. ProgressTracker 구현
3. 기본 배치분할 로직 구현

### Phase 2: BatchManager 통합
1. BatchManager에 step3 처리 메서드 추가
2. 브라우저 재시작 로직 적용
3. 로깅 및 에러 처리 강화

### Phase 3: 최적화 및 테스트
1. 배치 크기 최적화
2. 에러 복구 로직 강화
3. 성능 테스트 및 튜닝

## 4. 예상 효과

1. **메모리 사용량 감소**: 브라우저 재시작으로 메모리 누수 방지
2. **안정성 향상**: 중단점 복구로 작업 연속성 보장
3. **모니터링 개선**: 실시간 진행 상황 추적
4. **확장성**: 다른 step에도 동일한 패턴 적용 가능

## 5. 구현 시 고려사항

1. **진행 상황 파일 관리**: 작업 완료 후 정리 로직 필요
2. **에러 처리**: provider_code별 실패 시 재시도 로직
3. **동시 실행 방지**: 같은 계정의 중복 실행 방지
4. **로그 관리**: 배치별 상세 로그 기록

이 제안서를 바탕으로 단계적으로 구현하면 코어3의 배치분할을 효과적으로 적용할 수 있을 것입니다.