# 계정 ID 매핑 구현 완료

## 개요
5단계에서 발생하던 접미사 추가 실패 문제를 해결하기 위해 하이브리드 접근법을 구현했습니다.

## 문제점
- `batch_manager.py`에서 가상 계정 ID (`account_1`, `account_2` 등) 사용
- `percenty_id.xlsx`에는 실제 이메일 주소 저장
- `_get_suffix_from_excel` 메서드에서 ID 불일치로 접미사 검색 실패

## 해결책

### 1. 계정 ID 매핑 테이블 추가
`batch/batch_manager.py`에 하드코딩된 매핑 테이블 추가:

```python
# 계정 ID 매핑 테이블 (가상 ID -> 실제 이메일)
ACCOUNT_ID_MAPPING = {
    'account_1': 'percenty1@naver.com',
    'account_2': 'percenty2@naver.com', 
    'account_3': 'percenty3@naver.com',
    'account_4': 'percenty4@naver.com',
    'account_5': 'percenty5@naver.com',
    'account_6': 'percenty6@naver.com',
    'account_7': 'percenty7@naver.com'
}

def get_real_account_id(virtual_id: str) -> str:
    """가상 계정 ID를 실제 이메일로 변환"""
    return ACCOUNT_ID_MAPPING.get(virtual_id, virtual_id)
```

### 2. 계정 정보 조회 수정
모든 `get_account()` 및 `get_account_credentials()` 호출에서 실제 이메일 사용:

```python
# 기존
account_info = self.account_manager.get_account(account_id)

# 수정 후
real_account_id = get_real_account_id(account_id)
account_info = self.account_manager.get_account(real_account_id)
```

## 수정된 파일
- `batch/batch_manager.py`: 매핑 테이블 및 모든 계정 조회 로직 수정

## 장점
1. **즉시 문제 해결**: 5단계 접미사 추가 문제 해결
2. **안정성**: 하드코딩으로 예측 가능한 동작
3. **유지보수성**: 계정 수가 적어 관리 용이
4. **확장성**: 2, 3단계에도 동일한 방식 적용 가능

## 향후 계획
1. 5단계 테스트 완료 후 2, 3단계에도 적용
2. 공통 유틸리티 모듈(`account_utils.py`) 생성 고려
3. 계정 추가/삭제 시 매핑 테이블 업데이트

## 테스트 방법
```bash
python test_account_mapping.py
```

## 주의사항
- 새 계정 추가 시 `ACCOUNT_ID_MAPPING`에 수동으로 추가 필요
- 기존 디버깅 코어는 문제없이 작동하므로 당장 수정 불필요