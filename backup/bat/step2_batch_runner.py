# -*- coding: utf-8 -*-
"""
퍼센티 Step 2 배치 실행기
새로운 Step2 Core 파일들을 사용하여 서버별 배치 처리 수행
"""

import os
import sys
import time
import logging
import traceback
from typing import Dict, List, Optional

# 루트 디렉토리를 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 브라우저 설정 임포트
from browser_core import BrowserCore

# 계정 관리자 임포트
from account_manager import AccountManager

# Step 2 코어 기능 임포트
from core.steps.step2_1_core import Step2_1Core
from core.steps.step2_2_core import Step2_2Core
from core.steps.step2_3_core import Step2_3Core

# 로그인 기능 임포트
from login_percenty import PercentyLogin

# 공통 유틸리티 임포트
from percenty_utils import hide_channel_talk_and_modals, periodic_ui_cleanup

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('step2_batch_runner.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Step2BatchRunner:
    """
    Step 2 배치 실행기
    서버별로 독립적인 배치 처리 수행
    """
    
    def __init__(self):
        self.driver = None
        self.browser_core = None
        self.current_account_id = None
        self.step_cores = {
            "서버1": None,
            "서버2": None,
            "서버3": None
        }
        
    def setup_browser(self) -> bool:
        """
        브라우저 설정 및 초기화
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("브라우저 설정 시작")
            
            # PercentyLogin 클래스를 사용하여 브라우저 설정
            login_handler = PercentyLogin()
            if not login_handler.setup_driver():
                logger.error("브라우저 설정 실패")
                return False
            
            self.driver = login_handler.driver
            self.browser_core = BrowserCore()
            self.browser_core.driver = self.driver
            
            logger.info("브라우저 설정 완료")
            return True
            
        except Exception as e:
            logger.error(f"브라우저 설정 실패: {e}")
            return False
    
    def login_and_navigate(self, account_info: Dict) -> bool:
        """
        로그인 및 등록상품관리 페이지로 이동
        
        Args:
            account_info: 계정 정보
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"계정 {account_info['id']} 로그인 시작")
            
            # 현재 계정 ID 저장
            self.current_account_id = account_info['id']
            
            # 로그인 수행
            login_handler = PercentyLogin(driver=self.driver, account=account_info)
            if not login_handler.login():
                logger.error("로그인 실패")
                return False
            
            logger.info("로그인 성공")
            
            # 등록상품관리 메뉴로 이동
            if not self._navigate_to_product_management():
                logger.error("등록상품관리 메뉴 이동 실패")
                return False
            
            logger.info("등록상품관리 페이지 이동 완료")
            return True
            
        except Exception as e:
            logger.error(f"로그인 및 페이지 이동 중 오류: {e}")
            return False
    
    def _navigate_to_product_management(self) -> bool:
        """
        등록상품관리 메뉴로 이동
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("등록상품관리 메뉴로 이동")
            
            # 등록상품관리 메뉴 클릭 (DOM 선택자 우선 사용)
            from ui_elements import UI_ELEMENTS
            from click_utils import smart_click
            from timesleep import DELAY_MEDIUM
            
            product_manage_element = UI_ELEMENTS["PRODUCT_MANAGE"]
            success = smart_click(self.driver, product_manage_element, DELAY_MEDIUM)
            
            if not success:
                logger.warning("DOM 선택자로 등록상품관리 메뉴 클릭 실패, 좌표 방식으로 재시도")
                # 좌표 방식으로 폴백
                from coordinates.coordinates_all import MENU
                from coordinates.coordinate_conversion import convert_coordinates
                
                x, y = MENU["PRODUCT_MANAGE"]
                inner_width = self.driver.execute_script("return window.innerWidth;")
                converted_x, converted_y = convert_coordinates(x, y, inner_width)
                
                from selenium.webdriver.common.action_chains import ActionChains
                actions = ActionChains(self.driver)
                actions.move_by_offset(converted_x, converted_y).click().perform()
                
                # 원점으로 마우스 이동
                actions.move_by_offset(-converted_x, -converted_y).perform()
            
            # 페이지 로딩 대기
            time.sleep(DELAY_MEDIUM)
            
            # 채널톡 및 모달 숨기기
            hide_channel_talk_and_modals(self.driver)
            
            logger.info("등록상품관리 메뉴 이동 완료")
            return True
            
        except Exception as e:
            logger.error(f"등록상품관리 메뉴 이동 중 오류: {e}")
            return False
    
    def setup_step_cores(self, account_info: Dict) -> bool:
        """
        서버별 Step Core 객체들 설정
        
        Args:
            account_info: 계정 정보
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("서버별 Step Core 객체들 설정 시작")
            
            # 드라이버 준비 상태 확인
            if not self.driver:
                logger.error("드라이버가 설정되지 않았습니다")
                return False
                
            # 드라이버 연결 상태 확인
            try:
                self.driver.current_url
                logger.info("드라이버 연결 상태 확인 완료")
            except Exception as e:
                logger.error(f"드라이버 연결 상태 확인 실패: {e}")
                return False
            
            # 서버1 코어 설정
            self.step_cores["서버1"] = Step2_1Core(driver=self.driver, server_name="서버1", restart_browser_callback=self.restart_browser)
            logger.info("서버1 코어 설정 완료")
            
            # 서버2 코어 설정
            self.step_cores["서버2"] = Step2_2Core(driver=self.driver, server_name="서버2", restart_browser_callback=self.restart_browser)
            logger.info("서버2 코어 설정 완료")
            
            # 서버3 코어 설정
            self.step_cores["서버3"] = Step2_3Core(driver=self.driver, server_name="서버3", restart_browser_callback=self.restart_browser)
            logger.info("서버3 코어 설정 완료")
            
            logger.info("모든 서버 코어 설정 완료")
            return True
            
        except Exception as e:
            logger.error(f"Step Core 객체 설정 중 오류: {e}")
            return False
    
    def run_batch_processing(self, account_info: Dict, server_name: str = None, chunk_size: int = 5, reset_progress: bool = True) -> Dict:
        """
        배치 처리 실행
        
        Args:
            account_info: 계정 정보
            server_name: 특정 서버만 처리 (None이면 모든 서버)
            chunk_size: 청크 크기
            reset_progress: 진행 상황 초기화 여부 (기본값: True)
            
        Returns:
            Dict: 처리 결과
        """
        total_result = {
            'success': False,
            'servers_processed': 0,
            'servers_failed': 0,
            'total_keywords_processed': 0,
            'total_products_processed': 0,
            'server_results': {},
            'errors': []
        }
        
        try:
            logger.info(f"배치 처리 시작 - 계정: {account_info['id']}, 서버: {server_name or '전체'}, 청크 크기: {chunk_size}")
            
            # 진행 상황 초기화 (옵션)
            if reset_progress:
                self._reset_progress_files(account_info, server_name)
            
            # 처리할 서버 목록 결정
            servers_to_process = [server_name] if server_name else ["서버1", "서버2", "서버3"]
            
            for server in servers_to_process:
                try:
                    logger.info(f"===== {server} 배치 처리 시작 =====")
                    
                    # 해당 서버의 코어 가져오기
                    step_core = self.step_cores.get(server)
                    if not step_core:
                        error_msg = f"{server} 코어가 설정되지 않았습니다"
                        logger.error(error_msg)
                        total_result['errors'].append(error_msg)
                        total_result['servers_failed'] += 1
                        continue
                    
                    # 해당 서버의 키워드 목록 가져오기
                    provider_codes = self._get_provider_codes_for_server(account_info, server)
                    
                    if not provider_codes:
                        logger.info(f"{server}에 처리할 키워드가 없습니다")
                        total_result['server_results'][server] = {
                            'success': True,
                            'processed_keywords': 0,
                            'message': '처리할 키워드 없음'
                        }
                        total_result['servers_processed'] += 1
                        continue
                    
                    logger.info(f"{server} 처리 예정 키워드: {len(provider_codes)}개 - {provider_codes}")
                    
                    # 서버별 배치 처리 실행 (브라우저 재시작 지원)
                    server_result = None
                    remaining_keywords = provider_codes.copy()
                    
                    while remaining_keywords:
                        if server == "서버1":
                            current_result = step_core.execute_step2_1_with_browser_restart(
                                provider_codes=remaining_keywords,
                                chunk_size=chunk_size,
                                account_info=account_info
                            )
                        elif server == "서버2":
                            current_result = step_core.execute_step2_2_with_browser_restart(
                                provider_codes=remaining_keywords,
                                chunk_size=chunk_size,
                                account_info=account_info
                            )
                        else:
                            current_result = step_core.execute_step2_3_with_browser_restart(
                                provider_codes=remaining_keywords,
                                chunk_size=chunk_size,
                                account_info=account_info
                            )
                        
                        # 브라우저 재시작이 필요한 경우
                        if current_result.get('restart_required', False):
                            logger.info(f"{server} - 청크 완료 후 브라우저 재시작 실행")
                            
                            # 현재까지의 결과 저장
                            if server_result is None:
                                server_result = current_result.get('current_result', {})
                            else:
                                # 결과 누적
                                server_result['processed_keywords'] += current_result.get('current_result', {}).get('processed_keywords', 0)
                                server_result['failed_keywords'] += current_result.get('current_result', {}).get('failed_keywords', 0)
                                server_result['total_products_processed'] += current_result.get('current_result', {}).get('total_products_processed', 0)
                                if current_result.get('current_result', {}).get('errors'):
                                    server_result.setdefault('errors', []).extend(current_result['current_result']['errors'])
                                if current_result.get('current_result', {}).get('completed_keywords'):
                                    server_result.setdefault('completed_keywords', []).extend(current_result['current_result']['completed_keywords'])
                                if current_result.get('current_result', {}).get('failed_keywords_list'):
                                    server_result.setdefault('failed_keywords_list', []).extend(current_result['current_result']['failed_keywords_list'])
                            
                            # 브라우저 재시작
                            if not self.restart_browser():
                                logger.error(f"{server} - 브라우저 재시작 실패")
                                break
                            
                            # 남은 키워드 계산 (완료된 키워드 제외)
                            completed_keywords = server_result.get('completed_keywords', [])
                            remaining_keywords = [k for k in remaining_keywords if k not in completed_keywords]
                            
                            logger.info(f"{server} - 브라우저 재시작 완료, 남은 키워드: {len(remaining_keywords)}개")
                        else:
                            # 재시작이 필요하지 않은 경우 (모든 청크 완료)
                            if server_result is None:
                                server_result = current_result
                            else:
                                # 마지막 청크 결과도 누적
                                server_result['processed_keywords'] += current_result.get('processed_keywords', 0)
                                server_result['failed_keywords'] += current_result.get('failed_keywords', 0)
                                server_result['total_products_processed'] += current_result.get('total_products_processed', 0)
                                if current_result.get('errors'):
                                    server_result.setdefault('errors', []).extend(current_result['errors'])
                                if current_result.get('completed_keywords'):
                                    server_result.setdefault('completed_keywords', []).extend(current_result['completed_keywords'])
                                if current_result.get('failed_keywords_list'):
                                    server_result.setdefault('failed_keywords_list', []).extend(current_result['failed_keywords_list'])
                                # 성공 여부는 모든 키워드가 성공적으로 처리되었는지로 판단
                                server_result['success'] = server_result['processed_keywords'] > 0 and server_result['failed_keywords'] == 0
                            break
                    
                    # 결과 저장
                    total_result['server_results'][server] = server_result
                    
                    if server_result.get('success', False):
                        total_result['servers_processed'] += 1
                        total_result['total_keywords_processed'] += server_result.get('processed_keywords', 0)
                        total_result['total_products_processed'] += server_result.get('total_products_processed', 0)
                        logger.info(f"{server} 배치 처리 성공 - 처리된 키워드: {server_result.get('processed_keywords', 0)}개")
                    else:
                        total_result['servers_failed'] += 1
                        if server_result.get('errors'):
                            total_result['errors'].extend(server_result['errors'])
                        logger.error(f"{server} 배치 처리 실패")
                    
                    logger.info(f"===== {server} 배치 처리 완료 =====")
                    
                except Exception as e:
                    error_msg = f"{server} 배치 처리 중 오류: {str(e)}"
                    logger.error(error_msg)
                    total_result['errors'].append(error_msg)
                    total_result['servers_failed'] += 1
                    total_result['server_results'][server] = {
                        'success': False,
                        'error': str(e)
                    }
            
            # 전체 성공 여부 판단
            total_result['success'] = total_result['servers_processed'] > 0 and total_result['servers_failed'] == 0
            
            logger.info(f"배치 처리 완료 - 성공한 서버: {total_result['servers_processed']}, 실패한 서버: {total_result['servers_failed']}")
            logger.info(f"총 처리된 키워드: {total_result['total_keywords_processed']}, 총 처리된 상품: {total_result['total_products_processed']}")
            
        except Exception as e:
            error_msg = f"배치 처리 중 치명적 오류: {str(e)}"
            logger.error(error_msg)
            total_result['errors'].append(error_msg)
            total_result['success'] = False
        
        return total_result
    
    def _get_provider_codes_for_server(self, account_info: Dict, server_name: str) -> List[str]:
        """
        특정 서버에 대한 키워드 목록 가져오기
        
        Args:
            account_info: 계정 정보
            server_name: 서버 이름
            
        Returns:
            List[str]: 키워드 목록
        """
        try:
            # ProductEditorCore2를 임시로 생성하여 작업 목록 로드
            from product_editor_core2 import ProductEditorCore2
            temp_core = ProductEditorCore2(self.driver)
            
            task_list = temp_core.load_task_list_from_excel_with_server_filter(
                account_id=account_info['id'],
                step="step2",
                server_name=server_name
            )
            
            if not task_list:
                return []
            
            # 중복 제거하되 원본 순서 유지하여 키워드 목록 추출
            seen = set()
            provider_codes = []
            for task in task_list:
                if task.get('provider_code') and task['provider_code'] not in seen:
                    provider_codes.append(task['provider_code'])
                    seen.add(task['provider_code'])
            
            logger.info(f"{server_name} 키워드 목록 (엑셀 순서 유지): {provider_codes}")
            return provider_codes
            
        except Exception as e:
            logger.error(f"키워드 목록 가져오기 실패: {e}")
            return []
    
    def _reset_progress_files(self, account_info: Dict, server_name: str = None):
        """
        진행 상황 파일 초기화
        
        Args:
            account_info: 계정 정보
            server_name: 특정 서버만 초기화 (None이면 모든 서버)
        """
        try:
            account_id = account_info['id']
            servers_to_reset = [server_name] if server_name else ["서버1", "서버2", "서버3"]
            
            for server in servers_to_reset:
                progress_file = f"progress_{account_id}_step2_{server}.json"
                if os.path.exists(progress_file):
                    os.remove(progress_file)
                    logger.info(f"{server} 진행 상황 파일 삭제됨: {progress_file}")
                    
            logger.info("진행 상황 초기화 완료")
            
        except Exception as e:
            logger.error(f"진행 상황 초기화 중 오류: {e}")
    
    def restart_browser(self) -> bool:
        """
        브라우저 재시작
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("브라우저 재시작 시작")
            
            # 현재 계정 정보 백업
            current_account_id = self.current_account_id
            if not current_account_id:
                logger.error("현재 계정 정보가 없습니다")
                return False
            
            # 기존 브라우저만 정리 (Step Core 객체들은 유지)
            if self.driver:
                try:
                    self.driver.quit()
                    logger.info("기존 브라우저 종료 완료")
                except Exception as e:
                    logger.warning(f"브라우저 종료 중 오류: {e}")
                finally:
                    self.driver = None
            
            # 가비지 컬렉션 강제 실행 및 대기
            import gc
            gc.collect()
            time.sleep(5)  # Chrome 프로세스 완전 종료 대기
            
            # 새 브라우저 설정
            if not self.setup_browser():
                logger.error("브라우저 재시작 실패")
                return False
            
            # 계정 정보 복원을 위해 AccountManager에서 계정 정보 가져오기
            from account_manager import AccountManager
            account_manager = AccountManager()
            if not account_manager.load_accounts():
                logger.error("계정 정보 로드 실패")
                return False
            
            # 현재 계정 찾기
            current_account = None
            for account in account_manager.accounts:
                if account['id'] == current_account_id:
                    current_account = account
                    break
            
            if not current_account:
                logger.error(f"계정 {current_account_id}를 찾을 수 없습니다")
                return False
            
            # 로그인 및 페이지 이동
            if not self.login_and_navigate(current_account):
                logger.error("로그인 및 페이지 이동 실패")
                return False
            
            # 기존 Step Core 객체들의 드라이버 참조 업데이트
            logger.info(f"Step cores 상태 확인: {list(self.step_cores.keys())}")
            for server_name, step_core in self.step_cores.items():
                if step_core and hasattr(step_core, 'update_driver_references'):
                    try:
                        step_core.update_driver_references(self.driver)
                        logger.info(f"{server_name} 코어 드라이버 참조 업데이트 완료")
                    except Exception as e:
                        logger.error(f"{server_name} 코어 드라이버 참조 업데이트 중 오류: {e}")
                else:
                    logger.info(f"{server_name} 코어: 객체={step_core is not None}, 메서드 존재={hasattr(step_core, 'update_driver_references') if step_core else False}")
                    if step_core is None:
                        logger.warning(f"{server_name} 코어가 None 상태입니다 - 아직 초기화되지 않았을 수 있습니다")
                    else:
                        logger.warning(f"{server_name} 코어에 update_driver_references 메서드가 없습니다")
            
            # 재시작 후 UI 초기 설정 (신규수집 그룹 설정 포함)
            try:
                logger.info("재시작 후 UI 초기 설정 시작")
                # 서버2 코어를 사용하여 UI 설정
                if "서버2" in self.step_cores and self.step_cores["서버2"]:
                    step_core = self.step_cores["서버2"]
                    if hasattr(step_core, '_setup_initial_ui'):
                        if step_core._setup_initial_ui():
                            logger.info("재시작 후 신규수집 그룹 설정 성공")
                        else:
                            logger.warning("재시작 후 UI 초기 설정 실패")
                    
                logger.info("재시작 후 UI 초기 설정 완료")
            except Exception as ui_e:
                logger.warning(f"재시작 후 UI 설정 중 오류: {ui_e}")
                # UI 설정 실패는 치명적이지 않으므로 계속 진행
            
            logger.info("브라우저 재시작 완료")
            return True
            
        except Exception as e:
            logger.error(f"브라우저 재시작 중 오류: {e}")
            return False
    
    def cleanup(self, force_process_cleanup=True):
        """
        리소스 정리
        
        Args:
            force_process_cleanup: 프로세스 강제 종료 여부 (GUI 모드에서는 False)
        """
        try:
            logger.info("리소스 정리 시작")
            
            # Step Core 객체들 정리
            for server_name, step_core in self.step_cores.items():
                if step_core and hasattr(step_core, 'cleanup'):
                    try:
                        step_core.cleanup()
                    except Exception as e:
                        logger.warning(f"{server_name} 코어 정리 중 오류: {e}")
            
            # Step Core 객체들 초기화 (driver 참조 제거)
            self.step_cores = {
                "서버1": None,
                "서버2": None,
                "서버3": None
            }
            
            # 브라우저 정리
            if self.driver:
                try:
                    self.driver.quit()
                except Exception as e:
                    logger.warning(f"브라우저 종료 중 오류: {e}")
                finally:
                    self.driver = None
            
            # 프로세스 강제 종료 (GUI 모드에서는 건너뜀)
            if force_process_cleanup:
                # ChromeDriver 프로세스만 정리 (다른 Chrome 브라우저는 보호)
                try:
                    import subprocess
                    import psutil
                    
                    # ChromeDriver 프로세스만 종료
                    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                        try:
                            if proc.info['name'] == 'chromedriver.exe':
                                proc.terminate()
                                logger.info(f"ChromeDriver 프로세스 종료: PID {proc.info['pid']}")
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                    
                    # 자동화 관련 Chrome 프로세스만 종료 (--remote-debugging-port 옵션이 있는 것들)
                    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                        try:
                            if (proc.info['name'] == 'chrome.exe' and 
                                proc.info['cmdline'] and 
                                any('--remote-debugging-port' in arg for arg in proc.info['cmdline'])):
                                proc.terminate()
                                logger.info(f"자동화 Chrome 프로세스 종료: PID {proc.info['pid']}")
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                            
                    logger.info("자동화 관련 프로세스 정리 완료")
                except ImportError:
                    logger.warning("psutil 모듈이 없어 프로세스 정리를 건너뜁니다")
                except Exception as e:
                    logger.warning(f"프로세스 정리 중 오류: {e}")
            else:
                logger.info("GUI 모드: 프로세스 강제 종료 건너뜀 (다른 터미널 보호)")
            
            # 기타 객체 초기화
            self.browser_core = None
            # current_account_id는 재시작 시 필요하므로 여기서 초기화하지 않음
            
            logger.info("리소스 정리 완료")
            
        except Exception as e:
            logger.error(f"리소스 정리 중 오류: {e}")

def run_step2_batch(account_info: Dict, server_name: str, chunk_size: int = 5) -> Dict:
    """
    GUI에서 호출되는 Step 2 배치 실행 함수
    
    Args:
        account_info: 계정 정보 (driver 포함)
        server_name: 서버 이름 ("서버1", "서버2", "서버3")
        chunk_size: 청크 크기
        
    Returns:
        Dict: 실행 결과
    """
    runner = None
    
    try:
        logger.info(f"Step 2 배치 처리 시작 - 계정: {account_info['id']}, 서버: {server_name}")
        
        # 배치 실행기 초기화
        runner = Step2BatchRunner()
        
        # 브라우저 설정 (GUI에서 전달받은 driver 사용)
        if 'driver' in account_info:
            runner.driver = account_info['driver']
            runner.browser_core = BrowserCore()
            runner.browser_core.driver = runner.driver
            logger.info("GUI에서 전달받은 브라우저 사용")
        else:
            # 브라우저 설정
            if not runner.setup_browser():
                logger.error("브라우저 설정 실패")
                return {'success': False, 'error': '브라우저 설정 실패'}
        
        # 로그인 및 페이지 이동
        if not runner.login_and_navigate(account_info):
            logger.error("로그인 및 페이지 이동 실패")
            return {'success': False, 'error': '로그인 및 페이지 이동 실패'}
        
        # Step Core 객체들 설정
        if not runner.setup_step_cores(account_info):
            logger.error("Step Core 객체 설정 실패")
            return {'success': False, 'error': 'Step Core 객체 설정 실패'}
        
        # 배치 처리 실행
        logger.info("배치 처리 시작")
        result = runner.run_batch_processing(
            account_info=account_info,
            server_name=server_name,
            chunk_size=chunk_size
        )
        
        # 결과 로깅
        logger.info(f"배치 처리 완료 - 성공: {result['success']}")
        logger.info(f"처리된 서버: {result['servers_processed']}개")
        logger.info(f"총 처리된 키워드: {result['total_keywords_processed']}개")
        logger.info(f"총 처리된 상품: {result['total_products_processed']}개")
        
        if result['errors']:
            for error in result['errors']:
                logger.error(f"오류: {error}")
        
        return result
        
    except Exception as e:
        error_msg = f"Step 2 배치 처리 중 오류: {e}"
        logger.error(error_msg)
        logger.error(f"오류 상세: {traceback.format_exc()}")
        return {'success': False, 'error': error_msg}
    finally:
        if runner:
            runner.cleanup()

def main():
    """
    메인 실행 함수
    """
    import argparse
    
    # 명령행 인자 파싱
    parser = argparse.ArgumentParser(description='퍼센티 Step 2 배치 실행기')
    parser.add_argument('--account', type=str, required=True, help='계정 번호 또는 이메일')
    parser.add_argument('--server', type=str, required=True, help='서버 번호 (1, 2, 3)')
    parser.add_argument('--chunk-size', type=int, default=5, help='청크 크기 (기본값: 5)')
    parser.add_argument('--debug', action='store_true', help='디버그 모드')
    parser.add_argument('--verbose', action='store_true', help='상세 로그')
    parser.add_argument('--gui', action='store_true', help='GUI 모드에서 실행 (프로세스 강제 종료 비활성화)')
    
    args = parser.parse_args()
    
    runner = None
    
    try:
        print("=== 퍼센티 Step 2 배치 실행기 ===")
        
        # 계정 로드
        account_manager = AccountManager()
        if not account_manager.load_accounts():
            print("계정 정보를 로드할 수 없습니다.")
            return
        
        accounts = account_manager.accounts
        if not accounts:
            print("사용 가능한 계정이 없습니다.")
            return
        
        # 계정 선택 (번호 또는 이메일로)
        selected_account = None
        if args.account.isdigit():
            # 번호로 선택
            account_index = int(args.account) - 1
            if 0 <= account_index < len(accounts):
                selected_account = accounts[account_index]
        else:
            # 이메일로 선택
            for account in accounts:
                if account['id'] == args.account:
                    selected_account = account
                    break
        
        if not selected_account:
            print(f"계정을 찾을 수 없습니다: {args.account}")
            print("사용 가능한 계정:")
            for i, account in enumerate(accounts, 1):
                print(f"{i}. {account['id']} ({account.get('nickname', 'Unknown')})")
            return
        
        print(f"선택된 계정: {selected_account['id']}")
        
        # 서버 선택
        server_map = {'1': '서버1', '2': '서버2', '3': '서버3'}
        selected_server = server_map.get(args.server)
        
        if not selected_server:
            print(f"올바르지 않은 서버 번호: {args.server}")
            print("사용 가능한 서버: 1, 2, 3")
            return
        
        print(f"선택된 서버: {selected_server}")
        print(f"청크 크기: {args.chunk_size}")
        
        # 배치 실행기 초기화
        runner = Step2BatchRunner()
        
        # 브라우저 설정
        if not runner.setup_browser():
            logger.error("브라우저 설정 실패")
            return
        
        # 로그인 및 페이지 이동
        if not runner.login_and_navigate(selected_account):
            logger.error("로그인 및 페이지 이동 실패")
            return
        
        # Step Core 객체들 설정
        if not runner.setup_step_cores(selected_account):
            logger.error("Step Core 객체 설정 실패")
            return
        
        # 배치 처리 실행
        print("\n=== 배치 처리 시작 ===")
        result = runner.run_batch_processing(
            account_info=selected_account,
            server_name=selected_server,
            chunk_size=args.chunk_size
        )
        
        # 결과 출력
        print("\n=== 배치 처리 결과 ===")
        print(f"전체 성공 여부: {result['success']}")
        print(f"처리된 서버: {result['servers_processed']}개")
        print(f"실패한 서버: {result['servers_failed']}개")
        print(f"총 처리된 키워드: {result['total_keywords_processed']}개")
        print(f"총 처리된 상품: {result['total_products_processed']}개")
        
        if result['server_results']:
            print("\n서버별 상세 결과:")
            for server, server_result in result['server_results'].items():
                print(f"  {server}: 성공={server_result.get('success', False)}, "
                      f"키워드={server_result.get('processed_keywords', 0)}개, "
                      f"상품={server_result.get('total_products_processed', 0)}개")
        
        if result['errors']:
            print("\n발생한 오류:")
            for error in result['errors']:
                print(f"  - {error}")
        
        if result['success']:
            print("\n=== 배치 처리 완료 ===")
            logger.info("배치 처리 성공")
        else:
            print("\n=== 배치 처리 실패 ===")
            logger.error("배치 처리 실패")
        
        # GUI 모드에서는 자동 종료
        print("\n프로그램을 종료합니다.")
        
    except KeyboardInterrupt:
        logger.info("사용자에 의해 중단됨")
    except Exception as e:
        logger.error(f"메인 실행 중 오류: {e}")
        logger.error(f"오류 상세: {traceback.format_exc()}")
    finally:
        if runner:
            # GUI 모드에서는 프로세스 강제 종료를 비활성화하여 다른 터미널 보호
            force_cleanup = not args.gui if 'args' in locals() else True
            runner.cleanup(force_process_cleanup=force_cleanup)

if __name__ == "__main__":
    main()