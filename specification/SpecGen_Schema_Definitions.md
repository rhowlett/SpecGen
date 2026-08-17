# KiCad SpecGen — JSON Schema Definitions

> **Document role:** Complete JSON schemas for all SpecGen-owned configuration
> files. Normative reference for validation, testing, and implementation.
> **Authority:** This document and `SpecGen_File_Framework.md` together define
> the data model. When they conflict, identify and resolve the conflict — do not
> silently prefer one over the other.
> **Living document policy:** This document and `SpecGen_File_Framework.md`
> must be reviewed and updated whenever:
> - A new workspace tab wireframe is created or updated
> - A new dialog is specified that reads or writes a config file
> - A new field is discussed in any design document
> - Application code introduces a new config field
> - A stage is completed and its implementation reveals gaps
> **Status:** Updated — reflects decisions through `SpecGen_Tab_Report.md`,
> `SpecGen_Tab_Jobset.md`, and `SpecGen_GUI_Menus.md`.
>
> **Schema files:** The structural JSON Schemas described here live as
> standalone draft-07 files in the repo-root **`schema/`** folder, one complete
> file per config:
> `schema/kicad_specgen_local.schema.json`,
> `schema/kicad_specgen_company.schema.json`,
> `schema/kicad_specgen_users.schema.json`,
> `schema/specgen_project.schema.json`, and the partial read-only
> `schema/kicad_common.schema.json`. The application loads and enforces these
> at config-load time via `core/schema_loader.py`. This document references
> each schema file and keeps the human-readable **semantic** rules (the
> Validation Rules tables) that JSON Schema cannot express; those are enforced
> in `core/validators.py`.

---

## 1. Token Resolution Precedence

When building the effective token table, tokens are resolved in this order.
Later sources override earlier sources.

```text
1. kicad_common.json  environment.vars
   (KiCad-native variable names, available under their native names)

2. kicad_specgen_local.json  tokens.*
   (KSG_* absolute path tokens, override any same-named kicad_common entry)

3. kicad_specgen_company.json  resolved paths
   (resolved using local tokens; company/client/team path references)

4. kicad_specgen_users.json  resolved user paths
   (resolved using local tokens; user-specific path references)

5. Protected derived runtime tokens
   (computed from opened .kicad_specgen location — override everything)
   SPECGEN_PROJECT_FILE
   KSG_PROJECT_SPECGEN_DIR
   KICAD_PROJECT_DIR
   GIT_PROJECT_DIR
   JOBSET_OUTPUT_DIR
   FAB_OUTPUT_DIR
```

---

## 2. Schema: `kicad_specgen_local.json`

**Location:** `{KICAD_COMMON_DIR}/kicad_specgen_local.json`
**Owner:** SpecGen (local machine)
**Format:** JSON
**Portable:** No — contains absolute paths. Must not be committed to shared repos.

### Structural schema

The structural JSON Schema for this file lives in **`schema/kicad_specgen_local.schema.json`** (draft-07). It validates the local machine configuration written to the KiCad user config folder. The application loads this file at startup and validates each config against it before use (see `core/schema_loader.py`).

Semantic rules that JSON Schema cannot express (cross-references, path-containment, protected-token rules, etc.) are listed below and enforced in `core/validators.py`.

### Validation Rules

| Rule | Description |
|---|---|
| All token values must be absolute paths | Reject relative paths in `tokens` section |
| Token names must match `^KSG_[A-Z0-9_]+$` | Reject lowercase or non-KSG names |
| Protected derived tokens must not appear in `tokens` | Reject: `SPECGEN_PROJECT_FILE`, `KSG_PROJECT_SPECGEN_DIR`, `KICAD_PROJECT_DIR`, `GIT_PROJECT_DIR`, `JOBSET_OUTPUT_DIR`, `FAB_OUTPUT_DIR` |
| `schema_version` must be supported | Reject unknown versions; offer migration path |
| `kicad_cli` path must exist if set | Warn if path does not exist on disk |
| `recent_projects` capped at 10 | Remove oldest entry when adding an 11th |
| `recent_projects` items with paths that no longer exist are shown greyed out | Stale entries are not removed automatically; user clears them via Clear Recent Projects |
| Per-project state is not stored here | `active_tab` and `workspace.environment` belong in the `.kicad_specgen` file, not in `last_session` or `recent_projects` |
| `skipped_tokens` entries suppress Missing Tokens dialog on this machine only | They do not affect other users and do not modify the project file |
| Jobset reconciliation warnings stored in `last_session` are transient | They are machine-local and not written to the portable project file |

### Migration Rules

| From version | To version | Action |
|---|---|---|
| No file exists | 1 | Run setup to create |
| schema_version missing | 1 | Treat as version 1, validate and re-save |
| Future: 1 → 2 | 2 | Document field changes; migrate automatically or prompt user |

### JSON Example

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
    "setup_complete":       true,
    "last_setup_run":       "2026-06-03T09:00:00",
    "last_setup_platform":  "macos",
    "dependency_stage":     "stage2"
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
    },
    {
      "specgen_project":   "/Users/john/Engineering/Projects/PowerBoard/specgen/PowerBoard.kicad_specgen",
      "project_name":      "PowerBoard",
      "display_name":      "12V Power Supply",
      "kicad_project_dir": "/Users/john/Engineering/Projects/PowerBoard",
      "last_opened_at":    "2026-05-29T09:15:00"
    }
  ],

  "skipped_tokens": [],

  "preferences": {
    "theme": "dark"
  }
}
```

---

## 3. Schema: `kicad_specgen_company.json`

**Location:** `{KSG_COMPANY_DIR}/SpecGen/kicad_specgen_company.json`
**Owner:** SpecGen (company/shared)
**Format:** JSON
**Portable:** Yes — uses token references only (no absolute paths)

### Structural schema

The structural JSON Schema for this file lives in **`schema/kicad_specgen_company.schema.json`** (draft-07). It validates the shared company configuration (company identity, departments/teams, clients/projects, environments). The application loads this file at startup and validates each config against it before use (see `core/schema_loader.py`).

Semantic rules that JSON Schema cannot express (cross-references, path-containment, protected-token rules, etc.) are listed below and enforced in `core/validators.py`.

### Validation Rules

| Rule | Description |
|---|---|
| No absolute paths allowed | All path values must use `{TOKEN_NAME}/...` notation |
| Token references must resolve | Each `{TOKEN}` in path values must exist in the effective token table |
| `company.name` must be non-empty | Used as the company identifier in reports (no separate company_id) |
| `company.logo` must resolve inside `KSG_COMPANY_DIR` | Logo must live in the shared company folder |
| Department `team_id` references must exist | A user's `team` must exist within their `department` |
| Project `status` must be one of the enum values | Stage 1: `active` \| `inactive` |
| Environment `type` must be one of the enum values | Reject unknown types |

---

## 4. Schema: `kicad_specgen_users.json`

**Location:** `{KSG_COMPANY_DIR}/SpecGen/kicad_specgen_users.json`
**Owner:** SpecGen (company/shared)
**Format:** JSON
**Portable:** Yes — uses token references only

### Structural schema

The structural JSON Schema for this file lives in **`schema/kicad_specgen_users.schema.json`** (draft-07). It validates the user roster (worker profiles, department/team references, client assignments). The application loads this file at startup and validates each config against it before use (see `core/schema_loader.py`).

Semantic rules that JSON Schema cannot express (cross-references, path-containment, protected-token rules, etc.) are listed below and enforced in `core/validators.py`.

### Validation Rules

| Rule | Description |
|---|---|
| `worker_id` must be unique | Reject duplicate worker_id values |
| `active_user` in local config must match a `worker_id` | Warn if user not found |
| `department` must match a `dept_id` in company file | Warn on mismatch |
| `team` must match a `team_id` within the user's department | Warn on mismatch |
| `client_assignments[].client_id` must match `clients` keys | Warn on mismatch |
| Path values must use token notation | No absolute paths in `paths` |

### User folder convention

`KSG_USER_SPECGEN_DIR` and `KSG_USER_COMMON_DIR` are derived from the selected
user's `worker_id` using the documented convention:

```text
KSG_USER_SPECGEN_DIR = {KSG_COMPANY_DIR}/SpecGen/Users/<worker_id>/specgen
KSG_USER_COMMON_DIR  = {KSG_COMPANY_DIR}/SpecGen/Users/<worker_id>/common
```

Setup creates these folders when a new user is generated.

---

## 5. Schema: Project `.kicad_specgen`

**Location:** `{KICAD_PROJECT_DIR}/specgen/<name>.kicad_specgen`
**Owner:** SpecGen (project)
**Format:** JSON (`.kicad_specgen` extension, JSON content)
**Portable:** Yes — uses token references only. May be committed with the KiCad project.

See `SpecGen_File_Framework.md` §12 for ownership rules, location rules, and
application use. See `SpecGen_Tab_Report.md` for report and fabrication field
semantics. See `SpecGen_Tab_Jobset.md` for jobset field semantics.

### Derived Runtime Tokens (set when file is opened)

| Token | Derived From |
|---|---|
| `SPECGEN_PROJECT_FILE` | Absolute path of this file |
| `KSG_PROJECT_SPECGEN_DIR` | Parent folder of this file |
| `KICAD_PROJECT_DIR` | Parent of `KSG_PROJECT_SPECGEN_DIR` |
| `GIT_PROJECT_DIR` | Git root from `KICAD_PROJECT_DIR`, or `KICAD_PROJECT_DIR` if not in Git |
| `JOBSET_OUTPUT_DIR` | `KICAD_PROJECT_DIR` + jobset output path from active `.kicad_jobset` |
| `FAB_OUTPUT_DIR` | From `fabrication.output_dir` if set; else `{JOBSET_OUTPUT_DIR}/fab/` |

### Field resolution note: `jobset.active_jobset` vs `files.jobset`

Earlier drafts had both `files.jobset` and `jobset.active_jobset` referencing
the same file. **The single authoritative field is `jobset.active_jobset`.**
`files.jobset` is removed to eliminate the redundancy. All references to the
active `.kicad_jobset` file use `jobset.active_jobset`.

### Structural schema

The structural JSON Schema for this file lives in **`schema/specgen_project.schema.json`** (draft-07). It validates any project `.kicad_specgen` file. The application loads this file at startup and validates each config against it before use (see `core/schema_loader.py`).

Semantic rules that JSON Schema cannot express (cross-references, path-containment, protected-token rules, etc.) are listed below and enforced in `core/validators.py`.

### Complete JSON Example

```json
{
  "schema_version": 1,

  "workspace": {
    "mode": "repo",
    "environment": "medical_devices"
  },

  "project": {
    "name":            "BoardA",
    "display_name":    "Medical Devices BoardA",
    "document_number": "AE-MD-BA-001",
    "revision":        "Rev B",
    "description":     "Battery monitoring board for medical device platform",
    "engineer":        "John Smith",
    "company":         "Medical Devices Inc",
    "date":            "2026-06-03",
    "copyright":       "© 2026 Advanced Engineering",
    "release_name":    "Production Release v1.0"
  },

  "files": {
    "kicad_pro":        "{KICAD_PROJECT_DIR}/BoardA.kicad_pro",
    "logo":             "{KSG_COMPANY_DIR}/SpecGen/assets/logos/company_logo.png",
    "report_css":       "{KSG_COMPANY_DIR}/SpecGen/assets/report_style.css",
    "title_page":       "{KSG_COMPANY_DIR}/SpecGen/templates/title_page.md",
    "end_page":         "{KSG_COMPANY_DIR}/SpecGen/templates/end_page.md",
    "background_notes": "{KICAD_PROJECT_DIR}/background/release_notes.md"
  },

  "variables": {
    "custom": {
      "TEST_LEVEL":       "Engineering Release",
      "CUSTOMER_RELEASE": "true"
    }
  },

  "jobset": {
    "active_jobset":        "{KSG_PROJECT_SPECGEN_DIR}/release_default.kicad_jobset",
    "stop_on_error":        true,
    "clear_log_before_run": true,
    "destinations": {
      "sch_pdf":      { "selected": true,  "heading_override": "Schematics",       "notes": "Used in report." },
      "bom_csv":      { "selected": true,  "heading_override": "Bill of Materials", "notes": "Used in Report and FAB package." },
      "pcb_layers_pdf":{ "selected": true,  "heading_override": "PCB Layers",       "notes": "" },
      "gerbers":      { "selected": true,  "heading_override": "",                  "notes": "Included in FAB package." },
      "step_model":   { "selected": false, "heading_override": "",                  "notes": "" }
    },
    "last_run": {
      "timestamp":              "2026-06-03T14:32:09",
      "status":                 "success",
      "destinations_run":       4,
      "destinations_succeeded": 4
    }
  },

  "report": {
    "output_dir":        "{JOBSET_OUTPUT_DIR}/report/",
    "filename_template": "{project_name}_{revision}_{date}_report.pdf",

    "cover": {
      "template": "{KSG_USER_COMMON_DIR}/templates/cover_standard.md",
      "title":    "{{ display_name }} Technical Report",
      "subtitle": "Rev {{ revision }} — {{ date }}",
      "logo":     "{KSG_COMPANY_DIR}/SpecGen/assets/logos/company_logo.png"
    },

    "pages": {
      "order": ["cover", "background_notes", "sch_pdf", "bom_csv", "pcb_layers_pdf", "end_page"],
      "definitions": {
        "cover":           { "source_type": "markdown",   "template":    "{KSG_USER_COMMON_DIR}/templates/cover_standard.md", "include": true,  "section_label": "",               "page_break_before": false },
        "background_notes":{ "source_type": "custom_pdf", "source_file": "{KICAD_PROJECT_DIR}/background/release_notes.md",  "include": true,  "section_label": "Release Notes",  "page_break_before": true },
        "sch_pdf":         { "source_type": "jobset",     "destination": "sch_pdf",         "include": true,  "section_label": "Schematics",       "page_break_before": true },
        "bom_csv":         { "source_type": "jobset",     "destination": "bom_csv",         "include": true,  "section_label": "Bill of Materials", "page_break_before": true },
        "pcb_layers_pdf":  { "source_type": "jobset",     "destination": "pcb_layers_pdf",  "include": true,  "section_label": "PCB Layers",       "page_break_before": true },
        "end_page":        { "source_type": "markdown",   "template":    "{KSG_COMPANY_DIR}/SpecGen/templates/end_page.md",  "include": true,  "section_label": "",               "page_break_before": true }
      }
    }
  },

  "fabrication": {
    "output_dir":            "{JOBSET_OUTPUT_DIR}/fab/",
    "zip_filename_template": "{project_name}_{revision}_{date}_fab.zip",

    "destinations": {
      "gerbers": { "include": true,  "zip_folder": "gerbers/" },
      "bom_csv": { "include": true,  "zip_folder": "bom/" },
      "sch_pdf": { "include": false, "zip_folder": "" }
    },

    "readme":    { "include": true, "template": "{KSG_USER_COMMON_DIR}/templates/fab_readme_standard.md", "filename": "README.md" },
    "checksums": { "include": true, "algorithm": "sha256", "filename": "checksums.sha256" }
  },

  "ui": {
    "active_tab": "jobset",
    "panel_sizes": {}
  }
}
```

### Validation Rules

| Rule | Description |
|---|---|
| File must be under a `specgen/` folder | `KSG_PROJECT_SPECGEN_DIR` must be a folder named `specgen` |
| No absolute paths | All path values in `files`, `report`, `fabrication` must use `{TOKEN_NAME}/...` notation |
| Custom variable names must match `^[A-Z][A-Z0-9_]*$` | Reject lowercase or invalid names |
| `destinations` keys must be strings | Destination IDs come from parsed `.kicad_jobset` |
| `report.pages.definitions` with `source_type=jobset` requires `destination` | Warn if `destination` field absent |
| `report.pages.definitions` with `source_type=markdown` requires `template` | Warn if `template` field absent |
| `report.pages.definitions` with `source_type=custom_pdf` requires `source_file` | Warn if `source_file` field absent |
| `report.pages.order` entries should match keys in `pages.definitions` | Warn on unmatched page IDs |
| `fabrication.destinations` keys should match destination IDs in `jobset.destinations` | Warn on keys absent from jobset |
| `jobset.active_jobset` is the single jobset reference | `files.jobset` must not be used |
| `fabrication.output_dir` defaults to `{JOBSET_OUTPUT_DIR}/fab/` | If absent, `FAB_OUTPUT_DIR` resolves to this default |
| `report.output_dir` defaults to `{JOBSET_OUTPUT_DIR}/report/` | If absent, report output resolves to this default |
| `schema_version` must be supported | Offer migration on mismatch |
| `ui` section changes do not set the dirty flag | UI state is saved silently on close |

---

## 6. KiCad File Parsing Reference

### `.kicad_pro` — Fields SpecGen reads

| Field path | Description | Used for |
|---|---|---|
| `text_variables` | Key/value dict | Template variable substitution, Variables page display |
| `text_variables.REV` | Revision string | `{{REVISION}}` template token |
| `text_variables.DATE` | Date string | `{{DATE}}` template token |

SpecGen reads `text_variables` as-is. All keys are made available as template tokens under their original names. SpecGen does not write to `.kicad_pro`.

**Missing `.kicad_pro` handling:** If the file is not found at `{KICAD_PROJECT_DIR}/<project>.kicad_pro`, show a warning in the validation panel. Do not block operation — the file is discoverable by scanning `KICAD_PROJECT_DIR` for `*.kicad_pro`.

### `.kicad_jobset` — Fields SpecGen reads

SpecGen parses the `.kicad_jobset` JSON to extract destination definitions.

| Field path | Description |
|---|---|
| `outputs[].id` | Destination ID (e.g. `sch_pdf`, `bom_csv`) |
| `outputs[].description` | Human-readable description of the output |
| `outputs[].type` | Output type (e.g. `schematic_pdf`, `bom`, `gerbers`) |
| `outputs[].settings.output_path` | Output directory relative to `KICAD_PROJECT_DIR` |

`JOBSET_OUTPUT_DIR` is derived as:
```
JOBSET_OUTPUT_DIR = KICAD_PROJECT_DIR / outputs[0].settings.output_path
```

SpecGen does not write to `.kicad_jobset`. Destination selections, heading overrides, and notes are stored in the project `.kicad_specgen` file.

### `kicad_common.json` — Fields SpecGen reads

| Field path | Description |
|---|---|
| `environment.vars` | All KiCad environment variable definitions |

Variables from `kicad_common.json` are available in the token resolver under their native names (e.g. `KICAD_SYMBOL_DIR`, `KICAD_FOOTPRINT_DIR`). They do not need `KSG_` prefix. SpecGen does not write to this file during normal operation. Setup may write with user approval and timestamped backup.

**Structural schema (partial, read-only):** `schema/kicad_common.schema.json`
describes only the `environment.vars` subset SpecGen reads and is marked
read-only. KiCad owns and writes this file and does **not** publish an official
JSON Schema for it — KiCad validates these settings internally in C++
(`JSON_SETTINGS`, with schema versions as compile-time integers). SpecGen's
partial schema therefore sets `additionalProperties: true`, permits
`environment.vars` to be an object of string values or `null` (KiCad 10 may
serialize `null` when empty), and is used for **advisory** validation only:
`core/kicad_env.py` logs a debug note on mismatch but never rejects or rewrites
the file.

---

## 7. `schema_version` Migration Policy

| Situation | Action |
|---|---|
| File does not exist | Create with current schema_version |
| `schema_version` matches | Load normally |
| `schema_version` is lower than current | Attempt automatic migration, log changes, prompt user to save |
| `schema_version` is higher than current | Warn user: "This file was created by a newer version of SpecGen. Some settings may be ignored." Load with best effort. |
| `schema_version` missing | Treat as version 1. Re-save after validation. |

Migration functions shall be named `migrate_v{from}_to_v{to}(data: dict) -> dict` and collected in `core/migrations.py`.
