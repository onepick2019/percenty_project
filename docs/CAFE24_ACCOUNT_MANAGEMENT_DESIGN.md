# 🏪 카페24 계정 관리 시스템 설계 문서

## 📋 프로젝트 개요

### 🎯 핵심 목표
- **100여개 카페24 계정**을 **15-20개 사업자 그룹**으로 효율적 관리
- **카테고리별 순차 상품 전송/삭제** 자동화
- **중앙 관리 방식**으로 통합 운영
- **서버 환경 고려** 배치 실행 방식 선택 가능

### 🏗️ 시스템 아키텍처

```
카페24 관리 시스템
├── 사업자 관리 (15-20개)
│   ├── 사업자A (5개 계정)
│   ├── 사업자B (4개 계정)
│   └── 사업자C (6개 계정)
├── 카테고리 관리 (200-300개)
│   ├── 대분류 → 중분류 → 소분류 → 세분류
│   └── 마켓별 매핑 정보
└── 배치 실행 엔진
    ├── 순차 실행 모드
    └── 동시 실행 모드
```

---

## 🗂️ 엑셀 파일 구조 설계

### 📊 **1. `owners` 시트 - 사업자 정보**

| 컬럼명 | 타입 | 설명 | 예시 |
|--------|------|------|------|
| `owner_id` | 문자열 | 사업자 고유 ID | `BIZ001` |
| `owner_name` | 문자열 | 사업자명 | `김사장` |
| `business_type` | 문자열 | 사업 분야 | `의류`, `전자제품` |
| `account_count` | 숫자 | 보유 계정 수 | `5` |
| `active` | Y/N | 활성화 상태 | `Y` |
| `description` | 문자열 | 비고 | `여성의류 전문` |

### 📊 **2. `accounts` 시트 - 계정 정보**

| 컬럼명 | 타입 | 설명 | 예시 |
|--------|------|------|------|
| `account_id` | 문자열 | 계정 고유 ID | `ACC001` |
| `owner_id` | 문자열 | 소속 사업자 ID | `BIZ001` |
| `store_name` | 문자열 | 스토어명 | `패션몰1` |
| `cafe24_url` | 문자열 | 카페24 URL | `store1.cafe24.com` |
| `login_id` | 문자열 | 로그인 아이디 | `user1` |
| `password` | 문자열 | 로그인 비밀번호 | `pass1` |
| `active` | Y/N | 활성화 상태 | `Y` |
| `priority` | 숫자 | 실행 우선순위 | `1` |
| `description` | 문자열 | 계정 설명 | `여성의류 메인` |

### 📊 **3. `categories` 시트 - 카테고리 정보**

| 컬럼명 | 타입 | 설명 | 예시 |
|--------|------|------|------|
| `category_id` | 문자열 | 카테고리 고유 ID | `CAT001` |
| `large_category` | 문자열 | 대분류 | `의류` |
| `medium_category` | 문자열 | 중분류 | `여성의류` |
| `small_category` | 문자열 | 소분류 | `상의` |
| `detail_category` | 문자열 | 세분류 | `블라우스` |
| `target_markets` | 문자열 | 전송 대상 마켓 | `11번가,쿠팡,옥션` |
| `cafe24_code` | 문자열 | 카페24 카테고리 코드 | `1001` |
| `priority` | 숫자 | 처리 우선순위 | `1` |
| `active` | Y/N | 활성화 상태 | `Y` |

### 📊 **4. `batch_config` 시트 - 배치 설정**

| 컬럼명 | 타입 | 설명 | 예시 |
|--------|------|------|------|
| `config_key` | 문자열 | 설정 키 | `execution_mode` |
| `config_value` | 문자열 | 설정 값 | `sequential` |
| `description` | 문자열 | 설명 | `순차실행/동시실행` |

---

## 🖥️ GUI 워크플로우 설계

### **1단계: 사업자 선택**
```
=== 카페24 관리 시스템 ===
사업자를 선택하세요:

1. 김사장 (5개 계정) - 의류 전문
2. 박대표 (4개 계정) - 전자제품
3. 이사장 (6개 계정) - 생활용품
4. 최사장 (3개 계정) - 스포츠용품
...
15. 전체 사업자 (100개 계정)

선택: _
```

### **2단계: 작업 유형 선택**
```
=== 김사장 계정 관리 (5개 계정) ===
작업을 선택하세요:

1. 🚀 전체 계정 배치 작업
   ├── 순차 실행 (안정성 우선)
   └── 동시 실행 (속도 우선)

2. 🎯 개별 계정 선택 작업

3. 📦 카테고리별 상품 전송

4. 🗑️ 카테고리별 상품 삭제

5. 📊 계정 상태 확인

선택: _
```

### **3단계: 실행 모드 선택 (배치 작업 시)**
```
=== 배치 실행 모드 선택 ===
서버 환경을 고려하여 실행 방식을 선택하세요:

1. 🔄 순차 실행 (권장)
   ├── 안정성: ⭐⭐⭐⭐⭐
   ├── 속도: ⭐⭐⭐
   └── 서버 부하: 낮음

2. ⚡ 동시 실행 (고성능 서버)
   ├── 안정성: ⭐⭐⭐
   ├── 속도: ⭐⭐⭐⭐⭐
   └── 서버 부하: 높음

현재 서버 상태: [CPU: 45%, 메모리: 60%]

선택: _
```

### **4단계: 카테고리 선택 (상품 전송/삭제 시)**
```
=== 카테고리별 상품 처리 ===
처리할 카테고리를 선택하세요:

1. 📂 전체 카테고리 (200-300개) - 순차 처리
2. 🎯 특정 카테고리 선택
   ├── 대분류: 의류 (50개 하위 카테고리)
   ├── 중분류: 여성의류 (20개 하위 카테고리)
   └── 소분류: 상의 (10개 하위 카테고리)

3. 📋 카테고리 목록 보기

선택: _
```

---

## 🎯 3개 핵심 코어 개발 계획

### **🚀 Core 1: 카테고리별 상품 전송 배치 시스템**

#### 📋 **기능 개요**
- 카테고리별로 상품을 검색하여 매칭되는 마켓계정으로 전송
- 검색된 상품이 없으면 스킵하고 다음 카테고리로 진행
- 모든 카테고리에서 반복 진행하는 완전 자동화 배치

#### 🔧 **핵심 로직**
```python
def core1_category_product_transfer_batch(owner_id):
    """Core 1: 카테고리별 상품 전송 배치"""
    
    accounts = get_accounts_by_owner(owner_id)
    categories = get_active_categories()
    
    for account in accounts:
        login_to_cafe24(account)
        
        for category in categories:
            # 1. 카테고리별 상품 검색
            products = search_products_by_category(account, category)
            
            if products:
                # 2. 매칭되는 마켓계정 선택
                target_markets = parse_target_markets(category)
                
                # 3. 상품 전송
                for market in target_markets:
                    market_account = get_market_account(account, market)
                    transfer_products_to_market(products, market_account)
                    
                log_success(account, category, len(products))
            else:
                # 4. 상품 없음 - 스킵
                log_skip(account, category, "상품 없음")
                continue
        
        logout_from_cafe24(account)
```

---

### **🗑️ Core 2: 적정 상품수 관리 및 자동 삭제 시스템**

#### 📋 **기능 개요**
- 상품 전송 전 기존 등록된 상품수 조사
- 적정상품수(엑셀에서 파싱) 초과 시 자동 삭제
- 마켓아이디별(20-30개) 순차적 검색 및 삭제

#### 🔧 **핵심 로직**
```python
def core2_product_quantity_management(owner_id):
    """Core 2: 적정 상품수 관리 및 자동 삭제"""
    
    owner_accounts = get_accounts_by_owner(owner_id)
    
    # 첫 번째 카페24 서버에 로그인
    primary_account = owner_accounts[0]
    login_to_cafe24(primary_account)
    
    # 마켓아이디별 상품수 조사 및 삭제
    market_ids = get_market_ids_by_account(primary_account)  # 평균 20-30개
    
    for market_id in market_ids:
        # 1. 현재 등록된 상품수 조사
        current_products = get_products_by_market_id(market_id, order_by="registration_date_asc")
        current_count = len(current_products)
        
        # 2. 적정상품수 파싱 (엑셀에서)
        optimal_count = get_optimal_product_count(market_id)
        max_allowed_count = get_max_allowed_count(market_id)
        
        # 3. 초과 상품 삭제 (등록일이 오래된 순서)
        if current_count > optimal_count:
            excess_count = current_count - optimal_count
            products_to_delete = current_products[:excess_count]
            
            for product in products_to_delete:
                delete_product_from_market(product, market_id)
                log_deletion(market_id, product)
            
            log_cleanup_summary(market_id, excess_count, optimal_count)
    
    logout_from_cafe24(primary_account)
    
    # 삭제 완료 후 카테고리별 상품전송 배치 실행
    core1_category_product_transfer_batch(owner_id)
```

#### 📊 **상품수 관리 엑셀 구조 추가**

**`product_limits` 시트 - 상품수 제한 정보**

| 컬럼명 | 타입 | 설명 | 예시 |
|--------|------|------|------|
| `market_id` | 문자열 | 마켓 아이디 | `11ST_001` |
| `account_id` | 문자열 | 연결된 계정 ID | `ACC001` |
| `max_allowed_count` | 숫자 | 최대 등록 가능 상품수 | `1000` |
| `optimal_count` | 숫자 | 적정 상품수 | `800` |
| `current_count` | 숫자 | 현재 등록된 상품수 | `950` |
| `auto_delete` | Y/N | 자동 삭제 활성화 | `Y` |
| `delete_strategy` | 문자열 | 삭제 전략 | `oldest_first` |

---

### **🔗 Core 3: 외부 마켓 직접 관리 시스템**

#### 📋 **기능 개요**
- 카페24 서버에 등록된 마켓에 직접 접속
- 상품 삭제 또는 그룹화 진행
- 퍼센티 기존 기능 활용하여 개발

#### 🔧 **핵심 로직**
```python
def core3_direct_market_management(owner_id, operation_type):
    """Core 3: 외부 마켓 직접 관리"""
    
    accounts = get_accounts_by_owner(owner_id)
    
    for account in accounts:
        # 1. 카페24에서 연결된 마켓 정보 수집
        connected_markets = get_connected_markets(account)
        
        for market_info in connected_markets:
            market_type = market_info['type']  # 11번가, 쿠팡, 옥션 등
            market_credentials = market_info['credentials']
            
            # 2. 외부 마켓에 직접 로그인
            market_driver = create_market_driver(market_type)
            login_to_external_market(market_driver, market_credentials)
            
            if operation_type == "delete":
                # 3-1. 상품 삭제 작업
                products_to_delete = get_products_for_deletion(market_info)
                for product in products_to_delete:
                    delete_product_from_external_market(market_driver, product)
                    
            elif operation_type == "group":
                # 3-2. 상품 그룹화 작업
                products_to_group = get_products_for_grouping(market_info)
                group_products_in_external_market(market_driver, products_to_group)
            
            # 4. 외부 마켓 로그아웃
            logout_from_external_market(market_driver)
            
            log_external_market_operation(market_info, operation_type)
```

#### 🎯 **지원 마켓 및 기능**

**지원 마켓**
- 11번가 (11ST)
- 쿠팡 (Coupang)
- 옥션 (Auction)
- 지마켓 (Gmarket)
- 인터파크 (Interpark)

**지원 기능**
- 상품 일괄 삭제
- 상품 카테고리별 그룹화
- 상품 정보 일괄 수정
- 재고 관리
- 가격 일괄 조정

---

## ⚙️ 통합 배치 처리 로직

### 🔄 **완전 자동화 워크플로우**
```python
def integrated_cafe24_automation(owner_id):
    """3개 코어 통합 자동화 워크플로우"""
    
    try:
        # Phase 1: 상품수 관리 및 정리
        print("🗑️ Phase 1: 적정 상품수 관리 시작...")
        core2_product_quantity_management(owner_id)
        
        # Phase 2: 카테고리별 상품 전송
        print("🚀 Phase 2: 카테고리별 상품 전송 시작...")
        core1_category_product_transfer_batch(owner_id)
        
        # Phase 3: 외부 마켓 직접 관리 (선택적)
        if should_run_external_management():
            print("🔗 Phase 3: 외부 마켓 직접 관리 시작...")
            core3_direct_market_management(owner_id, "group")
        
        print("✅ 모든 자동화 작업 완료!")
        
    except Exception as e:
        print(f"❌ 자동화 작업 중 오류 발생: {e}")
        handle_automation_error(e)
```

### 📦 **카테고리별 상품 처리 (Core 1 상세)**
```python
def process_category_products(account, category):
    """카테고리별 상품 전송/삭제"""
    
    # 1. 카테고리 정보 파싱
    large_cat = category['large_category']
    medium_cat = category['medium_category']
    small_cat = category['small_category']
    detail_cat = category['detail_category']
    
    # 2. 대상 마켓 파싱
    target_markets = category['target_markets'].split(',')
    
    # 3. 상품 검색
    products = search_products_by_category(account, category)
    
    if products:
        # 4. 마켓별 전송
        for market in target_markets:
            send_products_to_market(products, market)
    else:
        # 5. 상품 없음 - 스킵
        log_skip(account, category, "상품 없음")
```

---

## 🎛️ 시스템 설정

### **배치 실행 설정**
```json
{
    "execution_mode": "sequential",  // sequential | concurrent
    "max_concurrent_accounts": 5,
    "retry_attempts": 3,
    "timeout_seconds": 300,
    "error_handling": "continue"     // continue | stop
}
```

### **카테고리 처리 설정**
```json
{
    "category_processing": {
        "mode": "sequential",
        "skip_empty_categories": true,
        "max_products_per_batch": 100,
        "delay_between_categories": 2
    }
}
```

---

## 📊 모니터링 및 로깅

### **실시간 진행 상황**
```
=== 배치 작업 진행 상황 ===
사업자: 김사장 (5개 계정)
실행 모드: 순차 실행

[계정 1/5] 패션몰1 ✅ 완료 (50개 카테고리 처리)
[계정 2/5] 패션몰2 🔄 진행중 (23/45 카테고리)
[계정 3/5] 패션몰3 ⏳ 대기중
[계정 4/5] 패션몰4 ⏳ 대기중
[계정 5/5] 패션몰5 ⏳ 대기중

전체 진행률: 34% (예상 완료: 2시간 15분)
```

### **에러 처리 및 재시도**
```
=== 에러 발생 시 처리 ===
1. 계정별 에러 로그 기록
2. 실패한 카테고리 별도 큐에 추가
3. 배치 완료 후 재시도 옵션 제공
4. 텔레그램 알림 발송 (선택사항)
```

---

## 🚀 개발 우선순위 (3개 핵심 코어 기준)

### **Phase 1: 기본 구조 및 Core 1 개발 (1-2주)**
- [ ] 엑셀 파일 구조 생성 (`owners`, `accounts`, `categories`, `product_limits`)
- [ ] 사업자/계정 관리 클래스 개발
- [ ] 카페24 로그인 시스템 구축
- [ ] **Core 1: 카테고리별 상품 전송 배치 시스템**
  - [ ] 카테고리별 상품 검색 엔진
  - [ ] 마켓계정 매칭 로직
  - [ ] 상품 전송 자동화
  - [ ] 스킵 로직 (상품 없음 시)

### **Phase 2: Core 2 개발 (1주)**
- [ ] **Core 2: 적정 상품수 관리 및 자동 삭제 시스템**
  - [ ] 마켓아이디별 상품수 조사 기능
  - [ ] 적정상품수 엑셀 파싱 로직
  - [ ] 등록일 기준 상품 정렬 및 삭제
  - [ ] 상품수 관리 대시보드
- [ ] Core 1과 Core 2 통합 워크플로우
- [ ] 순차/동시 실행 엔진 최적화

### **Phase 3: Core 3 개발 및 통합 (1-2주)**
- [ ] **Core 3: 외부 마켓 직접 관리 시스템**
  - [ ] 외부 마켓 로그인 시스템 (11번가, 쿠팡, 옥션 등)
  - [ ] 상품 직접 삭제 기능
  - [ ] 상품 그룹화 기능
  - [ ] 퍼센티 기존 기능 통합
- [ ] 3개 코어 완전 통합 자동화
- [ ] 에러 처리 및 재시도 로직
- [ ] 모니터링 및 로깅 시스템

### **Phase 4: 고급 기능 및 최적화 (1주)**
- [ ] GUI 통합 및 사용자 인터페이스
- [ ] 실시간 모니터링 대시보드
- [ ] 텔레그램 알림 시스템
- [ ] 성능 최적화 및 안정성 강화

---

## 📊 3개 코어별 개발 복잡도 분석

### **🚀 Core 1: 카테고리별 상품 전송 배치**
- **복잡도**: ⭐⭐⭐⭐ (높음)
- **개발 기간**: 1-2주
- **핵심 기술**: 카테고리 파싱, 상품 검색, 마켓 매칭
- **의존성**: 기존 퍼센티 상품 전송 로직 활용

### **🗑️ Core 2: 적정 상품수 관리**
- **복잡도**: ⭐⭐⭐ (중간)
- **개발 기간**: 1주
- **핵심 기술**: 상품수 조사, 엑셀 파싱, 자동 삭제
- **의존성**: Core 1 완성 후 통합

### **🔗 Core 3: 외부 마켓 직접 관리**
- **복잡도**: ⭐⭐⭐⭐⭐ (매우 높음)
- **개발 기간**: 1-2주
- **핵심 기술**: 다중 마켓 로그인, 직접 조작
- **의존성**: 퍼센티 기존 마켓 관리 기능 확장

---

## 💡 핵심 설계 원칙

1. **🎯 중앙 관리**: 모든 작업은 중앙에서 통제
2. **⚡ 유연한 실행**: 서버 환경에 따른 실행 모드 선택
3. **📊 투명한 모니터링**: 실시간 진행 상황 확인
4. **🔄 안정적 처리**: 에러 발생 시 자동 복구
5. **📈 확장 가능**: 새로운 사업자/계정 쉽게 추가

---

## 🎉 3개 핵심 코어 완성 시 예상 효과

### **🚀 Core 1 효과: 카테고리별 상품 전송 자동화**
- **효율성 향상**: 수동 카테고리 선택 → 완전 자동화로 **95% 시간 단축**
- **정확성 보장**: 매칭 로직으로 **오전송 위험 제거**
- **확장성**: 새로운 카테고리 추가 시 **즉시 적용**
- **안정성**: 상품 없음 시 자동 스킵으로 **무한 대기 방지**

### **🗑️ Core 2 효과: 적정 상품수 관리**
- **계정 안전성**: 상품수 초과로 인한 **계정 제재 방지**
- **최적화**: 마켓별 적정 상품수 유지로 **노출 효율 극대화**
- **자동화**: 20-30개 마켓아이디 **일괄 관리**
- **예방**: 사전 정리로 **전송 실패율 90% 감소**

### **🔗 Core 3 효과: 외부 마켓 직접 관리**
- **완전 통제**: 카페24 + 외부 마켓 **통합 관리**
- **유연성**: 상품 삭제/그룹화 **직접 제어**
- **확장성**: 5개 주요 마켓 **동시 관리**
- **독립성**: 카페24 의존도 **50% 감소**

### **🏆 통합 시스템 전체 효과**
- **관리 효율성**: 100개 계정 → 15-20개 그룹으로 **관리 복잡도 80% 감소**
- **처리 속도**: 3개 코어 통합으로 **전체 작업 시간 90% 단축**
- **안정성**: 단계별 검증으로 **오류율 95% 감소**
- **확장성**: 모듈화 설계로 **새로운 기능 쉽게 추가**
- **ROI**: 개발 투자 대비 **6개월 내 회수 예상**

---

## 💡 핵심 설계 원칙 (3개 코어 기준)

1. **🎯 단계별 완성**: Core 1 → Core 2 → Core 3 순차 개발
2. **🔄 통합 자동화**: 3개 코어가 하나의 워크플로우로 동작
3. **📊 데이터 중심**: 모든 설정과 제한은 엑셀에서 관리
4. **⚡ 유연한 실행**: 개별 코어 실행 또는 통합 실행 선택 가능
5. **🛡️ 안전 우선**: 각 단계별 검증 및 롤백 기능
6. **📈 확장 가능**: 새로운 마켓/기능 추가 시 기존 구조 재사용

---

## 🎯 최종 목표 달성 지표

### **정량적 지표**
- **계정 관리 효율**: 100개 → 20개 그룹 (80% 감소)
- **작업 시간**: 수동 8시간 → 자동 30분 (94% 단축)
- **오류율**: 수동 20% → 자동 1% (95% 감소)
- **상품 처리량**: 시간당 50개 → 500개 (10배 증가)

### **정성적 지표**
- **사용자 만족도**: 복잡한 수동 작업 → 원클릭 자동화
- **시스템 안정성**: 예측 가능한 동작 및 에러 처리
- **유지보수성**: 모듈화된 구조로 쉬운 수정/확장
- **비즈니스 확장성**: 새로운 사업자/계정 쉽게 추가

이 3개 핵심 코어 설계로 카페24 관리 시스템을 완성하시면, 효율적이고 안정적인 대규모 계정 관리가 가능할 것입니다! 🚀