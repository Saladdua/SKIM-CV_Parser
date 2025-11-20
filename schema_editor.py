# schema_editor.py
import tkinter as tk
from tkinter import ttk, messagebox
import copy

class SchemaFieldDialog(tk.Toplevel):
    """Cửa sổ con để Thêm/Sửa một trường Schema."""
    def __init__(self, parent, mode="add", item_data=None):
        super().__init__(parent)
        self.title(f"{'Thêm' if mode == 'add' else 'Sửa'} Trường Schema")
        self.geometry("450x350")
        self.transient(parent)
        self.grab_set()
        
        self.result = None
        self.data = item_data or {"key": "", "title": "", "description": ""}
        
        # UI Layout
        main = ttk.Frame(self, padding=20)
        main.pack(fill="both", expand=True)
        
        # 1. Key
        ttk.Label(main, text="Key (Mã nội bộ - không dấu, không cách):").pack(anchor="w")
        self.key_var = tk.StringVar(value=self.data.get("key", ""))
        entry_key = ttk.Entry(main, textvariable=self.key_var)
        entry_key.pack(fill="x", pady=(0, 10))
        if mode == 'edit':
            entry_key.config(state='disabled') # Không cho sửa Key để tránh lỗi logic

        # 2. Title
        ttk.Label(main, text="Tên trường (Hiển thị):").pack(anchor="w")
        self.title_var = tk.StringVar(value=self.data.get("title", ""))
        ttk.Entry(main, textvariable=self.title_var).pack(fill="x", pady=(0, 10))

        # 3. Description
        ttk.Label(main, text="Mô tả (Hướng dẫn cho AI):").pack(anchor="w")
        self.txt_desc = tk.Text(main, height=5, width=40)
        self.txt_desc.pack(fill="both", expand=True, pady=(0, 10))
        self.txt_desc.insert("1.0", self.data.get("description", ""))

        # Buttons
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill="x")
        ttk.Button(btn_frame, text="Lưu", command=self.save).pack(side="right")
        ttk.Button(btn_frame, text="Hủy", command=self.destroy).pack(side="right", padx=5)

    def save(self):
        key = self.key_var.get().strip()
        title = self.title_var.get().strip()
        desc = self.txt_desc.get("1.0", "end").strip()

        if not key or not title:
            messagebox.showwarning("Thiếu thông tin", "Key và Tên trường là bắt buộc.", parent=self)
            return
        
        if " " in key:
             messagebox.showwarning("Sai định dạng", "Key không được chứa khoảng trắng.", parent=self)
             return

        self.result = {
            "key": key,
            "title": title,
            "description": desc
        }
        self.destroy()


class SchemaEditorWindow:
    """Cửa sổ Quản lý danh sách Schema."""
    def __init__(self, parent, settings_mgr):
        self.settings_mgr = settings_mgr
        self.window = tk.Toplevel(parent)
        self.window.title("Quản lý Schema (Các trường trích xuất)")
        self.window.geometry("800x500")
        self.window.transient(parent)
        self.window.grab_set()
        
        # Load bản sao dữ liệu để chỉnh sửa, không ảnh hưởng ngay đến setting gốc
        self.schema = copy.deepcopy(settings_mgr.get("schema_definition", []))
        
        self._build_ui()
        self._refresh_tree()

    def _build_ui(self):
        main = ttk.Frame(self.window, padding=10)
        main.pack(fill="both", expand=True)
        
        ttk.Label(main, text="Cấu hình các trường dữ liệu (Schema)", font=("Segoe UI", 14, "bold")).pack(pady=(0, 10))

        # Treeview
        cols = ("key", "title", "desc")
        self.tree = ttk.Treeview(main, columns=cols, show="headings", selectmode="extended") # selectmode='extended' cho phép chọn nhiều
        
        self.tree.heading("key", text="Key")
        self.tree.heading("title", text="Tên trường")
        self.tree.heading("desc", text="Mô tả")
        
        self.tree.column("key", width=120, stretch=False)
        self.tree.column("title", width=200, stretch=False)
        self.tree.column("desc", width=400, stretch=True)
        
        scrollbar = ttk.Scrollbar(main, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Toolbar Buttons
        btn_frame = ttk.Frame(self.window, padding=10)
        btn_frame.pack(fill="x", side="bottom")
        
        ttk.Button(btn_frame, text="+ Thêm", command=self.add).pack(side="left")
        ttk.Button(btn_frame, text="Sửa", command=self.edit).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="- Xóa (Chọn nhiều)", command=self.delete).pack(side="left")
        
        ttk.Button(btn_frame, text="Lưu & Đóng", command=self.save_and_close).pack(side="right")

    def _refresh_tree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for item in self.schema:
            self.tree.insert("", "end", values=(item.get("key"), item.get("title"), item.get("description")))

    def add(self):
        d = SchemaFieldDialog(self.window, mode="add")
        self.window.wait_window(d)
        if d.result:
            # Kiểm tra trùng key
            for item in self.schema:
                if item['key'] == d.result['key']:
                    messagebox.showerror("Lỗi", f"Key '{d.result['key']}' đã tồn tại!")
                    return
            self.schema.append(d.result)
            self._refresh_tree()

    def edit(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showinfo("Thông báo", "Vui lòng chọn một dòng để sửa.")
            return
        
        if len(selected_items) > 1:
            messagebox.showwarning("Cảnh báo", "Chỉ được chọn 1 dòng để sửa.")
            return
            
        # Lấy data hiện tại
        item_values = self.tree.item(selected_items[0], "values")
        key_to_edit = item_values[0]
        
        # Tìm object trong list schema
        current_data = next((item for item in self.schema if item["key"] == key_to_edit), None)
        
        d = SchemaFieldDialog(self.window, mode="edit", item_data=current_data)
        self.window.wait_window(d)
        
        if d.result:
            # Cập nhật lại list
            for i, item in enumerate(self.schema):
                if item['key'] == key_to_edit:
                    self.schema[i] = d.result
                    break
            self._refresh_tree()

    def delete(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showinfo("Thông báo", "Vui lòng chọn ít nhất một dòng để xóa.")
            return
        
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa {len(selected_items)} trường đã chọn?"):
            # Lấy danh sách Key cần xóa
            keys_to_delete = []
            for item_id in selected_items:
                val = self.tree.item(item_id, "values")
                keys_to_delete.append(val[0]) # val[0] là key
            
            # Lọc lại list, giữ lại những cái KHÔNG nằm trong danh sách xóa
            self.schema = [item for item in self.schema if item['key'] not in keys_to_delete]
            self._refresh_tree()

    def save_and_close(self):
        # Lưu vào file settings
        self.settings_mgr.update("schema_definition", self.schema)
        if self.settings_mgr.save_settings():
            messagebox.showinfo("Thành công", "Đã cập nhật Schema.")
            self.window.destroy()
        else:
            messagebox.showerror("Lỗi", "Không thể lưu file cài đặt.")