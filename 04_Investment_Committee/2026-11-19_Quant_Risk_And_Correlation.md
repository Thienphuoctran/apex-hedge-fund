# [BAN 4 — QUANT RISK] BÁO CÁO MA TRẬN TƯƠNG QUAN, ĐỊNH CỠ VỊ THẾ & KIỂM THỬ SỨC CHỊU ĐỰNG (STRESS TEST)
**Ngày kiểm toán**: 2026-11-19  
**Công cụ định lượng**: `scripts/quant_portfolio_engine.py` (v5.0 Audited — 0 Imminent Earnings Violations, Chandelier Stop & ATR Risk-Parity)

---

## 1. Tổng Quan Chỉ Số Rủi Ro Danh Mục (Portfolio Risk Telemetry)
- **Tỷ trọng Cổ phiếu / Tiền mặt (T-Bills ~5%)**: **`60.0% Cổ phiếu` / `40.0% Tiền mặt`**
- **Hệ số Beta Danh mục Tổng hợp (Portfolio Weighted Beta vs S&P 500)**: **`0.4`** *(Thấp hơn đáng kể so với biến động thị trường chung 1.00)*
- **Kiểm soát Cụm Bán dẫn (`NVDA + TSM`)**: **`4.7% NAV`** *(Tuân thủ trần `<= 14.0% NAV`)*
- **Tổng rủi ro danh mục nếu toàn bộ 10 vị thế đồng loạt chạm Stop-Loss `2xATR(14)`**: **`-3.47% NAV`**
- **Số mã bị khóa mua mới do sát lịch BCTC (`0 <= days_to_earnings <= 7`)**: **`1 mã`** (`WMT`)

---

## 2. Ma Trận Tương Quan Lợi Suất 1 Năm (`Pairwise Return Correlation Matrix`)

| Mã | **`MSFT`** | **`TSM`** | **`JPM`** | **`OXY`** | **`NVDA`** | **`PG`** | **`JNJ`** | **`V`** | **`ABBV`** | **`COST`** |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`MSFT`** | `1.00` | 0.17 | 0.13 | -0.11 | 0.22 | -0.11 | -0.16 | 0.21 | -0.10 | -0.07 |
| **`TSM`** | 0.17 | `1.00` | 0.17 | -0.19 | **0.66** | -0.19 | -0.17 | -0.08 | -0.13 | -0.24 |
| **`JPM`** | 0.13 | 0.17 | `1.00` | -0.12 | 0.13 | 0.11 | 0.17 | 0.35 | 0.08 | -0.00 |
| **`OXY`** | -0.11 | -0.19 | -0.12 | `1.00` | -0.12 | -0.16 | 0.01 | -0.11 | 0.02 | 0.05 |
| **`NVDA`** | 0.22 | **0.66** | 0.13 | -0.12 | `1.00` | -0.28 | -0.19 | -0.10 | -0.14 | -0.31 |
| **`PG`** | -0.11 | -0.19 | 0.11 | -0.16 | -0.28 | `1.00` | 0.42 | 0.23 | 0.26 | 0.38 |
| **`JNJ`** | -0.16 | -0.17 | 0.17 | 0.01 | -0.19 | 0.42 | `1.00` | 0.16 | 0.53 | 0.32 |
| **`V`** | 0.21 | -0.08 | 0.35 | -0.11 | -0.10 | 0.23 | 0.16 | `1.00` | 0.23 | 0.25 |
| **`ABBV`** | -0.10 | -0.13 | 0.08 | 0.02 | -0.14 | 0.26 | 0.53 | 0.23 | `1.00` | 0.23 |
| **`COST`** | -0.07 | -0.24 | -0.00 | 0.05 | -0.31 | 0.38 | 0.32 | 0.25 | 0.23 | `1.00` |

---

## 3. Bảng Định Cỡ Vị Thế (`ATR Risk-Parity`), Chandelier Stop & Kiểm Toán Lịch BCTC

| Mã | Ngành | Giá ($) | Stop `2xATR` ($) | Chandelier Trailing ($) | Khoảng cách Stop (%) | Tỷ trọng (% NAV) | Rủi ro tối đa (% NAV) | Điểm IC (/100) | Lịch BCTC (`Earnings Radar`) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`PG`** | Consumer Household Staples | $170.29 | **$163.43** | $165.01 | -4.04% | **9.2% NAV** | `-0.37% NAV` | **81/100** | CLEAR (2027-01-21 BMO) |
| **`COST`** | Membership Warehouse Retail | $1096.62 | **$1053.0** | $1069.15 | -3.98% | **8.7% NAV** | `-0.35% NAV` | **77/100** | UPCOMING EARNINGS (21d, AMC) — Lưu ý biến động |
| **`V`** | Global Payment Network | $415.22 | **$395.49** | $417.57 | -4.76% | **7.7% NAV** | `-0.37% NAV` | **80/100** | CLEAR (2027-01-26 AMC) |
| **`ABBV`** | Biotech & Immunology | $286.01 | **$271.13** | $284.33 | -5.2% | **7.1% NAV** | `-0.37% NAV` | **83/100** | CLEAR (2026-10-30 BMO) |
| **`JPM`** | Global Diversified Banking | $324.11 | **$307.11** | $338.55 | -5.24% | **6.6% NAV** | `-0.35% NAV` | **83/100** | CLEAR (2027-01-14 BMO) |
| **`JNJ`** | Pharmaceuticals & MedTech | $272.7 | **$258.55** | $272.56 | -5.18% | **6.3% NAV** | `-0.33% NAV` | **74/100** | CLEAR (2027-01-26 BMO) |
| **`MSFT`** | Enterprise Software & Cloud | $508.29 | **$472.47** | $514.37 | -7.04% | **5.4% NAV** | `-0.38% NAV` | **83/100** | CLEAR (2027-01-27 AMC) |
| **`OXY`** | Upstream Oil & Carbon Capture | $53.76 | **$49.77** | $59.97 | -7.42% | **4.3% NAV** | `-0.32% NAV` | **67/100** | CLEAR (2026-11-09 AMC) |
| **`TSM`** | Global Chip Foundry | $362.62 | **$320.38** | $388.08 | -11.64% | **2.7% NAV** | `-0.31% NAV` | **70/100** | CLEAR (2027-01-14 BMO) |
| **`NVDA`** | Semiconductors & AI | $150.96 | **$127.11** | $192.38 | -15.8% | **2.0% NAV** | `-0.32% NAV` | **70/100** | JUST REPORTED (2d ago) — Đã qua rủi ro BCTC |

### Danh Sách Theo Dõi Tạm Khóa Do Sát Ngày Công Bố BCTC (`Locked Imminent Earnings Watchlist <= 7 Ngày`)
| Mã | Ngành | Giá ($) | Ngày BCTC | Phiên | Số Ngày Còn Lại | Implied Move (±%) | Điểm IC | Lý Do Khóa & Kế Hoạch Hành Động Sau BCTC |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`WMT`** | Discount Retail & Grocery | $127.36 | `2026-11-19` | BMO | **0d** | `±5.69%` | 58/100 | Quan sát phản ứng giá sau BCTC ngày 2026-11-19 trước khi mở vị thế. |

---

## 4. Kiểm Thử Sức Chịu Đựng Danh Mục Trước 3 Cú Sốc Vĩ Mô (`Institutional Stress-Testing`)

| Kịch bản Cú sốc Vĩ mô / Địa chính trị | Giả định S&P 500 | Tác động Dự kiến lên Danh mục | Mức Vượt trội (Alpha Bảo vệ) | Cơ chế Phòng vệ Tự động của Danh mục |
| :--- | :---: | :---: | :---: | :--- |
| **Kịch bản 1: Cú sốc Bán tháo Thị trường (S&P 500 sập -10.0%)**<br>*(Kích hoạt: Khủng hoảng thanh khoản hoặc dữ liệu kinh tế xấu đột biến)* | `-10.0%` | **`-3.86% NAV`** | **`+6.14%`** | Beta danh mục thấp (0.4) + Đệm 40.0% Tiền mặt/T-Bills + Kích hoạt Stop-Loss 2xATR & Chandelier Stop tự động |
| **Kịch bản 2: Cú sốc Lãi suất Fed Diều hâu (US 10Y Yield vọt lên 5.45%)**<br>*(Kích hoạt: PCE/CPI vượt 4.0% buộc Fed tăng lãi suất thêm +25–50 bps)* | `-6.5%` | **`-1.55% NAV`** | **`+4.95%`** | Nhóm Ngân hàng/Tài chính (JPM, V) và 40.0% T-Bills hưởng lợi trực tiếp bù đắp cho nhóm Công nghệ |
| **Kịch bản 3: Cú sốc Giá Dầu Địa chính trị (WTI Crude vọt lên $125/thùng)**<br>*(Kích hoạt: Gián đoạn nghiêm trọng eo biển Hormuz hoặc cơ sở lọc dầu toàn cầu)* | `-5.5%` | **`-0.65% NAV`** | **`+4.85%`** | Vị thế Dầu khí (OXY) và Phòng thủ Thiết yếu/Y tế (PG, JNJ, ABBV, COST) đóng vai trò Natural Hedge bảo vệ NAV |

---

## 5. Phiên Tranh Biện Đối Kháng Đa Tác Tử (`Adversarial Bull vs Bear Debate — CIO Anti-Paralysis Protocol`)
| Mã | Luận Điểm Bảo Vệ Của `Bull Agent` | Phản Biện Đào Bới Rủi Ro Của `Bear Agent` | Phán Quyết Hòa Giải Của `Master CIO` | Điểm Đồng Thuận |
| :--- | :--- | :--- | :--- | :---: |
| **`PG`** | FCF chuẩn hóa đạt +$12.65B USD, tăng trưởng doanh thu +4.0% YoY, giá ($170.29) giữ cấu trúc trên MA200 ($150.15), điểm IC 81/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`COST`** | FCF chuẩn hóa đạt +$6.75B USD, tăng trưởng doanh thu +11.1% YoY, giá ($1096.62) giữ cấu trúc trên MA200 ($977.85), điểm IC 77/100. | CẢNH BÁO ĐỊNH GIÁ/ĐÀ TĂNG: Định giá Fwd P/E cao (43.79x); RSI tiệm cận vùng nóng (69.08) — Cần tránh mua đuổi giá xanh. | **APPROVED_WITH_60_40_SPLIT (Bác bỏ Veto định giá • Duyệt giải ngân chia nhịp 60/40 Limit Pullback)** | **`84.5/100`** |
| **`V`** | FCF chuẩn hóa đạt +$20.98B USD, tăng trưởng doanh thu +13.2% YoY, giá ($415.22) giữ cấu trúc trên MA200 ($348.43), điểm IC 80/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`ABBV`** | FCF chuẩn hóa đạt +$17.69B USD, tăng trưởng doanh thu +10.3% YoY, giá ($286.01) giữ cấu trúc trên MA200 ($241.78), điểm IC 83/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`JPM`** | FCF chuẩn hóa đạt +$0.0B USD, tăng trưởng doanh thu +10.2% YoY, giá ($324.11) giữ cấu trúc trên MA200 ($325.18), điểm IC 83/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`JNJ`** | FCF chuẩn hóa đạt +$18.5B USD, tăng trưởng doanh thu +5.9% YoY, giá ($272.7) giữ cấu trúc trên MA200 ($250.5), điểm IC 74/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`MSFT`** | FCF chuẩn hóa đạt +$2.99B USD, tăng trưởng doanh thu +18.8% YoY, giá ($508.29) giữ cấu trúc trên MA200 ($442.76), điểm IC 83/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`OXY`** | FCF chuẩn hóa đạt +$4.91B USD, tăng trưởng doanh thu +19.0% YoY, giá ($53.76) giữ cấu trúc trên MA200 ($56.94), điểm IC 67/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`TSM`** | FCF chuẩn hóa đạt +$31.69B USD, tăng trưởng doanh thu +50.9% YoY, giá ($362.62) giữ cấu trúc trên MA200 ($403.49), điểm IC 70/100. | VI PHẠM CẤU TRÚC: Gãy cấu trúc MA200 ($362.62 < $403.49) | **ABSOLUTE_VETO (Từ chối giải ngân do vi phạm lằn ranh đỏ cấu trúc)** | **`35.0/100`** |
| **`NVDA`** | FCF chuẩn hóa đạt +$41.81B USD, tăng trưởng doanh thu +105.9% YoY, giá ($150.96) giữ cấu trúc trên MA200 ($203.72), điểm IC 70/100. | VI PHẠM CẤU TRÚC: Gãy cấu trúc MA200 ($150.96 < $203.72) | **ABSOLUTE_VETO (Từ chối giải ngân do vi phạm lằn ranh đỏ cấu trúc)** | **`35.0/100`** |
