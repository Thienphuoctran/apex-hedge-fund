# [BAN 4 — QUANT RISK] BÁO CÁO MA TRẬN TƯƠNG QUAN, ĐỊNH CỠ VỊ THẾ & KIỂM THỬ SỨC CHỊU ĐỰNG (STRESS TEST)
**Ngày kiểm toán**: 2026-10-30  
**Công cụ định lượng**: `scripts/quant_portfolio_engine.py` (1-Year Daily Returns, ATR(14) Risk-Parity & 3-Scenario Stress Test)

---

## 1. Tổng Quan Chỉ Số Rủi Ro Danh Mục (Portfolio Risk Telemetry)
- **Tỷ trọng Cổ phiếu / Tiền mặt (T-Bills ~5%)**: **`60.0% Cổ phiếu` / `40.0% Tiền mặt`**
- **Hệ số Beta Danh mục Tổng hợp (Portfolio Weighted Beta vs S&P 500)**: **`0.49`** *(Thấp hơn đáng kể so với biến động thị trường chung 1.00)*
- **Rủi ro Tối đa trên mỗi vị thế (Single-Trade Stop Risk)**: Trung bình **`~0.30% – 0.45% NAV`** nếu chạm ngưỡng cắt lỗ `2xATR(14)`
- **Tổng rủi ro danh mục nếu toàn bộ 10 vị thế đồng loạt chạm Stop-Loss**: **`-2.5% NAV`**

---

## 2. Ma Trận Tương Quan Lợi Suất 1 Năm (`Pairwise Return Correlation Matrix`)

| Mã | **`MSFT`** | **`TSM`** | **`JPM`** | **`OXY`** | **`NVDA`** | **`PG`** | **`JNJ`** | **`V`** | **`AAPL`** | **`BRK-B`** |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`MSFT`** | `1.00` | 0.17 | 0.06 | -0.09 | 0.25 | -0.14 | -0.23 | 0.19 | 0.11 | 0.04 |
| **`TSM`** | 0.17 | `1.00` | 0.12 | -0.25 | **0.66** | -0.18 | -0.24 | -0.11 | 0.09 | -0.21 |
| **`JPM`** | 0.06 | 0.12 | `1.00` | -0.12 | 0.12 | 0.07 | 0.09 | 0.32 | 0.16 | 0.23 |
| **`OXY`** | -0.09 | -0.25 | -0.12 | `1.00` | -0.16 | -0.13 | -0.00 | -0.10 | -0.18 | -0.08 |
| **`NVDA`** | 0.25 | **0.66** | 0.12 | -0.16 | `1.00` | -0.26 | -0.23 | -0.13 | 0.05 | -0.26 |
| **`PG`** | -0.14 | -0.18 | 0.07 | -0.13 | -0.26 | `1.00` | 0.41 | 0.20 | 0.19 | 0.36 |
| **`JNJ`** | -0.23 | -0.24 | 0.09 | -0.00 | -0.23 | 0.41 | `1.00` | 0.12 | 0.09 | 0.18 |
| **`V`** | 0.19 | -0.11 | 0.32 | -0.10 | -0.13 | 0.20 | 0.12 | `1.00` | 0.19 | 0.33 |
| **`AAPL`** | 0.11 | 0.09 | 0.16 | -0.18 | 0.05 | 0.19 | 0.09 | 0.19 | `1.00` | 0.15 |
| **`BRK-B`** | 0.04 | -0.21 | 0.23 | -0.08 | -0.26 | 0.36 | 0.18 | 0.33 | 0.15 | `1.00` |

### Cảnh Báo Cụm Tương Quan Cao (`Cluster Risk Alerts`)
| Cặp Cổ Phiếu | Hệ số Tương quan (`r`) | Mức độ Cảnh báo | Quy tắc Kiểm soát Tỷ trọng của Hội đồng |
| :--- | :---: | :--- | :--- |
| **`TSM - NVDA`** | `0.66` | MODERATE CORRELATION (0.55-0.69) | Giới hạn tổng tỷ trọng cụm Bán dẫn (`NVDA + TSM`) không vượt quá **12% – 14% NAV** |

---

## 3. Bảng Định Cỡ Vị Thế Theo Độ Biến Động (`ATR Risk-Parity Position Sizing`) & Radar Sự Kiện

| Mã | Ngành | Giá ($) | Stop `2xATR` ($) | Khoảng cách Stop (%) | Tỷ trọng chuẩn hóa (% NAV) | Rủi ro mất vốn tối đa (% NAV) | Sở hữu Tổ chức (%) | Tín hiệu Nội bộ (SEC Form 4) | Cảnh báo Lịch BCTC (`Earnings Radar`) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- |
| **`BRK-B`** | Diversified Conglomerate | $542.49 | **$528.67** | -2.54% | **9.1% NAV** | `-0.23% NAV` | 66.99% | Neutral / Routine | IMMINENT EARNINGS (7d) — Cấm mua đuổi sát BCTC |
| **`V`** | Global Payment Network | $413.59 | **$398.62** | -3.62% | **6.8% NAV** | `-0.25% NAV` | 88.73% | Neutral / Routine | CLEAR (2027-01-26) |
| **`JPM`** | Global Diversified Banking | $337.04 | **$324.06** | -3.84% | **6.6% NAV** | `-0.25% NAV` | 75.6% | Net Insider Buying (Tích cực) | CLEAR (2027-01-14) |
| **`PG`** | Consumer Household Staples | $161.57 | **$155.08** | -4.02% | **6.6% NAV** | `-0.27% NAV` | 71.83% | Net Insider Buying (Tích cực) | CLEAR (2027-01-21) |
| **`MSFT`** | Enterprise Software & Cloud | $521.91 | **$499.59** | -4.28% | **6.5% NAV** | `-0.28% NAV` | 75.78% | Net Insider Buying (Tích cực) | CLEAR (2027-01-27) |
| **`AAPL`** | Consumer Tech & Ecosystem | $344.63 | **$332.5** | -3.52% | **6.2% NAV** | `-0.22% NAV` | 66.33% | Net Insider Buying (Tích cực) | IMMINENT EARNINGS (2d) — Cấm mua đuổi sát BCTC |
| **`OXY`** | Upstream Oil & Carbon Capture | $64.0 | **$60.96** | -4.76% | **5.6% NAV** | `-0.27% NAV` | 58.19% | Neutral / Routine | UPCOMING EARNINGS (9d) — Lưu ý biến động |
| **`JNJ`** | Pharmaceuticals & MedTech | $273.2 | **$258.42** | -5.4% | **4.4% NAV** | `-0.24% NAV` | 76.77% | Neutral / Routine | CLEAR (2026-10-13) |
| **`NVDA`** | Semiconductors & AI | $204.64 | **$192.75** | -5.8% | **4.2% NAV** | `-0.24% NAV` | 71.52% | Net Insider Selling (Chốt lời nội bộ) | UPCOMING EARNINGS (17d) — Lưu ý biến động |
| **`TSM`** | Global Chip Foundry | $406.13 | **$380.4** | -6.34% | **4.0% NAV** | `-0.25% NAV` | 15.52% | Neutral / Routine | CLEAR (2027-01-14) |

---

## 4. Kiểm Thử Sức Chịu Đựng Danh Mục Trước 3 Cú Sốc Vĩ Mô (`Institutional Stress-Testing`)

| Kịch bản Cú sốc Vĩ mô / Địa chính trị | Giả định S&P 500 | Tác động Dự kiến lên Danh mục | Mức Vượt trội (Alpha Bảo vệ) | Cơ chế Phòng vệ Tự động của Danh mục |
| :--- | :---: | :---: | :---: | :--- |
| **Kịch bản 1: Cú sốc Bán tháo Thị trường (S&P 500 sập -10.0%)**<br>*(Kích hoạt: Khủng hoảng thanh khoản hoặc dữ liệu kinh tế xấu đột biến)* | `-10.0%` | **`-4.79% NAV`** | **`+5.21%`** | Beta danh mục thấp (0.49) + Đệm 40% Tiền mặt/T-Bills + Kích hoạt Stop-Loss 2xATR tự động |
| **Kịch bản 2: Cú sốc Lãi suất Fed Diều hâu (US 10Y Yield vọt lên 5.45%)**<br>*(Kích hoạt: PCE/CPI vượt 4.0% buộc Fed tăng lãi suất thêm +25–50 bps)* | `-6.5%` | **`-1.59% NAV`** | **`+4.91%`** | Nhóm Ngân hàng/Giá trị (JPM, BRK-B) và 40% T-Bills hưởng lợi trực tiếp bù đắp cho nhóm Công nghệ |
| **Kịch bản 3: Cú sốc Giá Dầu Địa chính trị (WTI Crude vọt lên $125/thùng)**<br>*(Kích hoạt: Gián đoạn nghiêm trọng eo biển Hormuz hoặc cơ sở lọc dầu toàn cầu)* | `-5.5%` | **`-0.8% NAV`** | **`+4.7%`** | Vị thế Dầu khí (OXY) và Phòng thủ (PG, JNJ, BRK-B) đóng vai trò Natural Hedge bảo vệ NAV |
