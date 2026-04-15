"""
Mini CRM - Quản lý danh sách khách hàng BĐS
Đọc/ghi contacts.csv, lọc, cập nhật trạng thái.
"""

import csv
import os
from datetime import date

CONTACTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "..", "data", "contacts.csv")
CONTACTS_FILE = os.path.normpath(CONTACTS_FILE)

HEADERS = ["sdt", "ho_ten", "nhom", "nguon", "trang_thai",
           "ghi_chu", "ngay_them", "ngay_lien_he_cuoi"]

TRANG_THAI_LIST = ["moi", "da_gui", "co_phan_hoi",
                   "quan_tam", "xem_dat", "da_coc", "khong_quan_tam"]

NHAN_TRANG_THAI = {
    "moi":            "Mới",
    "da_gui":         "Đã gửi tin",
    "co_phan_hoi":    "Có phản hồi",
    "quan_tam":       "Quan tâm",
    "xem_dat":        "Xem đất",
    "da_coc":         "Đã cọc",
    "khong_quan_tam": "Không quan tâm",
}

NHAN_NHOM = {
    "muon_o":  "Muốn ở",
    "dau_tu":  "Đầu tư",
    "chua_ro": "Chưa rõ",
}

NHAN_NGUON = {
    "zalo":       "Zalo",
    "facebook":   "Facebook",
    "gioi_thieu": "Giới thiệu",
    "tu_tim":     "Tự tìm",
}


class CRMManager:

    def doc_tat_ca(self):
        """Đọc toàn bộ contacts.csv, trả về list of dict."""
        if not os.path.exists(CONTACTS_FILE):
            return []
        with open(CONTACTS_FILE, "r", encoding="utf-8-sig") as f:
            return list(csv.DictReader(f))

    def ghi_tat_ca(self, rows):
        """Ghi toàn bộ danh sách xuống file."""
        with open(CONTACTS_FILE, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=HEADERS)
            writer.writeheader()
            writer.writerows(rows)

    def loc(self, trang_thai=None, nhom=None, tu_khoa=None):
        """Lọc danh sách theo tiêu chí. None = không lọc theo tiêu chí đó."""
        rows = self.doc_tat_ca()
        if trang_thai and trang_thai != "tat_ca":
            rows = [r for r in rows if r.get("trang_thai") == trang_thai]
        if nhom and nhom != "tat_ca":
            rows = [r for r in rows if r.get("nhom") == nhom]
        if tu_khoa:
            tu_khoa = tu_khoa.lower()
            rows = [r for r in rows
                    if tu_khoa in r.get("ho_ten", "").lower()
                    or tu_khoa in r.get("sdt", "")]
        return rows

    def cap_nhat(self, sdt, trang_thai=None, ghi_chu=None, ho_ten=None, nhom=None):
        """Cập nhật thông tin 1 khách theo SĐT. Trả về True nếu tìm thấy."""
        rows = self.doc_tat_ca()
        for row in rows:
            if row["sdt"] == sdt:
                if trang_thai:
                    row["trang_thai"] = trang_thai
                    row["ngay_lien_he_cuoi"] = date.today().isoformat()
                if ghi_chu is not None:
                    row["ghi_chu"] = ghi_chu
                if ho_ten:
                    row["ho_ten"] = ho_ten
                if nhom:
                    row["nhom"] = nhom
                self.ghi_tat_ca(rows)
                return True
        return False

    def them(self, sdt, ho_ten="", nhom="chua_ro", nguon="zalo", ghi_chu=""):
        """Thêm khách mới. Trả về False nếu SĐT đã tồn tại."""
        rows = self.doc_tat_ca()
        if any(r["sdt"] == sdt for r in rows):
            return False
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
        self.ghi_tat_ca(rows)
        return True

    def xoa(self, sdt):
        """Xóa khách khỏi danh sách."""
        rows = self.doc_tat_ca()
        rows_moi = [r for r in rows if r["sdt"] != sdt]
        if len(rows_moi) == len(rows):
            return False
        self.ghi_tat_ca(rows_moi)
        return True

    def thong_ke(self):
        """Trả về dict thống kê nhanh."""
        rows = self.doc_tat_ca()
        theo_ts = {}
        for r in rows:
            ts = r.get("trang_thai", "moi")
            theo_ts[ts] = theo_ts.get(ts, 0) + 1
        return {
            "tong": len(rows),
            "theo_trang_thai": theo_ts,
            "hot": theo_ts.get("quan_tam", 0) + theo_ts.get("co_phan_hoi", 0),
            "tiem_nang": theo_ts.get("xem_dat", 0),
            "da_coc": theo_ts.get("da_coc", 0),
            "moi": theo_ts.get("moi", 0),
        }
