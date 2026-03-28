import random
import threading
import time
from datetime import datetime

import schedule

from utils.logger import Logger
from utils.zalo_controller import ZaloController


class ScheduledPost:
    """Đại diện một bài đăng đã lên lịch."""

    def __init__(self, text, image_paths=None, scheduled_time=None):
        self.text = text
        self.image_paths = image_paths or []
        self.scheduled_time = scheduled_time  # datetime object
        self.status = "Đang chờ"  # Đang chờ / Đã đăng / Lỗi


class AutoPoster:
    """Tính năng 2: Đăng bài tự động lên nhật ký Zalo."""

    def __init__(self):
        self.controller = ZaloController()
        self.logger = Logger()
        self.stop_event = threading.Event()
        self.is_running = False
        self.scheduled_posts = []
        self._scheduler_thread = None

    def add_post(self, text, image_paths=None, scheduled_time=None):
        """Thêm bài đăng vào lịch trình."""
        post = ScheduledPost(text, image_paths, scheduled_time)
        self.scheduled_posts.append(post)
        return post

    def remove_post(self, index):
        """Xóa bài đăng khỏi lịch trình."""
        if 0 <= index < len(self.scheduled_posts):
            self.scheduled_posts.pop(index)

    def clear_posts(self):
        """Xóa toàn bộ lịch trình."""
        self.scheduled_posts.clear()

    def start_scheduler(self, status_callback=None):
        """Bắt đầu chạy scheduler kiểm tra lịch đăng bài."""
        self.stop_event.clear()
        self.is_running = True

        self._scheduler_thread = threading.Thread(
            target=self._run_scheduler,
            args=(status_callback,),
            daemon=True
        )
        self._scheduler_thread.start()

    def stop(self):
        """Dừng scheduler."""
        self.stop_event.set()
        self.is_running = False

    def post_now(self, text, image_paths=None, status_callback=None):
        """Đăng bài ngay lập tức trong thread riêng."""
        self.stop_event.clear()
        self.is_running = True

        thread = threading.Thread(
            target=self._execute_post,
            args=(text, image_paths, status_callback),
            daemon=True
        )
        thread.start()
        return thread

    def _run_scheduler(self, status_callback):
        """Vòng lặp kiểm tra và đăng bài theo lịch."""
        try:
            self._update_status(status_callback, "Đang kết nối Zalo PC...")
            self.controller.connect()
            self._update_status(status_callback, "Scheduler đang chạy. Chờ đến giờ đăng bài...")

            while not self.stop_event.is_set():
                now = datetime.now()

                for post in self.scheduled_posts:
                    if self.stop_event.is_set():
                        break

                    if post.status != "Đang chờ":
                        continue

                    if post.scheduled_time and now >= post.scheduled_time:
                        self._update_status(
                            status_callback,
                            f"Đang đăng bài lên lịch lúc {post.scheduled_time.strftime('%H:%M')}..."
                        )

                        try:
                            self.controller.create_post(post.text, post.image_paths)
                            post.status = "Đã đăng"

                            self.logger.log("auto_post", {
                                "noi_dung": post.text[:50] + "...",
                                "so_anh": len(post.image_paths),
                                "gio_hen": post.scheduled_time.strftime("%H:%M"),
                                "trang_thai": "Đã đăng",
                            })

                            self._update_status(
                                status_callback,
                                f"Đã đăng bài lúc {now.strftime('%H:%M:%S')}"
                            )

                        except Exception as e:
                            post.status = f"Lỗi: {e}"
                            self.logger.log("auto_post", {
                                "noi_dung": post.text[:50] + "...",
                                "so_anh": len(post.image_paths),
                                "gio_hen": post.scheduled_time.strftime("%H:%M"),
                                "trang_thai": f"Lỗi: {e}",
                            })

                        # Delay sau mỗi bài
                        time.sleep(random.uniform(3, 8))

                # Kiểm tra mỗi 10 giây
                for _ in range(20):
                    if self.stop_event.is_set():
                        break
                    time.sleep(0.5)

            self._update_status(status_callback, "Scheduler đã dừng.")

        except Exception as e:
            self._update_status(status_callback, f"Lỗi scheduler: {e}")
        finally:
            self.is_running = False

    def _execute_post(self, text, image_paths, status_callback):
        """Thực thi đăng bài ngay."""
        try:
            self._update_status(status_callback, "Đang kết nối Zalo PC...")
            self.controller.connect()

            self._update_status(status_callback, "Đang đăng bài...")
            self.controller.create_post(text, image_paths)

            self.logger.log("auto_post", {
                "noi_dung": text[:50] + "...",
                "so_anh": len(image_paths) if image_paths else 0,
                "gio_hen": "Ngay",
                "trang_thai": "Đã đăng",
            })

            self._update_status(status_callback, "Đã đăng bài thành công!")

        except Exception as e:
            self.logger.log("auto_post", {
                "noi_dung": text[:50] + "...",
                "so_anh": len(image_paths) if image_paths else 0,
                "gio_hen": "Ngay",
                "trang_thai": f"Lỗi: {e}",
            })
            self._update_status(status_callback, f"Lỗi: {e}")
        finally:
            self.is_running = False

    def _update_status(self, callback, message):
        if callback:
            callback(message)
