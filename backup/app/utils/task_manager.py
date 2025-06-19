# -*- coding: utf-8 -*-
"""
퍼센티 자동화 작업 관리자

각 계정별 자동화 작업을 생성, 관리, 모니터링하는 기능을 제공합니다.
"""

import os
import time
import uuid
import logging
import threading
from datetime import datetime

# 작업 단계 관리자 임포트
from app.steps.step1_manager import Step1Manager
# 향후 다른 단계 관리자도 추가

logger = logging.getLogger(__name__)

class TaskManager:
    """퍼센티 자동화 작업을 관리하는 클래스"""
    
    def __init__(self):
        """초기화"""
        self.tasks = {}  # 작업 ID를 키로 하는 작업 정보 딕셔너리
        self.lock = threading.Lock()  # 스레드 안전을 위한 락
    
    def create_task(self, account_info, step_number, quantity, driver):
        """
        새 작업 생성
        
        Args:
            account_info (dict): 계정 정보
            step_number (int): 작업 단계 번호 (1~6)
            quantity (int): 처리할 수량
            driver: 웹드라이버 인스턴스
        
        Returns:
            str: 작업 ID
        """
        try:
            # 작업 ID 생성
            task_id = str(uuid.uuid4())
            
            # 배치 정보 생성
            batch_info = {
                "batch_id": task_id,
                "quantity": int(quantity),
                "created_at": datetime.now().isoformat(),
                "account_id": account_info.get("id"),
                "step_number": step_number
            }
            
            # 단계에 맞는 관리자 생성
            step_manager = None
            if step_number == 1:
                step_manager = Step1Manager(driver)
            # 향후 다른 단계 관리자도 추가
            else:
                logger.error(f"지원되지 않는 작업 단계: {step_number}")
                return None
            
            # 계정 및 배치 정보 설정
            step_manager.set_account_info(account_info)
            step_manager.set_batch_info(batch_info)
            
            # 작업 정보 저장
            with self.lock:
                self.tasks[task_id] = {
                    "id": task_id,
                    "account_info": account_info,
                    "batch_info": batch_info,
                    "manager": step_manager,
                    "status": "created",
                    "progress": 0,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "completed_at": None,
                    "thread": None,
                    "initial_product_count": None,
                    "final_product_count": None,
                    "processed_count": 0,
                    "actual_processed_count": None,
                    "result": None,
                    "error": None
                }
            
            logger.info(f"새 작업이 생성되었습니다: {task_id} (계정: {account_info.get('id')}, 단계: {step_number}, 수량: {quantity})")
            return task_id
            
        except Exception as e:
            logger.error(f"작업 생성 중 오류: {str(e)}")
            return None
    
    def start_task(self, task_id):
        """
        작업 시작
        
        Args:
            task_id (str): 작업 ID
        
        Returns:
            bool: 시작 성공 여부
        """
        try:
            with self.lock:
                if task_id not in self.tasks:
                    logger.error(f"작업 ID가 존재하지 않습니다: {task_id}")
                    return False
                
                task = self.tasks[task_id]
                if task["status"] not in ["created", "stopped", "failed"]:
                    logger.warning(f"작업이 이미 실행 중이거나 완료되었습니다: {task_id} (상태: {task['status']})")
                    return False
                
                # 작업 상태 업데이트
                task["status"] = "running"
                task["updated_at"] = datetime.now().isoformat()
                task["progress"] = 0
                task["error"] = None
            
            # 작업 스레드 생성 및 시작
            thread = threading.Thread(target=self._run_task, args=(task_id,))
            thread.daemon = True  # 메인 스레드 종료 시 같이 종료
            
            with self.lock:
                self.tasks[task_id]["thread"] = thread
            
            thread.start()
            logger.info(f"작업이 시작되었습니다: {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"작업 시작 중 오류: {task_id}, {str(e)}")
            with self.lock:
                if task_id in self.tasks:
                    self.tasks[task_id]["status"] = "failed"
                    self.tasks[task_id]["error"] = str(e)
                    self.tasks[task_id]["updated_at"] = datetime.now().isoformat()
            return False
    
    def _run_task(self, task_id):
        """
        작업 실행 (스레드에서 호출)
        
        Args:
            task_id (str): 작업 ID
        """
        try:
            with self.lock:
                if task_id not in self.tasks:
                    logger.error(f"작업 ID가 존재하지 않습니다: {task_id}")
                    return
                
                task = self.tasks[task_id]
                manager = task["manager"]
            
            # 작업 실행
            logger.info(f"작업 실행 중: {task_id}")
            result = manager.run_automation()
            
            # 작업 결과 업데이트
            with self.lock:
                if task_id in self.tasks:
                    if result:
                        self.tasks[task_id]["status"] = "completed"
                        self.tasks[task_id]["progress"] = 100
                    else:
                        self.tasks[task_id]["status"] = "failed"
                    
                    # 상품 수량 정보 업데이트
                    if hasattr(manager, 'initial_product_count'):
                        self.tasks[task_id]["initial_product_count"] = manager.initial_product_count
                    if hasattr(manager, 'final_product_count'):
                        self.tasks[task_id]["final_product_count"] = manager.final_product_count
                    if hasattr(manager, 'processed_count'):
                        self.tasks[task_id]["processed_count"] = manager.processed_count
                    if hasattr(manager, 'actual_processed_count'):
                        self.tasks[task_id]["actual_processed_count"] = manager.actual_processed_count
                    
                    self.tasks[task_id]["result"] = result
                    self.tasks[task_id]["completed_at"] = datetime.now().isoformat()
                    self.tasks[task_id]["updated_at"] = datetime.now().isoformat()
            
            logger.info(f"작업 완료: {task_id} (결과: {'성공' if result else '실패'})")
            
        except Exception as e:
            logger.error(f"작업 실행 중 오류: {task_id}, {str(e)}")
            with self.lock:
                if task_id in self.tasks:
                    self.tasks[task_id]["status"] = "failed"
                    self.tasks[task_id]["error"] = str(e)
                    self.tasks[task_id]["updated_at"] = datetime.now().isoformat()
    
    def stop_task(self, task_id):
        """
        작업 중지
        
        Args:
            task_id (str): 작업 ID
        
        Returns:
            bool: 중지 성공 여부
        """
        try:
            with self.lock:
                if task_id not in self.tasks:
                    logger.error(f"작업 ID가 존재하지 않습니다: {task_id}")
                    return False
                
                task = self.tasks[task_id]
                if task["status"] != "running":
                    logger.warning(f"작업이 실행 중이 아닙니다: {task_id} (상태: {task['status']})")
                    return False
                
                # 작업 중지 요청
                manager = task["manager"]
                manager.stop_automation()
                
                # 작업 상태 업데이트
                task["status"] = "stopping"
                task["updated_at"] = datetime.now().isoformat()
            
            logger.info(f"작업 중지 요청됨: {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"작업 중지 중 오류: {task_id}, {str(e)}")
            return False
    
    def get_task(self, task_id):
        """
        작업 정보 조회
        
        Args:
            task_id (str): 작업 ID
        
        Returns:
            dict: 작업 정보 (없으면 None)
        """
        try:
            with self.lock:
                if task_id not in self.tasks:
                    logger.warning(f"작업 ID가 존재하지 않습니다: {task_id}")
                    return None
                
                # 반환용 작업 정보 복사 (스레드 안전)
                task = self.tasks[task_id].copy()
                
                # manager 및 thread는 직렬화 불가능하므로 제외
                if "manager" in task:
                    del task["manager"]
                if "thread" in task:
                    del task["thread"]
                
                return task
                
        except Exception as e:
            logger.error(f"작업 정보 조회 중 오류: {task_id}, {str(e)}")
            return None
    
    def get_all_tasks(self, account_id=None, status=None):
        """
        모든 작업 정보 조회 (필터링 가능)
        
        Args:
            account_id (str, optional): 계정 ID로 필터링
            status (str, optional): 작업 상태로 필터링
        
        Returns:
            list: 작업 정보 리스트
        """
        try:
            result = []
            
            with self.lock:
                for task_id, task in self.tasks.items():
                    # 필터링
                    if account_id and task["account_info"].get("id") != account_id:
                        continue
                    if status and task["status"] != status:
                        continue
                    
                    # 반환용 작업 정보 복사 (스레드 안전)
                    task_copy = task.copy()
                    
                    # manager 및 thread는 직렬화 불가능하므로 제외
                    if "manager" in task_copy:
                        del task_copy["manager"]
                    if "thread" in task_copy:
                        del task_copy["thread"]
                    
                    result.append(task_copy)
            
            return result
            
        except Exception as e:
            logger.error(f"작업 정보 목록 조회 중 오류: {str(e)}")
            return []
    
    def update_task_progress(self, task_id, progress):
        """
        작업 진행 상황 업데이트
        
        Args:
            task_id (str): 작업 ID
            progress (int): 진행률 (0-100)
        
        Returns:
            bool: 업데이트 성공 여부
        """
        try:
            with self.lock:
                if task_id not in self.tasks:
                    logger.warning(f"작업 ID가 존재하지 않습니다: {task_id}")
                    return False
                
                # 작업 진행 상황 업데이트
                self.tasks[task_id]["progress"] = max(0, min(100, progress))
                self.tasks[task_id]["updated_at"] = datetime.now().isoformat()
            
            return True
            
        except Exception as e:
            logger.error(f"작업 진행 상황 업데이트 중 오류: {task_id}, {str(e)}")
            return False
    
    def clean_completed_tasks(self, max_age_hours=24):
        """
        완료된 작업 정리 (오래된 작업 삭제)
        
        Args:
            max_age_hours (int): 최대 보존 시간 (시간)
        
        Returns:
            int: 삭제된 작업 수
        """
        try:
            now = datetime.now()
            deleted_count = 0
            
            with self.lock:
                task_ids_to_delete = []
                
                for task_id, task in self.tasks.items():
                    if task["status"] in ["completed", "failed", "stopped"]:
                        completed_at = datetime.fromisoformat(task["completed_at"]) if task["completed_at"] else None
                        updated_at = datetime.fromisoformat(task["updated_at"])
                        
                        # 완료 시간이 있으면 완료 시간 기준, 없으면 업데이트 시간 기준
                        reference_time = completed_at or updated_at
                        
                        # 기준 시간이 max_age_hours보다 오래된 경우 삭제 대상에 추가
                        if reference_time and (now - reference_time).total_seconds() / 3600 > max_age_hours:
                            task_ids_to_delete.append(task_id)
                
                # 삭제 대상 작업 삭제
                for task_id in task_ids_to_delete:
                    del self.tasks[task_id]
                    deleted_count += 1
            
            if deleted_count > 0:
                logger.info(f"오래된 작업 {deleted_count}개가 정리되었습니다.")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"작업 정리 중 오류: {str(e)}")
            return 0
