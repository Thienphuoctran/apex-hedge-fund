# [BAN 4 — QUANT RISK] BÁO CÁO MA TRẬN TƯƠNG QUAN, ĐỊNH CỠ VỊ THẾ & KIỂM THỬ SỨC CHỊU ĐỰNG (STRESS TEST)
**Ngày kiểm toán**: 2026-11-03  
**Công cụ định lượng**: `scripts/quant_portfolio_engine.py` (v5.0 Audited — 0 Imminent Earnings Violations, Chandelier Stop & ATR Risk-Parity)

---

## 1. Tổng Quan Chỉ Số Rủi Ro Danh Mục (Portfolio Risk Telemetry)
- **Tỷ trọng Cổ phiếu / Tiền mặt (T-Bills ~5%)**: **`60.0% Cổ phiếu` / `40.0% Tiền mặt`**
- **Hệ số Beta Danh mục Tổng hợp (Portfolio Weighted Beta vs S&P 500)**: **`0.46`** *(Thấp hơn đáng kể so với biến động thị trường chung 1.00)*
- **Kiểm soát Cụm Bán dẫn (`NVDA + TSM`)**: **`7.9% NAV`** *(Tuân thủ trần `<= 14.0% NAV`)*
- **Tổng rủi ro danh mục nếu toàn bộ 10 vị thế đồng loạt chạm Stop-Loss `2xATR(14)`**: **`-2.77% NAV`**
- **Số mã bị khóa mua mới do sát lịch BCTC (`0 <= days_to_earnings <= 7`)**: **`8 mã`** (`QCOM, ARM, NVO, MCD, BRK-B, OXY, AMD, SMCI`)

---

## 2. Ma Trận Tương Quan Lợi Suất 1 Năm (`Pairwise Return Correlation Matrix`)

| Mã | **`MSFT`** | **`TSM`** | **`JPM`** | **`NVDA`** | **`PG`** | **`JNJ`** | **`V`** | **`ABBV`** | **`COST`** | **`XOM`** |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`MSFT`** | `1.00` | 0.17 | 0.07 | 0.26 | -0.15 | -0.23 | 0.19 | -0.15 | -0.06 | -0.15 |
| **`TSM`** | 0.17 | `1.00` | 0.13 | **0.66** | -0.18 | -0.22 | -0.11 | -0.19 | -0.22 | -0.29 |
| **`JPM`** | 0.07 | 0.13 | `1.00` | 0.13 | 0.06 | 0.09 | 0.31 | 0.04 | -0.04 | -0.10 |
| **`NVDA`** | 0.26 | **0.66** | 0.13 | `1.00` | -0.26 | -0.22 | -0.13 | -0.20 | -0.28 | -0.23 |
| **`PG`** | -0.15 | -0.18 | 0.06 | -0.26 | `1.00` | 0.41 | 0.20 | 0.25 | 0.34 | -0.02 |
| **`JNJ`** | -0.23 | -0.22 | 0.09 | -0.22 | 0.41 | `1.00` | 0.12 | 0.51 | 0.30 | 0.08 |
| **`V`** | 0.19 | -0.11 | 0.31 | -0.13 | 0.20 | 0.12 | `1.00` | 0.21 | 0.24 | -0.05 |
| **`ABBV`** | -0.15 | -0.19 | 0.04 | -0.20 | 0.25 | 0.51 | 0.21 | `1.00` | 0.23 | 0.03 |
| **`COST`** | -0.06 | -0.22 | -0.04 | -0.28 | 0.34 | 0.30 | 0.24 | 0.23 | `1.00` | 0.16 |
| **`XOM`** | -0.15 | -0.29 | -0.10 | -0.23 | -0.02 | 0.08 | -0.05 | 0.03 | 0.16 | `1.00` |

---

## 3. Bảng Định Cỡ Vị Thế (`ATR Risk-Parity`), Chandelier Stop & Kiểm Toán Lịch BCTC

| Mã | Ngành | Giá ($) | Stop `2xATR` ($) | Chandelier Trailing ($) | Khoảng cách Stop (%) | Tỷ trọng (% NAV) | Rủi ro tối đa (% NAV) | Điểm IC (/100) | Lịch BCTC (`Earnings Radar`) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`V`** | Global Payment Network | $425.51 | **$410.64** | $398.42 | -3.5% | **7.7% NAV** | `-0.27% NAV` | **77/100** | CLEAR (2027-01-26 AMC) |
| **`JPM`** | Global Diversified Banking | $340.58 | **$326.63** | $328.31 | -4.1% | **7.4% NAV** | `-0.3% NAV` | **90/100** | CLEAR (2027-01-14 BMO) |
| **`PG`** | Consumer Household Staples | $163.56 | **$156.71** | $158.29 | -4.18% | **7.4% NAV** | `-0.31% NAV` | **89/100** | CLEAR (2027-01-21 BMO) |
| **`COST`** | Membership Warehouse Retail | $1040.55 | **$1005.55** | $977.71 | -3.36% | **7.3% NAV** | `-0.25% NAV` | **75/100** | CLEAR (2026-12-10 AMC) |
| **`MSFT`** | Enterprise Software & Cloud | $507.12 | **$483.64** | $521.81 | -4.62% | **6.4% NAV** | `-0.3% NAV` | **83/100** | CLEAR (2027-01-27 AMC) |
| **`XOM`** | Integrated Oil & Gas | $179.67 | **$171.4** | $178.16 | -4.6% | **5.9% NAV** | `-0.27% NAV` | **81/100** | CLEAR (2027-01-29 BMO) |
| **`ABBV`** | Biotech & Immunology | $288.84 | **$275.03** | $281.48 | -4.78% | **5.1% NAV** | `-0.24% NAV` | **79/100** | JUST REPORTED (4d ago) — Đã qua rủi ro BCTC |
| **`JNJ`** | Pharmaceuticals & MedTech | $270.56 | **$255.09** | $262.68 | -5.72% | **4.9% NAV** | `-0.28% NAV` | **82/100** | CLEAR (2027-01-26 BMO) |
| **`TSM`** | Global Chip Foundry | $398.63 | **$369.8** | $451.44 | -7.24% | **4.1% NAV** | `-0.3% NAV` | **83/100** | CLEAR (2027-01-14 BMO) |
| **`NVDA`** | Semiconductors & AI | $202.06 | **$188.98** | $227.02 | -6.48% | **3.8% NAV** | `-0.25% NAV` | **68/100** | UPCOMING EARNINGS (14d, AMC) — Lưu ý biến động |

### Danh Sách Theo Dõi Tạm Khóa Do Sát Ngày Công Bố BCTC (`Locked Imminent Earnings Watchlist <= 7 Ngày`)
| Mã | Ngành | Giá ($) | Ngày BCTC | Phiên | Số Ngày Còn Lại | Implied Move (±%) | Điểm IC | Lý Do Khóa & Kế Hoạch Hành Động Sau BCTC |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`QCOM`** | Mobile & Edge AI Processors | $162.08 | `2026-11-04` | AMC | **1d** | `±10.83%` | 45/100 | Quan sát phản ứng giá sau BCTC ngày 2026-11-04 trước khi mở vị thế. |
| **`ARM`** | Semiconductor IP Architecture | $196.79 | `2026-11-04` | AMC | **1d** | `±14.5%` | 60/100 | Quan sát phản ứng giá sau BCTC ngày 2026-11-04 trước khi mở vị thế. |
| **`NVO`** | Biopharma GLP-1 Leader | $40.45 | `2026-11-04` | BMO | **1d** | `±4.46%` | 65/100 | Quan sát phản ứng giá sau BCTC ngày 2026-11-04 trước khi mở vị thế. |
| **`MCD`** | Global Quick Service Restaurants | $265.64 | `2026-11-04` | BMO | **1d** | `±4.25%` | 61/100 | Quan sát phản ứng giá sau BCTC ngày 2026-11-04 trước khi mở vị thế. |
| **`BRK-B`** | Diversified Conglomerate | $556.11 | `2026-11-07` | BMO | **4d** | `±3.08%` | 72/100 | Chờ BCTC công bố ngày 2026-11-07; chỉ giải ngân nếu giữ vững MA50 ($515.11) và hướng dẫn EPS tích cực. |
| **`OXY`** | Upstream Oil & Carbon Capture | $60.72 | `2026-11-09` | AMC | **6d** | `±5.8%` | 84/100 | Chờ BCTC công bố ngày 2026-11-09; chỉ giải ngân nếu giữ vững MA50 ($60.18) và hướng dẫn EPS tích cực. |
| **`AMD`** | Processors & AI Accelerators | $466.84 | `2026-11-03` | AMC | **0d** | `±14.5%` | 77/100 | Quan sát phản ứng giá sau BCTC ngày 2026-11-03 trước khi mở vị thế. |
| **`SMCI`** | AI Server Infrastructure | $30.44 | `2026-11-03` | AMC | **0d** | `±14.5%` | 45/100 | Quan sát phản ứng giá sau BCTC ngày 2026-11-03 trước khi mở vị thế. |

---

## 4. Kiểm Thử Sức Chịu Đựng Danh Mục Trước 3 Cú Sốc Vĩ Mô (`Institutional Stress-Testing`)

| Kịch bản Cú sốc Vĩ mô / Địa chính trị | Giả định S&P 500 | Tác động Dự kiến lên Danh mục | Mức Vượt trội (Alpha Bảo vệ) | Cơ chế Phòng vệ Tự động của Danh mục |
| :--- | :---: | :---: | :---: | :--- |
| **Kịch bản 1: Cú sốc Bán tháo Thị trường (S&P 500 sập -10.0%)**<br>*(Kích hoạt: Khủng hoảng thanh khoản hoặc dữ liệu kinh tế xấu đột biến)* | `-10.0%` | **`-4.39% NAV`** | **`+5.61%`** | Beta danh mục thấp (0.46) + Đệm 40.0% Tiền mặt/T-Bills + Kích hoạt Stop-Loss 2xATR & Chandelier Stop tự động |
| **Kịch bản 2: Cú sốc Lãi suất Fed Diều hâu (US 10Y Yield vọt lên 5.45%)**<br>*(Kích hoạt: PCE/CPI vượt 4.0% buộc Fed tăng lãi suất thêm +25–50 bps)* | `-6.5%` | **`-1.53% NAV`** | **`+4.97%`** | Nhóm Ngân hàng/Tài chính (JPM, V) và 40.0% T-Bills hưởng lợi trực tiếp bù đắp cho nhóm Công nghệ |
| **Kịch bản 3: Cú sốc Giá Dầu Địa chính trị (WTI Crude vọt lên $125/thùng)**<br>*(Kích hoạt: Gián đoạn nghiêm trọng eo biển Hormuz hoặc cơ sở lọc dầu toàn cầu)* | `-5.5%` | **`-0.58% NAV`** | **`+4.92%`** | Vị thế Dầu khí (OXY) và Phòng thủ Thiết yếu/Y tế (PG, JNJ, ABBV, COST) đóng vai trò Natural Hedge bảo vệ NAV |

---

## 5. Phiên Tranh Biện Đối Kháng Đa Tác Tử (`Adversarial Bull vs Bear Debate — CIO Anti-Paralysis Protocol`)
| Mã | Luận Điểm Bảo Vệ Của `Bull Agent` | Phản Biện Đào Bới Rủi Ro Của `Bear Agent` | Phán Quyết Hòa Giải Của `Master CIO` | Điểm Đồng Thuận |
| :--- | :--- | :--- | :--- | :---: |
| **`V`** | FCF chuẩn hóa đạt +$21.12B USD, tăng trưởng doanh thu +13.2% YoY, giá ($425.51) giữ cấu trúc trên MA200 ($342.2), điểm IC 77/100. | CẢNH BÁO ĐỊNH GIÁ/ĐÀ TĂNG: RSI tiệm cận vùng nóng (69.44) — Cần tránh mua đuổi giá xanh. | **APPROVED_WITH_60_40_SPLIT (Bác bỏ Veto định giá • Duyệt giải ngân chia nhịp 60/40 Limit Pullback)** | **`84.5/100`** |
| **`JPM`** | FCF chuẩn hóa đạt +$0.0B USD, tăng trưởng doanh thu +10.2% YoY, giá ($340.58) giữ cấu trúc trên MA200 ($322.95), điểm IC 90/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`PG`** | FCF chuẩn hóa đạt +$12.65B USD, tăng trưởng doanh thu +4.0% YoY, giá ($163.56) giữ cấu trúc trên MA200 ($148.92), điểm IC 89/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`COST`** | FCF chuẩn hóa đạt +$6.75B USD, tăng trưởng doanh thu +11.1% YoY, giá ($1040.55) giữ cấu trúc trên MA200 ($970.91), điểm IC 75/100. | CẢNH BÁO ĐỊNH GIÁ/ĐÀ TĂNG: Định giá Fwd P/E cao (41.58x) — Cần tránh mua đuổi giá xanh. | **APPROVED_WITH_60_40_SPLIT (Bác bỏ Veto định giá • Duyệt giải ngân chia nhịp 60/40 Limit Pullback)** | **`84.5/100`** |
| **`MSFT`** | FCF chuẩn hóa đạt +$2.99B USD, tăng trưởng doanh thu +18.8% YoY, giá ($507.12) giữ cấu trúc trên MA200 ($437.93), điểm IC 83/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`XOM`** | FCF chuẩn hóa đạt +$28.9B USD, tăng trưởng doanh thu +32.6% YoY, giá ($179.67) giữ cấu trúc trên MA200 ($154.6), điểm IC 81/100. | CẢNH BÁO ĐỊNH GIÁ/ĐÀ TĂNG: RSI tiệm cận vùng nóng (72.97) — Cần tránh mua đuổi giá xanh. | **APPROVED_WITH_60_40_SPLIT (Bác bỏ Veto định giá • Duyệt giải ngân chia nhịp 60/40 Limit Pullback)** | **`84.5/100`** |
| **`ABBV`** | FCF chuẩn hóa đạt +$0.0B USD, tăng trưởng doanh thu +10.3% YoY, giá ($288.84) giữ cấu trúc trên MA200 ($237.1), điểm IC 79/100. | CẢNH BÁO ĐỊNH GIÁ/ĐÀ TĂNG: RSI tiệm cận vùng nóng (72.78) — Cần tránh mua đuổi giá xanh. | **APPROVED_WITH_60_40_SPLIT (Bác bỏ Veto định giá • Duyệt giải ngân chia nhịp 60/40 Limit Pullback)** | **`84.5/100`** |
| **`JNJ`** | FCF chuẩn hóa đạt +$18.5B USD, tăng trưởng doanh thu +5.9% YoY, giá ($270.56) giữ cấu trúc trên MA200 ($246.99), điểm IC 82/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`TSM`** | FCF chuẩn hóa đạt +$36.81B USD, tăng trưởng doanh thu +50.9% YoY, giá ($398.63) giữ cấu trúc trên MA200 ($400.16), điểm IC 83/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`NVDA`** | FCF chuẩn hóa đạt +$41.81B USD, tăng trưởng doanh thu +105.9% YoY, giá ($202.06) giữ cấu trúc trên MA200 ($204.38), điểm IC 68/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
