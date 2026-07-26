---
name: chuan-hoa-danh-sach-sdt
description: >
  Chuan hoa danh sach so dien thoai / khach hang (dan tho, copy tu Excel, hoac
  van ban lon xon) thanh dung dinh dang .txt hoac .csv ma zalo-tool doc duoc
  (utils/file_reader.py). Dung khi nguoi dung dan mot danh sach SDT/khach hang
  va muon tao file cho bulk_message, auto_post, hoac add_friend cua zalo-tool.
---

# Skill: Chuẩn hóa danh sách SĐT cho zalo-tool

Chuyển một danh sách SĐT/khách hàng thô (dán trực tiếp, copy từ Excel, ảnh chụp danh bạ đã được đọc thành text...) thành file đúng định dạng mà `utils/file_reader.py` của `zalo-tool` đọc được.

## Định dạng đích (bắt buộc theo code)

**`.txt`** — dùng khi chỉ có SĐT, không có biến khác:
```
0912345678
0987654321
```
Mỗi dòng đúng 1 số điện thoại, không có header.

**`.csv`** — dùng khi cần cá nhân hóa bằng `{ho_ten}`, `{du_an}`, `{gia}`, `{dien_tich}`:
```
sdt,ho_ten,du_an,gia,dien_tich
0912345678,Anh Minh,Lô 1 Phù Tăng,1.66 tỷ,83m2
0987654321,Chị Lan,Lô 2 Phù Tăng,2.21 tỷ,88.5m2
```
Cột đầu tiên bắt buộc phải tên `sdt` (viết thường, không dấu) — đây là key mà code tra cứu (`contact.get("sdt", "")`). Các cột khác tùy chọn, tên cột phải khớp chính xác với tên biến dùng trong tin nhắn/bài đăng (không dấu, không khoảng trắng).

## Quy trình

1. Nhận danh sách thô từ người dùng (dán trong chat, hoặc từ file đính kèm).
2. Trích các trường có sẵn: số điện thoại (chuẩn hóa về dạng không khoảng trắng, không dấu gạch ngang thừa, giữ số 0 đầu), họ tên, và bất kỳ biến nào khác được cung cấp.
3. Nếu chỉ có SĐT → xuất file dạng `.txt`. Nếu có thêm dữ liệu khác → xuất `.csv` với header `sdt` là cột đầu.
4. Loại bỏ dòng trống, dòng trùng SĐT, và số điện thoại không hợp lệ (báo lại cho người dùng những số bị loại và lý do).
5. Lưu file vào `zalo-tool/data/` (thư mục đã tồn tại, giống `contacts.csv` mẫu) trừ khi người dùng chỉ định nơi khác.

## Lưu ý

- Không đoán bừa họ tên/thông tin thiếu — để trống hoặc hỏi lại người dùng thay vì bịa dữ liệu khách hàng.
- Giữ encoding UTF-8 (có BOM, `utf-8-sig`) vì `file_reader.py` đọc file với `encoding="utf-8-sig"` để hỗ trợ tiếng Việt.
