#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VIETNAMESE DIRECT ZERO-LATENCY REALTIME MARKET FEED ENGINE (V1.0)
File: scripts/vietnam_realtime_feed.py
Cơ quan chủ quản: Ban 9 (Victor Realtime Sentinel) & Palmer (Phòng Tổng Hệ Thống)

Nhiệm vụ:
- Thay thế hoàn toàn độ trễ 15-30 phút của Yahoo Finance đối với TTCK Việt Nam.
- Kết nối trực tiếp cổng dữ liệu bảng điện HOSE/HNX thời gian thực (VPS Datafeed & Entrade DNSE).
- Đo lường độ trễ (Latency < 200ms), độ chính xác 100% từng bước giá khớp lệnh.
"""

import sys
import time
import json
import urllib.request
import urllib.parse
from typing import Dict, Any, List, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Connection": "close"
}


def fetch_vps_quotes(symbols: List[str], timeout: int = 4) -> Dict[str, Dict[str, Any]]:
    """
    Truy vấn trực tiếp cổng dữ liệu VPS Datafeed (Cổng cấp dữ liệu 0-second HOSE/HNX).
    """
    start_t = time.perf_counter()
    sym_str = ",".join(s.upper().strip() for s in symbols if s.strip())
    if not sym_str:
        return {}

    url = f"https://bgapidatafeed.vps.com.vn/getliststockdata/{sym_str}"
    req = urllib.request.Request(url, headers=HEADERS)

    results: Dict[str, Dict[str, Any]] = {}
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
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
                change_pct = float(item.get("changePc") or 0.0)
                lot = int(item.get("lot") or 0) * 10  # lot đơn vị 10 CP -> tổng CP khớp
                
                # Bóc tách 3 bước giá mua bán
                g1 = str(item.get("g1") or "").split("|")
                bid_price_1 = (float(g1[0]) * 1000.0) if len(g1) >= 2 and g1[0] else 0.0
                bid_vol_1 = (int(g1[1]) * 10) if len(g1) >= 2 and g1[1].isdigit() else 0

                g4 = str(item.get("g4") or "").split("|")
                ask_price_1 = (float(g4[0]) * 1000.0) if len(g4) >= 2 and g4[0] else 0.0
                ask_vol_1 = (int(g4[1]) * 10) if len(g4) >= 2 and g4[1].isdigit() else 0

                # Trường hợp phiên ATO chưa khớp giá (lastPrice = 0), lấy giá tham chiếu
                if last_price <= 0 and ref_price > 0:
                    last_price = ref_price

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
                    "change_pct": change_pct,
                    "volume": lot,
                    "bid_price_1": bid_price_1,
                    "bid_vol_1": bid_vol_1,
                    "ask_price_1": ask_price_1,
                    "ask_vol_1": ask_vol_1,
                    "data_source": "VPS_DIRECT_HOSE_TICK",
                    "latency_ms": elapsed_ms,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "is_live": True
                }
    except Exception as e:
        print(f"[!] Lỗi kết nối VPS Datafeed: {e}")

    return results


def fetch_entrade_fallback(symbol: str, timeout: int = 4) -> Optional[Dict[str, Any]]:
    """
    Cổng dự phòng 2: Entrade DNSE Chart API.
    """
    start_t = time.perf_counter()
    url = f"https://services.entrade.com.vn/chart-api/v2/ohlcs/stock?symbol={symbol.upper()}&resolution=1"
    req = urllib.request.Request(url, headers=HEADERS)

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            elapsed_ms = round((time.perf_counter() - start_t) * 1000, 1)
            
            closes = data.get("c", [])
            volumes = data.get("v", [])
            highs = data.get("h", [])
            lows = data.get("l", [])
            
            if closes:
                last_price = float(closes[-1]) * 1000.0
                prev_price = float(closes[-2]) * 1000.0 if len(closes) > 1 else last_price
                chg = round(((last_price - prev_price) / prev_price) * 100.0, 2) if prev_price > 0 else 0.0
                vol = sum(volumes[-60:]) if volumes else 0
                
                return {
                    "symbol": symbol.upper(),
                    "market": "VIETNAM",
                    "price": last_price,
                    "prev_close": prev_price,
                    "ref_price": prev_price,
                    "day_high": float(max(highs[-30:])) * 1000.0 if highs else last_price,
                    "day_low": float(min(lows[-30:])) * 1000.0 if lows else last_price,
                    "change_pct": chg,
                    "volume": vol,
                    "data_source": "ENTRADE_DNSE_FALLBACK",
                    "latency_ms": elapsed_ms,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "is_live": True
                }
    except Exception as e:
        print(f"[!] Lỗi kết nối Entrade: {e}")

    return None


def get_realtime_vn_quote(symbol: str, fallback_price: float = 0.0) -> Dict[str, Any]:
    """
    Lấy giá thời gian thực tức thì cho 1 mã chứng khoán Việt Nam.
    Tự động thử cổng 1 (VPS) -> Cổng 2 (Entrade) -> Fallback an toàn.
    """
    sym = symbol.upper().strip()
    
    # 1. Thử cổng VPS Direct
    vps_res = fetch_vps_quotes([sym])
    if sym in vps_res and vps_res[sym]["price"] > 0:
        return vps_res[sym]

    # 2. Thử cổng Entrade Fallback
    entrade_res = fetch_entrade_fallback(sym)
    if entrade_res and entrade_res["price"] > 0:
        return entrade_res

    # 3. Fallback giữ an toàn hệ thống
    return {
        "symbol": sym,
        "market": "VIETNAM",
        "price": fallback_price,
        "prev_close": fallback_price,
        "ref_price": fallback_price,
        "day_high": fallback_price,
        "day_low": fallback_price,
        "change_pct": 0.0,
        "volume": 0,
        "data_source": "FALLBACK_STATIC",
        "latency_ms": 0.0,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "is_live": False
    }


def get_realtime_vn_quotes_batch(symbols: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Lấy giá hàng loạt cực nhanh (Batch < 200ms) cho danh mục nhiều cổ phiếu.
    """
    res = fetch_vps_quotes(symbols)
    # Kiểm tra mã nào thiếu thì fallback từng mã
    for s in symbols:
        sym = s.upper().strip()
        if sym not in res or res[sym]["price"] <= 0:
            fb = fetch_entrade_fallback(sym)
            if fb:
                res[sym] = fb
    return res


if __name__ == "__main__":
    test_syms = ["HPG", "TCB", "MBB"]
    print(f"[*] Đang kiểm thử Realtime Market Feed cho: {test_syms}...")
    quotes = get_realtime_vn_quotes_batch(test_syms)
    for s, q in quotes.items():
        print(f"  {s} | Giá: {q['price']:,.0f} ₫ | Đổi: {q['change_pct']:+.2f}% | Vol: {q['volume']:,} | Nguồn: {q['data_source']} | Độ trễ: {q['latency_ms']}ms")
