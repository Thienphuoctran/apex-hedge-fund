# 🎯 KẾ HOẠCH TÁC CHIẾN THÍCH NGHI — PHIÊN ĐÁO HẠN PHÁI SINH `VN30F1M` THỨ NĂM `19/11/2026`
**Cơ quan ban hành:** Ban 7 VN (Minh Quân) — Phê duyệt bởi Ban 4 Risk, Master CIO James (Ban 8) & Kiểm sát Trọng (Ban 12)
**Căn cứ Hội nghị:** `APEX-SUMMIT-20261119-0430` (`04:30 ICT 19/11/2026`)
**Tài khoản thực thi:** TCBS `105C307855` — Chủ tịch Trần Quốc Thiên Phước (`0% Margin`)

---

## 1. BỨC TRANH VỐN & DANH MỤC HIỆN HỮU (SSOT CHỐT SAU PHIÊN `18/11`)

| Chỉ tiêu / Mã CP | Số lượng & Trạng thái | Giá vốn | Giá đóng cửa `18/11` | Giá trị / Lãi-Lỗ | Kế hoạch Kỷ luật Hôm nay (`19/11`) |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Tổng Tài sản (NAV)** | `0% Margin` | — | — | **`20,229,522 ₫`** | Trần tổng rủi ro tối đa toàn danh mục: `4.5% NAV = 910,328 ₫` |
| **Tiền mặt (`Cash`)** | Sẵn sàng | — | — | **`13,594,522 ₫ (67.2%)`** | Mặc định giữ **`0 ₫` giải ngân mới**; ngoại lệ tối đa `1 lô <= 2.2M` |
| **`MSH`** | `100 CP` (Khả dụng) | `34,510 ₫` | `35,200 ₫` | `3,520,000 ₫` (`+69,000 ₫ / +2.0%`) | `Trail Stop 34,600 ₫` \| `Hard Stop 33,090 ₫` \| `TP1 39,500 ₫` |
| **`BAF`** | `100 CP` (`T+1`, về chiều `19/11`) | `31,209 ₫` | `31,150 ₫` | `3,115,000 ₫` (`-5,900 ₫ / -0.2%`) | Quan sát khi về tài khoản `13h00–13h45`; giữ `>= 30,800`, cắt nếu gãy `Hard Stop 30,050 ₫` \| `TP1 33,200 ₫` |
| **`HDB`** | `0 CP` (Đã bán `22,050` chiều `18/11`) | — | `22,250 ₫` | — | **VETO TẠM THỜI `19/11`** (Đang chạy `hdb_post_exit_audit.yml` tới hết `20/11`, cấm Revenge Buy) |

- **Rủi ro Hard Stop đang khóa trên `MSH + BAF`:** `211,000 ₫ + 110,000 ₫ = 321,000 ₫` (`1.59% NAV`).
- **Ngân sách rủi ro còn lại dưới trần `4.5% NAV`:** `589,328 ₫` (`2.91% NAV`).

---

## 2. XUNG LỰC TỪ PHIÊN MỸ & BCTC QUỐC TẾ (`04:23–04:25 ICT`)

- **`^VIX` = `24.68 (-3.06%)` / AH `24.56`**: Hạ nhiệt từ đỉnh phiên `24.69` nhưng **chưa thủng `< 23.5`**; `.SPX = 7,323.55` (AH `7,323.63`) còn dưới `MA200 (7,340)`. Chế độ: **`Cautious High-Vol Rotation`**.
- **BCTC `NVDA` (công bố `17/11 AMC`) & `PANW` (`18/11 AMC`):**
  - `NVDA` Q3 FY27 doanh thu `$115.8B (+103% YoY)`, Data Center `$107.6B`, Q4 Guide `~$130B` — giá đóng `$150.96` (AH `$151.1932`) thuần túy do **chiết khấu chuyển giao CEO** (Jensen Huang từ chức `11/11`, CFO Colette Kress làm Interim CEO).
  - `PANW` Q1 FY27 bứt phá **`+8.04%` After-Hours (`$367.25`)** với RPO `$21.0B` và NGS ARR `$9.73B (+66% YoY)`.
- **Tác động chéo lên VN:** `VNM ETF` đóng `$16.70 (+0.18%)` và Russell 2000 `+0.52%` triệt tiêu nguy cơ hoảng loạn đầu phiên ATO. Ngược lại, `WTI` giảm **`-3.57%` (`$82.94`, AH `$83.12`)** tạo bất lợi ngắn hạn cho `BSR / PVD / GAS`, nhưng mở biên lợi nhuận cho **`PVT / GMD / BAF`**. `DXY 103.808` + `US10Y 5.068%` tiếp tục ghìm tỷ giá & dòng Ngân hàng.

---

## 3. SỔ LỆNH ĐIỀU KIỆN `19/11/2026` (KHUNG GIỜ VÀNG `14:00 – 14:25`)

> [!IMPORTANT]
> **Quy tắc Cửa Kép Bắt Buộc:** Mặc định hôm nay là **`0 ₫` (Không giải ngân mới)**. Lệnh dưới đây **CHỈ** được phép bấm nút khi đồng thời đạt cả 3 tiêu chuẩn tại bảng điện lúc `14:00 – 14:25`:
> 1. **Tỷ lệ Mua chủ động (`Buy-Up`) `>= 60%`**.
> 2. **Độ rộng thị trường `>= 40–45%` số mã tăng điểm**.
> 3. **Tín hiệu kỹ thuật VSA `No Supply` (cạn cung tại nền hỗ trợ) hoặc `Spring` rút chân thành công.**

| Thứ tự | Mã CP | Khối lượng & Lệnh | Vùng Giá VPS `18/11` | Giá trị Lệnh (% NAV) | Hard Stop & Mất tối đa | TP1 (`R:R`) | Tổng Rủi ro Danh mục |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **#1** | **`PVT`** | `100 CP` (`LO`) | `~19,000 ₫` | `1,900,000 ₫` (`9.39%`) | `17,700 ₫ (-6.84%)` / **`-130,000 ₫` (`0.64% NAV`)** | `21,600 ₫ (+13.68%)` / **`1:2.00`** | `451,000 ₫` (`2.23% NAV`) |
| **#2 (Dự phòng)** | **`TCB`** | `100 CP` (`LO`) | `~20,750 ₫` | `2,075,000 ₫` (`10.26%`) | `19,300 ₫ (-6.99%)` / **`-145,000 ₫` (`0.72% NAV`)** | `23,650 ₫ (+13.98%)` / **`1:2.00`** | `466,000 ₫` (`2.30% NAV`) |

- **Danh sách CẤM MUA (VETO) ngày `19/11`:** `HDB`, `BSR` (do `WTI -3.57%`), `FPT`, `DGC`, `MWG`, `FRT`, và các mã BĐS đòn bẩy cao.
- **Lệnh cấm ATC (`14:30 – 14:45`):** Ngừng mọi thao tác mua/bán đuổi giá trong 15 phút ATC ngày đáo hạn `VN30F1M`.

---

## 4. LỊCH HÀNH ĐỘNG THEO 4 KHUNG GIỜ

1. **`09:00 – 10:00`:** Tắt nút Mua. Để thị trường tiêu hóa cung-cầu ATO và biến động đáo hạn quanh `1,698–1,708`.
2. **`10:00 – 11:30`:** Giám sát vị thế **`MSH`** (`Trail Stop 34,600 ₫`, `Hard Stop 33,090 ₫`, `TP1 39,500 ₫`).
3. **`13:00 – 14:00`:** Kiểm tra **`100 CP BAF`** về tài khoản khả dụng. Xử lý dứt khoát nếu vi phạm `Hard Stop 30,050 ₫`; tiếp tục nắm giữ nếu giữ nền `>= 30,800 ₫`.
4. **`14:00 – 14:25`:** Đánh giá 3 tiêu chuẩn Cửa Kép. Đạt 3/3 ➔ Nhập **`LO 100 CP PVT`** (hoặc `TCB` nếu nhóm Ngân hàng dẫn sóng rõ). Thiếu dù chỉ 1 tiêu chuẩn ➔ Giữ **`0 ₫`**, bảo toàn `13,594,522 ₫` Tiền mặt.
