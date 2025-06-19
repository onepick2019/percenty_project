# 유틸리티 파일 메서드 문서

이 문서는 `upload_utils.py`와 `market_utils.py` 파일에 포함된 모든 메서드와 기능을 정리한 표준 문서입니다.

## `upload_utils.py`

`UploadUtils` 클래스는 상품 업로드 관련 기능을 제공하는 유틸리티 클래스입니다.

### 상품 선택 관련 메서드

- `select_all_products()`: 모든 상품을 선택합니다.
- `get_selected_products_count()`: 선택된 상품의 개수를 반환합니다.

### 버튼 클릭 메서드

- `click_upload_button()`: 업로드 버튼을 클릭합니다.
- `click_batch_translate_button()`: 일괄 번역 버튼을 클릭합니다.
- `click_delete_button()`: 삭제 버튼을 클릭합니다.
- `click_batch_edit_button()`: 일괄 수정 버튼을 클릭합니다.

### 워크플로우 메서드

- `perform_upload_workflow()`: 업로드 전체 워크플로우를 수행합니다.
- `perform_batch_translate_workflow()`: 일괄 번역 전체 워크플로우를 수행합니다.
- `perform_delete_workflow()`: 삭제 전체 워크플로우를 수행합니다.

### 업로드 모달 관련 메서드

- `handle_upload_modal()`: 업로드 모달창을 처리합니다.
- `select_markets_in_modal(market_list)`: 업로드 모달에서 특정 마켓들을 선택합니다.
- `click_upload_button_in_modal()`: 업로드 모달 내의 업로드 버튼을 클릭합니다.
- `close_upload_modal()`: 업로드 모달창을 닫습니다.

## `market_utils.py`

`MarketUtils` 클래스는 마켓 설정 및 API 검증 관련 기능을 제공하는 유틸리티 클래스입니다.

### 마켓 탭 관련 메서드

- `get_market_tab_selector(market_key)`: 특정 마켓의 탭 선택자를 반환합니다.
- `switch_to_market(market_key)`: 특정 마켓 탭으로 전환합니다.
- `wait_for_market_panel_load(market_key, timeout=10)`: 마켓 패널이 로드될 때까지 대기합니다.

### 기본 선택자 메서드

- `get_market_buttons_container_selector()`: 마켓 설정 탭 내 버튼 컨테이너 선택자를 반환합니다.
- `get_api_disconnect_button_selector()`: API 연결 끊기 버튼 선택자를 반환합니다.
- `get_upload_account_settings_button_selector()`: 업로드할 계정 설정하기 버튼 선택자를 반환합니다.
- `get_api_verification_button_selector()`: API 검증 버튼 선택자를 반환합니다.

### 기본 상호작용 메서드

- `click_api_disconnect_button()`: API 연결 끊기 버튼을 클릭합니다.
- `click_account_setting_button()`: 업로드할 계정 설정하기 버튼을 클릭합니다.
- `click_api_validation_button()`: API 검증 버튼을 클릭합니다.
- `click_button_by_text(button_text)`: 주어진 텍스트를 포함하는 버튼을 클릭합니다.
- `is_button_visible(button_text)`: 주어진 텍스트를 포함하는 버튼이 보이는지 확인합니다.
- `get_available_buttons()`: 현재 보이는 버튼 목록을 가져옵니다.

### 기본 워크플로우 메서드

- `perform_market_setup_workflow(market_name)`: 특정 마켓의 설정 탭으로 이동하고 사용 가능한 버튼을 확인합니다.

## API 연결 끊기 모달 관련 메서드

### 선택자 메서드

- `get_api_disconnect_modal_selector()`: API 연결 끊기 모달창 선택자를 반환합니다.
- `get_api_disconnect_modal_confirm_button_selector()`: API 연결 끊기 확인 버튼 선택자를 반환합니다.
- `get_api_disconnect_modal_cancel_button_selector()`: API 연결 끊기 취소 버튼 선택자를 반환합니다.
- `get_api_disconnect_modal_close_button_selector()`: API 연결 끊기 모달 닫기 버튼 선택자를 반환합니다.
- `get_api_disconnect_modal_error_alert_selector()`: API 연결 끊기 모달 에러 알림 선택자를 반환합니다.
- `get_api_disconnect_modal_warning_alert_selector()`: API 연결 끊기 모달 경고 알림 선택자를 반환합니다.

### 상호작용 메서드

- `wait_for_api_disconnect_modal(timeout=10)`: API 연결 끊기 모달창이 나타날 때까지 대기합니다.
- `click_api_disconnect_modal_confirm()`: API 연결 끊기 모달창에서 확인 버튼을 클릭합니다.
- `click_api_disconnect_modal_cancel()`: API 연결 끊기 모달창에서 취소 버튼을 클릭합니다.
- `close_api_disconnect_modal()`: API 연결 끊기 모달창을 닫습니다 (X 버튼 클릭).
- `get_api_disconnect_modal_alert_messages()`: API 연결 끊기 모달창의 알림 메시지들을 반환합니다.

### 통합 워크플로우 메서드

- `handle_api_disconnect_modal(confirm=True)`: API 연결 끊기 모달창을 처리합니다.
- `perform_complete_api_disconnect_workflow(market_key, confirm=True)`: API 연결 끊기 전체 워크플로우를 수행합니다.

## 11번가 API 검증 모달 관련 메서드

### 선택자 메서드

- `get_11st_api_verification_modal_selector()`: 11번가 API 검증 모달창(드로어) 선택자를 반환합니다.
- `get_11st_shipping_profile_create_button_selector()`: 11번가 배송프로필 만들기 버튼 선택자를 반환합니다.
- `get_11st_delivery_company_dropdown_selector()`: 11번가 출고 택배사 드롭다운 선택자를 반환합니다.
- `get_11st_delivery_company_dropdown_arrow_selector()`: 11번가 출고 택배사 드롭다운 화살표 선택자를 반환합니다.
- `get_11st_lotte_delivery_option_selector()`: 11번가 롯데(현대)택배 옵션 선택자를 반환합니다.

### 상호작용 메서드

- `wait_for_11st_api_verification_modal(timeout=10)`: 11번가 API 검증 모달창이 나타날 때까지 대기합니다.
- `select_11st_lotte_delivery_company()`: 11번가 출고 택배사에서 롯데(현대)택배를 선택합니다.
- `click_11st_shipping_profile_create_button()`: 11번가 배송프로필 만들기 버튼을 클릭합니다.

### 통합 워크플로우 메서드

- `handle_11st_api_verification_modal()`: 11번가 API 검증 모달창을 처리합니다 (롯데택배 선택 + 버튼 클릭).
- `perform_complete_11st_api_verification_workflow()`: 11번가 API 검증 전체 워크플로우를 수행합니다.

## 옥션/G마켓 API 검증 모달 관련 메서드

### 선택자 메서드

- `get_auction_gmarket_api_verification_modal_selector()`: 옥션/G마켓 API 검증 모달창(드로어) 선택자를 반환합니다.
- `get_auction_gmarket_shipping_profile_create_button_selector()`: 옥션/G마켓 배송프로필 만들기 버튼 선택자를 반환합니다.
- `get_auction_gmarket_delivery_company_dropdown_selector()`: 옥션/G마켓 택배사 드롭다운 선택자를 반환합니다.
- `get_auction_gmarket_lotte_delivery_option_selector()`: 옥션/G마켓 롯데택배 옵션 선택자를 반환합니다.
- `get_gmarket_site_discount_agree_button_selector()`: G마켓 사이트할인 동의 버튼 선택자를 반환합니다.
- `get_auction_site_discount_agree_button_selector()`: 옥션 사이트할인 동의 버튼 선택자를 반환합니다.

### 상호작용 메서드

- `wait_for_auction_gmarket_api_verification_modal(timeout=10)`: 옥션/G마켓 API 검증 모달창이 나타날 때까지 대기합니다.
- `select_auction_gmarket_lotte_delivery_company()`: 옥션/G마켓 택배사에서 롯데택배를 선택합니다.
- `click_gmarket_site_discount_agree()`: G마켓 사이트할인 동의 버튼을 클릭합니다.
- `click_auction_site_discount_agree()`: 옥션 사이트할인 동의 버튼을 클릭합니다.
- `click_auction_gmarket_shipping_profile_create_button()`: 옥션/G마켓 배송프로필 만들기 버튼을 클릭합니다.

### 통합 워크플로우 메서드

- `handle_auction_gmarket_api_verification_modal()`: 옥션/G마켓 API 검증 모달창을 처리합니다 (롯데택배 선택 + 동의 클릭 + 버튼 클릭).
- `perform_complete_auction_gmarket_api_verification_workflow(market_key)`: 옥션/G마켓 API 검증 전체 워크플로우를 수행합니다.

## 메서드 사용 가이드라인

### 1. 기본 원칙
- 모든 메서드는 SOLID 원칙을 따라 단일 책임을 가집니다.
- 선택자 메서드는 CSS 선택자만 반환하고, 상호작용 메서드는 실제 동작을 수행합니다.
- 통합 워크플로우 메서드는 여러 단계를 조합하여 완전한 작업을 수행합니다.

### 2. 에러 처리
- 모든 메서드는 적절한 예외 처리를 포함합니다.
- 실패 시 False를 반환하고, 성공 시 True를 반환합니다.
- 로깅을 통해 상세한 오류 정보를 제공합니다.

### 3. 재사용성
- 선택자 메서드는 다른 메서드에서 재사용 가능합니다.
- 기본 상호작용 메서드는 통합 워크플로우에서 조합하여 사용됩니다.
- DRY 원칙을 따라 중복 코드를 최소화합니다.

### 4. 확장성
- 새로운 마켓 추가 시 기존 패턴을 따라 메서드를 추가할 수 있습니다.
- 모달창 처리 패턴은 일관성을 유지하여 확장 가능합니다.

이 문서는 개발 과정에서 표준 참조 자료로 활용되어야 하며, 새로운 기능 추가 시 이 패턴을 따라 구현해야 합니다.