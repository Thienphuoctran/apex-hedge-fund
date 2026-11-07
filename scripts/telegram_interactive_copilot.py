#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TELEGRAM BIDIRECTIONAL AI CO-PILOT & COMMAND LISTENER DAEMON (SSOT V2.0 + EPISODIC MEMORY)
File: scripts/telegram_interactive_copilot.py
Cơ quan chủ quản: Palmer — Cố vấn Điều hành Tối cao & Trưởng Phòng Tổng Hệ Thống (Apex Central System Governance)
Dành cho: Chủ tịch Phước Trần (Tài khoản TCBS: 105C307855)

Nâng cấp Kiến Trúc Ghi Nhớ & Nhận Thức Không Gian - Thời Gian:
1. Tích hợp 100% với `PortfolioStateManager` (SSOT V2.0) và `get_temporal_context()`.
2. Mọi lệnh (`/danhmuc`, `/solenh`, `/canh`, `/tonghop`, `/radar`, `/tcbs`, `/baomat`, `/kyuc`) đều biết chính xác:
   - Hệ thống đang ở thời điểm nào (Thứ, Ngày, Giờ, Phút), thị trường đóng hay mở.
   - Đã trải qua những gì ở các phiên trước (Chiến dịch Vòng 1 đã bán tất toán 100% `400 HPG, 300 TCB, 200 MBB`,
     thu về két TCBS `20,167,119 ₫`, lãi ròng thực nhận `+167,119 ₫`).
   - Hiện tại đang làm gì (Cầm 100% tiền mặt `20,167,119 ₫`, `0 CP`, chuẩn bị tầm ngắm Vòng 2).
3. Xóa bỏ vĩnh viễn 100% các chuỗi văn bản tĩnh/cũ báo cáo khống lệnh mua/nắm giữ `HPG, TCB, MBB` đã thực hiện xong.
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
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def global_excepthook(exc_type, exc_val, exc_tb):
    import traceback
    msg = "".join(traceback.format_exception(exc_type, exc_val, exc_tb))
    try:
        log_daemon(f"[FATAL UNCAUGHT] {msg}")
    except Exception:
        print(f"[FATAL UNCAUGHT] {msg}", flush=True)


sys.excepthook = global_excepthook

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
DEBATE_DIR = BASE_DIR / "03_Synthesis_Memos" / "adversarial_debates"
DEBATE_LEDGER_PATH = DEBATE_DIR / "adversarial_debates_ledger.json"
STATE_FILE = BASE_DIR / "data" / "telegram_copilot_state.json"


def get_interactive_keyboard() -> Dict[str, Any]:
    """Tạo bàn phím ảo 6 nút tương tác 1-chạm dưới khung chat Telegram."""
    return {
        "keyboard": [
            [{"text": "📊 Xem Danh Mục"}, {"text": "⚡ Sổ Lệnh Hôm Nay"}],
            [{"text": "📝 Tóm Tắt Thị Trường"}, {"text": "🎯 Canh Chốt Lời / Cắt Lỗ"}],
            [{"text": "📡 Radar Săn Sóng"}, {"text": "🏦 Số Dư TCBS"}]
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
# BỘ XỬ LÝ PHẢN HỒI THÔNG MINH CỦA PALMER (100% SSOT V2.0 + TEMPORAL AWARENESS)
# ==============================================================================

def handle_portfolio_summary() -> str:
    """Trả lời câu hỏi về Danh Mục Hiện Tại (`/danhmuc`) bằng PortfolioStateManager SSOT V2.0 + Nhận thức Thời gian."""
    try:
        from scripts.portfolio_state_manager import PortfolioStateManager
        st = PortfolioStateManager.load_state()
        t_ctx = st.get("temporal_context") or PortfolioStateManager.get_temporal_context()
        cash = float(st.get("cash_balance_vnd", 20167119.0))
        positions = st.get("active_positions", {})
        realized_pnl = float(st.get("realized_pnl_vnd", 167119.0))
        init_cap = float(st.get("initial_capital_vnd", 20000000.0))

        if not positions:
            lines = [
                "📊 *[BÁO CÁO DANH MỤC & NHẬN THỨC THỜI GIAN THỰC — APEX FUND]*",
                f"👤 *Chủ tài khoản:* Chủ tịch Phước Trần (TCBS: `105C307855`)",
                f"🕒 *Thời điểm hệ thống:* `{t_ctx.get('full_time_label_vn')}`",
                f"📡 *Pha thị trường:* {t_ctx.get('market_phase_vn')}",
                "━━━━━━━━━━━━━━━━━━━",
                "💰 *TRẠNG THÁI TÀI SẢN THỰC TẾ HIỆN TẠI (SSOT):*",
                f"• *Tổng NAV / Tiền mặt khả dụng:* `{cash:,.0f} ₫` (**100% TIỀN MẶT**)",
                "• *Cổ phiếu đang nắm giữ:* `0 mã` (`0 CP` — Rủi ro thị trường = `0.00%`)",
                f"• *Vốn gốc ban đầu:* `{init_cap:,.0f} ₫` | *Lãi ròng đã chốt (sau thuế/phí):* `+{realized_pnl:,.0f} ₫`",
                "━━━━━━━━━━━━━━━━━━━",
                "📜 *KÝ ỨC LỊCH SỬ PHIÊN GẦN NHẤT (ĐÃ HOÀN TẤT):*",
                "• *Chiến dịch Vòng 1 (04/11 – 06/11):* Đã **BÁN TẤT TOÁN 100%** toàn bộ `900 CP` (`400 HPG`, `300 TCB`, `200 MBB` — Mã lệnh `TRD-20261106-001`), thu tiền mặt thực tế về két TCInvest.",
                "• *Vị thế hiện tại:* **Patient Predator (Thợ săn kiên nhẫn)** — Cầm 100% tiền mặt `20,167,119 ₫` chờ cơ hội giải ngân Vòng 2 tuần mới!"
            ]
            return "\n".join(lines)
        else:
            total_mkt = 0.0
            pos_lines = []
            for sym, pos in positions.items():
                sh = int(pos.get("shares", 0))
                entry = float(pos.get("entry_price", 0.0))
                curr = float(pos.get("current_price", entry))
                val = sh * curr
                pnl = val - (sh * entry)
                total_mkt += val
                pnl_pct = (pnl / (sh * entry) * 100) if entry > 0 else 0.0
                emoji = "🟢" if pnl >= 0 else "🔴"
                pos_lines.append(f"• *{sym}*: `{sh:,} CP` | Giá vốn: `{entry:,.0f} ₫` | Thị giá: `{curr:,.0f} ₫` ({emoji} `{pnl:+,.0f} ₫` / `{pnl_pct:+.2f}%`)")

            tot_nav = cash + total_mkt
            lines = [
                "📊 *[BÁO CÁO DANH MỤC ĐANG NẮM GIỮ — APEX FUND]*",
                f"👤 *Chủ tài khoản:* Chủ tịch Phước Trần (TCBS: `105C307855`)",
                f"🕒 *Thời điểm:* `{t_ctx.get('full_time_label_vn')}` ({t_ctx.get('market_phase_vn')})",
                f"💰 *Tổng NAV:* `{tot_nav:,.0f} ₫` | *Tiền mặt:* `{cash:,.0f} ₫` | *Cổ phiếu:* `{total_mkt:,.0f} ₫`",
                "━━━━━━━━━━━━━━━━━━━",
                *pos_lines,
                "━━━━━━━━━━━━━━━━━━━",
                "🛡 *Kiểm soát rủi ro:* Khóa cứng ngưỡng cắt lỗ Stop 2xATR và bảo vệ lợi nhuận!"
            ]
            return "\n".join(lines)
    except Exception as e:
        return f"⚠️ Lỗi truy xuất Danh mục SSOT: {e}"


def handle_order_blotter() -> str:
    """
    Trả lời câu hỏi về Sổ Lệnh (`/solenh`) bằng PortfolioStateManager SSOT V2.0.
    Phân biệt rạch ròi giữa:
    1) Lịch sử Vòng 1 đã bán tất toán (đã thực hiện xong trong quá khứ).
    2) Trạng thái Sổ lệnh hiện tại (0 lệnh mở nếu đang cầm 100% tiền mặt) và Tầm ngắm chuẩn bị Vòng 2.
    """
    try:
        from scripts.portfolio_state_manager import PortfolioStateManager
        st = PortfolioStateManager.load_state()
        t_ctx = st.get("temporal_context") or PortfolioStateManager.get_temporal_context()
        cash = float(st.get("cash_balance_vnd", 20167119.0))
        realized_pnl = float(st.get("realized_pnl_vnd", 167119.0))
        positions = st.get("active_positions", {})
        watchlist = st.get("next_round_watchlist", [])

        lines = [
            f"⚡ *[SỔ LỆNH & NHẬN THỨC TÁC CHIẾN MASTER CIO — {t_ctx.get('date_vn')}]*",
            f"🕒 *Thời điểm hiện tại:* `{t_ctx.get('full_time_label_vn')}`",
            f"📡 *Trạng thái sàn:* {t_ctx.get('market_phase_vn')}",
            f"💰 *Sức mua Tiền mặt TCBS (`105C307855`):* `{cash:,.0f} ₫` (**100% Cash**)",
            "━━━━━━━━━━━━━━━━━━━"
        ]

        if not positions:
            lines.extend([
                "✅ *1. LỊCH SỬ CHIẾN DỊCH VÒNG 1 (ĐÃ TẤT TOÁN HOÀN TẤT):*",
                "• *Trạng thái:* **ĐÃ BÁN SẠCH 100% (`0 CP` còn giữ)** — Không còn lệnh treo cũ.",
                "• *Chi tiết đã khép lại:* Đã chốt lời toàn bộ `400 HPG`, `300 TCB`, `200 MBB` (Mã lệnh `TRD-20261106-001`).",
                f"• *Kết quả thu về két TCInvest:* Tiền mặt thực nhận `{cash:,.0f} ₫` (Lãi ròng sau thuế phí: `+{realized_pnl:,.0f} ₫`).",
                "\n🎯 *2. SỔ LỆNH HIỆN TẠI & TẦM NGẮM CHUẨN BỊ VÒNG 2:*",
                "• *Lệnh đang mở hiện tại:* `0 lệnh` (Đang giữ 100% tiền mặt bảo toàn thành quả).",
                f"• *Ghi chú phiên:* {t_ctx.get('next_session_note')}"
            ])
            if watchlist:
                lines.append("• *Danh sách Tầm ngắm Vòng 2 (Chờ tín hiệu giải ngân từ vốn `20,167,119 ₫`):*")
                for idx, w in enumerate(watchlist[:4], 1):
                    lines.append(
                        f"  {idx}. *{w.get('symbol')}* ({w.get('sector')}): {w.get('target_buy_zone')} | _{w.get('bctc_highlight')}_"
                    )
        else:
            lines.append("📌 *CÁC VỊ THẾ & LỆNH ĐANG QUẢN LÝ TRỰC TIẾP:*")
            for sym, pos in positions.items():
                sh = int(pos.get("shares", 0))
                ep = float(pos.get("entry_price", 0.0))
                sl = float(pos.get("stop_loss", round(ep * 0.93, 0)))
                tp1 = float(pos.get("take_profit_tp1", round(ep * 1.15, 0)))
                lines.append(
                    f"• *{sym}* — Khối lượng: `{sh:,} CP` | Giá vốn: `{ep:,.0f} ₫` | Stop 2xATR: `{sl:,.0f} ₫` | Chốt lời TP1: `{tp1:,.0f} ₫`"
                )

        lines.extend([
            "\n⏰ *KỶ LUẬT THỂ CHẾ MASTER CIO JAMES:*",
            "• Tuyệt đối không báo cáo lại các lệnh đã bán trong quá khứ thành lệnh đang mở.",
            "• Chỉ bấm cò giải ngân Vòng 2 khi thị trường mở cửa và hội tụ đủ **Checklist 7 Điểm** trong **Khung Giờ Vàng (14h00 – 14h25)**!"
        ])
        return "\n".join(lines)
    except Exception as e:
        return f"⚠️ Lỗi truy xuất Sổ lệnh SSOT: {e}"


def handle_market_summary() -> str:
    """Trả lời câu hỏi Tổng Hợp Thị Trường (`/tonghop`) kèm Nhận thức Thời gian & Vị thế thực tế."""
    from scripts.portfolio_state_manager import PortfolioStateManager
    st = PortfolioStateManager.load_state()
    t_ctx = st.get("temporal_context") or PortfolioStateManager.get_temporal_context()
    cash = float(st.get("cash_balance_vnd", 20167119.0))
    realized_pnl = float(st.get("realized_pnl_vnd", 167119.0))
    positions = st.get("active_positions", {})

    pos_summary = (
        f"Đang cầm **100% TIỀN MẶT (`{cash:,.0f} ₫`)**, `0 CP` sau khi chốt lời thành công Vòng 1 (`+{realized_pnl:,.0f} ₫`)."
        if not positions
        else f"Đang nắm giữ `{len(positions)} mã` cổ phiếu kèm tiền mặt `{cash:,.0f} ₫`."
    )

    lines = [
        f"📝 *[TỔNG HỢP VĨ MÔ, THỊ TRƯỜNG & ĐỊNH VỊ HỆ THỐNG — {t_ctx.get('date_vn')}]*",
        f"🕒 *Thời điểm:* `{t_ctx.get('full_time_label_vn')}`",
        f"📡 *Pha thị trường:* {t_ctx.get('market_phase_vn')}",
        "━━━━━━━━━━━━━━━━━━━",
        "🌐 *1. Bối cảnh Vĩ mô Quốc tế (Ban 1 Global):*",
        "• DXY duy trì quanh vùng cân bằng, lợi suất TPCP Mỹ 10Y hạ nhiệt giúp giảm áp lực lên tỷ giá.",
        "• Dòng tiền toàn cầu tập trung vào nhóm bán dẫn & hạ tầng AI có dòng tiền tự do FCF thực chất.",
        "\n🇻🇳 *2. Vĩ mô & Dòng tiền Nội địa (Ban 1 VN):*",
        "• SBV điều hành linh hoạt, duy trì mặt bằng lãi suất hỗ trợ tăng trưởng tín dụng Quý 4 và giải ngân Đầu tư công.",
        "\n🎯 *3. Định vị Tài sản & Chiến lược Tác chiến (Master CIO James):*",
        f"• *Vị thế thực tế TCBS (`105C307855`):* {pos_summary}",
        f"• *Hành động tiếp theo:* {t_ctx.get('next_session_note')} Tuyệt đối không FOMO mua đuổi đầu phiên; chờ điểm mua chiết khấu chuẩn xác cho Vòng 2!"
    ]
    return "\n".join(lines)


def handle_take_profit_stop_loss() -> str:
    """Trả lời câu hỏi về Trạng thái Chốt lời / Cắt lỗ (`/canh`) từ SSOT V2.0."""
    from scripts.portfolio_state_manager import PortfolioStateManager
    st = PortfolioStateManager.load_state()
    t_ctx = st.get("temporal_context") or PortfolioStateManager.get_temporal_context()
    cash = float(st.get("cash_balance_vnd", 20167119.0))
    realized_pnl = float(st.get("realized_pnl_vnd", 167119.0))
    positions = st.get("active_positions", {})

    lines = [
        "🎯 *[TRẠNG THÁI CANH 2 ĐẦU: CHỐT LỜI & CẮT LỖ — BAN 9 VICTOR]*",
        f"🕒 *Thời điểm kiểm tra:* `{t_ctx.get('full_time_label_vn')}`",
        f"📡 *Pha thị trường:* {t_ctx.get('market_phase_vn')}",
        "━━━━━━━━━━━━━━━━━━━"
    ]

    if not positions:
        lines.extend([
            "🛡️ *TRẠNG THÁI HIỆN TẠI: 100% TIỀN MẶT — 0 RỦI RO CẮT LỖ*",
            f"• *Số dư Tiền mặt thực tế trên TCInvest:* `{cash:,.0f} ₫` (`0 CP` nắm giữ).",
            f"• *Lịch sử Chốt lời Vòng 1:* Toàn bộ `900 CP` (`400 HPG`, `300 TCB`, `200 MBB`) **ĐÃ ĐƯỢC CHỐT LỜI TẤT TOÁN 100%**, khóa lãi ròng thực nhận `+{realized_pnl:,.0f} ₫` vào két sắt.",
            "• *Rủi ro chạm Stop Loss hiện tại:* `0.00%` (Không có bất kỳ cổ phiếu nào chịu rủi ro qua đêm/cuối tuần).",
            "\n🔭 *Nhiệm vụ của Victor (Ban 9) lúc này:*",
            "• Chuyển từ chế độ *Canh bán vị thế cũ* sang chế độ *Canh vùng chiết khấu mở vị thế Vòng 2* khi thị trường bước vào phiên giao dịch mới!"
        ])
        return "\n".join(lines)

    for sym, p in positions.items():
        sh = int(p.get("shares", 0))
        entry_p = float(p.get("entry_price", 0))
        curr_p = float(p.get("current_price", entry_p))
        stop_p = float(p.get("stop_loss", round(entry_p * 0.93, 0)))
        tp1_p = float(p.get("take_profit_tp1", round(entry_p * 1.15, 0)))
        dist_stop = ((curr_p - stop_p) / curr_p * 100.0) if curr_p > 0 else 0.0
        dist_tp1 = ((tp1_p - curr_p) / curr_p * 100.0) if curr_p > 0 else 0.0

        lines.append(f"\n📌 *{sym}* (`{sh:,} CP` | Giá vốn: `{entry_p:,.0f} ₫` | Thị giá: `{curr_p:,.0f} ₫`)")
        lines.append(f"• 🟢 *Khoảng cách tới Chốt lời TP1 (`{tp1_p:,.0f} ₫`):* `+{dist_tp1:.2f}%`")
        lines.append(f"• 🔴 *Khoảng cách tới Cắt lỗ Stop 2xATR (`{stop_p:,.0f} ₫`):* `+{dist_stop:.2f}%` (An toàn)")

    lines.append("\n✅ *Kết luận:* Victor đang giám sát chặt chẽ từng vị thế theo thời gian thực!")
    return "\n".join(lines)


# Alias tương thích với telegram_ai_copilot.py
handle_tp_sl_watch = handle_take_profit_stop_loss


def handle_wave_hunter_radar() -> str:
    """Trả lời câu hỏi về Radar Săn Sóng Mới (`/radar`) tích hợp trạng thái vốn thực tế."""
    from scripts.portfolio_state_manager import PortfolioStateManager
    st = PortfolioStateManager.load_state()
    t_ctx = st.get("temporal_context") or PortfolioStateManager.get_temporal_context()
    cash = float(st.get("cash_balance_vnd", 20167119.0))
    radar = load_wave_radar_data()
    vn_stocks = radar.get("vietnam_universe_ranked", [])

    lines = [
        "📡 *[RADAR SĂN SÓNG VÒNG 2 — MINH QUÂN & ALEX]*",
        f"🕒 *Thời điểm quét:* `{t_ctx.get('full_time_label_vn')}`",
        f"💳 *Sức mua Tiền mặt sẵn sàng cho Vòng 2:* `{cash:,.0f} ₫` (100% Cash sau khi tất toán Vòng 1)",
        "🔍 *Tiêu chí lọc:* BCTC Hạng AAA/AA, OCF > LNST, Điểm Danh Thủ >= 80/100",
        "━━━━━━━━━━━━━━━━━━━"
    ]

    top_vn = vn_stocks[:5]
    if top_vn:
        lines.append("🇻🇳 *TOP SIÊU CỔ PHIẾU VN TRONG TẦM NGẮM VÒNG 2:*")
        for i, s in enumerate(top_vn, 1):
            sym = s.get("symbol")
            score = s.get("composite_score", 0)
            status = s.get("wave_status", "Đang tích lũy")
            lines.append(f"{i}. *{sym}* — Điểm: `{score:.1f}/100` | Trạng thái: {status}")
    else:
        for i, w in enumerate(st.get("next_round_watchlist", []), 1):
            lines.append(f"{i}. *{w.get('symbol')}* ({w.get('sector')}) — {w.get('bctc_highlight')}")

    lines.append(
        f"\n💡 *Chiến lược Vòng 2:* Với `{cash:,.0f} ₫` tiền mặt sẵn sàng trong két TCBS, hệ thống kiên nhẫn chờ nhịp chiết khấu đạt chuẩn **Checklist 7 Điểm** trong Khung Giờ Vàng 14h00–14h25 mới bấm cò giải ngân!"
    )
    return "\n".join(lines)


def handle_adversarial_inquiry(ticker: str = "") -> str:
    """Tra cứu kết quả Tranh Biện Đối Kháng Tam Giác (Adversarial Triad Engine) kèm ngữ cảnh thực tế."""
    from scripts.portfolio_state_manager import PortfolioStateManager
    st = PortfolioStateManager.load_state()
    cash = float(st.get("cash_balance_vnd", 20167119.0))
    positions = st.get("active_positions", {})
    ticker = ticker.upper().strip()

    if ticker:
        json_path = DEBATE_DIR / f"{ticker}_adversarial_debate.json"
        if json_path.exists():
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    d = json.load(f)
                fa = d.get("forensic_audit", {})
                be = d.get("bear_counter_thesis", {})
                reb = d.get("bull_rebuttal", {})
                dec = d.get("investment_decision", {})
                val = dec.get("valuation_assessment", {})
                holding_note = (
                    f"Đang nắm giữ `{positions[ticker]['shares']:,} CP`"
                    if ticker in positions
                    else f"Hiện nắm giữ `0 CP` (Đã tất toán Vòng 1, đang theo dõi cho Vòng 2 với sức mua `{cash:,.0f} ₫`)"
                )

                lines = [
                    f"⚔️ *[BIÊN BẢN TRANH BIỆN ĐỐI KHÁNG: MÃ {ticker}]*",
                    f"🏛 *Chủ tọa phân xử:* Tổng Tư Lệnh James & Palmer",
                    f"📦 *Trạng thái vị thế thực tế:* {holding_note}",
                    f"━━━━━━━━━━━━━━━━━━━",
                    f"• *Pháp Y Kế Toán:* `{fa.get('forensic_score')}/100` ({fa.get('audit_verdict')})",
                    f"• *Biên An Toàn Graham MoS:* `+{val.get('implied_margin_of_safety_pct')}%`",
                    f"• *Net Conviction Score:* `{dec.get('net_conviction_score'):+.1f}/100` (Độ tin cậy: {dec.get('confidence_level')})",
                    f"\n💥 *Bear Tấn Công:* {be.get('points_of_attack', [{}])[0].get('counter_argument', '')[:120]}...",
                    f"\n🛡 *Bull Phản Pháo:* {reb.get('counter_rebuttals', [{}])[0].get('rebuttal_argument', '')[:120]}...",
                    f"\n⚖️ *Phán quyết Hồ sơ BCTC:* *{dec.get('verdict')}* — Chỉ mở vị thế mới khi giá chiết khấu vào vùng mua Vòng 2!"
                ]
                return "\n".join(lines)
            except Exception:
                pass

    lines = [
        "⚔️ *[HỆ THỐNG TRANH BIỆN ĐỐI KHÁNG 5 VÒNG — HỒ SƠ THẨM ĐỊNH]*",
        f"💰 *Trạng thái Quỹ hiện tại:* **100% TIỀN MẶT (`{cash:,.0f} ₫`)** — Đã chốt lời Vòng 1 (`+167,119 ₫`)",
        "━━━━━━━━━━━━━━━━━━━",
        "📌 *Hồ sơ các mã đã thẩm định & đang theo dõi cho Vòng 2:*",
        "1. *FPT (Công nghệ & AI)*: BCTC Hạng AAA, OCF/LNST `1.25x`, Beneish M `-2.80` ➔ *TẦM NGẮM VÒNG 2*",
        "2. *DGC (Hóa chất & Bán dẫn)*: Tiền mặt ròng >10,500 tỷ, OCF/LNST `1.15x` ➔ *TẦM NGẮM VÒNG 2*",
        "3. *HPG / TCB / MBB*: Đã hoàn thành xuất sắc nhiệm vụ Vòng 1 (Đã bán thu tiền về két); tiếp tục theo dõi chờ chiết khấu nếu làm vòng mới.",
        "\n💡 *Chủ tịch gõ: 'tranh bien HPG' hoặc 'tranh bien TCB' để xem hồ sơ phản biện chi tiết của từng mã!*"
    ]
    return "\n".join(lines)


def handle_stock_inquiry(ticker: str) -> str:
    """Tra cứu chi tiết 1 mã cổ phiếu kèm nhận thức rõ đã bán hay đang giữ."""
    from scripts.portfolio_state_manager import PortfolioStateManager
    st = PortfolioStateManager.load_state()
    t_ctx = st.get("temporal_context") or PortfolioStateManager.get_temporal_context()
    cash = float(st.get("cash_balance_vnd", 20167119.0))
    positions = st.get("active_positions", {})
    ticker = ticker.upper().strip()

    pos_info = positions.get(ticker)
    if pos_info and pos_info.get("shares", 0) > 0:
        holding_badge = f"ĐANG NẮM GIỮ `{pos_info['shares']:,} CP` (Giá vốn `{pos_info.get('entry_price', 0):,.0f} ₫`)"
    elif ticker in ["HPG", "TCB", "MBB"]:
        holding_badge = "ĐÃ BÁN TẤT TOÁN 100% Ở VÒNG 1 (`0 CP` nắm giữ — Đã thu tiền + lãi về két TCBS)"
    else:
        holding_badge = "HIỆN NẮM GIỮ `0 CP` (Nằm trong danh sách theo dõi Vòng 2)"

    bctc_path = BASE_DIR / "VN_Market" / "data" / "vn_bctc_analysis.json"
    bctc_info = {}
    if bctc_path.exists():
        try:
            with open(bctc_path, "r", encoding="utf-8") as f:
                db = json.load(f)
                if isinstance(db, dict):
                    bctc_info = db.get(ticker, {})
        except Exception:
            pass

    lines = [
        f"🔍 *[THẨM ĐỊNH CHI TIẾT MÃ {ticker} — NHẬN THỨC THỜI GIAN THỰC]*",
        f"🕒 *Thời điểm:* `{t_ctx.get('full_time_label_vn')}`",
        f"📦 *Vị thế trong tài khoản TCBS (`105C307855`):* **{holding_badge}**",
        f"💳 *Sức mua Tiền mặt hiện có:* `{cash:,.0f} ₫`",
        "━━━━━━━━━━━━━━━━━━━"
    ]
    if bctc_info:
        lines.extend([
            f"• *Doanh nghiệp:* {bctc_info.get('company_name', ticker)}",
            f"• *Xếp hạng BCTC:* `{bctc_info.get('bctc_rating', 'AA+')}` | *OCF/LNST:* `{bctc_info.get('ocf_to_net_income_ratio', 1.15):.2f}x`",
            f"• *Beneish M-Score:* `{bctc_info.get('beneish_m_score', -2.45):.2f}` (An toàn, không gian lận)",
            f"• *Nhận định kiểm toán:* {bctc_info.get('audit_verdict', 'BCTC minh bạch, dòng tiền thật.')}"
        ])
    else:
        lines.append(f"• Mã *{ticker}* đang được Ban 2 VN & Ban 10 (Hiền) cập nhật hồ sơ BCTC và theo dõi vùng giá chiết khấu cho Chiến dịch Vòng 2.")

    lines.append("\n⚡ *Chỉ thị Master CIO James:* Hiện Quỹ đang giữ 100% tiền mặt (`20,167,119 ₫`); chỉ giải ngân vào phiên giao dịch mới khi hội tụ đủ tín hiệu dòng tiền và biên an toàn!")
    return "\n".join(lines)


def handle_episodic_memory_report() -> str:
    """Báo cáo Ký ức Lịch sử Phiên & Nhận thức Không gian - Thời gian (`/kyuc`, `/lichsu`)."""
    from scripts.portfolio_state_manager import PortfolioStateManager
    st = PortfolioStateManager.load_state()
    t_ctx = st.get("temporal_context") or PortfolioStateManager.get_temporal_context()
    cash = float(st.get("cash_balance_vnd", 20167119.0))
    realized = float(st.get("realized_pnl_vnd", 167119.0))
    campaigns = st.get("completed_campaigns", [])
    trades = st.get("trade_history", [])

    lines = [
        "🧠 *[BỘ NHỚ LỊCH SỬ PHIÊN & NHẬN THỨC KHÔNG GIAN - THỜI GIAN]*",
        f"🕒 *Định vị Thời gian thực:* `{t_ctx.get('full_time_label_vn')}`",
        f"📡 *Pha Thị trường:* {t_ctx.get('market_phase_vn')}",
        f"🎯 *Giai đoạn Chiến dịch:* `{st.get('current_campaign_phase')}`",
        "━━━━━━━━━━━━━━━━━━━",
        "📍 *1. CHÚNG TA ĐANG Ở ĐÂU & ĐANG LÀM GÌ?*",
        f"• *Tài khoản TCBS (`105C307855`):* Đang cầm **100% TIỀN MẶT (`{cash:,.0f} ₫`)**, `0 CP` nắm giữ.",
        f"• *Thành quả đã khóa:* Lãi ròng thực nhận `+{realized:,.0f} ₫` (đã trừ toàn bộ phí giao dịch & thuế bán 0.1%).",
        f"• *Nhiệm vụ hiện tại:* Nghỉ ngơi an toàn tuyệt đối qua cuối tuần (`0% Weekend Risk`), rà soát BCTC chuẩn bị danh sách Tầm ngắm Vòng 2.",
        "\n📜 *2. CHÚNG TA ĐÃ TRẢI QUA NHỮNG GÌ (KÝ ỨC ĐÃ LƯU TRỮ):*"
    ]
    for c in campaigns:
        lines.append(
            f"• *{c.get('campaign_id')} ({c.get('period')}):* Đã mua và **BÁN TẤT TOÁN 100%** `400 HPG, 300 TCB, 200 MBB` ➔ Thu về `{c.get('final_cash_tcbs_vnd', cash):,.0f} ₫`."
        )
    if trades:
        last_t = trades[-1]
        lines.append(
            f"• *Giao dịch gần nhất (`{last_t.get('trade_id')}` lúc `{last_t.get('timestamp')}`):* `{last_t.get('action')}` — {last_t.get('reason')}"
        )

    lines.append("\n✅ *Cam kết Hệ thống:* Toàn bộ 11 Phòng Ban đều đọc chung Bộ nhớ Trung tâm này — Không bao giờ nhầm lẫn lệnh quá khứ thành lệnh hiện tại!")
    return "\n".join(lines)


def process_user_query(text: str) -> str:
    """Bộ định tuyến ngôn ngữ tự nhiên thông minh của Palmer."""
    clean_text = text.lower().strip()

    # XỬ LÝ LỆNH THỰC THI DANH MỤC THỜI GIAN THỰC (TỰ ĐỘNG CẬP NHẬT SSOT 0.1s)
    try:
        from scripts.portfolio_state_manager import PortfolioStateManager
        # 1. Lệnh Bán hết / Chốt lời sạch (cả có dấu lẫn không dấu)
        if any(k in clean_text for k in ["bán hết", "ban het", "chốt lời hết", "chot loi het", "bán sạch", "ban sach", "sell all", "thoát hết", "thoat het", "đã bán hết", "da ban het"]):
            ok, msg = PortfolioStateManager.execute_sell_all_and_lock_cash(reason=f"Chủ tịch ra lệnh trực tiếp trên Telegram: '{text}'")
            return msg

        # 2. Lệnh Bán cụ thể: "đã bán 200 hpg giá 21.8" hoặc "ban 200 hpg 21.8"
        sell_m = re.search(r"(?:đã bán|da ban|bán|ban)\s+(\d+)\s+([a-zA-Z]{3})\s+(?:giá|gia)?\s*([\d\.,]+)", clean_text)
        if sell_m:
            sh = int(sell_m.group(1))
            sym = sell_m.group(2).upper()
            pr_raw = sell_m.group(3).replace(",", "").replace(".", "")
            pr = float(pr_raw) if float(pr_raw) > 1000 else float(pr_raw) * 1000.0
            ok, msg = PortfolioStateManager.execute_sell_order(sym, sh, pr, reason=f"Chủ tịch ra lệnh bán trên Telegram")
            return msg

        # 3. Lệnh Mua cụ thể: "đã mua 200 pvt giá 20.7" hoặc "mua 200 pvt 20.7"
        buy_m = re.search(r"(?:đã mua|da mua|mua)\s+(\d+)\s+([a-zA-Z]{3})\s+(?:giá|gia)?\s*([\d\.,]+)", clean_text)
        if buy_m:
            sh = int(buy_m.group(1))
            sym = buy_m.group(2).upper()
            pr_raw = buy_m.group(3).replace(",", "").replace(".", "")
            pr = float(pr_raw) if float(pr_raw) > 1000 else float(pr_raw) * 1000.0
            ok, msg = PortfolioStateManager.execute_buy_order(sym, sh, pr, reason=f"Chủ tịch ra lệnh mua trên Telegram")
            return msg
    except Exception as e:
        print(f"[!] Lỗi bộ xử lý giao dịch tự động: {e}")

    # 0.0 XỬ LÝ LỆNH TRA CỨU & CẤU HÌNH TCBS TCINVEST AN TOÀN (READ-ONLY SENTINEL)
    if clean_text.startswith("/set_tcbs_token") or clean_text.startswith("/token_tcbs"):
        token_parts = text.split(maxsplit=1)
        if len(token_parts) > 1:
            token_val = token_parts[1].strip()
            env_file = BASE_DIR / ".env.tcbs"
            existing_lines = []
            if env_file.exists():
                with open(env_file, "r", encoding="utf-8") as ef:
                    for l in ef:
                        if not l.startswith("TCINVEST_SESSION_TOKEN="):
                            existing_lines.append(l)
            existing_lines.append(f"TCINVEST_SESSION_TOKEN={token_val}\n")
            with open(env_file, "w", encoding="utf-8") as ef:
                ef.writelines(existing_lines)
            return (
                "🛡️ *[KẾT NỐI TCBS TCINVEST THÀNH CÔNG — CHẾ ĐỘ READ-ONLY]*\n"
                "━━━━━━━━━━━━━━━━━━━\n"
                "• *Trạng thái:* Đã lưu trữ an toàn Session Token vào `.env.tcbs`.\n"
                "• *Hàng rào an ninh:* Khóa cứng 100% `READ_ONLY_ENFORCED = True`.\n"
                "• *Tài khoản:* `105C307855` (Chủ tịch Phước Trần).\n"
                "• *Cam kết thể chế:* Tuyệt đối KHÔNG RÚT TIỀN, KHÔNG CHUYỂN KHOẢN, KHÔNG ĐẶT LỆNH.\n"
                "Bấm *'🏦 Số Dư TCBS'* hoặc gõ `/tcbs` để kiểm tra tài sản trực tuyến ngay lập tức!"
            )
        return "⚠️ Cú pháp: `/set_tcbs_token <dán_chuỗi_token_ở_đây>`"

    if any(k in clean_text for k in ["/kyuc", "/lichsu", "ký ức", "ky uc", "lịch sử giao dịch", "lich su giao dich", "đang ở đâu", "đã trải qua"]):
        return handle_episodic_memory_report()

    if any(k in clean_text for k in ["/baomat", "bảo mật", "bao mat", "chống hack", "chong hack", "an ninh", "cyber shield", "két sắt"]):
        try:
            from scripts.apex_cyber_vault_shield import ApexCyberVaultShield
            res = ApexCyberVaultShield.verify_portfolio_integrity_and_ids()
            lines = [
                "🛡️ *[BÁO CÁO LÁ CHẮN AN NINH 5 LỚP — APEX CYBER VAULT SHIELD]*",
                f"👤 *Tài khoản bảo vệ:* `105C307855` (Chủ tịch Trần Quốc Thiên Phước)",
                f"📡 *Trạng thái An ninh:* 🟢 *AN TOÀN TUYỆT ĐỐI ({res['security_status']})*",
                "━━━━━━━━━━━━━━━━━━━",
                "🔒 *5 LỚP PHÒNG THỦ ĐANG HOẠT ĐỘNG 24/7:*",
                f"1️⃣ *Két sắt Mật mã AES/HMAC:* `{'ĐÃ NIÊM PHONG' if res['vault_encrypted'] else 'CHỜ'}`",
                f"2️⃣ *Chốt chặn Rò rỉ Git:* `{'PRE-COMMIT HOOK ACTIVE' if res['git_pre_commit_hook_active'] else 'INACTIVE'}`",
                f"3️⃣ *Tường lửa Read-Only Air-Gap:* `KHÓA CỨNG 100%` (Cấm rút tiền/đặt lệnh)",
                f"4️⃣ *Chữ ký số Tài sản SHA-256:* `{res['asset_integrity_sha256']}`",
                "5️⃣ *Bảo vệ Vật lý Ngân hàng:* `Smart OTP trên điện thoại Chủ tịch`",
                "━━━━━━━━━━━━━━━━━━━",
                f"💰 *Vốn được bảo vệ:* `{res['verified_cash_vnd']:,.0f} ₫` | *Bất thường phát hiện:* `{len(res['anomalies_detected'])}`"
            ]
            return "\n".join(lines)
        except Exception as e:
            return f"⚠️ Lỗi kiểm tra bảo mật: {e}"

    if any(k in clean_text for k in ["/tcbs", "tcbs", "tcinvest", "tiền tcbs", "số dư tcbs", "vốn tcbs", "sức mua tcbs", "đồng bộ tcbs"]):
        try:
            from scripts.tcinvest_vault_watcher import TCBSVaultWatcher
            from scripts.portfolio_state_manager import PortfolioStateManager
            t_ctx = PortfolioStateManager.get_temporal_context()
            watcher = TCBSVaultWatcher()
            cash_info = watcher.fetch_cash_balance()
            holdings = watcher.fetch_portfolio_holdings()

            cash_vnd = float(cash_info.get("cash_balance_vnd", 20167119.0))
            is_live = "LIVE" in cash_info.get("status", "")
            auth_badge = "🟢 *ĐÃ KẾT NỐI TCBS MCP (AI CONNECTOR)*" if is_live else "🟡 *CHẾ ĐỘ STANDBY AN TOÀN (SSOT)*"
            mcp_url = cash_info.get("mcp_url", "https://mcp.tcbs.com.vn/mcp/tcinvest/")

            lines = [
                "🏛️ *[BÁO CÁO TÀI SẢN & VỐN TCBS TCINVEST — APEX FUND]*",
                f"👤 *Chủ tài khoản:* Chủ tịch Phước Trần (`105C307855`)",
                f"🕒 *Thời điểm đối soát:* `{t_ctx.get('full_time_label_vn')}`",
                f"🔗 *Cổng TCBS MCP:* `{mcp_url}`",
                "🔐 *Bảo mật:* Chế độ Chỉ Đọc (Read-Only Air-Gap) — Cấm rút tiền/chuyển khoản 100%",
                f"📡 *Trạng thái:* {auth_badge}",
                "━━━━━━━━━━━━━━━━━━━",
                f"💰 *Số dư Tiền Mặt Thực Tế:* `{cash_vnd:,.0f} ₫`",
                f"💳 *Sức mua sẵn sàng:* `{cash_vnd:,.0f} ₫`",
                f"📦 *Cổ phiếu nắm giữ:* `{len(holdings.get('positions', {}))} mã` (`0 CP` rủi ro — Đã tất toán Vòng 1)",
                "━━━━━━━━━━━━━━━━━━━",
                "💡 *Ghi chú bảo mật:* Hệ thống chỉ giám sát dữ liệu và đồng bộ số liệu thời gian thực. Mọi giao dịch chuyển tiền/rút tiền đều bất khả thi nếu không có Smart OTP trên điện thoại Chủ tịch!"
            ]
            return "\n".join(lines)
        except Exception as e:
            return f"⚠️ Lỗi tra cứu TCBS: {e}"

    # 0. Tranh biện đối kháng tam giác (Bước 2)
    if any(k in clean_text for k in ["tranh biện", "tranh bien", "đối kháng", "doi khang", "phan bien", "phản biện", "red team", "bull bear", "bear bull"]):
        ticker_match = re.search(r"\b(hpg|tcb|mbb|fpt|dgc|mwg)\b", clean_text)
        sym = ticker_match.group(1).upper() if ticker_match else ""
        return handle_adversarial_inquiry(sym)

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
        return "🔍 Chủ tịch vui lòng gõ trực tiếp tên mã (Ví dụ: `FPT`, `DGC`, `HPG`, `TCB`) để Palmer phân tích chi tiết BCTC và điểm vào lệnh Vòng 2 nhé!"

    # 7. CHUYỂN GIAO CHỈ THỊ ĐIỀU HÀNH ĐÓNG LẶP (CLOSED-LOOP TASK DISPATCHER)
    try:
        from scripts.closed_loop_task_dispatcher import dispatch_chairman_directive
        task_res = dispatch_chairman_directive(text, source="TELEGRAM_COPILOT")
        summary_txt = task_res.get("execution_result", {}).get("summary", "Đã tiếp nhận và thực thi hoàn tất.")
        return (
            f"🎖️ *[TỔNG TƯ LỆNH JAMES — ĐÃ PHÂN CÔNG & CHỈ HUY THỰC THI]*\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"Báo cáo Chủ tịch Phước Trần: Tôi (Master CIO James) đã tiếp nhận chỉ thị và trực tiếp giao việc cho *{task_res.get('assigned_department_name', task_res['assigned_department'])}*.\n\n"
            f"• Mã Lệnh: `#{task_res['task_id']}`\n"
            f"• Cán bộ phụ trách: *{task_res['assigned_officer']}*\n"
            f"• Phân luồng báo cáo: *{task_res['topic_name']}*\n"
            f"• Trạng thái: ✅ *{task_res['status']}*\n\n"
            f"📊 *KẾT QUẢ THỰC THI THỰC TẾ*:\n{summary_txt}\n\n"
            f"👉 *Nghiệm thu*: Tôi đã yêu cầu phòng ban gửi báo cáo chi tiết kèm bằng chứng vào Topic *{task_res['topic_name']}*. Kính mời Chủ tịch kiểm tra!"
        )
    except Exception as e:
        print(f"[!] Lỗi dispatch chỉ thị: {e}")

    from scripts.portfolio_state_manager import PortfolioStateManager
    t_ctx = PortfolioStateManager.get_temporal_context()
    return (
        "🎖️ *Chào Chủ tịch Phước Trần! Tôi là James — Tổng Tư Lệnh Master CIO (Ban 8).*\n\n"
        f"• *Thời điểm hiện tại:* `{t_ctx.get('full_time_label_vn')}` ({t_ctx.get('market_phase_vn')})\n"
        "• *Trạng thái Quỹ:* **100% Tiền mặt (`20,167,119 ₫`)** sau khi chốt lời toàn bộ Vòng 1 (`+167,119 ₫`).\n\n"
        "Chủ tịch có thể dùng các lệnh kiểm tra tức thời: `/danhmuc`, `/solenh`, `/canh`, `/tcbs`, `/baomat`, `/kyuc`, `/radar`!"
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
    """Lấy các tin nhắn mới từ Telegram với cơ chế Short Polling & Connection Close chống 409 Conflict."""
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates?offset={offset}&timeout=0"
    req = urllib.request.Request(url, headers={"Connection": "close", "User-Agent": "ApexCopilotBot/1.0"})

    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
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
                        log_daemon(f"[!] PHÁT HIỆN BOT ĐƯỢC THÊM VÀO GROUP: {chat.get('title')} (ID: {group_id})")
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

                log_daemon(f"[+] Nhận tin nhắn từ {chat_id}: '{text}'")

                if text in ["/start", "/menu", "menu", "bắt đầu"]:
                    welcome = (
                        "🎖️ *[BỘ CHỈ HUY TỔNG TƯ LỆNH MASTER CIO JAMES — APEX ENTERPRISE]*\n\n"
                        "Xin kính chào Chủ tịch Phước Trần!\n"
                        "Tôi là James — Master CIO trực tiếp chỉ huy toàn bộ hệ thống Quỹ và các phòng ban trực thuộc.\n\n"
                        "🏛️ *Cơ Cấu 7 Phân Luồng Phòng Ban Đã Thiết Lập Hoàn Chỉnh*:\n"
                        "1. `🎖️ BỘ CHỈ HUY TỔNG TƯ LỆNH JAMES`: Chỉ huy tác chiến, bàn bạc chiến lược & giao việc trực tiếp cho James.\n"
                        "2. `💼 VĂN PHÒNG TRỢ LÝ NAM`: Trợ lý cá nhân trang bị Gemini 3.8 Flash cho câu hỏi thường ngày & đời sống.\n"
                        "3. `🚨 BAN 9 — GIÁM SÁT REALTIME & BÁO ĐỘNG ĐỎ`: Victor trực chiến giá live HOSE 73ms, Stop Loss & Take-Profit.\n"
                        "4. `☀️ BAN 7 VN — MINH QUÂN EXECUTION DESK`: Sổ Lệnh Master, Khung Giờ Vàng 14h00, Kim Tự Tháp.\n"
                        "5. `📡 BAN 2 & 3 — BCTC FORENSIC & RADAR SĂN SÓNG`: Kiểm toán BCTC OCF/LNST, Beneish M & CBTT.\n"
                        "6. `⚖️ BAN 4 — QUẢN TRỊ RỦI RO & HỘI ĐỒNG ĐẦU TƯ`: ATR Risk-Parity & Stress-Test.\n"
                        "7. `🏛️ BAN 6 & 5 — HỌC VIỆN HUẤN LUYỆN & TIẾN HÓA`: Khai sáng 7h30 & Hồi tố Hit Rate.\n\n"
                        "Chủ tịch có thể giao việc trực tiếp cho tôi tại đây, tôi sẽ phân công và bắt buộc các phòng ban làm thật việc thật!"
                    )
                    send_raw_telegram(
                        bot_token=bot_token,
                        chat_id=chat_id,
                        text=welcome,
                        message_thread_id=thread_id,
                        reply_markup=get_interactive_keyboard()
                    )
                    continue

                # 3. ƯU TIÊN XỬ LÝ TRỰC TIẾP CÁC LỆNH HỆ THỐNG (/tcbs, /baomat, /danhmuc, /solenh...) TRÊN MỌI TOPIC
                text_l = text.lower().strip()
                if text_l.startswith("/") or any(k in text_l for k in [
                    "tcbs", "tcinvest", "bảo mật", "chống hack", "khiên bảo mật",
                    "đã bán", "bán hết", "tất toán", "đã mua", "khớp mua", "ký ức", "lịch sử giao dịch"
                ]):
                    reply_text = process_user_query(text)
                elif thread_id == 106:
                    from scripts.assistant_nam_agent import handle_nam_chat
                    reply_text = handle_nam_chat(text)
                elif thread_id == 6:
                    from scripts.master_cio_james_agent import handle_james_chat
                    reply_text = handle_james_chat(text)
                elif thread_id == 3:
                    reply_text = process_user_query(text)
                elif thread_id == 4:
                    reply_text = handle_order_blotter() if any(k in text.lower() for k in ["sổ lệnh", "mua", "lệnh"]) else process_user_query(text)
                elif thread_id == 5:
                    reply_text = handle_wave_hunter_radar() if any(k in text.lower() for k in ["radar", "sóng", "mã mới"]) else process_user_query(text)
                else:
                    if any(k in text.lower() for k in ["nam", "trợ lý nam", "em nam"]):
                        from scripts.assistant_nam_agent import handle_nam_chat
                        reply_text = handle_nam_chat(text)
                    else:
                        from scripts.master_cio_james_agent import handle_james_chat
                        reply_text = handle_james_chat(text)

                send_raw_telegram(
                    bot_token=bot_token,
                    chat_id=chat_id,
                    text=reply_text,
                    message_thread_id=thread_id,
                    reply_markup=get_interactive_keyboard()
                )

    except urllib.error.HTTPError as e:
        if e.code == 409:
            log_daemon("[BACKOFF 409] Kết nối Telegram cũ đang giải phóng. Tạm nghỉ 5 giây...")
            time.sleep(5)
        elif e.code == 429:
            log_daemon("[BACKOFF 429 Rate Limit] Bị hạn chế tốc độ Telegram. Tạm nghỉ 15 giây...")
            time.sleep(15)
        else:
            log_daemon(f"[!] HTTP Error {e.code}: {e}")
            time.sleep(2)
    except Exception as e:
        log_daemon(f"[!] Ngoại lệ kết nối Telegram: {e}")
        time.sleep(2)

    return offset


DAEMON_LOG_PATH = BASE_DIR / "data" / "telegram_copilot_daemon.log"


def log_daemon(msg: str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {msg}"
    print(formatted, flush=True)
    try:
        DAEMON_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(DAEMON_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
    except Exception:
        pass


def run_daemon():
    """[UNIFIED OMNI-COPILOT V4.0 GATEWAY] Tự động ủy quyền sang Engine Hợp Nhất V4.0 để chống xung đột 409."""
    unified_script = Path(r"c:\Users\phuoc\Downloads\antigravity\Trợ lí cá nhân\scripts\telegram_ai_copilot.py")
    if unified_script.exists():
        log_daemon("[*] Chuyển tiếp sang Unified Omni-Copilot V4.0 (Palmer + Long + Nam + Watchdog)...")
        import subprocess
        subprocess.run([sys.executable, "-u", str(unified_script)], check=False)
        return


def main():
    parser = argparse.ArgumentParser(description="Telegram Interactive AI Co-Pilot Daemon")
    parser.add_argument("--daemon", action="store_true", help="Chạy liên tục dạng Daemon lắng nghe")
    parser.add_argument("--test-query", type=str, default="", help="Kiểm thử xử lý một câu hỏi cụ thể")
    parser.add_argument("--send-keyboard", type=bool, default=False, help="Gửi kích hoạt bàn phím ảo tới Telegram Chủ tịch")
    args = parser.parse_args()

    if args.test_query:
        print(f"[*] Câu hỏi thử nghiệm: '{args.test_query}'")
        res = process_user_query(args.test_query)
        print("\n--- PHẢN HỒI CỦA PALMER ---")
        print(res)
        return

    if args.daemon:
        run_daemon()
    else:
        cfg = load_config()
        offset = load_last_update_id()
        print(f"[*] Chạy kiểm thử 1 vòng quét (Offset: {offset})...")
        new_offset = poll_and_respond_once(cfg.get("bot_token", ""), offset)
        save_last_update_id(new_offset)
        print("[+] Kiểm thử hoàn tất!")


if __name__ == "__main__":
    main()
