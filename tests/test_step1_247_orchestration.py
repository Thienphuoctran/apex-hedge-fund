#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KIỂM ĐỊNH TÍCH HỢP BƯỚC 1 (CÔNG VIỆC 2): TRÁI TIM ĐIỀU PHỐI 17 CỘT MỐC & VÒNG LẶP TỰ HỌC 24/24
File: tests/test_step1_247_orchestration.py
"""

import sys
import json
import datetime
import unittest
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.morning_war_room_hearing import conduct_morning_war_room
from scripts.eod_master_audit_engine import run_eod_master_audit
from scripts.eod_late_night_executive_council import run_council
import scripts.apex_institutional_cron_daemon as cron_daemon


class TestStep1OrchestrationAndSelfLearning(unittest.TestCase):

    def setUp(self):
        self.today_str = datetime.datetime.now().strftime("%Y-%m-%d")

    def test_01_daemon_source_zero_contradictions(self):
        """Đảm bảo mã nguồn apex_institutional_cron_daemon.py không còn text mẫu mâu thuẫn '100% TIỀN MẶT' hay lỗi thiếu DATA_DIR."""
        daemon_src = (BASE_DIR / "scripts" / "apex_institutional_cron_daemon.py").read_text(encoding="utf-8")
        self.assertNotIn("100% TIỀN MẶT", daemon_src)
        self.assertNotIn("Bán hết 100% 900 CP", daemon_src)
        self.assertIn("DATA_DIR = BASE_DIR / \"data\"", daemon_src)
        self.assertEqual(len(cron_daemon.SCHEDULED_MILESTONES), 17)

    def test_02_eod_master_audit_closed_loop(self):
        """Kiểm tra động cơ phúc tra EOD chạy thật và sinh biên bản sửa đổi cho Minh Quân & Alex."""
        res = run_eod_master_audit(audit_date=self.today_str)
        self.assertIn("minh_quan_audit", res)
        self.assertIn("alex_audit", res)
        self.assertGreaterEqual(res["minh_quan_audit"]["score"], 80.0)

        feedback_json = BASE_DIR / "08_Master_Investment_CIO" / "eod_audit_logs" / f"{self.today_str}_eod_audit_feedback.json"
        self.assertTrue(feedback_json.exists())

    def test_03_morning_war_room_dynamic_feedback_injection(self):
        """Kiểm tra Giao ban 8h30 sáng tự động đọc lỗi EOD và Kho bộ nhớ ngữ cảnh Ban 5."""
        res = conduct_morning_war_room()
        self.assertEqual(res["status"], "SUCCESS")
        self.assertGreaterEqual(res["mistakes_reviewed"], 4)
        self.assertEqual(res["guardrails_active"], 5)
        self.assertEqual(res["positions_count"], 3)

        pact_path = Path(res["pact_file"])
        self.assertTrue(pact_path.exists())
        pact_text = pact_path.read_text(encoding="utf-8")
        self.assertIn("EOD AUDIT", pact_text)
        self.assertIn("MEM-VN-001", pact_text)
        self.assertIn("HPG", pact_text)
        self.assertIn("TCB", pact_text)
        self.assertIn("MBB", pact_text)

    def test_04_eod_2300_council_dynamic_telemetry(self):
        """Kiểm tra Hội nghị 23h00 đọc số liệu động từ Telemetry & EOD Audit, không còn ngày cố định 04/11/2026."""
        code = run_council(target_date=self.today_str)
        self.assertEqual(code, 0)

        ledger_path = BASE_DIR / "08_Master_Investment_CIO" / "23h00_council_ledger.json"
        self.assertTrue(ledger_path.exists())
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        self.assertEqual(ledger["meeting_date"], self.today_str)
        self.assertIn("eod_audit_summary", ledger)
        self.assertEqual(len(ledger["financial_snapshot"]["holdings"]), 3)

        doc_path = BASE_DIR / "08_Master_Investment_CIO" / f"{self.today_str}_23h00_EOD_Executive_Council_Meeting.md"
        self.assertTrue(doc_path.exists())
        doc_text = doc_path.read_text(encoding="utf-8")
        self.assertNotIn("04/11/2026", doc_text)
        self.assertIn(self.today_str, doc_text)

    def test_05_cron_daemon_milestones_dry_run(self):
        """Chạy thử các cột mốc trọng tâm (06:00, 11:45, 13:00, 14:25, 23:00) ở chế độ DRY_RUN."""
        cron_daemon.DRY_RUN_MODE = True
        for m_id in ["06:00", "11:45", "13:00", "14:25", "23:00"]:
            ok = cron_daemon.execute_milestone(m_id)
            self.assertTrue(ok, f"Milestone {m_id} failed in dry-run!")

        cbtt_file = BASE_DIR / "VN_Market" / "02_BCTC_Equity_Research" / f"{self.today_str}_VN_CBTT_Radar.md"
        flash_file = BASE_DIR / "VN_Market" / "03_Synthesis_Memos" / f"{self.today_str}_Morning_Flash_Report.md"
        t2_file = BASE_DIR / "09_Realtime_Portfolio_Sentinel" / f"{self.today_str}_T2_Pressure_Radar.md"
        guard3_file = BASE_DIR / "VN_Market" / "04_Investment_Committee" / f"{self.today_str}_GUARD03_Pre_ATC_Lock.md"

        for f in [cbtt_file, flash_file, t2_file, guard3_file]:
            self.assertTrue(f.exists(), f"Missing output file: {f}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
