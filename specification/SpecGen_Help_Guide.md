# KiCad SpecGen — Help File Authoring Guide

> **Document role:** Developer guide for writing and maintaining the
> in-application help files served by `HelpDialog`. Covers file naming,
> folder structure, Markdown conventions, stage-by-stage authoring schedule,
> and content requirements for each help topic.
> **Authority:** `SpecGen_GUI_Menus.md §Required Help Files` (topic content
> requirements), `SpecGen_GUI_Dialogs.md §HelpDialog` (rendering behavior).
> **Companion documents:** `SpecGen_Help_JinJa.md` (Jinja2 template style
> example — use as a reference for the `variables_jinja.md` help file).
>
> ⚠ **DRAFT — INCOMPLETE**
> This document covers the authoring rules and Stage 1 content only.
> Sections marked `[Stage N — Not yet written]` must be completed as
> each implementation stage finishes. A final version of this document
> requires all five implementation stages to be complete.
> See §5 (Authoring Schedule) for the full stage-by-stage plan.

---

## 1. Help File System Overview

Help files are plain Markdown (`.md`) files stored in the `help/` folder
inside the SpecGen application repository:

```text
{KSG_APP_DIR}/
└─ help/
   ├─ index.md
   ├─ getting_started.md
   ├─ project_setup_tokens.md
   ├─ configure_tab.md
   ├─ project_page.md
   ├─ variables_jinja.md
   ├─ jobset.md
   ├─ report.md
   ├─ logs.md
   ├─ troubleshooting.md
   ├─ kicad_specgen_local.md
   └─ project_kicad_specgen.md
```

`HelpDialog` loads the requested file via:

```python
path = KSG_APP_DIR / help_file
self.browser.setMarkdown(path.read_text(encoding="utf-8"))
```

If the file is not found, `HelpDialog` shows a clear error message rather
than crashing. Placeholder files are therefore acceptable and preferred over
missing files.

### Help menu to file mapping

| Help Menu Item | File | Stage |
|---|---|---|
| KiCad SpecGen Help | `help/index.md` | Stage 1 — Full |
| Getting Started | `help/getting_started.md` | Stage 1 — Full |
| Project Setup and Tokens | `help/project_setup_tokens.md` | Stage 1 — Full |
| Configure Tab | `help/configure_tab.md` | Stage 1 — Full |
| Project Page | `help/project_page.md` | Stage 2 — Placeholder in Stage 1 |
| Variables and Jinja Templates | `help/variables_jinja.md` | Stage 2 — Placeholder in Stage 1 |
| Jobset | `help/jobset.md` | Stage 3 — Placeholder in Stage 1 |
| Report and Fabrication | `help/report.md` | Stage 4 — Placeholder in Stage 1 |
| Logs | `help/logs.md` | Stage 1 — Full |
| Troubleshooting | `help/troubleshooting.md` | Stage 1 — Full |

Additionally referenced (not in Help menu, loaded by application):

| Topic | File | Stage |
|---|---|---|
| Local config reference | `help/kicad_specgen_local.md` | Stage 1 — Full |
| Project file reference | `help/project_kicad_specgen.md` | Stage 2 — Placeholder in Stage 1 |

---

## 2. Markdown Conventions

`HelpDialog` renders Markdown using `QTextBrowser.setMarkdown()` (Qt 6.x /
PySide6). The following elements are confirmed supported:

```text
✓ Headings       # through ####
✓ Paragraphs     Normal prose
✓ Bold           **text**
✓ Italic         *text*
✓ Bullet lists   - item
✓ Numbered lists 1. item
✓ Code blocks    fenced with ```
✓ Inline code    `code`
✓ Horizontal rule  ---
✓ Tables         | col | col |  (Qt 6.x only — verify during Stage 1)
✓ External links [text](https://...)  — opens in OS browser
```

Elements to avoid:

```text
✗ HTML tags      — not rendered by QTextBrowser in Markdown mode
✗ Images         — not supported in inline Markdown via QTextBrowser
✗ Nested tables  — avoid for reliability
✗ Raw HTML       — stripped silently
```

### Style rules

- Use `#` for the page title (one per file).
- Use `##` for major sections. Use `###` for subsections. Do not go deeper
  than `####`.
- Keep prose short. Help files are reference material, not tutorials.
- Use code blocks for all file paths, token names, JSON examples, and
  command-line instructions.
- Use bullet lists for option sets and feature lists. Use numbered lists only
  for sequential steps.
- Tables are acceptable for reference data (token names, field definitions).
  Keep tables narrow — the dialog is 900 px wide minimum.
- Write in second person ("You can set the theme in...") not third person.
- Do not duplicate content from other help files. Cross-reference by name:
  "See **Project Setup and Tokens** for details on KSG_* tokens."

### Placeholder template

Every help file that is not yet fully written must contain this placeholder
rather than being empty or missing:

```markdown
# <Topic Name>

> **This help topic will be available in Stage N.**
> It covers: <one-line description of what it will explain>.

See **Getting Started** for an introduction to KiCad SpecGen.
```

Replace `<Topic Name>`, `N`, and the description with the correct values.
Never leave a help file empty — `HelpDialog` must always show something useful.

---

## 3. File-by-File Content Requirements

Content requirements are the authoritative list from
`SpecGen_GUI_Menus.md §Required Help Files`. This section adds authoring
notes and cross-references.

---

### `index.md` — KiCad SpecGen Help

**Stage:** 1 — Full
**Opens from:** Help → KiCad SpecGen Help

Required content:

```text
What KiCad SpecGen does
Workflow overview: setup → project → jobset → report → fabrication
Stage overview (briefly)
Links to each major help topic
```

Authoring notes:

- This is the entry point. Keep it short — two to three paragraphs plus a
  link list. Readers arrive here from the Help menu; they will navigate to
  a specific topic quickly.
- The link list format: `- [Topic Name](file.md)` — but note that
  `QTextBrowser` internal links require `setSource()` integration. For
  Stage 1, write the links as plain text topic names and let the user
  navigate the Help menu instead.

---

### `getting_started.md` — Getting Started

**Stage:** 1 — Full
**Opens from:** Help → Getting Started

Required content:

```text
1. Run setup.py from {KSG_APP_DIR}
2. Configure kicad-cli if not auto-detected
3. Open an existing SpecGen project (File → Open SpecGen Project...)
4. Review the Configure tab — verify all tokens resolve
5. Validate the project
6. Save the project
```

Authoring notes:

- Stage 1 does not have project creation (stub only) — do not mention
  File → New SpecGen Project as a first step.
- Use numbered steps. Each step should be achievable in under a minute.
- Reference **Configure Tab** help for token setup detail.
- Reference **Project Setup and Tokens** for token concepts.

---

### `project_setup_tokens.md` — Project Setup and Tokens

**Stage:** 1 — Full
**Opens from:** Help → Project Setup and Tokens

Required content:

```text
KSG_* stored tokens — what they are, where they live
Protected derived runtime tokens — read-only, computed at project open
kicad_specgen_local.json — the only file that stores absolute paths
kicad_common.json — KiCad's own environment vars, lowest priority
Effective token table — how the five layers resolve
Missing token repair — Provide / Skip / Remove options
Repository vs standalone workspace mode
```

Authoring notes:

- This is a conceptual page, not a reference page. Explain the token
  model in plain language before showing JSON.
- Include a short example of a token reference:
  `{KSG_COMPANY_DIR}/SpecGen/templates/title_page.md`
- The full token priority order:
  `USER → CLIENT → COMPANY → DEFAULT` at project level;
  five-layer stack at application level (see `SpecGen_File_Framework.md`
  §7.4 for the authoritative order).
- Cross-reference: "See **Configure Tab** to view and edit your KSG_* tokens."

---

### `configure_tab.md` — Configure Tab

**Stage:** 1 — Full
**Opens from:** Help → Configure Tab

Required content:

```text
Local Machine subtab
  KSG_* tokens — view, add, edit, remove
  kicad-cli path and version
  .venv status
  setup state and Re-run Setup Wizard

Company & User subtab
  Company identity
  Clients and teams
  User profiles — Worker ID, display name, role

Environments subtab
  Environment definitions
  Active environment and active user (machine-level defaults)
  Token priority order: USER → CLIENT → COMPANY → DEFAULT

Preferences subtab
  Theme selection — six available themes
  Future preferences placeholder

Validation subtab
  Run Validation
  ✓ ⚠ ✗ result icons
  What blocking vs non-blocking means
```

Authoring notes:

- The wireframe authority is `SpecGen_Tab_Configure.md`. Use the same
  section structure so users can relate the help to the UI.
- Keep each subtab section short — one paragraph plus a bullet list.
- For Preferences, name all six themes:
  System, Light, Dark, Engineering Dark, ION Dark, ION Light.

---

### `project_page.md` — Project Page

**Stage:** 2 — Placeholder in Stage 1
**Opens from:** Help → Project Page

Stage 1 placeholder:

```markdown
# Project Page

> **This help topic will be available in Stage 2.**
> It covers: viewing project metadata, the effective token table,
> support file references, and the project validation panel.

See **Getting Started** for an introduction to KiCad SpecGen.
```

[Stage 2 — Not yet written]

Required content (for Stage 2 author):

```text
Active .kicad_specgen file location
Selected environment
KiCad project paths (KICAD_PROJECT_DIR, GIT_PROJECT_DIR)
Effective token table panel — Token, Resolved Path, Source, Status
Support files panel — kicad_pro, logo, CSS, templates
Token status icons: ✓ resolved, ⚠ skipped, ✗ missing
Validation panel — per-field results
```

---

### `variables_jinja.md` — Variables and Jinja Templates

**Stage:** 2 — Placeholder in Stage 1
**Opens from:** Help → Variables and Jinja Templates

Stage 1 placeholder:

```markdown
# Variables and Jinja Templates

> **This help topic will be available in Stage 2.**
> It covers: Jinja2 template syntax, available SpecGen variables,
> custom variable naming rules, and template examples.

See `SpecGen_Help_JinJa.md` in the documentation folder for a
detailed style example.
```

[Stage 2 — Not yet written]

Required content (for Stage 2 author):

```text
Jinja variable syntax: {{ variable_name }}
Loops: {% for item in list %}
Conditionals: {% if condition %}
Available SpecGen variables:
  project metadata: name, display_name, revision, engineer, company,
                    date, copyright, release_name, document_number
  KiCad text_variables from .kicad_pro
  custom variables from .kicad_specgen → variables.custom
Custom variable naming rules: ^[A-Z][A-Z0-9_]*$
Markdown template examples
HTML template examples
CSV template examples (BOM)
Engineering examples (revision block, author block)
```

Authoring notes:

- `SpecGen_Help_JinJa.md` is the canonical style example — consult it
  before writing this page.
- Show concrete before/after examples: template source → rendered output.

---

### `jobset.md` — Jobset

**Stage:** 3 — Placeholder in Stage 1
**Opens from:** Help → Jobset

Stage 1 placeholder:

```markdown
# Jobset

> **This help topic will be available in Stage 3.**
> It covers: selecting a .kicad_jobset file, running destinations,
> reviewing output files, and how jobset results feed the Report tab.

See **Getting Started** for an introduction to KiCad SpecGen.
```

[Stage 3 — Not yet written]

Required content (for Stage 3 author):

```text
Dashboard subtab — project summary, active jobset, last run result
Setup & Run subtab
  selecting a .kicad_jobset file
  destination table — ID, type, output folder, status
  Run All, Run Selected, Stop on Error
  clear log before run option
Results subtab
  generated output files
  file tree: ✓ present, ⚠ stale, ✗ missing
  JOBSET_OUTPUT_DIR location
Output Log subtab
  live kicad-cli output during run
  save and clear log options
How jobset destinations feed the Report tab page definitions
How JOBSET_OUTPUT_DIR is derived from outputs[0].settings.output_path
```

---

### `report.md` — Report and Fabrication

**Stage:** 4 — Placeholder in Stage 1
**Opens from:** Help → Report and Fabrication

Stage 1 placeholder:

```markdown
# Report and Fabrication

> **This help topic will be available in Stage 4.**
> It covers: assembling a PDF report from jobset outputs and Markdown
> templates, and building a fabrication ZIP package.

See **Getting Started** for an introduction to KiCad SpecGen.
```

[Stage 4 — Not yet written]

Required content (for Stage 4 author):

```text
Report Recipe subtab
  page order — drag-and-drop or ordered list
  cover page configuration: template, title, subtitle, logo
  page source types:
    jobset — output from a specific destination
    markdown — Jinja2 template rendered to PDF
    custom_pdf — fixed PDF file inserted as-is
  section labels and page breaks
  filename template: {project_name}_{revision}_{date}_report.pdf
  output_dir: defaults to {JOBSET_OUTPUT_DIR}/report/

Preview & Build subtab
  generation scope: Report only / Report + Fabrication / Fabrication only
  pre-build checks: missing files, unresolved tokens, stale output
  build log
  overwrite confirmation
  dry run behavior (verify without writing)

Fabrication subtab
  FAB_OUTPUT_DIR — default: {JOBSET_OUTPUT_DIR}/fab/
  zip_filename_template: {project_name}_{revision}_{date}_fab.zip
  selecting jobset destinations to include
  per-destination ZIP folder: e.g. gerbers/
  README template and filename
  checksum algorithm (sha256, md5, sha1) and filename
```

---

### `logs.md` — Logs

**Stage:** 1 — Full
**Opens from:** Help → Logs

Required content:

```text
Application logs — what the Logs tab records
Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
Level filter and source filter
Clear Display — clears display, does not delete log files
Export Log — saves current display to a .txt file
Refresh — flushes buffered records
Background file logging: {KSG_SYSTEM_LOG_DIR}/specgen.log or fallback
Cross-session: logs do not persist across app restarts (export to save)
```

Authoring notes:

- Reference `SpecGen_Tab_Logs.md` for the authoritative Logs tab
  specification.
- Explain the difference between the Logs tab (structured SpecGen
  events, full session) and the Output Log subtab in Jobset (raw
  kicad-cli output, per-run).

---

### `troubleshooting.md` — Troubleshooting

**Stage:** 1 — Full (expand in later stages as new error types emerge)
**Opens from:** Help → Troubleshooting

Required content:

```text
kicad-cli not found
  → Edit → Configure kicad-cli...
  → Browse to kicad-cli executable
  → Click Check to verify

kicad_common.json not found
  → Verify KiCad is installed and has been run at least once
  → Check KICAD_COMMON_DIR in Configure tab → Local Machine

Missing KSG_* token
  → Edit → Resolve Missing Tokens...
  → Provide the absolute path for the token
  → Or Skip to suppress for this session

Invalid project .kicad_specgen location
  → File must be under a specgen/ folder within the KiCad project directory
  → Example: {KICAD_PROJECT_DIR}/specgen/myproject.kicad_specgen

Permission errors writing config files
  → Check that {KICAD_COMMON_DIR} and {KSG_COMPANY_DIR} are writable
  → Run with appropriate permissions

Jobset output missing  [Stage 3 — add when jobset is implemented]
Report file missing    [Stage 4 — add when report is implemented]
Template variable undefined  [Stage 2 — add when variables tab is implemented]
```

Authoring notes:

- Write as a flat Q&A list. Problem statement followed by numbered steps.
- Add new problems as each stage is implemented — see bracketed notes above.

---

### `kicad_specgen_local.md` — Local Configuration Reference

**Stage:** 1 — Full
**Opens from:** Application (not directly from Help menu — linked from
Configure tab Local Machine subtab and error dialogs)

Required content:

```text
File location: {KICAD_COMMON_DIR}/kicad_specgen_local.json
Purpose: machine-local state and absolute path token definitions
  tools — kicad-cli path and version
  tokens — KSG_* absolute path definitions
  setup — setup state and platform info
  last_session — last opened project reference and window geometry
  recent_projects — up to 10 recently opened projects
  skipped_tokens — token names suppressed on this machine
  preferences — UI preferences (theme)
This file is never committed to a repository.
```

Cross-reference: `SpecGen_Schema_Definitions.md §2` for the complete JSON
schema.

---

### `project_kicad_specgen.md` — Project File Reference

**Stage:** 2 — Placeholder in Stage 1
**Opens from:** Application (not directly from Help menu — linked from
project validation errors and Missing Tokens dialog)

Stage 1 placeholder:

```markdown
# Project File Reference (.kicad_specgen)

> **This reference will be available in Stage 2.**
> It covers: the full .kicad_specgen JSON schema, all sections,
> and tokenized path rules.

See **Project Setup and Tokens** for an introduction to token references.
```

[Stage 2 — Not yet written]

Required content (for Stage 2 author):

```text
File location: {KICAD_PROJECT_DIR}/specgen/<name>.kicad_specgen
Format: JSON with .kicad_specgen extension
Portable: yes — uses token references only
schema_version
workspace: mode, environment
project: name, display_name, document_number, revision, description,
         engineer, company, date, copyright, release_name
files: kicad_pro, logo, report_css, bom_css, title_page, end_page
variables.custom: key-value pairs (^[A-Z][A-Z0-9_]*$)
jobset: active_jobset, stop_on_error, clear_log_before_run,
        destinations, last_run
report: output_dir, filename_template, cover, pages.order,
        pages.definitions (source_type, destination, template,
        source_file, include, section_label, page_break_before)
fabrication: output_dir, zip_filename_template, destinations,
             readme, checksums
ui: active_tab, panel_sizes (not committed)
```

Cross-reference: `SpecGen_Schema_Definitions.md §5` for the complete JSON
schema.

---

## 4. Writing Process

When writing or updating a help file:

1. **Read the wireframe first.** For UI-facing help (configure_tab.md,
   project_page.md, jobset.md, report.md), read the corresponding
   `SpecGen_Tab_*.md` document before writing. The help file describes
   what the user sees — it must match the wireframe.

2. **Read the schema second.** For reference help (kicad_specgen_local.md,
   project_kicad_specgen.md), read the corresponding section of
   `SpecGen_Schema_Definitions.md` to ensure all fields are covered.

3. **Write the placeholder first.** If the stage is not yet implemented,
   add the placeholder template (see §2) immediately. Never leave a
   help file missing.

4. **Keep it user-facing.** Help files are for users, not developers.
   Do not reference internal module names, class names, or Python
   implementation details. Do not reference documentation filenames.

5. **Test in HelpDialog.** After writing, load the file in the running
   application and verify it renders correctly. Check headings, tables,
   code blocks, and bullet lists.

6. **Update this guide.** When a `[Stage N — Not yet written]` section
   is completed, remove the placeholder and the bracket note, and update
   the stage assignment table in §1.

---

## 5. Authoring Schedule

This schedule drives when each help file transitions from placeholder to full.

| File | Stage 1 | Stage 2 | Stage 3 | Stage 4 | Stage 5 |
|---|---|---|---|---|---|
| `index.md` | ✏ Write | — | Review | Review | Final |
| `getting_started.md` | ✏ Write | Review | Review | Review | Final |
| `project_setup_tokens.md` | ✏ Write | Review | — | — | Final |
| `configure_tab.md` | ✏ Write | — | — | — | Final |
| `project_page.md` | Placeholder | ✏ Write | Review | — | Final |
| `variables_jinja.md` | Placeholder | ✏ Write | — | — | Final |
| `jobset.md` | Placeholder | Placeholder | ✏ Write | Review | Final |
| `report.md` | Placeholder | Placeholder | Placeholder | ✏ Write | Final |
| `logs.md` | ✏ Write | — | Expand | Expand | Final |
| `troubleshooting.md` | ✏ Write | Expand | Expand | Expand | Final |
| `kicad_specgen_local.md` | ✏ Write | — | — | — | Final |
| `project_kicad_specgen.md` | Placeholder | ✏ Write | — | — | Final |

Legend: `✏ Write` = author this stage. `Expand` = add new content for
new features. `Review` = verify still accurate. `—` = no action needed.
`Final` = complete and reviewed.

---

## 6. Completion Checklist

This document is complete when all entries in the schedule above reach
`Final` status — i.e. all five implementation stages are done and all
help files have been reviewed against the final application.

Current status: **Stage 1 authoring in progress.**

| Requirement | Status |
|---|---|
| All Stage 1 files written (not placeholder) | ⬜ In progress |
| All Stage 2 files written | ⬜ Pending Stage 2 |
| All Stage 3 files written | ⬜ Pending Stage 3 |
| All Stage 4 files written | ⬜ Pending Stage 4 |
| All Stage 5 files reviewed against final application | ⬜ Pending Stage 5 |
| All files tested in HelpDialog (no rendering errors) | ⬜ Pending |
| This guide updated to remove all placeholder notes | ⬜ Pending |
| `SpecGen_Progress.md §9 Open Items` entry for this doc removed | ⬜ Pending |

---

*⚠ This document is a DRAFT. It requires updates at the end of each
implementation stage. Final version requires Stages 1–5 complete.*

*End of KiCad SpecGen Help File Authoring Guide.*
