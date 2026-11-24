#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V6.0 REGRESSION TEST SUITE — ZERO-SPAM TELEGRAM, SIMPLE SIGNALS, PROOF-OF-WORK & 2.5D UX
"""

import ast
import datetime
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from scripts import telegram_dispatcher as tg
from scripts.apex_tactical_war_room_engine import (
    build_simple_action_board,
    evaluate_and_trigger_tactical_alerts,
    get_tactical_war_room_state,
)
from scripts.apex_virtual_office_engine import (
    _finish_job,
    _record_job_start,
    _append_job_step,
    get_job_detail,
    get_virtual_office_room_detail,
)


ICT_TZ = datetime.timezone(datetime.timedelta(hours=7))


class TestV6TelegramAndOfficeUX(unittest.TestCase):
    def test_01_telegram_4layer_anti_spam_shield(self):
        """Kiểm tra Semantic Dedup, Event Key Cooldown, Quota 6 tin/giờ, Nghỉ lễ & Single-Owner Cloud."""
        with tempfile.TemporaryDirectory() as tmpd:
            tmp_cache = Path(tmpd) / "dedup.json"
            with patch.object(tg, "DEDUP_CACHE_FILE", tmp_cache):
                # 1) Semantic dedup: cùng mẫu chỉ lệch % nhỏ -> chặn tin thứ 2
                m1 = "🚨 BÁO CÁO BIẾN ĐỘNG: POW (13,250đ: ÁP LỰC CUNG BuyUp 39.1%) lúc 11:08"
                m2 = "🚨 BÁO CÁO BIẾN ĐỘNG: POW (13,300đ: ÁP LỰC CUNG BuyUp 39.9%) lúc 11:09"
                self.assertFalse(tg.is_duplicate_message("-1001", 4, m1, window_seconds=1800))
                self.assertTrue(tg.is_duplicate_message("-1001", 4, m2, window_seconds=1800))

                # 2) Event key cooldown: nội dung khác hẳn nhưng cùng event_key -> chặn
                self.assertFalse(tg.is_duplicate_message("-1001", 4, "Chốt lời HPG đợt một", window_seconds=14400, event_key="2026-11-25_HPG_TP1"))
                self.assertTrue(tg.is_duplicate_message("-1001", 4, "Cảnh báo giá HPG đạt đỉnh mới", window_seconds=14400, event_key="2026-11-25_HPG_TP1"))

                # 3) Quota Circuit Breaker: tối đa 6 tin/giờ trong cùng topic (trừ CRITICAL_STOP)
                for idx in range(4):
                    res = tg.is_duplicate_message("-1001", 4, f"Tin hợp lệ hoàn toàn riêng biệt số #{idx} nội dung độc lập {['Alpha', 'Beta', 'Gamma', 'Delta'][idx]} * {idx}", window_seconds=1800)
                    self.assertFalse(res)
                # Tin thứ 7 trong cùng 1 giờ bị chặn cứng bởi Quota Breaker
                self.assertTrue(tg.is_duplicate_message("-1001", 4, "Tin thứ bảy vượt trần giờ trong cùng một topic hoàn toàn khác biệt!", window_seconds=1800))
                # CRITICAL_STOP vẫn được phép vượt rào khẩn cấp
                self.assertFalse(tg.is_duplicate_message("-1001", 4, "CẮT LỖ KHẨN CẤP CRITICAL_STOP", window_seconds=1800, priority="CRITICAL_STOP"))

        # 4) Holiday & Cloud/PC Single-Owner Guard
        hol_dt = datetime.datetime(2026, 11, 24, 14, 5, 0, tzinfo=ICT_TZ)
        with patch.object(tg, "_get_ict_now", return_value=hol_dt):
            blocked, reason = tg.should_block_outbound_telegram(is_intraday_alert=True, priority="NORMAL")
            self.assertTrue(blocked)
            self.assertIn("HOLIDAY_OR_CLOSED_MARKET", reason)

        with patch.dict("os.environ", {"RENDER": "true", "TELEGRAM_POLLING_OWNER": "pc", "APEX_ALLOW_CLOUD_TELEGRAM_PUSH": "0"}):
            blocked_c, reason_c = tg.should_block_outbound_telegram(is_intraday_alert=False, priority="NORMAL")
            self.assertTrue(blocked_c)
            self.assertEqual(reason_c, "CLOUD_SINGLE_OWNER_PC")
            blocked_crit, _ = tg.should_block_outbound_telegram(is_intraday_alert=True, priority="CRITICAL_STOP")
            self.assertFalse(blocked_crit)

    def test_02_zero_target_guard_and_simple_action_board(self):
        """Mã có probe_target/stop/tp1 = 0 KHÔNG bao giờ bắn BUY_ZONE; Bảng hành động đơn giản MUA/BÁN/ĐỢI hoạt động chuẩn."""
        from scripts.apex_live_intraday_brain import compute_live_war_room_snapshot
        snap = compute_live_war_room_snapshot(force_refresh=False)
        for s in snap.get("live_stocks", []):
            if float(s.get("probe_target") or 0) <= 0 or float(s.get("stop_loss") or 0) <= 0:
                self.assertNotEqual(s.get("action_code"), "STANDBY_BUY_ZONE", f"{s.get('code')} có target 0 nhưng lại thành BUY_ZONE")

        wr = get_tactical_war_room_state(force_refresh=True)
        sab = wr.get("simple_action_board") or []
        self.assertGreater(len(sab), 0)
        for row in sab:
            self.assertIn(row.get("simple_action_code"), ("MUA", "BAN_CHOT_LOI", "BAN_CAT_LO", "DOI"))
            self.assertTrue(row.get("action_text_vi"))

        # Test consolidated Golden Window BUY alert (chỉ lấy mã target > 0 & bỏ qua mã 0 đ)
        fake_stocks = [
            {"code": "CTG", "is_holding": False, "price": 30100.0, "probe_target": 30150.0, "stop_loss": 28500.0, "tp1": 33200.0, "active_buy_pct": 68.5, "action_code": "STANDBY_BUY_ZONE", "change_pct": 0.4},
            {"code": "VHM", "is_holding": False, "price": 61500.0, "probe_target": 0.0, "stop_loss": 0.0, "tp1": 0.0, "active_buy_pct": 56.2, "action_code": "STANDBY_BUY_ZONE", "change_pct": 0.1},
        ]
        open_dt = datetime.datetime(2026, 11, 25, 14, 10, 0, tzinfo=ICT_TZ)
        fake_phase = {
            "active_phase_id": "GOLDEN_WINDOW",
            "active_phase_short": "GIỜ VÀNG",
            "is_weekend": False,
            "market_session": {"is_trading_day": True, "stale_feed_detected": False, "status_code": "GOLDEN_WINDOW", "next_trading_day": "2026-11-26"},
        }
        sent_calls = []
        with patch("scripts.apex_tactical_war_room_engine.get_ict_now", return_value=open_dt), \
             patch("scripts.apex_tactical_war_room_engine.save_directives_history"), \
             patch("scripts.telegram_dispatcher.dispatch_message", side_effect=lambda *a, **kw: sent_calls.append((a, kw)) or True):
            dirs = evaluate_and_trigger_tactical_alerts(
                live_stocks=fake_stocks,
                phase_info=fake_phase,
                directives=[],
                date_str="2026-11-25",
                snapshot={"portfolio_live": {"cash_vnd": 15541117.0, "cash_pct": 77.5, "total_nav_vnd": 20051117.0, "holdings": []}, "intraday_regime": {"regime_id": "S2_SIDEWAYS_SELECTIVE", "label": "S2"}},
            )
            joined = "\n".join(d.get("content", "") for d in dirs)
            self.assertIn("CTG", joined)
            self.assertNotIn("VHM", joined)
            self.assertEqual(len(sent_calls), 2)  # 1 bundle tới daily_warroom + 1 bundle tới james_hq (KHÔNG bắn 8 tin lẻ)

        board = build_simple_action_board(fake_stocks, fake_phase, {"regime_id": "S2_SIDEWAYS_SELECTIVE"})
        self.assertEqual(board[0]["symbol"], "CTG")
        self.assertEqual(board[0]["simple_action_code"], "MUA")
        self.assertEqual(board[1]["symbol"], "VHM")
        self.assertEqual(board[1]["simple_action_code"], "DOI")

    def test_03_virtual_office_proof_of_work_and_pure_stdlib(self):
        """apex_virtual_office_engine.py thuần Python & job Proof-of-Work ghi đủ steps_log + deliverables."""
        src = (BASE_DIR / "scripts" / "apex_virtual_office_engine.py").read_text(encoding="utf-8")
        tree = ast.parse(src)
        mods = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                mods.update(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                mods.add(node.module.split(".")[0])
        for bad in ("pandas", "numpy", "yfinance"):
            self.assertNotIn(bad, mods)

        from scripts import apex_virtual_office_engine as vo_eng
        with tempfile.TemporaryDirectory() as tmpd:
            tmp_jobs_file = Path(tmpd) / "office_jobs_history.json"
            with patch.object(vo_eng, "JOBS_HISTORY_FILE", tmp_jobs_file), \
                 patch.object(vo_eng, "_OFFICE_JOBS", []):
                jid = vo_eng._record_job_start("team_trong_palmer", "run_trong_audit", "Kiểm thử Proof Console")
                vo_eng._append_job_step(jid, "Bước 1 kiểm tra chéo SSOT", 50)
                vo_eng._finish_job(
                    jid,
                    True,
                    "Hoàn tất kiểm thử 10/10",
                    deliverables={"report_rel_path": "00_LIVE_INTER_CHAT_STATE.md", "handoff_note": "Đồng bộ xong"},
                )
                detail = vo_eng.get_job_detail(jid)
                self.assertTrue(detail["ok"])
                job = detail["job"]
                self.assertEqual(job["status"], "DONE")
                self.assertEqual(job["progress_pct"], 100)
                self.assertGreaterEqual(len(job["steps_log"]), 3)
                self.assertEqual(job["deliverables"]["report_rel_path"], "00_LIVE_INTER_CHAT_STATE.md")

        room_res = get_virtual_office_room_detail("team_james_palmer")
        self.assertTrue(room_res["ok"])
        self.assertIn("executive_brief", room_res["room"])
        self.assertIn("recent_jobs", room_res["room"])

    def test_04_portal_and_25d_ux_upgrades_present(self):
        """Kiểm tra HTML Portal và tài sản 2.5D chứa Bảng Đơn Giản, Proof Console và kích thước rộng mới."""
        import re as _re
        css = (BASE_DIR / "dashboard" / "office" / "office.css").read_text(encoding="utf-8")
        js = (BASE_DIR / "dashboard" / "office" / "office.js").read_text(encoding="utf-8")
        mh = _re.search(r"\.apex-office-shell\s*\{[^}]*min-height:\s*(\d+)px", css)
        dw = _re.search(r"\.office-drawer\s*\{[^}]*width:\s*(\d+)px", css)
        self.assertIsNotNone(mh)
        self.assertIsNotNone(dw)
        self.assertGreaterEqual(int(mh.group(1)), 700)
        self.assertGreaterEqual(int(dw.group(1)), 530)
        self.assertIn("office-proof-box", css)
        self.assertIn("ISO_X = 84", js)
        self.assertIn("drawer-live-job-box", js)
        self.assertIn("/api/office/job?id=", js)
        self.assertIn("office-quick-rooms", js)

        html = (BASE_DIR / "dashboard" / "index.html").read_text(encoding="utf-8")
        self.assertIn("wr-simple-action-board", html)
        self.assertIn("BẢNG HÀNH ĐỘNG ĐƠN GIẢN (MUA / BÁN / ĐỢI)", html)


if __name__ == "__main__":
    unittest.main()
