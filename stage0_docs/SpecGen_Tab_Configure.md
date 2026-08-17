# KiCad SpecGen — Configure Tab Wireframes

> **Document role:** Primary wireframe specification for the Configure tab
> and all five of its subtabs.
> **Authority:** `SpecGen_Terminology.md`, `SpecGen_Schema_Definitions.md`,
> `SpecGen_GUI_Theme.md`.
> **Companion documents:** `SpecGen_Setup_Process.md` (setup wizard that
> creates the initial configuration this tab edits),
> `SpecGen_File_Framework.md` (file ownership rules),
> `SpecGen_GUI_Menus.md` (Edit → Configure and Edit → Local Tokens...),
> `SpecGen_Schema_Definitions.md` (schemas for all files written here).
> **Status:** Approved — ready for Stage 1 implementation.

---

## Overview

The Configure tab is a permanent sidebar page (`[Configure]`) that provides
full post-setup configuration management without re-running `setup.py`. It
is always accessible — no project is required, and it remains functional
when setup is incomplete.

### Sidebar placement

```text
SIDEBAR

  [Project]
  [Variables]
  [Jobset]
  [Report]
  [Logs]
  ─────────────
  [Configure]
```

The separator visually divides the project workflow pages (Project through
Logs) from the application configuration page. The Configure tab is always
enabled regardless of project or setup state.

### Subtab layout

```text
┌───────────────────┬───────────────┬───────────────┬────────────────┬──────────────┐
│ Local Machine     │ Company & User│ Environments  │ Preferences    │ Validation   │
└───────────────────┴───────────────┴───────────────┴────────────────┴──────────────┘
```

| Subtab | Writes To | Always Available |
|---|---|---|
| Local Machine | `kicad_specgen_local.json` | Yes |
| Company & User | `kicad_specgen_company.json`, `kicad_specgen_users.json` | Yes |
| Environments | `kicad_specgen_company.json`, `kicad_specgen_local.json` | Yes |
| Preferences | `kicad_specgen_local.json → preferences` | Yes |
| Validation | Read-only | Yes |

### Scope boundaries

```text
Edit → Local Tokens...     Quick access — edits kicad_specgen_local.json tokens only
Edit → Configure           Page switch to this tab (same as clicking [Configure])

Configure tab:
  Local Machine subtab   → kicad_specgen_local.json (tokens + tools + setup state)
  Company & User subtab  → kicad_specgen_company.json + kicad_specgen_users.json
  Environments subtab    → kicad_specgen_company.json (environments) +
                           kicad_specgen_local.json (active_environment, active_user)
  Preferences subtab     → kicad_specgen_local.json → preferences
  Validation subtab      → read-only; no file writes
```

The Configure tab is the correct path for:
- Changing KSG_* tokens
- Switching active environment or active user
- Updating user info
- Editing company, client, and team data
- Setting UI preferences (theme)

`setup.py` remains the correct path for:
- Fresh machine installation
- Creating or updating `{KSG_APP_DIR}/.venv`
- Installing or upgrading dependency stages
- Platform-specific tool detection on a new OS
- Scripted or CI setup

### Status indicator

When the sidebar supports status icons:

```text
[Configure] ✓   All configuration valid
[Configure] ⚠   Warnings present (non-blocking)
[Configure] ✗   Errors present — setup may be required
```

---

## Local Machine Subtab

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [File]   [Edit]   [View]   [Help]                                                                          │
├───────────────┬────────────────────────────────────────────────────────────────────────────────────────────┤
│ SIDEBAR       │                                                                                            │
│               │ ┌─────────────────┬───────────────┬───────────────┬────────────────┬──────────────┐       │
│ [Project]     │ │▶ Local Machine  │ Company & User│ Environments  │ Preferences    │ Validation   │       │
│ [Variables]   │ └─────────────────┴───────────────┴───────────────┴────────────────┴──────────────┘       │
│ [Jobset]      │ ┌────────────────────────────────────────────────────────────────────────────────────────┐ │
│ [Report]      │ │ LOCAL MACHINE CONFIGURATION                                                            │ │
│               │ ├────────────────────────────────────────────────────────────────────────────────────────┤ │
│ [Logs]        │ │ Config File : ~/Library/Preferences/kicad/9.0/kicad_specgen_local.json          [Open] │ │
│ ───────────── │ │ Setup State : ✓ Complete (2026-06-03)                    [ Re-run Setup Wizard ]       │ │
│▶[Configure]   │ │ .venv       : {KSG_APP_DIR}/.venv  ✓ Active                                           │ │
│               │ └────────────────────────────────────────────────────────────────────────────────────────┘ │
│               │ ┌────────────────────────────────────────────────────────────────────────────────────────┐ │
│               │ │ KICAD-CLI                                                                              │ │
│               │ ├────────────────────────────────────────────────────────────────────────────────────────┤ │
│               │ │ Path    : /Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli         [ Browse ]   │ │
│               │ │ Source  : macOS application bundle                                                     │ │
│               │ │ Version : KiCad 9.0.3                                       [ Check ]  [ Re-detect ]  │ │
│               │ │ Status  : ✓ Working                                                                    │ │
│               │ └────────────────────────────────────────────────────────────────────────────────────────┘ │
│               │ ┌────────────────────────────────────────────────────────────────────────────────────────┐ │
│               │ │ LOCAL TOKENS  (kicad_specgen_local.json → tokens)                                      │ │
│               │ ├──────────────────────────────────────────┬───────────────────────────────┬────────────┤ │
│               │ │ Token                                    │ Value                         │ Status     │ │
│               │ ├──────────────────────────────────────────┼───────────────────────────────┼────────────┤ │
│               │ │ KSG_APP_DIR                              │ /Users/john/GitHub/ksg        │ ✓          │ │
│               │ │ KSG_SYSTEM_CONFIG_DIR                    │ ~/Library/Preferences/kicad/  │ ✓          │ │
│               │ │ KSG_COMPANY_DIR                          │ /Users/john/Engineering/Repo  │ ✓          │ │
│               │ │ KSG_USER_SPECGEN_DIR                     │ /Users/john/Engineering/Repo/ │ ✓          │ │
│               │ │                                          │ SpecGen/Users/12345           │            │ │
│               │ │ KSG_USER_COMMON_DIR                      │ /Users/john/Engineering/Repo/ │ ✓          │ │
│               │ │                                          │ SpecGen/Users/12345/common    │            │ │
│               │ ├──────────────────────────────────────────┴───────────────────────────────┴────────────┤ │
│               │ │  [ Add Token ]  [ Remove Selected ]  [ Browse... ]  [ Edit ]                          │ │
│               │ └────────────────────────────────────────────────────────────────────────────────────────┘ │
│               │ ┌────────────────────────────────────────────────────────────────────────────────────────┐ │
│               │ │ KICAD_COMMON.JSON (read-only reference)                                                │ │
│               │ ├────────────────────────────────────────────────────────────────────────────────────────┤ │
│               │ │ File : ~/Library/Preferences/kicad/9.0/kicad_common.json                   ✓          │ │
│               │ │ Vars : KICAD_SYMBOL_DIR, KICAD_FOOTPRINT_DIR, KICAD_TEMPLATE_DIR  (3 defined)         │ │
│               │ │ Note : SpecGen reads this file. It will not be modified during normal use.             │ │
│               │ └────────────────────────────────────────────────────────────────────────────────────────┘ │
│               │                                            [ Save Local Changes ]  [ Discard Changes ]    │
├───────────────┴────────────────────────────────────────────────────────────────────────────────────────────┤
│ STATUS: Configuration loaded | User: John Smith | Workspace: Shared/Repo | kicad-cli: KiCad 9.0.3        │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

**[ Re-run Setup Wizard ]** — Opens the Setup Wizard dialog in re-run mode,
pre-populated from the current configuration. See `SpecGen_Setup_Process.md` §8.

**[ Add Token ]** — Opens a small inline dialog to add a new `KSG_*` token.
Token name must match `^KSG_[A-Z0-9_]+$`. Value must be an absolute path.
Protected derived runtime tokens are rejected.

**[ Remove Selected ]** — Removes the selected token. Disabled when a required
token is selected (the five required tokens cannot be removed).

**[ Browse... ]** — Opens a folder picker for the selected token's path.

**[ Save Local Changes ]** — Validates all token values are absolute paths before
writing `kicad_specgen_local.json`. Shows inline error per offending row if
validation fails. After a successful save, reloads the effective token table
and refreshes the Project tab validation panel (if a project is open).

---

## Company and User Subtab

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [File]   [Edit]   [View]   [Help]                                                                          │
├───────────────┬────────────────────────────────────────────────────────────────────────────────────────────┤
│ SIDEBAR       │                                                                                            │
│               │ ┌─────────────────┬───────────────┬───────────────┬────────────────┬──────────────┐       │
│ [Project]     │ │  Local Machine  │▶Company & User│ Environments  │ Preferences    │ Validation   │       │
│ [Variables]   │ └─────────────────┴───────────────┴───────────────┴────────────────┴──────────────┘       │
│ [Jobset]      │ ┌──────────────────────────────────────────────┬─────────────────────────────────────────┐ │
│ [Report]      │ │ COMPANY CONFIGURATION                        │ SELECTED CLIENT / TEAM                  │ │
│               │ ├──────────────────────────────────────────────┼─────────────────────────────────────────┤ │
│ [Logs]        │ │ File : {KSG_COMPANY_DIR}/SpecGen/            │                                         │ │
│ ───────────── │ │        kicad_specgen_company.json            │ Select an item on the left to edit.     │ │
│▶[Configure]   │ │                                              │                                         │ │
│               │ │ ▼ Advanced Engineering  (AE)                 │                                         │ │
│               │ │   ▶ Medical Devices Inc  (medical_devices)   │                                         │ │
│               │ │   ▶ Aerospace Systems  (aerospace_systems)   │                                         │ │
│               │ │   ▶ Internal / Platform Development          │                                         │ │
│               │ │   + Add Client                               │                                         │ │
│               │ │   + Add Internal Team                        │                                         │ │
│               │ ├──────────────────────────────────────────────┴─────────────────────────────────────────┤ │
│               │ │ When "Medical Devices Inc" is selected:                                                │ │
│               │ │                                                                                        │ │
│               │ │  SELECTED CLIENT                                                                       │ │
│               │ │  Client ID   : [ medical_devices               ]                                       │ │
│               │ │  Client Name : [ Medical Devices Inc           ]                                       │ │
│               │ │  Root Path   : [ {KSG_COMPANY_DIR}/Clients/MedicalDevices  ]  [ Browse ]               │ │
│               │ │                                                                                        │ │
│               │ │  ▶ Hardware Team  (hardware)                                                           │ │
│               │ │  ▶ Manufacturing Engineering  (manufacturing)                                          │ │
│               │ │  + Add Team                                                                            │ │
│               │ └────────────────────────────────────────────────────────────────────────────────────────┘ │
│               │ ┌────────────────────────────────────────────────────────────────────────────────────────┐ │
│               │ │ USER PROFILES  (kicad_specgen_users.json)                                              │ │
│               │ ├────────────────────────────────────────────────────────────────────────────────────────┤ │
│               │ │  Worker ID   Display Name          Email                         Role        Active    │ │
│               │ │  ──────────  ───────────────────   ────────────────────────────  ──────────  ────────  │ │
│               │ │  12345    ▶  John Smith             john.smith@advancedeng.com   Sr. EE      ✓         │ │
│               │ │  23456       Jane Doe               jane.doe@advancedeng.com     Eng. Manager ✓        │ │
│               │ │                                                                                        │ │
│               │ │  [ Add User ]  [ Edit Selected ]  [ Deactivate ]                                       │ │
│               │ └────────────────────────────────────────────────────────────────────────────────────────┘ │
│               │                                    [ Save Company/User Changes ]  [ Discard Changes ]     │
├───────────────┴────────────────────────────────────────────────────────────────────────────────────────────┤
│ STATUS: Company: Advanced Engineering | 2 clients | 2 users                                               │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

**[ Add User ]** — Opens `AddUserDialog`. Collects the same fields as the
Setup Wizard user form. See `SpecGen_Setup_Process.md` §6.6.

**[ Edit Selected ]** — Opens an inline edit panel for the selected user row.

**[ Deactivate ]** — Sets `active = false` on the selected user. Does not
delete the record. A deactivated user cannot be set as the active user.

**[ Save Company/User Changes ]** — Writes `kicad_specgen_company.json`
and/or `kicad_specgen_users.json`. Validates before writing.

---

## Environments Subtab

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [File]   [Edit]   [View]   [Help]                                                                          │
├───────────────┬────────────────────────────────────────────────────────────────────────────────────────────┤
│ SIDEBAR       │                                                                                            │
│               │ ┌─────────────────┬───────────────┬───────────────┬────────────────┬──────────────┐       │
│ [Project]     │ │  Local Machine  │ Company & User│▶Environments  │ Preferences    │ Validation   │       │
│ [Variables]   │ └─────────────────┴───────────────┴───────────────┴────────────────┴──────────────┘       │
│ [Jobset]      │ ┌───────────────────────────────────────────────┬────────────────────────────────────────┐ │
│ [Report]      │ │ ENVIRONMENTS                                  │ SELECTED ENVIRONMENT                   │ │
│               │ ├───────────────────────────────────────────────┼────────────────────────────────────────┤ │
│ [Logs]        │ │                                               │                                        │ │
│ ───────────── │ │ ▶ medical_devices          [client]       ✦   │ Environment ID   : medical_devices     │ │
│▶[Configure]   │ │   medical_devices_hardware [client_group]     │ Type             : client              │ │
│               │ │   internal_tools           [internal_project] │ Client           : medical_devices     │ │
│               │ │   sandbox                  [sandbox]          │ Group            : (none)              │ │
│               │ │                                               │ Description      : Medical Devices     │ │
│               │ │  ✦ = active environment                       │                    client environment  │ │
│               │ │                                               │                                        │ │
│               │ │  [ Add ]  [ Remove ]  [ Set as Active ]       │  [ Edit ]                              │ │
│               │ └───────────────────────────────────────────────┴────────────────────────────────────────┘ │
│               │ ┌────────────────────────────────────────────────────────────────────────────────────────┐ │
│               │ │ ACTIVE SESSION  (kicad_specgen_local.json)                                             │ │
│               │ ├────────────────────────────────────────────────────────────────────────────────────────┤ │
│               │ │ Active Environment : [ medical_devices               ▼ ]  (from environments list)     │ │
│               │ │ Active User        : [ John Smith (12345)            ▼ ]  (from users list)            │ │
│               │ │                                                                                        │ │
│               │ │  Note: This is the machine-level default. Each SpecGen project selects its own         │ │
│               │ │  environment in the project .kicad_specgen file. Token priority at runtime:            │ │
│               │ │  USER → CLIENT → COMPANY → DEFAULT                                                     │ │
│               │ └────────────────────────────────────────────────────────────────────────────────────────┘ │
│               │                                    [ Save Environment Changes ]  [ Discard Changes ]      │
├───────────────┴────────────────────────────────────────────────────────────────────────────────────────────┤
│ STATUS: 4 environments defined | Active: medical_devices | User: John Smith                               │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

Environment type values: `client`, `client_group`, `internal_project`,
`sandbox`. See `SpecGen_Schema_Definitions.md` §3 for the enum.

**[ Add ]** — Adds a new environment to `kicad_specgen_company.json`.

**[ Remove ]** — Removes the selected environment. Disabled if the environment
is the currently active one.

**[ Set as Active ]** — Sets the selected environment as the machine-level
default in `kicad_specgen_local.json → active_environment`.

**[ Save Environment Changes ]** — Writes `kicad_specgen_company.json`
environments and `kicad_specgen_local.json` active session fields.

---

## Preferences Subtab

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [File]   [Edit]   [View]   [Help]                                                                          │
├───────────────┬────────────────────────────────────────────────────────────────────────────────────────────┤
│ SIDEBAR       │                                                                                            │
│               │ ┌─────────────────┬───────────────┬───────────────┬────────────────┬──────────────┐        │
│ [Project]     │ │  Local Machine  │ Company & User│ Environments  │▶Preferences    │ Validation   │        │
│ [Variables]   │ └─────────────────┴───────────────┴───────────────┴────────────────┴──────────────┘        │
│ [Jobset]      │ ┌────────────────────────────────────────────────────────────────────────────────────────┐ │
│ [Report]      │ │ APPEARANCE                                                                             │ │
│               │ ├────────────────────────────────────────────────────────────────────────────────────────┤ │
│ [Logs]        │ │                                                                                        │ │
│ ───────────── │ │ Theme                                                                                  │ │
│▶[Configure]   │ │                                                                                        │ │
│               │ │   ( ) System          Follow OS light/dark mode setting                                │ │
│               │ │   ( ) Light           Clean light background                                           │ │
│               │ │   (•) Dark            Dark background  ← current                                       │ │
│               │ │   ( ) Engineering Dark  High-contrast dark, EDA/PCB style                              │ │
│               │ │   ( ) ION Dark     ION brand — Obsidian Coal, Electric Cyan                            │ │
│               │ │   ( ) ION Light    ION brand — Clean Frost, Corporate Blue                             │ │
│               │ │                                                                                        │ │
│               │ │   Theme takes effect immediately when selected.                                        │ │
│               │ │   Shortcut: View → Theme selects a theme directly from any screen.                     │ │
│               │ │                                                                                        │ │
│               │ └────────────────────────────────────────────────────────────────────────────────────────┘ │
│               │ ┌────────────────────────────────────────────────────────────────────────────────────────┐ │
│               │ │ FUTURE PREFERENCES                                                                     │ │
│               │ ├────────────────────────────────────────────────────────────────────────────────────────┤ │
│               │ │ Additional preferences will appear here in future stages:                              │ │
│               │ │   Font size, log retention, default startup behavior,                                  │ │
│               │ │   recent project count, Markdown viewer size.                                          │ │
│               │ └────────────────────────────────────────────────────────────────────────────────────────┘ │
│               │                                                   [ Save Preferences ]  [ Discard ]        │
├───────────────┴────────────────────────────────────────────────────────────────────────────────────────────┤
│ STATUS: Theme: Dark | User: John Smith | Workspace: Shared/Repo                                            │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Theme selector** — Radio button group. Selecting a theme applies it
immediately to the running application without saving. The change is only
persisted when `[ Save Preferences ]` is clicked.

**[ Save Preferences ]** — Writes `kicad_specgen_local.json → preferences`.
Theme enum values: `system`, `light`, `dark`, `engineering_dark`,
`ion_dark`, `ion_light`. See `SpecGen_GUI_Theme.md` §3 for the
authoritative enum and `SpecGen_Schema_Definitions.md` §2 for the schema.

**[ Discard ]** — Reverts to the saved preference and re-applies the
previously active theme.

---

## Validation Subtab

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [File]   [Edit]   [View]   [Help]                                                                          │
├───────────────┬────────────────────────────────────────────────────────────────────────────────────────────┤
│ SIDEBAR       │                                                                                            │
│               │ ┌─────────────────┬───────────────┬───────────────┬────────────────┬──────────────┐       │
│ [Project]     │ │  Local Machine  │ Company & User│ Environments  │ Preferences    │▶Validation   │       │
│ [Variables]   │ └─────────────────┴───────────────┴───────────────┴────────────────┴──────────────┘       │
│ [Jobset]      │ ┌────────────────────────────────────────────────────────────────────────────────────────┐ │
│ [Report]      │ │ CONFIGURATION VALIDATION                                          [ Run Validation ]   │ │
│               │ ├────────────────────────────────────────────────────────────────────────────────────────┤ │
│ [Logs]        │ │ Last Run : 2026-06-13 09:14:22                                                         │ │
│ ───────────── │ └────────────────────────────────────────────────────────────────────────────────────────┘ │
│▶[Configure]   │ ┌────────────────────────────────────────────────────────────────────────────────────────┐ │
│               │ │ LOCAL CONFIGURATION                                                                    │ │
│               │ ├────────────────────────────────────────────────────────────────────────────────────────┤ │
│               │ │ ✓ kicad_specgen_local.json exists and is valid                                         │ │
│               │ │ ✓ schema_version is supported (1)                                                      │ │
│               │ │ ✓ All 5 required KSG_* tokens are present                                              │ │
│               │ │ ✓ All token values are absolute paths                                                  │ │
│               │ │ ✓ No protected derived tokens in token table                                           │ │
│               │ │ ✓ .venv found at {KSG_APP_DIR}/.venv and is active                                     │ │
│               │ │ ✓ kicad-cli found: /Applications/KiCad/KiCad.app/.../kicad-cli (KiCad 9.0.3)          │ │
│               │ └────────────────────────────────────────────────────────────────────────────────────────┘ │
│               │ ┌────────────────────────────────────────────────────────────────────────────────────────┐ │
│               │ │ COMPANY AND USER CONFIGURATION                                                         │ │
│               │ ├────────────────────────────────────────────────────────────────────────────────────────┤ │
│               │ │ ✓ KSG_COMPANY_DIR exists: /Users/john/Engineering/CompanyRepo                          │ │
│               │ │ ✓ SpecGen/ subfolder found                                                             │ │
│               │ │ ✓ kicad_specgen_company.json is valid (schema v1)                                      │ │
│               │ │ ✓ kicad_specgen_users.json is valid (schema v1)                                        │ │
│               │ │ ✓ Active user found: John Smith (12345)                                                │ │
│               │ │ ✓ Active environment found: medical_devices                                            │ │
│               │ │ ✓ active_environment references valid environment in company file                      │ │
│               │ └────────────────────────────────────────────────────────────────────────────────────────┘ │
│               │ ┌────────────────────────────────────────────────────────────────────────────────────────┐ │
│               │ │ OPTIONAL CHECKS                                                                        │ │
│               │ ├────────────────────────────────────────────────────────────────────────────────────────┤ │
│               │ │ ✓ KSG_USER_SPECGEN_DIR exists                                                          │ │
│               │ │ ✓ KSG_USER_COMMON_DIR exists                                                           │ │
│               │ │ ⚠ KSG_USER_COMMON_DIR is empty — no user assets found (non-blocking)                   │ │
│               │ │ ✓ kicad_common.json found: 3 environment vars available                                │ │
│               │ │ ✓ Recent projects: 2 entries (both valid)                                              │ │
│               │ └────────────────────────────────────────────────────────────────────────────────────────┘ │
│               │   Overall: ✓ Configuration valid (1 warning)                                              │
├───────────────┴────────────────────────────────────────────────────────────────────────────────────────────┤
│ STATUS: Validation passed with 1 warning | 2026-06-13 09:14:22                                            │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

**[ Run Validation ]** — Triggers `validation_service.run_config_validation()`.
Results refresh in place. No file writes occur.

**Result icons:**

```text
✓   Pass
⚠   Warning (non-blocking — configuration is usable)
✗   Error (blocking — must be resolved before project operations work)
```

---

## File Write Rules

All writes from the Configure tab go through `config_service`. The tab never
calls core module functions directly. If the underlying save implementation
changes, only `config_service` needs updating.

| Action | Writes To | Via |
|---|---|---|
| Save local tokens | `kicad_specgen_local.json → tokens` | `config_service.save_local_tokens()` |
| Save kicad-cli path | `kicad_specgen_local.json → tools` | `config_service.save_kicad_cli_path()` |
| Set active user | `kicad_specgen_local.json → active_user` | `config_service.save_active_session()` |
| Set active environment | `kicad_specgen_local.json → active_environment` | `config_service.save_active_session()` |
| Save preferences (theme) | `kicad_specgen_local.json → preferences` | `config_service.save_preferences()` |
| Save company identity | `kicad_specgen_company.json → company` | `config_service.save_company()` |
| Add/edit/remove client | `kicad_specgen_company.json → clients` | `config_service.save_company()` |
| Add/edit/remove environment | `kicad_specgen_company.json → environments` | `config_service.save_company()` |
| Add/edit/deactivate user | `kicad_specgen_users.json → users` | `config_service.save_user()` |
| Validation subtab | Nothing — read-only | — |

---

## Acceptance Criteria

```text
General
✓ Configure tab is always accessible in sidebar (even when setup incomplete)
✓ Configure tab shows correct content when no project is open
✓ Edit → Configure switches to this tab from any screen
✓ Status bar reflects current configuration state on all subtabs

Local Machine subtab
✓ Shows kicad_specgen_local.json path and setup state
✓ .venv path and status shown correctly
✓ Token table shows all KSG_* tokens with status indicators
✓ Add Token validates KSG_* naming rule before saving
✓ Remove Token is disabled when a required token is selected
✓ Browse sets absolute path for selected token
✓ Save Local Changes validates before writing — inline error on failure
✓ After save, effective token table reloads; Project tab validation refreshes

Company & User subtab
✓ Company tree shows company, clients, and teams
✓ Selecting a client shows its editable fields and team list
✓ User table shows all users with Worker ID, name, role, active status
✓ Add / Edit User opens AddUserDialog with correct fields
✓ Deactivate sets active = false; deactivated user greyed out in list
✓ Save Company/User Changes writes correct files

Environments subtab
✓ Environment list populates from kicad_specgen_company.json
✓ Active environment marked with ✦
✓ Remove is disabled when the selected environment is active
✓ Active Environment and Active User dropdowns save to kicad_specgen_local.json
✓ Token priority note (USER → CLIENT → COMPANY → DEFAULT) visible

Preferences subtab
✓ Theme radio buttons show all six themes
✓ Current active theme shown with filled radio (•) and "← current" label
✓ Selecting a theme applies it immediately (preview before save)
✓ Save Preferences writes kicad_specgen_local.json → preferences.theme
✓ Discard reverts to saved theme and re-applies it
✓ View → Theme shortcut navigates to Preferences subtab

Validation subtab
✓ Run Validation executes validation_service.run_config_validation()
✓ Results show ✓ ⚠ ✗ per check
✓ No files are written during validation
✓ Last Run timestamp updates after each run
```

---

*End of SpecGen Configure Tab Wireframes.*
