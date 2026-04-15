"""
ROUTINE BÁO CÁO NGÀY - Chạy lúc 21:00 mỗi ngày
Tổng hợp kết quả chiến dịch Zalo trong ngày, lưu file báo cáo.
"""

import csv
import os
import sys
from datetime import date, datetime

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "zalo-tool"))

from config import BAO_CAO_DIR


def _doc_log_theo_ngay(log_dir, hom_nay):
    """Đọc tất cả file log hôm nay, trả về dict thống kê."""
    thong_ke = {
        "bulk_message": {"tong": 0, "thanh_cong": 0, "khong_tim_thay": 0, "loi": 0, "sdt_list": []},
        "auto_post": {"tong": 0, "da_dang": 0, "loi": 0},
    }

    if not os.path.exists(log_dir):
        return thong_ke

    for fname in os.listdir(log_dir):
        if hom_nay not in fname:
            continue

        fpath = os.path.join(log_dir, fname)
        try:
            with open(fpath, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
        except Exception:
            continue

        if "bulk_message" in fname:
            for row in rows:
                thong_ke["bulk_message"]["tong"] += 1
                ts = row.get("trang_thai", "")
                sdt = row.get("sdt", "")
                ho_ten = row.get("ho_ten", "")
                if ts == "Thành công":
                    thong_ke["bulk_message"]["thanh_cong"] += 1
                    thong_ke["bulk_message"]["sdt_list"].append(f"{ho_ten} ({sdt})")
                elif ts == "Không tìm thấy":
                    thong_ke["bulk_message"]["khong_tim_thay"] += 1
                else:
                    thong_ke["bulk_message"]["loi"] += 1

        elif "auto_post" in fname:
            for row in rows:
                thong_ke["auto_post"]["tong"] += 1
                ts = row.get("trang_thai", "")
                if ts == "Đã đăng":
                    thong_ke["auto_post"]["da_dang"] += 1
                elif "Lỗi" in ts:
                    thong_ke["auto_post"]["loi"] += 1

    return thong_ke


def _tinh_ty_le(thanh_cong, tong):
    if tong == 0:
        return "0%"
    return f"{int(thanh_cong / tong * 100)}%"


def _de_xuat_ngay_mai(thong_ke):
    """Sinh đề xuất chiến thuật cho ngày mai."""
    ts = thong_ke["bulk_message"]["thanh_cong"]
    tong = thong_ke["bulk_message"]["tong"]
    ty_le = ts / tong if tong > 0 else 0

    if ty_le >= 0.9:
        return "Hệ thống hoạt động tốt. Ngày mai tăng số lượng danh sách lên 20%."
    elif ty_le >= 0.7:
        return "Tỷ lệ gửi khá tốt. Kiểm tra lại SĐT không tìm thấy - có thể cần cập nhật danh sách."
    elif ty_le >= 0.5:
        return "Tỷ lệ gửi trung bình. Kiểm tra kết nối Zalo PC và cập nhật danh sách khách mới."
    else:
        return "Tỷ lệ gửi thấp. Kiểm tra: (1) Zalo PC đang mở không? (2) Danh sách SĐT hợp lệ không?"


def _tao_bai_dang_ngay_mai():
    """Gợi ý chủ đề bài đăng ngày mai (xoay vòng 5 chủ đề)."""
    ngay = date.today().weekday()  # 0=Thứ 2, 6=CN
    chu_de = [
        "Góc độ: Hạ tầng Sóc Sơn - Nội Bài đang bứt phá",
        "Góc độ: So sánh giá với Đông Anh, Gia Lâm (Sóc Sơn rẻ hơn 40%)",
        "Góc độ: Lô góc 2 mặt thoáng - cơ hội hiếm có",
        "Góc độ: Câu chuyện thành công khách hàng đã mua đất Sóc Sơn",
        "Góc độ: Ưu đãi đặc biệt - thanh toán nhanh nhận ngay sổ đỏ",
        "Góc độ: Vị trí đắc địa - 15 phút ra sân bay Nội Bài",
        "Góc độ: Đất thổ cư full - xây nhà liền không cần chuyển đổi",
    ]
    return chu_de[ngay % len(chu_de)]


def chay(log_callback=None):
    """Chạy routine báo cáo ngày."""
    hom_nay = date.today().strftime("%Y-%m-%d")
    thoi_gian = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _log(msg):
        print(f"[BAO CAO {thoi_gian}] {msg}")
        if log_callback:
            log_callback(msg)

    _log("Đang tổng hợp báo cáo ngày...")

    # Đường dẫn log
    log_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "zalo-tool", "logs"
    )

    # Đọc dữ liệu log
    thong_ke = _doc_log_theo_ngay(log_dir, hom_nay)
    bm = thong_ke["bulk_message"]
    ap = thong_ke["auto_post"]

    # Tạo nội dung báo cáo
    de_xuat = _de_xuat_ngay_mai(thong_ke)
    chu_de_ngay_mai = _tao_bai_dang_ngay_mai()

    bao_cao = f"""
╔══════════════════════════════════════════════════════════════╗
║          BÁO CÁO CHIẾN DỊCH ZALO - {hom_nay}           ║
╚══════════════════════════════════════════════════════════════╝

📊 KẾT QUẢ NHẮN TIN HÀNG LOẠT
─────────────────────────────────────────
  Tổng SĐT xử lý   : {bm['tong']}
  Gửi thành công   : {bm['thanh_cong']} ({_tinh_ty_le(bm['thanh_cong'], bm['tong'])})
  Không tìm thấy   : {bm['khong_tim_thay']}
  Lỗi              : {bm['loi']}

📝 KẾT QUẢ ĐĂNG BÀI TỰ ĐỘNG
─────────────────────────────────────────
  Tổng bài đăng    : {ap['tong']}
  Đã đăng thành công: {ap['da_dang']}
  Lỗi              : {ap['loi']}

👥 DANH SÁCH KHÁCH ĐÃ NHẬN TIN HÔM NAY
─────────────────────────────────────────
{chr(10).join(f'  • {s}' for s in bm['sdt_list']) if bm['sdt_list'] else '  (Chưa có dữ liệu)'}

💡 ĐỀ XUẤT CHO NGÀY MAI
─────────────────────────────────────────
  {de_xuat}

📌 CHỦ ĐỀ BÀI ĐĂNG NGÀY MAI GỢI Ý
─────────────────────────────────────────
  {chu_de_ngay_mai}

══════════════════════════════════════════════════════════════
Báo cáo tự động lúc {thoi_gian}
Dự án: Phú Tằng - Đa Phúc - Sóc Sơn (Lô 1: 1.66 tỷ | Lô 2 góc: 2.21 tỷ)
══════════════════════════════════════════════════════════════
"""

    # Lưu file báo cáo
    os.makedirs(BAO_CAO_DIR, exist_ok=True)
    bao_cao_file = os.path.join(BAO_CAO_DIR, f"bao-cao-{hom_nay}.txt")

    with open(bao_cao_file, "w", encoding="utf-8") as f:
        f.write(bao_cao)

    _log(f"Đã lưu báo cáo: {bao_cao_file}")

    # In ra console
    print(bao_cao)

    return bao_cao_file


if __name__ == "__main__":
    chay()
