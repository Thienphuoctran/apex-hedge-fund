# KẾ HOẠCH TÁC CHIẾN TUẦN 48 (23–27/11/2026) — ĐẦU NÃO TỰ CHỦ BRAIN V3.0 & ĐÁNH CƯỢC BẤT ĐỐI XỨNG

> **CƠ QUAN BAN HÀNH:** Hội đồng Đầu tư 11 Đơn vị Độc lập & Master CIO James (Ban 8)  
> **KÍNH TRÌNH:** Chủ tịch **Trần Quốc Thiên Phước** (Tài khoản TCBS duy nhất: `105C307855`)  
> **CĂN CỨ DỮ LIỆU THỰC:** EOD Thứ Sáu `20/11/2026` + Quét Internet thực `506` tin / `13` RSS / `11` cổng IR / `20` Tavily / `6` SEC EDGAR + Backtest Walk-Forward 2 năm (`431` phiên)  
> **VỐN SẠCH THỰC TẾ (SSOT):** **`20,051,117 ₫`** (`100.0% Tiền mặt` — `0 cổ phiếu` đang giữ — Trạng thái `ALL_CASH_STANDDOWN`)

---

## 1. CHẨN ĐOÁN ĐỘC LẬP THỊ TRƯỜNG SAU PHIÊN THỨ SÁU (20/11/2026)

1. **Tất toán sạch Vòng 1 đúng kỷ luật:** Chiều Thứ Sáu `20/11`, Chủ tịch đã khớp bán hết `100 CP BAF @ 30,350 ₫` (`13:08`) và `100 CP MSH @ 34,300 ₫` (`13:12`), thu hồi đủ **`20,051,117 ₫`** tiền mặt sạch (`0% Margin`), bảo toàn hoàn toàn tài khoản trước kỳ nghỉ cuối tuần.
2. **Tín hiệu giá & cấu trúc thị trường sống (EOD `20/11/2026`):**
   - **VN-Index:** Đóng cửa **`1,688.79`** (`-0.05%` | Mở cửa `1,671.25` | Đáy phiên **`1,666.41`** -> Kéo rút chân đóng đúng đỉnh phiên: **`CloseInRange = 100.0%`**).
   - **Hệ thống Đường Trung Bình & Phân Phối:** Đứng dưới `MA20 (1,730.89)` (`-2.43%`), dưới `MA50 (1,748.05)` (`-3.39%`), dưới `MA200 (1,784.16)` (`-5.35%`), với `6` ngày phân phối trong 20 phiên gần nhất.
   - **Độ rộng (`Breadth`):** `> MA20 = 23.0%` | `> MA50 = 32.4%` | `> MA200 = 12.2%` | Mức rũ 5 phiên gần nhất `-4.94%`.
   - **Khối lượng (`Vol/Vol20`):** **`0.95x`** (tăng `+17%` so với phiên `19/11`, nhưng vẫn thiếu nhẹ so với ngưỡng xác nhận Spring `>= 1.05x`).
   - **Vĩ mô & Liên thị trường:** `VIX = 35.89`, `SP500 = 6,910.39` (`-3.70%`), `US10Y = 4.91%`, `DXY = 103.84`, `WTI = 83.41 USD`, `USD/VND = 25,705`, `GDP VN Q3/2026 = 9.95%`.
   - **Điểm Spring V3.0:** **`3/5`** (Đạt: Rũ 5 phiên `<= -2%`, Nến xanh, `CloseInRange >= 78%`; Chưa đạt: `Br20 = 23.0%` thiếu `1.0%` so với ngưỡng `24.0%`, `Vol = 0.95x` thiếu so với `1.05x`).
   - **KẾT LUẬN TRẠNG THÁI:** **`BEAR_WITH_SPRING_WATCH`** — Tuyệt đối **không mua sáng Thứ Hai**, nhưng **nạp sẵn đạn cho cú đánh úp bất đối xứng `30–40% NAV` chiều Thứ Hai (`14h05–14h25`)** nếu dòng tiền xác nhận rút chân thật.

---

## 2. KIỂM CHỨNG THỰC NGHIỆM 2 NĂM (CƠ SỞ KHOA HỌC CỦA SỰ MẠO HIỂM CÓ TÍNH TOÁN)

| Chiến Lược Backtest (2 Năm PIT: `03/03/2025 -> 20/11/2026`, `431` phiên, phí `0.60%`) | Lãi Ròng Thực | NAV Cuối (Từ `20.0M ₫`) | Max Drawdown | Sharpe | Profit Factor | Win Rate | Ý Nghĩa Điều Hành |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Baseline (Giữ hàng bừa / Nghe hô hào)** | `-22.08%` | `~15.58M ₫` | `-34.30%` | `-0.74` | `0.66` | `48.3%` | Đốt vốn vì gồng lỗ & bắt dao rơi |
| **V2.0 (Phòng thủ cứng chỉ đánh Uptrend)** | `+12.59%` | `22,518,054 ₫` | `-9.90%` | `0.71` | `2.11` | `57.1%` | Rất an toàn (`62.8%` tuần cầm tiền) nhưng dễ lỡ sóng hồi đầu |
| **V3.0 (V2 + Đánh Cược Spring Bất Đối Xứng)** | **`+13.00%`** | **`22,600,530 ₫`** | **`-9.90%`** | **`0.73`** | **`1.97`** | **`57.9%`** | **Payoff `3.04x`, EV `+7.36%/lệnh`, khóa MaxDD `-9.90%`** |

> [!IMPORTANT]
> Điểm mấu chốt của **Brain V3.0**: Kèo mạo hiểm chỉ được phép bấm cò khi đáp ứng bộ lọc thực nghiệm (`24% <= Br20 <= 45%`, `Vol >= 1.05x`, `CIR >= 78%`, mã dẫn đầu `F >= 6`, `RS >= 78`, Stop `-5.5%`, TP1 `+7.5%`, Time-stop `7` phiên). Nếu bắt đáy bừa khi `Br20 < 24%` hoặc hàng yếu thì kết quả backtest lỗ `-4.38%` đến `-10.61%`.

---

## 3. MA TRẬN 4 NHÁNH HÀNH ĐỘNG CHO THỨ HAI (23/11/2026) — KHUNG GIỜ VÀNG `14H05–14H25`

| Nhánh Kịch Bản | Điều Kiện Xác Nhận Trên Bảng Điện (Lúc `14h05–14h25` Thứ Hai `23/11`) | Tỷ Trọng Giải Ngân | Danh Sách Lệnh / Hành Động Cụ Thể | Ngưỡng Bảo Vệ & Mục Tiêu |
| :--- | :--- | :---: | :--- | :--- |
| **Nhánh S4: Bear Distribution Shield (Lá chắn Tiền mặt)** | `VN-Index < 1,666.41` (thủng đáy `20/11`) **HOẶC** `Buy-Up < 48%` **HOẶC** thanh khoản lịm với `Vol < 0.85x` | **`0.0% NAV`** | **ĐỨNG NGOÀI 100% TIỀN MẶT (`20,051,117 ₫`)**. Bảo toàn `0 ₫` thua lỗ nếu cú kéo cuối phiên Thứ Sáu chỉ là Bull-Trap. | Chờ đáy thật & không bắt dao rơi |
| **Nhánh S3: Asymmetric Spring Strike (Đánh Cược Bất Đối Xứng V3.0)** | `VN-Index >= 1,678` **VÀ** `Breadth > MA20 >= 24.0%` **VÀ** `Vol >= 1.05x MA20` **VÀ** `Buy-Up >= 58%` | **`30% – 40% NAV`** (`~7.3M – 8.0M ₫`) | Chọn tối đa **2 mã** từ rổ 3 Kèo Spring V3.0 (khóa rủi ro rổ `<= 2.0% NAV`): Ưu tiên **`TPB` (`300 CP @ 12,250 ₫`)** + **`HDB` (`200 CP @ 21,700 ₫`)** *(hoặc thay 1 mã bằng `CTG 100 @ 29,950 ₫` / `HPG 100 @ 19,900 ₫` để tránh tập trung 100% Ngân hàng)*. | Stop cứng `-5.5%` / TP1 `+9.0%` (chốt 50%) / TP2 `+18.0%` |
| **Nhánh S2: Sideways Rotation Sniper (Đi Ngang Phân Hóa)** | `VN-Index` giữ vững `1,685 – 1,730`, `Breadth > MA20` hồi phục lên `30.0% – 50.0%`, lực cầu ổn định | **`30% – 45% NAV`** (`~8.0M ₫`) | Bắn tỉa 2 mã giữ nền tốt trên `MA50`: `HDB (200 CP)` + `TPB (300 CP)` bằng lệnh `LO` khung `14h05–14h25`. | Chốt TP1 `+6.5%..+9.0%` (Scaling Out `50/50`), Stop `-5.5%` |
| **Nhánh S1: Bull Breakout Offense (Bùng Nổ Theo Đà Uptrend)** | `VN-Index` đóng cửa vượt `MA20 (1,730.9)` & hướng lên `MA50 (1,748.0)` + `Breadth > MA20 >= 50.0%` + `Buy-Up >= 60%` | **`75% – 85% NAV`** (`~15–17M ₫`) | Giải ngân chủ lực đa ngành: `TPB (500 CP)` + `HDB (200 CP)` + `HPG (300 CP)` (kèm `VPB / CTG` dự phòng). | Chốt 50% tại TP1 (`+15%`), nâng Stop hòa vốn gồng TP2 (`+24%..+28%`) |

---

## 4. CHI TIẾT RỔ 3 KÈO ĐÁNH CƯỢC BẤT ĐỐI XỨNG V3.0 (DUNG HỢP 6 TRỤ CỘT)

| Mã CP | Điểm V3 | BCTC Q3 (F) | Tin Internet (P) | Giá Đóng `20/11` | Lệnh Limit LO (`14h05–14h25`) | Khối Lượng Lô 100 | Quy Mô Vốn (`% NAV`) | Cắt Lỗ Stop (`-5.5%`) | Rủi Ro Tối Đa (`% NAV`) | TP1 (`+9%`) / TP2 (`+18%`) | R:R |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **TPB** | **`85.9`** | `9/9` | `97.5` (`+0.22`) | `12,350 ₫` | **`12,250 ₫`** | `300 CP` | `3,675,000 ₫` (`18.3%`) | `11,600 ₫` | `195,000 ₫` (`0.97%`) | `13,350 ₫` / `14,450 ₫` | `1:1.69 / 1:3.38` |
| **HDB** | **`75.1`** | `6/9` | `98.7` (`+0.25`) | `21,800 ₫` | **`21,700 ₫`** | `200 CP` | `4,340,000 ₫` (`21.6%`) | `20,500 ₫` | `240,000 ₫` (`1.20%`) | `23,650 ₫` / `25,600 ₫` | `1:1.62 / 1:3.25` |
| **CTG** | **`82.9`** | `8/9` | `94.9` (`+0.25`) | `30,100 ₫` | **`29,950 ₫`** | `100 CP` | `2,995,000 ₫` (`14.9%`) | `28,300 ₫` | `165,000 ₫` (`0.82%`) | `32,650 ₫` / `35,350 ₫` | `1:1.64 / 1:3.27` |

- **Mã Dự Phòng Đa Ngành:** **`HPG`** (Điểm V3 `78.1`, `F=8/9`, Tin Internet `100.0`, Giá `20/11` `20,450 ₫`, thanh khoản `402 tỷ/phiên`) và **`VPB`** (Điểm V3 `73.7`, `F=7/9`, Tin Internet `93.7`, Giá `20/11` `20,500 ₫`).
- **Quy tắc khóa rủi ro & chống trùng ngành từ Ban 4:** Khi kích hoạt Nhánh S3 (`30–40% NAV`), ưu tiên **tối đa 2 mã** để khóa rủi ro tổng rổ `<= 2.0% NAV`: ví dụ `TPB 300 CP` (`0.97%` rủi ro) + `CTG 100 CP` (`0.82%` rủi ro) = `6,670,000 ₫` (`33.3% NAV`, tổng lỗ tối đa `360,000 ₫ = 1.80% NAV`), hoặc `TPB 300 CP` + `HPG 100 CP` (`~5.7M ₫`) để phân tán rủi ro khỏi nhóm Ngân hàng; nếu chọn `TPB + HDB (200 CP)` thì hạ `TPB` xuống `200 CP` (`~6.79M ₫`) để tổng rủi ro rổ vẫn `<= 1.85% NAV`.

---

## 5. 4 PHẢN BIỆN ĐỘC LẬP CỦA ĐẦU NÃO V3.0 (CHẤT VẤN THẲNG TÍNH TRƯỚC KHI GIAO DỊCH)

1. **`CHAL_01_ANTI_PARALYSIS_INFLECTION` — Phản biện sự quá thận trọng (Chủ động đánh úp khi có điểm uốn):**  
   Nếu máy móc giữ `100%` tiền mặt suốt `62.8%` số tuần như V2, ta an toàn nhưng dễ bỏ lỡ sóng hồi đầu. Thứ Sáu `20/11`, VN-Index quét đáy `1,666.41` rồi kéo đóng đỉnh `1,688.79` (`CIR 100%`). Nếu chiều Thứ Hai `23/11` (`14h05–14h25`) VNI giữ `>= 1,678`, `Br20 >= 24%`, `Vol >= 1.05x`, `Buy-Up >= 58%`, James chủ động bấm cò `30–40% NAV` thay vì ngồi nhìn thụ động.
2. **`CHAL_02_VETO_TIKTOK_RECKLESS_BETS` — Phản biện tư duy bắt đáy mã đầu cơ rẻ thị giá (`VIX, CII, CEO, BAF`):**  
   Mạo hiểm có tính toán **KHÔNG** phải là nhắm mắt bắt đáy cổ phiếu yếu dòng tiền từ video TikTok. Backtest chứng minh bắt đáy dưới `Breadth < 24%` hoặc cổ phiếu lỗ/âm dòng tiền đốt `-4.38%` đến `-10.61%` tài khoản. **Lệnh cấm tuyệt đối:** Cấm mua `BAF`, `VIX`, `CII`, `CEO` hoặc bất kỳ mã nào `F-Score < 6` / `OCF` âm / gãy `MA200`.
3. **`CHAL_03_MORNING_TRAP_GUARDRAIL` — Phản biện tâm lý nôn nóng mua sáng Thứ Hai (`Anti-FOMO ATO / 10h00`):**  
   Cú rút chân Thứ Sáu thường tạo hưng phấn giả đầu sáng Thứ Hai, trong khi dư nợ Margin toàn sàn cuối Q3/2026 lên gần `460 nghìn tỷ đ` (lãi suất `13–16%`) có thể gây áp lực xả sáng sớm. **Khóa 100% nút Mua trước `14h00` Thứ Hai `23/11`**; chỉ bấm `LO` sau `14h05`.
4. **`CHAL_04_BEAR_CAPITAL_PRESERVATION` — Sẵn sàng đứng ngoài `0%` nếu rút chân Thứ Sáu chỉ là Bull-Trap:**  
   Vì `20/11` có `Vol/Vol20 = 0.95x` (chưa vượt `1.05x`) và VN-Index vẫn dưới `MA20`/`MA50`, nếu chiều Thứ Hai `23/11` thủng `1,666.41` hoặc `Buy-Up < 48%`, hệ thống tự động kích hoạt **Nhánh S4: Giữ nguyên `100% Tiền mặt` (`20,051,117 ₫`), `0 ₫` thua lỗ**.

---

## 6. LỊCH ĐIỀU HÀNH TUẦN 48 (23–27/11/2026)

- **Thứ Hai (`23/11`):** Chạy `scripts/run_master_unified_fund.py` trước giờ giao dịch; quan sát tĩnh suốt phiên sáng; chỉ kích hoạt nhánh **S1 / S2 / S3 / S4** lúc **`14h05–14h25`**.
- **Thứ Ba (`24/11`):** Tiền bán `MSH/BAF` (`6.46M ₫`) về tài khoản hợp nhất đủ `20.05M ₫`; điều hành vị thế theo đúng kịch bản đã kích hoạt.
- **Thứ Tư (`25/11`):** Kiểm tra trạng thái `T+2` của lô giải ngân Thứ Hai (nếu có); áp dụng Scaling Out `50%` tại TP1 và nâng Stop lên giá vốn.
- **Thứ Năm – Thứ Sáu (`26–27/11`):** Chốt sổ lãi thực tuần; giữ cổ phiếu `<= 45%–55% NAV` qua cuối tuần trừ khi S1 Uptrend bùng nổ rõ; Ban 5 & Ban 12 Trọng kiểm toán cuối tuần.
