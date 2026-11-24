#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JAMES DAILY OPS ACTIVATOR (ONE-PHRASE SCHEDULE ORCHESTRATOR V7.0)
File: scripts/james_daily_ops_activator.py
Pure Python Standard Library ONLY.

Phục vụ kích hoạt toàn bộ 8 mốc tác chiến trong ngày (08:30, 09:00, 11:35, 13:00, 13:30, 14:05, 14:20, 15:45)
tại phòng chat Antigravity của Master CIO James (qua tool `schedule`), Web Portal & Telegram James HQ.
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from scripts.vn_market_calendar import get_ict_now, get_vn_market_session_state

STATE_OUT = BASE_DIR / "data" / "james_daily_ops_schedule_state.json"

DAILY_8_OPS_SLOTS: List[Dict[str, Any]] = [
    {
        "slot_id": "0830_PREATO",
        "time": "08:30",
        "hour": 8,
        "minute": 30,
        "cron_expr": "30 8 * * 1-5",
        "title": "Chuẩn Bị Trước ATO & Quét Tin/BCTC (08h30)",
        "commands": [
            "python -X utf8 scripts/apex_daily_internet_intel_crawler.py",
            "python -X utf8 scripts/apex_brain_v4_profit_engine.py",
            "python -X utf8 scripts/apex_inspector_trong.py --run-v7-gates",
            "python -X utf8 scripts/palmer_antigravity_sync_bridge.py --sync-current",
        ],
    },
    {
        "slot_id": "0900_OPEN_ATO",
        "time": "09:00",
        "hour": 9,
        "minute": 0,
        "cron_expr": "0 9 * * 1-5",
        "title": "Mở Phiên ATO & Chốt Chặn Chống FOMO (09h00)",
        "commands": [
            "python -X utf8 scripts/apex_daily_live_warroom_engine.py --once --no-telegram",
            "python -X utf8 scripts/vn3_portfolio_autonomous_sentinel.py --scan-once",
            "python -X utf8 scripts/apex_inspector_trong.py --run-v7-gates",
            "python -X utf8 scripts/palmer_antigravity_sync_bridge.py --sync-current",
        ],
    },
    {
        "slot_id": "1135_NOON_CLOSE",
        "time": "11:35",
        "hour": 11,
        "minute": 35,
        "cron_expr": "35 11 * * 1-5",
        "title": "Chốt Phiên Sáng & Đánh Giá Cung Cầu (11h35)",
        "commands": [
            "python -X utf8 scripts/apex_daily_live_warroom_engine.py --once --no-telegram",
            "python -X utf8 scripts/vn3_portfolio_autonomous_sentinel.py --scan-once",
            "python -X utf8 scripts/apex_inspector_trong.py --run-v7-gates",
            "python -X utf8 scripts/palmer_antigravity_sync_bridge.py --sync-current",
        ],
    },
    {
        "slot_id": "1300_AFTERNOON_T25",
        "time": "13:00",
        "hour": 13,
        "minute": 0,
        "cron_expr": "0 13 * * 1-5",
        "title": "Bắt Đầu Phiên Chiều & Radar Hàng T+2.5 (13h00)",
        "commands": [
            "python -X utf8 scripts/vn3_portfolio_autonomous_sentinel.py --scan-once",
            "python -X utf8 scripts/apex_daily_live_warroom_engine.py --once --no-telegram",
            "python -X utf8 scripts/palmer_antigravity_sync_bridge.py --sync-current",
        ],
    },
    {
        "slot_id": "1330_PREP_14H",
        "time": "13:30",
        "hour": 13,
        "minute": 30,
        "cron_expr": "30 13 * * 1-5",
        "title": "Nghiên Cứu Thị Trường Chuẩn Bị Cho 14h00 (13h30)",
        "commands": [
            "python -X utf8 scripts/apex_daily_internet_intel_crawler.py",
            "python -X utf8 scripts/apex_brain_v4_profit_engine.py",
            "python -X utf8 scripts/apex_daily_live_warroom_engine.py --once --no-telegram",
            "python -X utf8 scripts/apex_inspector_trong.py --run-v7-gates",
            "python -X utf8 scripts/palmer_antigravity_sync_bridge.py --sync-current",
        ],
    },
    {
        "slot_id": "1405_GOLDEN_HOUR",
        "time": "14:05",
        "hour": 14,
        "minute": 5,
        "cron_expr": "5 14 * * 1-5",
        "title": "Khung Giờ Vàng Quyết Định Giải Ngân (14h05)",
        "commands": [
            "python -X utf8 scripts/vn3_portfolio_autonomous_sentinel.py --scan-once",
            "python -X utf8 scripts/apex_daily_live_warroom_engine.py --once --no-telegram",
            "python -X utf8 scripts/apex_inspector_trong.py --run-v7-gates",
            "python -X utf8 scripts/palmer_antigravity_sync_bridge.py --sync-current",
        ],
    },
    {
        "slot_id": "1420_PRE_ATC",
        "time": "14:20",
        "hour": 14,
        "minute": 20,
        "cron_expr": "20 14 * * 1-5",
        "title": "Nghiên Cứu & Chốt Kế Hoạch Trước ATC (14h20)",
        "commands": [
            "python -X utf8 scripts/vn3_portfolio_autonomous_sentinel.py --scan-once",
            "python -X utf8 scripts/apex_daily_live_warroom_engine.py --once --no-telegram",
            "python -X utf8 scripts/apex_inspector_trong.py --run-v7-gates",
            "python -X utf8 scripts/palmer_antigravity_sync_bridge.py --sync-current",
        ],
    },
    {
        "slot_id": "1545_EOD_WRAP",
        "time": "15:45",
        "hour": 15,
        "minute": 45,
        "cron_expr": "45 15 * * 1-5",
        "title": "Tổng Kết EOD, Tự Học & Kiểm Toán Trọng (15h45)",
        "commands": [
            "python -X utf8 scripts/apex_daily_live_warroom_engine.py --once --no-telegram",
            "python -X utf8 scripts/vn3_portfolio_autonomous_sentinel.py --scan-once",
            "python -X utf8 scripts/apex_brain_v4_profit_engine.py",
            "python -X utf8 scripts/palmer_antigravity_sync_bridge.py --sync-current",
            "python -X utf8 scripts/apex_inspector_trong.py --run-v7-gates",
            "python -X utf8 scripts/sync_chat_office_artifact.py",
            "python -X utf8 scripts/apex_system_watchdog.py --check-http",
        ],
    },
]


def _build_slot_prompt(slot: Dict[str, Any]) -> str:
    cmds_joined = " ; ".join(slot["commands"])
    return (
        f"[JAMES TÁC CHIẾN {slot['time']} ICT — {slot['title']}]\n"
        "1. Đọc bắt buộc `00_LIVE_INTER_CHAT_STATE.md` & `data/canonical_executive_briefing.json` trước khi kết luận.\n"
        f"2. Chạy chuỗi lệnh đồng bộ: `{cmds_joined}` (nếu ngày nghỉ lễ theo `scripts/vn_market_calendar.py` thì giữ nguyên kỷ luật standdown).\n"
        "3. Trả lời Chủ tịch ngay tại đoạn chat James này thật ngắn gọn, trực diện 4 ý: "
        "(1) Đang cầm gì & T+2.5, (2) Lãi/Lỗ ròng sau phí TCBS, (3) Hành động MUA/BÁN/ĐỢI cụ thể & giá nào, (4) Kết quả Trọng 12 Cổng & SCBP SHA-256."
    )


def get_daily_ops_schedule_plan(now_ict: Optional[datetime.datetime] = None) -> Dict[str, Any]:
    """Tính toán các khung giờ tác chiến còn lại trong ngày hôm nay theo giờ Việt Nam (ICT)."""
    now = now_ict or get_ict_now()
    msess = get_vn_market_session_state(now_ict=now)
    is_trading = bool(msess.get("is_trading_day", False))
    cur_hm = now.hour * 60 + now.minute

    upcoming: List[Dict[str, Any]] = []
    passed: List[Dict[str, Any]] = []

    for s in DAILY_8_OPS_SLOTS:
        slot_hm = s["hour"] * 60 + s["minute"]
        enriched = {
            **s,
            "prompt": _build_slot_prompt(s),
            "already_passed_today": is_trading and (slot_hm <= cur_hm),
        }
        if is_trading and slot_hm <= cur_hm:
            passed.append(enriched)
        else:
            upcoming.append(enriched)

    return {
        "ok": True,
        "generated_at_ict": now.strftime("%Y-%m-%d %H:%M:%S ICT"),
        "date_ict": now.strftime("%Y-%m-%d"),
        "is_trading_day": is_trading,
        "market_status_code": msess.get("status_code"),
        "next_trading_day": msess.get("next_trading_day"),
        "total_slots": len(DAILY_8_OPS_SLOTS),
        "upcoming_count": len(upcoming),
        "passed_count": len(passed),
        "upcoming_slots": upcoming,
        "passed_slots": passed,
    }


def arm_daily_ops_in_james(
    room_name: str = "JAMES_ANTIGRAVITY_CHAT",
    recurring_weekdays: bool = False,
    now_ict: Optional[datetime.datetime] = None,
) -> Dict[str, Any]:
    """Ghi nhận trạng thái đã kích hoạt lịch tác chiến trong ngày cho James & đồng bộ Portal."""
    plan = get_daily_ops_schedule_plan(now_ict=now_ict)
    state_payload = {
        "version": "V7.0",
        "armed_at_ict": plan["generated_at_ict"],
        "date_ict": plan["date_ict"],
        "room_name": room_name,
        "recurring_weekdays": bool(recurring_weekdays),
        "is_trading_day": plan["is_trading_day"],
        "market_status_code": plan["market_status_code"],
        "next_trading_day": plan["next_trading_day"],
        "armed_slots": [
            {"time": s["time"], "slot_id": s["slot_id"], "cron_expr": s["cron_expr"], "title": s["title"]}
            for s in plan["upcoming_slots"]
        ],
        "skipped_passed_slots": [s["time"] for s in plan["passed_slots"]],
    }
    STATE_OUT.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE_OUT.with_suffix(".tmp")
    tmp.write_text(json.dumps(state_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(STATE_OUT)
    return {**plan, "state_saved_to": str(STATE_OUT), "recurring_weekdays": bool(recurring_weekdays)}


def main():
    parser = argparse.ArgumentParser(description="James Daily Ops 8-Slot Activator")
    parser.add_argument("--plan-json", action="store_true", help="In kế hoạch các mốc còn lại hôm nay (JSON)")
    parser.add_argument("--arm-today", action="store_true", help="Ghi trạng thái kích hoạt hôm nay & in JSON các mốc cần schedule")
    parser.add_argument("--room", type=str, default="JAMES_ANTIGRAVITY_CHAT")
    args = parser.parse_args()

    if args.arm_today:
        res = arm_daily_ops_in_james(room_name=args.room)
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return

    res = get_daily_ops_schedule_plan()
    print(json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
