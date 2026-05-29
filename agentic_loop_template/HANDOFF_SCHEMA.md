# HANDOFF SCHEMA вЂ” Control Transfer Between Roles

> Every agent message **must** end with **exactly one JSON object**.  
> Nothing after the JSON.  
> All fields are required unless marked `(optional)`.  
> Empty arrays `[]` and empty strings `""` are valid вЂ” never omit fields.

---

## Full Schema (aligned with SYSTEM_PROMPT 2.1)

```json
{
  "handoff_to": "Coder",
  // Allowed: "Orchestrator" | "Coder" | "Tester" | "Debugger" | "Reviewer" | "None"
  // Use "None" only when status = "DONE"

  "role": "Orchestrator",
  // Current role: "Orchestrator" | "Coder" | "Tester" | "Debugger" | "Reviewer"

  "current_phase": "planning",
  // "planning" | "implementation" | "testing" | "debugging" | "review" | "finalization"

  "cycle_number": 0,
  // Incremented by Reviewer at the start of each new cycle.

  "summary": "Brief description of what was done (1вЂ“3 sentences).",

  "context_updates": ["PROJECT_CONTEXT.md", "SPRINTPLAN.md"],
  // Files that were created or significantly updated in this step.

  "artifacts": ["src/parser.py", "src/models.py"],
  // Important new or modified files/directories for the next role.

  "next_input_files": [
    "{{ SPEC_FILE }}",
    "PROJECT_CONTEXT.md",
    "SPRINTPLAN.md"
  ],
  // Files the next role MUST read before starting work.

  "git_branch": "feature-{{ FEATURE_NAME }}",

  "last_commit": "Р РµР°Р»РёР·РѕРІР°Р» Р±Р°Р·РѕРІС‹Р№ РїР°СЂСЃРµСЂ Рё РґРѕР±Р°РІРёР» С‚РµСЃС‚С‹ РЅР° РЅРѕСЂРјР°Р»РёР·Р°С†РёСЋ",
  // Last commit message (in Russian). Empty string if no commits were made.

  "confidence": 0.9,
  // 0.0вЂ“1.0. Below 0.7 usually means the handoff should be reconsidered.

  "status": "IN_PROGRESS",
  // "IN_PROGRESS" | "BLOCKED" | "DONE"

  "git_final": "",

  "metrics": {
    "tests_total": 12,
    "tests_failed": 3,
    "coverage": 67.4,
    "tool_calls": 5,
    "elapsed_minutes": 14.5
  },

  "issues_found": [
    {
      "type": "env_setup",
      "location": "agentic_loop_template/setup_kurbanov.ps1",
      "pattern": "Venv not activated before running tests",
      "frequency": 2
    }
  ],

  "process_tags": ["env_setup_missing_checks"],
  // Recurring process problems. Examples: "too_many_small_commits", "spec_not_reread", "architecture_skipped"

  "feedback_from_previous": {
    "what_worked_well": ["Good test coverage on normalization"],
    "what_needs_improvement": ["Missing error handling in parser"],
    "suggestions": ["Add retry logic for flaky network calls"]
  },

  "lessons_learned": [
    "Always run agentic_loop_template/setup_kurbanov.ps1 at the beginning of a new cycle"
  ]
}
```
      "Р‘С‹СЃС‚СЂР°СЏ СЂРµР°Р»РёР·Р°С†РёСЏ РјРѕРґРµР»РµР№",
      "Р§С‘С‚РєРѕРµ СЂР°Р·РґРµР»РµРЅРёРµ РЅРѕСЂРјР°Р»РёР·Р°С‚РѕСЂРѕРІ"
    ],
    "what_failed_or_was_inefficient": [
      "РЎРєРµР»РµС‚ С‚РµСЃС‚РѕРІ Р±С‹Р» СЃР»РёС€РєРѕРј РїРѕРІРµСЂС…РЅРѕСЃС‚РЅС‹Рј"
    ],
    "suggestions_for_next_agent": [
      "РЈРґРµР»РёС‚СЊ РѕСЃРѕР±РѕРµ РІРЅРёРјР°РЅРёРµ edge-РєРµР№СЃСѓ: РїСѓСЃС‚С‹Рµ РїРѕР»СЏ РІ СЃРµРєС†РёРё documents",
      "РџСЂРѕРІРµСЂРёС‚СЊ РїРѕРІРµРґРµРЅРёРµ РїСЂРё UTF-8 BOM РІ РЅР°С‡Р°Р»Рµ С„Р°Р№Р»Р°"
    ]
  },

  // в”Ђв”Ђв”Ђ РЈР РћРљР Р­РўРћР“Рћ РЁРђР“Рђ в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
  "lessons_learned": [
    "Р’СЃРµРіРґР° Р·Р°РїСѓСЃРєР°С‚СЊ PowerShell-СЃРєСЂРёРїС‚ РїРѕРґРіРѕС‚РѕРІРєРё РѕРєСЂСѓР¶РµРЅРёСЏ РїРµСЂРµРґ РѕС†РµРЅРєРѕР№ СЃС‚Р°С‚СѓСЃР°.",
    "Р§РёС‚Р°С‚СЊ TASK_SPECIFICATION.md Р·Р°РЅРѕРІРѕ РїРµСЂРµРґ РєР°Р¶РґС‹Рј С†РёРєР»РѕРј, РЅРµ РїРѕР»Р°РіР°С‚СЊСЃСЏ РЅР° РєСЌС€."
  ],
  // РљР°РЅРґРёРґР°С‚С‹ РІ РїРѕСЃС‚РѕСЏРЅРЅС‹Рµ РїСЂР°РІРёР»Р° СЃР»РµРґСѓСЋС‰РµРіРѕ С†РёРєР»Р°.

  "inner_loop_summary": "Р—Р°РїР»Р°РЅРёСЂРѕРІР°Р» 5 С€Р°РіРѕРІ, РІС‹РїРѕР»РЅРёР» 3 tool calls, РѕС‚СЂРµС„Р»РµРєСЃРёСЂРѕРІР°Р» РїРѕСЃР»Рµ РєР°Р¶РґРѕР№ С‚СЂРѕР№РєРё вЂ” РѕР±РЅР°СЂСѓР¶РёР» РїСЂРѕР±Р»РµРјСѓ СЃ venv, РёСЃРїСЂР°РІРёР» РІ РїР»Р°РЅРµ.",
  // РљСЂР°С‚РєРѕРµ РѕРїРёСЃР°РЅРёРµ РїРѕРІРµРґРµРЅРёСЏ PLAN в†’ ACT в†’ REFLECT РІ СЌС‚РѕРј С€Р°РіРµ.

  // в”Ђв”Ђв”Ђ Р¤Р›РђР“Р в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
  "requires_architecture_review": false,
  // true = РѕР±РЅР°СЂСѓР¶РµРЅС‹ Р°СЂС…РёС‚РµРєС‚СѓСЂРЅС‹Рµ РїСЂРѕР±Р»РµРјС‹, С‚СЂРµР±СѓСЋС‰РёРµ РїРµСЂРµСЂР°Р±РѕС‚РєРё.
  // РџСЂРё true: Reviewer РґРѕР»Р¶РµРЅ Р·Р°РїСѓСЃС‚РёС‚СЊ РЅРѕРІС‹Р№ С†РёРєР» СЃ architecture review С„Р°Р·РѕР№.

  // в”Ђв”Ђв”Ђ Р¤РРќРђР›Р¬РќРћР• РЎРћРЎРўРћРЇРќРР• в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
  "status": "IN_PROGRESS",
  // "IN_PROGRESS" = С†РёРєР» РїСЂРѕРґРѕР»Р¶Р°РµС‚СЃСЏ
  // "DONE" = Reviewer РїРѕРґС‚РІРµСЂРґРёР» 100% СЃРѕРѕС‚РІРµС‚СЃС‚РІРёРµ СЃРїРµС†РёС„РёРєР°С†РёРё

  "git_final": ""
  // Р—Р°РїРѕР»РЅСЏРµС‚СЃСЏ С‚РѕР»СЊРєРѕ Reviewer РїСЂРё status = "DONE".
  // РљРѕСЂРѕС‚РєР°СЏ Р·Р°РјРµС‚РєР° Рѕ С„РёРЅР°Р»СЊРЅРѕРј merge РІ main.
}
```

---

## РџСЂР°РІРёР»Р° РІР°Р»РёРґР°С†РёРё JSON

### РљСЂРёС‚РёС‡РµСЃРєРёРµ С‚СЂРµР±РѕРІР°РЅРёСЏ
1. Р РѕРІРЅРѕ **РѕРґРёРЅ** JSON-РѕР±СЉРµРєС‚ РІ РєРѕРЅС†Рµ СЃРѕРѕР±С‰РµРЅРёСЏ.
2. **РќРёРєР°РєРѕРіРѕ С‚РµРєСЃС‚Р°** РїРѕСЃР»Рµ Р·Р°РєСЂС‹РІР°СЋС‰РµР№ `}`.
3. Р’СЃРµ РѕР±СЏР·Р°С‚РµР»СЊРЅС‹Рµ РїРѕР»СЏ РїСЂРёСЃСѓС‚СЃС‚РІСѓСЋС‚ вЂ” РїСѓСЃС‚С‹Рµ Р·РЅР°С‡РµРЅРёСЏ (`""`, `[]`, `0`, `false`) РґРѕРїСѓСЃС‚РёРјС‹.
4. `handoff_to` СЃРѕРґРµСЂР¶РёС‚ С‚РѕР»СЊРєРѕ РґРѕРїСѓСЃС‚РёРјС‹Рµ Р·РЅР°С‡РµРЅРёСЏ.
5. `cycle_number` в‰Ґ 0, РЅРµ СѓР±С‹РІР°РµС‚.
6. `confidence` РІ РґРёР°РїР°Р·РѕРЅРµ `[0.0, 1.0]`.
7. `status` = `"DONE"` С‚РѕР»СЊРєРѕ РїСЂРё `handoff_to` = `"None"`.

### РўРёРїРёС‡РЅС‹Рµ РѕС€РёР±РєРё
| РћС€РёР±РєР° | РџСЂР°РІРёР»СЊРЅРѕ |
|--------|-----------|
| РћС‚СЃСѓС‚СЃС‚РІСѓРµС‚ РїРѕР»Рµ `metrics` | Р”РѕР±Р°РІРёС‚СЊ СЃ РЅСѓР»РµРІС‹РјРё Р·РЅР°С‡РµРЅРёСЏРјРё |
| `issues_found: null` | `issues_found: []` |
| `last_commit` СЃРѕРґРµСЂР¶РёС‚ СЃР»РѕРІРѕ "Р°РіРµРЅС‚" | РџРµСЂРµС„РѕСЂРјСѓР»РёСЂРѕРІР°С‚СЊ РїРѕ-С‡РµР»РѕРІРµС‡РµСЃРєРё |
| `confidence: 1.0` РїСЂРё РЅРµР·Р°РєСЂС‹С‚С‹С… issues | РЎРЅРёР·РёС‚СЊ РґРѕ в‰¤ 0.8 |
| РўРµРєСЃС‚ РїРѕСЃР»Рµ JSON | РЈРґР°Р»РёС‚СЊ РІСЃС‘ РїРѕСЃР»Рµ `}` |

---

## РњР°С‚СЂРёС†Р° РїРµСЂРµРґР°С‡Рё СѓРїСЂР°РІР»РµРЅРёСЏ

| РћС‚ / Р”Рѕ | Orchestrator | Coder | Tester | Debugger | Reviewer | None |
|---------|:---:|:---:|:---:|:---:|:---:|:---:|
| **Orchestrator** | в—‡ (РµСЃР»Рё РЅСѓР¶РµРЅ РµС‰С‘ С€Р°Рі) | вњ“ (РѕР±С‹С‡РЅС‹Р№) | вЂ” | вЂ” | вЂ” | вЂ” |
| **Coder** | вЂ” | в—‡ (РµСЃР»Рё РјРѕРґСѓР»СЊ РЅРµ Р·Р°РІРµСЂС€С‘РЅ) | вњ“ (РѕР±С‹С‡РЅС‹Р№) | вЂ” | вЂ” | вЂ” |
| **Tester** | вЂ” | вЂ” | в—‡ (РµСЃР»Рё С‚РµСЃС‚С‹ РЅРµ РЅР°РїРёСЃР°РЅС‹) | вњ“ (РѕР±С‹С‡РЅС‹Р№) | вЂ” | вЂ” |
| **Debugger** | вЂ” | вЂ” | в—‡ (РµСЃР»Рё РЅСѓР¶РЅРѕ РїРµСЂРµРїРёСЃР°С‚СЊ С‚РµСЃС‚С‹) | вЂ” | вњ“ (РѕР±С‹С‡РЅС‹Р№) | вЂ” |
| **Reviewer** | вњ“ (РµСЃР»Рё NOT DONE) | вЂ” | вЂ” | вЂ” | вЂ” | вњ“ (РµСЃР»Рё DONE) |

вњ“ = РѕСЃРЅРѕРІРЅРѕР№ РјР°СЂС€СЂСѓС‚  в—‡ = СѓСЃР»РѕРІРЅС‹Р№ (СЃ РѕР±РѕСЃРЅРѕРІР°РЅРёРµРј РІ summary)  вЂ” = РЅРµРґРѕРїСѓСЃС‚РёРјРѕ

---

## РџСЂРёРјРµСЂС‹ Р±С‹СЃС‚СЂС‹С… JSON-Р±Р»РѕРєРѕРІ

### Orchestrator в†’ Coder (СЃС‚Р°СЂС‚)
```json
{
  "handoff_to": "Coder", "role": "Orchestrator", "current_phase": "planning",
  "cycle_number": 0, "summary": "РџРѕРґРіРѕС‚РѕРІРёР» РѕРєСЂСѓР¶РµРЅРёРµ, СЃРѕР·РґР°Р» SPRINTPLAN.md СЃ 5 С„Р°Р·Р°РјРё.",
  "context_updates": ["PROJECT_CONTEXT.md", "SPRINTPLAN.md"],
  "artifacts": ["SPRINTPLAN.md", "PROJECT_CONTEXT.md"],
  "next_input_files": ["TASK_SPECIFICATION.md", "PROJECT_CONTEXT.md", "SPRINTPLAN.md"],
  "git_branch": "feature-parser-impl", "last_commit": "Р”РѕР±Р°РІРёР» РїР»Р°РЅ СЃРїСЂРёРЅС‚Р° Рё РѕР±РЅРѕРІРёР» РєРѕРЅС‚РµРєСЃС‚",
  "confidence": 0.92, "metrics": {"tests_total":0,"tests_failed":0,"coverage":0.0,"tool_calls":5,"elapsed_minutes":8},
  "issues_found": [], "process_tags": [], "feedback_from_previous": {"what_worked_well":[],"what_failed_or_was_inefficient":[],"suggestions_for_next_agent":[]},
  "lessons_learned": ["Р§РёС‚Р°С‚СЊ СЃРїРµС†РёС„РёРєР°С†РёСЋ Р·Р°РЅРѕРІРѕ РїРµСЂРµРґ РєР°Р¶РґС‹Рј С†РёРєР»РѕРј."],
  "inner_loop_summary": "Р—Р°РїР»Р°РЅРёСЂРѕРІР°Р» 4 С€Р°РіР°, РІС‹РїРѕР»РЅРёР», РЅР°С€С‘Р» РїСЂРѕРїСѓС‰РµРЅРЅС‹Р№ venv вЂ” РёСЃРїСЂР°РІРёР» РІ СЃРєСЂРёРїС‚Рµ.",
  "requires_architecture_review": false, "status": "IN_PROGRESS", "git_final": ""
}
```

### Reviewer в†’ None (DONE)
```json
{
  "handoff_to": "None", "role": "Reviewer", "current_phase": "finalization",
  "cycle_number": 2, "summary": "Р’СЃРµ 48 С‚РµСЃС‚РѕРІ РїСЂРѕС€Р»Рё, РїРѕРєСЂС‹С‚РёРµ 94%, СЃРїРµС†РёС„РёРєР°С†РёСЏ РІС‹РїРѕР»РЅРµРЅР° РїРѕР»РЅРѕСЃС‚СЊСЋ.",
  "context_updates": ["PROJECT_CONTEXT.md", "README.md", "USAGE.md"],
  "artifacts": ["src/", "tests/", "migrations/", "README.md", "USAGE.md", "pyproject.toml"],
  "next_input_files": [], "git_branch": "main", "last_commit": "Р¤РёРЅР°Р»РёР·РёСЂРѕРІР°Р» РґРѕРєСѓРјРµРЅС‚Р°С†РёСЋ Рё СЃРјРµСЂР¶РёР» РІ main",
  "confidence": 0.98, "metrics": {"tests_total":48,"tests_failed":0,"coverage":94.2,"tool_calls":6,"elapsed_minutes":12},
  "issues_found": [], "process_tags": [],
  "feedback_from_previous": {"what_worked_well":["Debugger Р±С‹СЃС‚СЂРѕ Р·Р°РєСЂС‹Р» РІСЃРµ edge-РєРµР№СЃС‹"],"what_failed_or_was_inefficient":[],"suggestions_for_next_agent":[]},
  "lessons_learned": ["DB roundtrip С‚РµСЃС‚ РґРѕР»Р¶РµРЅ Р±С‹С‚СЊ РІ С‡РµРєР»РёСЃС‚Рµ СЃ РїРµСЂРІРѕРіРѕ С†РёРєР»Р°."],
  "inner_loop_summary": "РџСЂРѕС€С‘Р» РїРѕ РІСЃРµРјСѓ С‡РµРєР»РёСЃС‚Сѓ, Р·Р°РїСѓСЃС‚РёР» smoke tests, СЃРјРµСЂР¶РёР» РІРµС‚РєСѓ.",
  "requires_architecture_review": false, "status": "DONE",
  "git_final": "Р’РµС‚РєР° feature-parser-impl СЃРјРµСЂР¶РµРЅР° РІ main, С‚РµРі v1.0.0 РїСЂРѕСЃС‚Р°РІР»РµРЅ."
}
```

