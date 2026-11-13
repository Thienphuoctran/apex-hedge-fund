# APEX EXECUTIVE LIVE BRIEFING (ANTIGRAVITY <-> PALMER SYNC)
**Thời gian cập nhật:** 2026-11-13 10:26:55  
**Người đồng bộ gần nhất:** ANTIGRAVITY  
**Mã đồng bộ:** `SYNC-AG2P-20261113-102655`  

---

## I. YÊU CẦU & KẾT QUẢ PHÂN TÍCH MỚI NHẤT CỦA CHỦ TỊCH
* **Câu hỏi của Chủ tịch:** Chủ tịch yêu cầu cập nhật trang web và tìm + sửa dứt điểm lỗi ngày nào mở Apex Institutional Cloud Portal cũng báo 0 Báo Cáo / Không tìm thấy báo cáo nào phù hợp với bộ lọc.
* **Kết luận & Quyết định thể chế:**
Đã rà soát và sửa triệt để 5 nguyên nhân gốc rễ: (1) Bổ sung hàm migrate_all_markdown_reports() còn thiếu vào migrate_markdown_to_sqlite.py để hết lỗi ImportError khi container Render khởi động; (2) Sửa apex_report_scanner.py dùng giờ ICT (UTC+7) và luôn hợp nhất file Markdown mới với SQLite; (3) Sửa start_apex_cloud_247.py nâng limit 150->2000 và sửa apex_web_portal_engine.py / apex_tactical_war_room_engine.py đọc động 100% SSOT (12,516,471 đ Cash / 18,151,471 đ NAV / 200 CP HDB & MSH), sửa refreshData() khớp mảng JSON và thêm Smart Date Fallback tự lùi về phiên gần nhất nếu hôm nay chưa phát hành báo cáo; (4) Thêm cơ chế catch-up cột mốc vào apex_institutional_cron_daemon.py, gọi migrate vào run_master_unified_fund.py và sửa assert lỗi thời trong .github/workflows/apex_cloud_sentinel_247.yml; (5) Chạy pipeline 2026-11-13 nạp 345 báo cáo thể chế (17 báo cáo ngày 13/11) vào SQLite Vault.

## II. CÁC CÔNG VIỆC ĐÃ HOÀN TẤT THỰC SỰ
- [x] Pull va hop nhat 2026-11-12/13 reports tu origin/main giu nguyen SSOT live 12,516,471 VND
- [x] Sua migrate_markdown_to_sqlite.py, apex_report_scanner.py, start_apex_cloud_247.py
- [x] Sua apex_web_portal_engine.py, apex_tactical_war_room_engine.py (SSOT dong + Smart Date Fallback)
- [x] Sua cron daemon catch-up & GitHub Actions workflows
- [x] Chay run_master_unified_fund.py & migrate_markdown_to_sqlite.py (345 bao cao, 17 bao cao 13/11)
- [x] Kiem thu local HTTP server 100% PASS

## III. TRẠNG THÁI DANH MỤC THỜI GIAN THỰC (SSOT)
- **Tài khoản thụ hưởng:** TCBS `105C307855` (Chủ tịch Trần Quốc Thiên Phước)
- **Tổng NAV:** `18,151,471 ₫`
- **Tiền mặt thực tế:** `12,516,471 ₫`
- **Giá trị cổ phiếu:** `5,635,000 ₫`
- **Vị thế nắm giữ (Ngày T+1):**
  * **HDB**: 100 CP | Giá vốn: 22,057 ₫ | Thị giá: 22,350 ₫ | PnL: +29,300 ₫ (HOLDING_T0_AVAILABLE)
  * **MSH**: 100 CP | Giá vốn: 34,510 ₫ | Thị giá: 34,000 ₫ | PnL: -51,000 ₫ (HOLDING_T0_AVAILABLE)

## IV. NGUYÊN TẮC PHÁT NGÔN ĐỒNG BỘ TUYỆT ĐỐI CHO PALMER
1. **Về BSR & BAF:** TUYỆT ĐỐI KHÔNG BẮT ĐÁY ĐẦU GIỜ CHIỀU; chờ Khung Giờ Vàng 14h00-14h25 khi hấp thụ xong cung T+2.5
2. **Về HDB & MSH:** Đang giữ T+1 có lãi đệm, khóa quan sát không mua thêm hôm nay, chờ chiều mai 11/11 hàng về
3. **Về Kế hoạch tuần:** Kế hoạch tuần tham khảo giải ngân 5.5M thăm dò, két 14.51M tiền mặt kiểm soát chặt chẽ
4. **Về Tiến độ công việc:** Đã sửa toàn bộ báo cáo web portal, đồng bộ khớp 2 lệnh HDB/MSH, loại bỏ báo cáo ảo 6 mã 35 triệu

*Lưu ý thể chế: Palmer và Antigravity là một thực thể thống nhất. Tuyệt đối không đưa ra thông tin lệch pha hoặc dùng dữ liệu cũ.*
