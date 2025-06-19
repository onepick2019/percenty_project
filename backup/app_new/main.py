#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Percenty 자동화 - 새로운 배치 아키텍처 GUI

이 모듈은 새로운 배치 아키텍처를 완전히 활용하는 현대적인 GUI 애플리케이션입니다.
주요 기능:
- 다중 계정 동시 실행
- 다중 단계 관리
- 실시간 모니터링
- 설정 기반 관리
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import json
import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 새로운 배치 아키텍처 모듈 임포트
from batch.batch_manager import BatchManager
from core.account.account_manager import CoreAccountManager
from core.browser.browser_manager import CoreBrowserManager

class PercentyGUI:
    """Percenty 자동화 GUI 메인 클래스"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.batch_manager = None
        self.account_manager = None
        self.browser_manager = None
        self.running_tasks = {}
        self._stop_execution = False
        self.setup_logging()
        self.setup_ui()
        self.load_configuration()
        self.start_gui_update_timer()
        
    def setup_logging(self):
        """로깅 설정"""
        log_dir = project_root / "logs"
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "gui_app.log", encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_ui(self):
        """UI 설정"""
        self.root.title("Percenty 자동화 - 새로운 배치 시스템")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 그리드 가중치 설정
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # 제목
        title_label = ttk.Label(main_frame, text="Percenty 자동화 시스템", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 설정 섹션
        self.create_config_section(main_frame)
        
        # 계정 선택 섹션
        self.create_account_section(main_frame)
        
        # 실행 제어 섹션
        self.create_control_section(main_frame)
        
        # 로그 및 모니터링 섹션
        self.create_monitoring_section(main_frame)
        
        # 상태바
        self.create_status_bar()
        
    def create_config_section(self, parent):
        """설정 섹션 생성"""
        config_frame = ttk.LabelFrame(parent, text="배치 설정", padding="10")
        config_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 최대 워커 수
        ttk.Label(config_frame, text="최대 동시 실행:").grid(row=0, column=0, sticky=tk.W)
        self.max_workers_var = tk.StringVar(value="3")
        max_workers_spin = ttk.Spinbox(config_frame, from_=1, to=10, width=10, 
                                      textvariable=self.max_workers_var)
        max_workers_spin.grid(row=0, column=1, sticky=tk.W, padx=(5, 20))
        
        # 기본 수량
        ttk.Label(config_frame, text="기본 수량:").grid(row=0, column=2, sticky=tk.W)
        self.default_quantity_var = tk.StringVar(value="10")
        quantity_spin = ttk.Spinbox(config_frame, from_=1, to=100, width=10,
                                   textvariable=self.default_quantity_var)
        quantity_spin.grid(row=0, column=3, sticky=tk.W, padx=(5, 20))
        
        # 헤드리스 모드
        self.headless_var = tk.BooleanVar(value=False)
        headless_check = ttk.Checkbutton(config_frame, text="헤드리스 모드", 
                                        variable=self.headless_var)
        headless_check.grid(row=0, column=4, sticky=tk.W, padx=(5, 0))
        
        # 설정 저장/로드 버튼
        ttk.Button(config_frame, text="설정 저장", 
                  command=self.save_configuration).grid(row=0, column=5, padx=(20, 5))
        ttk.Button(config_frame, text="설정 로드", 
                  command=self.load_configuration).grid(row=0, column=6, padx=(5, 0))
        
    def create_account_section(self, parent):
        """계정 선택 섹션 생성"""
        account_frame = ttk.LabelFrame(parent, text="계정 관리", padding="10")
        account_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        account_frame.columnconfigure(1, weight=1)
        
        # 계정 목록
        ttk.Label(account_frame, text="사용 가능한 계정:").grid(row=0, column=0, sticky=tk.W)
        
        # 계정 리스트박스와 스크롤바
        list_frame = ttk.Frame(account_frame)
        list_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0))
        list_frame.columnconfigure(0, weight=1)
        
        self.account_listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED, height=6)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.account_listbox.yview)
        self.account_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.account_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 계정 제어 버튼
        button_frame = ttk.Frame(account_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=(10, 0))
        
        ttk.Button(button_frame, text="모든 계정 선택", 
                  command=self.select_all_accounts).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="선택 해제", 
                  command=self.clear_account_selection).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="계정 새로고침", 
                  command=self.refresh_accounts).pack(side=tk.LEFT, padx=(0, 5))
        
    def create_control_section(self, parent):
        """실행 제어 섹션 생성"""
        control_frame = ttk.LabelFrame(parent, text="실행 제어", padding="10")
        control_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 10))
        
        # 단계 선택
        ttk.Label(control_frame, text="실행할 단계:").grid(row=0, column=0, sticky=tk.W)
        
        self.step_vars = {}
        steps = ["Step 1: 상품 수정", "Step 2: 그룹 이동", "Step 3: 메모 편집", 
                "Step 4: 이름 편집", "Step 5: 업로드", "Step 6: 최종 처리"]
        
        for i, step in enumerate(steps):
            var = tk.BooleanVar(value=(i == 0))  # Step 1은 기본 선택
            self.step_vars[f"step{i+1}"] = var
            ttk.Checkbutton(control_frame, text=step, variable=var).grid(
                row=1+i//2, column=i%2, sticky=tk.W, padx=(0, 20), pady=2)
        
        # 실행 버튼들
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(20, 0))
        
        self.start_button = ttk.Button(button_frame, text="배치 실행 시작", 
                                      command=self.start_batch_execution,
                                      style='Accent.TButton',
                                      state=tk.DISABLED)  # 초기에는 비활성화
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="실행 중지", 
                                     command=self.stop_batch_execution,
                                     state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="상태 새로고침", 
                  command=self.refresh_status).pack(side=tk.LEFT)
        
    def create_monitoring_section(self, parent):
        """모니터링 섹션 생성"""
        monitor_frame = ttk.LabelFrame(parent, text="실시간 모니터링", padding="10")
        monitor_frame.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), 
                          padx=(10, 0), pady=(0, 10))
        monitor_frame.columnconfigure(0, weight=1)
        monitor_frame.rowconfigure(1, weight=1)
        
        # 진행 상황 표시
        progress_frame = ttk.Frame(monitor_frame)
        progress_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(1, weight=1)
        
        ttk.Label(progress_frame, text="전체 진행률:").grid(row=0, column=0, sticky=tk.W)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100)
        self.progress_bar.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        
        self.progress_label = ttk.Label(progress_frame, text="0%")
        self.progress_label.grid(row=0, column=2, padx=(10, 0))
        
        # 로그 출력
        self.log_text = scrolledtext.ScrolledText(monitor_frame, height=20, width=60)
        self.log_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 로그 핸들러 추가
        log_handler = GuiLogHandler(self.log_text)
        log_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        log_handler.setFormatter(formatter)
        logging.getLogger().addHandler(log_handler)
        
    def create_status_bar(self):
        """상태바 생성"""
        self.status_var = tk.StringVar(value="준비")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
    def load_configuration(self):
        """설정 로드"""
        try:
            config_path = project_root / "batch" / "config" / "batch_config.json"
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # 설정 값 적용
                self.max_workers_var.set(str(config.get('max_workers', 3)))
                self.default_quantity_var.set(str(config.get('default_quantity', 10)))
                browser_config = config.get('browser', {})
                self.headless_var.set(browser_config.get('headless', False))
                
                self.logger.info("설정을 성공적으로 로드했습니다.")
            else:
                self.logger.warning("설정 파일을 찾을 수 없습니다. 기본값을 사용합니다.")
                
            # 배치 매니저 초기화
            self.initialize_managers()
            
        except Exception as e:
            self.logger.error(f"설정 로드 중 오류 발생: {e}")
            messagebox.showerror("오류", f"설정 로드 실패: {e}")
            
    def save_configuration(self):
        """설정 저장"""
        try:
            config = {
                'max_workers': int(self.max_workers_var.get()),
                'default_quantity': int(self.default_quantity_var.get()),
                'browser': {
                    'headless': self.headless_var.get(),
                    'window_size': {'width': 1920, 'height': 1080}
                },
                'logging': {
                    'level': 'INFO',
                    'file': 'logs/batch_processor.log'
                }
            }
            
            config_path = project_root / "batch" / "config" / "batch_config.json"
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                
            self.logger.info("설정을 성공적으로 저장했습니다.")
            messagebox.showinfo("성공", "설정이 저장되었습니다.")
            
        except Exception as e:
            self.logger.error(f"설정 저장 중 오류 발생: {e}")
            messagebox.showerror("오류", f"설정 저장 실패: {e}")
            
    def initialize_managers(self):
        """매니저 초기화"""
        try:
            # 배치 매니저 초기화
            self.batch_manager = BatchManager()
            self.account_manager = CoreAccountManager()
            
            # 브라우저 매니저는 별도 스레드에서 초기화하여 GUI 블로킹 방지
            self.status_var.set("브라우저 매니저 초기화 중...")
            self.logger.info("브라우저 매니저를 별도 스레드에서 초기화합니다.")
            
            def init_browser_manager():
                try:
                    # GUI에서 설정한 헤드리스 모드 사용
                    self.browser_manager = CoreBrowserManager(headless=self.headless_var.get())
                    self.logger.info("브라우저 매니저 초기화 완료")
                    
                    # GUI 업데이트는 메인 스레드에서 실행
                    self.root.after(0, self._on_browser_manager_ready)
                    
                except Exception as e:
                    self.logger.error(f"브라우저 매니저 초기화 중 오류 발생: {e}")
                    # GUI 업데이트는 메인 스레드에서 실행
                    self.root.after(0, lambda: self._on_browser_manager_error(e))
            
            # 브라우저 매니저 초기화를 별도 스레드에서 실행
            browser_thread = threading.Thread(target=init_browser_manager, daemon=True)
            browser_thread.start()
            
            # 계정 목록 새로고침 (브라우저 매니저와 독립적)
            self.refresh_accounts()
            
            self.status_var.set("매니저 초기화 진행 중... (브라우저 매니저 대기)")
            self.logger.info("배치 매니저와 계정 매니저 초기화 완료, 브라우저 매니저 초기화 중...")
            
        except Exception as e:
            self.logger.error(f"매니저 초기화 중 오류 발생: {e}")
            self.status_var.set(f"초기화 실패: {e}")
            
    def _on_browser_manager_ready(self):
        """브라우저 매니저 초기화 완료 시 호출"""
        self.status_var.set("모든 매니저 초기화 완료")
        self.logger.info("모든 매니저가 성공적으로 초기화되었습니다.")
        
        # 실행 버튼 활성화
        if hasattr(self, 'start_button'):
            self.start_button.config(state='normal')
            
    def _on_browser_manager_error(self, error):
        """브라우저 매니저 초기화 실패 시 호출"""
        self.status_var.set(f"브라우저 매니저 초기화 실패: {error}")
        self.logger.error(f"브라우저 매니저 초기화 실패: {error}")
        
        # 사용자에게 알림
        messagebox.showerror("브라우저 초기화 실패", 
                           f"브라우저 매니저 초기화에 실패했습니다.\n\n오류: {error}\n\n" +
                           "다음을 확인해주세요:\n" +
                           "1. Chrome 브라우저가 설치되어 있는지\n" +
                           "2. 인터넷 연결 상태\n" +
                           "3. 방화벽/보안 프로그램 설정\n" +
                           "4. 관리자 권한으로 실행")
            
    def refresh_accounts(self):
        """계정 목록 새로고침"""
        try:
            if not self.account_manager:
                return
                
            self.account_listbox.delete(0, tk.END)
            accounts = self.account_manager.get_all_accounts()
            
            for account in accounts:
                display_text = f"{account['id']} ({account.get('name', 'Unknown')})"
                self.account_listbox.insert(tk.END, display_text)
                
            self.logger.info(f"{len(accounts)}개의 계정을 로드했습니다.")
            
        except Exception as e:
            self.logger.error(f"계정 새로고침 중 오류 발생: {e}")
            
    def select_all_accounts(self):
        """모든 계정 선택"""
        self.account_listbox.select_set(0, tk.END)
        
    def clear_account_selection(self):
        """계정 선택 해제"""
        self.account_listbox.selection_clear(0, tk.END)
        
    def get_selected_accounts(self):
        """선택된 계정 목록 반환"""
        selected_indices = self.account_listbox.curselection()
        if not selected_indices:
            return []
            
        accounts = self.account_manager.get_all_accounts()
        return [accounts[i] for i in selected_indices]
        
    def get_selected_steps(self):
        """선택된 단계 목록 반환"""
        selected_steps = []
        for step, var in self.step_vars.items():
            if var.get():
                selected_steps.append(step)
        return selected_steps
        
    def start_batch_execution(self):
        """배치 실행 시작"""
        try:
            # 선택된 계정과 단계 확인
            selected_accounts = self.get_selected_accounts()
            selected_steps = self.get_selected_steps()
            
            if not selected_accounts:
                messagebox.showwarning("경고", "실행할 계정을 선택해주세요.")
                return
                
            if not selected_steps:
                messagebox.showwarning("경고", "실행할 단계를 선택해주세요.")
                return
                
            # UI 상태 변경
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.status_var.set("배치 실행 중...")
            
            # 배치 실행을 별도 스레드에서 수행
            execution_thread = threading.Thread(
                target=self.execute_batch,
                args=(selected_accounts, selected_steps),
                daemon=True
            )
            execution_thread.start()
            
            self.logger.info(f"배치 실행 시작: {len(selected_accounts)}개 계정, {len(selected_steps)}개 단계")
            
        except Exception as e:
            self.logger.error(f"배치 실행 시작 중 오류 발생: {e}")
            messagebox.showerror("오류", f"배치 실행 실패: {e}")
            self.reset_ui_state()
            
    def execute_batch(self, accounts, steps):
        """배치 실행 (별도 스레드)"""
        import traceback
        import time
        from concurrent.futures import ThreadPoolExecutor, TimeoutError
        
        try:
            # 브라우저 매니저 초기화 확인
            if not self.browser_manager:
                self.logger.error("브라우저 매니저가 초기화되지 않았습니다.")
                self.root.after(0, lambda: messagebox.showerror("오류", "브라우저 매니저가 아직 초기화되지 않았습니다.\n잠시 후 다시 시도해주세요."))
                self.root.after(0, self.reset_ui_state)
                return
                
            total_tasks = len(accounts) * len(steps)
            completed_tasks = 0
            
            self.logger.info(f"=== 배치 실행 시작 - 총 {total_tasks}개 작업 ===")
            self.logger.info(f"배치 매니저 상태: {type(self.batch_manager)}")
            self.logger.info(f"계정 목록: {[acc['id'] for acc in accounts]}")
            self.logger.info(f"단계 목록: {steps}")
            
            # 초기 상태 업데이트
            self.root.after(0, lambda: self.status_var.set("배치 실행 중... 초기화"))
            
            for account_idx, account in enumerate(accounts):
                if getattr(self, '_stop_execution', False):
                    self.logger.info("중지 요청으로 배치 실행 중단")
                    break
                    
                # 계정별 상태 업데이트
                self.root.after(0, lambda acc=account: self.status_var.set(f"계정 {acc['id']} 처리 중..."))
                
                for step_idx, step in enumerate(steps):
                    if getattr(self, '_stop_execution', False):
                        self.logger.info("중지 요청으로 배치 실행 중단")
                        break
                        
                    self.logger.info(f"=== 작업 시작: {account['id']} - {step} ===")
                    
                    # 단계별 상태 업데이트
                    self.root.after(0, lambda acc=account, s=step: self.status_var.set(f"계정 {acc['id']} - 단계 {s} 실행 중..."))
                    
                    try:
                        # 배치 매니저 execute_single_step 호출 전 로그
                        self.logger.info(f"execute_single_step 호출 준비: account_id={account['id']}, step={step}, quantity={int(self.default_quantity_var.get())}")
                        self.logger.info(f"배치 매니저 타입: {type(self.batch_manager)}")
                        self.logger.info(f"배치 매니저 메서드 존재 확인: {hasattr(self.batch_manager, 'execute_single_step')}")
                        
                        # UI 응답성을 위한 작은 지연
                        time.sleep(0.1)
                        
                        # 타임아웃을 적용한 배치 실행
                        with ThreadPoolExecutor(max_workers=1) as executor:
                            self.logger.info(f"ThreadPoolExecutor 생성 완료, execute_single_step 호출 시작")
                            
                            future = executor.submit(
                                self.batch_manager.execute_single_step,
                                account['id'],
                                step,
                                int(self.default_quantity_var.get())
                            )
                            
                            self.logger.info(f"executor.submit 호출 완료, future 대기 시작")
                            
                            # 30초 타임아웃으로 실행 (더 짧게 설정)
                            try:
                                # 타임아웃 동안 주기적으로 GUI 업데이트
                                start_time = time.time()
                                check_count = 0
                                while not future.done():
                                    check_count += 1
                                    elapsed = time.time() - start_time
                                    
                                    if elapsed > 30:  # 30초 타임아웃
                                        self.logger.error(f"30초 타임아웃 발생 (체크 횟수: {check_count})")
                                        raise TimeoutError("30초 타임아웃")
                                    
                                    # 5초마다 상태 로그
                                    if check_count % 50 == 0:  # 0.1초 * 50 = 5초
                                        self.logger.info(f"대기 중... 경과시간: {elapsed:.1f}초, 체크 횟수: {check_count}")
                                    
                                    # GUI 이벤트 처리
                                    self.root.update_idletasks()
                                    time.sleep(0.1)
                                
                                self.logger.info(f"future.done() 완료, result 획득 시작")
                                result = future.result()
                                self.logger.info(f"execute_single_step 호출 완료: 결과={result}")
                            except TimeoutError:
                                self.logger.error(f"execute_single_step 타임아웃 (30초): {account['id']} - {step}")
                                future.cancel()
                                result = False
                        
                    except Exception as step_error:
                        self.logger.error(f"execute_single_step 호출 중 예외 발생: {step_error}")
                        self.logger.error(f"예외 상세: {traceback.format_exc()}")
                        result = False
                    
                    completed_tasks += 1
                    progress = (completed_tasks / total_tasks) * 100
                    
                    # UI 업데이트 (메인 스레드에서)
                    self.root.after(0, self.update_progress, progress)
                    
                    if result:
                        self.logger.info(f"=== 작업 완료: {account['id']} - {step} ===")
                        self.root.after(0, lambda acc=account, s=step: self.status_var.set(f"계정 {acc['id']} - 단계 {s} 완료"))
                    else:
                        self.logger.error(f"=== 작업 실패: {account['id']} - {step} ===")
                        self.root.after(0, lambda acc=account, s=step: self.status_var.set(f"계정 {acc['id']} - 단계 {s} 실패"))
                    
                    # 각 단계 후 UI 응답성을 위한 지연
                    time.sleep(0.2)
                        
            # 실행 완료
            self.logger.info("=== 모든 배치 작업 완료 ===")
            self.root.after(0, self.on_batch_complete)
            
        except Exception as e:
            self.logger.error(f"배치 실행 중 최상위 오류 발생: {e}")
            self.logger.error(f"최상위 오류 상세: {traceback.format_exc()}")
            self.root.after(0, self.on_batch_error, str(e))
            
    def update_progress(self, progress):
        """진행률 업데이트"""
        self.progress_var.set(progress)
        self.progress_label.config(text=f"{progress:.1f}%")
        
    def on_batch_complete(self):
        """배치 실행 완료 처리"""
        self.logger.info("모든 배치 작업이 완료되었습니다.")
        self.status_var.set("배치 실행 완료")
        self.reset_ui_state()
        messagebox.showinfo("완료", "모든 배치 작업이 완료되었습니다.")
        
    def on_batch_error(self, error_msg):
        """배치 실행 오류 처리"""
        self.status_var.set(f"배치 실행 오류: {error_msg}")
        self.reset_ui_state()
        messagebox.showerror("오류", f"배치 실행 중 오류가 발생했습니다: {error_msg}")
        
    def stop_batch_execution(self):
        """배치 실행 중지"""
        self._stop_execution = True
        self.logger.info("배치 실행 중지 요청")
        self.status_var.set("배치 실행 중지 중...")
        
    def reset_ui_state(self):
        """UI 상태를 초기 상태로 복원"""
        try:
            if hasattr(self, 'start_button') and self.browser_manager:
                self.start_button.config(state=tk.NORMAL)
            else:
                self.start_button.config(state=tk.DISABLED)
                
            if hasattr(self, 'stop_button'):
                self.stop_button.config(state=tk.DISABLED)
                
            self._stop_execution = False
            
        except Exception as e:
            self.logger.error(f"UI 상태 복원 중 오류: {e}")
        
    def refresh_status(self):
        """상태 새로고침"""
        try:
            if self.batch_manager:
                status = self.batch_manager.get_status()
                self.logger.info(f"현재 상태: {status}")
            else:
                self.logger.warning("배치 매니저가 초기화되지 않았습니다.")
        except Exception as e:
            self.logger.error(f"상태 새로고침 중 오류 발생: {e}")
            
    def start_gui_update_timer(self):
        """GUI 업데이트 타이머 시작"""
        def update_gui():
            try:
                # GUI 이벤트 처리
                self.root.update_idletasks()
                # 100ms마다 반복
                self.root.after(100, update_gui)
            except Exception as e:
                self.logger.error(f"GUI 업데이트 중 오류: {e}")
        
        # 타이머 시작
        self.root.after(100, update_gui)
    
    def run(self):
        """GUI 애플리케이션 실행"""
        try:
            self.logger.info("Percenty GUI 애플리케이션을 시작합니다.")
            self.root.mainloop()
        except Exception as e:
            self.logger.error(f"GUI 실행 중 오류 발생: {e}")
        finally:
            self.logger.info("Percenty GUI 애플리케이션을 종료합니다.")

class GuiLogHandler(logging.Handler):
    """GUI 로그 출력을 위한 핸들러"""
    
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
        
    def emit(self, record):
        try:
            msg = self.format(record)
            # 메인 스레드에서 실행되도록 보장
            self.text_widget.after(0, self._append_log, msg)
        except Exception:
            self.handleError(record)
            
    def _append_log(self, msg):
        """로그 메시지를 텍스트 위젯에 추가"""
        self.text_widget.insert(tk.END, msg + '\n')
        self.text_widget.see(tk.END)
        
        # 로그가 너무 많이 쌓이지 않도록 제한
        lines = self.text_widget.get('1.0', tk.END).count('\n')
        if lines > 1000:
            self.text_widget.delete('1.0', '100.0')

def main():
    """메인 함수"""
    try:
        print("=== Percenty GUI 시작 ===")
        print("PercentyGUI 클래스 초기화 중...")
        app = PercentyGUI()
        print("PercentyGUI 초기화 완료")
        print("GUI 실행 시작...")
        app.run()
    except Exception as e:
        print(f"애플리케이션 실행 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        input("Enter 키를 눌러 종료하세요...")

if __name__ == "__main__":
    main()