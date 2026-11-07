#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DISPATCH MORNING FLASH CLOSE REPORT (11:45 AM) TO TELEGRAM
File: scripts/dispatch_morning_flash_close.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.telegram_dispatcher import dispatch_message

sys.stdout.reconfigure(encoding='utf-8')

msg_flash = (
    "☀️ [CỘT MỐC 11:45] BÁO CÁO FLASH CHỐT PHIÊN SÁNG (06/11/2026)\n"
    "Cơ quan đồng phát hành: Ban 1 & Ban 3 VN | Phê duyệt: Master CIO James\n\n"
    "💰 TÀI KHOẢN QUỸ: 100% TIỀN MẶT (20.199.425 ₫) | 0 Cổ phiếu\n"
    "• Đã chốt sạch 900 CP sáng nay, bảo toàn Lãi ròng đút túi: +199.600 ₫ (+1.07% ROI).\n"
    "• Đánh giá: Rút lui cực kỳ chuẩn xác! MBB đã rơi xuống 19.10 ₫ (thấp hơn giá bán 19.15), TCB đứng 21.60 ₫, HPG đứng 21.20 ₫.\n\n"
    "📊 ĐỘ RỘNG THỊ TRƯỜNG KẾT PHIÊN SÁNG (11:30):\n"
    "• Xanh: 8 mã (14.8%) | Tham chiếu: 4 mã | Đỏ: 42 mã (77.8%).\n"
    "• Trụ lớn tiếp tục bị khối ngoại đè ép: FPT (-2.65%), VIC (-1.51%), VCB (-0.7%), MWG (-1.07%).\n"
    "• Top mã RS cao giữ vững giá: PVT (20.65k, +0.24%, RS 95), GAS (74.70k, +0.13%, RS 89), BSR (26.50k, RS 98).\n\n"
    "🎯 CHỈ THỊ PHIÊN CHIỀU (13:00 - 15:00):\n"
    "1. 13:00 - 13:45: ÁN BINH BẤT ĐỘNG! Quan sát lượng hàng T+2 dội về tài khoản và áp lực xả hàng cuối tuần (Weekend De-risking).\n"
    "2. Kịch bản Tối ưu số 1: BẢO LƯU 100% TIỀN MẶT QUA CUỐI TUẦN để bảo vệ toàn bộ thành quả!\n\n"
    "Kính báo Chủ tịch nghỉ trưa ngon miệng!"
)

print("Dispatching Morning Flash Close to Topic 6 (james_hq)...")
dispatch_message("james_hq", msg_flash)

print("Dispatching Morning Flash Close to Topic 4 (morning_blotter)...")
dispatch_message("morning_blotter", msg_flash)

print("Dispatching Morning Flash Close to Topic 5 (radar_filings)...")
dispatch_message("radar_filings", msg_flash)

print("Dispatching Morning Flash Close to Private Chat...")
dispatch_message("james_hq", msg_flash, force_private=True)

print("--- MORNING FLASH CLOSE DISPATCH COMPLETED ---")
