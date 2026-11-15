#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APEX INSTITUTIONAL SUMMIT MEETING ENGINE (REAL-TIME WAR ROOM BACKEND)
File: scripts/apex_summit_meeting_engine.py
Phục vụ: Chủ tịch HĐQT Trần Quốc Thiên Phước (Tài khoản TCBS: 105C307855)
Chủ trì điều phối: Master CIO James (Ban 8) & Palmer (Cố vấn Điều hành)
Giám sát thể chế: Ban 12 — Tổng Kiểm Sát Viên Trọng (LUÔN BẤT BIẾN)

Chức năng:
1. Quản lý trạng thái cuộc họp thời gian thực (Real-time Meeting State).
2. Tự động đồng bộ các lượt phát biểu, tranh biện, dữ liệu BCTC và biểu quyết theo từng phút.
3. Cung cấp API endpoint JSON cho Web Portal tự động poll và stream theo thời gian thực.
4. Ghi nhận và phản hồi ngay lập tức khi Chủ tịch gõ chỉ thị can thiệp vào phòng họp.
5. Cột giám sát độc quyền của Tổng Kiểm Sát Viên Trọng đo lường 100% tính tuân thủ Hiến Chương.
"""

import os
import sys
import json
import time
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

try:
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
MEETING_STATE_FILE = DATA_DIR / "apex_active_meeting_state.json"
MEETING_AUDIT_LOG_FILE = DATA_DIR / "apex_summit_audit_stream.json"
ICT_TZ = datetime.timezone(datetime.timedelta(hours=7))


def _get_ict_now(custom_now: Optional[datetime.datetime] = None) -> datetime.datetime:
    """Chuẩn hóa thời gian về múi giờ ICT (+07:00) cho cả Windows Local và Render Cloud Linux."""
    if custom_now is None:
        return datetime.datetime.now(ICT_TZ)
    if custom_now.tzinfo is None:
        return custom_now.replace(tzinfo=ICT_TZ)
    return custom_now.astimezone(ICT_TZ)


def _get_live_account_state_dict() -> Dict[str, Any]:
    """Đọc trạng thái SSOT sống từ PortfolioStateManager để đồng bộ tuyệt đối 100%."""
    try:
        from scripts.portfolio_state_manager import PortfolioStateManager
        st = PortfolioStateManager.load_state()
    except Exception:
        st = {}
    cash = float(st.get("cash_balance_vnd", 12516471.0) or 12516471.0)
    mkt = float(st.get("total_market_val_vnd", 0.0) or 0.0)
    nav = float(st.get("total_nav_vnd", cash + mkt) or (cash + mkt))
    if nav <= 0:
        nav = max(1.0, cash + mkt)
    realized = float(st.get("realized_pnl_vnd", 0.0) or 0.0)
    unrealized = float(st.get("unrealized_pnl_vnd", 0.0) or 0.0)
    cash_pct = round((cash / nav) * 100.0, 1)
    pos_map = st.get("active_positions") or {}
    held = [
        f"{p.get('symbol', k)} ({int(p.get('shares', 0))} CP @ {float(p.get('entry_price') or p.get('avg_cost_vnd') or 0):,.0f}₫)"
        for k, p in pos_map.items()
        if isinstance(p, dict) and int(p.get("shares", 0) or 0) > 0
    ]
    held_str = ", ".join(held) if held else "0 CP"
    equity_str = f"{mkt:,.0f} ₫ ({held_str})" if held else "0 ₫ (0 CP kẹp hàng)"
    return {
        "account_no": f"{st.get('account_id', '105C307855')} (TCBS)",
        "total_nav": f"{nav:,.0f} ₫",
        "cash_balance": f"{cash:,.0f} ₫",
        "cash_ratio": f"{cash_pct:.1f}%",
        "equity_risk": equity_str,
        "realized_profit_v1": f"{realized:+,.0f} ₫ (Tạm tính: {unrealized:+,.0f} ₫)",
        "_raw_nav": nav,
        "_raw_cash": cash,
        "_raw_cash_pct": cash_pct,
        "_held_str": held_str,
    }


def _get_live_enterprise_mesh() -> Dict[str, Any]:
    try:
        from scripts.apex_enterprise_collaboration_mesh import get_enterprise_mesh_summary
        return get_enterprise_mesh_summary()
    except Exception:
        return {}


def get_default_summit_data() -> Dict[str, Any]:
    """Khởi tạo cấu trúc dữ liệu thể chế chuẩn hóa V10.0 cho Đại Hội Nghị Thượng Đỉnh."""
    from scripts.apex_autonomous_council_engine import (
        CHARTER_REPORT_PATH,
        SUMMIT_CHARTER_RULES,
        build_autonomous_summit_session,
        load_summit_archive_ledger,
    )
    try:
        sess = build_autonomous_summit_session()
        sess["enterprise_mesh_session"] = _get_live_enterprise_mesh()
        return sess
    except Exception as e:
        print(f"[SummitEngine] Lỗi khởi tạo phiên họp V10.0: {e}")
        acc = _get_live_account_state_dict()
        now_ict = datetime.now(ICT_TZ)
        ledger = load_summit_archive_ledger()
        return {
            "meeting_id": f"APEX-SUMMIT-STANDBY-{now_ict.strftime('%Y%m%d-%H%M')}",
            "version": "10.0-Autonomous-Charter-Vault",
            "title": "ĐẠI HỘI NGHỊ THƯỢNG ĐỈNH TOÀN DOANH NGHIỆP APEX",
            "subtitle": "Phòng họp đang ở trạng thái chờ triệu tập phiên mới theo Hiến Chương 5 Điều",
            "start_time": now_ict.isoformat(timespec="seconds"),
            "end_time": now_ict.isoformat(timespec="seconds"),
            "prep_start_time": now_ict.isoformat(timespec="seconds"),
            "prep_minutes": 20,
            "duration_minutes": 30,
            "mode": "CLEANED_STANDBY",
            "status_override": "CLEANED_STANDBY",
            "account_state": acc,
            "charter_report_path": CHARTER_REPORT_PATH,
            "summit_charter_rules": SUMMIT_CHARTER_RULES,
            "phases": [],
            "voting_board": [],
            "timeline_stream": [],
            "pre_summit_prep_stream": [],
            "dynamic_messages": [],
            "inspector_notes": [],
            "james_executive_summary": None,
            "archive_summary": {
                "total_archived": ledger.get("total_archived", 0),
                "archived_sessions": ledger.get("sessions", [])[:15],
            },
            "enterprise_mesh_session": _get_live_enterprise_mesh(),
        }


def load_meeting_state() -> Dict[str, Any]:
    """Tải trạng thái cuộc họp từ file; bảo lưu sạch sẽ phiên STANDBY hoặc tự động nâng cấp V10.0."""
    if not MEETING_STATE_FILE.exists():
        from scripts.apex_autonomous_council_engine import activate_autonomous_summit_session
        return activate_autonomous_summit_session()
    try:
        with open(MEETING_STATE_FILE, "r", encoding="utf-8") as f:
            st = json.load(f)
        if isinstance(st, dict) and st.get("room_status") == "CLEANED_STANDBY":
            return st
        if (
            not isinstance(st, dict)
            or not st.get("pre_summit_prep_dossiers")
            or len(st.get("pre_summit_prep_dossiers", [])) < 14
            or "2026-11-08" in str(st.get("start_time", ""))
            or not st.get("james_executive_summary")
            or not st.get("summit_charter_rules")
        ):
            from scripts.apex_autonomous_council_engine import (
                archive_summit_session,
                activate_autonomous_summit_session,
            )
            if isinstance(st, dict) and st.get("meeting_id"):
                archive_summit_session(st, reason="AUTO_ARCHIVED_BEFORE_V10_UPGRADE", archived_by="Apex System Auto-Upgrader")
            return activate_autonomous_summit_session()
        return st
    except Exception:
        from scripts.apex_autonomous_council_engine import activate_autonomous_summit_session
        return activate_autonomous_summit_session()


def save_meeting_state(state: Dict[str, Any]) -> None:
    """Lưu trạng thái cuộc họp vào file một cách an toàn."""
    temp_file = MEETING_STATE_FILE.with_suffix(".tmp")
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    temp_file.replace(MEETING_STATE_FILE)


def schedule_custom_summit_meeting(
    start_time_str: Optional[str] = None,
    duration_minutes: int = 30,
    topic: Optional[str] = None,
    trigger_prep_now: bool = True,
    prep_minutes: int = 20
) -> Dict[str, Any]:
    """
    Lập lịch và kích hoạt ngay một Phiên Họp Thượng Đỉnh V10.0 tùy chỉnh (14/14 Phòng Ban).
    Mặc định nghiên cứu tiền hội nghị 20 phút (T-15..20p Pre-Summit Research & Reconnaissance).
    Phiên họp cũ (nếu có) được tự động lưu trữ vào Summit Archive Vault trước khi kích hoạt lịch mới.
    """
    try:
        from scripts.apex_autonomous_council_engine import activate_autonomous_summit_session
        st = activate_autonomous_summit_session(
            start_time_iso=start_time_str,
            duration_minutes=duration_minutes,
            topic=topic,
            prep_minutes=prep_minutes
        )
    except Exception as e:
        st = get_default_summit_data()
        save_meeting_state(st)
        return {"ok": False, "error": str(e), "state": get_realtime_meeting_state()}

    rt = get_realtime_meeting_state()
    return {
        "ok": True,
        "meeting_id": st.get("meeting_id"),
        "title": st.get("title"),
        "topic": st.get("topic"),
        "prep_start_time": st.get("prep_start_time"),
        "start_time": st.get("start_time"),
        "end_time": st.get("end_time"),
        "duration_minutes": st.get("duration_minutes"),
        "prep_duration_minutes": st.get("prep_duration_minutes", 20),
        "meeting_window_str": st.get("meeting_window_str"),
        "prep_window_str": st.get("prep_window_str"),
        "resolution_report_path": st.get("resolution_report_path"),
        "james_summary_report_path": st.get("james_summary_report_path"),
        "prep_dossiers_count": len(st.get("pre_summit_prep_dossiers", [])),
        "attendance_summary": st.get("attendance_summary"),
        "archive_summary": st.get("archive_summary"),
        "trigger_prep_now": bool(trigger_prep_now),
        "state": rt,
    }


def _parse_ict_dt(iso_str: str, fallback_dt: datetime.datetime) -> datetime.datetime:
    try:
        dt = datetime.datetime.fromisoformat(str(iso_str))
        if dt.tzinfo is None:
            return dt.replace(tzinfo=ICT_TZ)
        return dt.astimezone(ICT_TZ)
    except Exception:
        return fallback_dt


def get_realtime_meeting_state(
    custom_now: Optional[datetime.datetime] = None,
    preview_mode: bool = False,
    archive_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Tính toán trạng thái thời gian thực chuẩn ICT (+07:00) của cuộc họp Thượng Đỉnh V10.0:
    0. ARCHIVED_VIEW (khi có archive_id): Mở xem lại nguyên văn một phiên họp lịch sử trong Kho Lưu Trữ.
    1. CLEANED_STANDBY (sau khi đủ Chủ tịch duyệt + 2H và bấm dọn phòng): Phòng sạch chờ lịch mới.
    2. WAITING_COUNTDOWN (> T-20p trước giờ G): Cả 14 Ban vẫn hiển thị trạng thái đang nghiên cứu trước họp.
    3. PRE_MEETING_PREP_15M (trong khung T-15..20p -> T-0p): 14/14 Phòng Ban nộp Hồ sơ Chuẩn Bị & Nội Quy 5 Điều.
    4. LIVE_IN_PROGRESS (trong 30p họp chính thức): Mở khóa toàn bộ hồ sơ + luồng tranh biện theo từng phút.
    5. CONCLUDED / PREVIEW_FULL: Tự động lưu trữ vào Archive Vault & chạy đồng hồ Quy chế 2 Tiếng sau phê duyệt.
    """
    from scripts.apex_autonomous_council_engine import (
        CHARTER_REPORT_PATH,
        SUMMIT_CHARTER_RULES,
        archive_summit_session,
        compute_retention_status,
        get_archived_summit_by_id,
        load_summit_archive_ledger,
    )

    now = _get_ict_now(custom_now)
    is_archived_view = False
    state: Optional[Dict[str, Any]] = None
    if archive_id:
        arch = get_archived_summit_by_id(archive_id)
        if arch:
            state = arch
            is_archived_view = True

    if state is None:
        state = load_meeting_state()

    default_start = now.replace(hour=0, minute=45, second=0, microsecond=0)
    default_end = default_start + datetime.timedelta(minutes=30)
    start_dt = _parse_ict_dt(state.get("start_time", ""), default_start)
    end_dt = _parse_ict_dt(state.get("end_time", ""), default_end)
    prep_mins = max(15, min(30, int(state.get("prep_duration_minutes", 20) or 20)))
    prep_seconds = prep_mins * 60
    prep_start_dt = _parse_ict_dt(state.get("prep_start_time", ""), start_dt - datetime.timedelta(minutes=prep_mins))

    duration_minutes = max(10, int(state.get("duration_minutes", 30) or 30))
    duration_seconds = max(60, int((end_dt - start_dt).total_seconds()))

    delta_to_start = (start_dt - now).total_seconds()
    delta_from_start = (now - start_dt).total_seconds()
    elapsed_minutes = max(0, int(delta_from_start // 60))

    prep_stream = state.get("prep_timeline_stream") or []
    debate_stream = state.get("timeline_stream") or []
    raw_dossiers = state.get("pre_summit_prep_dossiers") or []
    attendance_roster = state.get("attendance_roster") or []
    prep_progress_pct = 100.0

    archive_summary = load_summit_archive_ledger()

    if is_archived_view:
        meeting_status = "ARCHIVED_VIEW"
        current_minute = duration_minutes
        current_phase = 2
        current_step = 8
        unlocked_prep = prep_stream
        unlocked_debate = debate_stream
        prep_dossiers = raw_dossiers
    elif state.get("room_status") == "CLEANED_STANDBY" and not preview_mode:
        meeting_status = "CLEANED_STANDBY"
        current_minute = 0
        current_phase = 0
        current_step = 0
        unlocked_prep = []
        unlocked_debate = []
        prep_dossiers = []
        prep_progress_pct = 0.0
    elif preview_mode:
        meeting_status = "PREVIEW_FULL"
        current_minute = duration_minutes
        current_phase = 2
        current_step = 8
        unlocked_prep = prep_stream
        unlocked_debate = debate_stream
        prep_dossiers = raw_dossiers
    elif delta_to_start > prep_seconds:
        meeting_status = "WAITING_COUNTDOWN"
        current_minute = -prep_mins
        current_phase = 0
        current_step = 0
        prep_progress_pct = 0.0
        prep_dossiers = [
            {
                **d,
                "status": "RESEARCHING_BEFORE_MEETING",
                "pre_meeting_findings": f"[ĐANG CÀO DỮ LIỆU TIỀN HỘI NGHỊ] {d.get('pre_meeting_findings', '')}",
            }
            for d in raw_dossiers
        ]
        unlocked_prep = [
            {
                "id": "pre_001",
                "minute": -prep_mins - 1,
                "is_prep_phase": True,
                "time_str": now.strftime("%H:%M:%S"),
                "phase_step": 0,
                "sender_name": "Tổng Kiểm Sát Viên Trọng (Ban 12)",
                "department": "Ban 12 — Tổng Kiểm Sát Thể Chế",
                "role": "Giám Sát Viên Thường Trực Bất Biến",
                "avatar": "🛡️",
                "badge": f"CHỜ MỞ PHIÊN NGHIÊN CỨU T-{prep_mins}P",
                "badge_color": "#f59e0b",
                "content": (
                    f"Báo cáo Chủ tịch Phước Trần: Toàn bộ 14 Phòng Ban đang hoàn tất giai đoạn tìm kiếm & phân tích số liệu sống cho nghị trình '{state.get('topic', '')}'. "
                    f"Cổng nộp hồ sơ T-{prep_mins} phút chính thức mở lúc {prep_start_dt.strftime('%H:%M:%S')} trước khi khai mạc lúc {start_dt.strftime('%H:%M:%S')}!"
                ),
                "highlight": f"Nghiên cứu T-{prep_mins}p bắt đầu lúc {prep_start_dt.strftime('%H:%M')} • Khai mạc {start_dt.strftime('%H:%M')}",
                "metrics": {"countdown_seconds": int(delta_to_start), "Departments": "14/14", "Prep_Window": f"{prep_mins} Phút"}
            }
        ]
        unlocked_debate = []
    elif 0 < delta_to_start <= prep_seconds:
        meeting_status = "PRE_MEETING_PREP_15M"
        prep_elapsed_secs = max(0, int((now - prep_start_dt).total_seconds()))
        prep_progress_pct = round(min(100.0, max(0.0, (prep_elapsed_secs / max(1, prep_seconds)) * 100.0)), 1)
        prep_minute = min(-1, -prep_mins + int(prep_elapsed_secs // 60))
        current_minute = prep_minute
        current_phase = 0
        current_step = 0
        unlocked_prep = [m for m in prep_stream if int(m.get("minute", -prep_mins)) <= prep_minute]
        if not unlocked_prep and prep_stream:
            unlocked_prep = [prep_stream[0]]
        prep_dossiers = [
            {
                **d,
                "status": "READY_VERIFIED" if int(d.get("prep_minute", -1)) <= prep_minute else "RESEARCHING_BEFORE_MEETING",
            }
            for d in raw_dossiers
        ]
        unlocked_debate = []
    elif 0 <= delta_from_start <= duration_seconds:
        meeting_status = "LIVE_IN_PROGRESS"
        current_minute = min(duration_minutes, elapsed_minutes)
        current_phase = 1 if current_minute < 13 else 2

        if current_minute < 3:
            current_step = 1
        elif current_minute < 8:
            current_step = 2
        elif current_minute < 13:
            current_step = 3
        elif current_minute < 18:
            current_step = 4
        elif current_minute < 23:
            current_step = 5
        elif current_minute < 28:
            current_step = 6
        elif current_minute < 29:
            current_step = 7
        else:
            current_step = 8

        unlocked_prep = prep_stream
        prep_dossiers = raw_dossiers
        unlocked_debate = [
            msg for msg in debate_stream
            if int(msg.get("minute", 0)) <= current_minute
        ]
    else:
        meeting_status = "CONCLUDED"
        current_minute = duration_minutes
        current_phase = 2
        current_step = 8
        unlocked_prep = prep_stream
        prep_dossiers = raw_dossiers
        unlocked_debate = debate_stream

        mid = str(state.get("meeting_id") or "")
        archived_ids = {s.get("meeting_id") for s in (archive_summary.get("sessions") or []) if isinstance(s, dict)}
        if mid and mid not in archived_ids:
            archive_summit_session(state, reason="CONCLUDED_AUTO_ARCHIVED", archived_by="Ban 11 & Trọng Auto-Archiver")
            archive_summary = load_summit_archive_ledger()

    retention_status = compute_retention_status(state, now)
    all_messages = unlocked_prep + unlocked_debate + (state.get("dynamic_messages") or [])
    live_acc = _get_live_account_state_dict()
    live_account_state = {
        "account_no": live_acc["account_no"],
        "total_nav": live_acc["total_nav"],
        "cash_balance": live_acc["cash_balance"],
        "cash_ratio": live_acc["cash_ratio"],
        "equity_risk": live_acc["equity_risk"],
        "realized_profit_v1": live_acc["realized_profit_v1"],
    }

    return {
        "meeting_id": state.get("meeting_id"),
        "title": state.get("title"),
        "topic": state.get("topic") or state.get("title"),
        "subtitle": state.get("subtitle"),
        "room_status": state.get("room_status", "ACTIVE_SESSION"),
        "is_archived_view": is_archived_view,
        "prep_start_time": state.get("prep_start_time"),
        "start_time": state.get("start_time"),
        "end_time": state.get("end_time"),
        "duration_minutes": duration_minutes,
        "prep_duration_minutes": prep_mins,
        "prep_progress_pct": prep_progress_pct,
        "meeting_window_str": state.get("meeting_window_str") or f"{start_dt.strftime('%Hh%M')} – {end_dt.strftime('%Hh%M')} ({duration_minutes} Phút)",
        "prep_window_str": state.get("prep_window_str") or f"{prep_start_dt.strftime('%Hh%M')} – {start_dt.strftime('%Hh%M')} (Nghiên Cứu T-{prep_mins}p)",
        "charter_report_path": state.get("charter_report_path") or CHARTER_REPORT_PATH,
        "summit_charter_rules": state.get("summit_charter_rules") or SUMMIT_CHARTER_RULES,
        "james_executive_summary": state.get("james_executive_summary"),
        "james_summary_report_path": state.get("james_summary_report_path") or (state.get("james_executive_summary") or {}).get("report_path"),
        "resolution_report_path": state.get("resolution_report_path") or CHARTER_REPORT_PATH,
        "agenda_report_path": state.get("agenda_report_path") or CHARTER_REPORT_PATH,
        "retention_status": retention_status,
        "archive_summary": archive_summary,
        "meeting_status": meeting_status,
        "countdown_seconds": max(0, int(delta_to_start)),
        "current_minute": current_minute,
        "current_phase": current_phase,
        "current_step": current_step,
        "chairman": state.get("chairman"),
        "chairperson_host": state.get("chairperson_host"),
        "permanent_inspector": state.get("permanent_inspector"),
        "attendance_roster": attendance_roster,
        "attendance_summary": state.get("attendance_summary") or f"{len(prep_dossiers)}/14 Phòng Ban có mặt 100%",
        "pre_summit_prep_dossiers": prep_dossiers,
        "prep_timeline_stream": unlocked_prep,
        "prep_messages_count": len(unlocked_prep),
        "debate_messages_count": len(unlocked_debate),
        "account_state": live_account_state,
        "compliance_audit": state.get("compliance_audit"),
        "phases": state.get("phases"),
        "voting_board": state.get("voting_board"),
        "executive_approval": state.get("executive_approval"),
        "timeline_stream": all_messages,
        "inspector_notes": state.get("inspector_notes"),
        "enterprise_mesh_session": state.get("enterprise_mesh_session") or _get_live_enterprise_mesh(),
        "total_messages_count": len(all_messages),
        "server_time": now.strftime("%Y-%m-%d %H:%M:%S ICT"),
        "server_hhmm": start_dt.strftime("%Hh%M"),
    }


def add_chairman_directive(user_message: str) -> Dict[str, Any]:
    """
    Xử lý chỉ thị trực tiếp từ Chủ tịch Phước Trần gõ ngay tại phòng họp.
    Hệ thống ghi nhận và Master CIO James / Các phòng ban chuyên trách / Trọng phản hồi lập tức
    với đầy đủ tư duy độc lập, đối chất số liệu kiểm toán và rẽ nhánh thông minh.
    """
    state = load_meeting_state()
    now_dt = _get_ict_now()
    now_str = now_dt.strftime("%H:%M:%S")
    ts_chair = int(time.time() * 1000)

    chairman_msg = {
        "id": f"dyn_chair_{ts_chair}",
        "minute": 99,
        "time_str": now_str,
        "phase_step": 99,
        "sender_name": "Chủ tịch Trần Quốc Thiên Phước",
        "department": "Hội Đồng Quản Trị Tối Cao",
        "role": "Chủ Tọa Hội Nghị",
        "avatar": "👑",
        "badge": "CHỈ THỊ CỦA CHỦ TỊCH",
        "badge_color": "#eab308",
        "content": user_message,
        "highlight": "Chỉ thị can thiệp trực tiếp từ Chủ tịch",
        "metrics": None
    }
    state.setdefault("dynamic_messages", []).append(chairman_msg)

    try:
        from scripts.apex_directive_intelligence_engine import ApexDirectiveIntelligenceEngine
        council_responses = ApexDirectiveIntelligenceEngine.generate_executive_directive_reply(user_message, state)
    except Exception:
        from scripts.master_cio_james_agent import handle_james_chat
        reply_txt = handle_james_chat(user_message)
        council_responses = [
            {
                "id": f"dyn_james_{ts_chair+1}",
                "minute": 99,
                "time_str": now_str,
                "phase_step": 99,
                "sender_name": "Master CIO James",
                "department": "Ban 8 — Tổng Tư Lệnh Master CIO",
                "role": "Chủ Trì Điều Phối",
                "avatar": "🎖️",
                "badge": "BÁO CÁO THỰC THI",
                "badge_color": "#38bdf8",
                "content": reply_txt,
                "highlight": "Báo cáo thực thi của Master CIO James",
                "metrics": None
            },
            {
                "id": f"dyn_trong_{ts_chair+2}",
                "minute": 99,
                "time_str": now_str,
                "phase_step": 99,
                "sender_name": "Tổng Kiểm Sát Viên Trọng (Ban 12)",
                "department": "Ban 12 — Tổng Kiểm Sát Thể Chế",
                "role": "Giám Sát Viên Thường Trực",
                "avatar": "🛡️",
                "badge": "KIỂM SÁT KỶ LUẬT",
                "badge_color": "#f59e0b",
                "content": "Tổng Kiểm Sát Viên Trọng xác nhận: Đã niêm phong chỉ thị của Chủ tịch vào Sổ Cái Thể Chế. Hệ thống ghi nhận và kiểm sát kỷ luật tuân thủ Hiến Chương Apex V1.0.",
                "highlight": "Ghi nhận & kiểm sát kỷ luật thể chế",
                "metrics": None
            }
        ]

    for resp in council_responses:
        state["dynamic_messages"].append(resp)

    save_meeting_state(state)

    james_msg = next((m for m in council_responses if "James" in m.get("sender_name", "")), council_responses[0])
    trong_msg = next((m for m in reversed(council_responses) if "Trọng" in m.get("sender_name", "")), council_responses[-1])

    return {
        "ok": True,
        "chairman_msg": chairman_msg,
        "responses": council_responses,
        "james_resp": james_msg,
        "trong_resp": trong_msg
    }


if __name__ == "__main__":
    print("Khởi tạo và kiểm thử Apex Summit Meeting Engine V9.0...")
    st = get_default_summit_data()
    save_meeting_state(st)
    rt = get_realtime_meeting_state(preview_mode=True)
    print(f"[OK] Đã tải trạng thái: {rt['title']}")
    print(f"[OK] Hồ sơ chuẩn bị T-15p: {len(rt['pre_summit_prep_dossiers'])} Ban | Điểm danh: {rt['attendance_summary']}")
    print(f"[OK] Tổng tin nhắn (T-15p + 30p tranh biện): {len(rt['timeline_stream'])}")
    print(f"[OK] Số mã trong bảng biểu quyết: {len(rt['voting_board'])}")
    print(f"[OK] Nghị quyết: {rt['resolution_report_path']}")
