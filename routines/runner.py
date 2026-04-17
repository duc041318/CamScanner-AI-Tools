"""
RUNNER - Bộ lên lịch tự động cho tất cả Routines BĐS Sóc Sơn
─────────────────────────────────────────────────────────────
Chạy file này 1 lần duy nhất, để chạy nền cả ngày:

    cd CamScanner-AI-Tools
    python routines/runner.py

Lịch tự động:
    07:00  → Gửi Zalo hàng loạt buổi sáng
    12:00  → Đăng bài Feed Zalo
    19:30  → Follow-up khách buổi tối
    21:00  → Tổng hợp báo cáo ngày + Dashboard HTML
    Thứ 2  → Làm mới nội dung tuần

Phím tắt khi đang chạy:
    Ctrl+C → Dừng an toàn
"""

import sys
import os
import time
import threading
from datetime import datetime

# Thêm path zalo-tool
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "zalo-tool"))

import schedule

# Import các routine
from routine_sang import chay as chay_sang
from routine_toi import chay as chay_toi
from routine_bao_cao import chay as chay_bao_cao
from routine_noi_dung import chay as chay_noi_dung
from routine_dang_bai import chay as chay_dang_bai
from routine_dashboard import chay as chay_dashboard

from config import LICH_SANG, LICH_TOI, LICH_BAO_CAO, LICH_DANG_BAI, LICH_NOI_DUNG

try:
    from features.auto_reply import AutoReplyMonitor
    _AUTO_REPLY_OK = True
except ImportError:
    _AUTO_REPLY_OK = False


# ── Màu sắc terminal ──────────────────────────────────────────────────────────
class Color:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


def _banner():
    print(f"""
{Color.BOLD}{Color.BLUE}
╔══════════════════════════════════════════════════════════════╗
║       ZALO ROUTINE RUNNER - BĐS PHÚ TẰNG SÓC SƠN           ║
╠══════════════════════════════════════════════════════════════╣
║  Lịch chạy:                                                 ║
║   {LICH_SANG}   → Gửi Zalo hàng loạt buổi sáng              ║
║   {LICH_DANG_BAI}  → Đăng bài Feed Zalo                     ║
║   {LICH_TOI}  → Follow-up khách buổi tối                  ║
║   {LICH_BAO_CAO}  → Báo cáo ngày + Dashboard HTML           ║
║   Thứ 2 {LICH_NOI_DUNG} → Làm mới nội dung tuần              ║
╠══════════════════════════════════════════════════════════════╣
║  Nhấn Ctrl+C để dừng an toàn                                ║
╚══════════════════════════════════════════════════════════════╝
{Color.RESET}""")


def _log(loai, msg):
    """In log có màu ra console."""
    mau = {
        "INFO": Color.BLUE,
        "OK": Color.GREEN,
        "WARN": Color.YELLOW,
        "ERR": Color.RED,
    }.get(loai, Color.RESET)
    now = datetime.now().strftime("%H:%M:%S")
    print(f"{mau}[{now}] [{loai}] {msg}{Color.RESET}")


def _chay_an_toan(ten_routine, ham_chay):
    """Wrapper bắt exception cho mỗi routine."""
    def _wrapper():
        _log("INFO", f"Bắt đầu routine: {ten_routine}")
        try:
            ok = ham_chay()
            if ok:
                _log("OK", f"Hoàn tất: {ten_routine}")
            else:
                _log("WARN", f"Routine kết thúc sớm: {ten_routine}")
        except Exception as e:
            _log("ERR", f"Lỗi trong routine {ten_routine}: {e}")

    return _wrapper


def _chay_trong_thread(ten_routine, ham_chay):
    """Chạy routine trong thread riêng để không block lịch."""
    t = threading.Thread(
        target=_chay_an_toan(ten_routine, ham_chay),
        daemon=True
    )
    t.start()


# ── Hàm wrapper có tên rõ ràng cho từng routine ───────────────────────────────
def _job_sang():
    _chay_trong_thread("Gửi Zalo Buổi Sáng", chay_sang)

def _job_toi():
    _chay_trong_thread("Follow-up Buổi Tối", chay_toi)

def _job_bao_cao():
    _chay_trong_thread("Báo Cáo Ngày", chay_bao_cao)

def _job_noi_dung():
    _chay_trong_thread("Làm Mới Nội Dung", chay_noi_dung)

def _job_dang_bai():
    _chay_trong_thread("Đăng Bài Feed Zalo", chay_dang_bai)

def _job_dashboard():
    _chay_trong_thread("Dashboard HTML", chay_dashboard)


# ── Đăng ký lịch ──────────────────────────────────────────────────────────────
def _dang_ky_lich():
    schedule.every().day.at(LICH_SANG).do(_job_sang)
    schedule.every().day.at(LICH_DANG_BAI).do(_job_dang_bai)
    schedule.every().day.at(LICH_TOI).do(_job_toi)
    schedule.every().day.at(LICH_BAO_CAO).do(_job_bao_cao)
    schedule.every().monday.at(LICH_NOI_DUNG).do(_job_noi_dung)
    _log("OK", "Đã đăng ký 5 routine thành công.")


def _hien_thi_lich_tiep_theo():
    """Hiển thị lần chạy tiếp theo của từng job."""
    print(f"\n{Color.BOLD}Lần chạy tiếp theo:{Color.RESET}")
    for job in schedule.get_jobs():
        next_run = job.next_run
        if next_run:
            ten = getattr(job.job_func, "__name__", "routine").replace("_job_", "")
            ten_hien = {"sang": f"Gửi Zalo Sáng ({LICH_SANG})", "toi": f"Follow-up Tối ({LICH_TOI})",
                        "bao_cao": f"Báo Cáo ({LICH_BAO_CAO})", "noi_dung": f"Làm Mới Nội Dung (Thứ 2 {LICH_NOI_DUNG})",
                        "dang_bai": f"Đăng Bài Feed ({LICH_DANG_BAI})", "dashboard": "Dashboard HTML"}.get(ten, ten)
            print(f"  • {next_run.strftime('%d/%m/%Y %H:%M')}  →  {ten_hien}")


# ── Lệnh thủ công (chạy ngay không cần chờ lịch) ─────────────────────────────
def _xu_ly_lenh(lenh):
    lenh = lenh.strip().lower()
    if lenh == "sang":
        _chay_trong_thread("Routine Sáng (thủ công)", chay_sang)
    elif lenh == "toi":
        _chay_trong_thread("Routine Tối (thủ công)", chay_toi)
    elif lenh == "bc":
        _chay_trong_thread("Báo Cáo (thủ công)", chay_bao_cao)
    elif lenh == "nd":
        _chay_trong_thread("Nội Dung (thủ công)", chay_noi_dung)
    elif lenh == "dang":
        _chay_trong_thread("Đăng Bài Feed (thủ công)", chay_dang_bai)
    elif lenh == "dashboard":
        _chay_trong_thread("Dashboard (thủ công)", chay_dashboard)
    elif lenh.startswith("reply "):
        sdt = lenh.split(" ", 1)[1].strip()
        if _AUTO_REPLY_OK and _monitor:
            t = threading.Thread(target=_monitor.reply_to, args=(sdt,), daemon=True)
            t.start()
        else:
            _log("WARN", "Auto-reply không khả dụng (pywinauto chưa cài hoặc không chạy Windows).")
    elif lenh == "lich":
        _hien_thi_lich_tiep_theo()
    elif lenh == "help":
        print(f"""
{Color.BOLD}Lệnh thủ công:{Color.RESET}
  sang        → Chạy ngay Routine Sáng (gửi Zalo)
  toi         → Chạy ngay Routine Tối (follow-up)
  bc          → Chạy ngay Báo Cáo + Dashboard
  nd          → Chạy ngay Làm Mới Nội Dung
  dang        → Chạy ngay Đăng Bài Feed Zalo
  dashboard   → Tạo ngay Dashboard HTML
  reply <SĐT> → Gửi reply tự động đến số điện thoại
  lich        → Xem lịch chạy tiếp theo
  help        → Hiển thị trợ giúp này
  q           → Thoát
""")
    elif lenh in ("q", "quit", "exit"):
        _log("INFO", "Đang dừng Runner...")
        sys.exit(0)
    elif lenh:
        _log("WARN", f"Lệnh không hợp lệ: '{lenh}'. Gõ 'help' để xem hướng dẫn.")


_monitor = None  # AutoReplyMonitor instance, set in main()


def _vong_lap_nhap_lenh():
    """Vòng lặp nhận lệnh từ bàn phím trong thread riêng."""
    while True:
        try:
            lenh = input()
            _xu_ly_lenh(lenh)
        except (EOFError, KeyboardInterrupt):
            break


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    global _monitor
    _banner()
    _dang_ky_lich()
    _hien_thi_lich_tiep_theo()

    # Khởi động auto-reply monitor (chỉ chạy được trên Windows với pywinauto)
    if _AUTO_REPLY_OK:
        _monitor = AutoReplyMonitor()
        _monitor.start()
    else:
        _log("INFO", "Auto-reply monitor không khả dụng (cần pywinauto + Windows).")

    print(f"\n{Color.GREEN}Runner đang chạy... Gõ 'help' để xem lệnh thủ công.{Color.RESET}\n")

    # Thread nhận lệnh bàn phím
    lenh_thread = threading.Thread(target=_vong_lap_nhap_lenh, daemon=True)
    lenh_thread.start()

    # Vòng lặp chính kiểm tra lịch
    try:
        while True:
            schedule.run_pending()
            time.sleep(30)  # Kiểm tra mỗi 30 giây
    except KeyboardInterrupt:
        if _monitor:
            _monitor.stop()
        _log("INFO", "Đã dừng Runner (Ctrl+C). Tạm biệt!")


if __name__ == "__main__":
    main()
