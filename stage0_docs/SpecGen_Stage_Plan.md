# KiCad SpecGen — Implementation Stage Plan

> **Document role:** Formal staged implementation plan replacing the stage
> definitions in `SpecGen_Progress.md §10`.
> **Authority:** `SpecGen_File_Framework.md`, `SpecGen_Setup_Process.md`,
> `SpecGen_Tab_Report.md`.
> **Status:** Approved — ready for Stage 1 implementation.

---

## Overview

```text
Stage 0  Documentation and Architecture (complete)
Stage 1  Setup, GUI Foundation, Configuration Tab, Logs Tab
Stage 2  Project Tab, Variables Tab, Jobset Reading (no execution)
Stage 3  Jobset Execution (kicad-cli, Output Log, Results)
Stage 4  Report and Fabrication (unified tab, ZIP output)
Stage 5  Integration Testing and Polish
```

### Guiding principles for the stage sequence

```text
1. Prove the foundation before building on it.
   Each stage must pass its own acceptance tests before the next stage begins.

2. Read before you run.
   Stage 2 reads and displays all KiCad file content before Stage 3 executes
   any subprocess. No kicad-cli calls until the display side is verified.

3. Display before you package.
   Stage 3 verifies jobset output exists and is navigable before Stage 4
   assembles it into a report or ZIP.

4. Every stage ships its own tests.
   Tests are written alongside the code they cover. They are not deferred to
   a later stage.

5. Stage 5 is not a bug-fix sprint.
   It is a dedicated cross-stage integration pass with its own test plan.
   Feature bugs found in Stage 5 are fixed in the stage that owns the feature.
```

### What is not in any stage

```text
— Copy / Create From Existing Project wizard (deferred; documented as Future)
— Standalone Preferences dialog (Preferences is implemented as the fourth
  subtab within the Configure tab in Stage 1; no separate dialog is planned)
— QWebEngineView upgrade for Markdown rendering (monitor QTextBrowser limits;
  upgrade if needed during the stage that first hits the limit)
— KiCad S-expression file parsing (not needed; JSON is sufficient)
— kicad_common.json write path during setup (setup.py headless only; not a UI
  feature in any stage)
```

---

## Stage 0 — Documentation and Architecture

**Status: Complete.**

Deliverables produced:

```text
✓ SpecGen_Progress.md
✓ SpecGen_Setup_Process.md
✓ SpecGen_Tab_Report.md  (this replaces the separate Fabrication stage)
✓ SpecGen_Stage_Plan.md  (this document)
```

Remaining documentation tasks (all complete):

```text
✓ Update SpecGen_File_Framework.md:
    Fix §18 KICAD_COMMON_DIR copy-paste error (dir vs. file path)
    Add FAB_OUTPUT_DIR to protected derived runtime tokens list

✓ Update SpecGen_GUI_Menus.md:
    Redesign New Project dialog (remove KSG_SPECGEN_COMMON, remove inline
    environment creation, add environment selection from company file)

✓ Produce SpecGen_Terminology.md:
    Canonical list of all current token names, file names, GUI labels.
    Used during implementation to prevent terminology drift.
```

---

## Stage 1 — Setup, GUI Foundation, Configuration Tab, Logs Tab

### Scope

Build the application skeleton and validate that setup, configuration, logging,
and the GUI shell all work correctly before any project-domain content is added.

No project `.kicad_specgen` files are opened in Stage 1.
No KiCad files (`.kicad_pro`, `.kicad_jobset`) are parsed in Stage 1.
The Project, Variables, Jobset, and Report tabs exist as labeled placeholder pages.

### Modules to create

```text
main.py                          Application entry point
app.py                           QApplication setup, theme, font, signal wiring

core/
  platform_paths.py              OS detection, KICAD_COMMON_DIR resolution
  specgen_local_config.py        Load / validate / save kicad_specgen_local.json
  specgen_company_config.py      Load / validate / save kicad_specgen_company.json
  specgen_user_config.py         Load / validate / save kicad_specgen_users.json
  token_resolver.py              Build effective token table, report missing tokens
  validators.py                  All config validation rules
  file_ops.py                    Atomic JSON write, backup, directory creation
  migrations.py                  Schema version migration stubs (v1 baseline)
  logging_utils.py               Python logging config, structured log records
  app_state.py                   In-memory application state, observable fields

services/
  config_service.py              Save local / company / user configs, state refresh
  validation_service.py          run_config_validation() — config only, no project

setup/
  setup.py                       Entry point, phase orchestration, GUI/headless dispatch
  setup_macos.py                 macOS platform detection, kicad-cli search order
  setup_linux.py                 Linux platform detection, kicad-cli search order
  setup_windows.py               Windows platform detection, kicad-cli search order
  setup_utils.py                 .venv creation at {KSG_APP_DIR}/.venv, pip install,
                                 progress reporting, headless phase runners

ui/
  main_window.py                 QMainWindow, menu bar, sidebar, tab widget, status bar
  sidebar.py                     Sidebar navigation widget, active page tracking
  setup_wizard.py                SetupWizardDialog (6-phase wizard, phase navigator)
  theme.py                       Application theme constants, QSS template,
                                 palette loading. See SpecGen_GUI_Theme.md.
  actions.py                     QAction definitions, keyboard shortcuts

  tabs/
    configuration_tab.py         ConfigurationTab (5 subtabs: Local Machine,
                                 Company & User, Environments, Preferences,
                                 Validation) — see SpecGen_Tab_Configure.md
    logs_tab.py                  LogsTab — subscribes to log service, displays records
    project_tab.py               Placeholder page
    variables_tab.py             Placeholder page
    jobset_tab.py                Placeholder page
    report_tab.py                Placeholder page

  dialogs/
    local_tokens_dialog.py       Edit kicad_specgen_local.json tokens only
    missing_tokens_dialog.py     Display missing tokens, emit repair intents
    about_dialog.py              Version, platform, paths
    help_dialog.py               QTextBrowser Markdown renderer, OK button
    kicad_cli_dialog.py          Browse and check kicad-cli path
    add_user_dialog.py           Add / edit user in kicad_specgen_users.json
    clients_teams_dialog.py      Edit clients and teams in kicad_specgen_company.json

  widgets/
    token_table.py               Reusable token display table (read + edit modes)
    path_field.py                Path entry field with Browse button and status icon
    validation_panel.py          Display validation results (✓ ⚠ ✗ per check)
    log_viewer.py                Scrollable log record display widget

help/
  index.md                       Help index
  getting_started.md             First-run guide, setup.py invocation
  project_setup_tokens.md        KSG_* token reference, local config explanation
  configure_tab.md               Configure tab guide
  logs.md                        Logs tab guide
  troubleshooting.md             Common problems and fixes
  kicad_specgen_local.md         kicad_specgen_local.json schema reference
  jobset.md                      Placeholder — "Jobset features coming in Stage 2"
  variables_jinja.md             Placeholder — "Variables features coming in Stage 2"
  report.md                      Placeholder — "Report features coming in Stage 4"

.gitignore                       Includes .venv/ and kicad_specgen_local.json

tests/
  unit/
    test_platform_paths.py
    test_specgen_local_config.py
    test_specgen_company_config.py
    test_specgen_user_config.py
    test_token_resolver.py
    test_validators.py
    test_migrations.py
    test_file_ops.py
    test_logging_utils.py
    test_app_state.py
  integration/
    test_setup_headless.py
    test_config_service.py
    test_validation_service.py
  smoke/
    test_app_launch.py
    test_configuration_tab.py
    test_logs_tab.py
  fixtures/
    sample_local.json
    sample_company.json
    sample_users.json
    sample_company_standalone.json
    kicad_common_sample.json
```

### Acceptance criteria

```text
Setup
✓ python setup.py runs on macOS (Linux and Windows: documented as tested when
  platform is available)
✓ .venv created at {KSG_APP_DIR}/.venv
✓ .venv is not committed to the repository (.gitignore verified)
✓ kicad_specgen_local.json written with setup_complete = true
✓ Standalone mode creates minimal kicad_specgen_company.json with company
  name "personal" and kicad_specgen_users.json
✓ --headless mode runs all six phases without GUI
✓ --validate-only reports results without writing files
✓ --reconfigure pre-populates from existing configuration

Application shell
✓ Application starts and shows main window after completed setup
✓ Application detects missing setup and shows Setup Required banner
✓ [ Run Setup Now ] opens the setup wizard
✓ [ Defer — Limited Mode ] allows opening with limited functionality
✓ Limited mode warning bar is visible when setup is deferred
✓ Menu bar renders all four menus with correct items
✓ Sidebar shows all six pages plus Configuration separator
✓ All placeholder tabs show a clear "coming in Stage N" message
✓ Status bar shows current state (user, environment, setup status)

Configure tab
✓ Local Machine subtab shows kicad_specgen_local.json values
✓ .venv path and status shown in Local Machine subtab
✓ Token table shows all KSG_* tokens with status indicators
✓ Add Token validates KSG_* naming rule
✓ Remove Token rejects removal of required tokens
✓ Browse sets absolute path for selected token
✓ Save Local Changes validates before writing
✓ Company & User subtab shows company tree and user table
✓ Add / Edit / Deactivate User works correctly
✓ Environments subtab shows environment list and active session selectors
✓ Active environment and user dropdowns save to kicad_specgen_local.json
✓ Token priority note (USER → CLIENT → COMPANY → DEFAULT) is visible
✓ Validation subtab shows per-check results with ✓ ⚠ ✗
✓ Run Validation refreshes results without writing files
✓ [ Re-run Setup Wizard ] opens wizard in reconfigure mode

Logs tab
✓ Logs tab shows application startup log entries
✓ Log level (INFO, WARNING, ERROR) is visually distinguished
✓ Log viewer is scrollable
✓ Setup wizard actions appear in the log

Dialogs
✓ Local Tokens dialog opens from Edit menu and saves correctly
✓ Help dialog opens and renders all Stage 1 .md files correctly
✓ Help dialog shows clear error if .md file is missing
✓ About dialog shows version, platform, .venv path, config path
✓ kicad-cli dialog allows Browse, Check, and saves to kicad_specgen_local.json
```

### Automated tests

```text
Unit tests
  test_platform_paths       OS detection, KiCad config dir per platform
  test_specgen_local_config Load valid, load missing, reject protected token,
                            reject non-absolute path, reject non-KSG_ name,
                            recent_projects capped at 10
  test_specgen_company_config Load valid, reject absolute paths, validate
                              environment type enum, load standalone minimal
  test_specgen_user_config  Load valid, reject duplicate worker_id
  test_token_resolver       Resolve reference, resolve nested, report missing,
                            precedence (runtime > local > kicad_common),
                            protected tokens cannot be user-defined
  test_validators           All required tokens present/missing, kicad-cli path,
                            recent project paths
  test_migrations           missing schema_version treated as v1
  test_file_ops             Atomic write, backup creation, directory creation
  test_logging_utils        Logger initialises, records emit correctly,
                            QtLogHandler delivers records via Signal
                            (see SpecGen_Tab_Logs.md §logging_utils for spec)
  test_app_state            Fresh AppState() has all-None config fields and
                            empty resolved_tokens; config_reloaded signal fires
                            when local_config is set; dirty_changed signal fires
                            when dirty_project or dirty_local is set;
                            setup_state_changed signal fires when setup_complete
                            is set (use pytest-qt qtbot.waitSignal)
```

### Key interface contracts

See `SpecGen_Progress.md §5` for the complete specifications of:
- `AppState` — fields, signals, ownership, and canonical update protocol
- `ValidationResult` and `ValidationReport` — dataclass definitions
- All core module "Must Not Do" constraints

See `SpecGen_Tab_Logs.md §logging_utils` for the `QtLogHandler` specification.

```text
Integration tests
  test_setup_headless       Run setup_utils with fixture paths, verify
                            kicad_specgen_local.json created correctly
  test_config_service       Save local tokens, save company config, state refresh
  test_validation_service   Full config validation pass, validation with
                            missing tokens, validation with missing company file

Smoke tests (require display)
  test_app_launch           Application starts, main window visible
  test_configuration_tab    Tab opens, subtabs navigate, save and reload work
  test_logs_tab             Log entries appear after startup

Terminology regression tests
  Assert no file in core/ or ui/ contains KICAD_SPECGEN_DIR (old token)
  Assert no file uses kicad_specgen.json (old local config name)
  Assert no file uses KSG_SPECGEN_COMMON (old token name)
  Assert no file uses [Fabrication] as a sidebar label
```

### Risks

```text
- QTextBrowser Markdown rendering: test table rendering early in Stage 1.
  If complex tables render poorly, plan QWebEngineView upgrade for Stage 2.

- .venv creation inside {KSG_APP_DIR}: verify on case-sensitive file systems
  (Linux) and paths with spaces (Windows).

- PySide6 availability: confirm correct pip package name per platform.
  Minimum version is 6.4 (for QTextBrowser.setMarkdown()). If the installed
  version is < 6.4, setup_utils must warn and refuse to complete Stage 1.

- CI display for smoke tests: smoke tests (test_app_launch, test_configuration_tab,
  test_logs_tab) require a Qt display. In headless CI environments:
    Linux:   set QT_QPA_PLATFORM=offscreen  (or use Xvfb)
    macOS:   no action needed (virtual framebuffer available)
    Windows: no action needed (virtual display available on GitHub Actions)
  Smoke tests must be marked @pytest.mark.smoke and explicitly requested in CI.
  They must not be silently skipped — a skipped smoke test is the same as a
  missing smoke test.

  Register the marker in pytest.ini to avoid PytestUnknownMarkWarning:
    [pytest]
    markers =
        smoke: requires Qt display (set QT_QPA_PLATFORM=offscreen in CI)

- QtLogHandler thread safety: the logging-to-Qt bridge (logging_utils.QtLogHandler)
  must be instantiated before any log record is emitted. Instantiate it in app.py
  before creating any other objects. See SpecGen_Tab_Logs.md for the full spec.
```

### What not to implement in Stage 1

```text
— Project file open / save / close
— kicad_pro_parser, kicad_jobset_parser, kicad_env
— project_service
— New Project dialog
— Missing Tokens dialog (defer to Stage 2 where projects are opened)
— Jinja2 template rendering
— Any subprocess / kicad-cli execution
```

---

## Stage 2 — Project Tab, Variables Tab, Jobset Reading

### Scope

Open, display, and save SpecGen project files. Parse KiCad project and jobset
files in read-only mode. Display all project-domain content. No kicad-cli
subprocess calls in this stage.

This stage introduces the concept of an "open project" to the application.
After Stage 2, every project-domain tab (Project, Variables, Jobset Dashboard,
Jobset Setup & Run, Jobset Results) shows correct data from real KiCad files.
The Run button in Jobset Setup & Run exists but is disabled.

### Modules to create or complete

```text
core/
  kicad_pro_parser.py       Parse text_variables from .kicad_pro JSON
  kicad_jobset_parser.py    Parse outputs[], ids, descriptions from .kicad_jobset
  kicad_env.py              Read environment.vars from kicad_common.json
  project_config.py         Load / validate / save / migrate .kicad_specgen

services/
  project_service.py        Open, create, save, close project. Full startup
                            sequence: local → company → users → project →
                            token resolution → validation

ui/
  tabs/
    project_tab.py          Full implementation: project metadata, token table,
                            validation panel, effective path display
    variables_tab.py        Full implementation: KiCad text variables (read-only),
                            custom variables (editable), Jinja2 syntax reference
    jobset_tab.py           Full implementation of Dashboard and Setup & Run
                            subtabs (read-only — Run button disabled).
                            Full implementation of Results subtab (output folder
                            scan, file tree, status symbols, file preview panel).
                            Output Log subtab: placeholder "Run a jobset to
                            generate log output."

  dialogs/
    new_project_dialog.py   Select KiCad project folder, select environment from
                            company file, name the .kicad_specgen file
    missing_tokens_dialog.py Display missing tokens, allow adding to local config

  widgets/
    output_tree.py          File tree widget for Results subtab
    file_preview.py         Preview panel for PDF, image, text, CSV files

help/
  project_page.md           Project tab guide
  variables_jinja.md        Full Jinja2 variable guide (replaces placeholder)
  project_kicad_specgen.md  .kicad_specgen schema reference
  jobset.md                 Full jobset guide (replaces placeholder)

tests/
  unit/
    test_kicad_pro_parser.py
    test_kicad_jobset_parser.py
    test_kicad_env.py
    test_project_config.py
  integration/
    test_project_service.py
    test_token_resolution_full.py
    test_output_folder_scan.py
  smoke/
    test_project_tab.py
    test_variables_tab.py
    test_jobset_read.py
  fixtures/
    sample_project.kicad_specgen
    sample_kicad_pro.json
    sample_kicad_jobset.json
    sample_output_folder/     (pre-populated with fixture output files)
```

### Acceptance criteria

```text
Project open / create
✓ New Project dialog selects KiCad folder and environment, creates .kicad_specgen
  under specgen/ subfolder
✓ Open Project dialog opens an existing .kicad_specgen file
✓ Startup sequence loads all four config layers in correct order
✓ Effective token table is built and displayed on Project tab
✓ Missing token triggers Missing Tokens dialog
✓ Adding token via dialog writes kicad_specgen_local.json, not project file
✓ Save and Save As write .kicad_specgen correctly
✓ Close Project clears all project-domain displays

Project tab
✓ Active project path, environment, KiCad project folder are shown correctly
✓ Token table shows all effective tokens with source layer annotation
✓ Validation panel shows project-level validation results
✓ Open Recent shows last 10 projects (oldest removed at 11)

Variables tab
✓ KiCad text variables from .kicad_pro are shown read-only
✓ Multiple .kicad_pro files: auto-selects by name match, prompts if ambiguous
✓ Custom variables are shown as editable
✓ Custom variable names validated against ^[A-Z][A-Z0-9_]*$ pattern
✓ Jinja2 syntax ( {{ variable }} ) explained and distinguished from
  SpecGen token syntax ( {TOKEN_NAME} )

Jobset reading
✓ Dashboard subtab shows project, jobset, output root, kicad-cli, last run
✓ Setup & Run table populates all destinations from .kicad_jobset
✓ Run button is present but visually disabled with tooltip "Run available in
  Stage 3"
✓ Destination heading overrides and notes are editable and save to .kicad_specgen
✓ Results subtab scans JOBSET_OUTPUT_DIR and displays file tree
✓ File status symbols (✓ ⚠ ✗) shown correctly based on file existence and age
✓ File preview panel opens for PDF, image, text, and CSV files
✓ Stale file detection: warns when output file is older than source .kicad_sch
✓ Selecting a new .kicad_jobset reconciles stale destination keys (§Q9 behavior)
```

### Automated tests

```text
Unit tests
  test_kicad_pro_parser     Parse text_variables, handle missing section,
                            handle multiple .kicad_pro in directory
  test_kicad_jobset_parser  Parse outputs[], verify destination ID extraction,
                            JOBSET_OUTPUT_DIR derivation, warn on differing paths
  test_kicad_env            Load environment.vars, handle missing section
  test_project_config       Load valid, reject outside specgen/ folder, derive
                            KSG_PROJECT_SPECGEN_DIR and KICAD_PROJECT_DIR,
                            reject absolute paths, validate custom variable names,
                            dirty flag triggers per section

Integration tests
  test_project_service      Full open sequence (all four layers), missing company
                            file, missing token, save and reload
  test_token_resolution_full Precedence: USER > CLIENT > COMPANY > DEFAULT,
                             runtime tokens override all
  test_output_folder_scan   Scan fixture output folder, verify tree structure,
                            stale file detection

Smoke tests
  test_project_tab          Opens fixture project, token table correct
  test_variables_tab        KiCad vars read-only, custom vars editable
  test_jobset_read          Dashboard and Setup & Run table populated correctly,
                            Results file tree shows fixture files
```

### Risks

```text
- Dirty state tracking: define per §Q8 (all sections except ui trigger dirty).
  Implement the flag in app_state and verify it is not triggered by ui section
  saves (panel sizes, last active tab).
- File preview for PDF: PyMuPDF must be installed in Stage 2 (Stage Full deps).
  If only Stage 2 deps are installed, show a "PDF preview requires Full install"
  message rather than crashing.
- .kicad_jobset format: verify against a real KiCad 9 jobset file before
  finalizing test fixtures.
```

### What not to implement in Stage 2

```text
— kicad-cli subprocess execution (Run button exists but is disabled)
— Report rendering
— Fabrication ZIP packaging
— Output Log subtab live feed
```

---

## Stage 3 — Jobset Execution

### Scope

Enable kicad-cli jobset execution. Add live Output Log feed. Connect Output Log
to the Logs page for persistence. Implement stale destination reconciliation.

After Stage 3, the full Jobset workspace is functional.

### Modules to create or complete

```text
services/
  jobset_service.py        kicad-cli subprocess management, output capture,
                           run state, stop-on-error, destination reconciliation

ui/
  tabs/
    jobset_tab.py          Complete Output Log subtab (live feed from
                           jobset_service). Enable Run All / Run Selected / Stop.
                           Connect Output Log → Logs page.

help/
  jobset.md                Update with execution guide, run controls,
                           Output Log, log persistence

tests/
  unit/
    test_jobset_service.py
  integration/
    test_jobset_execution.py
    test_log_persistence.py
  smoke/
    test_jobset_run.py
  fixtures/
    mock_kicad_cli.py      Subprocess mock that returns fixture output and exit codes
```

### Acceptance criteria

```text
Execution
✓ Run All executes kicad-cli jobset run for all selected destinations
✓ Run Selected executes only checked destinations
✓ Stop terminates the subprocess cleanly
✓ Stop on Error halts the run after the first failed destination
✓ Clear log before run clears the Output Log if the option is checked

Output Log
✓ Output Log subtab shows live stdout/stderr from kicad-cli
✓ Each destination shows ► Running, then ✓ / ✗ / ⚠ on completion
✓ Run complete summary line appears at end of run
✓ [ Clear Log ] clears the Output Log display (not the Logs page)
✓ [ Save Log... ] saves log content to {KSG_PROJECT_SPECGEN_DIR}/logs/
✓ [ Copy to Clipboard ] copies the full log text

Log persistence
✓ Output Log content feeds the Logs workspace page for persistence
✓ Logs page retains log content across tab switches
✓ Logs page retains log content across project reloads within a session

Stale destination reconciliation (§Q9)
✓ Selecting a new .kicad_jobset with different destination IDs:
    — Existing matching destinations: overrides preserved
    — New destinations: added with empty overrides
    — Stale destinations: flagged [stale] in Setup & Run table, not deleted
✓ User can manually remove stale destinations from .kicad_specgen
✓ [stale] destinations are excluded from Run All and Run Selected

Results refresh
✓ Results subtab refreshes automatically after a run completes
✓ File status symbols update to reflect new run output
```

### Automated tests

```text
Unit tests
  test_jobset_service       Command construction, subprocess mock: success,
                            failure, stop-on-error, partial run, clean stop

Integration tests
  test_jobset_execution     Full run with mock kicad-cli, verify output files
                            appear in fixture output folder, verify log entries
  test_log_persistence      Output Log → Logs page: verify entries survive tab
                            switch and project reload

Smoke tests
  test_jobset_run           Run button enabled, mock run completes, Output Log
                            shows entries, Results tab refreshes
```

### Risks

```text
- Subprocess output encoding: kicad-cli output may be UTF-8 or platform locale.
  Detect and handle both; fall back to Latin-1 with replacement characters.
- Live feed UI performance: streaming a high volume of output lines to a
  QTextEdit widget can freeze the UI. Use a QThread + signal for output capture.
- Windows subprocess handling: test STARTUPINFO and creationflags to suppress
  console windows on Windows.
```

### What not to implement in Stage 3

```text
— Report rendering
— Fabrication ZIP packaging
— Report tab content (remains placeholder)
```

---

## Stage 4 — Report and Fabrication

### Scope

Implement the Report tab (three subtabs: Report Recipe, Preview & Build,
Fabrication). Render Jinja2 templates to PDF. Assemble multi-source PDF reports.
Build and write fabrication ZIP packages. Implement overwrite confirmation.

Fabrication is a subtab within the Report tab.
The Fabrication subtab is the third subtab within the Report workspace.
The sidebar shows `[Report]` only.

Reference wireframes: `SpecGen_Tab_Report.md`.

### Modules to create or complete

```text
core/
  render/
    jinja_renderer.py      Render .md templates with token + variable injection,
                           return rendered Markdown string
    pdf_assembler.py       Convert rendered Markdown to PDF pages, insert jobset
                           PDF files, assemble final report PDF

  fab/
    package_builder.py     Collect files from JOBSET_OUTPUT_DIR per fabrication
                           config, render README template, compute checksums,
                           write ZIP to FAB_OUTPUT_DIR

services/
  report_service.py        Orchestrate: pre_build_checks(), dry_run(),
                           render_report(), build_fab_zip(),
                           build_report_and_fab()

ui/
  tabs/
    report_tab.py          Full ReportTab with three subtabs:
                             RecipeSubtab (page order, cover, source config)
                             BuildSubtab (scope selector, pre-build checks,
                                         build log, outputs panel)
                             FabricationSubtab (ZIP location, contents,
                                               README, checksums)

help/
  report.md                Full report guide (replaces placeholder)
  variables_jinja.md       Update with report template variable reference

tests/
  unit/
    test_jinja_renderer.py
    test_pdf_assembler.py
    test_package_builder.py
    test_report_service.py
  integration/
    test_report_build.py
    test_fab_build.py
    test_overwrite_behavior.py
  smoke/
    test_report_tab.py
  fixtures/
    templates/
      cover_standard.md
      project_summary.md
      fab_readme_standard.md
    sample_report_recipe.json
    sample_fab_config.json
```

### Acceptance criteria

See `SpecGen_Tab_Report.md` — Acceptance Criteria section.

Key items:

```text
Report build
✓ Report only: renders PDF to {JOBSET_OUTPUT_DIR}/report/
✓ Report + Fabrication: renders report AND builds ZIP
✓ Fabrication only: builds ZIP from existing jobset outputs, no re-render
✓ Dry run: resolves all sources, shows what would be generated, writes nothing
✓ Overwrite confirmation dialog appears when target exists
✓ [ Overwrite ] replaces, [ Choose New Name... ] saves to alternate path,
  [ Cancel ] aborts with no writes

Fabrication ZIP
✓ ZIP written to FAB_OUTPUT_DIR (default: {JOBSET_OUTPUT_DIR}/fab/)
✓ ZIP is not written inside KICAD_PROJECT_DIR
✓ ZIP internal structure matches Rename in ZIP configuration
✓ README rendered from Jinja2 template and included in ZIP
✓ Checksums computed and included in ZIP
✓ ZIP filename resolved from template tokens

FAB_OUTPUT_DIR token
✓ FAB_OUTPUT_DIR is a protected derived runtime token
✓ FAB_OUTPUT_DIR cannot be defined in kicad_specgen_local.json tokens
✓ FAB_OUTPUT_DIR defaults to {JOBSET_OUTPUT_DIR}/fab/ when not set
✓ FAB_OUTPUT_DIR resolves from .kicad_specgen → fabrication.output_dir when set
```

### Automated tests

```text
Unit tests
  test_jinja_renderer       Render template with tokens, render with variables,
                            missing variable warning, syntax error handling
  test_pdf_assembler        Assemble fixture pages, verify page count in output,
                            verify jobset PDF inserted correctly
  test_package_builder      Build ZIP from fixture files, verify structure,
                            verify README included, verify checksums correct
  test_report_service       pre_build_checks all pass, pre_build_checks fail
                            on missing source, dry_run returns plan without
                            writing, build_report_and_fab integration

Integration tests
  test_report_build         Render fixture templates + fixture jobset outputs →
                            verify PDF file exists and is readable
  test_fab_build            Build ZIP from fixture outputs → verify ZIP structure,
                            README content, checksum file correctness
  test_overwrite_behavior   Target exists → confirmation dialog triggered;
                            [ Overwrite ] → file replaced; [ Cancel ] → no write

Smoke tests
  test_report_tab           All three subtabs navigate; Recipe saves correctly;
                            Build runs dry run without error
```

### Risks

```text
- PDF assembly library: PyMuPDF (fitz) is the recommended library for PDF
  manipulation. Test with a 50+ page schematic PDF to confirm it handles
  expected file sizes and page counts without memory issues.
- Markdown-to-PDF conversion: the chosen approach is render Markdown → HTML →
  PDF via WeasyPrint (already specified in requirements-stage4.txt).
  `pdf_assembler.py` uses this pipeline: Jinja2 renders to HTML, WeasyPrint
  converts HTML to PDF pages, PyMuPDF assembles the pages into the final PDF.
- ZIP path traversal safety: validate that folder values in fabrication
  destinations do not contain `..` or absolute paths before writing the ZIP.
```

### What not to implement in Stage 4

```text
— Copy / Create From Existing Project wizard
— Full Preferences dialog
— Any changes to the Jobset or Project tabs beyond bug fixes
```

---

## Stage 5 — Integration Testing and Polish

### Scope

Cross-stage integration tests covering the full workflow from setup through
fabrication ZIP output. UI polish: consistent spacing, disabled-state behavior,
keyboard navigation, status bar accuracy across all tabs. Terminology regression
sweep. Performance baseline.

This stage does not add new features. Issues found that require new code belong
to the stage that owns the affected feature.

### Deliverables

```text
tests/
  integration/
    test_full_workflow.py        Setup → open project → run jobset → build
                                 report → build FAB ZIP end-to-end
    test_cross_tab_consistency.py Token changes in Configure tab reflected
                                 on Project tab without restart
    test_session_restore.py      Close and reopen application, verify last
                                 project and session state restored correctly
    test_recent_projects.py      11 projects opened → list capped at 10
    test_dirty_state_all_tabs.py Dirty flag set/cleared correctly in Project,
                                 Variables, Jobset, Report tabs
    test_help_all_topics.py      All help .md files render without error in
                                 HelpDialog
  regression/
    test_terminology.py          No stale token names in codebase (grep-based)
    test_sidebar_no_fabrication.py No [Fabrication] sidebar label in codebase
  performance/
    test_open_large_project.py   Open project with 100+ token references in
                                 <2 seconds
    test_jobset_large_output.py  Results tab scans folder with 200+ files
                                 without UI freeze
```

### Acceptance criteria

```text
Full workflow
✓ Fresh machine: setup.py → open project → run jobset → build report + FAB ZIP
  completes without error
✓ All output files are in correct locations
✓ ZIP structure is correct and checksums verify

Cross-tab consistency
✓ Adding a token in Configure tab appears in Project tab token table
  after tab switch (no restart required)
✓ Changing active environment in Configure tab updates status bar
  after save

Session restore
✓ Last open project is restored on next launch
✓ Last active tab is restored on next launch
✓ Recent projects list is correct after restore

Polish
✓ All buttons have correct enabled/disabled states when no project is open
✓ All buttons have correct enabled/disabled states when project is open but
  jobset has not been run
✓ Status bar content is correct on all tabs
✓ Tab keyboard navigation works (Tab, Shift+Tab, arrow keys in tables)
✓ No UI freeze during jobset run (Output Log streams live)
✓ No UI freeze during output folder scan (Results tab with 200+ files)

Terminology regression
✓ No file in core/ or ui/ contains KICAD_SPECGEN_DIR
✓ No file uses kicad_specgen.json as local config name
✓ No file uses KSG_SPECGEN_COMMON
✓ No file uses [Fabrication] as a sidebar label
✓ No file uses KICAD_SPECGEN_DIR as a token name

Help
✓ All help .md files present and renderable
✓ No placeholder-only help files remain (all stages complete)
✓ QTextBrowser table rendering acceptable for all existing help tables
```

---

## Stage Summary Table

| Stage | Primary Deliverable | Core Modules Added | New UI | Tests |
|---|---|---|---|---|
| 0 | Documentation | — | — | — |
| 1 | Setup + GUI shell + Config tab + Logs | platform_paths, all config loaders, token_resolver, validators, migrations, file_ops, logging_utils, app_state | main_window, sidebar, setup_wizard, configuration_tab, logs_tab, all Stage 1 dialogs | Core unit, setup integration, GUI smoke |
| 2 | Project + Variables + Jobset reading | kicad_pro_parser, kicad_jobset_parser, kicad_env, project_config, project_service | project_tab, variables_tab, jobset_tab (read-only), new_project_dialog, missing_tokens_dialog | Parser unit, project service integration, output scan, GUI smoke |
| 3 | Jobset execution | jobset_service | jobset_tab (Output Log live), Run/Stop buttons enabled | Subprocess mock, log persistence, GUI smoke |
| 4 | Report + Fabrication | jinja_renderer, pdf_assembler, package_builder, report_service | report_tab (3 subtabs) | Renderer unit, assembler unit, builder unit, report + FAB integration |
| 5 | Integration + Polish | — | — | Full workflow, cross-tab, session restore, terminology regression, performance |


---

Note: `SpecGen_Help_Guide.md` is a living draft updated at the end of each stage.

*End of SpecGen Implementation Stage Plan.*
