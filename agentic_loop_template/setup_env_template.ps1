# setup_env.ps1 вЂ” РџРѕРґРіРѕС‚РѕРІРєР° РѕРєСЂСѓР¶РµРЅРёСЏ РґР»СЏ РїСЂРѕРµРєС‚Р°
# Р—Р°РїСѓСЃРє: powershell -ExecutionPolicy Bypass -File .\\agentic_loop_template\\setup_kurbanov.ps1

param(
    [string]$PythonVersion = "3.11",
    [string]$VenvDir = ".venv",
    [string]$RequirementsFile = "requirements.txt"
)

$ErrorActionPreference = "Stop"

Write-Host "=== РџРѕРґРіРѕС‚РѕРІРєР° РѕРєСЂСѓР¶РµРЅРёСЏ ===" -ForegroundColor Cyan

# в”Ђв”Ђв”Ђ 1. РџСЂРѕРІРµСЂРєР° Python в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
Write-Host "`n[1/6] РџСЂРѕРІРµСЂРєР° Python..." -ForegroundColor Yellow
$pythonExe = $null
foreach ($candidate in @("python", "python3", "py")) {
    try {
        $version = & $candidate --version 2>&1
        if ($version -match "Python $PythonVersion") {
            $pythonExe = $candidate
            Write-Host "  вњ“ РќР°Р№РґРµРЅ: $version ($candidate)" -ForegroundColor Green
            break
        }
    } catch { }
}

if (-not $pythonExe) {
    Write-Error "Python $PythonVersion РЅРµ РЅР°Р№РґРµРЅ. РЈСЃС‚Р°РЅРѕРІРёС‚Рµ Python $PythonVersion Рё РґРѕР±Р°РІСЊС‚Рµ РІ PATH."
    exit 1
}

# в”Ђв”Ђв”Ђ 2. РЎРѕР·РґР°РЅРёРµ РІРёСЂС‚СѓР°Р»СЊРЅРѕРіРѕ РѕРєСЂСѓР¶РµРЅРёСЏ в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
Write-Host "`n[2/6] РЎРѕР·РґР°РЅРёРµ РІРёСЂС‚СѓР°Р»СЊРЅРѕРіРѕ РѕРєСЂСѓР¶РµРЅРёСЏ РІ $VenvDir..." -ForegroundColor Yellow
if (Test-Path $VenvDir) {
    Write-Host "  вњ“ РћРєСЂСѓР¶РµРЅРёРµ СѓР¶Рµ СЃСѓС‰РµСЃС‚РІСѓРµС‚, РїСЂРѕРїСѓСЃРєР°РµРј СЃРѕР·РґР°РЅРёРµ." -ForegroundColor Green
} else {
    & $pythonExe -m venv $VenvDir
    if ($LASTEXITCODE -ne 0) { Write-Error "РќРµ СѓРґР°Р»РѕСЃСЊ СЃРѕР·РґР°С‚СЊ venv."; exit 1 }
    Write-Host "  вњ“ РћРєСЂСѓР¶РµРЅРёРµ СЃРѕР·РґР°РЅРѕ." -ForegroundColor Green
}

# в”Ђв”Ђв”Ђ 3. РђРєС‚РёРІР°С†РёСЏ РѕРєСЂСѓР¶РµРЅРёСЏ в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
Write-Host "`n[3/6] РђРєС‚РёРІР°С†РёСЏ РѕРєСЂСѓР¶РµРЅРёСЏ..." -ForegroundColor Yellow
$activateScript = Join-Path $VenvDir "Scripts\Activate.ps1"
if (-not (Test-Path $activateScript)) {
    Write-Error "РЎРєСЂРёРїС‚ Р°РєС‚РёРІР°С†РёРё РЅРµ РЅР°Р№РґРµРЅ: $activateScript"
    exit 1
}
. $activateScript
Write-Host "  вњ“ РћРєСЂСѓР¶РµРЅРёРµ Р°РєС‚РёРІРёСЂРѕРІР°РЅРѕ." -ForegroundColor Green

# в”Ђв”Ђв”Ђ 4. РћР±РЅРѕРІР»РµРЅРёРµ pip в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
Write-Host "`n[4/6] РћР±РЅРѕРІР»РµРЅРёРµ pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "  вњ“ pip РѕР±РЅРѕРІР»С‘РЅ." -ForegroundColor Green

# в”Ђв”Ђв”Ђ 5. РЈСЃС‚Р°РЅРѕРІРєР° Р·Р°РІРёСЃРёРјРѕСЃС‚РµР№ в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
Write-Host "`n[5/6] РЈСЃС‚Р°РЅРѕРІРєР° Р·Р°РІРёСЃРёРјРѕСЃС‚РµР№ РёР· $RequirementsFile..." -ForegroundColor Yellow
if (Test-Path $RequirementsFile) {
    python -m pip install -r $RequirementsFile --quiet
    if ($LASTEXITCODE -ne 0) { Write-Error "РћС€РёР±РєР° СѓСЃС‚Р°РЅРѕРІРєРё Р·Р°РІРёСЃРёРјРѕСЃС‚РµР№."; exit 1 }
    Write-Host "  вњ“ Р—Р°РІРёСЃРёРјРѕСЃС‚Рё СѓСЃС‚Р°РЅРѕРІР»РµРЅС‹." -ForegroundColor Green
} elseif (Test-Path "pyproject.toml") {
    python -m pip install -e ".[dev]" --quiet
    if ($LASTEXITCODE -ne 0) { Write-Error "РћС€РёР±РєР° СѓСЃС‚Р°РЅРѕРІРєРё С‡РµСЂРµР· pyproject.toml."; exit 1 }
    Write-Host "  вњ“ РЈСЃС‚Р°РЅРѕРІР»РµРЅРѕ С‡РµСЂРµР· pyproject.toml." -ForegroundColor Green
} else {
    Write-Host "  вљ  Р¤Р°Р№Р» Р·Р°РІРёСЃРёРјРѕСЃС‚РµР№ РЅРµ РЅР°Р№РґРµРЅ ($RequirementsFile / pyproject.toml). РџСЂРѕРїСѓСЃРєР°РµРј." -ForegroundColor DarkYellow
}

# в”Ђв”Ђв”Ђ 6. РџСЂРѕРІРµСЂРєР° git в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
Write-Host "`n[6/6] РџСЂРѕРІРµСЂРєР° git..." -ForegroundColor Yellow
try {
    $gitVersion = git --version 2>&1
    Write-Host "  вњ“ $gitVersion" -ForegroundColor Green
    
    $currentBranch = git rev-parse --abbrev-ref HEAD 2>&1
    Write-Host "  вњ“ РўРµРєСѓС‰Р°СЏ РІРµС‚РєР°: $currentBranch" -ForegroundColor Green
    
    $gitStatus = git status --short 2>&1
    if ($gitStatus) {
        Write-Host "  вљ  РќРµР·Р°РєРѕРјРјРёС‡РµРЅРЅС‹Рµ РёР·РјРµРЅРµРЅРёСЏ:" -ForegroundColor DarkYellow
        $gitStatus | ForEach-Object { Write-Host "    $_" }
    } else {
        Write-Host "  вњ“ Р Р°Р±РѕС‡Р°СЏ РґРёСЂРµРєС‚РѕСЂРёСЏ С‡РёСЃС‚Р°СЏ." -ForegroundColor Green
    }
} catch {
    Write-Host "  вљ  git РЅРµ РЅР°Р№РґРµРЅ РёР»Рё РЅРµ РёРЅРёС†РёР°Р»РёР·РёСЂРѕРІР°РЅ." -ForegroundColor DarkYellow
}

# в”Ђв”Ђв”Ђ РС‚РѕРі в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
Write-Host "`n=== РћРєСЂСѓР¶РµРЅРёРµ РіРѕС‚РѕРІРѕ Рє СЂР°Р±РѕС‚Рµ ===" -ForegroundColor Cyan
Write-Host "Р”Р»СЏ Р°РєС‚РёРІР°С†РёРё РѕРєСЂСѓР¶РµРЅРёСЏ РІ РЅРѕРІРѕР№ СЃРµСЃСЃРёРё: . .\$VenvDir\Scripts\Activate.ps1" -ForegroundColor Gray

