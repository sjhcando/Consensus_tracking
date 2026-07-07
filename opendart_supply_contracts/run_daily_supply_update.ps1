$ErrorActionPreference = "Stop"

$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonExe = "C:\Users\sjhca\anaconda3\python.exe"
$DateStamp = Get-Date -Format "yyyyMMdd"
$LogDir = Join-Path $ProjectDir "logs"
$StdoutLog = Join-Path $LogDir "scheduled_daily_update_$DateStamp.log"
$StderrLog = Join-Path $LogDir "scheduled_daily_update_$DateStamp.err.log"

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
Set-Location $ProjectDir

& $PythonExe ".\daily_update_supply_contracts.py" > $StdoutLog 2> $StderrLog
