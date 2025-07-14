# 텔레그램 알림 시스템 가이드

## 개요

배치 작업 중 특별한 이슈 발생 시 텔레그램을 통해 실시간 알림을 받을 수 있는 시스템입니다.

## 설정 방법

### 1. 텔레그램 봇 생성

1. 텔레그램 앱에서 `@BotFather`를 검색하여 대화 시작
2. `/newbot` 명령어 입력
3. 봇 이름 입력 (예: "퍼센티 배치 알림봇")
4. 봇 사용자명 입력 (예: "percenty_batch_bot")
5. 생성된 봇 토큰 복사 (예: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. 채팅 ID 확인

1. 생성된 봇과 대화 시작
2. `/start` 명령어 또는 아무 메시지 전송
3. 브라우저에서 다음 URL 접속:
   ```
   https://api.telegram.org/bot[봇토큰]/getUpdates
   ```
4. JSON 응답에서 `chat.id` 값 확인 (예: `7918845682`)

### 3. 설정 파일 구성

#### 방법 1: 기본 설정 파일 수정

`batch/config/batch_config.json` 파일의 `telegram` 섹션을 수정:

```json
{
  "telegram": {
    "enabled": true,
    "bot_token": "YOUR_BOT_TOKEN_HERE",
    "chat_id": "7918845682",
    "notify_start": true,
    "notify_complete": true,
    "notify_error": true,
    "notify_warning": true
  }
}
```

#### 방법 2: 예시 파일 복사 후 수정

1. `telegram_config_example.json` 파일을 `batch/config/batch_config.json`으로 복사
2. 봇 토큰과 채팅 ID 입력
3. `enabled`를 `true`로 변경

### 4. 연결 테스트

```python
from telegram_notifier import TelegramNotifier

# 텔레그램 알림 객체 생성
notifier = TelegramNotifier(
    bot_token="YOUR_BOT_TOKEN_HERE",
    chat_id="7918845682"
)

# 연결 테스트
if notifier.test_connection():
    print("텔레그램 알림 시스템이 정상적으로 설정되었습니다.")
else:
    print("텔레그램 알림 시스템 설정에 문제가 있습니다.")
```

## 알림 종류

### 1. 배치 시작 알림
- 배치 작업이 시작될 때 전송
- 계정, 단계, 서버, 시작 시간 정보 포함

### 2. 배치 완료 알림
- 배치 작업이 성공적으로 완료될 때 전송
- 계정, 단계, 서버, 완료 시간, 소요 시간 정보 포함

### 3. 배치 오류 알림
- 배치 작업 중 오류 발생 시 전송
- 계정, 단계, 서버, 오류 시간, 오류 내용 포함
- 즉시 확인이 필요한 상황

### 4. 배치 경고 알림
- 배치 작업 중 경고 상황 발생 시 전송
- 계정, 단계, 서버, 경고 시간, 경고 내용 포함

## 알림 설정 옵션

```json
{
  "telegram": {
    "enabled": true,           // 텔레그램 알림 활성화 여부
    "bot_token": "...",        // 봇 토큰
    "chat_id": "...",          // 채팅 ID
    "notify_start": true,      // 시작 알림 활성화
    "notify_complete": true,   // 완료 알림 활성화
    "notify_error": true,      // 오류 알림 활성화
    "notify_warning": true     // 경고 알림 활성화
  }
}
```

## 사용 예시

### 배치 매니저에서 자동 알림

```python
from batch.batch_manager import BatchManager

# 배치 매니저 생성 (설정 파일에서 텔레그램 설정 자동 로드)
batch_manager = BatchManager()

# 배치 실행 (알림 자동 전송)
result = batch_manager.run_single_step(
    step=1,
    accounts=['account_1'],
    quantity=100
)
```

### 수동 알림 전송

```python
from telegram_notifier import TelegramNotifier

notifier = TelegramNotifier(
    bot_token="YOUR_BOT_TOKEN_HERE",
    chat_id="7918845682"
)

# 사용자 정의 알림
notifier.send_custom_notification(
    title="중요한 알림",
    content="특별한 상황이 발생했습니다.",
    emoji="🚨"
)
```

## 문제 해결

### 1. 알림이 오지 않는 경우

- 봇 토큰이 올바른지 확인
- 채팅 ID가 올바른지 확인
- 봇과 대화를 시작했는지 확인
- 설정 파일에서 `enabled`가 `true`인지 확인

### 2. 연결 테스트 실패

- 인터넷 연결 상태 확인
- 방화벽 설정 확인
- 텔레그램 API 서버 상태 확인

### 3. 봇 토큰 오류

- BotFather에서 새 봇 생성
- 토큰 복사 시 공백이나 특수문자 포함 여부 확인

### 4. 채팅 ID 확인 안됨

- 봇과 대화를 먼저 시작했는지 확인
- `/start` 명령어 또는 아무 메시지 전송 후 getUpdates API 호출

## 보안 고려사항

1. **봇 토큰 보안**: 봇 토큰을 코드에 직접 하드코딩하지 말고 설정 파일이나 환경변수 사용
2. **설정 파일 관리**: 설정 파일을 Git에 커밋하지 않도록 `.gitignore`에 추가
3. **채팅 ID 관리**: 개인 채팅 ID는 외부에 노출되지 않도록 주의

## 추가 기능

### 다중 사용자 알림

여러 사용자에게 알림을 보내려면 각 사용자의 채팅 ID를 배열로 설정:

```json
{
  "telegram": {
    "enabled": true,
    "bot_token": "YOUR_BOT_TOKEN_HERE",
    "chat_ids": ["7918845682", "1234567890"],
    "notify_start": true,
    "notify_complete": true,
    "notify_error": true,
    "notify_warning": true
  }
}
```

### 그룹 채팅 알림

1. 봇을 그룹 채팅에 추가
2. 그룹 채팅 ID 확인 (음수 값)
3. 설정 파일에 그룹 채팅 ID 입력

## 참고 자료

- [텔레그램 봇 API 문서](https://core.telegram.org/bots/api)
- [BotFather 가이드](https://core.telegram.org/bots#6-botfather)
- [텔레그램 봇 생성 튜토리얼](https://core.telegram.org/bots/tutorial)