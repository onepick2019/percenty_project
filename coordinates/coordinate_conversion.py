"""
절대좌표를 상대좌표로 변환하는 유틸리티 모듈

X축과 Y축에 대한 구간별 보정값을 적용하여 좌표를 변환하는 공통 함수를 제공합니다.
"""

import logging

# 로깅 설정
logger = logging.getLogger(__name__)

def convert_coordinates(x, y, inner_width, inner_height):
    """
    절대좌표를 상대좌표로 변환
    
    Args:
        x: X 좌표 (절대값)
        y: Y 좌표 (절대값)
        inner_width: 브라우저 내부 너비
        inner_height: 브라우저 내부 높이
    
    Returns:
        tuple: 변환된 (x, y) 좌표
    """
    # 좌표 변환 공식 로깅
    logger.info(f"좌표 변환 공식: 개선된 비선형 변환 적용 - X축/Y축 화면 위치별 보정")
    
    # X축 보정계수 적용 (5구간으로 나누어 보정)
    # 구간 1: X 0-320 (최좌측 영역)
    if x <= 320:
        x_correction = 0.98
        logger.info(f"X축 최좌측 영역(0-320) 보정 계수 적용 ({x_correction})")
    # 구간 2: X 321-640 (좌측 영역)
    elif x <= 750:
        x_correction = 0.990
        logger.info(f"X축 좌측 영역(321-750) 보정 계수 적용 ({x_correction})")
    # 구간 3: X 751-1200 (중앙좌측 영역)
    elif x <= 1200:
        x_correction = 0.993
        logger.info(f"X축 중앙좌측 영역(751-1200) 보정 계수 적용 ({x_correction})")
    # 구간 4: X 1201-1300 (중앙 영역)
    elif x <= 1300:
        x_correction = 0.998
        logger.info(f"X축 중앙 영역(1201-1300) 보정 계수 적용 ({x_correction})")
    # 구간 5: X 1301-1425 (중앙우측 영역)
    elif x <= 1425:
        x_correction = 1.0
        logger.info(f"X축 중앙우측 영역(1301-1425) 보정 계수 적용 ({x_correction})")
    # 구간 6: X 1426-1435 (우측 영역) 
    elif x <= 1435:
        x_correction = 1.00355
        logger.info(f"X축 우측 영역(1426-1435) 보정 계수 적용 ({x_correction})")
    # 구간 7: X 1436-1500 (우측 영역)
    elif x <= 1500:
        x_correction = 1.0038
        logger.info(f"X축 우측 영역(1436-1500) 보정 계수 적용 ({x_correction})")
    # 구간 8: X 1501-1550 (최우측 영역)
    elif x <= 1550:
        x_correction = 1.004
        logger.info(f"X축 최우측 영역(1501-1550) 보정 계수 적용 ({x_correction})")
    # 구간 9: X 1551-1600 (최우측 영역)
    elif x <= 1600:
        x_correction = 1.005
        logger.info(f"X축 최우측 영역(1551-1600) 보정 계수 적용 ({x_correction})")
    elif x <= 1650:
        x_correction = 1.0055
        logger.info(f"X축 최우측 영역(1551-1600) 보정 계수 적용 ({x_correction})")        
    # 구간 10: X 1601-1700 (최우측 영역)
    elif x <= 1700:
        x_correction = 1.006
        logger.info(f"X축 최우측 영역(1601-1700) 보정 계수 적용 ({x_correction})")
    # 구간 11: X 1701-1800 (최우측 영역)
    elif x <= 1750:
        x_correction = 1.0062
        logger.info(f"X축 최우측 영역(1701-1800) 보정 계수 적용 ({x_correction})")    
    elif x <= 1800:
        x_correction = 1.0065
        logger.info(f"X축 최우측 영역(1701-1800) 보정 계수 적용 ({x_correction})")
    elif x <= 1850:
        x_correction = 1.0068
        logger.info(f"X축 최우측 영역(1701-1800) 보정 계수 적용 ({x_correction})")     
    elif x <= 1880:
        x_correction = 1.0071
        logger.info(f"X축 최우측 영역(1701-1800) 보정 계수 적용 ({x_correction})")              
    # 구간 12: X 1801+ (최외곽 영역)
    else:
        x_correction = 1.0072
        logger.info(f"X축 최외곽 영역(1801+) 보정 계수 적용 ({x_correction})")
        
    # 보정된 X축 계산
    rel_x = int(inner_width * (x / 1920) * x_correction)
    
    # Y축 보정계수 적용 (구간을 세분화하여 보정)
    # 구간 1: Y 0-115 (최상단 영역)
    if y <= 115:
        y_correction = 0.35
        logger.info(f"Y축 최상단 영역(0-115) 보정 계수 적용 ({y_correction})")
    # 구간 2: Y 116-121 (상단 영역)
    elif y <= 121:
        y_correction = 0.40
        logger.info(f"Y축 상단 영역(116-121) 보정 계수 적용 ({y_correction})")
    # 구간 3: Y 122-130 (상단 영역)
    elif y <= 130:
        y_correction = 0.46
        logger.info(f"Y축 상단 영역(122-130) 보정 계수 적용 ({y_correction})")
    # 구간 4: Y 131-140 (상단 영역)
    elif y <= 140:
        y_correction = 0.49
        logger.info(f"Y축 상단 영역(131-140) 보정 계수 적용 ({y_correction})")
    # 구간 5: Y 141-150 (상단 영역)
    elif y <= 150:
        y_correction = 0.52
        logger.info(f"Y축 상단 영역(141-150) 보정 계수 적용 ({y_correction})")
    # 구간 6: Y 151-180 (상단 영역)
    elif y <= 180:
        y_correction = 0.56
        logger.info(f"Y축 상단 영역(151-180) 보정 계수 적용 ({y_correction})")
    # 구간 7: Y 181-230 (상단 영역)
    elif y <= 230:
        y_correction = 0.73
        logger.info(f"Y축 상단 영역(181-230) 보정 계수 적용 ({y_correction})")
    # 구간 8: Y 231-280 (중상단 영역)
    elif y <= 280:
        y_correction = 0.80
        logger.info(f"Y축 중상단 영역(231-280) 보정 계수 적용 ({y_correction})")
    # 구간 9: Y 281-330 (중상단 영역)
    elif y <= 330:
        y_correction = 0.86
        logger.info(f"Y축 중상단 영역(281-330) 보정 계수 적용 ({y_correction})")
    # 구간 10: Y 331-440 (중상단 영역)
    elif y <= 440:
        y_correction = 0.89
        logger.info(f"Y축 중상단 영역(331-440) 보정 계수 적용 ({y_correction})")
    # 구간 11: Y 441-490 (중앙 영역)
    elif y <= 490:
        y_correction = 0.93
        logger.info(f"Y축 중앙 영역(441-490) 보정 계수 적용 ({y_correction})")
    # 구간 12: Y 491-540 (중앙 영역)
    elif y <= 540:
        y_correction = 0.94
        logger.info(f"Y축 중앙 영역(491-540) 보정 계수 적용 ({y_correction})")
    # 구간 13: Y 541-590 (중앙 영역)
    elif y <= 590:
        y_correction = 0.95
        logger.info(f"Y축 중앙 영역(541-590) 보정 계수 적용 ({y_correction})")
    # 구간 14: Y 591-640 (중앙 영역)
    elif y <= 640:
        y_correction = 0.96
        logger.info(f"Y축 중앙 영역(591-640) 보정 계수 적용 ({y_correction})")
    # 구간 15: Y 641-690 (중앙하단 영역)
    elif y <= 690:
        y_correction = 0.97
        logger.info(f"Y축 중앙하단 영역(641-690) 보정 계수 적용 ({y_correction})")
    # 구간 16: Y 691-715 (중앙하단 영역)
    elif y <= 715:
        y_correction = 1.00
        logger.info(f"Y축 중앙하단 영역(691-715) 보정 계수 적용 ({y_correction})")
    # 구간 17: Y 716-740 (하단 영역)
    elif y <= 740:
        y_correction = 1.00
        logger.info(f"Y축 하단 영역(716-740) 보정 계수 적용 ({y_correction})")
    # 구간 18: Y 741-845 (하단 영역)
    elif y <= 790:
        y_correction = 1.00
        logger.info(f"Y축 하단 영역(716-740) 보정 계수 적용 ({y_correction})")
    # 구간 18: Y 741-845 (하단 영역)    
    elif y <= 845:
        y_correction = 1.00
        logger.info(f"Y축 하단 영역(741-845) 보정 계수 적용 ({y_correction})")
    # 구간 19: Y 846-890 (최하단 영역)
    elif y <= 890:
        y_correction = 1.025
        logger.info(f"Y축 최하단 영역(846-890) 보정 계수 적용 ({y_correction})")
    # 구간 20: Y 891-935 (최하단 영역)
    elif y <= 935:
        y_correction = 1.03
        logger.info(f"Y축 최하단 영역(891-935) 보정 계수 적용 ({y_correction})")
    elif y <= 990:
        y_correction = 1.04
        logger.info(f"Y축 최하단 영역(891-935) 보정 계수 적용 ({y_correction})")        
    # 구간 21: Y 936+ (최하단 영역)
    else:
        y_correction = 1.05
        logger.info(f"Y축 최하단 영역(936+) 보정 계수 적용 ({y_correction})")
            
    # 보정된 Y축 계산
    rel_y = int(inner_height * (y / 1080) * y_correction)
    
    # 변환 상세 정보 추가 로깅
    logger.info(f"변환 상세 정보 - 브라우저 크기: {inner_width}x{inner_height}, 참조 크기: 1920x1080")
    logger.info(f"X축 계산: int({inner_width} * ({x} / 1920) * {x_correction:.2f}) = {rel_x}")
    logger.info(f"Y축 계산: int({inner_height} * ({y} / 1080) * {y_correction:.2f}) = {rel_y}")
    
    logger.info(f"좌표 변환: {(x, y)} -> {(rel_x, rel_y)}")
    return rel_x, rel_y
