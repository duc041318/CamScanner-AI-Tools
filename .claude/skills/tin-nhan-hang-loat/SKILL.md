---
name: tin-nhan-hang-loat
description: >
  Soan noi dung tin nhan hang loat gui Zalo cho khach hang tiem nang ve dat nen,
  dung cac bien {ho_ten} {du_an} {gia} {dien_tich} de dan thang vao tab
  "Nhan tin hang loat" cua zalo-tool. Dung khi nguoi dung muon soan tin nhan Zalo,
  chuan bi noi dung nhan tin hang loat, viet mau tin nhan gioi thieu lo dat,
  hoac can noi dung cho bulk_message.
---

# Skill: Soạn tin nhắn hàng loạt cho zalo-tool

Soạn nội dung tin nhắn để dán trực tiếp vào ô "Nội dung tin nhắn" của tab **Nhắn tin hàng loạt** trong `zalo-tool/main.py`.

## Bước 1 — Thu thập thông tin

Hỏi người dùng (nếu chưa cung cấp):
- Lô đất / dự án nào đang muốn giới thiệu? (tra cứu `ke-hoach-ban-dat-30-ngay.txt` nếu có trong repo để lấy đúng diện tích, giá, vị trí)
- Nhóm khách hàng mục tiêu là ai? (mua để ở, đầu tư, người địa phương...)
- Có muốn kèm ảnh không (chỉ để nhắc người dùng, tool tự xử lý việc gửi ảnh)

## Bước 2 — Soạn tin nhắn

Bắt buộc dùng đúng các biến mà `utils/file_reader.py` hỗ trợ thay thế qua `apply_template()`:
- `{ho_ten}` — họ tên khách hàng
- `{du_an}` — tên dự án / lô đất
- `{gia}` — giá bán (ví dụ: "1.66 tỷ", "20 triệu/m2")
- `{dien_tich}` — diện tích (ví dụ: "83m2")

Tham khảo giọng văn và cấu trúc trong `mau-bai-dang-zalo.txt` (nếu có trong repo) để tin nhắn nhất quán với các bài đăng khác. Giữ tin nhắn ngắn gọn (3-5 câu), có lời chào cá nhân hóa bằng `{ho_ten}` ở đầu, thông tin chính giữa, và một câu kêu gọi hành động (CTA) ở cuối.

## Bước 3 — Bàn giao

Xuất kết quả trong một khối code (` ``` `) để người dùng copy dễ dàng, và nhắc:
- Dán vào ô "Nội dung tin nhắn" ở tab **Nhắn tin hàng loạt**.
- File danh sách SĐT cần đúng định dạng `.txt` (mỗi dòng 1 SĐT) hoặc `.csv` (cột đầu tiên header `sdt`, các cột khác tương ứng với `ho_ten`, `du_an`, `gia`, `dien_tich` nếu dùng biến đó) — nếu người dùng chưa có file này đúng định dạng, gợi ý dùng skill `chuan-hoa-danh-sach-sdt`.

## Lưu ý

- Không tự ý thêm biến ngoài 4 biến trên trừ khi người dùng xác nhận sẽ sửa `file_reader.py`/CSV tương ứng.
- Nhắc người dùng rằng delay giữa các tin nhắn (10-30s mặc định) là cố ý để tránh bị Zalo đánh dấu spam — không đề xuất giảm delay.
