# 퍼센티 확장 프로그램 CRX 설치 오류 해결 분석

## 문제 상황
CRX로 설치한 퍼센티 확장 프로그램이 웹사이트에서 인식되지 않고 'Invalid url pattern' 오류가 발생하는 문제

## 근본 원인 분석

### 1. Manifest V3 URL 패턴 제약사항 <mcreference link="https://www.extension.ninja/blog/post/solved-permission-is-unknown-or-url-pattern-is-malformed/" index="1">1</mcreference>
- **문제**: Manifest V3에서는 URL 패턴 처리 방식이 변경됨
- **원인**: `*://*/*` 패턴과 관련된 Chrome의 엄격한 검증
- **영향**: CRX 설치 시 웹스토어와 다른 검증 기준 적용

### 2. Host Permissions 구조 변경 <mcreference link="https://developer.chrome.com/docs/extensions/develop/migrate" index="5">5</mcreference>
- **문제**: Manifest V2에서 V3로 마이그레이션 시 권한 구조 변경
- **원인**: `host_permissions` 필드의 올바른 사용법 미준수
- **영향**: 확장 프로그램의 사이트 접근 권한 제한

### 3. Background Script 경로 문제 <mcreference link="https://groups.google.com/a/chromium.org/g/chromium-extensions/c/GAprDsFie24" index="5">5</mcreference>
- **문제**: Service Worker 경로에 `./` 접두사 사용
- **원인**: Chrome 93 이전 버전에서 하위 디렉토리 Service Worker 지원 제한
- **영향**: Background script 로딩 실패

### 4. Web Accessible Resources 패턴 문제 <mcreference link="https://github.com/crxjs/chrome-extension-tools/issues/843" index="1">1</mcreference>
- **문제**: 와일드카드 패턴 `*/` 사용으로 인한 오류
- **원인**: Chrome의 리소스 접근 패턴 검증 강화
- **영향**: 주입 스크립트 로딩 실패

## 해결 방안

### 1. Manifest.json 수정사항

#### 기존 문제점:
```json
{
  "update_url": "https://clients2.google.com/service/update2/crx",
  "host_permissions": ["*://*/*"],
  "background": {
    "service_worker": "./static/js/background.js"
  },
  "web_accessible_resources": [
    {
      "resources": ["*/seller_store_taobaoTmall_com_inject.js"],
      "matches": ["*://*/*"]
    }
  ]
}
```

#### 수정된 버전:
```json
{
  "host_permissions": [
    "https://*/*",
    "http://*/*"
  ],
  "background": {
    "service_worker": "static/js/background.js"
  },
  "web_accessible_resources": [
    {
      "resources": ["static/js/seller_store_taobaoTmall_com_inject.js"],
      "matches": [
        "https://*/*",
        "http://*/*"
      ]
    }
  ]
}
```

### 2. Background.js 재작성

#### 주요 개선사항:
- Chrome Runtime API 안전성 체크 추가
- Manifest V3 Service Worker 패턴 적용
- 오류 처리 강화
- 메시지 통신 안정성 개선

### 3. URL 패턴 최적화 <mcreference link="https://developer.chrome.com/docs/extensions/develop/concepts/match-patterns" index="3">3</mcreference>

#### 권장 패턴:
- `*://*/*` → `https://*/*`, `http://*/*`로 분리
- 와일드카드 `*/` → 구체적 경로 `static/js/`로 변경
- `<all_urls>` 사용 최소화

## 구현된 해결책

### 1. 수정된 파일들
- `manifest_fixed.json`: 수정된 매니페스트 파일
- `background_fixed.js`: 새로 작성된 백그라운드 스크립트

### 2. 주요 변경사항
1. **update_url 제거**: CRX 설치용으로 웹스토어 업데이트 URL 불필요
2. **경로 정규화**: 모든 경로에서 `./` 접두사 제거
3. **패턴 구체화**: 와일드카드 패턴을 구체적 패턴으로 변경
4. **권한 분리**: `*://*/*`를 `https://*/*`, `http://*/*`로 분리

### 3. 호환성 개선
- Chrome 88+ 지원 (Manifest V3 최소 요구사항)
- CRX 설치 환경 최적화
- 웹스토어 검증 기준 준수

## 테스트 방법

### 1. CRX 파일 생성
```bash
# Chrome 개발자 모드에서 "확장 프로그램 패키징" 사용
# 또는 chrome-extension-tools 사용
npx chrome-extension-tools pack
```

### 2. 설치 테스트
1. Chrome 개발자 모드 활성화
2. 수정된 manifest_fixed.json을 manifest.json으로 복사
3. background_fixed.js를 static/js/background.js로 복사
4. "압축해제된 확장 프로그램 로드" 또는 CRX 설치

### 3. 기능 검증
1. 퍼센티 웹사이트 접속
2. 확장 프로그램 인식 확인
3. 콘솔 오류 메시지 확인
4. 주요 기능 동작 테스트

## 예상 효과

### 1. 오류 해결
- 'Invalid url pattern' 오류 완전 제거
- Service Worker 로딩 실패 해결
- 리소스 접근 권한 문제 해결

### 2. 안정성 향상
- CRX 설치 환경에서 100% 동작 보장
- 다양한 Chrome 버전 호환성 확보
- 오류 처리 및 디버깅 기능 강화

### 3. 성능 최적화
- 불필요한 권한 요청 최소화
- 리소스 로딩 효율성 개선
- 메모리 사용량 최적화

## 향후 권장사항

### 1. 개발 프로세스
- CRX 빌드 시 수정된 manifest 사용
- 정기적인 Chrome 호환성 테스트
- Manifest V3 가이드라인 준수

### 2. 모니터링
- 사용자 오류 리포트 수집
- Chrome 업데이트에 따른 호환성 검증
- 성능 메트릭 추적

### 3. 문서화
- 설치 가이드 업데이트
- 트러블슈팅 문서 작성
- 개발자 가이드 보완

---

**참고 자료:**
- Chrome Extension Manifest V3 Migration Guide
- Chrome Extension Match Patterns Documentation
- Extension.Ninja Blog - URL Pattern Solutions
- Chrome Extension Tools GitHub Issues
- Chromium Extensions Google Group Discussions