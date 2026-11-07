#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UNIT TEST SUITE FOR APEX AGENT ZERO ENGINE
File: tests/test_agent_zero_engine.py
Kiểm thử tự động 100% 4 trụ cột lõi của Agent Zero Engine
"""

import sys
import unittest
from pathlib import Path

# Đảm bảo import được module
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.apex_agent_zero_engine import (
    ZeroBrowserScout,
    ZeroForensicParser,
    ZeroForensicAuditor,
    DynamicCodeSandbox,
    ApexAgentZeroController
)


class TestApexAgentZeroEngine(unittest.TestCase):

    def setUp(self):
        self.controller = ApexAgentZeroController()
        self.scout = self.controller.scout
        self.parser = self.controller.parser
        self.auditor = self.controller.auditor
        self.sandbox = self.controller.sandbox

    # --- PILLAR 1: BROWSER SCOUT ---
    def test_browser_headers_generation(self):
        headers = self.scout._get_headers()
        self.assertIn("User-Agent", headers)
        self.assertTrue(len(headers["User-Agent"]) > 20)
        self.assertIn("Accept-Language", headers)

    def test_sbv_indicators_structure(self):
        sbv = self.scout.crawl_sbv_indicators()
        self.assertIn("central_rate_usd_vnd", sbv)
        self.assertIn("refinancing_rate", sbv)
        self.assertTrue(23000 <= sbv["central_rate_usd_vnd"] <= 26000)
        self.assertEqual(sbv["refinancing_rate"], 4.5)

    # --- PILLAR 2: FORENSIC PARSER ---
    def test_parser_availability(self):
        self.assertTrue(self.parser.pypdf_available, "pypdf should be available")

    def test_metric_extraction_regex(self):
        sample_text = (
            "1. Doanh thu thuần về bán hàng: 62.214.123.000\n"
            "2. Lợi nhuận sau thuế thu nhập doanh nghiệp: 8.217.456.000\n"
            "3. Lưu chuyển tiền thuần từ hoạt động kinh doanh: (1.500.000.000)\n"
        )
        rev = self.parser.extract_metric_from_text(sample_text, [r"Doanh thu thuần"])
        self.assertEqual(rev, 62214123000.0)

        lnst = self.parser.extract_metric_from_text(sample_text, [r"Lợi nhuận sau thuế"])
        self.assertEqual(lnst, 8217456000.0)

        # Kiểm tra số âm trong ngoặc
        ocf = self.parser.extract_metric_from_text(sample_text, [r"Lưu chuyển tiền thuần từ hoạt động kinh doanh"])
        self.assertEqual(ocf, -1500000000.0)

    # --- PILLAR 3: FORENSIC AUDITOR ---
    def test_cash_flow_quality_audit(self):
        # Trường hợp HPG: OCF > LNST (Tiền thật)
        audit_hpg = self.auditor.audit_cash_flow_quality(ocf=8866.0, lnst=8217.0)
        self.assertTrue(audit_hpg["is_real_cash"])
        self.assertEqual(audit_hpg["quality_grade"], "SOLID_PASS")

        # Trường hợp Lợi nhuận giấy: LNST > 0 nhưng OCF âm
        audit_bad = self.auditor.audit_cash_flow_quality(ocf=-500.0, lnst=1000.0)
        self.assertFalse(audit_bad["is_real_cash"])
        self.assertEqual(audit_bad["quality_grade"], "HIGH_RED_FLAG_PAPER_PROFIT")

    def test_beneish_m_score(self):
        safe_m = self.auditor.calculate_beneish_m_score(dsri=1.0, gmi=1.0, aqi=1.0, sgi=1.05)
        self.assertTrue(safe_m["is_safe"])
        self.assertTrue(safe_m["beneish_m_score"] <= -1.78)

    def test_altman_z_score(self):
        altman = self.auditor.calculate_altman_z_score(
            working_capital=40000,
            total_assets=200000,
            retained_earnings=35000,
            ebit=15000,
            book_value_equity=100000,
            total_liabilities=100000
        )
        self.assertTrue(altman["is_solvent"])
        self.assertEqual(altman["zone"], "SAFE_ZONE")

    def test_red_flags_scanner(self):
        bad_metrics = {
            "lnst": 1000,
            "ocf": -200,
            "debt_to_equity": 2.5,
            "receivables_growth_yoy": 40.0,
            "revenue_growth_yoy": 5.0,
            "inventory_growth_yoy": 50.0,
            "beneish_m_score": -1.2
        }
        flags = self.auditor.scan_red_flags(bad_metrics)
        self.assertEqual(len(flags), 5, "Must trigger all 5 red flags on suspicious company")

    # --- PILLAR 4: DYNAMIC CODE SANDBOX ---
    def test_sandbox_safe_math(self):
        res = self.sandbox.execute_safe_math("sum([10, 20, 30]) * 1.5")
        self.assertEqual(res, 90.0)

    def test_sandbox_security_barrier(self):
        with self.assertRaises(ValueError):
            self.sandbox.execute_safe_math("__import__('os').system('dir')")
        with self.assertRaises(ValueError):
            self.sandbox.execute_safe_math("open('secret.txt', 'r')")

    def test_position_sizing_lot_100(self):
        sizing = self.sandbox.calculate_position_sizing(
            nav=20000000.0,
            risk_pct_nav=0.015,
            entry_price=21150.0,
            stop_price=20310.0,
            lot_size=100
        )
        # 300,000 / 840 = 357.14 -> 300 cổ
        self.assertEqual(sizing["shares"], 300)
        self.assertEqual(sizing["shares"] % 100, 0, "Must be round lot of 100")
        self.assertTrue(sizing["is_risk_locked"])

    def test_expected_value_institutional(self):
        ev = self.sandbox.calculate_expected_value(p_win=0.65, target_win_pct=0.12, stop_loss_pct=0.04)
        self.assertTrue(ev["is_institutional_grade"])
        self.assertEqual(ev["risk_reward_ratio"], "1:3.0")
        self.assertTrue(ev["expected_value_pct"] > 0)

    # --- STEP 2: BAN 10 & SCOUT INTEGRATION TESTS ---
    def test_bctc_scout_integration(self):
        from scripts.bctc_ir_filing_scout import verify_and_enrich_ir_with_agent_zero
        res = verify_and_enrich_ir_with_agent_zero("HPG")
        self.assertEqual(res["symbol"], "HPG")
        self.assertIn("fundamentals", res)
        self.assertTrue(res["fundamentals"]["revenue_vnd_bil"] > 50000.0)
        self.assertIn("forensic", res)
        self.assertEqual(res["forensic"]["cash_flow_quality"]["is_real_cash"], True)

    def test_hien_live_ir_audit(self):
        from scripts.hien_bctc_agent import run_hien_live_ir_audit
        card = run_hien_live_ir_audit("HPG")
        self.assertIn("BAN 10 — HIỀN", card)
        self.assertIn("HPG", card)
        self.assertIn("Modified Beneish M-Score", card)
        self.assertIn("SAFE_AUTHENTIC", card)

    # --- PILLAR 5: ZERO MARKET WATCHER (BAN 9 VICTOR) ---
    def test_market_watcher_order_book_and_spoofing(self):
        from scripts.apex_agent_zero_engine import ZeroMarketWatcher
        watcher = ZeroMarketWatcher()
        # Test Bullish buy up
        res_bull = watcher.evaluate_order_book(buy_up_volume=70000, sell_down_volume=30000)
        self.assertEqual(res_bull["signal"], "BULLISH_BUY_UP")
        self.assertEqual(res_bull["buy_up_ratio"], 70.0)

        # Test Spoofing detection (kê lệnh ảo Giá 2)
        bid_depth = [{"price": 21100, "vol": 5000}, {"price": 21050, "vol": 35000}, {"price": 21000, "vol": 10000}]
        res_spoof = watcher.evaluate_order_book(buy_up_volume=10000, sell_down_volume=10000, bid_depth=bid_depth)
        self.assertTrue(res_spoof["spoofing_detected"], "Must detect spoofing on abnormally large bid 2")

    def test_market_watcher_sentinel_alerts(self):
        from scripts.apex_agent_zero_engine import ZeroMarketWatcher
        watcher = ZeroMarketWatcher()
        # Stop loss violation (Cost: 21150, ATR: 500 -> Stop: 20150. Current: 20000)
        incident_stop = watcher.check_sentinel_incident(
            ticker="HPG",
            current_price=20000.0,
            cost_price=21150.0,
            atr14=500.0
        )
        self.assertEqual(incident_stop["incident_type"], "STOP_LOSS_VIOLATION")
        self.assertEqual(incident_stop["severity"], "CRITICAL_RED_ALERT")

        # Take profit test (Cost: 21150, Current: 23500 -> +11.1%)
        incident_tp = watcher.check_sentinel_incident(
            ticker="HPG",
            current_price=23500.0,
            cost_price=21150.0,
            atr14=500.0
        )
        self.assertEqual(incident_tp["incident_type"], "TAKE_PROFIT_TP1")

    # --- PILLAR 6: ZERO MEDIA HARVESTER (BAN 11 KHÁNH & BẢO) ---
    def test_media_harvester_broll_and_hooks(self):
        from scripts.apex_agent_zero_engine import ZeroMediaHarvester
        harvester = ZeroMediaHarvester()
        pack = harvester.get_corporate_media_pack("HPG")
        self.assertIn("Dung Quất 2", pack["media_pack"]["key_project"])

        hooks = harvester.craft_viral_hook_brief("HPG", ocf_bil=8866.0, lnst_bil=8217.0)
        self.assertEqual(len(hooks), 3)
        self.assertIn("8,866 tỷ", hooks[0])

    # --- REAL PDF FILE EXTRACTION TEST ---
    def test_real_pdf_extraction_from_disk(self):
        real_pdf_path = "C:/Users/phuoc/.gemini/antigravity/brain/434b15db-b27c-41bb-b475-10a5bdc513b3/.user_uploaded/media_1793772419030_7e2ca40e.pdf"
        pages = self.parser.extract_text_from_pdf(real_pdf_path, max_pages=3)
        self.assertTrue(len(pages) >= 1, "Must extract pages from real user uploaded PDF")
        self.assertTrue("TÀI LIỆU" in pages[0]["text"] or len(pages[0]["text"]) > 50)


if __name__ == "__main__":
    unittest.main()
