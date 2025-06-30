#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
퍼센티 동적 업로드 테스트 스크립트

percenty_id.xlsx의 market_id 시트를 기반으로 동적 업로드를 테스트합니다.
기존 percenty_new_step6_1.py의 로그인 방식을 참고하여 안정적인 테스트 환경을 제공합니다.
"""

import sys
import time
import logging
import traceback
from pathlib import Path

# 로깅 설정 (디버깅 완료 후 파일 로깅 비활성화)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        # logging.FileHandler('dynamic_upload_test.log', encoding='utf-8')  # 디버깅 완료로 주석처리
    ]
)

logger = logging.getLogger(__name__)

def main():
    """
    메인 실행 함수
    """
    login = None
    
    try:
        print("\n" + "=" * 60)
        print("퍼센티 동적 업로드 테스트 시작")
        print("=" * 60)
        
        # 순환 임포트 문제 해결을 위해 동적 임포트 사용
        from login_percenty import PercentyLogin
        from account_manager import AccountManager
        from product_editor_core6_dynamic_3 import ProductEditorCore6_Dynamic3
        
        # 1. 계정 관리자 초기화
        print("\n1. 계정 관리자 초기화...")
        account_manager = AccountManager()
        
        # 2. 계정 정보 로드
        print("2. 계정 정보 로드...")
        if not account_manager.load_accounts():
            print("❌ 계정 정보를 로드할 수 없습니다. 프로그램을 종료합니다.")
            sys.exit(1)
        
        # 3. 계정 선택
        print("3. 계정 선택...")
        selected_account = account_manager.select_account()
        if not selected_account:
            print("❌ 계정을 선택하지 않았습니다. 프로그램을 종료합니다.")
            sys.exit(0)
        
        # 4. 선택한 계정으로 로그인 객체 생성
        print(f"\n4. 로그인 객체 생성...")
        print(f"   선택한 계정: {selected_account.get('nickname', selected_account['id'])}")
        login = PercentyLogin(account=selected_account)
        
        # 5. 웹드라이버 설정
        print("5. 웹드라이버 설정...")
        if not login.setup_driver():
            print("❌ 웹드라이버 설정 실패")
            sys.exit(1)
        
        # 6. 로그인 시도
        print("6. 로그인 시도...")
        if not login.login():
            print("❌ 로그인 실패")
            sys.exit(1)
        
        print("✅ 로그인 성공!")
        
        # 7. AI 소싱 메뉴 클릭
        print("7. AI 소싱 메뉴 클릭...")
        if not login.click_product_aisourcing_button_improved():
            print("❌ AI 소싱 메뉴 클릭 실패")
            sys.exit(1)
        
        print("✅ AI 소싱 메뉴 클릭 성공!")
        
        # 8. 채널톡 및 로그인 모달창 숨기기
        print("8. 채널톡 및 로그인 모달창 숨기기...")
        try:
            from percenty_utils import hide_channel_talk_and_modals
            result = hide_channel_talk_and_modals(login.driver, log_prefix="동적 업로드 테스트")
            print(f"✅ 채널톡 및 로그인 모달창 숨기기 결과: {result}")
        except Exception as e:
            print(f"⚠️ 채널톡 숨기기 중 오류 (계속 진행): {e}")
        
        # 9. 동적 업로드 코어 초기화
        print("\n9. 동적 업로드 코어 초기화...")
        account_id = selected_account.get('id', selected_account.get('nickname', 'unknown'))
        print(f"   계정 ID: {account_id}")
        dynamic_core = ProductEditorCore6_Dynamic3(login.driver, account_id)
        
        # 10. 신규상품등록 화면으로 전환
        print("\n10. 신규상품등록 화면으로 전환...")
        if not login.click_product_register():
            print("❌ 신규상품등록 화면 전환 실패")
            sys.exit(1)
        
        print("✅ 신규상품등록 화면 전환 성공!")
        
        """
        # 10-1. 퍼센티 확장프로그램 설치
        print("\n10-1. 퍼센티 확장프로그램 설치...")
        if not dynamic_core._install_percenty_extension():
            print("⚠️ 퍼센티 확장프로그램 설치 실패, 계속 진행합니다")
        else:
            print("✅ 퍼센티 확장프로그램 설치 성공!")
        """
        
        # 11. 동적 업로드 워크플로우 실행
        print("\n11. 동적 업로드 워크플로우 실행...")
        print("    percenty_id.xlsx의 market_id 시트를 기반으로 12번 순환 업로드를 진행합니다.")
        print("    각 설정별로 그룹 선택 → 상품 업로드 과정을 반복합니다.")
        
        if dynamic_core.execute_dynamic_upload_workflow():
            print("\n" + "=" * 60)
            print("🎉 동적 업로드 워크플로우 성공!")
            print("    모든 마켓 설정에 대한 업로드가 완료되었습니다.")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("❌ 동적 업로드 워크플로우 실패")
            print("    일부 또는 전체 마켓 설정 처리에 실패했습니다.")
            print("    자세한 내용은 로그를 확인하세요.")
            print("=" * 60)
        
        # 12. 무한 대기 (사용자가 Ctrl+C를 누를 때까지)
        print("\n종료하려면 Ctrl+C를 누르세요.")
        try:
            while True:
                time.sleep(10)  # 10초마다 한 번씩 체크
        except KeyboardInterrupt:
            print("\n\n" + "=" * 60)
            print("사용자가 스크립트를 종료했습니다.")
            print("=" * 60)
    
    except ImportError as e:
        logger.error(f"임포트 오류 발생: {e}")
        print(f"\n❌ 임포트 오류 발생: {e}")
        print("필요한 모듈을 임포트할 수 없습니다.")
        print("순환 임포트 문제가 발생했을 수 있습니다.")
        sys.exit(1)
    
    except Exception as e:
        logger.error(f"테스트 중 오류 발생: {e}")
        logger.error(f"스택 트레이스: {traceback.format_exc()}")
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        print("자세한 내용은 dynamic_upload_test.log 파일을 확인하세요.")
    
    finally:
        # 종료 시 브라우저 닫기
        if login and hasattr(login, 'driver') and login.driver:
            try:
                print("\n브라우저 종료 중...")
                login.close_driver()
                logger.info("WebDriver 종료 완료")
                print("✅ 브라우저 종료 완료")
            except Exception as e:
                logger.error(f"WebDriver 종료 중 오류: {e}")
                print(f"⚠️ 브라우저 종료 중 오류: {e}")
        
        if 'dynamic_core' in locals():
            print("=== 퍼센티 동적 업로드 테스트 완료 ===")
        else:
            print("=== 퍼센티 동적 업로드 테스트 실패 ===")

if __name__ == "__main__":
    main()