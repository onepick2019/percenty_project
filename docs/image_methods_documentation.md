# Image Utils3 메서드 정의 문서

이 문서는 `image_utils3.py`에 정의된 5개의 주요 이미지 처리 메서드들의 구현 내용을 정리한 것입니다.
3단계 코딩 과정에서 오류 발생 시 빠른 디버깅을 위한 참고 자료로 활용됩니다.

## 1. Copy Option Image 메서드들

### 핵심 메서드: `copy_option_images_to_thumbnail`
- **목적**: 옵션 이미지를 썸네일로 복사 (스마트 복사 기능)
- **파라미터**: `target_count` (2 또는 4)
- **특징**: 
  - 옵션 이미지가 부족한 경우 기존 이미지를 중복 클릭하여 목표 개수 달성
  - DOM 선택자: `//button[contains(@class, 'ant-btn') and .//span[text()='썸네일로 복사']]`
  - 최대 대기 시간: 10초

### 래퍼 메서드들
- **`copy_first_two_option_images`**: 2개 썸네일 생성
- **`copy_first_four_option_images`**: 4개 썸네일 생성
- 각 메서드는 옵션 탭 선택 후 `copy_option_images_to_thumbnail` 호출

### 이벤트 처리: `process_copy_option_image_events`
- **파라미터**: `copy_type` ('first_two' 또는 'first_four')
- **검증**: 빈 값 체크 및 지원되는 타입 확인
- **에러 처리**: 상세한 로깅 및 예외 처리

## 2. Delete Image 메서드들

### 핵심 메서드들
- **`delete_image_by_index`**: 특정 인덱스의 이미지 삭제
- **`delete_first_n_images`**: 앞에서부터 N개 이미지 삭제
- **`delete_last_n_images`**: 뒤에서부터 N개 이미지 삭제

### 공통 특징
- 상세페이지 탭 선택 필요
- 일괄편집 모달창 열기 필요
- DOM 선택자: `//button[contains(@class, 'ant-btn-dangerous')]` (삭제 버튼)
- 삭제 후 인덱스 변경 고려

### 이벤트 처리: `process_delete_image_events`
- **파라미터**: `events` (삭제 정보 리스트)
- **지원 타입**: 
  - `delete_by_index`: 특정 인덱스 삭제
  - `delete_first_n`: 앞에서 N개 삭제
  - `delete_last_n`: 뒤에서 N개 삭제

## 3. Delete Thumbnail 메서드들

### 핵심 메서드들
- **`delete_thumbnail_by_position`**: 특정 위치의 썸네일 삭제
- **`delete_thumbnails_by_positions`**: 여러 위치의 썸네일 삭제

### 주요 특징
- **최대 삭제 제한**: 5개까지만 삭제 가능
- **역순 삭제**: 인덱스 변경 문제 해결을 위해 큰 위치부터 삭제
- **DOM 선택자**: `//button[contains(@class, 'ant-btn') and contains(@class, 'ant-btn-sm') and .//span[contains(@class, 'anticon-delete')]]`
- **검증**: `get_thumbnail_count`로 유효한 위치인지 확인

### 이벤트 처리: `process_delete_thumbnail_events`
- **파라미터**: `positions` (삭제할 위치 리스트)
- **전처리**: 썸네일 탭 선택
- **제한사항**: 최대 5개까지 삭제

## 4. Translate Image 메서드들

### 핵심 메서드: `translate_image_by_position`
- **목적**: 특정 위치의 이미지 번역
- **프로세스**:
  1. 상세페이지 탭 선택
  2. 일괄편집 모달창 열기
  3. 특정 위치 이미지 편집하기 클릭
  4. 번역 모달창 확인
  5. 이미지 번역 실행
  6. 번역된 이미지 저장

### 세부 메서드들
- **`select_detail_tab`**: 상세페이지 탭 선택
- **`open_bulk_edit_modal_for_translate`**: 일괄편집 모달창 열기
- **`click_edit_image_by_position`**: 특정 위치 편집하기 버튼 클릭
- **`check_translate_modal_open`**: 번역 모달창 확인
- **`execute_image_translation`**: 번역 실행 (버튼 클릭 또는 단축키 T)
- **`save_translated_image`**: 번역 결과 저장

### 이벤트 처리: `process_translate_image_events`
- **파라미터**: `positions` (번역할 이미지 위치 리스트)
- **순차 처리**: 각 위치별로 번역 수행
- **대기 시간**: 번역 처리를 위한 10초 대기

## 5. Insert Image Tag 메서드들

### 핵심 메서드: `insert_image_tag_by_position`
- **목적**: 상세페이지에 이미지 태그 HTML 삽입
- **프로세스**:
  1. 상세페이지 탭 선택
  2. 소스 편집 모드로 전환
  3. 에디터 영역에 이미지 태그 붙여넣기
  4. 일반 모드로 복귀

### 세부 메서드들
- **`click_source_button`**: 소스 편집 버튼 클릭 (스마트 클릭)
  - DOM 선택자 우선: `//button[contains(@class, 'ck-source-editing-button')]`
  - 백업으로 좌표 방식 사용
- **에디터 조작**: CKEditor 소스 편집 영역에서 HTML 태그 삽입
  - 선택자: `//div[contains(@class, 'ck-source-editing-area')]//textarea`
  - 커서를 끝으로 이동 후 태그 삽입

### 이벤트 처리: `process_insert_image_tag_events`
- **파라미터**: `image_tag` (삽입할 HTML 태그)
- **검증**: 빈 태그 체크
- **전처리**: 태그 내용 trim 처리

## 공통 특징

### 에러 처리
- 모든 메서드에서 상세한 로깅 제공
- TimeoutException, NoSuchElementException 처리
- 단계별 실패 시 명확한 에러 메시지

### 대기 시간 관리
- `DELAY_SHORT`: 짧은 대기
- `DELAY_MEDIUM`: 중간 대기  
- `timeout` 파라미터: 기본 10초

### DOM 선택 전략
- XPath 선택자 우선 사용
- 좌표 방식을 백업으로 활용
- 스마트 클릭 방식 적용

### 탭 관리
- 각 기능별로 적절한 탭 선택
- 탭 활성화 상태 확인
- 모달창 열기/닫기 관리

## 디버깅 포인트

1. **DOM 선택자 실패**: XPath 변경 또는 페이지 구조 변경 시
2. **타이밍 이슈**: 페이지 로딩 지연 또는 애니메이션 시간
3. **모달창 상태**: 모달창이 제대로 열리지 않는 경우
4. **인덱스 오류**: 삭제 시 인덱스 변경으로 인한 오류
5. **권한 문제**: 편집 권한이 없는 경우

이 문서는 3단계 코딩 과정에서 발생할 수 있는 오류를 빠르게 진단하고 해결하기 위한 참고 자료입니다.