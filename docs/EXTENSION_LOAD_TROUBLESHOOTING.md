# 퍼센티 확장 프로그램 자동 로드 문제 해결 가이드

## 현재 상황 분석

### 문제 요약
- `browser_core.py`에 확장 프로그램 자동 로드 기능이 구현되었음
- Chrome 옵션에 `--load-extension` 플래그가 정상적으로 설정됨
- 하지만 `chrome://extensions/` 페이지에서 확장 프로그램이 표시되지 않음
- 확장 프로그램 파일 구조와 manifest.json은 정상임

### 진단 결과
```
✅ 확장 프로그램 디렉토리 존재: C:\Projects\percenty_project\percenty_extension
✅ manifest.json 파일 유효성: 정상
✅ 확장 프로그램 key 필드: 존재 (392자)
✅ Chrome 버전: 137.0.7151.120 (최신)
❌ Chrome 확장 프로그램 페이지에서 인식: 실패
❌ 확장 프로그램 키워드 검색: 실패
```

## 가능한 원인들

### 1. Chrome 보안 정책
- Chrome 최신 버전에서 보안 정책이 강화되어 `--load-extension` 플래그가 제한될 수 있음
- Manifest V3 확장 프로그램의 로드 방식 변경
- 서명되지 않은 확장 프로그램에 대한 제한

### 2. 경로 문제
- Windows 경로 구분자 문제
- 상대 경로 vs 절대 경로 문제
- 공백이나 특수 문자가 포함된 경로

### 3. Chrome 사용자 데이터 디렉토리
- 기존 Chrome 프로필과의 충돌
- 사용자 데이터 디렉토리 권한 문제

### 4. Selenium WebDriver 제한
- Selenium으로 실행된 Chrome에서의 확장 프로그램 로드 제한
- WebDriver 모드에서의 보안 제한

## 해결 방안들

### 방안 1: 개선된 Chrome 옵션 (현재 구현됨)
```python
# browser_core.py에 구현된 방식
chrome_options.add_argument("--enable-extensions")
chrome_options.add_argument("--disable-web-security")
chrome_options.add_argument("--disable-features=VizDisplayCompositor")
chrome_options.add_argument("--allow-running-insecure-content")
chrome_options.add_argument("--disable-extensions-file-access-check")
chrome_options.add_argument("--enable-extension-activity-logging")
chrome_options.add_argument(f"--load-extension={abs_extension_path}")
chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
```

### 방안 2: CRX 파일 설치 (대안)
- `extension_crx_installer.py` 스크립트 사용
- 수동으로 CRX 파일을 드래그 앤 드롭하여 설치
- 한 번 설치하면 Chrome 프로필에 영구적으로 저장됨

### 방안 3: Chrome 웹 스토어 설치 (권장)
- 가장 안정적인 방법
- Chrome 웹 스토어에서 퍼센티 확장 프로그램 검색 후 설치
- 자동 업데이트 지원

### 방안 4: 기존 Chrome 프로필 사용
```python
# 기존 Chrome 프로필 경로 사용
user_profile_path = os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\User Data")
chrome_options.add_argument(f"--user-data-dir={user_profile_path}")
```

## 즉시 사용 가능한 해결책

### 1단계: 수동 확장 프로그램 설치
1. Chrome 브라우저를 수동으로 열기
2. `chrome://extensions/` 페이지로 이동
3. 개발자 모드 활성화
4. "압축해제된 확장 프로그램을 로드합니다" 클릭
5. `C:\Projects\percenty_project\percenty_extension` 폴더 선택
6. 확장 프로그램 ID `omeekokppgdnpcla` 확인

### 2단계: 기존 Chrome 프로필 사용하도록 수정
```python
# browser_core.py 수정 예시
def setup_driver_with_existing_profile(self, headless=False):
    chrome_options = Options()
    
    # 기존 Chrome 프로필 사용 (확장 프로그램이 이미 설치된 상태)
    user_data_dir = os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\User Data")
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
    chrome_options.add_argument("--profile-directory=Default")
    
    # 나머지 옵션들...
    self.driver = webdriver.Chrome(options=chrome_options)
```

## 테스트 및 검증

### 현재 사용 가능한 테스트 스크립트들
1. `test_extension_autoload.py` - 기본 자동 로드 테스트
2. `test_extension_debug.py` - 상세 디버깅 정보 제공
3. `extension_crx_installer.py` - CRX 파일 설치 도구

### 검증 방법
1. **브라우저 툴바 확인**: 퍼센티 아이콘이 표시되는지 확인
2. **chrome://extensions/ 페이지**: 확장 프로그램 목록에서 퍼센티 확인
3. **확장 프로그램 ID**: `omeekokppgdnpcla`인지 확인
4. **활성화 상태**: "사용 설정됨" 상태인지 확인

## 권장 워크플로우

### 단기 해결책 (즉시 사용)
1. Chrome 웹 스토어에서 퍼센티 확장 프로그램 수동 설치
2. `browser_core.py`에서 기존 Chrome 프로필 사용하도록 수정
3. 자동화 스크립트 실행 및 테스트

### 장기 해결책 (개발 완료 후)
1. Chrome 최신 보안 정책에 맞는 확장 프로그램 로드 방식 연구
2. Selenium WebDriver의 확장 프로그램 지원 개선 사항 모니터링
3. 대안적인 브라우저 자동화 도구 검토 (예: Playwright)

## 파일 구조
```
C:\Projects\percenty_project\
├── browser_core.py                    # 수정된 브라우저 코어 (확장 프로그램 로드 기능 포함)
├── percenty_extension\                 # 퍼센티 확장 프로그램 소스
│   ├── manifest.json                  # 확장 프로그램 매니페스트
│   └── ...
├── test_extension_autoload.py         # 기본 자동 로드 테스트
├── test_extension_debug.py            # 상세 디버깅 테스트
├── extension_crx_installer.py         # CRX 설치 도구
├── jlcdjppbpplpdgfeknhioedbhfceaben.crx # CRX 파일 (있는 경우)
└── chrome_user_data\                   # Chrome 사용자 데이터 디렉토리
```

## 결론

현재 구현된 자동 로드 기능은 기술적으로 올바르게 구현되었으나, Chrome의 최신 보안 정책으로 인해 작동하지 않을 수 있습니다. 

**즉시 사용을 위해서는 수동 설치 + 기존 프로필 사용 방식을 권장합니다.**

향후 Chrome의 확장 프로그램 정책 변화를 모니터링하고, 필요시 대안적인 접근 방식을 검토해야 합니다.