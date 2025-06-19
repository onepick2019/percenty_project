# 퍼센티 자동화 설정 파일

# 로그인 정보
LOGIN = {
    "url": "https://www.percenty.co.kr/signin",
    "username": "onepick2019@gmail.com",
    "password": "qnwkehlwk8*"
}

# 브라우저 설정
HEADLESS = False  # True: 백그라운드 실행, False: 브라우저 표시

# 브라우저 상세 설정
BROWSER = {
    "headless": False,  # 백그라운드 실행 여부
    "maximize": True,  # 창 최대화 여부
    "disable_notifications": True,  # 알림 비활성화 여부
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"  # 사용자 에이전트
}

# 지연 시간 설정 (초)
MIN_DELAY = 1
MAX_DELAY = 5
PAGE_LOAD_MIN = 2
PAGE_LOAD_MAX = 4

# 보고서 파일명
REPORT_FILE = "percenty_report.csv"

# 지연 시간 설정 (utils.py에서 사용)
DELAY = {
    "min": 1,
    "max": 3,
    "page_load": {
        "min": 2,
        "max": 4
    }
}

# 재시도 설정
RETRY = {
    "max_attempts": 3,  # 최대 시도 횟수
    "delay": 2,        # 재시도 간격 (초)
    "backoff": 2       # 재시도 간격 증가 배수
}

# 로깅 설정
LOGGING = {
    "level": "INFO",  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    "file": "percenty_automation.log"
}
