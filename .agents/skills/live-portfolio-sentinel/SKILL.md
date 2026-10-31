---
name: live-portfolio-sentinel
description: >-
  Quy trình vận hành Ban 9 — Ban Giám Sát Danh Mục Thời Gian Thực & Ứng Phó Biến Động Khẩn Cấp ("Victor"). Quét liên tục thị trường trong phiên đối với toàn bộ cổ phiếu đã đầu tư, kích hoạt báo động khẩn cấp và lập phương án khắc phục tức thời trong ngày (Synthetic Short Hedge VN30F, T+0 Scalp, De-risking).
---

# Quy Trình Vận Hành Ban 9 — Giám Sát Danh Mục Trong Phiên & Ứng Phó Khẩn Cấp (Live Sentinel Pipeline)

Kỹ năng này vận hành **Phòng Ban 9 ("Victor")** — chốt chặn phòng thủ thời gian thực của quỹ, đảm bảo mọi biến động bất thường đối với cổ phiếu trong danh mục đều được phát hiện ngay lập tức và giải quyết trong ngày.

---

## 1. Các Chế Độ Chạy Lệnh Nhanh

### Chế độ 1: Quét Rà Soát Tức Thời 1 Lần (Single-Scan Audit)
Dùng để kiểm tra nhanh toàn bộ danh mục ngay lúc này xem có mã nào đang bị đe dọa không:
```powershell
python scripts\intraday_portfolio_sentinel.py --scan-once
```

### Chế độ 2: Chạy Giám Sát Nền Liên Tục Trong Phiên (Continuous Live Daemon)
Victor sẽ chạy ẩn trong nền, tự động lấy dữ liệu định kỳ mỗi 60 giây (hoặc tham số tùy chọn) trong suốt thời gian giao dịch:
```powershell
python scripts\intraday_portfolio_sentinel.py --daemon --interval 60
```

### Chế độ 3: Diễn Tập Khẩn Cấp / Mô Phỏng Biến Động Kịch Sàn (Simulation Drill)
Dùng để kiểm thử còi báo động và quy trình lập phương án khắc phục 60 giây đối với 1 mã cụ thể (ví dụ mô phỏng NVDA hoặc VHM bị đạp -5.5%):
```powershell
python scripts\intraday_portfolio_sentinel.py --drill VHM --drop-pct -5.8
```
Hoặc mã quốc tế:
```powershell
python scripts\intraday_portfolio_sentinel.py --drill NVDA --drop-pct -4.5
```

---

## 2. Quy Trình Vận Hành 4 Bước Khi Xảy Ra Sự Cố

### Bước 1: Phát Hiện Dị Thường Trong Phiên
- Victor quét giá hiện tại, khối lượng giao dịch đột biến, và khoảng cách đến ngưỡng cắt lỗ $Stop\ 2xATR$.
- Phân loại mức độ nguy hiểm theo Ma trận 5 Cấp độ (Level 1 đến Level 5).

### Bước 2: Kích Hoạt Còi Báo Động Đỏ (Red Alert Broadcast)
- Xuất còi âm thanh và banner cảnh báo màu đỏ trên màn hình console.
- Cập nhật bản tin khẩn cấp tại: `09_Realtime_Portfolio_Sentinel/latest_emergency_alert.md`.
- Gửi tin nhắn Telegram / Webhook tới điện thoại của Nhà đầu tư (nếu đã cấu hình token).

### Bước 3: Triệu Tập Live War-Room & Khắc Phục Tức Thời
Nhà đầu tư và Victor cùng đối soát bảng 4 Phương Án Khắc Phục:
1. **Short Phái Sinh VN30F1M** (nếu mã VN kẹt T+2.5 không bán được cơ sở).
2. **Cắt lỗ chủ động 30% - 50%** tại nhịp nảy kỹ thuật VWAP.
3. **Lướt sóng đảo hàng T+0** trên lượng hàng có sẵn để hạ giá vốn.
4. **Kiên định nắm giữ (Hold)** nếu BCTC vững vàng và đà giảm chỉ là tin đồn thất thiệt.

### Bước 4: Lưu Trữ Hồ Sơ Sự Cố & Tự Học
- Toàn bộ diễn biến và quyết định xử lý được tự động lưu vào `09_Realtime_Portfolio_Sentinel/incident_logs/` để Ban 5 (Performance Learning) hồi tố và hoàn thiện phản xạ cho các phiên sau.
