#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DISPATCH TIKTOK INTELLIGENCE RESEARCH REPORT TO TELEGRAM
File: scripts/dispatch_tiktok_research_report.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.telegram_dispatcher import dispatch_message

sys.stdout.reconfigure(encoding='utf-8')

# Message: Master CIO James (Topic 6 & Private Chat)
msg_tiktok = (
    "📱 [BỘ CHỈ HUY TỔNG TƯ LỆNH JAMES] BÁO CÁO NGHIÊN CỨU CHUYÊN SÂU KHO TIKTOK (@TRANPHUOC262)\n\n"
    "Kính gửi: Chủ tịch Trần Quốc Thiên Phước\n"
    "Hội đồng 11 Phòng ban đã mổ xẻ toàn diện 18 video tài chính trong mục 'Đã thích' của Chủ tịch:\n\n"
    "1. TÂM CHẤN VĨ MÔ QUỐC TẾ:\n"
    "• Cú sập Phố Wall (Nasdaq 100 -6,4%, bốc hơi 2.500 tỷ USD) khiến khối ngoại tháo chạy khỏi Bluechips, bán ròng 10 phiên (-305 tỷ).\n"
    "• Hậu quả: FPT bị ngoại xả sàn (-3,97%), kéo sập VN-Index về 1.725 điểm. Rất nhiều F0 đang kêu cứu vì 'Kẹp FPT giá 68'!\n\n"
    "2. CHÍNH SÁCH BẢN LỀ NỢ VAMC (THÔNG TƯ 54/2026/TT-NHNN CÓ HIỆU LỰC TỪ 06/11):\n"
    "• Nợ VAMC được xem xét vay lại nếu có phương án khả thi, nhưng ngân hàng thẩm định khắt khe.\n"
    "• Cổ phiếu hưởng lợi lớn nhất: TCB, MBB, CTG (đã sạch nợ VAMC từ trước).\n\n"
    "3. CẢNH BÁO NỢ XẤU OCB & BẪY '06/11 ĐỪNG BỎ LỠ':\n"
    "• OCB lãi 9 tháng 4.123 tỷ nhưng nợ xấu Q3 vượt 4.0% ➔ Không mua đuổi!\n"
    "• Video hô hào '06/11 đừng bỏ lỡ' sáng Thứ Sáu đã khiến F0 đu đỉnh ăn trọn cây nến giảm -15.37 điểm buổi chiều!\n\n"
    "🏆 KẾT LUẬN: Quyết định bán hết 900 CP sáng 06/11 của Quỹ đút túi +199.6k ₫ là THIÊN TÀI! Quỹ đang cầm 100% TIỀN MẶT (20.2M) thảnh thơi đón đáy 1.700 điểm vào tuần tới!\n\n"
    "Kính báo Chủ tịch!"
)

print("Dispatching TikTok Report to Topic 6 (james_hq)...")
dispatch_message("james_hq", msg_tiktok)

print("Dispatching TikTok Report to Topic 189 (hien_desk)...")
dispatch_message("hien_desk", msg_tiktok)

print("Dispatching TikTok Report to Topic 4 (morning_blotter)...")
dispatch_message("morning_blotter", msg_tiktok)

print("Dispatching TikTok Report to Topic 5 (radar_filings)...")
dispatch_message("radar_filings", msg_tiktok)

print("Dispatching TikTok Report to Private Chat...")
dispatch_message("james_hq", msg_tiktok, force_private=True)

print("--- TIKTOK INTELLIGENCE DISPATCH COMPLETED ---")
