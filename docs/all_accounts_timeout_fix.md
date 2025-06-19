# 모든 계정 타임아웃 수정 로직 문서

## 개요

이 문서는 주기적 실행에서 모든 계정에 대해 타임아웃 시 후속 스텝 계속 진행 로직을 적용하는 개선사항을 설명합니다.

## 문제점

### 기존 문제
1. **하드코딩된 계정 목록**: `periodic_config_enhanced.json`에서 특정 계정만 하드코딩
2. **제한적 적용**: 타임아웃 수정 로직이 일부 계정에만 적용
3. **확장성 부족**: 새로운 계정 추가 시 설정 파일 수동 수정 필요

### 타임아웃 발생 스텝
- **스텝 21, 22, 23**: 상품 검색/처리 관련
- **스텝 31, 32, 33**: 상품 관련 작업
- **원인**: `provider_code`별 상품 수량 차이로 인한 예측 불가능한 실행 시간

## 해결 방안

### 1. 동적 계정 관리

#### 설정 파일 개선
```json
{
  "selected_accounts": "all"
}
```

#### 구현 로직
```python
def get_selected_accounts(self):
    selected_accounts = self.config.get('selected_accounts', [])
    
    if selected_accounts == "all":
        # AccountManager를 통해 모든 계정 로드
        if not self.account_manager.load_accounts():
            return []
        
        all_accounts = self.account_manager.get_accounts()
        return [account['id'] for account in all_accounts]
    
    return selected_accounts
```

### 2. 타임아웃 시 후속 스텝 계속 진행 로직

#### 적용 대상 스텝
```python
continue_on_timeout_steps = ['21', '22', '23', '31', '32', '33']
```

#### 실행 로직
```python
for step in selected_steps:
    success = self._execute_single_step(account_id, step)
    
    if not success:
        if step in continue_on_timeout_steps:
            # 타임아웃 발생해도 후속 스텝 계속 진행
            self.logger.warning(
                f"스텝 {step} 실패/타임아웃 발생, 하지만 후속 스텝을 계속 진행합니다."
            )
        else:
            # 일반 스텝은 실패 시 account_success = False
            account_success = False
```

### 3. 개선된 설정 관리

#### 스텝별 타임아웃 설정
```json
{
  "step_timeout_settings": {
    "21": 3600,
    "22": 3600,
    "23": 3600,
    "31": 3600,
    "32": 3600,
    "33": 3600,
    "default": 1800
  }
}
```

#### 에러 처리 설정
```json
{
  "error_handling": {
    "continue_on_timeout": true,
    "max_retries": 1,
    "retry_delay": 60
  }
}
```

## 구현 파일

### 1. 수정된 파일
- `periodic_execution_manager.py`: 기존 파일에 타임아웃 로직 추가
- `periodic_config_enhanced.json`: 동적 계정 관리 설정

### 2. 새로 생성된 파일
- `enhanced_periodic_execution_manager.py`: 완전히 개선된 관리자
- `test_all_accounts_timeout_fix.py`: 모든 계정 테스트 스크립트
- `all_accounts_timeout_fix.md`: 이 문서

## 테스트 방법

### 1. 기본 테스트
```bash
python test_all_accounts_timeout_fix.py
```

### 2. 개선된 관리자 테스트
```bash
python enhanced_periodic_execution_manager.py
```

### 3. 실제 환경 테스트
```python
from enhanced_periodic_execution_manager import EnhancedPeriodicExecutionManager

manager = EnhancedPeriodicExecutionManager()
results = manager.execute_all_accounts()
print(f"성공률: {results['successful_accounts']/results['total_accounts']*100:.1f}%")
```

## 기대 효과

### 1. 확장성 개선
- ✅ 새로운 계정 추가 시 자동 포함
- ✅ 설정 파일 수동 수정 불필요
- ✅ Excel 파일 기반 동적 관리

### 2. 안정성 향상
- ✅ 타임아웃 발생해도 중요한 후속 스텝 실행
- ✅ 전체 주기적 실행 중단 방지
- ✅ 계정별 개별 결과 추적

### 3. 유지보수성 향상
- ✅ 명확한 로그 메시지
- ✅ 설정 기반 관리
- ✅ 모듈화된 구조

## 모니터링 포인트

### 1. 로그 확인 사항
```
계정 {account_id} - 스텝 {step} 실패/타임아웃 발생, 하지만 후속 스텝을 계속 진행합니다.
```

### 2. 성능 지표
- 전체 실행 시간
- 계정별 성공률
- 타임아웃 발생 빈도
- 후속 스텝 실행률

### 3. 알림 설정
- 전체 성공률 80% 미만 시 알림
- 특정 계정 연속 실패 시 알림
- 타임아웃 발생률 50% 초과 시 알림

## 향후 개선 방향

### 1. 계정별 개별 설정
```json
{
  "account_specific_settings": {
    "account1@example.com": {
      "continue_on_timeout_steps": ["21", "22"],
      "step_timeout": 1800
    }
  }
}
```

### 2. 동적 타임아웃 조정
- 과거 실행 시간 기반 타임아웃 자동 조정
- 상품 수량 기반 예상 실행 시간 계산

### 3. 병렬 실행 최적화
- 계정별 독립적 실행
- 리소스 사용량 기반 동시 실행 수 조정

## 결론

이번 개선을 통해:
1. **모든 계정**에 타임아웃 수정 로직이 적용됩니다
2. **동적 계정 관리**로 확장성이 크게 향상됩니다
3. **안정적인 주기적 실행**이 보장됩니다

특히 스텝 21에서 타임아웃이 발생해도 스텝 4, 51, 52, 53이 계속 실행되어 전체 작업의 완성도를 높일 수 있습니다.