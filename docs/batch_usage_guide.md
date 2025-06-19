# Percenty 배치 프로세서 사용 가이드

## 개요

Percenty 프로젝트에서는 두 가지 방식으로 배치 작업을 실행할 수 있습니다:

1. **대화형 인터페이스**: `batch_processor_new.py`
2. **명령줄 인터페이스**: `cli/batch_cli.py`

## 1. 대화형 인터페이스 (batch_processor_new.py)

### 기본 실행

```bash
python batch_processor_new.py
```

### 실행 과정

실행하면 다음과 같이 대화형으로 설정을 입력해야 합니다:

1. **계정 선택**
   ```
   📋 사용 가능한 계정:
       1. account_1 (onepick2019@gmail.com) - 활성
       2. account_2 (wop31garam@gmail.com) - 활성
       3. account_3 (wop32gsung@gmail.com) - 활성
       4. account_4 (wop33gogos@gmail.com) - 활성
       5. account_5 (wop34goyos@gmail.com) - 활성
       6. account_6 (wop35goens@gmail.com) - 활성
       7. account_7 (wop36gurum@gmail.com) - 활성
   
   계정 선택 방법:
       • 번호로 선택: 1,2,3 또는 1-3
       • 계정 ID로 선택: account1,account2
       • 모든 계정: all
   
   사용할 계정을 선택하세요: 7
   ```

2. **수량 입력**
   ```
   처리할 수량을 입력하세요 (기본값: 100): 30
   ```

3. **실행 모드 선택**
   ```
   실행 모드:
       1. 동시 실행 (빠름, 리소스 많이 사용)
       2. 순차 실행 (안정적, 리소스 적게 사용)
   실행 모드를 선택하세요 (1 또는 2, 기본값: 1): 1
   ```

4. **브라우저 모드 선택**
   ```
   브라우저 모드:
       1. 일반 모드 (브라우저 창 표시)
       2. 헤드리스 모드 (백그라운드 실행)
   브라우저 모드를 선택하세요 (1 또는 2, 기본값: 1): 1
   ```

## 2. 명령줄 인터페이스 (CLI)

### 기본 구조

```bash
python cli/batch_cli.py [명령어] [옵션들]
```

### 주요 명령어

#### 단일 단계 실행 (single)

```bash
python cli/batch_cli.py single --step [단계번호] --accounts [계정목록] --quantity [수량] [옵션]
```

**필수 옵션:**
- `--step`: 실행할 단계 번호 (1-6)
- `--accounts`: 계정 ID 목록 (공백으로 구분)
- `--quantity`: 처리할 수량 (기본값: 100)

**선택 옵션:**
- `--concurrent`: 동시 실행 (없으면 순차 실행)
- `--output`: 결과 저장 파일 경로

#### 사용 예시

```bash
# 기본 사용법 (요청하신 설정)
python cli/batch_cli.py single --step 1 --accounts account_7 --quantity 30 --concurrent

# 여러 계정 동시 실행
python cli/batch_cli.py single --step 1 --accounts account_1 account_2 account_7 --quantity 30 --concurrent

# 순차 실행 (--concurrent 제거)
python cli/batch_cli.py single --step 1 --accounts account_7 --quantity 30

# 결과를 파일로 저장
python cli/batch_cli.py single --step 1 --accounts account_7 --quantity 30 --concurrent --output result.json
```

#### 다중 단계 실행 (multi)

```bash
python cli/batch_cli.py multi --account [계정ID] --steps [단계목록] --quantities [수량목록] [옵션]
```

**사용 예시:**
```bash
# 하나의 계정으로 여러 단계 실행
python cli/batch_cli.py multi --account account_7 --steps 1 2 3 --quantities 30 20 10 --concurrent
```

#### 기타 명령어

```bash
# 계정 목록 확인
python cli/batch_cli.py accounts

# 사용 가능한 시나리오 목록
python cli/batch_cli.py scenarios

# 현재 설정 확인
python cli/batch_cli.py config

# 도움말
python cli/batch_cli.py --help
python cli/batch_cli.py single --help
```

## 3. 요청하신 설정에 맞는 명령어

### 설정 요약
- 계정: 7번 (account_7)
- 수량: 30개
- 실행 모드: 1 (동시 실행)
- 브라우저 모드: 1 (일반 모드)

### 해당 CLI 명령어

```bash
python cli/batch_cli.py single --step 1 --accounts account_7 --quantity 30 --concurrent
```

## 4. 권장사항

### 언제 어떤 방식을 사용할까?

| 상황 | 추천 방식 | 이유 |
|------|-----------|------|
| 수동 실행, 테스트 | `batch_processor_new.py` | 대화형으로 설정 확인 가능 |
| 자동화, 스크립트 | `cli/batch_cli.py` | 명령줄 인자로 완전 자동화 |
| 배치 파일 작성 | `cli/batch_cli.py` | .bat 파일에 포함하기 쉬움 |
| 반복 작업 | `cli/batch_cli.py` | 동일한 설정으로 빠른 재실행 |

### 주의사항

1. **헤드리스 모드**: CLI에서는 현재 헤드리스 옵션이 명시적으로 보이지 않음
2. **계정 ID**: `account_7` 형식으로 사용 (숫자만이 아님)
3. **동시 실행**: 리소스 사용량이 높으니 시스템 성능 고려
4. **로그 확인**: 실행 후 `logs/` 디렉토리에서 상세 로그 확인 가능

## 5. 트러블슈팅

### 자주 발생하는 문제

1. **계정을 찾을 수 없음**
   ```bash
   # 계정 목록 먼저 확인
   python cli/batch_cli.py accounts
   ```

2. **권한 오류**
   ```bash
   # 관리자 권한으로 실행
   # 또는 Python 가상환경 활성화 확인
   ```

3. **모듈을 찾을 수 없음**
   ```bash
   # 프로젝트 루트 디렉토리에서 실행 확인
   cd c:\Projects\percenty_project
   python cli/batch_cli.py --help
   ```

---

**마지막 업데이트**: 2024년 12월
**작성자**: AI Assistant
**프로젝트**: Percenty 자동화 시스템