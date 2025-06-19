# auto_detect_chinese 기능 테스트 방법

## 현재 상황

`debug_step3_only.py`를 실행하면 다음과 같은 로그가 나타납니다:

```
2025-06-06 19:21:22,880 - image_translation_handler_new - INFO - 이미지 번역 시작: specific:all
2025-06-06 19:21:22,881 - image_translation_handler_new - INFO - specific:all 형식 - 새로운 순차 처리 모드
```

이는 **기존 방식**으로 모든 이미지를 순차적으로 처리하고 있음을 의미합니다.

## 새로운 기능 테스트 방법

### 방법 1: 새로운 테스트 스크립트 사용 (권장)

```bash
python test_new_auto_detect.py
```

이 스크립트는 다음과 같은 테스트를 수행합니다:
- `auto_detect_chinese`: 중국어가 있는 이미지만 자동 감지하여 번역
- `auto_detect_chinese,1,2`: 중국어 자동 감지 + 1,2번 이미지 추가 번역

### 방법 2: 엑셀 파일 수정

`percenty_id.xlsx` 파일에서 K열 값을 다음과 같이 변경:

**기존:**
```
K열: specific:all
```

**신규:**
```
K열: auto_detect_chinese
```

또는 조합 사용:
```
K열: auto_detect_chinese,1,2
K열: 1,2,auto_detect_chinese
K열: auto_detect_chinese,specific:10
```

### 방법 3: 코드 직접 수정

`product_editor_core3.py`에서 임시로 테스트하려면:

```python
# 1524번째 줄 근처에서
# 기존:
success = self.image_translate(k_data)

# 임시 변경:
success = self.image_translate('auto_detect_chinese')  # 테스트용
```

## 기대되는 로그 변화

### 기존 방식 (specific:all)
```
INFO - 이미지 번역 시작: specific:all
INFO - specific:all 형식 - 새로운 순차 처리 모드
INFO - 총 16개의 이미지 순차 처리 시작
INFO - 이미지 1/16 처리 중...
INFO - 이미지 2/16 처리 중...
```

### 새로운 방식 (auto_detect_chinese)
```
INFO - 이미지 번역 시작: auto_detect_chinese
INFO - auto_detect_chinese 모드 - 중국어 이미지 자동 감지
INFO - 일괄편집 모달에서 이미지 스캔 시작
INFO - 16개 이미지 중 중국어 감지된 이미지: [4, 8, 12]
INFO - 중국어가 있는 3개 이미지만 처리
```

## 장점 비교

| 구분 | 기존 방식 (specific:all) | 새로운 방식 (auto_detect_chinese) |
|------|-------------------------|----------------------------------|
| 처리 방식 | 모든 이미지 순차 처리 | 중국어 이미지만 선별 처리 |
| 로봇 의심도 | 높음 (모든 이미지 클릭) | 낮음 (필요한 이미지만 클릭) |
| 처리 속도 | 느림 (불필요한 처리 포함) | 빠름 (필요한 것만 처리) |
| 정확도 | 낮음 (중국어 없는 이미지도 처리) | 높음 (중국어 있는 이미지만 처리) |

## 테스트 확인 포인트

1. **로그 메시지 확인**
   - `auto_detect_chinese 모드` 메시지가 나타나는지
   - 감지된 이미지 위치가 올바른지 (예: `[4, 8, 12]`)

2. **처리 시간 비교**
   - 기존 방식보다 빠른 처리 시간
   - 불필요한 이미지 스킵 확인

3. **번역 정확도**
   - 중국어가 있는 이미지만 번역되는지
   - 중국어가 없는 이미지는 스킵되는지

## 문제 해결

### 만약 여전히 기존 방식으로 동작한다면:

1. **캐시 문제**: Python 캐시 삭제
   ```bash
   python -c "import py_compile; py_compile.compile('image_translation_handler_new.py', doraise=True)"
   ```

2. **import 문제**: 올바른 핸들러 사용 확인
   ```python
   # product_editor_core3.py에서
   from image_translation_handler_new import ImageTranslationHandler  # 새 버전
   ```

3. **엑셀 파일 확인**: K열 데이터가 올바르게 설정되었는지 확인

## 추천 테스트 순서

1. **먼저 새로운 테스트 스크립트 실행**
   ```bash
   python test_new_auto_detect.py
   ```

2. **로그 확인하여 새로운 기능 동작 확인**

3. **정상 동작 확인 후 기존 워크플로우에 적용**
   - 엑셀 파일 수정 또는
   - debug_step3_only.py에서 임시 테스트

이렇게 하면 로봇으로 의심받지 않고 효율적으로 중국어 이미지만 번역할 수 있습니다.