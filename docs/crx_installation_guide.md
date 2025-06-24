# 퍼센티 확장 프로그램 설치 가이드

## 문제 상황
사용자가 CRX 확장 프로그램 설치 시도 중 다음과 같은 오류가 발생했습니다:
- "이 웹사이트에서 앱, 확장프로그램, 사용자 스크립트 등을 추가할 수 없습니다"
- "확장 프로그램 추가 버튼을 찾을 수 없음" 오류
- "개발자 모드 토글을 찾을 수 없음" 오류

## 해결 방안

### 1. 개선된 개발자 모드 활성화 로직

`product_editor_core6_1_dynamic.py`의 `_enable_developer_mode()` 메서드가 다음과 같이 개선되었습니다:

- **언어 감지**: Chrome 페이지가 한국어인지 영어인지 자동 감지
- **다양한 선택자**: 텍스트 기반, CSS, XPath 등 다양한 방법으로 개발자 모드 토글 찾기
- **전체 요소 검사**: 모든 cr-toggle 요소를 검사하여 개발자 모드 토글 식별
- **JavaScript 클릭**: 일반 클릭이 실패할 경우 JavaScript를 통한 클릭 시도

### 2. 새로운 설치 방식

CRX 파일 직접 설치 대신 압축 해제된 확장 프로그램 로드 방식으로 변경:

1. **CRX 파일 압축 해제**: `extract_crx.py` 스크립트로 CRX를 폴더로 변환
2. **개발자 모드 활성화**: Chrome 확장 프로그램 페이지에서 개발자 모드 활성화
3. **수동 로드**: "압축해제된 확장 프로그램을 로드합니다" 버튼으로 폴더 선택

## 테스트 방법

### 방법 1: 개별 메서드 테스트
```bash
python test_crx_install.py
```

이 스크립트는 다음을 수행합니다:
1. Chrome 브라우저 열기
2. 퍼센티 사이트 로그인 (수동)
3. Chrome 확장 프로그램 페이지로 이동
4. 페이지 언어 감지 (한국어/영어)
5. 개발자 모드 자동 활성화 시도
6. 로드 버튼 자동 감지
7. 수동 확장 프로그램 설치 안내
8. 설치 확인

### 방법 2: 전체 워크플로우 테스트
```python
# ProductEditorCore6_1Dynamic 인스턴스에서
core._install_percenty_extension_via_crx()
```

## 수동 설치 단계

개발자 모드 활성화 후 다음 단계를 수행하세요:

1. **"압축해제된 확장 프로그램을 로드합니다"** 또는 **"Load unpacked"** 버튼 클릭
2. 파일 탐색기에서 다음 폴더 선택:
   ```
   c:\Projects\percenty_project\percenty_extension
   ```
3. **"폴더 선택"** 버튼 클릭
4. 확장 프로그램이 목록에 나타나는지 확인

## 디버깅 도구

### 1. 개발자 모드 디버깅
```bash
python debug_developer_mode.py
```

### 2. 간단한 테스트
```bash
python test_simple_developer_mode.py
```

## 주요 개선 사항

### 1. 언어별 선택자 지원
```python
# 한국어 페이지
text_selectors = [
    "//span[text()='개발자 모드']/following-sibling::cr-toggle",
    "//span[contains(text(), '개발자 모드')]/parent::*/cr-toggle"
]

# 영어 페이지
text_selectors = [
    "//span[text()='Developer mode']/following-sibling::cr-toggle",
    "//span[contains(text(), 'Developer mode')]/parent::*/cr-toggle"
]
```

### 2. 강화된 토글 처리
```python
def _toggle_developer_mode(self, element, selector_info):
    # 요소 상태 확인
    is_pressed = element.get_attribute("aria-pressed")
    
    if is_pressed == "false":
        # JavaScript 클릭 시도
        self.driver.execute_script("arguments[0].click();", element)
        
        # 상태 변경 확인
        new_state = element.get_attribute("aria-pressed")
        return new_state == "true"
```

### 3. 전체 요소 검사
```python
# 모든 cr-toggle 요소 검사
toggles = self.driver.find_elements(By.TAG_NAME, "cr-toggle")
for toggle in toggles:
    toggle_id = toggle.get_attribute('id')
    if toggle_id == 'devMode':
        # 개발자 모드 토글 발견
```

## 예상 결과

성공적인 실행 시 다음과 같은 로그가 출력됩니다:

```
2025-06-23 23:13:23 - INFO - 개발자 모드 활성화 시작
2025-06-23 23:13:23 - INFO - 페이지 언어 감지 - 한국어: True, 영어: False
2025-06-23 23:13:24 - INFO - CSS: cr-toggle#devMode: 현재 상태 (aria-pressed) = false
2025-06-23 23:13:25 - INFO - CSS: cr-toggle#devMode: JavaScript 클릭으로 활성화 성공
2025-06-23 23:13:27 - INFO - 퍼센티 확장프로그램 설치 확인 시작
2025-06-23 23:13:30 - INFO - 퍼센티 확장프로그램 설치 확인 성공
```

## 문제 해결

### 개발자 모드 토글을 찾을 수 없는 경우
1. Chrome 버전 확인 (최신 버전 권장)
2. Chrome 언어 설정 확인
3. 관리자 권한으로 Chrome 실행
4. Chrome 정책 설정 확인

### 확장 프로그램 로드 실패
1. `percenty_extension` 폴더에 `manifest.json` 파일 존재 확인
2. 폴더 권한 확인
3. Chrome 보안 설정 확인

이 가이드를 통해 퍼센티 확장 프로그램 설치 문제를 해결할 수 있습니다.