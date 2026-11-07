#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DISPATCH COACH 07H30 MORNING BRIEFING TO TELEGRAM TOPIC 112
File: scripts/dispatch_coach_0730_briefing.py
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

    msg = """🏛️ *[BAN 6 — BẢN TIN KHAI SÁNG BUỔI SÁNG (07H30 AM - THỨ NĂM 05/11/2026)]*
👤 *Kính gửi*: **Chủ tịch Phước Trần** (*Tài khoản TCBS: `105C307855`*)
🎓 *Người hướng dẫn*: Huấn Luyện Viên Trưởng Học Viện Đầu Tư Thực Chiến (Ban 6 VN)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 *3 NGUYÊN TẮC THÉP HÔM NAY (NGÀY T+2.5)*:
1. ❌ *TUYỆT ĐỐI KHÔNG FOMO ATO*: 9h00 - 9h30 là giờ tạo lập kê lệnh ảo thử cung cầu, không mua đuổi giá xanh tím.
2. 💰 *BẢO TOÀN THÀNH QUẢ VÒNG 1*: Tài khoản TCBS 105C307855 đang giữ vững 100% Tiền Mặt (20,167,119 ₫), 0 CP rủi ro sau khi đã tất toán Vòng 1 (+167,119 ₫).
3. 🎯 *KHUNG GIỜ VÀNG 14h00 - 14h25*: Chỉ giải ngân thăm dò Vòng 2 (HDB, MSH, BAF, IDC) khi bảng điện đạt đủ 7 điều kiện kiểm định và tỷ lệ R:R >= 1:2.0.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 *BÀI HỌC BCTC HÔM NAY*:
*'Doanh thu là phù phiếm, Lợi nhuận là ảo tưởng, chỉ có Tiền Mặt trong két sắt mới là Sự Thật.'*
• Luôn kiểm tra tỷ lệ OCF/LNST >= 1.0x (HPG đạt 1.08x, MBB đạt 1.43x).
• Tránh xa các doanh nghiệp có Khoản phải thu phình to và dòng tiền âm liên tục.

Chúc Chủ tịch một ngày giao dịch điềm tĩnh, tự tin và thắng lợi rực rỡ!"""

    res1 = dispatch_message("academy_learning", msg)
    res2 = send_raw_telegram(bot_token, chairman_id, msg)
    print(f"Dispatch Academy Learning (Topic 112): {res1} | Private Chat: {res2}")

if __name__ == "__main__":
    main()
