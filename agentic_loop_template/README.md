# Agentic Loop Template (MiniMax M2.7)

A complete, self-contained template for running a closed-loop, self-improving multi-role agentic development cycle powered by **MiniMax M2.7**.

The agent cycles through roles (Orchestrator в†’ Coder в†’ Tester в†’ Debugger в†’ Reviewer) until the task fully meets the specification. All work happens inside a **local Python virtual environment** that is created and maintained by the agent itself.

## Key Improvements in This Version

- **Mandatory local Python environment**: The Orchestrator must ensure a `.venv` exists and all requirements from `pyproject.toml` (or `requirements.txt`) are installed at the beginning of every cycle.
- **Non-interactive friendly**: Designed to work when AI agents (Blackbox, Continue, etc.) spawn fresh PowerShell processes.
- **English primary language** with explicit requirement for **Russian commit messages** written in the voice of a real human developer (no mention of AI, LLM, agent, or model names in commits).
- Aligned with the project's root `AGENTS.md` (portable rules + Solver Loop).

## Directory Structure

```
agentic_loop_template/
в”њв”Ђв”Ђ README.md
в”њв”Ђв”Ђ SYSTEM_PROMPT.md              # Main system prompt
в”њв”Ђв”Ђ AGENT_ROLES.md
в”њв”Ђв”Ђ HANDOFF_SCHEMA.md
в”њв”Ђв”Ђ TOOLS_REGISTRY.md
в”њв”Ђв”Ђ PROJECT_CONTEXT_TEMPLATE.md
в”њв”Ђв”Ђ SPRINTPLAN_TEMPLATE.md
в”њв”Ђв”Ђ setup_kurbanov.ps1            # Kurbanov-specific (preferred for this project)
├── setup_env.ps1                 # Generic venv bootstrap (fallback)
в”њв”Ђв”Ђ Profile-Bootstrap.ps1         # PowerShell profile helper
в”њв”Ђв”Ђ Agent-Init.ps1                # Robust setup for Blackbox + VSCode (auto-heals broken .venv)
в””в”Ђв”Ђ Agent-Init.md                 # Detailed guide for Blackbox + MiniMax M2.7 in VSCode
```

## Quick Start (Recommended for Blackbox + MiniMax M2.7)

1. Copy the template into your project root.
2. Fill **all** `{{ ... }}` placeholders in `SYSTEM_PROMPT.md` (see the Pre-Flight Checklist inside it).
3. Create your main specification file (e.g. `TASK_SPECIFICATION.md` or `TODO.md`).
4. **For Blackbox + VSCode users** (strongly recommended):
   ```powershell
   .\agentic_loop_template\Agent-Init.ps1
   ```
   This prepares the Python environment and generates a ready-to-use starter prompt.

5. Start the loop by sending the content of `SYSTEM_PROMPT.md` (with placeholders filled) as the system prompt to MiniMax M2.7 via Blackbox.

See `Agent-Init.md` for the detailed Blackbox + VSCode launch guide, including recommended Custom Instructions and the first message.

## Environment Management (Critical)

The agent **must** maintain a local Python environment:

- At the start of every cycle, the **Orchestrator** should call:
  ```powershell
  powershell -ExecutionPolicy Bypass -File .\\agentic_loop_template\\setup_kurbanov.ps1
  ```
- The script is idempotent and prefers `pyproject.toml`.
- Never run Python commands outside the activated `.venv`.

See `setup_env.ps1` for details.

## Commit Rules (Strict)

All git commits **must** be written in natural Russian, in the voice of a real mid/senior human developer who has been working on the project for months.

**Forbidden** in commit messages:
- Any mention of AI, LLM, agent, MiniMax, Grok, Claude, "as an assistant", "РЅРµР№СЂРѕСЃРµС‚СЊ", "Р°РіРµРЅС‚", etc.

Good examples (from real developer style):
- "РґРѕР±Р°РІРёР» Р±РѕР»РµРµ СѓСЃС‚РѕР№С‡РёРІС‹Р№ РїР°СЂСЃРµСЂ Р±Р»РѕРєРѕРІ РґР»СЏ report_*.txt"
- "РїРѕС‡РёРЅРёР» РЅРѕСЂРјР°Р»РёР·Р°С†РёСЋ РЎРќРР›РЎ Рё С‚РµР»РµС„РѕРЅРѕРІ, РґРѕР±Р°РІРёР» С‚РµСЃС‚С‹ РЅР° edge cases"

The Orchestrator and Reviewer are responsible for enforcing this rule.

## Adaptation to MiniMax M2.7

This template is tuned for MiniMax M2.7. Recommended settings per role (including thinking traces and context summarization) are included in `SYSTEM_PROMPT.md`.

It is designed to be compatible with the portable rules in the root `AGENTS.md` of the host project.

## Standalone Archive

A ready-to-use zip of this template (for starting new autonomous agentic projects) is provided separately as `agentic_loop_template_v2.zip`.

## Applying to an Existing Project

1. Copy the template.
2. Wire the `agentic_loop_template/setup_kurbanov.ps1` call into your workflow (called by Orchestrator at start of every cycle).
3. Update root `AGENTS.md` (or equivalent) with a link to the new `agentic_loop_template/`.
4. Add a note in the root README about the autonomous development loop.

## Recommendations (Added for This Project)

- Always run the environment bootstrap as the very first action of the Orchestrator in cycle 0 and after any `git pull`.
- Keep `PROJECT_CONTEXT.md` under 3000 tokens by aggressive summarization.
- After 3 failed cycles without reaching DONE вЂ” force an architecture review step.
- For heavy data-processing projects (like leak-data-importer), add a dedicated "Data Sanity Checker" role if needed.

---

**License**: MIT (same as host project)

Use this template responsibly and only on codebases you have full rights to modify.
