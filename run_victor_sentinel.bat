@echo off
title PALMER & VICTOR ALWAYS-ON 24/7 SENTINEL & REALTIME WAVE RADAR
color 0A
chcp 65001 >nul
cls
echo ========================================================================================
echo   PALMER & VICTOR ALWAYS-ON 24/7 SENTINEL ^& REALTIME WAVE RADAR (9 PHÒNG BAN)
echo   - Canh Chốt Lời Tự Động (TP1 / TP2 Scaling Out 50/50) ^& Cắt Lỗ Stop 2xATR
echo   - Radar Săn Sóng Mới 54 Mã VN (Minh Quân) ^& 35 Mã Mỹ (Alex) — Chuẩn BCTC AAA/AA
echo   - Đồng Bộ Tin Tức CBTT Việt Nam ^& Hồ Sơ SEC EDGAR Mỹ + Báo Động Telegram Tức Thì
echo ========================================================================================
echo.
cd /d "%~dp0"
python scripts\intraday_portfolio_sentinel.py --daemon --interval 60
pause
