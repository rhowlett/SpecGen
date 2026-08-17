# KiCad SpecGen — Architecture Review and Implementation Plan

> **Document role:** Principal-engineer-level architecture review.
> **Authority:** `SpecGen_File_Framework.md` is the source of truth.
> **Status:** Pre-implementation. No production code is produced here.
> **Date:** 2026-06-13

---

## 1. Executive Summary

The KiCad SpecGen project has a solid and well-reasoned design intent. The token
model, file-ownership rules, and two-tier configuration split (local absolute vs.
shared tokenized) are architecturally sound. However, the document set is in an
uneven state: the two newest documents (`SpecGen_File_Framework.md` and
`SpecGen_Schema_Definitions.md`) are largely consistent and implementation-ready,
while the older supporting documents (`SpecGen_Application.md`,
`SpecGen_GUI_Menus.md`, `SpecGen_Tab_Jobset.md`) contain a mix of current
and stale content.

**The three most important things to resolve before coding begins:**

1. The Setup Process (Section 16 of `SpecGen_File_Framework.md`) is explicitly
   marked "Under Construction." A dedicated Setup Process document must be written
   and approved before any Stage 1 code that touches `kicad_specgen_local.json`
   creation can be finalized.

2. The `Configure Environments` dialog model in `SpecGen_Application.md`
   and `SpecGen_GUI_Menus.md` conflates two distinct responsibilities —
   editing `kicad_specgen_local.json` tokens AND editing `kicad_specgen_company.json`
   environments. These must be cleanly separated before the dialog is implemented.

3. The `SpecGen_GUI_Menus.md` New Project dialog is partially designed around
   an older model (references to "named environments" being created in the dialog
   itself, `KSG_SPECGEN_COMMON`, and a logic flow that is not fully consistent with
   the current `kicad_specgen_company.json` environment model). This dialog needs
   to be redesigned against the current framework before implementation.

Overall the project is well-positioned for a clean Stage 1 build once these gaps
are closed and the terminology is normalized.

---

## 2. Source-of-Truth Assessment

| Document | Role | Trustworthiness |
|---|---|---|
| `SpecGen_File_Framework.md` | **Primary source of truth** | High. Current. A few sections are marked Under Construction. |
| `SpecGen_Schema_Definitions.md` | **Primary source of truth** | High. Fully consistent with Framework. Resolves the §12.5 TODO. |
| `SpecGen_Application.md` | Supporting reference | Medium. Mostly current. Contains stale View menu items and sidebar entries. |
| `SpecGen_GUI_Menus.md` | Supporting GUI reference | Medium-Low. Contains stale naming and partially stale dialog flow in New Project. |
| `SpecGen_Tab_Jobset.md` | Supporting wireframe reference | Medium. Wireframes are good. Results tab is missing Output Log. Minor token naming issues. |
| `SpecGen_Help_JinJa.md` | Help file style example | High. Correct format and style. Use as the template for all help files. |

---

## 3. Document-by-Document Review

### 3.1 `SpecGen_File_Framework.md`

**Purpose:** Defines configuration file ownership, token model, local vs. shared
split, file-open sequence, required tokens, protected derived tokens, and setup
process skeleton.

**Current sections:** Sections 1–15, 17, 18. Schema summary in Section 18.

**Outstanding TODOs inside the document:**

- Section 12.4 "Required Contents — Under Construction": The table shows TOML-style
  `[workspace]` section headers instead of JSON keys. This is a formatting leftover
  from an earlier TOML design. Section 12.5 defers to `SpecGen_Schema_Definitions.md`
  for resolution — which is correct, and `SpecGen_Schema_Definitions.md` does resolve
  this correctly with JSON keys. The `[bracket]` notation in Section 12.4 should be
  updated to JSON key notation for clarity.

- Section 16 "Setup Process Requirements" is explicitly marked Under Construction.
  This is a blocking gap for Stage 1 (see Gap List).

- Section 18 file summary contains a copy-paste error:
  ```
  KICAD_COMMON_DIR=%APPDATA%\KiCad\9.0\kicad_specgen_local.json
  ```
  This defines `KICAD_COMMON_DIR` as pointing to the file itself, not the directory.
  The correct definition is:
  ```
  KICAD_COMMON_DIR = %APPDATA%\KiCad\9.0
  KSG_SPECGEN_LOCAL_FILE = {KICAD_COMMON_DIR}\kicad_specgen_local.json
  ```
  This error appears for all three platforms in Section 18.

- The prompt asks whether `KSG_PROJECT_SPECGEN_DIR` should be renamed to
  `SPECGEN_PROJECT_DIR`. **Recommendation: Keep `KSG_PROJECT_SPECGEN_DIR`.**
  The `KSG_` prefix correctly identifies this as a SpecGen-owned token.
  `SPECGEN_PROJECT_DIR` would lose the `KSG_` namespace consistency.
  The concern about consistency is valid but solved by keeping the `KSG_` prefix.

**Missing information:**

- No definition of what happens when `kicad_specgen_company.json` or
  `kicad_specgen_users.json` do not exist at startup (beyond "start setup").
- No definition of `active_environment` fallback when no project is open.
- No definition of what `active_environment` maps to when the environment is `sandbox`
  (which has no `client` or `team` key in the company file).

---

### 3.2 `SpecGen_Schema_Definitions.md`

**Purpose:** Provides complete JSON schemas for all four SpecGen-owned files, token
resolution precedence, KiCad file parsing reference, and migration policy.

**Current status:** Excellent. This document fills the gap left by the §12.5 TODO
in `SpecGen_File_Framework.md`. It is consistent with the Framework.

**Gaps:**

- Migration function naming convention (`migrate_v{from}_to_v{to}`) and the
  `core/migrations.py` module are mentioned but a stub list of expected functions
  is not provided. This is minor but should be noted in the test strategy.

- The `JOBSET_OUTPUT_DIR` derivation rule says:
  ```
  JOBSET_OUTPUT_DIR = KICAD_PROJECT_DIR / outputs[0].settings.output_path
  ```
  Using `outputs[0]` assumes all outputs share the same output path. This needs
  clarification: is it always `outputs[0]`, or should SpecGen validate that all
  outputs share a common root and warn if they do not?

- The `.kicad_jobset` parsing section lists `outputs[].id` as the destination ID
  but the KiCad 9 jobset format actually uses `outputs[].id` — this is consistent
  with the wireframe. Confirm this is correct against an actual KiCad 9 jobset file
  before implementation.

---

### 3.3 `SpecGen_Application.md`

**Purpose:** Application overview, workspace pages, menu structure, module layout,
and Stage 1 scope.

**Current sections:** Application overview, main window layout, Project page,
Variables page, Logs page, Configure Environments, Missing Tokens, Stage 1 scope,
module layout, implementation requirements. Most content is current.

**Stale or inconsistent sections:**

- View menu (line 631) lists `Results (Jobset subtab)` as a separate sidebar entry.
  `SpecGen_GUI_Menus.md` correctly removes this as a separate sidebar item and
  makes Results an internal tab within the Jobset workspace. The application
  description should be updated to match.

- Sidebar entries (line 723) still list `Results (Jobset subtab)` as a separate
  sidebar item. Same issue as above.

- Stage 1 placeholder pages (line 741) still lists `Results (Jobset subtab)` as
  a separate placeholder page.

- Help menu (line 662) is much simpler than the more complete version in
  `SpecGen_GUI_Menus.md`. The Pulldown Menus version is more complete and
  should be treated as the current design.

- Module layout (line 1253) is missing:
  - `core/specgen_company_config.py`
  - `core/specgen_user_config.py`
  - `core/migrations.py`
  - `core/kicad_jobset_parser.py`
  - `core/kicad_pro_parser.py`
  - `setup/setup.py` entry point
  - `ui/dialogs/help_dialog.py`
  - `ui/dialogs/new_project_dialog.py` (listed but not in core module list)
  - `help/` folder

- The Configure Environments dialog description says it edits `kicad_specgen_local.json`.
  But the Pulldown Menus document also says it edits "company and environment data."
  These responsibilities must be clarified. See Gap §6.

- TODO note at line 493: "Remove the submenus they are defined in the markdown /
  ask for the standard tokens to be defined in a table." This is an in-document
  author note that should be resolved or removed.

---

### 3.4 `SpecGen_GUI_Menus.md`

**Purpose:** GUI/menu concept document. Primary method for presenting proposed UI
pulldowns before implementation.

**Current sections:** File menu, Edit menu, View menu, Help menu, Help system
requirements, required help files. Most content is current and well-specified.

**Stale or inconsistent items:**

- **New Project dialog** (line 87): References `KSG_SPECGEN_COMMON` (old token
  name) and the concept of entering a "New named environment" directly in the dialog.
  Under the current framework, environments are defined in `kicad_specgen_company.json`
  and the local config selects from them. The New Project dialog should select an
  existing environment from `kicad_specgen_company.json.environments`, not create
  a new one inline.

- **New Project dialog** "Select Git Repository" and "Select Environment Common
  Folder" controls: These reference concepts (`KSG_SPECGEN_COMMON`) that are not
  defined in the current framework. These need to be redesigned against the current
  model before implementation.

- **Configure Environments dialog** description (line 255): Says it edits
  `kicad_specgen_company.json` environments AND `kicad_specgen_local.json` tokens.
  This conflation of two distinct files with different ownership is a design risk.
  See Gap §6.

- **Open Recent** (line 139): Says recent paths are in `kicad_specgen_local.json`.
  This is correct and consistent with the Framework.

- Help folder (line 659) lists `kicad_specgen_local.md` but not `kicad_common.md`
  or `migrations.md`. Minor gap.

- Help file `getting_started.md` (line 699) refers to running `setup.py` directly.
  The setup entry point should be clarified — is it `python setup.py`, `python -m
  setup`, or a wrapper script?

---

### 3.5 `SpecGen_Tab_Jobset.md`

**Purpose:** Visual wireframe reference for the Jobset workspace.

**Current status:** The four-tab wireframe (Dashboard, Setup & Run, Results, Output
Log) is well-designed and consistent with the direction in `SpecGen_GUI_Menus.md`.

**Issues:**

- Results tab wireframe (line 88) shows only three tabs: `Dashboard`, `Setup & Run`,
  `Results`. The Output Log tab is missing from the Results tab wireframe's tab bar.
  This is likely a copy-paste omission since the Output Log tab is fully specified
  elsewhere.

- Dashboard panel shows `{KICAD_PROJECT_DIR}/BoardA.kicad_pro`. This token usage
  is correct per the framework.

- Setup & Run table shows `Active Output Folder: {KICAD_PROJECT_DIR}/{JOBSET_OUTPUT_DIR}`.
  This is technically incorrect — `JOBSET_OUTPUT_DIR` is an absolute path derived
  from `KICAD_PROJECT_DIR` + the jobset output path. It should not be shown as
  `{KICAD_PROJECT_DIR}/{JOBSET_OUTPUT_DIR}`. Show `JOBSET_OUTPUT_DIR` as a resolved
  absolute path only.

- The wireframe correctly shows that `Output Log` feeds into the `Logs` workspace
  page for persistence (line 156). This cross-page relationship needs a clear
  implementation definition.

---

### 3.6 `SpecGen_Help_JinJa.md`

**Purpose:** Example of the Markdown-based help file style. Defines the authoring
format for all application help content.

**Status:** Correct and well-structured. Use this as the canonical style template.

**Notes for help file authors:**

- The document uses standard Markdown headings, fenced code blocks, and tables.
  All help files should follow this structure.
- YAML is used in examples. Application help files should use actual SpecGen JSON
  examples, not YAML.
- Jinja2 template syntax uses `{{ variable }}` (double braces). SpecGen token
  references use `{TOKEN_NAME}` (single braces). Help content must clearly
  distinguish these two syntaxes to avoid user confusion.

---

## 4. Terminology and Naming Corrections

| # | Old Term | Correct Term | Where It Appears | Why It Matters | Recommended Action |
|---|---|---|---|---|---|
| 1 | `kicad_specgen.json` | `kicad_specgen_local.json` | App description (implied by older assumptions) | Old local config name; new name is authoritative | Replace all occurrences |
| 2 | `KICAD_SPECGEN_DIR` | `KSG_PROJECT_SPECGEN_DIR` | Framework (flagged in prompt), older code | Old name blurs KiCad vs. SpecGen ownership | Replace everywhere; add validator rule to reject the old name |
| 3 | `KSG_SPECGEN_COMMON` | Not defined in current framework | Pulldown Menus New Project dialog | References a token that no longer exists | Remove from New Project dialog; redesign dialog |
| 4 | `KSG_SPECGEN_DIR` | Not a current token | Possibly in older code | Old umbrella token; replaced by specific tokens | Remove; add validator rule |
| 5 | `KSG_DIR` | Not a current token | Possibly in older code | Too generic; replaced by specific `KSG_*` tokens | Remove |
| 6 | `PROJECT_DIR` | `KICAD_PROJECT_DIR` | Older documents | Missing ownership prefix | Replace |
| 7 | `KSG_COMPANY_REPO_DIR` | `KSG_COMPANY_DIR` | Possibly in older code | Repo-mode naming baked into a general token | Replace |
| 8 | `Results` (as sidebar entry) | `Results` (as Jobset subtab only) | App description sidebar list, View menu | Results is not a standalone sidebar page | Remove from sidebar; make it an internal Jobset tab |
| 9 | TOML `[section]` headers in §12.4 | JSON key notation | `SpecGen_File_Framework.md` §12.4 | Formatting leftover; JSON keys should use `"key":` notation | Update §12.4 to show JSON key names without brackets |
| 10 | `kicad_specgen.json` as shared config | `kicad_specgen_company.json` + `kicad_specgen_users.json` | Older architecture references | Old single-file model replaced by split company/users files | Update any remaining references |
| 11 | `KICAD_COMMON_DIR` = full file path | `KICAD_COMMON_DIR` = directory; `KSG_SPECGEN_LOCAL_FILE` = file path | Framework §18 (copy-paste error) | Conflates directory token with file path token | Fix §18 in Framework document |
| 12 | `JS Results` (as separate sidebar tab) | Removed; Results is a Jobset internal tab | App description, earlier design notes | Old design had Results as a separate top-level sidebar page | Confirm removal; update all references |
| 13 | Setup entry point `setup.py` | Should be clarified as `python setup.py` or a wrapper | App description, Getting Started help | Ambiguous entry point | Define and document the exact invocation |
| 14 | `{KICAD_PROJECT_DIR}/{JOBSET_OUTPUT_DIR}` in wireframe | `{JOBSET_OUTPUT_DIR}` (absolute, not nested) | Jobset Window wireframe line 57 | `JOBSET_OUTPUT_DIR` is already absolute; nesting is incorrect | Fix wireframe display string |
| 15 | YAML in help examples | JSON in help examples | `SpecGen_Help_JinJa.md` (style document only) | App uses JSON; help examples should match | Use JSON in SpecGen-specific help files |

---

## 5. Configuration/File Framework Gaps

For each file, the following gap analysis uses the Framework as the authority.

### 5.1 `kicad_specgen_local.json`

| Area | Status |
|---|---|
| Full schema | ✅ Defined in `SpecGen_Schema_Definitions.md` §2 |
| Required fields | ✅ Defined |
| Optional fields | ✅ Defined (optional local tokens in Framework §6.6) |
| Validation rules | ✅ Defined in Schema Definitions §2 |
| Example file | ✅ Defined in Framework §8.6 |
| Read/write ownership | ✅ SpecGen owns; must not be committed to shared repos |
| Migration rules | ✅ Defined in Schema Definitions §7 |
| GUI editor | ✅ Configure Environments dialog (tokens section only) |
| Unit tests | ❌ Not yet specified |
| **Gap: Setup process for file creation** | ❌ Framework §16 is Under Construction |
| **Gap: Startup fallback when file is missing** | ❌ Not fully specified — what state does the app show? |
| **Gap: What happens when `active_environment` references an unknown environment** | ❌ Not specified |

### 5.2 `kicad_specgen_company.json`

| Area | Status |
|---|---|
| Full schema | ✅ Defined in Schema Definitions §3 |
| Required fields | ✅ `schema_version`, `company` |
| Optional fields | ✅ clients, internal_teams, environments, templates, assets |
| Validation rules | ✅ Defined |
| Example file | ✅ Defined in Framework §10.6 |
| Read/write ownership | ✅ SpecGen; shared; may be in Git repo |
| Migration rules | ✅ Covered by Schema Definitions §7 general policy |
| GUI editor | ⚠️ Partially — Configure Environments dialog (see Gap §6) |
| Unit tests | ❌ Not yet specified |
| **Gap: Who creates this file if it does not exist** | ⚠️ Setup process (Under Construction) |
| **Gap: Standalone mode — does `kicad_specgen_company.json` still exist?** | ❌ Not fully specified. Framework §2.1 says hobby users "may operate entirely without a company repository" but the startup sequence (§7) requires opening the company file (step 5). Contradiction. |
| **Gap: Minimum valid company file for standalone/hobby mode** | ❌ Not defined |

### 5.3 `kicad_specgen_users.json`

| Area | Status |
|---|---|
| Full schema | ✅ Defined in Schema Definitions §4 |
| Required fields | ✅ `schema_version`, `users`, each user requires `worker_id`, `display_name`, `active` |
| Optional fields | ✅ All other user fields |
| Validation rules | ✅ Defined |
| Example file | ✅ Defined in Framework §11.5 |
| Read/write ownership | ✅ SpecGen; shared |
| GUI editor | ⚠️ Partially via Configure Environments (not well specified) |
| Unit tests | ❌ Not specified |
| **Gap: Single-user / hobby mode — does this file still require `worker_id`?** | ❌ Not fully defined |
| **Gap: GUI path for adding/removing users** | ❌ Not specified. The Configure Environments dialog doesn't clearly expose user management |

### 5.4 Project `.kicad_specgen`

| Area | Status |
|---|---|
| Full schema | ✅ Defined in Schema Definitions §5 |
| Required fields | ✅ `schema_version`, `workspace`, `project` |
| Optional sections | ✅ files, variables, jobset, report, fabrication, ui |
| Validation rules | ✅ Defined |
| Complete example | ✅ Defined in Schema Definitions §5 |
| Read/write ownership | ✅ SpecGen; project-local; may be committed |
| Migration rules | ✅ Covered by general policy |
| GUI editor | ✅ Project page, Variables page, Jobset page, Report page, Fabrication page |
| Unit tests | ❌ Not specified |
| **Gap: `jobset.destinations` key population** | ⚠️ Keys come from parsing `.kicad_jobset`, but the population sequence is not fully defined. If the jobset file changes, how does SpecGen reconcile stale destination keys? |
| **Gap: `report.pages.order` validation against known identifiers** | ⚠️ Schema says "warn on unknown page IDs" but the list of known identifiers is not defined |
| **Gap: Dirty-state tracking** | ❌ Not defined. When is the project considered dirty? Which fields trigger a dirty flag? |

### 5.5 `.kicad_pro`

| Area | Status |
|---|---|
| Fields SpecGen reads | ✅ Defined in Schema Definitions §6 (`text_variables`) |
| Ownership | ✅ KiCad; SpecGen read-only |
| Parser behavior | ✅ Defined — warn if missing, scan for `*.kicad_pro` |
| Unit tests | ❌ Not specified |
| **Gap: Multiple `.kicad_pro` files in `KICAD_PROJECT_DIR`** | ❌ What does SpecGen do if scanning finds more than one? |

### 5.6 `.kicad_jobset`

| Area | Status |
|---|---|
| Fields SpecGen reads | ✅ Defined in Schema Definitions §6 |
| Ownership | ✅ KiCad; SpecGen read-only |
| `JOBSET_OUTPUT_DIR` derivation | ⚠️ Uses `outputs[0].settings.output_path` — ambiguous if outputs have different paths |
| Unit tests | ❌ Not specified |
| **Gap: Jobset file not under `specgen/` folder** | ⚠️ Framework §14.2 says the jobset "may also be selected from another tokenized path." This means the validation rule that `.kicad_specgen` must be under `specgen/` does not apply to the jobset. This is correct but should be explicitly documented. |
| **Gap: Jobset format version** | ❌ KiCad 9 jobset JSON format is assumed but not pinned. If KiCad changes the format, the parser will break silently. |

### 5.7 `kicad_common.json`

| Area | Status |
|---|---|
| Fields SpecGen reads | ✅ Defined in Schema Definitions §6 (`environment.vars`) |
| Ownership | ✅ KiCad; SpecGen read-only (except during setup with user approval) |
| Backup before write | ✅ Defined |
| Unit tests | ❌ Not specified |
| **Gap: `kicad_common.json` location on different KiCad versions** | ⚠️ Framework uses `9.0` in paths. KiCad version detection is mentioned but not fully specified. |

### 5.8 Markdown Help Files

| Area | Status |
|---|---|
| File format style | ✅ `SpecGen_Help_JinJa.md` provides the canonical style |
| Required topics | ✅ Defined in `SpecGen_GUI_Menus.md` §Help System Requirements |
| Recommended folder structure | ✅ `help/` folder with named `.md` files |
| Rendering requirements | ✅ Defined — `QTextBrowser` for Stage 1 |
| Help dialog behavior | ✅ Defined — modal, scrollable, OK button |
| Versioning | ❌ Not defined. Help files are in the app repo — they update with the app. No special versioning needed, but this should be stated. |
| **Gap: No `help/` folder file list with status** | ❌ Which help files are required for Stage 1 vs. later stages is not explicitly listed as a deliverable checklist |

---

## 6. GUI Framework Gaps

### 6.1 Area-by-Area Consistency Review

| GUI Area | Consistent with Framework? | Issues |
|---|---|---|
| Top menu bar `[File][Edit][View][Help]` | ✅ Yes | None |
| File menu items | ✅ Yes | "Copy / Create From Existing Project" in Pulldown Menus is not in App Description — this is a gap to resolve |
| Edit menu — `Configure kicad-cli` | ✅ In Pulldown Menus | Missing from App Description Edit menu |
| Edit menu — `Validate Project` | ✅ In Pulldown Menus | Missing from App Description Edit menu |
| View menu — sidebar page names | ⚠️ Partial | App Description still lists `Results (Jobset subtab)` as a sidebar item; Pulldown Menus correctly removes it |
| Sidebar navigation | ⚠️ Partial | Same Results issue above |
| Project page | ✅ Yes | Well-specified |
| Variables page | ✅ Yes | Well-specified |
| Jobset workspace (4 subtabs) | ✅ Yes | Wireframe is good |
| Report page | ❌ Not designed | No wireframe or spec exists yet |
| Fabrication page | ❌ Not designed | No wireframe or spec exists yet |
| Logs page | ✅ Yes | Simple; well-specified for Stage 1 |
| Configure Environments dialog | ⚠️ Design conflict | See below |
| Missing Tokens dialog | ✅ Yes | Consistent across all docs |
| New Project dialog | ⚠️ Partially stale | Contains `KSG_SPECGEN_COMMON` and inline environment creation — needs redesign |
| Markdown Help dialog | ✅ Yes | Well-specified |
| About dialog | ✅ Yes | Minimal; well-specified |

### 6.2 Configure Environments Dialog — Design Conflict

This is the most significant GUI design conflict in the document set.

**What the App Description says:** The dialog edits `kicad_specgen_local.json` only.
It does not edit the project `.kicad_specgen` report recipe. This is correct per
the Framework.

**What the Pulldown Menus description says:** The dialog allows editing
`active_environment`, `environment name`, `environment mode`, `environment
description`, `KSG_* token definitions`, and `support file defaults`. This mixes
concerns:

- `active_environment` lives in `kicad_specgen_local.json` — correct.
- `KSG_*` token definitions live in `kicad_specgen_local.json` — correct.
- `environment name`, `environment mode`, `environment description` live in
  `kicad_specgen_company.json.environments` — **different file with different
  ownership**.

**Resolution required before implementation:**

The dialog should be split or clearly scoped:

Option A — Single dialog, two tabs:
- Tab 1: Local Tokens (edits `kicad_specgen_local.json.tokens`)
- Tab 2: Environments (edits `kicad_specgen_company.json.environments`)

Option B — Two separate menu items:
- `Edit → Configure Local Tokens...` → edits `kicad_specgen_local.json`
- `Edit → Configure Environments...` → edits `kicad_specgen_company.json`

Option B is recommended because it is cleaner and avoids a dialog that writes to
two different files with different portability rules. This must be decided before
coding begins.

### 6.3 Write Responsibility Summary

| GUI Action | Writes To |
|---|---|
| Configure kicad-cli | `kicad_specgen_local.json` → `tools` |
| Add/Remove/Edit local token | `kicad_specgen_local.json` → `tokens` |
| Set active user | `kicad_specgen_local.json` → `active_user` |
| Set active environment | `kicad_specgen_local.json` → `active_environment` |
| Add/Remove/Edit environment definition | `kicad_specgen_company.json` → `environments` |
| Add/Remove/Edit client | `kicad_specgen_company.json` → `clients` |
| Add/Remove user | `kicad_specgen_users.json` → `users` |
| Edit project metadata | `.kicad_specgen` → `project` |
| Edit custom variables | `.kicad_specgen` → `variables.custom` |
| Save jobset destination selections | `.kicad_specgen` → `jobset.destinations` |
| Save report recipe | `.kicad_specgen` → `report` |
| Save FAB settings | `.kicad_specgen` → `fabrication` |
| Add token from Missing Tokens dialog | `kicad_specgen_local.json` → `tokens` |
| Read KiCad environment vars | `kicad_common.json` — read-only |
| Read KiCad project vars | `.kicad_pro` — read-only |
| Read jobset destinations | `.kicad_jobset` — read-only |

### 6.4 Stage 1 vs. Later Stage GUI Items

| Item | Stage |
|---|---|
| Menu bar (all menus) | Stage 1 |
| Sidebar navigation (all entries, placeholders ok) | Stage 1 |
| Project page (full) | Stage 1 |
| Variables page (full) | Stage 1 |
| Logs page (basic) | Stage 1 |
| Configure Environments dialog | Stage 1 |
| Missing Tokens dialog | Stage 1 |
| New Project dialog | Stage 1 |
| About dialog | Stage 1 |
| Help dialog (QTextBrowser) | Stage 1 |
| kicad-cli configuration dialog | Stage 1 |
| Jobset workspace (4 subtabs) | Stage 2 |
| Report page | Stage 3 |
| Fabrication page | Stage 4 |
| Copy/Create From Existing wizard | Stage 2 (or Stage 1 deferred) |
| Preferences dialog (real) | Future |

---

## 7. Jobset Workflow Review

### 7.1 Tab Structure

The four-tab structure — Dashboard, Setup & Run, Results, Output Log — is well-designed
and internally consistent. It correctly keeps jobset execution and generated output
review inside the Jobset workspace, removing the older `JS Results` sidebar entry.

**Confirmed design decisions:**

- `JS Results` as a standalone sidebar item is removed. ✅
- Results is an internal Jobset subtab. ✅
- Output Log is an internal Jobset subtab. ✅

### 7.2 `.kicad_jobset` Selection

The Setup & Run tab shows a `[Select Jobset...]` button. This button should:

1. Open a file picker filtered to `*.kicad_jobset`.
2. Allow selection from any tokenized path (not restricted to `specgen/` folder).
3. Store the selected path as a token reference in `.kicad_specgen` → `jobset.active_jobset`.
4. Never modify the `.kicad_jobset` file.

**Gap:** There is no defined behavior for what happens when `[Select Jobset...]`
is used and the new jobset has different destination IDs than those previously
stored in `.kicad_specgen` → `jobset.destinations`. A reconciliation strategy
is needed:

- Keys in `destinations` that no longer exist in the new jobset should be flagged
  as stale (and optionally pruned).
- New destination IDs from the new jobset should be added with default overrides.

### 7.3 Destination ID Parsing and Storage

Destination IDs come from `.kicad_jobset` → `outputs[].id`.

SpecGen stores per-destination overrides in `.kicad_specgen` → `jobset.destinations`
keyed by destination ID. This is correct and clean.

**Confirmed:** SpecGen must never write back to `.kicad_jobset`. ✅

### 7.4 Output File Scanning

The Results tab scans `JOBSET_OUTPUT_DIR` for generated files. The wireframe shows
a tree view grouped by output type folder (sch/, bom/, pcb/, gerbers/, 3d/).

**Gap:** The folder structure shown in the wireframe (`jobset_output/release_default/`)
assumes a specific folder layout. The actual structure depends on the jobset output
path settings. The file scanner must derive the structure from `JOBSET_OUTPUT_DIR`
dynamically, not assume a fixed layout.

**Gap:** The Results tab shows file status symbols (✓ ⚠ x). The stale-file detection
logic ("BOM output exists but is older than the active .kicad_sch file") requires
access to `.kicad_sch` file modification time. This means the Results tab implicitly
needs to know the KiCad project source file paths. This dependency should be
documented.

### 7.5 Output Log → Logs Page Relationship

The Jobset Window notes (line 155-156) say the Output Log feeds the Logs workspace
page for persistence. This cross-page relationship requires:

- A shared log service (not per-tab logging).
- The Logs page subscribes to the same log stream.
- The Output Log subtab shows the most recent jobset run log.
- The Logs page aggregates all log sources.

This should be defined in the logging architecture before Stage 2 begins.

---

## 8. Help System Review

### 8.1 Markdown Structure

`SpecGen_Help_JinJa.md` demonstrates the correct help file style: level-1 heading for the
title, level-2 headings for sections, fenced code blocks, bullet lists, and tables.
All help files should follow this style.

### 8.2 Required Help Topics — Stage 1

| Help File | Required for Stage 1? | Notes |
|---|---|---|
| `index.md` | ✅ Yes | Entry point; must exist |
| `getting_started.md` | ✅ Yes | Essential for first-run users |
| `project_setup_tokens.md` | ✅ Yes | Tokens are core to Stage 1 |
| `configure_environments.md` | ✅ Yes | Dialog is Stage 1 |
| `project_page.md` | ✅ Yes | Page is Stage 1 |
| `variables_jinja.md` | ✅ Yes | Page is Stage 1; Jinja is a key concept |
| `jobset.md` | Placeholder OK | Feature is Stage 2 |
| `report.md` | Placeholder OK | Feature is Stage 3 |
| `fabrication.md` | Placeholder OK | Feature is Stage 4 |
| `logs.md` | ✅ Yes | Page is Stage 1 |
| `troubleshooting.md` | ✅ Yes | Critical for user self-service |
| `kicad_specgen_local.md` | ✅ Yes | Key file; users need to understand it |
| `project_kicad_specgen.md` | ✅ Yes | Key file |

### 8.3 Jinja2 vs. Token Syntax Distinction

Help content must clearly distinguish:

- SpecGen path tokens: `{KSG_COMPANY_DIR}/path` — single braces, resolved at runtime
- Jinja2 template variables: `{{ variable_name }}` — double braces, resolved during rendering

This distinction is a likely source of user confusion and must be explained
prominently in `variables_jinja.md` and `project_setup_tokens.md`.

### 8.4 Help Rendering Requirements

For Stage 1, `QTextBrowser` with `markdown` format support is sufficient for the
specified Markdown elements (headings, paragraphs, bullets, numbered lists, tables,
code blocks, links, horizontal rules).

Limitation to document: `QTextBrowser` has limited table rendering. If complex
tables are needed, test rendering early. A `QWebEngineView` option should be
preserved for later stages.

---

## 9. Recommended Layered Architecture

### 9.1 Layer Stack

```text
┌─────────────────────────────────────────────────────────────┐
│  UI Layer                                                   │
│  ui/main_window.py   ui/tabs/   ui/dialogs/   ui/widgets/   │
│  NEVER parses files. NEVER resolves tokens.                 │
│  Calls Services. Emits user intents. Updates from signals.  │
├─────────────────────────────────────────────────────────────┤
│  Services / Use Cases Layer                                 │
│  services/project_service.py                                │
│  services/config_service.py                                 │
│  services/validation_service.py                             │
│  services/jobset_service.py   (Stage 2)                     │
│  services/report_service.py   (Stage 3)                     │
│  services/fab_service.py      (Stage 4)                     │
│  Orchestrates Core. Translates between Core and UI.         │
├─────────────────────────────────────────────────────────────┤
│  Core / Domain Layer                                        │
│  core/platform_paths.py                                     │
│  core/specgen_local_config.py                               │
│  core/specgen_company_config.py                             │
│  core/specgen_user_config.py                                │
│  core/project_config.py                                     │
│  core/token_resolver.py                                     │
│  core/validators.py                                         │
│  core/file_ops.py                                           │
│  core/kicad_pro_parser.py                                   │
│  core/kicad_jobset_parser.py                                │
│  core/kicad_env.py                                          │
│  core/migrations.py                                         │
│  core/logging_utils.py                                      │
│  core/app_state.py                                          │
│  No UI imports. No PySide6. No subprocess.                  │
│  Pure Python. Fully testable without a display.             │
├─────────────────────────────────────────────────────────────┤
│  Setup Layer                                                │
│  setup/setup.py  (entry point)                              │
│  setup/setup_macos.py                                       │
│  setup/setup_linux.py                                       │
│  setup/setup_windows.py                                     │
│  setup/setup_utils.py  (shared with core where possible)    │
│  Standalone bootstrap. Shares Core modules. No UI imports.  │
└─────────────────────────────────────────────────────────────┘
```

### 9.2 Core Layer — Module Responsibilities

| Module | Responsibility | Must Not Do |
|---|---|---|
| `platform_paths.py` | Resolve OS-specific KiCad config dir; detect OS. | No file I/O beyond path construction. |
| `specgen_local_config.py` | Load, validate, save, migrate `kicad_specgen_local.json`. Returns typed dataclass. | No token resolution. No GUI. |
| `specgen_company_config.py` | Load, validate, save `kicad_specgen_company.json`. Returns typed dataclass. | No token resolution. No GUI. |
| `specgen_user_config.py` | Load, validate, save `kicad_specgen_users.json`. Returns typed dataclass. | No token resolution. No GUI. |
| `project_config.py` | Load, validate, save, migrate `.kicad_specgen`. Returns typed dataclass. | No token resolution. No GUI. |
| `token_resolver.py` | Build effective token table. Resolve token references. Report missing tokens. | No file I/O beyond path existence checks. No GUI. |
| `validators.py` | Validate config objects against rules. Return structured results. | No file I/O. No GUI. No side effects. |
| `file_ops.py` | Atomic JSON write. Backup before write. Directory creation. Path existence checks. | No config parsing. No token resolution. |
| `kicad_pro_parser.py` | Parse `text_variables` from `.kicad_pro` JSON. Return dict. | No writes. No GUI. |
| `kicad_jobset_parser.py` | Parse `outputs[]` from `.kicad_jobset` JSON. Return list of destinations. | No writes. No GUI. |
| `kicad_env.py` | Read `environment.vars` from `kicad_common.json`. | No writes during normal operation. |
| `migrations.py` | Schema version migration functions. `migrate_v{from}_to_v{to}(data)`. | No file I/O. Pure data transforms. |
| `logging_utils.py` | Configure Python `logging`. Emit structured log records. | No GUI. |
| `app_state.py` | Single mutable in-memory application state object. Holds resolved tokens, active configs, dirty flags. | No file I/O. No GUI. Must be observable (signals or callbacks). |

### 9.3 Services Layer — Module Responsibilities

| Module | Responsibility | Inputs | Outputs |
|---|---|---|---|
| `project_service.py` | Open, create, save, close project. Orchestrates: load local config → load company → load users → load project → resolve tokens → validate. | File paths, user intents. | Updated `app_state`. Structured result objects. |
| `config_service.py` | Edit and save `kicad_specgen_local.json` and `kicad_specgen_company.json`. Coordinate writes, backups, and state refresh. | Edit intents from UI. | Updated configs. Write results. |
| `validation_service.py` | Run full project validation. Aggregate results from core validators. | `app_state`. | Structured validation report. |
| `jobset_service.py` (Stage 2) | Run `kicad-cli jobset run`. Parse output. Update `app_state`. | Jobset run config. | Run results, log entries. |

### 9.4 UI Layer — Module Responsibilities

| Module | Responsibility | Must Not Do |
|---|---|---|
| `main_window.py` | QMainWindow. Menu bar. Sidebar. Tab widget. Status bar. Wire signals from Services to pages. | No direct file I/O. No config parsing. |
| `ui/tabs/project_tab.py` | Display project state. Emit save/validate/configure intents. | No direct config access. |
| `ui/tabs/variables_tab.py` | Display and edit variables. Emit save intents. | No direct config access. |
| `ui/tabs/jobset_tab.py` (Stage 2) | Host 4 subtabs. Display jobset state. Emit run intents. | No subprocess calls. |
| `ui/dialogs/configure_env_dialog.py` | Edit local tokens. Emit save intent to `config_service`. | No direct file writes. |
| `ui/dialogs/missing_tokens_dialog.py` | Display missing tokens. Emit repair intents. | No direct token resolution. |
| `ui/dialogs/new_project_dialog.py` | Collect new project parameters. Emit create intent. | No direct file creation. |
| `ui/dialogs/help_dialog.py` | Load and render Markdown help file. | No config access. |
| `ui/widgets/token_table.py` | Reusable token table widget. Display-only. | No config writes. |
| `ui/widgets/validation_panel.py` | Display validation results. | No validation logic. |
| `ui/widgets/log_viewer.py` | Display log records from logging service. | No log generation. |

---

## 10. Recommended Implementation Stages

### Stage 0 — Documentation Completion (Required before coding)

**Scope:** Close all critical gaps in the document set.

**Deliverables:**

1. Write `SpecGen_Setup_Process.md`: Full setup process specification to replace
   the Under Construction §16. Must define: first-run detection, company/user
   storage creation, standalone vs. repo mode decision, `kicad_specgen_local.json`
   creation, `kicad_specgen_company.json` and `kicad_specgen_users.json` creation
   for standalone mode, minimum valid company file.

2. Update `SpecGen_File_Framework.md`: Fix §12.4 TOML bracket notation → JSON keys.
   Fix §18 `KICAD_COMMON_DIR` copy-paste error. Add standalone mode company file
   behavior.

3. Update `SpecGen_GUI_Menus.md`: Redesign New Project dialog to use
   `kicad_specgen_company.json` environments. Remove `KSG_SPECGEN_COMMON`.
   Resolve Configure Environments scope conflict (Option A or B from §6.2).

4. Update `SpecGen_Application.md`: Remove `Results (Jobset
   subtab)` from sidebar list and View menu. Expand Edit menu to include
   `Configure kicad-cli` and `Validate Project`. Expand Help menu. Expand module
   layout to include missing modules.

5. Produce a `SpecGen_Terminology.md`: Short canonical list of all current token
   names, file names, and GUI labels. Used as a reference during implementation to
   prevent terminology drift.

**Acceptance criteria:**

- No Under Construction sections remain in Framework.
- No stale token names remain in any document.
- Configure Environments scope is resolved and documented.
- New Project dialog is redesigned and documented.

---

### Stage 1 — Foundation (Core + Shell)

**Scope:** Core modules, setup bootstrap, application shell, Project page,
Variables page, Logs page, all Stage 1 dialogs.

**Files/modules to create:**

```text
main.py
app.py

core/
  platform_paths.py
  specgen_local_config.py
  specgen_company_config.py
  specgen_user_config.py
  project_config.py
  token_resolver.py
  validators.py
  file_ops.py
  kicad_pro_parser.py
  kicad_env.py
  migrations.py
  logging_utils.py
  app_state.py

services/
  project_service.py
  config_service.py
  validation_service.py

setup/
  setup.py
  setup_macos.py
  setup_linux.py
  setup_windows.py
  setup_utils.py

ui/
  main_window.py
  sidebar.py
  theme.py
  actions.py

  tabs/
    project_tab.py
    variables_tab.py
    logs_tab.py
    jobset_tab.py      (placeholder)
    report_tab.py      (placeholder)
    fabrication_tab.py (placeholder)

  dialogs/
    configure_env_dialog.py
    missing_tokens_dialog.py
    new_project_dialog.py
    about_dialog.py
    help_dialog.py
    kicad_cli_dialog.py

  widgets/
    token_table.py
    path_field.py
    validation_panel.py
    readonly_table.py
    log_viewer.py

help/
  index.md
  getting_started.md
  project_setup_tokens.md
  configure_environments.md
  project_page.md
  variables_jinja.md
  logs.md
  troubleshooting.md
  kicad_specgen_local.md
  project_kicad_specgen.md
  jobset.md             (placeholder content)
  report.md             (placeholder content)
  fabrication.md        (placeholder content)

tests/
  test_platform_paths.py
  test_specgen_local_config.py
  test_specgen_company_config.py
  test_specgen_user_config.py
  test_project_config.py
  test_token_resolver.py
  test_validators.py
  test_migrations.py
  test_kicad_pro_parser.py
  test_kicad_env.py
  fixtures/
    sample_local.json
    sample_company.json
    sample_users.json
    sample_project.kicad_specgen
    sample_kicad_pro.json
```

**Acceptance criteria:**

- `setup.py` runs without error on macOS, Linux, and Windows (or at least one
  platform to start).
- `kicad_specgen_local.json` is created correctly by setup.
- Application starts and shows main window.
- Project page loads and displays a project opened from a `.kicad_specgen` file.
- Effective token table is populated and displayed.
- Missing token triggers the Missing Tokens dialog.
- Variables page displays KiCad text variables read-only and custom variables as
  editable.
- Configure Environments dialog saves changes to `kicad_specgen_local.json`.
- Save and Save As work correctly.
- Open Recent shows last session.
- Logs page shows application log entries.
- All Stage 1 help files render in the Help dialog.

**Manual test steps:**

1. Run `setup.py` on a clean machine. Verify `kicad_specgen_local.json` is created.
2. Start the application with no previous session. Verify prompt to create/open project.
3. Create a new project in a KiCad project folder. Verify `.kicad_specgen` is created
   under `specgen/`.
4. Open the project. Verify Project page shows correct paths.
5. Introduce a missing token reference. Verify Missing Tokens dialog appears.
6. Add the token via the dialog. Verify `kicad_specgen_local.json` is updated.
7. Verify the project `.kicad_specgen` file is not modified by the token addition.
8. Edit a custom variable. Save. Reopen. Verify variable is persisted.
9. Open Help → Getting Started. Verify Markdown renders correctly.

**Automated test expectations:**

- Token resolution with all five required tokens present: passes.
- Token resolution with one missing token: returns structured missing token report.
- Protected token in `kicad_specgen_local.json.tokens`: validation fails with clear
  error.
- Absolute path in `kicad_specgen_company.json.paths`: validation fails.
- `recent_projects` exceeding 10 items: oldest entry is removed.
- `schema_version` missing: treated as version 1.
- `.kicad_specgen` not under a `specgen/` folder: validation fails.

**Risks:**

- Setup process is the highest-risk item because §16 is Under Construction.
  Do not begin `setup.py` implementation until `SpecGen_Setup_Process.md` is
  written and approved.
- `QTextBrowser` Markdown table rendering may require testing early.
- The Configure Environments scope conflict (local tokens vs. company environments)
  must be resolved before the dialog is implemented.

**What not to implement yet:**

- Jobset execution.
- `.kicad_jobset` parsing.
- Report pipeline.
- Fabrication packaging.
- Copy / Create From Existing wizard.

---

### Stage 2 — Jobset and Results

**Scope:** Jobset workspace (all 4 subtabs), `.kicad_jobset` parsing, `kicad-cli`
integration, generated output scanning.

**New modules:**

```text
core/kicad_jobset_parser.py
services/jobset_service.py
ui/tabs/jobset_tab.py (full implementation)
ui/widgets/output_tree.py
ui/widgets/file_preview.py
```

**Acceptance criteria:**

- Jobset workspace shows Dashboard with correct project/jobset/output info.
- Setup & Run tab shows destination table populated from `.kicad_jobset`.
- Run All executes `kicad-cli jobset run` and shows output in Output Log.
- Results tab shows generated files with correct status symbols.
- Destination overrides (selected, heading, notes) are saved in `.kicad_specgen`.
- Jobset file is never modified.
- Stale destination keys are detected and flagged.

---

### Stage 3 — Report Generation

**Scope:** Report page, report recipe, Jinja2 template rendering, PDF assembly.

**New modules:**

```text
services/report_service.py
ui/tabs/report_tab.py (full implementation)
core/render/jinja_renderer.py
core/render/pdf_assembler.py
```

---

### Stage 4 — Fabrication Packaging

**Scope:** Fabrication page, FAB output mapping, Gerber zip, checksums, README.

**New modules:**

```text
services/fab_service.py
ui/tabs/fabrication_tab.py (full implementation)
core/fab/package_builder.py
```

---

## 11. Testing Strategy

### 11.1 Test Principles

- Core layer modules must be testable without a display server (no PySide6).
- Tests use fixture files, not live KiCad installations.
- Token resolver tests cover all five layers of the resolution precedence stack.
- Schema validation tests use the JSON schemas from `SpecGen_Schema_Definitions.md`.
- Migration tests verify each version-to-version transform independently.

### 11.2 Core Module Tests

| Test File | Test Cases |
|---|---|
| `test_platform_paths.py` | OS detection, KiCad config dir paths for Windows/macOS/Linux, KiCad version detection |
| `test_specgen_local_config.py` | Load valid file, load missing file, load file with missing schema_version, reject protected token in tokens section, reject non-absolute path in tokens, reject non-KSG token name, recent_projects capped at 10, oldest entry removed when cap exceeded |
| `test_specgen_company_config.py` | Load valid file, reject absolute paths in paths section, validate environment type enum, validate company_id non-empty, load standalone minimal file |
| `test_specgen_user_config.py` | Load valid file, reject duplicate worker_id, warn on active_user not in users list, reject absolute paths in user paths |
| `test_project_config.py` | Load valid file, reject file not under specgen/ folder, derive KSG_PROJECT_SPECGEN_DIR correctly, derive KICAD_PROJECT_DIR correctly, reject absolute paths in files section, validate custom variable name pattern, load file with unknown schema_version (warn but load) |
| `test_token_resolver.py` | Resolve simple reference, resolve nested reference, report missing token, precedence: runtime tokens override local tokens, precedence: local tokens override kicad_common vars, protected tokens cannot be user-defined |
| `test_validators.py` | Validate all required tokens present, validate required tokens missing, validate kicad-cli path exists, validate recent project paths, validate project under specgen/ folder |
| `test_migrations.py` | migrate_v1_to_v2 (once v2 exists), missing schema_version treated as v1 |
| `test_kicad_pro_parser.py` | Parse text_variables from fixture .kicad_pro, handle missing text_variables, handle multiple .kicad_pro files in directory |
| `test_kicad_env.py` | Load environment.vars from fixture kicad_common.json, handle missing environment section |

### 11.3 Integration Tests

| Test | Description |
|---|---|
| Full project open sequence | Load all four config files in correct order, build effective token table, open fixture project |
| Missing token repair flow | Introduce missing token, call Missing Tokens handler, verify kicad_specgen_local.json updated, verify project file unchanged |
| Recent projects management | Open 11 projects in sequence, verify list stays at 10 |
| Save As flow | Save project to new path, verify new file exists under specgen/, verify original unchanged |
| Setup bootstrap (headless) | Run setup_utils with fixture paths, verify kicad_specgen_local.json created correctly |

### 11.4 GUI Smoke Tests

Where practical (CI with a virtual display):

- Application starts without crash.
- Project tab loads with fixture project.
- Missing Tokens dialog opens when token is missing.
- Configure Environments dialog opens and saves.
- Help dialog opens and renders `index.md`.
- About dialog opens.

### 11.5 Migration and Terminology Tests

- Grep-based test: verify no file in `core/` or `ui/` contains the old token name
  `KICAD_SPECGEN_DIR`.
- Grep-based test: verify no file uses `kicad_specgen.json` (old local config name).
- Grep-based test: verify no file uses `KSG_SPECGEN_COMMON` (old token name).

---

## 12. Prioritized Gap List

### Critical (blocks Stage 0 and Stage 1)

| # | Description | Source | Recommended Action |
|---|---|---|---|
| C1 | Setup process (Framework §16) is Under Construction | Framework §16 | Write `SpecGen_Setup_Process.md` before any Stage 1 coding that touches `kicad_specgen_local.json` creation |
| C2 | Configure Environments dialog scope conflict: edits both `kicad_specgen_local.json` tokens AND `kicad_specgen_company.json` environments without a defined split | Pulldown Menus, App Description | Choose Option A or B from §6.2 and document it before dialog implementation |
| C3 | New Project dialog references `KSG_SPECGEN_COMMON` (stale token) and inline environment creation (inconsistent with current model) | Pulldown Menus | Redesign dialog against current framework before implementation |

### High (should be resolved before Stage 1 coding)

| # | Description | Source | Recommended Action |
|---|---|---|---|
| H1 | Standalone/hobby mode: startup sequence (§7, step 5) requires opening `kicad_specgen_company.json` but §2.1 says hobby users may operate without a company repository | Framework §2.1 and §7 | Define minimum company file for standalone mode, or define how startup sequence handles missing company file gracefully |
| H2 | Framework §18 copy-paste error: `KICAD_COMMON_DIR` token is defined as pointing to the `.json` file itself instead of the directory | Framework §18 | Fix the three platform entries in §18 |
| H3 | Framework §12.4 uses TOML `[section]` headers instead of JSON key notation | Framework §12.4 | Update to use JSON key notation for clarity |
| H4 | `JOBSET_OUTPUT_DIR` derivation uses `outputs[0]` — ambiguous when outputs have different paths | Schema Definitions §6 | Define: validate all outputs share a common root path; warn if they do not; use first as representative |
| H5 | `Results (Jobset subtab)` still listed as a sidebar item in App Description | App Description sidebar, View menu | Update App Description to remove this as a sidebar item |
| H6 | Dirty-state tracking for project `.kicad_specgen` is not defined | All GUI docs | Define: which fields trigger dirty flag; when is dirty flag cleared |

### Medium (resolve before or during Stage 1)

| # | Description | Source | Recommended Action |
|---|---|---|---|
| M1 | App Description Edit menu missing `Configure kicad-cli` and `Validate Project` items that are in Pulldown Menus | App Description | Update App Description Edit menu |
| M2 | App Description Help menu is much less complete than Pulldown Menus Help menu | App Description | Update App Description Help menu |
| M3 | App Description module layout is missing several modules | App Description | Update module layout list |
| M4 | No defined behavior for multiple `.kicad_pro` files found in `KICAD_PROJECT_DIR` | Schema Definitions §6 | Define: list all found; require user to select; warn if none found |
| M5 | `report.pages.order` validation: "known identifiers" list is not defined | Schema Definitions §5 | Define the list of valid built-in identifiers vs. user-defined page IDs |
| M6 | `Jinja2 {{ }}` vs. SpecGen `{ }` token syntax distinction is not documented for users | SpecGen_Help_JinJa.md (style) | Add explicit section to `variables_jinja.md` help file |
| M7 | Results tab wireframe is missing the Output Log tab in its tab bar | Jobset Window | Fix wireframe |
| M8 | Jobset wireframe shows `{KICAD_PROJECT_DIR}/{JOBSET_OUTPUT_DIR}` — incorrect nesting | Jobset Window | Fix wireframe display string |
| M9 | Output Log → Logs page persistence relationship is not architecturally defined | Jobset Window | Define shared log service before Stage 2 |
| M10 | `Copy / Create From Existing Project` is in Pulldown Menus but not in App Description File menu | App Description | Add item to File menu in App Description; confirm Stage |

### Low (resolve before or during relevant stage)

| # | Description | Source | Recommended Action |
|---|---|---|---|
| L1 | Help file versioning not explicitly stated | Pulldown Menus | Document: help files are versioned with the app repository |
| L2 | Setup entry point invocation (`python setup.py` vs. wrapper) not defined | App Description, Help | Define and document the canonical setup invocation |
| L3 | `getting_started.md` references running `setup.py` | Pulldown Menus | Update once entry point is defined |
| L4 | KiCad version detection (beyond `9.0`) not defined | Platform paths | Document: detect KiCad config folder version dynamically or default to `9.0` |
| L5 | `active_environment` fallback when no project is open | All docs | Define: use `kicad_specgen_local.json.active_environment` as fallback |
| L6 | `sandbox` environment with no client or team key — no validation rule | Company schema | Add: `sandbox` type environments require no `client` or `team` key |

### Future (not needed before Stage 2)

| # | Description | Source | Recommended Action |
|---|---|---|---|
| F1 | KiCad jobset format version not pinned | Schema Definitions §6 | Pin expected format; add format version check when KiCad updates |
| F2 | Stale destination key reconciliation when jobset changes | Framework §14 | Define reconciliation strategy for Stage 2 |
| F3 | Output file scanning: stale-file detection requires `.kicad_sch` mod time | Jobset Window | Document dependency; implement in Stage 2 |
| F4 | `QTextBrowser` table rendering limitations | Pulldown Menus | Test early; plan `QWebEngineView` migration if needed |
| F5 | User management GUI (add/remove users in `kicad_specgen_users.json`) | Framework §11 | Not needed for Stage 1; define dialog for Stage 2 or later |

---

## 13. Questions That Must Be Answered Before Coding

These questions require decisions by the project owner. They cannot be resolved by
inference from the existing documents.

1. **Setup process:** What is the exact user experience for a first-run user on a
   machine with no `kicad_specgen_local.json`? Does the main application launch a
   setup wizard inline, or does the user run a separate `setup.py`? The Framework
   implies `setup.py` runs first and the main app checks for `setup_complete = true`.
   Confirm this model.

2. **Standalone hobby mode — company file:** In standalone mode with no shared
   company repository, does `kicad_specgen_company.json` still exist as a local
   file? If yes, where? If no, how does the startup sequence handle step 5 (open
   company file)?

3. **Configure Environments dialog scope:** Option A (single dialog with two tabs)
   or Option B (two separate menu items) for separating local token editing from
   company environment editing?

4. **New Project dialog — environment selection:** The dialog should let the user
   select from `kicad_specgen_company.json.environments`. Is it also required to
   let the user create a new environment inline in this dialog, or should environment
   creation be in the Configure Environments dialog only?

5. **`JOBSET_OUTPUT_DIR` derivation:** Should SpecGen validate that all jobset
   outputs share the same root path, or is `outputs[0]` always used as the
   representative? What is the user-visible behavior when outputs have different
   paths?

6. **Multiple `.kicad_pro` files:** If `KICAD_PROJECT_DIR` contains more than one
   `.kicad_pro` file, should SpecGen: auto-select the one matching the project name,
   prompt the user to select, or show an error?

7. **`KSG_PROJECT_SPECGEN_DIR` vs. `SPECGEN_PROJECT_DIR`:** The prompt asks about
   this rename. Recommendation is to keep `KSG_PROJECT_SPECGEN_DIR`. Confirm.

8. **Dirty state triggers:** Which changes to the project `.kicad_specgen` set the
   dirty flag? All changes? Only certain sections? Define before Project page
   implementation.

9. **Jobset destination reconciliation:** When the user selects a new `.kicad_jobset`
   with different destination IDs, should stale `.kicad_specgen.jobset.destinations`
   keys be: silently pruned, flagged with a warning, or kept for potential re-use?

10. **Setup entry point:** Is the canonical invocation `python setup.py`, `python
    -m setup`, or a shell script wrapper? This affects the `getting_started.md`
    help file and the application's first-run prompt.

---

## 14. Recommended Next Document to Write

**Write `SpecGen_Setup_Process.md` next.**

This is the highest-priority gap. The setup process is explicitly Under Construction
(Framework §16) and it blocks:

- Stage 1 `setup.py` implementation.
- `kicad_specgen_local.json` creation logic.
- First-run startup behavior.
- `getting_started.md` help content.
- Standalone vs. repo mode initialization.

The Setup Process document should cover:

1. Entry point invocation.
2. OS detection and platform dispatch.
3. Dependency stage installation.
4. `kicad-cli` detection (macOS, Linux, Windows).
5. KiCad config folder detection and `KICAD_COMMON_DIR` resolution.
6. Standalone vs. repo mode decision (user prompt).
7. `kicad_specgen_company.json` and `kicad_specgen_users.json` creation for
   standalone mode (minimum valid files).
8. `kicad_specgen_local.json` creation or update.
9. Required `KSG_*` token collection.
10. Validation after setup.
11. First-run help reference.
12. Re-run behavior (update existing config vs. start fresh).
13. Headless / no-prompt mode for CI environments.

After the Setup Process document is approved:

- Fix the three medium-priority document issues (H2, H3, H5) in the Framework and
  App Description.
- Resolve the Configure Environments scope conflict (C2).
- Redesign the New Project dialog (C3).
- Then proceed to Stage 1 implementation.

---

*End of Architecture Review and Implementation Plan.*
