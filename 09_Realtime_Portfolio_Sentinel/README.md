# PHÒNG BAN 9 — BAN GIÁM SÁT DANH MỤC THỜI GIAN THỰC & ỨNG PHÓ BIẾN ĐỘNG KHẨN CẤP
*(Apex Real-Time Portfolio Sentinel & Intraday Tactical Incident Commander Desk)*

**Tên Định Danh Chuyên Trách**: **"Victor"** — Trưởng Ban Giám Sát Rủi Ro Trong Phiên & Chỉ Huy Tác Chiến Khẩn Cấp.

---

## 1. Sứ Mệnh & Tôn Chỉ Hoạt Động
- **Lá Chắn Bảo Vệ Thời Gian Thực**: Nếu Ban 1-8 đưa ra chiến lược và ban hành lệnh trước phiên (Pre-market), thì Ban 9 ("Victor") trực chiến liên tục từng phút trong phiên để **bảo vệ từng đồng vốn danh mục** trước các biến cố khẩn cấp: flash crash, xả hàng margin call, tin đồn thiên nga đen, mất thanh khoản.
- **Tập Trung 100% Vào Cổ Phiếu Đang Đầu Tư**: Tự động tải và giám sát liên tục toàn bộ các mã đang thực tế giải ngân từ `08_Master_Investment_CIO/master_execution_blotter.json`, `04_Investment_Committee/portfolio_tracker.md` (Mỹ/Toàn cầu) và `VN_Market/04_Investment_Committee/vn_portfolio_tracker.md` (Việt Nam).
- **Phản Ứng Trong Vòng 60 Giây**: Khi có bất kỳ dị thường nào đe dọa cổ phiếu nắm giữ, Victor phát còi báo động đỏ ngay lập tức và triệu tập **Live War-Room** để cùng Nhà đầu tư chốt phương án khắc phục tức thời trong ngày.

---

## 2. Các Lệnh Điều Khiển & Vận Hành Trong Phiên

### A. Quét Kiểm Tra Toàn Bộ Danh Mục 1 Lần (Single-Scan Audit)
Dùng bất kỳ lúc nào để rà soát toàn bộ các vị thế đang nắm giữ:
```powershell
python scripts\intraday_portfolio_sentinel.py --scan-once
```

### B. Chạy Giám Sát Nền Liên Tục Trong Phiên (Intraday Continuous Daemon)
Khởi động Victor chạy ẩn trong suốt thời gian giao dịch, tự động quét mỗi 60 giây (hoặc tham số tùy chọn):
```powershell
python scripts\intraday_portfolio_sentinel.py --daemon --interval 60
```
*Ghi chú*: Nhấn `Ctrl + C` để tạm dừng tiến trình giám sát khi hết giờ giao dịch.

### C. Diễn Tập Tình Huống Khẩn Cấp / Kiểm Thử Còi Báo Động (Emergency Drill)
Mô phỏng tức thời tình huống 1 mã trong danh mục bị đạp mạnh (ví dụ mô phỏng VHM giảm -5.8% hoặc NVDA giảm -4.5%) để kiểm tra còi báo động và quy trình War-Room 60 giây:
```powershell
python scripts\intraday_portfolio_sentinel.py --drill VHM --drop-pct -5.8
```
Hoặc đối với cổ phiếu Mỹ:
```powershell
python scripts\intraday_portfolio_sentinel.py --drill NVDA --drop-pct -4.5
```

---

## 3. Ma Trận Dị Thường Kích Hoạt Còi Báo Động (5 Anomaly Triggers)

| Cấp Độ Cảnh Báo | Tên Dị Thường | Tiêu Chí Kích Hoạt Tức Thời | Hành Động Của Victor |
| :---: | :--- | :--- | :--- |
| **LEVEL 1** | **Intraday Price Shock** | Cổ phiếu giảm nhanh $\ge 2.0\%$ (Vàng) hoặc $\ge 3.5\%$ (Đỏ) trong phiên. | Bật cảnh báo, tính toán áp lực bán và theo dõi nhịp nảy VWAP. |
| **LEVEL 2** | **Stop Loss Proximity** | Giá rơi vào vùng cách ngưỡng cắt lỗ bắt buộc $Stop\ 2xATR$ dưới $1.5\%$. | 🚨 **BÁO ĐỘNG ĐỎ**: Chuẩn bị kích hoạt phương án phòng thủ. |
| **LEVEL 3** | **Whale Dumping / Volume Surge** | Khối lượng khớp lệnh tăng vọt $\ge 2.5x$ trung bình 20 phiên tại vùng giá đỏ. | Cảnh báo cá mập xả hàng, phân tích áp lực lệnh đối ứng. |
| **LEVEL 4** | **Circuit Breaker / Kẹt Sàn (VN)** | Giá giảm $\le -6.5\%$ (sát sàn HOSE -7%), trắng bên mua. | 🔥 **KHẨN CẤP**: Kích hoạt ngay lệnh Short VN30F khóa lỗ T+2.5! |
| **LEVEL 5** | **Black Swan Breaking News** | Phát hiện tin xấu đột ngột (khởi tố, thanh tra, đình chỉ pháp lý,...). | Triệu tập Live War-Room đối soát BCTC và chốt hướng xử lý. |

---

## 4. Chiến Hạm 4 Phương Án Khắc Phục Tức Thời Trong Ngày (Tactical Action Matrix)

Mỗi khi phát còi báo động, Victor lập tức phát hành **"Bản Tin Tác Chiến Khẩn Cấp" (`latest_emergency_alert.md`)** với 4 phương án chuẩn mực:

1. **🛡️ Phương Án A: Synthetic Short Hedge (Vũ khí phòng vệ khóa lỗ T+2.5)**:
   - Dành cho cổ phiếu Việt Nam kẹt T+2.5 không bán được cơ sở: Mở lệnh Short Hợp đồng Tương lai VN30F1M tương ứng với giá trị vị thế và Beta. Lãi Short bù lỗ cơ sở, khóa chặt tài khoản an toàn 100%!
2. **✂️ Phương Án B: Tactical Partial De-risking (Hạ 30% - 50% vị thế)**:
   - Canh nhịp kéo nảy kỹ thuật về vùng VWAP khung M15 để hạ bớt tỷ trọng, giảm áp lực Margin và thu tiền mặt về Dry Powder.
3. **⚡ Phương Án C: T+0 Intra-day Scalp (Lướt sóng hạ giá vốn)**:
   - Bắt đáy rũ bỏ washout tại vùng quá bán cực đại và bán trả ngay lượng hàng có sẵn khi giá hồi phục để hạ giá vốn mà không tăng rủi ro T+.
4. **🧘 Phương Án D: Disciplined Hold & Re-affirm Thesis (Giữ vững kỷ luật)**:
   - Nếu BCTC, FCF của doanh nghiệp vẫn tuyệt đối vững vàng và cú giảm chỉ là tâm lý bầy đàn, kiên quyết giữ vững vị thế.

---

## 5. Hướng Dẫn Thao Tác Thủ Công Cho Nhà Đầu Tư (Manual Setup Guide)

### 📲 Bước 1: Kích Hoạt Cảnh Báo Rung Điện Thoại Qua Telegram (Tùy Chọn Khuyên Dùng)
Để điện thoại của bạn reo chuông/rung báo động ngay khi có biến động trong phiên mà không cần nhìn chằm chằm màn hình máy tính:
1. Mở ứng dụng **Telegram** trên điện thoại, tìm bot `@BotFather` và gõ `/newbot` để tạo 1 bot riêng của bạn (mất 30 giây). Bạn sẽ nhận được `bot_token`.
2. Gửi một tin nhắn bất kỳ cho bot của bạn, sau đó vào link `https://api.telegram.org/bot<TOKEN_CỦA_BẠN>/getUpdates` để lấy `chat_id`.
3. Mở file `09_Realtime_Portfolio_Sentinel/sentinel_config.json`, cập nhật:
   ```json
   "telegram": {
     "enabled": true,
     "bot_token": "TOKEN_CỦA_BẠN",
     "chat_id": "CHAT_ID_CỦA_BẠN"
   }
   ```
4. Kể từ giờ, mỗi khi có biến động nguy hiểm, Victor sẽ gửi tin nhắn khẩn cấp rung điện thoại bạn lập tức!

### 💻 Bước 2: Bật Tiến Trình Giám Sát Khi Mở Phiên Giao Dịch
Vào đầu phiên (09h00 sáng với thị trường VN, hoặc 20h30 tối với thị trường Mỹ), bạn chỉ cần mở terminal PowerShell và chạy:
```powershell
python scripts\intraday_portfolio_sentinel.py --daemon
```
Victor sẽ tự động âm thầm làm việc, bảo vệ danh mục và chỉ lên tiếng khi có biến động thật sự cần bạn ra quyết định.

---

## 6. Hồ Sơ Tài Liệu Của Phòng Ban
- **Cấu hình ngưỡng rủi ro**: `09_Realtime_Portfolio_Sentinel/sentinel_config.json`
- **Bảng trạng thái trực tiếp**: `09_Realtime_Portfolio_Sentinel/live_sentinel_status.md` và `.json`
- **Bản tin báo động khẩn cấp mới nhất**: `09_Realtime_Portfolio_Sentinel/latest_emergency_alert.md`
- **Nhật ký lưu trữ sự cố lịch sử**: `09_Realtime_Portfolio_Sentinel/incident_logs/`
