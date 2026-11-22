@echo off
rem APEX DAILY LIVE WAR-ROOM LAUNCHER (09:00 - 16:00 ICT, MON-FRI)
cd /d "%~dp0.."
if not exist "data\logs" mkdir "data\logs"
python -X utf8 scripts\apex_daily_live_warroom_engine.py --daemon >> data\logs\daily_warroom_boot.log 2>&1
