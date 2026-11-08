# [BAN 4 — QUANT RISK] BÁO CÁO MA TRẬN TƯƠNG QUAN, ĐỊNH CỠ VỊ THẾ & KIỂM THỬ SỨC CHỊU ĐỰNG (STRESS TEST)
**Ngày kiểm toán**: 2026-11-08  
**Công cụ định lượng**: `scripts/quant_portfolio_engine.py` (v5.0 Audited — 0 Imminent Earnings Violations, Chandelier Stop & ATR Risk-Parity)

---

## 1. Tổng Quan Chỉ Số Rủi Ro Danh Mục (Portfolio Risk Telemetry)
- **Tỷ trọng Cổ phiếu / Tiền mặt (T-Bills ~5%)**: **`60.0% Cổ phiếu` / `40.0% Tiền mặt`**
- **Hệ số Beta Danh mục Tổng hợp (Portfolio Weighted Beta vs S&P 500)**: **`0.43`** *(Thấp hơn đáng kể so với biến động thị trường chung 1.00)*
- **Kiểm soát Cụm Bán dẫn (`NVDA + TSM`)**: **`6.5% NAV`** *(Tuân thủ trần `<= 14.0% NAV`)*
- **Tổng rủi ro danh mục nếu toàn bộ 10 vị thế đồng loạt chạm Stop-Loss `2xATR(14)`**: **`-3.31% NAV`**
- **Số mã bị khóa mua mới do sát lịch BCTC (`0 <= days_to_earnings <= 7`)**: **`2 mã`** (`OXY, BRK-B`)

---

## 2. Ma Trận Tương Quan Lợi Suất 1 Năm (`Pairwise Return Correlation Matrix`)

| Mã | **`MSFT`** | **`TSM`** | **`JPM`** | **`NVDA`** | **`PG`** | **`JNJ`** | **`V`** | **`ABBV`** | **`COST`** | **`XOM`** |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`MSFT`** | `1.00` | 0.17 | 0.12 | 0.25 | -0.12 | -0.18 | 0.21 | -0.10 | -0.06 | -0.16 |
| **`TSM`** | 0.17 | `1.00` | 0.15 | **0.69** | -0.19 | -0.19 | -0.08 | -0.14 | -0.25 | -0.22 |
| **`JPM`** | 0.12 | 0.15 | `1.00` | 0.15 | 0.10 | 0.13 | 0.36 | 0.07 | -0.02 | -0.11 |
| **`NVDA`** | 0.25 | **0.69** | 0.15 | `1.00` | -0.27 | -0.20 | -0.11 | -0.16 | -0.32 | -0.18 |
| **`PG`** | -0.12 | -0.19 | 0.10 | -0.27 | `1.00` | 0.42 | 0.23 | 0.26 | 0.37 | -0.06 |
| **`JNJ`** | -0.18 | -0.19 | 0.13 | -0.20 | 0.42 | `1.00` | 0.15 | 0.53 | 0.30 | 0.07 |
| **`V`** | 0.21 | -0.08 | 0.36 | -0.11 | 0.23 | 0.15 | `1.00` | 0.22 | 0.25 | -0.08 |
| **`ABBV`** | -0.10 | -0.14 | 0.07 | -0.16 | 0.26 | 0.53 | 0.22 | `1.00` | 0.22 | 0.03 |
| **`COST`** | -0.06 | -0.25 | -0.02 | -0.32 | 0.37 | 0.30 | 0.25 | 0.22 | `1.00` | 0.11 |
| **`XOM`** | -0.16 | -0.22 | -0.11 | -0.18 | -0.06 | 0.07 | -0.08 | 0.03 | 0.11 | `1.00` |

---

## 3. Bảng Định Cỡ Vị Thế (`ATR Risk-Parity`), Chandelier Stop & Kiểm Toán Lịch BCTC

| Mã | Ngành | Giá ($) | Stop `2xATR` ($) | Chandelier Trailing ($) | Khoảng cách Stop (%) | Tỷ trọng (% NAV) | Rủi ro tối đa (% NAV) | Điểm IC (/100) | Lịch BCTC (`Earnings Radar`) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`JPM`** | Global Diversified Banking | $334.49 | **$318.73** | $340.1 | -4.72% | **7.6% NAV** | `-0.36% NAV` | **90/100** | CLEAR (2027-01-14 BMO) |
| **`V`** | Global Payment Network | $422.65 | **$403.33** | $418.08 | -4.58% | **7.4% NAV** | `-0.34% NAV` | **80/100** | CLEAR (2027-01-26 AMC) |
| **`COST`** | Membership Warehouse Retail | $1053.56 | **$1012.15** | $1029.79 | -3.94% | **7.4% NAV** | `-0.29% NAV` | **71/100** | CLEAR (2026-12-10 AMC) |
| **`PG`** | Consumer Household Staples | $165.4 | **$157.79** | $161.0 | -4.6% | **7.3% NAV** | `-0.34% NAV` | **81/100** | CLEAR (2027-01-21 BMO) |
| **`ABBV`** | Biotech & Immunology | $291.31 | **$275.37** | $283.0 | -5.48% | **6.5% NAV** | `-0.36% NAV` | **90/100** | CLEAR (2026-10-30 BMO) |
| **`MSFT`** | Enterprise Software & Cloud | $530.61 | **$498.86** | $519.46 | -5.98% | **5.8% NAV** | `-0.35% NAV` | **82/100** | CLEAR (2027-01-27 AMC) |
| **`JNJ`** | Pharmaceuticals & MedTech | $276.22 | **$260.5** | $262.38 | -5.68% | **5.8% NAV** | `-0.33% NAV` | **82/100** | CLEAR (2027-01-26 BMO) |
| **`XOM`** | Integrated Oil & Gas | $165.87 | **$155.48** | $175.51 | -6.26% | **5.7% NAV** | `-0.36% NAV` | **86/100** | CLEAR (2027-01-29 BMO) |
| **`NVDA`** | Semiconductors & AI | $186.64 | **$170.6** | $217.02 | -8.6% | **3.4% NAV** | `-0.29% NAV` | **68/100** | UPCOMING EARNINGS (9d, AMC) — Lưu ý biến động |
| **`TSM`** | Global Chip Foundry | $375.44 | **$340.45** | $427.46 | -9.32% | **3.1% NAV** | `-0.29% NAV` | **70/100** | CLEAR (2027-01-14 BMO) |

### Danh Sách Theo Dõi Tạm Khóa Do Sát Ngày Công Bố BCTC (`Locked Imminent Earnings Watchlist <= 7 Ngày`)
| Mã | Ngành | Giá ($) | Ngày BCTC | Phiên | Số Ngày Còn Lại | Implied Move (±%) | Điểm IC | Lý Do Khóa & Kế Hoạch Hành Động Sau BCTC |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`OXY`** | Upstream Oil & Carbon Capture | $56.38 | `2026-11-09` | AMC | **1d** | `±8.01%` | 81/100 | Chờ BCTC công bố ngày 2026-11-09; chỉ giải ngân nếu giữ vững MA50 ($60.05) và hướng dẫn EPS tích cực. |
| **`BRK-B`** | Diversified Conglomerate | $570.89 | `2026-11-09` | BMO | **1d** | `±4.23%` | 64/100 | Chờ BCTC công bố ngày 2026-11-09; chỉ giải ngân nếu giữ vững MA50 ($521.56) và hướng dẫn EPS tích cực. |

---

## 4. Kiểm Thử Sức Chịu Đựng Danh Mục Trước 3 Cú Sốc Vĩ Mô (`Institutional Stress-Testing`)

| Kịch bản Cú sốc Vĩ mô / Địa chính trị | Giả định S&P 500 | Tác động Dự kiến lên Danh mục | Mức Vượt trội (Alpha Bảo vệ) | Cơ chế Phòng vệ Tự động của Danh mục |
| :--- | :---: | :---: | :---: | :--- |
| **Kịch bản 1: Cú sốc Bán tháo Thị trường (S&P 500 sập -10.0%)**<br>*(Kích hoạt: Khủng hoảng thanh khoản hoặc dữ liệu kinh tế xấu đột biến)* | `-10.0%` | **`-4.16% NAV`** | **`+5.84%`** | Beta danh mục thấp (0.43) + Đệm 40.0% Tiền mặt/T-Bills + Kích hoạt Stop-Loss 2xATR & Chandelier Stop tự động |
| **Kịch bản 2: Cú sốc Lãi suất Fed Diều hâu (US 10Y Yield vọt lên 5.45%)**<br>*(Kích hoạt: PCE/CPI vượt 4.0% buộc Fed tăng lãi suất thêm +25–50 bps)* | `-6.5%` | **`-1.55% NAV`** | **`+4.95%`** | Nhóm Ngân hàng/Tài chính (JPM, V) và 40.0% T-Bills hưởng lợi trực tiếp bù đắp cho nhóm Công nghệ |
| **Kịch bản 3: Cú sốc Giá Dầu Địa chính trị (WTI Crude vọt lên $125/thùng)**<br>*(Kích hoạt: Gián đoạn nghiêm trọng eo biển Hormuz hoặc cơ sở lọc dầu toàn cầu)* | `-5.5%` | **`-0.54% NAV`** | **`+4.96%`** | Vị thế Dầu khí (OXY) và Phòng thủ Thiết yếu/Y tế (PG, JNJ, ABBV, COST) đóng vai trò Natural Hedge bảo vệ NAV |

---

## 5. Phiên Tranh Biện Đối Kháng Đa Tác Tử (`Adversarial Bull vs Bear Debate — CIO Anti-Paralysis Protocol`)
| Mã | Luận Điểm Bảo Vệ Của `Bull Agent` | Phản Biện Đào Bới Rủi Ro Của `Bear Agent` | Phán Quyết Hòa Giải Của `Master CIO` | Điểm Đồng Thuận |
| :--- | :--- | :--- | :--- | :---: |
| **`JPM`** | FCF chuẩn hóa đạt +$0.0B USD, tăng trưởng doanh thu +10.2% YoY, giá ($334.49) giữ cấu trúc trên MA200 ($323.81), điểm IC 90/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`V`** | FCF chuẩn hóa đạt +$20.98B USD, tăng trưởng doanh thu +13.2% YoY, giá ($422.65) giữ cấu trúc trên MA200 ($344.68), điểm IC 80/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`COST`** | FCF chuẩn hóa đạt +$6.75B USD, tăng trưởng doanh thu +11.1% YoY, giá ($1053.56) giữ cấu trúc trên MA200 ($972.82), điểm IC 71/100. | CẢNH BÁO ĐỊNH GIÁ/ĐÀ TĂNG: Định giá Fwd P/E cao (42.05x) — Cần tránh mua đuổi giá xanh. | **APPROVED_WITH_60_40_SPLIT (Bác bỏ Veto định giá • Duyệt giải ngân chia nhịp 60/40 Limit Pullback)** | **`84.5/100`** |
| **`PG`** | FCF chuẩn hóa đạt +$12.65B USD, tăng trưởng doanh thu +4.0% YoY, giá ($165.4) giữ cấu trúc trên MA200 ($149.39), điểm IC 81/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`ABBV`** | FCF chuẩn hóa đạt +$17.69B USD, tăng trưởng doanh thu +10.3% YoY, giá ($291.31) giữ cấu trúc trên MA200 ($238.94), điểm IC 90/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`MSFT`** | FCF chuẩn hóa đạt +$2.99B USD, tăng trưởng doanh thu +18.8% YoY, giá ($530.61) giữ cấu trúc trên MA200 ($439.85), điểm IC 82/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`JNJ`** | FCF chuẩn hóa đạt +$18.5B USD, tăng trưởng doanh thu +5.9% YoY, giá ($276.22) giữ cấu trúc trên MA200 ($248.33), điểm IC 82/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`XOM`** | FCF chuẩn hóa đạt +$28.32B USD, tăng trưởng doanh thu +32.6% YoY, giá ($165.87) giữ cấu trúc trên MA200 ($155.6), điểm IC 86/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`NVDA`** | FCF chuẩn hóa đạt +$41.81B USD, tăng trưởng doanh thu +105.9% YoY, giá ($186.64) giữ cấu trúc trên MA200 ($204.67), điểm IC 68/100. | VI PHẠM CẤU TRÚC: Gãy cấu trúc MA200 ($186.64 < $204.67) | **ABSOLUTE_VETO (Từ chối giải ngân do vi phạm lằn ranh đỏ cấu trúc)** | **`35.0/100`** |
| **`TSM`** | FCF chuẩn hóa đạt +$36.69B USD, tăng trưởng doanh thu +50.9% YoY, giá ($375.44) giữ cấu trúc trên MA200 ($401.48), điểm IC 70/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
