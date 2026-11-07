#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DISPATCH REALISTIC BATTLEFIELD CORRECTION TO TELEGRAM
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.telegram_dispatcher import dispatch_message

def dispatch_reality_correction():
    msg = (
        "⚠️ *[MASTER CIO JAMES — ĐIỀU CHỈNH MỨC GIÁ BÁN THỰC CHIẾN 09H18]*\n"
        "👑 *Chủ tịch*: **Trần Quốc Thiên Phước** | Tiểu khoản: `105C307855`\n\n"
        "📉 *ĐỐI SOÁT THỰC TẾ BẢNG ĐIỆN*\n"
        "Toàn sàn HOSE đang bị đè đỏ trên diện rộng (249 mã giảm, trụ VIC -3.4, MSN -1.3, FPT -1.3).\n"
        "• *HPG*: `21.10` (-0.40) | Vốn 21.16 | Lãi/Lỗ: -24k (Hòa vốn)\n"
        "• *TCB*: `21.65 – 21.70` (-0.30) | Vốn 21.36 | Vẫn LÃI: +87k đến +102k (+1.4%)\n"
        "• *MBB*: `19.10` (-0.40) | Vốn 18.61 | Vẫn LÃI: +98k (+2.6%)\n"
        "👉 Tổng danh mục: *VẪN ĐANG LÃI DƯƠNG +161,000 ₫*!\n\n"
        "🎯 *CHỈ THỊ THAY ĐỔI MỨC GIÁ BÁN LO — BẢO VỆ VỐN & THU TIỀN VỀ NGAY*:\n"
        "Vì thị trường chung yếu, không kéo xanh mạnh được, CẤM treo lệnh giá cao ảo tưởng (21.8 hay 22.3) sẽ không thể khớp!\n"
        "Chủ tịch hạ giá bán LO khớp thẳng theo thị giá thực tế để đóng vị thế:\n"
        "1. *TCB (300 CP)*: Bán LO giá **`21.65 – 21.70 ₫`** (Khóa lãi +87k - +102k)\n"
        "2. *MBB (200 CP)*: Bán LO giá **`19.10 – 19.15 ₫`** (Khóa lãi +98k)\n"
        "3. *HPG (400 CP)*: Bán LO giá **`21.10 – 21.15 ₫`** (Bán hòa vốn, bảo toàn vốn)\n"
        "💰 Thu hồi toàn bộ ~20.16M tiền mặt, bảo toàn 100% vốn và lãi tươi!"
    )
    dispatch_message("alerts", msg)
    dispatch_message("james_hq", msg)
    dispatch_message("copilot_chat", msg)
    print("[+] Dispatched realistic correction to Telegram successfully!")

if __name__ == "__main__":
    dispatch_reality_correction()
