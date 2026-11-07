#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DISPATCH EMERGENCY COUNCIL RESOLUTION AT 09:30 TO TELEGRAM
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.telegram_dispatcher import dispatch_message

def dispatch_emergency_resolution():
    msg = (
        "🚨 *[HỘI NGHỊ KHẨN CẤP LIÊN PHÒNG BAN 09H30 — LỆNH THOÁT TOÀN BỘ 100% DANH MỤC]*\n"
        "👑 *Chủ tịch*: **Trần Quốc Thiên Phước** | Tiểu khoản: `105C307855`\n"
        "🏛️ *Hội đồng thẩm định*: Master CIO James (Ban 8), Victor (Ban 9), Minh Quân (Ban 7 VN), Ban 4 Quản trị rủi ro\n\n"
        "📉 *ĐÁNH GIÁ THỊ TRƯỜNG KHẨN CẤP*:\n"
        "• Thị trường chung đang chịu áp lực xả rất mạnh ở nhóm trụ (FPT -2.0, MWG -1.2, MSN -1.1, VIC -2.5).\n"
        "• Đà hồi phục của 3 mã đang bị suy yếu (TCB tụt về 21.55, HPG về 21.15, MBB về 19.10).\n"
        "• Nguy cơ: Nếu chần chừ, áp lực bán trước giờ trưa và lượng hàng T+2 chiều về sẽ biến khoản lãi thành lỗ!\n\n"
        "⚡ *QUYẾT NGHỊ TỐI CAO: BÁN HẾT 100% TOÀN BỘ 900 CP NGAY LẬP TỨC*:\n"
        "Chủ tịch mở App TCBS, bấm BÁN LO ngay tại bước giá bên mua đang kê đỡ:\n"
        "1. 🔴 *TCB (300 CP)*: Bán LO giá **`21.55 – 21.60 ₫`** (Khóa lãi +57k - +72k)\n"
        "2. 🔴 *MBB (200 CP)*: Bán LO giá **`19.05 – 19.10 ₫`** (Khóa lãi +88k - +98k)\n"
        "3. 🔴 *HPG (400 CP)*: Bán LO giá **`21.15 ₫`** (Bán hòa vốn tuyệt đối, thu hồi toàn bộ vốn gốc)\n\n"
        "💰 *TỔNG KẾT*: Thu hồi trọn vẹn **`~20.150.000 ₫ TIỀN MẶT`** (Bảo toàn 100% vốn gốc + Lãi tươi `~150k - 170k ₫`), sạch bóng rủi ro cuối tuần!"
    )

    print("[*] Dispatching Emergency Council Resolution to Telegram...")
    res_alerts = dispatch_message("alerts", msg)
    res_james = dispatch_message("james_hq", msg)
    res_blotter = dispatch_message("morning_blotter", msg)
    res_private = dispatch_message("copilot_chat", msg)
    print(f"[+] Results: Alerts={res_alerts}, JamesHQ={res_james}, Blotter={res_blotter}, Private={res_private}")

if __name__ == "__main__":
    dispatch_emergency_resolution()
