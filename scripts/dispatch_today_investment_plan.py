#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DISPATCH TODAY'S COMPREHENSIVE INVESTMENT PLAN TO TELEGRAM JAMES HQ & PRIVATE CHAT
File: scripts/dispatch_today_investment_plan.py
Cơ quan chủ quản: Master CIO Supreme Execution Desk (Ban 8) & Minh Quân (Ban 7 VN)
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

    plan_part1 = (
        "🎯 *[BỘ CHỈ HUY MASTER CIO JAMES — KẾ HOẠCH ĐẦU TƯ CHI TIẾT THỨ SÁU 06/11/2026]*\n"
        "🏛️ *Cơ quan*: Master CIO Supreme Execution Desk (Ban 8) & Minh Quân (Ban 7 VN)\n"
        "👤 *Kính trình*: Chủ tịch Phước Trần (Tài khoản TCBS: `105C307855`)\n"
        "⏰ *Thời điểm*: 08h22 Sáng 06/11/2026 | Trước thềm mở phiên ATO 09h00\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "💎 *1. HIỆN TRẠNG TÀI SẢN (VỊ THẾ CHIẾN LƯỢC)*:\n"
        "• Toàn bộ *900 CP* (`HPG: 400`, `TCB: 300`, `MBB: 200`) đã sẵn sàng 100% *\"ĐƯỢC GIAO DỊCH\"*.\n"
        "• Lợi nhuận tạm tính hiện tại: *`+494,600 ₫ (+2.66%)`* (MBB `+4.8%`, TCB `+2.8%`, HPG `+1.6%`).\n"
        "• Toàn bộ vị thế đã được Victor Sentinel dời ngưỡng dừng lỗ (Stop Loss) lên giá vốn ➔ *RISK-FREE TRADE* hoàn hảo!\n\n"
        "☀️ *2. GIAI ĐOẠN 1 (PHIÊN SÁNG: 09H15 – 10H00) — CHỐT LỜI ĐÓN NHỊP HƯNG PHẤN*:\n"
        "👉 *Bối cảnh*: Thứ Sáu thường có quán tính kéo giá hưng phấn đầu ngày do F0 đua lệnh theo phiên bứt phá hôm qua.\n"
        "👉 *Chiến thuật*: Bán chốt lời từng phần (*Scaling Out 50%*) hoặc chốt 100% tại vùng đỉnh ngắn hạn:\n"
        "1️⃣ `MBB` (200 CP, Vốn `18.61`, Hiện tại `19.50`):\n"
        "   - Vùng giá chốt: *`19.80 – 20.00 ₫`* (Kỳ vọng lãi *`+6.4% đến +7.5%`*)\n"
        "   - Khối lượng: Bán 100 CP (thu về ~1.98M ₫) hoặc bán hết 200 CP (thu về ~3.96M ₫).\n"
        "2️⃣ `TCB` (300 CP, Vốn `21.36`, Hiện tại `21.95`):\n"
        "   - Vùng giá chốt: *`22.30 – 22.50 ₫`* (Kỳ vọng lãi *`+4.4% đến +5.3%`*)\n"
        "   - Khối lượng: Bán 100-150 CP (thu về ~2.23M - 3.35M ₫) hoặc bán hết 300 CP.\n"
        "3️⃣ `HPG` (400 CP, Vốn `21.16`, Hiện tại `21.50`):\n"
        "   - Vùng giá chốt: *`21.80 – 22.00 ₫`* (Kỳ vọng lãi *`+3.0% đến +4.0%`*)\n"
        "   - Khối lượng: Bán 200 CP (thu về ~4.36M ₫) hoặc bán hết 400 CP.\n"
        "👉 *TỔNG LỢI NHUẬN THU VỀ DỰ KIẾN*: *`+750,000 ₫ đến +950,000 ₫`* tiền tươi thóc thật!"
    )

    plan_part2 = (
        "🔄 *3. GIAI ĐOẠN 2 (PHIÊN CHIỀU: 13H45 – 14H20) — TÁI CƠ CẤU VỐN VÒNG MỚI*:\n"
        "👉 *Bối cảnh*: Sau 13h45 chiều Thứ Sáu, thị trường thường có áp lực rung lắc hạ nhiệt trước 2 ngày nghỉ cuối tuần (*Weekend De-risking*). Đây là thời điểm vàng để gom hàng giá rẻ cho tuần sau!\n"
        "👉 *Quy mô tiền mặt*: Sau khi chốt lời sáng nay, tiền mặt nhàn rỗi sẽ vọt lên *`11,000,000 ₫ đến 20,400,000 ₫` (55% – 100% NAV)*.\n"
        "👉 *Top Siêu Cổ Phiếu Đón Sóng Mới (Data Pháp Y Ban 10)*:\n"
        "1. `DBC` (Dabaco): BCTC Q3 dòng tiền OCF đạt 1,615 tỷ (gấp *8.07x* lần lãi), catalyst vắc-xin dịch tả lợn ASF thương mại hóa. Canh gom thăm dò quanh vùng hỗ trợ `28.5 - 29.0`.\n"
        "2. `FPT`: Bluechip công nghệ, thặng dư tiền mặt khủng > 29.000 tỷ ₫, hợp tác AI Factory cùng Nvidia.\n"
        "3. `MWG`: Chuỗi Bách Hóa Xanh bước vào chu kỳ có lãi ròng thực chất.\n"
        "👉 *Cách đi vốn*: Tuân thủ phương pháp Kim Tự Tháp 30% Thăm dò ➔ 40% Gia tăng ➔ 30% Hoàn tất vị thế.\n\n"
        "⛔ *4. KỶ LUẬT THÉP BẮT BUỘC TRONG NGÀY*:\n"
        "• *Cấm 1*: Tuyệt đối không mua đua trần trong 15 phút ATO (09h00 - 09h15).\n"
        "• *Cấm 2*: Sử dụng 100% lệnh LO (Lệnh Giới Hạn) để bán được đúng giá mục tiêu, không dùng lệnh MP.\n"
        "• *Quyền quyết định*: Đúng 09h15 sáng nay, Master CIO James sẽ bắn tín hiệu giá khớp cụ thể để Chủ tịch thao tác 1-Click trên app TCBS!"
    )

    print("[*] Dispatching Today's Investment Plan to Telegram...")
    ok1 = dispatch_message("james_hq", plan_part1)
    ok2 = dispatch_message("james_hq", plan_part2)

    ok_p1 = send_raw_telegram(bot_token, str(private_chat_id), plan_part1, parse_mode="Markdown")
    ok_p2 = send_raw_telegram(bot_token, str(private_chat_id), plan_part2, parse_mode="Markdown")

    print(f"[+] Dispatch Results: JamesHQ=({ok1}, {ok2}), Private=({ok_p1}, {ok_p2})")
    return 0 if (ok1 and ok2) else 1

if __name__ == "__main__":
    sys.exit(main())
