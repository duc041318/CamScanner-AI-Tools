"""
Phân tích hiệu quả mẫu bài Zalo
─────────────────────────────────
Ghi lại mẫu bài nào được gửi cho ai → khi khách phản hồi
→ tính tỷ lệ hiệu quả từng mẫu → chọn mẫu theo trọng số.
"""

import csv
import hashlib
import os
import random
from datetime import date

# Đường dẫn tính từ vị trí file này
_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE      = os.path.join(_BASE, "data", "log_mau_bai.csv")
CONTACTS_FILE = os.path.join(_BASE, "data", "contacts.csv")
LOG_HEADERS   = ["mau_id", "mau_preview", "sdt", "ngay_gui"]

# Trạng thái tính là "đã phản hồi tích cực"
TRANG_THAI_TOT = {"co_phan_hoi", "quan_tam", "xem_dat", "da_coc"}

# Cần ít nhất bao nhiêu lần gửi để tin vào dữ liệu
MIN_GUI_DE_CAN_NHAC = 5


def mau_id(template: str) -> str:
    """Tạo ID ngắn ổn định cho 1 template (8 ký tự hex)."""
    return hashlib.md5(template[:80].encode("utf-8")).hexdigest()[:8]


class TemplateAnalytics:

    # ── Ghi log ───────────────────────────────────────────────────

    def ghi_log_gui(self, template: str, sdt_list: list):
        """Ghi nhận việc gửi template này cho danh sách SĐT."""
        mid    = mau_id(template)
        preview = template.replace("\n", " ")[:70]
        hom_nay = date.today().isoformat()

        file_moi = not os.path.exists(LOG_FILE)
        with open(LOG_FILE, "a", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=LOG_HEADERS)
            if file_moi:
                writer.writeheader()
            for sdt in sdt_list:
                writer.writerow({
                    "mau_id":      mid,
                    "mau_preview": preview,
                    "sdt":         sdt,
                    "ngay_gui":    hom_nay,
                })

    # ── Đọc log ───────────────────────────────────────────────────

    def _doc_log(self):
        if not os.path.exists(LOG_FILE):
            return []
        with open(LOG_FILE, "r", encoding="utf-8-sig") as f:
            return list(csv.DictReader(f))

    def _doc_trang_thai_hien_tai(self):
        """Trả về dict {sdt: trang_thai} từ contacts.csv."""
        if not os.path.exists(CONTACTS_FILE):
            return {}
        with open(CONTACTS_FILE, "r", encoding="utf-8-sig") as f:
            return {r["sdt"]: r.get("trang_thai","moi")
                    for r in csv.DictReader(f)}

    # ── Tính hiệu quả ─────────────────────────────────────────────

    def tinh_hieu_qua(self) -> list:
        """
        Trả về list các dict, mỗi dict là 1 mẫu bài:
          mau_id, mau_preview, so_gui, so_phan_hoi, ty_le, trong_so
        Sắp xếp giảm dần theo tỷ lệ.
        """
        log_rows  = self._doc_log()
        ts_hien_tai = self._doc_trang_thai_hien_tai()

        # Với mỗi SĐT, lấy mau_id gần nhất được gửi
        # (dùng để gán credit đúng mẫu)
        mau_gan_nhat = {}   # {sdt: mau_id}
        for row in log_rows:            # log đã sắp xếp theo thời gian ghi
            mau_gan_nhat[row["sdt"]] = row["mau_id"]

        # Thống kê per mau_id
        stats   = {}   # {mau_id: {"preview","gui","phan_hoi"}}
        for row in log_rows:
            mid     = row["mau_id"]
            preview = row.get("mau_preview","")
            if mid not in stats:
                stats[mid] = {"mau_preview": preview, "gui": 0, "phan_hoi": 0}
            stats[mid]["gui"] += 1

            # Gán credit nếu mẫu này là mẫu cuối cùng gửi cho SĐT này
            # và SĐT đó hiện có trạng thái tốt
            sdt = row["sdt"]
            if (mau_gan_nhat.get(sdt) == mid
                    and ts_hien_tai.get(sdt,"") in TRANG_THAI_TOT):
                stats[mid]["phan_hoi"] += 1

        # Loại bỏ đếm trùng (1 SĐT đã được đếm nhiều lần trong log)
        # → đếm unique SĐT per mau_id
        unique = {}  # {mau_id: {sdt set}}
        for row in log_rows:
            mid = row["mau_id"]
            unique.setdefault(mid, set()).add(row["sdt"])

        ket_qua = []
        for mid, s in stats.items():
            so_gui_unique   = len(unique.get(mid, set()))
            so_phan_hoi     = s["phan_hoi"]
            ty_le           = so_phan_hoi / so_gui_unique if so_gui_unique else 0
            trong_so        = _tinh_trong_so(ty_le, so_gui_unique)
            ket_qua.append({
                "mau_id":      mid,
                "mau_preview": s["mau_preview"],
                "so_gui":      so_gui_unique,
                "so_phan_hoi": so_phan_hoi,
                "ty_le":       ty_le,
                "trong_so":    trong_so,
            })

        ket_qua.sort(key=lambda x: x["ty_le"], reverse=True)
        return ket_qua

    # ── Chọn mẫu có trọng số ──────────────────────────────────────

    def chon_mau_co_trong_so(self, bai_list: list) -> tuple:
        """
        Chọn 1 template từ bai_list theo trọng số hiệu quả lịch sử.
        Trả về (template_text, mau_id).
        Nếu chưa có dữ liệu → random đều.
        """
        if not bai_list:
            return "", ""

        hieu_qua = {r["mau_id"]: r["trong_so"] for r in self.tinh_hieu_qua()}

        trong_so_list = []
        for bai in bai_list:
            mid = mau_id(bai)
            w   = hieu_qua.get(mid, 1.0)   # mẫu mới chưa có data → weight=1
            trong_so_list.append(w)

        chon = random.choices(bai_list, weights=trong_so_list, k=1)[0]
        return chon, mau_id(chon)

    # ── Tóm tắt nhanh ─────────────────────────────────────────────

    def tom_tat(self) -> str:
        """Chuỗi tóm tắt ngắn để in ra console."""
        rows = self.tinh_hieu_qua()
        if not rows:
            return "Chưa có dữ liệu phân tích (chưa ghi log lần gửi nào)."
        lines = ["ID       │ Gửi │ P.hồi │ Tỷ lệ │ Bar"]
        lines.append("─" * 44)
        for r in rows:
            bar = "█" * int(r["ty_le"] * 20) + "░" * (20 - int(r["ty_le"] * 20))
            lines.append(
                f"{r['mau_id']}  │ {r['so_gui']:>3} │  {r['so_phan_hoi']:>4} │"
                f" {r['ty_le']*100:>4.0f}% │ {bar[:10]}"
            )
        return "\n".join(lines)


def _tinh_trong_so(ty_le: float, so_gui: int) -> float:
    """
    Tính trọng số cho weighted random selection.
    - Chưa đủ MIN_GUI_DE_CAN_NHAC lần → weight = 1.0 (cần thêm data)
    - Đủ data: weight tỷ lệ với response rate, sàn 0.2 để mẫu tệ vẫn có cơ hội
    """
    if so_gui < MIN_GUI_DE_CAN_NHAC:
        return 1.0
    return max(ty_le * 10, 0.2)
