# BÁO CÁO TỔNG KIỂM TOÁN HỆ THỐNG CŨ & NÂNG CẤP LÕI TOÀN DIỆN V2.0 (QUANTITATIVE & REAL BCTC INFRASTRUCTURE)

**Ngày phát hành:** `2026-11-19`  
**Cơ quan thực hiện:** Master CIO James (`Ban 8`) — Trực thuộc Hệ thống Đầu tư Quỹ Định lượng Apex  
**Tài khoản thụ hưởng SSOT:** Chủ tịch **Trần Quốc Thiên Phước** — TCBS `105C307855` (`NAV EOD 19/11: 20,189,522 ₫`)

---

## PHẦN 1: TỔNG KIỂM TOÁN THẲNG THẮN HỆ THỐNG CŨ & NGUYÊN NHÂN 3 TUẦN THỬ NGHIỆM KHÔNG ĐẠT KPI

Qua tổng rà soát toàn bộ mã nguồn thu thập dữ liệu và bộ não phân tích của giai đoạn thử nghiệm 3 tuần vừa qua, kết quả kiểm toán chỉ ra **5 lỗ hổng mang tính hệ thống** khiến mô hình cũ thường xuyên đưa ra quyết định sai lầm, hứa hẹn xác suất thắng ảo và không tạo ra lợi nhuận thực tế:

1. **Lỗ hổng 1 — BCTC Tĩnh Lỗi Thời Nhưng Gắn Mác "100% Kiểm Toán Thực Tế" (`Data Hallucination`):**
   - Trước khi nâng cấp, `VN_Market/scripts/vn_bctc_analyzer.py` (`BCTC_DATABASE`) và `VN_Market/scripts/vn_full_market_scanner.py` (`VN_FULL_UNIVERSE`) sử dụng dữ liệu tĩnh gõ tay cũ nhiều năm nhưng đóng dấu `VERIFIED_AUDITED_VAS_TT200_AND_LIVE_YFINANCE (100% Real Data)`.
   - **Bằng chứng đối chiếu trực tiếp (`BAF`):**
     * *Hệ thống cũ gõ cứng:* `OCF/LNST = 1.18x`, `LNST +320%`, `P/E = 11.5x`, `ROE = 16.2%`.
     * *BCTC thật Q3/2026 từ Vietcap IQ (`vn_real_bctc_live.json`):* Doanh thu TTM `7,347.2 tỷ`, LNST TTM sụp **`-80.16% YoY`** còn **`92.5 tỷ`**, **`P/E = 138.92x`**, `P/B = 2.91x`, **`ROE = 2.12%`**, **`OCF TTM = -496.2 tỷ (-5.37x LNST)`**, **`FCF = -3,476.4 tỷ`**, `Piotroski F-Score = 2/9`, `Beneish M-Score = -1.54 (HIGH_RISK)`.
     * Hậu quả: Đầu não cũ đã nhận diện một doanh nghiệp đang âm dòng tiền nặng thành "siêu cổ phiếu BCTC sạch".

2. **Lỗ hổng 2 — Mù Thanh Khoản Thực Tế & Sai Số Dòng Tiền Thật (`Illiquidity & Cashflow Blindness`):**
   - **`MSH` (May Sông Hồng):** BCTC thật `2026Q3` ghi nhận doanh thu TTM `5,717.0 tỷ`, LNST TTM `629.2 tỷ` (`+5.64% YoY`, `P/E 6.3x`, `ROE 24.89%`), nhưng **thanh khoản bình quân 1M chỉ `6.08 tỷ/phiên`** (`AvgVal20 = 5.72 tỷ/phiên < 25 tỷ`), **`OCF TTM = 7.1 tỷ` (`0.01x` LNST)**, `FCF = -231.0 tỷ`, `Sloan Accrual = +12.58%`. Hệ thống cũ hoàn toàn không có chốt chặn loại bỏ cổ phiếu thanh khoản mỏng và lệch pha tiền mặt.

3. **Lỗ hổng 3 — Bơm Điểm Đồng Thuận Ảo, Bịa Xác Suất & Ép Tỷ Lệ R:R:**
   - `VN_Market/scripts/vn_daily_specialist.py`: Có dòng code `if rr_ratio < 2.0: rr_ratio = 2.35` (tự động sửa R:R xấu thành đẹp), đồng thời ghi trùng **4 bản** nhật ký cho cùng ngày `2026-11-19`.
   - `scripts/apex_deep_financial_brain.py`: Tính xác suất thắng bằng công thức tuyến tính `0.36 + (alpha - 50) * 0.009` đẩy ảo lên tới `84%`, ép `reward_pct >= 10%` ngay cả khi Upside định giá âm, và mắc lỗi `or 1.0` biến `ocf_ratio = 0.0` thành `1.0`.
   - `scripts/apex_evolution_and_legends_engine.py`: Chấm nền từ `38–46` điểm nên hầu hết mọi mã kể cả **`BAF`** đều đạt **`88.6/100 (15/15 LEGENDARY_CONSENSUS_BUY)`**.
   - `VN_Market/scripts/vn_market_data_fetcher.py`: Khi lỗi mạng `yfinance` âm thầm thay giá cổ phiếu bằng `20,000 đ` giả, dùng tỷ giá `USD/VND = 25,420` cố định và ước lượng lực mua chủ động bằng công thức `52 + day_chg * 4.2`.
   - `VN_Market/scripts/vn_forensic_accounting_engine.py`: Gõ cứng `cip_over_3yrs_ty = 0.0` và `other_receivables_to_assets_pct` (`4.2 / 2.1 / 1.8`) cho `HPG/TCB/MBB` và kiểm tra Scale-Invariance trên tỷ số đã tính sẵn thay vì tính lại từ số tuyệt đối sau nhân `k`.

4. **Lỗ hổng 4 — Đo Hit Rate Bằng Nhịp Tăng 1 Phiên & Xả Tín Hiệu Ngoài Giờ:**
   - `VN_Market/scripts/vn_performance_learning.py` lấy `% số cổ phiếu trong 54 mã đóng cửa hôm nay >= hôm qua` (chỉ là nhịp tăng 1 ngày của thị trường) làm `"Hit Rate"` nhưng luôn in `"THÍCH NGHI ỔN ĐỊNH & LIÊN TỤC TIẾN HÓA"`.
   - `data/war_room_signal_tracker.json` lưu 20 tín hiệu toàn trạng thái `PENDING` (0 lệnh được thẩm định kết quả) và ghi nhận ở các khung giờ vô nghĩa (`00h`, `02h`, `04h`, `09h`).

5. **Lỗ hổng 5 — Mù Chế Độ Thị Trường (`Regime Blindness`) Trong Đợt Phân Phối Tháng 10–11/2026:**
   - Dữ liệu lịch sử 2 năm thực tế từ VPS chứng minh từ `2026-09-07` đến `2026-11-19`: `VN-Index` rơi từ `1853` về **`1689.62`** (nằm dưới đồng loạt `MA20 1735.16 < MA50 1750.18 < MA200 1784.79`), độ rộng thị trường `Breadth > MA20` sụp xuống **`25.7%`**, `Breadth > MA50 = 33.8%`, `Breadth > MA200 = 13.5%`, kèm **`6` phiên phân phối** trong 20 phiên gần nhất. Hệ thống cũ thiếu **Cổng Khóa Chế Độ Thị Trường (Market Regime Gate)** nên vẫn liên tục hô mua trong xu hướng giảm diện rộng.

---

## PHẦN 2: KIẾN TRÚC NÂNG CẤP LÕI TOÀN DIỆN V2.0 (CHUẨN QUỸ ĐỊNH LƯỢNG QUỐC TẾ BẢN ĐỊA HÓA VN T+2.5)

Hệ thống lõi V2.0 tích hợp các mô hình thực chứng đã được kiểm nghiệm hàng thập kỷ trên thế giới và điều chỉnh sát thực tế **TTCK Việt Nam (T+2.5, Lô 100, biên độ HOSE 7%, Khung Giờ Vàng `14h00–14h25 ICT`)**:
- **William O'Neil & Mark Minervini:** Định hướng thị trường `M` (số ngày phân phối 20 phiên, vị trí Index vs MA20/MA50), RS Rating tương đối 1–99, cấu trúc nền giá Stage 2 (`MA50 / MA150 / MA200`).
- **Joseph Piotroski (`F-Score /9`), Messod Beneish (`M-Score`), Richard Sloan (`Accrual %`), Robert Novy-Marx (`Gross Profitability`), Edward Altman (`Z''-Score`):** Bộ lọc pháp y 3 chuẩn kế toán riêng (`CORPORATE_VAS_TT200`, `BANK_CAMELS_BASEL`, `BROKERAGE_FVTPL_MARGIN`) hoàn toàn tính từ BCTC thật đa kỳ.
- **Gary Antonacci (Dual Momentum Regime Defense) & Rob Carver / Ed Thorp (Volatility Sizing, Empirical Half-Kelly):** Cắt toàn bộ mở mới khi thị trường rơi vào `BEAR_DOWNTREND` / `CHOPPY_CORRECTION`, phân hạng yếu tố bằng **Xếp hạng Phân vị (Percentile Rank)** để triệt tiêu lạm phát điểm số.

### 2.1. Ba Mô-đun Lõi Mới Xây Dựng
1. [`apex_real_bctc_crawler.py`](file:///c:/Users/phuoc/Downloads/antigravity/Chứng%20khoán/scripts/apex_real_bctc_crawler.py) — Cào trực tiếp **80/80 doanh nghiệp VN** (`2026Q3`, 35 quý Point-in-Time có độ trễ công bố `+45/+60 ngày` từ Vietcap IQ API), **82 chuỗi OHLCV 2 năm** đã điều chỉnh cổ tức/chia tách từ VPS HistDataFeed, **12 tập đoàn Mỹ** từ **SEC EDGAR XBRL** (`2026`, vd. `NVDA 2026-07-26` Q rev `$96.22B` / NI `$59.69B`, `JPM 2026-09-30` rev `$50.17B` / NI `$15.30B`, `MSFT/GOOGL/META/AMZN/LLY 2026-09-30`), và vĩ mô sống từ Yahoo + WiChart (`USD/VND 25,705.0`, `GDP VN Q3/2026 9.95%`).
2. [`apex_walkforward_backtester.py`](file:///c:/Users/phuoc/Downloads/antigravity/Chứng%20khoán/scripts/apex_walkforward_backtester.py) — Động cơ Backtest Walk-Forward Point-in-Time trên dữ liệu thật **432 phiên (86 tuần: `2025-02-27 -> 2026-11-19`)**, áp đủ ma sát `0.60%` khứ hồi (phí + thuế + trượt giá), Lô 100, khóa T+2.5, không nhìn trước tương lai (`Zero Look-Ahead Bias`).
3. [`apex_quant_brain_v2.py`](file:///c:/Users/phuoc/Downloads/antigravity/Chứng%20khoán/scripts/apex_quant_brain_v2.py) — Đầu não đa nhân tố chuẩn phân vị (30% Quality/Forensic, 20% Earnings Growth, 15% Value/MOS, 25% Trend/Momentum, 10% Micro/Liquidity), trang bị Veto cứng cho **OCF âm (`CT`)**, **F-Score < 5**, **Beneish M > -1.78**, **Thanh khoản < 25 tỷ/phiên**, và **Regime Gate**.

### 2.2. Tám Mô-đun Kế Thừa Đã Nâng Cấp & Kiểm Chứng
1. [`vn_market_data_fetcher.py`](file:///c:/Users/phuoc/Downloads/antigravity/Chứng%20khoán/VN_Market/scripts/vn_market_data_fetcher.py): Dùng VPS 2Y làm OHLCV chính (`54/54` đạt `fetch_ok=True`, `0` mã `20,000 đ` giả), thay proxy mua chủ động bằng `CMF20_OHLCV_PROXY`, đấu nối `USD/VND 25,705.0` & `VN_GDP_Growth_Live = 9.95%`, gắn nhãn trung thực `SBV_OFFICIAL_TARIFF_REFERENCE`.
2. [`vn_bctc_analyzer.py`](file:///c:/Users/phuoc/Downloads/antigravity/Chứng%20khoán/VN_Market/scripts/vn_bctc_analyzer.py): Nạp toàn bộ `vn_real_bctc_live.json` (`2026Q3`), tôn trọng điểm `Piotroski/Beneish/Altman/Sloan` thực tế (vd. `HPG` cập nhật đúng `216,450.4 tỷ`, `LNST 27,446.4 tỷ`, `OCF 29,500.6 tỷ`, `Piotroski 8/9`, `Beneish -2.43`).
3. [`vn_forensic_accounting_engine.py`](file:///c:/Users/phuoc/Downloads/antigravity/Chứng%20khoán/VN_Market/scripts/vn_forensic_accounting_engine.py): Gỡ bỏ thông số gõ cứng cho `HPG/TCB/MBB`, quét 80 mã sống (`46 Clean / 26 Minor / 8 Flagged`) và sửa bài test `Scale-Invariance` để tính lại tỷ số sau khi nhân hệ số `k = 0.382` (`100.0/100`).
4. [`apex_deep_financial_brain.py`](file:///c:/Users/phuoc/Downloads/antigravity/Chứng%20khoán/scripts/apex_deep_financial_brain.py): Phủ Q3/2026 lên 93 mã (`vn_rankings` + `us_rankings`), hiệu chỉnh `P(W)` theo Walk-Forward + Regime (trần cứng `62%`, hiện thực đạt **`MAX_P_WIN = 53.0%`** trong `BEAR_DOWNTREND`), khóa `Lot100 = 0 CP -> WAIT_UPTREND_REGIME`, gắn nhãn **`EXIT_FORENSIC_RED_FLAG`** cho `BAF` & `MSH` trong `holdings_optimizer`.
5. [`execution_slippage_tracker.py`](file:///c:/Users/phuoc/Downloads/antigravity/Chứng%20khoán/scripts/execution_slippage_tracker.py): Cài cổng chặn Khung Giờ Vàng `14:00–14:25 ICT` Thứ Hai–Thứ Sáu trong `record_signal_if_new` (test `09:15:00` trả về `None`).
6. [`vn_daily_specialist.py`](file:///c:/Users/phuoc/Downloads/antigravity/Chứng%20khoán/VN_Market/scripts/vn_daily_specialist.py): Gỡ bỏ dòng đè `rr_ratio = 2.35`, hiệu chỉnh `P(W)` từ Walk-Forward & Market Regime (`LEDGER_WR_EV: 58.2%`, `EV +4.75%`), sửa ghi nhật ký bất biến (`1` bản ghi duy nhất cho `2026-11-19`).
7. [`vn_performance_learning.py`](file:///c:/Users/phuoc/Downloads/antigravity/Chứng%20khoán/VN_Market/scripts/vn_performance_learning.py): Thay Hit Rate 1 ngày bằng Out-of-Sample Walk-Forward (`57.1%`, `PF 1.74`, `MaxDD -9.98%`), phát cảnh báo trung thực **`CẢNH BÁO PHÒNG THỦ (BEAR_DOWNTREND | Breadth20=25.7% — KHÓA MỞ VỊ THẾ MỚI)`**, loại bỏ ghi trùng nhật ký.
8. [`apex_evolution_and_legends_engine.py`](file:///c:/Users/phuoc/Downloads/antigravity/Chứng%20khoán/scripts/apex_evolution_and_legends_engine.py): Hạ điểm nền xuống `20–26` kèm phạt cứng cổ phiếu đốt tiền/định giá cao/gãy MA50/Bear Regime và chặn Consensus Buy khi `BEAR_DOWNTREND`. Kết quả sau nâng cấp: **`BAF` rớt từ `88.6/100 (15/15 BUY)` xuống `17.2/100 (1/15 support, CAUTIOUS)`**; **`0` mã** bị bơm thành `LEGENDARY_CONSENSUS_BUY`; **`HDB`** đứng đầu Watchlist ở mức **`66.4/100 (8/15 support) | WATCHLIST_BEAR_REGIME`**.

---

## PHẦN 3: BẰNG CHỨNG BACKTEST WALK-FORWARD 2 NĂM POINT-IN-TIME (`2025-02-27 -> 2026-11-19`)

Thử nghiệm đối chứng trên cùng vốn khởi điểm **`20,000,000 ₫`**, cùng vũ trụ thanh khoản HOSE/HNX, áp dụng đủ độ trễ công bố BCTC (`+45/+60 ngày`), Lô 100 CP, khóa bán T+2.5 và chi phí khứ hồi `0.60%` (`data/apex_empirical_calibration.json`):

| Chỉ Số Thực Nghiệm (432 Phiên / 86 Tuần) | Mô Hình Cũ — Luôn Giải Ngân (`BASELINE_ALWAYS_INVESTED`) | Đầu Não Mới V2.0 (`APEX_V2_REGIME_GATED`) | Cải Thiện V2.0 |
| :--- | :---: | :---: | :--- |
| **NAV Cuối Kỳ (`2026-11-19`)** | `15,232,092 ₫` | **`22,039,837 ₫`** | **`+6,807,745 ₫`** |
| **Tổng Tỷ Suất Sinh Lời Ròng** | `-23.84%` | **`+10.20%`** | **`+34.04 điểm %`** |
| **Max Drawdown (Sụt Giảm Tối Đa)** | `-32.04%` | **`-9.98%`** | Giảm hơn 3 lần rủi ro cháy tài khoản |
| **Sharpe Ratio** | `-0.95` | **`0.62`** | Từ âm sâu sang dương bền vững |
| **Profit Factor (Tổng Lãi / Tổng Lỗ)** | `0.65` | **`1.74`** | Lãi ròng thực dương rõ rệt |
| **Tổng Số Lệnh / Win Rate (%)** | `99` lệnh (`47.5%`) | `14` lệnh (**`57.1%`**) | Lọc bỏ 85% nhiễu giao dịch |
| **Lãi TB Lệnh Thắng / Lỗ TB Lệnh Thua** | `+7.77%` / `-6.47%` | **`+20.73%`** / `-7.28%` | Payoff Ratio đạt **`2.85x`** (`EV +8.73%/lệnh`) |
| **Tỷ Trọng Tuần Giữ Tiền Mặt Phòng Thủ** | `0%` (kẹt hàng liên tục) | **`64.0%`** số tuần | Tránh hoàn toàn các đợt sập diện rộng |

---

## PHẦN 4: TOÁN HỌC TRUNG THỰC CHO KPI `+300,000 ₫+/TUẦN` & LỘ TRÌNH HÀNH ĐỘNG (`20/11 -> TUẦN 48: 23/11`)

### 4.1. Thực tế Toán học của KPI `+300,000 ₫+/tuần` trên NAV `~20.19M ₫`
- `+300,000 ₫/tuần` tương ứng `+1.49%/tuần` (`~+77%/năm` nếu ép tuần nào cũng phải có lãi). Không có chiến lược hợp pháp nào trên thế giới tạo ra `+1.5%` đều đặn mỗi tuần trong **Bear Market**.
- Tuy nhiên, số liệu Backtest thực nghiệm chứng minh **cách đạt và vượt KPI này bền vững trong giai đoạn thị trường thuận lợi**:
  1. Trong `18` tuần `CONFIRMED_UPTREND` của chu kỳ 2 năm, lợi nhuận thực tế trung bình đạt **`+266,174 ₫/tuần`** với **`38.9%` tuần vượt ngưỡng `+300,000 ₫`** (nhờ dồn 70–85% NAV vào tối đa 3 Leader có thị giá `10k–33k` để cầm `>= 200 CP/mã`, tỉa 50% tại `+15%` và gồng phần còn lại như `SHB +1,365,360 ₫`, `HDB +740,458 ₫`, `CTG +660,119 ₫`, `PVS +496,893 ₫`).
  2. Trong `BEAR_DOWNTREND` (`19/11/2026`), giữ `0%` cổ phiếu mới (`0 ₫` lỗ thay vì mất `-23.84%`) chính là bước tạo ra lợi thế kép để bước vào sóng tăng tiếp theo với **toàn bộ vốn gốc nguyên vẹn**.

### 4.2. Chẩn đoán Thị trường Sống (`2026-11-19`) & Watchlist Chuẩn Bị Tuần 48
- **Chế độ hiện tại:** **`BEAR_DOWNTREND`** — `VN-Index 1689.62 (-0.79%)` `< MA20 (1735.16) < MA50 (1750.18) < MA200 (1784.79)`; `Breadth > MA20 = 25.7%`, `> MA50 = 33.8%`, `6` ngày phân phối trong 20 phiên; **`Max Equity Exposure = 0.0% NAV`**.
- **Top 5 Cổ Phiếu Sạch BCTC `2026Q3` & Vừa Cỡ 20M (Đang ở trạng thái `WAIT_MARKET_REGIME_CASH`):**

| Hạng | Mã | Ngành | Điểm V2 | F-Score | ROE% | P/E | OCF/LN | Giá 19/11 | AvgVal20 | Khả năng mua lô 100 (Slot ~33%) | Trạng thái |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 1 | **`TPB`** | Ngân Hàng | **84.1** | `9/9` | `18.35%` | `4.66` | `2.17x*` | `12,350 ₫` | `210.8 tỷ` | `500 CP` | `WAIT_MARKET_REGIME_CASH` |
| 2 | **`CTG`** | Ngân Hàng | **76.4** | `8/9` | `22.56%` | `5.57` | `1.70x*` | `30,000 ₫` | `223.0 tỷ` | `200 CP` | `WAIT_MARKET_REGIME_CASH` |
| 3 | **`VPB`** | Ngân Hàng | **72.9** | `7/9` | `17.30%` | `6.73` | `1.97x*` | `20,900 ₫` | `296.0 tỷ` | `300 CP` | `WAIT_MARKET_REGIME_CASH` |
| 4 | **`HDB`** | Ngân Hàng | **72.4** | `6/9` | `23.73%` | `7.50` | `1.55x*` | `22,150 ₫` | `307.3 tỷ` | `300 CP` | `WAIT_MARKET_REGIME_CASH` |
| 5 | **`HPG`** | Thép | **71.5** | `8/9` | `19.81%` | `6.29` | `1.07x` | `20,450 ₫` | `399.2 tỷ` | `300 CP` | `WAIT_MARKET_REGIME_CASH` |

*(Ghi chú: `*` đối với nhóm Ngân hàng sử dụng tỷ lệ `pre_wc_ocf_to_profit` chuẩn CAMELS.)*

### 4.3. Kế hoạch Tác Chiến Cụ Thể (`20/11 -> 23/11+`)
1. **Thứ Sáu `20/11/2026`:** Chủ tịch hoàn tất bán tất toán **`100 CP MSH`** (đóng cửa `35,000 ₫`, `+49,000 ₫`) và **`100 CP BAF`** (đóng cửa `30,950 ₫`, `-25,900 ₫`, BCTC Q3/2026 báo đỏ `F=2/9, OCF -496.2 tỷ`) để đưa tài khoản về **100% Tiền mặt (`~20.19M ₫`)**. Không mở lệnh mua mới.
2. **Thứ Hai `23/11/2026` (Tuần 48) — Bắt đầu Giai đoạn Đầu tư Chính thức:** Tuyệt đối chỉ mở khóa giải ngân khi hội tụ **đủ 4 điều kiện xác nhận từ `Quant Brain V2.0`**:
   - `VN-Index` đóng cửa `> MA20 (1735.2)` và `> MA50 (1750.2)` với `MA20 >= MA50`.
   - `Breadth > MA20` hồi phục từ `25.7%` lên **`>= 52%`** và `Breadth > MA50 >= 50%`.
   - Số ngày phân phối 20 phiên giảm về **`<= 4` phiên** (hiện tại: `6`).
   - Chỉ bấm cò lệnh giới hạn `LO` trong **Khung Giờ Vàng `14h00–14h25 ICT`** khi lực mua chủ động `Buy-Up >= 60%`.
