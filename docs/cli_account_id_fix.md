# CLI 계정 ID 파싱 문제 해결

## 문제 상황

사용자가 배치 작업을 실행할 때 다음과 같은 오류가 발생했습니다:

```
계정 ID '1'를 찾을 수 없습니다.
```

## 원인 분석

1. **계정 ID 형식 불일치**:
   - CLI에서 입력: `--accounts 1` (숫자 형식)
   - 실제 계정 ID: `account_1` (account_ 접두사 포함)

2. **계정 매니저의 ID 생성 로직**:
   ```python
   account_id = f"account_{index + 1}"  # account_1, account_2, ...
   ```

3. **CLI 파라미터 처리**:
   - 사용자가 `--accounts 1 2 3`으로 입력
   - 시스템은 `['1', '2', '3']`으로 처리
   - 실제 필요한 형식: `['account_1', 'account_2', 'account_3']`

## 해결 방법

### 1. CLI 계정 ID 변환 로직 추가

`cli/batch_cli.py`에서 계정 ID를 자동으로 변환하도록 수정:

```python
# 단일 단계 실행
def run_single_step(self, args):
    # 계정 ID를 올바른 형식으로 변환 (숫자 -> account_숫자)
    converted_accounts = []
    for account in args.accounts:
        if account.isdigit():
            converted_accounts.append(f"account_{account}")
        else:
            converted_accounts.append(account)

# 다중 단계 실행
def run_multi_step(self, args):
    # 계정 ID를 올바른 형식으로 변환 (숫자 -> account_숫자)
    converted_account = args.account
    if args.account.isdigit():
        converted_account = f"account_{args.account}"
```

### 2. 변환 로직의 특징

- **숫자 입력**: `1` → `account_1`로 자동 변환
- **문자 입력**: `account_1` → 그대로 유지
- **혼합 지원**: 숫자와 문자 형식 모두 지원

## 테스트 방법

### 1. 단일 계정 테스트
```bash
python cli/batch_cli.py single --step 1 --accounts 1 --quantity 5 --concurrent
```

### 2. 다중 계정 테스트
```bash
python cli/batch_cli.py single --step 1 --accounts 1 2 3 --quantity 5 --concurrent
```

### 3. 혼합 형식 테스트
```bash
python cli/batch_cli.py single --step 1 --accounts 1 account_2 3 --quantity 5 --concurrent
```

## 예상 결과

수정 후 CLI 출력에서 다음과 같이 표시됩니다:

```
=== 1단계 배치 실행 ===
입력 계정: ['1']
변환된 계정: ['account_1']
수량: 5
동시 실행: True
```

## 추가 개선 사항

### 1. 계정 존재 여부 사전 검증

향후 CLI에서 계정 ID 변환 후 실제 존재하는지 사전 검증하는 로직 추가 가능:

```python
# 계정 존재 여부 확인
for account_id in converted_accounts:
    if not self.account_manager.account_exists(account_id):
        print(f"경고: 계정 '{account_id}'를 찾을 수 없습니다.")
        return
```

### 2. 사용자 친화적 오류 메시지

계정을 찾을 수 없을 때 사용 가능한 계정 목록을 표시:

```python
available_accounts = self.account_manager.get_active_accounts()
print(f"사용 가능한 계정: {available_accounts}")
```

## 결론

이 수정으로 사용자는 간편하게 숫자 형식(`1`, `2`, `3`)으로 계정을 지정할 수 있으며, 시스템은 자동으로 올바른 형식(`account_1`, `account_2`, `account_3`)으로 변환하여 처리합니다.