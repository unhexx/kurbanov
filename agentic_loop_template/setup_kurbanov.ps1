# setup_kurbanov.ps1
# Project-specific environment bootstrap for the kurbanov (Telegram AI Consultant) project.
# Adapts the generic agentic loop setup for the structure:
#   - Python code lives in services/consultant_api/
#   - Dependencies in requirements.txt + requirements-dev.txt (pinned)
#   - Supports local smoke mode with SQLite (no Docker required)
#   - Always activates .venv and sets PYTHONPATH correctly
#
# Usage (from project root):
#   powershell -ExecutionPolicy Bypass -File .\agentic_loop_template\setup_kurbanov.ps1
#   powershell -ExecutionPolicy Bypass -File .\agentic_loop_template\setup_kurbanov.ps1 -Smoke
#
# Call this at the start of every Orchestrator cycle and after git pull.

[CmdletBinding()]
param(
    [string]$PythonVersion = "3.12",
    [string]$VenvDir = ".venv",
    [switch]$Smoke,                 # Use SQLite smoke DB instead of Postgres
    [switch]$Dev                    # Also install dev requirements (pytest, ruff)
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$ApiDir = Join-Path $ProjectRoot "services\consultant_api"
$ReqFile = Join-Path $ApiDir "requirements.txt"
$ReqDevFile = Join-Path $ApiDir "requirements-dev.txt"

Write-Host "=== Kurbanov Agentic Loop Environment Bootstrap ===" -ForegroundColor Cyan
Write-Host "Project root: $ProjectRoot" -ForegroundColor Gray
Write-Host "API package:  $ApiDir" -ForegroundColor Gray
if ($Smoke) { Write-Host "Mode: SMOKE (SQLite)" -ForegroundColor Yellow }

# 1. Locate Python 3.12+
Write-Host "`n[1/8] Locating Python $PythonVersion..." -ForegroundColor Yellow
$pythonExe = $null
$candidates = @("python", "python3", "py")
foreach ($candidate in $candidates) {
    try {
        $ver = & $candidate --version 2>&1
        if ($ver -match "Python 3\.(1[2-9])") {
            $pythonExe = $candidate
            Write-Host "  Found: $ver via $candidate" -ForegroundColor Green
            break
        }
    } catch {}
}
if (-not $pythonExe) {
    Write-Error "Python 3.12+ not found in PATH. Please install Python 3.12 and add it to PATH."
    exit 1
}

# 2. Create/repair venv
Write-Host "`n[2/8] Ensuring virtual environment in $VenvDir..." -ForegroundColor Yellow
$venvPath = Join-Path $ProjectRoot $VenvDir
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
$venvPython = Join-Path $venvPath "Scripts\python.exe"

$needsRecreate = $false
if (Test-Path $venvPath) {
    if (-not (Test-Path $activateScript) -or -not (Test-Path $venvPython)) {
        Write-Host "  Existing .venv is broken. Recreating..." -ForegroundColor DarkYellow
        $needsRecreate = $true
    } else {
        try {
            $ver = & $venvPython --version 2>&1
            Write-Host "  Existing venv OK: $ver" -ForegroundColor Green
        } catch {
            $needsRecreate = $true
        }
    }
} else {
    $needsRecreate = $true
}

if ($needsRecreate) {
    if (Test-Path $venvPath) { Remove-Item $venvPath -Recurse -Force -ErrorAction SilentlyContinue }
    Write-Host "  Creating new venv..." -ForegroundColor Yellow
    & $pythonExe -m venv $venvPath
    if ($LASTEXITCODE -ne 0) { Write-Error "Failed to create venv."; exit 1 }
    Write-Host "  Venv created." -ForegroundColor Green
}

# 3. Activate
Write-Host "`n[3/8] Activating .venv..." -ForegroundColor Yellow
. $activateScript
Write-Host "  Activated." -ForegroundColor Green

# 4. Upgrade pip
Write-Host "`n[4/8] Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "  pip upgraded." -ForegroundColor Green

# 5. Install dependencies from the API subpackage
Write-Host "`n[5/8] Installing project dependencies..." -ForegroundColor Yellow
if (Test-Path $ReqFile) {
    python -m pip install -r $ReqFile --quiet
    Write-Host "  Installed from services/consultant_api/requirements.txt" -ForegroundColor Green
} else {
    Write-Warning "requirements.txt not found at $ReqFile"
}

if ($Dev -or $true) {  # Always install dev tools for agentic work (tests, lint)
    if (Test-Path $ReqDevFile) {
        python -m pip install -r $ReqDevFile --quiet
        Write-Host "  Installed dev requirements (pytest, ruff)" -ForegroundColor Green
    }
}

# 6. Verify critical imports (project-specific)
Write-Host "`n[6/8] Verifying key imports..." -ForegroundColor Yellow
$critical = @("fastapi", "pydantic", "sqlalchemy", "httpx", "jinja2")
foreach ($pkg in $critical) {
    try {
        $v = python -c "import $pkg; print($pkg.__version__)" 2>&1
        Write-Host "  $pkg $v" -ForegroundColor Green
    } catch {
        Write-Host "  $pkg NOT importable" -ForegroundColor DarkYellow
    }
}

# 7. Smoke DB preparation (optional, for fast local runs without Docker)
if ($Smoke) {
    Write-Host "`n[7/8] Preparing smoke SQLite DB..." -ForegroundColor Yellow
    $smokeDb = "C:\tmp\kurbanov_smoke.db"
    if (Test-Path $smokeDb) { Remove-Item $smokeDb -Force -ErrorAction SilentlyContinue }
    $env:DATABASE_URL = "sqlite+pysqlite:///$smokeDb"
    $env:ADMIN_API_TOKEN = ""
    Write-Host "  DATABASE_URL set to smoke SQLite. ADMIN_API_TOKEN empty (open admin)." -ForegroundColor Green
} else {
    Write-Host "`n[7/8] Smoke preparation skipped (use -Smoke for local SQLite mode)." -ForegroundColor DarkGray
}

# 8. Git + final instructions
Write-Host "`n[8/8] Git & reactivation info..." -ForegroundColor Yellow
try {
    $branch = git rev-parse --abbrev-ref HEAD 2>&1
    Write-Host "  Current branch: $branch" -ForegroundColor Gray
} catch {}
Write-Host "  Working tree status checked." -ForegroundColor Gray

Write-Host "`n=== Environment ready for agentic loop (kurbanov) ===" -ForegroundColor Cyan
Write-Host "Reactivate in new shell:" -ForegroundColor Gray
Write-Host "  . .\.venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  `$env:PYTHONPATH = 'services\consultant_api'" -ForegroundColor White
Write-Host ""
Write-Host "Run API (local):" -ForegroundColor Gray
Write-Host "  uvicorn app.main:app --app-dir services\consultant_api --reload" -ForegroundColor White
Write-Host ""
Write-Host "Smoke test (no Docker):" -ForegroundColor Gray
Write-Host "  powershell -ExecutionPolicy Bypass -File .\agentic_loop_template\setup_kurbanov.ps1 -Smoke" -ForegroundColor White
Write-Host "  python -m pytest -q --tb=line services\consultant_api\tests" -ForegroundColor White
Write-Host ""
Write-Host "Orchestrator: always call this script first in a new cycle." -ForegroundColor DarkYellow