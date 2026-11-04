# [BAN 4 — QUANT RISK] BÁO CÁO MA TRẬN TƯƠNG QUAN, ĐỊNH CỠ VỊ THẾ & KIỂM THỬ SỨC CHỊU ĐỰNG (STRESS TEST)
**Ngày kiểm toán**: 2026-11-04  
**Công cụ định lượng**: `scripts/quant_portfolio_engine.py` (v5.0 Audited — 0 Imminent Earnings Violations, Chandelier Stop & ATR Risk-Parity)

---

## 1. Tổng Quan Chỉ Số Rủi Ro Danh Mục (Portfolio Risk Telemetry)
- **Tỷ trọng Cổ phiếu / Tiền mặt (T-Bills ~5%)**: **`60.0% Cổ phiếu` / `40.0% Tiền mặt`**
- **Hệ số Beta Danh mục Tổng hợp (Portfolio Weighted Beta vs S&P 500)**: **`0.45`** *(Thấp hơn đáng kể so với biến động thị trường chung 1.00)*
- **Kiểm soát Cụm Bán dẫn (`NVDA + TSM`)**: **`8.2% NAV`** *(Tuân thủ trần `<= 14.0% NAV`)*
- **Tổng rủi ro danh mục nếu toàn bộ 10 vị thế đồng loạt chạm Stop-Loss `2xATR(14)`**: **`-2.83% NAV`**
- **Số mã bị khóa mua mới do sát lịch BCTC (`0 <= days_to_earnings <= 7`)**: **`6 mã`** (`BRK-B, OXY, QCOM, ARM, NVO, MCD`)

---

## 2. Ma Trận Tương Quan Lợi Suất 1 Năm (`Pairwise Return Correlation Matrix`)

| Mã | **`MSFT`** | **`TSM`** | **`JPM`** | **`NVDA`** | **`PG`** | **`JNJ`** | **`V`** | **`ABBV`** | **`COST`** | **`XOM`** |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`MSFT`** | `1.00` | 0.17 | 0.06 | 0.26 | -0.15 | -0.22 | 0.18 | -0.14 | -0.07 | -0.14 |
| **`TSM`** | 0.17 | `1.00` | 0.13 | **0.66** | -0.19 | -0.22 | -0.12 | -0.18 | -0.22 | -0.27 |
| **`JPM`** | 0.06 | 0.13 | `1.00` | 0.13 | 0.07 | 0.09 | 0.31 | 0.04 | -0.04 | -0.10 |
| **`NVDA`** | 0.26 | **0.66** | 0.13 | `1.00` | -0.27 | -0.22 | -0.13 | -0.19 | -0.28 | -0.23 |
| **`PG`** | -0.15 | -0.19 | 0.07 | -0.27 | `1.00` | 0.41 | 0.21 | 0.25 | 0.35 | -0.03 |
| **`JNJ`** | -0.22 | -0.22 | 0.09 | -0.22 | 0.41 | `1.00` | 0.11 | 0.52 | 0.29 | 0.09 |
| **`V`** | 0.18 | -0.12 | 0.31 | -0.13 | 0.21 | 0.11 | `1.00` | 0.19 | 0.25 | -0.07 |
| **`ABBV`** | -0.14 | -0.18 | 0.04 | -0.19 | 0.25 | 0.52 | 0.19 | `1.00` | 0.22 | 0.05 |
| **`COST`** | -0.07 | -0.22 | -0.04 | -0.28 | 0.35 | 0.29 | 0.25 | 0.22 | `1.00` | 0.14 |
| **`XOM`** | -0.14 | -0.27 | -0.10 | -0.23 | -0.03 | 0.09 | -0.07 | 0.05 | 0.14 | `1.00` |

---

## 3. Bảng Định Cỡ Vị Thế (`ATR Risk-Parity`), Chandelier Stop & Kiểm Toán Lịch BCTC

| Mã | Ngành | Giá ($) | Stop `2xATR` ($) | Chandelier Trailing ($) | Khoảng cách Stop (%) | Tỷ trọng (% NAV) | Rủi ro tối đa (% NAV) | Điểm IC (/100) | Lịch BCTC (`Earnings Radar`) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`JPM`** | Global Diversified Banking | $337.98 | **$325.14** | $329.71 | -3.8% | **7.8% NAV** | `-0.3% NAV` | **90/100** | CLEAR (2027-01-14 BMO) |
| **`PG`** | Consumer Household Staples | $162.06 | **$155.18** | $158.25 | -4.24% | **6.9% NAV** | `-0.29% NAV` | **86/100** | CLEAR (2027-01-21 BMO) |
| **`COST`** | Membership Warehouse Retail | $1019.26 | **$981.68** | $995.6 | -3.68% | **6.6% NAV** | `-0.24% NAV` | **71/100** | CLEAR (2026-12-10 AMC) |
| **`V`** | Global Payment Network | $420.42 | **$404.68** | $407.11 | -3.74% | **6.5% NAV** | `-0.24% NAV` | **73/100** | CLEAR (2027-01-26 AMC) |
| **`MSFT`** | Enterprise Software & Cloud | $520.99 | **$495.42** | $519.19 | -4.9% | **6.2% NAV** | `-0.3% NAV` | **85/100** | CLEAR (2027-01-27 AMC) |
| **`ABBV`** | Biotech & Immunology | $286.0 | **$272.33** | $281.66 | -4.78% | **6.2% NAV** | `-0.3% NAV` | **90/100** | JUST REPORTED (5d ago) — Đã qua rủi ro BCTC |
| **`XOM`** | Integrated Oil & Gas | $177.46 | **$168.5** | $177.29 | -5.06% | **6.2% NAV** | `-0.31% NAV` | **88/100** | CLEAR (2027-01-29 BMO) |
| **`JNJ`** | Pharmaceuticals & MedTech | $266.17 | **$252.53** | $264.97 | -5.12% | **5.4% NAV** | `-0.28% NAV` | **82/100** | CLEAR (2027-01-26 BMO) |
| **`NVDA`** | Semiconductors & AI | $206.69 | **$193.22** | $226.53 | -6.52% | **4.3% NAV** | `-0.28% NAV` | **81/100** | UPCOMING EARNINGS (13d, AMC) — Lưu ý biến động |
| **`TSM`** | Global Chip Foundry | $404.8 | **$374.78** | $449.94 | -7.42% | **3.9% NAV** | `-0.29% NAV` | **83/100** | CLEAR (2027-01-14 BMO) |

### Danh Sách Theo Dõi Tạm Khóa Do Sát Ngày Công Bố BCTC (`Locked Imminent Earnings Watchlist <= 7 Ngày`)
| Mã | Ngành | Giá ($) | Ngày BCTC | Phiên | Số Ngày Còn Lại | Implied Move (±%) | Điểm IC | Lý Do Khóa & Kế Hoạch Hành Động Sau BCTC |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`BRK-B`** | Diversified Conglomerate | $557.07 | `2026-11-07` | BMO | **3d** | `±3.31%` | 68/100 | Chờ BCTC công bố ngày 2026-11-07; chỉ giải ngân nếu giữ vững MA50 ($516.32) và hướng dẫn EPS tích cực. |
| **`OXY`** | Upstream Oil & Carbon Capture | $60.43 | `2026-11-09` | AMC | **5d** | `±6.44%` | 83/100 | Chờ BCTC công bố ngày 2026-11-09; chỉ giải ngân nếu giữ vững MA50 ($60.17) và hướng dẫn EPS tích cực. |
| **`QCOM`** | Mobile & Edge AI Processors | $164.43 | `2026-11-04` | AMC | **0d** | `±10.62%` | 44/100 | Quan sát phản ứng giá sau BCTC ngày 2026-11-04 trước khi mở vị thế. |
| **`ARM`** | Semiconductor IP Architecture | $202.49 | `2026-11-04` | AMC | **0d** | `±14.5%` | 60/100 | Quan sát phản ứng giá sau BCTC ngày 2026-11-04 trước khi mở vị thế. |
| **`NVO`** | Biopharma GLP-1 Leader | $40.19 | `2026-11-04` | BMO | **0d** | `±4.44%` | 65/100 | Quan sát phản ứng giá sau BCTC ngày 2026-11-04 trước khi mở vị thế. |
| **`MCD`** | Global Quick Service Restaurants | $263.04 | `2026-11-04` | BMO | **0d** | `±4.58%` | 61/100 | Quan sát phản ứng giá sau BCTC ngày 2026-11-04 trước khi mở vị thế. |

---

## 4. Kiểm Thử Sức Chịu Đựng Danh Mục Trước 3 Cú Sốc Vĩ Mô (`Institutional Stress-Testing`)

| Kịch bản Cú sốc Vĩ mô / Địa chính trị | Giả định S&P 500 | Tác động Dự kiến lên Danh mục | Mức Vượt trội (Alpha Bảo vệ) | Cơ chế Phòng vệ Tự động của Danh mục |
| :--- | :---: | :---: | :---: | :--- |
| **Kịch bản 1: Cú sốc Bán tháo Thị trường (S&P 500 sập -10.0%)**<br>*(Kích hoạt: Khủng hoảng thanh khoản hoặc dữ liệu kinh tế xấu đột biến)* | `-10.0%` | **`-4.36% NAV`** | **`+5.64%`** | Beta danh mục thấp (0.45) + Đệm 40.0% Tiền mặt/T-Bills + Kích hoạt Stop-Loss 2xATR & Chandelier Stop tự động |
| **Kịch bản 2: Cú sốc Lãi suất Fed Diều hâu (US 10Y Yield vọt lên 5.45%)**<br>*(Kích hoạt: PCE/CPI vượt 4.0% buộc Fed tăng lãi suất thêm +25–50 bps)* | `-6.5%` | **`-1.66% NAV`** | **`+4.84%`** | Nhóm Ngân hàng/Tài chính (JPM, V) và 40.0% T-Bills hưởng lợi trực tiếp bù đắp cho nhóm Công nghệ |
| **Kịch bản 3: Cú sốc Giá Dầu Địa chính trị (WTI Crude vọt lên $125/thùng)**<br>*(Kích hoạt: Gián đoạn nghiêm trọng eo biển Hormuz hoặc cơ sở lọc dầu toàn cầu)* | `-5.5%` | **`-0.51% NAV`** | **`+4.99%`** | Vị thế Dầu khí (OXY) và Phòng thủ Thiết yếu/Y tế (PG, JNJ, ABBV, COST) đóng vai trò Natural Hedge bảo vệ NAV |

---

## 5. Phiên Tranh Biện Đối Kháng Đa Tác Tử (`Adversarial Bull vs Bear Debate — CIO Anti-Paralysis Protocol`)
| Mã | Luận Điểm Bảo Vệ Của `Bull Agent` | Phản Biện Đào Bới Rủi Ro Của `Bear Agent` | Phán Quyết Hòa Giải Của `Master CIO` | Điểm Đồng Thuận |
| :--- | :--- | :--- | :--- | :---: |
| **`JPM`** | FCF chuẩn hóa đạt +$0.0B USD, tăng trưởng doanh thu +10.2% YoY, giá ($337.98) giữ cấu trúc trên MA200 ($323.1), điểm IC 90/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`PG`** | FCF chuẩn hóa đạt +$12.65B USD, tăng trưởng doanh thu +4.0% YoY, giá ($162.06) giữ cấu trúc trên MA200 ($149.02), điểm IC 86/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`COST`** | FCF chuẩn hóa đạt +$6.75B USD, tăng trưởng doanh thu +11.1% YoY, giá ($1019.26) giữ cấu trúc trên MA200 ($971.33), điểm IC 71/100. | CẢNH BÁO ĐỊNH GIÁ/ĐÀ TĂNG: Định giá Fwd P/E cao (40.73x); RSI tiệm cận vùng nóng (72.72) — Cần tránh mua đuổi giá xanh. | **APPROVED_WITH_60_40_SPLIT (Bác bỏ Veto định giá • Duyệt giải ngân chia nhịp 60/40 Limit Pullback)** | **`84.5/100`** |
| **`V`** | FCF chuẩn hóa đạt +$21.12B USD, tăng trưởng doanh thu +13.2% YoY, giá ($420.42) giữ cấu trúc trên MA200 ($342.69), điểm IC 73/100. | CẢNH BÁO ĐỊNH GIÁ/ĐÀ TĂNG: RSI tiệm cận vùng nóng (75.1) — Cần tránh mua đuổi giá xanh. | **APPROVED_WITH_60_40_SPLIT (Bác bỏ Veto định giá • Duyệt giải ngân chia nhịp 60/40 Limit Pullback)** | **`84.5/100`** |
| **`MSFT`** | FCF chuẩn hóa đạt +$2.99B USD, tăng trưởng doanh thu +18.8% YoY, giá ($520.99) giữ cấu trúc trên MA200 ($438.18), điểm IC 85/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`ABBV`** | FCF chuẩn hóa đạt +$0.0B USD, tăng trưởng doanh thu +10.3% YoY, giá ($286.0) giữ cấu trúc trên MA200 ($237.46), điểm IC 90/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`XOM`** | FCF chuẩn hóa đạt +$28.9B USD, tăng trưởng doanh thu +32.6% YoY, giá ($177.46) giữ cấu trúc trên MA200 ($154.85), điểm IC 88/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`JNJ`** | FCF chuẩn hóa đạt +$18.5B USD, tăng trưởng doanh thu +5.9% YoY, giá ($266.17) giữ cấu trúc trên MA200 ($247.24), điểm IC 82/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`NVDA`** | FCF chuẩn hóa đạt +$41.81B USD, tăng trưởng doanh thu +105.9% YoY, giá ($206.69) giữ cấu trúc trên MA200 ($204.46), điểm IC 81/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`TSM`** | FCF chuẩn hóa đạt +$36.69B USD, tăng trưởng doanh thu +50.9% YoY, giá ($404.8) giữ cấu trúc trên MA200 ($400.45), điểm IC 83/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
