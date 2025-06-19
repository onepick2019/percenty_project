# 배치분할 중단 기능 구현 가이드

## 개요

이 문서는 1단계 작업에서 비그룹상품 카운트가 0이 되었을 때 후속 배치분할을 자동으로 중단하는 기능의 구현 내용을 설명합니다.

## 문제 상황

기존에는 대량의 상품(예: 100개)을 작은 배치(예: 20개씩 5번)로 나누어 처리할 때, 중간에 비그룹상품이 모두 소진되어도 남은 배치분할이 계속 실행되는 문제가 있었습니다.

**예시:**
- 총 100개 상품을 20개씩 5번 배치분할로 처리
- 3번째 배치 후 비그룹상품이 0개가 됨
- 기존: 4번째, 5번째 배치도 계속 실행 (불필요한 작업)
- 개선: 3번째 배치 후 자동 중단

## 구현 내용

### 1. Step1Core 수정 (`core/steps/step1_core.py`)

#### 1.1 결과 구조체에 중단 플래그 추가

```python
result = {
    'success': False,
    'processed': 0,
    'failed': 0,
    'errors': [],
    'product_count_before': 0,
    'product_count_after': 0,
    'should_stop_batch': False  # 배치분할 중단 플래그
}
```

#### 1.2 실행 전 비그룹상품 확인

```python
if available_products == 0:
    logger.error("비그룹상품 목록이 비어있습니다.")
    result['errors'].append("비그룹상품 목록이 비어있습니다.")
    result['should_stop_batch'] = True  # 배치분할 중단 플래그 설정
    return result
```

#### 1.3 실행 후 비그룹상품 확인

```python
final_products = self._check_product_count()
result['product_count_after'] = final_products
logger.info(f"📊 실행 후 비그룹상품 수량: {final_products}개")

# 비그룹상품이 0개가 되면 배치분할 중단 플래그 설정
if final_products == 0:
    result['should_stop_batch'] = True
    logger.warning("⚠️ 비그룹상품이 0개가 되었습니다. 후속 배치분할을 중단합니다.")
```

### 2. BatchManager 수정 (`batch/batch_manager.py`)

#### 2.1 배치분할 중단 로직 추가

```python
chunk_result = step_core.execute_step1(current_chunk_size)

# 결과 누적
total_result['processed'] += chunk_result['processed']
total_result['failed'] += chunk_result['failed']
total_result['errors'].extend(chunk_result['errors'])
total_result['chunks_completed'] += 1

account_logger.info(f"청크 {chunk_idx + 1} 완료: 처리 {chunk_result['processed']}개, 실패 {chunk_result['failed']}개")

# 배치분할 중단 플래그 확인
if chunk_result.get('should_stop_batch', False):
    account_logger.warning(f"⚠️ 청크 {chunk_idx + 1}에서 비그룹상품이 0개가 되어 후속 배치분할을 중단합니다.")
    account_logger.info(f"총 {chunk_idx + 1}/{total_chunks} 청크 완료 후 중단")
    # 현재 브라우저 종료 후 루프 탈출
    self.browser_manager.close_browser(current_browser_id)
    break
```

#### 2.2 브라우저 재시작 로직 개선

```python
# 마지막 청크가 아니면 브라우저 재시작
if chunk_idx < total_chunks - 1:
    # 브라우저 재시작 로직
    # ...
else:
    # 마지막 청크인 경우 브라우저 종료
    self.browser_manager.close_browser(current_browser_id)
```

## 작동 방식

### 1. 실행 흐름

1. **배치분할 시작**: 총 수량을 청크 크기로 나누어 배치분할 계획 수립
2. **각 청크 실행**: Step1Core.execute_step1() 호출
3. **비그룹상품 확인**: 실행 전/후 비그룹상품 카운트 체크
4. **중단 플래그 확인**: should_stop_batch 플래그 확인
5. **조건부 중단**: 플래그가 True이면 후속 배치분할 중단

### 2. 중단 조건

- **실행 전**: 비그룹상품이 0개인 경우
- **실행 후**: 비그룹상품이 0개가 된 경우

### 3. 로그 메시지

```
⚠️ 비그룹상품이 0개가 되었습니다. 후속 배치분할을 중단합니다.
⚠️ 청크 3에서 비그룹상품이 0개가 되어 후속 배치분할을 중단합니다.
총 3/5 청크 완료 후 중단
```

## GUI 적용

GUI에서는 CLI를 통해 배치 작업을 실행하므로, 별도의 수정 없이 자동으로 이 기능이 적용됩니다.

### GUI 사용 시 동작

1. GUI에서 다중 배치 실행
2. 각 계정-단계 조합마다 별도의 CLI 프로세스 실행
3. CLI에서 BatchManager 호출
4. BatchManager에서 배치분할 중단 로직 적용
5. 중단 시 해당 프로세스만 종료, 다른 프로세스는 계속 실행

## 테스트 방법

### 1. 수동 테스트

```bash
# CLI를 통한 테스트
python cli/batch_cli.py single --step 1 --accounts account_1 --quantity 100
```

### 2. 자동 테스트

```bash
# 테스트 스크립트 실행
python test_batch_stop.py
```

## 주의사항

### 1. 1단계 전용 기능

- 이 기능은 1단계(상품 수정)에서만 적용됩니다.
- 다른 단계(2-6단계)에서는 비그룹상품보기 화면을 열어보는 과정이 없으므로 해당되지 않습니다.

### 2. 독립적인 배치분할

- 각 계정-단계 조합은 독립적으로 실행됩니다.
- 한 계정에서 배치분할이 중단되어도 다른 계정의 작업에는 영향을 주지 않습니다.

### 3. 브라우저 관리

- 배치분할 중단 시 현재 브라우저는 자동으로 종료됩니다.
- 메모리 누수를 방지하기 위해 적절한 리소스 정리가 수행됩니다.

## 향후 개발 고려사항

### 1. Steps 2-6 개발 시

- 각 단계별로 `stepX_core.py` 파일 구조 유지
- `product_editor_core.py`와 동일한 패턴으로 개발
- 비그룹상품 카운트 로직은 1단계에서만 필요

### 2. 아키텍처 일관성

- SOLID 원칙 준수
- Clean Architecture 적용
- TDD 방식으로 개발

### 3. GUI 우선 개발

- GUI가 CLI에 종속되지 않도록 설계
- GUI 환경에서의 사용성 우선 고려
- CLI는 보완적 역할로 유지

## 결론

이번 구현으로 배치분할 작업의 효율성이 크게 개선되었습니다. 비그룹상품이 소진된 후 불필요한 배치분할이 실행되지 않아 시간과 리소스를 절약할 수 있습니다. 또한 명확한 로그 메시지를 통해 사용자가 작업 상황을 쉽게 파악할 수 있습니다.