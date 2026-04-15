# HƯỚNG DẪN SỬ DỤNG CLAUDE CODE ROUTINES CHO KINH DOANH BẤT ĐỘNG SẢN
## Áp dụng thực tế: Bán đất nền Sóc Sơn, Hà Nội

---

## 1. ROUTINES LÀ GÌ?

**Claude Code Routines** là tính năng tự động hóa trên `claude.ai/code` cho phép bạn:
- Lên lịch tác vụ chạy **tự động theo giờ/ngày/tuần**
- Kích hoạt bởi **sự kiện** (GitHub, webhook, API)
- Claude sẽ tự thực hiện công việc **mà không cần bạn ngồi gõ lệnh**

### Các loại Trigger (kích hoạt):
| Loại | Mô tả | Ứng dụng BĐS |
|------|-------|--------------|
| **Schedule** | Chạy theo lịch cron (giờ cố định) | Gửi tin Zalo lúc 7h sáng mỗi ngày |
| **GitHub event** | Khi có sự kiện GitHub (PR, commit) | Khi cập nhật danh sách lô đất mới |
| **API** | Gọi từ code/ứng dụng bên ngoài | Kích hoạt chiến dịch từ file Excel |

---

## 2. TẠI SAO BẠN CẦN ROUTINES CHO BĐS?

Bạn đang bán **2 lô đất tại Phú Tằng, Sóc Sơn** và cần:
- Gửi tin nhắn Zalo **đúng giờ vàng** (7h-9h sáng, 19h-21h tối)
- **Thay nội dung** bài đăng liên tục để tránh spam
- Theo dõi khách hàng tiềm năng **24/7**
- Tổng hợp **báo cáo ngày** tự động

Làm thủ công: Mất 2-3 giờ/ngày
Với Routines: Chỉ cần setup 1 lần, hệ thống tự chạy

---

## 3. THIẾT LẬP ROUTINES CỤ THỂ CHO BẠN

### ROUTINE 1: Chiến dịch Zalo buổi sáng (7:00 sáng)

**Tên:** `zalo-sang-bat-dong-san`

**Prompt:**
```
Đọc file danh-sach-khach.csv, chọn ngẫu nhiên 1 trong 5 mẫu bài đăng 
từ mau-bai-dang-zalo.txt, thay thế biến:
- {du_an} = "Phú Tằng - Đa Phúc - Sóc Sơn"
- {gia} = "1.66 tỷ (Lô 1) hoặc 2.21 tỷ (Lô 2 - góc)"
- {dien_tich} = "83m2 và 88.5m2"
Sau đó chạy zalo-tool/main.py để gửi tin nhắn hàng loạt.
Ghi log vào zalo-tool/data/log_ngay.txt
```

**Cron:** `0 7 * * *` (7h00 sáng mỗi ngày)

---

### ROUTINE 2: Chiến dịch Zalo buổi tối (19:30)

**Tên:** `zalo-toi-follow-up`

**Prompt:**
```
Đọc log trong ngày từ zalo-tool/data/log_ngay.txt.
Tìm khách hàng đã xem tin nhưng chưa phản hồi.
Soạn tin nhắn follow-up cá nhân hóa cho từng người.
Gửi vào lúc 19h30 qua Zalo Tool.
```

**Cron:** `30 19 * * *` (19h30 mỗi ngày)

---

### ROUTINE 3: Báo cáo cuối ngày (21:00)

**Tên:** `bao-cao-ngay`

**Prompt:**
```
Đọc log Zalo hôm nay, tổng hợp:
1. Số tin đã gửi
2. Số người phản hồi
3. Khách nào hỏi về Lô 1 / Lô 2
4. Khách nào cần follow-up ngày mai
5. Đề xuất nội dung bài đăng cho ngày mai

Lưu báo cáo vào bao-cao/ngay-YYYY-MM-DD.txt
```

**Cron:** `0 21 * * *` (21h00 mỗi ngày)

---

### ROUTINE 4: Cập nhật nội dung tuần (Thứ 2, 8h sáng)

**Tên:** `cap-nhat-noi-dung-tuan`

**Prompt:**
```
Dựa trên ke-hoach-ban-dat-30-ngay.txt và kết quả tuần qua,
soạn 5 bài đăng Zalo MỚI cho tuần này.
Cập nhật vào mau-bai-dang-zalo.txt (giữ lại 5 bài cũ, thêm 5 bài mới).
Thay đổi góc độ tiếp cận:
- 2 bài: Nhấn mạnh vị trí Sóc Sơn - Nội Bài
- 2 bài: So sánh giá với Đông Anh, Gia Lâm  
- 1 bài: Câu chuyện khách hàng thành công
```

**Cron:** `0 8 * * 1` (8h sáng Thứ Hai)

---

### ROUTINE 5: API Trigger - Kích hoạt từ Excel/Điện thoại

**Tên:** `kich-hoat-chien-dich-gap`

**Mô tả:** Khi bạn có khách VIP hoặc muốn gửi tin khẩn

**Cách dùng:**
```bash
# Gọi từ terminal hoặc tích hợp vào app
curl -X POST https://hooks.routines.dev/r/kich-hoat-chien-dich-gap \
  -H "Authorization: Bearer rt_live_YOUR_TOKEN" \
  -d '{"lo": "2", "gia_uu_dai": "2.1 ty", "ly_do": "chu nha can tien gap"}'
```

**Prompt:**
```
Nhận thông tin từ API: lô đất, giá ưu đãi, lý do urgent.
Soạn tin nhắn "ưu đãi khẩn" cho top 20 khách tiềm năng nhất.
Gửi ngay lập tức qua Zalo Tool.
```

---

## 4. HƯỚNG DẪN TẠO ROUTINE TỪNG BƯỚC

### Bước 1: Truy cập claude.ai/code
### Bước 2: Nhấn **"New routine"**
### Bước 3: Điền thông tin:
- **Name:** Tên routine (vd: `zalo-sang-bat-dong-san`)
- **Prompt:** Lệnh Claude cần thực hiện (copy từ mục 3 trên)
- **Repository:** Chọn `duc041318/camscanner-ai-tools`
- **Trigger:** Chọn **Schedule** → nhập cron expression

### Bước 4: Lấy URL webhook (cho API trigger)
- Copy URL dạng: `https://hooks.routines.dev/r/ten-routine`
- Lưu Token: `rt_live_xxxxx`

### Bước 5: Test thủ công trước khi để tự động

---

## 5. LỊCH CHẠY TỔNG HỢP TRONG NGÀY

```
06:50 - Kiểm tra danh sách khách (chuẩn bị)
07:00 - [ROUTINE 1] Gửi Zalo buổi sáng ← QUAN TRỌNG NHẤT
12:00 - (tùy chọn) Đăng bài trên Facebook/Zalo Feed
19:30 - [ROUTINE 2] Follow-up khách chưa phản hồi
21:00 - [ROUTINE 3] Báo cáo tổng kết ngày
Thứ 2 - [ROUTINE 4] Làm mới nội dung tuần mới
Bất kỳ lúc nào - [ROUTINE 5] API trigger khi có nhu cầu khẩn
```

---

## 6. KẾT QUẢ KỲ VỌNG

Với plan 30 ngày hiện tại (28/03 - 27/04/2026):

| Chỉ số | Thủ công | Với Routines |
|--------|----------|--------------|
| Tin nhắn/ngày | 50-100 | 300-500 |
| Giờ làm việc/ngày | 3-4 giờ | 30 phút |
| Tỷ lệ phản hồi | ~3% | ~8-12% |
| Leads tiềm năng/tuần | 5-10 | 20-40 |

**Mục tiêu: Bán cả 2 lô trước ngày 27/04/2026**
- Lô 1 (83m2): 1.66 tỷ
- Lô 2 góc (88.5m2): 2.21 tỷ

---

## 7. LƯU Ý QUAN TRỌNG

1. **Giờ vàng Zalo:** 7h-9h sáng và 19h-21h tối - tỷ lệ đọc cao nhất
2. **Luân phiên nội dung:** Dùng ít nhất 5 mẫu khác nhau để tránh bị đánh dấu spam
3. **Cá nhân hóa:** Gọi đúng tên khách = tăng 40% tỷ lệ phản hồi
4. **Không spam:** Mỗi số điện thoại chỉ nhắn tối đa 1 lần/ngày
5. **Follow-up:** Khách hỏi nhưng chưa mua = cơ hội lớn nhất, cần chăm sóc đặc biệt

---

*Tài liệu được tạo bởi Claude Code - Cập nhật: 2026-04-15*
*Áp dụng cho dự án: Phân lô Phú Tằng, Đa Phúc, Sóc Sơn, Hà Nội*
