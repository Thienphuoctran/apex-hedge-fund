#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KIỂM ĐỊNH ĐỒNG BỘ CHÂN LÝ HỢP NHẤT & LỊCH GIAO DỊCH HOSE/HNX (APEX UNIFIED BRAIN V5.0)
File: tests/test_canonical_sync_v5.py
"""

import ast
import datetime
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.vn_market_calendar import (
    add_trading_days,
    get_vn_market_session_state,
    is_vn_trading_day,
    next_trading_day,
    prev_trading_day,
)
from scripts.apex_canonical_truth import (
    build_and_save_canonical_truth,
    classify_canonical_regime,
    load_canonical_truth,
)
from scripts.apex_virtual_office_engine import get_virtual_office_live_state, get_virtual_office_room_detail
from scripts.apex_web_portal_engine import generate_dynamic_tactical_stages_html, generate_portal_html


ICT_TZ = datetime.timezone(datetime.timedelta(hours=7))


class TestCanonicalSyncV5(unittest.TestCase):
    def test_01_vn_holiday_calendar_and_t2_settlement(self):
        """Nhận diện đúng 2026-11-24 là Ngày Văn hóa VN (NQ 28/2026/QH16) và dịch T+2 chính xác."""
        hol_date = datetime.date(2026, 11, 24)
        self.assertFalse(is_vn_trading_day(hol_date))
        self.assertEqual(prev_trading_day(hol_date), datetime.date(2026, 11, 23))
        self.assertEqual(next_trading_day(hol_date), datetime.date(2026, 11, 25))
        # Bán 20/11 (Thứ Sáu) + 2 ngày làm việc -> Thứ Tư 25/11 (bỏ qua 21, 22, 24)
        self.assertEqual(add_trading_days(datetime.date(2026, 11, 20), 2), datetime.date(2026, 11, 25))
        # Mua 23/11 (Thứ Hai) + 2 ngày làm việc -> Thứ Năm 26/11 (bỏ qua lễ 24/11)
        self.assertEqual(add_trading_days(datetime.date(2026, 11, 23), 2), datetime.date(2026, 11, 26))

        st = get_vn_market_session_state(
            now_ict=datetime.datetime(2026, 11, 24, 13, 2, 0, tzinfo=ICT_TZ),
            market_overview={"exchange_time": "15:05:00"},
        )
        self.assertTrue(st["is_holiday"])
        self.assertFalse(st["is_trading_day"])
        self.assertFalse(st["is_live_session"])
        self.assertEqual(st["status_code"], "HOLIDAY_CLOSED")
        self.assertEqual(st["next_trading_day"], "2026-11-25")

    def test_02_stale_feed_auto_detector_on_unlisted_closure(self):
        """Phát hiện dữ liệu đóng băng (exchange_time='15:05:00' lúc 11:36 ngày làm việc bình thường)."""
        fake_normal_day = datetime.datetime(2026, 11, 25, 11, 36, 0, tzinfo=ICT_TZ)
        st = get_vn_market_session_state(
            now_ict=fake_normal_day,
            market_overview={"exchange_time": "15:05:00"},
        )
        self.assertTrue(st["is_trading_day"])
        self.assertTrue(st["stale_feed_detected"])
        self.assertFalse(st["is_live_session"])
        self.assertEqual(st["status_code"], "EXCHANGE_STALE_FEED")

        reg = classify_canonical_regime(
            vn_index=1697.14,
            vn_index_chg_pct=0.49,
            vni_ma20=1727.57,
            vni_ma50=1746.23,
            br20_pct=19.4,
            buy_up_pct=59.4,
            adv_ratio=58.0,
            session_state=st,
            has_open_positions=True,
            current_invested_pct=22.5,
        )
        self.assertEqual(reg["regime_id"], "EXCHANGE_STALE_FEED")
        self.assertEqual(reg["max_new_allocation_pct"], 0)
        self.assertTrue(reg["is_closed_override"])

    def test_03_pure_python_stdlib_constraint(self):
        """vn_market_calendar, apex_canonical_truth, apex_virtual_office_engine KHÔNG import pandas/numpy/yfinance."""
        for rel in (
            "scripts/vn_market_calendar.py",
            "scripts/apex_canonical_truth.py",
            "scripts/apex_virtual_office_engine.py",
        ):
            src = (BASE_DIR / rel).read_text(encoding="utf-8")
            tree = ast.parse(src)
            mods = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    mods.update(a.name.split(".")[0] for a in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    mods.add(node.module.split(".")[0])
            for bad in ("pandas", "numpy", "yfinance"):
                self.assertNotIn(bad, mods, f"{rel} không được import {bad}")

    def test_04_canonical_consistency_across_all_engines(self):
        """Toàn bộ Chat Truth, War-Room, Intraday Brain, Virtual Office 2.5D và Web Portal thống nhất 100%."""
        truth = load_canonical_truth(refresh_if_missing=True)
        wr = json.loads((BASE_DIR / "data" / "live_warroom_state.json").read_text(encoding="utf-8"))
        ssot_disk = json.loads((BASE_DIR / "data" / "current_portfolio_state.json").read_text(encoding="utf-8"))

        self.assertEqual(truth["market_session"]["status_code"], wr["market_session"]["status_code"])
        self.assertEqual(truth["canonical_regime"]["regime_id"], wr["canonical_regime"]["regime_id"])
        self.assertEqual(truth["ssot"]["cash_vnd"], float(ssot_disk["cash_balance_vnd"]))
        self.assertEqual(truth["ssot"]["open_positions_count"], len(ssot_disk["active_positions"]))

        vo = get_virtual_office_live_state(force_refresh=True)
        self.assertEqual(vo["market_session"]["status_code"], truth["market_session"]["status_code"])
        self.assertEqual(vo["market_live"]["live_regime"], truth["canonical_regime"]["regime_id"])
        self.assertEqual(vo["ssot"]["cash_vnd"], truth["ssot"]["cash_vnd"])

        # Khối 3 ghim Nghị quyết 21h00 & Đồng bộ Chat lên đầu danh sách
        room3 = get_virtual_office_room_detail("team_james_palmer")["room"]
        pinned_rels = [r.get("rel_path") for r in room3["recent_reports"] if r.get("is_pinned")]
        self.assertIn("00_LIVE_INTER_CHAT_STATE.md", pinned_rels)
        self.assertTrue(any("Dai_Hoi_Dong" in str(x) or "council_resolutions" in str(x) for x in pinned_rels))

        # Kiểm tra HTML Tab 2 khi sàn đóng cửa ngày 2026-11-24 KHÔNG chứa thẻ live giả
        hol_dt = datetime.datetime(2026, 11, 24, 13, 5, 0, tzinfo=ICT_TZ)
        with patch.dict("os.environ", {"APEX_PORTAL_ENV": "test"}):
            stages_html = generate_dynamic_tactical_stages_html(now=hol_dt, wr_state={"market_session": truth["market_session"], "intraday_regime": truth["canonical_regime"]})
        self.assertIn("KHÔNG GIAO DỊCH HÔM NAY", stages_html)
        self.assertNotIn("Hấp Thụ Hàng T+2.5 Về Tài Khoản", stages_html)
        self.assertNotIn("TĂNG TỐC TẦNG 3", stages_html)

    def test_05_zero_legacy_poisoning_in_today_outputs(self):
        """Các báo cáo ngày 2026-11-24 & dashboard/index.html không còn text mẫu cũ lỗi thời."""
        forbidden_phrases = [
            "Đã tất toán sạch 20/11 (0 CP / 100% Cash)",
            "0 CP (100% Tiền mặt — Sẵn sàng Tuần 48)",
            "VETO HDB tới hết 20/11",
            "PVT, TCB, MSH, BAF",
            "SSOT 15,541,117 ₫ (0 CP)",
            "20,051,117 ₫ (0 CP)",
        ]
        target_files = [
            BASE_DIR / "08_Master_Investment_CIO" / "2026-11-24_Master_CIO_Final_Decision.md",
            BASE_DIR / "08_Master_Investment_CIO" / "2026-11-24_Morning_War_Room_Pact.md",
            BASE_DIR / "08_Master_Investment_CIO" / "2026-11-24_Master_Blotter_Snapshot.md",
            BASE_DIR / "VN_Market" / "07_Daily_Specialist" / "2026-11-24_Live_Intraday_Report.md",
            BASE_DIR / "dashboard" / "index.html",
        ]
        for fp in target_files:
            if not fp.exists():
                self.fail(f"Thiếu file bắt buộc sau tái sinh: {fp}")
            txt = fp.read_text(encoding="utf-8", errors="ignore")
            for bad in forbidden_phrases:
                self.assertNotIn(bad, txt, f"Phát hiện text mẫu cũ '{bad}' trong {fp.name}")


if __name__ == "__main__":
    unittest.main()
