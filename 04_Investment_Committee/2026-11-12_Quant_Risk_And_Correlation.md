# [BAN 4 — QUANT RISK] BÁO CÁO MA TRẬN TƯƠNG QUAN, ĐỊNH CỠ VỊ THẾ & KIỂM THỬ SỨC CHỊU ĐỰNG (STRESS TEST)
**Ngày kiểm toán**: 2026-11-12  
**Công cụ định lượng**: `scripts/quant_portfolio_engine.py` (v5.0 Audited — 0 Imminent Earnings Violations, Chandelier Stop & ATR Risk-Parity)

---

## 1. Tổng Quan Chỉ Số Rủi Ro Danh Mục (Portfolio Risk Telemetry)
- **Tỷ trọng Cổ phiếu / Tiền mặt (T-Bills ~5%)**: **`60.0% Cổ phiếu` / `40.0% Tiền mặt`**
- **Hệ số Beta Danh mục Tổng hợp (Portfolio Weighted Beta vs S&P 500)**: **`0.35`** *(Thấp hơn đáng kể so với biến động thị trường chung 1.00)*
- **Kiểm soát Cụm Bán dẫn (`NVDA + TSM`)**: **`3.7% NAV`** *(Tuân thủ trần `<= 14.0% NAV`)*
- **Tổng rủi ro danh mục nếu toàn bộ 10 vị thế đồng loạt chạm Stop-Loss `2xATR(14)`**: **`-3.19% NAV`**
- **Số mã bị khóa mua mới do sát lịch BCTC (`0 <= days_to_earnings <= 7`)**: **`2 mã`** (`NVDA, WMT`)

---

## 2. Ma Trận Tương Quan Lợi Suất 1 Năm (`Pairwise Return Correlation Matrix`)

| Mã | **`MSFT`** | **`TSM`** | **`JPM`** | **`OXY`** | **`PG`** | **`JNJ`** | **`V`** | **`ABBV`** | **`COST`** | **`XOM`** |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`MSFT`** | `1.00` | 0.17 | 0.12 | -0.11 | -0.11 | -0.17 | 0.20 | -0.10 | -0.06 | -0.17 |
| **`TSM`** | 0.17 | `1.00` | 0.16 | -0.21 | -0.18 | -0.18 | -0.08 | -0.13 | -0.23 | -0.22 |
| **`JPM`** | 0.12 | 0.16 | `1.00` | -0.15 | 0.11 | 0.14 | 0.36 | 0.07 | -0.01 | -0.11 |
| **`OXY`** | -0.11 | -0.21 | -0.15 | `1.00` | -0.16 | -0.02 | -0.12 | 0.00 | 0.04 | **0.76** |
| **`PG`** | -0.11 | -0.18 | 0.11 | -0.16 | `1.00` | 0.42 | 0.22 | 0.26 | 0.37 | -0.07 |
| **`JNJ`** | -0.17 | -0.18 | 0.14 | -0.02 | 0.42 | `1.00` | 0.14 | 0.53 | 0.31 | 0.06 |
| **`V`** | 0.20 | -0.08 | 0.36 | -0.12 | 0.22 | 0.14 | `1.00` | 0.22 | 0.26 | -0.08 |
| **`ABBV`** | -0.10 | -0.13 | 0.07 | 0.00 | 0.26 | 0.53 | 0.22 | `1.00` | 0.23 | 0.04 |
| **`COST`** | -0.06 | -0.23 | -0.01 | 0.04 | 0.37 | 0.31 | 0.26 | 0.23 | `1.00` | 0.11 |
| **`XOM`** | -0.17 | -0.22 | -0.11 | **0.76** | -0.07 | 0.06 | -0.08 | 0.04 | 0.11 | `1.00` |

---

## 3. Bảng Định Cỡ Vị Thế (`ATR Risk-Parity`), Chandelier Stop & Kiểm Toán Lịch BCTC

| Mã | Ngành | Giá ($) | Stop `2xATR` ($) | Chandelier Trailing ($) | Khoảng cách Stop (%) | Tỷ trọng (% NAV) | Rủi ro tối đa (% NAV) | Điểm IC (/100) | Lịch BCTC (`Earnings Radar`) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`JPM`** | Global Diversified Banking | $343.39 | **$327.51** | $339.96 | -4.62% | **7.6% NAV** | `-0.35% NAV` | **92/100** | CLEAR (2027-01-14 BMO) |
| **`PG`** | Consumer Household Staples | $167.67 | **$160.83** | $161.97 | -4.08% | **7.6% NAV** | `-0.31% NAV` | **82/100** | CLEAR (2027-01-21 BMO) |
| **`COST`** | Membership Warehouse Retail | $1087.61 | **$1044.13** | $1037.57 | -4.0% | **6.8% NAV** | `-0.27% NAV` | **71/100** | CLEAR (2026-12-10 AMC) |
| **`V`** | Global Payment Network | $425.55 | **$405.44** | $417.1 | -4.72% | **6.5% NAV** | `-0.31% NAV` | **79/100** | CLEAR (2027-01-26 AMC) |
| **`ABBV`** | Biotech & Immunology | $294.98 | **$280.3** | $284.58 | -4.98% | **6.4% NAV** | `-0.32% NAV` | **86/100** | CLEAR (2026-10-30 BMO) |
| **`JNJ`** | Pharmaceuticals & MedTech | $280.41 | **$265.91** | $265.13 | -5.18% | **5.9% NAV** | `-0.31% NAV` | **79/100** | CLEAR (2027-01-26 BMO) |
| **`XOM`** | Integrated Oil & Gas | $166.71 | **$156.88** | $176.21 | -5.9% | **5.7% NAV** | `-0.34% NAV` | **85/100** | CLEAR (2027-01-29 BMO) |
| **`MSFT`** | Enterprise Software & Cloud | $521.12 | **$486.11** | $515.38 | -6.72% | **5.1% NAV** | `-0.34% NAV` | **85/100** | CLEAR (2027-01-27 AMC) |
| **`OXY`** | Upstream Oil & Carbon Capture | $57.24 | **$53.39** | $60.15 | -6.72% | **4.7% NAV** | `-0.32% NAV` | **84/100** | JUST REPORTED (3d ago) — Đã qua rủi ro BCTC |
| **`TSM`** | Global Chip Foundry | $413.35 | **$377.35** | $400.5 | -8.7% | **3.7% NAV** | `-0.32% NAV` | **83/100** | CLEAR (2027-01-14 BMO) |

### Danh Sách Theo Dõi Tạm Khóa Do Sát Ngày Công Bố BCTC (`Locked Imminent Earnings Watchlist <= 7 Ngày`)
| Mã | Ngành | Giá ($) | Ngày BCTC | Phiên | Số Ngày Còn Lại | Implied Move (±%) | Điểm IC | Lý Do Khóa & Kế Hoạch Hành Động Sau BCTC |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`NVDA`** | Semiconductors & AI | $173.73 | `2026-11-17` | AMC | **5d** | `±12.36%` | 67/100 | Chờ BCTC công bố ngày 2026-11-17; chỉ giải ngân nếu giữ vững MA50 ($217.12) và hướng dẫn EPS tích cực. |
| **`WMT`** | Discount Retail & Grocery | $125.67 | `2026-11-19` | BMO | **7d** | `±5.83%` | 62/100 | Quan sát phản ứng giá sau BCTC ngày 2026-11-19 trước khi mở vị thế. |

---

## 4. Kiểm Thử Sức Chịu Đựng Danh Mục Trước 3 Cú Sốc Vĩ Mô (`Institutional Stress-Testing`)

| Kịch bản Cú sốc Vĩ mô / Địa chính trị | Giả định S&P 500 | Tác động Dự kiến lên Danh mục | Mức Vượt trội (Alpha Bảo vệ) | Cơ chế Phòng vệ Tự động của Danh mục |
| :--- | :---: | :---: | :---: | :--- |
| **Kịch bản 1: Cú sốc Bán tháo Thị trường (S&P 500 sập -10.0%)**<br>*(Kích hoạt: Khủng hoảng thanh khoản hoặc dữ liệu kinh tế xấu đột biến)* | `-10.0%` | **`-3.36% NAV`** | **`+6.64%`** | Beta danh mục thấp (0.35) + Đệm 40.0% Tiền mặt/T-Bills + Kích hoạt Stop-Loss 2xATR & Chandelier Stop tự động |
| **Kịch bản 2: Cú sốc Lãi suất Fed Diều hâu (US 10Y Yield vọt lên 5.45%)**<br>*(Kích hoạt: PCE/CPI vượt 4.0% buộc Fed tăng lãi suất thêm +25–50 bps)* | `-6.5%` | **`-1.31% NAV`** | **`+5.19%`** | Nhóm Ngân hàng/Tài chính (JPM, V) và 40.0% T-Bills hưởng lợi trực tiếp bù đắp cho nhóm Công nghệ |
| **Kịch bản 3: Cú sốc Giá Dầu Địa chính trị (WTI Crude vọt lên $125/thùng)**<br>*(Kích hoạt: Gián đoạn nghiêm trọng eo biển Hormuz hoặc cơ sở lọc dầu toàn cầu)* | `-5.5%` | **`0.32% NAV`** | **`+5.82%`** | Vị thế Dầu khí (OXY) và Phòng thủ Thiết yếu/Y tế (PG, JNJ, ABBV, COST) đóng vai trò Natural Hedge bảo vệ NAV |

---

## 5. Phiên Tranh Biện Đối Kháng Đa Tác Tử (`Adversarial Bull vs Bear Debate — CIO Anti-Paralysis Protocol`)
| Mã | Luận Điểm Bảo Vệ Của `Bull Agent` | Phản Biện Đào Bới Rủi Ro Của `Bear Agent` | Phán Quyết Hòa Giải Của `Master CIO` | Điểm Đồng Thuận |
| :--- | :--- | :--- | :--- | :---: |
| **`JPM`** | FCF chuẩn hóa đạt +$0.0B USD, tăng trưởng doanh thu +10.2% YoY, giá ($343.39) giữ cấu trúc trên MA200 ($324.45), điểm IC 92/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`PG`** | FCF chuẩn hóa đạt +$12.65B USD, tăng trưởng doanh thu +4.0% YoY, giá ($167.67) giữ cấu trúc trên MA200 ($149.67), điểm IC 82/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`COST`** | FCF chuẩn hóa đạt +$6.75B USD, tăng trưởng doanh thu +11.1% YoY, giá ($1087.61) giữ cấu trúc trên MA200 ($974.26), điểm IC 71/100. | CẢNH BÁO ĐỊNH GIÁ/ĐÀ TĂNG: Định giá Fwd P/E cao (43.45x); RSI tiệm cận vùng nóng (73.21) — Cần tránh mua đuổi giá xanh. | **APPROVED_WITH_60_40_SPLIT (Bác bỏ Veto định giá • Duyệt giải ngân chia nhịp 60/40 Limit Pullback)** | **`84.5/100`** |
| **`V`** | FCF chuẩn hóa đạt +$20.98B USD, tăng trưởng doanh thu +13.2% YoY, giá ($425.55) giữ cấu trúc trên MA200 ($346.13), điểm IC 79/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`ABBV`** | FCF chuẩn hóa đạt +$17.69B USD, tăng trưởng doanh thu +10.3% YoY, giá ($294.98) giữ cấu trúc trên MA200 ($240.04), điểm IC 86/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`JNJ`** | FCF chuẩn hóa đạt +$18.5B USD, tăng trưởng doanh thu +5.9% YoY, giá ($280.41) giữ cấu trúc trên MA200 ($249.22), điểm IC 79/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`XOM`** | FCF chuẩn hóa đạt +$28.32B USD, tăng trưởng doanh thu +32.6% YoY, giá ($166.71) giữ cấu trúc trên MA200 ($156.05), điểm IC 85/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`MSFT`** | FCF chuẩn hóa đạt +$2.99B USD, tăng trưởng doanh thu +18.8% YoY, giá ($521.12) giữ cấu trúc trên MA200 ($440.76), điểm IC 85/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`OXY`** | FCF chuẩn hóa đạt +$4.91B USD, tăng trưởng doanh thu +19.0% YoY, giá ($57.24) giữ cấu trúc trên MA200 ($56.64), điểm IC 84/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`TSM`** | FCF chuẩn hóa đạt +$36.45B USD, tăng trưởng doanh thu +50.9% YoY, giá ($413.35) giữ cấu trúc trên MA200 ($402.44), điểm IC 83/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
