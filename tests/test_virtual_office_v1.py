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
    DATA_FLOW_PIPES,
    LEGACY_ROOM_ALIAS,
    ROOMS_BLUEPRINT,
    get_kanban_board_state,
    get_virtual_office_full_bundle,
    get_virtual_office_live_state,
    get_virtual_office_room_detail,
)
from scripts.apex_web_portal_engine import generate_portal_html
from scripts.start_apex_cloud_247 import ApexSupervisorHTTPHandler
from scripts.sync_chat_office_artifact import build_chat_office_html


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

    def test_02_live_state_ssot_and_5_teams(self):
        """Kiểm tra đúng 5 Khối Chuyên Trách + 1 Tiện ích, 5 luồng bàn giao và SSOT 105C307855."""
        st = get_virtual_office_live_state(force_refresh=True)
        self.assertTrue(st["ok"])
        self.assertEqual(st["org_model"], "APEX_5_TEAMS_EXECUTIVE_WORKFLOW_V2")
        self.assertEqual(len(st["rooms"]), 6)
        room_ids = {r["room_id"] for r in st["rooms"]}
        expected_ids = {"team_hien", "team_quan_alex", "team_james_palmer", "team_victor", "team_trong_palmer", "room_lounge"}
        self.assertEqual(room_ids, expected_ids)
        self.assertEqual(len(DATA_FLOW_PIPES), 5)
        self.assertEqual(len(st["data_flows"]), 5)
        self.assertEqual(st["ssot"]["account_id"], "105C307855")
        self.assertAlmostEqual(st["ssot"]["cash_vnd"], 20051117.0, places=0)
        self.assertEqual(st["ssot"]["holdings_count"], 0)
        self.assertGreater(len(st["intel_feed"]["feed_items"]), 0)
        watchlist_syms = [w["symbol"] for w in st["weekly_plan_summary"]["approved_watchlist"]]
        for expected_sym in ("TPB", "HDB", "CTG", "HPG", "VPB"):
            self.assertIn(expected_sym, watchlist_syms)

    def test_03_all_6_room_details_and_legacy_aliases(self):
        """Tất cả 6 phòng trả chi tiết hợp lệ; 5 Khối nghiệp vụ có báo cáo thật & LEGACY_ROOM_ALIAS tương thích ngược."""
        for bp in ROOMS_BLUEPRINT:
            rid = bp["room_id"]
            detail_res = get_virtual_office_room_detail(rid)
            self.assertTrue(detail_res["ok"], f"Lỗi lấy chi tiết {rid}")
            room = detail_res["room"]
            self.assertEqual(room["room_id"], rid)
            if rid != "room_lounge":
                self.assertGreater(len(room["recent_reports"]), 0, f"{rid} bị thiếu báo cáo thật")

        for old_id, new_id in (
            ("room_ban_10", "team_hien"),
            ("room_ban_7", "team_quan_alex"),
            ("room_ban_8", "team_james_palmer"),
            ("room_ban_9", "team_victor"),
            ("room_ban_12", "team_trong_palmer"),
        ):
            self.assertEqual(LEGACY_ROOM_ALIAS[old_id], new_id)
            res = get_virtual_office_room_detail(old_id)
            self.assertTrue(res["ok"])
            self.assertEqual(res["room"]["room_id"], new_id)

        bundle = get_virtual_office_full_bundle(force_refresh=False)
        self.assertEqual(len(bundle["rooms_detail"]), 6)
        self.assertIn("tasks", bundle["kanban_board"])

    def test_04_portal_html_and_chat_artifact_5_teams(self):
        """Kiểm tra HTML Portal đặt tab-office (5 Khối) làm màn hình chính & Chat Artifact hợp lệ."""
        html = generate_portal_html({}, [], [], available_dates=[])
        self.assertIn('/api/office/assets/office.css', html)
        self.assertIn('/api/office/assets/office.js', html)
        self.assertIn('0. Văn Phòng 2.5D (5 Khối)', html)
        self.assertIn('● 5 KHỐI LIVE', html)
        self.assertIn('<main id="tab-office" class="tab-pane active">', html)
        self.assertIn('<main id="tab-reports" class="tab-pane">', html)
        self.assertNotIn('<main id="tab-reports" class="tab-pane active">', html)
        self.assertIn('id="tab-war-room"', html)
        self.assertIn('id="tab-portfolio"', html)
        self.assertIn('window.ApexVirtualOffice.init()', html)

        chat_html = build_chat_office_html(force_refresh=False)
        self.assertIn("https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js", chat_html)
        self.assertIn("window.APEX_OFFICE_BOOTSTRAP_BUNDLE =", chat_html)
        self.assertIn('id="apex-virtual-office-root"', chat_html)
        self.assertIn("team_hien", chat_html)
        self.assertIn("team_trong_palmer", chat_html)

    def test_05_http_endpoints_cors_and_kanban_lifecycle(self):
        """Kiểm tra toàn bộ HTTP GET/POST/OPTIONS endpoints (kèm CORS) và chu trình Kanban sạch."""
        code, ctype, home_html = self._get("/")
        self.assertEqual(code, 200)
        self.assertIn("text/html", ctype)
        self.assertIn('id="apex-virtual-office-root"', home_html)

        req_opt = urllib.request.Request(self._base_url + "/api/office/kanban", method="OPTIONS")
        with urllib.request.urlopen(req_opt, timeout=10) as resp_opt:
            self.assertEqual(resp_opt.status, 204)
            self.assertEqual(resp_opt.headers.get("Access-Control-Allow-Origin"), "*")

        code_css, ctype_css, css_body = self._get("/api/office/assets/office.css")
        self.assertEqual(code_css, 200)
        self.assertIn("text/css", ctype_css)
        self.assertIn(".apex-office-shell", css_body)

        code_js, ctype_js, js_body = self._get("/api/office/assets/office.js")
        self.assertEqual(code_js, 200)
        self.assertIn("javascript", ctype_js)
        self.assertIn("window.ApexVirtualOffice", js_body)

        with urllib.request.urlopen(self._base_url + "/api/office/live_status", timeout=10) as resp_st:
            self.assertEqual(resp_st.status, 200)
            self.assertEqual(resp_st.headers.get("Access-Control-Allow-Origin"), "*")
            st_json = json.loads(resp_st.read().decode("utf-8"))
        self.assertTrue(st_json["ok"])
        self.assertEqual(len(st_json["rooms"]), 6)

        for rid in ("team_hien", "team_quan_alex", "team_james_palmer", "team_victor", "team_trong_palmer", "room_ban_10"):
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
            "title": "Test Virtual Office 5 Teams Kanban Task",
            "dept": "Khối 3 (James & Palmer)",
            "assignee": "James & Palmer",
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

        sa, res_a = self._post("/api/office/room_action", {"room_id": "team_james_palmer", "action": "sync_office"})
        self.assertEqual(sa, 200)
        self.assertTrue(res_a["ok"])


if __name__ == "__main__":
    unittest.main()
