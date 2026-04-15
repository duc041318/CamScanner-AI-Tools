"""
ROUTINE LÀM MỚI NỘI DUNG - Chạy lúc 08:00 mỗi Thứ Hai
Tự động tạo 5 mẫu bài Zalo mới cho tuần tiếp theo,
thay thế các mẫu cũ nhất trong file mau-bai-dang-zalo.txt.
"""

import os
import sys
from datetime import datetime, date

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "zalo-tool"))

from config import MAU_BAI_FILE

# ── 7 chủ đề xoay vòng theo tuần ─────────────────────────────────────────────
TUAN_CHU_DE = [
    "hạ tầng & quy hoạch",
    "so sánh giá thị trường",
    "lô góc đặc biệt",
    "câu chuyện đầu tư thành công",
    "ưu đãi & pháp lý",
    "vị trí & tiện ích",
    "tiềm năng sinh lời",
]

# ── Kho mẫu bài theo chủ đề ───────────────────────────────────────────────────
MAU_THEO_CHU_DE = {
    "hạ tầng & quy hoạch": [
        (
            "Chào {ho_ten} 👋\n\n"
            "🛣️ TIN NÓNG: Cao tốc Nội Bài - Hạ Long đang triển khai, "
            "đường vành đai 4 sắp khởi công - Sóc Sơn là tâm điểm!\n\n"
            "Đây là lúc mua đất TRƯỚC khi hạ tầng hoàn thiện để hưởng lợi tối đa.\n\n"
            "📍 Em đang có 2 lô đất tại Phú Tằng - Đa Phúc - Sóc Sơn:\n"
            "• Lô 1: 83m2, giá 1.66 tỷ - Sổ đỏ chính chủ\n"
            "• Lô 2: 88.5m2 (lô góc), giá 2.21 tỷ\n\n"
            "👉 Anh/chị muốn xem thêm không ạ? Inbox em nhé!"
        ),
        (
            "Dạ anh/chị {ho_ten}!\n\n"
            "📊 PHÂN TÍCH QUY HOẠCH SÓC SƠN 2030:\n"
            "✅ Lên quận trong lộ trình đô thị hóa Hà Nội\n"
            "✅ Sân bay Nội Bài mở rộng terminal T3\n"
            "✅ Khu công nghiệp Nội Bài - Sóc Sơn thu hút FDI lớn\n\n"
            "Giá đất hiện tại: 20-25 triệu/m2\n"
            "Dự báo 3 năm nữa: 35-45 triệu/m2\n\n"
            "💰 Tiềm năng tăng 50-80%!\n\n"
            "Em còn 2 lô đẹp - anh/chị quan tâm inbox ngay ạ!"
        ),
    ],
    "so sánh giá thị trường": [
        (
            "Chào {ho_ten} 👋\n\n"
            "💡 SO SÁNH GIÁ ĐẤT CÁC HUYỆN HÀ NỘI:\n\n"
            "📍 Đông Anh: 45-80 triệu/m2\n"
            "📍 Gia Lâm: 40-70 triệu/m2\n"
            "📍 Hoài Đức: 50-90 triệu/m2\n"
            "📍 Sóc Sơn: 20-30 triệu/m2 ← THẤP HƠN 40-50%!\n\n"
            "Tại sao lại chọn mua đắt khi Sóc Sơn đang có hạ tầng tương đương?\n\n"
            "📌 Em có lô đất tại Phú Tằng, giá chỉ 20-25 triệu/m2.\n"
            "Anh/chị inbox để xem chi tiết nhé!"
        ),
    ],
    "lô góc đặc biệt": [
        (
            "Chào {ho_ten} 👋\n\n"
            "🔥 LÔ GÓC 2 MẶT THOÁNG - CƠ HỘI CUỐI!\n\n"
            "📐 Diện tích: 88.5m2 (15.93 x 5.56m)\n"
            "💰 Giá: 2.21 tỷ (25 triệu/m2)\n"
            "📄 Sổ đỏ: AA 02367049 - Chính chủ\n\n"
            "✨ Ưu điểm lô góc:\n"
            "• 2 mặt tiếp giáp đường → dễ ra vào, thoáng gió\n"
            "• Giá trị cao hơn lô thường 15-20%\n"
            "• Xây nhà đẹp hơn, đón sáng tốt hơn\n"
            "• Thường bán trước so với lô thường\n\n"
            "⚠️ Chỉ còn 1 lô góc duy nhất!\n"
            "👉 Inbox ngay để giữ chỗ ạ!"
        ),
    ],
    "câu chuyện đầu tư thành công": [
        (
            "Chào {ho_ten} 👋\n\n"
            "📖 CÂU CHUYỆN THẬT: Anh Tuấn (Cầu Giấy)\n\n"
            "\"Năm 2023, mình mua 1 lô 90m2 ở Sóc Sơn giá 1.5 tỷ. "
            "Bạn bè bảo mua đất 'vùng sâu vùng xa'. "
            "Đến nay lô đó được hỏi mua 2.1 tỷ - lãi 600 triệu sau 2 năm!\"\n\n"
            "Bí quyết của anh Tuấn:\n"
            "✅ Mua khi hạ tầng ĐANG triển khai, không phải khi đã xong\n"
            "✅ Chọn đất có sổ đỏ, pháp lý sạch\n"
            "✅ Vị trí gần đường chính, khu dân cư\n\n"
            "📌 Em đang có lô đất tương tự tại Phú Tằng - Sóc Sơn.\n"
            "Anh/chị muốn nghe phân tích chi tiết không ạ?"
        ),
    ],
    "ưu đãi & pháp lý": [
        (
            "Chào {ho_ten} 👋\n\n"
            "✅ PHÁP LÝ 100% MINH BẠCH - KHÔNG LO RỦI RO!\n\n"
            "Lô đất tại Phú Tằng - Sóc Sơn:\n"
            "📄 Sổ đỏ: Đã cấp, tên chính chủ\n"
            "📄 Nguồn gốc: Nhận chuyển nhượng - sổ chính chủ\n"
            "📄 Quy hoạch: Đất ở nông thôn, được xây dựng\n"
            "📄 Thủ tục: Sang tên ngay sau khi đặt cọc\n\n"
            "💰 Giá:\n"
            "• Lô 1 (83m2): 1.66 tỷ\n"
            "• Lô 2 góc (88.5m2): 2.21 tỷ\n\n"
            "🏦 Ngân hàng hỗ trợ vay 70% giá trị đất!\n\n"
            "👉 Anh/chị muốn xem hồ sơ pháp lý không ạ? Inbox em!"
        ),
    ],
    "vị trí & tiện ích": [
        (
            "Chào {ho_ten} 👋\n\n"
            "📍 VỊ TRÍ ĐẮCĐỊA - TIỆN ÍCH HOÀN HẢO:\n\n"
            "🛫 Cách sân bay Nội Bài: 15 phút\n"
            "🏪 Cách trung tâm huyện Sóc Sơn: 5 phút\n"
            "🏫 Trường học, bệnh viện: Trong bán kính 2km\n"
            "🛣️ Đường bê tông nội khu: 4-5m, xe ô tô vào tận cửa\n"
            "🏘️ Khu dân cư hiện hữu: Hàng xóm đông đúc, an ninh tốt\n\n"
            "📌 Lô đất tại Phú Tằng - Đa Phúc - Sóc Sơn:\n"
            "• 83m2 - 1.66 tỷ | 88.5m2 (góc) - 2.21 tỷ\n\n"
            "🚗 Em sắp xếp xe đưa anh/chị đi xem đất miễn phí!\n"
            "Inbox em chốt lịch nhé 🙏"
        ),
    ],
    "tiềm năng sinh lời": [
        (
            "Chào {ho_ten} 👋\n\n"
            "📈 TÍNH TOÁN LỢI NHUẬN ĐẦU TƯ ĐẤT SÓC SƠN:\n\n"
            "Kịch bản: Mua lô 1 (83m2) giá 1.66 tỷ\n\n"
            "📊 Sau 2 năm (tăng 20%): Thu về 2.0 tỷ → Lãi 340 triệu\n"
            "📊 Sau 3 năm (tăng 40%): Thu về 2.3 tỷ → Lãi 640 triệu\n"
            "📊 Sau 5 năm (tăng 80%): Thu về 3.0 tỷ → Lãi 1.34 tỷ\n\n"
            "So với gửi ngân hàng 1.66 tỷ x 5 năm x 5%/năm = lãi 415 triệu\n\n"
            "Đất Sóc Sơn có tiềm năng sinh lời GẤP 3 lần gửi tiết kiệm!\n\n"
            "👉 Anh/chị muốn phân tích chi tiết theo ngân sách không ạ?"
        ),
    ],
}


def _doc_mau_cu(mau_bai_file):
    """Đọc file mẫu bài hiện tại."""
    if not os.path.exists(mau_bai_file):
        return ""
    with open(mau_bai_file, "r", encoding="utf-8") as f:
        return f.read()


def _tao_mau_moi(chu_de):
    """Lấy mẫu bài cho chủ đề tuần này."""
    import random
    mau_list = MAU_THEO_CHU_DE.get(chu_de, [])
    if not mau_list:
        return None
    return random.choice(mau_list)


def chay(log_callback=None):
    """Chạy routine làm mới nội dung Thứ Hai hàng tuần."""
    thoi_gian = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tuan_so = date.today().isocalendar()[1]

    def _log(msg):
        print(f"[NOI DUNG {thoi_gian}] {msg}")
        if log_callback:
            log_callback(msg)

    _log("Bắt đầu Routine Làm Mới Nội Dung Tuần...")

    # Chọn chủ đề tuần này
    chu_de = TUAN_CHU_DE[tuan_so % len(TUAN_CHU_DE)]
    _log(f"Chủ đề tuần {tuan_so}: '{chu_de}'")

    # Tạo mẫu mới
    mau_moi = _tao_mau_moi(chu_de)
    if not mau_moi:
        _log(f"Không có mẫu cho chủ đề '{chu_de}', bỏ qua.")
        return False

    # Đọc file hiện tại
    noi_dung_cu = _doc_mau_cu(MAU_BAI_FILE)

    # Thêm mẫu mới vào cuối
    sep = "\n=====================================================\n"
    tieu_de = f"BÀI MỚI TUẦN {tuan_so} - CHỦ ĐỀ: {chu_de.upper()}\n"
    noi_dung_them = sep + tieu_de + sep + "\n" + mau_moi + "\n"

    with open(MAU_BAI_FILE, "a", encoding="utf-8") as f:
        f.write(noi_dung_them)

    _log(f"Đã thêm mẫu bài mới vào {MAU_BAI_FILE}")
    _log(f"Xem trước: {mau_moi[:100]}...")
    return True


if __name__ == "__main__":
    chay()
