param(
  [switch]$SkipInstall
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootDir = Split-Path -Parent $scriptDir
$backendDir = Join-Path $rootDir "backend"
$frontendDir = Join-Path $rootDir "frontend"
$backendVenvPython = Join-Path $backendDir ".venv\Scripts\python.exe"
$backendHealth = "http://127.0.0.1:8000/health"

function Assert-Command([string]$name) {
  if (-not (Get-Command $name -ErrorAction SilentlyContinue)) {
    throw "Command not found: $name"
  }
}

function Wait-BackendHealthy([System.Diagnostics.Process]$process, [int]$timeoutSec = 45) {
  $start = Get-Date
  while (((Get-Date) - $start).TotalSeconds -lt $timeoutSec) {
    if ($process.HasExited) {
      throw "Backend process exited early. Check logs/dev-backend.log"
    }
    try {
      $resp = Invoke-RestMethod -Uri $backendHealth -Method Get -TimeoutSec 2
      if ($resp.status -eq "ok") {
        return
      }
    } catch {
      Start-Sleep -Milliseconds 500
    }
  }
  throw "Backend health check timed out: $backendHealth"
}

Assert-Command "py"
Assert-Command "npm"

if (-not (Test-Path $backendDir)) { throw "Backend directory not found: $backendDir" }
if (-not (Test-Path $frontendDir)) { throw "Frontend directory not found: $frontendDir" }

if (-not (Test-Path $backendVenvPython)) {
  Write-Host "[setup] creating backend venv..."
  Push-Location $backendDir
  try {
    py -3 -m venv .venv
  } finally {
    Pop-Location
  }
}

if (-not $SkipInstall) {
  Write-Host "[setup] installing backend deps..."
  Push-Location $backendDir
  try {
    & $backendVenvPython -m pip install -r requirements.txt
  } finally {
    Pop-Location
  }

  if (-not (Test-Path (Join-Path $frontendDir "node_modules"))) {
    Write-Host "[setup] installing frontend deps..."
    Push-Location $frontendDir
    try {
      npm install --no-audit --no-fund
    } finally {
      Pop-Location
    }
  }
}

$logsDir = Join-Path $rootDir "logs"
New-Item -ItemType Directory -Force $logsDir | Out-Null
$backendLog = Join-Path $logsDir "dev-backend.log"
$backendErr = Join-Path $logsDir "dev-backend.err.log"

Write-Host "[start] backend..."
$backendProcess = Start-Process `
  -FilePath $backendVenvPython `
  -ArgumentList "-m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000" `
  -WorkingDirectory $backendDir `
  -PassThru `
  -RedirectStandardOutput $backendLog `
  -RedirectStandardError $backendErr

try {
  Write-Host "[wait] backend health check..."
  Wait-BackendHealthy -process $backendProcess
  Write-Host "[ok] backend ready: $backendHealth"

  Write-Host "[start] frontend..."
  Push-Location $frontendDir
  try {
    $env:VITE_CHAT_API_MODE = "sse"
    $env:VITE_CHAT_API_BASE_URL = "http://127.0.0.1:8000/api"
    $env:VITE_CHAT_STREAM_FORMAT = "json"
    npm run dev
  } finally {
    Pop-Location
  }
} finally {
  if ($backendProcess -and -not $backendProcess.HasExited) {
    Write-Host "[stop] backend..."
    Stop-Process -Id $backendProcess.Id -Force
  }
}
