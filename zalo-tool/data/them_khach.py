"""
THÊM KHÁCH HÀNG MỚI - Công cụ dòng lệnh
─────────────────────────────────────────
Cách dùng:

  # Thêm 1 khách:
  python them_khach.py 0912345678 "Anh Nam" dau_tu zalo

  # Thêm nhiều khách từ file .txt (mỗi dòng 1 SĐT):
  python them_khach.py --file sdt_moi.txt

  # Xem thống kê danh sách:
  python them_khach.py --stats

  # Tìm khách theo SĐT:
  python them_khach.py --tim 0912345678

  # Cập nhật trạng thái:
  python them_khach.py --cap-nhat 0912345678 quan_tam "Hỏi về lô 1"
"""

import csv
import os
import sys
from datetime import date, datetime

CONTACTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "contacts.csv")

TRANG_THAI_HOP_LE = ["moi", "da_gui", "co_phan_hoi", "quan_tam", "xem_dat", "da_coc", "khong_quan_tam"]
NHOM_HOP_LE = ["muon_o", "dau_tu", "chua_ro"]
NGUON_HOP_LE = ["zalo", "facebook", "gioi_thieu", "tu_tim"]

HEADERS = ["sdt", "ho_ten", "nhom", "nguon", "trang_thai", "ghi_chu", "ngay_them", "ngay_lien_he_cuoi"]


# ── Đọc / Ghi ─────────────────────────────────────────────────────────────────

def _doc_tat_ca():
    if not os.path.exists(CONTACTS_FILE):
        return []
    with open(CONTACTS_FILE, "r", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def _ghi_tat_ca(rows):
    with open(CONTACTS_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(rows)


def _chuan_hoa_sdt(sdt):
    """Chuẩn hóa SĐT: bỏ khoảng trắng, thêm 0 nếu thiếu."""
    sdt = sdt.strip().replace(" ", "").replace("-", "")
    if sdt.startswith("+84"):
        sdt = "0" + sdt[3:]
    return sdt


# ── Thêm 1 khách ──────────────────────────────────────────────────────────────

def them_khach(sdt, ho_ten="", nhom="chua_ro", nguon="zalo", ghi_chu=""):
    sdt = _chuan_hoa_sdt(sdt)

    rows = _doc_tat_ca()
    sdt_hien_co = {r["sdt"] for r in rows}

    if sdt in sdt_hien_co:
        print(f"[!] SĐT {sdt} đã tồn tại trong danh sách.")
        return False

    if nhom not in NHOM_HOP_LE:
        print(f"[!] nhom không hợp lệ: '{nhom}'. Chọn: {', '.join(NHOM_HOP_LE)}")
        nhom = "chua_ro"

    if nguon not in NGUON_HOP_LE:
        print(f"[!] nguon không hợp lệ: '{nguon}'. Chọn: {', '.join(NGUON_HOP_LE)}")
        nguon = "zalo"

    rows.append({
        "sdt": sdt,
        "ho_ten": ho_ten or f"Khách {sdt[-4:]}",
        "nhom": nhom,
        "nguon": nguon,
        "trang_thai": "moi",
        "ghi_chu": ghi_chu,
        "ngay_them": date.today().isoformat(),
        "ngay_lien_he_cuoi": "",
    })

    _ghi_tat_ca(rows)
    print(f"[+] Đã thêm: {ho_ten or sdt} ({sdt}) - {nhom} - {nguon}")
    return True


# ── Thêm từ file .txt ─────────────────────────────────────────────────────────

def them_tu_file(duong_dan_file, nhom="chua_ro", nguon="zalo"):
    if not os.path.exists(duong_dan_file):
        print(f"[!] Không tìm thấy file: {duong_dan_file}")
        return

    them = 0
    bo_qua = 0

    with open(duong_dan_file, "r", encoding="utf-8-sig") as f:
        for dong in f:
            dong = dong.strip()
            if not dong or dong.startswith("#"):
                continue

            # Hỗ trợ định dạng: "SĐT" hoặc "SĐT,Tên" hoặc "SĐT Tên"
            phan = dong.replace(",", " ").split()
            sdt = phan[0]
            ho_ten = " ".join(phan[1:]) if len(phan) > 1 else ""

            ok = them_khach(sdt, ho_ten, nhom, nguon)
            if ok:
                them += 1
            else:
                bo_qua += 1

    print(f"\nKết quả: Thêm mới {them}, Bỏ qua (trùng) {bo_qua}")


# ── Cập nhật trạng thái ────────────────────────────────────────────────────────

def cap_nhat_trang_thai(sdt, trang_thai, ghi_chu=""):
    sdt = _chuan_hoa_sdt(sdt)

    if trang_thai not in TRANG_THAI_HOP_LE:
        print(f"[!] trang_thai không hợp lệ: '{trang_thai}'")
        print(f"    Chọn 1 trong: {', '.join(TRANG_THAI_HOP_LE)}")
        return False

    rows = _doc_tat_ca()
    tim_thay = False

    for row in rows:
        if row["sdt"] == sdt:
            row["trang_thai"] = trang_thai
            row["ngay_lien_he_cuoi"] = date.today().isoformat()
            if ghi_chu:
                row["ghi_chu"] = ghi_chu
            tim_thay = True
            break

    if not tim_thay:
        print(f"[!] Không tìm thấy SĐT: {sdt}")
        return False

    _ghi_tat_ca(rows)
    print(f"[+] Cập nhật {sdt}: trang_thai={trang_thai}" + (f", ghi_chu={ghi_chu}" if ghi_chu else ""))
    return True


# ── Tìm khách ─────────────────────────────────────────────────────────────────

def tim_khach(sdt):
    sdt = _chuan_hoa_sdt(sdt)
    rows = _doc_tat_ca()
    for row in rows:
        if row["sdt"] == sdt:
            print("\n── Thông tin khách ──────────────────")
            for k, v in row.items():
                print(f"  {k:<22}: {v}")
            print("─────────────────────────────────────")
            return row
    print(f"[!] Không tìm thấy SĐT: {sdt}")
    return None


# ── Thống kê ──────────────────────────────────────────────────────────────────

def thong_ke():
    rows = _doc_tat_ca()
    if not rows:
        print("Danh sách trống.")
        return

    tong = len(rows)
    theo_trang_thai = {}
    theo_nhom = {}
    theo_nguon = {}

    for r in rows:
        ts = r.get("trang_thai", "?")
        nh = r.get("nhom", "?")
        ng = r.get("nguon", "?")
        theo_trang_thai[ts] = theo_trang_thai.get(ts, 0) + 1
        theo_nhom[nh] = theo_nhom.get(nh, 0) + 1
        theo_nguon[ng] = theo_nguon.get(ng, 0) + 1

    nhan_trang_thai = {
        "moi": "Mới chưa liên hệ",
        "da_gui": "Đã gửi tin",
        "co_phan_hoi": "Có phản hồi",
        "quan_tam": "Quan tâm mạnh",
        "xem_dat": "Đã/Sắp xem đất",
        "da_coc": "Đã cọc",
        "khong_quan_tam": "Không quan tâm",
    }

    print(f"""
╔══════════════════════════════════════╗
║      THỐNG KÊ DANH SÁCH KHÁCH       ║
╠══════════════════════════════════════╣
║  Tổng số: {tong:<27}║
╠══════════════════════════════════════╣
║  THEO TRẠNG THÁI:                   ║""")

    for ts in TRANG_THAI_HOP_LE:
        so = theo_trang_thai.get(ts, 0)
        if so > 0:
            bar = "█" * min(so, 20)
            ten = nhan_trang_thai.get(ts, ts)
            print(f"║  {ten:<20} {so:>3}  {bar}")

    print(f"""╠══════════════════════════════════════╣
║  THEO NHÓM:                         ║
║  Muốn ở         : {theo_nhom.get('muon_o', 0):<19}║
║  Đầu tư         : {theo_nhom.get('dau_tu', 0):<19}║
║  Chưa rõ        : {theo_nhom.get('chua_ro', 0):<19}║
╠══════════════════════════════════════╣
║  THEO NGUỒN:                        ║
║  Zalo           : {theo_nguon.get('zalo', 0):<19}║
║  Facebook       : {theo_nguon.get('facebook', 0):<19}║
║  Giới thiệu     : {theo_nguon.get('gioi_thieu', 0):<19}║
║  Tự tìm         : {theo_nguon.get('tu_tim', 0):<19}║
╚══════════════════════════════════════╝""")

    # Danh sách quan tâm mạnh
    hot = [r for r in rows if r.get("trang_thai") in ("quan_tam", "xem_dat")]
    if hot:
        print(f"\n🔥 KHÁCH NÓNG cần chăm sóc ngay ({len(hot)} người):")
        for r in hot:
            print(f"  • {r['ho_ten']:<15} {r['sdt']}  [{r['trang_thai']}]  {r.get('ghi_chu','')}")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]

    if not args or args[0] == "--stats":
        thong_ke()

    elif args[0] == "--file":
        if len(args) < 2:
            print("Dùng: python them_khach.py --file ten_file.txt [nhom] [nguon]")
            return
        nhom = args[2] if len(args) > 2 else "chua_ro"
        nguon = args[3] if len(args) > 3 else "zalo"
        them_tu_file(args[1], nhom, nguon)

    elif args[0] == "--tim":
        if len(args) < 2:
            print("Dùng: python them_khach.py --tim 0912345678")
            return
        tim_khach(args[1])

    elif args[0] == "--cap-nhat":
        if len(args) < 3:
            print("Dùng: python them_khach.py --cap-nhat 0912345678 quan_tam [ghi_chu]")
            return
        ghi_chu = args[3] if len(args) > 3 else ""
        cap_nhat_trang_thai(args[1], args[2], ghi_chu)

    elif args[0] == "--help":
        print(__doc__)

    else:
        # Thêm 1 khách: python them_khach.py SĐT [Tên] [nhom] [nguon] [ghi_chu]
        sdt = args[0]
        ho_ten = args[1] if len(args) > 1 else ""
        nhom = args[2] if len(args) > 2 else "chua_ro"
        nguon = args[3] if len(args) > 3 else "zalo"
        ghi_chu = args[4] if len(args) > 4 else ""
        them_khach(sdt, ho_ten, nhom, nguon, ghi_chu)


if __name__ == "__main__":
    main()
