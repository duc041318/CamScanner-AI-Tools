"""
WIZARD SETUP DỰ ÁN MỚI
─────────────────────────────────────────
Chạy script này khi có dự án BĐS mới để cập nhật config tự động:

    python scripts/du_an_moi.py

Hỏi các thông tin:
1. Tên dự án
2. Số lô đất (tối đa 5)
3. Thông tin từng lô: tên, diện tích, giá, vị trí, số sổ, điểm mạnh
4. Giờ gửi tin (mặc định 07:00, 19:30, 21:00)
5. Xác nhận trước khi ghi

Ghi đè file routines/config.py với thông tin mới.
BACKUP config cũ vào routines/config.backup.py trước khi ghi.
"""

import os
import sys
import shutil
from datetime import datetime

# Đường dẫn
_SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
_ROOT_DIR    = os.path.dirname(_SCRIPT_DIR)
_CONFIG_FILE = os.path.join(_ROOT_DIR, "routines", "config.py")


# ── Helpers ────────────────────────────────────────────────────────────────────

def _hoi(cau_hoi: str, mac_dinh: str = "") -> str:
    """In câu hỏi và nhận đầu vào, có hỗ trợ giá trị mặc định."""
    if mac_dinh:
        prompt = f"  {cau_hoi} [{mac_dinh}]: "
    else:
        prompt = f"  {cau_hoi}: "
    try:
        ans = input(prompt).strip()
    except (KeyboardInterrupt, EOFError):
        print("\n\nĐã hủy.")
        sys.exit(0)
    return ans if ans else mac_dinh


def _validate_gio(s: str) -> bool:
    """Kiểm tra định dạng HH:MM."""
    parts = s.split(":")
    if len(parts) != 2:
        return False
    try:
        h, m = int(parts[0]), int(parts[1])
        return 0 <= h <= 23 and 0 <= m <= 59
    except ValueError:
        return False


def _hoi_gio(cau_hoi: str, mac_dinh: str) -> str:
    """Hỏi giờ với validate HH:MM."""
    while True:
        val = _hoi(cau_hoi, mac_dinh)
        if _validate_gio(val):
            return val
        print(f"    ⚠ Định dạng không đúng. Vui lòng nhập HH:MM (ví dụ: 07:00)")


def _hoi_so(cau_hoi: str, mac_dinh: str, min_val: int = None, max_val: int = None) -> int:
    """Hỏi số nguyên với validate range."""
    while True:
        val = _hoi(cau_hoi, mac_dinh)
        try:
            n = int(val)
            if min_val is not None and n < min_val:
                print(f"    ⚠ Giá trị phải >= {min_val}")
                continue
            if max_val is not None and n > max_val:
                print(f"    ⚠ Giá trị phải <= {max_val}")
                continue
            return n
        except ValueError:
            print(f"    ⚠ Vui lòng nhập số nguyên hợp lệ.")


def _hoi_lo_dat(so_lo: int) -> dict:
    """Hỏi thông tin từng lô đất. Trả về dict {lo1: {...}, lo2: {...}, ...}."""
    lo_dat = {}
    for i in range(1, so_lo + 1):
        print(f"\n  --- Lô {i} ---")
        ten       = _hoi(f"Tên lô {i}", f"Lô {i}")
        dien_tich = _hoi("Diện tích (ví dụ: 83m2 hoặc 8.12x10.41m)", f"{80 + i * 5}m2")
        gia        = _hoi("Giá bán (ví dụ: 1.66 tỷ (20 triệu/m2))", "1.5 tỷ")
        vi_tri     = _hoi("Vị trí (thôn/xã/huyện)", "Sóc Sơn, Hà Nội")
        so_do      = _hoi("Số sổ đỏ (để trống nếu chưa có)", "")
        diem_manh  = _hoi("Điểm mạnh nổi bật", "Sổ đỏ chính chủ, pháp lý sạch")

        lo_dat[f"lo{i}"] = {
            "ten":       ten,
            "dien_tich": dien_tich,
            "gia":       gia,
            "vi_tri":    vi_tri,
            "so_do":     so_do,
            "diem_manh": diem_manh,
        }
    return lo_dat


def _lo_dat_to_python(lo_dat: dict) -> str:
    """Chuyển dict lo_dat thành chuỗi Python code (block LO_DAT)."""
    lines = ["LO_DAT = {"]
    for key, lo in lo_dat.items():
        lines.append(f'    "{key}": {{')
        lines.append(f'        "ten":       "{lo["ten"]}",')
        lines.append(f'        "dien_tich": "{lo["dien_tich"]}",')
        lines.append(f'        "gia":       "{lo["gia"]}",')
        lines.append(f'        "vi_tri":    "{lo["vi_tri"]}",')
        lines.append(f'        "so_do":     "{lo["so_do"]}",')
        lines.append(f'        "diem_manh": "{lo["diem_manh"]}",')
        lines.append("    },")
    lines.append("}")
    return "\n".join(lines)


def _tinh_gia_tu(lo_dat: dict) -> str:
    """Lấy giá thấp nhất trong các lô để điền vào TEMPLATE_VARS_DEFAULT."""
    # Lấy giá lô đầu tiên như mặc định
    if lo_dat:
        first = next(iter(lo_dat.values()))
        return first.get("gia", "").split("(")[0].strip()
    return "liên hệ"


def _tinh_dien_tich(lo_dat: dict) -> str:
    """Ghép diện tích các lô."""
    sizes = [lo.get("dien_tich", "").split("(")[0].strip() for lo in lo_dat.values()]
    if len(sizes) == 1:
        return sizes[0]
    # Lấy phần số đầu tiên mỗi lô để ghép dải
    nums = []
    for s in sizes:
        part = s.split("m")[0].strip()
        if part:
            nums.append(part)
    if len(nums) >= 2:
        return f"{nums[0]}-{nums[-1]}m2"
    return sizes[0] if sizes else "đang cập nhật"


def _tao_config(du_an: str, lo_dat: dict, lich: dict) -> str:
    """Sinh nội dung file config.py mới."""
    lo_py       = _lo_dat_to_python(lo_dat)
    gia_tu      = _tinh_gia_tu(lo_dat)
    dien_tich   = _tinh_dien_tich(lo_dat)
    gen_time    = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return f'''"""
Cấu hình chung cho tất cả Routines BĐS Sóc Sơn.
Chỉnh sửa file này khi cần cập nhật thông tin dự án hoặc lịch.
Tự động tạo bởi scripts/du_an_moi.py lúc {gen_time}
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
DU_AN = "{du_an}"

{lo_py}

# Biến mẫu mặc định cho template
TEMPLATE_VARS_DEFAULT = {{
    "du_an": DU_AN,
    "gia": "{gia_tu}",
    "dien_tich": "{dien_tich}",
}}

# ── Cài đặt gửi tin ────────────────────────────────────────────────────────────
DELAY_MIN_SANG = 10   # giây, buổi sáng gửi nhanh hơn
DELAY_MAX_SANG = 25
DELAY_MIN_TOI = 15    # buổi tối chậm hơn để tránh spam
DELAY_MAX_TOI = 40

# ── Lịch chạy (giờ:phút) ──────────────────────────────────────────────────────
LICH_SANG = "{lich_sang}"
LICH_TOI = "{lich_toi}"
LICH_BAO_CAO = "{lich_bao_cao}"
LICH_NOI_DUNG = "08:00"   # Thứ Hai
'''.format(
        du_an=du_an,
        lo_py=lo_py,
        gia_tu=gia_tu,
        dien_tich=dien_tich,
        lich_sang=lich["sang"],
        lich_toi=lich["toi"],
        lich_bao_cao=lich["bao_cao"],
        gen_time=gen_time,
    )


def _in_preview(du_an: str, lo_dat: dict, lich: dict):
    """In preview cấu hình sẽ được ghi."""
    print("\n" + "═" * 56)
    print("  PREVIEW CẤU HÌNH SẼ ĐƯỢC TẠO")
    print("═" * 56)
    print(f"  Dự án   : {du_an}")
    print(f"  Số lô   : {len(lo_dat)}")
    for key, lo in lo_dat.items():
        print(f"\n  [{key.upper()}] {lo['ten']}")
        print(f"    Diện tích : {lo['dien_tich']}")
        print(f"    Giá       : {lo['gia']}")
        print(f"    Vị trí    : {lo['vi_tri']}")
        if lo['so_do']:
            print(f"    Sổ đỏ     : {lo['so_do']}")
        print(f"    Điểm mạnh : {lo['diem_manh']}")
    print(f"\n  Lịch gửi sáng   : {lich['sang']}")
    print(f"  Lịch gửi tối    : {lich['toi']}")
    print(f"  Lịch báo cáo    : {lich['bao_cao']}")
    print("═" * 56)


def _backup_config():
    """Backup config.py hiện tại với timestamp."""
    if not os.path.exists(_CONFIG_FILE):
        return None

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = _CONFIG_FILE.replace("config.py", f"config.backup_{ts}.py")
    shutil.copy2(_CONFIG_FILE, backup_path)
    return backup_path


# ── Wizard chính ───────────────────────────────────────────────────────────────

def main():
    print()
    print("╔══════════════════════════════════════════════════════╗")
    print("║          WIZARD SETUP DỰ ÁN BĐS MỚI                ║")
    print("║  Tự động cập nhật routines/config.py                ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()
    print("  Nhấn Enter để giữ giá trị mặc định trong [dấu ngoặc]")
    print("  Nhấn Ctrl+C để hủy bất cứ lúc nào.")
    print()

    # 1. Tên dự án
    print("─── 1. THÔNG TIN DỰ ÁN ───────────────────────────────")
    du_an = _hoi("Tên dự án", "Phú Tằng - Đa Phúc - Sóc Sơn")

    # 2. Số lô đất
    print()
    print("─── 2. SỐ LÔ ĐẤT ────────────────────────────────────")
    so_lo = _hoi_so("Số lô đất (1-5)", "2", min_val=1, max_val=5)

    # 3. Thông tin từng lô
    print()
    print("─── 3. THÔNG TIN TỪNG LÔ ────────────────────────────")
    lo_dat = _hoi_lo_dat(so_lo)

    # 4. Lịch gửi
    print()
    print("─── 4. LỊCH CHẠY ─────────────────────────────────────")
    lich_sang    = _hoi_gio("Giờ gửi tin buổi sáng (HH:MM)", "07:00")
    lich_toi     = _hoi_gio("Giờ gửi tin buổi tối (HH:MM)", "19:30")
    lich_bao_cao = _hoi_gio("Giờ tạo báo cáo (HH:MM)", "21:00")

    lich = {"sang": lich_sang, "toi": lich_toi, "bao_cao": lich_bao_cao}

    # 5. Preview và xác nhận
    print()
    _in_preview(du_an, lo_dat, lich)
    print()
    xac_nhan = _hoi("Xác nhận ghi config? (y/N)", "n").lower()

    if xac_nhan not in ("y", "yes", "co", "có"):
        print("\n  Đã hủy. Không có thay đổi nào được lưu.")
        return

    # 6. Backup config cũ
    backup_path = _backup_config()
    if backup_path:
        print(f"\n  ✓ Đã backup config cũ: {backup_path}")
    else:
        print("\n  ℹ Không tìm thấy config cũ để backup.")

    # 7. Ghi config mới
    noi_dung_moi = _tao_config(du_an, lo_dat, lich)
    os.makedirs(os.path.dirname(_CONFIG_FILE), exist_ok=True)

    with open(_CONFIG_FILE, "w", encoding="utf-8") as f:
        f.write(noi_dung_moi)

    print(f"  ✓ Đã ghi config mới: {_CONFIG_FILE}")

    # 8. Hướng dẫn tiếp theo
    print()
    print("╔══════════════════════════════════════════════════════╗")
    print("║  HOÀN TẤT! Các bước tiếp theo:                     ║")
    print("╠══════════════════════════════════════════════════════╣")
    print("║                                                      ║")
    print("║  1. Cập nhật danh sách khách hàng:                  ║")
    print("║     zalo-tool/data/contacts.csv                     ║")
    print("║                                                      ║")
    print("║  2. Cập nhật mẫu bài đăng Zalo:                    ║")
    print("║     mau-bai-dang-zalo.txt                           ║")
    print("║                                                      ║")
    print("║  3. Khởi động runner để chạy lịch tự động:         ║")
    print("║     python routines/runner.py                       ║")
    print("║                                                      ║")
    print("║  4. Hoặc chạy thủ công từng routine:               ║")
    print("║     python routines/routine_sang.py                 ║")
    print("║     python routines/routine_toi.py                  ║")
    print("║     python routines/routine_dang_bai.py             ║")
    print("║     python routines/routine_dashboard.py            ║")
    print("║                                                      ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()


if __name__ == "__main__":
    main()
