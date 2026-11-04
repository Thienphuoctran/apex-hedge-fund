@echo off
chcp 65001 > nul
title APEX INSTITUTIONAL CRON DAEMON 24/7 (MASTER V2.0)
color 0A

echo ===============================================================================
echo   APEX INSTITUTIONAL CRON DAEMON 24/7 - PRODUCTION MASTER V2.0
echo   Co quan chu quan: Palmer (Phong Tong He Thong) ^& Master CIO James (Ban 8)
echo   Phuc vu truc tiep: Chu tich Phuoc Tran (Tai khoan TCBS: 105C307855)
echo   Cam ket: 100%% LAM THAT - VIEC THAT - KHEP KIN 17 COT MOC TAC CHIEN
echo ===============================================================================
echo.

python scripts\apex_institutional_cron_daemon.py --daemon

pause
