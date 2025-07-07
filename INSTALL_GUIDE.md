# Percenty 프로젝트 설치 가이드

이 문서는 다른 컴퓨터에 Percenty 프로젝트를 설치하는 방법을 설명합니다.

## 🖥️ 시스템별 설치 방법

### Windows 설치

#### 1. 사전 요구사항
- **Python 3.9 이상** ([python.org](https://www.python.org/downloads/)에서 다운로드)
- **Git** ([git-scm.com](https://git-scm.com/)에서 다운로드)
- **Chrome 브라우저** (최신 버전)
- **Visual C++ 재배포 가능 패키지** (OpenCV용)

#### 2. 자동 설치 (권장)
```cmd
# 1. 프로젝트 폴더로 이동
cd C:\Projects\percenty_project

# 2. 설치 스크립트 실행
install.bat
```

#### 3. 수동 설치
```cmd
# 1. 가상환경 생성
python -m venv venv

# 2. 가상환경 활성화
venv\Scripts\activate

# 3. 의존성 설치
pip install --upgrade pip
pip install -r requirements.txt
```

### macOS 설치

#### 1. 사전 요구사항
```bash
# Homebrew 설치 (없는 경우)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Python 설치
brew install python@3.11

# Git 설치
brew install git

# Chrome 설치
brew install --cask google-chrome
```

#### 2. 자동 설치 (권장)
```bash
# 1. 프로젝트 폴더로 이동
cd /path/to/percenty_project

# 2. 설치 스크립트에 실행 권한 부여
chmod +x install.sh

# 3. 설치 스크립트 실행
./install.sh
```

#### 3. 수동 설치
```bash
# 1. 가상환경 생성
python3 -m venv venv

# 2. 가상환경 활성화
source venv/bin/activate

# 3. 의존성 설치
pip install --upgrade pip
pip install -r requirements.txt
```

### Linux (Ubuntu/Debian) 설치

#### 1. 시스템 의존성 설치
```bash
# 시스템 패키지 업데이트
sudo apt update

# Python 및 개발 도구 설치
sudo apt install python3 python3-pip python3-venv python3-dev

# OpenCV 의존성 설치
sudo apt install libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1

# Git 설치
sudo apt install git

# Chrome 설치
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install google-chrome-stable
```

#### 2. 자동 설치 (권장)
```bash
# 1. 프로젝트 폴더로 이동
cd /path/to/percenty_project

# 2. 설치 스크립트에 실행 권한 부여
chmod +x install.sh

# 3. 설치 스크립트 실행
./install.sh
```

## 🔧 설치 후 설정

### 1. 계정 정보 설정
```bash
# percenty_id.xlsx 파일 편집
# 각 계정의 ID, 비밀번호, 서버 정보 입력
```

### 2. 브라우저 설정 확인
- Chrome 브라우저가 기본 브라우저로 설정되어 있는지 확인
- 퍼센티 확장 프로그램이 자동으로 설치됩니다

### 3. 첫 실행 테스트
```bash
# 가상환경 활성화 (필요한 경우)
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# GUI 실행
python percenty_gui_advanced.py
```

## 🚨 문제 해결

### 일반적인 문제

#### 1. Python 버전 문제
```bash
# Python 버전 확인
python --version
# 또는
python3 --version

# 3.9 이상이어야 함
```

#### 2. 의존성 설치 실패
```bash
# pip 업그레이드
pip install --upgrade pip

# 개별 패키지 설치 시도
pip install pandas
pip install numpy
pip install selenium
```

#### 3. EasyOCR 설치 문제
```bash
# Windows에서 Visual C++ 재배포 가능 패키지 필요
# https://aka.ms/vs/17/release/vc_redist.x64.exe

# Linux에서 추가 의존성 설치
sudo apt install libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1
```

#### 4. OpenCV 설치 문제
```bash
# 대안 설치 방법
pip install opencv-python-headless

# Linux에서 GUI 의존성 문제 시
sudo apt install python3-opencv
```

### 시스템별 특정 문제

#### Windows
- **긴 경로 문제**: Windows 설정에서 긴 경로 지원 활성화
- **권한 문제**: 관리자 권한으로 명령 프롬프트 실행
- **인코딩 문제**: `chcp 65001` 명령어로 UTF-8 설정

#### macOS
- **Xcode 명령줄 도구**: `xcode-select --install`
- **권한 문제**: `sudo` 사용 시 주의
- **M1/M2 Mac**: Rosetta 2 설치 필요할 수 있음

#### Linux
- **디스플레이 문제**: `export DISPLAY=:0` 설정
- **권한 문제**: 사용자를 적절한 그룹에 추가
- **의존성 문제**: 배포판별 패키지 관리자 사용

## 📋 설치 확인 체크리스트

- [ ] Python 3.9+ 설치됨
- [ ] 가상환경 생성됨
- [ ] 모든 의존성 설치됨
- [ ] Chrome 브라우저 설치됨
- [ ] percenty_id.xlsx 파일 설정됨
- [ ] GUI 정상 실행됨
- [ ] 브라우저 자동 실행됨
- [ ] 퍼센티 사이트 로그인 가능

## 🆘 추가 지원

설치 중 문제가 발생하면:

1. **로그 확인**: 오류 메시지를 자세히 읽어보세요
2. **문서 참조**: `docs/` 폴더의 상세 가이드 확인
3. **이슈 신고**: GitHub Issues에 문제 상황 보고
4. **환경 정보 제공**: OS, Python 버전, 오류 메시지 포함

---

**참고**: 이 가이드는 최신 버전 기준으로 작성되었습니다. 시스템 환경에 따라 일부 단계가 다를 수 있습니다.