import time
import subprocess

import pyautogui
import pyperclip
import pywinauto
from pywinauto import Application


# Tắt failsafe của pyautogui (di chuột góc trái trên vẫn dừng được)
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.3


class ZaloController:
    """Điều khiển Zalo PC thông qua UI automation."""

    ZALO_EXE = "Zalo.exe"
    WINDOW_TITLE_KEYWORD = "Zalo"

    def __init__(self):
        self.app = None
        self.main_window = None

    # ── Kiểm tra & kết nối ──────────────────────────────────────────

    def is_zalo_running(self):
        """Kiểm tra Zalo PC đang chạy hay chưa."""
        try:
            result = subprocess.run(
                ["tasklist", "/FI", f"IMAGENAME eq {self.ZALO_EXE}"],
                capture_output=True, text=True
            )
            return self.ZALO_EXE.lower() in result.stdout.lower()
        except Exception:
            return False

    def connect(self):
        """Kết nối tới cửa sổ Zalo đang chạy."""
        if not self.is_zalo_running():
            raise RuntimeError(
                "Zalo PC chưa được mở. Vui lòng mở Zalo và đăng nhập trước khi chạy tool."
            )

        try:
            self.app = Application(backend="uia").connect(
                path=self.ZALO_EXE, timeout=10
            )
            # Tìm cửa sổ chính của Zalo
            self.main_window = self.app.window(title_re=".*Zalo.*")
            return True
        except Exception as e:
            raise RuntimeError(f"Không thể kết nối tới Zalo PC: {e}")

    def bring_to_front(self):
        """Đưa cửa sổ Zalo lên trước."""
        try:
            if self.main_window:
                self.main_window.set_focus()
                time.sleep(0.5)
        except Exception:
            # Fallback: dùng pyautogui
            pyautogui.hotkey("alt", "tab")
            time.sleep(0.5)

    # ── Thao tác tìm kiếm ──────────────────────────────────────────

    def click_search_box(self):
        """Click vào ô tìm kiếm của Zalo."""
        self.bring_to_front()
        time.sleep(0.3)
        # Ctrl+F hoặc Ctrl+E để focus vào ô tìm kiếm trong Zalo
        pyautogui.hotkey("ctrl", "f")
        time.sleep(0.5)

    def search_contact(self, phone_number):
        """Tìm kiếm liên hệ theo SĐT.

        Returns:
            True nếu tìm thấy và mở được hội thoại, False nếu không.
        """
        try:
            self.click_search_box()
            time.sleep(0.3)

            # Xóa nội dung cũ trong ô tìm kiếm
            pyautogui.hotkey("ctrl", "a")
            time.sleep(0.1)

            # Nhập SĐT qua clipboard
            self._type_text(phone_number)
            time.sleep(1.5)  # Chờ kết quả tìm kiếm

            # Nhấn Enter để chọn kết quả đầu tiên
            pyautogui.press("enter")
            time.sleep(1.0)

            return True
        except Exception:
            return False

    # ── Gửi tin nhắn ────────────────────────────────────────────────

    def send_message(self, text):
        """Gửi tin nhắn text trong hội thoại hiện tại."""
        try:
            # Click vào ô nhập tin nhắn (phía dưới cửa sổ chat)
            self._click_message_box()
            time.sleep(0.3)

            # Nhập nội dung qua clipboard
            self._type_text(text)
            time.sleep(0.3)

            # Nhấn Enter để gửi
            pyautogui.press("enter")
            time.sleep(0.5)

            return True
        except Exception as e:
            raise RuntimeError(f"Lỗi gửi tin nhắn: {e}")

    def send_image(self, image_path):
        """Gửi ảnh trong hội thoại hiện tại."""
        import os
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Không tìm thấy ảnh: {image_path}")

        try:
            self._click_message_box()
            time.sleep(0.3)

            # Dùng Ctrl+V để paste file ảnh
            # Copy file vào clipboard bằng PowerShell
            abs_path = os.path.abspath(image_path).replace("/", "\\")
            ps_cmd = (
                f'powershell -command "'
                f"Add-Type -AssemblyName System.Windows.Forms; "
                f"$files = New-Object System.Collections.Specialized.StringCollection; "
                f"$files.Add('{abs_path}'); "
                f'[System.Windows.Forms.Clipboard]::SetFileDropList($files)"'
            )
            subprocess.run(ps_cmd, shell=True, check=True)
            time.sleep(0.5)

            # Paste ảnh vào Zalo
            pyautogui.hotkey("ctrl", "v")
            time.sleep(1.0)

            # Enter để gửi
            pyautogui.press("enter")
            time.sleep(1.0)

            return True
        except Exception as e:
            raise RuntimeError(f"Lỗi gửi ảnh: {e}")

    def send_multiple_images(self, image_paths):
        """Gửi nhiều ảnh cùng lúc."""
        import os
        for p in image_paths:
            if not os.path.exists(p):
                raise FileNotFoundError(f"Không tìm thấy ảnh: {p}")

        try:
            self._click_message_box()
            time.sleep(0.3)

            # Copy nhiều file vào clipboard
            paths_escaped = [os.path.abspath(p).replace("/", "\\") for p in image_paths]
            add_lines = "; ".join([f"$files.Add('{p}')" for p in paths_escaped])
            ps_cmd = (
                f'powershell -command "'
                f"Add-Type -AssemblyName System.Windows.Forms; "
                f"$files = New-Object System.Collections.Specialized.StringCollection; "
                f"{add_lines}; "
                f'[System.Windows.Forms.Clipboard]::SetFileDropList($files)"'
            )
            subprocess.run(ps_cmd, shell=True, check=True)
            time.sleep(0.5)

            pyautogui.hotkey("ctrl", "v")
            time.sleep(1.5)

            pyautogui.press("enter")
            time.sleep(1.0)

            return True
        except Exception as e:
            raise RuntimeError(f"Lỗi gửi ảnh: {e}")

    # ── Đăng nhật ký (Timeline) ─────────────────────────────────────

    def open_timeline(self):
        """Mở trang Nhật ký (Timeline) của Zalo."""
        try:
            self.bring_to_front()
            time.sleep(0.5)

            # Click vào icon Nhật ký ở thanh sidebar trái
            # Vị trí tương đối — có thể cần điều chỉnh theo phiên bản Zalo
            # Dùng phím tắt nếu có, hoặc tìm bằng hình ảnh
            # Cách phổ biến: click vào icon đồng hồ/timeline ở sidebar
            if self.main_window:
                window_rect = self.main_window.rectangle()
                # Icon nhật ký thường ở sidebar trái, khoảng vị trí thứ 3-4 từ trên
                timeline_x = window_rect.left + 35
                timeline_y = window_rect.top + 250
                pyautogui.click(timeline_x, timeline_y)
                time.sleep(1.0)

            return True
        except Exception as e:
            raise RuntimeError(f"Lỗi mở Nhật ký: {e}")

    def create_post(self, text, image_paths=None):
        """Tạo bài đăng nhật ký."""
        try:
            self.open_timeline()
            time.sleep(0.5)

            # Click nút "Đăng gì đó..." hoặc "What's on your mind"
            # Thường ở phía trên cùng của timeline
            if self.main_window:
                window_rect = self.main_window.rectangle()
                post_x = window_rect.left + (window_rect.width() // 2)
                post_y = window_rect.top + 180
                pyautogui.click(post_x, post_y)
                time.sleep(1.0)

            # Nhập nội dung bài đăng
            self._type_text(text)
            time.sleep(0.5)

            # Đính kèm ảnh nếu có
            if image_paths:
                for img_path in image_paths:
                    self._attach_image_to_post(img_path)
                    time.sleep(0.5)

            # Click nút Đăng
            time.sleep(0.5)
            pyautogui.hotkey("ctrl", "enter")
            time.sleep(2.0)

            return True
        except Exception as e:
            raise RuntimeError(f"Lỗi đăng bài: {e}")

    def _attach_image_to_post(self, image_path):
        """Đính kèm ảnh vào bài đăng nhật ký."""
        import os
        abs_path = os.path.abspath(image_path).replace("/", "\\")
        ps_cmd = (
            f'powershell -command "'
            f"Add-Type -AssemblyName System.Windows.Forms; "
            f"$files = New-Object System.Collections.Specialized.StringCollection; "
            f"$files.Add('{abs_path}'); "
            f'[System.Windows.Forms.Clipboard]::SetFileDropList($files)"'
        )
        subprocess.run(ps_cmd, shell=True, check=True)
        time.sleep(0.3)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(1.0)

    # ── Kết bạn ─────────────────────────────────────────────────────

    def send_friend_request(self, phone_number, greeting_message=""):
        """Gửi lời mời kết bạn theo SĐT.

        Returns:
            'sent' | 'already_friend' | 'not_found' | 'error'
        """
        try:
            # Tìm kiếm SĐT
            self.click_search_box()
            time.sleep(0.3)
            pyautogui.hotkey("ctrl", "a")
            time.sleep(0.1)
            self._type_text(phone_number)
            time.sleep(2.0)

            # Nhấn Enter để mở profile
            pyautogui.press("enter")
            time.sleep(1.5)

            # Tìm và click nút "Kết bạn" / "Add friend"
            # Nếu đã là bạn, sẽ không có nút này
            # Cần kiểm tra bằng hình ảnh hoặc tọa độ
            # Giả sử nút Kết bạn xuất hiện trong hội thoại
            # Đây là phần cần điều chỉnh theo giao diện Zalo cụ thể

            if greeting_message:
                # Nhập lời chào trước khi gửi kết bạn
                time.sleep(0.5)
                self._type_text(greeting_message)
                time.sleep(0.3)

            # Click nút gửi kết bạn
            pyautogui.press("enter")
            time.sleep(1.0)

            return "sent"
        except Exception:
            return "error"

    # ── Helper methods ──────────────────────────────────────────────

    def _type_text(self, text):
        """Nhập text qua clipboard để hỗ trợ tiếng Việt."""
        pyperclip.copy(text)
        time.sleep(0.1)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.2)

    def _click_message_box(self):
        """Click vào ô nhập tin nhắn trong hội thoại."""
        if self.main_window:
            window_rect = self.main_window.rectangle()
            # Ô nhập tin nhắn thường ở phía dưới, giữa cửa sổ
            msg_x = window_rect.left + (window_rect.width() * 2 // 3)
            msg_y = window_rect.bottom - 60
            pyautogui.click(msg_x, msg_y)
            time.sleep(0.3)
        else:
            # Fallback: click vào vùng dưới cùng
            screen_w, screen_h = pyautogui.size()
            pyautogui.click(screen_w // 2, screen_h - 100)
            time.sleep(0.3)

    def close_current_chat(self):
        """Đóng/quay lại từ hội thoại hiện tại."""
        pyautogui.press("escape")
        time.sleep(0.5)
