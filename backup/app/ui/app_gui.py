# -*- coding: utf-8 -*-
"""
퍼센티 자동화 앱 GUI

Tkinter를 사용한 간단한 GUI 구현
"""

import os
import time
import logging
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

logger = logging.getLogger(__name__)

class AppGUI:
    """퍼센티 자동화 앱 GUI 클래스"""
    
    def __init__(self, root, account_manager, task_manager, browser_manager):
        """
        초기화
        
        Args:
            root: Tkinter 루트 윈도우
            account_manager: 계정 관리자 인스턴스
            task_manager: 작업 관리자 인스턴스
            browser_manager: 브라우저 관리자 인스턴스
        """
        self.root = root
        self.account_manager = account_manager
        self.task_manager = task_manager
        self.browser_manager = browser_manager
        
        # GUI 상태 변수
        self.selected_account_id = tk.StringVar()
        self.selected_step = tk.IntVar(value=1)
        self.quantity_option = tk.StringVar(value="직접 입력")
        self.quantity = tk.StringVar(value="100")
        
        # 작업 상태 업데이트 스레드
        self.update_thread = None
        self.is_updating = False
        
        # GUI 초기화
        self._init_ui()
        
        # 작업 상태 업데이트 시작
        self._start_status_update()
    
    def _init_ui(self):
        """GUI 초기화"""
        # 프레임 생성
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 상단 프레임 (계정 및 작업 설정)
        self.top_frame = ttk.LabelFrame(self.main_frame, text="작업 설정", padding=10)
        self.top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 계정 선택
        ttk.Label(self.top_frame, text="계정 선택:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.account_combo = ttk.Combobox(self.top_frame, textvariable=self.selected_account_id, state="readonly", width=30)
        self.account_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self._update_account_list()
        
        # 단계 선택
        ttk.Label(self.top_frame, text="작업 단계:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        step_frame = ttk.Frame(self.top_frame)
        step_frame.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        for i in range(1, 7):
            ttk.Radiobutton(step_frame, text=f"{i}단계", variable=self.selected_step, value=i).pack(side=tk.LEFT, padx=5)
        
        # 수량 선택
        ttk.Label(self.top_frame, text="작업 수량:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        quantity_frame = ttk.Frame(self.top_frame)
        quantity_frame.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 수량 옵션
        quantity_options = ["직접 입력", "100개", "200개", "300개", "400개", "500개"]
        self.quantity_option_combo = ttk.Combobox(quantity_frame, textvariable=self.quantity_option, 
                                                 values=quantity_options, state="readonly", width=10)
        self.quantity_option_combo.pack(side=tk.LEFT, padx=5)
        self.quantity_option_combo.bind("<<ComboboxSelected>>", self._on_quantity_option_change)
        
        # 직접 입력 필드
        self.quantity_entry = ttk.Entry(quantity_frame, textvariable=self.quantity, width=10)
        self.quantity_entry.pack(side=tk.LEFT, padx=5)
        
        # 버튼 프레임
        button_frame = ttk.Frame(self.top_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        # 시작 버튼
        self.start_button = ttk.Button(button_frame, text="작업 시작", command=self._start_task, width=15)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        # 중지 버튼
        self.stop_button = ttk.Button(button_frame, text="작업 중지", command=self._stop_task, width=15, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # 상태 프레임
        self.status_frame = ttk.LabelFrame(self.main_frame, text="작업 상태", padding=10)
        self.status_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 작업 목록
        ttk.Label(self.status_frame, text="실행 중인 작업:").pack(anchor=tk.W, padx=5, pady=5)
        
        # 트리뷰 생성 (작업 목록 표시)
        columns = ("계정", "단계", "상태", "진행률", "시작 시간")
        self.task_tree = ttk.Treeview(self.status_frame, columns=columns, show="headings", height=5)
        
        # 컬럼 설정
        for col in columns:
            self.task_tree.heading(col, text=col)
            self.task_tree.column(col, width=100)
        
        # 스크롤바 추가
        tree_scroll = ttk.Scrollbar(self.status_frame, orient="vertical", command=self.task_tree.yview)
        self.task_tree.configure(yscrollcommand=tree_scroll.set)
        
        # 배치
        self.task_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 5), pady=5)
        
        # 로그 프레임
        self.log_frame = ttk.LabelFrame(self.main_frame, text="로그", padding=10)
        self.log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 로그 텍스트 영역
        self.log_text = scrolledtext.ScrolledText(self.log_frame, height=10, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 로그 핸들러 설정
        self._setup_log_handler()
    
    def _update_account_list(self):
        """계정 목록 업데이트"""
        accounts = self.account_manager.get_account_list()
        account_items = [f"{account_id}. {account_info.get('name', '')} ({account_info.get('id', '')})" 
                        for account_id, account_info in accounts]
        
        self.account_combo["values"] = account_items
        
        if account_items:
            self.account_combo.current(0)
            self.selected_account_id.set(accounts[0][0])
    
    def _on_quantity_option_change(self, event):
        """수량 옵션 변경 시 처리"""
        option = self.quantity_option.get()
        
        if option == "직접 입력":
            self.quantity_entry.configure(state="normal")
        else:
            # 숫자만 추출
            import re
            quantity_match = re.search(r'(\d+)', option)
            if quantity_match:
                self.quantity.set(quantity_match.group(1))
            
            self.quantity_entry.configure(state="readonly")
    
    def _setup_log_handler(self):
        """로그 핸들러 설정"""
        # GUI 로그 핸들러
        class TextHandler(logging.Handler):
            def __init__(self, text_widget):
                logging.Handler.__init__(self)
                self.text_widget = text_widget
            
            def emit(self, record):
                msg = self.format(record)
                
                def append():
                    self.text_widget.configure(state="normal")
                    self.text_widget.insert(tk.END, msg + "\n")
                    self.text_widget.configure(state="disabled")
                    self.text_widget.yview(tk.END)
                
                # GUI 스레드에서 안전하게 실행
                self.text_widget.after(0, append)
        
        # 핸들러 생성 및 설정
        text_handler = TextHandler(self.log_text)
        text_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        
        # 루트 로거에 핸들러 추가
        root_logger = logging.getLogger()
        root_logger.addHandler(text_handler)
    
    def _start_status_update(self):
        """작업 상태 업데이트 스레드 시작"""
        self.is_updating = True
        
        def update_status():
            while self.is_updating:
                try:
                    self._update_task_status()
                except Exception as e:
                    logger.error(f"작업 상태 업데이트 중 오류: {str(e)}")
                
                time.sleep(1)
        
        self.update_thread = threading.Thread(target=update_status)
        self.update_thread.daemon = True
        self.update_thread.start()
    
    def _update_task_status(self):
        """작업 상태 업데이트"""
        # 실행 중인 작업 목록 가져오기
        tasks = self.task_manager.get_all_tasks()
        
        # 트리뷰 아이템 초기화
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        
        # 작업 정보 추가
        for task in tasks:
            account_info = task.get("account_info", {})
            batch_info = task.get("batch_info", {})
            
            account_name = account_info.get("name", "") or account_info.get("id", "")
            step = batch_info.get("step_number", "")
            status = task.get("status", "")
            progress = f"{task.get('progress', 0)}%"
            created_at = task.get("created_at", "").split("T")[0] + " " + task.get("created_at", "").split("T")[1][:8]
            
            # 상품 수량 정보 추가 (완료된 작업에만 표시)
            product_info = ""
            if status == "completed" and task.get("initial_product_count") is not None:
                initial_count = task.get("initial_product_count", 0)
                final_count = task.get("final_product_count", 0)
                processed_count = task.get("processed_count", 0)
                actual_processed = task.get("actual_processed_count", 0)
                
                if actual_processed is not None:
                    if actual_processed == processed_count:
                        status_icon = "✅"
                        status_text = "정상 처리"
                    elif actual_processed > processed_count:
                        status_icon = "⚠️"
                        status_text = f"초과 처리 (+{actual_processed - processed_count})"
                    else:
                        status_icon = "⚠️"
                        status_text = f"누락 가능 (-{processed_count - actual_processed})"
                    
                    product_info = f" | 처리: {processed_count}개 → 실제: {actual_processed}개 | {status_icon} {status_text}"
            
            display_status = status + product_info
            
            self.task_tree.insert("", tk.END, values=(account_name, f"{step}단계", display_status, progress, created_at))
        
        # 버튼 상태 업데이트
        running_tasks = [task for task in tasks if task["status"] == "running"]
        
        if running_tasks:
            self.stop_button.configure(state=tk.NORMAL)
        else:
            self.stop_button.configure(state=tk.DISABLED)
    
    def _get_selected_account_info(self):
        """선택된 계정 정보 가져오기"""
        account_id = self.selected_account_id.get().split(".")[0]
        return self.account_manager.get_account(account_id)
    
    def _start_task(self):
        """작업 시작"""
        try:
            # 계정 정보 가져오기
            account_info = self._get_selected_account_info()
            if not account_info:
                messagebox.showerror("오류", "계정 정보를 가져올 수 없습니다.")
                return
            
            # 수량 가져오기
            try:
                quantity = int(self.quantity.get())
                if quantity <= 0:
                    raise ValueError("수량은 양수여야 합니다.")
            except ValueError as e:
                messagebox.showerror("오류", f"유효하지 않은 수량: {str(e)}")
                return
            
            # 브라우저 생성
            account_id = self.selected_account_id.get().split(".")[0]
            driver = self.browser_manager.create_browser(account_id)
            
            if not driver:
                messagebox.showerror("오류", "브라우저를 생성할 수 없습니다.")
                return
            
            # 작업 생성
            step_number = self.selected_step.get()
            task_id = self.task_manager.create_task(account_info, step_number, quantity, driver)
            
            if not task_id:
                messagebox.showerror("오류", "작업을 생성할 수 없습니다.")
                return
            
            # 작업 시작
            success = self.task_manager.start_task(task_id)
            
            if success:
                messagebox.showinfo("알림", f"작업이 시작되었습니다.\n계정: {account_info.get('name')}\n단계: {step_number}\n수량: {quantity}")
            else:
                messagebox.showerror("오류", "작업을 시작할 수 없습니다.")
            
        except Exception as e:
            messagebox.showerror("오류", f"작업 시작 중 오류 발생: {str(e)}")
    
    def _stop_task(self):
        """작업 중지"""
        try:
            # 선택된 작업 가져오기
            selection = self.task_tree.selection()
            
            if not selection:
                messagebox.showerror("오류", "중지할 작업을 선택하세요.")
                return
            
            # 모든 실행 중인 작업 가져오기
            tasks = self.task_manager.get_all_tasks(status="running")
            
            if not tasks:
                messagebox.showerror("오류", "실행 중인 작업이 없습니다.")
                return
            
            # 작업 중지
            for task in tasks:
                self.task_manager.stop_task(task["id"])
            
            messagebox.showinfo("알림", "작업 중지 요청이 전송되었습니다.")
            
        except Exception as e:
            messagebox.showerror("오류", f"작업 중지 중 오류 발생: {str(e)}")
    
    def on_closing(self):
        """앱 종료 시 처리"""
        try:
            # 작업 상태 업데이트 중지
            self.is_updating = False
            
            if self.update_thread:
                self.update_thread.join(timeout=1)
            
            # 모든 브라우저 종료
            self.browser_manager.close_all_browsers()
            
            # 창 종료
            self.root.destroy()
            
        except Exception as e:
            logger.error(f"앱 종료 중 오류: {str(e)}")
