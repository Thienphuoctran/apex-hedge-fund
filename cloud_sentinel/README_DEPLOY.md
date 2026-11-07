# HƯỚNG DẪN TRIỂN KHAI APEX CLOUD SENTINEL 24/7 & HỆ THỐNG QUỸ TRÊN CLOUD
*(Tắt máy tính cá nhân 100% — Toàn bộ Hệ Thống & Victor Sentinel vẫn trực chiến 24/7 trên Cloud, dữ liệu đồng bộ chuẩn xác tuyệt đối)*

Hệ thống đã được nâng cấp lên **Kiến Trúc Đơn Nguồn Sự Thật Chuẩn Mực (Single Source of Truth SSOT V2.0)** tích hợp **Temporal Awareness & Episodic Memory**:
- **Chủ tài khoản**: Chủ tịch Trần Quốc Thiên Phước (TCBS: `105C307855`).
- **Tình trạng tài sản thực tế**: **100% Tiền mặt (`20,167,119 ₫`)**, **`0 CP` rủi ro**.
- **Lịch sử Vòng 1**: Đã tất toán chốt lời 100% (HPG 400 CP, TCB 300 CP, MBB 200 CP), lãi ròng thực nhận **`+167,119 ₫`**.
- **Tầm ngắm Vòng 2**: Radar rà soát FPT, DGC, HPG, TCB chờ điểm mua bứt phá chuẩn xác.

---

## 🌟 PHƯƠNG ÁN 1: GITHUB ACTIONS 24/7 (ĐÃ CÀI SẴN TRONG REPO — 100% TỰ ĐỘNG & MIỄN PHÍ)

Hệ thống đã có sẵn workflow tự động chạy trên hạ tầng đám mây của GitHub:
- **File cấu hình**: `.github/workflows/apex_cloud_sentinel_247.yml` và `.github/workflows/apex_nightly_autonomous_fund.yml`.
- **Lịch chạy tự động**:
  * Mỗi 30 phút trong phiên giao dịch HOSE/HNX (08h00 - 15h30 VN, Thứ 2 - Thứ 6).
  * 20h00 Tối Chủ Nhật: Master CIO James họp tổng duyệt tuần mới.
  * 07h30 Sáng (Thứ 2 - Thứ 6): Bản tin khai sáng & Sổ lệnh sáng sớm gửi điện thoại.
  * 15h15 Chiều (Thứ 2 - Thứ 6): Tự động chốt phiên và học tập thích nghi.
- **Bấm chạy thủ công từ điện thoại (Manual 1-Click)**:
  1. Mở ứng dụng **GitHub Mobile** trên điện thoại (hoặc vào web repo `https://github.com/Thienphuoctran/apex-hedge-fund`).
  2. Bấm tab **Actions** ➔ Chọn **Apex Cloud Sentinel 24/7 & Institutional SSOT Guardian**.
  3. Bấm nút **Run workflow** ➔ Hệ thống sẽ tự động quét toàn vẹn tài sản và kiểm toán chỉ trong 60 giây!

---

## 🚀 PHƯƠNG ÁN 2: TRIỂN KHAI WEB DASHBOARD LIVE 24/7 TRÊN RENDER.COM (100% MIỄN PHÍ)

Nếu Chủ tịch muốn có một trang Web Dashboard trực quan chạy liên tục trên mạng (để mở xem số dư và radar bất cứ lúc nào từ trình duyệt điện thoại Safari / Chrome):

1. **Đăng nhập Render**:
   - Truy cập [https://render.com](https://render.com) và chọn **Sign in with GitHub**.
2. **Tạo Web Service Mới**:
   - Bấm nút **New +** ở góc trên ➔ Chọn **Web Service**.
   - Chọn repository: `Thienphuoctran/apex-hedge-fund`.
3. **Cấu hình thông số (chỉ mất 1 phút)**:
   - **Name**: `apex-sentinel-dashboard` (hoặc tên tùy chọn).
   - **Region**: `Singapore` (để kết nối về VN nhanh nhất).
   - **Root Directory**: `cloud_sentinel`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: Chọn **Free** (Miễn phí vĩnh viễn).
4. **Bấm "Deploy Web Service"**:
   - Render sẽ tự động dựng Web Dashboard trong 2 phút.
   - Chủ tịch sẽ nhận được 1 đường link riêng, ví dụ: `https://apex-sentinel-dashboard.onrender.com`.
   - Mở link trên điện thoại: Xem trực tiếp biểu đồ tài sản 20,167,119 ₫, trạng thái 100% Tiền Mặt, lịch sử Vòng 1 và radar Vòng 2!

*(Mẹo giữ server không ngủ: Dùng dịch vụ miễn phí [cron-job.org](https://cron-job.org) ping vào URL `https://apex-sentinel-dashboard.onrender.com/api/health` mỗi 10 phút).*

---

## 🏆 PHƯƠNG ÁN 3: HUGGING FACE SPACES (DOCKER 24/7 MIỄN PHÍ, 16GB RAM)

1. Truy cập [https://huggingface.co/new-space](https://huggingface.co/new-space).
2. Đặt tên Space: `apex-sentinel` ➔ Chọn SDK: **Docker** ➔ Chọn **Blank**.
3. Tải các file trong thư mục `cloud_sentinel/` lên (bao gồm `Dockerfile`, `main.py`, `portfolio_data.json`, `current_portfolio_state.json`, `requirements.txt`).
4. Bấm **Commit changes** ➔ Dashboard sẽ online 24/7 ngay lập tức.

---

## 🔒 NGUYÊN TẮC BẢO MẬT VÀ TOÀN VẸN DỮ LIỆU
1. **Zero Secret Leak**: Mật khẩu, token cá nhân và file `.env.tcbs` được bảo vệ bằng `.gitignore`, **tuyệt đối không bao giờ bị đẩy lên GitHub**.
2. **Chế Độ Chỉ Đọc (Read-Only Air-Gap)**: Mã nguồn trên Cloud chỉ có quyền đọc dữ liệu bảng giá và đồng bộ hóa báo cáo, hoàn toàn không có quyền rút tiền hay chuyển khoản. Mọi giao dịch tiền mặt bắt buộc phải có Smart OTP trên điện thoại của Chủ tịch Phước Trần.
