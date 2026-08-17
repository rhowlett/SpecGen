# KiCad SpecGen Application Reference

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
Configure Environments Dialog
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

The application is installed from a Git repository and runs in its own `.venv/` inside the SpecGen application repository.

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
Project
Variables
Logs
Configure Environments
Missing Token Resolution
```

Later stages implement:

```text
Jobset
JS Results
Report
Fabrication
Developer tools
Full packaging
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
KSG_DIR
KSG_WORKSPACE
KSG_SPECGEN_DIR
KSG_SPECGEN_COMMON
```

## Standalone mode

Standalone mode is used when the KiCad project is an independent folder and is not part of a shared Git workspace.

Standalone environments do not require:

```text
KSG_DIR
KSG_WORKSPACE
```

Standalone environments must still define:

```text
KSG_SPECGEN_DIR
KSG_SPECGEN_COMMON
```

---

# Configuration Files

KiCad SpecGen uses two primary configuration files.

## `kicad_specgen.json`

`kicad_specgen.json` is the local-machine SpecGen configuration file.

It stores:

```text
named environments
absolute token definitions
kicad-cli path
setup status
last opened SpecGen project
local support file paths
```

This file may contain absolute paths because it belongs to the local user and machine.

It is stored in the KiCad user configuration area near `kicad_common.json`.

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
tab state needed for reproducibility
```

The project `.kicad_specgen` file must live in the KiCad project-local `specgen/` folder:

```text
<KICAD_PROJECT_DIR>/specgen/<name>.kicad_specgen
```

The project `.kicad_specgen` file should store token references, not local machine absolute path definitions.

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
KSG_DIR
KSG_WORKSPACE
KSG_SPECGEN_DIR
KSG_SPECGEN_COMMON
KSG_CLIENT_DOCS
KSG_CLIENT_ASSETS
```

Project-derived runtime tokens do not use the `KSG_*` prefix.

Protected derived tokens:

```text
SPECGEN_PROJECT_FILE
KICAD_SPECGEN_DIR
KICAD_PROJECT_DIR
GIT_PROJECT_DIR
JOBSET_OUTPUT_DIR
FAB_OUTPUT_DIR
```

## Resolution order

When resolving a token reference, SpecGen builds an effective token table.

Resolution order:

```text
1. KiCad environment variables from kicad_common.json
2. selected named environment tokens from kicad_specgen.json
3. protected derived runtime tokens
```

Later sources override earlier sources.

Therefore:

```text
kicad_specgen.json environment tokens override kicad_common.json tokens.
protected derived runtime tokens override both.
```

This guarantees that project-local paths such as `KICAD_PROJECT_DIR` always come from the opened `.kicad_specgen` file location.

---

# Application Startup

The application startup flow restores the last project when possible.

Usage:

```text
Start KiCad SpecGen
  Read platform paths
  Locate kicad_specgen.json
  Load kicad_specgen.json
  Locate kicad-cli
  Load last_session.specgen_project if available
  Validate selected environment
  Resolve effective token table
  Open main window
```

If no previous session exists, the user is prompted to create or open a SpecGen project.

If setup has not completed, the application should prompt the user to run setup or continue with limited functionality.

---

# Setup Bootstrap

Setup is part of Stage 1.

The setup entry point is:

```text
setup.py
```

Usage:

```text
python setup.py [--stage STAGE] [--full] [--no-prompt]
```

The top-level setup script detects the operating system and dispatches to one of:

```text
setup_ubuntu.py
setup_macos.py
setup_windows.py
```

Setup responsibilities:

```text
create or update .venv/
install selected dependency stage
locate kicad-cli
locate kicad_common.json
create or update kicad_specgen.json
create named environments
copy default SpecGen support files if missing
validate required KSG_* tokens
write setup logs
```

On macOS, setup should check:

```text
/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
```

If `kicad-cli` is not found in the shell path but is found in the KiCad application bundle, setup should save the absolute path in `kicad_specgen.json`.

Creating a symlink is optional and should not be the default behavior.

If setup modifies `kicad_common.json`, it must create a timestamped backup first:

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
* open a dialog
* switch the active workspace view
* validate configuration
* display help content
* display application or diagnostic information

---

# Top Menu Bar Overview

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ [File]   [Edit]   [View]   [Help]                                            │
└──────────────────────────────────────────────────────────────────────────────┘
```

The menu bar spans the full width of the application window.

Recommended behavior:

```text
File
  Project/session file operations

Edit
  Configuration, tokens, variables, and settings

View
  Workspace navigation, refresh, layout, and visibility controls

Help
  Markdown-based documentation, diagnostics, and about dialogs
```

s or trigger clearly defined application commands.

---

## File menu

The File menu contains project file commands.

Usage:

```text
File
  New SpecGen Project...
  Open SpecGen Project...
  Open Recent
  Save
  Save As...
  Close Project
  Exit
```

[File] Submenu selection are defined in detail in SpecGen_Pulldown_Menu_File.md
TODO - Remove the submenus they are defined in the markdown
     - ask for the standard tokens to be defined in a table.

The user selects:

```text
environment
default file behavior
initial project filename
```

Default file behavior options:

```text
Use defaults by reference
Copy defaults into project specgen folder
Skip defaults and leave blank entries
```

### `Open SpecGen Project...`

Opens an existing `.kicad_specgen` file.

The selected file must be located under:

```text
<KICAD_PROJECT_DIR>/specgen/
```

Opening the file restores the SpecGen project state.

### `Open Recent`

Shows recent SpecGen project files.

Stage 1 may only show the last opened project from:

```text
kicad_specgen.json -> last_session.specgen_project
```

### `Save`

Saves the current project `.kicad_specgen` file.

### `Save As...`

Saves the current SpecGen project state to another `.kicad_specgen` file.

The destination must remain under:

```text
<KICAD_PROJECT_DIR>/specgen/
```

### `Close Project`

Closes the current project after prompting for unsaved changes.

### `Exit`

Exits the application.

If there are unsaved changes, prompt:

```text
Save
Discard
Cancel
```

---

## Edit menu

The Edit menu contains configuration and project-edit commands.

Usage:

```text
Edit
  Configure Environments...
  Resolve Missing Tokens...
  Edit Project Metadata...
  Edit Custom Variables...
  Preferences...
```

### `Configure Environments...`

Opens the Configure Environments dialog.

This dialog edits:

```text
kicad_specgen.json
```

It does not edit the project `.kicad_specgen` report recipe.

### `Resolve Missing Tokens...`

Opens the Missing Tokens dialog.

This dialog appears when the project references tokens not available in the effective token table.

### `Edit Project Metadata...`

Focuses the Variables page or opens a metadata edit dialog.

Project metadata is saved in the project `.kicad_specgen` file.

### `Edit Custom Variables...`

Focuses the Variables page or opens a custom-variable edit dialog.

Custom variables are saved in the project `.kicad_specgen` file.

### `Preferences...`

Reserved for future application preferences.

Stage 1 may provide a placeholder dialog.

---

## View menu

The View menu controls visible application pages and layout options.

Usage:

```text
View
  Project
  Variables
  Jobset
  JS Results
  Report
  Fabrication
  Logs
  Toggle Sidebar
  Toggle Status Bar
  Refresh
  Theme
```

Stage 1 implements:

```text
Project
Variables
Logs
```

Other pages may appear as disabled or placeholder pages until their implementation stage.

### `Refresh`

Reloads project-visible state from disk where safe.

Refresh should not discard unsaved project changes without confirmation.

---

## Help menu

The Help menu contains documentation and diagnostic commands.

Usage:

```text
Help
  About KiCad SpecGen
  Open Documentation
  Show kicad_specgen.json Location
  Show kicad_common.json Location
  Check kicad-cli
  View Logs Folder
```

### `About KiCad SpecGen`

Shows application version and basic environment information.

### `Show kicad_specgen.json Location`

Displays the resolved path to `kicad_specgen.json`.

### `Show kicad_common.json Location`

Displays the resolved path to `kicad_common.json`.

### `Check kicad-cli`

Runs a basic check using the configured `kicad-cli` path.

Stage 1 may run:

```text
kicad-cli version
```

and display the result.

---

# Sidebar Navigation

The sidebar navigation rail is shown on the left side of the main window.

Recommended implementation:

```text
QListWidget
```

or:

```text
QToolBar with checkable actions
```

Stage 1 should prefer `QListWidget` for simplicity.

Sidebar entries:

```text
Project
Variables
Jobset
JS Results
Report
Fabrication
Logs
```

Each entry selects the corresponding page in the central `QTabWidget`.

Stage 1 implemented pages:

```text
Project
Variables
Logs
```

Stage 1 placeholder pages:

```text
Jobset
JS Results
Report
Fabrication
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
ResultsTab
ReportTab
FabricationTab
LogsTab
```

Pages should read from application state.

Pages should emit intentional user actions.

Pages should not parse files directly.

Parsing, validation, token resolution, and file operations belong in shared core modules.

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
KICAD_SPECGEN_DIR
GIT_PROJECT_DIR
active .kicad_pro file
active .kicad_jobset file
KSG_SPECGEN_DIR
KSG_SPECGEN_COMMON
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
Configure Environment...
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

# Configure Environments Dialog

The Configure Environments dialog edits `kicad_specgen.json`.

It does not edit the project `.kicad_specgen` report recipe.

Usage:

```text
Edit -> Configure Environments...
```

The dialog should allow the user to:

```text
select active environment
add environment
rename environment
remove environment
set environment mode
edit environment description
add token
remove token
edit token path
browse for token path
validate environment
save changes
cancel changes
```

Recommended layout:

```text
Configure Environments
  Environment list
  Environment editor
    Name
    Mode
    Description
    Token table
    Defaults
    Validation options
  Buttons
    Add Environment
    Remove Environment
    Add Token
    Remove Token
    Browse
    Validate
    Save
    Cancel
```

Token table columns:

```text
Token
Path
Status
Notes
```

Stored token names must follow:

```text
^KSG_[A-Z0-9_]+$
```

Stored token values must be absolute paths.

The dialog must reject or warn if the user tries to define a protected derived token.

Protected derived tokens:

```text
SPECGEN_PROJECT_FILE
KICAD_SPECGEN_DIR
KICAD_PROJECT_DIR
GIT_PROJECT_DIR
JOBSET_OUTPUT_DIR
FAB_OUTPUT_DIR
```

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
Add token to selected environment
Pick replacement file or folder
Skip affected item
Cancel open
```

If the user adds a token, SpecGen updates:

```text
kicad_specgen.json -> environments.<environment>.tokens.<TOKEN_NAME>
```

The project `.kicad_specgen` file should remain portable and should not be rewritten with an absolute path.

---

# Project File Commands

SpecGen project commands operate on `.kicad_specgen` files.

## New project command

Usage:

```text
New SpecGen Project
  Select KICAD_PROJECT_DIR
  Create KICAD_SPECGEN_DIR if missing
  Select environment
  Select defaults behavior
  Create <name>.kicad_specgen
```

The config file must be saved under:

```text
<KICAD_PROJECT_DIR>/specgen/
```

## Open project command

Usage:

```text
Open SpecGen Project
  Select <name>.kicad_specgen
  Validate location
  Derive KICAD_SPECGEN_DIR
  Derive KICAD_PROJECT_DIR
  Discover active .kicad_pro
  Load selected environment
  Resolve tokens
  Populate Project page
```

## Save command

Usage:

```text
Save
  Validate dirty state
  Save current project .kicad_specgen
  Update last_session in kicad_specgen.json
```

## Save As command

Usage:

```text
Save As
  Select output filename
  Require output under KICAD_SPECGEN_DIR
  Save project .kicad_specgen
  Update last_session in kicad_specgen.json
```

---

# Stage 1 Scope

Stage 1 implements the foundation of the application.

Required Stage 1 deliverables:

```text
setup bootstrap
shared core utilities
QMainWindow shell
menu bar
sidebar navigation
central QTabWidget workspace
Project page
Variables page
Logs page
Configure Environments dialog
Missing Tokens dialog
kicad_specgen.json load/save
project .kicad_specgen load/save
token resolver
effective token table
validation framework
basic QSS theme
```

Stage 1 does not implement:

```text
jobset execution
JS Results file preview
report generation
fabrication packaging
full recipe import/export
```

---

# Future Application Stages

## Stage 2: Jobset and Results

Stage 2 implements:

```text
Jobset page
JS Results page
.kicad_jobset parsing
jobset destination display
jobset destination ID handling
safe kicad-cli jobset run
generated output scanning
basic generated file status
```

## Report stage

The Report stage implements:

```text
report recipe editing
report block model
Markdown/HTML/TXT/CSV/image/PDF input handling
PyMuPDF + pypdf rendering pipeline
final report output
dry-run validation
```

## Fabrication stage

The Fabrication stage implements:

```text
FAB output mapping
Gerber zip creation
BOM conversion
STEP and position file inclusion
README generation
checksums
dry-run validation
```

## Developer stage

The Developer stage implements:

```text
unit tests
fixtures
linting
type checks
test project fixtures
developer documentation
```

## Full stage

The Full stage installs all dependencies and enables the complete application.

---

# Validation

Validation should produce clear user-facing messages.

Validation should not show raw stack traces for normal user errors.

Stage 1 validation should check:

```text
kicad_specgen.json exists or can be created
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

Recommended Stage 1 module layout:

```text
main.py
app.py

core/
  app_state.py
  platform_paths.py
  logging_utils.py
  file_ops.py
  kicad_env.py
  specgen_json.py
  project_config.py
  token_resolver.py
  validators.py

setup/
  setup_ubuntu.py
  setup_macos.py
  setup_windows.py

ui/
  main_window.py
  actions.py
  theme.py
  sidebar.py

  dialogs/
    configure_environment_dialog.py
    missing_tokens_dialog.py
    new_project_dialog.py
    about_dialog.py

  widgets/
    token_table.py
    path_field.py
    validation_panel.py
    readonly_table.py
    log_viewer.py

  tabs/
    project_tab.py
    variables_tab.py
    jobset_tab.py
    results_tab.py
    report_tab.py
    fabrication_tab.py
    logs_tab.py
```

---

# Implementation Requirements

The application should be written as a clean, modular Python 3.10+ PySide6 application.

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
Use a basic QSS stylesheet.
Include a __main__ block.
```

The GUI layer should not duplicate setup logic.

The setup scripts and GUI should share utilities where practical.

The Configure Environments dialog edits `kicad_specgen.json`.

The Project and Variables pages edit the project `.kicad_specgen` file.

These responsibilities should not be mixed.

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
