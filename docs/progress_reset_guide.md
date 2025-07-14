# 진행 상황 파일 초기화 가이드

## 개요

새로운 배치 작업을 시작할 때 기존 진행 상황 파일로 인해 키워드가 제외되는 문제를 해결하기 위해 `--reset-progress` 옵션이 추가되었습니다.

## 문제 상황

기존에는 3단계 배치 작업이 중단된 후 다시 시작할 때, JSON 진행 상황 파일에 저장된 다음 정보들로 인해 이미 처리된 키워드가 제외되었습니다:

```json
{
  "completed_keywords": ["K22"],
  "total_products_processed": 35,
  "total_images_translated": 0
}
```

## 해결 방법

### 1. 단일 단계 실행 시 진행 상황 초기화

```bash
# 3단계 2번 하위 단계를 새로 시작하면서 진행 상황 파일 초기화
python cli/batch_cli.py single --step 32 --accounts 1 2 3 --quantity 100 --reset-progress

# 3단계 1번 1번 하위 단계를 새로 시작하면서 진행 상황 파일 초기화
python cli/batch_cli.py single --step 311 --accounts account_1 --quantity 50 --reset-progress
```

### 2. 다중 배치 실행 시 진행 상황 초기화

```bash
# 여러 계정에서 3단계를 새로 시작하면서 진행 상황 파일 초기화
python cli/batch_cli.py multi-batch 1 2 3 --step 32 --quantity 100 --reset-progress
```

## 동작 방식

### 초기화 대상 파일

`--reset-progress` 옵션이 활성화되면 다음 패턴의 진행 상황 파일들이 삭제됩니다:

```
progress_{계정ID}_{3단계하위단계}_{서버}.json
```

**3단계 하위 단계 목록:**
- `step3_1`, `step3_1_1`, `step3_1_2`, `step3_1_3`
- `step3_2`, `step3_2_1`, `step3_2_2`, `step3_2_3`
- `step3_3`, `step3_3_1`, `step3_3_2`, `step3_3_3`

**서버 목록:**
- `서버1`, `서버2`, `서버3`

### 예시 삭제 파일들

계정 `account_1`에 대해 다음과 같은 파일들이 삭제됩니다:

```
progress_account_1_step3_1_서버1.json
progress_account_1_step3_1_서버2.json
progress_account_1_step3_1_서버3.json
progress_account_1_step3_1_1_서버1.json
...
progress_account_1_step3_3_3_서버3.json
```

## 로그 출력 예시

```
🔄 3단계 진행 상황 파일 초기화 시작
   • 계정 account_1: 12개 파일 삭제
   • 계정 account_2: 8개 파일 삭제
   • 계정 account_3: 삭제할 진행 상황 파일 없음
🔄 3단계 진행 상황 파일 초기화 완료 - 총 20개 파일 삭제
```

## 주의사항

1. **3단계에만 적용**: 이 기능은 3단계(step 3) 관련 작업에만 적용됩니다.
2. **완전 초기화**: 모든 3단계 하위 단계의 진행 상황이 초기화됩니다.
3. **복구 불가**: 삭제된 진행 상황 파일은 복구할 수 없습니다.
4. **다중 배치**: 다중 배치 실행 시 첫 번째 배치에서만 초기화가 수행됩니다.

## 사용 시나리오

### 시나리오 1: 배치 작업 재시작

```bash
# 이전 배치 작업이 중단된 후 완전히 새로 시작
python cli/batch_cli.py single --step 32 --accounts 1 2 --quantity 200 --reset-progress
```

### 시나리오 2: 테스트 후 본격 실행

```bash
# 테스트 실행 후 진행 상황을 초기화하고 본격 실행
python cli/batch_cli.py single --step 311 --accounts account_test --quantity 10 --reset-progress
```

### 시나리오 3: 다중 계정 일괄 초기화

```bash
# 여러 계정의 진행 상황을 모두 초기화하고 새로 시작
python cli/batch_cli.py multi-batch 1 2 3 4 5 --step 33 --quantity 150 --reset-progress
```

## 기술적 세부사항

### 구현 위치

- **배치 매니저**: `batch/batch_manager.py`의 `_reset_step3_progress_files()` 메서드
- **CLI 인터페이스**: `cli/batch_cli.py`의 `--reset-progress` 옵션

### 파라미터 전달 경로

```
CLI args.reset_progress
  ↓
BatchCLI.run_single_step()
  ↓
BatchManager.run_single_step(reset_progress=True)
  ↓
BatchManager._reset_step3_progress_files()
```

이 기능을 통해 새로운 배치 작업을 깔끔하게 시작할 수 있으며, 기존 진행 상황으로 인한 키워드 제외 문제를 완전히 해결할 수 있습니다.