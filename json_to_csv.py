# json_to_csv.py
from datetime import datetime
# SỬA ĐỔI: Xóa import config cũ
# from config import ...
import csv # Dùng thư viện csv chuẩn của Python

# SỬA ĐỔI: Hàm này giờ đây nhận schema động
def build_data_for_sheet(extracted_list, user_email, schema_definition: list):
    """
    Chuyển list of dicts thành list of lists (CHỈ CÁC DÒNG DỮ LIỆU)
    và một list header riêng, dựa trên schema_definition động.
    
    returns (headers, data_rows)
    """
    data_rows = []
    
    # Xây dựng header và keys từ schema động
    headers = []
    field_keys_in_order = []
    for field in schema_definition:
        headers.append(field.get("title", ""))
        field_keys_in_order.append(field.get("key", ""))
        
    # Thêm các cột metadata
    headers.extend(["Người upload", "Thời gian upload"])
    
    for item in extracted_list:
        row_data = []
        # Map các keys động
        for key in field_keys_in_order:
            row_data.append(item.get(key, ""))
            
        # metadata
        row_data.append(user_email)
        row_data.append(datetime.now().strftime("%d/%m/%Y %H:%M")) # Hardcode format
        
        data_rows.append(row_data)
            
    return (headers, data_rows)

def save_data_to_csv(headers, data_rows, out_path):
    """Hàm lưu CSV, không cần pandas"""
    try:
        with open(out_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(data_rows)
        return out_path
    except Exception as e:
        print(f"Lỗi khi lưu CSV: {e}")
        return None