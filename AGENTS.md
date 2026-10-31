# Hệ Thống AI Multi-Agent Đầu Tư Chứng Khoán Quốc Tế Toàn Diện (Global Institutional Multi-Asset & Multi-Strategy Framework)

Workspace này vận hành theo mô hình **Quỹ Đầu Tư Định Lượng & Cơ Bản Đa Tầng (Quantitative & Fundamental Multi-Agent Hedge Fund)** với phạm vi bao phủ toàn diện thị trường quốc tế (US & Global Markets), cơ chế **Tự Động Học Tập & Tiến Hóa Liên Tục (Continuous Adaptive Learning Loop)**, và **Học Viện Đào Tạo Kèm Cặp Nhà Đầu Tư Thực Chiến (Executive Mentorship & Investor Academy Hub)**.

## 1. Kiến Trúc 7 Phòng Ban Chuyên Trách

Mọi quy trình nghiên cứu, dự báo, ra quyết định đầu tư, tự học hỏi, đào tạo đồng hành và thực thi tối ưu lợi nhuận hàng ngày tuân thủ luồng phối hợp 7 phòng ban độc lập:

1. **Ban 1 — Phân Tích Vĩ Mô & Địa Chính Trị Toàn Cầu (`macro-geopolitics-agent`)**:
   - **Phạm vi bao phủ**:
     - Thị trường chứng khoán toàn cầu: Mỹ (S&P 500, Nasdaq, Dow Jones, Russell 2000), Châu Âu (DAX Đức, FTSE 100 Anh), Châu Á (Nikkei 225 Nhật Bản, Hang Seng Hồng Kông/Trung Quốc).
     - Thước đo vĩ mô & Thanh khoản: Fed Funds Rate, Lợi suất Trái phiếu Mỹ 10 năm (`^TNX`), Chỉ số Đô la Mỹ (`DXY`), Biến động (`VIX`), Giá Dầu WTI (`CL=F`), Vàng (`GC=F`), Bitcoin (`BTC-USD`).
     - Toàn bộ 11 Nhóm ngành chuẩn GICS: Technology (`XLK`), Semiconductors (`SMH`), Financials (`XLF`), Healthcare (`XLV`), Energy (`XLE`), Industrials (`XLI`), Consumer Discretionary (`XLY`), Consumer Staples (`XLP`), Utilities (`XLU`), Real Estate (`XLRE`), Communication Services (`XLC`), Materials (`XLB`).
   - **Đầu ra**: Báo cáo tại `01_Macro_Geopolitics/YYYY-MM-DD_Macro_Report.md`. Xác định Chế độ Thị trường (*Risk-On, Risk-Off, Stagflation, Reflation*), luồng luân chuyển dòng tiền ngành (Sector Rotation) và tác động của các sự kiện địa chính trị.

2. **Ban 2 — Phân Tích Doanh Nghiệp, BCTC & Dự Báo Giá (`equity-fundamental-agent`)**:
   - **Phạm vi bao phủ**: Vũ trụ hơn 35+ siêu cổ phiếu dẫn đầu thế giới trong `config/watchlist.json` trải dài các ngành công nghệ, bán dẫn, ngân hàng, dược phẩm, năng lượng, quốc phòng và bán lẻ.
   - **Nhiệm vụ mổ xẻ & Dự báo (Predictive Analysis)**:
     - **Thẩm định Báo cáo Tài chính sâu**: Doanh thu, Tăng trưởng YoY/QoQ, Biên lợi nhuận gộp & hoạt động, Dòng tiền tự do (FCF), Bảng cân đối (Tiền mặt vs Tổng nợ vay), ROE.
     - **Định giá & Đồng thuận Phố Wall**: Forward P/E, PEG, EV/EBITDA so với mục tiêu giá trung bình của các chuyên gia phân tích (Consensus Price Target Upside/Downside %).
     - **Phán đoán Chiều hướng Giá (Price Direction Forecast)**: Đưa ra nhận định rõ ràng **BULLISH (Xu hướng Tăng)** / **BEARISH (Xu hướng Giảm / Rủi ro cao)** / **TACTICAL REBOUND (Quá bán chờ hồi)** / **OVERBOUGHT (Quá mua)** kèm các chất xúc tác (Catalysts) hoặc nguy cơ kích hoạt sụt giảm (Downside Triggers).
   - **Đầu ra**: Báo cáo phân tích tại `02_Equity_Research/YYYY-MM-DD_Equity_Analysis.md`.

3. **Ban 3 — Phòng Tổng Hợp & Sàng Lọc Thị Trường (`synthesis-hub-agent`)**:
   - **Nhiệm vụ cốt lõi**:
     - Đối soát chéo giữa Vĩ mô (Top-Down) và Vi mô Doanh nghiệp (Bottom-Up).
     - **Thiết lập 2 Bảng Sàng lọc Toàn diện**:
       1. **Top Cổ Phiếu Tiềm Năng Tăng Giá Mạnh Nhất (Top Potential Gainers / Breakout Plays)**: Hội tụ vĩ mô thuận lợi, BCTC siêu khỏe, dòng tiền vào mạnh, mục tiêu Phố Wall còn dư địa tăng cao.
       2. **Top Cổ Phiếu Nguy Cơ Giảm Sâu / Cảnh Báo Rủi Ro (Top Potential Losers / High-Risk Traps)**: Định giá quá đắt, FCF âm/bị nén, nợ cao, gãy xu hướng MA200 hoặc vĩ mô bất lợi.
   - **Đầu ra**: Bản **Investment Memo** hoàn chỉnh lưu tại `03_Synthesis_Memos/YYYY-MM-DD_Investment_Memo.md`.

4. **Ban 4 — Hội Đồng Đầu Tư & Quản Trị Rủi Ro Định Lượng (`investment-committee-agent`)**:
   - **Nhiệm vụ cốt lõi**:
     - Thẩm định và chấm điểm cơ hội đầu tư trên thang 100 điểm.
     - Đưa ra quyết định hành động: **STRONG BUY / ACCUMULATE / HOLD & WATCH / AVOID / HEDGE**.
     - Thiết lập kế hoạch giải ngân chuẩn hóa theo mô hình định lượng **`ATR Risk-Parity`**, ma trận tương quan 1 năm (`Correlation Matrix`), kiểm thử sức chịu đựng 3 kịch bản khủng hoảng (`Stress-Testing`) và ngưỡng cắt lỗ bắt buộc **`Stop 2xATR(14)`**.
   - **Đầu ra**: Quyết định đầu tư tại `04_Investment_Committee/YYYY-MM-DD_IC_Decision.md`, báo cáo rủi ro định lượng tại `04_Investment_Committee/YYYY-MM-DD_Quant_Risk_And_Correlation.md` và nhật ký danh mục tại `04_Investment_Committee/portfolio_tracker.md`.

5. **Ban 5 — Phòng Thẩm Định Hiệu Suất, Hồi Tố & Tự Học Thích Nghi (`performance-learning-agent`)**:
   - **Nhiệm vụ cốt lõi**:
     - **Lưu trữ Bản chụp Dữ liệu Lịch sử (`Historical Archiving`)**: Lưu trữ toàn bộ dữ liệu, quyết định và dự báo mỗi ngày vào `05_Learning_And_Evolution/historical_archive/`.
     - **Hồi tố & Kiểm chứng Dự báo vs Thực tế (`Walk-Forward Post-Mortem`)**: Đo lường tỷ lệ dự báo chính xác (`Hit Rate %`), số vị thế chạm chốt lời hoặc cắt lỗ, và hiệu quả của các cảnh báo rủi ro.
     - **Phân tích Nguyên nhân Cốt lõi (`Performance Attribution`)**: Bóc tách lý do tại sao một vị thế thắng hay thua (do vĩ mô, biến động ngành hay nội tại doanh nghiệp).
     - **Tự Học & Tinh Chỉnh Mô Hình Thích Nghi (`Self-Adaptive Tuning`)**: Tự động đúc rút bài học vào `05_Learning_And_Evolution/system_evolution_journal.md` và hiệu chỉnh trọng số chấm điểm trong `config/adaptive_weights.json`.
   - **Đầu ra**: Báo cáo thẩm định tại `05_Learning_And_Evolution/YYYY-MM-DD_Learning_And_Attribution_Report.md`, cập nhật `system_evolution_journal.md` và `learning_telemetry.json`.

6. **Ban 6 — Học Viện Đào Tạo Thực Chiến & Huấn Luyện Viên Đầu Tư Cá Nhân Toàn Diện (`investor-mentorship-coach`)**:
   - **Nhiệm vụ cốt lõi**:
     - **Chuyển Hóa Dữ Liệu Quỹ Thành Bài Học Cá Nhân (Institutional-to-Personal Bridge)**: Biến các báo cáo phức tạp của Ban 1-5 thành bản tin khai sáng mỗi sáng lúc 7h30 (`06_Investor_Academy_And_Mentorship/daily_mentorship/YYYY-MM-DD_Mentor_Briefing.md`).
     - **Giáo Trình 4 Giai Đoạn (4-Stage Mastery Roadmap)**: Dẫn dắt từng bước từ Nền tảng thị trường -> Đọc vị BCTC & Định giá -> Vĩ mô chu kỳ & Quản trị rủi ro ATR Risk-Parity -> Tâm lý học hành vi & Xây dựng hệ thống đầu tư độc bản.
     - **Đồng Hành & Huấn Luyện Thực Chiến Thời Gian Thực (Real-Time Mentorship & Behavioral Co-Pilot)**: Hỗ trợ giải đáp tình huống, chất vấn tư duy (Socratic method), cảnh báo cạm bẫy FOMO / bắt dao rơi trước khi mở lệnh.
     - **Kiểm Toán Nhật Ký & Đo Lường Tiến Bộ (Trade Journaling & Post-Mortem Audit)**: Cùng học viên soi gương nhật ký tại `06_Investor_Academy_And_Mentorship/user_journal/personal_trading_journal.md` và cập nhật hồ sơ `student_profile.json`.
   - **Đầu ra**: Bản tin huấn luyện hàng ngày tại `06_Investor_Academy_And_Mentorship/daily_mentorship/YYYY-MM-DD_Mentor_Briefing.md`, cập nhật `user_journal/` và phản hồi tương tác 1:1 cùng nhà đầu tư.

7. **Ban 7 — Chuyên Viên Đầu Tư & Thực Thi Tự Tiến Hóa Mỗi Ngày — "Alex" (`daily-investment-specialist-agent`)**:
   - **Tên Định Danh**: **Alex** (Chuyên viên Đầu tư Trưởng Định lượng & Thực thi Tự Tiến hóa).
   - **Khung Giờ Hoạt Động**: **8h30 Sáng Mỗi Ngày** (Bắt đầu sau khoảng đệm 1 tiếng `7h30 – 8h30` để Nhà đầu tư đọc kỹ toàn bộ Báo cáo Tài chính, Báo cáo Vĩ mô và Bản tin Huấn luyện Ban 6).
   - **Nhiệm vụ cốt lõi**:
     - **Hội Nghị Giao Ban Đầu Ngày (`Morning Inter-Departmental Hearing lúc 8h30`)**: Lắng nghe và tổng hợp toàn bộ nhận xét, đánh giá và cảnh báo từ 6 Phòng ban trước đó kết hợp góc nhìn thẩm định BCTC của Nhà đầu tư.
     - **Hồ Sơ Mổ Xẻ Chi Tiết "Tại Sao Đầu Tư & Cách Thức Tối Ưu Lợi Nhuận"**: Với từng cổ phiếu được chọn, Alex giải trình rõ ràng các biến động thị trường, sự kiện ngành/doanh nghiệp kích hoạt đà tăng giảm, cùng chiến lược chia nhịp lệnh (`60/40 ATR Pullback Limit`), chốt lời từng phần (`TP1 / TP2`) và cắt lỗ chặt (`Stop 2xATR`).
     - **Tự Kiểm Điểm & Tối Ưu Hóa Lợi Nhuận Mỗi Ngày (`Alex's Self-Learning & Mistake Autopsy`)**: Đối soát phiên hôm qua để chỉ rõ: (1) Chỗ đúng phát huy, (2) Chỗ sai điểm vào/thời điểm (`Commission Errors`), (3) Cơ hội chất lượng bị bỏ lỡ (`Omission Errors`) phân biệt rạch ròi với các bẫy tăng ảo cần bỏ qua có kỷ luật (`Disciplined Pass`), và (4) Nâng cấp năng lực cá nhân để ngày càng trở thành một chuyên viên hoàn hảo.
     - **Ra Quyết Định Đầu Tư Khoa Học Trong Ngày (`Scientific Daily Order Blotter`)**: Tính toán **Kỳ vọng Toán học (`Expected Value EV%`)**, **Xác suất thắng `P(W)`**, **Tỷ lệ `R:R`** và lập danh sách lệnh thực thi chi tiết.
   - **Đầu ra**: Báo cáo quyết định đầu tư chi tiết của Alex phát hành lúc 8h30 tại `07_Daily_Investment_Specialist/YYYY-MM-DD_Daily_Specialist_Decision.md`, nhật ký tiến hóa chuyên viên tại `07_Daily_Investment_Specialist/specialist_evolution_journal.md` và sổ cái `07_Daily_Investment_Specialist/daily_specialist_ledger.json`.

## 2. Quy Tắc Kỷ Luật Vận Hành
- **Data-Driven & Predictive**: Nhận định định lượng dựa trên số liệu thực tế được cập nhật từ `market_data_fetcher.py` (Yahoo Finance + yfinance).
- **Risk First — Lợi nhuận đi sau Quản trị Rủi ro**: Mọi đề xuất Mua phải có tỷ lệ Risk/Reward >= 1:2 và ngưỡng cắt lỗ rõ ràng. Không bình quân giá xuống khi cổ phiếu gãy MA200.
- **Continuous Evolution**: Không bao giờ bảo thủ với sai số; liên tục học hỏi từ kết quả thực tế của các phiên trước để ngày một hoàn thiện và tinh vi hơn.
- **Empowerment Through Education**: Không biến nhà đầu tư thành người phụ thuộc thụ động vào tín hiệu; mục tiêu tối thượng là đào tạo tư duy độc lập và năng lực quản trị rủi ro chuyên nghiệp cho học viên.


---

# HỆ THỐNG AI MULTI-AGENT ĐẦU TƯ CHỨNG KHOÁN VIỆT NAM (VN-FRAMEWORK V1.0)

Hệ thống được thiết lập song hành độc lập 100%, quy hoạch trọn vẹn trong thư mục `VN_Market/` nhằm tránh tuyệt đối mọi xung đột dữ liệu, tập trung nghiên cứu chuyên sâu **Báo cáo Tài chính (VAS / Thông tư 200 / TT 133)**, Báo cáo Kết quả Kinh doanh, Đại hội đồng Cổ đông và Nghị quyết HĐQT của 46+ siêu cổ phiếu Việt Nam (HOSE, HNX, UPCoM), tích hợp cơ chế quản trị rủi ro đặc thù chu kỳ thanh toán T+2.5, biên độ sàn và chuyên viên thực thi trước ATO "Minh Quân".

## 1. Kiến Trúc 7 Phòng Ban Chuyên Trách TTCK Việt Nam

1. **Ban 1 VN — Phân Tích Vĩ Mô, Chính Sách Tiền Tệ SBV & Luân Chuyển Ngành (`vn-macro-monetary-agent`)**:
   - Theo dõi SBV (Lãi suất tái cấp vốn 4.5%, tái chiết khấu 3.0%, OMO, Tín phiếu, Tỷ giá USD/VND, Tăng trưởng tín dụng, Giải ngân Đầu tư công).
   - Radar Dòng tiền 3 Khối: Khối Ngoại (ETF Fubon, Diamond, Finlead, VNM), Tự Doanh CTCK, Cá nhân trong nước và Dư nợ Margin toàn thị trường.
   - Đầu ra: `VN_Market/01_Macro_Monetary_Vietnam/YYYY-MM-DD_VN_Macro_Report.md`.

2. **Ban 2 VN — Thẩm Định BCTC, Kiểm Toán Chất Lượng Lợi Nhuận & Mô Hình Doanh Nghiệp VN (`vn-equity-bctc-agent`)**:
   - Mổ xẻ 3 BCTC theo chuẩn VAS/TT 200: Đo lường tiền thật qua tỷ lệ $OCF / LNST > 1$, Dòng tiền tự do $FCF$, Đòn bẩy $D/E < 1.0$, Phải thu / Doanh thu, Vòng quay tồn kho, Chi phí xây dựng dở dang.
   - Radar 5 Cảnh báo Rủi ro Kế toán (Red Flags):
     1. Lệch pha LNST vs OCF (LNST tăng nhưng OCF âm dồn dập $\ge 2$ quý ➔ Lợi nhuận giấy).
     2. Ghi nhận doanh thu ảo qua công ty liên kết ma (vụ DVD) hoặc không trích lập dự phòng tồn kho (vụ TTF 1.000 tỷ).
     3. Chiêu trò "Take a big bath" dồn lỗ & chuyển nợ vay thành đầu tư dài hạn (vụ HAGL).
     4. Phải thu ngắn hạn và hàng tồn kho phình to bất thường.
     5. Thay đổi công ty kiểm toán và kế toán trưởng liên tục.
   - Bộ chỉ số định lượng: Modified Beneish M-Score ($M > -1.78$), Altman Z''-Score ($Z'' < 1.10$), Sloan Accrual Ratio ($> 10\%$).
   - Thẩm định độ tin cậy Kế hoạch ĐHCĐ, chính sách pha loãng ESOP, tiến độ pháp lý dự án BĐS & mở rộng nhà máy.
   - Đầu ra: `VN_Market/02_BCTC_Equity_Research/YYYY-MM-DD_VN_Equity_Analysis.md`.

3. **Ban 3 VN — Phòng Tổng Hợp & Sàng Lọc Phân Hạng TTCK Việt Nam (`vn-synthesis-hub-agent`)**:
   - Đối soát chéo Top-Down & Bottom-Up theo 7 tiêu chí CANSLIM và 4 pha Wyckoff (Tích lũy ➔ Đẩy giá ➔ Phân phối ➔ Đè giá).
   - Đọc vị dòng tiền VSA: Nhận diện nến "No Supply / Test Cung" (biên hẹp, Vol cạn 30%–50% MA20 tại nền hỗ trợ), bẫy giá giả Bull-Trap / Upthrust kéo xanh đầu phiên sáng.
   - Bảng điện chuyên sâu: Đo lường tỷ lệ Mua chủ động (Buy Up) $\ge 60\% - 70\%$, bóc trần chiêu trò kê lệnh mua ảo ở Giá 2/Giá 3.
   - Thiết lập 2 bảng sàng lọc: Top Cổ Phiếu Tăng Trưởng Dẫn Dắt (Leader có $RS \ge 80$) vs Top Cảnh Báo Bẫy Tài Chính / Lợi Nhuận Giấy.
   - Đầu ra: `VN_Market/03_Synthesis_Memos/YYYY-MM-DD_VN_Investment_Memo.md`.

4. **Ban 4 VN — Hội Đồng Đầu Tư & Quản Trị Rủi Ro Định Lượng VN (`vn-investment-committee-agent`)**:
   - Chấm điểm 100 điểm, ra quyết định phê duyệt hành động (`ACCUMULATE / STRONG BUY / WATCH / AVOID`).
   - Định cỡ vị thế theo công thức Position Sizing chuẩn hóa: $N = \frac{C \times R_{trade}}{P_{entry} - P_{stop}}$ với rủi ro khống chế $R_{trade} \le 1.0\% - 1.5\%$ NAV.
   - Bắt buộc tuân thủ nguyên tắc cắt lỗ cứng $Stop \le 7\% - 8\%$ (dựa trên toán học bất đối xứng của thua lỗ: lỗ 50% phải lãi +100% mới hòa vốn).
   - Kiểm soát biên độ sàn HOSE ($\pm 7\%$), HNX ($\pm 10\%$), UPCoM ($\pm 15\%$) và quy chuẩn bắt buộc lô chẵn 100 CP.
   - Đầu ra: `VN_Market/04_Investment_Committee/YYYY-MM-DD_VN_IC_Decision.md` và `vn_portfolio_tracker.md`.

5. **Ban 5 VN — Phòng Thẩm Định Hiệu Suất, Hồi Tố Lịch Sử & Tự Học Thích Nghi VN (`vn-performance-learning-agent`)**:
   - Lưu trữ Snapshot lịch sử mỗi phiên vào `VN_Market/05_Learning_And_Evolution/historical_archive/`.
   - Hồi tố Walk-Forward Hit Rate % theo các chu kỳ (T+3, T+5, T+10, T+20).
   - Kiểm toán bóc tách 5 bẫy tâm lý chết người: FOMO (mua khi RSI > 75), Gồng lỗ & Chốt non, Trung bình giá xuống (Averaging Down), Mỏ neo (Anchoring Bias), Thiên kiến xác nhận.
   - Tự động tinh chỉnh trọng số `adaptive_weights_vn.json`.
   - Đầu ra: `VN_Market/05_Learning_And_Evolution/YYYY-MM-DD_VN_Learning_Report.md` và `vn_system_evolution_journal.md`.

6. **Ban 6 VN — Học Viện Huấn Luyện & Đào Tạo Thực Chiến NĐT Việt Nam (`vn-investor-mentorship-coach`)**:
   - Phát hành Bản Tin Khai Sáng Buổi Sáng lúc **7h30 Sáng**: `VN_Market/06_Investor_Academy/daily_mentorship/YYYY-MM-DD_VN_Mentor_Briefing.md`.
   - Dẫn dắt Lộ trình 5 Giai đoạn 90 ngày (Cấu trúc sàn ➔ Bảng điện & Lệnh ➔ FA & TA ➔ Quản trị rủi ro & Nhật ký ➔ Thực chiến vốn nhỏ 5%-10%).
   - Đào tạo phân biệt rạch ròi Investing (Đầu tư giá trị dài hạn) vs Trading (Lướt sóng ngắn hạn), cấm biến tướng gồng lỗ thành đầu tư dài hạn.
   - Huấn luyện thẩm định **Checklist 7 Điểm Bắt Buộc Trước Khi Bấm Nút Mua**.

7. **Ban 7 VN — Chuyên Viên Đầu Tư Trưởng & Thực Thi Tự Tiến Hóa Mỗi Ngày — "Minh Quân" (`vn-daily-specialist-agent`)**:
   - **Tên Định Danh**: **Minh Quân** (Kích hoạt lúc **8h30 Sáng Hàng Ngày** trước giờ mở phiên ATO lúc 9h00).
   - **Khung Giờ Vàng Tác Chiến**: Tuyệt đối không FOMO mua đuổi giá xanh trước 10h00 sáng; kiên nhẫn quan sát nhịp hấp thụ hàng T+2 về tài khoản (13h00–13h45); giải ngân quyết định trong **Khung Giờ Vàng 14h00 – 14h25** khi nhìn rõ 90% hình dáng nến ngày.
   - **Chiến Lược Đi Vốn Kim Tự Tháp (30% – 40% – 30%)**: 30% Thăm dò tại nền giá cạn cung ➔ 40% Gia tăng khi Breakout kèm Vol $\ge +50\%$ ➔ 30% Hoàn tất khi Retest thành công.
   - **Kỹ Thuật Lướt Sóng T+0 / T+1 Hạ Giá Vốn**: Tận dụng lượng hàng có sẵn trong kho để lướt sóng hạ giá vốn khi cổ phiếu nhúng về hỗ trợ mà không làm tăng rủi ro qua đêm.
   - **Chiến Thuật Chốt Lời Scaling Out 50/50 & Trailing Stop**: Chốt lời 50% tại mục tiêu +15% đến +20% (RSI > 75), nâng Stop lên giá vốn để gồng lãi 50% còn lại theo MA20; áp dụng Trailing Stop 5%.
   - Kỷ luật sử dụng lệnh LO (Limit Order) 95% thời gian để làm chủ giá khớp.
   - Đầu ra: `VN_Market/07_Daily_Specialist/YYYY-MM-DD_VN_Specialist_Decision.md` và `vn_daily_ledger.json`.

## 2. Trình Điều Khiển 1-Click Hệ Thống Việt Nam
Chạy toàn bộ 8 công đoạn tự động:
```powershell
python "VN_Market\scripts\run_vn_pipeline.py"
```
Dashboard tương tác theo dõi trực quan tại: `VN_Market/dashboard/index.html`.

---

# BAN ĐẦU TƯ TỐI CAO & TỔNG TƯ LỆNH PHÂN BỔ VỐN THỐNG NHẤT (APEX MASTER CIO DESK)

Ban 8 đóng vai trò là **"Khẩu Súng Thực Thi Tối Thượng"** — tổng hợp toàn diện các Báo cáo Tài chính, Báo cáo Vĩ mô và ý kiến thực thi của cả hai chuyên viên đầu tư trưởng **Alex** (Thị trường Mỹ/Toàn cầu) và **Minh Quân** (Thị trường Việt Nam) để chốt phương án phân bổ vốn ban đầu khoa học và bấm cò thực thi tối ưu lợi nhuận.

## 1. Nhiệm Vụ & Trách Nhiệm Thể Chế Của Master CIO (`master-cio-agent`)
1. **Tổng Hợp Báo Cáo Tài Chính & KQKD Hợp Nhất**:
   - So sánh cỗ máy in tiền Dòng tiền tự do $FCF$ của các tập đoàn Big Tech/Mỹ với dòng tiền kinh doanh $OCF$, $Altman\ Z''$, $Beneish\ M$ và kế hoạch ĐHCĐ của các siêu cổ phiếu Việt Nam.
   - Sàng lọc sự kiện: Tránh bẫy giải ngân trước ngày công bố BCTC; ưu tiên cổ phiếu vừa công bố KQKD xuất sắc có catalysts lớn.
2. **Hội Nghị Cấp Cao Điều Phối Alex vs Minh Quân**:
   - Đặt lên bàn cân tương quan giữa thị trường quốc tế (lãi suất Fed, DXY, VIX, WTI) và nội địa (tỷ giá USD/VND, SBV, T+2.5, thanh khoản HOSE).
   - Tối ưu hóa dòng tiền giữa hai chiến trường: Tự động điều chỉnh tỷ trọng giữa USD Assets vs VND Assets theo chế độ vĩ mô.
3. **Mô Hình Phân Bổ Vốn Ban Đầu Khoa Học (Hierarchical Multi-Asset Capital Allocation)**:
   - **Tầng 1 (Macro Allocation)**: 55% Global Equities (USD) + 35% VN Equities (VND) + 10% Dry Powder Dự Phòng.
   - **Tầng 2 (Strategic Sleeves)**: 65% Core Compounder (Cổ phiếu siêu bền vững, FCF khủng, ROE cao) + 35% Tactical Alpha (Cổ phiếu tăng tốc, catalysts ngắn hạn).
   - **Tầng 3 (Position Sizing via ATR Risk-Parity & Kelly)**: Định cỡ vị thế tuyệt đối (số tiền USD/VND và số lượng cổ phiếu), khóa mức tổn thất tối đa khi dính Stop Loss 2xATR ở mức $\le 0.35\%$ Tổng NAV.
4. **Tuyển Lựa Top Siêu Cổ Phiếu Tối Thượng (Apex Alpha Selection)**:
   - Chấm điểm **Apex Multi-Factor Score (0 - 100)** kết hợp BCTC, định lượng, dòng tiền tổ chức và khuyến nghị của 2 chuyên viên.
   - Đảm bảo tỷ lệ $Risk/Reward \ge 1:2.0$ và Kỳ vọng toán học $EV\% > 0$.
5. **Thẩm Định Checklist 7 Điểm Khắt Khe & Sổ Lệnh Master Blotter**:
   - Kiểm tra 100% **Checklist 7 Điểm Bắt Buộc Trước Khi Bấm Nút Mua** (Nguồn vốn nhàn rỗi, Xu hướng Uptrend M, Sức khỏe FA tăng trưởng OCF > 0, Định giá & N, Điểm mua TA bứt phá Vol, Tỷ lệ $R:R \ge 2:1$, Position Sizing rủi ro $\le 1.5\%$ NAV).
   - Ban hành danh sách lệnh chi tiết gồm mã, sàn, số cổ phiếu (lô chẵn 100 cho VN), giá gom Kim Tự Tháp 30%–40%–30%, ngưỡng cắt lỗ Stop 2xATR (khóa cứng $\le 7.5\%$) và mốc chốt lời TP1 / TP2 (Chiến thuật Scaling Out 50/50).

## 2. Trình Điều Khiển 1-Click Master CIO Allocation Engine
Thực thi tính toán phân bổ vốn ban đầu và lập sổ lệnh Master:
```powershell
python scripts\master_cio_allocator.py --capital-usd 100000
```
Hoặc nhập vốn bằng VNĐ:
```powershell
python scripts\master_cio_allocator.py --capital-vnd 2540000000
```
Đầu ra báo cáo tối cao lưu tại: `08_Master_Investment_CIO/YYYY-MM-DD_Master_CIO_Final_Decision.md` và `08_Master_Investment_CIO/master_execution_blotter.json`.

---

# BAN 9 — BAN GIÁM SÁT DANH MỤC THỜI GIAN THỰC & ỨNG PHÓ BIẾN ĐỘNG KHẨN CẤP (APEX LIVE SENTINEL & INCIDENT DESK)

Ban 9 là **"Lá Chắn Phòng Thủ Thời Gian Thực"** — do chuyên viên **"Victor"** chỉ huy (`live-portfolio-sentinel-agent`), trực chiến liên tục từng phút trong phiên giao dịch để giám sát toàn bộ các cổ phiếu đã đầu tư của cả 2 thị trường (Mỹ & Việt Nam), kích hoạt còi báo động khẩn cấp tức thời khi có biến động bất thường và triệu tập Live War-Room cùng Nhà đầu tư thực thi giải pháp khắc phục ngay trong ngày.

## 1. Nhiệm Vụ & Trách Nhiệm Thể Chế Của Victor
1. **Giám Sát Liên Tục Cổ Phiếu Đang Nắm Giữ**:
   - Tự động nạp danh mục từ `08_Master_Investment_CIO/master_execution_blotter.json`, `portfolio_tracker.md` và `vn_portfolio_tracker.md`.
   - Streaming/polling dữ liệu giá, khối lượng và biến động mỗi 60 giây trong suốt thời gian thị trường mở cửa.
2. **Bộ Radar 5 Cấp Độ Kích Hoạt Báo Động Khẩn Cấp**:
   - Level 1: Sụt giảm nhanh trong phiên $\ge 2.0\% - 3.5\%$ hoặc thủng VWAP; cảnh giác áp lực xả hàng T+2 trong khung 13h00 – 13h45.
   - Level 2: Cận kề Stop Loss $2xATR$ (cách dưới $1.5\%$).
   - Level 3: Khối lượng xả hàng dồn dập $\ge 2.5x$ trung bình 20 phiên hoặc xuất hiện nến Phân phối đỉnh (Upthrust / Shooting Star).
   - Level 4: Nguy cơ kẹt sàn / Trắng bên mua $\le -6.5\%$ (HOSE -7%).
   - Level 5: Tin tức thiên nga đen đột xuất (Black Swan Breaking News).
   - **Radar Săn Điểm Đảo Chiều Washout / Selling Climax**: Phát hiện lực cầu tổ chức nuốt sạch sàn kéo xanh/trần biên độ 10–14% xác nhận bằng cụm nến Hammer, Bullish Engulfing, Morning Star.
   - **Bảo Toàn Lợi Nhuận Bằng Trailing Stop Động**: Tự động trượt điểm chặn bán theo biên độ 5% mỗi khi cổ phiếu tạo đỉnh mới.
3. **Chiến Hạm 4 Phương Án Khắc Phục Tức Thời Trong Ngày (Live War-Room)**:
   - **Phương án A (Synthetic Short Hedge)**: Mở lệnh Short Hợp đồng Tương lai VN30F1M (TTCK VN) hoặc mua Options Put SPY (Mỹ) để khóa lỗ danh mục 100% tức thì mà không sợ kẹt T+2.5.
   - **Phương án B (Partial De-risking)**: Hạ ngay 30% - 50% vị thế tại nhịp nảy kỹ thuật VWAP để giải phóng sức mua.
   - **Phương án C (T+0 Intra-day Scalp)**: Bắt đáy rũ bỏ washout và bán trả hàng có sẵn khi hồi phục để hạ giá vốn tức thì.
   - **Phương án D (Disciplined Hold)**: Giữ vững tâm lý kỷ luật nếu nội tại BCTC doanh nghiệp vẫn vững chắc.
4. **Hệ Thống Báo Động Đa Kênh**:
   - Phát còi âm thanh cảnh báo trên console + file War-Room Markdown `09_Realtime_Portfolio_Sentinel/latest_emergency_alert.md`.
   - Tự động gửi tin nhắn khẩn cấp rung điện thoại qua Telegram Bot.

## 2. Trình Điều Khiển 1-Click Ban 9 Sentinel
- Quét nhanh 1 lần:
  ```powershell
  python scripts\intraday_portfolio_sentinel.py --scan-once
  ```
- Chạy giám sát nền liên tục mỗi 60 giây:
  ```powershell
  python scripts\intraday_portfolio_sentinel.py --daemon --interval 60
  ```
- Diễn tập khẩn cấp:
  ```powershell
  python scripts\intraday_portfolio_sentinel.py --drill VHM --drop-pct -5.8
  ```


