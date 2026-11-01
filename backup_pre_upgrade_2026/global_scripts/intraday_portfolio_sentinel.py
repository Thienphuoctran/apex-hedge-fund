#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/intraday_portfolio_sentinel.py

BAN 9 — BAN GIÁM SÁT DANH MỤC THỜI GIAN THỰC & ỨNG PHÓ BIẾN ĐỘNG KHẨN CẤP
Institutional Real-Time Portfolio Sentinel & Intraday Tactical Incident Commander ("Victor")

Features:
- Dynamic portfolio ingestion from Master Blotter & Portfolio Trackers (US & VN).
- Real-time intraday quote & volume streaming / polling via Yahoo Finance.
- Quantitative anomaly detection across 5 Trigger Levels:
    Level 1: Flash Price Drop (>= -2.0% warning, >= -3.5% critical).
    Level 2: Stop Loss Proximity (Distance to Stop 2xATR <= 1.5%).
    Level 3: Volume Surge / Heavy Block Dumping (Volume >= 2.5x 20d avg with price red).
    Level 4: Circuit Breaker Threat / Sàn trắng (VN floor threat <= -6.5%).
    Level 5: Breaking Black Swan Catalyst.
- Instant Incident Remediation Engine (Live War-Room):
    Option A: Synthetic Short Hedge (VN30F1M Futures or SPY Put Options).
    Option B: Tactical Partial De-risking (VWAP bounce exit).
    Option C: T+0 Intra-day Scalp (Rebound limit scalp on existing shares).
    Option D: Disciplined Fundamental Hold.
- Multi-channel Alert Dispatcher:
    - High-visibility Terminal Banner + Windows System Beep.
    - Markdown Incident War-Room file (latest_emergency_alert.md).
    - Telegram Bot Push Notification (configurable via sentinel_config.json).
    - Status telemetry json & markdown overview.
    - Simulation Drill mode (--drill <TICKER> --drop-pct <PCT>).
"""

import os
import sys
import logging

# Suppress environment and pandas/yfinance warnings completely
os.environ["PYTHONWARNINGS"] = "ignore"
import warnings
warnings.simplefilter(action='ignore', category=Warning)
logging.getLogger("yfinance").setLevel(logging.CRITICAL)

import json
import time
import re
import argparse
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import urllib.request
import urllib.parse

# Force UTF-8 on Windows Console to avoid cp1252 UnicodeEncodeError
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Try importing yfinance
try:
    import yfinance as yf
except ImportError:
    yf = None

# Try importing winsound for Windows audio alert
try:
    import winsound
except ImportError:
    winsound = None

BASE_DIR = Path(__file__).resolve().parent.parent
SENTINEL_DIR = BASE_DIR / "09_Realtime_Portfolio_Sentinel"
CONFIG_PATH = SENTINEL_DIR / "sentinel_config.json"
INCIDENT_LOGS_DIR = SENTINEL_DIR / "incident_logs"
STATUS_JSON_PATH = SENTINEL_DIR / "live_sentinel_status.json"
STATUS_MD_PATH = SENTINEL_DIR / "live_sentinel_status.md"
LATEST_ALERT_MD_PATH = SENTINEL_DIR / "latest_emergency_alert.md"

MASTER_BLOTTER_PATH = BASE_DIR / "08_Master_Investment_CIO" / "master_execution_blotter.json"
US_TRACKER_PATH = BASE_DIR / "04_Investment_Committee" / "portfolio_tracker.md"
VN_TRACKER_PATH = BASE_DIR / "VN_Market" / "04_Investment_Committee" / "vn_portfolio_tracker.md"


def load_config() -> Dict[str, Any]:
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[!] Warning: Could not read sentinel_config.json: {e}")
    return {
        "poll_interval_seconds": 60,
        "alert_thresholds": {
            "price_drop_warning_pct": -2.0,
            "price_drop_critical_pct": -3.5,
            "stop_loss_proximity_pct": 1.5,
            "volume_surge_multiplier": 2.5,
            "circuit_breaker_threat_pct_vn": -6.5,
            "circuit_breaker_threat_pct_us": -7.0
        },
        "notification_channels": {
            "terminal_banner": True,
            "system_beep": True,
            "emergency_memo_markdown": True,
            "telegram": {"enabled": False, "bot_token": "", "chat_id": ""}
        },
        "hedging_parameters": {
            "vn30f_multiplier": 100000,
            "vn30f_current_index_estimate": 1320.0,
            "us_spy_hedge_ticker": "SPY"
        }
    }


def parse_markdown_table_tracker(file_path: Path, market_type: str) -> List[Dict[str, Any]]:
    """Parse active holdings from portfolio_tracker.md or vn_portfolio_tracker.md"""
    positions = []
    if not file_path.exists():
        return positions

    try:
        content = file_path.read_text(encoding="utf-8")
        lines = content.splitlines()
        in_table = False
        headers = []

        for line in lines:
            line_str = line.strip()
            # Stop parsing when reaching Section 2 (Watchlist / Locked Earnings)
            if line_str.startswith("## 2.") or "KHÓA MUA MỚI" in line_str.upper() or "WATCHLIST" in line_str.upper():
                break

            if line_str.startswith("|") and "---" not in line_str:
                cells = [c.strip().replace("**", "").replace("`", "") for c in line_str.split("|")[1:-1]]
                if not headers and ("MÃ" in line_str.upper() or "MÃ CK" in line_str.upper() or "SYMBOL" in line_str.upper()):
                    headers = [c.upper() for c in cells]
                    in_table = True
                    continue
                if in_table and cells and len(cells) >= 4:
                    sym = cells[0].strip()
                    if not sym or sym.startswith("#") or "MÃ" in sym.upper() or "TỔNG" in sym.upper():
                        continue

                    # Extract price & stop if available
                    curr_price = 0.0
                    stop_price = 0.0
                    weight_pct = 5.0

                    for i, h in enumerate(headers):
                        if i < len(cells):
                            val = cells[i].replace("$", "").replace(",", "").replace("%", "").strip()
                            if "GIÁ HIỆN TẠI" in h or "GIÁ HIỆN" in h:
                                try:
                                    curr_price = float(val)
                                except ValueError:
                                    pass
                            elif "STOP" in h or "CẮT LỖ" in h:
                                try:
                                    stop_price = float(val)
                                except ValueError:
                                    pass
                            elif "TỶ TRỌNG" in h:
                                try:
                                    weight_pct = float(val)
                                except ValueError:
                                    pass

                    positions.append({
                        "symbol": sym,
                        "market": market_type,
                        "current_price": curr_price,
                        "stop_loss_2atr": stop_price,
                        "weight_nav_pct": weight_pct,
                        "source": file_path.name
                    })
    except Exception as e:
        print(f"[!] Warning parsing {file_path}: {e}")

    return positions


def load_all_active_positions() -> List[Dict[str, Any]]:
    """Loads active invested positions from Master Blotter and IC Trackers."""
    positions_map: Dict[str, Dict[str, Any]] = {}

    # 1. Read Master Execution Blotter (Highest Priority)
    if MASTER_BLOTTER_PATH.exists():
        try:
            with open(MASTER_BLOTTER_PATH, "r", encoding="utf-8") as f:
                blotter = json.load(f)

            for order in blotter.get("orders_us_global", []):
                sym = order.get("symbol", "").strip()
                if sym:
                    positions_map[sym] = {
                        "symbol": sym,
                        "market": "US_GLOBAL",
                        "name": order.get("name", sym),
                        "sector": order.get("sector", "Global"),
                        "sleeve": order.get("sleeve", "CORE COMPOUNDER"),
                        "shares": order.get("shares", 0),
                        "allocated_capital": order.get("allocated_capital_usd", 0.0),
                        "currency": "USD",
                        "current_price": order.get("current_price_usd", 0.0),
                        "entry_strategy": order.get("entry_strategy", ""),
                        "limit_pullback_price": order.get("limit_pullback_price_usd", 0.0),
                        "stop_loss_2atr": order.get("stop_loss_2atr_usd", 0.0),
                        "tp1": order.get("tp1_usd", 0.0),
                        "tp2": order.get("tp2_usd", 0.0),
                        "weight_nav_pct": order.get("weight_nav_pct", 5.0),
                        "bctc_thesis": order.get("bctc_thesis", ""),
                        "catalysts": order.get("catalysts", ""),
                        "source": "master_execution_blotter.json"
                    }

            for order in blotter.get("orders_vietnam", []):
                sym = order.get("symbol", "").strip()
                if sym:
                    positions_map[sym] = {
                        "symbol": sym,
                        "market": "VIETNAM",
                        "name": order.get("name", sym),
                        "sector": order.get("sector", "Vietnam"),
                        "sleeve": order.get("sleeve", "TACTICAL ALPHA"),
                        "shares": order.get("shares", 0),
                        "allocated_capital": order.get("allocated_capital_vnd", 0.0),
                        "currency": "VND",
                        "current_price": order.get("current_price_vnd", 0.0),
                        "entry_strategy": order.get("entry_strategy", ""),
                        "limit_pullback_price": order.get("limit_pullback_price_vnd", 0.0),
                        "stop_loss_2atr": order.get("stop_loss_2atr_vnd", 0.0),
                        "tp1": order.get("tp1_vnd", 0.0),
                        "tp2": order.get("tp2_vnd", 0.0),
                        "weight_nav_pct": order.get("weight_nav_pct", 5.0),
                        "bctc_thesis": order.get("bctc_thesis", ""),
                        "catalysts": order.get("catalysts", ""),
                        "source": "master_execution_blotter.json"
                    }
        except Exception as e:
            print(f"[!] Warning reading master blotter: {e}")

    # 2. Augment from US Tracker
    us_tracked = parse_markdown_table_tracker(US_TRACKER_PATH, "US_GLOBAL")
    for pos in us_tracked:
        sym = pos["symbol"]
        if sym not in positions_map:
            positions_map[sym] = {
                "symbol": sym,
                "market": "US_GLOBAL",
                "name": sym,
                "sector": "Global Sector",
                "shares": 10,
                "allocated_capital": pos["current_price"] * 10,
                "currency": "USD",
                "current_price": pos["current_price"],
                "stop_loss_2atr": pos["stop_loss_2atr"],
                "tp1": pos["current_price"] * 1.10,
                "tp2": pos["current_price"] * 1.20,
                "weight_nav_pct": pos["weight_nav_pct"],
                "bctc_thesis": "Vị thế danh mục IC Tracker",
                "source": "portfolio_tracker.md"
            }

    # 3. Augment from VN Tracker
    vn_tracked = parse_markdown_table_tracker(VN_TRACKER_PATH, "VIETNAM")
    for pos in vn_tracked:
        sym = pos["symbol"]
        if sym not in positions_map:
            positions_map[sym] = {
                "symbol": sym,
                "market": "VIETNAM",
                "name": sym,
                "sector": "Vietnam Sector",
                "shares": 1000,
                "allocated_capital": pos["current_price"] * 1000,
                "currency": "VND",
                "current_price": pos["current_price"],
                "stop_loss_2atr": pos["stop_loss_2atr"],
                "tp1": pos["current_price"] * 1.10,
                "tp2": pos["current_price"] * 1.20,
                "weight_nav_pct": pos["weight_nav_pct"],
                "bctc_thesis": "Vị thế danh mục VN IC Tracker",
                "source": "vn_portfolio_tracker.md"
            }

    return list(positions_map.values())


def fetch_live_quote(symbol: str, market: str, fallback_price: float) -> Dict[str, Any]:
    """Fetches latest intraday price, % change, and volume."""
    res = {
        "symbol": symbol,
        "market": market,
        "price": fallback_price,
        "prev_close": fallback_price,
        "change_pct": 0.0,
        "day_high": fallback_price,
        "day_low": fallback_price,
        "volume": 0,
        "avg_volume": 1000000,
        "volume_surge_ratio": 1.0,
        "vwap_est": fallback_price,
        "timestamp": datetime.datetime.now().isoformat(),
        "is_live": False
    }

    if not yf:
        return res

    yf_ticker = symbol if market == "US_GLOBAL" else f"{symbol}.VN"

    try:
        t = yf.Ticker(yf_ticker)
        # Try fast info
        info = getattr(t, "fast_info", None)
        if info:
            last_price = getattr(info, "last_price", None) or getattr(info, "regular_market_previous_close", None)
            prev_close = getattr(info, "previous_close", None) or getattr(info, "regular_market_previous_close", None)
            day_high = getattr(info, "day_high", None) or last_price
            day_low = getattr(info, "day_low", None) or last_price
            day_vol = getattr(info, "last_volume", None) or 0
            avg_vol = getattr(info, "three_month_average_volume", None) or 1000000

            if last_price and last_price > 0:
                res["price"] = float(last_price)
                res["prev_close"] = float(prev_close) if prev_close else float(last_price)
                if res["prev_close"] > 0:
                    res["change_pct"] = round(((res["price"] - res["prev_close"]) / res["prev_close"]) * 100.0, 2)
                res["day_high"] = float(day_high) if day_high else res["price"]
                res["day_low"] = float(day_low) if day_low else res["price"]
                res["volume"] = int(day_vol) if day_vol else 0
                res["avg_volume"] = int(avg_vol) if avg_vol else 1000000
                if res["avg_volume"] > 0 and res["volume"] > 0:
                    res["volume_surge_ratio"] = round(res["volume"] / res["avg_volume"], 2)
                res["vwap_est"] = round((res["day_high"] + res["day_low"] + res["price"]) / 3.0, 2)
                res["is_live"] = True
                return res

        # Fallback to history 1d
        hist = t.history(period="5d", interval="1d")
        if not hist.empty:
            last_row = hist.iloc[-1]
            prev_row = hist.iloc[-2] if len(hist) > 1 else last_row
            last_price = float(last_row["Close"])
            prev_close = float(prev_row["Close"])
            res["price"] = last_price
            res["prev_close"] = prev_close
            if prev_close > 0:
                res["change_pct"] = round(((last_price - prev_close) / prev_close) * 100.0, 2)
            res["day_high"] = float(last_row["High"])
            res["day_low"] = float(last_row["Low"])
            res["volume"] = int(last_row["Volume"])
            res["avg_volume"] = int(hist["Volume"].mean())
            if res["avg_volume"] > 0:
                res["volume_surge_ratio"] = round(res["volume"] / res["avg_volume"], 2)
            res["vwap_est"] = round((res["day_high"] + res["day_low"] + res["price"]) / 3.0, 2)
            res["is_live"] = True
    except Exception as e:
        # Graceful fallback, no panic
        pass

    return res


def compute_anomaly_metrics(position: Dict[str, Any], quote: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluates position against 5 Sentinel Trigger Levels."""
    thresholds = config.get("alert_thresholds", {})
    p_warn = thresholds.get("price_drop_warning_pct", -2.0)
    p_crit = thresholds.get("price_drop_critical_pct", -3.5)
    stop_prox_thresh = thresholds.get("stop_loss_proximity_pct", 1.5)
    vol_surge_thresh = thresholds.get("volume_surge_multiplier", 2.5)
    floor_thresh = thresholds.get("circuit_breaker_threat_pct_vn", -6.5) if position["market"] == "VIETNAM" else thresholds.get("circuit_breaker_threat_pct_us", -7.0)

    price = quote["price"]
    change_pct = quote["change_pct"]
    stop_loss = position.get("stop_loss_2atr", 0.0)

    stop_dist_pct = 999.0
    if price > 0 and stop_loss > 0:
        stop_dist_pct = round(((price - stop_loss) / price) * 100.0, 2)

    volume_ratio = quote.get("volume_surge_ratio", 1.0)

    triggers_hit = []
    severity = "NORMAL"  # NORMAL, WARNING, CRITICAL, EMERGENCY

    # Level 4: Floor / Circuit Breaker threat
    if change_pct <= floor_thresh:
        triggers_hit.append({
            "level": "LEVEL 4 — NGUY CƠ KẸT SÀN / MẤT THANH KHOẢN (CIRCUIT BREAKER)",
            "desc": f"Giá giảm kịch sàn ({change_pct:.2f}% <= {floor_thresh}%). Nguy cơ trắng bên mua!"
        })
        severity = "EMERGENCY"

    # Level 2: Stop proximity
    if stop_loss > 0 and stop_dist_pct <= stop_prox_thresh:
        triggers_hit.append({
            "level": "LEVEL 2 — BÁO ĐỘNG ĐỎ CẬN KỀ STOP LOSS 2xATR",
            "desc": f"Giá hiện tại {price} chỉ còn cách Stop Loss ({stop_loss}) {stop_dist_pct:.2f}% (Ngưỡng cảnh báo <= {stop_prox_thresh}%)."
        })
        if severity != "EMERGENCY":
            severity = "CRITICAL"

    # Level 1: Price shock
    if change_pct <= p_crit:
        triggers_hit.append({
            "level": "LEVEL 1B — BIẾN ĐỘNG SỤT GIẢM CỰC MẠNH (CRITICAL FLASH DROP)",
            "desc": f"Giá sụt giảm {change_pct:.2f}% trong phiên (Vượt ngưỡng cảnh báo đỏ {p_crit}%)."
        })
        if severity not in ["EMERGENCY", "CRITICAL"]:
            severity = "CRITICAL"
    elif change_pct <= p_warn:
        triggers_hit.append({
            "level": "LEVEL 1A — BIẾN ĐỘNG SỤT GIẢM CẦN QUAN SÁT (WARNING DROP)",
            "desc": f"Giá giảm {change_pct:.2f}% trong phiên (Vượt ngưỡng cảnh báo vàng {p_warn}%)."
        })
        if severity == "NORMAL":
            severity = "WARNING"

    # Level 3: Volume surge on red day
    if change_pct < -1.0 and volume_ratio >= vol_surge_thresh:
        triggers_hit.append({
            "level": "LEVEL 3 — XẢ HÀNG ĐỘT BIẾN / DẤU CHÂN CÁ MẬP (WHALE DUMPING)",
            "desc": f"Khối lượng khớp lệnh tăng vọt {volume_ratio:.2f}x so với trung bình 20 phiên tại vùng giá giảm."
        })
        if severity not in ["EMERGENCY"]:
            severity = "CRITICAL"

    # Synthetic Short Hedge Calculation
    hedging = {}
    if position["market"] == "VIETNAM":
        vn30f_idx = config.get("hedging_parameters", {}).get("vn30f_current_index_estimate", 1320.0)
        contract_val = vn30f_idx * 100000.0
        allocated_vnd = position.get("allocated_capital", price * position.get("shares", 1000))
        # Estimate contracts needed to hedge this position
        contracts_needed = max(1, round(allocated_vnd / contract_val)) if contract_val > 0 else 1
        hedging = {
            "instrument": "Hợp Đồng Tương Lai VN30F1M",
            "action": f"SHORT {contracts_needed} HỢP ĐỒNG VN30F1M",
            "notional_hedged_vnd": contracts_needed * contract_val,
            "hedge_ratio_pct": round((contracts_needed * contract_val / allocated_vnd) * 100.0, 1) if allocated_vnd > 0 else 100.0
        }
    else:
        allocated_usd = position.get("allocated_capital", price * position.get("shares", 50))
        contracts_needed = max(1, round(allocated_usd / (quote["price"] * 100.0))) if quote["price"] > 0 else 1
        hedging = {
            "instrument": "SPY / QQQ Put Options Protective Collar",
            "action": f"BUY {contracts_needed} PUT CONTRACT(S) AT-THE-MONEY",
            "notional_hedged_usd": allocated_usd,
            "hedge_ratio_pct": 100.0
        }

    return {
        "symbol": position["symbol"],
        "market": position["market"],
        "name": position.get("name", position["symbol"]),
        "current_price": price,
        "prev_close": quote["prev_close"],
        "change_pct": change_pct,
        "stop_loss_2atr": stop_loss,
        "stop_dist_pct": stop_dist_pct,
        "volume_surge_ratio": volume_ratio,
        "vwap_est": quote.get("vwap_est", price),
        "severity": severity,
        "triggers_hit": triggers_hit,
        "hedging_solution": hedging,
        "shares": position.get("shares", 0),
        "allocated_capital": position.get("allocated_capital", 0.0),
        "currency": position.get("currency", "USD" if position["market"] == "US_GLOBAL" else "VND"),
        "bctc_thesis": position.get("bctc_thesis", ""),
        "catalysts": position.get("catalysts", "")
    }


def send_telegram_alert(config: Dict[str, Any], text: str):
    """Sends message to Telegram Bot if enabled."""
    tg_cfg = config.get("notification_channels", {}).get("telegram", {})
    if not tg_cfg.get("enabled", False):
        return

    bot_token = tg_cfg.get("bot_token", "").strip()
    chat_id = tg_cfg.get("chat_id", "").strip()

    if not bot_token or not chat_id or "YOUR_" in bot_token:
        print("  [i] Telegram chưa kích hoạt token thực tế. Bỏ qua gửi tin nhắn.")
        return

    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                print("  [+] Đã gửi tin nhắn cảnh báo thành công qua Telegram Bot!")
    except Exception as e:
        print(f"  [!] Lỗi gửi Telegram: {e}")


def sound_emergency_alarm():
    """Sounds an audible beep on Windows."""
    if winsound:
        try:
            for _ in range(3):
                winsound.Beep(1200, 200)
                time.sleep(0.08)
        except Exception:
            pass


def generate_emergency_incident_memo(incident: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Generates the comprehensive War-Room Incident Markdown memo."""
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sym = incident["symbol"]
    market = incident["market"]
    price = incident["current_price"]
    change = incident["change_pct"]
    curr = incident["currency"]
    stop = incident["stop_loss_2atr"]
    stop_dist = incident["stop_dist_pct"]
    vol_ratio = incident["volume_surge_ratio"]
    hedging = incident["hedging_solution"]
    shares = incident["shares"]
    allocated = incident["allocated_capital"]

    triggers_md = ""
    for t in incident["triggers_hit"]:
        triggers_md += f"- **{t['level']}**: {t['desc']}\n"

    # Calculate exact Tactical Plan B & C
    shares_de_risk = int(shares * 0.5) if shares > 0 else 500
    cash_liberated = shares_de_risk * price
    scalp_buy_price = round(price * 0.97, 2 if curr == "USD" else 0)
    scalp_sell_price = round(price * 1.025, 2 if curr == "USD" else 0)

    memo = f"""# 🚨 [RED ALERT] BÁO CÁO BIẾN ĐỘNG KHẨN CẤP DANH MỤC & LIVE WAR-ROOM
**Phòng Ban 9**: Ban Giám Sát Danh Mục Thời Gian Thực & Ứng Phó Khẩn Cấp ("Victor")  
**Thời gian phát hiện**: `{now_str}` | **Mã Cổ Phiếu Báo Động**: **`{sym}`** ({market})  
**Mức độ khẩn cấp**: **`{incident['severity']}`** | **Trạng thái**: YÊU CẦU PHẢN ỨNG TỨC THỜI TRONG PHIÊN

---

## 1. Dữ Liệu Biến Động Thực Tế (Intraday Telemetry)
| Chỉ Số Đo Lường | Giá Trị Thực Tế | Ngưỡng Cảnh Báo An Toàn | Đánh Giá Tình Trạng |
| :--- | :---: | :---: | :--- |
| **Giá Hiện Tại** | **`{price:,.2f} {curr}`** | — | Giảm **`{change:+.2f}%`** so với tham chiếu |
| **Khoảng Cách Đến Stop 2xATR** | **`{stop_dist:+.2f}%`** | `> 1.5%` | Ngưỡng cắt lỗ: **`{stop:,.2f} {curr}`** |
| **Tỷ Lệ Bùng Nổ Khối Lượng** | **`{vol_ratio:.2f}x`** | `< 2.5x` | {"⚠️ Cá mập xả hàng bất thường" if vol_ratio >= 2.0 else "Khối lượng ở mức kiểm soát"} |
| **Quy Mô Vốn Đang Rủi Ro** | **`{allocated:,.2f} {curr}`** | — | Số lượng đang nắm: `{shares:,} cổ phiếu` |
| **Giá Trị Trung Bình VWAP** | **`{incident['vwap_est']:,.2f} {curr}`** | — | Vùng kháng cự ngắn hạn trong phiên |

### Các Dị Thường Kích Hoạt Còi Báo Động:
{triggers_md}

---

## 2. Thẩm Tra Căn Nguyên & Luận Điểm Doanh Nghiệp (Root-Cause Audit)
* **Luận điểm BCTC cốt lõi đã phê duyệt**:
  > *"{incident.get('bctc_thesis', 'Đang cập nhật BCTC')}"*
* **Chất xúc tác & Nguy cơ**:
  > *"{incident.get('catalysts', 'Đang cập nhật Catalysts')}"*
* **Nhận định sơ bộ của Victor**:
  - Biến động này do **áp lực bán tháo kỹ thuật toàn thị trường (Contagion)** hay do **tin đồn thiên nga đen ảnh hưởng trực tiếp tới nội tại doanh nghiệp**?
  - Dòng tiền tự do FCF / Dòng tiền hoạt động OCF của doanh nghiệp không thay đổi trong vài giờ. Đây là bài test bản lĩnh và kỷ luật thể chế!

---

## 3. CHIẾN HẠM 4 PHƯƠNG ÁN KHẮC PHỤC TỨC THỜI TRONG NGÀY (TACTICAL ACTION MATRIX)

Nhà đầu tư hãy cùng Victor chọn 1 trong 4 phương án hành động sau:

### 🛡️ PHƯƠNG ÁN A: SYNTHETIC SHORT HEDGE (VŨ KHÍ PHÒNG VỆ KHÓA LỖ T+2.5) — *[KHUYẾN NGHỊ CAO KHI KẸT HÀNG T+]*
* **Bản chất**: Cổ phiếu cơ sở bị giảm nhưng chưa về tài khoản hoặc không muốn bán tháo giá đáy.
* **Lệnh thực thi ngay**:
  - **Hành động**: **`{hedging['action']}`**
  - **Quy mô danh mục được bảo vệ**: `{hedging.get('notional_hedged_vnd', hedging.get('notional_hedged_usd', 0)):,.2f} {curr}` (Bảo hộ **`{hedging['hedge_ratio_pct']}%`** giá trị vị thế).
* **Kết quả**: Vị thế phái sinh Short sẽ sinh lời tương đương mức lỗ của cổ phiếu cơ sở, **khóa băng mức lỗ danh mục 100% tức thì**!

---

### ✂️ PHƯƠNG ÁN B: PARTIAL TACTICAL DE-RISKING (HẠ TỶ TRỌNG CHỦ ĐỘNG 50%)
* **Bản chất**: Giảm áp lực Margin và hạ rủi ro danh mục nếu hàng đã về tài khoản.
* **Lệnh thực thi ngay**:
  - Canh nhịp kéo nảy kỹ thuật về vùng VWAP (`{incident['vwap_est']:,.2f} {curr}`), đặt bán **`{shares_de_risk:,} cổ phiếu`** (50% vị thế).
  - Thu hồi ngay dòng tiền mặt: **`~{cash_liberated:,.2f} {curr}`** bổ sung vào quỹ Dry Powder.

---

### ⚡ PHƯƠNG ÁN C: T+0 INTRA-DAY SCALP (LƯỚT SÓNG ĐẢO HÀNG HẠ GIÁ VỐN)
* **Bản chất**: Dành cho trường hợp rũ bỏ kỹ thuật do tin giả (Washout), tài khoản đã có sẵn lượng hàng cũ.
* **Lệnh thực thi ngay**:
  - Trích một phần Dry Powder gom thêm một lượng cổ phiếu tại vùng giá quá bán: **`{scalp_buy_price:,.2f} {curr}`** (-3% dưới giá hiện tại).
  - Ngay khi lực cầu hồi phục kéo giá lên: **`{scalp_sell_price:,.2f} {curr}`**, bán trả ngay số lượng hàng tương ứng có sẵn.
  - Số cổ phiếu giữ nguyên nhưng hạ được giá vốn ngay trong ngày mà **không bị kẹt thêm vòng T+ mới**.

---

### 🧘 PHƯƠNG ÁN D: DISCIPLINED HOLD & RE-AFFIRM THESIS (GIỮ VỮNG TÂM LÝ KỶ LUẬT)
* **Bản chất**: Nếu giá vẫn chưa chạm $Stop 2xATR$ (`{stop:,.2f} {curr}`) và BCTC doanh nghiệp vẫn siêu tăng trưởng, không manh động bán tháo hoảng loạn cùng đám đông.
* **Hành động**: Giữ nguyên trạng thái, tiếp tục để Victor giám sát sát sao mỗi 60 giây.

---

## 4. Bàn Trực Tác Chiến (War-Room Confirmation)
> [!IMPORTANT]
> **Nhà Đầu Tư Hãy Lựa Chọn Phương Án**:  
> Vui lòng phản hồi tin nhắn trong phiên: gõ **`A`** (Hedge phái sinh), **`B`** (Hạ 50% vị thế), **`C`** (Lướt T+0 hạ giá vốn), hoặc **`D`** (Kiên định giữ) để Victor cùng bạn ghi nhận vào Sổ Nhật Ký Ứng Cứu Biến Động!
"""
    return memo


def run_sentinel_audit(positions: List[Dict[str, Any]], config: Dict[str, Any], drill_target: Optional[str] = None, drill_drop_pct: float = -5.5) -> Dict[str, Any]:
    """Runs a complete telemetry scan across all monitored positions."""
    print("\n" + "="*80)
    print(f"  BAN 9 — REAL-TIME PORTFOLIO SENTINEL ('VICTOR') — INTRADAY SCAN AUDIT")
    print(f"  Thời gian quét: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Số lượng mã theo dõi: {len(positions)}")
    print("="*80)

    results = []
    emergency_alerts = []

    for pos in positions:
        sym = pos["symbol"]
        market = pos["market"]
        base_price = pos.get("current_price", 100.0)

        # In drill mode, inject shock into chosen ticker
        if drill_target and sym.upper() == drill_target.upper():
            print(f"  [>>> DIỄN TẬP KHẨN CẤP <<<] Bơm biến động sốc {drill_drop_pct:.2f}% vào mã {sym}...")
            shocked_price = round(base_price * (1.0 + drill_drop_pct / 100.0), 2)
            quote = {
                "symbol": sym,
                "market": market,
                "price": shocked_price,
                "prev_close": base_price,
                "change_pct": drill_drop_pct,
                "day_high": base_price,
                "day_low": shocked_price,
                "volume": 3500000,
                "avg_volume": 1000000,
                "volume_surge_ratio": 3.5,
                "vwap_est": round((base_price + shocked_price) / 2.0, 2),
                "timestamp": datetime.datetime.now().isoformat(),
                "is_live": True
            }
        else:
            quote = fetch_live_quote(sym, market, base_price)

        metrics = compute_anomaly_metrics(pos, quote, config)
        results.append(metrics)

        # Print row
        sev = metrics["severity"]
        sym_str = f"{sym:<6}"
        price_str = f"{metrics['current_price']:>10,.2f}"
        change_str = f"{metrics['change_pct']:>+6.2f}%"
        stop_dist_str = f"{metrics['stop_dist_pct']:>+6.2f}%"
        vol_str = f"{metrics['volume_surge_ratio']:>4.1f}x"

        status_tag = "[OK] BÌNH THƯỜNG"
        if sev == "EMERGENCY":
            status_tag = "🔥 KHẨN CẤP CẤP ĐỘ 1"
            emergency_alerts.append(metrics)
        elif sev == "CRITICAL":
            status_tag = "🚨 BÁO ĐỘNG ĐỎ"
            emergency_alerts.append(metrics)
        elif sev == "WARNING":
            status_tag = "⚠️ CẢNH GIÁC"

        print(f"  {sym_str} | Giá: {price_str} | Thay đổi: {change_str} | Cách Stop: {stop_dist_str} | Vol: {vol_str} | {status_tag}")

    # Process Emergency Alerts if any
    if emergency_alerts:
        sound_emergency_alarm()
        print("\n" + "!"*80)
        print("  🚨🚨🚨 PHÁT HIỆN BIẾN ĐỘNG KHẨN CẤP TRONG PHIÊN! 🚨🚨🚨")
        print("!"*80)

        for alert in emergency_alerts:
            memo_content = generate_emergency_incident_memo(alert, config)

            # Write latest alert memo
            LATEST_ALERT_MD_PATH.write_text(memo_content, encoding="utf-8")

            # Write to incident log archive
            ts_slug = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
            log_file = INCIDENT_LOGS_DIR / f"{ts_slug}_{alert['symbol']}_INCIDENT.md"
            log_file.write_text(memo_content, encoding="utf-8")

            # Send Telegram alert if configured
            tg_msg = (
                f"🚨 *[VICTOR SENTINEL ALERT]*\n"
                f"Mã: *{alert['symbol']}* ({alert['market']})\n"
                f"Giá hiện tại: *{alert['current_price']:,.2f}* ({alert['change_pct']:+.2f}%)\n"
                f"Khoảng cách đến Stop 2xATR: *{alert['stop_dist_pct']:+.2f}%*\n"
                f"Mức độ: *{alert['severity']}*\n"
                f"👉 Phương án tức thời: {alert['hedging_solution']['action']}\n"
                f"Xem chi tiết tại latest_emergency_alert.md!"
            )
            send_telegram_alert(config, tg_msg)

            print(f"  -> Đã lập Bản Tin Tác Chiến Khẩn Cấp tại: {LATEST_ALERT_MD_PATH.name}")
            print(f"  -> Lưu trữ sự cố tại: incident_logs/{log_file.name}")
    else:
        print("\n  [✓] Toàn bộ danh mục đang trong ngưỡng an toàn ổn định. Không có dị thường.")

    # Save overall status JSON & Markdown
    status_summary = {
        "last_scan_utc": datetime.datetime.now().isoformat(),
        "total_positions_monitored": len(positions),
        "emergency_alerts_active": len(emergency_alerts),
        "status": "ALERT_ACTIVE" if emergency_alerts else "ALL_NORMAL",
        "positions": results
    }

    STATUS_JSON_PATH.write_text(json.dumps(status_summary, indent=2, ensure_ascii=False), encoding="utf-8")

    # Generate live_sentinel_status.md
    md_overview = f"""# BẢNG THEO DÕI DANH MỤC THỜI GIAN THỰC (LIVE SENTINEL STATUS)
*Cập nhật gần nhất*: `{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`  
*Trạng thái hệ thống*: **`{'🚨 CÓ BIẾN ĐỘNG KHẨN CẤP' if emergency_alerts else '✅ TOÀN BỘ ỔN ĐỊNH'}`**  
*Tổng số mã đang bảo vệ*: **`{len(positions)} mã`**

| Mã CP | Thị Trường | Giá Hiện Tại | Biến Động Hôm Nay | Ngưỡng Stop 2xATR | Cách Stop (%) | Vol Surge | Trạng Thái Rủi Ro |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
"""
    for r in results:
        curr = r["currency"]
        tag = "✅ Bình thường"
        if r["severity"] == "EMERGENCY":
            tag = "🔥 **Khẩn cấp sàn trắng**"
        elif r["severity"] == "CRITICAL":
            tag = "🚨 **Báo động đỏ**"
        elif r["severity"] == "WARNING":
            tag = "⚠️ Cảnh giác"

        md_overview += f"| **`{r['symbol']}`** | {r['market']} | `{r['current_price']:,.2f} {curr}` | `{r['change_pct']:+.2f}%` | `{r['stop_loss_2atr']:,.2f} {curr}` | `{r['stop_dist_pct']:+.2f}%` | `{r['volume_surge_ratio']:.1f}x` | {tag} |\n"

    STATUS_MD_PATH.write_text(md_overview, encoding="utf-8")

    return status_summary


def main():
    parser = argparse.ArgumentParser(description="Ban 9 — Apex Live Portfolio Sentinel & Tactical Incident Response Engine")
    parser.add_argument("--scan-once", action="store_true", help="Chạy quét rà soát toàn bộ danh mục 1 lần duy nhất.")
    parser.add_argument("--daemon", action="store_true", help="Chạy chế độ tiến trình nền giám sát liên tục theo chu kỳ.")
    parser.add_argument("--interval", type=int, default=60, help="Chu kỳ quét (giây) khi chạy chế độ nền (mặc định 60s).")
    parser.add_argument("--drill", type=str, default=None, help="Mã cổ phiếu dùng để diễn tập tình huống khẩn cấp (vd: NVDA, VHM, FPT).")
    parser.add_argument("--drop-pct", type=float, default=-5.8, help="Mức sụt giảm giả lập dùng trong chế độ diễn tập (vd: -5.8%%).")

    args = parser.parse_args()

    config = load_config()
    positions = load_all_active_positions()

    if not positions:
        print("[!] Không tìm thấy cổ phiếu nào trong danh mục đầu tư để theo dõi.")
        sys.exit(1)

    if args.drill:
        run_sentinel_audit(positions, config, drill_target=args.drill, drill_drop_pct=args.drop_pct)
        return

    if args.daemon:
        interval = args.interval or config.get("poll_interval_seconds", 60)
        print(f"\n[*] Khởi động Tiến trình Nền Ban 9 (Victor). Chu kỳ quét: mỗi {interval} giây.")
        print(f"[*] Nhấn Ctrl + C để dừng tiến trình.")
        try:
            while True:
                # Reload positions in case master blotter changed
                current_positions = load_all_active_positions()
                run_sentinel_audit(current_positions, config)
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n[*] Đã dừng tiến trình giám sát nền Ban 9 an toàn.")
    else:
        # Default single scan audit
        run_sentinel_audit(positions, config)


if __name__ == "__main__":
    main()
