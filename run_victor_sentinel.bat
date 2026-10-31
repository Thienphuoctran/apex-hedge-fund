@echo off
title BAN 9 - VICTOR SENTINEL 24/7 DESK
color 0A
chcp 65001 >nul
cls
echo ================================================================================
echo   BAN 9 — APEX LIVE PORTFOLIO SENTINEL & INCIDENT DESK ("VICTOR")
echo   GIÁM SÁT THỜI GIAN THỰC 22 CỔ PHIẾU ĐÃ ĐẦU TƯ & BẮN CẢNH BÁO TELEGRAM
echo ================================================================================
echo.
cd /d "%~dp0"
python scripts\intraday_portfolio_sentinel.py --daemon --interval 60
pause
