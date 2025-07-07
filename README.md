# Percenty 자동화 프로젝트

퍼센티 플랫폼을 위한 자동화 도구입니다. 상품 등록, 이미지 번역, 배치 작업 등을 자동화합니다.

## 🚀 빠른 시작

### 1. 시스템 요구사항

- **Python**: 3.9 이상
- **메모리**: 최소 8GB (16GB 권장)
- **저장공간**: 최소 2GB
- **OS**: Windows 10/11, macOS, Linux
- **브라우저**: Chrome (최신 버전 권장)

### 2. 설치 방법

#### 2.1 저장소 클론
```bash
git clone <repository-url>
cd percenty_project
```

#### 2.2 가상환경 생성 (권장)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 2.3 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 설정

#### 3.1 계정 정보 설정
- `percenty_id.xlsx` 파일에 계정 정보를 입력하세요
- 각 계정별로 ID, 비밀번호, 서버 정보를 설정합니다

#### 3.2 브라우저 설정
- Chrome 브라우저가 설치되어 있어야 합니다
- 퍼센티 확장 프로그램이 자동으로 설치됩니다

### 4. 실행 방법

#### 4.1 GUI 모드 (권장)
```bash
python percenty_gui_advanced.py
```

#### 4.2 CLI 모드
```bash
# 단일 배치 실행
python cli/batch_cli.py single-batch <step> <account_id>

# 멀티 배치 실행
python cli/batch_cli.py multi-batch <step1> <step2> <step3>
```

## 📋 주요 기능

### 1. 상품 관리
- **Step 1**: 상품 검색 및 선택
- **Step 2**: 상품 정보 편집 (서버별 처리)
- **Step 3**: 이미지 번역 및 최적화
- **Step 4**: 상품 업로드 준비
- **Step 5**: 마켓별 상품 등록
- **Step 6**: 동적 업로드 및 최종 처리

### 2. 이미지 처리
- 자동 이미지 번역 (중국어 → 한국어)
- 이미지 크기 최적화
- 썸네일 자동 생성
- 불필요한 이미지 제거

### 3. 배치 작업
- 다중 계정 동시 처리
- 단계별 배치 실행
- 진행 상황 모니터링
- 오류 복구 및 재시도

### 4. 주기적 실행
- 스케줄링 기능
- 자동 재시작
- 로그 관리

## 🛠️ 기술 스택

### 핵심 라이브러리
- **Selenium**: 웹 자동화
- **Pandas**: 데이터 처리
- **EasyOCR**: 이미지 텍스트 인식
- **OpenCV**: 이미지 처리
- **Tkinter**: GUI 인터페이스
- **Schedule**: 작업 스케줄링

### 아키텍처
- **Clean Architecture** 적용
- **SOLID 원칙** 준수
- **TDD** 개발 방식
- 모듈화된 구조

## 📁 프로젝트 구조

```
percenty_project/
├── core/                    # 핵심 비즈니스 로직
│   ├── steps/              # 단계별 처리 로직
│   ├── account/            # 계정 관리
│   ├── browser/            # 브라우저 관리
│   └── common/             # 공통 유틸리티
├── batch/                  # 배치 작업 관리
├── cli/                    # 명령줄 인터페이스
├── coordinates/            # 좌표 및 선택자 정의
├── docs/                   # 문서
├── backup/                 # 백업 파일
└── requirements.txt        # 의존성 목록
```

## 🔧 개발 환경 설정

### 1. 개발 도구 설치
```bash
# 코드 품질 도구
pip install pytest pylint black mypy flake8

# 테스트 실행
pytest

# 코드 포맷팅
black .

# 린팅
pylint *.py
```

### 2. Git 설정
```bash
# 원격 변경사항 가져오기
git pull origin main

# 변경사항 커밋
git add .
git commit -m "feat: 새로운 기능 추가"
git push origin main
```

## 📝 사용 가이드

### 1. 첫 실행 시
1. `percenty_id.xlsx`에 계정 정보 입력
2. GUI 실행: `python percenty_gui_advanced.py`
3. 브라우저 설정 확인
4. 테스트 실행으로 동작 확인

### 2. 배치 작업 설정
1. 계정별 작업 단계 선택
2. 실행 간격 설정 (기본: 300초)
3. 배치 실행 시작
4. 진행 상황 모니터링

### 3. 문제 해결
- 로그 파일 확인: `percenty_gui_log_*.txt`
- 브라우저 재시작: GUI에서 "브라우저 재시작" 버튼
- 설정 초기화: 설정 파일 삭제 후 재실행

## 🚨 주의사항

1. **계정 보안**: 계정 정보를 안전하게 관리하세요
2. **리소스 사용**: 다중 브라우저 실행 시 메모리 사용량 주의
3. **네트워크**: 안정적인 인터넷 연결 필요
4. **업데이트**: 정기적으로 의존성 업데이트 확인

## 📞 지원

- **문서**: `docs/` 폴더의 상세 가이드 참조
- **이슈**: GitHub Issues를 통한 버그 신고
- **기능 요청**: 새로운 기능 제안

## 📄 라이선스

이 프로젝트는 내부 사용을 위한 것입니다.

---

**마지막 업데이트**: 2024년 12월
**버전**: 1.0.0