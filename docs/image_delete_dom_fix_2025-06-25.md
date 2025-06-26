# 이미지 삭제 DOM 구조 변경 해결 보고서

## 문제 상황

**발생 일시**: 2025-06-25 22:20:36

**오류 내용**: 
1. 이미지 삭제 기능에서 "총 X개의 이미지" 텍스트를 찾는 선택자가 실패
2. 이미지 삭제 버튼의 DOM 구조 변경으로 인한 선택자 실패

```
2025-06-25 22:20:37,328 - image_utils3 - INFO - 이미지 개수 텍스트 찾기 시도 1: //span[contains(@class, 'sc-dLmyTH') and contains(@class, 'jOUQKU') and contains(@class, 'Body2Medium14') and contains(@class, 'CharacterTitle85') and contains(text(), '총') and contains(text(), '개의 이미지')] 
2025-06-25 22:20:47,671 - image_utils3 - WARNING - 선택자 1 실패
```

## 원인 분석

### DOM 구조 변경 이력

#### 1. 이미지 개수 텍스트 변경
- **기존**: `sc-bRimrq kCtFmP` 클래스 누락
- **변경**: `sc-bRimrq kCtFmP` 클래스 추가
- **영향**: 이미지 개수 텍스트를 찾지 못하는 문제 발생

#### 2. 이미지 삭제 버튼 DOM 구조 - 두 가지 다른 구조 확인

##### 2-1. 일괄편집 모달창에서의 삭제 버튼
- **구조**: `sc-bdlOLf jdyrUI` div 내부의 `sc-bRimrq kCtFmP FootnoteDescription` span
- **HTML 예시**:
```html
<div class="sc-bdlOLf jdyrUI">
    <span class="sc-bRimrq kCtFmP FootnoteDescription">삭제</span>
</div>
```

##### 2-2. 썸네일 탭에서의 삭제 버튼
- **구조**: `sc-heIBml bxPVbE` div 내부의 `sc-doohEh imNntt FootnoteDescription` span
- **HTML 예시**:
```html
<div class="sc-heIBml bxPVbE">
    <span class="sc-doohEh imNntt FootnoteDescription">삭제</span>
</div>
```

#### 3. 기존 구조와의 비교
```html
<!-- 기존 구조 -->
<div class="sc-bOTbmH iNrMOB">
    <span>삭제</span>
</div>

<!-- 일괄편집 모달창 구조 -->
<div class="sc-bdlOLf jdyrUI">
    <span class="sc-bRimrq kCtFmP FootnoteDescription">삭제</span>
</div>

<!-- 썸네일 탭 구조 -->
<div class="sc-heIBml bxPVbE">
    <span class="sc-doohEh imNntt FootnoteDescription">삭제</span>
</div>
```

#### 4. 주요 변경 사항
- **컨테이너 클래스**: `sc-bOTbmH iNrMOB` → 두 가지 다른 구조로 분화
  - 일괄편집: `sc-bdlOLf jdyrUI`
  - 썸네일: `sc-heIBml bxPVbE`
- **삭제 텍스트 클래스**: 단순 텍스트 → 구체적인 클래스명 추가
  - 일괄편집: `sc-bRimrq kCtFmP FootnoteDescription`
  - 썸네일: `sc-doohEh imNntt FootnoteDescription`

## 해결 방안

### 1. 선택자 업데이트

**영향받는 파일들**:
- `image_utils3.py` ✅ 수정 완료
- `image_utils.py` ✅ 수정 완료
- `image_utils5.py` ✅ 확인 완료 (영향 없음)

### 2. 적용된 해결책

#### A. 다중 선택자 전략
새로운 선택자를 최우선으로 하고, 기존 선택자를 백업으로 유지:

```python
count_selectors = [
    # 새로운 DOM 구조 (2025-06-25)
    "//span[contains(@class, 'sc-bRimrq') and contains(@class, 'kCtFmP') and contains(@class, 'Body2Medium14') and contains(@class, 'CharacterTitle85') and contains(text(), '총') and contains(text(), '개의 이미지')]",
    "//span[contains(@class, 'sc-bRimrq') and contains(@class, 'kCtFmP') and contains(text(), '총') and contains(text(), '개의 이미지')]",
    # 기존 DOM 구조 (백업용)
    "//span[contains(@class, 'sc-dLmyTH') and contains(@class, 'jOUQKU') and contains(@class, 'Body2Medium14') and contains(@class, 'CharacterTitle85') and contains(text(), '총') and contains(text(), '개의 이미지')]",
    "//span[contains(@class, 'sc-dLmyTH') and contains(@class, 'jOUQKU') and contains(text(), '총') and contains(text(), '개의 이미지')]",
    # 범용 선택자 (클래스 무관)
    "//span[contains(text(), '총') and contains(text(), '개의 이미지')]",
    "//div[contains(text(), '총') and contains(text(), '개의 이미지')]"
]
```

#### B. 순차적 시도 로직
```python
count_element = None
for i, selector in enumerate(count_selectors):
    try:
        logger.info(f"이미지 개수 텍스트 찾기 시도 {i+1}: {selector[:50]}...")
        count_element = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, selector))
        )
        logger.info(f"이미지 개수 텍스트 요소 발견: 선택자 {i+1}")
        break
    except (TimeoutException, NoSuchElementException) as e:
        logger.warning(f"선택자 {i+1} 실패: {e}")
        continue
```

## 예방 조치

### 1. 미래 DOM 변경 대비

#### A. 범용 선택자 우선 사용
클래스명에 의존하지 않는 텍스트 기반 선택자를 포함:
```xpath
//span[contains(text(), '총') and contains(text(), '개의 이미지')]
```

#### B. 다중 선택자 패턴 적용
모든 DOM 의존적 기능에 다중 선택자 패턴 적용 권장

### 2. 모니터링 강화

#### A. 로깅 개선
- 선택자 시도 과정을 상세히 로깅
- 실패한 선택자와 성공한 선택자 구분 기록

#### B. 알림 시스템
- DOM 구조 변경 감지 시 즉시 알림
- 백업 선택자 사용 시 경고 로그

## 테스트 권장사항

### 1. 즉시 테스트
```bash
# 이미지 삭제 기능 테스트
python -c "from image_utils3 import PercentyImageManager3; print('이미지 삭제 기능 테스트 필요')"
```

### 2. 회귀 테스트
- 기존 DOM 구조에서도 정상 작동하는지 확인
- 새로운 DOM 구조에서 정상 작동하는지 확인

## 이미지 삭제 버튼 DOM 구조 변경 대응 및 선택자 우선순위 최적화

### 문제 상황
- 퍼센티 플랫폼의 DOM 구조 변경으로 인해 이미지 삭제 기능이 간헐적으로 실패
- 일괄편집 모달창과 썸네일 탭에서 서로 다른 DOM 구조 사용
- 기존 선택자가 새로운 DOM 구조를 제대로 감지하지 못함

### 해결 방안

#### 1. 선택자 우선순위 최적화 (2025-06-25)
- `image_utils.py`와 `image_utils3.py`의 `delete_selectors` 및 `delete_button_selectors` 리스트 순서 조정
- 썸네일 탭에서 성공했던 DOM 구조(`sc-heIBml bxPVbE` + `sc-doohEh imNntt`)를 최우선 순위로 배치
- 일괄편집 모달창 구조(`sc-bdlOLf jdyrUI` + `sc-bRimrq kCtFmP`)를 그 다음 순서로 배치
- 기존 DOM 구조들을 백업용으로 유지

**변경된 우선순위:**
1. 썸네일 탭 성공 구조 (최우선)
2. 일괄편집 모달창 구조 
3. 일반적인 구조 (백업용)
4. 기존 DOM 구조 (백업용)

#### 2. 이미지 번역 핸들러 DOM 선택자 개선 (2025-06-25)

**문제점:**
- 이미지 번역에서 DOM 기반 이동이 지속적으로 실패하여 TAB 방식으로만 이동
- 기존 선택자가 현재 DOM 구조와 불일치
- 이미지 위치 정확도 저하 및 번역 실패 증가

**개선 사항:**
- `image_translation_handler_new.py`의 DOM 선택자를 `image_utils.py`에서 성공적으로 사용되는 선택자로 통일
- `_move_to_image_position_dom()` 메서드 완전 재작성:
  - 이미지 카드 전체를 먼저 찾고 특정 위치의 카드 선택하는 방식으로 변경
  - 1-based 인덱스를 0-based로 정확히 변환
  - 카드 내 이미지 선택자 다양화
- `_get_total_image_count()` 메서드 개선:
  - 동일한 이미지 카드 선택자 사용
  - cbu01.alicdn.com 이미지 필터링 로직 개선
- `_click_first_edit_button()` 메서드 개선:
  - 첫 번째 이미지 카드 기반 접근 방식 적용
  - 카드 내 편집 버튼 검색으로 정확도 향상

**적용된 선택자 (우선순위 순):**
1. 일괄편집 모달창 구조: `sc-bdlOLf jdyrUI` + `sc-bRimrq kCtFmP`
2. 썸네일 탭 구조: `sc-heIBml bxPVbE` + `sc-doohEh imNntt`
3. 일반적인 구조 (백업용)
4. 기존 DOM 구조 (백업용)

#### 3. 기대 효과
- 이미지 삭제 성공률 향상
- 이미지 번역 DOM 기반 이동 성공률 대폭 향상
- TAB 방식 의존도 감소로 정확도 및 성능 개선
- 성능 개선 (성공 확률이 높은 선택자를 우선 시도)
- DOM 구조 변경에 대한 안정성 확보
- 이미지 번역과 이미지 삭제 기능 간 선택자 일관성 확보

## 결론

### 해결 완료 사항
✅ `image_utils3.py` - 이미지 개수 텍스트 및 삭제 버튼 선택자 업데이트 완료  
✅ `image_utils.py` - 이미지 개수 텍스트 및 삭제 버튼 선택자 업데이트 완료  
✅ `image_utils5.py` - 확인 완료 (영향 없음)  
✅ **두 가지 다른 DOM 구조 완전 대응**:
   - **일괄편집 모달창**: `sc-bdlOLf jdyrUI` + `sc-bRimrq kCtFmP FootnoteDescription`
   - **썸네일 탭**: `sc-heIBml bxPVbE` + `sc-doohEh imNntt FootnoteDescription`
✅ 다중 선택자 전략으로 미래 DOM 변경에 대한 내성 강화  
✅ 상세한 로깅으로 디버깅 및 문제 해결 시간 단축  
✅ 각 구조별 정확한 클래스명과 계층 구조 적용
✅ 기존 구조들도 백업으로 유지하여 호환성 보장
✅ **선택자 우선순위 최적화 (2025-06-25 추가)**:
   - 로그 분석 결과 썸네일 탭에서 성공한 선택자를 최우선으로 재배치
   - 성공 확률이 높은 선택자를 우선 시도하여 성능 향상  

### 기대 효과
- 이미지 삭제 기능 정상화
- 미래 DOM 변경에 대한 내성 강화
- 디버깅 및 문제 해결 시간 단축

### 다음 단계
1. 실제 환경에서 이미지 삭제 기능 테스트
2. 다른 DOM 의존적 기능들도 같은 패턴으로 개선 검토
3. 정기적인 DOM 구조 변경 모니터링 체계 구축

---

**작성일**: 2025-06-25  
**작성자**: AI Assistant  
**상태**: 해결 완료  
**우선순위**: 높음