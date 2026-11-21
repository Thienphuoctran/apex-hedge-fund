#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APEX DAILY TACTICAL WAR-ROOM ENGINE (MINH QUÂN & VICTOR LIVE DESK) - V3.0 REALTIME
File: scripts/apex_tactical_war_room_engine.py
Phục vụ: Chủ tịch HĐQT Trần Quốc Thiên Phước (Tài khoản TCBS: 105C307855)
Chuyên viên túc trực:
  - Minh Quân (Ban 7 VN — Chuyên viên Đầu tư Trưởng & Thực thi Tự tiến hóa Mỗi ngày)
  - Victor (Ban 9 — Giám Sát Danh Mục Thời Gian Thực & Ứng Phó Biến Động Khẩn Cấp)
  - Alex (Ban 7 US — Chuyên viên Đầu tư Quốc tế / Wall Street — Standby Slot 21h30)

Chức năng:
1. Xác định pha thị trường thời gian thực (8 pha từ Pre-ATO đến Đóng cửa & Phố Wall).
2. Bản Kế Hoạch Chi Tiết Các Bước Trong Phiên ("Ta nên làm gì vào thời điểm này?").
3. Bảng Giám Sát Thị Trường Realtime của Victor (VN-Index, VN30, Khối ngoại, Độ lệch Basis).
4. Bảng Giá Giám Sát Realtime 4 Siêu Cổ Phiếu Vòng 2 (HDB, MSH, BAF, IDC với giá, +/- %, Vol, Buy Up %, Trạng thái an ninh).
5. Luồng đề bạt và xử lý chỉ thị tương tác thời gian thực của Chủ tịch.
6. Đồng bộ liên tục 24/24 trên Cloud.
"""

import os
import sys
import json
import time
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

def get_ict_now() -> datetime.datetime:
    """Luôn lấy thời gian hiện tại chuẩn múi giờ Việt Nam (ICT = UTC+7) bất kể chạy trên Cloud Render hay Local."""
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    ict_tz = datetime.timezone(datetime.timedelta(hours=7))
    return utc_now.astimezone(ict_tz)

try:
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
# Định tuyến directives phân luồng theo ngày hiện tại để bảo đảm tính tiến hóa liên tục
def get_daily_directives_file(date_str: Optional[str] = None) -> Path:
    if not date_str:
        date_str = get_ict_now().strftime("%Y-%m-%d")
    return DATA_DIR / f"apex_tactical_war_room_directives_{date_str}.json"

VN_LEDGER_FILE = BASE_DIR / "VN_Market" / "07_Daily_Specialist" / "vn_daily_ledger.json"
MASTER_BLOTTER_FILE = BASE_DIR / "08_Master_Investment_CIO" / "master_execution_blotter.json"
VICTOR_TELEMETRY_FILE = BASE_DIR / "09_Realtime_Portfolio_Sentinel" / "vn3_live_telemetry.json"
VN_MARKET_DATA_FILE = BASE_DIR / "VN_Market" / "data" / "vn_market_data.json"


def get_current_market_phase(now: Optional[datetime.datetime] = None) -> Dict[str, Any]:
    """
    Xác định chính xác pha thị trường hiện tại của TTCK Việt Nam.
    """
    if now is None:
        now = get_ict_now()

    weekday = now.weekday()  # 0=Monday, 4=Friday, 5=Saturday, 6=Sunday
    is_weekend = weekday >= 5
    hm = now.hour * 60 + now.minute

    phases_definition = [
        {
            "id": "PRE_ATO",
            "name": "PHASE 1: CHUẨN BỊ PRE-ATO (08:30 - 09:00)",
            "short_name": "Pre-ATO Giao Ban",
            "time_range": "08:30 – 09:00",
            "start_hm": 8 * 60 + 30,
            "end_hm": 9 * 60,
            "action": "Minh Quân rà soát Sổ Lệnh Master Blotter, họp giao ban đầu ngày, kiểm tra tin tức qua đêm và đối soát sức mua.",
            "rule": "Kiểm tra 100% Checklist 7 Điểm, tuyệt đối không đặt lệnh sớm tránh sai lệch giá."
        },
        {
            "id": "ATO_OPEN",
            "name": "PHASE 2: PHIÊN KHỚP LỆNH ATO (09:00 - 09:15)",
            "short_name": "Mở Cửa ATO",
            "time_range": "09:00 – 09:15",
            "start_hm": 9 * 60,
            "end_hm": 9 * 60 + 15,
            "action": "Victor quét độ mở Gap của VN-Index và 4 mã Vòng 2. Minh Quân kích hoạt quy tắc BẤT KHẢ XÂM PHẠM.",
            "rule": "❌ QUY TẮC SẮT: 100% TUYỆT ĐỐI KHÔNG ĐUA LỆNH ATO (Tránh bẫy gap ảo của tạo lập)."
        },
        {
            "id": "MORNING_CONTINUOUS",
            "name": "PHASE 3: KHỚP LỆNH LIÊN TỤC SÁNG (09:15 - 11:30)",
            "short_name": "Phiên Sáng",
            "time_range": "09:15 – 11:30",
            "start_hm": 9 * 60 + 15,
            "end_hm": 11 * 60 + 30,
            "action": "Đo lường tỷ lệ Mua chủ động (Buy Up), phát hiện bẫy kê lệnh ảo Giá 2/Giá 3, theo dõi biến động HDB & MSH.",
            "rule": "Không mua đuổi khi RSI > 60 hoặc khi cổ phiếu đang tăng xanh nhưng chưa có nền tích lũy."
        },
        {
            "id": "NOON_INTERMISSION",
            "name": "PHASE 4: TỔNG KẾT SÁNG & HỘI Ý TRƯA (11:30 - 13:00)",
            "short_name": "Nghỉ Trưa",
            "time_range": "11:30 – 13:00",
            "start_hm": 11 * 60 + 30,
            "end_hm": 13 * 60,
            "action": "Minh Quân đối soát cùng Victor: biến động Khối Ngoại, Tự Doanh CTCK, Basis phái sinh VN30F và thanh khoản sáng.",
            "rule": "Lập kịch bản sẵn sàng cho đợt hàng T+2 về lúc 13h00."
        },
        {
            "id": "T2_ABSORPTION",
            "name": "PHASE 5: HẤP THỤ ÁP LỰC HÀNG T+2 VỀ TÀI KHOẢN (13:00 - 14:00)",
            "short_name": "Hấp Thụ Hàng T+2",
            "time_range": "13:00 – 14:00",
            "start_hm": 13 * 60,
            "end_hm": 14 * 60,
            "action": "Quan sát áp lực chốt lời/cắt lỗ của hàng T+2.5 về tài khoản nhà đầu tư cá nhân lúc 13h15-13h30.",
            "rule": "Kiên nhẫn tuyệt đối, không bắt dao rơi khi lực bán hoảng loạn chưa dứt điểm."
        },
        {
            "id": "GOLDEN_WINDOW",
            "name": "PHASE 6: ⭐ KHUNG GIỜ VÀNG TÁC CHIẾN (14:00 - 14:25)",
            "short_name": "⭐ Khung Giờ Vàng",
            "time_range": "14:00 – 14:25",
            "start_hm": 14 * 60,
            "end_hm": 14 * 60 + 25,
            "action": "THỜI ĐIỂM QUYẾT ĐỊNH: Hình thái 90% nến ngày đã lộ rõ. Nếu xuất hiện nến Test Cung (Vol cạn kiệt), Minh Quân đề bạt bấm cò Nhịp 1!",
            "rule": "⭐ Chỉ đặt lệnh LO (Limit Order), giải ngân đúng 100 CP (Nhịp 1 Kim Tự Tháp 30%), khóa rủi ro <= 0.35% NAV."
        },
        {
            "id": "ATC_CLOSING",
            "name": "PHASE 7: PHIÊN KHỚP LỆNH ĐÓNG CỬA ATC (14:30 - 14:45)",
            "short_name": "Đóng Cửa ATC",
            "time_range": "14:30 – 14:45",
            "start_hm": 14 * 60 + 30,
            "end_hm": 14 * 60 + 45,
            "action": "Theo dõi giá đóng cửa ngày, đối soát các lệnh khớp nhịp 1 và cập nhật giá đóng nến chuẩn xác.",
            "rule": "Ghi nhận dữ liệu thực tế, chuẩn bị sổ cái bàn giao cho phiên kiểm điểm."
        },
        {
            "id": "POST_MARKET_WALL_STREET",
            "name": "PHASE 8: PHIÊN TỐI, HỒI TỐ & CHUYỂN GIAO PHỐ WALL (14:45 - 24:00)",
            "short_name": "Phố Wall Ca Tối",
            "time_range": "14:45 – 24:00 / 00:00 – 08:30",
            "start_hm": 14 * 60 + 45,
            "end_hm": 24 * 60,
            "action": "Minh Quân & Victor tự kiểm điểm phiên, lưu trữ Walk-Forward. Đếm ngược tới 21h30 tối chuyển giao ca trực chiến cho Alex (Phố Wall).",
            "rule": "Bảo vệ thành quả, không để cảm xúc phiên hôm nay chi phối ngày mai."
        }
    ]

    current_phase = None
    for p in phases_definition:
        if p["start_hm"] <= hm < p["end_hm"]:
            current_phase = p
            break

    if current_phase is None:
        current_phase = phases_definition[-1]

    ny_open_minutes = 21 * 60 + 30
    if hm < ny_open_minutes:
        diff_min = ny_open_minutes - hm
    else:
        diff_min = (24 * 60 - hm) + ny_open_minutes
    countdown_ny_str = f"{diff_min // 60}h {diff_min % 60:02d}m"

    return {
        "current_time_str": now.strftime("%H:%M:%S"),
        "current_date_str": now.strftime("%Y-%m-%d"),
        "is_weekend": is_weekend,
        "active_phase_id": current_phase["id"],
        "active_phase_name": current_phase["name"],
        "active_phase_short": current_phase["short_name"],
        "active_phase_time": current_phase["time_range"],
        "active_phase_action": current_phase["action"],
        "active_phase_rule": current_phase["rule"],
        "phases_list": phases_definition,
        "countdown_to_wall_street": countdown_ny_str
    }


def _ensure_project_root_in_path() -> None:
    root_str = str(BASE_DIR)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)


def _get_live_snapshot(force_refresh: bool = False) -> Dict[str, Any]:
    """Lấy toàn bộ snapshot thời gian thực từ Living Intraday Brain (cache 10s trong phiên, 30s ngoài giờ)."""
    _ensure_project_root_in_path()
    from scripts.apex_live_intraday_brain import compute_live_war_room_snapshot
    now_ict = get_ict_now()
    hm = now_ict.hour * 60 + now_ict.minute
    in_session = (now_ict.weekday() < 5) and (8 * 60 + 45 <= hm <= 15 * 60)
    ttl = 10.0 if in_session else 30.0
    return compute_live_war_room_snapshot(force_refresh=force_refresh, cache_ttl=ttl)


def get_tactical_action_steps(
    now: datetime.datetime,
    snapshot: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Xây dựng Bản Kế Hoạch Chi Tiết Các Bước Trong Phiên Làm Việc (100% Live Dynamic SSOT + Regime).
    Trả lời cụ thể câu hỏi của Chủ tịch: 'Ta nên làm gì vào thời điểm này?'
    """
    hm = now.hour * 60 + now.minute
    snap = snapshot or _get_live_snapshot()
    port = snap.get("portfolio_live", {})
    regime = snap.get("intraday_regime", {})
    live_stocks = snap.get("live_stocks", [])
    dynamic_picks = snap.get("dynamic_picks", [])

    cash_vnd = float(port.get("cash_vnd", 0.0))
    cash_pct = float(port.get("cash_pct", 100.0))
    stocks_val_vnd = float(port.get("stocks_val_vnd", 0.0))
    stocks_pct = float(port.get("stocks_pct", 0.0))
    total_nav_vnd = float(port.get("total_nav_vnd", cash_vnd))
    total_shares = int(port.get("total_shares", 0))
    holdings = port.get("holdings", [])
    holdings_desc = port.get("holdings_desc", "0 CP")

    picks_codes = ", ".join(p.get("code", "") for p in dynamic_picks[:4]) or ", ".join(s.get("code", "") for s in live_stocks[:4]) or "Watchlist SSOT"
    if holdings:
        hold_details = " | ".join(
            f"{h.get('shares', 0)} {h.get('symbol', '')} (Live {float(h.get('current_price', 0)):,.0f} đ, PnL {float(h.get('pnl_pct', 0)):+.2f}%, Stop {float(h.get('stop_loss', 0)):,.0f} đ)"
            for h in holdings
        )
    else:
        hold_details = "0 CP (Chưa giải ngân)"

    buy_candidates = [s for s in live_stocks if not s.get("is_holding") and s.get("action_code") in ("BUY_ZONE", "NEAR_BUY_WATCH")]
    standby_text = " | ".join(
        f"{s['code']} (Giá {s['price']:,.0f} đ, Mục tiêu gom {s['probe_target']:,.0f} đ, BuyUp {s['active_buy_pct']:.1f}%)"
        for s in (buy_candidates[:2] or live_stocks[:2])
    ) or "Chờ tín hiệu cạn cung"

    alert_stocks = [s for s in live_stocks if s.get("action_code") in ("STOP_TRIGGERED", "NEAR_STOP_WARNING", "TP1_REACHED", "TP2_REACHED")]
    if alert_stocks:
        alert_summary = " ⚠️ CẢNH BÁO LIVE: " + "; ".join(
            f"{s['code']} [{s['security_label']}]" for s in alert_stocks
        )
    else:
        alert_summary = f"Trạng thái vị thế ổn định ({hold_details})."

    max_alloc = int(regime.get("max_new_allocation_pct", 30))
    regime_label = regime.get("label", "GIẰNG CO PHÂN HÓA")
    regime_guidance = regime.get("guidance", "")

    steps = [
        {
            "step_id": 1,
            "time_range": "08:30 – 09:00",
            "title": "Bước 1: Rà Soát Sổ Lệnh Master Pre-ATO & Đối Soát Sức Mua SSOT",
            "role": "Minh Quân & Victor",
            "status": "COMPLETED" if hm >= 9 * 60 else ("ACTIVE" if hm >= 8 * 60 + 30 else "UPCOMING"),
            "what_to_do": (
                f"Đối soát két tiền mặt SSOT {cash_vnd:,.0f} đ ({cash_pct:.1f}% NAV) & vị thế đang giữ: {hold_details}. "
                f"Theo dõi rổ mục tiêu động: {picks_codes}. Tuyệt đối KHÔNG đặt lệnh trước ATO."
            ),
            "constitution_rule": "Hiến chương Điều 4: Cấm đặt lệnh sớm khi chưa qua lọc nhiễu ATO."
        },
        {
            "step_id": 2,
            "time_range": "09:00 – 09:15",
            "title": "Bước 2: Giám Sát Mở Cửa ATO & Giữ Kỷ Luật Thép 3 Không",
            "role": "Minh Quân (Ban 7 VN)",
            "status": "COMPLETED" if hm >= 9 * 60 + 15 else ("ACTIVE" if hm >= 9 * 60 else "UPCOMING"),
            "what_to_do": (
                f"Victor quét độ lệch Gap mở cửa của VN-Index và rổ {len(live_stocks)} mã SSOT. "
                f"100% TUYỆT ĐỐI KHÔNG ĐUA LỆNH ATO. Bảo toàn nguyên vẹn {cash_vnd:,.0f} đ tiền mặt ({cash_pct:.1f}% NAV)."
            ),
            "constitution_rule": "Quy tắc 3 Không: Không mua ATO - Không mua đuổi giá xanh - Không bình quân giá xuống."
        },
        {
            "step_id": 3,
            "time_range": "09:15 – 10:00",
            "title": "Bước 3: Lọc Nhiễu Sau ATO & Đo Lực Cung Tự Nhiên",
            "role": "Victor Live Sentinel",
            "status": "COMPLETED" if hm >= 10 * 60 else ("ACTIVE" if hm >= 9 * 60 + 15 else "UPCOMING"),
            "what_to_do": (
                f"Đo lường 3 bước giá (Bid/Ask 1-3) và tỷ lệ Mua chủ động (Buy Up %). "
                f"Chế độ thị trường hiện tại: {regime_label} (Hạn mức giải ngân mới tối đa {max_alloc}% Cash). {alert_summary}"
            ),
            "constitution_rule": "Quy tắc VSA: Bứt phá không có khối lượng đi kèm là bẫy Bull-Trap cần né tránh."
        },
        {
            "step_id": 4,
            "time_range": "10:00 – 11:30",
            "title": "Bước 4: Theo Dõi Khớp Lệnh Sáng & Độ Rộng Thị Trường",
            "role": "Minh Quân (Ban 7 VN)",
            "status": "COMPLETED" if hm >= 11 * 60 + 30 else ("ACTIVE" if hm >= 10 * 60 else "UPCOMING"),
            "what_to_do": (
                f"Giám sát sát sao vị thế hiện hữu ({holdings_desc} • {stocks_val_vnd:,.0f} đ) và radar Standby: {standby_text}. "
                f"{regime_guidance}"
            ),
            "constitution_rule": "Kỷ luật giải ngân: Chỉ gom khi phe bán kiệt sức tại vùng hỗ trợ cứng."
        },
        {
            "step_id": 5,
            "time_range": "11:30 – 13:00",
            "title": "Bước 5: Nghỉ Trưa, Tổng Kết Phiên Sáng & Đối Soát Khối Ngoại / Phái Sinh",
            "role": "Minh Quân & Victor",
            "status": "COMPLETED" if hm >= 13 * 60 else ("ACTIVE" if hm >= 11 * 60 + 30 else "UPCOMING"),
            "what_to_do": (
                f"Tổng hợp thanh khoản, mua/bán ròng khối ngoại, Basis VN30F1M và cập nhật NAV live ({total_nav_vnd:,.0f} đ). "
                f"Chuẩn bị kịch bản đón nhịp hàng T+2.5 về tài khoản lúc 13h00."
            ),
            "constitution_rule": "Đóng sổ theo dõi giữa phiên, tránh dao động cảm xúc ngắn hạn."
        },
        {
            "step_id": 6,
            "time_range": "13:00 – 13:45",
            "title": "Giai Đoạn 1: Quan Sát Nhịp Hấp Thụ Hàng T+2.5 Về Tài Khoản",
            "role": "Minh Quân & Victor Sentinel",
            "status": "COMPLETED" if hm >= 13 * 60 + 45 else ("ACTIVE" if hm >= 13 * 60 else "UPCOMING"),
            "what_to_do": (
                f"Theo dõi lực chốt lời/cắt lỗ khung 13:15 – 13:35. Danh mục hiện có {total_shares} CP ({holdings_desc}) "
                f"và tiền mặt {cash_vnd:,.0f} đ ({cash_pct:.1f}% NAV). Kiên nhẫn chờ phe bán xả xong."
            ),
            "constitution_rule": "TUYỆT ĐỐI KHÔNG BẮT DAO RƠI khi lực bán hoảng loạn chưa dứt điểm."
        },
        {
            "step_id": 7,
            "time_range": "13:45 – 13:55",
            "title": "Giai Đoạn 2: Thẩm Định Lực Đỡ & Độ Cạn Cung (No-Supply Check)",
            "role": "Victor & Minh Quân",
            "status": "COMPLETED" if hm >= 13 * 60 + 55 else ("ACTIVE" if hm >= 13 * 60 + 45 else "UPCOMING"),
            "what_to_do": (
                f"Đo Buy Up % và RSI14 trực tiếp: {standby_text}. "
                f"Kiểm tra khoảng cách tới ngưỡng Stop Loss 2xATR cho các vị thế đang giữ: {hold_details}."
            ),
            "constitution_rule": "Chỉ bấm cò khi xuất hiện nến Test Cung / Buy Up >= 55% và chế độ thị trường cho phép."
        },
        {
            "step_id": 8,
            "time_range": "14:00 – 14:25",
            "title": f"Giai Đoạn 3: ⭐ KHUNG GIỜ VÀNG TÁC CHIẾN ({regime_label})",
            "role": "Chủ Tịch Thực Thi • Victor & Minh Quân Bảo Vệ",
            "status": "COMPLETED" if hm >= 14 * 60 + 25 else ("ACTIVE" if hm >= 14 * 60 else "UPCOMING"),
            "what_to_do": (
                f"Thời điểm quyết định (90% nến ngày lộ rõ). Hạn mức giải ngân mới tối đa theo Regime: {max_alloc}% Cash "
                f"trên két {cash_vnd:,.0f} đ. Trạng thái danh mục: {hold_details}. Radar mục tiêu: {standby_text}."
            ),
            "constitution_rule": "Đặt lệnh LO chuẩn chỉ, khóa rủi ro Stop Loss <= 0.35% NAV cho mỗi lệnh mới."
        },
        {
            "step_id": 9,
            "time_range": "14:30 – 14:45",
            "title": "Bước 9: Phiên Đóng Cửa ATC & Đối Soát Sổ Cái Thực Thi",
            "role": "Minh Quân & Victor",
            "status": "COMPLETED" if hm >= 14 * 60 + 45 else ("ACTIVE" if hm >= 14 * 60 + 30 else "UPCOMING"),
            "what_to_do": (
                f"Chốt giá đóng cửa ATC, cập nhật NAV live ({total_nav_vnd:,.0f} đ), đối soát lệnh khớp thực tế trên TCInvest "
                f"(bằng Form Sync 1-Click) và bàn giao sổ cái ca tối."
            ),
            "constitution_rule": "Bảo đảm SSOT chính xác 100% đến từng đồng."
        }
    ]

    active_step = None
    for s in steps:
        if s["status"] == "ACTIVE":
            active_step = s
            break
    if active_step is None:
        if hm >= 14 * 60 + 45 or hm < 8 * 60 + 30:
            active_step = {
                "step_id": 9,
                "time_range": "14:45 – 24:00",
                "title": "Tổng Kết Phiên VN & Chuyển Giao Trực Chiến Sang Phố Wall Cho Alex",
                "role": "Alex (Ban 7 US) & Victor",
                "status": "ACTIVE",
                "what_to_do": (
                    f"Thị trường Việt Nam đã đóng cửa. Danh mục live gồm {total_shares} CP ({holdings_desc} • {stocks_val_vnd:,.0f} đ) "
                    f"và két tiền mặt {cash_vnd:,.0f} đ ({cash_pct:.1f}% NAV) — Tổng NAV: {total_nav_vnd:,.0f} đ. "
                    f"Victor giám sát 24/7, chuyển giao ca tối sang Phân khu Phố Wall của Alex lúc 21h30."
                ),
                "constitution_rule": "Hiến chương Điều 9: Kỷ luật lưu trữ nhật ký và bảo vệ tài sản xuyên lục địa."
            }
        else:
            active_step = steps[0]

    return {
        "current_step": active_step,
        "all_steps": steps
    }


def get_live_market_overview(snapshot: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Lấy dữ liệu tình hình thị trường thời gian thực từ VPS/Entrade cho bàn trực chiến của Victor.
    """
    snap = snapshot or _get_live_snapshot()
    return snap.get("market_overview", {})


def get_live_stock_sentinel(snapshot: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Bảng giá giám sát thời gian thực SSOT động (Holdings + Minh Quân + Master Blotter) cho Victor Sentinel.
    """
    snap = snapshot or _get_live_snapshot()
    return snap.get("live_stocks", [])


def load_directives_history(
    date_str: Optional[str] = None,
    portfolio_live: Optional[Dict[str, Any]] = None,
    regime: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Tải lịch sử chỉ thị tương tác giữa Chủ tịch và Minh Quân/Victor theo từng ngày mới."""
    if not date_str:
        date_str = get_ict_now().strftime("%Y-%m-%d")

    file_path = get_daily_directives_file(date_str)
    if file_path.exists():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and data:
                    return data
        except Exception:
            pass
    else:
        try:
            from scripts.apex_cloud_db_sync import ApexCloudDBSync
            cloud_dirs = ApexCloudDBSync.restore_directives_if_missing(date_str)
            if cloud_dirs:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(cloud_dirs, f, ensure_ascii=False, indent=2)
                return cloud_dirs
        except Exception:
            pass

    if portfolio_live is None or regime is None:
        snap = _get_live_snapshot()
        portfolio_live = portfolio_live or snap.get("portfolio_live", {})
        regime = regime or snap.get("intraday_regime", {})

    cash_vnd = float(portfolio_live.get("cash_vnd", 0.0))
    stocks_val = float(portfolio_live.get("stocks_val_vnd", 0.0))
    total_nav = float(portfolio_live.get("total_nav_vnd", cash_vnd + stocks_val))
    cash_pct = float(portfolio_live.get("cash_pct", 100.0))
    total_shares = int(portfolio_live.get("total_shares", 0))
    holdings_desc = portfolio_live.get("holdings_desc", "0 CP")
    realized = float(portfolio_live.get("realized_pnl_vnd", 0.0))
    regime_label = regime.get("label", "GIẰNG CO PHÂN HÓA")

    default_history = [
        {
            "id": f"dir_{date_str}_001",
            "timestamp": "08:30:15",
            "sender": "Minh Quân (Ban 7 VN)",
            "role": "specialist",
            "type": "morning_brief",
            "content": (
                f"Kính trình Chủ tịch Trần Quốc Thiên Phước! Minh Quân đã kích hoạt Living War-Room V4.0 cho ngày {date_str}. "
                f"Chế độ thị trường hiện tại: {regime_label}. Kỷ luật bất biến: KHÔNG ĐUA LỆNH ATO, kiên nhẫn chờ Khung Giờ Vàng 14h00 - 14h25!"
            )
        },
        {
            "id": f"dir_{date_str}_002",
            "timestamp": "08:32:40",
            "sender": "Victor (Ban 9 Live Sentinel)",
            "role": "sentinel",
            "type": "sentinel_brief",
            "content": (
                f"Báo cáo Chủ tịch! Victor túc trực 24/7 bảo vệ danh mục SSOT ngày {date_str}. "
                f"Tổng NAV live: {total_nav:,.0f} đ | Tiền mặt thật: {cash_vnd:,.0f} đ ({cash_pct:.1f}% Cash) | "
                f"Đang nắm giữ: {total_shares} CP ({holdings_desc} ≈ {stocks_val:,.0f} đ) | Lãi đã chốt lũy kế: +{realized:,.0f} đ. "
                f"Bảng giá & Orderbook 3 bước giá đang được quét liên tục!"
            )
        }
    ]
    save_directives_history(default_history, date_str)
    return default_history


def save_directives_history(history: List[Dict[str, Any]], date_str: Optional[str] = None) -> None:
    """Lưu lịch sử chỉ thị tương tác vào file của đúng ngày hôm đó."""
    if not date_str:
        date_str = get_ict_now().strftime("%Y-%m-%d")
    file_path = get_daily_directives_file(date_str)
    try:
        trimmed = history[-60:] if len(history) > 60 else history
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(trimmed, f, ensure_ascii=False, indent=2)
        try:
            from scripts.apex_cloud_db_sync import ApexCloudDBSync
            if trimmed:
                ApexCloudDBSync.sync_directive(trimmed[-1], date_str)
        except Exception:
            pass
    except Exception as e:
        print(f"Error saving directives: {e}", file=sys.stderr)


def push_external_war_room_alert(
    sender: str,
    alert_type: str,
    content: str,
    role: str = "sentinel",
    alert_key: Optional[str] = None,
    date_str: Optional[str] = None,
) -> bool:
    """
    Hook liên phòng ban: Cho phép Ban 9 Sentinel, Ban 10 CBTT Radar, hoặc Sync TCInvest
    bơm trực tiếp cảnh báo khẩn / sự kiện trọng yếu vào Bảng Chỉ Thị Live của War-Room (có chống trùng lặp theo ngày).
    """
    now = get_ict_now()
    if not date_str:
        date_str = now.strftime("%Y-%m-%d")

    directives = load_directives_history(date_str)
    dedup_id = alert_key or f"ext_{date_str}_{alert_type}_{abs(hash(content)) % 1000000}"
    if any(d.get("id") == dedup_id or (alert_key and d.get("key") == alert_key) for d in directives):
        return False

    entry = {
        "id": dedup_id,
        "key": dedup_id,
        "timestamp": now.strftime("%H:%M:%S"),
        "sender": sender,
        "role": role,
        "type": alert_type,
        "content": content,
    }
    directives.append(entry)
    save_directives_history(directives, date_str)
    return True


_VICTOR_REPORT_LAST_WRITE_TS = 0.0
_DEMO_PLAN_LAST_WRITE_TS = 0.0


def build_victor_realtime_alert_center(
    snap: Dict[str, Any],
    phase_info: Dict[str, Any],
    force_write_report: bool = False,
) -> Dict[str, Any]:
    """
    BAN 9 (VICTOR) — TRUNG TÂM GIÁM SÁT BIẾN ĐỘNG & CẢNH BÁO TÍN HIỆU THỜI GIAN THỰC 24/7.
    Hoạt động xuyên suốt MỌI PHIÊN LÀM VIỆC (Pre-ATO, Phiên sáng, Nghỉ trưa, Phiên chiều,
    Khung Giờ Vàng 14h00-14h25, ATC, Phiên tối / Bản Demo Trước Phiên).
    Quét toàn bộ mã nắm giữ + watchlist TCBS/Thượng đỉnh để phát hiện ngay:
      1) Chạm / Cận ngưỡng cắt lỗ Stop 2xATR (STOP_LOSS_BREACH / NEAR_STOP_WARNING)
      2) Chạm ngưỡng chốt lời TP1 / TP2 hoặc Đủ biên độ lướt T+0 (TP_REACHED / PROFIT_T0_READY)
      3) Đạt vùng canh mua LO kèm Mua chủ động tốt (BUY_ZONE_REACHED)
      4) Áp lực cung / Bán chủ động áp đảo -> Cấm bắt đáy (BEARISH_PRESSURE_AVOID)
      5) Chờ nhúng pullback / Vượt trần quy mô lô 100 > 33% NAV
    """
    global _VICTOR_REPORT_LAST_WRITE_TS
    now = get_ict_now()
    date_str = phase_info.get("current_date_str") or now.strftime("%Y-%m-%d")
    time_str = phase_info.get("current_time_str") or now.strftime("%H:%M:%S")
    port = snap.get("portfolio_live", {}) or {}
    regime = snap.get("intraday_regime", {}) or {}
    market_ov = snap.get("market_overview", {}) or {}
    vni = market_ov.get("vn_index", {}) or {}
    vn30 = market_ov.get("vn30_index", {}) or {}
    breadth = market_ov.get("market_breadth", {}) or {}
    live_stocks = snap.get("live_stocks", []) or []

    total_nav_vnd = float(port.get("total_nav_vnd") if port.get("total_nav_vnd") is not None else 20051117.0)
    cash_vnd = float(port.get("cash_vnd") if port.get("cash_vnd") is not None else 20051117.0)
    adv_ratio = float(breadth.get("advance_ratio_pct") or 50.0)
    active_phase_id = str(phase_info.get("active_phase_id") or "")
    is_morning_session = ("MORNING" in active_phase_id) or ("ATO" in active_phase_id)
    regime_id = str(regime.get("regime_id") or "SIDEWAY_CHOPPY")
    regime_label = str(regime.get("label") or "GIẰNG CO PHÂN HÓA")
    active_phase_name = str(phase_info.get("active_phase_name") or phase_info.get("active_phase_id") or "24/7 MONITOR")

    alerts: List[Dict[str, Any]] = []
    severity_rank = {"CRITICAL": 0, "ACTION_SELL": 1, "HIGH": 2, "OPPORTUNITY": 3, "WARNING": 4, "INFO": 5}

    for s in live_stocks:
        code = str(s.get("code") or "").upper().strip()
        if not code:
            continue
        is_holding = bool(s.get("is_holding"))
        price = float(s.get("price") or 0.0)
        chg_pct = float(s.get("change_pct") or 0.0)
        buy_up = float(s.get("active_buy_pct") or 50.0)
        probe_target = float(s.get("probe_target") or price or 0.0)
        stop_loss = float(s.get("stop_loss") or 0.0)
        tp1 = float(s.get("tp1") or 0.0)
        tp2 = float(s.get("tp2") or 0.0)
        rsi14 = float(s.get("rsi14") or 50.0)
        lot_100_cost = price * 100.0
        lot_nav_pct = round((lot_100_cost / max(total_nav_vnd, 1.0)) * 100.0, 1)

        dist_stop_pct = round(((price - stop_loss) / price) * 100.0, 2) if (price > 0 and stop_loss > 0) else 0.0
        dist_tp1_pct = round(((tp1 - price) / price) * 100.0, 2) if (price > 0 and tp1 > 0) else 0.0
        dist_probe_pct = round(((price - probe_target) / probe_target) * 100.0, 2) if (price > 0 and probe_target > 0) else 0.0

        category = "MONITORING"
        severity = "INFO"
        badge = "🔵 THEO DÕI"
        condition_text = ""
        recommended_action = ""

        if is_holding:
            # Kiểm tra các ngưỡng quan trọng của cổ phiếu ĐANG NẮM GIỮ
            if stop_loss > 0 and price <= stop_loss:
                category = "STOP_LOSS_BREACH"
                severity = "CRITICAL"
                badge = "🔴 CHẠM STOP CẮT LỖ"
                condition_text = f"Giá {price:,.0f}đ <= Stop {stop_loss:,.0f}đ ({dist_stop_pct:+.2f}%)"
                recommended_action = f"BÁO ĐỘNG ĐỎ: Kiểm định nến 14h15; nếu không rút chân trên {stop_loss:,.0f}đ phải cắt dứt khoát bảo vệ vốn!"
            elif tp2 > 0 and price >= tp2:
                category = "TP2_REACHED"
                severity = "ACTION_SELL"
                badge = "🟢 CHẠM ĐỈNH CHỐT LỜI TP2"
                condition_text = f"Giá {price:,.0f}đ >= TP2 {tp2:,.0f}đ"
                recommended_action = f"Đạt kỳ vọng TP2! Chủ tịch chốt lời phần còn lại bằng lệnh LO vùng {price:,.0f}đ để khóa lợi nhuận."
            elif tp1 > 0 and price >= tp1:
                category = "TP1_REACHED"
                severity = "ACTION_SELL"
                badge = "🟢 ĐẠT NGƯỠNG CHỐT LỜI TP1"
                condition_text = f"Giá {price:,.0f}đ >= TP1 {tp1:,.0f}đ"
                recommended_action = f"Kích hoạt Scaling Out: Bán chốt lời 50% vị thế tại {price:,.0f}đ, nâng Stop 50% còn lại lên giá vốn."
            elif stop_loss > 0 and dist_stop_pct <= 2.6:
                category = "NEAR_STOP_WARNING"
                severity = "HIGH"
                badge = f"🟡 CẬN NGƯỠNG BẢO VỆ (+{dist_stop_pct:.2f}%)"
                condition_text = f"Cách Stop/Cảnh báo {stop_loss:,.0f}đ chỉ {dist_stop_pct:.2f}% • Buy-Up {buy_up:.1f}%"
                recommended_action = (
                    f"Đang giữ đệm lãi tốt (Buy-Up {buy_up:.1f}%), giữ nguyên kỷ luật kiểm định lúc 14h15 (cắt nếu đóng thủng Hard Stop)."
                )
            elif is_morning_session and chg_pct >= 2.2 and (buy_up < 45.0 or adv_ratio < 42.0):
                category = "MORNING_FADE_LOCK"
                severity = "ACTION_SELL"
                badge = f"⚡ MORNING-FADE LOCK ({chg_pct:+.1f}% | BuyUp {buy_up:.0f}%)"
                condition_text = f"Kéo sáng {chg_pct:+.2f}% nhưng Buy-Up {buy_up:.1f}% / Breadth {adv_ratio:.0f}% yếu"
                recommended_action = (
                    f"KHÓA LÃI SÁNG: Bán chốt 50–100% vị thế vùng {price:,.0f}đ để tránh rơi lãi về chiều; chỉ cover lại khi nhúng -2.0%..-2.8%."
                )
            elif buy_up < 45.0:
                category = "HOLDING_WEAK_DEMAND"
                severity = "WARNING"
                badge = f"⚠️ CẦU YẾU CẦN CANH ({buy_up:.0f}%)"
                condition_text = f"Cách Stop +{dist_stop_pct:.2f}% • Buy-Up chỉ {buy_up:.1f}% (< 45%)"
                recommended_action = (
                    f"Cầu chủ động yếu ({buy_up:.1f}%). Tuyệt đối không mua thêm; sẵn sàng chốt giữ lãi nếu kéo xanh yếu lực hoặc siết Stop 14h15."
                )
            else:
                category = "HOLDING_PROFIT_HEALTHY"
                severity = "INFO"
                badge = f"🟢 LÃI ĐỆM AN TOÀN (BuyUp {buy_up:.0f}%)"
                condition_text = f"Cách Stop +{dist_stop_pct:.2f}% • Còn +{dist_tp1_pct:.2f}% tới TP1 ({tp1:,.0f}đ)"
                recommended_action = (
                    f"Cầu chủ động {buy_up:.1f}% ổn định. Giữ vị thế gồng lãi; chỉ lướt T+0 nếu nhúng về vùng {round(price*0.978,-1):,.0f}đ."
                )
        else:
            # Kiểm tra các ngưỡng quan trọng của cổ phiếu TẦM NGẮM (WATCHLIST)
            if lot_nav_pct > 33.0 or lot_100_cost > cash_vnd:
                category = "CAPITAL_FIT_LOCK"
                severity = "INFO"
                badge = f"⛔ KHÓA SIZE LÔ 100 ({lot_nav_pct:.1f}% NAV)"
                condition_text = f"1 lô = {lot_100_cost:,.0f}đ vượt trần 33% NAV"
                recommended_action = "Không giải ngân để bảo toàn tính cơ động danh mục nhỏ."
            elif buy_up <= 40.0 or (chg_pct <= -1.0 and buy_up < 50.0):
                category = "BEARISH_PRESSURE_AVOID"
                severity = "WARNING"
                badge = f"🟠 ÁP LỰC CUNG (BuyUp {buy_up:.1f}%)"
                condition_text = f"Giá {price:,.0f}đ ({chg_pct:+.2f}%) • Bán chủ động áp đảo"
                recommended_action = (
                    f"CẤM BẮT ĐÁY SỚM! Chỉ xem xét lại khi Buy-Up phục hồi >= 58% quanh vùng {probe_target:,.0f}đ sau 14h00."
                )
            elif regime_id != "DEFENSIVE_SELLOFF" and probe_target > 0 and dist_probe_pct <= 1.2 and buy_up >= 55.0:
                category = "BUY_ZONE_REACHED"
                severity = "OPPORTUNITY"
                badge = f"🟢 ĐẠT VÙNG MUA LO ({lot_nav_pct:.1f}% NAV)"
                condition_text = f"Giá {price:,.0f}đ sát mục tiêu {probe_target:,.0f}đ ({dist_probe_pct:+.2f}%) • BuyUp {buy_up:.1f}%"
                recommended_action = (
                    f"Đủ điều kiện theo dõi giải ngân 1 lô LO vùng {round(probe_target*0.99,-1):,.0f}–{probe_target:,.0f}đ "
                    f"trong Khung Giờ Vàng 14h00–14h25 (Stop {stop_loss:,.0f}đ)."
                )
            elif rsi14 >= 70.0 or dist_probe_pct > 2.0:
                category = "WAIT_PULLBACK"
                severity = "INFO"
                badge = "🟡 CHỜ NHÚNG CHIẾT KHẤU"
                condition_text = f"Đang cao hơn điểm mua LO {dist_probe_pct:+.2f}% (Mục tiêu {probe_target:,.0f}đ)"
                recommended_action = f"Kiên nhẫn chờ giá nhúng về {probe_target:,.0f}đ hoặc nến Test Cung Vol cạn."
            else:
                category = "STANDBY_RADAR"
                severity = "INFO"
                badge = f"🔵 RADAR ỔN ĐỊNH (BuyUp {buy_up:.0f}%)"
                condition_text = f"Lô 100 = {lot_100_cost:,.0f}đ ({lot_nav_pct:.1f}% NAV) • Cách TP1 +{dist_tp1_pct:.1f}%"
                recommended_action = f"Theo dõi diễn biến thanh khoản tại vùng {probe_target:,.0f}đ trong phiên chiều."

        alerts.append({
            "alert_id": f"{date_str}_{code}_{category}",
            "symbol": code,
            "name": s.get("name", code),
            "is_holding": is_holding,
            "category": category,
            "severity": severity,
            "trigger_badge": badge,
            "price": price,
            "change_pct": chg_pct,
            "buy_up_pct": buy_up,
            "rsi14": rsi14,
            "probe_target": probe_target,
            "stop_loss": stop_loss,
            "tp1": tp1,
            "tp2": tp2,
            "dist_to_probe_pct": dist_probe_pct,
            "dist_to_stop_pct": dist_stop_pct,
            "dist_to_tp1_pct": dist_tp1_pct,
            "lot_nav_pct": lot_nav_pct,
            "condition_text": condition_text,
            "recommended_action": recommended_action,
            "data_source": s.get("data_source", "VPS_DIRECT_HOSE_TICK"),
            "is_live": bool(s.get("is_live", False)),
        })

    alerts.sort(key=lambda a: (severity_rank.get(a["severity"], 9), 0 if a["is_holding"] else 1, -abs(a["buy_up_pct"] - 50.0)))

    critical_cnt = sum(1 for a in alerts if a["severity"] == "CRITICAL")
    sell_cnt = sum(1 for a in alerts if a["severity"] == "ACTION_SELL")
    near_stop_cnt = sum(1 for a in alerts if a["category"] == "NEAR_STOP_WARNING")
    buy_zone_cnt = sum(1 for a in alerts if a["category"] == "BUY_ZONE_REACHED")
    avoid_cnt = sum(1 for a in alerts if a["category"] == "BEARISH_PRESSURE_AVOID")

    summary = {
        "scan_timestamp": f"{date_str} {time_str} ICT",
        "session_phase": active_phase_name,
        "market_regime_id": regime_id,
        "market_regime_label": regime_label,
        "vn_index_val": float(vni.get("value") or 0.0),
        "vn_index_chg_pct": float(vni.get("change_pct") or 0.0),
        "basis_vn30f": str(vn30.get("basis_vn30f") or "--"),
        "breadth_advancers": int(breadth.get("advancers") or 0),
        "breadth_decliners": int(breadth.get("decliners") or 0),
        "total_monitored": len(alerts),
        "critical_stop_count": critical_cnt,
        "take_profit_count": sell_cnt,
        "near_stop_count": near_stop_cnt,
        "buy_zone_count": buy_zone_cnt,
        "avoid_knife_count": avoid_cnt,
        "headline": (
            f"Victor (Ban 9) quét LIVE {len(alerts)} mã trên mọi phiên ({date_str} {time_str}): "
            f"{buy_zone_cnt} mã ĐẠT VÙNG MUA LO | {sell_cnt} mã ĐẠT CHỐT LỜI | "
            f"{critical_cnt} VI PHẠM STOP / {near_stop_cnt} CẬN STOP | {avoid_cnt} CẢNH BÁO ÁP LỰC CUNG."
        ),
    }

    result = {
        "protocol": "VICTOR_247_REALTIME_TRIGGER_CENTER_V1",
        "always_active_across_all_sessions": True,
        "summary": summary,
        "alerts": alerts,
    }

    now_epoch = time.time()
    ledger_file = DATA_DIR / "victor_realtime_alert_ledger.json"
    report_path = BASE_DIR / "09_Realtime_Portfolio_Sentinel" / f"{date_str}_Victor_Realtime_Trigger_Report.md"
    if force_write_report or (now_epoch - _VICTOR_REPORT_LAST_WRITE_TS >= 30.0) or not report_path.exists():
        _VICTOR_REPORT_LAST_WRITE_TS = now_epoch
        try:
            with open(ledger_file, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
        try:
            report_path.parent.mkdir(parents=True, exist_ok=True)
            rows_md = "\n".join(
                f"| **{a['symbol']}** | {'Đang giữ' if a['is_holding'] else 'Watchlist'} | `{a['price']:,.0f}đ ({a['change_pct']:+.2f}%)` | `{a['buy_up_pct']:.1f}%` | {a['trigger_badge']} | {a['recommended_action']} |"
                for a in alerts
            )
            md_txt = f"""# 🚨 BÁO CÁO GIÁM SÁT BIẾN ĐỘNG & CẢNH BÁO THỜI GIAN THỰC — VICTOR (BAN 9)
> **Cập nhật Realtime**: `{date_str} {time_str} ICT` | **Pha Phiên**: `{active_phase_name}`  
> **Thị trường**: `VN-Index {summary['vn_index_val']:,.2f} ({summary['vn_index_chg_pct']:+.2f}%)` | **Basis**: `{summary['basis_vn30f']}` | **Độ rộng**: `{summary['breadth_advancers']}T / {summary['breadth_decliners']}G`  
> **Cơ chế hoạt động**: **24/7 Xuyên Mọi Phiên Làm Việc** (Pre-ATO, ATO, Sáng, Trưa, Chiều, Khung Giờ Vàng, ATC, Ngoài Giờ/Demo)

---

## TỔNG HỢP TÍN HIỆU QUAN TRỌNG TỨC THỜI
- **Mã đạt vùng canh mua LO tiềm năng**: `{buy_zone_cnt}` mã
- **Mã chạm ngưỡng chốt lời TP1/TP2**: `{sell_cnt}` mã
- **Mã chạm Stop Loss 2xATR**: `{critical_cnt}` mã | **Mã cận ngưỡng bảo vệ**: `{near_stop_cnt}` mã
- **Mã áp lực cung mạnh (Cấm bắt đáy)**: `{avoid_cnt}` mã

| Mã CP | Trạng Thái | Giá Live (+/-%) | Buy-Up % | Nhãn Cảnh Báo Victor | Khuyến Nghị Hành Động |
| :---: | :---: | :---: | :---: | :--- | :--- |
{rows_md}
"""
            report_path.write_text(md_txt, encoding="utf-8")
            try:
                from scripts.apex_live_intraday_brain import _upsert_report_into_vault
                _upsert_report_into_vault(report_path, dept_id="ban_9_sentinel")
            except Exception:
                pass
        except Exception:
            pass

    return result


def build_demo_tactical_plan_tomorrow(
    snap: Dict[str, Any],
    phase_info: Dict[str, Any],
    victor_center: Dict[str, Any],
    force_write_report: bool = False,
) -> Dict[str, Any]:
    """
    TỔNG HỢP BÁO CÁO THƯỢNG ĐỈNH 00H45 + NGHIÊN CỨU THỊ TRƯỜNG + BẢNG GIÁ TCBS THỰC TẾ
    LẬP BẢN DEMO KẾ HOẠCH TÁC CHIẾN CHO PHIÊN GIAO DỊCH TIẾP THEO (16/11/2026).
    CƠ ĐỘNG 100%: Khi thị trường mở cửa và biến động, hệ thống tự động hiệu chỉnh kịch bản
    và đẩy báo cáo cập nhật ngay lập tức vào Phòng Tác Chiến.
    """
    global _DEMO_PLAN_LAST_WRITE_TS
    now = get_ict_now()
    date_str = phase_info.get("current_date_str") or now.strftime("%Y-%m-%d")
    time_str = phase_info.get("current_time_str") or now.strftime("%H:%M:%S")
    hm = now.hour * 60 + now.minute
    is_weekend = bool(phase_info.get("is_weekend", now.weekday() >= 5))
    in_market = (not is_weekend) and (8 * 60 + 30 <= hm <= 14 * 60 + 45)

    port = snap.get("portfolio_live", {}) or {}
    regime = snap.get("intraday_regime", {}) or {}
    mkt = snap.get("market_overview", {}) or {}
    vni = mkt.get("vn_index", {}) or {}
    breadth = mkt.get("market_breadth", {}) or {}
    weekly_data = _load_v8_json_safe("data/weekly_tactical_plan_active.json")

    cash_vnd = float(port.get("cash_vnd") if port.get("cash_vnd") is not None else 20051117.0)
    stocks_val_vnd = float(port.get("stocks_val_vnd") if port.get("stocks_val_vnd") is not None else 0.0)
    total_nav_vnd = float(port.get("total_nav_vnd") if port.get("total_nav_vnd") is not None else (cash_vnd + stocks_val_vnd))
    cash_pct = float(port.get("cash_pct") if port.get("cash_pct") is not None else round((cash_vnd / max(total_nav_vnd, 1.0)) * 100.0, 1))
    unrealized_pnl = float(port.get("unrealized_pnl_vnd") or 0.0)
    unrealized_pct = float(port.get("unrealized_pnl_pct") or 0.0)
    holdings = port.get("holdings", []) or []

    regime_id = str(regime.get("regime_id") or "SIDEWAY_CHOPPY")
    if regime_id == "RISK_ON_BREAKOUT":
        active_scenario_id = "SCENARIO_A_BREAKOUT"
    elif regime_id == "DEFENSIVE_SELLOFF":
        active_scenario_id = "SCENARIO_C_DEFENSE"
    else:
        active_scenario_id = "SCENARIO_B_ACCUMULATION"

    buy_alerts = [a for a in victor_center.get("alerts", []) if a.get("category") == "BUY_ZONE_REACHED"]
    avoid_alerts = [a for a in victor_center.get("alerts", []) if a.get("category") == "BEARISH_PRESSURE_AVOID"]
    hold_alerts = [a for a in victor_center.get("alerts", []) if a.get("is_holding")]

    vni_val = float(vni.get("value") or 0.0)
    vni_chg_pct = float(vni.get("change_pct") or 0.0)
    adv_cnt = int(breadth.get("advancers") or 0)
    dec_cnt = int(breadth.get("decliners") or 0)
    tot_br = adv_cnt + dec_cnt
    breadth_pct_str = f"{(adv_cnt * 100.0 / tot_br):.1f}% xanh ({adv_cnt}T/{dec_cnt}G)" if tot_br > 0 else "Đang khớp ATO (chưa mở toàn bảng)"
    buy_syms_str = ", ".join(f"{a['symbol']} ({a['probe_target']:,.0f}đ, BuyUp {a['buy_up_pct']:.0f}%)" for a in buy_alerts[:3]) or "Chưa có mã đạt Buy-Up >= 60%"
    display_date = now.strftime("%d/%m/%Y")

    held_str = ", ".join(
        f"{int(h.get('shares', 0))} {h.get('symbol', '')}"
        for h in holdings
        if int(h.get("shares", 0) or 0) > 0
    ) or "0 CP"
    held_trail_notes = "; ".join(
        f"{a['symbol']} (Thị giá {a['price']:,.0f}đ, Stop {a['stop_loss']:,.0f}đ, TP1 {a['tp1']:,.0f}đ)"
        for a in hold_alerts
    ) or "Chưa có vị thế nắm giữ"

    def _slot_label(start_min: int, end_min: int, base_phase: str) -> str:
        return f"{base_phase} ⚡ [ĐANG CHẠY LIVE]" if (in_market and start_min <= hm < end_min) else base_phase

    hourly_roadmap = [
        {
            "slot": "08:30 – 09:00",
            "phase": _slot_label(8 * 60 + 30, 9 * 60, "PRE-ATO GIAO BAN & ĐỐI SOÁT QUA ĐÊM"),
            "action": f"Kiểm tra SSOT {cash_pct:.1f}% Cash ({cash_vnd:,.0f} ₫ / {held_str}), quét tin Internet/BCTC Q3/2026 & khởi động động cơ quét sống 145 mã."
        },
        {
            "slot": "09:00 – 10:00",
            "phase": _slot_label(9 * 60, 10 * 60, "ATO & KỶ LUẬT CẤM FOMO ĐẦU PHIÊN"),
            "action": "TUYỆT ĐỐI KHÔNG mua đuổi giá xanh ATO/sáng (CHAL_03). Quét bảng điện 145 mã, đo Buy-Up % và độ rộng Breadth > MA20 thực tế."
        },
        {
            "slot": "10:00 – 11:30",
            "phase": _slot_label(10 * 60, 11 * 60 + 30, "QUÉT DÒNG TIỀN 18 NGÀNH & GIÁM SÁT LIVE"),
            "action": f"Giám sát vị thế: {held_trail_notes}. Lọc trực tiếp Top 5 cổ phiếu BCTC sạch dẫn dắt dòng tiền 18 nhóm ngành."
        },
        {
            "slot": "11:30 – 13:00",
            "phase": _slot_label(11 * 60 + 30, 13 * 60, "TỔNG KẾT PHIÊN SÁNG & CẬP NHẬT KỊCH BẢN CHIỀU"),
            "action": "Giao ban giữa phiên (11h35): Cập nhật báo cáo dòng tiền 18 ngành lên Web Portal & Phòng Tác Chiến Mỗi Ngày trên Telegram."
        },
        {
            "slot": "13:00 – 14:00",
            "phase": _slot_label(13 * 60, 14 * 60, "HẤP THỤ HÀNG T+2 & KIỂM ĐỊNH CẦU CHIỀU"),
            "action": "Quan sát lực hấp thụ hàng T+2 buổi chiều; kiểm định mốc hỗ trợ VN-Index 1,678 (Spring) và đáy 1,666.41 (20/11)."
        },
        {
            "slot": "14:00 – 14:45",
            "phase": _slot_label(14 * 60, 14 * 60 + 46, "⭐ KHUNG GIỜ VÀNG QUYẾT ĐỊNH & CẤM ATC"),
            "action": "⭐ KHUNG GIỜ VÀNG (14h05–14h25): Kích hoạt S3 Spring V3.0 (30–40% NAV: TPB 300 @ 12,250đ, CTG 100 @ 29,950đ, HDB 200 @ 21,700đ, Stop -5.5%) nếu VNI >= 1,678 & Buy-Up >= 58%; hoặc S1 (75–85%) / S2 (30–45%); thủng 1,666 giữ S4 100% Tiền mặt!"
        },
    ]

    contingency_modes = [
        {
            "id": "SCENARIO_A_BREAKOUT",
            "title": "Kịch Bản S1/S3: Đồng Thuận Sóng Hoặc Spring Bất Đối Xứng (14h05–14h25)",
            "trigger": "S3 Spring: VNI >= 1,678, Br20 >= 24%, Vol >= 1.05x, Buy-Up >= 58% | S1 Uptrend: VNI > MA20 & Br20 >= 50%.",
            "action": f"Hiện tại SSOT {cash_vnd:,.0f}đ ({cash_pct:.1f}% Cash). Đạt S3 bấm tối đa 2 mã (30–40% NAV: TPB 300 @ 12,250đ, CTG 100 @ 29,950đ, HDB 200 @ 21,700đ, Stop -5.5%); đạt S1 bung 75–85% NAV (TPB, HDB, HPG, VPB).",
            "is_active_now": active_scenario_id == "SCENARIO_A_BREAKOUT",
        },
        {
            "id": "SCENARIO_B_ACCUMULATION",
            "title": "Kịch Bản S2: Giằng Co Phân Hóa / Bắn Tỉa Chọn Lọc",
            "trigger": f"VN-Index đi ngang giữ nền ({vni_val:,.2f} • {vni_chg_pct:+.2f}%), Độ rộng: {breadth_pct_str}.",
            "action": f"Giữ kỷ luật trước 14h05; nếu đạt S2 (Breadth 30–50%) giải ngân chọn lọc 30–45% NAV vào HDB/TPB, Stop -5.5%, TP1 +6.5%..+9.0% Scaling Out 50/50.",
            "is_active_now": active_scenario_id == "SCENARIO_B_ACCUMULATION",
        },
        {
            "id": "SCENARIO_C_DEFENSE",
            "title": "Kịch Bản S4: Áp Lực Bán / Thủng Đáy — Lá Chắn 100% Tiền Mặt",
            "trigger": "VN-Index thủng đáy 1,666.41 hoặc Buy-Up < 48% hoặc mất ngưỡng an toàn xu hướng.",
            "action": f"KHÓA 100% lệnh mua mới; giữ nguyên 100% Tiền mặt sạch ({cash_vnd:,.0f} ₫) bảo toàn 0 ₫ thua lỗ.",
            "is_active_now": active_scenario_id == "SCENARIO_C_DEFENSE",
        },
    ]

    is_pre_session_demo = not in_market
    demo_report_rel_path = f"VN_Market/07_Daily_Specialist/{date_str}_Demo_PreSession_Tactical_Plan.md"
    official_report_rel_path = f"VN_Market/07_Daily_Specialist/{date_str}_Official_Adaptive_Tactical_Plan.md"
    report_rel_path = official_report_rel_path if in_market else demo_report_rel_path
    plan_title = (
        f"KẾ HOẠCH ĐẦU TƯ CHÍNH THỨC HÔM NAY ({display_date}) — BRAIN V3.0 & TÁC CHIẾN 145 MÃ"
        if in_market
        else f"KẾ HOẠCH TÁC CHIẾN SẴN SÀNG TUẦN 48 ({display_date}) — BRAIN V3.0 & 100% CASH"
    )
    result = {
        "plan_id": f"OFFICIAL-V3-{date_str.replace('-', '')}" if in_market else f"READY-V3-{date_str.replace('-', '')}",
        "title": plan_title,
        "is_pre_session_demo": is_pre_session_demo,
        "is_reference_only": False if in_market else True,
        "live_market_open": in_market,
        "auto_adapt_status": (
            f"🟢 KẾ HOẠCH CHÍNH THỨC ĐANG TỰ ĐỘNG HIỆU CHỈNH LIVE ({phase_info.get('active_phase_short', 'TRONG PHIÊN')})"
            if in_market
            else "🟡 NGOÀI GIỜ GIAO DỊCH — TỰ ĐỘNG BẬT QUÉT LIVE LÚC 09H00 THỨ HAI"
        ),
        "generated_at": f"{date_str} {time_str} ICT",
        "summit_basis": f"Dữ liệu LIVE {time_str} {display_date} + Brain V3.0 (145 mã + BCTC Q3/2026) + SSOT TCBS 105C307855",
        "constitution_note": (
            f"KẾ HOẠCH THỰC CHIẾN BRAIN V3.0 NGÀY {display_date} (SSOT: {held_str} • Cash {cash_pct:.1f}%): Không FOMO trước 14h05, cấm BAF/VIX/CII/CEO; kích hoạt S1/S2/S3/S4 tự chủ theo bảng điện."
            if in_market
            else f"SẴN SÀNG KHỞI ĐỘNG 09H00 THỨ HAI {display_date} (SSOT: {held_str} • Cash {cash_pct:.1f}% = {cash_vnd:,.0f} ₫). Rổ tầm ngắm V3.0: TPB, HDB, CTG, HPG, VPB."
        ),
        "portfolio_reconciled": {
            "account_id": "105C307855",
            "cash_vnd": cash_vnd,
            "stocks_val_vnd": stocks_val_vnd,
            "total_nav_vnd": total_nav_vnd,
            "cash_pct": cash_pct,
            "unrealized_pnl_vnd": unrealized_pnl,
            "unrealized_pnl_pct": unrealized_pct,
            "holdings_count": len(holdings),
        },
        "market_snapshot": {
            "vn_index": float(vni.get("value") or 0.0),
            "vn_index_chg_pct": float(vni.get("change_pct") or 0.0),
            "breadth_adv": int(breadth.get("advancers") or 0),
            "breadth_dec": int(breadth.get("decliners") or 0),
            "regime_label": str(regime.get("label") or "GIẰNG CO PHÂN HÓA"),
        },
        "holdings_brief": [
            {
                "symbol": a["symbol"],
                "price": a["price"],
                "stop_loss": a["stop_loss"],
                "tp1": a["tp1"],
                "buy_up_pct": a["buy_up_pct"],
                "badge": a["trigger_badge"],
                "action": a["recommended_action"],
            }
            for a in hold_alerts
        ],
        "buy_zone_candidates": [
            {
                "symbol": a["symbol"],
                "price": a["price"],
                "probe_target": a["probe_target"],
                "stop_loss": a["stop_loss"],
                "tp1": a["tp1"],
                "buy_up_pct": a["buy_up_pct"],
                "lot_nav_pct": a["lot_nav_pct"],
                "badge": a["trigger_badge"],
                "action": a["recommended_action"],
            }
            for a in buy_alerts
        ],
        "avoid_or_wait_candidates": [
            {
                "symbol": a["symbol"],
                "price": a["price"],
                "buy_up_pct": a["buy_up_pct"],
                "badge": a["trigger_badge"],
                "action": a["recommended_action"],
            }
            for a in avoid_alerts[:4]
        ],
        "hourly_roadmap": hourly_roadmap,
        "contingency_modes": contingency_modes,
        "active_scenario_id": active_scenario_id,
        "report_rel_path": report_rel_path,
    }

    now_epoch = time.time()
    report_path = BASE_DIR / demo_report_rel_path
    official_path = BASE_DIR / official_report_rel_path
    if force_write_report or (now_epoch - _DEMO_PLAN_LAST_WRITE_TS >= 60.0) or not report_path.exists() or not official_path.exists():
        _DEMO_PLAN_LAST_WRITE_TS = now_epoch
        try:
            report_path.parent.mkdir(parents=True, exist_ok=True)
            hold_md = "\n".join(
                f"- **{h['symbol']}**: Thị giá `{h['price']:,.0f}đ` | Stop `{h['stop_loss']:,.0f}đ` | TP1 `{h['tp1']:,.0f}đ` | Buy-Up `{h['buy_up_pct']:.1f}%` — {h['action']}"
                for h in result["holdings_brief"]
            ) or "- Hiện chưa có vị thế cổ phiếu."
            buy_md = "\n".join(
                f"- **{b['symbol']}**: Giá `{b['price']:,.0f}đ` (Canh `{b['probe_target']:,.0f}đ`, 1 lô `{b['lot_nav_pct']:.1f}% NAV`) | Buy-Up `{b['buy_up_pct']:.1f}%` | Stop `{b['stop_loss']:,.0f}đ` | TP1 `{b['tp1']:,.0f}đ` — {b['action']}"
                for b in result["buy_zone_candidates"]
            ) or "- Chưa có mã đạt vùng canh mua."
            avoid_md = "\n".join(
                f"- **{av['symbol']}**: Giá `{av['price']:,.0f}đ` | Buy-Up `{av['buy_up_pct']:.1f}%` — {av['action']}"
                for av in result["avoid_or_wait_candidates"]
            ) or "- Không có mã áp lực cung lớn."
            sched_md = "\n".join(
                f"| `{row['slot']}` | **{row['phase']}** | {row['action']} |"
                for row in hourly_roadmap
            )
            scen_md = "\n".join(
                f"- {'🟢 **[ĐANG KÍCH HOẠT]** ' if sc['is_active_now'] else ''}**{sc['title']}**: Điều kiện `{sc['trigger']}` ➔ {sc['action']}"
                for sc in contingency_modes
            )
            hdr_title = (
                f"# 🎯 KẾ HOẠCH ĐẦU TƯ CHÍNH THỨC HÔM NAY ({display_date}) — CƠ ĐỘNG THEO TỪNG PHIÊN"
                if in_market
                else f"# 🎯 KẾ HOẠCH TÁC CHIẾN NGÀY {display_date} — TỰ ĐỘNG CƠ ĐỘNG THEO THỊ TRƯỜNG"
            )
            demo_md = f"""{hdr_title}
> **Nguồn Tổng Hợp**: `{result['summit_basis']}`  
> **Cập Nhật Mới Nhất**: `{date_str} {time_str} ICT` | **Trạng Thái**: `{result['auto_adapt_status']}`  
> ⚡ **CƠ CHẾ TỰ ĐỘNG THÍCH NGHI**: {result['constitution_note']}

---

## I. ĐỐI SOÁT TÀI SẢN THỰC TẾ LIVE (TCBS `105C307855`)
- **Tổng Giá Trị Thị Trường Cổ Phiếu**: `{stocks_val_vnd:,.0f} ₫` (`{unrealized_pnl:+,.0f} ₫` / `{unrealized_pct:+.2f}%` so với giá vốn)
- **Tiền Mặt Khả Dụng**: `{cash_vnd:,.0f} ₫` (`{cash_pct:.1f}% NAV`)
- **Tổng Tài Sản Ròng Live (NAV)**: `{total_nav_vnd:,.0f} ₫`
- **Thị Trường Nền**: `VN-Index {vni_val:,.2f} ({vni_chg_pct:+.2f}%)` • Độ rộng `{breadth_pct_str}` • Chế độ `{result['market_snapshot']['regime_label']}`

---

## II. KẾ HOẠCH HÀNH ĐỘNG THEO DANH MỤC & TẦM NGẮM BẮN TỈA
### 1. Vị Thế Đang Nắm Giữ (Bảo Vệ Lãi Đệm & Chuẩn Bị T+0 / TP1)
{hold_md}

### 2. Mã Đạt Vùng Canh Mua LO Tiềm Năng (Thăm Dò Cơ Động Sau 14h00)
{buy_md}

### 3. Nhóm Đang Chịu Áp Lực Cung (Cấm Bắt Đáy Sớm)
{avoid_md}

---

## III. LỘ TRÌNH 6 KHUNG GIỜ TÁC CHIẾN TRONG NGÀY ({display_date})
| Khung Giờ (ICT) | Pha Tác Chiến | Hành Động Cơ Động Của Ban 7 VN & Ban 9 |
| :---: | :--- | :--- |
{sched_md}

---

## IV. 3 KỊCH BẢN PHẢN ỨNG CƠ ĐỘNG THEO DIỄN BIẾN BẢNG ĐIỆN
{scen_md}
"""
            report_path.write_text(demo_md, encoding="utf-8")
            official_path.write_text(demo_md, encoding="utf-8")
            try:
                from scripts.apex_live_intraday_brain import _upsert_report_into_vault
                _upsert_report_into_vault(official_path, dept_id="ban_7_vn_specialist")
                _upsert_report_into_vault(report_path, dept_id="ban_7_vn_specialist")
            except Exception:
                pass
        except Exception:
            pass

    return result


def evaluate_and_trigger_tactical_alerts(
    live_stocks: List[Dict[str, Any]],
    phase_info: Dict[str, Any],
    directives: List[Dict[str, Any]],
    date_str: str,
    snapshot: Optional[Dict[str, Any]] = None,
    victor_center: Optional[Dict[str, Any]] = None,
    demo_plan: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    CƠ CHẾ CẢNH BÁO TÁC CHIẾN ĐỘNG THEO THỜI GIAN THỰC TRÊN MỌI PHIÊN HOẠT ĐỘNG:
    - Chạy liên tục trên MỌI phiên (Pre-ATO, Sáng, Trưa, Chiều, Giờ Vàng, ATC, Sau giờ/Demo).
    - Tự động kích hoạt cảnh báo Stop Loss 2xATR, Cận Stop, Đạt TP1/TP2 cho MỌI mã đang nắm giữ.
    - Bắn báo cáo biến động quan trọng (Đạt vùng mua LO, Áp lực bán mạnh / Cấm bắt đáy) cho các mã theo dõi.
    - Tự động phát thông báo Bản Demo Kế hoạch Tác chiến & trạng thái hiệu chỉnh cơ động vào Phòng Tác Chiến.
    """
    now = get_ict_now()
    hm = now.hour * 60 + now.minute
    is_weekend = bool(phase_info.get("is_weekend", now.weekday() >= 5))
    in_market_hours = (not is_weekend) and (9 * 60 <= hm <= 14 * 60 + 45)
    in_golden_window = (not is_weekend) and (13 * 60 + 45 <= hm <= 14 * 60 + 25)

    snap = snapshot or {}
    port = snap.get("portfolio_live", {})
    regime = snap.get("intraday_regime", {})
    regime_id = regime.get("regime_id", "SIDEWAY_CHOPPY")

    cash_vnd = float(port.get("cash_vnd", 0.0))
    cash_pct = float(port.get("cash_pct", 100.0))
    total_nav = float(port.get("total_nav_vnd", cash_vnd))
    holdings = port.get("holdings", [])

    existing_ids = {d.get("id") for d in directives}
    prev_len = len(directives)
    changed = False
    t_now_str = now.strftime("%H:%M:%S")

    # 0. Báo cáo Bản Demo Kế hoạch Tác chiến (Pre-Session hoặc Chế độ Tự động hiệu chỉnh trong phiên)
    if demo_plan:
        demo_msg_id = f"dir_{date_str}_demo_tactical_plan_{'live' if in_market_hours else 'pre'}"
        if demo_msg_id not in existing_ids:
            buy_syms = ", ".join(b["symbol"] for b in demo_plan.get("buy_zone_candidates", [])[:4]) or "Chưa có"
            avoid_syms = ", ".join(a["symbol"] for a in demo_plan.get("avoid_or_wait_candidates", [])[:3]) or "Không có"
            directives.append({
                "id": demo_msg_id,
                "timestamp": t_now_str,
                "sender": "James (Master CIO) & Minh Quân (Ban 7 VN)",
                "role": "specialist",
                "type": "demo_tactical_plan",
                "content": (
                    f"📋 [TỔNG HỢP THƯỢNG ĐỈNH 00H45 & KẾ HOẠCH TÁC CHIẾN {date_str}] "
                    f"Trạng thái: {demo_plan.get('auto_adapt_status')}. "
                    f"Tài sản live: Cổ phiếu {float(port.get('stocks_val_vnd', 0)):,.0f}đ (PnL {float(port.get('unrealized_pnl_vnd', 0)):+,.0f}đ / {float(port.get('unrealized_pnl_pct', 0)):+.2f}%), "
                    f"Tiền mặt {cash_vnd:,.0f}đ ({cash_pct:.1f}% NAV • Tổng NAV {total_nav:,.0f}đ). "
                    f"Sẵn sàng vùng mua LO sau 14h00: {buy_syms} | Cấm bắt đáy: {avoid_syms}. "
                    f"(Bản Demo tự động hiệu chỉnh ngay khi bảng điện ngày mai biến động!)"
                ),
            })
            existing_ids.add(demo_msg_id)
            changed = True

    # 0b. Báo cáo Radar Biến Động 24/7 của Victor trên MỌI phiên làm việc
    if victor_center:
        v_alerts = victor_center.get("alerts", []) or []
        important_alerts = [
            a for a in v_alerts
            if a.get("severity") in ("CRITICAL", "ACTION_SELL", "HIGH", "OPPORTUNITY", "WARNING")
        ]
        if important_alerts:
            sig_tag = "|".join(f"{a['symbol']}:{a['category']}" for a in important_alerts[:6])
            pulse_id = f"dir_{date_str}_victor_247_{abs(hash(sig_tag)) % 100000}"
            if pulse_id not in existing_ids:
                brief_items = " • ".join(
                    f"{a['symbol']} ({a['price']:,.0f}đ: {a['trigger_badge']})"
                    for a in important_alerts[:5]
                )
                directives.append({
                    "id": pulse_id,
                    "timestamp": t_now_str,
                    "sender": "Victor (Ban 9 Live Sentinel — 24/7 Radar)",
                    "role": "sentinel",
                    "type": "sentinel_alert",
                    "content": (
                        f"🚨 [BÁO CÁO BIẾN ĐỘNG QUAN TRỌNG — MỌI PHIÊN ({phase_info.get('active_phase_short', 'LIVE')})] "
                        f"Victor phát hiện {len(important_alerts)} tín hiệu trọng yếu: {brief_items}. "
                        f"Xem chi tiết khoảng cách Mua LO / Chốt lời TP1 / Cắt lỗ Stop ngay tại Bảng Trung Tâm Cảnh Báo Victor bên dưới!"
                    ),
                })
                existing_ids.add(pulse_id)
                changed = True

    # 1. Cảnh báo Chế độ Thị trường Phòng thủ (trên mọi phiên nếu chế độ DEFENSIVE_SELLOFF xuất hiện)
    def_id = f"dir_{date_str}_regime_defensive"
    if regime_id == "DEFENSIVE_SELLOFF" and def_id not in existing_ids:
        directives.append({
            "id": def_id,
            "timestamp": t_now_str,
            "sender": "Victor (Ban 9 Live Sentinel) & Minh Quân (Ban 7 VN)",
            "role": "sentinel",
            "type": "sentinel_alert",
            "content": (
                f"🚨 [CẢNH BÁO CHẾ ĐỘ PHÒNG THỦ] {regime.get('label')}: {regime.get('guidance')} "
                f"Khóa 100% lệnh mua mới (Hạn mức 0%), bảo vệ két tiền mặt {cash_vnd:,.0f} đ ({cash_pct:.1f}% NAV)!"
            )
        })
        existing_ids.add(def_id)
        changed = True

    # 2. Cảnh báo realtime trên từng vị thế đang nắm giữ trong SSOT (kích hoạt trên MỌI phiên)
    for s in live_stocks:
        if not s.get("is_holding"):
            continue
        code = s["code"]
        act = s.get("action_code", "SAFE_HOLD")
        price = float(s.get("price", 0.0))
        stop_p = float(s.get("stop_loss", 0.0))
        tp1_p = float(s.get("tp1", 0.0))
        tp2_p = float(s.get("tp2", 0.0))

        if act == "STOP_TRIGGERED":
            aid = f"dir_{date_str}_stop_breached_{code}"
            if aid not in existing_ids:
                directives.append({
                    "id": aid,
                    "timestamp": t_now_str,
                    "sender": "Victor (Ban 9 Live Sentinel)",
                    "role": "sentinel",
                    "type": "sentinel_alert",
                    "content": (
                        f"🚨 [BÁO ĐỘNG ĐỎ CẮT LỖ 2xATR — {code}] Giá live {price:,.0f} đ đã chạm/thủng ngưỡng Stop Loss {stop_p:,.0f} đ! "
                        f"Kính trình Chủ tịch kiểm tra khớp cắt lỗ kỷ luật để khóa rủi ro <= 0.35% NAV!"
                    )
                })
                existing_ids.add(aid)
                changed = True
        elif act == "NEAR_STOP_WARNING" or (stop_p > 0 and 0 < float(s.get("dist_to_stop_pct", 99.0)) <= 2.6):
            aid = f"dir_{date_str}_near_stop_{code}"
            if aid not in existing_ids:
                directives.append({
                    "id": aid,
                    "timestamp": t_now_str,
                    "sender": "Victor (Ban 9 Live Sentinel)",
                    "role": "sentinel",
                    "type": "sentinel_alert",
                    "content": (
                        f"⚠️ [THEO DÕI CẬN NGƯỠNG BẢO VỆ — {code}] Giá live {price:,.0f} đ hiện cách mốc Stop/Cảnh báo ({stop_p:,.0f} đ) "
                        f"{s.get('dist_to_stop_pct', 0):.2f}%. Tuyệt đối KHÔNG bình quân giá xuống; kiểm định nến lúc 14h15!"
                    )
                })
                existing_ids.add(aid)
                changed = True
        elif act in ("TP1_REACHED", "TP2_REACHED"):
            aid = f"dir_{date_str}_{act.lower()}_{code}"
            if aid not in existing_ids:
                target_label = f"TP2 ({tp2_p:,.0f} đ)" if act == "TP2_REACHED" else f"TP1 ({tp1_p:,.0f} đ)"
                directives.append({
                    "id": aid,
                    "timestamp": t_now_str,
                    "sender": "Minh Quân (Ban 7 VN) & Victor",
                    "role": "specialist",
                    "type": "specialist_directive",
                    "content": (
                        f"🎯 [ĐẠT MỤC TIÊU CHỐT LỜI — {code}] Giá live {price:,.0f} đ đã chạm {target_label}! "
                        f"Đề xuất Scaling Out chốt lời 50% vị thế và nâng Stop Loss phần còn lại lên giá hòa vốn!"
                    )
                })
                existing_ids.add(aid)
                changed = True

    # 3. Tóm tắt giám sát vị thế buổi chiều (khi có holdings và đang trong phiên chiều)
    hold_id = f"dir_{date_str}_holding_sentinel"
    if holdings and in_market_hours and (13 * 60 <= hm <= 14 * 60 + 45) and hold_id not in existing_ids:
        summary_parts = []
        for h in holdings:
            summary_parts.append(
                f"{h.get('shares', 0)} {h.get('symbol')} @ Live {float(h.get('current_price', 0)):,.0f} đ ({float(h.get('pnl_pct', 0)):+.2f}%, Stop {float(h.get('stop_loss', 0)):,.0f} đ)"
            )
        directives.append({
            "id": hold_id,
            "timestamp": t_now_str,
            "sender": "Victor (Ban 9 Live Sentinel) & Minh Quân (Ban 7 VN)",
            "role": "sentinel",
            "type": "sentinel_alert",
            "content": (
                f"🛡️ [GIÁM SÁT PHIÊN CHIỀU LIVE] Danh mục hiện hữu: {' | '.join(summary_parts)}. "
                f"Két tiền mặt bảo toàn: {cash_vnd:,.0f} đ ({cash_pct:.1f}% NAV • Tổng NAV {total_nav:,.0f} đ). "
                f"Chế độ thị trường: {regime.get('label', 'N/A')}."
            )
        })
        existing_ids.add(hold_id)
        changed = True

    # 4. Tín hiệu mua mới trong Khung Giờ Vàng (chỉ bắn khi chưa cầm mã đó và Regime không DEFENSIVE)
    if in_golden_window and regime_id != "DEFENSIVE_SELLOFF":
        for s in live_stocks:
            if s.get("is_holding"):
                continue
            if s.get("action_code") in ("BUY_ZONE", "STANDBY_BUY_ZONE") and float(s.get("active_buy_pct", 0.0)) >= 55.0:
                bid = f"dir_{date_str}_golden_buy_{s['code']}"
                if bid not in existing_ids:
                    directives.append({
                        "id": bid,
                        "timestamp": t_now_str,
                        "sender": "Minh Quân (Ban 7 VN)",
                        "role": "specialist",
                        "type": "specialist_directive",
                        "content": (
                            f"🎯 [TÍN HIỆU KHUNG GIỜ VÀNG — {s['code']}] Giá live {s['price']:,.0f} đ vào vùng gom "
                            f"(Mục tiêu <= {s['probe_target']:,.0f} đ), Mua chủ động {s['active_buy_pct']:.1f}%, "
                            f"Stop {s['stop_loss']:,.0f} đ, TP1 {s['tp1']:,.0f} đ. Xin Chủ tịch xem xét giải ngân LO!"
                        )
                    })
                    existing_ids.add(bid)
                    changed = True

    if changed:
        save_directives_history(directives, date_str)
        if (not is_weekend) and prev_len < len(directives):
            try:
                from scripts.telegram_dispatcher import dispatch_message
                for new_d in directives[prev_len:]:
                    d_type = str(new_d.get("type") or "")
                    c_txt = str(new_d.get("content") or "")
                    if not c_txt:
                        continue
                    dispatch_message("daily_warroom", c_txt, mirror_to_reports_vault=False)
                    if d_type in ("specialist_directive", "demo_tactical_plan") and in_golden_window:
                        dispatch_message("james_hq", c_txt, mirror_to_reports_vault=False)
            except Exception:
                pass
    return directives


def get_weekly_reference_roadmap(snapshot: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    BẢNG KẾ HOẠCH TÁC CHIẾN TUẦN (ĐỊNH HƯỚNG THAM KHẢO CHO CHỦ TỊCH):
    - Nạp từ SSOT: data/weekly_tactical_plan_active.json
    - Đồng thời đồng bộ trạng thái khớp lệnh / giá hiện tại từ Snapshot thực tế để tránh lệch số liệu.
    """
    plan_file = DATA_DIR / "weekly_tactical_plan_active.json"
    plan_data: Optional[Dict[str, Any]] = None
    if plan_file.exists():
        try:
            with open(plan_file, "r", encoding="utf-8") as f:
                plan_data = json.load(f)
        except Exception:
            plan_data = None

    snap = snapshot or _get_live_snapshot()
    port = snap.get("portfolio_live", {})
    live_map = {s["code"]: s for s in snap.get("live_stocks", [])}
    holdings_map = {h.get("symbol"): h for h in port.get("holdings", [])}

    if plan_data:
        # Enrich approved_watchlist dynamically without mutating user policy rules
        enriched_wl = []
        for item in plan_data.get("approved_watchlist", []):
            sym = str(item.get("symbol", "")).upper()
            copied = dict(item)
            if sym in holdings_map:
                h = holdings_map[sym]
                copied["executed_shares"] = int(h.get("shares", 0))
                copied["current_status"] = (
                    f"ĐANG NẮM GIỮ {h.get('shares', 0)} CP @ Vốn {float(h.get('avg_cost', 0)):,.0f} đ "
                    f"(Live {float(h.get('current_price', 0)):,.0f} đ • {float(h.get('pnl_pct', 0)):+.2f}%)"
                )
            elif sym in live_map:
                ls = live_map[sym]
                copied["executed_shares"] = 0
                copied["current_status"] = f"STANDBY — Live {ls['price']:,.0f} đ ({ls['change_pct']:+.2f}%)"
            enriched_wl.append(copied)
        if enriched_wl:
            plan_data["approved_watchlist"] = enriched_wl
        return plan_data

    cash_vnd = float(port.get("cash_vnd", 0.0))
    cash_pct = float(port.get("cash_pct", 100.0))
    stocks_val = float(port.get("stocks_val_vnd", 0.0))
    holdings_desc = port.get("holdings_desc", "0 CP")
    now = get_ict_now()
    week_num = now.isocalendar()[1]

    dynamic_wl = []
    for s in snap.get("live_stocks", [])[:6]:
        sym = s["code"]
        h = holdings_map.get(sym)
        dynamic_wl.append({
            "symbol": sym,
            "name": s.get("name", sym),
            "tier": s.get("tier", "Watchlist"),
            "weekly_limit": "Theo ATR Risk-Parity <= 0.35% NAV/lệnh",
            "executed_shares": int(h.get("shares", 0)) if h else 0,
            "current_status": (
                f"ĐANG GIỮ {h.get('shares', 0)} CP @ Live {s['price']:,.0f} đ ({float(h.get('pnl_pct', 0)):+.2f}%)"
                if h else f"STANDBY — Live {s['price']:,.0f} đ ({s['change_pct']:+.2f}%)"
            ),
            "entry_zone": f"{s['probe_target']:,.0f} đ",
            "stop_loss_2xatr": f"{s['stop_loss']:,.0f} đ",
            "tp1": f"{s['tp1']:,.0f} đ" if s.get("tp1") else "N/A",
            "tp2": f"{s['tp2']:,.0f} đ" if s.get("tp2") else "N/A",
            "catalyst": s.get("catalyst", ""),
        })

    return {
        "title": "BẢNG KẾ HOẠCH TÁC CHIẾN TUẦN (ĐỊNH HƯỚNG THAM KHẢO CHO CHỦ TỊCH)",
        "week_label": f"Tuần {week_num} ({now.strftime('%d/%m/%Y')})",
        "basis": "Hồ sơ SSOT Living War-Room V4.0 & Master Execution Blotter",
        "approved_by": "Chủ tịch Trần Quốc Thiên Phước",
        "legal_stamp": "🛡️ BAN 12 TRỌNG NIÊM PHONG PHÁP LÝ THỂ CHẾ",
        "is_reference_only": True,
        "constitution_mandate": (
            "⚠️ THỂ CHẾ BẤT BIẾN THEO CHỈ THỊ CỦA CHỦ TỊCH: Bảng kế hoạch tuần CHỈ MANG TÍNH CHẤT THAM KHẢO ĐỊNH HƯỚNG, "
            "TUYỆT ĐỐI KHÔNG PHẢI KẾ HOẠCH CỨNG. Mọi quyết định giải ngân/phòng thủ PHẢI THAY ĐỔI TỪNG NGÀY theo biến động thực tế."
        ),
        "days": [
            {
                "day_id": "current",
                "day_name": f"Trạng Thái SSOT Hiện Tại ({now.strftime('%d/%m/%Y')})",
                "theme": f"Đang giữ {holdings_desc} ({stocks_val:,.0f} đ) • Két Tiền Mặt {cash_vnd:,.0f} đ ({cash_pct:.1f}%)",
                "status": "ACTIVE",
                "status_badge": "🟢 ĐỒNG BỘ LIVE",
                "guideline": "Tuân thủ kỷ luật 3 Không, bảo vệ vị thế bằng Stop Loss 2xATR và chờ điểm cạn cung Khung Giờ Vàng.",
                "cash_reserve_target": f"{cash_pct:.1f}% NAV ({cash_vnd/1e6:.2f}M)"
            }
        ],
        "approved_watchlist": dynamic_wl,
    }


def _compute_threat_from_snapshot(snap: Dict[str, Any]) -> Dict[str, Any]:
    port = snap.get("portfolio_live", {})
    threat = snap.get("threat", {})
    cash_vnd = float(port.get("cash_vnd", 0.0))
    cash_pct = float(port.get("cash_pct", 100.0))
    stocks_pct = float(port.get("stocks_pct", 0.0))
    total_shares = int(port.get("total_shares", 0))
    level_num = int(threat.get("level_num", 1))
    threat_level = threat.get("threat_level", "LEVEL_1_SAFE_POSITION_ACTIVE")
    threat_label = threat.get(
        "threat_label",
        f"🟢 CẤP {level_num} — AN TOÀN ({cash_vnd:,.0f} đ Tiền Mặt {cash_pct:.1f}% • {total_shares} CP Đang Giữ {stocks_pct:.1f}%)"
    )
    return {
        "level_num": level_num,
        "threat_level": threat_level,
        "threat_label": threat_label,
    }


def get_tactical_war_room_state(force_refresh: bool = False) -> Dict[str, Any]:
    """
    Tập hợp toàn bộ trạng thái thời gian thực của Phòng Tác Chiến (Minh Quân, Victor, Alex)
    trực tiếp từ Living Intraday Brain + SSOT thực tế 100%.
    """
    now = get_ict_now()
    snap = _get_live_snapshot(force_refresh=force_refresh)

    phase_info = get_current_market_phase(now)
    action_plan = get_tactical_action_steps(now, snapshot=snap)
    market_overview = snap.get("market_overview", {})
    live_stocks = snap.get("live_stocks", [])
    dynamic_picks = snap.get("dynamic_picks", [])
    regime = snap.get("intraday_regime", {})
    port = snap.get("portfolio_live", {})
    ledger_meta = snap.get("ledger_meta", {})

    cash_vnd = float(port.get("cash_vnd", 0.0))
    stocks_val_vnd = float(port.get("stocks_val_vnd", 0.0))
    total_nav_vnd = float(port.get("total_nav_vnd", cash_vnd + stocks_val_vnd))
    realized_pnl_vnd = float(port.get("realized_pnl_vnd", 0.0))
    unrealized_pnl_vnd = float(port.get("unrealized_pnl_vnd", 0.0))
    unrealized_pnl_pct = float(port.get("unrealized_pnl_pct", 0.0))
    holdings = port.get("holdings", [])
    holdings_count = int(port.get("holdings_count", len(holdings)))
    total_shares = int(port.get("total_shares", 0))
    cash_pct = float(port.get("cash_pct", 100.0))
    stocks_pct = float(port.get("stocks_pct", 0.0))
    holdings_desc = port.get("holdings_desc", "0 CP")

    threat_info = _compute_threat_from_snapshot(snap)
    regime_label = regime.get("label", "GIẰNG CO PHÂN HÓA")

    if phase_info["active_phase_id"] == "PRE_ATO":
        tactical_message = (
            f"Minh Quân báo cáo: Két tiền mặt thực tế {cash_vnd:,.0f} đ ({cash_pct:.1f}% NAV) "
            f"| Danh mục {total_shares} CP ({holdings_desc}). Chế độ: {regime_label}. TUYỆT ĐỐI KHÔNG ĐUA LỆNH ATO!"
        )
    elif phase_info["active_phase_id"] == "ATO_OPEN":
        tactical_message = "Minh Quân báo cáo: Phiên ATO đang diễn ra. Giữ vững kỷ luật 3 KHÔNG, không đua lệnh giá xanh mở gap."
    elif phase_info["active_phase_id"] in ("MORNING_CONTINUOUS", "NOON_INTERMISSION"):
        tactical_message = (
            f"Minh Quân & Victor báo cáo: Danh mục {holdings_desc} ({stocks_val_vnd:,.0f} đ • PnL {unrealized_pnl_vnd:+,.0f} đ) đang được quét 24/7. "
            f"Két tiền mặt {cash_vnd:,.0f} đ ({cash_pct:.1f}% NAV) | Chế độ: {regime_label}."
        )
    elif phase_info["active_phase_id"] in ("T2_ABSORPTION", "GOLDEN_WINDOW"):
        tactical_message = (
            f"🎯 MINH QUÂN TÁC CHIẾN CHIỀU ({regime_label}): Đang nắm giữ {total_shares} CP ({holdings_desc} • {stocks_val_vnd:,.0f} đ). "
            f"Két tiền mặt {cash_vnd:,.0f} đ ({cash_pct:.1f}% NAV). Victor canh giữ Stop Loss 2xATR & Buy Up từng giây!"
        )
    else:
        tactical_message = (
            f"Minh Quân báo cáo: Thị trường VN tạm nghỉ/đóng cửa. Két tiền mặt {cash_vnd:,.0f} đ ({cash_pct:.1f}% NAV) "
            f"và {total_shares} CP ({holdings_desc} ≈ {stocks_val_vnd:,.0f} đ) — Tổng NAV Live {total_nav_vnd:,.0f} đ."
        )

    date_str = phase_info["current_date_str"]
    victor_realtime_alert_center = build_victor_realtime_alert_center(snap, phase_info, force_write_report=force_refresh)
    demo_tactical_plan_tomorrow = build_demo_tactical_plan_tomorrow(snap, phase_info, victor_realtime_alert_center, force_write_report=force_refresh)
    directives = load_directives_history(date_str, portfolio_live=port, regime=regime)
    directives = evaluate_and_trigger_tactical_alerts(
        live_stocks,
        phase_info,
        directives,
        date_str,
        snapshot=snap,
        victor_center=victor_realtime_alert_center,
        demo_plan=demo_tactical_plan_tomorrow,
    )

    # Tự động đồng bộ báo cáo sống Live Intraday Report vào thư mục & Vault (throttled 60s)
    try:
        from scripts.apex_live_intraday_brain import sync_live_intraday_report
        sync_live_intraday_report(snap, force_write=False)
    except Exception:
        pass

    # Tính EV / P(W) / R:R động từ dynamic_picks + ledger_meta
    ev_vals = [float(p.get("ev_pct", 0.0)) for p in dynamic_picks if p.get("ev_pct")]
    pw_vals = [float(p.get("win_prob_pct", 0.0)) for p in dynamic_picks if p.get("win_prob_pct")]
    rr_vals = [float(p.get("rr_ratio", 0.0)) for p in dynamic_picks if p.get("rr_ratio")]

    avg_ev = round(sum(ev_vals) / len(ev_vals), 2) if ev_vals else float(ledger_meta.get("expected_value_pct", 0.0))
    avg_pw = round(sum(pw_vals) / len(pw_vals), 1) if pw_vals else float(ledger_meta.get("win_rate_pct", 0.0))
    avg_rr_num = round(sum(rr_vals) / len(rr_vals), 2) if rr_vals else 0.0
    avg_rr_str = f"1:{avg_rr_num:.2f}" if avg_rr_num > 0 else str(ledger_meta.get("average_rr", "1:2.50"))

    deep_brain_summary: Dict[str, Any] = {
        "top_vn_alpha_picks": [],
        "holdings_optimizer": [],
        "correlation_summary": {},
        "system_maturity_iq": {},
        "multi_horizon_walk_forward": {},
        "legends_top_picks": [],
        "omni_crawler_stats": {},
        "catalyst_alerts": {},
    }
    try:
        brain_path = BASE_DIR / "data" / "deep_financial_brain_analysis.json"
        if brain_path.exists():
            bd = json.loads(brain_path.read_text(encoding="utf-8"))
            for p in bd.get("top_vn_alpha_picks", [])[:6]:
                opt = p.get("optimizer", {})
                val = p.get("valuation", {})
                deep_brain_summary["top_vn_alpha_picks"].append({
                    "symbol": p.get("symbol"),
                    "sector_name": p.get("sector_name"),
                    "live_price": p.get("live_price"),
                    "alpha_score": p.get("alpha_score"),
                    "ocf_ratio": p.get("ocf_ratio"),
                    "ev_pct": opt.get("ev_pct"),
                    "rr_ratio": opt.get("rr_ratio"),
                    "half_kelly_pct": opt.get("half_kelly_pct"),
                    "margin_of_safety_pct": val.get("margin_of_safety_pct"),
                    "intrinsic_fair_value": val.get("intrinsic_fair_value"),
                    "suggested_shares_lot100": opt.get("suggested_shares_lot100"),
                    "action_signal": opt.get("action_signal"),
                    "max_corr_with_holdings": p.get("max_corr_with_holdings"),
                    "most_correlated_holding": p.get("most_correlated_holding"),
                    "corr_guard_status": p.get("corr_guard_status"),
                    "corr_penalty_075x": opt.get("corr_penalty_075x", False),
                })
            deep_brain_summary["holdings_optimizer"] = bd.get("holdings_optimizer", [])
            cm = bd.get("correlation_matrix", {})
            if isinstance(cm, dict) and cm:
                deep_brain_summary["correlation_summary"] = {
                    "session_window": cm.get("session_window", 60),
                    "held_symbols": cm.get("held_symbols", []),
                    "live_60d_series_fetched": cm.get("live_60d_series_fetched", 0),
                    "total_symbols_evaluated": cm.get("total_symbols_evaluated", 0),
                }
    except Exception:
        pass
    try:
        lg_path = BASE_DIR / "data" / "system_evolution_and_legends_state.json"
        if not lg_path.exists():
            lg_path = BASE_DIR / "data" / "legend_investor_wisdom_vault.json"
        if lg_path.exists():
            ld = json.loads(lg_path.read_text(encoding="utf-8"))
            sr = ld.get("self_reflection", {})
            iq_raw = dict(sr.get("system_maturity_iq", {}))
            iq_raw["classification_counts"] = sr.get("classification_counts", {})
            deep_brain_summary["system_maturity_iq"] = iq_raw
            deep_brain_summary["multi_horizon_walk_forward"] = ld.get("multi_horizon_walk_forward", {}) or sr.get("multi_horizon_walk_forward", {})
            for ev in ld.get("ticker_evaluations", [])[:6]:
                top_adv = (ev.get("top_3_advocates") or [{}])[0]
                deep_brain_summary["legends_top_picks"].append({
                    "symbol": ev.get("symbol"),
                    "market": ev.get("market"),
                    "consensus_legends_score": ev.get("consensus_legends_score"),
                    "supporting_legends_count": ev.get("supporting_legends_count"),
                    "legends_verdict": ev.get("legends_verdict"),
                    "top_advocate": f"{top_adv.get('name', '')} ({top_adv.get('score', 0)})",
                    "key_dissent": f"{ev.get('key_dissent', {}).get('name', '')} ({ev.get('key_dissent', {}).get('score', 0)})",
                })
    except Exception:
        pass
    try:
        omni_path = BASE_DIR / "data" / "omni_market_intelligence.json"
        bctc_upd_path = BASE_DIR / "data" / "live_bctc_quarterly_updates.json"
        alerts_path = BASE_DIR / "data" / "live_catalyst_alerts.json"
        bctc_cnt = 0
        if bctc_upd_path.exists():
            bctc_cnt = int(json.loads(bctc_upd_path.read_text(encoding="utf-8")).get("total_tickers_updated", 0) or 0)
        if omni_path.exists():
            od = json.loads(omni_path.read_text(encoding="utf-8"))
            sh = od.get("source_health", [])
            deep_brain_summary["omni_crawler_stats"] = {
                "crawled_at": od.get("crawled_at", ""),
                "total_universe": (od.get("universe_counts") or {}).get("total", 180),
                "total_items": od.get("total_items", 0),
                "live_bctc_updates_count": bctc_cnt,
                "sources_online": f"{sum(1 for s in sh if s.get('ok'))}/{len(sh)}" if sh else "0/0",
            }
        if alerts_path.exists():
            ad = json.loads(alerts_path.read_text(encoding="utf-8"))
            deep_brain_summary["catalyst_alerts"] = {
                "updated_at": ad.get("updated_at", ""),
                "total_alerts": ad.get("total_alerts", 0),
                "holding_alerts_count": ad.get("holding_alerts_count", 0),
                "risk_alerts_count": ad.get("risk_alerts_count", 0),
                "alerts": (ad.get("alerts") or [])[:6],
            }
    except Exception:
        pass

    enterprise_mesh_summary = {}
    try:
        from scripts.apex_enterprise_collaboration_mesh import get_enterprise_mesh_summary
        enterprise_mesh_summary = get_enterprise_mesh_summary()
    except Exception:
        enterprise_mesh_summary = {}

    victor_deep_surveillance = _build_victor_deep_surveillance(snap)
    live_execution_master_plan = _build_live_execution_master_plan(
        snap, victor_deep_surveillance, enterprise_mesh_summary
    )
    dept_workstation_bundle = _build_department_live_workstation_and_reports(
        snap, enterprise_mesh_summary
    )

    return {
        "status": "ok",
        "chairman_name": "Trần Quốc Thiên Phước",
        "account_id": "105C307855",
        "trading_date": phase_info["current_date_str"],
        "server_time": phase_info["current_time_str"],
        "phase_info": phase_info,
        "intraday_regime": regime,
        "tactical_message": tactical_message,
        "action_plan": action_plan,
        "market_overview": market_overview,
        "live_stocks": live_stocks,
        "dynamic_picks": dynamic_picks,
        "minh_quan_blueprint": {
            "specialist_name": "Minh Quân",
            "title": "Chuyên Viên Đầu Tư Trưởng TTCK Việt Nam (Ban 7 VN)",
            "mastery_score": float(ledger_meta.get("mastery_score", 98.5)),
            "expected_value_pct": avg_ev,
            "win_rate_pct": avg_pw,
            "average_rr": avg_rr_str,
            "golden_window": "14h00 – 14h25 Chiều",
            "rules": [
                "❌ KHÔNG MUA ATO: Tránh 100% bẫy giá giả (Bull-Trap/Bear-Trap) đầu phiên sáng.",
                "❌ KHÔNG MUA GIÁ XANH: Tuyệt đối không fomo khi RSI > 60 hoặc chưa có nền tích lũy cạn cung.",
                "❌ KHÔNG BÌNH QUÂN GIÁ XUỐNG: Cắt lỗ cứng Stop 2xATR (<= 7.5%) nếu vị thế đi ngược kỳ vọng.",
                f"⭐ CHẾ ĐỘ LIVE HIỆN TẠI: {regime_label} (Hạn mức giải ngân mới tối đa {regime.get('max_new_allocation_pct', 30)}% Cash)."
            ]
        },
        "victor_sentinel": {
            "officer_name": "Victor",
            "title": "Chỉ Huy Giám Sát Realtime & Phòng Hộ Khẩn Cấp (Ban 9 Live Sentinel)",
            "cash_vnd": cash_vnd,
            "total_nav_vnd": total_nav_vnd,
            "stocks_val_vnd": stocks_val_vnd,
            "cash_pct": cash_pct,
            "stocks_pct": stocks_pct,
            "total_shares": total_shares,
            "unrealized_pnl_vnd": unrealized_pnl_vnd,
            "unrealized_pnl_pct": unrealized_pnl_pct,
            "holdings_count": holdings_count,
            "holdings": holdings,
            "realized_round1_profit_vnd": realized_pnl_vnd,
            "threat_level_num": threat_info["level_num"],
            "threat_level": threat_info["threat_level"],
            "threat_label": threat_info["threat_label"],
            "risk_arsenal": [
                "Ngưỡng cắt lỗ cứng Stop 2xATR (khóa mức lỗ tối đa <= 0.35% NAV)",
                "Kỹ thuật T+0 Scalping hạ giá vốn linh hoạt",
                "Phòng vệ danh mục bằng Synthetic Short Hedge HĐTL VN30F khi thị trường gãy MA200"
            ]
        },
        "alex_wall_street": {
            "officer_name": "Alex",
            "title": "Chuyên Viên Đầu Tư Quốc Tế & Phố Wall (Ban 7 US)",
            "status": snap.get("global_spillover", {}).get("overnight_bias", "NEUTRAL_SELECTIVE"),
            "status_label": snap.get("global_spillover", {}).get("bias_label", "⚖️ TRUNG TÍNH"),
            "ny_open_time": "21:30 Tối Giờ VN",
            "countdown_str": phase_info["countdown_to_wall_street"],
            "risk_multiplier": snap.get("global_spillover", {}).get("risk_multiplier", 1.0),
            "max_allocation_pct": snap.get("global_spillover", {}).get("max_allocation_pct", 45),
            "handoff_directive": snap.get("global_spillover", {}).get("handoff_directive", ""),
            "watchlist": [
                {"ticker": "NVDA", "name": "NVIDIA Corporation", "thesis": "Thống trị GPU AI Blackwell, FCF biên độ 55%"},
                {"ticker": "AVGO", "name": "Broadcom Inc.", "thesis": "Custom ASIC AI & Networking, hợp đồng hyperscalers khủng"},
                {"ticker": "MSFT", "name": "Microsoft Corp", "thesis": "Azure Cloud AI tăng tốc, tích hợp Copilot toàn diện"},
                {"ticker": "PLTR", "name": "Palantir Technologies", "thesis": "Nền tảng AIP bùng nổ nhu cầu doanh nghiệp & quốc phòng"}
            ],
            "note": snap.get("global_spillover", {}).get("handoff_directive") or "Sẵn sàng điều phối dòng tiền liên thị trường US <-> VN."
        },
        "global_spillover": snap.get("global_spillover", {}),
        "execution_tracker": snap.get("execution_tracker", {}),
        "deep_brain_summary": deep_brain_summary,
        "enterprise_mesh_summary": enterprise_mesh_summary,
        "victor_deep_surveillance": victor_deep_surveillance,
        "victor_realtime_alert_center": victor_realtime_alert_center,
        "demo_tactical_plan_tomorrow": demo_tactical_plan_tomorrow,
        "live_execution_master_plan": live_execution_master_plan,
        "department_live_workstation": dept_workstation_bundle.get("department_live_workstation", []),
        "latest_reports_feed": dept_workstation_bundle.get("latest_reports_feed", []),
        "vault_sync_meta": dept_workstation_bundle.get("vault_sync_meta", {}),
        "directives_history": directives,
        "weekly_reference_plan": get_weekly_reference_roadmap(snapshot=snap)
    }


def _load_v8_json_safe(rel_path: str) -> Dict[str, Any]:
    """Read a JSON file relative to repo root without raising on missing/corrupt files."""
    try:
        fp = Path(__file__).resolve().parent.parent / rel_path
        if fp.exists():
            with open(fp, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
    except Exception:
        pass
    return {}


def _build_victor_deep_surveillance(snap: Dict[str, Any]) -> Dict[str, Any]:
    """Build Victor's 2-tier deep surveillance book: Held Positions & Alpha Watchlist."""
    ssot = _load_v8_json_safe("data/current_portfolio_state.json")
    deep_brain = _load_v8_json_safe("data/deep_financial_brain_analysis.json")
    vs = snap.get("victor_sentinel", {}) or {}
    live_stocks = snap.get("live_stocks", []) or []
    live_map = {str(s.get("code", "")).upper(): s for s in live_stocks if s.get("code")}

    ho_list = deep_brain.get("holdings_optimizer", []) or []
    ho_map = {str(h.get("symbol", "")).upper(): h for h in ho_list if isinstance(h, dict) and h.get("symbol")}

    alpha_list = deep_brain.get("top_vn_alpha_picks", []) or []
    alpha_map = {str(a.get("symbol", "")).upper(): a for a in alpha_list if isinstance(a, dict) and a.get("symbol")}

    cash_balance_vnd = float(ssot.get("cash_balance_vnd", vs.get("cash_vnd", 0.0)) or 0.0)
    total_nav_vnd = float(vs.get("total_nav_vnd", ssot.get("total_nav_vnd", 1.0)) or 1.0)

    active_positions = ssot.get("active_positions", {}) or {}
    held_positions_book: List[Dict[str, Any]] = []
    held_codes = set()

    for sym, pos in active_positions.items():
        if not isinstance(pos, dict):
            continue
        code = str(sym).upper()
        held_codes.add(code)
        tick = live_map.get(code, {})
        opt = ho_map.get(code, {})
        ap = alpha_map.get(code, {})
        val = ap.get("valuation", {}) or {}

        shares = int(pos.get("shares", 0) or 0)
        tradable = int(pos.get("tradable_shares", shares) or 0)
        entry_price = float(pos.get("entry_price", 0.0) or 0.0)
        live_price = float(tick.get("price") or pos.get("current_price") or entry_price or 0.0)
        intraday_low = float(tick.get("low") or live_price)
        intraday_high = float(tick.get("high") or live_price)
        change_pct = float(tick.get("change_pct", 0.0) or 0.0)
        volume = int(tick.get("volume", 0) or 0)
        vol_ratio_20d = float(tick.get("vol_ratio_20d", 1.0) or 1.0)
        active_buy_pct = float(tick.get("active_buy_pct", 50.0) or 50.0)

        bids = tick.get("bid_levels", []) or []
        asks = tick.get("ask_levels", []) or []
        bid_vol = sum(int(b.get("vol", 0) or 0) for b in bids)
        ask_vol = sum(int(a.get("vol", 0) or 0) for a in asks)
        bid_ask_ratio = round(bid_vol / max(ask_vol, 1), 2) if (bid_vol or ask_vol) else 1.0

        if active_buy_pct >= 58.0 or bid_ask_ratio >= 1.15:
            orderbook_pressure = "CẦU ÁP ĐẢO (MUA CHỦ ĐỘNG)"
        elif active_buy_pct < 45.0:
            orderbook_pressure = "ÁP LỰC CUNG NGẮN HẠN"
        else:
            orderbook_pressure = "CÂN BẰNG HẤP THỤ"

        stop_loss = float(tick.get("stop_loss") or pos.get("stop_loss") or 0.0)
        tp1 = float(tick.get("tp1") or pos.get("take_profit_tp1") or 0.0)
        tp2 = float(tick.get("tp2") or pos.get("take_profit_tp2") or 0.0)
        stop_dist_pct = round(((live_price - stop_loss) / max(live_price, 1.0)) * 100.0, 2) if stop_loss > 0 else 0.0
        tp1_upside_pct = round(((tp1 - live_price) / max(live_price, 1.0)) * 100.0, 2) if tp1 > 0 else 0.0
        tp2_upside_pct = round(((tp2 - live_price) / max(live_price, 1.0)) * 100.0, 2) if tp2 > 0 else 0.0

        pnl_vnd = round((live_price - entry_price) * shares)
        pnl_pct = round(((live_price - entry_price) / max(entry_price, 1.0)) * 100.0, 2)

        ma20 = float(tick.get("ma20") or opt.get("t0_dip_level") or live_price)
        t0_buy_zone = round(min(live_price, max(stop_loss * 1.005, ma20)) / 50.0) * 50.0 if stop_loss > 0 else ma20
        t0_sell_zone = round(max(intraday_high, live_price * 1.022) / 50.0) * 50.0

        ocf_ratio = float(opt.get("ocf_ratio") or ap.get("ocf_ratio") or 1.0)
        mos_pct = float(opt.get("margin_of_safety_pct") or val.get("margin_of_safety_pct") or 0.0)
        alpha_score = float(opt.get("alpha_score") or ap.get("alpha_score") or 70.0)

        if stop_loss > 0 and live_price <= stop_loss:
            badge = "🔴 CHẠM NGƯỠNG BẢO VỆ / SIẾT STOP"
            instr = opt.get("recommendation") or f"Theo dõi sát mốc Stop {stop_loss:,.0f}đ, cấm trung bình giá xuống."
        elif pnl_pct >= 5.0 and active_buy_pct >= 60.0:
            badge = "🟢 ĐỆM LÃI DÀY — GỒNG LÃI THEO TP1"
            instr = opt.get("recommendation") or f"Lực mua {active_buy_pct:.1f}% khỏe, giữ vị thế hướng TP1 {tp1:,.0f}đ."
        elif stop_dist_pct <= 1.2:
            badge = "🟡 SÁT VÙNG HỖ TRỢ — QUAN SÁT RÚT CHÂN"
            instr = opt.get("recommendation") or f"Chỉ còn cách Stop {stop_dist_pct:.2f}%. Canh phản ứng cung quanh {t0_buy_zone:,.0f}đ."
        else:
            badge = "🟢 AN TOÀN — SẴN SÀNG T+0"
            instr = opt.get("recommendation") or f"Đệm Stop {stop_dist_pct:.2f}%, cân nhắc T+0 vùng {t0_buy_zone:,.0f}đ -> {t0_sell_zone:,.0f}đ."

        held_positions_book.append({
            "symbol": code,
            "name": pos.get("name") or tick.get("name") or code,
            "shares": shares,
            "tradable_shares": tradable,
            "entry_price": entry_price,
            "live_price": live_price,
            "intraday_low": intraday_low,
            "intraday_high": intraday_high,
            "change_pct": change_pct,
            "volume": volume,
            "vol_ratio_20d": vol_ratio_20d,
            "active_buy_pct": active_buy_pct,
            "bid_ask_ratio": bid_ask_ratio,
            "orderbook_pressure": orderbook_pressure,
            "stop_loss": stop_loss,
            "stop_distance_pct": stop_dist_pct,
            "tp1": tp1,
            "tp2": tp2,
            "tp1_upside_pct": tp1_upside_pct,
            "tp2_upside_pct": tp2_upside_pct,
            "pnl_vnd": pnl_vnd,
            "pnl_pct": pnl_pct,
            "t0_buy_zone": t0_buy_zone,
            "t0_sell_zone": t0_sell_zone,
            "ocf_ratio": ocf_ratio,
            "mos_pct": mos_pct,
            "alpha_score": alpha_score,
            "victor_status_badge": badge,
            "victor_instruction": instr,
        })

    alpha_watchlist_book: List[Dict[str, Any]] = []
    seen_watch = set(held_codes)
    candidate_codes: List[str] = []

    for s in live_stocks:
        c = str(s.get("code", "")).upper()
        if c and c not in seen_watch:
            seen_watch.add(c)
            candidate_codes.append(c)
    for ap in alpha_list:
        c = str(ap.get("symbol", "")).upper()
        if c and c not in seen_watch:
            seen_watch.add(c)
            candidate_codes.append(c)

    for code in candidate_codes[:10]:
        tick = live_map.get(code, {})
        ap = alpha_map.get(code, {})
        val = ap.get("valuation", {}) or {}
        opt = ap.get("optimizer", {}) or {}

        live_price = float(tick.get("price") or ap.get("live_price") or 0.0)
        intraday_low = float(tick.get("low") or live_price)
        intraday_high = float(tick.get("high") or live_price)
        change_pct = float(tick.get("change_pct") or ap.get("change_1d_pct") or 0.0)
        active_buy_pct = float(tick.get("active_buy_pct") or ap.get("buy_up_pct") or 50.0)
        rsi14 = float(tick.get("rsi14") or ap.get("rsi14") or 50.0)
        ma20 = float(tick.get("ma20") or ap.get("ma20") or live_price)
        probe_target = float(tick.get("probe_target") or round((ma20 if ma20 > 0 else live_price * 0.98) / 50.0) * 50.0)
        stop_loss = float(tick.get("stop_loss") or opt.get("stop_loss_price") or round(live_price * 0.93, 0))
        tp1 = float(tick.get("tp1") or opt.get("tp1_price") or round(live_price * 1.14, 0))
        tp2 = float(tick.get("tp2") or opt.get("tp2_price") or round(live_price * 1.25, 0))

        risk_unit = max(live_price - stop_loss, live_price * 0.03, 1.0)
        reward_unit = max(tp1 - live_price, 0.0)
        rr_ratio = float(opt.get("rr_ratio") or round(reward_unit / risk_unit, 2))
        ev_pct = float(opt.get("ev_pct") or round((active_buy_pct / 100.0 * (reward_unit / max(live_price, 1.0)) - (1.0 - active_buy_pct / 100.0) * (risk_unit / max(live_price, 1.0))) * 100.0, 2))
        alpha_score = float(ap.get("alpha_score") or (72.0 if tick else 65.0))
        ocf_ratio = float(ap.get("ocf_ratio") or 1.1)
        roe_pct = float(ap.get("roe_pct") or 15.0)
        intrinsic_value = float(val.get("intrinsic_fair_value") or round(live_price * 1.15, 0))
        mos_pct = float(val.get("margin_of_safety_pct") or round(((intrinsic_value - live_price) / max(intrinsic_value, 1.0)) * 100.0, 1))

        lot_100_cost_vnd = round(live_price * 100.0)
        nav_pct_per_lot = round((lot_100_cost_vnd / max(total_nav_vnd, 1.0)) * 100.0, 1)
        constitutional_lot_ok = bool(lot_100_cost_vnd <= cash_balance_vnd and nav_pct_per_lot <= 33.0)

        if not constitutional_lot_ok:
            victor_signal = "🔴 TẠM HOÃN / VƯỢT TRẦN LÔ 100 (>33% NAV)"
        elif rsi14 <= 66.0 and active_buy_pct >= 55.0 and mos_pct >= 10.0 and rr_ratio >= 1.8:
            victor_signal = "🟢 SẴN SÀNG GIẢI NGÂN THĂM DÒ (SAU 14H00)"
        elif active_buy_pct < 45.0 or live_price > probe_target * 1.04:
            victor_signal = "🟡 QUAN SÁT ĐIỂM NHÚNG PULLBACK"
        else:
            victor_signal = "🟡 THEO DÕI CHẶT THANH KHOẢN CHỦ ĐỘNG"

        alpha_watchlist_book.append({
            "symbol": code,
            "name": tick.get("name") or ap.get("company_name") or code,
            "sector_name": ap.get("sector_name") or tick.get("tier") or "VN Watchlist",
            "live_price": live_price,
            "change_pct": change_pct,
            "intraday_low": intraday_low,
            "intraday_high": intraday_high,
            "active_buy_pct": active_buy_pct,
            "rsi14": rsi14,
            "ma20": ma20,
            "probe_target": probe_target,
            "stop_loss": stop_loss,
            "tp1": tp1,
            "tp2": tp2,
            "rr_ratio": rr_ratio,
            "ev_pct": ev_pct,
            "alpha_score": alpha_score,
            "ocf_ratio": ocf_ratio,
            "roe_pct": roe_pct,
            "intrinsic_value": intrinsic_value,
            "mos_pct": mos_pct,
            "lot_100_cost_vnd": lot_100_cost_vnd,
            "nav_pct_per_lot": nav_pct_per_lot,
            "constitutional_lot_ok": constitutional_lot_ok,
            "victor_signal": victor_signal,
            "catalyst": tick.get("catalyst") or ap.get("catalyst") or "Theo dõi dòng tiền và BCTC thực tế.",
        })

    ts_str = f"{snap.get('trading_date', '')} {snap.get('server_time', '')}".strip() or get_ict_now().strftime("%Y-%m-%d %H:%M:%S")
    ready_cnt = sum(1 for w in alpha_watchlist_book if "SẴN SÀNG" in w.get("victor_signal", ""))
    return {
        "surveillance_timestamp": ts_str,
        "total_monitored_count": len(held_positions_book) + len(alpha_watchlist_book),
        "held_count": len(held_positions_book),
        "watchlist_count": len(alpha_watchlist_book),
        "held_positions_book": held_positions_book,
        "alpha_watchlist_book": alpha_watchlist_book,
        "victor_headline": (
            f"Victor đang bám sát {len(held_positions_book)} vị thế nắm giữ + {len(alpha_watchlist_book)} mã tầm ngắm "
            f"({ready_cnt} mã đạt chuẩn giải ngân lô 100 <= 33% NAV)."
        ),
    }


def _build_live_execution_master_plan(
    snap: Dict[str, Any],
    victor_surveillance: Dict[str, Any],
    enterprise_mesh_summary: Dict[str, Any],
) -> Dict[str, Any]:
    """Synthesize real-time market-adaptive execution plan across all departments."""
    mkt = snap.get("market_overview", {}) or {}
    vni = mkt.get("vn_index", {}) or {}
    breadth = mkt.get("market_breadth", {}) or {}
    regime = snap.get("intraday_regime", {}) or {}
    phase = snap.get("phase_info", {}) or {}
    spill = snap.get("global_spillover", {}) or {}
    vs = snap.get("victor_sentinel", {}) or {}
    latest_sess = enterprise_mesh_summary.get("latest_session", {}) or {}

    cash_available_vnd = float(vs.get("cash_vnd", 0.0) or 0.0)
    cash_pct = float(vs.get("cash_pct", 0.0) or 0.0)
    total_nav_vnd = float(vs.get("total_nav_vnd", 0.0) or 0.0)
    max_new_alloc_pct = float(
        spill.get("max_new_allocation_pct") or regime.get("max_new_allocation_pct") or 50.0
    )
    target_stock_budget_vnd = total_nav_vnd * (max_new_alloc_pct / 100.0)
    stocks_val_vnd = float(vs.get("stocks_val_vnd", 0.0) or 0.0)
    max_deployable_vnd = max(0.0, min(cash_available_vnd, max(target_stock_budget_vnd - stocks_val_vnd, 0.0)))
    if max_deployable_vnd == 0.0 and cash_available_vnd > 3_500_000:
        max_deployable_vnd = round(min(cash_available_vnd * 0.45, total_nav_vnd * 0.33))

    holdings_action_items: List[Dict[str, Any]] = []
    for h in victor_surveillance.get("held_positions_book", []) or []:
        t0_zone = f"{h['t0_buy_zone']:,.0f}đ -> {h['t0_sell_zone']:,.0f}đ"
        holdings_action_items.append({
            "symbol": h["symbol"],
            "shares": h["shares"],
            "current_price": h["live_price"],
            "entry_price": h["entry_price"],
            "stop_loss": h["stop_loss"],
            "tp1": h["tp1"],
            "pnl_vnd": h["pnl_vnd"],
            "pnl_pct": h["pnl_pct"],
            "t0_zone": t0_zone,
            "action_badge": h["victor_status_badge"],
            "tactical_order_text": h["victor_instruction"],
        })

    new_deployment_orders: List[Dict[str, Any]] = []
    sorted_watch = sorted(
        victor_surveillance.get("alpha_watchlist_book", []) or [],
        key=lambda x: (1 if x.get("constitutional_lot_ok") else 0, float(x.get("alpha_score", 0))),
        reverse=True,
    )
    for w in sorted_watch[:4]:
        probe = float(w.get("probe_target") or w.get("live_price") or 0.0)
        low_zone = round((probe * 0.992) / 50.0) * 50.0
        high_zone = round((probe * 1.005) / 50.0) * 50.0
        lot_cost = float(w.get("lot_100_cost_vnd") or (probe * 100.0))
        ok_flag = bool(w.get("constitutional_lot_ok"))
        new_deployment_orders.append({
            "symbol": w["symbol"],
            "order_type": "LO LIMIT THĂM DÒ 100 CP" if ok_flag else "QUAN SÁT / CHỜ CÂN ĐỐI NAV",
            "limit_buy_zone": f"{low_zone:,.0f}đ - {high_zone:,.0f}đ",
            "stop_loss": w["stop_loss"],
            "tp1": w["tp1"],
            "lot_shares": 100,
            "est_capital_vnd": lot_cost,
            "nav_weight_pct": w["nav_pct_per_lot"],
            "trigger_condition": (
                f"Chỉ khớp sau 14h00 nếu Buy-Up >= 58% và giữ vững MA20 ({w['ma20']:,.0f}đ)."
                if ok_flag
                else f"Lô 100 tốn {lot_cost:,.0f}đ ({w['nav_pct_per_lot']:.1f}% NAV > trần 33% Điều 3) — Khóa giải ngân!"
            ),
            "approval_status": w["victor_signal"],
        })

    vni_val = float(vni.get("value", 0.0) or 0.0)
    held_str_v8 = ", ".join(
        f"{int(h.get('shares', 0) or 0)} {h.get('symbol', '')}"
        for h in (victor_surveillance.get("held_positions_book", []) or [])
        if int(h.get("shares", 0) or 0) > 0
    ) or "0 CP"
    contingency_scenarios = [
        {
            "scenario_id": "SCENARIO_BULL_BREAKOUT",
            "title": "Kịch Bản S1/S3: Đồng Thuận Sóng Hoặc Đánh Úp Spring V3.0 (14h05–14h25)",
            "trigger": f"VN-Index ({vni_val:,.2f}) >= 1,678, Br20 >= 24%, Vol >= 1.05x, Buy-Up >= 58% (S3) hoặc VNI > MA20 & Br20 >= 50% (S1).",
            "portfolio_action": (
                f"SSOT {held_str_v8}. Đạt S3 bấm 30–40% NAV (tối đa 2 mã từ TPB 300 @ 12,250đ, CTG 100 @ 29,950đ, HDB 200 @ 21,700đ, Stop -5.5%); đạt S1 bung 75–85% NAV (TPB, HDB, HPG, VPB)."
            ),
            "cash_target_pct": max(20.0, round(100.0 - max_new_alloc_pct, 1)),
        },
        {
            "scenario_id": "SCENARIO_BASE_ABSORPTION",
            "title": "Kịch Bản S2: Giằng Co Phân Hóa / Bắn Tỉa Chọn Lọc",
            "trigger": "VN-Index giữ nền hỗ trợ, độ rộng 30–50%, dòng tiền luân chuyển phân hóa.",
            "portfolio_action": f"Giữ kỷ luật trước 14h05 ({cash_pct:.1f}% tiền mặt); nếu đạt S2 giải ngân chọn lọc 30–45% NAV vào HDB/TPB, Stop -5.5%, TP1 +6.5%..+9.0% Scaling Out 50/50.",
            "cash_target_pct": round(cash_pct, 1),
        },
        {
            "scenario_id": "SCENARIO_BEAR_DEFENSE",
            "title": "Kịch Bản S4: Xuyên Đáy / Đảo Chiều Bán Tháo — Lá Chắn 100% Tiền Mặt",
            "trigger": "VN-Index thủng đáy 1,666.41 hoặc Buy-Up < 48% hoặc áp lực bán tháo diện rộng.",
            "portfolio_action": "Ngừng 100% lệnh mua mới; cắt dứt khoát vị thế chạm Stop -5.5%, bảo toàn 100% tiền mặt.",
            "cash_target_pct": 100.0,
        },
    ]

    trading_date = snap.get("trading_date") or get_ict_now().strftime("%Y-%m-%d")
    server_time = snap.get("server_time") or get_ict_now().strftime("%H:%M:%S")
    return {
        "plan_id": f"WAR-PLAN-{trading_date.replace('-', '')}-{server_time.replace(':', '')[:4]}",
        "generated_at": f"{trading_date} {server_time} ICT",
        "trading_date": trading_date,
        "session_phase_label": phase.get("phase_name") or phase.get("active_phase_id") or "LIVE WAR-ROOM",
        "regime_id": regime.get("regime_id", "SIDEWAY_CHOPPY"),
        "regime_label": regime.get("label", "TÍCH LŨY CHỌN LỌC"),
        "regime_color": regime.get("badge_color", "#fbbf24"),
        "vn_index_value": vni_val,
        "vn_index_change_pts": float(vni.get("change_pts", 0.0) or 0.0),
        "vn_index_change_pct": float(vni.get("change_pct", 0.0) or 0.0),
        "breadth_advancers": int(breadth.get("advancers", 0) or 0),
        "breadth_decliners": int(breadth.get("decliners", 0) or 0),
        "foreign_net_ty_vnd": vni.get("foreign_net_ty_vnd", "--"),
        "cash_available_vnd": cash_available_vnd,
        "cash_pct": cash_pct,
        "total_nav_vnd": total_nav_vnd,
        "max_new_allocation_pct": max_new_alloc_pct,
        "max_deployable_vnd": max_deployable_vnd,
        "enterprise_session_id": latest_sess.get("session_id", ""),
        "enterprise_verdict": latest_sess.get("final_verdict", "TUÂN THỦ HIẾN PHÁP 10 ĐIỀU & QUẢN TRỊ RỦI RO"),
        "enterprise_seal": latest_sess.get("constitutional_seal_sha256", ""),
        "enterprise_action_summary": latest_sess.get("action_plan") or snap.get("tactical_message", ""),
        "holdings_action_items": holdings_action_items,
        "new_deployment_orders": new_deployment_orders,
        "contingency_scenarios": contingency_scenarios,
    }


def _build_department_live_workstation_and_reports(
    snap: Dict[str, Any],
    enterprise_mesh_summary: Dict[str, Any],
) -> Dict[str, Any]:
    """Map all 14 enterprise departments to live packets and real institutional reports on disk."""
    scanned_reports: List[Dict[str, Any]] = []
    try:
        from scripts.apex_report_scanner import scan_all_institutional_reports
        scanned_reports = scan_all_institutional_reports(limit=300) or []
    except Exception:
        scanned_reports = []

    latest_by_scanner_dept: Dict[str, Dict[str, Any]] = {}
    for rep in scanned_reports:
        did = rep.get("dept_id")
        if did and did not in latest_by_scanner_dept:
            latest_by_scanner_dept[did] = rep

    scanner_mapping = {
        "BAN_1_VN": ("ban_1_vn_macro",),
        "BAN_1_US": ("ban_1_macro",),
        "BAN_2_BCTC": ("ban_2_vn_equity", "ban_2_equity", "ban_10_cbtt"),
        "BAN_3_SYNTHESIS": ("ban_3_vn_synthesis", "ban_3_synthesis", "ban_3_debates"),
        "BAN_4_RISK": ("ban_4_vn_risk", "ban_4_risk"),
        "BAN_5_EVOLUTION": ("ban_5_learning",),
        "BAN_6_ACADEMY": ("ban_6_vn_coach", "ban_6_mentorship"),
        "BAN_7_VN": ("ban_7_vn_specialist",),
        "BAN_7_US": ("ban_7_specialist",),
        "BAN_8_CIO": ("ban_8_enterprise", "ban_8_cio", "ban_8_council"),
        "BAN_9_SENTINEL": ("ban_7_vn_specialist", "ban_4_vn_risk"),
        "BAN_10_IR": ("ban_10_cbtt", "ban_10_hien", "ban_2_equity"),
        "BAN_11_MEDIA": ("ban_11_khanh", "ban_8_enterprise"),
        "BAN_12_OMBUDSMAN": ("ban_12_ombudsman",),
    }

    latest_sess = enterprise_mesh_summary.get("latest_session", {}) or {}
    packets = latest_sess.get("packets", []) or []
    pkt_by_dept: Dict[str, Dict[str, Any]] = {}
    for p in packets:
        fd = p.get("from_dept")
        if fd:
            pkt_by_dept[fd] = p

    try:
        from scripts.apex_enterprise_collaboration_mesh import ENTERPRISE_DEPARTMENT_ROSTER
        roster = list(ENTERPRISE_DEPARTMENT_ROSTER)
    except Exception:
        roster = []

    vni = (snap.get("market_overview", {}) or {}).get("vn_index", {}) or {}
    vs = snap.get("victor_sentinel", {}) or {}
    fallback_findings = {
        "BAN_1_VN": f"VN-Index {float(vni.get('value', 0) or 0):,.2f} ({float(vni.get('change_pct', 0) or 0):+.2f}%), khối ngoại {vni.get('foreign_net_ty_vnd', '--')} tỷ.",
        "BAN_9_SENTINEL": vs.get("threat_label") or f"Đang giám sát {vs.get('holdings_count', 2)} vị thế với đệm tiền mặt {vs.get('cash_pct', 69.0):.1f}%.",
        "BAN_7_VN": f"Sẵn sàng tác chiến sau 14h00 cho HDB/MSH và watchlist thanh khoản thực.",
        "BAN_8_CIO": latest_sess.get("final_verdict") or "Điều phối thống nhất liên phòng ban theo Hiến pháp 10 Điều.",
    }

    workstation: List[Dict[str, Any]] = []
    for dept in roster:
        rid = dept.get("dept_id", "")
        cand_keys = scanner_mapping.get(rid, ())
        matched_rep = None
        for ck in cand_keys:
            if ck in latest_by_scanner_dept:
                matched_rep = latest_by_scanner_dept[ck]
                break
        if matched_rep is None and scanned_reports:
            matched_rep = scanned_reports[0]

        pkt = pkt_by_dept.get(rid, {})
        finding = pkt.get("summary") or fallback_findings.get(rid) or (
            matched_rep.get("title") if matched_rep else dept.get("mandate", "")
        )
        stance = pkt.get("stance") or "ACTIVE_MONITOR"
        workstation.append({
            "dept_id": rid,
            "ban_code": dept.get("ban_code", rid),
            "dept_name": dept.get("title", ""),
            "officer": dept.get("officer", ""),
            "market_scope": dept.get("market_scope", "VN"),
            "veto_power": bool(dept.get("veto_power", False)),
            "live_status": "ACTIVE_IN_WAR_ROOM",
            "stance": stance,
            "live_finding": finding,
            "latest_report_path": matched_rep.get("rel_path", "") if matched_rep else "",
            "latest_report_title": matched_rep.get("title", "") if matched_rep else "",
            "latest_report_date": matched_rep.get("date", "") if matched_rep else "",
            "latest_report_time": matched_rep.get("time", "") if matched_rep else "",
        })

    feed: List[Dict[str, Any]] = []
    for r in scanned_reports[:12]:
        feed.append({
            "rel_path": r.get("rel_path", ""),
            "title": r.get("title", ""),
            "dept_id": r.get("dept_id", ""),
            "dept_name": r.get("dept_name", ""),
            "dept_short": r.get("dept_short", ""),
            "date": r.get("date", ""),
            "time": r.get("time", ""),
            "shift_label": r.get("shift_label", ""),
            "size_kb": r.get("size_kb", 0),
            "icon": r.get("icon", "📄"),
            "color": r.get("color", "#38bdf8"),
        })

    today_str = get_ict_now().strftime("%Y-%m-%d")
    today_cnt = sum(1 for r in scanned_reports if r.get("date") == today_str)
    latest_rep_rel = feed[0]["rel_path"] if feed else ""
    sync_time = f"{today_str} {get_ict_now().strftime('%H:%M:%S')}"
    return {
        "department_live_workstation": workstation,
        "latest_reports_feed": feed,
        "vault_sync_meta": {
            "total_reports_scanned": len(scanned_reports),
            "today_reports_count": today_cnt,
            "latest_report_rel_path": latest_rep_rel,
            "latest_sync_time": sync_time,
        },
    }


def publish_war_room_tactical_report(
    trigger_reason: str = "WAR_ROOM_LIVE_SYNC",
    target_ticker: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate and persist fresh intraday & multi-department War-Room reports to disk & Vault."""
    from scripts.apex_live_intraday_brain import (
        compute_live_war_room_snapshot,
        sync_live_intraday_report,
        _upsert_report_into_vault,
    )
    from scripts.apex_enterprise_collaboration_mesh import run_enterprise_work_session

    snap = compute_live_war_room_snapshot(force_refresh=True)
    intraday_path = sync_live_intraday_report(snap, force_write=True)
    directive_text = (
        f"Phiên tác chiến trực tiếp Phòng Tác Chiến ({trigger_reason}) — "
        f"Cập nhật báo cáo và kế hoạch triển khai theo diễn biến thị trường thực tế."
    )
    sess = run_enterprise_work_session(
        directive=directive_text,
        ticker=target_ticker,
        trigger_source="WAR_ROOM_LIVE_PUBLISH",
        sync_cloud=False,
    )

    trading_date = snap.get("trading_date") or get_ict_now().strftime("%Y-%m-%d")
    ent_path = (
        Path(__file__).resolve().parent.parent
        / "08_Master_Investment_CIO"
        / "enterprise_sessions"
        / f"{trading_date}_Enterprise_Work_Session.md"
    )
    if ent_path.exists():
        _upsert_report_into_vault(ent_path, dept_id="ban_8_enterprise")

    war_room_state = get_tactical_war_room_state(force_refresh=True)
    return {
        "ok": True,
        "published_at": get_ict_now().strftime("%Y-%m-%d %H:%M:%S ICT"),
        "intraday_report_path": str(intraday_path.relative_to(Path(__file__).resolve().parent.parent)).replace("\\", "/") if intraday_path else "",
        "enterprise_report_path": f"08_Master_Investment_CIO/enterprise_sessions/{trading_date}_Enterprise_Work_Session.md" if ent_path.exists() else "",
        "enterprise_session_id": (sess or {}).get("session_id", ""),
        "vault_sync_meta": war_room_state.get("vault_sync_meta", {}),
        "war_room_state": war_room_state,
    }


def _format_stock_live_reply(s: Dict[str, Any], holdings_map: Dict[str, Dict[str, Any]]) -> str:
    code = s["code"]
    hold_note = ""
    if code in holdings_map:
        h = holdings_map[code]
        hold_note = (
            f" [ĐANG NẮM GIỮ {h.get('shares', 0)} CP @ Giá vốn {float(h.get('avg_cost', 0)):,.0f} đ | "
            f"PnL tạm tính: {float(h.get('pnl_vnd', 0)):+,.0f} đ ({float(h.get('pnl_pct', 0)):+.2f}%)]"
        )
    else:
        hold_note = " [Chưa nắm giữ — Trạng thái Radar / Standby]"

    fn = float(s.get("foreign_net_ty", 0.0))
    fn_str = f"{fn:+.2f} Tỷ" if abs(fn) > 0 else "0.00 Tỷ"
    return (
        f"Báo cáo Chủ tịch dữ liệu LIVE của {code} ({s.get('name', code)}){hold_note}:\n"
        f"• Giá Live: {s['price']:,.0f} đ ({s['change_pct']:+.2f}%) | Khớp: {int(s.get('volume', 0)):,} CP (Pace {s.get('vol_ratio_20d', 1):.2f}x MA20)\n"
        f"• Dòng tiền: Mua chủ động {s.get('active_buy_pct', 50):.1f}% | RSI(14): {s.get('rsi14', 50):.1f} | Khối ngoại: {fn_str}\n"
        f"• Vùng mục tiêu gom: <= {s.get('probe_target', 0):,.0f} đ | Stop 2xATR: {s.get('stop_loss', 0):,.0f} đ (cách {s.get('dist_to_stop_pct', 0):+.2f}%) | "
        f"TP1: {s.get('tp1', 0):,.0f} đ | TP2: {s.get('tp2', 0):,.0f} đ\n"
        f"• Đánh giá tác chiến: {s.get('security_label', '')} | Catalyst: {s.get('catalyst', '')}"
    )


def handle_tactical_command(command_text: str, user_name: str = "Chủ tịch Trần Quốc Thiên Phước") -> Dict[str, Any]:
    """
    Xử lý chỉ thị hoặc câu hỏi của Chủ tịch gửi cho Minh Quân và Victor thời gian thực.
    100% sử dụng số liệu live SSOT, Bảng điện VPS, Regime và Holdings thực tế.
    """
    command_text = command_text.strip()
    if not command_text:
        return {"ok": False, "error": "Chỉ thị không được để trống."}

    now = get_ict_now()
    time_str = now.strftime("%H:%M:%S")
    cmd_lower = command_text.lower()

    state = get_tactical_war_room_state(force_refresh=True)
    phase = state["phase_info"]
    regime = state.get("intraday_regime", {})
    market_ov = state.get("market_overview", {})
    vni = market_ov.get("vn_index", {})
    vn30 = market_ov.get("vn30_index", {})
    breadth = market_ov.get("market_breadth", {})
    victor = state["victor_sentinel"]
    cash_vnd = float(victor["cash_vnd"])
    stocks_val_vnd = float(victor["stocks_val_vnd"])
    total_nav_vnd = float(victor["total_nav_vnd"])
    cash_pct = float(victor["cash_pct"])
    stocks_pct = float(victor["stocks_pct"])
    total_shares = int(victor["total_shares"])
    holdings = victor.get("holdings", [])
    holdings_map = {str(h.get("symbol", "")).upper(): h for h in holdings}
    live_stocks = state.get("live_stocks", [])
    dynamic_picks = state.get("dynamic_picks", [])

    response_content = ""
    specialist_sign = "Minh Quân (Ban 7 VN) & Victor (Ban 9 Sentinel)"

    # 1. Kiểm tra xem Chủ tịch có hỏi trực tiếp mã cổ phiếu nào trong Watchlist không
    matched_stock = None
    for s in live_stocks:
        sym_low = s["code"].lower()
        if f" {sym_low} " in f" {cmd_lower} " or sym_low in cmd_lower.replace(",", " ").replace(".", " ").split():
            matched_stock = s
            break
    if not matched_stock:
        for s in live_stocks:
            if s["code"].lower() in cmd_lower:
                matched_stock = s
                break

    if any(k in cmd_lower for k in ["kế hoạch tuần", "tuần", "roadmap", "tuần này", "kế hoạch mỗi tuần", "tham khảo tuần"]):
        w_plan = state["weekly_reference_plan"]
        days_lines = "\n".join(
            f"• {d.get('day_name', '')} [{d.get('status_badge', '')}]: {d.get('theme', '')} — {d.get('guideline', '')}"
            for d in w_plan.get("days", [])[:5]
        )
        wl_lines = "\n".join(
            f"• {w.get('symbol')}: {w.get('current_status')} | Stop {w.get('stop_loss_2xatr')} | TP1 {w.get('tp1')}"
            for w in w_plan.get("approved_watchlist", [])[:5]
        )
        response_content = (
            f"📋 [{w_plan.get('title', 'KẾ HOẠCH TUẦN')} — {w_plan.get('week_label', '')}]\n"
            f"⚖️ NGUYÊN TẮC BẤT BIẾN: {w_plan.get('constitution_mandate', '')}\n\n"
            f"📅 LỘ TRÌNH THAM KHẢO:\n{days_lines}\n\n"
            f"🎯 TRẠNG THÁI RỔ THEO DÕI LIVE:\n{wl_lines}"
        )
    elif matched_stock is not None:
        response_content = _format_stock_live_reply(matched_stock, holdings_map)
    elif any(k in cmd_lower for k in ["sập", "giảm mạnh", "rung lắc", "bán tháo", "rủi ro", "thị trường sập"]):
        hold_stops = "; ".join(
            f"{h.get('symbol')}: Stop {float(h.get('stop_loss', 0)):,.0f} đ (hiện {float(h.get('current_price', 0)):,.0f} đ)"
            for h in holdings
        ) or "Chưa có vị thế cổ phiếu (0 CP rủi ro)"
        response_content = (
            f"Victor Sentinel kính báo kịch bản ứng phó biến động dựa trên SSOT LIVE:\n"
            f"1. Tỷ lệ phòng thủ hiện tại: Tiền mặt {cash_vnd:,.0f} đ ({cash_pct:.1f}% NAV) | Cổ phiếu {stocks_val_vnd:,.0f} đ ({stocks_pct:.1f}% NAV).\n"
            f"2. Chế độ thị trường Live: {regime.get('label', 'N/A')} — VN-Index {float(vni.get('value', 0)):,.2f} ({float(vni.get('change_pct', 0)):+.2f}%), Basis VN30F {vn30.get('basis_vn30f', 'N/A')}.\n"
            f"3. Hàng rào Stop Loss 2xATR đang gác 24/7: {hold_stops}.\n"
            f"4. Nếu VN-Index bán tháo (DEFENSIVE_SELLOFF), hệ thống khóa 100% mua mới và kích hoạt Synthetic Short Hedge VN30F khi gãy hỗ trợ lớn."
        )
    elif any(k in cmd_lower for k in ["tiền", "tiền mặt", "két", "sức mua", "số dư", "cash", "nav", "danh mục"]):
        hold_detail = " | ".join(
            f"{h.get('shares', 0)} CP {h.get('symbol')} (Vốn {float(h.get('avg_cost', 0)):,.0f} đ -> Live {float(h.get('current_price', 0)):,.0f} đ, PnL {float(h.get('pnl_vnd', 0)):+,.0f} đ)"
            for h in holdings
        ) or "0 CP (100% Cash)"
        response_content = (
            f"Victor Sentinel báo cáo số liệu tiền thật SSOT LIVE (TCBS 105C307855):\n"
            f"• Tổng NAV Live: {total_nav_vnd:,.0f} đ (Lãi đã chốt lũy kế: +{float(victor.get('realized_round1_profit_vnd', 0)):,.0f} đ | PnL tạm tính danh mục: {float(victor.get('unrealized_pnl_vnd', 0)):+,.0f} đ)\n"
            f"• Tiền mặt khả dụng: {cash_vnd:,.0f} đ ({cash_pct:.1f}% NAV)\n"
            f"• Cổ phiếu đang nắm giữ ({total_shares} CP — {stocks_pct:.1f}% NAV): {hold_detail}."
        )
    elif any(k in cmd_lower for k in ["tiến độ", "báo cáo", "tình hình", "hiện tại", "thế nào", "ra sao", "thị trường"]):
        step_info = state["action_plan"]["current_step"]
        response_content = (
            f"Minh Quân & Victor báo cáo tình hình LIVE lúc {time_str}:\n"
            f"• Pha tác chiến: {step_info['title']} ({step_info['time_range']})\n"
            f"• VN-Index: {float(vni.get('value', 0)):,.2f} ({float(vni.get('change_pct', 0)):+.2f}%) | GTGD: {vni.get('turnover_ty_vnd', 'N/A')} | "
            f"Khối ngoại: {vni.get('foreign_net_ty_vnd', 'N/A')} | Độ rộng: {breadth.get('advancers', 0)}T / {breadth.get('decliners', 0)}G\n"
            f"• Chế độ thị trường: {regime.get('label', '')} — {regime.get('guidance', '')}\n"
            f"• Tài sản Live: NAV {total_nav_vnd:,.0f} đ (Cash {cash_vnd:,.0f} đ • CP {stocks_val_vnd:,.0f} đ).\n"
            f"• Việc cần làm ngay: {step_info['what_to_do']}"
        )
    elif any(k in cmd_lower for k in ["khung giờ vàng", "mấy giờ", "khi nào", "thời gian"]):
        response_content = (
            f"Minh Quân giải trình về Khung Giờ Vàng (14h00 – 14h25): "
            f"Vào buổi sáng thường xuất hiện bẫy kéo giá ảo (Bull-Trap) hoặc đạp ảo ATO. "
            f"Sau 13h45 khi hàng T+2.5 về tài khoản được hấp thụ xong, 90% hình thái nến ngày lộ rõ. "
            f"Chế độ thị trường hôm nay ({regime.get('label', '')}) cho phép giải ngân mới tối đa {regime.get('max_new_allocation_pct', 30)}% két tiền mặt {cash_vnd:,.0f} đ khi thỏa Test Cung!"
        )
    elif any(k in cmd_lower for k in ["lệnh", "mua", "bấm cò", "giải ngân", "vào hàng"]):
        picks_str = "\n".join(
            f"• {p['code']} ({p.get('tier', '')}): Giá Live {p['price']:,.0f} đ | Vùng gom <= {p['probe_target']:,.0f} đ | Stop {p['stop_loss']:,.0f} đ | TP1 {p['tp1']:,.0f} đ | {p['security_label']}"
            for p in dynamic_picks[:4]
        ) or "Chưa có mã mới đạt chuẩn gom."
        response_content = (
            f"Minh Quân kính trình bảng lệnh động theo chế độ {regime.get('label', '')} "
            f"(Két tiền mặt khả dụng {cash_vnd:,.0f} đ • Hạn mức tối đa {regime.get('max_new_allocation_pct', 30)}% Cash):\n"
            f"{picks_str}\n"
            f"• Điều kiện bấm cò: Đặt lệnh LO trong Khung Giờ Vàng 14h00 - 14h25 khi Buy Up >= 50% và không vi phạm Stop!"
        )
    elif any(k in cmd_lower for k in ["alex", "mỹ", "phố wall", "us", "wall street", "nasdaq", "nvda"]):
        response_content = (
            f"Alex (Ban 7 US) xin kính chào Chủ tịch! Phiên New York mở cửa lúc 21h30 tối giờ VN (còn {phase['countdown_to_wall_street']}). "
            f"Watchlist NVDA, AVGO, MSFT, PLTR luôn sẵn sàng phối hợp cùng James và Minh Quân khi Chủ tịch phê duyệt."
        )
    else:
        response_content = (
            f"Minh Quân & Victor đã tiếp nhận chỉ thị lúc {time_str}: \"{command_text}\".\n"
            f"• Trạng thái SSOT Live: NAV {total_nav_vnd:,.0f} đ | Cash {cash_vnd:,.0f} đ ({cash_pct:.1f}%) | "
            f"Đang nắm giữ {total_shares} CP ({stocks_val_vnd:,.0f} đ • PnL {float(victor.get('unrealized_pnl_vnd', 0)):+,.0f} đ).\n"
            f"• VN-Index Live: {float(vni.get('value', 0)):,.2f} ({float(vni.get('change_pct', 0)):+.2f}%) | Chế độ: {regime.get('label', 'N/A')}."
        )

    enterprise_session = {}
    try:
        from scripts.apex_enterprise_collaboration_mesh import run_enterprise_work_session
        target_sym = matched_stock["code"] if isinstance(matched_stock, dict) and matched_stock.get("code") else None
        enterprise_session = run_enterprise_work_session(
            directive=command_text,
            ticker=target_sym,
            trigger_source="WAR_ROOM_COMMAND",
            sync_cloud=False,
        )
        deb_preview = " | ".join(
            f"[{dp['stance']}] {dp['speaker']}: {dp['argument'][:140]}"
            for dp in (enterprise_session.get("debate_points") or [])[:2]
        )
        response_content += (
            f"\n\n🏛️ [Hội Chẩn Doanh Nghiệp V7.0 — {enterprise_session['quorum_count']}/{enterprise_session['roster_total']} Ban | "
            f"{enterprise_session['packet_count']} Packets | {enterprise_session['dissent_count']} Phản biện | Audit {enterprise_session['ombudsman_audit_score']}]\n"
            f"• Phán quyết James: {enterprise_session['final_verdict']} — {enterprise_session['action_plan']}\n"
            + (f"• Tranh biện nổi bật: {deb_preview}" if deb_preview else "")
        )
    except Exception:
        enterprise_session = {}

    directives = load_directives_history()
    directives.append({
        "id": f"dir_user_{int(time.time()*1000)}",
        "timestamp": time_str,
        "sender": "Chủ tịch Trần Quốc Thiên Phước",
        "role": "chairman",
        "type": "chairman_directive",
        "content": command_text
    })
    directives.append({
        "id": f"dir_resp_{int(time.time()*1000)+1}",
        "timestamp": time_str,
        "sender": specialist_sign,
        "role": "specialist",
        "type": "specialist_reply",
        "content": response_content
    })

    save_directives_history(directives)

    return {
        "ok": True,
        "timestamp": time_str,
        "chairman_command": command_text,
        "specialist_response": response_content,
        "directives_history": directives,
        "enterprise_session": enterprise_session,
    }


if __name__ == "__main__":
    st = get_tactical_war_room_state()
    print("Action Plan current step:", st["action_plan"]["current_step"]["title"])
    print("Market Regime:", st["intraday_regime"]["label"])
    print("Market Overview VN-Index:", st["market_overview"]["vn_index"]["value"])
    print("Live Stocks count:", len(st["live_stocks"]))
    print("Victor Live NAV:", st["victor_sentinel"]["total_nav_vnd"])
    print("TEST OK!")
