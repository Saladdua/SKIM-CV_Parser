# main_app.py
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter.font import Font
import threading
import os
import json
import copy
import unicodedata
from config import resource_path, DEFAULT_SCHEMA_DEFINITION
from settings_manager import SettingsManager
from setup_wizard import SetupWizardWindow
from schema_editor import SchemaEditorWindow
from filter_editor import FilterEditorWindow

# App state
selected_files = []
extracted_results = []
user_email = None
creds = None
settings_mgr = SettingsManager()
txt_log = None
root = None

# UI Components
btn_choose = None
btn_process = None
btn_convert = None
btn_config = None
btn_schema = None
filter_combobox = None
selected_filter_var = None
login_frame = None
main_frame = None
lbl_user = None
lbl_files = None
txt_preview = None
btn_login = None
lbl_warning_bar = None
action_frame = None

# --- LOGIC LỌC (Giữ nguyên) ---
def normalize_text(text):
    if not text: return ""
    text = str(text).lower()
    text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')
    return text

def get_filters_from_settings():
    filters = settings_mgr.get("custom_filters", {})
    if not filters: return {"Mặc định (Không lọc)": {}}
    return filters

def validate_cv(cv_data, filter_name):
    all_filters = get_filters_from_settings()
    rules = all_filters.get(filter_name, {})
    if not rules: return True, "Không áp dụng quy tắc"

    school = normalize_text(cv_data.get("hoc_van_truong_hoc", ""))
    try:
        exp_str = str(cv_data.get("so_nam_kn", "0")).replace(",", ".").strip()
        import re
        num_match = re.search(r"(\d+(\.\d+)?)", exp_str)
        exp = float(num_match.group(1)) if num_match else 0.0
    except: exp = 0.0

    for bad_school in rules.get("excluded_schools", []):
        if bad_school and normalize_text(bad_school) in school:
            return False, f"Trường bị loại trừ: {bad_school}"

    preferred = rules.get("preferred_schools", [])
    if preferred:
        found = False
        for good_school in preferred:
            if good_school and normalize_text(good_school) in school:
                found = True; break
        if not found and school:
             return False, f"Trường không thuộc ưu tiên."

    min_e = rules.get("min_exp", 0)
    max_e = rules.get("max_exp", 100)
    if exp < min_e: return False, f"Kinh nghiệm {exp} < {min_e}"
    if exp > max_e: return False, f"Kinh nghiệm {exp} > {max_e}"

    return True, "Đạt yêu cầu"

# --- HÀM HỖ TRỢ ---
def check_and_setup_if_needed(root_window):
    if not settings_mgr.is_configured():
        print("[INFO] Config missing. Opening wizard...")
        wizard = SetupWizardWindow(root_window, settings_mgr)
        root_window.wait_window(wizard.window) 
        if not settings_mgr.is_configured():
            log("Cài đặt chưa hoàn tất.", "error")
            return False
    return True

def log(msg, level="info"):
    global txt_log, root
    if not txt_log or not root: print(f"[{level}] {msg}"); return
    try: root.after(0, _log_update, msg, level)
    except: pass

def _log_update(msg, tag):
    try:
        txt_log.config(state=tk.NORMAL)
        txt_log.insert(tk.END, f"[{tag.upper()}] {msg}\n", tag)
        txt_log.config(state=tk.DISABLED)
        txt_log.see(tk.END)
    except: pass

def toggle_app_state(enabled: bool):
    state = tk.NORMAL if enabled else tk.DISABLED
    btn_choose.config(state=state)
    filter_combobox.config(state="readonly" if enabled else "disabled")
    if enabled:
        lbl_warning_bar.config(text="")
        lbl_warning_bar.pack_forget()
    else:
        lbl_warning_bar.config(text="⚠ Vui lòng nhấn 'Cấu hình' để nhập thông tin hệ thống")
        lbl_warning_bar.pack(fill="x", before=action_frame)

# --- TÍNH NĂNG IMPORT / EXPORT ---
def export_config():
    path = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON Config", "*.json")],
        title="Xuất cấu hình (Bộ lọc & Schema)"
    )
    if path:
        success, msg = settings_mgr.export_shareable_config(path)
        if success:
            messagebox.showinfo("Xuất thành công", f"Đã lưu file tại:\n{path}")
            log(f"Đã xuất cấu hình ra: {os.path.basename(path)}", "success")
        else:
            messagebox.showerror("Lỗi xuất", msg)

def import_config():
    path = filedialog.askopenfilename(
        filetypes=[("JSON Config", "*.json")],
        title="Nhập cấu hình từ đồng nghiệp"
    )
    if path:
        if messagebox.askyesno("Xác nhận nhập", "Bạn có chắc muốn nhập cấu hình này?\nCác bộ lọc mới sẽ được thêm vào.\nSchema hiện tại sẽ bị thay thế."):
            success, msg = settings_mgr.import_shareable_config(path)
            if success:
                messagebox.showinfo("Nhập thành công", msg)
                log(f"Đã nhập cấu hình từ: {os.path.basename(path)}", "success")
                refresh_filter_combobox() # Cập nhật ngay dropdown
            else:
                messagebox.showerror("Lỗi nhập", msg)


# --- WORKER THREADS (Giữ nguyên) ---
def do_login_thread():
    global creds, user_email
    try: from google_sheets import get_creds
    except: log("Thiếu google_sheets.py", "error"); return

    try:
        log("Đang xác thực Google...", "info")
        root.after(0, lambda: btn_login.config(state=tk.DISABLED, text="Đang chờ..."))
        creds = get_creds(interactive=True)
        idinfo = {}
        if creds:
            try:
                from googleapiclient.discovery import build
                service = build('oauth2', 'v2', credentials=creds)
                idinfo = service.userinfo().get().execute()
            except: pass
        user_email = idinfo.get("email") or "Admin"
        root.after(0, _login_success_ui)
    except Exception as e:
        log(f"Lỗi login: {e}", "error")
        root.after(0, lambda: btn_login.config(state=tk.NORMAL, text="Thử lại"))

def _login_success_ui():
    lbl_user.config(text=f"User: {user_email}")
    log(f"Đăng nhập thành công: {user_email}", "success")
    login_frame.pack_forget()
    main_frame.pack(fill="both", expand=True)
    btn_config.config(state=tk.NORMAL)
    btn_schema.config(state=tk.NORMAL)
    refresh_filter_combobox()
    if settings_mgr.is_configured(): toggle_app_state(True)
    else: toggle_app_state(False)

# --- MAIN LOGIC (Giữ nguyên) ---
def choose_files():
    global selected_files
    if not settings_mgr.is_configured():
        messagebox.showwarning("Chưa cấu hình", "Vui lòng vào 'Cấu hình' trước.")
        return
    files = filedialog.askopenfilenames(title="Chọn CV", filetypes=[("CV", "*.pdf *.docx *.doc")])
    if files:
        selected_files = list(files)
        lbl_files.config(text=f"Đã chọn {len(selected_files)} file")
        log(f"Đã chọn {len(selected_files)} files.", "info")
        btn_process.config(state=tk.NORMAL)

def process_files_thread():
    global extracted_results
    try: from ade_extractor import extract_schema_from_file
    except: log("Thiếu ade_extractor.py", "error"); return
    if not selected_files: return
    root.after(0, lambda: _set_buttons_state(tk.DISABLED))
    extracted_results = []
    for i, fp in enumerate(selected_files, start=1):
        fname = os.path.basename(fp)
        log(f"Đang đọc: {fname}...", "info")
        try:
            extracted = extract_schema_from_file(fp)
            extracted_results.append(extracted)
            json_str = json.dumps(extracted, ensure_ascii=False, indent=2)
            root.after(0, _preview_append, f"--- {fname} ---\n{json_str}\n\n")
            log(f"Xong: {fname}", "success")
        except Exception as e:
            log(f"Lỗi file {fname}: {e}", "error")
    log("Hoàn tất.", "success")
    root.after(0, lambda: _set_buttons_state(tk.NORMAL))

def _set_buttons_state(state):
    btn_process.config(state=state)
    btn_choose.config(state=state)
    if extracted_results: btn_convert.config(state=tk.NORMAL)

def _preview_append(text):
    txt_preview.config(state=tk.NORMAL)
    txt_preview.insert(tk.END, text)
    txt_preview.config(state=tk.DISABLED)
    txt_preview.see(tk.END)

def convert_and_upload_thread():
    global creds
    try:
        from json_to_csv import build_data_for_sheet
        from google_sheets import append_values_to_sheet
        from config import get_sheet_name
    except: log("Lỗi import", "error"); return

    if not extracted_results: return
    if not creds: log("Mất kết nối Google.", "error"); return
    root.after(0, lambda: btn_convert.config(state=tk.DISABLED))
    filter_name = selected_filter_var.get()
    log(f"Lọc theo: {filter_name}", "warning")
    valid_results = []
    for cv in extracted_results:
        is_valid, reason = validate_cv(cv, filter_name)
        cv_name = cv.get("ho_ten", "CV không tên")
        if is_valid:
            valid_results.append(cv)
            log(f"  [PASS] {cv_name}", "success")
        else:
            log(f"  [LOẠI] {cv_name}: {reason}", "error")
    if not valid_results:
        log("Không có CV đạt yêu cầu.", "warning")
        messagebox.showwarning("Kết quả", "Tất cả CV đều bị loại.")
        root.after(0, lambda: btn_convert.config(state=tk.NORMAL))
        return
    try:
        current_schema = settings_mgr.get("schema_definition", DEFAULT_SCHEMA_DEFINITION)
        headers, data_rows = build_data_for_sheet(valid_results, user_email, current_schema)
        target_sheet = get_sheet_name()
        res = append_values_to_sheet(data_rows, creds, target_sheet)
        updated = res.get('updates', {}).get('updatedRows', 0)
        log(f"Upload thành công {updated} dòng!", "success")
        messagebox.showinfo("Thành công", f"Đã đẩy {updated} ứng viên.")
    except Exception as e:
        log(f"Lỗi Upload: {e}", "error")
        messagebox.showerror("Lỗi", str(e))
    finally:
        root.after(0, lambda: btn_convert.config(state=tk.NORMAL))

# --- UI & POPUPS ---
def open_settings():
    wizard = SetupWizardWindow(root, settings_mgr)
    root.wait_window(wizard.window)
    check_config_and_toggle_app()

def open_schema_editor():
    editor = SchemaEditorWindow(root, settings_mgr)
    root.wait_window(editor.window)

def open_filter_editor():
    editor = FilterEditorWindow(root, settings_mgr)
    root.wait_window(editor.window)
    refresh_filter_combobox()

def refresh_filter_combobox():
    filters = get_filters_from_settings()
    names = list(filters.keys())
    filter_combobox['values'] = names
    if names: filter_combobox.current(0)
    else: selected_filter_var.set("Mặc định")

def check_config_and_toggle_app():
    if settings_mgr.is_configured():
        lbl_warning_bar.pack_forget()
        if os.path.exists("token.json"):
            threading.Thread(target=do_login_thread).start()
    else:
        lbl_warning_bar.config(text="⚠ Chưa cấu hình. Vui lòng bấm 'Cấu hình'.")
        lbl_warning_bar.pack(fill="x", before=action_frame)
        btn_choose.config(state=tk.DISABLED)

def create_main_window():
    global root, txt_log, txt_preview, login_frame, main_frame
    global lbl_user, lbl_files, btn_login, btn_choose, btn_process, btn_convert
    global btn_config, btn_schema, btn_filter
    global filter_combobox, selected_filter_var, lbl_warning_bar, action_frame

    root = tk.Tk()
    root.title("SKIM - CV Parser")
    root.geometry("1000x700")
    
    try: root.iconbitmap(resource_path('app_icon.ico'))
    except: pass

    # === THÊM MENU BAR ===
    menubar = tk.Menu(root)
    root.config(menu=menubar)
    
    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="Nhập Cấu hình (Import)...", command=import_config)
    file_menu.add_command(label="Xuất Cấu hình (Export)...", command=export_config)
    file_menu.add_separator()
    file_menu.add_command(label="Thoát", command=root.quit)
    # =====================

    style = ttk.Style()
    style.configure("Bold.TLabel", font=("Segoe UI", 10, "bold"))
    style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"), foreground="#6610f2")
    
    login_frame = ttk.Frame(root)
    lf_content = ttk.Frame(login_frame)
    lf_content.place(relx=0.5, rely=0.5, anchor="center")
    ttk.Label(lf_content, text="SKIM CV PARSER", font=("Segoe UI", 24, "bold"), foreground="#6610f2").pack(pady=20)
    btn_login = ttk.Button(lf_content, text="Đăng nhập Google", command=lambda: threading.Thread(target=do_login_thread).start())
    btn_login.pack(ipadx=10, ipady=5)

    main_frame = ttk.Frame(root)
    
    header = ttk.Frame(main_frame, padding=10)
    header.pack(fill="x")
    ttk.Label(header, text="SKIM CV Parser", style="Title.TLabel").pack(side="left")
    h_right = ttk.Frame(header)
    h_right.pack(side="right")
    btn_schema = ttk.Button(h_right, text="Schema", command=open_schema_editor, state=tk.DISABLED)
    btn_schema.pack(side="left", padx=2)
    btn_config = ttk.Button(h_right, text="Cấu hình", command=open_settings, state=tk.DISABLED)
    btn_config.pack(side="left", padx=2)
    lbl_user = ttk.Label(h_right, text="...")
    lbl_user.pack(side="left", padx=10)
    
    ttk.Separator(main_frame).pack(fill="x")
    
    lbl_warning_bar = ttk.Label(main_frame, text="", foreground="red", anchor="center", font=("Segoe UI", 10, "bold"))
    
    action_frame = ttk.Labelframe(main_frame, text="Tác vụ", padding=10)
    action_frame.pack(fill="x", padx=10, pady=5)
    f_grid = ttk.Frame(action_frame)
    f_grid.pack(fill="x")
    f_grid.columnconfigure(0, weight=1); f_grid.columnconfigure(1, weight=1); f_grid.columnconfigure(2, weight=1)
    
    c1 = ttk.Frame(f_grid)
    c1.grid(row=0, column=0, sticky="ew", padx=5)
    btn_choose = ttk.Button(c1, text="1. Chọn File", command=choose_files)
    btn_choose.pack(fill="x")
    lbl_files = ttk.Label(c1, text="0 files")
    lbl_files.pack()
    
    c2 = ttk.Frame(f_grid)
    c2.grid(row=0, column=1, sticky="ew", padx=5)
    btn_process = ttk.Button(c2, text="2. Đọc CV (AI)", command=lambda: threading.Thread(target=process_files_thread).start(), state=tk.DISABLED)
    btn_process.pack(fill="x")
    
    c3 = ttk.Frame(f_grid)
    c3.grid(row=0, column=2, sticky="ew", padx=5)
    f_filter = ttk.Frame(c3)
    f_filter.pack(fill="x")
    selected_filter_var = tk.StringVar()
    filter_combobox = ttk.Combobox(f_filter, textvariable=selected_filter_var, state="readonly")
    filter_combobox.pack(side="left", fill="x", expand=True)
    btn_filter = ttk.Button(f_filter, text="⚙", width=3, command=open_filter_editor)
    btn_filter.pack(side="right")
    btn_convert = ttk.Button(c3, text="3. Lọc & Upload", command=lambda: threading.Thread(target=convert_and_upload_thread).start(), state=tk.DISABLED)
    btn_convert.pack(fill="x", pady=5)

    content = ttk.Panedwindow(main_frame, orient="horizontal")
    content.pack(fill="both", expand=True, padx=10, pady=5)
    preview_f = ttk.Labelframe(content, text="Kết quả")
    content.add(preview_f, weight=1)
    txt_preview = scrolledtext.ScrolledText(preview_f, height=15)
    txt_preview.pack(fill="both", expand=True)
    log_f = ttk.Labelframe(content, text="Log")
    content.add(log_f, weight=1)
    txt_log = scrolledtext.ScrolledText(log_f, height=15)
    txt_log.pack(fill="both", expand=True)
    txt_log.tag_config("error", foreground="red")
    txt_log.tag_config("success", foreground="green")

    return root

def start_app():
    global root
    root.withdraw()
    if not check_and_setup_if_needed(root):
        root.destroy(); return
    root.deiconify()
    if not settings_mgr.is_configured():
        login_frame.pack_forget()
        main_frame.pack(fill="both", expand=True)
        check_config_and_toggle_app()
    else:
        login_frame.pack(fill="both", expand=True)
        if os.path.exists("token.json"): threading.Thread(target=do_login_thread).start()

if __name__ == "__main__":
    root = create_main_window()
    root.after(100, start_app)
    root.mainloop()