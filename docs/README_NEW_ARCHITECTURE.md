# Percenty 자동화 프로젝트 - 새로운 아키텍처

## 🎯 개요

이 문서는 Percenty 자동화 프로젝트의 새로운 아키텍처에 대한 가이드입니다. 기존 코드와의 완전한 호환성을 유지하면서 확장성과 유지보수성을 크게 개선했습니다.

## 📁 새로운 디렉토리 구조

```
percenty_project/
├── core/                    # 핵심 비즈니스 로직
│   ├── steps/              # 단계별 핵심 로직
│   │   └── step1_core.py   # 1단계 핵심 로직
│   ├── browser/            # 브라우저 관리
│   │   └── browser_manager.py
│   ├── account/            # 계정 관리
│   │   └── account_manager.py
│   └── utils/              # 유틸리티
│
├── batch/                   # 배치 처리 시스템
│   ├── batch_manager.py    # 통합 배치 관리자
│   ├── legacy_wrapper.py   # 기존 코드 호환성
│   ├── config/             # 설정 파일
│   │   └── batch_config.yaml
│   ├── executors/          # 실행기
│   └── monitors/           # 모니터링
│
├── cli/                     # 명령줄 인터페이스
│   └── batch_cli.py        # CLI 도구
│
├── legacy/                  # 기존 코드 (참조용)
│   └── app/                # 기존 GUI 앱
│
├── docs/                    # 문서
│   └── architecture_redesign.md
│
├── batch_processor_new.py   # 새로운 배치 프로세서
├── batch_processor.py       # 기존 배치 프로세서 (유지)
└── [기존 파일들...]         # 모든 기존 파일 유지
```

## 🚀 주요 개선사항

### 1. 모듈화된 아키텍처
- **관심사 분리**: 각 모듈이 명확한 책임을 가짐
- **재사용성**: 핵심 로직을 다양한 인터페이스에서 활용 가능
- **테스트 용이성**: 각 모듈을 독립적으로 테스트 가능

### 2. 다중 실행 지원
- **다중 계정 동시 실행**: 여러 계정을 병렬로 처리
- **다중 단계 순차 실행**: 하나의 계정으로 여러 단계 연속 실행
- **혼합 실행**: 계정별로 다른 단계 조합 실행

### 3. 설정 기반 관리
- **YAML 설정 파일**: 복잡한 배치 시나리오를 설정으로 관리
- **사전 정의된 시나리오**: 자주 사용하는 패턴을 템플릿화
- **동적 설정 변경**: 런타임에 설정 수정 가능

### 4. 다양한 인터페이스
- **CLI**: 명령줄에서 배치 작업 실행
- **프로그래밍 API**: 다른 스크립트에서 호출 가능
- **기존 호환성**: 기존 코드 수정 없이 사용 가능

## 📖 사용 방법

### 1. 기존 방식 (완전 호환)

```python
# 기존 코드 그대로 사용 가능
from batch_processor import BatchProcessor

processor = BatchProcessor()
result = processor.run_batch(['account1', 'account2'], 100)
```

### 2. 새로운 배치 프로세서

```python
# 새로운 아키텍처 사용
from batch_processor_new import BatchProcessor

processor = BatchProcessor(headless=True)
result = processor.run_batch(['account1', 'account2'], 100)
```

### 3. 새로운 배치 관리자

```python
# 고급 기능 사용
from batch.batch_manager import BatchManager

manager = BatchManager()

# 1단계를 여러 계정에서 동시 실행
result = manager.run_single_step(
    step=1,
    accounts=['account1', 'account2', 'account3'],
    quantity=100,
    concurrent=True
)

# 여러 단계를 하나의 계정에서 순차 실행
result = manager.run_multi_step(
    account='account1',
    steps=[1, 2, 3],
    quantities=[100, 50, 30],
    concurrent=False
)
```

### 4. CLI 사용

```bash
# 1단계를 여러 계정에서 동시 실행
python cli/batch_cli.py single --step 1 --accounts account1 account2 --quantity 100 --concurrent

# 여러 단계를 하나의 계정에서 실행
python cli/batch_cli.py multi --account account1 --steps 1 2 3 --quantities 100 50 30

# 사전 정의된 시나리오 실행
python cli/batch_cli.py scenario --name step1_multi_account

# 계정 목록 조회
python cli/batch_cli.py accounts
```

### 5. 편의 함수 사용

```python
# 간단한 1단계 실행
from batch.batch_manager import run_step1_for_accounts

result = run_step1_for_accounts(
    accounts=['account1', 'account2'],
    quantity=100,
    concurrent=True
)

# 모든 단계 실행
from batch.batch_manager import run_all_steps_for_account

result = run_all_steps_for_account(
    account='account1',
    quantities=[100, 50, 30, 20, 10, 5]
)
```

## ⚙️ 설정 관리

### 기본 설정 파일: `batch/config/batch_config.yaml`

```yaml
# 배치 설정
batch:
  max_workers: 4
  default_quantity: 100
  retry_count: 3

# 브라우저 설정
browser:
  headless: false
  timeout: 30

# 사전 정의된 시나리오
scenarios:
  step1_multi_account:
    description: "여러 계정으로 1단계 동시 실행"
    type: "single_step"
    step: 1
    accounts: ["account1", "account2", "account3"]
    quantity: 100
    concurrent: true
```

## 🔄 마이그레이션 가이드

### 단계 1: 기존 코드 테스트
```python
# 기존 코드가 여전히 작동하는지 확인
python batch_processor.py
```

### 단계 2: 새로운 프로세서 테스트
```python
# 새로운 아키텍처 테스트
python batch_processor_new.py
```

### 단계 3: 점진적 전환
```python
# 기존 코드에서 import만 변경
# from batch_processor import BatchProcessor
from batch_processor_new import BatchProcessor
```

### 단계 4: 고급 기능 활용
```python
# 새로운 기능들 활용
from batch.batch_manager import BatchManager
```

## 🛠️ 개발자 가이드

### 새로운 단계 추가

1. **핵심 로직 구현**
   ```python
   # core/steps/step2_core.py
   class Step2Core:
       def execute_step2(self, quantity):
           # 2단계 로직 구현
           pass
   ```

2. **배치 관리자에 등록**
   ```python
   # batch/batch_manager.py의 _execute_step_for_account 메서드에 추가
   elif step == 2:
       step_core = Step2Core(driver)
       step_result = step_core.execute_step2(quantity)
   ```

3. **설정 파일 업데이트**
   ```yaml
   # batch/config/batch_config.yaml
   steps:
     step2:
       default_quantity: 50
       timeout: 600
   ```

### 테스트 작성

```python
# tests/test_step2.py
import pytest
from core.steps.step2_core import Step2Core

def test_step2_execution():
    # 테스트 코드 작성
    pass
```

## 📊 성능 최적화

### 동시 실행 설정
```python
# 최적의 워커 수 설정 (CPU 코어 수 고려)
manager = BatchManager()
manager.max_workers = 4  # 또는 os.cpu_count()
```

### 메모리 관리
```python
# 대량 처리 시 배치 크기 조절
for batch in chunks(large_account_list, batch_size=10):
    result = manager.run_single_step(1, batch, 100)
```

### 브라우저 최적화
```yaml
# batch_config.yaml
browser:
  headless: true      # 메모리 절약
  enable_images: false # 네트워크 절약
```

## 🔍 모니터링 및 로깅

### 로그 파일 위치
- `logs/batch_manager.log`: 배치 관리자 로그
- `logs/batch_processor.log`: 배치 프로세서 로그

### 진행상황 모니터링
```python
# 실시간 상태 확인
status = manager.get_task_status(task_id)
print(f"진행률: {status['progress']}%")
```

## 🚨 문제 해결

### 자주 발생하는 문제

1. **모듈 임포트 오류**
   ```bash
   # 경로 확인
   export PYTHONPATH=$PYTHONPATH:/path/to/percenty_project
   ```

2. **브라우저 드라이버 문제**
   ```python
   # 드라이버 경로 확인
   from core.browser.browser_manager import CoreBrowserManager
   manager = CoreBrowserManager()
   manager.check_driver_installation()
   ```

3. **계정 로그인 실패**
   ```python
   # 계정 정보 확인
   from core.account.account_manager import CoreAccountManager
   manager = CoreAccountManager()
   accounts = manager.get_all_accounts()
   ```

### 백업 및 복구

```bash
# 원본 파일이 손상된 경우
cp /originalfiles/[파일명] ./[파일명]
```

## 📈 향후 계획

### Phase 2: 2-6단계 구현
- [ ] Step2Core 구현
- [ ] Step3Core 구현
- [ ] Step4Core 구현
- [ ] Step5Core 구현
- [ ] Step6Core 구현

### Phase 3: 고급 기능
- [ ] 스케줄링 시스템
- [ ] 웹 대시보드
- [ ] 실시간 모니터링
- [ ] 자동 복구 시스템

## 🤝 기여 가이드

1. **코드 스타일**: PEP 8 준수
2. **테스트**: 새로운 기능에 대한 테스트 작성 필수
3. **문서화**: 주요 변경사항은 문서 업데이트
4. **호환성**: 기존 코드와의 호환성 유지

## 📞 지원

문제가 발생하거나 질문이 있으시면:
1. 로그 파일 확인
2. 백업 파일 활용
3. 이 문서의 문제 해결 섹션 참조

---

**새로운 아키텍처로 더 안정적이고 확장 가능한 자동화 환경을 경험해보세요!** 🚀