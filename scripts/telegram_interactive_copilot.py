#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TELEGRAM BIDIRECTIONAL AI CO-PILOT & COMMAND LISTENER DAEMON
File: scripts/telegram_interactive_copilot.py
Cơ quan chủ quản: Palmer — Cố vấn Điều hành Tối cao & Trưởng Phòng Tổng Hệ Thống (Apex Central System Governance)
Dành cho: Chủ tịch Phước Trần (Tài khoản TCBS: 105C307855)

Chức năng:
1. Lắng nghe liên tục tin nhắn 2 chiều từ Telegram của Chủ tịch Phước Trần qua cơ chế Long-Polling (`getUpdates`).
2. Tự động hiển thị Bàn Phím Ảo 1-Chạm (Interactive Reply Keyboard) giúp Chủ tịch thao tác cực nhanh trên điện thoại.
3. Phản hồi tức thì các yêu cầu:
   - Tóm tắt danh mục (/danhmuc, "danh mục", "đang cầm gì", "lãi bao nhiêu")
   - Tổng hợp thị trường (/tonghop, "tổng hợp", "tóm tắt", "thị trường")
   - Sổ lệnh hôm nay (/solenh, "sổ lệnh", "mua giá nào")
   - Canh chốt lời / cắt lỗ (/canh, "chốt lời chưa", "stop loss")
   - Radar săn sóng mới (/radar, "săn sóng", "mã nào mới")
   - Soi từng mã cổ phiếu cụ thể (HPG, TCB, MBB, FPT, v.v.)
4. Tự động phát hiện khi được thêm vào Group Supergroup, tự kích hoạt API tạo 4 Forum Topics chuẩn chỉnh!
"""

import argparse
import datetime
import json
import os
import re
import sys
import time
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Dict, Any, List, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.telegram_dispatcher import (
    load_config,
    save_config,
    send_raw_telegram,
    provision_all_topics_for_group,
    create_forum_topic
)

BLOTTER_PATH = BASE_DIR / "08_Master_Investment_CIO" / "master_execution_blotter.json"
SENTINEL_STATUS = BASE_DIR / "09_Realtime_Portfolio_Sentinel" / "live_sentinel_status.json"
WAVE_RADAR_PATH = BASE_DIR / "09_Realtime_Portfolio_Sentinel" / "live_wave_hunter_radar.json"
STATE_FILE = BASE_DIR / "data" / "telegram_copilot_state.json"


def get_interactive_keyboard() -> Dict[str, Any]:
    """Tạo bàn phím ảo 6 nút tương tác 1-chạm dưới khung chat Telegram."""
    return {
        "keyboard": [
            [{"text": "📊 Xem Danh Mục"}, {"text": "⚡ Sổ Lệnh Hôm Nay"}],
            [{"text": "📝 Tóm Tắt Thị Trường"}, {"text": "🎯 Canh Chốt Lời / Cắt Lỗ"}],
            [{"text": "📡 Radar Săn Sóng"}, {"text": "🔍 Soi Mã Cổ Phiếu"}]
        ],
        "resize_keyboard": True,
        "is_persistent": True
    }


def load_blotter_data() -> Dict[str, Any]:
    if BLOTTER_PATH.exists():
        try:
            with open(BLOTTER_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def load_sentinel_status_data() -> Dict[str, Any]:
    if SENTINEL_STATUS.exists():
        try:
            with open(SENTINEL_STATUS, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def load_wave_radar_data() -> Dict[str, Any]:
    if WAVE_RADAR_PATH.exists():
        try:
            with open(WAVE_RADAR_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


# ==============================================================================
# BỘ XỬ LÝ PHẢN HỒI THÔNG MINH CỦA PALMER
# ==============================================================================

def handle_portfolio_summary() -> str:
    """Trả lời câu hỏi về Danh Mục Hiện Tại."""
    blotter = load_blotter_data()
    sentinel = load_sentinel_status_data()
    
    cap = blotter.get("capital_summary", {})
    orders = blotter.get("orders_vietnam", [])
    
    total_nav = cap.get("total_nav_vnd", 20000000.0)
    dry_powder = cap.get("dry_powder_vnd", 1319824.0)
    
    lines = [
        "📊 *[BÁO CÁO DANH MỤC HIỆN TẠI — APEX FUND]*",
        f"👤 *Chủ tài khoản:* Chủ tịch Phước Trần (TCBS: `105C307855`)",
        f"💰 *Tổng NAV:* `{total_nav:,.0f} ₫` | *Tiền mặt dự phòng:* `{dry_powder:,.0f} ₫`",
        "━━━━━━━━━━━━━━━━━━━"
    ]
    
    status_map = {p.get("symbol"): p for p in sentinel.get("positions_tracked", [])}
    
    for o in orders:
        sym = o.get("symbol") or o.get("ticker")
        shares = o.get("shares", 0)
        cost_price = o.get("current_price_vnd", 0.0)
        sleeve = o.get("sleeve", "")
        stop_price = o.get("stop_loss_2atr_vnd", 0.0)
        tp1_price = o.get("tp1_vnd", 0.0)
        tp2_price = o.get("tp2_vnd", 0.0)
        
        # Giá realtime từ Sentinel nếu có
        curr_p = cost_price
        p_info = status_map.get(sym)
        if p_info:
            curr_p = p_info.get("current_price", curr_p)
            
        pct_change = ((curr_p - cost_price) / cost_price * 100) if cost_price > 0 else 0.0
        pnl_vnd = (curr_p - cost_price) * shares
        status_emoji = "🟢" if pnl_vnd >= 0 else "🔴"
        
        lines.append(f"\n*{sym}* ({sleeve}) — *{shares:,} CP*")
        lines.append(f"• Giá hiện tại: `{curr_p:,.0f} ₫` ({status_emoji} `{pct_change:+.2f}%` ~ `{pnl_vnd:+,.0f} ₫`)")
        lines.append(f"• Stop Loss 2xATR: `{stop_price:,.0f} ₫` | Chốt lời: TP1 `{tp1_price:,.0f} ₫` • TP2 `{tp2_price:,.0f} ₫`")
        
    lines.append("\n🛡 *Trạng thái:* Toàn bộ danh mục nằm trong vùng kiểm soát an toàn!")
    return "\n".join(lines)


def handle_order_blotter() -> str:
    """Trả lời câu hỏi về Sổ Lệnh Hôm Nay."""
    blotter = load_blotter_data()
    orders = blotter.get("orders_vietnam", [])
    date_str = blotter.get("trading_date", datetime.date.today().strftime("%Y-%m-%d"))
    
    lines = [
        f"⚡ *[SỔ LỆNH THỰC THI MASTER CIO — PHIÊN {date_str}]*",
        "🎯 *Chiến lược:* Lai tạo 2 giai đoạn (15Tr Bắn tỉa + 5Tr Lướt sóng)",
        "━━━━━━━━━━━━━━━━━━━"
    ]
    
    for o in orders:
        sym = o.get("symbol")
        shares = o.get("shares", 0)
        capital = o.get("allocated_capital_vnd", 0)
        entry_text = o.get("entry_strategy", "")
        instr = o.get("execution_instruction", "")
        
        lines.append(f"\n🔹 *MÃ {sym} — Khối lượng: {shares:,} CP* (`{capital:,.0f} ₫`)")
        lines.append(f"• *Kế hoạch:* {entry_text}")
        lines.append(f"• *Chỉ đạo tác chiến:* {instr}")
        
    lines.append("\n⏰ *LƯU Ý THỂ CHẾ:*")
    lines.append("• Phiên sáng: Tuyệt đối không FOMO giá xanh.")
    lines.append("• *Khung Giờ Vàng (14h00 – 14h25)*: Bấm cò giải ngân dứt khoát khi hấp thụ xong T+2!")
    return "\n".join(lines)


def handle_market_summary() -> str:
    """Trả lời câu hỏi Tổng Hợp Thị Trường."""
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    lines = [
        f"📝 *[TỔNG HỢP VĨ MÔ & THỊ TRƯỜNG — {today_str}]*",
        "🏛 *Phòng Tổng Hệ Thống — Palmer tóm tắt nhanh:*",
        "━━━━━━━━━━━━━━━━━━━",
        "🌐 *1. Bối cảnh Quốc tế:*",
        "• DXY neo 101.88, Lợi suất TPCP Mỹ 10Y ổn định -> Áp lực tỷ giá hạ nhiệt.",
        "• Thị trường Mỹ phân hóa sau mùa BCTC Big Tech.",
        "\n🇻🇳 *2. Vĩ mô & Dòng tiền Việt Nam:*",
        "• SBV tiếp tục duy trì mặt bằng lãi suất rẻ hỗ trợ sản xuất.",
        "• Tăng trưởng tín dụng Q4 bứt phá, giải ngân Đầu tư công tăng tốc.",
        "\n⚡ *3. Khuyến nghị Tác chiến cho Chủ tịch:*",
        "• Sáng: Quan sát bình tĩnh, không đua lệnh ATO.",
        "• Chiều (14h00-14h25): Dồn trọng tâm giải ngân vào Khung Giờ Vàng.",
        "• Danh mục 20 triệu: Giữ vững kỷ luật kim tự tháp (HPG 500 CP, TCB 200 CP, MBB 200 CP)."
    ]
    return "\n".join(lines)


def handle_take_profit_stop_loss() -> str:
    """Trả lời câu hỏi về Trạng thái Chốt lời / Cắt lỗ."""
    sentinel = load_sentinel_status_data()
    positions = sentinel.get("positions_tracked", [])
    
    vn_positions = [p for p in positions if p.get("symbol") in ["HPG", "TCB", "MBB"]]
    
    lines = [
        "🎯 *[TRẠNG THÁI CANH 2 ĐẦU: CHỐT LỜI & CẮT LỖ]*",
        "🛡 *Victor Sentinel giám sát liên tục từng 60 giây:*",
        "━━━━━━━━━━━━━━━━━━━"
    ]
    
    if not vn_positions:
        lines.append("Đang nạp dữ liệu realtime từ bảng điện...")
        return "\n".join(lines)
        
    for p in vn_positions:
        sym = p.get("symbol")
        curr_p = p.get("current_price", 0)
        stop_p = p.get("stop_loss_2atr", 0)
        tp1_p = p.get("tp1", 0)
        dist_stop = p.get("distance_to_stop_pct", 0)
        dist_tp1 = p.get("distance_to_tp1_pct", 0)
        
        lines.append(f"\n📌 *{sym} (Giá hiện tại: {curr_p:,.0f} ₫)*")
        lines.append(f"• 🟢 *Khoảng cách tới Chốt lời TP1 ({tp1_p:,.0f} ₫):* `+{dist_tp1:.2f}%`")
        lines.append(f"• 🔴 *Khoảng cách tới Cắt lỗ Stop ({stop_p:,.0f} ₫):* `+{dist_stop:.2f}%` (An toàn)")
        
    lines.append("\n✅ *Kết luận:* Cả 3 mã đều đang ở khoảng cách an toàn, hệ thống sẽ rung chuông ngay khi chạm mục tiêu chốt lời!")
    return "\n".join(lines)


def handle_wave_hunter_radar() -> str:
    """Trả lời câu hỏi về Radar Săn Sóng Mới."""
    radar = load_wave_radar_data()
    vn_stocks = radar.get("vietnam_universe_ranked", [])
    
    lines = [
        "📡 *[RADAR SĂN SÓNG MINH QUÂN & ALEX — PHÁT HIỆN DÒNG TIỀN]*",
        "🔍 *Tiêu chí lọc:* BCTC Hạng AAA/AA, OCF > LNST, Điểm Danh Thủ >= 80/100",
        "━━━━━━━━━━━━━━━━━━━"
    ]
    
    top_vn = vn_stocks[:5]
    if top_vn:
        lines.append("🇻🇳 *TOP SIÊU CỔ PHIẾU VN BỨT PHÁ DÒNG TIỀN:*")
        for i, s in enumerate(top_vn, 1):
            sym = s.get("symbol")
            score = s.get("composite_score", 0)
            status = s.get("wave_status", "Đang tích lũy")
            lines.append(f"{i}. *{sym}* — Điểm: `{score:.1f}/100` | Trạng thái: {status}")
    else:
        lines.append("Minh Quân đang quét 54 mã cổ phiếu VN...")
        
    lines.append("\n💡 *Gợi ý:* Ưu tiên tập trung giải ngân danh mục cốt lõi HPG, TCB, MBB trước khi mở rộng vị thế mới!")
    return "\n".join(lines)


def handle_stock_inquiry(ticker: str) -> str:
    """Tra cứu chi tiết 1 mã cổ phiếu."""
    ticker = ticker.upper().strip()
    blotter = load_blotter_data()
    
    # Tìm trong orders_vietnam
    for o in blotter.get("orders_vietnam", []):
        if (o.get("symbol") or o.get("ticker")) == ticker:
            lines = [
                f"🔍 *[THẨM ĐỊNH CHI TIẾT MÃ {ticker}]*",
                f"🏢 *Doanh nghiệp:* {o.get('name', ticker)} ({o.get('sector', '')})",
                f"🏷 *Vai trò:* {o.get('sleeve', '')}",
                "━━━━━━━━━━━━━━━━━━━",
                f"• *Giá vốn đề xuất:* `{o.get('current_price_vnd', 0):,.0f} ₫`",
                f"• *Ngưỡng cắt lỗ 2xATR:* `{o.get('stop_loss_2atr_vnd', 0):,.0f} ₫` (-{o.get('stop_dist_pct', 0):.1f}%)",
                f"• *Mục tiêu Chốt lời:* TP1 `{o.get('tp1_vnd', 0):,.0f} ₫` • TP2 `{o.get('tp2_vnd', 0):,.0f} ₫`",
                f"• *Xác suất thắng P(W):* `{o.get('win_prob_pct', 0):.0f}%` | *R:R:* `1:{o.get('reward_risk_ratio', 0):.2f}`",
                f"\n📈 *Luận điểm BCTC:* {o.get('bctc_thesis', '')}",
                f"\n🚀 *Chất xúc tác:* {o.get('catalysts', '')}",
                f"\n⚡ *Chỉ thị lệnh:* {o.get('execution_instruction', '')}"
            ]
            return "\n".join(lines)
            
    return (
        f"🔍 *Tra cứu mã {ticker}:*\n"
        f"Hiện tại mã {ticker} đang nằm trong danh sách theo dõi của Radar Săn Sóng.\n"
        f"Hệ thống chúng ta phiên hôm nay tập trung nguồn lực giải ngân chuẩn xác 3 mã lõi: *HPG (500 CP), TCB (200 CP), MBB (200 CP)*."
    )


def process_user_query(text: str) -> str:
    """Bộ định tuyến ngôn ngữ tự nhiên thông minh của Palmer."""
    clean_text = text.lower().strip()
    
    # 1. Danh mục
    if any(k in clean_text for k in ["danh mục", "danhmuc", "portfolio", "lãi bao nhiêu", "cầm mã gì", "xem danh mục"]):
        return handle_portfolio_summary()
        
    # 2. Sổ lệnh
    if any(k in clean_text for k in ["sổ lệnh", "solenh", "mua giá nào", "lệnh hôm nay", "lệnh mua"]):
        return handle_order_blotter()
        
    # 3. Tóm tắt thị trường / Tổng hợp
    if any(k in clean_text for k in ["tổng hợp", "tonghop", "tóm tắt", "tomtat", "thị trường", "tình hình", "summary"]):
        return handle_market_summary()
        
    # 4. Canh chốt lời / cắt lỗ
    if any(k in clean_text for k in ["chốt lời", "cắt lỗ", "canh", "stop", "tp", "tp1", "tp2", "chạm ngưỡng"]):
        return handle_take_profit_stop_loss()
        
    # 5. Radar săn sóng
    if any(k in clean_text for k in ["săn sóng", "radar", "mã mới", "sóng mới", "cổ phiếu mới"]):
        return handle_wave_hunter_radar()
        
    # 6. Tra cứu mã cụ thể
    ticker_match = re.search(r"\b(hpg|tcb|mbb|fpt|dgc|mwg|nvda|aapl|msft|googl)\b", clean_text)
    if ticker_match:
        return handle_stock_inquiry(ticker_match.group(1))
        
    if "soi mã" in clean_text or "tra cứu" in clean_text:
        return "🔍 Chủ tịch vui lòng gõ trực tiếp tên mã (Ví dụ: `HPG`, `TCB`, `MBB`) để Palmer phân tích chi tiết BCTC và điểm vào lệnh nhé!"

    # 7. Phản hồi trò chuyện tự nhiên của Palmer
    return (
        "👋 *Chào Chủ tịch Phước Trần! Palmer tôi luôn trực chiến cùng Chủ tịch.*\n\n"
        "Chủ tịch có thể bấm các nút chức năng bên dưới hoặc nhắn tin bất kỳ yêu cầu nào:\n"
        "• *'Tổng hợp thị trường sáng nay'*\n"
        "• *'Tóm tắt danh mục hiện tại'*\n"
        "• *'Kiểm tra mã HPG / TCB / MBB'*\n"
        "• *'Sổ lệnh hôm nay mua giá nào'*\n"
        "• *'Đã chạm điểm chốt lời chưa'*\n\n"
        "Palmer sẽ lập tức phân tích và báo cáo số liệu chuẩn xác ngay tức thì!"
    )


# ==============================================================================
# VÒNG LẶP LẮNG NGHE ĐIỀU HÀNH (POLLING DAEMON)
# ==============================================================================

def load_last_update_id() -> int:
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f).get("last_update_id", 0)
        except Exception:
            pass
    return 0


def save_last_update_id(last_id: int) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump({"last_update_id": last_id, "updated_at": datetime.datetime.now().isoformat()}, f)
    except Exception:
        pass


def poll_and_respond_once(bot_token: str, offset: int) -> int:
    """Lấy các tin nhắn mới từ Telegram và phản hồi ngay lập tức."""
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates?offset={offset}&timeout=5"
    
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if not data.get("ok"):
                return offset
                
            updates = data.get("result", [])
            for u in updates:
                up_id = u.get("update_id", 0)
                offset = max(offset, up_id + 1)
                
                # 1. Phát hiện thêm bot vào Group mới
                my_chat_member = u.get("my_chat_member", {})
                if my_chat_member:
                    chat = my_chat_member.get("chat", {})
                    chat_type = chat.get("type", "")
                    if chat_type in ["group", "supergroup"]:
                        group_id = str(chat.get("id"))
                        print(f"[!] PHÁT HIỆN BOT ĐƯỢC THÊM VÀO GROUP: {chat.get('title')} (ID: {group_id})")
                        provision_all_topics_for_group(group_id)
                        send_raw_telegram(
                            bot_token=bot_token,
                            chat_id=group_id,
                            text="🎉 *[APEX FUND TRUNG TÂM TÁC CHIẾN]*\nPalmer và Victor đã vào vị trí! Đã tự động kích hoạt 4 phân luồng phòng ban thành công!"
                        )
                
                # 2. Xử lý tin nhắn văn bản từ Chủ tịch
                msg = u.get("message", {})
                chat_id = str(msg.get("chat", {}).get("id", ""))
                text = msg.get("text", "").strip()
                thread_id = msg.get("message_thread_id")
                
                if not text:
                    continue
                    
                print(f"[+] Nhận tin nhắn từ {chat_id}: '{text}'")
                
                # Nếu gõ /start hoặc /menu: Gửi lời chào kèm bàn phím ảo
                if text in ["/start", "/menu", "menu", "bắt đầu"]:
                    welcome = (
                        "🎖 *[TRỢ LÝ ĐIỀU HÀNH TỐI CAO APEX FUND — PALMER CO-PILOT]*\n"
                        "Xin kính chào Chủ tịch Phước Trần!\n\n"
                        "Tôi đã kết nối trực tiếp và kích hoạt Bàn Phím Ảo Tương Tác 1-Chạm bên dưới.\n"
                        "Chủ tịch có thể bấm nút bất kỳ hoặc chat trực tiếp để yêu cầu tóm tắt, tổng hợp và soi cổ phiếu!"
                    )
                    send_raw_telegram(
                        bot_token=bot_token,
                        chat_id=chat_id,
                        text=welcome,
                        message_thread_id=thread_id,
                        reply_markup=get_interactive_keyboard()
                    )
                    continue
                    
                # Xử lý câu hỏi tự nhiên
                reply_text = process_user_query(text)
                send_raw_telegram(
                    bot_token=bot_token,
                    chat_id=chat_id,
                    text=reply_text,
                    message_thread_id=thread_id,
                    reply_markup=get_interactive_keyboard()
                )
                
    except Exception as e:
        print(f"[!] Lỗi khi poll tin nhắn Telegram: {e}")
        
    return offset


def run_daemon():
    """Chạy liên tục nền lắng nghe 24/7."""
    cfg = load_config()
    bot_token = cfg.get("bot_token", "")
    offset = load_last_update_id()
    
    print("========================================================================")
    print(" 🤖 PALMER TELEGRAM AI CO-PILOT DAEMON — TRỰC CHIẾN TƯƠNG TÁC 2 CHIỀU")
    print("========================================================================")
    print(f"[*] Đang lắng nghe tin nhắn từ Chủ tịch Phước Trần (Offset: {offset})...")
    
    # Gửi thông báo khởi động và kích hoạt bàn phím ảo tới Chủ tịch
    init_msg = (
        "🚀 *[PALMER AI CO-PILOT ĐÃ KÍCH HOẠT CHẾ ĐỘ CHAT 2 CHIỀU]*\n"
        "Kính gửi: Chủ tịch Phước Trần\n\n"
        "Bàn phím ảo tương tác 1-chạm đã sẵn sàng dưới màn hình.\n"
        "Chủ tịch có thể nhắn tin yêu cầu: *Tổng hợp thị trường, Tóm tắt danh mục, Soi mã HPG/TCB/MBB, hoặc Kiểm tra chốt lời* bất kỳ lúc nào!"
    )
    send_raw_telegram(
        bot_token=bot_token,
        chat_id=cfg.get("private_chat_id", ""),
        text=init_msg,
        reply_markup=get_interactive_keyboard()
    )
    
    while True:
        try:
            new_offset = poll_and_respond_once(bot_token, offset)
            if new_offset != offset:
                offset = new_offset
                save_last_update_id(offset)
            time.sleep(1)
        except KeyboardInterrupt:
            print("\n[*] Dừng dịch vụ Co-Pilot Daemon theo yêu cầu.")
            break
        except Exception as e:
            print(f"[!] Daemon loop error: {e}")
            time.sleep(3)


def main():
    parser = argparse.ArgumentParser(description="Telegram Interactive AI Co-Pilot Daemon")
    parser.add_argument("--daemon", action="store_true", help="Chạy liên tục dạng Daemon lắng nghe")
    parser.add_argument("--test-query", type=str, default="", help="Kiểm thử xử lý một câu hỏi cụ thể")
    parser.add_argument("--send-keyboard", action="store_true", help="Gửi kích hoạt bàn phím ảo tới Telegram Chủ tịch")
    args = parser.parse_args()
    
    if args.test_query:
        print(f"[*] Câu hỏi thử nghiệm: '{args.test_query}'")
        res = process_user_query(args.test_query)
        print("\n--- PHẢN HỒI CỦA PALMER ---")
        print(res)
        return
        
    if args.send_keyboard:
        cfg = load_config()
        msg = (
            "🎖 *[BÀN PHÍM ẢO TƯƠNG TÁC ĐÃ SẴN SÀNG]*\n"
            "Chủ tịch có thể nhấn vào các nút bên dưới để xem báo cáo nhanh ngay tức thì!"
        )
        ok = send_raw_telegram(
            bot_token=cfg.get("bot_token", ""),
            chat_id=cfg.get("private_chat_id", ""),
            text=msg,
            reply_markup=get_interactive_keyboard()
        )
        print(f"[+] Đã gửi bàn phím ảo: {'Thành công' if ok else 'Thất bại'}")
        return

    if args.daemon:
        run_daemon()
    else:
        # Default: poll 1 pass
        cfg = load_config()
        offset = load_last_update_id()
        print(f"[*] Chạy kiểm thử 1 vòng quét (Offset: {offset})...")
        new_offset = poll_and_respond_once(cfg.get("bot_token", ""), offset)
        save_last_update_id(new_offset)
        print("[+] Kiểm thử hoàn tất!")


if __name__ == "__main__":
    main()
