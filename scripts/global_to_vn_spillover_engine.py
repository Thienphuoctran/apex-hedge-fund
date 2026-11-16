#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APEX GLOBAL-TO-VN OVERNIGHT SPILLOVER ENGINE (PHASE 2.1)
File: scripts/global_to_vn_spillover_engine.py
Cơ quan chủ quản: Alex (Ban 7 US) -> Chuyển giao trước 08h30 cho Minh Quân (Ban 7 VN)

Nhiệm vụ:
1. Thu thập chỉ số kết phiên Mỹ & Vĩ mô toàn cầu mới nhất:
   - S&P 500 (^GSPC), Nasdaq (^IXIC), VIX (^VIX), US 10Y Yield (^TNX)
   - Chỉ số Đô la Mỹ DXY (DX-Y.NYB), Dầu WTI (CL=F), VanEck Vietnam ETF (VNM), EM ETF (EEM)
2. Tính hệ số điều chỉnh rủi ro liên thị trường (`risk_multiplier`: 0.35x - 1.15x)
   và trần phân bổ giải ngân (`max_allocation_pct`: 15% - 75%) cho Minh Quân trước ATO.
3. Cache 15 phút tại `data/global_spillover_state.json` + Fallback an toàn từ
   `data/latest_market_snapshot.json` nếu mạng Yahoo Finance gián đoạn.
"""

import sys
import os
import json
import time
import datetime
import threading
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
SPILLOVER_FILE = DATA_DIR / "global_spillover_state.json"
MARKET_SNAPSHOT_FILE = DATA_DIR / "latest_market_snapshot.json"

sys.path.insert(0, str(BASE_DIR))

_SPILL_LOCK = threading.Lock()
SPILLOVER_TICKERS = ["^GSPC", "^IXIC", "^VIX", "^TNX", "DX-Y.NYB", "CL=F", "VNM", "EEM"]


def _get_ict_now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc).astimezone(
        datetime.timezone(datetime.timedelta(hours=7))
    )


def _fetch_yahoo_chart_lightweight(tickers: List[str]) -> Dict[str, Dict[str, float]]:
    """Thu thập giá qua Yahoo Chart JSON nhẹ (0 MB pandas/numpy — an toàn cho Render 512MB RAM)."""
    import urllib.request
    import urllib.parse

    out: Dict[str, Dict[str, float]] = {}
    headers = {"User-Agent": "Mozilla/5.0 (compatible; ApexSpillover/1.0)"}
    for sym in tickers:
        try:
            q_sym = urllib.parse.quote(sym, safe="")
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{q_sym}?range=5d&interval=1d"
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            res_list = (data.get("chart") or {}).get("result") or []
            if not res_list:
                continue
            meta = res_list[0].get("meta") or {}
            closes_raw = ((res_list[0].get("indicators") or {}).get("quote") or [{}])[0].get("close") or []
            closes = [float(c) for c in closes_raw if c is not None]
            last_p = float(meta.get("regularMarketPrice") or (closes[-1] if closes else 0.0))
            if last_p <= 0:
                continue
            prev_p = float(meta.get("chartPreviousClose") or meta.get("previousClose") or (closes[-2] if len(closes) >= 2 else last_p))
            chg_1d = ((last_p - prev_p) / prev_p) * 100.0 if prev_p > 0 else 0.0
            out[sym] = {
                "last_price": round(last_p, 2),
                "prev_close": round(prev_p, 2),
                "change_1d_pct": round(chg_1d, 2),
                "source": "YAHOO_HTTP_LIGHT",
            }
        except Exception:
            continue
    return out


def _fetch_from_yfinance(tickers: List[str]) -> Dict[str, Dict[str, float]]:
    out = _fetch_yahoo_chart_lightweight(tickers)
    if len(out) >= 4:
        return out
    if os.environ.get("APEX_CLOUD_COMPACT_MODE", "").strip().lower() in ("1", "true", "yes"):
        return out
    try:
        import yfinance as yf
        df = yf.download(
            tickers=tickers,
            period="7d",
            interval="1d",
            group_by="ticker",
            auto_adjust=False,
            progress=False,
            threads=True,
            timeout=8,
        )
        if df is None or df.empty:
            return out

        multi = hasattr(df.columns, "levels")
        for sym in tickers:
            try:
                sub = df[sym] if multi and sym in df.columns.levels[0] else (df if len(tickers) == 1 else None)
                if sub is None or "Close" not in sub:
                    continue
                closes = sub["Close"].dropna()
                if len(closes) < 1:
                    continue
                last_p = float(closes.iloc[-1])
                prev_p = float(closes.iloc[-2]) if len(closes) >= 2 else last_p
                chg_1d = ((last_p - prev_p) / prev_p) * 100.0 if prev_p > 0 else 0.0
                out[sym] = {
                    "last_price": round(last_p, 2),
                    "prev_close": round(prev_p, 2),
                    "change_1d_pct": round(chg_1d, 2),
                    "source": "YFINANCE_LIVE",
                }
            except Exception:
                continue
    except Exception as e:
        print(f"[!] Global Spillover yfinance warning: {e}")
    return out


def _load_snapshot_fallback() -> Dict[str, Dict[str, float]]:
    out: Dict[str, Dict[str, float]] = {}
    if not MARKET_SNAPSHOT_FILE.exists():
        return out
    try:
        snap = json.loads(MARKET_SNAPSHOT_FILE.read_text(encoding="utf-8"))
        for bucket in ("global_indices", "macro_gauges"):
            for item in snap.get(bucket, []):
                sym = item.get("symbol")
                if sym in SPILLOVER_TICKERS and item.get("last_price") is not None:
                    out[sym] = {
                        "last_price": round(float(item.get("last_price", 0.0)), 2),
                        "prev_close": round(float(item.get("last_price", 0.0)), 2),
                        "change_1d_pct": round(float(item.get("change_1d_pct", 0.0)), 2),
                        "source": "SNAPSHOT_FALLBACK",
                    }
    except Exception:
        pass
    return out


def compute_global_to_vn_spillover(force_refresh: bool = False, cache_ttl: int = 900) -> Dict[str, Any]:
    now_ict = _get_ict_now()
    now_ts = time.time()

    with _SPILL_LOCK:
        if not force_refresh and SPILLOVER_FILE.exists():
            try:
                cached = json.loads(SPILLOVER_FILE.read_text(encoding="utf-8"))
                if now_ts - float(cached.get("fetched_epoch", 0)) < cache_ttl and cached.get("metrics"):
                    return cached
            except Exception:
                pass

    metrics = _fetch_from_yfinance(SPILLOVER_TICKERS)
    fallback_metrics = _load_snapshot_fallback()
    for sym, fb in fallback_metrics.items():
        if sym not in metrics:
            metrics[sym] = fb

    sp500 = metrics.get("^GSPC", {"last_price": 0.0, "change_1d_pct": 0.0, "source": "NONE"})
    nasdaq = metrics.get("^IXIC", {"last_price": 0.0, "change_1d_pct": 0.0, "source": "NONE"})
    vix = metrics.get("^VIX", {"last_price": 18.0, "change_1d_pct": 0.0, "source": "NONE"})
    us10y = metrics.get("^TNX", {"last_price": 4.3, "change_1d_pct": 0.0, "source": "NONE"})
    dxy = metrics.get("DX-Y.NYB", {"last_price": 103.0, "change_1d_pct": 0.0, "source": "NONE"})
    oil = metrics.get("CL=F", {"last_price": 75.0, "change_1d_pct": 0.0, "source": "NONE"})
    vnm = metrics.get("VNM", {"last_price": 0.0, "change_1d_pct": 0.0, "source": "NONE"})
    eem = metrics.get("EEM", {"last_price": 0.0, "change_1d_pct": 0.0, "source": "NONE"})

    risk_mult = 1.0
    drivers: List[str] = []
    sector_tilts: List[str] = []

    # 1. US Equities & VNM ETF Sentiment
    sp_chg = float(sp500.get("change_1d_pct", 0.0))
    nq_chg = float(nasdaq.get("change_1d_pct", 0.0))
    vnm_chg = float(vnm.get("change_1d_pct", 0.0))
    us_avg_chg = (sp_chg + nq_chg) / 2.0

    if us_avg_chg <= -2.0 or vnm_chg <= -2.0:
        risk_mult -= 0.30
        drivers.append(f"Bán tháo Phố Wall / VNM ETF (S&P {sp_chg:+.2f}%, VNM {vnm_chg:+.2f}%) -> Thu hẹp quy mô giải ngân")
    elif us_avg_chg <= -0.9:
        risk_mult -= 0.15
        drivers.append(f"Phiên Mỹ đỏ nhẹ (S&P {sp_chg:+.2f}%, Nasdaq {nq_chg:+.2f}%) -> Tránh mua đuổi đầu sáng")
    elif us_avg_chg >= 0.8 or vnm_chg >= 1.0:
        risk_mult += 0.08
        drivers.append(f"Phiên Mỹ & VNM ETF tích cực (S&P {sp_chg:+.2f}%, VNM {vnm_chg:+.2f}%) -> Hỗ trợ tâm lý đầu phiên VN")
    else:
        drivers.append(f"Phố Wall đi ngang phân hóa (S&P {sp_chg:+.2f}%, Nasdaq {nq_chg:+.2f}%)")

    # 2. VIX Fear Gauge
    vix_val = float(vix.get("last_price", 18.0))
    if vix_val >= 28.0:
        risk_mult -= 0.25
        drivers.append(f"VIX báo động cao ({vix_val:.1f}) -> Tăng phòng thủ tiền mặt")
    elif vix_val >= 22.0:
        risk_mult -= 0.12
        drivers.append(f"VIX nhích cao ({vix_val:.1f}) -> Hạn chế Margin & ưu tiên Stop chặt")
    elif 0 < vix_val < 16.0:
        risk_mult += 0.05
        drivers.append(f"VIX thấp ổn định ({vix_val:.1f})")

    # 3. DXY & US10Y Yield (Áp lực tỷ giá USD/VND & SBV)
    dxy_val = float(dxy.get("last_price", 103.0))
    dxy_chg = float(dxy.get("change_1d_pct", 0.0))
    tnx_val = float(us10y.get("last_price", 4.3))
    tnx_chg = float(us10y.get("change_1d_pct", 0.0))

    if dxy_val >= 105.0 or dxy_chg >= 0.65:
        risk_mult -= 0.12
        drivers.append(f"DXY tăng nóng ({dxy_val:.2f}, {dxy_chg:+.2f}%) -> Cảnh giác áp lực tỷ giá USD/VND & hút ròng OMO")
        sector_tilts.append("Hưởng lợi xuất khẩu USD (MSH, Thủy sản) / Thận trọng BĐS đòn bẩy cao")
    elif dxy_val > 0 and dxy_val <= 101.5:
        risk_mult += 0.05
        drivers.append(f"DXY hạ nhiệt ({dxy_val:.2f}) -> Giảm áp lực tỷ giá cho khối Ngân hàng & Ngoại")

    if tnx_val >= 4.75 and tnx_chg > 1.0:
        risk_mult -= 0.08
        drivers.append(f"Lợi suất US10Y neo cao ({tnx_val:.2f}%, {tnx_chg:+.2f}%)")

    # 4. Oil WTI (CL=F) Spillover cho Nhóm Dầu khí
    oil_val = float(oil.get("last_price", 0.0))
    oil_chg = float(oil.get("change_1d_pct", 0.0))
    if oil_chg >= 2.2:
        sector_tilts.append(f"Dầu WTI bật mạnh ({oil_val:.2f}$, {oil_chg:+.2f}%) -> Hỗ trợ nhóm Dầu khí (BSR, PVD, GAS)")
    elif oil_chg <= -2.5:
        sector_tilts.append(f"Dầu WTI giảm sâu ({oil_val:.2f}$, {oil_chg:+.2f}%) -> Áp lực ngắn hạn họ Dầu khí")

    risk_mult = round(max(0.35, min(1.15, risk_mult)), 2)
    base_cap_pct = 50
    max_alloc_pct = int(max(15, min(75, round(base_cap_pct * risk_mult))))

    if risk_mult >= 1.05:
        bias = "TAILWIND_RISK_ON"
        bias_label = "🟢 THUẬN CHIỀU TÍCH CỰC (US -> VN TAILWIND)"
        badge_color = "#10b981"
    elif risk_mult >= 0.85:
        bias = "NEUTRAL_SELECTIVE"
        bias_label = "⚖️ TRUNG TÍNH PHÂN HÓA (CHỌN LỌC CỔ PHIẾU)"
        badge_color = "#38bdf8"
    elif risk_mult >= 0.65:
        bias = "CAUTIOUS_HEADWIND"
        bias_label = "🟡 THẬN TRỌNG GIÓ NGƯỢC TỪ PHỐ WALL"
        badge_color = "#fbbf24"
    else:
        bias = "DEFENSIVE_SHOCK"
        bias_label = "🔴 BÁO ĐỘNG LIÊN THỊ TRƯỜNG — THU HẸP TỶ TRỌNG"
        badge_color = "#ef4444"

    result = {
        "snapshot_date": now_ict.strftime("%Y-%m-%d"),
        "updated_at": now_ict.strftime("%Y-%m-%d %H:%M:%S"),
        "fetched_epoch": round(now_ts, 2),
        "risk_multiplier": risk_mult,
        "max_allocation_pct": max_alloc_pct,
        "overnight_bias": bias,
        "bias_label": bias_label,
        "badge_color": badge_color,
        "drivers": drivers,
        "sector_tilts": sector_tilts or ["Ưu tiên cổ phiếu có OCF > LNST, Buy-Up chủ động > 60% và nền giá chặt"],
        "metrics": {
            "SP500": sp500,
            "NASDAQ": nasdaq,
            "VIX": vix,
            "US10Y": us10y,
            "DXY": dxy,
            "WTI_OIL": oil,
            "VNM_ETF": vnm,
            "EEM_ETF": eem,
        },
        "handoff_directive": (
            f"Alex (Ban 7 US) bàn giao trước 08h30 cho Minh Quân (Ban 7 VN): "
            f"Hệ số rủi ro liên thị trường {risk_mult:.2f}x | Trần giải ngân tối đa {max_alloc_pct}% NAV. "
            + (drivers[0] if drivers else "")
        ),
    }

    with _SPILL_LOCK:
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            SPILLOVER_FILE.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:
            print(f"[!] Lỗi lưu global_spillover_state.json: {e}")

    try:
        from scripts.apex_cloud_db_sync import ApexCloudDBSync
        ApexCloudDBSync.sync_spillover(result)
    except Exception:
        pass

    return result


if __name__ == "__main__":
    res = compute_global_to_vn_spillover(force_refresh=True)
    print(f"Bias: {res['bias_label']} | Multiplier: {res['risk_multiplier']}x | Max Alloc: {res['max_allocation_pct']}%")
    print(f"Handoff: {res['handoff_directive']}")
    for k, m in res["metrics"].items():
        print(f"  {k:<8}: {m.get('last_price')} ({m.get('change_1d_pct'):+.2f}%) [{m.get('source')}]")
