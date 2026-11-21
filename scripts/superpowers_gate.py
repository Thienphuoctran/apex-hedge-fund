#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SUPERPOWERS 24/7 VERIFICATION GATE & SYSTEMATIC DIAGNOSTICS (APEX HEDGE FUND)
File: scripts/superpowers_gate.py
Cơ quan sử dụng: Ban 12 (Trọng - Ombudsman), Ban 8 (James), Ban 10 (Hiền)
"""

import json
import datetime
import traceback
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
DIAGNOSTICS_FILE = BASE_DIR / "data" / "superpowers_diagnostics.jsonl"


def diagnose_exception(component: str, exc: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Ghi nhận lỗi theo chuẩn systematic-debugging thay cho im lặng nuốt lỗi."""
    err_type = type(exc).__name__
    err_msg = str(exc)
    hint = "Kiểm tra kết nối mạng, cấu trúc JSON hoặc quyền đọc/ghi tệp."
    lower_msg = err_msg.lower()
    if "401" in lower_msg or "unauthorized" in lower_msg or "api_key" in lower_msg:
        hint = "Kiểm tra lại API key trong .env hoặc Secrets môi trường Cloud."
    elif "timeout" in lower_msg or "timed out" in lower_msg:
        hint = "Nguồn ngoài phản hồi chậm; dùng fallback dữ liệu nội bộ."
    elif "409" in lower_msg or "conflict" in lower_msg:
        hint = "Xung đột polling trùng Bot Token Telegram; giữ duy nhất 1 daemon."

    record = {
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        "component": component,
        "error_type": err_type,
        "error_message": err_msg[:400],
        "remediation_hint": hint,
        "context": context or {},
        "traceback_tail": traceback.format_exc(limit=3)[-500:],
    }
    try:
        DIAGNOSTICS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(DIAGNOSTICS_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        pass
    return record


def verify_report_readiness(
    source_name: str,
    payload: Any,
    required_keys: Optional[Iterable[str]] = None,
    file_path_for_freshness: Optional[Path] = None,
    max_age_hours: float = 48.0,
) -> Dict[str, Any]:
    """Chốt verification-before-completion cho toàn bộ báo cáo 24/7 của các phòng ban."""
    checks: List[str] = []
    failures: List[str] = []

    if payload is None or (isinstance(payload, (dict, list, str)) and len(payload) == 0):
        failures.append(f"{source_name}: payload rỗng hoặc None")
    else:
        checks.append(f"{source_name}: có dữ liệu")

    if required_keys and isinstance(payload, dict):
        missing = [k for k in required_keys if k not in payload]
        if missing:
            failures.append(f"{source_name}: thiếu trường {missing}")
        else:
            checks.append(f"{source_name}: đủ trường bắt buộc")

    if file_path_for_freshness is not None:
        if not file_path_for_freshness.exists():
            failures.append(f"{source_name}: thiếu tệp {file_path_for_freshness.name}")
        else:
            age_hours = (datetime.datetime.now().timestamp() - file_path_for_freshness.stat().st_mtime) / 3600.0
            if age_hours > max_age_hours:
                failures.append(f"{source_name}: dữ liệu cũ ({age_hours:.1f}h > {max_age_hours}h)")
            else:
                checks.append(f"{source_name}: độ tươi đạt chuẩn ({age_hours:.1f}h)")

    return {
        "source": source_name,
        "passed": len(failures) == 0,
        "checks": checks,
        "failures": failures,
        "verified_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def check_247_readiness() -> Dict[str, Any]:
    from scripts.tavily_bridge import load_tavily_api_key

    ssot_file = BASE_DIR / "data" / "current_portfolio_state.json"
    cbtt_file = BASE_DIR / "data" / "cbtt_live_radar.json"

    has_tavily = bool(load_tavily_api_key())
    ssot_gate = verify_report_readiness(
        "SSOT_Portfolio",
        json.loads(ssot_file.read_text(encoding="utf-8")) if ssot_file.exists() else None,
        required_keys=["cash_balance_vnd", "total_nav_vnd"],
        file_path_for_freshness=ssot_file,
        max_age_hours=720.0,
    )
    cbtt_gate = verify_report_readiness(
        "CBTT_Radar",
        json.loads(cbtt_file.read_text(encoding="utf-8")) if cbtt_file.exists() else None,
        required_keys=["scan_date"],
        file_path_for_freshness=cbtt_file,
        max_age_hours=72.0,
    )

    diag_count = 0
    if DIAGNOSTICS_FILE.exists():
        try:
            diag_count = len(DIAGNOSTICS_FILE.read_text(encoding="utf-8", errors="ignore").splitlines())
        except Exception:
            pass

    return {
        "tavily_api_ready": has_tavily,
        "ssot_gate": ssot_gate,
        "cbtt_gate": cbtt_gate,
        "diagnostics_logged_events": diag_count,
        "overall_ok": has_tavily and ssot_gate["passed"],
    }
