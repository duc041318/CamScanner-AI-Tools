import random
import threading
import time

from utils.file_reader import read_phone_list, apply_template
from utils.logger import Logger
from utils.zalo_controller import ZaloController


class BulkMessageSender:
    """Tính năng 1: Nhắn tin hàng loạt từ danh sách SĐT."""

    def __init__(self):
        self.controller = ZaloController()
        self.logger = Logger()
        self.stop_event = threading.Event()
        self.is_running = False

    def start(self, file_path, message_template, image_path=None,
              delay_min=10, delay_max=30, progress_callback=None, status_callback=None):
        """Bắt đầu gửi tin nhắn hàng loạt trong thread riêng."""
        self.stop_event.clear()
        self.is_running = True

        thread = threading.Thread(
            target=self._run,
            args=(file_path, message_template, image_path,
                  delay_min, delay_max, progress_callback, status_callback),
            daemon=True
        )
        thread.start()
        return thread

    def stop(self):
        """Dừng khẩn cấp."""
        self.stop_event.set()
        self.is_running = False

    def _run(self, file_path, message_template, image_path,
             delay_min, delay_max, progress_callback, status_callback):
        try:
            # Kết nối Zalo
            self._update_status(status_callback, "Đang kết nối Zalo PC...")
            self.controller.connect()

            # Đọc danh sách
            self._update_status(status_callback, "Đang đọc danh sách SĐT...")
            contacts = read_phone_list(file_path)
            total = len(contacts)

            if total == 0:
                self._update_status(status_callback, "Danh sách trống!")
                self.is_running = False
                return

            self._update_status(status_callback, f"Tìm thấy {total} số. Bắt đầu gửi...")

            success_count = 0
            fail_count = 0

            for i, contact in enumerate(contacts):
                if self.stop_event.is_set():
                    self._update_status(status_callback, "Đã dừng bởi người dùng.")
                    break

                phone = contact.get("sdt", "")
                self._update_status(
                    status_callback,
                    f"[{i+1}/{total}] Đang gửi tới {phone}..."
                )

                result = self._send_to_contact(contact, message_template, image_path)

                # Log kết quả
                self.logger.log("bulk_message", {
                    "sdt": phone,
                    "ho_ten": contact.get("ho_ten", ""),
                    "trang_thai": result,
                })

                if result == "Thành công":
                    success_count += 1
                else:
                    fail_count += 1

                # Cập nhật progress
                if progress_callback:
                    progress_callback(i + 1, total)

                # Delay ngẫu nhiên (trừ tin cuối cùng)
                if i < total - 1 and not self.stop_event.is_set():
                    delay = random.uniform(delay_min, delay_max)
                    self._update_status(
                        status_callback,
                        f"Chờ {delay:.0f}s trước tin tiếp theo..."
                    )
                    # Chia nhỏ delay để có thể dừng nhanh
                    self._interruptible_sleep(delay)

            self._update_status(
                status_callback,
                f"Hoàn tất! Thành công: {success_count}, Lỗi: {fail_count}"
            )

        except Exception as e:
            self._update_status(status_callback, f"Lỗi: {e}")
        finally:
            self.is_running = False

    def _send_to_contact(self, contact, message_template, image_path):
        """Gửi tin nhắn tới một liên hệ."""
        phone = contact.get("sdt", "")
        try:
            # Tìm kiếm SĐT
            found = self.controller.search_contact(phone)
            if not found:
                return "Không tìm thấy"

            # Thay thế biến trong template
            message = apply_template(message_template, contact)

            # Gửi tin nhắn text
            self.controller.send_message(message)

            # Gửi ảnh nếu có
            if image_path:
                time.sleep(0.5)
                self.controller.send_image(image_path)

            # Đóng hội thoại
            time.sleep(0.5)
            self.controller.close_current_chat()

            return "Thành công"

        except Exception as e:
            return f"Lỗi: {e}"

    def _interruptible_sleep(self, seconds):
        """Sleep có thể bị ngắt bởi stop_event."""
        end_time = time.time() + seconds
        while time.time() < end_time:
            if self.stop_event.is_set():
                return
            time.sleep(0.5)

    def _update_status(self, callback, message):
        if callback:
            callback(message)
