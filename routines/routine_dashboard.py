"""
DASHBOARD HTML - Báo cáo trực quan offline
Được gọi sau routine_bao_cao (21:00) hoặc chạy thủ công.
Output: routines/bao-cao/dashboard-YYYY-MM-DD.html
"""

import csv
import os
from collections import defaultdict
from datetime import date, datetime, timedelta

_ROOT      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BAO_CAO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bao-cao")
CONTACTS_FILE = os.path.join(_ROOT, "zalo-tool", "data", "contacts.csv")
LOG_MAU_FILE  = os.path.join(_ROOT, "zalo-tool", "data", "log_mau_bai.csv")
LOG_DIR       = os.path.join(_ROOT, "zalo-tool", "logs")

TRANG_THAI_TOT = {"co_phan_hoi", "quan_tam", "xem_dat", "da_coc"}


# ── Đọc dữ liệu ───────────────────────────────────────────────────────────────

def _doc_contacts():
    if not os.path.exists(CONTACTS_FILE):
        return []
    with open(CONTACTS_FILE, "r", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def _doc_log_mau():
    if not os.path.exists(LOG_MAU_FILE):
        return []
    with open(LOG_MAU_FILE, "r", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def _gui_theo_ngay(n_ngay=14):
    """Đếm số tin đã gửi mỗi ngày trong N ngày qua."""
    result = {}
    today = date.today()
    for i in range(n_ngay):
        d = (today - timedelta(days=n_ngay - 1 - i)).isoformat()
        result[d] = 0

    if not os.path.exists(LOG_DIR):
        return result

    for fname in os.listdir(LOG_DIR):
        if "bulk_message" not in fname:
            continue
        # Tên file: bulk_message_YYYY-MM-DD.csv
        parts = fname.replace(".csv", "").split("_")
        ngay = parts[-1] if len(parts) >= 3 else ""
        if ngay in result:
            fpath = os.path.join(LOG_DIR, fname)
            try:
                with open(fpath, "r", encoding="utf-8-sig") as f:
                    rows = list(csv.DictReader(f))
                result[ngay] += sum(
                    1 for r in rows if r.get("trang_thai") == "Thành công"
                )
            except Exception:
                pass
    return result


def _hieu_qua_mau(contacts, log_mau):
    """Tính tỷ lệ phản hồi từng mẫu bài."""
    if not log_mau:
        return []
    ts_hien_tai = {r["sdt"]: r.get("trang_thai", "") for r in contacts}
    # Lấy mau_id gần nhất gửi cho từng sdt
    mau_gan_nhat = {}
    for row in log_mau:
        mau_gan_nhat[row["sdt"]] = row["mau_id"]

    stats = {}
    for row in log_mau:
        mid = row["mau_id"]
        preview = row.get("mau_preview", "")[:60]
        if mid not in stats:
            stats[mid] = {"preview": preview, "sdt_set": set(), "phan_hoi": 0}
        stats[mid]["sdt_set"].add(row["sdt"])

    for mid, s in stats.items():
        for sdt in s["sdt_set"]:
            if mau_gan_nhat.get(sdt) == mid and ts_hien_tai.get(sdt) in TRANG_THAI_TOT:
                s["phan_hoi"] += 1

    rows = []
    for mid, s in stats.items():
        gui = len(s["sdt_set"])
        ty_le = s["phan_hoi"] / gui if gui else 0
        rows.append({"id": mid, "preview": s["preview"],
                     "gui": gui, "phan_hoi": s["phan_hoi"], "ty_le": ty_le})
    rows.sort(key=lambda x: x["ty_le"], reverse=True)
    return rows


# ── Render HTML ───────────────────────────────────────────────────────────────

def _card(label, value, color="#2980b9", sub=""):
    return f"""
    <div class="card" style="border-top:4px solid {color}">
      <div class="card-val" style="color:{color}">{value}</div>
      <div class="card-lbl">{label}</div>
      {"<div class='card-sub'>"+sub+"</div>" if sub else ""}
    </div>"""


def _bar(pct, color="#2980b9", height=18):
    w = max(int(pct * 100), 2)
    return (f'<div style="background:#eee;border-radius:3px;height:{height}px;margin:2px 0">'
            f'<div style="width:{w}%;background:{color};height:100%;border-radius:3px;'
            f'display:flex;align-items:center;padding-left:4px;color:#fff;font-size:11px">'
            f'{pct*100:.0f}%</div></div>')


def _tao_html(contacts, log_mau, gui_ngay):
    hom_nay = date.today().isoformat()
    gen_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # Funnel
    funnel_keys = ["moi", "da_gui", "co_phan_hoi", "quan_tam", "xem_dat", "da_coc", "khong_quan_tam"]
    funnel_label = {"moi":"Mới", "da_gui":"Đã gửi", "co_phan_hoi":"Phản hồi",
                    "quan_tam":"Quan tâm", "xem_dat":"Xem đất", "da_coc":"Đã cọc",
                    "khong_quan_tam":"Không QT"}
    funnel_color = {"moi":"#95a5a6","da_gui":"#3498db","co_phan_hoi":"#e67e22",
                    "quan_tam":"#e74c3c","xem_dat":"#9b59b6","da_coc":"#27ae60",
                    "khong_quan_tam":"#bdc3c7"}
    ts_count = defaultdict(int)
    for c in contacts:
        ts_count[c.get("trang_thai","moi")] += 1
    tong = len(contacts)
    hot  = ts_count.get("quan_tam",0) + ts_count.get("co_phan_hoi",0)
    coc  = ts_count.get("da_coc",0)

    # Gửi 14 ngày
    ngay_labels = list(gui_ngay.keys())
    ngay_values = list(gui_ngay.values())
    max_gui = max(ngay_values) or 1
    bar_rows = ""
    for d, v in gui_ngay.items():
        w = int(v / max_gui * 200) if v else 2
        short = d[5:]  # MM-DD
        bar_rows += (f'<tr><td style="text-align:right;padding-right:6px;white-space:nowrap;'
                     f'font-size:12px;color:#666">{short}</td>'
                     f'<td><div style="width:{w}px;height:14px;background:#3498db;'
                     f'border-radius:2px;display:inline-block"></div>'
                     f'&nbsp;<span style="font-size:12px">{v}</span></td></tr>')

    # Top khách nóng
    hot_leads = [c for c in contacts if c.get("trang_thai") in ("quan_tam","co_phan_hoi","xem_dat")]
    hot_rows = ""
    for c in hot_leads[:10]:
        ts = c.get("trang_thai","")
        badge_color = {"quan_tam":"#e74c3c","co_phan_hoi":"#e67e22","xem_dat":"#9b59b6"}.get(ts,"#95a5a6")
        hot_rows += (f'<tr><td>{c.get("ho_ten","")}</td><td>{c.get("sdt","")}</td>'
                     f'<td><span style="background:{badge_color};color:#fff;padding:2px 6px;'
                     f'border-radius:10px;font-size:11px">{ts}</span></td>'
                     f'<td style="color:#666;font-size:12px">{c.get("ghi_chu","")[:40]}</td>'
                     f'<td style="color:#999;font-size:11px">{c.get("ngay_lien_he_cuoi","")}</td></tr>')

    # Hiệu quả mẫu bài
    mau_section = ""
    if log_mau:
        hq = _hieu_qua_mau(contacts, log_mau)
        mau_rows = ""
        for r in hq[:8]:
            color = "#27ae60" if r["ty_le"]>=0.25 else "#f39c12" if r["ty_le"]>=0.1 else "#e74c3c"
            mau_rows += (f'<tr><td style="font-family:monospace;font-size:11px">{r["id"]}</td>'
                         f'<td style="font-size:12px;max-width:280px;overflow:hidden;'
                         f'text-overflow:ellipsis;white-space:nowrap">{r["preview"]}</td>'
                         f'<td style="text-align:center">{r["gui"]}</td>'
                         f'<td style="text-align:center">{r["phan_hoi"]}</td>'
                         f'<td>{_bar(r["ty_le"], color, 14)}</td></tr>')
        mau_section = f"""
        <div class="section">
          <h2>Hiệu quả mẫu bài Zalo</h2>
          <table class="tbl"><thead><tr>
            <th>ID</th><th>Nội dung (60 ký tự)</th><th>Đã gửi</th><th>P.hồi</th><th>Tỷ lệ</th>
          </tr></thead><tbody>{mau_rows}</tbody></table>
        </div>"""
    else:
        mau_section = '<div class="section"><p style="color:#999">Chưa có dữ liệu mẫu bài (chạy Routine Sáng để bắt đầu ghi log).</p></div>'

    # Funnel bars
    funnel_rows = ""
    for k in funnel_keys:
        n = ts_count.get(k, 0)
        if n == 0:
            continue
        pct = n / tong if tong else 0
        funnel_rows += (f'<tr><td style="width:100px;font-size:13px">{funnel_label[k]}</td>'
                        f'<td style="width:200px">{_bar(pct, funnel_color[k], 16)}</td>'
                        f'<td style="font-size:13px;padding-left:8px">{n}</td></tr>')

    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Dashboard BĐS Sóc Sơn - {hom_nay}</title>
<style>
  body{{font-family:Arial,sans-serif;background:#f4f6f9;margin:0;padding:16px;color:#333}}
  h1{{font-size:20px;color:#2c3e50;margin:0 0 4px}}
  h2{{font-size:15px;color:#34495e;margin:12px 0 8px;border-bottom:2px solid #eee;padding-bottom:4px}}
  .sub{{color:#999;font-size:12px;margin-bottom:16px}}
  .cards{{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:16px}}
  .card{{background:#fff;border-radius:8px;padding:14px 18px;min-width:130px;
         box-shadow:0 1px 4px rgba(0,0,0,.08)}}
  .card-val{{font-size:28px;font-weight:bold;line-height:1.1}}
  .card-lbl{{font-size:12px;color:#888;margin-top:4px}}
  .card-sub{{font-size:11px;color:#aaa;margin-top:2px}}
  .section{{background:#fff;border-radius:8px;padding:14px 18px;
            margin-bottom:14px;box-shadow:0 1px 4px rgba(0,0,0,.08)}}
  .tbl{{width:100%;border-collapse:collapse;font-size:13px}}
  .tbl th{{text-align:left;padding:6px 8px;background:#f8f9fa;
           border-bottom:2px solid #dee2e6;color:#666;font-size:12px}}
  .tbl td{{padding:5px 8px;border-bottom:1px solid #f0f0f0}}
  .tbl tr:hover td{{background:#fafbfc}}
  .two-col{{display:grid;grid-template-columns:1fr 1fr;gap:14px}}
</style>
</head>
<body>
<h1>Dashboard BĐS Phú Tằng - Sóc Sơn</h1>
<p class="sub">Cập nhật: {gen_time} &nbsp;|&nbsp; Dự án: Phú Tằng - Đa Phúc - Sóc Sơn</p>

<div class="cards">
  {_card("Tổng khách hàng", tong, "#2980b9")}
  {_card("🔥 Khách nóng", hot, "#e74c3c", "quan_tam + phản hồi")}
  {_card("👀 Xem đất", ts_count.get("xem_dat",0), "#9b59b6")}
  {_card("✅ Đã cọc", coc, "#27ae60")}
  {_card("📩 Chưa liên hệ", ts_count.get("moi",0), "#95a5a6")}
</div>

<div class="two-col">
  <div class="section">
    <h2>Phễu chuyển đổi</h2>
    <table>{funnel_rows}</table>
  </div>
  <div class="section">
    <h2>Tin nhắn gửi thành công (14 ngày qua)</h2>
    <table>{bar_rows}</table>
  </div>
</div>

<div class="section">
  <h2>🔥 Khách nóng cần chăm sóc ({len(hot_leads)} người)</h2>
  {"<table class='tbl'><thead><tr><th>Tên</th><th>SĐT</th><th>Trạng thái</th><th>Ghi chú</th><th>Ngày LH cuối</th></tr></thead><tbody>"
   + hot_rows + "</tbody></table>" if hot_leads else
   "<p style='color:#999'>Chưa có khách nóng.</p>"}
</div>

{mau_section}

<p style="color:#ccc;font-size:11px;text-align:center;margin-top:20px">
  Tự động tạo bởi Zalo Routine Runner &nbsp;|&nbsp; {gen_time}
</p>
</body>
</html>"""
    return html


# ── Hàm chính ─────────────────────────────────────────────────────────────────

def chay(log_callback=None) -> str:
    thoi_gian = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    hom_nay   = date.today().isoformat()

    def _log(msg):
        print(f"[DASHBOARD {thoi_gian}] {msg}")
        if log_callback:
            log_callback(msg)

    _log("Đang tạo Dashboard HTML...")

    contacts = _doc_contacts()
    log_mau  = _doc_log_mau()
    gui_ngay = _gui_theo_ngay(14)

    _log(f"Dữ liệu: {len(contacts)} khách, {len(log_mau)} log mẫu bài.")

    html = _tao_html(contacts, log_mau, gui_ngay)

    os.makedirs(BAO_CAO_DIR, exist_ok=True)
    out = os.path.join(BAO_CAO_DIR, f"dashboard-{hom_nay}.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)

    _log(f"Đã lưu dashboard: {out}")
    return out


if __name__ == "__main__":
    path = chay()
    print(f"\nMở file trong trình duyệt: {path}")
