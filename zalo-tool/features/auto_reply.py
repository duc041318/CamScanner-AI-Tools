"""
AUTO-REPLY MONITOR - Giám sát tin nhắn Zalo mới
Chạy trong background thread, phát hiện khi Zalo có tin nhắn chưa đọc,
cảnh báo ra console và chuẩn bị nội dung reply.

Cách dùng trong runner.py:
    monitor = AutoReplyMonitor(on_alert=my_callback)
    monitor.start()
    ...
    monitor.stop()

Gửi reply thủ công:
    monitor.reply_to("0912345678", loai="thong_tin")
"""

import os
import sys
import threading
import time
from datetime import datetime

from utils.logger import Logger
from utils.zalo_controller import ZaloController

# ── Nội dung reply sẵn ────────────────────────────────────────────────────────

REPLY_THONG_TIN = """Dạ em cảm ơn anh/chị đã liên hệ! 🙏

Em đang có 2 lô đất tại Phú Tằng - Đa Phúc - Sóc Sơn:

🏡 LÔ 1 - 83m²
  • Kích thước: 8.12 x 10.41m (gần vuông)
  • Giá: 1.66 tỷ (20 triệu/m²)
  • Sổ đỏ: AA 01730140

🏡 LÔ 2 - 88.5m² (LÔ GÓC ⭐)
  • Kích thước: 15.93 x 5.56m - 2 mặt thoáng
  • Giá: 2.21 tỷ (25 triệu/m²)
  • Sổ đỏ: AA 02367049

✅ Điểm chung:
  • Đất thổ cư 100% - xây nhà không cần chuyển đổi
  • Đường bê tông 4-5m - xe ô tô vào tận nơi
  • Sổ đỏ chính chủ - sang tên ngay
  • Cách sân bay Nội Bài 15 phút

Anh/chị quan tâm lô nào ạ? Em sắp xếp đi xem thực tế bất kỳ lúc nào! 🚗"""

REPLY_HEN_XEM = """Dạ em sẽ sắp xếp đưa anh/chị đi xem đất ạ!

📍 Địa chỉ: Thôn Yên Tằng, Đa Phúc, Sóc Sơn, Hà Nội
🚗 Xe đưa đón miễn phí từ nội thành HN

Anh/chị có thể đi vào:
  • Buổi sáng (8h-11h)
  • Buổi chiều (14h-17h)
  • Cuối tuần bất kỳ

Anh/chị muốn đặt lịch ngày nào ạ? 😊"""


class AutoReplyMonitor:
    """Monitor Zalo PC trong background, phát hiện tin nhắn mới."""

    CHECK_INTERVAL = 45   # giây giữa mỗi lần kiểm tra

    def __init__(self, on_alert=None):
        """
        on_alert: callback(unread_count: int) khi phát hiện tin mới.
                  Nếu None, chỉ in ra console.
        """
        self._stop_event = threading.Event()
        self._thread = None
        self._on_alert = on_alert
        self._logger = Logger()
        self._prev_unread = 0

    # ── Kiểm tra Zalo ─────────────────────────────────────────────

    def _kiem_tra_zalo_co_tin_moi(self) -> int:
        """
        Trả về số tin nhắn chưa đọc bằng cách kiểm tra tiêu đề cửa sổ Zalo.
        Zalo thường hiển thị "(N)" trong tiêu đề khi có N tin chưa đọc.
        Trả về 0 nếu không phát hiện hoặc xảy ra lỗi.
        """
        try:
            import pywinauto.findwindows as fw
            # Tìm cửa sổ có title dạng "Zalo (3)" hoặc "Zalo - ... (5)"
            handles = fw.find_windows(title_re=r".*Zalo.*\(\d+\).*")
            if not handles:
                return 0
            # Lấy title của cửa sổ đầu tiên tìm thấy
            import re
            from pywinauto import Application
            app = Application(backend="uia").connect(handle=handles[0])
            win = app.window(handle=handles[0])
            title = win.window_text()
            m = re.search(r"\((\d+)\)", title)
            return int(m.group(1)) if m else 1
        except Exception:
            return 0

    # ── Vòng lặp giám sát ─────────────────────────────────────────

    def _run(self):
        while not self._stop_event.is_set():
            try:
                ctrl = ZaloController()
                if not ctrl.is_zalo_running():
                    self._stop_event.wait(self.CHECK_INTERVAL)
                    continue

                unread = self._kiem_tra_zalo_co_tin_moi()

                if unread > 0 and unread != self._prev_unread:
                    now = datetime.now().strftime("%H:%M:%S")
                    msg = (f"[{now}] 📩 Zalo có {unread} tin nhắn chưa đọc! "
                           f"Gõ lệnh 'reply <SĐT>' để gửi reply, hoặc mở Zalo PC để trả lời.")
                    print(f"\033[93m{msg}\033[0m")

                    self._logger.log("auto_reply_alert", {
                        "thoi_gian": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "so_tin_chua_doc": unread,
                        "trang_thai": "Phát hiện tin mới",
                    })

                    if self._on_alert:
                        self._on_alert(unread)

                self._prev_unread = unread

            except Exception:
                pass

            self._stop_event.wait(self.CHECK_INTERVAL)

    # ── Public API ────────────────────────────────────────────────

    def start(self):
        """Bắt đầu giám sát nền."""
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True,
                                        name="AutoReplyMonitor")
        self._thread.start()
        print(f"[AutoReply] Monitor bắt đầu (kiểm tra mỗi {self.CHECK_INTERVAL}s)")

    def stop(self):
        """Dừng giám sát."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
        print("[AutoReply] Monitor đã dừng.")

    def reply_to(self, sdt: str, loai: str = "thong_tin") -> bool:
        """
        Gửi reply đến SĐT cụ thể.
        loai: "thong_tin" (thông tin 2 lô đất) | "xem_dat" (hẹn lịch xem)
        """
        noi_dung = REPLY_THONG_TIN if loai == "thong_tin" else REPLY_HEN_XEM

        try:
            ctrl = ZaloController()
            ctrl.connect()

            found = ctrl.search_contact(sdt)
            if not found:
                print(f"[AutoReply] Không tìm thấy SĐT: {sdt}")
                return False

            ctrl.send_message(noi_dung)
            ctrl.close_current_chat()

            self._logger.log("auto_reply_gui", {
                "thoi_gian": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "sdt": sdt,
                "loai": loai,
                "trang_thai": "Đã gửi",
            })

            print(f"[AutoReply] Đã gửi reply '{loai}' đến {sdt}")
            return True

        except Exception as e:
            print(f"[AutoReply] Lỗi gửi reply đến {sdt}: {e}")
            return False


if __name__ == "__main__":
    import time as _time

    def _alert(n):
        print(f"  → Callback: phát hiện {n} tin chưa đọc!")

    monitor = AutoReplyMonitor(on_alert=_alert)
    monitor.start()
    print("Đang giám sát Zalo... Nhấn Ctrl+C để dừng.\n")
    try:
        while True:
            _time.sleep(1)
    except KeyboardInterrupt:
        monitor.stop()
