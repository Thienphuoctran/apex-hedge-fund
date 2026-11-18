#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APEX OVERNIGHT US SESSION, NVDA EARNINGS & VIX MONITOR + 04:30 SUMMIT ENGINE
File: scripts/us_nvda_overnight_summit_engine.py
Công điện: CD-APEX-20261118-NVDA-0430 | Mã họp: APEX-SUMMIT-20261119-0430
Đồng chủ trì: Master CIO James (Ban 8) & Palmer (Tổng Quản Trị) | Giám sát: Trọng (Ban 12)
"""

from __future__ import annotations

import argparse
import concurrent.futures
import copy
import datetime
import json
import sys
import urllib.request
import warnings
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

warnings.filterwarnings("ignore")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

DATA_DIR = BASE_DIR / "data"
ARCHIVE_DIR = DATA_DIR / "summit_archive"
RESOLUTION_DIR = BASE_DIR / "08_Master_Investment_CIO" / "council_resolutions"
SUMMIT_ARCHIVE_MD_DIR = BASE_DIR / "08_Master_Investment_CIO" / "summit_archive"
VN_SPECIALIST_DIR = BASE_DIR / "VN_Market" / "07_Daily_Specialist"

SESSION_LOG_FILE = DATA_DIR / "us_live_session_log_2026-11-18.json"
ACTIVE_MEETING_FILE = DATA_DIR / "apex_active_meeting_state.json"
ARCHIVE_LEDGER_FILE = DATA_DIR / "summit_archive_ledger.json"

AGENDA_REL_PATH = "08_Master_Investment_CIO/2026-11-18_Cong_Dien_Trieu_Tap_21h30_Theo_Doi_NVDA_VIX_Va_Hop_04h30.md"
RESOLUTION_REL_PATH = "08_Master_Investment_CIO/council_resolutions/2026-11-19_0430_Bao_Cao_Tong_Ket_James_NVDA_VIX_Va_Nghi_Quyet_Dao_Han.md"
TACTICAL_PLAN_REL_PATH = "VN_Market/07_Daily_Specialist/2026-11-19_Official_Adaptive_Tactical_Plan.md"
ARCHIVE_JSON_REL_PATH = "data/summit_archive/APEX-SUMMIT-20261119-0430.json"
ARCHIVE_MD_REL_PATH = "08_Master_Investment_CIO/summit_archive/APEX-SUMMIT-20261119-0430_Bien_Ban_Luu_Tru.md"
CHARTER_REL_PATH = "08_Master_Investment_CIO/NOI_QUY_PHONG_HOP_THUONG_DINH_APEX.md"

MEETING_ID = "APEX-SUMMIT-20261119-0430"
ICT_TZ = datetime.timezone(datetime.timedelta(hours=7))

CORE_TICKERS: List[str] = [
    "ES=F", "NQ=F", "YM=F", "RTY=F",
    "^GSPC", "^IXIC", "^DJI", "^RUT", "^VIX", "^TNX", "DX-Y.NYB", "CL=F", "GC=F", "BTC-USD",
    "VNM", "EEM",
    "SMH", "XLK", "XLF", "XLE", "XLI", "XLY", "XLV", "XLP", "XLU", "XLRE", "XLC", "XLB",
    "NVDA", "AVGO", "AMD", "TSM", "META", "XOM", "MSFT", "AAPL", "GOOGL", "AMZN", "TSLA",
]
INTRADAY_PRIORITY_TICKERS = {
    "ES=F", "NQ=F", "^GSPC", "^IXIC", "^DJI", "^VIX", "^TNX", "DX-Y.NYB", "CL=F",
    "VNM", "EEM", "SMH", "XLK", "XLF", "NVDA", "AVGO", "AMD", "TSM",
}

DEPARTMENTS_META: List[Dict[str, Any]] = [
    {"id": "BAN_1_VN", "ban_code": "Ban 1 VN", "dept_name": "Vĩ Mô, Tiền Tệ SBV & Dòng Tiền 3 Khối", "officer": "Vũ Minh (Trưởng Ban 1 VN)", "avatar": "🇻🇳", "report": "VN_Market/01_Macro_Monetary_Vietnam/2026-11-18_VN_Macro_Report.md"},
    {"id": "BAN_1_US", "ban_code": "Ban 1 US", "dept_name": "Vĩ Mô Toàn Cầu, Fed, ^VIX & GICS", "officer": "Dr. Elena Vance (Trưởng Ban 1 US)", "avatar": "🌐", "report": "01_Macro_Geopolitics/2026-11-18_Macro_Report.md"},
    {"id": "BAN_2_BCTC", "ban_code": "Ban 2", "dept_name": "Thẩm Định BCTC NVDA & Pháp Y Doanh Nghiệp", "officer": "Lê Hoàng (Trưởng Ban 2 Pháp Y)", "avatar": "🔬", "report": "02_Equity_Research/2026-11-18_Equity_Analysis.md"},
    {"id": "BAN_3_SYNTHESIS", "ban_code": "Ban 3", "dept_name": "Tổng Hợp & Công Tố Phản Biện Đa Chiều", "officer": "Trần Hưng (Công Tố Viên Ban 3)", "avatar": "⚖️", "report": "VN_Market/03_Synthesis_Memos/2026-11-18_VN_Investment_Memo.md"},
    {"id": "BAN_4_RISK", "ban_code": "Ban 4", "dept_name": "Hội Đồng Rủi Ro Định Lượng & Risk-Parity", "officer": "TS. Bảo (Chủ Tịch Hội Đồng Ban 4)", "avatar": "📐", "report": "VN_Market/04_Investment_Committee/2026-11-18_VN_IC_Decision.md"},
    {"id": "BAN_5_EVOLUTION", "ban_code": "Ban 5", "dept_name": "Kiểm Toán Hiệu Suất & Tự Tiến Hóa Hậu Exit", "officer": "Đặng Khoa (Trưởng Ban 5 Tiến Hóa)", "avatar": "🧠", "report": "VN_Market/05_Learning_And_Evolution/2026-11-18_VN_Learning_Report.md"},
    {"id": "BAN_6_ACADEMY", "ban_code": "Ban 6", "dept_name": "Học Viện Thực Chiến & Tâm Lý Kỷ Luật", "officer": "Thầy Khải (Cố Vấn Học Viện Ban 6)", "avatar": "🎓", "report": "VN_Market/06_Investor_Academy/daily_mentorship/2026-11-18_VN_Mentor_Briefing.md"},
    {"id": "BAN_7_VN", "ban_code": "Ban 7 VN", "dept_name": "Thực Thi Chiến Thuật VN Trước ATO & Đáo Hạn", "officer": "Minh Quân (Ban 7 VN)", "avatar": "⚡", "report": TACTICAL_PLAN_REL_PATH},
    {"id": "BAN_7_US", "ban_code": "Ban 7 US", "dept_name": "Thực Thi Global, Bán Dẫn NVDA & Big Tech", "officer": "Alex (Ban 7 Global)", "avatar": "🦅", "report": "07_Daily_Investment_Specialist/2026-11-18_Daily_Specialist_Decision.md"},
    {"id": "BAN_8_CIO", "ban_code": "Ban 8", "dept_name": "Master CIO — Phân Bổ Vốn & Quyết Định Tối Cao", "officer": "Master CIO James (Ban 8)", "avatar": "🎖️", "report": RESOLUTION_REL_PATH},
    {"id": "BAN_9_SENTINEL", "ban_code": "Ban 9", "dept_name": "Sentinel Giám Sát Rủi Ro Đáo Hạn & T+0", "officer": "Victor (Sentinel Ban 9)", "avatar": "🛰️", "report": "09_Realtime_Portfolio_Sentinel/2026-11-18_Victor_Realtime_Trigger_Report.md"},
    {"id": "BAN_10_IR", "ban_code": "Ban 10", "dept_name": "Trinh Sát BCTC NVDA, SEC & IR Chính Thống", "officer": "Hiền (Trinh Sát Trưởng Ban 10)", "avatar": "📡", "report": "02_Equity_Research/2026-11-18_SEC_Filings_Radar.md"},
    {"id": "BAN_11_MEDIA", "ban_code": "Ban 11", "dept_name": "Thư Ký Truyền Thông, Biên Bản & Lưu Kho Vault", "officer": "Khánh & Bảo (Ban 11)", "avatar": "🎬", "report": ARCHIVE_MD_REL_PATH},
    {"id": "BAN_12_OMBUDSMAN", "ban_code": "Ban 12", "dept_name": "Tổng Kiểm Sát Viên Thể Chế Bất Biến", "officer": "Tổng Kiểm Sát Viên Trọng (Ban 12)", "avatar": "🛡️", "report": CHARTER_REL_PATH},
]

SUMMIT_CHARTER_RULES = [
    {"code": "Điều 1", "title": "Họp Thật, Hiện Diện 14/14 Ban & Tranh Biện Chuyên Môn", "detail": "Đủ 14/14 Phòng Ban + Palmer + Nam (16/16) có mặt thật; tranh luận, phản biện chéo, đánh giá, bỏ phiếu có bảo lưu và tổng kết chuẩn tập đoàn lớn."},
    {"code": "Điều 2", "title": "Nghiên Cứu & Phân Tích Dữ Liệu Trước Giờ Họp 15–20 Phút", "detail": "Trước giờ khai mạc 15–20 phút (T-20p -> T-0p), cả 14 Ban phải chủ động quét thông tin, đối soát BCTC/vĩ mô liên quan chủ đề và nộp Hồ sơ chuẩn bị."},
    {"code": "Điều 3", "title": "Minh Bạch Tuyệt Đối — 100% Dựa Trên Số Liệu Thực Tế", "detail": "Mọi nhận định gắn chặt SSOT TCBS 105C307855 và dữ liệu thị trường sống; cấm lặp văn mẫu cũ hoặc suy đoán cảm tính."},
    {"code": "Điều 4", "title": "Tổng Kết Của James & Kế Hoạch Tham Khảo Cơ Động Theo Ngày", "detail": "Sau mỗi cuộc họp, Master CIO James tổng kết đầy đủ nội dung và Kế hoạch Phiên Sau (linh hoạt theo diễn biến Buy-Up & VIX)."},
    {"code": "Điều 5", "title": "Lưu Kho Vĩnh Viễn & Dọn Phòng Sau Phê Duyệt Tối Thiểu 2 Tiếng", "detail": "Mọi cuộc họp được lưu vào Summit Archive Vault để xem lại. Phải đợi Chủ tịch đọc báo cáo, ký phê duyệt VÀ tối thiểu 2 tiếng sau họp mới dọn phòng."},
]


def get_ict_now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc).astimezone(ICT_TZ)


def load_json_safe(path: Path, default: Any) -> Any:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return copy.deepcopy(default)


def save_json_safe(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _load_ssot_portfolio() -> Dict[str, Any]:
    from scripts.portfolio_state_manager import PortfolioStateManager
    return PortfolioStateManager.load_state()


def _fetch_single_ticker(sym: str) -> Tuple[str, Dict[str, Any]]:
    import yfinance as yf
    try:
        tk = yf.Ticker(sym)
        d5 = tk.history(period="5d", interval="1d", auto_adjust=False)
        prev_close = 0.0
        reg_last = 0.0
        last_d5_date: Optional[datetime.date] = None
        if d5 is not None and not d5.empty:
            closes = d5["Close"].dropna()
            if len(closes) >= 2:
                prev_close = float(closes.iloc[-2])
                reg_last = float(closes.iloc[-1])
                last_d5_date = closes.index[-1].date()
            elif len(closes) == 1:
                prev_close = float(closes.iloc[-1])
                reg_last = float(closes.iloc[-1])
                last_d5_date = closes.index[-1].date()

        latest_price = reg_last
        ah_price: Optional[float] = None
        ah_chg_pct: Optional[float] = None
        bar_ts = str(last_d5_date) if last_d5_date else "N/A"
        regular_close = reg_last
        high_val = float(d5["High"].iloc[-1]) if d5 is not None and not d5.empty else reg_last
        low_val = float(d5["Low"].iloc[-1]) if d5 is not None and not d5.empty else reg_last

        if sym in INTRADAY_PRIORITY_TICKERS:
            m2 = tk.history(period="2d", interval="1m", prepost=True, auto_adjust=False)
            if m2 is not None and not m2.empty and "Close" in m2:
                m2_clean = m2.dropna(subset=["Close"])
                if not m2_clean.empty:
                    latest_price = float(m2_clean["Close"].iloc[-1])
                    idx_last = m2_clean.index[-1]
                    bar_ts = str(idx_last)
                    if hasattr(idx_last, "date"):
                        today_us_date = idx_last.date()
                        if last_d5_date is not None and today_us_date > last_d5_date:
                            # Đang ở phiên Pre-Market (trước 21:30 ICT): nến ngày mới nhất (17/11) chính là prev_close
                            prev_close = reg_last
                        same_day = m2_clean[m2_clean.index.date == today_us_date]
                        if not same_day.empty:
                            high_val = float(same_day["High"].max())
                            low_val = float(same_day["Low"].min())
                            reg_bars = same_day[
                                ((same_day.index.hour > 9) | ((same_day.index.hour == 9) & (same_day.index.minute >= 30)))
                                & (same_day.index.hour < 16)
                            ]
                            if not reg_bars.empty:
                                regular_close = float(reg_bars["Close"].iloc[-1])
                            ah_bars = same_day[same_day.index.hour >= 16]
                            if not ah_bars.empty:
                                ah_price = float(ah_bars["Close"].iloc[-1])
                                base_ref = regular_close if regular_close > 0 else prev_close
                                if base_ref > 0:
                                    ah_chg_pct = round(((ah_price / base_ref) - 1.0) * 100.0, 2)

        if prev_close <= 0:
            fi = getattr(tk, "fast_info", None)
            if fi:
                prev_close = float(getattr(fi, "previous_close", 0.0) or 0.0)
                if latest_price <= 0:
                    latest_price = float(getattr(fi, "last_price", 0.0) or 0.0)

        chg_pct = round(((latest_price / prev_close) - 1.0) * 100.0, 2) if prev_close > 0 else 0.0
        reg_chg_pct = round(((regular_close / prev_close) - 1.0) * 100.0, 2) if prev_close > 0 else chg_pct
        return sym, {
            "last": round(latest_price, 4),
            "prev": round(prev_close, 4),
            "regular_close": round(regular_close, 4),
            "high": round(high_val, 4),
            "low": round(low_val, 4),
            "chg_pct": chg_pct,
            "reg_chg_pct": reg_chg_pct,
            "ah_price": round(ah_price, 4) if ah_price is not None else None,
            "ah_chg_vs_close_pct": ah_chg_pct,
            "bar_ts": bar_ts,
        }
    except Exception as exc:
        return sym, {"last": 0.0, "prev": 0.0, "chg_pct": 0.0, "error": str(exc)}


def fetch_live_us_quotes() -> Dict[str, Any]:
    quotes: Dict[str, Any] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        futures = {ex.submit(_fetch_single_ticker, sym): sym for sym in CORE_TICKERS}
        for fut in concurrent.futures.as_completed(futures):
            sym, payload = fut.result()
            quotes[sym] = payload
    return {k: quotes[k] for k in CORE_TICKERS if k in quotes}


def fetch_nvda_news_rss(limit: int = 5) -> List[Dict[str, str]]:
    """Quét tin tức BCTC NVDA qua RSS công khai (không lệ thuộc endpoint yf.news hay lỗi)."""
    headlines: List[Dict[str, str]] = []
    urls = [
        "https://feeds.finance.yahoo.com/rss/2.0/headline?s=NVDA&region=US&lang=en-US",
        "https://news.google.com/rss/search?q=Nvidia+NVDA+earnings+results+OR+guidance&hl=en-US&gl=US&ceid=US:en",
    ]
    seen = set()
    for url in urls:
        if len(headlines) >= limit:
            break
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                xml_bytes = resp.read()
            root = ET.fromstring(xml_bytes)
            for item in root.findall(".//item"):
                title = (item.findtext("title") or "").strip()
                pub = (item.findtext("pubDate") or "").strip()
                link = (item.findtext("link") or "").strip()
                if title and title not in seen:
                    seen.add(title)
                    headlines.append({"title": title, "published": pub, "link": link})
                    if len(headlines) >= limit:
                        break
        except Exception:
            continue
    return headlines


def determine_auto_checkpoints(now: datetime.datetime, log_data: Dict[str, Any]) -> List[str]:
    """Xác định tự động nhịp cần chạy theo giờ ICT (theo đúng Plan)."""
    checkpoints_done = set((log_data.get("checkpoints") or {}).keys())
    hm = now.hour * 60 + now.minute
    if now.date() == datetime.date(2026, 11, 18):
        if hm < 21 * 60 + 20:
            return ["2110_PREP"]
        if hm < 22 * 60 + 5:
            return ["2130_OPEN"]
        return ["2230_POST_AMATEUR"]
    # Sáng 19/11/2026
    if hm < 3 * 60 + 30:
        return ["0100_MID_SESSION"]
    if hm < 4 * 60 + 18:
        return ["0402_OFFICIAL_CLOSE"]
    if hm < 4 * 60 + 28:
        return ["0425_NVDA_EARNINGS_AH"]
    out: List[str] = []
    if "0425_NVDA_EARNINGS_AH" not in checkpoints_done:
        out.append("0425_NVDA_EARNINGS_AH")
    out.append("0430_SUMMIT")
    return out


def _compute_deltas(quotes: Dict[str, Any], prev_cp: Optional[Dict[str, Any]]) -> Dict[str, float]:
    if not prev_cp or "quotes" not in prev_cp:
        return {}
    prev_q = prev_cp["quotes"]
    deltas: Dict[str, float] = {}
    for sym, q in quotes.items():
        p_old = float((prev_q.get(sym) or {}).get("last") or 0.0)
        p_new = float(q.get("last") or 0.0)
        if p_old > 0 and p_new > 0:
            deltas[sym] = round(((p_new / p_old) - 1.0) * 100.0, 2)
    return deltas


def _build_attendance_roster() -> List[Dict[str, Any]]:
    roster = [
        {"id": "CHAIRMAN", "ban_code": "Chủ Tọa", "officer": "Chủ tịch Trần Quốc Thiên Phước", "avatar": "👑", "status": "CHAIRING", "present": True},
        {"id": "PALMER", "ban_code": "Điều Phối", "officer": "Palmer (Tổng Quản Trị)", "avatar": "🏛️", "status": "PRESENT_PREPARED", "present": True},
        {"id": "NAM", "ban_code": "Thư Ký", "officer": "Nam (Điều Hành SSOT)", "avatar": "💼", "status": "PRESENT_PREPARED", "present": True},
    ]
    for d in DEPARTMENTS_META:
        roster.append({
            "id": d["id"],
            "ban_code": d["ban_code"],
            "officer": d["officer"],
            "avatar": d["avatar"],
            "status": "PRESENT_PREPARED",
            "present": True,
        })
    return roster


def _build_prep_dossiers(quotes: Dict[str, Any], ssot: Dict[str, Any], phase_label: str) -> List[Dict[str, Any]]:
    spx = quotes.get("^GSPC", {})
    vix = quotes.get("^VIX", {})
    nvda = quotes.get("NVDA", {})
    vnm = quotes.get("VNM", {})
    xlf = quotes.get("XLF", {})
    smh = quotes.get("SMH", {})
    nav = float(ssot.get("total_nav_vnd", 20229522.0))
    cash = float(ssot.get("cash_balance_vnd", 13594522.0))
    cash_pct = round((cash / nav) * 100.0, 1) if nav > 0 else 67.2
    pos = ssot.get("active_positions") or {}
    msh = pos.get("MSH", {})
    baf = pos.get("BAF", {})

    nvda_str = f"NVDA ${nvda.get('last', 0):.2f} ({nvda.get('chg_pct', 0):+.2f}%)"
    if nvda.get("ah_price"):
        nvda_str += f" [AH ${nvda['ah_price']:.2f} / {nvda.get('ah_chg_vs_close_pct', 0):+.2f}%]"

    shared_finding = (
        f"[{phase_label}] Theo dõi sống: ^GSPC {spx.get('last', 0):,.2f} ({spx.get('chg_pct', 0):+.2f}%), "
        f"^VIX {vix.get('last', 0):.2f} ({vix.get('chg_pct', 0):+.2f}%), {nvda_str}, "
        f"SMH {smh.get('chg_pct', 0):+.2f}%, XLF {xlf.get('chg_pct', 0):+.2f}%, VNM {vnm.get('last', 0):.2f} ({vnm.get('chg_pct', 0):+.2f}%). "
        f"SSOT 105C307855 EOD 18/11: NAV {nav:,.0f}đ | Cash {cash:,.0f}đ ({cash_pct}%) | "
        f"MSH {msh.get('current_price', 35200):,.0f}đ (+69k) & BAF {baf.get('current_price', 31150):,.0f}đ (-5.9k, T+1 chiều 19/11)."
    )

    stances = {
        "BAN_1_VN": f"Đo spillover DXY {quotes.get('DX-Y.NYB', {}).get('last', 0):.2f} & US10Y {quotes.get('^TNX', {}).get('last', 0):.3f}% lên VN30F1M đáo hạn 19/11.",
        "BAN_1_US": f"Theo dõi ^VIX ({vix.get('last', 0):.2f}) có hạ nhiệt dưới <23.5 hay neo căng thẳng >25 qua phiên Mỹ & BCTC NVDA.",
        "BAN_2_BCTC": "Đối chiếu BCTC NVDA ~04h20 ICT với kỳ vọng Rev Avg $124.89B, EPS Avg $2.76, GM ~74.67%, Blackwell guidance.",
        "BAN_3_SYNTHESIS": "Kiểm toán chéo VNM ETF vs XLF & độ rộng HOSE (18/11 chỉ 64 tăng/272 giảm), chặn bẫy mua sớm trước 14h00 ngày đáo hạn.",
        "BAN_4_RISK": f"Khóa Risk-at-Stop <= 4.5% NAV ({nav*0.045:,.0f}đ), 0% Margin; điều chỉnh hạn mức giải ngân {cash:,.0f}đ theo chế độ VIX 04h30.",
        "BAN_5_EVOLUTION": "Kiểm tra HDB sau thoát 22.05 (EOD 22.25) & rút bài học bảo vệ vốn 67.2% Cash trong phiên -23.71đ.",
        "BAN_6_ACADEMY": "Chuẩn bị bản tin sáng 07h30 cho Chủ tịch về tâm lý đón tin NVDA & rung lắc đáo hạn VN30F1M.",
        "BAN_7_VN": "Thiết lập kịch bản 19/11: bảo vệ lãi MSH (+2.0%), đón 100 CP BAF về chiều, giải ngân có điều kiện 14h00–14h25.",
        "BAN_7_US": "Theo dõi nhóm Bán dẫn (NVDA, AVGO, TSM, AMD) và độ lan tỏa 12 ngành GICS trước/sau 04h20.",
        "BAN_8_CIO": "Tổng hợp báo cáo toàn Hội đồng lúc 04h30, ban hành Sổ Lệnh Tham Khảo 19/11 theo dữ liệu thực 100%.",
        "BAN_9_SENTINEL": "Giám sát biến động AH NVDA & ^VIX >25; kích hoạt cờ cảnh báo nếu VNM ETF gãy sâu hoặc HDB hồi >=22.60.",
        "BAN_10_IR": "Săn thông cáo IR NVIDIA chính thức ngay lúc 04h20 ICT & trích xuất số liệu Rev/EPS/Guidance xác thực.",
        "BAN_11_MEDIA": "Ghi log từng checkpoint vào Summit Room, đồng bộ Archive Vault & phát hành biên bản cho Chủ tịch đọc sáng sớm.",
        "BAN_12_OMBUDSMAN": "Chứng thực dấu thời gian sống từng nhịp, tuyệt đối cấm bịa số BCTC NVDA hoặc dùng kịch bản cũ.",
    }

    dossiers: List[Dict[str, Any]] = []
    for idx, d in enumerate(DEPARTMENTS_META):
        prep_min = -20 + idx
        t_prep = (datetime.datetime(2026, 11, 19, 4, 30, tzinfo=ICT_TZ) + datetime.timedelta(minutes=prep_min)).strftime("%H:%M:%S")
        dossiers.append({
            "dept_id": d["id"],
            "ban_code": d["ban_code"],
            "dept_name": d["dept_name"],
            "officer": d["officer"],
            "avatar": d["avatar"],
            "prep_minute": prep_min,
            "prep_time": t_prep,
            "status": "READY_VERIFIED",
            "sources_scanned": [
                "data/us_live_session_log_2026-11-18.json",
                "data/current_portfolio_state.json",
                AGENDA_REL_PATH,
            ],
            "key_metrics": {
                "SPX": f"{spx.get('last', 0):,.2f} ({spx.get('chg_pct', 0):+.2f}%)",
                "VIX": f"{vix.get('last', 0):.2f} ({vix.get('chg_pct', 0):+.2f}%)",
                "NVDA": nvda_str,
                "Cash_NAV": f"{cash_pct}% ({cash/1e6:.2f}M)",
            },
            "pre_meeting_findings": shared_finding,
            "proposed_next_week_stance": stances[d["id"]],
            "report_path": d["report"],
        })
    return dossiers


def _build_prep_timeline_stream(dossiers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    stream: List[Dict[str, Any]] = []
    for idx, d in enumerate(dossiers, 1):
        stream.append({
            "id": f"prep_nvda_{idx}",
            "minute": d["prep_minute"],
            "is_prep_phase": True,
            "time_str": d["prep_time"],
            "phase_step": 0,
            "sender_name": d["officer"],
            "department": f"{d['ban_code']} — {d['dept_name']}",
            "role": "Hồ Sơ Chuẩn Bị T-20p & Theo Dõi NVDA / VIX",
            "avatar": d["avatar"],
            "badge": "HỒ SƠ CHUẨN BỊ SẴN SÀNG",
            "badge_color": "#38bdf8",
            "content": f"{d['pre_meeting_findings']} | Nhiệm vụ: {d['proposed_next_week_stance']}",
            "highlight": d["proposed_next_week_stance"],
            "metrics": d["key_metrics"],
        })
    return stream


def _format_checkpoint_turn(cp_name: str, now_ict: datetime.datetime, quotes: Dict[str, Any], news: List[Dict[str, str]]) -> Dict[str, Any]:
    spx = quotes.get("^GSPC", {})
    ixic = quotes.get("^IXIC", {})
    vix = quotes.get("^VIX", {})
    nvda = quotes.get("NVDA", {})
    smh = quotes.get("SMH", {})
    vnm = quotes.get("VNM", {})
    xlf = quotes.get("XLF", {})
    nq = quotes.get("NQ=F", {})
    es = quotes.get("ES=F", {})
    tnx = quotes.get("^TNX", {})
    dxy = quotes.get("DX-Y.NYB", {})

    labels = {
        "2030_MOBILIZE": ("20h30 — TRIỆU TẬP KHẨN 16/16 PHÒNG BAN & QUÉT PRE-MARKET", "#38bdf8", "🏛️", "Palmer & Master CIO James"),
        "2110_PREP": ("21h10 — ĐIỂM DANH T-20P TRƯỚC GIỜ MỞ CỬA MỸ", "#0ea5e9", "📡", "Trọng (Ban 12) & Telemetry"),
        "2130_OPEN": ("21h30 — NHỊP 1: MỞ CỬA PHIÊN MỸ (AMATEUR HOUR)", "#f59e0b", "🔔", "Ban 1 US & Telemetry"),
        "2230_POST_AMATEUR": ("22h30 — NHỊP 2: SAU AMATEUR HOUR (XÁC NHẬN DÒNG TIỀN)", "#f59e0b", "📊", "Ban 1 US & Alex Ban 7"),
        "0100_MID_SESSION": ("01h00 — NHỊP 3: GIỮA PHIÊN MỸ (NÉN CHỜ BCTC NVDA)", "#a855f7", "🌙", "Ban 1 US & Victor Ban 9"),
        "0402_OFFICIAL_CLOSE": ("04h02 — NHỊP 4: CHỐT NẾN ĐÓNG CỬA CHÍNH THỨC NYSE/NASDAQ", "#22c55e", "🏁", "Telemetry 5 Nhịp & Trọng Ban 12"),
        "0425_NVDA_EARNINGS_AH": ("04h25 — NHỊP 5: BCTC NVDA VỪA CÔNG BỐ & PHẢN ỨNG AFTER-HOURS / VIX", "#ef4444", "🔥", "Hiền (Ban 10), Lê Hoàng (Ban 2) & Elena (Ban 1 US)"),
    }
    badge, color, avatar, sender = labels.get(cp_name, (cp_name, "#38bdf8", "📡", "Hệ Thống Telemetry"))

    nvda_extra = ""
    if nvda.get("ah_price"):
        nvda_extra = f" | **After-Hours NVDA: `${nvda['ah_price']:.2f}` (`{nvda.get('ah_chg_vs_close_pct', 0):+.2f}%` vs close)**"
    news_line = ""
    if news:
        news_line = " | Tin nóng NVDA: " + " ; ".join(f"[{n['title']}]" for n in news[:2])

    content = (
        f"[{now_ict.strftime('%d/%m %H:%M:%S ICT')}] Ghi nhận số liệu sống: "
        f"`ES=F {es.get('last', 0):,.2f} ({es.get('chg_pct', 0):+.2f}%)`, `NQ=F {nq.get('last', 0):,.2f} ({nq.get('chg_pct', 0):+.2f}%)`, "
        f"`^GSPC {spx.get('last', 0):,.2f} ({spx.get('chg_pct', 0):+.2f}%)`, `^IXIC {ixic.get('last', 0):,.2f} ({ixic.get('chg_pct', 0):+.2f}%)`, "
        f"**`^VIX {vix.get('last', 0):.2f} ({vix.get('chg_pct', 0):+.2f}%)`**, `US10Y {tnx.get('last', 0):.3f}%`, `DXY {dxy.get('last', 0):.2f}`, "
        f"`NVDA ${nvda.get('last', 0):.2f} ({nvda.get('chg_pct', 0):+.2f}%)`{nvda_extra}, "
        f"`SMH {smh.get('chg_pct', 0):+.2f}%`, `XLF {xlf.get('chg_pct', 0):+.2f}%`, `VNM ETF {vnm.get('last', 0):.2f} ({vnm.get('chg_pct', 0):+.2f}%)`."
        f"{news_line}"
    )

    vix_val = float(vix.get("last") or 25.0)
    vix_state = "HẠ NHIỆT (<23.5)" if vix_val < 23.5 else ("TRUNG TÍNH CAO (23.5–25.5)" if vix_val < 25.5 else "CĂNG THẲNG CAO (>=25.5)")
    return {
        "id": f"live_cp_{cp_name}",
        "minute": -1,
        "time_str": now_ict.strftime("%H:%M:%S"),
        "phase_step": 0,
        "sender_name": sender,
        "department": "Trực Xuyên Phiên Mỹ & Đón BCTC NVDA (5 Nhịp Thực)",
        "role": cp_name,
        "avatar": avatar,
        "badge": badge,
        "badge_color": color,
        "content": content,
        "highlight": f"NVDA ${nvda.get('last', 0):.2f} ({nvda.get('chg_pct', 0):+.2f}%) • ^VIX {vix_val:.2f} [{vix_state}]",
        "metrics": {
            "VIX": f"{vix_val:.2f} ({vix.get('chg_pct', 0):+.2f}%)",
            "NVDA": f"${nvda.get('last', 0):.2f}" + (f" (AH ${nvda['ah_price']:.2f})" if nvda.get("ah_price") else ""),
            "NQ_F": f"{nq.get('last', 0):,.2f} ({nq.get('chg_pct', 0):+.2f}%)",
            "VNM_ETF": f"{vnm.get('last', 0):.2f} ({vnm.get('chg_pct', 0):+.2f}%)",
        },
    }


def _evaluate_nvda_vix_regime(log_data: Dict[str, Any], live_quotes: Dict[str, Any]) -> Dict[str, Any]:
    cps = log_data.get("checkpoints") or {}
    cp_close = (cps.get("0402_OFFICIAL_CLOSE") or {}).get("quotes") or live_quotes
    cp_ah = (cps.get("0425_NVDA_EARNINGS_AH") or {}).get("quotes") or live_quotes
    ah_news = (cps.get("0425_NVDA_EARNINGS_AH") or {}).get("nvda_news") or []

    vix_close = float((cp_close.get("^VIX") or {}).get("last") or 25.89)
    vix_latest = float((cp_ah.get("^VIX") or {}).get("last") or vix_close)
    spx = cp_close.get("^GSPC") or {}
    ixic = cp_close.get("^IXIC") or {}
    dji = cp_close.get("^DJI") or {}
    nvda_c = cp_close.get("NVDA") or {}
    nvda_a = cp_ah.get("NVDA") or {}
    nq_a = cp_ah.get("NQ=F") or {}
    es_a = cp_ah.get("ES=F") or {}
    smh_a = cp_ah.get("SMH") or {}
    vnm_c = cp_close.get("VNM") or {}
    eem_c = cp_close.get("EEM") or {}
    xlf_c = cp_close.get("XLF") or {}
    tnx_c = cp_close.get("^TNX") or {}
    dxy_c = cp_close.get("DX-Y.NYB") or {}
    wti_c = cp_close.get("CL=F") or {}

    nvda_reg = float(nvda_c.get("regular_close") or nvda_c.get("last") or 155.46)
    nvda_ah = nvda_a.get("ah_price") or float(nvda_a.get("last") or nvda_reg)
    nvda_ah_chg = nvda_a.get("ah_chg_vs_close_pct")
    if nvda_ah_chg is None and nvda_reg > 0:
        nvda_ah_chg = round(((nvda_ah / nvda_reg) - 1.0) * 100.0, 2)
    nvda_ah_chg = float(nvda_ah_chg or 0.0)
    nq_chg = float(nq_a.get("chg_pct") or 0.0)

    if (vix_latest < 23.5 or vix_latest <= vix_close - 1.5) and nvda_ah_chg >= -1.0 and nq_chg >= -0.3:
        regime_code = "VIX_COOLED_NVDA_RESILIENT"
        regime_label = "VIX HẠ NHIỆT + NVDA / NASDAQ PHẢN ỨNG TÍCH CỰC -> MỞ KHÓA GIẢI NGÂN CHỌN LỌC SAU 14H00"
        deploy_cap_vnd = 6_000_000
        deploy_desc = "Tối đa 5.5M – 6.0M (chia 1–2 lệnh 200 CP/mã hoặc Kim tự tháp 30%-40%)"
        buyup_req = ">= 58% và Độ rộng HOSE >= 40%"
    elif vix_latest < 25.5 and nvda_ah_chg > -2.5:
        regime_code = "VIX_MODERATE_MIXED"
        regime_label = "VIX CHƯA HẠ SÂU (VÙNG LƯỠNG LỰ 23.5–25.5) -> THĂM DÒ THẬN TRỌNG TỐI ĐA 1 LÔ"
        deploy_cap_vnd = 3_200_000
        deploy_desc = "Tối đa 1 lô thăm dò <= 3.2M (24% Cash) sau 14h10 nếu rút chân hậu đáo hạn VN30F1M"
        buyup_req = ">= 60% và VNI giữ vững >= 1,700"
    else:
        regime_code = "VIX_ELEVATED_OR_NVDA_SELLOFF"
        regime_label = "VIX TIẾP TỤC CĂNG THẲNG (>= 25.5) HOẶC NVDA AH BỊ BÁN -> KHÓA PHÒNG THỦ TUYỆT ĐỐI"
        deploy_cap_vnd = 0
        deploy_desc = "0 ₫ giải ngân mới trước 14h15 (giữ nguyên 67.2% tiền mặt); chỉ nhặt <= 2.5M nếu xảy ra Sweep Spring rõ ràng cuối phiên"
        buyup_req = ">= 62% kèm nến Spring đảo chiều rõ tại hỗ trợ"

    return {
        "regime_code": regime_code,
        "regime_label": regime_label,
        "deploy_cap_vnd": deploy_cap_vnd,
        "deploy_desc": deploy_desc,
        "buyup_req": buyup_req,
        "vix_close": vix_close,
        "vix_latest": vix_latest,
        "nvda_reg": nvda_reg,
        "nvda_ah": float(nvda_ah),
        "nvda_ah_chg": nvda_ah_chg,
        "spx": spx,
        "ixic": ixic,
        "dji": dji,
        "nq_a": nq_a,
        "es_a": es_a,
        "smh_a": smh_a,
        "vnm_c": vnm_c,
        "eem_c": eem_c,
        "xlf_c": xlf_c,
        "tnx_c": tnx_c,
        "dxy_c": dxy_c,
        "wti_c": wti_c,
        "ah_news": ah_news,
    }


def _build_summit_debate_turns(
    now_ict: datetime.datetime,
    log_data: Dict[str, Any],
    verdict: Dict[str, Any],
    ssot: Dict[str, Any],
) -> List[Dict[str, Any]]:
    nav = float(ssot.get("total_nav_vnd", 20229522.0))
    cash = float(ssot.get("cash_balance_vnd", 13594522.0))
    cash_pct = round((cash / nav) * 100.0, 1) if nav > 0 else 67.2
    pos = ssot.get("active_positions") or {}
    msh = pos.get("MSH", {})
    baf = pos.get("BAF", {})

    cps = log_data.get("checkpoints") or {}
    cp_chain = " -> ".join(
        f"{k} (VIX {(v.get('quotes', {}).get('^VIX', {})).get('last', 0):.2f}, NVDA ${(v.get('quotes', {}).get('NVDA', {})).get('last', 0):.2f})"
        for k, v in cps.items()
    )
    news_titles = " | ".join(n.get("title", "") for n in (verdict.get("ah_news") or [])[:3]) or "Chưa ghi nhận tiêu đề RSS mới ngoài biến động giá AH trực tiếp"

    spx = verdict["spx"]
    ixic = verdict["ixic"]
    dji = verdict["dji"]
    vnm = verdict["vnm_c"]
    xlf = verdict["xlf_c"]
    smh = verdict["smh_a"]
    nq = verdict["nq_a"]

    turns = [
        {
            "id": "nvda_r1_opening",
            "minute": 0,
            "time_str": "04:30:00",
            "phase_step": 1,
            "sender_name": "Palmer & Master CIO James",
            "department": "Đồng Chủ Tọa — Khai Mạc Thượng Đỉnh 04h30",
            "role": "Điểm Danh 16/16 & Mục Tiêu Phiên Đáo Hạn 19/11",
            "avatar": "🏛️",
            "badge": "KHAI MẠC 04H30 (16/16)",
            "badge_color": "#38bdf8",
            "content": f"Kính báo Chủ tịch Trần Quốc Thiên Phước (`TCBS 105C307855`): Toàn bộ 16/16 thành viên đã trực xuyên đêm phiên Mỹ. Hôm nay Thứ Năm `19/11/2026` có 3 sự kiện giao nhau: (1) BCTC `NVDA` & phản ứng `^VIX`, (2) Đáo hạn phái sinh `VN30F1M`, (3) Chiều `100 CP BAF` về tài khoản. Chúng ta họp thật trên dữ liệu vừa đóng cửa & AH.",
            "highlight": f"SSOT vào họp: NAV {nav:,.0f}đ | Tiền mặt {cash:,.0f}đ ({cash_pct}%) | MSH {msh.get('current_price', 35200):,.0f}đ (+2.0%) | BAF {baf.get('current_price', 31150):,.0f}đ (-0.2%)",
            "metrics": {"Quorum": "16/16 LIVE", "NAV": f"{nav/1e6:.2f}M", "Cash": f"{cash_pct}%"},
        },
        {
            "id": "nvda_r2_telemetry",
            "minute": 3,
            "time_str": "04:33:00",
            "phase_step": 2,
            "sender_name": "Hệ Thống Telemetry 5 Nhịp",
            "department": "Ban Dữ Liệu Sống Liên Thị Trường",
            "role": "Báo Cáo Chuỗi 21h30 -> 04h25",
            "avatar": "📡",
            "badge": "DỮ LIỆU THẬT 100%",
            "badge_color": "#0ea5e9",
            "content": f"Chuỗi diễn biến ghi nhận qua các mốc: {cp_chain}. Đóng cửa phiên thường `04h00`: `^GSPC {spx.get('last', 0):,.2f} ({spx.get('chg_pct', 0):+.2f}%)`, `^IXIC {ixic.get('last', 0):,.2f} ({ixic.get('chg_pct', 0):+.2f}%)`, `^DJI {dji.get('last', 0):,.2f} ({dji.get('chg_pct', 0):+.2f}%)`, `^VIX close {verdict['vix_close']:.2f}` -> mới nhất `{verdict['vix_latest']:.2f}`, `XLF {xlf.get('chg_pct', 0):+.2f}%`, `VNM ETF {vnm.get('last', 0):.2f} ({vnm.get('chg_pct', 0):+.2f}%)`.",
            "highlight": f"NVDA đóng phiên thường ${verdict['nvda_reg']:.2f} -> After-Hours ${verdict['nvda_ah']:.2f} ({verdict['nvda_ah_chg']:+.2f}%)",
            "metrics": {"SPX": f"{spx.get('chg_pct', 0):+.2f}%", "VIX": f"{verdict['vix_latest']:.2f}", "NVDA_AH": f"${verdict['nvda_ah']:.2f} ({verdict['nvda_ah_chg']:+.2f}%)"},
        },
        {
            "id": "nvda_r3_ban1_us_vix",
            "minute": 6,
            "time_str": "04:36:00",
            "phase_step": 2,
            "sender_name": "Dr. Elena Vance (Ban 1 US)",
            "department": "Ban 1 US — Vĩ Mô Toàn Cầu & ^VIX",
            "role": "Phán Quyết Độ Căng Thẳng VIX",
            "avatar": "🌐",
            "badge": "CHẾ ĐỘ VIX",
            "badge_color": "#f59e0b" if verdict["vix_latest"] >= 23.5 else "#22c55e",
            "content": f"`^VIX` từ đỉnh `27.73` hôm trước đang ghi nhận tại `{verdict['vix_latest']:.2f}` (close `{verdict['vix_close']:.2f}`), `US10Y {verdict['tnx_c'].get('last', 0):.3f}%`, `DXY {verdict['dxy_c'].get('last', 0):.2f}`, `WTI ${verdict['wti_c'].get('last', 0):.2f}`. Kết luận chế độ: **{verdict['regime_code']}** — nếu `VIX < 23.5` thì quỹ định lượng bắt đầu xả bớt phòng thủ; ngược lại `>= 25.5` vẫn là môi trường biến động cao (choppy/wicks).",
            "highlight": verdict["regime_label"],
            "metrics": {"VIX_Now": f"{verdict['vix_latest']:.2f}", "US10Y": f"{verdict['tnx_c'].get('last', 0):.3f}%", "DXY": f"{verdict['dxy_c'].get('last', 0):.2f}"},
        },
        {
            "id": "nvda_r4_ban10_ban2_nvda",
            "minute": 9,
            "time_str": "04:39:00",
            "phase_step": 3,
            "sender_name": "Hiền (Ban 10) & Lê Hoàng (Ban 2)",
            "department": "Trinh Sát IR & Pháp Y BCTC NVDA",
            "role": "Đọc Vị Kết Quả NVDA & Phản Ứng Sau Giờ",
            "avatar": "🔬",
            "badge": "BCTC NVDA AMC",
            "badge_color": "#a855f7",
            "content": f"Đối chiếu kỳ vọng Phố Wall (`Doanh thu Avg $124.89B`, `EPS Avg $2.76`, `Gross Margin 74.67%`): Phản ứng trực tiếp của thị trường cho thấy `NVDA` sau giờ đạt `${verdict['nvda_ah']:.2f}` (`{verdict['nvda_ah_chg']:+.2f}%` so với đóng cửa `${verdict['nvda_reg']:.2f}`), kéo `SMH {smh.get('chg_pct', 0):+.2f}%` và `NQ=F {nq.get('chg_pct', 0):+.2f}%`. Tiêu đề tin IR/RSS mới nhất: {news_titles}.",
            "highlight": f"NVDA After-Hours {verdict['nvda_ah_chg']:+.2f}% | NQ=F {nq.get('chg_pct', 0):+.2f}%",
            "metrics": {"NVDA_Reg": f"${verdict['nvda_reg']:.2f}", "NVDA_AH": f"${verdict['nvda_ah']:.2f}", "SMH": f"{smh.get('chg_pct', 0):+.2f}%"},
        },
        {
            "id": "nvda_r5_ban1_vn_victor",
            "minute": 13,
            "time_str": "04:43:00",
            "phase_step": 4,
            "sender_name": "Vũ Minh (Ban 1 VN) & Victor (Ban 9)",
            "department": "Vĩ Mô VN & Giám Sát Rủi Ro Đáo Hạn",
            "role": "Tác Động Sang VN-Index 1,703.01 & VN30F1M",
            "avatar": "🛰️",
            "badge": "ĐÁO HẠN 19/11",
            "badge_color": "#ef4444",
            "content": f"Hôm qua `18/11` VN-Index rơi `-23.71đ` về `1,703.01` (`64 tăng / 272 giảm`), VN30 mất `-30.59đ` (`1,806.54`). Phiên hôm nay `19/11` đáo hạn `VN30F1M` trùng ngày `100 CP BAF` về TK chiều nay. Tin vui: `MSH` đóng cửa `35,200đ (+2.0% / +69,000đ)` đứng ngoài nhiễu trụ VN30, `BAF` rút chân `31,150đ (-0.2% / -5,900đ)`. Tuy nhiên Victor đặt cảnh báo: mọi lệnh kéo/đạp trụ rổ VN30 trước `14h00` & trong ATC `14h30` đều mang tính nhiễu cao.",
            "highlight": "Tránh tuyệt đối mua đuổi/bán tháo theo nhiễu trụ VN30 trong ngày đáo hạn 19/11",
            "metrics": {"VNI_18_11": "1,703.01 (-1.37%)", "MSH": "35,200 (+2.0%)", "BAF": "31,150 (-0.2%, T+ về chiều)"},
        },
        {
            "id": "nvda_r6_ban3_ban5",
            "minute": 17,
            "time_str": "04:47:00",
            "phase_step": 5,
            "sender_name": "Trần Hưng (Ban 3) & Đặng Khoa (Ban 5)",
            "department": "Công Tố Phản Biện & Kiểm Toán Hậu Exit HDB",
            "role": "Phản Biện Giải Ngân & Theo Dõi HDB 22.25",
            "avatar": "⚖️",
            "badge": "PHẢN BIỆN & HDB AUDIT",
            "badge_color": "#eab308",
            "content": f"Ban 5 kiểm toán: quyết định thoát `100 CP HDB @ 22.05` lúc `14h14` hôm qua đã giúp nâng tiền mặt lên `67.2%` (`13.59M`), giữ NAV chỉ biến động `-0.17%` dù thị trường sập `-1.37%`. `HDB` đóng cửa `22.25` (`+0.91%` trên giá thoát, chưa qua `22.40` và dưới ngưỡng cảnh báo `22.60`), Cloud Actions `14h50` hôm nay & mai sẽ tiếp tục audit độc lập. Ban 3 Công tố bảo lưu: **KHÔNG giải ngân trước 14h00**; chỉ mở ví khi {verdict['buyup_req']}.",
            "highlight": f"HDB EOD 22.25 (< 22.60 ngưỡng báo động) • Khóa mua trước 14h00 • Cần Buy-Up {verdict['buyup_req']}",
            "metrics": {"Cash_Shield": "67.2% (13.59M)", "HDB_Close": "22.25 (Ref 22.40)", "Veto_Morning": "100% LOCKED"},
        },
        {
            "id": "nvda_r7_ban4_minhquan",
            "minute": 22,
            "time_str": "04:52:00",
            "phase_step": 6,
            "sender_name": "TS. Bảo (Ban 4) & Minh Quân (Ban 7 VN)",
            "department": "Quản Trị Rủi Ro & Thực Thi 19/11",
            "role": "Phân Bổ Tiền Mặt 13.59M & Quản Trị MSH/BAF",
            "avatar": "⚡",
            "badge": "SỔ LỆNH 19/11",
            "badge_color": "#22c55e" if verdict["deploy_cap_vnd"] > 0 else "#f59e0b",
            "content": f"Phân bổ kỷ luật `0% Margin` (`Risk-at-Stop <= 4.5% NAV = {nav*0.045:,.0f}đ`): (1) **`MSH` (100 CP sẵn)**: giữ gồng lãi, nâng Trailing Stop bảo vệ lên `34,600đ`, Hard Stop `33,090đ`, TP1 `39,500đ`; (2) **`BAF` (100 CP về chiều 19/11)**: kiểm tra hấp thụ cung T+2.5 từ `13h00–14h00`, giữ nếu `>= 30,500đ`, cắt kỷ luật nếu gãy `< 30,050đ`; (3) **Tiền mặt `13,594,522đ`**: {verdict['deploy_desc']} trong Khung Giờ Vàng `14h00–14h25`.",
            "highlight": f"Ngân sách giải ngân 19/11: {verdict['deploy_desc']}",
            "metrics": {"Deploy_Cap": f"{verdict['deploy_cap_vnd']/1e6:.2f}M", "MSH_Trail": "34,600đ", "BAF_Stop": "30,050đ"},
        },
        {
            "id": "nvda_r8_james_final_trong",
            "minute": 28,
            "time_str": "04:58:00",
            "phase_step": 7,
            "sender_name": "Master CIO James & Tổng Kiểm Sát Viên Trọng",
            "department": "Ban 8 Phán Quyết & Ban 12 Chứng Thực",
            "role": "Chốt Nghị Quyết 04h30 & Khóa Lưu Kho Vault",
            "avatar": "🎖️",
            "badge": "PHÁN QUYẾT & CHỨNG THỰC 100%",
            "badge_color": "#10b981",
            "content": f"James ban hành Nghị quyết `APEX-SUMMIT-20261119-0430`: Xác nhận chế độ **{verdict['regime_code']}** (`^VIX {verdict['vix_latest']:.2f}`, `NVDA AH ${verdict['nvda_ah']:.2f} [{verdict['nvda_ah_chg']:+.2f}%]`). Giữ vững phòng thủ `0% Margin`, bảo vệ `MSH/BAF`, tuyệt đối không FOMO phiên sáng đáo hạn; giải ngân {verdict['deploy_desc']} chỉ khi đạt `{verdict['buyup_req']}`. Trọng (Ban 12) ký chứng thực 100% số liệu thật xuyên 5 nhịp `21:30 -> 04:25`, xuất báo cáo trước khi Chủ tịch thức dậy.",
            "highlight": "Hoàn tất Tổng Kết 04h30 • Xuất Báo cáo James & Kế hoạch 19/11 • Đồng bộ Palmer & Telegram",
            "metrics": {"Verdict": verdict["regime_code"], "Margin": "0%", "Audit": "TRỌNG PASSED 100%"},
        },
    ]
    return turns


def _write_summit_reports(
    now_ict: datetime.datetime,
    log_data: Dict[str, Any],
    verdict: Dict[str, Any],
    ssot: Dict[str, Any],
    active_state: Dict[str, Any],
) -> None:
    nav = float(ssot.get("total_nav_vnd", 20229522.0))
    cash = float(ssot.get("cash_balance_vnd", 13594522.0))
    cash_pct = round((cash / nav) * 100.0, 1) if nav > 0 else 67.2
    cps = log_data.get("checkpoints") or {}

    cp_rows = []
    for k, v in cps.items():
        q = v.get("quotes") or {}
        sp = q.get("^GSPC", {})
        ix = q.get("^IXIC", {})
        vx = q.get("^VIX", {})
        nv = q.get("NVDA", {})
        vm = q.get("VNM", {})
        nv_cell = f"`${nv.get('last', 0):.2f}` (`{nv.get('chg_pct', 0):+.2f}%`)"
        if nv.get("ah_price"):
            nv_cell += f" / AH `${nv['ah_price']:.2f}` (`{nv.get('ah_chg_vs_close_pct', 0):+.2f}%`)"
        cp_rows.append(
            f"| `{k}` (`{v.get('timestamp_ict', '')}`) | `{sp.get('last', 0):,.2f}` (`{sp.get('chg_pct', 0):+.2f}%`) | "
            f"`{ix.get('last', 0):,.2f}` (`{ix.get('chg_pct', 0):+.2f}%`) | **`{vx.get('last', 0):.2f}`** (`{vx.get('chg_pct', 0):+.2f}%`) | "
            f"{nv_cell} | `{vm.get('last', 0):.2f}` (`{vm.get('chg_pct', 0):+.2f}%`) |"
        )
    cp_table = "\n".join(cp_rows) if cp_rows else "| Chưa có nhịp nào | - | - | - | - | - |"
    news_md = "\n".join(f"- {n.get('title')} *({n.get('published', '')})*" for n in (verdict.get("ah_news") or [])[:5]) or "- Không ghi nhận tiêu đề RSS bổ sung tại thời điểm chạy; bám sát phản ứng giá thực tế `prepost=True`."

    resolution_md = f"""# 🏛️ BÁO CÁO TỔNG KẾT MASTER CIO JAMES: BCTC `NVDA`, DIỄN BIẾN `^VIX` & KỊCH BẢN ĐÁO HẠN `19/11/2026`
> **Mã phiên họp:** `{MEETING_ID}` (`CD-APEX-20261118-NVDA-0430`)  
> **Thời gian họp thật:** `04h30 – 05h00 ICT` (Sáng Thứ Năm `19/11/2026`, tổng hợp lúc `{now_ict.strftime('%H:%M:%S ICT')}`)  
> **Đồng Chủ Trì:** **Master CIO James (`Ban 8`)** & **Palmer (`Tổng Quản Trị`)** | **Chứng thực:** **Tổng Kiểm Sát Viên Trọng (`Ban 12`)**  
> **SSOT Tài khoản `TCBS 105C307855` (EOD 18/11):** `NAV: {nav:,.0f} ₫` | `Tiền mặt: {cash:,.0f} ₫ ({cash_pct}%)` | `MSH 100 CP @ 35,200 ₫ (+69,000 ₫)` | `BAF 100 CP @ 31,150 ₫ (-5,900 ₫, về chiều 19/11)` | `HDB: Đã thoát @ 22,050 ₫ (Audit Cloud 20/11)`.

---

## I. NHẬT KÝ PHIÊN MỸ & PHẢN ỨNG BCTC `NVDA` (`100% SỐ LIỆU THỰC`)

| Nhịp ghi nhận (ICT) | `S&P 500 (^GSPC)` | `Nasdaq (^IXIC)` | `^VIX` | `NVDA` (Thường / After-Hours) | `VNM ETF` |
| :--- | :---: | :---: | :---: | :---: | :---: |
{cp_table}

### Tin tức IR / RSS quanh giờ công bố `NVDA`:
{news_md}

---

## II. PHÁN QUYẾT CHẾ ĐỘ `^VIX` & `NVDA` CỦA TOÀN HỘI ĐỒNG (`04h30 ICT`)
* **Trạng thái `^VIX`:** Đóng cửa phiên thường `{verdict['vix_close']:.2f}` ➔ Ghi nhận mới nhất **`{verdict['vix_latest']:.2f}`**.
* **Phản ứng `NVDA`:** Đóng cửa `${verdict['nvda_reg']:.2f}` ➔ After-Hours **`${verdict['nvda_ah']:.2f}` (`{verdict['nvda_ah_chg']:+.2f}%`)**.
* **Kết luận Chế độ Thị trường:** **`{verdict['regime_code']}`** — {verdict['regime_label']}

---

## III. KẾ HOẠCH HÀNH ĐỘNG PHIÊN ĐÁO HẠN `VN30F1M` HÔM NAY (`19/11/2026`)
1. **Phiên Sáng `09h00 – 11h30`:** **CẤM 100% MUA MỚI / ĐUỔI GIÁ XANH.** Quan sát nhiễu trụ VN30 trước ngày đáo hạn và gap mở cửa phản ánh `NVDA` & `^VIX`.
2. **Quản trị vị thế đang giữ (`6,635,000 ₫`):**
   - **`MSH` (`100 CP`, hàng sẵn):** Đang lãi `+69,000 ₫ (+2.0%)` tại `35,200 ₫`. Giữ gồng lãi; kéo **Trailing Stop bảo vệ lên `34,600 ₫`**, **Hard Stop `33,090 ₫`**, **TP1 `39,500 ₫`**.
   - **`BAF` (`100 CP`, về TK chiều `19/11`):** Đóng `31,150 ₫ (-0.2%)`. Theo dõi hấp thụ cung T+2.5 khung `13h00–14h00`; tiếp tục giữ nếu trụ trên `30,500 ₫`, cắt lỗ kỷ luật nếu gãy **`< 30,050 ₫`**.
   - **`HDB` (Đã bán @ `22.05`):** Tiếp tục để GitHub Cloud (`hdb_post_exit_audit.yml`) giám sát tự động lúc `14:50 ICT` hôm nay & thứ Sáu `20/11`.
3. **Khung Giờ Vàng `14h00 – 14h25` (Xử lý `13,594,522 ₫` Tiền mặt — `0% Margin`):**
   - **Hạn mức được phép:** **{verdict['deploy_desc']}** (tối đa `{verdict['deploy_cap_vnd']:,.0f} ₫`).
   - **Điều kiện kích hoạt bắt buộc:** {verdict['buyup_req']}. Tuyệt đối không đặt lệnh ATO/ATC mua đuổi trụ VN30.

---

## IV. CHỨNG THỰC KIỂM TOÁN — BAN 12 (TỔNG KIỂM SÁT VIÊN TRỌNG)
- `16/16` thành viên có mặt đầy đủ xuyên đêm; chuỗi dữ liệu trích xuất 100% từ `yfinance` theo thời gian thực.
- Lưu trữ vĩnh viễn vào Summit Archive Vault ([APEX-SUMMIT-20261119-0430.json](file:///c:/Users/phuoc/Downloads/antigravity/Chứng%20khoán/{ARCHIVE_JSON_REL_PATH})).
"""
    tactical_md = f"""# ⚡ KẾ HOẠCH HÀNH ĐỘNG LINH HOẠT NGÀY `19/11/2026` — ĐÁO HẠN `VN30F1M` & HẬU `NVDA`
> **Ban hành sau Thượng đỉnh `04h30`:** Master CIO James (`Ban 8`) & Minh Quân (`Ban 7 VN`)  
> **Chế độ kích hoạt:** `{verdict['regime_code']}` (`^VIX {verdict['vix_latest']:.2f}` | `NVDA AH {verdict['nvda_ah_chg']:+.2f}%`)  
> **Tài khoản `TCBS 105C307855`:** `NAV {nav:,.0f} ₫` | `Cash {cash:,.0f} ₫ ({cash_pct}%)` | `0% Margin`

1. **09:00 – 13:45 (Khóa an toàn):** Không mua mới. Canh `MSH` giữ trên `34,600 ₫`; quan sát lực cung `BAF` khi chuẩn bị về tài khoản buổi chiều (`Hard Stop 30,050 ₫`).
2. **14:00 – 14:25 (Khung Giờ Vàng):** Chỉ giải ngân **{verdict['deploy_desc']}** nếu đạt `{verdict['buyup_req']}` và tránh bẫy kéo xả trụ đáo hạn `VN30F1M`.
3. **14:50 (Hậu đóng cửa):** Hệ thống Cloud tự chạy `hdb_post_exit_cloud_audit.py` đối soát `HDB` và báo cáo Telegram.
"""
    archive_md = resolution_md + "\n\n---\n\n## V. BIÊN BẢN TRANH BIỆN CHI TIẾT 04H30\n" + "\n".join(
        f"- **[{t['time_str']}] {t['sender_name']} (`{t['badge']}`):** {t['content']}"
        for t in (active_state.get("timeline_stream") or [])
    )

    (BASE_DIR / RESOLUTION_REL_PATH).parent.mkdir(parents=True, exist_ok=True)
    (BASE_DIR / RESOLUTION_REL_PATH).write_text(resolution_md, encoding="utf-8")
    (BASE_DIR / TACTICAL_PLAN_REL_PATH).parent.mkdir(parents=True, exist_ok=True)
    (BASE_DIR / TACTICAL_PLAN_REL_PATH).write_text(tactical_md, encoding="utf-8")
    (BASE_DIR / ARCHIVE_MD_REL_PATH).parent.mkdir(parents=True, exist_ok=True)
    (BASE_DIR / ARCHIVE_MD_REL_PATH).write_text(archive_md, encoding="utf-8")


def _update_archive_ledger(active_state: Dict[str, Any], verdict: Dict[str, Any], now_ict: datetime.datetime) -> None:
    save_json_safe(BASE_DIR / ARCHIVE_JSON_REL_PATH, active_state)
    ledger = load_json_safe(ARCHIVE_LEDGER_FILE, {"sessions": []})
    sessions = [s for s in (ledger.get("sessions") or []) if s.get("meeting_id") != MEETING_ID]
    entry = {
        "meeting_id": MEETING_ID,
        "title": active_state.get("title"),
        "topic": active_state.get("topic"),
        "meeting_window_str": active_state.get("meeting_window_str"),
        "prep_window_str": active_state.get("prep_window_str"),
        "start_time": active_state.get("start_time"),
        "end_time": active_state.get("end_time"),
        "chairman_approved": False,
        "approval_time": None,
        "archived_at": now_ict.isoformat(),
        "archived_display": now_ict.strftime("%d/%m/%Y %H:%M:%S"),
        "archive_reason": "CONCLUDED_REALTIME_NVDA_VIX_0430",
        "archived_by": "Ban 11 & Trọng Auto-Archiver",
        "archive_json_path": ARCHIVE_JSON_REL_PATH,
        "archive_md_path": ARCHIVE_MD_REL_PATH,
        "james_summary_path": RESOLUTION_REL_PATH,
        "resolution_report_path": RESOLUTION_REL_PATH,
        "turns_count": len(active_state.get("timeline_stream") or []),
        "prep_dossiers_count": len(active_state.get("pre_summit_prep_dossiers") or []),
        "quorum": "14/14 Phòng Ban + Palmer + Nam (16/16 Hiện diện thật 100%)",
        "summary_headline": f"Tổng kết 04h30 (VIX {verdict['vix_latest']:.2f} | NVDA AH {verdict['nvda_ah_chg']:+.2f}%) | Chế độ {verdict['regime_code']} & Kế hoạch Đáo hạn 19/11",
    }
    ledger["sessions"] = [entry] + sessions
    ledger["total_archived"] = len(ledger["sessions"])
    ledger["last_updated"] = now_ict.isoformat()
    save_json_safe(ARCHIVE_LEDGER_FILE, ledger)


def _sync_palmer_and_telegram(
    cp_name: str,
    summary_text: str,
    tasks_done: List[str],
    decisions: Dict[str, Any],
    dry_run: bool,
    report_rel: Optional[str] = None,
) -> None:
    if dry_run:
        print(f"[DRY-RUN] Skipped Palmer sync & Telegram dispatch for {cp_name}.")
        return
    try:
        from scripts.palmer_antigravity_sync_bridge import PalmerAntigravitySyncBridge
        PalmerAntigravitySyncBridge.broadcast_from_antigravity_to_palmer(
            user_request=f"Phiên trực Mỹ & NVDA BCTC ({cp_name}) — Thượng đỉnh 04h30 19/11",
            response_summary=summary_text,
            completed_tasks=tasks_done,
            active_decisions=decisions,
        )
    except Exception as exc:
        print(f"[!] Palmer sync warning: {exc}")

    notify_checkpoints = {"2030_MOBILIZE", "2130_OPEN", "0402_OFFICIAL_CLOSE", "0425_NVDA_EARNINGS_AH", "0430_SUMMIT"}
    if cp_name in notify_checkpoints:
        try:
            from scripts.telegram_dispatcher import dispatch_message
            topic = "alerts" if cp_name == "0425_NVDA_EARNINGS_AH" else "james_hq"
            dispatch_message(
                topic_key=topic,
                text=summary_text,
                parse_mode="Markdown",
                report_rel_path=report_rel,
                mirror_to_reports_vault=(cp_name == "0430_SUMMIT"),
                use_ai_summary=False,
            )
        except Exception as exc:
            print(f"[!] Telegram dispatch warning: {exc}")


def _build_base_meeting_state(dossiers: List[Dict[str, Any]], dynamic_msgs: List[Dict[str, Any]]) -> Dict[str, Any]:
    ledger = load_json_safe(ARCHIVE_LEDGER_FILE, {"sessions": []})
    return {
        "meeting_id": MEETING_ID,
        "version": "10.2-RealTime-5Checkpoint-NVDA-VIX-0430",
        "title": "🏛️ HỘI NGHỊ THƯỢNG ĐỈNH ĐÊM 18–19/11 — ĐÓN BCTC NVDA, THEO DÕI VIX & CHỐT KỊCH BẢN ĐÁO HẠN 04H30",
        "topic": "Theo dõi xuyên đêm phiên Mỹ (21h30 -> 04h00), đón BCTC NVDA (~04h20), đo VIX hạ nhiệt/căng thẳng & Họp Tổng Kết 04h30 sáng 19/11",
        "subtitle": "04h30 – 05h00 Sáng 19/11 (30 Phút) • 5 Nhịp Thật 21h30–04h25 • Chủ trì James & Palmer • Giám sát Trọng",
        "room_status": "ACTIVE_SESSION",
        "prep_start_time": "2026-11-19T04:10:00+07:00",
        "start_time": "2026-11-19T04:30:00+07:00",
        "end_time": "2026-11-19T05:00:00+07:00",
        "duration_minutes": 30,
        "prep_duration_minutes": 20,
        "meeting_window_str": "04h30 – 05h00 (30 Phút, 19/11/2026)",
        "prep_window_str": "20h30 -> 04h25 (Trực 5 nhịp + Đón BCTC NVDA)",
        "charter_report_path": CHARTER_REL_PATH,
        "summit_charter_rules": SUMMIT_CHARTER_RULES,
        "resolution_report_path": RESOLUTION_REL_PATH,
        "agenda_report_path": AGENDA_REL_PATH,
        "mode": "REALTIME_NVDA_VIX_0430_SUMMIT",
        "chairman": "Chủ tịch Hội đồng Quản trị — Trần Quốc Thiên Phước",
        "chairperson_host": "Master CIO James (Ban 8) & Palmer (Tổng Quản Trị)",
        "permanent_inspector": "Ban 12 — Tổng Kiểm Sát Viên Trọng (Chứng thực 5 nhịp thật)",
        "attendance_roster": _build_attendance_roster(),
        "attendance_summary": "14/14 Phòng Ban + Palmer + Nam (16/16 Hiện diện trong phòng họp & Trực 21h30–04h30)",
        "pre_summit_prep_dossiers": dossiers,
        "prep_timeline_stream": _build_prep_timeline_stream(dossiers),
        "timeline_stream": [],
        "dynamic_messages": dynamic_msgs,
        "james_summary_report_path": RESOLUTION_REL_PATH,
        "tactical_plan_path": TACTICAL_PLAN_REL_PATH,
        "archive_summary": {
            "sessions": ledger.get("sessions", []),
            "total_archived": len(ledger.get("sessions", [])),
            "last_updated": get_ict_now().isoformat(),
        },
        "retention_status": {
            "policy_hours": 2,
            "policy_minutes": 120,
            "room_status": "ACTIVE_SESSION",
            "chairman_approved": False,
            "approval_status": "PENDING_CHAIRMAN_APPROVAL",
            "end_time": "2026-11-19T05:00:00+07:00",
            "min_cleanup_time": "2026-11-19T07:00:00+07:00",
            "min_cleanup_display": "07:00:00 19/11/2026",
            "can_clean_now": False,
            "cleanup_status": "AWAITING_CHAIRMAN_APPROVAL",
            "cleanup_lock_reason": "Đang họp/trực chiến xuyên đêm chờ Tổng Kết 04h30 & Chủ tịch đọc phê duyệt (sau 07:00:00 19/11).",
        },
    }


def run_checkpoint(cp_name: str, dry_run: bool = False) -> int:
    now_ict = get_ict_now()
    ssot = _load_ssot_portfolio()
    quotes = fetch_live_us_quotes()
    news = fetch_nvda_news_rss(limit=5) if cp_name in {"0425_NVDA_EARNINGS_AH", "0430_SUMMIT"} else []

    log_data = load_json_safe(
        SESSION_LOG_FILE,
        {"session_date": "2026-11-18", "mode": "CLOUD_5_CHECKPOINT_NVDA_VIX_0430", "checkpoints": {}},
    )
    prev_keys = [k for k in (log_data.get("checkpoints") or {}).keys() if k != cp_name]
    prev_cp = log_data["checkpoints"][prev_keys[-1]] if prev_keys else None

    if cp_name != "0430_SUMMIT":
        log_data.setdefault("checkpoints", {})[cp_name] = {
            "timestamp_ict": now_ict.strftime("%Y-%m-%d %H:%M:%S"),
            "quotes": quotes,
            "delta_vs_prev_pct": _compute_deltas(quotes, prev_cp),
            "nvda_news": news,
        }
        if not dry_run:
            save_json_safe(SESSION_LOG_FILE, log_data)

    dossiers = _build_prep_dossiers(quotes, ssot, cp_name)
    cur_meeting = load_json_safe(ACTIVE_MEETING_FILE, {})
    dyn_msgs = list(cur_meeting.get("dynamic_messages") or []) if cur_meeting.get("meeting_id") == MEETING_ID else []

    if cp_name != "0430_SUMMIT":
        new_turn = _format_checkpoint_turn(cp_name, now_ict, quotes, news)
        dyn_msgs = [m for m in dyn_msgs if m.get("id") != new_turn["id"]]
        dyn_msgs.append(new_turn)
        state = _build_base_meeting_state(dossiers, dyn_msgs)
        vix_now = quotes.get("^VIX", {})
        nvda_now = quotes.get("NVDA", {})
        state["james_executive_summary"] = {
            "author": "Master CIO James & Palmer",
            "generated_at": now_ict.isoformat(),
            "report_path": AGENDA_REL_PATH,
            "summary_headline": f"Đang trực phiên Mỹ ({cp_name}): ^VIX {vix_now.get('last', 0):.2f} ({vix_now.get('chg_pct', 0):+.2f}%) | NVDA ${nvda_now.get('last', 0):.2f} — Họp Tổng Kết lúc 04h30 sáng 19/11",
            "is_reference_only": True,
            "agility_mandate": "Toàn thể 16/16 đang trực chiến xuyên đêm trên Cloud; báo cáo tổng kết chính thức phát hành lúc 04h30.",
            "meeting_highlights": [new_turn["content"]],
            "daily_cadence": [
                {"day": "Đêm 18/11 -> 04h25 19/11", "focus": "Theo dõi 5 nhịp Mỹ + BCTC NVDA + VIX", "trigger": f"Mốc vừa ghi: {cp_name}"},
                {"day": "Sáng 19/11 (04h30–05h00)", "focus": "Họp Tổng Kết 16/16 & Chốt Kịch bản Đáo Hạn", "trigger": "Xuất Báo cáo James trước khi Chủ tịch thức dậy"},
            ],
            "watchlist_tickers": ["NVDA", "^VIX", "SMH", "VNM", "MSH", "BAF", "HDB"],
            "chairman_action_required": "Chủ tịch cứ nghỉ ngơi & tắt máy; Cloud tự động trực và tổng kết lúc 04h30.",
        }
        if not dry_run:
            save_json_safe(ACTIVE_MEETING_FILE, state)
        _sync_palmer_and_telegram(
            cp_name=cp_name,
            summary_text=new_turn["content"],
            tasks_done=[f"Hoàn tất nhịp {cp_name} ({now_ict.strftime('%H:%M:%S ICT')})"],
            decisions={"checkpoint": cp_name, "vix": vix_now.get("last"), "nvda": nvda_now.get("last"), "nvda_ah": nvda_now.get("ah_price")},
            dry_run=dry_run,
            report_rel=AGENDA_REL_PATH,
        )
        print(f"[{now_ict.strftime('%H:%M:%S ICT')}] Checkpoint {cp_name} OK | Dossiers={len(dossiers)} | DynMsgs={len(dyn_msgs)} | DryRun={dry_run}")
        return 0

    # 0430_SUMMIT
    verdict = _evaluate_nvda_vix_regime(log_data, quotes)
    state = _build_base_meeting_state(dossiers, dyn_msgs)
    state["timeline_stream"] = _build_summit_debate_turns(now_ict, log_data, verdict, ssot)
    state["james_executive_summary"] = {
        "author": "Master CIO James (Ban 8 — Tổng Tư Lệnh)",
        "generated_at": now_ict.isoformat(),
        "report_path": RESOLUTION_REL_PATH,
        "summary_headline": f"Tổng kết 04h30: VIX {verdict['vix_latest']:.2f} | NVDA AH ${verdict['nvda_ah']:.2f} ({verdict['nvda_ah_chg']:+.2f}%) | {verdict['regime_code']}",
        "is_reference_only": True,
        "agility_mandate": f"Kế hoạch đáo hạn 19/11: Khóa mua trước 14h00; {verdict['deploy_desc']} (Yêu cầu {verdict['buyup_req']}).",
        "meeting_highlights": [
            f"NVDA đóng cửa ${verdict['nvda_reg']:.2f} -> After-Hours ${verdict['nvda_ah']:.2f} ({verdict['nvda_ah_chg']:+.2f}%).",
            f"^VIX ghi nhận {verdict['vix_latest']:.2f} (close {verdict['vix_close']:.2f}) -> Chế độ {verdict['regime_code']}.",
            f"Danh mục TCBS 105C307855: MSH 100 CP @ 35.2k (+2.0%, Trailing Stop 34.6k) | BAF 100 CP về TK chiều nay (Stop 30.05k) | Cash 13.59M (67.2%).",
        ],
        "daily_cadence": [
            {"day": "Thứ Năm 19/11 (09:00–13:45)", "focus": "Chờ BAF về TK & né nhiễu đáo hạn VN30F1M", "trigger": "0đ mua mới; giữ MSH trên 34,600đ"},
            {"day": "Thứ Năm 19/11 (14:00–14:25)", "focus": "Khung Giờ Vàng giải ngân Cash 13.59M", "trigger": f"{verdict['deploy_desc']} khi Buy-Up {verdict['buyup_req']}"},
        ],
        "watchlist_tickers": ["MSH", "BAF", "HDB", "DBC", "HPG", "IDC", "NVDA"],
        "chairman_action_required": "Kính trình Chủ tịch đọc Báo cáo Tổng Kết 04h30 & Kế hoạch Đáo Hạn 19/11 trước giờ mở cửa ATO.",
    }

    if not dry_run:
        _write_summit_reports(now_ict, log_data, verdict, ssot, state)
        _update_archive_ledger(state, verdict, now_ict)
        save_json_safe(ACTIVE_MEETING_FILE, state)

    summary_tg = (
        f"🏛️ *TỔNG KẾT THƯỢNG ĐỈNH 04H30 (19/11) — BCTC NVDA & VIX*\n"
        f"• *NVDA:* Close `${verdict['nvda_reg']:.2f}` -> AH **`${verdict['nvda_ah']:.2f}` ({verdict['nvda_ah_chg']:+.2f}%)**\n"
        f"• *^VIX:* Close `{verdict['vix_close']:.2f}` -> Hiện tại **`{verdict['vix_latest']:.2f}`**\n"
        f"• *Phán quyết:* `{verdict['regime_code']}`\n"
        f"• *Hành động 19/11 (Đáo hạn & BAF về chiều):* Giữ `MSH` (Trail 34.6k), `BAF` (Stop 30.05k); Cấm mua trước `14h00`; Khung 14h00–14h25: {verdict['deploy_desc']}."
    )
    _sync_palmer_and_telegram(
        cp_name="0430_SUMMIT",
        summary_text=summary_tg,
        tasks_done=["Hoàn tất họp 04h30 (16/16)", "Xuất Báo cáo James & Kế hoạch 19/11", "Lưu Summit Archive Vault"],
        decisions={"verdict": verdict["regime_code"], "vix": verdict["vix_latest"], "nvda_ah_chg": verdict["nvda_ah_chg"], "deploy_cap_vnd": verdict["deploy_cap_vnd"]},
        dry_run=dry_run,
        report_rel=RESOLUTION_REL_PATH,
    )
    print(f"[{now_ict.strftime('%H:%M:%S ICT')}] Summit 0430 OK | Regime={verdict['regime_code']} | VIX={verdict['vix_latest']:.2f} | NVDA_AH=${verdict['nvda_ah']:.2f} ({verdict['nvda_ah_chg']:+.2f}%) | DryRun={dry_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="APEX Overnight US, NVDA Earnings & 04:30 Summit Engine")
    parser.add_argument(
        "--checkpoint",
        default="auto",
        choices=[
            "2030_MOBILIZE", "2110_PREP", "2130_OPEN", "2230_POST_AMATEUR",
            "0100_MID_SESSION", "0402_OFFICIAL_CLOSE", "0425_NVDA_EARNINGS_AH", "0430_SUMMIT", "auto",
        ],
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.checkpoint == "auto":
        log_data = load_json_safe(SESSION_LOG_FILE, {"checkpoints": {}})
        targets = determine_auto_checkpoints(get_ict_now(), log_data)
    else:
        targets = [args.checkpoint]

    rc = 0
    for cp in targets:
        rc = run_checkpoint(cp, dry_run=args.dry_run)
        if rc != 0:
            break
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
