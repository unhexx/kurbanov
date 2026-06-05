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

## Linux (bash, for remote agents and sandboxes)

## One-command install (uv tool + systemd, from install.sh)
```bash
set -euo pipefail
# curl -fsSL <url>/install.sh | bash -s -- --central https://central.example.com --token xxxxx
# or with --from 'git+https://...@main#subdirectory=agent' --non-interactive
curl -fsSL https://raw.githubusercontent.com/unhexx/eegent/main/installers/linux/install.sh | bash -s -- --central "$CENTRAL" --token "$TOKEN"
```
**When to use:** Linux agent deploy. Architecture: uv tool for isolation, systemd user service, supports git-from for self-hosted no PyPI. Non-interactive for CI.

## Systemd service management (Linux)
```bash
systemctl --user daemon-reload
systemctl --user enable --now eeagent-agent
systemctl --user status eeagent-agent --no-pager
journalctl --user -u eeagent-agent -f
```
**When to use:** After install or restart. Architecture: user service by default, respects XDG_CONFIG_HOME.

## Firecracker / persistent sandbox status (Linux isolation)
```bash
# Check guest status (from poc_firecracker)
ls /var/lib/eeagent-sandbox/ || echo "no sandbox"
# or via vsock connector test
echo "ping" | socat - UNIX-CONNECT:/tmp/eeagent-guest.sock || echo "no guest"
```
**When to use:** Verify isolation for Linux remote agents. Architecture: persistent Firecracker + guest_command_server + policy.

## uv tool run / exec (Linux python tools)
```bash
uv tool run eeagent-agent --mode ws
# or for subtask
uv tool run --from git+https://... eeagent-agent --help
```
**When to use:** Run without full install shim. Architecture: matches project uv stack, for blackbox_wrapper Linux paths.

## Project-specific verified (eeagent self-dev tools)

## Sync worktree (multi-repo, before any PLAN per §11)
```powershell
$ErrorActionPreference = 'Stop'
powershell -ExecutionPolicy Bypass -File .\scripts\sync-worktree.ps1 -VerifyOnly
# or with main clone
git -C 'C:\_PROJECT\eegent' powershell -ExecutionPolicy Bypass -File .\scripts\sync-worktree.ps1 -MainClonePath 'C:\_PROJECT\eegent'
# Expect: SYNC_DONE: main=... verified=verify
```
**When to use:** Every cycle start/end. Architecture: keeps eeagent + kurbanov template in sync, emits machine-readable marker.

## Agent-Init + self-test (always first)
```powershell
$ErrorActionPreference = 'Stop'
powershell -ExecutionPolicy Bypass -File .\agentic_loop_template\Agent-Init.ps1
# Check output for: UTF-8 self-test passed (Russian roundtrip OK via defaults)
# Then: . .\.venv\Scripts\Activate.ps1
```
**When to use:** Before any task. Architecture: enforces PS defaults, PYTHONIOENCODING, venv report, .gitattributes.

## Blackbox wrapper call (autonomous subtask)
```powershell
$ErrorActionPreference = 'Stop'
& ".\.venv\Scripts\python.exe" skills/blackbox_wrapper.py --subtask-id "P0-EXAMPLE" --autonomous --yolo
# or simulate
& ".\.venv\Scripts\python.exe" skills/blackbox_wrapper.py --subtask-id "P0-EXAMPLE" --simulate
```
**When to use:** For self-dev loops. Architecture: creates worktree, injects .agent/ state, parses structured, updates TODO/DECISIONS/LESSONS.

## Memory snapshot / update (institutional memory)
```powershell
$ErrorActionPreference = 'Stop'
& ".\.venv\Scripts\python.exe" -m agentic_loop_template.memory snapshot
& ".\.venv\Scripts\python.exe" -m agentic_loop_template.memory query --top 5 --category 'Windows & PowerShell Gotchas'
# Update (Reviewer):
& '.\agentic_loop_template\memory\Invoke-AgenticMemory.ps1' update -Category 'Common Failure Patterns' -Description 'Always use exact gh_* before github ops'
```
**When to use:** Orchestrator start, Reviewer end. Architecture: workspace-scoped, dedup, compaction.

## Gateway health / monitor (live control plane)
```powershell
$ErrorActionPreference = 'Stop'
curl -f http://localhost:8000/health
curl -s http://localhost:8000/agentic/monitor | ConvertFrom-Json | Select executors, tasks
# WS test: use ws client or curl for /ws/ui but prefer in code
```
**When to use:** Verify live broadcasts, agents status. Architecture: central for WS /ws/ui agents:updated etc.

## gh pre-calls (exact from TOOLS_REGISTRY, before any github remote)
```powershell
$ErrorActionPreference = 'Stop'
gh auth status --hostname github.com 2>&1 | ConvertTo-Json -Depth 4 -Compress
gh repo view --json name,owner,nameWithOwner,defaultBranchRef,description,url | ConvertTo-Json -Depth 4 -Compress
$head = 'feature/your-feature'
gh pr list --head $head --state all --json number,title,state,headRefName,baseRefName,url | ConvertTo-Json -Depth 6 -Compress
```
**When to use:** Before push, PR, merge on github (eeagent + kurbanov). Show full output. Architecture: §8 enforcement, never raw git on github remote.

**Notes for M2.7 prompts (update):**
- Always start prompt with: "Use only exact blocks from TOOLS_INSTRUCTIONS.md. Run after Agent-Init. Respect eeagent isolation + self-cycle §11 + multi-repo sync."
- Linux blocks for bash/firecracker in remote agents.
- Project blocks for loop self-dev (wrapper, sync, memory, gh).
- After any block: update .agent/, sync-worktree -VerifyOnly, emit SYNC_DONE.
- Verify: run block, capture, log.

Add new only after verification on Win10 + Arch. This extends to ~30 blocks total. Seed memory with Linux gotchas too.

**Coverage now:** Full Common + Windows + Linux + Project (initial for 002). Next: M2.7 opt + integration.