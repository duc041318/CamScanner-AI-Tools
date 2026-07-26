---
name: loi-moi-ket-ban
description: >
  Soan loi chao ngan khi gui loi moi ket ban Zalo tu dong, dung cho tab
  "Ket ban tu dong" cua zalo-tool. Dung khi nguoi dung muon tao loi gioi thieu
  ket ban, soan greeting message cho tinh nang ket ban tu dong, hoac can noi
  dung cho add_friend.
---

# Skill: Soạn lời chào kết bạn cho zalo-tool

Soạn lời nhắn giới thiệu ngắn để dán vào ô "Lời nhắn giới thiệu" của tab **Kết bạn tự động** trong `zalo-tool/main.py`.

## Bước 1 — Thu thập thông tin

Hỏi người dùng (nếu chưa cung cấp):
- Đối tượng mục tiêu (khu vực, nhóm khách hàng) để lời chào phù hợp.
- Có muốn nhấn mạnh dự án cụ thể ngay từ lời mời kết bạn không, hay chỉ giới thiệu chung chung (khuyến nghị: giữ chung chung, vì lời mời kết bạn không phải chỗ chốt sale).

## Bước 2 — Soạn lời chào

Nguyên tắc:
- Rất ngắn (1-2 câu), vì đây là ấn tượng đầu và hiển thị hạn chế trong lời mời kết bạn Zalo.
- Dùng biến `{ho_ten}` để cá nhân hóa nếu file danh sách SĐT có cột `ho_ten`.
- Giọng thân thiện, không quảng cáo trực tiếp giá/lô đất — mục tiêu là được chấp nhận kết bạn trước, bán hàng để sau.

## Bước 3 — Bàn giao

Xuất lời chào trong khối code, và nhắc:
- Giới hạn mặc định trong code (`daily_limit=20`) là 20 lời mời/ngày để tránh bị Zalo khóa tài khoản — không đề xuất tăng số này trừ khi người dùng chủ động yêu cầu và hiểu rủi ro.
- Định dạng file danh sách SĐT giống các tính năng khác: `.txt` (1 SĐT/dòng) hoặc `.csv` (cột `sdt` + `ho_ten` nếu cần cá nhân hóa).

## Lưu ý

- Không soạn lời chào có nội dung nhạy cảm/spam rõ ràng (link, số điện thoại khác, giá cụ thể) vì dễ bị Zalo chặn ở bước kết bạn.
