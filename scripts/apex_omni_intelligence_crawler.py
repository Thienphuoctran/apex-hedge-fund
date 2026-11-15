#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APEX OMNI-MARKET INTELLIGENCE CRAWLER & SEARCH ENGINE (V5.0 — STEP 1)
File: scripts/apex_omni_intelligence_crawler.py
Cơ quan chủ quản: Ban 2 (BCTC & Pháp Y), Ban 10 (Hiền Radar IR/CBTT) & Palmer Architecture

Chức năng 4 lớp chuẩn định chế:
1. Real-Time Multi-Source Crawler (`crawl_realtime_market_intelligence`):
   - Quét song song (ThreadPoolExecutor, timeout 6s/nguồn) tin tức, KQKD, BCTC & CBTT từ CafeF, VnEconomy,
     VnExpress Kinh Doanh, Vietstock RSS, CNBC, MarketWatch và SEC EDGAR / CBTT Radar (`cbtt_live_radar.json`).
   - Tự động nhận diện 144+ mã VN (18 ngành HOSE/HNX/UPCoM) + 35 siêu cổ phiếu Mỹ/Toàn cầu,
     phân loại sự kiện (`BCTC_EARNINGS`, `DIVIDEND_ESOP`, `MA_INSIDER`, `MACRO_SBV_FED`, `RISK_WARNING`),
     chấm điểm tác động (`sentiment_score` [-1.0..+1.0], `urgency`).
2. Live Financial & Valuation Scraper (`fetch_live_ticker_financial_profile`):
   - Hợp nhất dữ liệu BCTC kiểm toán (`BCTC_DATABASE` 54 mã + `VN_FULL_UNIVERSE` 144 mã + US 35 mã),
     bảng giá sống VPS (`fetch_vps_quotes`), lịch sử 1 năm Entrade DNSE (`ohlcs/stock`),
     dữ liệu Phố Wall (`latest_market_snapshot.json` / `yfinance`) và cổng IR chính thống (`OFFICIAL_IR_DATABASE`).
3. Full-Market FTS5 Search Engine (`search_market_intelligence`):
   - Đồng bộ B-Tree + FTS5 trong `data/apex_institutional_vault.db` (`omni_intelligence_items`, `omni_intelligence_fts`,
     `omni_ticker_profiles`) và lưu snapshot `data/omni_market_intelligence.json`.
   - Tìm kiếm tức thời (<20ms) đồng thời hồ sơ BCTC cổ phiếu, tin tức/CBTT mới cào và kho báo cáo nội bộ.
"""

import argparse
import datetime
import hashlib
import json
import os
import re
import sqlite3
import ssl
import sys
import threading
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
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
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

DATA_DIR = BASE_DIR / "data"
CONFIG_DIR = BASE_DIR / "config"
OMNI_OUTPUT_JSON = DATA_DIR / "omni_market_intelligence.json"
LIVE_BCTC_UPDATES_JSON = DATA_DIR / "live_bctc_quarterly_updates.json"
LIVE_CATALYST_ALERTS_JSON = DATA_DIR / "live_catalyst_alerts.json"
LIVE_CATALYST_SENT_JSON = DATA_DIR / "live_catalyst_alerts_sent.json"
CBTT_RADAR_JSON = DATA_DIR / "cbtt_live_radar.json"
US_SNAPSHOT_JSON = DATA_DIR / "latest_market_snapshot.json"
US_WATCHLIST_JSON = CONFIG_DIR / "watchlist.json"
VN_WATCHLIST_JSON = BASE_DIR / "VN_Market" / "config" / "watchlist_vn.json"
DB_PATH = DATA_DIR / "apex_institutional_vault.db"

_OMNI_LOCK = threading.Lock()
_SCHEMA_READY = False
_UNIVERSE_CACHE: Optional[Dict[str, Dict[str, Any]]] = None

BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, application/json, */*",
    "Connection": "close",
}

VN_RSS_SOURCES = [
    ("CafeF - Chứng khoán", "https://cafef.vn/thi-truong-chung-khoan.rss", "VN"),
    ("CafeF - Doanh nghiệp", "https://cafef.vn/doanh-nghiep.rss", "VN"),
    ("CafeF - Tài chính Ngân hàng", "https://cafef.vn/tai-chinh-ngan-hang.rss", "VN"),
    ("CafeF - Bất động sản", "https://cafef.vn/bat-dong-san.rss", "VN"),
    ("VnEconomy - Chứng khoán", "https://vneconomy.vn/chung-khoan.rss", "VN"),
    ("VnEconomy - Tài chính", "https://vneconomy.vn/tai-chinh.rss", "VN"),
    ("VnExpress - Kinh doanh", "https://vnexpress.net/rss/kinh-doanh.rss", "VN"),
    ("Vietstock - Cổ phiếu", "https://vietstock.vn/830/chung-khoan/co-phieu.rss", "VN"),
    ("Vietstock - Doanh nghiệp", "https://vietstock.vn/739/kinh-doanh/doanh-nghiep.rss", "VN"),
]

US_RSS_SOURCES = [
    ("CNBC Top News", "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114", "US"),
    ("CNBC Economy", "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=20910258", "US"),
    ("MarketWatch Top Stories", "https://feeds.content.dowjones.io/public/rss/mw_topstories", "US"),
]

POSITIVE_KW = (
    "tăng trưởng", "bứt phá", "kỷ lục", "lãi ròng tăng", "vượt kế hoạch", "chia cổ tức",
    "mua ròng", "nâng hạng", "hợp đồng lớn", "mở rộng", "cấp phép", "khởi công", "tăng trần",
    "beats", "record", "surge", "upgrade", "rally", "growth", "profit jump", "dividend", "buyback"
)
NEGATIVE_KW = (
    "thua lỗ", "lỗ ròng", "sụt giảm", "cảnh báo", "vi phạm", "kiểm toán ngoại trừ",
    "đình chỉ", "bán tháo", "bán ròng", "giải trình", "phạt", "hủy niêm yết", "cắt margin", "vỡ nợ",
    "loss", "plunge", "miss", "downgrade", "slump", "default", "lawsuit", "investigation", "sell-off"
)


def _get_ict_now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc).astimezone(
        datetime.timezone(datetime.timedelta(hours=7))
    )


def _strip_html(raw: str) -> str:
    txt = re.sub(r"<[^>]+>", " ", raw or "")
    txt = re.sub(r"&nbsp;|&#160;", " ", txt)
    txt = re.sub(r"&amp;", "&", txt)
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt


def _load_json_safe(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _load_master_universe() -> Dict[str, Dict[str, Any]]:
    """Hợp nhất vũ trụ 144+ cổ phiếu VN (18 ngành) + 54 mã BCTC sâu + 35 mã Mỹ + IR Database."""
    global _UNIVERSE_CACHE
    if _UNIVERSE_CACHE is not None:
        return _UNIVERSE_CACHE

    universe: Dict[str, Dict[str, Any]] = {}

    # 1. Nạp 144 mã VN từ vn_full_market_scanner
    try:
        from VN_Market.scripts.vn_full_market_scanner import VN_FULL_UNIVERSE
        for sec_code, sec_info in VN_FULL_UNIVERSE.items():
            sec_name = sec_info.get("sector_name", sec_code)
            regime = sec_info.get("accounting_regime", "CORPORATE_VAS_TT200")
            for stk in sec_info.get("stocks", []):
                sym = str(stk.get("code", "")).upper().strip()
                if not sym:
                    continue
                universe[sym] = {
                    "symbol": sym,
                    "market": "VN",
                    "company_name": stk.get("name", sym),
                    "exchange": stk.get("exchange", "HOSE"),
                    "sector_code": sec_code,
                    "sector_name": sec_name,
                    "cap_tier": stk.get("cap_tier", "MidCap"),
                    "accounting_regime": regime,
                    "pe": float(stk.get("pe", 0.0) or 0.0),
                    "pb": float(stk.get("pb", 0.0) or 0.0),
                    "roe": float(stk.get("roe", 0.0) or 0.0),
                    "rev_growth_yoy": float(stk.get("rev_g", 0.0) or 0.0),
                    "profit_growth_yoy": float(stk.get("prof_g", 0.0) or 0.0),
                    "ocf_ratio": float(stk.get("ocf_r", 1.0) or 1.0),
                    "catalyst": stk.get("catalyst", ""),
                }
    except Exception:
        pass

    # Fallback watchlist_vn nếu chưa có gì
    if not universe and VN_WATCHLIST_JSON.exists():
        wl_vn = _load_json_safe(VN_WATCHLIST_JSON)
        for sec_code, sec_data in wl_vn.get("sectors", {}).items():
            for item in sec_data.get("tickers", []):
                sym = str(item.get("code") or item.get("symbol", "").replace(".VN", "")).upper().strip()
                if sym and sym not in universe:
                    universe[sym] = {
                        "symbol": sym,
                        "market": "VN",
                        "company_name": item.get("name", sym),
                        "exchange": item.get("exchange", "HOSE"),
                        "sector_code": sec_code,
                        "sector_name": sec_data.get("name", sec_code),
                        "cap_tier": item.get("tier", "LargeCap"),
                        "accounting_regime": "CORPORATE_VAS_TT200",
                        "pe": 0.0, "pb": 0.0, "roe": 0.0,
                        "rev_growth_yoy": 0.0, "profit_growth_yoy": 0.0, "ocf_ratio": 1.0,
                        "catalyst": "",
                    }

    # 2. Hợp nhất BCTC kiểm toán sâu (BCTC_DATABASE - 54 mã)
    try:
        from VN_Market.scripts.vn_bctc_analyzer import BCTC_DATABASE
        for sym, bdata in BCTC_DATABASE.items():
            s = sym.upper().strip()
            entry = universe.setdefault(s, {
                "symbol": s, "market": "VN", "company_name": s,
                "exchange": "HOSE", "sector_code": "Core", "sector_name": "Doanh Nghiệp",
                "cap_tier": "LargeCap", "pe": 0.0, "pb": 0.0, "roe": 0.0,
            })
            rev = float(bdata.get("revenue_ttm_ty", 0.0) or 0.0)
            np_ty = float(bdata.get("net_profit_ttm_ty", 0.0) or 0.0)
            ocf = float(bdata.get("ocf_ty", 0.0) or 0.0)
            eq = float(bdata.get("equity_ty", 0.0) or 0.0)
            debt = float(bdata.get("total_debt_ty", 0.0) or 0.0)
            cash = float(bdata.get("cash_and_equiv_ty", 0.0) or 0.0)
            capex = float(bdata.get("capex_ty", 0.0) or 0.0)
            entry.update({
                "accounting_regime": bdata.get("accounting_regime", entry.get("accounting_regime", "CORPORATE_VAS_TT200")),
                "revenue_ttm_ty": rev,
                "net_profit_ttm_ty": np_ty,
                "rev_growth_yoy": float(bdata.get("rev_growth_yoy", entry.get("rev_growth_yoy", 0.0)) or 0.0),
                "profit_growth_yoy": float(bdata.get("profit_growth_yoy", entry.get("profit_growth_yoy", 0.0)) or 0.0),
                "gross_margin_pct": float(bdata.get("gross_margin_pct", 0.0) or 0.0),
                "operating_margin_pct": float(bdata.get("operating_margin_pct", 0.0) or 0.0),
                "ocf_ty": ocf,
                "fcf_ty": round(ocf - capex, 1),
                "ocf_ratio": round(ocf / np_ty, 2) if np_ty > 0 else float(entry.get("ocf_ratio", 0.0)),
                "cash_and_equiv_ty": cash,
                "total_debt_ty": debt,
                "equity_ty": eq,
                "debt_to_equity": round(debt / eq, 2) if eq > 0 else 0.0,
                "roe": float(entry.get("roe", 0.0)) or (round((np_ty / eq) * 100.0, 2) if eq > 0 else 0.0),
                "casa_pct": bdata.get("casa_pct"),
                "nim_pct": bdata.get("nim_pct"),
                "npl_pct": bdata.get("npl_pct"),
                "llr_coverage_pct": bdata.get("llr_coverage_pct"),
                "car_pct": bdata.get("car_pct"),
                "receivables_ty": float(bdata.get("receivables_ty", 0.0) or 0.0),
                "inventory_ty": float(bdata.get("inventory_ty", 0.0) or 0.0),
                "unearned_revenue_ty": float(bdata.get("unearned_revenue_ty", 0.0) or 0.0),
                "agm_completion_est_pct": bdata.get("agm_completion_est_pct"),
                "audit_firm": bdata.get("audit_firm", "Kiểm toán độc lập"),
                "catalyst": bdata.get("key_catalyst") or entry.get("catalyst", ""),
                "deep_bctc_audited": True,
            })
    except Exception:
        pass

    # 3. Hợp nhất link IR chính thống
    try:
        from scripts.bctc_ir_filing_scout import OFFICIAL_IR_DATABASE
        for sym, ir in OFFICIAL_IR_DATABASE.items():
            s = sym.upper().strip()
            if s in universe:
                universe[s].update({
                    "company_name": ir.get("company_name") or universe[s].get("company_name", s),
                    "official_ir_url": ir.get("official_ir_url", ""),
                    "bctc_direct_portal": ir.get("bctc_direct_portal", ""),
                    "vietstock_docs": ir.get("vietstock_docs", f"https://finance.vietstock.vn/{s}/tai-lieu.htm"),
                    "cafef_docs": ir.get("cafef_docs", f"https://s.cafef.vn/tim-kiem.chn?keywords={s}"),
                })
    except Exception:
        pass

    for sym, info in universe.items():
        if info.get("market") == "VN":
            ex_slug = str(info.get("exchange", "HOSE")).lower()
            info.setdefault("vietstock_docs", f"https://finance.vietstock.vn/{sym}/tai-lieu.htm")
            info.setdefault("cafef_docs", f"https://s.cafef.vn/{ex_slug}/{sym}.chn")

    # 4. Nạp 35 siêu cổ phiếu Mỹ / Toàn cầu
    us_cfg = _load_json_safe(US_WATCHLIST_JSON)
    us_snap = _load_json_safe(US_SNAPSHOT_JSON)
    us_eq_map = {str(x.get("symbol", "")).upper(): x for x in us_snap.get("broad_equities", []) if x.get("symbol")}
    cik_map: Dict[str, str] = {}
    try:
        from scripts.cbtt_filings_radar import STATIC_CIK_MAP
        cik_map = dict(STATIC_CIK_MAP)
    except Exception:
        pass

    for item in us_cfg.get("broad_market_universe", []):
        sym = str(item.get("symbol", "")).upper().strip()
        if not sym:
            continue
        live_us = us_eq_map.get(sym, {})
        ext = _extract_us_snap_fields(live_us)
        cik = cik_map.get(sym, "")
        universe[sym] = {
            "symbol": sym,
            "market": "US",
            "company_name": item.get("name", sym),
            "exchange": "NASDAQ/NYSE",
            "sector_code": "US_GLOBAL",
            "sector_name": item.get("sector", "Global Equities"),
            "cap_tier": "Global_MegaCap",
            "accounting_regime": "US_GAAP",
            "sec_url": f"https://www.sec.gov/edgar/browse/?CIK={cik}" if cik else f"https://finance.yahoo.com/quote/{sym}",
            "deep_bctc_audited": bool(live_us),
            **ext,
        }

    # 5. Hợp nhất dữ liệu BCTC quý mới nhất được cào tự động (Live BCTC Auto-Refresher V6.0)
    bctc_updates = _load_json_safe(LIVE_BCTC_UPDATES_JSON).get("ticker_updates", {})
    if isinstance(bctc_updates, dict):
        for sym, patch in bctc_updates.items():
            s = sym.upper().strip()
            if s not in universe or not isinstance(patch, dict):
                continue
            universe[s]["live_bctc_patch"] = patch
            if patch.get("profit_growth_yoy") is not None and not universe[s].get("profit_growth_yoy"):
                universe[s]["profit_growth_yoy"] = float(patch["profit_growth_yoy"])
            if patch.get("rev_growth_yoy") is not None and not universe[s].get("rev_growth_yoy"):
                universe[s]["rev_growth_yoy"] = float(patch["rev_growth_yoy"])
            if patch.get("roe") is not None and not universe[s].get("roe"):
                universe[s]["roe"] = float(patch["roe"])
            if patch.get("headline"):
                old_cat = str(universe[s].get("catalyst", "")).strip()
                live_tag = f"[BCTC Live] {patch['headline'][:90]}"
                if live_tag not in old_cat:
                    universe[s]["catalyst"] = f"{live_tag} | {old_cat}" if old_cat else live_tag

    _UNIVERSE_CACHE = universe
    return universe


def _extract_us_snap_fields(live_us: Dict[str, Any]) -> Dict[str, Any]:
    """Chuẩn hóa trường dữ liệu US GAAP từ cấu trúc nested fundamentals + technical trong latest_market_snapshot.json."""
    if not live_us:
        return {
            "live_price": 0.0, "change_1d_pct": 0.0, "pe": 0.0, "pb": 0.0, "roe": 0.0,
            "rev_growth_yoy": 0.0, "profit_growth_yoy": 0.0, "ocf_ratio": 1.0,
            "fcf_b_usd": 0.0, "target_upside_pct": 0.0, "catalyst": "",
        }
    fund = live_us.get("fundamentals") if isinstance(live_us.get("fundamentals"), dict) else {}
    fcf_b = float(fund.get("free_cashflow_bil") or live_us.get("free_cash_flow_b") or 0.0)
    ocf_b = float(fund.get("operating_cashflow_bil") or 0.0)
    ni_b = float(fund.get("net_income_usd_bil") or 0.0)
    if ni_b > 0 and ocf_b != 0:
        ocf_ratio = round(ocf_b / ni_b, 2)
    else:
        ocf_ratio = 1.15 if fcf_b > 0 else 0.75
    d_to_e_raw = float(fund.get("debt_to_equity") or 0.0)
    # Yahoo Finance debtToEquity trả theo % (vd 16.97 = 0.17x)
    d_to_e = round(d_to_e_raw / 100.0, 2) if d_to_e_raw > 5.0 else round(d_to_e_raw, 2)
    upside = float(fund.get("upside_to_consensus_pct") or live_us.get("upside_to_target_pct") or 0.0)
    roic_pct = float(fund.get("roic_pct") or 0.0)
    earn_flag = str(fund.get("earnings_risk_flag") or "").strip()
    cat = f"Mục tiêu Phố Wall Upside {upside:+.1f}% | FCF ${fcf_b:.1f}B | ROIC {roic_pct:.1f}%"
    if earn_flag:
        cat += f" | {earn_flag}"
    return {
        "live_price": float(live_us.get("last_price") or 0.0),
        "change_1d_pct": float(live_us.get("change_1d_pct") or 0.0),
        "pe": float(fund.get("forward_pe") or fund.get("trailing_pe") or live_us.get("forward_pe") or live_us.get("trailing_pe") or 0.0),
        "pb": float(fund.get("price_to_book") or live_us.get("price_to_book") or 0.0),
        "roe": float(fund.get("roe_pct") or live_us.get("roe_pct") or 0.0),
        "rev_growth_yoy": float(fund.get("revenue_growth_yoy") or live_us.get("revenue_growth_pct") or 0.0),
        "profit_growth_yoy": float(fund.get("earnings_growth_yoy") or live_us.get("earnings_growth_pct") or 0.0),
        "gross_margin_pct": float(fund.get("gross_margin") or 0.0),
        "operating_margin_pct": float(fund.get("operating_margin") or 0.0),
        "ocf_ratio": ocf_ratio,
        "fcf_b_usd": fcf_b,
        "debt_to_equity": d_to_e,
        "target_upside_pct": upside,
        "rsi14": float(live_us.get("rsi_14") or 50.0),
        "ma20": float(live_us.get("ma20") or 0.0),
        "ma50": float(live_us.get("ma50") or 0.0),
        "ma200": float(live_us.get("ma200") or 0.0),
        "atr14": float(live_us.get("atr_14") or 0.0),
        "high_6m": float(live_us.get("high_52w") or 0.0),
        "low_6m": float(live_us.get("low_52w") or 0.0),
        "catalyst": cat,
    }


def _get_db_conn() -> sqlite3.Connection:
    try:
        from scripts.apex_database_engine import ApexDatabaseEngine
        return ApexDatabaseEngine.get_connection(DB_PATH)
    except Exception:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(DB_PATH), timeout=30.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        return conn


def _ensure_omni_tables() -> None:
    global _SCHEMA_READY
    if _SCHEMA_READY:
        return
    with _OMNI_LOCK:
        if _SCHEMA_READY:
            return
        with _get_db_conn() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS omni_intelligence_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_id TEXT UNIQUE NOT NULL,
                    market TEXT NOT NULL,
                    category TEXT NOT NULL,
                    urgency TEXT NOT NULL,
                    sentiment_score REAL DEFAULT 0.0,
                    tickers_json TEXT,
                    tickers_text TEXT,
                    sector TEXT,
                    title TEXT NOT NULL,
                    summary TEXT,
                    source_name TEXT,
                    source_url TEXT,
                    published_at TEXT,
                    crawled_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_omni_items_cat_crawled
                    ON omni_intelligence_items(category, crawled_at DESC);
                CREATE INDEX IF NOT EXISTS idx_omni_items_market
                    ON omni_intelligence_items(market);

                CREATE VIRTUAL TABLE IF NOT EXISTS omni_intelligence_fts USING fts5(
                    item_id UNINDEXED,
                    title,
                    summary,
                    tickers_text,
                    category,
                    sector,
                    source_name
                );

                CREATE TABLE IF NOT EXISTS omni_ticker_profiles (
                    symbol TEXT PRIMARY KEY,
                    market TEXT NOT NULL,
                    company_name TEXT,
                    sector_name TEXT,
                    live_price REAL DEFAULT 0.0,
                    change_pct REAL DEFAULT 0.0,
                    pe REAL DEFAULT 0.0,
                    pb REAL DEFAULT 0.0,
                    roe REAL DEFAULT 0.0,
                    ocf_ratio REAL DEFAULT 0.0,
                    profile_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_omni_profiles_market
                    ON omni_ticker_profiles(market, sector_name);
            """)
            conn.commit()
        _SCHEMA_READY = True


def _classify_item(title: str, summary: str, symbols_found: List[str], market: str) -> Tuple[str, str, float]:
    txt = f"{title} {summary}".lower()
    category = "MACRO_SBV_FED" if any(k in txt for k in (
        "sbv", "ngân hàng nhà nước", "lãi suất", "tỷ giá", "lạm phát", "cpi", "fed", "fomc",
        "gdp", "omo", "tín phiếu", "thuế quan", "dầu thô", "trái phiếu chính phủ", "treasury", "inflation", "rate"
    )) else "MARKET_GENERAL"

    if any(k in txt for k in ("bctc", "báo cáo tài chính", "kết quả kinh doanh", "lợi nhuận", "lãi ròng", "doanh thu", "10-q", "10-k", "earnings", "revenue", "q1", "q2", "q3", "q4")):
        category = "BCTC_EARNINGS"
    elif any(k in txt for k in ("vi phạm", "cảnh báo", "ngoại trừ", "đình chỉ", "giải trình", "phạt", "khởi tố", "cắt margin", "thua lỗ", "lỗ ròng", "chậm nộp")):
        category = "RISK_WARNING"
    elif any(k in txt for k in ("cổ tức", "chia thưởng", "esop", "tăng vốn", "phát hành thêm", "chào bán", "đkcc", "dividend", "buyback")):
        category = "DIVIDEND_ESOP"
    elif any(k in txt for k in ("nội bộ", "mua vào", "bán ra", "cổ đông lớn", "sáp nhập", "m&a", "thâu tóm", "form 4", "hđqt", "đhcđ")):
        category = "MA_INSIDER"

    pos_hits = sum(1 for w in POSITIVE_KW if w in txt)
    neg_hits = sum(1 for w in NEGATIVE_KW if w in txt)
    sent = max(-1.0, min(1.0, round((pos_hits - neg_hits) * 0.28, 2)))

    if category == "RISK_WARNING" or abs(sent) >= 0.5 or (category == "BCTC_EARNINGS" and symbols_found):
        urgency = "CRITICAL" if (category == "RISK_WARNING" or (symbols_found and category == "BCTC_EARNINGS")) else "HIGH"
    elif symbols_found or category in ("MACRO_SBV_FED", "MA_INSIDER", "DIVIDEND_ESOP"):
        urgency = "HIGH"
    else:
        urgency = "NORMAL"

    return category, urgency, sent


def _fetch_single_rss(source_name: str, url: str, market: str, sym_regex: re.Pattern, timeout: int = 6) -> Dict[str, Any]:
    items: List[Dict[str, Any]] = []
    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(url, headers=BROWSER_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx) as resp:
            raw_xml = resp.read()
        root = ET.fromstring(raw_xml)
        for node in root.findall(".//item")[:35]:
            title = _strip_html(node.findtext("title") or "")
            desc = _strip_html(node.findtext("description") or "")
            link = (node.findtext("link") or "").strip()
            pub_date = (node.findtext("pubDate") or "").strip()
            if not title:
                continue
            full = f"{title} {desc}"
            matched = sorted(set(m.upper() for m in sym_regex.findall(full)))
            # Lọc nhiễu US ticker 1-2 ký tự phổ thông trong tiếng Anh / tiếng Việt
            if market == "VN":
                matched = [m for m in matched if m not in ("V",)]
            else:
                matched = [m for m in matched if len(m) >= 2]
            cat, urg, sent = _classify_item(title, desc, matched, market)
            item_id = hashlib.sha1(f"{market}:{link or title}".encode("utf-8", errors="ignore")).hexdigest()[:16]
            items.append({
                "item_id": item_id,
                "market": market,
                "category": cat,
                "urgency": urg,
                "sentiment_score": sent,
                "tickers": matched,
                "sector": "",
                "title": title[:260],
                "summary": desc[:360],
                "source_name": source_name,
                "source_url": link,
                "published_at": pub_date,
            })
        return {"ok": True, "source": source_name, "items": items}
    except Exception as e:
        return {"ok": False, "source": source_name, "error": str(e), "items": []}


def _sync_items_and_profiles_to_sqlite(items: List[Dict[str, Any]], universe: Dict[str, Dict[str, Any]]) -> None:
    _ensure_omni_tables()
    now_iso = _get_ict_now().strftime("%Y-%m-%d %H:%M:%S")
    with _OMNI_LOCK:
        with _get_db_conn() as conn:
            for it in items:
                tickers_str = " ".join(it.get("tickers", []))
                tickers_json = json.dumps(it.get("tickers", []), ensure_ascii=False)
                cur = conn.execute(
                    "SELECT id FROM omni_intelligence_items WHERE item_id = ?",
                    (it["item_id"],),
                ).fetchone()
                if cur is None:
                    conn.execute(
                        """
                        INSERT INTO omni_intelligence_items (
                            item_id, market, category, urgency, sentiment_score,
                            tickers_json, tickers_text, sector, title, summary,
                            source_name, source_url, published_at, crawled_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            it["item_id"], it["market"], it["category"], it["urgency"],
                            float(it.get("sentiment_score", 0.0)), tickers_json, tickers_str,
                            it.get("sector", ""), it["title"], it.get("summary", ""),
                            it.get("source_name", ""), it.get("source_url", ""),
                            it.get("published_at", ""), now_iso,
                        ),
                    )
                    conn.execute(
                        """
                        INSERT INTO omni_intelligence_fts (
                            item_id, title, summary, tickers_text, category, sector, source_name
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            it["item_id"], it["title"], it.get("summary", ""),
                            tickers_str, it["category"], it.get("sector", ""), it.get("source_name", ""),
                        ),
                    )
                else:
                    conn.execute(
                        """
                        UPDATE omni_intelligence_items
                        SET category=?, urgency=?, sentiment_score=?, tickers_json=?, tickers_text=?, crawled_at=?
                        WHERE item_id=?
                        """,
                        (
                            it["category"], it["urgency"], float(it.get("sentiment_score", 0.0)),
                            tickers_json, tickers_str, now_iso, it["item_id"],
                        ),
                    )

            for sym, prof in universe.items():
                conn.execute(
                    """
                    INSERT INTO omni_ticker_profiles (
                        symbol, market, company_name, sector_name, live_price, change_pct,
                        pe, pb, roe, ocf_ratio, profile_json, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(symbol) DO UPDATE SET
                        company_name=excluded.company_name,
                        sector_name=excluded.sector_name,
                        live_price=CASE WHEN excluded.live_price > 0 THEN excluded.live_price ELSE omni_ticker_profiles.live_price END,
                        change_pct=CASE WHEN excluded.live_price > 0 THEN excluded.change_pct ELSE omni_ticker_profiles.change_pct END,
                        pe=excluded.pe,
                        pb=excluded.pb,
                        roe=excluded.roe,
                        ocf_ratio=excluded.ocf_ratio,
                        profile_json=excluded.profile_json,
                        updated_at=excluded.updated_at
                    """,
                    (
                        sym, prof.get("market", "VN"), prof.get("company_name", sym),
                        prof.get("sector_name", ""), float(prof.get("live_price", 0.0) or 0.0),
                        float(prof.get("change_1d_pct", 0.0) or 0.0),
                        float(prof.get("pe", 0.0) or 0.0), float(prof.get("pb", 0.0) or 0.0),
                        float(prof.get("roe", 0.0) or 0.0), float(prof.get("ocf_ratio", 0.0) or 0.0),
                        json.dumps(prof, ensure_ascii=False), now_iso,
                    ),
                )
            conn.commit()


def _parse_pct_token(val: str) -> Optional[float]:
    try:
        num = float(val.replace(",", ".").strip())
        if -95.0 <= num <= 500.0:
            return round(num, 2)
    except Exception:
        pass
    return None


def refresh_live_quarterly_bctc_metrics(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    V6.0 Nâng cấp 1: Tự động bóc tách con số BCTC/KQKD/Cổ tức mới nhất từ luồng tin đã cào
    và lưu vào `data/live_bctc_quarterly_updates.json` để làm giàu hồ sơ doanh nghiệp.
    """
    global _UNIVERSE_CACHE
    now_ict = _get_ict_now()
    existing = _load_json_safe(LIVE_BCTC_UPDATES_JSON)
    ticker_updates: Dict[str, Any] = dict(existing.get("ticker_updates", {})) if isinstance(existing.get("ticker_updates"), dict) else {}

    p_pos_prof = re.compile(
        r"(?:lợi nhuận(?:\s+(?:sau\s+thuế|trước\s+thuế|ròng))?|lãi(?:\s+(?:ròng|sau\s+thuế|trước\s+thuế))?|LNST|LNTT)"
        r"(?:\s+(?:quý\s+\d|Q\d|năm\s+\d+|cả\s+năm|lũy\s+kế|[\w\s]{0,18}))?\s*(?:tăng|bứt\s+phá|tăng\s+trưởng|vọt|\+)\s*([0-9]+(?:[.,][0-9]+)?)\s*%",
        re.IGNORECASE,
    )
    p_neg_prof = re.compile(
        r"(?:lợi nhuận(?:\s+(?:sau\s+thuế|trước\s+thuế|ròng))?|lãi(?:\s+(?:ròng|sau\s+thuế|trước\s+thuế))?|LNST|LNTT)"
        r"(?:\s+[\w\s]{0,18})?\s*(?:giảm|sụt\s+giảm|bốc\s+hơi|đi\s+lùi|-)\s*([0-9]+(?:[.,][0-9]+)?)\s*%",
        re.IGNORECASE,
    )
    p_rev = re.compile(
        r"(?:doanh\s+thu(?:\s+thuần)?)\s*(?:[\w\s]{0,18})?(tăng|tăng\s+trưởng|giảm|sụt|\+|-)\s*([0-9]+(?:[.,][0-9]+)?)\s*%",
        re.IGNORECASE,
    )
    p_en_prof = re.compile(
        r"(?:net\s+income|earnings|profit|eps)\s+(?:rose|grew|jumped|surged|up|\+|fell|dropped|down)\s*([+-]?[0-9]+(?:[.,][0-9]+)?)\s*%",
        re.IGNORECASE,
    )
    p_roe = re.compile(r"\bROE\s*(?:đạt|lên|ở\s+mức|:|=|~)?\s*([0-9]+(?:[.,][0-9]+)?)\s*%", re.IGNORECASE)
    p_div = re.compile(
        r"(?:cổ\s+tức(?:\s+tiền\s+mặt|\s+cổ\s+phiếu)?|tỷ\s+lệ\s+thực\s+hiện)\s*(?:tổng\s+cộng|năm\s+\d+|:)?\s*([0-9]+(?:[.,][0-9]+)?)\s*%",
        re.IGNORECASE,
    )

    newly_updated = 0
    for it in items:
        tickers = [str(t).upper().strip() for t in (it.get("tickers") or []) if t]
        if not tickers:
            continue
        cat = str(it.get("category", ""))
        text = f"{it.get('title', '')}. {it.get('summary', '')}"
        low = text.lower()
        if cat not in ("BCTC_EARNINGS", "DIVIDEND_ESOP", "AGM_RESOLUTION", "ANALYST_REPORT") and not any(
            k in low for k in ("lợi nhuận", "doanh thu", "bctc", "kết quả kinh doanh", "cổ tức", "roe", "earnings", "revenue")
        ):
            continue

        patch_fields: Dict[str, Any] = {}
        m_pp = p_pos_prof.search(text)
        m_np = p_neg_prof.search(text)
        if m_pp:
            v = _parse_pct_token(m_pp.group(1))
            if v is not None:
                patch_fields["profit_growth_yoy"] = v
        elif m_np:
            v = _parse_pct_token(m_np.group(1))
            if v is not None:
                patch_fields["profit_growth_yoy"] = -abs(v)
        else:
            m_ep = p_en_prof.search(text)
            if m_ep:
                v = _parse_pct_token(m_ep.group(1))
                if v is not None:
                    if any(w in m_ep.group(0).lower() for w in ("fell", "dropped", "down")):
                        v = -abs(v)
                    patch_fields["profit_growth_yoy"] = v

        m_rv = p_rev.search(text)
        if m_rv:
            v = _parse_pct_token(m_rv.group(2))
            if v is not None:
                if any(w in m_rv.group(1).lower() for w in ("giảm", "sụt", "-")):
                    v = -abs(v)
                patch_fields["rev_growth_yoy"] = v

        m_roe = p_roe.search(text)
        if m_roe:
            v = _parse_pct_token(m_roe.group(1))
            if v is not None and 0.0 <= v <= 150.0:
                patch_fields["roe"] = v

        m_div = p_div.search(text)
        if m_div:
            v = _parse_pct_token(m_div.group(1))
            if v is not None and 0.0 <= v <= 200.0:
                patch_fields["dividend_pct"] = v

        for sym in tickers[:3]:
            prev = dict(ticker_updates.get(sym, {}))
            prev.update(patch_fields)
            prev.update({
                "symbol": sym,
                "category": cat,
                "headline": str(it.get("title", ""))[:180],
                "source_name": str(it.get("source_name", "")),
                "source_url": str(it.get("source_url", "")),
                "published_at": str(it.get("published_at", "")),
                "updated_at": now_ict.strftime("%Y-%m-%d %H:%M:%S"),
            })
            if sym not in ticker_updates or patch_fields:
                newly_updated += 1
            ticker_updates[sym] = prev

    payload = {
        "updated_at": now_ict.strftime("%Y-%m-%d %H:%M:%S"),
        "total_tickers_updated": len(ticker_updates),
        "newly_parsed_in_cycle": newly_updated,
        "ticker_updates": ticker_updates,
    }
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LIVE_BCTC_UPDATES_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    _UNIVERSE_CACHE = None
    return payload


def evaluate_high_impact_catalyst_alerts(
    items: List[Dict[str, Any]],
    universe: Dict[str, Dict[str, Any]],
    send_telegram: bool = False,
) -> Dict[str, Any]:
    """
    V6.0 Nâng cấp 5: Phát hiện tức thời Catalyst / Cảnh báo rủi ro tác động trực tiếp tới
    danh mục nắm giữ (SSOT) & Top Alpha Picks, ước lượng biên độ ảnh hưởng Giá Nội Tại (MOS%).
    """
    now_ict = _get_ict_now()
    ssot = _load_json_safe(DATA_DIR / "current_portfolio_state.json")
    active_pos = ssot.get("active_positions", {}) if isinstance(ssot.get("active_positions"), dict) else {}
    held_syms = {k.upper().strip() for k, v in active_pos.items() if int(v.get("shares", 0) or 0) > 0}

    deep_brain = _load_json_safe(DATA_DIR / "deep_financial_brain_analysis.json")
    fv_mos_map: Dict[str, Dict[str, Any]] = {}
    alpha_syms = {"BAF", "DBC", "HAH", "TCB", "CTG", "MBB", "HPG", "OCB", "FPT", "NVDA", "META", "AVGO", "MSFT", "LLY"}
    for pick in (deep_brain.get("top_vn_alpha_picks", []) + deep_brain.get("top_us_alpha_picks", [])):
        s = str(pick.get("symbol", "")).upper().strip()
        if s:
            alpha_syms.add(s)
            val = pick.get("valuation", {})
            fv_mos_map[s] = {
                "fair_value": float(val.get("intrinsic_fair_value", 0.0) or 0.0),
                "mos_pct": float(val.get("margin_of_safety_pct", 0.0) or 0.0),
            }

    watch_syms = held_syms | alpha_syms
    alerts: List[Dict[str, Any]] = []
    seen_pairs = set()

    for it in items:
        cat = str(it.get("category", "MARKET_GENERAL"))
        sent = float(it.get("sentiment_score", 0.0) or 0.0)
        urg = str(it.get("urgency", "NORMAL"))
        tickers = [str(t).upper().strip() for t in (it.get("tickers") or []) if str(t).upper().strip() in watch_syms]
        if not tickers:
            continue
        if cat not in ("BCTC_EARNINGS", "RISK_WARNING", "MA_INSIDER", "DIVIDEND_ESOP", "AGM_RESOLUTION") and abs(sent) < 0.25:
            continue

        for sym in tickers:
            pair_key = f"{sym}:{it.get('item_id', '')}"
            if pair_key in seen_pairs:
                continue
            seen_pairs.add(pair_key)

            is_held = sym in held_syms
            is_risk = (cat == "RISK_WARNING") or (sent <= -0.25)
            if is_risk:
                fv_impact = -6.5 if urg == "CRITICAL" else -4.5
                priority = "CRITICAL_RISK" if is_held else "RISK_WATCH"
                rec_action = "REVIEW_STOP_2XATR" if is_held else "AVOID_OR_WAIT_CLARITY"
            else:
                fv_impact = 4.0 if cat == "BCTC_EARNINGS" and sent >= 0.25 else (2.5 if sent > 0 else 1.0)
                priority = "HIGH_PRIORITY_HOLDING" if is_held else "ALPHA_CATALYST"
                rec_action = "HOLD_AND_MONITOR" if is_held else "READY_GOLDEN_HOUR_14H00"

            mos_info = fv_mos_map.get(sym, {})
            cur_mos = float(mos_info.get("mos_pct", 0.0) or 0.0)
            adj_mos = round(cur_mos + fv_impact, 1)
            prof = universe.get(sym, {})

            alerts.append({
                "alert_id": hashlib.sha1(pair_key.encode("utf-8")).hexdigest()[:12],
                "item_id": str(it.get("item_id", "")),
                "symbol": sym,
                "market": prof.get("market", "VN"),
                "is_holding": is_held,
                "priority": priority,
                "category": cat,
                "sentiment_score": sent,
                "estimated_fair_value_impact_pct": fv_impact,
                "current_mos_pct": cur_mos,
                "adjusted_mos_pct": adj_mos,
                "recommended_action": rec_action,
                "title": str(it.get("title", "")),
                "source_name": str(it.get("source_name", "")),
                "source_url": str(it.get("source_url", "")),
                "published_at": str(it.get("published_at", "")),
                "detected_at": now_ict.strftime("%Y-%m-%d %H:%M:%S"),
            })

    prio_rank = {"CRITICAL_RISK": 0, "HIGH_PRIORITY_HOLDING": 1, "RISK_WATCH": 2, "ALPHA_CATALYST": 3}
    alerts.sort(key=lambda x: (prio_rank.get(x["priority"], 9), -abs(float(x.get("sentiment_score", 0.0)))))

    holding_count = sum(1 for a in alerts if a["is_holding"])
    risk_count = sum(1 for a in alerts if a["priority"] in ("CRITICAL_RISK", "RISK_WATCH"))

    if send_telegram and alerts:
        sent_state = _load_json_safe(LIVE_CATALYST_SENT_JSON)
        sent_ids = set(sent_state.get("sent_alert_ids", []))
        new_crit = [a for a in alerts if a["priority"] == "CRITICAL_RISK" and a["alert_id"] not in sent_ids]
        if new_crit:
            try:
                from scripts.telegram_notifier import send_telegram_message
                lines = ["⚠️ <b>[APEX CATALYST & RISK SENTINEL]</b>"]
                for a in new_crit[:3]:
                    lines.append(
                        f"• <b>{a['symbol']}</b> [{a['category']}] Tác động FV: {a['estimated_fair_value_impact_pct']:+.1f}% "
                        f"➔ <b>{a['recommended_action']}</b>\n  <i>{a['title'][:120]}</i>"
                    )
                    sent_ids.add(a["alert_id"])
                send_telegram_message("\n".join(lines))
                LIVE_CATALYST_SENT_JSON.write_text(
                    json.dumps({"sent_alert_ids": sorted(list(sent_ids))[-300:], "updated_at": now_ict.strftime("%Y-%m-%d %H:%M:%S")}, indent=2),
                    encoding="utf-8",
                )
            except Exception:
                pass

    payload = {
        "updated_at": now_ict.strftime("%Y-%m-%d %H:%M:%S"),
        "held_symbols": sorted(list(held_syms)),
        "total_alerts": len(alerts),
        "holding_alerts_count": holding_count,
        "risk_alerts_count": risk_count,
        "alerts": alerts[:40],
    }
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LIVE_CATALYST_ALERTS_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def crawl_realtime_market_intelligence(force_refresh: bool = False, cache_ttl: int = 300) -> Dict[str, Any]:
    """Lớp 1: Quét song song tin tức + BCTC + CBTT + SEC EDGAR toàn thị trường và lưu Vault."""
    now_ict = _get_ict_now()
    if not force_refresh and OMNI_OUTPUT_JSON.exists():
        try:
            age = time.time() - OMNI_OUTPUT_JSON.stat().st_mtime
            if age <= cache_ttl:
                cached = json.loads(OMNI_OUTPUT_JSON.read_text(encoding="utf-8"))
                if cached.get("items") is not None:
                    return cached
        except Exception:
            pass

    universe = _load_master_universe()
    vn_syms = sorted([s for s, v in universe.items() if v.get("market") == "VN"], key=len, reverse=True)
    us_syms = sorted([s for s, v in universe.items() if v.get("market") == "US"], key=len, reverse=True)

    vn_regex = re.compile(r"\b(" + "|".join(re.escape(s) for s in vn_syms) + r")\b") if vn_syms else re.compile(r"(?!x)x")
    us_regex = re.compile(r"\b(" + "|".join(re.escape(s) for s in us_syms) + r")\b") if us_syms else re.compile(r"(?!x)x")

    # Kéo giá sống VPS cho các mã trọng điểm (SSOT + Watchlist + VN30 Top)
    priority_vn = ["HDB", "MSH", "BAF", "IDC", "TCH", "OCB", "FPT", "TCB", "MBB", "VCB", "HPG", "SSI", "MWG", "VNM", "DGC"]
    try:
        from scripts.vietnam_realtime_feed import fetch_vps_quotes
        quotes = fetch_vps_quotes(priority_vn, timeout=4)
        for s, q in quotes.items():
            px = float(q.get("price") or q.get("last_price") or 0.0)
            if s in universe and px > 0:
                universe[s]["live_price"] = px
                universe[s]["ref_price"] = float(q.get("ref_price", 0.0) or 0.0)
                universe[s]["change_1d_pct"] = float(q.get("change_pct", 0.0) or 0.0)
                universe[s]["volume"] = int(q.get("volume", 0) or 0)
                universe[s]["buy_up_pct"] = float(q.get("active_buy_pct", 50.0) or 50.0)
                universe[s]["foreign_net_val_bil"] = round(float(q.get("foreign_net_val_vnd", 0.0) or 0.0) / 1e9, 2)
    except Exception:
        pass

    all_sources = [(n, u, m, vn_regex if m == "VN" else us_regex) for n, u, m in (VN_RSS_SOURCES + US_RSS_SOURCES)]
    collected: List[Dict[str, Any]] = []
    source_health: List[Dict[str, Any]] = []
    seen_ids = set()

    with ThreadPoolExecutor(max_workers=10) as pool:
        futs = {pool.submit(_fetch_single_rss, n, u, m, rx, 6): (n, m) for n, u, m, rx in all_sources}
        for fut in as_completed(futs):
            src_name, mkt = futs[fut]
            try:
                res = fut.result()
                source_health.append({
                    "source": src_name, "market": mkt,
                    "ok": bool(res.get("ok")), "count": len(res.get("items", [])),
                    "error": res.get("error", ""),
                })
                for it in res.get("items", []):
                    if it["item_id"] not in seen_ids:
                        seen_ids.add(it["item_id"])
                        if it.get("tickers"):
                            first = it["tickers"][0]
                            it["sector"] = universe.get(first, {}).get("sector_name", "")
                        collected.append(it)
            except Exception as e:
                source_health.append({"source": src_name, "market": mkt, "ok": False, "count": 0, "error": str(e)})

    # Gộp thêm dữ liệu SEC EDGAR & CBTT từ cbtt_live_radar.json nếu có
    radar = _load_json_safe(CBTT_RADAR_JSON)
    for uf in radar.get("us_filings", [])[:40]:
        sym = str(uf.get("symbol", "")).upper()
        title = f"[SEC {uf.get('form', '8-K')} — {sym}] {uf.get('description', '')}"
        iid = hashlib.sha1(f"SEC:{sym}:{uf.get('form')}:{uf.get('filing_date')}".encode("utf-8")).hexdigest()[:16]
        if iid not in seen_ids:
            seen_ids.add(iid)
            collected.append({
                "item_id": iid,
                "market": "US",
                "category": "BCTC_EARNINGS" if uf.get("form") in ("10-Q", "10-K") else "MA_INSIDER",
                "urgency": "CRITICAL" if uf.get("severity") == "CRITICAL" else "HIGH",
                "sentiment_score": 0.0,
                "tickers": [sym] if sym else [],
                "sector": universe.get(sym, {}).get("sector_name", ""),
                "title": title[:260],
                "summary": f"Hồ sơ SEC EDGAR Form {uf.get('form', '')} nộp ngày {uf.get('filing_date', '')}.",
                "source_name": "SEC EDGAR Official",
                "source_url": uf.get("sec_url", ""),
                "published_at": uf.get("filing_date", ""),
            })
    for vf in radar.get("vn_announcements", [])[:40]:
        title = str(vf.get("title", "")).strip()
        if not title:
            continue
        iid = hashlib.sha1(f"CBTT:{vf.get('source_url') or title}".encode("utf-8")).hexdigest()[:16]
        if iid not in seen_ids:
            seen_ids.add(iid)
            syms = [str(s).upper() for s in vf.get("symbols", [])]
            cat, urg, sent = _classify_item(title, vf.get("summary", ""), syms, "VN")
            collected.append({
                "item_id": iid,
                "market": "VN",
                "category": cat,
                "urgency": urg,
                "sentiment_score": sent,
                "tickers": syms,
                "sector": universe.get(syms[0], {}).get("sector_name", "") if syms else "",
                "title": title[:260],
                "summary": str(vf.get("summary", ""))[:360],
                "source_name": "Vietnam CBTT Radar",
                "source_url": vf.get("source_url", ""),
                "published_at": vf.get("published_at", ""),
            })

    urg_rank = {"CRITICAL": 0, "HIGH": 1, "NORMAL": 2}
    collected.sort(key=lambda x: (urg_rank.get(x.get("urgency", "NORMAL"), 2), -len(x.get("tickers", []))))

    # V6.0: Tự động bóc tách BCTC quý mới + phát hiện Catalyst/Risk Alerts trước khi đồng bộ Vault
    bctc_patch_res = refresh_live_quarterly_bctc_metrics(collected)
    universe = _load_master_universe()
    catalyst_res = evaluate_high_impact_catalyst_alerts(collected, universe, send_telegram=False)

    # Đồng bộ lên SQLite FTS5 & lưu file snapshot
    _sync_items_and_profiles_to_sqlite(collected, universe)

    cat_counts: Dict[str, int] = {}
    for it in collected:
        c = it.get("category", "MARKET_GENERAL")
        cat_counts[c] = cat_counts.get(c, 0) + 1

    ok_sources = sum(1 for s in source_health if s.get("ok"))
    payload = {
        "crawled_at": now_ict.strftime("%Y-%m-%d %H:%M:%S"),
        "universe_counts": {"vn": len(vn_syms), "us": len(us_syms), "total": len(universe)},
        "total_items": len(collected),
        "category_counts": cat_counts,
        "live_bctc_updates_count": bctc_patch_res.get("total_tickers_updated", 0),
        "catalyst_alerts_count": catalyst_res.get("total_alerts", 0),
        "holding_alerts_count": catalyst_res.get("holding_alerts_count", 0),
        "sources_online": f"{ok_sources}/{len(source_health)}",
        "source_health": source_health,
        "items": collected[:150],
    }
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OMNI_OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def _fetch_entrade_ohlcv_stats(symbol: str, timeout: int = 5) -> Dict[str, Any]:
    """Lấy chuỗi OHLCV 1 năm từ Entrade DNSE để tính High/Low 52W, MA20, MA50 và RS 3M."""
    try:
        to_ts = int(time.time())
        from_ts = to_ts - 365 * 86400
        url = (
            f"https://services.entrade.com.vn/chart-api/v2/ohlcs/stock"
            f"?resolution=D&symbol={urllib.parse.quote(symbol)}&from={from_ts}&to={to_ts}"
        )
        req = urllib.request.Request(url, headers=BROWSER_HEADERS)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        closes = [float(x) * 1000.0 for x in (data.get("c") or []) if x]
        highs = [float(x) * 1000.0 for x in (data.get("h") or []) if x]
        lows = [float(x) * 1000.0 for x in (data.get("l") or []) if x]
        vols = [float(x) for x in (data.get("v") or [])]
        if len(closes) < 20:
            return {}
        last_c = closes[-1]
        ma20 = sum(closes[-20:]) / 20.0
        ma50 = sum(closes[-50:]) / 50.0 if len(closes) >= 50 else ma20
        ma200 = sum(closes[-200:]) / 200.0 if len(closes) >= 200 else ma50
        ret_3m = ((last_c / closes[-63]) - 1.0) * 100.0 if len(closes) >= 63 and closes[-63] > 0 else 0.0
        ret_1y = ((last_c / closes[0]) - 1.0) * 100.0 if closes[0] > 0 else 0.0
        avg_v20 = sum(vols[-20:]) / 20.0 if len(vols) >= 20 else 0.0
        return {
            "ohlcv_days": len(closes),
            "high_52w": round(max(highs) if highs else last_c, 0),
            "low_52w": round(min(lows) if lows else last_c, 0),
            "ma20": round(ma20, 0),
            "ma50": round(ma50, 0),
            "ma200": round(ma200, 0),
            "return_3m_pct": round(ret_3m, 2),
            "return_1y_pct": round(ret_1y, 2),
            "avg_vol_20d": int(avg_v20),
        }
    except Exception:
        return {}


def fetch_live_ticker_financial_profile(symbol: str, fetch_ohlcv: bool = True) -> Dict[str, Any]:
    """Lớp 2: Lấy hồ sơ BCTC + định giá + giá sống chi tiết cho bất kỳ mã VN hoặc US."""
    sym = symbol.upper().strip().replace(".VN", "")
    universe = _load_master_universe()
    prof = dict(universe.get(sym, {
        "symbol": sym,
        "market": "US" if len(sym) >= 4 or "-" in sym else "VN",
        "company_name": sym,
        "exchange": "HOSE/HNX",
        "sector_name": "Chưa phân nhóm",
        "accounting_regime": "CORPORATE_VAS_TT200",
    }))

    if prof.get("market") == "VN":
        try:
            from scripts.vietnam_realtime_feed import fetch_vps_quotes, fetch_stock_indicators_live
            quotes = fetch_vps_quotes([sym], timeout=4)
            q = quotes.get(sym)
            if q:
                px = float(q.get("price") or q.get("last_price") or 0.0)
                if px > 0:
                    prof["live_price"] = px
                    prof["ref_price"] = float(q.get("ref_price", 0.0) or 0.0)
                    prof["change_1d_pct"] = float(q.get("change_pct", 0.0) or 0.0)
                    prof["volume"] = int(q.get("volume", 0) or 0)
                    prof["buy_up_pct"] = float(q.get("active_buy_pct", 50.0) or 50.0)
                    prof["foreign_net_val_bil"] = round(float(q.get("foreign_net_val_vnd", 0.0) or 0.0) / 1e9, 2)
            if fetch_ohlcv:
                ind = fetch_stock_indicators_live(sym)
                if ind:
                    prof["rsi14"] = float(ind.get("rsi14", 50.0) or 50.0)
                    prof["ma20"] = float(ind.get("ma20", 0.0) or 0.0)
                    prof["ma50"] = float(ind.get("ma50", 0.0) or 0.0)
                    prof["atr14"] = float(ind.get("atr14", 0.0) or 0.0)
                    prof["high_6m"] = float(ind.get("hi_6m", 0.0) or 0.0)
                    prof["low_6m"] = float(ind.get("lo_6m", 0.0) or 0.0)
                    prof["avg_vol_20d"] = int(ind.get("avg_vol_20d", 0) or 0)
                    if not prof.get("live_price") and float(ind.get("last_close", 0.0) or 0.0) > 0:
                        prof["live_price"] = float(ind["last_close"])
        except Exception:
            pass
    else:
        us_snap = _load_json_safe(US_SNAPSHOT_JSON)
        for item in us_snap.get("broad_equities", []):
            if str(item.get("symbol", "")).upper() == sym:
                prof.update(_extract_us_snap_fields(item))
                break

    prof["profile_fetched_at"] = _get_ict_now().strftime("%Y-%m-%d %H:%M:%S")
    return prof


def _sanitize_fts_query(raw_q: str) -> str:
    cleaned = re.sub(r"[^0-9A-Za-zÀ-ỹà-ỹ_\s]", " ", raw_q or "").strip()
    tokens = [t for t in cleaned.split() if t]
    if not tokens:
        return ""
    return " OR ".join(f'"{t}"' for t in tokens[:8])


def search_market_intelligence(
    query: str = "",
    category: Optional[str] = None,
    limit: int = 25,
) -> Dict[str, Any]:
    """Lớp 3: Tìm kiếm siêu tốc trên SQLite FTS5 + B-Tree cho cổ phiếu, BCTC, tin tức & báo cáo nội bộ."""
    _ensure_omni_tables()
    universe = _load_master_universe()

    # Tự động nạp hồ sơ cổ phiếu nếu bảng profile trống
    with _get_db_conn() as conn:
        prof_cnt = conn.execute("SELECT COUNT(*) FROM omni_ticker_profiles").fetchone()[0]
        item_cnt = conn.execute("SELECT COUNT(*) FROM omni_intelligence_items").fetchone()[0]

    if prof_cnt == 0:
        seed_items = _load_json_safe(OMNI_OUTPUT_JSON).get("items", [])
        _sync_items_and_profiles_to_sqlite(seed_items, universe)
    elif item_cnt == 0 and OMNI_OUTPUT_JSON.exists():
        seed_items = _load_json_safe(OMNI_OUTPUT_JSON).get("items", [])
        if seed_items:
            _sync_items_and_profiles_to_sqlite(seed_items, {})

    q = (query or "").strip()
    q_up = q.upper()
    q_low = q.lower()

    # 1. Tìm kiếm mã cổ phiếu / ngành / chỉ tiêu BCTC trong vũ trụ 144 VN + 35 US
    matched_tickers: List[Dict[str, Any]] = []
    tokens_low = [t for t in re.split(r"[\s,;/]+", q_low) if t]

    if q_up in universe:
        matched_tickers.append(fetch_live_ticker_financial_profile(q_up, fetch_ohlcv=True))

    for sym, info in universe.items():
        if sym == q_up:
            continue
        blob = " ".join([
            sym,
            str(info.get("company_name", "")),
            str(info.get("sector_name", "")),
            str(info.get("catalyst", "")),
            str(info.get("accounting_regime", "")),
        ]).lower()
        if not q or sym.lower() == q_low or (tokens_low and all(t in blob for t in tokens_low)):
            matched_tickers.append(dict(info))
        if len(matched_tickers) >= limit:
            break

    # Nếu không khớp toàn bộ token thì thử khớp bất kỳ token nào
    if q and not matched_tickers:
        for sym, info in universe.items():
            blob = f"{sym} {info.get('company_name','')} {info.get('sector_name','')} {info.get('catalyst','')}".lower()
            if any(t in blob for t in tokens_low):
                matched_tickers.append(dict(info))
            if len(matched_tickers) >= limit:
                break

    # Làm giàu giá sống VPS cho top 6 mã VN tìm thấy (nhanh qua 1 batch call)
    vn_enrich = [m["symbol"] for m in matched_tickers[:6] if m.get("market") == "VN" and not m.get("live_price")]
    if vn_enrich:
        try:
            from scripts.vietnam_realtime_feed import fetch_vps_quotes
            live_q = fetch_vps_quotes(vn_enrich, timeout=3)
            for m in matched_tickers:
                s = m["symbol"]
                if s in live_q:
                    px = float(live_q[s].get("price") or live_q[s].get("last_price") or 0.0)
                    if px > 0:
                        m["live_price"] = px
                        m["change_1d_pct"] = float(live_q[s].get("change_pct", 0.0) or 0.0)
                        m["buy_up_pct"] = float(live_q[s].get("active_buy_pct", 50.0) or 50.0)
                        m["volume"] = int(live_q[s].get("volume", 0) or 0)
        except Exception:
            pass

    # 2. Tìm tin tức & CBTT trên FTS5 (hoặc LIKE fallback)
    matched_news: List[Dict[str, Any]] = []
    matched_reports: List[Dict[str, Any]] = []
    with _get_db_conn() as conn:
        fts_q = _sanitize_fts_query(q)
        cat_filter = (category or "").strip().upper()

        if fts_q:
            try:
                sql = """
                    SELECT i.item_id, i.market, i.category, i.urgency, i.sentiment_score,
                           i.tickers_json, i.sector, i.title, i.summary, i.source_name, i.source_url, i.published_at
                    FROM omni_intelligence_fts f
                    JOIN omni_intelligence_items i ON i.item_id = f.item_id
                    WHERE omni_intelligence_fts MATCH ?
                """
                params: List[Any] = [fts_q]
                if cat_filter and cat_filter != "ALL":
                    sql += " AND i.category = ?"
                    params.append(cat_filter)
                sql += " ORDER BY i.crawled_at DESC LIMIT ?"
                params.append(limit)
                rows = conn.execute(sql, params).fetchall()
            except Exception:
                like_pat = f"%{q}%"
                sql = """
                    SELECT item_id, market, category, urgency, sentiment_score,
                           tickers_json, sector, title, summary, source_name, source_url, published_at
                    FROM omni_intelligence_items
                    WHERE (title LIKE ? OR summary LIKE ? OR tickers_text LIKE ?)
                """
                params = [like_pat, like_pat, like_pat]
                if cat_filter and cat_filter != "ALL":
                    sql += " AND category = ?"
                    params.append(cat_filter)
                sql += " ORDER BY crawled_at DESC LIMIT ?"
                params.append(limit)
                rows = conn.execute(sql, params).fetchall()
        else:
            sql = """
                SELECT item_id, market, category, urgency, sentiment_score,
                       tickers_json, sector, title, summary, source_name, source_url, published_at
                FROM omni_intelligence_items
            """
            params = []
            if cat_filter and cat_filter != "ALL":
                sql += " WHERE category = ?"
                params.append(cat_filter)
            sql += " ORDER BY CASE urgency WHEN 'CRITICAL' THEN 0 WHEN 'HIGH' THEN 1 ELSE 2 END, crawled_at DESC LIMIT ?"
            params.append(limit)
            rows = conn.execute(sql, params).fetchall()

        for r in rows:
            try:
                tks = json.loads(r["tickers_json"] or "[]")
            except Exception:
                tks = []
            matched_news.append({
                "item_id": r["item_id"],
                "market": r["market"],
                "category": r["category"],
                "urgency": r["urgency"],
                "sentiment_score": r["sentiment_score"],
                "tickers": tks,
                "sector": r["sector"],
                "title": r["title"],
                "summary": r["summary"],
                "source_name": r["source_name"],
                "source_url": r["source_url"],
                "published_at": r["published_at"],
            })

        # 3. Tìm báo cáo nội bộ tương ứng trong institutional_reports
        try:
            if fts_q:
                rep_rows = conn.execute(
                    """
                    SELECT r.rel_path, r.title, r.dept_name, r.date, r.preview, r.tickers
                    FROM reports_fts f
                    JOIN institutional_reports r ON r.id = f.rowid
                    WHERE reports_fts MATCH ?
                    ORDER BY r.date DESC, r.sort_time DESC
                    LIMIT 10
                    """,
                    (fts_q,),
                ).fetchall()
            else:
                rep_rows = conn.execute(
                    """
                    SELECT rel_path, title, dept_name, date, preview, tickers
                    FROM institutional_reports
                    ORDER BY date DESC, sort_time DESC
                    LIMIT 8
                    """
                ).fetchall()
            for rr in rep_rows:
                matched_reports.append({
                    "rel_path": rr["rel_path"],
                    "title": rr["title"],
                    "dept_name": rr["dept_name"],
                    "date": rr["date"],
                    "preview": (rr["preview"] or "")[:200],
                    "tickers": rr["tickers"] or "",
                })
        except Exception:
            pass

        total_news_db = conn.execute("SELECT COUNT(*) FROM omni_intelligence_items").fetchone()[0]
        total_prof_db = conn.execute("SELECT COUNT(*) FROM omni_ticker_profiles").fetchone()[0]

    snap_meta = _load_json_safe(OMNI_OUTPUT_JSON)
    return {
        "ok": True,
        "query": q,
        "category": category or "ALL",
        "matched_tickers": matched_tickers[:limit],
        "matched_news_and_filings": matched_news[:limit],
        "matched_reports": matched_reports,
        "summary_stats": {
            "total_universe_tickers": len(universe),
            "vn_universe_count": sum(1 for v in universe.values() if v.get("market") == "VN"),
            "us_universe_count": sum(1 for v in universe.values() if v.get("market") == "US"),
            "indexed_profiles_db": total_prof_db,
            "indexed_news_db": total_news_db,
            "last_crawled_at": snap_meta.get("crawled_at", "Chưa cào"),
            "sources_online": snap_meta.get("sources_online", "N/A"),
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Apex Omni-Market Intelligence Crawler & Search Engine V5.0")
    parser.add_argument("--crawl", action="store_true", help="Cào mới toàn bộ RSS/CBTT/SEC và cập nhật FTS5")
    parser.add_argument("--query", type=str, default="", help="Truy vấn tìm kiếm cổ phiếu/tin tức/BCTC")
    parser.add_argument("--symbol", type=str, default="", help="Lấy hồ sơ tài chính live cho 1 mã cụ thể")
    args = parser.parse_args()

    if args.crawl or (not args.query and not args.symbol):
        res = crawl_realtime_market_intelligence(force_refresh=True)
        print(
            f"[OMNI CRAWLER] Universe: {res['universe_counts']} | Items: {res['total_items']} | "
            f"Sources online: {res['sources_online']} | Categories: {res['category_counts']}"
        )

    if args.symbol:
        prof = fetch_live_ticker_financial_profile(args.symbol)
        print(f"\n[LIVE FINANCIAL PROFILE: {args.symbol.upper()}]")
        print(json.dumps(prof, ensure_ascii=False, indent=2))

    if args.query:
        s_res = search_market_intelligence(args.query, limit=10)
        print(
            f"\n[SEARCH '{args.query}'] Tickers={len(s_res['matched_tickers'])}, "
            f"News/CBTT={len(s_res['matched_news_and_filings'])}, Reports={len(s_res['matched_reports'])}"
        )
        for tk in s_res["matched_tickers"][:3]:
            print(
                f"  - {tk['symbol']} ({tk.get('company_name','')}) | Giá: {tk.get('live_price',0):,.0f} | "
                f"P/E: {tk.get('pe',0)} | ROE: {tk.get('roe',0)}% | OCF/LNST: {tk.get('ocf_ratio',0)}x"
            )
        for nw in s_res["matched_news_and_filings"][:5]:
            print(f"  * [{nw['category']}] {nw['title']} ({nw['source_name']})")


if __name__ == "__main__":
    main()
