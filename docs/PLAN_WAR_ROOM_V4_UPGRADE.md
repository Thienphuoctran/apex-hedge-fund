# KẾ HOẠCH TRIỂN KHAI NÂNG CẤP TOÀN DIỆN HỆ THỐNG APEX & PHÒNG TÁC CHIẾN THỜI GIAN THỰC (WAR-ROOM V4.0)

- **Ngày lập kế hoạch:** 2026-11-13 (Chủ tịch Trần Quốc Thiên Phước phê duyệt giữ lại để triển khai ngay khi hạn mức Weekly Token Gemini được reset vào trưa 2026-11-14)
- **Tài khoản SSOT:** TCBS `105C307855` — Hiện nắm giữ `12,516,471 ₫` Cash (`69.0%`) + `200 CP` (`100 HDB`, `100 MSH` = `5,635,000 ₫`, `31.0%`), Tổng NAV `18,151,471 ₫`.
- **Cổng Portal:** `https://apex-hedge-fund.onrender.com`

---

## GIAI ĐOẠN 1: NÂNG CẤP PHÒNG TÁC CHIẾN THỜI GIAN THỰC (REAL-TIME ADAPTIVE WAR-ROOM V4.0)
*(Triển khai trực tiếp trên codebase hiện có — Không cần dịch vụ trả phí mới)*

### 1.1. Tầng Dữ Liệu Bảng Điện & Chỉ Số Sống 100% (`scripts/vietnam_realtime_feed.py` + `scripts/apex_tactical_war_room_engine.py`)
- **Xóa bỏ 100% số giả lập cứng trong `get_live_market_overview()`:** Thay các số mock (`VN-Index 1,258.62`, `VN30 1,324.95`, `GTGD 14,820 Tỷ`, `Khối ngoại +52.6 Tỷ`, `242 Tăng / 145 Giảm`) bằng dữ liệu sống từ cổng API chỉ số sàn (VN-Index, VN30, HNX, VN30F1M để tính **Basis phái sinh live**), độ rộng Tăng/Giảm, GTGD và Mua/Bán ròng Khối ngoại.
- **Volume Pace Ratio (Tốc độ thanh khoản theo khung giờ):** So sánh thanh khoản lũy kế tính tới phút hiện tại với bình quân 20 phiên cùng khung giờ.
- **Bóc tách 3 bước giá & Buy-Up Ratio thực:** Đọc đầy đủ `g1..g6` từ VPS Datafeed (`fetch_vps_quotes`) + đo tỷ lệ lệnh khớp chủ động bên Bán (Buy-Up %) thực thay cho giá trị tĩnh `52.4% / 56.8%`.
- **Watchlist động hợp nhất SSOT:** Tự động gộp `[Mã đang giữ trong current_portfolio_state.json]` + `[Top Watchlist trong VN_Market/07_Daily_Specialist/vn_daily_ledger.json & 08_Master_Investment_CIO/master_execution_blotter.json]` (loại bỏ cố định 4 mã cũ `HDB, MSH, BAF, IDC`).

### 1.2. Động Cơ Tái Tính Toán Quyết Định & Báo Cáo Sống (`scripts/apex_live_intraday_brain.py`)
- **Chạy quét mỗi 15–30 giây trong giờ giao dịch (09:00–14:45 ICT):**
  - Tự động tính **PnL sống từng giây**, khoảng cách % tới **Stop Loss 2xATR**, khoảng cách tới **TP1 / TP2** cho danh mục nắm giữ (`GIỮ NGUYÊN` / `NÂNG TRAILING STOP VỀ HÒA VỐN` / `CHỐT LỜI 50% TP1` / `CẢNH BÁO CẮT LỖ KHẨN`).
  - Tự động chuyển trạng thái cho mã tầm ngắm (`ĐỨNG NGOÀI` ➔ `TIỆM CẬN VÙNG MUA` ➔ `HOÃN/HỦY KÈO NẾU THỊ TRƯỜNG XẤU`).
- **Cập nhật liên tục Cột Trái (Kế Hoạch Đầu Ngày -> Kế Hoạch Động) & Cột Giữa (Living Intraday Tactical Report):**
  - Đọc động kế hoạch sáng từ `vn_daily_ledger.json` & `master_execution_blotter.json` thay cho HTML cứng (`HDB 22,100–22,450`, `20,167,119 đ`...).
  - Đánh giá **Market Regime Intraday** (`RISK_ON_BREAKOUT` / `SIDEWAY_CHOPPY` / `DEFENSIVE_SELLOFF`) để tự động đổi khuyến nghị & tỷ trọng hành động ngay trong phiên khi có biến số mới.
  - Ghi nhận thành file báo cáo thật `VN_Market/07_Daily_Specialist/YYYY-MM-DD_Live_Intraday_Report.md` và đồng bộ thẳng vào `data/apex_institutional_vault.db` (SQLite Vault) sau mỗi nhịp biến động lớn hoặc mỗi 30 phút.
- **Sửa các chuỗi tĩnh còn sót:** Loại bỏ câu chào cứng `20,167,119 ₫ (100% Cash)` trong `load_directives_history()` (dòng 472 `apex_tactical_war_room_engine.py`) và đồng bộ `get_weekly_reference_roadmap()` động theo tuần hiện tại.

### 1.3. Cross-Report Event Hook & Streaming Realtime
- **Nối sự kiện liên phòng ban:** Khi `cbtt_filings_radar.py` (Ban 10) hoặc `intraday_portfolio_sentinel.py` (Ban 9) phát hiện tin BCTC / biến động >= ±2%, tự động kích hoạt recalc kế hoạch War-Room + đẩy cảnh báo lên khung chat War-Room & Telegram.
- **Streaming SSE:** Bổ sung endpoint `GET /api/tactical_war_room/stream` (Server-Sent Events) kèm cache tick 3–5 giây để bảng giá, PnL, báo cáo tác chiến và radar 5 cấp độ tự cập nhật mượt trên trình duyệt không giật.

### 1.4. Công Cụ Đồng Bộ Nhanh TCInvest & Sửa Audit Cũ
- **Form "1-Click Sync TCInvest" trên Portal:** Nhập `MÃ | MUA/BÁN | SL | GIÁ` (hoặc đối soát sao kê) ➔ tự tính lại tiền mặt sau phí/thuế, giá vốn, Stop 2xATR, TP1/TP2 và ghi thẳng vào `data/current_portfolio_state.json`.
- **Sửa `scripts/comprehensive_system_audit.py`:** Chuyển kiểm toán SSOT từ số cứng `20,167,119 ₫ / 0 CP` sang kiểm toán nhất quán động giữa SSOT ↔ Health API ↔ War-Room ↔ Master Blotter.

---

## GIAI ĐOẠN 2: NÂNG CẤP LIÊN THỊ TRƯỜNG, CLOUD DB BỀN VỮNG & BẢO MẬT
1. **Cầu nối Phiên Đêm Mỹ → Trước ATO VN (`Global-to-VN Spillover Engine`):** Dùng kết quả phiên Mỹ của Alex (S&P 500, DXY, US10Y, Oil, VNM/EEM ETF) làm hệ số điều chỉnh trần rủi ro giải ngân cho Minh Quân trước 08h30 sáng.
2. **Hồi tố Thực Thi (`Live Signal vs Execution Slippage Tracker`):** Đối chiếu hiệu quả tín hiệu Khung Giờ Vàng sau T+3 / T+5 để tự động tinh chỉnh điều kiện lọc Bull-Trap.
3. **Cloud DB Bền Vững (Supabase Postgres):** Lưu SSOT, nhật ký chỉ thị War-Room và báo cáo live lên Postgres để **không bao giờ mất trạng thái trong ngày** khi Render Free Tier ngủ đông hoặc redeploy.
4. **Bảo Mật Portal (`PIN / Bearer Token Auth`):** Bảo vệ toàn bộ trang điều hành `apex-hedge-fund.onrender.com` bằng lớp xác thực cookie `HttpOnly`.
5. **Keep-Alive Ping trong giờ giao dịch (08:25 – 15:00 ICT, T2–T6):** Ping `/api/health` mỗi 10 phút qua GitHub Actions để Render luôn thức xuyên suốt phiên.
