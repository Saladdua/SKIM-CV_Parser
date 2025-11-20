# filter_editor.py
import tkinter as tk
from tkinter import ttk, messagebox

class FilterEditDialog(tk.Toplevel):
    """Cửa sổ con để Thêm hoặc Sửa một bộ lọc cụ thể."""
    def __init__(self, parent, mode="add", item_name="", item_data=None):
        super().__init__(parent)
        self.title(f"{'Thêm' if mode == 'add' else 'Sửa'} Bộ lọc")
        self.geometry("500x600")
        self.transient(parent)
        self.grab_set()
        
        self.result = None
        self.data = item_data or {}
        
        main = ttk.Frame(self, padding=20)
        main.pack(fill="both", expand=True)
        
        # 1. Tên vị trí
        ttk.Label(main, text="Tên vị trí (VD: Kỹ sư MEP):", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.name = tk.StringVar(value=item_name)
        ttk.Entry(main, textvariable=self.name).pack(fill="x", pady=(5, 15))
        
        # 2. Kinh nghiệm
        lf_exp = ttk.LabelFrame(main, text="Kinh nghiệm (Năm)", padding=10)
        lf_exp.pack(fill="x", pady=5)
        
        f_e = ttk.Frame(lf_exp)
        f_e.pack(fill="x")
        
        ttk.Label(f_e, text="Tối thiểu:").pack(side="left")
        self.min_e = tk.DoubleVar(value=self.data.get("min_exp", 0))
        ttk.Entry(f_e, textvariable=self.min_e, width=10).pack(side="left", padx=5)
        
        ttk.Label(f_e, text="Tối đa:").pack(side="left", padx=(20, 0))
        self.max_e = tk.DoubleVar(value=self.data.get("max_exp", 100))
        ttk.Entry(f_e, textvariable=self.max_e, width=10).pack(side="left", padx=5)
        
        # 3. Trường Ưu tiên
        ttk.Label(main, text="Trường Ưu tiên (cách nhau dấu phẩy):", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(15, 5))
        ttk.Label(main, text="VD: bach khoa, xay dung", font=("Segoe UI", 8, "italic")).pack(anchor="w")
        self.txt_pref = tk.Text(main, height=4, width=50)
        self.txt_pref.pack(fill="x")
        # Load dữ liệu cũ
        self.txt_pref.insert("1.0", ", ".join(self.data.get("preferred_schools", [])))
        
        # 4. Trường Loại trừ
        ttk.Label(main, text="Trường Loại trừ (cách nhau dấu phẩy):", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(15, 5))
        self.txt_excl = tk.Text(main, height=3, width=50)
        self.txt_excl.pack(fill="x")
        # Load dữ liệu cũ
        self.txt_excl.insert("1.0", ", ".join(self.data.get("excluded_schools", [])))
        
        # Nút Lưu
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill="x", side="bottom", pady=20)
        ttk.Button(btn_frame, text="Lưu", command=self.save).pack(side="right")
        ttk.Button(btn_frame, text="Hủy", command=self.destroy).pack(side="right", padx=10)

    def save(self):
        if not self.name.get().strip():
            messagebox.showwarning("Lỗi", "Tên vị trí không được để trống")
            return
        
        def parse(t): 
            raw = t.get("1.0", "end").strip()
            if not raw: return []
            return [x.strip().lower() for x in raw.split(',') if x.strip()]
        
        self.result = {
            "name": self.name.get().strip(),
            "data": {
                "min_exp": self.min_e.get(),
                "max_exp": self.max_e.get(),
                "preferred_schools": parse(self.txt_pref),
                "excluded_schools": parse(self.txt_excl)
            }
        }
        self.destroy()

class FilterEditorWindow:
    """Cửa sổ chính Quản lý danh sách bộ lọc."""
    def __init__(self, parent, settings_mgr):
        self.settings_mgr = settings_mgr
        self.window = tk.Toplevel(parent)
        self.window.title("Quản lý Bộ lọc")
        self.window.geometry("900x500") # Tăng chiều rộng để hiển thị đủ cột
        self.window.transient(parent)
        self.window.grab_set()
        
        # Load dữ liệu
        self.filters = self.settings_mgr.get("custom_filters", {})
        # Nếu rỗng thì tạo mẫu (để test)
        if not self.filters:
             self.filters = {
                "Kỹ sư Kết cấu": {"min_exp": 2.0, "max_exp": 5.0, "preferred_schools": ["xay dung", "kien truc"], "excluded_schools": ["dai nam"]},
                "Kỹ sư MEP": {"min_exp": 0.0, "max_exp": 100.0, "preferred_schools": ["bach khoa", "cong nghiep"], "excluded_schools": []}
            }
        
        self._build_ui()
        
    def _build_ui(self):
        main = ttk.Frame(self.window, padding=10)
        main.pack(fill="both", expand=True)
        
        ttk.Label(main, text="Danh sách vị trí tuyển dụng (JD)", font=("Segoe UI", 14, "bold")).pack(pady=(0, 10))
        
        # --- CẤU HÌNH BẢNG HIỂN THỊ (Treeview) ---
        cols = ("name", "exp", "pref", "excl")
        self.tree = ttk.Treeview(main, columns=cols, show="headings")
        
        # Định nghĩa tiêu đề cột
        self.tree.heading("name", text="Tên Vị trí")
        self.tree.heading("exp", text="Kinh nghiệm (Năm)")
        self.tree.heading("pref", text="Ưu tiên (Trường)")
        self.tree.heading("excl", text="Loại trừ (Trường)")
        
        # Định nghĩa độ rộng cột
        self.tree.column("name", width=200)
        self.tree.column("exp", width=120, anchor="center")
        self.tree.column("pref", width=300)
        self.tree.column("excl", width=200)
        
        # Thêm thanh cuộn
        scrollbar = ttk.Scrollbar(main, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # --- THANH CÔNG CỤ ---
        btn_frame = ttk.Frame(self.window, padding=10)
        btn_frame.pack(fill="x", side="bottom")
        
        ttk.Button(btn_frame, text="+ Thêm Mới", command=self.add).pack(side="left")
        ttk.Button(btn_frame, text="Sửa", command=self.edit).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Xóa", command=self.delete).pack(side="left", padx=5)
        
        ttk.Button(btn_frame, text="Lưu & Đóng", command=self.save).pack(side="right")
        
        self.refresh()

    def refresh(self):
        """Tải lại dữ liệu vào bảng."""
        # Xóa hết dữ liệu cũ trên bảng
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        # Duyệt qua danh sách filters và thêm vào bảng
        for name, data in self.filters.items():
            # Format lại dữ liệu để hiển thị đẹp hơn
            exp_str = f"{data.get('min_exp', 0)} - {data.get('max_exp', 'Max')}"
            pref_str = ", ".join(data.get('preferred_schools', []))
            excl_str = ", ".join(data.get('excluded_schools', []))
            
            self.tree.insert("", "end", values=(name, exp_str, pref_str, excl_str))

    def add(self):
        d = FilterEditDialog(self.window, mode="add")
        self.window.wait_window(d)
        if d.result:
            name = d.result['name']
            if name in self.filters:
                messagebox.showerror("Lỗi", "Tên vị trí này đã tồn tại!")
                return
            self.filters[name] = d.result['data']
            self.refresh()

    def edit(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Thông báo", "Vui lòng chọn một dòng để sửa.")
            return
            
        # Lấy tên vị trí từ dòng được chọn
        item = self.tree.item(sel[0])
        old_name = item['values'][0]
        old_data = self.filters.get(old_name)
        
        d = FilterEditDialog(self.window, mode="edit", item_name=old_name, item_data=old_data)
        self.window.wait_window(d)
        
        if d.result:
            new_name = d.result['name']
            new_data = d.result['data']
            
            # Nếu đổi tên thì xóa cái cũ đi
            if new_name != old_name:
                del self.filters[old_name]
            
            self.filters[new_name] = new_data
            self.refresh()

    def delete(self):
        sel = self.tree.selection()
        if sel:
            name = self.tree.item(sel[0], 'values')[0]
            if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa '{name}'?"):
                del self.filters[name]
                self.refresh()

    def save(self):
        self.settings_mgr.update("custom_filters", self.filters)
        self.settings_mgr.save_settings()
        messagebox.showinfo("Thành công", "Đã lưu danh sách bộ lọc.")
        self.window.destroy()