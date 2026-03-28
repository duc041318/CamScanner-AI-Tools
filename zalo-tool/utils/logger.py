import csv
import os
from datetime import datetime


class Logger:
    """Ghi log kết quả ra file CSV."""

    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)

    def _get_log_path(self, feature_name):
        date_str = datetime.now().strftime("%Y-%m-%d")
        return os.path.join(self.log_dir, f"{feature_name}_{date_str}.csv")

    def log(self, feature_name, data: dict):
        """Ghi một dòng log. data là dict chứa các cột cần ghi."""
        log_path = self._get_log_path(feature_name)
        file_exists = os.path.exists(log_path)

        row = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), **data}

        try:
            with open(log_path, "a", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=row.keys())
                if not file_exists:
                    writer.writeheader()
                writer.writerow(row)
        except Exception as e:
            print(f"[Logger] Lỗi ghi log: {e}")

    def read_logs(self, feature_name, date_str=None):
        """Đọc log theo feature và ngày. Trả về list of dict."""
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
        log_path = os.path.join(self.log_dir, f"{feature_name}_{date_str}.csv")

        if not os.path.exists(log_path):
            return []

        try:
            with open(log_path, "r", encoding="utf-8-sig") as f:
                return list(csv.DictReader(f))
        except Exception:
            return []

    def get_log_files(self):
        """Lấy danh sách tất cả file log."""
        if not os.path.exists(self.log_dir):
            return []
        return sorted(
            [f for f in os.listdir(self.log_dir) if f.endswith(".csv")],
            reverse=True,
        )
