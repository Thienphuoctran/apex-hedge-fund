#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DISPATCH 08:45 MASTER BLOTTER OVERRIDE & OFFICIAL 100% EXIT MANDATE
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.telegram_dispatcher import dispatch_message

def dispatch_0845_official_blotter():
    blotter_msg = (
        "🎖️ *[BAN 8 — MASTER CIO JAMES: PHÊ DUYỆT CHÍNH THỨC SỔ LỆNH MASTER BLOTTER 08H45]*\n"
        "👑 *Chủ tịch*: **Trần Quốc Thiên Phước** | Tiểu khoản: `105C307855` (TCBS)\n"
        "📅 *Phiên giao dịch*: Thứ Sáu 06/11/2026 | *Chiến lược*: **KỊCH BẢN A — BÁN HẾT 100% (900 CP)**\n\n"
        "⚡ *MỆNH LỆNH THỰC THI CHỐT LỜI — KHUNG GIỜ VÀNG 09H15 - 09H45*:\n"
        "Toàn bộ 900 CP đã KHẢ DỤNG 100%. Master CIO James ban hành các mức giá bán Limit Order (LO) chuẩn hóa:\n\n"
        "1. 🔴 *HPG (Tập đoàn Hòa Phát)*: BÁN HẾT **400 CP**\n"
        "   • Giá vốn: `21.16` | Thị giá tham chiếu: `21.50`\n"
        "   • Mức giá bán LO: **`21.80 – 22.00 ₫`** (+3.0% – +4.0%)\n"
        "   • Lợi nhuận dự kiến: **`+257,600 ₫ đến +337,600 ₫`**\n\n"
        "2. 🔴 *TCB (Techcombank)*: BÁN HẾT **300 CP**\n"
        "   • Giá vốn: `21.36` | Thị giá tham chiếu: `21.95`\n"
        "   • Mức giá bán LO: **`22.30 – 22.50 ₫`** (+4.4% – +5.3%)\n"
        "   • Lợi nhuận dự kiến: **`+283,200 ₫ đến +343,200 ₫`**\n\n"
        "3. 🔴 *MBB (MBBank)*: BÁN HẾT **200 CP**\n"
        "   • Giá vốn: `18.61` | Thị giá tham chiếu: `19.50`\n"
        "   • Mức giá bán LO: **`19.80 – 20.00 ₫`** (+6.4% – +7.5%)\n"
        "   • Lợi nhuận dự kiến: **`+238,800 ₫ đến +278,800 ₫`**\n\n"
        "💰 *TỔNG KẾT THƯƠNG VỤ ĐẦU TƯ*:\n"
        "• Tổng lãi tiền tươi bỏ túi trọn vẹn: **`+780,000 ₫ đến +960,000 ₫`** (ROI `+4.2% – +5.2%`)\n"
        "• Tổng tiền mặt sau khi chốt: **`~20,500,000 ₫`** (100% Tiền Mặt, 0% Cổ Phiếu)\n"
        "• Triệt tiêu hoàn toàn rủi ro 2 ngày cuối tuần (Zero Weekend Risk)!\n\n"
        "🚨 *QUY TẮC CẦU CHÌ SÁNG NAY*:\n"
        "• 09:00 - 09:15: CẦU CHÌ GUARD-01: CẤM đặt lệnh bán ATO hoảng loạn, CẤM mua đua ATO.\n"
        "• 09:15 - 09:45: ĐẶT BÁN LO 3 LỆNH THEO BẢNG GIÁ TRÊN.\n"
        "👉 Báo cáo chi tiết song song đã hiển thị đầy đủ tại Antigravity Chat!"
    )

    print("[*] Dispatching Official 08:45 Master Blotter to Telegram...")
    res_james = dispatch_message("james_hq", blotter_msg)
    res_blotter = dispatch_message("morning_blotter", blotter_msg)
    res_private = dispatch_message("copilot_chat", blotter_msg)
    print(f"[+] Results: JamesHQ={res_james}, Blotter={res_blotter}, Private={res_private}")

if __name__ == "__main__":
    dispatch_0845_official_blotter()
