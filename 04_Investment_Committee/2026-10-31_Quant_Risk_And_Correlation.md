# [BAN 4 — QUANT RISK] BÁO CÁO MA TRẬN TƯƠNG QUAN, ĐỊNH CỠ VỊ THẾ & KIỂM THỬ SỨC CHỊU ĐỰNG (STRESS TEST)
**Ngày kiểm toán**: 2026-10-31  
**Công cụ định lượng**: `scripts/quant_portfolio_engine.py` (v5.0 Audited — 0 Imminent Earnings Violations, Chandelier Stop & ATR Risk-Parity)

---

## 1. Tổng Quan Chỉ Số Rủi Ro Danh Mục (Portfolio Risk Telemetry)
- **Tỷ trọng Cổ phiếu / Tiền mặt (T-Bills ~5%)**: **`60.0% Cổ phiếu` / `40.0% Tiền mặt`**
- **Hệ số Beta Danh mục Tổng hợp (Portfolio Weighted Beta vs S&P 500)**: **`0.48`** *(Thấp hơn đáng kể so với biến động thị trường chung 1.00)*
- **Kiểm soát Cụm Bán dẫn (`NVDA + TSM`)**: **`8.7% NAV`** *(Tuân thủ trần `<= 14.0% NAV`)*
- **Tổng rủi ro danh mục nếu toàn bộ 10 vị thế đồng loạt chạm Stop-Loss `2xATR(14)`**: **`-2.66% NAV`**
- **Số mã bị khóa mua mới do sát lịch BCTC (`0 <= days_to_earnings <= 7`)**: **`9 mã`** (`AAPL, PLTR, AMD, SMCI, QCOM, ARM, NVO, MCD, BRK-B`)

---

## 2. Ma Trận Tương Quan Lợi Suất 1 Năm (`Pairwise Return Correlation Matrix`)

| Mã | **`MSFT`** | **`TSM`** | **`JPM`** | **`OXY`** | **`NVDA`** | **`PG`** | **`JNJ`** | **`V`** | **`ABBV`** | **`COST`** |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`MSFT`** | `1.00` | 0.17 | 0.07 | -0.09 | 0.25 | -0.14 | -0.23 | 0.19 | -0.14 | -0.06 |
| **`TSM`** | 0.17 | `1.00` | 0.13 | -0.25 | **0.66** | -0.18 | -0.23 | -0.12 | -0.19 | -0.21 |
| **`JPM`** | 0.07 | 0.13 | `1.00` | -0.13 | 0.13 | 0.07 | 0.09 | 0.31 | 0.05 | -0.05 |
| **`OXY`** | -0.09 | -0.25 | -0.13 | `1.00` | -0.16 | -0.12 | -0.00 | -0.09 | 0.00 | 0.08 |
| **`NVDA`** | 0.25 | **0.66** | 0.13 | -0.16 | `1.00` | -0.26 | -0.22 | -0.13 | -0.20 | -0.28 |
| **`PG`** | -0.14 | -0.18 | 0.07 | -0.12 | -0.26 | `1.00` | 0.41 | 0.21 | 0.26 | 0.34 |
| **`JNJ`** | -0.23 | -0.23 | 0.09 | -0.00 | -0.22 | 0.41 | `1.00` | 0.12 | 0.52 | 0.29 |
| **`V`** | 0.19 | -0.12 | 0.31 | -0.09 | -0.13 | 0.21 | 0.12 | `1.00` | 0.21 | 0.24 |
| **`ABBV`** | -0.14 | -0.19 | 0.05 | 0.00 | -0.20 | 0.26 | 0.52 | 0.21 | `1.00` | 0.22 |
| **`COST`** | -0.06 | -0.21 | -0.05 | 0.08 | -0.28 | 0.34 | 0.29 | 0.24 | 0.22 | `1.00` |

---

## 3. Bảng Định Cỡ Vị Thế (`ATR Risk-Parity`), Chandelier Stop & Kiểm Toán Lịch BCTC

| Mã | Ngành | Giá ($) | Stop `2xATR` ($) | Chandelier Trailing ($) | Khoảng cách Stop (%) | Tỷ trọng (% NAV) | Rủi ro tối đa (% NAV) | Điểm IC (/100) | Lịch BCTC (`Earnings Radar`) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`JPM`** | Global Diversified Banking | $337.04 | **$324.06** | $325.02 | -3.84% | **7.2% NAV** | `-0.28% NAV` | **90/100** | CLEAR (2027-01-14 BMO) |
| **`V`** | Global Payment Network | $413.59 | **$398.62** | $394.89 | -3.62% | **7.2% NAV** | `-0.26% NAV` | **81/100** | CLEAR (2027-01-26 AMC) |
| **`PG`** | Consumer Household Staples | $161.57 | **$155.08** | $153.44 | -4.02% | **7.1% NAV** | `-0.29% NAV` | **89/100** | CLEAR (2027-01-21 BMO) |
| **`MSFT`** | Enterprise Software & Cloud | $521.91 | **$499.59** | $513.48 | -4.28% | **7.0% NAV** | `-0.3% NAV` | **87/100** | CLEAR (2027-01-27 AMC) |
| **`COST`** | Membership Warehouse Retail | $1012.28 | **$978.88** | $970.53 | -3.3% | **7.0% NAV** | `-0.23% NAV` | **78/100** | CLEAR (2026-12-10 AMC) |
| **`OXY`** | Upstream Oil & Carbon Capture | $64.0 | **$60.96** | $60.2 | -4.76% | **6.0% NAV** | `-0.29% NAV` | **91/100** | UPCOMING EARNINGS (9d, AMC) — Lưu ý biến động |
| **`ABBV`** | Biotech & Immunology | $294.89 | **$281.46** | $278.12 | -4.56% | **5.1% NAV** | `-0.23% NAV` | **80/100** | JUST REPORTED (1d ago) — Đã qua rủi ro BCTC |
| **`JNJ`** | Pharmaceuticals & MedTech | $273.2 | **$258.42** | $254.72 | -5.4% | **4.7% NAV** | `-0.25% NAV` | **82/100** | CLEAR (2026-10-13 BMO) |
| **`NVDA`** | Semiconductors & AI | $204.64 | **$192.75** | $212.54 | -5.8% | **4.5% NAV** | `-0.26% NAV` | **81/100** | UPCOMING EARNINGS (17d, AMC) — Lưu ý biến động |
| **`TSM`** | Global Chip Foundry | $406.13 | **$380.4** | $417.61 | -6.34% | **4.2% NAV** | `-0.27% NAV` | **83/100** | CLEAR (2027-01-14 BMO) |

### Danh Sách Theo Dõi Tạm Khóa Do Sát Ngày Công Bố BCTC (`Locked Imminent Earnings Watchlist <= 7 Ngày`)
| Mã | Ngành | Giá ($) | Ngày BCTC | Phiên | Số Ngày Còn Lại | Implied Move (±%) | Điểm IC | Lý Do Khóa & Kế Hoạch Hành Động Sau BCTC |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`AAPL`** | Consumer Tech & Ecosystem | $344.63 | `2026-11-02` | AMC | **2d** | `±4.14%` | 68/100 | Chờ BCTC công bố ngày 2026-11-02; chỉ giải ngân nếu giữ vững MA50 ($332.37) và hướng dẫn EPS tích cực. |
| **`PLTR`** | Enterprise & Defense AI Software | $184.11 | `2026-11-02` | AMC | **2d** | `±10.95%` | 74/100 | Quan sát phản ứng giá sau BCTC ngày 2026-11-02 trước khi mở vị thế. |
| **`AMD`** | Processors & AI Accelerators | $504.8 | `2026-11-03` | AMC | **3d** | `±13.23%` | 77/100 | Quan sát phản ứng giá sau BCTC ngày 2026-11-03 trước khi mở vị thế. |
| **`SMCI`** | AI Server Infrastructure | $32.95 | `2026-11-03` | AMC | **3d** | `±14.5%` | 62/100 | Quan sát phản ứng giá sau BCTC ngày 2026-11-03 trước khi mở vị thế. |
| **`QCOM`** | Mobile & Edge AI Processors | $164.79 | `2026-11-04` | AMC | **4d** | `±8.58%` | 44/100 | Quan sát phản ứng giá sau BCTC ngày 2026-11-04 trước khi mở vị thế. |
| **`ARM`** | Semiconductor IP Architecture | $205.97 | `2026-11-04` | AMC | **4d** | `±14.5%` | 60/100 | Quan sát phản ứng giá sau BCTC ngày 2026-11-04 trước khi mở vị thế. |
| **`NVO`** | Biopharma GLP-1 Leader | $40.0 | `2026-11-04` | BMO | **4d** | `±4.37%` | 65/100 | Quan sát phản ứng giá sau BCTC ngày 2026-11-04 trước khi mở vị thế. |
| **`MCD`** | Global Quick Service Restaurants | $258.12 | `2026-11-04` | BMO | **4d** | `±4.25%` | 61/100 | Quan sát phản ứng giá sau BCTC ngày 2026-11-04 trước khi mở vị thế. |
| **`BRK-B`** | Diversified Conglomerate | $542.49 | `2026-11-07` | BMO | **7d** | `±2.98%` | 72/100 | Chờ BCTC công bố ngày 2026-11-07; chỉ giải ngân nếu giữ vững MA50 ($514.2) và hướng dẫn EPS tích cực. |

---

## 4. Kiểm Thử Sức Chịu Đựng Danh Mục Trước 3 Cú Sốc Vĩ Mô (`Institutional Stress-Testing`)

| Kịch bản Cú sốc Vĩ mô / Địa chính trị | Giả định S&P 500 | Tác động Dự kiến lên Danh mục | Mức Vượt trội (Alpha Bảo vệ) | Cơ chế Phòng vệ Tự động của Danh mục |
| :--- | :---: | :---: | :---: | :--- |
| **Kịch bản 1: Cú sốc Bán tháo Thị trường (S&P 500 sập -10.0%)**<br>*(Kích hoạt: Khủng hoảng thanh khoản hoặc dữ liệu kinh tế xấu đột biến)* | `-10.0%` | **`-4.64% NAV`** | **`+5.36%`** | Beta danh mục thấp (0.48) + Đệm 40.0% Tiền mặt/T-Bills + Kích hoạt Stop-Loss 2xATR & Chandelier Stop tự động |
| **Kịch bản 2: Cú sốc Lãi suất Fed Diều hâu (US 10Y Yield vọt lên 5.45%)**<br>*(Kích hoạt: PCE/CPI vượt 4.0% buộc Fed tăng lãi suất thêm +25–50 bps)* | `-6.5%` | **`-1.63% NAV`** | **`+4.87%`** | Nhóm Ngân hàng/Tài chính (JPM, V) và 40.0% T-Bills hưởng lợi trực tiếp bù đắp cho nhóm Công nghệ |
| **Kịch bản 3: Cú sốc Giá Dầu Địa chính trị (WTI Crude vọt lên $125/thùng)**<br>*(Kích hoạt: Gián đoạn nghiêm trọng eo biển Hormuz hoặc cơ sở lọc dầu toàn cầu)* | `-5.5%` | **`-0.59% NAV`** | **`+4.91%`** | Vị thế Dầu khí (OXY) và Phòng thủ Thiết yếu/Y tế (PG, JNJ, ABBV, COST) đóng vai trò Natural Hedge bảo vệ NAV |
