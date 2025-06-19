#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
모달창 처리 문제 분석 스크립트

브라우저를 실행하지 않고 모달창 처리 로직의 문제점을 분석합니다.
"""

import sys
import os
import logging
import importlib
import inspect

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('analyze_modal_issue.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def analyze_modal_handler_imports():
    """
    모달 처리 관련 import 체인을 분석합니다.
    """
    logger.info("=== 모달 처리 import 체인 분석 시작 ===")
    
    try:
        # 1. core.common.modal_handler 분석
        logger.info("1. core.common.modal_handler 분석")
        try:
            from core.common import modal_handler
            logger.info(f"modal_handler 모듈 로드 성공: {modal_handler.__file__}")
            
            # handle_post_login_modals 함수 확인
            if hasattr(modal_handler, 'handle_post_login_modals'):
                func = modal_handler.handle_post_login_modals
                logger.info(f"handle_post_login_modals 함수 발견: {func}")
                
                # 함수 소스 코드 확인
                try:
                    source = inspect.getsource(func)
                    logger.info(f"함수 소스 코드 (처음 500자): {source[:500]}...")
                except Exception as e:
                    logger.warning(f"소스 코드 확인 실패: {e}")
            else:
                logger.error("handle_post_login_modals 함수를 찾을 수 없습니다")
                
        except ImportError as e:
            logger.error(f"modal_handler 모듈 import 실패: {e}")
        except Exception as e:
            logger.error(f"modal_handler 분석 중 오류: {e}")
        
        # 2. percenty_utils 분석
        logger.info("2. percenty_utils 분석")
        try:
            import percenty_utils
            logger.info(f"percenty_utils 모듈 로드 성공: {percenty_utils.__file__}")
            
            # hide_login_modal import 확인
            if hasattr(percenty_utils, 'hide_login_modal'):
                logger.info("percenty_utils에서 hide_login_modal 발견")
            else:
                logger.warning("percenty_utils에서 hide_login_modal을 찾을 수 없습니다")
                
        except ImportError as e:
            logger.error(f"percenty_utils 모듈 import 실패: {e}")
        except Exception as e:
            logger.error(f"percenty_utils 분석 중 오류: {e}")
        
        # 3. login_modal_utils 분석
        logger.info("3. login_modal_utils 분석")
        try:
            import login_modal_utils
            logger.info(f"login_modal_utils 모듈 로드 성공: {login_modal_utils.__file__}")
            
            # hide_login_modal 함수 확인
            if hasattr(login_modal_utils, 'hide_login_modal'):
                func = login_modal_utils.hide_login_modal
                logger.info(f"hide_login_modal 함수 발견: {func}")
                
                # 전역 변수 확인
                if hasattr(login_modal_utils, 'login_modal_hidden'):
                    logger.info(f"login_modal_hidden 전역 변수: {login_modal_utils.login_modal_hidden}")
                else:
                    logger.warning("login_modal_hidden 전역 변수를 찾을 수 없습니다")
                    
                if hasattr(login_modal_utils, 'last_login_modal_attempt'):
                    logger.info(f"last_login_modal_attempt 전역 변수: {login_modal_utils.last_login_modal_attempt}")
                else:
                    logger.warning("last_login_modal_attempt 전역 변수를 찾을 수 없습니다")
                    
            else:
                logger.error("hide_login_modal 함수를 찾을 수 없습니다")
                
        except ImportError as e:
            logger.error(f"login_modal_utils 모듈 import 실패: {e}")
        except Exception as e:
            logger.error(f"login_modal_utils 분석 중 오류: {e}")
        
        # 4. modal_blocker 분석
        logger.info("4. modal_blocker 분석")
        try:
            import modal_blocker
            logger.info(f"modal_blocker 모듈 로드 성공: {modal_blocker.__file__}")
            
            # block_modals_on_page 함수 확인
            if hasattr(modal_blocker, 'block_modals_on_page'):
                logger.info("block_modals_on_page 함수 발견")
            else:
                logger.warning("block_modals_on_page 함수를 찾을 수 없습니다")
                
        except ImportError as e:
            logger.error(f"modal_blocker 모듈 import 실패: {e}")
        except Exception as e:
            logger.error(f"modal_blocker 분석 중 오류: {e}")
        
        # 5. channel_talk_utils 분석
        logger.info("5. channel_talk_utils 분석")
        try:
            import channel_talk_utils
            logger.info(f"channel_talk_utils 모듈 로드 성공: {channel_talk_utils.__file__}")
            
            # check_and_hide_channel_talk 함수 확인
            if hasattr(channel_talk_utils, 'check_and_hide_channel_talk'):
                logger.info("check_and_hide_channel_talk 함수 발견")
            else:
                logger.warning("check_and_hide_channel_talk 함수를 찾을 수 없습니다")
                
        except ImportError as e:
            logger.error(f"channel_talk_utils 모듈 import 실패: {e}")
        except Exception as e:
            logger.error(f"channel_talk_utils 분석 중 오류: {e}")
        
        logger.info("=== 모달 처리 import 체인 분석 완료 ===")
        return True
        
    except Exception as e:
        logger.error(f"전체 분석 중 오류: {e}")
        import traceback
        logger.error(f"상세 오류: {traceback.format_exc()}")
        return False

def analyze_step2_1_core_modal_methods():
    """
    Step2_1Core의 모달 처리 메서드들을 분석합니다.
    """
    logger.info("=== Step2_1Core 모달 처리 메서드 분석 시작 ===")
    
    try:
        from core.steps.step2_1_core import Step2_1Core
        logger.info(f"Step2_1Core 클래스 로드 성공")
        
        # _handle_post_login_modals 메서드 확인
        if hasattr(Step2_1Core, '_handle_post_login_modals'):
            method = Step2_1Core._handle_post_login_modals
            logger.info(f"_handle_post_login_modals 메서드 발견: {method}")
            
            try:
                source = inspect.getsource(method)
                logger.info(f"_handle_post_login_modals 소스 코드: {source}")
            except Exception as e:
                logger.warning(f"_handle_post_login_modals 소스 코드 확인 실패: {e}")
        else:
            logger.error("_handle_post_login_modals 메서드를 찾을 수 없습니다")
        
        # _hide_channel_talk 메서드 확인
        if hasattr(Step2_1Core, '_hide_channel_talk'):
            method = Step2_1Core._hide_channel_talk
            logger.info(f"_hide_channel_talk 메서드 발견: {method}")
            
            try:
                source = inspect.getsource(method)
                logger.info(f"_hide_channel_talk 소스 코드: {source}")
            except Exception as e:
                logger.warning(f"_hide_channel_talk 소스 코드 확인 실패: {e}")
        else:
            logger.error("_hide_channel_talk 메서드를 찾을 수 없습니다")
        
        # execute_step2_1 메서드에서 모달 처리 부분 확인
        if hasattr(Step2_1Core, 'execute_step2_1'):
            method = Step2_1Core.execute_step2_1
            logger.info(f"execute_step2_1 메서드 발견: {method}")
            
            try:
                source = inspect.getsource(method)
                # 모달 처리 관련 부분만 추출
                lines = source.split('\n')
                modal_lines = []
                in_modal_section = False
                
                for line in lines:
                    if '_handle_post_login_modals' in line or '_hide_channel_talk' in line:
                        in_modal_section = True
                        modal_lines.append(line)
                    elif in_modal_section and (line.strip() == '' or line.startswith('        ')):
                        modal_lines.append(line)
                    elif in_modal_section:
                        break
                
                if modal_lines:
                    logger.info(f"execute_step2_1의 모달 처리 부분:\n{''.join(modal_lines)}")
                else:
                    logger.warning("execute_step2_1에서 모달 처리 부분을 찾을 수 없습니다")
                    
            except Exception as e:
                logger.warning(f"execute_step2_1 소스 코드 확인 실패: {e}")
        else:
            logger.error("execute_step2_1 메서드를 찾을 수 없습니다")
        
        logger.info("=== Step2_1Core 모달 처리 메서드 분석 완료 ===")
        return True
        
    except ImportError as e:
        logger.error(f"Step2_1Core import 실패: {e}")
        return False
    except Exception as e:
        logger.error(f"Step2_1Core 분석 중 오류: {e}")
        import traceback
        logger.error(f"상세 오류: {traceback.format_exc()}")
        return False

def analyze_batch_manager_step21_execution():
    """
    BatchManager의 Step 21 실행 부분을 분석합니다.
    """
    logger.info("=== BatchManager Step 21 실행 부분 분석 시작 ===")
    
    try:
        from batch.batch_manager import BatchManager
        logger.info(f"BatchManager 클래스 로드 성공")
        
        # _execute_step_for_account 메서드 확인
        if hasattr(BatchManager, '_execute_step_for_account'):
            method = BatchManager._execute_step_for_account
            logger.info(f"_execute_step_for_account 메서드 발견: {method}")
            
            try:
                source = inspect.getsource(method)
                # Step 21 관련 부분만 추출
                lines = source.split('\n')
                step21_lines = []
                in_step21_section = False
                
                for line in lines:
                    if 'step == 21' in line or 'Step2_1Core' in line:
                        in_step21_section = True
                        step21_lines.append(line)
                    elif in_step21_section and (line.strip() == '' or line.startswith('        ') or line.startswith('            ')):
                        step21_lines.append(line)
                    elif in_step21_section and ('elif' in line or 'else:' in line or 'except' in line):
                        break
                
                if step21_lines:
                    logger.info(f"BatchManager의 Step 21 실행 부분:\n{''.join(step21_lines)}")
                else:
                    logger.warning("BatchManager에서 Step 21 실행 부분을 찾을 수 없습니다")
                    
            except Exception as e:
                logger.warning(f"_execute_step_for_account 소스 코드 확인 실패: {e}")
        else:
            logger.error("_execute_step_for_account 메서드를 찾을 수 없습니다")
        
        logger.info("=== BatchManager Step 21 실행 부분 분석 완료 ===")
        return True
        
    except ImportError as e:
        logger.error(f"BatchManager import 실패: {e}")
        return False
    except Exception as e:
        logger.error(f"BatchManager 분석 중 오류: {e}")
        import traceback
        logger.error(f"상세 오류: {traceback.format_exc()}")
        return False

def check_modal_processing_flow():
    """
    모달 처리 플로우를 종합적으로 확인합니다.
    """
    logger.info("=== 모달 처리 플로우 종합 확인 시작 ===")
    
    # 1. Import 체인 확인
    logger.info("1. Import 체인 확인")
    import_success = analyze_modal_handler_imports()
    
    # 2. Step2_1Core 메서드 확인
    logger.info("2. Step2_1Core 메서드 확인")
    step_core_success = analyze_step2_1_core_modal_methods()
    
    # 3. BatchManager 실행 부분 확인
    logger.info("3. BatchManager 실행 부분 확인")
    batch_manager_success = analyze_batch_manager_step21_execution()
    
    # 4. 종합 결과
    logger.info("=== 모달 처리 플로우 종합 확인 결과 ===")
    logger.info(f"Import 체인 확인: {'성공' if import_success else '실패'}")
    logger.info(f"Step2_1Core 메서드 확인: {'성공' if step_core_success else '실패'}")
    logger.info(f"BatchManager 실행 부분 확인: {'성공' if batch_manager_success else '실패'}")
    
    if import_success and step_core_success and batch_manager_success:
        logger.info("모든 모달 처리 컴포넌트가 정상적으로 로드되었습니다.")
        logger.info("문제는 런타임 실행 과정에서 발생하는 것으로 보입니다.")
        
        # 가능한 원인 분석
        logger.info("=== 가능한 원인 분석 ===")
        logger.info("1. 브라우저 드라이버 초기화 문제")
        logger.info("2. 페이지 로드 타이밍 문제")
        logger.info("3. JavaScript 실행 환경 문제")
        logger.info("4. 모달창 요소 선택자 변경")
        logger.info("5. 네트워크 연결 문제")
        logger.info("6. 브라우저 권한 문제")
        
        # 권장 해결 방안
        logger.info("=== 권장 해결 방안 ===")
        logger.info("1. 브라우저 초기화 후 충분한 대기 시간 추가")
        logger.info("2. 모달 처리 전 페이지 로드 완료 확인")
        logger.info("3. JavaScript 실행 가능 여부 사전 확인")
        logger.info("4. 모달창 요소 존재 여부 사전 확인")
        logger.info("5. 예외 처리 강화 및 상세 로깅 추가")
        logger.info("6. 브라우저 재시작 로직 개선")
        
    else:
        logger.error("모달 처리 컴포넌트에 문제가 있습니다.")
        logger.error("Import 오류나 메서드 누락을 먼저 해결해야 합니다.")
    
    logger.info("=== 모달 처리 플로우 종합 확인 완료 ===")

if __name__ == "__main__":
    print("모달창 처리 문제 분석 스크립트")
    print("브라우저를 실행하지 않고 코드 레벨에서 문제를 분석합니다.")
    
    check_modal_processing_flow()
    
    print("\n분석 완료. 로그 파일 'analyze_modal_issue.log'를 확인하세요.")