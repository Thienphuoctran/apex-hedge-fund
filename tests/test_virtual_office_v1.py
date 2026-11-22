#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KIỂM ĐỊNH TOÀN DIỆN VĂN PHÒNG TRỰC QUAN 2.5D APEX (VIRTUAL OFFICE V1.0)
File: tests/test_virtual_office_v1.py
"""

import http.server
import json
import os
import sys
import threading
import unittest
import urllib.request
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.apex_virtual_office_engine import (
    ROOMS_BLUEPRINT,
    get_kanban_board_state,
    get_virtual_office_live_state,
    get_virtual_office_room_detail,
)
from scripts.apex_web_portal_engine import generate_portal_html
from scripts.start_apex_cloud_247 import ApexSupervisorHTTPHandler


class TestVirtualOfficeV1(unittest.TestCase):
    _prev_pin = None
    _srv = None
    _base_url = None

    @classmethod
    def setUpClass(cls):
        cls._prev_pin = os.environ.get("APEX_PORTAL_PIN")
        os.environ["APEX_PORTAL_PIN"] = ""
        cls._srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), ApexSupervisorHTTPHandler)
        port = cls._srv.server_address[1]
        cls._base_url = f"http://127.0.0.1:{port}"
        cls._thread = threading.Thread(target=cls._srv.serve_forever, daemon=True)
        cls._thread.start()

    @classmethod
    def tearDownClass(cls):
        if cls._srv is not None:
            cls._srv.shutdown()
            cls._srv.server_close()
        if cls._prev_pin is None:
            os.environ.pop("APEX_PORTAL_PIN", None)
        else:
            os.environ["APEX_PORTAL_PIN"] = cls._prev_pin

    def _get(self, path: str):
        with urllib.request.urlopen(self._base_url + path, timeout=10) as resp:
            return resp.status, resp.headers.get("Content-Type", ""), resp.read().decode("utf-8")

    def _post(self, path: str, payload: dict):
        req = urllib.request.Request(
            self._base_url + path,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))

    def test_01_engine_no_heavy_ml_imports(self):
        """Đảm bảo apex_virtual_office_engine.py thuần Python, không import pandas/numpy/yfinance."""
        import ast
        src = (BASE_DIR / "scripts" / "apex_virtual_office_engine.py").read_text(encoding="utf-8")
        tree = ast.parse(src)
        imported_mods = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_mods.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_mods.add(node.module.split(".")[0])
        for forbidden in ("pandas", "numpy", "yfinance"):
            self.assertNotIn(forbidden, imported_mods)

    def test_02_live_state_ssot_and_12_rooms(self):
        """Kiểm tra 12 phòng đầy đủ, đúng SSOT 105C307855 (20,051,117 đ, 0 CP) và rổ Tuần 48."""
        st = get_virtual_office_live_state(force_refresh=True)
        self.assertTrue(st["ok"])
        self.assertEqual(len(st["rooms"]), 12)
        self.assertEqual(st["ssot"]["account_id"], "105C307855")
        self.assertAlmostEqual(st["ssot"]["cash_vnd"], 20051117.0, places=0)
        self.assertEqual(st["ssot"]["holdings_count"], 0)
        self.assertGreater(len(st["intel_feed"]["feed_items"]), 0)
        watchlist_syms = [w["symbol"] for w in st["weekly_plan_summary"]["approved_watchlist"]]
        for expected_sym in ("TPB", "HDB", "CTG", "HPG", "VPB"):
            self.assertIn(expected_sym, watchlist_syms)

    def test_03_all_12_room_details_and_real_reports(self):
        """Tất cả 12 phòng trả chi tiết hợp lệ; cả 11 phòng nghiệp vụ đều có báo cáo thật."""
        for bp in ROOMS_BLUEPRINT:
            rid = bp["room_id"]
            detail_res = get_virtual_office_room_detail(rid)
            self.assertTrue(detail_res["ok"], f"Lỗi lấy chi tiết {rid}")
            room = detail_res["room"]
            self.assertEqual(room["room_id"], rid)
            if rid != "room_lounge":
                self.assertGreater(len(room["recent_reports"]), 0, f"{rid} bị thiếu báo cáo thật")

    def test_04_portal_html_office_is_default_home(self):
        """Kiểm tra HTML Portal đặt tab-office làm màn hình chính active và vẫn giữ đủ 3 tab chuyên sâu."""
        html = generate_portal_html({}, [], [], available_dates=[])
        self.assertIn('/api/office/assets/office.css', html)
        self.assertIn('/api/office/assets/office.js', html)
        self.assertIn('<main id="tab-office" class="tab-pane active">', html)
        self.assertIn('<main id="tab-reports" class="tab-pane">', html)
        self.assertNotIn('<main id="tab-reports" class="tab-pane active">', html)
        self.assertIn('id="tab-war-room"', html)
        self.assertIn('id="tab-portfolio"', html)
        self.assertIn('window.ApexVirtualOffice.init()', html)

    def test_05_http_endpoints_and_kanban_lifecycle(self):
        """Kiểm tra toàn bộ HTTP GET/POST endpoints của Văn phòng 2.5D và chu trình Kanban sạch."""
        code, ctype, home_html = self._get("/")
        self.assertEqual(code, 200)
        self.assertIn("text/html", ctype)
        self.assertIn('id="apex-virtual-office-root"', home_html)

        code_css, ctype_css, css_body = self._get("/api/office/assets/office.css")
        self.assertEqual(code_css, 200)
        self.assertIn("text/css", ctype_css)
        self.assertIn(".apex-office-shell", css_body)

        code_js, ctype_js, js_body = self._get("/api/office/assets/office.js")
        self.assertEqual(code_js, 200)
        self.assertIn("javascript", ctype_js)
        self.assertIn("window.ApexVirtualOffice", js_body)

        code_st, _, st_raw = self._get("/api/office/live_status")
        self.assertEqual(code_st, 200)
        st_json = json.loads(st_raw)
        self.assertTrue(st_json["ok"])
        self.assertEqual(len(st_json["rooms"]), 12)

        for rid in ("room_ban_10", "room_ban_8", "room_ban_9", "room_ban_12"):
            c_rm, _, rm_raw = self._get(f"/api/office/room?id={rid}")
            self.assertEqual(c_rm, 200)
            self.assertTrue(json.loads(rm_raw)["ok"])

        c_kb, _, kb_raw = self._get("/api/office/kanban")
        self.assertEqual(c_kb, 200)
        self.assertTrue(json.loads(kb_raw)["ok"])

        c_jb, _, jb_raw = self._get("/api/office/jobs")
        self.assertEqual(c_jb, 200)
        self.assertTrue(json.loads(jb_raw)["ok"])

        # Kanban create -> move -> delete cleanup
        before_total = get_kanban_board_state()["total_tasks"]
        sc, res_c = self._post("/api/office/kanban", {
            "op": "create",
            "title": "Test Virtual Office Kanban Task",
            "dept": "Ban 8",
            "assignee": "James",
            "priority": "HIGH",
        })
        self.assertEqual(sc, 200)
        self.assertTrue(res_c["ok"])
        tid = res_c["task"]["id"]

        sm, res_m = self._post("/api/office/kanban", {
            "op": "move",
            "task_id": tid,
            "status": "AUDIT_REVIEW",
        })
        self.assertEqual(sm, 200)
        self.assertEqual(res_m["task"]["status"], "AUDIT_REVIEW")

        sd, res_d = self._post("/api/office/kanban", {"op": "delete", "task_id": tid})
        self.assertEqual(sd, 200)
        self.assertTrue(res_d["ok"])
        self.assertEqual(get_kanban_board_state()["total_tasks"], before_total)

        sa, res_a = self._post("/api/office/room_action", {"room_id": "room_ban_8", "action": "sync_office"})
        self.assertEqual(sa, 200)
        self.assertTrue(res_a["ok"])


if __name__ == "__main__":
    unittest.main()
