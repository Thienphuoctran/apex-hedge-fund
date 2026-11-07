@echo off
chcp 65001 > nul
title APEX CLOUD SUPERVISOR 24/7 (TCBS 105C307855)
echo ================================================================================
echo  🚀 KHỞI ĐỘNG APEX INSTITUTIONAL SUPERVISOR 24/7 TRÊN MÁY TÍNH BÀN
echo  Danh mục: 400 HPG + 300 TCB + 200 MBB (TCBS: 105C307855)
echo ================================================================================

cd /d "%~dp0\.."

if not exist "data\logs" mkdir "data\logs"

set PYTHONUNBUFFERED=1
set PYTHONIOENCODING=utf-8

python scripts\start_apex_cloud_247.py %*
