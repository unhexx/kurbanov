<#
.SYNOPSIS
    Robust initialization script for Blackbox + MiniMax M2.7 agentic development in VSCode.

.DESCRIPTION
    Prepares a reliable local Python virtual environment and can generate
    a ready-to-use starter prompt for Blackbox (optimized for MiniMax M2.7).

    Key improvements:
    - Automatically creates or repairs broken .venv
    - Clear, step-by-step messages with status
    - Auto-detects task from TODO.md or TASK_SPECIFICATION.md
    - Generates M2.7-aware starter prompt with thinking traces / curated context reminders
#>

[CmdletBinding()]
param(
    [string]$TaskDescription,
    [string]$TaskSpecFile = "TASK_SPECIFICATION.md",
    [string]$OutputFile,
    [switch]$GeneratePromptOnly,
    [int]$MaxTaskLength = 2800
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot

# Force UTF-8 defaults for the entire session (critical for Russian Windows)
# This prevents mojibake in handoff JSONs and other text files.
try {
    $OutputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    $PSDefaultParameterValues['Out-File:Encoding']    = 'utf8'
    $PSDefaultParameterValues['Set-Content:Encoding'] = 'utf8'
    $PSDefaultParameterValues['Add-Content:Encoding'] = 'utf8'
    $PSDefaultParameterValues['Get-Content:Encoding'] = 'utf8'
    $env:PYTHONIOENCODING = 'utf-8'
} catch {}

function Get-AutoTaskDescription {
    param([int]$MaxLength = 2800)

    $candidates = @(
        (Join-Path $ProjectRoot "TASK_SPECIFICATION.md"),
        (Join-Path $ProjectRoot "TODO.md")
    )

    foreach ($file in $candidates) {
        if (Test-Path $file) {
            try {
                $raw = Get-Content $file -Raw -ErrorAction Stop
                if ($raw.Length -gt $MaxLength) {
                    $raw = $raw.Substring(0, $MaxLength) + "`n... (truncated)"
                }
                Write-Host "  Auto-detected task from: $(Split-Path $file -Leaf)" -ForegroundColor Green
                return $raw.Trim()
            } catch {}
        }
    }
    return $null
}

function Generate-AgentStarterPrompt {
    param([string]$Task, [string]$SpecFile = "TASK_SPECIFICATION.md")

    $lines = @(
        "We are starting an autonomous agentic development loop using the template in agentic_loop_template/ for the kurbanov project (Telegram AI Consultant / автоподбор).",
        "",
        "**Current Task:**",
        $Task,
        "",
        "**Instructions:**",
        "",
        "1. First, ensure the local Python environment is ready by running:",
        "   powershell -ExecutionPolicy Bypass -File .\agentic_loop_template\setup_kurbanov.ps1",
        "",
        "2. Activate the virtual environment and set PYTHONPATH:",
        "   . .\.venv\Scripts\Activate.ps1",
        "   `$env:PYTHONPATH = 'services\consultant_api'",
        "",
        "3. Read in this order:",
        "   - agentic_loop_template/README.md",
        "   - agentic_loop_template/SYSTEM_PROMPT.md (M2.7 tuned version)",
        "   - agentic_loop_template/Agent-Init.md",
        "   - $SpecFile",
        "",
        "4. Start as ORCHESTRATOR according to the SYSTEM_PROMPT.",
        "",
        "**M2.7 Best Practices (use these when working with MiniMax M2.7 in Blackbox):**",
        "- Сохраняй thinking traces модели (<think>...</think> или эквивалент), если они выдаются — они сильно улучшают качество длинных итераций.",
        "- Для истории контекста используй curated summary: последние 8-12 сообщений + сжатые итоги предыдущих фаз (что сделано, какие решения приняты, открытые риски). Не заливай сырую историю.",
        "- Следуй таблице рекомендуемых параметров генерации из SYSTEM_PROMPT.md (разные temperature/top-p/top-k для разных ролей).",
        "- Внутри каждой роли применяй Solver Loop (Inspect → Define success → Smallest vertical slice → Proportional verification → Reflect). Максимум 3 tool-вызова без рефлексии.",
        "",
        "Rules:",
        "- Write all git commits in natural Russian, as a real human developer (Евгений Чистяков style).",
        "- Never mention AI, LLM, agent, MiniMax, Grok, Claude, etc. in commit messages.",
        "- Always work inside the local .venv with correct PYTHONPATH for the consultant_api package.",
        "- For fast local testing without Docker/Postgres use: ...\\setup_kurbanov.ps1 -Smoke"
    )

    return ($lines -join "`r`n")
}

# ============================================
# Main Logic - Robust Venv Handling
# ============================================

Write-Host "=== Agentic Loop Environment Initialization ===" -ForegroundColor Cyan
Write-Host "Reminder: Before starting work, the agent must complete the Pre-Flight Checklist in SYSTEM_PROMPT.md (version 2.1)." -ForegroundColor DarkGray
Write-Host "Project: $ProjectRoot" -ForegroundColor Gray

# 1. Locate Python
Write-Host "`n[1/6] Locating Python..." -ForegroundColor Yellow
$python = $null
foreach ($candidate in @("python", "py")) {
    try {
        $ver = & $candidate --version 2>&1
        if ($ver -match "Python 3\.(1[0-9])") {
            $python = $candidate
            Write-Host "  Found: $ver via $candidate" -ForegroundColor Green
            break
        }
    } catch {}
}

if (-not $python) {
    Write-Error "Python 3.10+ not found in PATH."
    exit 1
}

# 2. Robust venv handling
Write-Host "`n[2/6] Ensuring virtual environment..." -ForegroundColor Yellow

$venvPath = Join-Path $ProjectRoot ".venv"
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"

$needsRecreate = $false

if (Test-Path $venvPath) {
    if (-not (Test-Path $activateScript)) {
        Write-Host "  Existing .venv is broken (missing Activate.ps1). Recreating..." -ForegroundColor DarkYellow
        $needsRecreate = $true
    } else {
        # Try to verify the venv Python works
        $venvPython = Join-Path $venvPath "Scripts\python.exe"
        if (Test-Path $venvPython) {
            try {
                $ver = & $venvPython --version 2>&1
                Write-Host "  Existing venv is valid ($ver)" -ForegroundColor Green
            } catch {
                Write-Host "  Existing venv is broken. Recreating..." -ForegroundColor DarkYellow
                $needsRecreate = $true
            }
        } else {
            $needsRecreate = $true
        }
    }
} else {
    $needsRecreate = $true
}

if ($needsRecreate) {
    if (Test-Path $venvPath) {
        Remove-Item $venvPath -Recurse -Force -ErrorAction SilentlyContinue
    }
    Write-Host "  Creating new virtual environment..." -ForegroundColor Yellow
    & $python -m venv $venvPath
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create virtual environment."
        exit 1
    }
    Write-Host "  Virtual environment created successfully." -ForegroundColor Green
}

# 3. Activate
Write-Host "`n[3/6] Activating virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path $activateScript)) {
    Write-Error "Activation script is missing after creation attempt."
    exit 1
}
. $activateScript
Write-Host "  Virtual environment activated." -ForegroundColor Green

# 4. Upgrade pip + install dependencies
Write-Host "`n[4/6] Upgrading pip and installing dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet

if (Test-Path (Join-Path $ProjectRoot "pyproject.toml")) {
    python -m pip install -e "$ProjectRoot.[dev]" --quiet
    Write-Host "  Dependencies installed from pyproject.toml." -ForegroundColor Green
} elseif (Test-Path (Join-Path $ProjectRoot "requirements.txt")) {
    python -m pip install -r (Join-Path $ProjectRoot "requirements.txt") --quiet
    Write-Host "  Dependencies installed from requirements.txt." -ForegroundColor Green
} else {
    Write-Host "  No dependency file found. Skipping installation." -ForegroundColor DarkYellow
}

# 5. Set helpful environment variables
Write-Host "`n[5/6] Setting agent-friendly environment variables..." -ForegroundColor Yellow
[Environment]::SetEnvironmentVariable("POSH_BASH_CHAINING_NONINTERACTIVE", "1", "User")
$env:POSH_BASH_CHAINING_NONINTERACTIVE = "1"
Write-Host "  Variables set for non-interactive sessions." -ForegroundColor Green

# 6. Prompt generation
Write-Host "`n[6/6] Checking for task description..." -ForegroundColor Yellow

$finalTask = $TaskDescription
if (-not $finalTask) {
    $finalTask = Get-AutoTaskDescription -MaxLength $MaxTaskLength
}

if ($finalTask) {
    $prompt = Generate-AgentStarterPrompt -Task $finalTask -SpecFile $TaskSpecFile

    if ($OutputFile) {
        $out = if ([System.IO.Path]::IsPathRooted($OutputFile)) { $OutputFile } else { Join-Path $ProjectRoot $OutputFile }
        Set-Content -Path $out -Value $prompt -Encoding UTF8
        Write-Host "  Starter prompt saved to: $out" -ForegroundColor Green
    }

    Write-Host "`n=== Ready-to-use prompt for Blackbox ===" -ForegroundColor Yellow
    Write-Host $prompt
    Write-Host "========================================" -ForegroundColor Yellow
} else {
    Write-Host "  No task description found automatically." -ForegroundColor DarkYellow
}

Write-Host "`n=== Environment initialization completed successfully ===" -ForegroundColor Green