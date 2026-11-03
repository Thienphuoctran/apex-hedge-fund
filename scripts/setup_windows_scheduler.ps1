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

Write-Host "============================================================"
Write-Host " AUTOMATION ACTIVE: Computer does NOT need to run 24/24!"
Write-Host " If machine is OFF at schedule, it will auto-run on boot."
Write-Host "============================================================"
