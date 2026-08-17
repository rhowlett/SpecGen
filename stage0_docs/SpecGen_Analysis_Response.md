# KiCad SpecGen — Architecture Review and Implementation Tracker

> **Document role:** Project state tracker, architecture record, and
> gap closure log. Updated at the end of each documentation session.
> **Stage 0 status:** Complete — all Stage 0 documents written and reviewed.
> **Stage 1 status:** Ready to begin coding.
> **Authoritative references:** `SpecGen_Stage_Plan.md` (implementation),
> `SpecGen_Terminology.md` (all names), `SpecGen_File_Framework.md` (architecture).

---

## 1. Project State Summary

Stage 0 documentation is complete. All critical architectural decisions have
been made, documented, reviewed, and cross-checked. Stage 1 coding can begin.

### What was resolved in Stage 0

| Category | Resolution |
|---|---|
| Configuration file names | `kicad_specgen_local.json`, `kicad_specgen_company.json`, `kicad_specgen_users.json`, `<name>.kicad_specgen` — all finalised |
| Token names | All `KSG_*` tokens and protected runtime tokens finalised in `SpecGen_Terminology.md` |
| JSON schemas | Complete schemas for all four SpecGen-owned files in `SpecGen_Schema_Definitions.md` |
| `.kicad_specgen` format | JSON throughout — no TOML |
| Configure tab scope | `Edit → Local Tokens...` for quick token editing; Configure tab (5 subtabs) for full management |
| Fabrication | The Fabrication subtab is the third subtab within the Report tab. It selects tokenized output paths, chooses which jobset destinations to include in the FAB ZIP, generates the README, and produces the ZIP package. |
| Sidebar navigation | `[Project] [Variables] [Jobset] [Report] [Logs] ───── [Configure]` |
| Startup sequence | Defined in `SpecGen_File_Framework.md` §7; authoritative detail in `SpecGen_Setup_Process.md` §4 |
| Jobset reconciliation | Defined in `SpecGen_File_Framework.md` §7.3 — checked at open, save, and close |
| Absolute path rule | All file references in portable files must be in tokenized paths; no exceptions |
| Skipped tokens | `kicad_specgen_local.json → skipped_tokens[]` — machine-local suppression |
| Theme system | 6 themes with full colour palettes — `SpecGen_GUI_Theme.md` |
| Preferences | Preferences subtab in Configure tab; `kicad_specgen_local.json → preferences` |

---

## 2. Document Inventory

### Primary authority documents — all complete

| Document | Role | Stage | Status |
|---|---|---|---|
| `SpecGen_Terminology.md` | Canonical names, tokens, enums, modules, class names | 0 | ✅ Current |
| `SpecGen_File_Framework.md` | Token model, file ownership, startup sequence, validation | 0 | ✅ 10-point review complete |
| `SpecGen_Schema_Definitions.md` | JSON schemas for all SpecGen-owned config files | 0 | ✅ Fully updated |
| `SpecGen_Setup_Process.md` | Setup wizard — 6 phases; §9 → normative ref to Tab_Configure | 0 | ✅ Approved |
| `SpecGen_Stage_Plan.md` | 5-stage implementation plan with module lists and acceptance criteria | 0 | ✅ Approved |
| `SpecGen_Application_Description.md` | Application overview, full module layout, stage scope | 0 | ✅ 10-point review complete |
| `SpecGen_GUI_Menus.md` | All menus, all actions, help system — 10-point review complete | 0 | ✅ 10-point review complete |
| `SpecGen_GUI_Dialogs.md` | All 8 dialog wireframes — 6 full Stage 1, 2 Stage 2 stubs | 0 | ✅ Complete |
| `SpecGen_GUI_Theme.md` | 6 themes with full colour palettes and QSS guidance | 0 | ✅ Complete |
| `SpecGen_Tab_Configure.md` | Configure tab — 5 subtab wireframes including Preferences | 0 | ✅ Complete |
| `SpecGen_Tab_Jobset.md` | Jobset tab — initial structure | 0 | 🔄 Started — Stage 2 and 3 updates pending |
| `SpecGen_Tab_Logs.md` | Logs tab — Stage 1 full; Stage 3 Output Log feed documented | 0 | ✅ Complete |
| `SpecGen_Tab_Report.md` | Report + Fabrication tab — 3 subtabs | 0 | ✅ Complete |

### Reference documents

| Document | Role | Status |
|---|---|---|
| `SpecGen_Help_JinJa.md` | Jinja2 help file style example — use as authoring template | ✅ Reference |
| `SpecGen_Architecture_Review.md` | Historical initial architecture analysis | 📁 Archive |

### Documents to create — by stage

| Document | Stage | Purpose | Blocks coding? |
|---|---|---|---|
| `SpecGen_Help_Guide.md` | Stage 1 | Developer guide for writing help `.md` files | No — format defined in `SpecGen_GUI_Menus.md` |
| `SpecGen_Tab_Project.md` | Stage 2 | Project tab wireframes | Stage 2 |
| `SpecGen_Tab_Variables.md` | Stage 2 | Variables tab wireframes | Stage 2 |
| `SpecGen_Tab_Jobset.md` (Stage 2 update) | Stage 2 | Read-side detail: Dashboard fields, destination table, Results file tree | Stage 2 |
| `SpecGen_Tab_Jobset.md` (Stage 3 update) | Stage 3 | Execution detail: Output Log live feed, Run/Stop controls, stale destinations | Stage 3 |

---

## 3. Document Naming Convention

```text
SpecGen_{Category}_{Topic}.md

Category prefixes:
  Tab_     Workspace tab wireframe specifications
  GUI_     Menus, dialogs, and non-tab UI specifications
  Help_    Help file style examples and authoring guides
  (none)   Core design, planning, and reference documents
```

All filenames use `SpecGen_` as the mandatory prefix.

---

## 4. Architecture Summary

### Configuration file model

| File | Owner | Portable | Contains |
|---|---|---|---|
| `kicad_specgen_local.json` | SpecGen | No | KSG_* tokens, kicad-cli path, setup state, last_session, recent_projects, skipped_tokens, preferences |
| `kicad_specgen_company.json` | SpecGen | Yes | Company identity, clients, teams, environments, shared tokenized paths |
| `kicad_specgen_users.json` | SpecGen | Yes | User profiles, worker IDs, client/team associations |
| `<name>.kicad_specgen` | SpecGen | Yes | Project state, environment selection, jobset config, report recipe, fabrication config |
| `.kicad_pro` | KiCad | n/a | Read-only: text_variables |
| `.kicad_jobset` | KiCad | n/a | Read-only: destination IDs, output paths |
| `kicad_common.json` | KiCad | n/a | Read-only: environment.vars (lowest-priority token source) |

### Token resolution priority (highest to lowest)

```text
1. Protected derived runtime tokens (SPECGEN_PROJECT_FILE, KSG_PROJECT_SPECGEN_DIR,
   KICAD_PROJECT_DIR, GIT_PROJECT_DIR, JOBSET_OUTPUT_DIR, FAB_OUTPUT_DIR)
2. kicad_specgen_users.json resolved user paths
3. kicad_specgen_company.json resolved company/client paths
4. kicad_specgen_local.json tokens (KSG_* absolute paths)
5. kicad_common.json environment.vars (lowest priority)
```

At project level: `USER → CLIENT → COMPANY → DEFAULT`

### Absolute path rule

All file references in `kicad_specgen_company.json`, `kicad_specgen_users.json`,
and project `.kicad_specgen` files must be within a tokenized path root. No
absolute paths in portable files — no exceptions. If a path cannot be tokenized,
it must be added as a new `KSG_*` token in `kicad_specgen_local.json`, or the
file must be copied to a tokenized location.

### Sidebar navigation

```text
[Project]
[Variables]
[Jobset]
[Report]
[Logs]
─────────────
[Configure]
```


### Write target rules

| Action | Writes To |
|---|---|
| `Edit → Local Tokens...` | `kicad_specgen_local.json → tokens` |
| `Edit → Configure kicad-cli...` | `kicad_specgen_local.json → tools.kicad_cli_path` |
| `Edit → Configure` (page switch) | Nothing — navigation only |
| Missing Tokens dialog — Provide | `kicad_specgen_local.json → tokens` |
| Missing Tokens dialog — Skip | `kicad_specgen_local.json → skipped_tokens` |
| Missing Tokens dialog — Remove | Active `.kicad_specgen` (sets dirty flag) |
| Configure tab — Local Machine | `kicad_specgen_local.json` |
| Configure tab — Company & User | `kicad_specgen_company.json`, `kicad_specgen_users.json` |
| Configure tab — Environments | `kicad_specgen_company.json`, `kicad_specgen_local.json` |
| Configure tab — Preferences | `kicad_specgen_local.json → preferences` |
| Configure tab — Validation | Nothing — read-only |
| File → Save / Save As | Active `.kicad_specgen` |
| File → Exit | `kicad_specgen_local.json → last_session` |
| Project open | `kicad_specgen_local.json → last_session`, `recent_projects` |
| View → Theme (shortcut) | `kicad_specgen_local.json → preferences.theme` |

---

## 5. Application Layer Architecture

```text
┌──────────────────────────────────────────────────────────────┐
│  UI Layer (PySide6)                                          │
│  main_window, sidebar, setup_wizard, actions, theme          │
│  tabs: configuration_tab, logs_tab, project_tab,             │
│        variables_tab, jobset_tab, report_tab                 │
│  dialogs: local_tokens, missing_tokens, new_project,         │
│           about, help, kicad_cli, add_user, clients_teams    │
│  widgets: token_table, path_field, validation_panel,         │
│           log_viewer, output_tree, file_preview              │
│  → Calls services only. No direct config file access.       │
├──────────────────────────────────────────────────────────────┤
│  Services Layer                                              │
│  config_service.py       Load/save config files              │
│  validation_service.py   Run config validation               │
│  project_service.py      Open/create/save/close project      │
│  jobset_service.py       kicad-cli subprocess (Stage 3)      │
│  report_service.py       Report + FAB build (Stage 4)        │
├──────────────────────────────────────────────────────────────┤
│  Core Layer                                                  │
│  specgen_local_config.py   Load/validate/save local JSON     │
│  specgen_company_config.py Load/validate/save company JSON   │
│  specgen_user_config.py    Load/validate/save users JSON     │
│  project_config.py         Load/validate/save .kicad_specgen │
│  token_resolver.py         Build effective token table       │
│  validators.py             Structured validation results     │
│  file_ops.py               Atomic write, backup, mkdir       │
│  migrations.py             Schema version migration          │
│  logging_utils.py          Structured log records            │
│  app_state.py              In-memory observable state        │
│  platform_paths.py         OS detection, KICAD_COMMON_DIR    │
│  kicad_env.py              Read kicad_common.json vars       │
│  kicad_pro_parser.py       Read .kicad_pro (read-only)       │
│  kicad_jobset_parser.py    Read .kicad_jobset (read-only)    │
│  render/jinja_renderer.py  Jinja2 template rendering         │
│  render/pdf_assembler.py   PDF assembly                      │
│  fab/package_builder.py    FAB ZIP packaging                 │
└──────────────────────────────────────────────────────────────┘
```

---

## 6. Testing Strategy Summary

Full test plan is in `SpecGen_Stage_Plan.md` §Stage 1 through §Stage 5.
Summary of the per-stage testing approach:

| Stage | Focus | Key tests |
|---|---|---|
| 1 | Config load/save, token resolver, validation, GUI smoke | `test_specgen_local_config`, `test_token_resolver`, `test_validators`, `test_logs_tab` |
| 2 | Project open/save/close, KiCad file parsing, Missing Tokens | `test_project_config`, `test_kicad_pro_parser`, `test_missing_tokens_dialog` |
| 3 | Subprocess management, log persistence, reconciliation | `test_jobset_service`, `test_log_persistence`, `test_reconciliation` |
| 4 | Report render, PDF assembly, FAB ZIP | `test_jinja_renderer`, `test_pdf_assembler`, `test_package_builder` |
| 5 | Integration, session restore, terminology regression | `test_session_restore`, `test_terminology` |

Terminology regression test (`tests/regression/test_terminology.py`) scans all
source files for retired names. See `SpecGen_Terminology.md` §16 for the full
list of strings that must not appear in code.

---

## 7. Stage 0 Completed Deliverables

### Documents written

- [x] `SpecGen_Terminology.md` — canonical reference for all names
- [x] `SpecGen_File_Framework.md` — fully reviewed (10-point)
- [x] `SpecGen_Schema_Definitions.md` — all schemas including project, preferences, skipped_tokens
- [x] `SpecGen_Setup_Process.md` — 6-phase wizard; §9 → Tab_Configure normative ref
- [x] `SpecGen_Stage_Plan.md` — 5-stage plan, module lists, acceptance criteria
- [x] `SpecGen_Application_Description.md` — fully reviewed (10-point)
- [x] `SpecGen_GUI_Menus.md` — fully reviewed (10-point)
- [x] `SpecGen_GUI_Dialogs.md` — 8 dialogs (6 full Stage 1, 2 Stage 2 stubs)
- [x] `SpecGen_GUI_Theme.md` — 6 themes with full colour palettes
- [x] `SpecGen_Tab_Configure.md` — 5 subtabs including Preferences
- [x] `SpecGen_Tab_Logs.md` — Stage 1 full; Stage 3 feed documented
- [x] `SpecGen_Tab_Report.md` — Report + Fabrication 3 subtabs
- [x] `SpecGen_Tab_Jobset.md` — initial structure (Stage 2/3 updates pending)

### Key decisions made

- [x] `kicad_specgen_local.json` is the only file that stores absolute paths
- [x] All portable files use `{TOKEN_NAME}/...` notation — no exceptions
- [x] `skipped_tokens` is machine-local; `Remove` is the only way to affect the project file
- [x] Jobset reconciliation at open/save/close — not on tab display
- [x] `active_tab` and `workspace.environment` are per-project state in `.kicad_specgen → ui`
- [x] `last_session` stores only: `specgen_project`, `project_name`, `display_name`, `kicad_project_dir`, `window_geometry`, `last_opened_at`
- [x] `recent_projects` items have the same fields as `last_session` minus `window_geometry`
- [x] `Configure` is `Edit → Configure` (page switch) — not in View menu
- [x] `Preferences` is the fourth Configure subtab — not a separate dialog
- [x] 6 themes: `system`, `light`, `dark`, `engineering_dark`, `ion_dark`, `ion_light`
- [x] Setup process is `setup.py` — not a separate application; app does not exit on incomplete setup

---

## 8. Open Items

### Stage 1 — one document not yet written

| Item | Priority | Notes |
|---|---|---|
| `SpecGen_Help_Guide.md` | Low — non-blocking | Developer guide for writing help `.md` files. Format is already defined in `SpecGen_GUI_Menus.md §Required Help Files`. Write during Stage 1 alongside initial help files. |

### Stage 2 — documentation needed before coding begins

| Item | Document | Notes |
|---|---|---|
| Project tab wireframes | `SpecGen_Tab_Project.md` | Create before Stage 2 coding |
| Variables tab wireframes | `SpecGen_Tab_Variables.md` | Create before Stage 2 coding |
| Jobset tab read-side detail | `SpecGen_Tab_Jobset.md` update | Add Dashboard fields, destination table columns, Results file tree |
| Multi-user edit conflict for company JSON | `SpecGen_File_Framework.md` note | Low priority — flag in Stage 2 when project_service is built |

### Stage 3+ — documentation needed before coding begins

| Item | Document | Notes |
|---|---|---|
| Jobset tab execution detail | `SpecGen_Tab_Jobset.md` update | Add Output Log wireframe, Run/Stop controls, stale destination display |

### Living document policy

`SpecGen_Schema_Definitions.md` and `SpecGen_File_Framework.md` must be
reviewed and updated whenever:
- A new tab wireframe is created or updated
- A dialog reads or writes a config field
- Application code introduces a new config field
- A stage is completed

The three tracker documents (`SpecGen_Terminology.md`, `SpecGen_Analysis_Response.md`,
`SpecGen_Stage_Plan.md`) must be updated whenever any document is created or updated.

---

## 9. Stage 1 Readiness

**Status: Ready to begin Stage 1 coding.**

All Stage 1 documentation is complete. All 10-point document reviews are done.
All critical architectural decisions are recorded. No unresolved blockers.

The one non-blocking gap (`SpecGen_Help_Guide.md`) can be written during Stage 1
alongside the initial help files without delaying any code.

See `SpecGen_Stage_Plan.md` §Stage 1 for the full module list, acceptance
criteria, test plan, and risks.

