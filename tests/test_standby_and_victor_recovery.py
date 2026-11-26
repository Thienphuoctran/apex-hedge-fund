#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for Market Hibernation Standby Mode & Victor 5-Minute Recovery Radar."""

from __future__ import annotations

import datetime
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from scripts import apex_standby_controller as sb
from scripts import cbtt_filings_radar
from scripts import pre_market_readiness_audit
from scripts import system_health_audit
from scripts import telegram_dispatcher as tg
from scripts import telegram_eod_audit_reporter
from scripts import telegram_morning_magazine_card
from scripts import telegram_morning_reporter
from scripts import vn3_portfolio_autonomous_sentinel as victor

ICT_TZ = datetime.timezone(datetime.timedelta(hours=7))


class TestStandbyAndVictorRecovery(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp_dir.name)
        self.orig_sb_file = sb.STANDBY_CONFIG_FILE
        self.orig_rec_file = victor.VICTOR_RECOVERY_STATE_FILE
        self.orig_dedup_file = tg.DEDUP_CACHE_FILE

        sb.STANDBY_CONFIG_FILE = self.tmp_path / "system_standby_mode.json"
        victor.VICTOR_RECOVERY_STATE_FILE = self.tmp_path / "victor_recovery_radar_state.json"
        tg.DEDUP_CACHE_FILE = self.tmp_path / "telegram_dedup_cache.json"

        sb.set_standby_mode(True, reason="Unit test hibernation")

    def tearDown(self) -> None:
        sb.STANDBY_CONFIG_FILE = self.orig_sb_file
        victor.VICTOR_RECOVERY_STATE_FILE = self.orig_rec_file
        tg.DEDUP_CACHE_FILE = self.orig_dedup_file
        self.tmp_dir.cleanup()

    def test_telegram_guard_strictly_allows_eod_victor_and_interactive_only(self) -> None:
        for topic in ("daily_warroom", "alerts", "hien_desk", "khanh_studio", "academy_learning", "morning_blotter"):
            blocked, reason = tg.should_block_outbound_telegram(topic_key=topic, priority="NORMAL")
            self.assertTrue(blocked, f"Expected topic {topic} blocked in standby mode")
            self.assertIn("STANDBY_HIBERNATION_BLOCKED", reason)

        blocked_stop, _ = tg.should_block_outbound_telegram(
            topic_key="daily_warroom", priority="CRITICAL_STOP", event_key="2026-11-27_HPG_STOP"
        )
        self.assertTrue(blocked_stop, "Normal CRITICAL_STOP should stay muted unless opted in")

        blocked_eod, _ = tg.should_block_outbound_telegram(
            topic_key="james_hq",
            priority="EOD_JAMES_PALMER",
            event_key="EOD_SINGLE_DIGEST_2026-11-27",
        )
        self.assertFalse(blocked_eod, "James + Palmer EOD digest MUST pass")

        blocked_rec, _ = tg.should_block_outbound_telegram(
            topic_key="daily_warroom",
            priority="RECOVERY_ALERT",
            event_key="VICTOR_MARKET_RECOVERY_2026-11-27",
            is_intraday_alert=False,
        )
        self.assertFalse(blocked_rec, "Victor recovery alert MUST pass")

        blocked_reply, _ = tg.should_block_outbound_telegram(
            priority="NORMAL", is_interactive_reply=True
        )
        self.assertFalse(blocked_reply, "Direct interactive copilot reply MUST pass")

    def test_legacy_direct_telegram_senders_are_blocked_in_standby(self) -> None:
        with mock.patch("urllib.request.urlopen") as m_url:
            self.assertFalse(cbtt_filings_radar.send_telegram_alert("test cbtt"))
            self.assertFalse(telegram_morning_reporter.send_telegram_message("tok", "cid", "test morning"))
            self.assertFalse(pre_market_readiness_audit.send_telegram("test premarket"))
            self.assertFalse(telegram_eod_audit_reporter.send_telegram_message("tok", "cid", "test eod"))
            self.assertFalse(telegram_morning_magazine_card.publish_morning_magazine_card())
            self.assertFalse(system_health_audit.send_telegram_audit("2026-11-27", 100, "ok"))
            m_url.assert_not_called()

    def test_recovery_alert_bypasses_6_per_hour_quota_breaker(self) -> None:
        # Simulate 8 recovery alerts in same hour (more than 6/hr normal limit)
        base_ts = 1_800_000_000.0
        for i in range(8):
            with mock.patch("scripts.telegram_dispatcher.time.time", return_value=base_ts + i * 310):
                dup = tg.is_duplicate_message(
                    chat_id="-1001",
                    thread_id=4,
                    text=f"Recovery ping #{i + 1} VNI=1660",
                    window_seconds=290,
                    event_key="VICTOR_MARKET_RECOVERY_2026-11-27",
                    priority="RECOVERY_ALERT",
                )
                self.assertFalse(dup, f"5-minute recovery alert #{i + 1} should not hit quota cap")

    def test_victor_recovery_triggers_only_when_green_and_repeats_every_5_mins(self) -> None:
        trading_dt = datetime.datetime(2026, 11, 27, 10, 15, 0, tzinfo=ICT_TZ)
        red_idx = {
            "vn_index": {"value": 1615.0, "change_pct": -0.9, "ma20": 1665.0, "volume_pace_ratio": 0.9},
            "market_breadth": {"advancers": 80, "decliners": 250, "advance_ratio_pct": 24.2},
        }
        green_idx = {
            "vn_index": {"value": 1655.0, "change_pct": 1.55, "ma20": 1665.0, "volume_pace_ratio": 1.18},
            "market_breadth": {"advancers": 265, "decliners": 70, "advance_ratio_pct": 79.1},
        }
        green_quotes = {
            "HPG": {"price": 20500, "change_pct": 2.5, "active_buy_pct": 66.0},
            "CTG": {"price": 30800, "change_pct": 2.1, "active_buy_pct": 64.0},
            "MBB": {"price": 18500, "change_pct": 1.8, "active_buy_pct": 63.0},
        }

        # 1. Red market -> NEVER alerts
        with mock.patch("scripts.vn3_portfolio_autonomous_sentinel.dispatch_message", return_value=True) as m_tg:
            st_red = victor.run_victor_recovery_radar(
                notify_telegram=True,
                now_ict=trading_dt,
                now_ts_override=1000.0,
                indices_override=red_idx,
                quotes_override=green_quotes,
                br20_override=12.0,
            )
            self.assertFalse(st_red["recovery_triggered"])
            self.assertFalse(st_red["active_repeating"])
            m_tg.assert_not_called()

        # 2. Off hours (21:30 ICT) even with green snapshot -> NEVER alerts
        off_dt = datetime.datetime(2026, 11, 27, 21, 30, 0, tzinfo=ICT_TZ)
        with mock.patch("scripts.vn3_portfolio_autonomous_sentinel.dispatch_message", return_value=True) as m_tg:
            st_off = victor.run_victor_recovery_radar(
                notify_telegram=True,
                now_ict=off_dt,
                now_ts_override=1000.0,
                indices_override=green_idx,
                quotes_override=green_quotes,
                br20_override=28.0,
            )
            self.assertFalse(st_off["recovery_triggered"])
            m_tg.assert_not_called()

        # 3. Live trading green & investable -> t=1000s (#1), skipped at t=1120s, repeats at t=1300s (#2)
        with mock.patch("scripts.vn3_portfolio_autonomous_sentinel.dispatch_message", return_value=True) as m_tg:
            st1 = victor.run_victor_recovery_radar(
                notify_telegram=True,
                now_ict=trading_dt,
                now_ts_override=1000.0,
                indices_override=green_idx,
                quotes_override=green_quotes,
                br20_override=26.5,
            )
            self.assertTrue(st1["recovery_triggered"])
            self.assertTrue(st1["dispatched_this_cycle"])
            self.assertEqual(st1["alerts_sent_today"], 1)

            st_wait = victor.run_victor_recovery_radar(
                notify_telegram=True,
                now_ict=trading_dt + datetime.timedelta(minutes=2),
                now_ts_override=1120.0,
                indices_override=green_idx,
                quotes_override=green_quotes,
                br20_override=26.5,
            )
            self.assertFalse(st_wait["dispatched_this_cycle"])

            st2 = victor.run_victor_recovery_radar(
                notify_telegram=True,
                now_ict=trading_dt + datetime.timedelta(minutes=5),
                now_ts_override=1300.0,
                indices_override=green_idx,
                quotes_override=green_quotes,
                br20_override=27.0,
            )
            self.assertTrue(st2["dispatched_this_cycle"])
            self.assertEqual(st2["alerts_sent_today"], 2)
            self.assertEqual(m_tg.call_count, 2)

        # 4. Market turns red again at t=1650s -> stops repeating!
        with mock.patch("scripts.vn3_portfolio_autonomous_sentinel.dispatch_message", return_value=True) as m_tg:
            st_stop = victor.run_victor_recovery_radar(
                notify_telegram=True,
                now_ict=trading_dt + datetime.timedelta(minutes=11),
                now_ts_override=1660.0,
                indices_override=red_idx,
                quotes_override=green_quotes,
                br20_override=14.0,
            )
            self.assertFalse(st_stop["active_repeating"])
            m_tg.assert_not_called()


if __name__ == "__main__":
    unittest.main()
