"""
ROUTINE ĐĂNG BÀI ZALO FEED - Chạy lúc 12:00 trưa mỗi ngày
Đăng bài lên Nhật ký Zalo để tăng tiếp cận organic.
Nội dung ngắn gọn, có CTA rõ ràng, phù hợp Feed (khác với tin nhắn DM).
"""

import os
import sys
from datetime import datetime, date

# Import từ zalo-tool
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "zalo-tool"))

from utils.logger import Logger

# ── Mẫu bài FEED (5 mẫu, xoay vòng theo ngày trong tuần) ─────────────────────
# Khác với mẫu DM: ngắn hơn, không có {ho_ten}, có hashtag, tone công khai

MAU_FEED = [
    # Thứ 2 - Hạ tầng Sóc Sơn
    """🛣️ SÓC SƠN - VÙNG ĐẤT SẮP CHUYỂN MÌNH!

Sân bay Nội Bài chỉ cách 15 phút lái xe.
Cao tốc Hà Nội - Thái Nguyên kết nối thẳng.
Quy hoạch đô thị sân bay đang được đẩy nhanh.

📌 Phú Tằng - Đa Phúc: Vị trí đắc địa trong vùng lõi phát triển.
💰 Giá hiện tại: Từ 1.66 tỷ/lô - Sổ đỏ chính chủ.

👉 Còn 2 lô duy nhất. Inbox ngay trước khi hết!

#SocSon #DatNen #DauTuBatDongSan #NoiBai""",

    # Thứ 3 - Tiềm năng đầu tư
    """💹 TẠI SAO NHÀ ĐẦU TƯ CHỌN ĐẤT SÓC SƠN 2026?

✅ Giá còn thấp hơn Đông Anh, Gia Lâm 35-40%
✅ Hạ tầng đang được rót hàng nghìn tỷ đồng
✅ Sân bay Nội Bài T3 đang xây dựng → dân số tăng nhanh
✅ Thanh khoản tốt do quỹ đất khan hiếm

📍 Thôn Yên Tằng, Đa Phúc, Sóc Sơn
📐 Diện tích: 83m² và 88.5m² (lô góc)
📄 Pháp lý: Sổ đỏ - Đất thổ cư

💬 DM để nhận bảng giá chi tiết và sơ đồ lô đất!

#DauTu #DatNenSocSon #BatDongSan2026""",

    # Thứ 4 - So sánh giá
    """📊 SO SÁNH GIÁ ĐẤT GẦN SÂN BAY NỘI BÀI:

🔴 Đông Anh: 45-60 triệu/m²
🔴 Gia Lâm: 40-55 triệu/m²
🟡 Mê Linh: 28-35 triệu/m²
🟢 Sóc Sơn (Đa Phúc): 20-25 triệu/m² ← ĐANG Ở ĐÂY

Cùng khoảng cách đến trung tâm, cùng tiệm cận sân bay...
Chênh lệch giá lên đến 200-300%!

🏡 Lô 1 - 83m²: 1.66 tỷ (20tr/m²) | Sổ đỏ AA 01730140
🏡 Lô 2 - 88.5m² GÓC: 2.21 tỷ (25tr/m²) | Sổ đỏ AA 02367049

Cơ hội mua thấp, bán cao còn đang mở.
Inbox em để xem thực tế bất kỳ lúc nào! 🤝

#SoSanhGia #DatNen #SocSon #DauTuThongMinh""",

    # Thứ 5 - Pháp lý
    """📄 PHÁP LÝ MINH BẠCH - AN TÂM ĐẦU TƯ

Nhiều người ngại mua đất Sóc Sơn vì lo pháp lý...
Nhưng 2 lô đất này KHÁC BIỆT hoàn toàn:

✅ Sổ đỏ chính chủ - KHÔNG TRANH CHẤP
✅ Đất thổ cư 100% - Xây nhà KHÔNG cần chuyển đổi
✅ Đường bê tông 4-5m trước lô - Xe ô tô vào tận nơi
✅ Hạ tầng điện nước đầy đủ
✅ Giao dịch công chứng chuẩn pháp lý

📍 Thôn Yên Tằng, Đa Phúc, Sóc Sơn, Hà Nội

Xem sổ tận tay, thực địa bất kỳ ngày nào.
Nhắn tin đặt lịch nhé! ☎️

#PhapLy #SoDo #DatNenSocSon #AnTam""",

    # Thứ 6 - Lô góc
    """⭐ LÔ GÓC 2 MẶT THOÁNG - CƠ HỘI HIẾM CÓ!

Tại sao lô góc lại đặc biệt?
🔹 2 mặt tiền → Giá trị cao hơn 15-20% so với lô trong
🔹 Thông gió tự nhiên → Nhà mát mẻ, sáng sủa
🔹 Dễ thiết kế → Nhiều phương án kiến trúc
🔹 Thanh khoản tốt hơn khi bán lại

📌 LÔ 2 - Phú Tằng, Đa Phúc, Sóc Sơn:
  • Diện tích: 88.5m² (15.93 x 5.56m)
  • Góc 2 mặt đường - Thoáng 2 hướng
  • Giá: 2.21 tỷ (25 triệu/m²)
  • Sổ đỏ: AA 02367049

Lô góc đẹp, giá hợp lý như này cực hiếm!
Inbox ngay để đặt cọc giữ chỗ trước khi người khác lấy mất 🏃

#LoGoc #DatNen #SocSon #BatDongSan""",
]


def _chon_mau_theo_ngay() -> str:
    """Chọn mẫu feed xoay vòng theo ngày trong tuần (0=Thứ 2, 6=CN)."""
    thu = date.today().weekday()  # 0=Thứ 2 ... 6=CN
    # 5 mẫu xoay vòng, T7 và CN lặp lại mẫu Thứ 5 & Thứ 6
    idx = thu % len(MAU_FEED)
    return MAU_FEED[idx]


def chay(log_callback=None) -> bool:
    """Chạy routine đăng bài Feed Zalo lúc 12:00 trưa."""
    logger = Logger(log_dir=os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "zalo-tool", "logs"
    ))
    thoi_gian = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _log(msg):
        print(f"[DANG_BAI {thoi_gian}] {msg}")
        if log_callback:
            log_callback(msg)

    _log("Bắt đầu Routine Đăng Bài Feed Zalo (12:00)...")

    # 1. Chọn nội dung theo ngày trong tuần
    thu = date.today().weekday()
    ten_thu = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"]
    _log(f"Hôm nay {ten_thu[thu]} → Chọn mẫu #{(thu % len(MAU_FEED)) + 1}")

    noi_dung = _chon_mau_theo_ngay()
    _log(f"Nội dung: {noi_dung[:80]}...")

    # 2. Đăng bài lên Feed
    ket_qua = False
    try:
        from features.auto_post import AutoPoster

        poster = AutoPoster()

        trang_thai_dang = {"ok": False, "loi": None}

        def _status_callback(msg):
            _log(msg)
            if "thành công" in msg.lower() or "đã đăng" in msg.lower():
                trang_thai_dang["ok"] = True
            if "lỗi" in msg.lower():
                trang_thai_dang["loi"] = msg

        thread = poster.post_now(
            text=noi_dung,
            image_paths=None,
            status_callback=_status_callback,
        )

        # Chờ hoàn tất (tối đa 120 giây)
        if thread:
            thread.join(timeout=120)

        ket_qua = trang_thai_dang["ok"]

    except Exception as e:
        _log(f"Lỗi khi đăng bài: {e}")
        ket_qua = False

    # 3. Ghi log kết quả
    logger.log("routine_dang_bai", {
        "thoi_gian": thoi_gian,
        "thu": ten_thu[date.today().weekday()],
        "mau_so": (date.today().weekday() % len(MAU_FEED)) + 1,
        "noi_dung_preview": noi_dung[:100].replace("\n", " "),
        "trang_thai": "Đã đăng" if ket_qua else "Lỗi",
    })

    if ket_qua:
        _log("Đăng bài Feed thành công!")
    else:
        _log("Đăng bài Feed thất bại hoặc không xác nhận được kết quả.")

    return ket_qua


if __name__ == "__main__":
    chay()
