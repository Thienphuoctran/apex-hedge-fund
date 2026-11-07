#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UNIT TEST: TCBS VAULT WATCHER & READ-ONLY SECURITY GUARDRAIL
File: tests/test_tcinvest_vault_watcher.py
"""

import unittest
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.tcinvest_vault_watcher import (
    TCBSVaultWatcher,
    assert_read_only_safety,
    SecurityViolationError,
    ENFORCE_READ_ONLY,
    FORBIDDEN_OPERATIONS
)


class TestTCBSVaultWatcher(unittest.TestCase):

    def test_read_only_enforced_flag(self):
        """Đảm bảo cờ ENFORCE_READ_ONLY luôn luôn là True."""
        self.assertTrue(ENFORCE_READ_ONLY, "ENFORCE_READ_ONLY must be strictly True")

    def test_security_interceptor_blocks_forbidden_actions(self):
        """Kiểm thử tường lửa chặn 100% các từ khóa liên quan đến tác động tiền và đặt lệnh."""
        for forbidden in FORBIDDEN_OPERATIONS:
            with self.subTest(forbidden=forbidden):
                url = f"https://openapi.tcbs.com.vn/v1/{forbidden}"
                with self.assertRaises(SecurityViolationError):
                    assert_read_only_safety(url)

    def test_security_interceptor_blocks_write_http_methods(self):
        """Kiểm thử chặn tuyệt đối các method POST, PUT, DELETE, PATCH."""
        for method in ["POST", "PUT", "DELETE", "PATCH"]:
            with self.subTest(method=method):
                with self.assertRaises(SecurityViolationError):
                    assert_read_only_safety("https://openapi.tcbs.com.vn/v1/some_endpoint", method=method)

    def test_safe_read_actions_allowed(self):
        """Đảm bảo các thao tác đọc an toàn không bị chặn."""
        safe_urls = [
            "https://openapi.tcbs.com.vn/aion/v1/accounts/105C307855/cashInvestments",
            "https://openapi.tcbs.com.vn/aion/v1/accounts/105C307855/se",
            "https://openapi.tcbs.com.vn/aion/v1/accounts/105C307855/orders",
            "fetch_cash_balance",
            "fetch_portfolio_holdings",
            "fetch_realtime_board",
            "fetch_orders_status_history",
            "fetch_pnl_realtime"
        ]
        for url in safe_urls:
            with self.subTest(url=url):
                try:
                    assert_read_only_safety(url, method="GET")
                except SecurityViolationError:
                    self.fail(f"Safe URL {url} should not trigger SecurityViolationError")

    def test_watcher_initialization_and_ssot_fallback(self):
        """Kiểm tra khởi tạo watcher và chế độ fallback SSOT."""
        watcher = TCBSVaultWatcher()
        self.assertEqual(watcher.account_id, "105C307855")
        cash_info = watcher.fetch_cash_balance()
        self.assertIn("cash_balance_vnd", cash_info)
        self.assertGreater(cash_info["cash_balance_vnd"], 0)

    def test_realtime_board_quotes(self):
        """Kiểm tra bảng giá trực tuyến có giá trị hợp lệ."""
        watcher = TCBSVaultWatcher()
        board = watcher.fetch_realtime_board(["HPG", "TCB", "MBB"])
        self.assertEqual(board.get("status"), "SUCCESS")
        quotes = board.get("quotes", {})
        self.assertIn("HPG", quotes)
        self.assertGreater(quotes["HPG"]["price"], 0)

    def test_pnl_and_session_patrol_audit(self):
        """Kiểm tra báo cáo tuần tra phiên của Master CIO James."""
        watcher = TCBSVaultWatcher()
        pnl = watcher.fetch_pnl_realtime()
        self.assertIn("total_nav_vnd", pnl)
        self.assertIn("cash_balance_vnd", pnl)
        self.assertGreaterEqual(pnl["total_nav_vnd"], 20000000.0)

        report = watcher.run_session_patrol_audit("morning", dispatch_telegram=False)
        self.assertIn("BÁO CÁO TUẦN TRA PHIÊN SÁNG", report)
        self.assertIn("Chủ tịch Phước Trần", report)
        self.assertIn("105C307855", report)


if __name__ == "__main__":
    unittest.main()
