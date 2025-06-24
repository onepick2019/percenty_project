# 퍼센티 확장 프로그램 동일 ID 생성 대안 방법

## 문제 상황
웹스토어에서 다운로드한 CRX 파일에는 key 필드가 없어서 동일한 ID를 생성할 수 없습니다.

## 대안 해결책

### 방법 1: Chrome Extension Source Viewer 사용
1. Chrome 웹스토어에서 "Chrome Extension Source Viewer" 설치
2. 퍼센티 확장 프로그램 페이지에서 Source Viewer 실행
3. 콘솔에서 key 값 확인

### 방법 2: 개발자 도구 사용
1. Chrome에서 퍼센티 확장 프로그램 설치
2. chrome://extensions/ 에서 개발자 모드 활성화
3. "확장 프로그램 패키징" 클릭
4. 설치된 확장 프로그램 디렉토리 선택
5. 생성된 .pem 파일로 key 값 생성

### 방법 3: 수동 key 생성
1. OpenSSL 사용하여 RSA 키 쌍 생성
2. 공개키를 Base64로 인코딩
3. manifest.json에 key 필드 추가

### 방법 4: 웹스토어 ID 무시하고 새 ID 사용
1. 새로운 key 값으로 고유한 ID 생성
2. 퍼센티 웹사이트에서 새 ID 인식하도록 요청
3. 또는 확장 프로그램 코드 수정으로 인식 개선

## 권장 방법
가장 확실한 방법은 **방법 2 (개발자 도구 사용)**입니다:

```bash
# 1. 퍼센티 확장 프로그램을 웹스토어에서 설치
# 2. 다음 스크립트 실행
python extract_percenty_key.py

# 3. 만약 key가 없다면 개발자 도구로 패키징
# chrome://extensions/ -> 개발자 모드 -> 확장 프로그램 패키징
```

## 다음 단계
1. 위 방법 중 하나를 선택하여 key 값 획득
2. manifest.json에 key 값 추가
3. CRX 파일 재생성
4. 테스트 및 검증

## 주의사항
- key 값은 확장 프로그램의 고유 식별자입니다
- 잘못된 key 사용 시 다른 확장 프로그램과 충돌할 수 있습니다
- 웹스토어 업로드 시에는 key 필드를 제거해야 합니다
