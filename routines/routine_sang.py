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
from features.analytics import TemplateAnalytics


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


_FALLBACK_MAU = (
    "Chào {ho_ten},\n\n"
    "Em đang có lô đất nền đẹp tại {du_an}.\n"
    "📐 Diện tích: {dien_tich}\n"
    "💰 Giá chỉ: {gia}\n"
    "✅ Sổ đỏ chính chủ - Pháp lý sạch\n\n"
    "Anh/chị quan tâm inbox em nhé!"
)


def _chon_mau_co_trong_so(mau_bai_file):
    """Chọn mẫu bài theo trọng số hiệu quả lịch sử (fallback về random nếu chưa có data)."""
    bai_list = _doc_mau_bai(mau_bai_file)
    if not bai_list:
        return _FALLBACK_MAU, "fallback"
    template, mid = TemplateAnalytics().chon_mau_co_trong_so(bai_list)
    return template, mid


def _loc_contacts(contacts):
    """
    Lọc danh sách theo trạng thái:
    - Bỏ qua: khong_quan_tam, da_coc (không cần liên hệ nữa)
    - Ưu tiên đầu: quan_tam, co_phan_hoi (khách nóng)
    - Còn lại: moi, da_gui (chưa/đã liên hệ)
    """
    bo_qua = {"khong_quan_tam", "da_coc", "xem_dat"}
    uu_tien = []
    binh_thuong = []

    for c in contacts:
        ts = c.get("trang_thai", "moi").strip()
        if ts in bo_qua:
            continue
        if ts in ("quan_tam", "co_phan_hoi"):
            uu_tien.append(c)
        else:
            binh_thuong.append(c)

    return uu_tien + binh_thuong


def _cap_nhat_ngay_lien_he(contacts_gui):
    """Cập nhật ngày_lien_he_cuoi cho các số vừa gửi."""
    import csv as _csv
    hom_nay = datetime.now().strftime("%Y-%m-%d")
    sdt_da_gui = {c["sdt"] for c in contacts_gui}

    if not os.path.exists(CONTACTS_FILE):
        return

    all_rows = []
    with open(CONTACTS_FILE, "r", encoding="utf-8-sig") as f:
        reader = _csv.DictReader(f)
        headers = reader.fieldnames
        all_rows = list(reader)

    for row in all_rows:
        if row["sdt"] in sdt_da_gui:
            row["ngay_lien_he_cuoi"] = hom_nay
            if row.get("trang_thai") == "moi":
                row["trang_thai"] = "da_gui"

    with open(CONTACTS_FILE, "w", encoding="utf-8", newline="") as f:
        writer = _csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(all_rows)


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

    # 2. Đọc và lọc danh sách khách
    try:
        tat_ca = read_phone_list(CONTACTS_FILE)
        _log(f"Tổng danh sách: {len(tat_ca)} khách.")
    except Exception as e:
        _log(f"Lỗi đọc danh sách: {e}")
        return False

    contacts = _loc_contacts(tat_ca)
    bo_qua = len(tat_ca) - len(contacts)
    _log(f"Sẽ gửi: {len(contacts)} khách (bỏ qua {bo_qua} đã cọc/không quan tâm).")

    if not contacts:
        _log("Không còn khách để gửi.")
        return False

    # Phân loại để log rõ hơn
    n_hot = sum(1 for c in contacts if c.get("trang_thai") in ("quan_tam", "co_phan_hoi"))
    if n_hot:
        _log(f"  → Trong đó {n_hot} khách NÓNG (quan_tam/co_phan_hoi) được gửi trước.")

    # 3. Chọn mẫu bài theo trọng số hiệu quả
    mau, mid = _chon_mau_co_trong_so(MAU_BAI_FILE)
    _log(f"Đã chọn mẫu bài (ID:{mid}): {mau[:60]}...")

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

    # 6. Cập nhật ngày liên hệ cuối trong contacts.csv
    _cap_nhat_ngay_lien_he(contacts)

    # 7. Ghi log mẫu bài đã dùng (để phân tích hiệu quả)
    sdt_da_gui = [c["sdt"] for c in contacts]
    TemplateAnalytics().ghi_log_gui(mau, sdt_da_gui)
    _log(f"Đã ghi log mẫu bài {mid} cho {len(sdt_da_gui)} SĐT.")

    # 8. Ghi kết quả
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
