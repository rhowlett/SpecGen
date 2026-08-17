# KiCad SpecGen — Report Tab Wireframes

> **Document role:** GUI wireframe specification for the Report workspace.
> **Authority:** `SpecGen_File_Framework.md`, `SpecGen_Setup_Process.md`.
> **Companion documents:** `SpecGen_Tab_Jobset.md`, `SpecGen_Schema_Definitions.md`.
> **Status:** Approved — ready for Stage 4 implementation.

---

## Overview

The Report tab is a unified workspace for configuring, building, and packaging
engineering deliverables. It contains three subtabs:

```text
┌──────────────────┬──────────────────┬──────────────────┐
│▶ Report Recipe   │ Preview & Build  │ Fabrication      │
└──────────────────┴──────────────────┴──────────────────┘
```

**Report Recipe** — Define what goes into the report: page order, template
assignments, variable overrides, cover page settings. Writes to
`.kicad_specgen` → `report`.

**Preview & Build** — Select generation scope (Report only, Report + Fabrication,
or Fabrication only), run the build, and open outputs. Writes to
`.kicad_specgen` → `report` and `fabrication` as needed.

**Fabrication** — Configure the fabrication ZIP package: output path, filename
template, which jobset destinations to include, README template, checksum
algorithm, and customer-specific file renaming rules. Writes to
`.kicad_specgen` → `fabrication`.

### Sidebar placement

The Report tab covers report assembly and fabrication packaging.
Fabrication is the third subtab, handling FAB output paths, ZIP contents, README, and checksums.

```text
SIDEBAR

  [Project]
  [Variables]
  [Jobset]
  [Report]       ← Report and Fabrication both live here
  [Logs]
  ─────────────
  [Configure]
```

### Data dependencies

```text
Report Recipe and Fabrication configuration:
  ← reads:  .kicad_specgen → report, fabrication sections
  → writes: .kicad_specgen → report, fabrication sections

Preview & Build:
  ← reads:  JOBSET_OUTPUT_DIR (jobset-generated files)
             .kicad_specgen → report recipe
             .kicad_specgen → fabrication config
             project metadata tokens (for filename and cover page)
  → writes:  rendered PDF report  → {JOBSET_OUTPUT_DIR}/report/
             fabrication ZIP      → FAB_OUTPUT_DIR
                                    (default: {JOBSET_OUTPUT_DIR}/fab/)
                                    (overridden per-project in fabrication.output_dir)

FAB_OUTPUT_DIR:
  Defined per-project in .kicad_specgen → fabrication.output_dir
  Defaults to {JOBSET_OUTPUT_DIR}/fab/ if not set.
  User is prompted to confirm overwrite if the ZIP already exists.
```

---

## Report Recipe Subtab

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [File]   [Edit]   [View]   [Help]                                                                          │
├───────────────┬────────────────────────────────────────────────────────────────────────────────────────────┤
│ SIDEBAR       │                                                                                            │
│               │ ┌──────────────────┬──────────────────┬──────────────────┐                                 │
│ [Project]     │ │▶ Report Recipe   │ Preview & Build  │ Fabrication      │                                 │
│ [Variables]   │ └──────────────────┴──────────────────┴──────────────────┘                                 │
│ [Jobset]      │ ┌────────────────────────────────────────────────────────────────────────────────────────┐ │
│▶[Report]      │ │ REPORT CONFIGURATION                                                                   │ │
│ [Logs]        │ ├────────────────────────────────────────────────────────────────────────────────────────┤ │
│ ─────────────── │ Recipe file : .kicad_specgen → report                                                  │ │
│ [Configure]   │ │ Status      : ✓ 6 pages configured                                                     │ │
│               │ └────────────────────────────────────────────────────────────────────────────────────────┘ │
│               │ ┌────────────────────────────────────────────────────────────────────────────────────────┐ │
│               │ │ COVER PAGE                                                                             │ │
│               │ ├────────────────────────────────────────────────────────────────────────────────────────┤ │
│               │ │ Template   : [ cover_standard.md               ▼ ]  [ Browse... ]                      │ │
│               │ │ Title      : [ {{ project_name }} Technical Report ]                                   │ │
│               │ │ Subtitle   : [ Rev {{ revision }} — {{ date }}     ]                                   │ │
│               │ │ Logo asset : [ {KSG_COMPANY_DIR}/SpecGen/assets/logo.png ]  [ Browse... ]              │ │
│               │ └────────────────────────────────────────────────────────────────────────────────────────┘ │
│               │ ┌────────────────────────────────────────────────────────────────────────────────────────┐ │
│               │ │ PAGE ORDER  (drag to reorder)                                                          │ │
│               │ ├────┬───────────────────────┬───────────────────────────────┬──────────┬────────────────┤ │
│               │ │ ## │ Page ID               │ Source / Template             │ Type     │ Include        │ │
│               │ ├────┼───────────────────────┼───────────────────────────────┼──────────┼────────────────┤ │
│               │ │ ≡1 │ cover                 │ cover_standard.md             │ Markdown │ [x]            │ │
│               │ │ ≡2 │ project_summary       │ project_summary.md            │ Markdown │ [x]            │ │
│               │ │ ≡3 │ schematics            │ sch_pdf  (jobset output)      │ PDF      │ [x]            │ │
│               │ │ ≡4 │ erc_report            │ erc_report  (jobset output)   │ TXT→PDF  │ [x]            │ │
│               │ │ ≡5 │ bom                   │ bom_csv  (jobset output)      │ CSV→PDF  │ [x]            │ │
│               │ │ ≡6 │ pcb_layers            │ pcb_layers_pdf  (jobset)      │ PDF      │ [ ]            │ │
│               │ ├────┴───────────────────────┴───────────────────────────────┴──────────┴────────────────┤ │
│               │ │  [ Add Page ]  [ Remove Selected ]  [ Move Up ]  [ Move Down ]                         │ │
│               │ └────────────────────────────────────────────────────────────────────────────────────────┘ │
│               │ ┌────────────────────────────────────────────────────────────────────────────────────────┐ │
│               │ │ SELECTED PAGE DETAIL  (schematics)                                                     │ │
│               │ ├────────────────────────────────────────────────────────────────────────────────────────┤ │
│               │ │ Page ID       : schematics                                                             │ │
│               │ │ Source type   : jobset output                                                          │ │
│               │ │ Jobset dest.  : sch_pdf                           (resolved: ✓ file found)             │ │
│               │ │ Section label : [ Schematics                  ]                                        │ │
│               │ │ Page break    : [x] Insert page break before this section                              │ │
│               │ │ Notes         : [ (optional notes for this page entry)          ]                      │ │
│               │ └────────────────────────────────────────────────────────────────────────────────────────┘ │
│               │                                           [ Save Recipe ]  [ Discard Changes ]             │
├───────────────┴────────────────────────────────────────────────────────────────────────────────────────────┤
│ STATUS: Project valid | Environment: client_a | Report: 6 pages (5 active) | Jobset last run: Success      │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Page source types

```text
jobset output   — references a destination ID from the active .kicad_jobset
                  SpecGen reads the output file(s) from JOBSET_OUTPUT_DIR
markdown        — a Jinja2-rendered .md template from the project or user templates
                  rendered by jinja_renderer, converted to PDF by pdf_assembler
custom pdf      — a fixed PDF file referenced by a tokenized path
                  included as-is; not rendered or modified
```

### Page order drag behavior

The `≡` handle on each row enables drag-to-reorder within the table. The order
is saved to `.kicad_specgen` → `report.pages.order` on `[ Save Recipe ]`.

### Add Page dialog

```text
┌──────────────────────────────────────────────────────────────┐
│  Add Report Page                                             │
├──────────────────────────────────────────────────────────────┤
│  Page ID     : [ new_page_id          ]  (unique, required)  │
│  Source type : ( ) Jobset output                             │
│               (•) Markdown template                          │
│               ( ) Custom PDF                                 │
│                                                              │
│  (Markdown template selected)                                │
│  Template    : [ project_summary.md   ▼ ]  [ Browse... ]     │
│  Section label: [ New Section         ]                      │
│                                                              │
│                          [ Add ]  [ Cancel ]                 │
└──────────────────────────────────────────────────────────────┘
```

---

## Preview & Build Subtab

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [File]   [Edit]   [View]   [Help]                                                                          │
├───────────────┬────────────────────────────────────────────────────────────────────────────────────────────┤
│ SIDEBAR       │                                                                                            │
│               │ ┌──────────────────┬──────────────────┬──────────────────┐                                 │
│ [Project]     │ │  Report Recipe   │▶ Preview & Build │ Fabrication      │                                 │
│ [Variables]   │ └──────────────────┴──────────────────┴──────────────────┘                                 │
│ [Jobset]      │ ┌────────────────────────────────────────────────────────────────────────────────────────┐ │
│▶[Report]      │ │ GENERATION SCOPE                                                                       │ │
│ [Logs]        │ ├────────────────────────────────────────────────────────────────────────────────────────┤ │
│ ─────────────── │ (•) Report only                                                                        │ │
│ [Configure]   │ │     Renders PDF report → {JOBSET_OUTPUT_DIR}/report/                                   │ │
│               │ │     Output: BoardA_RevA_2026-06-03_report.pdf                                          │ │
│               │ │                                                                                        │ │
│               │ │ ( ) Report + Fabrication                                                               │ │
│               │ │     Renders PDF report AND builds fabrication ZIP                                      │ │
│               │ │     Report  → {JOBSET_OUTPUT_DIR}/report/                                              │ │
│               │ │     FAB ZIP → {FAB_OUTPUT_DIR}/BoardA_RevA_2026-06-03_fab.zip                          │ │
│               │ │                                                                                        │ │
│               │ │ ( ) Fabrication only                                                                   │ │
│               │ │     Builds fabrication ZIP from current jobset outputs (no report re-render)           │ │
│               │ │     FAB ZIP → {FAB_OUTPUT_DIR}/BoardA_RevA_2026-06-03_fab.zip                          │ │
│               │ │                                                                                        │ │
│               │ │ [ Dry Run ]      [ Build ]                                                             │ │
│               │ └────────────────────────────────────────────────────────────────────────────────────────┘ │
│               │ ┌────────────────────────────────────────────────────────────────────────────────────────┐ │
│               │ │ PRE-BUILD CHECKS                                                                       │ │
│               │ ├────────────────────────────────────────────────────────────────────────────────────────┤ │
│               │ │ ✓ Report recipe has 5 active pages                                                     │ │
│               │ │ ✓ All jobset source files found in {JOBSET_OUTPUT_DIR}                                 │ │
│               │ │ ✓ All Markdown templates found                                                         │ │
│               │ │ ✓ Report output folder is writable                                                     │ │
│               │ │ ✓ FAB_OUTPUT_DIR is set: {JOBSET_OUTPUT_DIR}/fab/                                      │ │
│               │ │ ✓ FAB output folder is writable                                                        │ │
│               │ │ ⚠ BoardA_RevA_2026-06-03_fab.zip already exists — will prompt to overwrite             │ │
│               │ └────────────────────────────────────────────────────────────────────────────────────────┘ │
│               │ ┌────────────────────────────────────────────────────────────────────────────────────────┐ │
│               │ │ BUILD LOG                                                                              │ │
│               │ ├──────────────────────────────────────────────────────────────────────────────────────┬─┤ │
│               │ │  Waiting for build...                                                                │^│ │
│               │ │                                                                                      │ │ │
│               │ │                                                                                      │v│ │
│               │ └──────────────────────────────────────────────────────────────────────────────────────┴─┘ │
│               │ ┌────────────────────────────────────────────────────────────────────────────────────────┐ │
│               │ │ OUTPUTS                                                                                │ │
│               │ ├────────────────────────────────────────────────────────────────────────────────────────┤ │
│               │ │ (No outputs yet)                                                                       │ │
│               │ │                                                                                        │ │
│               │ │ [ Open Report Folder ]   [ Open FAB Folder ]                                           │ │
│               │ └────────────────────────────────────────────────────────────────────────────────────────┘ │
├───────────────┴────────────────────────────────────────────────────────────────────────────────────────────┤
│ STATUS: Project valid | Environment: client_a | Report ready | Last build: Never                           │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### After a successful Report + Fabrication build

```text
│               │ ┌────────────────────────────────────────────────────────────────────────────────────────┐ │
│               │ │ BUILD LOG                                                                              │ │
│               │ ├──────────────────────────────────────────────────────────────────────────────────────┬─┤ │
│               │ │  2026-06-03 15:01:00  Starting Report + Fabrication build...                         │^│ │
│               │ │  2026-06-03 15:01:00  ► Rendering cover page (cover_standard.md)             ✓       │ │ │
│               │ │  2026-06-03 15:01:01  ► Rendering project_summary.md                         ✓       │ │ │
│               │ │  2026-06-03 15:01:01  ► Inserting schematics (sch_pdf → BoardA.pdf)          ✓       │ │ │
│               │ │  2026-06-03 15:01:02  ► Rendering ERC report (erc_report.txt → PDF)          ✓       │ │ │
│               │ │  2026-06-03 15:01:02  ► Rendering BOM (bom.csv → PDF)                        ✓       │ │ │
│               │ │  2026-06-03 15:01:03  ► Assembling PDF report                                ✓       │ │ │
│               │ │  2026-06-03 15:01:03  ✓ Report written: BoardA_RevA_2026-06-03_report.pdf            │ │ │
│               │ │  2026-06-03 15:01:03  ─────────────────────────────────────────────────────          │ │ │
│               │ │  2026-06-03 15:01:03  ► Building fabrication package...                              │ │ │
│               │ │  2026-06-03 15:01:03  ► Collecting: gerbers/ (12 files)                      ✓       │ │ │
│               │ │  2026-06-03 15:01:03  ► Collecting: bom/bom.csv                              ✓       │ │ │
│               │ │  2026-06-03 15:01:04  ► Generating README.md from template                   ✓       │ │ │
│               │ │  2026-06-03 15:01:04  ► Computing SHA-256 checksums                          ✓       │ │ │
│               │ │  2026-06-03 15:01:04  ► Writing ZIP: BoardA_RevA_2026-06-03_fab.zip          ✓       │ │ │
│               │ │  2026-06-03 15:01:04  ─────────────────────────────────────────────────────          │ │ │
│               │ │  2026-06-03 15:01:04  Build complete: Report + Fabrication succeeded.                │ │ │
│               │ │                                                                                      │v│ │
│               │ └──────────────────────────────────────────────────────────────────────────────────────┴─┘ │
│               │ ┌────────────────────────────────────────────────────────────────────────────────────────┐ │
│               │ │ OUTPUTS                                                                                │ │
│               │ ├────────────────────────────────────────────────────────────────────────────────────────┤ │
│               │ │ ✓ Report PDF  : {JOBSET_OUTPUT_DIR}/report/BoardA_RevA_2026-06-03_report.pdf  [View]   │ │
│               │ │ ✓ FAB ZIP     : {FAB_OUTPUT_DIR}/BoardA_RevA_2026-06-03_fab.zip              [Open]    │ │
│               │ │                                                                                        │ │
│               │ │ [ Open Report Folder ]   [ Open FAB Folder ]                                           │ │
│               │ └────────────────────────────────────────────────────────────────────────────────────────┘ │
```

### Overwrite confirmation dialog

Shown before build if the target report PDF or FAB ZIP already exists:

```text
┌──────────────────────────────────────────────────────────────────┐
│  Overwrite Existing Output?                                      │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  The following output files already exist:                       │
│                                                                  │
│  ✓ Report PDF  : BoardA_RevA_2026-06-03_report.pdf               │
│    Modified    : 2026-06-03 14:55                                │
│                                                                  │
│  ⚠ FAB ZIP    : BoardA_RevA_2026-06-03_fab.zip                   │
│    Modified    : 2026-06-03 14:55                                │
│                                                                  │
│  Overwriting cannot be undone.                                   │
│                                                                  │
│  [ Overwrite ]          [ Choose New Name... ]   [ Cancel ]      │
└──────────────────────────────────────────────────────────────────┘
```

**[ Overwrite ]** — Proceeds with the build. Existing files are replaced.

**[ Choose New Name... ]** — Opens a Save As dialog pre-populated with the
current filename so the user can change the revision or date suffix.

**[ Cancel ]** — Aborts the build. No files are written.

### Dry run behavior

`[ Dry Run ]` renders all templates and resolves all sources but writes no
files. The Build Log shows what would be generated and any errors or missing
sources. Pre-Build Checks also refresh on Dry Run. The Outputs panel shows
`(Dry run — no files written)`.

---

## Fabrication Subtab

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [File]   [Edit]   [View]   [Help]                                                                          │
├───────────────┬────────────────────────────────────────────────────────────────────────────────────────────┤
│ SIDEBAR       │                                                                                            │
│               │ ┌──────────────────┬──────────────────┬──────────────────┐                                 │
│ [Project]     │ │  Report Recipe   │ Preview & Build  │▶ Fabrication     │                                 │
│ [Variables]   │ └──────────────────┴──────────────────┴──────────────────┘                                 │
│ [Jobset]      │ ┌────────────────────────────────────────────────────────────────────────────────────────┐ │
│▶[Report]      │ │ FAB OUTPUT LOCATION                                                                    │ │
│ [Logs]        │ ├────────────────────────────────────────────────────────────────────────────────────────┤ │
│ ─────────────── │ FAB_OUTPUT_DIR : [ {JOBSET_OUTPUT_DIR}/fab/                    ]  [ Browse... ]        │ │
│ [Configure]   │ │                  (default — relative to jobset output root)                            │ │
│               │ │ ZIP filename   : [ {project_name}_{revision}_{date}_fab.zip    ]  (template; editable) │ │
│               │ │ Resolved name  : BoardA_RevA_2026-06-03_fab.zip                                        │ │
│               │ └────────────────────────────────────────────────────────────────────────────────────────┘ │
│               │ ┌────────────────────────────────────────────────────────────────────────────────────────┐ │
│               │ │ ZIP CONTENTS  (select jobset destinations to include)                                  │ │
│               │ ├────┬──────────────────┬─────────────────────────────┬─────────────┬────────────────────┤ │
│               │ │ In │ Destination ID   │ Description                 │ Output Type │ Rename in ZIP      │ │
│               │ ├────┼──────────────────┼─────────────────────────────┼─────────────┼────────────────────┤ │
│               │ │ [x]│ gerbers          │ Gerber Package              │ Gerber/NC   │ [ gerbers/       ] │ │
│               │ │ [x]│ bom_csv          │ Bill of Materials           │ CSV         │ [ bom/           ] │ │
│               │ │ [ ]│ sch_pdf          │ Schematic PDF               │ PDF         │ [                ] │ │
│               │ │ [ ]│ step_model       │ STEP 3D Model               │ STEP        │ [                ] │ │
│               │ │ [ ]│ erc_report       │ ERC Report                  │ TXT         │ [                ] │ │
│               │ └────┴──────────────────┴─────────────────────────────┴─────────────┴────────────────────┘ │
│               │ ┌────────────────────────────────────────────────────────────────────────────────────────┐ │
│               │ │ README                                                                                 │ │
│               │ ├────────────────────────────────────────────────────────────────────────────────────────┤ │
│               │ │ Include README : [x]                                                                   │ │
│               │ │ Template       : [ fab_readme_standard.md   ▼ ]   [ Browse... ]                        │ │
│               │ │ README name    : [ README.md                  ]                                        │ │
│               │ └────────────────────────────────────────────────────────────────────────────────────────┘ │
│               │ ┌────────────────────────────────────────────────────────────────────────────────────────┐ │
│               │ │ CHECKSUMS                                                                              │ │
│               │ ├────────────────────────────────────────────────────────────────────────────────────────┤ │
│               │ │ Generate checksums : [x]                                                               │ │
│               │ │ Algorithm          : [ SHA-256    ▼ ]                                                  │ │
│               │ │ Checksum filename  : [ checksums.sha256 ]                                              │ │
│               │ └────────────────────────────────────────────────────────────────────────────────────────┘ │
│               │                                        [ Save FAB Config ]  [ Discard Changes ]            │
├───────────────┴────────────────────────────────────────────────────────────────────────────────────────────┤
│ STATUS: Project valid | Environment: client_a | FAB: 2 destinations selected | Last build: Never           │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### ZIP internal structure

The fabrication ZIP is built with a clean internal folder structure derived from
the Rename in ZIP column. Example for the configuration above:

```text
BoardA_RevA_2026-06-03_fab.zip
├── gerbers/
│   ├── BoardA-F_Cu.gbr
│   ├── BoardA-B_Cu.gbr
│   ├── BoardA-Edge_Cuts.gbr
│   ├── BoardA.drl
│   └── ... (all gerber and drill files)
├── bom/
│   └── bom.csv
├── README.md
└── checksums.sha256
```

### FAB_OUTPUT_DIR token

`FAB_OUTPUT_DIR` is a **protected derived runtime token** computed as follows:

```text
If .kicad_specgen → fabrication.output_dir is set:
    FAB_OUTPUT_DIR = resolve_tokens(fabrication.output_dir)
Else:
    FAB_OUTPUT_DIR = JOBSET_OUTPUT_DIR / fab/
```

Like other protected derived tokens (`JOBSET_OUTPUT_DIR`, `KICAD_PROJECT_DIR`,
etc.), `FAB_OUTPUT_DIR` is computed at runtime and must not appear as a
user-defined token in `kicad_specgen_local.json`.

### ZIP filename template tokens

The ZIP filename template supports project metadata tokens:

```text
{project_name}   — from .kicad_specgen → project.name
{revision}       — from .kicad_specgen → project.revision
{date}           — build date in YYYY-MM-DD format (local machine time)
{board_name}     — from .kicad_pro text variables (if defined)
```

Example template: `{project_name}_{revision}_{date}_fab.zip`
Resolved:         `BoardA_RevA_2026-06-03_fab.zip`

---

## Menu and Navigation Reference

The View menu, sidebar navigation labels, and Edit menu are defined in
`SpecGen_GUI_Menus.md`. That document is the authoritative source for all
menu structure and behavior.

Key points relevant to the Report tab:

- The Fabrication subtab is the third subtab within this Report workspace.
- `[Report]` is the single sidebar entry that covers all three subtabs
  (Report Recipe, Preview & Build, Fabrication).
- `Edit → Configure` switches to the Configure tab.

---

## Schema Impact

The `.kicad_specgen` `fabrication` section is updated to add `output_dir` and
`zip_filename_template`:

```json
"fabrication": {
  "output_dir": "{JOBSET_OUTPUT_DIR}/fab/",
  "zip_filename_template": "{project_name}_{revision}_{date}_fab.zip",
  "destinations": {
    "gerbers": { "include": true, "zip_folder": "gerbers/" },
    "bom_csv": { "include": true, "zip_folder": "bom/" }
  },
  "readme": {
    "include": true,
    "template": "{KSG_USER_COMMON_DIR}/templates/fab_readme_standard.md",
    "filename": "README.md"
  },
  "checksums": {
    "include": true,
    "algorithm": "sha256",
    "filename": "checksums.sha256"
  }
}
```

The `report` section is unchanged from `SpecGen_Schema_Definitions.md` except
that `pages` now explicitly supports `source_type` per page entry:

```json
"report": {
  "output_dir": "{JOBSET_OUTPUT_DIR}/report/",
  "filename_template": "{project_name}_{revision}_{date}_report.pdf",
  "cover": {
    "template": "{KSG_USER_COMMON_DIR}/templates/cover_standard.md",
    "title": "{{ project_name }} Technical Report",
    "subtitle": "Rev {{ revision }} — {{ date }}",
    "logo": "{KSG_COMPANY_DIR}/SpecGen/assets/logo.png"
  },
  "pages": {
    "order": ["cover", "project_summary", "schematics", "erc_report", "bom"],
    "definitions": {
      "cover":           { "source_type": "markdown", "template": "cover_standard.md",    "include": true },
      "project_summary": { "source_type": "markdown", "template": "project_summary.md",   "include": true },
      "schematics":      { "source_type": "jobset",   "destination": "sch_pdf",           "include": true },
      "erc_report":      { "source_type": "jobset",   "destination": "erc_report",        "include": true },
      "bom":             { "source_type": "jobset",   "destination": "bom_csv",           "include": true },
      "pcb_layers":      { "source_type": "jobset",   "destination": "pcb_layers_pdf",    "include": false }
    }
  }
}
```

---

## Module Impact

| Module | Change |
|---|---|
| `ui/tabs/report_tab.py` | **New** — ReportTab with three subtabs (RecipeSubtab, BuildSubtab, FabricationSubtab) |
| `services/report_service.py` | **New** — render_report(), build_fab_zip(), dry_run(), pre_build_checks() |
| `core/render/jinja_renderer.py` | **New** — render Markdown templates with token + variable injection |
| `core/render/pdf_assembler.py` | **New** — assemble rendered pages + jobset PDFs into final report PDF |
| `core/fab/package_builder.py` | **New** — collect files, render README, compute checksums, write ZIP |
| `core/app_state.py` | Add: `fab_output_dir`, `last_report_build`, `last_fab_build` |

---

## Acceptance Criteria

### Report Recipe Subtab

```text
✓ Page order table populates from .kicad_specgen → report.pages
✓ Drag-to-reorder updates page order and sets dirty flag
✓ Add Page dialog validates unique page ID before adding
✓ Remove Page warns if the page is the only cover page
✓ Selected page detail panel updates when a row is clicked
✓ Jobset destination source shows resolved status (✓ found / ✗ missing)
✓ Save Recipe writes .kicad_specgen → report section
✓ Discard Changes reloads from saved .kicad_specgen
```

### Preview & Build Subtab

```text
✓ Generation scope selector shows all three options with correct path previews
✓ Pre-build checks run automatically when the subtab is shown
✓ Pre-build checks re-run when scope selection changes
✓ Build button is disabled if any pre-build check fails with ✗
✓ Build button is enabled if pre-build checks show only ✓ or ⚠
✓ Overwrite confirmation dialog appears when target file already exists
✓ [ Overwrite ] proceeds and replaces the existing file
✓ [ Choose New Name... ] opens Save As dialog pre-populated with current name
✓ [ Cancel ] in overwrite dialog aborts build with no writes
✓ Dry run shows what would be generated without writing files
✓ Build log shows timestamped per-step results
✓ Build log feeds the Logs workspace page for persistence
✓ Outputs panel shows resolved paths and [View] / [Open] buttons after build
✓ [ Open Report Folder ] opens the report output folder in the OS file manager
✓ [ Open FAB Folder ] opens FAB_OUTPUT_DIR in the OS file manager
✓ "Fabrication only" scope skips template rendering; uses existing jobset output
```

### Fabrication Subtab

```text
✓ FAB_OUTPUT_DIR field shows resolved value (default or from .kicad_specgen)
✓ ZIP filename template resolves correctly with project metadata tokens
✓ Destination table populates from active .kicad_jobset destinations
✓ Destinations not in the jobset are not shown
✓ Include checkbox and Rename in ZIP field save to .kicad_specgen → fabrication
✓ README include toggle shows/hides template and filename fields
✓ Checksum include toggle shows/hides algorithm and filename fields
✓ Save FAB Config writes .kicad_specgen → fabrication section
✓ FAB_OUTPUT_DIR is not allowed as a user-defined token in local config
✓ ZIP is not written into KICAD_PROJECT_DIR directly
```

---

*End of SpecGen Report Tab Specification.*
