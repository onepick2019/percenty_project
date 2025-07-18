# 청크사이즈별 타임아웃 및 메모리 누수 문제 해결 보고서

## 문제 상황

### 1. 타임아웃 계산 오류
- **문제**: 500개 수량을 청크사이즈 20개로 진행할 경우, 20개씩 25회 진행되어야 하지만 조기에 중단됨
- **원인**: 청크별 타임아웃이 전체 프로세스에 적용되어 부족한 시간 할당
- **기존 계산**: 청크크기(20) × 아이템당시간(195초) + 오버헤드(300초) = 4200초(70분)
- **실제 필요**: 총수량(500) × 아이템당시간(195초) + 청크별오버헤드(25×300초) = 105,000초(약 29시간)

### 2. 메모리 누수 문제
- **문제**: 타임아웃 발생 시 브라우저와 프롬프트가 닫히지 않아 메모리 점유
- **원인**: 프로세스 종료 시 관련 브라우저 프로세스 정리 로직 부재

## 해결 방안

### 1. 타임아웃 계산 방식 개선

#### 변경 전
```python
# 청크별 타임아웃 계산 (청크 크기 * 아이템당 시간 + 오버헤드)
chunk_timeout = chunk_size * base_time_per_item
overhead = 300
chunk_timeout += overhead
```

#### 변경 후
```python
# 전체 배치 타임아웃 계산 (총 수량 * 아이템당 시간 + 청크별 오버헤드)
total_timeout = quantity * base_time_per_item
chunk_overhead = total_chunks * 300
total_timeout += chunk_overhead
```

#### 주요 개선사항
- **전체 프로세스 기준 계산**: 청크별이 아닌 전체 배치 완료까지의 시간 계산
- **청크별 오버헤드 누적**: 각 청크마다 발생하는 브라우저 재시작 시간 반영
- **타임아웃 범위 확대**: 최소 20분, 최대 48시간으로 확장 (대용량 배치 작업 지원)

### 2. 브라우저 프로세스 정리 기능 추가

#### 새로운 정리 메서드
```python
def _cleanup_browser_processes(self, account_id: str):
    """타임아웃 시 관련 브라우저 프로세스 정리"""
    # Chrome/Edge 프로세스 찾기 및 종료
    # Python batch_cli.py 프로세스 정리
    # 정상 종료 → 강제 종료 단계적 접근
```

#### 프로세스 종료 단계
1. **정상 종료 시도**: `process.terminate()` + 10초 대기
2. **강제 종료**: `process.kill()` 실행
3. **브라우저 정리**: psutil을 사용한 관련 브라우저 프로세스 종료
4. **Python 프로세스 정리**: batch_cli.py 관련 프로세스 종료

### 3. 의존성 추가

#### requirements.txt 업데이트
```
psutil>=5.9.0  # 프로세스 관리를 위해 추가
```

## 예상 효과

### 1. 타임아웃 문제 해결
- **500개/청크20 예시**:
  - 기존: 4,200초 (70분) → 조기 중단
  - 개선: 105,000초 (29시간) → 정상 완료
- **적절한 시간 할당**: 실제 처리 시간에 맞는 타임아웃 설정

### 2. 메모리 누수 방지
- **완전한 정리**: 타임아웃 시 모든 관련 프로세스 종료
- **메모리 효율성**: 브라우저 프로세스 누적 방지
- **시스템 안정성**: 장시간 실행 시 메모리 부족 방지

### 3. 로그 개선
- **명확한 정보**: 전체 배치 타임아웃, 예상 청크 수 표시
- **정리 과정 추적**: 프로세스 종료 단계별 로그

## 테스트 권장사항

1. **소규모 테스트**: 50개/청크10으로 타임아웃 계산 확인
2. **중규모 테스트**: 200개/청크20으로 브라우저 정리 확인
3. **대규모 테스트**: 500개/청크20으로 전체 프로세스 검증

## 주의사항

1. **psutil 설치 필요**: `pip install psutil>=5.9.0`
2. **타임아웃 증가**: 대용량 배치의 경우 더 긴 실행 시간 예상
3. **시스템 리소스**: 프로세스 정리 시 일시적 CPU 사용량 증가 가능

## 파일 변경 목록

- `core/periodic_execution_manager.py`: 타임아웃 계산 및 프로세스 정리 로직 개선
- `requirements.txt`: psutil 의존성 추가
- `docs/timeout_fix_report.md`: 본 문서 생성