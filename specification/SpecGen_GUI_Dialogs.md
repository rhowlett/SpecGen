# KiCad SpecGen — Dialog Wireframe Specifications

> **Document role:** Wireframe specifications for all SpecGen dialogs —
> layout, field behavior, button behavior, validation, write targets,
> and acceptance criteria.
> **Authority:** `SpecGen_Terminology.md`, `SpecGen_Schema_Definitions.md`,
> `SpecGen_File_Framework.md`.
> **Companion documents:** `SpecGen_GUI_Menus.md` (menu item descriptions
> and behavior), `SpecGen_Tab_Configure.md` (Configure tab context for
> Local Tokens, Add User, Edit Clients and Teams),
> `SpecGen_Stage_Plan.md` (stage assignments).
> **Status:** Approved — ready for Stage 1 and Stage 2 implementation.

---

## Dialog Inventory

| Dialog | Class | Stage | Launched From | Full/Stub |
|---|---|---|---|---|
| New SpecGen Project | `NewProjectDialog` | Stage 2 | File → New SpecGen Project... | Stub in Stage 1; full in Stage 2 |
| Local Tokens | `LocalTokensDialog` | Stage 1 | Edit → Local Tokens... | Full in Stage 1 |
| Missing Tokens | `MissingTokensDialog` | Stage 2 | Automatic on token failure; Edit → Resolve Missing Tokens... | Stub in Stage 1; full in Stage 2 |
| Configure kicad-cli | `KicadCliDialog` | Stage 1 | Edit → Configure kicad-cli... | Full in Stage 1 |
| Add / Edit User | `AddUserDialog` | Stage 1 | Configure tab → Company & User subtab | Full in Stage 1. Department and Team are dropdowns sourced from `company.departments`. |
| Add / Edit Department | `DepartmentDialog` | Stage 1 | Configure tab → Company & User → Departments section | Full in Stage 1. Manages a department and its teams; warns to reassign users before removing a team. |
| Clients and Projects | `ClientsTeamsDialog` | Stage 2 | Configure tab → Environments subtab | Placeholder in Stage 1. Internal teams moved to the Departments section; client/project management belongs to the Environments tab. |
| About KiCad SpecGen | `AboutDialog` | Stage 1 | Help → About KiCad SpecGen | Full in Stage 1 |
| Help | `HelpDialog` | Stage 1 | Help menu (all topics) | Full in Stage 1 |

Dialogs that are **not** covered here (they are simple QFileDialog or MessageBox
calls, fully specified in `SpecGen_GUI_Menus.md`):

```text
Open SpecGen Project...     QFileDialog (filter: *.kicad_specgen)
Save As...                  QFileDialog + overwrite prompt
Show kicad_specgen_local.json Location   MessageBox
Show kicad_common.json Location          MessageBox
Check kicad-cli                          MessageBox
Open Logs Folder                         OS file manager call
```

---

## Common Dialog Conventions

All SpecGen dialogs follow these conventions unless a section below states otherwise.

**Layout:**
- Title bar shows the dialog name exactly as defined in `SpecGen_Terminology.md` §12.
- Content area uses a consistent label/field grid.
- Action buttons (`[ Save ]`, `[ Create ]`, `[ OK ]`) are right-aligned in the
  button row at the bottom.
- Destructive or cancel actions (`[ Cancel ]`, `[ Discard ]`) are to the right
  of the primary action button.
- Dialogs are modal (block the main window) unless noted otherwise.
- Minimum width: 540 px. Minimum height: auto-fit content.
- Resizable unless noted otherwise.

**Validation:**
- Inline validation errors appear below the offending field, not in a popup.
- The primary action button (`[ Save ]`, `[ Create ]`) is disabled until all
  required fields are valid.
- Validation runs on field change (not only on button press).

**Write targets:**
- Every dialog writes only to the file(s) explicitly listed in its write target.
- **All file writes go through `config_service`.** Dialogs never call core
  module functions (e.g. `specgen_local_config.save()`) directly. The dialog
  collects user intent and passes it to `config_service`, which handles the
  file write, `app_state` update, and signal emission. If the underlying save
  implementation changes, only `config_service` needs updating.
- No dialog modifies the project `.kicad_specgen` file unless explicitly noted.
- No dialog modifies KiCad-owned files (`kicad_common.json`, `.kicad_pro`,
  `.kicad_jobset`).

**Escape / Cancel:**
- Pressing Escape or clicking `[ Cancel ]` / `[ Discard ]` closes the dialog
  with no writes and no side effects.

---

## `NewProjectDialog` — New SpecGen Project

**Class:** `NewProjectDialog`
**Stage:** Stub in Stage 1. Full implementation in Stage 2.
**Launched from:** File → New SpecGen Project...
**Writes to:** New `.kicad_specgen` file under `{KICAD_PROJECT_DIR}/specgen/`;
  updates `kicad_specgen_local.json → last_session` and `recent_projects`.

### Stage 1 stub behavior

In Stage 1, `NewProjectDialog` opens and shows a placeholder message:

```text
┌─────────────────────────────────────────────┐
│  New SpecGen Project                        │
├─────────────────────────────────────────────┤
│                                             │
│  New project creation will be available     │
│  in Stage 2.                                │
│                                             │
│  To open an existing project, use           │
│  File → Open SpecGen Project...             │
│                                             │
├─────────────────────────────────────────────┤
│                                  [ Close ]  │
└─────────────────────────────────────────────┘
```

### Stage 2 full wireframe

```text
┌──────────────────────────────────────────────────────────────────────────┐
│  New SpecGen Project                                                     │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  KiCad Project Folder                                                    │
│  ┌───────────────────────────────────────────────────┐  [ Browse... ]   │
│  │ (no folder selected)                              │                  │
│  └───────────────────────────────────────────────────┘                  │
│  ⚠ No .kicad_pro found in this folder. (non-blocking — shown if needed) │
│                                                                          │
│  SpecGen Project Name                                                    │
│  ┌───────────────────────────────────────────────────┐                  │
│  │ (auto-filled from KiCad project folder name)      │                  │
│  └───────────────────────────────────────────────────┘                  │
│  Will create: {KICAD_PROJECT_DIR}/specgen/<name>.kicad_specgen           │
│                                                                          │
│  Environment                                                             │
│  ┌───────────────────────────────────────────────────┐                  │
│  │ (select from list)                           ▼    │                  │
│  └───────────────────────────────────────────────────┘                  │
│  ⚠ No environments defined. Configure → Environments subtab.            │
│    (shown only when environment list is empty)                           │
│                                                                          │
│  ── Summary ──────────────────────────────────────────────────────────  │
│  KiCad Project Folder  : (none)                                          │
│  SpecGen Project Name  : (none)                                          │
│  Environment           : (none)                                          │
│  Project file          : (none)                                          │
│                                                                          │
├──────────────────────────────────────────────────────────────────────────┤
│                                          [ Create ]       [ Cancel ]     │
└──────────────────────────────────────────────────────────────────────────┘
```

### Field behavior

**KiCad Project Folder**
- `[ Browse... ]` opens a folder picker (not a file picker).
- After selection, SpecGen scans the folder for a `.kicad_pro` file.
- If found, the resolved path appears in the Summary panel.
- If not found, shows the ⚠ non-blocking warning inline. The user may proceed
  — KiCad may not have been run in that folder yet.
- `{KICAD_PROJECT_DIR}` in the "Will create" preview is derived from this
  selection. It is not a pre-existing runtime token.

**SpecGen Project Name**
- Auto-fills with the selected folder's base name.
- User may edit. Must not be blank, spaces only, or contain characters invalid
  in a filename.
- Updates the "Will create" path preview on each keystroke.

**Environment**
- Dropdown populated from `kicad_specgen_company.json → environments`.
- Seeded with `kicad_specgen_local.json → active_environment`.
- If no environments are defined: shows inline ⚠ warning; `[ Create ]` is
  disabled until at least one environment exists.

**[ Create ]**
- Enabled only when KiCad Project Folder is set, SpecGen Project Name is
  valid, and at least one environment is selected.
- Creates `specgen/` subfolder if absent.
- Copies `{KSG_APP_DIR}/default.kicad_specgen` to the new path.
- Sets `workspace.environment` in the new file.
- Saves the file and opens the project.
- If the target file already exists: prompt Overwrite / Rename / Cancel before
  writing.

### Validation rules

```text
KiCad Project Folder must be set (non-empty)
SpecGen Project Name must be a valid filename (no path separators, not blank)
At least one environment must be available
Target .kicad_specgen path must not already exist (or user confirms overwrite)
```

### Write targets

```text
{KICAD_PROJECT_DIR}/specgen/<name>.kicad_specgen    (new file — created)
kicad_specgen_local.json → last_session             (updated on success)
kicad_specgen_local.json → recent_projects          (updated on success)
```

### Acceptance criteria

```text
✓ Dialog opens from File → New SpecGen Project...
✓ Folder picker filters for folders only
✓ Project name auto-fills from folder name
✓ Name field validates on each keystroke
✓ Environment dropdown populates from company file
✓ Summary panel updates in real time as fields are filled
✓ [ Create ] disabled until all three fields are valid
✓ No-environments warning shown and [ Create ] disabled when list is empty
✓ No-kicad_pro warning shown inline (non-blocking)
✓ Overwrite prompt shown if target file exists
✓ specgen/ subfolder created if absent
✓ New file uses the correct default template
✓ New file stores environment, not absolute paths
✓ last_session and recent_projects updated on success
✓ [ Cancel ] closes with no writes
```

---

## `LocalTokensDialog` — Local Tokens

**Class:** `LocalTokensDialog`
**Stage:** Full in Stage 1.
**Launched from:** Edit → Local Tokens...
**Writes to:** `kicad_specgen_local.json → tokens`

```text
┌──────────────────────────────────────────────────────────────────────────┐
│  Local Tokens                                                            │
├────────────────────────────────────────┬────────────────────────┬───────┤
│ Token                                  │ Value                  │ Status│
├────────────────────────────────────────┼────────────────────────┼───────┤
│ KSG_APP_DIR                         ★  │ /Users/john/kicad-sg   │  ✓   │
│ KSG_SYSTEM_CONFIG_DIR               ★  │ ~/Library/Pref/kicad/  │  ✓   │
│ KSG_COMPANY_DIR                     ★  │ /Users/john/CompanyRepo │  ✓   │
│ KSG_USER_SPECGEN_DIR                ★  │ /Users/john/.../12345  │  ✓   │
│ KSG_USER_COMMON_DIR                 ★  │ /Users/john/.../common │  ✓   │
│ KSG_SYSTEM_LOG_DIR                     │ /Users/john/logs       │  ✓   │
├────────────────────────────────────────┴────────────────────────┴───────┤
│  ★ = required token (cannot be removed)                                  │
├──────────────────────────────────────────────────────────────────────────┤
│  [ Add Token ]   [ Remove Selected ]   [ Browse... ]   [ Edit ]         │
├──────────────────────────────────────────────────────────────────────────┤
│  (inline error area — shown when validation fails on Save)               │
├──────────────────────────────────────────────────────────────────────────┤
│                                            [ Save ]       [ Cancel ]     │
└──────────────────────────────────────────────────────────────────────────┘
```

### Field and button behavior

**Token table**
- Three columns: Token name, Value, Status.
- Status column shows ✓ (path exists), ⚠ (path not found on disk), ✗ (invalid
  format).
- Required tokens are marked ★ in the Token column.
- Single-click selects a row.
- Double-click opens inline editing for the Value cell.

**[ Add Token ]**
- Opens a small inline Add Token row at the bottom of the table:

```text
│ ┌──────────────────────────┐  ┌──────────────────────────┐  [ Browse ] │
│ │ Token name (KSG_*)       │  │ Absolute path             │             │
│ └──────────────────────────┘  └──────────────────────────┘             │
│  ✗ Token name must match ^KSG_[A-Z0-9_]+$   (inline, shown if invalid) │
│  ✗ Value must be an absolute path            (inline, shown if invalid) │
│  ✗ Protected token — cannot be defined here  (inline, shown if rejected)│
```

- Inline row is confirmed with Enter or clicking Add; dismissed with Escape.

**[ Remove Selected ]**
- Disabled when a required token (★) is selected.
- Disabled when no row is selected.
- Removes the selected row immediately (not saved until `[ Save ]`).

**[ Browse... ]**
- Disabled when no row is selected.
- Opens a folder picker for the selected token's Value cell.
- Updates the Value cell with the selected absolute path.

**[ Edit ]**
- Opens the selected row's Value cell for inline editing.
- Equivalent to double-clicking the Value cell.

**[ Save ]**
- Validates all token values are absolute paths before writing.
- If any value fails validation, shows an inline error below the table
  identifying the offending row. Save is blocked.
- On success: writes `kicad_specgen_local.json → tokens`, closes the dialog,
  reloads the effective token table, refreshes the Project tab validation
  panel (if a project is open).

### Validation rules

```text
All token names must match ^KSG_[A-Z0-9_]+$
All token values must be absolute paths
Protected derived runtime tokens rejected:
  SPECGEN_PROJECT_FILE, KSG_PROJECT_SPECGEN_DIR, KICAD_PROJECT_DIR,
  GIT_PROJECT_DIR, JOBSET_OUTPUT_DIR, FAB_OUTPUT_DIR
Required tokens cannot be removed:
  KSG_APP_DIR, KSG_SYSTEM_CONFIG_DIR, KSG_COMPANY_DIR,
  KSG_USER_SPECGEN_DIR, KSG_USER_COMMON_DIR
```

### Write targets

```text
kicad_specgen_local.json → tokens    (via config_service.save_local_tokens())
```

### Acceptance criteria

```text
✓ Dialog opens from Edit → Local Tokens...
✓ Token table shows all KSG_* tokens from kicad_specgen_local.json → tokens
✓ Required tokens marked ★; Remove Selected disabled when one is selected
✓ Status column shows ✓ / ⚠ / ✗ per token path
✓ Add Token validates name (^KSG_[A-Z0-9_]+$) and value (absolute path) inline
✓ Add Token rejects protected derived runtime tokens with inline error
✓ Browse sets absolute path for selected token row
✓ Edit allows inline editing of Value cell
✓ Save blocked with inline error if any value fails validation
✓ Save writes kicad_specgen_local.json → tokens
✓ After save: effective token table reloads; Project tab validation refreshes
✓ Cancel closes with no writes
```

---

## `MissingTokensDialog` — Missing Tokens

**Class:** `MissingTokensDialog`
**Stage:** Stub in Stage 1. Full implementation in Stage 2.
**Launched from:** Automatically on token resolution failure at project open;
  manually from Edit → Resolve Missing Tokens...
**Writes to:** `kicad_specgen_local.json → tokens` (Provide option);
  `kicad_specgen_local.json → skipped_tokens` (Skip option);
  Active `.kicad_specgen` (Remove option — sets dirty flag).

### Stage 1 stub behavior

In Stage 1, the dialog module exists but triggers are not yet active (no project
opens in Stage 1). The stub shows a placeholder if launched manually:

```text
┌─────────────────────────────────────────────┐
│  Missing Tokens                             │
├─────────────────────────────────────────────┤
│                                             │
│  Token resolution requires an open project. │
│  Open a project to use this feature.        │
│                                             │
├─────────────────────────────────────────────┤
│                                  [ Close ]  │
└─────────────────────────────────────────────┘
```

### Stage 2 full wireframe

Shown once per missing token. If multiple tokens are missing, iterates through
each one sequentially (e.g. "Token 1 of 3").

```text
┌──────────────────────────────────────────────────────────────────────────┐
│  Missing Tokens  (1 of 3)                                                │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Missing Token   : KSG_CLIENT_LEGACY_DOCS                                │
│  Used in         : files.title_page                                      │
│  Reference       : {KSG_CLIENT_LEGACY_DOCS}/templates/cover.md          │
│  Environment     : medical_devices                                       │
│                                                                          │
│  ── What would you like to do? ────────────────────────────────────────  │
│                                                                          │
│  (•) Provide path — add token to local config                            │
│                                                                          │
│      Token name  : [ KSG_CLIENT_LEGACY_DOCS              ]               │
│      Path        : [ (enter absolute path)          ]  [ Browse... ]    │
│      ✗ Path must be an absolute path.  (shown if invalid)                │
│                                                                          │
│  ( ) Skip for this session                                               │
│      The dialog will appear again on next project open.                  │
│                                                                          │
│  ( ) Remove from project                                                 │
│      Deletes the reference from the project file. Sets dirty flag.       │
│      Other users will not see this dialog for this reference.            │
│                                                                          │
├──────────────────────────────────────────────────────────────────────────┤
│                             [ Apply ]   [ Skip All ]   [ Cancel ]        │
└──────────────────────────────────────────────────────────────────────────┘
```

### Button behavior

**[ Apply ]**
- Applies the selected option for the current token and advances to the next.
- If this is the last token: closes the dialog.
- **Provide:** Writes the new token to `kicad_specgen_local.json → tokens`.
  The project file is not modified.
- **Skip:** Adds the token name to `kicad_specgen_local.json → skipped_tokens`.
  The project file is not modified.
- **Remove:** Deletes the token reference from the active `.kicad_specgen` file.
  Sets the project dirty flag. Does not save automatically — user must save
  the project for the removal to persist.

**[ Skip All ]**
- Skips all remaining unresolved tokens in this session.
- Adds all remaining token names to `kicad_specgen_local.json → skipped_tokens`.
- Closes the dialog.

**[ Cancel ]**
- Closes the dialog. No tokens are resolved.
- The project opens in a degraded state — affected features may be unavailable.

### Repository file not found variant

When a token resolves correctly but the referenced file is not found on disk
(different from a missing token — the token exists but the file is absent):

```text
┌──────────────────────────────────────────────────────────────────────────┐
│  File Not Found                                                          │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  A referenced file was not found on disk.                                │
│                                                                          │
│  Token     : KSG_COMPANY_DIR                                             │
│  Reference : {KSG_COMPANY_DIR}/SpecGen/templates/title_page.md          │
│  Resolved  : /Users/john/CompanyRepo/SpecGen/templates/title_page.md    │
│  Status    : ✗ File not found                                            │
│                                                                          │
│  If you are using a shared repository, ensure you have the latest        │
│  version pulled, then use View → Refresh to re-check.                   │
│                                                                          │
│  SpecGen does not perform git operations.                                │
│                                                                          │
├──────────────────────────────────────────────────────────────────────────┤
│              [ Skip for Session ]   [ Remove from Project ]   [ Close ]  │
└──────────────────────────────────────────────────────────────────────────┘
```

### Validation rules

```text
Provide option: token name must match ^KSG_[A-Z0-9_]+$
Provide option: path must be an absolute path
Provide option: token name must not be a protected derived runtime token
Remove option: sets project dirty flag — user must save to persist removal
```

### Write targets

```text
kicad_specgen_local.json → tokens           (Provide — via config_service.save_local_tokens())
kicad_specgen_local.json → skipped_tokens   (Skip   — via config_service.save_skipped_tokens())
Active .kicad_specgen (reference removed)   (Remove — via config_service.remove_project_token_ref(),
                                             sets dirty flag; requires explicit project save)
```

**Service boundary note:** `remove_project_token_ref()` writes to the project
`.kicad_specgen` file, which is normally owned by `project_service` (Stage 2).
It is placed on `config_service` as a Stage 1 stub because `MissingTokensDialog`
is a Stage 2 full implementation and no project is opened in Stage 1. When
Stage 2 is built, evaluate moving this method to `project_service.remove_token_ref()`
for cleaner service ownership.

### Acceptance criteria

```text
✓ Dialog fires automatically when token resolution fails at project open
✓ Dialog accessible manually from Edit → Resolve Missing Tokens...
✓ Shows token name, usage context, full reference, and active environment
✓ "1 of N" counter shown when multiple tokens are missing
✓ Provide option validates token name and path inline
✓ Provide writes to kicad_specgen_local.json → tokens; project file unchanged
✓ Skip writes to kicad_specgen_local.json → skipped_tokens; fires again next open
✓ Remove deletes reference from project file; sets dirty flag
✓ Skip All skips all remaining tokens and closes dialog
✓ Cancel leaves project in degraded state without writes
✓ File Not Found variant shown when token resolves but file is absent
✓ File Not Found variant provides repo pull guidance
✓ Project file never written with absolute paths by this dialog
```

---

## `KicadCliDialog` — Configure kicad-cli

**Class:** `KicadCliDialog`
**Stage:** Full in Stage 1.
**Launched from:** Edit → Configure kicad-cli...
**Writes to:** `kicad_specgen_local.json → tools.kicad_cli_path`

```text
┌──────────────────────────────────────────────────────────────────────────┐
│  Configure kicad-cli                                                     │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  kicad-cli Path                                                          │
│  ┌───────────────────────────────────────────────────┐  [ Browse... ]   │
│  │ /Applications/KiCad/KiCad.app/Contents/MacOS/ki.. │                  │
│  └───────────────────────────────────────────────────┘                  │
│  Source   : macOS application bundle                                     │
│                                                                          │
│  ── Version Check ──────────────────────────────────────────────────    │
│  Result   : KiCad 9.0.3  ✓                                              │
│             (shown after [ Check ] is run; blank before first check)    │
│                                                                          │
│  ⚠ Path has not been verified. (shown if Save clicked without Check)    │
│                                                                          │
├──────────────────────────────────────────────────────────────────────────┤
│  [ Check ]                          [ Save ]            [ Cancel ]       │
└──────────────────────────────────────────────────────────────────────────┘
```

### Button behavior

**[ Browse... ]**
- Opens a file picker for an executable.
- macOS default start path: `/Applications/KiCad/KiCad.app/Contents/MacOS/`
- Linux/Windows: last known location or home directory.
- Clears the Version Check result when a new path is selected.

**[ Check ]**
- Runs `kicad-cli --version` against the current path field content.
- On success: shows `KiCad X.Y.Z  ✓` in the Version Check area.
- On failure: shows `Error: <stderr text or "file not found">  ✗` inline.
  No popup.

**[ Save ]**
- Disabled until the path field contains a non-empty value that exists on disk.
- If `[ Check ]` has not been run: shows inline warning
  "Path has not been verified." and prompts `[ Save Anyway ]` / `[ Check First ]`.
- On success: writes `kicad_specgen_local.json → tools.kicad_cli_path` and
  closes the dialog.

**[ Cancel ]**
- Closes with no writes.

### Validation rules

```text
Path field must be non-empty
Path must point to a file that exists on disk (required for Save to enable)
kicad-cli --version must succeed for the path to be considered verified
  (unverified path can still be saved with explicit confirmation)
```

### Write targets

```text
kicad_specgen_local.json → tools.kicad_cli_path    (via config_service.save_kicad_cli_path())
```

### Acceptance criteria

```text
✓ Dialog opens from Edit → Configure kicad-cli...
✓ Current path pre-filled from kicad_specgen_local.json → tools.kicad_cli_path
✓ Source label shows detection method (macOS app bundle, PATH, manual)
✓ Browse opens file picker at platform-appropriate default location
✓ Check runs kicad-cli --version and shows result inline
✓ Check failure shows error inline (no popup)
✓ Save disabled when path field is empty or file does not exist on disk
✓ Save without Check shows inline warning with Save Anyway / Check First
✓ Save writes kicad_specgen_local.json → tools.kicad_cli_path
✓ Cancel closes with no writes
```

---

## `AddUserDialog` — Add / Edit User

**Class:** `AddUserDialog`
**Stage:** Full in Stage 1.
**Launched from:** Configure tab → Company & User subtab →
  `[ Add User ]` or `[ Edit Selected ]`
**Writes to:** `kicad_specgen_users.json → users`

```text
┌──────────────────────────────────────────────────────────────────────────┐
│  Add User                         (title shows "Edit User" in edit mode) │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Worker ID *        [ 12345                         ]                    │
│                     ✗ Worker ID already exists.  (shown on duplicate)   │
│                                                                          │
│  Display Name *     [ John Smith                    ]                    │
│                                                                          │
│  Preferred Name     [ John                          ]                    │
│  Family Name        [ Smith                         ]                    │
│  Email              [ john.smith@company.com        ]                    │
│  Department         [ Engineering Tools          ▼ ]                    │
│                       dropdown sourced from company.departments         │
│  Team               [ Automation                  ▼ ]                    │
│                       dropdown — repopulates when Department changes     │
│  Job Title          [ Senior Electrical Engineer    ]                    │
│                                                                          │
│  Worker Type        [ Employee                 ▼   ]                     │
│                       employee / contractor / external / hobby           │
│                                                                          │
│  Active             [✓] (checkbox — checked by default for new users)   │
│  Admin              [ ] (checkbox — grants permission to edit shared     │
│                           SpecGen configuration)                         │
│                                                                          │
│  Client Assignments (optional)                                           │
│  ┌───────────────────────────────────────────────────────────────────┐   │
│  │ medical_devices / pacemaker_mk2    aerospace_systems / avionics_v3 │   │
│  └───────────────────────────────────────────────────────────────────┘   │
│  Each entry is a {client_id, project_id} pair from company.clients      │
│  (managed in the Environments tab in Stage 2)                           │
│                                                                          │
│  * Required field                                                        │
│                                                                          │
├──────────────────────────────────────────────────────────────────────────┤
│                                           [ Save ]       [ Cancel ]      │
└──────────────────────────────────────────────────────────────────────────┘
```

### Field behavior

**Worker ID**
- Required. Must be unique across all users in `kicad_specgen_users.json`.
- In Edit mode: field is read-only (Worker ID cannot be changed after creation).
- Inline error shown if a duplicate is entered in Add mode.

**Display Name**
- Required. Used in report author fields and UI user dropdowns.

**Department / Team**
- Dropdowns sourced from `company.departments`. `department` stores the
  `dept_id`; `team` stores the `team_id`. Selecting a department repopulates
  the Team dropdown with that department's teams.
- On Add, the user's folders are created per the documented convention:
  `{KSG_COMPANY_DIR}/SpecGen/Users/<worker_id>/specgen` and `/common`.

**Worker Type**
- Dropdown: `employee`, `contractor`, `external`, `hobby`.
- See `SpecGen_Schema_Definitions.md` §4 for enum definitions.

**Client Assignments**
- Optional list of `{client_id, project_id}` pairs from the company file.
- Preserved unchanged when editing a user in Stage 1; full editing UI lands
  with the Environments tab in Stage 2.

**Active**
- Default: checked for new users.
- Unchecked: deactivated users cannot be set as the active user.

**Admin**
- Default: unchecked.
- Checked: user can edit shared SpecGen configuration.

### Write targets

```text
kicad_specgen_users.json → users    (via config_service.save_user())
```

### Validation rules

```text
Worker ID must be non-empty and unique (add mode)
Display Name must be non-empty
Worker Type must be one of: employee, contractor, external, hobby
```

### Acceptance criteria

```text
✓ Dialog opens in Add mode from [ Add User ] button
✓ Dialog opens in Edit mode from [ Edit Selected ] with fields pre-filled
✓ Worker ID is editable in Add mode; read-only in Edit mode
✓ Duplicate Worker ID shows inline error; Save blocked
✓ Display Name required; Save blocked if empty
✓ Worker Type dropdown shows all four valid values
✓ Department and Team dropdowns populate from company.departments
✓ Selecting a Department repopulates the Team dropdown
✓ Department/Team dropdowns show "(none)" when company file has none
✓ Active checkbox defaults to checked for new users
✓ Admin checkbox defaults to unchecked
✓ Save writes kicad_specgen_users.json → users
✓ On Add, the user's specgen/ and common/ folders are created
✓ Cancel closes with no writes
✓ Title bar shows "Add User" or "Edit User" correctly
```

---

## `DepartmentDialog` — Add / Edit Department

**Class:** `DepartmentDialog`
**Stage:** Full in Stage 1.
**Launched from:** Configure tab → Company & User subtab → Departments section →
  `[ Add Department ]` or `[ Edit Selected Department ]`
**Writes to:** `kicad_specgen_company.json → departments`

```text
┌──────────────────────────────────────────────────────────────────────────┐
│  Edit Department                  (title shows "Add Department" in add)  │
├──────────────────────────────────────────────────────────────────────────┤
│  Department Name    [ Engineering Tools             ]                    │
│                                                                          │
│  Teams:                                                                  │
│  ┌───────────────────────────────────────────────────────────────────┐   │
│  │ Automation   [automation]                                         │   │
│  │ Core         [core]                                               │   │
│  └───────────────────────────────────────────────────────────────────┘   │
│  [ Add Team ]   [ Rename Team ]   [ Remove Team ]                        │
│                                                                          │
├──────────────────────────────────────────────────────────────────────────┤
│                                           [ Save ]       [ Cancel ]      │
└──────────────────────────────────────────────────────────────────────────┘
```

### Behavior notes

- A department contains teams keyed by `team_id`. Renaming a team changes its
  display name only; the `team_id` (and therefore user references) stays stable.
- `[ Remove Team ]` checks for users assigned to this department + team. If any
  exist, it warns: "This team has assigned users: … Reassign these users to
  another team before removing this team." and blocks removal.
- Removing a **department** is handled at the tab level (the Departments
  section's `[ Remove Selected Department ]` button), which likewise blocks
  removal while any user is assigned to that department.
- `[ Add Team ]` prompts for a team name and derives a `team_id` slug.

### Write targets

```text
kicad_specgen_company.json → departments   (via config_service.save_company())
```

### Acceptance criteria

```text
✓ Dialog opens from the Departments section
✓ Department name is required; Save blocked if empty
✓ Teams list shows each team's display name and team_id
✓ Add Team prompts for a name and creates a slugged team_id
✓ Rename Team changes display name only; team_id is preserved
✓ Remove Team warns and blocks when users are assigned to that team
✓ Save writes kicad_specgen_company.json → departments
✓ Cancel closes with no writes
```

---

## `ClientsTeamsDialog` — Clients and Projects (Stage 2 placeholder)

**Class:** `ClientsTeamsDialog`
**Stage:** Placeholder in Stage 1; full in Stage 2 (Environments tab).
**Launched from:** Configure tab → Environments subtab (Stage 2)
**Writes to:** `kicad_specgen_company.json → clients` (with nested `projects`)

Internal teams are no longer edited here — they are managed in the Departments
section of the Company & User subtab via `DepartmentDialog`. Client and project
management mirrors the department/team structure
(`clients.<client_id>.projects.<project_id>` with a `status` of `active` |
`inactive` in Stage 1) and is delivered with the Environments tab in Stage 2.
In Stage 1 this dialog is a placeholder that directs the user to the
Departments section and the forthcoming Environments tab.

---

## `AboutDialog` — About KiCad SpecGen

**Class:** `AboutDialog`
**Stage:** Full in Stage 1.
**Launched from:** Help → About KiCad SpecGen
**Writes to:** Nothing — read-only.
**Always available:** Yes. No project required.
**Resizable:** No — fixed size.

```text
┌──────────────────────────────────────────────────┐
│            About KiCad SpecGen                   │
├──────────────────────────────────────────────────┤
│                                                  │
│  KiCad SpecGen                                   │
│  Version  : 0.1.0                                │
│             (from __version__ or git tag)        │
│                                                  │
│  Python   : 3.11.4                               │
│  PySide6  : 6.x.x                               │
│  Platform : macOS 14.5  (or Linux x86_64, etc.) │
│                                                  │
│  ────────────────────────────────────────────    │
│                                                  │
│  KSG_APP_DIR                                     │
│  /Users/john/GitHub/kicad-specgen                │
│                                                  │
│  Local Config                                    │
│  ~/Library/Preferences/kicad/9.0/               │
│  kicad_specgen_local.json                        │
│                                                  │
│  .venv                                           │
│  {KSG_APP_DIR}/.venv   ✓ Active                  │
│                                                  │
│  ────────────────────────────────────────────    │
│                                                  │
│  © 2026 KiCad SpecGen Contributors               │
│                                                  │
├──────────────────────────────────────────────────┤
│                             [ OK ]               │
└──────────────────────────────────────────────────┘
```

### Content rules

- **Version** — Read from `__version__` in the application package, or from
  the latest Git tag. Falls back to "development" if neither is available.
- **Python** — `sys.version_info`.
- **PySide6** — `PySide6.__version__`.
- **Platform** — `platform.system()` + `platform.release()`.
- **KSG_APP_DIR** — From the effective token table.
- **Local Config path** — Resolved from `platform_paths.py`.
- **.venv** — Path is `{KSG_APP_DIR}/.venv`. Status shows ✓ Active if the
  running Python is inside the `.venv`, ⚠ Not active if not.
- `[ OK ]` — Only button. Closes the dialog.

### Acceptance criteria

```text
✓ Dialog opens from Help → About KiCad SpecGen
✓ Version shown correctly from __version__ or git tag
✓ Python, PySide6, and platform versions shown
✓ KSG_APP_DIR path shown
✓ Local Config path shown (resolved, not tokenized)
✓ .venv path and active status shown
✓ [ OK ] closes the dialog
✓ Dialog is non-resizable
✓ No writes to any file
```

---

## `HelpDialog` — Help

**Class:** `HelpDialog`
**Stage:** Full in Stage 1.
**Launched from:** All Help menu topic items.
**Writes to:** Nothing — read-only.
**Always available:** Yes. No project required.
**Resizable:** Yes. Minimum size: 900 × 650.

```text
┌──────────────────────────────────────────────────────────────────────────┐
│  Help — Getting Started                                                  │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                                                                    │  │
│  │  # Getting Started with KiCad SpecGen                              │  │
│  │                                                                    │  │
│  │  ## 1. Run setup.py                                                │  │
│  │  ...                                                               │  │
│  │  ## 2. Configure kicad-cli                                         │  │
│  │  ...                                                               │  │
│  │                                                                    │  │
│  │  (scrollable QTextBrowser area)                                    │  │
│  │                                                                    │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
├──────────────────────────────────────────────────────────────────────────┤
│                                                      [ OK ]              │
└──────────────────────────────────────────────────────────────────────────┘
```

### Missing file error variant

When the requested `.md` file is not found:

```text
┌──────────────────────────────────────────────────────────────────────────┐
│  Help — Jobset                                                           │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                                                                    │  │
│  │  Help file not found:                                              │  │
│  │  help/jobset.md                                                    │  │
│  │                                                                    │  │
│  │  This help topic may not be available yet.                         │  │
│  │                                                                    │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
├──────────────────────────────────────────────────────────────────────────┤
│                                                      [ OK ]              │
└──────────────────────────────────────────────────────────────────────────┘
```

### Implementation

```python
# Recommended Stage 1 implementation pattern
class HelpDialog(QDialog):
    def __init__(self, help_file: str, title: str, parent=None):
        # help_file: relative path from app root, e.g. "help/getting_started.md"
        # title: shown in title bar, e.g. "Getting Started"
        ...
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(True)
        ...

    def load(self, help_file: str):
        path = KSG_APP_DIR / help_file
        if path.exists():
            self.browser.setMarkdown(path.read_text(encoding="utf-8"))
        else:
            self.browser.setPlainText(
                f"Help file not found:\n{help_file}\n\n"
                "This help topic may not be available yet."
            )
```

### Markdown rendering support

`QTextBrowser.setMarkdown()` (Qt 5.14+) renders:

```text
Headings (# through ####)
Paragraphs
Bold and italic
Bullet and numbered lists
Horizontal rules
Inline code
Fenced code blocks
Links (external links open in OS browser)
```

Tables are supported in Qt 6.x via `QTextBrowser`. Verify rendering in the
target PySide6 version during Stage 1 implementation.

### Help file to menu item mapping

| Help Menu Item | File | Stage 1 status |
|---|---|---|
| KiCad SpecGen Help | `help/index.md` | Full |
| Getting Started | `help/getting_started.md` | Full |
| Project Setup and Tokens | `help/project_setup_tokens.md` | Full |
| Configure Tab | `help/configure_tab.md` | Full |
| Project Page | `help/project_page.md` | Placeholder |
| Variables and Jinja Templates | `help/variables_jinja.md` | Placeholder |
| Jobset | `help/jobset.md` | Placeholder |
| Report and Fabrication | `help/report.md` | Placeholder |
| Logs | `help/logs.md` | Full |
| Troubleshooting | `help/troubleshooting.md` | Full |

Additionally referenced (not in Help menu but used by application):

| Topic | File | Stage 1 status |
|---|---|---|
| Local config reference | `help/kicad_specgen_local.md` | Full |
| Project file reference | `help/project_kicad_specgen.md` | Placeholder |

### Acceptance criteria

```text
✓ Dialog opens for every Help menu topic item
✓ Title bar shows the topic name
✓ QTextBrowser renders Markdown headings, paragraphs, lists, code blocks
✓ Content area is scrollable
✓ External links open in the OS browser (not inside the dialog)
✓ Missing file shows the error variant with the file path (no crash)
✓ [ OK ] closes the dialog
✓ Dialog is resizable; minimum size 900 × 650
✓ No writes to any file
✓ Placeholder files show clear "feature coming in Stage N" message
```

---

## Shared Widget: `token_table.py`

Several dialogs use the same token table widget. To avoid duplication, the
token table is implemented as a shared widget in `ui/widgets/token_table.py`.

The widget supports two modes:

```text
Read-only mode    — shows token name, resolved path, status (✓ ⚠ ✗)
                    Used in: Configure tab Local Machine subtab
                             Validation subtab effective token display

Edit mode         — adds Add / Remove / Browse / Edit buttons
                    Used in: LocalTokensDialog
                             Configure tab Local Machine subtab (token editing)
```

Column layout:

```text
Token name  (fixed width, monospace font)
Value       (expands, path or token reference)
Status      (fixed width, icon: ✓ ⚠ ✗)
```

The required-token marker (★) is added by `LocalTokensDialog` as an overlay
on the Token name column; it is not part of the base widget.

---

## Acceptance Criteria Summary

| Dialog | Stage | Key gate |
|---|---|---|
| `NewProjectDialog` | 1 (stub) / 2 (full) | Stage 2: creates valid portable .kicad_specgen |
| `LocalTokensDialog` | 1 (full) | Stage 1: saves tokens; rejects protected names |
| `MissingTokensDialog` | 1 (stub) / 2 (full) | Stage 2: Provide/Skip/Remove all work correctly |
| `KicadCliDialog` | 1 (full) | Stage 1: Check runs kicad-cli; Save writes local config |
| `AddUserDialog` | 1 (full) | Stage 1: adds/edits users in kicad_specgen_users.json |
| `ClientsTeamsDialog` | 1 (full) | Stage 1: edits clients/teams in kicad_specgen_company.json |
| `AboutDialog` | 1 (full) | Stage 1: shows version, paths, .venv status |
| `HelpDialog` | 1 (full) | Stage 1: renders all Stage 1 .md files; safe error on missing |

---

*End of KiCad SpecGen Dialog Wireframe Specifications.*
