#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/vn3_portfolio_autonomous_sentinel.py

BAN 9 — BỘ ĐIỀU KHIỂN GIÁM SÁT THỜI GIAN THỰC ĐỘNG (VICTOR SENTINEL 24/7)
Phục vụ: Chủ tịch HĐQT Trần Quốc Thiên Phước | Tài khoản TCBS: 105C307855

Cơ chế hoạt động xuyên suốt MỌI PHIÊN LÀM VIỆC (Pre-ATO, ATO, Sáng, Trưa, Chiều, Giờ Vàng, ATC, Ngoài giờ/Demo):
1. Nạp động 100% vị thế đang nắm giữ & tiền mặt thật từ SSOT `data/current_portfolio_state.json`.
2. Kéo bảng giá trực tiếp VPS Realtime Feed (Độ trễ < 200ms) cho toàn bộ 12 mã cốt lõi & Danh mục quan tâm TCBS.
3. Quét liên tục các ngưỡng quan trọng: Chạm Stop 2xATR, Cận Stop, Đạt chốt lời TP1/TP2, Đạt vùng canh mua LO, Đột biến Buy-Up %.
4. Bắn cảnh báo trực tiếp vào Phòng Tác Chiến (`directives_history`), Telegram (`alerts`) & đồng bộ file Telemetry JSON/MD + SQLite Vault.
"""

import os
import sys
import time
import json
import datetime
import argparse
import logging
from pathlib import Path
from typing import Dict, Any, List

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# --- TÍCH HỢP AGENT ZERO MARKET WATCHER (BAN 9 VICTOR) ---
try:
    from scripts.apex_agent_zero_engine import ZeroMarketWatcher
    SENTINEL_ZERO_WATCHER = ZeroMarketWatcher()
except Exception:
    SENTINEL_ZERO_WATCHER = None

import warnings

warnings.simplefilter("ignore")
os.environ["PYTHONWARNINGS"] = "ignore"
logging.getLogger("yfinance").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)

yf = None  # Lazy-loaded only outside compact cloud mode if VPS datafeed returns empty

try:
    import winsound
except ImportError:
    winsound = None

from scripts.telegram_dispatcher import dispatch_message
from scripts.vietnam_realtime_feed import fetch_vps_quotes
from scripts.vn_market_calendar import get_vn_market_session_state

SENTINEL_DIR = BASE_DIR / "09_Realtime_Portfolio_Sentinel"
TELEMETRY_JSON = SENTINEL_DIR / "vn3_live_telemetry.json"
TELEMETRY_MD = SENTINEL_DIR / "vn3_live_telemetry.md"
VICTOR_TRAILING_FILE = BASE_DIR / "data" / "victor_trailing_state.json"


def _load_victor_trailing_state() -> Dict[str, Any]:
    if VICTOR_TRAILING_FILE.exists():
        try:
            data = json.loads(VICTOR_TRAILING_FILE.read_text(encoding="utf-8-sig"))
            if isinstance(data, dict):
                return data
        except Exception:
            pass
    return {"version": "V7.0", "updated_at": "", "positions": {}}


def _save_victor_trailing_state(payload: Dict[str, Any]) -> None:
    try:
        VICTOR_TRAILING_FILE.parent.mkdir(parents=True, exist_ok=True)
        tmp = VICTOR_TRAILING_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(VICTOR_TRAILING_FILE)
    except Exception:
        pass


def compute_dynamic_trailing_stop(
    sym: str,
    entry_px: float,
    live_px: float,
    base_stop_px: float,
    trailing_state: Dict[str, Any],
) -> Dict[str, Any]:
    """Cập nhật đỉnh cao nhất từ giá vốn & tính Trailing Stop (hòa vốn +6%, trailing -5% từ +11%)."""
    pos_map = trailing_state.setdefault("positions", {})
    prev = pos_map.get(sym) if isinstance(pos_map.get(sym), dict) else {}
    prev_high = float(prev.get("highest_since_entry") or 0.0)
    high = max(prev_high, entry_px, live_px)
    gain_pct = ((high - entry_px) / entry_px * 100.0) if entry_px > 0 else 0.0

    trailing_5pct = round(high * 0.95, -1) if high > 0 else base_stop_px
    breakeven_px = round(entry_px * 1.005, -1) if entry_px > 0 else base_stop_px
    if gain_pct >= 11.0:
        eff_stop = max(base_stop_px, breakeven_px, trailing_5pct)
        mode = "TRAILING_5PCT_PROFIT"
    elif gain_pct >= 6.0:
        eff_stop = max(base_stop_px, breakeven_px)
        mode = "BREAKEVEN_LOCKED"
    else:
        eff_stop = base_stop_px
        mode = "INITIAL_2ATR"

    row = {
        "symbol": sym,
        "entry_price": round(entry_px, 0),
        "live_price": round(live_px, 0),
        "highest_since_entry": round(high, 0),
        "max_gain_pct": round(gain_pct, 2),
        "base_stop_vnd": round(base_stop_px, 0),
        "trailing_stop_5pct": round(trailing_5pct, 0),
        "effective_stop_vnd": round(eff_stop, 0),
        "stop_mode": mode,
        "updated_at": _ict_now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    pos_map[sym] = row
    return row

WATCHLIST_FALLBACKS: Dict[str, Dict[str, Any]] = {
    "TPB": {"name": "TPBank", "entry_price": 12300.0, "stop_loss": 11600.0, "stop_warning": 11850.0, "sell_target_min": 13350.0, "sell_target_max": 14450.0, "probe_target": 12250.0},
    "HPG": {"name": "Tập Đoàn Hòa Phát", "entry_price": 20500.0, "stop_loss": 19300.0, "stop_warning": 19700.0, "sell_target_min": 22300.0, "sell_target_max": 24100.0, "probe_target": 20200.0},
    "CTG": {"name": "VietinBank", "entry_price": 30150.0, "stop_loss": 28500.0, "stop_warning": 29100.0, "sell_target_min": 33200.0, "sell_target_max": 35800.0, "probe_target": 30150.0},
    "NAB": {"name": "Nam A Bank", "entry_price": 13100.0, "stop_loss": 12400.0, "stop_warning": 12650.0, "sell_target_min": 14400.0, "sell_target_max": 15700.0, "probe_target": 13100.0},
    "CTS": {"name": "Chứng Khoán VietinBank", "entry_price": 23800.0, "stop_loss": 22300.0, "stop_warning": 22800.0, "sell_target_min": 26600.0, "sell_target_max": 29000.0, "probe_target": 23800.0},
    "HDB": {"name": "HDBank", "entry_price": 21800.0, "stop_loss": 20500.0, "stop_warning": 20950.0, "sell_target_min": 23650.0, "sell_target_max": 25600.0, "probe_target": 21800.0},
    "VPB": {"name": "VPBank", "entry_price": 20300.0, "stop_loss": 19350.0, "stop_warning": 19700.0, "sell_target_min": 23450.0, "sell_target_max": 25200.0, "probe_target": 20300.0},
    "TCB": {"name": "Techcombank", "entry_price": 21000.0, "stop_loss": 19850.0, "stop_warning": 20250.0, "sell_target_min": 23100.0, "sell_target_max": 25000.0, "probe_target": 21000.0},
    "PVT": {"name": "PVTrans", "entry_price": 18650.0, "stop_loss": 17800.0, "stop_warning": 18150.0, "sell_target_min": 20700.0, "sell_target_max": 22300.0, "probe_target": 18650.0},
    "NT2": {"name": "Điện Lực Nhơn Trạch 2", "entry_price": 23600.0, "stop_loss": 22300.0, "stop_warning": 22750.0, "sell_target_min": 25950.0, "sell_target_max": 28100.0, "probe_target": 23600.0},
    "SSI": {"name": "Chứng Khoán SSI", "entry_price": 19800.0, "stop_loss": 18700.0, "stop_warning": 19100.0, "sell_target_min": 21800.0, "sell_target_max": 23600.0, "probe_target": 19800.0},
    "PVP": {"name": "Vận Tải Dầu Khí TBD", "entry_price": 16550.0, "stop_loss": 15650.0, "stop_warning": 15950.0, "sell_target_min": 18250.0, "sell_target_max": 19750.0, "probe_target": 16550.0},
}

alerted_triggers = set()
LAST_KNOWN_QUOTES: Dict[str, Dict[str, Any]] = {}


def load_dynamic_ssot_state() -> Dict[str, Any]:
    """Đọc động danh mục SSOT và cấu hình giám sát cho tất cả mã đang giữ + watchlist."""
    try:
        from scripts.portfolio_state_manager import PortfolioStateManager
        st = PortfolioStateManager.load_state()
    except Exception:
        st = {}

    active_pos = st.get("active_positions", {}) if isinstance(st.get("active_positions"), dict) else {}
    cash_vnd = float(st.get("cash_balance_vnd", 12516471.0) or 12516471.0)
    realized_pnl = float(st.get("realized_pnl_vnd", 167119.0) or 167119.0)
    is_closed = (len(active_pos) == 0) or (st.get("status") in ("ALL_CASH_STANDDOWN", "ALL_POSITIONS_CLOSED_100_PERCENT_CASH"))

    cfg_map: Dict[str, Dict[str, Any]] = {}
    for sym, pos in active_pos.items():
        s_up = str(sym).upper().strip()
        if not s_up or not isinstance(pos, dict):
            continue
        sh = int(pos.get("shares", 0) or 0)
        ep = float(pos.get("entry_price", 0.0) or 0.0)
        sl = float(pos.get("stop_loss", 0.0) or round(ep * 0.935, -1))
        tp1 = float(pos.get("take_profit_tp1", 0.0) or round(ep * 1.10, -1))
        tp2 = float(pos.get("take_profit_tp2", 0.0) or round(ep * 1.18, -1))
        cfg_map[s_up] = {
            "status": "HOLDING" if sh > 0 else "WATCHLIST",
            "is_holding": sh > 0,
            "shares": sh,
            "entry_price": ep,
            "current_price": float(pos.get("current_price") or ep),
            "stop_loss": sl,
            "stop_warning": round(sl * 1.02, -1),
            "sell_target_min": tp1,
            "sell_target_max": tp2,
            "tp1": tp1,
            "tp2": tp2,
            "probe_target": ep,
            "name": pos.get("name") or WATCHLIST_FALLBACKS.get(s_up, {}).get("name", s_up),
        }

    for sym, defaults in WATCHLIST_FALLBACKS.items():
        if sym not in cfg_map:
            cfg_map[sym] = {
                "status": "WATCHLIST",
                "is_holding": False,
                "shares": 0,
                "entry_price": defaults["entry_price"],
                "current_price": defaults["entry_price"],
                "stop_loss": defaults["stop_loss"],
                "stop_warning": defaults["stop_warning"],
                "sell_target_min": defaults["sell_target_min"],
                "sell_target_max": defaults["sell_target_max"],
                "tp1": defaults["sell_target_min"],
                "tp2": defaults["sell_target_max"],
                "probe_target": defaults["probe_target"],
                "name": defaults["name"],
            }

    return {
        "raw": st,
        "active_positions": active_pos,
        "cash_vnd": cash_vnd,
        "realized_pnl": realized_pnl,
        "is_closed": is_closed,
        "config": cfg_map,
        "symbols": list(cfg_map.keys())[:12],
    }


_INIT_SSOT = load_dynamic_ssot_state()
_is_closed = _INIT_SSOT["is_closed"]
_verified_cash = _INIT_SSOT["cash_vnd"]
CONFIG = _INIT_SSOT["config"]


def sound_beep(freq=1500, dur=300, times=3):
    if winsound:
        try:
            for _ in range(times):
                winsound.Beep(freq, dur)
                time.sleep(0.06)
        except Exception:
            pass


def fetch_live_quotes(symbols: List[str] = None) -> Dict[str, Dict[str, Any]]:
    """
    Ưu tiên số 1: VPS Realtime Datafeed (Độ trễ < 200ms).
    Fallback số 2: Yahoo Finance (yfinance) hoặc SSOT fallback.
    """
    global LAST_KNOWN_QUOTES
    ssot_state = load_dynamic_ssot_state()
    target_syms = symbols or ssot_state["symbols"]
    cfg_map = ssot_state["config"]
    quotes: Dict[str, Dict[str, Any]] = {}

    try:
        vps_data = fetch_vps_quotes(target_syms, timeout=4)
        for sym in target_syms:
            if sym in vps_data and float(vps_data[sym].get("price") or 0.0) > 0:
                d = vps_data[sym]
                p = float(d["price"])
                quotes[sym] = {
                    "price": p,
                    "ref_price": float(d.get("ref_price") or p),
                    "change_pct": float(d.get("change_pct") or 0.0),
                    "high": float(d.get("day_high") or d.get("high") or p),
                    "low": float(d.get("day_low") or d.get("low") or p),
                    "volume": int(d.get("volume") or 0),
                    "active_buy_pct": float(d.get("active_buy_pct") or 50.0),
                    "is_live": True,
                    "data_source": d.get("data_source", "VPS_DIRECT_HOSE_TICK"),
                }
                LAST_KNOWN_QUOTES[sym] = dict(quotes[sym])
    except Exception:
        pass

    for sym in target_syms:
        if sym not in quotes or quotes[sym].get("price", 0.0) <= 0:
            fb_p = float(cfg_map.get(sym, {}).get("current_price") or 0.0)
            quotes[sym] = dict(LAST_KNOWN_QUOTES.get(sym, {
                "price": fb_p,
                "ref_price": fb_p,
                "change_pct": 0.0,
                "high": fb_p,
                "low": fb_p,
                "volume": 0,
                "active_buy_pct": 50.0,
                "is_live": False,
                "data_source": "FALLBACK_SSOT",
            }))
            if quotes[sym]["price"] <= 0 and os.environ.get("APEX_CLOUD_COMPACT_MODE", "").strip().lower() not in ("1", "true", "yes"):
                try:
                    import yfinance as _yf_lazy
                    t = _yf_lazy.Ticker(f"{sym}.VN")
                    h = t.history(period="1d")
                    if not h.empty:
                        p = float(h["Close"].iloc[-1])
                        if p > 0:
                            quotes[sym]["price"] = p
                            quotes[sym]["high"] = float(h["High"].iloc[-1])
                            quotes[sym]["low"] = float(h["Low"].iloc[-1])
                            quotes[sym]["volume"] = int(h["Volume"].iloc[-1])
                            LAST_KNOWN_QUOTES[sym] = dict(quotes[sym])
                except Exception:
                    pass
    return quotes


def _ict_now() -> datetime.datetime:
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    return utc_now.astimezone(datetime.timezone(datetime.timedelta(hours=7)))


def check_triggers_and_alert(quotes: Dict[str, Dict[str, Any]], notify_telegram: bool = True) -> List[Dict[str, Any]]:
    """
    Quét toàn bộ mã đang nắm giữ & watchlist trên phiên giao dịch hợp lệ:
    - Chốt lời TP1/TP2 hoặc Cắt lỗ Stop 2xATR / Cận Stop cho vị thế nắm giữ (tin ngắn gọn 4 dòng).
    - Đạt vùng canh mua LO kèm Mua chủ động >= 55% trong Khung Giờ Vàng.
    - Khóa tuyệt đối thông báo intraday trong ngày nghỉ lễ / cuối tuần / dữ liệu đóng băng.
    """
    now = _ict_now()
    now_str = now.strftime("%H:%M:%S")
    date_str = now.strftime("%Y-%m-%d")
    hm = now.hour * 60 + now.minute
    msess = get_vn_market_session_state(now_ict=now)
    is_closed = (not msess.get("is_trading_day", True)) or bool(msess.get("stale_feed_detected", False))
    in_market_hours = (not is_closed) and (now.weekday() < 5) and (9 * 60 <= hm <= 14 * 60 + 45)

    ssot_state = load_dynamic_ssot_state()
    cfg_map = ssot_state["config"]
    trailing_state = _load_victor_trailing_state()
    trailing_state["updated_at"] = f"{date_str} {now_str}"
    triggered_events: List[Dict[str, Any]] = []

    for sym, cfg in cfg_map.items():
        q = quotes.get(sym, {})
        price = float(q.get("price") or 0.0)
        if price <= 0:
            continue
        buy_up = float(q.get("active_buy_pct") or 50.0)
        chg_pct = float(q.get("change_pct") or 0.0)

        if cfg["is_holding"]:
            t_row = compute_dynamic_trailing_stop(
                sym=sym,
                entry_px=float(cfg.get("entry_price") or price),
                live_px=price,
                base_stop_px=float(cfg.get("stop_loss") or 0.0),
                trailing_state=trailing_state,
            )
            eff_stop = float(t_row.get("effective_stop_vnd") or cfg.get("stop_loss") or 0.0)
            cfg["effective_stop"] = eff_stop
            cfg["stop_mode"] = t_row.get("stop_mode", "INITIAL_2ATR")
            cost = cfg["shares"] * cfg["entry_price"]
            market_val = cfg["shares"] * price
            pnl_trade = market_val - cost
            pnl_pct_trade = (pnl_trade / cost) * 100.0 if cost > 0 else 0.0

            if cfg["sell_target_min"] > 0 and price >= cfg["sell_target_min"]:
                key = f"{date_str}_{sym}_TP1"
                triggered_events.append({"symbol": sym, "type": "TP1_REACHED", "price": price, "buy_up": buy_up})
                if key not in alerted_triggers:
                    alerted_triggers.add(key)
                    sound_beep(1900, 350, 3)
                    msg_ui = (
                        f"💰 [ĐẠT NGƯỠNG BÁN CHỐT LỜI — {sym}] Giá {price:,.0f} đ >= TP1 ({cfg['sell_target_min']:,.0f} đ). "
                        f"Hành động: TIẾN HÀNH BÁN chốt lời 50% vị thế!"
                    )
                    msg_tg = (
                        f"💰 <b>CHẠM NGƯỠNG BÁN CHỐT LỜI — {sym}</b> ({now_str})\n"
                        f"• Giá hiện tại: <b>{price:,.0f} đ</b> (vượt TP1 {cfg['sell_target_min']:,.0f} đ • Lãi {pnl_pct_trade:+.2f}%)\n"
                        f"• 👉 <b>Hành động: TIẾN HÀNH BÁN chốt lời 50%</b> bằng lệnh LO tại {price:,.0f} đ\n"
                        f"• 🛡️ Quản trị: Giữ 50% còn lại hướng TP2 {cfg.get('tp2', 0):,.0f} đ (kéo Stop về giá vốn)."
                    )
                    try:
                        from scripts.apex_tactical_war_room_engine import push_external_war_room_alert
                        push_external_war_room_alert("Victor (Ban 9 Live Sentinel)", "sentinel_alert", msg_ui, role="sentinel", alert_key=key, date_str=date_str)
                    except Exception:
                        pass
                    if notify_telegram and in_market_hours:
                        dispatch_message("daily_warroom", msg_tg, parse_mode="HTML", mirror_to_reports_vault=False, event_key=key, cooldown_seconds=14400, is_intraday_alert=True)

            elif eff_stop > 0 and price <= eff_stop:
                key = f"{date_str}_{sym}_STOP"
                triggered_events.append({"symbol": sym, "type": "STOP_LOSS_BREACH", "price": price, "buy_up": buy_up})
                if key not in alerted_triggers:
                    alerted_triggers.add(key)
                    sound_beep(2000, 500, 4)
                    msg_ui = (
                        f"🔴 [CHẠM NGƯỠNG BÁN CẮT LỖ ({cfg['stop_mode']}) — {sym}] Giá {price:,.0f} đ <= Stop {eff_stop:,.0f} đ! "
                        f"Hành động: TIẾN HÀNH BÁN cắt lỗ dứt khoát nếu không rút chân trước 14h15!"
                    )
                    msg_tg = (
                        f"🔴 <b>CHẠM NGƯỠNG BÁN ({cfg['stop_mode']}) — {sym}</b> ({now_str})\n"
                        f"• Giá hiện tại: <b>{price:,.0f} đ</b> (thủng Stop {eff_stop:,.0f} đ • {pnl_pct_trade:+.2f}%)\n"
                        f"• 👉 <b>Hành động: TIẾN HÀNH BÁN dứt khoát</b> (kiểm định 14h15)\n"
                        f"• 🛡️ Quản trị: Khóa rủi ro danh mục, tuyệt đối không trung bình giá xuống."
                    )
                    try:
                        from scripts.apex_tactical_war_room_engine import push_external_war_room_alert
                        push_external_war_room_alert("Victor (Ban 9 Live Sentinel)", "sentinel_alert", msg_ui, role="sentinel", alert_key=key, date_str=date_str)
                    except Exception:
                        pass
                    if notify_telegram and in_market_hours:
                        dispatch_message("daily_warroom", msg_tg, parse_mode="HTML", mirror_to_reports_vault=False, event_key=key, cooldown_seconds=14400, is_intraday_alert=True, priority="CRITICAL_STOP")
                        dispatch_message("james_hq", msg_tg, parse_mode="HTML", mirror_to_reports_vault=False, event_key=f"{key}_JAMES", cooldown_seconds=14400, is_intraday_alert=True, priority="CRITICAL_STOP")

            elif eff_stop > 0 and ((price - eff_stop) / price * 100.0) <= 2.6:
                key = f"{date_str}_{sym}_NEARSTOP"
                triggered_events.append({"symbol": sym, "type": "NEAR_STOP_WARNING", "price": price, "buy_up": buy_up})
                if key not in alerted_triggers:
                    alerted_triggers.add(key)
                    msg_ui = (
                        f"🟡 [CẬN NGƯỠNG BẢO VỆ ({cfg['stop_mode']}) — {sym}] Giá {price:,.0f} đ (cách Stop {eff_stop:,.0f} đ chỉ {((price - eff_stop) / price * 100.0):.2f}%). "
                        f"Hành động: TẠM ĐỢI — Chưa bán, theo dõi nến 14h15!"
                    )
                    try:
                        from scripts.apex_tactical_war_room_engine import push_external_war_room_alert
                        push_external_war_room_alert("Victor (Ban 9 Live Sentinel)", "sentinel_alert", msg_ui, role="sentinel", alert_key=key, date_str=date_str)
                    except Exception:
                        pass
        else:
            probe_p = float(cfg.get("probe_target") or 0.0)
            stop_p = float(cfg.get("stop_loss") or 0.0)
            tp1_p = float(cfg.get("tp1") or 0.0)
            if probe_p > 0 and stop_p > 0 and tp1_p > 0 and price <= probe_p * 1.012 and buy_up >= 55.0:
                key = f"{date_str}_{sym}_BUYZONE"
                triggered_events.append({"symbol": sym, "type": "BUY_ZONE_REACHED", "price": price, "buy_up": buy_up})
                if key not in alerted_triggers and in_market_hours:
                    alerted_triggers.add(key)
                    msg_ui = (
                        f"🟢 [ĐẠT MỨC MUA — {sym}] Giá {price:,.0f} đ (mục tiêu <= {probe_p:,.0f} đ), BuyUp {buy_up:.1f}%. "
                        f"Hành động: ĐẶT MUA LO sau 14h05 | Stop {stop_p:,.0f} đ | TP1 {tp1_p:,.0f} đ."
                    )
                    try:
                        from scripts.apex_tactical_war_room_engine import push_external_war_room_alert
                        push_external_war_room_alert("Victor (Ban 9 Live Sentinel)", "sentinel_alert", msg_ui, role="sentinel", alert_key=key, date_str=date_str)
                    except Exception:
                        pass
                    if notify_telegram and in_market_hours and (13 * 60 + 45 <= hm <= 14 * 60 + 25):
                        msg_tg = (
                            f"🟢 <b>CỔ PHIẾU ĐẠT MỨC MUA — {sym}</b> ({now_str})\n"
                            f"• Giá hiện tại: <b>{price:,.0f} đ</b> (sát mục tiêu gom {probe_p:,.0f} đ • BuyUp {buy_up:.1f}%)\n"
                            f"• 👉 <b>Hành động: ĐẶT MUA LO 100 CP</b> vùng {probe_p:,.0f} đ (Khung 14h05–14h25)\n"
                            f"• 🛡️ Quản trị: Chốt lời TP1 {tp1_p:,.0f} đ | Cắt lỗ {stop_p:,.0f} đ."
                        )
                        dispatch_message("daily_warroom", msg_tg, parse_mode="HTML", mirror_to_reports_vault=False, event_key=key, cooldown_seconds=14400, is_intraday_alert=True)

    _save_victor_trailing_state(trailing_state)

    # Đồng bộ trực tiếp trạng thái War-Room & Trigger Report 24/7
    try:
        from scripts.apex_tactical_war_room_engine import get_tactical_war_room_state
        get_tactical_war_room_state(force_refresh=True)
    except Exception:
        pass

    return triggered_events


def update_telemetry(quotes: Dict[str, Dict[str, Any]]) -> None:
    now_dt = _ict_now().strftime("%Y-%m-%d %H:%M:%S")
    ssot_state = load_dynamic_ssot_state()
    cfg_map = ssot_state["config"]
    cash_vnd = ssot_state["cash_vnd"]
    realized_pnl = ssot_state["realized_pnl"]
    trailing_state = _load_victor_trailing_state()
    trailing_state["updated_at"] = now_dt

    total_cost = 0.0
    total_market_val = 0.0
    total_unrealized_pnl = 0.0
    held_rows: List[str] = []
    watch_rows: List[str] = []
    positions_summary: List[Dict[str, Any]] = []

    for sym, cfg in cfg_map.items():
        q = quotes.get(sym, {})
        price = float(q.get("price") or cfg.get("current_price") or 0.0)
        buy_up = float(q.get("active_buy_pct") or 50.0)
        chg_pct = float(q.get("change_pct") or 0.0)
        vol = int(q.get("volume") or 0)

        if cfg["is_holding"]:
            t_row = compute_dynamic_trailing_stop(
                sym=sym,
                entry_px=float(cfg.get("entry_price") or price),
                live_px=price,
                base_stop_px=float(cfg.get("stop_loss") or 0.0),
                trailing_state=trailing_state,
            )
            eff_stop = float(t_row.get("effective_stop_vnd") or cfg.get("stop_loss") or 0.0)
            cfg["stop_loss"] = eff_stop
            shares = cfg["shares"]
            entry = cfg["entry_price"]
            cost = shares * entry
            market_val = shares * price
            pnl = market_val - cost
            pnl_pct = (pnl / cost) * 100.0 if cost > 0 else 0.0
            total_cost += cost
            total_market_val += market_val
            total_unrealized_pnl += pnl

            dist_stop = ((price - cfg["stop_loss"]) / price) * 100.0 if price > 0 else 0.0
            dist_target = ((cfg["sell_target_min"] - price) / price) * 100.0 if price > 0 else 0.0
            pnl_str = f"+{pnl:,.0f} ₫ (+{pnl_pct:.2f}%)" if pnl >= 0 else f"{pnl:,.0f} ₫ ({pnl_pct:.2f}%)"
            held_rows.append(
                f"| **{sym}** | {cfg['name']} | `{shares:,}` CP | `{entry:,.0f} ₫` | **`{price:,.0f} ₫`** | "
                f"**{pnl_str}** | `{cfg['stop_loss']:,.0f} ₫` ({dist_stop:+.1f}%) | "
                f"**`{cfg['sell_target_min']:,.0f} ₫`** ({dist_target:+.1f}%) | `{buy_up:.1f}%` | **🟢 TRỰC CHIẾN 24/7** |"
            )
            positions_summary.append({
                "symbol": sym,
                "name": cfg["name"],
                "shares": shares,
                "entry_price": entry,
                "current_price": price,
                "cost": cost,
                "market_value": market_val,
                "unrealized_pnl": pnl,
                "unrealized_pnl_pct": round(pnl_pct, 2),
                "stop_loss": cfg["stop_loss"],
                "sell_target_min": cfg["sell_target_min"],
                "sell_target_max": cfg["sell_target_max"],
                "volume": vol,
                "active_buy_pct": buy_up,
                "action_mandate": "BẢO VỆ VỊ THẾ STOP 2xATR & LƯỚT T+0 / TP1",
            })
        else:
            probe_p = float(cfg.get("probe_target") or 0.0)
            signal_lbl = (
                "🟢 ĐẠT VÙNG MUA LO" if (probe_p > 0 and price <= probe_p * 1.012 and buy_up >= 55.0)
                else ("🟠 ÁP LỰC CUNG (CẤM ĐUỔI)" if buy_up <= 40.0 else "🟡 THEO DÕI CUNG CẦU")
            )
            watch_rows.append(
                f"| **{sym}** | {cfg['name']} | **`{price:,.0f} ₫`** ({chg_pct:+.2f}%) | `{probe_p:,.0f} ₫` | `{cfg['stop_loss']:,.0f} ₫` | `{cfg['tp1']:,.0f} ₫` | `{buy_up:.1f}%` | {signal_lbl} |"
            )

    total_pnl_pct = (total_unrealized_pnl / total_cost) * 100.0 if total_cost > 0 else 0.0
    total_nav = total_market_val + cash_vnd

    telemetry_data = {
        "timestamp": now_dt,
        "account_id": "105C307855",
        "chairman": "Trần Quốc Thiên Phước",
        "mode": "ALL_CASH_STANDDOWN" if len(positions_summary) == 0 else "REALTIME_VPS_DIRECT_FEED",
        "mandate": "VICTOR 24/7 CONTINUOUS SURVEILLANCE ACROSS ALL SESSIONS",
        "total_cost": total_cost,
        "total_market_val": total_market_val,
        "total_unrealized_pnl": total_unrealized_pnl,
        "total_unrealized_pnl_pct": round(total_pnl_pct, 2),
        "dry_powder": cash_vnd,
        "total_nav": total_nav,
        "realized_pnl_vnd": realized_pnl,
        "positions": positions_summary,
    }
    _save_victor_trailing_state(trailing_state)
    SENTINEL_DIR.mkdir(parents=True, exist_ok=True)
    with open(TELEMETRY_JSON, "w", encoding="utf-8") as f:
        json.dump(telemetry_data, f, indent=2, ensure_ascii=False)

    held_md = "\n".join(held_rows) if held_rows else "| -- | 100% Tiền mặt | 0 | -- | -- | -- | -- | -- | -- | Standdown |"
    watch_md = "\n".join(watch_rows)
    md_content = f"""# BẢNG ĐIỀU KHIỂN TELEMETRY THỜI GIAN THỰC — VICTOR SENTINEL 24/7 (BAN 9)
**Thời gian cập nhật**: `{now_dt} ICT` | **Chu kỳ quét**: `15 giây/lần` (VPS Direct Feed)  
**Tài khoản giám sát**: Chủ tịch **Trần Quốc Thiên Phước** | **TCBS**: `105C307855`  
**Tiền mặt thật (Cash)**: `{cash_vnd:,.0f} VNĐ` | **Cổ phiếu Live**: `{total_market_val:,.0f} VNĐ` (`{total_unrealized_pnl:+,.0f} VNĐ` / `{total_pnl_pct:+.2f}%`) | **Tổng NAV Live**: **`{total_nav:,.0f} VNĐ`**

---

## 1. VỊ THẾ ĐANG NẮM GIỮ (GIÁM SÁT STOP 2xATR & CHỐT LỜI)
| Mã CP | Doanh Nghiệp | SL | Giá Vốn | Thị Giá Live | Lãi/Lỗ Ròng | Stop 2xATR | TP1 | Buy-Up % | Trạng Thái |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
{held_md}

---

## 2. RADAR WATCHLIST CHỨNG KHOÁN VIỆT NAM (CẢNH BÁO MỌI PHIÊN)
| Mã CP | Doanh Nghiệp | Thị Giá Live | Vùng Mua LO | Stop 2xATR | TP1 | Buy-Up % | Tín Hiệu Victor |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
{watch_md}
"""
    TELEMETRY_MD.write_text(md_content, encoding="utf-8")


def broadcast_status_to_telegram(quotes: Dict[str, Dict[str, Any]]) -> bool:
    now_str = _ict_now().strftime("%H:%M:%S")
    ssot_state = load_dynamic_ssot_state()
    cfg_map = ssot_state["config"]
    cash_vnd = ssot_state["cash_vnd"]
    held_parts = []
    stock_val = 0.0
    for sym, cfg in cfg_map.items():
        if cfg["is_holding"]:
            p = float(quotes.get(sym, {}).get("price") or cfg["current_price"] or 0.0)
            stock_val += p * cfg["shares"]
            pnl = (p - cfg["entry_price"]) * cfg["shares"]
            held_parts.append(f"• *{sym} ({cfg['shares']} CP)*: `{p:,.0f} ₫` (`{pnl:+,.0f} ₫`) | Stop `{cfg['stop_loss']:,.0f} ₫`")

    held_str = "\n".join(held_parts) if held_parts else "• Đang giữ 100% Tiền mặt (0 CP)"
    total_nav = cash_vnd + stock_val
    msg = (
        f"🛡️ *[VICTOR SENTINEL 24/7 — BÁO CÁO TRỰC CHIẾN REALTIME TCBS 105C307855]*\n"
        f"⏱️ *Thời gian*: `{now_str} ICT` | *Cổng*: `VPS Direct Feed`\n"
        f"💰 *Tổng NAV Live*: `{total_nav:,.0f} VNĐ` (Cash: `{cash_vnd:,.0f} VNĐ` | CP: `{stock_val:,.0f} VNĐ`)\n"
        f"{held_str}"
    )
    return dispatch_message("alerts", msg)


def main():
    parser = argparse.ArgumentParser(description="Victor Autonomous Sentinel — 24/7 Dynamic Monitoring")
    parser.add_argument("--daemon", action="store_true", help="Chạy chế độ nền liên tục mỗi 15 giây")
    parser.add_argument("--scan-once", action="store_true", help="Quét rà soát 1 lần, cập nhật telemetry và thoát")
    parser.add_argument("--interval", type=int, default=15, help="Chu kỳ quét (giây), mặc định 15s")
    parser.add_argument("--broadcast-status", action="store_true", help="Bắn báo cáo trạng thái tức thời lên Telegram")

    args = parser.parse_args()
    SENTINEL_DIR.mkdir(parents=True, exist_ok=True)

    if args.broadcast_status:
        quotes = fetch_live_quotes()
        success = broadcast_status_to_telegram(quotes)
        print(f"[+] Bắn báo cáo trạng thái Telegram: {'THÀNH CÔNG' if success else 'THẤT BẠI'}")
        return

    if args.scan_once:
        quotes = fetch_live_quotes()
        events = check_triggers_and_alert(quotes, notify_telegram=False)
        update_telemetry(quotes)
        now_str = _ict_now().strftime("%H:%M:%S")
        print(f"[{now_str}] Quét Victor 24/7 hoàn tất ({len(quotes)} mã, {len(events)} trigger).")
        return

    interval = args.interval or 15
    print("=" * 85)
    print("  APEX SENTINEL (VICTOR BAN 9) — GIÁM SÁT REALTIME 24/7 XUYÊN MỌI PHIÊN")
    print(f"  Chu kỳ quét: mỗi {interval}s qua VPS Live Datafeed | Đồng bộ War-Room & Vault")
    print("=" * 85)

    iteration = 0
    try:
        while True:
            iteration += 1
            quotes = fetch_live_quotes()
            events = check_triggers_and_alert(quotes, notify_telegram=True)
            update_telemetry(quotes)

            now_dt = _ict_now()
            now_str = now_dt.strftime("%H:%M:%S")
            now_hm = now_dt.strftime("%H:%M")
            is_off_hours = (now_dt.weekday() >= 5) or (now_hm < "08:30") or (now_hm > "15:00") or ("11:30" <= now_hm < "13:00")
            current_interval = max(interval, 45) if is_off_hours else interval
            hdb_p = float(quotes.get("HDB", {}).get("price") or 0)
            msh_p = float(quotes.get("MSH", {}).get("price") or 0)
            baf_p = float(quotes.get("BAF", {}).get("price") or 0)
            print(f"[{now_str}] #{iteration} Triggers={len(events)} | HDB={hdb_p:,.0f} MSH={msh_p:,.0f} BAF={baf_p:,.0f}")
            time.sleep(current_interval)
    except KeyboardInterrupt:
        print("[*] Đã dừng tiến trình giám sát Sentinel an toàn.")


if __name__ == "__main__":
    main()
