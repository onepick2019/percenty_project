# 🔐 보안 설정 가이드

## ⚠️ 중요: 텔레그램 봇 토큰 보안 사고 대응

### 발생한 문제
- 텔레그램 봇 토큰이 GitHub 공개 저장소에 노출됨
- GitHub Security Alert 발생
- 즉시 보안 조치 필요

### 완료된 조치
1. ✅ 설정 파일에서 하드코딩된 토큰 제거
2. ✅ 환경변수 방식으로 변경
3. ✅ 문서에서 민감 정보 제거
4. ✅ .env.example 파일 생성

### 🚨 사용자가 해야 할 조치

#### 1. 텔레그램 봇 토큰 무효화 (필수)
1. 텔레그램에서 @BotFather 검색
2. `/mybots` 명령어 입력
3. 해당 봇 선택
4. `Bot Settings` → `Revoke Bot Token` 클릭
5. 새로운 토큰 생성

#### 2. 새로운 환경변수 설정
```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집하여 새로운 토큰 입력
TELEGRAM_BOT_TOKEN=새로운_봇_토큰
TELEGRAM_CHAT_ID=채팅_ID
```

#### 3. Git 히스토리에서 민감 정보 제거 (권장)
```bash
# BFG Repo-Cleaner 사용 (권장)
git clone --mirror https://github.com/username/repo.git
java -jar bfg.jar --replace-text passwords.txt repo.git
cd repo.git
git reflog expire --expire=now --all && git gc --prune=now --aggressive
git push

# 또는 git filter-branch 사용
git filter-branch --force --index-filter \
'git rm --cached --ignore-unmatch batch/config/batch_config.json' \
--prune-empty --tag-name-filter cat -- --all
```

### 🛡️ 향후 보안 모범 사례

#### 1. 민감 정보 관리
- ❌ 설정 파일에 직접 저장
- ✅ 환경변수 사용
- ✅ 암호화된 설정 파일 사용
- ✅ 클라우드 시크릿 매니저 활용

#### 2. Git 커밋 전 체크리스트
- [ ] API 키, 토큰, 비밀번호 포함 여부 확인
- [ ] .env 파일이 .gitignore에 포함되어 있는지 확인
- [ ] 민감한 설정 파일 검토

#### 3. 자동화된 보안 검사
```bash
# pre-commit hook 설정
pip install pre-commit
echo "repos:
- repo: https://github.com/Yelp/detect-secrets
  rev: v1.4.0
  hooks:
  - id: detect-secrets" > .pre-commit-config.yaml
pre-commit install
```

### 📋 체크리스트

#### 즉시 조치 (필수)
- [ ] 텔레그램 봇 토큰 무효화
- [ ] 새로운 봇 토큰 생성
- [ ] .env 파일 생성 및 설정
- [ ] 애플리케이션 재시작

#### 추가 보안 강화 (권장)
- [ ] Git 히스토리에서 민감 정보 제거
- [ ] GitHub에서 해당 커밋 강제 삭제
- [ ] 다른 민감 정보 노출 여부 전체 검토
- [ ] 팀원들에게 보안 가이드라인 공유

### 🔍 추가 검토 항목
- 다른 API 키나 토큰 노출 여부
- 데이터베이스 연결 정보
- 서드파티 서비스 인증 정보
- 암호화 키나 시드

### 📞 문의
보안 관련 추가 질문이나 도움이 필요한 경우 즉시 연락하세요.