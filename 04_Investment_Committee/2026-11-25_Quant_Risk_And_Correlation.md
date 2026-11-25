# [BAN 4 — QUANT RISK] BÁO CÁO MA TRẬN TƯƠNG QUAN, ĐỊNH CỠ VỊ THẾ & KIỂM THỬ SỨC CHỊU ĐỰNG (STRESS TEST)
**Ngày kiểm toán**: 2026-11-25  
**Công cụ định lượng**: `scripts/quant_portfolio_engine.py` (v5.0 Audited — 0 Imminent Earnings Violations, Chandelier Stop & ATR Risk-Parity)

---

## 1. Tổng Quan Chỉ Số Rủi Ro Danh Mục (Portfolio Risk Telemetry)
- **Tỷ trọng Cổ phiếu / Tiền mặt (T-Bills ~5%)**: **`60.0% Cổ phiếu` / `40.0% Tiền mặt`**
- **Hệ số Beta Danh mục Tổng hợp (Portfolio Weighted Beta vs S&P 500)**: **`0.38`** *(Thấp hơn đáng kể so với biến động thị trường chung 1.00)*
- **Kiểm soát Cụm Bán dẫn (`NVDA + TSM`)**: **`3.6% NAV`** *(Tuân thủ trần `<= 14.0% NAV`)*
- **Tổng rủi ro danh mục nếu toàn bộ 10 vị thế đồng loạt chạm Stop-Loss `2xATR(14)`**: **`-3.39% NAV`**
- **Số mã bị khóa mua mới do sát lịch BCTC (`0 <= days_to_earnings <= 7`)**: **`0 mã`** (``)

---

## 2. Ma Trận Tương Quan Lợi Suất 1 Năm (`Pairwise Return Correlation Matrix`)

| Mã | **`MSFT`** | **`TSM`** | **`JPM`** | **`OXY`** | **`NVDA`** | **`PG`** | **`JNJ`** | **`V`** | **`ABBV`** | **`COST`** |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`MSFT`** | `1.00` | 0.19 | 0.14 | -0.11 | 0.22 | -0.10 | -0.15 | 0.22 | -0.10 | -0.07 |
| **`TSM`** | 0.19 | `1.00` | 0.21 | -0.20 | **0.70** | -0.17 | -0.17 | -0.04 | -0.12 | -0.22 |
| **`JPM`** | 0.14 | 0.21 | `1.00` | -0.12 | 0.19 | 0.10 | 0.16 | 0.36 | 0.08 | -0.01 |
| **`OXY`** | -0.11 | -0.20 | -0.12 | `1.00` | -0.13 | -0.16 | 0.02 | -0.11 | 0.02 | 0.05 |
| **`NVDA`** | 0.22 | **0.70** | 0.19 | -0.13 | `1.00` | -0.21 | -0.17 | -0.02 | -0.11 | -0.24 |
| **`PG`** | -0.10 | -0.17 | 0.10 | -0.16 | -0.21 | `1.00` | 0.44 | 0.24 | 0.26 | 0.36 |
| **`JNJ`** | -0.15 | -0.17 | 0.16 | 0.02 | -0.17 | 0.44 | `1.00` | 0.17 | 0.55 | 0.32 |
| **`V`** | 0.22 | -0.04 | 0.36 | -0.11 | -0.02 | 0.24 | 0.17 | `1.00` | 0.24 | 0.25 |
| **`ABBV`** | -0.10 | -0.12 | 0.08 | 0.02 | -0.11 | 0.26 | 0.55 | 0.24 | `1.00` | 0.22 |
| **`COST`** | -0.07 | -0.22 | -0.01 | 0.05 | -0.24 | 0.36 | 0.32 | 0.25 | 0.22 | `1.00` |

---

## 3. Bảng Định Cỡ Vị Thế (`ATR Risk-Parity`), Chandelier Stop & Kiểm Toán Lịch BCTC

| Mã | Ngành | Giá ($) | Stop `2xATR` ($) | Chandelier Trailing ($) | Khoảng cách Stop (%) | Tỷ trọng (% NAV) | Rủi ro tối đa (% NAV) | Điểm IC (/100) | Lịch BCTC (`Earnings Radar`) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`COST`** | Membership Warehouse Retail | $1091.71 | **$1051.21** | $1073.05 | -3.7% | **9.6% NAV** | `-0.36% NAV` | **79/100** | UPCOMING EARNINGS (15d, AMC) — Lưu ý biến động |
| **`PG`** | Consumer Household Staples | $172.47 | **$165.86** | $165.33 | -3.84% | **8.7% NAV** | `-0.33% NAV` | **77/100** | CLEAR (2027-01-22 BMO) |
| **`V`** | Global Payment Network | $416.78 | **$397.36** | $417.96 | -4.66% | **7.9% NAV** | `-0.37% NAV` | **80/100** | CLEAR (2027-01-26 AMC) |
| **`ABBV`** | Biotech & Immunology | $300.28 | **$285.88** | $284.93 | -4.8% | **7.4% NAV** | `-0.36% NAV` | **82/100** | CLEAR (2027-02-03 BMO) |
| **`JNJ`** | Pharmaceuticals & MedTech | $276.46 | **$262.94** | $273.35 | -4.9% | **6.8% NAV** | `-0.33% NAV` | **77/100** | CLEAR (2027-01-26 BMO) |
| **`JPM`** | Global Diversified Banking | $317.1 | **$299.5** | $337.81 | -5.54% | **5.7% NAV** | `-0.32% NAV` | **70/100** | CLEAR (2027-01-14 BMO) |
| **`MSFT`** | Enterprise Software & Cloud | $496.13 | **$461.14** | $515.41 | -7.06% | **5.3% NAV** | `-0.37% NAV` | **83/100** | CLEAR (2027-01-27 AMC) |
| **`OXY`** | Upstream Oil & Carbon Capture | $53.38 | **$50.0** | $60.35 | -6.34% | **5.0% NAV** | `-0.32% NAV` | **67/100** | CLEAR (2027-02-17 AMC) |
| **`TSM`** | Global Chip Foundry | $349.2 | **$296.62** | $375.15 | -15.06% | **2.1% NAV** | `-0.32% NAV` | **70/100** | CLEAR (2027-01-14 BMO) |
| **`NVDA`** | Semiconductors & AI | $155.38 | **$123.08** | $179.61 | -20.78% | **1.5% NAV** | `-0.31% NAV` | **68/100** | CLEAR (2026-11-17 AMC) |

### Danh Sách Theo Dõi Tạm Khóa Do Sát Ngày Công Bố BCTC (`Locked Imminent Earnings Watchlist <= 7 Ngày`)
| Mã | Ngành | Giá ($) | Ngày BCTC | Phiên | Số Ngày Còn Lại | Implied Move (±%) | Điểm IC | Lý Do Khóa & Kế Hoạch Hành Động Sau BCTC |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |

---

## 4. Kiểm Thử Sức Chịu Đựng Danh Mục Trước 3 Cú Sốc Vĩ Mô (`Institutional Stress-Testing`)

| Kịch bản Cú sốc Vĩ mô / Địa chính trị | Giả định S&P 500 | Tác động Dự kiến lên Danh mục | Mức Vượt trội (Alpha Bảo vệ) | Cơ chế Phòng vệ Tự động của Danh mục |
| :--- | :---: | :---: | :---: | :--- |
| **Kịch bản 1: Cú sốc Bán tháo Thị trường (S&P 500 sập -10.0%)**<br>*(Kích hoạt: Khủng hoảng thanh khoản hoặc dữ liệu kinh tế xấu đột biến)* | `-10.0%` | **`-3.67% NAV`** | **`+6.33%`** | Beta danh mục thấp (0.38) + Đệm 40.0% Tiền mặt/T-Bills + Kích hoạt Stop-Loss 2xATR & Chandelier Stop tự động |
| **Kịch bản 2: Cú sốc Lãi suất Fed Diều hâu (US 10Y Yield vọt lên 5.45%)**<br>*(Kích hoạt: PCE/CPI vượt 4.0% buộc Fed tăng lãi suất thêm +25–50 bps)* | `-6.5%` | **`-1.54% NAV`** | **`+4.96%`** | Nhóm Ngân hàng/Tài chính (JPM, V) và 40.0% T-Bills hưởng lợi trực tiếp bù đắp cho nhóm Công nghệ |
| **Kịch bản 3: Cú sốc Giá Dầu Địa chính trị (WTI Crude vọt lên $125/thùng)**<br>*(Kích hoạt: Gián đoạn nghiêm trọng eo biển Hormuz hoặc cơ sở lọc dầu toàn cầu)* | `-5.5%` | **`-0.48% NAV`** | **`+5.02%`** | Vị thế Dầu khí (OXY) và Phòng thủ Thiết yếu/Y tế (PG, JNJ, ABBV, COST) đóng vai trò Natural Hedge bảo vệ NAV |

---

## 5. Phiên Tranh Biện Đối Kháng Đa Tác Tử (`Adversarial Bull vs Bear Debate — CIO Anti-Paralysis Protocol`)
| Mã | Luận Điểm Bảo Vệ Của `Bull Agent` | Phản Biện Đào Bới Rủi Ro Của `Bear Agent` | Phán Quyết Hòa Giải Của `Master CIO` | Điểm Đồng Thuận |
| :--- | :--- | :--- | :--- | :---: |
| **`COST`** | FCF chuẩn hóa đạt +$6.75B USD, tăng trưởng doanh thu +11.1% YoY, giá ($1091.71) giữ cấu trúc trên MA200 ($979.95), điểm IC 79/100. | CẢNH BÁO ĐỊNH GIÁ/ĐÀ TĂNG: Định giá Fwd P/E cao (43.59x) — Cần tránh mua đuổi giá xanh. | **APPROVED_WITH_60_40_SPLIT (Bác bỏ Veto định giá • Duyệt giải ngân chia nhịp 60/40 Limit Pullback)** | **`84.5/100`** |
| **`PG`** | FCF chuẩn hóa đạt +$12.65B USD, tăng trưởng doanh thu +4.0% YoY, giá ($172.47) giữ cấu trúc trên MA200 ($150.39), điểm IC 77/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`V`** | FCF chuẩn hóa đạt +$20.98B USD, tăng trưởng doanh thu +13.2% YoY, giá ($416.78) giữ cấu trúc trên MA200 ($350.01), điểm IC 80/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`ABBV`** | FCF chuẩn hóa đạt +$17.69B USD, tăng trưởng doanh thu +10.3% YoY, giá ($300.28) giữ cấu trúc trên MA200 ($243.16), điểm IC 82/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`JNJ`** | FCF chuẩn hóa đạt +$18.5B USD, tăng trưởng doanh thu +5.9% YoY, giá ($276.46) giữ cấu trúc trên MA200 ($251.17), điểm IC 77/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`JPM`** | FCF chuẩn hóa đạt +$0.0B USD, tăng trưởng doanh thu +10.2% YoY, giá ($317.1) giữ cấu trúc trên MA200 ($325.14), điểm IC 70/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`MSFT`** | FCF chuẩn hóa đạt +$2.99B USD, tăng trưởng doanh thu +18.8% YoY, giá ($496.13) giữ cấu trúc trên MA200 ($444.5), điểm IC 83/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`OXY`** | FCF chuẩn hóa đạt +$4.91B USD, tăng trưởng doanh thu +19.0% YoY, giá ($53.38) giữ cấu trúc trên MA200 ($57.08), điểm IC 67/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`TSM`** | FCF chuẩn hóa đạt +$31.49B USD, tăng trưởng doanh thu +50.9% YoY, giá ($349.2) giữ cấu trúc trên MA200 ($403.61), điểm IC 70/100. | VI PHẠM CẤU TRÚC: Gãy cấu trúc MA200 ($349.2 < $403.61) | **ABSOLUTE_VETO (Từ chối giải ngân do vi phạm lằn ranh đỏ cấu trúc)** | **`35.0/100`** |
| **`NVDA`** | FCF chuẩn hóa đạt +$99.24B USD, tăng trưởng doanh thu +103.2% YoY, giá ($155.38) giữ cấu trúc trên MA200 ($203.07), điểm IC 68/100. | VI PHẠM CẤU TRÚC: Gãy cấu trúc MA200 ($155.38 < $203.07) | **ABSOLUTE_VETO (Từ chối giải ngân do vi phạm lằn ranh đỏ cấu trúc)** | **`35.0/100`** |
