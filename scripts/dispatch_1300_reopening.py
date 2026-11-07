#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DISPATCH 13:00 AFTERNOON REOPENING REPORT TO TELEGRAM
File: scripts/dispatch_1300_reopening.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.telegram_dispatcher import dispatch_message

sys.stdout.reconfigure(encoding='utf-8')

msg_1300 = (
    "🔔 [CỘT MỐC 13:00] MỞ BÁT PHIÊN CHIỀU THỨ SÁU (06/11/2026)\n"
    "Cơ quan trực chiến: Ban 7 VN (Minh Quân) & Ban 9 (Victor Sentinel)\n\n"
    "🛡️ VỊ THẾ QUỸ: 100% TIỀN MẶT (20.199.425 ₫) | 0 CỔ PHIẾU\n"
    "• Đã chốt lãi đút túi an toàn: +199.600 ₫ (+1.07% ROI).\n\n"
    "⚡ KÍCH HOẠT PHA 1: ÁN BINH BẤT ĐỘNG (13:00 - 13:45)\n"
    "• Toàn bộ đợt hàng bắt đáy T+2 (từ Thứ Tư) đang dội về tài khoản thị trường.\n"
    "• Kỷ luật sắt của Ban 7: TUYỆT ĐỐI KHÔNG MUA ĐUỔI khi xuất hiện một vài mã đầu cơ xanh sớm (VND, DXG, KDH) tránh dính bẫy Bull-trap đầu phiên chiều.\n"
    "• Ngồi im quan sát áp lực xả hàng và tâm lý thoát hàng trước 2 ngày nghỉ cuối tuần (Weekend De-risking).\n\n"
    "Kính báo Chủ tịch: Quỹ đang ở vị thế Thợ săn rình mồi an toàn 100%!"
)

print("Dispatching 13:00 Reopening to Topic 6 (james_hq)...")
dispatch_message("james_hq", msg_1300)

print("Dispatching 13:00 Reopening to Topic 4 (morning_blotter)...")
dispatch_message("morning_blotter", msg_1300)

print("Dispatching 13:00 Reopening to Private Chat...")
dispatch_message("james_hq", msg_1300, force_private=True)

print("--- 13:00 REOPENING DISPATCH COMPLETED ---")
