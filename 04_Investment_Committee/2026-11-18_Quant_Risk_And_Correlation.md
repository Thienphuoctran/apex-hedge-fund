# [BAN 4 — QUANT RISK] BÁO CÁO MA TRẬN TƯƠNG QUAN, ĐỊNH CỠ VỊ THẾ & KIỂM THỬ SỨC CHỊU ĐỰNG (STRESS TEST)
**Ngày kiểm toán**: 2026-11-18  
**Công cụ định lượng**: `scripts/quant_portfolio_engine.py` (v5.0 Audited — 0 Imminent Earnings Violations, Chandelier Stop & ATR Risk-Parity)

---

## 1. Tổng Quan Chỉ Số Rủi Ro Danh Mục (Portfolio Risk Telemetry)
- **Tỷ trọng Cổ phiếu / Tiền mặt (T-Bills ~5%)**: **`60.0% Cổ phiếu` / `40.0% Tiền mặt`**
- **Hệ số Beta Danh mục Tổng hợp (Portfolio Weighted Beta vs S&P 500)**: **`0.39`** *(Thấp hơn đáng kể so với biến động thị trường chung 1.00)*
- **Kiểm soát Cụm Bán dẫn (`NVDA + TSM`)**: **`4.7% NAV`** *(Tuân thủ trần `<= 14.0% NAV`)*
- **Tổng rủi ro danh mục nếu toàn bộ 10 vị thế đồng loạt chạm Stop-Loss `2xATR(14)`**: **`-3.42% NAV`**
- **Số mã bị khóa mua mới do sát lịch BCTC (`0 <= days_to_earnings <= 7`)**: **`1 mã`** (`WMT`)

---

## 2. Ma Trận Tương Quan Lợi Suất 1 Năm (`Pairwise Return Correlation Matrix`)

| Mã | **`MSFT`** | **`TSM`** | **`JPM`** | **`OXY`** | **`NVDA`** | **`PG`** | **`JNJ`** | **`V`** | **`ABBV`** | **`COST`** |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`MSFT`** | `1.00` | 0.17 | 0.13 | -0.10 | 0.22 | -0.10 | -0.16 | 0.21 | -0.10 | -0.07 |
| **`TSM`** | 0.17 | `1.00` | 0.17 | -0.20 | **0.66** | -0.19 | -0.16 | -0.07 | -0.13 | -0.24 |
| **`JPM`** | 0.13 | 0.17 | `1.00` | -0.13 | 0.13 | 0.10 | 0.16 | 0.35 | 0.07 | -0.01 |
| **`OXY`** | -0.10 | -0.20 | -0.13 | `1.00` | -0.14 | -0.17 | -0.01 | -0.11 | 0.01 | 0.05 |
| **`NVDA`** | 0.22 | **0.66** | 0.13 | -0.14 | `1.00` | -0.28 | -0.20 | -0.10 | -0.15 | -0.32 |
| **`PG`** | -0.10 | -0.19 | 0.10 | -0.17 | -0.28 | `1.00` | 0.42 | 0.23 | 0.26 | 0.37 |
| **`JNJ`** | -0.16 | -0.16 | 0.16 | -0.01 | -0.20 | 0.42 | `1.00` | 0.16 | 0.53 | 0.32 |
| **`V`** | 0.21 | -0.07 | 0.35 | -0.11 | -0.10 | 0.23 | 0.16 | `1.00` | 0.23 | 0.25 |
| **`ABBV`** | -0.10 | -0.13 | 0.07 | 0.01 | -0.15 | 0.26 | 0.53 | 0.23 | `1.00` | 0.23 |
| **`COST`** | -0.07 | -0.24 | -0.01 | 0.05 | -0.32 | 0.37 | 0.32 | 0.25 | 0.23 | `1.00` |

---

## 3. Bảng Định Cỡ Vị Thế (`ATR Risk-Parity`), Chandelier Stop & Kiểm Toán Lịch BCTC

| Mã | Ngành | Giá ($) | Stop `2xATR` ($) | Chandelier Trailing ($) | Khoảng cách Stop (%) | Tỷ trọng (% NAV) | Rủi ro tối đa (% NAV) | Điểm IC (/100) | Lịch BCTC (`Earnings Radar`) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`PG`** | Consumer Household Staples | $171.72 | **$164.8** | $164.94 | -4.02% | **8.4% NAV** | `-0.34% NAV` | **78/100** | CLEAR (2027-01-21 BMO) |
| **`COST`** | Membership Warehouse Retail | $1110.08 | **$1067.05** | $1069.89 | -3.88% | **8.0% NAV** | `-0.31% NAV` | **63/100** | CLEAR (2026-12-10 AMC) |
| **`V`** | Global Payment Network | $416.77 | **$396.26** | $416.59 | -4.92% | **7.6% NAV** | `-0.37% NAV` | **83/100** | CLEAR (2027-01-26 AMC) |
| **`ABBV`** | Biotech & Immunology | $292.82 | **$278.11** | $284.55 | -5.02% | **7.4% NAV** | `-0.37% NAV` | **86/100** | CLEAR (2026-10-30 BMO) |
| **`JPM`** | Global Diversified Banking | $329.96 | **$312.95** | $338.54 | -5.16% | **6.8% NAV** | `-0.35% NAV` | **86/100** | CLEAR (2027-01-14 BMO) |
| **`JNJ`** | Pharmaceuticals & MedTech | $278.7 | **$264.42** | $272.4 | -5.12% | **6.7% NAV** | `-0.34% NAV` | **75/100** | CLEAR (2027-01-26 BMO) |
| **`OXY`** | Upstream Oil & Carbon Capture | $56.52 | **$52.74** | $60.24 | -6.68% | **5.4% NAV** | `-0.36% NAV` | **84/100** | CLEAR (2026-11-09 AMC) |
| **`MSFT`** | Enterprise Software & Cloud | $506.24 | **$468.65** | $512.16 | -7.42% | **5.0% NAV** | `-0.37% NAV` | **83/100** | CLEAR (2027-01-27 AMC) |
| **`TSM`** | Global Chip Foundry | $359.69 | **$317.59** | $388.26 | -11.7% | **2.6% NAV** | `-0.3% NAV` | **70/100** | CLEAR (2027-01-14 BMO) |
| **`NVDA`** | Semiconductors & AI | $155.46 | **$132.47** | $193.45 | -14.78% | **2.1% NAV** | `-0.31% NAV` | **70/100** | JUST REPORTED (1d ago) — Đã qua rủi ro BCTC |

### Danh Sách Theo Dõi Tạm Khóa Do Sát Ngày Công Bố BCTC (`Locked Imminent Earnings Watchlist <= 7 Ngày`)
| Mã | Ngành | Giá ($) | Ngày BCTC | Phiên | Số Ngày Còn Lại | Implied Move (±%) | Điểm IC | Lý Do Khóa & Kế Hoạch Hành Động Sau BCTC |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`WMT`** | Discount Retail & Grocery | $127.52 | `2026-11-19` | BMO | **1d** | `±5.71%` | 55/100 | Quan sát phản ứng giá sau BCTC ngày 2026-11-19 trước khi mở vị thế. |

---

## 4. Kiểm Thử Sức Chịu Đựng Danh Mục Trước 3 Cú Sốc Vĩ Mô (`Institutional Stress-Testing`)

| Kịch bản Cú sốc Vĩ mô / Địa chính trị | Giả định S&P 500 | Tác động Dự kiến lên Danh mục | Mức Vượt trội (Alpha Bảo vệ) | Cơ chế Phòng vệ Tự động của Danh mục |
| :--- | :---: | :---: | :---: | :--- |
| **Kịch bản 1: Cú sốc Bán tháo Thị trường (S&P 500 sập -10.0%)**<br>*(Kích hoạt: Khủng hoảng thanh khoản hoặc dữ liệu kinh tế xấu đột biến)* | `-10.0%` | **`-3.78% NAV`** | **`+6.22%`** | Beta danh mục thấp (0.39) + Đệm 40.0% Tiền mặt/T-Bills + Kích hoạt Stop-Loss 2xATR & Chandelier Stop tự động |
| **Kịch bản 2: Cú sốc Lãi suất Fed Diều hâu (US 10Y Yield vọt lên 5.45%)**<br>*(Kích hoạt: PCE/CPI vượt 4.0% buộc Fed tăng lãi suất thêm +25–50 bps)* | `-6.5%` | **`-1.54% NAV`** | **`+4.96%`** | Nhóm Ngân hàng/Tài chính (JPM, V) và 40.0% T-Bills hưởng lợi trực tiếp bù đắp cho nhóm Công nghệ |
| **Kịch bản 3: Cú sốc Giá Dầu Địa chính trị (WTI Crude vọt lên $125/thùng)**<br>*(Kích hoạt: Gián đoạn nghiêm trọng eo biển Hormuz hoặc cơ sở lọc dầu toàn cầu)* | `-5.5%` | **`-0.47% NAV`** | **`+5.03%`** | Vị thế Dầu khí (OXY) và Phòng thủ Thiết yếu/Y tế (PG, JNJ, ABBV, COST) đóng vai trò Natural Hedge bảo vệ NAV |

---

## 5. Phiên Tranh Biện Đối Kháng Đa Tác Tử (`Adversarial Bull vs Bear Debate — CIO Anti-Paralysis Protocol`)
| Mã | Luận Điểm Bảo Vệ Của `Bull Agent` | Phản Biện Đào Bới Rủi Ro Của `Bear Agent` | Phán Quyết Hòa Giải Của `Master CIO` | Điểm Đồng Thuận |
| :--- | :--- | :--- | :--- | :---: |
| **`PG`** | FCF chuẩn hóa đạt +$12.65B USD, tăng trưởng doanh thu +4.0% YoY, giá ($171.72) giữ cấu trúc trên MA200 ($150.08), điểm IC 78/100. | CẢNH BÁO ĐỊNH GIÁ/ĐÀ TĂNG: RSI tiệm cận vùng nóng (68.49) — Cần tránh mua đuổi giá xanh. | **APPROVED_WITH_60_40_SPLIT (Bác bỏ Veto định giá • Duyệt giải ngân chia nhịp 60/40 Limit Pullback)** | **`84.5/100`** |
| **`COST`** | FCF chuẩn hóa đạt +$6.75B USD, tăng trưởng doanh thu +11.1% YoY, giá ($1110.08) giữ cấu trúc trên MA200 ($977.26), điểm IC 63/100. | CẢNH BÁO ĐỊNH GIÁ/ĐÀ TĂNG: Định giá Fwd P/E cao (44.33x); RSI tiệm cận vùng nóng (75.34) — Cần tránh mua đuổi giá xanh. | **APPROVED_WITH_60_40_SPLIT (Bác bỏ Veto định giá • Duyệt giải ngân chia nhịp 60/40 Limit Pullback)** | **`84.5/100`** |
| **`V`** | FCF chuẩn hóa đạt +$20.98B USD, tăng trưởng doanh thu +13.2% YoY, giá ($416.77) giữ cấu trúc trên MA200 ($348.0), điểm IC 83/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`ABBV`** | FCF chuẩn hóa đạt +$17.69B USD, tăng trưởng doanh thu +10.3% YoY, giá ($292.82) giữ cấu trúc trên MA200 ($241.48), điểm IC 86/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`JPM`** | FCF chuẩn hóa đạt +$0.0B USD, tăng trưởng doanh thu +10.2% YoY, giá ($329.96) giữ cấu trúc trên MA200 ($325.13), điểm IC 86/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`JNJ`** | FCF chuẩn hóa đạt +$18.5B USD, tăng trưởng doanh thu +5.9% YoY, giá ($278.7) giữ cấu trúc trên MA200 ($250.3), điểm IC 75/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`OXY`** | FCF chuẩn hóa đạt +$4.91B USD, tăng trưởng doanh thu +19.0% YoY, giá ($56.52) giữ cấu trúc trên MA200 ($56.89), điểm IC 84/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`MSFT`** | FCF chuẩn hóa đạt +$2.99B USD, tăng trưởng doanh thu +18.8% YoY, giá ($506.24) giữ cấu trúc trên MA200 ($442.27), điểm IC 83/100. | Rủi ro thị trường chung và biến động lãi suất US10Y; không có điểm yếu nội tại BCTC. | **UNANIMOUS_STRONG_APPROVAL (Đồng thuận tuyệt đối Bull & Risk Manager)** | **`92.0/100`** |
| **`TSM`** | FCF chuẩn hóa đạt +$31.69B USD, tăng trưởng doanh thu +50.9% YoY, giá ($359.69) giữ cấu trúc trên MA200 ($403.36), điểm IC 70/100. | VI PHẠM CẤU TRÚC: Gãy cấu trúc MA200 ($359.69 < $403.36) | **ABSOLUTE_VETO (Từ chối giải ngân do vi phạm lằn ranh đỏ cấu trúc)** | **`35.0/100`** |
| **`NVDA`** | FCF chuẩn hóa đạt +$41.81B USD, tăng trưởng doanh thu +105.9% YoY, giá ($155.46) giữ cấu trúc trên MA200 ($203.87), điểm IC 70/100. | VI PHẠM CẤU TRÚC: Gãy cấu trúc MA200 ($155.46 < $203.87) | **ABSOLUTE_VETO (Từ chối giải ngân do vi phạm lằn ranh đỏ cấu trúc)** | **`35.0/100`** |
