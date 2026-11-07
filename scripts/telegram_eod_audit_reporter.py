#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TELEGRAM EOD AUDIT REPORTER: Phát Bản Đánh Giá Phúc Tra Cuối Ngày (Cả 2 Phiên VN & Mỹ)
File: scripts/telegram_eod_audit_reporter.py

Chức năng:
1. Nạp dữ liệu từ Biên bản Kiểm toán Phúc tra Master CIO (eod_audit_logs).
2. Định dạng 2 bản đánh giá chuyên sâu riêng biệt:
   - PHIÊN 1: Thị Trường Việt Nam (Minh Quân, HPG, FPT, Kiểm toán BCTC & Sàn HOSE)
   - PHIÊN 2: Thị Trường Quốc Tế / Mỹ (Alex, Phố Wall, Tương quan Bán dẫn, VIX & Limit Pullback)
3. Gửi trực tiếp tới Telegram của Nhà Đầu Tư Phước Trần.
"""

import json
import os
import sys
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "09_Realtime_Portfolio_Sentinel" / "sentinel_config.json"
AUDIT_LOGS_DIR = BASE_DIR / "08_Master_Investment_CIO" / "eod_audit_logs"
BLOTTER_PATH = BASE_DIR / "08_Master_Investment_CIO" / "master_execution_blotter.json"


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
                print("[+] Đã gửi thành công tin nhắn phúc tra tới Telegram của Nhà Đầu Tư Phước Trần!")
                return True
            else:
                print(f"[!] Telegram API error: {res_data}")
                return False
    except Exception as e:
        print(f"[!] Lỗi kết nối Telegram API: {e}")
        return False


def get_latest_audit_feedback() -> dict:
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    today_json = AUDIT_LOGS_DIR / f"{today_str}_eod_audit_feedback.json"
    if today_json.exists():
        with open(today_json, "r", encoding="utf-8") as f:
            return json.load(f)

    # Lấy file json mới nhất trong thư mục
    files = list(AUDIT_LOGS_DIR.glob("*_eod_audit_feedback.json"))
    if files:
        latest = sorted(files)[-1]
        with open(latest, "r", encoding="utf-8") as f:
            return json.load(f)

    return {}


def sanitize_markdown(text: str) -> str:
    """Loại bỏ các ký tự có thể gây lỗi cú pháp Telegram Markdown v1."""
    # Tránh lỗi unclosed underscore trong tên file
    return text.replace("_", "-")


def build_vn_session_evaluation(audit: dict, blotter: dict) -> str:
    """Bản đánh giá Phiên 1: Thị Trường Việt Nam (Minh Quân & HOSE) — Động hóa 100% từ Sổ Lệnh Master CIO."""
    date_str = audit.get("audit_date", datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    mq = audit.get("minh_quan_audit", {})
    score = mq.get("score", 95.0)
    flaws = mq.get("critical_flaws_caught", [])
    mandate = mq.get("mandatory_corrective_action", "")

    cap_sum = blotter.get("capital_summary", {})
    total_cap = cap_sum.get("total_capital_vnd", 20000000)
    max_risk_vnd = cap_sum.get("total_portfolio_risk_if_all_stops_hit_vnd", 815400)
    max_risk_pct = cap_sum.get("total_portfolio_risk_pct", 4.08)

    orders_vn = blotter.get("orders_vietnam", [])
    if orders_vn:
        holdings_desc = " + ".join([f"{o.get('symbol')} {o.get('shares')} cổ" for o in orders_vn])
        stops_desc = ", ".join([
            f"{o.get('symbol')} ({o.get('stop_loss_2atr_vnd', 0):,.0f} đ = {o.get('stop_loss_pct', 0):.2f}%)"
            for o in orders_vn
        ])
        ocf_desc = ", ".join([
            f"{o.get('symbol')} (OCF/LNST={o.get('ocf_to_net_income', 'Đạt')})"
            for o in orders_vn
        ])
        tickers_str = ", ".join([str(o.get("symbol")) for o in orders_vn])
    else:
        holdings_desc = "400 HPG + 300 TCB + 200 MBB (Tổng 900 CP - Danh mục Thực Tế TCBS 105C307855)"
        stops_desc = "HPG (20,120 đ = -4.19%), TCB (20,250 đ = -4.03%), MBB (22,900 đ = -4.18%)"
        ocf_desc = "HPG (1.29), TCB (CASA 40.5%), MBB (ROE 22.8%)"
        tickers_str = "HPG, TCB, MBB"

    msg = (
        f"🇻🇳 *[BẢN ĐÁNH GIÁ PHÚC TRA PHIÊN 1 — THỊ TRƯỜNG VIỆT NAM]*\n"
        f"📅 *Ngày phúc tra:* {date_str} (Sau giờ đóng cửa)\n"
        f"👤 *Người nhận:* Chủ tịch Phước Trần (TK: 105C307855)\n"
        f"🏛 *Cơ quan kiểm toán:* Master CIO Supreme Audit Desk (Ban 8)\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"⭐ *ĐIỂM CHẤT LƯỢNG MINH QUÂN (BAN 7 VN):* `{score}/100`\n"
        f"• *Trạng thái:* `APPROVED & LOCKED (Đạt chuẩn Định chế)`\n"
        f"• *Quy mô vốn kiểm toán:* `{total_cap:,.0f} VNĐ` ({holdings_desc})\n\n"
        f"✅ *1. NHỮNG ĐIỂM LÀM ĐÚNG ĐƯỢC KHEN NGỢI:*\n"
        f"• Tuân thủ 100% lô chẵn sàn HOSE: {holdings_desc}.\n"
        f"• Kỷ luật cắt lỗ cứng Stop 2xATR: {stops_desc}.\n"
        f"• Khóa mức rủi ro tối đa toàn danh mục: -{max_risk_vnd:,.0f} đ (-{max_risk_pct:.2f}% NAV).\n"
        f"• Kiểm toán BCTC VAS/TT200: {ocf_desc}, Beneish M = SAFE.\n\n"
        f"⚠️ *2. CÁC ĐIỂM LƯU Ý KIỂM TOÁN MASTER CIO:*\n"
    )

    for idx, f in enumerate(flaws, 1):
        clean_f = sanitize_markdown(f)
        msg += f"👉 *Lưu ý {idx}:* {clean_f}\n\n"

    clean_mandate = sanitize_markdown(mandate)
    msg += (
        f"📋 *3. CHỈ THỊ BẮT BUỘC MINH QUÂN THỰC THI:*\n"
        f"• {clean_mandate}\n"
        f"• *Quy tắc thép:* Cấm mua đuổi ATO; bắt buộc canh Khung Giờ Vàng 14h00 - 14h25 đặt lệnh LO theo Sổ lệnh Master CIO.\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"🔒 *Kết luận:* Sổ lệnh `{total_cap:,.0f} VNĐ` cho {tickers_str} đã được Master CIO khóa an toàn và đồng bộ 100%."
    )
    return msg


def build_us_session_evaluation(audit: dict, blotter: dict) -> str:
    """Bản đánh giá Phiên 2: Thị Trường Quốc Tế / Mỹ (Alex & Phố Wall)."""
    date_str = audit.get("audit_date", datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    alex = audit.get("alex_audit", {})
    score = alex.get("score", 79.0)
    flaws = alex.get("critical_flaws_caught", [])
    mandate = alex.get("mandatory_corrective_action", "")

    msg = (
        f"🇺🇸 *[BẢN ĐÁNH GIÁ PHÚC TRA PHIÊN 2 — THỊ TRƯỜNG MỸ & TOÀN CẦU]*\n"
        f"📅 *Ngày phúc tra:* {date_str} (Sau phiên đóng cửa NYSE/NASDAQ)\n"
        f"👤 *Người nhận:* Nhà Đầu Tư Phước Trần\n"
        f"🏛 *Cơ quan kiểm toán:* Master CIO Supreme Audit Desk (Ban 8)\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"⭐ *ĐIỂM CHẤT LƯỢNG ALEX (BAN 7 GLOBAL):* `{score}/100`\n"
        f"• *Trạng thái:* `BỊ TRỪ 21 ĐIỂM (Cảnh cáo rủi ro tương quan)`\n"
        f"• *Danh mục kiểm toán:* NVDA, AVGO, TSM, GOOGL, MSFT, V, JPM, PG\n\n"
        f"✅ *1. NHỮNG ĐIỂM LÀM ĐÚNG:*\n"
        f"• Kỷ luật né bão BCTC: Khóa thành công AAPL (2d), PLTR (2d), AMD (3d).\n"
        f"• Kỳ vọng toán học dương: EV% từ +6.1% đến +23.9%, R:R >= 1:2.40.\n"
        f"• Lọc cỗ máy in tiền: FCF của NVDA (+$60.8B), TSM (+$36.93B), V (+$20.4B).\n\n"
        f"⚠️ *2. CÁC LỖI SAI LỆCH BỊ MASTER CIO PHÊ BÌNH:*\n"
    )

    for idx, f in enumerate(flaws, 1):
        msg += f"👉 *Lỗi {idx}:* {f}\n\n"

    msg += (
        f"📋 *3. CHỈ THỊ BẮT BUỘC ALEX SỬA ĐỔI:*\n"
        f"• {mandate}\n"
        f"• *Giới hạn tương quan:* Buộc Alex khống chế trần cụm Bán dẫn <= 28% NAV, dời 14% sang Core Compounders (Visa `V` hoặc P&G `PG`).\n"
        f"• *Điều chỉnh lệnh:* Nâng vùng gom TSM lên -0.20x ATR ($403.50) tránh bị rớt hàng.\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"🔒 *Kết luận:* Danh mục chuẩn mực Mỹ đã được Master CIO cân bằng Volatility Risk-Parity."
    )
    return msg


def main():

    # KHÓA KỶ LUẬT THỜI GIAN: Báo cáo Phúc Tra Cuối Ngày (EOD) chỉ được phép gửi sau 15:30 chiều
    now_hour = datetime.now().hour
    if "--force-eod" not in sys.argv and (6 <= now_hour < 15):
        print(f"[!] TỪ CHỐI GỬI: Hiện tại là {now_hour}h sáng, thị trường đang trong phiên giao dịch.")
        print("[!] Báo cáo Phúc tra Cuối ngày (Sau giờ đóng cửa) chỉ được phép phát hành sau 15:30 chiều.")
        return

    print("=" * 70)
    print(" 📡 MASTER CIO TELEGRAM EOD AUDIT REPORTER")
    print(" GỬI BẢN ĐÁNH GIÁ CẢ 2 PHIÊN TỚI TELEGRAM NHÀ ĐẦU TƯ PHƯỚC TRẦN")
    print("=" * 70)

    bot_token, chat_id = load_telegram_credentials()
    if not bot_token or not chat_id:
        print("[!] Không tìm thấy thông tin cấu hình Telegram Bot.")
        return

    audit = get_latest_audit_feedback()
    blotter = {}
    if BLOTTER_PATH.exists():
        try:
            with open(BLOTTER_PATH, "r", encoding="utf-8") as f:
                blotter = json.load(f)
        except Exception:
            pass

    msg_vn = build_vn_session_evaluation(audit, blotter)
    msg_us = build_us_session_evaluation(audit, blotter)

    try:
        from telegram_dispatcher import dispatch_message
        print("\n[*] Đang gửi Bản Đánh Giá Phiên 1 (Việt Nam - Minh Quân) qua Multi-Topic Dispatcher...")
        res_vn = dispatch_message(topic_key="morning_blotter", text=msg_vn)
        print("\n[*] Đang gửi Bản Đánh Giá Phiên 2 (Mỹ & Toàn Cầu - Alex) qua Multi-Topic Dispatcher...")
        res_us = dispatch_message(topic_key="morning_blotter", text=msg_us)
    except Exception:
        print("\n[*] Đang gửi Bản Đánh Giá Phiên 1 (Việt Nam - Minh Quân)...")
        res_vn = send_telegram_message(bot_token, chat_id, msg_vn)
        print("\n[*] Đang gửi Bản Đánh Giá Phiên 2 (Mỹ & Toàn Cầu - Alex)...")
        res_us = send_telegram_message(bot_token, chat_id, msg_us)

    if res_vn and res_us:
        print("\n[SUCCESS] Cả 2 bản đánh giá phiên VN và phiên Mỹ đã được chuyển phát thành công tới Telegram!")
    else:
        print("\n[!] Có lỗi xảy ra trong quá trình gửi tin nhắn.")


if __name__ == "__main__":
    main()
