# KiCad SpecGen — Terminology Reference

> **Document role:** Canonical single-source reference for all SpecGen names,
> labels, tokens, file names, and enumerated values.
> **Authority:** This document. When any other document conflicts with a name
> defined here, this document wins and the other document must be updated.
> **Use:** Check every new document, every code identifier, and every UI string
> against this reference before committing.
> **Status:** Approved — required before Stage 1 implementation begins.

---

## 1. Document File Names

All SpecGen documentation files follow this convention:

```text
SpecGen_{Category}_{Topic}.md

Categories:
  Tab_     Workspace tab wireframe specifications
  GUI_     Menus, dialogs, and non-tab UI concepts
  Help_    Help file style examples and authoring guides
  (none)   Core design, planning, architecture, and reference documents
```

| File Name | Category | Description |
|---|---|---|
| `SpecGen_Analysis_Prompt.md` | — | Original analysis prompt (archive) |
| `SpecGen_Progress.md` | — | Architecture review and implementation tracker |
| `SpecGen_Application_Description.md` | — | Application overview, architecture, workspace pages, module layout |
| `SpecGen_Progress.md` | — | Superseded by Progress; retained for history |
| `SpecGen_File_Framework.md` | — | Architecture specification, token model, file ownership, startup sequence, jobset reconciliation, validation requirements — primary authority |
| `SpecGen_Tab_Configure.md` | Tab_ | Configure tab wireframes — all five subtabs |
| `SpecGen_GUI_Menus.md` | GUI_ | Menu bar, dialog wireframes, help system requirements |
| `SpecGen_GUI_Theme.md` | GUI_ | Theme system specification, colour palettes, QSS guidance |
| `SpecGen_Help_JinJa.md` | Help_ | Jinja2 help file style example — canonical style template |
| `SpecGen_Schema_Definitions.md` | — | JSON schemas for all SpecGen-owned config files including `kicad_specgen_local.json`, `kicad_specgen_company.json`, `kicad_specgen_users.json`, and project `.kicad_specgen`. Living document. |
| `SpecGen_Setup_Process.md` | — | Setup wizard and Configure tab specification |
| `SpecGen_Stage_Plan.md` | — | Staged implementation plan |
| `SpecGen_Tab_Jobset.md` | Tab_ | Jobset workspace tab wireframes — started; will be updated at Stages 2 and 3 |
| `SpecGen_Tab_Report.md` | Tab_ | Report + Fabrication tab wireframes |
| `SpecGen_Terminology.md` | — | This document |

### Documents to be created

| Planned File Name | Stage | Description |
|---|---|---|
| `SpecGen_Tab_Logs.md` | Tab_ | Logs workspace tab wireframe |
| `SpecGen_Tab_Project.md` | Stage 2 | Project tab wireframes |
| `SpecGen_Tab_Variables.md` | Stage 2 | Variables tab wireframes |
| `SpecGen_Tab_Jobset.md` (Stage 2 update) | Stage 2 | Add read-side detail: Dashboard, Setup & Run table, Results file tree — Run button disabled |
| `SpecGen_Tab_Jobset.md` (Stage 3 update) | Stage 3 | Add execution detail: Output Log live feed, Run/Stop controls, stale destination reconciliation, log persistence |
| `SpecGen_GUI_Dialogs.md` | GUI_ | All dialog wireframes — Stage 1 full, Stage 2 stubs |
| `SpecGen_Help_Guide.md` | Stage 1 | Help file authoring guide |

### Note on `SpecGen_Tab_Jobset.md`

`SpecGen_Tab_Jobset.md` is a living wireframe document that evolves across three
stages. The current file reflects the initial design intent and overall structure.
It is not considered complete until Stage 3 finishes.

```text
Current (Stage 0): Overall tab structure, four subtab layout, sidebar labels,
                   general content areas. Run button shown but scope not yet
                   fully detailed.

Stage 2 update:    Add full read-side detail — Dashboard data fields, Setup & Run
                   destination table with all columns, Results file tree and
                   preview panel. Run button explicitly shown as disabled.

Stage 3 update:    Add execution detail — Output Log live feed wireframe,
                   Run/Stop/Run Selected controls enabled, stale destination
                   [stale] flag display, log persistence to Logs page.
```

These are the exact file names used on disk. Do not abbreviate, shorten, or
vary the capitalisation.

| File Name | Owner | Portable |
|---|---|---|
| `kicad_specgen_local.json` | SpecGen — local machine | No — never commit |
| `kicad_specgen_company.json` | SpecGen — shared | Yes |
| `kicad_specgen_users.json` | SpecGen — shared | Yes |
| `<name>.kicad_specgen` | SpecGen — project | Yes |
| `kicad_common.json` | KiCad — read-only | n/a |
| `<project>.kicad_pro` | KiCad — read-only | n/a |
| `<name>.kicad_jobset` | KiCad — read-only | n/a |

### Retired / invalid names — must not appear in any document or code

| Invalid Name | Correct Name | Reason |
|---|---|---|
| `kicad_specgen.json` | `kicad_specgen_local.json` | Old local config name |

---

## 3. Configuration File Locations

Canonical paths by platform. `{KICAD_COMMON_DIR}` is the OS-specific KiCad
user configuration folder detected at runtime.

| Platform | `{KICAD_COMMON_DIR}` |
|---|---|
| macOS | `~/Library/Preferences/kicad/9.0` |
| Linux | `~/.config/kicad/9.0` |
| Windows | `%APPDATA%\kicad\9.0` |

`kicad_specgen_local.json` lives alongside `kicad_common.json` in
`{KICAD_COMMON_DIR}`.

The shared SpecGen folder structure under `{KSG_COMPANY_DIR}`:

```text
{KSG_COMPANY_DIR}/
└── SpecGen/
    ├── kicad_specgen_company.json
    ├── kicad_specgen_users.json
    ├── templates/
    ├── assets/
    └── Users/
        └── <worker_id>/
            └── common/
```

---

## 4. Required Local Tokens

Stored in `kicad_specgen_local.json` → `tokens`. All values must be absolute
paths. All names must match `^KSG_[A-Z0-9_]+$`.

| Token | Required | Description |
|---|---|---|
| `KSG_APP_DIR` | Yes | Root of the installed SpecGen application repository |
| `KSG_SYSTEM_CONFIG_DIR` | Yes | OS KiCad user config folder (`{KICAD_COMMON_DIR}`) |
| `KSG_COMPANY_DIR` | Yes | Root of the shared or standalone SpecGen data folder |
| `KSG_USER_SPECGEN_DIR` | Yes | User-owned SpecGen resources folder |
| `KSG_USER_COMMON_DIR` | Yes | User-owned shared templates and assets folder |

### Optional local tokens

| Token | Description |
|---|---|
| `KSG_APP_COMMON_DIR` | Application-provided common files |
| `KSG_USER_REPORTS_DIR` | User-owned generated or reusable reports |
| `KSG_USER_TEMPLATES_DIR` | User-owned templates |
| `KSG_USER_ASSETS_DIR` | User-owned images, logos, and assets |
| `KSG_SYSTEM_LOG_DIR` | Local machine log output folder |
| `KSG_SYSTEM_CACHE_DIR` | Local cache folder |

---

## 5. Protected Derived Runtime Tokens

Computed at runtime from the opened project and active jobset. Must not appear
in `kicad_specgen_local.json` → `tokens`. Validators must reject them if found there.

| Token | Derived From | Description |
|---|---|---|
| `SPECGEN_PROJECT_FILE` | Opened `.kicad_specgen` path | Absolute path to the active project file |
| `KSG_PROJECT_SPECGEN_DIR` | Parent of `SPECGEN_PROJECT_FILE` | Project `specgen/` folder |
| `KICAD_PROJECT_DIR` | Parent of `KSG_PROJECT_SPECGEN_DIR` | KiCad project folder |
| `GIT_PROJECT_DIR` | Git root from `KICAD_PROJECT_DIR` | Git repo root; defaults to `KICAD_PROJECT_DIR` |
| `JOBSET_OUTPUT_DIR` | Active jobset output settings | Root folder for generated jobset outputs |
| `FAB_OUTPUT_DIR` | `.kicad_specgen` → `fabrication.output_dir` | Fabrication ZIP output folder; defaults to `{JOBSET_OUTPUT_DIR}/fab/` |

### Retired / invalid token names — must not appear in any document or code

| Invalid Name | Correct Name | Reason |
|---|---|---|
| `KICAD_SPECGEN_DIR` | `KSG_PROJECT_SPECGEN_DIR` | Old name; does not reflect SpecGen ownership |
| `KSG_SPECGEN_DIR` | `KSG_APP_DIR` or `KSG_PROJECT_SPECGEN_DIR` | Ambiguous — context-dependent |
| `KSG_DIR` | `KSG_COMPANY_DIR` | Too generic |
| `KSG_WORKSPACE` | (removed) | Not defined in current framework |
| `KSG_SPECGEN_COMMON` | `KSG_USER_COMMON_DIR` | Old standalone mode token name |
| `KSG_COMPANY_REPO_DIR` | `KSG_COMPANY_DIR` | Repo-mode naming baked into a general token |
| `PROJECT_DIR` | `KICAD_PROJECT_DIR` | Missing ownership prefix |
| `SPECGEN_PROJECT_DIR` | `KSG_PROJECT_SPECGEN_DIR` | Missing `KSG_` namespace prefix |

---

## 6. Token Naming Prefixes

| Prefix | Scope |
|---|---|
| `KSG_USER_*` | Individual user resources |
| `KSG_COMPANY_*` | Company, organisation, or standalone shared resources |
| `KSG_CLIENT_*` | External client resources |
| `KSG_PROJECT_*` | SpecGen-owned project resources |
| `KSG_APP_*` | SpecGen application installation resources |
| `KSG_SYSTEM_*` | OS-specific configuration resources |
| `KICAD_*` | KiCad-owned project and jobset resources (read-only) |

---

## 7. Token Reference Syntax

SpecGen token references use **single braces**:

```text
{TOKEN_NAME}/relative/path
```

Jinja2 template variables use **double braces**:

```jinja2
{{ variable_name }}
```

These two syntaxes must never be confused in documentation, help files, or
user-facing UI text. When both appear in the same document, distinguish them
explicitly.

### Token resolution priority (highest to lowest)

```text
1. Protected derived runtime tokens  (computed — override everything)
2. kicad_specgen_local.json tokens   (KSG_* absolute paths)
3. kicad_specgen_users.json paths    (resolved user paths)
4. kicad_specgen_company.json paths  (resolved company/client paths)
5. kicad_common.json environment.vars (KiCad native vars — lowest priority)
```

In project context, the per-project token selection follows:

```text
USER → CLIENT → COMPANY → DEFAULT
```

---

## 8. Enumerated Values

### Environment types (`kicad_specgen_company.json` → `environments.<id>.type`)

| Value | Description |
|---|---|
| `client` | Work performed for an external client |
| `client_group` | Work performed for a group within an external client |
| `internal_project` | Internal company or personal project |
| `sandbox` | Experimental, personal, or standalone environment |

### Worker types (`kicad_specgen_users.json` → `users.<id>.worker_type`)

| Value | Description |
|---|---|
| `employee` | Full-time or part-time employed worker |
| `contractor` | External contractor engaged by the company |
| `external` | External collaborator or partner |
| `hobby` | Standalone / personal use |

### Setup platform values (`kicad_specgen_local.json` → `setup.last_setup_platform`)

| Value |
|---|
| `macos` |
| `linux` |
| `windows` |

### Theme values (`kicad_specgen_local.json` → `preferences.theme`)

See `SpecGen_GUI_Theme.md` for full specifications and colour palettes.

| Value | Display Name | Description |
|---|---|---|
| `system` | System | OS-adaptive; resolves to `light` or `dark` at runtime |
| `light` | Light | Clean light background |
| `dark` | Dark | Dark background. Default. |
| `engineering_dark` | Engineering Dark | High-contrast dark; EDA/PCB style |
| `ion_dark` | ION Dark | ION brand — Obsidian Coal, Electric Cyan accents |
| `ion_light` | ION Light | ION brand — Clean Frost, Corporate Blue accents |

### Dependency stages (`kicad_specgen_local.json` → `setup.dependency_stage`)

| Value | Packages |
|---|---|
| `stage1` | PySide6, jsonschema, jinja2 |
| `stage2` | stage1 + subprocess management |
| `full` | stage2 + PyMuPDF, pypdf, Pillow, markdown |

### Validation result severity

| Symbol | Value | Meaning |
|---|---|---|
| ✓ | pass | Check passed — no action required |
| ⚠ | warning | Non-blocking — configuration is usable but attention recommended |
| ✗ | error | Blocking — must be resolved before project operations work |

### Schema versions

All SpecGen-owned JSON files carry `schema_version`. Current version for all
files is `1`. Files missing `schema_version` are treated as version 1.

---

## 9. Sidebar Navigation Labels

Exact labels as they appear in the UI sidebar. Case and spacing are fixed.

```text
[Project]
[Variables]
[Jobset]
[Report]
[Logs]
─────────────
[Configure]
```

Rules:
- `[Configure]` is the sidebar label. "Configure tab" is the prose description.
- The separator line `─────────────` visually divides the project workflow
  pages from the application configuration page.

---

## 10. Tab and Subtab Names

### Jobset tab subtabs

| Subtab Label | Description |
|---|---|
| `Dashboard` | Project, jobset, and last-run summary |
| `Setup & Run` | Destination table, run controls |
| `Results` | Generated output file tree and preview |
| `Output Log` | Live kicad-cli subprocess output |

### Report tab subtabs

| Subtab Label | Description |
|---|---|
| `Report Recipe` | Page order, templates, cover page configuration |
| `Preview & Build` | Generation scope selector, build log, outputs |
| `Fabrication` | ZIP contents, output location, README, checksums |

### Configure tab subtabs

| Subtab Label | Description |
|---|---|
| `Local Machine` | kicad-cli path, KSG_* tokens, .venv, setup state |
| `Company & User` | Company identity, clients, teams, user profiles |
| `Environments` | Environment definitions, active environment, active user |
| `Preferences` | UI preferences — theme and future UI behavior settings |
| `Validation` | Full configuration validation results |

---

## 11. Menu Bar Labels

Exact menu names and key items. Full menu specifications are in `SpecGen_GUI_Menus.md`.

### File menu

```text
New SpecGen Project...
Open SpecGen Project...
Open Recent
Copy / Create From Existing Project...
Save
Save As...
Close Project
───────────────────────────────────────
Exit
```

### Edit menu

```text
Local Tokens...
Resolve Missing Tokens...
Configure kicad-cli...
───────────────────────────────────────
Edit Project Metadata...
Edit Custom Variables...
Validate Project
───────────────────────────────────────
Configure
```

### View menu

```text
Project
Variables
Jobset
Report
Logs
─────────────────────────────────────
Toggle Sidebar
Toggle Status Bar
Refresh
─────────────────────────────────────
Theme
```

### Help menu

Per `SpecGen_GUI_Menus.md` specification.

### Retired / invalid menu items — must not appear in code or documents

| Invalid Label | Correct Replacement | Reason |
|---|---|---|
| `Configure Environments...` | `Local Tokens...` (Edit menu) | Old scope — conflated local and company file edits |
| `Preferences...` (Edit menu) | `Configure` (Edit menu) | Renamed to match sidebar label; now a page switch |
| `Results (Jobset subtab)` (View menu) | Removed | Results is internal to the Jobset tab |
| `JS Results` (sidebar) | Removed | Old design; Results is a Jobset subtab |

---

## 12. Dialog Names

Exact dialog title bar text.

| Dialog Title | Launched From |
|---|---|
| `KiCad SpecGen Setup Wizard` | Startup banner / `[Configure]` tab → Re-run Setup Wizard |
| `New SpecGen Project` | File → New SpecGen Project... |
| `Missing Tokens` | Automatic on token resolution failure |
| `Local Tokens` | Edit → Local Tokens... |
| `Configure kicad-cli` | Edit → Configure kicad-cli... |
| `Edit Clients and Teams` | Configure tab → Company & User subtab |
| `Add User` / `Edit User` | Configure tab → Company & User subtab → Add/Edit User |
| `Overwrite Existing Output?` | Preview & Build subtab → Build (when target exists) |
| `Add Report Page` | Report Recipe subtab → Add Page |
| `About KiCad SpecGen` | Help → About |
| `Help` | Help → (any topic) |

---

## 13. Python Module Names

Canonical module names by layer. These are the names used in `import` statements
and file paths. Do not introduce synonyms.

### Application root

| File | Description |
|---|---|
| `main.py` | Application entry point |
| `app.py` | QApplication setup, theme, font, signal wiring |

### `core/`

| Module | Description |
|---|---|
| `platform_paths.py` | OS detection, `KICAD_COMMON_DIR` resolution |
| `specgen_local_config.py` | Load / validate / save `kicad_specgen_local.json` |
| `specgen_company_config.py` | Load / validate / save `kicad_specgen_company.json` |
| `specgen_user_config.py` | Load / validate / save `kicad_specgen_users.json` |
| `project_config.py` | Load / validate / save / migrate `.kicad_specgen` |
| `token_resolver.py` | Build effective token table, report missing tokens |
| `validators.py` | All validation rules; returns structured results |
| `file_ops.py` | Atomic JSON write, backup, directory creation |
| `migrations.py` | Schema version migration functions |
| `logging_utils.py` | Python logging config, structured log records |
| `app_state.py` | In-memory application state, observable fields |
| `kicad_pro_parser.py` | Parse `text_variables` from `.kicad_pro` |
| `kicad_jobset_parser.py` | Parse `outputs[]` and destination IDs from `.kicad_jobset` |
| `kicad_env.py` | Read `environment.vars` from `kicad_common.json` |

### `core/render/`

| Module | Description |
|---|---|
| `jinja_renderer.py` | Render `.md` templates with token + variable injection |
| `pdf_assembler.py` | Assemble rendered pages and jobset PDFs into report PDF |

### `core/fab/`

| Module | Description |
|---|---|
| `package_builder.py` | Collect files, render README, compute checksums, write ZIP |

### `services/`

| Module | Description |
|---|---|
| `config_service.py` | Save local / company / user configs; state refresh |
| `validation_service.py` | `run_config_validation()` — configuration-only validation |
| `project_service.py` | Open, create, save, close project; full startup sequence |
| `jobset_service.py` | kicad-cli subprocess, output capture, run state (Stage 3) |
| `report_service.py` | Orchestrate report render and fabrication ZIP build (Stage 4) |

### `setup/`

| Module | Description |
|---|---|
| `setup.py` | Entry point; phase orchestration; GUI/headless dispatch |
| `setup_macos.py` | macOS platform detection, kicad-cli search order |
| `setup_linux.py` | Linux platform detection, kicad-cli search order |
| `setup_windows.py` | Windows platform detection, kicad-cli search order |
| `setup_utils.py` | .venv creation, pip install, progress reporting |

### `ui/`

| Module | Description |
|---|---|
| `main_window.py` | QMainWindow, menu bar, sidebar, tab widget, status bar |
| `sidebar.py` | Sidebar navigation widget, active page tracking |
| `setup_wizard.py` | SetupWizardDialog — 6-phase wizard with phase navigator |
| `theme.py` | Application theme constants, stylesheet loading |
| `actions.py` | QAction definitions, keyboard shortcuts |

### `ui/tabs/`

| Module | Description |
|---|---|
| `configuration_tab.py` | ConfigurationTab — 4 subtabs |
| `logs_tab.py` | LogsTab |
| `project_tab.py` | ProjectTab |
| `variables_tab.py` | VariablesTab |
| `jobset_tab.py` | JobsetTab — 4 subtabs |
| `report_tab.py` | ReportTab — 3 subtabs |

### `ui/dialogs/`

| Module | Description |
|---|---|
| `local_tokens_dialog.py` | Edit `kicad_specgen_local.json` tokens only |
| `missing_tokens_dialog.py` | Display missing tokens, emit repair intents |
| `new_project_dialog.py` | New project folder and environment selection |
| `about_dialog.py` | Version, platform, paths |
| `help_dialog.py` | QTextBrowser Markdown renderer |
| `kicad_cli_dialog.py` | Browse and check kicad-cli path |
| `add_user_dialog.py` | Add / edit user in `kicad_specgen_users.json` |
| `clients_teams_dialog.py` | Edit clients and teams in `kicad_specgen_company.json` |

### `ui/widgets/`

| Module | Description |
|---|---|
| `token_table.py` | Reusable token display table (read + edit modes) |
| `path_field.py` | Path entry field with Browse button and status icon |
| `validation_panel.py` | Display validation results (✓ ⚠ ✗ per check) |
| `log_viewer.py` | Scrollable log record display widget |
| `output_tree.py` | File tree widget for Jobset Results subtab |
| `file_preview.py` | Preview panel for PDF, image, text, CSV files |

---

## 14. Python Class Names

| Class | Module | Description |
|---|---|---|
| `ConfigurationTab` | `ui/tabs/configuration_tab.py` | Note: class name uses "Configuration"; sidebar label is `[Configure]` |
| `SetupWizardDialog` | `ui/setup_wizard.py` | |
| `LocalTokensDialog` | `ui/dialogs/local_tokens_dialog.py` | Formerly `ConfigureEnvironmentsDialog` — do not use old name |

**Important:** The Python class name `ConfigurationTab` and the sidebar label
`[Configure]` are intentionally different. The class name is a code identifier;
the sidebar label is a UI string. Do not rename the class to match the label.

---

## 15. Help File Names

Files in the application `help/` folder. These are the exact filenames used in
`help_dialog.py` to load help content.

| File | Stage | Status |
|---|---|---|
| `index.md` | Stage 1 | Required |
| `getting_started.md` | Stage 1 | Required |
| `project_setup_tokens.md` | Stage 1 | Required |
| `configure_tab.md` | Stage 1 | Required |
| `logs.md` | Stage 1 | Required |
| `troubleshooting.md` | Stage 1 | Required |
| `kicad_specgen_local.md` | Stage 1 | Required |
| `project_kicad_specgen.md` | Stage 2 | Required |
| `variables_jinja.md` | Stage 2 | Required |
| `jobset.md` | Stage 2 | Placeholder in Stage 1; full in Stage 2 |
| `report.md` | Stage 4 | Placeholder in Stage 1; full in Stage 4 |

---

## 16. Terminology Regression Test Targets

The following strings must not appear anywhere in the `core/`, `ui/`, `setup/`,
or `tests/` directories. Each is a retired name that would indicate a
terminology drift error.

```text
KICAD_SPECGEN_DIR           (retired token name)
KSG_SPECGEN_DIR             (retired token name)
KSG_DIR                     (retired token name)
KSG_WORKSPACE               (retired token name)
KSG_SPECGEN_COMMON          (retired token name)
kicad_specgen.json          (retired file name)
Configure Environments      (retired dialog name — now Local Tokens)
JS Results                  (retired sidebar label)
ConfigureEnvironmentsDialog (retired class name — now LocalTokensDialog)
```

These strings are checked by the terminology regression tests in Stage 5
(`tests/regression/test_terminology.py`) and should be checked by code review
from Stage 1 onwards.

---

*End of SpecGen Terminology Reference.*
