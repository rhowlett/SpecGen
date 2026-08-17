# KiCad SpecGen — Architecture Review and Implementation Plan

> Produced by Claude (Anthropic) from analysis of all attached design documents.
> Primary source of truth: `SpecGen_File_Framework.md`
> Use this document to track gap closure and stage completion.

---

## 1. Executive Summary

This is a well-conceived application with a strong, detailed framework document. The architecture direction in `SpecGen_File_Framework.md` is sound and implementable. However, the four supporting documents contain accumulated terminology drift, TOML/JSON inconsistency, outdated token names, and conflicting file references that would cause serious confusion if implementation began today without reconciliation.

The most critical issues are:

- **The local config file has two names** — `kicad_specgen.json` (old) vs `kicad_specgen_local.json` (current) — used interchangeably across all four supporting documents. This single ambiguity would generate bugs in every layer.
- **The `.kicad_specgen` example in the framework is still TOML**, not JSON. This contradicts the stated JSON preference and leaves the project file schema undefined.
- **`KICAD_SPECGEN_DIR` vs `KSG_PROJECT_SPECGEN_DIR`** — the old protected token name appears in every supporting document and in the framework's own wireframe.
- **The environment model changed** — the older documents use a flat `environments` dict inside `kicad_specgen.json`; the framework now uses separate `kicad_specgen_company.json` and `kicad_specgen_users.json` files. The dialogs in the supporting documents still reference the old model.
- **Setup is marked "Under Construction"** in the framework but is fully described (incorrectly) in the application description.
- **No JSON schema exists** for any file. Without schemas, token validation, migration detection, and automated testing cannot be built cleanly.

Implementation can proceed in Stage 1 if the terminology table is resolved and the `.kicad_specgen` JSON schema is defined first. Do not start writing application code until those two items are complete.

---

## 2. Source-of-Truth Assessment

| Document | Role | Current Usefulness | Authority Level |
|---|---|---|---|
| `SpecGen_File_Framework.md` | Architecture specification | High — defines the target | **Primary authority** |
| `kicad_specgen_application_description.md` | Application reference manual | Medium — good structural description, stale config model | Supporting reference |
| `SpecGen_Pulldown_Menus.md` | GUI menu and help design | Medium — good intent, stale token names | Supporting reference |
| `SpecGen_Jobset_Window.md` | Jobset wireframes | High value — clear layout, one stale token | Supporting reference |
| `Help_JinJa.md` | Help file format example | High — ready to use as-is | Supporting reference |

---

## 3. Document-by-Document Review

### `SpecGen_File_Framework.md`

**Purpose:** Defines the authoritative configuration model, token framework, file ownership, open sequence, and validation rules.

**Current sections (implement as written):**
- Sections 2–6: User types, installation model, token framework, required/protected tokens
- Section 7: File open and token resolution sequence
- Sections 8–14: File chapters for all config files
- Section 15: Company/user storage structure
- Section 17: Validation requirements
- Section 18: Required core modules

**Outdated or incomplete:**
- Section 12.5: `.kicad_specgen` example is TOML, not JSON. Explicitly marked `TODO`.
- Section 16: Setup process marked `TODO - Under Construction`.
- Dashboard wireframe in Jobset window uses `{KICAD_SPECGEN_DIR}` instead of `{KSG_PROJECT_SPECGEN_DIR}`.

**Missing:**
- Full JSON schema for each file (required fields, types, validation rules)
- Example `.kicad_specgen` file in JSON
- Token resolution precedence when tokens appear in multiple sources
- `schema_version` migration strategy

---

### `kicad_specgen_application_description.md`

**Purpose:** Application reference manual describing the full application structure and Stage 1 scope.

**Current sections (still useful):**
- Application overview, main window layout, sidebar/tabwidget structure
- Stage 1 scope list
- Module layout recommendation (`core/`, `ui/`, `setup/`, `dialogs/`, `widgets/`, `tabs/`)
- Implementation requirements (dataclasses, pathlib, type hints, PEP 8)
- Future stage descriptions

**Outdated:**
- Uses `kicad_specgen.json` throughout (old name, should be `kicad_specgen_local.json`)
- Token model uses flat `environments` dict inside one local file — framework now uses three separate files
- `Configure Environments` dialog edits `kicad_specgen.json` environments — now incorrect
- Resolution order references `kicad_specgen.json environment tokens` — now `kicad_specgen_company.json + kicad_specgen_users.json`
- `KSG_DIR`, `KSG_WORKSPACE`, `KSG_SPECGEN_DIR`, `KSG_SPECGEN_COMMON` listed as tokens — all outdated names
- `KICAD_SPECGEN_DIR` listed as protected derived token — correct concept, wrong name
- `JS Results` listed as a separate sidebar page — wireframe correctly uses `Results` as subtab of `Jobset`

---

### `SpecGen_Pulldown_Menus.md`

**Purpose:** Menu bar design, dialog wireframes, and help system requirements.

**Current sections (ready to use):**
- File menu structure — correct
- Help system requirements REQ-HELP-001 through REQ-HELP-006 — ready to implement
- Help file topic list — complete
- Menu-to-dialog mapping table — good reference

**Outdated:**
- `New SpecGen Project` dialog references `{KSG_SPECGEN_DIR}` — should be `{KSG_APP_DIR}`
- `Open SpecGen Project` describes deriving `KICAD_SPECGEN_DIR` — should be `KSG_PROJECT_SPECGEN_DIR`
- `Open Recent` stores paths in `kicad_specgen.json` — correct concept, wrong filename
- `Configure Environments` dialog edits `kicad_specgen.json` named environments — should be `kicad_specgen_company.json`
- Protected tokens list includes `KICAD_SPECGEN_DIR` — should be `KSG_PROJECT_SPECGEN_DIR`
- `Resolve Missing Tokens` writes to `kicad_specgen.json -> environments.<env>.tokens` — should write to `kicad_specgen_local.json -> tokens`
- Help file `project_kicad_specgen.md` references TOML — should say JSON
- Help file `kicad_specgen_json.md` uses old filename
- `TODO finish` on New SpecGen Project dialog — incomplete spec

---

### `SpecGen_Jobset_Window.md`

**Purpose:** Wireframe layouts for the Jobset workspace.

**Current (ready to implement):**
- Dashboard, Setup & Run, Results layouts are clear and accurate
- Job table columns are well specified

**Outdated:**
- Dashboard shows `{KICAD_SPECGEN_DIR}` — should be `{KSG_PROJECT_SPECGEN_DIR}`
- Setup & Run shows same stale token
- Output Log subtab referenced but no wireframe shown

---

### `Help_JinJa.md`

**Status:** Ready to use as-is. Ship as `help/variables_jinja.md` with minor SpecGen token examples added.

---

## 4. Terminology and Naming Corrections

** <-- DONE Stage 0: Apply all corrections below to all documents **

| Old Term | Correct Term | Appears In | Why It Matters | Recommended Action |
|---|---|---|---|---|
| `kicad_specgen.json` | `kicad_specgen_local.json` | App description, Pulldown menus, Framework §8.6 | Every config load/save call uses wrong filename | Global find/replace before any code |
| `KICAD_SPECGEN_DIR` | `KSG_PROJECT_SPECGEN_DIR` | App description, Pulldown menus, Jobset wireframe | Wrong token in resolver causes path failures | Replace everywhere |
| `KSG_DIR` | `KSG_COMPANY_DIR` | App description (repo mode) | Token resolver will not find the root path | Replace |
| `KSG_WORKSPACE` | *(remove — not in framework)* | App description (repo mode) | Undefined token | Remove entirely |
| `KSG_SPECGEN_DIR` | `KSG_APP_DIR` or `KSG_PROJECT_SPECGEN_DIR` | App description (repo mode) | Ambiguous — could mean app dir or project dir | Clarify context, then replace |
| `KSG_SPECGEN_COMMON` | `KSG_USER_COMMON_DIR` | App description (standalone mode) | Wrong token name | Replace |
| `kicad_specgen.json` (as environments store) | `kicad_specgen_company.json` | App description, Pulldown menus | Dialogs edit wrong file | Update all dialog descriptions |
| `KICAD_SPECGEN_DIR` (protected token) | `KSG_PROJECT_SPECGEN_DIR` | App description protected token list | Guard list is wrong | Correct the list |
| `JS Results` (sidebar page) | `Results` (subtab of Jobset) | App description future stages | Wrong navigation structure | Update future stage description |
| `.kicad_specgen` format | JSON (not TOML) | Framework §12.5 (TODO) | Tooling and schema depend on format | Write JSON schema and example |
| `kicad_specgen.json` (help file ref) | `kicad_specgen_local.json` | Pulldown menus help file list | Help describes wrong filename | Rename help file reference |
| `SPECGEN_PROJECT_DIR` (alternative) | `KSG_PROJECT_SPECGEN_DIR` | Framework (unresolved question) | Decision deferred — consistency wins | Use `KSG_PROJECT_SPECGEN_DIR` |

** DONE --> **

---

## 5. Configuration/File Framework Gaps

** <-- DONE Stage 0: JSON schemas written for all config files **

### `kicad_specgen_local.json`

| Gap | Status |
|---|---|
| Full JSON schema | **Done — see SpecGen_Schema_local.md** |
| Required vs optional field list | Done |
| Validation rules | Done |
| Example file | Present (Framework §8.6) |
| Read/write ownership | Defined |
| Migration rules | Done |
| GUI editor requirements | Covered by Configure Environments dialog |
| Unit tests | Missing — Stage 1 |

### `kicad_specgen_company.json`

| Gap | Status |
|---|---|
| Full JSON schema | **Done — see SpecGen_Schema_company.md** |
| Required vs optional fields | Done |
| Validation rules | Done |
| Example file | Present (Framework §10.6) |
| Read/write ownership | Defined |
| Multi-user edit conflict handling | Future — flag in Stage 2 |
| Migration rules | Done |
| GUI editor requirements | Configure Environments redesigned |

### `kicad_specgen_users.json`

| Gap | Status |
|---|---|
| Full JSON schema | **Done — see SpecGen_Schema_users.md** |
| Required vs optional fields | Done |
| Validation rules | Done |
| Example file | Present (Framework §11.5) |
| Read/write ownership | Defined |
| Migration rules | Done |

### Project `.kicad_specgen`

| Gap | Status |
|---|---|
| **JSON schema** | **Done — see SpecGen_Schema_project.md** |
| Required vs optional sections | Done |
| Validation rules | Done |
| Example file in JSON | **Done — see SpecGen_Schema_project.md** |
| Read/write ownership | Defined |
| Portability rules | Defined |
| `.kicad_jobset` change detection | Partially described §12.4 — Stage 2 |
| Migration from TOML | Done — none exist yet |

### `.kicad_pro`

| Gap | Status |
|---|---|
| `text_variables` parsing spec | Defined in schema docs |
| Which fields SpecGen reads | Listed |
| Handling of missing `.kicad_pro` | Defined |
| No write rules | Defined (read-only) |

### `.kicad_jobset`

| Gap | Status |
|---|---|
| JSON structure spec for parsing | Defined in schema docs |
| Destination ID parsing rules | Defined |
| Output file type mapping | Defined |
| No write rules | Defined (read-only) |

### `kicad_common.json`

| Gap | Status |
|---|---|
| Which `environment.vars` keys SpecGen reads | Listed |
| Handling of missing file | Defined |
| Backup naming | Defined in Framework §9.2 |

** DONE --> **

---

## 6. GUI Framework Gaps

** <-- DONE Stage 0: Configure Environments dialog redesigned for correct files **

### Consistent with framework

- Top menu bar `[File] [Edit] [View] [Help]`
- Sidebar navigation `[Project] [Variables] [Jobset] [Report] [Fabrication] [Logs]`
- `QMainWindow` + `QTabWidget`
- `Results` as subtabs of `Jobset`
- Help as Markdown dialog

### Corrected in Stage 0

| GUI Area | Fix Applied |
|---|---|
| Configure Environments dialog | Redesigned to target `kicad_specgen_company.json`; token edits → `kicad_specgen_local.json` |
| Missing Tokens dialog | Write target corrected to `kicad_specgen_local.json -> tokens` |
| New SpecGen Project dialog | `{KSG_SPECGEN_DIR}` replaced with `{KSG_APP_DIR}` |
| Open Recent | Filename corrected to `kicad_specgen_local.json` |
| Project page token source description | Updated for three-file model |

### Actions by write target

| Action | Writes To |
|---|---|
| Configure Environments — token table edits | `kicad_specgen_local.json` (tokens section) |
| Configure Environments — company/environment edits | `kicad_specgen_company.json` |
| Configure kicad-cli path | `kicad_specgen_local.json` (tools section) |
| Resolve Missing Tokens | `kicad_specgen_local.json` (tokens section) |
| Edit Project Metadata, Custom Variables | Project `.kicad_specgen` |
| Save / Save As | Project `.kicad_specgen` |
| Recent Projects, last session | `kicad_specgen_local.json` |
| User profile edits | `kicad_specgen_users.json` |

** DONE --> **

---

## 7. Jobset Workflow Review

** <-- DONE Stage 0: Jobset wireframe token corrected **

- `{KICAD_SPECGEN_DIR}` replaced with `{KSG_PROJECT_SPECGEN_DIR}` in Dashboard and Setup & Run
- Output Log added as 4th subtab in wireframe
- SpecGen stores destination overrides in `.kicad_specgen`, never writes to `.kicad_jobset`

### What SpecGen stores in `.kicad_specgen` for jobset

```json
{
  "jobset": {
    "active_jobset": "{KSG_PROJECT_SPECGEN_DIR}/release_default.kicad_jobset",
    "stop_on_error": true,
    "destinations": {
      "sch_pdf":  { "selected": true,  "heading_override": "Schematics", "notes": "" },
      "bom_csv":  { "selected": true,  "heading_override": "BOM",        "notes": "Used in FAB" },
      "gerbers":  { "selected": false, "heading_override": "",            "notes": "" }
    }
  }
}
```

** DONE --> **

---

## 8. Help System Review

- `Help_JinJa.md` is ready to ship as `help/variables_jinja.md`
- Stub help files created for Stage 1 topics
- Rule: A feature is not complete until its help topic exists or is updated

### Help file status

| File | Stage | Status |
|---|---|---|
| `help/index.md` | 1 | Written (stub) |
| `help/getting_started.md` | 1 | Written (stub) |
| `help/project_setup_tokens.md` | 1 | Written |
| `help/configure_environments.md` | 1 | Written |
| `help/variables_jinja.md` | 1 | Ready (from Help_JinJa.md) |
| `help/troubleshooting.md` | 1 | Written (stub) |
| `help/kicad_specgen_local.md` | 1 | Written |
| `help/project_kicad_specgen.md` | 1 | Written (JSON, not TOML) |
| `help/logs.md` | 1 | Written (stub) |
| `help/jobset.md` | 2 | Placeholder |
| `help/report.md` | 3 | Placeholder |
| `help/fabrication.md` | 4 | Placeholder |

---

## 9. Recommended Layered Architecture

```
┌─────────────────────────────────────────────────────────┐
│  UI Layer (PySide6)                                      │
│  main_window, sidebar, dialogs, tabs, widgets            │
│  • Calls services only — no direct config parsing       │
├─────────────────────────────────────────────────────────┤
│  Application State Layer                                 │
│  app_state.py                                            │
│  • Holds loaded config, resolved token table            │
├─────────────────────────────────────────────────────────┤
│  Services / Use Cases Layer                              │
│  OpenProjectService, NewProjectService,                  │
│  SaveProjectService, ResolveTokensService,               │
│  ValidateProjectService, RunJobsetService,               │
│  BuildReportService, BuildFabPackageService              │
├─────────────────────────────────────────────────────────┤
│  Core Config Layer                                       │
│  specgen_local_config.py  — load/save local JSON        │
│  specgen_company_config.py — load/save company JSON     │
│  specgen_user_config.py   — load/save users JSON        │
│  project_config.py        — load/save .kicad_specgen    │
│  kicad_env.py             — read kicad_common.json      │
│  kicad_pro.py             — read .kicad_pro             │
│  kicad_jobset.py          — read .kicad_jobset          │
├─────────────────────────────────────────────────────────┤
│  Token Resolution Layer                                  │
│  token_resolver.py                                       │
│  • Builds effective token table from all sources        │
│  • Resolves {TOKEN_NAME}/path strings                   │
│  • Reports missing tokens                               │
├─────────────────────────────────────────────────────────┤
│  Validation Layer                                        │
│  validators.py                                           │
│  • Validates schema_version, token names/values         │
│  • Reports structured ValidationResult objects          │
│  • Does not modify state                                │
├─────────────────────────────────────────────────────────┤
│  Infrastructure Layer                                    │
│  platform_paths.py — OS config folder detection         │
│  file_ops.py       — safe read/write/backup             │
│  logging_utils.py  — structured log output             │
└─────────────────────────────────────────────────────────┘
```

---

## 10. Recommended Implementation Stages

### Stage 0 — Foundation documents ✅ COMPLETE

** <-- DONE Stage 0 **

All Stage 0 deliverables:
- [x] Terminology corrections applied to all documents
- [x] `.kicad_specgen` JSON schema written
- [x] `.kicad_specgen` JSON example written
- [x] `kicad_specgen_local.json` formal schema defined
- [x] `kicad_specgen_company.json` formal schema defined
- [x] `kicad_specgen_users.json` formal schema defined
- [x] Configure Environments dialog redesigned for correct files
- [x] `KSG_PROJECT_SPECGEN_DIR` used consistently everywhere

** DONE --> **

---

### Stage 1 — Application shell and project foundation

**Scope:** Config loading, token resolution, project open/save, validation, Project/Variables/Logs pages, dialogs.

**Modules to create:**
```
main.py
app.py
core/platform_paths.py
core/specgen_local_config.py
core/specgen_company_config.py
core/specgen_user_config.py
core/project_config.py
core/kicad_env.py
core/kicad_pro.py
core/token_resolver.py
core/validators.py
core/file_ops.py
core/logging_utils.py
core/app_state.py
ui/main_window.py
ui/sidebar.py
ui/theme.py
ui/tabs/project_tab.py
ui/tabs/variables_tab.py
ui/tabs/logs_tab.py
ui/dialogs/configure_environment_dialog.py
ui/dialogs/missing_tokens_dialog.py
ui/dialogs/new_project_dialog.py
ui/dialogs/about_dialog.py
ui/widgets/token_table.py
ui/widgets/validation_panel.py
ui/widgets/log_viewer.py
help/ (all Stage 1 topics)
setup/setup_macos.py
setup/setup_linux.py
setup/setup_windows.py
```

**Acceptance criteria:**
- Application starts without a project loaded
- Setup detects `kicad-cli` and writes to `kicad_specgen_local.json`
- Opening `.kicad_specgen` derives all protected tokens correctly
- Token resolver resolves all references or triggers Missing Tokens dialog
- Save writes portable `.kicad_specgen` with no absolute paths
- All Stage 1 help topics open and render correctly

---

### Stage 2 — Jobset and Results

Implements: `.kicad_jobset` parsing, jobset run via `kicad-cli`, Results file tree, Output Log.

---

### Stage 3 — Report

Implements: report recipe editing, template variable substitution, PDF generation.

---

### Stage 4 — Fabrication

Implements: FAB output mapping, Gerber zip, BOM conversion, README, checksums.

---

## 11. Testing Strategy

### Unit tests (per module)

| Module | Tests |
|---|---|
| `platform_paths.py` | Correct paths per OS, missing KiCad config dir |
| `specgen_local_config.py` | Load valid, load missing, wrong schema_version, save roundtrip |
| `specgen_company_config.py` | Load valid, missing client section, extra fields |
| `project_config.py` | Load valid JSON, reject TOML, reject file outside specgen/ |
| `token_resolver.py` | Resolve single token, nested ref, missing token, protected override |
| `validators.py` | Valid config passes, missing required token fails, absolute path in company warns |
| `kicad_env.py` | Parse text_variables from .kicad_pro, handle missing file |
| `kicad_jobset.py` | Parse destination IDs, extract output paths, reject write attempts |

### Migration/naming regression tests

Scan all config files for:
- `kicad_specgen.json` (old name)
- `KICAD_SPECGEN_DIR` (old token)
- TOML syntax in `.kicad_specgen` files

---

## 12. Prioritized Gap List

### Critical — blocks implementation ✅ All resolved in Stage 0

| # | Gap | Status |
|---|---|---|
| C1 | `kicad_specgen.json` vs `kicad_specgen_local.json` — two names | ✅ Resolved |
| C2 | `.kicad_specgen` TOML example, JSON schema missing | ✅ Resolved |
| C3 | `KICAD_SPECGEN_DIR` vs `KSG_PROJECT_SPECGEN_DIR` | ✅ Resolved |
| C4 | `Configure Environments` dialog targets wrong file | ✅ Resolved |

### High — must address before Stage 1 coding ✅ All resolved in Stage 0

| # | Gap | Status |
|---|---|---|
| H1 | Formal JSON schemas missing for all config files | ✅ Written |
| H2 | Token resolution precedence with three-file model | ✅ Defined in schema docs |
| H3 | Missing Tokens dialog writes to wrong location | ✅ Corrected |
| H4 | Setup process Under Construction | Deferred — document separately before Stage 1 |
| H5 | Outdated tokens in app description | ✅ Corrected |

### Medium — address before or during Stage 1

| # | Gap | Status |
|---|---|---|
| M1 | New SpecGen Project dialog incomplete (TODO) | ✅ Completed in Pulldown Menus update |
| M2 | Output Log subtab missing wireframe | ✅ Added |
| M3 | `{KICAD_SPECGEN_DIR}` in jobset wireframes | ✅ Corrected |
| M4 | `schema_version` migration strategy | ✅ Defined in schema docs |
| M5 | `.kicad_pro` text_variables parsing spec | ✅ Defined |
| M6 | `.kicad_jobset` destination ID extraction spec | ✅ Defined |
| M7 | Multi-user edit conflict for company JSON | Future — flag in Stage 2 |

### Low — future quality

| # | Gap | Status |
|---|---|---|
| L1 | Help file `kicad_specgen_json.md` old filename | ✅ Renamed to `kicad_specgen_local.md` |
| L2 | `project_kicad_specgen.md` references TOML | ✅ Updated to JSON |
| L3 | Jinja2 SpecGen token examples missing | Added to variables_jinja.md |
| L4 | Validation panel widget specification | Define in Stage 1 design |

---

## 13. Questions That Must Be Answered Before Coding

| # | Question | Status |
|---|---|---|
| Q1 | `KSG_PROJECT_SPECGEN_DIR` naming decided? | ✅ Yes — `KSG_PROJECT_SPECGEN_DIR` |
| Q2 | `.kicad_specgen` strictly JSON? | ✅ Yes — JSON with `.kicad_specgen` extension |
| Q3 | Does Configure Environments edit company file or local only? | ✅ Both — token table → local, environment/company data → company |
| Q4 | Token resolution precedence with three files? | ✅ Defined: local → company/users → protected runtime |
| Q5 | Can local config define non-`KSG_*` tokens? | ✅ Yes — KiCad vars available under their native names from kicad_common.json |
| Q6 | Setup scope for Stage 1? | Deferred — define in setup document |
| Q7 | What does Variables page show? | Both kicad_pro vars (read-only) and project custom vars (editable) |
| Q8 | How does jobset output_path map to JOBSET_OUTPUT_DIR? | ✅ Defined in schema docs |

---

## 14. Recommended Next Document to Write

~~**Write the `.kicad_specgen` JSON Schema document first.**~~ ✅ Done in Stage 0.

**Next: Write the Setup Process document** (Framework §16 is Under Construction).

This unblocks Stage 1 setup bootstrap implementation across all three platforms.
