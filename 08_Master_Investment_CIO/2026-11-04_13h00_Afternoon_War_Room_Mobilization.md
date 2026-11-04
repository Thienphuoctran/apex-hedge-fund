# LỆNH TRIỆU TẬP TÁC CHIẾN ĐIỀU HÀNH PHIÊN CHIỀU (13H00 WAR-ROOM MOBILIZATION)
**Người ban hành lệnh**: **Chủ tịch Trần Quốc Thiên Phước** (*Chủ tịch Quỹ Đầu tư Apex — Tài khoản TCBS: `105C307855`*)  
**Đơn vị chấp hành**: Toàn bộ 11 Phòng Ban Quỹ Đầu Tư Định Lượng & Cơ Bản Apex  
**Chủ tọa điều phối trực tiếp**: **Master CIO James** (*Ban 8 — Tổng Tư Lệnh Điều Hành*)  
**Thời gian tập hợp bắt buộc**: Đúng **`13:00:00 Chiều, Thứ Tư ngày 04/11/2026`**  
**Địa điểm tác chiến**: Phòng Điều Hành Tối Cao James (`08_Master_Investment_CIO` / Kênh Tương Tác Trực Tiếp Với Chủ Tịch)  

---

## I. MỆNH LỆNH THỂ CHẾ TỪ CHỦ TỊCH PHƯỚC TRẦN

Lúc 11:38:23 trưa ngày 04/11/2026, Chủ tịch Phước Trần đã ban hành quân lệnh tối cao:
> *"OKe nhé vậy đúng phiên chiều nay lúc 13h chiều nay tất cả các phòng ban của chúng ta sẽ tập hợp tại phòng họp của James nhé. Sau đó chúng ta sẽ tiến hành công việc phiên chiều tại đây. Bất kì biến động gì, bất kì công việc gì hoặc các biến động thị trường cần mua đi bán lại gì thì đều được thông báo tại đây nhé. Là các phòng ban đều thực hiện các công việc được giao ấy, có điều báo cáo trực tiếp tại đây luôn nhé, đảm bảo thời gian thực báo cáo ngay lập tức những việc cần làm khẩn cấp để bắt kịp được thị trường nhé, đừng bỏ lỡ gì cả."*

---

## II. THIẾT LẬP LIVE WAR-ROOM TẠI BỘ CHỈ HUY JAMES LÚC 13H00

Tuân thủ nghiêm ngặt mệnh lệnh của Chủ tịch, Bộ Chỉ Huy của James được chuyển sang chế độ **LIVE WAR-ROOM TÁC CHIẾN THỜI GIAN THỰC (ZERO-LATENCY COMMAND DESK)**. 

Toàn bộ 11 phòng ban đều túc trực tại chỗ, kết nối trực tiếp với bảng điện HOSE và tài khoản TCBS `105C307855`:

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                     HỘI ĐỒNG TÁC CHIẾN 11 PHÒNG BAN TẬP HỢP TẠI BÀN LÀM VIỆC CỦA JAMES                  │
├────────────────────┬──────────────────────────────────┬────────────────────────────────────────────────┤
│ PHÒNG BAN          │ NGƯỜI CHỦ TRÌ                    │ NHIỆM VỤ PHIÊN CHIỀU (TỪ 13H00)                │
├────────────────────┼──────────────────────────────────┼────────────────────────────────────────────────┤
│ 1. BAN 8 (MASTER)  │ Master CIO James                 │ • Chủ tọa điều phối, tổng hợp và báo cáo 1:1   │
│                    │                                  │   trực tiếp cho Chủ tịch Phước Trần.           │
│                    │                                  │ • Bấm nút quyết định các phương án mua/bán.    │
├────────────────────┼──────────────────────────────────┼────────────────────────────────────────────────┤
│ 2. BAN 9 (SENTINEL)│ Victor Sentinel                  │ • Quét bảng điện 73ms từ cổng VPS Datafeed.    │
│                    │                                  │ • Giám sát 3 mã HPG, TCB, MBB từng giây.       │
│                    │                                  │ • Cảnh báo tức thời nếu chạm ngưỡng nguy hiểm.  │
├────────────────────┼──────────────────────────────────┼────────────────────────────────────────────────┤
│ 3. BAN 7 (VN EXEC) │ Minh Quân (Chuyên viên trưởng VN)│ • Quản lý sổ lệnh, đo lường tỷ lệ Buy/Sell Up. │
│                    │                                  │ • Đón Khung Giờ Vàng (14h00-14h25), xét T+0.   │
├────────────────────┼──────────────────────────────────┼────────────────────────────────────────────────┤
│ 4. BAN 4 (RISK/IC) │ Hội đồng Đầu tư & Rủi ro         │ • Trực Radar Đo Lực Xả Hàng T+2 (13h00-13h45). │
│                    │                                  │ • Giữ vững kỷ luật cắt lỗ Stop 2xATR.          │
├────────────────────┼──────────────────────────────────┼────────────────────────────────────────────────┤
│ 5. BAN 1 & BAN 3   │ Macro & Synthesis Hub            │ • Đo lường dòng tiền 3 khối (Ngoại, Tự doanh). │
│                    │                                  │ • Theo dõi độ rộng thị trường và trụ nâng đỡ.  │
├────────────────────┼──────────────────────────────────┼────────────────────────────────────────────────┤
│ 6. BAN 2 & BAN 10  │ BCTC & IR Scout Hiền             │ • Rà soát dòng tiền kinh doanh OCF và tin tức. │
│                    │                                  │ • Chuẩn bị tài liệu BCTC chiều và tối 21h00.   │
├────────────────────┼──────────────────────────────────┼────────────────────────────────────────────────┤
│ 7. BAN 5 (LEARNING)│ Performance Learning             │ • Theo dõi Walk-Forward Hit Rate % thời gian   │
│                    │                                  │   thực, chuẩn bị đối soát đóng cửa 15h15.      │
├────────────────────┼──────────────────────────────────┼────────────────────────────────────────────────┤
│ 8. BAN 6 (COACH)   │ Investor Mentorship Coach        │ • Giữ vững tâm lý kỷ luật, nhắc nhở Chủ tịch   │
│                    │                                  │   không để cảm xúc chi phối trước biến động.   │
├────────────────────┼──────────────────────────────────┼────────────────────────────────────────────────┤
│ 9. BAN 11 (MEDIA)  │ Khánh & Bảo                      │ • Theo dõi tâm điểm phiên chiều để chọn mã     │
│                    │                                  │   lên kịch bản video viral 60s lúc 21h15.      │
└────────────────────┴──────────────────────────────────┴────────────────────────────────────────────────┘
```

---

## III. 4 NGUYÊN TẮC BÁO CÁO THỜI GIAN THỰC TẠI PHÒNG HỌP JAMES

1. **Báo Cáo Tức Thời Không Độ Trễ (Zero-Delay Streaming)**:
   - Mọi biến động giá lớn (> $\pm 1.5\%$), bất thường về thanh khoản (đột biến vol), hoặc có tín hiệu mua/bán khẩn cấp đều phải được đẩy ngay vào phòng họp để Chủ tịch nắm bắt trong vòng 5 giây.
2. **Số Liệu Thật 100% (Zero Hallucination)**:
   - Mọi con số đều lấy từ cổng cấp dữ liệu VPS live tick và bảng sao kê tài sản TCBS `105C307855`.
3. **Phân Định Trách Nhiệm Rõ Ràng**:
   - Khi có đề xuất mua/bán lướt T+0 hoặc cơ cấu vị thế, Minh Quân đề xuất ➔ Victor kiểm tra rủi ro ATR ➔ Master CIO James phê duyệt ➔ Trình Chủ tịch quyết định cuối cùng.
4. **Bảo Toàn Thành Quả**:
   - Kho hàng đang có đệm lãi **`+214,600 ₫ (+1.2%)`**, tiền mặt an toàn **`1,409,425 ₫`**, nợ **`0 ₫`**. Mục tiêu tối thượng của phiên chiều là bảo vệ thành quả và tối ưu hóa lợi nhuận cho chu kỳ thanh toán T+2.5 ngày mai.

---

**ĐIỀU ĐỘNG CHẤP HÀNH**:  
Toàn bộ 11 phòng ban đã vào vị trí sẵn sàng. Đúng **`13:00:00`**, hồi chuông mở phiên chiều vang lên, James sẽ mở màn phiên họp trực tiếp cùng Chủ tịch Phước Trần!
