#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DISPATCH FULL INSTITUTIONAL 08:30 WAR ROOM REPORT TO TELEGRAM JAMES HQ, BLOTTER & PRIVATE CHAT
File: scripts/dispatch_milestone_0830_war_room.py
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

    # Đọc telemetry chốt hôm qua
    telemetry_path = BASE_DIR / "09_Realtime_Portfolio_Sentinel" / "vn3_live_telemetry.json"
    tcb_p = 21950
    mbb_p = 19500
    hpg_p = 21500
    total_val = 19085000
    total_pnl = 494600
    pnl_pct = 2.66

    if telemetry_path.exists():
        try:
            with open(telemetry_path, "r", encoding="utf-8") as f:
                tdata = json.load(f)
                quotes = tdata.get("quotes", {})
                tcb_p = quotes.get("TCB", {}).get("price", tcb_p)
                mbb_p = quotes.get("MBB", {}).get("price", mbb_p)
                hpg_p = quotes.get("HPG", {}).get("price", hpg_p)
                summary = tdata.get("portfolio_summary", {})
                total_val = summary.get("total_market_value_vnd", total_val)
                total_pnl = summary.get("total_unrealized_pnl_vnd", total_pnl)
                pnl_pct = summary.get("total_unrealized_pnl_pct", pnl_pct)
        except Exception as e:
            print(f"[!] Warning reading telemetry: {e}")

    report_text = (
        "☀️ *[BAN 7 VN & BAN 8 — BIÊN BẢN GIAO BAN SOI GƯƠNG SÁNG 08H30 (06/11/2026)]*\n"
        "🏛️ *Chủ tọa*: Master CIO James & Palmer | Chuyên viên thực thi: Minh Quân (Ban 7 VN)\n"
        "👤 *Kính trình*: Chủ tịch Phước Trần (Tài khoản TCBS: `105C307855`)\n"
        "⏰ *Thời điểm*: `08:30:00 AM` — Chuẩn bị thềm mở phiên ATO Thứ Sáu\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🛡️ *1. TUYÊN THỆ KỶ LUẬT THÉP & KHÓA CỨNG KỊCH BẢN A*:\n"
        "• *Lời thề Chuyên viên Minh Quân*: Tiếp thu 100% lời rèn giũa của Chủ tịch sáng nay, xóa bỏ triệt để tâm lý tham lam & tiếc rẻ.\n"
        "• *Khóa chết 1 Quyết nghị duy nhất*: **BÁN HẾT 100% TOÀN BỘ 900 CỔ PHIẾU (400 HPG, 300 TCB, 200 MBB) TRONG KHUNG GIỜ VÀNG 09H15 – 09H45 SÁNG NAY!**\n"
        "• Không dao động, không để lại 50% gồng sang tuần sau, triệt tiêu 100% rủi ro Weekend Risk!\n\n"
        "💎 *2. HIỆN TRẠNG KHO HÀNG TRƯỚC GIỜ G (100% ĐƯỢC GIAO DỊCH)*:\n"
        f"• `MBB`: 200 CP | Giá vốn `18.61` ➔ Thị giá `{mbb_p:,.0f} ₫` | Lãi: `+178,800 ₫ (+4.80%)` 🟢\n"
        f"• `TCB`: 300 CP | Giá vốn `21.36` ➔ Thị giá `{tcb_p:,.0f} ₫` | Lãi: `+178,200 ₫ (+2.78%)` 🟢\n"
        f"• `HPG`: 400 CP | Giá vốn `21.16` ➔ Thị giá `{hpg_p:,.0f} ₫` | Lãi: `+137,600 ₫ (+1.63%)` 🟢\n"
        f"👉 *Tổng giá trị*: `{total_val:,.0f} ₫` | Lãi hiện tại: *`+{total_pnl:,.0f} ₫ (+{pnl_pct:.2f}%)`*\n"
        "👉 *Tiền mặt*: `1,409,425 ₫` | *Tổng NAV*: `20,494,425 ₫`\n\n"
        "⛔ *3. KÍCH HOẠT 2 CẦU CHÌ AN TOÀN TRƯỚC GIỜ ATO*:\n"
        "1️⃣ **Cầu chì GUARD-01 (09h00 - 09h15)**: Tuyệt đối NGHIÊM CẤM đặt lệnh mua đuổi giá xanh tím trong phiên ATO.\n"
        "2️⃣ **Cầu chì LO-Order**: 100% lệnh chốt lời phải sử dụng lệnh Giới hạn (LO), không dùng lệnh MP.\n\n"
        "⏰ *LỘ TRÌNH TIẾP THEO*:\n"
        "• *08:45*: Master CIO James xuất bản Sổ Lệnh Master Blotter chốt mức giá bán đỉnh chi tiết.\n"
        "• *09:15*: Khởi động Khung Giờ Vàng bấm cò lệnh bán sạch 100%!\n\n"
        "👉 Báo cáo chi tiết đã lưu: `08_Master_Investment_CIO/2026-11-06_Morning_War_Room_Pact.md`"
    )

    print("[*] Dispatching Milestone 08:30 War Room report to Telegram...")
    # Dispatch to James HQ (Topic 6)
    ok_james = dispatch_message("james_hq", report_text)
    # Dispatch to Morning Blotter (Topic 4)
    ok_blotter = dispatch_message("morning_blotter", report_text)
    # Dispatch to Private Chat (Push Notification for Chairman's mobile)
    ok_private = send_raw_telegram(bot_token, str(private_chat_id), report_text, parse_mode="Markdown")

    print(f"[+] Milestone 08:30 Dispatch Results: JamesHQ={ok_james}, Blotter={ok_blotter}, Private={ok_private}")
    return 0 if (ok_james and ok_blotter and ok_private) else 1

if __name__ == "__main__":
    sys.exit(main())
