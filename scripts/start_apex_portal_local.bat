@echo off
cd /d "%~dp0.."
if not exist "logs" mkdir "logs"
for %%F in ("logs\apex_local_portal.log") do if exist %%F if %%~zF GTR 2097152 move /Y "logs\apex_local_portal.log" "logs\apex_local_portal.prev.log" > nul 2>&1
python -X utf8 scripts\start_apex_portal_local.py >> "logs\apex_local_portal.log" 2>&1
