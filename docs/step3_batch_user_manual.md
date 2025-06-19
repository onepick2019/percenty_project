# 스텝3 배치 사용자 매뉴얼

## 목차
1. [시작하기](#시작하기)
2. [기본 사용법](#기본-사용법)
3. [설정 파일 준비](#설정-파일-준비)
4. [실행 방법](#실행-방법)
5. [결과 확인](#결과-확인)
6. [문제 해결](#문제-해결)
7. [고급 설정](#고급-설정)

## 시작하기

### 시스템 요구사항
- Windows 10 이상
- Python 3.8 이상
- Chrome 브라우저 최신 버전
- 최소 4GB RAM (권장: 8GB 이상)

### 필수 파일 확인
배치 실행 전 다음 파일들이 준비되어 있는지 확인하세요:

```
Percenty_Project/
├── percenty_id.xlsx          # 계정 정보 및 작업 목록
├── step3_batch_runner.py     # 배치 실행 파일
├── start_gui.py              # GUI 실행 파일
└── core/steps/               # 스텝 처리 모듈들
```

## 기본 사용법

### 1단계: 작업 목록 준비

`percenty_id.xlsx` 파일에 처리할 작업을 입력합니다:

| id | provider_code | server | step |
|----|---------------|--------|----- |
| account_001 | KEYWORD001 | 서버1 | step3 |
| account_001 | KEYWORD002 | 서버1 | step3 |
| account_002 | KEYWORD003 | 서버2 | step3 |

**컬럼 설명**:
- `id`: 계정 식별자
- `provider_code`: 검색할 키워드
- `server`: 처리할 서버 (서버1, 서버2, 서버3)
- `step`: 작업 단계 (step3 고정)

### 2단계: 배치 실행

#### GUI 방식 (권장)
```bash
python start_gui.py
```

1. GUI 창에서 "스텝3 배치" 버튼 클릭
2. 계정 선택
3. "시작" 버튼 클릭

#### CLI 방식
```bash
python step3_batch_runner.py
```

### 3단계: 진행 상황 모니터링

실행 중 콘솔에서 다음과 같은 로그를 확인할 수 있습니다:

```
2025-06-12 20:20:50,123 - INFO - 스텝3 배치 작업 시작
2025-06-12 20:20:51,456 - INFO - 키워드 'KEYWORD001' 처리 완료 (처리된 상품: 5개)
2025-06-12 20:20:52,789 - INFO - 청크 1 완료 - 처리된 키워드: 2개
```

## 설정 파일 준비

### Excel 파일 구조

**시트명**: 기본 시트 또는 'accounts'

**필수 컬럼**:
- `id`: 계정 고유 식별자
- `provider_code`: 검색 키워드
- `server`: 대상 서버
- `step`: 작업 단계

**선택 컬럼**:
- `login_id`: 로그인 이메일 (계정 검증용)
- `password`: 로그인 비밀번호 (계정 검증용)
- `description`: 작업 설명

### 예시 데이터

```excel
id          | provider_code | server | step  | login_id           | description
account_001 | BRAND_A      | 서버1  | step3 | user1@company.com | 브랜드A 상품 수정
account_001 | BRAND_B      | 서버1  | step3 | user1@company.com | 브랜드B 상품 수정
account_002 | CATEGORY_X   | 서버2  | step3 | user2@company.com | 카테고리X 상품 수정
```

## 실행 방법

### GUI 실행

1. **프로그램 시작**
   ```bash
   python start_gui.py
   ```

2. **계정 선택**
   - 드롭다운에서 처리할 계정 선택
   - 여러 계정이 있는 경우 하나씩 선택하여 실행

3. **배치 옵션 설정**
   - 청크 크기: 한 번에 처리할 키워드 수 (기본값: 5)
   - 서버 선택: 처리할 서버 선택 (전체 또는 개별)

4. **실행 시작**
   - "스텝3 배치 시작" 버튼 클릭
   - 진행 상황을 실시간으로 확인

### CLI 실행

```bash
# 기본 실행
python step3_batch_runner.py

# 특정 계정만 처리
python step3_batch_runner.py --account account_001

# 청크 크기 조정
python step3_batch_runner.py --chunk-size 3

# 특정 서버만 처리
python step3_batch_runner.py --servers 서버1
```

## 결과 확인

### 실행 완료 메시지

```
=== 배치 처리 결과 ===
전체 성공 여부: True
처리된 서버: 1개
실패한 서버: 0개
총 처리된 키워드: 5개
총 처리된 상품: 23개

서버별 상세 결과:
  서버1: 성공=True, 키워드=5개, 상품=23개

=== 배치 처리 완료 ===
```

### 로그 파일 확인

**위치**: `logs/` 폴더

- `unified/`: 통합 로그 파일
- `accounts/`: 계정별 상세 로그
- `errors/`: 에러 로그만 별도 저장

**로그 파일 명명 규칙**:
```
step3_batch_YYYYMMDD_HHMMSS.log
step3_account_001_YYYYMMDD_HHMMSS.log
```

### 처리 결과 해석

**성공적인 처리**:
```
키워드 'BRAND_A' 처리 완료 (소요시간: 15.23초, 처리된 상품: 8개)
```

**실패한 처리**:
```
키워드 'BRAND_B' 처리 실패 - 상품을 찾을 수 없음
```

**상품이 없는 경우**:
```
키워드 'BRAND_C'로 검색된 상품이 없습니다. 작업 완료.
```

## 문제 해결

### 일반적인 문제

#### 1. 브라우저 연결 오류

**증상**: "드라이버 연결 오류" 메시지

**해결책**:
```bash
# 크롬 드라이버 업데이트
# 브라우저 프로세스 종료 후 재시작
taskkill /f /im chrome.exe
taskkill /f /im chromedriver.exe
```

#### 2. 로그인 실패

**증상**: "로그인 실패" 또는 "계정 정보 불일치"

**해결책**:
1. Excel 파일의 로그인 정보 확인
2. 수동으로 로그인하여 계정 상태 확인
3. 2단계 인증 설정 확인

#### 3. 메모리 부족

**증상**: 브라우저가 느려지거나 응답 없음

**해결책**:
```python
# 청크 크기 감소
chunk_size = 2  # 기본값 5에서 2로 변경

# 더 자주 브라우저 재시작
```

#### 4. 키워드 검색 실패

**증상**: "상품을 찾을 수 없음" 메시지

**해결책**:
1. 키워드 철자 확인
2. 해당 서버에 상품이 실제로 존재하는지 확인
3. 검색 필터 설정 확인

### 디버깅 모드

문제 발생 시 디버깅 모드로 실행:

```bash
# 헤드리스 모드 비활성화 (브라우저 화면 표시)
python step3_batch_runner.py --debug

# 상세 로그 출력
python step3_batch_runner.py --verbose
```

### 로그 분석

**에러 패턴 확인**:
```bash
# 에러 로그만 필터링
findstr "ERROR" logs/unified/step3_batch_*.log

# 특정 키워드 관련 로그 확인
findstr "BRAND_A" logs/unified/step3_batch_*.log
```

## 고급 설정

### 성능 최적화

#### 청크 크기 조정

```python
# 시스템 사양별 권장 설정

# 저사양 (4GB RAM 이하)
chunk_size = 2
delay_between_actions = 3.0

# 일반 사양 (4-8GB RAM)
chunk_size = 5  # 기본값
delay_between_actions = 2.0

# 고사양 (8GB RAM 이상)
chunk_size = 10
delay_between_actions = 1.0
```

#### 지연 시간 설정

```python
# config.py에서 설정 가능
DELAY_SETTINGS = {
    'page_load': 3.0,      # 페이지 로딩 대기
    'element_wait': 2.0,   # 요소 대기 시간
    'action_delay': 1.0,   # 액션 간 지연
    'critical_delay': 5.0  # 중요 작업 후 지연
}
```

### 병렬 처리 (실험적)

```python
# 여러 계정 동시 처리 (주의: 리소스 사용량 증가)
parallel_accounts = 2  # 동시 처리할 계정 수
```

### 자동 재시도 설정

```python
# 실패 시 재시도 횟수
max_retries = 3

# 재시도 간격 (초)
retry_delay = 30

# 브라우저 재시작 후 재시도
browser_restart_on_failure = True
```

### 모니터링 설정

```python
# 진행 상황 저장 간격
progress_save_interval = 5  # 5개 키워드마다 저장

# 상세 로그 레벨
log_level = 'DEBUG'  # INFO, WARNING, ERROR, DEBUG

# 로그 파일 최대 크기
max_log_size = '10MB'
```

## 베스트 프랙티스

### 1. 실행 전 체크리스트

- [ ] Excel 파일 데이터 검증
- [ ] 계정 로그인 상태 확인
- [ ] 브라우저 및 드라이버 버전 확인
- [ ] 충분한 디스크 공간 확보
- [ ] 네트워크 연결 상태 확인

### 2. 대량 처리 시 권장사항

- 청크 크기를 작게 설정 (3-5개)
- 정기적인 진행 상황 백업
- 시스템 리소스 모니터링
- 오프피크 시간대 실행

### 3. 안전한 운영

- 테스트 계정으로 먼저 검증
- 중요한 작업은 수동 확인 후 실행
- 정기적인 로그 파일 정리
- 백업 및 복구 계획 수립

## 지원 및 문의

문제 발생 시 다음 정보를 포함하여 문의하세요:

1. **에러 메시지**: 정확한 에러 내용
2. **로그 파일**: 관련 로그 파일 첨부
3. **실행 환경**: OS, 브라우저 버전 등
4. **재현 단계**: 문제 발생까지의 단계
5. **Excel 데이터**: 문제가 된 작업 데이터 (개인정보 제외)

---

**버전**: 1.0  
**최종 업데이트**: 2025-06-12  
**작성자**: AI Assistant