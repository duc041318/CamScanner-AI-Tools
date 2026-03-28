import json
import os
import random
import threading
import time
from datetime import datetime

from utils.file_reader import read_phone_list, apply_template
from utils.logger import Logger
from utils.zalo_controller import ZaloController


class FriendAdder:
    """Tính năng 3: Kết bạn tự động theo danh sách SĐT."""

    DAILY_LIMIT_FILE = "data/daily_friend_count.json"

    def __init__(self, daily_limit=20):
        self.controller = ZaloController()
        self.logger = Logger()
        self.stop_event = threading.Event()
        self.is_running = False
        self.daily_limit = daily_limit

    def start(self, file_path, greeting_template="",
              delay_min=15, delay_max=45,
              progress_callback=None, status_callback=None):
        """Bắt đầu gửi lời mời kết bạn."""
        self.stop_event.clear()
        self.is_running = True

        thread = threading.Thread(
            target=self._run,
            args=(file_path, greeting_template, delay_min, delay_max,
                  progress_callback, status_callback),
            daemon=True
        )
        thread.start()
        return thread

    def stop(self):
        """Dừng khẩn cấp."""
        self.stop_event.set()
        self.is_running = False

    def _run(self, file_path, greeting_template, delay_min, delay_max,
             progress_callback, status_callback):
        try:
            self._update_status(status_callback, "Đang kết nối Zalo PC...")
            self.controller.connect()

            # Kiểm tra giới hạn ngày
            sent_today = self._get_daily_count()
            remaining = self.daily_limit - sent_today
            if remaining <= 0:
                self._update_status(
                    status_callback,
                    f"Đã đạt giới hạn {self.daily_limit} lời mời/ngày. Thử lại ngày mai."
                )
                self.is_running = False
                return

            # Đọc danh sách
            self._update_status(status_callback, "Đang đọc danh sách SĐT...")
            contacts = read_phone_list(file_path)
            total = len(contacts)

            if total == 0:
                self._update_status(status_callback, "Danh sách trống!")
                self.is_running = False
                return

            # Giới hạn số lượng theo quota còn lại
            actual_total = min(total, remaining)
            self._update_status(
                status_callback,
                f"Sẽ gửi {actual_total}/{total} lời mời (còn {remaining} quota hôm nay)"
            )

            success_count = 0
            fail_count = 0

            for i, contact in enumerate(contacts[:actual_total]):
                if self.stop_event.is_set():
                    self._update_status(status_callback, "Đã dừng bởi người dùng.")
                    break

                phone = contact.get("sdt", "")
                self._update_status(
                    status_callback,
                    f"[{i+1}/{actual_total}] Đang gửi kết bạn tới {phone}..."
                )

                # Tạo lời chào từ template
                greeting = apply_template(greeting_template, contact) if greeting_template else ""

                result = self._send_request(phone, greeting)

                self.logger.log("add_friend", {
                    "sdt": phone,
                    "ho_ten": contact.get("ho_ten", ""),
                    "trang_thai": result,
                })

                if result == "sent":
                    success_count += 1
                    self._increment_daily_count()
                else:
                    fail_count += 1

                if progress_callback:
                    progress_callback(i + 1, actual_total)

                # Delay ngẫu nhiên
                if i < actual_total - 1 and not self.stop_event.is_set():
                    delay = random.uniform(delay_min, delay_max)
                    self._update_status(
                        status_callback,
                        f"Chờ {delay:.0f}s trước lời mời tiếp..."
                    )
                    self._interruptible_sleep(delay)

            self._update_status(
                status_callback,
                f"Hoàn tất! Đã gửi: {success_count}, Lỗi: {fail_count}"
            )

        except Exception as e:
            self._update_status(status_callback, f"Lỗi: {e}")
        finally:
            self.is_running = False

    def _send_request(self, phone, greeting):
        """Gửi lời mời kết bạn tới một SĐT."""
        try:
            result = self.controller.send_friend_request(phone, greeting)
            self.controller.close_current_chat()
            return result
        except Exception as e:
            return f"error: {e}"

    def _get_daily_count(self):
        """Lấy số lời mời đã gửi hôm nay."""
        today = datetime.now().strftime("%Y-%m-%d")
        try:
            if os.path.exists(self.DAILY_LIMIT_FILE):
                with open(self.DAILY_LIMIT_FILE, "r") as f:
                    data = json.load(f)
                    return data.get(today, 0)
        except Exception:
            pass
        return 0

    def _increment_daily_count(self):
        """Tăng bộ đếm lời mời hôm nay."""
        today = datetime.now().strftime("%Y-%m-%d")
        data = {}
        try:
            if os.path.exists(self.DAILY_LIMIT_FILE):
                with open(self.DAILY_LIMIT_FILE, "r") as f:
                    data = json.load(f)
        except Exception:
            pass

        data[today] = data.get(today, 0) + 1

        # Xóa dữ liệu cũ hơn 7 ngày
        keys_to_remove = [k for k in data if k < today and k != today]
        for k in keys_to_remove[:max(0, len(keys_to_remove) - 7)]:
            del data[k]

        try:
            os.makedirs(os.path.dirname(self.DAILY_LIMIT_FILE), exist_ok=True)
            with open(self.DAILY_LIMIT_FILE, "w") as f:
                json.dump(data, f)
        except Exception:
            pass

    def _interruptible_sleep(self, seconds):
        end_time = time.time() + seconds
        while time.time() < end_time:
            if self.stop_event.is_set():
                return
            time.sleep(0.5)

    def _update_status(self, callback, message):
        if callback:
            callback(message)
