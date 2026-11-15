#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APEX EXECUTION SLIPPAGE & BULL-TRAP RETROSPECTION TRACKER (PHASE 2.2)
File: scripts/execution_slippage_tracker.py
Cơ quan chủ quản: Minh Quân (Ban 7 VN) & Ban 5 Tự Học Thích Nghi

Nhiệm vụ:
1. Ghi nhận các tín hiệu hành động từ War-Room / Khung Giờ Vàng (MUA / BREAKOUT / VÙNG GOM)
   với đầy đủ ngữ cảnh: Buy-Up %, RSI14, Độ rộng thị trường, Market Regime.
2. Đối chiếu giá khớp thực tế từ Form Sync TCInvest (POST /api/sync_tcinvest BUY) để đo:
   - Execution Slippage (bps & %) = (Giá khớp - Giá tín hiệu) / Giá tín hiệu * 10,000.
3. Hồi tố T+3 và T+5 từ dữ liệu lịch sử VPS HistDataFeed:
   - Phát hiện tỷ lệ Bull-Trap (tín hiệu xanh lúc báo nhưng gãy sau T+3/T+5).
   - Tự động tinh chỉnh bộ lọc chống Bull-Trap trong `config/war_room_adaptive_filters.json`.
"""

import sys
import os
import json
import time
import datetime
import threading
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Dict, Any, List, Optional

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CONFIG_DIR = BASE_DIR / "config"
TRACKER_FILE = DATA_DIR / "war_room_signal_tracker.json"
ADAPTIVE_FILTERS_FILE = CONFIG_DIR / "war_room_adaptive_filters.json"

sys.path.insert(0, str(BASE_DIR))

_TRACKER_LOCK = threading.Lock()

DEFAULT_ADAPTIVE_FILTERS = {
    "min_buy_up_pct": 58.0,
    "max_rsi_buy": 70.0,
    "min_breadth_pct": 32.0,
    "max_slippage_warn_bps": 60.0,
    "total_signals_tracked": 0,
    "evaluated_signals": 0,
    "hit_rate_t3_pct": 0.0,
    "hit_rate_t5_pct": 0.0,
    "hit_rate_t10_pct": 0.0,
    "hit_rate_t20_pct": 0.0,
    "multi_horizon_attribution": {
        "T+3": {"samples": 0, "hit_rate_pct": 0.0, "avg_return_pct": 0.0},
        "T+5": {"samples": 0, "hit_rate_pct": 0.0, "avg_return_pct": 0.0},
        "T+10": {"samples": 0, "hit_rate_pct": 0.0, "avg_return_pct": 0.0},
        "T+20": {"samples": 0, "hit_rate_pct": 0.0, "avg_return_pct": 0.0},
    },
    "bull_trap_rate_pct": 0.0,
    "avg_slippage_bps": 0.0,
    "tuning_note": "Ngưỡng khởi tạo chuẩn V4.0 (BuyUp >= 58%, RSI <= 70, Độ rộng >= 32%)",
    "last_tuned_at": "",
}


def _get_ict_now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc).astimezone(
        datetime.timezone(datetime.timedelta(hours=7))
    )


def _load_tracker_list() -> List[Dict[str, Any]]:
    if not TRACKER_FILE.exists():
        return []
    try:
        data = json.loads(TRACKER_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _save_tracker_list(records: List[Dict[str, Any]]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    TRACKER_FILE.write_text(
        json.dumps(records[:500], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_adaptive_filters() -> Dict[str, Any]:
    with _TRACKER_LOCK:
        if ADAPTIVE_FILTERS_FILE.exists():
            try:
                cfg = json.loads(ADAPTIVE_FILTERS_FILE.read_text(encoding="utf-8"))
                merged = DEFAULT_ADAPTIVE_FILTERS.copy()
                merged.update(cfg)
                return merged
            except Exception:
                pass
        return DEFAULT_ADAPTIVE_FILTERS.copy()


def _save_adaptive_filters(cfg: Dict[str, Any]) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    ADAPTIVE_FILTERS_FILE.write_text(
        json.dumps(cfg, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def record_signal_if_new(
    symbol: str,
    signal_type: str,
    signal_price: float,
    buy_up_pct: float = 50.0,
    rsi14: float = 50.0,
    breadth_pct: float = 50.0,
    regime_id: str = "SIDEWAY_CHOPPY",
    trading_date: Optional[str] = None,
    signal_time: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    sym = symbol.upper().strip()
    if not sym or signal_price <= 0:
        return None
    now_ict = _get_ict_now()
    t_date = trading_date or now_ict.strftime("%Y-%m-%d")
    t_time = signal_time or now_ict.strftime("%H:%M:%S")
    sig_id = f"SIG_{t_date}_{sym}_{signal_type.upper()}"

    with _TRACKER_LOCK:
        records = _load_tracker_list()
        if any(r.get("signal_id") == sig_id for r in records):
            return None
        rec = {
            "signal_id": sig_id,
            "symbol": sym,
            "signal_date": t_date,
            "signal_time": t_time,
            "signal_type": signal_type.upper(),
            "signal_price": round(float(signal_price), 2),
            "buy_up_pct": round(float(buy_up_pct), 1),
            "rsi14": round(float(rsi14), 1),
            "breadth_pct": round(float(breadth_pct), 1),
            "regime_id": regime_id,
            "executed_price": None,
            "executed_shares": 0,
            "slippage_bps": None,
            "slippage_pct": None,
            "t3_price": None,
            "t3_return_pct": None,
            "t5_price": None,
            "t5_return_pct": None,
            "t10_price": None,
            "t10_return_pct": None,
            "t20_price": None,
            "t20_return_pct": None,
            "outcome": "PENDING",
            "updated_at": now_ict.strftime("%Y-%m-%d %H:%M:%S"),
        }
        records.insert(0, rec)
        _save_tracker_list(records)

    try:
        from scripts.apex_cloud_db_sync import ApexCloudDBSync
        ApexCloudDBSync.sync_signal(rec)
    except Exception:
        pass
    return rec


def record_execution_fill(
    symbol: str,
    executed_price: float,
    shares: int = 0,
    fill_date: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Đối chiếu giá khớp thực tế (từ Sync TCInvest BUY) với tín hiệu War-Room gần nhất."""
    sym = symbol.upper().strip()
    if not sym or executed_price <= 0:
        return None
    now_ict = _get_ict_now()
    f_date = fill_date or now_ict.strftime("%Y-%m-%d")

    updated_rec = None
    with _TRACKER_LOCK:
        records = _load_tracker_list()
        for r in records:
            if r.get("symbol") == sym and r.get("executed_price") is None:
                sig_p = float(r.get("signal_price", 0.0))
                if sig_p > 0:
                    slip_pct = ((float(executed_price) - sig_p) / sig_p) * 100.0
                    slip_bps = slip_pct * 100.0
                else:
                    slip_pct = 0.0
                    slip_bps = 0.0
                r["executed_price"] = round(float(executed_price), 2)
                r["executed_shares"] = int(shares)
                r["executed_date"] = f_date
                r["slippage_pct"] = round(slip_pct, 3)
                r["slippage_bps"] = round(slip_bps, 1)
                r["updated_at"] = now_ict.strftime("%Y-%m-%d %H:%M:%S")
                updated_rec = dict(r)
                break

        if updated_rec is None:
            sig_id = f"FILL_{f_date}_{sym}_{int(time.time())}"
            updated_rec = {
                "signal_id": sig_id,
                "symbol": sym,
                "signal_date": f_date,
                "signal_time": now_ict.strftime("%H:%M:%S"),
                "signal_type": "DIRECT_EXECUTION",
                "signal_price": round(float(executed_price), 2),
                "buy_up_pct": 50.0,
                "rsi14": 50.0,
                "breadth_pct": 50.0,
                "regime_id": "LIVE_EXECUTION",
                "executed_price": round(float(executed_price), 2),
                "executed_shares": int(shares),
                "executed_date": f_date,
                "slippage_pct": 0.0,
                "slippage_bps": 0.0,
                "t3_price": None,
                "t3_return_pct": None,
                "t5_price": None,
                "t5_return_pct": None,
                "t10_price": None,
                "t10_return_pct": None,
                "t20_price": None,
                "t20_return_pct": None,
                "outcome": "PENDING",
                "updated_at": now_ict.strftime("%Y-%m-%d %H:%M:%S"),
            }
            records.insert(0, updated_rec)

        _save_tracker_list(records)

    try:
        from scripts.apex_cloud_db_sync import ApexCloudDBSync
        ApexCloudDBSync.sync_signal(updated_rec)
    except Exception:
        pass
    return updated_rec


def _fetch_daily_bars_vps(symbol: str, days_back: int = 35) -> List[Dict[str, Any]]:
    now_ts = int(time.time())
    t1 = now_ts - 86400 * days_back
    url = f"https://histdatafeed.vps.com.vn/tradingview/history?symbol={urllib.parse.quote(symbol)}&resolution=D&from={t1}&to={now_ts}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        if data.get("s") != "ok":
            return []
        ts_list = data.get("t", [])
        closes = data.get("c", [])
        bars = []
        for t_epoch, c_val in zip(ts_list, closes):
            d_str = datetime.datetime.fromtimestamp(t_epoch, tz=datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d")
            bars.append({"date": d_str, "close": round(float(c_val) * 1000.0, 2)})
        return bars
    except Exception:
        return []


def evaluate_matured_signals(use_network: bool = True) -> Dict[str, Any]:
    """
    Hồi tố các tín hiệu đã qua T+3 / T+5 / T+10 / T+20 ngày giao dịch, tính Hit Rate & Bull-Trap Rate,
    và tự động tinh chỉnh bộ lọc chống Bull-Trap trong `config/war_room_adaptive_filters.json`.
    """
    now_ict = _get_ict_now()
    bars_cache: Dict[str, List[Dict[str, Any]]] = {}

    with _TRACKER_LOCK:
        records = _load_tracker_list()
        if use_network:
            pending_syms = sorted({
                r.get("symbol", "")
                for r in records
                if r.get("symbol") and (r.get("outcome") in ("PENDING", "OPEN") or r.get("t20_price") is None)
            })
            for sym in pending_syms:
                bars_cache[sym] = _fetch_daily_bars_vps(sym, days_back=45)

        changed_recs: List[Dict[str, Any]] = []
        for r in records:
            sym = r.get("symbol", "")
            s_date = r.get("signal_date", "")
            base_p = float(r.get("executed_price") or r.get("signal_price") or 0.0)
            if not sym or not s_date or base_p <= 0:
                continue

            bars = bars_cache.get(sym, [])
            after_bars = [b for b in bars if b["date"] > s_date]
            updated_row = False
            for idx_n, field_p, field_r in (
                (2, "t3_price", "t3_return_pct"),
                (4, "t5_price", "t5_return_pct"),
                (9, "t10_price", "t10_return_pct"),
                (19, "t20_price", "t20_return_pct"),
            ):
                if len(after_bars) > idx_n and r.get(field_p) is None:
                    px_n = float(after_bars[idx_n]["close"])
                    r[field_p] = px_n
                    r[field_r] = round(((px_n - base_p) / base_p) * 100.0, 2)
                    updated_row = True

            if updated_row:
                r["updated_at"] = now_ict.strftime("%Y-%m-%d %H:%M:%S")
                changed_recs.append(dict(r))

            t3_ret = r.get("t3_return_pct")
            t5_ret = r.get("t5_return_pct")
            t10_ret = r.get("t10_return_pct")
            t20_ret = r.get("t20_return_pct")
            eval_ret = t20_ret if t20_ret is not None else (t10_ret if t10_ret is not None else t5_ret)
            if eval_ret is not None:
                if float(eval_ret) >= 1.5:
                    r["outcome"] = "WIN"
                elif float(eval_ret) <= -3.0:
                    r["outcome"] = "BULL_TRAP"
                else:
                    r["outcome"] = "NEUTRAL_HOLD"
            elif t3_ret is not None:
                if float(t3_ret) <= -3.5:
                    r["outcome"] = "BULL_TRAP"
                elif float(t3_ret) >= 2.0:
                    r["outcome"] = "WIN_EARLY"
                else:
                    r["outcome"] = "OPEN"

        if changed_recs:
            _save_tracker_list(records)

        # Tổng hợp KPI đa chu kỳ T+3 / T+5 / T+10 / T+20 & Tự tinh chỉnh bộ lọc Bull-Trap
        def _horizon_stats(field_r: str) -> Dict[str, Any]:
            rows = [r for r in records if r.get(field_r) is not None]
            if not rows:
                return {"samples": 0, "hit_rate_pct": 0.0, "avg_return_pct": 0.0}
            rets = [float(r[field_r]) for r in rows]
            hits = sum(1 for x in rets if x > 0)
            return {
                "samples": len(rows),
                "hit_rate_pct": round((hits / len(rows)) * 100.0, 1),
                "avg_return_pct": round(sum(rets) / len(rets), 2),
            }

        mh_attr = {
            "T+3": _horizon_stats("t3_return_pct"),
            "T+5": _horizon_stats("t5_return_pct"),
            "T+10": _horizon_stats("t10_return_pct"),
            "T+20": _horizon_stats("t20_return_pct"),
        }
        slips = [float(r["slippage_bps"]) for r in records if r.get("slippage_bps") is not None]
        traps = [r for r in records if r.get("outcome") == "BULL_TRAP"]
        matured = [r for r in records if r.get("outcome") not in ("PENDING", None)]

        hit_t3 = mh_attr["T+3"]["hit_rate_pct"]
        hit_t5 = mh_attr["T+5"]["hit_rate_pct"]
        hit_t10 = mh_attr["T+10"]["hit_rate_pct"]
        hit_t20 = mh_attr["T+20"]["hit_rate_pct"]
        trap_rate = round((len(traps) / len(matured)) * 100.0, 1) if matured else 0.0
        avg_slip = round(sum(slips) / len(slips), 1) if slips else 0.0

        filters = DEFAULT_ADAPTIVE_FILTERS.copy()
        if ADAPTIVE_FILTERS_FILE.exists():
            try:
                filters.update(json.loads(ADAPTIVE_FILTERS_FILE.read_text(encoding="utf-8")))
            except Exception:
                pass

        min_bu = float(filters.get("min_buy_up_pct", 58.0))
        max_rsi = float(filters.get("max_rsi_buy", 70.0))
        min_br = float(filters.get("min_breadth_pct", 32.0))
        note = "Ổn định theo bộ lọc chuẩn."

        if len(matured) >= 3:
            if trap_rate >= 30.0:
                min_bu = min(68.0, round(min_bu + 2.0, 1))
                max_rsi = max(64.0, round(max_rsi - 1.5, 1))
                min_br = min(45.0, round(min_br + 3.0, 1))
                note = f"Siết bộ lọc Bull-Trap (TrapRate {trap_rate:.1f}%): nâng BuyUp >= {min_bu}%, hạ RSI <= {max_rsi}."
            elif hit_t5 >= 65.0 and trap_rate <= 15.0:
                min_bu = max(54.0, round(min_bu - 1.0, 1))
                max_rsi = min(73.0, round(max_rsi + 1.0, 1))
                note = f"Nới nhẹ biên độ săn điểm (HitRate T+5 {hit_t5:.1f}%, Trap {trap_rate:.1f}%)."

        filters.update({
            "min_buy_up_pct": min_bu,
            "max_rsi_buy": max_rsi,
            "min_breadth_pct": min_br,
            "total_signals_tracked": len(records),
            "evaluated_signals": len(matured),
            "hit_rate_t3_pct": hit_t3,
            "hit_rate_t5_pct": hit_t5,
            "hit_rate_t10_pct": hit_t10,
            "hit_rate_t20_pct": hit_t20,
            "multi_horizon_attribution": mh_attr,
            "bull_trap_rate_pct": trap_rate,
            "avg_slippage_bps": avg_slip,
            "tuning_note": note,
            "last_tuned_at": now_ict.strftime("%Y-%m-%d %H:%M:%S"),
        })
        _save_adaptive_filters(filters)

    for rec in changed_recs:
        try:
            from scripts.apex_cloud_db_sync import ApexCloudDBSync
            ApexCloudDBSync.sync_signal(rec)
        except Exception:
            pass

    return {
        "filters": filters,
        "recent_signals": records[:10],
    }


def get_tracker_summary() -> Dict[str, Any]:
    with _TRACKER_LOCK:
        records = _load_tracker_list()
        filters = DEFAULT_ADAPTIVE_FILTERS.copy()
        if ADAPTIVE_FILTERS_FILE.exists():
            try:
                filters.update(json.loads(ADAPTIVE_FILTERS_FILE.read_text(encoding="utf-8")))
            except Exception:
                pass
        slips = [float(r["slippage_bps"]) for r in records if r.get("slippage_bps") is not None]
        filters["total_signals_tracked"] = len(records)
        if slips:
            filters["avg_slippage_bps"] = round(sum(slips) / len(slips), 1)
        return {
            "filters": filters,
            "recent_signals": records[:8],
        }


if __name__ == "__main__":
    summary = evaluate_matured_signals(use_network=True)
    print("=== EXECUTION SLIPPAGE & BULL-TRAP TRACKER ===")
    print(json.dumps(summary["filters"], ensure_ascii=False, indent=2))
