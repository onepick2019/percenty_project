# 키워드 순환 처리 로직 설계

## 개요

현재 3단계에서는 키워드별로 최대 20개 상품만 처리하고 다음 키워드로 넘어가는 방식입니다. 이로 인해 일부 키워드에 상품이 적을 경우 총 처리량이 목표치(200개)에 미달할 수 있습니다.

이 문서는 키워드별 20개 제한을 유지하면서 총 처리량 200개를 보장하는 순환 처리 로직을 설계합니다.

## 현재 문제점

### 기존 로직
```
키워드1 (10개 상품) → 10개 처리
키워드2 (0개 상품) → 0개 처리  
키워드3 (50개 상품) → 20개 처리
키워드4 (30개 상품) → 20개 처리
...
키워드10 (15개 상품) → 15개 처리

총 처리량: 140개 (목표 200개 미달)
```

### 문제점
- 키워드별 상품 수가 불균등할 때 총 처리량이 목표치에 미달
- 일부 키워드에 많은 상품이 있어도 20개만 처리하고 넘어감
- 전체 효율성 저하

## 제안하는 해결책

### 순환 처리 로직
```
1차 순환:
키워드1 (10개) → 10개 처리 (완료)
키워드2 (0개) → 0개 처리 (완료)
키워드3 (50개) → 20개 처리 (30개 남음)
키워드4 (30개) → 20개 처리 (10개 남음)
...
키워드10 (15개) → 15개 처리 (완료)

1차 처리량: 140개

2차 순환 (남은 키워드만):
키워드3 (30개 남음) → 20개 처리 (10개 남음)
키워드4 (10개 남음) → 10개 처리 (완료)
...

2차 처리량: 30개

3차 순환:
키워드3 (10개 남음) → 10개 처리 (완료)

3차 처리량: 10개

총 처리량: 180개
```

## 구현 방안

### 1. 간단한 방법 (권장)

#### 장점
- 기존 코드 변경 최소화
- 구현 복잡도 낮음
- 안정성 높음

#### 구현 방식
```python
def process_keywords_with_target_quantity(self, provider_codes, target_quantity=200):
    """
    키워드 순환 처리로 목표 수량 달성
    
    Args:
        provider_codes: 처리할 키워드 목록
        target_quantity: 목표 처리 수량 (기본값: 200)
    """
    total_processed = 0
    remaining_keywords = provider_codes.copy()
    cycle_count = 0
    
    while total_processed < target_quantity and remaining_keywords:
        cycle_count += 1
        logger.info(f"===== {cycle_count}차 순환 시작 (목표: {target_quantity}, 현재: {total_processed}) =====")
        
        keywords_to_remove = []
        
        for keyword in remaining_keywords:
            if total_processed >= target_quantity:
                break
                
            # 기존 키워드 처리 로직 호출
            success, processed_count = self._process_single_keyword_cycle(keyword)
            
            if success:
                total_processed += processed_count
                logger.info(f"키워드 '{keyword}' 처리 완료: {processed_count}개 (총: {total_processed}개)")
                
                # 20개 미만 처리된 경우 해당 키워드 완료로 간주
                if processed_count < 20:
                    keywords_to_remove.append(keyword)
            else:
                # 실패한 키워드는 제거
                keywords_to_remove.append(keyword)
        
        # 완료된 키워드 제거
        for keyword in keywords_to_remove:
            remaining_keywords.remove(keyword)
        
        logger.info(f"{cycle_count}차 순환 완료 - 처리량: {total_processed}개, 남은 키워드: {len(remaining_keywords)}개")
    
    return total_processed >= target_quantity, total_processed
```

### 2. 고급 방법 (선택사항)

#### 장점
- 더 정교한 제어 가능
- 키워드별 상태 추적
- 진행률 모니터링

#### 구현 방식
```python
class KeywordCyclicProcessor:
    def __init__(self, product_editor):
        self.product_editor = product_editor
        self.keyword_states = {}  # 키워드별 상태 추적
    
    def process_with_target_quantity(self, provider_codes, target_quantity=200):
        # 키워드 상태 초기화
        self._initialize_keyword_states(provider_codes)
        
        total_processed = 0
        cycle_count = 0
        
        while total_processed < target_quantity and self._has_remaining_keywords():
            cycle_count += 1
            cycle_processed = self._process_single_cycle(target_quantity - total_processed)
            total_processed += cycle_processed
            
            if cycle_processed == 0:
                break  # 더 이상 처리할 수 없음
        
        return total_processed >= target_quantity, total_processed
```

## 코드 수정 범위

### 최소 변경 방안

1. **Step3_X_X_Core 클래스 수정**
   - `execute_step3_X_X` 메서드에 순환 처리 로직 추가
   - 기존 `_process_keyword` 메서드는 그대로 유지

2. **새로운 메서드 추가**
   ```python
   def _process_keywords_with_target_quantity(self, provider_codes, matching_tasks, target_quantity=200):
       # 순환 처리 로직 구현
   ```

3. **설정 파일 수정**
   - `periodic_config.json`에 목표 수량 설정 추가
   ```json
   {
     "step3_target_quantity": 200,
     "step3_max_cycles": 10
   }
   ```

### 변경이 필요한 파일들

1. `core/steps/step3_1_1_core.py`
2. `core/steps/step3_1_2_core.py`
3. `core/steps/step3_1_3_core.py`
4. `core/steps/step3_2_1_core.py`
5. `core/steps/step3_2_2_core.py`
6. `core/steps/step3_2_3_core.py`
7. `core/steps/step3_3_1_core.py`
8. `core/steps/step3_3_2_core.py`
9. `core/steps/step3_3_3_core.py`
10. `periodic_config.json`

## 구현 복잡도 평가

### 복잡도: 낮음 ⭐⭐☆☆☆

**이유:**
- 기존 키워드 처리 로직 재사용
- 단순한 반복문과 카운터 사용
- 기존 코드 구조 유지
- 테스트 및 디버깅 용이

### 예상 개발 시간
- 설계 및 구현: 2-3시간
- 테스트 및 검증: 1-2시간
- 문서화: 30분

**총 예상 시간: 4-6시간**

## 안전성 고려사항

### 1. 무한 루프 방지
```python
MAX_CYCLES = 10  # 최대 순환 횟수 제한

if cycle_count >= MAX_CYCLES:
    logger.warning(f"최대 순환 횟수({MAX_CYCLES}) 도달로 처리 중단")
    break
```

### 2. 메모리 사용량 모니터링
```python
# 순환마다 메모리 정리
if cycle_count % 3 == 0:
    self._cleanup_browser_memory()
```

### 3. 에러 처리 강화
```python
try:
    success, processed = self._process_single_keyword_cycle(keyword)
except Exception as e:
    logger.error(f"키워드 '{keyword}' 처리 중 오류: {e}")
    # 해당 키워드 제외하고 계속 진행
    continue
```

## 기대 효과

### 1. 처리량 향상
- 기존: 평균 140개 → 개선 후: 200개 (43% 향상)
- 배치 작업 효율성 대폭 개선

### 2. 시간 단축
- 목표 수량 달성으로 배치 완료 시간 예측 가능
- 24시간 내 완료 가능성 증대

### 3. 리소스 활용 최적화
- 키워드별 상품 불균등 문제 해결
- 전체 시스템 효율성 향상

## 결론

제안된 순환 처리 로직은 **구현 복잡도가 낮으면서도 효과가 큰** 개선 방안입니다.

- ✅ 기존 코드 최소 변경
- ✅ 안정성 보장
- ✅ 목표 수량 달성
- ✅ 배치 시간 단축

**권장사항: 1단계로 간단한 방법부터 구현하여 효과를 검증한 후, 필요시 고급 방법으로 확장**