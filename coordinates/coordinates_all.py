# -*- coding: utf-8 -*-
"""
퍼센티 좌표 통합 관리 파일 (coordinates_all.py)
이 파일은 모든 좌표 정의 파일을 가져와 통합하는 메인 임포트 파일입니다.
기존 코드에서 'coordinates1.py' 대신 이 파일을 임포트하여 사용하세요.

# 좌표 변환 공식
# relative_x = int(inner_width * (x / 1920))
# relative_y = int(inner_height * (y / 1080))
"""

# 모든 좌표 파일 명시적으로 가져오기
# 로그인 관련 좌표
from coordinates.coordinates_login import LOGIN, BROWSER_UI_HEIGHT, NOTIFICATION, LOGIN_MODAL

# 메뉴 관련 좌표
from coordinates.coordinates_menu import MENU

# 액션 관련 좌표
from coordinates.coordinates_action import PRODUCT, GROUP, PRODUCT_FORM_ELEMENTS

# 모달 관련 좌표
from coordinates.coordinates_modal import MODAL

# 상품 편집 관련 좌표
from coordinates.coordinates_editgoods import (
    PRODUCT_OPTION_TAB,
    PRODUCT_PRICE_TAB,
    PRODUCT_MODAL_CLOSE,
    PRODUCT_DETAIL_EDIT,
    PRODUCT_MEMO_MODAL,
    PRODUCT_MODAL_TAB,
    PRODUCT_MODAL_EDIT1,
    PRODUCT_MODAL_EDIT2,
    MANAGE_REGISTER_VIEW
)

# 좌표 변환 함수 가져오기
from coordinates.coordinate_conversion import convert_coordinates

# convert_coordinates 함수를 get_converted_coordinates라는 이름으로 재내보내기(re-export)
get_converted_coordinates = convert_coordinates

# 전역 상수 정의
# 브라우저 해상도 참조값 (좌표는 이 해상도 기준으로 측정됨)
REFERENCE_WIDTH = 1920   # 참조 화면 너비
REFERENCE_HEIGHT = 1080  # 참조 화면 높이

# 기존 코드 호환성을 위한 별칭 (coordinates1.py에 있던 변수들)
# 이전 코드가 참조하는 변수명이 유지되도록 함
MENU_OLD = MENU  # 기존 MENU 변수 호환성 유지
BROWSER_UI_HEIGHT_OLD = BROWSER_UI_HEIGHT  # 기존 변수 호환성 유지

# 참고: 이 함수는 이미 파일 상단에서 coordinate_conversion.py의 convert_coordinates 함수를 
# get_converted_coordinates라는 이름으로 재내보내기(re-export)했으므로 여기서는 제거합니다.
# 함수 중복 정의를 방지합니다.
