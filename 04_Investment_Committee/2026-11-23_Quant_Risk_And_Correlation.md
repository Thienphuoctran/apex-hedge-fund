# [BAN 4 — QUANT RISK] BÁO CÁO MA TRẬN TƯƠNG QUAN, ĐỊNH CỠ VỊ THẾ & KIỂM THỬ SỨC CHỊU ĐỰNG (STRESS TEST)
**Ngày kiểm toán**: 2026-11-23  
**Công cụ định lượng**: `scripts/quant_portfolio_engine.py` (v5.0 Audited — 0 Imminent Earnings Violations, Chandelier Stop & ATR Risk-Parity)

---

## 1. Tổng Quan Chỉ Số Rủi Ro Danh Mục (Portfolio Risk Telemetry)
- **Tỷ trọng Cổ phiếu / Tiền mặt (T-Bills ~5%)**: **`60.0% Cổ phiếu` / `40.0% Tiền mặt`**
- **Hệ số Beta Danh mục Tổng hợp (Portfolio Weighted Beta vs S&P 500)**: **`0.38`** *(Thấp hơn đáng kể so với biến động thị trường chung 1.00)*
- **Kiểm soát Cụm Bán dẫn (`NVDA + TSM`)**: **`4.0% NAV`** *(Tuân thủ trần `<= 14.0% NAV`)*
- **Tổng rủi ro danh mục nếu toàn bộ 10 vị thế đồng loạt chạm Stop-Loss `2xATR(14)`**: **`-3.55% NAV`**
- **Số mã bị khóa mua mới do sát lịch BCTC (`0 <= days_to_earnings <= 7`)**: **`0 mã`** (``)

---

## 2. Ma Trận Tương Quan Lợi Suất 1 Năm (`Pairwise Return Correlation Matrix`)

| Mã | **`MSFT`** | **`TSM`** | **`JPM`** | **`OXY`** | **`NVDA`** | **`PG`** | **`JNJ`** | **`V`** | **`ABBV`** | **`COST`** |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`MSFT`** | `1.00` | 0.18 | 0.14 | -0.11 | 0.24 | -0.10 | -0.16 | 0.22 | -0.10 | -0.07 |
| **`TSM`** | 0.18 | `1.00` | 0.19 | -0.19 | **0.68** | -0.19 | -0.16 | -0.06 | -0.13 | -0.23 |
| **`JPM`** | 0.14 | 0.19 | `1.00` | -0.12 | 0.17 | 0.11 | 0.16 | 0.36 | 0.08 | -0.00 |
| **`OXY`** | -0.11 | -0.19 | -0.12 | `1.00` | -0.11 | -0.16 | 0.01 | -0.11 | 0.02 | 0.05 |
| **`NVDA`** | 0.24 | **0.68** | 0.17 | -0.11 | `1.00` | -0.26 | -0.19 | -0.08 | -0.15 | -0.30 |
| **`PG`** | -0.10 | -0.19 | 0.11 | -0.16 | -0.26 | `1.00` | 0.43 | 0.23 | 0.26 | 0.38 |
| **`JNJ`** | -0.16 | -0.16 | 0.16 | 0.01 | -0.19 | 0.43 | `1.00` | 0.17 | 0.54 | 0.32 |
| **`V`** | 0.22 | -0.06 | 0.36 | -0.11 | -0.08 | 0.23 | 0.17 | `1.00` | 0.23 | 0.25 |
| **`ABBV`** | -0.10 | -0.13 | 0.08 | 0.02 | -0.15 | 0.26 | 0.54 | 0.23 | `1.00` | 0.24 |
| **`COST`** | -0.07 | -0.23 | -0.00 | 0.05 | -0.30 | 0.38 | 0.32 | 0.25 | 0.24 | `1.00` |

---

## 3. Bảng Định Cỡ Vị Thế (`ATR Risk-Parity`), Chandelier Stop & Kiểm Toán Lịch BCTC

| Mã | Ngành | Giá ($) | Stop `2xATR` ($) | Chandelier Trailing ($) | Khoảng cách Stop (%) | Tỷ trọng (% NAV) | Rủi ro tối đa (% NAV) | Điểm IC (/100) | Lịch BCTC (`Earnings Radar`) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`COST`** | Membership Warehouse Retail | $1102.15 | **$1060.4** | $1071.48 | -3.78% | **9.3% NAV** | `-0.35% NAV` | **74/100** | UPCOMING EARNINGS (17d, AMC) — Lưu ý biến động |
| **`PG`** | Consumer Household Staples | $169.37 | **$162.56** | $165.08 | -4.02% | **9.1% NAV** | `-0.37% NAV` | **77/100** | CLEAR (2027-01-21 BMO) |
| **`V`** | Global Payment Network | $401.87 | **$381.8** | $417.14 | -5.0% | **7.7% NAV** | `-0.39% NAV` | **83/100** | CLEAR (2027-01-26 AMC) |
| **`ABBV`** | Biotech & Immunology | $286.2 | **$271.87** | $285.01 | -5.0% | **7.7% NAV** | `-0.39% NAV` | **83/100** | CLEAR (2026-10-30 BMO) |
| **`JNJ`** | Pharmaceuticals & MedTech | $270.47 | **$256.5** | $272.79 | -5.16% | **6.6% NAV** | `-0.34% NAV` | **74/100** | CLEAR (2027-01-26 BMO) |
| **`JPM`** | Global Diversified Banking | $310.53 | **$292.53** | $337.3 | -5.8% | **5.7% NAV** | `-0.33% NAV` | **73/100** | CLEAR (2027-01-14 BMO) |
| **`MSFT`** | Enterprise Software & Cloud | $484.52 | **$447.18** | $512.47 | -7.7% | **5.1% NAV** | `-0.39% NAV` | **83/100** | CLEAR (2027-01-27 AMC) |
| **`OXY`** | Upstream Oil & Carbon Capture | $53.9 | **$50.2** | $60.33 | -6.86% | **4.8% NAV** | `-0.33% NAV` | **67/100** | CLEAR (2026-11-09 AMC) |
| **`TSM`** | Global Chip Foundry | $318.71 | **$275.17** | $386.46 | -13.66% | **2.4% NAV** | `-0.33% NAV` | **72/100** | CLEAR (2027-01-14 BMO) |
| **`NVDA`** | Semiconductors & AI | $125.53 | **$99.85** | $187.89 | -20.46% | **1.6% NAV** | `-0.33% NAV` | **67/100** | CLEAR (2026-11-17 AMC) |

### Danh Sách Theo Dõi Tạm Khóa Do Sát Ngày Công Bố BCTC (`Locked Imminent Earnings Watchlist <= 7 Ngày`)
| Mã | Ngành | Giá ($) | Ngày BCTC | Phiên | Số Ngày Còn Lại | Implied Move (±%) | Điểm IC | Lý Do Khóa & Kế Hoạch Hành Động Sau BCTC |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |

---

## 4. Kiểm Thử Sức Chịu Đựng Danh Mục Trước 3 Cú Sốc Vĩ Mô (`Institutional Stress-Testing`)

| Kịch bản Cú sốc Vĩ mô / Địa chính trị | Giả định S&P 500 | Tác động Dự kiến lên Danh mục | Mức Vượt trội (Alpha Bảo vệ) | Cơ chế Phòng vệ Tự động của Danh mục |
| :--- | :---: | :---: | :---: | :--- |
| **Kịch bản 1: Cú sốc Bán tháo Thị trường (S&P 500 sập -10.0%)**<br>*(Kích hoạt: Khủng hoảng thanh khoản hoặc dữ liệu kinh tế xấu đột biến)* | `-10.0%` | **`-3.68% NAV`** | **`+6.32%`** | Beta danh mục thấp (0.38) + Đệm 40.0% Tiền mặt/T-Bills + Kích hoạt Stop-Loss 2xATR & Chandelier Stop tự động |
| **Kịch bản 2: Cú sốc Lãi suất Fed Diều hâu (US 10Y Yield vọt lên 5.45%)**<br>*(Kích hoạt: PCE/CPI vượt 4.0% buộc Fed tăng lãi suất thêm +25–50 bps)* | `-6.5%` | **`-1.57% NAV`** | **`+4.93%`** | Nhóm Ngân hàng/Tài chính (JPM, V) và 40.0% T-Bills hưởng lợi trực tiếp bù đắp cho nhóm Công nghệ |
| **Kịch bản 3: Cú sốc Giá Dầu Địa chính trị (WTI Crude vọt lên $125/thùng)**<br>*(Kích hoạt: Gián đoạn nghiêm trọng eo biển Hormuz hoặc cơ sở lọc dầu toàn cầu)* | `-5.5%` | **`-0.51% NAV`** | **`+4.99%`** | Vị thế Dầu khí (OXY) và Phòng thủ Thiết yếu/Y tế (PG, JNJ, ABBV, COST) đóng vai trò Natural Hedge bảo vệ NAV |

---

## 5. Phiên Tranh Biện Đối Kháng Đa Tác Tử (`Adversarial Bull vs Bear Debate — CIO Anti-Paralysis Protocol`)
| Mã | Luận Điểm Bảo Vệ Của `Bull Agent` | Phản Biện Đào Bới Rủi Ro Của `Bear Agent` | Phán Quyết Hòa Giải Của `Master CIO` | Điểm Đồng Thuận |
| :--- | :--- | :--- | :--- | :---: |
| **`COST`** | FCF chuẩn hóa đạt +$6.75B USD, tăng trưởng doanh thu +11.1% YoY, giá ($1102.15) giữ cấu trúc trên MA200 ($979.0), điểm IC 74/100. | CẢNH BÁO ĐỊNH GIÁ/ĐÀ TĂNG: Định giá Fwd P/E cao (44.01x); RSI tiệm cận vùng nóng (69.6) — Cần tránh mua đuổi giá xanh. | **APPROVED_WITH_60_40_SPLIT (Bác bỏ Veto định giá • Duyệt giải ngân chia nhịp 60/40 Limit Pullback)** | **`84.5/100`** |
| **`PG`** | FCF chuẩn hóa đạt +$12.65B USD, tăng trưởng doanh thu +4.0% YoY, giá ($169.37) giữ cấu trúc trên MA200 ($150.26), điểm IC 77/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`V`** | FCF chuẩn hóa đạt +$20.98B USD, tăng trưởng doanh thu +13.2% YoY, giá ($401.87) giữ cấu trúc trên MA200 ($349.16), điểm IC 83/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`ABBV`** | FCF chuẩn hóa đạt +$17.69B USD, tăng trưởng doanh thu +10.3% YoY, giá ($286.2) giữ cấu trúc trên MA200 ($242.45), điểm IC 83/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`JNJ`** | FCF chuẩn hóa đạt +$18.5B USD, tăng trưởng doanh thu +5.9% YoY, giá ($270.47) giữ cấu trúc trên MA200 ($250.83), điểm IC 74/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`JPM`** | FCF chuẩn hóa đạt +$0.0B USD, tăng trưởng doanh thu +10.2% YoY, giá ($310.53) giữ cấu trúc trên MA200 ($325.19), điểm IC 73/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`MSFT`** | FCF chuẩn hóa đạt +$2.99B USD, tăng trưởng doanh thu +18.8% YoY, giá ($484.52) giữ cấu trúc trên MA200 ($443.63), điểm IC 83/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`OXY`** | FCF chuẩn hóa đạt +$4.91B USD, tăng trưởng doanh thu +19.0% YoY, giá ($53.9) giữ cấu trúc trên MA200 ($57.02), điểm IC 67/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`TSM`** | FCF chuẩn hóa đạt +$31.69B USD, tăng trưởng doanh thu +50.9% YoY, giá ($318.71) giữ cấu trúc trên MA200 ($403.56), điểm IC 72/100. | VI PHẠM CẤU TRÚC: Gãy cấu trúc MA200 ($318.71 < $403.56) | **ABSOLUTE_VETO (Từ chối giải ngân do vi phạm lằn ranh đỏ cấu trúc)** | **`35.0/100`** |
| **`NVDA`** | FCF chuẩn hóa đạt +$99.24B USD, tăng trưởng doanh thu +103.2% YoY, giá ($125.53) giữ cấu trúc trên MA200 ($203.35), điểm IC 67/100. | VI PHẠM CẤU TRÚC: Gãy cấu trúc MA200 ($125.53 < $203.35) | **ABSOLUTE_VETO (Từ chối giải ngân do vi phạm lằn ranh đỏ cấu trúc)** | **`35.0/100`** |
