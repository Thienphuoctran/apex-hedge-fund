# Windows Task Scheduler Setup for Apex Quantitative Fund
param (
    [switch]$Uninstall,
    [string]$CapitalVnd = "20000000"
)

$WorkspaceDir = "C:\Users\phuoc\Downloads\antigravity\Chứng khoán"
$PythonExe = "python.exe"

if ($Uninstall) {
    Write-Host "Unregistering Apex Fund scheduled tasks..."
    Unregister-ScheduledTask -TaskName "ApexFund_Morning_PreMarket_Audit_0700" -Confirm:$false -ErrorAction SilentlyContinue
    Unregister-ScheduledTask -TaskName "ApexFund_Sunday_CIO_Summit" -Confirm:$false -ErrorAction SilentlyContinue
    Unregister-ScheduledTask -TaskName "ApexFund_Morning_PreATO" -Confirm:$false -ErrorAction SilentlyContinue
    Unregister-ScheduledTask -TaskName "ApexFund_Evening_PreUS" -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "All automated tasks have been removed."
    exit 0
}

Write-Host "============================================================"
Write-Host "  APEX FUND: 100% AUTOMATED BACKGROUND PIPELINE SCHEDULER"
Write-Host "============================================================"

$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -WakeToRun -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

# 0. Morning 07:00 Mon-Fri - Palmer Pre-Market Total Audit (Rà Soát Tổng Hệ Thống)
$AuditAction = New-ScheduledTaskAction -Execute $PythonExe -Argument "scripts\pre_market_readiness_audit.py --send-telegram" -WorkingDirectory $WorkspaceDir
$AuditTrigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At "07:00"
Register-ScheduledTask -TaskName "ApexFund_Morning_PreMarket_Audit_0700" -Action $AuditAction -Trigger $AuditTrigger -Settings $Settings -Description "Palmer 07:00 AM Pre-Market System Audit" -Force | Out-Null
Write-Host "[OK] Task 0 registered: ApexFund_Morning_PreMarket_Audit_0700 (Mon-Fri at 07:00)"

# 1. Sunday 20:00 - Master CIO Summit
$SundayAction = New-ScheduledTaskAction -Execute $PythonExe -Argument "scripts\run_master_unified_fund.py --capital-vnd $CapitalVnd" -WorkingDirectory $WorkspaceDir
$SundayTrigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At "20:00"
Register-ScheduledTask -TaskName "ApexFund_Sunday_CIO_Summit" -Action $SundayAction -Trigger $SundayTrigger -Settings $Settings -Description "Master CIO Weekly Decision" -Force | Out-Null
Write-Host "[OK] Task 1 registered: ApexFund_Sunday_CIO_Summit (Every Sunday at 20:00)"

# 2. Morning 08:30 Mon-Fri - Minh Quan Pre-ATO Blotter + Sentinel Scan + Telegram Morning Briefing
$MorningAction = New-ScheduledTaskAction -Execute $PythonExe -Argument "scripts\run_master_unified_fund.py --cio-only --capital-vnd $CapitalVnd" -WorkingDirectory $WorkspaceDir
$MorningTrigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At "08:30"
Register-ScheduledTask -TaskName "ApexFund_Morning_PreATO" -Action $MorningAction -Trigger $MorningTrigger -Settings $Settings -Description "Minh Quan Pre-ATO Briefing & Morning Telegram Dispatch" -Force | Out-Null
Write-Host "[OK] Task 2 registered: ApexFund_Morning_PreATO (Mon-Fri at 08:30 -> run_master_unified_fund.py --cio-only)"

# 3. Evening 20:30 Mon-Fri - Alex Pre-Market US (Full Live Data Fetch + Recompute)
$EveningAction = New-ScheduledTaskAction -Execute $PythonExe -Argument "scripts\run_daily_pipeline.py" -WorkingDirectory $WorkspaceDir
$EveningTrigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At "20:30"
Register-ScheduledTask -TaskName "ApexFund_Evening_PreUS" -Action $EveningAction -Trigger $EveningTrigger -Settings $Settings -Description "Alex US Pre-Market Live Data Pipeline" -Force | Out-Null
Write-Host "[OK] Task 3 registered: ApexFund_Evening_PreUS (Mon-Fri at 20:30 -> run_daily_pipeline.py live)"

# 4. Evening 21:00 Daily - Ban 10 Hien BCTC & IR Scout Report
$HienAction = New-ScheduledTaskAction -Execute $PythonExe -Argument "scripts\apex_institutional_cron_daemon.py --at=21:00" -WorkingDirectory $WorkspaceDir
$HienTrigger = New-ScheduledTaskTrigger -Daily -At "21:00"
Register-ScheduledTask -TaskName "ApexFund_Hien_BCTC_2100" -Action $HienAction -Trigger $HienTrigger -Settings $Settings -Description "Ban 10 Hien 21:00 PM BCTC & IR Scout Report" -Force | Out-Null
Write-Host "[OK] Task 4 registered: ApexFund_Hien_BCTC_2100 (Daily at 21:00 -> Hien BCTC Review)"

# 5. Evening 21:15 Daily - Ban 11 Khanh Viral Video 60s Script
$KhanhAction = New-ScheduledTaskAction -Execute $PythonExe -Argument "scripts\apex_institutional_cron_daemon.py --at=21:15" -WorkingDirectory $WorkspaceDir
$KhanhTrigger = New-ScheduledTaskTrigger -Daily -At "21:15"
Register-ScheduledTask -TaskName "ApexFund_Khanh_Viral_2115" -Action $KhanhAction -Trigger $KhanhTrigger -Settings $Settings -Description "Ban 11 Khanh 21:15 PM Viral 60s Script" -Force | Out-Null
Write-Host "[OK] Task 5 registered: ApexFund_Khanh_Viral_2115 (Daily at 21:15 -> Khanh Viral Script)"

# 6. Night 23:00 Daily - Apex EOD 23h00 Executive Council Meeting
$CouncilAction = New-ScheduledTaskAction -Execute $PythonExe -Argument "scripts\apex_institutional_cron_daemon.py --at=23:00" -WorkingDirectory $WorkspaceDir
$CouncilTrigger = New-ScheduledTaskTrigger -Daily -At "23:00"
Register-ScheduledTask -TaskName "ApexFund_EOD_Council_2300" -Action $CouncilAction -Trigger $CouncilTrigger -Settings $Settings -Description "Apex 23:00 EOD Executive Council Meeting" -Force | Out-Null
Write-Host "[OK] Task 6 registered: ApexFund_EOD_Council_2300 (Daily at 23:00 -> EOD Council Meeting)"

# 7. Auto-Launch 24/7 Cron Daemon on Windows Logon via Startup Folder
$StartupBat = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\launch_apex_fund.bat"
if (Test-Path $StartupBat) {
    Write-Host "[OK] Task 7 active: Windows Startup Folder bat launches apex_institutional_cron_daemon.py on boot"
}

Write-Host "============================================================"
Write-Host " AUTOMATION ACTIVE: Computer does NOT need to run 24/24!"
Write-Host " If machine is OFF at schedule, it will auto-run on boot."
Write-Host "============================================================"
