# KiCad SpecGen — GUI Menus Specification

> **Document role:** Primary specification for the top menu bar, menu item
> behavior, dialog mappings, help system requirements, and required help file
> topics.
> **Authority:** `SpecGen_Terminology.md`, `SpecGen_Tab_Configure.md`.
> **Companion documents:** `SpecGen_Tab_Jobset.md`, `SpecGen_Tab_Report.md`,
> `SpecGen_Stage_Plan.md`, `SpecGen_Setup_Process.md`.
> **Status:** Updated — ready for Stage 1 implementation.

---

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

Creates a new `.kicad_specgen` project file under `{KICAD_PROJECT_DIR}/specgen/`
by copying the default template from `{KSG_APP_DIR}/default.kicad_specgen` and
setting the selected environment in the project workspace section.

Environments are defined in `kicad_specgen_company.json`. They are selected here,
not created here. Environment creation and management belongs in the Configure tab.

Dialog behavior:

```text
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              New SpecGen Project                                        │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  KiCad Project Folder                                                                   │
│  ┌──────────────────────────────────────────────────────────────┐  [ Browse... ]       │
│  │ (no folder selected)                                         │                      │
│  └──────────────────────────────────────────────────────────────┘                      │
│  Resolved: (none)                                                                       │
│                                                                                         │
│  SpecGen Project Name                                                                   │
│  ┌──────────────────────────────────────────────────────────────┐                      │
│  │ (auto-filled from KiCad project folder name)                 │                      │
│  └──────────────────────────────────────────────────────────────┘                      │
│  Will create: {KICAD_PROJECT_DIR}/specgen/<name>.kicad_specgen                         │
│                                                                                         │
│  Environment                                                                            │
│  ┌──────────────────────────────────────────────────────────────┐                      │
│  │ (select from list)                                     ▼     │                      │
│  └──────────────────────────────────────────────────────────────┘                      │
│  Populated from kicad_specgen_company.json → environments                              │
│  To add environments, use the Configure tab → Environments subtab.                     │
│                                                                                         │
│  ── Summary ─────────────────────────────────────────────────────────────────────────  │
│  KiCad Project Folder  : (none)                                                        │
│  SpecGen Project Name  : (none)                                                        │
│  Environment           : (none)                                                        │
│  Project file          : (none)                                                        │
│                                                                                         │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                              [ Create ]   [ Cancel ]    │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

Field behavior:

- **KiCad Project Folder** — Browse to any folder containing a `.kicad_pro` file.
  The picker filters for folders, not files. After selection, SpecGen scans for
  `.kicad_pro` files and shows the resolved path.

- **SpecGen Project Name** — Auto-filled with the KiCad project folder name. The
  user may override. Must not be blank or spaces only. Must produce a valid filename.

- **Environment** — Dropdown populated from `kicad_specgen_company.json → environments`.
  Seeded with the `active_environment` from `kicad_specgen_local.json`. If no
  environments are defined, the dropdown shows a warning and the `[ Create ]`
  button is disabled until the user configures one.

- **[ Create ]** — Enabled only when all three fields are valid. Creates the
  `specgen/` subfolder if it does not exist, copies the default template, sets
  the environment, saves the file, and opens the project.

- **[ Cancel ]** — Closes the dialog with no changes.

Rules:

- The new file must use the `.kicad_specgen` extension.
- The file must be saved under `{KICAD_PROJECT_DIR}/specgen/`.
- The new project must use tokenized paths.
- The new project must not store local-machine absolute path definitions.
- Environments are never created inline in this dialog.
- If `specgen/<name>.kicad_specgen` already exists, prompt: Overwrite / Rename / Cancel.
- If no `.kicad_pro` file is found in the selected folder, show a non-blocking warning
  in the dialog. The user may proceed — KiCad may not have been run in that folder yet.
- `{KICAD_PROJECT_DIR}` in the "Will create" preview is derived from the selected
  KiCad Project Folder, not from a pre-existing runtime token. The runtime token
  `KICAD_PROJECT_DIR` is set after the project is opened.

Stage: **Stage 2** — requires the project open/save infrastructure from Stage 2.
The dialog module `new_project_dialog.py` is created as a stub in Stage 1
but is not functional until Stage 2.

---

## `Open SpecGen Project...`

Opens a file picker for an existing `.kicad_specgen` file.

Purpose:

Open an existing SpecGen project and replaces the project state.

Rules:

- The selected file must have extension `.kicad_specgen`.
- The selected file should live under a `specgen/` folder. If it does not, show a
  non-blocking warning — the file is still opened.
- If a project is already open with unsaved changes, prompt Save / Discard / Cancel
  before opening the new project.
- Opening the file restores the full SpecGen project state.
- The application derives `KSG_PROJECT_SPECGEN_DIR` and `KICAD_PROJECT_DIR` from
  the opened file location.
- After loading, token resolution runs automatically. If any token references cannot
  be resolved, the Missing Tokens dialog opens immediately.
- The application updates `kicad_specgen_local.json → last_session` and
  `kicad_specgen_local.json → recent_projects` after a successful open.

Stage: **Stage 2**

---

## `Open Recent`

Displays recently opened SpecGen project files as a submenu.

```text
┌───────────────────────────────────────┐
│ Open Recent                           │
├───────────────────────────────────────┤
│ /path/to/ProjectA/specgen/A.kicad_... │
│ /path/to/ProjectB/specgen/B.kicad_... │
│ ⚠ /missing/path/C.kicad_specgen      │
│ ───────────────────────────────────── │
│ Clear Recent Projects                 │
└───────────────────────────────────────┘
```

Rules:

- Recent project paths are stored in `kicad_specgen_local.json → recent_projects`.
- Maximum of 10 recent entries. When a new project is opened, the oldest entry is
  removed if the list exceeds 10 items.
- If a recent project path no longer exists on disk, the entry is shown greyed out
  with a ⚠ prefix. Selecting a missing entry shows a warning MessageBox and does
  not attempt to open the file.
- If a project is already open with unsaved changes, prompt Save / Discard / Cancel
  before switching projects.
- `Clear Recent Projects` clears `kicad_specgen_local.json → recent_projects` array
  after a confirmation prompt: "Clear recent projects list? This cannot be undone.
  [ Clear ] [ Cancel ]"
- The current open project (if any) is not removed from the list when it is closed —
  it stays at the top of the recent list.

Stage: **Stage 2**

---

## `Copy / Create From Existing Project...`

Opens a wizard for creating a new SpecGen project from an existing project file.

Purpose:

Convenience flow for copying an existing `.kicad_specgen` recipe into a new KiCad
project, with the option to link or copy support files depending on where they live.

Stage: **Future (post-Stage 2)** — requires a dedicated specification document
(`SpecGen_GUI_Dialogs.md`) before implementation. The menu item exists in Stage 2
but shows a "Coming soon" placeholder dialog.

### Wizard steps

```text
Step 1.  Select source .kicad_specgen file
Step 2.  Select destination KiCad project folder
Step 3.  Set destination SpecGen project name
         (auto-filled from source project name if different folder, blank if same)
Step 4.  Review and resolve support file references (see Link Eligibility below)
Step 5.  Validate token resolution for the new project
Step 6.  Confirm and create
```

### Link eligibility check (Step 4)

Each support file reference in the source `.kicad_specgen` is checked individually:

```text
Case A — Source path is within a tokenized root
  (e.g. {KSG_COMPANY_DIR}/..., {KSG_USER_COMMON_DIR}/..., {KSG_APP_DIR}/...)
  → The reference is already portable and will resolve correctly in the new project.
  → Default: Link (keep the token reference as-is). No copy needed.
  → User may still choose to copy if they want a local override.

Case B — Source path is under the source project's KSG_PROJECT_SPECGEN_DIR
  and the destination project shares the same KICAD_PROJECT_DIR
  → The reference will still resolve correctly because both projects are in the
     same KiCad project folder.
  → Default: Link. User may choose to copy.

Case C — Source path is under the source project's KSG_PROJECT_SPECGEN_DIR
  and the destination is a different KICAD_PROJECT_DIR
  → The reference would point to the wrong project's specgen/ folder.
  → Copy is required. Link is disabled for this file. A copy is made to
     the destination specgen/ folder.

Case D — Source path contains an absolute path with no token root
  → The reference is not portable and cannot be safely linked.
  → Copy is required. Link is disabled. User is warned that the copied file
     should be moved to a tokenized location after creation.
```

The Step 4 UI presents a table of all support file references with their case
classification and Copy / Link choice for eligible files.

### Rules

- Generated jobset outputs are never copied. They are regenerated by running the
  Jobset tab in the new project.
- The destination `.kicad_specgen` must be under `{KICAD_PROJECT_DIR}/specgen/`.
- The new project must use tokenized paths. Any copied absolute paths trigger a
  post-create warning with guidance to tokenize them.
- Token resolution is validated in Step 5 before [ Create ] is enabled.
- If validation finds unresolved tokens, the user must resolve them before
  proceeding (redirects to Missing Tokens behavior).

---

## `Save`

Saves the active project `.kicad_specgen` file.

Rules:

- Disabled when no project is open.
- Disabled when the dirty flag is false (no unsaved changes).
- Writes the full project state to `{SPECGEN_PROJECT_FILE}`.
- Before writing, validates that no absolute paths are present in the file.
  If absolute paths are found, shows a non-blocking warning: "Unsaved project
  contains absolute paths that may not be portable. Save anyway? [ Save ] [ Review ]"
- Clears the dirty flag after a successful save.
- Updates the status bar to confirm the save.

Stage: **Stage 2**

---

## `Save As...`

Opens a Save As dialog.

Purpose:

Save the current SpecGen project state to a new `.kicad_specgen` file.

Rules:

- Disabled when no project is open.
- File picker opens in `{KSG_PROJECT_SPECGEN_DIR}` (the current project's `specgen/`
  folder) as the default directory.
- File extension must be `.kicad_specgen`.
- If the user navigates outside `{KICAD_PROJECT_DIR}/specgen/`, show a non-blocking
  warning: "The selected location is outside the expected specgen/ folder. SpecGen
  projects should live under the KiCad project's specgen/ subfolder." The user may
  proceed regardless.
- If the destination file already exists, prompt:

```text
┌──────────────────────────────────────────────┐
│  File already exists                         │
├──────────────────────────────────────────────┤
│  <name>.kicad_specgen already exists.        │
│  What would you like to do?                  │
│                                              │
│  [ Overwrite ]  [ Rename... ]  [ Cancel ]    │
└──────────────────────────────────────────────┘
```

- After a successful Save As, the newly saved file becomes the active project file
  (`{SPECGEN_PROJECT_FILE}` is updated).

Stage: **Stage 2**

---

## `Close Project`

Closes the active SpecGen project.

If unsaved changes exist, prompt:

```text
┌──────────────────────────────────────────────┐
│  Unsaved Changes                             │
├──────────────────────────────────────────────┤
│  The project has unsaved changes.            │
│                                              │
│  [ Save ]   [ Discard ]   [ Cancel ]         │
└──────────────────────────────────────────────┘
```

After close:

- All project-domain tabs show placeholder content ("No project open").
- The following menu items are disabled until a project is opened:
  Save, Save As, Close Project, Edit Project Metadata, Edit Custom Variables,
  Validate Project, Resolve Missing Tokens.
- The status bar clears the project name and environment fields.

Stage: **Stage 2**

---

## `Exit`

Closes the application.

If unsaved changes exist, prompt:

```text
┌──────────────────────────────────────────────┐
│  Unsaved Changes                             │
├──────────────────────────────────────────────┤
│  The project has unsaved changes.            │
│                                              │
│  [ Save ]   [ Discard ]   [ Cancel ]         │
└──────────────────────────────────────────────┘
```

Before the application closes (regardless of project save outcome):

- `main_window.closeEvent()` calls `config_service.save_session(geometry, project_ref)`,
  which writes `kicad_specgen_local.json → last_session` with:
  `specgen_project`, `project_name`, `display_name`, `kicad_project_dir`,
  `window_geometry`, `last_opened_at`.
  Per-project state (`active_tab`, `workspace.environment`) is already in
  the `.kicad_specgen` file and is not duplicated here.
  This write always occurs, even when the project itself is not saved.

Stage: **Stage 1**

# Edit Menu

The Edit menu contains actions for editing tokens, project metadata, and user-defined values.

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

---

## `Local Tokens...`

Opens the Local Tokens dialog.

Purpose:

Edit `KSG_*` token definitions stored in `kicad_specgen_local.json → tokens`.
This dialog is scoped strictly to local machine token editing. It does not edit
environment definitions, company data, or user profiles. Those belong in the
Configure tab.

Editable items:

```text
KSG_* token name
KSG_* token value (absolute path)
```

Rules:

- Token names must match `^KSG_[A-Z0-9_]+$`.
- Token values must be absolute paths.
- Protected derived runtime tokens must not be added here.
- The five required tokens (`KSG_APP_DIR`, `KSG_SYSTEM_CONFIG_DIR`,
  `KSG_COMPANY_DIR`, `KSG_USER_SPECGEN_DIR`, `KSG_USER_COMMON_DIR`) cannot be
  removed. `[ Remove Selected ]` is disabled when any of these is selected.
- `[ Save ]` validates all token values are absolute paths before writing.
  Non-absolute values block the save with an inline error message per offending row.
- After a successful save, the application reloads the effective token table and
  refreshes the Project tab validation panel (if a project is open).

Stage: **Stage 1**

Protected derived runtime tokens (rejected if entered):

```text
SPECGEN_PROJECT_FILE
KSG_PROJECT_SPECGEN_DIR
KICAD_PROJECT_DIR
GIT_PROJECT_DIR
JOBSET_OUTPUT_DIR
FAB_OUTPUT_DIR
```

Dialog layout:

```text
┌─────────────────────────────────────────────────────────────────┐
│  Local Tokens                                                   │
├──────────────────────────────────────┬──────────────────────────┤
│ Token                                │ Value              Status│
├──────────────────────────────────────┼──────────────────────────┤
│ KSG_APP_DIR                          │ /Users/...            ✓  │
│ KSG_SYSTEM_CONFIG_DIR                │ ~/Library/...         ✓  │
│ KSG_COMPANY_DIR                      │ /Users/...            ✓  │
│ KSG_USER_SPECGEN_DIR                 │ /Users/...            ✓  │
│ KSG_USER_COMMON_DIR                  │ /Users/...            ✓  │
├──────────────────────────────────────┴──────────────────────────┤
│  [ Add Token ]  [ Remove Selected ]  [ Browse... ]  [ Edit ]   │
├─────────────────────────────────────────────────────────────────┤
│                              [ Save ]             [ Cancel ]    │
└─────────────────────────────────────────────────────────────────┘
```

Note: For full environment, company, and user configuration, use the
Configure tab (`[Configure]` in the sidebar).

---

## `Resolve Missing Tokens...`

Opens the Missing Tokens dialog.

Purpose:

Resolve unresolved token references in the active project `.kicad_specgen`.

This dialog is also triggered automatically after `Open SpecGen Project...`
and `Open Recent` when token resolution fails. The manual menu item is provided
for re-running resolution after the user has added tokens via the Configure tab
or `Local Tokens...` dialog.

Disabled when no project is open.

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
Add token to kicad_specgen_local.json → tokens
Pick replacement file or folder
Skip affected item
Cancel
```

**"Add token"** — The user enters or confirms a name (`KSG_*` pattern enforced)
and browses to an absolute path. Writes to `kicad_specgen_local.json → tokens`.

**"Pick replacement file or folder"** — Opens a file/folder picker. The selected
absolute path is stored as a new `KSG_*` token in `kicad_specgen_local.json → tokens`.
The suggested token name is derived from the missing token name. The project
`.kicad_specgen` file is not modified — the token reference in the project
remains as-is and now resolves via the new local token.

**"Skip affected item"** — The item is skipped for this session only. It is not
persisted and will trigger again on the next open.

The project `.kicad_specgen` file remains portable — it is never modified by this
dialog.

Stage: **Stage 2** (requires open project)

---

## `Configure kicad-cli...`

Opens the kicad-cli configuration dialog.

Purpose:

Set or validate the `kicad-cli` executable path.

Writes to: `kicad_specgen_local.json → tools.kicad_cli_path`

The dialog should show:

```text
Current kicad-cli path      (editable text field)
Detected source             (e.g. "macOS application bundle", "PATH", "manual")
KiCad version               (result of kicad-cli --version, shown after Check)
[ Browse... ]
[ Check ]
[ Save ]
[ Cancel ]
```

Auto-detection search order is platform-specific. See `SpecGen_Setup_Process.md`
Phase 3 for the full ordered search list per platform (macOS, Linux, Windows).

**[ Check ]** — Runs `kicad-cli --version` against the current path field content.
Shows the result inline in the dialog below the path field.
On success: shows "KiCad X.Y.Z ✓".
On failure: shows "Error: <error text> ✗" inline — no popup.

**[ Save ]** — Disabled until the path field contains a value that exists on disk.
Does not require `[ Check ]` to have been run, but warns if it has not:
"Path has not been verified. Save anyway? [ Save ] [ Check First ]"

**[ Browse... ]** — Opens a file picker. On macOS, defaults to
`/Applications/KiCad/KiCad.app/Contents/MacOS/`. On Linux and Windows, opens
at the last known location or home directory.

Stage: **Stage 1**

---

## `Edit Project Metadata...`

Switches to the Variables tab and highlights the Project Metadata section.

Purpose:

Navigate the user directly to the project metadata fields in the Variables tab,
where metadata stored in the active `.kicad_specgen → project` section is shown
and edited inline.

This is a page switch, not a separate dialog. The Variables tab owns the editing
UI for project metadata. This menu item is a navigation shortcut.

Metadata fields in the Variables tab include:

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

Writes to: active `.kicad_specgen → project` section (via the Variables tab save
action, not directly from this menu item).

Disabled when no project is open.

Stage: **Stage 2**

---

## `Edit Custom Variables...`

Switches to the Variables tab and highlights the Custom Variables section.

Purpose:

Navigate the user directly to the custom variables editor in the Variables tab,
where user-defined Jinja template variables stored in `.kicad_specgen → variables.custom`
are shown and edited inline.

This is a page switch, not a separate dialog. The Variables tab owns the editing UI.

Variable naming rule:

```text
^[A-Z][A-Z0-9_]*$
```

Validation:

- If a custom variable name matches a KiCad text variable name from the active
  `.kicad_pro`, show an inline warning in the Variables tab: "This variable name
  shadows a KiCad text variable. The custom value will take precedence in Jinja
  templates." This is a warning, not an error — shadowing may be intentional.

Writes to: active `.kicad_specgen → variables.custom` section (via the Variables
tab save action).

Disabled when no project is open.

Stage: **Stage 2**

---

## `Validate Project`

Runs project validation. Read-only — no files are written.

Disabled when no project is open.

Validation checks:

```text
active project file exists and is readable
selected environment exists in kicad_specgen_company.json
effective token table — all required tokens present
missing token references in .kicad_specgen
active .kicad_pro — exists and is readable
active .kicad_jobset — if configured, exists and is readable
support files — tokenized paths resolve to existing files
custom variables — valid names, no schema errors
project save location — file is under specgen/ folder
```

Validation results appear in:

```text
Project tab validation panel (✓ ⚠ ✗ per check)
Status bar summary (e.g. "Validation: ✓ 8 passed, ⚠ 1 warning")
Logs page (full validation log entry with timestamp)
```

Stage: **Stage 2**

---

## `Configure`

Switches to the Configure tab.

Purpose:

Navigate directly to the Configure tab (`[Configure]` in the sidebar), which
provides full access to local machine tokens, company and user configuration,
environment management, preferences (including theme), and configuration
validation.

This is a page switch, not a dialog. It is equivalent to clicking `[Configure]`
in the sidebar. See `SpecGen_Tab_Configure.md` for the full specification of
all five subtabs and their wireframes.

Always available — no project required.

Stage: **Stage 1**

---

# View Menu

The View menu controls workspace navigation, layout, and refresh behavior.

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

---

## Workspace Navigation Actions

These menu actions switch the active sidebar/workspace page.

```text
Project     — Stage 1 (placeholder); full content Stage 2
Variables   — Stage 1 (placeholder); full content Stage 2
Jobset      — Stage 1 (placeholder); full content Stage 2 (read) / Stage 3 (execute)
Report      — Stage 1 (placeholder); full content Stage 4
Logs        — Stage 1 (full)
```

All workspace pages show placeholder content ("Open a project to get started")
when no project is open. They are not disabled — they remain navigable.

`Configure` is accessed via `Edit → Configure`, not from the View menu.
The Fabrication subtab is the third subtab within the Report workspace.
See `SpecGen_Tab_Report.md` for the Report tab subtab structure.

The sidebar does not include a separate Results item.

Reason:

The Jobset workspace owns its generated output review internally via the Results
subtab. See `SpecGen_Tab_Jobset.md` for the Jobset tab subtab structure:

```text
Dashboard
Setup & Run
Results
Output Log
```

---

## `Toggle Sidebar`

Shows or hides the left navigation rail.

---

## `Toggle Status Bar`

Shows or hides the bottom status bar.

---

## `Refresh`

Reloads KiCad-owned file data from disk without affecting the in-memory project state.

Disabled when no project is open.

Refresh scope — reads from disk and updates the display:

```text
kicad_common.json environment variables
.kicad_pro text variables
.kicad_jobset destination list and output path
Generated output file list (JOBSET_OUTPUT_DIR scan)
Effective token table (recomputed from loaded data)
Validation status
Logs page (flushes buffered entries)
```

Refresh does not:

```text
Modify any SpecGen-owned files
Discard unsaved project changes
Reload the .kicad_specgen project file itself (use Close + Open for that)
```

Because Refresh does not touch the project file or in-memory edits, no
confirmation prompt is required.

Stage: **Stage 2**

---

## `Theme`

Theme submenu. Full theme specifications, colour palettes, and implementation
guidance are in `SpecGen_GUI_Theme.md` — the normative reference for all
theme-related values.

```text
┌───────────────────────────────────────┐
│ Theme                                 │
├───────────────────────────────────────┤
│   System                              │
│   Light                               │
│   Dark                                │
│   Engineering Dark                    │
│   ION Dark                            │
│   ION Light                           │
└───────────────────────────────────────┘
```

The active theme selection is indicated with a checkmark next to the current
theme name.

| Display Name | `preferences.theme` value | Description |
|---|---|---|
| System | `system` | OS-adaptive — resolves to Light or Dark at runtime |
| Light | `light` | Clean light background |
| Dark | `dark` | Dark background |
| Engineering Dark | `engineering_dark` | High-contrast dark, EDA/PCB style |
| ION Dark | `ion_dark` | ION brand — Obsidian Coal, Electric Cyan accents |
| ION Light | `ion_light` | ION brand — Clean Frost, Corporate Blue accents |

Writes to: `kicad_specgen_local.json → preferences.theme`

Default when absent or unrecognised: `dark`.

Theme takes effect immediately when selected. No restart required.

Stage 1 must implement Light and Dark fully. System and Engineering Dark
are implemented in Stage 1 if time permits; otherwise they fall back to Dark.
All four entries are present in the submenu from Stage 1 onwards.

See `SpecGen_GUI_Theme.md` §8 for the stage plan and §9 for acceptance criteria.

Stage: **Stage 1**

---

# Help Menu

The Help menu displays Markdown-based help files and diagnostic dialogs.

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

## `Show kicad_specgen_local.json Location`

Shows the resolved path to the local configuration file.

```text
MessageBox:
  kicad_specgen_local.json
  Path: ~/Library/Preferences/kicad/9.0/kicad_specgen_local.json
  [ Open Folder ]   [ Copy Path ]   [ OK ]
```

Read-only. Always available (Stage 1). No project required.

---

## `Show kicad_common.json Location`

Shows the resolved path to the KiCad common configuration file.

```text
MessageBox:
  kicad_common.json
  Path: ~/Library/Preferences/kicad/9.0/kicad_common.json
  Status: ✓ Found   (or ✗ Not found — KiCad may not be installed)
  [ Open Folder ]   [ Copy Path ]   [ OK ]
```

Read-only. Always available (Stage 1). No project required.

---

## `Check kicad-cli`

Runs `kicad-cli --version` and shows the result.

```text
On success:
  MessageBox:
    kicad-cli
    Path: /Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
    Version: KiCad 9.0.3 ✓
    [ OK ]

On failure (binary not found or returns non-zero):
  MessageBox:
    kicad-cli — Not Working
    Path: /path/that/was/configured  (or "not configured")
    Error: <error text from stderr or "file not found">
    Use Edit → Configure kicad-cli... to set the correct path.
    [ Configure kicad-cli... ]   [ OK ]
```

Read-only command (subprocess). Always available (Stage 1). No project required.

---

## `Open Logs Folder`

Opens the application log folder in the OS file manager.

Folder resolution:

```text
If KSG_SYSTEM_LOG_DIR is defined → open that folder.
Else → fall back to {KSG_APP_DIR}/logs/.
If {KSG_APP_DIR}/logs/ does not exist → create it, then open it.
```

If neither path can be determined, shows a MessageBox with the error.

Read-only (navigation). Always available (Stage 1). No project required.

---

## `About KiCad SpecGen`

Opens the About dialog.

```text
┌─────────────────────────────────────────────────────┐
│              About KiCad SpecGen                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│  KiCad SpecGen                                      │
│  Version : 0.1.0  (or from __version__ / git tag)  │
│                                                     │
│  Python   : 3.11.4                                  │
│  PySide6  : 6.x.x                                  │
│  Platform : macOS 14.5                              │
│                                                     │
│  KSG_APP_DIR :                                      │
│  /Users/john/GitHub/kicad-specgen                   │
│                                                     │
│  Local Config :                                     │
│  ~/Library/Preferences/kicad/9.0/                  │
│  kicad_specgen_local.json                           │
│                                                     │
│                           [ OK ]                    │
└─────────────────────────────────────────────────────┘
```

Read-only. Always available (Stage 1). No project required.

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
  configure_tab.md
  project_page.md
  variables_jinja.md
  jobset.md
  report.md
  logs.md
  troubleshooting.md
  kicad_specgen_local.md
  project_kicad_specgen.md
```

Note: `fabrication.md` is not a separate help file. Fabrication is covered in
`report.md` since it is a subtab within the Report workspace. The Help menu
entry `Report and Fabrication` opens `report.md`.

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
kicad_specgen_local.json
kicad_common.json
effective token table
missing token repair
repo vs standalone mode
```

---

## `configure_tab.md`

Explains the Configure tab and its five subtabs.

See `SpecGen_Tab_Configure.md` for the full wireframe specification. This
help file is the in-application user guide version of that content.

Should include:

```text
Local Machine subtab — KSG_* tokens, kicad-cli path, .venv status, setup state
Company & User subtab — company identity, clients, teams, user profiles
Environments subtab — environment definitions, active environment, active user,
                      token priority order (USER → CLIENT → COMPANY → DEFAULT)
Preferences subtab — theme selection, future UI preferences
Validation subtab — configuration validation results, Run Validation
Re-run Setup Wizard
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

Explains the Report workspace and its three subtabs.

Should include:

```text
Report Recipe subtab
  page order
  cover page configuration
  page source types (jobset output, Markdown template, custom PDF)
  section labels and page breaks

Preview & Build subtab
  generation scope (Report only / Report + Fabrication / Fabrication only)
  pre-build checks
  build log
  overwrite confirmation
  dry run behavior

Fabrication subtab
  FAB_OUTPUT_DIR and zip filename template
  selecting jobset destinations to include
  ZIP internal folder structure
  README template
  checksum configuration
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

## `kicad_specgen_local.md`

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

Reference help for the project `.kicad_specgen` JSON file.

Should include:

```text
schema (JSON)
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
File → New SpecGen Project...
  NewProjectDialog

File → Open SpecGen Project...
  QFileDialog (filter: *.kicad_specgen)

File → Save As...
  QFileDialog + overwrite confirmation

Edit → Local Tokens...
  LocalTokensDialog

Edit → Resolve Missing Tokens...
  MissingTokensDialog

Edit → Configure kicad-cli...
  KicadCliDialog

Edit → Configure
  Switches sidebar to Configure tab

Edit → Validate Project
  ValidationPanel update + status bar update

Help → KiCad SpecGen Help
  HelpDialog(help/index.md)

Help → Getting Started
  HelpDialog(help/getting_started.md)

Help → Project Setup and Tokens
  HelpDialog(help/project_setup_tokens.md)

Help → Configure Tab
  HelpDialog(help/configure_tab.md)

Help → Project Page
  HelpDialog(help/project_page.md)

Help → Variables and Jinja Templates
  HelpDialog(help/variables_jinja.md)

Help → Jobset
  HelpDialog(help/jobset.md)

Help → Report and Fabrication
  HelpDialog(help/report.md)

Help → Logs
  HelpDialog(help/logs.md)

Help → Troubleshooting
  HelpDialog(help/troubleshooting.md)

Help → Show kicad_specgen_local.json Location
  MessageBox with resolved path + Open Folder button

Help → Show kicad_common.json Location
  MessageBox with resolved path + Open Folder button

Help → Check kicad-cli
  Runs kicad-cli --version and shows result in MessageBox

Help → Open Logs Folder
  Opens KSG_SYSTEM_LOG_DIR (or fallback log location) in OS file manager

Help → About KiCad SpecGen
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

The Help menu and HelpDialog belong in Stage 1. See `SpecGen_Stage_Plan.md`
for the complete stage breakdown.

Stage 1 should implement:

```text
Help menu (all items; later-stage topics open a placeholder .md)
HelpDialog with QTextBrowser Markdown rendering
OK button close behavior
Missing file error display
index.md
getting_started.md
project_setup_tokens.md
configure_tab.md
logs.md
troubleshooting.md
kicad_specgen_local.md
jobset.md (placeholder — "Jobset features coming in Stage 2")
variables_jinja.md (placeholder — "Variables features coming in Stage 2")
project_page.md (placeholder — "Project tab features coming in Stage 2")
report.md (placeholder — "Report features coming in Stage 4")
```

Later stages complete topic help as each feature is implemented.

Required rule:

```text
A feature is not complete until its help topic is added or updated.
```

