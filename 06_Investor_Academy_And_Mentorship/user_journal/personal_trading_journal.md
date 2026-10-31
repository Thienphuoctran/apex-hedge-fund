# NHẬT KÝ GIAO DỊCH THỰC CHIẾN & SOI GƯƠNG TÂM LÝ CÁ NHÂN
## (Personal Trade Journal & Behavioral Audit — Đồng Hành Cùng Giảng Viên Ban 6)
### Chiến Lược: Core & Satellite (Core 65% Tích Sản | Satellite 35% Lướt Sóng) • Chế Độ: Paper Trading

> *"Gương soi không nói dối. Nhật ký giao dịch chính là tấm gương chân thực nhất phản chiếu sự kỷ luật và tâm lý của bạn trước thị trường."*

Học viên sử dụng công cụ mô phỏng [scripts/paper_trading_simulator.py](file:///c:/Users/phuoc/Downloads/antigravity/Chứng%20khoán/scripts/paper_trading_simulator.py) để thực thi lệnh ảo (\$100,000 USD), sau đó ghi chép lại lý do và tâm lý vào sổ tay này để Giảng viên (`investor-mentorship-coach`) cùng bạn đối soát, chấm điểm kỷ luật và phân tích nguyên nhân.

---

## 1. Lệnh Nhanh Bằng Công Cụ Mô Phỏng (Paper Trading Commands)
- **Xem trạng thái danh mục, tiền mặt & P&L**:
  ```powershell
  python "c:\Users\phuoc\Downloads\antigravity\Chứng khoán\scripts\paper_trading_simulator.py" status
  ```
- **Đặt lệnh Mua (Tự động áp dụng Stop 2xATR)**:
  ```powershell
  python "c:\Users\phuoc\Downloads\antigravity\Chứng khoán\scripts\paper_trading_simulator.py" buy --symbol MSFT --shares 10 --type Core
  ```
- **Đặt lệnh Bán chốt lời / cắt lỗ**:
  ```powershell
  python "c:\Users\phuoc\Downloads\antigravity\Chứng khoán\scripts\paper_trading_simulator.py" sell --symbol MSFT --shares 10 --reason "Dat muc tieu TP1"
  ```

---

## 2. Bảng Tổng Hợp Vị Thế Đang Nắm Giữ (Live Active Positions)

| Mã Cổ Phiếu | Phân Loại | Ngày Mở | Giá Khớp (Entry) | Số Lượng | Tỷ Trọng (% NAV) | Ngưỡng Stop 2xATR | Mục Tiêu TP1 / TP2 | Trạng Thái Hiện Tại | Đánh Giá Kỷ Luật Của Mentor |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **MSFT** | **Core (Tích sản)** | 2026-10-31 | \$520.94 | 10 cp | 5.2% | \$497.46 | \$560.00 / \$580.00 | Đang mở (+0.0%) | Chuẩn kỷ luật Stop 2xATR Quỹ |

---

## 3. Nhật Ký Chi Tiết Từng Lệnh Giao Dịch (Trade Audit Logs)

### Lệnh Số 01: [MSFT — Microsoft Corp]
- **Ngày thực hiện**: 2026-10-31
- **Phân loại chiến lược**: `Core (Tích sản dài hạn)`
- **Loại lệnh**: `Mua mới vị thế mô phỏng Tranche 1 (50% kế hoạch)`
- **Luận điểm vào lệnh**:
  - Đối chiếu Ban 1 (Vĩ mô): VIX > 20 -> Ưu tiên doanh nghiệp pháo đài tiền mặt, Net Cash lớn.
  - Đối chiếu Ban 2 (BCTC & Định giá): Forward P/E 32.4x, FCF Yield 2.8%, Moat đám mây AI vượt trội.
  - Khuyến nghị Ban 4 (Hội đồng Đầu tư): Nằm trong nhóm STRONG BUY / ACCUMULATE.
- **Thông số kỹ thuật & Quản trị rủi ro**:
  - Giá khớp thực tế: \$520.94
  - Số lượng: 10 cổ phiếu (\$5,209.40 USD ~ 5.2% NAV mô phỏng).
  - Ngưỡng Hard Stop-Loss: \$497.46 (Thủng -4.5% đóng lệnh dứt khoát).
  - Tỷ lệ Risk/Reward (R:R) dự kiến: 1:2.5 (Risk \$23.48 vs Reward \$59.06).
- **Tự vấn tâm lý trước khi bấm nút (Psychological Self-Check)**:
  - *Tôi có đang bị hưng phấn (FOMO) không?* -> Không, giải ngân theo tỷ trọng ATR chuẩn.
  - *Tôi có chấp nhận sẵn sàng mất số tiền cắt lỗ kia mà vẫn mỉm cười không?* -> Có, rủi ro chỉ là \$234.80 USD (~0.23% NAV).
  - *Tôi có đang dùng tiền Margin vay nợ không?* -> Không, 100% tiền mặt.
- **Đánh giá của Giảng Viên (`investor-mentorship-coach`)**:
  - *Điểm kỷ luật*: **10 / 10 Điểm**.
  - *Lời nhận xét*: "Tuyệt vời. Bạn đã mở lệnh đầu tiên với tư duy phòng thủ chuẩn mực. Không mua đuổi, xác định rõ điểm cắt lỗ trước khi vào lệnh. Hãy kiên nhẫn quan sát cách thị trường vận động quanh đường MA20!"

---

## 4. Tiêu Chuẩn Tốt Nghiệp Chuyển Sang Vốn Thật (Graduation Criteria)
Để hoàn thành giai đoạn mô phỏng và được Giảng viên phê duyệt chuyển sang giải ngân vốn thật:
1. Thực hiện tối thiểu **15 đến 20 lệnh mô phỏng**.
2. Đạt **Điểm kỷ luật trung bình >= 85/100 Điểm**.
3. **100% lệnh vi phạm phải được cắt lỗ dứt khoát tại Stop 2xATR**, không có ngoại lệ gồng lỗ.
4. Tỷ lệ **Lợi nhuận/Rủi ro (R:R) thực tế đạt >= 1:1.8**.
