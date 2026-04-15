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
from features.crm import CRMManager, TRANG_THAI_LIST, NHAN_TRANG_THAI, NHAN_NHOM, NHAN_NGUON
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
        self.crm = CRMManager()

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

        # Tab 4: Mini CRM
        self.tab_crm = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_crm, text="  Mini CRM  ")
        self._build_tab_crm()

        # Tab 5: Xem log
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
    # TAB 4: MINI CRM
    # ══════════════════════════════════════════════════════════════

    def _build_tab_crm(self):
        frame = self.tab_crm

        # ── Thanh thống kê nhanh ──
        self.crm_stats_var = tk.StringVar()
        lbl_stats = ttk.Label(frame, textvariable=self.crm_stats_var,
                              font=("", 9, "bold"), foreground="#c0392b")
        lbl_stats.pack(fill=tk.X, padx=10, pady=(6, 2))

        # ── Bộ lọc ──
        row_filter = ttk.LabelFrame(frame, text="Bộ lọc", padding=4)
        row_filter.pack(fill=tk.X, padx=10, pady=2)

        ttk.Label(row_filter, text="Trạng thái:").pack(side=tk.LEFT, padx=(0, 3))
        ts_options = ["tat_ca"] + TRANG_THAI_LIST
        ts_labels  = ["-- Tất cả --"] + [NHAN_TRANG_THAI[t] for t in TRANG_THAI_LIST]
        self.crm_filter_ts = tk.StringVar(value="tat_ca")
        cb_ts = ttk.Combobox(row_filter, textvariable=self.crm_filter_ts,
                             values=ts_options, width=16, state="readonly")
        cb_ts.pack(side=tk.LEFT, padx=(0, 8))

        ttk.Label(row_filter, text="Nhóm:").pack(side=tk.LEFT, padx=(0, 3))
        nhom_options = ["tat_ca", "muon_o", "dau_tu", "chua_ro"]
        self.crm_filter_nhom = tk.StringVar(value="tat_ca")
        cb_nhom = ttk.Combobox(row_filter, textvariable=self.crm_filter_nhom,
                               values=nhom_options, width=12, state="readonly")
        cb_nhom.pack(side=tk.LEFT, padx=(0, 8))

        ttk.Label(row_filter, text="Tìm:").pack(side=tk.LEFT, padx=(0, 3))
        self.crm_search_var = tk.StringVar()
        self.crm_search_var.trace_add("write", lambda *_: self._crm_load())
        ttk.Entry(row_filter, textvariable=self.crm_search_var, width=18).pack(side=tk.LEFT, padx=(0, 6))

        ttk.Button(row_filter, text="🔄 Tải lại", command=self._crm_load).pack(side=tk.LEFT)

        cb_ts.bind("<<ComboboxSelected>>", lambda _: self._crm_load())
        cb_nhom.bind("<<ComboboxSelected>>", lambda _: self._crm_load())

        # ── Bảng danh sách ──
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=4)

        cols = ("stt", "ho_ten", "sdt", "nhom", "nguon", "trang_thai", "ghi_chu", "ngay_lh")
        self.crm_tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=14)

        head = [("#",25),("Họ tên",130),("SĐT",105),("Nhóm",75),
                ("Nguồn",80),("Trạng thái",100),("Ghi chú",200),("Ngày LH",90)]
        for (col, w), cid in zip(head, cols):
            self.crm_tree.heading(cid, text=col,
                                  command=lambda c=cid: self._crm_sort(c))
            self.crm_tree.column(cid, width=w, anchor=tk.W)

        sb_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL,   command=self.crm_tree.yview)
        sb_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.crm_tree.xview)
        self.crm_tree.configure(yscrollcommand=sb_y.set, xscrollcommand=sb_x.set)
        self.crm_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_y.pack(side=tk.RIGHT, fill=tk.Y)

        # Màu nền theo trạng thái
        self.crm_tree.tag_configure("hot",   background="#fdecea")
        self.crm_tree.tag_configure("warm",  background="#fff8e1")
        self.crm_tree.tag_configure("coc",   background="#e8f5e9")
        self.crm_tree.tag_configure("skip",  background="#f5f5f5", foreground="#aaaaaa")

        self.crm_tree.bind("<<TreeviewSelect>>", self._crm_on_select)

        # ── Panel chỉnh sửa ──
        edit_frame = ttk.LabelFrame(frame, text="Chỉnh sửa khách đã chọn", padding=6)
        edit_frame.pack(fill=tk.X, padx=10, pady=(0, 6))

        # Hàng 1: tên, SĐT, nhóm
        r1 = ttk.Frame(edit_frame)
        r1.pack(fill=tk.X, pady=2)

        ttk.Label(r1, text="Tên:").pack(side=tk.LEFT)
        self.crm_edit_ten = tk.StringVar()
        ttk.Entry(r1, textvariable=self.crm_edit_ten, width=18).pack(side=tk.LEFT, padx=(3,10))

        ttk.Label(r1, text="SĐT:").pack(side=tk.LEFT)
        self.crm_edit_sdt = tk.StringVar()
        ttk.Entry(r1, textvariable=self.crm_edit_sdt, width=13,
                  state="readonly").pack(side=tk.LEFT, padx=(3,10))

        ttk.Label(r1, text="Nhóm:").pack(side=tk.LEFT)
        self.crm_edit_nhom = tk.StringVar()
        ttk.Combobox(r1, textvariable=self.crm_edit_nhom,
                     values=["muon_o","dau_tu","chua_ro"],
                     width=10, state="readonly").pack(side=tk.LEFT, padx=(3,0))

        # Hàng 2: trạng thái, ghi chú, nút
        r2 = ttk.Frame(edit_frame)
        r2.pack(fill=tk.X, pady=2)

        ttk.Label(r2, text="Trạng thái:").pack(side=tk.LEFT)
        self.crm_edit_ts = tk.StringVar()
        ttk.Combobox(r2, textvariable=self.crm_edit_ts,
                     values=TRANG_THAI_LIST, width=16,
                     state="readonly").pack(side=tk.LEFT, padx=(3,10))

        ttk.Label(r2, text="Ghi chú:").pack(side=tk.LEFT)
        self.crm_edit_ghi_chu = tk.StringVar()
        ttk.Entry(r2, textvariable=self.crm_edit_ghi_chu,
                  width=35).pack(side=tk.LEFT, padx=(3,10))

        ttk.Button(r2, text="✅ Cập nhật",
                   command=self._crm_cap_nhat).pack(side=tk.LEFT, padx=(0,4))
        ttk.Button(r2, text="📋 Copy SĐT",
                   command=self._crm_copy_sdt).pack(side=tk.LEFT, padx=(0,4))
        ttk.Button(r2, text="🗑 Xóa",
                   command=self._crm_xoa).pack(side=tk.LEFT, padx=(0,4))

        # Hàng 3: thêm khách mới
        r3 = ttk.LabelFrame(edit_frame, text="Thêm khách mới", padding=4)
        r3.pack(fill=tk.X, pady=(6,0))

        ttk.Label(r3, text="SĐT:").pack(side=tk.LEFT)
        self.crm_new_sdt = tk.StringVar()
        ttk.Entry(r3, textvariable=self.crm_new_sdt, width=13).pack(side=tk.LEFT, padx=(3,8))

        ttk.Label(r3, text="Tên:").pack(side=tk.LEFT)
        self.crm_new_ten = tk.StringVar()
        ttk.Entry(r3, textvariable=self.crm_new_ten, width=16).pack(side=tk.LEFT, padx=(3,8))

        ttk.Label(r3, text="Nhóm:").pack(side=tk.LEFT)
        self.crm_new_nhom = tk.StringVar(value="chua_ro")
        ttk.Combobox(r3, textvariable=self.crm_new_nhom,
                     values=["muon_o","dau_tu","chua_ro"],
                     width=9, state="readonly").pack(side=tk.LEFT, padx=(3,8))

        ttk.Label(r3, text="Nguồn:").pack(side=tk.LEFT)
        self.crm_new_nguon = tk.StringVar(value="zalo")
        ttk.Combobox(r3, textvariable=self.crm_new_nguon,
                     values=["zalo","facebook","gioi_thieu","tu_tim"],
                     width=11, state="readonly").pack(side=tk.LEFT, padx=(3,8))

        ttk.Button(r3, text="➕ Thêm",
                   command=self._crm_them_moi).pack(side=tk.LEFT)

        # Tải dữ liệu lần đầu
        self._crm_load()

    # ── CRM: helpers ──────────────────────────────────────────────

    _crm_sort_col = ""
    _crm_sort_rev = False

    def _crm_load(self):
        ts   = self.crm_filter_ts.get()
        nhom = self.crm_filter_nhom.get()
        kw   = self.crm_search_var.get().strip()

        rows = self.crm.loc(
            trang_thai=ts   if ts   != "tat_ca" else None,
            nhom=nhom       if nhom != "tat_ca" else None,
            tu_khoa=kw or None,
        )

        # Xóa bảng cũ
        for item in self.crm_tree.get_children():
            self.crm_tree.delete(item)

        for i, r in enumerate(rows, 1):
            tts = r.get("trang_thai", "moi")
            tag = ("hot"  if tts in ("quan_tam","co_phan_hoi") else
                   "warm" if tts in ("xem_dat",) else
                   "coc"  if tts == "da_coc" else
                   "skip" if tts == "khong_quan_tam" else "")

            self.crm_tree.insert("", tk.END, iid=r["sdt"], tags=(tag,), values=(
                i,
                r.get("ho_ten",""),
                r.get("sdt",""),
                NHAN_NHOM.get(r.get("nhom",""), r.get("nhom","")),
                NHAN_NGUON.get(r.get("nguon",""), r.get("nguon","")),
                NHAN_TRANG_THAI.get(tts, tts),
                r.get("ghi_chu",""),
                r.get("ngay_lien_he_cuoi",""),
            ))

        # Cập nhật thống kê
        tk_data = self.crm.thong_ke()
        self.crm_stats_var.set(
            f"Tổng: {tk_data['tong']}  |  "
            f"🔥 Nóng: {tk_data['hot']}  |  "
            f"👀 Xem đất: {tk_data['tiem_nang']}  |  "
            f"✅ Đã cọc: {tk_data['da_coc']}  |  "
            f"📩 Mới: {tk_data['moi']}"
        )

    def _crm_on_select(self, _event=None):
        sel = self.crm_tree.selection()
        if not sel:
            return
        sdt = sel[0]
        rows = self.crm.doc_tat_ca()
        for r in rows:
            if r["sdt"] == sdt:
                self.crm_edit_sdt.set(r["sdt"])
                self.crm_edit_ten.set(r.get("ho_ten",""))
                self.crm_edit_nhom.set(r.get("nhom","chua_ro"))
                self.crm_edit_ts.set(r.get("trang_thai","moi"))
                self.crm_edit_ghi_chu.set(r.get("ghi_chu",""))
                break

    def _crm_cap_nhat(self):
        sdt = self.crm_edit_sdt.get().strip()
        if not sdt:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn 1 khách trong bảng.")
            return
        ok = self.crm.cap_nhat(
            sdt,
            trang_thai=self.crm_edit_ts.get() or None,
            ghi_chu=self.crm_edit_ghi_chu.get(),
            ho_ten=self.crm_edit_ten.get() or None,
            nhom=self.crm_edit_nhom.get() or None,
        )
        if ok:
            self._crm_load()
        else:
            messagebox.showerror("Lỗi", f"Không tìm thấy SĐT: {sdt}")

    def _crm_copy_sdt(self):
        sdt = self.crm_edit_sdt.get().strip()
        if sdt:
            self.root.clipboard_clear()
            self.root.clipboard_append(sdt)
            messagebox.showinfo("Đã copy", f"Đã copy SĐT: {sdt}")

    def _crm_xoa(self):
        sdt = self.crm_edit_sdt.get().strip()
        if not sdt:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn 1 khách trong bảng.")
            return
        if messagebox.askyesno("Xác nhận", f"Xóa khách {sdt} khỏi danh sách?"):
            self.crm.xoa(sdt)
            self.crm_edit_sdt.set("")
            self._crm_load()

    def _crm_them_moi(self):
        sdt = self.crm_new_sdt.get().strip()
        ten = self.crm_new_ten.get().strip()
        if not sdt:
            messagebox.showwarning("Thiếu SĐT", "Vui lòng nhập số điện thoại.")
            return
        ok = self.crm.them(
            sdt, ten,
            nhom=self.crm_new_nhom.get(),
            nguon=self.crm_new_nguon.get(),
        )
        if ok:
            self.crm_new_sdt.set("")
            self.crm_new_ten.set("")
            self._crm_load()
        else:
            messagebox.showwarning("Trùng SĐT", f"SĐT {sdt} đã có trong danh sách.")

    def _crm_sort(self, col):
        """Sắp xếp bảng khi click vào tiêu đề cột."""
        col_map = {
            "stt": 0, "ho_ten": 1, "sdt": 2, "nhom": 3,
            "nguon": 4, "trang_thai": 5, "ghi_chu": 6, "ngay_lh": 7
        }
        idx = col_map.get(col, 0)
        items = [(self.crm_tree.set(iid, col), iid)
                 for iid in self.crm_tree.get_children()]
        rev = (self._crm_sort_col == col and not self._crm_sort_rev)
        items.sort(key=lambda x: x[0], reverse=rev)
        for order, (_, iid) in enumerate(items):
            self.crm_tree.move(iid, "", order)
        self._crm_sort_col = col
        self._crm_sort_rev = rev

    # ══════════════════════════════════════════════════════════════
    # TAB 5: XEM LOG
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
