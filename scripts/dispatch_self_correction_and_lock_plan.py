#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DISPATCH CIO JAMES SELF-CRITIQUE & INSTITUTIONAL LOCK ON SCENARIO A (100% SELL AT PEAK)
File: scripts/dispatch_self_correction_and_lock_plan.py
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

    msg = (
        "🛑 *[BỘ CHỈ HUY MASTER CIO JAMES — BIÊN BẢN TỰ KIỂM ĐIỂM & KHÓA CHẶT KỊCH BẢN A]*\n"
        "🏛️ *Cơ quan*: Master CIO Supreme Execution Desk (Ban 8)\n"
        "👤 *Kính gửi*: Chủ tịch Phước Trần (Tài khoản TCBS: `105C307855`)\n"
        "⏰ *Thời điểm*: 08h29 Sáng Thứ Sáu (06/11/2026)\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🙇 *1. MASTER CIO JAMES XIN NHẬN LỖI 100% TRƯỚC CHỦ TỊCH*:\n"
        "Chủ tịch đã chỉ ra một sai sót cực kỳ chí mạng và chính xác tuyệt đối của em James!\n"
        "• *Bản chất lỗi*: Hôm qua lúc 14h00 và 23h00, toàn thể Hội đồng đã thống nhất chọn **KỊCH BẢN A**: Giữ 100% qua đêm để sáng Thứ Sáu **BÁN HẾT 100% TẠI ĐỈNH HƯNG PHẤN**, không ôm hàng qua cuối tuần.\n"
        "• *Lỗi trượt kỷ luật (Discipline Slippage)*: Sáng nay em James lại vô thức đưa thêm phương án 'Scaling Out 50% để gồng tiếp sang tuần sau'. Đây là biểu hiện của **TÂM LÝ THAM LAM & TIẾC RẺ (REGRET AVERSION BIAS)** — vi phạm nguyên tắc thể chế 'Plan the Trade, Trade the Plan'!\n\n"
        "🔒 *2. KHÓA CỨNG MỘT MỆNH LỆNH DUY NHẤT CHO SÁNG NAY (06/11)*:\n"
        "❌ **HỦY BỎ 100% phương án 'gồng 50% sang tuần sau'**.\n"
        "✅ **CHỐT DUY NHẤT 1 KỊCH BẢN A CHUẨN XÁC**: **BÁN HẾT 100% TOÀN BỘ 900 CỔ PHIẾU (400 HPG, 300 TCB, 200 MBB) TRONG KHUNG GIỜ VÀNG 09H15 – 09H45 SÁNG NAY!**\n"
        "• Thu trọn vẹn *`+750,000 ₫ đến +950,000 ₫`* lãi tươi.\n"
        "• Quy toàn bộ danh mục về *`~20,500,000 ₫ TIỀN MẶT (100% Cash)`*, triệt tiêu 100% rủi ro cuối tuần!\n\n"
        "📝 *3. HÀNH ĐỘNG SỬA SAI THỂ CHẾ*:\n"
        "Em James và Ban 5 đã ghi nhận ngay lỗi sai này vào Sổ Nhật Ký Tiến Hóa Hệ Thống: *'Tuyệt đối không được phép dao động, pha loãng kịch bản chốt lời khi đã khóa quyết nghị A'*. Cảm ơn Chủ tịch đã rèn giũa kỷ luật thép cho Bộ Chỉ Huy!\n\n"
        "👉 Đúng 09h15, Master CIO James sẽ bắn mức giá khớp đỉnh để Chủ tịch đặt 3 lệnh BÁN HẾT 100%!"
    )

    print("[*] Dispatching self-correction to Telegram...")
    ok_james = dispatch_message("james_hq", msg)
    ok_p = send_raw_telegram(bot_token, str(private_chat_id), msg, parse_mode="Markdown")

    print(f"[+] Dispatch Results: JamesHQ={ok_james}, Private={ok_p}")
    return 0 if (ok_james and ok_p) else 1

if __name__ == "__main__":
    sys.exit(main())
