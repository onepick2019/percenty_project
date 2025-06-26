# 카페24 엑셀 매크로 Python 프로그램 개발 계획

## 📋 프로젝트 개요

### 현재 상황 분석
- **기존 엑셀 파일**: `카페24 최적화.xlsm` (27MB)
- **주요 시트**: 카페24업데이트, 카페24자료, 수정작업, 판매가 설정, 분류코드 등
- **VBA 매크로**: `A02_카페24_기초자료만들기_NEW_ALL` 등 복잡한 데이터 처리 로직
- **처리 데이터**: 약 3,000개 상품, 90개 컬럼의 대용량 데이터

### 개발 목표
기존 VBA 매크로의 모든 기능을 Python으로 재구현하여 더 빠르고 안정적인 상품 데이터 처리 시스템 구축

## 🔍 엑셀 파일 구조 분석

### 주요 시트별 역할

#### 1. 카페24업데이트 시트 (2,999행 × 90열)
- **역할**: 카페24 쇼핑몰 업로드용 최종 데이터
- **주요 컬럼**:
  - 상품 기본정보: 상품코드, 상품명, 모델명
  - 가격정보: 소비자가, 공급가, 판매가
  - 옵션정보: 옵션입력, 색상설정, 사이즈
  - 상세설명: HTML 형태의 상품 상세설명
  - 이미지: 상세/목록/축소 이미지 경로
  - 배송/정책: 배송정보, 교환/반품 안내

#### 2. 카페24자료 시트
- **역할**: 원본 상품 데이터 저장소
- **특징**: 가공 전 원시 데이터 보관

#### 3. 수정작업 시트
- **역할**: 데이터 변환 및 가공 작업 공간
- **특징**: 매크로 실행 시 임시 작업 영역

#### 4. 판매가 설정 시트 (118행 × 33열)
- **역할**: 가격 계산 로직 및 마진율 설정
- **특징**: 공급가 기반 판매가 자동 계산

#### 5. 분류코드 시트 (118행 × 267열)
- **역할**: 상품 카테고리 분류 및 키워드 매핑
- **특징**: 대분류/중분류/소분류별 검색어 자동 생성

## 🎯 VBA 매크로 기능 분석

### A02_카페24_기초자료만들기_NEW_ALL 매크로 주요 기능

1. **데이터 초기화**
   - "수정작업" 시트 기존 데이터 삭제
   - 작업 영역 준비

2. **기본 데이터 복사**
   - 상품코드, 자체상품코드, 공급가, 판매가, 상품명 복사
   - "카페24자료" → "수정작업" 시트 이동

3. **옵션 데이터 처리**
   - 상품 옵션 정보 복사 및 정리
   - 색상/사이즈 옵션 표준화

4. **상세설명 처리**
   - HTML 상세설명 복사
   - 글자수 계산 및 최적화
   - 상세설명 변환 및 정리

5. **메타정보 추출**
   - 1688 상품코드 추출
   - 판매자ID, 꼬릿말, 상품소싱URL 처리

6. **카테고리 분류**
   - 자동 카테고리 매핑
   - 분류코드 기반 정리

7. **필수 정보 보완**
   - 브랜드명, 시즌정보 추가
   - 정보고시분류코드 설정
   - 검색어, 모델명 자동 생성

8. **가격 최적화**
   - 옵션 차등가 상품 식별
   - 서버/그룹별 가격 구분
   - 자사상품코드 변경

9. **최종 처리**
   - `A02_퍼센티_카페24업데이트시트만들기_SP1` 매크로 실행
   - 최종 업로드 시트 생성

## 🏗️ Python 프로그램 아키텍처 설계

### 모듈 구조 (Clean Architecture 적용)

```
src/
├── core/                    # 핵심 비즈니스 로직
│   ├── entities/           # 엔티티 (상품, 옵션, 카테고리)
│   ├── use_cases/          # 유스케이스 (데이터 변환, 가격 계산)
│   └── interfaces/         # 인터페이스 정의
├── infrastructure/         # 외부 의존성
│   ├── excel/             # 엑셀 파일 처리
│   ├── data/              # 데이터 저장소
│   └── config/            # 설정 관리
├── application/           # 애플리케이션 서비스
│   ├── services/          # 비즈니스 서비스
│   └── dto/               # 데이터 전송 객체
└── presentation/          # 프레젠테이션 계층
    ├── cli/               # 명령행 인터페이스
    └── gui/               # GUI (선택사항)
```

### 핵심 클래스 설계

#### 1. Product Entity
```python
@dataclass
class Product:
    code: str
    name: str
    supply_price: float
    selling_price: float
    options: List[ProductOption]
    description: str
    images: ProductImages
    category: Category
    meta_info: ProductMetaInfo
```

#### 2. PriceCalculator Service
```python
class PriceCalculator:
    def calculate_selling_price(self, supply_price: float, margin_rate: float) -> float
    def apply_option_price_difference(self, base_price: float, option: ProductOption) -> float
    def validate_price_range(self, price: float) -> bool
```

#### 3. CategoryMapper Service
```python
class CategoryMapper:
    def map_category_by_keywords(self, product_name: str) -> Category
    def generate_search_keywords(self, category: Category) -> List[str]
    def validate_category_mapping(self, category: Category) -> bool
```

#### 4. DescriptionProcessor Service
```python
class DescriptionProcessor:
    def process_html_description(self, raw_html: str) -> str
    def calculate_description_length(self, description: str) -> int
    def optimize_description(self, description: str) -> str
```

## 🛠️ 기술 스택 및 라이브러리

### 필수 라이브러리
```python
# 데이터 처리
pandas>=2.0.0           # 엑셀 데이터 처리
openpyxl>=3.1.0         # 엑셀 파일 읽기/쓰기
numpy>=1.24.0           # 수치 계산

# 웹 스크래핑 (필요시)
beautifulsoup4>=4.12.0  # HTML 파싱
requests>=2.31.0        # HTTP 요청

# 데이터 검증
pydantic>=2.0.0         # 데이터 모델 검증

# 로깅 및 설정
loguru>=0.7.0           # 로깅
python-dotenv>=1.0.0    # 환경변수 관리

# 테스트
pytest>=7.4.0           # 단위 테스트
pytest-cov>=4.1.0       # 테스트 커버리지

# CLI (선택사항)
click>=8.1.0            # 명령행 인터페이스
rich>=13.0.0            # 터미널 출력 개선
```

## 📝 개발 단계별 로드맵

### Phase 1: 기반 구조 구축 (1-2주)
- [ ] 프로젝트 구조 설정
- [ ] 핵심 엔티티 클래스 구현
- [ ] 엑셀 파일 읽기/쓰기 모듈 구현
- [ ] 기본 테스트 케이스 작성
- [ ] 로깅 및 설정 시스템 구축

### Phase 2: 데이터 처리 엔진 구현 (2-3주)
- [ ] 엑셀 데이터 파싱 및 검증
- [ ] 상품 데이터 변환 로직
- [ ] 가격 계산 엔진 구현
- [ ] 옵션 데이터 처리 로직
- [ ] 상세설명 처리 엔진

### Phase 3: 비즈니스 로직 구현 (2-3주)
- [ ] 카테고리 자동 매핑 시스템
- [ ] 검색어 자동 생성 로직
- [ ] 메타정보 추출 및 처리
- [ ] 이미지 경로 처리 로직
- [ ] 데이터 검증 및 품질 관리

### Phase 4: 통합 및 최적화 (1-2주)
- [ ] 전체 워크플로우 통합
- [ ] 성능 최적화
- [ ] 에러 처리 및 복구 로직
- [ ] 사용자 인터페이스 구현
- [ ] 문서화 및 사용자 가이드

### Phase 5: 테스트 및 배포 (1주)
- [ ] 통합 테스트 실행
- [ ] 실제 데이터로 검증
- [ ] 성능 벤치마크
- [ ] 배포 및 운영 가이드

## 🚀 즉시 시작 가능한 작업

### 1. 프로젝트 초기 설정
```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 필수 라이브러리 설치
pip install pandas openpyxl numpy pydantic loguru python-dotenv pytest
```

### 2. 기본 디렉토리 구조 생성
```bash
mkdir -p src/{core/{entities,use_cases,interfaces},infrastructure/{excel,data,config},application/{services,dto},presentation/{cli,gui}}
mkdir -p tests/{unit,integration}
mkdir -p docs/{api,guides}
```

### 3. 첫 번째 구현 목표
- 엑셀 파일 읽기 기능 구현
- Product 엔티티 클래스 정의
- 기본 데이터 변환 로직 구현

## 📊 예상 성능 개선 효과

### 처리 속도
- **현재 VBA**: 3,000개 상품 처리 시 약 10-15분
- **예상 Python**: 3,000개 상품 처리 시 약 2-3분 (5배 향상)

### 안정성
- **메모리 관리**: Python의 자동 메모리 관리로 안정성 향상
- **에러 처리**: 체계적인 예외 처리로 중단 없는 처리
- **데이터 검증**: Pydantic을 통한 강력한 데이터 검증

### 확장성
- **모듈화**: 기능별 독립적인 모듈로 유지보수 용이
- **테스트**: 자동화된 테스트로 품질 보장
- **설정 관리**: 환경별 설정 분리로 운영 편의성 향상

## 🔧 개발 환경 요구사항

### 시스템 요구사항
- **Python**: 3.9 이상
- **메모리**: 최소 8GB (16GB 권장)
- **저장공간**: 최소 2GB
- **OS**: Windows 10/11, macOS, Linux

### 개발 도구
- **IDE**: VS Code, PyCharm
- **버전 관리**: Git
- **패키지 관리**: pip, poetry (선택사항)
- **테스트**: pytest

## 📈 성공 지표 (KPI)

### 기능적 지표
- [ ] 100% VBA 매크로 기능 재현
- [ ] 3,000개 상품 무오류 처리
- [ ] 90개 컬럼 데이터 완전 변환

### 성능 지표
- [ ] 처리 시간 50% 이상 단축
- [ ] 메모리 사용량 30% 이상 절약
- [ ] 에러 발생률 90% 이상 감소

### 품질 지표
- [ ] 테스트 커버리지 90% 이상
- [ ] 코드 품질 점수 A 등급
- [ ] 문서화 완성도 95% 이상

## 🎯 다음 단계

1. **엑셀 파일 상세 분석**: 각 시트별 데이터 구조 완전 파악
2. **VBA 코드 분석**: 기존 매크로 로직 완전 이해
3. **프로토타입 개발**: 핵심 기능 최소 구현체 제작
4. **성능 테스트**: 실제 데이터로 처리 속도 검증
5. **점진적 기능 확장**: 단계별 기능 추가 및 검증

---

**📞 문의사항이나 추가 요구사항이 있으시면 언제든 말씀해 주세요!**

이 계획서를 바탕으로 체계적이고 효율적인 Python 프로그램 개발을 진행할 수 있습니다.