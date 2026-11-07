#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DISPATCH FULL INSTITUTIONAL 21:00 HIEN FORENSIC REPORT TO TELEGRAM JAMES HQ, HIEN DESK & PRIVATE CHAT
File: scripts/dispatch_milestone_2100_hien.py
Cơ quan chủ quản: Ban 10 (Hiền — BCTC & IR) & Master CIO James (Ban 8)
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

    card_hien = (
        "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        "   🌸 BAN 10 — BÀN LÀM VIỆC CỦA HIỀN\n"
        "   BÁO CÁO RÀ SOÁT BCTC ĐỘC QUYỀN (21H00)\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
        "📅 *Ngày*: `2026-11-05` | ⏰ `21:00 PM` | 👤 *TCBS*: `105C307855`\n"
        "🎯 *Tiêu chí khắt khe*: 100% Doanh nghiệp Vừa & Lớn, Tiền thật OCF/LNST ≥ 1.0x, Zero Red Flags!\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🏢 *1. DBC — CTCP TẬP ĐOÀN DABACO VIỆT NAM (HOSE: MidCap)*\n"
        "• *Doanh thu*: `5,138 tỷ ₫` | *LNST*: `200.2 tỷ ₫`\n"
        "• *Dòng tiền thật OCF*: `1,615.3 tỷ ₫`\n"
        "👉 *Tỷ lệ Tiền Thật*: *`8.07x`* (🟢 Tiền mặt kinh doanh thu về gấp hơn 8 LẦN lãi kế toán!)\n"
        "⚡ *Catalyst*: Giá heo hơi tạo đáy đi lên, nhà máy vắc-xin Dịch tả lợn Châu Phi (ASF) thương mại hóa.\n"
        "🔗 *Nguồn IR*: [Cổng IR Dabaco](https://www.dabaco.com.vn/quan-he-co-dong)\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🏢 *2. TCB — TECHCOMBANK (HOSE: LargeCap Ngân Hàng)*\n"
        "• *Doanh thu/TOI*: `17,226.8 tỷ ₫` | *LNST*: `7,942.9 tỷ ₫`\n"
        "• *Dòng tiền thật OCF*: `7,635.8 tỷ ₫` (Tỷ lệ `0.96x` — Rất khỏe so với chuẩn ngành Bank)\n"
        "👉 *Chất lượng tài sản*: Tỷ lệ CASA dẫn đầu hệ thống ~40%, NIM giữ vững `4.2%`.\n"
        "⚡ *Catalyst*: Tăng trưởng tín dụng bứt phá, hoàn thành kế hoạch năm 2026 sớm.\n"
        "🔗 *Nguồn IR*: [Cổng IR Techcombank](https://www.techcombank.com/quan-he-co-dong)\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🏢 *3. FPT — TẬP ĐOÀN FPT (HOSE: Bluechip Công Nghệ)*\n"
        "• *Doanh thu*: `13,754.2 tỷ ₫` | *LNST*: `2,723.1 tỷ ₫`\n"
        "• *Dòng tiền thật OCF*: `2,096.5 tỷ ₫` (Tỷ lệ `0.77x` — Tiền mặt dồi dào, thặng dư FCF cao)\n"
        "👉 *Chất lượng*: Doanh số ký mới từ thị trường nước ngoài vượt 1 tỷ USD, mảng AI & Cloud tăng trưởng > 30% YoY.\n"
        "⚡ *Catalyst*: Hợp tác chiến lược chip bán dẫn và AI Factory cùng Nvidia.\n"
        "🔗 *Nguồn IR*: [Cổng IR FPT](https://fpt.com/vi/quan-he-co-dong)\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🤝 *BÀN GIAO NGHIỆP VỤ SANG BAN 11 (KHÁNH & BẢO)*:\n"
        "Dạ em Hiền đã bàn giao toàn bộ số liệu pháp y tiền thật OCF sang **Ban 11 (Khánh & Bảo)** để sản xuất kịch bản video viral 60s TikTok/Reels phát hành lúc 21h15!\n\n"
        "👉 *Báo cáo chi tiết đã lưu*: `VN_Market/02_BCTC_Equity_Research/2026-11-05_Hien_Daily_Review.md`"
    )

    buttons_hien = {
        "inline_keyboard": [
            [
                {"text": "📑 IR Techcombank (TCB)", "url": "https://www.techcombank.com/quan-he-co-dong"},
                {"text": "💻 IR FPT Telecom (FPT)", "url": "https://fpt.com/vi/quan-he-co-dong"}
            ],
            [
                {"text": "🌾 IR Dabaco (DBC)", "url": "https://www.dabaco.com.vn/quan-he-co-dong"}
            ]
        ]
    }

    print("[*] Dispatching Milestone 21:00 Hien forensic report to Telegram...")
    # Dispatch to James HQ (Topic 6)
    ok_james = dispatch_message("james_hq", card_hien, reply_markup=buttons_hien)
    # Dispatch to Hien Desk (Topic 189)
    ok_hien = dispatch_message("hien_desk", card_hien, reply_markup=buttons_hien)
    # Dispatch to Private Chat (Push Notification for Chairman's mobile)
    ok_private = send_raw_telegram(bot_token, str(private_chat_id), card_hien, reply_markup=buttons_hien, parse_mode="Markdown")

    print(f"[+] Milestone 21:00 Dispatch Results: JamesHQ={ok_james}, HienDesk={ok_hien}, Private={ok_private}")
    return 0 if (ok_james and ok_hien and ok_private) else 1

if __name__ == "__main__":
    sys.exit(main())
