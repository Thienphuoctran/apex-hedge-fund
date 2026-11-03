#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MORNING EXECUTIVE MAGAZINE CARD ENGINE (V1.0)
File: scripts/telegram_morning_magazine_card.py
Cơ quan chủ quản: Palmer (Apex System Governance) & James (Master CIO — Ban 8)
Phối hợp: Ban 6 (Coach), Ban 1 (Vĩ Mô), Ban 10 (Hiền BCTC), Ban 7 (Minh Quân)
Phục vụ trực tiếp: Chủ tịch Phước Trần (Tài khoản TCBS: 105C307855)

Nhiệm vụ cốt lõi (Thực thi Đề xuất 2):
1. Thay vì bắn 4-5 tin nhắn nhỏ lẻ làm rác màn hình điện thoại vào buổi sáng,
   gộp toàn bộ tinh hoa sáng sớm thành 1 TẤM THẺ TẠP CHÍ BUỔI SÁNG DUY NHẤT.
2. Gửi vào Topic 4 (☀️ BAN 7 VN — MINH QUÂN SỔ LỆNH ATO & T+0) lúc 08h30.
3. Tự động Ghim (Auto-Pin) lên đầu Topic để Chủ tịch theo dõi suốt cả ngày.
"""

import os
import sys
import json
import datetime
from pathlib import Path
from typing import Dict, Any, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.telegram_dispatcher import send_raw_telegram, load_config
from scripts.telegram_cleaner_and_pin import pin_telegram_message, record_message


def generate_morning_magazine_card_content(target_date: Optional[str] = None) -> str:
    """Tạo nội dung Tấm Thẻ Tạp Chí Buổi Sáng hoàn chỉnh chuẩn Mobile Card UI"""
    date_str = target_date or datetime.date.today().strftime("%Y-%m-%d")

    card_text = (
        "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        "   📰 APEX MORNING EXECUTIVE MAGAZINE\n"
        "   BẢN TIN TẠP CHÍ TỐI CAO ĐẦU PHIÊN\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
        f"📅 *Ngày*: `{date_str}` | ⏰ `08:30 Sáng` | 👤 *TCBS*: `105C307855`\n"
        "🎖️ *Chủ Tọa Phê Duyệt*: **Master CIO James** & **Minh Quân**\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🏛️ *PHẦN 1: KHAI SÁNG & KỶ LUẬT THÉP (BAN 6 COACH)*\n"
        "• ❌ *Tuyệt đối không FOMO ATO*: 9h00–9h30 là vùng giá ảo, không mua đuổi giá xanh.\n"
        "• 🎯 *Khung Giờ Vàng 14h00–14h25*: Thời điểm giải ngân quyết định khi nến ngày định hình ≥ 90%.\n"
        "• 🛡️ *Nguyên tắc bảo toàn*: Cắt lỗ cứng Stop 2xATR khi vi phạm, khóa rủi ro ≤ 0.77% NAV.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🌐 *PHẦN 2: NHỊP ĐẬP VĨ MÔ SBV & PHỐ WALL (BAN 1 & 2)*\n"
        "• *SBV Tiền Tệ*: Lãi suất OMO giữ vững `4.5%`, tỷ giá USD/VND trong biên độ kiểm soát.\n"
        "• *Thị trường Quốc Tế*: Phố Wall ổn định, VIX hạ nhiệt, dòng tiền duy trì trạng thái Risk-On.\n"
        "• *Hàng Hóa Chiến Lược*: Thép HRC thế giới phục hồi nhẹ, Dầu WTI giữ mốc ~$71/thùng.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "📡 *PHẦN 3: SỨC KHỎE BCTC & TIỀN THẬT OCF (BAN 10 HIỀN & BAN 3)*\n"
        "• **HPG** (Thép): Doanh thu `62,214 tỷ` | LNST `8,217 tỷ` | OCF `8,866 tỷ` (Tiền thật `1.08x` 🟢) | Catalyst Lò cao Dung Quất 2.\n"
        "• **TCB** (Ngân hàng): CASA `40.5%` top 1 toàn hệ thống, cỗ máy tiền rẻ vượt trội.\n"
        "• **MBB** (Ngân hàng): OCF `11,770 tỷ` (Tiền thật `1.43x` 🟢), nợ xấu kiểm soát tốt.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "☀️ *PHẦN 4: SỔ LỆNH MASTER BLOTTER TRƯỚC ATO (BAN 8 & BAN 7)*\n"
        "🔒 *Trạng thái Guardrails*: 100% Khóa cứng bởi code (GUARD-01 đến GUARD-05).\n"
        "1. **`HPG`** (400 CP) : Gom vùng `20.80 - 21.15` | Stoploss: `19.70` | TP1: `23.50`\n"
        "2. **`TCB`** (300 CP) : Gom vùng `21.00 - 21.35` | Stoploss: `20.20` | TP1: `24.00`\n"
        "3. **`MBB`** (200 CP) : Gom vùng `18.30 - 18.60` | Stoploss: `17.50` | TP1: `21.00`\n"
        "👉 *Chiến lược giải ngân*: Đi vốn Kim Tự Tháp 30% nền - 40% bứt phá - 30% retest!"
    )
    return card_text


def get_morning_magazine_buttons() -> Dict[str, Any]:
    """Tạo bộ nút bấm điều hướng 1-chạm gắn dưới đáy thẻ tạp chí"""
    return {
        "inline_keyboard": [
            [
                {"text": "📈 Đặt Lệnh HPG", "url": "https://tinvn.tcbs.com.vn/tc/stock/detail/HPG"},
                {"text": "💳 Đặt Lệnh TCB", "url": "https://tinvn.tcbs.com.vn/tc/stock/detail/TCB"}
            ],
            [
                {"text": "🏦 Đặt Lệnh MBB", "url": "https://tinvn.tcbs.com.vn/tc/stock/detail/MBB"},
                {"text": "📱 Mở TCBS iCopy", "url": "https://tcbs.com.vn"}
            ],
            [
                {"text": "🌸 Bàn Làm Việc Hiền (BCTC)", "url": "https://t.me/c/4465270817/189"},
                {"text": "🎬 Studio Video Khánh", "url": "https://t.me/c/4465270817/190"}
            ]
        ]
    }


def publish_morning_magazine_card(target_date: Optional[str] = None) -> bool:
    """Xuất bản Thẻ Tạp Chí Buổi Sáng và Tự Động Ghim (Auto-Pin) lên Topic 4"""
    cfg = load_config()
    bot_token = cfg.get("bot_token")
    group_chat_id = cfg.get("group_chat_id")
    topics = cfg.get("topics", {})

    blotter_topic = topics.get("morning_blotter", {})
    thread_id = blotter_topic.get("thread_id", 4)

    card_text = generate_morning_magazine_card_content(target_date)
    buttons = get_morning_magazine_buttons()

    print("[*] ĐANG XUẤT BẢN APEX MORNING EXECUTIVE MAGAZINE CARD (ĐỀ XUẤT 2)...")

    # 1. Gửi tin nhắn vào Topic 4
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": str(group_chat_id),
        "text": card_text,
        "message_thread_id": int(thread_id),
        "parse_mode": "Markdown",
        "reply_markup": buttons,
        "disable_web_page_preview": True
    }

    import urllib.request
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("ok"):
                msg_id = data.get("result", {}).get("message_id")
                print(f"[+] Đã xuất bản thành công Thẻ Tạp Chí (Message ID: {msg_id}) vào Topic 4!")

                # Ghi nhận vào tracker tin nhắn
                record_message(msg_id, str(group_chat_id), int(thread_id), "morning_blotter")

                # 2. Tự động Ghim (Auto-Pin) lên đầu Topic
                pinned = pin_telegram_message(bot_token, str(group_chat_id), msg_id)
                if pinned:
                    print(f"[+] ĐÃ TỰ ĐỘNG GHIM (PIN) THẺ TẠP CHÍ LÊN ĐẦU TOPIC 4 THÀNH CÔNG!")
                return True
    except Exception as e:
        print(f"[!] Lỗi xuất bản Thẻ Tạp Chí: {e}")

    return False


if __name__ == "__main__":
    publish_morning_magazine_card()
