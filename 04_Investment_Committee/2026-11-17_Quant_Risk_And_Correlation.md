# [BAN 4 — QUANT RISK] BÁO CÁO MA TRẬN TƯƠNG QUAN, ĐỊNH CỠ VỊ THẾ & KIỂM THỬ SỨC CHỊU ĐỰNG (STRESS TEST)
**Ngày kiểm toán**: 2026-11-17  
**Công cụ định lượng**: `scripts/quant_portfolio_engine.py` (v5.0 Audited — 0 Imminent Earnings Violations, Chandelier Stop & ATR Risk-Parity)

---

## 1. Tổng Quan Chỉ Số Rủi Ro Danh Mục (Portfolio Risk Telemetry)
- **Tỷ trọng Cổ phiếu / Tiền mặt (T-Bills ~5%)**: **`60.0% Cổ phiếu` / `40.0% Tiền mặt`**
- **Hệ số Beta Danh mục Tổng hợp (Portfolio Weighted Beta vs S&P 500)**: **`0.33`** *(Thấp hơn đáng kể so với biến động thị trường chung 1.00)*
- **Kiểm soát Cụm Bán dẫn (`NVDA + TSM`)**: **`2.4% NAV`** *(Tuân thủ trần `<= 14.0% NAV`)*
- **Tổng rủi ro danh mục nếu toàn bộ 10 vị thế đồng loạt chạm Stop-Loss `2xATR(14)`**: **`-3.21% NAV`**
- **Số mã bị khóa mua mới do sát lịch BCTC (`0 <= days_to_earnings <= 7`)**: **`2 mã`** (`WMT, NVDA`)

---

## 2. Ma Trận Tương Quan Lợi Suất 1 Năm (`Pairwise Return Correlation Matrix`)

| Mã | **`MSFT`** | **`TSM`** | **`JPM`** | **`OXY`** | **`PG`** | **`JNJ`** | **`V`** | **`ABBV`** | **`COST`** | **`XOM`** |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`MSFT`** | `1.00` | 0.17 | 0.13 | -0.11 | -0.11 | -0.16 | 0.21 | -0.10 | -0.06 | -0.16 |
| **`TSM`** | 0.17 | `1.00` | 0.17 | -0.20 | -0.19 | -0.17 | -0.07 | -0.13 | -0.23 | -0.20 |
| **`JPM`** | 0.13 | 0.17 | `1.00` | -0.14 | 0.10 | 0.16 | 0.35 | 0.07 | -0.01 | -0.10 |
| **`OXY`** | -0.11 | -0.20 | -0.14 | `1.00` | -0.17 | -0.01 | -0.12 | 0.01 | 0.04 | **0.76** |
| **`PG`** | -0.11 | -0.19 | 0.10 | -0.17 | `1.00` | 0.42 | 0.22 | 0.26 | 0.37 | -0.08 |
| **`JNJ`** | -0.16 | -0.17 | 0.16 | -0.01 | 0.42 | `1.00` | 0.15 | 0.53 | 0.31 | 0.07 |
| **`V`** | 0.21 | -0.07 | 0.35 | -0.12 | 0.22 | 0.15 | `1.00` | 0.23 | 0.25 | -0.08 |
| **`ABBV`** | -0.10 | -0.13 | 0.07 | 0.01 | 0.26 | 0.53 | 0.23 | `1.00` | 0.23 | 0.04 |
| **`COST`** | -0.06 | -0.23 | -0.01 | 0.04 | 0.37 | 0.31 | 0.25 | 0.23 | `1.00` | 0.10 |
| **`XOM`** | -0.16 | -0.20 | -0.10 | **0.76** | -0.08 | 0.07 | -0.08 | 0.04 | 0.10 | `1.00` |

---

## 3. Bảng Định Cỡ Vị Thế (`ATR Risk-Parity`), Chandelier Stop & Kiểm Toán Lịch BCTC

| Mã | Ngành | Giá ($) | Stop `2xATR` ($) | Chandelier Trailing ($) | Khoảng cách Stop (%) | Tỷ trọng (% NAV) | Rủi ro tối đa (% NAV) | Điểm IC (/100) | Lịch BCTC (`Earnings Radar`) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`PG`** | Consumer Household Staples | $172.97 | **$166.06** | $164.94 | -4.0% | **7.9% NAV** | `-0.32% NAV` | **78/100** | CLEAR (2027-01-21 BMO) |
| **`COST`** | Membership Warehouse Retail | $1114.22 | **$1071.38** | $1070.12 | -3.84% | **7.4% NAV** | `-0.28% NAV` | **63/100** | CLEAR (2026-12-10 AMC) |
| **`V`** | Global Payment Network | $420.08 | **$399.81** | $416.9 | -4.82% | **7.1% NAV** | `-0.34% NAV` | **83/100** | CLEAR (2027-01-26 AMC) |
| **`ABBV`** | Biotech & Immunology | $293.03 | **$278.32** | $284.55 | -5.02% | **6.8% NAV** | `-0.34% NAV` | **86/100** | CLEAR (2026-10-30 BMO) |
| **`JPM`** | Global Diversified Banking | $330.53 | **$313.54** | $338.57 | -5.14% | **6.3% NAV** | `-0.32% NAV` | **86/100** | CLEAR (2027-01-14 BMO) |
| **`XOM`** | Integrated Oil & Gas | $167.31 | **$158.05** | $176.92 | -5.54% | **6.3% NAV** | `-0.35% NAV` | **85/100** | CLEAR (2027-01-29 BMO) |
| **`JNJ`** | Pharmaceuticals & MedTech | $280.07 | **$265.79** | $272.4 | -5.1% | **6.1% NAV** | `-0.31% NAV` | **75/100** | CLEAR (2027-01-26 BMO) |
| **`OXY`** | Upstream Oil & Carbon Capture | $56.98 | **$53.27** | $60.32 | -6.52% | **5.1% NAV** | `-0.33% NAV` | **84/100** | CLEAR (2026-11-09 AMC) |
| **`MSFT`** | Enterprise Software & Cloud | $501.85 | **$464.26** | $512.16 | -7.5% | **4.6% NAV** | `-0.34% NAV` | **83/100** | CLEAR (2027-01-27 AMC) |
| **`TSM`** | Global Chip Foundry | $360.89 | **$318.79** | $388.26 | -11.66% | **2.4% NAV** | `-0.28% NAV` | **70/100** | CLEAR (2027-01-14 BMO) |

### Danh Sách Theo Dõi Tạm Khóa Do Sát Ngày Công Bố BCTC (`Locked Imminent Earnings Watchlist <= 7 Ngày`)
| Mã | Ngành | Giá ($) | Ngày BCTC | Phiên | Số Ngày Còn Lại | Implied Move (±%) | Điểm IC | Lý Do Khóa & Kế Hoạch Hành Động Sau BCTC |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`WMT`** | Discount Retail & Grocery | $127.54 | `2026-11-19` | BMO | **2d** | `±5.71%` | 55/100 | Quan sát phản ứng giá sau BCTC ngày 2026-11-19 trước khi mở vị thế. |
| **`NVDA`** | Semiconductors & AI | $154.36 | `2026-11-17` | AMC | **0d** | `±14.5%` | 67/100 | Chờ BCTC công bố ngày 2026-11-17; chỉ giải ngân nếu giữ vững MA50 ($211.74) và hướng dẫn EPS tích cực. |

---

## 4. Kiểm Thử Sức Chịu Đựng Danh Mục Trước 3 Cú Sốc Vĩ Mô (`Institutional Stress-Testing`)

| Kịch bản Cú sốc Vĩ mô / Địa chính trị | Giả định S&P 500 | Tác động Dự kiến lên Danh mục | Mức Vượt trội (Alpha Bảo vệ) | Cơ chế Phòng vệ Tự động của Danh mục |
| :--- | :---: | :---: | :---: | :--- |
| **Kịch bản 1: Cú sốc Bán tháo Thị trường (S&P 500 sập -10.0%)**<br>*(Kích hoạt: Khủng hoảng thanh khoản hoặc dữ liệu kinh tế xấu đột biến)* | `-10.0%` | **`-3.15% NAV`** | **`+6.85%`** | Beta danh mục thấp (0.33) + Đệm 40.0% Tiền mặt/T-Bills + Kích hoạt Stop-Loss 2xATR & Chandelier Stop tự động |
| **Kịch bản 2: Cú sốc Lãi suất Fed Diều hâu (US 10Y Yield vọt lên 5.45%)**<br>*(Kích hoạt: PCE/CPI vượt 4.0% buộc Fed tăng lãi suất thêm +25–50 bps)* | `-6.5%` | **`-1.25% NAV`** | **`+5.25%`** | Nhóm Ngân hàng/Tài chính (JPM, V) và 40.0% T-Bills hưởng lợi trực tiếp bù đắp cho nhóm Công nghệ |
| **Kịch bản 3: Cú sốc Giá Dầu Địa chính trị (WTI Crude vọt lên $125/thùng)**<br>*(Kích hoạt: Gián đoạn nghiêm trọng eo biển Hormuz hoặc cơ sở lọc dầu toàn cầu)* | `-5.5%` | **`0.56% NAV`** | **`+6.06%`** | Vị thế Dầu khí (OXY) và Phòng thủ Thiết yếu/Y tế (PG, JNJ, ABBV, COST) đóng vai trò Natural Hedge bảo vệ NAV |

---

## 5. Phiên Tranh Biện Đối Kháng Đa Tác Tử (`Adversarial Bull vs Bear Debate — CIO Anti-Paralysis Protocol`)
| Mã | Luận Điểm Bảo Vệ Của `Bull Agent` | Phản Biện Đào Bới Rủi Ro Của `Bear Agent` | Phán Quyết Hòa Giải Của `Master CIO` | Điểm Đồng Thuận |
| :--- | :--- | :--- | :--- | :---: |
| **`PG`** | FCF chuẩn hóa đạt +$12.65B USD, tăng trưởng doanh thu +4.0% YoY, giá ($172.97) giữ cấu trúc trên MA200 ($150.08), điểm IC 78/100. | CẢNH BÁO ĐỊNH GIÁ/ĐÀ TĂNG: RSI tiệm cận vùng nóng (72.03) — Cần tránh mua đuổi giá xanh. | **APPROVED_WITH_60_40_SPLIT (Bác bỏ Veto định giá • Duyệt giải ngân chia nhịp 60/40 Limit Pullback)** | **`84.5/100`** |
| **`COST`** | FCF chuẩn hóa đạt +$6.75B USD, tăng trưởng doanh thu +11.1% YoY, giá ($1114.22) giữ cấu trúc trên MA200 ($977.28), điểm IC 63/100. | CẢNH BÁO ĐỊNH GIÁ/ĐÀ TĂNG: Định giá Fwd P/E cao (44.49x); RSI tiệm cận vùng nóng (77.18) — Cần tránh mua đuổi giá xanh. | **APPROVED_WITH_60_40_SPLIT (Bác bỏ Veto định giá • Duyệt giải ngân chia nhịp 60/40 Limit Pullback)** | **`84.5/100`** |
| **`V`** | FCF chuẩn hóa đạt +$20.98B USD, tăng trưởng doanh thu +13.2% YoY, giá ($420.08) giữ cấu trúc trên MA200 ($348.02), điểm IC 83/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`ABBV`** | FCF chuẩn hóa đạt +$17.69B USD, tăng trưởng doanh thu +10.3% YoY, giá ($293.03) giữ cấu trúc trên MA200 ($241.48), điểm IC 86/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`JPM`** | FCF chuẩn hóa đạt +$0.0B USD, tăng trưởng doanh thu +10.2% YoY, giá ($330.53) giữ cấu trúc trên MA200 ($325.13), điểm IC 86/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`XOM`** | FCF chuẩn hóa đạt +$28.32B USD, tăng trưởng doanh thu +32.6% YoY, giá ($167.31) giữ cấu trúc trên MA200 ($156.63), điểm IC 85/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`JNJ`** | FCF chuẩn hóa đạt +$18.5B USD, tăng trưởng doanh thu +5.9% YoY, giá ($280.07) giữ cấu trúc trên MA200 ($250.31), điểm IC 75/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`OXY`** | FCF chuẩn hóa đạt +$4.91B USD, tăng trưởng doanh thu +19.0% YoY, giá ($56.98) giữ cấu trúc trên MA200 ($56.9), điểm IC 84/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`MSFT`** | FCF chuẩn hóa đạt +$2.99B USD, tăng trưởng doanh thu +18.8% YoY, giá ($501.85) giữ cấu trúc trên MA200 ($442.25), điểm IC 83/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`TSM`** | FCF chuẩn hóa đạt +$31.69B USD, tăng trưởng doanh thu +50.9% YoY, giá ($360.89) giữ cấu trúc trên MA200 ($403.36), điểm IC 70/100. | VI PHẠM CẤU TRÚC: Gãy cấu trúc MA200 ($360.89 < $403.36) | **ABSOLUTE_VETO (Từ chối giải ngân do vi phạm lằn ranh đỏ cấu trúc)** | **`35.0/100`** |
