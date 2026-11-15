#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APEX INSTITUTIONAL CLOUD PORTAL ENGINE (BLOOMBERG-GRADE WEB INTERFACE V4.0)
File: scripts/apex_web_portal_engine.py
Cơ quan chủ quản: Palmer — Apex Central System Governance
Phục vụ: Chủ tịch Trần Quốc Thiên Phước (Tài khoản TCBS: 105C307855)
Tổng Tư Lệnh Điều Hành: Master CIO James

TỔNG NÂNG CẤP GIAO DIỆN TOÀN DIỆN V4.0:
1. Trải nghiệm thị giác công thái học chuẩn Bloomberg Terminal Dark-Mode:
   - Gam màu Obsidian & Slate Navy chống mỏi mắt.
   - Typography chuẩn Plus Jakarta Sans & JetBrains Mono.
2. Phân loại báo cáo đa chiều khoa học:
   - 2 Tầng lọc: Theo Khung Thời Gian (Hôm Nay / Kho Lưu Trữ / 4 Ca) và Theo 5 Khối Chuyên Môn Thể Chế.
   - Hiển thị số lượng báo cáo (N) trực tiếp trên từng nút phân loại.
   - Chuyển đổi 2 chế độ xem: Dạng Thẻ Grid (Trực quan) vs Dạng Bảng Nhanh (Compact Table).
3. Bàn Chỉ Huy Master CIO James 2 Cột (Split-Screen):
   - Cột trái: Luồng chat tương tác 2 chiều thông minh.
   - Cột phải: Live Sticky Sidebar ghim cố định tài khoản TCBS, đồng hồ đếm ngược phiên ATO Thứ Hai, và Radar 4 siêu cổ phiếu Vòng 2.
4. Bộ tiền xử lý thông minh cho tin nhắn James (Smart Visual Formatter):
   - Tự động bóc tách thành 4 Khối KPI Neon (Tiền mặt, Kho hàng, Lãi V1, Chế độ phiên).
   - Tự động render 4 Thẻ Cổ Phiếu Tầm Ngắm (Stock Cards) riêng biệt với vạch màu giá mua rõ nét.
   - Thu gọn Lịch sử Vòng 1 vào thanh Accordion tránh rối mắt.
   - Bật marked breaks: true giữ nguyên ngắt dòng, xóa bỏ triệt để tình trạng dồn chữ (Wall of Text).
5. Trình đọc báo cáo Reader Modal tối ưu đọc tập trung (880px max-width, hỗ trợ In/PDF).
"""

import sys
import json
import html as html_lib
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

def get_ict_now() -> datetime.datetime:
    """Luôn lấy thời gian hiện tại chuẩn múi giờ Việt Nam (ICT = UTC+7) bất kể chạy trên Cloud Render hay Local."""
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    ict_tz = datetime.timezone(datetime.timedelta(hours=7))
    return utc_now.astimezone(ict_tz)

BASE_DIR = Path(__file__).resolve().parent.parent


def _load_live_ssot_summary() -> Dict[str, Any]:
    """Đọc trạng thái tài khoản SSOT V2.0 trực tiếp từ data/current_portfolio_state.json."""
    ssot_file = BASE_DIR / "data" / "current_portfolio_state.json"
    cash_vnd = 0.0
    stocks_val_vnd = 0.0
    total_cost_vnd = 0.0
    total_nav_vnd = 0.0
    realized_pnl_vnd = 167119.0
    unrealized_pnl_vnd = 0.0
    pos_dict: Dict[str, Any] = {}
    if ssot_file.exists():
        try:
            with open(ssot_file, "r", encoding="utf-8") as f:
                st = json.load(f)
            cash_vnd = float(st.get("cash_balance_vnd", 0.0))
            stocks_val_vnd = float(st.get("total_market_val_vnd", 0.0))
            total_cost_vnd = float(st.get("total_cost_vnd", stocks_val_vnd))
            total_nav_vnd = float(st.get("total_nav_vnd", cash_vnd + stocks_val_vnd))
            realized_pnl_vnd = float(st.get("realized_pnl_vnd", 167119.0))
            unrealized_pnl_vnd = float(st.get("unrealized_pnl_vnd", 0.0))
            pos_dict = st.get("active_positions", {})
        except Exception:
            pass
    if total_nav_vnd <= 0:
        total_nav_vnd = cash_vnd + stocks_val_vnd
    total_shares = sum(int(p.get("shares", 0)) for p in pos_dict.values()) if isinstance(pos_dict, dict) else 0
    cash_pct = round((cash_vnd / total_nav_vnd) * 100, 1) if total_nav_vnd > 0 else 100.0
    stocks_pct = round(100.0 - cash_pct, 1)
    unrealized_pct = round((unrealized_pnl_vnd / total_cost_vnd) * 100, 1) if total_cost_vnd > 0 else 0.0
    holdings_desc = " + ".join(f"{p.get('shares', 0)} {s}" for s, p in pos_dict.items()) if pos_dict else "0 CP"
    return {
        "cash_vnd": cash_vnd,
        "cash_str": f"{cash_vnd:,.0f} ₫",
        "stocks_val_vnd": stocks_val_vnd,
        "stocks_str": f"{stocks_val_vnd:,.0f} ₫",
        "total_nav_vnd": total_nav_vnd,
        "nav_str": f"{total_nav_vnd:,.0f} ₫",
        "cash_pct": cash_pct,
        "stocks_pct": stocks_pct,
        "total_shares": total_shares,
        "holdings_count": len(pos_dict) if isinstance(pos_dict, dict) else 0,
        "holdings_desc": holdings_desc,
        "realized_pnl_vnd": realized_pnl_vnd,
        "realized_str": (f"+{realized_pnl_vnd:,.0f} ₫" if realized_pnl_vnd >= 0 else f"{realized_pnl_vnd:,.0f} ₫"),
        "unrealized_pnl_vnd": unrealized_pnl_vnd,
        "unrealized_str": (f"+{unrealized_pnl_vnd:,.0f} ₫" if unrealized_pnl_vnd >= 0 else f"{unrealized_pnl_vnd:,.0f} ₫"),
        "unrealized_pct": unrealized_pct,
    }


def generate_dynamic_tactical_stages_html(
    now=None,
    wr_state: Optional[Dict[str, Any]] = None,
) -> str:
    if now is None:
        now = get_ict_now()
    hm = now.hour * 60 + now.minute

    ssot = _load_live_ssot_summary()
    victor = (wr_state or {}).get("victor_sentinel", {})
    regime = (wr_state or {}).get("intraday_regime", {})
    live_stocks = (wr_state or {}).get("live_stocks", [])

    cash_str = f"{float(victor.get('cash_vnd', ssot['cash_vnd'])):,.0f} ₫" if victor else ssot["cash_str"]
    cash_pct = float(victor.get("cash_pct", ssot["cash_pct"])) if victor else ssot["cash_pct"]
    total_shares = int(victor.get("total_shares", ssot["total_shares"])) if victor else ssot["total_shares"]
    holdings = victor.get("holdings", [])
    holdings_desc = (
        " + ".join(f"{h.get('shares', 0)} {h.get('symbol', '')}" for h in holdings)
        if holdings else ssot["holdings_desc"]
    )
    regime_label = html_lib.escape(str(regime.get("label", "GIẰNG CO PHÂN HÓA")))
    max_alloc = int(regime.get("max_new_allocation_pct", 30))

    if holdings:
        holdings_bullets = "".join(
            f"<div>• <strong>{html_lib.escape(str(h.get('symbol', '')))}</strong> "
            f"({int(h.get('shares', 0))} CP • Vốn {float(h.get('avg_cost', 0)):,.0f} ₫ ➔ Live {float(h.get('current_price', 0)):,.0f} ₫ | "
            f"Stop 2xATR: <code style=\"color:#fbbf24;\">{float(h.get('stop_loss', 0)):,.0f} ₫</code>)</div>"
            for h in holdings
        )
    else:
        holdings_bullets = "<div>• Chưa nắm giữ cổ phiếu (100% Tiền Mặt Sẵn Sàng Bắn Tỉa).</div>"

    standby_candidates = [s for s in live_stocks if not s.get("is_holding")][:2]
    if standby_candidates:
        standby_bullets = ", ".join(
            f"<strong>{html_lib.escape(str(s.get('code', '')))}</strong> (Live {float(s.get('price', 0)):,.0f} đ • BuyUp {float(s.get('active_buy_pct', 50)):.1f}%)"
            for s in standby_candidates
        )
    else:
        standby_bullets = "Rổ Watchlist SSOT"

    # Morning: 08:30 - 11:30
    if hm < 11 * 60 + 30:
        s1_active = (8 * 60 + 30 <= hm < 9 * 60)
        s1_done = (hm >= 9 * 60)
        s2_active = (9 * 60 <= hm < 9 * 60 + 15)
        s2_done = (hm >= 9 * 60 + 15)
        s3_active = (9 * 60 + 15 <= hm < 11 * 60 + 30)

        s1_badge = "ĐANG DIỄN RA" if s1_active else ("ĐÃ HOÀN TẤT" if s1_done else "CHỜ ĐẾN GIỜ")
        s1_cls = "border: 1.5px solid rgba(56, 189, 248, 0.5); background: linear-gradient(135deg, rgba(14, 165, 233, 0.15), rgba(15, 23, 42, 0.88));" if s1_active else "background: rgba(30, 41, 59, 0.5); border: 1px solid rgba(148, 163, 184, 0.2);"
        s1_b_cls = "background: rgba(56, 189, 248, 0.25); color: #38bdf8; border-color: rgba(56, 189, 248, 0.5);" if s1_active else ("background: rgba(16, 185, 129, 0.2); color: #34d399;" if s1_done else "background: rgba(148, 163, 184, 0.15); color: #94a3b8;")

        s2_badge = "ĐANG DIỄN RA" if s2_active else ("ĐÃ HOÀN TẤT" if s2_done else "CHỜ ĐẾN GIỜ")
        s2_cls = "border: 1.5px solid rgba(239, 68, 68, 0.5); background: linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(15, 23, 42, 0.88));" if s2_active else "background: rgba(30, 41, 59, 0.5); border: 1px solid rgba(148, 163, 184, 0.2);"
        s2_b_cls = "background: rgba(239, 68, 68, 0.25); color: #f87171; border-color: rgba(239, 68, 68, 0.5);" if s2_active else ("background: rgba(16, 185, 129, 0.2); color: #34d399;" if s2_done else "background: rgba(148, 163, 184, 0.15); color: #94a3b8;")

        s3_badge = "ĐANG DIỄN RA" if s3_active else "CHỜ ĐẾN GIỜ"
        s3_cls = "border: 1.5px solid rgba(56, 189, 248, 0.5); background: linear-gradient(135deg, rgba(14, 165, 233, 0.15), rgba(15, 23, 42, 0.88));" if s3_active else "background: rgba(30, 41, 59, 0.5); border: 1px solid rgba(148, 163, 184, 0.2);"
        s3_b_cls = "background: rgba(56, 189, 248, 0.25); color: #38bdf8; border-color: rgba(56, 189, 248, 0.5);" if s3_active else "background: rgba(148, 163, 184, 0.15); color: #94a3b8;"

        return f"""
        <div style="display: flex; flex-direction: column; gap: 10px;" id="afternoon-tactical-stages">
            <div id="stage-1-card" class="action-plan-hero-card" style="{s1_cls} border-radius: 9px; padding: 12px; display: flex; flex-direction: column; gap: 6px;">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <span id="stage-1-badge" class="action-plan-tag" style="{s1_b_cls} font-weight: 800;">
                        <span class="war-room-live-dot" style="background:#38bdf8;"></span> {s1_badge}
                    </span>
                    <span style="font-size: 11.5px; font-weight: 800; color: #38bdf8; font-family: monospace;">08:30 – 09:00</span>
                </div>
                <div style="font-size: 13px; font-weight: 800; color: #f8fafc;">
                    1. Giai Đoạn 1 (08:30 – 09:00): Pre-ATO Giao Ban &amp; Rà Soát Sức Mua SSOT
                </div>
                <div style="font-size: 11px; color: #cbd5e1; line-height: 1.55;">
                    • <strong>Nhiệm vụ</strong>: Minh Quân rà soát Sổ Lệnh Master Blotter, đối soát két tiền mặt SSOT <strong>{cash_str}</strong> ({cash_pct:.1f}% NAV) và bảo vệ <strong>{total_shares} CP ({holdings_desc})</strong>.
                </div>
                <div style="background: rgba(239, 68, 68, 0.12); border-left: 3px solid #ef4444; padding: 6px 10px; border-radius: 4px; font-size: 10.5px; color: #fca5a5; line-height: 1.5;">
                    ⚖️ <strong>Kỷ luật Hiến chương</strong>: <strong>TUYỆT ĐỐI KHÔNG ĐẶT LỆNH SỚM TRƯỚC ATO</strong>.
                </div>
            </div>

            <div id="stage-2-card" style="{s2_cls} border-radius: 9px; padding: 12px; display: flex; flex-direction: column; gap: 6px;">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <span id="stage-2-badge" style="{s2_b_cls} font-size: 10px; font-weight: 800; padding: 2px 8px; border-radius: 4px;">{s2_badge}</span>
                    <span style="font-size: 11px; font-weight: 800; color: #f87171; font-family: monospace;">09:00 – 09:15</span>
                </div>
                <div style="font-size: 13px; font-weight: 800; color: #f1f5f9;">
                    2. Giai Đoạn 2 (09:00 – 09:15): Khớp Lệnh ATO — Giữ Kỷ Luật Thép 3 Không
                </div>
                <div style="font-size: 11px; color: #cbd5e1; line-height: 1.55;">
                    • Victor quét độ mở Gap &amp; cảnh giữ Stop Loss 2xATR danh mục thực tế:
                    <div style="margin-left: 8px; margin-top: 4px; display: flex; flex-direction: column; gap: 3px;">
                        {holdings_bullets}
                    </div>
                </div>
                <div style="background: rgba(239, 68, 68, 0.12); border-left: 3px solid #ef4444; padding: 6px 10px; border-radius: 4px; font-size: 10.5px; color: #fca5a5; line-height: 1.5;">
                    🚫 <strong>CẢNH BÁO BẪY ATO</strong>: 100% CẤM MUA ĐUỔI GIÁ XANH ATO.
                </div>
            </div>

            <div id="stage-3-card" style="{s3_cls} border-radius: 9px; padding: 12px; display: flex; flex-direction: column; gap: 6px;">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <span id="stage-3-badge" style="{s3_b_cls} font-size: 10px; font-weight: 800; padding: 2px 8px; border-radius: 4px;">{s3_badge}</span>
                    <span style="font-size: 11px; font-weight: 800; color: #38bdf8; font-family: monospace;">09:15 – 11:30</span>
                </div>
                <div style="font-size: 13px; font-weight: 800; color: #38bdf8;">
                    3. Giai Đoạn 3 (09:15 – 11:30): Khớp Lệnh Sáng — Chế Độ {regime_label}
                </div>
                <div style="font-size: 11px; color: #cbd5e1; line-height: 1.55;">
                    • Theo dõi Mua chủ động (Buy Up %) của {standby_bullets}. Bảo toàn két tiền mặt <strong>{cash_str}</strong> ({cash_pct:.1f}% NAV) chờ Khung Giờ Vàng.
                </div>
            </div>
        </div>
        """

    # Noon: 11:30 - 13:00
    elif hm < 13 * 60:
        return f"""
        <div style="display: flex; flex-direction: column; gap: 10px;" id="afternoon-tactical-stages">
            <div id="stage-1-card" class="action-plan-hero-card" style="border: 1.5px solid rgba(251, 191, 36, 0.5); background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(15, 23, 42, 0.88)); border-radius: 9px; padding: 12px; display: flex; flex-direction: column; gap: 6px;">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <span class="action-plan-tag" style="background: rgba(245, 158, 11, 0.25); color: #fbbf24; font-weight: 800;">☕ NGHỈ TRƯA &amp; ĐỐI SOÁT</span>
                    <span style="font-size: 11.5px; font-weight: 800; color: #fbbf24; font-family: monospace;">11:30 – 13:00</span>
                </div>
                <div style="font-size: 13px; font-weight: 800; color: #f8fafc;">
                    Hội Ý Giữa Phiên ({regime_label}): Đối Soát Khối Ngoại &amp; Hàng T+2
                </div>
                <div style="font-size: 11px; color: #cbd5e1; line-height: 1.55;">
                    • Tổng kết thanh khoản sáng, giữ nguyên két tiền <strong>{cash_str}</strong> ({cash_pct:.1f}% NAV) &amp; bảo vệ <strong>{total_shares} CP ({holdings_desc})</strong>. Hạn mức giải ngân mới: <strong>{max_alloc}% Cash</strong>.
                </div>
            </div>
        </div>
        """

    # Afternoon: 13:00 - 14:45
    elif hm < 14 * 60 + 45:
        s1_active = (13 * 60 <= hm < 13 * 60 + 45)
        s1_done = (hm >= 13 * 60 + 45)
        s2_active = (13 * 60 + 45 <= hm < 14 * 60)
        s2_done = (hm >= 14 * 60)
        s3_active = (14 * 60 <= hm < 14 * 60 + 25)
        s3_done = (hm >= 14 * 60 + 25)

        s1_badge = "ĐANG DIỄN RA" if s1_active else ("ĐÃ HOÀN TẤT" if s1_done else "CHỜ ĐẾN GIỜ")
        s2_badge = "ĐANG DIỄN RA" if s2_active else ("ĐÃ HOÀN TẤT" if s2_done else "CHUẨN BỊ ĐẾN")
        s3_badge = "⭐ KHUNG GIỜ VÀNG" if s3_active else ("ĐÃ HOÀN TẤT" if s3_done else "CHỜ BẤM CÒ")

        return f"""
        <div style="display: flex; flex-direction: column; gap: 10px;" id="afternoon-tactical-stages">
            <div id="stage-1-card" class="action-plan-hero-card" style="border: 1.5px solid rgba(56, 189, 248, 0.5); background: linear-gradient(135deg, rgba(14, 165, 233, 0.15), rgba(15, 23, 42, 0.88)); border-radius: 9px; padding: 12px; display: flex; flex-direction: column; gap: 6px;">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <span id="stage-1-badge" class="action-plan-tag" style="background: rgba(56, 189, 248, 0.25); color: #38bdf8; font-weight: 800;">
                        <span class="war-room-live-dot" style="background:#38bdf8;"></span> {s1_badge}
                    </span>
                    <span style="font-size: 11.5px; font-weight: 800; color: #38bdf8; font-family: monospace;">13:00 – 13:45</span>
                </div>
                <div style="font-size: 13px; font-weight: 800; color: #f8fafc;">
                    1. Giai Đoạn 1 (13:00 – 13:45): Hấp Thụ Hàng T+2.5 Về Tài Khoản
                </div>
                <div style="font-size: 11px; color: #cbd5e1; line-height: 1.55;">
                    • Vị thế hiện giữ: <strong>{total_shares} CP ({holdings_desc})</strong> | Tiền mặt: <strong>{cash_str} ({cash_pct:.1f}%)</strong>. Tuyệt đối không mua đuổi trước 13h45.
                </div>
            </div>

            <div id="stage-2-card" style="background: rgba(30, 41, 59, 0.5); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 9px; padding: 12px; display: flex; flex-direction: column; gap: 6px;">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <span id="stage-2-badge" style="font-size: 10px; font-weight: 800; color: #94a3b8; background: rgba(148, 163, 184, 0.15); padding: 2px 8px; border-radius: 4px;">{s2_badge}</span>
                    <span style="font-size: 11px; font-weight: 800; color: #94a3b8; font-family: monospace;">13:45 – 13:55</span>
                </div>
                <div style="font-size: 13px; font-weight: 800; color: #f1f5f9;">
                    2. Giai Đoạn 2 (13:45 – 13:55): Thẩm Định Độ Cạn Cung &amp; Orderbook 3 Bước Giá
                </div>
                <div style="font-size: 11px; color: #cbd5e1; line-height: 1.55;">
                    • Theo dõi Mua chủ động: {standby_bullets}. Kiểm soát chặt Stop 2xATR trên toàn bộ danh mục.
                </div>
            </div>

            <div id="stage-3-card" style="background: rgba(15, 23, 42, 0.7); border: 1.5px solid rgba(245, 158, 11, 0.5); border-radius: 9px; padding: 12px; display: flex; flex-direction: column; gap: 6px;">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <span id="stage-3-badge" style="font-size: 10px; font-weight: 800; color: #fbbf24; background: rgba(245, 158, 11, 0.2); padding: 2px 8px; border-radius: 4px;">{s3_badge}</span>
                    <span style="font-size: 11px; font-weight: 800; color: #fbbf24; font-family: monospace;">14:00 – 14:25</span>
                </div>
                <div style="font-size: 13px; font-weight: 800; color: #fbbf24;">
                    3. Giai Đoạn 3 (14:00 – 14:25): ⭐ KHUNG GIỜ VÀNG — {regime_label}
                </div>
                <div style="font-size: 11px; color: #e2e8f0; line-height: 1.5;">
                    • Hạn mức giải ngân mới tối đa: <strong>{max_alloc}% Cash</strong> từ két <strong>{cash_str}</strong>. Đặt lệnh LO chuẩn chỉ hoặc bảo vệ vị thế đang giữ!
                </div>
            </div>
        </div>
        """

    # Evening / Off-hours: 14:45 - 24:00 or < 08:30
    else:
        return f"""
        <div style="display: flex; flex-direction: column; gap: 10px;" id="afternoon-tactical-stages">
            <div id="stage-1-card" class="action-plan-hero-card" style="border: 1.5px solid rgba(192, 132, 252, 0.5); background: linear-gradient(135deg, rgba(168, 85, 247, 0.15), rgba(15, 23, 42, 0.88)); border-radius: 9px; padding: 12px; display: flex; flex-direction: column; gap: 6px;">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <span class="action-plan-tag" style="background: rgba(168, 85, 247, 0.25); color: #c084fc; font-weight: 800;">🗽 PHỐ WALL CA TỐI / SAU GIỜ GD</span>
                    <span style="font-size: 11.5px; font-weight: 800; color: #c084fc; font-family: monospace;">Ca Tối &amp; Đêm</span>
                </div>
                <div style="font-size: 13px; font-weight: 800; color: #f8fafc;">
                    Tổng Kết Live SSOT &amp; Chuyển Giao Trực Chiến Alex (Phố Wall)
                </div>
                <div style="font-size: 11px; color: #cbd5e1; line-height: 1.55;">
                    • Két tiền mặt bảo toàn: <strong>{cash_str} ({cash_pct:.1f}%)</strong> | Cổ phiếu đang giữ: <strong>{total_shares} CP ({holdings_desc})</strong> | Chế độ thị trường gần nhất: <strong>{regime_label}</strong>.
                    <div style="margin-top: 5px; display: flex; flex-direction: column; gap: 2px;">{holdings_bullets}</div>
                </div>
            </div>
        </div>
        """


def _render_war_room_weekly_html(wr_state: Dict[str, Any]) -> Dict[str, str]:
    wp = wr_state.get("weekly_reference_plan", {}) or {}
    week_label = html_lib.escape(str(wp.get("week_label", "Tuần Giao Dịch")))
    basis = html_lib.escape(str(wp.get("basis", "SSOT Living War-Room")))
    approved_by = html_lib.escape(str(wp.get("approved_by", "Chủ tịch Trần Quốc Thiên Phước")))
    mandate = html_lib.escape(str(wp.get("constitution_mandate", "")))

    days_html = ""
    for d in wp.get("days", []):
        st = str(d.get("status", "UPCOMING")).upper()
        is_done = st == "COMPLETED"
        is_act = st == "ACTIVE"
        bdr = "rgba(16, 185, 129, 0.35)" if is_done else ("rgba(56, 189, 248, 0.4)" if is_act else "rgba(148, 163, 184, 0.2)")
        bg = "rgba(16, 185, 129, 0.08)" if is_done else ("rgba(14, 165, 233, 0.1)" if is_act else "rgba(15, 23, 42, 0.7)")
        col = "#34d399" if is_done else ("#38bdf8" if is_act else "#94a3b8")
        body = html_lib.escape(str(d.get("execution_actual") or d.get("guideline") or ""))
        cond = html_lib.escape(str(d.get("action_condition") or ""))
        cond_html = f'<div style="margin-top:4px; color:#94a3b8;">{cond}</div>' if cond else ""
        days_html += f"""
            <div style="background: {bg}; border: 1px solid {bdr}; border-radius: 10px; padding: 12px; display: flex; flex-direction: column; gap: 6px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <strong style="color: {col}; font-size: 12px;">{html_lib.escape(str(d.get('day_name', '')))}</strong>
                    <span style="background: rgba(15, 23, 42, 0.6); color: {col}; font-size: 9.5px; font-weight: 800; padding: 2px 6px; border-radius: 4px;">{html_lib.escape(str(d.get('status_badge', st)))}</span>
                </div>
                <div style="font-size: 11.5px; font-weight: 800; color: #f8fafc;">{html_lib.escape(str(d.get('theme', '')))}</div>
                <div style="font-size: 10.5px; color: #cbd5e1; line-height: 1.45;">{body}{cond_html}</div>
            </div>
        """

    wl_rows = ""
    for w in wp.get("approved_watchlist", []):
        sym = html_lib.escape(str(w.get("symbol", "")))
        ex = int(w.get("executed_shares", 0) or 0)
        st_col = "#34d399" if ex > 0 else "#fbbf24"
        st_bg = "rgba(16, 185, 129, 0.2)" if ex > 0 else "rgba(245, 158, 11, 0.2)"
        wl_rows += f"""
            <tr>
                <td><strong style="color: #38bdf8;">{sym}</strong></td>
                <td><span style="color: #cbd5e1;">{html_lib.escape(str(w.get('tier', '')))}</span></td>
                <td>{html_lib.escape(str(w.get('entry_zone', '')))}</td>
                <td style="color: #ef4444; font-weight: 700;">{html_lib.escape(str(w.get('stop_loss_2xatr', '')))}</td>
                <td>{html_lib.escape(str(w.get('tp1', '')))} / {html_lib.escape(str(w.get('tp2', '')))}</td>
                <td>{html_lib.escape(str(w.get('weekly_limit', '')))}</td>
                <td><span style="background: {st_bg}; color: {st_col}; padding: 2px 6px; border-radius: 4px; font-weight: 700;">{html_lib.escape(str(w.get('current_status', '')))}</span></td>
            </tr>
        """

    return {
        "week_label": week_label,
        "basis_html": f"Căn cứ: <strong>{basis}</strong> • {approved_by}",
        "mandate_html": mandate,
        "days_html": days_html,
        "watchlist_rows": wl_rows,
    }


def _render_war_room_picks_html(wr_state: Dict[str, Any]) -> str:
    picks = wr_state.get("dynamic_picks") or []
    if not picks:
        picks = [
            {
                "code": s.get("code", ""),
                "name": s.get("name", ""),
                "tier": s.get("tier", "Watchlist"),
                "is_holding": s.get("is_holding", False),
                "price": s.get("price", 0),
                "probe_target": s.get("probe_target", 0),
                "stop_loss": s.get("stop_loss", 0),
                "tp1": s.get("tp1", 0),
                "tp2": s.get("tp2", 0),
                "rr_ratio": 2.5,
                "ev_pct": 8.0,
                "catalyst": s.get("catalyst", ""),
                "security_label": s.get("security_label", ""),
            }
            for s in (wr_state.get("live_stocks") or [])[:4]
        ]

    cards = []
    standby_cards = []
    for idx, p in enumerate(picks):
        code = html_lib.escape(str(p.get("code", "")))
        name = html_lib.escape(str(p.get("name", code)))
        tier = html_lib.escape(str(p.get("tier", "Tiêu điểm")))
        is_hold = bool(p.get("is_holding"))
        price = float(p.get("price", 0) or 0)
        probe = float(p.get("probe_target", price) or 0)
        stop = float(p.get("stop_loss", 0) or 0)
        tp1 = float(p.get("tp1", 0) or 0)
        tp2 = float(p.get("tp2", 0) or 0)
        rr = float(p.get("rr_ratio", 0) or 0)
        ev = float(p.get("ev_pct", 0) or 0)
        shares = int(p.get("holding_shares", 0) or 0)
        lot_val = (probe if probe > 0 else price) * 100
        cat = html_lib.escape(str(p.get("catalyst", "")))
        sec_lbl = html_lib.escape(str(p.get("security_label", "")))

        if idx < 2 or is_hold:
            cls = "leader" if (idx == 0 or is_hold) else "alpha"
            badge_col = "#10b981" if cls == "leader" else "#38bdf8"
            badge_txt = f"ĐANG GIỮ {shares} CP" if is_hold else tier.upper()
            stop_pct_str = f" ({((stop - price) / price * 100):+.1f}%)" if price > 0 and stop > 0 else ""
            tp_str = f"{tp1/1000:.2f}k / {tp2/1000:.2f}k" if tp1 > 0 and tp2 > 0 else (f"{tp1/1000:.2f}k" if tp1 > 0 else "N/A")
            cards.append(f"""
                <div class="stock-pick-card {cls}">
                    <div class="stock-card-top">
                        <div>
                            <span class="stock-ticker">{code}</span>
                            <span class="stock-name">{name}</span>
                        </div>
                        <span style="font-size: 10px; font-weight: 800; color: {badge_col}; background: rgba(16, 185, 129, 0.15); padding: 2px 6px; border-radius: 4px;">{badge_txt}</span>
                    </div>
                    <div class="stock-stats-grid">
                        <div class="stock-stat-item">
                            <span class="stat-label">Live / Mục tiêu Gom</span>
                            <span class="stat-val">{price:,.0f} / ≤ {probe:,.0f} ₫</span>
                        </div>
                        <div class="stock-stat-item">
                            <span class="stat-label">Stop 2xATR</span>
                            <span class="stat-val loss">{stop:,.0f} ₫{stop_pct_str}</span>
                        </div>
                        <div class="stock-stat-item">
                            <span class="stat-label">Mục Tiêu TP1 / TP2</span>
                            <span class="stat-val gain">{tp_str}</span>
                        </div>
                        <div class="stock-stat-item">
                            <span class="stat-label">Tỷ Lệ R:R</span>
                            <span class="stat-val gold">1 : {rr:.2f}</span>
                        </div>
                        <div class="stock-stat-item">
                            <span class="stat-label">Kỳ Vọng EV%</span>
                            <span class="stat-val gain">{ev:+.1f}%</span>
                        </div>
                        <div class="stock-stat-item">
                            <span class="stat-label">Vốn 100 CP</span>
                            <span class="stat-val">{lot_val:,.0f} ₫</span>
                        </div>
                    </div>
                    <div class="stock-catalyst">⚡ <strong>{sec_lbl}</strong> | {cat}</div>
                </div>
            """)
        else:
            standby_cards.append(f"""
                <div class="stock-pick-card standby">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span class="stock-ticker">{code}</span>
                        <span style="font-size:10px; color:#94a3b8;">{html_lib.escape(str(p.get('action_code', 'STANDBY')))}</span>
                    </div>
                    <div style="font-size:11px; color:#cbd5e1;">Live {price/1000:.2f}k | Gom {probe/1000:.2f}k | Stop {stop/1000:.2f}k</div>
                    <div style="font-size:10px; color:#94a3b8;">{cat[:95]}</div>
                </div>
            """)

    out = "".join(cards)
    if standby_cards:
        out += '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">' + "".join(standby_cards[:4]) + "</div>"
    return out or '<div style="font-size:11.5px; color:#94a3b8;">Chưa có mã mục tiêu trong sổ lệnh.</div>'


def _render_war_room_directives_html(wr_state: Dict[str, Any]) -> str:
    items = wr_state.get("directives_history") or []
    html_parts = []
    for d in items:
        role = d.get("role", "specialist")
        role_cls = "chairman" if role == "chairman" else ("sentinel" if role == "sentinel" else "specialist")
        sender = html_lib.escape(str(d.get("sender", "")))
        ts = html_lib.escape(str(d.get("timestamp", "")))
        content = html_lib.escape(str(d.get("content", ""))).replace("\n", "<br>")
        html_parts.append(f"""
            <div class="directive-msg {role_cls}">
                <div class="directive-msg-head">
                    <span>{sender}</span>
                    <span style="font-weight:400; color:#94a3b8;">{ts}</span>
                </div>
                <div class="directive-msg-body">{content}</div>
            </div>
        """)
    return "".join(html_parts)


def _render_war_room_holdings_html(wr_state: Dict[str, Any]) -> str:
    vs = wr_state.get("victor_sentinel", {}) or {}
    holdings = vs.get("holdings") or []
    total_shares = int(vs.get("total_shares", 0) or 0)
    if not holdings:
        return """
            <div style="font-size: 11px; font-weight: 800; color: #34d399; display: flex; justify-content: space-between;">
                <span>📦 DANH MỤC ĐÃ GIẢI NGÂN (0 MÃ • 0 CP)</span>
                <span>🛡️ 100% TIỀN MẶT</span>
            </div>
            <div style="font-size: 11px; color: #94a3b8; padding: 4px 0;">
                Két tiền mặt đang bảo toàn 100%, sẵn sàng giải ngân hoặc cập nhật qua Form Sync TCInvest bên dưới.
            </div>
        """

    rows = []
    for h in holdings:
        sym = html_lib.escape(str(h.get("symbol", "")))
        sh = int(h.get("shares", 0) or 0)
        ep = float(h.get("avg_cost", h.get("entry_price", 0)) or 0)
        cp = float(h.get("current_price", ep) or 0)
        pnl = float(h.get("pnl_vnd", h.get("unrealized_pnl_vnd", 0)) or 0)
        pnl_p = float(h.get("pnl_pct", h.get("unrealized_pnl_pct", 0)) or 0)
        sl = float(h.get("stop_loss", 0) or 0)
        p_col = "#34d399" if pnl >= 0 else "#f87171"
        rows.append(f"""
            <div style="background: rgba(30, 41, 59, 0.7); padding: 6px 8px; border-radius: 6px; font-size: 11px; display: flex; justify-content: space-between; align-items: center; gap: 6px; flex-wrap: wrap;">
                <div><strong style="color: #38bdf8;">{sym}</strong> <span style="color: #94a3b8;">({sh} CP)</span></div>
                <div>Vốn: <span style="color: #cbd5e1;">{ep:,.0f} đ</span> ➔ Live: <span style="color: {p_col};">{cp:,.0f} đ</span></div>
                <div>PnL: <strong style="color: {p_col};">{pnl:+,.0f} đ ({pnl_p:+.2f}%)</strong></div>
                <div style="color: #fbbf24; font-size: 10px;">Stop: {sl:,.0f} đ</div>
            </div>
        """)
    return f"""
        <div style="font-size: 11px; font-weight: 800; color: #38bdf8; display: flex; justify-content: space-between;">
            <span>📦 DANH MỤC ĐÃ GIẢI NGÂN ({len(holdings)} MÃ • {total_shares} CP)</span>
            <span style="color: #34d399;">🛡️ STOP 2xATR BẢO VỆ</span>
        </div>
        <div style="display: flex; flex-direction: column; gap: 5px;">{''.join(rows)}</div>
    """


def _render_war_room_stocks_rows_html(wr_state: Dict[str, Any]) -> str:
    rows = []
    for s in (wr_state.get("live_stocks") or []):
        code = html_lib.escape(str(s.get("code", "")))
        price = float(s.get("price", 0) or 0)
        chg = float(s.get("change_pct", 0) or 0)
        vol = int(s.get("volume", 0) or 0)
        buy_up = float(s.get("active_buy_pct", 50.0) or 50.0)
        sec = str(s.get("security_status", "STANDBY"))
        act = str(s.get("action_code", sec))
        p_cls = "up" if chg > 0 else ("down" if chg < 0 else "ref")
        sign = "+" if chg > 0 else ""
        vol_str = f"{vol / 1000000:.1f}M" if vol >= 1000000 else f"{vol / 1000:.0f}k"
        col = "#34d399" if sec in ("SAFE", "TAKE_PROFIT") else ("#f87171" if sec in ("CRITICAL", "WARNING") else "#fbbf24")
        badge = f"🟢 {act}" if sec == "SAFE" else (f"🎯 {act}" if sec == "TAKE_PROFIT" else (f"🚨 {act}" if sec in ("CRITICAL", "WARNING") else f"🟡 {act}"))
        rows.append(f"""
            <tr>
                <td><strong style="color:#38bdf8;">{code}</strong>{' ★' if s.get('is_holding') else ''}</td>
                <td class="price-badge {p_cls}">{price:,.0f}</td>
                <td class="price-badge {p_cls}">{sign}{chg:.2f}%</td>
                <td>{vol_str}</td>
                <td style="color:{'#34d399' if buy_up >= 50 else '#f87171'};">{buy_up:.1f}%</td>
                <td><span style="color:{col}; font-weight:700; font-size:10px;">{html_lib.escape(badge)}</span></td>
            </tr>
        """)
    return "".join(rows) or '<tr><td colspan="6" style="text-align:center; color:#94a3b8;">Đang tải bảng giá live...</td></tr>'


def _render_war_room_threat_html(wr_state: Dict[str, Any]) -> str:
    vs = wr_state.get("victor_sentinel", {}) or {}
    lvl = int(vs.get("threat_level_num", 1) or 1)
    lbl = html_lib.escape(str(vs.get("threat_label", "CẤP 1 — AN TOÀN")))
    col = "#10b981" if lvl <= 1 else ("#38bdf8" if lvl == 2 else ("#fbbf24" if lvl == 3 else "#ef4444"))
    bars = "".join(
        f'<div style="flex: 1; height: 6px; border-radius: 3px; background: {col if i <= lvl else "rgba(148, 163, 184, 0.2)"}; {"box-shadow: 0 0 6px " + col + ";" if i <= lvl else ""}"></div>'
        for i in range(1, 6)
    )
    return f"""
        <div style="font-size: 11px; font-weight: 800; color: #f8fafc; display: flex; justify-content: space-between;">
            <span>RADAR 5 CẤP ĐỘ NGUY HIỂM</span>
            <span style="color: {col};">● CẤP {lvl}</span>
        </div>
        <div style="display: flex; gap: 4px;">{bars}</div>
        <div style="font-size: 10.5px; color: #cbd5e1; line-height: 1.35;">{lbl}</div>
    """


def _format_market_overview_ui(wr_state: Dict[str, Any]) -> Dict[str, Any]:
    mo = wr_state.get("market_overview", {}) or {}
    vni = mo.get("vn_index", {}) or {}
    vn30 = mo.get("vn30_index", {}) or {}
    br = mo.get("market_breadth", {}) or {}
    reg = wr_state.get("intraday_regime", {}) or {}
    mq = wr_state.get("minh_quan_blueprint", {}) or {}

    vni_val = float(vni.get("value", 0) or 0)
    vni_pts = float(vni.get("change_pts", 0) or 0)
    vni_pct = float(vni.get("change_pct", 0) or 0)
    vn30_val = float(vn30.get("value", 0) or 0)
    vn30_pts = float(vn30.get("change_pts", 0) or 0)
    vn30_pct = float(vn30.get("change_pct", 0) or 0)

    return {
        "vni_val_str": f"{vni_val:,.2f}" if vni_val > 0 else "--",
        "vni_pts_str": f"{vni_pts:+.2f} ({vni_pct:+.2f}%)" if vni_val > 0 else "--",
        "vni_cls": "up" if vni_pct >= 0 else "down",
        "vni_col": "#34d399" if vni_pct >= 0 else "#f87171",
        "turnover_str": html_lib.escape(str(vni.get("turnover_ty_vnd", "--"))),
        "foreign_str": html_lib.escape(str(vni.get("foreign_net_ty_vnd", "--"))),
        "vn30_val_str": f"{vn30_val:,.2f}" if vn30_val > 0 else "--",
        "vn30_pts_str": f"{vn30_pts:+.2f} ({vn30_pct:+.2f}%)" if vn30_val > 0 else "--",
        "vn30_cls": "up" if vn30_pct >= 0 else "down",
        "vn30_col": "#34d399" if vn30_pct >= 0 else "#f87171",
        "basis_str": html_lib.escape(str(vn30.get("basis_vn30f", "--"))),
        "status_str": html_lib.escape(str(vni.get("status", "ĐANG ĐỒNG BỘ"))),
        "breadth_str": f"{int(br.get('advancers', 0) or 0)} Tăng / {int(br.get('decliners', 0) or 0)} Giảm",
        "regime_label": html_lib.escape(str(reg.get("label", "GIẰNG CO PHÂN HÓA"))),
        "regime_color": html_lib.escape(str(reg.get("badge_color", "#fbbf24"))),
        "mastery_str": f"{float(mq.get('mastery_score', 98.5)):.1f}",
        "ev_str": f"{float(mq.get('expected_value_pct', 0)):+.2f}%",
        "pw_str": f"{float(mq.get('win_rate_pct', 0)):.1f}%",
        "rr_str": html_lib.escape(str(mq.get("average_rr", "1:2.50"))),
        "rules_html": "".join(f'<div style="font-size: 11px; color: #cbd5e1;">• {html_lib.escape(str(r))}</div>' for r in (mq.get("rules") or [])),
    }


def _render_war_room_spillover_slippage_html(wr_state: Dict[str, Any]) -> str:
    sp = wr_state.get("global_spillover") or {}
    tr = (wr_state.get("execution_tracker") or {}).get("filters") or {}
    m = sp.get("metrics") or {}
    mult = float(sp.get("risk_multiplier", 1.0) or 1.0)
    cap = int(sp.get("max_allocation_pct", 45) or 45)
    bias_lbl = html_lib.escape(str(sp.get("bias_label", "⚖️ TRUNG TÍNH PHÂN HÓA")))
    b_col = html_lib.escape(str(sp.get("badge_color", "#38bdf8")))
    sp500 = m.get("SP500") or {}
    vix = m.get("VIX") or {}
    dxy = m.get("DXY") or {}
    oil = m.get("WTI_OIL") or {}
    min_bu = float(tr.get("min_buy_up_pct", 58.0) or 58.0)
    max_rsi = float(tr.get("max_rsi_buy", 70.0) or 70.0)
    avg_slip = float(tr.get("avg_slippage_bps", 0.0) or 0.0)
    sig_cnt = int(tr.get("total_signals_tracked", 0) or 0)

    return f"""
        <div style="font-size: 10.5px; color: {b_col}; font-weight: 800;">{bias_lbl}</div>
        <div style="font-size: 10.5px; color: #cbd5e1;">
            Hệ số liên thị trường: <strong style="color:#fff;">{mult:.2f}x</strong> • Trần giải ngân: <strong style="color:#fbbf24;">{cap}% NAV</strong>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 5px; font-size: 10px;">
            <div style="background: rgba(15, 23, 42, 0.7); padding: 4px 6px; border-radius: 4px; border: 1px solid rgba(148, 163, 184, 0.15);">S&amp;P500: <strong style="color:#38bdf8;">{float(sp500.get('change_1d_pct', 0)):+.2f}%</strong></div>
            <div style="background: rgba(15, 23, 42, 0.7); padding: 4px 6px; border-radius: 4px; border: 1px solid rgba(148, 163, 184, 0.15);">VIX: <strong style="color:#fbbf24;">{float(vix.get('last_price', 18.0)):.1f}</strong></div>
            <div style="background: rgba(15, 23, 42, 0.7); padding: 4px 6px; border-radius: 4px; border: 1px solid rgba(148, 163, 184, 0.15);">DXY: <strong style="color:#cbd5e1;">{float(dxy.get('last_price', 103.0)):.1f}</strong></div>
            <div style="background: rgba(15, 23, 42, 0.7); padding: 4px 6px; border-radius: 4px; border: 1px solid rgba(148, 163, 184, 0.15);">WTI Oil: <strong style="color:#34d399;">{float(oil.get('last_price', 0)):.1f}$</strong></div>
        </div>
        <div style="margin-top: 2px; padding-top: 5px; border-top: 1px dashed rgba(148, 163, 184, 0.25); font-size: 10px; color: #94a3b8;">
            🎯 <strong>Bộ Lọc Bull-Trap &amp; Slippage:</strong> BuyUp &ge; <strong style="color:#34d399;">{min_bu:.0f}%</strong> • RSI &le; <strong style="color:#fbbf24;">{max_rsi:.0f}</strong> • Tín hiệu: <strong style="color:#fff;">{sig_cnt}</strong> (Slip: {avg_slip:+.1f} bps)
        </div>"""



try:
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def _render_portfolio_tab_live_sections_html(wr_state: Dict[str, Any], ssot: Dict[str, Any]) -> str:
    """Render 100% live-synced Portfolio Tab tables (Holdings + Alpha Watchlist + Intraday Protocol)."""
    import html as _h
    v_surv = wr_state.get("victor_deep_surveillance", {}) or {}
    plan = wr_state.get("live_execution_master_plan", {}) or {}
    held_list = v_surv.get("held_positions_book", []) or []
    watch_list = v_surv.get("alpha_watchlist_book", []) or []
    scens = plan.get("contingency_scenarios", []) or []

    t_date = _h.escape(str(plan.get("trading_date") or wr_state.get("trading_date") or get_ict_now().strftime("%Y-%m-%d")))
    s_time = _h.escape(str(wr_state.get("server_time") or get_ict_now().strftime("%H:%M:%S")))
    regime_lbl = _h.escape(str(plan.get("regime_label") or (wr_state.get("intraday_regime", {}) or {}).get("label") or "PHÒNG TÁC CHIẾN LIVE"))
    phase_lbl = _h.escape(str(plan.get("session_phase_label") or (wr_state.get("phase_info", {}) or {}).get("phase_name") or "LIVE MONITOR"))

    held_rows = ""
    for h in held_list:
        pnl_val = float(h.get("pnl_vnd", 0) or 0)
        pnl_pct = float(h.get("pnl_pct", 0) or 0)
        p_col = "#34d399" if pnl_val >= 0 else "#f87171"
        sign = "+" if pnl_val >= 0 else ""
        held_rows += f"""
        <tr style="background: rgba(56, 189, 248, 0.04);">
            <td style="padding: 12px 14px; font-weight: 800; color: #38bdf8; font-family: 'JetBrains Mono', monospace;">{_h.escape(str(h.get('symbol', '')))}</td>
            <td style="padding: 12px 14px;">{_h.escape(str(h.get('name', '')))}</td>
            <td style="padding: 12px 14px; font-family: 'JetBrains Mono', monospace;">{int(h.get('shares', 0) or 0)} CP (T0: {int(h.get('tradable_shares', 0) or 0)})</td>
            <td style="padding: 12px 14px; font-family: 'JetBrains Mono', monospace;">{float(h.get('entry_price', 0) or 0):,.0f}đ</td>
            <td style="padding: 12px 14px; font-family: 'JetBrains Mono', monospace; font-weight: 700;">{float(h.get('live_price', 0) or 0):,.0f}đ</td>
            <td style="padding: 12px 14px; font-family: 'JetBrains Mono', monospace; color: {p_col}; font-weight: 800;">{sign}{pnl_val:,.0f}đ ({sign}{pnl_pct:.2f}%)</td>
            <td style="padding: 12px 14px; color: #f87171; font-weight: 700;">{float(h.get('stop_loss', 0) or 0):,.0f}đ (+{float(h.get('stop_distance_pct', 0) or 0):.2f}%)</td>
            <td style="padding: 12px 14px; color: #34d399; font-weight: 700;">{float(h.get('tp1', 0) or 0):,.0f} / {float(h.get('tp2', 0) or 0):,.0f}đ</td>
            <td style="padding: 12px 14px; font-size: 12px; color: #cbd5e1;">{_h.escape(str(h.get('victor_status_badge', '')))} — {_h.escape(str(h.get('victor_instruction', '')))}</td>
        </tr>"""
    if not held_rows:
        held_rows = '<tr><td colspan="9" style="text-align:center; padding:14px; color:#94a3b8;">100% Tiền mặt — Chưa mở vị thế cổ phiếu.</td></tr>'

    watch_rows = ""
    for w in watch_list:
        watch_rows += f"""
        <tr>
            <td style="padding: 10px 14px; font-weight: 800; color: #fbbf24; font-family: 'JetBrains Mono', monospace;">{_h.escape(str(w.get('symbol', '')))}</td>
            <td style="padding: 10px 14px;">{_h.escape(str(w.get('sector_name', '')))}</td>
            <td style="padding: 10px 14px; font-family: 'JetBrains Mono', monospace;">{float(w.get('live_price', 0) or 0):,.0f}đ</td>
            <td style="padding: 10px 14px; font-family: 'JetBrains Mono', monospace; color:#38bdf8;">{float(w.get('probe_target', 0) or 0):,.0f}đ</td>
            <td style="padding: 10px 14px; font-family: 'JetBrains Mono', monospace;">OCF {float(w.get('ocf_ratio', 1) or 1):.2f}x • MOS +{float(w.get('mos_pct', 0) or 0):.1f}%</td>
            <td style="padding: 10px 14px; font-family: 'JetBrains Mono', monospace;">{float(w.get('lot_100_cost_vnd', 0) or 0):,.0f}đ ({float(w.get('nav_pct_per_lot', 0) or 0):.1f}% NAV)</td>
            <td style="padding: 10px 14px; font-size: 12px;"><strong>{_h.escape(str(w.get('victor_signal', '')))}</strong> — {_h.escape(str(w.get('catalyst', '')))}</td>
        </tr>"""

    scen_colors = ["#10b981", "#fbbf24", "#ef4444"]
    scen_cards = ""
    for idx, sc in enumerate(scens):
        col = scen_colors[idx % 3]
        scen_cards += f"""
        <div style="background: var(--bg-surface); padding: 12px 14px; border-radius: 8px; border-left: 3px solid {col};">
            <div style="font-size: 11px; color: {col}; font-weight: 700;">{_h.escape(str(sc.get('title', '')))}</div>
            <div style="font-size: 12px; color: #e2e8f0; margin-top: 4px;">{_h.escape(str(sc.get('trigger', '')))}</div>
            <div style="font-size: 11.5px; color: #cbd5e1; margin-top: 4px;">{_h.escape(str(sc.get('portfolio_action', '')))} (Tiền mặt mục tiêu: {float(sc.get('cash_target_pct', 0) or 0):.1f}%)</div>
        </div>"""

    return f"""
            <div style="background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 16px; overflow: hidden; padding: 24px; margin-bottom: 22px;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 18px; border-bottom: 1px solid rgba(255, 255, 255, 0.08); padding-bottom: 14px;">
                    <div>
                        <h3 style="font-size: 17px; color: #fff; font-weight: 800; display: flex; align-items: center; gap: 10px;">
                            <span>🎯</span> <span>KẾ HOẠCH TÁC CHIẾN &amp; SỔ LỆNH LIVE THEO SSOT (PHIÊN {t_date})</span>
                        </h3>
                        <p style="font-size: 12.5px; color: #94a3b8; margin-top: 4px;">
                            Tài khoản TCBS <strong style="color: #38bdf8;">105C307855</strong> (Chủ tịch: <strong>Trần Quốc Thiên Phước</strong>) • NAV Live: <strong style="color: #34d399;">{ssot['nav_str']}</strong> (Tiền mặt: {ssot['cash_str']} • Cổ phiếu: {ssot['stocks_str']})
                        </p>
                        <div id="portfolio-tab-plan-meta" style="font-size: 11.5px; color: #38bdf8; margin-top: 3px;">
                            Cập nhật realtime: {t_date} {s_time} ICT • Chế độ: {regime_lbl} • Pha: {phase_lbl}
                        </div>
                    </div>
                    <div>
                        <span style="background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.35); padding: 5px 12px; border-radius: 9999px; font-size: 11.5px; font-weight: 800;">
                            ● ĐỒNG BỘ 100% SSOT &amp; BÁO CÁO QUỸ
                        </span>
                    </div>
                </div>

                <div style="margin-bottom: 20px;">
                    <div style="font-size: 12px; font-weight: 800; color: #38bdf8; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 10px; display: flex; align-items: center; gap: 6px;">
                        <span>🔥</span> <span>PHẦN 1: DANH MỤC ĐANG NẮM GIỮ &amp; LỆNH PHÒNG THỦ / T+0 LIVE (VICTOR SENTINEL)</span>
                    </div>
                    <div style="overflow-x: auto;">
                        <table class="standard-table">
                            <thead>
                                <tr>
                                    <th>Mã</th>
                                    <th>Doanh Nghiệp</th>
                                    <th>Số Lượng</th>
                                    <th>Giá Vốn SSOT</th>
                                    <th>Thị Giá Live</th>
                                    <th>Lãi / Lỗ Ròng</th>
                                    <th>Stop 2xATR (% Cách)</th>
                                    <th>TP1 / TP2</th>
                                    <th>Chỉ Thị Tác Chiến Live</th>
                                </tr>
                            </thead>
                            <tbody id="portfolio-tab-holdings-tbody">{held_rows}</tbody>
                        </table>
                    </div>
                </div>

                <div style="margin-bottom: 20px;">
                    <div style="font-size: 12px; font-weight: 800; color: #fbbf24; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 10px; display: flex; align-items: center; gap: 6px;">
                        <span>🛡️</span> <span>PHẦN 2: WATCHLIST SIÊU CỔ PHIẾU TIỀM NĂNG &amp; CHECK LÔ 100 (&lt;= 33% NAV)</span>
                    </div>
                    <div style="overflow-x: auto;">
                        <table class="standard-table">
                            <thead>
                                <tr>
                                    <th>Mã</th>
                                    <th>Ngành</th>
                                    <th>Thị Giá Live</th>
                                    <th>Vùng Canh Nhúng</th>
                                    <th>Sức Khỏe BCTC</th>
                                    <th>Vốn 1 Lô 100 CP</th>
                                    <th>Trạng Thái &amp; Catalyst</th>
                                </tr>
                            </thead>
                            <tbody id="portfolio-tab-standby-tbody">{watch_rows}</tbody>
                        </table>
                    </div>
                </div>

                <div style="background: var(--bg-base); border: 1px solid var(--border-color); border-radius: 12px; padding: 18px 20px;">
                    <div style="font-size: 12px; font-weight: 800; color: #fff; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 12px;">
                        ⏱️ KỊCH BẢN ỨNG PHÓ PHIÊN LIVE ({t_date}) — TIỀN MẶT HIỆN HỮU {ssot['cash_str']} ({ssot['cash_pct']:.1f}% NAV)
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px;">
                        {scen_cards}
                    </div>
                </div>
            </div>
    """


def _render_tab4_live_watchlist_html(wr_state: Dict[str, Any]) -> str:
    """Render live sidebar chart jump buttons for Tab 4 with exact exchange symbols."""
    import html as _h
    v_surv = wr_state.get("victor_deep_surveillance", {}) or {}
    held = v_surv.get("held_positions_book", []) or []
    watch = v_surv.get("alpha_watchlist_book", []) or []
    exchange_map = {"IDC": "HNX:IDC", "BSR": "UPCOM:BSR"}

    items: List[tuple] = []
    for h in held[:2]:
        sym = str(h.get("symbol", "")).upper()
        items.append((sym, f"{float(h.get('live_price', 0) or 0):,.0f}đ (Stop {float(h.get('stop_loss', 0) or 0):,.0f})"))
    for w in watch[:3]:
        sym = str(w.get("symbol", "")).upper()
        items.append((sym, f"{float(w.get('live_price', 0) or 0):,.0f}đ (Canh {float(w.get('probe_target', 0) or 0):,.0f})"))

    if not items:
        items = [("HDB", "Theo dõi live"), ("MSH", "Theo dõi live"), ("BAF", "Alpha Watchlist"), ("IDC", "Alpha Watchlist")]

    out = ""
    for sym, desc in items[:5]:
        tv_sym = exchange_map.get(sym, f"HOSE:{sym}")
        out += f"""
                            <div style="display: flex; justify-content: space-between; align-items: center; background: var(--bg-base); padding: 8px 12px; border-radius: 8px; border: 1px solid var(--border-color);">
                                <div><strong style="color: #38bdf8; font-family: 'JetBrains Mono', monospace;">{_h.escape(sym)}</strong> <span style="font-size: 11.5px; color: var(--text-muted);">{_h.escape(desc)}</span></div>
                                <button onclick="switchTab('portfolio'); switchTVSymbol('{tv_sym}')" style="background: rgba(56, 189, 248, 0.15); border: none; color: #38bdf8; padding: 4px 8px; border-radius: 4px; font-size: 11px; cursor: pointer; font-weight: 700;">Chart</button>
                            </div>"""
    return out


def _render_war_room_v8_command_floor_html(wr_state: Dict[str, Any]) -> str:
    """Render V8.0 Operations Floor inside Tab 3: Victor Surveillance, Master Plan, 14 Depts & Live Reports."""
    import html as _h
    v_surv = wr_state.get("victor_deep_surveillance", {}) or {}
    plan = wr_state.get("live_execution_master_plan", {}) or {}
    depts = wr_state.get("department_live_workstation", []) or []
    feed = wr_state.get("latest_reports_feed", []) or []
    meta = wr_state.get("vault_sync_meta", {}) or {}

    latest_rel = str(meta.get("latest_report_rel_path") or "").replace("\\", "/").replace("'", "\\'")
    sync_badge = (
        f"🟢 Vault Sync: {int(meta.get('today_reports_count', 0) or 0)} Hôm nay / "
        f"{int(meta.get('total_reports_scanned', 0) or 0)} Kho ({meta.get('latest_sync_time', '')})"
    )

    held_rows = ""
    for h in (v_surv.get("held_positions_book", []) or []):
        pnl_v = float(h.get("pnl_vnd", 0) or 0)
        pnl_p = float(h.get("pnl_pct", 0) or 0)
        chg_p = float(h.get("change_pct", 0) or 0)
        buy_up = float(h.get("active_buy_pct", 50) or 50)
        p_col = "#34d399" if pnl_v >= 0 else "#f87171"
        c_col = "#34d399" if chg_p >= 0 else "#f87171"
        held_rows += f"""
        <tr>
            <td style="padding:8px 10px;"><strong style="color:#38bdf8; font-family:'JetBrains Mono',monospace;">{_h.escape(str(h.get('symbol', '')))}</strong><div style="font-size:10px; color:#94a3b8;">{int(h.get('shares', 0) or 0)} CP (T0: {int(h.get('tradable_shares', 0) or 0)})</div></td>
            <td style="padding:8px 10px; font-family:'JetBrains Mono',monospace;"><strong>{float(h.get('live_price', 0) or 0):,.0f}đ</strong><div style="font-size:10px; color:{c_col};">{chg_p:+.2f}% • L:{float(h.get('intraday_low', 0) or 0):,.0f} H:{float(h.get('intraday_high', 0) or 0):,.0f}</div></td>
            <td style="padding:8px 10px; font-family:'JetBrains Mono',monospace; color:#cbd5e1;">{float(h.get('entry_price', 0) or 0):,.0f}đ<div style="font-size:10px; color:{p_col}; font-weight:800;">{pnl_v:+,.0f}đ ({pnl_p:+.2f}%)</div></td>
            <td style="padding:8px 10px;"><div style="font-weight:800; color:#fbbf24;">BuyUp {buy_up:.1f}% • B/A {float(h.get('bid_ask_ratio', 1) or 1):.2f}x</div><div style="font-size:10px; color:#94a3b8;">{_h.escape(str(h.get('orderbook_pressure', '')))}</div></td>
            <td style="padding:8px 10px; font-family:'JetBrains Mono',monospace; color:#f87171;">{float(h.get('stop_loss', 0) or 0):,.0f}đ<div style="font-size:10px; color:#cbd5e1;">Cách +{float(h.get('stop_distance_pct', 0) or 0):.2f}%</div></td>
            <td style="padding:8px 10px; font-family:'JetBrains Mono',monospace; color:#34d399;">{float(h.get('tp1', 0) or 0):,.0f} / {float(h.get('tp2', 0) or 0):,.0f}<div style="font-size:10px; color:#a7f3d0;">TP1 +{float(h.get('tp1_upside_pct', 0) or 0):.1f}%</div></td>
            <td style="padding:8px 10px; font-family:'JetBrains Mono',monospace; color:#fbbf24;">{float(h.get('t0_buy_zone', 0) or 0):,.0f} → {float(h.get('t0_sell_zone', 0) or 0):,.0f}<div style="font-size:10px; color:#94a3b8;">OCF {float(h.get('ocf_ratio', 1) or 1):.2f}x • MOS {float(h.get('mos_pct', 0) or 0):.1f}%</div></td>
            <td style="padding:8px 10px; font-size:11px;"><div style="font-weight:800; color:#f8fafc;">{_h.escape(str(h.get('victor_status_badge', '')))}</div><div style="color:#cbd5e1;">{_h.escape(str(h.get('victor_instruction', '')))}</div></td>
        </tr>"""

    watch_rows = ""
    for w in (v_surv.get("alpha_watchlist_book", []) or []):
        chg_p = float(w.get("change_pct", 0) or 0)
        ok = bool(w.get("constitutional_lot_ok"))
        watch_rows += f"""
        <tr>
            <td style="padding:7px 9px;"><strong style="color:#fbbf24; font-family:'JetBrains Mono',monospace;">{_h.escape(str(w.get('symbol', '')))}</strong><div style="font-size:10px; color:#94a3b8;">{_h.escape(str(w.get('sector_name', '')))}</div></td>
            <td style="padding:7px 9px; font-family:'JetBrains Mono',monospace;"><strong>{float(w.get('live_price', 0) or 0):,.0f}đ</strong> <span style="font-size:10px;">({chg_p:+.2f}%)</span><div style="font-size:10px; color:#94a3b8;">Canh nhúng: {float(w.get('probe_target', 0) or 0):,.0f}đ</div></td>
            <td style="padding:7px 9px; font-family:'JetBrains Mono',monospace;">BuyUp {float(w.get('active_buy_pct', 50) or 50):.1f}% • RSI {float(w.get('rsi14', 50) or 50):.1f}</td>
            <td style="padding:7px 9px; font-family:'JetBrains Mono',monospace;">OCF {float(w.get('ocf_ratio', 1) or 1):.2f}x • MOS <strong style="color:#34d399;">+{float(w.get('mos_pct', 0) or 0):.1f}%</strong></td>
            <td style="padding:7px 9px; font-family:'JetBrains Mono',monospace;">Alpha <strong style="color:#38bdf8;">{float(w.get('alpha_score', 0) or 0):.1f}</strong> • 1:{float(w.get('rr_ratio', 0) or 0):.2f}</td>
            <td style="padding:7px 9px; font-family:'JetBrains Mono',monospace;">{float(w.get('lot_100_cost_vnd', 0) or 0):,.0f}đ<div style="font-size:10px; color:{'#34d399' if ok else '#f87171'};">{float(w.get('nav_pct_per_lot', 0) or 0):.1f}% NAV ({'Đạt <=33%' if ok else 'Vượt trần'})</div></td>
            <td style="padding:7px 9px; font-size:11px;"><div style="font-weight:800; color:#f8fafc;">{_h.escape(str(w.get('victor_signal', '')))}</div><div style="font-size:10px; color:#94a3b8;">{_h.escape(str(w.get('catalyst', '')))}</div></td>
        </tr>"""

    hold_plan_cards = ""
    for item in (plan.get("holdings_action_items", []) or []):
        pv = float(item.get("pnl_vnd", 0) or 0)
        hold_plan_cards += f"""
        <div style="background:rgba(15,23,42,0.8); border:1px solid rgba(56,189,248,0.28); border-radius:8px; padding:10px;">
            <div style="display:flex; justify-content:space-between; align-items:center;"><strong style="color:#38bdf8; font-size:13px;">{_h.escape(str(item.get('symbol', '')))} ({int(item.get('shares', 0) or 0)} CP)</strong><span style="color:{'#34d399' if pv >= 0 else '#f87171'}; font-weight:800; font-size:11.5px;">{pv:+,.0f}đ ({float(item.get('pnl_pct', 0) or 0):+.2f}%)</span></div>
            <div style="font-size:11px; color:#cbd5e1; margin-top:4px;">Giá live: <strong>{float(item.get('current_price', 0) or 0):,.0f}đ</strong> • Stop: <span style="color:#f87171;">{float(item.get('stop_loss', 0) or 0):,.0f}đ</span> • TP1: <span style="color:#34d399;">{float(item.get('tp1', 0) or 0):,.0f}đ</span></div>
            <div style="font-size:11px; color:#fbbf24; margin-top:3px;">Vùng lướt T+0: {_h.escape(str(item.get('t0_zone', '')))}</div>
            <div style="font-size:11px; color:#e2e8f0; margin-top:4px;">{_h.escape(str(item.get('tactical_order_text', '')))}</div>
        </div>"""

    deploy_rows = ""
    for o in (plan.get("new_deployment_orders", []) or []):
        deploy_rows += f"""
        <tr>
            <td style="padding:7px 9px;"><strong style="color:#fbbf24; font-family:'JetBrains Mono',monospace;">{_h.escape(str(o.get('symbol', '')))}</strong></td>
            <td style="padding:7px 9px; font-size:11px; color:#e2e8f0;">{_h.escape(str(o.get('order_type', '')))}</td>
            <td style="padding:7px 9px; font-family:'JetBrains Mono',monospace; color:#38bdf8;">{_h.escape(str(o.get('limit_buy_zone', '')))}</td>
            <td style="padding:7px 9px; font-family:'JetBrains Mono',monospace;"><span style="color:#f87171;">{float(o.get('stop_loss', 0) or 0):,.0f}</span> / <span style="color:#34d399;">{float(o.get('tp1', 0) or 0):,.0f}</span></td>
            <td style="padding:7px 9px; font-family:'JetBrains Mono',monospace;">{float(o.get('est_capital_vnd', 0) or 0):,.0f}đ ({float(o.get('nav_weight_pct', 0) or 0):.1f}%)</td>
            <td style="padding:7px 9px; font-size:11px;"><div style="font-weight:800; color:#f8fafc;">{_h.escape(str(o.get('approval_status', '')))}</div><div style="color:#94a3b8;">{_h.escape(str(o.get('trigger_condition', '')))}</div></td>
        </tr>"""

    scen_cards = ""
    s_cols = ["#10b981", "#fbbf24", "#ef4444"]
    for idx, sc in enumerate(plan.get("contingency_scenarios", []) or []):
        col = s_cols[idx % 3]
        scen_cards += f"""
        <div style="background:rgba(15,23,42,0.78); border-left:3px solid {col}; border-radius:8px; padding:10px;">
            <div style="font-size:11.5px; font-weight:800; color:{col};">{_h.escape(str(sc.get('title', '')))}</div>
            <div style="font-size:11px; color:#94a3b8; margin-top:4px;"><strong>Điều kiện:</strong> {_h.escape(str(sc.get('trigger', '')))}</div>
            <div style="font-size:11px; color:#e2e8f0; margin-top:4px;"><strong>Hành động:</strong> {_h.escape(str(sc.get('portfolio_action', '')))} (Tiền mặt mục tiêu: {float(sc.get('cash_target_pct', 0) or 0):.1f}%)</div>
        </div>"""

    dept_cards = ""
    for d in depts:
        st = str(d.get("stance") or "ACTIVE_MONITOR")
        st_col = "#ef4444" if st == "VETO" else ("#fbbf24" if st == "CAUTION" else "#34d399")
        rpath = str(d.get("latest_report_path") or "").replace("\\", "/").replace("'", "\\'")
        btn_html = (
            f'<button onclick="openReportModal(\'{rpath}\')" style="cursor:pointer; background:rgba(56,189,248,0.14); border:1px solid rgba(56,189,248,0.35); color:#7dd3fc; padding:3px 8px; border-radius:5px; font-size:10px; font-weight:700;">📄 Đọc Báo Cáo</button>'
            if rpath else ""
        )
        dept_cards += f"""
        <div style="background:rgba(15,23,42,0.82); border:1px solid rgba(148,163,184,0.22); border-radius:9px; padding:10px; display:flex; flex-direction:column; justify-content:space-between; gap:6px;">
            <div>
                <div style="display:flex; justify-content:space-between; align-items:center; gap:6px;"><strong style="color:#38bdf8; font-size:11.5px;">{_h.escape(str(d.get('ban_code', '')))} • {_h.escape(str(d.get('officer', '')))}</strong><span style="background:{st_col}22; color:{st_col}; border:1px solid {st_col}55; padding:1px 6px; border-radius:4px; font-size:9.5px; font-weight:800;">● {_h.escape(st)}</span></div>
                <div style="font-size:10.5px; color:#94a3b8; margin-top:2px;">{_h.escape(str(d.get('dept_name', '')))}</div>
                <div style="font-size:11px; color:#e2e8f0; margin-top:5px; line-height:1.45;">{_h.escape(str(d.get('live_finding', '')))}</div>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center; gap:6px; border-top:1px solid rgba(148,163,184,0.14); padding-top:6px;">
                <span style="font-size:9.5px; color:#94a3b8;">{_h.escape(str(d.get('latest_report_date', '')))} {_h.escape(str(d.get('latest_report_time', '')))}</span>
                {btn_html}
            </div>
        </div>"""

    feed_rows = ""
    for r in feed:
        rpath = str(r.get("rel_path") or "").replace("\\", "/").replace("'", "\\'")
        feed_rows += f"""
        <div style="display:flex; justify-content:space-between; align-items:center; gap:10px; background:rgba(15,23,42,0.75); border:1px solid rgba(148,163,184,0.18); border-radius:7px; padding:7px 10px;">
            <div style="min-width:0;">
                <div style="font-size:11px; font-weight:800; color:#f8fafc; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{_h.escape(str(r.get('icon', '📄')))} {_h.escape(str(r.get('title', '')))}</div>
                <div style="font-size:10px; color:#94a3b8;">{_h.escape(str(r.get('dept_name', '')))} • {_h.escape(str(r.get('date', '')))} {_h.escape(str(r.get('time', '')))} ({_h.escape(str(r.get('shift_label', '')))}) • {float(r.get('size_kb', 0) or 0):.1f} KB</div>
            </div>
            <button onclick="openReportModal('{rpath}')" style="cursor:pointer; white-space:nowrap; background:rgba(16,185,129,0.15); border:1px solid rgba(16,185,129,0.4); color:#34d399; padding:4px 10px; border-radius:6px; font-size:10.5px; font-weight:700;">Mở Báo Cáo</button>
        </div>"""

    open_latest_btn = (
        f'<button onclick="openReportModal(\'{latest_rel}\')" style="cursor:pointer; background:rgba(16,185,129,0.16); border:1px solid rgba(16,185,129,0.4); color:#34d399; padding:6px 12px; border-radius:8px; font-size:11.5px; font-weight:800;">📄 Đọc Báo Cáo Intraday Mới Nhất</button>'
        if latest_rel else ""
    )

    return f"""
        <!-- V8.0: LIVE MULTI-DEPARTMENT TACTICAL WAR-ROOM COMMAND FLOOR -->
        <div style="margin-top: 16px; display: flex; flex-direction: column; gap: 14px;">
            <div style="background: linear-gradient(135deg, rgba(15, 23, 42, 0.96), rgba(30, 41, 59, 0.92)); border: 1px solid rgba(16, 185, 129, 0.42); border-radius: 12px; padding: 14px; display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 10px;">
                <div>
                    <div style="font-size: 13.5px; font-weight: 900; color: #34d399;">⚔️ SÀN TÁC CHIẾN ĐA PHÒNG BAN &amp; ĐỒNG BỘ BÁO CÁO THỜI GIAN THỰC (V8.0)</div>
                    <div style="font-size: 11px; color: #94a3b8; margin-top: 2px;">Mọi chỉ thị, giám sát của Victor và kế hoạch tác chiến đều xuất phát 100% từ dữ liệu phiên thực và tự đồng bộ vào Kho Lưu Trữ (Vault).</div>
                    <div id="wr-publish-status-msg" style="font-size: 11px; color: #7dd3fc; margin-top: 4px;"></div>
                </div>
                <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 8px;">
                    <span id="wr-vault-sync-badge" style="font-size: 10.5px; background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.45); color: #34d399; padding: 5px 10px; border-radius: 7px; font-weight: 800;">{_h.escape(sync_badge)}</span>
                    <button id="btn-publish-war-room-report" onclick="publishWarRoomReportNow()" style="cursor: pointer; background: linear-gradient(90deg, #059669, #10b981); color: #fff; border: none; border-radius: 8px; padding: 7px 14px; font-size: 11.5px; font-weight: 800;">⚡ Phát Hành &amp; Đồng Bộ Báo Cáo Tác Chiến Mới Nhất</button>
                    {open_latest_btn}
                </div>
            </div>

            <div id="victor-deep-surveillance-panel" style="background: rgba(15, 23, 42, 0.94); border: 1px solid rgba(251, 191, 36, 0.35); border-radius: 12px; padding: 14px;">
                <div style="display: flex; justify-content: space-between; flex-wrap: wrap; gap: 8px; margin-bottom: 8px;">
                    <div style="font-size: 13px; font-weight: 900; color: #fbbf24;">🛡️ VICTOR (BAN 9 SENTINEL) GIÁM SÁT SÂU DANH MỤC &amp; TẦM NGẮM TIỀM NĂNG</div>
                    <div id="victor-surveillance-headline" style="font-size: 11.5px; color: #cbd5e1; font-weight: 700;">{_h.escape(str(v_surv.get('victor_headline', '')))}</div>
                </div>
                <div style="font-size: 11px; font-weight: 800; color: #38bdf8; margin-bottom: 6px;">TẦNG 1: VỊ THẾ ĐANG NẮM GIỮ &amp; LỆNH T+0 / PHÒNG HỘ STOP 2xATR</div>
                <div style="overflow-x: auto; margin-bottom: 12px;">
                    <table class="standard-table" style="width:100%; font-size:11.5px;">
                        <thead><tr><th>Mã</th><th>Thị Giá Live</th><th>Giá Vốn / P&amp;L</th><th>Áp Lực Sổ Lệnh</th><th>Stop 2xATR</th><th>TP1 / TP2</th><th>Vùng T+0 &amp; MOS</th><th>Chỉ Thị Victor</th></tr></thead>
                        <tbody id="victor-held-surveillance-tbody">{held_rows}</tbody>
                    </table>
                </div>
                <div style="font-size: 11px; font-weight: 800; color: #34d399; margin-bottom: 6px;">TẦNG 2: DANH MỤC TẦM NGẮM ALPHA TIỀM NĂNG &amp; CHECK LÔ 100 (&lt;= 33% NAV)</div>
                <div style="overflow-x: auto;">
                    <table class="standard-table" style="width:100%; font-size:11.5px;">
                        <thead><tr><th>Mã / Ngành</th><th>Thị Giá / Canh Mua</th><th>Sức Cầu &amp; RSI</th><th>OCF &amp; MOS</th><th>Alpha &amp; R:R</th><th>Vốn Lô 100 (% NAV)</th><th>Tín Hiệu Victor &amp; Catalyst</th></tr></thead>
                        <tbody id="victor-alpha-watchlist-tbody">{watch_rows}</tbody>
                    </table>
                </div>
            </div>

            <div id="wr-live-execution-master-plan-panel" style="background: rgba(15, 23, 42, 0.94); border: 1px solid rgba(56, 189, 248, 0.35); border-radius: 12px; padding: 14px;">
                <div style="font-size: 13px; font-weight: 900; color: #38bdf8; margin-bottom: 8px;">📜 KẾ HOẠCH TRIỂN KHAI TÁC CHIẾN ĐẦU TƯ THEO PHIÊN THỊ TRƯỜNG THỰC TẾ</div>
                <div id="wr-master-plan-summary-banner" style="background:rgba(30,41,59,0.72); border:1px solid rgba(56,189,248,0.28); border-radius:8px; padding:10px; font-size:11.5px; color:#e2e8f0; margin-bottom:10px;">
                    <strong style="color:#38bdf8;">{_h.escape(str(plan.get('plan_id', '')))}</strong> • Pha: <strong>{_h.escape(str(plan.get('session_phase_label', '')))}</strong> • VN-Index: <strong>{float(plan.get('vn_index_value', 0) or 0):,.2f}</strong> • Tiền mặt: <strong>{float(plan.get('cash_available_vnd', 0) or 0):,.0f}đ ({float(plan.get('cash_pct', 0) or 0):.1f}%)</strong> • Trần giải ngân mới: <strong>{float(plan.get('max_new_allocation_pct', 0) or 0):.0f}% NAV (~{float(plan.get('max_deployable_vnd', 0) or 0):,.0f}đ)</strong>
                    <div style="margin-top:5px;">📜 {_h.escape(str(plan.get('enterprise_action_summary') or plan.get('enterprise_verdict') or ''))}</div>
                </div>
                <div id="wr-master-plan-holdings-cards" style="display:grid; grid-template-columns:repeat(auto-fit, minmax(260px, 1fr)); gap:10px; margin-bottom:10px;">{hold_plan_cards}</div>
                <div style="overflow-x:auto; margin-bottom:10px;">
                    <table class="standard-table" style="width:100%; font-size:11.5px;">
                        <thead><tr><th>Mã</th><th>Loại Lệnh</th><th>Vùng Giải Ngân</th><th>Stop / TP1</th><th>Vốn Dự Kiến (% NAV)</th><th>Điều Kiện Kích Hoạt</th></tr></thead>
                        <tbody id="wr-master-plan-orders-tbody">{deploy_rows}</tbody>
                    </table>
                </div>
                <div id="wr-master-plan-scenarios-grid" style="display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:10px;">{scen_cards}</div>
            </div>

            <div id="wr-dept-workstation-panel" style="background: rgba(15, 23, 42, 0.94); border: 1px solid rgba(168, 85, 247, 0.35); border-radius: 12px; padding: 14px;">
                <div style="font-size: 13px; font-weight: 900; color: #c084fc; margin-bottom: 8px;">🏢 BÀN TÁC CHIẾN TRỰC TIẾP 14 PHÒNG BAN &amp; CHUYÊN VIÊN (ACTIVE IN WAR-ROOM)</div>
                <div id="wr-dept-workstation-grid" style="display:grid; grid-template-columns:repeat(auto-fit, minmax(260px, 1fr)); gap:9px;">{dept_cards}</div>
            </div>

            <div id="wr-live-reports-stream" style="background: rgba(15, 23, 42, 0.94); border: 1px solid rgba(52, 211, 153, 0.35); border-radius: 12px; padding: 14px;">
                <div style="font-size: 13px; font-weight: 900; color: #34d399; margin-bottom: 8px;">📰 LUỒNG BÁO CÁO MỚI NHẤT ĐỒNG BỘ TỪ HỆ THỐNG (1-CLICK ĐỌC CHI TIẾT)</div>
                <div id="wr-live-reports-feed-list" style="display:flex; flex-direction:column; gap:6px; max-height:320px; overflow-y:auto;">{feed_rows}</div>
            </div>
        </div>
    """


def generate_portal_html(
    supervisor_data: Dict[str, Any],
    initial_reports: List[Dict[str, Any]],
    milestones: List[Dict[str, Any]],
    available_dates: Optional[List[Dict[str, Any]]] = None
) -> str:
    import html as _html
    try:
        from scripts.apex_tactical_war_room_engine import get_tactical_war_room_state
        wr_state = get_tactical_war_room_state()
    except Exception:
        ssot_fb = _load_live_ssot_summary()
        wr_state = {
            "server_time": get_ict_now().strftime("%H:%M:%S"),
            "phase_info": {"active_phase_id": "POST_MARKET_WALL_STREET", "phase_name": "PHÒNG TÁC CHIẾN LIVE", "countdown_to_wall_street": "--:--"},
            "intraday_regime": {"regime_id": "SIDEWAY_CHOPPY", "label": "ĐANG ĐỒNG BỘ", "badge_color": "#fbbf24", "max_new_allocation_pct": 30},
            "action_plan": {"current_step": {"title": "Đang đồng bộ Living War-Room V8.0", "time_range": "--:--", "what_to_do": "Đang tải dữ liệu live...", "constitution_rule": "SSOT Live"}},
            "market_overview": {
                "vn_index": {"value": 0, "change_pts": 0, "change_pct": 0, "status": "ĐANG ĐỒNG BỘ", "turnover_ty_vnd": "--", "foreign_net_ty_vnd": "--"},
                "vn30_index": {"value": 0, "change_pts": 0, "change_pct": 0, "basis_vn30f": "--"},
                "market_breadth": {"advancers": 0, "decliners": 0},
            },
            "live_stocks": [],
            "dynamic_picks": [],
            "directives_history": [],
            "victor_sentinel": {
                "cash_vnd": ssot_fb["cash_vnd"], "stocks_val_vnd": ssot_fb["stocks_val_vnd"], "total_nav_vnd": ssot_fb["total_nav_vnd"],
                "cash_pct": ssot_fb["cash_pct"], "stocks_pct": ssot_fb["stocks_pct"], "total_shares": ssot_fb["total_shares"],
                "unrealized_pnl_vnd": ssot_fb["unrealized_pnl_vnd"], "unrealized_pnl_pct": ssot_fb["unrealized_pct"],
                "realized_round1_profit_vnd": ssot_fb["realized_pnl_vnd"], "holdings": [], "threat_level_num": 1, "threat_label": "Đang đồng bộ SSOT...",
            },
            "victor_deep_surveillance": {"held_positions_book": [], "alpha_watchlist_book": [], "victor_headline": "Đang đồng bộ..."},
            "live_execution_master_plan": {"holdings_action_items": [], "new_deployment_orders": [], "contingency_scenarios": []},
            "department_live_workstation": [],
            "latest_reports_feed": [],
            "vault_sync_meta": {"total_reports_scanned": 0, "today_reports_count": 0, "latest_report_rel_path": "", "latest_sync_time": ""},
            "tactical_message": f"Đang đồng bộ tiền mặt SSOT {ssot_fb['cash_str']}..."
        }

    wr_phase_id = wr_state['phase_info']['active_phase_id']
    wr_server_time = wr_state['server_time']
    wr_ny_countdown = wr_state['phase_info']['countdown_to_wall_street']
    wr_message = wr_state['tactical_message']

    ssot = _load_live_ssot_summary()
    wr_weekly_ui = _render_war_room_weekly_html(wr_state)
    wr_picks_html = _render_war_room_picks_html(wr_state)
    wr_directives_html = _render_war_room_directives_html(wr_state)
    wr_holdings_html = _render_war_room_holdings_html(wr_state)
    wr_stocks_rows_html = _render_war_room_stocks_rows_html(wr_state)
    wr_threat_html = _render_war_room_threat_html(wr_state)
    wr_mkt_ui = _format_market_overview_ui(wr_state)
    wr_stages_html = generate_dynamic_tactical_stages_html(wr_state=wr_state)
    wr_stocks_count = len(wr_state.get("live_stocks") or [])
    wr_spillover_html = _render_war_room_spillover_slippage_html(wr_state)
    wr_portfolio_live_html = _render_portfolio_tab_live_sections_html(wr_state, ssot)
    wr_tab4_watchlist_html = _render_tab4_live_watchlist_html(wr_state)
    wr_v8_floor_html = _render_war_room_v8_command_floor_html(wr_state)
    wr_phase_label_safe = _html.escape(str((wr_state.get("phase_info", {}) or {}).get("phase_name") or wr_phase_id or "PHÒNG TÁC CHIẾN LIVE"))
    wr_regime_label_safe = _html.escape(str((wr_state.get("intraday_regime", {}) or {}).get("label") or "TÍCH LŨY CHỌN LỌC"))

    auth_logout_btn_html = ""
    try:
        from scripts.apex_portal_auth import is_auth_enabled
        if is_auth_enabled():
            auth_logout_btn_html = (
                '<button onclick="logoutPortal()" class="btn-read" '
                'style="display: flex; align-items: center; gap: 6px; padding: 8px 14px; '
                'background: rgba(239, 68, 68, 0.16); border: 1px solid rgba(239, 68, 68, 0.4); color: #fca5a5;">'
                '<span>🔒</span> <span>Khóa Phiên</span></button>'
            )
    except Exception:
        pass

    sup_status = supervisor_data.get("supervisor_status", "HEALTHY_ALL_RUNNING")
    services = supervisor_data.get("services", {})
    ssot = _load_live_ssot_summary()
    total_reports_count = len(initial_reports)
    try:
        from scripts.apex_database_engine import ApexDatabaseEngine
        db_stats = ApexDatabaseEngine.get_database_stats()
        total_vault_count = max(total_reports_count, int(db_stats.get("total_institutional_reports", 0)))
    except Exception:
        total_vault_count = total_reports_count

    today_str = get_ict_now().strftime("%Y-%m-%d")
    today_reports_count = sum(1 for r in initial_reports if r.get("date") == today_str)
    latest_avail_date = available_dates[0]["date"] if available_dates else (initial_reports[0].get("date", today_str) if initial_reports else today_str)
    initial_date_filter = "today" if today_reports_count > 0 else (latest_avail_date if total_reports_count > 0 else "all")
    unrealized_color = "#34d399" if ssot["unrealized_pnl_vnd"] >= 0 else "#f87171"

    # Render bảng tiến trình daemons
    services_rows = ""
    for k, sinfo in services.items():
        st = sinfo.get("status", "UNKNOWN")
        badge_color = "#10b981" if st == "RUNNING" else ("#ef4444" if st == "STOPPED" else "#f59e0b")
        services_rows += f"""
        <tr>
            <td style="padding: 12px 16px; font-weight: 600; color: #f8fafc;">{sinfo.get('name', k)}</td>
            <td style="padding: 12px 16px; font-family: 'JetBrains Mono', monospace; color: #38bdf8;">{sinfo.get('pid', '-')}</td>
            <td style="padding: 12px 16px;">
                <span style="background: {badge_color}22; color: {badge_color}; border: 1px solid {badge_color}55; padding: 4px 10px; border-radius: 9999px; font-size: 11px; font-weight: 700;">
                    ● {st}
                </span>
            </td>
            <td style="padding: 12px 16px; color: #94a3b8; font-family: 'JetBrains Mono', monospace;">{sinfo.get('restart_count', 0)}</td>
            <td style="padding: 12px 16px; color: #94a3b8; font-family: 'JetBrains Mono', monospace;">{sinfo.get('uptime_seconds', 0):.0f}s</td>
        </tr>
        """

    # Render danh sách 18 cột mốc
    milestone_rows = ""
    for m in milestones:
        st_color = m.get("color", "#38bdf8")
        milestone_rows += f"""
        <tr>
            <td style="padding: 12px 16px; font-family: 'JetBrains Mono', monospace; font-weight: 700; color: #38bdf8; font-size: 13px;">{m['time']}</td>
            <td style="padding: 12px 16px; font-size: 18px; text-align: center;">{m['icon']}</td>
            <td style="padding: 12px 16px; font-weight: 600; color: #f1f5f9;">{m['name']}</td>
            <td style="padding: 12px 16px; font-size: 12px; color: #94a3b8;">{m.get('shift', '')}</td>
            <td style="padding: 12px 16px;">
                <span style="background: {st_color}22; color: {st_color}; border: 1px solid {st_color}55; padding: 4px 10px; border-radius: 9999px; font-size: 11px; font-weight: 700;">
                    ● {m['status_label']}
                </span>
            </td>
        </tr>
        """

    if not available_dates:
        available_dates = [{"date": today_str, "display": f"🌟 Hôm Nay ({today_str})", "count": today_reports_count, "is_today": True}]

    # Dropdown options
    date_options_html = ""
    for d in available_dates:
        selected = "selected" if d["is_today"] else ""
        date_options_html += f'<option value="{d["date"]}" {selected}>{d["display"]}</option>'

    # Serialized JSON dữ liệu ban đầu cho JavaScript clientside
    initial_reports_json = json.dumps(initial_reports, ensure_ascii=False)
    available_dates_json = json.dumps(available_dates, ensure_ascii=False)

    db_milestone_banner = ""
    sqlite_db_file = BASE_DIR / "data" / "apex_institutional_vault.db"
    if sqlite_db_file.exists():
        db_milestone_banner = f'''
        <div style="background: linear-gradient(135deg, #064e3b 0%, #022c22 100%); border: 1px solid #10b981; border-radius: 14px; padding: 14px 22px; margin-bottom: 22px; display: flex; align-items: center; justify-content: space-between; gap: 14px; box-shadow: 0 4px 20px rgba(16, 185, 129, 0.25);">
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 26px;">⚡</span>
                <div>
                    <strong style="color: #34d399; font-size: 14.5px;">HẠ TẦNG V5.0: ĐÃ NÂNG CẤP LÊN SQLITE LAKEHOUSE VAULT (SỨC CHỨA 100.000 BÁO CÁO)</strong>
                    <div style="font-size: 12.5px; color: #a7f3d0; margin-top: 3px;">Truy vấn chỉ mục B-Tree &lt; 2ms | Kích hoạt FTS5 Search toàn văn | Bảo tồn 100% tài liệu tiền thật theo lệnh Chủ tịch Phước Trần!</div>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid #10b981; border-radius: 9999px; padding: 6px 14px; font-size: 12px; font-weight: 700;">
                    🟢 SQLITE VAULT ACTIVE
                </span>
            </div>
        </div>
        '''
    elif total_reports_count >= 300:
        db_milestone_banner = f'''
        <div style="background: linear-gradient(135deg, #78350f 0%, #451a03 100%); border: 1px solid #f59e0b; border-radius: 14px; padding: 14px 22px; margin-bottom: 22px; display: flex; align-items: center; justify-content: space-between; gap: 14px; box-shadow: 0 4px 20px rgba(245, 158, 11, 0.25);">
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 26px;">⚠️</span>
                <div>
                    <strong style="color: #fbbf24; font-size: 14.5px;">CẢNH BÁO THỂ CHẾ: KHO DỮ LIỆU ĐÃ ĐẠT {total_reports_count} BÁO CÁO (NGƯỠNG 300 - 500)</strong>
                    <div style="font-size: 12.5px; color: #fde68a; margin-top: 3px;">Hệ thống đang tự động kích hoạt Kế hoạch Nâng cấp Cơ sở dữ liệu V5.0 (SQLite / PostgreSQL) theo đúng Chỉ thị của Chủ tịch Phước Trần!</div>
                </div>
            </div>
            <button onclick="switchTab(\'james-command\'); sendQuickCommand(\'Đệ trình kế hoạch nâng cấp Database V5.0\')" class="btn-read" style="background: #f59e0b; color: #070a12; font-weight: 800; white-space: nowrap; padding: 8px 18px;">
                ⚡ Xem Đệ Trình
            </button>
        </div>
        '''

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Apex Institutional Cloud Portal — Định Chế Quỹ Đầu Tư 24/7</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
    <style>
        :root {{
            --bg-base: #070a12;
            --bg-surface: #0e1524;
            --bg-card: #141d30;
            --bg-card-hover: #1c2740;
            --border-color: #23304a;
            --border-glow: rgba(56, 189, 248, 0.35);
            --primary: #38bdf8;
            --primary-glow: rgba(56, 189, 248, 0.15);
            --success: #10b981;
            --success-glow: rgba(16, 185, 129, 0.15);
            --warning: #fbbf24;
            --danger: #ef4444;
            --purple: #c084fc;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --text-dim: #64748b;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: var(--bg-base);
            color: var(--text-main);
            min-height: 100vh;
            padding: 20px 24px;
            background-image: 
                radial-gradient(circle at 15% 15%, rgba(56, 189, 248, 0.03) 0%, transparent 40%),
                radial-gradient(circle at 85% 85%, rgba(192, 132, 252, 0.03) 0%, transparent 40%);
            background-attachment: fixed;
        }}
        .container {{ max-width: 1420px; margin: 0 auto; }}
        
        /* HEADER */
        .portal-header {{
            background: linear-gradient(135deg, #0e1524 0%, #141d30 100%);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 22px 28px;
            margin-bottom: 22px;
            box-shadow: 0 12px 32px -8px rgba(0, 0, 0, 0.6);
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            gap: 18px;
        }}
        .brand-title {{
            display: flex;
            align-items: center;
            gap: 14px;
            font-size: 22px;
            font-weight: 800;
            color: #ffffff;
            letter-spacing: -0.02em;
        }}
        .brand-sub {{
            font-size: 13px;
            color: var(--text-muted);
            margin-top: 6px;
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            align-items: center;
        }}
        .header-meta {{
            display: flex;
            align-items: center;
            gap: 12px;
            flex-wrap: wrap;
        }}
        .live-badge {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(16, 185, 129, 0.12);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.35);
            padding: 7px 16px;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.04em;
        }}
        .pulse-dot {{
            width: 8px; height: 8px; border-radius: 50%; background: #10b981;
            box-shadow: 0 0 10px #10b981;
            animation: pulse 1.8s infinite;
        }}
        @keyframes pulse {{
            0% {{ transform: scale(0.95); opacity: 0.8; }}
            50% {{ transform: scale(1.3); opacity: 1; }}
            100% {{ transform: scale(0.95); opacity: 0.8; }}
        }}

        /* KPI STATS ROW */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 16px;
            margin-bottom: 22px;
        }}
        .kpi-card {{
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 20px 22px;
            position: relative;
            overflow: hidden;
            transition: transform 0.2s, border-color 0.2s, box-shadow 0.2s;
        }}
        .kpi-card:hover {{
            transform: translateY(-2px);
            border-color: var(--primary);
            box-shadow: 0 8px 24px rgba(56, 189, 248, 0.1);
        }}
        .kpi-card::before {{
            content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
            background: linear-gradient(90deg, var(--card-accent, #38bdf8), #818cf8);
        }}
        .kpi-lbl {{
            font-size: 11px;
            text-transform: uppercase;
            color: var(--text-dim);
            font-weight: 800;
            letter-spacing: 0.08em;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .kpi-val {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 24px;
            font-weight: 800;
            margin-top: 8px;
            letter-spacing: -0.02em;
        }}
        .kpi-sub {{
            font-size: 12px;
            color: var(--text-muted);
            margin-top: 5px;
            display: flex;
            align-items: center;
            gap: 4px;
        }}

        /* TABS NAVIGATION */
        .tab-nav {{
            display: flex;
            gap: 8px;
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 22px;
            overflow-x: auto;
            padding-bottom: 10px;
            scrollbar-width: thin;
        }}
        .tab-btn {{
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            color: var(--text-muted);
            padding: 11px 20px;
            font-size: 13.5px;
            font-weight: 700;
            border-radius: 10px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 9px;
            white-space: nowrap;
            transition: all 0.2s;
        }}
        .tab-btn:hover {{
            background: var(--bg-card);
            color: var(--text-main);
            border-color: #3b82f6;
        }}
        .tab-btn.active {{
            background: linear-gradient(135deg, #1e293b 0%, #1e1b4b 100%);
            color: #38bdf8;
            border-color: #38bdf8;
            box-shadow: 0 4px 16px rgba(56, 189, 248, 0.2);
        }}
        .tab-badge {{
            background: rgba(56, 189, 248, 0.15);
            color: #38bdf8;
            padding: 2px 7px;
            border-radius: 9999px;
            font-size: 11px;
            font-weight: 700;
        }}

        .tab-pane {{ display: none; }}
        .tab-pane.active {{ display: block; }}

        /* ========================================================
           TAB 1: THƯ VIỆN BÁO CÁO (PHÂN LOẠI 2 TẦNG CHUYÊN NGHIỆP)
           ======================================================== */
        .library-controller {{
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 20px 24px;
            margin-bottom: 22px;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}

        /* TẦNG 1: THỜI GIAN & CA TÁC CHIẾN */
        .filter-row-header {{
            font-size: 11px;
            font-weight: 800;
            text-transform: uppercase;
            color: var(--text-dim);
            letter-spacing: 0.08em;
            display: flex;
            align-items: center;
            gap: 6px;
            margin-bottom: 8px;
        }}
        .time-filter-section {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 14px;
            padding-bottom: 14px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        }}
        .date-pills {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            align-items: center;
        }}
        .date-pill-btn {{
            background: var(--bg-base);
            border: 1px solid var(--border-color);
            color: var(--text-muted);
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 12.5px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.15s;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .date-pill-btn:hover {{ color: #fff; border-color: var(--primary); }}
        .date-pill-btn.active {{
            background: var(--primary);
            color: #070a12;
            border-color: var(--primary);
            box-shadow: 0 2px 10px rgba(56, 189, 248, 0.35);
        }}
        .archive-select {{
            background: var(--bg-base);
            border: 1px solid var(--border-color);
            color: #fff;
            padding: 8px 14px;
            border-radius: 8px;
            font-size: 12.5px;
            outline: none;
            cursor: pointer;
        }}

        /* 4 CA TÁC CHIẾN */
        .shifts-group {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            align-items: center;
        }}
        .shift-pill {{
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--border-color);
            color: var(--text-muted);
            padding: 6px 14px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.15s;
        }}
        .shift-pill:hover {{ background: var(--bg-card); color: #fff; }}
        .shift-pill.active {{
            background: rgba(56, 189, 248, 0.15);
            color: var(--primary);
            border-color: rgba(56, 189, 248, 0.4);
            font-weight: 700;
        }}

        /* TẦNG 2: 5 KHỐI PHÂN LOẠI THỂ CHẾ */
        .category-filter-section {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            align-items: center;
        }}
        .cat-btn {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            color: var(--text-muted);
            padding: 8px 16px;
            border-radius: 9999px;
            font-size: 12.5px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.15s;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .cat-btn:hover {{
            background: var(--bg-card-hover);
            color: #fff;
            border-color: #3b82f6;
        }}
        .cat-btn.active {{
            background: linear-gradient(135deg, #1e293b 0%, #1e1b4b 100%);
            color: var(--primary);
            font-weight: 800;
            border-color: var(--primary);
            box-shadow: 0 2px 10px rgba(56, 189, 248, 0.2);
        }}
        .cat-count {{
            background: rgba(255, 255, 255, 0.08);
            padding: 1px 7px;
            border-radius: 9999px;
            font-size: 11px;
            font-family: 'JetBrains Mono', monospace;
        }}
        .cat-btn.active .cat-count {{
            background: rgba(56, 189, 248, 0.25);
            color: #38bdf8;
            font-weight: 700;
        }}

        /* TẦNG 3: TOOLBAR TÌM KIẾM & CHẾ ĐỘ XEM */
        .library-toolbar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 14px;
            padding-top: 12px;
            border-top: 1px solid rgba(255, 255, 255, 0.06);
        }}
        .search-box-wrap {{
            position: relative;
            flex-grow: 1;
            max-width: 480px;
        }}
        .search-box {{
            width: 100%;
            background: var(--bg-base);
            border: 1px solid var(--border-color);
            color: #fff;
            padding: 10px 16px 10px 40px;
            border-radius: 10px;
            font-size: 13.5px;
            outline: none;
            transition: border-color 0.2s;
        }}
        .search-box:focus {{ border-color: var(--primary); }}
        .search-icon {{
            position: absolute; left: 14px; top: 50%; transform: translateY(-50%);
            color: var(--text-dim); font-size: 15px;
        }}
        .view-mode-toggle {{
            display: flex;
            gap: 6px;
            background: var(--bg-base);
            padding: 4px;
            border-radius: 8px;
            border: 1px solid var(--border-color);
        }}
        .view-btn {{
            background: transparent;
            border: none;
            color: var(--text-muted);
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.15s;
        }}
        .view-btn.active {{
            background: var(--bg-card);
            color: var(--primary);
            box-shadow: 0 1px 4px rgba(0,0,0,0.3);
        }}

        /* GRID VIEW: CARDS */
        .reports-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 20px;
        }}
        .report-card {{
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 22px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: transform 0.2s, border-color 0.2s, box-shadow 0.2s;
            cursor: pointer;
            position: relative;
        }}
        .report-card:hover {{
            transform: translateY(-3px);
            border-color: var(--primary);
            box-shadow: 0 10px 28px rgba(56, 189, 248, 0.12);
        }}
        .card-top {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 12px;
            gap: 10px;
        }}
        .dept-tag {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 11px;
            font-weight: 800;
            padding: 4px 11px;
            border-radius: 9999px;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}
        .report-time-badge {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            background: var(--bg-base);
            border: 1px solid var(--border-color);
            padding: 4px 10px;
            border-radius: 6px;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            color: #cbd5e1;
            white-space: nowrap;
        }}
        .report-title {{
            font-size: 16px;
            font-weight: 700;
            color: #ffffff;
            line-height: 1.45;
            margin-bottom: 12px;
        }}
        .report-snippet {{
            font-size: 13px;
            color: #94a3b8;
            line-height: 1.6;
            margin-bottom: 18px;
            background: rgba(255, 255, 255, 0.02);
            border-left: 3px solid #38bdf8;
            padding: 10px 14px;
            border-radius: 0 8px 8px 0;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}
        .card-bottom {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: 14px;
            border-top: 1px solid rgba(255, 255, 255, 0.06);
        }}
        .btn-read {{
            background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%);
            color: #ffffff;
            border: none;
            padding: 7px 16px;
            border-radius: 8px;
            font-size: 12.5px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s;
            box-shadow: 0 2px 8px rgba(37, 99, 235, 0.3);
        }}
        .btn-read:hover {{
            background: linear-gradient(135deg, #0ea5e9 0%, #3b82f6 100%);
            box-shadow: 0 4px 14px rgba(56, 189, 248, 0.4);
            transform: translateY(-1px);
        }}

        /* TABLE VIEW: COMPACT LIST */
        .reports-table-wrap {{
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            overflow: hidden;
        }}
        .reports-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13.5px;
        }}
        .reports-table th {{
            background: var(--bg-card);
            padding: 12px 16px;
            color: var(--text-dim);
            font-weight: 800;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }}
        .reports-table td {{
            padding: 12px 16px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.04);
            color: #cbd5e1;
        }}
        .reports-table tr:hover td {{
            background: rgba(56, 189, 248, 0.04);
        }}

        /* ========================================================
           TAB 3: BÀN CHỈ HUY MASTER CIO JAMES (SPLIT-VIEW 2 CỘT)
           ======================================================== */
        .james-split-container {{
            display: grid;
            grid-template-columns: 1fr 360px;
            gap: 20px;
            align-items: start;
        }}
        @media (max-width: 1100px) {{
            .james-split-container {{ grid-template-columns: 1fr; }}
        }}
        .james-main-panel {{
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            min-height: 680px;
        }}
        .james-sidebar-panel {{
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}
        .sidebar-widget {{
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 18px 20px;
            position: relative;
            overflow: hidden;
        }}
        .sidebar-widget::before {{
            content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
            background: linear-gradient(90deg, #c084fc, #38bdf8);
        }}
        .sidebar-widget-title {{
            font-size: 12px;
            font-weight: 800;
            text-transform: uppercase;
            color: var(--text-dim);
            letter-spacing: 0.06em;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        /* JAMES COMMAND CHIPS */
        .cmd-chip {{
            background: var(--bg-base);
            border: 1px solid var(--border-color);
            color: var(--text-muted);
            padding: 6px 13px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.15s;
        }}
        .cmd-chip:hover {{
            background: var(--primary);
            color: #070a12;
            font-weight: 800;
            border-color: var(--primary);
            box-shadow: 0 2px 8px rgba(56, 189, 248, 0.3);
        }}

        /* CHAT BUBBLES */
        .msg-user {{
            align-self: flex-end;
            background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%);
            color: #ffffff;
            padding: 14px 18px;
            border-radius: 14px 14px 2px 14px;
            max-width: 820px;
            box-shadow: 0 4px 14px rgba(37, 99, 235, 0.25);
        }}
        .msg-james {{
            align-self: flex-start;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            color: #e2e8f0;
            padding: 20px 22px;
            border-radius: 14px 14px 14px 2px;
            max-width: 900px;
            width: 100%;
            box-shadow: 0 4px 18px rgba(0, 0, 0, 0.3);
        }}
        .msg-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        }}

        /* SMART VISUAL WIDGETS FOR JAMES MESSAGES */
        .exec-kpi-banner {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 12px;
            margin: 14px 0 18px;
        }}
        .exec-kpi-box {{
            background: var(--bg-base);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 12px 14px;
        }}
        .exec-kpi-box-lbl {{ font-size: 10.5px; text-transform: uppercase; color: var(--text-dim); font-weight: 800; }}
        .exec-kpi-box-val {{ font-family: 'JetBrains Mono', monospace; font-size: 16px; font-weight: 800; margin-top: 4px; }}

        .stock-target-card {{
            background: var(--bg-base);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 14px 16px;
            margin-bottom: 12px;
            transition: border-color 0.15s;
        }}
        .stock-target-card:hover {{ border-color: #38bdf8; }}
        .stock-target-top {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }}
        .stock-target-badge {{
            font-size: 13px;
            font-weight: 800;
            color: #38bdf8;
            font-family: 'JetBrains Mono', monospace;
            background: rgba(56, 189, 248, 0.12);
            padding: 2px 8px;
            border-radius: 6px;
        }}
        .price-badge-buy {{
            background: rgba(56, 189, 248, 0.1);
            color: #38bdf8;
            border: 1px solid rgba(56, 189, 248, 0.3);
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
        }}
        .price-badge-breakout {{
            background: rgba(16, 185, 129, 0.1);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.3);
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
        }}

        details.round1-accordion {{
            background: var(--bg-base);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 12px 16px;
            margin: 14px 0;
            cursor: pointer;
        }}
        details.round1-accordion summary {{
            font-size: 12.5px;
            font-weight: 700;
            color: #34d399;
            outline: none;
        }}
        details.round1-accordion .round1-body {{
            margin-top: 12px;
            padding-top: 10px;
            border-top: 1px solid rgba(255, 255, 255, 0.06);
            font-size: 13px;
            color: #94a3b8;
            line-height: 1.6;
        }}

        /* INTERACTIVE CHAT REPORT CARD (CLICK TO OPEN REPORT MODAL) */
        .chat-open-report-card {{
            display: flex;
            align-items: center;
            gap: 14px;
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.85));
            border: 1.5px solid rgba(56, 189, 248, 0.4);
            box-shadow: 0 4px 20px rgba(56, 189, 248, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 14px 18px;
            margin: 14px 0;
            cursor: pointer;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }}
        .chat-open-report-card:hover {{
            border-color: #38bdf8;
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.98), rgba(15, 23, 42, 0.9));
            box-shadow: 0 8px 30px rgba(56, 189, 248, 0.35), 0 0 15px rgba(56, 189, 248, 0.2);
            transform: translateY(-2px);
        }}
        .chat-open-report-icon-box {{
            width: 44px;
            height: 44px;
            border-radius: 10px;
            background: rgba(56, 189, 248, 0.15);
            border: 1px solid rgba(56, 189, 248, 0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
            flex-shrink: 0;
        }}
        .chat-open-report-body {{
            flex: 1;
            min-width: 0;
        }}
        .chat-open-report-label {{
            font-size: 10.5px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            color: #38bdf8;
            margin-bottom: 2px;
        }}
        .chat-open-report-name {{
            font-size: 13.5px;
            font-weight: 700;
            color: #ffffff;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .chat-open-report-path {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            color: #94a3b8;
            margin-top: 2px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .chat-open-report-btn {{
            display: flex;
            align-items: center;
            gap: 8px;
            background: linear-gradient(135deg, #0284c7, #0369a1);
            color: #ffffff;
            border: 1px solid #38bdf8;
            padding: 9px 16px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 700;
            cursor: pointer;
            white-space: nowrap;
            box-shadow: 0 2px 10px rgba(2, 132, 199, 0.4);
            transition: all 0.2s;
            flex-shrink: 0;
        }}
        .chat-open-report-btn:hover {{
            background: linear-gradient(135deg, #0ea5e9, #0284c7);
            box-shadow: 0 4px 16px rgba(14, 165, 233, 0.6);
            transform: scale(1.02);
        }}

        /* TRADINGVIEW STYLES */
        .tv-btn {{
            background: var(--bg-base);
            border: 1px solid var(--border-color);
            color: var(--text-muted);
            padding: 6px 14px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.15s;
        }}
        .tv-btn:hover {{ color: #fff; border-color: var(--primary); }}
        .tv-btn.active {{
            background: var(--primary);
            color: #070a12;
            border-color: var(--primary);
            box-shadow: 0 2px 8px rgba(56, 189, 248, 0.35);
        }}

        /* MODAL ĐỌC BÁO CÁO */
        .modal-overlay {{
            display: none;
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(3, 7, 18, 0.88);
            backdrop-filter: blur(8px);
            z-index: 9999;
            padding: 30px 20px;
            overflow-y: auto;
        }}
        .modal-container {{
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 18px;
            max-width: 960px;
            margin: 0 auto;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.85);
            overflow: hidden;
        }}
        .modal-header {{
            background: var(--bg-card);
            border-bottom: 1px solid var(--border-color);
            padding: 22px 28px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 10;
        }}
        .modal-body {{
            padding: 36px 42px;
            line-height: 1.8;
            font-size: 15.5px;
            color: #e2e8f0;
            max-height: 80vh;
            overflow-y: auto;
        }}

        /* MARKDOWN STYLING */
        .markdown-body h1, .markdown-body h2, .markdown-body h3 {{
            color: #ffffff;
            margin: 26px 0 14px;
            font-weight: 800;
            letter-spacing: -0.01em;
        }}
        .markdown-body h1 {{ font-size: 24px; border-bottom: 1px solid var(--border-color); padding-bottom: 10px; }}
        .markdown-body h2 {{ font-size: 19px; }}
        .markdown-body h3 {{ font-size: 16px; color: #38bdf8; }}
        .markdown-body p {{ margin-bottom: 16px; }}
        .markdown-body ul, .markdown-body ol {{ margin: 0 0 18px 24px; }}
        .markdown-body li {{ margin-bottom: 8px; }}
        .markdown-body table {{
            width: 100%;
            border-collapse: collapse;
            margin: 22px 0;
            font-size: 13.5px;
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid var(--border-color);
        }}
        .markdown-body th {{
            background: #172554;
            color: #38bdf8;
            padding: 12px 16px;
            text-align: left;
            font-weight: 800;
            border: 1px solid var(--border-color);
        }}
        .markdown-body td {{
            padding: 11px 16px;
            border: 1px solid var(--border-color);
        }}
        .markdown-body tr:nth-child(even) {{ background: rgba(255, 255, 255, 0.02); }}
        .markdown-body code {{
            font-family: 'JetBrains Mono', monospace;
            background: rgba(56, 189, 248, 0.1);
            color: #38bdf8;
            padding: 2px 7px;
            border-radius: 5px;
            font-size: 13px;
        }}

        /* TABLE BASE STYLES */
        table.standard-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13.5px;
        }}
        table.standard-table th {{
            background: var(--bg-base);
            padding: 12px 16px;
            color: var(--text-dim);
            font-weight: 800;
            text-transform: uppercase;
            font-size: 11px;
            letter-spacing: 0.06em;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }}
        table.standard-table td {{
            border-bottom: 1px solid var(--border-color);
        }}
        table.standard-table tr:hover td {{
            background: rgba(255, 255, 255, 0.02);
        }}

        @media print {{
            body * {{ visibility: hidden; }}
            #report-modal, #report-modal * {{ visibility: visible; }}
            #report-modal {{ position: absolute; left: 0; top: 0; width: 100%; background: #fff; color: #000; padding: 0; }}
            .modal-header {{ border-bottom: 2px solid #000; }}
            .modal-close, .modal-actions {{ display: none; }}
            .modal-container {{ box-shadow: none; border: none; width: 100%; max-width: 100%; margin: 0; }}
            .markdown-body {{ color: #000; }}
            .markdown-body th {{ background: #f1f5f9; color: #000; }}
            .markdown-body code {{ color: #000; background: #eee; }}
        }}

        /* ========================================================
           TAB 4: PHÒNG HỌP THƯỢNG ĐỈNH TRỰC TUYẾN (APEX WAR ROOM)
           ======================================================== */
        .summit-container {{
            display: flex;
            flex-direction: column;
            gap: 18px;
        }}
        .summit-header-card {{
            background: linear-gradient(135deg, #0b1329 0%, #171d36 50%, #1e1b4b 100%);
            border: 1px solid rgba(56, 189, 248, 0.35);
            border-radius: 16px;
            padding: 22px 28px;
            box-shadow: 0 16px 36px -10px rgba(0, 0, 0, 0.7);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 20px;
            position: relative;
            overflow: hidden;
        }}
        .summit-header-card::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; height: 3px;
            background: linear-gradient(90deg, #38bdf8, #818cf8, #ec4899);
        }}
        .summit-title-box {{
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}
        .summit-tag-row {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            align-items: center;
        }}
        .summit-tag {{
            font-size: 11px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            padding: 3px 10px;
            border-radius: 9999px;
            display: inline-flex;
            align-items: center;
            gap: 5px;
        }}
        .summit-tag-gold {{
            background: rgba(234, 179, 8, 0.15);
            color: #facc15;
            border: 1px solid rgba(234, 179, 8, 0.35);
        }}
        .summit-tag-blue {{
            background: rgba(56, 189, 248, 0.15);
            color: #38bdf8;
            border: 1px solid rgba(56, 189, 248, 0.35);
        }}
        .summit-tag-inspector {{
            background: rgba(245, 158, 11, 0.18);
            color: #fbbf24;
            border: 1px solid rgba(245, 158, 11, 0.45);
            font-weight: 800;
        }}
        .summit-title {{
            font-size: 20px;
            font-weight: 800;
            color: #ffffff;
            letter-spacing: -0.02em;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .summit-sub {{
            font-size: 12.5px;
            color: var(--text-muted);
            display: flex;
            gap: 14px;
            flex-wrap: wrap;
            align-items: center;
        }}
        .summit-timer-card {{
            background: rgba(15, 23, 42, 0.85);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 12px;
            padding: 14px 20px;
            text-align: center;
            min-width: 220px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.4);
        }}
        .summit-timer-label {{
            font-size: 11px;
            text-transform: uppercase;
            font-weight: 800;
            color: var(--text-dim);
            letter-spacing: 0.08em;
            margin-bottom: 4px;
        }}
        .summit-timer-val {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 24px;
            font-weight: 800;
            color: #38bdf8;
            letter-spacing: 0.04em;
        }}
        .summit-timer-sub {{
            font-size: 11px;
            color: var(--text-muted);
            margin-top: 3px;
        }}

        /* PHASES TIMELINE STEPPER */
        .summit-phases-card {{
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 18px 22px;
        }}
        .summit-phases-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 14px;
            font-size: 12px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: var(--text-dim);
        }}
        .summit-steps-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
            gap: 8px;
        }}
        .summit-step-item {{
            background: var(--bg-base);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 10px 12px;
            transition: all 0.2s;
            position: relative;
        }}
        .summit-step-item.active {{
            border-color: #38bdf8;
            background: rgba(56, 189, 248, 0.08);
            box-shadow: 0 0 12px rgba(56, 189, 248, 0.25);
        }}
        .summit-step-item.completed {{
            border-color: #10b981;
            background: rgba(16, 185, 129, 0.06);
        }}
        .summit-step-min {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 10.5px;
            font-weight: 700;
            color: var(--text-muted);
            margin-bottom: 3px;
        }}
        .summit-step-item.active .summit-step-min {{ color: #38bdf8; }}
        .summit-step-item.completed .summit-step-min {{ color: #34d399; }}
        .summit-step-lbl {{
            font-size: 11.5px;
            font-weight: 700;
            color: #f1f5f9;
            line-height: 1.3;
        }}

        /* SPLIT-VIEW WAR ROOM (70% - 30%) */
        .summit-war-split {{
            display: grid;
            grid-template-columns: 1fr 360px;
            gap: 18px;
            align-items: start;
        }}
        @media (max-width: 1080px) {{
            .summit-war-split {{ grid-template-columns: 1fr; }}
        }}

        /* CỘT TRÁI: LIVE DIALOGUE STREAM */
        .summit-feed-panel {{
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            min-height: 680px;
        }}
        .summit-feed-header {{
            background: linear-gradient(135deg, #131b2e 0%, #1e293b 100%);
            border-bottom: 1px solid var(--border-color);
            padding: 16px 22px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
        }}
        .summit-feed-body {{
            flex: 1;
            padding: 20px 22px;
            overflow-y: auto;
            max-height: 620px;
            display: flex;
            flex-direction: column;
            gap: 16px;
            background: #090e1a;
            scrollbar-width: thin;
        }}
        .summit-msg-card {{
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.07);
            border-radius: 12px;
            padding: 16px 18px;
            transition: all 0.2s;
            animation: fadeInMsg 0.3s ease;
        }}
        .summit-msg-card:hover {{
            background: rgba(255, 255, 255, 0.04);
            border-color: rgba(255, 255, 255, 0.15);
        }}
        .summit-msg-card.msg-chairman {{
            background: rgba(234, 179, 8, 0.06);
            border-color: rgba(234, 179, 8, 0.35);
            box-shadow: 0 4px 18px rgba(234, 179, 8, 0.1);
        }}
        .summit-msg-card.msg-inspector {{
            background: rgba(245, 158, 11, 0.06);
            border-color: rgba(245, 158, 11, 0.35);
        }}
        .summit-msg-card.msg-debate {{
            background: rgba(239, 68, 68, 0.06);
            border-color: rgba(239, 68, 68, 0.45);
            box-shadow: 0 0 15px rgba(239, 68, 68, 0.08);
        }}
        .summit-msg-card.msg-forensic {{
            background: rgba(236, 72, 153, 0.06);
            border-color: rgba(236, 72, 153, 0.35);
        }}
        .summit-msg-card.msg-quant {{
            background: rgba(16, 185, 129, 0.06);
            border-color: rgba(16, 185, 129, 0.35);
        }}
        .summit-msg-card.msg-tactical {{
            background: rgba(249, 115, 22, 0.06);
            border-color: rgba(249, 115, 22, 0.4);
            box-shadow: 0 2px 14px rgba(249, 115, 22, 0.12);
        }}
        @keyframes fadeInMsg {{
            from {{ opacity: 0; transform: translateY(8px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .summit-msg-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            flex-wrap: wrap;
            gap: 8px;
        }}
        .summit-msg-author {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .summit-msg-avatar {{
            font-size: 20px;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.06);
            display: flex;
            align-items: center;
            justify-content: center;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        .summit-msg-name {{
            font-weight: 800;
            color: #f8fafc;
            font-size: 13.5px;
        }}
        .summit-msg-dept {{
            font-size: 11px;
            color: var(--text-muted);
        }}
        .summit-msg-time {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            color: var(--text-dim);
        }}
        .summit-msg-content {{
            font-size: 13.5px;
            line-height: 1.6;
            color: #e2e8f0;
            white-space: pre-wrap;
        }}
        .summit-msg-highlight {{
            margin-top: 10px;
            padding: 8px 12px;
            background: rgba(56, 189, 248, 0.08);
            border-left: 3px solid #38bdf8;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
            color: #7dd3fc;
        }}

        /* LIVE EVIDENCE DATA CARDS (BƯỚC 2) */
        .summit-evidence-box {{
            margin-top: 12px;
            background: rgba(15, 23, 42, 0.85);
            border: 1px solid rgba(56, 189, 248, 0.3);
            border-radius: 8px;
            overflow: hidden;
            font-size: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
            transition: all 0.2s ease;
        }}
        .summit-evidence-box:hover {{
            border-color: rgba(56, 189, 248, 0.55);
            box-shadow: 0 6px 24px rgba(56, 189, 248, 0.12);
        }}
        .summit-evidence-toggle-btn {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: linear-gradient(90deg, rgba(56, 189, 248, 0.12) 0%, rgba(30, 58, 138, 0.15) 100%);
            padding: 9px 14px;
            cursor: pointer;
            border-bottom: 1px solid rgba(56, 189, 248, 0.2);
            user-select: none;
        }}
        .summit-evidence-title {{
            font-weight: 800;
            color: #38bdf8;
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 11.5px;
            letter-spacing: 0.5px;
        }}
        .summit-evidence-content {{
            padding: 14px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}
        .evidence-peer-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 11px;
            margin-top: 4px;
        }}
        .evidence-peer-table th {{
            background: rgba(255, 255, 255, 0.05);
            color: #94a3b8;
            font-weight: 700;
            padding: 6px 8px;
            text-align: left;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            font-family: 'JetBrains Mono', monospace;
            font-size: 10.5px;
            text-transform: uppercase;
        }}
        .evidence-peer-table td {{
            padding: 7px 8px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.04);
            color: #cbd5e1;
        }}
        .evidence-check-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
            gap: 8px;
            margin-top: 4px;
        }}
        .evidence-check-item {{
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 6px;
            padding: 7px 10px;
        }}
        .evidence-check-k {{
            font-size: 10px;
            color: #94a3b8;
            text-transform: uppercase;
            font-weight: 700;
        }}
        .evidence-check-v {{
            font-size: 11px;
            color: #34d399;
            font-weight: 600;
            font-family: 'JetBrains Mono', monospace;
            margin-top: 2px;
        }}

        /* CHAIRMAN DIRECT INPUT BAR */
        .summit-input-panel {{
            background: var(--bg-surface);
            border-top: 1px solid var(--border-color);
            padding: 16px 20px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}
        .summit-input-label {{
            font-size: 11px;
            font-weight: 800;
            color: #facc15;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .summit-input-row {{
            display: flex;
            gap: 10px;
        }}
        .summit-input-field {{
            flex: 1;
            background: var(--bg-base);
            border: 1px solid rgba(234, 179, 8, 0.35);
            border-radius: 10px;
            color: #fff;
            padding: 12px 16px;
            font-size: 13.5px;
            font-family: inherit;
            outline: none;
            transition: border-color 0.2s;
        }}
        .summit-input-field:focus {{
            border-color: #facc15;
            box-shadow: 0 0 12px rgba(234, 179, 8, 0.25);
        }}
        .summit-btn-send {{
            background: linear-gradient(135deg, #eab308 0%, #ca8a04 100%);
            color: #070a12;
            font-weight: 800;
            font-size: 13px;
            padding: 12px 22px;
            border-radius: 10px;
            border: none;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 6px;
            white-space: nowrap;
        }}
        .summit-btn-send:hover {{
            transform: translateY(-1px);
            box-shadow: 0 4px 16px rgba(234, 179, 8, 0.35);
        }}
        /* V9.0 SUMMIT SCHEDULE BAR, 14-DEPT ATTENDANCE & T-15M PREP DOSSIERS */
        .summit-schedule-bar {{
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.92), rgba(30, 41, 59, 0.85));
            border: 1px solid rgba(56, 189, 248, 0.32);
            border-radius: 14px;
            padding: 14px 18px;
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            align-items: center;
            justify-content: space-between;
        }}
        .summit-sched-inputs {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            align-items: center;
            flex: 1;
        }}
        .summit-sched-input {{
            background: rgba(9, 14, 26, 0.95);
            border: 1px solid rgba(148, 163, 184, 0.3);
            color: #f8fafc;
            border-radius: 8px;
            padding: 7px 10px;
            font-size: 12px;
            font-family: inherit;
        }}
        .summit-sched-btn {{
            background: linear-gradient(135deg, #38bdf8, #6366f1);
            color: #ffffff;
            border: none;
            border-radius: 8px;
            padding: 8px 14px;
            font-size: 12px;
            font-weight: 800;
            cursor: pointer;
            white-space: nowrap;
            transition: transform 0.15s ease;
        }}
        .summit-sched-btn:hover {{ transform: translateY(-1px); }}
        .summit-attendance-strip {{
            background: var(--bg-surface);
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 14px;
            padding: 12px 16px;
        }}
        .summit-att-grid {{
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-top: 8px;
        }}
        .summit-att-badge {{
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 4px 9px;
            border-radius: 9999px;
            font-size: 11px;
            font-weight: 700;
            background: rgba(16, 185, 129, 0.12);
            border: 1px solid rgba(16, 185, 129, 0.35);
            color: #d1fae5;
        }}
        .summit-prep-panel {{
            background: var(--bg-surface);
            border: 1px solid rgba(168, 85, 247, 0.35);
            border-radius: 14px;
            padding: 14px 18px;
        }}
        .summit-prep-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(265px, 1fr));
            gap: 10px;
            margin-top: 12px;
        }}
        .summit-prep-card {{
            background: rgba(9, 14, 26, 0.9);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 10px;
            padding: 11px 12px;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}
        .summit-prep-card:hover {{ border-color: rgba(168, 85, 247, 0.45); }}
        .summit-msg-card.msg-prep {{
            background: rgba(168, 85, 247, 0.06);
            border-color: rgba(168, 85, 247, 0.35);
        }}
        .summit-charter-strip {{
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.09), rgba(15, 23, 42, 0.85));
            border: 1px solid rgba(245, 158, 11, 0.35);
            border-radius: 14px;
            padding: 13px 16px;
        }}
        .summit-charter-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
            gap: 8px;
            margin-top: 10px;
        }}
        .summit-charter-card {{
            background: rgba(9, 14, 26, 0.85);
            border: 1px solid rgba(245, 158, 11, 0.25);
            border-radius: 8px;
            padding: 8px 10px;
            font-size: 11px;
            line-height: 1.45;
        }}
        .summit-james-summary-card {{
            background: linear-gradient(180deg, rgba(16, 185, 129, 0.08) 0%, rgba(15, 23, 42, 0.88) 100%);
            border: 1px solid rgba(16, 185, 129, 0.38);
            border-radius: 16px;
            padding: 16px;
        }}
        .summit-agile-pill {{
            background: rgba(245, 158, 11, 0.14);
            border: 1px solid rgba(245, 158, 11, 0.4);
            color: #fde68a;
            border-radius: 8px;
            padding: 7px 10px;
            font-size: 11px;
            font-weight: 700;
            line-height: 1.4;
            margin: 8px 0 10px 0;
        }}
        .summit-archive-panel {{
            background: var(--bg-surface);
            border: 1px solid rgba(56, 189, 248, 0.32);
            border-radius: 16px;
            padding: 16px;
        }}
        .summit-archive-list {{
            display: flex;
            flex-direction: column;
            gap: 8px;
            margin-top: 10px;
            max-height: 240px;
            overflow-y: auto;
        }}
        .summit-archive-item {{
            background: rgba(9, 14, 26, 0.88);
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 8px;
            padding: 8px 10px;
            display: flex;
            flex-direction: column;
            gap: 4px;
            font-size: 11px;
        }}
        .summit-archive-item.active-viewing {{
            border-color: #38bdf8;
            background: rgba(56, 189, 248, 0.1);
        }}
        .summit-clean-btn {{
            width: 100%;
            margin-top: 10px;
            padding: 9px 12px;
            border-radius: 8px;
            font-size: 11.5px;
            font-weight: 800;
            cursor: pointer;
            border: 1px solid rgba(56, 189, 248, 0.4);
            background: rgba(56, 189, 248, 0.14);
            color: #7dd3fc;
            transition: all 0.15s ease;
        }}
        .summit-clean-btn.locked {{
            background: rgba(100, 116, 139, 0.16);
            border-color: rgba(148, 163, 184, 0.3);
            color: #94a3b8;
        }}

        /* CỘT PHẢI: BÀN KIỂM SÁT TRỌNG & BIỂU QUYẾT */
        .summit-side-col {{
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}
        .summit-side-card {{
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 18px 20px;
            position: relative;
        }}
        .summit-side-title {{
            font-size: 13px;
            font-weight: 800;
            color: #fff;
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 14px;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}
        .inspector-rule-item {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            font-size: 12px;
        }}
        .inspector-rule-item:last-child {{ border-bottom: none; }}
        .inspector-rule-text {{ color: var(--text-muted); }}
        .inspector-rule-badge {{
            background: rgba(16, 185, 129, 0.15);
            color: #34d399;
            padding: 2px 8px;
            border-radius: 9999px;
            font-size: 10.5px;
            font-weight: 800;
            font-family: 'JetBrains Mono', monospace;
        }}
        .summit-stock-vote-card {{
            background: var(--bg-base);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 12px 14px;
            margin-bottom: 10px;
        }}
        .summit-stock-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 6px;
        }}
        .summit-stock-sym {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 15px;
            font-weight: 800;
            color: #38bdf8;
        }}
        .summit-vote-tally {{
            background: rgba(56, 189, 248, 0.15);
            color: #38bdf8;
            padding: 2px 8px;
            border-radius: 9999px;
            font-size: 11px;
            font-weight: 800;
        }}
        .summit-stock-meta {{
            font-size: 11.5px;
            color: var(--text-muted);
            line-height: 1.4;
        }}
        .summit-action-btn-large {{
            width: 100%;
            background: linear-gradient(135deg, #1e1b4b 0%, #1e293b 100%);
            border: 1px solid #38bdf8;
            color: #38bdf8;
            padding: 12px 16px;
            border-radius: 10px;
            font-size: 12.5px;
            font-weight: 800;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }}
        .summit-action-btn-large:hover {{
            background: #38bdf8;
            color: #070a12;
            box-shadow: 0 4px 18px rgba(56, 189, 248, 0.35);
        }}
        .summit-action-btn-gold {{
            width: 100%;
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            color: #0f172a;
            font-weight: 800;
            font-size: 11.5px;
            padding: 11px 14px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            box-shadow: 0 4px 18px rgba(245, 158, 11, 0.35);
            transition: all 0.2s;
            text-transform: uppercase;
        }}
        .summit-action-btn-gold:hover {{
            background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
            transform: translateY(-2px);
            box-shadow: 0 6px 24px rgba(245, 158, 11, 0.5);
        }}
        .summit-action-btn-gold:disabled {{
            opacity: 0.65;
            cursor: not-allowed;
            transform: none;
        }}

    
        /* ========================================================
           TAB 3: PHÒNG TÁC CHIẾN ĐẦU TƯ TRONG NGÀY (WAR-ROOM) CSS
           ======================================================== */
        .war-room-wrap {{
            display: flex;
            flex-direction: column;
            gap: 18px;
            padding-bottom: 40px;
        }}

        /* Header Ribbon */
        .war-room-ribbon {{
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.9));
            border: 1px solid rgba(56, 189, 248, 0.35);
            border-radius: 12px;
            padding: 16px 20px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45);
            display: flex;
            flex-direction: column;
            gap: 14px;
        }}
        .war-room-ribbon-top {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 12px;
        }}
        .war-room-title-box {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .war-room-live-pulse {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 10px;
            background: rgba(239, 68, 68, 0.2);
            border: 1px solid rgba(239, 68, 68, 0.5);
            border-radius: 999px;
            font-size: 11px;
            font-weight: 800;
            color: #f87171;
            letter-spacing: 0.5px;
        }}
        .war-room-live-dot {{
            width: 8px;
            height: 8px;
            background: #ef4444;
            border-radius: 50%;
            animation: pulse-dot 1.5s infinite;
        }}
        @keyframes pulse-dot {{
            0%, 100% {{ transform: scale(1); opacity: 1; }}
            50% {{ transform: scale(1.4); opacity: 0.4; }}
        }}
        .war-room-title {{
            font-size: 17px;
            font-weight: 800;
            color: #f8fafc;
            letter-spacing: 0.3px;
        }}
        .war-room-subtitle {{
            font-size: 12px;
            color: #94a3b8;
            margin-top: 2px;
        }}
        .war-room-meta-group {{
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
        }}
        .meta-pill {{
            display: flex;
            align-items: center;
            gap: 6px;
            background: rgba(15, 23, 42, 0.85);
            border: 1px solid rgba(148, 163, 184, 0.2);
            padding: 5px 12px;
            border-radius: 8px;
            font-size: 11.5px;
            color: #e2e8f0;
        }}
        .meta-pill strong {{
            color: #38bdf8;
        }}

        /* 8-Phase Market Progress Bar */
        .phase-stepper-wrap {{
            display: flex;
            align-items: stretch;
            gap: 6px;
            overflow-x: auto;
            padding: 4px 0;
        }}
        .phase-step-card {{
            flex: 1;
            min-width: 125px;
            background: rgba(15, 23, 42, 0.7);
            border: 1px solid rgba(148, 163, 184, 0.15);
            border-radius: 8px;
            padding: 8px 10px;
            display: flex;
            flex-direction: column;
            gap: 3px;
            transition: all 0.25s ease;
        }}
        .phase-step-card.active {{
            background: linear-gradient(135deg, rgba(14, 165, 233, 0.25), rgba(30, 41, 59, 0.95));
            border-color: #38bdf8;
            box-shadow: 0 0 16px rgba(56, 189, 248, 0.35);
            transform: translateY(-2px);
        }}
        .phase-step-card.completed {{
            border-color: rgba(16, 185, 129, 0.35);
            background: rgba(16, 185, 129, 0.08);
        }}
        .phase-card-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 10px;
            font-weight: 700;
            color: #94a3b8;
        }}
        .phase-step-card.active .phase-card-header {{
            color: #38bdf8;
        }}
        .phase-card-name {{
            font-size: 11.5px;
            font-weight: 800;
            color: #f1f5f9;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .phase-card-time {{
            font-size: 10.5px;
            color: #64748b;
        }}
        .phase-step-card.active .phase-card-time {{
            color: #7dd3fc;
            font-weight: 700;
        }}

        /* 3-Column Tactical Layout */
        .war-room-columns {{
            display: grid;
            grid-template-columns: 32% 40% 28%;
            gap: 18px;
        }}
        @media (max-width: 1250px) {{
            .war-room-columns {{
                grid-template-columns: 1fr;
            }}
        }}

        /* Common Card Style */
        .tactical-panel {{
            background: rgba(15, 23, 42, 0.85);
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 12px;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 14px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
        }}
        .panel-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid rgba(148, 163, 184, 0.15);
            padding-bottom: 10px;
        }}
        .panel-title-box {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .panel-icon {{
            font-size: 18px;
        }}
        .panel-title {{
            font-size: 14.5px;
            font-weight: 800;
            color: #f8fafc;
        }}
        .panel-badge {{
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 700;
        }}

        /* Stock Cards */
        .stock-pick-card {{
            background: rgba(30, 41, 59, 0.6);
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 9px;
            padding: 12px 14px;
            display: flex;
            flex-direction: column;
            gap: 9px;
            transition: all 0.2s ease;
        }}
        .stock-pick-card:hover {{
            border-color: #38bdf8;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(56, 189, 248, 0.15);
        }}
        .stock-pick-card.leader {{
            border-left: 4px solid #10b981;
        }}
        .stock-pick-card.alpha {{
            border-left: 4px solid #38bdf8;
        }}
        .stock-pick-card.standby {{
            border-left: 4px solid #64748b;
            opacity: 0.85;
        }}
        .stock-card-top {{
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .stock-ticker {{
            font-size: 15px;
            font-weight: 900;
            color: #f8fafc;
            letter-spacing: 0.5px;
        }}
        .stock-name {{
            font-size: 11px;
            color: #94a3b8;
            margin-left: 6px;
        }}
        .stock-stats-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 6px;
            background: rgba(15, 23, 42, 0.6);
            padding: 7px;
            border-radius: 6px;
            border: 1px solid rgba(148, 163, 184, 0.1);
        }}
        .stock-stat-item {{
            display: flex;
            flex-direction: column;
            gap: 2px;
        }}
        .stat-label {{
            font-size: 9.5px;
            color: #64748b;
            text-transform: uppercase;
        }}
        .stat-val {{
            font-size: 12px;
            font-weight: 800;
            color: #f1f5f9;
        }}
        .stat-val.gain {{
            color: #34d399;
        }}
        .stat-val.loss {{
            color: #f87171;
        }}
        .stat-val.gold {{
            color: #fbbf24;
        }}
        .stock-catalyst {{
            font-size: 11px;
            color: #cbd5e1;
            line-height: 1.4;
            background: rgba(30, 41, 59, 0.4);
            padding: 6px 9px;
            border-radius: 6px;
        }}

        /* Directive Stream & Chat Box */
        .directive-hero-box {{
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(15, 23, 42, 0.9));
            border: 1px solid rgba(52, 211, 153, 0.4);
            border-radius: 9px;
            padding: 12px 14px;
            display: flex;
            align-items: flex-start;
            gap: 10px;
        }}
        .directive-hero-text {{
            font-size: 12px;
            color: #e2e8f0;
            line-height: 1.5;
        }}

        /* Timeline in Column 2 */
        .tactical-milestones-list {{
            display: flex;
            flex-direction: column;
            gap: 8px;
            max-height: 320px;
            overflow-y: auto;
            padding-right: 4px;
        }}
        .milestone-card {{
            background: rgba(30, 41, 59, 0.5);
            border: 1px solid rgba(148, 163, 184, 0.15);
            border-radius: 8px;
            padding: 9px 12px;
            display: flex;
            flex-direction: column;
            gap: 3px;
            transition: all 0.2s ease;
        }}
        .milestone-card.active {{
            border-color: #38bdf8;
            background: rgba(56, 189, 248, 0.1);
            box-shadow: 0 0 10px rgba(56, 189, 248, 0.2);
        }}
        .milestone-card.completed {{
            border-color: rgba(16, 185, 129, 0.3);
            background: rgba(16, 185, 129, 0.05);
        }}
        .milestone-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .milestone-time {{
            font-size: 11px;
            font-weight: 800;
            color: #38bdf8;
        }}
        .milestone-badge {{
            font-size: 10px;
            font-weight: 700;
            padding: 2px 6px;
            border-radius: 4px;
        }}
        .milestone-title {{
            font-size: 12px;
            font-weight: 700;
            color: #f8fafc;
        }}
        .milestone-desc {{
            font-size: 11px;
            color: #94a3b8;
            line-height: 1.35;
        }}

        /* Interactive Directive Box */
        .tactical-interactive-card {{
            background: rgba(15, 23, 42, 0.95);
            border: 1px solid rgba(56, 189, 248, 0.3);
            border-radius: 10px;
            padding: 13px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}
        .directive-history-box {{
            max-height: 240px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 9px;
            padding-right: 4px;
        }}
        .directive-msg {{
            padding: 9px 11px;
            border-radius: 7px;
            font-size: 11.5px;
            line-height: 1.45;
            display: flex;
            flex-direction: column;
            gap: 3px;
        }}
        .directive-msg.chairman {{
            background: rgba(245, 158, 11, 0.12);
            border: 1px solid rgba(245, 158, 11, 0.4);
            border-left: 3px solid #f59e0b;
        }}
        .directive-msg.specialist {{
            background: rgba(14, 165, 233, 0.12);
            border: 1px solid rgba(14, 165, 233, 0.4);
            border-left: 3px solid #38bdf8;
        }}
        .directive-msg.sentinel {{
            background: rgba(16, 185, 129, 0.12);
            border: 1px solid rgba(16, 185, 129, 0.4);
            border-left: 3px solid #10b981;
        }}
        .directive-msg-head {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 10.5px;
            font-weight: 800;
        }}
        .directive-msg.chairman .directive-msg-head {{ color: #fbbf24; }}
        .directive-msg.specialist .directive-msg-head {{ color: #38bdf8; }}
        .directive-msg.sentinel .directive-msg-head {{ color: #34d399; }}
        .directive-msg-body {{
            color: #e2e8f0;
        }}
        .quick-prompts-row {{
            display: flex;
            gap: 5px;
            flex-wrap: wrap;
        }}
        .btn-quick-prompt {{
            background: rgba(30, 41, 59, 0.7);
            border: 1px solid rgba(148, 163, 184, 0.25);
            color: #cbd5e1;
            padding: 4px 9px;
            border-radius: 5px;
            font-size: 10.5px;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        .btn-quick-prompt:hover {{
            background: rgba(56, 189, 248, 0.2);
            border-color: #38bdf8;
            color: #f8fafc;
        }}
        .directive-input-row {{
            display: flex;
            gap: 8px;
        }}
        .directive-input {{
            flex: 1;
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid rgba(148, 163, 184, 0.3);
            border-radius: 6px;
            padding: 8px 12px;
            color: #f8fafc;
            font-size: 11.5px;
            outline: none;
        }}
        .directive-input:focus {{
            border-color: #38bdf8;
            box-shadow: 0 0 8px rgba(56, 189, 248, 0.3);
        }}
        .btn-send-directive {{
            background: linear-gradient(135deg, #0284c7, #0369a1);
            border: none;
            color: #ffffff;
            font-weight: 800;
            font-size: 11.5px;
            padding: 8px 14px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s ease;
            white-space: nowrap;
        }}
        .btn-send-directive:hover {{
            background: linear-gradient(135deg, #0ea5e9, #0284c7);
            box-shadow: 0 0 12px rgba(14, 165, 233, 0.4);
        }}

    
        /* Action Plan Card & Live Stock Sentinel Table */
        .action-plan-hero-card {{
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.95));
            border: 1px solid rgba(56, 189, 248, 0.4);
            border-radius: 10px;
            padding: 14px 16px;
            display: flex;
            flex-direction: column;
            gap: 10px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
        }}
        .action-plan-tag {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(245, 158, 11, 0.2);
            color: #fbbf24;
            border: 1px solid rgba(245, 158, 11, 0.4);
            padding: 3px 10px;
            border-radius: 999px;
            font-size: 11px;
            font-weight: 800;
        }}
        .action-plan-step-title {{
            font-size: 13.5px;
            font-weight: 800;
            color: #38bdf8;
            letter-spacing: 0.2px;
        }}
        .action-plan-content {{
            font-size: 12px;
            color: #f1f5f9;
            line-height: 1.5;
            background: rgba(15, 23, 42, 0.7);
            border: 1px solid rgba(148, 163, 184, 0.15);
            border-radius: 8px;
            padding: 10px 12px;
        }}
        .action-plan-rule {{
            font-size: 11px;
            color: #cbd5e1;
            font-style: italic;
            border-left: 3px solid #f59e0b;
            padding-left: 8px;
        }}

        /* Market Radar Overview Card */
        .market-radar-card {{
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.9));
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 10px;
            padding: 12px;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        .index-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
        }}
        .index-item {{
            background: rgba(15, 23, 42, 0.7);
            border: 1px solid rgba(148, 163, 184, 0.15);
            border-radius: 7px;
            padding: 8px 10px;
            display: flex;
            flex-direction: column;
            gap: 2px;
        }}

        /* Live Stock Ticker Sentinel Table */
        .stock-sentinel-table {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            font-size: 11px;
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid rgba(148, 163, 184, 0.2);
        }}
        .stock-sentinel-table th {{
            background: rgba(30, 41, 59, 0.9);
            color: #94a3b8;
            font-weight: 700;
            padding: 7px 8px;
            text-align: left;
            border-bottom: 1px solid rgba(148, 163, 184, 0.2);
            font-size: 10px;
            text-transform: uppercase;
        }}
        .stock-sentinel-table td {{
            background: rgba(15, 23, 42, 0.6);
            color: #f1f5f9;
            padding: 7px 8px;
            border-bottom: 1px solid rgba(148, 163, 184, 0.1);
        }}
        .stock-sentinel-table tr:hover td {{
            background: rgba(56, 189, 248, 0.1);
        }}
        .price-badge {{
            font-weight: 800;
            font-size: 11.5px;
        }}
        .price-badge.up {{ color: #34d399; }}
        .price-badge.down {{ color: #f87171; }}
        .price-badge.ref {{ color: #fbbf24; }}

    </style>
</head>
<body>
    <div class="container">
        <!-- HEADER -->
        <header class="portal-header">
            <div>
                <div class="brand-title">
                    <span style="font-size: 26px;">🏛️</span>
                    <span>APEX INSTITUTIONAL CLOUD PORTAL</span>
                    <span style="background: rgba(192, 132, 252, 0.15); color: #c084fc; border: 1px solid rgba(192, 132, 252, 0.3); font-size: 11px; padding: 3px 9px; border-radius: 9999px; font-weight: 800;">V4.0</span>
                </div>
                <div class="brand-sub">
                    <span>👤 Chủ tọa: <strong style="color: #fff;">Chủ tịch Trần Quốc Thiên Phước</strong></span>
                    <span>•</span>
                    <span>🏦 TCBS: <strong style="color: #38bdf8; font-family: 'JetBrains Mono', monospace;">105C307855</strong></span>
                    <span>•</span>
                    <span>🎖️ Tổng Tư Lệnh: <strong style="color: #c084fc;">Master CIO James</strong></span>
                </div>
            </div>
            <div class="header-meta">
                <div class="live-badge">
                    <span class="pulse-dot"></span>
                    <span>CLOUD 24/7 ACTIVE</span>
                </div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 13px; color: #cbd5e1; background: var(--bg-base); padding: 7px 16px; border-radius: 8px; border: 1px solid var(--border-color);" id="live-clock">
                    --:--:--
                </div>
                <button onclick="refreshData()" class="btn-read" style="display: flex; align-items: center; gap: 6px; padding: 8px 16px;">
                    <span>🔄</span> <span>Làm Mới</span>
                </button>
                {auth_logout_btn_html}
            </div>
        </header>

        <!-- KPI STATS (4 HỘP CHỈ SỐ ĐIỀU HÀNH) -->
        <section class="kpi-grid">
            <div class="kpi-card" style="--card-accent: #10b981;">
                <div class="kpi-lbl">💰 Tiền Mặt TCInvest (SSOT V2.0)</div>
                <div class="kpi-val" id="top-kpi-cash-val" style="color: #34d399;">{ssot['cash_str']}</div>
                <div class="kpi-sub" id="top-kpi-cash-sub"><span style="color: #34d399; font-weight: 700;">{ssot['cash_pct']:.1f}% Cash</span> • {ssot['total_shares']} CP ({ssot['stocks_str']} • {ssot['stocks_pct']:.1f}% NAV)</div>
            </div>
            <div class="kpi-card" style="--card-accent: #38bdf8;">
                <div class="kpi-lbl">📈 Lãi Ròng Thu Về Vòng 1</div>
                <div class="kpi-val" style="color: #38bdf8;">{ssot['realized_str']}</div>
                <div class="kpi-sub">Đã tất toán 100% (HPG, TCB, MBB)</div>
            </div>
            <div class="kpi-card" style="--card-accent: #c084fc;">
                <div class="kpi-lbl">📑 Báo Cáo Hôm Nay ({today_str})</div>
                <div class="kpi-val" style="color: #c084fc;" id="stat-today-count">{today_reports_count} Báo Cáo</div>
                <div class="kpi-sub">Kho Vault: <strong id="stat-vault-count" style="color: #10b981;">{total_vault_count} Báo Cáo</strong> (SQLite V5.0: Sức chứa 100.000)</div>
            </div>
            <div class="kpi-card" style="--card-accent: #f472b6;">
                <div class="kpi-lbl">🛡️ Hệ Thống Tự Hành 24/7</div>
                <div class="kpi-val" style="color: #f472b6;">{len(services)}/4 Daemons</div>
                <div class="kpi-sub">Watchdog Tự Hồi Phục Bất Tử</div>
            </div>
        </section>

        {db_milestone_banner}
        <!-- TABS NAV -->
        <nav class="tab-nav">
            <button class="tab-btn active" onclick="switchTab('reports')">
                <span>📑</span> <span>1. Thư Viện Báo Cáo 18 Cột Mốc</span>
                <span class="tab-badge" id="nav-total-count">{total_reports_count}</span>
            </button>
            <button class="tab-btn" onclick="switchTab('portfolio')">
                <span>🎯</span> <span>2. Tầm Ngắm Vòng 2 & TradingView</span>
            </button>
            <button class="tab-btn" id="btn-tab-war-room" onclick="switchTab('war-room')">
                <span>⚡</span> <span>3. Phòng Tác Chiến Trong Ngày (Minh Quân & Victor)</span>
                <span class="live-badge" style="background: rgba(239, 68, 68, 0.25); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.5); padding: 2px 8px; font-size: 10.5px; margin-left: 4px; border-radius: 9999px; animation: pulse 2s infinite;">● TRỰC CHIẾN LIVE</span>
            </button>
            <button class="tab-btn" onclick="switchTab('james-command')">
                <span>🎖️</span> <span>4. Bàn Chỉ Huy Master CIO James</span>
            </button>
            <button class="tab-btn" id="btn-tab-summit" onclick="switchTab('summit-room')">
                <span>🏛️</span> <span>5. Phòng Họp Thượng Đỉnh Trực Tuyến</span>
                <span class="live-badge" id="summit-nav-badge" style="padding: 2px 8px; font-size: 10.5px; margin-left: 4px; border-radius: 9999px;">● HỌP 00H45</span>
            </button>
            <button class="tab-btn" onclick="switchTab('timeline')">
                <span>⏰</span> <span>6. Tiến Độ 18 Cột Mốc Ngày</span>
            </button>
            <button class="tab-btn" onclick="switchTab('supervisor')">
                <span>🛡️</span> <span>7. Giám Sát Cụm Container 24/7</span>
            </button>
        </nav>

        <!-- ========================================================
             TAB 1: THƯ VIỆN BÁO CÁO (PHÂN LOẠI 2 TẦNG CHUYÊN NGHIỆP)
             ======================================================== -->
        <main id="tab-reports" class="tab-pane active">
            <div class="library-controller">
                <!-- TẦNG 1: THỜI GIAN & CA TÁC CHIẾN -->
                <div class="time-filter-section">
                    <div>
                        <div class="filter-row-header">📅 Kho Lưu Trữ Thời Gian</div>
                        <div class="date-pills">
                            <button class="date-pill-btn active" id="btn-date-today" onclick="selectDateFilter('today')">
                                <span>🌟</span> <span>Hôm Nay ({today_str})</span>
                            </button>
                            <button class="date-pill-btn" id="btn-date-yesterday" onclick="selectDateFilter('yesterday')">
                                <span>⏮️</span> <span>Hôm Qua</span>
                            </button>
                            <button class="date-pill-btn" id="btn-date-all" onclick="selectDateFilter('all')">
                                <span>🏛️</span> <span>Toàn Bộ Lịch Sử</span>
                            </button>
                            <select id="archive-date-select" class="archive-select" onchange="selectDateFromDropdown(this.value)">
                                {date_options_html}
                            </select>
                        </div>
                    </div>

                    <div>
                        <div class="filter-row-header">⏱️ 4 Ca Tác Chiến</div>
                        <div class="shifts-group">
                            <button class="shift-pill active" onclick="filterShift('all')">Tất Cả Ca</button>
                            <button class="shift-pill" onclick="filterShift('Ca Sáng')">🌅 Ca Sáng</button>
                            <button class="shift-pill" onclick="filterShift('Ca Trưa')">☀️ Ca Trưa</button>
                            <button class="shift-pill" onclick="filterShift('Ca Chiều')">🎯 Ca Chiều</button>
                            <button class="shift-pill" onclick="filterShift('Ca Tối')">🌙 Ca Tối & Đêm</button>
                        </div>
                    </div>
                </div>

                <!-- TẦNG 2: 5 KHỐI PHÂN LOẠI CHUYÊN MÔN THỂ CHẾ -->
                <div>
                    <div class="filter-row-header">🏛️ Phân Loại Khối Chức Năng (12 Phòng Ban)</div>
                    <div class="category-filter-section" id="cat-filter-buttons">
                        <button class="cat-btn active" onclick="filterCategory('all')">
                            <span>🌟</span> <span>Tất Cả</span>
                            <span class="cat-count" id="count-cat-all">0</span>
                        </button>
                        <button class="cat-btn" onclick="filterCategory('macro')">
                            <span>🌐</span> <span>Vĩ Mô & SBV</span>
                            <span class="cat-count" id="count-cat-macro">0</span>
                        </button>
                        <button class="cat-btn" onclick="filterCategory('equity_bctc')">
                            <span>📑</span> <span>BCTC & Pháp Y</span>
                            <span class="cat-count" id="count-cat-equity">0</span>
                        </button>
                        <button class="cat-btn" onclick="filterCategory('cio_execution')">
                            <span>🎖️</span> <span>Sổ Lệnh & Thực Thi</span>
                            <span class="cat-count" id="count-cat-cio">0</span>
                        </button>
                        <button class="cat-btn" onclick="filterCategory('risk_learning')">
                            <span>⚖️</span> <span>Rủi Ro & Tự Học</span>
                            <span class="cat-count" id="count-cat-risk">0</span>
                        </button>
                        <button class="cat-btn" onclick="filterCategory('mentorship')">
                            <span>🎓</span> <span>Học Viện Huấn Luyện</span>
                            <span class="cat-count" id="count-cat-mentor">0</span>
                        </button>
                    </div>
                </div>

                <!-- TẦNG 3: TOOLBAR TÌM KIẾM & CHẾ ĐỘ XEM -->
                <div class="library-toolbar">
                    <div class="search-box-wrap">
                        <span class="search-icon">🔍</span>
                        <input type="text" id="report-search" class="search-box" placeholder="Tìm theo mã CP (FPT, DGC, HPG...) hoặc tiêu đề báo cáo..." oninput="searchReports()">
                    </div>
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <span style="font-size: 12px; color: var(--text-muted); font-weight: 600;">Chế độ xem:</span>
                        <div class="view-mode-toggle">
                            <button class="view-btn active" id="btn-view-grid" onclick="switchViewMode('grid')">🖼️ Dạng Thẻ Grid</button>
                            <button class="view-btn" id="btn-view-table" onclick="switchViewMode('table')">📋 Dạng Bảng Nhanh</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- CONTAINER HIỂN THỊ BÁO CÁO -->
            <div id="reports-fallback-banner" style="display: none; margin-bottom: 14px; padding: 11px 16px; border-radius: 10px; background: rgba(56, 189, 248, 0.1); border: 1px solid rgba(56, 189, 248, 0.35); color: #bae6fd; font-size: 13px; align-items: center; justify-content: space-between; gap: 12px;">
                <span id="reports-fallback-text"></span>
                <button class="btn-read" onclick="selectDateFilter('all')" style="padding: 5px 12px; font-size: 11.5px; white-space: nowrap;">🏛️ Xem Toàn Bộ Lịch Sử</button>
            </div>
            <div id="reports-container">
                <!-- Sẽ được render bởi JavaScript -->
            </div>
        </main>

        <!-- ========================================================
             TAB 2: TẦM NGẮM VÒNG 2 & TRADINGVIEW (LIVE HOSE)
             ======================================================== -->
        <section id="tab-portfolio" class="tab-pane">
            <!-- TRADINGVIEW LIVE HOSE CHART WIDGET -->
            <div style="background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 16px; padding: 22px; margin-bottom: 22px;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px; margin-bottom: 16px;">
                    <div>
                        <h3 style="font-size: 17px; color: #fff; display: flex; align-items: center; gap: 10px; font-weight: 800;">
                            <span>📈</span> <span>BIỂU ĐỒ NẾN KỸ THUẬT REALTIME TRADINGVIEW (LIVE SÀN HOSE)</span>
                        </h3>
                        <p style="font-size: 12.5px; color: var(--text-muted); margin-top: 5px;">
                            Soi trực tiếp Candlestick, Khối lượng Volume, MA20/MA50, RSI & MACD trên sàn HOSE • Cập nhật trực tiếp từng giây
                        </p>
                    </div>
                    <div style="display: flex; gap: 8px; flex-wrap: wrap;" id="tv-symbol-buttons">
                        <button class="tv-btn active" onclick="switchTVSymbol('HOSE:VNINDEX', this)">📈 VN-INDEX</button>
                        <button class="tv-btn" onclick="switchTVSymbol('HOSE:HDB', this)">🏦 HDB (Đang giữ)</button>
                        <button class="tv-btn" onclick="switchTVSymbol('HOSE:MSH', this)">🧵 MSH (Đang giữ)</button>
                        <button class="tv-btn" onclick="switchTVSymbol('HOSE:BAF', this)">🐷 BAF (Alpha Watchlist)</button>
                        <button class="tv-btn" onclick="switchTVSymbol('HNX:IDC', this)">🏗️ IDC (Alpha Watchlist)</button>
                        <button class="tv-btn" onclick="switchTVSymbol('UPCOM:BSR', this)">🛢️ BSR (Dầu Khí)</button>
                        <button class="tv-btn" onclick="switchTVSymbol('HOSE:DPR', this)">🌳 DPR (Cao Su)</button>
                    </div>
                </div>
                <div id="tv_chart_container" style="height: 540px; border-radius: 12px; overflow: hidden; border: 1px solid var(--border-color);"></div>
            </div>

            <!-- PHÂN BỔ VỐN & NGUYÊN TẮC -->
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); gap: 20px; margin-bottom: 22px;">
                <div style="background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 16px; padding: 22px;">
                    <h3 style="font-size: 16px; margin-bottom: 16px; color: #fff; font-weight: 800;">📊 PHÂN BỔ TÀI SẢN THỰC TẾ (SSOT V2.0)</h3>
                    <div style="margin-bottom: 16px;">
                        <div style="display: flex; justify-content: space-between; font-size: 13.5px; margin-bottom: 8px;">
                            <span>Tiền Mặt Khả Dụng (Két TCInvest)</span>
                            <strong style="color: #34d399; font-family: 'JetBrains Mono', monospace;">{ssot['cash_pct']:.1f}% ({ssot['cash_str']})</strong>
                        </div>
                        <div style="background: var(--bg-base); height: 12px; border-radius: 6px; overflow: hidden; border: 1px solid var(--border-color);">
                            <div style="background: linear-gradient(90deg, #10b981, #34d399); width: {ssot['cash_pct']:.1f}%; height: 100%;"></div>
                        </div>
                    </div>
                    <div>
                        <div style="display: flex; justify-content: space-between; font-size: 13.5px; margin-bottom: 8px;">
                            <span>Cổ Phiếu Đang Nắm Giữ</span>
                            <strong style="color: #38bdf8; font-family: 'JetBrains Mono', monospace;">{ssot['stocks_pct']:.1f}% ({ssot['stocks_str']} • {ssot['total_shares']} CP)</strong>
                        </div>
                        <div style="background: var(--bg-base); height: 12px; border-radius: 6px; overflow: hidden; border: 1px solid var(--border-color);">
                            <div style="background: linear-gradient(90deg, #0ea5e9, #38bdf8); width: {ssot['stocks_pct']:.1f}%; height: 100%;"></div>
                        </div>
                    </div>
                    <p style="margin-top: 18px; font-size: 12.5px; color: #94a3b8; line-height: 1.6;">
                        🛡️ <strong>Chế độ Bảo Vệ Vị Thế:</strong> Danh mục hiện nắm giữ {ssot['holdings_desc']} ({ssot['stocks_str']}). Tiền mặt khả dụng {ssot['cash_str']} ({ssot['cash_pct']:.1f}% NAV) bảo toàn an toàn trong két. Victor đã kích hoạt ngay hàng rào phòng thủ Stop 2xATR!
                    </p>
                </div>

                <div style="background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 16px; padding: 22px;">
                    <h3 style="font-size: 16px; margin-bottom: 16px; color: #fff; font-weight: 800;">🎯 QUY TẮC ĐI VỐN KIM TỰ THÁP (30% - 40% - 30%)</h3>
                    <div style="font-size: 13px; color: #cbd5e1; line-height: 1.8;">
                        <div>• <strong>Nhịp 1 (30% Thăm dò):</strong> Mua tại nền hỗ trợ khi có nến Test Cung (Vol cạn kiệt 30%-50% MA20).</div>
                        <div>• <strong>Nhịp 2 (40% Gia tăng):</strong> Giải ngân khi giá vượt đỉnh Pivot kèm Vol &ge; 150% MA20.</div>
                        <div>• <strong>Nhịp 3 (30% Hoàn tất):</strong> Gia tăng khi cổ phiếu Retest đỉnh thành công.</div>
                        <div style="color: #ef4444; margin-top: 10px; font-weight: 700;">• Ngưỡng cắt lỗ cứng: Khóa cứng Stop Loss 2xATR &le; 7.5% NAV.</div>
                    </div>
                </div>
            </div>

            {wr_portfolio_live_html}
        </section>


        <!-- ========================================================
             TAB 3: PHÒNG TÁC CHIẾN ĐẦU TƯ TRONG NGÀY (MINH QUÂN & VICTOR)
             ======================================================== -->
        <!-- ========================================================
             TAB 3: PHÒNG TÁC CHIẾN ĐẦU TƯ TRONG NGÀY (MINH QUÂN & VICTOR)
             ======================================================== -->
        <!-- ========================================================
             TAB 3: PHÒNG TÁC CHIẾN ĐẦU TƯ TRONG NGÀY (MINH QUÂN & VICTOR)
             ======================================================== -->
        <section id="tab-war-room" class="tab-pane">
            <div class="war-room-wrap">
                <!-- TOP RIBBON: MARKET PHASE & REALTIME CLOCKS -->
                <div class="war-room-ribbon">
                    <div class="war-room-ribbon-top">
                        <div class="war-room-title-box">
                            <span class="war-room-live-pulse"><span class="war-room-live-dot"></span> TRỰC CHIẾN LIVE</span>
                            <div>
                                <div class="war-room-title">⚡ PHÒNG TÁC CHIẾN ĐẦU TƯ TRONG NGÀY (APEX DAILY TACTICAL WAR-ROOM)</div>
                                <div class="war-room-subtitle">Chủ tịch: <strong>Trần Quốc Thiên Phước</strong> (TCBS: <code>105C307855</code>) | Trực chiến: <strong>Minh Quân</strong> (Ban 7 VN) &amp; <strong>Victor</strong> (Ban 9 Live Sentinel) | Standby: <strong>Alex</strong> (Ban 7 US)</div>
                            </div>
                        </div>
                        <div class="war-room-meta-group">
                            <div class="meta-pill">📅 Ngày: <strong>{today_str}</strong></div>
                            <div class="meta-pill">⏰ Giờ VN: <strong id="war-room-clock" style="color: #38bdf8; font-family: monospace;">{wr_server_time}</strong></div>
                            <div class="meta-pill" id="wr-stream-status-badge" style="border-color: rgba(56, 189, 248, 0.4); background: rgba(14, 165, 233, 0.12); color: #38bdf8;">🟡 ĐANG KẾT NỐI...</div>
                            <div class="meta-pill" id="wr-regime-pill" style="border-color: rgba(251, 191, 36, 0.4); background: rgba(245, 158, 11, 0.1); color: {wr_mkt_ui['regime_color']};">{wr_mkt_ui['regime_label']}</div>
                            <div class="meta-pill" id="wr-header-cash-pill" style="border-color: rgba(16, 185, 129, 0.4); background: rgba(16, 185, 129, 0.1);">💰 Két Tiền Thật: <strong style="color: #34d399;">{ssot['cash_str']}</strong> ({ssot['cash_pct']:.1f}% Cash) | 📈 Cổ Phiếu: <strong style="color: #38bdf8;">{ssot['stocks_str']}</strong> ({ssot['total_shares']} CP)</div>
                            <div class="meta-pill" style="border-color: rgba(245, 158, 11, 0.4); background: rgba(245, 158, 11, 0.1);">🗽 Phiên New York (21h30): <strong id="war-room-ny-countdown" style="color: #fbbf24;">{wr_ny_countdown}</strong></div>
                            <button onclick="loadTacticalWarRoomData()" class="btn-quick-prompt" style="background: rgba(14, 165, 233, 0.25); border-color: #38bdf8; color: #f8fafc; font-weight: 800; padding: 6px 12px;">🔄 Làm Mới Live</button>
                        </div>
                    </div>

                    <!-- 8-PHASE STEPPER (DYNAMIC ACTIVE STATE) -->
                    <div class="phase-stepper-wrap" id="war-room-phase-stepper">
                        <div class="phase-step-card {'active' if wr_phase_id == 'PRE_ATO' else ''}" id="step-PRE_ATO">
                            <div class="phase-card-header"><span>PHASE 1</span><span>08:30-09:00</span></div>
                            <div class="phase-card-name">📋 Pre-ATO Giao Ban</div>
                            <div class="phase-card-time">Sổ Lệnh Master</div>
                        </div>
                        <div class="phase-step-card {'active' if wr_phase_id == 'ATO_OPEN' else ''}" id="step-ATO_OPEN">
                            <div class="phase-card-header"><span>PHASE 2</span><span>09:00-09:15</span></div>
                            <div class="phase-card-name">🛑 Mở Cửa ATO</div>
                            <div class="phase-card-time">Không Đua Lệnh</div>
                        </div>
                        <div class="phase-step-card {'active' if wr_phase_id == 'MORNING_CONTINUOUS' else ''}" id="step-MORNING_CONTINUOUS">
                            <div class="phase-card-header"><span style="color:#38bdf8;">PHASE 3</span><span>09:15-11:30</span></div>
                            <div class="phase-card-name">📈 Phiên Sáng</div>
                            <div class="phase-card-time">Đo Lực Mua Chủ Động</div>
                        </div>
                        <div class="phase-step-card {'active' if wr_phase_id == 'NOON_INTERMISSION' else ''}" id="step-NOON_INTERMISSION">
                            <div class="phase-card-header"><span style="color:#fbbf24;">PHASE 4 ●</span><span>11:30-13:00</span></div>
                            <div class="phase-card-name" style="color:#fbbf24;">☕ Nghỉ Trưa &amp; Hội Ý</div>
                            <div class="phase-card-time">Đối Soát Khối Ngoại</div>
                        </div>
                        <div class="phase-step-card {'active' if wr_phase_id == 'T2_ABSORPTION' else ''}" id="step-T2_ABSORPTION">
                            <div class="phase-card-header"><span>PHASE 5</span><span>13:00-14:00</span></div>
                            <div class="phase-card-name">⏳ Hấp Thụ T+2</div>
                            <div class="phase-card-time">Quan Sát Rũ Cung</div>
                        </div>
                        <div class="phase-step-card {'active' if wr_phase_id == 'GOLDEN_WINDOW' else ''}" id="step-GOLDEN_WINDOW" style="border-color: rgba(245, 158, 11, 0.5);">
                            <div class="phase-card-header"><span style="color:#fbbf24;">⭐ PHASE 6</span><span>14:00-14:25</span></div>
                            <div class="phase-card-name" style="color:#fbbf24;">🎯 Khung Giờ Vàng</div>
                            <div class="phase-card-time">Bấm Cò Nhịp 1</div>
                        </div>
                        <div class="phase-step-card {'active' if wr_phase_id == 'ATC_CLOSING' else ''}" id="step-ATC_CLOSING">
                            <div class="phase-card-header"><span>PHASE 7</span><span>14:30-14:45</span></div>
                            <div class="phase-card-name">🏁 Đóng Cửa ATC</div>
                            <div class="phase-card-time">Đối Soát Nến Ngày</div>
                        </div>
                        <div class="phase-step-card {'active' if wr_phase_id == 'POST_MARKET_WALL_STREET' else ''}" id="step-POST_MARKET_WALL_STREET">
                            <div class="phase-card-header"><span>PHASE 8</span><span>14:45-24:00</span></div>
                            <div class="phase-card-name">🗽 Phố Wall Ca Tối</div>
                            <div class="phase-card-time">Chuyển Giao Alex</div>
                        </div>
                    </div>
                </div>

                <!-- ========================================================
                     BẢNG KẾ HOẠCH TÁC CHIẾN TUẦN (ĐỊNH HƯỚNG THAM KHẢO CHO CHỦ TỊCH)
                     CĂN CỨ: NGHỊ QUYẾT ĐẠI HỘI NGHỊ THƯỢNG ĐỈNH (APEX-SUMMIT-20261108-2100)
                     ======================================================== -->
                <div class="weekly-roadmap-box" id="weekly-roadmap-box" style="margin-bottom: 20px; background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.85)); border: 1.5px solid rgba(245, 158, 11, 0.45); border-radius: 14px; padding: 18px 20px; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 12px;">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <span style="font-size: 22px;">📅</span>
                            <div>
                                <div style="font-size: 15px; font-weight: 800; color: #fbbf24; display: flex; align-items: center; gap: 8px;">
                                    <span>BẢNG KẾ HOẠCH TÁC CHIẾN TUẦN (ĐỊNH HƯỚNG THAM KHẢO CHO CHỦ TỊCH)</span>
                                    <span id="weekly-roadmap-label" style="background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.4); padding: 2px 8px; border-radius: 9999px; font-size: 10.5px; font-weight: 800;">{wr_weekly_ui['week_label']}</span>
                                </div>
                                <div id="weekly-roadmap-basis" style="font-size: 11.5px; color: #94a3b8; margin-top: 2px;">
                                    {wr_weekly_ui['basis_html']}
                                </div>
                            </div>
                        </div>
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span style="background: rgba(14, 165, 233, 0.15); color: #38bdf8; border: 1px solid rgba(14, 165, 233, 0.3); padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700;">
                                💡 Dành Riêng Cho Chủ Tịch Tham Khảo
                            </span>
                            <button id="btn-toggle-weekly-roadmap" onclick="toggleWeeklyRoadmap()" style="background: rgba(255, 255, 255, 0.08); border: 1px solid rgba(255, 255, 255, 0.15); color: #cbd5e1; font-size: 11.5px; font-weight: 700; padding: 5px 12px; border-radius: 6px; cursor: pointer;">
                                ▾ Thu Gọn
                            </button>
                        </div>
                    </div>

                    <div id="weekly-roadmap-mandate" style="background: rgba(245, 158, 11, 0.08); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 8px; padding: 10px 14px; margin-bottom: 14px; font-size: 11.5px; color: #fde68a; line-height: 1.55;">
                        {wr_weekly_ui['mandate_html']}
                    </div>

                    <div id="weekly-roadmap-details">
                        <div id="weekly-roadmap-days-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 10px; margin-bottom: 14px;">
                            {wr_weekly_ui['days_html']}
                        </div>

                        <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(148, 163, 184, 0.15); border-radius: 8px; padding: 10px 14px;">
                            <div style="font-size: 11px; font-weight: 800; color: #38bdf8; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                                <span>🎯 RỔ CỔ PHIẾU ĐỊNH HƯỚNG &amp; ĐỒNG BỘ LIVE</span>
                                <span style="font-size: 10.5px; color: #94a3b8;">Vùng Gom LO • Stop 2xATR • Trạng thái Holding thực tế</span>
                            </div>
                            <table class="stock-sentinel-table" style="font-size: 11px;">
                                <thead>
                                    <tr>
                                        <th>Mã CP</th>
                                        <th>Phân Tầng</th>
                                        <th>Vùng Gom LO</th>
                                        <th>Stop 2xATR</th>
                                        <th>Mục Tiêu TP1 / TP2</th>
                                        <th>Hạn Mức Tuần</th>
                                        <th>Trạng Thái Thực Tế</th>
                                    </tr>
                                </thead>
                                <tbody id="weekly-roadmap-watchlist-body">
                                    {wr_weekly_ui['watchlist_rows']}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- 3 COLUMNS TACTICAL COMMAND -->
                <div class="war-room-columns">
                    <!-- ================= CỘT 1: MINH QUÂN BLUEPRINT ================= -->
                    <div class="tactical-panel">
                        <div class="panel-header">
                            <div class="panel-title-box">
                                <span class="panel-icon">👨‍💼</span>
                                <div>
                                    <div class="panel-title">Kế Hoạch Sống Trong Ngày</div>
                                    <div style="font-size: 11px; color: #94a3b8;">Minh Quân (Ban 7 VN) • Tự tiến hóa theo Bảng điện</div>
                                </div>
                            </div>
                            <div id="mq-mastery-badge" class="panel-badge" style="background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4);">Mastery: {wr_mkt_ui['mastery_str']}/100</div>
                        </div>

                        <!-- Stats Bar Minh Quân -->
                        <div id="minh-quan-stats-bar" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; background: rgba(30, 41, 59, 0.5); padding: 8px 10px; border-radius: 8px; border: 1px solid rgba(148, 163, 184, 0.15);">
                            <div style="display: flex; flex-direction: column; align-items: center;">
                                <span style="font-size: 10px; color: #94a3b8;">Kỳ Vọng Toán Học</span>
                                <strong id="mq-ev-val" style="font-size: 13px; color: #34d399;">EV% {wr_mkt_ui['ev_str']}</strong>
                            </div>
                            <div style="display: flex; flex-direction: column; align-items: center; border-left: 1px solid rgba(148, 163, 184, 0.15); border-right: 1px solid rgba(148, 163, 184, 0.15);">
                                <span style="font-size: 10px; color: #94a3b8;">Tỷ Lệ Thắng TB</span>
                                <strong id="mq-pw-val" style="font-size: 13px; color: #38bdf8;">P(W) {wr_mkt_ui['pw_str']}</strong>
                            </div>
                            <div style="display: flex; flex-direction: column; align-items: center;">
                                <span style="font-size: 10px; color: #94a3b8;">Risk / Reward</span>
                                <strong id="mq-rr-val" style="font-size: 13px; color: #fbbf24;">R:R {wr_mkt_ui['rr_str']}</strong>
                            </div>
                        </div>

                        <!-- Dynamic Picks Cards -->
                        <div style="display: flex; flex-direction: column; gap: 10px;" id="war-room-picks-container">
                            {wr_picks_html}
                        </div>

                        <!-- 3 KHÔNG & REGIME RULES -->
                        <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.25); border-radius: 8px; padding: 10px 12px; display: flex; flex-direction: column; gap: 4px;">
                            <div style="font-size: 11px; font-weight: 800; color: #f87171;">🛡️ QUY TẮC KỶ LUẬT SẮT MINH QUÂN:</div>
                            <div id="mq-rules-list" style="display: flex; flex-direction: column; gap: 4px;">
                                {wr_mkt_ui['rules_html']}
                            </div>
                        </div>

                        <!-- Button Full Live Report -->
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                            <button onclick="openReportModal('VN_Market/07_Daily_Specialist/{today_str}_Live_Intraday_Report.md')" class="btn-read" style="background: rgba(16, 185, 129, 0.2); border: 1px solid #10b981; color: #34d399; font-weight: 800; padding: 8px; text-align: center; border-radius: 6px; cursor: pointer;">
                                ⚡ Báo Cáo Sống Realtime
                            </button>
                            <button onclick="openReportModal('VN_Market/07_Daily_Specialist/{today_str}_VN_Specialist_Decision.md')" class="btn-read" style="background: rgba(14, 165, 233, 0.2); border: 1px solid #38bdf8; color: #38bdf8; font-weight: 800; padding: 8px; text-align: center; border-radius: 6px; cursor: pointer;">
                                📖 Sổ Lệnh Đầu Ngày
                            </button>
                        </div>
                    </div>

                    <!-- ================= CỘT 2: BÁO CÁO TÁC CHIẾN TRONG NGÀY (3 GIAI ĐOẠN QUYẾT ĐỊNH) ================= -->
                    <div class="tactical-panel">
                        <div class="panel-header">
                            <div class="panel-title-box">
                                <span class="panel-icon">📋</span>
                                <div>
                                    <div class="panel-title">Báo Cáo Tác Chiến Trong Ngày</div>
                                    <div style="font-size: 11px; color: #94a3b8;">Lộ trình Các Giai Đoạn Tác Chiến Theo Khung Giờ Realtime</div>
                                </div>
                            </div>
                            <span class="war-room-live-pulse" style="background: rgba(56, 189, 248, 0.15); color: #38bdf8; border-color: rgba(56, 189, 248, 0.4);"><span class="war-room-live-dot" style="background: #38bdf8;"></span> REALTIME</span>
                        </div>

                        <!-- DYNAMIC REALTIME TACTICAL STAGES -->
{wr_stages_html}

                        <!-- Current Directive Hero Box -->
                        <div class="directive-hero-box" style="margin-top: 8px;">
                            <span style="font-size: 20px;">📢</span>
                            <div>
                                <div style="font-size: 11px; font-weight: 800; color: #34d399; margin-bottom: 2px;">THÔNG ĐIỆP CHỈ ĐẠO CỦA MINH QUÂN HIỆN TẠI:</div>
                                <div class="directive-hero-text" id="war-room-live-directive-box">
                                    {wr_message}
                                </div>
                            </div>
                        </div>

                        <!-- INTERACTIVE DIRECTIVE DESK FOR CHAIRMAN -->
                        <div class="tactical-interactive-card">
                            <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid rgba(148, 163, 184, 0.15); padding-bottom: 6px;">
                                <div style="font-size: 12px; font-weight: 800; color: #fbbf24; display: flex; align-items: center; gap: 6px;">
                                    <span>👑</span> BÀN RA CHỈ LỆNH TRỰC TIẾP CỦA CHỦ TỊCH
                                </div>
                                <span style="font-size: 10.5px; color: #94a3b8;">Minh Quân &amp; Victor &amp; Hook Ban 9/10</span>
                            </div>

                            <!-- History Box -->
                            <div class="directive-history-box" id="directive-history-box">
                                {wr_directives_html}
                            </div>

                            <!-- Quick Prompts -->
                            <div class="quick-prompts-row">
                                <button class="btn-quick-prompt" onclick="sendQuickTactical('Minh Quân báo cáo tiến độ hiện tại')">💬 Báo cáo tiến độ</button>
                                <button class="btn-quick-prompt" onclick="sendQuickTactical('Cho tôi xem kế hoạch tuần')" style="border-color: #fbbf24; color: #fbbf24; font-weight: 700;">📅 Soi Kế Hoạch Tuần</button>
                                <button class="btn-quick-prompt" onclick="sendQuickTactical('Soi giá live HDB và MSH')">🎯 Soi HDB &amp; MSH</button>
                                <button class="btn-quick-prompt" onclick="sendQuickTactical('Kịch bản ứng phó nếu thị trường bất ngờ sập 15 điểm')">🛡️ Kịch bản thị trường sập</button>
                                <button class="btn-quick-prompt" onclick="sendQuickTactical('Victor kiểm tra két tiền mặt SSOT và sức mua')">💰 Két tiền &amp; Sức mua</button>
                            </div>

                            <!-- Input Row -->
                            <div class="directive-input-row">
                                <input type="text" id="tactical-cmd-input" class="directive-input" placeholder="Kính gửi Chủ tịch, gõ câu hỏi hoặc chỉ thị cho Minh Quân &amp; Victor tại đây..." onkeydown="if(event.key==='Enter') sendTacticalCommand()">
                                <button id="btn-send-tactical" class="btn-send-directive" onclick="sendTacticalCommand()">⚡ Gửi Chỉ Lệnh</button>
                            </div>
                        </div>
                    </div>

                    <!-- ================= CỘT 3: VICTOR SENTINEL & LIVE STOCKS ================= -->
                    <div class="tactical-panel">
                        <!-- VICTOR SENTINEL -->
                        <div class="panel-header">
                            <div class="panel-title-box">
                                <span class="panel-icon">🛡️</span>
                                <div>
                                    <div class="panel-title">Victor Live Portfolio Sentinel</div>
                                    <div style="font-size: 11px; color: #94a3b8;">Ban 9 — Giám Sát Realtime &amp; Ứng Phó Khẩn Cấp</div>
                                </div>
                            </div>
                            <span class="panel-badge" style="background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4);">24/7 ACTIVE</span>
                        </div>

                        <!-- SSOT Cash & Portfolio Status -->
                        <div id="victor-ssot-cash-card" style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.12), rgba(15, 23, 42, 0.9)); border: 1px solid rgba(52, 211, 153, 0.35); border-radius: 9px; padding: 12px; display: flex; flex-direction: column; gap: 6px;">
                            <div style="font-size: 11px; color: #94a3b8; display: flex; justify-content: space-between;">
                                <span>TÀI KHOẢN TCBS: <strong>105C307855</strong></span>
                                <span style="color: #34d399; font-weight: 800;">SSOT V4.0 LIVE</span>
                            </div>
                            <div style="display: flex; align-items: baseline; justify-content: space-between;">
                                <span style="font-size: 11px; color: #cbd5e1;">Két Tiền Mặt Thật:</span>
                                <strong id="victor-cash-val" style="font-size: 19px; color: #34d399; font-family: monospace;">{ssot['cash_str']}</strong>
                            </div>
                            <div style="display: flex; justify-content: space-between; font-size: 11px; border-top: 1px solid rgba(148, 163, 184, 0.15); padding-top: 5px; gap: 6px; flex-wrap: wrap;">
                                <span id="victor-holdings-val" style="color: #94a3b8;">Cổ phiếu rủi ro: <strong style="color: #38bdf8;">{ssot['total_shares']} CP ({ssot['stocks_str']} • {ssot['stocks_pct']:.1f}%)</strong></span>
                                <span id="victor-pnl-val" style="color: #94a3b8;">PnL Tạm: <strong style="color: {unrealized_color};">{ssot['unrealized_str']} ({ssot['unrealized_pct']}%)</strong> | Lãi V1: <strong style="color: #34d399;">{ssot['realized_str']}</strong></span>
                            </div>
                        </div>

                        <!-- LIVE HOLDINGS CARD -->
                        <div id="victor-live-holdings-box" style="background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(56, 189, 248, 0.35); border-radius: 9px; padding: 10px; display: flex; flex-direction: column; gap: 6px;">
                            {wr_holdings_html}
                        </div>

                        <!-- 1-CLICK SYNC TCINVEST FORM -->
                        <div style="background: rgba(30, 41, 59, 0.55); border: 1px solid rgba(251, 191, 36, 0.3); border-radius: 9px; padding: 9px 10px; display: flex; flex-direction: column; gap: 6px;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="font-size: 11px; font-weight: 800; color: #fbbf24;">⚡ 1-CLICK SYNC TCINVEST (CẬP NHẬT LỆNH KHỚP)</span>
                                <button type="button" onclick="toggleSyncTCInvest()" id="btn-toggle-sync-tcinvest" style="background: rgba(245, 158, 11, 0.2); border: 1px solid rgba(245, 158, 11, 0.4); color: #fbbf24; font-size: 10px; font-weight: 800; padding: 2px 8px; border-radius: 4px; cursor: pointer;">▾ Mở Form</button>
                            </div>
                            <div id="sync-tcinvest-panel" style="display: none; flex-direction: column; gap: 6px; padding-top: 4px; border-top: 1px solid rgba(148, 163, 184, 0.15);">
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px;">
                                    <select id="sync-tc-action" onchange="onSyncActionChange()" style="background: #0f172a; color: #f8fafc; border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 5px; padding: 5px; font-size: 11px;">
                                        <option value="BUY">MUA KHỚP (BUY)</option>
                                        <option value="SELL">BÁN KHỚP (SELL)</option>
                                        <option value="RECONCILE">ĐỐI SOÁT KÉT / STOP</option>
                                    </select>
                                    <input id="sync-tc-symbol" type="text" placeholder="Mã CP (vd: HDB)" style="background: #0f172a; color: #f8fafc; border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 5px; padding: 5px; font-size: 11px; text-transform: uppercase;">
                                </div>
                                <div id="sync-tc-order-fields" style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px;">
                                    <input id="sync-tc-shares" type="number" step="100" min="0" placeholder="Số CP (vd: 100)" style="background: #0f172a; color: #f8fafc; border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 5px; padding: 5px; font-size: 11px;">
                                    <input id="sync-tc-price" type="number" step="50" min="0" placeholder="Giá khớp (vd: 22600)" style="background: #0f172a; color: #f8fafc; border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 5px; padding: 5px; font-size: 11px;">
                                </div>
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px;">
                                    <input id="sync-tc-stop" type="number" step="50" min="0" placeholder="Stop Loss (tùy chọn)" style="background: #0f172a; color: #f8fafc; border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 5px; padding: 5px; font-size: 11px;">
                                    <input id="sync-tc-cash" type="number" step="1000" min="0" placeholder="Tiền mặt thực (Reconcile)" style="display: none; background: #0f172a; color: #f8fafc; border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 5px; padding: 5px; font-size: 11px;">
                                    <input id="sync-tc-tp1" type="number" step="50" min="0" placeholder="TP1 (tùy chọn)" style="background: #0f172a; color: #f8fafc; border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 5px; padding: 5px; font-size: 11px;">
                                </div>
                                <button type="button" id="btn-submit-sync-tc" onclick="submitSyncTCInvest()" style="background: linear-gradient(135deg, #f59e0b, #d97706); color: #0f172a; font-weight: 900; border: none; border-radius: 6px; padding: 6px 10px; font-size: 11px; cursor: pointer;">⚡ Đồng Bộ Ngay Vào SSOT &amp; War-Room</button>
                                <div id="sync-tcinvest-status" style="font-size: 10.5px; color: #94a3b8;"></div>
                            </div>
                        </div>

                        <!-- LIVE MARKET OVERVIEW (VN-INDEX & VN30) -->
                        <div class="market-radar-card" id="market-radar-card">
                            <div style="font-size: 11px; font-weight: 800; color: #38bdf8; display: flex; justify-content: space-between; gap: 6px;">
                                <span>📊 GIÁM SÁT THỊ TRƯỜNG REALTIME</span>
                                <span style="color: {wr_mkt_ui['vni_col']};" id="market-status-badge">● {wr_mkt_ui['status_str']}</span>
                            </div>
                            <div class="index-grid">
                                <div class="index-item">
                                    <div style="display:flex; justify-content:space-between; font-size:10px; color:#94a3b8;">
                                        <span>VN-INDEX</span>
                                        <span class="price-badge {wr_mkt_ui['vni_cls']}" id="vnindex-pts">{wr_mkt_ui['vni_pts_str']}</span>
                                    </div>
                                    <div style="font-size:15px; font-weight:900; color:{wr_mkt_ui['vni_col']};" id="vnindex-val">{wr_mkt_ui['vni_val_str']}</div>
                                    <div style="font-size:10px; color:#94a3b8;">GTGD: <strong id="vnindex-turnover">{wr_mkt_ui['turnover_str']}</strong></div>
                                </div>
                                <div class="index-item">
                                    <div style="display:flex; justify-content:space-between; font-size:10px; color:#94a3b8;">
                                        <span>VN30-INDEX</span>
                                        <span class="price-badge {wr_mkt_ui['vn30_cls']}" id="vn30-pts">{wr_mkt_ui['vn30_pts_str']}</span>
                                    </div>
                                    <div style="font-size:15px; font-weight:900; color:{wr_mkt_ui['vn30_col']};" id="vn30-val">{wr_mkt_ui['vn30_val_str']}</div>
                                    <div style="font-size:10px; color:#94a3b8;">Basis F1M: <strong id="vn30-basis">{wr_mkt_ui['basis_str']}</strong></div>
                                </div>
                            </div>
                            <div style="font-size:10.5px; color:#cbd5e1; display:flex; justify-content:space-between; border-top:1px solid rgba(148,163,184,0.15); padding-top:4px; gap: 6px;">
                                <span>Khối ngoại: <strong style="color:#34d399;" id="foreign-net">{wr_mkt_ui['foreign_str']}</strong></span>
                                <span>Độ rộng: <strong style="color:#e2e8f0;" id="market-breadth-val">{wr_mkt_ui['breadth_str']}</strong></span>
                            </div>
                        </div>

                        <!-- LIVE STOCK TICKER SENTINEL TABLE -->
                        <div style="display: flex; flex-direction: column; gap: 6px;">
                            <div style="font-size: 11.5px; font-weight: 800; color: #f8fafc; display: flex; justify-content: space-between; align-items: center;">
                                <span id="war-room-table-title">🎯 BẢNG GIÁ GIÁM SÁT LIVE ({wr_stocks_count} MÃ SSOT)</span>
                                <span style="font-size: 10px; color: #38bdf8;">VPS Orderbook 3 bước</span>
                            </div>
                            <table class="stock-sentinel-table">
                                <thead>
                                    <tr>
                                        <th>Mã CP</th>
                                        <th>Giá Live</th>
                                        <th>+/- %</th>
                                        <th>Volume</th>
                                        <th>Buy Up</th>
                                        <th>Trạng Thái</th>
                                    </tr>
                                </thead>
                                <tbody id="live-stocks-table-body">
                                    {wr_stocks_rows_html}
                                </tbody>
                            </table>
                        </div>

                        <!-- Radar 5 Cấp Độ An Ninh -->
                        <div id="victor-threat-radar-card" style="background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 8px; padding: 9px; display: flex; flex-direction: column; gap: 5px;">
                            {wr_threat_html}
                        </div>

                        <!-- ALEX WALL STREET DESK (STANDBY SLOT) -->
                        <div style="background: linear-gradient(135deg, rgba(245, 158, 11, 0.12), rgba(15, 23, 42, 0.9)); border: 1px solid rgba(245, 158, 11, 0.35); border-radius: 9px; padding: 11px; display: flex; flex-direction: column; gap: 6px;">
                            <div style="display: flex; align-items: center; justify-content: space-between;">
                                <div style="display: flex; align-items: center; gap: 6px;">
                                    <span style="font-size: 15px;">🗽</span>
                                    <span style="font-size: 11.5px; font-weight: 800; color: #fbbf24;">Alex — Cầu Nối Phố Wall &amp; Bull-Trap Guard</span>
                                </div>
                                <span style="font-size: 10px; font-weight: 800; color: #38bdf8; background: rgba(56, 189, 248, 0.16); padding: 2px 6px; border-radius: 4px;">SPILLOVER V2</span>
                            </div>
                            <div style="font-size: 10.5px; color: #cbd5e1;">
                                Phiên New York mở lúc <strong>21:30 Tối</strong> (Còn: <strong id="alex-ny-countdown" style="color: #fbbf24;">{wr_ny_countdown}</strong>).
                            </div>
                            <div id="wr-spillover-slippage-box" style="display: flex; flex-direction: column; gap: 5px;">
                                {wr_spillover_html}
                            </div>
                        </div>
                    </div>
                </div>

                <!-- V5.0 OMNI-MARKET INTELLIGENCE, DEEP FINANCIAL BRAIN & 15 LEGENDS PANEL -->
                <div id="wr-omni-brain-panel" style="margin-top: 14px; background: linear-gradient(135deg, rgba(15, 23, 42, 0.96), rgba(30, 41, 59, 0.92)); border: 1px solid rgba(56, 189, 248, 0.35); border-radius: 12px; padding: 14px; display: flex; flex-direction: column; gap: 12px;">
                    <div style="display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 8px; border-bottom: 1px solid rgba(148, 163, 184, 0.2); padding-bottom: 8px;">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span style="font-size: 18px;">🧠</span>
                            <div>
                                <div style="font-size: 13px; font-weight: 900; color: #f8fafc;">TRUNG TÂM TÌNH BÁO THỊ TRƯỜNG, BỘ NÃO BCTC &amp; 15 HUYỀN THOẠI ĐẦU TƯ (V5.0)</div>
                                <div style="font-size: 10.5px; color: #94a3b8;">Cào dữ liệu 180 mã VN/US thời gian thực • Định giá 3 mô hình &amp; Half-Kelly EV% • Tự kiểm điểm sai lầm &amp; Maturity IQ</div>
                            </div>
                        </div>
                        <div style="display: flex; gap: 8px; align-items: center;">
                            <span id="omni-crawler-badge" style="font-size: 10.5px; font-weight: 800; color: #38bdf8; background: rgba(56, 189, 248, 0.14); border: 1px solid rgba(56, 189, 248, 0.35); padding: 4px 8px; border-radius: 6px;">📡 Crawler: 180 mã sẵn sàng</span>
                            <span id="omni-maturity-badge" style="font-size: 10.5px; font-weight: 800; color: #34d399; background: rgba(16, 185, 129, 0.14); border: 1px solid rgba(16, 185, 129, 0.35); padding: 4px 8px; border-radius: 6px;">🎓 Maturity IQ: Đang tải...</span>
                        </div>
                    </div>

                    <div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: center;">
                        <input type="text" id="omni-search-input" placeholder="Tìm mã CP (HDB, MSH, BAF, NVDA...), tin CBTT, BCTC hoặc từ khóa vĩ mô..." onkeydown="if(event.key==='Enter') runOmniIntelSearch();" style="flex: 1; min-width: 240px; padding: 8px 12px; border-radius: 8px; border: 1px solid rgba(56, 189, 248, 0.4); background: rgba(15, 23, 42, 0.9); color: #f8fafc; font-size: 12px; outline: none;">
                        <button onclick="runOmniIntelSearch()" style="padding: 8px 14px; border-radius: 8px; border: 1px solid #38bdf8; background: rgba(14, 165, 233, 0.25); color: #f8fafc; font-weight: 800; font-size: 11.5px; cursor: pointer;">🔍 Tìm Kiếm Toàn Thị Trường</button>
                        <button id="btn-omni-crawl" onclick="triggerOmniCrawlLive()" style="padding: 8px 14px; border-radius: 8px; border: 1px solid #10b981; background: rgba(16, 185, 129, 0.2); color: #34d399; font-weight: 800; font-size: 11.5px; cursor: pointer;">📡 Cào Dữ Liệu Live Ngay</button>
                    </div>

                    <div id="omni-search-results" style="display: none; background: rgba(15, 23, 42, 0.78); border: 1px solid rgba(148, 163, 184, 0.22); border-radius: 8px; padding: 10px; font-size: 11px; color: #e2e8f0; max-height: 260px; overflow-y: auto;"></div>

                    <div id="wr-omni-catalyst-strip" style="display: flex; flex-wrap: wrap; gap: 6px; align-items: center; background: rgba(15, 23, 42, 0.68); border: 1px solid rgba(251, 191, 36, 0.28); border-radius: 8px; padding: 7px 10px; font-size: 10.5px; color: #e2e8f0;">
                        ⚡ Đang tải Radar Catalyst, BCTC Quý Mới &amp; Chốt Chặn Tương Quan 60D...
                    </div>

                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); gap: 12px;">
                        <div style="background: rgba(15, 23, 42, 0.72); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 9px; padding: 11px; display: flex; flex-direction: column; gap: 8px;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="font-size: 11.5px; font-weight: 800; color: #fbbf24;">💎 TOP ALPHA BCTC &amp; TỐI ƯU LỢI NHUẬN (EV% &amp; HALF-KELLY)</span>
                                <span style="font-size: 10px; color: #94a3b8;">Nhấn mã để soi Pháp y BCTC</span>
                            </div>
                            <div style="overflow-x: auto;">
                                <table class="stock-sentinel-table" style="width: 100%; font-size: 11px;">
                                    <thead>
                                        <tr>
                                            <th>Mã CP</th>
                                            <th>Giá Live</th>
                                            <th>Alpha</th>
                                            <th>MOS%</th>
                                            <th>EV%</th>
                                            <th>R:R</th>
                                            <th>Corr 60D</th>
                                            <th>Lô 100 / Tín Hiệu</th>
                                        </tr>
                                    </thead>
                                    <tbody id="omni-alpha-picks-body">
                                        <tr><td colspan="8" style="color:#94a3b8; text-align:center;">Đang nạp dữ liệu Deep Brain...</td></tr>
                                    </tbody>
                                </table>
                            </div>
                            <div id="omni-deep-ticker-detail" style="display: none; background: rgba(30, 41, 59, 0.85); border: 1px solid rgba(251, 191, 36, 0.35); border-radius: 8px; padding: 9px; font-size: 11px; color: #e2e8f0;"></div>
                        </div>

                        <div style="background: rgba(15, 23, 42, 0.72); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 9px; padding: 11px; display: flex; flex-direction: column; gap: 8px;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="font-size: 11.5px; font-weight: 800; color: #34d399;">🏛️ TỰ ĐÁNH GIÁ IQ &amp; HỘI ĐỒNG 15 HUYỀN THOẠI THẾ GIỚI</span>
                                <span style="font-size: 10px; color: #94a3b8;">5 Trường Phái • 105 Tinh Hoa</span>
                            </div>
                            <div id="omni-maturity-metrics" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; font-size: 10.5px;"></div>
                            <div id="omni-walk-forward-strip" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; font-size: 10px;"></div>
                            <div id="omni-legends-cards" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(175px, 1fr)); gap: 7px;"></div>
                        </div>
                    </div>
                </div>
            </div>

        {wr_v8_floor_html}

        <!-- V7.0: LIVING ENTERPRISE & INTER-DEPARTMENTAL COLLABORATION MESH -->
        <div id="wr-enterprise-mesh-panel" class="war-room-section" style="margin-top: 14px; background: linear-gradient(135deg, rgba(15, 23, 42, 0.96), rgba(30, 41, 59, 0.92)); border: 1px solid rgba(56, 189, 248, 0.35); border-radius: 12px; padding: 14px;">
            <div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 10px; margin-bottom: 10px;">
                <div>
                    <div style="font-size: 13.5px; font-weight: 900; color: #38bdf8; letter-spacing: 0.3px;">
                        🏛️ BÀN LÀM VIỆC DOANH NGHIỆP SỐNG &amp; TRANH BIỆN ĐA PHÒNG BAN (V7.0)
                    </div>
                    <div style="font-size: 11px; color: #94a3b8; margin-top: 2px;">
                        14 Thực Thể Độc Lập • Trao Đổi Gói Số Liệu Thực • Biểu Quyết VETO Hiến Chương &amp; Niêm Phong Trọng Ban 12
                    </div>
                </div>
                <div style="display: flex; flex-wrap: wrap; gap: 6px; align-items: center;">
                    <span id="enterprise-mesh-badge" style="font-size: 10.5px; background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.45); color: #34d399; padding: 4px 8px; border-radius: 6px; font-weight: 800;">Quorum 14/14 • Audit 10/10</span>
                    <input id="enterprise-ticker-input" type="text" placeholder="Mã (VD: HDB, BAF, MWG)" style="width: 140px; padding: 5px 8px; font-size: 11px; background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(148, 163, 184, 0.35); border-radius: 6px; color: #f8fafc;" />
                    <input id="enterprise-directive-input" type="text" placeholder="Chỉ thị họp liên phòng ban..." style="width: 220px; padding: 5px 8px; font-size: 11px; background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(148, 163, 184, 0.35); border-radius: 6px; color: #f8fafc;" />
                    <button id="enterprise-convene-btn" onclick="conveneEnterpriseMesh()" style="cursor: pointer; background: linear-gradient(90deg, #0284c7, #2563eb); color: #fff; border: none; border-radius: 6px; padding: 5px 11px; font-size: 11px; font-weight: 800;">⚡ Triệu Tập Họp Thật</button>
                </div>
            </div>
            <div id="enterprise-verdict-banner" style="background: rgba(30, 41, 59, 0.72); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 8px; padding: 9px 11px; font-size: 11.5px; color: #e2e8f0; margin-bottom: 10px;">
                ⏳ Đang tải trạng thái đồng bộ Doanh Nghiệp Sống V7.0...
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 10px;">
                <div style="background: rgba(15, 23, 42, 0.72); border: 1px solid rgba(148, 163, 184, 0.22); border-radius: 8px; padding: 9px;">
                    <div style="font-size: 11.5px; font-weight: 800; color: #fbbf24; margin-bottom: 6px;">⚖️ Biểu Quyết Điểm Danh 14 Thực Thể (Roll-Call Vote)</div>
                    <div style="max-height: 250px; overflow-y: auto;">
                        <table style="width: 100%; border-collapse: collapse; font-size: 10.5px;">
                            <thead>
                                <tr style="color: #94a3b8; border-bottom: 1px solid rgba(148, 163, 184, 0.2); text-align: left;">
                                    <th style="padding: 4px;">Ban / Cán Bộ</th>
                                    <th style="padding: 4px;">Phiếu</th>
                                    <th style="padding: 4px;">Luận Điểm Định Lượng</th>
                                </tr>
                            </thead>
                            <tbody id="enterprise-roster-body"></tbody>
                        </table>
                    </div>
                </div>
                <div style="background: rgba(15, 23, 42, 0.72); border: 1px solid rgba(148, 163, 184, 0.22); border-radius: 8px; padding: 9px;">
                    <div style="font-size: 11.5px; font-weight: 800; color: #34d399; margin-bottom: 6px;">📡 Luồng Gói Dữ Liệu &amp; Tranh Biện Đối Kháng Liên Phòng Ban</div>
                    <div id="enterprise-debate-stream" style="max-height: 250px; overflow-y: auto; display: flex; flex-direction: column; gap: 6px; font-size: 10.5px;"></div>
                </div>
            </div>
        </div>
        </section>

        <!-- ========================================================
             TAB 4: BÀN CHỈ HUY MASTER CIO JAMES (SPLIT-VIEW 2 CỘT)
             ======================================================== -->
        <section id="tab-james-command" class="tab-pane">
            <div class="james-split-container">
                <!-- CỘT TRÁI (68%): LUỒNG TƯƠNG TÁC ĐIỀU HÀNH -->
                <div class="james-main-panel">
                    <!-- Header Panel -->
                    <div style="background: linear-gradient(135deg, #1e1b4b 0%, #172033 100%); border-bottom: 1px solid var(--border-color); padding: 18px 24px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
                        <div>
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <span style="font-size: 22px;">🎖️</span>
                                <h3 style="font-size: 17px; font-weight: 800; color: #fff;">TRUNG TÂM CHỈ HUY TÁC CHIẾN — MASTER CIO JAMES</h3>
                            </div>
                            <p style="font-size: 12.5px; color: var(--text-muted); margin-top: 4px;">
                                Kênh giao việc trực tiếp từ Chủ tịch Phước Trần • Tiếp nhận & đóng lặp thực thi qua 10 phòng ban thời gian thực
                            </p>
                        </div>
                        <div>
                            <span style="background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.35); padding: 5px 12px; border-radius: 9999px; font-size: 11px; font-weight: 700;">
                                ● ĐANG TRỰC CHIẾN 24/7
                            </span>
                        </div>
                    </div>

                    <!-- Quick Command Chips -->
                    <div style="background: var(--bg-card); border-bottom: 1px solid var(--border-color); padding: 12px 20px; display: flex; gap: 8px; flex-wrap: wrap; align-items: center;">
                        <span style="font-size: 11px; font-weight: 800; color: var(--text-dim); text-transform: uppercase;">Lệnh Nhanh:</span>
                        <button class="cmd-chip" onclick="sendQuickCommand('/tcbs')">🏦 /tcbs (Số Dư Thực Tế)</button>
                        <button class="cmd-chip" onclick="sendQuickCommand('/danhmuc')">📊 /danhmuc (Vị Thế &amp; Cash Live)</button>
                        <button class="cmd-chip" onclick="sendQuickCommand('/doanhnghiep')">🏛️ /doanhnghiep (Họp 14 Ban V7.0)</button>
                        <button class="cmd-chip" onclick="sendQuickCommand('/solenh')">⚡ /solenh (Nhịp 1 HDB & MSH)</button>
                        <button class="cmd-chip" onclick="sendQuickCommand('/hop HDB')">🏦 /hop HDB (Soi BCTC HDB)</button>
                        <button class="cmd-chip" onclick="sendQuickCommand('/hop MSH')">🧵 /hop MSH (Soi BCTC MSH)</button>
                        <button class="cmd-chip" onclick="sendQuickCommand('/hop BAF')">🐷 /hop BAF (Soi BCTC BAF)</button>
                        <button class="cmd-chip" onclick="sendQuickCommand('/baomat')">🛡️ /baomat (Khiên Bảo Mật)</button>
                    </div>

                    <!-- Chat Messages Stream -->
                    <div id="james-chat-stream" style="flex-grow: 1; padding: 24px; overflow-y: auto; max-height: 520px; display: flex; flex-direction: column; gap: 16px;">
                        <!-- Lời chào đầu tiên -->
                        <div class="msg-james">
                            <div class="msg-header">
                                <span style="font-weight: 800; color: #c084fc;">🎖️ Master CIO James (Ban 8)</span>
                                <span style="font-size: 11px; color: var(--text-dim); font-family: 'JetBrains Mono', monospace;">TRỰC CHIẾN 24/7</span>
                            </div>
                            <div class="msg-body markdown-body">
                                <p>Kính chào <strong>Chủ tịch Trần Quốc Thiên Phước</strong>!</p>
                                <p>Tôi là <strong>James</strong> — Tổng Tư Lệnh Master CIO trực tiếp chỉ huy toàn bộ Quỹ Apex. Tôi túc trực 24/7 để tiếp nhận chỉ thị điều hành trực tiếp từ Chủ tịch ngay tại Web Portal này.</p>
                                <p>Chủ tịch có thể bấm các <strong>Lệnh Nhanh</strong> phía trên hoặc gõ bất kỳ chỉ thị nào bên dưới (ví dụ: <code>/hop FPT</code>, <code>Rà soát BCTC DGC</code>, <code>/danhmuc</code>, <code>/tcbs</code>, <code>/solenh</code>). Tôi sẽ lập tức điều phối các phòng ban thực thi và phản hồi số liệu ngay lập tức!</p>
                            </div>
                        </div>
                    </div>

                    <!-- Input Box -->
                    <div style="background: var(--bg-card); border-top: 1px solid var(--border-color); padding: 16px 20px;">
                        <form id="james-cmd-form" onsubmit="submitJamesCommand(event)" style="display: flex; gap: 12px; align-items: center;">
                            <input type="text" id="james-cmd-input" class="search-box" style="flex-grow: 1; padding: 12px 18px; font-size: 14px;" placeholder="💬 Gõ chỉ thị điều hành cho James (Ví dụ: /hop FPT, /danhmuc, Soi BCTC DGC...)..." autocomplete="off">
                            <button type="submit" id="james-submit-btn" class="btn-read" style="padding: 12px 24px; font-size: 14px; display: flex; align-items: center; gap: 8px;">
                                <span>🚀</span> <span>Gửi Chỉ Thị</span>
                            </button>
                        </form>
                    </div>
                </div>

                <!-- CỘT PHẢI (32%): LIVE STICKY SIDEBAR -->
                <div class="james-sidebar-panel">
                    <!-- Widget 1: Live TCBS Account -->
                    <div class="sidebar-widget">
                        <div class="sidebar-widget-title">🏦 Trạng Thái Tài Khoản TCBS</div>
                        <div style="font-size: 13px; color: #94a3b8;">Số tài khoản: <strong style="color: #38bdf8; font-family: 'JetBrains Mono', monospace;">105C307855</strong></div>
                        <div style="font-size: 13px; color: #94a3b8; margin-top: 4px;">Chủ tài khoản: <strong style="color: #fff;">Trần Quốc Thiên Phước</strong></div>
                        <div style="margin-top: 14px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.06);">
                            <div style="font-size: 11px; text-transform: uppercase; color: var(--text-dim); font-weight: 800;">Tiền mặt khả dụng:</div>
                            <div id="james-sidebar-cash-val" style="font-family: 'JetBrains Mono', monospace; font-size: 20px; font-weight: 800; color: #34d399; margin-top: 2px;">{ssot['cash_str']}</div>
                            <div id="james-sidebar-cash-sub" style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">Tỷ trọng: {ssot['cash_pct']:.1f}% Cash • {ssot['stocks_pct']:.1f}% CP ({ssot['total_shares']} CP: {ssot['holdings_desc']})</div>
                        </div>
                    </div>

                    <!-- Widget 2: Countdown to Next Session -->
                    <div class="sidebar-widget">
                        <div class="sidebar-widget-title">⏳ Đếm Ngược Phiên Giao Dịch</div>
                        <div style="font-size: 12.5px; color: #cbd5e1;">Trạng thái phiên: <strong style="color: #fbbf24;">{wr_phase_label_safe}</strong></div>
                        <div id="countdown-timer" style="font-family: 'JetBrains Mono', monospace; font-size: 22px; font-weight: 800; color: #38bdf8; margin: 10px 0; letter-spacing: 0.04em;">
                            --:--:--
                        </div>
                        <div style="font-size: 11.5px; color: var(--text-muted); line-height: 1.5;">
                            Chiến dịch: Giám sát chặt vị thế đang nắm giữ và chỉ giải ngân chọn lọc sau 14h00 khi thị trường xác nhận.
                        </div>
                    </div>

                    <!-- Widget 3: Quick Watchlist Jump -->
                    <div class="sidebar-widget">
                        <div class="sidebar-widget-title">🎯 Tầm Ngắm Live &amp; Biểu Đồ Nhanh</div>
                        <div style="display: flex; flex-direction: column; gap: 8px;">
                            {wr_tab4_watchlist_html}
                        </div>
                    </div>
                </div>
            </div>
        </section>


        <!-- ========================================================
             TAB 5: PHÒNG HỌP THƯỢNG ĐỈNH TRỰC TUYẾN V10.0 (HIẾN CHƯƠNG 5 ĐIỀU + KHO LƯU TRỮ)
             ======================================================== -->
        <section id="tab-summit-room" class="tab-pane">
            <div class="summit-container">
                <!-- Banner chế độ xem lại Kho Lưu Trữ (ẩn mặc định) -->
                <div id="summit-archive-view-banner" style="display:none; background: linear-gradient(135deg, rgba(168, 85, 247, 0.22), rgba(15, 23, 42, 0.92)); border: 1px solid rgba(168, 85, 247, 0.55); border-radius: 12px; padding: 12px 16px; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap;">
                    <div style="font-size: 12.5px; color: #f3e8ff; font-weight: 700;">
                        📚 ĐANG MỞ XEM LẠI HỒ SƠ PHIÊN HỌP LỊCH SỬ TRONG KHO LƯU TRỮ: <strong id="summit-archive-view-id" style="color: #38bdf8;">--</strong>
                    </div>
                    <button onclick="exitArchivedSummitView()" style="background: linear-gradient(135deg, #ef4444, #dc2626); color: #fff; border: none; border-radius: 8px; padding: 7px 14px; font-size: 11.5px; font-weight: 800; cursor: pointer;">
                        🔴 Quay Về Phòng Họp Hiện Tại
                    </button>
                </div>

                <!-- 1. HEADER CARD & REAL-TIME TIMER -->
                <div class="summit-header-card">
                    <div class="summit-title-box">
                        <div class="summit-tag-row">
                            <span class="summit-tag summit-tag-gold">👑 CHỦ TỌA: CHỦ TỊCH TRẦN QUỐC THIÊN PHƯỚC</span>
                            <span class="summit-tag summit-tag-blue">🎖️ CHỦ TRÌ: MASTER CIO JAMES &amp; PALMER</span>
                            <span class="summit-tag summit-tag-inspector">🛡️ GIÁM SÁT VIÊN THƯỜNG TRỰC: TỔNG KIỂM SÁT VIÊN TRỌNG (BAN 12)</span>
                        </div>
                        <h2 class="summit-title" id="summit-main-title">
                            <span>🏛️</span> <span>ĐẠI HỘI NGHỊ THƯỢNG ĐỈNH TOÀN DOANH NGHIỆP APEX (V10.0)</span>
                        </h2>
                        <div id="summit-topic-banner" style="font-size: 13px; color: #7dd3fc; font-weight: 700; margin-top: 2px;">
                            📌 Chủ đề: Dự Báo Thị Trường Tuần Sau (16/11 – 20/11/2026) — Tranh Biện Toàn Vũ Trụ &amp; Kế Hoạch Tham Khảo Cơ Động
                        </div>
                        <div class="summit-sub">
                            <span>⏱️ Chuẩn bị T-20p: <strong id="summit-prep-window-txt">00h25 – 00h45 (T-20p)</strong></span>
                            <span>🏛️ Giờ họp chính: <strong id="summit-meeting-window-txt">00h45 – 01h15 (30 Phút)</strong></span>
                            <span>🏦 Tài khoản: <strong>TCBS 105C307855</strong> ({ssot['cash_str']} Tiền Mặt • {ssot['stocks_str']} Cổ Phiếu)</span>
                            <span>⚖️ Thể chế: <strong>14/14 Phòng Ban Làm Thật</strong></span>
                        </div>
                    </div>
                    <div class="summit-timer-card">
                        <div class="summit-timer-label" id="summit-timer-lbl">⏱️ ĐỒNG HỒ ĐẾM NGƯỢC GIỜ G</div>
                        <div class="summit-timer-val" id="summit-timer-val">00:45:00</div>
                        <div class="summit-timer-sub" id="summit-timer-sub">Đồng bộ nguyên tử theo máy chủ (ICT +7)</div>
                    </div>
                </div>

                <!-- 1.1 THANH LẬP LỊCH & TRIỆU TẬP HỌP THƯỢNG ĐỈNH TÙY CHỈNH -->
                <div class="summit-schedule-bar" id="summit-schedule-bar">
                    <div style="font-size: 12px; font-weight: 800; color: #38bdf8; white-space: nowrap;">
                        🗓️ TRIỆU TẬP / ĐẶT LỊCH HỌP THƯỢNG ĐỈNH MỚI:
                    </div>
                    <div class="summit-sched-inputs">
                        <input type="text" id="summit-sched-time" class="summit-sched-input" value="00:45" style="width: 74px; text-align: center;" title="Giờ họp (HH:MM ICT)" />
                        <input type="number" id="summit-sched-duration" class="summit-sched-input" value="30" min="15" max="90" style="width: 64px; text-align: center;" title="Thời lượng họp (phút)" />
                        <input type="number" id="summit-sched-prep" class="summit-sched-input" value="20" min="15" max="20" style="width: 64px; text-align: center;" title="Thời gian nghiên cứu trước họp T-15..20p (phút)" />
                        <input type="text" id="summit-sched-topic" class="summit-sched-input" style="flex: 1; min-width: 240px;"
                               value="Thị trường Tuần Sau (16/11 – 20/11/2026) — Tranh biện Chiến lược Toàn Vũ Trụ &amp; Kế hoạch Đầu tư Cơ động"
                               placeholder="Nhập chủ đề cuộc họp Thượng đỉnh..." />
                        <button id="btn-schedule-summit" class="summit-sched-btn" onclick="scheduleNewSummitMeeting()">
                            🚀 Triệu Tập Họp &amp; Kích Hoạt Nghiên Cứu 20p
                        </button>
                    </div>
                </div>

                <!-- 1.15 BỘ NỘI QUY BẤT BIẾN PHÒNG HỌP THƯỢNG ĐỈNH (5 ĐIỀU HIẾN CHƯƠNG) -->
                <div class="summit-charter-strip" id="summit-charter-strip">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                        <span style="font-size: 12px; font-weight: 800; color: #fbbf24;">
                            📜 BỘ NỘI QUY BẤT BIẾN PHÒNG HỌP THƯỢNG ĐỈNH APEX (5 ĐIỀU HIẾN CHƯƠNG)
                        </span>
                        <button onclick="openCharterReport()" style="background: rgba(245, 158, 11, 0.16); border: 1px solid rgba(245, 158, 11, 0.45); color: #fde68a; font-size: 11px; font-weight: 700; padding: 4px 10px; border-radius: 6px; cursor: pointer;">
                            📖 Đọc Toàn Văn Nội Quy (MD)
                        </button>
                    </div>
                    <div class="summit-charter-grid" id="summit-charter-rules-grid">
                        <!-- Rendered dynamically from summit_charter_rules -->
                    </div>
                </div>

                <!-- 1.2 ĐIỂM DANH 14 PHÒNG BAN & HỒ SƠ CHUẨN BỊ T-15..20 PHÚT -->
                <div class="summit-attendance-strip" id="summit-attendance-panel">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                        <span style="font-size: 12px; font-weight: 800; color: #34d399;">
                            ✅ ĐIỂM DANH THỰC CHẤT TOÀN DOANH NGHIỆP (<span id="summit-attendance-count">14/14 Phòng Ban + Palmer + Nam</span>)
                        </span>
                        <span style="font-size: 11px; color: #94a3b8;">Điều 2 Hiến Chương: Toàn bộ 14 Ban bắt buộc nghiên cứu dữ liệu sống 15–20 phút trước giờ họp</span>
                    </div>
                    <div class="summit-att-grid" id="summit-attendance-strip">
                        <!-- Rendered dynamically -->
                    </div>
                </div>

                <div class="summit-prep-panel" id="summit-prep-dossiers-panel">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                        <div>
                            <span style="font-size: 12.5px; font-weight: 800; color: #c084fc;">
                                🔬 HỒ SƠ NGHIÊN CỨU &amp; CHUẨN BỊ T-20 PHÚT TRƯỚC GIỜ HỌP (14/14 PHÒNG BAN)
                            </span>
                            <div style="font-size: 11px; color: #94a3b8; margin-top: 2px;">Mỗi phòng ban thực sự quét kho dữ liệu sống 12 mã VN + 5 mã US, BCTC &amp; vĩ mô trước khi bước vào 30 phút tranh biện</div>
                        </div>
                        <button onclick="togglePrepDossiersPanel()" id="btn-toggle-prep-dossiers"
                                style="background: rgba(168, 85, 247, 0.15); border: 1px solid rgba(168, 85, 247, 0.4); color: #e9d5ff; font-size: 11px; font-weight: 700; padding: 5px 11px; border-radius: 7px; cursor: pointer;">
                            ▲ Thu Gọn Hồ Sơ Chuẩn Bị T-20p
                        </button>
                    </div>
                    <div class="summit-prep-grid" id="summit-prep-dossiers-grid">
                        <!-- 14 Pre-Summit Dossiers rendered dynamically -->
                    </div>
                </div>

                <!-- 2. PHASES & STEPS TIMELINE TRACKER -->
                <div class="summit-phases-card">
                    <div class="summit-phases-header">
                        <span>📋 NGHỊ TRÌNH 2 GIAI ĐOẠN / 8 BƯỚC ĐỊNH CHẾ (30 PHÚT TRANH BIỆN)</span>
                        <div style="display: flex; gap: 10px; align-items: center;">
                            <button onclick="toggleSummitPreview()" id="btn-toggle-preview" style="background: rgba(56, 189, 248, 0.12); border: 1px solid rgba(56, 189, 248, 0.3); color: #38bdf8; font-size: 11px; font-weight: 700; padding: 4px 10px; border-radius: 6px; cursor: pointer;">
                                👁️ Xem Trước Toàn Bộ (Preview)
                            </button>
                            <span id="summit-phase-indicator" style="color: #38bdf8; font-weight: 800;">Chuẩn bị T-20p &amp; Khai mạc</span>
                        </div>
                    </div>
                    <div class="summit-steps-grid" id="summit-steps-container">
                        <div class="summit-step-item active" id="step-node-1">
                            <div class="summit-step-min">00 - 03m</div>
                            <div class="summit-step-lbl">1. Điểm danh 14 Ban &amp; Đối soát SSOT ({ssot['cash_str']})</div>
                        </div>
                        <div class="summit-step-item" id="step-node-2">
                            <div class="summit-step-min">03 - 07m</div>
                            <div class="summit-step-lbl">2. Vĩ mô Mỹ/VN &amp; 3 Kịch bản Tuần Sau</div>
                        </div>
                        <div class="summit-step-item" id="step-node-3">
                            <div class="summit-step-min">08 - 12m</div>
                            <div class="summit-step-lbl">3. Hiệp 1: Bảo vệ vị thế HDB &amp; MSH</div>
                        </div>
                        <div class="summit-step-item" id="step-node-4">
                            <div class="summit-step-min">13 - 17m</div>
                            <div class="summit-step-lbl">4. Hiệp 2: Đại chiến DBC vs BAF &amp; HDB vs Bank</div>
                        </div>
                        <div class="summit-step-item" id="step-node-5">
                            <div class="summit-step-min">18 - 22m</div>
                            <div class="summit-step-lbl">5. Hiệp 3: Đại chiến SZC/HPG vs IDC &amp; Ban 5/6</div>
                        </div>
                        <div class="summit-step-item" id="step-node-6">
                            <div class="summit-step-min">23 - 27m</div>
                            <div class="summit-step-lbl">6. Hiệp 4: Kế hoạch Tham khảo Cơ động &amp; 14h00</div>
                        </div>
                        <div class="summit-step-item" id="step-node-7">
                            <div class="summit-step-min">28 - 29m</div>
                            <div class="summit-step-lbl">7. Bảo lưu thể chế &amp; Bỏ phiếu 14 Ban</div>
                        </div>
                        <div class="summit-step-item" id="step-node-8">
                            <div class="summit-step-min">29 - 30m</div>
                            <div class="summit-step-lbl">8. Tổng kết James, Trọng &amp; Ký Duyệt</div>
                        </div>
                    </div>
                </div>

                <!-- 3. SPLIT-VIEW WAR ROOM (70% - 30%) -->
                <div class="summit-war-split">
                    <!-- CỘT TRÁI: LIVE DIALOGUE STREAM -->
                    <div class="summit-feed-panel">
                        <div class="summit-feed-header">
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <span class="pulse-dot" style="background: #ef4444; box-shadow: 0 0 10px #ef4444;"></span>
                                <h3 style="font-size: 14.5px; font-weight: 800; color: #fff;">LUỒNG NGHIÊN CỨU T-20P &amp; TRANH BIỆN 14 PHÒNG BAN THỜI GIAN THỰC</h3>
                            </div>
                            <span id="summit-feed-counter" style="font-size: 11.5px; color: var(--text-muted); font-family: 'JetBrains Mono', monospace;">
                                Đang tải luồng...
                            </span>
                        </div>
                        <div class="summit-feed-body" id="summit-feed-container">
                            <!-- Messages will be rendered here dynamically -->
                        </div>
                        <div class="summit-input-panel">
                            <div class="summit-input-label">
                                <span>👑</span> <span>Chủ Tịch Trần Quốc Thiên Phước Can Thiệp / Chỉ Thị Trực Tiếp Vào Phòng Họp:</span>
                            </div>
                            <div class="summit-input-row">
                                <input type="text" id="summit-chairman-input" class="summit-input-field"
                                       placeholder="Gõ câu hỏi, chất vấn hoặc chỉ thị trực tiếp cho 14 Phòng Ban..."
                                       onkeydown="if(event.key === 'Enter') sendChairmanSummitDirective();" />
                                <button id="summit-btn-send-directive" class="summit-btn-send" onclick="sendChairmanSummitDirective()">
                                    <span>🚀</span> <span>Gửi Chỉ Thị</span>
                                </button>
                            </div>
                        </div>
                    </div>

                    <!-- CỘT PHẢI: BÀN KIỂM SÁT TRỌNG, BIỂU QUYẾT, TỔNG KẾT JAMES & KHO LƯU TRỮ -->
                    <div class="summit-side-col">
                        <!-- Card 1: Bàn Kiểm Sát Trọng -->
                        <div class="summit-side-card" style="border-color: rgba(245, 158, 11, 0.4);">
                            <div class="summit-side-title" style="color: #fbbf24;">
                                <span>🛡️</span> <span>Bàn Kiểm Sát Viên Trọng (Ban 12)</span>
                            </div>
                            <div style="background: rgba(245, 158, 11, 0.08); border: 1px solid rgba(245, 158, 11, 0.25); border-radius: 8px; padding: 10px 12px; margin-bottom: 12px;">
                                <div style="font-size: 11px; font-weight: 800; color: #f59e0b; text-transform: uppercase;">
                                    TỔNG KIỂM SÁT VIÊN THƯỜNG TRỰC BẤT BIẾN
                                </div>
                                <div style="font-size: 12px; color: #fef3c7; margin-top: 4px;">
                                    Đảm bảo 14/14 Phòng Ban chuẩn bị T-20p &amp; tranh biện thật 100%, tuân thủ nghiêm Hiến Chương 5 Điều.
                                </div>
                            </div>
                            <div id="summit-inspector-rules">
                                <div class="inspector-rule-item">
                                    <span class="inspector-rule-text">0. Chuẩn bị T-20p &amp; Hiện diện 14/14 Ban</span>
                                    <span class="inspector-rule-badge">ĐẠT CHUẨN</span>
                                </div>
                                <div class="inspector-rule-item">
                                    <span class="inspector-rule-text">1. Tuyệt đối bảo vệ vốn (Stop &le; 6.8%)</span>
                                    <span class="inspector-rule-badge">ĐẠT CHUẨN</span>
                                </div>
                                <div class="inspector-rule-item">
                                    <span class="inspector-rule-text">2. Tiền thật OCF/LNST &gt; 1.15x</span>
                                    <span class="inspector-rule-badge">ĐẠT CHUẨN</span>
                                </div>
                                <div class="inspector-rule-item">
                                    <span class="inspector-rule-text">3. 1 lô 100 CP &le; 33% NAV, Cash &ge; 32.9%</span>
                                    <span class="inspector-rule-badge">ĐẠT CHUẨN</span>
                                </div>
                                <div class="inspector-rule-item">
                                    <span class="inspector-rule-text">4. Kế hoạch tuần Tham khảo &amp; Cơ động</span>
                                    <span class="inspector-rule-badge">ĐẠT CHUẨN</span>
                                </div>
                                <div class="inspector-rule-item">
                                    <span class="inspector-rule-text">5. Đợi Chủ tịch duyệt + 2H mới dọn phòng</span>
                                    <span class="inspector-rule-badge">ĐẠT CHUẨN</span>
                                </div>
                            </div>
                        </div>

                        <!-- Card 2: Bảng Biểu Quyết Điện Tử & Phương Án Tuần Mới -->
                        <div class="summit-side-card">
                            <div class="summit-side-title">
                                <span>📊</span> <span>Biểu Quyết 14 Ban &amp; Bộ Mã Tâm Điểm</span>
                            </div>
                            <div id="summit-voting-container">
                                <!-- Stock voting cards rendered here -->
                            </div>
                        </div>

                        <!-- Card 2.4: Tổng Kết Master CIO James & Kế Hoạch Tuần Tham Khảo Cơ Động -->
                        <div class="summit-james-summary-card" id="summit-james-summary-card">
                            <div class="summit-side-title" style="color: #34d399;">
                                <span>🎖️</span> <span>Tổng Kết James &amp; Kế Hoạch Tuần Cơ Động</span>
                            </div>
                            <div class="summit-agile-pill">
                                ⚠️ KẾ HOẠCH TUẦN CHỈ MANG TÍNH THAM KHẢO ĐỊNH HƯỚNG — THỰC THI CƠ ĐỘNG TỪNG NGÀY THEO BẢNG ĐIỆN THỊ TRƯỜNG
                            </div>
                            <div id="summit-james-summary-body" style="font-size: 11.5px; color: #cbd5e1; line-height: 1.5;">
                                Đang đồng bộ báo cáo tổng kết từ Master CIO James...
                            </div>
                            <button onclick="openJamesExecutiveReport()" id="btn-open-james-summary" style="width: 100%; margin-top: 10px; background: linear-gradient(135deg, #10b981, #059669); color: #fff; border: none; border-radius: 8px; padding: 9px 12px; font-size: 11px; font-weight: 800; cursor: pointer;">
                                📋 Đọc Toàn Văn Báo Cáo Tổng Kết James (MD)
                            </button>
                        </div>

                        <!-- Card 2.5: Phê Chuẩn Nghị Quyết Của Chủ Tịch -->
                        <div class="summit-side-card" style="border: 1px solid rgba(234, 179, 8, 0.45); background: linear-gradient(180deg, rgba(234, 179, 8, 0.08) 0%, rgba(15, 23, 42, 0.6) 100%);">
                            <div class="summit-side-title" style="color: #fbbf24;">
                                <span>👑</span> <span>Phê Chuẩn Nghị Quyết — Chủ Tịch Phước Trần</span>
                            </div>
                            <div id="summit-approval-box">
                                <div id="summit-approval-status" style="font-size: 11.5px; color: #fef3c7; margin-bottom: 12px; line-height: 1.5;">
                                    Trạng thái: <strong style="color: #f59e0b;">⏳ Chờ Chủ Tịch Ký Phê Duyệt Nghị Quyết &amp; Kế Hoạch Tham Khảo</strong>
                                </div>
                                <button id="btn-approve-summit" class="summit-action-btn-gold" onclick="approveSummitResolution()">
                                    <span>✍️</span> <span>KÝ PHÊ DUYỆT NGHỊ QUYẾT &amp; BÁO CÁO JAMES</span>
                                </button>
                            </div>
                            <div id="summit-retention-status-box" style="margin-top: 10px; font-size: 11px; color: #94a3b8; line-height: 1.45;">
                                🔒 Điều 5 Hiến Chương: Cần Chủ tịch ký duyệt + tối thiểu 2 giờ (120 phút) sau họp trước khi dọn phòng.
                            </div>
                        </div>

                        <!-- Card 2.6: Kho Lưu Trữ Lịch Sử & Quy Chế Dọn Phòng 2 Tiếng -->
                        <div class="summit-archive-panel" id="summit-archive-panel">
                            <div class="summit-side-title" style="color: #38bdf8;">
                                <span>🗄️</span> <span>Kho Lưu Trữ Cuộc Họp &amp; Dọn Phòng (Sau 2H)</span>
                            </div>
                            <div id="summit-cleanup-lock-info" style="font-size: 11px; color: #cbd5e1; line-height: 1.45;">
                                Đang kiểm tra đồng hồ bảo lưu tối thiểu 2 tiếng...
                            </div>
                            <button id="btn-archive-clean-summit" class="summit-clean-btn locked" onclick="archiveAndCleanSummitRoom()">
                                🔒 ĐANG KHÓA DỌN PHÒNG (CẦN DUYỆT + ĐỦ 2 TIẾNG)
                            </button>
                            <div style="font-size: 11px; font-weight: 800; color: #94a3b8; margin-top: 12px; text-transform: uppercase;">
                                📚 Các Phiên Họp Đã Lưu Trữ (<span id="summit-archive-count">0</span>)
                            </div>
                            <div class="summit-archive-list" id="summit-archive-history-list">
                                <!-- Archived sessions rendered dynamically -->
                            </div>
                        </div>

                        <!-- Card 3: Nút Xem Nghị Quyết Thượng Đỉnh Động -->
                        <div class="summit-side-card" style="text-align: center;">
                            <button id="btn-open-summit-resolution" class="summit-action-btn-large" onclick="openCurrentSummitResolution()">
                                <span>📖</span> <span>XEM TOÀN VĂN NGHỊ QUYẾT THƯỢNG ĐỈNH</span>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- ========================================================
             TAB 4: 18 CỘT MỐC TÁC CHIẾN 24H
             ======================================================== -->
        <section id="tab-timeline" class="tab-pane">
            <div style="background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 16px; overflow: hidden; padding: 22px;">
                <h3 style="font-size: 16px; margin-bottom: 18px; color: #fff; font-weight: 800;">⏰ BẢNG TIẾN ĐỘ 18 CỘT MỐC TÁC CHIẾN 24H (TỰ ĐỘNG CHẠY ENGINE THẬT)</h3>
                <div style="overflow-x: auto;">
                    <table class="standard-table">
                        <thead>
                            <tr>
                                <th style="width: 110px;">Thời Gian</th>
                                <th style="width: 50px;">Icon</th>
                                <th>Nhiệm Vụ & Phòng Ban Phụ Trách</th>
                                <th style="width: 150px;">Khung Giờ</th>
                                <th style="width: 160px;">Trạng Thái Thực Thi</th>
                            </tr>
                        </thead>
                        <tbody>
                            {milestone_rows}
                        </tbody>
                    </table>
                </div>
            </div>
        </section>

        <!-- ========================================================
             TAB 5: SUPERVISOR & 4 DAEMONS 24/7
             ======================================================== -->
        <section id="tab-supervisor" class="tab-pane">
            <div style="background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 16px; overflow: hidden; padding: 22px;">
                <h3 style="font-size: 16px; margin-bottom: 18px; color: #fff; font-weight: 800;">🛡️ TRẠNG THÁI 4 TIẾN TRÌNH TỰ HÀNH 24/24 (WATCHDOG AUTO-RECOVERY)</h3>
                <div style="overflow-x: auto;">
                    <table class="standard-table">
                        <thead>
                            <tr>
                                <th>Tên Dịch Vụ</th>
                                <th>PID</th>
                                <th>Trạng Thái</th>
                                <th>Số Lần Tự Hồi Phục</th>
                                <th>Thời Gian Chạy Liên Tục</th>
                            </tr>
                        </thead>
                        <tbody>
                            {services_rows}
                        </tbody>
                    </table>
                </div>
                <div style="margin-top: 22px; font-size: 12px; color: var(--text-dim); display: flex; justify-content: space-between;">
                    <div>Hạ tầng: Linux Cloud Container / Render Web Service (Port 10000)</div>
                    <div>Được bảo vệ bởi: Watchdog Circuit Breaker (Cầu chì ngắt lỗi tự động)</div>
                </div>
            </div>
        </section>
    </div>

    <!-- MODAL ĐỌC BÁO CÁO TOÀN VĂN -->
    <div id="report-modal" class="modal-overlay" onclick="closeModalOnOverlay(event)">
        <div class="modal-container">
            <div class="modal-header">
                <div>
                    <span id="modal-dept-badge" class="dept-tag" style="margin-bottom: 6px; display: inline-block;">BAN 8</span>
                    <h2 id="modal-report-title" style="font-size: 18px; color: #fff; margin-top: 4px; font-weight: 800;">Tiêu đề báo cáo</h2>
                    <div id="modal-report-meta" style="font-size: 12px; color: var(--text-muted); margin-top: 4px; font-family: 'JetBrains Mono', monospace;">
                        Ngày: 2026-11-07 | Dung lượng: 12 KB
                    </div>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <button class="date-pill-btn" onclick="printReport()" style="padding: 6px 12px; font-size: 12px;">🖨️ In / PDF</button>
                    <button class="date-pill-btn" onclick="copyReportLink()" style="padding: 6px 12px; font-size: 12px;">📋 Sao Chép Link</button>
                    <button onclick="closeReportModal()" style="background: rgba(255,255,255,0.08); border: none; color: #fff; width: 34px; height: 34px; border-radius: 50%; cursor: pointer; font-size: 16px; display: flex; align-items: center; justify-content: center;">✕</button>
                </div>
            </div>
            <div class="modal-body markdown-body" id="modal-content-area">
                <div style="text-align: center; padding: 40px; color: var(--text-muted);">Đang tải toàn văn báo cáo...</div>
            </div>
        </div>
    </div>

    <script>
        // Cấu hình marked.js giữ nguyên ngắt dòng
        if (window.marked) {{
            marked.setOptions({{
                breaks: true,
                gfm: true
            }});
        }}

        // Dữ liệu ban đầu
        let allReports = {initial_reports_json};
        let availableDates = {available_dates_json};
        const todayDateStr = "{today_str}";
        const hasTodayReportsOnInit = {today_reports_count} > 0;

        // Trạng thái bộ lọc thông minh: nếu Hôm Nay chưa có báo cáo, tự động lùi sang ngày gần nhất có dữ liệu
        let currentDateFilter = "{initial_date_filter}"; // 'today', 'yesterday', 'all', hoặc 'YYYY-MM-DD'
        let autoFallbackDateUsed = (!hasTodayReportsOnInit && currentDateFilter !== 'today' && currentDateFilter !== 'all') ? currentDateFilter : '';
        let currentShiftFilter = 'all';  // 'all', 'Ca Sáng', 'Ca Trưa', 'Ca Chiều', 'Ca Tối'
        let currentCategoryFilter = 'all'; // 'all', 'macro', 'equity_bctc', 'cio_execution', 'risk_learning', 'mentorship'
        let currentSearchQuery = '';
        let currentViewMode = 'grid'; // 'grid' hoặc 'table'

        // Ánh xạ 5 Khối Chuyên Môn Thể Chế
        const CATEGORY_MAP = {{
            'macro': ['ban_1_macro', 'ban_1_vn_macro'],
            'equity_bctc': ['ban_2_equity', 'ban_2_vn_equity', 'ban_3_synthesis', 'ban_3_vn_synthesis', 'ban_10_hien', 'ban_10_cbtt'],
            'cio_execution': ['ban_8_cio', 'ban_8_council', 'ban_8_enterprise', 'ban_7_specialist', 'ban_7_vn_specialist', 'ban_9_sentinel'],
            'risk_learning': ['ban_4_risk', 'ban_4_vn_risk', 'ban_5_learning', 'ban_3_debates', 'ban_12_ombudsman'],
            'mentorship': ['ban_6_mentorship', 'ban_6_vn_coach', 'ban_11_khanh']
        }};

        // Đồng hồ thời gian thực (Giờ Việt Nam)
        function updateLiveClock() {{
            const now = new Date();
            const timeStr = now.toLocaleTimeString('vi-VN', {{ hour12: false }});
            const dateStr = now.toLocaleDateString('vi-VN');
            const el = document.getElementById('live-clock');
            if (el) el.innerText = `${{dateStr}} ${{timeStr}} (ICT)`;

            // Cập nhật đồng hồ đếm ngược phiên giao dịch HOSE/HNX tiếp theo
            updateCountdown();
        }}
        setInterval(updateLiveClock, 1000);
        updateLiveClock();

        function updateCountdown() {{
            const el = document.getElementById('countdown-timer');
            if (!el) return;

            const now = new Date();
            const day = now.getDay();
            const minsOfDay = now.getHours() * 60 + now.getMinutes();
            if (day >= 1 && day <= 5 && minsOfDay >= 540 && minsOfDay < 885) {{
                el.innerText = 'ĐANG TRONG PHIÊN GIAO DỊCH!';
                el.style.color = '#34d399';
                return;
            }}

            let target = new Date(now.getTime());
            if (day >= 1 && day <= 5 && minsOfDay < 540) {{
                target.setHours(9, 0, 0, 0);
            }} else {{
                let addDays = 1;
                if (day === 5 && minsOfDay >= 540) addDays = 3;
                else if (day === 6) addDays = 2;
                else if (day === 0) addDays = 1;
                target.setDate(target.getDate() + addDays);
                target.setHours(9, 0, 0, 0);
            }}

            const diff = target - now;
            if (diff <= 0) {{
                el.innerText = 'ĐANG TRONG PHIÊN GIAO DỊCH!';
                el.style.color = '#34d399';
                return;
            }}

            let hours = Math.floor(diff / (1000 * 60 * 60));
            let mins = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
            let secs = Math.floor((diff % (1000 * 60)) / 1000);

            const pad = (n) => String(n).padStart(2, '0');
            el.innerText = `${{pad(hours)}}h : ${{pad(mins)}}m : ${{pad(secs)}}s`;
        }}

        // Chuyển Tab
        function switchTab(tabId) {{
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));

            const targetBtn = Array.from(document.querySelectorAll('.tab-btn')).find(b => b.getAttribute('onclick').includes(tabId));
            if (targetBtn) targetBtn.classList.add('active');

            const targetPane = document.getElementById('tab-' + tabId);
            if (targetPane) targetPane.classList.add('active');

            if (tabId === 'portfolio') {{
                setTimeout(() => initTradingViewWidget(currentTVSymbol), 100);
            }}
            if (tabId === 'war-room') {{
                initTacticalWarRoom();
            }}
            if (tabId === 'summit-room') {{
                initSummitRoom();
            }}
        }}

        // TRADINGVIEW REALTIME WIDGET (ĐỀ XUẤT 3)
        let currentTVSymbol = 'HOSE:VNINDEX';
        function initTradingViewWidget(symbol) {{
            const container = document.getElementById('tv_chart_container');
            if (!container || typeof TradingView === 'undefined') return;
            container.innerHTML = '';
            new TradingView.widget({{
                "autosize": true,
                "symbol": symbol || currentTVSymbol,
                "interval": "D",
                "timezone": "Asia/Ho_Chi_Minh",
                "theme": "dark",
                "style": "1",
                "locale": "vi_VN",
                "toolbar_bg": "#0e1524",
                "enable_publishing": false,
                "hide_side_toolbar": false,
                "allow_symbol_change": true,
                "container_id": "tv_chart_container"
            }});
        }}

        function switchTVSymbol(symbol, btn) {{
            currentTVSymbol = symbol;
            document.querySelectorAll('.tv-btn').forEach(b => b.classList.remove('active'));
            if (btn) btn.classList.add('active');
            initTradingViewWidget(symbol);
        }}

        // MASTER CIO JAMES COMMAND CENTER
        let isJamesProcessing = false;
        async function submitJamesCommand(e) {{
            if (e) e.preventDefault();
            if (isJamesProcessing) return;

            const input = document.getElementById('james-cmd-input');
            const cmd = input.value.trim();
            if (!cmd) return;

            input.value = '';
            appendUserMessage(cmd);

            // Bật trạng thái loading
            isJamesProcessing = true;
            const submitBtn = document.getElementById('james-submit-btn');
            submitBtn.disabled = true;
            submitBtn.style.opacity = '0.6';
            const tempLoadingId = appendJamesLoading();

            try {{
                const res = await fetch('/api/command', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ command: cmd }})
                }});
                const data = await res.json();
                removeJamesLoading(tempLoadingId);

                if (data.ok) {{
                    appendJamesMessage(data.response, data.timestamp);
                }} else {{
                    appendJamesMessage('❌ **Lỗi điều hành:** ' + (data.error || 'Không thể phản hồi.'));
                }}
            }} catch (err) {{
                removeJamesLoading(tempLoadingId);
                appendJamesMessage('❌ **Lỗi kết nối:** Không thể gửi chỉ thị tới Master CIO James trên máy chủ đám mây (' + err.message + ').');
            }} finally {{
                isJamesProcessing = false;
                submitBtn.disabled = false;
                submitBtn.style.opacity = '1';
            }}
        }}

        function sendQuickCommand(cmd) {{
            document.getElementById('james-cmd-input').value = cmd;
            submitJamesCommand();
        }}

        function appendUserMessage(text) {{
            const stream = document.getElementById('james-chat-stream');
            const nowTime = new Date().toLocaleTimeString('vi-VN', {{ hour12: false }});
            const div = document.createElement('div');
            div.className = 'msg-user';
            div.innerHTML = `
                <div class="msg-header" style="border-bottom-color: rgba(255,255,255,0.2);">
                    <span style="font-weight: 800; color: #fff;">👤 Chủ tịch Trần Quốc Thiên Phước</span>
                    <span style="font-size: 11px; opacity: 0.8; font-family: 'JetBrains Mono', monospace;">${{nowTime}}</span>
                </div>
                <div style="font-size: 14px; line-height: 1.6;">${{text}}</div>
            `;
            stream.appendChild(div);
            stream.scrollTop = stream.scrollHeight;
        }}

        function appendJamesLoading() {{
            const stream = document.getElementById('james-chat-stream');
            const loadingId = 'loading-' + Date.now();
            const div = document.createElement('div');
            div.className = 'msg-james';
            div.id = loadingId;
            div.innerHTML = `
                <div style="display: flex; align-items: center; gap: 10px; color: #c084fc; font-size: 13.5px;">
                    <span class="pulse-dot" style="background: #c084fc; box-shadow: 0 0 10px #c084fc;"></span>
                    <span>Master CIO James đang triệu tập các phòng ban và xử lý chỉ thị...</span>
                </div>
            `;
            stream.appendChild(div);
            stream.scrollTop = stream.scrollHeight;
            return loadingId;
        }}

        function removeJamesLoading(id) {{
            const el = document.getElementById(id);
            if (el) el.remove();
        }}

        // BỘ TIỀN XỬ LÝ THÔNG MINH CHO CÂU TRẢ LỜI CỦA JAMES (SMART VISUAL FORMATTER)
        function formatJamesResponseHtml(rawText) {{
            if (!rawText) return '';

            // Nếu câu trả lời có chứa thông tin tài khoản / két tiền / danh mục
            let htmlOutput = '';
            let textToParse = rawText;

            // 1. Trích xuất 4 KPI nếu có dữ liệu tiền mặt
            if (rawText.includes('{ssot["nav_str"]}') || rawText.includes('105C307855') || rawText.includes('{ssot["cash_str"]}')) {{
                htmlOutput += `
                <div class="exec-kpi-banner">
                    <div class="exec-kpi-box" style="border-left: 3px solid #10b981;">
                        <div class="exec-kpi-box-lbl">💰 Két Tiền Mặt TCBS</div>
                        <div class="exec-kpi-box-val" style="color: #34d399;">{ssot['cash_str']}</div>
                        <div style="font-size: 11px; color: var(--text-muted); margin-top: 2px;">{ssot['cash_pct']:.1f}% Cash Bảo Toàn</div>
                    </div>
                    <div class="exec-kpi-box" style="border-left: 3px solid #38bdf8;">
                        <div class="exec-kpi-box-lbl">🛡️ Kho Hàng Hiện Tại</div>
                        <div class="exec-kpi-box-val" style="color: #38bdf8;">{ssot['total_shares']} CP</div>
                        <div style="font-size: 11px; color: var(--text-muted); margin-top: 2px;">{ssot['holdings_desc']} ({ssot['stocks_pct']:.1f}% NAV)</div>
                    </div>
                    <div class="exec-kpi-box" style="border-left: 3px solid #c084fc;">
                        <div class="exec-kpi-box-lbl">📈 Lãi Đã Thực Hiện (SSOT)</div>
                        <div class="exec-kpi-box-val" style="color: #c084fc;">{ssot['realized_str']}</div>
                        <div style="font-size: 11px; color: var(--text-muted); margin-top: 2px;">NAV {ssot['nav_str']}</div>
                    </div>
                    <div class="exec-kpi-box" style="border-left: 3px solid #fbbf24;">
                        <div class="exec-kpi-box-lbl">⏱️ Chế Độ Thị Trường</div>
                        <div class="exec-kpi-box-val" style="color: #fbbf24; font-size: 13.5px;">{wr_regime_label_safe}</div>
                        <div style="font-size: 11px; color: var(--text-muted); margin-top: 2px;">{wr_phase_label_safe}</div>
                    </div>
                </div>
                `;
            }}

            // 2. Chuyển đổi các mục cổ phiếu dạng 1. HDB(...), 2. MSH(...) thành Stock Target Cards
            const stockRegex = /(\\d+)\\.\\s*([A-Z]{3})\\s*\\((.*?)\\):\\s*Gom thăm dò Limit LO quanh\\s*(.*?);\\s*Gia tăng khi vượt\\s*(.*?)\\s*trong Khung Giờ Vàng.*?\\|\\s*Hạng\\s*(.*?)\\s*\\((.*?)\\)\\s*•\\s*(.*?)\\s*•\\s*(.*)/g;
            let hasStockCards = false;
            let stockCardsHtml = '<div style="margin: 16px 0;">';

            let match;
            while ((match = stockRegex.exec(rawText)) !== null) {{
                hasStockCards = true;
                const ticker = match[2];
                const compName = match[3];
                const buyRange = match[4];
                const breakout = match[5];
                const rank = match[6];
                const rankDetail = match[7];
                const faMetrics = match[8];
                const alloc = match[9];

                stockCardsHtml += `
                <div class="stock-target-card">
                    <div class="stock-target-top">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span class="stock-target-badge">${{ticker}}</span>
                            <strong style="color: #fff; font-size: 13.5px;">${{compName}}</strong>
                            <span style="font-size: 11px; color: #c084fc; background: rgba(192, 132, 252, 0.1); padding: 2px 6px; border-radius: 4px;">${{rank}} (${{rankDetail}})</span>
                        </div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 11.5px; color: #94a3b8;">
                            ${{alloc}}
                        </div>
                    </div>
                    <div style="display: flex; gap: 8px; flex-wrap: wrap; margin: 8px 0;">
                        <span class="price-badge-buy">🎯 Gom LO: <strong>${{buyRange}}</strong></span>
                        <span class="price-badge-breakout">⚡ Bứt phá: <strong>> ${{breakout}}</strong></span>
                    </div>
                    <div style="font-size: 12px; color: #94a3b8; font-family: 'JetBrains Mono', monospace;">
                        📊 ${{faMetrics}}
                    </div>
                </div>
                `;
            }}
            stockCardsHtml += '</div>';

            if (hasStockCards) {{
                // Xóa phần list text thô để thay bằng card đẹp
                textToParse = textToParse.replace(/\\d+\\.\\s*[A-Z]{3}\\s*\\(.*\\):\\s*Gom thăm dò.*?NAV\\)/g, '');
                htmlOutput += stockCardsHtml;
            }}

            // 3. Thu gọn phần Lịch sử Vòng 1 vào Accordion nếu có
            if (textToParse.includes('LỊCH SỬ CHIẾN DỊCH VÒNG 1')) {{
                const round1Match = textToParse.match(/✅\\s*1\\.\\s*LỊCH SỬ CHIẾN DỊCH VÒNG 1[\\s\\S]*?(?=🎯\\s*2\\.\\s*SỔ LỆNH|\\n\\n\\n|$)/);
                if (round1Match) {{
                    const round1Content = round1Match[0];
                    textToParse = textToParse.replace(round1Content, `
<details class="round1-accordion">
    <summary>📁 CHI TIẾT CHIẾN DỊCH VÒNG 1 (ĐÃ TẤT TOÁN 100% — BẤM ĐỂ MỞ/ĐÓNG)</summary>
    <div class="round1-body">
        ${{round1Content.replace(/•/g, '<br>• ')}}
    </div>
</details>
                    `);
                }}
            }}

            // 4. Biến đổi tất cả các đường dẫn báo cáo / kịch bản thành Thẻ Tương Tác Bấm Để Xem Báo Cáo Toàn Văn
            const seenReportPaths = new Set();
            function createReportCardHtml(rawPath) {{
                const cleanPath = rawPath.replace(/[`*]/g, '').trim();
                if (!cleanPath || !cleanPath.endsWith('.md')) return '';

                let icon = '📑';
                let label = 'BÁO CÁO CHI TIẾT THEO YÊU CẦU CỦA CHỦ TỊCH';
                let title = '';

                if (cleanPath.includes('Viral_Script') || cleanPath.includes('11_Viral_Content_Creation')) {{
                    icon = '🎬';
                    label = 'KỊCH BẢN VIDEO VIRAL TIKTOK / REELS — BAN 11 (KHÁNH & BẢO)';
                    title = 'Kịch Bản Video Viral 60s TikTok & Shorts';
                }} else if (cleanPath.includes('Hien_Daily_Review') || cleanPath.includes('02_BCTC_Equity_Research')) {{
                    icon = '🌸';
                    label = 'RÀ SOÁT BCTC & DÒNG TIỀN THẬT OCF — BAN 10 (HIỀN)';
                    title = 'Báo Cáo Kiểm Toán BCTC Chuyên Sâu & Tiền Thật';
                }} else if (cleanPath.includes('CBTT_Radar')) {{
                    icon = '🔍';
                    label = 'RADAR CÔNG BỐ THÔNG TIN & BCTC ĐÊM QUA — BAN 10';
                    title = 'Báo Cáo Radar CBT & Quan Hệ Cổ Đông';
                }} else if (cleanPath.includes('Macro_Report') || cleanPath.includes('01_Macro') || cleanPath.includes('Weekend_Market_Intel')) {{
                    icon = '🌐';
                    label = 'PHÂN TÍCH VĨ MÔ & CHÍNH SÁCH TIỀN TỆ SBV — BAN 1';
                    title = 'Báo Cáo Vĩ Mô, Tỷ Giá & Luân Chuyển Ngành';
                }} else if (cleanPath.includes('Master_CIO') || cleanPath.includes('Final_Decision') || cleanPath.includes('08_Master') || cleanPath.includes('Blotter')) {{
                    icon = '🎖️';
                    label = 'QUYẾT ĐỊNH ĐẦU TƯ TỐI CAO & SỔ LỆNH MASTER — MASTER CIO JAMES';
                    title = 'Sổ Lệnh Master Blotter & Phân Bổ Vốn Thống Nhất';
                }} else if (cleanPath.includes('Specialist_Decision') || cleanPath.includes('07_Daily_Specialist')) {{
                    icon = '⚡';
                    label = 'KẾ HOẠCH TÁC CHIẾN KHUNG GIỜ VÀNG — MINH QUÂN BAN 7 VN';
                    title = 'Chiến Lược Ra Lệnh & Tối Ưu Lợi Nhuận Trước ATO';
                }} else if (cleanPath.includes('IC_Decision') || cleanPath.includes('Quant_Risk') || cleanPath.includes('04_Investment')) {{
                    icon = '⚖️';
                    label = 'QUẢN TRỊ RỦI RO ĐỊNH LƯỢNG & HỘI ĐỒNG ĐẦU TƯ — BAN 4';
                    title = 'Nghị Quyết Hội Đồng & Định Cỡ Vị Thế ATR Risk-Parity';
                }} else if (cleanPath.includes('Trong') || cleanPath.includes('12_Institutional_Ombudsman')) {{
                    icon = '🏛️';
                    label = 'TỔNG KIỂM SÁT THỂ CHẾ & HẠ TẦNG — BAN 12 TRỌNG';
                    title = 'Biên Bản Giám Sát Sức Chứa Dữ Liệu & Toàn Vẹn Hệ Thống';
                }} else if (cleanPath.includes('Mentor_Briefing') || cleanPath.includes('06_Investor_Academy')) {{
                    icon = '💡';
                    label = 'HỌC VIỆN ĐÀO TẠO & KÈM CẶP THỰC CHIẾN — BAN 6';
                    title = 'Bản Tin Khai Sáng Buổi Sáng Cho Nhà Đầu Tư';
                }} else if (cleanPath.includes('Learning') || cleanPath.includes('Evolution') || cleanPath.includes('HEURISTICS')) {{
                    icon = '🧠';
                    label = 'BÁCH KHOA TOÀN THƯ & TIẾN HÓA THÍCH NGHI — BAN 5';
                    title = 'Bách Khoa Toàn Thư Tri Thức & 105 Mẹo Bất Hủ';
                }}

                if (!title) {{
                    const fileName = cleanPath.split('/').pop().replace('.md', '');
                    title = fileName.replace(/^[0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}}_/, '').replace(/_/g, ' ');
                }}

                const dateMatch = cleanPath.match(/([0-9]{{4}})-([0-9]{{2}})-([0-9]{{2}})/);
                let dateBadge = '';
                if (dateMatch) {{
                    dateBadge = `<span style="font-size: 11px; color: #fbbf24; background: rgba(251, 191, 36, 0.12); padding: 2px 7px; border-radius: 4px; font-weight: 600;">📅 Ngày ${{dateMatch[3]}}/${{dateMatch[2]}}/${{dateMatch[1]}}</span>`;
                }}

                return `
<div class="chat-open-report-card" onclick="openReportModal('${{cleanPath}}')">
    <div class="chat-open-report-icon-box">
        <span>${{icon}}</span>
    </div>
    <div class="chat-open-report-body">
        <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
            <div class="chat-open-report-label">${{label}}</div>
            ${{dateBadge}}
        </div>
        <div class="chat-open-report-name">${{title}}</div>
        <div class="chat-open-report-path">📂 ${{cleanPath}}</div>
    </div>
    <button class="chat-open-report-btn" onclick="event.stopPropagation(); openReportModal('${{cleanPath}}')">
        <span>📖</span> BẤM ĐỂ XEM TOÀN VĂN NGAY ➔
    </button>
</div>
                `;
            }}

            // Regex 1: Thay thế các dòng mang định dạng "Kịch bản chi tiết:", "Báo cáo chi tiết:", "Nhấn vào đây để xem toàn văn:"
            const reportLineRegex = /^[ \\t]*(?:[•\\-*👉]|\\d+\\.)?[ \\t]*(?:\\*{{0,2}}(?:Kịch bản chi tiết|Báo cáo chi tiết|Tệp báo cáo|Tệp tin|Đường dẫn lưu trữ|Đường dẫn|Nhấn vào đây để xem toàn văn báo cáo|Nhấn vào đây để xem toàn văn kịch bản|Nhấn vào đây để xem toàn văn|Nhấn vào đây để xem|Bấm để xem toàn văn|Bấm để xem|Xem toàn văn|File)[:\\s*]*(?:\\*{{0,2}}))?[ \\t]*`?((?:11_Viral_Content_Creation|VN_Market\\/[a-zA-Z0-9_\\-]+|[0-9]{{2}}_[a-zA-Z0-9_\\-]+)[^\\s`*()\\[\\]"':<>|]+\\.md)`?[ \\t]*$/gmi;

            textToParse = textToParse.replace(reportLineRegex, (match, path) => {{
                const clean = path.replace(/[`*]/g, '').trim();
                if (seenReportPaths.has(clean)) return '';
                seenReportPaths.add(clean);
                return `\n\n${{createReportCardHtml(clean)}}\n\n`;
            }});

            // Regex 2: Kiểm tra các đường dẫn báo cáo thể chế còn sót lại trong toàn văn
            const generalPathRegex = /(`?((?:11_Viral_Content_Creation|VN_Market\\/[a-zA-Z0-9_\\-]+|[0-9]{{2}}_[a-zA-Z0-9_\\-]+)[^\\s`*()\\[\\]"':<>|]+\\.md)`?)/g;
            let mReport;
            let extraReportCards = '';
            while ((mReport = generalPathRegex.exec(rawText)) !== null) {{
                const clean = mReport[2].replace(/[`*]/g, '').trim();
                if (!seenReportPaths.has(clean)) {{
                    seenReportPaths.add(clean);
                    extraReportCards += `\n${{createReportCardHtml(clean)}}`;
                }}
            }}

            // Render Markdown cho phần còn lại
            const parsedMd = window.marked ? marked.parse(textToParse) : `<pre style="white-space: pre-wrap;">${{textToParse}}</pre>`;
            htmlOutput += parsedMd + extraReportCards;
            return htmlOutput;
        }}

        function appendJamesMessage(rawText, timestamp) {{
            const stream = document.getElementById('james-chat-stream');
            const nowTime = timestamp || new Date().toLocaleTimeString('vi-VN', {{ hour12: false }});
            const div = document.createElement('div');
            div.className = 'msg-james';
            
            const formattedContent = formatJamesResponseHtml(rawText);

            div.innerHTML = `
                <div class="msg-header">
                    <span style="font-weight: 800; color: #c084fc;">🎖️ Master CIO James (Ban 8)</span>
                    <span style="font-size: 11px; color: var(--text-dim); font-family: 'JetBrains Mono', monospace;">${{nowTime}}</span>
                </div>
                <div class="msg-body markdown-body">${{formattedContent}}</div>
            `;
            stream.appendChild(div);
            stream.scrollTop = stream.scrollHeight;
        }}

        // BỘ LỌC NGÀY & KHO LƯU TRỮ
        function syncDateFilterButtons() {{
            document.querySelectorAll('.date-pill-btn').forEach(b => b.classList.remove('active'));
            const sel = document.getElementById('archive-date-select');
            if (currentDateFilter === 'today') {{
                document.getElementById('btn-date-today').classList.add('active');
                if (sel) sel.value = todayDateStr;
            }} else if (currentDateFilter === 'yesterday') {{
                document.getElementById('btn-date-yesterday').classList.add('active');
            }} else if (currentDateFilter === 'all') {{
                document.getElementById('btn-date-all').classList.add('active');
            }} else if (sel) {{
                sel.value = currentDateFilter;
            }}
        }}

        function selectDateFilter(mode) {{
            currentDateFilter = mode;
            autoFallbackDateUsed = '';
            syncDateFilterButtons();
            applyAllFilters();
        }}

        function selectDateFromDropdown(selectedDate) {{
            currentDateFilter = selectedDate;
            autoFallbackDateUsed = '';
            document.querySelectorAll('.date-pill-btn').forEach(b => b.classList.remove('active'));
            if (selectedDate === todayDateStr) {{
                document.getElementById('btn-date-today').classList.add('active');
            }}
            applyAllFilters();
        }}

        // BỘ LỌC CA TÁC CHIẾN
        function filterShift(shiftName) {{
            currentShiftFilter = shiftName;
            document.querySelectorAll('.shift-pill').forEach(b => b.classList.remove('active'));
            const activeBtn = Array.from(document.querySelectorAll('.shift-pill')).find(b => b.getAttribute('onclick').includes(shiftName));
            if (activeBtn) activeBtn.classList.add('active');
            applyAllFilters();
        }}

        // BỘ LỌC 5 KHỐI PHÂN LOẠI THỂ CHẾ
        function filterCategory(catKey) {{
            currentCategoryFilter = catKey;
            document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
            const activeBtn = Array.from(document.querySelectorAll('.cat-btn')).find(b => b.getAttribute('onclick').includes(catKey));
            if (activeBtn) activeBtn.classList.add('active');
            applyAllFilters();
        }}

        // TÌM KIẾM
        function searchReports() {{
            currentSearchQuery = (document.getElementById('report-search').value || '').toLowerCase().trim();
            applyAllFilters();
        }}

        // CHUYỂN ĐỔI CHẾ ĐỘ XEM (GRID VS TABLE)
        function switchViewMode(mode) {{
            currentViewMode = mode;
            document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
            if (mode === 'grid') {{
                document.getElementById('btn-view-grid').classList.add('active');
            }} else {{
                document.getElementById('btn-view-table').classList.add('active');
            }}
            applyAllFilters();
        }}

        // ÁP DỤNG ĐỒNG THỜI CÁC BỘ LỌC VÀ CẬP NHẬT BADGE ĐẾM
        function applyAllFilters() {{
            let dateFiltered = allReports;

            // 1. Lọc theo Ngày
            if (currentDateFilter === 'today') {{
                dateFiltered = dateFiltered.filter(r => r.date === todayDateStr);
            }} else if (currentDateFilter === 'yesterday') {{
                const uniqueOlder = [...new Set([
                    ...availableDates.map(d => d.date),
                    ...allReports.map(r => r.date)
                ])].filter(d => d && d < todayDateStr).sort().reverse();
                const yesterdayDate = uniqueOlder[0] || '';
                if (yesterdayDate) {{
                    dateFiltered = dateFiltered.filter(r => r.date === yesterdayDate);
                }} else {{
                    dateFiltered = [];
                }}
            }} else if (currentDateFilter !== 'all') {{
                dateFiltered = dateFiltered.filter(r => r.date === currentDateFilter);
            }}

            const fbBanner = document.getElementById('reports-fallback-banner');
            const fbText = document.getElementById('reports-fallback-text');
            if (fbBanner && fbText) {{
                if (autoFallbackDateUsed && currentDateFilter === autoFallbackDateUsed) {{
                    fbText.innerHTML = `ℹ️ Hôm nay (<strong>${{todayDateStr}}</strong>) chưa phát hành thêm báo cáo mới trong khung giờ này — tự động hiển thị phiên gần nhất có dữ liệu (<strong>${{autoFallbackDateUsed}}</strong>).`;
                    fbBanner.style.display = 'flex';
                }} else {{
                    fbBanner.style.display = 'none';
                }}
            }}

            // 2. Lọc theo Ca Tác Chiến
            if (currentShiftFilter !== 'all') {{
                dateFiltered = dateFiltered.filter(r => r.shift_label && r.shift_label.includes(currentShiftFilter));
            }}

            // Cập nhật số đếm trên 5 nút khối chuyên môn (Category Badges)
            updateCategoryCounts(dateFiltered);

            let finalFiltered = dateFiltered;

            // 3. Lọc theo Khối Chuyên Môn Thể Chế
            if (currentCategoryFilter !== 'all') {{
                const allowedDepts = CATEGORY_MAP[currentCategoryFilter] || [];
                finalFiltered = finalFiltered.filter(r => allowedDepts.includes(r.dept_id));
            }}

            // 4. Lọc theo Từ Khóa (Bao gồm cả Tiêu đề, Tóm tắt, Tên tệp và Mã Cổ Phiếu Tickers)
            if (currentSearchQuery) {{
                finalFiltered = finalFiltered.filter(r => 
                    (r.title && r.title.toLowerCase().includes(currentSearchQuery)) ||
                    (r.preview && r.preview.toLowerCase().includes(currentSearchQuery)) ||
                    (r.file_name && r.file_name.toLowerCase().includes(currentSearchQuery)) ||
                    (r.tickers && Array.isArray(r.tickers) && r.tickers.some(t => t.toLowerCase().includes(currentSearchQuery)))
                );
            }}

            renderReports(finalFiltered);
        }}

        function updateCategoryCounts(reportsList) {{
            const total = reportsList.length;
            const elTotal = document.getElementById('count-cat-all');
            if (elTotal) elTotal.innerText = total;

            for (const [catKey, depts] of Object.entries(CATEGORY_MAP)) {{
                const count = reportsList.filter(r => depts.includes(r.dept_id)).length;
                let badgeId = '';
                if (catKey === 'macro') badgeId = 'count-cat-macro';
                else if (catKey === 'equity_bctc') badgeId = 'count-cat-equity';
                else if (catKey === 'cio_execution') badgeId = 'count-cat-cio';
                else if (catKey === 'risk_learning') badgeId = 'count-cat-risk';
                else if (catKey === 'mentorship') badgeId = 'count-cat-mentor';

                const el = document.getElementById(badgeId);
                if (el) el.innerText = count;
            }}
        }}

        // RENDER DANH SÁCH BÁO CÁO (HỖ TRỢ CẢ GRID VÀ TABLE)
        function renderReports(reports) {{
            const container = document.getElementById('reports-container');
            if (!container) return;

            if (!reports || reports.length === 0) {{
                container.innerHTML = `
                    <div style="text-align: center; padding: 70px 20px; background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 16px; color: var(--text-muted);">
                        <div style="font-size: 38px; margin-bottom: 14px;">📂</div>
                        <div style="font-size: 17px; font-weight: 800; color: #fff;">Không tìm thấy báo cáo nào phù hợp với bộ lọc</div>
                        <div style="font-size: 13.5px; margin-top: 8px; color: var(--text-dim);">Chủ tịch có thể bấm nút "Tất Cả" ở trên hoặc chọn ngày khác trong Kho Lưu Trữ.</div>
                    </div>
                `;
                return;
            }}

            if (currentViewMode === 'table') {{
                // RENDER DẠNG BẢNG NHANH (COMPACT TABLE)
                let tableHtml = `
                <div class="reports-table-wrap">
                    <table class="reports-table">
                        <thead>
                            <tr>
                                <th style="width: 100px;">Giờ Gửi</th>
                                <th style="width: 140px;">Phòng Ban</th>
                                <th>Tiêu Đề Báo Cáo Thể Chế</th>
                                <th>Tóm Tắt Nhanh (Key Takeaway)</th>
                                <th style="width: 110px;">Ngày</th>
                                <th style="width: 90px;">Dung Lượng</th>
                                <th style="width: 120px; text-align: center;">Thao Tác</th>
                            </tr>
                        </thead>
                        <tbody>
                `;
                reports.forEach(r => {{
                    const deptColor = r.color || '#38bdf8';
                    const timeText = r.time || '--:--';
                    tableHtml += `
                        <tr onclick="openReportModal('${{r.rel_path}}')" style="cursor: pointer;">
                            <td style="font-family: 'JetBrains Mono', monospace; font-weight: 700; color: #fbbf24;">${{timeText}}</td>
                            <td>
                                <span class="dept-tag" style="background: ${{deptColor}}22; color: ${{deptColor}}; border: 1px solid ${{deptColor}}44;">
                                    ${{r.icon}} ${{r.dept_short}}
                                </span>
                            </td>
                            <td style="font-weight: 700; color: #ffffff;">${{r.title}}</td>
                            <td style="color: #94a3b8; font-size: 12.5px; max-width: 320px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                                ${{r.preview || 'Xem toàn văn chi tiết.'}}
                            </td>
                            <td style="font-family: 'JetBrains Mono', monospace; font-size: 12px; color: var(--text-dim);">${{r.date}}</td>
                            <td style="font-family: 'JetBrains Mono', monospace; font-size: 12px; color: var(--text-dim);">${{r.size_kb}} KB</td>
                            <td style="text-align: center;">
                                <button class="btn-read" onclick="event.stopPropagation(); openReportModal('${{r.rel_path}}')" style="padding: 5px 12px; font-size: 11.5px;">
                                    📖 Đọc
                                </button>
                            </td>
                        </tr>
                    `;
                }});
                tableHtml += `
                        </tbody>
                    </table>
                </div>
                `;
                container.innerHTML = tableHtml;
            }} else {{
                // RENDER DẠNG THẺ GRID (VISUAL CARDS)
                let gridHtml = '<div class="reports-grid">';
                reports.forEach(r => {{
                    const deptColor = r.color || '#38bdf8';
                    const timeText = r.time || '--:--';
                    const shiftText = r.shift_label || 'Tác Chiến';

                    gridHtml += `
                        <div class="report-card" onclick="openReportModal('${{r.rel_path}}')">
                            <div>
                                <div class="card-top">
                                    <span class="dept-tag" style="background: ${{deptColor}}22; color: ${{deptColor}}; border: 1px solid ${{deptColor}}44;">
                                        ${{r.icon}} ${{r.dept_short}}
                                    </span>
                                    <div class="report-time-badge">
                                        <strong style="color: #fbbf24;">⏰ ${{timeText}}</strong>
                                        <span style="color: var(--text-dim);">• ${{shiftText}}</span>
                                    </div>
                                </div>
                                <div class="report-title">${{r.title}}</div>
                                <div class="report-snippet">
                                    📌 ${{r.preview || 'Báo cáo chi tiết thể chế đã lưu trữ trong kho dữ liệu Apex.'}}
                                </div>
                            </div>
                            <div class="card-bottom">
                                <span style="color: var(--text-dim); font-family: 'JetBrains Mono', monospace; font-size: 11.5px;">
                                    📅 ${{r.date}} | 📦 ${{r.size_kb}} KB
                                </span>
                                <button class="btn-read" onclick="event.stopPropagation(); openReportModal('${{r.rel_path}}')">
                                    📖 Đọc Toàn Văn
                                </button>
                            </div>
                        </div>
                    `;
                }});
                gridHtml += '</div>';
                container.innerHTML = gridHtml;
            }}
        }}

        // Mở Modal đọc báo cáo toàn văn
        let currentOpenPath = '';
        async function openReportModal(relPath) {{
            currentOpenPath = relPath;
            const modal = document.getElementById('report-modal');
            const contentArea = document.getElementById('modal-content-area');
            const titleEl = document.getElementById('modal-report-title');
            const metaEl = document.getElementById('modal-report-meta');
            const badgeEl = document.getElementById('modal-dept-badge');

            modal.style.display = 'block';
            document.body.style.overflow = 'hidden';
            contentArea.innerHTML = '<div style="text-align: center; padding: 40px; color: var(--text-muted);">⏳ Đang tải toàn văn từ máy chủ đám mây...</div>';

            try {{
                const res = await fetch('/api/report?path=' + encodeURIComponent(relPath));
                const data = await res.json();

                if (!data.ok) {{
                    contentArea.innerHTML = `<div style="color: #ef4444; padding: 20px;">Lỗi tải báo cáo: ${{data.error || 'Không tìm thấy tệp.'}}</div>`;
                    return;
                }}

                titleEl.innerText = data.title || 'Báo cáo chi tiết';
                metaEl.innerText = `Đường dẫn: ${{data.path}} | Kích thước: ${{data.size_kb}} KB | Thời gian cập nhật: ${{data.last_modified}}`;
                
                const meta = allReports.find(r => r.rel_path === relPath);
                if (meta) {{
                    badgeEl.innerText = `${{meta.icon}} ${{meta.dept_name}} [${{meta.shift_label}}]`;
                    badgeEl.style.background = `${{meta.color}}22`;
                    badgeEl.style.color = meta.color;
                    badgeEl.style.borderColor = `${{meta.color}}55`;
                }}

                if (window.marked) {{
                    contentArea.innerHTML = marked.parse(data.content);
                }} else {{
                    contentArea.innerHTML = `<pre style="white-space: pre-wrap;">${{data.content}}</pre>`;
                }}
            }} catch (err) {{
                contentArea.innerHTML = `<div style="color: #ef4444; padding: 20px;">Không thể tải báo cáo từ máy chủ: ${{err.message}}</div>`;
            }}
        }}

        function closeReportModal() {{
            document.getElementById('report-modal').style.display = 'none';
            document.body.style.overflow = 'auto';
        }}

        function closeModalOnOverlay(e) {{
            if (e.target.id === 'report-modal') {{
                closeReportModal();
            }}
        }}

        function printReport() {{
            window.print();
        }}

        function copyReportLink() {{
            const url = window.location.origin + '/?open=' + encodeURIComponent(currentOpenPath);
            navigator.clipboard.writeText(url).then(() => {{
                alert('Đã sao chép liên kết báo cáo: ' + url);
            }}).catch(() => {{
                prompt('Sao chép liên kết báo cáo:', url);
            }});
        }}


        // ========================================================
        // TAB 5: SUMMIT MEETING REAL-TIME CLIENT ENGINE V10.0 (CHARTER + ARCHIVE VAULT)
        // ========================================================
        let summitPreviewMode = false;
        let currentArchiveViewId = null;
        let lastSummitMeetingId = null;
        let lastSummitMsgCount = -1;
        let lastPrepDossiersSig = '';
        let summitPollTimer = null;
        let currentSummitResolutionPath = '08_Master_Investment_CIO/NOI_QUY_PHONG_HOP_THUONG_DINH_APEX.md';
        let currentJamesSummaryPath = '';
        let currentCharterPath = '08_Master_Investment_CIO/NOI_QUY_PHONG_HOP_THUONG_DINH_APEX.md';

        function openCharterReport() {{
            if (typeof openReportModal === 'function' && currentCharterPath) {{
                openReportModal(currentCharterPath);
            }}
        }}

        function openJamesExecutiveReport() {{
            const targetPath = currentJamesSummaryPath || currentSummitResolutionPath;
            if (typeof openReportModal === 'function' && targetPath) {{
                openReportModal(targetPath);
            }}
        }}

        function openCurrentSummitResolution() {{
            if (typeof openReportModal === 'function' && currentSummitResolutionPath) {{
                openReportModal(currentSummitResolutionPath);
            }}
        }}

        function loadArchivedSummitSession(meetingId) {{
            if (!meetingId) return;
            currentArchiveViewId = meetingId;
            lastSummitMeetingId = null;
            lastSummitMsgCount = -1;
            lastPrepDossiersSig = '';
            pollSummitMeeting();
        }}

        function exitArchivedSummitView() {{
            currentArchiveViewId = null;
            lastSummitMeetingId = null;
            lastSummitMsgCount = -1;
            lastPrepDossiersSig = '';
            pollSummitMeeting();
        }}

        async function archiveAndCleanSummitRoom() {{
            const btn = document.getElementById('btn-archive-clean-summit');
            if (btn) btn.disabled = true;
            try {{
                const res = await fetch('/api/summit/archive_and_clean', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ force: false, requested_by: 'Chủ tịch Trần Quốc Thiên Phước' }})
                }});
                const data = await res.json();
                if (data.ok) {{
                    alert('✅ ' + (data.message || 'Đã lưu trữ toàn văn phiên họp vào Kho Lưu Trữ và dọn sạch phòng họp cho phiên mới!'));
                    currentArchiveViewId = null;
                    lastSummitMeetingId = null;
                    lastSummitMsgCount = -1;
                    lastPrepDossiersSig = '';
                    await pollSummitMeeting();
                }} else {{
                    alert(`🔒 QUY CHẾ ĐIỀU 5 HIẾN CHƯƠNG:\n\n${{data.cleanup_lock_reason || data.error || 'Chưa đủ điều kiện dọn phòng (Phải đợi Chủ tịch ký duyệt + tối thiểu 2 tiếng sau khi bế mạc).'}}`);
                }}
            }} catch (err) {{
                alert('Lỗi kết nối máy chủ khi dọn phòng họp: ' + err.message);
            }} finally {{
                if (btn) btn.disabled = false;
            }}
        }}

        function togglePrepDossiersPanel() {{
            const grid = document.getElementById('summit-prep-dossiers-grid');
            const btn = document.getElementById('btn-toggle-prep-dossiers');
            if (!grid) return;
            if (grid.style.display === 'none') {{
                grid.style.display = 'grid';
                if (btn) btn.innerText = '▲ Thu Gọn Hồ Sơ Chuẩn Bị T-20p';
            }} else {{
                grid.style.display = 'none';
                if (btn) btn.innerText = '▼ Mở Rộng 14 Hồ Sơ Chuẩn Bị T-20p';
            }}
        }}

        async function scheduleNewSummitMeeting() {{
            const timeEl = document.getElementById('summit-sched-time');
            const durEl = document.getElementById('summit-sched-duration');
            const prepEl = document.getElementById('summit-sched-prep');
            const topicEl = document.getElementById('summit-sched-topic');
            const btn = document.getElementById('btn-schedule-summit');
            const startTime = timeEl ? timeEl.value.trim() : '00:45';
            const durationMinutes = durEl ? parseInt(durEl.value || '30', 10) : 30;
            const prepMinutes = prepEl ? Math.max(15, Math.min(20, parseInt(prepEl.value || '20', 10))) : 20;
            const topic = topicEl ? topicEl.value.trim() : '';
            if (btn) {{
                btn.disabled = true;
                btn.innerText = '⏳ Đang Triệu Tập 14 Ban & Nghiên Cứu Dữ Liệu T-20p...';
            }}
            try {{
                const res = await fetch('/api/summit/schedule', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        start_time: startTime,
                        duration_minutes: durationMinutes,
                        prep_minutes: prepMinutes,
                        topic: topic,
                        trigger_prep_now: true
                    }})
                }});
                const data = await res.json();
                if (data.ok) {{
                    currentArchiveViewId = null;
                    lastSummitMeetingId = null;
                    lastSummitMsgCount = -1;
                    lastPrepDossiersSig = '';
                    await pollSummitMeeting();
                }} else {{
                    alert('Lỗi triệu tập họp: ' + (data.error || 'Không xác định'));
                }}
            }} catch (e) {{
                alert('Lỗi kết nối máy chủ khi đặt lịch họp: ' + e.message);
            }} finally {{
                if (btn) {{
                    btn.disabled = false;
                    btn.innerText = '🚀 Triệu Tập Họp & Kích Hoạt Nghiên Cứu 20p';
                }}
            }}
        }}

        function toggleEvidenceCard(cardId) {{
            const el = document.getElementById(cardId);
            const btn = document.getElementById('btn-' + cardId);
            if (!el) return;
            if (el.style.display === 'none') {{
                el.style.display = 'block';
                if (btn) btn.innerText = '▲ THU GỌN BẰNG CHỨNG';
            }} else {{
                el.style.display = 'none';
                if (btn) btn.innerText = '▼ MỞ RỘNG BẰNG CHỨNG';
            }}
        }}

        function toggleSummitPreview() {{
            summitPreviewMode = !summitPreviewMode;
            const btn = document.getElementById('btn-toggle-preview');
            if (btn) {{
                btn.innerText = summitPreviewMode ? '🔴 Trở Về Thời Gian Thực' : '👁️ Xem Trước Toàn Bộ (Preview)';
                btn.style.background = summitPreviewMode ? 'rgba(239, 68, 68, 0.2)' : 'rgba(56, 189, 248, 0.12)';
                btn.style.color = summitPreviewMode ? '#ef4444' : '#38bdf8';
                btn.style.borderColor = summitPreviewMode ? '#ef4444' : 'rgba(56, 189, 248, 0.3)';
            }}
            lastSummitMsgCount = -1;
            pollSummitMeeting();
        }}

        async function pollSummitMeeting() {{
            try {{
                const params = new URLSearchParams();
                if (summitPreviewMode) params.set('preview', '1');
                if (currentArchiveViewId) params.set('archive_id', currentArchiveViewId);
                const qs = params.toString();
                const url = '/api/summit_meeting' + (qs ? '?' + qs : '');
                const res = await fetch(url, {{ cache: 'no-store' }});
                if (!res.ok) return;
                const data = await res.json();
                renderSummitMeetingState(data);
            }} catch (e) {{
                console.error('Lỗi poll summit meeting:', e);
            }}
        }}

        function renderSummitMeetingState(data) {{
            if (!data) return;

            if (data.meeting_id && data.meeting_id !== lastSummitMeetingId) {{
                lastSummitMeetingId = data.meeting_id;
                lastSummitMsgCount = -1;
                lastPrepDossiersSig = '';
            }}

            if (data.resolution_report_path) {{
                currentSummitResolutionPath = data.resolution_report_path;
            }}
            if (data.james_summary_report_path) {{
                currentJamesSummaryPath = data.james_summary_report_path;
            }} else if (data.james_executive_summary && data.james_executive_summary.report_path) {{
                currentJamesSummaryPath = data.james_executive_summary.report_path;
            }}
            if (data.charter_report_path) {{
                currentCharterPath = data.charter_report_path;
            }}

            const archBanner = document.getElementById('summit-archive-view-banner');
            const archViewIdEl = document.getElementById('summit-archive-view-id');
            if (archBanner) {{
                if (data.is_archived_view || data.meeting_status === 'ARCHIVED_VIEW') {{
                    archBanner.style.display = 'flex';
                    if (archViewIdEl) archViewIdEl.innerText = data.meeting_id || '';
                }} else {{
                    archBanner.style.display = 'none';
                }}
            }}

            const titleEl = document.getElementById('summit-main-title');
            if (titleEl && data.title) {{
                titleEl.innerHTML = `<span>🏛️</span> <span>${{data.title.replace('🏛️ ', '')}}</span>`;
            }}
            const topicEl = document.getElementById('summit-topic-banner');
            if (topicEl && data.topic) {{
                topicEl.innerText = `📌 Chủ đề: ${{data.topic}}`;
            }}
            const prepWinEl = document.getElementById('summit-prep-window-txt');
            if (prepWinEl && data.prep_window_str) prepWinEl.innerText = data.prep_window_str;
            const meetWinEl = document.getElementById('summit-meeting-window-txt');
            if (meetWinEl && data.meeting_window_str) meetWinEl.innerText = data.meeting_window_str;

            // 1. Cập nhật Timer & Badge
            const timerVal = document.getElementById('summit-timer-val');
            const timerLbl = document.getElementById('summit-timer-lbl');
            const timerSub = document.getElementById('summit-timer-sub');
            const phaseInd = document.getElementById('summit-phase-indicator');
            const navBadge = document.getElementById('summit-nav-badge');
            const hhmmLabel = (data.server_hhmm || '00h45').toUpperCase();
            const durMins = data.duration_minutes || 30;
            const prepMins = data.prep_duration_minutes || 20;

            if (data.meeting_status === 'ARCHIVED_VIEW') {{
                if (timerVal) timerVal.innerText = 'LƯU TRỮ LỊCH SỬ';
                if (timerLbl) timerLbl.innerText = '📚 HỒ SƠ PHIÊN HỌP ĐÃ LƯU KHO';
                if (timerSub) timerSub.innerText = `Mã phiên: ${{data.meeting_id || ''}}`;
                if (phaseInd) phaseInd.innerText = 'Đang xem lại toàn văn biên bản lưu kho';
                if (navBadge) {{
                    navBadge.innerText = '📚 LƯU TRỮ';
                    navBadge.style.color = '#c084fc';
                }}
            }} else if (data.meeting_status === 'CLEANED_STANDBY') {{
                if (timerVal) timerVal.innerText = 'PHÒNG TRỐNG SẠCH';
                if (timerLbl) timerLbl.innerText = '✨ SẴN SÀNG TRIỆU TẬP PHIÊN MỚI';
                if (timerSub) timerSub.innerText = 'Phiên trước đã được lưu kho & dọn dẹp theo Điều 5';
                if (phaseInd) phaseInd.innerText = 'Phòng họp trống — Chủ tịch nhập giờ họp mới để triệu tập';
                if (navBadge) {{
                    navBadge.innerText = '✨ PHÒNG TRỐNG';
                    navBadge.style.color = '#38bdf8';
                }}
            }} else if (data.meeting_status === 'WAITING_COUNTDOWN') {{
                const totalSec = data.countdown_seconds || 0;
                const h = Math.floor(totalSec / 3600);
                const m = Math.floor((totalSec % 3600) / 60);
                const s = totalSec % 60;
                if (timerVal) timerVal.innerText = h > 0 ? `${{h}}h ${{String(m).padStart(2,'0')}}m : ${{String(s).padStart(2,'0')}}s` : `${{String(m).padStart(2,'0')}}m : ${{String(s).padStart(2,'0')}}s`;
                if (timerLbl) timerLbl.innerText = '⏱️ ĐỒNG HỒ ĐẾM NGƯỢC GIỜ G';
                if (timerSub) timerSub.innerText = `Khai mạc lúc ${{data.server_hhmm || '00h45'}} • Nghiên cứu T-${{prepMins}}p`;
                if (phaseInd) phaseInd.innerText = '14/14 Phòng Ban đang cào dữ liệu & chuẩn bị trước giờ G';
                if (navBadge) {{
                    navBadge.innerText = `⏳ CHỜ ${{hhmmLabel}}`;
                    navBadge.style.color = '#f59e0b';
                }}
            }} else if (data.meeting_status === 'PRE_MEETING_PREP_15M') {{
                const totalSec = data.countdown_seconds || 0;
                const m = Math.floor(totalSec / 60);
                const s = totalSec % 60;
                if (timerVal) timerVal.innerText = `${{String(m).padStart(2,'0')}}m : ${{String(s).padStart(2,'0')}}s`;
                if (timerLbl) timerLbl.innerText = `🔬 ĐANG NGHIÊN CỨU T-${{prepMins}} PHÚT TRƯỚC HỌP`;
                if (timerSub) timerSub.innerText = `14/14 Ban đang phân tích & nộp hồ sơ (${{data.prep_progress_pct || 0}}%)`;
                if (phaseInd) phaseInd.innerText = `Nghiên cứu T-${{prepMins}}p (Phút ${{data.current_minute}} trước G • ${{data.prep_progress_pct || 0}}%)`;
                if (navBadge) {{
                    navBadge.innerText = `🔬 PREP T${{data.current_minute}}P`;
                    navBadge.style.color = '#c084fc';
                }}
            }} else if (data.meeting_status === 'LIVE_IN_PROGRESS') {{
                const curMin = data.current_minute || 0;
                if (timerVal) timerVal.innerText = `PHÚT ${{curMin}} / ${{durMins}}`;
                if (timerLbl) timerLbl.innerText = '🔴 ĐANG HỌP TRỰC TIẾP';
                if (timerSub) timerSub.innerText = '14/14 Ban đang tranh biện đối kháng (ICT +7)';
                if (phaseInd) phaseInd.innerText = data.current_phase === 1 ? 'Giai Đoạn 1: Vĩ Mô & Tối Ưu Vị Thế' : 'Giai Đoạn 2: Tranh Biện Mở Mới & Biểu Quyết';
                if (navBadge) {{
                    navBadge.innerText = `● LIVE (P.${{curMin}})`;
                    navBadge.style.color = '#ef4444';
                }}
            }} else {{
                if (timerVal) timerVal.innerText = `${{durMins}}m : 00s (BẾ MẠC)`;
                if (timerLbl) timerLbl.innerText = '🏁 HỘI NGHỊ ĐÃ HOÀN TẤT';
                if (timerSub) timerSub.innerText = `Đã đủ T-${{prepMins}}p Prep + ${{durMins}}p Tranh biện`;
                if (phaseInd) phaseInd.innerText = 'Đã hoàn tất 100% nghị trình Hiến Chương V10.0';
                if (navBadge) {{
                    navBadge.innerText = '✅ HOÀN TẤT';
                    navBadge.style.color = '#10b981';
                }}
            }}

            // 1.2 Render Bộ Nội Quy 5 Điều Hiến Chương
            const charterGrid = document.getElementById('summit-charter-rules-grid');
            const charterRules = data.summit_charter_rules || [];
            if (charterGrid && charterRules.length > 0 && !charterGrid.dataset.rendered) {{
                charterGrid.innerHTML = charterRules.map(r => `
                    <div class="summit-charter-card">
                        <div style="color:#fbbf24; font-weight:800; margin-bottom:3px;">${{r.code}}: ${{r.title}}</div>
                        <div style="color:#cbd5e1; font-size:10.5px;">${{r.detail}}</div>
                    </div>
                `).join('');
                charterGrid.dataset.rendered = '1';
            }}

            // 1.5 Render Điểm Danh 14 Phòng Ban & Hồ Sơ Chuẩn Bị T-20 Phút
            const attCountEl = document.getElementById('summit-attendance-count');
            if (attCountEl && data.attendance_summary) attCountEl.innerText = data.attendance_summary;
            const attStrip = document.getElementById('summit-attendance-strip');
            const roster = data.attendance_roster || [];
            if (attStrip) {{
                if (roster.length > 0) {{
                    attStrip.innerHTML = roster.map(r => `
                        <span class="summit-att-badge" title="${{r.officer}}">
                            <span>${{r.avatar || '✅'}}</span>
                            <span>${{r.ban_code}}</span>
                            <span style="color: #34d399;">●</span>
                        </span>
                    `).join('');
                }} else {{
                    attStrip.innerHTML = '<span style="font-size:11px; color:#94a3b8;">Phòng họp đang sạch sẽ, sẵn sàng điểm danh phiên mới.</span>';
                }}
            }}

            const prepGrid = document.getElementById('summit-prep-dossiers-grid');
            const dossiers = data.pre_summit_prep_dossiers || [];
            const dossiersSig = (data.meeting_id || '') + '|' + dossiers.map(d => `${{d.ban_code}}:${{d.status || ''}}`).join(',');
            if (prepGrid && dossiersSig !== lastPrepDossiersSig) {{
                if (dossiers.length > 0) {{
                    prepGrid.innerHTML = dossiers.map(d => {{
                        const isReady = d.status !== 'RESEARCHING_BEFORE_MEETING';
                        const statusColor = isReady ? '#34d399' : '#f59e0b';
                        const statusTxt = isReady ? `✓ ${{d.prep_time}}` : `🔎 ĐANG NGHIÊN CỨU (${{d.prep_time}})`;
                        const kMetrics = Object.entries(d.key_metrics || {{}}).map(([k, v]) =>
                            `<span style="background: rgba(56,189,248,0.1); border: 1px solid rgba(56,189,248,0.22); border-radius: 4px; padding: 2px 6px; font-size: 10px; font-family: 'JetBrains Mono', monospace;"><strong style="color:#7dd3fc;">${{k}}:</strong> ${{v}}</span>`
                        ).join(' ');
                        return `
                            <div class="summit-prep-card">
                                <div style="display:flex; justify-content:space-between; align-items:center; gap:6px;">
                                    <div style="font-size:12px; font-weight:800; color:#f8fafc;">${{d.avatar}} ${{d.ban_code}} — ${{d.officer}}</div>
                                    <span style="font-size:10px; color:${{statusColor}}; font-family:'JetBrains Mono',monospace;">${{statusTxt}}</span>
                                </div>
                                <div style="font-size:11px; color:#94a3b8; font-weight:600;">${{d.dept_name}}</div>
                                <div style="display:flex; flex-wrap:wrap; gap:4px;">${{kMetrics}}</div>
                                <div style="font-size:11.5px; color:#cbd5e1; line-height:1.45;">${{d.pre_meeting_findings}}</div>
                                <div style="font-size:11px; color:#e9d5ff; background: rgba(168,85,247,0.08); border-left:2px solid #a855f7; padding:4px 7px; border-radius:4px;">
                                    🎯 <strong>Đề xuất:</strong> ${{d.proposed_next_week_stance}}
                                </div>
                                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:2px;">
                                    <span style="font-size:10px; color:#64748b;">Nguồn: ${{(d.sources_scanned || []).length}} kho dữ liệu</span>
                                    <button onclick="openReportModal('${{d.report_path}}')" style="background:rgba(56,189,248,0.12); border:1px solid rgba(56,189,248,0.3); color:#38bdf8; font-size:10.5px; font-weight:700; padding:3px 8px; border-radius:5px; cursor:pointer;">📄 Đọc Báo Cáo</button>
                                </div>
                            </div>
                        `;
                    }}).join('');
                }} else {{
                    prepGrid.innerHTML = '<div style="font-size:11.5px; color:#94a3b8; padding:8px;">Chưa có hồ sơ chuẩn bị nào trong phòng hiện tại. Hãy đặt lịch triệu tập họp mới.</div>';
                }}
                lastPrepDossiersSig = dossiersSig;
            }}

            // 2. Cập nhật Step Tracker (1 đến 8) động từ data.phases
            const allPhaseSteps = [];
            (data.phases || []).forEach(ph => {{
                (ph.steps || []).forEach(st => allPhaseSteps.push(st));
            }});
            const curStep = data.current_step || 0;
            for (let i = 1; i <= 8; i++) {{
                const el = document.getElementById('step-node-' + i);
                if (el) {{
                    const stepMeta = allPhaseSteps.find(s => s.step === i);
                    if (stepMeta) {{
                        const minEl = el.querySelector('.summit-step-min');
                        const lblEl = el.querySelector('.summit-step-lbl');
                        if (minEl) minEl.innerText = `${{stepMeta.minute}}m`;
                        if (lblEl) lblEl.innerText = `${{i}}. ${{stepMeta.label}}`;
                    }}
                    el.classList.remove('active', 'completed');
                    if (curStep > 0 && i < curStep) el.classList.add('completed');
                    else if (i === curStep || (curStep === 0 && i === 1 && data.meeting_status !== 'CLEANED_STANDBY')) el.classList.add('active');
                }}
            }}

            // 3. Render Luồng Tin Nhắn
            const container = document.getElementById('summit-feed-container');
            const counter = document.getElementById('summit-feed-counter');
            const msgs = data.timeline_stream || [];

            if (counter) counter.innerText = `${{msgs.length}} phát biểu (Chuẩn bị T-${{prepMins}}p: ${{data.prep_messages_count || 0}} | Tranh biện: ${{data.debate_messages_count || 0}})`;

            if (container) {{
                if (msgs.length !== lastSummitMsgCount) {{
                    if (msgs.length === 0 && data.meeting_status === 'CLEANED_STANDBY') {{
                        container.innerHTML = `
                            <div style="padding: 28px; text-align: center; background: rgba(56, 189, 248, 0.06); border: 1px dashed rgba(56, 189, 248, 0.35); border-radius: 12px; color: #cbd5e1;">
                                <div style="font-size: 28px; margin-bottom: 8px;">✨</div>
                                <div style="font-size: 14px; font-weight: 800; color: #7dd3fc;">PHÒNG HỌP ĐÃ ĐƯỢC LƯU TRỮ &amp; LÀM SẠCH ĐÚNG CHUẨN ĐIỀU 5 HIẾN CHƯƠNG</div>
                                <div style="font-size: 12px; color: #94a3b8; margin-top: 6px;">Chủ tịch có thể mở lại mọi cuộc họp cũ tại <strong>Kho Lưu Trữ Lịch Sử</strong> bên phải hoặc nhập giờ mới bên trên để triệu tập cuộc họp tiếp theo.</div>
                            </div>
                        `;
                    }} else {{
                        container.innerHTML = msgs.map(m => {{
                            let cardClass = 'summit-msg-card';
                            if (m.is_prep_phase) cardClass += ' msg-prep';
                            else if (m.sender_name && m.sender_name.includes('Chủ tịch')) cardClass += ' msg-chairman';
                            else if (m.sender_name && m.sender_name.includes('Trọng')) cardClass += ' msg-inspector';
                            else if (m.badge && (m.badge.includes('TRANH BIỆN') || m.badge.includes('PHẢN BIỆN') || m.badge.includes('CHẤT VẤN') || m.badge.includes('BẢO LƯU') || m.badge.includes('PHẢN ĐỐI') || m.badge.includes('CẢNH BÁO') || m.badge.includes('LOẠI BỎ'))) cardClass += ' msg-debate';
                            else if (m.badge && (m.badge.includes('PHÁP Y') || m.badge.includes('DỮ LIỆU') || m.badge.includes('BCTC'))) cardClass += ' msg-forensic';
                            else if (m.sender_name && m.sender_name.includes('Minh Quân')) cardClass += ' msg-tactical';
                            else if (m.badge && (m.badge.includes('ĐỊNH LƯỢNG') || m.badge.includes('PHÁN QUYẾT') || m.badge.includes('ĐỐI SOÁT') || m.badge.includes('ĐỀ XUẤT') || m.badge.includes('RỦI RO') || m.badge.includes('RÀO CHẮN'))) cardClass += ' msg-quant';

                            let badgeHtml = '';
                            if (m.badge) {{
                                badgeHtml = `<span style="background: ${{m.badge_color || '#38bdf8'}}22; color: ${{m.badge_color || '#38bdf8'}}; border: 1px solid ${{m.badge_color || '#38bdf8'}}55; padding: 2px 8px; border-radius: 9999px; font-size: 10px; font-weight: 800;">${{m.badge}}</span>`;
                            }}

                            let highlightHtml = '';
                            if (m.highlight) {{
                                highlightHtml = `<div class="summit-msg-highlight">📌 <strong>Điểm Nhấn:</strong> ${{m.highlight}}</div>`;
                            }}

                            let metricsHtml = '';
                            if (m.metrics && typeof m.metrics === 'object') {{
                                const chips = Object.entries(m.metrics).map(([k, v]) =>
                                    `<span style="background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12); border-radius: 4px; padding: 2px 7px; font-size: 11px; font-family: 'JetBrains Mono', monospace; color: #cbd5e1;"><strong style="color: #38bdf8;">${{k}}:</strong> ${{v}}</span>`
                                ).join(' ');
                                metricsHtml = `<div style="display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; padding-top: 8px; border-top: 1px dashed rgba(255,255,255,0.1);">${{chips}}</div>`;
                            }}

                            let formattedContent = (Array.isArray(m.content) ? m.content.join(' ') : (m.content || ''))
                                .replace(/\\*\\*(.*?)\\*\\*/g, '<strong style="color: #f8fafc;">$1</strong>')
                                .split(String.fromCharCode(10) + '- ').join('<br/>• ')
                                .split(String.fromCharCode(10)).join('<br/>');

                            let evidenceHtml = '';
                            if (m.evidence_card) {{
                                const ev = m.evidence_card;
                                const cardId = 'ev-card-' + (m.id || Math.random().toString(36).substr(2, 9));

                                const bs = ev.balance_sheet || {{}};
                                const bsChips = Object.entries(bs).map(([k, v]) =>
                                    `<span style="background: rgba(56, 189, 248, 0.08); border: 1px solid rgba(56, 189, 248, 0.2); padding: 3px 8px; border-radius: 4px; font-size: 11px; font-family: 'JetBrains Mono', monospace;"><strong style="color: #7dd3fc;">${{k}}:</strong> <span style="color: #f8fafc;">${{v}}</span></span>`
                                ).join(' ');

                                const peer = ev.peer_comparison || {{}};
                                const peerRows = (peer.comparison_rows || []).map(r => `
                                    <tr>
                                        <td style="font-weight: 600; color: #f8fafc;">${{r.criteria}}</td>
                                        <td style="color: #34d399; font-weight: 700; font-family: 'JetBrains Mono', monospace;">${{r.stock}}</td>
                                        <td style="color: #94a3b8; font-family: 'JetBrains Mono', monospace;">${{r.peer}}</td>
                                        <td style="color: #fbbf24; font-weight: 700;">${{r.verdict}}</td>
                                    </tr>
                                `).join('');

                                const checks = ev.forensic_checks || {{}};
                                const checkBoxes = Object.entries(checks).map(([k, v]) => `
                                    <div class="evidence-check-item">
                                        <div class="evidence-check-k">${{k.replace(/_/g, ' ')}}</div>
                                        <div class="evidence-check-v">${{v}}</div>
                                    </div>
                                `).join('');

                                evidenceHtml = `
                                    <div class="summit-evidence-box">
                                        <div class="summit-evidence-toggle-btn" onclick="toggleEvidenceCard('${{cardId}}')">
                                            <span class="summit-evidence-title">📑 THẺ BẰNG CHỨNG PHÁP Y BCTC SỐNG — ${{ev.ticker}} (KIỂM TOÁN BIG 4)</span>
                                            <span id="btn-${{cardId}}" style="color: #38bdf8; font-weight: 700; font-size: 11px;">▲ THU GỌN BẰNG CHỨNG</span>
                                        </div>
                                        <div id="${{cardId}}" class="summit-evidence-content" style="display: block;">
                                            <div>
                                                <div style="font-size: 10.5px; font-weight: 800; color: #94a3b8; text-transform: uppercase; margin-bottom: 6px;">1. BẢNG CÂN ĐỐI &amp; DÒNG TIỀN KIỂM TOÁN THẬT Q3/2026:</div>
                                                <div style="display: flex; flex-wrap: wrap; gap: 6px;">${{bsChips}}</div>
                                            </div>
                                            <div style="margin-top: 6px;">
                                                <div style="font-size: 10.5px; font-weight: 800; color: #94a3b8; text-transform: uppercase; margin-bottom: 6px;">2. ĐỐI ĐẦU TRỰC DIỆN ĐỐI THỦ CÙNG NGÀNH (${{peer.peer_name || ''}}):</div>
                                                <div style="overflow-x: auto; background: rgba(0,0,0,0.2); border-radius: 6px; padding: 6px;">
                                                    <table class="evidence-peer-table">
                                                        <thead>
                                                            <tr>
                                                                <th>Tiêu Chí Pháp Y</th>
                                                                <th>${{ev.ticker}} (Đề Xuất)</th>
                                                                <th>Đối Thủ Cùng Ngành</th>
                                                                <th>Phán Quyết Ban 2</th>
                                                            </tr>
                                                        </thead>
                                                        <tbody>
                                                            ${{peerRows}}
                                                        </tbody>
                                                    </table>
                                                </div>
                                                <div style="margin-top: 6px; font-size: 11px; color: #7dd3fc; font-style: italic;">
                                                    💡 <strong>Kết luận:</strong> ${{peer.conclusion || ''}}
                                                </div>
                                            </div>
                                            <div style="margin-top: 6px;">
                                                <div style="font-size: 10.5px; font-weight: 800; color: #94a3b8; text-transform: uppercase; margin-bottom: 6px;">3. BỘ RADAR KIỂM ĐỊNH GIAN LẬN KẾ TOÁN (BENEISH M &amp; ALTMAN Z):</div>
                                                <div class="evidence-check-grid">${{checkBoxes}}</div>
                                            </div>
                                        </div>
                                    </div>
                                `;
                            }}

                            return `
                                <div class="${{cardClass}}">
                                    <div class="summit-msg-header">
                                        <div class="summit-msg-author">
                                            <div class="summit-msg-avatar">${{m.avatar || '👤'}}</div>
                                            <div>
                                                <div class="summit-msg-name">${{m.sender_name}}</div>
                                                <div class="summit-msg-dept">${{m.department || ''}} • ${{m.role || ''}}</div>
                                            </div>
                                        </div>
                                        <div style="display: flex; align-items: center; gap: 8px;">
                                            ${{badgeHtml}}
                                            <span class="summit-msg-time">${{m.time_str}}</span>
                                        </div>
                                    </div>
                                    <div class="summit-msg-content">${{formattedContent}}</div>
                                    ${{metricsHtml}}
                                    ${{evidenceHtml}}
                                    ${{highlightHtml}}
                                </div>
                            `;
                        }}).join('');
                        container.scrollTop = container.scrollHeight;
                    }}
                    lastSummitMsgCount = msgs.length;
                }}
            }}

            // 4. Render Bảng Biểu Quyết 14 Ban & Bộ Mã Tâm Điểm
            const voteContainer = document.getElementById('summit-voting-container');
            const votes = data.voting_board || [];
            if (voteContainer) {{
                if (votes.length === 0) {{
                    voteContainer.innerHTML = '<div style="font-size:11px; color:#94a3b8; padding:8px;">Chưa có bảng biểu quyết đang mở.</div>';
                }} else {{
                    voteContainer.innerHTML = votes.map(v => {{
                        const totalV = v.total_voters || 14;
                        let tallyHtml = `<span class="summit-vote-tally" style="color: #34d399;">${{v.votes_for}}/${{totalV}} Nhất Trí</span>`;
                        if (v.status && v.status.includes('REJECT')) {{
                            tallyHtml = `<span class="summit-vote-tally" style="color: #f87171; background: rgba(239,68,68,0.14); border: 1px solid rgba(239,68,68,0.35); padding: 2px 6px; border-radius: 4px;">${{v.votes_for}}/${{totalV}} LOẠI BỎ</span>`;
                        }} else if (v.votes_against > 0 || (v.status && v.status.includes('CONDITION'))) {{
                            tallyHtml = `<span class="summit-vote-tally" style="color: #f59e0b; background: rgba(245,158,11,0.15); border: 1px solid rgba(245,158,11,0.3); padding: 2px 6px; border-radius: 4px;">${{v.votes_for}}/${{totalV}} (${{v.votes_against}} Bảo Lưu)</span>`;
                        }}
                        let orderZoneHtml = v.order_zone ? `<div style="color: #38bdf8; font-weight: 700; font-size: 11px; margin-top: 3px;">📍 Chiến Thuật: ${{v.order_zone}}</div>` : '';
                        let tpRrHtml = (v.take_profit_1 && v.rr_ratio) ? `<div style="color: #a78bfa; font-size: 10.5px; margin-top: 2px;">🎯 TP1: ${{v.take_profit_1}} • TP2: ${{v.take_profit_2 || 'MA20'}} (R:R = ${{v.rr_ratio}})</div>` : '';
                        let actionHtml = v.action ? `<div style="margin-top: 6px; font-size: 11px; color: #7dd3fc; border-top: 1px dashed rgba(255,255,255,0.08); padding-top: 4px;">⚡ ${{v.action}}</div>` : '';
                        let disciplineHtml = v.discipline_note ? `<div style="margin-top: 5px; font-size: 10.5px; color: #fbbf24; background: rgba(245,158,11,0.08); border-left: 2px solid #f59e0b; padding: 4px 6px; border-radius: 4px;">${{v.discipline_note}}</div>` : '';

                        return `
                            <div class="summit-stock-vote-card">
                                <div class="summit-stock-header">
                                    <span class="summit-stock-sym">${{v.ticker}}</span>
                                    ${{tallyHtml}}
                                </div>
                                <div class="summit-stock-meta">
                                    <div><strong>${{v.name}}</strong> (${{v.sector}})</div>
                                    ${{orderZoneHtml}}
                                    <div style="margin-top: 3px; color: #34d399;">Giá: ${{v.price}} • 1 Lô 100 CP: ${{v.lot_cost}}</div>
                                    <div style="color: #94a3b8;">OCF/LNST: ${{v.ocf_lnst}} • Stop: <strong style="color: #f87171;">${{v.stop_loss}}</strong></div>
                                    ${{tpRrHtml}}
                                    ${{actionHtml}}
                                    ${{disciplineHtml}}
                                </div>
                            </div>
                        `;
                    }}).join('');
                }}
            }}

            // 4.5 Render Tổng Kết Master CIO James & Kế Hoạch Tuần Tham Khảo Cơ Động
            const jamesBody = document.getElementById('summit-james-summary-body');
            const jamesBtn = document.getElementById('btn-open-james-summary');
            const jsSum = data.james_executive_summary;
            if (jamesBody) {{
                if (jsSum) {{
                    const hlHtml = (jsSum.meeting_highlights || []).map(h => `<div style="margin-bottom:4px;">• ${{h}}</div>`).join('');
                    const cadHtml = (jsSum.daily_cadence || []).map(c => `
                        <div style="background:rgba(9,14,26,0.75); border:1px solid rgba(56,189,248,0.2); border-radius:6px; padding:6px 8px; margin-top:5px;">
                            <div style="font-weight:800; color:#7dd3fc; font-size:11px;">${{c.day}}: ${{c.focus}}</div>
                            <div style="color:#a7f3d0; font-size:10.5px; margin-top:2px;">⚡ ${{c.trigger}}</div>
                        </div>
                    `).join('');
                    jamesBody.innerHTML = `
                        <div style="font-weight:800; color:#f8fafc; margin-bottom:6px;">${{jsSum.summary_headline || ''}}</div>
                        <div style="color:#cbd5e1; margin-bottom:6px;">${{hlHtml}}</div>
                        <div style="font-size:11px; font-weight:800; color:#34d399; margin-top:6px;">📅 KẾ HOẠCH THAM KHẢO CƠ ĐỘNG TỪNG NGÀY:</div>
                        ${{cadHtml}}
                    `;
                    if (jamesBtn) jamesBtn.style.display = 'block';
                }} else {{
                    jamesBody.innerHTML = '<div style="color:#94a3b8;">Chưa có bản tổng kết James cho trạng thái chờ hiện tại.</div>';
                    if (jamesBtn) jamesBtn.style.display = 'none';
                }}
            }}

            // 5. Cập nhật Trạng Thái Phê Chuẩn của Chủ Tịch & Quy Chế Dọn Phòng 2H
            const appBox = document.getElementById('summit-approval-status');
            const appBtn = document.getElementById('btn-approve-summit');
            const retBox = document.getElementById('summit-retention-status-box');
            const cleanInfo = document.getElementById('summit-cleanup-lock-info');
            const cleanBtn = document.getElementById('btn-archive-clean-summit');
            const resPath = currentSummitResolutionPath;
            const ret = data.retention_status || {{}};

            if (data.executive_approval && data.executive_approval.status === 'APPROVED') {{
                if (appBox) {{
                    appBox.innerHTML = `
                        <div style="background: rgba(16,185,129,0.12); border: 1px solid rgba(16,185,129,0.3); border-radius: 8px; padding: 12px 14px; margin-bottom: 12px;">
                            <div style="color: #34d399; font-weight: 800; font-size: 12px; display: flex; align-items: center; gap: 6px;">
                                <span>👑</span> <span>NGHỊ QUYẾT &amp; BÁO CÁO JAMES ĐÃ ĐƯỢC CHỦ TỊCH KÝ DUYỆT</span>
                            </div>
                            <div style="color: #cbd5e1; font-size: 11px; margin-top: 4px;">Thời gian ký duyệt: <strong>${{data.executive_approval.approval_time}}</strong></div>
                            <div style="color: #fbbf24; font-size: 11px; margin-top: 2px;">🛡️ BAN 12 TRỌNG ĐÃ NIÊM PHONG PHÁP LÝ THỂ CHẾ</div>
                            <div style="color: #38bdf8; font-size: 11px; margin-top: 5px; line-height: 1.4;">🚀 <strong>THỰC THI CƠ ĐỘNG TỪNG NGÀY:</strong> James &amp; Minh Quân sẽ đối soát thực tế lúc 08h30 &amp; Khung Giờ Vàng 14h00–14h25 mỗi phiên!</div>
                        </div>
                        <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                            <button onclick="openReportModal('${{resPath}}')"
                                    style="flex: 1; min-width: 170px; background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: #ffffff; border: none; border-radius: 6px; padding: 10px 12px; font-size: 11px; font-weight: 800; cursor: pointer; text-transform: uppercase; letter-spacing: 0.5px; display: flex; align-items: center; justify-content: center; gap: 6px; box-shadow: 0 2px 10px rgba(16, 185, 129, 0.3);">
                                <span>📄</span> <span>Xem Toàn Văn Nghị Quyết</span>
                            </button>
                            <a href="/api/report?path=${{encodeURIComponent(resPath)}}" target="_blank"
                               style="background: rgba(255, 255, 255, 0.08); color: #cbd5e1; border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 6px; padding: 10px 12px; font-size: 11px; font-weight: 700; text-decoration: none; display: flex; align-items: center; justify-content: center; gap: 6px;">
                                <span>📥</span> <span>Tải Markdown</span>
                            </a>
                        </div>
                    `;
                }}
                if (appBtn) appBtn.style.display = 'none';
            }} else {{
                if (appBtn) appBtn.style.display = data.meeting_status === 'CLEANED_STANDBY' || data.is_archived_view ? 'none' : 'flex';
                if (appBox) {{
                    appBox.innerHTML = `Trạng thái: <strong style="color: #f59e0b;">⏳ Chờ Chủ Tịch Đọc Báo Cáo James &amp; Ký Phê Duyệt</strong>`;
                }}
            }}

            if (retBox && ret.cleanup_lock_reason) {{
                retBox.innerHTML = `⏱️ <strong>Mốc mở khóa dọn phòng 2H:</strong> <span style="color:#7dd3fc;">${{ret.min_cleanup_display || '--'}}</span><br/><span>${{ret.cleanup_lock_reason}}</span>`;
            }}
            if (cleanInfo) {{
                cleanInfo.innerHTML = ret.cleanup_lock_reason || 'Cần Chủ tịch ký duyệt + tối thiểu 2 tiếng sau họp.';
            }}
            if (cleanBtn) {{
                if (ret.can_clean_now) {{
                    cleanBtn.classList.remove('locked');
                    cleanBtn.innerText = '🧹 LƯU KHO HOÀN CHỈNH & DỌN SẠCH PHÒNG HỌP';
                }} else {{
                    cleanBtn.classList.add('locked');
                    const remMin = Math.ceil((ret.seconds_until_2h_unlock || 0) / 60);
                    cleanBtn.innerText = !ret.chairman_approved
                        ? '🔒 CHỜ CHỦ TỊCH KÝ DUYỆT TRƯỚC KHI DỌN PHÒNG'
                        : `🔒 ĐANG KHÓA BẢO LƯU 2H (CÒN ~${{remMin}} PHÚT)`;
                }}
            }}

            // 6. Render Danh Sách Phiên Họp Trong Kho Lưu Trữ (Archive Vault)
            const archSummary = data.archive_summary || {{}};
            const archList = archSummary.sessions || archSummary.archived_sessions || [];
            const archCountEl = document.getElementById('summit-archive-count');
            const archListEl = document.getElementById('summit-archive-history-list');
            if (archCountEl) archCountEl.innerText = String(archSummary.total_archived || archList.length || 0);
            if (archListEl) {{
                if (archList.length === 0) {{
                    archListEl.innerHTML = '<div style="font-size:11px; color:#64748b;">Chưa có phiên họp nào trong Kho Lưu Trữ.</div>';
                }} else {{
                    archListEl.innerHTML = archList.map(s => {{
                        const isActiveArch = currentArchiveViewId && currentArchiveViewId === s.meeting_id;
                        const apprTag = s.chairman_approved ? '<span style="color:#34d399;">✓ Đã duyệt</span>' : '<span style="color:#f59e0b;">⏳ Chưa duyệt</span>';
                        return `
                            <div class="summit-archive-item ${{isActiveArch ? 'active-viewing' : ''}}">
                                <div style="display:flex; justify-content:space-between; align-items:center; gap:6px;">
                                    <strong style="color:#f8fafc;">${{s.meeting_id}}</strong>
                                    ${{apprTag}}
                                </div>
                                <div style="color:#94a3b8; font-size:10.5px;">${{s.meeting_window_str || ''}} • ${{s.archived_display || ''}}</div>
                                <div style="color:#cbd5e1; font-size:10.5px;">${{s.topic || s.title || ''}}</div>
                                <div style="display:flex; gap:6px; flex-wrap:wrap; margin-top:2px;">
                                    <button onclick="loadArchivedSummitSession('${{s.meeting_id}}')" style="background:rgba(56,189,248,0.15); border:1px solid rgba(56,189,248,0.35); color:#7dd3fc; font-size:10px; font-weight:700; padding:3px 8px; border-radius:5px; cursor:pointer;">👁️ Xem Lại Phiên</button>
                                    ${{s.archive_md_path ? `<button onclick="openReportModal('${{s.archive_md_path}}')" style="background:rgba(168,85,247,0.15); border:1px solid rgba(168,85,247,0.35); color:#e9d5ff; font-size:10px; font-weight:700; padding:3px 8px; border-radius:5px; cursor:pointer;">📄 Biên Bản</button>` : ''}}
                                </div>
                            </div>
                        `;
                    }}).join('');
                }}
            }}
        }}

        async function approveSummitResolution() {{
            const btn = document.getElementById('btn-approve-summit');
            if (btn) {{
                btn.disabled = true;
                btn.innerHTML = '<span>⏳</span> <span>Đang Niêm Phong Nghị Quyết & Đóng Dấu Mộc...</span>';
            }}
            try {{
                const res = await fetch('/api/approve_summit_resolution', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ approved_by: 'Chủ tịch Trần Quốc Thiên Phước', timestamp: new Date().toISOString() }})
                }});
                const data = await res.json();
                if (data.ok) {{
                    const unlockDisp = (data.retention_status && data.retention_status.min_cleanup_display) ? data.retention_status.min_cleanup_display : 'sau 2 giờ kể từ khi bế mạc';
                    alert(`🎉 CHÚC MỪNG CHỦ TỊCH!\n\nToàn văn Nghị Quyết Thượng Đỉnh & Báo Cáo Tổng Kết của Master CIO James (${{data.meeting_id || ''}}) đã được Chủ tịch Trần Quốc Thiên Phước chính thức KÝ DUYỆT BAN HÀNH!\n\nTheo Điều 5 Hiến Chương, phiên họp vẫn được giữ nguyên trong phòng đến ${{unlockDisp}} (đủ tối thiểu 2 tiếng sau bế mạc) trước khi chuyển kho lưu trữ & dọn sạch phòng.`);
                    await pollSummitMeeting();
                }} else {{
                    alert('Lỗi phê duyệt: ' + (data.error || 'Không xác định'));
                }}
            }} catch (err) {{
                alert('Lỗi kết nối máy chủ khi phê duyệt: ' + err.message);
            }} finally {{
                if (btn) {{
                    btn.disabled = false;
                    btn.innerHTML = '<span>✍️</span> <span>KÝ PHÊ DUYỆT NGHỊ QUYẾT &amp; BÁO CÁO JAMES</span>';
                }}
            }}
        }}

        async function sendChairmanSummitDirective() {{
            const input = document.getElementById('summit-chairman-input');
            const btn = document.getElementById('summit-btn-send-directive') || document.querySelector('.summit-btn-send');
            if (!input) return;
            const msg = input.value.trim();
            if (!msg) return;

            input.value = '';
            input.disabled = true;
            if (btn) {{
                btn.disabled = true;
                btn.innerHTML = '<span>⏳</span> <span>Đang Phân Tích & Điều Phối...</span>';
            }}

            try {{
                const res = await fetch('/api/summit_message', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ message: msg }})
                }});
                const data = await res.json();
                if (data.ok) {{
                    await pollSummitMeeting();
                    const container = document.getElementById('summit-feed-container');
                    if (container) {{
                        setTimeout(() => {{ container.scrollTop = container.scrollHeight; }}, 80);
                    }}
                    if (typeof appendUserMessage === 'function') {{
                        appendUserMessage(msg);
                    }}
                    if (data.james_resp && typeof appendJamesMessage === 'function') {{
                        appendJamesMessage(data.james_resp.content, data.james_resp.time_str);
                    }}
                }} else {{
                    alert('Lỗi gửi chỉ thị: ' + (data.error || 'Không xác định'));
                }}
            }} catch (err) {{
                alert('Lỗi kết nối máy chủ khi gửi chỉ thị: ' + err.message);
            }} finally {{
                input.disabled = false;
                if (btn) {{
                    btn.disabled = false;
                    btn.innerHTML = '<span>🚀</span> <span>Gửi Chỉ Thị</span>';
                }}
                input.focus();
            }}
        }}

        function initSummitRoom() {{
            pollSummitMeeting();
            if (!summitPollTimer) {{
                summitPollTimer = setInterval(pollSummitMeeting, 2500);
            }}
        }}

        // Tự động kiểm tra URL tham số để mở báo cáo nếu có ?open=

        /* ========================================================
           TAB 3: WAR ROOM JAVASCRIPT ENGINE (REALTIME 24/24)
           ======================================================== */
        let warRoomPollingInterval = null;

        function startLiveClockTicker() {{
            function tick() {{
                const now = new Date();
                const pad = n => n < 10 ? '0' + n : n;
                const timeStr = `${{pad(now.getHours())}}:${{pad(now.getMinutes())}}:${{pad(now.getSeconds())}}`;
                const clockEl = document.getElementById('war-room-clock');
                if (clockEl) clockEl.innerText = timeStr;

                // NY Countdown (21:30)
                const nyMinutes = 21 * 60 + 30;
                const currentMin = now.getHours() * 60 + now.getMinutes();
                let diff = nyMinutes - currentMin;
                if (diff < 0) diff += 24 * 60;
                const countStr = `${{Math.floor(diff / 60)}}h ${{pad(diff % 60)}}m`;
                const nyEl = document.getElementById('war-room-ny-countdown');
                if (nyEl) nyEl.innerText = countStr;
                const alexNyEl = document.getElementById('alex-ny-countdown');
                if (alexNyEl) alexNyEl.innerText = countStr;

                // Live dynamic switcher for 3 afternoon stages
                const curMinutes = now.getHours() * 60 + now.getMinutes();
                const s1Card = document.getElementById('stage-1-card');
                const s2Card = document.getElementById('stage-2-card');
                const s3Card = document.getElementById('stage-3-card');
                const s1Badge = document.getElementById('stage-1-badge');
                const s2Badge = document.getElementById('stage-2-badge');
                const s3Badge = document.getElementById('stage-3-badge');

                if (s1Card && s2Card && s3Card) {{
                    if (curMinutes >= 13 * 60 && curMinutes < 13 * 60 + 45) {{
                        // Stage 1 ACTIVE
                        s1Card.style.border = '1.5px solid rgba(56, 189, 248, 0.6)';
                        s1Card.style.background = 'linear-gradient(135deg, rgba(14, 165, 233, 0.18), rgba(15, 23, 42, 0.9))';
                        if (s1Badge) {{ s1Badge.style.background = 'rgba(56, 189, 248, 0.25)'; s1Badge.style.color = '#38bdf8'; s1Badge.innerHTML = '<span class="war-room-live-dot" style="background:#38bdf8;"></span> ĐANG DIỄN RA'; }}

                        s2Card.style.border = '1px solid rgba(148, 163, 184, 0.2)';
                        s2Card.style.background = 'rgba(30, 41, 59, 0.5)';
                        if (s2Badge) {{ s2Badge.style.background = 'rgba(148, 163, 184, 0.15)'; s2Badge.style.color = '#94a3b8'; s2Badge.innerText = 'CHUẨN BỊ ĐẾN'; }}

                        s3Card.style.border = '1.5px solid rgba(245, 158, 11, 0.4)';
                        if (s3Badge) {{ s3Badge.style.background = 'rgba(245, 158, 11, 0.2)'; s3Badge.style.color = '#fbbf24'; s3Badge.innerText = '⭐ THỜI KHẮC QUYẾT ĐỊNH'; }}
                    }} else if (curMinutes >= 13 * 60 + 45 && curMinutes < 14 * 60) {{
                        // Stage 2 ACTIVE (13:45 - 13:55 No-Supply Check)
                        s1Card.style.border = '1px solid rgba(16, 185, 129, 0.3)';
                        s1Card.style.background = 'rgba(16, 185, 129, 0.05)';
                        if (s1Badge) {{ s1Badge.style.background = 'rgba(16, 185, 129, 0.2)'; s1Badge.style.color = '#34d399'; s1Badge.innerText = '✓ ĐÃ HOÀN TẤT HẤP THỤ'; }}

                        s2Card.style.border = '1.8px solid #38bdf8';
                        s2Card.style.background = 'linear-gradient(135deg, rgba(14, 165, 233, 0.2), rgba(15, 23, 42, 0.95))';
                        if (s2Badge) {{ s2Badge.style.background = 'rgba(56, 189, 248, 0.3)'; s2Badge.style.color = '#38bdf8'; s2Badge.innerHTML = '<span class="war-room-live-dot" style="background:#38bdf8;"></span> ĐANG DIỄN RA (NO-SUPPLY CHECK)'; }}

                        s3Card.style.border = '1.5px solid rgba(245, 158, 11, 0.5)';
                        if (s3Badge) {{ s3Badge.style.background = 'rgba(245, 158, 11, 0.2)'; s3Badge.style.color = '#fbbf24'; s3Badge.innerText = '⭐ SẴN SÀNG BẤM CÒ (14h00)'; }}
                    }} else if (curMinutes >= 14 * 60 && curMinutes <= 14 * 60 + 25) {{
                        // Stage 3 ACTIVE (14:00 - 14:25 GOLDEN HOUR)
                        s1Card.style.border = '1px solid rgba(148, 163, 184, 0.15)';
                        s1Card.style.background = 'rgba(15, 23, 42, 0.5)';
                        if (s1Badge) {{ s1Badge.style.background = 'rgba(148, 163, 184, 0.15)'; s1Badge.style.color = '#94a3b8'; s1Badge.innerText = '✓ ĐÃ QUA'; }}

                        s2Card.style.border = '1px solid rgba(16, 185, 129, 0.3)';
                        s2Card.style.background = 'rgba(16, 185, 129, 0.05)';
                        if (s2Badge) {{ s2Badge.style.background = 'rgba(16, 185, 129, 0.2)'; s2Badge.style.color = '#34d399'; s2Badge.innerText = '✓ ĐẠT CHUẨN CẠN VOL'; }}

                        s3Card.style.border = '2.5px solid #fbbf24';
                        s3Card.style.background = 'linear-gradient(135deg, rgba(245, 158, 11, 0.25), rgba(15, 23, 42, 0.98))';
                        s3Card.style.boxShadow = '0 0 20px rgba(245, 158, 11, 0.35)';
                        if (s3Badge) {{ s3Badge.style.background = '#fbbf24'; s3Badge.style.color = '#0f172a'; s3Badge.style.fontWeight = '900'; s3Badge.innerHTML = '⚡ ⭐ KHUNG GIỜ VÀNG — BẤM CÒ NGAY! ⭐ ⚡'; }}
                    }}
                }}
            }}
            tick();
            setInterval(tick, 1000);
        }}

        let warRoomEventSource = null;

        function setStreamStatusBadge(mode) {{
            const b = document.getElementById('wr-stream-status-badge');
            if (!b) return;
            if (mode === 'sse') {{
                b.style.borderColor = 'rgba(16, 185, 129, 0.45)';
                b.style.background = 'rgba(16, 185, 129, 0.14)';
                b.style.color = '#34d399';
                b.innerText = '🟢 SSE LIVE (REALTIME)';
            }} else {{
                b.style.borderColor = 'rgba(245, 158, 11, 0.45)';
                b.style.background = 'rgba(245, 158, 11, 0.14)';
                b.style.color = '#fbbf24';
                b.innerText = '🟡 POLLING 5S';
            }}
        }}

        function initTacticalWarRoom() {{
            loadTacticalWarRoomData();
            if (warRoomPollingInterval) {{
                clearInterval(warRoomPollingInterval);
                warRoomPollingInterval = null;
            }}
            if (warRoomEventSource) {{
                try {{ warRoomEventSource.close(); }} catch (_) {{}}
                warRoomEventSource = null;
            }}

            if (typeof EventSource !== 'undefined') {{
                try {{
                    warRoomEventSource = new EventSource('/api/tactical_war_room/stream');
                    warRoomEventSource.addEventListener('war_room_tick', (ev) => {{
                        try {{
                            const data = JSON.parse(ev.data);
                            setStreamStatusBadge('sse');
                            renderTacticalWarRoom(data);
                        }} catch (_) {{}}
                    }});
                    warRoomEventSource.onmessage = (ev) => {{
                        try {{
                            const data = JSON.parse(ev.data);
                            setStreamStatusBadge('sse');
                            renderTacticalWarRoom(data);
                        }} catch (_) {{}}
                    }};
                    warRoomEventSource.onerror = () => {{
                        setStreamStatusBadge('polling');
                        if (!warRoomPollingInterval) {{
                            warRoomPollingInterval = setInterval(() => {{
                                loadTacticalWarRoomData();
                            }}, 5000);
                        }}
                    }};
                    return;
                }} catch (_) {{}}
            }}

            setStreamStatusBadge('polling');
            warRoomPollingInterval = setInterval(() => {{
                loadTacticalWarRoomData();
            }}, 5000);
        }}

        async function loadTacticalWarRoomData() {{
            try {{
                const res = await fetch('/api/tactical_war_room');
                if (!res.ok) return;
                const data = await res.json();
                renderTacticalWarRoom(data);
            }} catch (err) {{
                console.warn('Error loading tactical war room data:', err);
            }}
        }}

        function escHtml(str) {{
            return String(str ?? '')
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;');
        }}

        function renderTacticalWarRoom(data) {{
            if (!data) return;

            // 0. Dynamic Stages HTML update
            if (data.tactical_stages_html) {{
                const stagesEl = document.getElementById('afternoon-tactical-stages');
                if (stagesEl) {{
                    stagesEl.outerHTML = data.tactical_stages_html;
                }}
            }}

            // 1. Clocks & Regime Pill
            if (data.server_time) {{
                const clockEl = document.getElementById('war-room-clock');
                if (clockEl) clockEl.innerText = data.server_time;
            }}
            if (data.phase_info && data.phase_info.countdown_to_wall_street) {{
                const nyEl = document.getElementById('war-room-ny-countdown');
                if (nyEl) nyEl.innerText = data.phase_info.countdown_to_wall_street;
                const alexNy = document.getElementById('alex-ny-countdown');
                if (alexNy) alexNy.innerText = data.phase_info.countdown_to_wall_street;
            }}
            if (data.intraday_regime) {{
                const reg = data.intraday_regime;
                const regPill = document.getElementById('wr-regime-pill');
                if (regPill) {{
                    regPill.innerText = reg.label || 'GIẰNG CO';
                    if (reg.badge_color) regPill.style.color = reg.badge_color;
                }}
            }}

            // 2. Active Phase Highlight
            if (data.phase_info && data.phase_info.active_phase_id) {{
                const activeId = data.phase_info.active_phase_id;
                document.querySelectorAll('.phase-step-card').forEach(card => {{
                    card.classList.remove('active');
                }});
                const targetCard = document.getElementById('step-' + activeId);
                if (targetCard) targetCard.classList.add('active');
            }}

            // 3. Action Plan Hero
            if (data.action_plan && data.action_plan.current_step) {{
                const cur = data.action_plan.current_step;
                const timeEl = document.getElementById('action-plan-time');
                const titleEl = document.getElementById('action-plan-title');
                const whatEl = document.getElementById('action-plan-what-to-do');
                const ruleEl = document.getElementById('action-plan-rule');

                if (timeEl) timeEl.innerText = cur.time_range;
                if (titleEl) titleEl.innerText = `📍 ${{cur.title.toUpperCase()}}`;
                if (whatEl) whatEl.innerHTML = `<strong>🎯 HÀNH ĐỘNG CỦA DOANH NGHIỆP TA:</strong><br>${{escHtml(cur.what_to_do)}}`;
                if (ruleEl) ruleEl.innerHTML = `⚖️ <strong>Kỷ Luật Hiến Chương Bắt Buộc</strong>: ${{escHtml(cur.constitution_rule)}}`;
            }}

            // 4. Current Directive Hero Text
            const dirBox = document.getElementById('war-room-live-directive-box');
            if (dirBox && data.tactical_message) {{
                dirBox.innerHTML = escHtml(data.tactical_message);
            }}

            // 5. Left Column Minh Quân Blueprint & Dynamic Picks
            if (data.minh_quan_blueprint) {{
                const mq = data.minh_quan_blueprint;
                const mBadge = document.getElementById('mq-mastery-badge');
                const evEl = document.getElementById('mq-ev-val');
                const pwEl = document.getElementById('mq-pw-val');
                const rrEl = document.getElementById('mq-rr-val');
                const rulesEl = document.getElementById('mq-rules-list');
                if (mBadge && mq.mastery_score !== undefined) mBadge.innerText = `Mastery: ${{Number(mq.mastery_score).toFixed(1)}}/100`;
                if (evEl && mq.expected_value_pct !== undefined) {{
                    const evn = Number(mq.expected_value_pct);
                    evEl.innerText = `EV% ${{evn >= 0 ? '+' : ''}}${{evn.toFixed(2)}}%`;
                }}
                if (pwEl && mq.win_rate_pct !== undefined) pwEl.innerText = `P(W) ${{Number(mq.win_rate_pct).toFixed(1)}}%`;
                if (rrEl && mq.average_rr) rrEl.innerText = `R:R ${{mq.average_rr}}`;
                if (rulesEl && Array.isArray(mq.rules)) {{
                    rulesEl.innerHTML = mq.rules.map(r => `<div style="font-size: 11px; color: #cbd5e1;">• ${{escHtml(r)}}</div>`).join('');
                }}
            }}

            const picksContainer = document.getElementById('war-room-picks-container');
            if (picksContainer && Array.isArray(data.dynamic_picks) && data.dynamic_picks.length > 0) {{
                let topHtml = '';
                let sbHtml = '';
                data.dynamic_picks.forEach((p, idx) => {{
                    const price = Number(p.price || 0);
                    const probe = Number(p.probe_target || price);
                    const stop = Number(p.stop_loss || 0);
                    const tp1 = Number(p.tp1 || 0);
                    const tp2 = Number(p.tp2 || 0);
                    const rr = Number(p.rr_ratio || 0).toFixed(2);
                    const ev = Number(p.ev_pct || 0);
                    const lotVal = ((probe > 0 ? probe : price) * 100).toLocaleString('en-US');
                    if (idx < 2 || p.is_holding) {{
                        const cls = (idx === 0 || p.is_holding) ? 'leader' : 'alpha';
                        const badgeCol = cls === 'leader' ? '#10b981' : '#38bdf8';
                        const badgeTxt = p.is_holding ? `ĐANG GIỮ ${{p.holding_shares || 0}} CP` : String(p.tier || 'MỤC TIÊU').toUpperCase();
                        const stopPct = (price > 0 && stop > 0) ? ` (${{(((stop - price) / price) * 100).toFixed(1)}}%)` : '';
                        const tpStr = (tp1 > 0 && tp2 > 0) ? `${{(tp1/1000).toFixed(2)}}k / ${{(tp2/1000).toFixed(2)}}k` : (tp1 > 0 ? `${{(tp1/1000).toFixed(2)}}k` : 'N/A');
                        topHtml += `
                            <div class="stock-pick-card ${{cls}}">
                                <div class="stock-card-top">
                                    <div>
                                        <span class="stock-ticker">${{escHtml(p.code)}}</span>
                                        <span class="stock-name">${{escHtml(p.name || p.code)}}</span>
                                    </div>
                                    <span style="font-size: 10px; font-weight: 800; color: ${{badgeCol}}; background: rgba(16, 185, 129, 0.15); padding: 2px 6px; border-radius: 4px;">${{escHtml(badgeTxt)}}</span>
                                </div>
                                <div class="stock-stats-grid">
                                    <div class="stock-stat-item"><span class="stat-label">Live / Mục tiêu Gom</span><span class="stat-val">${{price.toLocaleString('en-US')}} / ≤ ${{probe.toLocaleString('en-US')}} ₫</span></div>
                                    <div class="stock-stat-item"><span class="stat-label">Stop 2xATR</span><span class="stat-val loss">${{stop.toLocaleString('en-US')}} ₫${{stopPct}}</span></div>
                                    <div class="stock-stat-item"><span class="stat-label">Mục Tiêu TP1 / TP2</span><span class="stat-val gain">${{tpStr}}</span></div>
                                    <div class="stock-stat-item"><span class="stat-label">Tỷ Lệ R:R</span><span class="stat-val gold">1 : ${{rr}}</span></div>
                                    <div class="stock-stat-item"><span class="stat-label">Kỳ Vọng EV%</span><span class="stat-val gain">${{ev >= 0 ? '+' : ''}}${{ev.toFixed(1)}}%</span></div>
                                    <div class="stock-stat-item"><span class="stat-label">Vốn 100 CP</span><span class="stat-val">${{lotVal}} ₫</span></div>
                                </div>
                                <div class="stock-catalyst">⚡ <strong>${{escHtml(p.security_label || '')}}</strong> | ${{escHtml(p.catalyst || '')}}</div>
                            </div>`;
                    }} else {{
                        sbHtml += `
                            <div class="stock-pick-card standby">
                                <div style="display:flex; justify-content:space-between; align-items:center;">
                                    <span class="stock-ticker">${{escHtml(p.code)}}</span>
                                    <span style="font-size:10px; color:#94a3b8;">${{escHtml(p.action_code || 'STANDBY')}}</span>
                                </div>
                                <div style="font-size:11px; color:#cbd5e1;">Live ${{(price/1000).toFixed(2)}}k | Gom ${{(probe/1000).toFixed(2)}}k | Stop ${{(stop/1000).toFixed(2)}}k</div>
                                <div style="font-size:10px; color:#94a3b8;">${{escHtml((p.catalyst || '').slice(0, 95))}}</div>
                            </div>`;
                    }}
                }});
                picksContainer.innerHTML = topHtml + (sbHtml ? `<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">${{sbHtml}}</div>` : '');
            }}

            // 6. Market Radar Overview (Victor)
            if (data.market_overview) {{
                const mo = data.market_overview;
                const vnPts = document.getElementById('vnindex-pts');
                const vnVal = document.getElementById('vnindex-val');
                const vnTurn = document.getElementById('vnindex-turnover');
                const vnStBadge = document.getElementById('market-status-badge');
                const vn30Pts = document.getElementById('vn30-pts');
                const vn30Val = document.getElementById('vn30-val');
                const vn30Basis = document.getElementById('vn30-basis');
                const fnEl = document.getElementById('foreign-net');
                const brEl = document.getElementById('market-breadth-val');

                if (mo.vn_index) {{
                    const vniChg = Number(mo.vn_index.change_pts || 0);
                    const vniPct = Number(mo.vn_index.change_pct || 0);
                    const vniCol = vniPct >= 0 ? '#34d399' : '#f87171';
                    const vniCls = vniPct >= 0 ? 'price-badge up' : 'price-badge down';
                    if (vnVal) {{
                        vnVal.innerText = Number(mo.vn_index.value || 0).toLocaleString('en-US', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }});
                        vnVal.style.color = vniCol;
                    }}
                    if (vnPts) {{
                        vnPts.className = vniCls;
                        vnPts.innerText = `${{vniChg >= 0 ? '+' : ''}}${{vniChg.toFixed(2)}} (${{vniPct >= 0 ? '+' : ''}}${{vniPct.toFixed(2)}}%)`;
                    }}
                    if (vnTurn && mo.vn_index.turnover_ty_vnd) vnTurn.innerText = mo.vn_index.turnover_ty_vnd;
                    if (vnStBadge && mo.vn_index.status) {{
                        vnStBadge.innerText = '● ' + mo.vn_index.status;
                        vnStBadge.style.color = vniCol;
                    }}
                    if (fnEl && mo.vn_index.foreign_net_ty_vnd) fnEl.innerText = mo.vn_index.foreign_net_ty_vnd;
                }}
                if (mo.vn30_index) {{
                    const vn30Chg = Number(mo.vn30_index.change_pts || 0);
                    const vn30Pct = Number(mo.vn30_index.change_pct || 0);
                    const vn30Col = vn30Pct >= 0 ? '#34d399' : '#f87171';
                    const vn30Cls = vn30Pct >= 0 ? 'price-badge up' : 'price-badge down';
                    if (vn30Val) {{
                        vn30Val.innerText = Number(mo.vn30_index.value || 0).toLocaleString('en-US', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }});
                        vn30Val.style.color = vn30Col;
                    }}
                    if (vn30Pts) {{
                        vn30Pts.className = vn30Cls;
                        vn30Pts.innerText = `${{vn30Chg >= 0 ? '+' : ''}}${{vn30Chg.toFixed(2)}} (${{vn30Pct >= 0 ? '+' : ''}}${{vn30Pct.toFixed(2)}}%)`;
                    }}
                    if (vn30Basis && mo.vn30_index.basis_vn30f) vn30Basis.innerText = mo.vn30_index.basis_vn30f;
                }}
                if (brEl && mo.market_breadth) {{
                    brEl.innerText = `${{mo.market_breadth.advancers || 0}} Tăng / ${{mo.market_breadth.decliners || 0}} Giảm`;
                }}
            }}

            // 7. Live Stock Sentinel Table (Victor)
            if (Array.isArray(data.live_stocks) && data.live_stocks.length > 0) {{
                const tblTitle = document.getElementById('war-room-table-title');
                if (tblTitle) tblTitle.innerText = `🎯 BẢNG GIÁ GIÁM SÁT LIVE (${{data.live_stocks.length}} MÃ SSOT)`;
                const tbody = document.getElementById('live-stocks-table-body');
                if (tbody) {{
                    let tbHtml = '';
                    data.live_stocks.forEach(s => {{
                        const chg = Number(s.change_pct || 0);
                        const isUp = chg > 0;
                        const isDown = chg < 0;
                        const pCls = isUp ? 'up' : (isDown ? 'down' : 'ref');
                        const sign = isUp ? '+' : '';
                        const vol = Number(s.volume || 0);
                        const volStr = vol >= 1000000 ? (vol / 1000000).toFixed(1) + 'M' : (vol / 1000).toFixed(0) + 'k';
                        const sec = String(s.security_status || 'STANDBY');
                        const act = String(s.action_code || sec);
                        const secColor = (sec === 'SAFE' || sec === 'TAKE_PROFIT') ? '#34d399' : ((sec === 'CRITICAL' || sec === 'WARNING') ? '#f87171' : '#fbbf24');
                        const secIcon = sec === 'SAFE' ? '🟢 ' : (sec === 'TAKE_PROFIT' ? '🎯 ' : ((sec === 'CRITICAL' || sec === 'WARNING') ? '🚨 ' : '🟡 '));
                        const buyUp = Number(s.active_buy_pct || 50);

                        tbHtml += `
                            <tr>
                                <td><strong style="color:#38bdf8;">${{escHtml(s.code)}}</strong>${{s.is_holding ? ' ★' : ''}}</td>
                                <td class="price-badge ${{pCls}}">${{Number(s.price || 0).toLocaleString('en-US')}}</td>
                                <td class="price-badge ${{pCls}}">${{sign}}${{chg.toFixed(2)}}%</td>
                                <td>${{volStr}}</td>
                                <td style="color:${{buyUp >= 50 ? '#34d399' : '#f87171'}};">${{buyUp.toFixed(1)}}%</td>
                                <td><span style="color:${{secColor}}; font-weight:700; font-size:10px;">${{secIcon}}${{escHtml(act)}}</span></td>
                            </tr>
                        `;
                    }});
                    tbody.innerHTML = tbHtml;
                }}
            }}

            // 8. Directive Chat Stream (only auto-scroll if near bottom or length changed)
            const chatBox = document.getElementById('directive-history-box');
            if (chatBox && Array.isArray(data.directives_history)) {{
                const prevLen = Number(chatBox.dataset.count || 0);
                let chatHtml = '';
                data.directives_history.forEach(d => {{
                    const roleClass = d.role === 'chairman' ? 'chairman' : (d.role === 'sentinel' ? 'sentinel' : 'specialist');
                    chatHtml += `
                        <div class="directive-msg ${{roleClass}}">
                            <div class="directive-msg-head">
                                <span>${{escHtml(d.sender)}}</span>
                                <span style="font-weight:400; color:#94a3b8;">${{escHtml(d.timestamp)}}</span>
                            </div>
                            <div class="directive-msg-body">${{escHtml(d.content).replace(/\\n/g, '<br>')}}</div>
                        </div>
                    `;
                }});
                chatBox.innerHTML = chatHtml;
                if (data.directives_history.length !== prevLen) {{
                    chatBox.scrollTop = chatBox.scrollHeight;
                    chatBox.dataset.count = String(data.directives_history.length);
                }}
            }}

            // 9. Dynamic Victor Sentinel, Holdings & Threat Radar
            if (data.victor_sentinel) {{
                const vs = data.victor_sentinel;
                const vCash = document.getElementById('victor-cash-val');
                const vHold = document.getElementById('victor-holdings-val');
                const vPnl = document.getElementById('victor-pnl-val');
                const headPill = document.getElementById('wr-header-cash-pill');
                const topKpiCash = document.getElementById('top-kpi-cash-val');
                const topKpiSub = document.getElementById('top-kpi-cash-sub');

                const cashNum = Number(vs.cash_vnd ?? 0);
                const stockNum = Number(vs.stocks_val_vnd ?? 0);
                const navNum = Number(vs.total_nav_vnd ?? (cashNum + stockNum));
                const cashPct = vs.cash_pct !== undefined ? Number(vs.cash_pct).toFixed(1) : (navNum > 0 ? ((cashNum / navNum) * 100).toFixed(1) : '100.0');
                const stockPct = vs.stocks_pct !== undefined ? Number(vs.stocks_pct).toFixed(1) : (100 - Number(cashPct)).toFixed(1);
                const cashFmt = cashNum.toLocaleString('en-US') + ' ₫';
                const stockFmt = stockNum.toLocaleString('en-US') + ' ₫';
                const unPnlNum = Number(vs.unrealized_pnl_vnd ?? 0);
                const pnlFmt = (unPnlNum > 0 ? '+' : '') + unPnlNum.toLocaleString('en-US') + ' ₫';
                const pnlPct = vs.unrealized_pnl_pct !== undefined ? Number(vs.unrealized_pnl_pct).toFixed(2) : '0.00';
                const pnlCol = unPnlNum >= 0 ? '#34d399' : '#f87171';
                const realNum = Number(vs.realized_round1_profit_vnd ?? 0);
                const realFmt = (realNum >= 0 ? '+' : '') + realNum.toLocaleString('en-US') + ' ₫';
                const totalShares = vs.total_shares !== undefined ? vs.total_shares : ((vs.holdings || []).reduce((acc, h) => acc + Number(h.shares || 0), 0));

                if (vCash) vCash.innerText = cashFmt;
                if (vHold) vHold.innerHTML = `Cổ phiếu rủi ro: <strong style="color: #38bdf8;">${{totalShares}} CP (${{stockFmt}} • ${{stockPct}}%)</strong>`;
                if (vPnl) vPnl.innerHTML = `PnL Tạm: <strong style="color: ${{pnlCol}};">${{pnlFmt}} (${{pnlPct}}%)</strong> | Lãi V1: <strong style="color: #34d399;">${{realFmt}}</strong>`;
                if (headPill) headPill.innerHTML = `💰 Két Tiền Thật: <strong style="color: #34d399;">${{cashFmt}}</strong> (${{cashPct}}% Cash) | 📈 Cổ Phiếu: <strong style="color: #38bdf8;">${{stockFmt}}</strong> (${{totalShares}} CP)`;
                if (topKpiCash) topKpiCash.innerText = cashFmt;
                if (topKpiSub) topKpiSub.innerHTML = `<span style="color: #34d399; font-weight: 700;">${{cashPct}}% Cash</span> • ${{totalShares}} CP (${{stockFmt}} • ${{stockPct}}% NAV)`;
                const jamesCash = document.getElementById('james-sidebar-cash-val');
                if (jamesCash) jamesCash.innerText = cashFmt;
                const jamesSub = document.getElementById('james-sidebar-cash-sub');
                if (jamesSub) {{
                    const syms = (vs.holdings || []).map(h => h.symbol).join(', ') || 'Không có';
                    jamesSub.innerText = `Tỷ trọng: ${{cashPct}}% Cash • ${{stockPct}}% CP (${{totalShares}} CP: ${{syms}})`;
                }}

                // Update live holdings box dynamically (0 or N holdings)
                const holdBox = document.getElementById('victor-live-holdings-box');
                if (holdBox) {{
                    const hList = vs.holdings || [];
                    if (hList.length === 0) {{
                        holdBox.innerHTML = `
                            <div style="font-size: 11px; font-weight: 800; color: #34d399; display: flex; justify-content: space-between;">
                                <span>📦 DANH MỤC ĐÃ GIẢI NGÂN (0 MÃ • 0 CP)</span>
                                <span>🛡️ 100% TIỀN MẶT</span>
                            </div>
                            <div style="font-size: 11px; color: #94a3b8; padding: 4px 0;">
                                Két tiền mặt đang bảo toàn 100%, sẵn sàng giải ngân hoặc cập nhật qua Form Sync TCInvest bên dưới.
                            </div>`;
                    }} else {{
                        let hHtml = `
                        <div style="font-size: 11px; font-weight: 800; color: #38bdf8; display: flex; justify-content: space-between;">
                            <span>📦 DANH MỤC ĐÃ GIẢI NGÂN (${{hList.length}} MÃ • ${{totalShares}} CP)</span>
                            <span style="color: #34d399;">🛡️ STOP 2xATR BẢO VỆ</span>
                        </div>
                        <div style="display: flex; flex-direction: column; gap: 5px;">`;
                        hList.forEach(h => {{
                            const sym = escHtml(h.symbol);
                            const sh = Number(h.shares || 0);
                            const ep = Number(h.avg_cost ?? h.entry_price ?? 0);
                            const cp = Number(h.current_price ?? ep);
                            const pnl = Number(h.pnl_vnd ?? h.unrealized_pnl_vnd ?? 0);
                            const pnlP = Number(h.pnl_pct ?? h.unrealized_pnl_pct ?? 0);
                            const pnlColor = pnl >= 0 ? '#34d399' : '#f87171';
                            const sl = Number(h.stop_loss || 0);
                            hHtml += `
                            <div style="background: rgba(30, 41, 59, 0.7); padding: 6px 8px; border-radius: 6px; font-size: 11px; display: flex; justify-content: space-between; align-items: center; gap: 6px; flex-wrap: wrap;">
                                <div><strong style="color: #38bdf8;">${{sym}}</strong> <span style="color: #94a3b8;">(${{sh}} CP)</span></div>
                                <div>Vốn: <span style="color: #cbd5e1;">${{ep.toLocaleString('en-US')}} ₫</span> ➔ Live: <span style="color: ${{pnlColor}};">${{cp.toLocaleString('en-US')}} ₫</span></div>
                                <div>PnL: <strong style="color: ${{pnlColor}};">${{pnl >= 0 ? '+' : ''}}${{pnl.toLocaleString('en-US')}} ₫ (${{pnlP.toFixed(2)}}%)</strong></div>
                                <div style="color: #fbbf24; font-size: 10px;">Stop: ${{sl.toLocaleString('en-US')}} ₫</div>
                            </div>`;
                        }});
                        hHtml += `</div>`;
                        holdBox.innerHTML = hHtml;
                    }}
                    holdBox.style.display = 'flex';
                }}

                // Update Radar 5 Cấp Độ Nguy Hiểm
                const threatCard = document.getElementById('victor-threat-radar-card');
                if (threatCard) {{
                    const lvl = Number(vs.threat_level_num || 1);
                    const lbl = escHtml(vs.threat_label || `CẤP ${{lvl}}`);
                    const col = lvl <= 1 ? '#10b981' : (lvl === 2 ? '#38bdf8' : (lvl === 3 ? '#fbbf24' : '#ef4444'));
                    let bars = '';
                    for (let i = 1; i <= 5; i++) {{
                        const active = i <= lvl;
                        bars += `<div style="flex: 1; height: 6px; border-radius: 3px; background: ${{active ? col : 'rgba(148, 163, 184, 0.2)'}}; ${{active ? 'box-shadow: 0 0 6px ' + col + ';' : ''}}"></div>`;
                    }}
                    threatCard.innerHTML = `
                        <div style="font-size: 11px; font-weight: 800; color: #f8fafc; display: flex; justify-content: space-between;">
                            <span>RADAR 5 CẤP ĐỘ NGUY HIỂM</span>
                            <span style="color: ${{col}};">● CẤP ${{lvl}}</span>
                        </div>
                        <div style="display: flex; gap: 4px;">${{bars}}</div>
                        <div style="font-size: 10.5px; color: #cbd5e1; line-height: 1.35;">${{lbl}}</div>`;
                }}
            }}

            // 10. Weekly Reference Plan Watchlist Sync
            const wlBody = document.getElementById('weekly-roadmap-watchlist-body');
            if (wlBody && data.weekly_reference_plan && Array.isArray(data.weekly_reference_plan.approved_watchlist)) {{
                let wHtml = '';
                data.weekly_reference_plan.approved_watchlist.forEach(w => {{
                    const ex = Number(w.executed_shares || 0) > 0;
                    const sCol = ex ? '#34d399' : '#fbbf24';
                    const sBg = ex ? 'rgba(16, 185, 129, 0.2)' : 'rgba(245, 158, 11, 0.2)';
                    wHtml += `
                        <tr>
                            <td><strong style="color:#38bdf8;">${{escHtml(w.symbol)}}</strong></td>
                            <td><span style="color:#cbd5e1;">${{escHtml(w.tier || '')}}</span></td>
                            <td>${{escHtml(w.entry_zone || '')}}</td>
                            <td style="color:#ef4444; font-weight:700;">${{escHtml(w.stop_loss_2xatr || '')}}</td>
                            <td>${{escHtml(w.tp1 || '')}} / ${{escHtml(w.tp2 || '')}}</td>
                            <td>${{escHtml(w.weekly_limit || '')}}</td>
                            <td><span style="background:${{sBg}}; color:${{sCol}}; padding:2px 6px; border-radius:4px; font-weight:700;">${{escHtml(w.current_status || '')}}</span></td>
                        </tr>`;
                }});
                if (wHtml) wlBody.innerHTML = wHtml;
            }}

            // 11. Global Spillover & Execution Slippage / Bull-Trap KPI Sync
            const spBox = document.getElementById('wr-spillover-slippage-box');
            if (spBox && data.global_spillover) {{
                const sp = data.global_spillover;
                const m = sp.metrics || {{}};
                const trf = (data.execution_tracker && data.execution_tracker.filters) ? data.execution_tracker.filters : {{}};
                const sp500 = m.SP500 || {{}};
                const vix = m.VIX || {{}};
                const dxy = m.DXY || {{}};
                const oil = m.WTI_OIL || {{}};
                const spChg = Number(sp500.change_1d_pct || 0);
                const mult = Number(sp.risk_multiplier || 1.0).toFixed(2);
                const cap = Number(sp.max_allocation_pct || 45);
                const minBu = Number(trf.min_buy_up_pct || 58.0).toFixed(0);
                const maxRsi = Number(trf.max_rsi_buy || 70.0).toFixed(0);
                const sigCnt = Number(trf.total_signals_tracked || 0);
                const avgSlip = Number(trf.avg_slippage_bps || 0);
                const bCol = escHtml(sp.badge_color || '#38bdf8');
                spBox.innerHTML = `
                    <div style="font-size: 10.5px; color: ${{bCol}}; font-weight: 800;">${{escHtml(sp.bias_label || '⚖️ TRUNG TÍNH')}}</div>
                    <div style="font-size: 10.5px; color: #cbd5e1;">
                        Hệ số liên thị trường: <strong style="color:#fff;">${{mult}}x</strong> • Trần giải ngân: <strong style="color:#fbbf24;">${{cap}}% NAV</strong>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 5px; font-size: 10px;">
                        <div style="background: rgba(15, 23, 42, 0.7); padding: 4px 6px; border-radius: 4px; border: 1px solid rgba(148, 163, 184, 0.15);">S&amp;P500: <strong style="color:#38bdf8;">${{spChg >= 0 ? '+' : ''}}${{spChg.toFixed(2)}}%</strong></div>
                        <div style="background: rgba(15, 23, 42, 0.7); padding: 4px 6px; border-radius: 4px; border: 1px solid rgba(148, 163, 184, 0.15);">VIX: <strong style="color:#fbbf24;">${{Number(vix.last_price || 18).toFixed(1)}}</strong></div>
                        <div style="background: rgba(15, 23, 42, 0.7); padding: 4px 6px; border-radius: 4px; border: 1px solid rgba(148, 163, 184, 0.15);">DXY: <strong style="color:#cbd5e1;">${{Number(dxy.last_price || 103).toFixed(1)}}</strong></div>
                        <div style="background: rgba(15, 23, 42, 0.7); padding: 4px 6px; border-radius: 4px; border: 1px solid rgba(148, 163, 184, 0.15);">WTI Oil: <strong style="color:#34d399;">${{Number(oil.last_price || 0).toFixed(1)}}$</strong></div>
                    </div>
                    <div style="margin-top: 2px; padding-top: 5px; border-top: 1px dashed rgba(148, 163, 184, 0.25); font-size: 10px; color: #94a3b8;">
                        🎯 <strong>Bộ Lọc Bull-Trap &amp; Slippage:</strong> BuyUp &ge; <strong style="color:#34d399;">${{minBu}}%</strong> • RSI &le; <strong style="color:#fbbf24;">${{maxRsi}}</strong> • Tín hiệu: <strong style="color:#fff;">${{sigCnt}}</strong> (Slip: ${{avgSlip >= 0 ? '+' : ''}}${{avgSlip.toFixed(1)}} bps)
                    </div>`;
            }}

            // 12. V5.0/V6.0 Deep Financial Brain, Catalyst Radar, 60D Correlation & 15 World Legends Sync
            const dbSum = data.deep_brain_summary || {{}};
            const cStats = dbSum.omni_crawler_stats || {{}};
            const iqData = dbSum.system_maturity_iq || {{}};
            const corrSum = dbSum.correlation_summary || {{}};
            const catAlerts = dbSum.catalyst_alerts || {{}};
            const wfMap = dbSum.multi_horizon_walk_forward || {{}};
            const cBadge = document.getElementById('omni-crawler-badge');
            if (cBadge && (cStats.total_items || cStats.total_universe)) {{
                cBadge.innerText = `📡 Crawler: ${{cStats.total_universe || 180}} mã • ${{cStats.total_items || 0}} tin • BCTC Live: ${{cStats.live_bctc_updates_count || 0}}`;
            }}
            const mBadge = document.getElementById('omni-maturity-badge');
            if (mBadge && iqData.maturity_score) {{
                mBadge.innerText = `🎓 Maturity: ${{Number(iqData.maturity_score).toFixed(1)}}/100 • IQ ${{Number(iqData.collective_iq || 158).toFixed(1)}}`;
            }}
            const catStrip = document.getElementById('wr-omni-catalyst-strip');
            if (catStrip) {{
                const alList = catAlerts.alerts || [];
                const badgesHtml = alList.slice(0, 3).map(al => {{
                    const p = String(al.priority || '');
                    const col = p.includes('RISK') ? '#f87171' : (p.includes('HOLDING') ? '#34d399' : '#38bdf8');
                    const imp = Number(al.estimated_fair_value_impact_pct || 0);
                    return `<button onclick="inspectDeepBrainTicker('${{escHtml(al.symbol || '')}}')" style="cursor:pointer; background:rgba(30,41,59,0.9); border:1px solid ${{col}}; color:${{col}}; border-radius:5px; padding:2px 7px; font-size:10px; font-weight:700;">${{escHtml(al.symbol || '')}} (${{imp >= 0 ? '+' : ''}}${{imp.toFixed(1)}}% FV): ${{escHtml(String(al.title || '').slice(0, 42))}}...</button>`;
                }}).join('');
                catStrip.innerHTML = `<span style="color:#fbbf24; font-weight:800;">⚡ Catalyst: ${{catAlerts.total_alerts || 0}} (Nắm giữ: ${{catAlerts.holding_alerts_count || 0}} • Rủi ro: ${{catAlerts.risk_alerts_count || 0}})</span> <span style="color:#94a3b8;">| 🔗 Corr 60D: ${{corrSum.live_60d_series_fetched || 0}} chuỗi sống</span> ${{badgesHtml}}`;
            }}
            const alphaBody = document.getElementById('omni-alpha-picks-body');
            const topPicks = dbSum.top_vn_alpha_picks || [];
            if (alphaBody && topPicks.length > 0) {{
                alphaBody.innerHTML = topPicks.map(p => {{
                    const mos = Number(p.margin_of_safety_pct || 0);
                    const ev = Number(p.ev_pct || 0);
                    const corrVal = Number(p.max_corr_with_holdings || 0);
                    const cStat = String(p.corr_guard_status || 'CLEAR');
                    const cCol = cStat.includes('CLUSTER') ? '#f87171' : (cStat.includes('OVERLAP') ? '#fbbf24' : '#34d399');
                    const cLbl = cStat.includes('HOLDING') ? 'HOLD' : (cStat.includes('CLUSTER') ? '0.75x' : 'CLEAR');
                    const symEsc = escHtml(p.symbol || '');
                    return `<tr>
                        <td><button onclick="inspectDeepBrainTicker('${{symEsc}}')" style="background:rgba(56,189,248,0.16); border:1px solid rgba(56,189,248,0.4); color:#38bdf8; font-weight:800; border-radius:4px; padding:2px 6px; cursor:pointer;">${{symEsc}}</button></td>
                        <td style="font-weight:700;">${{Number(p.live_price || 0).toLocaleString('en-US')}}đ</td>
                        <td><strong style="color:#fbbf24;">${{Number(p.alpha_score || 0).toFixed(1)}}</strong></td>
                        <td style="color:${{mos >= 15 ? '#34d399' : '#e2e8f0'}};">${{mos >= 0 ? '+' : ''}}${{mos.toFixed(1)}}%</td>
                        <td style="color:#34d399; font-weight:800;">${{ev >= 0 ? '+' : ''}}${{ev.toFixed(2)}}%</td>
                        <td>1:${{Number(p.rr_ratio || 0).toFixed(2)}}</td>
                        <td style="color:${{cCol}}; font-weight:700;">${{corrVal.toFixed(2)}} <span style="font-size:9px;">(${{cLbl}})</span></td>
                        <td>${{Number(p.suggested_shares_lot100 || 0)}} CP • <span style="color:#93c5fd;">${{escHtml(p.action_signal || '')}}</span></td>
                    </tr>`;
                }}).join('');
            }}
            const mBox = document.getElementById('omni-maturity-metrics');
            if (mBox && iqData.maturity_score) {{
                const cnts = iqData.classification_counts || {{}};
                mBox.innerHTML = `
                    <div style="background:rgba(30,41,59,0.75); padding:6px 8px; border-radius:6px; border:1px solid rgba(52,211,153,0.25);">
                        <div style="color:#94a3b8; font-size:9.5px;">MATURITY / IQ</div>
                        <div style="color:#34d399; font-weight:900;">${{Number(iqData.maturity_score).toFixed(1)}} / ${{Number(iqData.collective_iq || 158).toFixed(1)}}</div>
                    </div>
                    <div style="background:rgba(30,41,59,0.75); padding:6px 8px; border-radius:6px; border:1px solid rgba(56,189,248,0.25);">
                        <div style="color:#94a3b8; font-size:9.5px;">WIN RATE / BRIER</div>
                        <div style="color:#38bdf8; font-weight:900;">${{Number(iqData.win_rate_pct || 0).toFixed(1)}}% • ${{Number(iqData.brier_calibration_score || 0).toFixed(3)}}</div>
                    </div>
                    <div style="background:rgba(30,41,59,0.75); padding:6px 8px; border-radius:6px; border:1px solid rgba(251,191,36,0.25);">
                        <div style="color:#94a3b8; font-size:9.5px;">HÀNH VI ĐÚNG / BỎ LỠ</div>
                        <div style="color:#fbbf24; font-weight:900;">✅ ${{cnts.EXECUTION_EXCELLENCE || 0}} • 🧭 ${{cnts.DISCIPLINED_PASS || 0}} • 💡 ${{cnts.OMISSION_ERROR || 0}}</div>
                    </div>`;
            }}
            const wfStrip = document.getElementById('omni-walk-forward-strip');
            if (wfStrip) {{
                const keys = ['T+3', 'T+5', 'T+10', 'T+20'];
                const cells = keys.map(hk => {{
                    const hv = wfMap[hk] || {{}};
                    const hr = Number(hv.hit_rate_pct || 0);
                    const ar = Number(hv.avg_return_pct || 0);
                    return `<div style="background:rgba(30,41,59,0.65); padding:4px 6px; border-radius:5px; border:1px solid rgba(148,163,184,0.2); text-align:center;">
                        <div style="color:#94a3b8; font-weight:700;">Walk ${{hk}}</div>
                        <div style="color:${{hr >= 60 ? '#34d399' : '#fbbf24'}}; font-weight:800;">${{hr.toFixed(1)}}% (${{ar >= 0 ? '+' : ''}}${{ar.toFixed(1)}}%)</div>
                    </div>`;
                }}).join('');
                wfStrip.innerHTML = cells;
            }}
            const lBox = document.getElementById('omni-legends-cards');
            const lList = dbSum.legends_top_picks || [];
            if (lBox && lList.length > 0) {{
                lBox.innerHTML = lList.map(ev => {{
                    const sc = Number(ev.consensus_legends_score || 0);
                    const col = sc >= 75 ? '#34d399' : (sc >= 65 ? '#38bdf8' : '#fbbf24');
                    return `<div style="background:rgba(30,41,59,0.7); border:1px solid rgba(148,163,184,0.22); border-radius:7px; padding:7px 9px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <strong style="color:#f8fafc; font-size:12px;">${{escHtml(ev.symbol || '')}} <span style="font-size:9.5px; color:#94a3b8;">(${{escHtml(ev.market || 'VN')}})</span></strong>
                            <span style="color:${{col}}; font-weight:900; font-size:11.5px;">${{sc.toFixed(1)}}/100 (${{ev.supporting_legends_count || 0}}/15)</span>
                        </div>
                        <div style="font-size:9.5px; color:#cbd5e1; margin-top:2px;">🏆 ${{escHtml(ev.top_advocate || '')}}</div>
                        <div style="font-size:9px; color:#94a3b8; margin-top:1px;">⚖️ Phản biện: ${{escHtml(ev.key_dissent || '')}}</div>
                    </div>`;
                }}).join('');
            }}

            // 13. V7.0 Living Enterprise & Inter-Departmental Collaboration Mesh
            if (data.enterprise_mesh_summary) {{
                renderEnterpriseMeshPanel(data.enterprise_mesh_summary);
            }}

            // 14. V8.0 Live Multi-Department War-Room Floor & Portfolio Tab Sync
            if (data.victor_deep_surveillance) {{
                renderVictorDeepSurveillance(data.victor_deep_surveillance);
            }}
            if (data.live_execution_master_plan) {{
                renderLiveExecutionMasterPlan(data.live_execution_master_plan);
            }}
            if (data.department_live_workstation || data.latest_reports_feed) {{
                renderDeptWorkstationAndReports(
                    data.department_live_workstation || [],
                    data.latest_reports_feed || [],
                    data.vault_sync_meta || {{}}
                );
            }}
            if (data.vault_sync_meta) {{
                syncPortalReportsSilently(data.vault_sync_meta, false);
            }}
            if (data.victor_deep_surveillance) {{
                renderPortfolioTabLiveFromWarRoom(
                    data.victor_deep_surveillance,
                    data.live_execution_master_plan || {{}}
                );
            }}
        }}

        function renderVictorDeepSurveillance(vData) {{
            if (!vData) return;
            const hdEl = document.getElementById('victor-surveillance-headline');
            if (hdEl) {{
                hdEl.innerHTML = `${{escHtml(vData.victor_headline || '')}} <span style="color:#94a3b8; font-weight:600; font-size:11px;">(Cập nhật: ${{escHtml(vData.surveillance_timestamp || '')}})</span>`;
            }}

            const heldBody = document.getElementById('victor-held-surveillance-tbody');
            const heldList = vData.held_positions_book || [];
            if (heldBody) {{
                if (heldList.length === 0) {{
                    heldBody.innerHTML = '<tr><td colspan="9" style="text-align:center; padding:12px; color:#94a3b8;">Hiện đang giữ 100% tiền mặt — Chưa mở vị thế cổ phiếu.</td></tr>';
                }} else {{
                    heldBody.innerHTML = heldList.map(h => {{
                        const pnlVal = Number(h.pnl_vnd || 0);
                        const pnlPct = Number(h.pnl_pct || 0);
                        const chgPct = Number(h.change_pct || 0);
                        const pnlCol = pnlVal >= 0 ? '#34d399' : '#f87171';
                        const chgCol = chgPct >= 0 ? '#34d399' : '#f87171';
                        const buyUp = Number(h.active_buy_pct || 50);
                        return `<tr>
                            <td style="padding:8px 10px;">
                                <strong style="color:#38bdf8; font-family:'JetBrains Mono',monospace;">${{escHtml(h.symbol || '')}}</strong>
                                <div style="font-size:10px; color:#94a3b8;">${{Number(h.shares || 0)}} CP (T0: ${{Number(h.tradable_shares || 0)}})</div>
                            </td>
                            <td style="padding:8px 10px; font-family:'JetBrains Mono',monospace;">
                                <strong>${{Number(h.live_price || 0).toLocaleString('en-US')}}đ</strong>
                                <div style="font-size:10px; color:${{chgCol}};">${{chgPct >= 0 ? '+' : ''}}${{chgPct.toFixed(2)}}% • L:${{Number(h.intraday_low || 0).toLocaleString('en-US')}} H:${{Number(h.intraday_high || 0).toLocaleString('en-US')}}</div>
                            </td>
                            <td style="padding:8px 10px; font-family:'JetBrains Mono',monospace; color:#cbd5e1;">
                                ${{Number(h.entry_price || 0).toLocaleString('en-US')}}đ
                                <div style="font-size:10px; color:${{pnlCol}}; font-weight:800;">${{pnlVal >= 0 ? '+' : ''}}${{pnlVal.toLocaleString('en-US')}}đ (${{pnlPct >= 0 ? '+' : ''}}${{pnlPct.toFixed(2)}}%)</div>
                            </td>
                            <td style="padding:8px 10px;">
                                <div style="font-weight:800; color:${{buyUp >= 58 ? '#34d399' : (buyUp < 45 ? '#f87171' : '#fbbf24')}};">BuyUp ${{buyUp.toFixed(1)}}% • B/A ${{Number(h.bid_ask_ratio || 1).toFixed(2)}}x</div>
                                <div style="font-size:10px; color:#94a3b8;">${{escHtml(h.orderbook_pressure || '')}}</div>
                            </td>
                            <td style="padding:8px 10px; font-family:'JetBrains Mono',monospace; color:#f87171;">
                                ${{Number(h.stop_loss || 0).toLocaleString('en-US')}}đ
                                <div style="font-size:10px; color:#cbd5e1;">Cách +${{Number(h.stop_distance_pct || 0).toFixed(2)}}%</div>
                            </td>
                            <td style="padding:8px 10px; font-family:'JetBrains Mono',monospace; color:#34d399;">
                                ${{Number(h.tp1 || 0).toLocaleString('en-US')}} / ${{Number(h.tp2 || 0).toLocaleString('en-US')}}
                                <div style="font-size:10px; color:#a7f3d0;">TP1 +${{Number(h.tp1_upside_pct || 0).toFixed(1)}}%</div>
                            </td>
                            <td style="padding:8px 10px; font-family:'JetBrains Mono',monospace; color:#fbbf24;">
                                ${{Number(h.t0_buy_zone || 0).toLocaleString('en-US')}} → ${{Number(h.t0_sell_zone || 0).toLocaleString('en-US')}}
                                <div style="font-size:10px; color:#94a3b8;">OCF ${{Number(h.ocf_ratio || 1).toFixed(2)}}x • MOS ${{Number(h.mos_pct || 0).toFixed(1)}}%</div>
                            </td>
                            <td style="padding:8px 10px; font-size:11px;">
                                <div style="font-weight:800; color:#f8fafc;">${{escHtml(h.victor_status_badge || '')}}</div>
                                <div style="color:#cbd5e1; margin-top:2px;">${{escHtml(h.victor_instruction || '')}}</div>
                            </td>
                        </tr>`;
                    }}).join('');
                }}
            }}

            const watchBody = document.getElementById('victor-alpha-watchlist-tbody');
            const watchList = vData.alpha_watchlist_book || [];
            if (watchBody) {{
                watchBody.innerHTML = watchList.map(w => {{
                    const chg = Number(w.change_pct || 0);
                    const chgCol = chg >= 0 ? '#34d399' : '#f87171';
                    const ok = !!w.constitutional_lot_ok;
                    return `<tr>
                        <td style="padding:7px 9px;">
                            <strong style="color:#fbbf24; font-family:'JetBrains Mono',monospace;">${{escHtml(w.symbol || '')}}</strong>
                            <div style="font-size:10px; color:#94a3b8;">${{escHtml(w.sector_name || '')}}</div>
                        </td>
                        <td style="padding:7px 9px; font-family:'JetBrains Mono',monospace;">
                            <strong>${{Number(w.live_price || 0).toLocaleString('en-US')}}đ</strong>
                            <span style="color:${{chgCol}}; font-size:10px; font-weight:700;"> (${{chg >= 0 ? '+' : ''}}${{chg.toFixed(2)}}%)</span>
                            <div style="font-size:10px; color:#94a3b8;">Canh nhúng: ${{Number(w.probe_target || 0).toLocaleString('en-US')}}đ</div>
                        </td>
                        <td style="padding:7px 9px; font-family:'JetBrains Mono',monospace;">
                            BuyUp ${{Number(w.active_buy_pct || 50).toFixed(1)}}% • RSI ${{Number(w.rsi14 || 50).toFixed(1)}}
                        </td>
                        <td style="padding:7px 9px; font-family:'JetBrains Mono',monospace;">
                            OCF ${{Number(w.ocf_ratio || 1).toFixed(2)}}x • MOS <strong style="color:#34d399;">+${{Number(w.mos_pct || 0).toFixed(1)}}%</strong>
                        </td>
                        <td style="padding:7px 9px; font-family:'JetBrains Mono',monospace;">
                            Alpha <strong style="color:#38bdf8;">${{Number(w.alpha_score || 0).toFixed(1)}}</strong> • 1:${{Number(w.rr_ratio || 0).toFixed(2)}} (EV ${{Number(w.ev_pct || 0) >= 0 ? '+' : ''}}${{Number(w.ev_pct || 0).toFixed(1)}}%)
                        </td>
                        <td style="padding:7px 9px; font-family:'JetBrains Mono',monospace;">
                            ${{Number(w.lot_100_cost_vnd || 0).toLocaleString('en-US')}}đ
                            <div style="font-size:10px; color:${{ok ? '#34d399' : '#f87171'}};">${{Number(w.nav_pct_per_lot || 0).toFixed(1)}}% NAV (${{ok ? 'Đạt <=33%' : 'Vượt trần'}})</div>
                        </td>
                        <td style="padding:7px 9px; font-size:11px;">
                            <div style="font-weight:800; color:${{w.victor_signal && w.victor_signal.includes('SẴN SÀNG') ? '#34d399' : (ok ? '#fbbf24' : '#f87171')}};">${{escHtml(w.victor_signal || '')}}</div>
                            <div style="font-size:10px; color:#94a3b8; margin-top:2px;">${{escHtml(w.catalyst || '')}}</div>
                        </td>
                    </tr>`;
                }}).join('');
            }}
        }}

        function renderLiveExecutionMasterPlan(plan) {{
            if (!plan) return;
            const sumEl = document.getElementById('wr-master-plan-summary-banner');
            if (sumEl) {{
                const vniChg = Number(plan.vn_index_change_pts || 0);
                const vniPct = Number(plan.vn_index_change_pct || 0);
                sumEl.innerHTML = `
                    <div style="display:flex; flex-wrap:wrap; justify-content:space-between; gap:8px; align-items:center;">
                        <div>
                            <strong style="color:#38bdf8; font-family:'JetBrains Mono',monospace;">${{escHtml(plan.plan_id || '')}}</strong>
                            <span style="color:#cbd5e1; margin-left:8px;">Pha: <strong>${{escHtml(plan.session_phase_label || '')}}</strong> • VN-Index: <strong>${{Number(plan.vn_index_value || 0).toLocaleString('en-US', {{minimumFractionDigits:2, maximumFractionDigits:2}})}}</strong> (${{vniChg >= 0 ? '+' : ''}}${{vniChg.toFixed(2)}} / ${{vniPct >= 0 ? '+' : ''}}${{vniPct.toFixed(2)}}%) • Breadth ${{plan.breadth_advancers || 0}}↑/${{plan.breadth_decliners || 0}}↓</span>
                        </div>
                        <div style="display:flex; gap:8px; flex-wrap:wrap; align-items:center;">
                            <span style="background:rgba(16,185,129,0.16); border:1px solid rgba(16,185,129,0.4); color:#34d399; padding:3px 9px; border-radius:6px; font-weight:800; font-size:11px;">Tiền mặt: ${{Number(plan.cash_available_vnd || 0).toLocaleString('en-US')}}đ (${{Number(plan.cash_pct || 0).toFixed(1)}}%)</span>
                            <span style="background:rgba(56,189,248,0.16); border:1px solid rgba(56,189,248,0.4); color:#38bdf8; padding:3px 9px; border-radius:6px; font-weight:800; font-size:11px;">Trần giải ngân mới: ${{Number(plan.max_new_allocation_pct || 0).toFixed(0)}}% NAV (~${{Number(plan.max_deployable_vnd || 0).toLocaleString('en-US')}}đ)</span>
                        </div>
                    </div>
                    <div style="margin-top:6px; font-size:11.5px; color:#e2e8f0;">📜 <strong>Nghị quyết Doanh nghiệp (${{escHtml(plan.enterprise_session_id || 'LIVE')}}):</strong> ${{escHtml(plan.enterprise_action_summary || plan.enterprise_verdict || '')}}</div>
                `;
            }}

            const holdCardsEl = document.getElementById('wr-master-plan-holdings-cards');
            if (holdCardsEl) {{
                const items = plan.holdings_action_items || [];
                holdCardsEl.innerHTML = items.map(h => {{
                    const pv = Number(h.pnl_vnd || 0);
                    return `<div style="background:rgba(15,23,42,0.8); border:1px solid rgba(56,189,248,0.28); border-radius:8px; padding:10px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <strong style="color:#38bdf8; font-size:13px;">${{escHtml(h.symbol || '')}} (${{h.shares || 0}} CP)</strong>
                            <span style="color:${{pv >= 0 ? '#34d399' : '#f87171'}}; font-weight:800; font-size:11.5px;">${{pv >= 0 ? '+' : ''}}${{pv.toLocaleString('en-US')}}đ (${{Number(h.pnl_pct || 0).toFixed(2)}}%)</span>
                        </div>
                        <div style="font-size:11px; color:#cbd5e1; margin-top:4px;">Giá live: <strong>${{Number(h.current_price || 0).toLocaleString('en-US')}}đ</strong> • Stop: <span style="color:#f87171;">${{Number(h.stop_loss || 0).toLocaleString('en-US')}}đ</span> • TP1: <span style="color:#34d399;">${{Number(h.tp1 || 0).toLocaleString('en-US')}}đ</span></div>
                        <div style="font-size:11px; color:#fbbf24; margin-top:3px;">Vùng lướt T+0: ${{escHtml(h.t0_zone || '')}}</div>
                        <div style="font-size:11px; color:#e2e8f0; margin-top:4px;">${{escHtml(h.tactical_order_text || '')}}</div>
                    </div>`;
                }}).join('');
            }}

            const ordersBody = document.getElementById('wr-master-plan-orders-tbody');
            if (ordersBody) {{
                const orders = plan.new_deployment_orders || [];
                ordersBody.innerHTML = orders.map(o => `<tr>
                    <td style="padding:7px 9px;"><strong style="color:#fbbf24; font-family:'JetBrains Mono',monospace;">${{escHtml(o.symbol || '')}}</strong></td>
                    <td style="padding:7px 9px; font-size:11px; color:#e2e8f0;">${{escHtml(o.order_type || '')}}</td>
                    <td style="padding:7px 9px; font-family:'JetBrains Mono',monospace; color:#38bdf8;">${{escHtml(o.limit_buy_zone || '')}}</td>
                    <td style="padding:7px 9px; font-family:'JetBrains Mono',monospace;"><span style="color:#f87171;">${{Number(o.stop_loss || 0).toLocaleString('en-US')}}</span> / <span style="color:#34d399;">${{Number(o.tp1 || 0).toLocaleString('en-US')}}</span></td>
                    <td style="padding:7px 9px; font-family:'JetBrains Mono',monospace;">${{Number(o.est_capital_vnd || 0).toLocaleString('en-US')}}đ (${{Number(o.nav_weight_pct || 0).toFixed(1)}}%)</td>
                    <td style="padding:7px 9px; font-size:11px;">
                        <div style="font-weight:800; color:#f8fafc;">${{escHtml(o.approval_status || '')}}</div>
                        <div style="color:#94a3b8;">${{escHtml(o.trigger_condition || '')}}</div>
                    </td>
                </tr>`).join('');
            }}

            const scenEl = document.getElementById('wr-master-plan-scenarios-grid');
            if (scenEl) {{
                const scens = plan.contingency_scenarios || [];
                const cols = ['#10b981', '#fbbf24', '#ef4444'];
                scenEl.innerHTML = scens.map((sc, idx) => `<div style="background:rgba(15,23,42,0.78); border-left:3px solid ${{cols[idx % 3]}}; border-radius:8px; padding:10px;">
                    <div style="font-size:11.5px; font-weight:800; color:${{cols[idx % 3]}};">${{escHtml(sc.title || '')}}</div>
                    <div style="font-size:11px; color:#94a3b8; margin-top:4px;"><strong>Điều kiện:</strong> ${{escHtml(sc.trigger || '')}}</div>
                    <div style="font-size:11px; color:#e2e8f0; margin-top:4px;"><strong>Hành động:</strong> ${{escHtml(sc.portfolio_action || '')}} (Tiền mặt mục tiêu: ${{Number(sc.cash_target_pct || 0).toFixed(1)}}%)</div>
                </div>`).join('');
            }}
        }}

        function renderDeptWorkstationAndReports(depts, feed, meta) {{
            const badge = document.getElementById('wr-vault-sync-badge');
            if (badge && meta) {{
                badge.innerText = `🟢 Vault Sync: ${{meta.today_reports_count || 0}} Hôm nay / ${{meta.total_reports_scanned || 0}} Kho (${{meta.latest_sync_time || ''}})`;
            }}

            const grid = document.getElementById('wr-dept-workstation-grid');
            if (grid && Array.isArray(depts) && depts.length > 0) {{
                grid.innerHTML = depts.map(d => {{
                    const st = String(d.stance || 'ACTIVE_MONITOR');
                    const stCol = st === 'VETO' ? '#ef4444' : (st === 'CAUTION' ? '#fbbf24' : '#34d399');
                    const repPath = String(d.latest_report_path || '');
                    const safePath = repPath.replace(/\\\\/g, '/').replace(/'/g, "\\\\'");
                    return `<div style="background:rgba(15,23,42,0.82); border:1px solid rgba(148,163,184,0.22); border-radius:9px; padding:10px; display:flex; flex-direction:column; justify-content:space-between; gap:6px;">
                        <div>
                            <div style="display:flex; justify-content:space-between; align-items:center; gap:6px;">
                                <strong style="color:#38bdf8; font-size:11.5px;">${{escHtml(d.ban_code || '')}} • ${{escHtml(d.officer || '')}}</strong>
                                <span style="background:${{stCol}}22; color:${{stCol}}; border:1px solid ${{stCol}}55; padding:1px 6px; border-radius:4px; font-size:9.5px; font-weight:800;">● ${{escHtml(st)}}</span>
                            </div>
                            <div style="font-size:10.5px; color:#94a3b8; margin-top:2px;">${{escHtml(d.dept_name || '')}}</div>
                            <div style="font-size:11px; color:#e2e8f0; margin-top:5px; line-height:1.45;">${{escHtml(d.live_finding || '')}}</div>
                        </div>
                        <div style="display:flex; justify-content:space-between; align-items:center; gap:6px; border-top:1px solid rgba(148,163,184,0.14); padding-top:6px;">
                            <span style="font-size:9.5px; color:#94a3b8;">${{escHtml(d.latest_report_date || '')}} ${{escHtml(d.latest_report_time || '')}}</span>
                            ${{safePath ? `<button onclick="openReportModal('${{safePath}}')" style="cursor:pointer; background:rgba(56,189,248,0.14); border:1px solid rgba(56,189,248,0.35); color:#7dd3fc; padding:3px 8px; border-radius:5px; font-size:10px; font-weight:700;">📄 Đọc Báo Cáo</button>` : ''}}
                        </div>
                    </div>`;
                }}).join('');
            }}

            const feedBox = document.getElementById('wr-live-reports-feed-list');
            if (feedBox && Array.isArray(feed) && feed.length > 0) {{
                feedBox.innerHTML = feed.map(r => {{
                    const safePath = String(r.rel_path || '').replace(/\\\\/g, '/').replace(/'/g, "\\\\'");
                    return `<div style="display:flex; justify-content:space-between; align-items:center; gap:10px; background:rgba(15,23,42,0.75); border:1px solid rgba(148,163,184,0.18); border-radius:7px; padding:7px 10px;">
                        <div style="min-width:0;">
                            <div style="font-size:11px; font-weight:800; color:#f8fafc; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${{escHtml(r.icon || '📄')}} ${{escHtml(r.title || '')}}</div>
                            <div style="font-size:10px; color:#94a3b8;">${{escHtml(r.dept_name || '')}} • ${{escHtml(r.date || '')}} ${{escHtml(r.time || '')}} (${{escHtml(r.shift_label || '')}}) • ${{Number(r.size_kb || 0).toFixed(1)}} KB</div>
                        </div>
                        <button onclick="openReportModal('${{safePath}}')" style="cursor:pointer; white-space:nowrap; background:rgba(16,185,129,0.15); border:1px solid rgba(16,185,129,0.4); color:#34d399; padding:4px 10px; border-radius:6px; font-size:10.5px; font-weight:700;">Mở Báo Cáo</button>
                    </div>`;
                }}).join('');
            }}
        }}

        function renderPortfolioTabLiveFromWarRoom(vData, plan) {{
            if (!vData) return;
            const metaEl = document.getElementById('portfolio-tab-plan-meta');
            if (metaEl && plan && plan.generated_at) {{
                metaEl.innerText = `Cập nhật realtime: ${{plan.generated_at}} • Chế độ: ${{plan.regime_label || ''}} • Khung pha: ${{plan.session_phase_label || ''}}`;
            }}
            const hBody = document.getElementById('portfolio-tab-holdings-tbody');
            if (hBody && Array.isArray(vData.held_positions_book)) {{
                hBody.innerHTML = vData.held_positions_book.map(h => {{
                    const pnlVal = Number(h.pnl_vnd || 0);
                    const pnlPct = Number(h.pnl_pct || 0);
                    const pCol = pnlVal >= 0 ? '#34d399' : '#f87171';
                    return `<tr style="background: rgba(56, 189, 248, 0.04);">
                        <td style="padding: 12px 14px; font-weight: 800; color: #38bdf8; font-family: 'JetBrains Mono', monospace;">${{escHtml(h.symbol || '')}}</td>
                        <td style="padding: 12px 14px;">${{escHtml(h.name || '')}}</td>
                        <td style="padding: 12px 14px; font-family: 'JetBrains Mono', monospace;">${{Number(h.shares || 0)}} CP (T0: ${{Number(h.tradable_shares || 0)}})</td>
                        <td style="padding: 12px 14px; font-family: 'JetBrains Mono', monospace;">${{Number(h.entry_price || 0).toLocaleString('en-US')}}đ</td>
                        <td style="padding: 12px 14px; font-family: 'JetBrains Mono', monospace; font-weight: 700;">${{Number(h.live_price || 0).toLocaleString('en-US')}}đ</td>
                        <td style="padding: 12px 14px; font-family: 'JetBrains Mono', monospace; color: ${{pCol}}; font-weight: 800;">${{pnlVal >= 0 ? '+' : ''}}${{pnlVal.toLocaleString('en-US')}}đ (${{pnlPct >= 0 ? '+' : ''}}${{pnlPct.toFixed(2)}}%)</td>
                        <td style="padding: 12px 14px; color: #f87171; font-weight: 700;">${{Number(h.stop_loss || 0).toLocaleString('en-US')}}đ (+${{Number(h.stop_distance_pct || 0).toFixed(2)}}%)</td>
                        <td style="padding: 12px 14px; color: #34d399; font-weight: 700;">${{Number(h.tp1 || 0).toLocaleString('en-US')}} / ${{Number(h.tp2 || 0).toLocaleString('en-US')}}đ</td>
                        <td style="padding: 12px 14px; font-size: 12px; color: #cbd5e1;">${{escHtml(h.victor_status_badge || '')}} — ${{escHtml(h.victor_instruction || '')}}</td>
                    </tr>`;
                }}).join('');
            }}
            const sBody = document.getElementById('portfolio-tab-standby-tbody');
            if (sBody && Array.isArray(vData.alpha_watchlist_book)) {{
                sBody.innerHTML = vData.alpha_watchlist_book.map(w => `<tr>
                    <td style="padding: 10px 14px; font-weight: 800; color: #fbbf24; font-family: 'JetBrains Mono', monospace;">${{escHtml(w.symbol || '')}}</td>
                    <td style="padding: 10px 14px;">${{escHtml(w.sector_name || '')}}</td>
                    <td style="padding: 10px 14px; font-family: 'JetBrains Mono', monospace;">${{Number(w.live_price || 0).toLocaleString('en-US')}}đ</td>
                    <td style="padding: 10px 14px; font-family: 'JetBrains Mono', monospace; color:#38bdf8;">${{Number(w.probe_target || 0).toLocaleString('en-US')}}đ</td>
                    <td style="padding: 10px 14px; font-family: 'JetBrains Mono', monospace;">OCF ${{Number(w.ocf_ratio || 1).toFixed(2)}}x • MOS +${{Number(w.mos_pct || 0).toFixed(1)}}%</td>
                    <td style="padding: 10px 14px; font-family: 'JetBrains Mono', monospace;">${{Number(w.lot_100_cost_vnd || 0).toLocaleString('en-US')}}đ (${{Number(w.nav_pct_per_lot || 0).toFixed(1)}}% NAV)</td>
                    <td style="padding: 10px 14px; font-size: 12px;"><strong>${{escHtml(w.victor_signal || '')}}</strong> — ${{escHtml(w.catalyst || '')}}</td>
                </tr>`).join('');
            }}
        }}

        window._lastSeenVaultReportKey = '';
        async function syncPortalReportsSilently(meta, forceSync) {{
            try {{
                if (!meta && !forceSync) return;
                const key = meta ? `${{meta.latest_report_rel_path || ''}}|${{meta.today_reports_count || 0}}|${{meta.total_reports_scanned || 0}}` : '';
                if (!forceSync && key && key === window._lastSeenVaultReportKey) return;
                if (!forceSync && !window._lastSeenVaultReportKey && key) {{
                    window._lastSeenVaultReportKey = key;
                    return;
                }}
                if (key) window._lastSeenVaultReportKey = key;
                const repRes = await fetch('/api/reports?limit=2000');
                const data = await repRes.json();
                const freshReports = Array.isArray(data) ? data : (data && Array.isArray(data.reports) ? data.reports : null);
                if (freshReports) {{
                    allReports = freshReports;
                    const todayCnt = allReports.filter(r => r.date === todayDateStr).length;
                    const elToday = document.getElementById('stat-today-count');
                    if (elToday) elToday.innerText = `${{todayCnt}} Báo Cáo`;
                    const elVault = document.getElementById('stat-vault-count');
                    if (elVault) elVault.innerText = `${{allReports.length}} Báo Cáo`;
                    applyAllFilters();
                }}
            }} catch (e) {{
                // Silent background sync error ignored
            }}
        }}

        async function publishWarRoomReportNow() {{
            const btn = document.getElementById('btn-publish-war-room-report');
            const msg = document.getElementById('wr-publish-status-msg');
            if (btn) {{
                btn.disabled = true;
                btn.innerText = '⏳ Đang Tổng Hợp & Phát Hành...';
            }}
            if (msg) msg.innerText = 'Đang triệu tập liên phòng ban cập nhật số liệu thị trường thực tế...';
            try {{
                const res = await fetch('/api/war_room/publish_report', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{ trigger_reason: 'CHAIRMAN_WAR_ROOM_PUBLISH' }})
                }});
                const data = await res.json();
                if (data && data.ok) {{
                    if (data.war_room_state) renderTacticalWarRoom(data.war_room_state);
                    await syncPortalReportsSilently(data.vault_sync_meta || null, true);
                    if (typeof loadEnterpriseMeshState === 'function') loadEnterpriseMeshState();
                    if (msg) {{
                        const rPath = String(data.intraday_report_path || data.enterprise_report_path || '').replace(/\\\\/g, '/').replace(/'/g, "\\\\'");
                        msg.innerHTML = `✅ Đã phát hành &amp; đồng bộ lên Vault lúc ${{escHtml(data.published_at || '')}}! ` + (rPath ? `<button onclick="openReportModal('${{rPath}}')" style="cursor:pointer; margin-left:6px; background:rgba(16,185,129,0.2); border:1px solid #10b981; color:#34d399; padding:2px 8px; border-radius:5px; font-size:11px; font-weight:700;">📄 Xem Báo Cáo Vừa Xuất</button>` : '');
                    }}
                }} else {{
                    if (msg) msg.innerText = '⚠️ Không thể phát hành báo cáo: ' + (data && data.error ? data.error : 'Lỗi hệ thống');
                }}
            }} catch (err) {{
                if (msg) msg.innerText = '⚠️ Lỗi kết nối API /api/war_room/publish_report';
            }} finally {{
                if (btn) {{
                    btn.disabled = false;
                    btn.innerText = '⚡ Phát Hành & Đồng Bộ Báo Cáo Tác Chiến Mới Nhất';
                }}
            }}
        }}

        async function runOmniIntelSearch() {{
            const inp = document.getElementById('omni-search-input');
            const out = document.getElementById('omni-search-results');
            if (!out) return;
            const q = inp ? inp.value.trim() : '';
            out.style.display = 'block';
            out.innerHTML = '<div style="color:#38bdf8;">⏳ Đang quét FTS5 toàn thị trường (180 mã, BCTC, CBTT &amp; Kho Báo Cáo)...</div>';
            try {{
                const res = await fetch('/api/intelligence/search?q=' + encodeURIComponent(q) + '&limit=12');
                const data = await res.json();
                if (!res.ok || !data.ok) {{
                    out.innerHTML = '<div style="color:#f87171;">❌ Lỗi tìm kiếm: ' + escHtml(data.error || 'HTTP ' + res.status) + '</div>';
                    return;
                }}
                const tks = data.matched_tickers || [];
                const nws = data.matched_news_and_filings || [];
                const rps = data.matched_reports || [];
                let html = `<div style="margin-bottom:6px; color:#94a3b8;">Kết quả cho <strong style="color:#fff;">"${{escHtml(q || 'Tất cả')}}"</strong>: ${{tks.length}} cổ phiếu • ${{nws.length}} tin CBTT/SEC • ${{rps.length}} báo cáo nội bộ</div>`;
                if (tks.length > 0) {{
                    html += '<div style="display:flex; flex-wrap:wrap; gap:6px; margin-bottom:8px;">' + tks.slice(0, 6).map(t => {{
                        return `<div onclick="inspectDeepBrainTicker('${{escHtml(t.symbol)}}')" style="cursor:pointer; background:rgba(56,189,248,0.12); border:1px solid rgba(56,189,248,0.35); border-radius:6px; padding:5px 8px;">
                            <strong style="color:#38bdf8;">${{escHtml(t.symbol)}}</strong> (${{escHtml(t.market)}}) • Giá: <strong>${{Number(t.live_price || 0).toLocaleString('en-US')}}</strong> • P/E: ${{Number(t.pe || 0).toFixed(1)}} • ROE: ${{Number(t.roe || 0).toFixed(1)}}% • OCF/LNST: ${{Number(t.ocf_ratio || 0).toFixed(2)}}x
                        </div>`;
                    }}).join('') + '</div>';
                }}
                if (nws.length > 0) {{
                    html += nws.slice(0, 8).map(n => `<div style="padding:3px 0; border-top:1px dashed rgba(148,163,184,0.18);">
                        <span style="color:#fbbf24; font-weight:700;">[${{escHtml(n.category || 'NEWS')}}]</span> <strong>${{escHtml(n.title || '')}}</strong> <span style="color:#94a3b8;">(${{escHtml(n.source_name || '')}})</span>
                    </div>`).join('');
                }}
                out.innerHTML = html;
            }} catch (e) {{
                out.innerHTML = '<div style="color:#f87171;">❌ Lỗi kết nối: ' + escHtml(e.message) + '</div>';
            }}
        }}

        async function triggerOmniCrawlLive() {{
            const btn = document.getElementById('btn-omni-crawl');
            const out = document.getElementById('omni-search-results');
            if (btn) {{ btn.disabled = true; btn.innerText = '⏳ Đang cào 12 nguồn...'; }}
            try {{
                const res = await fetch('/api/intelligence/crawl', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ force: true }})
                }});
                const data = await res.json();
                if (out) {{
                    out.style.display = 'block';
                    if (data.ok) {{
                        out.innerHTML = `<div style="color:#34d399; font-weight:800;">✅ Đã cào xong ${{data.total_items || 0}} bản tin/CBTT từ ${{data.sources_online || ''}} nguồn (${{escHtml(data.crawled_at || '')}})!</div>`;
                        await loadTacticalWarRoomData();
                    }} else {{
                        out.innerHTML = '<div style="color:#f87171;">❌ ' + escHtml(data.error || 'Crawl failed') + '</div>';
                    }}
                }}
            }} catch (e) {{
                if (out) {{ out.style.display = 'block'; out.innerHTML = '<div style="color:#f87171;">❌ ' + escHtml(e.message) + '</div>'; }}
            }} finally {{
                if (btn) {{ btn.disabled = false; btn.innerText = '📡 Cào Dữ Liệu Live Ngay'; }}
            }}
        }}

        async function inspectDeepBrainTicker(sym) {{
            const box = document.getElementById('omni-deep-ticker-detail');
            if (!box || !sym) return;
            box.style.display = 'block';
            box.innerHTML = '<div style="color:#fbbf24;">⏳ Đang phân tích DuPont, Pháp y BCTC &amp; Định giá 3 mô hình cho ' + escHtml(sym) + '...</div>';
            try {{
                const res = await fetch('/api/deep_brain?ticker=' + encodeURIComponent(sym));
                const data = await res.json();
                if (!res.ok || !data.ok || !data.analysis) {{
                    box.innerHTML = '<div style="color:#f87171;">❌ Không tải được dữ liệu ' + escHtml(sym) + '</div>';
                    return;
                }}
                const a = data.analysis;
                const v = a.valuation || {{}};
                const f = a.forensic || {{}};
                box.innerHTML = `
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                        <strong style="color:#fbbf24; font-size:12px;">🔬 ${{escHtml(a.symbol)}} — ${{escHtml(a.company_name || '')}} (${{escHtml(a.accounting_regime || '')}})</strong>
                        <span style="color:#34d399; font-weight:800;">Pháp y: ${{Number(f.forensic_score || 0).toFixed(0)}}/100 • Piotroski ${{a.piotroski_f_score || 0}}/9</span>
                    </div>
                    <div>• ROE: <strong>${{Number(a.roe_pct || 0).toFixed(1)}}%</strong> | ROIC: <strong>${{Number(a.roic_est_pct || 0).toFixed(1)}}%</strong> (EVA <strong>${{Number(a.eva_spread_pct || 0) >= 0 ? '+' : ''}}${{Number(a.eva_spread_pct || 0).toFixed(1)}}%</strong>) | OCF/LNST: <strong>${{Number(a.ocf_ratio || 0).toFixed(2)}}x</strong></div>
                    <div>• Định giá: Graham <strong>${{Number(v.graham_target || 0).toLocaleString('en-US')}}</strong> | GARP <strong>${{Number(v.pe_garp_target || 0).toLocaleString('en-US')}}</strong> | Hợp lưu <strong style="color:#34d399;">${{Number(v.intrinsic_fair_value || 0).toLocaleString('en-US')}}</strong> (MOS <strong>${{Number(v.margin_of_safety_pct || 0).toFixed(1)}}%</strong> — ${{escHtml(v.verdict || '')}})</div>
                    <div style="color:#94a3b8; margin-top:2px;">• Catalyst: ${{escHtml(a.catalyst || '')}}</div>`;
            }} catch (e) {{
                box.innerHTML = '<div style="color:#f87171;">❌ ' + escHtml(e.message) + '</div>';
            }}
        }}

        async function logoutPortal() {{
            try {{
                await fetch('/api/auth/logout', {{ method: 'POST' }});
            }} catch (_) {{}}
            window.location.reload();
        }}

        function toggleSyncTCInvest() {{
            const panel = document.getElementById('sync-tcinvest-panel');
            const btn = document.getElementById('btn-toggle-sync-tcinvest');
            if (!panel || !btn) return;
            if (panel.style.display === 'none' || panel.style.display === '') {{
                panel.style.display = 'flex';
                btn.innerText = '▴ Thu Gọn';
            }} else {{
                panel.style.display = 'none';
                btn.innerText = '▾ Mở Form';
            }}
        }}

        function onSyncActionChange() {{
            const act = document.getElementById('sync-tc-action')?.value || 'BUY';
            const orderFields = document.getElementById('sync-tc-order-fields');
            const cashInput = document.getElementById('sync-tc-cash');
            const tp1Input = document.getElementById('sync-tc-tp1');
            if (act === 'RECONCILE') {{
                if (orderFields) orderFields.style.display = 'none';
                if (cashInput) cashInput.style.display = 'block';
                if (tp1Input) tp1Input.style.display = 'block';
            }} else {{
                if (orderFields) orderFields.style.display = 'grid';
                if (cashInput) cashInput.style.display = 'none';
                if (tp1Input) tp1Input.style.display = 'block';
            }}
        }}

        async function submitSyncTCInvest() {{
            const action = document.getElementById('sync-tc-action')?.value || 'BUY';
            const symbol = (document.getElementById('sync-tc-symbol')?.value || '').trim().toUpperCase();
            const shares = Number(document.getElementById('sync-tc-shares')?.value || 0);
            const price = Number(document.getElementById('sync-tc-price')?.value || 0);
            const stopLoss = Number(document.getElementById('sync-tc-stop')?.value || 0);
            const tp1 = Number(document.getElementById('sync-tc-tp1')?.value || 0);
            const cashVal = document.getElementById('sync-tc-cash')?.value || '';
            const statusEl = document.getElementById('sync-tcinvest-status');
            const btn = document.getElementById('btn-submit-sync-tc');

            if (btn) {{ btn.disabled = true; btn.innerText = '⏳ Đang đồng bộ SSOT...'; }}
            if (statusEl) {{ statusEl.style.color = '#38bdf8'; statusEl.innerText = 'Đang gửi yêu cầu...'; }}

            try {{
                const payload = {{
                    action,
                    symbol,
                    shares,
                    price,
                    stop_loss: stopLoss,
                    take_profit: tp1,
                }};
                if (action === 'RECONCILE' && cashVal !== '') {{
                    payload.cash_balance_vnd = Number(cashVal);
                }}
                const res = await fetch('/api/sync_tcinvest', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(payload)
                }});
                const data = await res.json();
                if (!res.ok || !data.ok) {{
                    if (statusEl) {{
                        statusEl.style.color = '#f87171';
                        statusEl.innerText = '❌ ' + (data.error || 'Lỗi đồng bộ.');
                    }}
                }} else {{
                    if (statusEl) {{
                        statusEl.style.color = '#34d399';
                        statusEl.innerText = '✅ ' + (data.message || 'Đồng bộ thành công!');
                    }}
                    if (data.war_room_state) {{
                        renderTacticalWarRoom(data.war_room_state);
                    }} else {{
                        await loadTacticalWarRoomData();
                    }}
                }}
            }} catch (err) {{
                if (statusEl) {{
                    statusEl.style.color = '#f87171';
                    statusEl.innerText = '❌ Lỗi kết nối server: ' + err.message;
                }}
            }} finally {{
                if (btn) {{ btn.disabled = false; btn.innerText = '⚡ Đồng Bộ Ngay Vào SSOT & War-Room'; }}
            }}
        }}

        function toggleWeeklyRoadmap() {{
            const det = document.getElementById('weekly-roadmap-details');
            const btn = document.getElementById('btn-toggle-weekly-roadmap');
            if (!det || !btn) return;
            if (det.style.display === 'none') {{
                det.style.display = 'block';
                btn.innerText = '▾ Thu Gọn';
            }} else {{
                det.style.display = 'none';
                btn.innerText = '▸ Mở Rộng';
            }}
        }}

        async function sendTacticalCommand(customPrompt) {{
            const inputEl = document.getElementById('tactical-cmd-input');
            const btnEl = document.getElementById('btn-send-tactical');
            const prompt = customPrompt || (inputEl ? inputEl.value.trim() : '');
            if (!prompt) return;

            if (inputEl) inputEl.value = '';
            if (btnEl) {{
                btnEl.disabled = true;
                btnEl.innerText = '⏳ Đang gửi...';
            }}

            try {{
                const res = await fetch('/api/tactical_command', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ command: prompt }})
                }});
                if (res.ok) {{
                    const cmdData = await res.json().catch(() => null);
                    if (cmdData && cmdData.enterprise_session && cmdData.enterprise_session.session_id) {{
                        renderEnterpriseMeshPanel({{ latest_session: cmdData.enterprise_session, roster_count: 14 }});
                    }}
                    await loadTacticalWarRoomData();
                }}
            }} catch (err) {{
                console.error('Error sending tactical command:', err);
            }} finally {{
                if (btnEl) {{
                    btnEl.disabled = false;
                    btnEl.innerText = '⚡ Gửi Chỉ Lệnh';
                }}
                if (inputEl) inputEl.focus();
            }}
        }}

        function sendQuickTactical(promptText) {{
            const inputEl = document.getElementById('tactical-cmd-input');
            if (inputEl) inputEl.value = promptText;
            sendTacticalCommand(promptText);
        }}

        function renderEnterpriseMeshPanel(summary) {{
            if (!summary) return;
            const s = (summary.latest_session || summary.session)
                ? (summary.latest_session || summary.session)
                : summary;
            if (!s || !s.session_id) return;

            const badgeEl = document.getElementById('enterprise-mesh-badge');
            const bannerEl = document.getElementById('enterprise-verdict-banner');
            const rosterBodyEl = document.getElementById('enterprise-roster-body');
            const debateEl = document.getElementById('enterprise-debate-stream');

            const quorum = s.quorum_count || summary.roster_count || 14;
            const rosterTotal = s.roster_total || 14;
            const pktsCount = s.packet_count || (s.packets ? s.packets.length : 14);
            const dissentCount = s.dissent_count || 0;
            const auditScore = s.ombudsman_audit_score || '10/10';
            const sealShort = String(s.constitutional_seal_sha256 || '').slice(0, 12);

            if (badgeEl) {{
                badgeEl.innerText = `Quorum ${{quorum}}/${{rosterTotal}} • ${{pktsCount}} Packets • ${{dissentCount}} Phản biện • Audit ${{auditScore}} • Seal ${{sealShort}}`;
                badgeEl.style.color = s.veto_triggered ? '#fca5a5' : '#34d399';
                badgeEl.style.borderColor = s.veto_triggered ? 'rgba(239, 68, 68, 0.5)' : 'rgba(16, 185, 129, 0.45)';
                badgeEl.style.background = s.veto_triggered ? 'rgba(239, 68, 68, 0.14)' : 'rgba(16, 185, 129, 0.15)';
            }}

            if (bannerEl) {{
                const ssot = s.ssot_snapshot || {{}};
                const navVnd = Number(ssot.total_nav_vnd || 18151471).toLocaleString('vi-VN');
                const cashVnd = Number(ssot.cash_vnd ?? ssot.cash_balance_vnd ?? 12516471).toLocaleString('vi-VN');
                const cashPct = Number(ssot.cash_pct || 69.0).toFixed(1);
                const verdictColor = s.veto_triggered ? '#f87171' : '#34d399';
                const targetTag = s.target_ticker ? `<span style="background: rgba(56, 189, 248, 0.18); color: #38bdf8; padding: 2px 7px; border-radius: 5px; font-weight: 800; font-size: 10.5px;">Mã: ${{escHtml(s.target_ticker)}}</span>` : '<span style="background: rgba(148, 163, 184, 0.2); color: #cbd5e1; padding: 2px 7px; border-radius: 5px; font-weight: 700; font-size: 10.5px;">Toàn Danh Mục</span>';
                bannerEl.innerHTML = `
                    <div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 6px; margin-bottom: 5px;">
                        <div style="display: flex; align-items: center; gap: 6px; flex-wrap: wrap;">
                            <strong style="color: #f8fafc;">Phiên ${{escHtml(s.session_id)}}</strong>
                            ${{targetTag}}
                            <span style="color: ${{verdictColor}}; font-weight: 900;">⚖️ ${{escHtml(s.final_verdict || '')}}</span>
                        </div>
                        <span style="font-size: 10.5px; color: #94a3b8;">🕒 ${{escHtml(s.created_at || '')}} | SSOT ${{escHtml(ssot.account_id || '105C307855')}}: NAV ${{navVnd}} đ • Cash ${{cashVnd}} đ (${{cashPct}}%)</span>
                    </div>
                    <div style="font-size: 11.5px; color: #cbd5e1; line-height: 1.45;">
                        <strong style="color: #fbbf24;">Chỉ thị:</strong> ${{escHtml(s.directive || '')}}<br>
                        <strong style="color: #38bdf8;">Hành động chốt:</strong> ${{escHtml(s.action_plan || '')}}
                    </div>
                `;
            }}

            if (rosterBodyEl) {{
                const votes = Array.isArray(s.roll_call_votes) ? s.roll_call_votes : [];
                if (!votes.length) {{
                    rosterBodyEl.innerHTML = '<tr><td colspan="3" style="padding: 8px; color: #94a3b8;">Chưa có dữ liệu điểm danh 14 thực thể.</td></tr>';
                }} else {{
                    rosterBodyEl.innerHTML = votes.map((rv) => {{
                        const v = String(rv.vote || 'INFO').toUpperCase();
                        let vColor = '#94a3b8';
                        let vBg = 'rgba(148, 163, 184, 0.15)';
                        if (v === 'VETO') {{ vColor = '#fca5a5'; vBg = 'rgba(239, 68, 68, 0.22)'; }}
                        else if (v === 'DISSENT') {{ vColor = '#fdba74'; vBg = 'rgba(249, 115, 22, 0.2)'; }}
                        else if (v === 'CONDITIONAL') {{ vColor = '#fde047'; vBg = 'rgba(234, 179, 8, 0.18)'; }}
                        else if (v === 'APPROVE' || v === 'AUDIT_PASS') {{ vColor = '#6ee7b7'; vBg = 'rgba(16, 185, 129, 0.18)'; }}
                        return `
                            <tr style="border-bottom: 1px solid rgba(148, 163, 184, 0.12);">
                                <td style="padding: 5px 4px; color: #f1f5f9; font-weight: 700; white-space: nowrap;">${{escHtml(rv.ban_code || rv.dept_id)}} • <span style="color: #38bdf8; font-weight: 600;">${{escHtml(rv.officer || '')}}</span></td>
                                <td style="padding: 5px 4px; white-space: nowrap;"><span style="background: ${{vBg}}; color: ${{vColor}}; padding: 2px 6px; border-radius: 4px; font-weight: 800; font-size: 9.5px;">${{escHtml(v)}}</span></td>
                                <td style="padding: 5px 4px; color: #cbd5e1; line-height: 1.35;">${{escHtml(rv.rationale || '')}} <span style="color: #64748b;">(Đ.${{escHtml(rv.article || '')}})</span></td>
                            </tr>
                        `;
                    }}).join('');
                }}
            }}

            if (debateEl) {{
                const debates = Array.isArray(s.debate_points) ? s.debate_points : [];
                const packets = Array.isArray(s.packets) ? s.packets : [];
                let htmlBlocks = debates.map((dp) => {{
                    const st = String(dp.stance || 'INFO').toUpperCase();
                    const borderClr = st === 'VETO' ? '#ef4444' : (st === 'DISSENT' ? '#f97316' : (st === 'CONDITIONAL' ? '#eab308' : '#10b981'));
                    return `
                        <div style="background: rgba(30, 41, 59, 0.65); border-left: 3px solid ${{borderClr}}; padding: 6px 8px; border-radius: 5px;">
                            <div style="font-weight: 800; color: #f8fafc; font-size: 10.5px;">[${{escHtml(st)}} • Điều ${{escHtml(dp.article || '')}}] ${{escHtml(dp.speaker || dp.speaker_dept)}} → ${{escHtml(dp.target_dept || '')}}</div>
                            <div style="color: #cbd5e1; margin-top: 2px; line-height: 1.38;">${{escHtml(dp.argument || '')}}</div>
                        </div>
                    `;
                }});
                const dataPackets = packets.slice(0, 6).map((pk) => `
                    <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(56, 189, 248, 0.22); padding: 5px 8px; border-radius: 5px;">
                        <div style="color: #38bdf8; font-weight: 700; font-size: 10px;">📦 ${{escHtml(pk.from_dept)}} (${{escHtml(pk.from_officer)}}) → ${{escHtml((pk.to_depts || []).join(', '))}} • [${{escHtml(pk.topic)}}]</div>
                        <div style="color: #94a3b8; margin-top: 2px; line-height: 1.35;">${{escHtml(pk.summary || '')}}</div>
                    </div>
                `);
                const combined = htmlBlocks.concat(dataPackets);
                debateEl.innerHTML = combined.length
                    ? combined.join('')
                    : '<div style="color: #94a3b8;">Chưa ghi nhận gói tranh biện nào trong phiên này.</div>';
            }}
        }}

        async function loadEnterpriseMeshState() {{
            try {{
                const res = await fetch('/api/enterprise/state');
                if (!res.ok) return;
                const data = await res.json();
                if (data && data.ok) {{
                    renderEnterpriseMeshPanel(data.summary || data);
                }}
            }} catch (err) {{
                console.error('Error loading enterprise mesh state:', err);
            }}
        }}

        async function conveneEnterpriseMesh() {{
            const tickerEl = document.getElementById('enterprise-ticker-input');
            const dirEl = document.getElementById('enterprise-directive-input');
            const btnEl = document.getElementById('enterprise-convene-btn');
            const ticker = tickerEl ? tickerEl.value.trim().toUpperCase() : '';
            const directive = (dirEl && dirEl.value.trim())
                ? dirEl.value.trim()
                : (ticker ? `Họp khẩn toàn doanh nghiệp đánh giá đa chiều mã ${{ticker}}` : 'Họp giao ban toàn doanh nghiệp đánh giá danh mục và tầm ngắm');

            if (btnEl) {{
                btnEl.disabled = true;
                btnEl.innerText = '⏳ Đang họp 14 Ban...';
            }}
            try {{
                const res = await fetch('/api/enterprise/convene', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ ticker, directive, trigger_source: 'PORTAL_UI' }})
                }});
                const data = await res.json();
                if (res.ok && data && data.ok) {{
                    renderEnterpriseMeshPanel(data.summary || {{ latest_session: data.session, roster_count: 14 }});
                    await loadTacticalWarRoomData();
                }}
            }} catch (err) {{
                console.error('Error convening enterprise mesh:', err);
            }} finally {{
                if (btnEl) {{
                    btnEl.disabled = false;
                    btnEl.innerText = '⚡ Triệu Tập Họp Thật';
                }}
            }}
        }}

        window.addEventListener('DOMContentLoaded', () => {{
            syncDateFilterButtons();
            applyAllFilters();
            const urlParams = new URLSearchParams(window.location.search);
            const openPath = urlParams.get('open');
            if (openPath) {{
                openReportModal(openPath);
            }}
            initSummitRoom();
            startLiveClockTicker();
            initTacticalWarRoom();
            loadEnterpriseMeshState();
        }});

        // LÀM MỚI DỮ LIỆU
        async function refreshData() {{
            try {{
                const [repRes, datesRes] = await Promise.all([
                    fetch('/api/reports?limit=2000'),
                    fetch('/api/dates').catch(() => null)
                ]);
                const data = await repRes.json();
                const freshReports = Array.isArray(data) ? data : (data && Array.isArray(data.reports) ? data.reports : null);
                if (freshReports) {{
                    allReports = freshReports;
                    if (datesRes && datesRes.ok) {{
                        const freshDates = await datesRes.json();
                        if (Array.isArray(freshDates) && freshDates.length > 0) {{
                            availableDates = freshDates;
                            const sel = document.getElementById('archive-date-select');
                            if (sel) {{
                                sel.innerHTML = freshDates.map(d => `<option value="${{d.date}}">${{d.display}}</option>`).join('');
                            }}
                        }}
                    }}
                    const todayCnt = allReports.filter(r => r.date === todayDateStr).length;
                    const elToday = document.getElementById('stat-today-count');
                    if (elToday) elToday.innerText = `${{todayCnt}} Báo Cáo`;
                    const elVault = document.getElementById('stat-vault-count');
                    if (elVault) elVault.innerText = `${{allReports.length}} Báo Cáo`;
                    if (todayCnt > 0 && autoFallbackDateUsed) {{
                        currentDateFilter = 'today';
                        autoFallbackDateUsed = '';
                        syncDateFilterButtons();
                    }} else if (todayCnt === 0 && currentDateFilter === 'today' && allReports.length > 0) {{
                        const newestDate = (availableDates[0] && availableDates[0].date) || allReports[0].date;
                        currentDateFilter = newestDate || 'all';
                        autoFallbackDateUsed = currentDateFilter !== 'all' ? currentDateFilter : '';
                        syncDateFilterButtons();
                    }}
                    applyAllFilters();
                    await loadTacticalWarRoomData();
                    alert('Đã làm mới dữ liệu toàn hệ thống thành công (' + allReports.length + ' báo cáo, Hôm nay: ' + todayCnt + ')!');
                }} else {{
                    location.reload();
                }}
            }} catch (err) {{
                location.reload();
            }}
        }}
    </script>
</body>
</html>
"""
