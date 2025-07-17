# 🎯 즉시 실행 가능한 코드 품질 개선 액션 플랜

## 📋 **1단계: 중복 파일 정리 (우선순위 1)**

### 🔍 **현재 상황 분석**
프로젝트에서 발견된 주요 중복 파일들:

#### A. Product Editor 시리즈 (7개 버전)
```
product_editor_core.py → product_editor_core6_dynamic_4.py
```
- `product_editor_core.py` (원본)
- `product_editor_core2.py`
- `product_editor_core3.py`
- `product_editor_core4.py`
- `product_editor_core5_1.py`, `product_editor_core5_2.py`, `product_editor_core5_3.py`
- `product_editor_core6_1.py`
- `product_editor_core6_dynamic_1.py` ~ `product_editor_core6_dynamic_4.py`

#### B. Dropdown Utils 시리즈 (6개 버전)
```
dropdown_utils.py → dropdown_utils5.py
dropdown_utils_common.py, dropdown_utils_unified.py
```

#### C. Percenty Step 시리즈 (30개 이상)
```
percenty_new_step1.py
percenty_new_step2.py, percenty_new_step2_server1-3.py
percenty_new_step3_1_1.py ~ percenty_new_step3_3_3.py
percenty_new_step4.py
percenty_new_step5_1.py ~ percenty_new_step5_3.py
percenty_new_step6_1.py, percenty_new_step6_dynamic_1-4.py
```

#### D. Image Utils 시리즈 (3개 버전)
```
image_utils.py, image_utils3.py, image_utils5.py
```

### 🚀 **즉시 실행 계획**

#### **Phase 1: 백업 및 분석 (30분)**
1. **현재 상태 백업**
   ```bash
   # 전체 프로젝트 백업
   cp -r c:\Projects\percenty_project c:\Projects\percenty_project_backup_$(date +%Y%m%d)
   ```

2. **활성 파일 식별**
   - 최근 수정 날짜 확인
   - 다른 파일에서 import되는 파일 확인
   - 실제 사용되는 파일 식별

#### **Phase 2: 중복 파일 정리 (1시간)**

1. **Legacy 폴더 생성 및 이동**
   ```
   legacy/
   ├── product_editor/
   ├── dropdown_utils/
   ├── percenty_steps/
   └── image_utils/
   ```

2. **최신 버전만 유지**
   - `product_editor_core6_dynamic_4.py` → `product_editor_core.py`로 통합
   - `dropdown_utils5.py` → `dropdown_utils.py`로 통합
   - `image_utils5.py` → `image_utils.py`로 통합

3. **Import 문 업데이트**
   - 모든 파일에서 구버전 import를 최신 버전으로 변경

---

## 📁 **2단계: 프로젝트 구조 개선 (우선순위 2)**

### 🎯 **목표 구조**
```
src/
├── core/                    # 핵심 비즈니스 로직
│   ├── steps/              # 단계별 처리 로직 (기존 유지)
│   ├── browser/            # 브라우저 관련 (기존 유지)
│   ├── account/            # 계정 관리 (기존 유지)
│   └── common/             # 공통 유틸리티 (기존 유지)
├── automation/             # 자동화 스크립트
│   ├── product_editor/     # 상품 편집 관련
│   ├── market_managers/    # 마켓별 관리자
│   └── batch_processors/   # 배치 처리
├── utils/                  # 유틸리티 함수들
│   ├── ui/                # UI 관련 유틸리티
│   ├── image/             # 이미지 처리
│   └── excel/             # 엑셀 처리
├── config/                 # 설정 파일들
└── gui/                   # GUI 관련 파일들
```

### 🚀 **실행 단계**

#### **Step 1: 새 디렉토리 생성**
```python
# 디렉토리 생성 스크립트
import os

directories = [
    "src/automation/product_editor",
    "src/automation/market_managers", 
    "src/automation/batch_processors",
    "src/utils/ui",
    "src/utils/image",
    "src/utils/excel",
    "src/config",
    "src/gui"
]

for dir_path in directories:
    os.makedirs(dir_path, exist_ok=True)
```

#### **Step 2: 파일 분류 및 이동**
```python
# 파일 이동 매핑
file_moves = {
    # Product Editor 관련
    "product_editor_core.py": "src/automation/product_editor/",
    "product_name_editor.py": "src/automation/product_editor/",
    
    # Market Managers
    "market_manager*.py": "src/automation/market_managers/",
    
    # Batch Processors  
    "batch_processor*.py": "src/automation/batch_processors/",
    
    # Utils
    "dropdown_utils.py": "src/utils/ui/",
    "image_utils.py": "src/utils/image/",
    "dom_utils.py": "src/utils/ui/",
    "click_utils.py": "src/utils/ui/",
    
    # GUI
    "percenty_gui_advanced.py": "src/gui/",
    
    # Config
    "config.py": "src/config/",
    "*.json": "src/config/"
}
```

---

## ⚙️ **3단계: 설정 중앙화 (우선순위 3)**

### 🎯 **목표**
하드코딩된 설정값들을 중앙 설정 파일로 통합

### 📝 **설정 파일 구조**
```python
# src/config/constants.py
class TimeoutConfig:
    """타임아웃 관련 설정"""
    DEFAULT_WAIT = 3
    MODAL_TIMEOUT = 10
    PAGE_LOAD_TIMEOUT = 30
    ELEMENT_WAIT = 15
    MAX_RETRIES = 3

class UIConfig:
    """UI 관련 설정"""
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 900
    SCROLL_PAUSE = 1
    CLICK_DELAY = 0.5

class BatchConfig:
    """배치 처리 설정"""
    DEFAULT_QUANTITY = 5
    MAX_CONCURRENT = 3
    RETRY_INTERVAL = 60
    LOG_LEVEL = "INFO"

class PathConfig:
    """경로 관련 설정"""
    EXCEL_FILE = "percenty_id.xlsx"
    LOG_DIR = "logs"
    BACKUP_DIR = "backup"
    CONFIG_DIR = "src/config"
```

### 🚀 **실행 계획**
1. **설정 파일 생성** (15분)
2. **하드코딩된 값 추출** (30분)
3. **Import 문 업데이트** (30분)

---

## 🧹 **4단계: 공통 유틸리티 개발 (우선순위 4)**

### 🎯 **목표**
중복되는 코드 패턴을 공통 유틸리티로 추상화

### 📝 **주요 유틸리티 클래스**

#### A. 표준화된 에러 핸들러
```python
# src/utils/error_handler.py
class StandardErrorHandler:
    @staticmethod
    def handle_with_retry(func, max_retries=3, delay=1):
        """표준화된 재시도 로직"""
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                time.sleep(delay * (attempt + 1))
```

#### B. 공통 UI 조작 클래스
```python
# src/utils/ui/common_actions.py
class CommonUIActions:
    def __init__(self, driver):
        self.driver = driver
    
    def wait_and_click(self, selector, timeout=10):
        """요소 대기 후 클릭"""
        pass
    
    def handle_modal(self, modal_selector, close_selector):
        """모달창 처리"""
        pass
    
    def select_dropdown(self, dropdown_selector, option_text):
        """드롭다운 선택"""
        pass
```

---

## 📊 **5단계: 진행 상황 추적**

### 📝 **체크리스트**
- [ ] **Phase 1 완료**: 중복 파일 정리
- [ ] **Phase 2 완료**: 프로젝트 구조 개선  
- [ ] **Phase 3 완료**: 설정 중앙화
- [ ] **Phase 4 완료**: 공통 유틸리티 개발
- [ ] **테스트 완료**: 기존 기능 정상 동작 확인

### 📈 **예상 소요 시간**
- **1단계**: 1.5시간
- **2단계**: 2시간  
- **3단계**: 1시간
- **4단계**: 2시간
- **총 소요 시간**: 6.5시간

### 🎯 **다음 액션**
어떤 단계부터 시작하시겠습니까? 

1. **중복 파일 정리**부터 시작 (가장 즉각적인 효과)
2. **프로젝트 구조 개선**부터 시작 (장기적 관점)
3. **설정 중앙화**부터 시작 (개발 편의성 우선)

구체적인 실행 계획을 함께 수립해보겠습니다!