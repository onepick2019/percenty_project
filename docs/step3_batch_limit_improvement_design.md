# Step3 배치 작업 제한 개선 설계

## 문제점 분석

### 1. 현재 제한 로직의 문제점

#### 1.1 개별 키워드 단위 제한 적용
- **현재 상황**: `step3_product_limit`와 `step3_image_limit`가 각 키워드별로 개별 적용됨
- **문제**: 전체 배치 작업에 대한 누적 제한이 아닌 키워드별 제한으로 작동
- **예시**: 상품 제한 100개, 이미지 제한 500개 설정 시
  - 키워드 A: 최대 100개 상품, 500개 이미지
  - 키워드 B: 최대 100개 상품, 500개 이미지
  - 결과: 총 200개 상품, 1000개 이미지 처리 가능 (의도와 다름)

#### 1.2 청크 단위 재시작 시 키워드 중복 처리
- **현재 상황**: 브라우저 재시작 시 이전에 처리된 키워드가 제외되지 않음
- **문제**: 동일한 키워드가 여러 청크에서 반복 처리됨
- **원인**: `load_task_list_from_excel_with_server_filter`에서 완료된 키워드 필터링이 제대로 작동하지 않음

### 2. 개선 목표

#### 2.1 전체 배치 작업 단위 제한 적용
- 상품 제한: 전체 배치 작업에서 처리되는 총 상품 수 제한
- 이미지 제한: 전체 배치 작업에서 번역되는 총 이미지 수 제한
- 키워드별 기본 제한(20개)은 유지하되, 전체 제한이 우선 적용

#### 2.2 청크 단위 재시작 시 진행 상황 정확한 복구
- 완료된 키워드는 다음 청크에서 제외
- 누적 상품/이미지 카운터 정확한 복구
- 남은 키워드만 다음 청크에서 처리

## 해결 방안

### 1. 전체 배치 제한 관리자 클래스 생성

```python
class BatchLimitManager:
    """
    배치 작업 전체에 대한 상품 및 이미지 제한을 관리하는 클래스
    """
    
    def __init__(self, product_limit: int, image_limit: int):
        self.product_limit = product_limit
        self.image_limit = image_limit
        self.total_products_processed = 0
        self.total_images_translated = 0
        
    def can_process_more_products(self) -> bool:
        """더 많은 상품을 처리할 수 있는지 확인"""
        return self.total_products_processed < self.product_limit
        
    def can_translate_more_images(self) -> bool:
        """더 많은 이미지를 번역할 수 있는지 확인"""
        return self.total_images_translated < self.image_limit
        
    def add_processed_products(self, count: int):
        """처리된 상품 수 추가"""
        self.total_products_processed += count
        
    def add_translated_images(self, count: int):
        """번역된 이미지 수 추가"""
        self.total_images_translated += count
        
    def get_remaining_product_limit(self) -> int:
        """남은 상품 처리 가능 수량"""
        return max(0, self.product_limit - self.total_products_processed)
        
    def get_remaining_image_limit(self) -> int:
        """남은 이미지 번역 가능 수량"""
        return max(0, self.image_limit - self.total_images_translated)
        
    def is_batch_limit_reached(self) -> bool:
        """배치 제한에 도달했는지 확인"""
        return (self.total_products_processed >= self.product_limit or 
                self.total_images_translated >= self.image_limit)
```

### 2. Step3_1Core 클래스 수정

#### 2.1 BatchLimitManager 통합

```python
class Step3_1Core:
    def __init__(self, driver=None, server_name="서버1", restart_browser_callback=None, 
                 step3_product_limit=None, step3_image_limit=None):
        # 기존 초기화 코드...
        
        # 배치 제한 관리자 초기화
        self.batch_limit_manager = BatchLimitManager(
            product_limit=step3_product_limit or 100,
            image_limit=step3_image_limit or 500
        )
```

#### 2.2 키워드 처리 로직 수정

```python
def execute_step3_1(self, provider_codes: List[str], account_info: Dict = None) -> Dict:
    # 기존 초기화 코드...
    
    # 7. 키워드별 처리 (배치 제한 적용)
    for provider_code in provider_codes:
        # 배치 제한 확인
        if self.batch_limit_manager.is_batch_limit_reached():
            logger.info(f"배치 제한 달성 - 상품: {self.batch_limit_manager.total_products_processed}/{self.batch_limit_manager.product_limit}, "
                       f"이미지: {self.batch_limit_manager.total_images_translated}/{self.batch_limit_manager.image_limit}")
            logger.info(f"남은 키워드 {len(provider_codes) - provider_codes.index(provider_code)}개 처리 중단")
            break
            
        # 키워드별 처리 (동적 제한 적용)
        success, products_processed = self._process_keyword_with_batch_limit(provider_code, matching_tasks)
        
        if success:
            # 배치 제한 관리자에 결과 반영
            self.batch_limit_manager.add_processed_products(products_processed)
            # 이미지 수는 ProductEditorCore3에서 직접 업데이트
```

#### 2.3 동적 제한 적용 키워드 처리

```python
def _process_keyword_with_batch_limit(self, provider_code: str, matching_tasks: List[Dict]) -> Tuple[bool, int]:
    """
    배치 제한을 고려한 키워드 처리
    """
    # 남은 상품 처리 가능 수량 계산
    remaining_products = self.batch_limit_manager.get_remaining_product_limit()
    remaining_images = self.batch_limit_manager.get_remaining_image_limit()
    
    # 키워드별 최대 처리 상품 수 결정 (기본 20개와 남은 제한 중 작은 값)
    max_products_for_keyword = min(20, remaining_products)
    
    if max_products_for_keyword <= 0:
        logger.info(f"키워드 '{provider_code}' 처리 건너뜀 - 상품 제한 달성")
        return True, 0
        
    logger.info(f"키워드 '{provider_code}' 처리 시작 - 최대 상품: {max_products_for_keyword}개, 최대 이미지: {remaining_images}개")
    
    # ProductEditorCore3에 동적 제한 전달
    success, processed_count = self.product_editor.process_keyword_with_batch_limits(
        keyword=provider_code,
        target_group=target_group,
        task_data=task_data,
        max_products=max_products_for_keyword,
        max_images=remaining_images,
        batch_limit_manager=self.batch_limit_manager
    )
    
    return success, processed_count
```

### 3. ProductEditorCore3 클래스 수정

#### 3.1 배치 제한 인식 처리 메서드 추가

```python
def process_keyword_with_batch_limits(self, keyword, target_group, task_data, 
                                     max_products=20, max_images=None, 
                                     batch_limit_manager=None):
    """
    배치 제한을 고려한 키워드 처리
    """
    try:
        logger.info(f"키워드 '{keyword}' 배치 제한 적용 처리 시작 - 상품: {max_products}개, 이미지: {max_images}개")
        
        # 키워드로 상품 검색
        product_count = self.search_products_by_keyword(keyword, max_products=max_products)
        
        if product_count == 0:
            return True, 0
            
        total_processed = 0
        
        # 상품별 처리 (배치 제한 실시간 확인)
        for i in range(product_count):
            # 배치 제한 실시간 확인
            if batch_limit_manager and batch_limit_manager.is_batch_limit_reached():
                logger.info(f"상품 {i+1} 처리 전 배치 제한 달성 - 키워드 '{keyword}' 처리 중단")
                break
                
            # 상품 처리
            if self._process_single_product_with_batch_limit(task_data, batch_limit_manager):
                total_processed += 1
                
                # 배치 제한 관리자에 상품 처리 결과 반영
                if batch_limit_manager:
                    batch_limit_manager.add_processed_products(1)
                    
        return True, total_processed
        
    except Exception as e:
        logger.error(f"키워드 '{keyword}' 배치 제한 처리 중 오류: {e}")
        return False, 0
```

#### 3.2 이미지 번역 메서드 수정

```python
def image_translate(self, action_value, batch_limit_manager=None):
    """
    배치 제한을 고려한 이미지 번역
    """
    # 배치 제한 확인
    if batch_limit_manager and not batch_limit_manager.can_translate_more_images():
        logger.warning(f"배치 이미지 번역 제한 달성. 번역을 건너뜁니다.")
        return True
        
    # 실제 번역 수행
    translated_count = self.image_translation_handler.image_translate(action_value, 'detail')
    
    if translated_count > 0:
        # 배치 제한 관리자에 결과 반영
        if batch_limit_manager:
            batch_limit_manager.add_translated_images(translated_count)
            
        # 기존 카운터도 유지 (호환성)
        self.total_translated_images += translated_count
        self.current_product_translated_images += translated_count
        
        logger.info(f"이미지 번역 완료: +{translated_count}개 (배치 총합: {batch_limit_manager.total_images_translated if batch_limit_manager else 'N/A'}개)")
        return True
    else:
        return False
```

### 4. 진행 상황 복구 로직 개선

#### 4.1 정확한 키워드 필터링

```python
def _resume_from_progress(self, provider_codes: List[str], progress_file: str) -> Tuple[List[str], int, int]:
    """
    진행 상황에서 정확한 복구
    """
    if not os.path.exists(progress_file):
        return provider_codes, 0, 0
        
    try:
        with open(progress_file, 'r', encoding='utf-8') as f:
            progress_data = json.load(f)
            
        completed_keywords = progress_data.get('completed_keywords', [])
        total_products = progress_data.get('total_products_processed', 0)
        total_images = progress_data.get('total_images_translated', 0)
        
        # 완료된 키워드 제외
        remaining_keywords = [kw for kw in provider_codes if kw not in completed_keywords]
        
        logger.info(f"진행 상황 복구: 완료된 키워드 {len(completed_keywords)}개 제외, 남은 키워드 {len(remaining_keywords)}개")
        logger.info(f"누적 처리량: 상품 {total_products}개, 이미지 {total_images}개")
        
        return remaining_keywords, total_products, total_images
        
    except Exception as e:
        logger.error(f"진행 상황 복구 실패: {e}")
        return provider_codes, 0, 0
```

#### 4.2 배치 제한 관리자 상태 복구

```python
def execute_step3_1_with_browser_restart(self, provider_codes: List[str], chunk_size: int = 2, account_info: Dict = None) -> Dict:
    # 기존 진행 상황 복구
    remaining_keywords, accumulated_products, accumulated_images = self._resume_from_progress(provider_codes, progress_file)
    
    # 배치 제한 관리자 상태 복구
    self.batch_limit_manager.total_products_processed = accumulated_products
    self.batch_limit_manager.total_images_translated = accumulated_images
    
    logger.info(f"배치 제한 관리자 상태 복구: 상품 {accumulated_products}/{self.batch_limit_manager.product_limit}, "
               f"이미지 {accumulated_images}/{self.batch_limit_manager.image_limit}")
    
    # 이미 제한에 도달한 경우 조기 종료
    if self.batch_limit_manager.is_batch_limit_reached():
        logger.info("배치 제한에 이미 도달함 - 작업 종료")
        return {'success': True, 'limit_reached': True}
```

## 구현 순서

1. **BatchLimitManager 클래스 생성** (`core/common/batch_limit_manager.py`)
2. **Step3_1Core 클래스 수정** (배치 제한 관리자 통합)
3. **ProductEditorCore3 클래스 수정** (배치 제한 인식 메서드 추가)
4. **진행 상황 복구 로직 개선**
5. **다른 Step3 코어 클래스들에도 동일한 로직 적용**
6. **테스트 및 검증**

## 예상 효과

1. **정확한 제한 적용**: 전체 배치 작업에 대해 설정된 상품/이미지 제한이 정확히 적용됨
2. **메모리 효율성**: 불필요한 키워드 중복 처리 방지로 메모리 사용량 최적화
3. **진행 상황 정확성**: 청크 단위 재시작 시 정확한 진행 상황 복구
4. **사용자 의도 반영**: GUI에서 설정한 제한 값이 의도한 대로 작동

## 호환성 고려사항

1. **기존 로직 유지**: 키워드별 기본 제한(20개)은 그대로 유지
2. **점진적 적용**: 기존 메서드는 유지하고 새로운 메서드 추가
3. **로그 개선**: 배치 제한 상태를 명확히 보여주는 로그 추가
4. **설정 호환성**: 기존 GUI 설정 값과 완전 호환