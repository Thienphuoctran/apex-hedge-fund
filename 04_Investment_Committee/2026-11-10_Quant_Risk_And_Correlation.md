# [BAN 4 — QUANT RISK] BÁO CÁO MA TRẬN TƯƠNG QUAN, ĐỊNH CỠ VỊ THẾ & KIỂM THỬ SỨC CHỊU ĐỰNG (STRESS TEST)
**Ngày kiểm toán**: 2026-11-10  
**Công cụ định lượng**: `scripts/quant_portfolio_engine.py` (v5.0 Audited — 0 Imminent Earnings Violations, Chandelier Stop & ATR Risk-Parity)

---

## 1. Tổng Quan Chỉ Số Rủi Ro Danh Mục (Portfolio Risk Telemetry)
- **Tỷ trọng Cổ phiếu / Tiền mặt (T-Bills ~5%)**: **`60.0% Cổ phiếu` / `40.0% Tiền mặt`**
- **Hệ số Beta Danh mục Tổng hợp (Portfolio Weighted Beta vs S&P 500)**: **`0.36`** *(Thấp hơn đáng kể so với biến động thị trường chung 1.00)*
- **Kiểm soát Cụm Bán dẫn (`NVDA + TSM`)**: **`3.1% NAV`** *(Tuân thủ trần `<= 14.0% NAV`)*
- **Tổng rủi ro danh mục nếu toàn bộ 10 vị thế đồng loạt chạm Stop-Loss `2xATR(14)`**: **`-3.24% NAV`**
- **Số mã bị khóa mua mới do sát lịch BCTC (`0 <= days_to_earnings <= 7`)**: **`1 mã`** (`NVDA`)

---

## 2. Ma Trận Tương Quan Lợi Suất 1 Năm (`Pairwise Return Correlation Matrix`)

| Mã | **`MSFT`** | **`TSM`** | **`JPM`** | **`OXY`** | **`PG`** | **`JNJ`** | **`V`** | **`ABBV`** | **`COST`** | **`XOM`** |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`MSFT`** | `1.00` | 0.18 | 0.12 | -0.11 | -0.11 | -0.17 | 0.21 | -0.10 | -0.06 | -0.16 |
| **`TSM`** | 0.18 | `1.00` | 0.16 | -0.21 | -0.18 | -0.18 | -0.08 | -0.14 | -0.24 | -0.22 |
| **`JPM`** | 0.12 | 0.16 | `1.00` | -0.15 | 0.11 | 0.14 | 0.35 | 0.08 | -0.01 | -0.12 |
| **`OXY`** | -0.11 | -0.21 | -0.15 | `1.00` | -0.16 | -0.02 | -0.12 | 0.00 | 0.04 | **0.76** |
| **`PG`** | -0.11 | -0.18 | 0.11 | -0.16 | `1.00` | 0.42 | 0.23 | 0.26 | 0.37 | -0.06 |
| **`JNJ`** | -0.17 | -0.18 | 0.14 | -0.02 | 0.42 | `1.00` | 0.15 | 0.53 | 0.31 | 0.07 |
| **`V`** | 0.21 | -0.08 | 0.35 | -0.12 | 0.23 | 0.15 | `1.00` | 0.22 | 0.25 | -0.07 |
| **`ABBV`** | -0.10 | -0.14 | 0.08 | 0.00 | 0.26 | 0.53 | 0.22 | `1.00` | 0.22 | 0.03 |
| **`COST`** | -0.06 | -0.24 | -0.01 | 0.04 | 0.37 | 0.31 | 0.25 | 0.22 | `1.00` | 0.10 |
| **`XOM`** | -0.16 | -0.22 | -0.12 | **0.76** | -0.06 | 0.07 | -0.07 | 0.03 | 0.10 | `1.00` |

---

## 3. Bảng Định Cỡ Vị Thế (`ATR Risk-Parity`), Chandelier Stop & Kiểm Toán Lịch BCTC

| Mã | Ngành | Giá ($) | Stop `2xATR` ($) | Chandelier Trailing ($) | Khoảng cách Stop (%) | Tỷ trọng (% NAV) | Rủi ro tối đa (% NAV) | Điểm IC (/100) | Lịch BCTC (`Earnings Radar`) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`JPM`** | Global Diversified Banking | $342.08 | **$326.05** | $339.77 | -4.68% | **7.9% NAV** | `-0.37% NAV` | **92/100** | CLEAR (2027-01-14 BMO) |
| **`V`** | Global Payment Network | $422.16 | **$402.4** | $417.52 | -4.68% | **7.1% NAV** | `-0.33% NAV` | **80/100** | CLEAR (2027-01-26 AMC) |
| **`COST`** | Membership Warehouse Retail | $1066.18 | **$1023.38** | $1028.05 | -4.02% | **7.1% NAV** | `-0.29% NAV` | **75/100** | CLEAR (2026-12-10 AMC) |
| **`PG`** | Consumer Household Staples | $168.32 | **$160.46** | $160.69 | -4.68% | **6.8% NAV** | `-0.32% NAV` | **82/100** | CLEAR (2027-01-21 BMO) |
| **`ABBV`** | Biotech & Immunology | $293.3 | **$277.83** | $283.6 | -5.28% | **6.3% NAV** | `-0.33% NAV` | **86/100** | CLEAR (2026-10-30 BMO) |
| **`MSFT`** | Enterprise Software & Cloud | $545.18 | **$512.1** | $517.8 | -6.06% | **5.8% NAV** | `-0.35% NAV` | **83/100** | CLEAR (2027-01-27 AMC) |
| **`JNJ`** | Pharmaceuticals & MedTech | $282.11 | **$266.46** | $263.17 | -5.54% | **5.8% NAV** | `-0.32% NAV` | **79/100** | CLEAR (2027-01-26 BMO) |
| **`XOM`** | Integrated Oil & Gas | $164.73 | **$154.67** | $175.92 | -6.1% | **5.8% NAV** | `-0.35% NAV` | **86/100** | CLEAR (2027-01-29 BMO) |
| **`OXY`** | Upstream Oil & Carbon Capture | $55.76 | **$52.02** | $60.29 | -6.7% | **4.3% NAV** | `-0.29% NAV` | **71/100** | JUST REPORTED (1d ago) — Đã qua rủi ro BCTC |
| **`TSM`** | Global Chip Foundry | $388.62 | **$352.65** | $419.87 | -9.26% | **3.1% NAV** | `-0.29% NAV` | **70/100** | CLEAR (2027-01-14 BMO) |

### Danh Sách Theo Dõi Tạm Khóa Do Sát Ngày Công Bố BCTC (`Locked Imminent Earnings Watchlist <= 7 Ngày`)
| Mã | Ngành | Giá ($) | Ngày BCTC | Phiên | Số Ngày Còn Lại | Implied Move (±%) | Điểm IC | Lý Do Khóa & Kế Hoạch Hành Động Sau BCTC |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`NVDA`** | Semiconductors & AI | $178.67 | `2026-11-17` | AMC | **7d** | `±11.56%` | 67/100 | Chờ BCTC công bố ngày 2026-11-17; chỉ giải ngân nếu giữ vững MA50 ($219.04) và hướng dẫn EPS tích cực. |

---

## 4. Kiểm Thử Sức Chịu Đựng Danh Mục Trước 3 Cú Sốc Vĩ Mô (`Institutional Stress-Testing`)

| Kịch bản Cú sốc Vĩ mô / Địa chính trị | Giả định S&P 500 | Tác động Dự kiến lên Danh mục | Mức Vượt trội (Alpha Bảo vệ) | Cơ chế Phòng vệ Tự động của Danh mục |
| :--- | :---: | :---: | :---: | :--- |
| **Kịch bản 1: Cú sốc Bán tháo Thị trường (S&P 500 sập -10.0%)**<br>*(Kích hoạt: Khủng hoảng thanh khoản hoặc dữ liệu kinh tế xấu đột biến)* | `-10.0%` | **`-3.42% NAV`** | **`+6.58%`** | Beta danh mục thấp (0.36) + Đệm 40.0% Tiền mặt/T-Bills + Kích hoạt Stop-Loss 2xATR & Chandelier Stop tự động |
| **Kịch bản 2: Cú sốc Lãi suất Fed Diều hâu (US 10Y Yield vọt lên 5.45%)**<br>*(Kích hoạt: PCE/CPI vượt 4.0% buộc Fed tăng lãi suất thêm +25–50 bps)* | `-6.5%` | **`-1.27% NAV`** | **`+5.23%`** | Nhóm Ngân hàng/Tài chính (JPM, V) và 40.0% T-Bills hưởng lợi trực tiếp bù đắp cho nhóm Công nghệ |
| **Kịch bản 3: Cú sốc Giá Dầu Địa chính trị (WTI Crude vọt lên $125/thùng)**<br>*(Kích hoạt: Gián đoạn nghiêm trọng eo biển Hormuz hoặc cơ sở lọc dầu toàn cầu)* | `-5.5%` | **`0.24% NAV`** | **`+5.74%`** | Vị thế Dầu khí (OXY) và Phòng thủ Thiết yếu/Y tế (PG, JNJ, ABBV, COST) đóng vai trò Natural Hedge bảo vệ NAV |

---

## 5. Phiên Tranh Biện Đối Kháng Đa Tác Tử (`Adversarial Bull vs Bear Debate — CIO Anti-Paralysis Protocol`)
| Mã | Luận Điểm Bảo Vệ Của `Bull Agent` | Phản Biện Đào Bới Rủi Ro Của `Bear Agent` | Phán Quyết Hòa Giải Của `Master CIO` | Điểm Đồng Thuận |
| :--- | :--- | :--- | :--- | :---: |
| **`JPM`** | FCF chuẩn hóa đạt +$0.0B USD, tăng trưởng doanh thu +10.2% YoY, giá ($342.08) giữ cấu trúc trên MA200 ($324.03), điểm IC 92/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`V`** | FCF chuẩn hóa đạt +$20.98B USD, tăng trưởng doanh thu +13.2% YoY, giá ($422.16) giữ cấu trúc trên MA200 ($345.16), điểm IC 80/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`COST`** | FCF chuẩn hóa đạt +$6.75B USD, tăng trưởng doanh thu +11.1% YoY, giá ($1066.18) giữ cấu trúc trên MA200 ($973.23), điểm IC 75/100. | CẢNH BÁO ĐỊNH GIÁ/ĐÀ TĂNG: Định giá Fwd P/E cao (42.55x); RSI tiệm cận vùng nóng (69.58) — Cần tránh mua đuổi giá xanh. | **APPROVED_WITH_60_40_SPLIT (Bác bỏ Veto định giá • Duyệt giải ngân chia nhịp 60/40 Limit Pullback)** | **`84.5/100`** |
| **`PG`** | FCF chuẩn hóa đạt +$12.65B USD, tăng trưởng doanh thu +4.0% YoY, giá ($168.32) giữ cấu trúc trên MA200 ($149.48), điểm IC 82/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`ABBV`** | FCF chuẩn hóa đạt +$17.69B USD, tăng trưởng doanh thu +10.3% YoY, giá ($293.3) giữ cấu trúc trên MA200 ($239.31), điểm IC 86/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`MSFT`** | FCF chuẩn hóa đạt +$2.99B USD, tăng trưởng doanh thu +18.8% YoY, giá ($545.18) giữ cấu trúc trên MA200 ($440.24), điểm IC 83/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`JNJ`** | FCF chuẩn hóa đạt +$18.5B USD, tăng trưởng doanh thu +5.9% YoY, giá ($282.11) giữ cấu trúc trên MA200 ($248.64), điểm IC 79/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`XOM`** | FCF chuẩn hóa đạt +$28.32B USD, tăng trưởng doanh thu +32.6% YoY, giá ($164.73) giữ cấu trúc trên MA200 ($155.75), điểm IC 86/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`OXY`** | FCF chuẩn hóa đạt +$3.79B USD, tăng trưởng doanh thu +53.4% YoY, giá ($55.76) giữ cấu trúc trên MA200 ($56.51), điểm IC 71/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`TSM`** | FCF chuẩn hóa đạt +$36.69B USD, tăng trưởng doanh thu +50.9% YoY, giá ($388.62) giữ cấu trúc trên MA200 ($401.75), điểm IC 70/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
