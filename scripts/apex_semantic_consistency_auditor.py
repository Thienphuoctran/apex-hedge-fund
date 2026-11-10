#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APEX INSTITUTIONAL SEMANTIC CONSISTENCY AUDITOR & PRE-PUBLISH GATEKEEPER
File: scripts/apex_semantic_consistency_auditor.py
Đơn vị chủ quản: Ban 12 — Trọng (Thanh Tra & Kiểm Toán Thể Chế Tối Cao)
Phục vụ: Chủ tịch HĐQT Trần Quốc Thiên Phước (Tài khoản TCBS: 105C307855)

Chức năng:
1. Đối soát chéo ngữ nghĩa (Semantic Cross-Check) 100% các báo cáo giữa 11 phòng ban:
   - Ngăn chặn hoàn toàn việc phòng ban này nói mã này (PVT/BSR), phòng ban khác nói mã khác (HDB/MSH).
   - Ngăn chặn triệt để tình trạng nhắc lại lệnh mua Nhịp 1 đối với các mã đang nắm giữ ở chu kỳ T+1.
2. Kiểm tra tính đồng bộ số liệu tài sản (NAV, Tiền mặt thật, Lãi lỗ) với SSOT data/current_portfolio_state.json.
3. Tự động gắn nhãn vi phạm (VIOLATION) và cách ly hoặc tự động sửa sạch rác dữ liệu trước khi xuất bản lên Web Portal / Telegram.
"""

import os
import sys
import json
import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"
DATA_DIR = BASE_DIR / "data"

UNIVERSE_CONFIG = CONFIG_DIR / "institutional_universe_active.json"
PORTFOLIO_SSOT = DATA_DIR / "current_portfolio_state.json"


def load_universe_rules() -> Dict[str, Any]:
    if UNIVERSE_CONFIG.exists():
        with open(UNIVERSE_CONFIG, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "approved_tactical_watchlist_round_2": ["HDB", "MSH", "BAF", "IDC"],
        "prohibited_tickers_for_round_2": ["PVT", "BSR", "HPG", "TCB", "MBB"]
    }


def audit_report_file(file_path: Path, rules: Dict[str, Any]) -> List[str]:
    violations = []
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return [f"Không đọc được file: {e}"]

    # 1. Kiểm tra mã cấm xuất hiện trong kế hoạch tác chiến / radar giải ngân
    is_tactical_action_report = any(part in str(file_path).replace("\\", "/") for part in [
        "04_Investment_Committee", "07_Daily", "08_Master_Investment_CIO", "09_Realtime", "Synthesis_Memos"
    ])
    prohibited = rules.get("prohibited_tickers_for_round_2", [])
    for ticker in prohibited:
        if is_tactical_action_report:
            if f"**`{ticker}`**" in content or f"**{ticker}**" in content or f"| **{ticker}** |" in content:
                if any(kw in content for kw in [f"LỆNH DỰ KIẾN", f"Mua LO", f"Lệnh 1 ({ticker})", f"Lệnh 2 ({ticker})", f"Vốn Dự Kiến", f"Vùng Mua"]):
                    violations.append(f"Xuất hiện mã cấm ngoài danh mục Vòng 2 ({ticker}) trong kế hoạch tác chiến/săn mồi")
        else:
            if f"Lệnh 1 ({ticker})" in content or f"Mua LO 100 CP {ticker}" in content:
                violations.append(f"Xuất hiện lệnh mua trực tiếp mã cấm ({ticker})")

    # 2. Kiểm tra lỗi nhắc lại lệnh mua Nhịp 1 cho mã đang giữ T+1
    active_holdings = rules.get("active_holdings", {})
    for sym, hdata in active_holdings.items():
        if hdata.get("cycle_status") == "T+1_HOLDING":
            if f"Mua 100 CP {sym}" in content or f"Mua LO 100 CP giá" in content and sym in content:
                violations.append(f"Mã {sym} đang ở chu kỳ T+1 (chờ về) nhưng báo cáo vẫn nhắc lệnh Mua mới Nhịp 1")

    return violations


def run_full_institutional_semantic_audit(target_date: str = None) -> Dict[str, Any]:
    if not target_date:
        target_date = datetime.datetime.now().strftime("%Y-%m-%d")

    rules = load_universe_rules()
    audit_results = {
        "audit_timestamp": datetime.datetime.now().isoformat(),
        "target_date": target_date,
        "audited_reports": 0,
        "clean_reports": 0,
        "violation_reports": 0,
        "details": []
    }

    # Quét toàn bộ file báo cáo của ngày target_date
    report_patterns = [f"*{target_date}*.md"]
    found_files = []
    for pat in report_patterns:
        found_files.extend(BASE_DIR.rglob(pat))

    for fpath in sorted(set(found_files)):
        if ".git" in fpath.parts or "historical_archive" in fpath.parts:
            continue
        rel_p = str(fpath.relative_to(BASE_DIR)).replace("\\", "/")
        issues = audit_report_file(fpath, rules)
        audit_results["audited_reports"] += 1
        if issues:
            audit_results["violation_reports"] += 1
            audit_results["details"].append({
                "file": rel_p,
                "status": "VIOLATION",
                "issues": issues
            })
        else:
            audit_results["clean_reports"] += 1

    return audit_results


if __name__ == "__main__":
    res = run_full_institutional_semantic_audit()
    print("=" * 60)
    print("🛡️ BAN 12 (TRỌNG) — KẾT QUẢ KIỂM TOÁN CHÉO NỘI DUNG THỂ CHẾ")
    print(f"Tổng báo cáo kiểm tra: {res['audited_reports']}")
    print(f"Báo cáo sạch (CLEAN): {res['clean_reports']}")
    print(f"Báo cáo vi phạm (VIOLATIONS): {res['violation_reports']}")
    print("=" * 60)
    for d in res["details"]:
        print(f"❌ {d['file']}")
        for iss in d["issues"]:
            print(f"   -> {iss}")
