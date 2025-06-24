
# 퍼센티 확장 프로그램 CRX 생성 가이드

## 생성 일시
2025년 06월 24일 10시 14분

## 수정 사항
1. manifest.json 업데이트
   - URL 패턴 수정 (*://*/* → https://*/*, http://*/*)
   - Service worker 경로 수정 (./static/js/background.js → static/js/background.js)
   - Web accessible resources 패턴 정규화
   - update_url 제거 (CRX 전용)

2. background.js 재작성
   - Manifest V3 Service Worker 패턴 적용
   - Chrome Runtime API 안전성 체크 추가
   - 오류 처리 강화
   - 메시지 통신 안정성 개선

## CRX 파일 생성 방법

### 방법 1: Chrome 개발자 도구 사용
1. Chrome에서 chrome://extensions/ 접속
2. 개발자 모드 활성화
3. "확장 프로그램 패키징" 클릭
4. 확장 프로그램 루트 디렉터리 선택: C:\Projects\percenty_project\percenty_extension
5. 개인 키 파일 선택 (선택사항)
6. "확장 프로그램 패키징" 버튼 클릭

### 방법 2: 명령줄 도구 사용
```bash
# Chrome 설치 경로에서
chrome --pack-extension="C:\Projects\percenty_project\percenty_extension" --pack-extension-key="private-key.pem"
```

### 방법 3: Node.js 도구 사용
```bash
npm install -g chrome-extension-tools
chrome-extension-tools pack C:\Projects\percenty_project\percenty_extension
```

## 설치 테스트
1. 생성된 .crx 파일을 Chrome으로 드래그 앤 드롭
2. 또는 chrome://extensions/에서 "압축해제된 확장 프로그램 로드" 사용
3. 퍼센티 웹사이트에서 확장 프로그램 인식 확인

## 문제 해결
- 설치 오류 시: Chrome 개발자 콘솔에서 오류 메시지 확인
- 인식 안됨: 퍼센티 웹사이트에서 F12 → Console 탭에서 오류 확인
- 권한 문제: manifest.json의 host_permissions 확인

## 백업 위치
C:\Projects\percenty_project\percenty_extension\backup\backup_20250624_101434
