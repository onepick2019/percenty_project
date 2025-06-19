# 배치 로깅 및 보고서 시스템 가이드

## 개요

이 문서는 퍼센티 프로젝트의 배치 처리 시스템에서 새롭게 추가된 로깅 및 보고서 기능에 대한 가이드입니다.

## 주요 기능

### 1. 시작 시간 기반 파일명

모든 로그 파일과 보고서는 배치 시작 시간을 기준으로 파일명이 생성됩니다.

**형식:** `YYYYMMDD_HHMMSS`

**예시:**
- `20241201_143052` (2024년 12월 1일 14시 30분 52초)

### 2. 계정별 로그 분리

각 계정의 실행 로그가 독립적인 파일로 저장됩니다.

**디렉토리 구조:**
```
logs/
├── accounts/
│   └── 20241201_143052/
│       ├── user1@example.com.log
│       ├── user2@example.com.log
│       └── user3@example.com.log
├── errors/
│   └── 20241201_143052/
│       ├── user1@example.com_errors.log
│       ├── user2@example.com_errors.log
│       └── user3@example.com_errors.log
├── reports/
│   └── 20241201_143052/
│       ├── batch_report_single_step_1_20241201_143052.md
│       └── summary_report_20241201_143052.md
└── batch_processor_20241201_143052.log
```

### 3. 배치 결과 보고서

#### 개별 배치 보고서

각 배치 작업 완료 후 자동으로 생성되는 상세 보고서입니다.

**포함 내용:**
- 작업 ID 및 실행 시간 정보
- 계정별 처리 결과 (성공/실패, 처리 수량)
- 오류 내용 (발생 시)
- 전체 요약 통계
- 로그 파일 위치

#### 종합 보고서

여러 배치 작업의 통합 결과를 보여주는 보고서입니다.

**포함 내용:**
- 전체 배치 작업 수
- 각 배치별 요약 정보
- 전체 통계 (총 계정 수, 성공률 등)

## 사용 방법

### 1. BatchManager 사용

```python
from batch.batch_manager import BatchManager

# 배치 매니저 초기화 (시작 시간 자동 설정)
batch_manager = BatchManager()

# 단일 단계 실행
result = batch_manager.run_single_step(
    step=1,
    accounts=['user1@example.com', 'user2@example.com'],
    quantity=100,
    concurrent=False
)

# 종합 보고서 생성
summary_report = batch_manager.generate_summary_report()
print(f"종합 보고서: {summary_report}")
```

### 2. 계정별 로그 확인

```python
# 특정 계정의 로그 확인
account_logger = batch_manager.account_loggers.get('user1@example.com')
if account_logger:
    account_logger.info("사용자 정의 로그 메시지")
    account_logger.error("오류 메시지")
```

### 3. 로그 파일 위치 확인

```python
# 시작 시간 확인
print(f"배치 시작 시간: {batch_manager.start_time}")

# 로그 디렉토리 확인
print(f"계정별 로그: logs/accounts/{batch_manager.start_time}/")
print(f"에러 로그: logs/errors/{batch_manager.start_time}/")
print(f"보고서: logs/reports/{batch_manager.start_time}/")
```

## 로그 파일 내용 예시

### 계정별 로그 파일 (user1@example.com.log)

```
2024-12-01 14:30:52,123 - INFO - [user1@example.com] === 1단계 실행 시작: 수량=100 ===
2024-12-01 14:30:52,124 - INFO - [user1@example.com] 브라우저 생성 시작: user1@example.com_browser
2024-12-01 14:30:55,456 - INFO - [user1@example.com] 브라우저 생성 성공: user1@example.com_browser
2024-12-01 14:30:56,789 - INFO - [user1@example.com] 로그인 성공
2024-12-01 14:31:02,345 - INFO - [user1@example.com] 1단계 실행 완료 - 처리: 100, 실패: 0
2024-12-01 14:31:03,678 - INFO - [user1@example.com] === 1단계 실행 완료 ===
```

### 에러 로그 파일 (user2@example.com_errors.log)

```
2024-12-01 14:31:15,234 - ERROR - [user2@example.com] 로그인 중 예외 발생: 비밀번호가 올바르지 않습니다
2024-12-01 14:31:15,235 - ERROR - [user2@example.com] === 1단계 실행 중 오류 ===
```

## 보고서 예시

### 개별 배치 보고서 (batch_report_single_step_1_20241201_143052.md)

```markdown
# 배치 실행 보고서

**작업 ID:** single_step_1_20241201_143052
**시작 시간:** 20241201_143052
**실행 시간:** 2024-12-01 14:30:52.123456
**완료 시간:** 2024-12-01 14:31:05.789012
**소요 시간:** 13.67초
**전체 성공 여부:** ✅ 성공

## 계정별 실행 결과

### ✅ user1@example.com
- **처리 완료:** 100개
- **처리 실패:** 0개
- **성공 여부:** 성공

### ❌ user2@example.com
- **처리 완료:** 0개
- **처리 실패:** 0개
- **성공 여부:** 실패
- **오류 내용:**
  - 로그인 실패

## 전체 요약

- **총 계정 수:** 2개
- **성공한 계정:** 1개
- **실패한 계정:** 1개
- **총 처리 완료:** 100개
- **총 처리 실패:** 0개
- **성공률:** 50.0%

## 상세 로그 파일

- **계정별 로그:** `logs/accounts/20241201_143052/`
- **에러 로그:** `logs/errors/20241201_143052/`
- **보고서:** `logs/reports/20241201_143052/`
```

## 장점

### 1. 디버깅 효율성 향상
- 계정별로 독립된 로그로 문제 추적 용이
- 에러 전용 로그로 문제점 빠른 파악

### 2. 배치 완료 후 분석
- 상세한 보고서로 전체 실행 결과 한눈에 파악
- 성공률 및 처리량 통계 제공

### 3. 로그 관리 개선
- 시작 시간 기반 파일명으로 실행 세션 구분
- 체계적인 디렉토리 구조로 로그 정리

### 4. 운영 편의성
- 자동 보고서 생성으로 수동 분석 작업 감소
- 마크다운 형식으로 가독성 높은 보고서

## 주의사항

1. **디스크 공간**: 계정별 로그 분리로 인한 파일 수 증가
2. **성능**: 다중 파일 핸들러 사용으로 약간의 성능 오버헤드
3. **로그 보존**: 오래된 로그 파일의 정리 정책 필요

## 향후 개선 계획

1. **로그 압축**: 오래된 로그 파일 자동 압축
2. **웹 대시보드**: 보고서를 웹에서 확인할 수 있는 인터페이스
3. **알림 기능**: 배치 완료 시 이메일/슬랙 알림
4. **로그 검색**: 특정 키워드로 로그 검색 기능