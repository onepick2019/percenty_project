#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI 다중 배치 실행기

GUI에서 여러 계정을 독립적인 프로세스로 실행하는 스크립트
"""

import os
import sys
import time
import subprocess
import logging
import tkinter as tk
from tkinter import ttk, messagebox

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GUIMultiBatchLauncher:
    """GUI 다중 배치 실행기"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("퍼센티 다중 배치 실행기")
        self.root.geometry("600x500")
        
        # 실행 중인 프로세스들
        self.running_processes = []
        
        self._init_ui()
    
    def _init_ui(self):
        """UI 초기화"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 제목
        title_label = ttk.Label(main_frame, text="퍼센티 다중 배치 실행기", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # 설정 프레임
        config_frame = ttk.LabelFrame(main_frame, text="배치 설정", padding=10)
        config_frame.pack(fill=tk.X, pady=10)
        
        # 단계 선택
        ttk.Label(config_frame, text="단계:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.step_var = tk.StringVar(value="1")
        step_combo = ttk.Combobox(config_frame, textvariable=self.step_var, values=["1", "2", "3", "4", "5", "6"], width=10)
        step_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 수량 입력
        ttk.Label(config_frame, text="수량:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.quantity_var = tk.StringVar(value="5")
        quantity_entry = ttk.Entry(config_frame, textvariable=self.quantity_var, width=10)
        quantity_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 계정 선택
        ttk.Label(config_frame, text="계정들:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.accounts_var = tk.StringVar(value="1 2 3")
        accounts_entry = ttk.Entry(config_frame, textvariable=self.accounts_var, width=20)
        accounts_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(config_frame, text="(공백으로 구분)", font=("Arial", 8)).grid(row=2, column=2, sticky=tk.W, padx=5)
        
        # 실행 간격
        ttk.Label(config_frame, text="실행 간격(초):").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.interval_var = tk.StringVar(value="5")
        interval_entry = ttk.Entry(config_frame, textvariable=self.interval_var, width=10)
        interval_entry.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 버튼 프레임
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # 실행 버튼
        self.start_button = ttk.Button(button_frame, text="다중 배치 시작", command=self._start_multi_batch)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        # 중지 버튼
        self.stop_button = ttk.Button(button_frame, text="모든 배치 중지", command=self._stop_all_batches)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # 상태 프레임
        status_frame = ttk.LabelFrame(main_frame, text="실행 상태", padding=10)
        status_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 상태 텍스트
        self.status_text = tk.Text(status_frame, height=15, width=70)
        scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 초기 메시지
        self._add_status("다중 배치 실행기가 준비되었습니다.")
        self._add_status("각 계정은 독립적인 프로세스에서 실행됩니다.")
    
    def _add_status(self, message):
        """상태 메시지 추가"""
        timestamp = time.strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        self.root.update()
    
    def _start_multi_batch(self):
        """다중 배치 시작"""
        try:
            # 입력값 검증
            step = self.step_var.get().strip()
            quantity = self.quantity_var.get().strip()
            accounts_str = self.accounts_var.get().strip()
            interval = int(self.interval_var.get().strip())
            
            if not step or not quantity or not accounts_str:
                messagebox.showerror("오류", "모든 필드를 입력해주세요.")
                return
            
            # 계정 목록 파싱
            accounts = accounts_str.split()
            if not accounts:
                messagebox.showerror("오류", "계정을 입력해주세요.")
                return
            
            self._add_status(f"다중 배치 시작: 단계 {step}, 수량 {quantity}, 계정 {len(accounts)}개")
            self._add_status(f"계정 목록: {', '.join(accounts)}")
            
            # 기존 프로세스 정리
            self._stop_all_batches()
            
            # 각 계정별로 독립적인 프로세스 실행
            project_root = os.path.dirname(os.path.abspath(__file__))
            
            for i, account in enumerate(accounts):
                self._add_status(f"계정 {account} 실행 중...")
                
                cmd = [
                    sys.executable,  # python.exe 경로
                    os.path.join(project_root, "cli", "batch_cli.py"),
                    "single",
                    "--step", step,
                    "--account", account,
                    "--quantity", quantity
                ]
                
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
                        'started_at': time.time()
                    })
                    
                    self._add_status(f"계정 {account} 프로세스 시작됨 (PID: {process.pid})")
                    
                except Exception as e:
                    self._add_status(f"계정 {account} 실행 실패: {str(e)}")
                
                # 다음 계정 실행 전 대기
                if i < len(accounts) - 1:  # 마지막 계정이 아니면
                    self._add_status(f"{interval}초 대기 중...")
                    time.sleep(interval)
            
            self._add_status(f"모든 계정 실행 완료! 총 {len(self.running_processes)}개 프로세스 실행 중")
            
            # 프로세스 모니터링 시작
            self._start_process_monitoring()
            
        except Exception as e:
            self._add_status(f"다중 배치 시작 중 오류: {str(e)}")
            messagebox.showerror("오류", f"다중 배치 시작 실패: {str(e)}")
    
    def _stop_all_batches(self):
        """모든 배치 중지"""
        if not self.running_processes:
            self._add_status("실행 중인 프로세스가 없습니다.")
            return
        
        self._add_status(f"실행 중인 {len(self.running_processes)}개 프로세스 중지 중...")
        
        for proc_info in self.running_processes:
            try:
                process = proc_info['process']
                account = proc_info['account']
                
                if process.poll() is None:  # 프로세스가 아직 실행 중
                    process.terminate()
                    self._add_status(f"계정 {account} 프로세스 중지됨 (PID: {process.pid})")
                else:
                    self._add_status(f"계정 {account} 프로세스 이미 종료됨")
                    
            except Exception as e:
                self._add_status(f"프로세스 중지 중 오류: {str(e)}")
        
        self.running_processes.clear()
        self._add_status("모든 프로세스 중지 완료")
    
    def _start_process_monitoring(self):
        """프로세스 모니터링 시작"""
        def monitor():
            while self.running_processes:
                active_count = 0
                completed_processes = []
                
                for i, proc_info in enumerate(self.running_processes):
                    process = proc_info['process']
                    account = proc_info['account']
                    
                    if process.poll() is None:  # 아직 실행 중
                        active_count += 1
                    else:  # 완료됨
                        exit_code = process.returncode
                        if exit_code == 0:
                            self._add_status(f"계정 {account} 배치 완료 (성공)")
                        else:
                            self._add_status(f"계정 {account} 배치 완료 (오류 코드: {exit_code})")
                        completed_processes.append(i)
                
                # 완료된 프로세스 제거 (역순으로 제거)
                for i in reversed(completed_processes):
                    del self.running_processes[i]
                
                if active_count == 0:
                    self._add_status("모든 배치 작업이 완료되었습니다!")
                    break
                
                time.sleep(5)  # 5초마다 확인
        
        # 별도 스레드에서 모니터링
        import threading
        monitor_thread = threading.Thread(target=monitor)
        monitor_thread.daemon = True
        monitor_thread.start()
    
    def on_closing(self):
        """창 닫기 이벤트"""
        if self.running_processes:
            if messagebox.askokcancel("종료 확인", "실행 중인 배치가 있습니다. 모든 프로세스를 중지하고 종료하시겠습니까?"):
                self._stop_all_batches()
                self.root.destroy()
        else:
            self.root.destroy()

def main():
    """메인 함수"""
    root = tk.Tk()
    app = GUIMultiBatchLauncher(root)
    
    # 창 닫기 이벤트 처리
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    root.mainloop()

if __name__ == "__main__":
    main()