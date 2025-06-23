# 모달창 문제 정확한 분석 - 스마트스토어 연결끊기 버튼 클릭 실패

## 로그 재분석 결과

### 실제 진행 과정

**1. 쿠팡 처리 (정상 완료)**
```
16:14:50,923 - API 연결 끊기 버튼 클릭 완료
16:14:52,964 - API 연결 끊기 모달창 확인
16:14:52,989 - 에러 알림: API 연결 끊기 시 해당 마켓의 API 연동이 제거됩니다.
16:14:52,990 - 경고 알림: API 연결을 끊어도 기존에 업로드된 상품에 영향이 가지 않습니다.
16:14:52,990 - 모달창 확인 버튼 찾기 시도 1/3
16:14:53,041 - API 연결 끊기 모달창 확인 버튼 클릭 완료
```
✅ **쿠팡 모달창 정상 처리 및 닫힘**

**2. 스마트스토어 탭 전환 (정상 완료)**
```
16:14:55,042 - smartstore API 연결 끊기 시도
16:14:55,152 - 스마트스토어 탭 클릭 완료
16:14:58,218 - 스마트스토어 패널 로드 완료
```
✅ **스마트스토어 탭 정상 전환**

**3. 스마트스토어 API 연결 끊기 버튼 클릭 (정상 완료)**
```
16:14:58,227 - API 연결 끊기 버튼 찾기 시도 1/3
16:14:58,316 - API 연결 끊기 버튼 클릭 완료
```
✅ **스마트스토어 API 연결 끊기 버튼 정상 클릭**

**4. 스마트스토어 모달창 대기 (실패)**
```
16:15:02,481 - ERROR - API 연결 끊기 모달창 대기 시간 초과
```
❌ **스마트스토어 모달창이 열리지 않음 또는 선택자 문제**

## 실제 문제 진단

### 문제 1: 스마트스토어 모달창이 열리지 않음
**가능한 원인:**
- 스마트스토어 API 연결 끊기 버튼 클릭 후 모달창이 실제로 생성되지 않음
- 네트워크 지연으로 인한 모달창 생성 지연
- 스마트스토어 특유의 UI 동작 방식

### 문제 2: 모달창 선택자 불일치
**가능한 원인:**
- 스마트스토어 모달창의 DOM 구조가 쿠팡과 다름
- 모달창 제목이 다름 ("API 연결 끊기" vs 다른 텍스트)
- 모달창 클래스명이 다름

### 문제 3: 모달창 내 버튼 구조 차이
**가능한 원인:**
- 스마트스토어 모달창의 확인 버튼 클래스가 다름
- 버튼 텍스트가 다름 ("API 연결 끊기" vs "확인" vs "연결 해제")
- 버튼 구조 자체가 다름

## 해결 방안

### 1. 즉시 적용 - 디버깅 강화

**A. 스마트스토어 전용 디버깅 추가**
```python
def disconnect_smartstore_api(self):
    """스마트스토어 API 연결을 끊습니다."""
    try:
        # 1. 스마트스토어 탭으로 전환
        if not self.switch_to_market('smartstore'):
            return False
        
        # 2. 패널 로드 대기
        if not self.wait_for_market_panel_load('smartstore'):
            return False
        
        # 3. API 연결 끊기 버튼 클릭
        if not self.click_api_disconnect_button():
            return False
        
        # 4. 스마트스토어 전용 모달창 처리
        return self.handle_smartstore_api_disconnect_modal()
        
    except Exception as e:
        self.logger.error(f"스마트스토어 API 연결 끊기 중 오류: {e}")
        return False

def handle_smartstore_api_disconnect_modal(self):
    """스마트스토어 전용 API 연결 끊기 모달창 처리"""
    try:
        self.logger.info("스마트스토어 모달창 대기 시작")
        
        # 더 긴 대기 시간으로 모달창 대기
        time.sleep(2)  # 스마트스토어 모달창 생성 대기
        
        # 모든 가능한 모달창 선택자 시도
        modal_selectors = [
            "//div[@class='ant-modal-content']//div[@class='ant-modal-title' and text()='API 연결 끊기']",
            "//div[@class='ant-modal-content']//div[@class='ant-modal-title' and contains(text(), '연결')]",
            "//div[@class='ant-modal-content']//div[@class='ant-modal-title' and contains(text(), 'API')]",
            "//div[contains(@class, 'ant-modal')]//div[contains(text(), 'API')]",
            "//div[contains(@class, 'modal')]//div[contains(text(), '연결')]"
        ]
        
        modal_found = False
        for i, selector in enumerate(modal_selectors):
            try:
                self.logger.info(f"스마트스토어 모달창 선택자 {i+1}/{len(modal_selectors)} 시도")
                modal_element = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                self.logger.info(f"스마트스토어 모달창 발견 (선택자 {i+1})")
                modal_found = True
                break
            except TimeoutException:
                continue
        
        if not modal_found:
            self.logger.error("스마트스토어 모달창을 찾을 수 없음 - 전체 페이지 디버깅 시작")
            self.debug_smartstore_page_state()
            return False
        
        # 스마트스토어 전용 확인 버튼 클릭
        return self.click_smartstore_modal_confirm_button()
        
    except Exception as e:
        self.logger.error(f"스마트스토어 모달창 처리 중 오류: {e}")
        return False

def debug_smartstore_page_state(self):
    """스마트스토어 페이지 상태 전체 디버깅"""
    try:
        self.logger.info("=== 스마트스토어 페이지 상태 디버깅 시작 ===")
        
        # 1. 현재 활성 탭 확인
        active_tab = self.get_active_market_tab()
        self.logger.info(f"현재 활성 탭: {active_tab}")
        
        # 2. 모든 모달창 찾기
        all_modals = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'modal')]")
        self.logger.info(f"페이지 내 모든 모달창 개수: {len(all_modals)}")
        
        for i, modal in enumerate(all_modals):
            if modal.is_displayed():
                modal_html = modal.get_attribute('outerHTML')[:500]
                self.logger.info(f"표시된 모달창 {i+1}: {modal_html}")
        
        # 3. 스마트스토어 패널 내 모든 버튼 찾기
        ss_panel = self.driver.find_element(By.CSS_SELECTOR, "div[id='rc-tabs-0-panel-ss']")
        panel_buttons = ss_panel.find_elements(By.TAG_NAME, "button")
        self.logger.info(f"스마트스토어 패널 내 버튼 개수: {len(panel_buttons)}")
        
        for i, button in enumerate(panel_buttons):
            try:
                text = button.text.strip()
                is_displayed = button.is_displayed()
                self.logger.info(f"패널 버튼 {i+1}: '{text}' (표시: {is_displayed})")
            except Exception:
                continue
        
        # 4. 페이지 전체 HTML에서 'API' 또는 '연결' 포함 요소 찾기
        api_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'API') or contains(text(), '연결')]")
        self.logger.info(f"'API' 또는 '연결' 포함 요소 개수: {len(api_elements)}")
        
        for i, element in enumerate(api_elements[:10]):  # 최대 10개만
            try:
                text = element.text.strip()
                tag = element.tag_name
                self.logger.info(f"관련 요소 {i+1}: <{tag}> '{text}'")
            except Exception:
                continue
        
        self.logger.info("=== 스마트스토어 페이지 상태 디버깅 완료 ===")
        
    except Exception as e:
        self.logger.error(f"스마트스토어 페이지 디버깅 중 오류: {e}")

def click_smartstore_modal_confirm_button(self):
    """스마트스토어 모달창 확인 버튼 클릭"""
    try:
        # 스마트스토어 전용 버튼 선택자들
        button_selectors = [
            # 기본 패턴
            "//button[contains(@class, 'ant-btn-primary') and contains(@class, 'ant-btn-dangerous')]//span[text()='API 연결 끊기']",
            "//button[contains(@class, 'ant-btn-dangerous')]//span[text()='API 연결 끊기']",
            
            # 스마트스토어 특화 패턴
            "//button[contains(@class, 'ant-btn-primary')]//span[text()='확인']",
            "//button[contains(@class, 'ant-btn-primary')]//span[text()='연결 해제']",
            "//button[contains(@class, 'ant-btn-primary')]//span[contains(text(), '연결')]",
            
            # 일반적인 확인 버튼
            "//button//span[text()='확인']",
            "//button[contains(@class, 'ant-btn')]//span[text()='확인']",
            
            # 최후 수단
            "//div[contains(@class, 'ant-modal')]//button[contains(@class, 'ant-btn-primary')]"
        ]
        
        for i, selector in enumerate(button_selectors):
            try:
                self.logger.info(f"스마트스토어 확인 버튼 선택자 {i+1}/{len(button_selectors)} 시도")
                element = WebDriverWait(self.driver, 2).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                
                # 버튼 정보 로깅
                button_text = element.text.strip()
                button_class = element.get_attribute('class')
                self.logger.info(f"스마트스토어 확인 버튼 발견: '{button_text}' (클래스: {button_class})")
                
                element.click()
                self.logger.info("스마트스토어 모달창 확인 버튼 클릭 완료")
                time.sleep(1)
                return True
                
            except TimeoutException:
                self.logger.warning(f"스마트스토어 확인 버튼 선택자 {i+1} 실패")
                continue
            except Exception as e:
                self.logger.warning(f"스마트스토어 확인 버튼 선택자 {i+1} 오류: {e}")
                continue
        
        # 모든 선택자 실패 시 모달창 전체 디버깅
        self.logger.error("스마트스토어 모든 확인 버튼 선택자 실패 - 모달창 디버깅")
        self.debug_api_disconnect_modal()
        return False
        
    except Exception as e:
        self.logger.error(f"스마트스토어 확인 버튼 클릭 중 전체 오류: {e}")
        return False
```

### 2. 마켓별 독립 처리 구조

**각 마켓별 완전 독립적인 처리:**
```python
# 쿠팡 전용
def disconnect_coupang_api(self):
    return self.handle_coupang_disconnect_workflow()

# 스마트스토어 전용  
def disconnect_smartstore_api(self):
    return self.handle_smartstore_disconnect_workflow()

# 옥션/G마켓 전용
def disconnect_auction_gmarket_api(self):
    return self.handle_auction_gmarket_disconnect_workflow()
```

## 결론

**실제 문제:**
1. ✅ 쿠팡 모달창 정상 처리
2. ✅ 스마트스토어 탭 정상 전환
3. ✅ 스마트스토어 API 연결 끊기 버튼 정상 클릭
4. ❌ **스마트스토어 모달창 대기 실패** (4초 타임아웃)

**해결 방향:**
- 스마트스토어 모달창 생성 지연 대응 (더 긴 대기 시간)
- 스마트스토어 전용 모달창 선택자 추가
- 스마트스토어 전용 확인 버튼 선택자 추가
- 각 마켓별 완전 독립적인 처리 구조 구축

이전 분석에서 "쿠팡 모달창 잔존"이라고 잘못 진단했던 것을 정정하며, 실제로는 스마트스토어 모달창 처리 로직의 문제임을 확인했습니다.