# BẢN TIN HUẤN LUYỆN ĐẦU TƯ THỰC CHIẾN BUỔI SÁNG (MORNING MENTOR BRIEFING v5.0)
## Ngày Huấn Luyện: 2026-11-10 | Huấn Luyện Viên: `investor-mentorship-coach` (Ban 6)
### Chương trình: 4 Tiếng/Ngày • Mô hình Core & Satellite • Thực hành Paper Trading & VN Localization

> *"Chào buổi sáng! Toàn bộ số liệu trong Bản tin Huấn luyện hôm nay đã được đồng bộ hóa 100% với Snapshot Kiểm toán v5.0 (Zero-Defect). Hôm nay chúng ta sẽ đi sâu vào thước đo tạo giá trị thực `EVA Spread (ROIC - WACC)`, `True FCF ex-SBC` và công cụ tính khối lượng đi lệnh theo USD & VND."*

---

### PHẦN 1: BÀI HỌC VI MÔ CỦA NGÀY (DAILY MICRO-LESSON — 3 PHÚT)
- **Chủ đề**: **Chiến Thuật Chia Lệnh 60/40 & Lọc Siêu Cổ Phiếu Tạo Giá Trị Thực (EVA Spread > 0) Khi VIX = 19.92 (< 20)**
- **Bản chất chiến lược**: Khi VIX hạ nhiệt xuống dưới 20 (19.92), Ban 5 đã cân bằng trọng số chấm điểm chuẩn 100% (Vĩ mô 25% / BCTC-FCF 30% / Định giá 25% / Kỹ thuật 20%). Danh mục Core (65%) tập trung tích sản các doanh nghiệp có ROIC > WACC (EVA dương) và Piotroski F-Score >= 7/9; trong khi phần Satellite (35%) tận dụng quy tắc chia lệnh 60/40 (40% đặt Limit tại Giá - 0.35xATR) để tối ưu giá vốn.
- **Công thức / Quy tắc vàng**:
  > Quy tắc Phân Bổ Vốn Quỹ & Thuế Cổ Tức VN: (1) Không giải ngân mới vào mã có lịch BCTC <= 7 ngày; (2) Tính cổ tức thực nhận sau thuế khấu trừ tại nguồn 30% của Mỹ (WHT); (3) Luôn kiểm tra cả Stop 2xATR ban đầu và Chandelier Trailing Stop (Highest_22d - 2.5xATR).
- **Thực tế thị trường hôm nay (2026-11-10)**: 
  - VIX hiện tại: **19.92** *(Dưới ngưỡng 20)* | Lợi suất US10Y: **4.86%** | Dầu WTI: **$86.21**.
  - Độ rộng thị trường (`Market Breadth`): **57.1%** cổ phiếu giữ trên MA200.

---

### PHẦN 2: BÓC TÁCH CA THỰC CHIẾN HÔM NAY (LIVE CASE STUDY: `MSFT`)
- **Mã cổ phiếu mổ xẻ**: **`MSFT`** (Giá khớp thực tế: **$545.18**).
- **Phân loại chiến lược**: Trụ cột **Danh Mục Core (`8.0% NAV`)** — Đã qua kỳ BCTC an toàn.
- **Góc nhìn Quỹ Đầu Tư (Số liệu Kiểm toán v5.0)**:
  1. **Nội tại doanh nghiệp & Dòng tiền thực (Ban 2)**:
     - Forward P/E: **`22.53x`** | Dòng tiền tự do GAAP FCF: **`+$2.99B USD`** | Dòng tiền thực sau trừ thưởng cổ phiếu (`True FCF ex-SBC`): **`+$-4.63B USD`**.
     - Hiệu suất sinh lời trên vốn đầu tư (`ROIC`): **`23.81%`** vs Chi phí vốn (`WACC`): **`9.2%`** -> Tạo giá trị kinh tế ròng **`EVA Spread = +14.61%`**.
     - Điểm sức khỏe tài chính **`Piotroski F-Score = 9/9`** | Tỷ suất cổ tức chuẩn hóa: **`0.68%`** *(Thực nhận sau thuế Mỹ 30% WHT cho NĐT Việt Nam: **`0.48%`**)*.
  2. **Định lượng & Quản trị rủi ro 2 Tầng (Ban 4)**:
     - Biến động `ATR(14)` = **$15.88**.
     - **Tầng 1 — Cắt lỗ bảo vệ vốn ban đầu (`Stop 2xATR`)**: **$513.43** (`-4.28%`).
     - **Tầng 2 — Chặn lãi động theo xu hướng (`Chandelier Trailing Stop 22d - 2.5xATR`)**: **$519.46**.
- **Bài tập Paper Trading hôm nay**:
  - Chạy lệnh mô phỏng: `python scripts/paper_trading_simulator.py buy --symbol MSFT --shares 10 --type Core`.

---

### PHẦN 3: CHUYÊN ĐỀ ĐẶC BIỆT CHO NHÀ ĐẦU TƯ VIỆT NAM (`VN LOCALIZATION LAYER`)
1. **Thuế Khấu Trừ Cổ Tức Mỹ (`US Withholding Tax 30%`)**:
   - Cổ tức tiền mặt từ cổ phiếu Mỹ bị khấu trừ tự động `30%` tại nguồn (`Net Yield = Gross Yield × 0.70`). Do đó, lợi nhuận chính của nhà đầu tư Việt Nam trên thị trường Mỹ đến từ **Tăng trưởng thị giá & Mua lại cổ phiếu quỹ (`Share Buybacks`)** thay vì săn cổ tức thuần túy.
2. **Chuyển Đổi Mô Hình `ATR Risk-Parity` Sang Chứng Khoán Việt Nam (`HOSE T+2.5`)**:
   - Trên sàn HOSE (biên độ `±7%/ngày` và chu kỳ thanh toán `T+2.5` chiều ngày T+2 cổ phiếu mới về tài khoản), cổ phiếu có thể bị khóa thanh khoản 2 phiên nếu gặp rủi ro hệ thống.
   - **Quy tắc hiệu chỉnh**: Khi áp dụng hệ thống 7 Phòng ban cho cổ phiếu VN30/HOSE, nới khoảng cách cắt lỗ định lượng từ `2.0x ATR(14)` lên **`2.5x ATR(14)`** và hạ rủi ro tối đa mỗi lệnh từ `0.35% NAV` xuống **`0.25% NAV`**.

---

### PHẦN 4: THỬ THÁCH TƯ DUY SOCRATIC TRONG NGÀY (SOCRATIC CHALLENGE)
> *Tại sao Ban 4 và Ban 7 (Alex) hôm nay lại kiên quyết loại `AAPL` (còn 2 ngày ra BCTC) và `BRK-B` (còn 7 ngày ra BCTC) ra khỏi danh mục giải ngân mới để đưa vào `Locked Earnings Watchlist`, mặc dù cả hai đều là những tập đoàn vĩ đại?*
