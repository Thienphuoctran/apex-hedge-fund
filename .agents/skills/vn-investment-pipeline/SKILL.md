---
name: vn-investment-pipeline
description: >-
  Quy trình vận hành Hệ thống 7 Phòng ban AI Agent nghiên cứu chuyên sâu BCTC, ra quyết định đầu tư, tự học hỏi thích nghi, kèm cặp đào tạo thực chiến và chuyên viên thực thi tự tiến hóa mỗi ngày "Minh Quân" (Vietnam Stock Market - Full VAS/TT200 BCTC, T+2.5, Circuit Breakers & Daily Pre-ATO Blotter Suite).
---

# Quy Trình Vận Hành Đội Ngũ 7 Phòng Ban AI Agent Chứng Khoán Việt Nam (VN-Framework v1.0)

Kỹ năng này hướng dẫn thực thi trọn vẹn chu trình nghiên cứu đầu tư định lượng & mổ xẻ Báo cáo Tài chính chuyên sâu 7 phòng ban Việt Nam với cam kết **100% minh bạch, kiểm toán VAS/TT200, đo lường dòng tiền thật OCF/FCF, không bịa đặt số liệu**, tích hợp **Quản trị rủi ro chu kỳ T+2.5**, **Kiểm soát biên độ sàn HOSE (+/-7%) / HNX (+/-10%)**, **Sổ Lệnh Pre-ATO của Chuyên viên Minh Quân lúc 8h30 sáng**, **Interactive HTML Dashboard**, và **Cơ chế Hồi tố & Tự học Tiến hóa Mô hình**.

## Bước 1: Kích Hoạt Bộ Công Cụ Định Lượng, Mổ Xẻ BCTC & Chuyên Viên Minh Quân
Thực thi 1-click trình điều khiển:
```powershell
python "VN_Market\scripts\run_vn_pipeline.py"
```
Bộ script sẽ tuần tự thực thi 8 công đoạn:
1. `vn_market_data_fetcher.py`: Thu thập dữ liệu giao dịch 46 siêu cổ phiếu & vĩ mô SBV.
2. `vn_bctc_analyzer.py`: Mổ xẻ 3 BCTC, FCF, OCF/LNST, M-Score, Z-Score, ĐHCĐ.
3. `vn_audit_and_verify.py`: Kiểm toán số liệu, xuất `audited_briefing_vn.md`.
4. `vn_quant_portfolio.py`: Phân bổ ATR Risk-Parity, stress-test 3 kịch bản, ra nghị quyết Ban 4.
5. `vn_performance_learning.py`: Lưu snapshot, đối soát Walk-Forward Hit Rate %, cập nhật trọng số.
6. `vn_mentor_engine.py`: Phát hành bản tin khai sáng 7h30 sáng Ban 6.
7. `vn_daily_specialist.py`: Kích hoạt Giao ban 8h30, chuyên viên Minh Quân lập sổ lệnh trước ATO.
8. `generate_vn_dashboard.py`: Xuất bản Dashboard tương tác tại `VN_Market/dashboard/index.html`.

## Bước 2: Ban 1 VN — Phân Tích Vĩ Mô & Luân Chuyển Ngành (`vn-macro-monetary-agent`)
- Phân tích động thái SBV (Lãi suất, Tín phiếu, OMO, Tỷ giá USD/VND, Tăng trưởng tín dụng).
- Phân tích Dòng tiền 3 Khối: Khối Ngoại, Tự Doanh CTCK, Dư nợ Margin toàn thị trường.
- Xác định Sector Tailwind / Headwind trong 12 nhóm ngành kinh tế VN.
- Báo cáo tại: `VN_Market/01_Macro_Monetary_Vietnam/YYYY-MM-DD_VN_Macro_Report.md`.

## Bước 3: Ban 2 VN — Thẩm Định BCTC & Báo Cáo Kinh Doanh (`vn-equity-bctc-agent`)
- Mổ xẻ chi tiết 3 Báo cáo Tài chính + Bản Thuyết minh BCTC + Nghị quyết ĐHCĐ.
- Đo lường Tiền Thật ($OCF / LNST$), Dòng tiền tự do $FCF$, Hệ số nợ $D/E$, $Z''$-Score, $M$-Score.
- Phán đoán 4 nhóm: `BULLISH`, `TACTICAL_REBOUND`, `OVERBOUGHT_PULLBACK`, `BEARISH_TRAP`.
- Báo cáo tại: `VN_Market/02_BCTC_Equity_Research/YYYY-MM-DD_VN_Equity_Analysis.md`.

## Bước 4: Ban 3 VN — Phòng Tổng Hợp & Sàng Lọc Cơ Hội (`vn-synthesis-hub-agent`)
- Đối soát chéo Top-Down (Vĩ mô) và Bottom-Up (BCTC).
- Lập 2 bảng sàng lọc: Top Cổ Phiếu Tiềm Năng Tăng Trưởng vs Cảnh Báo Bẫy Tài Chính.
- Báo cáo tại: `VN_Market/03_Synthesis_Memos/YYYY-MM-DD_VN_Investment_Memo.md`.

## Bước 5: Ban 4 VN — Hội Đồng Đầu Tư & Quản Trị Rủi Ro (`vn-investment-committee-agent`)
- Chấm điểm cơ hội đầu tư trên thang 100 điểm.
- Định cỡ vị thế theo `ATR Risk-Parity`, kiểm soát biên độ sàn và rủi ro chu kỳ T+2.5.
- Cắt lỗ bắt buộc $Stop = 2 \times ATR(14)$.
- Kiểm thử Stress-Test 3 kịch bản khủng hoảng.
- Báo cáo tại: `VN_Market/04_Investment_Committee/YYYY-MM-DD_VN_IC_Decision.md` và `vn_portfolio_tracker.md`.

## Bước 6: Ban 5 VN — Phòng Thẩm Định Hiệu Suất & Tự Học (`vn-performance-learning-agent`)
- Lưu trữ Snapshot lịch sử giao dịch.
- Đo lường Hit Rate % tại các mốc T+3, T+5, T+10, T+20.
- Bóc tách nguyên nhân hiệu suất (Alpha vs Beta vs Timing).
- Tự học & Tinh chỉnh trọng số trong `VN_Market/config/adaptive_weights_vn.json`.
- Báo cáo tại: `VN_Market/05_Learning_And_Evolution/YYYY-MM-DD_VN_Learning_Report.md`.

## Bước 7: Ban 6 VN — Học Viện Huấn Luyện & Đào Tạo Thực Chiến (`vn-investor-mentorship-coach`)
- Phát hành Bản tin Khai sáng Buổi sáng lúc **7h30 Sáng**: `VN_Market/06_Investor_Academy/daily_mentorship/YYYY-MM-DD_VN_Mentor_Briefing.md`.
- Đào tạo cách đọc BCTC thực chiến, giải mã các "chiêu trò" làm đẹp số liệu.
- Kèm cặp tâm lý tránh fomo mở phiên ATO, kiểm toán sổ tay giao dịch cá nhân.

## Bước 8: Ban 7 VN — Chuyên Viên Đầu Tư Trưởng "Minh Quân" (`vn-daily-specialist-agent`)
- **Thời điểm kích hoạt**: **8h30 Sáng Hàng Ngày** (30 phút trước khi thị trường mở phiên ATO lúc 9h00).
- **Hội nghị giao ban 8h30**: Lắng nghe Ban 1-6 và ý kiến của Nhà đầu tư.
- **Tự kiểm điểm phiên hôm qua (Yesterday Autopsy)**: Ghi nhật ký tiến hóa vào `vn_specialist_evolution_journal.md`.
- **Ra quyết định đầu tư khoa học**: Lập sổ lệnh thực thi với Kỳ vọng Toán học $EV\% > 0$, tỷ lệ $R:R \ge 1:2$, chiến lược chia nhịp 60/40.
- Báo cáo tại: `VN_Market/07_Daily_Specialist/YYYY-MM-DD_VN_Specialist_Decision.md`.
