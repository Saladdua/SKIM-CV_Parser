# setup_wizard.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from config import DEFAULT_ADE_PARSE_ENDPOINT, DEFAULT_SCHEMA_DEFINITION
import os
import copy

class SetupWizardWindow:
    def __init__(self, parent, settings_mgr):
        self.settings_mgr = settings_mgr
        self.window = tk.Toplevel(parent)
        self.window.title("Cài đặt SKIM")
        self.window.geometry("600x550")
        
        # === SỬA LỖI QUAN TRỌNG ===
        # Đã xóa dòng self.window.transient(parent) để tránh bị ẩn theo cửa sổ chính
        self.window.grab_set() # Vẫn giữ quyền ưu tiên (không bấm được cửa sổ kia khi đang mở cái này)
        self.window.focus_force() # Bắt buộc hiện lên trên cùng
        # ==========================
        
        # Variables
        self.cred_path = tk.StringVar(value=settings_mgr.get("credentials_file", ""))
        self.ade_key = tk.StringVar(value=settings_mgr.get("ade_api_key", ""))
        self.sheet_id = tk.StringVar(value=settings_mgr.get("spreadsheet_id", ""))
        self.sheet_name = tk.StringVar(value=settings_mgr.get("sheet_name", ""))
        
        self._build_ui()
        
    def _build_ui(self):
        main = ttk.Frame(self.window, padding=20)
        main.pack(fill="both", expand=True)
        
        ttk.Label(main, text="Cấu hình Hệ thống", font=("Segoe UI", 16, "bold")).pack(pady=(0, 20))
        
        # 1. Credentials
        lf_cred = ttk.LabelFrame(main, text="1. Google Credentials (.json)", padding=10)
        lf_cred.pack(fill="x", pady=5)
        
        f_file = ttk.Frame(lf_cred)
        f_file.pack(fill="x")
        self.ent_cred = ttk.Entry(f_file, textvariable=self.cred_path)
        self.ent_cred.pack(side="left", fill="x", expand=True)
        ttk.Button(f_file, text="Chọn...", command=self.browse_cred).pack(side="right", padx=5)
        
        # 2. LandingAI
        lf_ade = ttk.LabelFrame(main, text="2. LandingAI API Key", padding=10)
        lf_ade.pack(fill="x", pady=5)
        ttk.Entry(lf_ade, textvariable=self.ade_key, show="*").pack(fill="x")
        
        # 3. Google Sheet
        lf_gs = ttk.LabelFrame(main, text="3. Google Sheet", padding=10)
        lf_gs.pack(fill="x", pady=5)
        
        ttk.Label(lf_gs, text="Spreadsheet ID:").pack(anchor="w")
        ttk.Entry(lf_gs, textvariable=self.sheet_id).pack(fill="x", pady=(0, 5))
        
        ttk.Label(lf_gs, text="Sheet Name (Tên tab):").pack(anchor="w")
        ttk.Entry(lf_gs, textvariable=self.sheet_name).pack(fill="x")
        
        # Buttons
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill="x", pady=20)
        ttk.Button(btn_frame, text="Lưu Cấu Hình", command=self.save).pack(side="right")
        ttk.Button(btn_frame, text="Hủy", command=self.window.destroy).pack(side="right", padx=10)

    def browse_cred(self):
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if path: self.cred_path.set(path)

    def save(self):
        if not all([self.cred_path.get(), self.ade_key.get(), self.sheet_id.get(), self.sheet_name.get()]):
            messagebox.showwarning("Thiếu thông tin", "Vui lòng điền đầy đủ các trường.")
            return
            
        self.settings_mgr.update("credentials_file", self.cred_path.get())
        self.settings_mgr.update("ade_api_key", self.ade_key.get())
        self.settings_mgr.update("spreadsheet_id", self.sheet_id.get())
        self.settings_mgr.update("sheet_name", self.sheet_name.get())
        
        if self.settings_mgr.save_settings():
            messagebox.showinfo("Thành công", "Đã lưu cấu hình.")
            self.window.destroy()
        else:
            messagebox.showerror("Lỗi", "Không thể lưu file settings.")