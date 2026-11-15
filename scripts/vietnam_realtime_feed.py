#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VIETNAMESE DIRECT ZERO-LATENCY REALTIME MARKET FEED ENGINE (V4.0)
File: scripts/vietnam_realtime_feed.py
Cơ quan chủ quản: Ban 9 (Victor Realtime Sentinel) & Palmer (Phòng Tổng Hệ Thống)

Nâng cấp War-Room V4.0:
- Kết nối trực tiếp cổng dữ liệu bảng điện HOSE/HNX thời gian thực (VPS Datafeed & Entrade DNSE).
- Bóc tách đầy đủ 3 bước giá Mua/Bán (g1..g6), dòng tiền khối ngoại từng mã & rổ VN30.
- Tính Buy-Up Pressure Ratio thực từ diễn biến giá trong ngày + VWAP + cân bằng sổ lệnh 3 bước giá.
- Kéo chỉ số VN-Index, VN30, HNX, UPCOM, phái sinh VN30F1M (Basis), độ rộng Tăng/Giảm,
  tốc độ thanh khoản (Volume Pace Ratio) và chỉ báo kỹ thuật sống (RSI14, MA20, MA50, ATR14).
"""

import sys
import time
import json
import datetime
import threading
import urllib.request
import urllib.parse
from typing import Dict, Any, List, Optional, Tuple

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Connection": "close"
}

VN30_BASKET = [
    "ACB", "BCM", "BID", "BVH", "CTG", "FPT", "GAS", "GVR", "HDB", "HPG",
    "LPB", "MBB", "MSN", "MWG", "PLX", "SAB", "SHB", "SSB", "SSI", "STB",
    "TCB", "TPB", "VCB", "VHM", "VIB", "VIC", "VJC", "VNM", "VPB", "VRE"
]

_CACHE_LOCK = threading.Lock()
_MARKET_CACHE: Dict[str, Any] = {"ts": 0.0, "data": None}
_FOREIGN_CACHE: Dict[str, Any] = {"ts": 0.0, "data": None}
_INDICATOR_CACHE: Dict[str, Dict[str, Any]] = {}


def _get_ict_now() -> datetime.datetime:
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    return utc_now.astimezone(datetime.timezone(datetime.timedelta(hours=7)))


def _fetch_json(url: str, timeout: int = 5) -> Any:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _parse_order_level(raw: Any) -> Tuple[float, int]:
    """Parse VPS orderbook string 'price|vol|side' -> (price_vnd, volume_shares)."""
    parts = str(raw or "").split("|")
    if len(parts) < 2:
        return 0.0, 0
    try:
        p = float(parts[0]) * 1000.0 if parts[0] else 0.0
    except Exception:
        p = 0.0
    try:
        v = int(float(parts[1])) * 10 if parts[1] else 0
    except Exception:
        v = 0
    return p, v


def _compute_active_buy_pct(
    last_price: float,
    ref_price: float,
    high_price: float,
    low_price: float,
    ave_price: float,
    total_bid_vol: int,
    total_ask_vol: int,
    bid_p1: float,
    ask_p1: float,
) -> float:
    """
    Tính tỷ lệ áp lực Mua chủ động (Buy-Up Ratio %) từ:
    1) Vị thế giá khớp trong biên độ ngày (45%),
    2) Vị thế so với VWAP bình quân & tham chiếu (25%),
    3) Cán cân 3 bước giá đặt Mua vs đặt Bán (30%).
    """
    if high_price > low_price > 0 and last_price > 0:
        range_pos = max(0.0, min(1.0, (last_price - low_price) / (high_price - low_price)))
    elif ref_price > 0 and last_price > 0:
        range_pos = max(0.0, min(1.0, 0.5 + ((last_price - ref_price) / ref_price) * 8.0))
    else:
        range_pos = 0.5

    pivot = ave_price if ave_price > 0 else ref_price
    if pivot > 0 and last_price > 0:
        vwap_score = max(0.0, min(1.0, 0.5 + ((last_price - pivot) / pivot) * 12.0))
    else:
        vwap_score = 0.5

    if total_bid_vol + total_ask_vol > 0:
        ob_score = total_bid_vol / float(total_bid_vol + total_ask_vol)
    elif last_price > 0 and ask_p1 > 0 and last_price >= ask_p1:
        ob_score = 0.65
    elif last_price > 0 and bid_p1 > 0 and last_price <= bid_p1:
        ob_score = 0.35
    else:
        ob_score = 0.5

    raw_ratio = (0.45 * range_pos + 0.25 * vwap_score + 0.30 * ob_score) * 100.0
    return round(max(15.0, min(85.0, raw_ratio)), 1)


def fetch_vps_quotes(symbols: List[str], timeout: int = 4) -> Dict[str, Dict[str, Any]]:
    """
    Truy vấn trực tiếp cổng dữ liệu VPS Datafeed (Cổng cấp dữ liệu 0-second HOSE/HNX).
    Bóc tách 3 bước giá Mua/Bán (g1..g6), Buy-Up Ratio thực & Dòng tiền Khối ngoại live.
    """
    start_t = time.perf_counter()
    sym_str = ",".join(s.upper().strip() for s in symbols if s and s.strip())
    if not sym_str:
        return {}

    url = f"https://bgapidatafeed.vps.com.vn/getliststockdata/{sym_str}"
    results: Dict[str, Dict[str, Any]] = {}
    try:
        data = _fetch_json(url, timeout=timeout)
        elapsed_ms = round((time.perf_counter() - start_t) * 1000, 1)

        for item in data:
            sym = item.get("sym", "").upper().strip()
            if not sym:
                continue

            # VPS trả về đơn vị nghìn đồng (vd: 21.20 = 21,200 VND)
            last_price = float(item.get("lastPrice") or 0.0) * 1000.0
            ref_price = float(item.get("r") or 0.0) * 1000.0
            ceil_price = float(item.get("c") or 0.0) * 1000.0
            floor_price = float(item.get("f") or 0.0) * 1000.0
            high_price = float(item.get("highPrice") or 0.0) * 1000.0
            low_price = float(item.get("lowPrice") or 0.0) * 1000.0
            open_price = float(item.get("openPrice") or 0.0) * 1000.0
            ave_price = float(item.get("avePrice") or 0.0) * 1000.0
            lot = int(float(item.get("lot") or 0)) * 10  # tổng CP khớp

            # Trường hợp phiên ATO chưa khớp giá (lastPrice = 0), lấy giá tham chiếu
            if last_price <= 0 and ref_price > 0:
                last_price = ref_price

            change_pts = (last_price - ref_price) if (last_price > 0 and ref_price > 0) else 0.0
            if ref_price > 0 and last_price > 0:
                change_pct = round((change_pts / ref_price) * 100.0, 2)
            else:
                change_pct = float(item.get("changePc") or 0.0)

            # Bóc tách đầy đủ 3 bước giá Mua (g1, g2, g3) và 3 bước giá Bán (g4, g5, g6)
            bid_levels = []
            for key in ("g1", "g2", "g3"):
                bp, bv = _parse_order_level(item.get(key))
                if bp > 0 or bv > 0:
                    bid_levels.append({"price": bp, "vol": bv})

            ask_levels = []
            for key in ("g4", "g5", "g6"):
                ap, av = _parse_order_level(item.get(key))
                if ap > 0 or av > 0:
                    ask_levels.append({"price": ap, "vol": av})

            bid_price_1, bid_vol_1 = _parse_order_level(item.get("g1"))
            ask_price_1, ask_vol_1 = _parse_order_level(item.get("g4"))
            total_bid_vol = sum(lv["vol"] for lv in bid_levels)
            total_ask_vol = sum(lv["vol"] for lv in ask_levels)

            active_buy_pct = _compute_active_buy_pct(
                last_price=last_price,
                ref_price=ref_price,
                high_price=high_price if high_price > 0 else last_price,
                low_price=low_price if low_price > 0 else last_price,
                ave_price=ave_price,
                total_bid_vol=total_bid_vol,
                total_ask_vol=total_ask_vol,
                bid_p1=bid_price_1,
                ask_p1=ask_price_1,
            )

            # Dòng tiền Khối ngoại live (fBValue/fSValue đơn vị 100 VND trên VPS)
            fb_vol = int(float(item.get("fBVol") or 0))
            fs_vol = int(float(item.get("fSVolume") or 0))
            fb_val_vnd = float(item.get("fBValue") or 0.0) * 100.0
            fs_val_vnd = float(item.get("fSValue") or 0.0) * 100.0

            results[sym] = {
                "symbol": sym,
                "market": "VIETNAM",
                "price": last_price,
                "prev_close": ref_price,
                "ref_price": ref_price,
                "ceiling_price": ceil_price,
                "floor_price": floor_price,
                "day_high": high_price if high_price > 0 else last_price,
                "day_low": low_price if low_price > 0 else last_price,
                "open_price": open_price if open_price > 0 else last_price,
                "ave_price": ave_price if ave_price > 0 else last_price,
                "change_pts": round(change_pts, 0),
                "change_pct": change_pct,
                "volume": lot,
                "bid_price_1": bid_price_1,
                "bid_vol_1": bid_vol_1,
                "ask_price_1": ask_price_1,
                "ask_vol_1": ask_vol_1,
                "bid_levels": bid_levels,
                "ask_levels": ask_levels,
                "total_bid_vol": total_bid_vol,
                "total_ask_vol": total_ask_vol,
                "active_buy_pct": active_buy_pct,
                "foreign_buy_vol": fb_vol,
                "foreign_sell_vol": fs_vol,
                "foreign_net_vol": fb_vol - fs_vol,
                "foreign_net_val_vnd": round(fb_val_vnd - fs_val_vnd, 0),
                "data_source": "VPS_DIRECT_HOSE_TICK",
                "latency_ms": elapsed_ms,
                "timestamp": _get_ict_now().strftime("%Y-%m-%dT%H:%M:%S"),
                "is_live": True
            }
    except Exception as e:
        print(f"[!] Lỗi kết nối VPS Datafeed: {e}")

    return results


def fetch_entrade_fallback(symbol: str, timeout: int = 4) -> Optional[Dict[str, Any]]:
    """Cổng dự phòng 2: Entrade DNSE Chart API."""
    start_t = time.perf_counter()
    url = f"https://services.entrade.com.vn/chart-api/v2/ohlcs/stock?symbol={symbol.upper()}&resolution=1"
    try:
        data = _fetch_json(url, timeout=timeout)
        elapsed_ms = round((time.perf_counter() - start_t) * 1000, 1)

        closes = data.get("c", [])
        volumes = data.get("v", [])
        highs = data.get("h", [])
        lows = data.get("l", [])

        if closes:
            last_price = float(closes[-1]) * 1000.0
            prev_price = float(closes[-2]) * 1000.0 if len(closes) > 1 else last_price
            chg = round(((last_price - prev_price) / prev_price) * 100.0, 2) if prev_price > 0 else 0.0
            vol = int(sum(volumes[-60:])) if volumes else 0
            dh = float(max(highs[-30:])) * 1000.0 if highs else last_price
            dl = float(min(lows[-30:])) * 1000.0 if lows else last_price

            return {
                "symbol": symbol.upper(),
                "market": "VIETNAM",
                "price": last_price,
                "prev_close": prev_price,
                "ref_price": prev_price,
                "day_high": dh,
                "day_low": dl,
                "change_pts": round(last_price - prev_price, 0),
                "change_pct": chg,
                "volume": vol,
                "active_buy_pct": _compute_active_buy_pct(last_price, prev_price, dh, dl, prev_price, 0, 0, 0, 0),
                "bid_levels": [],
                "ask_levels": [],
                "foreign_net_val_vnd": 0.0,
                "data_source": "ENTRADE_DNSE_FALLBACK",
                "latency_ms": elapsed_ms,
                "timestamp": _get_ict_now().strftime("%Y-%m-%dT%H:%M:%S"),
                "is_live": True
            }
    except Exception as e:
        print(f"[!] Lỗi kết nối Entrade: {e}")

    return None


def get_realtime_vn_quote(symbol: str, fallback_price: float = 0.0) -> Dict[str, Any]:
    """Lấy giá thời gian thực tức thì cho 1 mã chứng khoán Việt Nam."""
    sym = symbol.upper().strip()
    vps_res = fetch_vps_quotes([sym])
    if sym in vps_res and vps_res[sym]["price"] > 0:
        return vps_res[sym]

    entrade_res = fetch_entrade_fallback(sym)
    if entrade_res and entrade_res["price"] > 0:
        return entrade_res

    return {
        "symbol": sym,
        "market": "VIETNAM",
        "price": fallback_price,
        "prev_close": fallback_price,
        "ref_price": fallback_price,
        "day_high": fallback_price,
        "day_low": fallback_price,
        "change_pts": 0.0,
        "change_pct": 0.0,
        "volume": 0,
        "active_buy_pct": 50.0,
        "bid_levels": [],
        "ask_levels": [],
        "foreign_net_val_vnd": 0.0,
        "data_source": "FALLBACK_STATIC",
        "latency_ms": 0.0,
        "timestamp": _get_ict_now().strftime("%Y-%m-%dT%H:%M:%S"),
        "is_live": False
    }


def get_realtime_vn_quotes_batch(symbols: List[str]) -> Dict[str, Dict[str, Any]]:
    """Lấy giá hàng loạt cực nhanh (Batch < 200ms) cho danh mục nhiều cổ phiếu."""
    res = fetch_vps_quotes(symbols)
    for s in symbols:
        sym = s.upper().strip()
        if sym and (sym not in res or res[sym]["price"] <= 0):
            fb = fetch_entrade_fallback(sym)
            if fb:
                res[sym] = fb
    return res


def _compute_session_elapsed_fraction(now: Optional[datetime.datetime] = None) -> float:
    """
    Tính tỷ lệ thời gian giao dịch đã trôi qua trong ngày trên HOSE (tổng 240 phút:
    Sáng 09:00-11:30 = 150p, Chiều 13:00-14:30 = 90p). Dùng cho Volume Pace Ratio.
    """
    if now is None:
        now = _get_ict_now()
    if now.weekday() >= 5:
        return 1.0

    hm = now.hour * 60 + now.minute
    if hm < 9 * 60:
        return 1.0  # Trước giờ mở cửa dùng tổng phiên gần nhất
    elif hm < 11 * 60 + 30:
        elapsed = max(10, hm - 9 * 60)
    elif hm < 13 * 60:
        elapsed = 150
    elif hm < 14 * 60 + 30:
        elapsed = 150 + (hm - 13 * 60)
    else:
        elapsed = 240
    return max(0.05, min(1.0, elapsed / 240.0))


def fetch_stock_indicators_live(symbol: str, ttl_seconds: int = 300) -> Dict[str, Any]:
    """
    Lấy dữ liệu nến ngày từ VPS HistDataFeed để tính RSI(14), MA20, MA50, ATR(14), AvgVol20.
    Có cache 5 phút theo từng mã để tối ưu tốc độ SSE stream.
    """
    sym = symbol.upper().strip()
    now_ts = time.time()
    with _CACHE_LOCK:
        cached = _INDICATOR_CACHE.get(sym)
        if cached and (now_ts - cached["ts"] < cached.get("ttl", ttl_seconds)):
            return cached["data"]

    res = {
        "symbol": sym,
        "rsi14": 50.0,
        "ma20": 0.0,
        "ma50": 0.0,
        "atr14": 0.0,
        "avg_vol_20d": 0.0,
        "hi_6m": 0.0,
        "lo_6m": 0.0,
        "last_close": 0.0,
        "is_index": sym in ("VNINDEX", "VN30", "HNX", "HNXINDEX", "UPCOM", "VN30F1M")
    }
    fetch_ok = False
    try:
        t2 = int(now_ts)
        t1 = t2 - 86400 * 140
        url = f"https://histdatafeed.vps.com.vn/tradingview/history?symbol={urllib.parse.quote(sym)}&resolution=D&from={t1}&to={t2}"
        data = _fetch_json(url, timeout=7)
        closes = data.get("c", [])
        highs = data.get("h", [])
        lows = data.get("l", [])
        vols = data.get("v", [])

        if data.get("s") == "ok" and len(closes) >= 15:
            fetch_ok = True
            scale = 1.0 if res["is_index"] else 1000.0
            c_arr = [float(x) * scale for x in closes]
            h_arr = [float(x) * scale for x in highs]
            l_arr = [float(x) * scale for x in lows]
            v_arr = [float(x) for x in vols]

            # Wilder RSI(14)
            deltas = [c_arr[i] - c_arr[i - 1] for i in range(1, len(c_arr))]
            gains = [max(d, 0.0) for d in deltas]
            losses = [max(-d, 0.0) for d in deltas]
            avg_g = sum(gains[:14]) / 14.0
            avg_l = sum(losses[:14]) / 14.0
            for i in range(14, len(deltas)):
                avg_g = (avg_g * 13.0 + gains[i]) / 14.0
                avg_l = (avg_l * 13.0 + losses[i]) / 14.0
            rs = avg_g / avg_l if avg_l > 1e-9 else 100.0
            rsi14 = 100.0 - (100.0 / (1.0 + rs))

            # True Range & ATR(14)
            trs = []
            for i in range(1, len(c_arr)):
                tr = max(
                    h_arr[i] - l_arr[i],
                    abs(h_arr[i] - c_arr[i - 1]),
                    abs(l_arr[i] - c_arr[i - 1]),
                )
                trs.append(tr)
            atr14 = sum(trs[-14:]) / min(14, len(trs)) if trs else 0.0

            ma20 = sum(c_arr[-20:]) / min(20, len(c_arr))
            ma50 = sum(c_arr[-50:]) / min(50, len(c_arr)) if len(c_arr) >= 20 else ma20
            # Bỏ thanh khoản phiên hiện tại nếu đang trong phiên khi tính Avg20
            hist_vols = v_arr[-21:-1] if len(v_arr) > 21 else v_arr[:-1]
            avg_vol_20d = (sum(hist_vols) / len(hist_vols)) if hist_vols else 0.0

            res.update({
                "rsi14": round(rsi14, 1),
                "ma20": round(ma20, 2 if res["is_index"] else 0),
                "ma50": round(ma50, 2 if res["is_index"] else 0),
                "atr14": round(atr14, 2 if res["is_index"] else 0),
                "avg_vol_20d": round(avg_vol_20d, 0),
                "hi_6m": round(max(h_arr), 2 if res["is_index"] else 0),
                "lo_6m": round(min(l_arr), 2 if res["is_index"] else 0),
                "last_close": round(c_arr[-1], 2 if res["is_index"] else 0),
            })
    except Exception as e:
        print(f"[!] Lỗi tải chỉ báo kỹ thuật {sym}: {e}")

    with _CACHE_LOCK:
        _INDICATOR_CACHE[sym] = {"ts": now_ts, "ttl": (ttl_seconds if fetch_ok else 120), "data": res}
    return res


def _fetch_vn30_foreign_net_ty(ttl_seconds: int = 15) -> Dict[str, Any]:
    """Tính tổng Mua/Bán ròng Khối ngoại trực tiếp trên rổ 30 cổ phiếu VN30."""
    now_ts = time.time()
    with _CACHE_LOCK:
        if _FOREIGN_CACHE["data"] is not None and (now_ts - _FOREIGN_CACHE["ts"] < ttl_seconds):
            return _FOREIGN_CACHE["data"]

    result = {"buy_ty": 0.0, "sell_ty": 0.0, "net_ty": 0.0, "is_live": False}
    try:
        sym_str = ",".join(VN30_BASKET)
        data = _fetch_json(f"https://bgapidatafeed.vps.com.vn/getliststockdata/{sym_str}", timeout=5)
        if isinstance(data, list) and data:
            buy_vnd = sum(float(d.get("fBValue") or 0.0) * 100.0 for d in data)
            sell_vnd = sum(float(d.get("fSValue") or 0.0) * 100.0 for d in data)
            net_vnd = buy_vnd - sell_vnd
            result = {
                "buy_ty": round(buy_vnd / 1e9, 1),
                "sell_ty": round(sell_vnd / 1e9, 1),
                "net_ty": round(net_vnd / 1e9, 1),
                "is_live": True,
            }
    except Exception:
        pass

    with _CACHE_LOCK:
        _FOREIGN_CACHE["ts"] = now_ts
        _FOREIGN_CACHE["data"] = result
    return result


def _fetch_vn30f1m_live(vn30_spot: float) -> Tuple[float, float]:
    """Lấy giá hợp đồng tương lai VN30F1M sống & tính độ lệch Basis so với VN30 cơ sở."""
    f1m_price = 0.0
    try:
        t2 = int(time.time())
        t1 = t2 - 86400 * 5
        url = f"https://services.entrade.com.vn/chart-api/v2/ohlcs/derivative?symbol=VN30F1M&resolution=1&from={t1}&to={t2}"
        d = _fetch_json(url, timeout=4)
        closes = d.get("c", [])
        if closes:
            f1m_price = float(closes[-1])
    except Exception:
        pass

    if f1m_price <= 0:
        try:
            ind = fetch_stock_indicators_live("VN30F1M", ttl_seconds=60)
            f1m_price = float(ind.get("last_close") or 0.0)
        except Exception:
            pass

    if f1m_price > 0 and vn30_spot > 0:
        return round(f1m_price, 2), round(f1m_price - vn30_spot, 2)
    return 0.0, 0.0


def fetch_vn_market_indices_live(ttl_seconds: int = 4) -> Dict[str, Any]:
    """
    Lấy dữ liệu chỉ số thị trường VN-Index, VN30, HNX, UPCOM, VN30F1M Basis,
    độ rộng Tăng/Giảm, khối ngoại VN30 ròng và Volume Pace Ratio 100% LIVE.
    """
    now_ts = time.time()
    with _CACHE_LOCK:
        if _MARKET_CACHE["data"] is not None and (now_ts - _MARKET_CACHE["ts"] < ttl_seconds):
            return _MARKET_CACHE["data"]

    now_ict = _get_ict_now()
    pace_fraction = _compute_session_elapsed_fraction(now_ict)

    # Khung mặc định an toàn nếu mất kết nối ngoài giờ hoặc mạng lỗi (đánh dấu is_live=False rõ ràng)
    parsed: Dict[str, Any] = {
        "is_live": False,
        "timestamp": now_ict.strftime("%Y-%m-%d %H:%M:%S"),
        "vn_index": {
            "value": 0.0,
            "ref": 0.0,
            "change_pts": 0.0,
            "change_pct": 0.0,
            "status": "CHƯA CÓ KẾT NỐI BẢNG ĐIỆN",
            "volume_cp": "0.0M",
            "raw_volume": 0,
            "volume_pace_ratio": 1.0,
            "turnover_ty_vnd": "0 Tỷ",
            "raw_turnover_ty": 0.0,
            "foreign_net_ty_vnd": "0.0 Tỷ (VN30)",
            "raw_foreign_net_ty": 0.0,
            "rsi14": 50.0,
            "ma20": 0.0,
            "ma50": 0.0,
            "trend": "Chờ đồng bộ chỉ số"
        },
        "vn30_index": {
            "value": 0.0,
            "ref": 0.0,
            "change_pts": 0.0,
            "change_pct": 0.0,
            "vn30f1m": 0.0,
            "basis_pts": 0.0,
            "basis_vn30f": "Chưa có dữ liệu F1M",
            "status": "CHỜ ĐỒNG BỘ VN30"
        },
        "hnx_index": {
            "value": 0.0,
            "change_pts": 0.0,
            "change_pct": 0.0,
            "turnover_ty_vnd": "0 Tỷ",
        },
        "market_breadth": {
            "advancers": 0,
            "decliners": 0,
            "unchanged": 0,
            "advance_ratio_pct": 50.0,
            "sentiment": "50% TRUNG TÍNH"
        }
    }

    try:
        idx_list = _fetch_json("https://bgapidatafeed.vps.com.vn/getlistindexdetail/10,11,02,03", timeout=5)
        idx_map = {str(item.get("mc", "")): item for item in idx_list if isinstance(item, dict)}

        def _extract_idx(mc_code: str) -> Dict[str, Any]:
            raw = idx_map.get(mc_code, {})
            val = float(raw.get("cIndex") or 0.0)
            ref = float(raw.get("oIndex") or 0.0)
            vol = int(float(raw.get("vol") or 0))
            val_trieu = float(raw.get("value") or 0.0)
            ot_parts = str(raw.get("ot") or "").split("|")
            adv = int(float(ot_parts[3])) if len(ot_parts) > 3 and ot_parts[3] else 0
            dec = int(float(ot_parts[4])) if len(ot_parts) > 4 and ot_parts[4] else 0
            unc = int(float(ot_parts[5])) if len(ot_parts) > 5 and ot_parts[5] else 0
            if val <= 0 and ref > 0:
                val = ref
            chg_pts = round(val - ref, 2) if (val > 0 and ref > 0) else 0.0
            chg_pct = round((chg_pts / ref) * 100.0, 2) if ref > 0 else 0.0
            return {
                "value": round(val, 2),
                "ref": round(ref, 2),
                "change_pts": chg_pts,
                "change_pct": chg_pct,
                "volume": vol,
                "turnover_ty": round(val_trieu / 1000.0, 1),
                "advancers": adv,
                "decliners": dec,
                "unchanged": unc,
                "time": str(raw.get("time") or ""),
            }

        vni = _extract_idx("10")
        vn30 = _extract_idx("11")
        hnx = _extract_idx("02")

        # Nếu ngoài giờ nghỉ VPS index chưa có số liệu, lấy từ histdatafeed làm tham chiếu đóng cửa gần nhất
        vni_ind = fetch_stock_indicators_live("VNINDEX", ttl_seconds=300)
        if vni["value"] <= 0 and vni_ind.get("last_close", 0) > 0:
            vni["value"] = vni_ind["last_close"]

        avg_vni_vol = float(vni_ind.get("avg_vol_20d") or 0.0)
        vol_pace = round(vni["volume"] / (avg_vni_vol * pace_fraction), 2) if (avg_vni_vol > 0 and vni["volume"] > 0) else 1.0

        f1m_val, basis_pts = _fetch_vn30f1m_live(vn30["value"])
        if basis_pts > 3.0:
            basis_desc = f"+{basis_pts:.2f}đ (Kỳ vọng tăng mạnh)"
        elif basis_pts < -4.0:
            basis_desc = f"{basis_pts:.2f}đ (Phái sinh chiết khấu thủng)"
        else:
            basis_desc = f"{basis_pts:+.2f}đ (F1M: {f1m_val:,.1f})" if f1m_val > 0 else "Chờ khớp F1M"

        fn = _fetch_vn30_foreign_net_ty()
        fn_net = fn.get("net_ty", 0.0)
        if fn["is_live"]:
            fn_label = f"{fn_net:+.1f} Tỷ ({'Mua ròng' if fn_net >= 0 else 'Bán ròng'} VN30)"
        else:
            fn_label = "Chưa có dữ liệu ngoại"

        adv = vni["advancers"]
        dec = vni["decliners"]
        unc = vni["unchanged"]
        total_br = adv + dec
        adv_ratio = round((adv / total_br) * 100.0, 1) if total_br > 0 else 50.0

        if adv_ratio >= 62.0:
            sent_lbl = f"{adv_ratio:.0f}% TÍCH CỰC"
        elif adv_ratio <= 38.0:
            sent_lbl = f"{adv_ratio:.0f}% ÁP LỰC BÁN"
        else:
            sent_lbl = f"{adv_ratio:.0f}% PHÂN HÓA"

        ma20 = float(vni_ind.get("ma20") or 0.0)
        ma50 = float(vni_ind.get("ma50") or 0.0)
        vni_val = vni["value"]
        if vni_val > 0 and ma20 > 0 and ma50 > 0:
            if vni_val >= ma20 and vni["change_pct"] >= 0.3:
                vni_status = "TÍCH CỰC (TRÊN MA20)"
            elif vni_val < ma20 and vni_val >= ma50:
                vni_status = "GIẰNG CO (GIỮA MA20-MA50)"
            elif vni_val < ma50:
                vni_status = "THẬN TRỌNG (DƯỚI MA50)"
            else:
                vni_status = "ĐI NGANG TÍCH LŨY"
            trend_str = f"MA20: {ma20:,.1f} | MA50: {ma50:,.1f} | RSI14: {vni_ind['rsi14']}"
        else:
            vni_status = "ĐANG THEO DÕI PHIÊN"
            trend_str = "Đang đồng bộ đường trung bình"

        if vn30["change_pct"] >= 0.4:
            vn30_status = "RỔ VN30 DẪN DẮT TĂNG"
        elif vn30["change_pct"] <= -0.5:
            vn30_status = "VN30 CHỊU ÁP LỰC CHỈNH"
        else:
            vn30_status = "VN30 PHÂN HÓA NHẸ"

        parsed = {
            "is_live": vni["value"] > 0,
            "timestamp": now_ict.strftime("%Y-%m-%d %H:%M:%S"),
            "exchange_time": vni.get("time", ""),
            "vn_index": {
                "value": vni["value"],
                "ref": vni["ref"],
                "change_pts": vni["change_pts"],
                "change_pct": vni["change_pct"],
                "status": vni_status,
                "volume_cp": f"{vni['volume'] / 1e6:.1f}M" if vni["volume"] > 0 else "0.0M",
                "raw_volume": vni["volume"],
                "volume_pace_ratio": vol_pace,
                "turnover_ty_vnd": f"{vni['turnover_ty']:,.1f} Tỷ",
                "raw_turnover_ty": vni["turnover_ty"],
                "foreign_net_ty_vnd": fn_label,
                "raw_foreign_net_ty": fn_net,
                "rsi14": vni_ind["rsi14"],
                "ma20": ma20,
                "ma50": ma50,
                "trend": trend_str,
            },
            "vn30_index": {
                "value": vn30["value"],
                "ref": vn30["ref"],
                "change_pts": vn30["change_pts"],
                "change_pct": vn30["change_pct"],
                "vn30f1m": f1m_val,
                "basis_pts": basis_pts,
                "basis_vn30f": basis_desc,
                "status": vn30_status,
            },
            "hnx_index": {
                "value": hnx["value"],
                "change_pts": hnx["change_pts"],
                "change_pct": hnx["change_pct"],
                "turnover_ty_vnd": f"{hnx['turnover_ty']:,.1f} Tỷ",
            },
            "market_breadth": {
                "advancers": adv,
                "decliners": dec,
                "unchanged": unc,
                "advance_ratio_pct": adv_ratio,
                "sentiment": sent_lbl,
            }
        }
    except Exception as e:
        print(f"[!] Lỗi tải chỉ số thị trường VN live: {e}")

    with _CACHE_LOCK:
        _MARKET_CACHE["ts"] = now_ts
        _MARKET_CACHE["data"] = parsed
    return parsed


if __name__ == "__main__":
    test_syms = ["HDB", "MSH", "BAF", "IDC"]
    print(f"[*] Đang kiểm thử Realtime Market Feed V4.0 cho: {test_syms}...")
    mkt = fetch_vn_market_indices_live()
    print(
        f"  VN-Index: {mkt['vn_index']['value']:,.2f} ({mkt['vn_index']['change_pts']:+.2f} / {mkt['vn_index']['change_pct']:+.2f}%) "
        f"| GTGD: {mkt['vn_index']['turnover_ty_vnd']} | Pace: {mkt['vn_index']['volume_pace_ratio']:.2f}x "
        f"| Ngoại VN30: {mkt['vn_index']['foreign_net_ty_vnd']} | Độ rộng: {mkt['market_breadth']['advancers']}T/{mkt['market_breadth']['decliners']}G"
    )
    print(f"  VN30: {mkt['vn30_index']['value']:,.2f} | Basis: {mkt['vn30_index']['basis_vn30f']}")
    quotes = get_realtime_vn_quotes_batch(test_syms)
    for s, q in quotes.items():
        print(
            f"  {s} | Giá: {q['price']:,.0f} ₫ ({q['change_pct']:+.2f}%) | Vol: {q['volume']:,} "
            f"| BuyUp: {q['active_buy_pct']}% | Ngoại: {q['foreign_net_val_vnd']/1e9:+.2f}B | {q['latency_ms']}ms"
        )
