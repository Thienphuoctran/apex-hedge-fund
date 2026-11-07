#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DISPATCH ANSWER TO CHAIRMAN: SELL ALL VS HOLD FOR FRIDAY
File: scripts/dispatch_answer_sell_or_hold.py
Cơ quan chủ quản: Master CIO Supreme Execution Desk (Ban 8)
"""

import sys
import os
import json
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.telegram_dispatcher import dispatch_message, send_raw_telegram, load_config

def main():
    cfg = load_config()
    bot_token = cfg.get("bot_token")
    private_chat_id = cfg.get("private_chat_id")

    msg = (
        "💡 *[MASTER CIO JAMES — TRẢ LỜI QUYẾT ĐỊNH: BÁN HẾT HAY GIỮ LẠI HÔM NAY?]*\n"
        "🏛️ *Cơ quan*: Apex Master CIO Executive Desk (Ban 8)\n"
        "👤 *Kính gửi*: Chủ tịch Phước Trần (Tài khoản TCBS: `105C307855`)\n"
        "⏰ *Thời điểm*: 08h25 Sáng Thứ Sáu (06/11/2026)\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🎯 *KẾT LUẬN DỨT KHOÁT: NÊN TIẾN HÀNH BÁN HẾT 100% TRONG SÁNG NAY (09H15 – 09H45)!*\n\n"
        "📌 *3 LÝ DO VÀNG MASTER CIO KHUYẾN NGHỊ BÁN HẾT*:\n"
        "1️⃣ *Đúng mục tiêu Kịch bản A*: Hôm qua chúng ta giữ lại là để ăn trọn 'nhịp kéo giá hưng phấn sáng nay'. Khi giá chạm vùng đỉnh ngắn hạn vào 09h15 - 09h45, đó chính là thời khắc mục tiêu đã hoàn thành xuất sắc!\n"
        "2️⃣ *Triệt tiêu rủi ro chiều Thứ Sáu (Weekend Risk)*: Chiều Thứ Sáu thường xuyên có áp lực bán xả hạ tỷ trọng để tránh rủi ro tin tức 2 ngày cuối tuần. Bán hết vào sáng nay giúp Chủ tịch chốt trọn vẹn đỉnh, không bị mất lãi vào phiên chiều!\n"
        "3️⃣ *Hiện thực hóa tiền tươi*: Thu về trọn vẹn *`+750,000 ₫ đến +950,000 ₫`* lãi ròng, quy toàn bộ danh mục về *`~20,500,000 ₫ TIỀN MẶT (100% Cash)`*, thảnh thơi đón kỳ nghỉ cuối tuần.\n\n"
        "👉 *NGOẠI LỆ DUY NHẤT*: Chỉ giữ lại 50% nếu sáng nay một trong 3 mã bứt phá dư mua trần tím (hàng triệu cổ kê trần). Nếu không có tím, chúng ta chốt sạch 100% bỏ túi tiền tươi!\n\n"
        "⏰ Đúng 09h15 mở phiên, James sẽ bắn giá chốt cụ thể từng mã để Chủ tịch bấm lệnh!"
    )

    ok_james = dispatch_message("james_hq", msg)
    ok_p = send_raw_telegram(bot_token, str(private_chat_id), msg, parse_mode="Markdown")
    print(f"[+] Dispatched answer: JamesHQ={ok_james}, Private={ok_p}")
    return 0 if (ok_james and ok_p) else 1

if __name__ == "__main__":
    sys.exit(main())
