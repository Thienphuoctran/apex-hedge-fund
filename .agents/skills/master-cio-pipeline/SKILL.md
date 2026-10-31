---
name: master-cio-pipeline
description: >-
  Quy trình vận hành Ban Đầu Tư Tối Cao — Tổng Tư Lệnh Phân Bổ Vốn Thống Nhất Toàn Cầu & Việt Nam (Unified Chief Investment Officer - "Apex CIO Master Execution Desk"). Tổng hợp toàn diện BCTC, KQKD của 2 đội nhóm Quốc tế & VN, đối thoại Alex vs Minh Quân, chốt phân bổ vốn ban đầu khoa học và bấm cò thực thi tối ưu lợi nhuận.
---

# Quy Trình Vận Hành Ban Đầu Tư Tối Cao & Bấm Cò Thực Thi Thống Nhất (Apex Master CIO Pipeline)

Kỹ năng này điều phối bước thực thi tối cao — **"Khẩu súng" của toàn bộ hệ thống**, tích hợp trí tuệ của 14 phòng ban chuyên môn và 2 chuyên viên thực thi trưởng:
- **Alex** (Ban 7 Global): Phụ trách thị trường Mỹ / Quốc tế, 60/40 Pullback Limit.
- **Minh Quân** (Ban 7 VN): Phụ trách thị trường Việt Nam, 60/40 Pre-ATO & Breakout, kiểm soát T+2.5 và biên độ sàn HOSE/HNX.

---

## 1. Lệnh Kích Hoạt Nhanh Master CIO Engine

### Lựa Chọn A: Nạp Vốn Bằng Đô La Mỹ (USD)
```powershell
python scripts\master_cio_allocator.py --capital-usd 100000
```

### Lựa Chọn B: Nạp Vốn Bằng Tiền Đồng Việt Nam (VNĐ)
```powershell
python scripts\master_cio_allocator.py --capital-vnd 2540000000
```

---

## 2. Quy Trình Vận Hành 5 Bước Chuẩn Thể Chế

### Bước 1: Nạp Dữ Liệu Tự Động & Thẩm Tra BCTC 2 Thị Trường
- Đọc `07_Daily_Investment_Specialist/daily_specialist_ledger.json` (Alex).
- Đọc `VN_Market/07_Daily_Specialist/vn_daily_ledger.json` (Minh Quân).
- Đối chiếu dòng tiền tự do $FCF$ quốc tế với dòng tiền hoạt động $OCF$ thực dương, $Altman\ Z''$, và $Beneish\ M$ tại Việt Nam.

### Bước 2: Tòa Đàm Thượng Đỉnh Alex vs Minh Quân (Cross-Market Hearing)
- Đặt lên bàn cân: Áp lực tỷ giá USD/VND, chu kỳ tiền tệ Fed vs SBV, luân chuyển dòng tiền khối ngoại.
- Phản biện sắc bén: Loại trừ các cổ phiếu đang trong vùng quá mua hoặc sắp công bố BCTC ($\le 7$ ngày).

### Bước 3: Phân Bổ Vốn Ban Đầu Đa Tầng (Hierarchical Capital Allocation)
- **Tầng 1 (Vĩ mô)**: $55\%$ Global Portfolio (USD) + $35\%$ VN Portfolio (VND) + $10\%$ Dry Powder.
- **Tầng 2 (Chiến lược)**: $65\%$ Core Compounder + $35\%$ Tactical Alpha.
- **Tầng 3 (Từng vị thế)**: Định cỡ bằng $ATR\ Risk-Parity$ & $Kelly$, làm tròn số cổ phiếu (đặc biệt chuẩn lô chẵn 100 CP cho sàn HOSE/HNX).

### Bước 4: Khóa Rủi Ro Tuyệt Đối (Risk Lock-in)
- Ngưỡng cắt lỗ cứng: $Stop = 2\times ATR(14)$.
- Rủi ro tối đa cho mỗi lệnh nếu dính Stop Loss: **$\le 0.35\%$ Tổng NAV**.

### Bước 5: Ban Hành Sổ Lệnh Master Blotter & Báo Cáo
- `08_Master_Investment_CIO/YYYY-MM-DD_Master_CIO_Final_Decision.md`: Báo cáo phân tích quyết định đầy đủ.
- `08_Master_Investment_CIO/master_execution_blotter.json`: Sổ lệnh định dạng JSON sẵn sàng kết nối API giao dịch.
