# 퍼센티 자동화 프로젝트 아키텍처 재설계

## 📋 현재 상황 분석

### 기존 구조의 문제점
1. **batch_processor.py**가 app 모듈에 종속
2. 다중 계정, 다중 단계 동시 실행 기능 부족
3. GUI 앱의 불안정성 (TensorFlow 초기화 후 멈춤)
4. 확장성 부족 (2-6단계 추가 시 복잡성 증가)

### 요구사항
1. 현재 batch_processor.py 기능 유지
2. 루트 코어 파일 보존
3. 다중 계정 동시 실행
4. 다중 단계 선택적 실행
5. 2-6단계 배치 작업 지원
6. 주기적 실행 스케줄링

## 🏗️ 새로운 아키텍처 설계

### 디렉토리 구조
```
percentyproject/
├── core/                           # 핵심 비즈니스 로직 (기존 파일들)
│   ├── steps/                      # 단계별 코어 모듈
│   │   ├── step1_core.py          # 1단계 핵심 로직
│   │   ├── step2_core.py          # 2단계 핵심 로직 (향후)
│   │   └── ...
│   ├── browser/                    # 브라우저 관리
│   │   ├── browser_core.py
│   │   └── browser_manager.py
│   ├── account/                    # 계정 관리
│   │   └── account_manager.py
│   └── utils/                      # 공통 유틸리티
│       ├── coordinates/
│       ├── dom_selectors.py
│       └── ...
├── batch/                          # 새로운 배치 시스템
│   ├── batch_manager.py           # 통합 배치 관리자
│   ├── config/                    # 설정 파일들
│   │   ├── batch_config.yaml
│   │   └── account_config.yaml
│   ├── executors/                 # 실행자들
│   │   ├── single_executor.py     # 단일 작업 실행
│   │   ├── multi_executor.py      # 다중 작업 실행
│   │   └── scheduled_executor.py  # 스케줄 실행
│   └── monitors/                  # 모니터링
│       ├── progress_monitor.py
│       └── log_monitor.py
├── legacy/                         # 기존 파일들 (호환성 유지)
│   ├── batch_processor.py         # 기존 배치 프로세서 (수정됨)
│   └── app/                       # 기존 GUI 앱
├── cli/                           # 명령줄 인터페이스
│   ├── batch_cli.py              # CLI 진입점
│   └── commands/                  # CLI 명령들
└── gui/                           # 새로운 GUI (선택사항)
    └── modern_gui.py
```

## 🔧 구현 계획

### Phase 1: 코어 모듈 분리 및 정리
1. **core 디렉토리 생성** 및 기존 파일 분류
2. **batch 디렉토리 생성** 및 새로운 배치 시스템 구축
3. **기존 batch_processor.py 수정** (app 종속성 제거)

### Phase 2: 새로운 배치 관리자 개발
1. **BatchManager 클래스** 구현
2. **설정 기반 실행** 시스템
3. **다중 실행 지원**

### Phase 3: CLI 및 모니터링 시스템
1. **명령줄 인터페이스** 구현
2. **진행상황 모니터링** 시스템
3. **로그 관리** 시스템

## 🎯 핵심 기능 설계

### 1. 통합 배치 관리자 (BatchManager)
```python
class BatchManager:
    def run_single_step(self, step: int, accounts: List[str], quantity: int)
    def run_multi_step(self, account: str, steps: List[int], quantities: List[int])
    def run_concurrent(self, config: Dict)
    def run_scheduled(self, schedule: Dict)
```

### 2. 설정 기반 실행
```yaml
# batch_config.yaml
accounts:
  - id: "account1"
    email: "user1@example.com"
    password: "password1"

tasks:
  - name: "daily_step1_all"
    step: 1
    accounts: ["account1", "account2", "account3", "account4"]
    quantity: 100
    concurrent: true
    
  - name: "full_process_single"
    account: "account1"
    steps: [1, 2, 3, 4, 5, 6]
    quantities: [100, 50, 30, 20, 10, 5]
    concurrent: false
```

### 3. 호환성 유지
- 기존 `batch_processor.py` 실행 방식 유지
- 새로운 시스템으로 점진적 마이그레이션
- 백워드 호환성 보장

## 🚀 즉시 실행 계획

1. **docs 디렉토리 생성** 및 설계 문서 작성 ✅
2. **core 디렉토리 생성** 및 파일 분류
3. **batch 디렉토리 생성** 및 기본 구조 구축
4. **기존 batch_processor.py 수정** (종속성 제거)
5. **새로운 BatchManager 구현**
6. **CLI 인터페이스 구현**
7. **테스트 및 검증**

## 📝 주의사항

1. **기존 파일 보존**: 모든 루트 코어 파일 유지
2. **점진적 마이그레이션**: 기존 기능 중단 없이 새 기능 추가
3. **백업 활용**: originalfiles 디렉토리의 백업 파일 참조
4. **테스트 우선**: 각 단계별 철저한 테스트
5. **문서화**: 변경사항 및 사용법 문서화

---

**다음 단계**: core 디렉토리 생성 및 파일 분류 작업 시작