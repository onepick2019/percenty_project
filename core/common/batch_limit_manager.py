import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class BatchLimitManager:
    """
    배치 작업 전체에 대한 상품 및 이미지 제한을 관리하는 클래스
    
    이 클래스는 다음 기능을 제공합니다:
    - 전체 배치 작업에 대한 상품 처리 수량 제한
    - 전체 배치 작업에 대한 이미지 번역 수량 제한
    - 실시간 제한 상태 확인
    - 남은 처리 가능 수량 계산
    """
    
    def __init__(self, product_limit: int, image_limit: int):
        """
        배치 제한 관리자 초기화
        
        Args:
            product_limit: 전체 배치에서 처리할 최대 상품 수
            image_limit: 전체 배치에서 번역할 최대 이미지 수
        """
        self.product_limit = product_limit
        self.image_limit = image_limit
        self.total_products_processed = 0
        self.total_images_translated = 0
        self.current_chunk_images_translated = 0  # 현재 청크에서만의 번역 수량
        
        logger.info(f"배치 제한 관리자 초기화 - 상품 제한: {product_limit}개, 이미지 제한: {image_limit}개")
        
    def can_process_more_products(self) -> bool:
        """
        더 많은 상품을 처리할 수 있는지 확인
        
        Returns:
            bool: 상품 처리 가능 여부
        """
        return self.total_products_processed < self.product_limit
        
    def can_translate_more_images(self) -> bool:
        """
        더 많은 이미지를 번역할 수 있는지 확인
        
        Returns:
            bool: 이미지 번역 가능 여부
        """
        return self.total_images_translated < self.image_limit
        
    def add_processed_products(self, count: int):
        """
        처리된 상품 수 추가
        
        Args:
            count: 추가할 상품 수
        """
        if count > 0:
            self.total_products_processed += count
            logger.debug(f"상품 처리 수 업데이트: +{count}개 (총 {self.total_products_processed}/{self.product_limit}개)")
        
    def add_translated_images(self, count: int):
        """
        번역된 이미지 수 추가
        
        Args:
            count: 추가할 이미지 수
        """
        if count > 0:
            self.total_images_translated += count
            self.current_chunk_images_translated += count
            logger.debug(f"이미지 번역 수 업데이트: +{count}개 (총 {self.total_images_translated}/{self.image_limit}개, 현재 청크: {self.current_chunk_images_translated}개)")
    
    def reset_current_chunk_counter(self):
        """
        현재 청크의 이미지 번역 카운터 초기화
        """
        self.current_chunk_images_translated = 0
        logger.debug("현재 청크 이미지 번역 카운터 초기화")
    
    def get_current_chunk_images_translated(self) -> int:
        """
        현재 청크에서 번역된 이미지 수 반환
        
        Returns:
            int: 현재 청크에서 번역된 이미지 수
        """
        return self.current_chunk_images_translated
        
    def get_remaining_product_limit(self) -> int:
        """
        남은 상품 처리 가능 수량 계산
        
        Returns:
            int: 남은 상품 처리 가능 수량 (0 이상)
        """
        return max(0, self.product_limit - self.total_products_processed)
        
    def get_remaining_image_limit(self) -> int:
        """
        남은 이미지 번역 가능 수량 계산
        
        Returns:
            int: 남은 이미지 번역 가능 수량 (0 이상)
        """
        return max(0, self.image_limit - self.total_images_translated)
        
    def is_batch_limit_reached(self) -> bool:
        """
        배치 제한에 도달했는지 확인
        
        Returns:
            bool: 상품 또는 이미지 제한 중 하나라도 도달했으면 True
        """
        product_limit_reached = self.total_products_processed >= self.product_limit
        image_limit_reached = self.total_images_translated >= self.image_limit
        
        return product_limit_reached or image_limit_reached
        
    def get_limit_status(self) -> Dict[str, Any]:
        """
        현재 제한 상태 정보 반환
        
        Returns:
            Dict: 제한 상태 정보
        """
        return {
            'product_limit': self.product_limit,
            'image_limit': self.image_limit,
            'products_processed': self.total_products_processed,
            'images_translated': self.total_images_translated,
            'remaining_products': self.get_remaining_product_limit(),
            'remaining_images': self.get_remaining_image_limit(),
            'product_limit_reached': self.total_products_processed >= self.product_limit,
            'image_limit_reached': self.total_images_translated >= self.image_limit,
            'batch_limit_reached': self.is_batch_limit_reached()
        }
        
    def log_current_status(self, context: str = ""):
        """
        현재 제한 상태를 로그로 출력
        
        Args:
            context: 로그 컨텍스트 (선택적)
        """
        status = self.get_limit_status()
        context_str = f"[{context}] " if context else ""
        
        logger.info(f"{context_str}배치 제한 상태 - "
                   f"상품: {status['products_processed']}/{status['product_limit']}개 "
                   f"(남은 수량: {status['remaining_products']}개), "
                   f"이미지: {status['images_translated']}/{status['image_limit']}개 "
                   f"(남은 수량: {status['remaining_images']}개)")
                   
        if status['batch_limit_reached']:
            if status['product_limit_reached']:
                logger.warning(f"{context_str}상품 처리 제한에 도달했습니다!")
            if status['image_limit_reached']:
                logger.warning(f"{context_str}이미지 번역 제한에 도달했습니다!")
                
    def reset_counters(self):
        """
        카운터 초기화 (테스트 또는 새로운 배치 시작 시 사용)
        """
        logger.info("배치 제한 관리자 카운터 초기화")
        self.total_products_processed = 0
        self.total_images_translated = 0
        self.current_chunk_images_translated = 0
        
    def set_accumulated_counts(self, products: int, images: int):
        """
        누적 카운터 설정 (진행 상황 복구 시 사용)
        
        Args:
            products: 누적 처리된 상품 수
            images: 누적 번역된 이미지 수
        """
        self.total_products_processed = products
        self.total_images_translated = images
        
        logger.info(f"배치 제한 관리자 누적 카운터 설정 - "
                   f"상품: {products}개, 이미지: {images}개")
                   
    def calculate_keyword_limits(self, keyword_product_limit: int = 20) -> tuple[int, int]:
        """
        현재 키워드에 적용할 동적 제한 계산
        
        Args:
            keyword_product_limit: 키워드별 기본 상품 제한 (기본값: 20)
            
        Returns:
            tuple: (키워드 상품 제한, 키워드 이미지 제한)
        """
        # 남은 상품 처리 가능 수량과 키워드 기본 제한 중 작은 값
        remaining_products = self.get_remaining_product_limit()
        keyword_max_products = min(keyword_product_limit, remaining_products)
        
        # 남은 이미지 번역 가능 수량
        remaining_images = self.get_remaining_image_limit()
        
        return keyword_max_products, remaining_images
        
    def should_stop_batch(self) -> bool:
        """
        배치 작업을 중단해야 하는지 확인
        
        Returns:
            bool: 배치 작업 중단 여부
        """
        return self.is_batch_limit_reached()
        
    def get_progress_percentage(self) -> Dict[str, float]:
        """
        진행률 계산
        
        Returns:
            Dict: 상품 및 이미지 처리 진행률
        """
        product_progress = (self.total_products_processed / self.product_limit * 100) if self.product_limit > 0 else 0
        image_progress = (self.total_images_translated / self.image_limit * 100) if self.image_limit > 0 else 0
        
        return {
            'product_progress': round(product_progress, 2),
            'image_progress': round(image_progress, 2)
        }