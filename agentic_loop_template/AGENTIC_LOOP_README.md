# Agentic Loop Template for MiniMax M2.7 + Blackbox (VSCode)

> Self-improving multi-role agentic development loop optimized for **Blackbox AI** in VSCode using the **MiniMax M2.7** model.
> Version: 2.2 (M2.7) | Platform: Windows (PowerShell) | Primary Target: Blackbox + MiniMax M2.7

---

## What This Is

A complete, production-oriented template for running a closed-loop, self-improving agentic development cycle where **MiniMax 2.5** (via Blackbox) sequentially takes on the roles of:

**Orchestrator → Coder → Tester → Debugger → Reviewer**

The agent works iteratively until the task fully meets the specification.

### Key Characteristics

- **Closed loop**: The Reviewer can send control back to the Orchestrator if the task is not complete.
- **Self-improving**: Lessons from each cycle are crystallized into permanent rules in `PROJECT_CONTEXT.md` and `SPRINTPLAN.md`.
- **Deterministic**: Strict JSON handoff between roles for reliable state transfer.
- **Blackbox & non-interactive friendly**: Designed to work reliably when Blackbox spawns new PowerShell processes.

---

## Directory Structure

```
agentic_loop_template/
├── README.md                          # This file (Blackbox + MiniMax 2.5 focused)
├── SYSTEM_PROMPT.md                   # Main system prompt (fill {{placeholders}})
├── AGENT_ROLES.md                     # Detailed instructions for each role
├── HANDOFF_SCHEMA.md                  # JSON handoff contract between roles
├── TOOLS_REGISTRY.md                  # Available tools for the local runner
├── PROJECT_CONTEXT_TEMPLATE.md        # Template for PROJECT_CONTEXT.md
├── SPRINTPLAN_TEMPLATE.md             # Template for SPRINTPLAN.md
├── setup_env.ps1                      # Robust Python venv + requirements bootstrap
├── Agent-Init.ps1                     # One-command setup for Blackbox + VSCode
├── Agent-Init.md                      # Detailed Blackbox + MiniMax 2.5 launch guide
└── Profile-Bootstrap.ps1              # PowerShell profile helper for non-interactive sessions
```

---

## Quick Start (Blackbox + MiniMax 2.5 in VSCode)

### 1. One-time environment preparation

```powershell
cd X:\Your\Project\Root
.\agentic_loop_template\Agent-Init.ps1
```

This script will:
- Create and activate the local Python virtual environment (`.venv`)
- Install dependencies from `pyproject.toml`
- Install `posh-bash-chaining` (for `&&`, `||`, `|&` support)
- Set environment variables optimized for Blackbox agents
- Optionally generate a ready-to-paste starter prompt

### 2. Recommended Blackbox Configuration

**Model**: MiniMax 2.5 (or the highest quality available model)

**Custom Instructions** (add to Blackbox settings):

```
You are participating in a structured Agentic Development Loop using the template in agentic_loop_template/.

Core Rules:
- Follow the cycle: Orchestrator → Coder → Tester → Debugger → Reviewer.
- Always ensure the local Python environment is ready before major work.
- All git commit messages must be written in natural Russian, as a real human mid/senior developer.
- Never mention AI, LLM, agent, MiniMax, Grok, Claude, or any model name in commit messages.
- Work iteratively with small, well-tested changes.
- Use the local .venv for all Python commands.
- Read agentic_loop_template/SYSTEM_PROMPT.md and follow its structure and handoff format.
```

### 3. Starting the Loop

After running `Agent-Init.ps1`, copy the generated prompt (or the example in `Agent-Init.md`) and paste it as your first message to Blackbox.

The agent will:
- Read the system prompt
- Begin as **Orchestrator**
- Create/update `PROJECT_CONTEXT.md` and `SPRINTPLAN.md`
- Start the first planning cycle

---

## How the Cycle Works

```
External Loop (Sprint)
┌─────────────────────────────────────────────────────────────┐
│  [Orchestrator] → [Coder] → [Tester] → [Debugger] → [Reviewer]
│       ↑                                                    │
│       └──────────── NOT DONE ──────────────────────────────┘
│                     DONE → Task Complete
└─────────────────────────────────────────────────────────────┘
```

Inside each role the agent follows:
**PLAN → ACT (max 3 tool calls) → REFLECT → repeat**

---

## Important Rules for Blackbox + MiniMax 2.5

- **Commits must be in Russian** and sound like they were written by a real developer.
- **Never mention** AI, agent, LLM, MiniMax, etc. in commit messages.
- The agent should call `setup_env.ps1` (or `Agent-Init.ps1`) at the start of major cycles to maintain the local Python environment.
- For non-interactive sessions (common with Blackbox), the system automatically disables the PSReadLine handler to avoid breaking output capture.

---

## Recommended Model Settings (MiniMax 2.5)

| Role          | Temperature | Top-P | Max Tokens |
|---------------|-------------|-------|------------|
| Orchestrator  | 0.0         | 0.9   | 4096       |
| Coder         | 0.2         | 0.95  | 8192       |
| Tester        | 0.0         | 0.9   | 4096       |
| Debugger      | 0.2         | 0.95  | 4096       |
| Reviewer      | 0.0         | 0.9   | 4096       |

---

## PowerShell Command to Launch the Cycle

The simplest way to start:

```powershell
cd X:\Path\To\Your\Project
.\agentic_loop_template\Agent-Init.ps1 -OutputFile "blackbox_start_prompt.txt"
```

Then open the generated file and send its content to Blackbox as the first message.

For maximum automation you can combine it with opening the file:

```powershell
.\agentic_loop_template\Agent-Init.ps1 -OutputFile "blackbox_start_prompt.txt"; code "blackbox_start_prompt.txt"
```

---

## Adapting for Other Projects

1. Copy the `agentic_loop_template` folder into your project.
2. Fill all `{{ ... }}` placeholders in `SYSTEM_PROMPT.md`.
3. Create a `TASK_SPECIFICATION.md` with clear requirements.
4. Run `Agent-Init.ps1` and follow the Blackbox instructions in `Agent-Init.md`.

---

## Limitations

- Optimized for Windows + PowerShell + Blackbox + MiniMax 2.5.
- The local runner must support the tools defined in `TOOLS_REGISTRY.md`.
- Maximum recommended 3–4 full cycles before doing an architecture review.

This template is specifically tuned for reliable autonomous development when using **Blackbox AI** with the **MiniMax 2.5** model in Visual Studio Code.