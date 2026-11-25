# BÁO CÁO THẨM ĐỊNH HIỆU SUẤT & TỰ HỌC TIẾN HÓA TTCK VIỆT NAM — 2026-11-25
**Cơ quan thực hiện**: Ban 5 — Phòng Thẩm Định Hiệu Suất, Hồi Tố Lịch Sử & Tự Học Thích Nghi

---

## 🏛️ ĐỐI SOÁT TÀI KHOẢN THỰC CHIẾN CHỦ TỊCH TRẦN QUỐC THIÊN PHƯỚC (TCBS: 105C307855)
- **Tổng Giá Trị Tài Sản Ròng (NAV)**: **`20,051,117 VNĐ`**
- **Vốn Thực Khớp (300 CP)**: **`4,510,000 VNĐ`**
- **Giá Trị Thị Trường Sống**: **`4,510,000 VNĐ`**
- **Lợi Nhuận Tạm Tính (PnL Thực)**: **`<font color="#00C087">+0 VNĐ (+0.00%)</font>`** | **Lãi đã chốt**: **`+51,117 VNĐ`**
- **Tiền Mặt Dry Powder Bảo Toàn**: **`15,541,117 VNĐ`**
- **Account Hit Rate Thực Chiến**: **`50.0%`** (1/2 mã đang giữ lãi dương)

| Mã CK | Khối Lượng | Giá Vốn Thực Tế | Thị Giá Sống | Giá Trị Vốn | Giá Trị Thị Trường | Lãi/Lỗ Thực Tế | Ngưỡng Stop 2xATR | Trạng Thái Rủi Ro |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`TPB`** | **200 CP** | 12,300 ₫ | 12,350 ₫ | 2,460,000 ₫ | 2,470,000 ₫ | **+10,000 ₫ (+0.41%)** | 11,600 ₫ | 🟢 AN TOÀN |
| **`HPG`** | **100 CP** | 20,500 ₫ | 20,400 ₫ | 2,050,000 ₫ | 2,040,000 ₫ | **-10,000 ₫ (-0.49%)** | 19,300 ₫ | 🟢 AN TOÀN |

---

## 1. KẾT QUẢ ĐỐI SOÁT DỰ BÁO VS THỰC TẾ (WALK-FORWARD POST-MORTEM)
- **Out-of-Sample Walk-Forward Win Rate (2Y PIT Backtest)**: **57.1%** (`14` lệnh | Profit Factor: `1.74` | Return: `+10.20%` | MaxDD: `-9.98%`)
- **Độ rộng tăng giá 1 phiên gần nhất (`daily_market_advance_pct`)**: `100.0%`
- **Số lượng phiên lịch sử lưu trữ**: 22 phiên giao dịch.
- **Trạng thái mô hình**: **ĐẠT CHUẨN THỰC NGHIỆM (EMPIRICAL PF=1.74 >= 1.1 & SIDEWAY_CHOPPY)**

## 2. BÓC TÁCH NGUYÊN NHÂN HIỆU SUẤT (PERFORMANCE ATTRIBUTION)
1. **Đóng góp từ Chọn lọc Cổ phiếu BCTC Tốt (Alpha Selection)**: +65% tỷ trọng lợi nhuận (Các mã Dẫn dắt BCTC OCF >= 1.1x giữ sức chống chịu vượt trội).
2. **Đóng góp từ Sóng Ngành & Vĩ mô (Sector Tailwind)**: +25% (Hạ tầng đầu tư công, chu kỳ tín dụng nới lỏng, xuất khẩu dệt may).
3. **Đóng góp từ Quản trị Rủi ro T+2.5**: +10% (Tránh được các nhịp đua lệnh trần ATO bị kẹt hàng T+2.5).

## 3. CƠ CHẾ TỰ ĐỘNG TINH CHỈNH TRỌNG SỐ (ADAPTIVE TUNING)
- Đã đối soát và ghi nhận nhật ký vào `vn_system_evolution_journal.md`.
- Trọng số chấm điểm trong `adaptive_weights_vn.json` bảo đảm tổng = `1.00`.

## 4. KHO BỘ NHỚ SAI SỐ & HÀNH VI DÀI HẠN (`VN Mem0 Contextual Memory Vault`)
| Mã Bộ Nhớ | Phân Loại Ký Ức | Điều Kiện Kích Hoạt Ngữ Cảnh (`Regime Trigger`) | Mã Liên Quan | Bài Học Lịch Sử Đã Số Hóa | Quy Tắc Tự Động Nạp Cho Minh Quân |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **`MEM-VN-001`** | `ATO_BULL_TRAP_GUARD` | Mở cửa tạo Gap xanh > +2.5% phiên ATO nhưng thanh khoản phiên sáng thấp | **`HPG, MWG, SSI`** | Đua lệnh giá xanh phiên ATO (9h00-9h15) tại TTCK Việt Nam thường chịu thiệt giá vốn 1.5%-2.5% khi áp lực hàng T+2.5 về tài khoản lúc 13h30 chiều. | **Cấm mua đuổi ATO; bắt buộc đặt lệnh Limit LO chiết khấu -0.35x ATR(14) và chờ xác nhận lực hấp thụ trong Khung Giờ Vàng 14h00-14h25.** |
| **`MEM-VN-002`** | `OMISSION_ERROR_NO_SUPPLY` | Nến Test Cung (No-Supply) Vol cạn < 45% MA20 tại nền tích lũy Wyckoff + Tiền mặt ròng lớn | **`DGC, FPT`** | Chần chừ không giải ngân thăm dò khi siêu cổ phiếu BCTC hạng AAA xuất hiện nến Test Cung cạn Vol tại nền hỗ trợ sẽ bỏ lỡ nhịp bứt phá mạnh. | **Giải ngân ngay 30%-60% vị thế thăm dò tại nền No-Supply khi OCF/LNST >= 1.0x và Altman Z'' > 4.0.** |
| **`MEM-VN-003`** | `FORENSIC_DEBT_TRAP_VETO` | OCF âm liên tục + Đòn bẩy nợ D/E > 2.0x + Altman Z'' < 1.1 | **`FRT, VCG, NVL`** | Các nhịp kéo trần đầu cơ của cổ phiếu âm dòng tiền kinh doanh và nợ vay cao thường kết thúc bằng chuỗi giảm sàn mất thanh khoản. | **Khóa cứng trong danh sách Veto; đánh giá mọi nhịp tăng của nhóm này là Disciplined Pass (Bỏ qua có kỷ luật).** |
| **`MEM-VN-004`** | `INTRADAY_LIMIT_ORDER_CALIBRATION` | Dòng tiền lớn mua chủ động bứt phá cản (Breakout Volume > +40% MA20) | **`HPG, TCB, MBB`** | Đặt lệnh Limit LO quá sâu dưới chân hỗ trợ (lệch > 2% so với giá giao dịch thực tế) khi dòng tiền hấp thụ mạnh sẽ dẫn đến tình trạng sửa lệnh nhiều lần hoặc trượt mất hàng. | **Linh hoạt nâng giá đặt Limit LO lên sát bước giá khớp thực tế trong Khung Giờ Vàng 14h00-14h25 khi đã xác nhận lực hấp thụ của khối ngoại/tổ chức, khóa chặt mức trượt giá tối đa <= 0.5%.** |
| **`MEM-VN-005`** | `POSITION_SIZING_AND_CASH_PRESERVATION` | Tác chiến danh mục tài khoản thực tế chuẩn lô chẵn 100 CP | **`HPG, MBB, TCB`** | Giải ngân 100% tiền mặt mà không giữ lại lượng tiền dự phòng sẽ làm giảm tính cơ động khi thị trường xuất hiện nhịp điều chỉnh bất ngờ ở phiên kế tiếp. | **Luôn bảo đảm tỷ lệ phân bổ lô chẵn 100 CP chuẩn xác và giữ tỷ lệ tiền mặt dự phòng (Dry Powder >= 7% NAV), tuyệt đối không dùng margin để triệt tiêu mọi rủi ro tài khoản.** |
| **`MEM-EVO-VN-001`** | `SELF_REFLECTION_AUTOPSY` | Đánh giá tự động ngày 2026-11-21 | Cash 20,051,117₫ | Lỗi thực thi=1 | **`HDB, MSH, BAF`** | Các lệnh lướt ngắn thiếu biên EV >= +5% không tạo giá trị ròng; cơ hội EV >= +15% phải chờ khung 14h00-14h25 mới bấm LO lô chẵn 100 CP. | **Chỉ mở vị thế mới khi Alpha Score >= 73, EV >= +12%, R:R >= 1:2.5 và thanh khoản mua chủ động >= 58%.** |

## 5. CHỈ SỐ TRƯỞNG THÀNH PILLAR 3 & ĐỒNG THUẬN 15 HUYỀN THOẠI ĐẦU TƯ
- **System Maturity Score**: **`78.4/100`** | **Collective IQ**: **`156.4`** | **Brier Score**: `0.1233`
- **`HDB`**: Đồng thuận **70.4/100** (10/15 Huyền thoại ủng hộ) — `ACCUMULATE`
- **`TCB`**: Đồng thuận **56.6/100** (6/15 Huyền thoại ủng hộ) — `WATCHLIST`
- **`VCB`**: Đồng thuận **54.3/100** (7/15 Huyền thoại ủng hộ) — `WATCHLIST`
- **`MSFT`**: Đồng thuận **51.8/100** (6/15 Huyền thoại ủng hộ) — `CAUTIOUS`
- **`MSH`**: Đồng thuận **49.4/100** (4/15 Huyền thoại ủng hộ) — `CAUTIOUS`
