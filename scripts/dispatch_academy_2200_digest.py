#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DISPATCH ACADEMY 22H00 DEEP LEARNING DIGEST TO TELEGRAM TOPIC 112 (ACADEMY_LEARNING)
File: scripts/dispatch_academy_2200_digest.py
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

    msg = """🏛️ *[BAN 6 & BAN 5 — HỌC VIỆN HUẤN LUYỆN: PHIÊN TỰ NGHIÊN CỨU & NẠP TRI THỨC 22H00]*
👤 *Kính gửi*: **Chủ tịch Phước Trần** (*Tài khoản TCBS: `105C307855`*)
🧠 *Chỉ số IQ Tập thể Quỹ Apex*: 🌟 **`152.0 Điểm (+1.5 IQ / Tuần)`**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📖 *CHUYÊN ĐỀ ĐÊM NAY (THỨ TƯ)*:
**TOÁN HỌC ĐỊNH LƯỢNG & TỐI ƯU HÓA RỦI RO (QUANTITATIVE RISK PARITY)**
• *Ban chủ trì*: Ban 4 (Hội Đồng Quản Trị Rủi Ro Định Lượng) & Ban 6
• *Tài liệu gốc*: Lý thuyết Edward Thorp (A Man for All Markets) & Quỹ Medallion (Jim Simons)
• *Câu hỏi cốt lõi*: Làm thế nào để giải ngân tối ưu hóa tốc độ tăng trưởng vốn kép G(f) qua Kelly Criterion và ATR Risk-Parity mà không bao giờ cháy tài khoản?

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 *ỨNG DỤNG THỰC CHIẾN VÀO DANH MỤC 20 TRIỆU TCBS CỦA CHỦ TỊCH*:
1. 🛡️ **Khóa Rủi Ro Tối Đa 1.5% NAV**: Mức thua lỗ tối đa cho phép trên mỗi mã cổ phiếu (HPG, TCB, MBB) khi dính Stop Loss 2xATR được khống chế chặt chẽ ở mức <= 300.000 ₫.
2. 📐 **Lợi thế Bất Đối Xứng (Asymmetric Payoff)**: Quỹ Medallion chỉ cần tỷ lệ thắng 51% nhưng lợi nhuận đạt 66%/năm nhờ cắt lỗ cực nhanh và gồng lãi theo xu hướng. Danh mục của Chủ tịch hiện đạt 100% tỷ lệ xanh (+2.40% tổng vốn).
3. ⚡ **Chuẩn bị cho Ngày Mai T+2.5**: Chiều mai 13:00 cổ phiếu về tài khoản, sẵn sàng kích hoạt Scaling Out chốt lời 50% TP1 bảo toàn thành quả!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧠 *NẠP NGUYÊN LÝ THỂ CHẾ THỨ 12 VÀO BỘ NHỚ VĨNH VIỄN*:
*"Lợi nhuận là phù phiếm, dòng tiền mới là sự thật. Trong bất kỳ cuộc khủng hoảng nào, doanh nghiệp có OCF dương và tiền mặt dồi dào sẽ nuốt chửng các đối thủ đọng vốn ảo. Mọi quyết định giải ngân bắt buộc phải có chứng thực OCF >= 1.0!"*

📂 Toàn văn báo cáo nghiên cứu và hồ sơ IQ:
• `06_Investor_Academy_And_Mentorship/research_library/2026-11-04_Autonomous_Research_Digest.md`
• `data/apex_knowledge_vault/apex_institutional_encyclopedia.md`"""

    res1 = dispatch_message("academy_learning", msg)
    res2 = send_raw_telegram(bot_token, chairman_id, msg)
    print(f"Dispatch Academy Learning (Topic 112): {res1} | Private Chat: {res2}")

if __name__ == "__main__":
    main()
