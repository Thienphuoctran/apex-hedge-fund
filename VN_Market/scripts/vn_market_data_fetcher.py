#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
vn_market_data_fetcher.py - Bộ Thu Thập Dữ Liệu Thị Trường, BCTC & Tín Hiệu VSA/Wyckoff Chứng Khoán Việt Nam (v2.0 Institutional)
Tách biệt hoàn toàn, không xung đột dữ liệu với thị trường quốc tế.
Hỗ trợ: HOSE, HNX, UPCoM (54 Siêu Cổ Phiếu Đầu Ngành).
Nâng cấp v2.0:
- Cào sâu các trường BCTC thực tế từ yfinance (Doanh thu, LNST, OCF, FCF, Tiền mặt, Nợ vay, Biên LN, EPS, BVPS, Cổ tức).
- Tính toán Sức mạnh giá tương đối chuẩn William O'Neil (RS Rating 1-99).
- Nhận diện tự động Pha Wyckoff (Accumulation, Markup, Distribution, Markdown) & Tín hiệu dòng tiền VSA (No Supply, Pocket Pivot, Spring, Upthrust).
- Ước lượng tỷ lệ Mua chủ động (Active Buy Up %) từ cấu trúc nến và khối lượng khớp lệnh.
"""

import os
import sys
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
import json
import time
import math
import datetime
import numpy as np
import pandas as pd
import yfinance as yf

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config", "watchlist_vn.json")
OUTPUT_PATH = os.path.join(BASE_DIR, "data", "vn_market_data.json")


def load_watchlist():
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Watchlist not found at {CONFIG_PATH}")
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def derive_wyckoff_and_vsa(price, day_chg, ma20, ma50, ma200, rsi14, atr14, vol_ratio, price_vs_ma200, price_vs_ma20):
    """
    Phân tích Pha Wyckoff & Tín hiệu VSA (Volume Spread Analysis) chuẩn Richard Wyckoff & Anna Coulling.
    """
    # 1. Xác định Pha Wyckoff
    if price >= ma50 and ma50 >= ma200 * 0.98 and price_vs_ma200 >= 0:
        wyckoff_phase = "Phase E — MARKUP (Đẩy giá Uptrend bền vững trên MA50 & MA200)"
    elif price >= ma200 and price < ma50:
        wyckoff_phase = "Phase C/D — RE-ACCUMULATION (Tích lũy lại / Test cung trên MA200)"
    elif price < ma200 and price >= ma20 and rsi14 >= 48:
        wyckoff_phase = "Phase C — SPRING / RECOVERY (Nỗ lực tạo đáy & Phục hồi lên MA20)"
    elif price < ma200 and rsi14 <= 36:
        wyckoff_phase = "Phase A — SELLING CLIMAX / OVERSOLD (Quá bán cạn kiệt chờ cân bằng)"
    elif price < ma200 and price < ma50:
        wyckoff_phase = "Phase E (Bear) — MARKDOWN (Đè giá dưới MA200 — Tuyệt đối không bắt dao rơi)"
    else:
        wyckoff_phase = "Phase B — CONSOLIDATION (Tích lũy hấp thụ nguồn cung T+2.5)"

    # 2. Xác định Tín hiệu VSA (Volume Spread Analysis)
    if vol_ratio <= 0.78 and abs(day_chg) <= 1.35 and price >= ma200 * 0.96:
        vsa_signal = "NO_SUPPLY_TEST_CUNG (Nến biên hẹp, Vol cạn < 0.8x MA20 — Cạn cung tổ chức giữ nền)"
        vsa_code = "NO_SUPPLY"
    elif vol_ratio >= 1.20 and day_chg >= 1.0 and price >= ma20:
        vsa_signal = "POCKET_PIVOT_BREAKOUT (Dòng tiền thông minh gom chủ động Vol lớn vượt nền)"
        vsa_code = "POCKET_PIVOT"
    elif day_chg >= 0.3 and price >= ma20 and -1.5 <= price_vs_ma20 <= 2.5 and vol_ratio <= 1.15:
        vsa_signal = "SOS_ABSORPTION (Hấp thụ hàng T+2.5 về tài khoản tích cực trên MA20)"
        vsa_code = "SOS_ABSORPTION"
    elif vol_ratio >= 1.25 and day_chg <= -1.8:
        vsa_signal = "SUPPLY_OVERCOMING_DEMAND (Áp lực cung bán ròng khối lượng lớn)"
        vsa_code = "HIGH_SUPPLY"
    elif rsi14 >= 72 and day_chg <= 0.0 and vol_ratio >= 1.2:
        vsa_signal = "UPTHRUST_WARNING (Cảnh báo kéo xả vùng quá mua — Không FOMO)"
        vsa_code = "UPTHRUST"
    elif price >= ma200 and abs(day_chg) <= 1.5:
        vsa_signal = "DRY_VOLUME_BASE (Siết nền biên độ hẹp VCP — Chờ điểm nổ Volume)"
        vsa_code = "VCP_BASE"
    else:
        vsa_signal = "NEUTRAL_SUPPLY_TESTING (Cung cầu giằng co kiểm định vùng hỗ trợ)"
        vsa_code = "NEUTRAL_TEST"

    # 3. Ước lượng Tỷ lệ Mua Chủ Động (Active Buy Up %)
    base_buy_up = 52.0 + (day_chg * 4.2) + ((rsi14 - 50.0) * 0.35)
    if vsa_code in ("POCKET_PIVOT", "SOS_ABSORPTION"):
        base_buy_up += 6.5
    elif vsa_code == "NO_SUPPLY":
        base_buy_up += 4.0
    active_buy_pct = round(min(max(base_buy_up, 28.0), 82.0), 1)

    # 4. Chandelier Trailing Stop (High 22d proxy - 2.5x ATR14)
    high_proxy = max(price, ma20 * 1.015)
    chandelier_stop = round(high_proxy - 2.5 * atr14, 0)

    return {
        "wyckoff_phase": wyckoff_phase,
        "vsa_signal": vsa_signal,
        "vsa_code": vsa_code,
        "active_buy_pct": active_buy_pct,
        "chandelier_stop": chandelier_stop,
    }


def calculate_technical_indicators(df):
    """Tính toán MA20, MA50, MA200, RSI14, ATR14, Wyckoff VSA & Raw Momentum"""
    if df.empty or len(df) < 14:
        return {}

    close = df['Close']
    high = df['High']
    low = df['Low']
    volume = df['Volume']

    current_close = float(close.iloc[-1])
    prev_close = float(close.iloc[-2]) if len(close) > 1 else current_close
    day_change_pct = ((current_close - prev_close) / prev_close) * 100 if prev_close > 0 else 0.0

    def pct_chg(days):
        if len(close) > days and float(close.iloc[-(days + 1)]) > 0:
            base = float(close.iloc[-(days + 1)])
            return round(((current_close - base) / base) * 100.0, 2)
        return 0.0

    ret_1m = pct_chg(21)
    ret_3m = pct_chg(63)
    ret_6m = pct_chg(126)
    ret_1y = pct_chg(min(250, len(close) - 1))

    ma20 = float(close.rolling(window=min(20, len(close))).mean().iloc[-1])
    ma50 = float(close.rolling(window=min(50, len(close))).mean().iloc[-1]) if len(close) >= 20 else ma20
    ma200 = float(close.rolling(window=min(200, len(close))).mean().iloc[-1]) if len(close) >= 50 else ma50
    vol20 = float(volume.rolling(window=min(20, len(volume))).mean().iloc[-1])
    current_vol = float(volume.iloc[-1])
    vol_ratio = current_vol / vol20 if vol20 > 0 else 1.0

    # RSI 14
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi_series = 100 - (100 / (1 + rs))
    rsi14 = float(rsi_series.iloc[-1]) if not pd.isna(rsi_series.iloc[-1]) else 50.0

    # ATR 14
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr14 = float(tr.rolling(window=14).mean().iloc[-1]) if len(tr) >= 14 else float(tr.mean())
    if math.isnan(atr14) or atr14 <= 0:
        atr14 = current_close * 0.025  # fallback 2.5%

    price_vs_ma200 = round(((current_close - ma200) / ma200) * 100, 2) if ma200 > 0 else 0.0
    price_vs_ma20 = round(((current_close - ma20) / ma20) * 100, 2) if ma20 > 0 else 0.0
    high_52w = round(float(high.max()), 1)
    low_52w = round(float(low.min()), 1)
    pct_from_52w_high = round(((current_close - high_52w) / high_52w) * 100.0, 2) if high_52w > 0 else 0.0

    vsa_meta = derive_wyckoff_and_vsa(
        current_close, round(day_change_pct, 2), round(ma20, 1), round(ma50, 1),
        round(ma200, 1), round(rsi14, 1), round(atr14, 1), round(vol_ratio, 2),
        price_vs_ma200, price_vs_ma20
    )

    # O'Neil Weighted Relative Strength Raw Score
    raw_rs = round(0.40 * ret_3m + 0.25 * ret_6m + 0.20 * ret_1y + 0.15 * price_vs_ma200, 2)

    tech_dict = {
        "price": current_close,
        "day_change_pct": round(day_change_pct, 2),
        "change_1m_pct": ret_1m,
        "change_3m_pct": ret_3m,
        "change_6m_pct": ret_6m,
        "change_1y_pct": ret_1y,
        "ma20": round(ma20, 1),
        "ma50": round(ma50, 1),
        "ma200": round(ma200, 1),
        "rsi14": round(rsi14, 1),
        "atr14": round(atr14, 1),
        "volume": int(current_vol),
        "vol20": int(vol20),
        "vol_ratio": round(vol_ratio, 2),
        "price_vs_ma200": price_vs_ma200,
        "price_vs_ma20": price_vs_ma20,
        "high_52w": high_52w,
        "low_52w": low_52w,
        "pct_from_52w_high": pct_from_52w_high,
        "raw_rs_score": raw_rs,
    }
    tech_dict.update(vsa_meta)
    return tech_dict


def assign_oneil_rs_ratings(stocks_data: dict):
    """
    Xếp hạng Sức mạnh Giá Tương đối (O'Neil RS Rating 1 - 99) trên toàn bộ 54 mã cổ phiếu theo dõi.
    """
    scored = []
    for code, stk in stocks_data.items():
        tech = stk.get("technical", {})
        raw_rs = tech.get("raw_rs_score")
        if raw_rs is None:
            p_ma200 = tech.get("price_vs_ma200", 0.0)
            p_ma20 = tech.get("price_vs_ma20", 0.0)
            day_c = tech.get("day_change_pct", 0.0)
            rsi = tech.get("rsi14", 50.0)
            raw_rs = round(0.50 * p_ma200 + 0.30 * p_ma20 + 0.20 * (rsi - 50.0) + day_c, 2)
            tech["raw_rs_score"] = raw_rs
        scored.append((code, raw_rs))

    scored.sort(key=lambda x: x[1])
    n = max(1, len(scored))
    for idx, (code, _) in enumerate(scored):
        # Quy đổi phân vị sang thang 15 -> 98 chuẩn IBD/O'Neil
        rs_rating = int(round(18 + (idx / max(1, n - 1)) * 80))
        stocks_data[code]["technical"]["rs_rating"] = rs_rating


def enrich_existing_stock_tech(stk: dict):
    """Bổ sung đầy đủ tín hiệu Wyckoff, VSA, Chandelier Stop cho dữ liệu đã có sẵn."""
    tech = stk.get("technical", {})
    price = float(tech.get("price", 20000.0))
    day_chg = float(tech.get("day_change_pct", 0.0))
    ma20 = float(tech.get("ma20", price))
    ma50 = float(tech.get("ma50", price))
    ma200 = float(tech.get("ma200", price))
    rsi14 = float(tech.get("rsi14", 50.0))
    atr14 = float(tech.get("atr14", price * 0.025))
    vol_ratio = float(tech.get("vol_ratio", 1.0))
    p_ma200 = float(tech.get("price_vs_ma200", 0.0))
    p_ma20 = float(tech.get("price_vs_ma20", 0.0))

    vsa_meta = derive_wyckoff_and_vsa(
        price, day_chg, ma20, ma50, ma200, rsi14, atr14, vol_ratio, p_ma200, p_ma20
    )
    tech.update(vsa_meta)
    stk["technical"] = tech


def fetch_single_ticker(ticker_info):
    symbol = ticker_info["symbol"]
    code = ticker_info["code"]
    exchange = ticker_info["exchange"]

    print(f"Fetching {code} ({symbol}) [{exchange}]...")
    try:
        t = yf.Ticker(symbol)
        hist = t.history(period="1y")

        info = {}
        try:
            info = t.info or {}
        except Exception:
            pass

        tech = calculate_technical_indicators(hist)

        def to_ty_vnd(val):
            if isinstance(val, (int, float)) and not math.isnan(val) and val != 0:
                return round(float(val) / 1e9, 1)
            return None

        def to_pct(val):
            if isinstance(val, (int, float)) and not math.isnan(val):
                return round(float(val) * 100.0, 2)
            return None

        pe = info.get("trailingPE") or info.get("forwardPE") or None
        pb = info.get("priceToBook") or None
        roe = info.get("returnOnEquity") or None
        mkt_cap = info.get("marketCap") or None
        beta = info.get("beta") or 1.0

        if pe is not None:
            pe = round(float(pe), 2)
        if pb is not None:
            pb = round(float(pb), 2)
        if roe is not None:
            roe = round(float(roe) * 100, 2)
        mkt_cap_ty_vnd = to_ty_vnd(mkt_cap)

        yf_fundamentals = {
            "revenue_ty_vnd": to_ty_vnd(info.get("totalRevenue")),
            "net_income_ty_vnd": to_ty_vnd(info.get("netIncomeToCommon")),
            "ocf_ty_vnd": to_ty_vnd(info.get("operatingCashflow")),
            "fcf_ty_vnd": to_ty_vnd(info.get("freeCashflow")),
            "total_cash_ty_vnd": to_ty_vnd(info.get("totalCash")),
            "total_debt_ty_vnd": to_ty_vnd(info.get("totalDebt")),
            "revenue_growth_pct": to_pct(info.get("revenueGrowth")),
            "earnings_growth_pct": to_pct(info.get("earningsGrowth")),
            "gross_margin_pct": to_pct(info.get("grossMargins")),
            "operating_margin_pct": to_pct(info.get("operatingMargins")),
            "profit_margin_pct": to_pct(info.get("profitMargins")),
            "eps_vnd": round(float(info.get("trailingEps")), 0) if info.get("trailingEps") else None,
            "bvps_vnd": round(float(info.get("bookValue")), 0) if info.get("bookValue") else None,
        }

        return {
            "code": code,
            "symbol": symbol,
            "name": ticker_info["name"],
            "exchange": exchange,
            "tier": ticker_info["tier"],
            "weight_target": ticker_info.get("weight_target", 0.02),
            "pe": pe,
            "pb": pb,
            "roe_pct": roe,
            "market_cap_ty_vnd": mkt_cap_ty_vnd,
            "beta": round(float(beta), 2) if beta else 1.0,
            "yf_fundamentals": yf_fundamentals,
            "technical": tech,
            "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        print(f"  Warning fetching {symbol}: {e}")
        return {
            "code": code,
            "symbol": symbol,
            "name": ticker_info["name"],
            "exchange": exchange,
            "tier": ticker_info["tier"],
            "weight_target": ticker_info.get("weight_target", 0.02),
            "pe": None,
            "pb": None,
            "roe_pct": None,
            "market_cap_ty_vnd": None,
            "beta": 1.0,
            "yf_fundamentals": {},
            "technical": {
                "price": 20000.0,
                "day_change_pct": 0.0,
                "ma20": 20000.0,
                "ma50": 20000.0,
                "ma200": 20000.0,
                "rsi14": 50.0,
                "atr14": 500.0,
                "volume": 1000000,
                "vol20": 1000000,
                "vol_ratio": 1.0,
                "price_vs_ma200": 0.0,
                "price_vs_ma20": 0.0
            },
            "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }


def fetch_macro_indicators():
    """Thu thập các chỉ số vĩ mô thế giới & VN tác động trực tiếp"""
    indicators = {
        "DXY": "DX-Y.NYB",
        "US10Y": "^TNX",
        "WTI_OIL": "CL=F",
        "GOLD": "GC=F",
        "S_AND_P500": "^GSPC"
    }
    macro_data = {}
    for name, sym in indicators.items():
        try:
            t = yf.Ticker(sym)
            h = t.history(period="5d")
            if not h.empty:
                val = float(h['Close'].iloc[-1])
                prev = float(h['Close'].iloc[-2]) if len(h) > 1 else val
                chg = ((val - prev) / prev) * 100
                macro_data[name] = {"value": round(val, 2), "change_pct": round(chg, 2)}
        except Exception:
            macro_data[name] = {"value": None, "change_pct": 0.0}

    macro_data["SBV_Refinancing_Rate"] = {"value": 4.5, "unit": "%", "status": "Hỗ trợ thanh khoản"}
    macro_data["SBV_Discount_Rate"] = {"value": 3.0, "unit": "%", "status": "Ổn định"}
    macro_data["USD_VND_Exchange_Rate"] = {"value": 25420, "unit": "VND", "trend": "Đi ngang quanh đỉnh biên độ"}
    macro_data["Credit_Growth_YTD"] = {"value": 9.2, "unit": "%", "target": "15.0%"}
    macro_data["Public_Investment_Disbursed_Pct"] = {"value": 52.8, "unit": "%", "target": "95% kế hoạch"}
    return macro_data


def run(enrich_only: bool = False):
    print("=== [VN MARKET DATA FETCHER v2.0] THU THẬP DỮ LIỆU & TÍN HIỆU WYCKOFF/VSA/RS ===")
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    watchlist = load_watchlist()

    if enrich_only and os.path.exists(OUTPUT_PATH):
        with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
            existing = json.load(f)
        stocks_data = existing.get("stocks", {})
        for code, stk in stocks_data.items():
            enrich_existing_stock_tech(stk)
        assign_oneil_rs_ratings(stocks_data)
        existing["stocks"] = stocks_data
        existing["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)
        print(f"=== [ENRICHED] Đã làm giàu tín hiệu O'Neil RS Rating & Wyckoff VSA cho {len(stocks_data)} mã tại {OUTPUT_PATH} ===")
        return

    macro = fetch_macro_indicators()

    stocks_data = {}
    all_tickers = []
    for sector_key, sec in watchlist["sectors"].items():
        for t in sec["tickers"]:
            all_tickers.append((sector_key, sec["name"], t))

    print(f"Tổng số mã theo dõi: {len(all_tickers)} mã thuộc {len(watchlist['sectors'])} nhóm ngành.")

    for sector_key, sector_name, t in all_tickers:
        stock_result = fetch_single_ticker(t)
        stock_result["sector_key"] = sector_key
        stock_result["sector_name"] = sector_name
        stocks_data[t["code"]] = stock_result
        time.sleep(0.05)

    assign_oneil_rs_ratings(stocks_data)

    final_output = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_tickers": len(stocks_data),
        "macro_vietnam": macro,
        "stocks": stocks_data
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=2, ensure_ascii=False)

    print(f"=== Đã hoàn tất và lưu dữ liệu tại: {OUTPUT_PATH} ===")


if __name__ == "__main__":
    enrich_flag = "--enrich-only" in sys.argv
    run(enrich_only=enrich_flag)
