# Windows Task Scheduler Setup for Apex Quantitative Fund
param (
    [switch]$Uninstall,
    [string]$CapitalVnd = "15000000"
)

$WorkspaceDir = "C:\Users\phuoc\Downloads\antigravity\Chứng khoán"
$PythonExe = "python.exe"

if ($Uninstall) {
    Write-Host "Unregistering Apex Fund scheduled tasks..."
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

# 1. Sunday 20:00 - Master CIO Summit
$SundayAction = New-ScheduledTaskAction -Execute $PythonExe -Argument "scripts\run_master_unified_fund.py --capital-vnd $CapitalVnd" -WorkingDirectory $WorkspaceDir
$SundayTrigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At "20:00"
Register-ScheduledTask -TaskName "ApexFund_Sunday_CIO_Summit" -Action $SundayAction -Trigger $SundayTrigger -Settings $Settings -Description "Master CIO Weekly Decision" -Force | Out-Null
Write-Host "[OK] Task 1 registered: ApexFund_Sunday_CIO_Summit (Every Sunday at 20:00)"

# 2. Morning 08:30 Mon-Fri - Minh Quan Pre-ATO Blotter
$MorningAction = New-ScheduledTaskAction -Execute $PythonExe -Argument "scripts\master_cio_allocator.py --capital-vnd $CapitalVnd" -WorkingDirectory $WorkspaceDir
$MorningTrigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At "08:30"
Register-ScheduledTask -TaskName "ApexFund_Morning_PreATO" -Action $MorningAction -Trigger $MorningTrigger -Settings $Settings -Description "Minh Quan Pre-ATO Briefing" -Force | Out-Null
Write-Host "[OK] Task 2 registered: ApexFund_Morning_PreATO (Mon-Fri at 08:30)"

# 3. Evening 20:30 Mon-Fri - Alex Pre-Market US
$EveningAction = New-ScheduledTaskAction -Execute $PythonExe -Argument "scripts\run_daily_pipeline.py --fast" -WorkingDirectory $WorkspaceDir
$EveningTrigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At "20:30"
Register-ScheduledTask -TaskName "ApexFund_Evening_PreUS" -Action $EveningAction -Trigger $EveningTrigger -Settings $Settings -Description "Alex US Pre-Market Briefing" -Force | Out-Null
Write-Host "[OK] Task 3 registered: ApexFund_Evening_PreUS (Mon-Fri at 20:30)"

Write-Host "============================================================"
Write-Host " AUTOMATION ACTIVE: Computer does NOT need to run 24/24!"
Write-Host " If machine is OFF at schedule, it will auto-run on boot."
Write-Host "============================================================"
