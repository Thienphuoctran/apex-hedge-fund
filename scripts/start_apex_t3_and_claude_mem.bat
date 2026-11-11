@echo off
rem APEX BACKGROUND SERVICES LAUNCHER (SILENT & LIGHTWEIGHT)
rem Tự động khởi chạy T3 Code server & Claude-Mem worker ở chế độ nền ngầm
cd /d "C:\Users\phuoc\Downloads\antigravity\Chứng khoán"

rem 1. Khởi động Claude-Mem Worker (Cổng 37725)
start /B "" "C:\Users\phuoc\.bun\bin\bun.exe" "C:\Users\phuoc\.claude\plugins\marketplaces\thedotmack\plugin\scripts\worker-service.cjs" --daemon > nul 2>&1

rem 2. Khởi động T3 Code Server (Cổng 37888)
start /B "" "C:\Users\phuoc\.local\bin\t3.cmd" serve --port 37888 --lan --no-browser > nul 2>&1
