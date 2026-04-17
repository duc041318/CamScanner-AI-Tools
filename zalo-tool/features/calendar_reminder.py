"""
Tính năng Lịch hẹn & Nhắc nhở: Lưu cuộc hẹn, nhắc trước 1 tiếng qua popup.
"""

import json
import os
import threading
import time
from datetime import datetime, timedelta


DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "..", "data", "appointments.json")


class Appointment:
    def __init__(self, id, date, time_str, title, note="", reminded=False):
        self.id = id
        self.date = date          # "YYYY-MM-DD"
        self.time_str = time_str  # "HH:MM"
        self.title = title
        self.note = note
        self.reminded = reminded  # đã nhắc chưa

    def datetime_obj(self):
        return datetime.strptime(f"{self.date} {self.time_str}", "%Y-%m-%d %H:%M")

    def reminder_datetime(self):
        return self.datetime_obj() - timedelta(hours=1)

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date,
            "time": self.time_str,
            "title": self.title,
            "note": self.note,
            "reminded": self.reminded,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d["id"],
            date=d["date"],
            time_str=d["time"],
            title=d["title"],
            note=d.get("note", ""),
            reminded=d.get("reminded", False),
        )


class CalendarReminder:
    def __init__(self):
        self.appointments: list[Appointment] = []
        self._next_id = 1
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._alert_callback = None  # fn(appointment) hiển thị thông báo
        self._load()

    # ── Lưu / tải ──────────────────────────────────────────────────

    def _load(self):
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        if not os.path.exists(DATA_FILE):
            self.appointments = []
            self._next_id = 1
            return
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.appointments = [Appointment.from_dict(d) for d in data]
            ids = [a.id for a in self.appointments]
            self._next_id = (max(ids) + 1) if ids else 1
        except Exception:
            self.appointments = []
            self._next_id = 1

    def _save(self):
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([a.to_dict() for a in self.appointments], f,
                      ensure_ascii=False, indent=2)

    # ── CRUD ────────────────────────────────────────────────────────

    def add(self, date: str, time_str: str, title: str, note: str = "") -> Appointment:
        appt = Appointment(self._next_id, date, time_str, title, note)
        self._next_id += 1
        self.appointments.append(appt)
        self._save()
        return appt

    def delete(self, appt_id: int):
        self.appointments = [a for a in self.appointments if a.id != appt_id]
        self._save()

    def get_by_date(self, date: str) -> list[Appointment]:
        return sorted(
            [a for a in self.appointments if a.date == date],
            key=lambda a: a.time_str,
        )

    def get_all_sorted(self) -> list[Appointment]:
        return sorted(self.appointments, key=lambda a: (a.date, a.time_str))

    # ── Scheduler nhắc nhở ──────────────────────────────────────────

    def start_reminder(self, alert_callback):
        """Chạy vòng lặp nền kiểm tra nhắc nhở mỗi 30 giây."""
        self._alert_callback = alert_callback
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop_reminder(self):
        self._stop_event.set()

    def _loop(self):
        while not self._stop_event.is_set():
            now = datetime.now().replace(second=0, microsecond=0)
            for appt in list(self.appointments):
                if appt.reminded:
                    continue
                remind_at = appt.reminder_datetime().replace(second=0, microsecond=0)
                if now >= remind_at and now < appt.datetime_obj():
                    appt.reminded = True
                    self._save()
                    if self._alert_callback:
                        self._alert_callback(appt)
            self._stop_event.wait(30)
