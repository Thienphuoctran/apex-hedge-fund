# TỪ ĐIỂN THUẬT NGỮ PHỐ WALL & ĐẦU TƯ ĐỊNH LƯỢNG THỰC CHIẾN
## (Wall Street & Institutional Quant Glossary — Song Ngữ Anh - Việt Thực Chiến)

> Cẩm nang giải thích ngắn gọn, súc tích, dễ nhớ dành cho nhà đầu tư cá nhân, được thiết kế bởi **Ban 6 — investor-mentorship-coach**.

---

### Nhóm 1: Thước Đo Thị Trường & Định Lượng
- **VIX (CBOE Volatility Index)**: "Chỉ số sợ hãi". Đo lường mức độ biến động kỳ vọng của chỉ số S&P 500 trong 30 ngày tới thông qua giá hợp đồng quyền chọn. VIX > 20 là thị trường bắt đầu có rủi ro rung lắc.
- **ATR (Average True Range)**: Biên độ dao động trung bình thực tế của cổ phiếu trong $N$ phiên (thường là 14 phiên). Dùng để đặt ngưỡng cắt lỗ (Stop-Loss = $2 \times \text{ATR}$) và định cỡ vị thế theo mức độ biến động.
- **Sharpe Ratio**: Tỷ số đo lường lợi nhuận trên một đơn vị rủi ro so với lãi suất phi rủi ro: $(\text{Return} - R_f) / \sigma$. Sharpe > 1.0 là tốt; Sharpe > 2.0 là xuất sắc.
- **Max Drawdown (MDD)**: Mức sụt giảm tối đa từ đỉnh cao nhất xuống đáy sâu nhất của danh mục trong một khoảng thời gian. Thước đo khả năng chịu đựng của nhà đầu tư.
- **Beta ($\beta$)**: Độ nhạy của một cổ phiếu so với toàn bộ thị trường (S&P 500). $\beta = 1.0$ là chuyển động cùng nhịp thị trường; $\beta = 1.5$ nghĩa là nếu thị trường tăng 1%, cổ phiếu có xu hướng tăng 1.5% (và ngược lại nếu giảm).
- **Correlation ($r$)**: Hệ số tương quan giữa hai tài sản, chạy từ -1.0 đến +1.0. Nếu $r > 0.70$, hai tài sản chuyển động gần như cùng chiều (cụm tương quan cao, cần tránh mua dồn vốn).

---

### Nhóm 2: Báo Cáo Tài Chính & Định Giá Doanh Nghiệp
- **Gross Margin (Biên Lợi Nhuận Gộp)**: Phần trăm doanh thu còn lại sau khi trừ đi giá vốn hàng bán (COGS). Phản ánh "con hào kinh tế" và quyền lực định giá sản phẩm.
- **FCF (Free Cash Flow - Dòng Tiền Tự Do)**: Tiền mặt thuần túy doanh nghiệp tạo ra sau khi trừ toàn bộ chi phí hoạt động và chi phí đầu tư tài sản cố định (CapEx).
- **FCF Margin**: Tỷ lệ $\text{FCF} / \text{Doanh thu}$. FCF Margin > 20% là doanh nghiệp thuộc hàng siêu cỗ máy in tiền mặt (như MSFT, NVDA, GOOGL).
- **Forward P/E**: Tỷ số Giá trên Thu nhập dự phóng cho 12 tháng tới. Phản ánh thị trường đang trả bao nhiêu tiền cho mỗi đồng lợi nhuận tương lai.
- **PEG Ratio**: P/E chia cho Tỷ lệ Tăng trưởng Lợi nhuận (Earnings Growth Rate). Chuẩn mực của huyền thoại Peter Lynch để tìm siêu cổ phiếu tăng trưởng giá rẻ.
- **SEC Form 10-K / 10-Q**: Báo cáo tài chính năm (10-K) và báo cáo tài chính quý (10-Q) bắt buộc nộp cho Ủy ban Chứng khoán Mỹ (SEC).
- **SEC Form 4**: Báo cáo công khai mọi giao dịch mua hoặc bán cổ phiếu của lãnh đạo nội bộ (Insiders: CEO, CFO, HĐQT) trong vòng 2 ngày làm việc sau khi giao dịch phát sinh.

---

### Nhóm 3: Thuật Ngữ Chiến Lược & Hành Động Giao Dịch
- **Risk-to-Reward Ratio (R:R)**: Tỷ lệ giữa mức rủi ro sẵn sàng chấp nhận mất so với mức lợi nhuận kỳ vọng đạt được. Chuẩn mực Quỹ luôn yêu cầu $R:R \ge 1:2$.
- **Hard Stop-Loss**: Mức giá cắt lỗ cố định được cài đặt trước khi vào lệnh, tuyệt đối không được dời xa hơn khi giá đi ngược hướng kỳ vọng.
- **Trailing Stop**: Điểm dừng lỗ di động tịnh tiến theo chiều tăng của giá cổ phiếu để khóa chặt lợi nhuận khi cổ phiếu vào xu hướng tăng mạnh.
- **Breakout**: Hiện tượng giá bứt phá vượt qua vùng kháng cự đỉnh cũ kèm theo khối lượng giao dịch (Volume) bùng nổ, báo hiệu một sóng tăng mới bắt đầu.
- **Pullback / Retracement**: Cú điều chỉnh kỹ thuật ngắn hạn của một cổ phiếu đang trong xu hướng tăng khỏe về các đường hỗ trợ quan trọng (như MA20 hoặc MA50), tạo ra điểm mua an toàn giá rẻ.
- **Risk-On vs Risk-Off**:
  - *Risk-On*: Tâm lý thị trường ưa thích rủi ro, dòng tiền đổ mạnh vào Cổ phiếu công nghệ, Tiền mã hóa, Bán dẫn.
  - *Risk-Off*: Tâm lý thị trường phòng thủ, dòng tiền tháo chạy về Tiền mặt (USD), Trái phiếu Mỹ, Vàng, Tiện ích thiết yếu.
