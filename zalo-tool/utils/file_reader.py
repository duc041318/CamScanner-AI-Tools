import csv
import os


def read_phone_list(file_path):
    """Đọc danh sách SĐT từ file .txt hoặc .csv.

    .txt: mỗi dòng là một SĐT
    .csv: cột đầu tiên có header 'sdt', các cột còn lại là biến thay thế

    Returns:
        list of dict, mỗi dict có key 'sdt' và các biến khác (nếu có)
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Không tìm thấy file: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()
    results = []

    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8-sig") as f:
            for line in f:
                phone = line.strip()
                if phone:
                    results.append({"sdt": phone})

    elif ext == ".csv":
        with open(file_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("sdt", "").strip():
                    cleaned = {k.strip(): v.strip() for k, v in row.items()}
                    results.append(cleaned)
    else:
        raise ValueError(f"Định dạng file không hỗ trợ: {ext}. Chỉ hỗ trợ .txt và .csv")

    return results


def apply_template(template, variables: dict):
    """Thay thế các biến {key} trong template bằng giá trị từ dict."""
    result = template
    for key, value in variables.items():
        result = result.replace(f"{{{key}}}", str(value))
    return result
