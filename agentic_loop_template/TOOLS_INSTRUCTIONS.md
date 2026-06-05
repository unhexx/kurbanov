# TOOLS_INSTRUCTIONS.md — Limited-Context, M2.7-Optimized Instructions for Windows, Linux and Common Development Tools

**Purpose (for M2.7 prompts):** Use ONLY exact blocks from this file in executor prompts. Copy-paste the full block. Keep total usage under 1500 tokens per subtask. Always reference architecture: eeagent (MCP tools with isolation routing, self-cycle §11, utf8 enforcement via Agent-Init, multi-repo with sync-worktree and gh pre-calls, .agent/ state, blackbox_wrapper for autonomous worktrees).

**Rules for use:**
- Run Agent-Init.ps1 first in every session (enforces UTF-8, PS defaults, Python venv report).
- For GitHub: always pre-call exact gh_* from TOOLS_REGISTRY.md, show full JSON output.
- For multi-repo (eeagent + agentic_loop_template): cd to each clone, run commands with git -C or sync-worktree.ps1, never leave one behind.
- Respect isolation: commands must run inside allowed paths/policies. Use sandbox_requirements when calling via MCP.
- Narrow subtasks only. Verify after each block (run, check output, update .agent/ TODO/DECISIONS/LESSONS).
- UTF-8 always. On Windows prefer .NET for file ops.

**Common (cross-platform, use after Init)**

## Git worktree for isolated execution (used in blackbox_wrapper)
```powershell
$ErrorActionPreference = 'Stop'
$subtaskId = "P0-EXAMPLE"
$ts = Get-Date -Format "yyyyMMdd_HHmmss"
$safe = $subtaskId -replace '[^a-zA-Z0-9_-]', '-'
$branch = "agent/$safe-$ts"
$worktreePath = ".\.agent\worktrees\$safe-$ts"
New-Item -ItemType Directory -Path (Split-Path $worktreePath) -Force | Out-Null
git worktree add -b $branch $worktreePath
# After work: git worktree remove $worktreePath ; git branch -D $branch
```
**When to use:** For autonomous subtask execution. Architecture note: enables safe self-dev without polluting main checkout. Always follow with sync-worktree.ps1 -VerifyOnly after merge.

## Safe file read/write (UTF-8, Windows-safe)
```powershell
$ErrorActionPreference = 'Stop'
# Read
$content = [System.IO.File]::ReadAllText("path\to\file.txt", [System.Text.UTF8Encoding]::new($false))
# Write (with BOM for .ps1 compatibility if needed)
$utf8Bom = [System.Text.UTF8Encoding]::new($true)
[System.IO.File]::WriteAllText("path\to\file.txt", $content, $utf8Bom)
```
**When to use:** All .agent/ , handoff, logs. Architecture: complements Agent-Init defaults and .gitattributes. Never use bare > or Set-Content without explicit.

## Python in project .venv (never system python)
```powershell
$ErrorActionPreference = 'Stop'
$python = ".\.venv\Scripts\python.exe"
& $python -c "import sys; print(sys.executable)"
& $python -m pip list
# Or for memory
& $python -m agentic_loop_template.memory snapshot
```
**When to use:** All Python work. Architecture: from Get-PythonEnvironmentReport in Init. Use for blackbox_wrapper, MCP clients, tests.

## Docker / compose (gateway, central, verification)
```powershell
$ErrorActionPreference = 'Stop'
docker compose -f docker-compose.yml up -d --build
docker compose ps
docker compose logs gateway --tail 50
# Health
curl -f http://localhost:8000/health || echo "not ready"
```
**When to use:** Local gateway for testing live WS / MCP. Architecture: central service for agents and live monitoring.

**Windows (PowerShell specific, run after Init on Win)**

## Encoding self-test and defaults (critical on Russian Windows)
```powershell
$ErrorActionPreference = 'Stop'
$testFile = Join-Path $env:TEMP ("test_utf8_" + (Get-Random) + ".txt")
$russian = "Привет мир! Тест UTF-8: ёжик, テスト, café"
Set-Content -Path $testFile -Value $russian -Encoding utf8 -Force
$read = Get-Content -Path $testFile -Raw -Encoding utf8
Remove-Item $testFile -Force
if ($read.Trim() -ne $russian) { throw "UTF-8 roundtrip failed" }
Write-Host "UTF-8 OK"
```
**When to use:** At start of every Win session. Architecture: enforced by Agent-Init. Prevents mojibake in .agent/, logs, handoffs.

## Safe Set-Content / file ops with defaults
```powershell
$ErrorActionPreference = 'Stop'
$PSDefaultParameterValues['Set-Content:Encoding'] = 'utf8'
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
"content with русский" | Set-Content "file.txt"
```
**When to use:** Scripts, logs. Prefer .NET for binary safety.

## Get reliable Python path (from Init)
```powershell
$ErrorActionPreference = 'Stop'
# Call the report helper from Init or direct
& ".\.venv\Scripts\python.exe" -c "import sys; print(sys.executable)"
```
**When to use:** Before any python call on Win. Architecture: rejects Inkscape/MSStore junk Pythons.

## Windows service / installer patterns (from Install-Eeagent.ps1)
```powershell
$ErrorActionPreference = 'Stop'
# Example: check service
Get-Service -Name "eeagent*" | Select Name, Status, StartType
# Low IL / JobObject context (for isolation checks)
# (see local-agent for full JobObject code)
```
**When to use:** Verification of one-command install, isolation. Architecture: Win fallback for JobObject + Hyper-V stubs.

## JobObject / isolation status (Windows)
```powershell
$ErrorActionPreference = 'Stop'
# Quick check (full impl in launcher)
Write-Host "Check isolation level via policy or process"
```
**When to use:** In policy-aware commands. Tie to sandbox_requirements.

**Notes for M2.7 prompts:**
- Always start prompt with: "Use only exact blocks from TOOLS_INSTRUCTIONS.md. Run after Agent-Init. Respect eeagent isolation + self-cycle §11 + multi-repo sync."
- After block: update .agent/ files, run sync-worktree -VerifyOnly, emit SYNC_DONE.
- For github ops: first emit exact gh_* block from TOOLS_REGISTRY.md and show JSON.
- Verify every block: run it, capture output, log in EXECUTION_LOG.

Add new blocks only after real run verification on Win10 + Arch. Update this file + TOOLS_REGISTRY if gh changes. Seed memory with new gotchas.

**Current coverage target:** 15-20 blocks for Common + Windows (this initial draft). Linux + project-specific in next slice.