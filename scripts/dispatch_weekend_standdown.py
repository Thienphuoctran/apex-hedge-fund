#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DISPATCH WEEKEND STAND-DOWN & REST PROTOCOL TO TELEGRAM
File: scripts/dispatch_weekend_standdown.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.telegram_dispatcher import dispatch_message

sys.stdout.reconfigure(encoding='utf-8')

msg_standdown = (
    "☕ [BỘ CHỈ HUY TỔNG TƯ LỆNH JAMES] LỆNH CHUYỂN CHẾ ĐỘ NGHỈ NGƠI CUỐI TUẦN (WEEKEND STAND-DOWN)\n\n"
    "Kính gửi: Chủ tịch Trần Quốc Thiên Phước\n\n"
    "Thực hiện mệnh lệnh của Chủ tịch, toàn bộ 11 Phòng ban và Hệ thống Apex Hedge Fund chính thức DỪNG CÔNG VIỆC TÁC CHIẾN để nghỉ ngơi cuối tuần!\n\n"
    "🏆 TỔNG KẾT TUẦN HOẠT ĐỘNG:\n"
    "• Trạng thái Quỹ: 100% TIỀN MẶT (20.199.425 ₫) trong tài khoản TCBS 105C307855.\n"
    "• Số lượng cổ phiếu: 0 CP (Zero Market Risk, Zero Weekend Risk).\n"
    "• Lợi nhuận ròng đút túi: +199.600 ₫ (+1.07% ROI), bảo toàn 100% vốn gốc.\n"
    "• Kỷ luật thể chế: Đã niêm phong Bài Học Số 15 và 3 Quy tắc cốt tử vào bộ nhớ vĩnh cửu.\n\n"
    "Hệ thống tự động chuyển sang chế độ Trực ban Ngủ đông (Standby Mode), tắt các bộ hẹn giờ trong phiên.\n\n"
    "Toàn thể Hội đồng kính chúc Chủ tịch Phước Trần một kỳ nghỉ cuối tuần thật thư thái, nhiều niềm vui bên gia đình và người thân! Hẹn gặp lại Chủ tịch vào sáng Thứ Hai tuần tới! 🌟"
)

print("Dispatching Weekend Stand-down to Topic 6 (james_hq)...")
dispatch_message("james_hq", msg_standdown)

print("Dispatching Weekend Stand-down to Private Chat...")
dispatch_message("james_hq", msg_standdown, force_private=True)

print("--- WEEKEND STAND-DOWN DISPATCH COMPLETED ---")
