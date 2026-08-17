# KiCad SpecGen — Configuration and Token Framework

> **Document role:** Authoritative specification for configuration file
> ownership, token framework, file-open sequence, validation requirements,
> and implementation architecture.
> **Authority:** This document and `SpecGen_Schema_Definitions.md` together
> define the data model. `SpecGen_Schema_Definitions.md` provides the formal
> JSON schemas; this document provides the ownership rules, location rules,
> and behavioral specification.
> **Normative references:** `SpecGen_Schema_Definitions.md` (schemas),
> `SpecGen_Setup_Process.md` (setup), `SpecGen_Terminology.md` (names).
> **Living document policy:** This document must be reviewed and updated
> alongside `SpecGen_Schema_Definitions.md` whenever configuration fields
> are added, renamed, or removed in any design document or application code.
> **Status:** Updated — reflects decisions through Stage 0 documentation.

---

## 1. Purpose

This document defines the required configuration files, token framework, file ownership rules, and file-open sequence for KiCad SpecGen.

This document is intended to be used as an implementation specification for building KiCad SpecGen with Python 3 and PySide6.

The configuration model is based on one core rule:

```text
Local absolute path token definitions live in kicad_specgen_local.json.

Company, user, and project configuration files use token references.

The application resolves token references during file open, validation, and runtime operation.
```

This rule keeps machine-specific paths out of shared company files and project files while still allowing each user to resolve the same shared configuration on their own machine.

---

## 2. User Types and Installation Model

KiCad SpecGen supports two primary user types while maintaining a common application framework.

A project must be capable of operating in either standalone mode or repository mode without requiring modifications to the user's workspace structure. The mode is determined by the environment configuration and project location rather than by changes to the project itself.

### 2.1 Hobby User

A hobby user typically:

* Uses a single machine.
* Works from one or more local project locations.
* May maintain personal templates, libraries, and report assets.
* May choose to separate projects while sharing common user resources.
* Installs the application locally and seeds or links projects with application-provided templates and support files.
* Uses a standalone local SpecGen workspace. The `kicad_specgen_company.json` file is always created with company name "personal" during setup — no shared Git repository is required.

### 2.2 Professional User

A professional user typically:

* Works for a company or organization.
* Supports one or more internal teams, groups, or departments.
* Supports one or more external clients.
* Maintains company-wide templates, libraries, documentation, and report assets.
* Maintains client-specific templates, libraries, documentation, and report assets.
* May work on internal company projects, client projects, or sandbox projects.
* May store projects, company resources, and client resources in separate repositories.
* May share common company configuration across multiple users.
* May synchronize company and client information through a shared company repository.

---

## 3. Application Installation Model

The SpecGen application is always installed from the official Git repository.

Requirements:

* The application is cloned from the SpecGen Git repository.
* Users update the application by running `git pull` from `{KSG_APP_DIR}`.
* All default templates, support files, examples, and bundled resources are maintained within the application repository.
* Application updates must not overwrite user, company, client, or project data.
* User, company, client, and project data must be stored separately from the application repository.
* The Python virtual environment is always located at `{KSG_APP_DIR}/.venv` and is excluded from the Git repository.

This separation ensures that application updates remain independent from company and project configuration.

---

## 4. Ownership Terminology

To eliminate ambiguity, the following terms have specific meanings throughout SpecGen.

### 4.1 User

The individual engineer, designer, employee, contractor, or hobby user using SpecGen.

Examples:

* John Smith
* Jane Doe
* Contractor A
* Hobby User A

### 4.2 Company

The organization, team, or personal shared-work root that owns shared SpecGen resources.

For a professional user, this is normally the user's company or organization.

For a hobby or standalone user, this may be a local personal SpecGen data folder.

Examples:

* Advanced Engineering
* ABC Electronics
* Internal R&D Organization
* Personal SpecGen Workspace

Company resources may include templates, logos, reusable report content, libraries, and shared configuration.

### 4.3 Client

An external organization for which the user's company performs work.

Examples:

* Client A
* Medical Devices Inc.
* Aerospace Systems Ltd.

Client resources belong to the external organization.

### 4.4 Client Group

A subdivision within a client organization.

Examples:

* Hardware Team
* Product Development Group
* Manufacturing Engineering
* Program Alpha Team

A user may perform work for multiple groups within the same client organization.

### 4.5 Project

The specific engineering effort being performed.

Examples:

* Motor Controller Rev B
* Sensor Gateway
* Production Test Fixture

Projects may belong to:

* The user's company.
* A client organization.
* A specific client group.
* A user's personal, sandbox, or experimental environment.

Recommended conceptual model:

```text
User
  └─ Company / Shared SpecGen Data Root
       ├─ Internal Team / Group
       │    └─ Project
       │
       └─ Client
            ├─ Client Group / Team
            │    └─ Project
            │
            └─ Client Group / Team
                 └─ Project
```

The token naming system shall make these ownership boundaries obvious to users configuring environments.

---

## 5. Configuration File Inventory

KiCad SpecGen uses the following configuration and input files.

| File                                 | Owner                       | Location                                     | Purpose                                                                                                             |
| ------------------------------------ | --------------------------- | -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `kicad_specgen_local.json`           | SpecGen local machine       | KiCad user configuration folder              | Stores local machine paths, tool paths, setup state, recent projects, active user, and active environment.          |
| `kicad_common.json`                  | KiCad                       | KiCad user configuration folder              | Optional read-only source of KiCad environment variables and user configuration.                                    |
| `SpecGen/kicad_specgen_company.json` | SpecGen shared/company data | Under `{KSG_COMPANY_DIR}/SpecGen/`           | Stores company, client, team, shared path references, shared templates, shared assets, and environment definitions. |
| `SpecGen/kicad_specgen_users.json`   | SpecGen shared/company data | Under `{KSG_COMPANY_DIR}/SpecGen/`           | Stores minimal user directory information used by SpecGen.                                                          |
| `<name>.kicad_specgen`               | SpecGen project             | Under `{KSG_PROJECT_SPECGEN_DIR}/` folder    | Stores project-specific SpecGen state and report/FAB recipe data using token references.                            |
| `<project>.kicad_pro`                | KiCad project               | Under `{KICAD_PROJECT_DIR}/` folder          | KiCad project file and source of KiCad text variables.                                                              |
| `<name>.kicad_jobset`                | KiCad jobset                | Ideally under `specgen/` or `common/` folder | Defines KiCad jobset destinations and generated output files.                                                       |

---

# 6. Token Framework

## 6.1 Token Definitions and Token References

SpecGen separates path data into two categories.

```text
Token definitions
  Absolute local paths stored in kicad_specgen_local.json.

Token references
  Portable paths stored in company, user, and project configuration files.
```

Example token definition in `kicad_specgen_local.json`:

```json
{
  "tokens": {
    "KSG_COMPANY_DIR": "/Users/john/Engineering/CompanyRepo"
  }
}
```

Example token reference in `kicad_specgen_company.json`:

```json
{
  "paths": {
    "company_templates": "{KSG_COMPANY_DIR}/SpecGen/templates"
  }
}
```

Example token reference in a project `.kicad_specgen` file:

```json
{
  "files": {
    "report_css": "{KSG_COMPANY_DIR}/SpecGen/assets/report_style.css" 
  }
}
```

Resolved result on this user’s machine:

```text
/Users/john/Engineering/CompanyRepo/SpecGen/assets/report_style.css
```

## 6.2 Token Storage Rule

Only `kicad_specgen_local.json` stores local absolute path definitions.

The following files must use token references and must not contain local
machine absolute paths under any circumstances:

* `SpecGen/kicad_specgen_company.json`
* `SpecGen/kicad_specgen_users.json`
* Project `.kicad_specgen` files

Every file reference in a `.kicad_specgen` project must resolve to a path
rooted at a defined `KSG_*` token. There are no exceptions.

### Handling files outside a tokenized path

If a user attempts to reference a file that does not reside under any
existing `KSG_*` token root, SpecGen shall not store an absolute path.
Instead, SpecGen offers two options:

```text
Option A — Create a new token:
  SpecGen suggests a KSG_* token name for the file's parent directory.
  The user confirms or edits the name.
  The absolute path is saved to kicad_specgen_local.json → tokens.
  The project file stores the token reference.
  On another machine where that token is absent: Missing Tokens dialog fires.

Option B — Copy the file into a tokenized location:
  SpecGen copies the file to a location under an existing token root
  (e.g. {KSG_PROJECT_SPECGEN_DIR}/local_assets/ or {KSG_USER_COMMON_DIR}/...).
  The project file stores the token reference to the copied file.
  The file travels with the project or user assets and is portable.
```

Option A is preferred when the file is shared across projects (e.g. a company
logo stored in a company folder outside the repo). Option B is preferred for
one-off project-specific files.

### Automatic tokenization on selection (PathField)

File and folder pickers in the UI are the `PathField` widget
(`ui/widgets/path_field.py`). In token-aware mode, when the user selects a
path, the widget automatically rewrites the chosen absolute path to a
`{TOKEN}`-relative reference before storing it, using
`core.token_resolver.tokenize_path()`:

```text
Selected:  /Users/me/CompanyRepo/SpecGen/common/logo.png
Stored:    {KSG_COMPANY_DIR}/SpecGen/common/logo.png
```

Rules:
- The widget may be given an **anchor token** (the token the field is
  conceptually tied to, e.g. the company logo field is anchored to
  `KSG_COMPANY_DIR`). If the selected path is under the anchor's directory,
  the anchor token is used.
- Otherwise the **longest matching token directory** wins, so a nested token
  (e.g. `KSG_COMPANY_SPECGEN_DIR`) is preferred over a broader one
  (`KSG_COMPANY_DIR`).
- If the selection is **not** under the anchor's directory, the field signals
  an anchor violation so the subtab can warn the user (e.g. "the logo must
  live inside the company folder"), and stores the best available
  tokenization (or, if nothing matches, the raw path — at which point the
  "files outside a tokenized path" flow above applies).
- The file dialog is **seeded** from the resolved absolute path of the current
  value, or from the anchor token's directory when the field is empty, so the
  picker opens in the expected location.

This is the mechanism by which path fields satisfy the rule that company,
user, and project paths are stored in token notation rather than as absolute
paths. The reverse operation (token → absolute) is `resolve_ref()`.

### Skipped tokens

When a token cannot be resolved and the user chooses to skip it (rather than
provide a path or remove the reference), the skip is recorded locally:

```text
kicad_specgen_local.json → skipped_tokens: ["TOKEN_NAME", ...]
```

A skipped token is machine-local state. It suppresses the Missing Tokens
dialog for that token on this machine until the user clears it. It does not
affect other users.

A skipped token shows in the Project tab with a ⚠ badge. The user can
clear the skip from the Project tab to re-trigger resolution.

### Repository files not found

If a token resolves correctly but the referenced file is not found on disk
(e.g. a company template not yet pulled from a shared repository), SpecGen
shows an informational warning:

```text
"File not found: {KSG_COMPANY_DIR}/SpecGen/templates/title_page.md
 If you are using a shared repository, ensure you have the latest
 version pulled. Use Refresh after pulling to re-check."
```

SpecGen does not perform any git operations. The user pulls the repository
manually and uses View → Refresh to re-trigger resolution.

## 6.3 Stored Token Naming Rule

Stored local tokens in `kicad_specgen_local.json` shall use the `KSG_*` namespace.

Recommended validation rule:

```text
^KSG_[A-Z0-9_]+$
```

All stored token values must be absolute paths.

## 6.4 Reserved Token Prefixes

Token names must clearly identify ownership and scope.

| Prefix          | Scope                                                  |
| --------------- | ------------------------------------------------------ |
| `KSG_USER_*`    | Individual user resources.                             |
| `KSG_COMPANY_*` | Company, organization, or standalone shared resources. |
| `KSG_CLIENT_*`  | External client resources.                             |
| `KSG_PROJECT_*` | SpecGen-owned project resources.                       |
| `KSG_APP_*`     | SpecGen application installation resources.            |
| `KSG_SYSTEM_*`  | OS-specific configuration resources.                   |
| `KICAD_*`       | KiCad-owned project and jobset resources.              |

## 6.5 Required Local Tokens

The following tokens are required in `kicad_specgen_local.json` for all installations.

| Token                   | Required For     | Description                                                                                                                                        |
| ----------------------- | ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| `KSG_APP_DIR`           | standalone, repo | Root folder of the installed SpecGen application repository. Used to find bundled defaults, examples, setup scripts, and application resources.    |
| `KSG_SYSTEM_CONFIG_DIR` | standalone, repo | OS-specific KiCad user configuration folder containing `kicad_specgen_local.json`.                                                                 |
| `KSG_COMPANY_DIR`       | standalone, repo | Root folder containing the shared or standalone `SpecGen/` data folder. May be a Git repository in repo mode or a local folder in standalone mode. |
| `KSG_USER_SPECGEN_DIR`  | standalone, repo | Root folder for user-owned SpecGen resources. Recommended location: `{KSG_COMPANY_DIR}/SpecGen/Users/<worker_id>/` where `<worker_id>` is the user's worker_id string. |
| `KSG_USER_COMMON_DIR`   | standalone, repo | User-owned shared templates, CSS, logos, report assets, and reusable resources. Recommended location: `{KSG_USER_SPECGEN_DIR}/common/`. |

Recommended relationship:

```text
KSG_COMPANY_DIR
└─ SpecGen/
   └─ Users/
      └─ <worker_id>/
         ├─ common/
         ├─ reports/
         ├─ templates/
         └─ assets/
```

Recommended token expansion (values stored as absolute paths in `kicad_specgen_local.json`):

```text
KSG_USER_SPECGEN_DIR = {KSG_COMPANY_DIR}/SpecGen/Users/<worker_id>
KSG_USER_COMMON_DIR  = {KSG_USER_SPECGEN_DIR}/common
```

Where `<worker_id>` is the user's `worker_id` string from `kicad_specgen_users.json`.
Note: the expansion shown above uses token notation for clarity, but the actual
values written to `kicad_specgen_local.json` must be resolved absolute paths.

## 6.6 Optional Local Tokens

The local configuration may define additional absolute path tokens when needed.

Examples:

| Token                    | Description                                                  |
| ------------------------ | ------------------------------------------------------------ |
| `KSG_APP_COMMON_DIR`     | Optional explicit path to application-provided common files. |
| `KSG_USER_REPORTS_DIR`   | User-owned generated or reusable reports folder.             |
| `KSG_USER_TEMPLATES_DIR` | User-owned templates folder.                                 |
| `KSG_USER_ASSETS_DIR`    | User-owned images, logos, and reusable assets folder.        |
| `KSG_SYSTEM_LOG_DIR`     | Local machine log output folder.                             |
| `KSG_SYSTEM_CACHE_DIR`   | Local cache folder.                                          |

Optional tokens should point to folders or root paths, not individual normal report files.

## 6.7 Protected Derived Runtime Tokens

The following tokens are computed at runtime and must not be stored as token definitions in `kicad_specgen_local.json`.

| Token                     | Derived From                                 | Description                                                                                      |
| ------------------------- | -------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| `SPECGEN_PROJECT_FILE`    | Opened `.kicad_specgen` file                 | Absolute path to the active SpecGen project file.                                                |
| `KSG_PROJECT_SPECGEN_DIR` | Parent folder of `SPECGEN_PROJECT_FILE`      | Project-local `specgen/` folder containing the active `.kicad_specgen` file.                     |
| `KICAD_PROJECT_DIR`       | Parent folder of `KSG_PROJECT_SPECGEN_DIR`   | KiCad project folder containing the active `.kicad_pro`.                                         |
| `GIT_PROJECT_DIR`         | Git root discovered from `KICAD_PROJECT_DIR` | Git repository root for the active project. In standalone mode, defaults to `KICAD_PROJECT_DIR`. |
| `JOBSET_OUTPUT_DIR`       | Active `.kicad_jobset` output settings       | Root folder for generated jobset outputs.                                                        |
| `FAB_OUTPUT_DIR`          | Project/FAB settings and active jobset       | From `fabrication.output_dir` if set in the project `.kicad_specgen`; else defaults to `{JOBSET_OUTPUT_DIR}/fab/`. |

The project-local `specgen/` directory token is named:

```text
KSG_PROJECT_SPECGEN_DIR
```

This folder is owned by SpecGen, not KiCad.

## 6.8 Token Reference Format

Token references use braces:

```text
{TOKEN_NAME}/relative/path
```

Examples:

```text
{KSG_COMPANY_DIR}/SpecGen/templates/title_page.md
{KSG_USER_COMMON_DIR}/logos/default_logo.png
{KSG_PROJECT_SPECGEN_DIR}/release_default.kicad_jobset
{KICAD_PROJECT_DIR}/background/release_notes.md
{JOBSET_OUTPUT_DIR}/sch/BoardA.pdf
```

## 6.9 Missing Token Handling

If a token reference cannot be resolved, SpecGen shall show a Missing Tokens
dialog. See `SpecGen_GUI_Menus.md` for the full dialog wireframe and behavior.

The dialog shall show:

* Missing token name.
* File or setting where the token is used.
* Suggested repair action.

User options:

```text
Provide path   → User enters or browses to an absolute path.
                 SpecGen saves it as kicad_specgen_local.json → tokens.<TOKEN_NAME>.
                 The project file is not modified — the token reference remains as-is.

Skip           → Suppresses the dialog for this token on this machine.
                 Saved to kicad_specgen_local.json → skipped_tokens array.
                 Fires again on next project open.
                 Shown in Project tab with a ⚠ "skipped" badge.

Remove         → Deletes the token reference from the project .kicad_specgen file.
                 Sets the project dirty flag.
                 User must save the project for the removal to take effect.
                 Other users will not see a Missing Tokens dialog for this
                 reference because it no longer exists in the project file.

Cancel         → Closes the dialog. Unresolved tokens remain unresolved.
                 The project opens in a degraded state.
```

The project `.kicad_specgen` file is never rewritten with absolute paths.
Token references remain portable regardless of which option the user chooses.

---

# 7. Application Startup and Token Resolution Sequence

The authoritative startup sequence is defined in `SpecGen_Setup_Process.md` §4.
That document is the normative reference for startup detection, setup banner
behavior, Defer mode, and the six-step file-open flow.

The summary below covers the token resolution aspects relevant to this framework.

## 7.1 Startup Summary

```text
Step 1.  Detect KICAD_COMMON_DIR for the current OS and KiCad version.

Step 2.  Check kicad_specgen_local.json exists and setup_complete = true.
         If not: show Setup Required banner. Offer Run Setup or Defer.
         In Defer mode: Configure tab is accessible; project operations disabled.

Step 3.  Load kicad_specgen_local.json.
         Apply preferences.theme immediately (before GUI is shown).
         Load local absolute tokens (KSG_APP_DIR, KSG_SYSTEM_CONFIG_DIR,
         KSG_COMPANY_DIR, KSG_USER_SPECGEN_DIR, KSG_USER_COMMON_DIR).
         Read kicad_common.json environment.vars as the lowest-priority token source.

Step 4.  Load kicad_specgen_company.json using KSG_COMPANY_DIR.

Step 5.  Load kicad_specgen_users.json using KSG_COMPANY_DIR.

Step 6.  If last_session.specgen_project exists: open the project file.
           Derive protected runtime tokens (SPECGEN_PROJECT_FILE,
           KSG_PROJECT_SPECGEN_DIR, KICAD_PROJECT_DIR, GIT_PROJECT_DIR).
           Expand token references across company, user, and project data.
           Resolve and validate all token references.
           Trigger Missing Tokens dialog for any unresolved references.
           Parse the active .kicad_jobset file (see §7.2).
           Check for jobset/report reconciliation issues (see §7.3).
         If no last project: show empty workspace; project operations await
         File → New or File → Open.

Step 7.  Populate the GUI.
```

## 7.2 Jobset Parse Timing

The active `.kicad_jobset` file is parsed **at startup** when a project is
restored from `last_session`, and at **project open** in all other cases.
It is parsed after all config files (local, company, users, project) have
finished loading. It is not parsed lazily on first tab display.

Parsing reads destination IDs and output paths from the KiCad-owned
`.kicad_jobset` file. SpecGen never writes to this file.

`JOBSET_OUTPUT_DIR` is derived from the first output entry's
`settings.output_path` in the parsed jobset.

## 7.3 Jobset/Report Reconciliation

Because the `.kicad_jobset` is KiCad-owned and may be edited outside SpecGen,
a reconciliation check runs at three points:

```text
1. Project open / startup restore
2. Project save
3. Project close
```

The check compares the currently parsed jobset destination IDs and output paths
against the destination references stored in the project `.kicad_specgen`
(jobset destinations, report page definitions, fabrication destinations).

If a mismatch is detected (destination removed, output path changed):

```text
Show a warning dialog:
  "The active jobset has changed since this project was last saved.
   Some report or fabrication references may no longer be valid."

Options:
  [ Review Now ]   → Switch to Jobset tab, highlight stale destinations
  [ Defer ]        → Save with warnings noted in last_session (machine-local);
                     fires again on next open
  [ Cancel ]       → Cancel the save/close operation (project remains open)
```

The `.kicad_specgen` project file is not modified by the reconciliation check
itself. Changes require explicit user action in the Jobset or Report tab.

Reconciliation warnings are stored in `kicad_specgen_local.json → last_session`
as a transient machine-local flag, not in the portable project file.

## 7.4 Token Resolution Priority

When building the effective token table, sources are applied in this order
(lowest to highest priority):

```text
1. kicad_common.json environment.vars       (KiCad-native vars — lowest)
2. kicad_specgen_local.json tokens          (KSG_* absolute paths)
3. kicad_specgen_company.json resolved paths
4. kicad_specgen_users.json resolved paths
5. Protected derived runtime tokens         (computed — highest)
```

At project level, per-project token selection follows:

```text
USER → CLIENT → COMPANY → DEFAULT
```

---

# 8. File Chapter: `kicad_specgen_local.json`

## 8.1 Purpose

`kicad_specgen_local.json` is the local machine configuration file for KiCad SpecGen.

It stores:

* Local machine paths.
* Application installation paths.
* Setup state.
* Recent projects.
* Active user.
* Active environment.
* Local tool paths.
* Machine-specific preferences.
* Local absolute token definitions.

This file is required.

## 8.2 Location

`kicad_specgen_local.json` is stored in the same OS-specific configuration location used by KiCad for user configuration data.

Typical examples:

```text
Windows:
%APPDATA%\kicad\9.0\kicad_specgen_local.json

Linux:
~/.config/kicad/9.0/kicad_specgen_local.json

macOS:
~/Library/Preferences/kicad/9.0/kicad_specgen_local.json
```

Where `9.0` is the KiCad configuration version.

## 8.3 Ownership

This file is owned by SpecGen and is local to one user and one machine.

It must never be treated as the company source of truth.

It may contain absolute paths.

It should not be committed into a shared company or project repository.

## 8.4 Required Contents

Required top-level sections:

| Section              | Purpose                                            |
| -------------------- | -------------------------------------------------- |
| `schema_version`     | Local config schema version.                       |
| `active_user`        | Current user ID from `kicad_specgen_users.json`.   |
| `active_environment` | Current environment ID from company configuration. |
| `tools`              | Local executable paths such as `kicad-cli`.        |
| `tokens`             | Local absolute path token definitions.             |
| `setup`              | Setup/bootstrap state.                             |
| `last_session`       | Project reference fields for the last opened project (for restore on next launch), plus window_geometry. Per-project state (active tab, environment) is stored in the .kicad_specgen file itself. |
| `recent_projects`    | Up to 10 recently opened SpecGen projects (most recent first). Each entry contains only the fields needed to populate the Open Recent submenu without re-opening the file: `specgen_project`, `project_name`, `display_name`, `kicad_project_dir`, `last_opened_at`. |
| `skipped_tokens`     | Array of token names suppressed on this machine via the Missing Tokens dialog Skip option. Machine-local; does not affect other users. |
| `preferences`        | UI preferences. Currently: `theme` (see `SpecGen_GUI_Theme.md` for theme specifications and enum values). |

## 8.5 Recent Projects

`recent_projects` is local session state and belongs only in `kicad_specgen_local.json`.

Rules:

```text
Keep up to 10 entries.
Each entry must reference a unique absolute specgen_project path.
When a project is opened, move it to the top.
If the list grows beyond 10 entries, remove the oldest entry.
If a recent project file no longer exists, show a warning when selected.
Do not store recent projects in the project `.kicad_specgen` file.
```

## 8.6 Example

See `SpecGen_Schema_Definitions.md` §2 for the complete schema and full example.

Key structural rules:
- `last_session` carries the project-reference fields plus `window_geometry`
  (machine-specific window position). Per-project state (`active_tab`,
  `workspace.environment`) is in the `.kicad_specgen` file and is not
  duplicated here.
- `recent_projects` items carry only the five fields needed to populate
  the Open Recent submenu without re-opening each file.

```json
{
  "schema_version": 1,
  "active_user":        "12345",
  "active_environment": "medical_devices",

  "tools": {
    "kicad_cli":        "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli",
    "kicad_cli_source": "detected_macos_app",
    "kicad_version":    "9.0.3"
  },

  "tokens": {
    "KSG_APP_DIR":          "/Users/john/GitHub/kicad-specgen",
    "KSG_SYSTEM_CONFIG_DIR":"/Users/john/Library/Preferences/kicad/9.0",
    "KSG_COMPANY_DIR":      "/Users/john/Engineering/CompanyRepo",
    "KSG_USER_SPECGEN_DIR": "/Users/john/Engineering/CompanyRepo/SpecGen/Users/12345",
    "KSG_USER_COMMON_DIR":  "/Users/john/Engineering/CompanyRepo/SpecGen/Users/12345/common"
  },

  "setup": {
    "setup_complete":      true,
    "last_setup_run":      "2026-06-03T09:00:00",
    "last_setup_platform": "macos",
    "dependency_stage":    "stage2"
  },

  "last_session": {
    "specgen_project":   "/Users/john/Engineering/Projects/BoardA/specgen/BoardA.kicad_specgen",
    "project_name":      "BoardA",
    "display_name":      "Medical Devices BoardA",
    "kicad_project_dir": "/Users/john/Engineering/Projects/BoardA",
    "window_geometry":   { "x": 100, "y": 100, "width": 1400, "height": 900 },
    "last_opened_at":    "2026-06-03T14:32:09"
  },

  "recent_projects": [
    {
      "specgen_project":   "/Users/john/Engineering/Projects/BoardA/specgen/BoardA.kicad_specgen",
      "project_name":      "BoardA",
      "display_name":      "Medical Devices BoardA",
      "kicad_project_dir": "/Users/john/Engineering/Projects/BoardA",
      "last_opened_at":    "2026-06-03T14:32:09"
    },
    {
      "specgen_project":   "/Users/john/Engineering/Projects/CtrlBoard/specgen/CtrlBoard.kicad_specgen",
      "project_name":      "CtrlBoard",
      "display_name":      "Control Board Rev C",
      "kicad_project_dir": "/Users/john/Engineering/Projects/CtrlBoard",
      "last_opened_at":    "2026-06-01T11:15:00"
    }
  ],

  "skipped_tokens": [],

  "preferences": {
    "theme": "dark"
  }
}
```

## 8.7 Application Use

The application uses `kicad_specgen_local.json` to:

* Find `kicad-cli`.
* Locate the shared or standalone SpecGen data root.
* Open company and user configuration files.
* Restore the last opened project.
* Populate the File → Open Recent menu.
* Resolve local absolute path tokens.
* Apply the active UI theme at startup from `preferences.theme` before the
  GUI is shown. See `SpecGen_GUI_Theme.md` for theme specifications.
* Save local setup and preference changes.
* Store machine-specific values that must not be written into project files.
* Track skipped tokens (`skipped_tokens`) and reconciliation warnings
  (`last_session`) as machine-local transient state.

## 8.8 Dirty Flag for Local Configuration

`kicad_specgen_local.json` has its own dirty state, tracked in
`app_state.dirty_local`. It is separate from `app_state.dirty_project`.

| Event | `dirty_local` |
|---|---|
| User edits a token in `LocalTokensDialog` or Configure tab Local Machine subtab | Set to `True` |
| User edits kicad-cli path in `KicadCliDialog` | Set to `True` |
| User changes active environment or user in Configure tab Environments subtab | Set to `True` |
| User changes theme in Preferences subtab | Set to `True` |
| `config_service` writes `kicad_specgen_local.json` successfully | Reset to `False` |
| User clicks `[ Discard Changes ]` in Configure tab | Reset to `False`; reload from disk |
| User clicks `[ Cancel ]` in `LocalTokensDialog` or `KicadCliDialog` | Reset to `False`; no write |

The dirty flag for the local config does **not** affect the application close
prompt. Unsaved local config changes are discarded silently on exit — the user
is expected to use the `[ Save ]` button in the relevant dialog or subtab. This
is consistent with the behavior of system preference panels on all three
supported platforms.

`window_geometry` changes (resize, move) do not set `dirty_local`. They are
written to `kicad_specgen_local.json → last_session` on exit without prompting.

---

# 9. File Chapter: `kicad_common.json`

## 9.1 Purpose

`kicad_common.json` is KiCad’s user configuration file.

SpecGen may read this file to inspect KiCad environment variables and configuration paths.

## 9.2 Ownership

This file is owned by KiCad.

SpecGen shall treat it as read-only during normal application operation.

SpecGen may modify this file during setup only if the user approves.

Before writing to `kicad_common.json`, SpecGen must create a timestamped backup:

```text
kicad_common.json.bak_YYYYMMDD_HHMMSS
```

## 9.3 Application Use

SpecGen may use `kicad_common.json` to:

* Display KiCad environment variables in the Project tab.
* Compare KiCad paths to SpecGen tokens.
* Help locate KiCad user configuration folders.
* Validate KiCad-related paths.

SpecGen-specific local path tokens belong in `kicad_specgen_local.json`.

---

# 10. File Chapter: `SpecGen/kicad_specgen_company.json`

## 10.1 Purpose

`kicad_specgen_company.json` stores shared company, client, team, template, asset, and environment information.

This file is the shared organizational configuration file.

It does not store local absolute path token definitions.

It stores token references that resolve through `kicad_specgen_local.json`.

## 10.2 Location

The file is located at:

```text
{KSG_COMPANY_DIR}/SpecGen/kicad_specgen_company.json
```

The resolved path is determined by expanding `KSG_COMPANY_DIR` from `kicad_specgen_local.json`.

## 10.3 Ownership

This file is owned by SpecGen.

For a professional workflow, this file may be stored in a Git repository shared by multiple users.

For a standalone workflow, this file may be stored in a local user folder.

SpecGen should be the authoritative writer for this file. Manual edits are not recommended and should be validated by SpecGen before use.

## 10.4 Top-Level Sections

See `SpecGen_Schema_Definitions.md` §3 for the complete JSON schema, field
definitions, validation rules, and a full example.

| Section | Required | Purpose |
|---|---|---|
| `schema_version` | Yes | Company config schema version. |
| `company` | Yes | Company identity (`name`, `description`, `website`, `address`, `logo`). Single-company model — `name` is the identifier; there is no `company_id`. |
| `departments` | No | Internal department definitions keyed by `dept_id`. Each department contains `teams` keyed by `team_id`. |
| `paths` | No | Company-wide shared path references using token notation. |
| `clients` | No | External client definitions keyed by `client_id`. Each client contains `projects` keyed by `project_id`; each project has a `status` (Stage 1: `active` \| `inactive`). |
| `environments` | No | Logical environment definitions used by project files. |
| `templates` | No | Shared template token references. |
| `assets` | No | Shared logo, CSS, and reusable asset token references. |

**Note on nested `paths`:** The top-level `paths` section holds company-wide
shared path references. The `paths` key also appears nested within individual
`departments` entries, `teams` entries, `clients` entries, and `projects`
entries for scope-specific path references. The top-level `paths` is for
resources shared across all departments and clients; nested `paths` are for
resources specific to that department, team, client, or project.

## 10.5 Path Rules

Paths in this file should be token references.

Good:

```json
{
  "paths": {
    "company_templates": "{KSG_COMPANY_DIR}/SpecGen/templates"
  }
}
```

Avoid:

```json
{
  "paths": {
    "company_templates": "/Users/john/Engineering/CompanyRepo/SpecGen/templates"
  }
}
```

Absolute paths in this file make the company configuration non-portable across users and machines.

## 10.6 Example

```json
{
  "schema_version": 1,

  "company": {
    "name": "Advanced Engineering",
    "description": "Engineering consulting and product development",
    "website": "https://advanced-eng.example.com",
    "address": {
      "street1": "100 Innovation Way",
      "suite": "200",
      "city": "Austin",
      "state": "TX",
      "zip": "78701",
      "country": "USA"
    },
    "logo": "{KSG_COMPANY_DIR}/SpecGen/common/logo.png"
  },

  "departments": {
    "platform_development": {
      "name": "Platform Development",
      "teams": {
        "core": {
          "name": "Core Platform",
          "paths": {
            "team_docs": "{KSG_COMPANY_DIR}/Internal/PlatformDevelopment/core/docs"
          }
        }
      }
    },
    "engineering_tools": {
      "name": "Engineering Tools",
      "teams": {
        "automation": { "name": "Automation" }
      }
    }
  },

  "paths": {
    "company_root": "{KSG_COMPANY_DIR}",
    "company_specgen": "{KSG_COMPANY_DIR}/SpecGen",
    "company_templates": "{KSG_COMPANY_DIR}/SpecGen/templates",
    "company_assets": "{KSG_COMPANY_DIR}/SpecGen/assets"
  },

  "clients": {
    "medical_devices": {
      "name": "Medical Devices Inc",
      "paths": {
        "client_root": "{KSG_COMPANY_DIR}/Clients/MedicalDevices"
      },
      "projects": {
        "pacemaker_mk2": {
          "name": "Pacemaker Mk II",
          "status": "active",
          "paths": {
            "project_docs": "{KSG_COMPANY_DIR}/Clients/MedicalDevices/pacemaker_mk2/docs"
          }
        },
        "legacy_monitor": {
          "name": "Legacy Monitor",
          "status": "inactive"
        }
      }
    },

    "aerospace_systems": {
      "name": "Aerospace Systems Ltd",
      "projects": {
        "avionics_v3": { "name": "Avionics v3", "status": "active" }
      }
    }
  },

  "environments": {
    "medical_devices": {
      "type": "client",
      "client": "medical_devices",
      "description": "Medical Devices client environment"
    },
    "pacemaker": {
      "type": "client_group",
      "client": "medical_devices",
      "project": "pacemaker_mk2",
      "description": "Pacemaker Mk II project environment"
    },
    "internal_tools": {
      "type": "internal_project",
      "department": "engineering_tools",
      "team": "automation",
      "description": "Internal engineering tools environment"
    },
    "sandbox": {
      "type": "sandbox",
      "description": "Local sandbox and experimental projects"
    }
  },

  "templates": {
    "default_title_page": "{KSG_COMPANY_DIR}/SpecGen/templates/title_page.md",
    "default_end_page": "{KSG_COMPANY_DIR}/SpecGen/templates/end_page.md"
  },

  "assets": {
    "default_report_css": "{KSG_COMPANY_DIR}/SpecGen/assets/report_style.css",
    "default_bom_css": "{KSG_COMPANY_DIR}/SpecGen/assets/bom_style.css",
    "default_logo": "{KSG_COMPANY_DIR}/SpecGen/common/logo.png"
  }
}
```

## 10.7 Application Use

The application uses `kicad_specgen_company.json` to:

* Populate environment choices.
* Identify company, client, and client-group metadata.
* Locate shared templates and assets.
* Populate default project configuration values.
* Validate project references.
* Provide report metadata and template defaults.

---

# 11. File Chapter: `SpecGen/kicad_specgen_users.json`

## 11.1 Purpose

`kicad_specgen_users.json` stores minimal user directory information used by SpecGen.

This file supports:

* User selection.
* Report attribution.
* Environment filtering.
* Basic permissions for shared SpecGen configuration.
* User-owned resource folders.

It is not intended to be a full HR database.

## 11.2 Location

The file is located at:

```text
{KSG_COMPANY_DIR}/SpecGen/kicad_specgen_users.json
```

## 11.3 Ownership

This file is owned by SpecGen.

For a professional workflow, it may be stored in a shared Git repository.

For a standalone workflow, it may be stored in a local user folder.

## 11.4 Recommended User Fields

See `SpecGen_Schema_Definitions.md` §4 for the complete JSON schema and
formal field definitions. The table below describes the purpose of each field.

| Field            | Description                                                                       |
| ---------------- | --------------------------------------------------------------------------------- |
| `worker_id`      | Internal employee, contractor, or local user identifier.                          |
| `display_name`   | User-facing display name.                                                         |
| `preferred_name` | Preferred first name.                                                             |
| `family_name`    | Last/family name.                                                                 |
| `email`          | Work or preferred contact email.                                                  |
| `department`     | `dept_id` referencing a key in `company.departments`.                             |
| `team`           | `team_id` referencing a key in `company.departments.<department>.teams`.          |
| `job_title`      | Role or title used in reports.                                                    |
| `worker_type`    | Optional classification such as `employee`, `contractor`, `external`, or `hobby`. |
| `active`         | Boolean indicating whether the user profile is active.                            |
| `is_admin`       | Boolean indicating whether the user can modify shared SpecGen configuration.      |
| `client_assignments` | Optional list of `{client_id, project_id}` objects assigning the user to client projects. |
| `paths`          | Optional user path references using local tokens.                                 |

## 11.5 Example

```json
{
  "schema_version": 1,

  "users": [
    {
      "worker_id": "12345",
      "display_name": "John Smith",
      "preferred_name": "John",
      "family_name": "Smith",
      "email": "john.smith@advancedeng.com",
      "department": "platform_development",
      "team": "core",
      "job_title": "Senior Electrical Engineer",
      "worker_type": "employee",
      "active": true,
      "is_admin": true,
      "client_assignments": [
        { "client_id": "medical_devices", "project_id": "pacemaker_mk2" },
        { "client_id": "aerospace_systems", "project_id": "avionics_v3" }
      ],
      "paths": {
        "user_common": "{KSG_USER_COMMON_DIR}",
        "user_templates": "{KSG_USER_SPECGEN_DIR}/templates",
        "user_reports": "{KSG_USER_SPECGEN_DIR}/reports",
        "user_assets": "{KSG_USER_SPECGEN_DIR}/assets"
      }
    },

    {
      "worker_id": "23456",
      "display_name": "Jane Doe",
      "preferred_name": "Jane",
      "family_name": "Doe",
      "email": "jane.doe@advancedeng.com",
      "department": "engineering_tools",
      "team": "automation",
      "job_title": "Engineering Manager",
      "worker_type": "employee",
      "active": true,
      "is_admin": false,
      "client_assignments": [
        { "client_id": "medical_devices", "project_id": "legacy_monitor" }
      ],
      "paths": {
        "user_common": "{KSG_USER_COMMON_DIR}"
      }
    }
  ]
}
```

## 11.6 Application Use

The application uses `kicad_specgen_users.json` to:

* Identify the active user.
* Populate report author fields.
* Filter available client or internal environments.
* Determine whether the user can edit shared configuration.
* Locate user-specific templates and assets through token references.

---

# 12. File Chapter: Project `.kicad_specgen`

## 12.1 Purpose

The project `.kicad_specgen` file is the SpecGen project/session file.

Opening this file is equivalent to opening a SpecGen project.

It stores project-specific SpecGen state and recipe data.

It does not store local absolute token definitions.

## 12.2 Location

A project `.kicad_specgen` file must be stored under the KiCad project-local `specgen/` folder:

```text
{KICAD_PROJECT_DIR}/specgen/<name>.kicad_specgen
```

When opened, the application derives:

```text
SPECGEN_PROJECT_FILE     = absolute path of the opened .kicad_specgen file
KSG_PROJECT_SPECGEN_DIR  = parent folder of SPECGEN_PROJECT_FILE
KICAD_PROJECT_DIR        = parent folder of KSG_PROJECT_SPECGEN_DIR
```

The `.kicad_specgen` file may be committed to the KiCad project's Git repository.
It must not contain absolute paths — only token references.

## 12.3 Ownership

This file is owned by SpecGen and belongs to the KiCad project.

It may be committed with the KiCad project repository.

It should be portable between machines.

It should store token references, not local absolute path definitions.

## 12.4 Required Contents

The project `.kicad_specgen` file uses JSON format. The complete schema is
defined in `SpecGen_Schema_Definitions.md` §5. The table below summarises the
top-level sections; refer to the Schema document for field-level detail,
types, validation rules, and the full example.

| Section | Required | Purpose |
|---|---|---|
| `schema_version` | Yes | Schema version integer. Current: `1`. |
| `workspace` | Yes | Selected environment and workspace mode (`repo` or `standalone`). |
| `project` | Yes | Project metadata: name, revision, engineer, company, date, copyright, etc. |
| `files` | No | Tokenized references to support files: `.kicad_pro`, logo, CSS, templates, etc. **Note: the active jobset is in `jobset.active_jobset`, not here.** |
| `variables` | No | Custom Jinja2 template variables (`variables.custom`). |
| `jobset` | No | Active jobset reference (`jobset.active_jobset`), run options, per-destination overrides, last run result. |
| `report` | No | Report recipe: output folder, filename template, cover page config, page order and per-page definitions. |
| `fabrication` | No | FAB ZIP settings: output folder, filename template, per-destination ZIP config, README, checksums. |
| `ui` | No | Project UI state (active tab, panel sizes). Does not trigger dirty flag. Not committed. |

Key design rules:

```text
- jobset.active_jobset is the single reference to the active .kicad_jobset file.
  files.jobset must not be used.

- fabrication.output_dir defaults to {JOBSET_OUTPUT_DIR}/fab/ when absent.
  FAB_OUTPUT_DIR is computed from this field at runtime.

- report.output_dir defaults to {JOBSET_OUTPUT_DIR}/report/ when absent.

- The ui section is saved silently on close and does not set the dirty flag.

- All path values must use {TOKEN_NAME}/... notation.
  No absolute paths are permitted in this file.
```

## 12.5 Example

The complete schema and full JSON example are in `SpecGen_Schema_Definitions.md` §5.

Minimal valid example (only required sections):

```json
{
  "schema_version": 1,

  "workspace": {
    "mode": "repo",
    "environment": "medical_devices"
  },

  "project": {
    "name": "BoardA",
    "display_name": "Medical Devices BoardA",
    "document_number": "AE-MD-BA-001",
    "revision": "Rev B",
    "engineer": "John Smith",
    "company": "Medical Devices Inc",
    "date": "2026-06-03",
    "copyright": "© 2026 Advanced Engineering"
  }
}
```

Typical project with jobset and report configured:

```json
{
  "schema_version": 1,

  "workspace": {
    "mode": "repo",
    "environment": "medical_devices"
  },

  "project": {
    "name": "BoardA",
    "display_name": "Medical Devices BoardA",
    "document_number": "AE-MD-BA-001",
    "revision": "Rev B",
    "engineer": "John Smith",
    "company": "Medical Devices Inc",
    "date": "2026-06-03",
    "copyright": "© 2026 Advanced Engineering"
  },

  "files": {
    "kicad_pro":  "{KICAD_PROJECT_DIR}/BoardA.kicad_pro",
    "logo":       "{KSG_COMPANY_DIR}/SpecGen/assets/logos/company_logo.png",
    "title_page": "{KSG_COMPANY_DIR}/SpecGen/templates/title_page.md"
  },

  "variables": {
    "custom": {
      "TEST_LEVEL": "Engineering Release"
    }
  },

  "jobset": {
    "active_jobset":       "{KSG_PROJECT_SPECGEN_DIR}/release_default.kicad_jobset",
    "stop_on_error":       true,
    "clear_log_before_run": true,
    "destinations": {
      "sch_pdf":  { "selected": true,  "heading_override": "Schematics",       "notes": "" },
      "bom_csv":  { "selected": true,  "heading_override": "Bill of Materials", "notes": "Used in FAB package." },
      "gerbers":  { "selected": true,  "heading_override": "",                  "notes": "Included in FAB package." }
    }
  },

  "report": {
    "output_dir":         "{JOBSET_OUTPUT_DIR}/report/",
    "filename_template":  "{project_name}_{revision}_{date}_report.pdf",
    "pages": {
      "order": ["cover", "sch_pdf", "bom_csv"],
      "definitions": {
        "cover":   { "source_type": "markdown", "template": "{KSG_COMPANY_DIR}/SpecGen/templates/title_page.md", "include": true },
        "sch_pdf": { "source_type": "jobset",   "destination": "sch_pdf",   "include": true, "section_label": "Schematics" },
        "bom_csv": { "source_type": "jobset",   "destination": "bom_csv",   "include": true, "section_label": "Bill of Materials" }
      }
    }
  },

  "fabrication": {
    "output_dir":            "{JOBSET_OUTPUT_DIR}/fab/",
    "zip_filename_template": "{project_name}_{revision}_{date}_fab.zip",
    "destinations": {
      "gerbers": { "include": true, "zip_folder": "gerbers/" },
      "bom_csv": { "include": true, "zip_folder": "bom/" }
    },
    "readme":    { "include": true,  "template": "{KSG_USER_COMMON_DIR}/templates/fab_readme_standard.md", "filename": "README.md" },
    "checksums": { "include": true,  "algorithm": "sha256", "filename": "checksums.sha256" }
  }
}
```

## 12.6 Application Use

The application uses the project `.kicad_specgen` file to:

* Open and restore a SpecGen project.
* Determine the selected environment.
* Locate the active jobset (`jobset.active_jobset`).
* Load project metadata for display and template variable injection.
* Load custom Jinja2 template variables.
* Store jobset destination overrides and run results.
* Store the report recipe (page order, cover page, per-page source definitions).
* Store the fabrication ZIP package settings (output folder, filename template,
  per-destination ZIP config, README, checksums).
* Save reproducible project release configuration.

The `ui` section is written silently on close and is not written during normal
save operations. It does not set the project dirty flag.

---

# 13. File Chapter: KiCad `.kicad_pro`

## 13.1 Purpose

The `.kicad_pro` file is the KiCad project file.

SpecGen reads this file to validate the KiCad project and extract project text variables.

## 13.2 Ownership

This file is owned by KiCad.

SpecGen shall not modify this file.

## 13.3 Application Use

SpecGen uses the `.kicad_pro` file to:

* Confirm the active KiCad project.
* Load read-only KiCad project text variables.
* Populate the Variables tab.
* Provide project data for report templates.
* Run `kicad-cli jobset run`.

---

# 14. File Chapter: KiCad `.kicad_jobset`

## 14.1 Purpose

The `.kicad_jobset` file defines KiCad jobset destinations and generated output files.

SpecGen uses this file to run KiCad output generation.

## 14.2 Location

A project’s active `.kicad_jobset` file is usually stored under:

```text
{KSG_PROJECT_SPECGEN_DIR}/<jobset_name>.kicad_jobset
```

It may also be selected from another tokenized path if the project configuration allows it.

## 14.3 Ownership

This file is owned by KiCad.

SpecGen shall treat it as read-only by default.

SpecGen-specific destination notes, heading overrides, and selections shall be stored in the project `.kicad_specgen` file, keyed by destination ID.

## 14.4 Application Use

SpecGen uses `.kicad_jobset` files to:

* Parse jobset destinations.
* Display destination IDs and descriptions.
* Run all destinations.
* Run selected destinations by destination ID when supported.
* Generate source output files for the Results, Report, and Fabrication workflows.
* Determine or validate jobset output folders.

---

# 15. Company/User Storage Structure

SpecGen uses a common root location for company, user, and shared SpecGen files.

The local token for this location is:

```text
KSG_COMPANY_DIR
```

`KSG_COMPANY_DIR` identifies the root location that contains the shared or standalone `SpecGen/` folder.

This location may be:

* A Git repository root in professional/repository mode.
* A local standalone folder in hobby/standalone mode.
* A shared company folder.
* A company-controlled repository checkout.
* A local personal SpecGen workspace.

Expected structure:

```text
{KSG_COMPANY_DIR}/
├─ path/to/kicad/libraries/
└─ SpecGen/
   ├─ kicad_specgen_company.json
   ├─ kicad_specgen_users.json
   ├─ docs/
   ├─ templates/
   ├─ assets/
   └─ Users/
      └─ <worker_id>/          (the user's worker_id string)
         ├─ common/
         ├─ reports/
         ├─ templates/
         └─ assets/
```

In standalone mode, `KSG_COMPANY_DIR` may point to a local user-controlled folder.

Example:

```text
/Users/john/Library/Preferences/kicad/9.0/SpecGenData
```

In repo mode, `KSG_COMPANY_DIR` may point to a Git repository root.

Example:

```text
/Users/john/Engineering/CompanyRepo
```

---

# 16. Setup Process Requirements

The setup process is fully specified in `SpecGen_Setup_Process.md`.

That document defines:

* The six-phase setup wizard (Platform Detection, Dependency Installation,
  Tool Detection, Workspace Mode Selection, Company and User Configuration,
  Local Token Configuration and Validation).
* Headless / text-mode setup (`python setup.py --headless`).
* Startup detection and the Setup Required banner.
* The Configure tab as the in-application post-setup editing surface.
  See `SpecGen_Tab_Configure.md` for the full five-subtab wireframe specification.
* The `.venv` location: always `{KSG_APP_DIR}/.venv`.
* Standalone mode: `kicad_specgen_company.json` always present, defaults to
  company name "personal".
* Answers to all ten pre-coding questions from the Progress.

The summary of setup responsibilities relevant to this framework:

```text
Phase 1: Detect OS and KICAD_COMMON_DIR.
Phase 2: Create {KSG_APP_DIR}/.venv and install dependencies.
Phase 3: Locate kicad-cli. Write path to kicad_specgen_local.json → tools.
Phase 4: User selects workspace mode (Shared/Repo or Standalone/Local).
Phase 5: Identify or create KSG_COMPANY_DIR.
         Load or create kicad_specgen_company.json and kicad_specgen_users.json.
Phase 6: Collect KSG_* tokens.
         Write kicad_specgen_local.json with setup_complete = true.
         Validate all required tokens.
```

---

# 17. Application Validation Requirements

Validation should produce clear user-facing messages.

Validation should not show raw stack traces for normal user errors.

Validation shall check:

```text
kicad_specgen_local.json exists or can be created
schema_version values are supported
required local tokens exist
local token values are absolute paths (must — not nested references)
KSG_COMPANY_DIR exists or can be created
SpecGen company/user files exist or can be created
active_user exists in kicad_specgen_users.json
active_environment exists in kicad_specgen_company.json
recent project paths are valid or can be reported missing
project .kicad_specgen file is under a specgen folder
KSG_PROJECT_SPECGEN_DIR can be derived
KICAD_PROJECT_DIR can be derived
active .kicad_pro exists
active .kicad_jobset exists and is parseable when a project is open
project token references resolve
company token references resolve
user token references resolve
custom variable names are valid
no absolute paths in company, user, or project files — if found, trigger
  the auto-conversion flow (create token or copy file) rather than blocking
skipped_tokens entries are noted in Project tab with ⚠ badge
```

Missing-token validation shall offer the full set of repair options:
Provide, Skip, Remove. See §6.9 for the complete option definitions.

File-writing validation shall warn before overwrite.

If modifying `kicad_common.json`, SpecGen must create a timestamped backup first.

Jobset/report reconciliation checks (at open, save, and close) shall offer:
Review Now, Defer, or Cancel. See §7.3 for the full reconciliation behavior.

---

# 18. Implementation Architecture

The implementation shall keep configuration loading and token resolution
centralized in `core/` modules. See `SpecGen_Stage_Plan.md` for the complete
module layout and `SpecGen_Schema_Definitions.md` for all JSON schemas.

Required core modules:

```text
core/
  platform_paths.py       OS detection and KICAD_COMMON_DIR resolution
  specgen_local_config.py Load / validate / save kicad_specgen_local.json
  specgen_company_config.py Load / validate / save kicad_specgen_company.json
  specgen_user_config.py  Load / validate / save kicad_specgen_users.json
  project_config.py       Load / validate / save / migrate .kicad_specgen
  token_resolver.py       Build effective token table; report missing tokens
  validators.py           All validation rules; returns structured results
  file_ops.py             Atomic JSON write, backup, directory creation

### `file_ops.py` — Atomic write contract

All JSON config file writes must go through `file_ops.write_json_atomic()`.
Direct `open(path, 'w')` writes are forbidden — a crash mid-write would corrupt
the config file with no recovery path.

```python
def write_json_atomic(path: Path, data: dict,
                      indent: int = 2,
                      backup: bool = False) -> None:
    """
    Write data as JSON to path atomically using write-to-temp-then-rename.

    1. Serialise data to a JSON string.
    2. Write the JSON string to a sibling temp file:
         path.parent / (path.name + ".tmp")
    3. If backup=True, copy the existing file to:
         path.parent / (path.stem + ".bak_YYYYMMDD_HHMMSS" + path.suffix)
    4. os.replace(tmp_path, path)  — atomic on POSIX; near-atomic on Windows.
    5. If any step raises, the original file is untouched.
    """
    ...
```

`os.replace()` is atomic on POSIX (Linux, macOS) because it maps to the
`rename(2)` syscall. On Windows it is not guaranteed atomic but is sufficiently
safe for this use case — the temp file and the target are on the same drive.

`backup=True` is required when writing `kicad_common.json` (KiCad-owned file).
It is optional for SpecGen-owned files but recommended for `kicad_specgen_local.json`.

```text
  migrations.py           Schema version migration functions
  logging_utils.py        Python logging config and structured log records
  kicad_env.py            Read kicad_common.json environment.vars
  kicad_pro_parser.py     Read .kicad_pro text_variables (read-only)
  kicad_jobset_parser.py  Read .kicad_jobset outputs[] (read-only)
  app_state.py            In-memory application state; observable fields
```

UI code shall not independently parse or resolve configuration files.

The GUI shall call shared services for:

* Loading and saving config files.
* Resolving token references.
* Validating paths and schemas.
* Reporting and repairing missing tokens.
* Updating recent projects and session state.
* Deriving project runtime tokens.

The application shall treat each configuration file according to its ownership rules.

## 18.1 File Summary

Canonical file locations and ownership by platform.

`KICAD_COMMON_DIR` is the OS-specific KiCad user configuration directory:

```text
Windows : %APPDATA%\kicad\9.0
Linux   : ~/.config/kicad/9.0
macOS   : ~/Library/Preferences/kicad/9.0
```

Where `9.0` is the KiCad configuration version detected at runtime.

| File | Location | Owner | Format | Portable |
|---|---|---|---|---|
| `kicad_specgen_local.json` | `{KICAD_COMMON_DIR}/kicad_specgen_local.json` | SpecGen | JSON | No |
| `kicad_specgen_company.json` | `{KSG_COMPANY_DIR}/SpecGen/kicad_specgen_company.json` | SpecGen | JSON | Yes |
| `kicad_specgen_users.json` | `{KSG_COMPANY_DIR}/SpecGen/kicad_specgen_users.json` | SpecGen | JSON | Yes |
| `<name>.kicad_specgen` | `{KICAD_PROJECT_DIR}/specgen/<name>.kicad_specgen` | SpecGen | JSON | Yes |
| `<project>.kicad_pro` | `{KICAD_PROJECT_DIR}/<project>.kicad_pro` | KiCad | JSON | n/a |
| `<name>.kicad_jobset` | Any tokenized path | KiCad | JSON | n/a |
| `kicad_common.json` | `{KICAD_COMMON_DIR}/kicad_common.json` | KiCad | JSON | n/a |

## 18.2 .gitignore Requirements

The SpecGen application repository `.gitignore` must include:

```text
# Virtual environment
.venv/

# Local machine configuration — contains absolute paths
kicad_specgen_local.json
```

`kicad_specgen_company.json`, `kicad_specgen_users.json`, and `.kicad_specgen`
project files may be committed to their respective repositories.
`kicad_specgen_local.json` must never be committed anywhere.

## 18.3 Short Descriptions

**`kicad_specgen_local.json`**
Local machine state and absolute path token definitions. Stores KSG_* tokens,
kicad-cli path, setup state, active user, active environment, recent projects,
and session state. Machine-specific and non-portable.

**`kicad_specgen_company.json`**
Shared company/client/team data and tokenized path references. Stores company
identity, client definitions, team definitions, environment definitions, shared
template and asset path references. Portable — no absolute paths.

**`kicad_specgen_users.json`**
User directory data. Stores worker_id, display names, roles, client associations,
and user-specific path references. Portable — no absolute paths.
Example: `worker_id=12345` → `KSG_USER_SPECGEN_DIR={KSG_COMPANY_DIR}/SpecGen/Users/12345`

**`<name>.kicad_specgen`** (SpecGen project file)
Full SpecGen project state: workspace mode, environment, project metadata,
support file references, custom variables, jobset configuration and destination
overrides, report recipe, and fabrication ZIP settings. Portable — token
references only. The active `.kicad_jobset` reference lives in
`jobset.active_jobset`. If the KiCad project is updated and the jobset
destinations and output paths remain the same, the user can re-run the jobset
and regenerate the report without modifying this file. If destinations change
or output paths move, SpecGen detects the mismatch and flags it during validation.

**`<project>.kicad_pro`** (KiCad project file)
KiCad project file. SpecGen reads `text_variables` (key/value pairs such as
REV, DATE, PART_NUMBER) as read-only template variables. SpecGen never writes
to this file.

**`<name>.kicad_jobset`** (KiCad jobset file)
KiCad-owned jobset input. Defines an ordered sequence of kicad-cli export jobs.
SpecGen reads destination IDs and output paths. Never modified by SpecGen.
Output root: `JOBSET_OUTPUT_DIR = {KICAD_PROJECT_DIR}/{outputs[0].settings.output_path}`.

**`kicad_common.json`** (KiCad common configuration)
KiCad application preferences. SpecGen reads `environment.vars` for KiCad
environment variable definitions. Read-only during normal operation. May be
modified during setup only with user approval and a timestamped backup.
