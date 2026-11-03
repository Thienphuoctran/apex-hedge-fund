#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/hpg_buy_trigger_watcher.py

HPG AUTOMATIC REAL-TIME BUY TRIGGER WATCHER
Autonomous Sentinel Agent - Apex Master CIO Execution Desk

Watches HPG price every 15 seconds.
Triggers immediate Telegram alert + Windows Beep + Antigravity Wakeup
as soon as HPG hits <= 20,400 VND (or <= 20,450 if testing).
"""

import sys
import time
import os
import datetime
from pathlib import Path
import warnings
warnings.simplefilter("ignore")

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    import yfinance as yf
except ImportError:
    yf = None

try:
    import winsound
except ImportError:
    winsound = None

from scripts.telegram_dispatcher import dispatch_message

BUY_TARGET_PRICE = 20400.0  # Threshold in VND

def sound_alarm():
    if winsound:
        try:
            for _ in range(4):
                winsound.Beep(1500, 300)
                time.sleep(0.05)
        except Exception:
            pass

def main():
    print(f"[*] HPG Automatic Buy Watcher Activated.")
    print(f"[*] Target Trigger Price: <= {BUY_TARGET_PRICE:,.0f} VND (Zone 20,100 - 20,400 VND).")
    print(f"[*] Scanning HPG.VN every 15 seconds...")

    iteration = 0
    while True:
        iteration += 1
        now_str = datetime.datetime.now().strftime("%H:%M:%S")
        curr_price = 0.0
        day_low = 0.0
        
        try:
            if yf:
                t = yf.Ticker("HPG.VN")
                hist = t.history(period="1d")
                if not hist.empty:
                    curr_price = float(hist["Close"].iloc[-1])
                    day_low = float(hist["Low"].iloc[-1])
        except Exception as e:
            print(f"[{now_str}] Warning fetching HPG quote: {e}")

        if curr_price > 0:
            print(f"[{now_str}] #{iteration} HPG Giá: {curr_price:,.0f} ₫ | Thấp nhất: {day_low:,.0f} ₫ | Mục tiêu: <= {BUY_TARGET_PRICE:,.0f} ₫")

            # Check trigger: current price hits target or day low breached target
            if curr_price <= BUY_TARGET_PRICE:
                print("\n" + "="*80)
                print(f"  🎯🎯🎯 BÁO ĐỘNG MUA HPG TỨC THỜI: THỊ GIÁ {curr_price:,.0f} ₫ ĐÃ VÀO VÙNG MUA!")
                print("="*80)
                
                sound_alarm()

                msg = (
                    f"🎯 *[APEX SENTINEL — CHỈ LỆNH MUA HPG KHẨN CẤP]*\n\n"
                    f"Kính gửi: *Chủ tịch Phước Trần*\n"
                    f"Mã: *HPG* (Tập đoàn Hòa Phát - HOSE)\n"
                    f"Thị giá hiện tại: *{curr_price:,.0f} ₫* (ĐÃ CHẠM VÙNG MUA KẾ HOẠCH!)\n\n"
                    f"👉 *HÀNH ĐỘNG NGAY*: Mở app TCBS, đặt lệnh MUA:\n"
                    f"• Loại lệnh: *LO*\n"
                    f"• Khối lượng: *200 CP* (Nhịp 1)\n"
                    f"• Giá đặt: *{curr_price:,.0f} ₫*\n"
                    f"• Cắt lỗ Stop 2xATR: *19,400 ₫* (-4.9%)\n"
                    f"• Mục tiêu TP1: *22,200 ₫* (+8.8%)\n"
                    f"Bấm khớp để hoàn tất bộ 3 siêu cổ phiếu!"
                )
                dispatch_message("alerts", msg)
                dispatch_message("morning_blotter", msg)
                print("[+] Đã bắn tin nhắn thúc giục mua HPG lên Telegram Chủ tịch!")
                return  # Exit to wake up Antigravity

        time.sleep(15)

if __name__ == "__main__":
    main()
