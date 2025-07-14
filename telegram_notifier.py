import requests
import json
from datetime import datetime
import logging

class TelegramNotifier:
    """
    텔레그램 봇을 통한 알림 전송 클래스
    """
    
    def __init__(self, bot_token, chat_id):
        """
        텔레그램 알림 초기화
        
        Args:
            bot_token (str): 텔레그램 봇 토큰
            chat_id (str): 채팅 ID
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        
        # 로깅 설정
        self.logger = logging.getLogger(__name__)
        
    def send_message(self, message, parse_mode='HTML'):
        """
        텔레그램 메시지 전송
        
        Args:
            message (str): 전송할 메시지
            parse_mode (str): 메시지 파싱 모드 (HTML, Markdown)
            
        Returns:
            bool: 전송 성공 여부
        """
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                self.logger.info(f"텔레그램 메시지 전송 성공: {message[:50]}...")
                return True
            else:
                self.logger.error(f"텔레그램 메시지 전송 실패: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"텔레그램 메시지 전송 중 오류: {str(e)}")
            return False
    
    def send_batch_start_notification(self, account_email, step_name, server_name):
        """
        배치 작업 시작 알림
        
        Args:
            account_email (str): 계정 이메일
            step_name (str): 단계명
            server_name (str): 서버명
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"""
🚀 <b>배치 작업 시작</b>

📧 계정: {account_email}
📋 단계: {step_name}
🖥️ 서버: {server_name}
⏰ 시작 시간: {timestamp}

작업이 시작되었습니다.
        """
        return self.send_message(message)
    
    def send_batch_complete_notification(self, account_email, step_name, server_name, duration_minutes):
        """
        배치 작업 완료 알림
        
        Args:
            account_email (str): 계정 이메일
            step_name (str): 단계명
            server_name (str): 서버명
            duration_minutes (float): 소요 시간(분)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"""
✅ <b>배치 작업 완료</b>

📧 계정: {account_email}
📋 단계: {step_name}
🖥️ 서버: {server_name}
⏰ 완료 시간: {timestamp}
⏱️ 소요 시간: {duration_minutes:.1f}분

작업이 성공적으로 완료되었습니다.
        """
        return self.send_message(message)
    
    def send_batch_error_notification(self, account_email, step_name, server_name, error_message):
        """
        배치 작업 오류 알림
        
        Args:
            account_email (str): 계정 이메일
            step_name (str): 단계명
            server_name (str): 서버명
            error_message (str): 오류 메시지
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"""
❌ <b>배치 작업 오류 발생</b>

📧 계정: {account_email}
📋 단계: {step_name}
🖥️ 서버: {server_name}
⏰ 오류 시간: {timestamp}

🚨 <b>오류 내용:</b>
{error_message[:500]}...

즉시 확인이 필요합니다.
        """
        return self.send_message(message)
    
    def send_batch_warning_notification(self, account_email, step_name, server_name, warning_message):
        """
        배치 작업 경고 알림
        
        Args:
            account_email (str): 계정 이메일
            step_name (str): 단계명
            server_name (str): 서버명
            warning_message (str): 경고 메시지
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"""
⚠️ <b>배치 작업 경고</b>

📧 계정: {account_email}
📋 단계: {step_name}
🖥️ 서버: {server_name}
⏰ 경고 시간: {timestamp}

⚠️ <b>경고 내용:</b>
{warning_message[:500]}...

확인을 권장합니다.
        """
        return self.send_message(message)
    
    def send_custom_notification(self, title, content, emoji="📢"):
        """
        사용자 정의 알림
        
        Args:
            title (str): 알림 제목
            content (str): 알림 내용
            emoji (str): 이모지
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"""
{emoji} <b>{title}</b>

{content}

⏰ 시간: {timestamp}
        """
        return self.send_message(message)
    
    def test_connection(self):
        """
        텔레그램 봇 연결 테스트
        
        Returns:
            bool: 연결 성공 여부
        """
        test_message = "🔧 텔레그램 알림 시스템 연결 테스트"
        return self.send_message(test_message)


# 사용 예시
if __name__ == "__main__":
    # 텔레그램 봇 설정 (실제 사용 시 환경변수나 설정 파일에서 로드)
    BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # 실제 봇 토큰으로 교체
    CHAT_ID = "7918845682"  # 확인된 채팅 ID
    
    # 알림 객체 생성
    notifier = TelegramNotifier(BOT_TOKEN, CHAT_ID)
    
    # 연결 테스트
    if notifier.test_connection():
        print("텔레그램 알림 시스템이 정상적으로 설정되었습니다.")
    else:
        print("텔레그램 알림 시스템 설정에 문제가 있습니다.")