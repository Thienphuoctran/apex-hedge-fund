# 🎖️ BIÊN BẢN GIAO BAN SOI GƯƠNG TỰ PHÊ BÌNH 8H30 SÁNG — NGÀY 2026-11-24
*Thời gian họp*: `2026-11-24 13:34:33` | *Trạng thái sàn*: `🎌 NGHỈ LỄ 24/11 (Mở lại 25/11)`  
*Chủ trì phiên họp*: **James — Master CIO (Ban 8)** & **Palmer (Quản Trị Hệ Thống)**  
*Chuyên viên tuyên thệ*: **Minh Quân (Ban 7 VN)** & **Alex (Ban 7 Global)**  
*Hội đồng thẩm định & tự học*: **Ban 5 (Performance & Adaptive Learning)**, **Hiền (Ban 10 — BCTC)** & **Victor (Ban 9 — Sentinel)**  
*Phục vụ trực tiếp*: **Chủ tịch Trần Quốc Thiên Phước** *(TCBS: `105C307855` - NAV: `20,051,117 ₫`)*  

> [!IMPORTANT]
> **🎌 NGHỈ LỄ NGÀY VĂN HÓA VIỆT NAM (24/11) — HOSE/HNX ĐÓNG CỬA (Mở lại Thứ Tư 25/11/2026)**  
> Do 24/11 là ngày nghỉ lễ (Ngày Văn hóa Việt Nam (24/11)), lịch thanh toán T+2 dịch thêm 1 ngày làm việc: tiền bán 20/11 về 25/11; cổ phiếu mua 23/11 về chiều 26/11/2026. — Hôm nay khóa 100% lệnh mới (`0%`), giữ vững kỷ luật cho phiên mở lại **Thứ Tư 25/11/2026**.

---
## I. TUYÊN THỆ TỰ KIỂM ĐIỂM & RÚT KINH NGHIỆM TỪ PHIÊN TRƯỚC (CLOSED-LOOP FEEDBACK)
Kính thưa Chủ tịch Phước Trần và Tổng Tư Lệnh Master CIO James, tôi là **Minh Quân** cùng **Alex**. Trước giờ phiên mới (`SÀN ĐÓNG CỬA NGÀY LỄ — RÀ SOÁT KỶ LUẬT`), chúng tôi tuyên thệ tuân thủ:

> ⚠️ **[CHỈ THỊ SỬA ĐỔI BẮT BUỘC CHO ALEX (US)] Alex phải cập nhật trần rủi ro tương quan Bán dẫn khống chế <= 28% NAV và tinh chỉnh lại độ sâu lệnh Limit Pullback vào specialist_evolution_journal.md.**
> ⚠️ **[MEM-VN-001 • ATO_BULL_TRAP_GUARD] Bài học: Đua lệnh giá xanh phiên ATO (9h00-9h15) tại TTCK Việt Nam thường chịu thiệt giá vốn 1.5%-2.5% khi áp lực hàng T+2.5 về tài khoản lúc 13h30 chiều. -> Hành động: Cấm mua đuổi ATO; bắt buộc đặt lệnh Limit LO chiết khấu -0.35x ATR(14) và chờ xác nhận lực hấp thụ trong Khung Giờ Vàng 14h00-14h25.**
> ⚠️ **[MEM-VN-002 • OMISSION_ERROR_NO_SUPPLY] Bài học: Chần chừ không giải ngân thăm dò khi siêu cổ phiếu BCTC hạng AAA xuất hiện nến Test Cung cạn Vol tại nền hỗ trợ sẽ bỏ lỡ nhịp bứt phá mạnh. -> Hành động: Giải ngân ngay 30%-60% vị thế thăm dò tại nền No-Supply khi OCF/LNST >= 1.0x và Altman Z'' > 4.0.**
> ⚠️ **[MEM-VN-003 • FORENSIC_DEBT_TRAP_VETO] Bài học: Các nhịp kéo trần đầu cơ của cổ phiếu âm dòng tiền kinh doanh và nợ vay cao thường kết thúc bằng chuỗi giảm sàn mất thanh khoản. -> Hành động: Khóa cứng trong danh sách Veto; đánh giá mọi nhịp tăng của nhóm này là Disciplined Pass (Bỏ qua có kỷ luật).**

---
## II. TRẠNG THÁI 5 KHÓA CHỐT KỶ LUẬT BẰNG MÃ NGUỒN (HARD-CODED GUARDRAILS)
Hệ thống phần mềm đã kích hoạt cơ chế tự động từ chối lệnh vi phạm:

| Mã Khóa Chốt | Tên Quy Tắc An Toàn | Trạng Thái Phần Mềm | Nguồn Gốc Bài Học Sai Lầm |
| :---: | :--- | :---: | :--- |
| **`GUARD-01`** | Khóa Cứng Bẫy Mua Đuổi ATO (9h00 - 10h00) | **🟢 HOẠT ĐỘNG KHÓA CỨNG (ENFORCED)** | _MEM-VN-001 (Mistake Autopsy: F0 thường đu đỉnh ATO khi tạo Gap xanh ảo, bị xả T+2 lúc 13h30)_ |
| **`GUARD-02`** | Khóa Cứng Cổ Phiếu Rác / Bẫy Nợ Vay / Lợi Nhuận Giấy | **🟢 HOẠT ĐỘNG KHÓA CỨNG (ENFORCED)** | _MEM-VN-003 (Vụ án DVD, TTF, NVL: Lãi kế toán nhưng OCF âm dồn dập và nợ đầm đìa)_ |
| **`GUARD-03`** | Cầu Chì Bắt Buộc Cân Bằng Trạng Thái T+0 Trước 14h25 | **🟢 HOẠT ĐỘNG KHÓA CỨNG (ENFORCED)** | _Quy tắc an toàn vốn: Tham lướt sóng biến thành gồng lỗ qua đêm do kẹt hàng T+2.5_ |
| **`GUARD-04`** | Khống Chế Tổn Thất Tuyệt Đối Stop Loss <= 1.5% NAV | **🟢 HOẠT ĐỘNG KHÓA CỨNG (ENFORCED)** | _Công thức Position Sizing chuẩn mực thể chế của Palmer & Hội đồng Rủi ro Ban 4_ |
| **`GUARD-05`** | Cấm Tuyệt Đối Bình Quân Giá Xuống Dưới MA200 | **🟢 HOẠT ĐỘNG KHÓA CỨNG (ENFORCED)** | _Bài học xương máu của Jesse Livermore & Stan Weinstein: Trung bình giá xuống khi downtrend là tự sát_ |

---
## III. RÀ SOÁT DANH MỤC THỰC TẾ THEO SSOT (TCBS `105C307855`)
- **Tổng NAV thực tế**: **`20,051,117 ₫`**
- **Lợi nhuận tạm tính**: **`+0 ₫ (+0.00%)`**
- **Tiền mặt dự phòng (Dry Powder)**: **`15,541,117 ₫`** (`77.5% NAV`)

| Mã Cổ Phiếu | Khối Lượng | Giá Vốn | Thị Giá Hiện Tại | Ngưỡng Cắt Lỗ Stop 2xATR | Mục Tiêu Chốt Lời TP1 | Kế Hoạch Tác Chiến |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`TPB`** | 200 CP | 12,300 ₫ | 12,350 ₫ | **11,600 ₫** | **13,350 ₫** | Giữ Stop 2xATR • Két `15,541,117 ₫` • Chờ T+2 về & Nhịp 2 lúc `14h05–14h25` (Thứ Tư 25/11/2026) |
| **`HPG`** | 100 CP | 20,500 ₫ | 20,400 ₫ | **19,300 ₫** | **22,300 ₫** | Giữ Stop 2xATR • Két `15,541,117 ₫` • Chờ T+2 về & Nhịp 2 lúc `14h05–14h25` (Thứ Tư 25/11/2026) |

---
## IV. PHÊ DUYỆT CUỐI CÙNG TỪ TỔNG TƯ LỆNH MASTER CIO JAMES
- **Nghị quyết tham chiếu**: `2026-11-23_Full_10Dept_Council_And_145Stocks_Scan.md`
- **Chỉ thị hợp nhất**: 🎌 NGHỈ LỄ NGÀY VĂN HÓA VIỆT NAM (24/11) — HOSE/HNX ĐÓNG CỬA (Mở lại Thứ Tư 25/11/2026). Danh mục SSOT TCBS 105C307855 giữ nguyên: 200 TPB + 100 HPG (4,510,000 ₫ = 22.5% NAV) + Tiền mặt 15,541,117 ₫ (77.5% NAV). Hàng T+2: 200 TPB về chiều 26/11, 100 HPG về chiều 26/11. Mọi giải ngân mới Nhịp 2 (ưu tiên 100 CTG @ 30,000–30,300 & 200 NAB @ 13,000–13,200, dự phòng 100 CTS) chỉ xét trong Khung Giờ Vàng 14h05–14h25 phiên mở lại (Thứ Tư 25/11/2026).
- **Trạng thái phần mềm Guardrails**: ✅ **ĐÃ KHÓA CỨNG — KHÔNG AI CÓ THỂ PHÁ VỠ KỶ LUẬT.**
- **Lệnh điều hành hôm nay**: 🎌 **KHÓA GIAO DỊCH NGÀY NGHỈ LỄ (0%) — CHUẨN BỊ CHO THỨ TƯ 25/11/2026**
- *Chữ ký phê duyệt*: **James — Apex Master CIO (Ban 8)** *(Đã ký số hệ thống lúc 08:30)*