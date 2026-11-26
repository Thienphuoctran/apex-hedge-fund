#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APEX SYSTEM STANDBY & MARKET HIBERNATION CONTROLLER
File: scripts/apex_standby_controller.py

Quản lý trạng thái Ngủ Đông Thị Trường (Market Hibernation Mode):
- Lưu/đọc cấu hình duy nhất tại data/system_standby_mode.json.
- Khi standby_active=True:
  1. Giữ nguyên hệ thống cào dữ liệu BCTC / IR / Internet Intel / OHLCV.
  2. Chỉ cho phép báo cáo Tổng kết Cuối Ngày (EOD) hợp nhất của James & Palmer trên Telegram.
  3. Chặn toàn bộ báo cáo intraday / Hiền / Khánh / Học viện / WarRoom spam trên Telegram.
  4. Kích hoạt Radar Rà Đáy & Phục Hồi 24/7 của Victor (Ban 9), chỉ lặp lại 5 phút/lần trên Telegram
     KHI VÀ CHỈ KHI thị trường đang mở phiên, XANH trở lại và đạt ngưỡng quay lại đầu tư.
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path
from typing import Any, Dict

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

STANDBY_CONFIG_FILE = BASE_DIR / "data" / "system_standby_mode.json"

DEFAULT_STANDBY_CONFIG: Dict[str, Any] = {
    "version": "1.0",
    "standby_active": False,
    "mode_code": "ACTIVE_TRADING_MODE",
    "activated_at_ict": "",
    "activated_by": "Chủ tịch Trần Quốc Thiên Phước",
    "reason": "",
    "keep_data_crawlers": True,
    "telegram_policy": {
        "eod_only_james_palmer": True,
        "allow_victor_recovery_radar": True,
        "allow_interactive_copilot_replies": True,
        "allow_critical_stop_alerts": False,
    },
    "victor_recovery_radar": {
        "enabled": True,
        "repeat_interval_seconds": 300,
        "require_active_trading_session": True,
        "session_start_hm": "09:15",
        "session_end_hm": "14:45",
        "min_vni_change_pct": 0.35,
        "min_breadth_advance_ratio_pct": 52.0,
        "min_breadth_ma20_pct": 23.0,
        "min_buy_up_pct": 58.0,
        "ftd_min_vni_change_pct": 1.20,
        "ftd_min_advance_ratio_pct": 60.0,
        "ftd_min_vol_pace_ratio": 1.05,
        "ftd_min_buy_up_pct": 62.0,
    },
}


def _now_ict_str() -> str:
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    return utc_now.astimezone(datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S ICT")


def load_standby_config() -> Dict[str, Any]:
    """Đọc cấu hình chế độ Ngủ Đông (utf-8-sig safe, merge default keys)."""
    cfg = json.loads(json.dumps(DEFAULT_STANDBY_CONFIG))
    if STANDBY_CONFIG_FILE.exists():
        try:
            raw = json.loads(STANDBY_CONFIG_FILE.read_text(encoding="utf-8-sig"))
            if isinstance(raw, dict):
                for k, v in raw.items():
                    if isinstance(v, dict) and isinstance(cfg.get(k), dict):
                        cfg[k].update(v)
                    else:
                        cfg[k] = v
        except Exception:
            pass
    return cfg


def is_standby_mode_active() -> bool:
    """Trả về True nếu toàn hệ thống đang ở chế độ Ngủ Đông chờ thị trường phục hồi."""
    return bool(load_standby_config().get("standby_active", False))


def set_standby_mode(active: bool, reason: str = "") -> Dict[str, Any]:
    """Bật hoặc tắt chế độ Ngủ Đông Thị Trường và lưu nguyên tử xuống JSON."""
    cfg = load_standby_config()
    cfg["standby_active"] = bool(active)
    cfg["mode_code"] = "MARKET_HIBERNATION_RECOVERY_RADAR" if active else "ACTIVE_TRADING_MODE"
    cfg["updated_at_ict"] = _now_ict_str()
    if active:
        cfg["activated_at_ict"] = cfg["updated_at_ict"]
    if reason:
        cfg["reason"] = reason
    elif not active and not cfg.get("reason"):
        cfg["reason"] = "Khôi phục trạng thái tác chiến bình thường."

    STANDBY_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = STANDBY_CONFIG_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(STANDBY_CONFIG_FILE)
    return cfg


def is_telegram_allowed_in_standby(
    event_key: str | None = None,
    priority: str | None = None,
    topic_key: str | None = None,
    is_interactive_reply: bool = False,
) -> tuple[bool, str]:
    """
    Kiểm tra quyền gửi Telegram khi standby_active=True.
    Chỉ cho phép:
      1) Báo cáo Tổng kết EOD duy nhất của James & Palmer (`EOD_SINGLE_DIGEST_*` / `EOD_JAMES_PALMER`).
      2) Cảnh báo Thị trường Đạt Ngưỡng Đáy / Phục Hồi từ Victor (`VICTOR_MARKET_RECOVERY_*` / `RECOVERY_ALERT`).
      3) Tin nhắn phản hồi trực tiếp lệnh của Chủ tịch trên Telegram Copilot (`is_interactive_reply=True`).
    """
    cfg = load_standby_config()
    if not bool(cfg.get("standby_active", False)):
        return True, "NORMAL_MODE"

    policy = cfg.get("telegram_policy") or {}
    ev = str(event_key or "").upper().strip()
    prio = str(priority or "NORMAL").upper().strip()

    if is_interactive_reply and bool(policy.get("allow_interactive_copilot_replies", True)):
        return True, "STANDBY_ALLOW_INTERACTIVE_REPLY"

    if bool(policy.get("eod_only_james_palmer", True)) and (
        ev.startswith("EOD_SINGLE_DIGEST_") or prio == "EOD_JAMES_PALMER"
    ):
        return True, "STANDBY_ALLOW_JAMES_PALMER_EOD"

    if bool(policy.get("allow_victor_recovery_radar", True)) and (
        ev.startswith("VICTOR_MARKET_RECOVERY_") or prio == "RECOVERY_ALERT"
    ):
        return True, "STANDBY_ALLOW_VICTOR_RECOVERY"

    if bool(policy.get("allow_critical_stop_alerts", False)) and prio == "CRITICAL_STOP":
        return True, "STANDBY_ALLOW_CRITICAL_STOP"

    return False, f"STANDBY_HIBERNATION_BLOCKED(topic={topic_key or '-'},event={ev or '-'},prio={prio})"


def main() -> int:
    parser = argparse.ArgumentParser(description="Apex Market Hibernation / Standby Controller")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--enable", action="store_true", help="Bật chế độ Ngủ Đông (chỉ giữ cào dữ liệu, EOD James+Palmer & Victor 5p Recovery)")
    group.add_argument("--resume", "--disable", dest="resume", action="store_true", help="Tắt chế độ Ngủ Đông, quay lại tác chiến đầy đủ")
    group.add_argument("--status", action="store_true", help="Xem trạng thái Ngủ Đông hiện tại")
    parser.add_argument("--reason", type=str, default="", help="Lý do chuyển chế độ")
    args = parser.parse_args()

    if args.enable:
        cfg = set_standby_mode(True, reason=args.reason)
        print(json.dumps({"action": "ENABLED", "standby_active": cfg["standby_active"], "mode_code": cfg["mode_code"]}, ensure_ascii=False, indent=2))
    elif args.resume:
        cfg = set_standby_mode(False, reason=args.reason or "Chủ tịch kích hoạt quay lại giao dịch bình thường.")
        print(json.dumps({"action": "RESUMED", "standby_active": cfg["standby_active"], "mode_code": cfg["mode_code"]}, ensure_ascii=False, indent=2))
    else:
        cfg = load_standby_config()
        print(json.dumps(cfg, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
