#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MASTER ORCHESTRATOR v6.0: Closed-Loop 7-Department Institutional Pipeline (`run_daily_pipeline.py`)
Coordinates all 7 Departments + Automated Gatekeeper seamlessly:
- Step 1: Ban 1 & Ban 2 Global Market & Fundamental Scanner (`market_data_fetcher.py`)
- Step 2: Ban 3 Cross-Department Synthesis & Zero-Hallucination Auditor (`audit_and_verify.py`)
- Step 3: Ban 4 Quantitative Portfolio Risk, Correlation & Stress-Test Engine (`quant_portfolio_engine.py`)
- Step 4: Ban 5 Walk-Forward Attribution & Adaptive Calibration (`performance_learning_engine.py`)
- Step 5: Ban 6 Investor Academy, 35-Stock Case Studies & VN Localization (`mentor_engine.py`)
- Step 6: Ban 7 Daily Investment Specialist "Alex" (`daily_investment_specialist.py`)
- Step 7: Part 4 Automated Pipeline Gatekeeper & Report Synchronizer (`pipeline_gatekeeper.py`)
- Step 8: Compile Interactive HTML Command Center Dashboard (`generate_dashboard.py`)
"""

import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"


def run_step(script_name: str, extra_args: list[str] | None = None) -> None:
    cmd = [sys.executable, str(SCRIPTS_DIR / script_name)] + (extra_args or [])
    res = subprocess.run(cmd, cwd=str(BASE_DIR))
    if res.returncode != 0:
        raise RuntimeError(f"Script {script_name} exited with code {res.returncode}")


def main() -> None:
    print("=" * 78)
    print(" HỆ THỐNG ĐIỀU PHỐI 7 PHÒNG BAN KHÉP KÍN (v6.0 AUDITED ZERO-DEFECT PIPELINE)")
    print("=" * 78)

    fast_mode = "--fast" in sys.argv
    run_step("market_data_fetcher.py", ["--recompute-only"] if fast_mode else [])
    run_step("audit_and_verify.py")
    run_step("quant_portfolio_engine.py")
    run_step("performance_learning_engine.py")
    run_step("mentor_engine.py")
    run_step("daily_investment_specialist.py")
    run_step("pipeline_gatekeeper.py")
    run_step("generate_dashboard.py")

    print("=" * 78)
    print(" [HOÀN TẤT 100%] CẢ 7 PHÒNG BAN & GATEKEEPER ĐÃ ĐỒNG BỘ DỮ LIỆU, BÁO CÁO & DASHBOARD v6.0!")
    print("=" * 78)


if __name__ == "__main__":
    main()
