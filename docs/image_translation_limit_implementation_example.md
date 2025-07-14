# 이미지 번역 개수 기반 조기 종료 기능 구현 예시

## 1. BatchLimitManager 클래스 구현

```python
# core/utils/batch_limit_manager.py
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class BatchLimitManager:
    """배치 작업의 이중 제한 관리 클래스"""
    
    def __init__(self, product_limit: int = 200, translation_limit: int = 500):
        """
        Args:
            product_limit: 처리할 상품 수 제한
            translation_limit: 번역할 이미지 수 제한
        """
        self.product_limit = product_limit
        self.translation_limit = translation_limit
        self.processed_products = 0
        self.translated_images = 0
        self.start_time = None
        
        logger.info(f"BatchLimitManager 초기화 - 상품 제한: {product_limit}개, 번역 제한: {translation_limit}개")
    
    def should_continue(self) -> bool:
        """배치 작업 계속 여부 판단
        
        Returns:
            bool: 계속 진행 가능 여부
        """
        product_ok = self.processed_products < self.product_limit
        translation_ok = self.translated_images < self.translation_limit
        
        return product_ok and translation_ok
    
    def add_product(self, translated_count: int = 0) -> None:
        """상품 처리 완료 시 호출
        
        Args:
            translated_count: 이번 상품에서 번역된 이미지 수
        """
        self.processed_products += 1
        self.translated_images += translated_count
        
        logger.debug(f"상품 처리 추가 - 상품: {self.processed_products}/{self.product_limit}, "
                    f"번역: {self.translated_images}/{self.translation_limit}")
    
    def get_status(self) -> Dict[str, Any]:
        """현재 상태 반환
        
        Returns:
            Dict: 현재 진행 상태 정보
        """
        return {
            'products': f"{self.processed_products}/{self.product_limit}",
            'translations': f"{self.translated_images}/{self.translation_limit}",
            'product_progress': (self.processed_products / self.product_limit) * 100,
            'translation_progress': (self.translated_images / self.translation_limit) * 100,
            'can_continue': self.should_continue(),
            'reached_product_limit': self.processed_products >= self.product_limit,
            'reached_translation_limit': self.translated_images >= self.translation_limit
        }
    
    def get_termination_reason(self) -> str:
        """종료 사유 반환
        
        Returns:
            str: 종료 사유 메시지
        """
        if self.processed_products >= self.product_limit:
            return f"상품 처리 제한 달성 ({self.processed_products}/{self.product_limit})"
        elif self.translated_images >= self.translation_limit:
            return f"이미지 번역 제한 달성 ({self.translated_images}/{self.translation_limit})"
        else:
            return "정상 완료"
```

## 2. ImageTranslationTracker 클래스 구현

```python
# core/utils/image_translation_tracker.py
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class ImageTranslationTracker:
    """이미지 번역 개수 추적 클래스"""
    
    def __init__(self):
        self.session_translated_count = 0
        self.product_translated_count = 0
        self.last_translation_log = None
        
    def start_product_translation(self) -> None:
        """상품별 번역 시작 시 호출"""
        self.product_translated_count = 0
        logger.debug("상품별 이미지 번역 추적 시작")
    
    def add_translation_count(self, count: int) -> None:
        """번역된 이미지 개수 추가
        
        Args:
            count: 번역된 이미지 개수
        """
        if count > 0:
            self.session_translated_count += count
            self.product_translated_count += count
            
            logger.info(f"이미지 번역 완료: {count}개 (상품별: {self.product_translated_count}개, "
                       f"세션 총: {self.session_translated_count}개)")
    
    def get_product_count(self) -> int:
        """현재 상품에서 번역된 이미지 개수 반환
        
        Returns:
            int: 현재 상품의 번역된 이미지 개수
        """
        return self.product_translated_count
    
    def get_session_count(self) -> int:
        """세션 전체 번역된 이미지 개수 반환
        
        Returns:
            int: 세션 전체 번역된 이미지 개수
        """
        return self.session_translated_count
    
    def reset_session(self) -> None:
        """세션 카운터 초기화"""
        self.session_translated_count = 0
        self.product_translated_count = 0
        logger.info("이미지 번역 추적 세션 초기화")
```

## 3. ProductEditorCore3 클래스 확장

```python
# core/product_editor_core3.py (기존 클래스에 메서드 추가)

class ProductEditorCore3:
    def __init__(self, driver, config=None):
        # 기존 초기화 코드...
        self.translation_tracker = ImageTranslationTracker()
        
    def process_keyword_with_dual_limits(self, keyword: str, target_group: str, 
                                       task_data: Dict, limit_manager: BatchLimitManager) -> Tuple[bool, int, int]:
        """
        키워드로 검색된 상품을 개별 수정하되 이중 제한 적용
        
        Args:
            keyword: 검색 키워드
            target_group: 이동할 그룹명
            task_data: H~L열 수정 데이터
            limit_manager: BatchLimitManager 인스턴스
            
        Returns:
            Tuple[bool, int, int]: (성공 여부, 처리된 상품 수, 번역된 이미지 수)
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
                
                # 상품별 번역 추적 시작
                self.translation_tracker.start_product_translation()
                
                # H~L열 수정 작업 수행 (이미지 번역 포함)
                if self.process_product_modifications_with_translation_tracking(task_data):
                    # 이번 상품에서 번역된 이미지 개수 가져오기
                    product_translated_count = self.translation_tracker.get_product_count()
                    logger.info(f"상품 {i+1} 수정 완료 - 번역된 이미지: {product_translated_count}개")
                    
                    # 상품을 target_group으로 이동
                    if self.move_product_to_target_group(target_group):
                        # 제한 관리자에 결과 추가
                        limit_manager.add_product(product_translated_count)
                        total_processed += 1
                        total_translated += product_translated_count
                        
                        logger.info(f"상품 {i+1} 처리 완료 - 누적: 상품 {limit_manager.processed_products}개, "
                                   f"번역 {limit_manager.translated_images}개")
                    else:
                        logger.error(f"상품 {i+1} 그룹 이동 실패")
                else:
                    logger.warning(f"상품 {i+1} 수정 작업 실패")
                
                # 작업 간 대기
                time.sleep(DELAY_SHORT)
            
            logger.info(f"키워드 '{keyword}' 처리 완료 - 상품: {total_processed}개, 번역: {total_translated}개")
            return True, total_processed, total_translated
            
        except Exception as e:
            logger.error(f"키워드 '{keyword}' 처리 중 오류: {e}")
            return False, 0, 0
    
    def process_product_modifications_with_translation_tracking(self, task_data: Dict) -> bool:
        """상품 수정 작업 수행 및 번역 개수 추적
        
        Args:
            task_data: 수정할 작업 데이터
            
        Returns:
            bool: 성공 여부
        """
        try:
            # 기존 수정 작업 수행
            success = self.process_product_modifications(task_data)
            
            # 이미지 번역 작업이 포함된 경우 번역 개수 추적
            if success and self._has_image_translation_task(task_data):
                # 번역 로그에서 번역된 이미지 개수 파싱
                translated_count = self._parse_translation_count_from_logs()
                if translated_count > 0:
                    self.translation_tracker.add_translation_count(translated_count)
            
            return success
            
        except Exception as e:
            logger.error(f"상품 수정 작업 중 오류: {e}")
            return False
    
    def _has_image_translation_task(self, task_data: Dict) -> bool:
        """작업 데이터에 이미지 번역 작업이 포함되어 있는지 확인
        
        Args:
            task_data: 작업 데이터
            
        Returns:
            bool: 이미지 번역 작업 포함 여부
        """
        # I열(이미지 번역) 작업이 있는지 확인
        return task_data.get('I', '') in ['first', 'last', 'specific', 'special']
    
    def _parse_translation_count_from_logs(self) -> int:
        """최근 로그에서 번역된 이미지 개수 파싱
        
        Returns:
            int: 번역된 이미지 개수
        """
        try:
            # 로그 파일에서 최근 번역 완료 로그 찾기
            # 예: "식별된 8개 이미지 번역 처리 시작"
            # 실제 구현에서는 로그 파일을 읽거나 메모리에서 추적
            
            # 임시 구현: 실제로는 로그 파싱 또는 번역 핸들러에서 직접 반환
            return self._get_last_translation_count_from_handler()
            
        except Exception as e:
            logger.error(f"번역 개수 파싱 중 오류: {e}")
            return 0
    
    def _get_last_translation_count_from_handler(self) -> int:
        """이미지 번역 핸들러에서 마지막 번역 개수 가져오기
        
        Returns:
            int: 마지막 번역된 이미지 개수
        """
        try:
            # image_translation_handler에서 마지막 번역 개수 반환
            if hasattr(self, 'image_translation_handler') and hasattr(self.image_translation_handler, 'get_last_translation_count'):
                return self.image_translation_handler.get_last_translation_count()
            else:
                # 기본값 반환 (실제 구현에서는 정확한 개수 추적 필요)
                return 0
                
        except Exception as e:
            logger.error(f"번역 핸들러에서 개수 가져오기 실패: {e}")
            return 0
```

## 4. Step3_1_1_Core 클래스 확장

```python
# core/steps/step3_1_1_core.py (기존 클래스에 메서드 추가)

class Step3_1_1Core:
    def execute_step3_1_1_with_dual_limits(self, provider_codes: List[str], 
                                         product_limit: int = 200, 
                                         translation_limit: int = 500) -> Tuple[bool, Dict]:
        """
        3-1-1 단계 실행 (이중 제한 적용)
        
        Args:
            provider_codes: 처리할 키워드 목록
            product_limit: 상품 처리 제한
            translation_limit: 이미지 번역 제한
            
        Returns:
            Tuple[bool, Dict]: (성공 여부, 실행 결과)
        """
        try:
            logger.info(f"Step 3-1-1 실행 시작 (이중 제한) - 키워드: {len(provider_codes)}개")
            logger.info(f"제한 설정 - 상품: {product_limit}개, 번역: {translation_limit}개")
            
            # 제한 관리자 초기화
            limit_manager = BatchLimitManager(product_limit, translation_limit)
            
            # 키워드별 작업 목록 준비
            matching_tasks_dict = self._prepare_matching_tasks_dict(provider_codes)
            
            # 이중 제한 키워드 순환 처리
            success, total_processed, total_translated, completed_keywords = self._process_keywords_with_dual_limits(
                provider_codes, matching_tasks_dict, limit_manager
            )
            
            # 실행 결과 정리
            result = {
                'success': success,
                'total_processed_products': total_processed,
                'total_translated_images': total_translated,
                'completed_keywords': completed_keywords,
                'termination_reason': limit_manager.get_termination_reason(),
                'final_status': limit_manager.get_status()
            }
            
            logger.info(f"Step 3-1-1 실행 완료 - {result['termination_reason']}")
            logger.info(f"최종 결과: 상품 {total_processed}개, 번역 {total_translated}개")
            
            return success, result
            
        except Exception as e:
            logger.error(f"Step 3-1-1 실행 중 오류: {e}")
            return False, {'error': str(e)}
    
    def _process_keywords_with_dual_limits(self, provider_codes: List[str], 
                                         matching_tasks_dict: Dict, 
                                         limit_manager: BatchLimitManager) -> Tuple[bool, int, int, List[str]]:
        """
        키워드 순환 처리 + 이중 제한 적용
        
        Args:
            provider_codes: 처리할 키워드 목록
            matching_tasks_dict: 키워드별 작업 목록 딕셔너리
            limit_manager: 제한 관리자
            
        Returns:
            Tuple[bool, int, int, List[str]]: (성공 여부, 처리된 상품 수, 번역된 이미지 수, 완료된 키워드 목록)
        """
        completed_keywords = []
        remaining_keywords = provider_codes.copy()
        cycle_count = 0
        MAX_CYCLES = 10
        
        logger.info(f"이중 제한 키워드 순환 처리 시작")
        
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
                    success, processed_count, translated_count = self.product_editor.process_keyword_with_dual_limits(
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
        success = (limit_manager.processed_products >= limit_manager.product_limit or 
                  limit_manager.translated_images >= limit_manager.translation_limit)
        
        return success, limit_manager.processed_products, limit_manager.translated_images, completed_keywords
```

## 5. 설정 파일 확장

```json
// periodic_config.json
{
  "step3_1_1": {
    "product_limit": 200,
    "translation_limit": 500,
    "max_cycles": 10,
    "enable_dual_limits": true,
    "priority_limit": "translation"
  },
  "step3_1_2": {
    "product_limit": 200,
    "translation_limit": 500,
    "max_cycles": 10,
    "enable_dual_limits": true
  },
  "step3_1_3": {
    "product_limit": 200,
    "translation_limit": 500,
    "max_cycles": 10,
    "enable_dual_limits": true
  }
}
```

## 6. GUI 연동 예시

```python
# gui/batch_settings_dialog.py
class BatchSettingsDialog:
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        # 상품 수량 제한 설정
        self.product_limit_spinbox = QSpinBox()
        self.product_limit_spinbox.setRange(1, 1000)
        self.product_limit_spinbox.setValue(200)
        
        # 이미지 번역 제한 설정
        self.translation_limit_spinbox = QSpinBox()
        self.translation_limit_spinbox.setRange(1, 2000)
        self.translation_limit_spinbox.setValue(500)
        
    def get_settings(self):
        return {
            'product_limit': self.product_limit_spinbox.value(),
            'translation_limit': self.translation_limit_spinbox.value()
        }

# gui/batch_progress_monitor.py
class BatchProgressMonitor:
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        # 상품 처리 진행률 바
        self.product_progress_bar = QProgressBar()
        self.product_progress_label = QLabel("상품: 0/200")
        
        # 이미지 번역 진행률 바
        self.translation_progress_bar = QProgressBar()
        self.translation_progress_label = QLabel("번역: 0/500")
        
    def update_progress(self, status):
        # 상품 처리 진행률 업데이트
        self.product_progress_bar.setValue(int(status['product_progress']))
        self.product_progress_label.setText(status['products'])
        
        # 이미지 번역 진행률 업데이트
        self.translation_progress_bar.setValue(int(status['translation_progress']))
        self.translation_progress_label.setText(status['translations'])
```

## 7. 테스트 시나리오

### 시나리오 1: 상품 제한 먼저 도달
```python
# 상품 200개, 번역 500개 설정
# 키워드당 평균 1-2개 번역 → 상품 제한이 먼저 도달
# 예상 결과: 상품 200개, 번역 200-400개에서 종료
```

### 시나리오 2: 번역 제한 먼저 도달
```python
# 상품 200개, 번역 300개 설정
# 키워드당 평균 3-5개 번역 → 번역 제한이 먼저 도달
# 예상 결과: 상품 60-100개, 번역 300개에서 종료
```

### 시나리오 3: 정상 완료
```python
# 상품 500개, 번역 1000개 설정
# 키워드 10개, 각각 20개씩 → 총 200개 상품
# 예상 결과: 상품 200개, 번역 400-800개에서 정상 완료
```

## 8. 기대 효과

### 정밀한 배치 제어
- ✅ 상품 수량과 번역 개수 이중 제한
- ✅ 더 예측 가능한 배치 완료 시간
- ✅ 리소스 사용량 최적화

### 운영 효율성 향상
- ✅ GUI에서 동적 설정 가능
- ✅ 실시간 진행률 모니터링
- ✅ 조기 종료로 시간 절약

### 안정성 보장
- ✅ 기존 안전장치 유지
- ✅ 이중 제한으로 과부하 방지
- ✅ 세밀한 로깅 및 추적

## 결론

이 구현 예시는 **기존 키워드 순환 처리 로직과 완벽하게 통합**되어 더 강력하고 유연한 배치 제어를 제공합니다.

**구현 우선순위:**
1. BatchLimitManager 및 ImageTranslationTracker 클래스 구현
2. ProductEditorCore3에 이중 제한 메서드 추가
3. Step3_X_X_Core 클래스에 이중 제한 로직 통합
4. GUI 연동 및 설정 기능 추가
5. 테스트 및 검증

**예상 개발 시간: 9-12시간**