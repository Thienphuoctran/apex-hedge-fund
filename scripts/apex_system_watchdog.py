#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APEX V7.0 SYSTEM WATCHDOG & INTEGRITY GUARD
File: scripts/apex_system_watchdog.py

Giám sát sức khỏe toàn hệ thống V7.0:
- Kiểm tra Web Portal 127.0.0.1:8000 (hoặc chế độ --skip-http khi test offline)
- Kiểm tra Kho BCTC 145/145 mã, JSON integrity (utf-8-sig), SCBP SHA-256 sync
- Kiểm tra đủ 8 Automations sidecar.json thường trực
- TUYỆT ĐỐI KHÔNG can thiệp Eco/Travel, chroma-mcp hay telegram_ai_copilot.py
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path
from typing import Any, Dict, List

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from scripts.vn_market_calendar import get_ict_now

EXPECTED_8_SIDECARS = [
    "apex-daily-preato-0830",
    "apex-daily-warroom-0900",
    "apex-daily-noon-1135",
    "apex-daily-afternoon-1300",
    "apex-daily-prep14h-1330",
    "apex-daily-goldenhour-1405",
    "apex-daily-preatc-1420",
    "apex-daily-eod-1545",
]


def run_watchdog_check(check_http: bool = True, port: int = 8000) -> Dict[str, Any]:
    now_ict = get_ict_now()
    issues: List[str] = []

    # 1. JSON stores integrity (utf-8-sig safe for PowerShell backup files)
    corrupt_jsons: List[str] = []
    for folder in [BASE_DIR / "data", BASE_DIR / "VN_Market" / "data"]:
        if folder.exists():
            for jf in folder.glob("*.json"):
                try:
                    json.loads(jf.read_text(encoding="utf-8-sig"))
                except Exception:
                    corrupt_jsons.append(jf.name)
    if corrupt_jsons:
        issues.append(f"Corrupt JSON stores: {corrupt_jsons[:5]}")

    # 2. BCTC 145/145 verified check
    bctc_path = BASE_DIR / "VN_Market" / "data" / "vn_real_bctc_live.json"
    bctc_ver = 0
    bctc_req = 0
    if bctc_path.exists():
        bctc_data = json.loads(bctc_path.read_text(encoding="utf-8-sig"))
        cov = bctc_data.get("coverage_stats") or {}
        bctc_ver = int(cov.get("bctc_verified_count") or 0)
        bctc_req = int(cov.get("requested_vn_tickers") or 145)
        if bctc_ver < 135:
            issues.append(f"Low BCTC coverage: {bctc_ver}/{bctc_req}")
    else:
        issues.append("Missing vn_real_bctc_live.json")

    # 3. SCBP SHA-256 sync check
    scbp_path = BASE_DIR / "data" / "canonical_executive_briefing.json"
    state_md_path = BASE_DIR / "00_LIVE_INTER_CHAT_STATE.md"
    scbp_seal = ""
    if scbp_path.exists() and state_md_path.exists():
        scbp = json.loads(scbp_path.read_text(encoding="utf-8-sig"))
        scbp_seal = str(scbp.get("sha256_seal") or "")
        state_txt = state_md_path.read_text(encoding="utf-8", errors="ignore")
        if not scbp_seal or scbp_seal not in state_txt:
            issues.append("SCBP SHA-256 not synced in 00_LIVE_INTER_CHAT_STATE.md")
    else:
        issues.append("Missing canonical_executive_briefing.json or 00_LIVE_INTER_CHAT_STATE.md")

    # 4. 8 Permanent Automations sidecar.json check
    sidecars_root = Path.home() / ".gemini" / "config" / "sidecars"
    valid_sidecars: List[str] = []
    missing_sidecars: List[str] = []
    for s_name in EXPECTED_8_SIDECARS:
        sp = sidecars_root / s_name / "sidecar.json"
        if not sp.exists():
            missing_sidecars.append(s_name)
            continue
        try:
            sd = json.loads(sp.read_text(encoding="utf-8"))
            grants = ((sd.get("agent_permissions") or {}).get("access_grants") or [])
            has_wildcard = any("*" in str(g) for g in grants)
            if sd.get("builtin") == "schedule" and not has_wildcard:
                valid_sidecars.append(s_name)
            else:
                issues.append(f"Invalid sidecar schema/wildcard: {s_name}")
        except Exception:
            issues.append(f"Corrupt sidecar.json: {s_name}")
    if missing_sidecars:
        issues.append(f"Missing sidecars: {missing_sidecars}")

    # 5. Live Portal HTTP check (optional)
    portal_http_ok = None
    if check_http:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/system/health_v7", timeout=4) as resp:
                portal_http_ok = (resp.status == 200)
                if not portal_http_ok:
                    issues.append(f"Portal HTTP status={resp.status}")
        except Exception as e:
            portal_http_ok = False
            issues.append(f"Portal HTTP unreachable on :{port} ({e})")

    return {
        "ok": len(issues) == 0,
        "checked_at_ict": now_ict.strftime("%Y-%m-%d %H:%M:%S ICT"),
        "bctc_verified": f"{bctc_ver}/{bctc_req}",
        "scbp_seal": scbp_seal[:16],
        "valid_sidecars_count": len(valid_sidecars),
        "expected_sidecars_count": len(EXPECTED_8_SIDECARS),
        "portal_http_ok": portal_http_ok,
        "issues": issues,
    }


def main():
    parser = argparse.ArgumentParser(description="Apex V7.0 System Watchdog")
    parser.add_argument("--check-http", action="store_true", help="Kiểm tra luôn HTTP 200 của Web Portal đang chạy")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    res = run_watchdog_check(check_http=args.check_http, port=args.port)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    if not res["ok"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
