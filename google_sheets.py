# google_sheets.py
import os
import json 
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# SỬA LỖI: Chỉ import các hàm "get" và không import schema cũ
from config import (
    get_google_sheets_api_credentials, # Đây là hàm get_... duy nhất chúng ta cần
)
from settings_manager import SettingsManager

# SỬA LỖI CIRCULAR IMPORT:
# Xóa instance global, tạo instance bên trong hàm khi cần
# settings_mgr = SettingsManager() # <--- XÓA DÒNG NÀY

TOKEN_FILE = "token.json"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid",
]

def get_creds(interactive=True):
    """
    Xử lý xác thực Google (đã dọn dẹp).
    """
    creds = None
    
    # SỬA LỖI: Tạo instance SettingsManager bên trong hàm
    settings_mgr = SettingsManager()
    
    # Dùng settings_mgr để lấy credentials_file
    credentials_file = settings_mgr.get("credentials_file") 
    
    if not credentials_file or not os.path.exists(credentials_file):
        raise FileNotFoundError(
            f"Google OAuth credentials file not found: {credentials_file}\n"
            f"Please complete the setup wizard."
        )
    
    # ... (Phần còn lại của hàm giữ nguyên) ...
    try:
        with open(credentials_file, 'r') as f:
            if not f.read():
                raise ValueError(f"File credentials '{credentials_file}' bị rỗng.")
    except Exception as e:
         raise ValueError(f"Lỗi khi đọc '{credentials_file}': {e}")

    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except Exception as e:
            print(f"Lỗi đọc token.json (sẽ xóa và tạo lại): {e}")
            if os.path.exists(TOKEN_FILE): os.remove(TOKEN_FILE)
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Lỗi làm mới token (sẽ xóa và tạo lại): {e}")
                if os.path.exists(TOKEN_FILE):
                    os.remove(TOKEN_FILE)
                creds = None # Buộc đăng nhập lại
        
        if not creds:
            if interactive:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
                with open(TOKEN_FILE, "w") as token:
                    token.write(creds.to_json())
            else:
                raise Exception("Không có thông tin xác thực hợp lệ và không thể chạy chế độ tương tác.")
    
    return creds

def append_values_to_sheet(data_rows: list, creds, target_sheet_name: str):
    """
    Nối List[List] dữ liệu vào Sheet.
    """
    try:
        # SỬA LỖI: Tạo instance SettingsManager bên trong hàm
        settings_mgr = SettingsManager()
        spreadsheet_id = settings_mgr.get("spreadsheet_id")
        
        if not spreadsheet_id:
            raise Exception("Spreadsheet ID not configured. Please complete setup.")
        
        service = build("sheets", "v4", credentials=creds)
        values = data_rows
        body = {"values": values}
        
        res = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=f"'{target_sheet_name}'!A1",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body=body
        ).execute()
        return res
    except Exception as e:
        print(f"Lỗi khi gọi Google Sheets API: {e}")
        raise e