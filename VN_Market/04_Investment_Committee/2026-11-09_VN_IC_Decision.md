# [BAN 4 VN] NGHỊ QUYẾT HỘI ĐỒNG ĐẦU TƯ & QUẢN TRỊ RỦI RO ĐỊNH LƯỢNG T+2.5
> **CƠ QUAN PHÁT HÀNH**: BAN 4 VN — HỘI ĐỒNG ĐẦU TƯ & QUẢN TRỊ RỦI RO ĐỊNH LƯỢNG  
> **PHIÊN GIAO DỊCH**: Thứ Hai, Ngày 2026-11-09 | **KHUNG GIỜ CÔNG BỐ**: `09:30 AM` Ca Sáng (task-0930-guard03)  
> **CHỦ TRÌ**: Trưởng Ban Quản Trị Rủi Ro Định Lượng T+2.5 (`vn-investment-committee-agent`)  
> **TÀI KHOẢN THỤ HƯỞNG**: TCBS Tiểu Khoản Thường: **`105C307855`** (Chủ tịch: **Trần Quốc Thiên Phước**)  
> **TỔNG VỐN QUẢN LÝ**: **`20,167,119 ₫`** (100% TIỀN MẶT, 0 CP kẹp hàng qua đêm)

---

## 🛡️ 1. PHÊ DUYỆT ĐỊNH CỠ VỊ THẾ POSITION SIZING & VAN AN TOÀN TOÁN HỌC

Tuân thủ nghiêm ngặt Hiến Chương Apex V1.0 và chu kỳ thanh toán T+2.5 của TTCK Việt Nam, Hội đồng Rủi ro Ban 4 VN chính thức phê duyệt định mức giải ngân cho phiên hôm nay:

$$N = \frac{C \times R_{trade}}{P_{entry} - P_{stop}}$$

| Mã CP | Sàn | Thị Giá Tham Chiếu | Lệnh Phê Duyệt Hôm Nay (Nhịp 1) | Vốn Giải Ngân Thực Tế | Ngưỡng Cắt Lỗ Cứng Stop 2xATR | Mức Lỗ Tối Đa Khi Dính Cắt Lỗ | Tỷ Lệ Tổn Thất Trên NAV (% NAV) | Mốc Chốt Lời TP1 / TP2 | Trạng Thái Phê Duyệt |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`HDB`** | HOSE | 22,300 – 22,450 đ | **100 CP (Lô chẵn 100)** | **~2,230,000 ₫** | **21,220 đ** *(-5.69%)* | **-123,000 ₫** | **0.61% NAV** *(< 1.0%)* | 24,290 đ / 25,820 đ | **PHÊ DUYỆT BẮM CÒ 14h00** |
| **`MSH`** | HOSE | 34,600 – 35,000 đ | **100 CP (Lô chẵn 100)** | **~3,460,000 ₫** | **33,090 đ** *(-6.79%)* | **-237,000 ₫** | **1.17% NAV** *(< 1.2%)* | 39,560 đ / 43,040 đ | **PHÊ DUYỆT BẮM CÒ 14h00** |
| **TỔNG CỘNG** | — | — | **200 CP (2 Lô)** | **~5,690,000 ₫** | — | **-360,000 ₫** | **1.78% NAV** *(Bảo toàn 98.2%)* | — | **TIỀN MẶT CÒN LẠI: 14.47M (71.8%)** |

---

## 🔒 2. BA ĐIỀU KIỆN CẦU CHÌ AN TOÀN BẮT BUỘC (SAFETY FUSE INVARIANTS)
1. **Cầu Chì Thời Gian (Khung Giờ Vàng 14h00 – 14h25)**: Chỉ mở mua trong khoảng 14h00 – 14h25 khi đã xác nhận xong lực hấp thụ hàng T+2.5. Chậm nhất đúng **14h25** đóng toàn bộ sổ lệnh mua.
2. **Cầu Chì Loại Lệnh (100% Lệnh Limit LO)**: Nghiêm cấm dùng lệnh thị trường MP để tránh bị tạo lập quét trượt giá.
3. **Cầu Chì Cắt Lỗ Tự Động (Stop 2xATR $\le 6.8\%$)**: Nếu thị trường có biến động bất ngờ, lệnh Stop Loss tự động bảo vệ két tiền, mức tổn thất tối đa cả 2 mã chỉ là 360,000 ₫ (chỉ 1.78% NAV), giữ nguyên 98.2% vốn cho Quỹ!
