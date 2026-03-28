"""
Zalo Tool - Công cụ hỗ trợ môi giới BĐS đất nền Sóc Sơn
Tự động hóa Zalo PC: nhắn tin hàng loạt, đăng bài, kết bạn.
"""

import csv
import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from datetime import datetime

# Thêm thư mục gốc vào path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from features.bulk_message import BulkMessageSender
from features.auto_post import AutoPoster
from features.add_friend import FriendAdder
from utils.logger import Logger


class ZaloToolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Zalo Tool - BĐS Sóc Sơn")
        self.root.geometry("800x650")
        self.root.resizable(True, True)

        self.logger = Logger()
        self.bulk_sender = BulkMessageSender()
        self.auto_poster = AutoPoster()
        self.friend_adder = FriendAdder()

        self._build_ui()

    def _build_ui(self):
        # Notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tab 1: Nhắn tin hàng loạt
        self.tab_message = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_message, text="  Nhắn tin hàng loạt  ")
        self._build_tab_message()

        # Tab 2: Đăng bài tự động
        self.tab_post = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_post, text="  Đăng bài tự động  ")
        self._build_tab_post()

        # Tab 3: Kết bạn tự động
        self.tab_friend = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_friend, text="  Kết bạn tự động  ")
        self._build_tab_friend()

        # Tab 4: Xem log
        self.tab_log = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_log, text="  Xem Log  ")
        self._build_tab_log()

    # ══════════════════════════════════════════════════════════════
    # TAB 1: NHẮN TIN HÀNG LOẠT
    # ══════════════════════════════════════════════════════════════

    def _build_tab_message(self):
        frame = self.tab_message

        # ── File SĐT ──
        row_file = ttk.LabelFrame(frame, text="Danh sách SĐT", padding=5)
        row_file.pack(fill=tk.X, padx=10, pady=5)

        self.msg_file_path = tk.StringVar()
        ttk.Entry(row_file, textvariable=self.msg_file_path, width=60).pack(side=tk.LEFT, padx=5)
        ttk.Button(row_file, text="Chọn file...", command=self._browse_msg_file).pack(side=tk.LEFT)

        # ── Nội dung tin nhắn ──
        row_content = ttk.LabelFrame(frame, text="Nội dung tin nhắn (biến: {ho_ten}, {du_an}, {gia})", padding=5)
        row_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.msg_text = scrolledtext.ScrolledText(row_content, height=8, wrap=tk.WORD)
        self.msg_text.pack(fill=tk.BOTH, expand=True)
        self.msg_text.insert(tk.END,
            "Chào {ho_ten},\n\n"
            "Em là môi giới BĐS tại Sóc Sơn. "
            "Hiện em có lô đất tại {du_an}, giá chỉ từ {gia}. "
            "Anh/chị quan tâm em gửi thông tin chi tiết ạ!"
        )

        # ── Ảnh đính kèm ──
        row_img = ttk.LabelFrame(frame, text="Ảnh đính kèm (tùy chọn)", padding=5)
        row_img.pack(fill=tk.X, padx=10, pady=5)

        self.msg_image_path = tk.StringVar()
        ttk.Entry(row_img, textvariable=self.msg_image_path, width=60).pack(side=tk.LEFT, padx=5)
        ttk.Button(row_img, text="Chọn ảnh...", command=self._browse_msg_image).pack(side=tk.LEFT)

        # ── Cài đặt delay ──
        row_delay = ttk.Frame(frame)
        row_delay.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(row_delay, text="Delay (giây):").pack(side=tk.LEFT)
        self.msg_delay_min = tk.IntVar(value=10)
        self.msg_delay_max = tk.IntVar(value=30)
        ttk.Label(row_delay, text="Từ").pack(side=tk.LEFT, padx=(10, 2))
        ttk.Spinbox(row_delay, from_=5, to=120, width=5, textvariable=self.msg_delay_min).pack(side=tk.LEFT)
        ttk.Label(row_delay, text="đến").pack(side=tk.LEFT, padx=5)
        ttk.Spinbox(row_delay, from_=10, to=300, width=5, textvariable=self.msg_delay_max).pack(side=tk.LEFT)

        # ── Progress & Status ──
        self.msg_progress = ttk.Progressbar(frame, mode="determinate")
        self.msg_progress.pack(fill=tk.X, padx=10, pady=2)

        self.msg_status = tk.StringVar(value="Sẵn sàng")
        ttk.Label(frame, textvariable=self.msg_status, foreground="blue").pack(padx=10, anchor=tk.W)

        # ── Nút điều khiển ──
        row_btn = ttk.Frame(frame)
        row_btn.pack(fill=tk.X, padx=10, pady=5)

        self.btn_msg_start = ttk.Button(row_btn, text="▶ Bắt đầu gửi", command=self._start_bulk_message)
        self.btn_msg_start.pack(side=tk.LEFT, padx=5)

        self.btn_msg_stop = ttk.Button(row_btn, text="■ Dừng", command=self._stop_bulk_message, state=tk.DISABLED)
        self.btn_msg_stop.pack(side=tk.LEFT, padx=5)

    def _browse_msg_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("CSV/TXT", "*.csv *.txt"), ("All", "*.*")]
        )
        if path:
            self.msg_file_path.set(path)

    def _browse_msg_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.gif *.bmp"), ("All", "*.*")]
        )
        if path:
            self.msg_image_path.set(path)

    def _start_bulk_message(self):
        file_path = self.msg_file_path.get().strip()
        if not file_path:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn file danh sách SĐT.")
            return

        message = self.msg_text.get("1.0", tk.END).strip()
        if not message:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập nội dung tin nhắn.")
            return

        image = self.msg_image_path.get().strip() or None

        self.btn_msg_start.config(state=tk.DISABLED)
        self.btn_msg_stop.config(state=tk.NORMAL)
        self.msg_progress["value"] = 0

        self.bulk_sender.start(
            file_path=file_path,
            message_template=message,
            image_path=image,
            delay_min=self.msg_delay_min.get(),
            delay_max=self.msg_delay_max.get(),
            progress_callback=self._msg_progress_update,
            status_callback=self._msg_status_update,
        )

    def _stop_bulk_message(self):
        self.bulk_sender.stop()
        self.btn_msg_start.config(state=tk.NORMAL)
        self.btn_msg_stop.config(state=tk.DISABLED)

    def _msg_progress_update(self, current, total):
        self.root.after(0, lambda: self.msg_progress.config(
            maximum=total, value=current
        ))
        if current >= total:
            self.root.after(0, lambda: self.btn_msg_start.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.btn_msg_stop.config(state=tk.DISABLED))

    def _msg_status_update(self, message):
        self.root.after(0, lambda: self.msg_status.set(message))

    # ══════════════════════════════════════════════════════════════
    # TAB 2: ĐĂNG BÀI TỰ ĐỘNG
    # ══════════════════════════════════════════════════════════════

    def _build_tab_post(self):
        frame = self.tab_post

        # ── Nội dung bài đăng ──
        row_content = ttk.LabelFrame(frame, text="Nội dung bài đăng", padding=5)
        row_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.post_text = scrolledtext.ScrolledText(row_content, height=8, wrap=tk.WORD)
        self.post_text.pack(fill=tk.BOTH, expand=True)

        # ── Ảnh đính kèm ──
        row_img = ttk.LabelFrame(frame, text="Ảnh đính kèm (nhiều ảnh)", padding=5)
        row_img.pack(fill=tk.X, padx=10, pady=5)

        self.post_images = tk.StringVar()
        ttk.Entry(row_img, textvariable=self.post_images, width=55).pack(side=tk.LEFT, padx=5)
        ttk.Button(row_img, text="Chọn ảnh...", command=self._browse_post_images).pack(side=tk.LEFT)

        # ── Lên lịch ──
        row_schedule = ttk.LabelFrame(frame, text="Lên lịch đăng", padding=5)
        row_schedule.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(row_schedule, text="Giờ (HH:MM):").pack(side=tk.LEFT, padx=5)
        self.post_time = tk.StringVar(value="07:00")
        ttk.Entry(row_schedule, textvariable=self.post_time, width=8).pack(side=tk.LEFT)

        ttk.Button(row_schedule, text="+ Thêm vào lịch", command=self._add_scheduled_post).pack(side=tk.LEFT, padx=10)
        ttk.Button(row_schedule, text="Đăng ngay", command=self._post_now).pack(side=tk.LEFT, padx=5)

        # ── Danh sách lịch trình ──
        row_list = ttk.LabelFrame(frame, text="Lịch trình đăng bài hôm nay", padding=5)
        row_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        cols = ("stt", "gio", "noi_dung", "anh", "trang_thai")
        self.post_tree = ttk.Treeview(row_list, columns=cols, show="headings", height=5)
        self.post_tree.heading("stt", text="#")
        self.post_tree.heading("gio", text="Giờ")
        self.post_tree.heading("noi_dung", text="Nội dung")
        self.post_tree.heading("anh", text="Ảnh")
        self.post_tree.heading("trang_thai", text="Trạng thái")

        self.post_tree.column("stt", width=30)
        self.post_tree.column("gio", width=60)
        self.post_tree.column("noi_dung", width=350)
        self.post_tree.column("anh", width=50)
        self.post_tree.column("trang_thai", width=100)

        self.post_tree.pack(fill=tk.BOTH, expand=True)

        # ── Status & Controls ──
        self.post_status = tk.StringVar(value="Sẵn sàng")
        ttk.Label(frame, textvariable=self.post_status, foreground="blue").pack(padx=10, anchor=tk.W)

        row_btn = ttk.Frame(frame)
        row_btn.pack(fill=tk.X, padx=10, pady=5)

        self.btn_post_start = ttk.Button(row_btn, text="▶ Chạy Scheduler", command=self._start_scheduler)
        self.btn_post_start.pack(side=tk.LEFT, padx=5)

        self.btn_post_stop = ttk.Button(row_btn, text="■ Dừng", command=self._stop_scheduler, state=tk.DISABLED)
        self.btn_post_stop.pack(side=tk.LEFT, padx=5)

        ttk.Button(row_btn, text="Xóa lịch", command=self._clear_schedule).pack(side=tk.LEFT, padx=5)

    def _browse_post_images(self):
        paths = filedialog.askopenfilenames(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.gif *.bmp"), ("All", "*.*")]
        )
        if paths:
            self.post_images.set(";".join(paths))

    def _add_scheduled_post(self):
        text = self.post_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập nội dung bài đăng.")
            return

        time_str = self.post_time.get().strip()
        try:
            hour, minute = map(int, time_str.split(":"))
            scheduled_dt = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
        except ValueError:
            messagebox.showerror("Lỗi", "Định dạng giờ không hợp lệ. Dùng HH:MM (ví dụ: 07:00)")
            return

        images = self.post_images.get().strip()
        image_list = [p.strip() for p in images.split(";") if p.strip()] if images else []

        self.auto_poster.add_post(text, image_list, scheduled_dt)
        self._refresh_schedule_list()

    def _refresh_schedule_list(self):
        for item in self.post_tree.get_children():
            self.post_tree.delete(item)

        for i, post in enumerate(self.auto_poster.scheduled_posts):
            self.post_tree.insert("", tk.END, values=(
                i + 1,
                post.scheduled_time.strftime("%H:%M") if post.scheduled_time else "N/A",
                post.text[:60] + "..." if len(post.text) > 60 else post.text,
                len(post.image_paths),
                post.status,
            ))

    def _post_now(self):
        text = self.post_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập nội dung bài đăng.")
            return

        images = self.post_images.get().strip()
        image_list = [p.strip() for p in images.split(";") if p.strip()] if images else []

        self.auto_poster.post_now(text, image_list, status_callback=self._post_status_update)

    def _start_scheduler(self):
        if not self.auto_poster.scheduled_posts:
            messagebox.showwarning("Chưa có lịch", "Vui lòng thêm bài đăng vào lịch trình trước.")
            return

        self.btn_post_start.config(state=tk.DISABLED)
        self.btn_post_stop.config(state=tk.NORMAL)
        self.auto_poster.start_scheduler(status_callback=self._post_status_update)

        # Cập nhật trạng thái mỗi 5 giây
        self._schedule_refresh()

    def _schedule_refresh(self):
        if self.auto_poster.is_running:
            self._refresh_schedule_list()
            self.root.after(5000, self._schedule_refresh)

    def _stop_scheduler(self):
        self.auto_poster.stop()
        self.btn_post_start.config(state=tk.NORMAL)
        self.btn_post_stop.config(state=tk.DISABLED)

    def _clear_schedule(self):
        self.auto_poster.clear_posts()
        self._refresh_schedule_list()

    def _post_status_update(self, message):
        self.root.after(0, lambda: self.post_status.set(message))

    # ══════════════════════════════════════════════════════════════
    # TAB 3: KẾT BẠN TỰ ĐỘNG
    # ══════════════════════════════════════════════════════════════

    def _build_tab_friend(self):
        frame = self.tab_friend

        # ── File SĐT ──
        row_file = ttk.LabelFrame(frame, text="Danh sách SĐT", padding=5)
        row_file.pack(fill=tk.X, padx=10, pady=5)

        self.friend_file_path = tk.StringVar()
        ttk.Entry(row_file, textvariable=self.friend_file_path, width=60).pack(side=tk.LEFT, padx=5)
        ttk.Button(row_file, text="Chọn file...", command=self._browse_friend_file).pack(side=tk.LEFT)

        # ── Lời chào ──
        row_greeting = ttk.LabelFrame(frame, text="Lời nhắn giới thiệu (biến: {ho_ten})", padding=5)
        row_greeting.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.friend_greeting = scrolledtext.ScrolledText(row_greeting, height=4, wrap=tk.WORD)
        self.friend_greeting.pack(fill=tk.BOTH, expand=True)
        self.friend_greeting.insert(tk.END,
            "Chào {ho_ten}, mình là môi giới BĐS tại Sóc Sơn, Hà Nội. "
            "Rất vui được kết nối!"
        )

        # ── Cài đặt ──
        row_settings = ttk.LabelFrame(frame, text="Cài đặt", padding=5)
        row_settings.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(row_settings, text="Delay (giây): Từ").pack(side=tk.LEFT, padx=5)
        self.friend_delay_min = tk.IntVar(value=15)
        ttk.Spinbox(row_settings, from_=10, to=120, width=5, textvariable=self.friend_delay_min).pack(side=tk.LEFT)
        ttk.Label(row_settings, text="đến").pack(side=tk.LEFT, padx=5)
        self.friend_delay_max = tk.IntVar(value=45)
        ttk.Spinbox(row_settings, from_=15, to=300, width=5, textvariable=self.friend_delay_max).pack(side=tk.LEFT)

        ttk.Label(row_settings, text="    Giới hạn/ngày:").pack(side=tk.LEFT, padx=5)
        self.friend_daily_limit = tk.IntVar(value=20)
        ttk.Spinbox(row_settings, from_=1, to=50, width=5, textvariable=self.friend_daily_limit).pack(side=tk.LEFT)

        # ── Progress & Status ──
        self.friend_progress = ttk.Progressbar(frame, mode="determinate")
        self.friend_progress.pack(fill=tk.X, padx=10, pady=2)

        self.friend_status = tk.StringVar(value="Sẵn sàng")
        ttk.Label(frame, textvariable=self.friend_status, foreground="blue").pack(padx=10, anchor=tk.W)

        # ── Nút điều khiển ──
        row_btn = ttk.Frame(frame)
        row_btn.pack(fill=tk.X, padx=10, pady=5)

        self.btn_friend_start = ttk.Button(row_btn, text="▶ Bắt đầu kết bạn", command=self._start_add_friend)
        self.btn_friend_start.pack(side=tk.LEFT, padx=5)

        self.btn_friend_stop = ttk.Button(row_btn, text="■ Dừng", command=self._stop_add_friend, state=tk.DISABLED)
        self.btn_friend_stop.pack(side=tk.LEFT, padx=5)

    def _browse_friend_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("CSV/TXT", "*.csv *.txt"), ("All", "*.*")]
        )
        if path:
            self.friend_file_path.set(path)

    def _start_add_friend(self):
        file_path = self.friend_file_path.get().strip()
        if not file_path:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn file danh sách SĐT.")
            return

        greeting = self.friend_greeting.get("1.0", tk.END).strip()

        self.friend_adder.daily_limit = self.friend_daily_limit.get()

        self.btn_friend_start.config(state=tk.DISABLED)
        self.btn_friend_stop.config(state=tk.NORMAL)
        self.friend_progress["value"] = 0

        self.friend_adder.start(
            file_path=file_path,
            greeting_template=greeting,
            delay_min=self.friend_delay_min.get(),
            delay_max=self.friend_delay_max.get(),
            progress_callback=self._friend_progress_update,
            status_callback=self._friend_status_update,
        )

    def _stop_add_friend(self):
        self.friend_adder.stop()
        self.btn_friend_start.config(state=tk.NORMAL)
        self.btn_friend_stop.config(state=tk.DISABLED)

    def _friend_progress_update(self, current, total):
        self.root.after(0, lambda: self.friend_progress.config(
            maximum=total, value=current
        ))
        if current >= total:
            self.root.after(0, lambda: self.btn_friend_start.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.btn_friend_stop.config(state=tk.DISABLED))

    def _friend_status_update(self, message):
        self.root.after(0, lambda: self.friend_status.set(message))

    # ══════════════════════════════════════════════════════════════
    # TAB 4: XEM LOG
    # ══════════════════════════════════════════════════════════════

    def _build_tab_log(self):
        frame = self.tab_log

        # ── Chọn file log ──
        row_select = ttk.Frame(frame)
        row_select.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(row_select, text="Chọn file log:").pack(side=tk.LEFT, padx=5)

        self.log_file_var = tk.StringVar()
        self.log_combo = ttk.Combobox(row_select, textvariable=self.log_file_var, width=40, state="readonly")
        self.log_combo.pack(side=tk.LEFT, padx=5)

        ttk.Button(row_select, text="Tải lại", command=self._refresh_log_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(row_select, text="Xem", command=self._view_log).pack(side=tk.LEFT, padx=5)

        # ── Bảng log ──
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.log_tree = ttk.Treeview(tree_frame, show="headings", height=20)

        scrollbar_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.log_tree.yview)
        scrollbar_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.log_tree.xview)
        self.log_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        self.log_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Load danh sách file log
        self._refresh_log_files()

    def _refresh_log_files(self):
        files = self.logger.get_log_files()
        self.log_combo["values"] = files
        if files:
            self.log_combo.current(0)

    def _view_log(self):
        filename = self.log_file_var.get()
        if not filename:
            messagebox.showinfo("Thông báo", "Chưa có file log nào.")
            return

        log_path = os.path.join("logs", filename)
        if not os.path.exists(log_path):
            messagebox.showerror("Lỗi", f"Không tìm thấy file: {log_path}")
            return

        # Đọc CSV
        try:
            with open(log_path, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                if not rows:
                    messagebox.showinfo("Thông báo", "File log trống.")
                    return

                headers = list(rows[0].keys())
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không đọc được file log: {e}")
            return

        # Xóa dữ liệu cũ
        for item in self.log_tree.get_children():
            self.log_tree.delete(item)

        # Cập nhật cột
        self.log_tree["columns"] = headers
        for h in headers:
            self.log_tree.heading(h, text=h)
            self.log_tree.column(h, width=120)

        # Thêm dữ liệu
        for row in rows:
            self.log_tree.insert("", tk.END, values=[row.get(h, "") for h in headers])


def main():
    root = tk.Tk()

    # Style
    style = ttk.Style()
    style.theme_use("clam")

    app = ZaloToolApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
