# settings_manager.py
import json
import os
import config 

SETTINGS_FILE = "app_settings.json"

class SettingsManager:
    """Manages persistent user settings and configuration."""
    
    DEFAULT_SETTINGS = {
        "credentials_file": "",
        "ade_api_key": "",
        "google_sheets_api_key": "",
        "spreadsheet_id": "",
        "sheet_name": "",
        "user_email": "",
        "schema_definition": config.DEFAULT_SCHEMA_DEFINITION,
        "custom_filters": {} # Nơi lưu các bộ lọc tùy chỉnh
    }
    
    def __init__(self, settings_file=SETTINGS_FILE):
        self.settings_file = settings_file
        self.settings = self.load_settings()
    
    def load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    defaults = self.DEFAULT_SETTINGS.copy()
                    defaults.update(loaded)
                    
                    # Validation cơ bản
                    if "schema_definition" not in defaults or not defaults["schema_definition"]:
                        defaults["schema_definition"] = config.DEFAULT_SCHEMA_DEFINITION
                        
                    return defaults
            except Exception as e:
                print(f"Error loading settings: {e}")
                return self.DEFAULT_SETTINGS.copy()
        return self.DEFAULT_SETTINGS.copy()
    
    def save_settings(self):
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def update(self, key, value):
        self.settings[key] = value
    
    def get(self, key, default=None):
        return self.settings.get(key, default)
    
    def is_configured(self):
        required = ["credentials_file", "ade_api_key", "spreadsheet_id", "sheet_name"]
        return all(self.settings.get(key) for key in required)

    # --- TÍNH NĂNG MỚI: IMPORT / EXPORT ---
    
    def export_shareable_config(self, file_path):
        """Chỉ xuất Schema và Bộ lọc (Không xuất API Key)."""
        data_to_export = {
            "schema_definition": self.settings.get("schema_definition", []),
            "custom_filters": self.settings.get("custom_filters", {})
        }
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data_to_export, f, indent=2, ensure_ascii=False)
            return True, "Xuất file thành công!"
        except Exception as e:
            return False, str(e)

    def import_shareable_config(self, file_path):
        """Nhập Schema và Bộ lọc từ file bên ngoài (Merge vào hiện tại)."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_data = json.load(f)
            
            # Kiểm tra hợp lệ
            if "custom_filters" not in imported_data and "schema_definition" not in imported_data:
                return False, "File không đúng định dạng cấu hình SKIM."

            # 1. Merge Filters (Gộp cái mới vào cái cũ, đè nếu trùng tên)
            current_filters = self.settings.get("custom_filters", {})
            new_filters = imported_data.get("custom_filters", {})
            if new_filters:
                current_filters.update(new_filters)
                self.settings["custom_filters"] = current_filters

            # 2. Update Schema (Lấy luôn schema mới)
            new_schema = imported_data.get("schema_definition")
            if new_schema:
                self.settings["schema_definition"] = new_schema
            
            self.save_settings()
            return True, f"Đã nhập thành công: {len(new_filters)} bộ lọc."
            
        except Exception as e:
            return False, str(e)