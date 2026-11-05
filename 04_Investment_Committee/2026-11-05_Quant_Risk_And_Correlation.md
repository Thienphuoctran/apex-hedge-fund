# [BAN 4 — QUANT RISK] BÁO CÁO MA TRẬN TƯƠNG QUAN, ĐỊNH CỠ VỊ THẾ & KIỂM THỬ SỨC CHỊU ĐỰNG (STRESS TEST)
**Ngày kiểm toán**: 2026-11-05  
**Công cụ định lượng**: `scripts/quant_portfolio_engine.py` (v5.0 Audited — 0 Imminent Earnings Violations, Chandelier Stop & ATR Risk-Parity)

---

## 1. Tổng Quan Chỉ Số Rủi Ro Danh Mục (Portfolio Risk Telemetry)
- **Tỷ trọng Cổ phiếu / Tiền mặt (T-Bills ~5%)**: **`60.0% Cổ phiếu` / `40.0% Tiền mặt`**
- **Hệ số Beta Danh mục Tổng hợp (Portfolio Weighted Beta vs S&P 500)**: **`0.44`** *(Thấp hơn đáng kể so với biến động thị trường chung 1.00)*
- **Kiểm soát Cụm Bán dẫn (`NVDA + TSM`)**: **`6.7% NAV`** *(Tuân thủ trần `<= 14.0% NAV`)*
- **Tổng rủi ro danh mục nếu toàn bộ 10 vị thế đồng loạt chạm Stop-Loss `2xATR(14)`**: **`-2.66% NAV`**
- **Số mã bị khóa mua mới do sát lịch BCTC (`0 <= days_to_earnings <= 7`)**: **`2 mã`** (`BRK-B, OXY`)

---

## 2. Ma Trận Tương Quan Lợi Suất 1 Năm (`Pairwise Return Correlation Matrix`)

| Mã | **`MSFT`** | **`TSM`** | **`JPM`** | **`NVDA`** | **`PG`** | **`JNJ`** | **`V`** | **`ABBV`** | **`COST`** | **`XOM`** |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`MSFT`** | `1.00` | 0.18 | 0.06 | 0.26 | -0.16 | -0.23 | 0.17 | -0.14 | -0.08 | -0.14 |
| **`TSM`** | 0.18 | `1.00` | 0.13 | **0.66** | -0.19 | -0.22 | -0.12 | -0.18 | -0.22 | -0.28 |
| **`JPM`** | 0.06 | 0.13 | `1.00` | 0.13 | 0.07 | 0.09 | 0.32 | 0.04 | -0.03 | -0.10 |
| **`NVDA`** | 0.26 | **0.66** | 0.13 | `1.00` | -0.27 | -0.22 | -0.13 | -0.19 | -0.29 | -0.23 |
| **`PG`** | -0.16 | -0.19 | 0.07 | -0.27 | `1.00` | 0.41 | 0.21 | 0.25 | 0.35 | -0.03 |
| **`JNJ`** | -0.23 | -0.22 | 0.09 | -0.22 | 0.41 | `1.00` | 0.12 | 0.52 | 0.30 | 0.10 |
| **`V`** | 0.17 | -0.12 | 0.32 | -0.13 | 0.21 | 0.12 | `1.00` | 0.20 | 0.26 | -0.06 |
| **`ABBV`** | -0.14 | -0.18 | 0.04 | -0.19 | 0.25 | 0.52 | 0.20 | `1.00` | 0.22 | 0.05 |
| **`COST`** | -0.08 | -0.22 | -0.03 | -0.29 | 0.35 | 0.30 | 0.26 | 0.22 | `1.00` | 0.14 |
| **`XOM`** | -0.14 | -0.28 | -0.10 | -0.23 | -0.03 | 0.10 | -0.06 | 0.05 | 0.14 | `1.00` |

---

## 3. Bảng Định Cỡ Vị Thế (`ATR Risk-Parity`), Chandelier Stop & Kiểm Toán Lịch BCTC

| Mã | Ngành | Giá ($) | Stop `2xATR` ($) | Chandelier Trailing ($) | Khoảng cách Stop (%) | Tỷ trọng (% NAV) | Rủi ro tối đa (% NAV) | Điểm IC (/100) | Lịch BCTC (`Earnings Radar`) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`JPM`** | Global Diversified Banking | $352.11 | **$339.97** | $330.57 | -3.44% | **9.0% NAV** | `-0.31% NAV` | **96/100** | CLEAR (2027-01-14 BMO) |
| **`V`** | Global Payment Network | $436.57 | **$420.89** | $407.18 | -3.6% | **7.3% NAV** | `-0.26% NAV` | **81/100** | CLEAR (2027-01-26 AMC) |
| **`PG`** | Consumer Household Staples | $167.32 | **$160.65** | $158.51 | -3.98% | **7.1% NAV** | `-0.28% NAV` | **85/100** | CLEAR (2027-01-21 BMO) |
| **`COST`** | Membership Warehouse Retail | $1046.47 | **$1009.83** | $996.77 | -3.5% | **6.9% NAV** | `-0.24% NAV` | **78/100** | CLEAR (2026-12-10 AMC) |
| **`MSFT`** | Enterprise Software & Cloud | $555.8 | **$529.78** | $518.63 | -4.68% | **6.0% NAV** | `-0.28% NAV` | **82/100** | CLEAR (2027-01-27 AMC) |
| **`ABBV`** | Biotech & Immunology | $294.83 | **$281.8** | $282.45 | -4.42% | **6.0% NAV** | `-0.27% NAV` | **85/100** | CLEAR (2026-10-30 BMO) |
| **`XOM`** | Integrated Oil & Gas | $169.27 | **$160.34** | $177.34 | -5.28% | **5.7% NAV** | `-0.3% NAV` | **88/100** | CLEAR (2027-01-29 BMO) |
| **`JNJ`** | Pharmaceuticals & MedTech | $276.32 | **$262.63** | $264.9 | -4.96% | **5.3% NAV** | `-0.26% NAV` | **82/100** | CLEAR (2027-01-26 BMO) |
| **`NVDA`** | Semiconductors & AI | $200.13 | **$186.92** | $226.85 | -6.6% | **3.5% NAV** | `-0.23% NAV` | **68/100** | UPCOMING EARNINGS (12d, AMC) — Lưu ý biến động |
| **`TSM`** | Global Chip Foundry | $395.75 | **$366.77** | $451.25 | -7.32% | **3.2% NAV** | `-0.23% NAV` | **70/100** | CLEAR (2027-01-14 BMO) |

### Danh Sách Theo Dõi Tạm Khóa Do Sát Ngày Công Bố BCTC (`Locked Imminent Earnings Watchlist <= 7 Ngày`)
| Mã | Ngành | Giá ($) | Ngày BCTC | Phiên | Số Ngày Còn Lại | Implied Move (±%) | Điểm IC | Lý Do Khóa & Kế Hoạch Hành Động Sau BCTC |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`BRK-B`** | Diversified Conglomerate | $579.09 | `2026-11-07` | BMO | **2d** | `±3.15%` | 68/100 | Chờ BCTC công bố ngày 2026-11-07; chỉ giải ngân nếu giữ vững MA50 ($517.37) và hướng dẫn EPS tích cực. |
| **`OXY`** | Upstream Oil & Carbon Capture | $57.33 | `2026-11-09` | AMC | **4d** | `±6.84%` | 81/100 | Chờ BCTC công bố ngày 2026-11-09; chỉ giải ngân nếu giữ vững MA50 ($60.18) và hướng dẫn EPS tích cực. |

---

## 4. Kiểm Thử Sức Chịu Đựng Danh Mục Trước 3 Cú Sốc Vĩ Mô (`Institutional Stress-Testing`)

| Kịch bản Cú sốc Vĩ mô / Địa chính trị | Giả định S&P 500 | Tác động Dự kiến lên Danh mục | Mức Vượt trội (Alpha Bảo vệ) | Cơ chế Phòng vệ Tự động của Danh mục |
| :--- | :---: | :---: | :---: | :--- |
| **Kịch bản 1: Cú sốc Bán tháo Thị trường (S&P 500 sập -10.0%)**<br>*(Kích hoạt: Khủng hoảng thanh khoản hoặc dữ liệu kinh tế xấu đột biến)* | `-10.0%` | **`-4.28% NAV`** | **`+5.72%`** | Beta danh mục thấp (0.44) + Đệm 40.0% Tiền mặt/T-Bills + Kích hoạt Stop-Loss 2xATR & Chandelier Stop tự động |
| **Kịch bản 2: Cú sốc Lãi suất Fed Diều hâu (US 10Y Yield vọt lên 5.45%)**<br>*(Kích hoạt: PCE/CPI vượt 4.0% buộc Fed tăng lãi suất thêm +25–50 bps)* | `-6.5%` | **`-1.46% NAV`** | **`+5.04%`** | Nhóm Ngân hàng/Tài chính (JPM, V) và 40.0% T-Bills hưởng lợi trực tiếp bù đắp cho nhóm Công nghệ |
| **Kịch bản 3: Cú sốc Giá Dầu Địa chính trị (WTI Crude vọt lên $125/thùng)**<br>*(Kích hoạt: Gián đoạn nghiêm trọng eo biển Hormuz hoặc cơ sở lọc dầu toàn cầu)* | `-5.5%` | **`-0.6% NAV`** | **`+4.9%`** | Vị thế Dầu khí (OXY) và Phòng thủ Thiết yếu/Y tế (PG, JNJ, ABBV, COST) đóng vai trò Natural Hedge bảo vệ NAV |

---

## 5. Phiên Tranh Biện Đối Kháng Đa Tác Tử (`Adversarial Bull vs Bear Debate — CIO Anti-Paralysis Protocol`)
| Mã | Luận Điểm Bảo Vệ Của `Bull Agent` | Phản Biện Đào Bới Rủi Ro Của `Bear Agent` | Phán Quyết Hòa Giải Của `Master CIO` | Điểm Đồng Thuận |
| :--- | :--- | :--- | :--- | :---: |
| **`JPM`** | FCF chuẩn hóa đạt +$0.0B USD, tăng trưởng doanh thu +10.2% YoY, giá ($352.11) giữ cấu trúc trên MA200 ($323.23), điểm IC 96/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`V`** | FCF chuẩn hóa đạt +$21.12B USD, tăng trưởng doanh thu +13.2% YoY, giá ($436.57) giữ cấu trúc trên MA200 ($343.15), điểm IC 81/100. | CẢNH BÁO ĐỊNH GIÁ/ĐÀ TĂNG: RSI tiệm cận vùng nóng (69.2) — Cần tránh mua đuổi giá xanh. | **APPROVED_WITH_60_40_SPLIT (Bác bỏ Veto định giá • Duyệt giải ngân chia nhịp 60/40 Limit Pullback)** | **`84.5/100`** |
| **`PG`** | FCF chuẩn hóa đạt +$12.65B USD, tăng trưởng doanh thu +4.0% YoY, giá ($167.32) giữ cấu trúc trên MA200 ($149.11), điểm IC 85/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`COST`** | FCF chuẩn hóa đạt +$6.75B USD, tăng trưởng doanh thu +11.1% YoY, giá ($1046.47) giữ cấu trúc trên MA200 ($971.61), điểm IC 78/100. | CẢNH BÁO ĐỊNH GIÁ/ĐÀ TĂNG: Định giá Fwd P/E cao (41.81x) — Cần tránh mua đuổi giá xanh. | **APPROVED_WITH_60_40_SPLIT (Bác bỏ Veto định giá • Duyệt giải ngân chia nhịp 60/40 Limit Pullback)** | **`84.5/100`** |
| **`MSFT`** | FCF chuẩn hóa đạt +$2.99B USD, tăng trưởng doanh thu +18.8% YoY, giá ($555.8) giữ cấu trúc trên MA200 ($438.48), điểm IC 82/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`ABBV`** | FCF chuẩn hóa đạt +$0.0B USD, tăng trưởng doanh thu +10.3% YoY, giá ($294.83) giữ cấu trúc trên MA200 ($237.81), điểm IC 85/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`XOM`** | FCF chuẩn hóa đạt +$28.9B USD, tăng trưởng doanh thu +32.6% YoY, giá ($169.27) giữ cấu trúc trên MA200 ($155.09), điểm IC 88/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`JNJ`** | FCF chuẩn hóa đạt +$18.5B USD, tăng trưởng doanh thu +5.9% YoY, giá ($276.32) giữ cấu trúc trên MA200 ($247.48), điểm IC 82/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`NVDA`** | FCF chuẩn hóa đạt +$41.81B USD, tăng trưởng doanh thu +105.9% YoY, giá ($200.13) giữ cấu trúc trên MA200 ($204.56), điểm IC 68/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`TSM`** | FCF chuẩn hóa đạt +$36.57B USD, tăng trưởng doanh thu +50.9% YoY, giá ($395.75) giữ cấu trúc trên MA200 ($400.76), điểm IC 70/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
