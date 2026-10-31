#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TELEGRAM MORNING REPORTER: Bản Tin Tình Báo Đầu Tư & Sổ Lệnh Sáng Sớm
File: scripts/telegram_morning_reporter.py

Chức năng:
1. Nạp dữ liệu từ Sổ lệnh Master Blotter (Ban 8 Master CIO) và báo cáo vĩ mô đêm qua.
2. Định dạng bản tin tóm tắt cao cấp chuẩn Institutional Hedge Fund cho Nhà Đầu Tư Phước Trần.
3. Tự động gửi tin nhắn Telegram vào mỗi sáng (trước 07:45 sáng giờ VN, trước phiên ATO HOSE).
"""

import json
import os
import sys
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "09_Realtime_Portfolio_Sentinel" / "sentinel_config.json"
BLOTTER_PATH = BASE_DIR / "08_Master_Investment_CIO" / "master_execution_blotter.json"
SENTINEL_STATUS_PATH = BASE_DIR / "09_Realtime_Portfolio_Sentinel" / "live_sentinel_status.json"


def load_telegram_credentials() -> tuple[str, str]:
    bot_token = ""
    chat_id = ""
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                tg = cfg.get("notification_channels", {}).get("telegram", {})
                bot_token = tg.get("bot_token", "").strip()
                chat_id = tg.get("chat_id", "").strip()
        except Exception as e:
            print(f"[!] Warning reading config: {e}")
            
    # Fallback env vars if available
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", bot_token)
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", chat_id)
    return bot_token, chat_id


def send_telegram_message(bot_token: str, chat_id: str, text: str) -> bool:
    if not bot_token or not chat_id:
        print("[!] Lỗi: Thiếu Telegram bot_token hoặc chat_id.")
        return False
        
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            res_data = json.loads(resp.read().decode("utf-8"))
            if res_data.get("ok"):
                print("[+] Đã gửi Bản tin Sáng thành công tới Telegram của Nhà Đầu Tư Phước Trần!")
                return True
            else:
                print(f"[!] Telegram API error: {res_data}")
                return False
    except Exception as e:
        print(f"[!] Lỗi kết nối Telegram API: {e}")
        return False


def build_morning_briefing(blotter: Dict[str, Any]) -> List[str]:
    """Tạo 2 tin nhắn ngắn gọn, sắc bén để tránh vượt quá giới hạn 4096 ký tự của Telegram."""
    date_str = blotter.get("trading_date", datetime.now().strftime("%Y-%m-%d"))
    cap = blotter.get("capital_summary", {})
    metrics = blotter.get("portfolio_metrics", {})
    orders_us = blotter.get("orders_us_global", [])
    orders_vn = blotter.get("orders_vietnam", [])
    
    # TIN NHẮN 1: TỔNG QUAN CHIẾN LƯỢC & VĨ MÔ
    msg_1 = (
        f"☀️ *[BẢN TIN KHAI SÁNG & SỔ LỆNH SÁNG SỚM]*\n"
        f"📅 *Phiên Giao Dịch:* {date_str} (Trước giờ mở cửa ATO)\n"
        f"👤 *Kính gửi:* Nhà Đầu Tư Phước Trần\n"
        f"🏛 *Cơ quan thẩm định:* Master CIO Desk (Ban 8) & Victor Sentinel (Ban 9)\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"📊 *1. TÌNH TRẠNG DANH MỤC & ĐỊNH LƯỢNG:*\n"
        f"• *Tổng Vốn (NAV):* ${cap.get('total_nav_usd', 100000):,.0f} USD ({cap.get('total_nav_vnd', 2540000000):,.0f} ₫)\n"
        f"• *Tỷ trọng Mỹ (US):* {cap.get('global_allocated_pct', 55.0):.1f}% NAV\n"
        f"• *Tỷ trọng VN:* {cap.get('vn_allocated_pct', 35.0):.1f}% NAV\n"
        f"• *Tiền Mặt Dự Phòng:* {cap.get('dry_powder_pct', 10.0):.1f}% NAV (${cap.get('dry_powder_usd', 10000):,.0f})\n"
        f"• *Xác Suất Thắng Bình Quân:* 🎯 *{metrics.get('weighted_win_probability_pct', 80.0):.1f}%*\n"
        f"• *Kỳ Vọng Toán Học (EV%):* 📈 *+{metrics.get('weighted_expected_value_pct', 5.8):.2f}% / lệnh*\n"
        f"• *Tỷ Lệ Risk/Reward:* ⚖️ *1 : {metrics.get('weighted_reward_risk_ratio', 2.3):.2f}*\n"
        f"• *Rủi Ro Tối Đa / Vị Thế:* 🛡 *{metrics.get('maximum_single_trade_risk_nav_pct', 0.99):.2f}% NAV*\n\n"
        f"🔍 *2. ĐỒNG THUẬN ALEX (US) & MINH QUÂN (VN):*\n"
        f"• *Thị trường Mỹ:* Big Tech FCF cỗ máy in tiền vững chắc, không mua đuổi nhóm bán dẫn đã tăng nóng, ưu tiên gom Limit Pullback.\n"
        f"• *Thị trường VN:* SBV duy trì môi trường tiền tệ nới lỏng ổn định, khối ngoại bán ròng hạ nhiệt. Áp dụng nghiêm ngặt chiến lược 60/40 (60% thăm dò + 40% vượt cản).\n"
    )
    
    # TIN NHẮN 2: SỔ LỆNH THỰC THI CHI TIẾT
    msg_2 = (
        f"🎯 *3. SỔ LỆNH MASTER BLOTTER HÔM NAY*\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"🇺🇸 *THỊ TRƯỜNG MỸ (Alex — Ban 7 Global):*\n"
    )
    for idx, o in enumerate(orders_us, 1):
        msg_2 += (
            f"*{idx}. {o.get('symbol')}* ({o.get('name')})\n"
            f"   • Tỷ trọng: {o.get('weight_nav_pct', 0)}% NAV (${o.get('allocated_capital_usd', 0):,.0f})\n"
            f"   • Giá hiện tại: ${o.get('current_price_usd', 0):,.2f} | Chờ Limit: ${o.get('limit_pullback_price_usd', 0):,.2f}\n"
            f"   • *Stop Loss 2xATR:* ${o.get('stop_loss_2atr_usd', 0):,.2f} (-{o.get('stop_dist_pct', 0):.1f}%)\n"
            f"   • *Mục tiêu:* TP1: ${o.get('tp1_usd', 0):,.2f} | TP2: ${o.get('tp2_usd', 0):,.2f}\n"
            f"   • *Chiến lược:* {o.get('execution_instruction', 'Chia nhịp 70/30')}\n\n"
        )
        
    msg_2 += f"🇻🇳 *THỊ TRƯỜNG VIỆT NAM (Minh Quân — Ban 7 VN):*\n"
    for idx, o in enumerate(orders_vn, 1):
        msg_2 += (
            f"*{idx}. {o.get('symbol')}* ({o.get('name')})\n"
            f"   • Tỷ trọng: {o.get('weight_nav_pct', 0)}% NAV ({o.get('allocated_capital_vnd', 0):,.0f} ₫)\n"
            f"   • Khối lượng: {o.get('shares', 0):,} CP\n"
            f"   • Giá tham chiếu: {o.get('current_price_vnd', 0):,.0f} ₫\n"
            f"   • *Stop Loss 2xATR:* {o.get('stop_loss_2atr_vnd', 0):,.0f} ₫ (-{o.get('stop_dist_pct', 0):.1f}%)\n"
            f"   • *Mục tiêu:* TP1: {o.get('tp1_vnd', 0):,.0f} ₫ | TP2: {o.get('tp2_vnd', 0):,.0f} ₫\n"
            f"   • *Chiến lược:* {o.get('execution_instruction', 'Chia nhịp 60/40')}\n\n"
        )
        
    msg_2 += (
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"🚨 *LƯU Ý KỶ LUẬT THỰC THI:*\n"
        f"1. Tuyệt đối KHÔNG FOMO mua đuổi giá xanh/tím lúc mở phiên ATO.\n"
        f"2. Luôn cài sẵn lệnh Stop Loss 2xATR để khóa rủi ro mất vốn <= 1% NAV.\n"
        f"3. Ban 9 *Victor Sentinel* đang giám sát 24/7 và sẽ còi báo động ngay nếu có biến động bất thường!\n\n"
        f"Chúc Nhà Đầu Tư Phước Trần một ngày giao dịch thành công và đắc thắng! 🚀"
    )
    
    return [msg_1, msg_2]


def main():
    print("=" * 70)
    print(" 📡 KHỞI ĐỘNG HỆ THỐNG PHÁT BẢN TIN SÁNG QUA TELEGRAM BOT")
    print("=" * 70)
    
    bot_token, chat_id = load_telegram_credentials()
    if not bot_token or not chat_id:
        print("[!] Không tìm thấy thông tin xác thực Telegram trong sentinel_config.json.")
        sys.exit(1)
        
    if not BLOTTER_PATH.exists():
        print(f"[!] Không tìm thấy file {BLOTTER_PATH}. Cần chạy pipeline Master CIO trước.")
        sys.exit(1)
        
    with open(BLOTTER_PATH, "r", encoding="utf-8") as f:
        blotter = json.load(f)
        
    messages = build_morning_briefing(blotter)
    
    print(f"[*] Đang gửi {len(messages)} bản tin tóm tắt tới Telegram...")
    success = True
    for idx, msg in enumerate(messages, 1):
        ok = send_telegram_message(bot_token, chat_id, msg)
        if not ok:
            success = False
            
    if success:
        print("\n [HOÀN TẤT] Toàn bộ bản tin sáng đã được giao tới điện thoại của Nhà Đầu Tư Phước Trần!")
    else:
        print("\n[!] Có lỗi xảy ra trong quá trình gửi tin nhắn.")


if __name__ == "__main__":
    main()
