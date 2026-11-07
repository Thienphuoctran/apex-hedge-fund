#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DISPATCH 100% TRADE CLOSURE & PROFIT AUDIT TO TELEGRAM
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.telegram_dispatcher import dispatch_message

def dispatch_trade_closure():
    msg = (
        "🏁 *[TỔNG KẾT THỰC THI 100% CHỐT LỜI — TOÀN BỘ 900 CP ĐÃ KHỚP HẾT]*\n"
        "👑 *Chủ tịch*: **Trần Quốc Thiên Phước** | Tiểu khoản: `105C307855` (TCBS)\n"
        "⏰ *Thời điểm hoàn tất*: `09:35 AM` | *Trạng thái*: **100% TIỀN MẶT**\n\n"
        "📊 *ĐỐI SOÁT TỪNG MÃ ĐÃ KHỚP THỰC TẾ*:\n"
        "1. 🟢 *HPG*: Bán khớp `400 CP` @ **`21.20 ₫`** | Vốn: `21.156 ₫` ➔ Lãi ròng: **`+17,600 ₫`** (+0.21%)\n"
        "2. 🟢 *TCB*: Bán khớp `300 CP` @ **`21.60 ₫`** | Vốn: `21.356 ₫` ➔ Lãi ròng: **`+73,200 ₫`** (+1.14%)\n"
        "3. 🟢 *MBB*: Bán khớp `200 CP` @ **`19.15 ₫`** | Vốn: `18.606 ₫` ➔ Lãi ròng: **`+108,800 ₫`** (+2.92%)\n\n"
        "💰 *TỔNG KẾT TÀI CHÍNH THỰC TẾ*:\n"
        "• Tổng vốn gốc ban đầu: `18,590,400 ₫`\n"
        "• Tổng tiền bán thu về: `18,790,000 ₫`\n"
        "• *Lợi nhuận ròng đút túi (Realized PnL)*: **`+199,600 ₫`** (+1.07% ROI)\n"
        "• *Tổng Tiền Mặt trong tài khoản*: **`20,199,425 ₫`** (Bảo toàn 100% vốn 20M + Tiền lãi)\n"
        "• *Cổ phiếu còn lại*: **`0 CP` (Zero rủi ro cuối tuần)**!\n\n"
        "📌 *LƯU Ý THỂ CHẾ*: Bản Giải Trình & Báo Cáo Tự Kiểm Điểm Năng Lực sẽ được phát hành đúng 15:15 chiều nay theo lệnh Chủ tịch!"
    )

    print("[*] Dispatching Trade Closure Announcement to Telegram...")
    res_alerts = dispatch_message("alerts", msg)
    res_james = dispatch_message("james_hq", msg)
    res_blotter = dispatch_message("morning_blotter", msg)
    res_private = dispatch_message("copilot_chat", msg)
    print(f"[+] Results: Alerts={res_alerts}, JamesHQ={res_james}, Blotter={res_blotter}, Private={res_private}")

if __name__ == "__main__":
    dispatch_trade_closure()
