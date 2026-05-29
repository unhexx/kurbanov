# Agent Init for Blackbox + MiniMax2.5 in VSCode

This guide helps you (or your agent) correctly bootstrap the **agentic_loop_template** when working inside **Visual Studio Code + Blackbox AI agent** using **MiniMax2.5**.

## Why This File Exists

Blackbox (and most VSCode AI agents) have specific behaviors that break normal agentic loops:

- Every command is often executed in a **fresh PowerShell process** (non-interactive).
- `&&`, `||`, `|&` do not work by default.
- The PSReadLine Enter handler can break output capture.
- The agent frequently loses the activated Python virtual environment.
- Profile loading is unreliable.

This document + `Agent-Init.ps1` / `setup_kurbanov.ps1` solve these problems for the kurbanov (Telegram AI Consultant) project and any similar Python project with code in a subdirectory.

---

## Step 1: One-time Human Setup (Run this yourself)

Open PowerShell in the project root and run:

```powershell
cd X:\LocalRepo\kurbanov
.\agentic_loop_template\Agent-Init.ps1
```

This script will:
- Create and activate the local `.venv`
- Install all dependencies from `pyproject.toml`
- Install the `posh-bash-chaining` tool into your PowerShell profile (with Blackbox-friendly settings)
- Set helpful environment variables
- Print the exact text you should give to the Blackbox agent

---

## Step 2: Recommended Blackbox Custom Instructions

Before the agent starts, make sure it has the latest `SYSTEM_PROMPT.md` (version 2.1) which contains the **Pre-Flight Checklist**. The agent must verify that all placeholders are filled before beginning any work.

Go to Blackbox settings → Custom Instructions (or System Prompt) and add the following block:

```text
You are working on the kurbanov project (MVP Telegram AI Consultant for car selection / автоподбор) using the Agentic Loop Template in agentic_loop_template/.

CRITICAL RULES:

1. Always start a new task by ensuring the local Python environment is ready:
   powershell -ExecutionPolicy Bypass -File .\agentic_loop_template\Agent-Init.ps1

2. Never run Python commands outside the activated .venv. Always activate it first if needed:
   . .\.venv\Scripts\Activate.ps1

3. For shell commands that use chaining, prefer using the posh-bash-chaining functions or run commands via the bootstrap.

4. All git commit messages MUST be written in natural Russian, as a real human mid/senior developer. Never mention AI, LLM, agent, MiniMax, Grok, or "as an assistant" in commits.

5. Work iteratively with small, well-tested changes. Run tests frequently.

6. When the task is complex, follow the structure from agentic_loop_template/SYSTEM_PROMPT.md (Orchestrator → Coder → Tester → Debugger → Reviewer).

7. Always read TASK_SPECIFICATION.md (or equivalent) before starting implementation.
```

---

## Step 3: First Message to the Agent (Copy-Paste)

Use this as the first message when starting a new autonomous development session:

```
We are using the Agentic Loop Template located in agentic_loop_template/.

Please read the following files in order:
1. agentic_loop_template/README.md
2. agentic_loop_template/SYSTEM_PROMPT.md
3. agentic_loop_template/Agent-Init.md

Then:
- Run the environment initialization: powershell -ExecutionPolicy Bypass -File .\agentic_loop_template\Agent-Init.ps1
- Activate the venv
- Read the main task specification (TASK_SPECIFICATION.md or equivalent)
- Start acting as ORCHESTRATOR and begin the agentic loop.

Use natural Russian developer-style commit messages only.
```

---

## Recommended VSCode + Blackbox Settings

- **Default Shell**: PowerShell (preferably PowerShell 7 if available)
- **Execution Policy**: Make sure it allows running local scripts:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```
- **Terminal**: Use the integrated terminal (not external).
- **Model**: MiniMax2.5 (or the closest available high-quality model)
- **Temperature**: 0.0 – 0.2 for planning and review roles (let the agent manage this via instructions)

---

## Environment Variables That Help Blackbox

The `Agent-Init.ps1` sets these variables. You can also set them manually:

```powershell
$env:POSH_BASH_CHAINING_NONINTERACTIVE = "1"
$env:BLACKBOX_AGENT_MODE = "1"
```

These tell the tools to behave safely when output is being captured by an agent.

---

## Common Problems & Solutions

| Problem                              | Solution |
|--------------------------------------|--------|
| Agent uses `&&` and it fails         | Use the posh-bash-chaining tool or run `Agent-Init.ps1` first |
| No output returned from commands     | Make sure `POSH_BASH_CHAINING_NONINTERACTIVE=1` is set |
| Python commands fail (no module)     | Run `Agent-Init.ps1` or manually activate `.venv` |
| Agent forgets previous context       | Keep `PROJECT_CONTEXT.md` and `SPRINTPLAN.md` updated |
| Commits contain "AI" or "agent"      | Explicitly remind the agent in every major handoff |

---

## Generating a Task-Specific Starter Prompt (Recommended)

The easiest and recommended way is to let the script **auto-detect** the task:

```powershell
.\agentic_loop_template\Agent-Init.ps1 -OutputFile "start_prompt.txt"
```

The script will automatically search for the task description in this priority order:
1. `TASK_SPECIFICATION.md` (the official spec)
2. `TODO.md`
3. `docs/TASK_SPECIFICATION.md`

When reading `TODO.md`, it tries to intelligently extract the most relevant sections (e.g. "## Current Tasks", "## In Progress", "## TODO"). For specification files it takes the main description block. This produces a much cleaner and more useful prompt than just dumping the raw file.

### Manual mode (if you want full control)

```powershell
.\agentic_loop_template\Agent-Init.ps1 `
    -TaskDescription "Реализовать улучшенный парсер dossier-отчётов..." `
    -TaskSpecFile "TASK_SPECIFICATION.md" `
    -OutputFile "start_prompt.txt"
```

### Example of Generated Prompt Content

The generated prompt will include:
- Your specific task
- Instructions to read the template files
- Command to initialize the environment
- Reminder about Russian developer-style commits
- Instruction to start as ORCHESTRATOR

## Robust Virtual Environment Handling (New in v2)

`Agent-Init.ps1` now has significantly improved reliability for the Python virtual environment:

- It automatically detects if `.venv` is missing, broken, or corrupted.
- If problems are detected, it **fully removes and recreates** the virtual environment.
- It verifies that the Python inside `.venv` is actually working before proceeding.
- Clear messages are shown at each step (e.g. "Existing .venv is broken. Recreating...", "Virtual environment created successfully").

This greatly reduces issues when the agent or you run the script multiple times, or after pulling changes that affect dependencies.

You no longer need to manually delete `.venv` when something goes wrong — the script handles it.

## Quick One-Liner for the Agent (when it gets confused)

If the agent loses the environment, tell it:

> "Run this first: `powershell -ExecutionPolicy Bypass -File .\agentic_loop_template\Agent-Init.ps1` then activate the venv and continue."

---

## Files to Give the Agent

When starting a serious autonomous session, give the agent access to read:

- `agentic_loop_template/README.md`
- `agentic_loop_template/SYSTEM_PROMPT.md`
- `agentic_loop_template/Agent-Init.md`
- `TASK_SPECIFICATION.md` (your actual task spec)
- `pyproject.toml`

This combination gives the agent enough context to work autonomously and correctly with Blackbox + MiniMax2.5 in VSCode.

---

**Last updated:** 2026-05-28  
**Compatible with:** Blackbox AI in VSCode + MiniMax2.5 + Windows PowerShell
