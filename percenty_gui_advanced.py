# -*- coding: utf-8 -*-
"""
Percenty 고급 GUI - 다중 배치 실행기

기존 run_gui_multi_batch.py의 안정적인 구조를 기반으로
고급 기능을 추가한 현대적인 GUI 애플리케이션

주요 기능:
- 다중 계정 동시 실행 (subprocess 기반)
- 1-6단계 모든 지원
- 실시간 로그 모니터링
- 진행률 표시
- 설정 저장/로드
- 현대적인 UI 디자인
"""

import os
import sys
import time
import subprocess
import logging
import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
from pathlib import Path
import threading
from account_manager import AccountManager

# 주기적 실행 관리자 import
try:
    from core.periodic_execution_manager import PeriodicExecutionManager
except ImportError:
    print("Warning: 주기적 실행 관리자를 로드할 수 없습니다. core/periodic_execution_manager.py를 확인하세요.")
    PeriodicExecutionManager = None

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PercentyAdvancedGUI:
    """Percenty 고급 GUI 메인 클래스"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Percenty 고급 다중 배치 실행기")
        self.root.geometry("1000x900")
        self.root.configure(bg='#f0f0f0')
        
        # 실행 중인 프로세스들
        self.running_processes = []
        self.total_tasks = 0
        self.completed_tasks = 0
        
        # 주기적 실행 관리자 초기화
        if PeriodicExecutionManager:
            self.periodic_manager = PeriodicExecutionManager(log_callback=self._add_log)
        else:
            self.periodic_manager = None
        
        # 설정 파일 경로
        self.config_file = Path("percenty_gui_config.json")
        
        # UI 변수들
        self.setup_variables()
        
        # UI 초기화
        self._init_ui()
        
        # 설정 로드
        self.load_configuration()
        
        # 주기적 실행 설정 로드
        self._load_periodic_config()
        
        # 프로세스 모니터링 스레드
        self.monitoring_active = False
    
    def _add_product_count_summary(self):
        """상품수량 비교 정보를 요약에 추가"""
        try:
            import os
            import glob
            from datetime import datetime
            
            # 최신 보고서 디렉토리 찾기
            reports_dir = "logs/reports"
            if not os.path.exists(reports_dir):
                return
            
            # 가장 최근 보고서 디렉토리 찾기
            report_dirs = [d for d in os.listdir(reports_dir) if os.path.isdir(os.path.join(reports_dir, d))]
            if not report_dirs:
                return
            
            latest_dir = max(report_dirs)
            latest_report_path = os.path.join(reports_dir, latest_dir)
            
            # 배치 보고서 파일 찾기
            batch_reports = glob.glob(os.path.join(latest_report_path, "batch_report_*.md"))
            if not batch_reports:
                return
            
            # 가장 최근 배치 보고서 읽기
            latest_report = max(batch_reports, key=os.path.getmtime)
            
            total_before = 0
            total_after = 0
            total_processed = 0
            account_count = 0
            
            with open(latest_report, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # 상품수량 정보 추출
                import re
                before_matches = re.findall(r'실행 전 비그룹상품 수량.*?(\d+)개', content)
                after_matches = re.findall(r'실행 후 비그룹상품 수량.*?(\d+)개', content)
                processed_matches = re.findall(r'처리된 상품 수량.*?(\d+)개', content)
                
                if before_matches and after_matches and processed_matches:
                    for i in range(len(before_matches)):
                        total_before += int(before_matches[i])
                        total_after += int(after_matches[i])
                        total_processed += int(processed_matches[i])
                        account_count += 1
            
            if account_count > 0:
                self._add_log("")
                self._add_log("📈 상품수량 비교 요약:")
                self._add_log(f"   • 총 실행 전 비그룹상품: {total_before}개")
                self._add_log(f"   • 총 실행 후 비그룹상품: {total_after}개")
                self._add_log(f"   • 총 처리된 상품: {total_processed}개")
                
                actual_decrease = total_before - total_after
                if actual_decrease == total_processed:
                    self._add_log(f"   • ✅ 상태: 누락 없이 정상 처리 (처리량과 감소량 일치)")
                elif actual_decrease > total_processed:
                    self._add_log(f"   • ⚠️ 상태: 실제 감소량({actual_decrease}개)이 처리량({total_processed}개)보다 많음")
                elif actual_decrease < total_processed:
                    self._add_log(f"   • ⚠️ 상태: 실제 감소량({actual_decrease}개)이 처리량({total_processed}개)보다 적음")
                
                self._add_log(f"   • 📋 상세 보고서: {latest_report}")
                
        except Exception as e:
            self._add_log(f"상품수량 정보 수집 중 오류: {str(e)}")
        
    def setup_variables(self):
        """UI 변수들 초기화"""
        # 기본 설정
        self.quantity_var = tk.StringVar(value="5")
        self.interval_var = tk.StringVar(value="15")
        
        # 계정 관리자 초기화
        self.account_manager = AccountManager()
        self.available_accounts = []
        self.account_vars = {}  # 계정별 체크박스 변수
        
        # 계정 정보 로드
        self.load_account_data()
        
        # 단계 선택 (체크박스) - 1-6단계 지원 (2단계는 21, 22, 23으로, 3단계는 31, 32, 33으로, 5단계는 51, 52, 53으로 분리)
        self.step_vars = {}
        steps = ['1', '21', '22', '23', '31', '32', '33', '4', '51', '52', '53', '6']
        for step in steps:
            self.step_vars[step] = tk.BooleanVar(value=False)  # 기본적으로 아무것도 선택하지 않음
        
        # 고급 설정
        self.headless_var = tk.BooleanVar(value=False)
        self.auto_retry_var = tk.BooleanVar(value=True)
        self.max_retries_var = tk.StringVar(value="3")
        
        # 진행률
        self.progress_var = tk.DoubleVar()
        
        # 배치 결과 추적
        self.total_tasks = 0
        self.successful_tasks = 0
        self.failed_tasks = 0
        self.task_results = {}  # 계정별 결과 저장
        
    def _init_ui(self):
        """UI 초기화"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 제목
        title_label = ttk.Label(main_frame, text="Percenty 고급 다중 배치 실행기", 
                               font=("Arial", 18, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 탭 컨테이너
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 탭들 생성
        self.create_basic_tab()
        self.create_periodic_tab()
        self.create_advanced_tab()
        self.create_monitoring_tab()
        
        # 하단 제어 패널 (기본설정 탭에서만 표시되도록 제거)
        # self.create_control_panel(main_frame)
        
        # 상태바
        self.create_status_bar()
        
        # 계정 체크박스들 생성
        self.create_account_checkboxes()
        
    def create_basic_tab(self):
        """기본 설정 탭"""
        basic_frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(basic_frame, text="기본 설정")
        
        # 단계 선택 섹션
        step_frame = ttk.LabelFrame(basic_frame, text="실행할 단계 선택", padding=15)
        step_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 단계 체크박스들을 배치 (1, 21, 22, 23, 31, 32, 33, 4, 51, 52, 53, 6단계)
        step_labels = {
            '1': '단계 1',
            '21': '단계 2-1 (서버1)',
            '22': '단계 2-2 (서버2)',
            '23': '단계 2-3 (서버3)',
            '31': '단계 3-1 (서버1)',
            '32': '단계 3-2 (서버2)',
            '33': '단계 3-3 (서버3)',
            '4': '단계 4',
            '51': '단계 5-1',
            '52': '단계 5-2',
            '53': '단계 5-3',
            '6': '단계 6'
        }
        
        # 체크박스를 배치
        positions = [
            ('1', 0, 0), ('51', 0, 1), ('52', 0, 2), ('53', 0, 3),
            ('21', 1, 0), ('22', 1, 1), ('23', 1, 2), ('4', 1, 3),
            ('31', 2, 0), ('32', 2, 1), ('33', 2, 2), ('6', 2, 3)
        ]
        
        for step, row, col in positions:
            if step in self.step_vars:
                label_text = step_labels.get(step, f"단계 {step}")
                cb = ttk.Checkbutton(step_frame, text=label_text, variable=self.step_vars[step])
                cb.grid(row=row, column=col, sticky=tk.W, padx=10, pady=5)
        
        # 단계 선택 버튼들
        step_btn_frame = ttk.Frame(step_frame)
        step_btn_frame.grid(row=3, column=0, columnspan=3, pady=(10, 0))
        
        ttk.Button(step_btn_frame, text="모든 단계 선택", 
                  command=self.select_all_steps, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(step_btn_frame, text="선택 해제", 
                  command=self.clear_step_selection, width=10).pack(side=tk.LEFT, padx=5)
        
        # 계정 선택 섹션
        account_frame = ttk.LabelFrame(basic_frame, text="계정 선택", padding=15)
        account_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 계정 선택 버튼들
        account_btn_frame = ttk.Frame(account_frame)
        account_btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(account_btn_frame, text="모든 계정 선택", 
                  command=self.select_all_accounts, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(account_btn_frame, text="선택 해제", 
                  command=self.clear_account_selection, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(account_btn_frame, text="계정 새로고침", 
                  command=self.refresh_accounts, width=12).pack(side=tk.LEFT, padx=5)
        
        # 계정 체크박스들을 담을 스크롤 가능한 프레임
        self.account_scroll_frame = ttk.Frame(account_frame)
        self.account_scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        # 계정 체크박스들 생성
        self.create_account_checkboxes()
        
        # 배치 설정 섹션
        config_frame = ttk.LabelFrame(basic_frame, text="배치 설정", padding=15)
        config_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 설정 항목들을 그리드로 배치
        ttk.Label(config_frame, text="수량:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        quantity_entry = ttk.Entry(config_frame, textvariable=self.quantity_var, width=15)
        quantity_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 수량 설명 라벨
        quantity_desc = ttk.Label(config_frame, text="(단계 1,5: 상품 개수 / 단계 3: 청크 크기)", 
                                 foreground="gray")
        quantity_desc.grid(row=0, column=2, sticky=tk.W, padx=10, pady=5)
        
        ttk.Label(config_frame, text="실행 간격(초):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        interval_entry = ttk.Entry(config_frame, textvariable=self.interval_var, width=15)
        interval_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 간격 설명 라벨
        interval_desc = ttk.Label(config_frame, text="(단계 3 권장: 5-10초)", 
                                 foreground="gray")
        interval_desc.grid(row=1, column=2, sticky=tk.W, padx=10, pady=5)

        # 제어 패널을 기본 설정 탭 내부에 추가
        self.create_control_panel(basic_frame)
    
    def create_periodic_tab(self):
        """주기적 실행 탭"""
        periodic_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(periodic_frame, text="주기적 실행")
        
        # 배치 수량 설정 섹션
        batch_frame = ttk.LabelFrame(periodic_frame, text="배치 수량 설정", padding=5)
        batch_frame.pack(fill=tk.X, pady=(0, 5))
        
        # 배치 수량 입력
        quantity_frame = ttk.Frame(batch_frame)
        quantity_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(quantity_frame, text="배치 수량:").pack(side=tk.LEFT, padx=(0, 10))
        
        # 배치 수량 변수 초기화 (아직 없다면)
        if not hasattr(self, 'periodic_quantity_var'):
            self.periodic_quantity_var = tk.StringVar(value="100")
        
        quantity_entry = ttk.Entry(quantity_frame, textvariable=self.periodic_quantity_var, width=10)
        quantity_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(quantity_frame, text="개 (숫자만 입력)", foreground="gray").pack(side=tk.LEFT)
        
        # 단계별 청크 사이즈 설정 섹션
        chunk_frame = ttk.LabelFrame(periodic_frame, text="단계별 청크 사이즈 설정", padding=5)
        chunk_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 청크 사이즈 변수들 초기화
        if not hasattr(self, 'periodic_chunk_vars'):
            self.periodic_chunk_vars = {
                '1': tk.StringVar(value="10"),      # step1_core.py 기본값
                '21': tk.StringVar(value="5"),      # step2_1_core.py 기본값
                '22': tk.StringVar(value="5"),      # step2_2_core.py 기본값
                '23': tk.StringVar(value="5"),      # step2_3_core.py 기본값
                '31': tk.StringVar(value="2"),      # step3_1_core.py 기본값
                '32': tk.StringVar(value="2"),      # step3_2_core.py 기본값
                '33': tk.StringVar(value="2"),      # step3_3_core.py 기본값
                '4': tk.StringVar(value="자동"),     # step4는 자동으로 번역 가능한 수량 감지
                '51': tk.StringVar(value="10"),     # step5_1_core.py 기본값
                '52': tk.StringVar(value="10"),     # step5_2_core.py 기본값
                '53': tk.StringVar(value="10"),     # step5_3_core.py 기본값
            }
        
        # 청크 사이즈 입력 필드들을 그리드로 배치
        chunk_labels = {
            '1': '단계 1',
            '21': '단계 2-1',
            '22': '단계 2-2', 
            '23': '단계 2-3',
            '31': '단계 3-1',
            '32': '단계 3-2',
            '33': '단계 3-3',
            '4': '단계 4',
            '51': '단계 5-1',
            '52': '단계 5-2',
            '53': '단계 5-3'
        }
        
        # 청크 사이즈 입력 필드들을 6열로 배치
        chunk_grid_frame = ttk.Frame(chunk_frame)
        chunk_grid_frame.pack(fill=tk.X, pady=5)
        
        row = 0
        col = 0
        for step_id, label in chunk_labels.items():
            step_chunk_frame = ttk.Frame(chunk_grid_frame)
            step_chunk_frame.grid(row=row, column=col, padx=10, pady=5, sticky="w")
            
            ttk.Label(step_chunk_frame, text=f"{label}:", width=8).pack(side=tk.LEFT)
            chunk_entry = ttk.Entry(step_chunk_frame, textvariable=self.periodic_chunk_vars[step_id], width=5)
            
            # 4단계는 청크 사이즈를 사용하지 않으므로 비활성화
            if step_id == '4':
                chunk_entry.config(state='disabled')
            
            chunk_entry.pack(side=tk.LEFT, padx=(5, 0))
            
            col += 1
            if col >= 6:  # 6열로 배치
                col = 0
                row += 1
        
        # 청크 사이즈 설명
        chunk_info_frame = ttk.Frame(chunk_frame)
        chunk_info_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Label(chunk_info_frame, text="※ 청크 사이즈: 한 번에 처리할 항목 수 (작을수록 안정적, 클수록 빠름)", 
                 foreground="gray", font=("맑은 고딕", 8)).pack(side=tk.LEFT)
        
        # 4단계 특별 설명 추가
        chunk_info_frame2 = ttk.Frame(chunk_frame)
        chunk_info_frame2.pack(fill=tk.X, pady=(2, 0))
        ttk.Label(chunk_info_frame2, text="※ 단계 4: 번역 가능한 상품 수량을 자동으로 감지하여 처리 (청크 사이즈 불필요)", 
                 foreground="blue", font=("맑은 고딕", 8)).pack(side=tk.LEFT)
        
        # 단계 선택 섹션
        step_frame = ttk.LabelFrame(periodic_frame, text="실행할 단계 선택", padding=5)
        step_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 주기적 실행용 단계 변수들 초기화
        if not hasattr(self, 'periodic_step_vars'):
            self.periodic_step_vars = {}
            for step in ['1', '21', '22', '23', '31', '32', '33', '4', '51', '52', '53', '6']:
                self.periodic_step_vars[step] = tk.BooleanVar()
        
        # 단계 체크박스들을 배치
        step_labels = {
            '1': '단계 1',
            '21': '단계 2-1 (서버1)',
            '22': '단계 2-2 (서버2)',
            '23': '단계 2-3 (서버3)',
            '31': '단계 3-1 (서버1)',
            '32': '단계 3-2 (서버2)',
            '33': '단계 3-3 (서버3)',
            '4': '단계 4',
            '51': '단계 5-1',
            '52': '단계 5-2',
            '53': '단계 5-3',
            '6': '단계 6'
        }
        
        positions = [
            ('1', 0, 0), ('51', 0, 1), ('52', 0, 2), ('53', 0, 3),
            ('21', 1, 0), ('22', 1, 1), ('23', 1, 2), ('4', 1, 3),
            ('31', 2, 0), ('32', 2, 1), ('33', 2, 2), ('6', 2, 3)
        ]
        
        for step, row, col in positions:
            if step in self.periodic_step_vars:
                label_text = step_labels.get(step, f"단계 {step}")
                cb = ttk.Checkbutton(step_frame, text=label_text, variable=self.periodic_step_vars[step])
                cb.grid(row=row, column=col, sticky=tk.W, padx=10, pady=5)
        
        # 단계 선택 버튼들
        step_btn_frame = ttk.Frame(step_frame)
        step_btn_frame.grid(row=3, column=0, columnspan=4, pady=(10, 0))
        
        ttk.Button(step_btn_frame, text="모든 단계 선택", 
                  command=self.select_all_periodic_steps, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(step_btn_frame, text="선택 해제", 
                  command=self.clear_periodic_step_selection, width=10).pack(side=tk.LEFT, padx=5)
        
        # 계정 선택 섹션
        account_frame = ttk.LabelFrame(periodic_frame, text="계정 선택", padding=15)
        account_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 주기적 실행용 계정 변수들 초기화
        if not hasattr(self, 'periodic_account_vars'):
            self.periodic_account_vars = {}
        
        # 계정 선택 버튼들
        account_btn_frame = ttk.Frame(account_frame)
        account_btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(account_btn_frame, text="모든 계정 선택", 
                  command=self.select_all_periodic_accounts, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(account_btn_frame, text="선택 해제", 
                  command=self.clear_periodic_account_selection, width=10).pack(side=tk.LEFT, padx=5)
        
        # 계정 목록 표시
        periodic_account_list_frame = ttk.Frame(account_frame)
        periodic_account_list_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # 스크롤 가능한 계정 목록
        periodic_canvas = tk.Canvas(periodic_account_list_frame, height=100)
        periodic_scrollbar = ttk.Scrollbar(periodic_account_list_frame, orient="vertical", command=periodic_canvas.yview)
        periodic_scrollable_frame = ttk.Frame(periodic_canvas)
        
        periodic_scrollable_frame.bind(
            "<Configure>",
            lambda e: periodic_canvas.configure(scrollregion=periodic_canvas.bbox("all"))
        )
        
        periodic_canvas.create_window((0, 0), window=periodic_scrollable_frame, anchor="nw")
        periodic_canvas.configure(yscrollcommand=periodic_scrollbar.set)
        
        # 계정 목록 로드 및 체크박스 생성
        try:
            from account_manager import AccountManager
            account_manager = AccountManager()
            accounts = account_manager.get_accounts()
            
            # 주기적 실행용 계정 변수 초기화
            for account in accounts:
                account_id = account.get('id', str(account))
                if account_id not in self.periodic_account_vars:
                    self.periodic_account_vars[account_id] = tk.BooleanVar()
            
            # 계정 체크박스들을 3열로 배치
            row = 0
            col = 0
            for account in accounts:
                account_id = account.get('id', str(account))
                account_name = account.get('nickname', account_id)
                
                cb = ttk.Checkbutton(periodic_scrollable_frame, 
                                   text=f"{account_name} ({account_id})", 
                                   variable=self.periodic_account_vars[account_id])
                cb.grid(row=row, column=col, sticky=tk.W, padx=10, pady=2)
                
                col += 1
                if col >= 3:  # 3열로 배치
                    col = 0
                    row += 1
                    
        except Exception as e:
            # 계정 로드 실패 시 기본 메시지 표시
            ttk.Label(periodic_scrollable_frame, 
                     text=f"계정 로드 실패: {str(e)}", 
                     foreground="red").pack(pady=10)
        
        periodic_canvas.pack(side="left", fill="both", expand=True)
        periodic_scrollbar.pack(side="right", fill="y")
        
        # 스케줄 설정 섹션
        schedule_frame = ttk.LabelFrame(periodic_frame, text="주기적 실행 설정", padding=5)
        schedule_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 실행 시간 설정
        time_frame = ttk.Frame(schedule_frame)
        time_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(time_frame, text="매일 실행 시간:").pack(side=tk.LEFT, padx=(0, 10))
        
        # 시간 변수 초기화
        if not hasattr(self, 'periodic_hour_var'):
            self.periodic_hour_var = tk.StringVar(value="09")
        if not hasattr(self, 'periodic_minute_var'):
            self.periodic_minute_var = tk.StringVar(value="00")
        
        hour_entry = ttk.Entry(time_frame, textvariable=self.periodic_hour_var, width=5)
        hour_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Label(time_frame, text="시").pack(side=tk.LEFT, padx=(0, 10))
        
        minute_entry = ttk.Entry(time_frame, textvariable=self.periodic_minute_var, width=5)
        minute_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Label(time_frame, text="분").pack(side=tk.LEFT)
        
        # 주기적 실행 제어 버튼들
        control_frame = ttk.Frame(periodic_frame)
        control_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.periodic_start_button = tk.Button(control_frame, text="주기적 실행 시작", 
                                              command=self._start_periodic_execution,
                                              width=15, height=2,
                                              bg="#28a745", fg="white",
                                              font=("Arial", 10, "bold"))
        self.periodic_start_button.pack(side=tk.LEFT, padx=5)
        
        self.periodic_stop_button = tk.Button(control_frame, text="주기적 실행 중지", 
                                             command=self._stop_periodic_execution,
                                             state=tk.DISABLED,
                                             width=15, height=2,
                                             bg="#dc3545", fg="white",
                                             font=("Arial", 10, "bold"))
        self.periodic_stop_button.pack(side=tk.LEFT, padx=5)
        
        self.periodic_test_button = tk.Button(control_frame, text="즉시 실행 (테스트)", 
                                             command=self._test_periodic_execution,
                                             width=15, height=2,
                                             bg="#007bff", fg="white",
                                             font=("Arial", 10, "bold"))
        self.periodic_test_button.pack(side=tk.LEFT, padx=5)
                
    def create_advanced_tab(self):
        """고급 설정 탭"""
        advanced_frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(advanced_frame, text="고급 설정")
        
        # 브라우저 설정
        browser_frame = ttk.LabelFrame(advanced_frame, text="브라우저 설정", padding=15)
        browser_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Checkbutton(browser_frame, text="헤드리스 모드 (백그라운드 실행)", 
                       variable=self.headless_var).pack(anchor=tk.W, pady=5)
        
        # 오류 처리 설정
        error_frame = ttk.LabelFrame(advanced_frame, text="오류 처리", padding=15)
        error_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Checkbutton(error_frame, text="자동 재시도 활성화", 
                       variable=self.auto_retry_var).pack(anchor=tk.W, pady=5)
        
        retry_frame = ttk.Frame(error_frame)
        retry_frame.pack(fill=tk.X, pady=5)
        ttk.Label(retry_frame, text="최대 재시도 횟수:").pack(side=tk.LEFT)
        ttk.Entry(retry_frame, textvariable=self.max_retries_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # 설정 저장/로드
        config_mgmt_frame = ttk.LabelFrame(advanced_frame, text="설정 관리", padding=15)
        config_mgmt_frame.pack(fill=tk.X, pady=(0, 15))
        
        btn_frame = ttk.Frame(config_mgmt_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="설정 저장", 
                  command=self.save_configuration, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="설정 로드", 
                  command=self.load_configuration, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="기본값 복원", 
                  command=self.reset_to_defaults, width=12).pack(side=tk.LEFT, padx=5)
        
    def create_monitoring_tab(self):
        """모니터링 탭"""
        monitoring_frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(monitoring_frame, text="실행 모니터링")
        
        # 진행률 표시
        progress_frame = ttk.LabelFrame(monitoring_frame, text="전체 진행률", padding=15)
        progress_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100, length=400)
        self.progress_bar.pack(pady=5)
        
        self.progress_label = ttk.Label(progress_frame, text="0% (0/0)")
        self.progress_label.pack(pady=5)
        
        # 실행 상태 로그
        log_frame = ttk.LabelFrame(monitoring_frame, text="실행 로그", padding=15)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # 로그 텍스트 위젯
        self.log_text = scrolledtext.ScrolledText(log_frame, height=20, width=80)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 로그 제어 버튼
        log_btn_frame = ttk.Frame(log_frame)
        log_btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(log_btn_frame, text="로그 지우기", 
                  command=self.clear_log, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(log_btn_frame, text="로그 저장", 
                  command=self.save_log, width=10).pack(side=tk.LEFT, padx=5)
        
    def create_control_panel(self, parent):
        """제어 패널"""
        control_frame = ttk.Frame(parent, padding=10)
        control_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 실행 버튼들
        self.start_button = tk.Button(control_frame, text="다중 배치 시작", 
                                      command=self._start_multi_batch,
                                      width=15, height=3,
                                      bg="#0078d4", fg="black",
                                      font=("Arial", 10, "bold"))
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = tk.Button(control_frame, text="모든 배치 중지", 
                                     command=self._stop_all_batches,
                                     state=tk.DISABLED,
                                     width=15, height=3,
                                     bg="#d13438", fg="black",
                                     font=("Arial", 10, "bold"))
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # 상태 정보
        status_info_frame = ttk.Frame(control_frame)
        status_info_frame.pack(side=tk.RIGHT)
        
        self.process_count_label = ttk.Label(status_info_frame, text="실행 중: 0개")
        self.process_count_label.pack(side=tk.RIGHT, padx=10)
        
    def create_status_bar(self):
        """상태바"""
        self.status_var = tk.StringVar(value="준비")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def select_all_steps(self):
        """모든 단계 선택"""
        for var in self.step_vars.values():
            var.set(True)
        self._add_log("모든 단계가 선택되었습니다.")
        
    def clear_step_selection(self):
        """단계 선택 해제"""
        for var in self.step_vars.values():
            var.set(False)
        self._add_log("모든 단계 선택이 해제되었습니다.")
    
    def load_account_data(self):
        """계정 데이터 로드"""
        try:
            if self.account_manager.load_accounts():
                self.available_accounts = self.account_manager.accounts
                # 계정별 체크박스 변수 초기화
                self.account_vars = {}
                for i, account in enumerate(self.available_accounts):
                    # 계정 ID를 키로 사용 (1, 2, 3, 4 형태)
                    account_key = str(i + 1)
                    self.account_vars[account_key] = tk.BooleanVar(value=False)
                logger.info(f"{len(self.available_accounts)}개의 계정을 로드했습니다.")
            else:
                logger.warning("계정 정보를 로드할 수 없습니다. 기본 계정을 사용합니다.")
                # 기본 계정 설정 (1, 2, 3, 4)
                self.available_accounts = [
                    {'id': 'account1', 'nickname': '계정 1'},
                    {'id': 'account2', 'nickname': '계정 2'},
                    {'id': 'account3', 'nickname': '계정 3'},
                    {'id': 'account4', 'nickname': '계정 4'}
                ]
                self.account_vars = {}
                for i in range(1, 5):
                    self.account_vars[str(i)] = tk.BooleanVar(value=(i <= 3))  # 기본적으로 1,2,3 선택
        except Exception as e:
            logger.error(f"계정 데이터 로드 중 오류: {e}")
            # 오류 시 기본 계정 사용
            self.available_accounts = [
                {'id': 'account1', 'nickname': '계정 1'},
                {'id': 'account2', 'nickname': '계정 2'},
                {'id': 'account3', 'nickname': '계정 3'},
                {'id': 'account4', 'nickname': '계정 4'}
            ]
            self.account_vars = {}
            for i in range(1, 5):
                self.account_vars[str(i)] = tk.BooleanVar(value=(i <= 3))  # 기본적으로 1,2,3 선택
    
    def create_account_checkboxes(self):
        """계정 체크박스들 생성"""
        # 기존 체크박스들 제거
        for widget in self.account_scroll_frame.winfo_children():
            widget.destroy()
        
        if not self.available_accounts:
            ttk.Label(self.account_scroll_frame, text="사용 가능한 계정이 없습니다.").pack(pady=10)
            return
        
        # 계정 체크박스들을 2열로 배치
        for i, account in enumerate(self.available_accounts):
            account_key = str(i + 1)
            row = i // 2
            col = i % 2
            
            nickname = account.get('nickname', f"계정 {i+1}")
            account_id = account.get('id', f"account{i+1}")
            
            # 체크박스 텍스트: "계정 1 (account@email.com / operator)"
            operator = account.get('operator', '')
            checkbox_text = f"{account_key}. {nickname}"
            if account_id != nickname:
                if operator:
                    checkbox_text += f" ({account_id} / {operator})"
                else:
                    checkbox_text += f" ({account_id})"
            
            cb = ttk.Checkbutton(
                self.account_scroll_frame, 
                text=checkbox_text, 
                variable=self.account_vars[account_key]
            )
            cb.grid(row=row, column=col, sticky=tk.W, padx=10, pady=2)
    
    def select_all_accounts(self):
        """모든 계정 선택"""
        for var in self.account_vars.values():
            var.set(True)
    
    def clear_account_selection(self):
        """모든 계정 선택 해제"""
        for var in self.account_vars.values():
            var.set(False)
    
    def refresh_accounts(self):
        """계정 목록 새로고침"""
        self.load_account_data()
        self.create_account_checkboxes()
        self._add_log("계정 목록이 새로고침되었습니다.")
    
    def get_selected_accounts(self):
        """선택된 계정들 반환"""
        selected = []
        for account_key, var in self.account_vars.items():
            if var.get():
                selected.append(account_key)
        return selected
        
    def get_selected_steps(self):
        """선택된 단계 목록 반환"""
        return [step for step, var in self.step_vars.items() if var.get()]
        
    def _add_log(self, message):
        """로그 메시지 추가"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        self.root.update()
        
        # 콘솔에도 출력
        logger.info(message)
        
    def clear_log(self):
        """로그 지우기"""
        self.log_text.delete(1.0, tk.END)
        self._add_log("로그가 지워졌습니다.")
        
    def save_log(self):
        """로그 저장"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_filename = f"percenty_gui_log_{timestamp}.txt"
            
            with open(log_filename, 'w', encoding='utf-8') as f:
                f.write(self.log_text.get(1.0, tk.END))
            
            self._add_log(f"로그가 {log_filename}에 저장되었습니다.")
            messagebox.showinfo("성공", f"로그가 {log_filename}에 저장되었습니다.")
            
        except Exception as e:
            self._add_log(f"로그 저장 실패: {str(e)}")
            messagebox.showerror("오류", f"로그 저장 실패: {str(e)}")
            
    def save_configuration(self):
        """설정 저장"""
        try:
            config = {
                'quantity': self.quantity_var.get(),
                'selected_accounts': {account: var.get() for account, var in self.account_vars.items()},
                'interval': self.interval_var.get(),
                'selected_steps': {step: var.get() for step, var in self.step_vars.items()},
                'headless': self.headless_var.get(),
                'auto_retry': self.auto_retry_var.get(),
                'max_retries': self.max_retries_var.get(),
                'saved_at': datetime.now().isoformat()
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            self._add_log("설정이 저장되었습니다.")
            messagebox.showinfo("성공", "설정이 저장되었습니다.")
            
        except Exception as e:
            self._add_log(f"설정 저장 실패: {str(e)}")
            messagebox.showerror("오류", f"설정 저장 실패: {str(e)}")
            
    def load_configuration(self):
        """설정 로드"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # 설정 적용
                self.quantity_var.set(config.get('quantity', '5'))
                self.interval_var.set(config.get('interval', '5'))
                
                # 계정 선택 복원
                selected_accounts = config.get('selected_accounts', {})
                for account, var in self.account_vars.items():
                    var.set(selected_accounts.get(account, account in ['1', '2', '3']))
                
                # 단계 선택 복원
                selected_steps = config.get('selected_steps', {})
                for step, var in self.step_vars.items():
                    var.set(selected_steps.get(step, False))
                
                self.headless_var.set(config.get('headless', False))
                self.auto_retry_var.set(config.get('auto_retry', True))
                self.max_retries_var.set(config.get('max_retries', '3'))
                
                self._add_log("설정이 로드되었습니다.")
            else:
                self._add_log("설정 파일이 없습니다. 기본값을 사용합니다.")
                
        except Exception as e:
            self._add_log(f"설정 로드 실패: {str(e)}")
            messagebox.showerror("오류", f"설정 로드 실패: {str(e)}")
            
    def reset_to_defaults(self):
        """기본값 복원"""
        self.quantity_var.set("5")
        self.interval_var.set("5")
        
        # 계정 선택 초기화 (1,2,3 선택)
        for account, var in self.account_vars.items():
            var.set(account in ['1', '2', '3'])
        
        # 아무 단계도 선택하지 않음
        for step, var in self.step_vars.items():
            var.set(False)
        
        self.headless_var.set(False)
        self.auto_retry_var.set(True)
        self.max_retries_var.set("3")
        
        self._add_log("기본값으로 복원되었습니다.")
        
    def _start_multi_batch(self):
        """다중 배치 시작"""
        try:
            # 입력값 검증
            selected_steps = self.get_selected_steps()
            if not selected_steps:
                messagebox.showerror("오류", "실행할 단계를 선택해주세요.")
                return
            
            quantity = self.quantity_var.get().strip()
            interval = int(self.interval_var.get().strip())
            
            if not quantity:
                messagebox.showerror("오류", "수량을 입력해주세요.")
                return
            
            # 선택된 계정들 가져오기
            accounts = self.get_selected_accounts()
            if not accounts:
                messagebox.showerror("오류", "실행할 계정을 선택해주세요.")
                return
            
            # 총 작업 수 계산 및 결과 추적 초기화
            self.total_tasks = len(accounts) * len(selected_steps)
            self.completed_tasks = 0
            self.successful_tasks = 0
            self.failed_tasks = 0
            self.task_results = {}
            self.update_progress()
            
            self._add_log(f"=== 다중 배치 시작 ===")
            self._add_log(f"선택된 단계: {', '.join(selected_steps)}")
            self._add_log(f"수량: {quantity}")
            self._add_log(f"계정 목록: {', '.join(accounts)}")
            self._add_log(f"총 작업 수: {self.total_tasks}개")
            
            # UI 상태 변경
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.status_var.set("배치 실행 중...")
            
            # 기존 프로세스 정리
            self._stop_all_batches()
            
            # 각 계정별로 독립적인 프로세스 실행
            project_root = os.path.dirname(os.path.abspath(__file__))
            
            for account_idx, account in enumerate(accounts):
                for step_idx, step in enumerate(selected_steps):
                    self._add_log(f"계정 {account} - 단계 {step} 실행 중...")
                    
                    # Step 2 처리 (21, 22, 23을 step2_batch_runner.py로 실행)
                    if step in ['21', '22', '23']:
                        server_num = step[-1]  # 21->1, 22->2, 23->3
                        cmd = [
                            sys.executable,  # python.exe 경로
                            os.path.join(project_root, "step2_batch_runner.py"),
                            "--account", account,
                            "--server", server_num,
                            "--chunk-size", quantity,
                            "--gui"  # GUI 모드 플래그 추가 (프로세스 강제 종료 비활성화)
                        ]
                    # Step 3 처리 (31, 32, 33을 step3_batch_runner.py로 실행)
                    elif step in ['31', '32', '33']:
                        server_num = step[-1]  # 31->1, 32->2, 33->3
                        cmd = [
                            sys.executable,  # python.exe 경로
                            os.path.join(project_root, "step3_batch_runner.py"),
                            "--account", account,
                            "--server", server_num,
                            "--chunk-size", quantity,
                            "--gui"  # GUI 모드 플래그 추가 (프로세스 강제 종료 비활성화)
                        ]
                    # Step 4 처리 (step4_core.py 사용)
                    elif step == '4':
                        cmd = [
                            sys.executable,  # python.exe 경로
                            os.path.join(project_root, "core", "steps", "step4_core.py"),
                            "--account", account,
                            "--quantity", quantity
                        ]
                    else:
                        # 기존 단계들은 batch_cli.py 사용
                        cli_step = str(step)  # step을 문자열로 변환
                        cmd = [
                            sys.executable,  # python.exe 경로
                            os.path.join(project_root, "cli", "batch_cli.py"),
                            "single",
                            "--step", cli_step,
                            "--accounts", account,
                            "--quantity", quantity,
                            "--interval", str(interval)
                        ]
                    
                    # 헤드리스 모드 옵션 추가 (Step 2, 3가 아닌 경우에만)
                    if self.headless_var.get() and step not in ['21', '22', '23', '31', '32', '33']:
                        cmd.extend(["--headless"])
                    
                    try:
                        # 새로운 콘솔 창에서 프로세스 실행
                        process = subprocess.Popen(
                            cmd,
                            creationflags=subprocess.CREATE_NEW_CONSOLE,
                            cwd=project_root
                        )
                        
                        self.running_processes.append({
                            'process': process,
                            'account': account,
                            'step': step,
                            'started_at': time.time()
                        })
                        
                        self._add_log(f"계정 {account} - 단계 {step} 프로세스 시작됨 (PID: {process.pid})")
                        
                    except Exception as e:
                        self._add_log(f"계정 {account} - 단계 {step} 실행 실패: {str(e)}")
                    
                    # 다음 작업 실행 전 대기 (마지막 작업이 아닌 경우)
                    is_last_task = (account_idx == len(accounts) - 1) and (step_idx == len(selected_steps) - 1)
                    if not is_last_task:
                        self._add_log(f"{interval}초 대기 중...")
                        time.sleep(interval)
            
            self.update_process_count()
            self._add_log(f"모든 작업 실행 완료! 총 {len(self.running_processes)}개 프로세스 실행 중")
            
            # 프로세스 모니터링 시작
            self._start_process_monitoring()
            
        except Exception as e:
            self._add_log(f"다중 배치 시작 중 오류: {str(e)}")
            messagebox.showerror("오류", f"다중 배치 시작 실패: {str(e)}")
            self._reset_ui_state()
            
    def _stop_all_batches(self):
        """모든 배치 중지"""
        if not self.running_processes:
            self._add_log("실행 중인 프로세스가 없습니다.")
            return
        
        self._add_log(f"실행 중인 {len(self.running_processes)}개 프로세스 중지 중...")
        
        for proc_info in self.running_processes:
            try:
                process = proc_info['process']
                account = proc_info['account']
                step = proc_info.get('step', 'Unknown')
                
                if process.poll() is None:  # 프로세스가 아직 실행 중
                    process.terminate()
                    self._add_log(f"계정 {account} - 단계 {step} 프로세스 중지됨 (PID: {process.pid})")
                    
            except Exception as e:
                self._add_log(f"프로세스 중지 중 오류: {str(e)}")
        
        self.running_processes.clear()
        self.monitoring_active = False
    
    def _add_product_count_summary(self):
        """상품수량 비교 정보를 요약에 추가"""
        try:
            import os
            import glob
            from datetime import datetime
            
            # 최신 보고서 디렉토리 찾기
            reports_dir = "logs/reports"
            if not os.path.exists(reports_dir):
                return
            
            # 가장 최근 보고서 디렉토리 찾기
            report_dirs = [d for d in os.listdir(reports_dir) if os.path.isdir(os.path.join(reports_dir, d))]
            if not report_dirs:
                return
            
            latest_dir = max(report_dirs)
            latest_report_path = os.path.join(reports_dir, latest_dir)
            
            # 배치 보고서 파일 찾기
            batch_reports = glob.glob(os.path.join(latest_report_path, "batch_report_*.md"))
            if not batch_reports:
                return
            
            # 가장 최근 배치 보고서 읽기
            latest_report = max(batch_reports, key=os.path.getmtime)
            
            total_before = 0
            total_after = 0
            total_processed = 0
            account_count = 0
            
            with open(latest_report, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # 상품수량 정보 추출
                import re
                before_matches = re.findall(r'실행 전 비그룹상품 수량.*?(\d+)개', content)
                after_matches = re.findall(r'실행 후 비그룹상품 수량.*?(\d+)개', content)
                processed_matches = re.findall(r'처리된 상품 수량.*?(\d+)개', content)
                
                if before_matches and after_matches and processed_matches:
                    for i in range(len(before_matches)):
                        total_before += int(before_matches[i])
                        total_after += int(after_matches[i])
                        total_processed += int(processed_matches[i])
                        account_count += 1
            
            if account_count > 0:
                self._add_log("")
                self._add_log("📈 상품수량 비교 요약:")
                self._add_log(f"   • 총 실행 전 비그룹상품: {total_before}개")
                self._add_log(f"   • 총 실행 후 비그룹상품: {total_after}개")
                self._add_log(f"   • 총 처리된 상품: {total_processed}개")
                
                actual_decrease = total_before - total_after
                if actual_decrease == total_processed:
                    self._add_log(f"   • ✅ 상태: 누락 없이 정상 처리 (처리량과 감소량 일치)")
                elif actual_decrease > total_processed:
                    self._add_log(f"   • ⚠️ 상태: 실제 감소량({actual_decrease}개)이 처리량({total_processed}개)보다 많음")
                elif actual_decrease < total_processed:
                    self._add_log(f"   • ⚠️ 상태: 실제 감소량({actual_decrease}개)이 처리량({total_processed}개)보다 적음")
                
                self._add_log(f"   • 📋 상세 보고서: {latest_report}")
                
        except Exception as e:
            self._add_log(f"상품수량 정보 수집 중 오류: {str(e)}")
        self._reset_ui_state()
        self._add_log("모든 프로세스가 중지되었습니다.")
        
    def _reset_ui_state(self):
        """UI 상태 초기화"""
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("준비")
        self.update_process_count()
        
    def _start_process_monitoring(self):
        """프로세스 모니터링 시작"""
        if not self.monitoring_active:
            self.monitoring_active = True
            monitor_thread = threading.Thread(target=self._monitor_processes, daemon=True)
            monitor_thread.start()
            
    def _monitor_processes(self):
        """프로세스 모니터링 (별도 스레드)"""
        while self.monitoring_active and self.running_processes:
            completed_count = 0
            
            for proc_info in self.running_processes[:]:
                process = proc_info['process']
                account = proc_info['account']
                step = proc_info.get('step', 'Unknown')
                
                if process.poll() is not None:  # 프로세스 완료
                    self.running_processes.remove(proc_info)
                    completed_count += 1
                    
                    # 결과 코드 확인
                    exit_code = process.returncode
                    task_key = f"계정{account}_단계{step}"
                    
                    if exit_code == 0:
                        # 성공
                        self.successful_tasks += 1
                        self.task_results[task_key] = "성공"
                        self.root.after(0, lambda a=account, s=step: 
                                       self._add_log(f"계정 {a} - 단계 {s} 완료 (성공)"))
                    else:
                        # 실패
                        self.failed_tasks += 1
                        self.task_results[task_key] = f"실패 (코드: {exit_code})"
                        self.root.after(0, lambda a=account, s=step, c=exit_code: 
                                       self._add_log(f"계정 {a} - 단계 {s} 완료 (실패, 코드: {c})"))
                    
                    self.completed_tasks += 1
                    self.root.after(0, self.update_progress)
            
            if completed_count > 0:
                self.root.after(0, self.update_process_count)
            
            if not self.running_processes:
                # 모든 프로세스 완료
                self.root.after(0, self._show_batch_summary)
                self.root.after(0, self._reset_ui_state)
                break
            
            time.sleep(2)  # 2초마다 체크
        
        self.monitoring_active = False
    
    def _add_product_count_summary(self):
        """상품수량 비교 정보를 요약에 추가"""
        try:
            import os
            import glob
            from datetime import datetime
            
            # 최신 보고서 디렉토리 찾기
            reports_dir = "logs/reports"
            if not os.path.exists(reports_dir):
                return
            
            # 가장 최근 보고서 디렉토리 찾기
            report_dirs = [d for d in os.listdir(reports_dir) if os.path.isdir(os.path.join(reports_dir, d))]
            if not report_dirs:
                return
            
            latest_dir = max(report_dirs)
            latest_report_path = os.path.join(reports_dir, latest_dir)
            
            # 배치 보고서 파일 찾기
            batch_reports = glob.glob(os.path.join(latest_report_path, "batch_report_*.md"))
            if not batch_reports:
                return
            
            # 가장 최근 배치 보고서 읽기
            latest_report = max(batch_reports, key=os.path.getmtime)
            
            total_before = 0
            total_after = 0
            total_processed = 0
            account_count = 0
            
            with open(latest_report, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # 상품수량 정보 추출
                import re
                before_matches = re.findall(r'실행 전 비그룹상품 수량.*?(\d+)개', content)
                after_matches = re.findall(r'실행 후 비그룹상품 수량.*?(\d+)개', content)
                processed_matches = re.findall(r'처리된 상품 수량.*?(\d+)개', content)
                
                if before_matches and after_matches and processed_matches:
                    for i in range(len(before_matches)):
                        total_before += int(before_matches[i])
                        total_after += int(after_matches[i])
                        total_processed += int(processed_matches[i])
                        account_count += 1
            
            if account_count > 0:
                self._add_log("")
                self._add_log("📈 상품수량 비교 요약:")
                self._add_log(f"   • 총 실행 전 비그룹상품: {total_before}개")
                self._add_log(f"   • 총 실행 후 비그룹상품: {total_after}개")
                self._add_log(f"   • 총 처리된 상품: {total_processed}개")
                
                actual_decrease = total_before - total_after
                if actual_decrease == total_processed:
                    self._add_log(f"   • ✅ 상태: 누락 없이 정상 처리 (처리량과 감소량 일치)")
                elif actual_decrease > total_processed:
                    self._add_log(f"   • ⚠️ 상태: 실제 감소량({actual_decrease}개)이 처리량({total_processed}개)보다 많음")
                elif actual_decrease < total_processed:
                    self._add_log(f"   • ⚠️ 상태: 실제 감소량({actual_decrease}개)이 처리량({total_processed}개)보다 적음")
                
                self._add_log(f"   • 📋 상세 보고서: {latest_report}")
                
        except Exception as e:
            self._add_log(f"상품수량 정보 수집 중 오류: {str(e)}")
        
    def update_process_count(self):
        """실행 중인 프로세스 수 업데이트"""
        count = len(self.running_processes)
        self.process_count_label.config(text=f"실행 중: {count}개")
        
        if count == 0:
            self.status_var.set("준비")
        else:
            self.status_var.set(f"실행 중... ({count}개 프로세스)")
    
    def _show_batch_summary(self):
        """배치 작업 완료 후 결과 요약 표시"""
        self._add_log("=== 모든 배치 작업 완료 ===")
        self._add_log(f"📊 실행 결과 요약:")
        self._add_log(f"   • 총 작업 수: {self.total_tasks}개")
        self._add_log(f"   • ✅ 성공: {self.successful_tasks}개")
        self._add_log(f"   • ❌ 실패: {self.failed_tasks}개")
        
        if self.total_tasks > 0:
            success_rate = (self.successful_tasks / self.total_tasks) * 100
            self._add_log(f"   • 📈 성공률: {success_rate:.1f}%")
        
        # 상세 결과 표시
        if self.task_results:
            self._add_log("")
            self._add_log("📋 상세 결과:")
            for task_key, result in self.task_results.items():
                status_icon = "✅" if "성공" in result else "❌"
                self._add_log(f"   {status_icon} {task_key}: {result}")
        
        # 상품수량 비교 정보 추가
        self._add_product_count_summary()
        
        self._add_log("")
        if self.failed_tasks > 0:
            self._add_log("⚠️  실패한 작업이 있습니다. 로그를 확인하여 원인을 파악하세요.")
        else:
            self._add_log("🎉 모든 작업이 성공적으로 완료되었습니다!")
        
    def update_progress(self):
        """진행률 업데이트"""
        if self.total_tasks > 0:
            progress = (self.completed_tasks / self.total_tasks) * 100
            self.progress_var.set(progress)
            self.progress_label.config(text=f"{progress:.1f}% ({self.completed_tasks}/{self.total_tasks})")
        else:
            self.progress_var.set(0)
            self.progress_label.config(text="0% (0/0)")

    # 주기적 실행 관련 메서드들
    def _load_periodic_config(self):
        """주기적 실행 설정 로드"""
        try:
            config_file = "periodic_config.json"
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'periodic_config' in data:
                        config = data['periodic_config']
                        # 설정값들을 UI에 반영
                        if 'execution_time' in config:
                            self.periodic_time_var.set(config['execution_time'])
                        if 'selected_steps' in config:
                            for step, enabled in config['selected_steps'].items():
                                if step in self.periodic_step_vars:
                                    self.periodic_step_vars[step].set(enabled)
                        if 'selected_accounts' in config:
                            # 계정 선택 상태 복원 (필요시 구현)
                            pass
                        logger.info("주기적 실행 설정을 로드했습니다.")
            else:
                logger.info("주기적 실행 설정 파일이 없습니다. 기본값을 사용합니다.")
        except Exception as e:
            logger.error(f"주기적 실행 설정 로드 오류: {e}")
    
    def _save_periodic_config(self, config):
        """주기적 실행 설정 저장"""
        try:
            config_file = "periodic_config.json"
            data = {"periodic_config": config}
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info("주기적 실행 설정을 저장했습니다.")
        except Exception as e:
            logger.error(f"주기적 실행 설정 저장 오류: {e}")
    
    def select_all_periodic_steps(self):
        """주기적 실행 탭의 모든 단계 선택"""
        for var in self.periodic_step_vars.values():
            var.set(True)
    
    def clear_periodic_step_selection(self):
        """주기적 실행 탭의 단계 선택 해제"""
        for var in self.periodic_step_vars.values():
            var.set(False)
    
    def select_all_periodic_accounts(self):
        """주기적 실행 탭의 모든 계정 선택"""
        for var in self.periodic_account_vars.values():
            var.set(True)
    
    def clear_periodic_account_selection(self):
        """주기적 실행 탭의 계정 선택 해제"""
        for var in self.periodic_account_vars.values():
            var.set(False)
    
    def _start_periodic_execution(self):
        """주기적 실행 시작"""
        try:
            if not self.periodic_manager:
                messagebox.showerror("오류", "주기적 실행 관리자가 초기화되지 않았습니다.")
                return
            
            # 배치 수량 검증
            quantity_str = self.periodic_quantity_var.get().strip()
            if not quantity_str.isdigit():
                messagebox.showerror("오류", "배치 수량은 숫자만 입력해주세요.")
                return
            
            quantity = int(quantity_str)
            if quantity <= 0:
                messagebox.showerror("오류", "배치 수량은 1 이상이어야 합니다.")
                return
            
            # 시간 검증
            hour_str = self.periodic_hour_var.get().strip()
            minute_str = self.periodic_minute_var.get().strip()
            
            if not (hour_str.isdigit() and minute_str.isdigit()):
                messagebox.showerror("오류", "시간은 숫자만 입력해주세요.")
                return
            
            hour = int(hour_str)
            minute = int(minute_str)
            
            if not (0 <= hour <= 23) or not (0 <= minute <= 59):
                messagebox.showerror("오류", "올바른 시간을 입력해주세요. (시: 0-23, 분: 0-59)")
                return
            
            # 선택된 단계 확인
            selected_steps = [step for step, var in self.periodic_step_vars.items() if var.get()]
            if not selected_steps:
                messagebox.showerror("오류", "실행할 단계를 선택해주세요.")
                return
            
            # 선택된 계정 확인
            selected_accounts = [account for account, var in self.periodic_account_vars.items() if var.get()]
            if not selected_accounts:
                messagebox.showerror("오류", "실행할 계정을 선택해주세요.")
                return
            
            # 청크 사이즈 설정 수집
            chunk_sizes = {}
            for step_id, var in self.periodic_chunk_vars.items():
                chunk_str = var.get().strip()
                if chunk_str.isdigit() and int(chunk_str) > 0:
                    chunk_sizes[step_id] = int(chunk_str)
                else:
                    # 기본값 사용
                    default_chunks = {
                        '1': 10, '21': 5, '22': 5, '23': 5,
                        '31': 2, '32': 2, '33': 2, '4': 10,
                        '51': 10, '52': 10, '53': 10
                    }
                    chunk_sizes[step_id] = default_chunks.get(step_id, 10)
            
            # 주기적 실행 설정 구성
            schedule_time = f"{hour:02d}:{minute:02d}"
            config = {
                'batch_quantity': quantity,
                'selected_steps': selected_steps,
                'selected_accounts': selected_accounts,
                'schedule_time': schedule_time,
                'step_interval': 30,  # 단계 간 30초 대기
                'chunk_sizes': chunk_sizes  # 단계별 청크 사이즈 추가
            }
            
            # 설정 적용 및 스케줄러 시작
            self.periodic_manager.set_config(config)
            success = self.periodic_manager.start_periodic_execution()
            
            if success:
                # 성공 메시지
                message = f"주기적 실행이 시작되었습니다.\n\n"
                message += f"실행 시간: 매일 {schedule_time}\n"
                message += f"배치 수량: {quantity}개\n"
                message += f"선택된 단계: {', '.join(selected_steps)}\n"
                message += f"선택된 계정: {len(selected_accounts)}개"
                
                messagebox.showinfo("주기적 실행 시작", message)
                
                # UI 상태 변경
                self.periodic_start_button.config(state=tk.DISABLED)
                self.periodic_stop_button.config(state=tk.NORMAL)
                
                # 설정 저장
                self._save_periodic_config(config)
                
            else:
                messagebox.showerror("오류", "주기적 실행 시작에 실패했습니다. 로그를 확인하세요.")
            
        except Exception as e:
            messagebox.showerror("오류", f"주기적 실행 시작 중 오류가 발생했습니다: {str(e)}")
            logger.error(f"주기적 실행 시작 오류: {e}", exc_info=True)
    
    def _stop_periodic_execution(self):
        """주기적 실행 중지"""
        try:
            if not self.periodic_manager:
                messagebox.showerror("오류", "주기적 실행 관리자가 초기화되지 않았습니다.")
                return
            
            # 스케줄러 중지
            self.periodic_manager.stop_periodic_execution()
            
            messagebox.showinfo("주기적 실행 중지", "주기적 실행이 중지되었습니다.")
            
            # UI 상태 변경
            self.periodic_start_button.config(state=tk.NORMAL)
            self.periodic_stop_button.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("오류", f"주기적 실행 중지 중 오류가 발생했습니다: {str(e)}")
            logger.error(f"주기적 실행 중지 오류: {e}", exc_info=True)
    
    def _test_periodic_execution(self):
        """주기적 실행 테스트 (즉시 실행)"""
        try:
            if not self.periodic_manager:
                messagebox.showerror("오류", "주기적 실행 관리자가 초기화되지 않았습니다.")
                return
            
            # 배치 수량 검증
            quantity_str = self.periodic_quantity_var.get().strip()
            if not quantity_str.isdigit():
                messagebox.showerror("오류", "배치 수량은 숫자만 입력해주세요.")
                return
            
            quantity = int(quantity_str)
            if quantity <= 0:
                messagebox.showerror("오류", "배치 수량은 1 이상이어야 합니다.")
                return
            
            # 선택된 단계 확인
            selected_steps = [step for step, var in self.periodic_step_vars.items() if var.get()]
            if not selected_steps:
                messagebox.showerror("오류", "실행할 단계를 선택해주세요.")
                return
            
            # 선택된 계정 확인
            selected_accounts = [account for account, var in self.periodic_account_vars.items() if var.get()]
            if not selected_accounts:
                messagebox.showerror("오류", "실행할 계정을 선택해주세요.")
                return
            
            # 테스트 실행 (여기서는 메시지만 표시)
            message = f"테스트 실행이 시작됩니다.\n\n"
            message += f"배치 수량: {quantity}개\n"
            message += f"선택된 단계: {', '.join(selected_steps)}\n"
            message += f"선택된 계정: {len(selected_accounts)}개"
            
            messagebox.showinfo("테스트 실행", message)
            self._add_log(f"주기적 실행 테스트 시작: 배치 수량 {quantity}개, 단계 {', '.join(selected_steps)}")
            
        except Exception as e:
            messagebox.showerror("오류", f"테스트 실행 중 오류가 발생했습니다: {str(e)}")

def main():
    """메인 함수"""
    root = tk.Tk()
    
    # 스타일 설정
    style = ttk.Style()
    style.theme_use('clam')  # 현대적인 테마
    
    # 커스텀 스타일
    style.configure('Accent.TButton', foreground='white', background='#0078d4')
    
    app = PercentyAdvancedGUI(root)
    
    # 초기 메시지
    app._add_log("Percenty 고급 다중 배치 실행기가 준비되었습니다.")
    app._add_log("각 계정은 독립적인 프로세스에서 실행됩니다.")
    app._add_log("설정을 확인하고 '다중 배치 시작' 버튼을 클릭하세요.")
    
    root.mainloop()

if __name__ == "__main__":
    main()