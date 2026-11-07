#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DISPATCH KHÁNH 21H15 VIRAL VIDEO SCRIPT TO TELEGRAM KHANH_STUDIO (TOPIC 190)
File: scripts/dispatch_khanh_2115_video.py
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

    msg = """🎬 *[BAN 11 — KHÁNH & BẢO: XUẤT BẢN KỊCH BẢN VIDEO VIRAL 60S LÚC 21H15]*
👤 *Kính gửi*: **Chủ tịch Phước Trần** (*Tài khoản TCBS: `105C307855`*)
🏛 *Cơ quan sáng tạo*: Ban 11 — Khánh (Viral Content Creator) & Bảo (AI Video Production)
🤝 *Bảo chứng BCTC*: Ban 10 — Hiền (Apex Corporate Filings & IR Scout)
🎖 *Phê duyệt*: Master CIO James (Ban 8)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔥 *TIÊU ĐỀ VIDEO 9:16 (TIKTOK / REELS / SHORTS)*:
**SỰ THẬT VỀ 'CỖ MÁY IN TIỀN' HÒA PHÁT: LÃI 8.200 TỶ NHƯNG TIỀN THẬT VÀO TÀI KHOẢN LÀ BAO NHIÊU?**

📊 *SỐ LIỆU TIỀN THẬT 100% TỪ HIỀN (BAN 10)*:
• *Mã cổ phiếu*: **HPG** (CTCP Tập đoàn Hòa Phát — 400 CP trong danh mục)
• *Doanh thu*: `62,214.2 tỷ ₫` | *LNST*: `8,217.3 tỷ ₫`
• *Dòng tiền OCF thật*: `8,865.9 tỷ ₫` (**1.08x LNST** 🟢 Tiền tươi thóc thật)
• *Catalyst lớn*: Lò cao Dung Quất 2 bổ sung 5.6M tấn HRC/năm tài trợ bằng tiền tự có!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 *CẤU TRÚC 6 PHÂN CẢNH 60 GIÂY*:
1️⃣ `00:00 - 00:03` [🔥 HOOK]: *"Đừng mua Hòa Phát nếu chưa biết con số này! Công ty báo lãi 8.200 tỷ, nhưng tiền mặt thật chảy về két là bao nhiêu?"*
2️⃣ `00:04 - 00:18` [📊 CON SỐ GIẤY]: Mổ xẻ LNST 8,217 tỷ vs Dòng tiền kinh doanh OCF.
3️⃣ `00:19 - 00:36` [💎 TIỀN THẬT]: Bóc trần 8,865.9 tỷ tiền tươi thóc thật đổ về két, OCF/LNST = 1.08x.
4️⃣ `00:37 - 00:48` [🚀 DUNG QUẤT 2]: Cú hích lò cao 5.6M tấn HRC tài trợ bằng cỗ máy in tiền nội tại.
5️⃣ `00:49 - 00:55` [💡 INSIGHT]: OCF > LNST = Viên ngọc quý; OCF âm = Chạy ngay kẻo ăn bẫy xào nấu số liệu.
6️⃣ `00:56 - 01:00` [🎯 CTA & PHỄU ICOPY]: Kêu gọi bình luận vùng giá vốn & dẫn link iCopy TCBS `105C307855` kiếm thêm 3 - 4 triệu/tháng.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚙️ *BẢO (KỸ THUẬT DỰNG PHIM) ĐÃ HOÀN TẤT*:
✅ Đã xuất 6 file âm thanh Edge-TTS AI tiếng Việt tự nhiên (`vi-VN-NamMinhNeural`).
✅ Đã thiết kế 6 khung hình đồ họa tài chính 1080x1920 siêu nét tại `11_Viral_Content_Creation/assets/JOB-2026-11-04-HPG/`.
✅ Điểm tiềm năng Viral của James: 🌟 **95/100 (HIGH VIRALITY)** — **APPROVED FOR PRODUCTION**.

📂 Toàn văn kịch bản Shooting Script đã lưu trữ tại:
`11_Viral_Content_Creation/2026-11-04_Viral_Script_Khánh.md`
Chủ tịch có thể bấm máy quay trực tiếp hoặc sử dụng bộ asset để đăng tải ngay tối nay!"""

    res1 = dispatch_message("khanh_studio", msg)
    res2 = send_raw_telegram(bot_token, chairman_id, msg)
    print(f"Dispatch Khanh Studio (Topic 190): {res1} | Private Chat: {res2}")

if __name__ == "__main__":
    main()
