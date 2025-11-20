# config.py
import sys
import os

# --- PYINSTALLER CODE ---
def resource_path(relative_path):
    """
    Get absolute path to resource, works both in dev and when frozen by PyInstaller.
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
# --- END PYINSTALLER CODE ---


# --- CONSTANTS ---
ADE_PARSE_ENDPOINT = "https://api.va.landing.ai/v1/tools/agentic-document-analysis"
DEFAULT_ADE_PARSE_ENDPOINT = ADE_PARSE_ENDPOINT
DATETIME_FORMAT = "%d/%m/%Y %H:%M"

# === CẤU HÌNH TỐI ƯU CREDIT ===
MAX_PAGES_TO_SCAN = 3  # Chỉ quét tối đa 3 trang đầu của PDF.

# === CẤU TRÚC SCHEMA MỚI CHO CV PARSER ===
DEFAULT_SCHEMA_DEFINITION = [
    {
        "key": "ho_ten",
        "title": "Họ và tên",
        "description": "Họ và tên đầy đủ của ứng viên."
    },
    {
        "key": "email",
        "title": "Email",
        "description": "Địa chỉ email liên hệ."
    },
    {
        "key": "so_dien_thoai",
        "title": "Số điện thoại",
        "description": "Số điện thoại liên hệ."
    },
    {
        "key": "hoc_van_truong_hoc",
        "title": "Trường Đại học",
        "description": "Tên trường đại học/cao đẳng cao nhất. Ví dụ: 'Đại học Bách Khoa', 'Đại học Xây Dựng'."
    },
    {
        "key": "hoc_van_chuyen_nganh",
        "title": "Chuyên ngành",
        "description": "Chuyên ngành đào tạo. Ví dụ: 'Kỹ thuật Xây dựng', 'Kiến trúc'."
    },
    {
        "key": "so_nam_kn",
        "title": "Số năm kinh nghiệm",
        "description": "Tổng số năm kinh nghiệm làm việc. Hãy ước lượng thành MỘT CON SỐ cụ thể. Nếu là sinh viên mới ra trường hoặc dưới 1 năm, trả về 0. Nếu 2-3 năm, trả về 2.5."
    },
    {
        "key": "ky_nang_mem",
        "title": "Kỹ năng/Phần mềm",
        "description": "Các phần mềm thành thạo (Revit, CAD, Etabs...) và kỹ năng (Tiếng Anh, Làm việc nhóm...)."
    },
    {
        "key": "cong_ty_gan_nhat",
        "title": "Công ty gần nhất",
        "description": "Tên công ty gần đây nhất ứng viên làm việc."
    },
    {
        "key": "vi_tri_gan_nhat",
        "title": "Vị trí gần nhất",
        "description": "Chức danh công việc gần đây nhất."
    }
]

# === CÁC HÀM GET ĐỘNG ===

def get_credentials_file():
    return resource_path("credentials.json")

def get_landingai_api_key():
    from settings_manager import SettingsManager
    settings_mgr = SettingsManager()
    return settings_mgr.get("ade_api_key", "")

def get_spreadsheet_id():
    from settings_manager import SettingsManager
    settings_mgr = SettingsManager()
    return settings_mgr.get("spreadsheet_id", "")

def get_sheet_name():
    from settings_manager import SettingsManager
    settings_mgr = SettingsManager()
    return settings_mgr.get("sheet_name", "")

def get_google_sheets_api_credentials():
    from settings_manager import SettingsManager
    settings_mgr = SettingsManager()
    return settings_mgr.get("google_sheets_api_key", get_credentials_file())

# --- CÁC HÀM SCHEMA ---
def get_schema_definition():
    from settings_manager import SettingsManager
    settings_mgr = SettingsManager()
    return settings_mgr.get("schema_definition", DEFAULT_SCHEMA_DEFINITION)

def get_schema_keys():
    schema = get_schema_definition()
    return [item.get("key") for item in schema]

def get_schema_titles():
    schema = get_schema_definition()
    return [item.get("title") for item in schema]

def get_schema_headers():
    return get_schema_titles()