# Step 2-3 최적화 구현 계획서

## 🎯 목표
성공적으로 적용된 dropdown_utils_common.py 최적화를 Step 2-3에 적용하여 전체 프로세스 성능 향상

## 📋 대상 파일

### Step 2 파일들
- `percenty_new_step2_server1.py`
- `percenty_new_step2_server2.py` 
- `percenty_new_step2_server3.py`

### Step 3 파일들
- `percenty_new_step3_server1.py`
- `percenty_new_step3_server2.py`
- `percenty_new_step3_server3.py`

## 🔧 적용할 최적화 기법

### 1. dropdown_utils_common.py 통합
```python
# 기존 import 방식
from dropdown_utils2 import DropdownUtils2
from dropdown_utils3 import DropdownUtils3

# 최적화된 import 방식
from dropdown_utils_common import CommonDropdownUtils
```

### 2. 초기화 코드 최적화
```python
class OptimizedStepCore:
    def __init__(self, driver):
        self.driver = driver
        # 최적화된 공통 유틸리티 사용
        self.dropdown_utils = CommonDropdownUtils(driver)
        
        # 성능 모니터링 추가
        self.performance_metrics = {
            'dropdown_operations': [],
            'product_moves': [],
            'group_selections': []
        }
    
    def track_performance(self, operation, start_time):
        """성능 추적 메서드"""
        duration = time.time() - start_time
        if operation not in self.performance_metrics:
            self.performance_metrics[operation] = []
        self.performance_metrics[operation].append(duration)
        
        # 평균 시간 로깅
        avg_time = sum(self.performance_metrics[operation]) / len(self.performance_metrics[operation])
        logger.info(f"{operation} 평균 시간: {avg_time:.2f}초")
```

### 3. 상품 이동 메서드 최적화
```python
def move_product_to_group_optimized(self, product_index, target_group):
    """
    최적화된 상품 이동 메서드
    
    Args:
        product_index (int): 상품 인덱스
        target_group (str): 대상 그룹명
        
    Returns:
        bool: 성공 여부
    """
    start_time = time.time()
    
    try:
        logger.info(f"상품 {product_index}를 '{target_group}' 그룹으로 이동 시작 (최적화된 방식)")
        
        # 최적화된 공통 유틸리티 사용
        success = self.dropdown_utils.move_product_to_group(
            product_index=product_index,
            target_group=target_group,
            timeout=5  # 단축된 타임아웃
        )
        
        if success:
            logger.info(f"상품 {product_index} 이동 성공: '{target_group}'")
            self.track_performance('product_move', start_time)
            return True
        else:
            logger.error(f"상품 {product_index} 이동 실패: '{target_group}'")
            return False
            
    except Exception as e:
        logger.error(f"상품 이동 중 오류: {e}")
        return False
```

### 4. 에러 처리 및 복구 메커니즘
```python
class AutoRecoveryMixin:
    """자동 복구 기능을 제공하는 믹스인 클래스"""
    
    def execute_with_retry(self, func, max_retries=3, *args, **kwargs):
        """
        재시도 로직이 포함된 실행 메서드
        
        Args:
            func: 실행할 함수
            max_retries: 최대 재시도 횟수
            *args, **kwargs: 함수 인자
            
        Returns:
            함수 실행 결과
        """
        for attempt in range(max_retries):
            try:
                result = func(*args, **kwargs)
                if result:  # 성공한 경우
                    if attempt > 0:
                        logger.info(f"재시도 {attempt}회 후 성공")
                    return result
                    
            except Exception as e:
                logger.warning(f"시도 {attempt + 1}/{max_retries} 실패: {e}")
                
                if attempt == max_retries - 1:
                    logger.error(f"최대 재시도 횟수 초과: {e}")
                    raise e
                    
                # 지수 백오프 대기
                wait_time = 0.5 * (2 ** attempt)
                logger.info(f"{wait_time}초 대기 후 재시도")
                time.sleep(wait_time)
                
        return False
```

### 5. 로깅 시스템 개선
```python
import logging
from datetime import datetime

class PerformanceLogger:
    """성능 로깅 전용 클래스"""
    
    def __init__(self, step_name):
        self.step_name = step_name
        self.logger = logging.getLogger(f"performance_{step_name}")
        
        # 성능 로그 파일 설정
        handler = logging.FileHandler(f"performance_{step_name}.log")
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_operation(self, operation, duration, success=True, details=None):
        """작업 성능 로깅"""
        status = "SUCCESS" if success else "FAILED"
        message = f"{operation} - {status} - {duration:.3f}s"
        
        if details:
            message += f" - {details}"
            
        self.logger.info(message)
    
    def log_step_summary(self, total_time, operations_count, success_rate):
        """단계별 요약 로깅"""
        self.logger.info(
            f"STEP_SUMMARY - Total: {total_time:.2f}s, "
            f"Operations: {operations_count}, "
            f"Success Rate: {success_rate:.1f}%"
        )
```

## 📊 구현 단계별 계획

### Phase 1: Step 2 최적화 (1일)
1. **server1 최적화**
   - dropdown_utils_common 통합
   - 성능 모니터링 추가
   - 테스트 및 검증

2. **server2, server3 적용**
   - server1 패턴 복사 적용
   - 각 서버별 특성 고려 조정

### Phase 2: Step 3 최적화 (1일)
1. **동일한 패턴 적용**
   - Step 2에서 검증된 최적화 패턴 적용
   - 서버별 특성 반영

2. **통합 테스트**
   - 전체 프로세스 성능 측정
   - 안정성 검증

### Phase 3: 모니터링 및 최적화 (0.5일)
1. **성능 데이터 수집**
   - 각 단계별 성능 메트릭 분석
   - 병목 지점 식별

2. **추가 최적화**
   - 데이터 기반 미세 조정
   - 문서화 업데이트

## 🎯 예상 성과

### 성능 개선
- **Step 2 처리 시간**: 30-40% 단축
- **Step 3 처리 시간**: 30-40% 단축
- **전체 프로세스**: 25-35% 단축

### 안정성 향상
- **실패율 감소**: 50% 이상
- **자동 복구**: 90% 이상의 일시적 오류 자동 해결
- **로깅 품질**: 디버깅 시간 50% 단축

### 유지보수성
- **코드 중복 제거**: 공통 유틸리티 활용
- **일관된 패턴**: 모든 단계에서 동일한 최적화 패턴
- **모니터링**: 실시간 성능 추적 가능

## 🚀 시작 가이드

### 1. 백업 생성
```bash
# 현재 파일들 백업
cp percenty_new_step2_server1.py backup/percenty_new_step2_server1_backup.py
cp percenty_new_step2_server2.py backup/percenty_new_step2_server2_backup.py
cp percenty_new_step2_server3.py backup/percenty_new_step2_server3_backup.py
```

### 2. 첫 번째 파일 최적화
- `percenty_new_step2_server1.py`부터 시작
- dropdown_utils_common 통합
- 성능 모니터링 추가

### 3. 테스트 및 검증
- 기능 정상 작동 확인
- 성능 개선 측정
- 로그 품질 확인

### 4. 나머지 파일 적용
- 검증된 패턴을 다른 파일들에 적용
- 각 파일별 특성 고려 조정

## 📞 결론

이미 검증된 최적화 기법을 Step 2-3에 체계적으로 적용하여 전체 프로세스의 성능과 안정성을 크게 향상시킬 수 있습니다. 단계별 접근을 통해 안전하고 효과적인 최적화를 달성할 것입니다.