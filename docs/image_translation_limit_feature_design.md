# 이미지 번역 개수 기반 조기 종료 기능 설계

## 개요

3단계 배치 작업에서 키워드 순환 처리와 함께 **이미지 번역 개수 제한**을 추가하여 더 강력한 조기 종료 기능을 구현합니다.

- **기존 제한**: 배치 작업 수량 200개
- **추가 제한**: 이미지 번역 개수 500개 (GUI에서 동적 설정 가능)
- **동작 방식**: 두 제한 중 하나라도 달성하면 조기 종료

## 요구사항 분석

### 현재 이미지 번역 로직
```
상품 처리 → 이미지 번역 (first, last, specific, special) → '원클릭 이미지 번역' 버튼 클릭 → 번역된 이미지 개수 누적
```

### 로그 분석
```
2025-07-10 22:57:12,662 - image_translation_handler_new - INFO - 제한된 스캔 완료: 8개 이미지가 번역 대상으로 식별됨
2025-07-10 22:57:12,662 - image_translation_handler_new - INFO - 식별된 8개 이미지 번역 처리 시작
```

**핵심**: 각 상품마다 번역된 이미지 개수를 추적하여 총 누적 개수가 설정값에 도달하면 조기 종료

## 설계 방안

### 1. 이중 제한 시스템

```python
class BatchLimitManager:
    def __init__(self, product_limit=200, translation_limit=500):
        self.product_limit = product_limit
        self.translation_limit = translation_limit
        self.processed_products = 0
        self.translated_images = 0
        
    def should_continue(self):
        """배치 작업 계속 여부 판단"""
        return (self.processed_products < self.product_limit and 
                self.translated_images < self.translation_limit)
    
    def add_product(self, translated_count=0):
        """상품 처리 완료 시 호출"""
        self.processed_products += 1
        self.translated_images += translated_count
        
    def get_status(self):
        """현재 상태 반환"""
        return {
            'products': f"{self.processed_products}/{self.product_limit}",
            'translations': f"{self.translated_images}/{self.translation_limit}",
            'can_continue': self.should_continue()
        }
```

### 2. 이미지 번역 개수 추적

#### ImageTranslationManager 수정
```python
class ImageTranslationManager:
    def __init__(self, driver):
        self.driver = driver
        self.session_translated_count = 0  # 세션별 번역 개수
        
    def image_translate(self, action_value, image_type='detail'):
        """이미지 번역 실행 및 개수 추적"""
        try:
            # 기존 번역 로직 실행
            success, translated_count = self._execute_translation(action_value, image_type)
            
            if success:
                self.session_translated_count += translated_count
                logger.info(f"이미지 번역 완료: {translated_count}개 (세션 총: {self.session_translated_count}개)")
                
            return success, translated_count
            
        except Exception as e:
            logger.error(f"이미지 번역 중 오류: {e}")
            return False, 0
    
    def get_session_count(self):
        """세션별 번역 개수 반환"""
        return self.session_translated_count
    
    def reset_session_count(self):
        """세션 카운터 초기화"""
        self.session_translated_count = 0
```

### 3. ProductEditorCore3 수정

```python
class ProductEditorCore3:
    def __init__(self, driver, config=None):
        self.driver = driver
        self.image_translation_handler = ImageTranslationManager(driver)
        self.batch_limit_manager = None  # 배치 실행 시 초기화
        
    def process_keyword_with_individual_modifications_and_limits(self, keyword, target_group, task_data, limit_manager):
        """
        키워드로 검색된 상품을 개별 수정하되 이중 제한 적용
        
        Args:
            keyword: 검색 키워드
            target_group: 이동할 그룹명
            task_data: H~L열 수정 데이터
            limit_manager: BatchLimitManager 인스턴스
            
        Returns:
            tuple: (성공 여부, 처리된 상품 수, 번역된 이미지 수)
        """
        try:
            logger.info(f"키워드 '{keyword}' 상품들의 개별 수정 및 이동 시작 (이중 제한 적용)")
            
            total_processed = 0
            total_translated = 0
            
            # 키워드로 상품 검색 (상품 수 20개로 제한)
            product_count = self.search_products_by_keyword(keyword, max_products=20)
            
            if product_count == 0:
                logger.info(f"키워드 '{keyword}'로 검색된 상품이 없습니다.")
                return True, 0, 0
            
            logger.info(f"현재 페이지에 {product_count}개 상품 발견")
            
            # 현재 페이지의 모든 상품 처리
            for i in range(product_count):
                # 제한 확인
                if not limit_manager.should_continue():
                    logger.info(f"제한 도달로 상품 {i+1} 처리 중단")
                    logger.info(f"현재 상태: {limit_manager.get_status()}")
                    break
                    
                logger.info(f"상품 {i+1}/{product_count} 처리 중")
                
                # 상품 모달창 열기
                if not self.open_first_product_modal():
                    logger.error(f"상품 {i+1} 모달창 열기 실패")
                    continue
                
                # H~L열 수정 작업 수행 (이미지 번역 포함)
                product_translated_count = 0
                if self.process_product_modifications_with_translation_tracking(task_data):
                    # 이번 상품에서 번역된 이미지 개수 가져오기
                    product_translated_count = self._get_last_product_translation_count()
                    logger.info(f"상품 {i+1} 수정 완료 - 번역된 이미지: {product_translated_count}개")
                else:
                    logger.warning(f"상품 {i+1} 수정 작업 실패")
                
                # 상품을 target_group으로 이동
                if not self.move_product_to_target_group(target_group):
                    logger.error(f"상품 {i+1} 그룹 이동 실패")
                
                # 제한 관리자에 결과 추가
                limit_manager.add_product(product_translated_count)
                total_processed += 1
                total_translated += product_translated_count
                
                logger.info(f"상품 {i+1} 처리 완료 - 누적: 상품 {limit_manager.processed_products}개, 번역 {limit_manager.translated_images}개")
                
                # 작업 간 대기
                time.sleep(DELAY_SHORT)
            
            logger.info(f"키워드 '{keyword}' 처리 완료 - 상품: {total_processed}개, 번역: {total_translated}개")
            return True, total_processed, total_translated
            
        except Exception as e:
            logger.error(f"키워드 '{keyword}' 처리 중 오류: {e}")
            return False, 0, 0
    
    def process_product_modifications_with_translation_tracking(self, task_data):
        """상품 수정 작업 수행 및 번역 개수 추적"""
        try:
            # 번역 카운터 초기화
            self.image_translation_handler.reset_session_count()
            
            # 기존 수정 작업 수행
            success = self.process_product_modifications(task_data)
            
            return success
            
        except Exception as e:
            logger.error(f"상품 수정 작업 중 오류: {e}")
            return False
    
    def _get_last_product_translation_count(self):
        """마지막 상품에서 번역된 이미지 개수 반환"""
        return self.image_translation_handler.get_session_count()
```

### 4. Step3_X_X_Core 클래스 수정

```python
class Step3_1_1Core:
    def _process_keywords_with_dual_limits(self, provider_codes, matching_tasks_dict, product_limit=200, translation_limit=500):
        """
        키워드 순환 처리 + 이중 제한 적용
        
        Args:
            provider_codes: 처리할 키워드 목록
            matching_tasks_dict: 키워드별 작업 목록 딕셔너리
            product_limit: 상품 처리 제한 (기본값: 200)
            translation_limit: 이미지 번역 제한 (기본값: 500)
            
        Returns:
            Tuple[bool, int, int, List[str]]: (성공 여부, 처리된 상품 수, 번역된 이미지 수, 완료된 키워드 목록)
        """
        # 제한 관리자 초기화
        limit_manager = BatchLimitManager(product_limit, translation_limit)
        
        total_processed = 0
        total_translated = 0
        completed_keywords = []
        remaining_keywords = provider_codes.copy()
        cycle_count = 0
        MAX_CYCLES = 10
        
        logger.info(f"이중 제한 키워드 순환 처리 시작 - 상품 제한: {product_limit}개, 번역 제한: {translation_limit}개")
        
        while limit_manager.should_continue() and remaining_keywords and cycle_count < MAX_CYCLES:
            cycle_count += 1
            cycle_start_products = limit_manager.processed_products
            cycle_start_translations = limit_manager.translated_images
            keywords_to_remove = []
            
            logger.info(f"===== {cycle_count}차 순환 시작 =====") 
            logger.info(f"현재 상태: {limit_manager.get_status()}")
            
            for keyword in remaining_keywords:
                if not limit_manager.should_continue():
                    logger.info(f"제한 도달로 키워드 '{keyword}' 처리 중단")
                    break
                    
                try:
                    logger.info(f"키워드 '{keyword}' 처리 시작 ({cycle_count}차 순환)")
                    
                    # 키워드별 작업 목록 가져오기
                    matching_tasks = matching_tasks_dict.get(keyword, [])
                    if not matching_tasks:
                        logger.warning(f"키워드 '{keyword}'에 대한 작업이 없습니다")
                        keywords_to_remove.append(keyword)
                        continue
                    
                    # 첫 번째 작업에서 target_group 추출
                    target_group = matching_tasks[0].get('target_group')
                    task_data = matching_tasks[0]
                    
                    # 이중 제한 적용 키워드 처리
                    success, processed_count, translated_count = self.product_editor.process_keyword_with_individual_modifications_and_limits(
                        keyword=keyword,
                        target_group=target_group,
                        task_data=task_data,
                        limit_manager=limit_manager
                    )
                    
                    if success:
                        logger.info(f"키워드 '{keyword}' 처리 완료: 상품 {processed_count}개, 번역 {translated_count}개")
                        
                        # 20개 미만 처리된 경우 해당 키워드 완료로 간주
                        if processed_count < 20:
                            keywords_to_remove.append(keyword)
                            completed_keywords.append(keyword)
                            logger.info(f"키워드 '{keyword}' 완료 (처리된 상품이 20개 미만)")
                    else:
                        logger.warning(f"키워드 '{keyword}' 처리 실패")
                        keywords_to_remove.append(keyword)
                        
                except Exception as e:
                    logger.error(f"키워드 '{keyword}' 처리 중 오류: {e}")
                    keywords_to_remove.append(keyword)
            
            # 완료된 키워드 제거
            for keyword in keywords_to_remove:
                if keyword in remaining_keywords:
                    remaining_keywords.remove(keyword)
            
            cycle_products = limit_manager.processed_products - cycle_start_products
            cycle_translations = limit_manager.translated_images - cycle_start_translations
            
            logger.info(f"{cycle_count}차 순환 완료 - 이번 순환: 상품 {cycle_products}개, 번역 {cycle_translations}개")
            logger.info(f"총 누적: {limit_manager.get_status()}")
            
            # 이번 순환에서 아무것도 처리하지 못한 경우 중단
            if cycle_products == 0:
                logger.warning("이번 순환에서 처리된 상품이 없어 순환 중단")
                break
        
        # 최종 결과
        final_status = limit_manager.get_status()
        success = (limit_manager.processed_products >= product_limit or 
                  limit_manager.translated_images >= translation_limit)
        
        if limit_manager.processed_products >= product_limit:
            logger.info(f"상품 처리 제한 달성! {final_status['products']}")
        if limit_manager.translated_images >= translation_limit:
            logger.info(f"이미지 번역 제한 달성! {final_status['translations']}")
        
        return success, limit_manager.processed_products, limit_manager.translated_images, completed_keywords
```

## GUI 연동 방안

### 1. 설정 UI 추가
```python
# GUI에서 설정값 입력
class BatchSettingsDialog:
    def __init__(self):
        self.product_limit = 200  # 기본값
        self.translation_limit = 500  # 기본값
        
    def get_settings(self):
        return {
            'product_limit': self.product_limit,
            'translation_limit': self.translation_limit
        }
```

### 2. 실시간 진행률 표시
```python
# GUI에서 진행률 모니터링
class BatchProgressMonitor:
    def update_progress(self, limit_manager):
        status = limit_manager.get_status()
        
        # 상품 처리 진행률
        product_progress = (limit_manager.processed_products / limit_manager.product_limit) * 100
        
        # 이미지 번역 진행률  
        translation_progress = (limit_manager.translated_images / limit_manager.translation_limit) * 100
        
        # GUI 업데이트
        self.update_product_progress_bar(product_progress)
        self.update_translation_progress_bar(translation_progress)
        self.update_status_text(status)
```

## 설정 파일 확장

### periodic_config.json 수정
```json
{
  "step3_product_limit": 200,
  "step3_translation_limit": 500,
  "step3_max_cycles": 10,
  "step3_enable_dual_limits": true,
  "step3_priority_limit": "translation"
}
```

## 구현 복잡도 평가

### 복잡도: 중간 ⭐⭐⭐☆☆

**이유:**
- 기존 순환 처리 로직 확장
- 이미지 번역 개수 추적 로직 추가
- GUI 연동 필요
- 이중 제한 관리 시스템

### 예상 개발 시간
- 설계 및 구현: 4-5시간
- GUI 연동: 2-3시간
- 테스트 및 검증: 2-3시간
- 문서화: 1시간

**총 예상 시간: 9-12시간**

## 기대 효과

### 1. 정밀한 배치 제어
- 상품 수량과 번역 개수 이중 제한
- 더 예측 가능한 배치 완료 시간
- 리소스 사용량 최적화

### 2. 운영 효율성 향상
- GUI에서 동적 설정 가능
- 실시간 진행률 모니터링
- 조기 종료로 시간 절약

### 3. 안정성 보장
- 기존 안전장치 유지
- 이중 제한으로 과부하 방지
- 세밀한 로깅 및 추적

## 결론

제안된 이미지 번역 개수 기반 조기 종료 기능은 기존 키워드 순환 처리 로직과 완벽하게 통합 가능하며, **더 강력하고 유연한 배치 제어**를 제공합니다.

- ✅ 이중 제한 시스템 (상품 + 번역)
- ✅ GUI 동적 설정 지원
- ✅ 실시간 진행률 모니터링
- ✅ 기존 로직과 완전 호환

**권장사항: 기존 순환 처리 로직 구현 후 이 기능을 단계적으로 추가하여 안정성 확보**