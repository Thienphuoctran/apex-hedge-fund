#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DISPATCH LOCKED MORNING ACTION PLAN & FULL DAILY ROADMAP TO TELEGRAM JAMES HQ, BLOTTER & PRIVATE CHAT
File: scripts/dispatch_locked_morning_plan.py
Cơ quan chủ quản: Master CIO Supreme Execution Desk (Ban 8) & Palmer Governance Desk
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

    plan_text = (
        "🎯 *[BỘ CHỈ HUY MASTER CIO JAMES — BẢN KẾ HOẠCH TÁC CHIẾN CHỐT HẠ PHIÊN SÁNG (06/11)]*\n"
        "🏛️ *Cơ quan*: Master CIO Supreme Execution Desk (Ban 8) & Palmer Governance Desk\n"
        "👤 *Kính trình*: Chủ tịch Phước Trần (Tài khoản TCBS: `105C307855`)\n"
        "⏰ *Thời điểm*: 08h35 Sáng Thứ Sáu 06/11/2026 | Khóa cứng 100% Kịch Bản A\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔒 *I. NGUYÊN TẮC THỂ CHẾ BẤT BIẾN (ZERO NƯỚC ĐÔI)*:\n"
        "• Thực thi nghiêm túc chỉ đạo của Chủ tịch: *Không có phương án gồng 50% sang tuần sau*.\n"
        "• **CHỈ CÓ DUY NHẤT 1 MỆNH LỆNH**: **BÁN HẾT 100% TOÀN BỘ 900 CỔ PHIẾU (400 HPG, 300 TCB, 200 MBB) TRONG KHUNG GIỜ VÀNG 09H15 – 09H45 SÁNG NAY!**\n\n"
        "📊 *II. CHI TIẾT 3 LỆNH BÁN LO CHỐT ĐỈNH HƯNG PHẤN*:\n"
        "1️⃣ `MBB` (200 CP | Giá vốn `18.61` | Hiện tại `19.50`):\n"
        "   - **Hành động**: *BÁN HẾT 200 CP* bằng lệnh LO\n"
        "   - **Vùng giá đặt**: *`19.80 – 20.00 ₫`* (Lãi `+6.4% đến +7.5%`)\n"
        "   - **Tiền thu về**: `~3,960,000 ₫` (Lãi ròng: `+238,000 ₫ đến +278,000 ₫`)\n\n"
        "2️⃣ `TCB` (300 CP | Giá vốn `21.36` | Hiện tại `21.95`):\n"
        "   - **Hành động**: *BÁN HẾT 300 CP* bằng lệnh LO\n"
        "   - **Vùng giá đặt**: *`22.30 – 22.50 ₫`* (Lãi `+4.4% đến +5.3%`)\n"
        "   - **Tiền thu về**: `~6,700,000 ₫` (Lãi ròng: `+282,000 ₫ đến +342,000 ₫`)\n\n"
        "3️⃣ `HPG` (400 CP | Giá vốn `21.16` | Hiện tại `21.50`):\n"
        "   - **Hành động**: *BÁN HẾT 400 CP* bằng lệnh LO\n"
        "   - **Vùng giá đặt**: *`21.80 – 22.00 ₫`* (Lãi `+3.0% đến +4.0%`)\n"
        "   - **Tiền thu về**: `~8,720,000 ₫` (Lãi ròng: `+256,000 ₫ đến +336,000 ₫`)\n\n"
        "💰 *THÀNH QUẢ TỔNG KẾT SAU KHI BÁN HẾT*:\n"
        "👉 *Tổng lợi nhuận ròng thu về*: *`+750,000 ₫ đến +950,000 ₫`* tiền tươi thóc thật!\n"
        "👉 *Quy toàn bộ tài khoản về*: *`~20,500,000 ₫ TIỀN MẶT (100% Cash)`*, xóa sạch mọi rủi ro thị trường đảo chiều chiều Thứ Sáu!\n\n"
        "⏱️ *III. LỘ TRÌNH TÁC CHIẾN CẢ NGÀY HÔM NAY (THỰC HIỆN NGHIÊM TÚC)*:\n"
        "• *08:45*: Master CIO James xuất bản Sổ Lệnh Master Blotter chính thức.\n"
        "• *09:00*: Mở phiên ATO, kích hoạt GUARD-01 khóa cứng lệnh mua đuổi.\n"
        "• *09:15 – 09:45*: Master CIO James bắn giá đỉnh để Chủ tịch đặt 3 lệnh BÁN HẾT 100% trên app TCBS.\n"
        "• *11:45*: Báo cáo Flash chốt phiên sáng & kiểm toán tiền về tài khoản.\n"
        "• *13:45 – 14:20*: Khung Giờ Vàng phiên chiều ➔ Quan sát nhịp xả hàng Weekend De-risking để lọc hàng chiết khấu gom cho tuần tới (`DBC`, `FPT`).\n"
        "• *14:25*: Cầu chì an toàn GUARD-03 khóa danh mục trước ATC.\n"
        "• *15:15*: Ban 5 hồi tố hiệu suất tổng kết tuần đại thắng.\n"
        "• *18:00*: Ban 10 cập nhật Thư viện BCTC Master.\n"
        "• *21:00*: Hiền báo cáo BCTC độc quyền.\n"
        "• *21:15*: Khánh & Bảo ra video viral 60s.\n"
        "• *22:00*: Giờ tự học viện sĩ.\n"
        "• *23:00*: Giao ban đêm EOD.\n\n"
        "👉 Hệ thống cam kết thực thi kỷ luật sắt, không dao động, báo cáo song song 100%!"
    )

    print("[*] Dispatching Locked Morning Plan to Telegram...")
    ok_james = dispatch_message("james_hq", plan_text)
    ok_blotter = dispatch_message("morning_blotter", plan_text)
    ok_p = send_raw_telegram(bot_token, str(private_chat_id), plan_text, parse_mode="Markdown")

    print(f"[+] Dispatch Results: JamesHQ={ok_james}, Blotter={ok_blotter}, Private={ok_p}")
    return 0 if (ok_james and ok_blotter and ok_p) else 1

if __name__ == "__main__":
    sys.exit(main())
