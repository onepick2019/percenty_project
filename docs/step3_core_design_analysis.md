# Step3 코어 설계 분석 및 구현 계획

## 1. 기존 Step5 코어들 분석

### Step5 코어들의 공통 구조

#### 1.1 임포트 구조
```python
# 기존 모듈들 임포트 (루트에서)
try:
    from product_editor_core5_1 import ProductEditorCore5_1  # 각 단계별 코어
except ImportError:
    pass
from browser_core import BrowserCore
from login_percenty import PercentyLogin
from menu_clicks import MenuClicks
from coordinates.coordinates_all import MENU
from timesleep import DELAY_STANDARD, DELAY_SHORT
from human_delay import HumanLikeDelay
from ui_elements import UI_ELEMENTS
from click_utils import smart_click

# 공통 함수들 임포트
from core.common.modal_handler import handle_post_login_modals, hide_channel_talk, close_modal_dialogs
from core.common.navigation_handler import navigate_to_ai_sourcing, navigate_to_group_management5
from core.common.product_handler import check_toggle_state, toggle_product_view
from core.common.ui_handler import periodic_ui_cleanup, ensure_clean_ui_before_action
```

#### 1.2 클래스 구조
- `__init__(self, driver=None)`: 드라이버 초기화
- `setup_managers()`: 관리자 객체들 설정
- `execute_step5_X_with_browser_restart()`: 브라우저 재시작 방식 배치 실행
- `execute_step5_X()`: 단일 실행 메서드
- 기타 헬퍼 메서드들

#### 1.3 배치 처리 로직
- **청크 기반 처리**: 지정된 수량(chunk_size)마다 브라우저 재시작
- **결과 누적**: 각 청크의 결과를 total_result에 누적
- **에러 처리**: 청크별 에러 처리 및 로깅
- **브라우저 재시작**: 마지막 청크가 아니면 브라우저 재시작

## 2. Product_editor_core3 분석

### 2.1 핵심 기능
- **키워드 기반 검색**: `search_products_by_keyword(keyword)`
- **개별 상품 처리**: `process_keyword_with_individual_modifications(keyword, target_group, task_data)`
- **상품 수정**: H~M열 데이터 기반 수정 작업
- **그룹 이동**: 수정 완료 후 target_group으로 이동

### 2.2 처리 방식의 특징
- **키워드 단위 처리**: provider_code별로 상품 검색 및 처리
- **페이지 단위 반복**: 한 키워드로 검색된 모든 상품을 페이지별로 처리
- **개별 상품 수정**: 각 상품마다 모달창 열기 → 수정 → 닫기 → 그룹이동
- **서버별 필터링**: final_group 컬럼으로 서버1/서버2/서버3 구분

### 2.3 주요 메서드
```python
# 엑셀에서 작업 목록 로드 (서버 필터링 포함)
load_task_list_from_excel_with_server_filter(account_id, step="step3", server_name=None)

# 키워드로 상품 검색
search_products_by_keyword(keyword)

# 첫 번째 상품 모달창 열기
open_first_product_modal()

# 상품 수정 작업 (H~M열 데이터 기반)
process_product_modifications(task_data)

# 키워드별 전체 처리 (핵심 메서드)
process_keyword_with_individual_modifications(keyword, target_group, task_data)

# 상품을 타겟 그룹으로 이동
move_product_to_target_group(target_group)
```

## 3. Step3 코어들 설계 방안

### 3.1 파일 구조
```
core/steps/
├── step3_1_core.py  # 서버1 전용
├── step3_2_core.py  # 서버2 전용
└── step3_3_core.py  # 서버3 전용
```

### 3.2 각 코어의 역할
- **step3_1_core.py**: server_name="서버1"로 product_editor_core3 사용
- **step3_2_core.py**: server_name="서버2"로 product_editor_core3 사용
- **step3_3_core.py**: server_name="서버3"로 product_editor_core3 사용

### 3.3 중앙관리식 구조 적용

#### 3.3.1 임포트 구조 (Step5와 동일)
```python
# 기존 모듈들 임포트
try:
    from product_editor_core3 import ProductEditorCore3
except ImportError:
    pass
from browser_core import BrowserCore
from login_percenty import PercentyLogin
from menu_clicks import MenuClicks
# ... 기타 공통 임포트

# 공통 함수들 임포트
from core.common.modal_handler import handle_post_login_modals, hide_channel_talk
from core.common.navigation_handler import navigate_to_registered_products  # step3용 네비게이션
from core.common.ui_handler import periodic_ui_cleanup, ensure_clean_ui_before_action
```

#### 3.3.2 클래스 구조
```python
class Step3_1Core:  # Step3_2Core, Step3_3Core도 동일 구조
    def __init__(self, driver=None, server_name="서버1"):
        self.driver = driver
        self.server_name = server_name
        self.browser_core = None
        self.login_manager = None
        self.menu_clicks = None
        self.product_editor = None
        
        if driver:
            self.setup_managers()
    
    def setup_managers(self):
        # Step5와 동일한 관리자 객체 설정
        # + ProductEditorCore3 초기화
        
    def execute_step3_1_with_browser_restart(self, provider_codes: List[str], chunk_size: int = 5, account_info: Dict = None):
        # 브라우저 재시작 방식 배치 실행
        
    def execute_step3_1(self, provider_codes: List[str], account_info: Dict = None):
        # 단일 실행 메서드
```

## 4. Step3 배치 처리 방식

### 4.1 Step5와의 차이점

| 구분 | Step5 | Step3 |
|------|-------|-------|
| 처리 단위 | 고정 수량 (quantity) | 키워드 목록 (provider_codes) |
| 분할 기준 | 상품 개수 | 키워드 개수 |
| 진행률 측정 | 처리된 상품 수 / 총 상품 수 | 처리된 키워드 수 / 총 키워드 수 |
| 중단점 복구 | 상품 번호 기반 | 키워드 기반 |

### 4.2 배치 분할 전략

#### 4.2.1 키워드 기반 청크 분할
```python
# 예시: 20개 키워드를 5개씩 4개 청크로 분할
provider_codes = ["A01", "A02", "A03", ..., "A20"]
chunk_size = 5

# 청크 1: ["A01", "A02", "A03", "A04", "A05"]
# 청크 2: ["A06", "A07", "A08", "A09", "A10"]
# 청크 3: ["A11", "A12", "A13", "A14", "A15"]
# 청크 4: ["A16", "A17", "A18", "A19", "A20"]
```

#### 4.2.2 진행 상황 추적
```python
total_result = {
    'success': False,
    'processed_keywords': 0,
    'failed_keywords': 0,
    'total_products_processed': 0,
    'errors': [],
    'chunks_completed': 0,
    'total_chunks': 0,
    'completed_keywords': []  # 완료된 키워드 목록
}
```

### 4.3 중단점 복구 메커니즘

#### 4.3.1 진행 상황 저장
```python
# progress_[account_id]_step3_[server].json
{
    "account_id": "account123",
    "server_name": "서버1",
    "total_keywords": 20,
    "completed_keywords": ["A01", "A02", "A03"],
    "current_chunk": 1,
    "last_updated": "2024-01-15T10:30:00"
}
```

#### 4.3.2 재시작 시 복구
```python
def resume_from_progress(self, account_id):
    progress_file = f"progress_{account_id}_step3_{self.server_name}.json"
    if os.path.exists(progress_file):
        with open(progress_file, 'r') as f:
            progress = json.load(f)
        
        # 완료되지 않은 키워드만 추출
        all_keywords = self.load_keywords_from_excel(account_id)
        remaining_keywords = [k for k in all_keywords if k not in progress['completed_keywords']]
        
        return remaining_keywords
    return None
```

## 5. 구현 계획

### 5.1 1단계: 기본 구조 구축
1. **step3_1_core.py 생성**
   - Step5_1Core를 템플릿으로 사용
   - ProductEditorCore3 임포트 및 초기화
   - server_name="서버1" 설정

2. **step3_2_core.py, step3_3_core.py 생성**
   - step3_1_core.py와 동일 구조
   - 각각 server_name="서버2", "서버3" 설정

### 5.2 2단계: 배치 처리 로직 구현
1. **키워드 기반 청크 분할 로직**
2. **진행 상황 추적 및 저장**
3. **중단점 복구 메커니즘**
4. **브라우저 재시작 처리**

### 5.3 3단계: BatchManager 통합
1. **BatchManager에 step3 코어들 추가**
2. **step3 전용 실행 메서드 구현**
3. **기존 step2+step3 연속 실행과 분리**

### 5.4 4단계: 테스트 및 최적화
1. **각 서버별 개별 테스트**
2. **배치 분할 크기 최적화**
3. **에러 처리 강화**
4. **로깅 및 모니터링 개선**

## 6. 예상 효과

### 6.1 메모리 효율성
- 키워드 단위 청크 처리로 메모리 사용량 제어
- 브라우저 재시작으로 메모리 누수 방지

### 6.2 안정성 향상
- 중단점 복구로 작업 연속성 보장
- 서버별 독립 실행으로 간섭 최소화

### 6.3 모니터링 개선
- 키워드별 진행 상황 추적
- 상세한 에러 로깅 및 리포팅

### 6.4 확장성
- 중앙관리식 구조로 유지보수 용이
- 새로운 서버 추가 시 쉬운 확장

## 7. 주의사항

### 7.1 기존 코드와의 호환성
- product_editor_core3.py의 기존 인터페이스 유지
- 기존 step3 실행 파일들과의 호환성 고려

### 7.2 서버별 데이터 격리
- 각 서버의 진행 상황 파일 분리
- 동시 실행 시 데이터 충돌 방지

### 7.3 에러 처리
- 키워드별 에러 발생 시 다음 키워드 계속 처리
- 치명적 에러 발생 시 안전한 중단 및 상태 저장