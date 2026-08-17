# KiCad SpecGen Menu Bar and Help System Requirements
TODO - This is just for reference for some ideas on how to work out the GUI windows, pulldowns, and pop-ups.

## Purpose

This document defines the top menu bar contents for the KiCad SpecGen desktop application.

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

The menu bar should be implemented using standard PySide6 `QMenuBar`, `QMenu`, and `QAction` objects.

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

---

# File Menu

The File menu manages SpecGen project files and application session actions.

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

## `New SpecGen Project...`

Opens the New SpecGen Project dialog.

Purpose:

Copies the default {KSG_SPECGEN_DIR}/default.kicad_specgen to <KICAD_PROJECT_DIR>/specgen/<specgen_project_name>.kicad_specgen
Edits copyed <new_project_neam_string>.kicad_specgen environment section with user selection <environment>

Dialog behavior:

```text
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              New SpecGen Project Dialog                                 │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ Select KiCad Project Folder:                                                            │
│  [ Select ] KiCad project folder                                                        │<KICAD_PROJECT_DIR>
│ Select Named Environment:                                                               │
│  [ <input_text_string> ] Enter NEW named environment OR                                 │<environment> wins if there is a text value (string can not be just spaces)
│  [ ] Standalone                                                                         │
│  [ Select ] Git Repository                                                              │if <enviroment> is NEW then newopen folder picker dialog to select a repo otherwise gray out
│  [ Select ] Environment Common Folder (don't select for default)                        │if <enviroment> is NEW then newopen folder picker dialog to select a KSG_SPECGEN_COMMON otherwise gray out
│  [ <pull_down_list_from kicad_specgen.json> ] Select named environment                  │<environment> seed with "internal"
│ New SpecGen Project Name:                                                               │
│  [ <input_text_string> ] Enter New SpecGen Project Name (default support files)         │<specgen_project_name> will seed with <project_folder> name if blank
│ ─────────────────────────────────────────────────────────────────────────────────────── │
│ Selected:                                                                               │
│ Selected KiCad Project Folder       : <KICAD_PROJECT_DIR>                               │
│ Selected SpecGen Project Name       : <specten_project_name>                            │
│ Selected Named Environment          : <environment>                                     │
│ Selected SpecGen Project Type       : < "Standalone" | "Repo" >                         │
│ Selected Repo Folder                : <                                                 │
│ Selected SpecGen Common File Folder :                                                   │
│ ─────────────────────────────────────────────────────────────────────────────────────── │
│  [ Create ]                                                                    [Cancel] │if <enviroment> is NEW then newopen folder picker dialog 
└─────────────────────────────────────────────────────────────────────────────────────────┘
TODO finish

```

Rules:

* The new file must use the `.kicad_specgen` extension.
* The file must be saved under `<KICAD_PROJECT_DIR>/specgen/`.
* The new project should use tokenized paths.
* The new project should not store local-machine absolute path definitions.

---

## `Open SpecGen Project...`

Opens a file picker for an existing `.kicad_specgen` file.

Purpose:

Open an existing SpecGen project and replaces the project state.

Rules:

* The selected file must have extension `.kicad_specgen`.
* The selected file should live under a `specgen/` folder.
* Opening the file restores the full SpecGen project state.
* The application should derive `KICAD_SPECGEN_DIR` and `KICAD_PROJECT_DIR` from the opened file location.
* The application should update `kicad_specgen.json -> last_session`.

---

## `Open Recent`

Displays recently opened SpecGen project files.

```text
Open Recent
  Recent project list
  Clear recent projects
```
Recent project paths are local-machine state and should be stored in `kicad_specgen.json`.

---

## `Copy / Create From Existing Project...`

Opens a wizard for creating a new SpecGen project from an existing project file.

Purpose:

Convenience flow for copying an existing `.kicad_specgen` recipe into another KiCad project.

The wizard should (similar layout to New SpecGen Project):

```text
Select source .kicad_specgen
Select destination KiCad project folder
Select destination <specgen_project_name> (seed with copied project name if not the same folder location otherwise blank)
Ask to Copy or reference support files (local specgen/ or link to source)
Rebind project-local paths
Validate unresolved tokens
Save <specgen_project_name>.kicad_specgen under destination specgen/ use [Create] [Cancel] buttons
Add a note that jobset output will not be copied, User must generate from local project
```
Generated jobset outputs should not be copied. They should be regenerated by running the Jobset tab.

---

## `Save`

Saves the active project `.kicad_specgen` file.

Rules:

* Save full project state. (update <specgen_project_name>.kicad_specgen
* Update dirty state.
* Update status bar.

---

## `Save As...`

Opens a Save As dialog.

Purpose:

Save the current SpecGen project state to another `.kicad_specgen` file.

Rules:

* Destination must remain under `<KICAD_PROJECT_DIR>/specgen/`.
* File extension must be `.kicad_specgen`.
* If the destination exists, prompt:

```text
Overwrite
Rename
Cancel
```

---

## `Close Project`

Closes the active SpecGen project.

If unsaved changes exist, prompt:

```text
Save
Discard
Cancel
```

---

## `Exit`

Closes the application.

If unsaved changes exist, prompt:

```text
Save
Discard
Cancel
```
---

# Edit Menu

The Edit menu contains actions for editing environments, tokens, project metadata, and user-defined values.

```text
[Edit]
  Configure Environments...
  Resolve Missing Tokens...
  Configure kicad-cli...
  Edit Project Metadata...
  Edit Custom Variables...
  Validate Project
  ─────────────────────────
  Preferences...
```

---

## `Configure Environments...`

Opens the Configure Environments dialog.

Purpose:

Edit `kicad_specgen.json` named environments.

This dialog edits local-machine configuration, not the project report recipe.
  Adds a note to user that customer names are common for the environment

Editable items:

```text
active_environment
environment name
environment mode: repo / standalone
environment description
KSG_* token definitions
support file defaults
validation preferences
```

Rules:

* Stored token names must use the `KSG_*` namespace.
* Stored token values must be absolute paths.
* Protected derived tokens must not be stored in `kicad_specgen.json`.

Protected derived tokens:

```text
SPECGEN_PROJECT_FILE
KICAD_SPECGEN_DIR
KICAD_PROJECT_DIR
GIT_PROJECT_DIR
JOBSET_OUTPUT_DIR
FAB_OUTPUT_DIR
```

Recommended dialog layout:

```text
Configure Environments
  ├── Environment list
  ├── Environment editor
  │     ├── Name
  │     ├── Mode
  │     ├── Description
  │     ├── Token table
  │     ├── Defaults
  │     └── Validation
  └── Buttons
        Add Environment
        Remove Environment
        Add Token
        Remove Token
        Browse
        Validate
        Save
        Cancel
```

---

## `Resolve Missing Tokens...`

Opens the Missing Tokens dialog.

Purpose:

Resolve unresolved token references in the active project `.kicad_specgen`.

The dialog should show:

```text
missing token name
selected environment
where the token is used
affected project setting or file
suggested repair action
```

User choices:

```text
Add token to selected environment
Pick replacement file or folder
Skip affected item
Cancel
```

If the user adds a token, the application updates:

```text
kicad_specgen.json -> environments.<environment>.tokens.<TOKEN_NAME>
```

The project `.kicad_specgen` file should remain portable.

---

## `Configure kicad-cli...`

Opens a tool configuration dialog.

Purpose:

Set or validate the `kicad-cli` path.

The dialog should show:

```text
Current kicad-cli path
Detected source
KiCad version
Browse...
Check
Save
Cancel
```

On macOS, the application should check:

```text
/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
```

If found outside PATH, save the absolute path in `kicad_specgen.json`.

---

## `Edit Project Metadata...`

Switches to the Variables workspace or opens a metadata dialog.

Purpose:

Edit project-level metadata stored in the active project `.kicad_specgen`.

Examples:

```text
project display name
company
engineer
release name
document number
revision
date
copyright
```

---

## `Edit Custom Variables...`

Switches to the Variables workspace or opens a custom variables dialog.

Purpose:

Edit user-defined variables available to Jinja templates.

Variable names should follow:

```text
^[A-Z][A-Z0-9_]*$
```

---

## `Validate Project`

Runs project validation.

Validation should check:

```text
active project file
selected environment
effective token table
missing tokens
active .kicad_pro
active .kicad_jobset
support files
custom variables
project save location
```

Validation results should appear in:

```text
Project page validation panel
Status bar
Logs page
```

---

## `Preferences...`

Reserved for future application preferences.

Stage 1 may show a placeholder dialog.

Future preferences may include:

```text
theme
font size
default startup behavior
recent project count
log retention
default markdown help viewer size
```

---

# View Menu

The View menu controls workspace navigation, layout, and refresh behavior.

```text
[View]
  Project
  Variables
  Jobset
  Report
  Fabrication
  Logs
  ─────────────────────────
  Toggle Sidebar
  Toggle Status Bar
  Refresh
  ─────────────────────────
  Theme
```

---

## Workspace Navigation Actions

These menu actions switch the active sidebar/workspace page.

```text
Project
Variables
Jobset
Report
Fabrication
Logs
```

The sidebar should no longer include a separate JS Results item.

Reason:

The Jobset workspace owns its generated output review internally.

Recommended Jobset internal tabs:

```text
Dashboard
Setup & Run
Results
Output Log
```

This keeps the left sidebar focused on major workflow areas and keeps jobset execution and generated jobset results together.

---

## `Toggle Sidebar`

Shows or hides the left navigation rail.

---

## `Toggle Status Bar`

Shows or hides the bottom status bar.

---

## `Refresh`

Reloads safe project-visible information from disk.

Refresh may update:

```text
effective token table
raw kicad_common.json environment table
jobset file status
generated output file list
validation status
logs
```

Refresh must not discard unsaved project changes without confirmation.

---

## `Theme`

Theme submenu.

```text
Theme
  System
  Light
  Dark
  Engineering Dark
```

Stage 1 should include at least one clean QSS theme.

---

# Help Menu

The Help menu displays Markdown-based help files and diagnostic dialogs.

```text
[Help]
  KiCad SpecGen Help
  Getting Started
  Project Setup and Tokens
  Configure Environments
  Project Page Help
  Variables and Jinja Templates
  Jobset Help
  Report Help
  Fabrication Help
  Logs Help
  Troubleshooting
  ─────────────────────────
  Show kicad_specgen.json Location
  Show kicad_common.json Location
  Check kicad-cli
  Open Logs Folder
  ─────────────────────────
  About KiCad SpecGen
```

---

# Help System Requirements

Help content should be written in Markdown.

The application should display help content in a modal dialog with:

```text
Help title
Rendered Markdown content area
OK button
```

Recommended dialog:

```text
HelpDialog
  ├── Title
  ├── Scrollable Markdown viewer
  └── OK
```

The Markdown viewer should support:

```text
headings
paragraphs
bullet lists
numbered lists
tables
fenced code blocks
inline code
horizontal rules
links
```

The dialog should close when the user presses:

```text
OK
```

Implementation options:

```text
QTextBrowser
QTextEdit in read-only mode
QWebEngineView if later needed
```

Recommended Stage 1 implementation:

```text
QTextBrowser
```

The help renderer should load Markdown from files stored in the SpecGen help documentation folder.

Recommended help folder:

```text
help/
  index.md
  getting_started.md
  project_setup_tokens.md
  configure_environments.md
  project_page.md
  variables_jinja.md
  jobset.md
  report.md
  fabrication.md
  logs.md
  troubleshooting.md
  kicad_specgen_json.md
  project_kicad_specgen.md
```

---

# Required Help Files

## `index.md`

Main help index.

Should include:

```text
what KiCad SpecGen does
workflow overview
stage overview
links to major help topics
```

---

## `getting_started.md`

First-run user guide.

Should include:

```text
run setup.py
find kicad-cli
create or open a SpecGen project
choose an environment
validate project
save project
```

---

## `project_setup_tokens.md`

Explains tokens and paths.

Should include:

```text
KSG_* stored tokens
protected derived tokens
kicad_specgen.json
kicad_common.json
effective token table
missing token repair
repo vs standalone mode
```

---

## `configure_environments.md`

Explains the Configure Environments dialog.

Should include:

```text
environment list
repo mode
standalone mode
adding tokens
removing tokens
validating paths
saving kicad_specgen.json
```

---

## `project_page.md`

Explains the Project workspace.

Should include:

```text
active .kicad_specgen file
selected environment
KiCad project paths
effective token table
support files
validation panel
```

---

## `variables_jinja.md`

Explains variables and Jinja template insertion.

Should include:

```text
Jinja variable syntax
loops
conditionals
Markdown templates
HTML templates
CSV templates
engineering examples
available SpecGen variables
custom variable naming rules
```

The uploaded Jinja help file is a good starting point for this topic.

---

## `jobset.md`

Explains the Jobset workspace.

Should include:

```text
Dashboard tab
Setup & Run tab
Results tab
Output Log tab
selecting a .kicad_jobset
destination IDs
run all
run selected
stop on error
generated output files
how results feed the Report and Fabrication pages
```

---

## `report.md`

Explains the Report workspace.

Should include:

```text
report recipe
file order
generated pages
template variables
supported input types
preview behavior
build report
dry run
```

---

## `fabrication.md`

Explains the Fabrication workspace.

Should include:

```text
FAB output folder
Gerber files
drill files
BOM files
position files
STEP files
README manifest
checksums
zip output
dry run
```

---

## `logs.md`

Explains the Logs workspace.

Should include:

```text
application logs
validation messages
jobset run output
report build output
fabrication output
log levels
```

---

## `troubleshooting.md`

Common problems and fixes.

Should include:

```text
kicad-cli not found
kicad_common.json not found
missing KSG_* token
invalid project .kicad_specgen location
jobset output missing
report file missing
template variable undefined
permission errors
```

---

## `kicad_specgen_json.md`

Reference help for the local machine JSON file.

Should include:

```text
schema
tools
setup
last_session
environments
tokens
validation
examples
```

---

## `project_kicad_specgen.md`

Reference help for the project `.kicad_specgen` TOML file.

Should include:

```text
schema
workspace
project metadata
variables
jobset state
report recipe
fabrication recipe
tokenized paths
validation rules
```

---

# Help Menu Dialog Behavior

Each Help menu action should open a Markdown help dialog.

Example:

```text
Help -> Variables and Jinja Templates
  opens help/variables_jinja.md
```

Dialog requirements:

```text
modal dialog
resizable
scrollable content
render Markdown headings
render Markdown tables
render fenced code examples
OK button closes the dialog
```

Recommended minimum size:

```text
900 x 650
```

The help dialog should show a clear error if the Markdown file is missing.

Example error:

```text
Help file not found:
help/variables_jinja.md
```

---

# Menu-to-Dialog Mapping

```text
File -> New SpecGen Project...
  NewProjectDialog

File -> Open SpecGen Project...
  QFileDialog

File -> Save As...
  QFileDialog + overwrite confirmation

Edit -> Configure Environments...
  ConfigureEnvironmentsDialog

Edit -> Resolve Missing Tokens...
  MissingTokensDialog

Edit -> Configure kicad-cli...
  ToolPathDialog

Edit -> Validate Project
  ValidationPanel update + status dialog if needed

Help -> Variables and Jinja Templates
  HelpDialog(help/variables_jinja.md)

Help -> Jobset Help
  HelpDialog(help/jobset.md)

Help -> Show kicad_specgen.json Location
  MessageBox with path + Open Folder button

Help -> Check kicad-cli
  Runs configured kicad-cli version and displays result

Help -> About KiCad SpecGen
  AboutDialog
```

---

# Project Requirement Addition

The application shall include a Markdown-based help system.

Requirement:

```text
REQ-HELP-001
  The application shall store user help files as Markdown documents.

REQ-HELP-002
  The application shall display help files in a modal Help dialog.

REQ-HELP-003
  The Help dialog shall render Markdown headings, paragraphs, lists,
  tables, inline code, and fenced code blocks.

REQ-HELP-004
  The Help dialog shall include an OK button that closes the dialog.

REQ-HELP-005
  The Help menu shall provide topic-specific help entries for Project,
  Variables/Jinja, Jobset, Report, Fabrication, Logs, setup/tokens,
  troubleshooting, and configuration file references.

REQ-HELP-006
  If a help file is missing, the application shall show a user-readable
  error message and shall not crash.
```

---

# Stage Placement

The basic Help menu and Markdown Help dialog belong in Stage 1.

Stage 1 should implement:

```text
Help menu
HelpDialog
Markdown rendering
OK button close behavior
variables_jinja.md help file
getting_started.md placeholder
project_setup_tokens.md placeholder
jobset.md placeholder
```

Later stages should complete topic help as each feature is implemented.

Recommended rule:

```text
A feature is not complete until its Help topic is added or updated.
```

