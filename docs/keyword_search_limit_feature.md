# 키워드 검색 상품 수 제한 기능

## 개요
키워드 검색 시 상품 수를 20개로 제한하는 기능이 추가되었습니다.

## 구현 내용

### 1. ProductEditorCore3 클래스 수정
- `search_products_by_keyword` 메서드에 `max_products` 매개변수 추가 (기본값: 20)
- `_limit_search_results` 메서드 추가로 상품 수 제한 로직 구현

### 2. 상품 수 제한 방법
1. **페이지 크기 조정**: 페이지네이션 드롭다운을 통해 페이지당 표시 개수를 20개로 설정
2. **JavaScript 숨기기**: 페이지 크기 조정이 불가능한 경우 JavaScript로 초과 상품 행을 숨김
3. **안전장치**: 모든 방법이 실패한 경우 원래 개수를 반환하여 시스템 안정성 보장

### 3. 적용 범위
- `product_editor_core3.py`의 `process_keyword_with_individual_modifications` 메서드
- Step 3-1, 3-2, 3-3 작업에서 자동으로 적용됨

## 사용법
```python
# 기본 사용 (20개 제한)
product_count = self.search_products_by_keyword(keyword)

# 사용자 정의 제한
product_count = self.search_products_by_keyword(keyword, max_products=30)
```

## 로그 메시지
- 검색 시작: "키워드 'XXX'로 상품 검색 시작 (최대 20개 제한)"
- 제한 적용: "검색 결과가 20개를 초과합니다. 상품 수를 제한합니다."
- 제한 완료: "상품 수 제한 완료: XX개로 제한됨"

## 장점
1. **성능 향상**: 대량의 상품 처리 시 메모리 사용량 감소
2. **안정성 증대**: 브라우저 과부하 방지
3. **처리 시간 단축**: 제한된 상품 수로 인한 빠른 처리
4. **유연성**: 필요에 따라 제한 수 조정 가능