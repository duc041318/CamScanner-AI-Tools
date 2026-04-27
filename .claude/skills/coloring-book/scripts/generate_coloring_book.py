"""
Coloring Book Generator – tạo PDF sách tô màu trẻ em chuẩn Amazon KDP.
Kích thước: 8.5 x 11 inch, black & white line art.
"""

import argparse
import math
import random
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Kích thước trang chuẩn KDP
PAGE_WIDTH, PAGE_HEIGHT = letter  # 612 x 792 points = 8.5 x 11 inch
MARGIN = 0.5 * inch

# Bảng chủ đề – từng chủ đề có danh sách hình vẽ
THEMES = {
    "animals": [
        "Cute Lion", "Happy Elephant", "Playful Monkey", "Friendly Giraffe",
        "Baby Bear", "Smiling Tiger", "Funny Penguin", "Sweet Rabbit",
        "Little Frog", "Baby Deer", "Chubby Hippo", "Silly Zebra",
        "Flying Parrot", "Sleepy Owl", "Hungry Shark", "Jumping Dolphin",
        "Baby Turtle", "Fluffy Cat", "Playful Dog", "Funny Duck",
        "Baby Chick", "Happy Cow", "Little Pig", "Cute Goat",
        "Baby Lamb", "Colorful Fish", "Jumping Frog", "Flying Butterfly",
        "Busy Bee", "Crawling Snail", "Friendly Crab", "Smiling Starfish",
    ],
    "vehicles": [
        "Big Fire Truck", "School Bus", "Police Car", "Racing Car",
        "Monster Truck", "Excavator", "Bulldozer", "Crane Truck",
        "Rocket Ship", "Airplane", "Hot Air Balloon", "Sailboat",
        "Submarine", "Train Engine", "Bicycle", "Motorcycle",
        "Tractor", "Dump Truck", "Ambulance", "Ice Cream Truck",
        "Garbage Truck", "Mail Truck", "Helicopter", "Speed Boat",
    ],
    "princess": [
        "Princess in Castle", "Fairy with Wings", "Unicorn", "Magic Wand",
        "Royal Crown", "Princess Dress", "Enchanted Forest", "Fairy House",
        "Rainbow", "Magic Mirror", "Princess Shoes", "Flower Garden",
        "Butterfly Princess", "Mermaid Princess", "Star Princess", "Moon Princess",
        "Dragon Friend", "Magic Carpet", "Treasure Chest", "Crystal Ball",
        "Fairy Tale Book", "Princess Carriage", "Talking Bird", "Magic Flower",
    ],
    "dinosaurs": [
        "T-Rex Roar", "Long Neck Brachiosaurus", "Triceratops", "Flying Pterodactyl",
        "Baby Stegosaurus", "Cute Raptor", "Ankylosaurus", "Spinosaurus",
        "Dino Egg", "Dino Family", "Volcano Scene", "Dino in Jungle",
        "Swimming Plesiosaur", "Small Compsognathus", "Pachycephalosaurus", "Allosaurus",
        "Dino Footprint", "Fossil Bones", "Dino Hatching", "Happy Dino",
    ],
    "ocean": [
        "Happy Whale", "Clownfish & Anemone", "Friendly Octopus", "Seahorse",
        "Starfish", "Jellyfish", "Crab on Beach", "Lobster",
        "Cute Seal", "Walrus", "Narwhal", "Hammerhead Shark",
        "Angel Fish", "Puffer Fish", "Manta Ray", "Electric Eel",
        "Sea Turtle", "Coral Reef", "Pearl Oyster", "Treasure Chest",
        "Lighthouse", "Anchor", "Ship Wreck", "Submarine",
    ],
    "nature": [
        "Sunflower", "Rose", "Daisy", "Tulip",
        "Oak Tree", "Cherry Blossom", "Mushroom", "Cactus",
        "Waterfall", "Mountain", "Rainbow", "Snowflake",
        "Sun & Clouds", "Moon & Stars", "Butterfly on Flower", "Ladybug on Leaf",
        "Caterpillar", "Dragonfly", "Bee & Honeycomb", "Acorn",
        "Maple Leaf", "Pine Cone", "Berry Bush", "Pond with Lily",
    ],
}


def get_theme_items(theme: str, count: int) -> list[str]:
    """Lấy danh sách tiêu đề trang theo chủ đề, lặp lại nếu cần."""
    items = THEMES.get(theme, THEMES["animals"])
    result = []
    while len(result) < count:
        result.extend(items)
    return result[:count]


# ── Các hàm vẽ hình SVG-style bằng ReportLab ──────────────────────────────

def draw_rounded_blob(c, cx, cy, rx, ry, fill=False):
    """Vẽ blob tròn – dùng làm thân nhân vật."""
    c.saveState()
    c.translate(cx, cy)
    path = c.beginPath()
    path.ellipse(-rx, -ry, rx, ry)
    if fill:
        c.setFillColor(colors.white)
        c.drawPath(path, fill=1, stroke=1)
    else:
        c.drawPath(path, fill=0, stroke=1)
    c.restoreState()


def draw_star(c, cx, cy, r_outer, r_inner, points=5, lw=2.5):
    """Vẽ ngôi sao."""
    c.saveState()
    c.setLineWidth(lw)
    path = c.beginPath()
    for i in range(points * 2):
        angle = math.pi / 2 + i * math.pi / points
        r = r_outer if i % 2 == 0 else r_inner
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        if i == 0:
            path.moveTo(x, y)
        else:
            path.lineTo(x, y)
    path.close()
    c.setFillColor(colors.white)
    c.drawPath(path, fill=1, stroke=1)
    c.restoreState()


def draw_flower(c, cx, cy, petal_r, center_r, num_petals=6, lw=2.5):
    """Vẽ bông hoa."""
    c.saveState()
    c.setLineWidth(lw)
    for i in range(num_petals):
        angle = i * 2 * math.pi / num_petals
        px = cx + petal_r * math.cos(angle)
        py = cy + petal_r * math.sin(angle)
        path = c.beginPath()
        path.ellipse(px - petal_r * 0.4, py - petal_r * 0.4,
                     px + petal_r * 0.4, py + petal_r * 0.4)
        c.setFillColor(colors.white)
        c.drawPath(path, fill=1, stroke=1)
    # nhụy hoa
    path = c.beginPath()
    path.ellipse(cx - center_r, cy - center_r, cx + center_r, cy + center_r)
    c.setFillColor(colors.white)
    c.drawPath(path, fill=1, stroke=1)
    c.restoreState()


def draw_animal_generic(c, cx, cy, size, label: str, lw=3.0):
    """Vẽ nhân vật động vật generic dễ thương."""
    c.saveState()
    c.setLineWidth(lw)
    c.setStrokeColor(colors.black)
    c.setFillColor(colors.white)

    # Thân
    body_w, body_h = size * 0.55, size * 0.45
    body_path = c.beginPath()
    body_path.ellipse(cx - body_w, cy - size * 0.1 - body_h,
                      cx + body_w, cy - size * 0.1 + body_h)
    c.drawPath(body_path, fill=1, stroke=1)

    # Đầu
    head_r = size * 0.32
    head_path = c.beginPath()
    head_path.ellipse(cx - head_r, cy + size * 0.18 - head_r,
                      cx + head_r, cy + size * 0.18 + head_r)
    c.drawPath(head_path, fill=1, stroke=1)

    # Tai trái
    ear_lx = cx - head_r * 0.65
    ear_ty = cy + size * 0.18 + head_r * 0.75
    ear_path = c.beginPath()
    ear_path.ellipse(ear_lx - head_r * 0.22, ear_ty - head_r * 0.28,
                     ear_lx + head_r * 0.22, ear_ty + head_r * 0.28)
    c.drawPath(ear_path, fill=1, stroke=1)

    # Tai phải
    ear_rx = cx + head_r * 0.65
    ear_path2 = c.beginPath()
    ear_path2.ellipse(ear_rx - head_r * 0.22, ear_ty - head_r * 0.28,
                      ear_rx + head_r * 0.22, ear_ty + head_r * 0.28)
    c.drawPath(ear_path2, fill=1, stroke=1)

    # Mắt trái
    eye_size = head_r * 0.18
    el_x = cx - head_r * 0.35
    el_y = cy + size * 0.18 + head_r * 0.1
    ep = c.beginPath()
    ep.ellipse(el_x - eye_size, el_y - eye_size, el_x + eye_size, el_y + eye_size)
    c.setFillColor(colors.black)
    c.drawPath(ep, fill=1, stroke=1)
    c.setFillColor(colors.white)

    # Mắt phải
    er_x = cx + head_r * 0.35
    ep2 = c.beginPath()
    ep2.ellipse(er_x - eye_size, el_y - eye_size, er_x + eye_size, el_y + eye_size)
    c.setFillColor(colors.black)
    c.drawPath(ep2, fill=1, stroke=1)
    c.setFillColor(colors.white)

    # Mũi
    nose_y = cy + size * 0.18 - head_r * 0.22
    np_ = c.beginPath()
    np_.ellipse(cx - head_r * 0.14, nose_y - head_r * 0.1,
                cx + head_r * 0.14, nose_y + head_r * 0.1)
    c.setFillColor(colors.black)
    c.drawPath(np_, fill=1, stroke=1)
    c.setFillColor(colors.white)

    # Nụ cười (arc)
    smile_r = head_r * 0.28
    c.arc(cx - smile_r, nose_y - smile_r * 1.2,
          cx + smile_r, nose_y + smile_r * 0.4,
          startAng=200, extent=140)

    # Chân trước trái
    leg_lx = cx - body_w * 0.55
    leg_y_top = cy - size * 0.1 + body_h * 0.0
    leg_w, leg_h = size * 0.14, size * 0.28
    c.rect(leg_lx - leg_w / 2, leg_y_top - body_h - leg_h, leg_w, leg_h)

    # Chân trước phải
    leg_rx = cx + body_w * 0.55
    c.rect(leg_rx - leg_w / 2, leg_y_top - body_h - leg_h, leg_w, leg_h)

    # Đuôi (nhỏ ở phải)
    tail_cx = cx + body_w * 0.9
    tail_cy = cy - size * 0.1
    tail_path = c.beginPath()
    tail_path.ellipse(tail_cx - size * 0.07, tail_cy - size * 0.12,
                      tail_cx + size * 0.07, tail_cy + size * 0.12)
    c.setFillColor(colors.white)
    c.drawPath(tail_path, fill=1, stroke=1)

    c.restoreState()


def draw_vehicle_generic(c, cx, cy, size, lw=3.0):
    """Vẽ xe hơi cute generic."""
    c.saveState()
    c.setLineWidth(lw)
    c.setStrokeColor(colors.black)
    c.setFillColor(colors.white)

    body_w = size * 0.65
    body_h = size * 0.22
    body_y = cy - size * 0.1

    # Thân xe dưới
    c.rect(cx - body_w, body_y - body_h, body_w * 2, body_h)

    # Thân xe trên (cabin)
    cabin_w = body_w * 0.65
    cabin_h = body_h * 0.9
    c.roundRect(cx - cabin_w, body_y, cabin_w * 2, cabin_h, radius=size * 0.06)

    # Cửa sổ trái
    win_w = cabin_w * 0.38
    win_h = cabin_h * 0.55
    win_y = body_y + cabin_h * 0.22
    c.roundRect(cx - cabin_w * 0.85, win_y, win_w, win_h, radius=size * 0.03)

    # Cửa sổ phải
    c.roundRect(cx + cabin_w * 0.85 - win_w, win_y, win_w, win_h, radius=size * 0.03)

    # Bánh xe trái
    wheel_r = size * 0.16
    wl_cx = cx - body_w * 0.55
    wl_cy = body_y - body_h
    wpath = c.beginPath()
    wpath.ellipse(wl_cx - wheel_r, wl_cy - wheel_r, wl_cx + wheel_r, wl_cy + wheel_r)
    c.drawPath(wpath, fill=1, stroke=1)
    # Hub
    hub_r = wheel_r * 0.4
    hp = c.beginPath()
    hp.ellipse(wl_cx - hub_r, wl_cy - hub_r, wl_cx + hub_r, wl_cy + hub_r)
    c.setFillColor(colors.lightgrey)
    c.drawPath(hp, fill=1, stroke=1)
    c.setFillColor(colors.white)

    # Bánh xe phải
    wr_cx = cx + body_w * 0.55
    wpath2 = c.beginPath()
    wpath2.ellipse(wr_cx - wheel_r, wl_cy - wheel_r, wr_cx + wheel_r, wl_cy + wheel_r)
    c.drawPath(wpath2, fill=1, stroke=1)
    hp2 = c.beginPath()
    hp2.ellipse(wr_cx - hub_r, wl_cy - hub_r, wr_cx + hub_r, wl_cy + hub_r)
    c.setFillColor(colors.lightgrey)
    c.drawPath(hp2, fill=1, stroke=1)
    c.setFillColor(colors.white)

    # Đèn xe
    light_w, light_h = size * 0.1, size * 0.07
    c.rect(cx + body_w - light_w - size * 0.04,
           body_y - body_h * 0.55, light_w, light_h)

    c.restoreState()


def draw_theme_art(c, cx, cy, size, label: str, theme: str, lw: float):
    """Điều phối vẽ hình theo chủ đề."""
    if theme in ("animals", "dinosaurs", "ocean"):
        draw_animal_generic(c, cx, cy, size, label, lw)
    elif theme == "vehicles":
        draw_vehicle_generic(c, cx, cy, size, lw)
    elif theme in ("princess", "nature"):
        draw_flower(c, cx, cy, size * 0.35, size * 0.12, num_petals=7, lw=lw)
        # Thêm ngôi sao trang trí
        draw_star(c, cx + size * 0.55, cy + size * 0.4, size * 0.1, size * 0.05, lw=lw)
        draw_star(c, cx - size * 0.6, cy + size * 0.35, size * 0.08, size * 0.04, lw=lw)
    else:
        draw_animal_generic(c, cx, cy, size, label, lw)


# ── Các hàm vẽ trang ───────────────────────────────────────────────────────

def draw_cover(c, title: str, author: str, theme: str):
    """Vẽ trang bìa."""
    c.setPageSize(letter)

    # Viền ngoài
    c.setLineWidth(4)
    c.setStrokeColor(colors.black)
    c.rect(MARGIN * 0.5, MARGIN * 0.5,
           PAGE_WIDTH - MARGIN, PAGE_HEIGHT - MARGIN)

    # Viền trong trang trí
    c.setLineWidth(1.5)
    c.rect(MARGIN * 0.75, MARGIN * 0.75,
           PAGE_WIDTH - MARGIN * 1.5, PAGE_HEIGHT - MARGIN * 1.5)

    # Hoa trang trí 4 góc
    corner_offsets = [
        (MARGIN * 1.2, MARGIN * 1.2),
        (PAGE_WIDTH - MARGIN * 1.2, MARGIN * 1.2),
        (MARGIN * 1.2, PAGE_HEIGHT - MARGIN * 1.2),
        (PAGE_WIDTH - MARGIN * 1.2, PAGE_HEIGHT - MARGIN * 1.2),
    ]
    for ox, oy in corner_offsets:
        draw_flower(c, ox, oy, 0.25 * inch, 0.08 * inch, num_petals=6, lw=1.5)

    # Tiêu đề sách
    c.setFont("Helvetica-Bold", 36)
    c.setFillColor(colors.black)
    title_y = PAGE_HEIGHT - 2.2 * inch
    c.drawCentredString(PAGE_WIDTH / 2, title_y, title)

    # Subtitle
    c.setFont("Helvetica", 16)
    c.drawCentredString(PAGE_WIDTH / 2, title_y - 0.5 * inch,
                        f"A {theme.title()} Coloring Adventure")

    # Hình minh họa trung tâm trang bìa
    art_cx = PAGE_WIDTH / 2
    art_cy = PAGE_HEIGHT / 2 - 0.3 * inch
    art_size = 2.8 * inch
    c.setLineWidth(4)
    draw_theme_art(c, art_cx, art_cy, art_size, title, theme, lw=4.0)

    # Khung trang trí quanh hình
    frame_margin = art_size * 0.25
    c.setLineWidth(1.5)
    c.setDash([6, 3])
    c.rect(art_cx - art_size - frame_margin,
           art_cy - art_size - frame_margin,
           (art_size + frame_margin) * 2,
           (art_size + frame_margin) * 2)
    c.setDash([])

    # Tên tác giả
    c.setFont("Helvetica-Oblique", 14)
    c.drawCentredString(PAGE_WIDTH / 2, MARGIN * 1.5 + 0.3 * inch,
                        f"By {author}")

    # Nhãn "Ages 4-8"
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(PAGE_WIDTH / 2, MARGIN * 1.5,
                        "For Ages 4-8")

    c.showPage()


def draw_copyright_page(c, title: str, author: str):
    """Vẽ trang copyright."""
    c.setPageSize(letter)
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.black)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 2 * inch, title)

    lines = [
        f"Copyright © 2025 {author}",
        "All rights reserved.",
        "",
        "No part of this publication may be reproduced,",
        "distributed, or transmitted in any form or by any means,",
        "including photocopying, recording, or other electronic",
        "or mechanical methods, without the prior written permission",
        "of the publisher.",
        "",
        "Printed in the United States of America",
        "",
        "First Edition, 2025",
        "",
        "For permissions contact:",
        f"{author}",
    ]

    c.setFont("Helvetica", 10)
    y = PAGE_HEIGHT / 2 + 1 * inch
    for line in lines:
        c.drawCentredString(PAGE_WIDTH / 2, y, line)
        y -= 0.22 * inch

    c.showPage()


def draw_coloring_page(c, title: str, page_num: int, total_pages: int,
                       theme: str, book_title: str, lw: float):
    """Vẽ một trang tô màu."""
    c.setPageSize(letter)
    c.setStrokeColor(colors.black)
    c.setFillColor(colors.black)

    # Viền trang mỏng
    c.setLineWidth(1.0)
    c.rect(MARGIN * 0.6, MARGIN * 0.6,
           PAGE_WIDTH - MARGIN * 1.2, PAGE_HEIGHT - MARGIN * 1.2)

    # Tên sách góc trên
    c.setFont("Helvetica", 7)
    c.setFillColor(colors.grey)
    c.drawString(MARGIN, PAGE_HEIGHT - MARGIN * 0.75, book_title)

    # Số trang góc phải
    c.drawRightString(PAGE_WIDTH - MARGIN, PAGE_HEIGHT - MARGIN * 0.75,
                      f"Page {page_num}")
    c.setFillColor(colors.black)

    # Tiêu đề hình vẽ
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 1.4 * inch, title)

    # Vùng vẽ hình
    art_cx = PAGE_WIDTH / 2
    art_cy = PAGE_HEIGHT / 2 + 0.2 * inch
    art_size = 2.9 * inch

    draw_theme_art(c, art_cx, art_cy, art_size, title, theme, lw=lw)

    # Dòng chấm phía dưới để trẻ viết tên màu
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.grey)
    c.drawCentredString(PAGE_WIDTH / 2, MARGIN * 1.1, "Color me!")

    dot_y = MARGIN * 1.35
    c.setLineWidth(0.5)
    c.setDash([2, 4])
    c.line(MARGIN, dot_y, PAGE_WIDTH - MARGIN, dot_y)
    c.setDash([])

    c.showPage()


def draw_back_matter(c, book_title: str, author: str):
    """Trang kết sách."""
    c.setPageSize(letter)

    # Viền
    c.setLineWidth(3)
    c.setStrokeColor(colors.black)
    c.rect(MARGIN * 0.5, MARGIN * 0.5,
           PAGE_WIDTH - MARGIN, PAGE_HEIGHT - MARGIN)

    # Trang trí hoa
    for i in range(8):
        angle = i * math.pi / 4
        fx = PAGE_WIDTH / 2 + 2.5 * inch * math.cos(angle)
        fy = PAGE_HEIGHT / 2 + 2.5 * inch * math.sin(angle)
        draw_flower(c, fx, fy, 0.2 * inch, 0.07 * inch, lw=1.5)

    # Ngôi sao trung tâm
    draw_star(c, PAGE_WIDTH / 2, PAGE_HEIGHT / 2 + 0.5 * inch,
              0.9 * inch, 0.4 * inch, points=5, lw=3)

    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(colors.black)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT / 2 - 0.2 * inch, "THE END")

    c.setFont("Helvetica", 12)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT / 2 - 0.65 * inch,
                        "Great job coloring! You are an artist!")

    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(PAGE_WIDTH / 2, MARGIN * 2.2,
                        "Enjoyed this book? Please leave a review!")

    c.setFont("Helvetica", 9)
    c.drawCentredString(PAGE_WIDTH / 2, MARGIN * 1.7, f"© 2025 {author}")

    c.showPage()


# ── Main generator ──────────────────────────────────────────────────────────

def generate(title: str, author: str, theme: str, num_pages: int,
             age_group: str, output: str):
    # Tính độ dày nét theo độ tuổi
    age_to_lw = {"2-4": 5.0, "4-8": 3.5, "8-12": 2.5}
    lw = age_to_lw.get(age_group, 3.5)

    # Đảm bảo số trang chẵn (yêu cầu KDP)
    if num_pages % 2 != 0:
        num_pages += 1

    # Số trang nội dung = tổng - bìa - copyright - kết
    content_pages = num_pages - 4
    if content_pages < 1:
        content_pages = 1

    items = get_theme_items(theme, content_pages)

    out_path = Path(output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    c = rl_canvas.Canvas(str(out_path), pagesize=letter)
    c.setTitle(title)
    c.setAuthor(author)
    c.setSubject(f"Children's Coloring Book – {theme.title()} Theme")
    c.setKeywords(f"coloring book, kids, {theme}, activity book")

    # Trang bìa
    draw_cover(c, title, author, theme)

    # Trang copyright
    draw_copyright_page(c, title, author)

    # Các trang tô màu
    for i, item_label in enumerate(items, start=1):
        draw_coloring_page(c, item_label, i, content_pages,
                           theme, title, lw)

    # Trang kết
    draw_back_matter(c, title, author)

    c.save()
    print(f"[OK] Đã tạo: {out_path}  ({num_pages} trang, chủ đề: {theme})")

    # Tạo thêm ảnh preview trang đầu nếu có Pillow
    try:
        _make_preview(str(out_path))
    except Exception:
        pass


def _make_preview(pdf_path: str):
    """Chuyển trang đầu PDF thành JPG preview (dùng pdf2image nếu có)."""
    try:
        from pdf2image import convert_from_path
        imgs = convert_from_path(pdf_path, dpi=150, first_page=1, last_page=3)
        base = Path(pdf_path).stem
        for i, img in enumerate(imgs, 1):
            out = Path(pdf_path).parent / f"{base}_preview_p{i}.jpg"
            img.save(str(out), "JPEG", quality=90)
        print(f"[OK] Preview ảnh: {len(imgs)} trang")
    except ImportError:
        print("[INFO] Cài pdf2image để tạo preview: pip install pdf2image")


# ── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Tạo PDF sách tô màu trẻ em chuẩn Amazon KDP"
    )
    parser.add_argument("--title", default="My Coloring Book",
                        help="Tên sách")
    parser.add_argument("--author", default="Happy Kids Press",
                        help="Tên tác giả / bút danh")
    parser.add_argument("--theme",
                        choices=list(THEMES.keys()),
                        default="animals",
                        help=f"Chủ đề: {', '.join(THEMES.keys())}")
    parser.add_argument("--pages", type=int, default=50,
                        help="Số trang (50-100, sẽ làm chẵn nếu lẻ)")
    parser.add_argument("--age-group",
                        choices=["2-4", "4-8", "8-12"],
                        default="4-8",
                        help="Độ tuổi mục tiêu (ảnh hưởng độ dày nét vẽ)")
    parser.add_argument("--output", default="coloring_book.pdf",
                        help="Đường dẫn file PDF đầu ra")
    args = parser.parse_args()

    generate(
        title=args.title,
        author=args.author,
        theme=args.theme,
        num_pages=args.pages,
        age_group=args.age_group,
        output=args.output,
    )


if __name__ == "__main__":
    main()
