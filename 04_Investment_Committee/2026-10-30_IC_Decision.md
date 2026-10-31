# [BAN 4] QUYẾT ĐỊNH HỘI ĐỒNG ĐẦU TƯ & KẾ HOẠCH HÀNH ĐỘNG (AUDITED v3.0 — FULL QUANT SUITE)
**Ngày quyết định**: 2026-10-30 (Kiểm toán v3.0 lúc `17:27 UTC`)  
**Đơn vị phê duyệt**: `investment-committee-agent` (Hội đồng Đầu tư & Quản trị Rủi ro Định lượng)  
**Báo cáo Định lượng Đi kèm**: [`2026-10-30_Quant_Risk_And_Correlation.md`](./2026-10-30_Quant_Risk_And_Correlation.md)

---

## 1. Chiến Lược Phân Bổ Tài Sản Tổng Thể (Master Asset Allocation)
* **Thông số Rủi ro Hệ thống**: `VIX` = **21.15** (+22.97% 1D), `US 10Y Yield` = **4.94%**, `WTI Crude Oil` = **$104.81/thùng**, `S&P 500` = **7,576.74** (điều chỉnh dưới MA50 `7,697.01`, trên MA200 `7,309.74`).
* **Chế độ Quản trị Danh mục**: **`ATR Risk-Parity & Multi-Sector Balance` (Định cỡ Vị thế Theo Độ biến động ATR kết hợp Đa dạng hóa Đa ngành)**.
* **Tỷ trọng Phân bổ Khuyến nghị**:
  - **Cổ phiếu Quốc tế (US/Global Equities)**: **60.0% NAV** — Được phân bổ tự động theo mô hình **`ATR Risk-Parity`** trên 10 vị thế dẫn đầu sao cho:
    - **Hệ số Beta Danh mục Tổng hợp (`Portfolio Weighted Beta`)**: **`0.51`** (Thấp hơn một nửa biến động của S&P 500).
    - **Rủi ro Cắt lỗ Tối đa trên mỗi vị thế (`Single-Position Stop Risk`)**: Khóa chặt trong biên độ **`-0.23% đến -0.30% NAV`**.
    - **Tổng Rủi ro Danh mục nếu toàn bộ 10 vị thế chạm Stop-Loss cùng lúc**: **`-2.58% NAV`**.
  - **Dự trữ Tiền mặt / T-Bills Ngắn hạn (~5.0% Yield)**: **40.0% NAV** — Tạo đệm thanh khoản và sẵn sàng giải ngân khi `VIX` hạ nhiệt dưới 18 hoặc khi nhóm dẫn dắt đang quá mua (`XOM`, `CVX`, `LLY`, `LMT`) lùi về đường MA20.

---

## 2. Bảng Chấm Điểm Hội Đồng Đầu Tư, Radar BCTC & Dòng Tiền Nội Bộ (IC Scoring Matrix v3.0)

| Mã (Ticker) | Vĩ mô & Ngành (/25) | BCTC & Moat (/30) | Định giá & Upside (/25) | Kỹ thuật & R:R (/20) | Sở hữu Tổ chức (%) | Tín hiệu Nội bộ (SEC Form 4) | Cảnh báo Lịch BCTC (`Earnings Radar`) | **Tổng điểm (/100)** | **Quyết định của Hội đồng** |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- | :--- | :---: | :--- |
| **`MSFT`** | 21 | 29 | 22 *(Upside +20.5%)* | 18 *(Giữ MA50)* | **75.78%** | **Net Insider Buying (+263,995 cp)** | `CLEAR (2027-01-27)` | **90 / 100** | **STRONG BUY / ACCUMULATE** |
| **`TSM`** | 19 | 29 *(FCF $36.93B)* | 23 *(Fwd P/E 17.31x)* | 16 *(Chạm MA200)* | **15.52%** *(ADR)* | Neutral / Routine | `CLEAR (2027-01-14)` | **87 / 100** | **ACCUMULATE AT MA200** |
| **`JPM`** | 23 | 27 | 19 *(Fwd P/E 13.23x)* | 17 *(Quanh MA20)* | **75.60%** | **Net Insider Buying (Tích cực)** | `CLEAR (2027-01-14)` | **86 / 100** | **ACCUMULATE (Mua tích lũy)** |
| **`OXY`** | 24 *(XLE Sharpe 2.46)* | 24 | 20 *(Fwd P/E 12.74x)* | 16 *(RSI 64.09)* | **58.19%** | Neutral / Routine | `UPCOMING EARNINGS (10d)` | **84 / 100** | **ACCUMULATE (Mua tích lũy)** |
| **`NVDA`** | 19 | 30 *(FCF $41.81B)* | 22 *(Fwd P/E 12.79x)* | 13 *(Sát MA200)* | **71.52%** | Net Insider Selling (-3.58M cp) | `UPCOMING EARNINGS (18d)` | **84 / 100** | **SCALE-IN AT MA200 (Thăm dò)** |
| **`PG`** | 24 *(XLP Top 2)* | 26 | 16 *(Upside +6.4%)* | 16 *(Strong Uptrend)* | **71.83%** | **Net Insider Buying (Tích cực)** | `CLEAR (2027-01-21)` | **82 / 100** | **ACCUMULATE (Phòng thủ)** |
| **`JNJ`** | 24 *(XLV Top 1)* | 26 *(FCF $18.50B)* | 15 | 16 *(RSI 63.78)* | **76.77%** | Neutral / Routine | `CLEAR (2026-10-13)` | **81 / 100** | **ACCUMULATE (Phòng thủ)** |
| **`V`** | 21 | 29 *(Gross 97.7%)* | 16 | 14 *(RSI 70.77)* | **88.73%** | Neutral / Routine | `CLEAR (2027-01-26)` | **80 / 100** | **ACCUMULATE ON MINOR DIP** |
| **`BRK-B`** | 22 | 28 *(FCF $71.98B)* | 15 | 15 *(Biến động cực thấp)* | **66.99%** | Neutral / Routine | `UPCOMING EARNINGS (8d)` | **80 / 100** | **CORE DEFENSIVE ANCHOR** |
| **`AAPL`** | 20 | 28 *(FCF $107.72B)* | 14 *(-4.04% Target)* | 16 *(Strong Uptrend)* | **66.33%** | **Net Insider Buying (+257,744 cp)** | ⚠️ `IMMINENT EARNINGS (3d)` | **78 / 100** | **WAIT POST-EARNINGS / HOLD** |
| **`XOM` / `CVX`** | 25 | 27 | 15 *(Sát Target)* | 11 *(RSI ~73.0)* | **67.0% / 71.2%** | XOM Mua ròng / CVX Bán ròng | ⚠️ `IMMINENT EARNINGS (0d)` | **78 / 100** | **WAIT POST-EARNINGS & MA20 DIP** |
| **`GOOGL`** | 15 | 27 *(OCF $179.55B)* | 22 *(Fwd P/E 18.42x)* | 10 *(Dưới MA200)* | **80.76%** | Neutral / Routine | `JUST REPORTED (2d ago)` | **74 / 100** | **WATCH FOR REBOUND SIGNAL** |
| **`TSLA` / `COIN` / `QCOM` / `SMCI`** | 12 | 12 | 10 | 8 *(Gãy xu hướng)* | **43.7% – 83.4%** | Phân hóa | `SMCI (4d), QCOM (5d)` | **42 / 100** | **AVOID (Đứng ngoài hoàn toàn)** |

> **Quy tắc Kỷ luật Sự kiện BCTC (`Earnings Radar Rule`)**: Với các mã có cảnh báo **`IMMINENT EARNINGS (<= 7d)`** như `AAPL` (3 ngày — `2026-11-02`), `AMD` (4 ngày), `PLTR` (3 ngày), `XOM` (0 ngày), `CVX` (0 ngày), Hội đồng **nghiêm cấm giải ngân mới tối đa tỷ trọng ngay trước giờ công bố BCTC** để triệt tiêu rủi ro nhảy gap qua đêm. Chỉ giải ngân sau khi BCTC đã công bố hoặc giữ vị thế có sẵn với đệm lãi an toàn.

---

## 3. Kế Hoạch Giải Ngân Chuẩn Hóa `ATR Risk-Parity` & Ngưỡng Cắt Lỗ `2xATR(14)`

| Mã (Ticker) | Giá Hiện Tại | Vùng Mua Khuyến Nghị (Entry Zone) | Chốt Lời 1 (TP1) | Chốt Lời 2 (TP2 — Consensus) | Cắt Lỗ Định Lượng (`Stop 2xATR`) | Tỷ Trọng `ATR Risk-Parity` | Tổn Thất NAV Tối Đa Nếu Chạm Stop |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`BRK-B`** | $546.01 | **$535.00 – $546.00** *(Trụ cột biến động thấp)* | $575.00 | $605.00 | **$531.47** *(-2.66%)* | **9.2% NAV** | **`-0.24% NAV`** |
| **`AAPL`** | $346.38 | *Chờ sau BCTC ngày 02/11* (**$333.00 – $342.00**) | $370.00 | $405.00 *(High)* | **$334.38** *(-3.46%)* | **7.1% NAV** | **`-0.25% NAV`** |
| **`V`** | $416.16 | **$402.00 – $414.00** *(Chờ nhúng nhẹ)* | $441.09 | $460.00 | **$401.30** *(-3.58%)* | **6.8% NAV** | **`-0.24% NAV`** |
| **`MSFT`** | $520.94 | **$512.00 – $521.50** *(Vùng MA50)* | $565.00 | $627.73 | **$497.46** *(-4.50%)* | **6.6% NAV** | **`-0.30% NAV`** |
| **`JPM`** | $337.73 | **$332.00 – $338.50** *(Vùng MA20)* | $366.50 | $373.26 | **$324.05** *(-4.04%)* | **6.2% NAV** | **`-0.25% NAV`** |
| **`OXY`** | $63.91 | **$61.50 – $64.00** *(Trên MA50)* | $68.50 | $70.74 | **$60.93** *(-4.66%)* | **5.6% NAV** | **`-0.26% NAV`** |
| **`PG`** | $163.21 | **$158.00 – $163.50** | $173.65 | $182.00 | **$156.36** *(-4.20%)* | **5.5% NAV** | **`-0.23% NAV`** |
| **`NVDA`** | $203.46 | **$198.00 – $204.50** *(Vùng MA200)* | $230.00 | $265.00 | **$190.69** *(-6.28%)* | **4.5% NAV** | **`-0.28% NAV`** |
| **`JNJ`** | $276.18 | **$268.00 – $276.50** | $292.00 | $305.00 | **$260.97** *(-5.50%)* | **4.4% NAV** | **`-0.24% NAV`** |
| **`TSM`** | $404.71 | **$398.00 – $405.00** *(Vùng MA200)* | $455.00 | $520.00 | **$376.43** *(-6.98%)* | **4.1% NAV** | **`-0.29% NAV`** |

> **Kiểm soát Tương quan Cụm Bán dẫn (`Cluster Risk Control`)**: Ma trận tương quan 1 năm phát hiện cặp **`TSM - NVDA`** có hệ số tương quan **`r = 0.67`**. Nhờ mô hình `ATR Risk-Parity`, tổng tỷ trọng của `NVDA` (`4.5% NAV`) + `TSM` (`4.1% NAV`) được khóa ở mức **`8.6% NAV`** (nằm sâu dưới ngưỡng trần an toàn 12–14% NAV của Hội đồng).
