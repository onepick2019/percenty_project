# 타임아웃 설정 및 스텝 순서 수정 문서

## 수정 사항 요약

### 1. 21단계 타임아웃 시 22단계 건너뛰기 문제 해결

#### 문제 분석
- **기존 코드는 올바르게 작동**: 21단계 타임아웃 시 22단계가 건너뛰어지지 않음
- **실제 로직**: `continue_on_timeout_steps = ['21', '22', '23', '31', '32', '33']`에 포함된 스텝은 타임아웃 발생해도 후속 스텝 계속 진행

#### 코드 확인
```python
for step in selected_steps:
    success = self._execute_single_step(account_id, step, batch_quantity)
    
    if not success:
        if step not in continue_on_timeout_steps:
            account_success = False
        else:
            self._log(f"계정 {account_id}, 단계 {step}: 타임아웃/실패했지만 후속 단계 계속 진행")
```

### 2. 스텝별 타임아웃 설정 수정

#### 수정된 타임아웃 설정
```python
step_timeouts = {
    '2': 7200,  # 2시간 (사용자 요구사항)
    '3': 7200,  # 2시간 (사용자 요구사항)
    '1': 3600,  # 1시간 (사용자 요구사항)
    '4': 3600,  # 1시간 (사용자 요구사항)
    '5': 3600,  # 1시간 (사용자 요구사항)
    '51': 3600, # 1시간 (사용자 요구사항)
    '52': 3600, # 1시간 (사용자 요구사항)
    '53': 3600  # 1시간 (사용자 요구사항)
}
timeout = step_timeouts.get(step, 1800)  # 기본 30분
```

#### 타임아웃 로그 추가
```python
self._log(f"단계 {step} 타임아웃 설정: {timeout}초 ({timeout//3600}시간 {(timeout%3600)//60}분)")
```

### 3. 배치 크기 수정

#### 설정 파일 수정
- `periodic_config.json`: `batch_quantity` 100 → 10
- `periodic_config_enhanced.json`: `batch_quantity` 100 → 10

## 수정된 파일 목록

### 1. 핵심 로직 파일
- `core/periodic_execution_manager.py`: 스텝별 타임아웃 설정 추가

### 2. 설정 파일
- `periodic_config.json`: 배치 크기 수정
- `periodic_config_enhanced.json`: 배치 크기 수정

### 3. 테스트 파일
- `test_timeout_settings.py`: 수정된 설정 테스트 스크립트
- `docs/timeout_settings_fix.md`: 이 문서

## 테스트 방법

### 1. 설정 확인 테스트
```bash
python test_timeout_settings.py
```

### 2. 실제 실행 테스트
```bash
# 주기적 실행 관리자를 통한 테스트
python -c "from core.periodic_execution_manager import PeriodicExecutionManager; manager = PeriodicExecutionManager(); manager.load_config('periodic_config.json'); manager.execute_immediate()"
```

## 예상 결과

### 1. 스텝 실행 순서
```
계정 example@gmail.com 처리 시작
단계 1 타임아웃 설정: 3600초 (1시간)
계정 example@gmail.com, 단계 1 완료
단계 21 타임아웃 설정: 1800초 (30분)
계정 example@gmail.com, 단계 21: 타임아웃/실패했지만 후속 단계 계속 진행
단계 22 타임아웃 설정: 1800초 (30분)
계정 example@gmail.com, 단계 22 완료
단계 4 타임아웃 설정: 3600초 (1시간)
계정 example@gmail.com, 단계 4 완료
```

### 2. 타임아웃 동작
- **스텝 2, 3**: 2시간 후 타임아웃
- **스텝 1, 4, 5, 51, 52, 53**: 1시간 후 타임아웃
- **기타 스텝**: 30분 후 타임아웃

### 3. 배치 크기
- 모든 스텝에서 10개씩 처리

## 모니터링 포인트

### 1. 로그 확인 사항
```
단계 {step} 타임아웃 설정: {timeout}초 ({hours}시간 {minutes}분)
계정 {account_id}, 단계 {step}: 타임아웃/실패했지만 후속 단계 계속 진행
```

### 2. 성능 지표
- 각 스텝별 실행 시간
- 타임아웃 발생 빈도
- 21단계 타임아웃 후 22단계 실행률

### 3. 알림 설정
- 스텝 2, 3에서 2시간 초과 시 알림
- 스텝 1, 4, 5에서 1시간 초과 시 알림
- 21단계 타임아웃 후 22단계 미실행 시 알림

## 문제 해결 가이드

### Q1: 21단계 타임아웃 후 22단계가 실행되지 않는 경우
**확인사항:**
1. `continue_on_timeout_steps`에 '21'이 포함되어 있는지 확인
2. 스텝 순서가 올바른지 확인 (`selected_steps`에서 21 다음에 22가 있는지)
3. 로그에서 "후속 단계 계속 진행" 메시지 확인

### Q2: 타임아웃이 예상보다 빨리 발생하는 경우
**확인사항:**
1. `step_timeouts` 딕셔너리에 해당 스텝이 올바르게 설정되어 있는지 확인
2. 로그에서 "타임아웃 설정" 메시지로 실제 적용된 시간 확인

### Q3: 배치 크기가 반영되지 않는 경우
**확인사항:**
1. `periodic_config.json` 파일의 `batch_quantity` 값 확인
2. 설정 파일 로드 로그 확인

## 향후 개선 방향

### 1. 동적 타임아웃 조정
- 과거 실행 시간 기반 자동 타임아웃 조정
- 상품 수량 기반 예상 실행 시간 계산

### 2. 스텝별 개별 설정
```json
{
  "step_specific_settings": {
    "21": {
      "timeout": 1800,
      "continue_on_timeout": true,
      "batch_size": 5
    }
  }
}
```

### 3. 실시간 모니터링
- 스텝별 실행 상태 대시보드
- 타임아웃 발생 알림
- 성능 지표 추적

## 결론

이번 수정을 통해:
1. ✅ **스텝별 타임아웃 설정**: 2,3단계 2시간, 1,4,5,51,52,53단계 1시간
2. ✅ **배치 크기 조정**: 100개 → 10개
3. ✅ **21단계 타임아웃 시 22단계 계속 진행 확인**: 기존 로직이 올바르게 작동
4. ✅ **상세한 로그 추가**: 타임아웃 설정 및 실행 상태 추적

모든 요구사항이 충족되었으며, 안정적인 주기적 실행이 보장됩니다.