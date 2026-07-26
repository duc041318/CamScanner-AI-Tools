---
name: dang-bai-zalo
description: >
  Soan noi dung bai dang Nhat ky (Timeline) Zalo gioi thieu lo dat / du an,
  san sang de dan vao tab "Dang bai tu dong" cua zalo-tool, kem goi y gio dang.
  Dung khi nguoi dung muon tao bai dang Zalo, len lich dang bai, quang cao du an
  dat nen, hoac can noi dung cho auto_post.
---

# Skill: Soạn bài đăng Zalo Timeline cho zalo-tool

Soạn nội dung để dán vào ô "Nội dung bài đăng" của tab **Đăng bài tự động** trong `zalo-tool/main.py`.

## Bước 1 — Thu thập thông tin

Hỏi người dùng (nếu chưa cung cấp):
- Lô đất / dự án nào cần quảng bá — tra `ke-hoach-ban-dat-30-ngay.txt` để lấy đúng số liệu (diện tích, giá, sổ đỏ, vị trí).
- Mục tiêu bài đăng: giới thiệu dự án mới, nhắc lại ưu đãi, hay tạo cảm giác khan hiếm/cập nhật tiến độ bán?
- Giờ muốn đăng (nếu không nói, gợi ý khung giờ hay tương tác: ~7h sáng hoặc 19-21h tối).

## Bước 2 — Soạn bài

Dùng đúng biến mà `apply_template()` hỗ trợ nếu bài đăng có cá nhân hóa: `{ho_ten}`, `{du_an}`, `{gia}`, `{dien_tich}` (bài đăng Timeline thường không cá nhân hóa theo `{ho_ten}` vì đăng công khai — chỉ dùng khi thực sự cần).

Tham khảo các mẫu có sẵn trong `mau-bai-dang-zalo.txt` (ví dụ "BÀI 1: GIỚI THIỆU DỰ ÁN MỚI") để giữ đúng văn phong, emoji, và cấu trúc (hook mở đầu → thông tin lô đất bằng bullet có emoji → câu khẳng định thị trường/cơ hội → CTA). Viết bài mới theo cùng khuôn mẫu đó thay vì bịa phong cách khác.

## Bước 3 — Bàn giao

Xuất bài đăng trong khối code, kèm:
- Gợi ý giờ đăng cụ thể (định dạng `HH:MM`) để điền vào ô "Giờ (HH:MM)".
- Nhắc nếu có nhiều ảnh, đường dẫn ảnh cách nhau bằng `;` khi chọn trong tool.
- Hỏi có cần soạn thêm bài luân phiên cho các ngày tiếp theo trong kế hoạch 30 ngày không.

## Lưu ý

- Không cam kết pháp lý/giá trị đầu tư mà không có trong tài liệu gốc (`ke-hoach-ban-dat-30-ngay.txt`) — tránh phát sinh thông tin sai lệch về sổ đỏ, quy hoạch.
- Giữ bài đăng súc tích, tránh trùng lặp gần như 100% với các mẫu đã đăng trước để không bị Zalo/khách hàng nhận diện là spam.
