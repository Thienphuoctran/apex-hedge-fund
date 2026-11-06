# [BAN 4 — QUANT RISK] BÁO CÁO MA TRẬN TƯƠNG QUAN, ĐỊNH CỠ VỊ THẾ & KIỂM THỬ SỨC CHỊU ĐỰNG (STRESS TEST)
**Ngày kiểm toán**: 2026-11-06  
**Công cụ định lượng**: `scripts/quant_portfolio_engine.py` (v5.0 Audited — 0 Imminent Earnings Violations, Chandelier Stop & ATR Risk-Parity)

---

## 1. Tổng Quan Chỉ Số Rủi Ro Danh Mục (Portfolio Risk Telemetry)
- **Tỷ trọng Cổ phiếu / Tiền mặt (T-Bills ~5%)**: **`60.0% Cổ phiếu` / `40.0% Tiền mặt`**
- **Hệ số Beta Danh mục Tổng hợp (Portfolio Weighted Beta vs S&P 500)**: **`0.43`** *(Thấp hơn đáng kể so với biến động thị trường chung 1.00)*
- **Kiểm soát Cụm Bán dẫn (`NVDA + TSM`)**: **`6.4% NAV`** *(Tuân thủ trần `<= 14.0% NAV`)*
- **Tổng rủi ro danh mục nếu toàn bộ 10 vị thế đồng loạt chạm Stop-Loss `2xATR(14)`**: **`-3.18% NAV`**
- **Số mã bị khóa mua mới do sát lịch BCTC (`0 <= days_to_earnings <= 7`)**: **`2 mã`** (`BRK-B, OXY`)

---

## 2. Ma Trận Tương Quan Lợi Suất 1 Năm (`Pairwise Return Correlation Matrix`)

| Mã | **`MSFT`** | **`TSM`** | **`JPM`** | **`NVDA`** | **`PG`** | **`JNJ`** | **`V`** | **`ABBV`** | **`COST`** | **`XOM`** |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`MSFT`** | `1.00` | 0.18 | 0.12 | 0.25 | -0.12 | -0.18 | 0.21 | -0.10 | -0.06 | -0.16 |
| **`TSM`** | 0.18 | `1.00` | 0.16 | **0.68** | -0.19 | -0.20 | -0.08 | -0.15 | -0.24 | -0.22 |
| **`JPM`** | 0.12 | 0.16 | `1.00` | 0.15 | 0.09 | 0.13 | 0.36 | 0.08 | -0.02 | -0.11 |
| **`NVDA`** | 0.25 | **0.68** | 0.15 | `1.00` | -0.27 | -0.21 | -0.11 | -0.16 | -0.31 | -0.18 |
| **`PG`** | -0.12 | -0.19 | 0.09 | -0.27 | `1.00` | 0.42 | 0.23 | 0.27 | 0.36 | -0.06 |
| **`JNJ`** | -0.18 | -0.20 | 0.13 | -0.21 | 0.42 | `1.00` | 0.15 | 0.53 | 0.31 | 0.07 |
| **`V`** | 0.21 | -0.08 | 0.36 | -0.11 | 0.23 | 0.15 | `1.00` | 0.22 | 0.26 | -0.08 |
| **`ABBV`** | -0.10 | -0.15 | 0.08 | -0.16 | 0.27 | 0.53 | 0.22 | `1.00` | 0.22 | 0.03 |
| **`COST`** | -0.06 | -0.24 | -0.02 | -0.31 | 0.36 | 0.31 | 0.26 | 0.22 | `1.00` | 0.11 |
| **`XOM`** | -0.16 | -0.22 | -0.11 | -0.18 | -0.06 | 0.07 | -0.08 | 0.03 | 0.11 | `1.00` |

---

## 3. Bảng Định Cỡ Vị Thế (`ATR Risk-Parity`), Chandelier Stop & Kiểm Toán Lịch BCTC

| Mã | Ngành | Giá ($) | Stop `2xATR` ($) | Chandelier Trailing ($) | Khoảng cách Stop (%) | Tỷ trọng (% NAV) | Rủi ro tối đa (% NAV) | Điểm IC (/100) | Lịch BCTC (`Earnings Radar`) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`JPM`** | Global Diversified Banking | $337.34 | **$321.72** | $340.28 | -4.62% | **7.5% NAV** | `-0.35% NAV` | **90/100** | CLEAR (2027-01-14 BMO) |
| **`V`** | Global Payment Network | $422.59 | **$404.07** | $419.08 | -4.38% | **7.5% NAV** | `-0.33% NAV` | **80/100** | CLEAR (2027-01-26 AMC) |
| **`COST`** | Membership Warehouse Retail | $1065.59 | **$1025.64** | $1031.61 | -3.74% | **7.5% NAV** | `-0.28% NAV` | **75/100** | CLEAR (2026-12-10 AMC) |
| **`PG`** | Consumer Household Staples | $167.1 | **$159.86** | $161.47 | -4.34% | **7.2% NAV** | `-0.31% NAV` | **82/100** | CLEAR (2027-01-21 BMO) |
| **`ABBV`** | Biotech & Immunology | $288.24 | **$273.06** | $283.95 | -5.26% | **6.6% NAV** | `-0.35% NAV` | **90/100** | CLEAR (2026-10-30 BMO) |
| **`JNJ`** | Pharmaceuticals & MedTech | $272.32 | **$257.58** | $263.59 | -5.42% | **5.9% NAV** | `-0.32% NAV` | **82/100** | CLEAR (2027-01-26 BMO) |
| **`MSFT`** | Enterprise Software & Cloud | $535.93 | **$505.09** | $520.59 | -5.76% | **5.8% NAV** | `-0.33% NAV` | **82/100** | CLEAR (2027-01-27 AMC) |
| **`XOM`** | Integrated Oil & Gas | $165.3 | **$155.08** | $175.73 | -6.18% | **5.6% NAV** | `-0.35% NAV` | **86/100** | CLEAR (2027-01-29 BMO) |
| **`NVDA`** | Semiconductors & AI | $181.6 | **$166.68** | $220.42 | -8.22% | **3.4% NAV** | `-0.28% NAV` | **70/100** | UPCOMING EARNINGS (11d, AMC) — Lưu ý biến động |
| **`TSM`** | Global Chip Foundry | $353.1 | **$319.98** | $434.4 | -9.38% | **3.0% NAV** | `-0.28% NAV` | **72/100** | CLEAR (2027-01-14 BMO) |

### Danh Sách Theo Dõi Tạm Khóa Do Sát Ngày Công Bố BCTC (`Locked Imminent Earnings Watchlist <= 7 Ngày`)
| Mã | Ngành | Giá ($) | Ngày BCTC | Phiên | Số Ngày Còn Lại | Implied Move (±%) | Điểm IC | Lý Do Khóa & Kế Hoạch Hành Động Sau BCTC |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`BRK-B`** | Diversified Conglomerate | $572.33 | `2026-11-07` | BMO | **1d** | `±3.9%` | 64/100 | Chờ BCTC công bố ngày 2026-11-07; chỉ giải ngân nếu giữ vững MA50 ($520.22) và hướng dẫn EPS tích cực. |
| **`OXY`** | Upstream Oil & Carbon Capture | $56.36 | `2026-11-09` | AMC | **3d** | `±7.87%` | 81/100 | Chờ BCTC công bố ngày 2026-11-09; chỉ giải ngân nếu giữ vững MA50 ($60.11) và hướng dẫn EPS tích cực. |

---

## 4. Kiểm Thử Sức Chịu Đựng Danh Mục Trước 3 Cú Sốc Vĩ Mô (`Institutional Stress-Testing`)

| Kịch bản Cú sốc Vĩ mô / Địa chính trị | Giả định S&P 500 | Tác động Dự kiến lên Danh mục | Mức Vượt trội (Alpha Bảo vệ) | Cơ chế Phòng vệ Tự động của Danh mục |
| :--- | :---: | :---: | :---: | :--- |
| **Kịch bản 1: Cú sốc Bán tháo Thị trường (S&P 500 sập -10.0%)**<br>*(Kích hoạt: Khủng hoảng thanh khoản hoặc dữ liệu kinh tế xấu đột biến)* | `-10.0%` | **`-4.15% NAV`** | **`+5.85%`** | Beta danh mục thấp (0.43) + Đệm 40.0% Tiền mặt/T-Bills + Kích hoạt Stop-Loss 2xATR & Chandelier Stop tự động |
| **Kịch bản 2: Cú sốc Lãi suất Fed Diều hâu (US 10Y Yield vọt lên 5.45%)**<br>*(Kích hoạt: PCE/CPI vượt 4.0% buộc Fed tăng lãi suất thêm +25–50 bps)* | `-6.5%` | **`-1.56% NAV`** | **`+4.94%`** | Nhóm Ngân hàng/Tài chính (JPM, V) và 40.0% T-Bills hưởng lợi trực tiếp bù đắp cho nhóm Công nghệ |
| **Kịch bản 3: Cú sốc Giá Dầu Địa chính trị (WTI Crude vọt lên $125/thùng)**<br>*(Kích hoạt: Gián đoạn nghiêm trọng eo biển Hormuz hoặc cơ sở lọc dầu toàn cầu)* | `-5.5%` | **`-0.55% NAV`** | **`+4.95%`** | Vị thế Dầu khí (OXY) và Phòng thủ Thiết yếu/Y tế (PG, JNJ, ABBV, COST) đóng vai trò Natural Hedge bảo vệ NAV |

---

## 5. Phiên Tranh Biện Đối Kháng Đa Tác Tử (`Adversarial Bull vs Bear Debate — CIO Anti-Paralysis Protocol`)
| Mã | Luận Điểm Bảo Vệ Của `Bull Agent` | Phản Biện Đào Bới Rủi Ro Của `Bear Agent` | Phán Quyết Hòa Giải Của `Master CIO` | Điểm Đồng Thuận |
| :--- | :--- | :--- | :--- | :---: |
| **`JPM`** | FCF chuẩn hóa đạt +$0.0B USD, tăng trưởng doanh thu +10.2% YoY, giá ($337.34) giữ cấu trúc trên MA200 ($323.66), điểm IC 90/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`V`** | FCF chuẩn hóa đạt +$21.12B USD, tăng trưởng doanh thu +13.2% YoY, giá ($422.59) giữ cấu trúc trên MA200 ($344.19), điểm IC 80/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`COST`** | FCF chuẩn hóa đạt +$6.75B USD, tăng trưởng doanh thu +11.1% YoY, giá ($1065.59) giữ cấu trúc trên MA200 ($972.43), điểm IC 75/100. | CẢNH BÁO ĐỊNH GIÁ/ĐÀ TĂNG: Định giá Fwd P/E cao (42.58x); RSI tiệm cận vùng nóng (72.05) — Cần tránh mua đuổi giá xanh. | **APPROVED_WITH_60_40_SPLIT (Bác bỏ Veto định giá • Duyệt giải ngân chia nhịp 60/40 Limit Pullback)** | **`84.5/100`** |
| **`PG`** | FCF chuẩn hóa đạt +$12.65B USD, tăng trưởng doanh thu +4.0% YoY, giá ($167.1) giữ cấu trúc trên MA200 ($149.31), điểm IC 82/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`ABBV`** | FCF chuẩn hóa đạt +$17.69B USD, tăng trưởng doanh thu +10.3% YoY, giá ($288.24) giữ cấu trúc trên MA200 ($238.58), điểm IC 90/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`JNJ`** | FCF chuẩn hóa đạt +$18.5B USD, tăng trưởng doanh thu +5.9% YoY, giá ($272.32) giữ cấu trúc trên MA200 ($248.04), điểm IC 82/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`MSFT`** | FCF chuẩn hóa đạt +$2.99B USD, tăng trưởng doanh thu +18.8% YoY, giá ($535.93) giữ cấu trúc trên MA200 ($439.45), điểm IC 82/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`XOM`** | FCF chuẩn hóa đạt +$28.9B USD, tăng trưởng doanh thu +32.6% YoY, giá ($165.3) giữ cấu trúc trên MA200 ($155.44), điểm IC 86/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`NVDA`** | FCF chuẩn hóa đạt +$41.81B USD, tăng trưởng doanh thu +105.9% YoY, giá ($181.6) giữ cấu trúc trên MA200 ($204.66), điểm IC 70/100. | VI PHẠM CẤU TRÚC: Gãy cấu trúc MA200 ($181.6 < $204.66) | **ABSOLUTE_VETO (Từ chối giải ngân do vi phạm lằn ranh đỏ cấu trúc)** | **`35.0/100`** |
| **`TSM`** | FCF chuẩn hóa đạt +$36.69B USD, tăng trưởng doanh thu +50.9% YoY, giá ($353.1) giữ cấu trúc trên MA200 ($401.24), điểm IC 72/100. | VI PHẠM CẤU TRÚC: Gãy cấu trúc MA200 ($353.1 < $401.24) | **ABSOLUTE_VETO (Từ chối giải ngân do vi phạm lằn ranh đỏ cấu trúc)** | **`35.0/100`** |
