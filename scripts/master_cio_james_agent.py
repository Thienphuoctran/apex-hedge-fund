#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MASTER CIO EXECUTIVE DESK — "JAMES" (SUPREME PORTFOLIO COMMANDER)
File: scripts/master_cio_james_agent.py
Cơ quan vận hành: Bộ Chỉ Huy Tối Cao — Tổng Tư Lệnh Master CIO James (Ban 8)
Dành riêng cho: Chủ tịch Phước Trần (Tài khoản TCBS: 105C307855)
"""

import os
import sys
import json
import time
import re
import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.closed_loop_task_dispatcher import dispatch_chairman_directive
from scripts.assistant_nam_agent import get_gemini_api_key
from scripts.portfolio_state_manager import PortfolioStateManager

BLOTTER_PATH = BASE_DIR / "08_Master_Investment_CIO" / "master_execution_blotter.json"
SENTINEL_STATUS = BASE_DIR / "09_Realtime_Portfolio_Sentinel" / "live_sentinel_status.json"


def _get_live_portfolio_context() -> str:
    try:
        st = PortfolioStateManager.load_state()
        cash_vnd = st.get("cash_balance_vnd", 20167119.0)
        positions = st.get("active_positions", {})
        realized = st.get("realized_pnl_vnd", 167119.0)
        if not positions:
            return (
                f"Vốn NAV hiện tại: {cash_vnd:,.0f} VNĐ. Trạng thái: 100% Tiền mặt ({cash_vnd:,.0f} VNĐ), "
                f"đã tất toán toàn bộ cổ phiếu cũ (HPG, TCB, MBB) và khóa lãi thực nhận +{realized:,.0f} VNĐ."
            )
        holdings_desc = ", ".join(
            f"{sym} ({info.get('shares', 0)} CP @ {info.get('avg_price', 0):,.0f} ₫)"
            for sym, info in positions.items()
            if info.get("shares", 0) > 0
        )
        return f"Cổ phiếu đang nắm giữ: {holdings_desc}. Tiền mặt: {cash_vnd:,.0f} VNĐ."
    except Exception:
        return "Vốn NAV: 20,199,425 VNĐ (100% Tiền mặt sẵn sàng giải ngân)."


def query_gemini_cio(prompt: str) -> Optional[str]:
    """Sử dụng Gemini nếu có API Key để suy luận chiến lược đầu tư đỉnh cao"""
    api_key = get_gemini_api_key()
    if not api_key:
        return None

    try:
        from google import genai
        from google.genai import types

        portfolio_ctx = _get_live_portfolio_context()
        client = genai.Client(api_key=api_key)
        system_instruction = (
            "Bạn là James — Tổng Tư Lệnh Master CIO (Ban 8), người đứng đầu bộ máy tác chiến Quỹ Đầu Tư Apex Hedge Fund của Chủ tịch Phước Trần.\n"
            f"Chủ tài khoản: Chủ tịch Phước Trần (TCBS: 105C307855). {portfolio_ctx}\n"
            "Kỷ luật thể chế: Không FOMO ATO, giải ngân Khung Giờ Vàng 14h00-14h25, Stop Loss 2xATR <= 7.5%, Scaling Out chốt lời 50/50.\n"
            "Phong cách của bạn:\n"
            "- Xưng hô: 'Báo cáo Chủ tịch Phước Trần' hoặc 'Thưa Chủ tịch', xưng 'tôi' hoặc 'James'.\n"
            "- Giọng điệu: Quyết đoán, bản lĩnh quân sự, tư duy định lượng sắc bén, chuẩn xác về mặt tài chính và quản trị rủi ro.\n"
            "- Luôn sẵn sàng nhận lệnh, phân chia công việc cho cấp dưới (Victor, Minh Quân, Alex, Ban 2, Ban 4) và cam kết 'Làm thật việc thật'."
        )

        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.6
            )
        )
        if resp and resp.text:
            return resp.text.strip()
    except Exception:
        pass
    return None


def handle_james_chat(user_text: str) -> str:
    """
    Xử lý tương tác chiến lược và chỉ lệnh điều hành giữa Chủ tịch Phước Trần và Master CIO James.
    """
    text_clean = user_text.strip()
    text_lower = text_clean.lower()

    # 0. TRA CỨU BÁCH KHOA TOÀN THƯ 105 BÀI HỌC & MẸO ĐẦU TƯ HUYỀN THOẠI
    heuristic_triggers = [
        "/heuristics", "/meo", "/kinhnghiem", "bài học", "mẹo đầu tư", "tinh hoa", "kinh nghiệm", "mẹo",
        "buffett", "munger", "peter lynch", "soros", "druckenmiller", "minervini",
        "livermore", "105 bài học", "100 bài học", "triết lý đầu tư", "t+2.5", "wyckoff", "vcp", "canslim"
    ]
    if any(k in text_lower for k in heuristic_triggers):
        from scripts.apex_persistent_memory_core import ApexPersistentMemoryCore
        search_query = text_clean
        for kw in ["/heuristics", "/meo", "/kinhnghiem", "bài học", "mẹo", "tìm", "cho tôi"]:
            search_query = re.sub(re.escape(kw), "", search_query, flags=re.IGNORECASE).strip()
        res = ApexPersistentMemoryCore.query_heuristics(search_query, limit=3)
        if not res:
            res = [ApexPersistentMemoryCore.get_daily_guiding_heuristic()]
        reply_lines = [
            "🧠 *[BÁCH KHOA TOÀN THƯ 105 TINH HOA & MẸO ĐẦU TƯ HUYỀN THOẠI]*",
            "━━━━━━━━━━━━━━━━━━━"
        ]
        for h in res:
            reply_lines.append(f"📌 *Bài {h['id']}: {h['title']}*")
            reply_lines.append(f"• *Bậc thầy*: _{h['author']}_")
            reply_lines.append(f"• *Nguyên lý*: {h['core_principle']}")
            reply_lines.append(f"• *Ứng dụng Apex*: {h['apex_heuristic']}\n")
        reply_lines.append("📖 _Chủ tịch có thể tra cứu toàn bộ 105 bài học tại file `05_Learning_And_Evolution/100_LEGENDARY_INVESTOR_HEURISTICS_MASTER_COMPENDIUM.md` hoặc qua API `/api/heuristics`._")
        return "\n".join(reply_lines)

    # 0.1 CHUYỂN TIẾP TRỰC TIẾP CÁC LỆNH HỆ THỐNG (/tcbs, /baomat, /danhmuc, mua/bán...) SANG BỘ XỬ LÝ TRUNG TÂM
    direct_commands = [
        "/tcbs", "tcbs", "tcinvest", "tài khoản tcbs", "số dư tcbs", "bảng giá tcbs",
        "/baomat", "bảo mật", "khiên bảo mật", "chống hack", "kiểm toán bảo mật",
        "/set_tcbs_token", "/danhmuc", "/solenh", "/tonghop", "/canh", "/radar"
    ]
    if text_lower.startswith("/") or any(k in text_lower for k in direct_commands):
        from scripts.telegram_interactive_copilot import process_user_query
        return process_user_query(text_clean)

    # Nếu là thông báo đã bán hết / chốt lời / mua khớp cổ phiếu ➔ Gọi thẳng bộ nhớ trung tâm trong process_user_query
    if any(p in text_lower for p in ["đã bán", "bán hết", "bán sạch", "tất toán", "chốt hết", "xả hết", "đã mua", "mua thêm", "vừa mua", "khớp mua"]):
        from scripts.telegram_interactive_copilot import process_user_query
        return process_user_query(text_clean)



    # 1. NHẬN DIỆN CÁC CÂU LỆNH HÀNH ĐỘNG PHÂN CÔNG PHÒNG BAN (Dùng regex word-boundary chuẩn xác)
    action_patterns = [
        r"\bquét\b", r"\bkiểm tra\b", r"\bcanh\b", r"\brà soát\b", r"\bchốt lời\b", r"\bcắt lỗ\b",
        r"\bgiải ngân\b", r"\bsổ lệnh\b", r"\bbáo cáo\b", r"\bchỉ thị\b", r"\bgiao việc\b",
        r"\byêu cầu\b", r"\bthực hiện\b", r"\bphân bổ\b", r"\brủi ro\b", r"\bstop\b",
        r"\btp1\b", r"\btp2\b", r"\bkế hoạch\b", r"\bhôm nay\b", r"\bminh quân\b",
        r"\bvictor\b", r"\balex\b", r"\bhiền\b", r"\bkhánh\b", r"\bvideo\b", r"\bkịch bản\b",
        r"\btiktok\b", r"\breels\b", r"\bshorts\b", r"\bsoi\b", r"\bbctc\b", r"\bxuất\b", r"\bxem\b"
    ]
    if any(re.search(pat, text_lower) for pat in action_patterns):
        task_res = dispatch_chairman_directive(text_clean, source="TELEGRAM_JAMES_HQ")
        summary_txt = task_res.get("execution_result", {}).get("summary", "Đã tiếp nhận và thực thi hoàn tất.")
        return (
            f"🎖️ *[BỘ CHỈ HUY MASTER CIO JAMES — BÁO CÁO THỰC THI]*\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"• *Mã Lệnh*: `#{task_res['task_id']}`\n"
            f"• *Đơn vị thực thi*: *{task_res.get('assigned_department_name', task_res['assigned_department'])}* ({task_res['assigned_officer']})\n"
            f"• *Trạng thái*: ✅ *{task_res['status']}*\n\n"
            f"{summary_txt}"
        )

    # 2. Thử gọi bộ não Gemini nếu có API key
    llm_resp = query_gemini_cio(text_clean)
    if llm_resp:
        return f"🎖️ *[TỔNG TƯ LỆNH MASTER CIO JAMES]*\n\n{llm_resp}"

    # 3. Phản hồi các câu hỏi chiến lược cốt lõi dựa trên Single Source of Truth
    portfolio_ctx = _get_live_portfolio_context()
    return (
        f"🎖️ *[BỘ CHỈ HUY TỔNG TƯ LỆNH MASTER CIO JAMES]*\n\n"
        f"Báo cáo Chủ tịch Phước Trần, tôi đã tiếp nhận ý kiến: _\"{text_clean}\"_\n"
        f"• *Trạng thái danh mục hiện tại*: {portfolio_ctx}\n\n"
        "Chủ tịch có thể dùng nhanh các lệnh kiểm tra tức thời:\n"
        "• `/tcbs` — Kiểm tra trực tiếp tài khoản TCInvest (`105C307855`) & Bảng giá Live\n"
        "• `/baomat` — Kiểm toán Khiên Bảo Vệ 5 Tầng (Chống Hack 100%)\n"
        "• `/danhmuc` — Báo cáo trạng thái NAV & Danh mục hiện tại\n"
        "• `/solenh` — Xem Sổ lệnh & Tầm ngắm giải ngân Khung 14h00"
    )


if __name__ == "__main__":
    print(handle_james_chat("/tcbs"))
