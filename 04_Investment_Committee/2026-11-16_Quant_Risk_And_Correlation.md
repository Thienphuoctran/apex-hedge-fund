# [BAN 4 — QUANT RISK] BÁO CÁO MA TRẬN TƯƠNG QUAN, ĐỊNH CỠ VỊ THẾ & KIỂM THỬ SỨC CHỊU ĐỰNG (STRESS TEST)
**Ngày kiểm toán**: 2026-11-16  
**Công cụ định lượng**: `scripts/quant_portfolio_engine.py` (v5.0 Audited — 0 Imminent Earnings Violations, Chandelier Stop & ATR Risk-Parity)

---

## 1. Tổng Quan Chỉ Số Rủi Ro Danh Mục (Portfolio Risk Telemetry)
- **Tỷ trọng Cổ phiếu / Tiền mặt (T-Bills ~5%)**: **`60.0% Cổ phiếu` / `40.0% Tiền mặt`**
- **Hệ số Beta Danh mục Tổng hợp (Portfolio Weighted Beta vs S&P 500)**: **`0.34`** *(Thấp hơn đáng kể so với biến động thị trường chung 1.00)*
- **Kiểm soát Cụm Bán dẫn (`NVDA + TSM`)**: **`2.6% NAV`** *(Tuân thủ trần `<= 14.0% NAV`)*
- **Tổng rủi ro danh mục nếu toàn bộ 10 vị thế đồng loạt chạm Stop-Loss `2xATR(14)`**: **`-3.18% NAV`**
- **Số mã bị khóa mua mới do sát lịch BCTC (`0 <= days_to_earnings <= 7`)**: **`2 mã`** (`NVDA, WMT`)

---

## 2. Ma Trận Tương Quan Lợi Suất 1 Năm (`Pairwise Return Correlation Matrix`)

| Mã | **`MSFT`** | **`TSM`** | **`JPM`** | **`OXY`** | **`PG`** | **`JNJ`** | **`V`** | **`ABBV`** | **`COST`** | **`XOM`** |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`MSFT`** | `1.00` | 0.16 | 0.12 | -0.11 | -0.11 | -0.17 | 0.20 | -0.10 | -0.06 | -0.16 |
| **`TSM`** | 0.16 | `1.00` | 0.16 | -0.21 | -0.20 | -0.18 | -0.08 | -0.14 | -0.23 | -0.21 |
| **`JPM`** | 0.12 | 0.16 | `1.00` | -0.14 | 0.10 | 0.15 | 0.35 | 0.07 | -0.01 | -0.10 |
| **`OXY`** | -0.11 | -0.21 | -0.14 | `1.00` | -0.17 | -0.01 | -0.12 | 0.00 | 0.04 | **0.76** |
| **`PG`** | -0.11 | -0.20 | 0.10 | -0.17 | `1.00` | 0.42 | 0.22 | 0.26 | 0.37 | -0.08 |
| **`JNJ`** | -0.17 | -0.18 | 0.15 | -0.01 | 0.42 | `1.00` | 0.15 | 0.53 | 0.32 | 0.07 |
| **`V`** | 0.20 | -0.08 | 0.35 | -0.12 | 0.22 | 0.15 | `1.00` | 0.22 | 0.26 | -0.08 |
| **`ABBV`** | -0.10 | -0.14 | 0.07 | 0.00 | 0.26 | 0.53 | 0.22 | `1.00` | 0.23 | 0.04 |
| **`COST`** | -0.06 | -0.23 | -0.01 | 0.04 | 0.37 | 0.32 | 0.26 | 0.23 | `1.00` | 0.11 |
| **`XOM`** | -0.16 | -0.21 | -0.10 | **0.76** | -0.08 | 0.07 | -0.08 | 0.04 | 0.11 | `1.00` |

---

## 3. Bảng Định Cỡ Vị Thế (`ATR Risk-Parity`), Chandelier Stop & Kiểm Toán Lịch BCTC

| Mã | Ngành | Giá ($) | Stop `2xATR` ($) | Chandelier Trailing ($) | Khoảng cách Stop (%) | Tỷ trọng (% NAV) | Rủi ro tối đa (% NAV) | Điểm IC (/100) | Lịch BCTC (`Earnings Radar`) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`PG`** | Consumer Household Staples | $173.04 | **$166.15** | $164.95 | -3.98% | **7.8% NAV** | `-0.31% NAV` | **78/100** | CLEAR (2027-01-21 BMO) |
| **`COST`** | Membership Warehouse Retail | $1110.16 | **$1067.59** | $1063.78 | -3.84% | **7.3% NAV** | `-0.28% NAV` | **63/100** | CLEAR (2026-12-10 AMC) |
| **`JPM`** | Global Diversified Banking | $338.38 | **$322.11** | $339.47 | -4.8% | **6.8% NAV** | `-0.33% NAV` | **87/100** | CLEAR (2027-01-14 BMO) |
| **`V`** | Global Payment Network | $427.64 | **$407.12** | $416.58 | -4.8% | **6.6% NAV** | `-0.32% NAV` | **79/100** | CLEAR (2027-01-26 AMC) |
| **`ABBV`** | Biotech & Immunology | $295.93 | **$280.8** | $284.02 | -5.12% | **6.2% NAV** | `-0.32% NAV` | **82/100** | CLEAR (2026-10-30 BMO) |
| **`XOM`** | Integrated Oil & Gas | $167.38 | **$158.06** | $176.85 | -5.56% | **6.2% NAV** | `-0.34% NAV` | **85/100** | CLEAR (2027-01-29 BMO) |
| **`JNJ`** | Pharmaceuticals & MedTech | $284.68 | **$270.16** | $272.1 | -5.1% | **6.1% NAV** | `-0.31% NAV` | **75/100** | CLEAR (2027-01-26 BMO) |
| **`MSFT`** | Enterprise Software & Cloud | $520.81 | **$485.04** | $514.43 | -6.86% | **5.2% NAV** | `-0.36% NAV` | **85/100** | CLEAR (2027-01-27 AMC) |
| **`OXY`** | Upstream Oil & Carbon Capture | $57.86 | **$54.2** | $60.39 | -6.32% | **5.2% NAV** | `-0.33% NAV` | **84/100** | CLEAR (2026-11-09 AMC) |
| **`TSM`** | Global Chip Foundry | $375.41 | **$335.59** | $391.1 | -10.6% | **2.6% NAV** | `-0.28% NAV` | **70/100** | CLEAR (2027-01-14 BMO) |

### Danh Sách Theo Dõi Tạm Khóa Do Sát Ngày Công Bố BCTC (`Locked Imminent Earnings Watchlist <= 7 Ngày`)
| Mã | Ngành | Giá ($) | Ngày BCTC | Phiên | Số Ngày Còn Lại | Implied Move (±%) | Điểm IC | Lý Do Khóa & Kế Hoạch Hành Động Sau BCTC |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`NVDA`** | Semiconductors & AI | $155.19 | `2026-11-17` | AMC | **1d** | `±14.5%` | 67/100 | Chờ BCTC công bố ngày 2026-11-17; chỉ giải ngân nếu giữ vững MA50 ($213.14) và hướng dẫn EPS tích cực. |
| **`WMT`** | Discount Retail & Grocery | $128.33 | `2026-11-19` | BMO | **3d** | `±5.59%` | 55/100 | Quan sát phản ứng giá sau BCTC ngày 2026-11-19 trước khi mở vị thế. |

---

## 4. Kiểm Thử Sức Chịu Đựng Danh Mục Trước 3 Cú Sốc Vĩ Mô (`Institutional Stress-Testing`)

| Kịch bản Cú sốc Vĩ mô / Địa chính trị | Giả định S&P 500 | Tác động Dự kiến lên Danh mục | Mức Vượt trội (Alpha Bảo vệ) | Cơ chế Phòng vệ Tự động của Danh mục |
| :--- | :---: | :---: | :---: | :--- |
| **Kịch bản 1: Cú sốc Bán tháo Thị trường (S&P 500 sập -10.0%)**<br>*(Kích hoạt: Khủng hoảng thanh khoản hoặc dữ liệu kinh tế xấu đột biến)* | `-10.0%` | **`-3.22% NAV`** | **`+6.78%`** | Beta danh mục thấp (0.34) + Đệm 40.0% Tiền mặt/T-Bills + Kích hoạt Stop-Loss 2xATR & Chandelier Stop tự động |
| **Kịch bản 2: Cú sốc Lãi suất Fed Diều hâu (US 10Y Yield vọt lên 5.45%)**<br>*(Kích hoạt: PCE/CPI vượt 4.0% buộc Fed tăng lãi suất thêm +25–50 bps)* | `-6.5%` | **`-1.26% NAV`** | **`+5.24%`** | Nhóm Ngân hàng/Tài chính (JPM, V) và 40.0% T-Bills hưởng lợi trực tiếp bù đắp cho nhóm Công nghệ |
| **Kịch bản 3: Cú sốc Giá Dầu Địa chính trị (WTI Crude vọt lên $125/thùng)**<br>*(Kích hoạt: Gián đoạn nghiêm trọng eo biển Hormuz hoặc cơ sở lọc dầu toàn cầu)* | `-5.5%` | **`0.53% NAV`** | **`+6.03%`** | Vị thế Dầu khí (OXY) và Phòng thủ Thiết yếu/Y tế (PG, JNJ, ABBV, COST) đóng vai trò Natural Hedge bảo vệ NAV |

---

## 5. Phiên Tranh Biện Đối Kháng Đa Tác Tử (`Adversarial Bull vs Bear Debate — CIO Anti-Paralysis Protocol`)
| Mã | Luận Điểm Bảo Vệ Của `Bull Agent` | Phản Biện Đào Bới Rủi Ro Của `Bear Agent` | Phán Quyết Hòa Giải Của `Master CIO` | Điểm Đồng Thuận |
| :--- | :--- | :--- | :--- | :---: |
| **`PG`** | FCF chuẩn hóa đạt +$12.65B USD, tăng trưởng doanh thu +4.0% YoY, giá ($173.04) giữ cấu trúc trên MA200 ($149.98), điểm IC 78/100. | CẢNH BÁO ĐỊNH GIÁ/ĐÀ TĂNG: RSI tiệm cận vùng nóng (72.19) — Cần tránh mua đuổi giá xanh. | **APPROVED_WITH_60_40_SPLIT (Bác bỏ Veto định giá • Duyệt giải ngân chia nhịp 60/40 Limit Pullback)** | **`84.5/100`** |
| **`COST`** | FCF chuẩn hóa đạt +$6.75B USD, tăng trưởng doanh thu +11.1% YoY, giá ($1110.16) giữ cấu trúc trên MA200 ($976.53), điểm IC 63/100. | CẢNH BÁO ĐỊNH GIÁ/ĐÀ TĂNG: Định giá Fwd P/E cao (44.37x); RSI tiệm cận vùng nóng (76.61) — Cần tránh mua đuổi giá xanh. | **APPROVED_WITH_60_40_SPLIT (Bác bỏ Veto định giá • Duyệt giải ngân chia nhịp 60/40 Limit Pullback)** | **`84.5/100`** |
| **`JPM`** | FCF chuẩn hóa đạt +$0.0B USD, tăng trưởng doanh thu +10.2% YoY, giá ($338.38) giữ cấu trúc trên MA200 ($325.02), điểm IC 87/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`V`** | FCF chuẩn hóa đạt +$20.98B USD, tăng trưởng doanh thu +13.2% YoY, giá ($427.64) giữ cấu trúc trên MA200 ($347.59), điểm IC 79/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`ABBV`** | FCF chuẩn hóa đạt +$17.69B USD, tăng trưởng doanh thu +10.3% YoY, giá ($295.93) giữ cấu trúc trên MA200 ($241.15), điểm IC 82/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`XOM`** | FCF chuẩn hóa đạt +$28.32B USD, tăng trưởng doanh thu +32.6% YoY, giá ($167.38) giữ cấu trúc trên MA200 ($156.49), điểm IC 85/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`JNJ`** | FCF chuẩn hóa đạt +$18.5B USD, tăng trưởng doanh thu +5.9% YoY, giá ($284.68) giữ cấu trúc trên MA200 ($250.07), điểm IC 75/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`MSFT`** | FCF chuẩn hóa đạt +$2.99B USD, tăng trưởng doanh thu +18.8% YoY, giá ($520.81) giữ cấu trúc trên MA200 ($441.87), điểm IC 85/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`OXY`** | FCF chuẩn hóa đạt +$4.91B USD, tăng trưởng doanh thu +19.0% YoY, giá ($57.86) giữ cấu trúc trên MA200 ($56.83), điểm IC 84/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`TSM`** | FCF chuẩn hóa đạt +$36.57B USD, tăng trưởng doanh thu +50.9% YoY, giá ($375.41) giữ cấu trúc trên MA200 ($403.28), điểm IC 70/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
