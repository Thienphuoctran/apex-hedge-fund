@echo off
cd /d "c:\Users\phuoc\Downloads\antigravity\Chứng khoán"
if not exist "logs" mkdir "logs"
python -X utf8 scripts\start_apex_portal_local.py >> "logs\apex_local_portal.log" 2>&1
