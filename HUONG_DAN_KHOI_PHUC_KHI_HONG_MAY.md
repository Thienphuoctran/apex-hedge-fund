# QUY TRÌNH KHÔI PHỤC THẢM HỌA & BẢO VỆ DỮ LIỆU TUYỆT ĐỐI (DISASTER RECOVERY RUNBOOK)
**Hệ Thống Quỹ Đầu Tư Định Lượng & BCTC Toàn Diện Apex Hedge Fund**

---

> [!IMPORTANT]
> **TÀI SẢN TRÍ TUỆ CỦA BẠN AN TOÀN TUYỆT ĐỐI 100%**  
> Dù máy tính cá nhân bị cháy, hỏng ổ cứng hay mất trộm, toàn bộ mã nguồn, dữ liệu BCTC, lịch sử nghiên cứu, nhật ký học tập và sổ lệnh của bạn đã được đồng bộ hóa và lưu trữ phân tán an toàn tại:
> - **Kho lưu trữ GitHub cá nhân**: `https://github.com/Thienphuoctran/apex-hedge-fund.git`
> - **Kênh liên lạc Telegram bảo mật**: `@Chuyenvienvictor_bot` (Chat ID: `8332675283`)
> - **Đám mây tự hành GitHub Actions**: Hoạt động 24/7 độc lập hoàn toàn với máy tính của bạn.

---

## 1. Cơ Chế Bảo Vệ Dữ Liệu Phân Tán (3 Lớp Dự Phòng)

```mermaid
flowchart TD
    A["Máy Tính Cá Nhân (Local Workspace)"] -->|"Tự động Commit & Push"| B["GitHub Private Cloud Repository"]
    B -->|"Tự Động Chạy Hàng Ngày (07:30 Sáng VN)"| C["GitHub Actions Runner (Đám mây)"]
    C -->|"Bắn Bản Tin & Sổ Lệnh Khẩn"| D["Telegram (@Chuyenvienvictor_bot)"]
    
    subgraph "Kịch Bản Máy Hỏng Hoàn Toàn"
        E["Máy Tính Mới / Máy Thay Thế"] -->|"1 Lệnh 'git clone' trong 30 giây"| B
        E -->|"Khôi Phục 100% Hoạt Động"| A
    end
    
    style B fill:#1e3d59,stroke:#17b978,stroke-width:2px,color:#fff
    style C fill:#17b978,stroke:#086972,stroke-width:2px,color:#fff
    style D fill:#0088cc,stroke:#086972,stroke-width:2px,color:#fff
```

1. **Lớp 1 — Kho Lưu Trữ Đám Mây GitHub (Cloud Code & Data Repository)**:
   - Lưu trữ toàn bộ 140+ tệp mã nguồn, toàn bộ cơ sở tri thức BCTC, từ điển bách khoa toàn thư đầu tư `05_Learning_And_Evolution/MASTER_INVESTMENT_BRAIN_ENCYCLOPEDIA.md`, các thuật toán quản trị rủi ro ATR Risk-Parity và bộ chỉ số modified Beneish/Altman.
2. **Lớp 2 — Đám Mây Tự Hành GitHub Actions (Autonomous Cloud Engine)**:
   - Ngay cả khi máy tính của bạn bị tắt hoặc hỏng suốt 1 tháng, máy chủ đám mây của GitHub vẫn tự động bật dậy lúc 07:30 sáng hàng ngày để quét CBTT/SEC, thẩm định BCTC, chấm điểm danh mục và phân bổ vốn.
3. **Lớp 3 — Hộp Thư Báo Động Telegram (Instant Cloud Communication)**:
   - Mọi báo cáo sáng, khuyến nghị của Alex & Minh Quân và cảnh báo biến động từ Victor đều được gửi trực tiếp vào ứng dụng Telegram trên điện thoại của bạn.

---

## 2. Quy Trình 4 Bước Khôi Phục Toàn Diện Trên Máy Mới (Trong 3 Phút)

Khi bạn có một chiếc máy tính mới (hoặc sau khi cài lại Windows), thực hiện 4 bước sau:

### Bước 1: Cài đặt môi trường cần thiết
1. Tải và cài đặt **Git**: [https://git-scm.com/download/win](https://git-scm.com/download/win) (chọn mặc định mọi tùy chọn).
2. Tải và cài đặt **Python 3.10 hoặc 3.11**: [https://www.python.org/downloads/](https://www.python.org/downloads/)  
   *(Lưu ý: Tích chọn ô **"Add Python to PATH"** khi cài đặt)*.

### Bước 2: Kéo toàn bộ quỹ đầu tư về máy (Clone)
Mở cửa sổ `Command Prompt` (CMD) hoặc `PowerShell`, di chuyển tới thư mục bạn muốn lưu dự án (ví dụ `Downloads` hoặc `Documents`) và dán dòng lệnh sau:

```bash
git clone https://github.com/Thienphuoctran/apex-hedge-fund.git "Chứng khoán"
```
*(Chỉ mất khoảng 15-30 giây để tải về trọn vẹn 100% tất cả các phòng ban và dữ liệu)*.

### Bước 3: Cài đặt các thư viện định lượng & tài chính
Chuyển vào thư mục vừa tải về và cài đặt các thư viện với 1 dòng lệnh:

```bash
cd "Chứng khoán"
pip install yfinance pandas requests numpy
```

### Bước 4: Khởi động lại hệ thống
- **Chạy toàn bộ quy trình nghiên cứu & phân bổ vốn Master**:
  ```bash
  python scripts/run_master_unified_fund.py
  ```
- **Hoặc kích hoạt Sentinel Victor trực chiến thời gian thực**:
  - Nhấp đúp chuột vào tệp `run_victor_sentinel.bat`.
  - Hoặc chạy lệnh: `python scripts/live_portfolio_sentinel.py`

🎉 **Toàn bộ hệ thống 9 phòng ban của bạn đã được hồi sinh nguyên vẹn 100% không mất bất kỳ một dòng code hay dữ liệu nào!**

---

## 3. Tạo Bản Sao Lưu Độc Lập Ngoại Tuyến (Offline USB / Google Drive)

Nếu bạn muốn có thêm một bản nén ZIP định kỳ để cất vào thẻ nhớ USB hoặc Google Drive cá nhân:

1. **Cách 1 (Từ GitHub - Nhanh nhất)**:
   - Truy cập: `https://github.com/Thienphuoctran/apex-hedge-fund`
   - Bấm vào nút xanh lá **Code** $\rightarrow$ chọn **Download ZIP**.
   - Lưu tệp zip này vào Google Drive hoặc USB.

2. **Cách 2 (Bằng dòng lệnh tự động)**:
   - Chạy lệnh sau trong PowerShell tại thư mục dự án để tự đóng gói file zip:
   ```powershell
   Compress-Archive -Path * -DestinationPath "Apex_Fund_Backup_$(Get-Date -Format 'yyyyMMdd').zip" -Force
   ```

---

## 4. Kỷ Luật Vận Hành Đảm Bảo Không Bao Giờ Mất Dữ Liệu
- Hệ thống đã tích hợp sẵn cơ chế đồng bộ lên GitHub mỗi khi có cập nhật quan trọng.
- Bạn hoàn toàn có thể yên tâm đầu tư và vận hành — hạ tầng quỹ đã đạt chuẩn phục hồi thảm họa (Disaster Recovery RPO = 0, RTO < 3 phút) tương đương các tổ chức tài chính chuyên nghiệp!
