# 스텝3 배치 작업 개발 가이드

## 개요

스텝3 배치 작업은 퍼센티 플랫폼에서 상품 정보를 자동으로 수정하는 배치 처리 시스템입니다. 이 시스템은 키워드 기반으로 상품을 검색하고, 개별 상품에 대해 지정된 수정 작업을 수행합니다.

## 시스템 아키텍처

### 핵심 컴포넌트

1. **배치 러너 (step3_batch_runner.py)**
   - 전체 배치 작업의 오케스트레이션 담당
   - 서버별 작업 분배 및 결과 집계
   - 브라우저 재시작 관리

2. **스텝 코어 모듈들**
   - `step3_1_core.py`: 서버1 전용 처리 로직
   - `step3_2_core.py`: 서버2 전용 처리 로직
   - `step3_3_core.py`: 서버3 전용 처리 로직

3. **상품 에디터 (product_editor_core3.py)**
   - 실제 상품 수정 작업 수행
   - 키워드 검색 및 상품 처리

### 처리 흐름

```
배치 시작
    ↓
서버별 작업 분배
    ↓
청크 단위 키워드 처리
    ↓
키워드별 상품 검색
    ↓
개별 상품 수정
    ↓
결과 집계 및 보고
```

## 주요 개발 이슈 및 해결 과정

### 1. 처리된 상품 수 부정확 문제

**문제**: 키워드로 검색된 상품이 0개인 경우에도 처리된 상품 수가 1개로 기록됨

**원인**: 
- `product_editor_core3.py`의 `process_keyword_with_individual_modifications` 메서드가 boolean 값만 반환
- 스텝 코어 모듈들에서 성공 시 하드코딩된 1을 반환

**해결책**:
```python
# product_editor_core3.py 수정
def process_keyword_with_individual_modifications(self, keyword: str) -> Tuple[bool, int]:
    # 반환 타입을 (성공 여부, 처리된 상품 수) 튜플로 변경
    return (True, total_processed)

# step3_x_core.py 수정
success, processed_count = product_editor.process_keyword_with_individual_modifications(provider_code)
if success:
    return True, processed_count  # 실제 처리된 상품 수 반환
```

### 2. 키워드 처리 개수 누적 문제

**문제**: 청크 단위 처리에서 마지막 청크 완료 시 이전 누적 결과가 덮어써짐

**원인**: 
```python
# 문제가 있던 코드
else:
    server_result = current_result  # 이전 누적 결과 덮어쓰기
    break
```

**해결책**:
```python
# 수정된 코드
else:
    if server_result is None:
        server_result = current_result
    else:
        # 마지막 청크 결과도 누적
        server_result['processed_keywords'] += current_result.get('processed_keywords', 0)
        server_result['failed_keywords'] += current_result.get('failed_keywords', 0)
        server_result['total_products_processed'] += current_result.get('total_products_processed', 0)
        # ... 기타 결과 누적
    break
```

### 3. 청크 기반 처리 시스템

**목적**: 메모리 사용량 최적화 및 브라우저 안정성 향상

**구현**:
- 키워드 목록을 지정된 크기(기본 5개)의 청크로 분할
- 각 청크 처리 후 브라우저 재시작
- 진행 상황 저장 및 복구 기능

```python
# 청크 분할 로직
keyword_chunks = [provider_codes[i:i + chunk_size] for i in range(0, total_keywords, chunk_size)]

for chunk_idx, keyword_chunk in enumerate(keyword_chunks):
    # 청크 처리
    chunk_result = self.execute_step3_1(keyword_chunk, account_info)
    
    # 마지막 청크가 아니면 브라우저 재시작
    if chunk_idx < total_chunks - 1:
        return {'restart_required': True, 'current_result': total_result}
```

## 배치 사용법

### 1. 기본 실행

```bash
# GUI를 통한 실행
python start_gui.py

# CLI를 통한 실행
python step3_batch_runner.py
```

### 2. 설정 파일

**percenty_id.xlsx**: 계정 정보 및 작업 목록
- 시트 구조:
  - `id`: 계정 ID
  - `provider_code`: 처리할 키워드
  - `server`: 대상 서버 (서버1, 서버2, 서버3)
  - `step`: 작업 단계 (step3)

### 3. 실행 옵션

```python
# 청크 크기 조정 (기본값: 5)
chunk_size = 3  # 더 작은 청크로 처리

# 특정 서버만 처리
servers_to_process = ["서버1"]  # 서버1만 처리

# 계정별 처리
account_info = {
    'id': 'account_001',
    'login_id': 'user@example.com',
    'password': 'password123'
}
```

### 4. 로그 확인

**로그 위치**: 
- 통합 로그: `logs/unified/`
- 계정별 로그: `logs/accounts/`
- 에러 로그: `logs/errors/`

**주요 로그 메시지**:
```
# 배치 시작
2025-06-12 20:20:50,123 - __main__ - INFO - 스텝3 배치 작업 시작

# 키워드 처리
2025-06-12 20:20:51,456 - step3_1_core - INFO - 키워드 'KEYWORD001' 처리 완료 (소요시간: 15.23초, 처리된 상품: 5개)

# 청크 완료
2025-06-12 20:20:52,789 - step3_1_core - INFO - 청크 1 완료 - 처리된 키워드: 2, 실패: 0, 처리된 상품: 8

# 배치 완료
2025-06-12 20:20:54,012 - __main__ - INFO - 배치 처리 완료 - 성공한 서버: 1, 실패한 서버: 0
```

### 5. 에러 처리

**일반적인 에러 상황**:
1. **브라우저 연결 오류**: 자동 재시작 시도
2. **로그인 실패**: 계정 정보 확인 필요
3. **상품 검색 실패**: 키워드 유효성 확인
4. **모달 팝업**: 자동 차단 시스템 동작

**복구 메커니즘**:
- 진행 상황 자동 저장
- 브라우저 재시작 후 중단 지점부터 재개
- 실패한 키워드 별도 기록

### 6. 성능 최적화

**권장 설정**:
```python
# 청크 크기 조정 (시스템 사양에 따라)
chunk_size = 3  # 저사양 시스템
chunk_size = 5  # 일반 시스템 (기본값)
chunk_size = 10 # 고사양 시스템

# 지연 시간 조정
delay_strategy = {
    'critical': 2.0,    # 중요 작업 후 지연
    'normal': 1.0,      # 일반 작업 후 지연
    'minimal': 0.5      # 최소 지연
}
```

## 모니터링 및 디버깅

### 1. 실시간 모니터링

```python
# 진행 상황 확인
tail -f logs/unified/step3_batch_*.log

# 에러 모니터링
tail -f logs/errors/step3_*.log
```

### 2. 성능 메트릭

- **처리 속도**: 키워드당 평균 처리 시간
- **성공률**: 전체 키워드 대비 성공한 키워드 비율
- **상품 처리량**: 시간당 처리된 상품 수

### 3. 문제 해결 가이드

**브라우저 관련 문제**:
```bash
# 크롬 드라이버 업데이트
# 브라우저 캐시 정리
# 헤드리스 모드 비활성화 (디버깅 시)
```

**메모리 관련 문제**:
```python
# 청크 크기 감소
chunk_size = 2

# 브라우저 재시작 빈도 증가
restart_interval = 3  # 3개 키워드마다 재시작
```

## 향후 개선 사항

### 1. 단기 개선
- [ ] 더 정교한 에러 분류 및 처리
- [ ] 실시간 진행률 표시 개선
- [ ] 배치 일시정지/재개 기능

### 2. 중기 개선
- [ ] 병렬 처리 지원 (멀티 브라우저)
- [ ] 웹 기반 모니터링 대시보드
- [ ] 자동 스케줄링 기능

### 3. 장기 개선
- [ ] 머신러닝 기반 최적화
- [ ] 클라우드 기반 스케일링
- [ ] API 기반 통합

## 결론

스텝3 배치 시스템은 안정적이고 확장 가능한 상품 수정 자동화 솔루션입니다. 청크 기반 처리와 자동 복구 메커니즘을 통해 대량의 상품을 안전하게 처리할 수 있으며, 상세한 로깅과 모니터링 기능을 제공합니다.

개발 과정에서 발견된 주요 이슈들이 해결되어 현재는 안정적으로 운영 가능한 상태입니다. 지속적인 모니터링과 피드백을 통해 더욱 개선해 나갈 예정입니다.