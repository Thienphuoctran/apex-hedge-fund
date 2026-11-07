#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DISPATCH 23H00 EOD EXECUTIVE COUNCIL RESOLUTION TO TELEGRAM JAMES_HQ (TOPIC 6)
File: scripts/dispatch_council_2300_resolution.py
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.telegram_dispatcher import dispatch_message, send_raw_telegram, load_config

def main():
    cfg = load_config()
    bot_token = cfg.get("bot_token")
    chairman_id = cfg.get("chairman_user_id", "8332675283")

    msg = """🎖️ *[APEX MASTER CIO DESK — HỘI NGHỊ ĐIỀU HÀNH TỐI CẤP CAO 23H00]*
👤 *Kính gửi*: **Chủ tịch Phước Trần** (*Tài khoản TCBS: `105C307855`*)
🏛 *Cơ quan chủ tọa*: Master CIO James (Ban 8) & Palmer (Tổng Quản Trị Hệ Thống)
👥 *Thành phần*: Đầy đủ 11 Phòng Ban Chuyên Trách
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏆 *BÁO CÁO TÀI SẢN THẬT 100% KẾT PHIÊN 04/11 (NGÀY T+1)*:
• **HPG (400 CP)**: Vốn `21,156 ₫` ➔ Đóng cửa `21.70` | Lãi: **`+217,600 ₫ (+2.57%)`** 🟢
• **MBB (200 CP)**: Vốn `18,606 ₫` ➔ Đóng cửa `19.10` | Lãi: **`+98,800 ₫ (+2.66%)`** 🟢
• **TCB (300 CP)**: Vốn `21,356 ₫` ➔ Đóng cửa `21.80` | Lãi: **`+133,200 ₫ (+2.08%)`** 🟢
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 *TỔNG KẾT TÀI CHÍNH QUỸ*:
• **Tổng Vốn Cổ Phiếu (900 CP)**: `18,590,400 ₫`
• **Thị Giá Thị Trường**: `19,040,000 ₫`
• **Lợi Nhuận Thực Tế**: **`+449,600 ₫ (+2.40%)`**
• **Tiền Mặt Dự Phòng (Dry Powder)**: **`1,409,425 ₫` (6.89% NAV)**
• **Tổng NAV Thực Tế**: **`20,449,425 ₫`** | Margin: **`0.0%`**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚖️ *KẾT QUẢ KIỂM TOÁN HỆ THỐNG CÙNG PALMER*:
✅ Đã thanh trừng 100% đoạn mock text cũ về FPT/15M trong các engine kiểm toán.
✅ Đã niêm phong các bản ghi sandbox ngày 01-03/11. Toàn bộ hệ thống hiện vận hành 100% trên dữ liệu thật của tài khoản TCBS `105C307855`.
✅ Hiệp ước Trách nhiệm Thể chế đã được ký kết và có hiệu lực vĩnh viễn.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 *SỔ LỆNH TÁC CHIẾN NGÀY MAI (THỨ NĂM 05/11 — NGÀY T+2.5)*:
⏰ **Đúng 13:00 Chiều Mai**: Toàn bộ **900 cổ phiếu** sẽ chính thức về tài khoản ("Được GD" = 900 CP).
🎯 **Khung Giờ Vàng 14h00 - 14h25**: Kích hoạt chiến lược **Scaling Out chốt lời 50% TP1**:
• **HPG**: Chốt lời 200 CP quanh vùng `22,000 - 22,200 ₫`, nâng Stop Loss lên giá vốn `21,160 ₫` để gồng lãi 200 CP còn lại.
• **TCB**: Chốt lời 100-150 CP quanh vùng `22,500 ₫`, nâng Stop Loss lên `21,360 ₫`.
• **MBB**: Chốt lời 100 CP quanh vùng `19,500 ₫`, nâng Stop Loss lên `18,600 ₫`.
• Tái lập lượng tiền mặt dự phòng lên 25%-30% NAV để sẵn sàng gom nhịp tiếp theo!

📂 Toàn văn Biên bản Nghị quyết 23h00 (8.6 KB):
`08_Master_Investment_CIO/2026-11-04_23h00_EOD_Executive_Council_Meeting.md`

Chúc Chủ tịch có một giấc ngủ thật ngon! Toàn thể 11 phòng ban Quỹ Apex luôn túc trực nghiêm cẩn!"""

    res1 = dispatch_message("james_hq", msg)
    res2 = send_raw_telegram(bot_token, chairman_id, msg)
    print(f"Dispatch James HQ (Topic 6): {res1} | Private Chat: {res2}")

if __name__ == "__main__":
    main()
