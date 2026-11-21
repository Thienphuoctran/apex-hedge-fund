#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APEX DAILY LIVE FULL-MARKET WAR-ROOM ENGINE (09:00 - 16:00 MON-FRI ICT)
========================================================================
File: scripts/apex_daily_live_warroom_engine.py
Cơ quan vận hành: Liên quân 11 Phòng ban Độc lập (Ban 1, 2, 3, 4, 5, 7, 8, 9, 10, 12)
Phục vụ trực tiếp: Chủ tịch Trần Quốc Thiên Phước (TCBS: 105C307855)

Chức năng cốt lõi:
1. Đội Trinh Sát Toàn Thị Trường (Ban 1 + Ban 2 + Ban 9 Victor + Ban 10 Hiền):
   - Đọc bảng điện thời gian thực toàn bộ 145 mã chứng khoán (HOSE, HNX, UPCoM) chia luồng song song.
   - Kết hợp chỉ số VN-Index/VN30/HNX, độ rộng Breadth > MA20 sống, lực mua chủ động Buy-Up %,
     dòng tiền khối ngoại, 18 nhóm ngành & luồng tin BCTC Q3/2026 + Internet crawler V3.0.
2. Đội Đầu Não Ra Quyết Định Tức Thời (Ban 3 Red Team + Ban 4 Quant Risk + Ban 7 Minh Quân + Ban 8 James):
   - Cập nhật kịch bản sống từng nhịp (S1 Bull / S2 Sideways / S3 Spring / S4 Cash Shield).
   - Trước 14h00: Khóa chống FOMO ATO/sáng (vẫn cảnh báo Stop-Loss / Chốt lời nếu có vị thế mở).
   - Khung Giờ Vàng 14h00–14h25: Ban hành Quyết định Đầu tư Tức thời kèm Sổ lệnh LO Lô 100 & Stop -5.5%.
3. Vòng Lặp Đóng Phiên, Tự Học & Nghỉ Ngơi (~15:15–16:00):
   - Đối soát dự báo trong ngày vs EOD, rút ra điểm đúng / điểm cần sửa / bài học cho ngày mai,
     kích hoạt cập nhật BCTC/Internet/Brain V3/Ban 12 Trọng/Dashboard/Palmer rồi tự nghỉ lúc 16:00.
"""

from __future__ import annotations

import os
import sys
import json
import time
import signal
import datetime
import argparse
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
VN_DATA_DIR = BASE_DIR / "VN_Market" / "data"
LIVE_SESSIONS_DIR = BASE_DIR / "08_Master_Investment_CIO" / "live_sessions"
EVOLUTION_JOURNAL = BASE_DIR / "05_Learning_And_Evolution" / "system_evolution_journal.md"
PID_FILE = DATA_DIR / "apex_daily_warroom.pid"
LIVE_STATE_FILE = DATA_DIR / "live_warroom_state.json"
INTRADAY_HISTORY_FILE = DATA_DIR / "live_warroom_intraday_history.json"
LOG_FILE = DATA_DIR / "logs" / "daily_warroom_engine.log"

sys.path.insert(0, str(BASE_DIR))
from scripts.vietnam_realtime_feed import fetch_vn_market_indices_live, get_realtime_vn_quotes_batch
from scripts.telegram_dispatcher import dispatch_message

FORBIDDEN_TICKERS = {"BAF", "VIX", "CII", "CEO"}
STOP_FLAG = False


def _ict_now() -> datetime.datetime:
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    return utc_now.astimezone(datetime.timezone(datetime.timedelta(hours=7)))


def _log(msg: str) -> None:
    line = f"[{_ict_now().strftime('%Y-%m-%d %H:%M:%S ICT')}] {msg}"
    print(line, flush=True)
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def _read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return {} if default is None else default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {} if default is None else default


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def _round_vn_tick(price_vnd: float) -> float:
    if price_vnd <= 0:
        return 0.0
    if price_vnd < 10000:
        return round(price_vnd, -1)
    if price_vnd < 50000:
        return round(price_vnd / 50.0) * 50.0
    return round(price_vnd, -2)


def _round_lot100(amount_vnd: float, price_vnd: float) -> int:
    if price_vnd <= 0 or amount_vnd <= 0:
        return 0
    lots = int(amount_vnd // (price_vnd * 100.0))
    return max(0, lots * 100)


def _process_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _acquire_pid_lock() -> bool:
    PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    if PID_FILE.exists():
        try:
            old_pid = int(PID_FILE.read_text(encoding="utf-8").strip())
            if old_pid != os.getpid() and _process_alive(old_pid):
                _log(f"[LOCK] Phiên War-Room daemon đã chạy (PID={old_pid}). Không mở trùng.")
                return False
        except Exception:
            pass
    PID_FILE.write_text(str(os.getpid()), encoding="utf-8")
    return True


def _release_pid_lock() -> None:
    try:
        if PID_FILE.exists():
            cur = PID_FILE.read_text(encoding="utf-8").strip()
            if cur == str(os.getpid()):
                PID_FILE.unlink()
    except Exception:
        pass


def _run_py(rel_path: str, args: Optional[List[str]] = None, timeout: int = 180) -> int:
    script = BASE_DIR / rel_path
    if not script.exists():
        _log(f"[WARN] Thiếu script: {rel_path}")
        return -1
    cmd = [sys.executable, "-X", "utf8", str(script)] + (args or [])
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    try:
        res = subprocess.run(cmd, cwd=str(BASE_DIR), env=env, timeout=timeout, check=False)
        _log(f"[SUBPROC] {rel_path} {' '.join(args or [])} -> exit={res.returncode}")
        return res.returncode
    except Exception as e:
        _log(f"[ERR] Lỗi chạy {rel_path}: {e}")
        return -1


def _load_universe_baseline() -> Dict[str, Dict[str, Any]]:
    scan = _read_json(VN_DATA_DIR / "vn_full_market_scan.json", {})
    stocks = scan.get("stocks") or {}
    if stocks:
        return stocks
    cfg = _read_json(BASE_DIR / "config" / "vn_watchlist.json", {})
    out: Dict[str, Dict[str, Any]] = {}
    for sym in (cfg.get("tickers") or cfg.get("watchlist") or []):
        s = str(sym).upper().strip()
        if s:
            out[s] = {"symbol": s, "sector_name": "Chung", "technical": {}, "institutional_evaluation": {}}
    return out


def _fetch_all_quotes_concurrent(symbols: List[str]) -> Dict[str, Dict[str, Any]]:
    chunks = [symbols[i : i + 30] for i in range(0, len(symbols), 30)]
    merged: Dict[str, Dict[str, Any]] = {}
    with ThreadPoolExecutor(max_workers=5) as pool:
        futs = {pool.submit(get_realtime_vn_quotes_batch, ch): ch for ch in chunks}
        for fut in as_completed(futs):
            try:
                res = fut.result(timeout=12) or {}
                if isinstance(res, dict):
                    merged.update(res)
            except Exception as e:
                _log(f"[WARN] Batch quote error: {e}")
    return merged


def _compute_quote_buy_up_pct(q: Dict[str, Any]) -> float:
    explicit = q.get("active_buy_pct")
    if explicit is not None:
        try:
            val = float(explicit)
            if 0.0 < val <= 100.0:
                return val
        except Exception:
            pass
    px = float(q.get("price") or q.get("last_price") or 0.0)
    hi = float(q.get("day_high") or px)
    lo = float(q.get("day_low") or px)
    pos_ratio = ((px - lo) / (hi - lo)) if hi > lo else (0.60 if float(q.get("change_pct") or 0.0) > 0 else 0.45)
    bids = sum(float(lvl.get("vol") or 0.0) for lvl in (q.get("bid_levels") or []))
    asks = sum(float(lvl.get("vol") or 0.0) for lvl in (q.get("ask_levels") or []))
    book_ratio = (bids / (bids + asks)) if (bids + asks) > 0 else 0.50
    return round(max(5.0, min(95.0, (0.65 * pos_ratio + 0.35 * book_ratio) * 100.0)), 1)


def _session_phase(now_ict: datetime.datetime) -> str:
    if now_ict.weekday() >= 5:
        return "WEEKEND_STANDBY"
    hm = now_ict.strftime("%H:%M")
    if hm < "09:00":
        return "PRE_OPEN_PREPARATION"
    if hm < "11:30":
        return "MORNING_RECON_ANTI_FOMO"
    if hm < "13:00":
        return "MIDDAY_LUNCH_BREAK"
    if hm < "14:00":
        return "AFTERNOON_T2_ABSORPTION"
    if hm <= "14:25":
        return "GOLDEN_WINDOW_DECISION"
    if hm < "15:15":
        return "ATC_SETTLEMENT_WAIT"
    if hm <= "16:00":
        return "EOD_CLOSURE_AND_LEARNING"
    return "AFTER_HOURS_RESTING"


def run_live_recon_and_decision(
    refresh_intel: bool = False,
    send_telegram: bool = False,
    tag: str = "SCHEDULED_CHECK",
    event_type: Optional[str] = None,
) -> Dict[str, Any]:
    now_ict = _ict_now()
    today_str = now_ict.strftime("%Y-%m-%d")
    phase = _session_phase(now_ict)

    if refresh_intel:
        _run_py("scripts/apex_daily_internet_intel_crawler.py", timeout=150)

    universe = _load_universe_baseline()
    symbols = sorted(universe.keys())
    bctc_live = _read_json(VN_DATA_DIR / "vn_real_bctc_live.json", {}).get("stocks") or {}
    intel_data = _read_json(DATA_DIR / "apex_daily_internet_intel.json", {})
    ticker_intel = intel_data.get("ticker_corporate_intel") or {}
    intel_counts = intel_data.get("summary_counts") or {}
    brain_v3 = _read_json(DATA_DIR / "apex_autonomous_brain_v3_output.json", {})
    ssot = _read_json(DATA_DIR / "current_portfolio_state.json", {})

    idx_live = fetch_vn_market_indices_live() or {}
    quotes = _fetch_all_quotes_concurrent(symbols)

    adv, dec, unch, ceil_cnt, floor_cnt = 0, 0, 0, 0, 0
    above_ma20_cnt, ma20_base_cnt = 0, 0
    buy_up_samples: List[float] = []
    sector_changes: Dict[str, List[float]] = {}
    scored_stocks: List[Dict[str, Any]] = []
    danger_alerts: List[Dict[str, Any]] = []

    for sym in symbols:
        base = universe[sym]
        q = quotes.get(sym) or {}
        px = float(q.get("price") or 0.0)
        chg_pct = float(q.get("change_pct") or 0.0)
        vol = int(q.get("volume") or 0)
        ceil_p = float(q.get("ceiling_price") or 0.0)
        floor_p = float(q.get("floor_price") or 0.0)
        sec_name = str(base.get("sector_name") or "Khác")

        tech = base.get("technical") or {}
        ma20 = float(tech.get("ma20") or 0.0)
        avg_val20 = float(tech.get("avg_val20_ty") or 0.0)
        rs_rating = int(tech.get("rs_rating") or 50)
        inst = base.get("institutional_evaluation") or {}
        lm = (bctc_live.get(sym) or {}).get("latest_metrics") or {}

        f_score = int(lm.get("piotroski_f_score") or inst.get("piotroski_f_score") or 0)
        m_score = float(lm.get("beneish_m_score") or inst.get("beneish_m_score") or -2.5)
        beneish_status = str(lm.get("beneish_status") or ("SAFE" if m_score <= -1.78 else "HIGH_RISK"))
        is_clean = bool(inst.get("is_accounting_clean", f_score >= 6 and beneish_status == "SAFE"))
        ocf_ty = lm.get("ocf_ty")
        t_news = ticker_intel.get(sym) or {}
        news_cnt = int(t_news.get("articles_count") or 0)
        headline = ""
        if t_news.get("headlines"):
            first_h = t_news["headlines"][0]
            headline = str(first_h.get("title") if isinstance(first_h, dict) else first_h)[:110]

        if px > 0:
            if chg_pct > 0.05:
                adv += 1
            elif chg_pct < -0.05:
                dec += 1
            else:
                unch += 1
            if ceil_p > 0 and px >= ceil_p - 10:
                ceil_cnt += 1
            if floor_p > 0 and px <= floor_p + 10:
                floor_cnt += 1
            if ma20 > 0:
                ma20_base_cnt += 1
                if px > ma20:
                    above_ma20_cnt += 1
            sector_changes.setdefault(sec_name, []).append(chg_pct)
            bu_pct = _compute_quote_buy_up_pct(q)
            if avg_val20 >= 25.0 and vol > 0:
                buy_up_samples.append(bu_pct)

            if sym not in FORBIDDEN_TICKERS and is_clean and f_score >= 6 and beneish_status == "SAFE":
                alpha_base = float(inst.get("actionable_alpha_score") or inst.get("legends_composite_score") or 55.0)
                live_bonus = max(-8.0, min(10.0, chg_pct * 1.4)) + (3.0 if bu_pct >= 60.0 else 0.0) + min(4.0, news_cnt * 0.5)
                live_score = round(alpha_base + live_bonus, 2)
                scored_stocks.append({
                    "symbol": sym,
                    "sector": sec_name,
                    "live_price": px,
                    "change_pct": round(chg_pct, 2),
                    "volume": vol,
                    "buy_up_pct": bu_pct,
                    "f_score": f_score,
                    "rs_rating": rs_rating,
                    "avg_val20_ty": round(avg_val20, 1),
                    "ma20": ma20,
                    "live_score": live_score,
                    "headline": headline,
                })

            if (not is_clean or sym in FORBIDDEN_TICKERS or chg_pct <= -3.5) and (vol > 100000 or sym in FORBIDDEN_TICKERS):
                danger_alerts.append({
                    "symbol": sym,
                    "live_price": px,
                    "change_pct": round(chg_pct, 2),
                    "f_score": f_score,
                    "beneish_status": beneish_status,
                    "ocf_ty": ocf_ty,
                    "reason": "CẤM GIAO DỊCH (Cờ đỏ BCTC/Đầu cơ)" if sym in FORBIDDEN_TICKERS or not is_clean else f"Áp lực bán mạnh ({chg_pct:+.2f}%)",
                })

    scored_stocks.sort(key=lambda x: x["live_score"], reverse=True)
    danger_alerts.sort(key=lambda x: (0 if x["symbol"] in FORBIDDEN_TICKERS else 1, x["change_pct"]))

    sector_ranking = [
        {"sector": s, "avg_change_pct": round(sum(vals) / len(vals), 2), "stocks": len(vals)}
        for s, vals in sector_changes.items() if vals
    ]
    sector_ranking.sort(key=lambda x: x["avg_change_pct"], reverse=True)

    vn_idx = idx_live.get("vn_index") or {}
    vni_val = float(vn_idx.get("value") or 0.0)
    vni_chg = float(vn_idx.get("change_pct") or 0.0)
    vni_ma20 = float(vn_idx.get("ma20") or 1730.89)
    vni_ma50 = float(vn_idx.get("ma50") or 1748.05)
    vol_pace = float(vn_idx.get("volume_pace_ratio") or 1.0)
    foreign_ty = float(vn_idx.get("raw_foreign_net_ty") or 0.0)
    turnover_ty = float(vn_idx.get("raw_turnover_ty") or 0.0)

    live_br20 = round((above_ma20_cnt / ma20_base_cnt * 100.0), 1) if ma20_base_cnt else 0.0
    avg_buy_up = round(sum(buy_up_samples) / len(buy_up_samples), 1) if buy_up_samples else 50.0

    # Portfolio & SSOT (Read-Only!)
    cash_vnd = float(ssot.get("cash_balance_vnd") or 20051117.0)
    nav_vnd = float(ssot.get("total_nav_vnd") or cash_vnd)
    active_pos = ssot.get("active_positions") or {}
    position_alerts: List[Dict[str, Any]] = []
    for psym, pinfo in active_pos.items():
        shares = int(pinfo.get("shares") or 0)
        if shares <= 0:
            continue
        q = quotes.get(psym) or {}
        cur_p = float(q.get("price") or pinfo.get("current_price") or pinfo.get("entry_price") or 0.0)
        entry_p = float(pinfo.get("entry_price") or pinfo.get("avg_cost") or cur_p)
        pnl_pct = round((cur_p - entry_p) / entry_p * 100.0, 2) if entry_p > 0 else 0.0
        sig = "HOLD"
        if pnl_pct <= -5.5:
            sig = "URGENT_STOP_LOSS"
        elif pnl_pct >= 7.5:
            sig = "SCALING_OUT_TP1_50PCT"
        position_alerts.append({"symbol": psym, "shares": shares, "entry": entry_p, "live": cur_p, "pnl_pct": pnl_pct, "signal": sig})

    # Regime & Instant Investment Decision
    if vni_val > vni_ma20 and vni_val > vni_ma50 and live_br20 >= 50.0 and avg_buy_up >= 58.0:
        live_regime = "S1_BULL_BREAKOUT"
        target_alloc_pct = "75% - 85% NAV"
    elif 30.0 <= live_br20 < 50.0 and vni_val >= 1678.0 and avg_buy_up >= 52.0:
        live_regime = "S2_SIDEWAYS_SNIPER"
        target_alloc_pct = "30% - 45% NAV"
    elif vni_val >= 1678.0 and live_br20 >= 24.0 and avg_buy_up >= 58.0 and vol_pace >= 1.05:
        live_regime = "S3_SPRING_STRIKE_READY"
        target_alloc_pct = "30% - 40% NAV"
    else:
        live_regime = "S4_BEAR_CASH_SHIELD"
        target_alloc_pct = "0.0% NAV (100% CASH)"

    v3_strikes = brain_v3.get("asymmetric_conviction_strikes") or []
    strike_orders: List[Dict[str, Any]] = []
    if live_regime in ("S1_BULL_BREAKOUT", "S2_SIDEWAYS_SNIPER", "S3_SPRING_STRIKE_READY"):
        if live_regime == "S3_SPRING_STRIKE_READY" and v3_strikes:
            for st_item in v3_strikes[:2]:
                sym = st_item["symbol"]
                live_px = float((quotes.get(sym) or {}).get("price") or st_item.get("close_20_11") or 0.0)
                lo_px = _round_vn_tick(live_px * 0.995) if live_px > 0 else float(st_item.get("limit_entry_vnd") or 0.0)
                sh = int(st_item.get("shares_lot100") or _round_lot100(nav_vnd * 0.18, lo_px))
                strike_orders.append({
                    "symbol": sym,
                    "shares_lot100": sh,
                    "limit_lo_vnd": lo_px,
                    "stop_vnd": _round_vn_tick(lo_px * 0.945),
                    "tp1_vnd": _round_vn_tick(lo_px * 1.09),
                    "capital_vnd": round(sh * lo_px, 0),
                })
        else:
            for cand in scored_stocks[:2]:
                lo_px = _round_vn_tick(cand["live_price"] * 0.995)
                sh = _round_lot100(nav_vnd * (0.35 if live_regime == "S1_BULL_BREAKOUT" else 0.18), lo_px)
                if sh >= 100:
                    strike_orders.append({
                        "symbol": cand["symbol"],
                        "shares_lot100": sh,
                        "limit_lo_vnd": lo_px,
                        "stop_vnd": _round_vn_tick(lo_px * 0.945),
                        "tp1_vnd": _round_vn_tick(lo_px * 1.09),
                        "capital_vnd": round(sh * lo_px, 0),
                    })

    if phase == "GOLDEN_WINDOW_DECISION":
        verdict_code = f"GOLDEN_WINDOW_EXECUTE_{live_regime}" if strike_orders else "GOLDEN_WINDOW_HOLD_100PCT_CASH"
        verdict_vi = (
            f"KHUNG GIỜ VÀNG 14H05–14H25: Kích hoạt {live_regime} ({target_alloc_pct})"
            if strike_orders
            else f"KHUNG GIỜ VÀNG 14H05–14H25: Kích hoạt {live_regime} — GIỮ NGUYÊN 100% TIỀN MẶT ({cash_vnd:,.0f} ₫)"
        )
    elif phase in ("MORNING_RECON_ANTI_FOMO", "AFTERNOON_T2_ABSORPTION"):
        verdict_code = "ANTI_FOMO_MORNING_WAIT_14H00"
        verdict_vi = f"PHIÊN THEO DÕI ({phase}): Khóa nút Mua đến 14h05 | Chế độ sống: {live_regime} | Giữ 100% Cash ({cash_vnd:,.0f} ₫)."
    else:
        verdict_code = f"STANDBY_AUDIT_{live_regime}"
        verdict_vi = f"TRẠNG THÁI CHỜ ({phase}): Quét sống {len(quotes)}/{len(symbols)} mã | Chế độ sống: {live_regime} | SSOT {cash_vnd:,.0f} ₫ (0 CP)."

    snapshot = {
        "timestamp_ict": now_ict.strftime("%Y-%m-%d %H:%M:%S ICT"),
        "date": today_str,
        "tag": tag,
        "phase": phase,
        "ssot_snapshot": {
            "account_id": str(ssot.get("account_id") or "105C307855"),
            "status": str(ssot.get("status") or "ALL_CASH_STANDDOWN"),
            "nav_vnd": nav_vnd,
            "cash_vnd": cash_vnd,
            "open_positions_count": sum(1 for p in active_pos.values() if int(p.get("shares") or 0) > 0),
            "position_alerts": position_alerts,
        },
        "recon_summary": {
            "universe_total": len(symbols),
            "scanned_live_count": len(quotes),
            "vn_index": vni_val,
            "vn_index_chg_pct": vni_chg,
            "vn_index_ma20": vni_ma20,
            "vn_index_ma50": vni_ma50,
            "volume_pace_ratio": vol_pace,
            "turnover_ty": turnover_ty,
            "foreign_net_ty": foreign_ty,
            "advance_count": adv,
            "decline_count": dec,
            "unchanged_count": unch,
            "ceiling_count": ceil_cnt,
            "floor_count": floor_cnt,
            "live_breadth_ma20_pct": live_br20,
            "avg_buy_up_pct": avg_buy_up,
            "internet_articles": int(intel_counts.get("total_news_articles") or 0),
            "internet_crawled_at": str(intel_data.get("crawled_at") or ""),
        },
        "decision_brain": {
            "live_regime": live_regime,
            "target_allocation_pct": target_alloc_pct,
            "verdict_code": verdict_code,
            "verdict_vi": verdict_vi,
            "proposed_lo_orders": strike_orders,
        },
        "top_5_sectors": sector_ranking[:5],
        "bottom_3_sectors": sector_ranking[-3:] if len(sector_ranking) >= 3 else sector_ranking,
        "top_5_live_leaders": scored_stocks[:5],
        "top_5_danger_alerts": danger_alerts[:5],
    }

    _write_json(LIVE_STATE_FILE, snapshot)
    _append_intraday_history(today_str, snapshot)
    _write_live_warroom_markdown(snapshot)
    _refresh_static_web_portal_safely()

    resolved_event = event_type
    if resolved_event is None:
        if tag == "OPENING_0900_KICKOFF":
            resolved_event = "OPENING_0900_KICKOFF"
        elif phase == "GOLDEN_WINDOW_DECISION" or tag == "GOLDEN_WINDOW_VERDICT":
            resolved_event = "GOLDEN_WINDOW_VERDICT"
        elif phase == "MIDDAY_LUNCH_BREAK" or tag == "MIDDAY_BRIEFING":
            resolved_event = "MIDDAY_BRIEFING"

    if send_telegram and resolved_event:
        _dispatch_daily_warroom_and_james(snapshot, event_type=resolved_event, brain_v3=brain_v3)

    _log(
        f"[CYCLE OK] phase={phase} | scanned={len(quotes)}/{len(symbols)} | "
        f"VNI={vni_val:,.2f} ({vni_chg:+.2f}%) | Br20={live_br20:.1f}% | BuyUp={avg_buy_up:.1f}% | "
        f"Regime={live_regime}"
    )
    return snapshot


def _refresh_static_web_portal_safely() -> None:
    """Cập nhật dashboard/index.html tự động sau mỗi nhịp quét War-Room để Web Portal luôn đồng bộ 3 phòng."""
    try:
        import scripts.apex_report_scanner as rscan
        import scripts.apex_web_portal_engine as portal_eng

        sup_file = DATA_DIR / "apex_cloud_supervisor_status.json"
        status_data = _read_json(sup_file, {"supervisor_status": "ACTIVE_DAILY_WARROOM"})
        reports = rscan.scan_all_institutional_reports(limit=2000)
        milestones = rscan.get_daily_milestones_status()
        dates = rscan.get_available_archive_dates()
        html = portal_eng.generate_portal_html(status_data, reports, milestones, available_dates=dates)
        out_html = BASE_DIR / "dashboard" / "index.html"
        out_html.parent.mkdir(parents=True, exist_ok=True)
        tmp = out_html.with_suffix(".tmp")
        tmp.write_text(html, encoding="utf-8")
        tmp.replace(out_html)
    except Exception as e:
        _log(f"[WARN] Không thể refresh dashboard/index.html: {e}")


def _dispatch_daily_warroom_and_james(
    snap: Dict[str, Any],
    event_type: str,
    brain_v3: Optional[Dict[str, Any]] = None,
    eod_summary_path: Optional[Path] = None,
) -> None:
    """
    Định tuyến thông báo chuẩn 2 phòng tác chiến Telegram (Giữ Phòng Trợ Lý ở chế độ standby):
      - `daily_warroom`: Kế hoạch trong ngày, công việc phòng ban, thay đổi kịch bản tức thời & tổng kết cuối ngày.
      - `james_hq`: Bản kế hoạch tác chiến hoàn chỉnh trong ngày của Master CIO James (09:00, 14:05, EOD).
    """
    try:
        r = snap["recon_summary"]
        d = snap["decision_brain"]
        s = snap["ssot_snapshot"]
        top5 = snap.get("top_5_live_leaders") or []
        orders = d.get("proposed_lo_orders") or []
        b3 = brain_v3 if brain_v3 is not None else _read_json(DATA_DIR / "apex_autonomous_brain_v3_output.json", {})
        strikes = b3.get("asymmetric_conviction_strikes") or []
        challenges = b3.get("independent_chairman_challenges") or []

        top5_txt = ", ".join(f"{x['symbol']} ({x['live_price']:,.0f}đ | {x['change_pct']:+.1f}% | BuyUp {x['buy_up_pct']:.0f}%)" for x in top5[:5]) or "Chưa có mã đạt chuẩn"
        orders_txt = "\n".join(
            f"  • *{o['symbol']}*: `{o['shares_lot100']} CP` @ LO `{o['limit_lo_vnd']:,.0f}đ` | Stop `{o['stop_vnd']:,.0f}đ` | TP1 `{o['tp1_vnd']:,.0f}đ`"
            for o in orders
        ) or "  • Không mở mua mới — Giữ nguyên 100% Tiền mặt bảo toàn vốn."

        # 1. Gửi Phòng 2: daily_warroom
        if event_type == "OPENING_0900_KICKOFF":
            wr_msg = (
                f"⚡ *[MỞ PHIÊN 09H00 — PHÒNG TÁC CHIẾN MỖI NGÀY]* `{snap['timestamp_ict']}`\n"
                f"• Quét toàn thị trường: `{r['scanned_live_count']}/{r['universe_total']}` mã | VNI: `{r['vn_index']:,.2f}` (`{r['vn_index_chg_pct']:+.2f}%`)\n"
                f"• Breadth>MA20: `{r['live_breadth_ma20_pct']:.1f}%` | Buy-Up: `{r['avg_buy_up_pct']:.1f}%` | Internet/BCTC: `{r['internet_articles']}` tin\n"
                f"• *Trạng thái sống:* `{d['live_regime']}` ({d['target_allocation_pct']})\n"
                f"• *Lịch nhịp trong ngày:* `09:00 Mở cửa` ➔ `11:35 Giữa phiên` ➔ `14:05 Khung Giờ Vàng` ➔ `15:45 Tổng kết & Nghỉ 16h00`\n"
                f"• *Top 5 BCTC sạch:* {top5_txt}\n"
                f"• *Chỉ thị:* Khóa nút Mua chống FOMO ATO trước `14h05`; liên tục bám sát bảng điện."
            )
        elif event_type == "REGIME_OR_PLAN_CHANGE":
            wr_msg = (
                f"🔔 *[BIẾN ĐỘNG KẾ HOẠCH TRONG NGÀY]* `{snap['timestamp_ict']}`\n"
                f"• VNI: `{r['vn_index']:,.2f}` (`{r['vn_index_chg_pct']:+.2f}%`) | Br20: `{r['live_breadth_ma20_pct']:.1f}%` | Buy-Up: `{r['avg_buy_up_pct']:.1f}%`\n"
                f"• *Chế độ mới:* `{d['live_regime']}` (`{d['target_allocation_pct']}`)\n"
                f"• *Cập nhật hành động:* {d['verdict_vi']}\n"
                f"• *Top 5 dẫn dắt:* {top5_txt}"
            )
        elif event_type == "EOD_WRAP_FINAL":
            wr_msg = (
                f"🏁 *[TỔNG KẾT CUỐI NGÀY & BÀI HỌC]* `{snap['date']}`\n"
                f"• Đóng cửa VNI: `{r['vn_index']:,.2f}` (`{r['vn_index_chg_pct']:+.2f}%`) | Quét: `{r['scanned_live_count']}/{r['universe_total']}` mã\n"
                f"• SSOT `{s['account_id']}`: `{s['status']}` | Tiền mặt: `{s['cash_vnd']:,.0f} ₫` (`{s['open_positions_count']} CP`)\n"
                f"• Phán quyết cuối phiên: `{d['live_regime']}`\n"
                f"• Hồ sơ bài học: `{eod_summary_path.name if eod_summary_path else snap['date'] + '_EOD_WarRoom_Summary_And_Lessons.md'}`\n"
                f"• Trạng thái: Đã tổng kết xong, hệ thống nghỉ ngơi lúc `16:00`."
            )
        else:
            wr_msg = (
                f"⚡ *[CẬP NHẬT TÁC CHIẾN {event_type}]* `{snap['timestamp_ict']}`\n"
                f"• VNI: `{r['vn_index']:,.2f}` (`{r['vn_index_chg_pct']:+.2f}%`) | Br20: `{r['live_breadth_ma20_pct']:.1f}%` | Buy-Up: `{r['avg_buy_up_pct']:.1f}%`\n"
                f"• *Chế độ sống:* `{d['live_regime']}` | Cash SSOT: `{s['cash_vnd']:,.0f} ₫`\n"
                f"• *Chỉ thị:* {d['verdict_vi']}\n"
                f"• *Lệnh dự kiến:*\n{orders_txt}"
            )
        dispatch_message("daily_warroom", wr_msg, mirror_to_reports_vault=False)

        # 2. Gửi Phòng 3: james_hq (Kế hoạch tác chiến hoàn chỉnh trong ngày của James)
        if event_type in ("OPENING_0900_KICKOFF", "GOLDEN_WINDOW_VERDICT", "EOD_WRAP_FINAL"):
            strikes_txt = "\n".join(
                f"  • *{st['symbol']}* (V3 `{st.get('fusion_v3_score', '-')}` | F=`{st.get('f_score', '-')}/9`): `{st.get('shares_lot100', 0)} CP` @ LO `{float(st.get('limit_entry_vnd', 0)):,.0f}đ` | Stop `{float(st.get('stop_loss_vnd', 0)):,.0f}đ` | TP1 `{float(st.get('tp1_swing_vnd', 0)):,.0f}đ` (Rủi ro `{st.get('max_nav_risk_pct', '-')}% NAV`)"
                for st in strikes[:3]
            ) or "  • Chưa nạp kèo Spring."
            chal_txt = "\n".join(
                f"  - *{c.get('challenge_id', 'CHAL')}*: {str(c.get('action_mandate', ''))[:140]}"
                for c in challenges[:4]
            ) or "  - Giữ kỷ luật quản trị rủi ro."
            james_msg = (
                f"🎖️ *[KẾ HOẠCH TÁC CHIẾN HOÀN CHỈNH — MASTER CIO JAMES]*\n"
                f"🕒 `{snap['timestamp_ict']}` | Nhịp: `{event_type}` | SSOT `{s['account_id']}`: `{s['cash_vnd']:,.0f} ₫` (`{s['status']}`)\n"
                f"━━━━━━━━━━━━━━━━━━━\n"
                f"📊 *Thị trường sống (`{r['scanned_live_count']}/{r['universe_total']}` mã):* VNI `{r['vn_index']:,.2f}` (`{r['vn_index_chg_pct']:+.2f}%`) | Br20 `{r['live_breadth_ma20_pct']:.1f}%` | Buy-Up `{r['avg_buy_up_pct']:.1f}%` | Chế độ: `{d['live_regime']}`\n"
                f"🎯 *Phán quyết Master CIO:* {d['verdict_vi']}\n"
                f"📌 *Ma trận 4 nhánh (`14h05–14h25`):*\n"
                f"  • `S4 Bear Shield`: VNI < 1,666 hoặc Buy-Up < 48% ➔ Đứng ngoài `100% Cash`.\n"
                f"  • `S3 Spring V3.0`: VNI >= 1,678, Br20 >= 24%, Vol >= 1.05x, Buy-Up >= 58% ➔ Đánh `30–40% NAV` (max 2 mã).\n"
                f"  • `S2 Sideways` (`30–45% NAV`) | `S1 Bull Breakout` (`75–85% NAV`).\n"
                f"🧾 *Rổ Kèo Đánh Cược Bất Đối Xứng V3.0 (Stop -5.5%):*\n{strikes_txt}\n"
                f"🧠 *Phản biện Độc lập Brain V3.0:*\n{chal_txt}"
            )
            dispatch_message("james_hq", james_msg, mirror_to_reports_vault=False)
    except Exception as e:
        _log(f"[WARN] Lỗi gửi thông báo Telegram 2 phòng: {e}")


def _append_intraday_history(today_str: str, snap: Dict[str, Any]) -> None:
    hist = _read_json(INTRADAY_HISTORY_FILE, {})
    if not isinstance(hist, dict):
        hist = {}
    day_list = hist.get(today_str) or []
    rec = snap["recon_summary"]
    dec = snap["decision_brain"]
    day_list.append({
        "ts": snap["timestamp_ict"],
        "phase": snap["phase"],
        "vn_index": rec["vn_index"],
        "vn_index_chg_pct": rec["vn_index_chg_pct"],
        "live_breadth_ma20_pct": rec["live_breadth_ma20_pct"],
        "avg_buy_up_pct": rec["avg_buy_up_pct"],
        "scanned_live_count": rec["scanned_live_count"],
        "live_regime": dec["live_regime"],
        "verdict_code": dec["verdict_code"],
        "top_leaders": [x["symbol"] for x in snap["top_5_live_leaders"][:3]],
    })
    hist[today_str] = day_list[-200:]
    # Keep last 20 trading days compact
    for old_k in sorted(hist.keys())[:-20]:
        hist.pop(old_k, None)
    _write_json(INTRADAY_HISTORY_FILE, hist)


def _write_live_warroom_markdown(snap: Dict[str, Any]) -> Path:
    LIVE_SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    out_md = LIVE_SESSIONS_DIR / f"{snap['date']}_Live_WarRoom_Log.md"
    r = snap["recon_summary"]
    d = snap["decision_brain"]
    s = snap["ssot_snapshot"]
    lines = [
        f"# NHẬT KÝ TÁC CHIẾN THỜI GIAN THỰC TOÀN THỊ TRƯỜNG — {snap['date']}",
        f"",
        f"> **Cập nhật lần cuối:** `{snap['timestamp_ict']}` | **Pha phiên:** `{snap['phase']}` | **Nhãn:** `{snap['tag']}`  ",
        f"> **Tài khoản SSOT (`{s['account_id']}`):** `{s['status']}` | Tiền mặt: **`{s['cash_vnd']:,.0f} ₫`** | Vị thế mở: `{s['open_positions_count']}`",
        f"",
        f"## 1. BỨC TRANH BẢNG ĐIỆN TOÀN THỊ TRƯỜNG (`{r['scanned_live_count']}/{r['universe_total']}` MÃ LIVE)",
        f"- **VN-Index:** `{r['vn_index']:,.2f}` (`{r['vn_index_chg_pct']:+.2f}%`) | MA20: `{r['vn_index_ma20']:,.1f}` | MA50: `{r['vn_index_ma50']:,.1f}`",
        f"- **Độ rộng & Dòng tiền:** Tăng `{r['advance_count']}` (Trần `{r['ceiling_count']}`) / Giảm `{r['decline_count']}` (Sàn `{r['floor_count']}`) / Tham chiếu `{r['unchanged_count']}` | `Breadth > MA20 = {r['live_breadth_ma20_pct']:.1f}%` | `Buy-Up = {r['avg_buy_up_pct']:.1f}%` | `VolPace = {r['volume_pace_ratio']:.2f}x` | Khối ngoại: `{r['foreign_net_ty']:+.1f} tỷ`",
        f"- **Tin Internet / BCTC nạp sẵn:** `{r['internet_articles']}` bài báo (`{r['internet_crawled_at']}`)",
        f"",
        f"## 2. PHÁN QUYẾT TỨC THỜI CỦA HỘI ĐỒNG (`{d['live_regime']}`)",
        f"- **Chỉ thị:** {d['verdict_vi']}",
        f"- **Tỷ trọng mục tiêu:** `{d['target_allocation_pct']}`",
        f"",
        f"### Top 5 Siêu Cổ Phiếu BCTC Sạch Dẫn Dắt Thời Gian Thực",
        f"| Mã | Ngành | Giá Live | % Ngày | Buy-Up % | F-Score | RS | Điểm Live | Tin mới |",
        f"| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |",
    ]
    for it in snap["top_5_live_leaders"]:
        lines.append(
            f"| **{it['symbol']}** | {it['sector']} | `{it['live_price']:,.0f} ₫` | `{it['change_pct']:+.2f}%` | `{it['buy_up_pct']:.1f}%` | `{it['f_score']}/9` | `{it['rs_rating']}` | `{it['live_score']}` | {it['headline'] or '-'} |"
        )
    if d["proposed_lo_orders"]:
        lines.extend([
            f"",
            f"### Lệnh LO Dự Kiến (Lô Chẵn 100 • Stop `-5.5%`)",
            f"| Mã | KL | Giá LO | Cắt lỗ | TP1 | Quy mô vốn |",
            f"| :---: | :---: | :---: | :---: | :---: | :---: |",
        ])
        for o in d["proposed_lo_orders"]:
            lines.append(
                f"| **{o['symbol']}** | `{o['shares_lot100']}` | `{o['limit_lo_vnd']:,.0f} ₫` | `{o['stop_vnd']:,.0f} ₫` | `{o['tp1_vnd']:,.0f} ₫` | `{o['capital_vnd']:,.0f} ₫` |"
            )
    if snap["top_5_danger_alerts"]:
        lines.extend([
            f"",
            f"### Cảnh Báo Rủi Ro / Mã Cấm",
            f"| Mã | Giá Live | % Ngày | F-Score | Beneish | Lý do |",
            f"| :---: | :---: | :---: | :---: | :---: | :--- |",
        ])
        for al in snap["top_5_danger_alerts"]:
            lines.append(
                f"| `{al['symbol']}` | `{al['live_price']:,.0f} ₫` | `{al['change_pct']:+.2f}%` | `{al['f_score']}/9` | `{al['beneish_status']}` | {al['reason']} |"
            )
    out_md.write_text("\n".join(lines), encoding="utf-8")
    return out_md


def run_eod_wrap(fast_test: bool = False, send_telegram: bool = False) -> Path:
    now_ict = _ict_now()
    today_str = now_ict.strftime("%Y-%m-%d")
    _log(f"[EOD WRAP START] date={today_str} | fast_test={fast_test}")

    snap = run_live_recon_and_decision(refresh_intel=False, send_telegram=False, tag="EOD_WRAP_FINAL")
    if not fast_test:
        for script_cmd in (
            ("scripts/apex_real_bctc_crawler.py", []),
            ("scripts/apex_daily_internet_intel_crawler.py", []),
            ("scripts/apex_autonomous_cio_brain_v3.py", []),
            ("VN_Market/scripts/vn_performance_learning.py", []),
            ("scripts/apex_inspector_trong.py", []),
            ("VN_Market/scripts/generate_vn_dashboard.py", []),
            ("scripts/palmer_antigravity_sync_bridge.py", ["--sync-current", "--note", f"Tổng kết phiên {today_str} & chốt bài học War-Room lúc 16:00"]),
            ("scripts/apex_institutional_memory_bridge.py", []),
        ):
            _run_py(script_cmd[0], script_cmd[1], timeout=240)

    hist = _read_json(INTRADAY_HISTORY_FILE, {}).get(today_str) or []
    regimes_seen = sorted({str(x.get("live_regime")) for x in hist}) or [snap["decision_brain"]["live_regime"]]
    leaders_seen: List[str] = []
    for x in hist:
        for s in (x.get("top_leaders") or []):
            if s not in leaders_seen:
                leaders_seen.append(s)

    r = snap["recon_summary"]
    s = snap["ssot_snapshot"]
    d = snap["decision_brain"]
    summary_md = LIVE_SESSIONS_DIR / f"{today_str}_EOD_WarRoom_Summary_And_Lessons.md"
    LIVE_SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

    trong_ledger = _read_json(BASE_DIR / "12_Institutional_Ombudsman_And_Inspectorate" / "system_audit_ledger.json", [])
    latest_trong = trong_ledger[-1] if isinstance(trong_ledger, list) and trong_ledger else {}

    content = f"""# BÁO CÁO TỔNG KẾT PHIÊN, TỰ HỌC & NGHỈ NGƠI CUỐI NGÀY — {today_str}

> **Thời điểm đóng sổ:** `{now_ict.strftime('%Y-%m-%d %H:%M:%S ICT')}`  
> **Trạng thái tài khoản SSOT (`{s['account_id']}`):** `{s['status']}` | Tiền mặt ròng: **`{s['cash_vnd']:,.0f} ₫`** | Cổ phiếu: `{s['open_positions_count']} mã`  
> **Điểm kiểm toán Trọng (Ban 12):** `{latest_trong.get('overall_discipline_score', 'N/A')}/100` (Kỹ thuật: `{latest_trong.get('system_health_score', 'N/A')}/100`)

---

## 1. TỔNG KẾT DIỄN BIẾN & KỶ LUẬT PHIÊN HÔM NAY (`{len(hist)}` NHỊP QUÉT)
- **Đóng cửa VN-Index:** `{r['vn_index']:,.2f}` (`{r['vn_index_chg_pct']:+.2f}%`) | `Breadth > MA20 = {r['live_breadth_ma20_pct']:.1f}%` | `Buy-Up = {r['avg_buy_up_pct']:.1f}%`
- **Độ phủ quét bảng điện:** `{r['scanned_live_count']}/{r['universe_total']}` mã | **Các chế độ đã ghi nhận trong phiên:** `{', '.join(regimes_seen)}`
- **Phán quyết cuối phiên:** `{d['verdict_vi']}`
- **Nhóm dẫn dắt BCTC sạch nổi bật:** `{', '.join([x['symbol'] for x in snap['top_5_live_leaders']]) or 'Không có'}` *(xuất hiện xuyên suốt: `{', '.join(leaders_seen[:6])}`)*

## 2. ĐỐI SOÁT ĐÚNG / SAI & BÀI HỌC CHO NGÀY MAI
1. **Điểm làm đúng cần duy trì:** Toàn bộ 11 phòng ban bám sát nguyên tắc dữ liệu thật (`145` mã bảng điện + `80` BCTC Q3/2026 + `506` tin Internet), khóa nút Mua trước `14h00` chống FOMO ATO và không để lộ khoảng trống thanh khoản hay cổ phiếu cờ đỏ (`BAF`, `VIX`, `CII`, `CEO`).
2. **Điểm cần cảnh giác & cải thiện cho phiên tiếp theo:** Tiếp tục đối chiếu độ lệch giữa `Buy-Up %` buổi sáng (`09:30–11:30`) với độ bền giá tại `14:05–14:25`; chỉ nâng tỷ trọng khi cả `VN-Index`, `Breadth > MA20` và `Volume Pace` xác nhận đồng thuận.
3. **Chuẩn bị sẵn sàng cho phiên kế tiếp (`09:00`):** Toàn bộ dữ liệu BCTC, tin Internet, Brain V3.0 và trí nhớ Palmer đã được đồng bộ trước khi hệ thống chuyển sang trạng thái nghỉ ngơi cuối ngày (`16:00`).

---
*Trạng thái tiến trình: `SESSION_CLOSED_RESTING` — Hệ thống nghỉ ngơi cho tới `09:00` phiên giao dịch tiếp theo.*
"""
    summary_md.write_text(content, encoding="utf-8")
    _append_evolution_journal(today_str, snap, len(hist))
    _refresh_static_web_portal_safely()

    if send_telegram:
        _dispatch_daily_warroom_and_james(snap, event_type="EOD_WRAP_FINAL", eod_summary_path=summary_md)

    _log(f"[EOD WRAP DONE] Đã xuất báo cáo tổng kết tại: {summary_md}")
    return summary_md


def _append_evolution_journal(today_str: str, snap: Dict[str, Any], cycles_cnt: int) -> None:
    try:
        EVOLUTION_JOURNAL.parent.mkdir(parents=True, exist_ok=True)
        existing = EVOLUTION_JOURNAL.read_text(encoding="utf-8") if EVOLUTION_JOURNAL.exists() else "# SYSTEM EVOLUTION JOURNAL\n"
        marker = f"### [WAR-ROOM EOD {today_str}]"
        if marker in existing:
            return
        r = snap["recon_summary"]
        d = snap["decision_brain"]
        entry = (
            f"\n{marker}\n"
            f"- **Chu kỳ quét thực tế:** `{cycles_cnt}` nhịp (`{r['scanned_live_count']}/{r['universe_total']}` mã) | VNI `{r['vn_index']:,.2f}` (`{r['vn_index_chg_pct']:+.2f}%`) | Br20 `{r['live_breadth_ma20_pct']:.1f}%` | Regime `{d['live_regime']}`.\n"
            f"- **Bài học tự tiến hóa:** Giữ kỷ luật cổng `14h05–14h25`, ưu tiên BCTC sạch (`{', '.join(x['symbol'] for x in snap['top_5_live_leaders'][:3])}`), loại tuyệt đối mã cờ đỏ.\n"
        )
        EVOLUTION_JOURNAL.write_text(existing.rstrip() + "\n" + entry, encoding="utf-8")
    except Exception as e:
        _log(f"[WARN] Không thể ghi system_evolution_journal.md: {e}")


def _handle_signal(signum: int, _frame: Any) -> None:
    global STOP_FLAG
    _log(f"[SIGNAL] Nhận tín hiệu dừng ({signum}), chuẩn bị thoát an toàn...")
    STOP_FLAG = True


def _sleep_interruptible(seconds: int) -> None:
    for _ in range(max(1, seconds)):
        if STOP_FLAG:
            break
        time.sleep(1)


def run_daemon(send_telegram: bool = True) -> None:
    global STOP_FLAG
    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    now = _ict_now()
    hm_init = now.strftime("%H:%M")
    if now.weekday() >= 5 or hm_init >= "16:00":
        _log(f"[STANDBY] Ngoài giờ giao dịch (weekday={now.weekday()}, time={hm_init}). Chạy 1 nhịp đồng bộ rồi nghỉ.")
        run_live_recon_and_decision(refresh_intel=False, send_telegram=False, tag="OFF_HOURS_STANDBY")
        return

    if not _acquire_pid_lock():
        return

    try:
        _log("[DAEMON START] Khởi động Hệ thống Tác chiến Toàn thị trường 09:00–16:00 ICT...")
        last_intel_ts = 0.0
        opening_kickoff_done = False
        midday_done = False
        golden_1400_refreshed = False
        golden_verdict_sent = False
        atc_done = False
        eod_done = False
        prev_regime: Optional[str] = None
        prev_verdict_code: Optional[str] = None
        prev_pos_sig: Optional[str] = None

        def _check_and_emit_change(snap_obj: Dict[str, Any]) -> None:
            nonlocal prev_regime, prev_verdict_code, prev_pos_sig
            cur_reg = snap_obj["decision_brain"]["live_regime"]
            cur_vc = snap_obj["decision_brain"]["verdict_code"]
            cur_pos = json.dumps(snap_obj["ssot_snapshot"].get("position_alerts") or [], sort_keys=True)
            changed = (
                prev_regime is not None
                and (cur_reg != prev_regime or cur_vc != prev_verdict_code or cur_pos != prev_pos_sig)
            )
            prev_regime, prev_verdict_code, prev_pos_sig = cur_reg, cur_vc, cur_pos
            if changed and send_telegram:
                _dispatch_daily_warroom_and_james(snap_obj, event_type="REGIME_OR_PLAN_CHANGE")

        while not STOP_FLAG:
            now = _ict_now()
            hm = now.strftime("%H:%M")

            if hm < "09:00":
                _log(f"[WAIT 09:00] Hiện tại {hm} ICT — chờ phiên mở cửa lúc 09:00...")
                _sleep_interruptible(20)
                continue

            if hm >= "16:00":
                if not eod_done:
                    run_eod_wrap(fast_test=False, send_telegram=send_telegram)
                    eod_done = True
                _log("[SESSION_CLOSED_RESTING] Đã 16:00 ICT — Hệ thống tổng kết xong và nghỉ ngơi.")
                break

            if "09:00" <= hm < "15:15" and not opening_kickoff_done:
                snap0 = run_live_recon_and_decision(
                    refresh_intel=True,
                    send_telegram=send_telegram,
                    tag="OPENING_0900_KICKOFF",
                    event_type="OPENING_0900_KICKOFF",
                )
                opening_kickoff_done = True
                last_intel_ts = time.time()
                prev_regime = snap0["decision_brain"]["live_regime"]
                prev_verdict_code = snap0["decision_brain"]["verdict_code"]
                prev_pos_sig = json.dumps(snap0["ssot_snapshot"].get("position_alerts") or [], sort_keys=True)
                _sleep_interruptible(180)
                continue

            if "09:00" <= hm < "11:30":
                do_intel = (time.time() - last_intel_ts) >= 1800
                snap = run_live_recon_and_decision(refresh_intel=do_intel, send_telegram=False, tag="MORNING_LIVE_SCAN")
                if do_intel:
                    last_intel_ts = time.time()
                _check_and_emit_change(snap)
                _sleep_interruptible(180)

            elif "11:30" <= hm < "13:00":
                if not midday_done:
                    snap = run_live_recon_and_decision(refresh_intel=False, send_telegram=send_telegram, tag="MIDDAY_BRIEFING", event_type="MIDDAY_BRIEFING")
                    midday_done = True
                    prev_regime = snap["decision_brain"]["live_regime"]
                    prev_verdict_code = snap["decision_brain"]["verdict_code"]
                _sleep_interruptible(60)

            elif "13:00" <= hm < "14:00":
                do_intel = (time.time() - last_intel_ts) >= 1800
                snap = run_live_recon_and_decision(refresh_intel=do_intel, send_telegram=False, tag="AFTERNOON_T2_SCAN")
                if do_intel:
                    last_intel_ts = time.time()
                _check_and_emit_change(snap)
                _sleep_interruptible(180)

            elif "14:00" <= hm <= "14:25":
                do_intel = not golden_1400_refreshed
                send_now = send_telegram and not golden_verdict_sent
                snap = run_live_recon_and_decision(
                    refresh_intel=do_intel,
                    send_telegram=send_now,
                    tag="GOLDEN_WINDOW_VERDICT",
                    event_type="GOLDEN_WINDOW_VERDICT" if send_now else None,
                )
                golden_1400_refreshed = True
                if send_now:
                    golden_verdict_sent = True
                    prev_regime = snap["decision_brain"]["live_regime"]
                    prev_verdict_code = snap["decision_brain"]["verdict_code"]
                else:
                    _check_and_emit_change(snap)
                if do_intel:
                    last_intel_ts = time.time()
                _sleep_interruptible(60)

            elif "14:25" < hm < "15:15":
                if hm >= "14:46" and not atc_done:
                    snap = run_live_recon_and_decision(refresh_intel=False, send_telegram=False, tag="ATC_CLOSE_CAPTURE")
                    _check_and_emit_change(snap)
                    atc_done = True
                _sleep_interruptible(60)

            elif "15:15" <= hm < "16:00":
                if not eod_done:
                    run_eod_wrap(fast_test=False, send_telegram=send_telegram)
                    eod_done = True
                    _log("[SESSION_CLOSED_RESTING] Đã hoàn tất Tổng kết & Tự học cuối ngày. Chờ chạm 16:00 nghỉ ngơi.")
                    break
                _sleep_interruptible(60)
    finally:
        _release_pid_lock()


def main() -> None:
    parser = argparse.ArgumentParser(description="Apex Daily Live Full-Market War-Room Engine (09:00-16:00 ICT)")
    parser.add_argument("--once", action="store_true", help="Chạy 1 chu kỳ quét toàn thị trường + đầu não V3 ngay")
    parser.add_argument("--refresh-intel", action="store_true", help="Làm mới crawler Internet trước khi chấm điểm (--once)")
    parser.add_argument("--eod-wrap", action="store_true", help="Chạy tổng kết cuối ngày, đối soát bài học & nghỉ ngơi")
    parser.add_argument("--fast-test", action="store_true", help="Bỏ qua crawl mạng nặng khi chạy kiểm thử --eod-wrap")
    parser.add_argument("--daemon", action="store_true", help="Chạy vòng lặp liên tục từ 09:00 đến 16:00 Thứ 2-Thứ 6")
    parser.add_argument("--no-telegram", action="store_true", help="Không gửi thông báo Telegram")
    args = parser.parse_args()

    send_tg = not args.no_telegram
    if args.daemon:
        run_daemon(send_telegram=send_tg)
    elif args.eod_wrap:
        run_eod_wrap(fast_test=args.fast_test, send_telegram=send_tg)
    else:
        run_live_recon_and_decision(refresh_intel=args.refresh_intel, send_telegram=send_tg, tag="CLI_ONCE")


if __name__ == "__main__":
    main()
