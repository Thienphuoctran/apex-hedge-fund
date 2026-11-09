<<<<<<< HEAD
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
=======
# NGHỊ QUYẾT HỘI ĐỒNG ĐẦU TƯ TTCK VIỆT NAM (IC DECISION) — 2026-11-09
**Cơ quan ban hành**: Hội Đồng Đầu Tư & Quản Trị Rủi Ro (Ban 4 VN)
**Trạng thái phê duyệt**: PHÊ DUYỆT GIẢI NGÂN CHỌN LỌC THEO HỘI ĐỒNG 10 ĐẠI DANH THỦ (SELECTIVE ACCUMULATION)

---

## QUYẾT NGHỊ GIẢI NGÂN DANH MỤC TOP 8 SIÊU CỔ PHIẾU ĐẦU NGÀNH

### 🎯 **IDC** — Tổng Công Ty IDICO (HNX)
- **Quyết định**: **ACCUMULATE (Gom Mua Chủ Động Kim Tự Tháp 30-40-30)**
- **Điểm IC Tổng Hợp**: **90.3/100** | **Điểm 10 Đại Danh Thủ**: **94.9/100** | Xếp Hạng BCTC: **AAA** | F-Score: **9/9**
- **Định giá Graham & Lynch**: Giá trị nội tại Graham = **41,198 ₫** (MoS = **+64.8%**) | PEG = **0.39x** | EVA Spread = **+19.1%**
- **Luận điểm Bảo vệ (`Bull Agent`)**: BCTC hạng AAA (Điểm 10 Danh Thủ: 94.9/100, Piotroski F-Score: 9/9, Lynch PEG: 0.39x, Graham MoS: +64.8%), Tiền thật OCF/LNST = 1.58x, FCF = 2,530 tỷ VNĐ, tín hiệu VSA: Tích lũy cạn cung.
- **Phản biện Rủi ro (`Bear Agent`)**: Áp lực rung lắc T+2.5 phiên chiều; nội tại BCTC kiểm toán và điểm số 10 Đại Danh Thủ đồng thuận tuyệt đối.
- **Phán quyết Hòa giải (`Master CIO`)**: **UNANIMOUS_APPROVAL (Đồng thuận tuyệt đối Bull & Risk IC)**
- **Tỷ trọng phân bổ**: **13.4%** NAV (Tương đương 134,000,000 VND / ~5,300 cổ phiếu lô chẵn 100)
- **Ngưỡng Cắt Lỗ Nghiêm Ngặt**: **23,750 VND** (Chandelier Stop: 0 VND)
- **Mục tiêu Chốt Lời**: TP1 = **26,625 VND** | TP2 = **27,812 VND** (Tỷ lệ R:R hiệu dụng = **1:2.05**)

### 🎯 **STB** — Sài Gòn Thương Tín (Sacombank) (HOSE)
- **Quyết định**: **ACCUMULATE (Gom Mua Chủ Động Kim Tự Tháp 30-40-30)**
- **Điểm IC Tổng Hợp**: **93.4/100** | **Điểm 10 Đại Danh Thủ**: **89.6/100** | Xếp Hạng BCTC: **AAA** | F-Score: **9/9**
- **Định giá Graham & Lynch**: Giá trị nội tại Graham = **110,780 ₫** (MoS = **+58.3%**) | PEG = **0.54x** | EVA Spread = **-6.6%**
- **Luận điểm Bảo vệ (`Bull Agent`)**: BCTC hạng AAA (Điểm 10 Danh Thủ: 89.6/100, Piotroski F-Score: 9/9, Lynch PEG: 0.54x, Graham MoS: +58.3%), Tiền thật OCF/LNST = 1.26x, FCF = 11,650 tỷ VNĐ, tín hiệu VSA: POCKET_PIVOT_BREAKOUT (Dòng tiền thông minh gom chủ động Vol lớn vượt nền).
- **Phản biện Rủi ro (`Bear Agent`)**: CẢNH BÁO ĐIỂM MUA: RSI tiệm cận vùng quá mua (75.3) — Cấm đua lệnh giá xanh ATO.
- **Phán quyết Hòa giải (`Master CIO`)**: **APPROVED_LIMIT_PULLBACK (Bác bỏ Veto định giá • Duyệt chia lệnh Kim Tự Tháp 30-40-30)**
- **Tỷ trọng phân bổ**: **11.5%** NAV (Tương đương 115,000,000 VND / ~1,600 cổ phiếu lô chẵn 100)
- **Ngưỡng Cắt Lỗ Nghiêm Ngặt**: **65,757 VND** (Chandelier Stop: 64,696 VND)
- **Mục tiêu Chốt Lời**: TP1 = **75,516 VND** | TP2 = **79,546 VND** (Tỷ lệ R:R hiệu dụng = **1:2.05**)

### 🎯 **MSN** — Tập Đoàn Masan (HOSE)
- **Quyết định**: **ACCUMULATE (Gom Mua Chủ Động Kim Tự Tháp 30-40-30)**
- **Điểm IC Tổng Hợp**: **93.0/100** | **Điểm 10 Đại Danh Thủ**: **90.3/100** | Xếp Hạng BCTC: **AAA** | F-Score: **7/9**
- **Định giá Graham & Lynch**: Giá trị nội tại Graham = **116,732 ₫** (MoS = **+59.9%**) | PEG = **0.25x** | EVA Spread = **-2.8%**
- **Luận điểm Bảo vệ (`Bull Agent`)**: BCTC hạng AAA (Điểm 10 Danh Thủ: 90.3/100, Piotroski F-Score: 7/9, Lynch PEG: 0.25x, Graham MoS: +59.9%), Tiền thật OCF/LNST = 3.79x, FCF = 4,200 tỷ VNĐ, tín hiệu VSA: POCKET_PIVOT_BREAKOUT (Dòng tiền thông minh gom chủ động Vol lớn vượt nền).
- **Phản biện Rủi ro (`Bear Agent`)**: Áp lực rung lắc T+2.5 phiên chiều; nội tại BCTC kiểm toán và điểm số 10 Đại Danh Thủ đồng thuận tuyệt đối.
- **Phán quyết Hòa giải (`Master CIO`)**: **UNANIMOUS_APPROVAL (Đồng thuận tuyệt đối Bull & Risk IC)**
- **Tỷ trọng phân bổ**: **14.0%** NAV (Tương đương 140,000,000 VND / ~1,900 cổ phiếu lô chẵn 100)
- **Ngưỡng Cắt Lỗ Nghiêm Ngặt**: **69,371 VND** (Chandelier Stop: 68,742 VND)
- **Mục tiêu Chốt Lời**: TP1 = **77,717 VND** | TP2 = **81,164 VND** (Tỷ lệ R:R hiệu dụng = **1:2.05**)

### 🎯 **SSI** — Chứng Khoán SSI (HOSE)
- **Quyết định**: **ACCUMULATE (Gom Mua Chủ Động Kim Tự Tháp 30-40-30)**
- **Điểm IC Tổng Hợp**: **89.1/100** | **Điểm 10 Đại Danh Thủ**: **91.4/100** | Xếp Hạng BCTC: **AAA** | F-Score: **9/9**
- **Định giá Graham & Lynch**: Giá trị nội tại Graham = **31,106 ₫** (MoS = **+52.5%**) | PEG = **0.45x** | EVA Spread = **+4.1%**
- **Luận điểm Bảo vệ (`Bull Agent`)**: BCTC hạng AAA (Điểm 10 Danh Thủ: 91.4/100, Piotroski F-Score: 9/9, Lynch PEG: 0.45x, Graham MoS: +52.5%), Tiền thật OCF/LNST = 1.11x, FCF = 3,200 tỷ VNĐ, tín hiệu VSA: NEUTRAL_SUPPLY_TESTING (Cung cầu giằng co kiểm định vùng hỗ trợ).
- **Phản biện Rủi ro (`Bear Agent`)**: Áp lực rung lắc T+2.5 phiên chiều; nội tại BCTC kiểm toán và điểm số 10 Đại Danh Thủ đồng thuận tuyệt đối.
- **Phán quyết Hòa giải (`Master CIO`)**: **UNANIMOUS_APPROVAL (Đồng thuận tuyệt đối Bull & Risk IC)**
- **Tỷ trọng phân bổ**: **12.9%** NAV (Tương đương 129,000,000 VND / ~6,300 cổ phiếu lô chẵn 100)
- **Ngưỡng Cắt Lỗ Nghiêm Ngặt**: **19,350 VND** (Chandelier Stop: 19,088 VND)
- **Mục tiêu Chốt Lời**: TP1 = **21,765 VND** | TP2 = **22,762 VND** (Tỷ lệ R:R hiệu dụng = **1:2.05**)

### 🎯 **GMD** — Gemadept (Cảng nước sâu Gemalink) (HOSE)
- **Quyết định**: **ACCUMULATE (Gom Mua Chủ Động Kim Tự Tháp 30-40-30)**
- **Điểm IC Tổng Hợp**: **92.2/100** | **Điểm 10 Đại Danh Thủ**: **94.6/100** | Xếp Hạng BCTC: **AAA** | F-Score: **9/9**
- **Định giá Graham & Lynch**: Giá trị nội tại Graham = **62,634 ₫** (MoS = **+18.6%**) | PEG = **0.82x** | EVA Spread = **+2.9%**
- **Luận điểm Bảo vệ (`Bull Agent`)**: BCTC hạng AAA (Điểm 10 Danh Thủ: 94.6/100, Piotroski F-Score: 9/9, Lynch PEG: 0.82x, Graham MoS: +18.6%), Tiền thật OCF/LNST = 1.14x, FCF = 1,070 tỷ VNĐ, tín hiệu VSA: NO_SUPPLY_TEST_CUNG (Nến biên hẹp, Vol cạn < 0.8x MA20 — Cạn cung tổ chức giữ nền).
- **Phản biện Rủi ro (`Bear Agent`)**: Áp lực rung lắc T+2.5 phiên chiều; nội tại BCTC kiểm toán và điểm số 10 Đại Danh Thủ đồng thuận tuyệt đối.
- **Phán quyết Hòa giải (`Master CIO`)**: **UNANIMOUS_APPROVAL (Đồng thuận tuyệt đối Bull & Risk IC)**
- **Tỷ trọng phân bổ**: **9.5%** NAV (Tương đương 95,000,000 VND / ~1,700 cổ phiếu lô chẵn 100)
- **Ngưỡng Cắt Lỗ Nghiêm Ngặt**: **49,104 VND** (Chandelier Stop: 49,523 VND)
- **Mục tiêu Chốt Lời**: TP1 = **57,787 VND** | TP2 = **61,431 VND** (Tỷ lệ R:R hiệu dụng = **1:2.05**)

### 🎯 **TCB** — Kỹ Thương Việt Nam (Techcombank) (HOSE)
- **Quyết định**: **ACCUMULATE (Gom Mua Chủ Động Kim Tự Tháp 30-40-30)**
- **Điểm IC Tổng Hợp**: **88.1/100** | **Điểm 10 Đại Danh Thủ**: **92.9/100** | Xếp Hạng BCTC: **AAA** | F-Score: **9/9**
- **Định giá Graham & Lynch**: Giá trị nội tại Graham = **51,025 ₫** (MoS = **+135.7%**) | PEG = **0.33x** | EVA Spread = **+7.1%**
- **Luận điểm Bảo vệ (`Bull Agent`)**: BCTC hạng AAA (Điểm 10 Danh Thủ: 92.9/100, Piotroski F-Score: 9/9, Lynch PEG: 0.33x, Graham MoS: +135.7%), Tiền thật OCF/LNST = 1.16x, FCF = 24,700 tỷ VNĐ, tín hiệu VSA: DRY_VOLUME_BASE (Siết nền biên độ hẹp VCP — Chờ điểm nổ Volume).
- **Phản biện Rủi ro (`Bear Agent`)**: Áp lực rung lắc T+2.5 phiên chiều; nội tại BCTC kiểm toán và điểm số 10 Đại Danh Thủ đồng thuận tuyệt đối.
- **Phán quyết Hòa giải (`Master CIO`)**: **UNANIMOUS_APPROVAL (Đồng thuận tuyệt đối Bull & Risk IC)**
- **Tỷ trọng phân bổ**: **14.4%** NAV (Tương đương 144,000,000 VND / ~6,600 cổ phiếu lô chẵn 100)
- **Ngưỡng Cắt Lỗ Nghiêm Ngặt**: **20,664 VND** (Chandelier Stop: 21,225 VND)
- **Mục tiêu Chốt Lời**: TP1 = **22,932 VND** | TP2 = **23,868 VND** (Tỷ lệ R:R hiệu dụng = **1:2.05**)

### 🎯 **MWG** — Thế Giới Di Động (HOSE)
- **Quyết định**: **ACCUMULATE (Gom Mua Chủ Động Kim Tự Tháp 30-40-30)**
- **Điểm IC Tổng Hợp**: **87.2/100** | **Điểm 10 Đại Danh Thủ**: **94.1/100** | Xếp Hạng BCTC: **AAA** | F-Score: **9/9**
- **Định giá Graham & Lynch**: Giá trị nội tại Graham = **137,874 ₫** (MoS = **+87.1%**) | PEG = **0.21x** | EVA Spread = **+8.4%**
- **Luận điểm Bảo vệ (`Bull Agent`)**: BCTC hạng AAA (Điểm 10 Danh Thủ: 94.1/100, Piotroski F-Score: 9/9, Lynch PEG: 0.21x, Graham MoS: +87.1%), Tiền thật OCF/LNST = 2.22x, FCF = 7,700 tỷ VNĐ, tín hiệu VSA: NEUTRAL_SUPPLY_TESTING (Cung cầu giằng co kiểm định vùng hỗ trợ).
- **Phản biện Rủi ro (`Bear Agent`)**: Áp lực rung lắc T+2.5 phiên chiều; nội tại BCTC kiểm toán và điểm số 10 Đại Danh Thủ đồng thuận tuyệt đối.
- **Phán quyết Hòa giải (`Master CIO`)**: **UNANIMOUS_APPROVAL (Đồng thuận tuyệt đối Bull & Risk IC)**
- **Tỷ trọng phân bổ**: **15.6%** NAV (Tương đương 156,000,000 VND / ~2,100 cổ phiếu lô chẵn 100)
- **Ngưỡng Cắt Lỗ Nghiêm Ngặt**: **70,629 VND** (Chandelier Stop: 71,804 VND)
- **Mục tiêu Chốt Lời**: TP1 = **77,693 VND** | TP2 = **80,611 VND** (Tỷ lệ R:R hiệu dụng = **1:2.05**)

### 🎯 **PVT** — Tổng Công Ty Vận Tải Dầu Khí (HOSE)
- **Quyết định**: **ACCUMULATE (Gom Mua Chủ Động Kim Tự Tháp 30-40-30)**
- **Điểm IC Tổng Hợp**: **90.3/100** | **Điểm 10 Đại Danh Thủ**: **92.4/100** | Xếp Hạng BCTC: **AAA** | F-Score: **9/9**
- **Định giá Graham & Lynch**: Giá trị nội tại Graham = **47,672 ₫** (MoS = **+132.0%**) | PEG = **0.46x** | EVA Spread = **+2.0%**
- **Luận điểm Bảo vệ (`Bull Agent`)**: BCTC hạng AAA (Điểm 10 Danh Thủ: 92.4/100, Piotroski F-Score: 9/9, Lynch PEG: 0.46x, Graham MoS: +132.0%), Tiền thật OCF/LNST = 2.01x, FCF = 500 tỷ VNĐ, tín hiệu VSA: NO_SUPPLY_TEST_CUNG (Nến biên hẹp, Vol cạn < 0.8x MA20 — Cạn cung tổ chức giữ nền).
- **Phản biện Rủi ro (`Bear Agent`)**: Áp lực rung lắc T+2.5 phiên chiều; nội tại BCTC kiểm toán và điểm số 10 Đại Danh Thủ đồng thuận tuyệt đối.
- **Phán quyết Hòa giải (`Master CIO`)**: **UNANIMOUS_APPROVAL (Đồng thuận tuyệt đối Bull & Risk IC)**
- **Tỷ trọng phân bổ**: **8.7%** NAV (Tương đương 87,000,000 VND / ~4,200 cổ phiếu lô chẵn 100)
- **Ngưỡng Cắt Lỗ Nghiêm Ngặt**: **19,112 VND** (Chandelier Stop: 21,179 VND)
- **Mục tiêu Chốt Lời**: TP1 = **22,621 VND** | TP2 = **24,134 VND** (Tỷ lệ R:R hiệu dụng = **1:2.05**)
>>>>>>> fd7b2149c1ea47855685c449428d9024ef39f4eb
