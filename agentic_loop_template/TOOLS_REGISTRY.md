# TOOLS REGISTRY — Tools for the Agentic Development Loop

> This registry defines all tools available to the agent during the loop.
> Extend this file when adding new capabilities to your local runner.

---

## Tool Call Format

The model emits a JSON object. Your local runner executes it and returns the result.

**Request (from model):**
```json
{
  "tool": "tool_name",
  "param1": "value1",
  "param2": "value2",
  "purpose": "Short explanation why this tool is being called"
}
```

**Response (from your runner):**
```json
{
  "tool": "tool_name",
  "exit_code": 0,
  "stdout": "...",
  "stderr": "...",
  "elapsed_ms": 1234
}
```

**Important for Blackbox / non-interactive usage:**
- Always return both `stdout` and `stderr`.
- Include `elapsed_ms` when possible.
- Never swallow errors silently.

---

## Core Tools

### `powershell` — Execute commands in Windows PowerShell

| Field         | Type   | Required | Description |
|---------------|--------|----------|-------------|
| `command`     | string | yes      | PowerShell command to execute |
| `working_dir` | string | no       | Working directory (default: project root) |
| `timeout_sec` | int    | no       | Timeout in seconds (default: 120) |

**Best Practice Examples:**

```json
{
  "tool": "powershell",
  "command": "powershell -ExecutionPolicy Bypass -File .\\agentic_loop_template\\setup_kurbanov.ps1",
  "purpose": "Bootstrap Python venv and install dependencies (MANDATORY at start of cycle)"
}
```

```json
{
  "tool": "powershell",
  "command": "git status --porcelain",
  "purpose": "Check for uncommitted changes before major implementation"
}
```

**Rules:**
- Always use Windows path separators (`\`)
- Activate venv explicitly: `.\.venv\Scripts\Activate.ps1`
- Run Python via: `.\.venv\Scripts\python.exe`
- Prefer full commands over interactive mode

---

### `read_file` — Read file contents

| Field       | Type   | Required | Description |
|-------------|--------|----------|-------------|
| `path`      | string | yes      | Relative path from project root |
| `encoding`  | string | no       | Default: utf-8 |
| `lines_from`| int    | no       | Start line (1-based) |
| `lines_to`  | int    | no       | End line |

**Best Practice:**
```json
{
  "tool": "read_file",
  "path": "src/leak_data_importer/importers/txt_report.py",
  "lines_from": 480,
  "lines_to": 520,
  "purpose": "Review current implementation of parse_to_graph before extending entity types"
}
```

---

### `write_file` — Write / overwrite a file

| Field     | Type   | Required | Description |
|-----------|--------|----------|-------------|
| `path`    | string | yes      | Relative path from project root |
| `content` | string | yes      | Full file content |
| `encoding`| string | no       | Default: utf-8 |

**Best Practice:**
```json
{
  "tool": "write_file",
  "path": "src/leak_data_importer/graph/factories.py",
  "content": "# full file content here...",
  "purpose": "Add make_vehicle and make_sim_card factories as per new entity model"
}
```

---

### `append_file` — Append content to a file

| Field     | Type   | Required | Description |
|-----------|--------|----------|-------------|
| `path`    | string | yes      | Relative path |
| `content` | string | yes      | Text to append |

**Best Practice (for logs):**
```json
{
  "tool": "append_file",
  "path": "PROJECT_CONTEXT.md",
  "content": "\n\n## Cycle 2 — 2026-05-28\n\n**Lessons learned:**\n- Always run setup_env at the beginning of a cycle\n- Entity resolution needs fuzzy matching across files",
  "purpose": "Record self-improvement insights from current cycle"
}
```

---

### `list_dir` — List directory contents

| Field       | Type | Required | Description |
|-------------|------|----------|-------------|
| `path`      | string | yes    | Relative path |
| `recursive` | bool   | no     | Default: false |
| `depth`     | int    | no     | Max recursion depth (default: 1) |

**Best Practice:**
```json
{
  "tool": "list_dir",
  "path": "src/leak_data_importer",
  "recursive": true,
  "depth": 2,
  "purpose": "Understand current module structure before planning new importers"
}
```

---

### `search_replace` — Precise search & replace in a file

| Field       | Type   | Required | Description |
|-------------|--------|----------|-------------|
| `path`      | string | yes      | File to modify |
| `search`    | string | yes      | Exact text or regex to find |
| `replace`   | string | yes      | Replacement text |
| `use_regex` | bool   | no       | Default: false |

**Best Practice (preferred over write_file for small changes):**
```json
{
  "tool": "search_replace",
  "path": "src/leak_data_importer/importers/txt_report.py",
  "search": "from leak_data_importer.graph import (",
  "replace": "from leak_data_importer.graph import (\n    make_vehicle,\n    registered_at,",
  "purpose": "Add missing graph factories required for parse_to_graph"
}
```

---

### `git_status` — Get repository status

No required parameters.

**Best Practice:**
```json
{
  "tool": "git_status",
  "purpose": "Check for uncommitted changes before creating a new feature branch"
}
```

---

### `git_commit` — Create a commit

| Field     | Type    | Required | Description |
|-----------|---------|----------|-------------|
| `message` | string  | yes      | Commit message **in natural Russian**, written as a real developer |
| `add_all` | boolean | no       | Run `git add -A` first (default: true) |
| `files`   | array   | no       | Specific files to add |

**Strict Rule:**
Never use words like: AI, LLM, agent, MiniMax, Grok, Claude, нейросеть, "as an assistant", "автоматически" in the commit message.

**Best Practice Examples:**
```json
{
  "tool": "git_commit",
  "message": "добавил поддержку make_vehicle и make_address в графовом режиме",
  "add_all": true,
  "purpose": "Зафиксировать расширение графовой модели"
}
```

```json
{
  "tool": "git_commit",
  "message": "починил нормализацию телефонов и добавил тесты на edge-кейсы с +7 и 8",
  "purpose": "Улучшить качество парсинга реальных отчётов"
}
```

---

### `run_tests` — Run tests

| Field       | Type    | Required | Description |
|-------------|---------|----------|-------------|
| `test_path` | string  | no       | Path to tests (default: `tests/`) |
| `coverage`  | boolean | no       | Collect coverage (default: true) |
| `verbose`   | boolean | no       | Verbose output (default: true) |

**Best Practice:**
```json
{
  "tool": "run_tests",
  "test_path": "tests/",
  "coverage": true,
  "purpose": "Verify that recent changes in txt_report.py did not break existing functionality"
}
```

---

## Best Practices for Tool Usage (All Roles)

- Always include a clear `"purpose"` — it helps the next role understand your intent.
- Prefer `search_replace` over `write_file` when making targeted changes.
- After any significant change, run `git_status` before committing.
- When debugging, use `run_tests` frequently instead of manual verification.
- Never commit without a meaningful Russian commit message.

---

## Extending the Registry

When adding a new tool:
1. Add it to this file with description, parameters, and at least 2 good examples.
2. Implement it in your local runner.
3. Update `SYSTEM_PROMPT.md` (section "Available Tools").
4. Update `AGENT_ROLES.md` if the new tool is especially important for certain roles.