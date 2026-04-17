"""
Cấu hình chung cho tất cả Routines BĐS Sóc Sơn.
Chỉnh sửa file này khi cần cập nhật thông tin dự án hoặc lịch.
"""

import os

# ── Đường dẫn gốc ─────────────────────────────────────────────────────────────
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZALO_TOOL_DIR = os.path.join(ROOT_DIR, "zalo-tool")
ROUTINES_DIR = os.path.join(ROOT_DIR, "routines")

# File dữ liệu
CONTACTS_FILE = os.path.join(ZALO_TOOL_DIR, "data", "contacts.csv")
MAU_BAI_FILE = os.path.join(ROOT_DIR, "mau-bai-dang-zalo.txt")
BAO_CAO_DIR = os.path.join(ROUTINES_DIR, "bao-cao")

# ── Thông tin dự án ────────────────────────────────────────────────────────────
DU_AN = "Phú Tằng - Đa Phúc - Sóc Sơn"

LO_DAT = {
    "lo1": {
        "ten": "Lô 1 - 83m2",
        "dien_tich": "83m2 (8.12x10.41m - gần vuông)",
        "gia": "1.66 tỷ (20 triệu/m2)",
        "vi_tri": "Thôn Yên Tằng, Đa Phúc, Sóc Sơn",
        "so_do": "AA 01730140",
        "diem_manh": "Sổ đỏ chính chủ, đường bê tông 4-5m",
    },
    "lo2": {
        "ten": "Lô 2 - 88.5m2 (LÔ GÓC)",
        "dien_tich": "88.5m2 (15.93x5.56m - LÔ GÓC 2 mặt thoáng)",
        "gia": "2.21 tỷ (25 triệu/m2)",
        "vi_tri": "Thôn Yên Tằng, Đa Phúc, Sóc Sơn",
        "so_do": "AA 02367049",
        "diem_manh": "Lô góc 2 mặt thoáng, thông gió, dễ xây nhà",
    },
}

# Biến mẫu mặc định cho template
TEMPLATE_VARS_DEFAULT = {
    "du_an": DU_AN,
    "gia": "từ 1.66 tỷ",
    "dien_tich": "83-88.5m2",
}

# ── Cài đặt gửi tin ────────────────────────────────────────────────────────────
DELAY_MIN_SANG = 10   # giây, buổi sáng gửi nhanh hơn
DELAY_MAX_SANG = 25
DELAY_MIN_TOI = 15    # buổi tối chậm hơn để tránh spam
DELAY_MAX_TOI = 40

# ── Lịch chạy (giờ:phút) ──────────────────────────────────────────────────────
LICH_SANG = "07:00"
LICH_TOI = "19:30"
LICH_BAO_CAO = "21:00"
LICH_DANG_BAI = "12:00"   # Đăng bài Feed Zalo
LICH_NOI_DUNG = "08:00"   # Thứ Hai
