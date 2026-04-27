---
name: coloring-book
description: "Tạo sách tô màu cho trẻ em (50-100 trang) dạng PDF chất lượng cao, sẵn sàng đăng bán trên Amazon KDP hoặc eBay. Kích thước chuẩn 8.5x11 inch. Dùng skill này khi người dùng muốn tạo sách tô màu, coloring book, activity book cho trẻ. Use this skill when the user wants to generate a children's coloring book PDF ready for print-on-demand publishing on Amazon KDP or eBay."
---

# Coloring Book Skill

Tạo sách tô màu trẻ em dạng PDF chuẩn in ấn, sẵn sàng đăng bán trên **Amazon KDP** hoặc **eBay**.

---

## Thông số chuẩn xuất bản

| Thông số | Giá trị |
|----------|---------|
| Kích thước trang | 8.5 × 11 inch (216 × 279 mm) |
| Độ phân giải | 300 DPI |
| Số trang | 50–100 trang (nên chẵn) |
| Màu sắc | Đen trắng (black & white line art) |
| Bleed | 0.125 inch (3.175 mm) mỗi cạnh nếu có bleed |
| Font chữ | Sans-serif đơn giản, dễ đọc cho trẻ |
| Định dạng xuất | PDF/X-1a hoặc PDF tiêu chuẩn |

---

## Workflow

### Bước 1 – Thu thập thông tin
Hỏi người dùng các thông tin sau nếu chưa có:
- **Chủ đề** (ví dụ: động vật, xe cộ, cổ tích, thiên nhiên, công chúa, khủng long…)
- **Độ tuổi mục tiêu** (2–4, 4–8, 8–12 tuổi)
- **Số trang** (mặc định: 50)
- **Tên sách** và tên tác giả (dùng bút danh nếu muốn)
- **Phong cách line art** (đơn giản/chunky cho trẻ nhỏ, chi tiết hơn cho trẻ lớn)

### Bước 2 – Lên kế hoạch nội dung
Tạo danh sách trang gồm:
- **Trang bìa** (Cover) – 1 trang
- **Trang lót bìa** (Copyright/Title page) – 1–2 trang  
- **Trang nội dung** (Coloring pages) – 46–96 trang
- **Trang kết** (Back matter: "The End", bonus activity, rating request) – 1–2 trang

Mỗi trang nội dung cần:
- 1 hình vẽ line art chiếm 70–80% trang
- Tiêu đề ngắn phía trên hoặc phía dưới hình (tùy chủ đề)
- Khoảng trắng đủ để trẻ tô màu

### Bước 3 – Tạo PDF bằng Python
Dùng script `scripts/generate_coloring_book.py`. Đọc file đó trước khi chạy.

```bash
# Cài dependencies
pip install reportlab Pillow

# Chạy script
python scripts/generate_coloring_book.py \
  --title "My Animal Coloring Book" \
  --author "Happy Kids Press" \
  --theme "animals" \
  --pages 50 \
  --age-group "4-8" \
  --output "coloring_book.pdf"
```

### Bước 4 – Kiểm tra chất lượng (QA)
Sau khi tạo PDF, kiểm tra:
- [ ] Kích thước trang đúng 8.5×11 inch
- [ ] Line art rõ nét, không bị mờ hay vỡ
- [ ] Font chữ dễ đọc, đủ lớn
- [ ] Không có phần tử bị cắt ngoài lề
- [ ] Trang bìa hấp dẫn, có tên sách + tác giả
- [ ] Copyright page có thông tin đầy đủ
- [ ] Số trang chẵn (yêu cầu của KDP)

### Bước 5 – Chuẩn bị đăng bán
Đọc `references/publishing-guide.md` để biết chi tiết về:
- Đăng lên Amazon KDP
- Đăng lên eBay dạng digital download
- Viết mô tả sản phẩm và keywords

---

## Cấu trúc trang coloring book

```
┌─────────────────────────────┐
│  Tên sách (nhỏ, góc trên)   │
├─────────────────────────────┤
│                             │
│    TIÊU ĐỀ HÌNH VẼ         │
│                             │
│  ┌───────────────────────┐  │
│  │                       │  │
│  │    LINE ART DRAWING   │  │
│  │    (thick outlines,   │  │
│  │     no fill)          │  │
│  │                       │  │
│  └───────────────────────┘  │
│                             │
│  [khoảng trắng tô màu]      │
└─────────────────────────────┘
```

---

## Nguyên tắc vẽ line art cho trẻ em

### Theo độ tuổi:
- **2–4 tuổi**: Đường nét rất dày (5–8pt), hình đơn giản, không chi tiết nhỏ
- **4–8 tuổi**: Đường nét dày (3–5pt), hình dễ nhận biết, ít chi tiết
- **8–12 tuổi**: Đường nét vừa (2–3pt), có thể có chi tiết trang trí, mandala

### Quy tắc chung:
- Outline **khép kín** (closed paths) để trẻ tô không bị tràn màu
- **Không có gradient** – chỉ outline đen trên nền trắng
- Khoảng trống tô màu **đủ rộng** (tối thiểu 5mm)
- Không dùng hình quá nhỏ (dưới 1cm²)
- Tránh crosshatch hoặc shading phức tạp

---

## Chủ đề phổ biến bán chạy trên Amazon KDP

| Chủ đề | Từ khóa gợi ý |
|--------|--------------|
| Động vật farm | farm animals, cute cow, pig, chicken |
| Dưới biển | ocean, fish, dolphin, mermaid |
| Khủng long | dinosaur, T-rex, cute dino |
| Công chúa/Unicorn | princess, unicorn, fairy |
| Xe cộ | trucks, cars, construction vehicles |
| Thiên nhiên/Hoa | flowers, butterfly, garden |
| Mandala đơn giản | easy mandala, kids mandala |
| Tết/Lễ hội | Christmas, Halloween, Easter |
| Nghề nghiệp | doctor, firefighter, astronaut |
| Siêu anh hùng | superhero (tránh bản quyền thương hiệu) |

---

## Dependencies

```bash
pip install reportlab Pillow svglib cairosvg
```

Nếu muốn tạo SVG rồi chuyển sang PDF:
```bash
pip install svglib reportlab
```

---

## Lưu ý bản quyền (Copyright)

- **KHÔNG** sao chép nhân vật có bản quyền (Disney, Marvel, Pokémon…)
- Tạo nhân vật **gốc** hoặc dùng style chung (generic animals, vehicles)
- Thêm dòng copyright: `© [Năm] [Tên tác giả]. All rights reserved.`
- Có thể đăng ký ISBN miễn phí qua Amazon KDP

---

## Output mong đợi

Script tạo ra:
1. `coloring_book.pdf` – File PDF sẵn sàng upload KDP
2. `cover.pdf` – File bìa riêng (nếu cần)
3. `preview_pages.jpg` – Ảnh preview 3–5 trang đầu để đăng eBay/Etsy
