"""
ROUTINE BUỔI TỐI - Chạy lúc 19:30 mỗi ngày
Follow-up khách đã được nhắn sáng nhưng chưa phản hồi.
"""

import csv
import os
import sys
from datetime import datetime, date

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "zalo-tool"))

from config import CONTACTS_FILE, DELAY_MIN_TOI, DELAY_MAX_TOI
from utils.logger import Logger


TIN_FOLLOW_UP = [
    (
        "Chào {ho_ten} 👋\n\n"
        "Sáng nay em có nhắn thông tin về đất nền Sóc Sơn.\n"
        "Không biết anh/chị đã xem chưa ạ?\n\n"
        "Hiện còn 2 lô đẹp:\n"
        "📍 Lô 1: 83m2, giá 1.66 tỷ - Sổ đỏ chính chủ\n"
        "📍 Lô 2: 88.5m2 (LÔ GÓC), giá 2.21 tỷ - 2 mặt thoáng\n\n"
        "Anh/chị quan tâm lô nào em tư vấn thêm ạ? 🙏"
    ),
    (
        "Dạ anh/chị {ho_ten} ơi!\n\n"
        "Em gửi lại thông tin lô đất Phú Tằng - Sóc Sơn:\n"
        "✅ Pháp lý: Sổ đỏ, sang tên ngay\n"
        "✅ Vị trí: Đường bê tông 4-5m, khu dân cư đông đúc\n"
        "✅ Tiềm năng: Sóc Sơn sắp lên quận, hạ tầng đang bứt phá\n\n"
        "Giá còn rất tốt so với thị trường hiện tại.\n"
        "Anh/chị muốn em đặt lịch xem đất không ạ? 🚗"
    ),
    (
        "Chào {ho_ten}!\n\n"
        "💡 Tip đầu tư: Đất Sóc Sơn hiện đang thấp hơn Đông Anh 40-50%.\n"
        "Khi hạ tầng hoàn thiện (cao tốc, mở rộng Nội Bài), giá sẽ nhảy vọt!\n\n"
        "Em đang giữ 2 lô đẹp cuối cùng tại Phú Tằng.\n"
        "👉 Inbox em để nhận bảng giá + hình ảnh thực tế nhé!"
    ),
]


def _doc_log_hom_nay():
    """Đọc log gửi tin buổi sáng hôm nay, trả về list SĐT đã gửi thành công."""
    log_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "zalo-tool", "logs"
    )
    if not os.path.exists(log_dir):
        return []

    hom_nay = date.today().strftime("%Y-%m-%d")
    sdt_da_gui = []

    for fname in os.listdir(log_dir):
        if hom_nay in fname and "bulk_message" in fname:
            fpath = os.path.join(log_dir, fname)
            try:
                with open(fpath, "r", encoding="utf-8-sig") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row.get("trang_thai", "") == "Thành công":
                            sdt_da_gui.append(row.get("sdt", "").strip())
            except Exception:
                continue

    return sdt_da_gui


def _doc_khach_follow_up(sdt_da_gui):
    """Lọc danh sách khách đã nhận tin sáng để follow-up tối."""
    import csv as _csv
    if not os.path.exists(CONTACTS_FILE):
        return []

    khach = []
    with open(CONTACTS_FILE, "r", encoding="utf-8-sig") as f:
        reader = _csv.DictReader(f)
        for row in reader:
            sdt = row.get("sdt", "").strip()
            if sdt in sdt_da_gui:
                khach.append(row)

    return khach


def chay(log_callback=None):
    """Chạy routine buổi tối: follow-up khách đã nhận tin sáng."""
    import random

    logger = Logger()
    thoi_gian = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _log(msg):
        print(f"[TOI {thoi_gian}] {msg}")
        if log_callback:
            log_callback(msg)

    _log("Bắt đầu Routine Buổi Tối (Follow-up)...")

    # 1. Lấy danh sách SĐT đã gửi sáng
    sdt_da_gui = _doc_log_hom_nay()
    _log(f"Tìm thấy {len(sdt_da_gui)} SĐT đã gửi sáng nay.")

    if not sdt_da_gui:
        _log("Không có dữ liệu log buổi sáng, gửi follow-up cho toàn bộ danh sách.")
        # Nếu không có log sáng, đọc toàn bộ contacts
        from utils.file_reader import read_phone_list
        try:
            contacts = read_phone_list(CONTACTS_FILE)
        except Exception as e:
            _log(f"Lỗi đọc danh sách: {e}")
            return False
    else:
        contacts = _doc_khach_follow_up(sdt_da_gui)

    if not contacts:
        _log("Không có khách để follow-up tối nay.")
        return True

    _log(f"Sẽ follow-up {len(contacts)} khách...")

    # 2. Gửi follow-up
    from features.bulk_message import BulkMessageSender

    sender = BulkMessageSender()
    tin_hom_nay = random.choice(TIN_FOLLOW_UP)

    ket_qua = {"thanh_cong": 0, "loi": 0}

    def _on_status(msg):
        _log(msg)

    thread = sender.start(
        file_path=CONTACTS_FILE,
        message_template=tin_hom_nay,
        image_path=None,
        delay_min=DELAY_MIN_TOI,
        delay_max=DELAY_MAX_TOI,
        progress_callback=None,
        status_callback=_on_status,
    )

    if thread:
        thread.join(timeout=7200)

    logger.log("routine_toi_ket_qua", {
        "thoi_gian": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "so_follow_up": len(contacts),
        "trang_thai": "Hoàn tất",
    })

    _log("Hoàn tất follow-up buổi tối!")
    return True


if __name__ == "__main__":
    chay()
