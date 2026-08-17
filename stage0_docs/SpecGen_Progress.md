# KiCad SpecGen — Project Progress and Architecture Record

> **Document role:** Single authoritative project tracker combining
> architecture record, implementation progress, design decisions, and
> stage readiness. Replaces `SpecGen_Analysis_Response.md` and
> `SpecGen_Architecture_Review.md`.
> **Updated:** End of Stage 0. Stage 1 ready to begin.
> **Authoritative references:** `SpecGen_Stage_Plan.md` (implementation plan),
> `SpecGen_Terminology.md` (all names), `SpecGen_File_Framework.md` (architecture).

---

## 1. Project State Summary

Stage 0 documentation is complete. All critical architectural decisions have been
made, documented, reviewed, and cross-checked. Stage 1 coding can begin.

### Resolved in Stage 0

| Category | Resolution |
|---|---|
| Configuration file names | `kicad_specgen_local.json`, `kicad_specgen_company.json`, `kicad_specgen_users.json`, `<name>.kicad_specgen` — all finalised |
| Token names | All `KSG_*` tokens and protected runtime tokens finalised in `SpecGen_Terminology.md` |
| JSON schemas | Complete schemas for all four SpecGen-owned files in `SpecGen_Schema_Definitions.md` |
| `.kicad_specgen` format | JSON with `.kicad_specgen` extension |
| Configure tab scope | `Edit → Local Tokens...` for quick token editing; Configure tab (5 subtabs) for full management |
| Configure Environments scope conflict | Resolved: Option B — two separate concerns. `Edit → Local Tokens...` edits `kicad_specgen_local.json` tokens only. Configure tab Environments subtab edits `kicad_specgen_company.json` environments. |
| New Project dialog | Redesigned: selects existing environment from `kicad_specgen_company.json`; no inline environment creation |
| Fabrication | Third subtab within the Report tab — handles FAB output paths, ZIP contents, README, and checksums |
| Sidebar navigation | `[Project] [Variables] [Jobset] [Report] [Logs] ───── [Configure]` |
| Startup sequence | Defined in `SpecGen_File_Framework.md` §7; authoritative detail in `SpecGen_Setup_Process.md` §4 |
| Jobset reconciliation | Checked at project open, save, and close — defined in `SpecGen_File_Framework.md` §7.3 |
| Absolute path rule | All file references in portable files must be within a tokenized path root — no exceptions |
| Skipped tokens | `kicad_specgen_local.json → skipped_tokens[]` — machine-local; does not affect other users |
| Theme system | 6 themes with full colour palettes — `SpecGen_GUI_Theme.md` |
| Preferences | Preferences subtab in Configure tab; `kicad_specgen_local.json → preferences` |
| Setup process | 6-phase wizard in `SpecGen_Setup_Process.md`; app shows Setup Required banner on incomplete setup |
| Standalone mode | `kicad_specgen_company.json` always exists; created with company name "personal" during setup |
| `KSG_PROJECT_SPECGEN_DIR` name | Confirmed — keeps the `KSG_` namespace prefix |
| Setup entry point | `python setup.py` from `{KSG_APP_DIR}`; also available headless via `--headless` flag |
| `JOBSET_OUTPUT_DIR` derivation | From `outputs[0].settings.output_path` in the active `.kicad_jobset`; validate all outputs share same root; warn if they diverge |
| Multiple `.kicad_pro` files | SpecGen reads `files.kicad_pro` from project file; if not set, auto-selects the first `.kicad_pro` found in `KICAD_PROJECT_DIR` |
| Dirty flag | Set by any user-initiated edit to `.kicad_specgen` through the SpecGen UI; not set by KiCad-owned file changes |

---

## 2. Document Inventory

### Primary authority documents

| Document | Role | Status |
|---|---|---|
| `SpecGen_Terminology.md` | Canonical names, tokens, enums, modules, class names | ✅ Current |
| `SpecGen_File_Framework.md` | Token model, file ownership, startup sequence, validation | ✅ 10-point review complete |
| `SpecGen_Schema_Definitions.md` | JSON schemas for all SpecGen-owned config files | ✅ Fully updated |
| `SpecGen_Setup_Process.md` | Setup wizard — 6 phases; §9 → normative ref to Tab_Configure | ✅ Approved |
| `SpecGen_Stage_Plan.md` | 5-stage implementation plan with module lists and acceptance criteria | ✅ Approved |
| `SpecGen_Application_Description.md` | Application overview, full module layout, stage scope | ✅ 10-point review complete |
| `SpecGen_GUI_Menus.md` | All menus, all actions, help system | ✅ 10-point review complete |
| `SpecGen_GUI_Dialogs.md` | All 8 dialog wireframes — 6 full Stage 1, 2 Stage 2 stubs | ✅ Complete |
| `SpecGen_GUI_Theme.md` | 6 themes with full colour palettes and QSS guidance | ✅ Complete |
| `SpecGen_Tab_Configure.md` | Configure tab — 5 subtab wireframes including Preferences | ✅ Complete |
| `SpecGen_Tab_Jobset.md` | Jobset tab — initial structure | 🔄 Stage 2 and 3 updates pending |
| `SpecGen_Tab_Logs.md` | Logs tab — Stage 1 full; Stage 3 Output Log feed documented | ✅ Complete |
| `SpecGen_Tab_Report.md` | Report tab — 3 subtabs (Report Recipe, Preview & Build, Fabrication) | ✅ Complete |

### Reference documents

| Document | Role | Status |
|---|---|---|
| `SpecGen_Help_Guide.md` | Help file authoring guide — draft; all stages required for final | 🔄 Draft |
| `SpecGen_Help_JinJa.md` | Jinja2 help file style example — use as authoring template | ✅ Reference |

### Documents to create

| Document | Stage | Purpose | Blocks coding? |
|---|---|---|---|
| `SpecGen_Help_Guide.md` | Stage 1 | Developer guide for writing help `.md` files | No |
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

All filenames use `SpecGen_` as the mandatory prefix. No exceptions.
Topic words use Title_Case with underscores between words.

---

## 4. Architecture Summary

### Configuration file model

| File | Owner | Portable | Contains |
|---|---|---|---|
| `kicad_specgen_local.json` | SpecGen | No | KSG_* tokens, kicad-cli path, setup state, last_session, recent_projects, skipped_tokens, preferences |
| `kicad_specgen_company.json` | SpecGen | Yes | Company identity, clients, teams, environments, shared tokenized paths |
| `kicad_specgen_users.json` | SpecGen | Yes | User profiles, worker IDs, client/team associations |
| `<name>.kicad_specgen` | SpecGen | Yes | Project state, environment, jobset config, report recipe, fabrication config |
| `.kicad_pro` | KiCad | n/a | Read-only: text_variables |
| `.kicad_jobset` | KiCad | n/a | Read-only: destination IDs, output paths |
| `kicad_common.json` | KiCad | n/a | Read-only: environment.vars (lowest-priority token source) |

### Token resolution priority (highest to lowest)

```text
1. Protected derived runtime tokens
   (SPECGEN_PROJECT_FILE, KSG_PROJECT_SPECGEN_DIR, KICAD_PROJECT_DIR,
    GIT_PROJECT_DIR, JOBSET_OUTPUT_DIR, FAB_OUTPUT_DIR)
2. kicad_specgen_users.json resolved user paths
3. kicad_specgen_company.json resolved company/client paths
4. kicad_specgen_local.json tokens  (KSG_* absolute paths)
5. kicad_common.json environment.vars  (lowest priority)
```

At project level: `USER → CLIENT → COMPANY → DEFAULT`

### Absolute path rule

All file references in `kicad_specgen_company.json`, `kicad_specgen_users.json`,
and project `.kicad_specgen` files must be within a tokenized path root — no
absolute paths in portable files, no exceptions. If a path cannot be tokenized,
create a new `KSG_*` token in `kicad_specgen_local.json` or copy the file to a
tokenized location.

### Write target rules

| Action | Writes To |
|---|---|
| `Edit → Local Tokens...` | `kicad_specgen_local.json → tokens` |
| `Edit → Configure kicad-cli...` | `kicad_specgen_local.json → tools.kicad_cli_path` |
| `Edit → Configure` | Nothing — page switch |
| Missing Tokens — Provide | `kicad_specgen_local.json → tokens` |
| Missing Tokens — Skip | `kicad_specgen_local.json → skipped_tokens` |
| Missing Tokens — Remove | Active `.kicad_specgen` (sets dirty flag) |
| Configure tab — Local Machine | `kicad_specgen_local.json` |
| Configure tab — Company & User | `kicad_specgen_company.json`, `kicad_specgen_users.json` |
| Configure tab — Environments | `kicad_specgen_company.json`, `kicad_specgen_local.json` |
| Configure tab — Preferences | `kicad_specgen_local.json → preferences` |
| Configure tab — Validation | Nothing — read-only |
| File → Save / Save As | Active `.kicad_specgen` |
| File → Exit | `kicad_specgen_local.json → last_session` |
| Project open | `kicad_specgen_local.json → last_session`, `recent_projects` |
| View → Theme | `kicad_specgen_local.json → preferences.theme` |

---

## 5. Application Layer Architecture

The following diagram and tables define the layer boundaries for implementation.
The "Must Not Do" column is enforced by code review and confirmed by unit tests
that import modules without PySide6 available.

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
│  → No UI imports. No PySide6. No subprocess.               │
│  → Pure Python. Fully testable without a display.           │
└──────────────────────────────────────────────────────────────┘
```

### Core module responsibilities

| Module | Responsibility | Must Not Do |
|---|---|---|
| `platform_paths.py` | Resolve OS-specific KiCad config dir; detect OS and KiCad version | No file I/O beyond path construction |
| `specgen_local_config.py` | Load, validate, save, migrate `kicad_specgen_local.json`. Return typed dataclass. | No token resolution. No GUI. |
| `specgen_company_config.py` | Load, validate, save `kicad_specgen_company.json`. Return typed dataclass. | No token resolution. No GUI. |
| `specgen_user_config.py` | Load, validate, save `kicad_specgen_users.json`. Return typed dataclass. | No token resolution. No GUI. |
| `project_config.py` | Load, validate, save, migrate `.kicad_specgen`. Return typed dataclass. | No token resolution. No GUI. |
| `token_resolver.py` | Build effective token table. Resolve `{TOKEN}/path` references. Report missing tokens. | No file I/O beyond path existence checks. No GUI. |
| `validators.py` | Validate config objects against schema rules. Return structured `ValidationResult` objects. | No file I/O. No GUI. No side effects. |

### `ValidationResult` and `ValidationReport` Contracts

All validator functions return `ValidationResult` objects. `validation_service`
aggregates them into a `ValidationReport`.

```python
from dataclasses import dataclass, field
from typing import Literal

@dataclass(frozen=True)
class ValidationResult:
    check_id: str
    # Unique identifier, e.g. "local_config_exists", "token_ksg_app_dir",
    # "kicad_cli_path". Used by validation_panel.py to display per-check rows.

    status: Literal["pass", "warn", "fail"]
    # "pass"  → ✓ green
    # "warn"  → ⚠ amber  (non-blocking — configuration is usable)
    # "fail"  → ✗ red    (blocking — must be resolved before project operations)

    message: str
    # Short human-readable result message shown in the validation panel.
    # Example: "KSG_APP_DIR: /Users/john/kicad-specgen ✓ exists"
    # Example: "kicad-cli: not found — configure via Edit → Configure kicad-cli..."

    detail: str | None = None
    # Optional extended explanation shown in a tooltip or expanded row.
    # Use for repair guidance, file paths, or expected vs actual values.

    source: str = "config"
    # Which validator produced this result.
    # Values: "config", "project", "tokens", "kicad"


@dataclass
class ValidationReport:
    results: list[ValidationResult] = field(default_factory=list)

    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.status == "pass")

    @property
    def warnings(self) -> int:
        return sum(1 for r in self.results if r.status == "warn")

    @property
    def failures(self) -> int:
        return sum(1 for r in self.results if r.status == "fail")

    @property
    def overall(self) -> Literal["pass", "warn", "fail"]:
        if self.failures:  return "fail"
        if self.warnings:  return "warn"
        return "pass"
```

`validation_panel.py` receives a `ValidationReport` and renders one row per
`ValidationResult` using the `check_id` for ordering and the `status` for the
icon (✓ ⚠ ✗). The `detail` field is shown in a tooltip on row hover.

### Core module responsibilities (continued)

| Module | Responsibility | Must Not Do |
|---|---|---|
| `file_ops.py` | Atomic JSON write. Timestamped backup before write. Directory creation. Path existence checks. | No config parsing. No token resolution. |
| `kicad_pro_parser.py` | Parse `text_variables` from `.kicad_pro` JSON. Return dict. | No writes. No GUI. |
| `kicad_jobset_parser.py` | Parse `outputs[]` from `.kicad_jobset` JSON. Return list of destination objects. | No writes. No GUI. |
| `kicad_env.py` | Read `environment.vars` from `kicad_common.json`. | No writes during normal operation. |
| `migrations.py` | Schema version migration functions — `migrate_v{from}_to_v{to}(data)`. Return migrated data. | No file I/O. Pure data transforms. |
| `logging_utils.py` | Configure Python `logging`. Emit structured log records with timestamp, level, source, message. | No GUI. |
| `app_state.py` | Single mutable in-memory application state. Holds resolved tokens, active configs, dirty flags. Must be observable (signals or callbacks). | No file I/O. No GUI. |

### `app_state.py` Contract

`AppState` is a `QObject` subclass. Using `QObject` is the correct choice for
a PySide6 application — it gives thread-safe signal delivery to the main thread
at no extra cost, and it integrates naturally with `QAction` enabled-state
management.

#### Fields and `__init__`

`AppState` is a plain `QObject` subclass with an explicit `__init__`. Do not
use `@dataclass` — Python's dataclass decorator conflicts with `QObject`'s
metaclass and will raise a `TypeError` at import time in PySide6.

```python
class AppState(QObject):
    # Signals — declared at class level as class variables
    config_reloaded     = Signal()         # after any config load/reload
    tokens_changed      = Signal()         # after token table is rebuilt
    dirty_changed       = Signal()         # after any dirty flag changes
    validation_complete = Signal(object)   # payload: ValidationReport
    setup_state_changed = Signal(bool)     # payload: setup_complete bool

    def __init__(self, parent=None):
        super().__init__(parent)           # QObject.__init__ must be first

        # Configuration objects — set after each load/save cycle
        self.local_config:    LocalConfig   | None = None
        self.company_config:  CompanyConfig | None = None
        self.users_config:    UsersConfig   | None = None
        self.project_config:  ProjectConfig | None = None  # Stage 2+

        # Resolved token table — rebuilt by token_resolver
        self.resolved_tokens: dict[str, str] = {}

        # Active session identifiers
        self.active_user:           str  = ""
        self.active_environment:    str  = ""

        # Dirty flags — one per writeable file
        self.dirty_project: bool = False  # .kicad_specgen has unsaved changes
        self.dirty_local:   bool = False  # kicad_specgen_local.json has unsaved changes

        # Setup state
        self.setup_complete: bool = False
```

#### Canonical update protocol

**UI components never modify `app_state` fields.** Only services do. Services
receive `app_state` by dependency injection, update its fields, and emit
signals. UI components read `app_state` fields (read-only) and connect to its
signals to know when to refresh.

Example flow for a token save:

```text
1. LocalTokensDialog collects edited tokens from the table widget.
2. LocalTokensDialog calls config_service.save_local_tokens(new_tokens).
3. config_service writes the file via file_ops.write_json_atomic().
4. config_service reloads via specgen_local_config.load() → new LocalConfig.
5. config_service updates app_state:
       app_state.local_config   = new_local_config
       app_state.dirty_local    = False
       app_state.config_reloaded.emit()
       app_state.dirty_changed.emit()
6. Any connected UI components (token_table, validation_panel, status bar)
   refresh themselves in response to the signal.
7. LocalTokensDialog closes.
```

If `specgen_local_config.save()` changes, only `config_service` needs
updating — no dialog changes are required.

#### Ownership and access

`AppState` is a singleton instantiated in `app.py` and passed by reference to
every service and tab that needs it. It is **not** a global module-level variable.
Dependency injection keeps it testable — unit tests can construct a fresh
`AppState()` per test.

```python
# app.py
app_state = AppState()
config_service = ConfigService(app_state)
validation_service = ValidationService(app_state)
main_window = MainWindow(app_state, config_service, validation_service)
```

### Services module responsibilities

| Module | Responsibility | Inputs | Outputs |
|---|---|---|---|
| `project_service.py` | Open, create, save, close project. Orchestrates full startup sequence: load local → company → users → project → resolve tokens → validate. | File paths, user intents | Updated `app_state`. Structured results. |
| `config_service.py` | Edit and save `kicad_specgen_local.json`, `kicad_specgen_company.json`, and `kicad_specgen_users.json`. Coordinate writes, backups, and state refresh. | Edit intents from UI | Updated configs. Write results. |
| `validation_service.py` | Run full project validation. Aggregate results from core validators. Emits `app_state.validation_complete` with the `ValidationReport`; also returns the report directly for callers that need a synchronous result. | `app_state` | `ValidationReport` (return value + signal) |
| `jobset_service.py` | Run `kicad-cli jobset run`. Capture output. Update `app_state`. (Stage 3) | Jobset run config | Run results, log entries. |
| `report_service.py` | Orchestrate report render and FAB ZIP build. (Stage 4) | Report recipe, active project | Output files, build log. |

---

## 6. Jobset Design Notes

These notes capture design reasoning from the architecture review that is not
fully captured elsewhere. Relevant to Stage 2 and 3 implementation.

### Jobset file selection

When the user selects a new `.kicad_jobset` via the Setup & Run tab:

1. Open a file picker filtered to `*.kicad_jobset`.
2. Allow selection from any tokenized path — not restricted to `specgen/` folder.
3. Store the selected path as a token reference in `.kicad_specgen → jobset.active_jobset`.
4. Never modify the `.kicad_jobset` file.
5. After selection, run destination reconciliation: flag stale keys in `jobset.destinations`
   that no longer exist in the new jobset; add default entries for new destination IDs.

### `JOBSET_OUTPUT_DIR` derivation

```text
JOBSET_OUTPUT_DIR = KICAD_PROJECT_DIR / outputs[0].settings.output_path
```

Use `outputs[0]` as the representative. Before derivation, validate that all
`outputs[].settings.output_path` values share the same root. If they diverge,
show a warning: "Jobset destinations use different output paths. Using first
entry as JOBSET_OUTPUT_DIR." This is a rare edge case but must be handled.

### Output file scanning (Stage 2 Results subtab)

The Results subtab scans `JOBSET_OUTPUT_DIR` for generated files. The folder
structure must be derived dynamically from `JOBSET_OUTPUT_DIR` — do not assume
a fixed layout. The file status symbols (✓ ⚠ ✗) require stale-file detection:
a generated file is stale if it is older than the source `.kicad_sch` or
`.kicad_pcb` file. This means `output_tree.py` implicitly depends on the
KiCad project source file modification times. Document this dependency in
Stage 2.

### Output Log → Logs tab persistence (Stage 3)

The Logs tab subscribes to a shared log service (`logging_utils.py`). The
Output Log subtab shows the most recent jobset run's raw subprocess output.
After each run, the run summary is appended to the Logs tab as structured
records with `source = jobset_svc`. These are separate concerns:

```text
Output Log subtab   — raw kicad-cli stdout/stderr, cleared per run option
Logs tab            — structured SpecGen log records, persisted for session
```

---

## 7. Testing Strategy

Full test plan is in `SpecGen_Stage_Plan.md`. The tables below provide the
detailed test case specifications that guide implementation.

### Core module unit tests

| Test file | Key test cases |
|---|---|
| `test_platform_paths.py` | OS detection, KiCad config dir paths for all three platforms, KiCad version detection, missing KiCad config dir |
| `test_specgen_local_config.py` | Load valid file; load missing file; load file with missing `schema_version`; reject protected token in tokens section; reject non-absolute path in tokens; reject non-`KSG_*` token name; `recent_projects` capped at 10; oldest entry removed when cap exceeded |
| `test_specgen_company_config.py` | Load valid file; reject absolute paths in paths section; validate environment type enum; validate `company_id` non-empty; load standalone minimal file (company name "personal") |
| `test_specgen_user_config.py` | Load valid file; reject duplicate `worker_id`; warn on `active_user` not in users list; reject absolute paths in user paths |
| `test_project_config.py` | Load valid file; reject file not under `specgen/` folder; derive `KSG_PROJECT_SPECGEN_DIR` correctly; derive `KICAD_PROJECT_DIR` correctly; reject absolute paths in `files` section; validate custom variable name pattern; load file with unknown `schema_version` (warn but load) |
| `test_token_resolver.py` | Resolve simple reference; resolve nested reference; report missing token; precedence — runtime tokens override local tokens; precedence — local tokens override kicad_common vars; protected tokens cannot be user-defined; `skipped_tokens` suppresses Missing Tokens dialog |
| `test_validators.py` | All required tokens present passes; missing required token fails; kicad-cli path exists; recent project paths valid; project under `specgen/` folder; absolute path in company file fails; skipped token shows warning badge |
| `test_migrations.py` | `migrate_v1_to_v2` once v2 exists; missing `schema_version` treated as v1; future version shows upgrade prompt |
| `test_kicad_pro_parser.py` | Parse `text_variables` from fixture `.kicad_pro`; handle missing `text_variables`; handle multiple `.kicad_pro` files in directory (uses `files.kicad_pro` from project) |
| `test_kicad_jobset_parser.py` | Parse destination IDs and output paths from fixture `.kicad_jobset`; handle missing outputs section; validate all outputs share same root path; warn on divergent paths |
| `test_kicad_env.py` | Load `environment.vars` from fixture `kicad_common.json`; handle missing environment section; handle missing `kicad_common.json` gracefully |

### Integration tests

| Test | Description |
|---|---|
| Full project open sequence | Load all four config files in correct order; build effective token table; open fixture project |
| Missing token — Provide | Introduce missing token; call MissingTokensDialog handler; verify `kicad_specgen_local.json` tokens updated; verify project file unchanged |
| Missing token — Skip | Verify added to `skipped_tokens`; verify fires again on next open; verify project file unchanged |
| Missing token — Remove | Verify reference deleted from project file; verify dirty flag set; verify other users unaffected |
| File outside tokenized path | Trigger auto-conversion flow; verify new `KSG_*` token created in local config; verify project file uses token reference |
| Jobset reconciliation — open | Change jobset destinations; open project; verify warning dialog fires |
| Jobset reconciliation — save | Change jobset destinations; save project; verify warning dialog fires |
| Recent projects management | Open 11 projects in sequence; verify list stays at 10; oldest entry removed |
| Save As flow | Save project to new path; verify new file exists under `specgen/`; verify original unchanged |
| Setup bootstrap headless | Run `setup_utils` with fixture paths; verify `kicad_specgen_local.json` created correctly; verify standalone company file created with name "personal" |

### Terminology regression tests

`tests/regression/test_terminology.py` scans all source files for retired names.
See `SpecGen_Terminology.md` §16 for the complete list. Key strings that must
not appear in `core/`, `ui/`, `setup/`, or `tests/`:

```text
KICAD_SPECGEN_DIR       (old token name)
KSG_SPECGEN_DIR         (old token name)
KSG_SPECGEN_COMMON      (old token name)
kicad_specgen.json      (old config filename)
Configure Environments  (old dialog name)
ConfigureEnvironmentsDialog  (old class name)
fabrication_tab.py      (removed module)
```

---

## 8. Stage 0 Completed Deliverables

### Documents written

- [x] `SpecGen_Terminology.md`
- [x] `SpecGen_File_Framework.md` — fully reviewed (10-point)
- [x] `SpecGen_Schema_Definitions.md` — all schemas including `skipped_tokens`, preferences
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

### Key decisions made and recorded

- [x] `kicad_specgen_local.json` is the only file that stores absolute paths
- [x] All portable files use `{TOKEN_NAME}/...` notation — no exceptions
- [x] `skipped_tokens` is machine-local; `Remove` is the only way to affect the project file
- [x] Jobset reconciliation at open/save/close — not on tab display
- [x] `active_tab` and `workspace.environment` are per-project state in `.kicad_specgen → ui`
- [x] `last_session` stores only: `specgen_project`, `project_name`, `display_name`, `kicad_project_dir`, `window_geometry`, `last_opened_at`
- [x] `recent_projects` items: same fields as `last_session` minus `window_geometry`
- [x] Fabrication is the third subtab within the Report tab
- [x] `Configure` is `Edit → Configure` — not in View menu
- [x] `Preferences` is the fourth Configure subtab — not a separate dialog
- [x] 6 themes: `system`, `light`, `dark`, `engineering_dark`, `ion_dark`, `ion_light`
- [x] Setup entry point: `python setup.py` from `{KSG_APP_DIR}`
- [x] `JOBSET_OUTPUT_DIR = KICAD_PROJECT_DIR / outputs[0].settings.output_path`; warn if outputs diverge
- [x] Standalone mode: company file always exists, created with name "personal" during setup
- [x] Configure Environments scope: Option B — `Local Tokens...` for local config, Configure tab for company

---

## 9. Open Items

### Stage 1 — one document not yet written (non-blocking)

| Item | Notes |
|---|---|

### Stage 2 — needed before coding begins

| Item | Document | Notes |
|---|---|---|
| Project tab wireframes | `SpecGen_Tab_Project.md` | Create before Stage 2 coding |
| Variables tab wireframes | `SpecGen_Tab_Variables.md` | Create before Stage 2 coding |
| Jobset tab read-side detail | `SpecGen_Tab_Jobset.md` update | Add Dashboard fields, destination table columns, Results file tree, Run button disabled |
| Multi-user edit conflict for company JSON | Note in Framework | Low priority — flag when `project_service` is built |

### Stage 3+ — needed before coding begins

| Item | Document | Notes |
|---|---|---|
| Jobset tab execution detail | `SpecGen_Tab_Jobset.md` update | Add Output Log wireframe, Run/Stop controls, stale destination display |

### Living document policy

`SpecGen_Schema_Definitions.md` and `SpecGen_File_Framework.md` must be reviewed
and updated whenever:
- A new tab wireframe is created or updated
- A dialog reads or writes a config field
- Application code introduces a new config field
- A stage is completed

The three living documents (`SpecGen_Terminology.md`, `SpecGen_Progress.md`,
`SpecGen_Stage_Plan.md`) must be updated whenever any document is created or
updated.

---

## 10. Stage 1 Readiness

**Status: Ready to begin Stage 1 coding.**

All Stage 1 documentation is complete. All 10-point document reviews are done.
All critical architectural decisions are recorded. No unresolved blockers.

The one non-blocking gap (`SpecGen_Help_Guide.md`) can be written during Stage 1
alongside the initial help files without delaying any code.

See `SpecGen_Stage_Plan.md` §Stage 1 for the full module list, acceptance
criteria, test plan, and risks.

