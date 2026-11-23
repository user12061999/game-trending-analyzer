<#
.SYNOPSIS
  Registers (or removes) Windows scheduled tasks that keep the market database growing
  even when the dashboard is not open.

.DESCRIPTION
  Creates two tasks for the current user (no admin rights needed):
    - "GameTrendAnalyzer - Daily Crawl": runs scripts\crawl_once.py at the crawl hour and again
      12 hours later as a safety net. The script skips itself if today's data already exists,
      so the second run (or a run while the web server already crawled) costs nothing.
      "Start when available" makes Windows run a missed crawl as soon as the PC is on again.
    - "GameTrendAnalyzer - Weekly DB Backup": copies data\game_trends.db to data\backups\
      every Sunday and keeps the newest 8 copies.

  Tasks run only while you are logged on (no password is stored), hidden (pythonw.exe).

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File scripts\install_scheduled_tasks.ps1
  powershell -ExecutionPolicy Bypass -File scripts\install_scheduled_tasks.ps1 -CrawlTime 07:30
  powershell -ExecutionPolicy Bypass -File scripts\install_scheduled_tasks.ps1 -Uninstall
#>
param(
    [string]$CrawlTime = "06:00",
    [string]$BackupDay = "Sunday",
    [string]$BackupTime = "12:00",
    [switch]$Uninstall
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Pythonw = Join-Path $Root ".venv\Scripts\pythonw.exe"
$CrawlTaskName = "GameTrendAnalyzer - Daily Crawl"
$BackupTaskName = "GameTrendAnalyzer - Weekly DB Backup"
$TaskFolder = "\GameTrendAnalyzer\"

if ($Uninstall) {
    foreach ($name in @($CrawlTaskName, $BackupTaskName)) {
        if (Get-ScheduledTask -TaskName $name -TaskPath $TaskFolder -ErrorAction SilentlyContinue) {
            Unregister-ScheduledTask -TaskName $name -TaskPath $TaskFolder -Confirm:$false
            Write-Host "Removed: $name"
        }
    }
    return
}

if (-not (Test-Path $Pythonw)) {
    throw "Không tìm thấy $Pythonw. Hãy chạy start.bat một lần để tạo môi trường ảo (.venv) trước."
}

$crawlAt = [datetime]::ParseExact($CrawlTime, "HH:mm", $null)
$user = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$principal = New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Limited

$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -RunOnlyIfNetworkAvailable `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1)

# --- Daily crawl ---
$crawlAction = New-ScheduledTaskAction -Execute $Pythonw `
    -Argument "`"$(Join-Path $Root 'scripts\crawl_once.py')`"" -WorkingDirectory $Root
$crawlTriggers = @(
    (New-ScheduledTaskTrigger -Daily -At $crawlAt),
    (New-ScheduledTaskTrigger -Daily -At $crawlAt.AddHours(12))
)
Register-ScheduledTask -TaskName $CrawlTaskName -TaskPath $TaskFolder -Action $crawlAction `
    -Trigger $crawlTriggers -Settings $settings -Principal $principal -Force `
    -Description "Crawl bảng xếp hạng game mỗi ngày (bỏ qua nếu hôm nay đã có dữ liệu). Log: data\logs\" | Out-Null
Write-Host "Installed: $CrawlTaskName (daily at $CrawlTime and $($crawlAt.AddHours(12).ToString('HH:mm')))"

# --- Weekly backup ---
$backupAction = New-ScheduledTaskAction -Execute $Pythonw `
    -Argument "`"$(Join-Path $Root 'scripts\backup_db.py')`" --keep 8" -WorkingDirectory $Root
$backupTrigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $BackupDay -At ([datetime]::ParseExact($BackupTime, "HH:mm", $null))
Register-ScheduledTask -TaskName $BackupTaskName -TaskPath $TaskFolder -Action $backupAction `
    -Trigger $backupTrigger -Settings $settings -Principal $principal -Force `
    -Description "Sao lưu data\game_trends.db vào data\backups\ (giữ 8 bản mới nhất)" | Out-Null
Write-Host "Installed: $BackupTaskName ($BackupDay at $BackupTime)"

Write-Host ""
Write-Host "Chạy thử ngay:  Start-ScheduledTask -TaskPath '$TaskFolder' -TaskName '$CrawlTaskName'"
Write-Host "Xem log:        $(Join-Path $Root 'data\logs')"
