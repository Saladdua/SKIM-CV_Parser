# ade_extractor.py
import json
import ssl
import requests
import os
import tempfile # [MỚI] Để tạo file tạm
from pypdf import PdfReader, PdfWriter # [MỚI] Để cắt PDF
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
from config import (
    get_landingai_api_key, 
    ADE_PARSE_ENDPOINT, 
    get_schema_definition,
    MAX_PAGES_TO_SCAN # [MỚI] Import biến giới hạn trang
)

# --- TLS adapter ---
class TLSAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        kwargs["ssl_context"] = ctx
        return super(TLSAdapter, self).init_poolmanager(*args, **kwargs)

_session = requests.Session()
_session.mount("https://", TLSAdapter())
# --- End TLS adapter ---

def build_fields_schema():
    """
    Xây dựng schema gửi cho API.
    SỬA LỖI: Cho phép nhận cả String, Number và Null để tránh lỗi Validation.
    """
    try:
        props = {}
        schema_definition = get_schema_definition() 
        
        for field in schema_definition:
            title_key = field.get("title")
            if title_key:
                props[title_key] = {
                    # Cho phép nhiều kiểu dữ liệu để tránh lỗi '0 is not string'
                    "type": ["string", "number", "integer", "null"], 
                    "description": field.get("description", "")
                }
        
        return {"type": "object", "properties": props}
        
    except Exception as e:
        print(f"Lỗi khi build_fields_schema: {e}")
        return {"type": "object", "properties": {}}

def _create_trimmed_pdf(original_path, max_pages):
    """
    [HÀM MỚI] Tạo một file PDF tạm thời chỉ chứa 'max_pages' trang đầu tiên.
    Trả về: (đường_dẫn_file_tạm, số_trang_cắt_được)
    """
    try:
        reader = PdfReader(original_path)
        total_pages = len(reader.pages)
        
        # Nếu số trang ít hơn hoặc bằng giới hạn, không cần cắt
        if total_pages <= max_pages:
            return None, total_pages

        writer = PdfWriter()
        # Chỉ lấy max_pages trang đầu
        for i in range(max_pages):
            writer.add_page(reader.pages[i])
            
        # Tạo file tạm
        fd, temp_path = tempfile.mkstemp(suffix="_trimmed.pdf")
        os.close(fd) # Đóng file descriptor
        
        with open(temp_path, "wb") as f:
            writer.write(f)
            
        return temp_path, max_pages
    except Exception as e:
        print(f"Cảnh báo: Không thể cắt PDF ({e}). Sẽ dùng file gốc.")
        return None, 0

def extract_schema_from_file(file_path: str, timeout: int = 180):
    """
    Gửi PDF/DOCX đến ADE. Tự động cắt ngắn file PDF nếu quá dài.
    """
    api_key = get_landingai_api_key()
    if not api_key:
        raise Exception("Chưa có API Key. Vui lòng vào Cấu hình.")

    headers = {"Authorization": f"Bearer {api_key}"}
    
    fields_schema = build_fields_schema()
    
    file_ext = os.path.splitext(file_path)[1].lower()
    files_key = "pdf" if file_ext == ".pdf" else "file"
    
    # === LOGIC TỐI ƯU CREDIT ===
    file_to_send = file_path
    is_temp_file = False
    
    if file_ext == ".pdf":
        trimmed_path, pages_count = _create_trimmed_pdf(file_path, MAX_PAGES_TO_SCAN)
        if trimmed_path:
            # In ra console để biết (hoặc có thể log ra UI nếu cần)
            print(f"--> Đã cắt file '{os.path.basename(file_path)}' xuống còn {pages_count} trang đầu để tiết kiệm credit.")
            file_to_send = trimmed_path
            is_temp_file = True
    # ===========================
    
    # Mở file an toàn
    file_handle = None
    try:
        file_handle = open(file_to_send, "rb")
        files = {files_key: file_handle}
        
        data = {
            "fields_schema": json.dumps(fields_schema, ensure_ascii=False),
        }

        # Gọi API
        resp = _session.post(ADE_PARSE_ENDPOINT, headers=headers, files=files, data=data, timeout=timeout)
    
    except Exception as e:
        raise Exception(f"Lỗi kết nối hoặc mở file: {e}")
    finally:
        if file_handle:
            file_handle.close()
        # Dọn dẹp file tạm nếu có
        if is_temp_file and os.path.exists(file_to_send):
            try:
                os.remove(file_to_send)
            except: pass

    # Xử lý lỗi HTTP
    if resp.status_code != 200:
        try:
            err_detail = resp.json()
            if "extraction_error" in err_detail:
                raise Exception(f"Lỗi Dữ liệu từ AI: {err_detail['extraction_error']}")
        except: pass
        raise Exception(f"ADE parse error {resp.status_code}: {resp.text}")

    try:
        rj = resp.json()
    except Exception as e:
        raise Exception(f"Invalid JSON from ADE: {e} ; raw: {resp.text[:1000]}")

    # --- Logic chuẩn hóa kết quả ---
    candidate = {}
    raw_extraction = None
    
    if isinstance(rj.get("data"), dict):
        raw_extraction = rj["data"].get("extracted_schema") or rj["data"].get("extraction")
    if raw_extraction is None:
        raw_extraction = rj.get("extraction")

    if isinstance(raw_extraction, str):
        try:
            candidate = json.loads(raw_extraction)
        except json.JSONDecodeError:
            candidate = {}
    elif isinstance(raw_extraction, dict):
        candidate = raw_extraction
    else:
        candidate = rj 

    # Map lại key
    schema_definition = get_schema_definition()
    title_to_key_map = {}
    all_keys = []
    for item in schema_definition:
        title_to_key_map[item['title']] = item['key'] 
        title_to_key_map[item['key']] = item['key']
        all_keys.append(item['key'])

    normalized = {key: "" for key in all_keys}
    
    if candidate:
        for api_key_from_response, api_value in candidate.items():
            norm_key = title_to_key_map.get(api_key_from_response) 
            if norm_key in normalized:
                normalized[norm_key] = _extract_value(api_value)
    
    return normalized

def _extract_value(v):
    """Chuyển mọi kiểu dữ liệu thành String."""
    if v is None: return ""
    if isinstance(v, str): return v.strip()
    if isinstance(v, (int, float)): return str(v)
    if isinstance(v, dict):
        if "value" in v: return str(v.get("value") or "").strip()
        if "text" in v: return str(v.get("text") or "").strip()
        return json.dumps(v, ensure_ascii=False)
    if isinstance(v, list):
        try:
            return " ; ".join([_extract_value(x) for x in v if _extract_value(x)])
        except Exception:
            return json.dumps(v, ensure_ascii=False)
    return str(v)