---
name: global-investment-pipeline
description: >-
  Quy trình vận hành Hệ thống 7 Phòng ban AI Agent nghiên cứu, ra quyết định đầu tư, tự học hỏi thích nghi, kèm cặp đào tạo thực chiến và chuyên viên đầu tư thực thi tự tiến hóa mỗi ngày (US/Global Markets - Audited v6.0 Full Quantitative, Adaptive Learning, Mentorship & Daily Investment Specialist Suite).
---

# Quy Trình Vận Hành Đội Ngũ 7 Phòng Ban AI Agent Đầu Tư Quốc Tế (Audited v6.0 — Full Institutional Suite, Mentorship & Daily Specialist)

Kỹ năng này hướng dẫn thực thi trọn vẹn chu trình nghiên cứu đầu tư định lượng & cơ bản 7 phòng ban với cam kết **100% minh bạch, chuẩn hóa tỷ giá USD, không bịa đặt số liệu**, tích hợp **Radar Lịch BCTC**, **Theo dõi Giao dịch Nội bộ SEC Form 4**, **Ma trận Tương quan & Định cỡ Vị thế ATR Risk-Parity**, **Kiểm thử Stress-Test 3 Kịch bản**, **Interactive HTML Dashboard**, **Cơ chế Hồi tố & Tự học Tiến hóa Mô hình**, **Học Viện Đào Tạo Kèm Cặp Thực Chiến 1:1**, và **Chuyên Viên Đầu Tư Tự Học & Tối Ưu Lợi Nhuận Mỗi Ngày (Ban 7)**.

## Bước 1: Chạy Bộ 7 Công Cụ Định Lượng, Kiểm Toán, Tự Học, Huấn Luyện & Chuyên Viên Đầu Tư Hàng Ngày
Thực thi tuần tự 7 script Python chuẩn hóa (hoặc chạy `python scripts/run_daily_pipeline.py --fast`):
```powershell
python "c:\Users\phuoc\Downloads\antigravity\Chứng khoán\scripts\market_data_fetcher.py"
python "c:\Users\phuoc\Downloads\antigravity\Chứng khoán\scripts\audit_and_verify.py"
python "c:\Users\phuoc\Downloads\antigravity\Chứng khoán\scripts\quant_portfolio_engine.py"
python "c:\Users\phuoc\Downloads\antigravity\Chứng khoán\scripts\performance_learning_engine.py"
python "c:\Users\phuoc\Downloads\antigravity\Chứng khoán\scripts\mentor_engine.py"
python "c:\Users\phuoc\Downloads\antigravity\Chứng khoán\scripts\daily_investment_specialist.py"
python "c:\Users\phuoc\Downloads\antigravity\Chứng khoán\scripts\generate_dashboard.py"
```
Đọc trực tiếp bảng kiểm toán tại `data/audited_briefing.md`, báo cáo rủi ro định lượng tại `04_Investment_Committee/YYYY-MM-DD_Quant_Risk_And_Correlation.md` và bản tin huấn luyện tại `06_Investor_Academy_And_Mentorship/daily_mentorship/YYYY-MM-DD_Mentor_Briefing.md`.

## Bước 2: Ban 1 — Phân Tích Vĩ Mô & Địa Chính Trị Toàn Cầu (`macro-geopolitics-agent`)
- Phân tích 8 chỉ số chứng khoán Mỹ, Châu Âu, Châu Á (`^GSPC`, `^IXIC`, `^DJI`, `^RUT`, `^N225`, `^GDAXI`, `^FTSE`, `^HSI`).
- Phân tích 6 thước đo vĩ mô & hàng hóa (`^VIX`, `^TNX`, `DX-Y.NYB`, `GC=F`, `CL=F`, `BTC-USD`).
- Xếp hạng dòng tiền toàn bộ 12 ETF nhóm ngành chuẩn GICS kèm chỉ số **Sharpe Ratio 1Y**.
- Lưu báo cáo tại `01_Macro_Geopolitics/YYYY-MM-DD_Macro_Report.md`.

## Bước 3: Ban 2 — Phân Tích Doanh Nghiệp, BCTC, Radar Sự Kiện & Dự Báo Giá (`equity-fundamental-agent`)
- Đánh giá toàn diện vũ trụ 35 cổ phiếu quốc tế trong `data/audited_briefing.md` (kèm **Radar Lịch BCTC** và **Dòng tiền Sở hữu Tổ chức / Giao dịch Nội bộ SEC Form 4**).
- Phân tách rõ 4 nhóm phán đoán định lượng:
  1. **Nhóm Dự Báo TĂNG — Dẫn Dắt Xu Hướng (`BULLISH — Uptrend Leaders`)**
  2. **Nhóm Quá Bán Chờ Phục Hồi Kỹ Thuật (`TACTICAL REBOUND — Oversold Value`)**
  3. **Nhóm Cảnh Báo Quá Mua — Chờ Chỉnh Về MA20 (`OVERBOUGHT PULLBACK ALERTS`)**
  4. **Nhóm Dự Báo GIẢM / Rủi Ro Cao (`BEARISH / HIGH-RISK TRAPS`)**
- Lưu báo cáo tại `02_Equity_Research/YYYY-MM-DD_Equity_Analysis.md`.

## Bước 4: Ban 3 — Phòng Tổng Hợp & Điều Phối (`synthesis-hub-agent`)
- Đối soát chéo Top-Down (Ban 1) và Bottom-Up (Ban 2), loại trừ các cổ phiếu sắp ra BCTC trong vòng <= 7 ngày khỏi danh sách mua đuổi.
- Lập bản **Investment Memo** hoàn chỉnh lưu tại `03_Synthesis_Memos/YYYY-MM-DD_Investment_Memo.md`.

## Bước 5: Ban 4 — Hội Đồng Đầu Tư & Quản Trị Rủi Ro Định Lượng (`investment-committee-agent`)
- Chấm điểm trên thang 100 điểm, ra quyết định hành động (`STRONG BUY / ACCUMULATE / BUY ON DIP / WATCH / AVOID`).
- Áp dụng **Tỷ trọng Định cỡ Vị thế theo Độ biến động (`ATR Risk-Parity Position Sizing`)**, kiểm soát **Cụm Tương quan Cao (`Correlation Cluster Cap`)**, thiết lập **Ngưỡng Cắt lỗ `Stop 2xATR(14)`** và đính kèm kết quả **Kiểm thử Stress-Test 3 Kịch bản**.
- Lưu quyết định tại `04_Investment_Committee/YYYY-MM-DD_IC_Decision.md`, báo cáo định lượng tại `04_Investment_Committee/YYYY-MM-DD_Quant_Risk_And_Correlation.md`, và cập nhật `04_Investment_Committee/portfolio_tracker.md`.

## Bước 6: Ban 5 — Phòng Thẩm Định Hiệu Suất, Hồi Tố & Tự Học Thích Nghi (`performance-learning-agent`)
- **Lưu trữ Lịch sử (`Historical Archiving`)**: Lưu bản chụp dữ liệu ngày vào `05_Learning_And_Evolution/historical_archive/snapshot_YYYY-MM-DD.json`.
- **Hồi tố & Đối soát Dự báo vs Thực tế (`Walk-Forward Post-Mortem`)**: Kiểm tra các dự báo của những phiên trước xem có đúng xu hướng không, tính toán **Hit Rate % (Tỷ lệ dự báo chuẩn xác)** và kiểm tra xem có vị thế nào chạm Stop-Loss hoặc Take-Profit không.
- **Tự Học & Tinh Chỉnh Thích Nghi**: Đúc rút bài học kinh nghiệm thị trường vào `05_Learning_And_Evolution/system_evolution_journal.md`, tự động cập nhật trọng số chấm điểm trong `config/adaptive_weights.json` và xuất báo cáo ngày tại `05_Learning_And_Evolution/YYYY-MM-DD_Learning_And_Attribution_Report.md`.

## Bước 7: Ban 6 — Học Viện Đào Tạo Thực Chiến & Huấn Luyện Viên Cá Nhân (`investor-mentorship-coach`)
- **Phát hành Bản tin Khai sáng Buổi sáng (7h30 AM)**: Tự động chạy `scripts/mentor_engine.py` để biên soạn bài học vi mô trong ngày, giải mã tình huống giao dịch thực tế từ danh mục Ban 4, và đưa ra câu hỏi tư duy phản biện Socratic tại `06_Investor_Academy_And_Mentorship/daily_mentorship/YYYY-MM-DD_Mentor_Briefing.md`.
- **Kèm cặp Tư duy & Tâm lý Giao dịch (Real-Time Co-Pilot)**: Trực tiếp trả lời, giải thích cặn kẽ mọi khái niệm tài chính, kiểm soát các phản ứng tâm lý (FOMO, sợ cắt lỗ, bắt dao rơi).
- **Kiểm toán Sổ tay Lệnh Cá nhân**: Định kỳ rà soát `06_Investor_Academy_And_Mentorship/user_journal/personal_trading_journal.md`, chấm điểm kỷ luật cá nhân, và cập nhật tiến độ học tập vào `student_profile.json`.

## Bước 8: Ban 7 — Chuyên Viên Đầu Tư & Thực Thi Tự Tiến Hóa Mỗi Ngày (`daily-investment-specialist-agent`) — Kích Hoạt Lúc 8h30 Sáng
- **Thời điểm kích hoạt**: **8h30 Sáng Mỗi Ngày** (Dành khoảng đệm 60 phút từ 7h30 đến 8h30 để Nhà đầu tư đọc kỹ toàn bộ BCTC và báo cáo phân tích trước đó).
- **Hội Nghị Giao Ban Đầu Ngày (`Inter-Departmental Hearing lúc 8h30`)**: Lắng nghe và tổng hợp nhận xét từ cả 6 Phòng ban (Ban 1 -> Ban 6) kết hợp ý kiến phản hồi của Nhà đầu tư sau khi đọc BCTC.
- **Tự Kiểm Điểm Ngày Hôm Qua & Tối Ưu Hóa Lợi Nhuận (`Yesterday Post-Mortem & Profit Optimization`)**: Chạy `scripts/daily_investment_specialist.py` để đối soát phiên hôm qua với phiên hôm nay, chỉ rõ chỗ đúng, chỗ sai (`Commission Errors`), chỗ còn thiếu sót (`Omission Errors vs Disciplined Pass`), và nạp các quy tắc tối ưu lợi nhuận mới (`60/40 ATR Pullback Limit`, `Tactical Alpha Sleeve`, `Dynamic Profit Ratchet`).
- **Quyết Định Đầu Tư Khoa Học Trong Ngày (`Scientific Daily Order Blotter`)**: Tính toán Kỳ vọng Toán học (`Expected Value EV%`), Xác suất thắng `P(W)` và xuất báo cáo tại `07_Daily_Investment_Specialist/YYYY-MM-DD_Daily_Specialist_Decision.md`, cập nhật `specialist_evolution_journal.md` và `daily_specialist_ledger.json`.
