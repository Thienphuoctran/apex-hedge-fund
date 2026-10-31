# GIAI ĐOẠN 3: VĨ MÔ CHU KỲ, DÒNG TIỀN LIÊN THỊ TRƯỜNG & QUẢN TRỊ RỦI RO ĐỊNH LƯỢNG
## (Stage 3: Macro Cycles & Quantitative Portfolio Risk Engineering)

> **Mục tiêu**: Nâng cấp tư duy từ người "chọn cổ phiếu lẻ" (Stock Picker) lên nhà quản lý danh mục cấp Quỹ (Portfolio Manager), biết đọc dòng chảy thanh khoản toàn cầu và bảo vệ tài khoản bằng toán học định lượng.

---

### Bài 3.1: 4 Chế Độ Vĩ Mô Toàn Cầu (The 4 Macro Regimes)
Kinh tế học vĩ mô chi phối 80% xu hướng lớn của thị trường chứng khoán. Mô hình Ray Dalio & Bridgewater chia nền kinh tế làm 4 góc phần tư:

| Chế Độ Vĩ Mô | Đặc Điểm (Tăng trưởng vs Lạm phát) | Nhóm Ngành Hưởng Lợi | Nhóm Ngành Bất Lợi |
| :--- | :--- | :--- | :--- |
| **1. Reflation / Risk-On** | Tăng trưởng tăng, Lạm phát hạ nhiệt | Công nghệ (`XLK`), Bán dẫn (`SMH`), Tiêu dùng không thiết yếu (`XLY`) | Tiện ích (`XLU`), Hàng tiêu dùng thiết yếu (`XLP`) |
| **2. Inflationary Boom** | Tăng trưởng tăng, Lạm phát tăng nóng | Năng lượng (`XLE`), Nguyên vật liệu (`XLB`), Công nghiệp (`XLI`) | Cổ phiếu tăng trưởng định giá cao |
| **3. Stagflation (Đình lạm)** | Tăng trưởng suy giảm, Lạm phát neo cao | Dầu mỏ (`CL=F`), Vàng (`GC=F`), Phòng thủ (`XLP`, `XLU`) | Công nghệ, Bán lẻ, Cổ phiếu nợ vay lớn |
| **4. Deflationary Recession** | Tăng trưởng giảm, Lạm phát sụt giảm | Trái phiếu dài hạn (`TLT`), Tiền mặt (`USD`), Cổ phiếu y tế (`XLV`) | Hàng hóa, Ngân hàng, Bán dẫn |

---

### Bài 3.2: 4 Thước Đo Vĩ Mô Hàng Ngày Phải Xem Lúc 7h30 Sáng
1. **Chỉ số Biến động CBOE (`^VIX`) — Thước đo Nỗi sợ hãi**:
   - `VIX < 15`: Thị trường hưng phấn, bình lặng (Complacent).
   - `15 <= VIX <= 20`: Mức biến động trung bình bình thường.
   - `VIX > 20`: Bắt đầu có rung lắc và áp lực phòng vệ quyền chọn.
   - `VIX > 30`: Hoảng loạn tột độ, cơ hội săn tài sản giá rẻ cho nhà đầu tư kiên nhẫn.
2. **Lợi suất Trái phiếu Mỹ 10 năm (`^TNX`) — Lãi suất chuẩn toàn cầu**:
   - Khi `^TNX` tăng mạnh: Chi phí vốn của doanh nghiệp tăng lên, chiết khấu dòng tiền tương lai của các cổ phiếu Tech giảm mạnh.
3. **Chỉ số Đô la Mỹ (`DXY` / `DX-Y.NYB`) — Sức mạnh đồng USD**:
   - `DXY` tăng quá nóng thường gây áp lực thanh khoản lên các thị trường mới nổi (Emerging Markets) và làm giảm doanh thu quốc tế quy đổi về USD của các tập đoàn đa quốc gia như Apple, Microsoft.
4. **Giá Dầu WTI (`CL=F`)**: Thước đo trực tiếp của kỳ vọng lạm phát toàn cầu.

---

### Bài 3.3: Quản Trị Rủi Ro Định Lượng — Phương Pháp ATR Risk-Parity
Tại sao Quỹ đầu tư không mua theo kiểu "chia đều mỗi mã 20% tiền"?
Bởi vì một cổ phiếu biến động mạnh như Nvidia (`NVDA` - ATR hàng ngày $4.5) có rủi ro gấp 4 lần một cổ phiếu phòng thủ như Johnson & Johnson (`JNJ` - ATR hàng ngày $1.1).

- **ATR (Average True Range)**: Thước đo biên độ dao động trung bình thực tế trong 14 phiên.
- **Quy tắc Định Cỡ Vị Thế Theo ATR (Volatility Sizing)**:
  $$\text{Tỷ trọng Cổ phiếu} \propto \frac{1}{\text{ATR}(14)}$$
  Cổ phiếu biến động càng mạnh thì tỷ trọng phân bổ vốn càng phải nhỏ lại, để nếu thị trường biến động giật cục, tổn thất tối đa của mỗi vị thế lên danh mục là hoàn toàn tương đương nhau.
- **Ngưỡng Cắt Lỗ Bắt Buộc (Stop-Loss 2xATR)**:
  $$\text{Ngưỡng Stop-Loss} = \text{Entry Price} - 2 \times \text{ATR}(14)$$
  Nếu giá thủng ngưỡng này, xác nhận sóng ngắn hạn đã bị phá vỡ, bắt buộc phải cắt lỗ để bảo vệ vốn.

---

### Bài 3.4: Ma Trận Tương Quan (Correlation Matrix) & Tránh "Bẫy Đa Dạng Hóa Ảo"
- Nếu bạn mua cùng lúc: Nvidia, AMD, TSMC, Broadcom và Qualcomm -> Bạn tưởng mình sở hữu 5 cổ phiếu đa dạng, nhưng thực tế hệ số tương quan của chúng $r > 0.70$. Khi ngành bán dẫn bị điều chỉnh, toàn bộ 5 mã sẽ cùng giảm!
- **Quy tắc Quỹ**: Khóa tổng tỷ trọng cho một cụm tương quan cao (Cluster Cap) không quá 15% - 20% tổng danh mục.

---

### Bài Thực Hành & Tự Đánh Giá Cấp Độ 3
1. Hãy mở báo cáo `04_Investment_Committee/YYYY-MM-DD_Quant_Risk_And_Correlation.md` hôm nay: Cổ phiếu nào đang có hệ số biến động ATR cao nhất? Tại sao Ban 4 lại phân bổ tỷ trọng của mã đó thấp hơn các mã phòng thủ?
2. Nếu VIX tăng vọt từ 17 lên 23 trong 1 ngày, kế hoạch hành động khôn ngoan nhất của bạn là gì: Mua full margin hay thắt chặt ngưỡng cắt lỗ và giữ tỷ trọng tiền mặt?
