#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APEX DAILY MULTI-SOURCE INTERNET, BCTC, CBTT & IR INTELLIGENCE CRAWLER (V3.0 — PHASE 1)
File: scripts/apex_daily_internet_intel_crawler.py
Cơ quan chủ quản: Ban 2 (Pháp y BCTC), Ban 10 (Hiền IR Scout), Ban 1 (Vĩ mô) & Master CIO James

Kiến trúc 5 Lớp Cào Dữ Liệu Sống Hàng Ngày (Zero Fabrication — 100% Real Sources):
1. Layer 1 — BCTC & EOD OHLCV Freshness Check:
   - Kiểm tra độ tươi dữ liệu Q3/2026 Vietcap IQ (80 mã VN), 2Y VPS OHLCV, SEC EDGAR XBRL (12 mã Mỹ).
   - Hỗ trợ `--refresh-bctc` để kéo mới toàn bộ BCTC + OHLCV khi cần.
2. Layer 2 — Live Corporate News & Official CBTT Disclosures (30 mã trọng điểm VN):
   - Vietcap AI News API (`ai.vietcap.com.vn/api/v2/news_info`) kèm Sentiment AI & summary.
   - CafeF Corporate News (`Type=1`) & Official CBTT / Events (`Type=2`).
3. Layer 3 — 13 Live Financial Press RSS Feeds (VN + Global):
   - CafeF (4 chuyên mục), VnEconomy (2), VnExpress Kinh doanh, Vietstock (3), CNBC (2), MarketWatch (1).
4. Layer 4 — Official Company IR Portals + Tavily Live Search + SEC EDGAR Live Filings:
   - Kiểm tra HTTP 200 & trích link BCTC trên 11 cổng Quan hệ Cổ đông (HPG, TPB, HDB, TCB, FPT, VCB, CTG...).
   - Truy vấn Tavily Search API 4 chuyên đề Vĩ mô & Doanh nghiệp nóng trong tuần.
   - Cào hồ sơ `10-K / 10-Q / 8-K` mới nhất trực tiếp từ `data.sec.gov/submissions`.
5. Layer 5 — Persistence, FTS5 Vault Indexing & Vietnamese Executive Digest:
   - Xuất `data/apex_daily_internet_intel.json` & làm mới `data/omni_market_intelligence.json`.
   - Đánh chỉ mục toàn văn vào SQLite FTS5 (`data/apex_institutional_vault.db`).
   - Xuất báo cáo tổng hợp tiếng Việt tại `02_Equity_Research/YYYY-MM-DD_Daily_Internet_And_BCTC_Intel_Report.md`.
"""

import argparse
import datetime
import hashlib
import html as html_lib
import json
import re
import sqlite3
import ssl
import subprocess
import sys
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
VN_DATA_DIR = BASE_DIR / "VN_Market" / "data"
RESEARCH_DIR = BASE_DIR / "02_Equity_Research"
OUT_INTEL_JSON = DATA_DIR / "apex_daily_internet_intel.json"
OMNI_OUTPUT_JSON = DATA_DIR / "omni_market_intelligence.json"
VN_BCTC_LIVE_PATH = VN_DATA_DIR / "vn_real_bctc_live.json"
US_BCTC_LIVE_PATH = DATA_DIR / "us_real_bctc_live.json"
DB_PATH = DATA_DIR / "apex_institutional_vault.db"

SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, application/json, text/html, */*",
    "Connection": "close",
}
SEC_HEADERS = {
    "User-Agent": "ApexInstitutionalFund/3.0 (research@apex-fund.internal)",
    "Accept": "application/json",
    "Connection": "close",
}

PRIORITY_VN_TICKERS: List[str] = [
    "TPB", "HDB", "HPG", "CTG", "VPB", "MBB", "TCB", "VCB", "BID", "FPT",
    "MWG", "SSI", "VND", "VHM", "KDH", "NLG", "GAS", "PVD", "PVT", "BSR",
    "BAF", "MSH", "VIX", "CII", "CEO", "NT2", "HDG", "DGC", "VNM", "MSN",
]

US_RECOGNITION_TICKERS: List[str] = [
    "NVDA", "AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "AMD", "TSM", "AVGO", "INTC", "JPM",
]

VERIFIED_IR_PORTALS: Dict[str, Tuple[str, str]] = {
    "HPG": ("CTCP Tập đoàn Hòa Phát", "https://www.hoaphat.com.vn/quan-he-co-dong/bao-cao-tai-chinh"),
    "TPB": ("Ngân hàng TMCP Tiên Phong (TPBank)", "https://tpb.vn/nha-dau-tu/bao-cao-tai-chinh"),
    "HDB": ("Ngân hàng TMCP Phát triển TP.HCM (HDBank)", "https://hdbank.com.vn/vi/investor/thong-tin-nha-dau-tu/bao-cao-tai-chinh"),
    "TCB": ("Ngân hàng TMCP Kỹ Thương VN (Techcombank)", "https://techcombank.com/nha-dau-tu"),
    "FPT": ("CTCP FPT", "https://fpt.com/vi/nha-dau-tu"),
    "VCB": ("Ngân hàng TMCP Ngoại Thương VN (Vietcombank)", "https://vietcombank.com.vn/vi-VN/Nha-dau-tu"),
    "CTG": ("Ngân hàng TMCP Công Thương VN (VietinBank)", "https://www.vietinbank.vn/vi/nha-dau-tu"),
    "ACB": ("Ngân hàng TMCP Á Châu (ACB)", "https://acb.com.vn/quan-he-co-dong"),
    "BID": ("Ngân hàng TMCP Đầu tư & PT VN (BIDV)", "https://bidv.com.vn/vn/quan-he-nha-dau-tu"),
    "MWG": ("CTCP Đầu tư Thế Giới Di Động", "https://mwg.vn/"),
    "BAF": ("CTCP Nông nghiệp BAF Việt Nam", "https://baf.vn/quan-he-co-dong/"),
}

RSS_FEEDS: List[Tuple[str, str, str]] = [
    ("CafeF - Chứng khoán", "https://cafef.vn/thi-truong-chung-khoan.rss", "VN"),
    ("CafeF - Doanh nghiệp", "https://cafef.vn/doanh-nghiep.rss", "VN"),
    ("CafeF - Tài chính Ngân hàng", "https://cafef.vn/tai-chinh-ngan-hang.rss", "VN"),
    ("CafeF - Bất động sản", "https://cafef.vn/bat-dong-san.rss", "VN"),
    ("VnEconomy - Chứng khoán", "https://vneconomy.vn/chung-khoan.rss", "VN"),
    ("VnEconomy - Tài chính", "https://vneconomy.vn/tai-chinh.rss", "VN"),
    ("VnExpress - Kinh doanh", "https://vnexpress.net/rss/kinh-doanh.rss", "VN"),
    ("Vietstock - Cổ phiếu", "https://vietstock.vn/830/chung-khoan/co-phieu.rss", "VN"),
    ("Vietstock - Doanh nghiệp", "https://vietstock.vn/739/kinh-doanh/doanh-nghiep.rss", "VN"),
    ("Vietstock - Hoạt động KD", "https://vietstock.vn/737/doanh-nghiep/hoat-dong-kinh-doanh.rss", "VN"),
    ("CNBC Top News", "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114", "US"),
    ("CNBC Economy", "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=20910258", "US"),
    ("MarketWatch Top Stories", "https://feeds.content.dowjones.io/public/rss/mw_topstories", "US"),
]

SEC_TOP_CIKS: Dict[str, str] = {
    "NVDA": "0001045810",
    "AAPL": "0000320193",
    "MSFT": "0000789019",
    "GOOGL": "0001652044",
    "AMZN": "0001018724",
    "META": "0001326801",
}

def _build_dynamic_tavily_queries() -> List[Dict[str, Any]]:
    """Tao truy van Tavily theo quy/thang/nam thuc te, khong gan cung thoi gian."""
    now_ict = datetime.datetime.now(datetime.timezone.utc).astimezone(datetime.timezone(datetime.timedelta(hours=7)))
    yr = now_ict.year
    prev_q = ((now_ict.month - 1) // 3) or 4
    q_yr = yr if prev_q < 4 else (yr - 1)
    mo_str = now_ict.strftime("%B %Y")
    return [
        {
            "topic_id": "VN_MACRO_MARGIN",
            "title_vi": f"Vĩ mô VN-Index, Dư nợ Margin & Thanh khoản Ngân hàng Nhà nước (Q{prev_q}/{q_yr})",
            "query": f"VN-Index dư nợ margin chứng khoán quý {prev_q} {q_yr} ngân hàng nhà nước tỷ giá lãi suất {yr}",
        },
        {
            "topic_id": "VN_BANKS_LEADERS",
            "title_vi": "Kết quả Kinh doanh & Tín dụng Nhóm Ngân hàng Đầu ngành (TPB, HDB, CTG, NAB)",
            "query": f"TPBank TPB HDBank HDB VietinBank CTG Nam A Bank NAB lợi nhuận quý {prev_q} {q_yr} tăng trưởng tín dụng",
        },
        {
            "topic_id": "HPG_DUNG_QUAT_2",
            "title_vi": "Hòa Phát (HPG) & Ngành Thép — Tiến độ Dung Quất 2, HRC & Bảo hộ",
            "query": f"Hòa Phát HPG Dung Quất 2 sản lượng thép HRC quý {prev_q} {yr}",
        },
        {
            "topic_id": "US_MACRO_AI_TECH",
            "title_vi": f"Vĩ mô Mỹ (Fed, US10Y, VIX) & Big Tech / AI ({mo_str})",
            "query": f"Federal Reserve US 10Y yield VIX Nvidia Google Amazon AI outlook {mo_str}",
        },
    ]


def _resolve_dynamic_priority_tickers() -> List[str]:
    """Hop nhat PRIORITY_VN_TICKERS + SSOT holdings/watchlist + Top 15 Alpha tu Brain V4/V3."""
    ordered: List[str] = []
    seen = set()

    def _add(sym: str) -> None:
        s = str(sym or "").upper().strip()
        if s and s not in seen:
            seen.add(s)
            ordered.append(s)

    ssot_p = DATA_DIR / "current_portfolio_state.json"
    if ssot_p.exists():
        try:
            ssot = json.loads(ssot_p.read_text(encoding="utf-8"))
            for s in (ssot.get("active_positions") or {}).keys():
                _add(s)
            for w in (ssot.get("next_round_watchlist") or []):
                _add((w or {}).get("symbol", ""))
        except Exception:
            pass

    for brain_name in ("apex_brain_v4_output.json", "apex_autonomous_brain_v3_output.json"):
        bp = DATA_DIR / brain_name
        if bp.exists():
            try:
                bd = json.loads(bp.read_text(encoding="utf-8"))
                for row in (bd.get("ranked_universe") or bd.get("top_picks") or [])[:15]:
                    _add((row or {}).get("symbol", ""))
                break
            except Exception:
                pass

    for s in PRIORITY_VN_TICKERS:
        _add(s)
    return ordered


TAVILY_QUERIES: List[Dict[str, Any]] = _build_dynamic_tavily_queries()

POS_KW = (
    "tăng trưởng", "bứt phá", "kỷ lục", "lãi ròng tăng", "vượt kế hoạch", "chia cổ tức",
    "mua ròng", "nâng hạng", "hợp đồng lớn", "mở rộng", "cấp phép", "khởi công", "tốp", "top ",
    "vinh danh", "hoàn thành", "khả quan", "beats", "record", "surge", "upgrade", "rally", "growth",
)
NEG_KW = (
    "thua lỗ", "lỗ ròng", "sụt giảm", "giảm sâu", "cảnh báo", "vi phạm", "ngoại trừ",
    "đình chỉ", "bán tháo", "bán ròng", "giải trình", "phạt", "hủy niêm yết", "cắt margin",
    "vỡ nợ", "call margin", "force sell", "loss", "plunge", "miss", "downgrade", "slump", "sell-off",
)


def _get_ict_now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc).astimezone(datetime.timezone(datetime.timedelta(hours=7)))


def _clean_text(raw: str) -> str:
    txt = html_lib.unescape(raw or "")
    txt = re.sub(r"<[^>]+>", " ", txt)
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt


def _fetch_url_bytes(url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 8) -> Tuple[int, bytes, str]:
    req = urllib.request.Request(url, headers=headers or BROWSER_HEADERS)
    with urllib.request.urlopen(req, timeout=timeout, context=SSL_CTX) as resp:
        return int(getattr(resp, "status", 200)), resp.read(), str(resp.geturl())


def _score_sentiment(text: str, explicit_label: str = "") -> float:
    lbl = (explicit_label or "").strip().lower()
    base = 0.0
    if lbl == "positive":
        base = 0.45
    elif lbl == "negative":
        base = -0.45

    low = (text or "").lower()
    pos_hits = sum(1 for kw in POS_KW if kw in low)
    neg_hits = sum(1 for kw in NEG_KW if kw in low)
    score = base + 0.16 * pos_hits - 0.20 * neg_hits
    return round(max(-1.0, min(1.0, score)), 3)


def _classify_item(title: str, summary: str, market: str) -> Tuple[str, str]:
    blob = f"{title} {summary}".lower()
    if any(k in blob for k in ("cảnh báo", "lỗ", "vi phạm", "call margin", "bán tháo", "phạt", "ngoại trừ", "plunge", "sell-off")):
        return "RISK_WARNING", "HIGH"
    if any(k in blob for k in ("bctc", "báo cáo tài chính", "lợi nhuận", "doanh thu", "lãi ròng", "kqkd", "quý 3", "earnings", "10-q", "10-k")):
        return "BCTC_EARNINGS", "HIGH"
    if any(k in blob for k in ("nội bộ", "mua vào", "bán ra", "cổ đông lớn", "esop", "sáp nhập", "m&a")):
        return "MA_INSIDER", "MEDIUM"
    if any(k in blob for k in ("cổ tức", "chia thưởng", "phát hành", "quyền mua", "niêm yết", "ipo")):
        return "DIVIDEND_ESOP", "MEDIUM"
    if any(k in blob for k in ("lãi suất", "tỷ giá", "nhnn", "sbv", "fed", "gdp", "lạm phát", "margin", "vĩ mô", "dầu", "vàng")):
        return "MACRO_SBV_FED", "HIGH"
    return ("MARKET_GENERAL" if market == "VN" else "MACRO_SBV_FED"), "NORMAL"


def _extract_tickers(text: str, default_ticker: Optional[str] = None) -> List[str]:
    found: List[str] = []
    if default_ticker:
        found.append(default_ticker)
    tokens = set(re.findall(r"\b([A-Z]{2,5})\b", text or ""))
    known = set(PRIORITY_VN_TICKERS) | set(US_RECOGNITION_TICKERS)
    for tk in sorted(tokens & known):
        if tk not in found:
            found.append(tk)
    return found


def check_layer1_bctc_and_ohlcv_freshness() -> Dict[str, Any]:
    """Layer 1: Kiểm tra độ tươi dữ liệu BCTC Q3/2026, VPS OHLCV và SEC EDGAR."""
    now = _get_ict_now()
    res: Dict[str, Any] = {
        "vn_bctc_exists": VN_BCTC_LIVE_PATH.exists(),
        "us_bctc_exists": US_BCTC_LIVE_PATH.exists(),
        "vn_crawled_at": None,
        "vn_age_hours": None,
        "vn_stocks_count": 0,
        "latest_ohlcv_bar_date": None,
        "vnindex_last_close": None,
        "us_crawled_at": None,
        "us_stocks_count": 0,
        "is_fresh_under_24h": False,
        "latest_quarter_distribution": {},
    }
    if VN_BCTC_LIVE_PATH.exists():
        try:
            vd = json.loads(VN_BCTC_LIVE_PATH.read_text(encoding="utf-8"))
            c_at = vd.get("crawled_at")
            res["vn_crawled_at"] = c_at
            stocks = vd.get("stocks") or {}
            res["vn_stocks_count"] = len(stocks)
            cov = vd.get("coverage_stats") or {}
            res["latest_quarter_distribution"] = cov.get("latest_quarter_distribution") or {}
            dates = [str(s.get("last_bar_date")) for s in stocks.values() if s.get("last_bar_date")]
            res["latest_ohlcv_bar_date"] = max(dates) if dates else None
            if c_at:
                dt = datetime.datetime.strptime(c_at, "%Y-%m-%d %H:%M:%S").replace(
                    tzinfo=datetime.timezone(datetime.timedelta(hours=7))
                )
                age_h = round((now - dt).total_seconds() / 3600.0, 2)
                res["vn_age_hours"] = age_h
                res["is_fresh_under_24h"] = age_h <= 24.0
            vni_cache = DATA_DIR / "real_ohlcv_cache" / "VNINDEX.json"
            if vni_cache.exists():
                vni_d = json.loads(vni_cache.read_text(encoding="utf-8"))
                bars = vni_d.get("bars") or []
                if bars:
                    res["vnindex_last_close"] = bars[-1].get("close")
                    res["vnindex_last_date"] = bars[-1].get("date")
        except Exception as e:
            res["vn_error"] = str(e)

    if US_BCTC_LIVE_PATH.exists():
        try:
            ud = json.loads(US_BCTC_LIVE_PATH.read_text(encoding="utf-8"))
            res["us_crawled_at"] = ud.get("crawled_at")
            res["us_stocks_count"] = len(ud.get("stocks") or {})
        except Exception as e:
            res["us_error"] = str(e)
    return res


def _crawl_single_ticker_news(sym: str) -> Dict[str, Any]:
    """Layer 2: Cào tin doanh nghiệp sống từ Vietcap AI News + CafeF News & CBTT cho 1 mã."""
    items: List[Dict[str, Any]] = []
    errors: List[str] = []

    # 2A. Vietcap AI News v2
    vci_url = f"https://ai.vietcap.com.vn/api/v2/news_info?ticker={sym}&page=1&page_size=5"
    try:
        headers = {**BROWSER_HEADERS, "Referer": "https://trading.vietcap.com.vn/", "Origin": "https://trading.vietcap.com.vn"}
        _, raw_b, _ = _fetch_url_bytes(vci_url, headers=headers, timeout=8)
        payload = json.loads(raw_b.decode("utf-8", errors="replace"))
        for row in payload.get("news_info") or []:
            title = _clean_text(row.get("news_title", ""))
            summary = _clean_text(row.get("news_short_content", ""))[:320]
            if not title:
                continue
            link = str(row.get("news_source_link") or vci_url)
            pub = str(row.get("update_date") or "")
            sent_lbl = str(row.get("sentiment") or "")
            sent = _score_sentiment(f"{title} {summary}", explicit_label=sent_lbl)
            cat, urg = _classify_item(title, summary, "VN")
            items.append({
                "symbol": sym,
                "source_channel": "VIETCAP_AI_NEWS",
                "source_name": f"Vietcap/{row.get('news_from_name') or 'Market'}",
                "title": title,
                "summary": summary,
                "url": link,
                "published_at": pub,
                "sentiment_label": sent_lbl or "Neutral",
                "sentiment_score": sent,
                "category": cat,
                "urgency": urg,
            })
    except Exception as e:
        errors.append(f"Vietcap:{e}")

    # 2B. CafeF Related News (Type=1 Corporate News, Type=2 CBTT / Dividends / Insider)
    for ev_type, type_lbl in [(1, "CafeF Doanh nghiệp"), (2, "CafeF CBTT/Sự kiện")]:
        cf_url = f"https://cafef.vn/du-lieu/Ajax/Events_RelatedNews_New.aspx?symbol={sym}&floorID=0&configID=0&PageIndex=1&PageSize=4&Type={ev_type}"
        try:
            headers = {**BROWSER_HEADERS, "Referer": "https://cafef.vn/"}
            _, raw_b, _ = _fetch_url_bytes(cf_url, headers=headers, timeout=8)
            raw_html = raw_b.decode("utf-8", errors="replace")
            blocks = re.findall(
                r'<span class="timeTitle">([^<]+)</span>.*?<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
                raw_html,
                flags=re.S | re.I,
            )
            for t_str, href, ttl_raw in blocks[:4]:
                title = _clean_text(ttl_raw)
                if not title:
                    continue
                full_href = href if href.startswith("http") else f"https://cafef.vn{href}"
                sent = _score_sentiment(title)
                cat, urg = _classify_item(title, "", "VN")
                if ev_type == 2 and cat == "MARKET_GENERAL":
                    cat = "DIVIDEND_ESOP"
                items.append({
                    "symbol": sym,
                    "source_channel": f"CAFEF_TYPE_{ev_type}",
                    "source_name": type_lbl,
                    "title": title,
                    "summary": f"[{sym} - {type_lbl} @ {_clean_text(t_str)}] {title}",
                    "url": full_href,
                    "published_at": _clean_text(t_str),
                    "sentiment_label": "Positive" if sent > 0.1 else ("Negative" if sent < -0.1 else "Neutral"),
                    "sentiment_score": sent,
                    "category": cat,
                    "urgency": urg,
                })
        except Exception as e:
            errors.append(f"CafeF_T{ev_type}:{e}")

    # Deduplicate by normalized title
    seen_t = set()
    dedup: List[Dict[str, Any]] = []
    for it in items:
        norm = re.sub(r"\W+", "", it["title"].lower())[:64]
        if norm and norm not in seen_t:
            seen_t.add(norm)
            dedup.append(it)

    avg_sent = round(sum(x["sentiment_score"] for x in dedup) / len(dedup), 3) if dedup else 0.0
    pos_cnt = sum(1 for x in dedup if x["sentiment_score"] > 0.1)
    neg_cnt = sum(1 for x in dedup if x["sentiment_score"] < -0.1)
    return {
        "symbol": sym,
        "news_count": len(dedup),
        "avg_sentiment": avg_sent,
        "positive_count": pos_cnt,
        "negative_count": neg_cnt,
        "latest_headline": dedup[0]["title"] if dedup else "",
        "latest_date": dedup[0]["published_at"] if dedup else "",
        "items": dedup,
        "errors": errors,
    }


def _crawl_single_rss_feed(spec: Tuple[str, str, str]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """Layer 3 helper: Cào 1 kênh RSS báo chí tài chính."""
    name, url, market = spec
    health = {"source": name, "market": market, "url": url, "ok": False, "count": 0, "error": None}
    articles: List[Dict[str, Any]] = []
    try:
        status, raw_b, _ = _fetch_url_bytes(url, timeout=9)
        if status >= 400:
            health["error"] = f"HTTP_{status}"
            return health, articles
        xml_txt = raw_b.decode("utf-8", errors="replace").lstrip("\ufeff \t\r\n")
        root = ET.fromstring(xml_txt)
        for item_el in root.findall(".//item")[:20]:
            title = _clean_text(item_el.findtext("title") or "")
            link = _clean_text(item_el.findtext("link") or "")
            desc = _clean_text(item_el.findtext("description") or "")[:350]
            pub = _clean_text(item_el.findtext("pubDate") or "")
            if not title:
                continue
            tickers = _extract_tickers(f"{title} {desc}")
            sent = _score_sentiment(f"{title} {desc}")
            cat, urg = _classify_item(title, desc, market)
            item_id = hashlib.md5(f"{market}:{link or title}".encode("utf-8")).hexdigest()[:16]
            articles.append({
                "item_id": item_id,
                "market": market,
                "category": cat,
                "urgency": urg,
                "sentiment_score": sent,
                "tickers": tickers,
                "sector": "MACRO" if not tickers else tickers[0],
                "title": title,
                "summary": desc or title,
                "source_name": name,
                "source_url": link or url,
                "published_at": pub,
            })
        health["ok"] = True
        health["count"] = len(articles)
    except Exception as e:
        health["error"] = str(e)[:120]
    return health, articles


def _probe_single_ir_portal(sym: str, company_name: str, url: str) -> Dict[str, Any]:
    """Layer 4A helper: Kiểm tra cổng Quan hệ Cổ đông (IR) chính thống & trích link BCTC."""
    out: Dict[str, Any] = {
        "symbol": sym,
        "company_name": company_name,
        "portal_url": url,
        "http_status": None,
        "ok": False,
        "page_title": "",
        "bctc_links_found": 0,
        "sample_bctc_links": [],
        "error": None,
    }
    try:
        status, raw_b, final_url = _fetch_url_bytes(url, timeout=8)
        html_txt = raw_b.decode("utf-8", errors="replace")
        m_title = re.search(r"<title[^>]*>(.*?)</title>", html_txt, flags=re.S | re.I)
        title = _clean_text(m_title.group(1)) if m_title else sym
        links = re.findall(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html_txt, flags=re.S | re.I)
        bctc_links: List[Dict[str, str]] = []
        for href, anchor_raw in links:
            anchor = _clean_text(anchor_raw)
            low = f"{href} {anchor}".lower()
            if any(k in low for k in ("bctc", "báo cáo tài chính", "bao-cao-tai-chinh", "financial", "2026", "quý", "q3")):
                abs_url = urllib.parse.urljoin(final_url, href)
                if abs_url.startswith("http") and anchor:
                    bctc_links.append({"text": anchor[:100], "url": abs_url})
        out.update({
            "http_status": status,
            "ok": status == 200,
            "final_url": final_url,
            "page_title": title[:120],
            "bctc_links_found": len(bctc_links),
            "sample_bctc_links": bctc_links[:5],
        })
    except Exception as e:
        out["error"] = str(e)[:120]
    return out


def _fetch_sec_recent_filings() -> List[Dict[str, Any]]:
    """Layer 4B helper: Cào trực tiếp danh sách hồ sơ 10-Q/10-K/8-K mới nhất từ SEC EDGAR."""
    results: List[Dict[str, Any]] = []
    for sym, cik in SEC_TOP_CIKS.items():
        url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        try:
            _, raw_b, _ = _fetch_url_bytes(url, headers=SEC_HEADERS, timeout=9)
            data = json.loads(raw_b.decode("utf-8", errors="replace"))
            recent = (data.get("filings") or {}).get("recent") or {}
            forms = recent.get("form") or []
            fdates = recent.get("filingDate") or []
            rdates = recent.get("reportDate") or []
            acc_nums = recent.get("accessionNumber") or []
            docs = recent.get("primaryDocument") or []
            picked = []
            for form, fdate, rdate, acc, doc in zip(forms, fdates, rdates, acc_nums, docs):
                if form in ("10-K", "10-Q", "8-K"):
                    acc_nodash = str(acc).replace("-", "")
                    doc_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_nodash}/{doc}"
                    picked.append({"form": form, "filing_date": fdate, "report_date": rdate, "url": doc_url})
                    if len(picked) >= 3:
                        break
            results.append({
                "symbol": sym,
                "cik": cik,
                "entity_name": data.get("name", sym),
                "ok": True,
                "recent_filings": picked,
            })
        except Exception as e:
            results.append({"symbol": sym, "cik": cik, "ok": False, "error": str(e)[:100], "recent_filings": []})
    return results


def _run_tavily_queries() -> List[Dict[str, Any]]:
    """Layer 4C helper: Truy vấn Tavily Search API 4 chuyên đề nóng (thời gian động)."""
    try:
        from scripts.tavily_bridge import tavily_search
    except Exception:
        return []

    outputs: List[Dict[str, Any]] = []
    for qspec in _build_dynamic_tavily_queries():
        res = tavily_search(
            query=qspec["query"],
            search_depth="advanced",
            max_results=5,
            time_range="week",
            include_answer=True,
            timeout=12,
        )
        hits = []
        for r in res.get("results") or []:
            hits.append({
                "title": _clean_text(r.get("title", "")),
                "url": r.get("url", ""),
                "snippet": _clean_text(r.get("content", ""))[:320],
                "score": r.get("score"),
            })
        outputs.append({
            "topic_id": qspec["topic_id"],
            "title_vi": qspec["title_vi"],
            "query": qspec["query"],
            "ok": bool(res.get("ok")),
            "answer": _clean_text(res.get("answer") or "")[:500],
            "hits_count": len(hits),
            "hits": hits,
            "error": res.get("error"),
        })
    return outputs


def _index_items_to_sqlite_fts(items: List[Dict[str, Any]], crawled_at: str) -> int:
    """Layer 5 helper: Nạp các tin tức/CBTT mới cào vào SQLite + FTS5 Vault."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    cur.execute("""
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
        )
    """)
    cur.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS omni_intelligence_fts USING fts5(
            item_id UNINDEXED,
            title,
            summary,
            tickers_text,
            category,
            sector,
            source_name
        )
    """)
    indexed = 0
    for it in items:
        iid = str(it.get("item_id") or "")
        if not iid:
            continue
        tks = it.get("tickers") or []
        tks_txt = " ".join(tks)
        cur.execute(
            """
            INSERT OR REPLACE INTO omni_intelligence_items
            (item_id, market, category, urgency, sentiment_score, tickers_json, tickers_text, sector, title, summary, source_name, source_url, published_at, crawled_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                iid,
                it.get("market", "VN"),
                it.get("category", "MARKET_GENERAL"),
                it.get("urgency", "NORMAL"),
                float(it.get("sentiment_score") or 0.0),
                json.dumps(tks, ensure_ascii=False),
                tks_txt,
                it.get("sector", ""),
                it.get("title", ""),
                it.get("summary", ""),
                it.get("source_name", ""),
                it.get("source_url", ""),
                it.get("published_at", ""),
                crawled_at,
            ),
        )
        cur.execute("DELETE FROM omni_intelligence_fts WHERE item_id = ?", (iid,))
        cur.execute(
            """
            INSERT INTO omni_intelligence_fts (item_id, title, summary, tickers_text, category, sector, source_name)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                iid,
                it.get("title", ""),
                it.get("summary", ""),
                tks_txt,
                it.get("category", "MARKET_GENERAL"),
                it.get("sector", ""),
                it.get("source_name", ""),
            ),
        )
        indexed += 1
    conn.commit()
    conn.close()
    return indexed


def _write_markdown_digest(intel: Dict[str, Any], out_path: Path) -> None:
    counts = intel.get("summary_counts") or {}
    bctc_f = intel.get("bctc_and_ohlcv_freshness") or {}
    ticker_profs = intel.get("ticker_corporate_intel") or {}
    ir_list = intel.get("ir_portals") or []
    tavily_list = intel.get("tavily_intelligence") or []
    sec_list = intel.get("sec_edgar_filings") or []
    top_articles = intel.get("top_priority_headlines") or []

    lines = [
        f"# BÁO CÁO TÌNH BÁO THỊ TRƯỜNG, BCTC & INTERNET SỐNG HÀNG NGÀY ({intel['crawl_date']})",
        f"> **Thời điểm cào dữ liệu thật:** `{intel['crawled_at']} ICT` (Thời gian chạy: `{intel['elapsed_sec']}s`)  ",
        f"> **Cơ quan thực thi:** Ban 2 (Pháp y BCTC) & Ban 10 (`Hiền` IR Scout) — Giai đoạn 1 Nâng cấp Toàn diện",
        "",
        "---",
        "",
        "## I. TỔNG QUAN NGUỒN DỮ LIỆU ĐÃ CÀO TRỰC TIẾP TRÊN INTERNET HÔM NAY",
        f"- **Tổng bài báo RSS / Tin doanh nghiệp / CBTT hợp nhất:** **`{counts.get('total_news_articles', 0)}` mục sống** (`{counts.get('rss_sources_online', 0)}/13` kênh RSS online).",
        f"- **Tin doanh nghiệp Vietcap AI & CafeF theo mã:** **`{counts.get('tickers_with_live_news', 0)}/{len(PRIORITY_VN_TICKERS)}` mã trọng điểm VN**.",
        f"- **Cổng Quan hệ Cổ đông (IR) doanh nghiệp HTTP 200:** **`{counts.get('verified_ir_portals', 0)}/{len(VERIFIED_IR_PORTALS)}` cổng xác thực**.",
        f"- **Tìm kiếm Web nâng cao Tavily:** **`{counts.get('tavily_live_hits', 0)}` kết quả sống** trên 4 chuyên đề Vĩ mô & Doanh nghiệp.",
        f"- **Hồ sơ SEC EDGAR Mỹ mới nhất (`10-Q/10-K/8-K`):** **`{counts.get('sec_edgar_filings', 0)}` tập đoàn**.",
        f"- **Kho BCTC & Giá EOD VPS:** `{bctc_f.get('vn_stocks_count', 0)}` DN VN (`{bctc_f.get('latest_quarter_distribution')}`), thanh giá cuối `{bctc_f.get('latest_ohlcv_bar_date')}` (`VNINDEX = {bctc_f.get('vnindex_last_close')}`), cập nhật `{bctc_f.get('vn_crawled_at')}` (`{bctc_f.get('vn_age_hours')}h` trước).",
        "",
        "## II. TÌNH BÁO DOANH NGHIỆP & TIN TỨC RỔ TUẦN 48 VS NHÓM RỦI RO",
        "",
        "| Mã | Số Tin | Sentiment TB | Tin Mới Nhất (Vietcap AI / CafeF CBTT) |",
        "| :--- | :---: | :---: | :--- |",
    ]
    focus_syms = ["TPB", "HDB", "HPG", "CTG", "VPB", "MBB", "TCB", "FPT", "BAF", "MSH", "VIX", "CII", "CEO"]
    for sym in focus_syms:
        tp = ticker_profs.get(sym)
        if not tp:
            continue
        hdl = (tp.get("latest_headline") or "Không có tin mới").replace("|", "-")[:120]
        dt_s = tp.get("latest_date") or ""
        lines.append(f"| **{sym}** | `{tp.get('news_count', 0)}` | `{tp.get('avg_sentiment', 0.0):+.2f}` | `{dt_s}` — {hdl} |")

    lines.extend([
        "",
        "## III. TÌNH BÁO WEB TAVILY & CỔNG IR DOANH NGHIỆP CHÍNH THỐNG",
        "",
    ])
    for tv in tavily_list:
        lines.append(f"### 🔍 {tv.get('title_vi')} (`{tv.get('hits_count', 0)} nguồn`)")
        if tv.get("answer"):
            lines.append(f"> {tv['answer']}")
        for h in (tv.get("hits") or [])[:3]:
            lines.append(f"- [{h.get('title', 'Nguồn')}]({h.get('url', '')}): {h.get('snippet', '')[:180]}...")
        lines.append("")

    lines.append("### 🏛️ Kiểm Chứng Cổng IR Doanh Nghiệp Trực Tiếp")
    for ir in ir_list:
        st_lbl = f"HTTP {ir.get('http_status')}" if ir.get("ok") else f"LỖI ({ir.get('error')})"
        lines.append(f"- **{ir['symbol']}** ({ir['company_name']}): `{st_lbl}` | Tìm thấy `{ir.get('bctc_links_found', 0)}` link BCTC/tài liệu tại {ir['portal_url']}")

    lines.extend(["", "### 🇺🇸 Hồ Sơ SEC EDGAR Mỹ Mới Nhất", ""])
    for sc in sec_list:
        if sc.get("ok") and sc.get("recent_filings"):
            top_f = sc["recent_filings"][0]
            lines.append(f"- **{sc['symbol']}** ({sc['entity_name']}): `{top_f['form']}` nộp `{top_f['filing_date']}` ([Xem SEC]({top_f['url']}))")

    lines.extend(["", "## IV. TOP TIÊU ĐIỂM BÁO CHÍ TÀI CHÍNH MỚI CÀO", ""])
    for art in top_articles[:15]:
        tks = ", ".join(art.get("tickers") or []) or art.get("market")
        lines.append(f"- `[{art.get('source_name')}]` (`{tks}`, Sent `{art.get('sentiment_score', 0):+.2f}`): [{art.get('title')}]({art.get('source_url')})")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_daily_intelligence_crawl(refresh_bctc: bool = False) -> Dict[str, Any]:
    t0 = time.time()
    now_ict = _get_ict_now()
    crawled_at_str = now_ict.strftime("%Y-%m-%d %H:%M:%S")
    crawl_date_str = now_ict.strftime("%Y-%m-%d")

    print("=" * 76)
    print(f"  [BAN 2 & BAN 10] DAILY LIVE INTERNET, BCTC & IR INTELLIGENCE CRAWLER ({crawled_at_str} ICT)")
    print("=" * 76)

    # Optional BCTC refresh
    if refresh_bctc:
        print(">>> [Layer 0] Đang kích hoạt làm mới BCTC Q3/2026 & VPS OHLCV + SEC EDGAR...")
        subprocess.run([sys.executable, str(BASE_DIR / "scripts" / "apex_real_bctc_crawler.py"), "--force", "--with-us"], cwd=str(BASE_DIR))

    # Layer 1
    print(">>> [Layer 1] Kiểm tra độ tươi dữ liệu BCTC Q3/2026 & OHLCV VPS...")
    layer1 = check_layer1_bctc_and_ohlcv_freshness()
    print(f"    VN BCTC: {layer1.get('vn_stocks_count')} mã | Last bar: {layer1.get('latest_ohlcv_bar_date')} | Age: {layer1.get('vn_age_hours')}h")

    # Layer 2 (Dynamic priority tickers: SSOT + Top Alpha + Priority 30)
    target_tickers = _resolve_dynamic_priority_tickers()
    print(f">>> [Layer 2] Cào Vietcap AI News + CafeF Tin DN & CBTT cho {len(target_tickers)} mã (SSOT + Alpha + Trọng điểm)...")
    ticker_intel: Dict[str, Dict[str, Any]] = {}
    corp_items_for_omni: List[Dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        futs = {pool.submit(_crawl_single_ticker_news, sym): sym for sym in target_tickers}
        for fut in as_completed(futs):
            tp = fut.result()
            sym = tp["symbol"]
            ticker_intel[sym] = {k: v for k, v in tp.items() if k != "items"}
            ticker_intel[sym]["top_items"] = tp["items"][:5]
            for it in tp["items"]:
                iid = hashlib.md5(f"CORP:{sym}:{it['title']}".encode("utf-8")).hexdigest()[:16]
                corp_items_for_omni.append({
                    "item_id": iid,
                    "market": "VN",
                    "category": it["category"],
                    "urgency": it["urgency"],
                    "sentiment_score": it["sentiment_score"],
                    "tickers": [sym],
                    "sector": sym,
                    "title": it["title"],
                    "summary": it["summary"],
                    "source_name": it["source_name"],
                    "source_url": it["url"],
                    "published_at": it["published_at"],
                })

    # Layer 3 (13 RSS feeds concurrent)
    print(f">>> [Layer 3] Cào {len(RSS_FEEDS)} kênh RSS Báo chí Tài chính VN & Quốc tế...")
    rss_health: List[Dict[str, Any]] = []
    rss_items: List[Dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        futs = {pool.submit(_crawl_single_rss_feed, sp): sp[0] for sp in RSS_FEEDS}
        for fut in as_completed(futs):
            h, arts = fut.result()
            rss_health.append(h)
            rss_items.extend(arts)

    # Layer 4 (IR Portals + Tavily + SEC EDGAR)
    print(">>> [Layer 4] Kiểm chứng Cổng IR chính thống + Tavily Web + SEC EDGAR...")
    ir_results: List[Dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=6) as pool:
        futs = {pool.submit(_probe_single_ir_portal, sym, comp, url): sym for sym, (comp, url) in VERIFIED_IR_PORTALS.items()}
        for fut in as_completed(futs):
            ir_results.append(fut.result())
    ir_results.sort(key=lambda x: x["symbol"])

    tavily_results = _run_tavily_queries()
    sec_results = _fetch_sec_recent_filings()

    # Merge + Deduplicate all articles
    merged_items: List[Dict[str, Any]] = []
    seen_titles = set()
    for it in corp_items_for_omni + rss_items:
        norm = re.sub(r"\W+", "", (it.get("title") or "").lower())[:64]
        if norm and norm not in seen_titles:
            seen_titles.add(norm)
            merged_items.append(it)

    cat_counts: Dict[str, int] = {}
    for it in merged_items:
        c = it.get("category", "MARKET_GENERAL")
        cat_counts[c] = cat_counts.get(c, 0) + 1

    # Prioritize HIGH urgency or watchlist tickers for top_priority_headlines
    priority_set = {"TPB", "HDB", "HPG", "CTG", "VPB", "NVDA", "GOOGL", "AMZN", "META"}
    priority_sorted = sorted(
        merged_items,
        key=lambda x: (
            1 if any(t in priority_set for t in (x.get("tickers") or [])) else 0,
            1 if x.get("urgency") == "HIGH" else 0,
            abs(float(x.get("sentiment_score") or 0.0)),
        ),
        reverse=True,
    )

    indexed_count = _index_items_to_sqlite_fts(merged_items, crawled_at_str)
    tavily_hits_total = sum(x.get("hits_count", 0) for x in tavily_results)
    ir_ok_count = sum(1 for x in ir_results if x.get("ok"))
    sec_ok_count = sum(1 for x in sec_results if x.get("ok"))
    rss_online_count = sum(1 for x in rss_health if x.get("ok"))
    tickers_with_news = sum(1 for v in ticker_intel.values() if v.get("news_count", 0) > 0)

    elapsed = round(time.time() - t0, 2)

    daily_intel = {
        "engine": "APEX_DAILY_INTERNET_INTEL_CRAWLER_V7",
        "crawled_at": crawled_at_str,
        "crawl_date": crawl_date_str,
        "elapsed_sec": elapsed,
        "target_tickers_count": len(target_tickers),
        "freshness_sla": {
            "crawled_at_ict": crawled_at_str,
            "bctc_age_hours": layer1.get("vn_age_hours"),
            "bctc_stocks_count": layer1.get("vn_stocks_count", 0),
            "latest_ohlcv_bar_date": layer1.get("latest_ohlcv_bar_date"),
            "rss_sources_online": rss_online_count,
            "ir_portals_ok": ir_ok_count,
            "sla_status": "HEALTHY" if (layer1.get("is_fresh_under_24h") and rss_online_count >= 8) else "DEGRADED",
        },
        "summary_counts": {
            "total_news_articles": len(merged_items),
            "corp_vietcap_cafef_articles": len(corp_items_for_omni),
            "rss_articles": len(rss_items),
            "rss_sources_online": rss_online_count,
            "tickers_with_live_news": tickers_with_news,
            "verified_ir_portals": ir_ok_count,
            "tavily_live_hits": tavily_hits_total,
            "sec_edgar_filings": sec_ok_count,
            "sqlite_fts_indexed": indexed_count,
        },
        "bctc_and_ohlcv_freshness": layer1,
        "ticker_corporate_intel": {k: ticker_intel[k] for k in sorted(ticker_intel.keys())},
        "rss_source_health": rss_health,
        "ir_portals": ir_results,
        "tavily_intelligence": tavily_results,
        "sec_edgar_filings": sec_results,
        "top_priority_headlines": priority_sorted[:40],
    }

    omni_compat = {
        "crawled_at": crawled_at_str,
        "universe_counts": {"vn": layer1.get("vn_stocks_count", 80), "us": layer1.get("us_stocks_count", 12), "total": layer1.get("vn_stocks_count", 80) + layer1.get("us_stocks_count", 12)},
        "total_items": len(merged_items),
        "category_counts": cat_counts,
        "live_bctc_updates_count": layer1.get("vn_stocks_count", 0),
        "catalyst_alerts_count": sum(1 for x in merged_items if x.get("urgency") == "HIGH"),
        "holding_alerts_count": 0,
        "sources_online": rss_online_count + ir_ok_count,
        "source_health": rss_health,
        "items": merged_items[:250],
    }

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUT_INTEL_JSON.write_text(json.dumps(daily_intel, ensure_ascii=False, indent=2), encoding="utf-8")
    OMNI_OUTPUT_JSON.write_text(json.dumps(omni_compat, ensure_ascii=False, indent=2), encoding="utf-8")

    md_report_path = RESEARCH_DIR / f"{crawl_date_str}_Daily_Internet_And_BCTC_Intel_Report.md"
    _write_markdown_digest(daily_intel, md_report_path)

    print(
        f"[+] HOÀN TẤT CÀO INTERNET & BCTC TRONG {elapsed}s | "
        f"Tin hợp nhất: {len(merged_items)} | Mã có tin: {tickers_with_news}/{len(PRIORITY_VN_TICKERS)} | "
        f"RSS Online: {rss_online_count}/13 | Cổng IR OK: {ir_ok_count}/{len(VERIFIED_IR_PORTALS)} | "
        f"Tavily hits: {tavily_hits_total} | SEC EDGAR: {sec_ok_count}/6"
    )
    print(f"    -> JSON: {OUT_INTEL_JSON}")
    print(f"    -> MD  : {md_report_path}")
    return daily_intel


def main() -> None:
    parser = argparse.ArgumentParser(description="Apex Daily Internet, BCTC & IR Intelligence Crawler V3.0")
    parser.add_argument("--refresh-bctc", action="store_true", help="Chạy kèm apex_real_bctc_crawler.py --force --with-us")
    args = parser.parse_args()
    run_daily_intelligence_crawl(refresh_bctc=args.refresh_bctc)


if __name__ == "__main__":
    main()
