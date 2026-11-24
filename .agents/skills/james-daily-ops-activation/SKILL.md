---
name: james-daily-ops-activation
description: >-
  Cơ chế kích hoạt một câu toàn bộ 8 mốc tác chiến trong ngày (08:30, 09:00, 11:35, 13:00, 13:30, 14:05, 14:20, 15:45 ICT)
  ngay bên trong phòng chat Antigravity của Master CIO James (hoặc bất kỳ phòng chat nào Chủ tịch chỉ định) bằng tool `schedule`.
---

# Kích Hoạt Tác Vụ Tác Chiến Trong Ngày Tại Phòng Chat James (V7.0)

## 1. Khi nào kích hoạt kỹ năng này?
Khi Chủ tịch nhắn bất kỳ câu lệnh nào mang ý nghĩa kích hoạt lịch trong ngày tại phòng chat (đặc biệt tại phòng **James**), ví dụ:
- *"hãy bật tác vụ tác chiến trong ngày"*
- *"bật lịch tác chiến hôm nay"*
- *"kích hoạt 8 mốc tác chiến"*
- *"bật lịch phòng James"* / *"lên lịch chạy hôm nay đi"*

## 2. Quy Trình Bắt Buộc 4 Bước (Thực Thi Trong 1–2 Lượt, Không Trùng Lịch)

### Bước 1: Chống Trùng Lặp & Đọc Chân Lý Hiện Hành
Chạy song song trong lượt đầu tiên:
1. Gọi `manage_task(Action="list")` để kiểm tra xem đoạn chat này đã có sẵn những lịch `schedule` nào đang chạy chưa.
2. Đọc `00_LIVE_INTER_CHAT_STATE.md` và `data/canonical_executive_briefing.json`.
3. Chạy lệnh:
   ```powershell
   python -X utf8 scripts/james_daily_ops_activator.py --arm-today
   ```
   Lệnh này trả về JSON gồm `is_trading_day`, `upcoming_slots` (các mốc chưa trôi qua tính theo giờ ICT hiện tại) và `passed_slots` (các mốc đã qua trong ngày), mỗi phần tử đã có sẵn `cron_expr` và `prompt` chuẩn xác.

### Bước 2: Tạo Đồng Loạt Các Lịch Còn Lại Ngay Trong Đoạn Chat
- Với mỗi mốc trong `upcoming_slots` **chưa tồn tại** trong kết quả của `manage_task(Action="list")`, gọi song song tool `schedule(...)`:
  - `CronExpression`: giá trị `slot["cron_expr"]` (chạy theo giờ máy `Asia/Ho_Chi_Minh`: `30 8 * * 1-5`, `0 9 * * 1-5`, `35 11 * * 1-5`, `0 13 * * 1-5`, `30 13 * * 1-5`, `5 14 * * 1-5`, `20 14 * * 1-5`, `45 15 * * 1-5`).
  - `Prompt`: giá trị `slot["prompt"]`.
  - `ExactTiming`: `true` (để nổ đúng giờ giao dịch HOSE/HNX không bị trễ jitter).
  - `MaxIterations`: `1` khi Chủ tịch nói *"trong ngày"* / *"hôm nay"* (tránh tích tụ lịch rác qua các ngày khác khi ngày mới Chủ tịch gọi lại lệnh); bỏ qua `MaxIterations` chỉ khi Chủ tịch nói rõ *"bật cố định hàng tuần"*.
  - `IsDaemon`: `false` (giữ mặc định).

> [!NOTE]
> Nếu là ngày nghỉ lễ/cuối tuần (`is_trading_day == false`) hoặc đã qua `15:45`: báo rõ cho Chủ tịch biết các mốc đã hoàn tất/nghỉ lễ hôm nay, và nêu rõ các mốc đã gắn cho phiên giao dịch kế tiếp (`next_trading_day`) theo đúng `cron_expr` Thứ 2–Thứ 6 (`1-5`).

### Bước 3: Chốt Phản Hồi Rõ Ràng & Đứng Chờ Đúng Quy Chuẩn
- Báo cáo Chủ tịch danh sách bảng **tổng các mốc đã bật trong đoạn chat James**, các mốc đã bỏ qua (nếu quá giờ hoặc đã có sẵn), kèm trạng thái danh mục `SSOT 105C307855` mới nhất từ `SCBP`.
- Kết thúc lượt (không gọi thêm tool) để hệ thống tự đánh thức phòng chat James đúng từng cột mốc giờ đã lên.

### Bước 4: Khi Từng Cột Mốc Đến Giờ & Đánh Thức Phòng Chat
- Thực hiện đúng chuỗi lệnh Python trong `Prompt` của mốc đó (`apex_daily_live_warroom_engine.py`, `vn3_portfolio_autonomous_sentinel.py`, `apex_brain_v4_profit_engine.py`, `apex_inspector_trong.py --run-v7-gates`, `palmer_antigravity_sync_bridge.py --sync-current`).
- In bản tin ngắn gọn 4 phần trực diện ngay trong đoạn chat James, không cần vòng lặp poll.
