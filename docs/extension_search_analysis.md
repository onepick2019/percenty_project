# 퍼센티 확장 프로그램 검색 문제 분석 및 해결 방안

## 📊 현재 상황 분석

### 테스트 결과 요약
- **테스트 일시**: 2025-06-24 09:47:25 ~ 09:48:52
- **총 검색 시간**: 70.1초 (2회 시도)
- **결과**: 퍼센티 확장 프로그램 미발견
- **Chrome 버전**: 137.0.0.0

### 🔍 상세 분석

#### 1. 확장 프로그램 로딩 상태
```
✅ 확장 프로그램 경로 설정: c:\Projects\percenty_project\percenty_extension
✅ Chrome 옵션에 --load-extension 추가됨
✅ Chrome 드라이버 생성 성공
✅ chrome://extensions/ 페이지 접근 성공
```

#### 2. Shadow DOM 구조 분석
```
✅ extensions-manager shadowRoot 접근 성공
✅ 중첩 shadowRoot 요소들 발견:
   - EXTENSIONS-DROP-OVERLAY
   - EXTENSIONS-TOOLBAR  
   - EXTENSIONS-SIDEBAR
   - CR-VIEW-MANAGER
   - EXTENSIONS-ITEM-LIST ⭐ (핵심 요소)
   - CR-LAZY-RENDER-LIT (6개)
   - CR-TOAST-MANAGER
```

#### 3. 검색 전략별 결과

| 전략 | 결과 | 상세 |
|------|------|------|
| Enhanced Shadow DOM | ❌ 실패 | 모든 선택자에서 0개 발견 |
| Chrome API | ⚠️ 타임아웃 | 30초 후 script timeout 발생 |
| Original Shadow DOM | ❌ 실패 | Shadow DOM에서 0개 확장프로그램 |
| DOM Text Search | ❌ 실패 | 퍼센티 관련 텍스트 없음 |
| Element Attribute | ❌ 실패 | 속성에서 퍼센티 관련 내용 없음 |

## 🚨 핵심 문제점

### 1. CR-LAZY-RENDER-LIT 지연 렌더링
- **문제**: Chrome 확장 프로그램 페이지가 지연 렌더링(Lazy Rendering) 사용
- **영향**: 확장 프로그램 목록이 즉시 DOM에 로드되지 않음
- **증거**: 6개의 CR-LAZY-RENDER-LIT 요소 발견

### 2. EXTENSIONS-ITEM-LIST 내부 구조
- **문제**: 실제 확장 프로그램이 EXTENSIONS-ITEM-LIST 내부에 있을 가능성
- **현재 검색**: 최상위 shadowRoot만 검색
- **필요**: 중첩된 shadowRoot 내부까지 재귀적 검색

### 3. Chrome Management API 제한
- **문제**: chrome://extensions/ 페이지에서 Management API 접근 제한
- **증거**: 30초 타임아웃 발생
- **원인**: 보안 정책으로 인한 API 접근 제한

## 💡 해결 방안

### 1. 지연 렌더링 대응 전략

```python
def _wait_for_lazy_rendering(self, max_wait=30):
    """
    CR-LAZY-RENDER-LIT 요소들이 완전히 렌더링될 때까지 대기
    """
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        # 지연 렌더링 상태 확인
        lazy_elements = self.driver.execute_script("""
            const lazyElements = document.querySelectorAll('cr-lazy-render-lit');
            return Array.from(lazyElements).map(el => ({
                rendered: el.shadowRoot !== null,
                hasContent: el.shadowRoot && el.shadowRoot.children.length > 0
            }));
        """)
        
        # 모든 지연 요소가 렌더링되었는지 확인
        all_rendered = all(elem['rendered'] and elem['hasContent'] for elem in lazy_elements)
        
        if all_rendered:
            logger.info("✅ 모든 지연 렌더링 요소 로드 완료")
            return True
            
        time.sleep(1)
    
    logger.warning("⚠️ 지연 렌더링 대기 시간 초과")
    return False
```

### 2. 재귀적 Shadow DOM 검색

```python
def _recursive_shadow_dom_search(self, root_element, depth=0, max_depth=5):
    """
    Shadow DOM을 재귀적으로 검색하여 확장 프로그램 찾기
    """
    if depth > max_depth:
        return False, []
    
    found_extensions = []
    
    try:
        # 현재 레벨에서 확장 프로그램 검색
        extensions = root_element.querySelectorAll('extensions-item, .extension-item');
        
        for ext in extensions:
            # 확장 프로그램 정보 추출
            name = self._extract_extension_name(ext)
            if name and ('퍼센티' in name or 'Percenty' in name.lower()):
                return True, [{'name': name, 'depth': depth}]
            found_extensions.append({'name': name, 'depth': depth})
        
        # 하위 Shadow DOM 재귀 검색
        shadow_elements = root_element.querySelectorAll('*');
        for element in shadow_elements:
            if element.shadowRoot:
                found, sub_extensions = self._recursive_shadow_dom_search(
                    element.shadowRoot, depth + 1, max_depth
                )
                if found:
                    return True, sub_extensions
                found_extensions.extend(sub_extensions)
        
        return False, found_extensions
        
    except Exception as e:
        logger.error(f"재귀 검색 오류 (depth {depth}): {e}")
        return False, []
```

### 3. 확장 프로그램 강제 활성화

```python
def _force_extension_visibility(self):
    """
    확장 프로그램 목록을 강제로 활성화/표시
    """
    try:
        # 개발자 모드 토글 (확장 프로그램 새로고침 효과)
        self.driver.execute_script("""
            const extensionsManager = document.querySelector('extensions-manager');
            if (extensionsManager && extensionsManager.shadowRoot) {
                const toolbar = extensionsManager.shadowRoot.querySelector('extensions-toolbar');
                if (toolbar && toolbar.shadowRoot) {
                    const devModeToggle = toolbar.shadowRoot.querySelector('#devMode');
                    if (devModeToggle) {
                        // 토글을 두 번 클릭하여 새로고침 효과
                        devModeToggle.click();
                        setTimeout(() => devModeToggle.click(), 500);
                    }
                }
            }
        """)
        
        time.sleep(2)
        
        # 확장 프로그램 목록 강제 새로고침
        self.driver.execute_script("""
            const itemList = document.querySelector('extensions-item-list');
            if (itemList && itemList.shadowRoot) {
                // 목록 새로고침 트리거
                const event = new CustomEvent('refresh-extensions');
                itemList.dispatchEvent(event);
            }
        """)
        
        time.sleep(3)
        return True
        
    except Exception as e:
        logger.error(f"강제 활성화 오류: {e}")
        return False
```

### 4. 확장 프로그램 ID 기반 검색

```python
def _search_by_extension_id(self):
    """
    확장 프로그램 ID를 통한 직접 검색
    """
    try:
        # 로드된 확장 프로그램 경로에서 manifest.json 읽기
        manifest_path = os.path.join(PERCENTY_EXTENSION_PATH, 'manifest.json')
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
                extension_name = manifest.get('name', '')
                
            # manifest에서 추출한 이름으로 검색
            if extension_name:
                logger.info(f"Manifest에서 확장 프로그램 이름 확인: {extension_name}")
                return self._search_by_exact_name(extension_name)
        
        return False
        
    except Exception as e:
        logger.error(f"확장 프로그램 ID 검색 오류: {e}")
        return False
```

## 🎯 권장 구현 순서

1. **지연 렌더링 대기 로직 추가**
   - CR-LAZY-RENDER-LIT 완전 로딩 대기
   - 렌더링 상태 모니터링

2. **재귀적 Shadow DOM 검색 구현**
   - 중첩된 shadowRoot 탐색
   - EXTENSIONS-ITEM-LIST 내부 검색

3. **확장 프로그램 강제 활성화**
   - 개발자 모드 토글을 통한 새로고침
   - 목록 강제 업데이트

4. **Manifest 기반 검색 추가**
   - 정확한 확장 프로그램 이름 확인
   - ID 기반 직접 검색

5. **포괄적인 대기 전략**
   - 적응형 대기 시간 조정
   - 단계별 검증 로직

## 📈 예상 개선 효과

- **검색 성공률**: 현재 0% → 예상 85%+
- **검색 시간**: 현재 70초 → 예상 15-30초
- **안정성**: 지연 렌더링 및 중첩 구조 대응
- **디버깅**: 상세한 단계별 로깅

## 🔧 다음 단계

1. 개선된 검색 로직을 기존 `product_editor_core6_1_dynamic.py`에 통합
2. 단계별 테스트 및 검증
3. 성능 최적화 및 안정성 개선
4. 문서화 및 사용자 가이드 업데이트

---

**작성일**: 2025-06-24  
**분석 대상**: ProductEditorCore6_1Enhanced 테스트 결과  
**다음 업데이트**: 개선 로직 구현 후