# HỒ SƠ ĐÓNG BĂNG DỰ ÁN: NÂNG CẤP VŨ TRANG AGENT ZERO CORE SUITE CHO 11 PHÒNG BAN
*Mã dự án*: `APEX-PRJ-AGENT-ZERO-V1`  
*Trạng thái*: **TẠM TREO THEO LỆNH CHỦ TỊCH PHƯỚC TRẦN (FROZEN ON-HOLD)**  
*Thời điểm đóng băng*: **04/11/2026 lúc 14:12**  
*Thời điểm kích hoạt triển khai*: **Đúng 3 ngày sau — 07/11/2026 (Sau khi Quota Token Tuần Reset)**  
*Kiến trúc sư trưởng*: **Palmer** | *Tổng tư lệnh phê duyệt*: **Master CIO James**  
*Phục vụ trực tiếp*: **Chủ tịch Phước Trần (Tài khoản TCBS: `105C307855`)**

---

## 🎯 I. MỤC TIÊU VÀ NGUYÊN TẮC THI CÔNG KHI MỞ LẠI DỰ ÁN (07/11/2026)
1. **Tuyệt đối không làm sơ sài, chắp vá**: Mọi mô-đun phải được viết chuẩn mực Python 3, kiểm thử đầy đủ qua unit test, không gây lỗi cú pháp, không làm ảnh hưởng xấu hay đứt gãy 17 mốc tác chiến đang chạy.
2. **Bảo tồn toàn bộ chức năng hiện tại**: Các phòng ban cũ (Hiền BCTC, Khánh Video, Minh Quân Sổ lệnh, Victor Sentinel) vẫn giữ nguyên nghiệp vụ cốt lõi, Agent Zero chỉ đóng vai trò là "Vũ khí khuếch đại sức mạnh chuyên môn".
3. **Chuyên nghiệp và đẳng cấp thể chế**: Đạt chuẩn Hedge Fund định lượng quốc tế.

---

## 🏰 II. KIẾN TRÚC 4 VŨ KHÍ AGENT ZERO CORE ĐÃ QUY HOẠCH

### 1. Module 1: `ZeroBrowserScout` (Trinh Sát Web Độc Lập Vượt Tường Lửa)
* **Phân bổ**: **Ban 1 (Vĩ Mô SBV)** & **Ban 10 (Hiền BCTC & IR)**.
* **Nhiệm vụ chi tiết**:
  - Ban 1: Cào trực tiếp tỷ giá trung tâm, kết quả đấu thầu OMO/Tín phiếu từ Cổng Ngân hàng Nhà nước `sbv.gov.vn` lúc 06:30 sáng.
  - Ban 10: Tự động lướt các cổng SSC (UBCKNN), Sở GDCK HOSE/HNX và Cổng IR của 54 siêu cổ phiếu để lấy link file PDF BCTC có dấu mộc đỏ gốc.
* **Công nghệ**: Giả lập Chrome Browser Engine, cơ chế xoay vòng User-Agent, xử lý Cookie phiên, bộ lọc Anti-404 URL Validation (chỉ nhận link HTTP 200).

### 2. Module 2: `ZeroForensicParser` (Cỗ Máy Mổ Xẻ BCTC Từ PDF Tự Động)
* **Phân bổ**: **Ban 2 (Thẩm Định BCTC)** & **Ban 8 (Master CIO James)**.
* **Nhiệm vụ chi tiết**:
  - Tự động quét các tệp PDF Báo cáo Tài chính, nhận diện bảng biểu (Bảng Cân đối kế toán, Báo cáo KQKD, Báo cáo Lưu chuyển tiền tệ).
  - Trích xuất tự động các chỉ số: Doanh thu, Lợi nhuận sau thuế ($LNST$), Dòng tiền thuần từ HĐKD ($OCF$), Tiền mặt, Nợ vay, Chi phí xây dựng dở dang.
  - Tính toán tự động và kiểm toán số học:
    $$\text{Tỷ lệ Tiền Thật} = \frac{OCF}{LNST} \ge 1.0x$$
    $$\text{Beneish M-Score} \le -1.78 \quad \text{và} \quad \text{Altman Z''-Score} \ge 1.10$$
  - Loại bỏ hoàn toàn công đoạn nhập liệu thủ công bằng tay.

### 3. Module 3: `ZeroMarketWatcher` (Radar Bảng Điện Đa Nguồn & Bóc Trần Lệnh Ảo)
* **Phân bổ**: **Ban 3 (Săn Sóng Alpha)**, **Ban 7 (Minh Quân)** & **Ban 9 (Victor Sentinel)**.
* **Nhiệm vụ chi tiết**:
  - Ban 3: Đo lường chính xác tỷ lệ Khớp lệnh Mua chủ động (Buy Up $\ge 70\%$) và nhận diện nến Test Cung VSA.
  - Ban 7: Quét sổ lệnh trước giờ ATO (09h00) và trước giờ ATC (14h25), phát hiện chiêu trò kê lệnh ảo ở Giá 2/Giá 3 để dụ cầu nhỏ lẻ.
  - Ban 9: Kết nối cơ chế **Multi-Source Failover** 3 luồng (VPS API $\leftrightarrow$ TCBS Data Feed $\leftrightarrow$ SSI Web Stream) giúp Victor không bao giờ bị "mù dữ liệu" khi một bên bảo trì mạng.

### 4. Module 4: `ZeroMediaHarvester` (Thu Thập Tư Liệu Đa Phương Tiện Cho Video)
* **Phân bổ**: **Ban 11 (Khánh & Bảo)** & **Ban 6 (Coach)**.
* **Nhiệm vụ chi tiết**:
  - Tự động cào tư liệu hình ảnh thực tế (ảnh lò cao Dung Quất của Hòa Phát, cảng nước sâu Gemalink của Gemadept, nhà máy hóa chất của Đức Giang) theo kịch bản của Khánh.
  - Tải logo PNG trong suốt chuẩn xác của doanh nghiệp, sơ đồ BCTC trực quan và chuyển thẳng vào thư mục làm việc của Bảo để lồng ghép vào Video TikTok/Reels 9:16.

---

## 📅 III. LỘ TRÌNH TRIỂN KHAI VÀO NGÀY 07/11/2026 (KHUNG GIỜ & THỨ TỰ BẮT BUỘC)

Khi Chủ tịch kích hoạt lại vào ngày 07/11/2026, hệ thống sẽ thực hiện theo 3 giai đoạn khép kín:

| Giai Đoạn | Thời Gian Thực Hiện | Nội Dung Công Việc | Tiêu Chuẩn Nghiệm Thu |
| :---: | :--- | :--- | :--- |
| **Giai đoạn 1** | Buổi sáng 07/11/2026 | Viết module lõi `scripts/apex_agent_zero_engine.py` đóng gói đủ 4 class chức năng | Chạy kiểm thử độc lập 100% Passed, không lỗi thư viện |
| **Giai đoạn 2** | Đầu giờ chiều 07/11/2026 | Tích hợp vào Ban 1 (SBV), Ban 10 (Hiền BCTC) và Ban 2 (Forensic) | Cào thử nghiệm thành công 3 BCTC của HPG, TCB, MBB có trích xuất bảng OCF |
| **Giai đoạn 3** | Cuối giờ chiều 07/11/2026 | Tích hợp vào Ban 7 (Minh Quân), Ban 9 (Victor) và Ban 11 (Khánh & Bảo) | Kiểm tra trực quan trên FounderOS Dashboard và nộp báo cáo hoàn thiện cho Chủ tịch |

---

## 🔒 IV. CAM KẾT DANH DỰ CỦA PALMER & HỘI ĐỒNG QUỸ
- **Không bao giờ quên**: Hồ sơ này được lưu trữ vĩnh viễn trên ổ đĩa vật lý và Git repository. Đúng 3 ngày nữa, khi Chủ tịch mở chat ra, Palmer sẽ lập tức đọc lại toàn bộ hồ sơ này và báo cáo kế hoạch bấm nút thi công ngay.
- **Không làm sơ sài**: Toàn bộ kiến trúc đã được thiết kế chuẩn xác đến từng tên hàm, tên tệp tin và từng tham số.
- **Bảo toàn token tuần này**: Tất cả các tiến trình cron daemon 24/7 của Quỹ ngoài nền vẫn chạy âm thầm phục vụ Chủ tịch mà **hoàn toàn không tiêu tốn 1 token Antigravity nào**!
