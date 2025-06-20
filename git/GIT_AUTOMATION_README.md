# Git 자동화 스크립트 사용 가이드

## 개요
Percenty 프로젝트의 Git 작업을 자동화하기 위한 스크립트들입니다. 프로젝트의 모든 변경사항을 한 번에 커밋하고 푸시할 수 있습니다.

## 제공되는 스크립트

### 1. Windows 배치 파일 (git_commit_all.bat)
- **사용법**: 프로젝트 루트 디렉토리에서 `git\git_commit_all.bat` 실행
- **특징**: 간단한 배치 스크립트로 빠른 실행 가능

### 2. PowerShell 스크립트 (git_commit_all.ps1)
- **사용법**: PowerShell에서 `git\git_commit_all.ps1` 실행
- **특징**: 컬러 출력과 더 나은 오류 처리
- **실행 정책**: 필요시 `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` 실행

### 3. Linux/Mac 셸 스크립트 (git_commit_all.sh)
- **사용법**: 터미널에서 `chmod +x git/git_commit_all.sh && git/git_commit_all.sh` 실행
- **특징**: 크로스 플랫폼 지원

## 스크립트 실행 과정

1. **Git 상태 확인**: 현재 변경사항 표시
2. **커밋 메시지 입력**: 사용자로부터 커밋 메시지 받기
3. **스테이징**: 모든 변경사항을 `git add .`로 추가
4. **커밋**: 입력받은 메시지로 커밋 실행
5. **푸시**: 원격 저장소(origin/main)로 푸시
6. **최종 확인**: Git 상태 재확인

## 사용 예시

### Windows에서 배치파일 실행
```cmd
C:\Projects\percenty_project> ./git\git_commit_all.bat
========================================
Percenty Project Git Commit Script
========================================

[1/5] Checking Git status...
...
Enter commit message (e.g., feat: add new feature): feat: 새로운 자동화 기능 추가
[2/5] Adding all changes to staging area...
Done!
...
```

### PowerShell에서 실행
```powershell
PS C:\Projects\percenty_project> git\git_commit_all.ps1
```

## 커밋 메시지 컨벤션

권장하는 커밋 메시지 형식:
- `feat: 새로운 기능 추가`
- `fix: 버그 수정`
- `docs: 문서 업데이트`
- `refactor: 코드 리팩토링`
- `test: 테스트 추가`
- `chore: 기타 작업`

## 주의사항

1. **백업**: 중요한 변경사항은 스크립트 실행 전에 별도 백업 권장
2. **검토**: 대규모 변경사항은 `git status`로 먼저 확인
3. **네트워크**: 인터넷 연결 상태 확인 필요
4. **인증**: GitHub 인증 정보가 올바르게 설정되어 있어야 함

## 문제 해결

### 실행 권한 오류 (PowerShell)
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 인증 오류
- GitHub 토큰이나 SSH 키 설정 확인
- `git config --global user.name` 및 `git config --global user.email` 확인

### 네트워크 오류
- 인터넷 연결 상태 확인
- 방화벽 설정 확인

## 수동 Git 명령어 (참고용)

스크립트 없이 수동으로 실행하려면:
```bash
git add .
git commit -m "커밋 메시지"
git push origin main
```

---

**생성일**: 2024년 12월 19일  
**버전**: 1.0  
**작성자**: Percenty Development Team