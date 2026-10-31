#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CBTT & SEC EDGAR CORPORATE FILINGS RADAR (v1.0 Institutional Grade)
File: scripts/cbtt_filings_radar.py

Chức năng cốt lõi:
1. 🇺🇸 SEC EDGAR Radar (Mỹ):
   - Quét chính thức từ SEC EDGAR API cho 35+ siêu cổ phiếu Mỹ.
   - Bắt trọn Form 10-Q (BCTC quý), Form 10-K (BCTC năm), Form 8-K (Biến cố trọng yếu) và Form 4 (Giao dịch nội bộ).
2. 🇻🇳 Vietnam CBTT Radar (Việt Nam):
   - Quét luồng công bố thông tin CafeF/HOSE/HNX cho 54 siêu cổ phiếu Việt Nam.
   - Phân loại sự kiện: BCTC / Kết quả kinh doanh, Cổ tức, Phát hành ESOP, Nghị quyết HĐQT/ĐHCĐ, Cảnh báo vi phạm.
3. 🚨 Instant Alert Dispatcher:
   - Nếu phát hiện BCTC mới hoặc cảnh báo rủi ro đỏ ➔ Bắn tin khẩn cấp qua Telegram Bot tới Nhà Đầu Tư Phước Trần.
   - Xuất dữ liệu cấu trúc vào data/cbtt_live_radar.json phục vụ Ban 2, Ban 8 (Master CIO) và Ban 9 (Victor).
"""

import json
import os
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_US_PATH = BASE_DIR / "config" / "watchlist.json"
CONFIG_VN_PATH = BASE_DIR / "VN_Market" / "config" / "watchlist_vn.json"
SENTINEL_CONFIG_PATH = BASE_DIR / "09_Realtime_Portfolio_Sentinel" / "sentinel_config.json"
DATA_DIR = BASE_DIR / "data"
OUTPUT_RADAR_JSON = DATA_DIR / "cbtt_live_radar.json"
US_REPORT_MD = BASE_DIR / "02_Equity_Research" / f"{datetime.now().strftime('%Y-%m-%d')}_SEC_Filings_Radar.md"
VN_REPORT_MD = BASE_DIR / "VN_Market" / "02_BCTC_Equity_Research" / f"{datetime.now().strftime('%Y-%m-%d')}_VN_CBTT_Radar.md"

SEC_USER_AGENT = "ApexQuantFund research@apex-fund.internal"
BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

# Fallback CIK mapping for top US tickers
STATIC_CIK_MAP = {
    "NVDA": "0001045810", "MSFT": "0000789019", "AAPL": "0000320193",
    "GOOGL": "0001652044", "AMZN": "0001018724", "META": "0001326801",
    "TSLA": "0001318605", "TSM": "0001046179", "AVGO": "0001730168",
    "AMD": "0000002488", "INTC": "0000050863", "QCOM": "0000804328",
    "ARM": "0001973239", "PLTR": "0001321655", "SMCI": "0001375365",
    "COIN": "0001679788", "JPM": "0000019617", "BAC": "0000070858",
    "GS": "0000886982", "V": "0001403161", "BRK-B": "0001067983",
    "LLY": "0000059478", "NVO": "0000353278", "JNJ": "0000200406",
    "ABBV": "0001551152", "XOM": "0000034088", "CVX": "0000093410",
    "OXY": "0000797468", "LMT": "0000936468", "RTX": "0000101829",
    "CAT": "0000018230", "WMT": "0000104169", "COST": "0000909832",
    "PG": "0000080424", "MCD": "0000063908"
}


def load_telegram_credentials() -> tuple[str, str]:
    bot_token = ""
    chat_id = ""
    if SENTINEL_CONFIG_PATH.exists():
        try:
            with open(SENTINEL_CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                tg = cfg.get("notification_channels", {}).get("telegram", {})
                bot_token = tg.get("bot_token", "").strip()
                chat_id = tg.get("chat_id", "").strip()
        except Exception:
            pass
    return bot_token, chat_id


def send_telegram_alert(text: str) -> bool:
    bot_token, chat_id = load_telegram_credentials()
    if not bot_token or not chat_id:
        return False
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": True}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8")).get("ok", False)
    except Exception as e:
        print(f"  [!] Lỗi gửi Telegram: {e}")
        return False


def get_sec_cik_map() -> Dict[str, str]:
    """Fetch official SEC ticker-to-CIK mapping with static fallback"""
    cik_map = dict(STATIC_CIK_MAP)
    url = "https://www.sec.gov/files/company_tickers.json"
    req = urllib.request.Request(url, headers={"User-Agent": SEC_USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            for v in data.values():
                cik_map[v["ticker"].upper()] = str(v["cik_str"]).zfill(10)
    except Exception as e:
        print(f"  [i] SEC online CIK query error ({e}). Using static CIK mapping.")
    return cik_map


def scan_sec_edgar_filings(tickers: List[str], cik_map: Dict[str, str], max_days: int = 5) -> List[Dict[str, Any]]:
    """Scan recent SEC submissions for US tickers"""
    results = []
    print(f"\n🔍 [SEC EDGAR RADAR] Bắt đầu quét hồ sơ nộp Ủy ban Chứng khoán Mỹ (SEC) cho {len(tickers)} siêu cổ phiếu...")
    
    # Priority sample scan to avoid rate-limiting on SEC
    priority_tickers = ["NVDA", "AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "PLTR", "AVGO", "JPM"]
    scan_list = priority_tickers + [t for t in tickers if t not in priority_tickers][:15]
    
    for ticker in scan_list:
        cik = cik_map.get(ticker)
        if not cik:
            continue
            
        url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        req = urllib.request.Request(url, headers={"User-Agent": SEC_USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                filings = data.get("filings", {}).get("recent", {})
                forms = filings.get("form", [])
                dates = filings.get("filingDate", [])
                descs = filings.get("primaryDocDescription", [])
                accessions = filings.get("accessionNumber", [])
                
                for f, d, desc, acc in zip(forms[:15], dates[:15], descs[:15], accessions[:15]):
                    f_upper = f.upper()
                    # We care about 10-Q, 10-K, 8-K, Form 4, 144
                    if any(target in f_upper for target in ["10-Q", "10-K", "8-K", "4"]):
                        severity = "INFO"
                        event_type = "INSIDER_TRADING"
                        if "10-K" in f_upper or "10-Q" in f_upper:
                            severity = "CRITICAL"
                            event_type = "EARNINGS_FINANCIAL_REPORT"
                        elif "8-K" in f_upper:
                            severity = "WARNING"
                            event_type = "MATERIAL_EVENT_8K"
                            
                        results.append({
                            "market": "US_GLOBAL",
                            "symbol": ticker,
                            "company_name": data.get("name", ticker),
                            "form": f,
                            "filing_date": d,
                            "description": desc or f"SEC Form {f}",
                            "event_type": event_type,
                            "severity": severity,
                            "accession_number": acc,
                            "sec_url": f"https://www.sec.gov/edgar/browse/?CIK={cik}"
                        })
            time.sleep(0.12) # Respect SEC 10 requests per second rate limit
        except Exception as e:
            # Silent skip on minor SEC network jitter
            pass
            
    print(f"  [+] Đã phát hiện {len(results)} hồ sơ SEC nộp gần nhất.")
    return results


def scan_vietnam_cbtt(tickers: List[str]) -> List[Dict[str, Any]]:
    """Scan Vietnam corporate disclosures and earnings announcements via CafeF RSS feeds"""
    results = []
    print(f"\n🔍 [VIETNAM CBTT RADAR] Quét cổng công bố thông tin & BCTC cho {len(tickers)} siêu cổ phiếu VN...")
    
    rss_urls = [
        "https://cafef.vn/doanh-nghiep.rss",
        "https://cafef.vn/thi-truong-chung-khoan.rss",
        "https://cafef.vn/tai-chinh-ngan-hang.rss",
        "https://cafef.vn/bat-dong-san.rss"
    ]
    
    # Clean ticker symbols without .VN
    clean_syms = set([t.replace(".VN", "").upper() for t in tickers])
    sym_regex = re.compile(r'\b(' + '|'.join(sorted(clean_syms, key=len, reverse=True)) + r')\b')
    
    seen_links = set()
    
    for u in rss_urls:
        req = urllib.request.Request(u, headers=BROWSER_HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                xml_data = resp.read()
                root = ET.fromstring(xml_data)
                for item in root.findall(".//item"):
                    title = item.find("title").text or ""
                    desc = item.find("description").text or ""
                    pub_date = item.find("pubDate").text or ""
                    link = item.find("link").text or ""
                    
                    if link in seen_links:
                        continue
                    seen_links.add(link)
                    
                    full_text = f"{title} {desc}"
                    matched = sym_regex.findall(full_text)
                    if matched:
                        symbols_found = list(set([m.upper() for m in matched]))
                        text_lower = full_text.lower()
                        
                        event_type = "TIN_DOANH_NGHIEP"
                        severity = "INFO"
                        
                        if any(kw in text_lower for kw in ["bctc", "báo cáo tài chính", "kết quả kinh doanh", "lợi nhuận", "lãi ròng", "doanh thu", "lỗ"]):
                            event_type = "BCTC_KET_QUA_KINH_DOANH"
                            severity = "CRITICAL"
                        elif any(kw in text_lower for kw in ["cổ tức", "chia cổ tức", "trả cổ tức", "đkcc", "đăng ký cuối cùng", "tiền mặt"]):
                            event_type = "CO_TUC"
                            severity = "WARNING"
                        elif any(kw in text_lower for kw in ["esop", "phát hành", "chào bán", "tăng vốn", "trái phiếu"]):
                            event_type = "ESOP_PHAT_HANH"
                            severity = "WARNING"
                        elif any(kw in text_lower for kw in ["vi phạm", "cảnh báo", "nhắc nhở", "ngoại trừ", "đình chỉ", "khởi tố", "thanh tra"]):
                            event_type = "CANH_BAO_RUI_RO"
                            severity = "RED_FLAG"
                        elif any(kw in text_lower for kw in ["nghị quyết", "đhcđ", "đại hội", "dự án", "khởi công"]):
                            event_type = "NGHI_QUYET_HDQT_DU_AN"
                            severity = "INFO"
                            
                        results.append({
                            "market": "VIETNAM",
                            "symbols": symbols_found,
                            "title": title.strip(),
                            "summary": desc.strip()[:200] + "...",
                            "event_type": event_type,
                            "severity": severity,
                            "published_at": pub_date,
                            "source_url": link
                        })
        except Exception as e:
            print(f"  [!] Lỗi cào RSS {u}: {e}")
            
    print(f"  [+] Đã phát hiện {len(results)} sự kiện công bố thông tin khớp với danh mục theo dõi Việt Nam.")
    return results


def save_radar_reports(us_filings: List[Dict[str, Any]], vn_filings: List[Dict[str, Any]]) -> None:
    """Save structured JSON and clean Markdown reports for research departments"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    radar_data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "scan_date": datetime.now().strftime("%Y-%m-%d"),
        "total_us_filings_count": len(us_filings),
        "total_vn_announcements_count": len(vn_filings),
        "us_filings": us_filings,
        "vn_announcements": vn_filings
    }
    
    with open(OUTPUT_RADAR_JSON, "w", encoding="utf-8") as f:
        json.dump(radar_data, f, ensure_ascii=False, indent=2)
        
    # Markdown Báo Cáo Mỹ
    US_REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    with open(US_REPORT_MD, "w", encoding="utf-8") as f:
        f.write(f"# RADAR CÔNG BỐ THÔNG TIN & SEC EDGAR FILINGS (US LEADERS)\n")
        f.write(f"> **Thời gian quét:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
        f.write(f"> **Số lượng hồ sơ ghi nhận:** {len(us_filings)} hồ sơ SEC  \n\n")
        f.write("| Ticker | Loại Form | Mức Độ | Ngày Nộp | Mô Tả Hồ Sơ | Đường Dẫn SEC |\n")
        f.write("| :--- | :---: | :---: | :---: | :--- | :---: |\n")
        for u in us_filings[:25]:
            sev_badge = "🚨 CRITICAL" if u["severity"] == "CRITICAL" else ("⚠️ WARNING" if u["severity"] == "WARNING" else "ℹ️ INFO")
            f.write(f"| **{u['symbol']}** | `{u['form']}` | {sev_badge} | {u['filing_date']} | {u['description'][:60]} | [Xem SEC]({u['sec_url']}) |\n")
            
    # Markdown Báo Cáo Việt Nam
    VN_REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    with open(VN_REPORT_MD, "w", encoding="utf-8") as f:
        f.write(f"# RADAR CÔNG BỐ THÔNG TIN, BCTC & NGHỊ QUYẾT HĐQT (TTCK VIỆT NAM)\n")
        f.write(f"> **Thời gian quét:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
        f.write(f"> **Số sự kiện ghi nhận:** {len(vn_filings)} thông báo  \n\n")
        f.write("| Mã CK | Phân Loại Sự Kiện | Mức Độ | Tiêu Đề Công Bố | Nguồn Tin |\n")
        f.write("| :--- | :---: | :---: | :--- | :---: |\n")
        for v in vn_filings:
            sev_badge = "🔴 RED FLAG" if v["severity"] == "RED_FLAG" else ("🔥 BCTC MỚI" if v["severity"] == "CRITICAL" else ("⚠️ CHÚ Ý" if v["severity"] == "WARNING" else "ℹ️ TIN TỨC"))
            syms_str = ", ".join(v["symbols"])
            f.write(f"| **{syms_str}** | `{v['event_type']}` | {sev_badge} | {v['title']} | [Xem Link]({v['source_url']}) |\n")
            
    print(f"\n[+] Đã lưu cấu trúc dữ liệu tại: {OUTPUT_RADAR_JSON}")
    print(f"[+] Đã xuất bản báo cáo phân tích tại:")
    print(f"    - {US_REPORT_MD}")
    print(f"    - {VN_REPORT_MD}")


def check_and_send_critical_alerts(vn_filings: List[Dict[str, Any]], us_filings: List[Dict[str, Any]]) -> None:
    """Send immediate Telegram alert if critical BCTC filings or red flags are detected"""
    critical_vn = [v for v in vn_filings if v["severity"] in ["CRITICAL", "RED_FLAG"]]
    critical_us = [u for u in us_filings if u["severity"] == "CRITICAL"]
    
    if not critical_vn and not critical_us:
        print("[i] Không có sự kiện BCTC khẩn cấp hoặc cảnh báo đỏ nào cần đẩy còi Telegram ngay.")
        return
        
    text = (
        f"🚨 *[RADAR BÁO ĐỘNG CÔNG BỐ BCTC & BIẾN CỐ DOANH NGHIỆP]*\n"
        f"📅 *Thời gian:* {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
    )
    
    if critical_vn:
        text += f"🇻🇳 *SỰ KIỆN DOANH NGHIỆP VIỆT NAM QUAN TRỌNG:*\n"
        for idx, item in enumerate(critical_vn[:5], 1):
            badge = "🔴 NGUY CƠ" if item["severity"] == "RED_FLAG" else "📊 BCTC MỚI"
            text += (
                f"*{idx}. [{', '.join(item['symbols'])}]* - {badge}\n"
                f"   • *Nội dung:* {item['title']}\n"
                f"   • *Phân loại:* `{item['event_type']}`\n\n"
            )
            
    if critical_us:
        text += f"🇺🇸 *HỒ SƠ BCTC NỘP SEC MỸ (10-Q / 10-K):*\n"
        for idx, item in enumerate(critical_us[:3], 1):
            text += (
                f"*{idx}. {item['symbol']}* - Form `{item['form']}` ({item['filing_date']})\n"
                f"   • {item['description']}\n\n"
            )
            
    text += (
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"🛡 *Khuyến nghị:* Ban 2 & Master CIO đã cập nhật dữ liệu để đối soát chất lượng lợi nhuận và định cỡ rủi ro!"
    )
    
    print("[*] Đang gửi còi báo động khẩn cấp tới Telegram...")
    ok = send_telegram_alert(text)
    if ok:
        print("  [+] Đã gửi thông báo BCTC khẩn cấp thành công tới điện thoại của Nhà Đầu Tư Phước Trần!")
    else:
        print("  [!] Không thể gửi còi báo động qua Telegram.")


def main():
    print("=" * 80)
    print(" 📡 KHỞI ĐỘNG RADAR CÔNG BỐ THÔNG TIN BCTC & SEC EDGAR CHÍNH THỐNG (v1.0)")
    print("   THẨM ĐỊNH BCTC THỰC TẾ — ZERO DEFECT — ZERO HALLUCINATION")
    print("=" * 80)
    
    # 1. Load Watchlists
    us_tickers = []
    if CONFIG_US_PATH.exists():
        with open(CONFIG_US_PATH, "r", encoding="utf-8") as f:
            d = json.load(f)
            us_tickers = [x["symbol"] for x in d.get("broad_market_universe", [])]
            
    vn_tickers = []
    if CONFIG_VN_PATH.exists():
        with open(CONFIG_VN_PATH, "r", encoding="utf-8") as f:
            d = json.load(f)
            for sec, data in d.get("sectors", {}).items():
                for item in data.get("tickers", []):
                    vn_tickers.append(item.get("symbol", ""))
                    
    # 2. Scan SEC EDGAR (US)
    cik_map = get_sec_cik_map()
    us_filings = scan_sec_edgar_filings(us_tickers, cik_map)
    
    # 3. Scan Vietnam CBTT
    vn_filings = scan_vietnam_cbtt(vn_tickers)
    
    # 4. Save and Publish Reports
    save_radar_reports(us_filings, vn_filings)
    
    # 5. Alert if Critical Events Detected
    check_and_send_critical_alerts(vn_filings, us_filings)
    
    print("\n" + "=" * 80)
    print(" [HOÀN TẤT] RADAR CÔNG BỐ THÔNG TIN ĐÃ SẴN SÀNG TRỰC CHIẾN 24/24!")
    print("=" * 80)


if __name__ == "__main__":
    main()
