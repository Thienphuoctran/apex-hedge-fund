#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APEX ENTERPRISE V7.0 MASTER ARCHITECTURE VERIFICATION SUITE
File: tests/test_v7_master_architecture.py
"""

import ast
import json
import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


class TestApexV7MasterArchitecture(unittest.TestCase):
    def test_01_full_universe_145_real_bctc_and_zero_unverified_buy_leak(self):
        bctc = json.loads((ROOT_DIR / "VN_Market" / "data" / "vn_real_bctc_live.json").read_text(encoding="utf-8-sig"))
        cov = bctc.get("coverage_stats") or {}
        req = int(cov.get("requested_vn_tickers") or 0)
        ver = int(cov.get("bctc_verified_count") or 0)
        self.assertGreaterEqual(req, 145)
        self.assertGreaterEqual(ver, 135)
        self.assertGreaterEqual(float(cov.get("universe_coverage_pct") or 0.0), 95.0)

        scan = json.loads((ROOT_DIR / "VN_Market" / "data" / "vn_full_market_scan.json").read_text(encoding="utf-8-sig"))
        stocks = scan.get("stocks") or {}
        for sym in (scan.get("top_12_diversified_actionable_discoveries") or []):
            self.assertTrue((stocks.get(sym) or {}).get("bctc_verified", False), f"{sym} leaked without verified BCTC")

        # CTS must reflect real ROE (~3.93%), not old fake AA tier
        if "CTS" in stocks:
            self.assertLess(float(stocks["CTS"].get("roe_pct") or 0.0), 6.0)

    def test_02_brain_v4_beats_v3_empirically_and_zero_stale_hardcodes(self):
        cal = json.loads((ROOT_DIR / "data" / "apex_empirical_calibration.json").read_text(encoding="utf-8-sig"))
        v4_cal = cal.get("apex_v4_sector_alpha") or {}
        v3_cal = cal.get("apex_v3_asymmetric_conviction") or {}
        self.assertGreater(float(v4_cal.get("total_return_pct") or -999), float(v3_cal.get("total_return_pct") or 999))
        self.assertGreaterEqual(float(v4_cal.get("max_drawdown_pct") or -100), -12.5)
        self.assertGreaterEqual(float(v4_cal.get("sharpe_ratio") or 0), 0.5)

        v4_raw = (ROOT_DIR / "data" / "apex_brain_v4_output.json").read_text(encoding="utf-8-sig")
        for stale in ("BAF & MSH", "20/11", "HDB & MSH"):
            self.assertNotIn(stale, v4_raw)
        v4 = json.loads(v4_raw)
        for cand in (v4.get("tactical_round2_candidates") or []):
            self.assertLessEqual(float(cand.get("max_nav_risk_pct") or 99), 1.6)
            self.assertGreaterEqual(float(cand.get("rr_ratio_tp1") or 0), 2.0)

    def test_03_constitution_v2_12_gates_and_violation_catch(self):
        from scripts.apex_constitution_enforcer import ApexConstitutionEnforcer

        res = ApexConstitutionEnforcer.run_12_constitutional_gates(base_dir=ROOT_DIR)
        failed = [g["gate_id"] for g in res.get("gates", []) if not g.get("passed")]
        self.assertTrue(res.get("all_passed"), f"Failed constitutional gates: {failed}")
        self.assertEqual(res.get("passed_count"), 12)
        self.assertEqual(res.get("status"), "PASS_ALL_12")

        # MWG lot-100 (~7.09M) > 33% of 20.05M NAV -> must block cleanly when order_hour overrides holiday short-circuit
        ok_mwg, msg_mwg = ApexConstitutionEnforcer.pre_flight_order_gatekeeper("MWG", 70900.0, order_hour=14, order_minute=10)
        self.assertFalse(ok_mwg)
        self.assertIn("33%", msg_mwg)

        # Unverified BCTC block -> UNVERIFIED_BLOCKED
        ok_unv, msg_unv = ApexConstitutionEnforcer.pre_flight_order_gatekeeper(
            "TPB", 12350.0, order_hour=14, order_minute=10, is_verified_bctc=False
        )
        self.assertFalse(ok_unv)
        self.assertIn("UNVERIFIED_BLOCKED", msg_unv)

    def test_04_scbp_sha256_single_source_sync_and_ssot_invariants(self):
        ssot = json.loads((ROOT_DIR / "data" / "current_portfolio_state.json").read_text(encoding="utf-8-sig"))
        self.assertEqual(ssot.get("account_id"), "105C307855")
        self.assertAlmostEqual(float(ssot.get("cash_balance_vnd")), 15541117.0, delta=1.0)
        self.assertAlmostEqual(float(ssot.get("total_nav_vnd")), 20051117.0, delta=1.0)

        scbp = json.loads((ROOT_DIR / "data" / "canonical_executive_briefing.json").read_text(encoding="utf-8-sig"))
        seal = str(scbp.get("sha256_seal") or "")
        self.assertEqual(len(seal), 64)

        state_md = (ROOT_DIR / "00_LIVE_INTER_CHAT_STATE.md").read_text(encoding="utf-8")
        palmer = json.loads((ROOT_DIR / "data" / "palmer_live_briefing.json").read_text(encoding="utf-8-sig"))
        self.assertIn(seal, state_md)
        self.assertEqual(palmer.get("scbp_sha256"), seal)

        ledger = json.loads((ROOT_DIR / "data" / "real_performance_ledger.json").read_text(encoding="utf-8-sig"))
        self.assertEqual(ledger.get("account_id"), "105C307855")
        self.assertEqual(ledger.get("open_positions_count"), len(ssot.get("active_positions") or {}))

    def test_05_telegram_room_mute_toggle_and_restore(self):
        from scripts.telegram_dispatcher import (
            get_room_telegram_controls,
            set_room_telegram_mute,
            should_block_outbound_telegram,
        )

        orig = bool(get_room_telegram_controls().get("team_victor", {}).get("muted", False))
        try:
            set_room_telegram_mute("team_victor", True)
            blocked, reason = should_block_outbound_telegram(is_intraday_alert=False, priority="NORMAL", topic_key="alerts")
            self.assertTrue(blocked)
            self.assertEqual(reason, "ROOM_MUTED:team_victor")

            # Critical emergency stop override still works
            blk_crit, _ = should_block_outbound_telegram(is_intraday_alert=True, priority="CRITICAL_STOP", topic_key="alerts")
            self.assertFalse(blk_crit)

            set_room_telegram_mute("team_victor", False)
            blk_after, rsn_after = should_block_outbound_telegram(is_intraday_alert=False, priority="NORMAL", topic_key="alerts")
            self.assertFalse(blk_after)
            self.assertEqual(rsn_after, "ALLOWED")
        finally:
            set_room_telegram_mute("team_victor", orig)

    def test_06_eight_permanent_automations_valid_and_wildcard_free(self):
        expected = [
            ("apex-daily-preato-0830", "CRON_TZ=Asia/Ho_Chi_Minh 30 8 * * 1-5"),
            ("apex-daily-warroom-0900", "CRON_TZ=Asia/Ho_Chi_Minh 0 9 * * 1-5"),
            ("apex-daily-noon-1135", "CRON_TZ=Asia/Ho_Chi_Minh 35 11 * * 1-5"),
            ("apex-daily-afternoon-1300", "CRON_TZ=Asia/Ho_Chi_Minh 0 13 * * 1-5"),
            ("apex-daily-prep14h-1330", "CRON_TZ=Asia/Ho_Chi_Minh 30 13 * * 1-5"),
            ("apex-daily-goldenhour-1405", "CRON_TZ=Asia/Ho_Chi_Minh 5 14 * * 1-5"),
            ("apex-daily-preatc-1420", "CRON_TZ=Asia/Ho_Chi_Minh 20 14 * * 1-5"),
            ("apex-daily-eod-1545", "CRON_TZ=Asia/Ho_Chi_Minh 45 15 * * 1-5"),
        ]
        sidecars_root = Path.home() / ".gemini" / "config" / "sidecars"
        for name, expected_cron in expected:
            sp = sidecars_root / name / "sidecar.json"
            self.assertTrue(sp.exists(), f"Missing sidecar {sp}")
            data = json.loads(sp.read_text(encoding="utf-8"))
            self.assertEqual(data.get("builtin"), "schedule")
            self.assertEqual(data.get("restart_policy"), "always")
            self.assertEqual((data.get("args") or [None])[0], expected_cron)
            grants = ((data.get("agent_permissions") or {}).get("access_grants") or [])
            self.assertTrue(len(grants) >= 5)
            for g in grants:
                self.assertNotIn("*", str(g), f"Wildcard forbidden in {name}: {g}")

    def test_07_cloud_modules_pure_stdlib_memory_guard(self):
        banned = {"pandas", "numpy", "yfinance", "requests", "scipy", "sklearn", "torch"}
        pure_modules = [
            "scripts/vn_market_calendar.py",
            "scripts/apex_canonical_truth.py",
            "scripts/apex_virtual_office_engine.py",
            "scripts/apex_unified_briefing_builder.py",
            "scripts/james_daily_ops_activator.py",
        ]
        for rel in pure_modules:
            src = (ROOT_DIR / rel).read_text(encoding="utf-8")
            tree = ast.parse(src, filename=rel)
            imports = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.update(a.name.split(".")[0] for a in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.add(node.module.split(".")[0])
            self.assertEqual(imports & banned, set(), f"{rel} has heavy imports: {imports & banned}")

    def test_08_james_daily_ops_one_phrase_activation(self):
        import datetime as _dt
        from scripts.james_daily_ops_activator import get_daily_ops_schedule_plan
        from scripts.master_cio_james_agent import handle_james_chat

        ict = _dt.timezone(_dt.timedelta(hours=7))
        # Early morning 01:57 on Wednesday 2026-11-25 -> all 8 slots upcoming
        plan_morning = get_daily_ops_schedule_plan(now_ict=_dt.datetime(2026, 11, 25, 1, 57, tzinfo=ict))
        self.assertTrue(plan_morning["is_trading_day"])
        self.assertEqual(plan_morning["upcoming_count"], 8)
        self.assertEqual(plan_morning["passed_count"], 0)

        # Mid-day 13:15 on Wednesday 2026-11-25 -> 4 slots passed (08:30..13:00), 4 remaining (13:30..15:45)
        plan_mid = get_daily_ops_schedule_plan(now_ict=_dt.datetime(2026, 11, 25, 13, 15, tzinfo=ict))
        self.assertEqual(plan_mid["upcoming_count"], 4)
        self.assertEqual([s["time"] for s in plan_mid["upcoming_slots"]], ["13:30", "14:05", "14:20", "15:45"])

        # Skill file exists & has all 8 crons
        skill_p = ROOT_DIR / ".agents" / "skills" / "james-daily-ops-activation" / "SKILL.md"
        self.assertTrue(skill_p.exists())
        skill_txt = skill_p.read_text(encoding="utf-8")
        for expr in ("30 8 * * 1-5", "0 9 * * 1-5", "35 11 * * 1-5", "0 13 * * 1-5", "30 13 * * 1-5", "5 14 * * 1-5", "20 14 * * 1-5", "45 15 * * 1-5"):
            self.assertIn(expr, skill_txt)

        # handle_james_chat activation phrase works
        reply = handle_james_chat("hãy bật tác vụ tác chiến trong ngày")
        self.assertIn("KÍCH HOẠT TÁC VỤ TÁC CHIẾN TRONG NGÀY", reply)
        self.assertTrue((ROOT_DIR / "data" / "james_daily_ops_schedule_state.json").exists())


if __name__ == "__main__":
    unittest.main()
