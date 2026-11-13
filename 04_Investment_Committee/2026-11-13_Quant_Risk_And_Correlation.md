# [BAN 4 — QUANT RISK] BÁO CÁO MA TRẬN TƯƠNG QUAN, ĐỊNH CỠ VỊ THẾ & KIỂM THỬ SỨC CHỊU ĐỰNG (STRESS TEST)
**Ngày kiểm toán**: 2026-11-13  
**Công cụ định lượng**: `scripts/quant_portfolio_engine.py` (v5.0 Audited — 0 Imminent Earnings Violations, Chandelier Stop & ATR Risk-Parity)

---

## 1. Tổng Quan Chỉ Số Rủi Ro Danh Mục (Portfolio Risk Telemetry)
- **Tỷ trọng Cổ phiếu / Tiền mặt (T-Bills ~5%)**: **`60.0% Cổ phiếu` / `40.0% Tiền mặt`**
- **Hệ số Beta Danh mục Tổng hợp (Portfolio Weighted Beta vs S&P 500)**: **`0.34`** *(Thấp hơn đáng kể so với biến động thị trường chung 1.00)*
- **Kiểm soát Cụm Bán dẫn (`NVDA + TSM`)**: **`2.8% NAV`** *(Tuân thủ trần `<= 14.0% NAV`)*
- **Tổng rủi ro danh mục nếu toàn bộ 10 vị thế đồng loạt chạm Stop-Loss `2xATR(14)`**: **`-3.09% NAV`**
- **Số mã bị khóa mua mới do sát lịch BCTC (`0 <= days_to_earnings <= 7`)**: **`2 mã`** (`NVDA, WMT`)

---

## 2. Ma Trận Tương Quan Lợi Suất 1 Năm (`Pairwise Return Correlation Matrix`)

| Mã | **`MSFT`** | **`TSM`** | **`JPM`** | **`OXY`** | **`PG`** | **`JNJ`** | **`V`** | **`ABBV`** | **`COST`** | **`XOM`** |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`MSFT`** | `1.00` | 0.16 | 0.11 | -0.11 | -0.11 | -0.17 | 0.20 | -0.10 | -0.06 | -0.16 |
| **`TSM`** | 0.16 | `1.00` | 0.15 | -0.21 | -0.19 | -0.19 | -0.08 | -0.14 | -0.23 | -0.22 |
| **`JPM`** | 0.11 | 0.15 | `1.00` | -0.15 | 0.11 | 0.14 | 0.36 | 0.07 | -0.00 | -0.11 |
| **`OXY`** | -0.11 | -0.21 | -0.15 | `1.00` | -0.16 | -0.02 | -0.12 | 0.00 | 0.05 | **0.76** |
| **`PG`** | -0.11 | -0.19 | 0.11 | -0.16 | `1.00` | 0.42 | 0.23 | 0.26 | 0.37 | -0.07 |
| **`JNJ`** | -0.17 | -0.19 | 0.14 | -0.02 | 0.42 | `1.00` | 0.14 | 0.53 | 0.31 | 0.06 |
| **`V`** | 0.20 | -0.08 | 0.36 | -0.12 | 0.23 | 0.14 | `1.00` | 0.22 | 0.26 | -0.08 |
| **`ABBV`** | -0.10 | -0.14 | 0.07 | 0.00 | 0.26 | 0.53 | 0.22 | `1.00` | 0.23 | 0.04 |
| **`COST`** | -0.06 | -0.23 | -0.00 | 0.05 | 0.37 | 0.31 | 0.26 | 0.23 | `1.00` | 0.11 |
| **`XOM`** | -0.16 | -0.22 | -0.11 | **0.76** | -0.07 | 0.06 | -0.08 | 0.04 | 0.11 | `1.00` |

---

## 3. Bảng Định Cỡ Vị Thế (`ATR Risk-Parity`), Chandelier Stop & Kiểm Toán Lịch BCTC

| Mã | Ngành | Giá ($) | Stop `2xATR` ($) | Chandelier Trailing ($) | Khoảng cách Stop (%) | Tỷ trọng (% NAV) | Rủi ro tối đa (% NAV) | Điểm IC (/100) | Lịch BCTC (`Earnings Radar`) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`PG`** | Consumer Household Staples | $170.34 | **$163.89** | $162.67 | -3.78% | **7.9% NAV** | `-0.3% NAV` | **78/100** | CLEAR (2027-01-21 BMO) |
| **`JPM`** | Global Diversified Banking | $344.86 | **$329.3** | $340.35 | -4.52% | **7.8% NAV** | `-0.35% NAV` | **92/100** | CLEAR (2027-01-14 BMO) |
| **`COST`** | Membership Warehouse Retail | $1107.79 | **$1064.64** | $1055.57 | -3.9% | **7.0% NAV** | `-0.27% NAV` | **63/100** | CLEAR (2026-12-10 AMC) |
| **`V`** | Global Payment Network | $426.12 | **$405.42** | $416.36 | -4.86% | **6.3% NAV** | `-0.31% NAV` | **79/100** | CLEAR (2027-01-26 AMC) |
| **`XOM`** | Integrated Oil & Gas | $170.13 | **$160.58** | $176.56 | -5.62% | **6.3% NAV** | `-0.35% NAV` | **87/100** | CLEAR (2027-01-29 BMO) |
| **`ABBV`** | Biotech & Immunology | $294.76 | **$279.92** | $284.37 | -5.04% | **6.1% NAV** | `-0.31% NAV` | **82/100** | CLEAR (2026-10-30 BMO) |
| **`JNJ`** | Pharmaceuticals & MedTech | $287.0 | **$273.0** | $270.61 | -4.88% | **5.6% NAV** | `-0.27% NAV` | **68/100** | CLEAR (2027-01-26 BMO) |
| **`MSFT`** | Enterprise Software & Cloud | $521.8 | **$486.74** | $515.33 | -6.72% | **5.1% NAV** | `-0.34% NAV` | **85/100** | CLEAR (2027-01-27 AMC) |
| **`OXY`** | Upstream Oil & Carbon Capture | $58.75 | **$55.07** | $60.35 | -6.28% | **5.1% NAV** | `-0.32% NAV` | **84/100** | JUST REPORTED (4d ago) — Đã qua rủi ro BCTC |
| **`TSM`** | Global Chip Foundry | $393.6 | **$355.5** | $393.26 | -9.68% | **2.8% NAV** | `-0.27% NAV` | **70/100** | CLEAR (2027-01-14 BMO) |

### Danh Sách Theo Dõi Tạm Khóa Do Sát Ngày Công Bố BCTC (`Locked Imminent Earnings Watchlist <= 7 Ngày`)
| Mã | Ngành | Giá ($) | Ngày BCTC | Phiên | Số Ngày Còn Lại | Implied Move (±%) | Điểm IC | Lý Do Khóa & Kế Hoạch Hành Động Sau BCTC |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`NVDA`** | Semiconductors & AI | $158.97 | `2026-11-17` | AMC | **4d** | `±14.5%` | 67/100 | Chờ BCTC công bố ngày 2026-11-17; chỉ giải ngân nếu giữ vững MA50 ($214.57) và hướng dẫn EPS tích cực. |
| **`WMT`** | Discount Retail & Grocery | $127.92 | `2026-11-19` | BMO | **6d** | `±5.55%` | 55/100 | Quan sát phản ứng giá sau BCTC ngày 2026-11-19 trước khi mở vị thế. |

---

## 4. Kiểm Thử Sức Chịu Đựng Danh Mục Trước 3 Cú Sốc Vĩ Mô (`Institutional Stress-Testing`)

| Kịch bản Cú sốc Vĩ mô / Địa chính trị | Giả định S&P 500 | Tác động Dự kiến lên Danh mục | Mức Vượt trội (Alpha Bảo vệ) | Cơ chế Phòng vệ Tự động của Danh mục |
| :--- | :---: | :---: | :---: | :--- |
| **Kịch bản 1: Cú sốc Bán tháo Thị trường (S&P 500 sập -10.0%)**<br>*(Kích hoạt: Khủng hoảng thanh khoản hoặc dữ liệu kinh tế xấu đột biến)* | `-10.0%` | **`-3.28% NAV`** | **`+6.72%`** | Beta danh mục thấp (0.34) + Đệm 40.0% Tiền mặt/T-Bills + Kích hoạt Stop-Loss 2xATR & Chandelier Stop tự động |
| **Kịch bản 2: Cú sốc Lãi suất Fed Diều hâu (US 10Y Yield vọt lên 5.45%)**<br>*(Kích hoạt: PCE/CPI vượt 4.0% buộc Fed tăng lãi suất thêm +25–50 bps)* | `-6.5%` | **`-1.21% NAV`** | **`+5.29%`** | Nhóm Ngân hàng/Tài chính (JPM, V) và 40.0% T-Bills hưởng lợi trực tiếp bù đắp cho nhóm Công nghệ |
| **Kịch bản 3: Cú sốc Giá Dầu Địa chính trị (WTI Crude vọt lên $125/thùng)**<br>*(Kích hoạt: Gián đoạn nghiêm trọng eo biển Hormuz hoặc cơ sở lọc dầu toàn cầu)* | `-5.5%` | **`0.5% NAV`** | **`+6.0%`** | Vị thế Dầu khí (OXY) và Phòng thủ Thiết yếu/Y tế (PG, JNJ, ABBV, COST) đóng vai trò Natural Hedge bảo vệ NAV |

---

## 5. Phiên Tranh Biện Đối Kháng Đa Tác Tử (`Adversarial Bull vs Bear Debate — CIO Anti-Paralysis Protocol`)
| Mã | Luận Điểm Bảo Vệ Của `Bull Agent` | Phản Biện Đào Bới Rủi Ro Của `Bear Agent` | Phán Quyết Hòa Giải Của `Master CIO` | Điểm Đồng Thuận |
| :--- | :--- | :--- | :--- | :---: |
| **`PG`** | FCF chuẩn hóa đạt +$12.65B USD, tăng trưởng doanh thu +4.0% YoY, giá ($170.34) giữ cấu trúc trên MA200 ($149.88), điểm IC 78/100. | CẢNH BÁO ĐỊNH GIÁ/ĐÀ TĂNG: RSI tiệm cận vùng nóng (68.92) — Cần tránh mua đuổi giá xanh. | **APPROVED_WITH_60_40_SPLIT (Bác bỏ Veto định giá • Duyệt giải ngân chia nhịp 60/40 Limit Pullback)** | **`84.5/100`** |
| **`JPM`** | FCF chuẩn hóa đạt +$0.0B USD, tăng trưởng doanh thu +10.2% YoY, giá ($344.86) giữ cấu trúc trên MA200 ($324.85), điểm IC 92/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`COST`** | FCF chuẩn hóa đạt +$6.75B USD, tăng trưởng doanh thu +11.1% YoY, giá ($1107.79) giữ cấu trúc trên MA200 ($975.69), điểm IC 63/100. | CẢNH BÁO ĐỊNH GIÁ/ĐÀ TĂNG: Định giá Fwd P/E cao (44.24x); RSI tiệm cận vùng nóng (76.25) — Cần tránh mua đuổi giá xanh. | **APPROVED_WITH_60_40_SPLIT (Bác bỏ Veto định giá • Duyệt giải ngân chia nhịp 60/40 Limit Pullback)** | **`84.5/100`** |
| **`V`** | FCF chuẩn hóa đạt +$20.98B USD, tăng trưởng doanh thu +13.2% YoY, giá ($426.12) giữ cấu trúc trên MA200 ($347.07), điểm IC 79/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`XOM`** | FCF chuẩn hóa đạt +$28.32B USD, tăng trưởng doanh thu +32.6% YoY, giá ($170.13) giữ cấu trúc trên MA200 ($156.36), điểm IC 87/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`ABBV`** | FCF chuẩn hóa đạt +$17.69B USD, tăng trưởng doanh thu +10.3% YoY, giá ($294.76) giữ cấu trúc trên MA200 ($240.79), điểm IC 82/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`JNJ`** | FCF chuẩn hóa đạt +$18.5B USD, tăng trưởng doanh thu +5.9% YoY, giá ($287.0) giữ cấu trúc trên MA200 ($249.79), điểm IC 68/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`MSFT`** | FCF chuẩn hóa đạt +$2.99B USD, tăng trưởng doanh thu +18.8% YoY, giá ($521.8) giữ cấu trúc trên MA200 ($441.41), điểm IC 85/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`OXY`** | FCF chuẩn hóa đạt +$4.91B USD, tăng trưởng doanh thu +19.0% YoY, giá ($58.75) giữ cấu trúc trên MA200 ($56.77), điểm IC 84/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`TSM`** | FCF chuẩn hóa đạt +$36.57B USD, tăng trưởng doanh thu +50.9% YoY, giá ($393.6) giữ cấu trúc trên MA200 ($403.03), điểm IC 70/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
