# 퍼센티 확장 프로그램 자동 설치 분석 보고서

## 문제 상황 요약

현재 자동화 솔루션에서 퍼센티 확장 프로그램의 올바른 ID와 출처를 확인하기 위해 여러 방법을 시도했으나 모두 실패했습니다.

### 핵심 문제
- **압축 해제된 확장 프로그램**: 임시 ID (`iopmiegemkgodkipipmgpdlnkplcalja`), 출처: 로컬 디렉토리
- **웹스토어 설치 버전**: 고정 ID (`jlcdjppbpplpdgfeknhioedbhfceaben`), 출처: Chrome Web Store
- **자동화 요구사항**: 브라우저 간섭 없이 동시 진행, 사용자 개입 불가

## 시도한 방법들과 실패 원인

### 1. 웹스토어 직접 설치 (`install_webstore_extension.py`)
**결과**: 실패  
**원인**: Chrome의 보안 정책으로 인해 Selenium을 통한 웹스토어 확장 프로그램 자동 설치 차단

### 2. CRX 파일 직접 설치 (`install_crx_extension.py`)
**결과**: 실패  
**원인**: CRX 파일이 비어있음 (0 bytes)

### 3. CRX 파일 다운로드 및 설치 (`download_and_install_crx.py`)
**결과**: 부분 성공 (다운로드 및 압축 해제), 최종 실패 (확장 프로그램 감지 안됨)  
**원인**: 압축 해제된 확장 프로그램이 Chrome에서 인식되지 않음

### 4. 엔터프라이즈 정책 설치 (`enterprise_policy_installer.py`)
**결과**: 실패  
**원인**: 관리자 권한 부족으로 레지스트리 정책 설정 불가

### 5. Preferences 파일 수정 (`preferences_policy_installer.py`)
**결과**: 실패  
**원인**: Chrome이 수동으로 수정된 Preferences 파일을 무시하거나 재설정

## Chrome 보안 정책 분석

### Chrome의 확장 프로그램 설치 제한사항
1. **웹스토어 외부 설치 제한**: Chrome 88+ 버전부터 웹스토어 외부 확장 프로그램 설치 엄격히 제한
2. **자동화 도구 감지**: Selenium 등 자동화 도구를 통한 확장 프로그램 설치 차단
3. **사용자 상호작용 필수**: 확장 프로그램 설치 시 사용자의 명시적 승인 필요
4. **엔터프라이즈 정책 제한**: 관리자 권한 및 도메인 가입 환경에서만 작동

## 현실적인 해결 방안

### 방안 1: 기존 설치된 확장 프로그램 활용 (권장)
```python
# 기존 Chrome 프로필에서 확장 프로그램 ID 추출
def get_installed_extension_id():
    # 사용자의 기본 Chrome 프로필에서 퍼센티 확장 프로그램 ID 확인
    # 한 번만 수동으로 확인하여 하드코딩
    return "jlcdjppbpplpdgfeknhioedbhfceaben"
```

**장점**:
- 즉시 구현 가능
- 안정적이고 신뢰할 수 있음
- 추가 설치 과정 불필요

**단점**:
- 초기 수동 확인 필요
- 확장 프로그램 업데이트 시 ID 변경 가능성 (매우 낮음)

### 방안 2: 조건부 ID 사용
```python
def get_percenty_extension_id(browser_type="isolated"):
    if browser_type == "isolated":
        # 격리된 환경에서는 압축 해제 버전 사용
        return "iopmiegemkgodkipipmgpdlnkplcalja"
    else:
        # 일반 환경에서는 웹스토어 버전 사용
        return "jlcdjppbpplpdgfeknhioedbhfceaben"
```

### 방안 3: 확장 프로그램 기능 직접 구현
퍼센티 확장 프로그램의 핵심 기능을 JavaScript 인젝션으로 직접 구현

```python
# 퍼센티 기능을 대체하는 JavaScript 코드 인젝션
def inject_percenty_functionality(driver):
    percenty_script = """
    // 퍼센티 확장 프로그램 핵심 기능 구현
    // DOM 조작, 데이터 추출 등
    """
    driver.execute_script(percenty_script)
```

### 방안 4: 하이브리드 접근법
```python
def setup_percenty_environment(driver):
    # 1. 확장 프로그램 감지 시도
    extension_id = detect_percenty_extension(driver)
    
    if extension_id:
        # 2. 확장 프로그램이 있으면 사용
        return use_extension(driver, extension_id)
    else:
        # 3. 없으면 JavaScript 기능 인젝션
        return inject_percenty_functionality(driver)
```

## 권장 구현 방안

### 단계 1: 즉시 구현 (방안 1)
1. 개발자가 한 번 수동으로 Chrome에서 퍼센티 확장 프로그램 설치
2. `chrome://extensions/`에서 확장 프로그램 ID 확인
3. 해당 ID를 코드에 하드코딩

### 단계 2: 장기적 해결책 (방안 4)
1. 확장 프로그램 자동 감지 로직 구현
2. 감지 실패 시 JavaScript 기능 인젝션으로 대체
3. 두 방식 모두 지원하는 통합 인터페이스 구현

## 결론

Chrome의 강화된 보안 정책으로 인해 **프로그래밍 방식의 웹스토어 확장 프로그램 자동 설치는 현재 기술적으로 불가능**합니다.

가장 현실적인 해결책은 **기존 설치된 확장 프로그램의 ID를 활용**하거나, **확장 프로그램 기능을 JavaScript로 직접 구현**하는 것입니다.

자동화 솔루션의 안정성과 신뢰성을 위해서는 **방안 1 (하드코딩된 ID 사용)**을 즉시 적용하고, 장기적으로는 **방안 4 (하이브리드 접근법)**을 구현하는 것을 권장합니다.