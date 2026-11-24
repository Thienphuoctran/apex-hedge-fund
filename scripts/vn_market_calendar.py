#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VIETNAM EXCHANGE TRADING CALENDAR & STALE-FEED AUTO-DETECTOR (PURE PYTHON STDLIB)
File: scripts/vn_market_calendar.py

Nhiệm vụ:
1. Chuẩn hóa lịch giao dịch HOSE / HNX / UPCoM (bỏ cuối tuần + ngày nghỉ lễ chính thức).
2. Nhận diện ngày nghỉ lễ Việt Nam (ví dụ 2026-11-24: Ngày Văn hóa Việt Nam — NQ 28/2026/QH16).
3. Tự động phát hiện dữ liệu đóng băng từ API (ví dụ `exchange_time = '15:05:00'` trong giờ hành chính
   khi sàn đóng cửa đột xuất mà chưa kịp cập nhật vào danh sách JSON).
4. Tính chính xác ngày thanh toán T+2 / T+2.5 bỏ qua ngày nghỉ lễ & cuối tuần.
   (Thuần Python stdlib — KHÔNG import pandas/numpy/yfinance để chạy nhẹ trên mọi môi trường.)
"""

from __future__ import annotations

import datetime
import json
import re
from pathlib import Path
from typing import Any, Dict, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
HOLIDAYS_CONFIG_FILE = BASE_DIR / "config" / "vn_exchange_holidays.json"

_BUILTIN_VN_HOLIDAYS: Dict[str, Dict[str, str]] = {
    "2026-01-01": {"name_vi": "Tết Dương lịch 2026", "authority": "Bộ luật Lao động 2019"},
    "2026-02-16": {"name_vi": "Nghỉ Tết Nguyên Đán Bính Ngọ 2026", "authority": "HOSE/HNX"},
    "2026-02-17": {"name_vi": "Mùng 1 Tết Nguyên Đán Bính Ngọ 2026", "authority": "HOSE/HNX"},
    "2026-02-18": {"name_vi": "Mùng 2 Tết Nguyên Đán Bính Ngọ 2026", "authority": "HOSE/HNX"},
    "2026-02-19": {"name_vi": "Mùng 3 Tết Nguyên Đán Bính Ngọ 2026", "authority": "HOSE/HNX"},
    "2026-02-20": {"name_vi": "Mùng 4 Tết Nguyên Đán Bính Ngọ 2026", "authority": "HOSE/HNX"},
    "2026-04-27": {"name_vi": "Nghỉ bù Giỗ Tổ Hùng Vương (10/3 Âm lịch)", "authority": "HOSE/HNX"},
    "2026-04-30": {"name_vi": "Ngày Giải phóng miền Nam 30/4", "authority": "Bộ luật Lao động 2019"},
    "2026-05-01": {"name_vi": "Ngày Quốc tế Lao động 1/5", "authority": "Bộ luật Lao động 2019"},
    "2026-09-01": {"name_vi": "Nghỉ lễ Quốc khánh (liền kề 02/9)", "authority": "HOSE/HNX"},
    "2026-09-02": {"name_vi": "Ngày Quốc khánh nước CHXHCN Việt Nam 02/9", "authority": "Bộ luật Lao động 2019"},
    "2026-11-24": {
        "name_vi": "Ngày Văn hóa Việt Nam (24/11)",
        "authority": "Nghị quyết số 28/2026/QH16 — HOSE & HNX nghỉ giao dịch toàn ngày",
    },
    "2027-01-01": {"name_vi": "Tết Dương lịch 2027", "authority": "Bộ luật Lao động 2019"},
    "2027-02-05": {"name_vi": "Nghỉ Tết Nguyên Đán Đinh Mùi 2027", "authority": "HOSE/HNX"},
    "2027-02-08": {"name_vi": "Nghỉ Tết Nguyên Đán Đinh Mùi 2027", "authority": "HOSE/HNX"},
    "2027-02-09": {"name_vi": "Nghỉ Tết Nguyên Đán Đinh Mùi 2027", "authority": "HOSE/HNX"},
    "2027-02-10": {"name_vi": "Nghỉ Tết Nguyên Đán Đinh Mùi 2027", "authority": "HOSE/HNX"},
    "2027-02-11": {"name_vi": "Nghỉ Tết Nguyên Đán Đinh Mùi 2027", "authority": "HOSE/HNX"},
    "2027-04-16": {"name_vi": "Giỗ Tổ Hùng Vương (10/3 Âm lịch)", "authority": "Bộ luật Lao động 2019"},
    "2027-04-30": {"name_vi": "Ngày Giải phóng miền Nam 30/4", "authority": "Bộ luật Lao động 2019"},
    "2027-05-03": {"name_vi": "Nghỉ bù Ngày Quốc tế Lao động 1/5", "authority": "Bộ luật Lao động 2019"},
    "2027-09-02": {"name_vi": "Ngày Quốc khánh 02/9", "authority": "Bộ luật Lao động 2019"},
    "2027-09-03": {"name_vi": "Nghỉ lễ Quốc khánh (liền kề 02/9)", "authority": "HOSE/HNX"},
    "2027-11-24": {
        "name_vi": "Ngày Văn hóa Việt Nam (24/11)",
        "authority": "Nghị quyết số 28/2026/QH16 — HOSE & HNX nghỉ giao dịch toàn ngày",
    },
}

_WEEKDAY_VI = [
    "Thứ Hai",
    "Thứ Ba",
    "Thứ Tư",
    "Thứ Năm",
    "Thứ Sáu",
    "Thứ Bảy",
    "Chủ Nhật",
]


def get_ict_now() -> datetime.datetime:
    """Luôn trả về giờ Việt Nam chuẩn ICT (UTC+7)."""
    return datetime.datetime.now(datetime.timezone.utc).astimezone(
        datetime.timezone(datetime.timedelta(hours=7))
    )


def _coerce_date(d: Any) -> datetime.date:
    if isinstance(d, datetime.datetime):
        return d.date()
    if isinstance(d, datetime.date):
        return d
    if isinstance(d, str):
        s = d.strip()[:10]
        return datetime.date.fromisoformat(s)
    return get_ict_now().date()


def load_vn_holidays() -> Dict[str, Dict[str, str]]:
    """Tải bảng ngày nghỉ lễ từ config/vn_exchange_holidays.json kết hợp fallback nội tại."""
    merged: Dict[str, Dict[str, str]] = {k: dict(v) for k, v in _BUILTIN_VN_HOLIDAYS.items()}
    if HOLIDAYS_CONFIG_FILE.exists():
        try:
            raw = json.loads(HOLIDAYS_CONFIG_FILE.read_text(encoding="utf-8"))
            file_holidays = raw.get("holidays") if isinstance(raw, dict) else {}
            if isinstance(file_holidays, dict):
                for k, v in file_holidays.items():
                    if isinstance(v, dict):
                        merged[str(k)] = {
                            "name_vi": str(v.get("name_vi") or "Nghỉ lễ HOSE/HNX"),
                            "authority": str(v.get("authority") or "HOSE/HNX"),
                        }
                    elif isinstance(v, str):
                        merged[str(k)] = {"name_vi": v, "authority": "HOSE/HNX"}
        except Exception:
            pass
    return merged


def get_holiday_info(d: Any, holidays: Optional[Dict[str, Dict[str, str]]] = None) -> Optional[Dict[str, str]]:
    dt = _coerce_date(d)
    hols = holidays if holidays is not None else load_vn_holidays()
    return hols.get(dt.isoformat())


def is_vn_trading_day(d: Any, holidays: Optional[Dict[str, Dict[str, str]]] = None) -> bool:
    """Trả về True nếu là ngày làm việc bình thường của sàn HOSE/HNX (không phải T7/CN hay ngày lễ)."""
    dt = _coerce_date(d)
    if dt.weekday() >= 5:
        return False
    hols = holidays if holidays is not None else load_vn_holidays()
    return dt.isoformat() not in hols


def next_trading_day(d: Any, holidays: Optional[Dict[str, Dict[str, str]]] = None) -> datetime.date:
    """Tìm ngày giao dịch kế tiếp ngay sau ngày d."""
    hols = holidays if holidays is not None else load_vn_holidays()
    cur = _coerce_date(d) + datetime.timedelta(days=1)
    for _ in range(30):
        if is_vn_trading_day(cur, hols):
            return cur
        cur += datetime.timedelta(days=1)
    return cur


def prev_trading_day(d: Any, holidays: Optional[Dict[str, Dict[str, str]]] = None) -> datetime.date:
    """Tìm ngày giao dịch gần nhất trước ngày d."""
    hols = holidays if holidays is not None else load_vn_holidays()
    cur = _coerce_date(d) - datetime.timedelta(days=1)
    for _ in range(30):
        if is_vn_trading_day(cur, hols):
            return cur
        cur -= datetime.timedelta(days=1)
    return cur


def add_trading_days(d: Any, n: int, holidays: Optional[Dict[str, Dict[str, str]]] = None) -> datetime.date:
    """Cộng/trừ n ngày giao dịch thực tế (bỏ qua cuối tuần và ngày nghỉ lễ HOSE/HNX)."""
    hols = holidays if holidays is not None else load_vn_holidays()
    cur = _coerce_date(d)
    if n == 0:
        return cur
    step = 1 if n > 0 else -1
    remaining = abs(n)
    guard = 0
    while remaining > 0 and guard < 180:
        cur += datetime.timedelta(days=step)
        guard += 1
        if is_vn_trading_day(cur, hols):
            remaining -= 1
    return cur


def _extract_exchange_time_hms(market_overview: Optional[Dict[str, Any]]) -> str:
    if not isinstance(market_overview, dict):
        return ""
    raw = str(
        market_overview.get("exchange_time")
        or (market_overview.get("vn_index") or {}).get("time")
        or ""
    ).strip()
    m = re.search(r"(\d{1,2}:\d{2}(?::\d{2})?)", raw)
    if not m:
        return ""
    parts = m.group(1).split(":")
    h = int(parts[0])
    mi = int(parts[1])
    s = int(parts[2]) if len(parts) > 2 else 0
    return f"{h:02d}:{mi:02d}:{s:02d}"


def get_vn_market_session_state(
    now_ict: Optional[datetime.datetime] = None,
    market_overview: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Trả về trạng thái phiên giao dịch thống nhất cho toàn bộ hệ thống Apex:
    - HOLIDAY_CLOSED / WEEKEND_CLOSED nếu sàn nghỉ lễ / cuối tuần.
    - EXCHANGE_STALE_FEED nếu đang trong giờ giao dịch (09:20-14:45) nhưng bảng điện trả
      exchange_time >= 15:00:00 (dữ liệu đóng băng từ phiên trước — dấu hiệu sàn nghỉ đột xuất).
    - Hoặc PRE_MARKET / ATO / MORNING_SESSION / MIDDAY_BREAK / AFTERNOON_T2 / GOLDEN_HOUR / ATC / AFTER_HOURS.
    """
    if now_ict is None:
        now_ict = get_ict_now()
    elif now_ict.tzinfo is None:
        now_ict = now_ict.replace(tzinfo=datetime.timezone(datetime.timedelta(hours=7)))

    hols = load_vn_holidays()
    d = now_ict.date()
    date_str = d.isoformat()
    time_str = now_ict.strftime("%H:%M:%S")
    hm = now_ict.hour * 60 + now_ict.minute

    holiday_info = hols.get(date_str)
    is_weekend = d.weekday() >= 5
    is_holiday = holiday_info is not None
    is_trading_day = (not is_weekend) and (not is_holiday)

    next_td = next_trading_day(d, hols)
    prev_td = prev_trading_day(d, hols)
    next_td_vi = f"{_WEEKDAY_VI[next_td.weekday()]} {next_td.strftime('%d/%m/%Y')}"
    next_td_short = next_td.strftime("%d/%m")
    prev_td_short = prev_td.strftime("%d/%m")

    exchange_time_hms = _extract_exchange_time_hms(market_overview)
    stale_feed_detected = False
    stale_feed_reason = ""
    if is_trading_day and (9 * 60 + 20 <= hm <= 14 * 60 + 45) and exchange_time_hms:
        ex_h = int(exchange_time_hms[:2])
        ex_m = int(exchange_time_hms[3:5])
        ex_hm = ex_h * 60 + ex_m
        # Trong khung giao dịch 09:20-14:45 mà API trả mốc đóng cửa (>= 15:00) -> feed đóng băng từ phiên trước!
        if ex_hm >= 15 * 60:
            stale_feed_detected = True
            stale_feed_reason = (
                f"Bảng điện VPS lúc {now_ict.strftime('%H:%M')} ICT vẫn trả exchange_time={exchange_time_hms} "
                f"(ảnh chụp đóng cửa phiên trước {prev_td_short}), không có khớp lệnh trực tiếp."
            )

    holiday_name = str(holiday_info.get("name_vi", "")) if holiday_info else ""
    holiday_authority = str(holiday_info.get("authority", "")) if holiday_info else ""

    if is_holiday:
        status_code = "HOLIDAY_CLOSED"
        is_live_session = False
        status_label_vi = f"🎌 NGHỈ LỄ {holiday_name.upper()} — HOSE/HNX ĐÓNG CỬA (Mở lại {next_td_vi})"
        short_badge_vi = f"🎌 NGHỈ LỄ {d.strftime('%d/%m')} (Mở lại {next_td_short})"
        settlement_note_vi = (
            f"Do {d.strftime('%d/%m')} là ngày nghỉ lễ ({holiday_name}), lịch thanh toán T+2 dịch thêm 1 ngày làm việc: "
            f"tiền bán 20/11 về {next_td_short}; cổ phiếu mua 23/11 về chiều {add_trading_days(datetime.date(2026, 11, 23), 2, hols).strftime('%d/%m/%Y')}."
            if date_str == "2026-11-24"
            else f"Ngày nghỉ lễ ({holiday_name}): mọi chu kỳ T+2 được dời sang ngày làm việc kế tiếp ({next_td_vi})."
        )
    elif is_weekend:
        status_code = "WEEKEND_CLOSED"
        is_live_session = False
        status_label_vi = f"🛑 CUỐI TUẦN — SÀN HOSE/HNX ĐÓNG CỬA (Mở lại {next_td_vi})"
        short_badge_vi = f"🛑 CUỐI TUẦN (Mở lại {next_td_short})"
        settlement_note_vi = f"Cuối tuần sàn nghỉ giao dịch. Phiên mở cửa kế tiếp: {next_td_vi}."
    elif stale_feed_detected:
        status_code = "EXCHANGE_STALE_FEED"
        is_live_session = False
        status_label_vi = f"⚠️ SÀN HOSE/HNX KHÔNG PHÁT GIAO DỊCH LIVE (exchange_time={exchange_time_hms} từ phiên {prev_td_short})"
        short_badge_vi = f"⚠️ DỮ LIỆU ĐÓNG BĂNG ({exchange_time_hms})"
        settlement_note_vi = stale_feed_reason
    else:
        if hm < 8 * 60 + 55:
            status_code = "PRE_MARKET"
            is_live_session = False
            status_label_vi = "🌅 TRƯỚC GIỜ MỞ CỬA HOSE (Chuẩn bị giao ban trước 09h00)"
            short_badge_vi = "🌅 PRE-MARKET"
        elif hm < 9 * 60 + 15:
            status_code = "ATO"
            is_live_session = True
            status_label_vi = "🔔 PHIÊN KHỚP LỆNH MỞ CỬA ATO (09:00 – 09:15) — CẤM FOMO ĐUỔI GAP"
            short_badge_vi = "🔔 ATO LIVE"
        elif hm < 11 * 60 + 30:
            status_code = "MORNING_SESSION"
            is_live_session = True
            status_label_vi = "📈 PHIÊN LIÊN TỤC SÁNG HOSE/HNX (09:15 – 11:30)"
            short_badge_vi = "📈 PHIÊN SÁNG LIVE"
        elif hm < 13 * 60:
            status_code = "MIDDAY_BREAK"
            is_live_session = False
            status_label_vi = "☕ NGHỈ TRƯA & ĐỐI SOÁT GIỮA PHIÊN (11:30 – 13:00)"
            short_badge_vi = "☕ NGHỈ TRƯA"
        elif hm < 14 * 60:
            status_code = "AFTERNOON_T2"
            is_live_session = True
            status_label_vi = "🌊 PHIÊN CHIỀU — HẤP THỤ HÀNG T+2.5 (13:00 – 14:00)"
            short_badge_vi = "🌊 CHIỀU T+2.5 LIVE"
        elif hm <= 14 * 60 + 25:
            status_code = "GOLDEN_HOUR"
            is_live_session = True
            status_label_vi = "⭐ KHUNG GIỜ VÀNG QUYẾT ĐỊNH LỆNH LO (14:00 – 14:25)"
            short_badge_vi = "⭐ GIỜ VÀNG LO"
        elif hm <= 14 * 60 + 48:
            status_code = "ATC"
            is_live_session = True
            status_label_vi = "🔒 PHIÊN ĐÓNG CỬA ATC (14:30 – 14:45) — KHÓA MUA MỚI"
            short_badge_vi = "🔒 ATC LIVE"
        else:
            status_code = "AFTER_HOURS"
            is_live_session = False
            status_label_vi = f"🌙 ĐÃ ĐÓNG CỬA PHIÊN {d.strftime('%d/%m')} — CHUYỂN GIAO PHỐ WALL CA TỐI"
            short_badge_vi = f"🌙 ĐÃ ĐÓNG CỬA ({d.strftime('%d/%m')})"
        settlement_note_vi = f"Phiên giao dịch bình thường ngày {d.strftime('%d/%m/%Y')}; T+2 về chiều {add_trading_days(d, 2, hols).strftime('%d/%m/%Y')}."

    return {
        "date_ict": date_str,
        "time_ict": time_str,
        "weekday_vi": _WEEKDAY_VI[d.weekday()],
        "is_trading_day": is_trading_day,
        "is_holiday": is_holiday,
        "is_weekend": is_weekend,
        "holiday_name": holiday_name,
        "holiday_authority": holiday_authority,
        "is_live_session": is_live_session,
        "stale_feed_detected": stale_feed_detected,
        "stale_feed_reason": stale_feed_reason,
        "exchange_time_hms": exchange_time_hms,
        "status_code": status_code,
        "status_label_vi": status_label_vi,
        "short_badge_vi": short_badge_vi,
        "prev_trading_day": prev_td.isoformat(),
        "prev_trading_day_vi": f"{_WEEKDAY_VI[prev_td.weekday()]} {prev_td.strftime('%d/%m/%Y')}",
        "next_trading_day": next_td.isoformat(),
        "next_trading_day_vi": next_td_vi,
        "settlement_note_vi": settlement_note_vi,
    }


if __name__ == "__main__":
    print(json.dumps(get_vn_market_session_state(), ensure_ascii=False, indent=2))
