# 🛡️ NHẬT KÝ GIÁM SÁT SPILLOVER QUA ĐÊM — PHƯƠNG ÁN 1B (`17–18/11/2026`)
- **Phòng ban:** Ban 9 — Victor Realtime Sentinel
- **Tài khoản giám sát (SSOT):** TCBS `105C307855` (`HDB` 100 CP @ `22,400đ` Stop `22,060đ`; `MSH` 100 CP @ `35,050đ` Stop `33,090đ`; `BAF` 100 CP `T+0` @ `31,300đ` Stop `30,050đ` chờ về chiều `19/11`)
- **Mục tiêu:** Theo dõi đủ 4 nhịp Mỹ (`21:30`, `22:30`, `01:00`, `04:00`) làm căn cứ lượng hóa rủi ro gap sáng `18/11` (không kết luận sớm trước khi đủ dữ liệu).

## Bảng Ghi Nhận Thời Gian Thực

| Nhịp | Thời điểm (ICT) | VIX | US10Y | WTI | VNM ETF | EEM ETF | ^DJI | ^IXIC | Trạng thái đánh giá |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| Pre-Market | 21:10:47 (17/11) | 23.05 (+0.74%) | 5.145% | $87.06 (+2.41%) | 16.81 (-0.41%) | — | — | — | Khởi động bộ theo dõi |
| Nhịp 1/4 (`21:30_OPEN`) | 21:30:32 (17/11) | 22.92 (+0.17%) | 5.147% (+0.51%) | $87.28 (+2.67%) | 16.81 (-0.41%) | 58.53 (-0.74%) | -0.82% | -0.09% | Ghi nhận log; giữ trực tới 22:30 |
| Nhịp 2/4 (`22:30_POST_AMATEUR`) | 22:30:23 (17/11) | 22.78 (-0.44%) | 5.145% | $86.71 (+2.00%) | 16.765 (-0.68%) | 58.285 (-1.16%) | — (`^GSPC -0.49%`) | -0.53% | `TSM -3.90%`, `NVDA -1.78%`; `Spillover mult 0.65x -> 0.50x (MaxAlloc 25%)`; chờ 01:00 |
| Nhịp 3/4 (`01:00_RED_ALERT`) | 01:00:23 (18/11) | **25.69 (+12.28% vs prev / +12.77% vs 22.78)** | 5.093% (-0.55%) | — | 16.665 (-1.27%) | 58.18 (-1.34%) | -1.55% (`50830.02`) | -1.16% (`24231.89`) | **🚨 BÁO ĐỘNG ĐỎ (`VIX > 24`, `task-8611`)**: `^GSPC 7330.40 (-1.21%)`, `BTC $63,717 (-1.70%)`, 12/12 ngành đỏ (`SMH -1.74%`, `XLF -1.50%`, `MSFT -3.71%`); chờ nến 04:00 |
| Nhịp 4/4 (`04:00_OFFICIAL_CLOSE`) | 04:02:00 (18/11) | **25.89 (+13.01%, đỉnh 27.73)** | 5.103% (-0.35%) | $85.67 (-0.06%) | 16.665 (-0.86%) | 58.28 (-1.04%) | -1.64% | -0.74% | **ĐÓNG CỬA CHÍNH THỨC**: `^GSPC 7,340.73 (-1.02%)`, `XLF -1.89%`, `SMH -0.39%` (rút chân), `DXY 103.50 (-0.05%)`; chốt báo cáo Sentinel `04h05` |

### Mục `22:30_POST_AMATEUR` (Nhịp 2/4 — 22:30:23 ICT)
- **Dữ liệu sống ghi nhận:** `EEM 58.285 (-1.16%)`, `VNM 16.765 (-0.68%)`, `^IXIC -0.53%`, `^GSPC -0.49%`, `TSM -3.90%`, `NVDA -1.78%`, `US10Y 5.145%`, `WTI $86.71 (+2.00%)`, `^VIX 22.78 (-0.44%)`.
- **Điều chỉnh hệ số phòng thủ:** `Spillover mult` tự động hạ từ `0.65x -> 0.50x (MaxAlloc 25%)`.
- **Khóa bảo vệ 3 vị thế:** Giữ nguyên ngưỡng Stop `HDB (22,060đ)`, `MSH (33,090đ)`, `BAF (30,050đ — T+0 chờ về chiều 19/11)`; tiếp tục trực chiến chờ Nhịp 3/4 lúc `01:00` ICT.

### 🚨 BÁO ĐỘNG ĐỎ NHỊP 3/4 (`01:00:23 ICT — 18/11/2026`) — CẢNH BÁO RỦI RO GAP SÁNG `18/11` (`task-8611`)
- **Kích hoạt ngưỡng `VIX > 24`:** `^VIX` vọt `+12.77%` từ `22.78` lên **`25.69`** (`+12.28% vs prev`).
- **Tín hiệu Flight-to-Safety diện rộng:** Cầu trú ẩn đẩy `US10Y` lùi về `5.093% (-0.55%)` và vàng nhích lại; xả đồng loạt cổ phiếu & crypto: `^GSPC 7330.40 (-1.21%)`, `^IXIC 24231.89 (-1.16%)`, `^DJI 50830.02 (-1.55%)`, `BTC $63,717 (-1.70%)`, `VNM 16.665 (-1.27%)`, `EEM 58.18 (-1.34%)`, **12/12 ngành GICS đỏ** (`SMH -1.74%`, `XLF -1.50%`, `MSFT -3.71%`).
- **Đánh giá rủi ro gap sáng `18/11` trên 3 vị thế (trước phiên họp `04h05`, vẫn chờ nến đóng cửa `04h00`):**
  1. **`HDB` (100 CP @ `22,400đ` | Bảo vệ hòa vốn `22,060đ` | Đệm `+1.52%` — RỦI RO CAO NHẤT):** `XLF -1.50%` và `VNM -1.27%` tạo áp lực trực tiếp lên nhóm Bank mở cửa ATO/sáng `18/11`; khoảng đệm `+1.52%` rất mỏng, có nguy cơ cao kiểm định hoặc xuyên `22,060đ` nếu gap giảm `>= 1.5%`. Cần sẵn sàng kích hoạt cắt/bảo vệ hòa vốn hoặc Phương án B/A nếu xảy ra contagion.
  2. **`BAF` (100 CP `T+0` @ `31,300đ` | Stop `30,050đ` | Đệm `+3.99%` — KẸT `T+`):** Hàng chưa về tài khoản (chờ chiều `19/11`), không thể bán cơ sở sáng `18/11`; nếu gap sáng mở rộng về vùng Stop `30,050đ`, cần đánh giá Phương án A (`Synthetic Short Hedge VN30F1M`) hoặc giữ kỷ luật theo BCTC/nến `04h00`.
  3. **`MSH` (100 CP @ `35,050đ` | Stop `33,090đ` | Đệm `+5.59%`):** Biên an toàn rộng nhất trong 3 mã, tiếp tục giám sát phản ứng cầu tại vùng hỗ trợ.
- **Trạng thái trực chiến:** Đã gắn cờ **`RED_ALERT_GAP_RISK_18_11`**, tiếp tục trực tới nến đóng cửa Mỹ **`04h00` (Nhịp 4/4)** để hoàn tất số liệu báo cáo cuộc họp **`04h05`** sáng nay.

### 📊 BÁO CÁO SENTINEL LÚC `04h05` (`04:00_OFFICIAL_CLOSE` — 18/11/2026)
- **Bức tranh đóng cửa Mỹ (`04:00` ICT):** `^VIX` chốt **`25.89 (+13.01%)`** sau khi đạt đỉnh **`27.73`**, `^GSPC 7,340.73 (-1.02%)`, `^IXIC -0.74%` (`SMH` rút chân còn `-0.39%`), `^DJI -1.64%`, đặc biệt **`XLF` (Bank Mỹ) giảm sâu `-1.89%`**; điểm sáng là `VNM 16.665 (-0.86%)`, `EEM 58.28 (-1.04%)`, `^TNX 5.103% (-0.35%)`, `DXY 103.50 (-0.05%)`, `WTI $85.67 (-0.06%)` đều hạ nhiệt áp lực tỷ giá/lạm phát so với nhịp `01h00`.
- **(1) Đánh giá rủi ro Gap sáng `18/11` (`09h00 ATO`) theo từng mã:**
  1. **`HDB` (100 CP @ `22,400đ` | Bảo vệ hòa vốn `22,060đ`, đệm `+1.52%`) — RỦI RO CAO:** `XLF -1.89%` + `^VIX 25.89` tạo áp lực trực tiếp lên nhóm Ngân hàng ngay ATO; dự báo nguy cơ gap giảm `-0.9%` đến `-1.6%` (vùng `22,050đ – 22,200đ`), áp sát/chạm ngay ngưỡng bảo vệ `22,060đ`. Lợi thế: hàng đã sẵn sàng bán (`HOLDING_T0_AVAILABLE`).
  2. **`MSH` (100 CP @ `35,050đ` | Stop `33,090đ`, đệm `+5.59%`) — RỦI RO THẤP–TRUNG BÌNH:** `DXY` dịu về `103.50` và `^IXIC` rút chân giúp nhóm xuất khẩu ít chịu cú sốc trực diện; dự kiến rung lắc ATO `-0.5%` đến `-1.2%` (`~34,600đ – 34,850đ`), còn rất xa ngưỡng Stop `33,090đ`.
  3. **`BAF` (100 CP `T+0` @ `31,300đ` chờ về chiều `19/11` | Stop `30,050đ`, đệm `+3.99%`) — RỦI RO TRUNG BÌNH + BỊ ĐỘNG `T+`:** Ít tương quan với `XLF` nhưng có thể bị vạ lây tâm lý ATO (`-0.8%` đến `-1.5%`, vùng `30,850đ – 31,050đ`), vẫn giữ đệm `~2.6%–3.3%` trên Stop `30,050đ`; nhược điểm là khóa giao dịch tới chiều `19/11`.
- **(2) Kịch bản kích hoạt Stop / Bảo toàn lãi & Điều kiện Victor bấm còi Báo động Đỏ trong phiên `18/11`:**
  - **Điều kiện bấm còi RED ALERT tức thì:** (i) Giá tiến vào vùng cận Stop `<= 1.5%` (`HDB <= 22,390đ` — chỉ cần nhích đỏ nhẹ từ `22,400đ`; `MSH <= 33,590đ`; `BAF <= 30,500đ`); (ii) Rơi nhanh intraday `>= 2.5%–3.5%` hoặc thủng VWAP kèm Vol `>= 2.5x` MA20 (cảnh giác khung `13h00–13h45`); (iii) Mất thanh khoản / chất bán sàn.
  - **Hành động chuẩn bị (Điều 8 — Chủ tịch bấm lệnh):** Không bán hoảng loạn ATO `09h00–09h15`; với **`HDB`**, nếu sau `09h30` (hoặc `14h00–14h25`) gãy `22,060đ` kèm Vol xả lớn ➔ kích hoạt cắt bảo vệ hòa vốn (`Phương án B/cắt dứt điểm`), giữ vững trên `22,100đ` ➔ `Phương án D`; **`MSH`** giữ kỷ luật tới khi vi phạm `33,090đ`; **`BAF`** nếu thị trường bán tháo kéo giá xuyên `30,500đ` / chạm `30,050đ` khi chưa có hàng ➔ bật War-Room cân nhắc `Phương án A (Synthetic Short Hedge VN30F1M)` khóa rủi ro tới chiều `19/11`.
