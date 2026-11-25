# [BAN 4 — QUANT RISK] BÁO CÁO MA TRẬN TƯƠNG QUAN, ĐỊNH CỠ VỊ THẾ & KIỂM THỬ SỨC CHỊU ĐỰNG (STRESS TEST)
**Ngày kiểm toán**: 2026-11-25  
**Công cụ định lượng**: `scripts/quant_portfolio_engine.py` (v5.0 Audited — 0 Imminent Earnings Violations, Chandelier Stop & ATR Risk-Parity)

---

## 1. Tổng Quan Chỉ Số Rủi Ro Danh Mục (Portfolio Risk Telemetry)
- **Tỷ trọng Cổ phiếu / Tiền mặt (T-Bills ~5%)**: **`60.0% Cổ phiếu` / `40.0% Tiền mặt`**
- **Hệ số Beta Danh mục Tổng hợp (Portfolio Weighted Beta vs S&P 500)**: **`0.38`** *(Thấp hơn đáng kể so với biến động thị trường chung 1.00)*
- **Kiểm soát Cụm Bán dẫn (`NVDA + TSM`)**: **`3.4% NAV`** *(Tuân thủ trần `<= 14.0% NAV`)*
- **Tổng rủi ro danh mục nếu toàn bộ 10 vị thế đồng loạt chạm Stop-Loss `2xATR(14)`**: **`-3.17% NAV`**
- **Số mã bị khóa mua mới do sát lịch BCTC (`0 <= days_to_earnings <= 7`)**: **`0 mã`** (``)

---

## 2. Ma Trận Tương Quan Lợi Suất 1 Năm (`Pairwise Return Correlation Matrix`)

| Mã | **`MSFT`** | **`TSM`** | **`JPM`** | **`OXY`** | **`NVDA`** | **`PG`** | **`JNJ`** | **`V`** | **`ABBV`** | **`COST`** |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`MSFT`** | `1.00` | 0.19 | 0.14 | -0.11 | 0.22 | -0.10 | -0.15 | 0.21 | -0.09 | -0.07 |
| **`TSM`** | 0.19 | `1.00` | 0.21 | -0.21 | **0.70** | -0.18 | -0.17 | -0.05 | -0.12 | -0.22 |
| **`JPM`** | 0.14 | 0.21 | `1.00` | -0.12 | 0.18 | 0.10 | 0.16 | 0.36 | 0.08 | -0.01 |
| **`OXY`** | -0.11 | -0.21 | -0.12 | `1.00` | -0.14 | -0.16 | 0.02 | -0.11 | 0.02 | 0.05 |
| **`NVDA`** | 0.22 | **0.70** | 0.18 | -0.14 | `1.00` | -0.21 | -0.17 | -0.03 | -0.10 | -0.24 |
| **`PG`** | -0.10 | -0.18 | 0.10 | -0.16 | -0.21 | `1.00` | 0.44 | 0.24 | 0.26 | 0.36 |
| **`JNJ`** | -0.15 | -0.17 | 0.16 | 0.02 | -0.17 | 0.44 | `1.00` | 0.17 | 0.55 | 0.32 |
| **`V`** | 0.21 | -0.05 | 0.36 | -0.11 | -0.03 | 0.24 | 0.17 | `1.00` | 0.23 | 0.25 |
| **`ABBV`** | -0.09 | -0.12 | 0.08 | 0.02 | -0.10 | 0.26 | 0.55 | 0.23 | `1.00` | 0.22 |
| **`COST`** | -0.07 | -0.22 | -0.01 | 0.05 | -0.24 | 0.36 | 0.32 | 0.25 | 0.22 | `1.00` |

---

## 3. Bảng Định Cỡ Vị Thế (`ATR Risk-Parity`), Chandelier Stop & Kiểm Toán Lịch BCTC

| Mã | Ngành | Giá ($) | Stop `2xATR` ($) | Chandelier Trailing ($) | Khoảng cách Stop (%) | Tỷ trọng (% NAV) | Rủi ro tối đa (% NAV) | Điểm IC (/100) | Lịch BCTC (`Earnings Radar`) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`COST`** | Membership Warehouse Retail | $1092.39 | **$1055.23** | $1077.22 | -3.4% | **9.7% NAV** | `-0.33% NAV` | **79/100** | UPCOMING EARNINGS (15d, AMC) — Lưu ý biến động |
| **`PG`** | Consumer Household Staples | $173.95 | **$167.64** | $166.67 | -3.62% | **8.6% NAV** | `-0.31% NAV` | **77/100** | CLEAR (2027-01-22 BMO) |
| **`V`** | Global Payment Network | $424.69 | **$406.51** | $419.5 | -4.28% | **7.9% NAV** | `-0.34% NAV` | **80/100** | CLEAR (2027-01-26 AMC) |
| **`ABBV`** | Biotech & Immunology | $296.89 | **$283.71** | $286.49 | -4.44% | **7.9% NAV** | `-0.35% NAV` | **86/100** | CLEAR (2027-02-03 BMO) |
| **`JNJ`** | Pharmaceuticals & MedTech | $276.51 | **$263.54** | $274.04 | -4.7% | **6.6% NAV** | `-0.31% NAV` | **77/100** | CLEAR (2027-01-26 BMO) |
| **`JPM`** | Global Diversified Banking | $317.07 | **$301.71** | $340.6 | -4.84% | **6.0% NAV** | `-0.29% NAV` | **70/100** | CLEAR (2027-01-14 BMO) |
| **`MSFT`** | Enterprise Software & Cloud | $489.84 | **$455.73** | $516.52 | -6.96% | **5.0% NAV** | `-0.35% NAV` | **83/100** | CLEAR (2027-01-27 AMC) |
| **`OXY`** | Upstream Oil & Carbon Capture | $54.42 | **$51.19** | $60.1 | -5.96% | **4.9% NAV** | `-0.29% NAV` | **67/100** | CLEAR (2027-02-17 AMC) |
| **`TSM`** | Global Chip Foundry | $337.57 | **$287.34** | $378.09 | -14.88% | **2.0% NAV** | `-0.3% NAV` | **70/100** | CLEAR (2027-01-14 BMO) |
| **`NVDA`** | Semiconductors & AI | $146.97 | **$115.31** | $180.41 | -21.54% | **1.4% NAV** | `-0.3% NAV` | **68/100** | CLEAR (2026-11-17 AMC) |

### Danh Sách Theo Dõi Tạm Khóa Do Sát Ngày Công Bố BCTC (`Locked Imminent Earnings Watchlist <= 7 Ngày`)
| Mã | Ngành | Giá ($) | Ngày BCTC | Phiên | Số Ngày Còn Lại | Implied Move (±%) | Điểm IC | Lý Do Khóa & Kế Hoạch Hành Động Sau BCTC |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |

---

## 4. Kiểm Thử Sức Chịu Đựng Danh Mục Trước 3 Cú Sốc Vĩ Mô (`Institutional Stress-Testing`)

| Kịch bản Cú sốc Vĩ mô / Địa chính trị | Giả định S&P 500 | Tác động Dự kiến lên Danh mục | Mức Vượt trội (Alpha Bảo vệ) | Cơ chế Phòng vệ Tự động của Danh mục |
| :--- | :---: | :---: | :---: | :--- |
| **Kịch bản 1: Cú sốc Bán tháo Thị trường (S&P 500 sập -10.0%)**<br>*(Kích hoạt: Khủng hoảng thanh khoản hoặc dữ liệu kinh tế xấu đột biến)* | `-10.0%` | **`-3.65% NAV`** | **`+6.35%`** | Beta danh mục thấp (0.38) + Đệm 40.0% Tiền mặt/T-Bills + Kích hoạt Stop-Loss 2xATR & Chandelier Stop tự động |
| **Kịch bản 2: Cú sốc Lãi suất Fed Diều hâu (US 10Y Yield vọt lên 5.45%)**<br>*(Kích hoạt: PCE/CPI vượt 4.0% buộc Fed tăng lãi suất thêm +25–50 bps)* | `-6.5%` | **`-1.52% NAV`** | **`+4.98%`** | Nhóm Ngân hàng/Tài chính (JPM, V) và 40.0% T-Bills hưởng lợi trực tiếp bù đắp cho nhóm Công nghệ |
| **Kịch bản 3: Cú sốc Giá Dầu Địa chính trị (WTI Crude vọt lên $125/thùng)**<br>*(Kích hoạt: Gián đoạn nghiêm trọng eo biển Hormuz hoặc cơ sở lọc dầu toàn cầu)* | `-5.5%` | **`-0.49% NAV`** | **`+5.01%`** | Vị thế Dầu khí (OXY) và Phòng thủ Thiết yếu/Y tế (PG, JNJ, ABBV, COST) đóng vai trò Natural Hedge bảo vệ NAV |

---

## 5. Phiên Tranh Biện Đối Kháng Đa Tác Tử (`Adversarial Bull vs Bear Debate — CIO Anti-Paralysis Protocol`)
| Mã | Luận Điểm Bảo Vệ Của `Bull Agent` | Phản Biện Đào Bới Rủi Ro Của `Bear Agent` | Phán Quyết Hòa Giải Của `Master CIO` | Điểm Đồng Thuận |
| :--- | :--- | :--- | :--- | :---: |
| **`COST`** | FCF chuẩn hóa đạt +$6.75B USD, tăng trưởng doanh thu +11.1% YoY, giá ($1092.39) giữ cấu trúc trên MA200 ($980.56), điểm IC 79/100. | CẢNH BÁO ĐỊNH GIÁ/ĐÀ TĂNG: Định giá Fwd P/E cao (43.63x) — Cần tránh mua đuổi giá xanh. | **APPROVED_WITH_60_40_SPLIT (Bác bỏ Veto định giá • Duyệt giải ngân chia nhịp 60/40 Limit Pullback)** | **`84.5/100`** |
| **`PG`** | FCF chuẩn hóa đạt +$12.65B USD, tăng trưởng doanh thu +4.0% YoY, giá ($173.95) giữ cấu trúc trên MA200 ($150.46), điểm IC 77/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`V`** | FCF chuẩn hóa đạt +$20.98B USD, tăng trưởng doanh thu +13.2% YoY, giá ($424.69) giữ cấu trúc trên MA200 ($350.49), điểm IC 80/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`ABBV`** | FCF chuẩn hóa đạt +$17.69B USD, tăng trưởng doanh thu +10.3% YoY, giá ($296.89) giữ cấu trúc trên MA200 ($243.53), điểm IC 86/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`JNJ`** | FCF chuẩn hóa đạt +$18.5B USD, tăng trưởng doanh thu +5.9% YoY, giá ($276.51) giữ cấu trúc trên MA200 ($251.36), điểm IC 77/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`JPM`** | FCF chuẩn hóa đạt +$0.0B USD, tăng trưởng doanh thu +10.2% YoY, giá ($317.07) giữ cấu trúc trên MA200 ($325.14), điểm IC 70/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`MSFT`** | FCF chuẩn hóa đạt +$2.99B USD, tăng trưởng doanh thu +18.8% YoY, giá ($489.84) giữ cấu trúc trên MA200 ($444.88), điểm IC 83/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`OXY`** | FCF chuẩn hóa đạt +$4.91B USD, tăng trưởng doanh thu +19.0% YoY, giá ($54.42) giữ cấu trúc trên MA200 ($57.12), điểm IC 67/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`TSM`** | FCF chuẩn hóa đạt +$31.38B USD, tăng trưởng doanh thu +50.9% YoY, giá ($337.57) giữ cấu trúc trên MA200 ($403.49), điểm IC 70/100. | VI PHẠM CẤU TRÚC: Gãy cấu trúc MA200 ($337.57 < $403.49) | **ABSOLUTE_VETO (Từ chối giải ngân do vi phạm lằn ranh đỏ cấu trúc)** | **`35.0/100`** |
| **`NVDA`** | FCF chuẩn hóa đạt +$99.24B USD, tăng trưởng doanh thu +103.2% YoY, giá ($146.97) giữ cấu trúc trên MA200 ($202.86), điểm IC 68/100. | VI PHẠM CẤU TRÚC: Gãy cấu trúc MA200 ($146.97 < $202.86) | **ABSOLUTE_VETO (Từ chối giải ngân do vi phạm lằn ranh đỏ cấu trúc)** | **`35.0/100`** |
