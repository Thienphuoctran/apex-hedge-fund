#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DISPATCH WEEKLY STRATEGIC PLAN (09/11 - 13/11/2026) TO TELEGRAM
File: scripts/dispatch_weekly_strategic_plan.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.telegram_dispatcher import dispatch_message

sys.stdout.reconfigure(encoding='utf-8')

# Message: Master CIO James (Topic 6 & Private Chat)
msg_weekly = (
    "🏛️ [BỘ CHỈ HUY TỔNG TƯ LỆNH JAMES] KẾ HOẠCH TÁC CHIẾN & PHÂN BỔ ĐẦU TƯ TUẦN MỚI (09/11 - 13/11/2026)\n\n"
    "Kính gửi: Chủ tịch Trần Quốc Thiên Phước\n"
    "Hội đồng 11 Phòng ban đã hoàn tất họp chiến lược tuần mới theo chỉ thị của Chủ tịch:\n\n"
    "1. DỰ BÁO XU HƯỚNG THỊ TRƯỜNG TUẦN TỚI:\n"
    "• Kịch bản Cơ sở (70%): Đầu tuần nhúng rũ bỏ về vùng hỗ trợ cứng 1.700 - 1.710 điểm (MA50); giữa đến cuối tuần xuất hiện nến rút chân test cung hồi phục lên 1.735 - 1.745 điểm.\n"
    "• Kịch bản Tiêu cực (30%): Khối ngoại xả mạnh thủng 1.700 về 1.680 ➔ Quỹ tiếp tục ôm tiền mặt phòng thủ.\n\n"
    "2. TOP 2 SIÊU CỔ PHIẾU TIỀM NĂNG NHẤT:\n"
    "🏆 PVT: RS 95 | OCF/LNST 2.01x | F-Score 9/9 | Gom nhịp 1 quanh 20.0 - 20.4k | Stop: 19.2k | TP: 22.5k - 24.0k\n"
    "🏆 TCB: RS 86 | OCF/LNST 1.16x | Sạch nợ VAMC (TT54) | Gom nhịp 1 quanh 20.8 - 21.2k | Stop: 19.8k | TP: 23.0k - 24.5k\n"
    "⛔ CẢNH BÁO TRÁNH XA: FPT (ngoại xả mạnh, kẹp giá 68, RS 26) & OCB (nợ xấu Q3 vượt 4.0%).\n\n"
    "3. KẾ HOẠCH TRIỂN KHAI VỐN 20.2 TRIỆU:\n"
    "• Đi vốn Kim Tự Tháp 30% - 40% - 30% trong Khung Giờ Vàng 14h00 - 14h25 khi có xác nhận nến rút chân.\n"
    "• Luôn giữ tối thiểu 30% - 40% tiền mặt tươi phòng thủ.\n\n"
    "Kính trình Chủ tịch phê chuẩn bản Kế Hoạch Tác Chiến!"
)

print("Dispatching Weekly Strategic Plan to Topic 6 (james_hq)...")
dispatch_message("james_hq", msg_weekly)

print("Dispatching Weekly Strategic Plan to Topic 4 (morning_blotter)...")
dispatch_message("morning_blotter", msg_weekly)

print("Dispatching Weekly Strategic Plan to Topic 5 (radar_filings)...")
dispatch_message("radar_filings", msg_weekly)

print("Dispatching Weekly Strategic Plan to Private Chat...")
dispatch_message("james_hq", msg_weekly, force_private=True)

print("--- WEEKLY STRATEGIC PLAN DISPATCH COMPLETED ---")
