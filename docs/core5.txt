5단계 product_editor_core5.py 개발

percenty_new_step5.py 는 현재 등록상품관리 화면까지 열리도록 코딩되어 있다.
지금부터 코어는 product_editor_core5.py 파일을 새로 만들어서 만들 것이니, percenty_new_step5.py 에서는 product_editor_core5.py 를 임포트할 수 있도록 준비한다.

코어파일의 내용은 아래와 같다.
>> 대기1 그룹에 있는 상품 1개마다 복제상품을 3개 만들면 모두 4개의 상품이 된다. 4개 상품마다 일부 내용을 수정한 후에 쇼핑몰A1, 쇼핑몰B1, 쇼핑몰C1,쇼핑몰D1으로 이동하는 로직을 완성해야 한다.


logger.info("\n\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
logger.info("!!! 복사상품 3개 만들기 !!!")
logger.info("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n")

# 1-1. 대기1 그룹을 선택해 상품 검색
# dropdown_utils.py 에 있는 select_group_in_management_screen 메서드를 이용해 '대기1' 그룹을 선택해 상품을 검색한다.
logger.info("1-1. 대기1 그룹을 선택해 상품 검색")

# 1-2. 첫번째 상품 쇼핑몰T로 이동하기
# 첫번째 상품을 개별상품의 그룹이동 메서드를 이용해 '쇼핑몰T' 그룹으로 이동한다.
# 개별상품내 드롭박스를 이용해 이동하기 (dropdown_utils.py 에 있는 메서드 이용)
logger.info("1-2. 첫번째 상품 쇼핑몰T로 이동하기")

# 1-3. 쇼핑몰T 그룹을 선택해 상품 검색
# select_group_in_management_screen 메서드를 이용해 '쇼핑몰T' 그룹을 선택해 상품을 검색한다.
logger.info("1-3. 쇼핑몰T 그룹을 선택해 상품 검색")

# 1-4. 첫번째 상품 클릭해 수정화면 모달창 열기
# 코어1의 _click_first_product 와 wait_for_tab_active 를 사용해서, 첫번째 상품을 클릭해 수정화면 모달창을 열고, 잘 열렸는지 확인한다.
logger.info("1-4. 첫번째 상품 클릭해 수정화면 모달창 열기 (FIRST_PRODUCT_ITEM DOM 선택자 사용)")

# 1-5. 메모편집 모달창 열기
# 코어1에 있는 "# 4. 메모편집 모달창 열기" 를 그대로 사용한다.
logger.info("1-5. 메모편집 모달창 열기")

# 1-6. 상품 목록에 메모 내용 노출하기 클릭 - 체크되지 않은 경우에만 클릭
# 코어1에 있는 "# 5. 상품 목록에 메모 내용 노출하기 클릭 - 체크되지 않은 경우에만 클릭" 를 그대로 사용한다.
logger.info("1-6. 상품 목록에 메모 내용 노출하기 체크박스 상태 확인")

# 1-7. 메모 저장 버튼 클릭
# 코어1에 있는 "# 8. 메모 저장 버튼 클릭" 를 그대로 사용한다.
logger.info("1-7. 메모 저장 버튼 클릭")
smart_click(self.driver, UI_ELEMENTS["MEMO_MODAL_SAVEBUTTON"], DELAY_VERY_SHORT)

# 1-8. 옵션 탭 선택 (하이브리드방식)
logger.info("1-8. 옵션 탭 선택 (하이브리드방식)")
smart_click(self.driver, UI_ELEMENTS["PRODUCT_TAB_OPTION"], DELAY_VERY_SHORT)
# 탭이 활성화될 때까지 명시적 대기
self.wait_for_tab_active("PRODUCT_TAB_OPTION")

# 1-9. AI 옵션명 다듬기 클릭 (하이브리드방식)
logger.info("1-9. AI 옵션명 다듬기 클릭 (하이브리드방식)")
smart_click(self.driver, UI_ELEMENTS["PRODUCT_OPTION_AI"], DELAY_VERY_SHORT)

# 1-10. 옵션명 접두어로 숫자 추가 버튼 클릭 (하이브리드방식)
logger.info("1-10. 옵션명 접두어로 숫자 추가 버튼 클릭 (하이브리드방식)")
smart_click(self.driver, UI_ELEMENTS["PRODUCT_OPTION_NUMBER"], DELAY_VERY_SHORT)

# 1-11. 상품명 탭 선택 (하이브리드방식)
logger.info("1-11. 상품명 탭 선택 (하이브리드방식)")
smart_click(self.driver, UI_ELEMENTS["PRODUCT_TAB_BASIC"], DELAY_VERY_SHORT)
# 탭이 활성화될 때까지 명시적 대기
self.wait_for_tab_active("PRODUCT_TAB_BASIC")


# 1-12. 상품복사하기 3회 진행하는 함수
# smart_click(self.driver, UI_ELEMENTS["PRODUCT_COPY_ITEM"], DELAY_EXTRA_LONG) 로 클릭해서 복사한다.
# 동적요소가 없다면 지연시간은 10초인 DELAY_EXTRA_LONG 정도 주어야 한다. 아래의 방법으로 동적으로 작동하도록 한다.
# 상품복사 버튼을 클릭하면, 복제상품이 만들어지기까지 네트워크 상황에 따라 빠른 경우에는 3초 이내, 간혹 있는 상황이지만 5초이상 소요되는 경우가 있다.
# 첫번째 상품복사를 클릭한 후, 쇼핑몰T의 총상품수가 2개인 것을 확인하고, 두번째 상품복사를 클릭한다. 
# 쇼핑몰T의 총상품수가 3개인 것을 확인하고 상품복사를 클릭한다. 
# 이렇게 총상품수의 변화를 체크해서 불필요한 지연시간을 줄일 수 있도록 동적으로 상품복사를 3회 진행해야 한다.
# 복사하기 3회 이후에는 쇼핑몰T의 총상품수가 4개인 것을 확인해야 한다.
logger.info("1-12. 상품복사하기 3회 진행하는 함수")

# 1-13. 상품명 TEXTAREA 클릭 (하이브리드방식) 
logger.info("1-13. 상품명 TEXTAREA 클릭 (하이브리드방식) ")
smart_click(self.driver, UI_ELEMENTS["PRODUCT_NAMEEDIT_TEXTAREA"], DELAY_VERY_SHORT2)

# 1-14. 기존의 상품명에 E열(suffixA1)의 접미사 추가 함수 개발
# 로그인한 각각의 계정별로 percenty_id.xlsx 파일의 login_id 시트에 있는 E열에서 P열까지의 값을 파싱해야한다.
# 공백 하나 추가한 다음에 H열(suffixB1)의 접미사 추가하도록 해야 한다.
# 상품명에 접미사를 붙여 저장하는 방식은 코어1의 22번 과정 참조한다.
logger.info("1-14. 기존의 상품명에 E열(suffixA1)의 접미사 추가")

# 1-15. 상품수정 모달창 나가기 (ESC 키로 나가기)
logger.info("1-15. 상품수정 모달창 나가기 (ESC 키로 나가기)")

logger.info("\n\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
logger.info("!!! 첫번째 복사상품 최적화하기 !!!")
logger.info("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n")

# 2-1. 첫번째 상품 클릭해 수정화면 모달창 열기
# 코어1의 _click_first_product 와 wait_for_tab_active 를 사용해서, 첫번째 상품을 클릭해 수정화면 모달창을 열고, 잘 열렸는지 확인한다.
logger.info("2-1. 첫번째 상품 클릭해 수정화면 모달창 열기 (FIRST_PRODUCT_ITEM DOM 선택자 사용)")

# 2-2. 상품명 TEXTAREA 클릭 (하이브리드방식) 
logger.info("2-2. 상품명 TEXTAREA 클릭 (하이브리드방식)")
smart_click(self.driver, UI_ELEMENTS["PRODUCT_NAMEEDIT_TEXTAREA"], DELAY_VERY_SHORT2)

# 2-3. 기존의 상품명에 H열(suffixB1)의 접미사 추가 함수 개발
# 로그인한 각각의 계정별로 percenty_id.xlsx 파일의 login_id 시트에 있는 E열에서 P열까지의 값을 파싱해야한다.
# 복사하면서 추가된 접미사 (3)을 삭제하고, 공백 하나 추가한 다음에 H열(suffixB1)의 접미사 추가하도록 해야 한다.
# 접미사 (3)의 삭제방법은 Backspace 3회 실행으로 처리한다.
# 상품명에 접미사를 붙여 저장하는 방식은 코어1의 22번 과정 참조한다.
logger.info("2-3. 기존의 상품명에 H열(suffixB1)의 접미사 추가")

# 2-4. 가격 탭 선택 (하이브리드방식)
logger.info("2-4. 가격 탭 선택 (하이브리드방식)")
smart_click(self.driver, UI_ELEMENTS["PRODUCT_TAB_PRICE"], DELAY_VERY_SHORT2)
# 탭이 활성화될 때까지 명시적 대기
self.wait_for_tab_active("PRODUCT_TAB_PRICE")

# 2-5. 마켓 표시 할인율 입력 입력창 선택
logger.info("2-5. 마켓 표시 할인율 입력 입력창 선택")
smart_click(self.driver, UI_ELEMENTS["PRODUCT_PRICE_DISCOUNTRATE"], DELAY_VERY_SHORT2)

# 2-6. 기존의 할인율을 지우고 새로운 할인율을 순차적으로 붙여주는 함수
# 기존의 할인율은 지워야 하므로, 순차적으로 붙여주는 새로운 할인율은 Ctrl+A를 하고 붙여주어야 한다.
# 순차적으로 붙여주는 할인율은 10개 상품마다 반복한다.
# 순차적으로 붙여주는 할인율 순서 : 2, 5, 10, 15, 20, 25, 30, 35, 40, 45
logger.info("2-6. 새로운 할인율 입력 시작")

# 2-7. 썸네일 탭 선택 (하이브리드방식)
logger.info("2-6. 썸네일 탭 선택 (하이브리드방식)")
smart_click(self.driver, UI_ELEMENTS["PRODUCT_TAB_THUMBNAIL"], DELAY_VERY_SHORT2)
# 탭이 활성화될 때까지 명시적 대기
self.wait_for_tab_active("PRODUCT_TAB_THUMBNAIL")

# 2-8. 두번째 썸네일을 맨 앞으로 이동하기
# image_utils 에 있는 move_thumbnail_to_front 를 이용한다.
logger.info("2-8. 두번째 썸네일을 맨 앞으로 이동하기)")

# 2-9. 상품수정 모달창 나가기 (ESC 키로 나가기)
logger.info("2-9. 상품수정 모달창 나가기 (ESC 키로 나가기)")

# 2-10. 수정한 첫번째 상품을 쇼핑몰B1 그룹으로 이동하기
# 개별상품내 드롭박스를 이용해 이동하기 (dropdown_utils.py 에 있는 메서드 이용)
logger.info("2-10. 수정한 첫번째 상품을 쇼핑몰B1 그룹으로 이동하기")


logger.info("\n\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
logger.info("!!! 두번째 복사상품 최적화하기 !!!")
logger.info("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n")

# 3-1. 첫번째 상품 클릭해 수정화면 모달창 열기
# 코어1의 _click_first_product 와 wait_for_tab_active 를 사용해서, 첫번째 상품을 클릭해 수정화면 모달창을 열고, 잘 열렸는지 확인한다.
logger.info("3-1. 첫번째 상품 클릭해 수정화면 모달창 열기 (FIRST_PRODUCT_ITEM DOM 선택자 사용)")

# 3-2. 상품명 TEXTAREA 클릭 (하이브리드방식) 
logger.info("3-2. 상품명 TEXTAREA 클릭 (하이브리드방식)")
smart_click(self.driver, UI_ELEMENTS["PRODUCT_NAMEEDIT_TEXTAREA"], DELAY_VERY_SHORT2)

# 3-3. 기존의 상품명에 K열(suffixC1)의 접미사 추가 함수 개발
# 로그인한 각각의 계정별로 percenty_id.xlsx 파일의 login_id 시트에 있는 E열에서 P열까지의 값을 파싱해야한다.
# 복사하면서 추가된 접미사 (2)을 삭제하고, 공백 하나 추가한 다음에 K열(suffixC1)의 접미사 추가하도록 해야 한다.
# 접미사 (2)의 삭제방법은 Backspace 3회 실행으로 처리한다.
# 상품명에 접미사를 붙여 저장하는 방식은 코어1의 22번 과정 참조한다.
logger.info("3-3. 기존의 상품명에 K열(suffixC1)의 접미사 추가")

# 3-4. 가격 탭 선택 (하이브리드방식)
logger.info("3-4. 가격 탭 선택 (하이브리드방식)")
smart_click(self.driver, UI_ELEMENTS["PRODUCT_TAB_PRICE"], DELAY_VERY_SHORT2)
# 탭이 활성화될 때까지 명시적 대기
self.wait_for_tab_active("PRODUCT_TAB_PRICE")

# 3-5. 마켓 표시 할인율 입력 입력창 선택
logger.info("3-5. 마켓 표시 할인율 입력 입력창 선택")
smart_click(self.driver, UI_ELEMENTS["PRODUCT_PRICE_DISCOUNTRATE"], DELAY_VERY_SHORT2)

# 3-6. 기존의 할인율을 지우고 새로운 할인율을 순차적으로 붙여주는 함수
# 기존의 할인율은 지워야 하므로, 순차적으로 붙여주는 새로운 할인율은 Ctrl+A를 하고 붙여주어야 한다.
# 순차적으로 붙여주는 할인율은 10개 상품마다 반복한다.
# 순차적으로 붙여주는 할인율 순서 : 15, 20, 25, 30, 35, 40, 45, 2, 5, 10
logger.info("3-6. 새로운 할인율 입력 시작")

# 3-7. 썸네일 탭 선택 (하이브리드방식)
logger.info("3-6. 썸네일 탭 선택 (하이브리드방식)")
smart_click(self.driver, UI_ELEMENTS["PRODUCT_TAB_THUMBNAIL"], DELAY_VERY_SHORT2)
# 탭이 활성화될 때까지 명시적 대기
self.wait_for_tab_active("PRODUCT_TAB_THUMBNAIL")

# 3-8. 세번째 썸네일을 맨 앞으로 이동하기
# image_utils 에 있는 move_thumbnail_to_front 를 이용한다.
logger.info("3-8. 세번째 썸네일을 맨 앞으로 이동하기)")

# 3-9. 상품수정 모달창 나가기 (ESC 키로 나가기)
logger.info("3-9. 상품수정 모달창 나가기 (ESC 키로 나가기)")

# 3-10. 수정한 첫번째 상품을 쇼핑몰C1 그룹으로 이동하기
# 개별상품내 드롭박스를 이용해 이동하기 (dropdown_utils.py 에 있는 메서드 이용)
logger.info("3-10. 수정한 첫번째 상품을 쇼핑몰C1 그룹으로 이동하기")


logger.info("\n\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
logger.info("!!! 세번째 복사상품 최적화하기 !!!")
logger.info("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n")

# 4-1. 첫번째 상품 클릭해 수정화면 모달창 열기
# 코어1의 _click_first_product 와 wait_for_tab_active 를 사용해서, 첫번째 상품을 클릭해 수정화면 모달창을 열고, 잘 열렸는지 확인한다.
logger.info("4-1. 첫번째 상품 클릭해 수정화면 모달창 열기 (FIRST_PRODUCT_ITEM DOM 선택자 사용)")

# 4-2. 상품명 TEXTAREA 클릭 (하이브리드방식) 
logger.info("4-2. 상품명 TEXTAREA 클릭 (하이브리드방식)")
smart_click(self.driver, UI_ELEMENTS["PRODUCT_NAMEEDIT_TEXTAREA"], DELAY_VERY_SHORT2)

# 4-3. 기존의 상품명에 N열(suffixD1)의 접미사 추가 함수 개발
# 로그인한 각각의 계정별로 percenty_id.xlsx 파일의 login_id 시트에 있는 E열에서 P열까지의 값을 파싱해야한다.
# 복사하면서 추가된 접미사 (1)을 삭제하고, 공백 하나 추가한 다음에 N열(suffixD1)의 접미사 추가하도록 해야 한다.
# 접미사 (1)의 삭제방법은 Backspace 3회 실행으로 처리한다.
# 상품명에 접미사를 붙여 저장하는 방식은 코어1의 22번 과정 참조한다.
logger.info("4-3. 기존의 상품명에 N열(suffixD1)의 접미사 추가")

# 4-4. 가격 탭 선택 (하이브리드방식)
logger.info("4-4. 가격 탭 선택 (하이브리드방식)")
smart_click(self.driver, UI_ELEMENTS["PRODUCT_TAB_PRICE"], DELAY_VERY_SHORT2)
# 탭이 활성화될 때까지 명시적 대기
self.wait_for_tab_active("PRODUCT_TAB_PRICE")

# 4-5. 마켓 표시 할인율 입력 입력창 선택
logger.info("4-5. 마켓 표시 할인율 입력 입력창 선택")
smart_click(self.driver, UI_ELEMENTS["PRODUCT_PRICE_DISCOUNTRATE"], DELAY_VERY_SHORT2)

# 4-6. 기존의 할인율을 지우고 새로운 할인율을 순차적으로 붙여주는 함수
# 기존의 할인율은 지워야 하므로, 순차적으로 붙여주는 새로운 할인율은 Ctrl+A를 하고 붙여주어야 한다.
# 순차적으로 붙여주는 할인율은 10개 상품마다 반복한다.
# 순차적으로 붙여주는 할인율 순서 : 30, 35, 40, 45, 2, 5, 10, 15, 20, 25
logger.info("4-6. 새로운 할인율 입력 시작")

# 4-7. 썸네일 탭 선택 (하이브리드방식)
logger.info("4-6. 썸네일 탭 선택 (하이브리드방식)")
smart_click(self.driver, UI_ELEMENTS["PRODUCT_TAB_THUMBNAIL"], DELAY_VERY_SHORT2)
# 탭이 활성화될 때까지 명시적 대기
self.wait_for_tab_active("PRODUCT_TAB_THUMBNAIL")

# 4-8. 두번째 썸네일을 맨 앞으로 이동하기
# image_utils 에 있는 move_thumbnail_to_front 를 이용한다.
logger.info("4-8. 두번째 썸네일을 맨 앞으로 이동하기)")

# 4-9. 상품수정 모달창 나가기 (ESC 키로 나가기)
logger.info("4-9. 상품수정 모달창 나가기 (ESC 키로 나가기)")

# 4-10. 수정한 첫번째 상품을 쇼핑몰B1 그룹으로 이동하기
# 개별상품내 드롭박스를 이용해 이동하기 (dropdown_utils.py 에 있는 메서드 이용)
logger.info("4-10. 수정한 첫번째 상품을 쇼핑몰D1 그룹으로 이동하기")

logger.info("\n\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
logger.info("!!! 원본상품 그룹이동하기 !!!")
logger.info("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n")

# 5. 원본 상품을 쇼핑몰A1 그룹으로 이동하기
# 개별상품내 드롭박스를 이용해 이동하기 (dropdown_utils.py 에 있는 메서드 이용)
logger.info("4-10. 수정한 첫번째 상품을 쇼핑몰A1 그룹으로 이동하기")

