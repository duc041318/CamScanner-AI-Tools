"""
ROUTINE BUỔI SÁNG - Chạy lúc 07:00 mỗi ngày
Tự động gửi tin Zalo hàng loạt đến danh sách khách hàng.
"""

import os
import random
import sys
from datetime import datetime

# Import từ zalo-tool
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "zalo-tool"))

from config import CONTACTS_FILE, MAU_BAI_FILE, TEMPLATE_VARS_DEFAULT, DELAY_MIN_SANG, DELAY_MAX_SANG
from utils.file_reader import read_phone_list, apply_template
from utils.logger import Logger


def _doc_mau_bai(mau_bai_file):
    """Đọc tất cả các mẫu bài từ file, tách bởi dòng === BÀI."""
    if not os.path.exists(mau_bai_file):
        return []

    with open(mau_bai_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Tách các bài theo separator
    bai_list = []
    phan = content.split("=====================================================")
    for doan in phan:
        doan = doan.strip()
        # Chỉ lấy đoạn có nội dung thực (bắt đầu bằng "Chào" hoặc có emoji)
        if doan.startswith("Chào") or doan.startswith("🔥") or doan.startswith("🎉"):
            bai_list.append(doan.strip())

    return bai_list


def _chon_mau_bai_ngau_nhien(mau_bai_file):
    """Chọn ngẫu nhiên 1 mẫu bài từ file."""
    bai_list = _doc_mau_bai(mau_bai_file)
    if not bai_list:
        # Fallback nếu không đọc được file
        return (
            "Chào {ho_ten},\n\n"
            "Em đang có lô đất nền đẹp tại {du_an}.\n"
            "📐 Diện tích: {dien_tich}\n"
            "💰 Giá chỉ: {gia}\n"
            "✅ Sổ đỏ chính chủ - Pháp lý sạch\n\n"
            "Anh/chị quan tâm inbox em nhé!"
        )
    return random.choice(bai_list)


def chay(log_callback=None):
    """Chạy routine buổi sáng: gửi tin Zalo hàng loạt."""
    logger = Logger()
    thoi_gian = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _log(msg):
        print(f"[SANG {thoi_gian}] {msg}")
        if log_callback:
            log_callback(msg)

    _log("Bắt đầu Routine Buổi Sáng...")

    # 1. Kiểm tra file danh sách
    if not os.path.exists(CONTACTS_FILE):
        _log(f"KHÔNG TÌM THẤY file contacts: {CONTACTS_FILE}")
        return False

    # 2. Đọc danh sách khách
    try:
        contacts = read_phone_list(CONTACTS_FILE)
        _log(f"Đọc được {len(contacts)} khách hàng từ file.")
    except Exception as e:
        _log(f"Lỗi đọc danh sách: {e}")
        return False

    if not contacts:
        _log("Danh sách khách trống, bỏ qua.")
        return False

    # 3. Chọn mẫu bài ngẫu nhiên
    mau = _chon_mau_bai_ngau_nhien(MAU_BAI_FILE)
    _log(f"Đã chọn mẫu bài: {mau[:60]}...")

    # 4. Ghi thông tin chuẩn bị vào log (trước khi gửi)
    logger.log("routine_sang_chuan_bi", {
        "thoi_gian": thoi_gian,
        "so_khach": len(contacts),
        "mau_bai": mau[:80] + "...",
        "trang_thai": "Chuẩn bị gửi",
    })

    # 5. Gửi tin - dùng BulkMessageSender
    from features.bulk_message import BulkMessageSender

    sender = BulkMessageSender()

    ket_qua = {"thanh_cong": 0, "loi": 0}

    def _on_progress(current, total):
        pct = int(current / total * 100)
        _log(f"Tiến độ: {current}/{total} ({pct}%)")

    def _on_status(msg):
        _log(msg)
        if "Thành công" in msg:
            ket_qua["thanh_cong"] += 1
        elif "Lỗi" in msg or "lỗi" in msg:
            ket_qua["loi"] += 1

    # Tạo template với biến mặc định của dự án
    template_final = mau
    for key, val in TEMPLATE_VARS_DEFAULT.items():
        template_final = template_final.replace(f"{{{key}}}", val)

    thread = sender.start(
        file_path=CONTACTS_FILE,
        message_template=template_final,
        image_path=None,
        delay_min=DELAY_MIN_SANG,
        delay_max=DELAY_MAX_SANG,
        progress_callback=_on_progress,
        status_callback=_on_status,
    )

    # Chờ hoàn tất
    if thread:
        thread.join(timeout=3600)  # Tối đa 1 giờ

    # 6. Ghi kết quả
    logger.log("routine_sang_ket_qua", {
        "thoi_gian": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "so_khach": len(contacts),
        "thanh_cong": ket_qua["thanh_cong"],
        "loi": ket_qua["loi"],
        "trang_thai": "Hoàn tất",
    })

    _log(f"Hoàn tất! Thành công: {ket_qua['thanh_cong']}, Lỗi: {ket_qua['loi']}")
    return True


if __name__ == "__main__":
    chay()
