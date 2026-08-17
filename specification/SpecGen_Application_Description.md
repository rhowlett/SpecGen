# KiCad SpecGen — Application Reference

> **Document role:** Application overview, architecture description, workspace
> page summaries, module layout, and implementation requirements.
> **Authority:** `SpecGen_Terminology.md`, `SpecGen_Stage_Plan.md`,
> `SpecGen_Setup_Process.md`.
> **Companion documents:** `SpecGen_GUI_Menus.md`, `SpecGen_Tab_Jobset.md`,
> `SpecGen_Tab_Report.md`, `SpecGen_Schema_Definitions.md`.
> **Status:** Updated — ready for Stage 1 implementation reference.
>
> **Note:** Menu item behavior, dialog acceptance criteria, and help system
> requirements are fully specified in `SpecGen_GUI_Menus.md`. This document
> describes the application structure and implementation architecture.

---

## Table of Contents

Introduction to KiCad SpecGen
Software and Documentation Version
Application Overview
Workspace Modes
Configuration Files
Token and Path Resolution
Application Startup
Setup Bootstrap
Main Window
Menu Commands
Sidebar Navigation
Workspace Pages
Project Page
Variables Page
Logs Page
Configure Tab
Local Tokens Dialog
Missing Tokens Dialog
Project File Commands
Stage 1 Scope
Future Application Stages
Validation
Recommended Module Layout
Implementation Requirements

---

# KiCad SpecGen Application Reference Manual

This document describes the KiCad SpecGen application user interface, configuration model, and Stage 1 implementation scope.

KiCad SpecGen is a desktop application for creating repeatable KiCad project release documentation and fabrication packages. It is intended to assist electronics design engineers with project setup, environment validation, jobset execution, generated file review, report generation, and fabrication output packaging.

This document focuses on the application framework and Stage 1 GUI behavior.

---

## Software and Documentation Version

This reference is written for KiCad SpecGen Stage 1.

The intended KiCad target is KiCad 9.0 or later.

The intended Python target is Python 3.10 or later.

The GUI toolkit is PySide6.

The application is installed from a Git repository and runs in its own `.venv/`
located at `{KSG_APP_DIR}/.venv` inside the SpecGen application repository.
The `.venv` is excluded from the Git repository.

---

# Introduction to KiCad SpecGen

KiCad SpecGen is a standalone Python desktop application.

The application does not depend on KiCad’s bundled Python environment.

The application does not require the `pcbnew` Python module.

KiCad integration is performed through:

```text
kicad-cli
read-only JSON parsing
read-only KiCad S-expression parsing where needed
```

The primary goal of KiCad SpecGen is to make KiCad release generation repeatable and portable.

The application manages:

```text
project configuration
portable path tokens
project variables
KiCad jobset selection
generated output review
release report generation
fabrication package generation
logs and validation results
```

---

# Application Overview

KiCad SpecGen is organized around a main window with:

```text
top menu bar
left sidebar navigation rail
central workspace
status bar
```

The application uses a standard `QMainWindow` layout.

The central workspace is implemented with a `QTabWidget`.

The left sidebar controls the active workspace page.

The tab bar may be hidden so that the sidebar is the primary navigation control.

Usage:

```text
SpecGen main window
  File menu
  Edit menu
  View menu
  Help menu
  Sidebar navigation
  Workspace pages
  Status bar
```

Stage 1 implements the application shell and the first functional pages:

```text
Setup wizard (inline and standalone)
Project
Variables
Logs
Configure tab
Local Tokens dialog
Missing Tokens dialog
```

Later stages implement:

```text
Stage 2: Project tab (full), Variables tab (full), Jobset tab (read-only)
Stage 3: Jobset tab (execution, Output Log)
Stage 4: Report tab (Report Recipe, Preview & Build, Fabrication subtab)
Stage 5: Integration testing and polish
```

---

# Workspace Modes

KiCad SpecGen supports two workspace modes:

```text
repo
standalone
```

## Repo mode

Repo mode is used when the KiCad project is part of a Git-managed workspace.

Repo mode is intended for:

```text
professional multi-project workflows
shared hardware repositories
client-separated workspaces
internal engineering repositories
```

A repo environment normally defines:

```text
KSG_COMPANY_DIR
KSG_APP_DIR
KSG_USER_COMMON_DIR
```

## Standalone mode

Standalone mode is used when the KiCad project is an independent folder and is
not part of a shared Git workspace. Typical users are hobby users, students, or
one-off project users.

In standalone mode, `kicad_specgen_company.json` always exists — it is created
with company name "personal" by default during setup. There is no Git repository
requirement.

All five required tokens must still be defined:

```text
KSG_APP_DIR
KSG_SYSTEM_CONFIG_DIR
KSG_COMPANY_DIR        (points to a local folder, not a Git repo)
KSG_USER_SPECGEN_DIR
KSG_USER_COMMON_DIR
```

---

# Configuration Files

KiCad SpecGen uses the following configuration files.

## `kicad_specgen_local.json`

`kicad_specgen_local.json` is the local-machine SpecGen configuration file.

It stores:

```text
KSG_* absolute token definitions
kicad-cli path
setup status and platform
last opened SpecGen project (last_session)
recent project list
active user
active environment
preferences (theme etc.)
```

This file may contain absolute paths because it belongs to the local user and
machine. It must not be committed to any shared repository.

It is stored in the KiCad user configuration folder alongside `kicad_common.json`.

## `kicad_specgen_company.json`

`kicad_specgen_company.json` is the shared company configuration file.

It stores:

```text
company identity
client definitions
internal team definitions
environment definitions
shared path references (tokenized)
```

It lives under `{KSG_COMPANY_DIR}/SpecGen/`. It uses token references, not
absolute paths. It may be committed to a shared repository.

In standalone mode, this file is created automatically with company name
"personal" during setup.

## `kicad_specgen_users.json`

`kicad_specgen_users.json` stores user profiles.

It lives under `{KSG_COMPANY_DIR}/SpecGen/`. It may be committed to a shared
repository.

## Project `.kicad_specgen` file

A project `.kicad_specgen` file is the SpecGen project file.

Opening a `.kicad_specgen` file is equivalent to opening a SpecGen project.

It stores:

```text
project state
selected environment name
active KiCad project identity
active jobset reference
project variables
jobset destination overrides
report recipe
fabrication recipe
UI state (last active tab, panel sizes)
```

The project `.kicad_specgen` file must live in the KiCad project-local
`specgen/` folder:

```text
{KICAD_PROJECT_DIR}/specgen/<name>.kicad_specgen
```

The project `.kicad_specgen` file must store token references, not local
machine absolute path definitions.

---

# Token and Path Resolution

SpecGen separates path information into two categories.

```text
Token definitions
  Absolute paths stored in local machine configuration.

Token references
  Portable path strings stored in project configuration.
```

Stored SpecGen token definitions use the `KSG_*` namespace.

Examples:

```text
KSG_COMPANY_DIR
KSG_APP_DIR
KSG_USER_COMMON_DIR
KSG_CLIENT_DOCS
KSG_CLIENT_ASSETS
```

Project-derived runtime tokens do not use the `KSG_*` prefix.

Protected derived tokens:

```text
SPECGEN_PROJECT_FILE
KSG_PROJECT_SPECGEN_DIR
KICAD_PROJECT_DIR
GIT_PROJECT_DIR
JOBSET_OUTPUT_DIR
FAB_OUTPUT_DIR
```

## Resolution order

When resolving a token reference, SpecGen builds an effective token table from
all sources. The full resolution order (lowest to highest priority):

```text
1. kicad_common.json environment.vars
   (KiCad-native variable names)

2. kicad_specgen_local.json tokens
   (KSG_* absolute path tokens — override kicad_common entries)

3. kicad_specgen_company.json resolved paths
   (resolved using local tokens)

4. kicad_specgen_users.json resolved user paths
   (resolved using local tokens)

5. Protected derived runtime tokens
   (computed from opened .kicad_specgen — override everything)
```

Later sources override earlier sources.

At project level, the per-project token selection priority is:

```text
USER → CLIENT → COMPANY → DEFAULT
```

This guarantees that project-local paths such as `KICAD_PROJECT_DIR` always
come from the opened `.kicad_specgen` file location.

---

# Application Startup

The application startup flow checks for completed setup, then restores the last
project when possible. See `SpecGen_Setup_Process.md` §4 for the full startup
detection sequence.

```text
Start KiCad SpecGen
  Detect KICAD_COMMON_DIR for current OS and KiCad version
  Check whether kicad_specgen_local.json exists
  If missing or setup_complete = false:
    Show Setup Required banner
    Launch Setup Wizard (inline)
  Else:
    Load kicad_specgen_local.json
    Load kicad_specgen_company.json
    Load kicad_specgen_users.json
    Restore last_session project if available
    Resolve effective token table
    Open main window
```

If no previous session exists, the user is prompted to create or open a
SpecGen project.

If setup has not completed, the application shows a Setup Required banner and
offers: `[ Run Setup Now ]` or `[ Defer — Limited Mode ]`. In Limited Mode,
the Configure tab is accessible but project operations are disabled.

---

# Setup Bootstrap

Setup is part of Stage 1. See `SpecGen_Setup_Process.md` for the full
six-phase specification, wireframes, and headless mode documentation.

The setup entry point is:

```text
python setup.py
```

Run from `{KSG_APP_DIR}`.

Invocation options:

```text
python setup.py                    Standard interactive setup
python setup.py --headless         Text-only mode
python setup.py --no-prompt        Accept defaults (CI)
python setup.py --full             Install all dependency stages
python setup.py --reconfigure      Force re-run
python setup.py --validate-only    Report only, no writes
```

The top-level setup script detects the operating system and dispatches to:

```text
setup/setup_macos.py
setup/setup_linux.py
setup/setup_windows.py
```

Setup responsibilities:

```text
Phase 1: Platform detection — OS, KiCad version, KICAD_COMMON_DIR
Phase 2: Dependency installation — create {KSG_APP_DIR}/.venv, install packages
Phase 3: Tool detection — locate kicad-cli per platform search order
Phase 4: Workspace mode selection — Shared/Repo or Standalone/Local
Phase 5: Company and user configuration
Phase 6: Local token configuration and validation
```

The `.venv` is always created at `{KSG_APP_DIR}/.venv` and is excluded from
the Git repository.

If `kicad-cli` is not found in the shell PATH but is found in a known
application bundle location, setup saves the absolute path in
`kicad_specgen_local.json → tools.kicad_cli_path`.

If setup modifies `kicad_common.json`, it must create a timestamped backup:

```text
kicad_common.json.bak_YYYYMMDD_HHMMSS
```

---

# Main Window

The main window is implemented with `QMainWindow`.

The main window contains:

```text
QMenuBar
optional QToolBar
left sidebar navigation rail
central QTabWidget workspace
QStatusBar
```

Recommended layout:

```text
QMainWindow
  QMenuBar
  QWidget central widget
    QHBoxLayout
      Sidebar navigation rail
      QTabWidget workspace
  QStatusBar
```

The sidebar is the primary navigation control.

The `QTabWidget` holds page widgets.

The tab bar may be hidden:

```text
QTabWidget.tabBar().hide()
```

This avoids duplicate navigation while preserving simple page management.

---

# Menu Commands

The application uses a standard top menu bar with:

```text
[File] [Edit] [View] [Help]
```

Each menu contains actions that either:

* operate on the active SpecGen project file
* open a dialog or switch the active workspace view
* validate configuration
* display help content or diagnostic information

Menu item behavior, dialog specifications, and help system requirements are
fully defined in `SpecGen_GUI_Menus.md`. The sections below describe the menu
structure for reference.

---

## File menu

```text
┌───────────────────────────────────────┐
│ [File]                                │
├───────────────────────────────────────┤
│ New SpecGen Project...                │
│ Open SpecGen Project...               │
│ Open Recent                           │
│ Copy / Create From Existing Project...│
│ Save                                  │
│ Save As...                            │
│ Close Project                         │
│ ───────────────────────────────────── │
│ Exit                                  │
└───────────────────────────────────────┘
```

See `SpecGen_GUI_Menus.md` for full behavior specification of each item.

---

## Edit menu

```text
┌───────────────────────────────────────┐
│ [Edit]                                │
├───────────────────────────────────────┤
│ Local Tokens...                       │
│ Resolve Missing Tokens...             │
│ Configure kicad-cli...                │
│ ───────────────────────────────────── │
│ Edit Project Metadata...              │
│ Edit Custom Variables...              │
│ Validate Project                      │
│ ───────────────────────────────────── │
│ Configure                             │
└───────────────────────────────────────┘
```

See `SpecGen_GUI_Menus.md` for full behavior specification of each item.

---

## View menu

```text
┌───────────────────────────────────────┐
│ [View]                                │
├───────────────────────────────────────┤
│ Project                               │
│ Variables                             │
│ Jobset                                │
│ Report                                │
│ Logs                                  │
│ ───────────────────────────────────── │
│ Toggle Sidebar                        │
│ Toggle Status Bar                     │
│ Refresh                               │
│ ───────────────────────────────────── │
│ Theme                                 │
└───────────────────────────────────────┘
```

`Configure` is accessed via `Edit → Configure`, not the View menu.

Stage 1 implements Project, Variables, Logs, and Configure as functional pages.
Jobset and Report show placeholder content until their implementation stages.

See `SpecGen_GUI_Menus.md` for full behavior specification of each item.

---

## Help menu

```text
┌─────────────────────────────────────────────────┐
│ [Help]                                          │
├─────────────────────────────────────────────────┤
│ KiCad SpecGen Help                              │
│ Getting Started                                 │
│ Project Setup and Tokens                        │
│ Configure Tab                                   │
│ Project Page                                    │
│ Variables and Jinja Templates                   │
│ Jobset                                          │
│ Report and Fabrication                          │
│ Logs                                            │
│ Troubleshooting                                 │
│ ─────────────────────────────────────────────── │
│ Show kicad_specgen_local.json Location          │
│ Show kicad_common.json Location                 │
│ Check kicad-cli                                 │
│ Open Logs Folder                                │
│ ─────────────────────────────────────────────── │
│ About KiCad SpecGen                             │
└─────────────────────────────────────────────────┘
```

Help topics open a `HelpDialog` (`QTextBrowser`) rendering the corresponding
Markdown file from the application `help/` folder.

See `SpecGen_GUI_Menus.md` for full behavior specification of each item.

---

# Sidebar Navigation

The sidebar navigation rail is shown on the left side of the main window.

Implementation: `QListWidget`.

The visual separator between `[Logs]` and `[Configure]` is implemented as a
non-selectable `QListWidgetItem` with a `QFrame(QFrame.Shape.HLine)` set as
its `setItemWidget()`, and `Qt.ItemFlag.NoItemFlags` to prevent selection and
keyboard navigation onto the separator. The sidebar's selection-changed handler
must exclude separator items.

Sidebar entries:

```text
[Project]
[Variables]
[Jobset]
[Report]
[Logs]
─────────────
[Configure]
```

The Fabrication subtab is the third subtab within the Report workspace.
`[Results]` is a subtab within the Jobset workspace, not a separate sidebar entry.

The separator line visually divides the project workflow pages (Project through
Logs) from the application configuration page (Configure).

Each entry selects the corresponding page in the central `QTabWidget`.

Stage 1 functional pages:

```text
[Logs]
[Configure]
```

Stage 1 placeholder pages (show "Open a project to get started"):

```text
[Project]
[Variables]
[Jobset]
[Report]
```

The sidebar may display page status in later versions:

```text
OK
Warning
Error
Not Ready
```

---

# Workspace Pages

Each workspace page is a separate widget.

Recommended page classes:

```text
ProjectTab
VariablesTab
JobsetTab
ReportTab
LogsTab
ConfigurationTab
```

Results is a subtab within `JobsetTab`. Fabrication is a subtab within `ReportTab`.

Pages should read from application state.

Pages should emit intentional user actions.

Pages should not parse files directly.

Parsing, validation, token resolution, and file operations belong in shared
core modules.

---

# Project Page

The Project page is the main project dashboard.

It displays the active project file, selected environment, effective tokens, KiCad paths, and report support file selections.

Usage:

```text
Project page
  Project identity panel
  SpecGen project file panel
  Selected environment panel
  Effective token table
  KiCad environment table
  Report support files panel
  Validation panel
```

The Project page should show:

```text
active .kicad_specgen file
selected environment
KICAD_PROJECT_DIR
KSG_PROJECT_SPECGEN_DIR
GIT_PROJECT_DIR
active .kicad_pro file
active .kicad_jobset file
KSG_APP_DIR
KSG_USER_COMMON_DIR
logo path
report CSS path
BOM CSS path
title page template
end page template
validation status
```

Recommended Project page actions:

```text
Open SpecGen Project...
Save
Save As...
Local Tokens...
Resolve Missing Tokens...
Validate Project
Refresh From Disk
```

The Project page should include an effective token table.

Recommended columns:

```text
Token
Resolved Path
Source
Status
Notes
```

The Project page may also include a read-only table of raw `kicad_common.json` environment variables.

---

# Variables Page

The Variables page displays variables available to templates and report generation.

Usage:

```text
Variables page
  KiCad project variables
  SpecGen metadata
  Custom variables
  Validation panel
```

The Variables page should show:

```text
read-only variables from .kicad_pro
editable SpecGen metadata
editable company metadata
editable custom template variables
validation status
```

Read-only variables include KiCad `.kicad_pro` text variables.

Editable values are saved in the project `.kicad_specgen` file.

Custom variable names should be validated.

Recommended custom variable name rule:

```text
^[A-Z][A-Z0-9_]*$
```

---

# Logs Page

The Logs page displays basic application log messages.

Stage 1 logging is intentionally simple.

Usage:

```text
Logs page
  Timestamp
  Level
  Source
  Message
```

Stage 1 log sources may include:

```text
setup
application
project
validation
token_resolver
config_io
```

Later stages may add:

```text
jobset execution output
report build output
fabrication package output
```

Setup may share logging utilities with the GUI, but `setup.py` remains a standalone bootstrap program.

---

# Configure Tab

The Configure tab is a permanent sidebar page (`[Configure]`) that provides
full post-setup configuration management without re-running `setup.py`.

It is always accessible — no project is required.

It contains six subtabs:

```text
Local Machine   — KSG_* tokens, kicad-cli path, .venv status, setup state
                  Writes: kicad_specgen_local.json
Company         — company identity (name, description, website, logo, address)
                  Writes: kicad_specgen_company.json
Users           — departments, teams, and user profiles
                  Writes: kicad_specgen_company.json, kicad_specgen_users.json
Environments    — environment definitions, active environment, active user
                  Writes: kicad_specgen_company.json, kicad_specgen_local.json
Preferences     — active UI theme
                  Writes: kicad_specgen_local.json
Validation      — full configuration validation results (read-only)
```

**Subtab architecture.** `configuration_tab.py` is a thin container. Each
subtab lives in its own file under `ui/tabs/configure/` and subclasses
`SubtabBase`, which defines the contract: `TITLE`, `ORDER`, a `populate()`
that reads from `app_state`, and an `on_save()` that writes through
`config_service`. The container instantiates the registered subtab classes in
`ORDER`, adds them to a `QTabWidget`, and calls each one's `refresh()` when
`app_state.config_reloaded` fires. To add a subtab, create a new file and add
its class to the container's `SUBTABS` list — no other file changes.

**Stickiness and the dirty save button.** Subtab widgets are created once and
kept alive, so switching subtabs preserves unsaved input. `refresh()`
repopulates a subtab only when it is not dirty, so an external config reload
never clobbers unsaved edits. Editing any field calls `mark_dirty()`, which
turns the subtab's Save button green (via `theme.set_save_dirty`); a
successful save calls `mark_clean()`, which clears it.

`Edit → Configure` is a page switch to this tab. `Edit → Local Tokens...`
opens the `LocalTokensDialog` for quick token editing without navigating to
the tab.

See `SpecGen_Setup_Process.md` §9 for full wireframes and behavior.

---

# Local Tokens Dialog

`LocalTokensDialog` is opened via `Edit → Local Tokens...`.

Purpose: quick editing of `KSG_*` token definitions in `kicad_specgen_local.json → tokens`.

Rules:

```text
Token names must match ^KSG_[A-Z0-9_]+$
Token values must be absolute paths
The five required tokens cannot be removed
Protected derived runtime tokens are rejected
```

Protected derived tokens (rejected if entered):

```text
SPECGEN_PROJECT_FILE
KSG_PROJECT_SPECGEN_DIR
KICAD_PROJECT_DIR
GIT_PROJECT_DIR
JOBSET_OUTPUT_DIR
FAB_OUTPUT_DIR
```

See `SpecGen_GUI_Menus.md` for the full dialog wireframe and acceptance criteria.

---

# Missing Tokens Dialog

The Missing Tokens dialog resolves token references that cannot be resolved for the current project.

Usage:

```text
Edit -> Resolve Missing Tokens...
```

The dialog should show:

```text
missing token name
selected environment
affected project settings
affected files
suggested action
```

User actions:

```text
Add token to kicad_specgen_local.json → tokens
Pick replacement file or folder
Skip affected item
Cancel open
```

If the user adds a token, SpecGen updates:

```text
kicad_specgen_local.json → tokens.<TOKEN_NAME>
```

The project `.kicad_specgen` file should remain portable and should not be rewritten with an absolute path.

---

# Project File Commands

SpecGen project commands operate on `.kicad_specgen` files.

## New project command

```text
New SpecGen Project
  Select {KICAD_PROJECT_DIR} (Browse to KiCad project folder)
  Set SpecGen project name (auto-fills from folder name)
  Select environment (from kicad_specgen_company.json → environments)
  Create {KSG_PROJECT_SPECGEN_DIR} if missing
  Copy default.kicad_specgen from {KSG_APP_DIR}
  Set environment in project workspace section
  Save <name>.kicad_specgen under {KICAD_PROJECT_DIR}/specgen/
  Update kicad_specgen_local.json → last_session and recent_projects
```

Stage: Stage 2.

## Open project command

```text
Open SpecGen Project
  Select <name>.kicad_specgen via QFileDialog
  If unsaved changes: prompt Save / Discard / Cancel
  Derive KSG_PROJECT_SPECGEN_DIR from file location
  Derive KICAD_PROJECT_DIR from file location
  Load kicad_specgen_company.json and kicad_specgen_users.json
  Discover active .kicad_pro
  Resolve effective token table
  If tokens missing: trigger MissingTokensDialog automatically
  Populate Project page
  Update kicad_specgen_local.json → last_session and recent_projects
```

Stage: Stage 2.

## Save command

```text
Save
  Check dirty flag (skip if clean)
  Validate no absolute paths in project file
  Write {SPECGEN_PROJECT_FILE}
  Clear dirty flag
  Update status bar
  Update kicad_specgen_local.json → last_session
```

Stage: Stage 2.

## Save As command

```text
Save As
  Open QFileDialog (default: {KSG_PROJECT_SPECGEN_DIR})
  Warn if destination is outside {KICAD_PROJECT_DIR}/specgen/
  If destination exists: prompt Overwrite / Rename / Cancel
  Save project .kicad_specgen to new path
  Update {SPECGEN_PROJECT_FILE} to new path
  Update kicad_specgen_local.json → last_session and recent_projects
```

Stage: Stage 2.

---

# Stage 1 Scope

Stage 1 implements the application foundation. See `SpecGen_Stage_Plan.md` §Stage 1
for the full module list, acceptance criteria, and test plan.

Required Stage 1 deliverables:

```text
setup.py (6-phase wizard, headless mode, {KSG_APP_DIR}/.venv)
core layer (all modules: token_resolver, validators, config loaders, etc.)
services layer (config_service, validation_service)
QMainWindow shell
menu bar (File / Edit / View / Help — all items present)
sidebar navigation with separator
central QTabWidget workspace
Project page (placeholder — full in Stage 2)
Variables page (placeholder — full in Stage 2)
Jobset page (placeholder — full in Stage 2/3)
Report page (placeholder — full in Stage 4)
Logs page (full)
Configure tab (full — 6 subtabs)
LocalTokensDialog
MissingTokensDialog (stub — full in Stage 2)
NewProjectDialog (stub — full in Stage 2)
AboutDialog
HelpDialog (QTextBrowser)
KicadCliDialog
kicad_specgen_local.json load/save
kicad_specgen_company.json load/save
kicad_specgen_users.json load/save
token resolver
effective token table
validation framework
setup wizard (inline and standalone)
basic QSS theme
help/ folder with Stage 1 topics
```

Stage 1 does not implement:

```text
project .kicad_specgen open/save (Stage 2)
kicad_pro_parser (Stage 2)
kicad_jobset_parser (Stage 2)
jobset execution (Stage 3)
report rendering (Stage 4)
fabrication ZIP packaging (Stage 4)
Copy / Create From Existing wizard (Future)
```

---

# Future Application Stages

See `SpecGen_Stage_Plan.md` for the complete stage plan with module lists,
acceptance criteria, and test strategies.

## Stage 2: Project Tab, Variables Tab, Jobset Reading

```text
project .kicad_specgen open/save/close (full)
kicad_pro_parser — read .kicad_pro text variables
kicad_jobset_parser — read .kicad_jobset destinations
Project tab (full)
Variables tab (full — KiCad vars read-only, custom vars editable)
Jobset tab Dashboard and Setup & Run (read-only; Run button disabled)
Jobset tab Results (output folder scan, file tree, preview)
NewProjectDialog (full)
MissingTokensDialog (full)
```

## Stage 3: Jobset Execution

```text
jobset_service — kicad-cli subprocess, output capture
Jobset tab Output Log (live feed)
Run All / Run Selected / Stop controls enabled
stale destination reconciliation
Output Log → Logs page persistence
```

## Stage 4: Report and Fabrication

```text
report_service — Jinja2 rendering, PDF assembly, FAB ZIP packaging
Report tab (full — Report Recipe, Preview & Build, Fabrication subtabs)
jinja_renderer, pdf_assembler, package_builder
```

## Stage 5: Integration Testing and Polish

```text
cross-stage integration tests
session restore verification
terminology regression sweep
performance baseline
UI polish (disabled states, keyboard navigation, status bar accuracy)
```

---

# Validation

Validation should produce clear user-facing messages.

Validation should not show raw stack traces for normal user errors.

Stage 1 validation should check:

```text
kicad_specgen_local.json exists or can be created
schema_version is supported
active environment exists
required KSG_* tokens exist
stored token values are absolute paths
protected derived tokens are not stored
kicad-cli path exists or is marked missing
opened .kicad_specgen file is under a specgen folder
KICAD_PROJECT_DIR can be derived
active .kicad_pro can be found or selected
project token references resolve
custom variable names are valid
```

Missing-token validation should offer a repair path.

File-writing validation should warn before overwrite.

If modifying `kicad_common.json`, SpecGen must create a timestamped backup first.

---

# Recommended Module Layout

See `SpecGen_Stage_Plan.md` for the authoritative stage-by-stage module list.
The layout below shows the full expected structure after all stages complete.

```text
main.py
app.py

schema/                              # standalone JSON Schema files (draft-07)
  kicad_specgen_local.schema.json
  kicad_specgen_company.schema.json
  kicad_specgen_users.schema.json
  specgen_project.schema.json
  kicad_common.schema.json           # partial, read-only (KiCad-owned file)

core/
  app_state.py
  platform_paths.py
  logging_utils.py
  file_ops.py
  migrations.py
  kicad_env.py
  kicad_pro_parser.py
  kicad_jobset_parser.py
  specgen_local_config.py
  specgen_company_config.py
  specgen_user_config.py
  project_config.py
  token_resolver.py
  validators.py
  schema_loader.py

  render/
    jinja_renderer.py
    pdf_assembler.py

  fab/
    package_builder.py

services/
  config_service.py
  validation_service.py
  project_service.py
  jobset_service.py
  report_service.py

setup/
  setup.py
  setup_macos.py
  setup_linux.py
  setup_windows.py
  setup_utils.py

ui/
  main_window.py
  sidebar.py
  setup_wizard.py
  actions.py
  theme.py

  tabs/
    configuration_tab.py        # thin container for the Configure tab
    configure/                  # one file per Configure subtab
      subtab_base.py            # SubtabBase contract (TITLE/ORDER/populate/on_save)
      local_machine_subtab.py
      company_subtab.py
      user_subtab.py
      environments_subtab.py
      preferences_subtab.py
      validation_subtab.py
    logs_tab.py
    project_tab.py
    variables_tab.py
    jobset_tab.py
    report_tab.py

  dialogs/
    local_tokens_dialog.py
    missing_tokens_dialog.py
    new_project_dialog.py
    about_dialog.py
    help_dialog.py
    kicad_cli_dialog.py
    add_user_dialog.py
    department_dialog.py
    clients_teams_dialog.py

  widgets/
    token_table.py
    path_field.py
    validation_panel.py
    log_viewer.py
    output_tree.py
    file_preview.py

help/
  index.md
  getting_started.md
  project_setup_tokens.md
  configure_tab.md
  project_page.md
  variables_jinja.md
  jobset.md
  report.md
  logs.md
  troubleshooting.md
  kicad_specgen_local.md
  project_kicad_specgen.md

tests/
  unit/
  integration/
  smoke/
  regression/
  fixtures/
```

Stage 1 creates the `core/`, `services/` (config_service, validation_service),
`setup/`, `ui/` shell, and `help/` (Stage 1 topics). Later stages add modules
as their features are implemented.

---

# Implementation Requirements

The application should be written as a clean, modular Python 3.10+ PySide6
application.

Implementation requirements:

```text
Use QMainWindow for the root window.
Use QMenuBar for File/Edit/View/Help menus.
Use QListWidget or QToolBar for sidebar navigation.
Use QTabWidget for the central workspace.
Use standard PySide6 widgets.
Use shared core utilities for config and validation.
Keep parsing and token logic out of UI widgets.
Use PEP 8 style.
Use type hints.
Use pathlib for paths.
Use dataclasses for structured state.
Use a QSS stylesheet parameterised from theme.py palette constants.
  See SpecGen_GUI_Theme.md for the complete theme specification,
  colour palettes, and QSS template guidance.
Include a __main__ block.
```

Responsibility separation:

```text
LocalTokensDialog and the Configure tab edit kicad_specgen_local.json (tokens).
The Configure tab (Environments subtab) edits kicad_specgen_company.json environments.
The Configure tab (Company and Users subtabs) edits kicad_specgen_company.json and
  kicad_specgen_users.json.
The Project and Variables pages edit the project .kicad_specgen file.
These responsibilities must not be mixed.
```

The GUI layer should not duplicate setup logic.

The setup scripts and GUI share utilities through `core/` and `services/`.

---

# Notes

The application shell should be functional in Stage 1, even though later workflow pages may be placeholders.

Placeholder pages should clearly state their implementation stage.

Example:

```text
Jobset page
  This page is implemented in Stage 2.
```

The project should remain usable for Stage 1 tasks:

```text
configure environment
open project config
validate tokens
edit variables
save project config
view logs
```
