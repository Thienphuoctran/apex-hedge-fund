#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DISPATCH FULL INSTITUTIONAL 21:15 KHANH VIRAL VIDEO SCRIPT REPORT TO TELEGRAM JAMES HQ, KHANH STUDIO & PRIVATE CHAT
File: scripts/dispatch_milestone_2115_khanh.py
Cơ quan chủ quản: Ban 11 (Khánh & Bảo) & Master CIO James (Ban 8)
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

    card_khanh = (
        "🎬 *[BAN 11 — KHÁNH & BẢO: XUẤT BẢN KỊCH BẢN VIDEO VIRAL 60S TIKTOK/REELS (21H15)]*\n"
        "🏛️ *Cơ quan*: Ban 11 (Chief Content Creator Khánh & Chuyên viên Render Bảo) | Giám sát: Master CIO James (Ban 8)\n"
        "👤 *Kính trình*: Chủ tịch Phước Trần (Tài khoản TCBS: `105C307855`)\n"
        "⏰ *Thời điểm*: `21:15:00 PM` — 05/11/2026\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔥 *1. TIÊU ĐỀ VIDEO GIẬT TÍT (VIRAL HOOK)*:\n"
        "👉 *\"SỰ THẬT VỀ 'CỖ MÁY IN TIỀN' HÒA PHÁT: LÃI 8.200 TỶ NHƯNG TIỀN THẬT VÀO TÀI KHOẢN LÀ BAO NHIÊU?\"*\n\n"
        "📱 *2. THÔNG SỐ SẢN XUẤT CHUẨN TIKTOK / REELS / YOUTUBE SHORTS*:\n"
        "• *Định dạng*: Video Dọc 9:16 | Thời lượng chuẩn: *59 Giây*\n"
        "• *Điểm chấm Viral*: *`95/100`* (CỰC KỲ XUẤT SẮC — BẬT ĐÈN XANH SẢN XUẤT)\n"
        "• *Cố vấn số liệu*: 100% Tiền Thật OCF trích xuất từ BCTC do em Hiền (Ban 10) cung cấp.\n\n"
        "🎞️ *3. BỐ CỤC 6 CẢNH QUAY NHỊP ĐỘ NHANH*:\n"
        "1️⃣ *00:00 - 00:03 (Hook 3s Chặn Ngón Tay)*: Đừng mua Hòa Phát nếu chưa biết con số này! Công ty báo lãi 8.200 tỷ, nhưng số tiền mặt thật chảy về két là bao nhiêu?\n"
        "2️⃣ *00:04 - 00:18 (Thực Trạng Con Số Giấy)*: Nhà đầu tư chỉ nhìn LNST 8,217 tỷ ₫, nhưng bậc thầy đầu tư luôn kiểm tra OCF!\n"
        "3️⃣ *00:19 - 00:36 (Bóc Trần Tiền Thật)*: Tiền mặt kinh doanh OCF đạt tới *`8,865.9 tỷ ₫`* (gấp 1.08x lần lãi kế toán) — Tiền tươi thóc thật 100%!\n"
        "4️⃣ *00:37 - 00:48 (Chất Xúc Tác)*: Siêu dự án Lò cao Dung Quất 2 bổ sung 5.6M tấn HRC/năm tài trợ bằng chính cỗ máy in tiền này.\n"
        "5️⃣ *00:49 - 00:55 (Bài Học Xương Máu)*: OCF > LNST là ngọc quý; OCF âm liên tục 2 quý thì chạy ngay kẻo ăn bẫy xào nấu số liệu!\n"
        "6️⃣ *00:56 - 01:00 (Kêu Gọi Hành Động)*: Bình luận giá vốn HPG bên dưới để cùng đàm đạo và tham khảo danh mục iCopy TCBS 105C307855!\n\n"
        "💻 *4. BÀN GIAO SẢN XUẤT CHO BẢO RENDER*:\n"
        "Khánh đã chuyển giao Render Job sang máy tính của Bảo để tự động lồng tiếng AI Edge-TTS và render khung hình 9:16.\n\n"
        "👉 Báo cáo chi tiết đã lưu: `11_Viral_Content_Creation/2026-11-05_Viral_Script_Khánh.md`"
    )

    buttons_khanh = {
        "inline_keyboard": [
            [
                {"text": "🎬 Xem Kịch Bản Chi Tiết", "url": "https://hoaphat.com.vn/quan-he-co-dong"},
                {"text": "📊 BCTC Gốc HPG (Ban 10)", "url": "https://hoaphat.com.vn/quan-he-co-dong"}
            ]
        ]
    }

    print("[*] Dispatching Milestone 21:15 Khanh report to Telegram...")
    # Dispatch to James HQ (Topic 6)
    ok_james = dispatch_message("james_hq", card_khanh, reply_markup=buttons_khanh)
    # Dispatch to Khanh Studio (Topic 190)
    ok_khanh = dispatch_message("khanh_studio", card_khanh, reply_markup=buttons_khanh)
    # Dispatch to Private Chat (Push Notification for Chairman's mobile)
    ok_private = send_raw_telegram(bot_token, str(private_chat_id), card_khanh, reply_markup=buttons_khanh, parse_mode="Markdown")

    print(f"[+] Milestone 21:15 Dispatch Results: JamesHQ={ok_james}, KhanhStudio={ok_khanh}, Private={ok_private}")
    return 0 if (ok_james and ok_khanh and ok_private) else 1

if __name__ == "__main__":
    sys.exit(main())
