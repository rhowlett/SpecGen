# KiCad SpecGen — Setup Process Specification

> **Document role:** Primary specification for the SpecGen setup process and the
> in-application Configuration workspace.
> **Authority:** `SpecGen_Terminology.md`, `SpecGen_File_Framework.md`,
> `SpecGen_Tab_Configure.md`.
> **Companion documents:** `SpecGen_Schema_Definitions.md`,
> `SpecGen_GUI_Menus.md`, `SpecGen_Tab_Jobset.md`.
> **Status:** Approved — ready for Stage 1 implementation.

---

## 1. Purpose

This document defines:

1. The SpecGen first-run setup process and the `setup.py` bootstrap program.
2. The in-application **Configuration workspace** — a permanent sidebar tab that
   mirrors the setup process for post-installation editing without re-running
   `setup.py`.
3. The startup detection logic that determines whether setup has completed and
   whether to launch the setup wizard automatically.
4. Answers to all ten pre-coding questions (see §9 of this document).
5. GUI wireframes for all setup screens and the Configure tab, following the
   wireframe style of `SpecGen_Tab_Jobset.md`.

---

## 2. Design Principles

```text
1. The .venv is always located at {KSG_APP_DIR}/.venv.
   This keeps all SpecGen installation artifacts in one place.
   If the user wants to uninstall SpecGen completely, deleting {KSG_APP_DIR}
   removes the application, the virtual environment, and all bundled defaults.
   The .venv folder is listed in the SpecGen .gitignore and is never committed.

2. The main application and the setup process share the same core modules.
   setup.py is not a separate codebase — it uses core/ and services/.

3. setup.py can run headlessly (no GUI) for CI and scripted environments.
   setup.py can also launch a GUI wizard when a display is available.

4. If setup has not completed, the main application detects this at startup
   and launches the setup wizard inline rather than blocking with an error.
   The user may also defer setup and use the Configure tab to configure
   the application manually.

5. The Configure tab in the main application replicates all setup
   capabilities so users never need to re-run setup.py for normal edits.

6. setup.py is the correct path for:
     — Fresh machine installation
     — Creating or updating {KSG_APP_DIR}/.venv
     — Installing or upgrading dependency stages
     — Platform-specific tool detection on a new OS
     — Scripted or CI setup
   The Configure tab is the correct path for:
     — Changing KSG_* tokens
     — Switching active environment or active user
     — Updating user info
     — Editing company, client, and team data

7. Setup is a database-building exercise.
   The setup process locates and records where things are.
   The individual SpecGen project (.kicad_specgen file) makes the final
   per-project selections — choosing which environment, which client, which
   token overrides apply, and which support files to use.
   Token priority order at project runtime (highest to lowest):
     USER → CLIENT → COMPANY → DEFAULT

8. All writes follow the Framework ownership rules:
     — Local tokens and session state  → kicad_specgen_local.json
     — Environment and company data    → kicad_specgen_company.json
     — User data                       → kicad_specgen_users.json
     — KiCad-owned files               → never modified during normal operation
       (kicad_common.json may be modified during setup only with user approval
        and a timestamped backup)
```

---

## 3. Setup Entry Point and Invocation

### 3.1 Entry Point

The canonical setup entry point is:

```text
python setup.py
```

Run from the root of the SpecGen application repository (`{KSG_APP_DIR}`).

The `.venv` is always created at:

```text
{KSG_APP_DIR}/.venv
```

This location is fixed and is listed in `.gitignore`. It is never committed to the
SpecGen repository.

For platform-specific dispatch, `setup.py` detects the OS and calls:

```text
setup/setup_macos.py
setup/setup_linux.py
setup/setup_windows.py
```

All platform files share utilities from:

```text
setup/setup_utils.py
core/platform_paths.py
core/file_ops.py
core/specgen_local_config.py
core/specgen_company_config.py
core/specgen_user_config.py
core/validators.py
```

### 3.2 Invocation Options

```text
python setup.py                    Standard interactive setup (GUI if display available)
python setup.py --headless         Text-only mode, no GUI
python setup.py --no-prompt        Accept all defaults without prompting (for CI)
python setup.py --stage STAGE      Install only up to dependency stage STAGE
python setup.py --full             Install all dependency stages
python setup.py --reconfigure      Force re-run even if setup_complete = true
python setup.py --validate-only    Run validation checks and report; make no changes
```

### 3.3 GUI vs. Headless Detection

```text
If --headless is specified:
  Run text-mode setup.
Else if a display is available (DISPLAY on Linux, always on macOS/Windows):
  Launch the setup GUI wizard.
Else:
  Fall back to text-mode setup.
```

### 3.4 .gitignore Requirements

The SpecGen application repository `.gitignore` must include:

```text
# Virtual environment — always installed at {KSG_APP_DIR}/.venv
.venv/

# Local machine configuration — contains absolute paths; never commit
# (this file lives in the KiCad user config folder, not in the repo,
#  but this entry protects against accidental copies being committed)
kicad_specgen_local.json
```

---

## 4. Startup Detection and Auto-Launch

### 4.1 Startup Check Sequence

When the main SpecGen application starts, before displaying the main window:

```text
Step 1.  Detect KICAD_COMMON_DIR for the current OS and KiCad version.

Step 2.  Check whether kicad_specgen_local.json exists in KICAD_COMMON_DIR.
         If missing → go to Step 5.

Step 3.  Load kicad_specgen_local.json.
         If load fails (corrupt JSON, unreadable) → go to Step 5.

Step 4.  Check setup.setup_complete == true.
         If false or missing → go to Step 5.

Step 5.  (Setup required)
         Show the Setup Required banner (§5.1) inside the main window,
         then open the Setup Wizard dialog (§6).
         Do not open the main workspace until setup completes or is deferred.

Step 6.  (Setup complete)
         Continue normal startup sequence:
           Load kicad_specgen_company.json
           Load kicad_specgen_users.json
           Restore last session
           Populate main window
```

### 4.2 Setup Required Banner

If setup is required, the main window shows a banner instead of the normal workspace.

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [File]   [Edit]   [View]   [Help]                                                                          │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                            │
│                             ┌──────────────────────────────────────────────┐                              │
│                             │  ⚙  KiCad SpecGen Setup Required             │                              │
│                             │                                              │                              │
│                             │  SpecGen has not been configured on this     │                              │
│                             │  machine.                                    │                              │
│                             │                                              │                              │
│                             │  Setup takes about 2 minutes and will:       │                              │
│                             │    • Locate kicad-cli                        │                              │
│                             │    • Create your local configuration         │                              │
│                             │    • Set up your workspace                   │                              │
│                             │                                              │                              │
│                             │       [ Run Setup Now ]                      │                              │
│                             │       [ Defer — Limited Mode ]               │                              │
│                             └──────────────────────────────────────────────┘                              │
│                                                                                                            │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ STATUS: Setup required — configuration not found                                                           │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

**[ Run Setup Now ]** — Opens the Setup Wizard dialog (§6).

**[ Defer — Limited Mode ]** — Allows the application to open in a restricted state
where no project can be opened or created. The Configure tab is accessible so
the user can configure manually. A persistent warning bar reminds the user that
setup is incomplete.

### 4.3 Limited Mode Warning Bar

When deferred, a persistent warning bar is shown below the menu bar:

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [File]   [Edit]   [View]   [Help]                                                                          │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ⚠  Setup incomplete — project operations are disabled.  [ Run Setup ] [ Dismiss ]                         │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ...workspace...                                                                                            │
```

---

## 5. Setup Process Overview

The setup process has six phases, executed in order:

```text
Phase 1.  Platform Detection
          Detect OS, KiCad version, KICAD_COMMON_DIR.

Phase 2.  Dependency Installation
          Create or update .venv/, install required Python packages.

Phase 3.  Tool Detection
          Locate kicad-cli, detect KiCad version string.

Phase 4.  Workspace Mode Selection
          User chooses: Shared/Repo workspace or Standalone/Local workspace.

Phase 5.  Company, Client, and User Configuration
          Identify or create KSG_COMPANY_DIR and populate company/user files.

Phase 6.  Local Token Configuration and Validation
          Collect remaining KSG_* tokens, write kicad_specgen_local.json,
          run final validation.
```

Each phase maps to one page of the Setup Wizard dialog.

**Important:** Setup builds the database of where things are located. The individual
SpecGen project (`.kicad_specgen` file) makes the final per-project selections —
choosing which environment, which client, which token overrides apply, and which
support files to use. Token priority order at project runtime:

```text
USER → CLIENT → COMPANY → DEFAULT
```

---

## 6. Setup Wizard Dialog

The Setup Wizard is a modal dialog with a left-side phase navigator, a central
content area, and standard navigation buttons.

### 6.1 Overall Wizard Layout

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    KiCad SpecGen Setup Wizard                                            │
├─────────────────────────┬────────────────────────────────────────────────────────────────────────────────┤
│ PHASES                  │                                                                                │
│                         │   (phase content area — changes per phase)                                     │
│ ▶ 1. Platform           │                                                                                │
│   2. Dependencies       │                                                                                │
│   3. Tool Detection     │                                                                                │
│   4. Workspace Mode     │                                                                                │
│   5. Company & User     │                                                                                │
│   6. Tokens & Validate  │                                                                                │
│                         │                                                                                │
│ ─────────────────────── │                                                                                │
│ Status:                 │                                                                                │
│  ✓ Platform detected    │                                                                                │
│  … Dependencies         │                                                                                │
│  … Tools                │                                                                                │
│  … Workspace            │                                                                                │
│  … Company              │                                                                                │
│  … Tokens               │                                                                                │
│                         │                                                                                │
├─────────────────────────┴────────────────────────────────────────────────────────────────────────────────┤
│                                               [ < Back ]  [ Next > ]             [ Finish ]  [ Cancel ]  │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Phase navigator:** Shows all six phases. Completed phases show ✓. Active phase
is highlighted. Future phases are dimmed. Clicking a completed phase navigates back.

**Status panel (left, below phases):** Shows real-time status of each phase as the
user progresses.

**Navigation buttons:**
- `< Back` — Return to the previous phase.
- `Next >` — Advance to the next phase (disabled until the current phase is valid).
- `Finish` — Available only on Phase 6 when validation passes.
- `Cancel` — Close without saving. Warns if any data was collected.

---

### 6.2 Phase 1 — Platform Detection

Detects the OS, locates `KICAD_COMMON_DIR`, and records the KiCad configuration
version. This phase runs first and its output is required by all subsequent phases.

#### KiCad configuration version detection algorithm

`platform_paths.py` must resolve the exact `KICAD_COMMON_DIR` path including
the KiCad configuration version number (e.g. `9.0`). The algorithm:

```text
Step 1.  If kicad-cli is already known (reconfigure mode or setup re-run):
           Run `kicad-cli --version` → parse version string → extract major.minor
           Use that as the config version (e.g. "9.0.3" → "9.0")
           Go to Step 4.

Step 2.  If kicad-cli is not yet known:
           Scan the OS-specific KiCad config parent directory for versioned
           subdirectories that look like config version folders:
             Windows: %APPDATA%\kicad\
             Linux:   ~/.config/kicad/
             macOS:   ~/Library/Preferences/kicad/
           Collect all subdirectory names that match the pattern \d+\.\d+
           (e.g. "8.0", "9.0", "9.1")

Step 3.  Select the detected version:
           If exactly one versioned folder exists → use it.
           If multiple exist → use the highest version number.
           If none exist → prompt the user to enter the version manually
             (they may be setting up before running KiCad for the first time;
              the folder will be created by KiCad on first launch).

Step 4.  Construct KICAD_COMMON_DIR:
           Windows: %APPDATA%\kicad\{version}\
           Linux:   ~/.config/kicad/{version}/
           macOS:   ~/Library/Preferences/kicad/{version}/

Step 5.  Verify: check that KICAD_COMMON_DIR exists (it may not on first run).
           If it does not exist:
             Create it (KiCad may not have run yet — this is valid).
             Log a warning: "KiCad config dir created; KiCad may not have been
             run yet on this machine."
           If it exists: proceed.
```

The detected or user-confirmed version is stored in
`kicad_specgen_local.json → tools.kicad_version` after Phase 3 completes
and in `KSG_SYSTEM_CONFIG_DIR` after Phase 6 completes.

**Multi-version installations:** If the user has both KiCad 8.0 and 9.0
installed, the algorithm selects 9.0 (highest). The Setup wizard shows the
detected version with a `[ Detect ]` button and an editable field so the user
can override if needed. The user-confirmed value is stored and used on all
subsequent startups.

#### Acceptance criteria (Phase 1)

```text
✓ OS detected correctly on macOS, Linux, Windows
✓ KICAD_COMMON_DIR resolved correctly for the running KiCad version
✓ Highest version selected when multiple config folders exist
✓ User prompted to enter version manually when no config folder exists
✓ KICAD_COMMON_DIR created (not error) when it does not yet exist
✓ Detected version shown in Setup wizard Phase 1 panel
✓ User can override detected version via editable field
```

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    KiCad SpecGen Setup Wizard                                            │
├─────────────────────────┬────────────────────────────────────────────────────────────────────────────────┤
│ PHASES                  │ PHASE 1 — PLATFORM DETECTION                                                   │
│                         │ ────────────────────────────────────────────────────────────────────────────── │
│ ▶ 1. Platform        ✓  │                                                                                │
│   2. Dependencies       │ Detected Environment                                                           │
│   3. Tool Detection     │                                                                                │
│   4. Workspace Mode     │   Operating System   : macOS 14.5                                              │
│   5. Company & User     │   Python Version     : 3.11.4                                                  │
│   6. Tokens & Validate  │   KiCad Config Dir   : ~/Library/Preferences/kicad/9.0                         │
│                         │   KiCad Version Hint : 9.0  (detected from config folder name)                 │
│ ─────────────────────── │                                                                                │
│ Status:                 │ ── Override KiCad Version (optional) ───────────────────────────────────────── │
│  ✓ Platform detected    │                                                                                │
│  … Dependencies         │   KiCad Config Version : [ 9.0           ▼ ]  [ Detect ]                       │
│  … Tools                │                                                                                │
│  … Workspace            │   Resolved Config Dir  : ~/Library/Preferences/kicad/9.0         ✓             │
│  … Company              │   Local Config File    : kicad_specgen_local.json  ( not yet created )         │
│  … Tokens               │   kicad_common.json    : ~/Library/Preferences/kicad/9.0/kicad_common.json ✓   │
│                         │                                                                                │
│                         │ ── Notes ───────────────────────────────────────────────────────────────────── │
│                         │   SpecGen stores its local configuration alongside kicad_common.json.          │
│                         │   If KiCad is not yet installed, enter the expected version manually.          │
│                         │                                                                                │
├─────────────────────────┴────────────────────────────────────────────────────────────────────────────────┤
│                                               [ < Back ]  [ Next > ]             [ Finish ]  [ Cancel ]  │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Controls:**

- `KiCad Config Version` dropdown — pre-populated from detected folder name; editable.
- `[ Detect ]` — Re-scan for KiCad config folder.

**Validation to pass before Next:**

- `KICAD_COMMON_DIR` resolves to an accessible path.
- Python version ≥ 3.10.

---

### 6.3 Phase 2 — Dependency Installation

Creates `{KSG_APP_DIR}/.venv` and installs required Python packages using pip.

Dependencies are installed in stages. Each stage is a superset of the previous.
The `dependency_stage` field in `kicad_specgen_local.json → setup` records the
highest completed stage. The `--stage STAGE` flag installs only up to that stage.

#### Dependency stages

| Stage | Packages | Needed for |
|---|---|---|
| `stage1` | `PySide6 >= 6.4`, `jsonschema >= 4.0` | GUI shell, config validation |
| `stage2` | `stage1` + `Jinja2 >= 3.0` | Template rendering (Variables tab) |
| `stage3` | same as `stage2` | No new packages — kicad-cli is an external binary |
| `stage4` | `stage3` + `WeasyPrint >= 60.0` | PDF assembly and report generation |

**Minimum PySide6 version is 6.4.** `QTextBrowser.setMarkdown()` was introduced
in Qt 6.4 (PySide6 6.4). Earlier versions will silently fall back to plain text,
breaking the HelpDialog.

#### Development and test dependencies

```text
pytest >= 7.0
pytest-qt >= 4.0        (for QApplication-based smoke tests)
```

These are installed in a separate dev install step and are not part of the
application `.venv` for end users.

#### `requirements.txt` structure

The repository shall include the following files:

```text
requirements/
  requirements-stage1.txt     PySide6>=6.4, jsonschema>=4.0
  requirements-stage2.txt     -r requirements-stage1.txt
                              Jinja2>=3.0
  requirements-stage3.txt     -r requirements-stage2.txt
                              # No new packages — kicad-cli is an external tool,
                              # not a Python package. Stage 3 reuses Stage 2 deps.
  requirements-stage4.txt     -r requirements-stage3.txt
                              WeasyPrint>=60.0
  requirements-dev.txt        -r requirements-stage1.txt
                              pytest>=7.0
                              pytest-qt>=4.0
```

`setup_utils.py` installs the correct requirements file based on the requested
dependency stage. `--full` installs `requirements-stage4.txt`. Each stage file
is a real file so `--stage stageN` always has a concrete file to reference.

#### CI and headless display

Smoke tests (`test_app_launch.py`, `test_configuration_tab.py`,
`test_logs_tab.py`) require a Qt display. In CI environments without a physical
display, set:

```text
QT_QPA_PLATFORM=offscreen
```

before running the test suite. On Linux CI, `Xvfb` is an alternative. Document
the CI setup requirement in the repository `README.md`. The smoke tests must
not be skipped silently — they should be gated by a `pytest` marker
(`@pytest.mark.smoke`) and the CI configuration must explicitly request them.

#### Acceptance criteria (Phase 2)

```text
✓ .venv created at {KSG_APP_DIR}/.venv
✓ .venv is not committed to the repository (.gitignore verified)
✓ pip install completes for the requested dependency stage
✓ Required packages are importable from within .venv
✓ Phase 2 skips .venv creation if already inside an active {KSG_APP_DIR}/.venv
✓ PySide6 version is >= 6.4 (checked by setup_utils after install)
✓ kicad_specgen_local.json → setup.dependency_stage updated on success
```

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    KiCad SpecGen Setup Wizard                                            │
├─────────────────────────┬────────────────────────────────────────────────────────────────────────────────┤
│ PHASES                  │ PHASE 2 — DEPENDENCY INSTALLATION                                              │
│                         │ ────────────────────────────────────────────────────────────────────────────── │
│   1. Platform       ✓   │                                                                                │
│ ▶ 2. Dependencies       │ Virtual Environment                                                            │
│   3. Tool Detection     │                                                                                │
│   4. Workspace Mode     │   .venv location : {KSG_APP_DIR}/.venv                                         │
│   5. Company & User     │   Status         : Not found — will be created                                 │
│   6. Tokens & Validate  │                                                                                │
│                         │   Note: The .venv is always installed inside the SpecGen application           │
│ ─────────────────────── │   folder ({KSG_APP_DIR}). To fully uninstall SpecGen, delete                   │
│ Status:                 │   {KSG_APP_DIR}. The .venv is excluded from the Git repository.                │
│  ✓ Platform detected    │                                                                                │
│  … Dependencies         │ ── Dependency Stage ────────────────────────────────────────────────────────── │
│  … Tools                │                                                                                │
│  … Workspace            │   ( ) Stage 1 — Core only                                                      │
│  … Company              │       PySide6, jsonschema, jinja2                                              │
│  … Tokens               │                                                                                │
│                         │   (•) Stage 2 — Core + Jobset                      ← recommended               │
│  … Workspace            │       + subprocess management                                                  │
│  … Company              │                                                                                │
│  … Tokens               │   ( ) Full — All stages                                                        │
│                         │       + PyMuPDF, pypdf, Pillow, markdown                                       │
│                         │                                                                                │
│                         │ ── Install ─────────────────────────────────────────────────────────────────── │
│                         │                                                                                │
│                         │   [ Install / Update Dependencies ]                                            │
│                         │                                                                                │
│                         │  ┌──────────────────────────────────────────────────────────────────────────┐  │
│                         │  │  Waiting for install...                                                  │  │
│                         │  └──────────────────────────────────────────────────────────────────────────┘  │
│                         │                                                                                │
│                         │   Status: Not installed                                                        │
│                         │                                                                                │
├─────────────────────────┴────────────────────────────────────────────────────────────────────────────────┤
│                                               [ < Back ]  [ Next > ]             [ Finish ]  [ Cancel ]  │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

**After clicking Install / Update Dependencies:**

```text
│  ┌────────────────────────────────────────────────────────────────────────────────┐  │
│  │  Creating .venv at {KSG_APP_DIR}/.venv ...                       ✓             │  │
│  │  Installing PySide6 ...                                          ✓             │  │
│  │  Installing jsonschema ...                                       ✓             │  │
│  │  Installing jinja2 ...                                           ✓             │  │
│  │  Verifying installation ...                                      ✓             │  │
│  └────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                      │
│   Status: ✓ Dependencies installed — Stage 2                                         │
```

**Note:** If the user is already running inside `{KSG_APP_DIR}/.venv`, skip `.venv`
creation and validate that the required packages are present.

**Validation to pass before Next:**

- Required packages for selected stage are importable.

---

### 6.4 Phase 3 — Tool Detection

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    KiCad SpecGen Setup Wizard                                            │
├─────────────────────────┬────────────────────────────────────────────────────────────────────────────────┤
│ PHASES                  │ PHASE 3 — TOOL DETECTION                                                       │
│                         │ ────────────────────────────────────────────────────────────────────────────── │
│   1. Platform       ✓   │                                                                                │
│   2. Dependencies   ✓   │ kicad-cli                                                                      │
│ ▶ 3. Tool Detection     │                                                                                │
│   4. Workspace Mode     │   Auto-detected Path : /Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli  │
│   5. Company & User     │   Detection Source   : macOS application bundle                                │
│   6. Tokens & Validate  │   KiCad Version      : Application 9.0.3                                       │
│                         │   Status             : ✓ Found                                                 │
│ ─────────────────────── │                                                                                │
│ Status:                 │   kicad-cli path : /Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli      │
│  ✓ Platform detected    │                                                 [ Browse... ]  [ Check ]       │
│  ✓ Dependencies         │                                                                                │
│  … Tools                │ ── Search Locations Checked ────────────────────────────────────────────────── │
│  … Workspace            │                                                                                │
│  … Company              │   macOS bundle  /Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli  ✓      │
│  … Tokens               │   Shell PATH    kicad-cli                                               ✗      │
│                         │   Custom        (not set)                                                      │
│                         │                                                                                │
│                         │   [ Re-detect ]                                                                │
│                         │                                                                                │
│                         │ ── KiCad kicad_common.json ──────────────────────────────────────────────────  │
│                         │                                                                                │
│                         │   kicad_common.json : ~/Library/Preferences/kicad/9.0/kicad_common.json  ✓     │
│                         │   Environment Vars  : 3 defined (read-only; SpecGen will not modify)           │
│                         │                                                                                │
├─────────────────────────┴────────────────────────────────────────────────────────────────────────────────┤
│                                               [ < Back ]  [ Next > ]             [ Finish ]  [ Cancel ]  │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Detection order for kicad-cli:**

```text
macOS:
  1. /Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
  2. ~/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
  3. Shell PATH: which kicad-cli

Linux:
  1. Shell PATH: which kicad-cli
  2. /usr/bin/kicad-cli
  3. /usr/local/bin/kicad-cli
  4. /snap/kicad/current/usr/bin/kicad-cli

Windows:
  1. %ProgramFiles%\KiCad\9.0\bin\kicad-cli.exe
  2. %ProgramFiles(x86)%\KiCad\9.0\bin\kicad-cli.exe
  3. Shell PATH: where kicad-cli
```

**[ Browse... ]** — Opens a file picker to manually locate kicad-cli.

**[ Check ]** — Runs `kicad-cli version` against the current path and shows the result.

**[ Re-detect ]** — Clears the current path and re-runs auto-detection.

**Validation to pass before Next:**

- `kicad-cli` path is set and the file exists.
- `kicad-cli version` runs without error.

**If kicad-cli is not found:** A warning is shown. The user may continue without
kicad-cli, but jobset execution will not be available. The path can be set later
via `Edit → Configure kicad-cli...` or the Configure tab.

---

### 6.5 Phase 4 — Workspace Mode Selection

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    KiCad SpecGen Setup Wizard                                            │
├─────────────────────────┬────────────────────────────────────────────────────────────────────────────────┤
│ PHASES                  │ PHASE 4 — WORKSPACE MODE                                                       │
│                         │ ────────────────────────────────────────────────────────────────────────────── │
│   1. Platform       ✓   │                                                                                │
│   2. Dependencies   ✓   │ How will you use KiCad SpecGen?                                                │
│   3. Tool Detection ✓   │                                                                                │
│ ▶ 4. Workspace Mode     │                                                                                │
│   5. Company & User     │   (•) Shared / Repository Workspace                                            │
│   6. Tokens & Validate  │                                                                                │
│                         │       Your company, team, or personal shared SpecGen data lives in a           │
│ ─────────────────────── │       folder or Git repository shared across projects.                         │
│ Status:                 │                                                                                │
│  ✓ Platform detected    │       Typical users: professional engineer, team lead, consultant,             │
│  ✓ Dependencies         │       freelancer with multiple clients, solo user with organized workspace.    │
│  ✓ Tools                │                                                                                │
│  … Workspace            │                                                                                │
│  … Company              │   ( ) Standalone / Local Workspace                                             │
│  … Tokens               │                                                                                │
│                         │       All SpecGen data lives locally on this machine.                          │
│                         │       No shared repository is required.                                        │
│                         │                                                                                │
│                         │       Typical users: hobby user, student, one-off project user.                │
│                         │                                                                                │
│                         │ ── Selected Mode ───────────────────────────────────────────────────────────── │
│                         │                                                                                │
│                         │   Mode        : Shared / Repository Workspace                                  │
│                         │   Description : Company data stored in a shared folder or Git repo.            │
│                         │                                                                                │
│                         │   Note: This choice sets the default project workspace mode.                   │
│                         │   Individual projects may use either mode regardless of this choice.           │
│                         │                                                                                │
├─────────────────────────┴────────────────────────────────────────────────────────────────────────────────┤
│                                               [ < Back ]  [ Next > ]             [ Finish ]  [ Cancel ]  │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

**This choice determines Phase 5 behavior:**

- **Shared / Repository** → Phase 5 prompts for existing `KSG_COMPANY_DIR` or
  creates a new one. Company, client, and user fields are all collected.

- **Standalone / Local** → Phase 5 creates a minimal local `SpecGen/` folder and
  prompts only for essential user identity fields. A minimal `kicad_specgen_company.json`
  and `kicad_specgen_users.json` are generated automatically.

---

### 6.6 Phase 5A — Company and User Configuration (Shared/Repo Mode)

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    KiCad SpecGen Setup Wizard                                            │
├─────────────────────────┬────────────────────────────────────────────────────────────────────────────────┤
│ PHASES                  │ PHASE 5 — COMPANY AND USER CONFIGURATION  [Shared / Repo Mode]                 │
│                         │ ────────────────────────────────────────────────────────────────────────────── │
│   1. Platform       ✓   │                                                                                │
│   2. Dependencies   ✓   │ ── Company / Shared Workspace Root ─────────────────────────────────────────── │
│   3. Tool Detection ✓   │                                                                                │
│   4. Workspace Mode ✓   │   KSG_COMPANY_DIR : /Users/john/Engineering/CompanyRepo         [ Browse... ]  │
│ ▶ 5. Company & User     │                     ✓ Folder found                                             │
│   6. Tokens & Validate  │                     ✓ SpecGen/ subfolder found                                 │
│                         │                     ✓ kicad_specgen_company.json found — loading...            │
│ ─────────────────────── │                                                                                │
│ Status:                 │ ── Company Information ─────────────────────────────────────────────────────── │
│  ✓ Platform detected    │                                                                                │
│  ✓ Dependencies         │   Company ID   : [ AE                           ]                              │
│  ✓ Tools                │   Company Name : [ Advanced Engineering          ]                             │
│  ✓ Workspace            │   Description  : [ Engineering consulting and... ]                             │
│  … Company              │                                                                                │
│  … Tokens               │ ── Clients (optional) ──────────────────────────────────────────────────────── │
│                         │                                                                                │
│                         │   Clients defined in company file:                                             │
│                         │    • Medical Devices Inc  (medical_devices)                                    │
│                         │    • Aerospace Systems Ltd  (aerospace_systems)                                │
│                         │                                                                                │
│                         │   [ Edit Clients and Teams... ]   (opens sub-dialog)                           │
│                         │                                                                                │
│                         │ ── Your User Profile ───────────────────────────────────────────────────────── │
│                         │                                                                                │
│                         │   Worker ID      : [ 12345  ]  (must be unique)                                │
│                         │   Display Name   : [ John Smith                  ]                             │
│                         │   Email          : [ john.smith@advancedeng.com  ]                             │
│                         │   Job Title      : [ Senior Electrical Engineer  ]                             │
│                         │   Worker Type    : [ Employee          ▼ ]                                     │
│                         │   Is Admin       : [x] Can modify shared SpecGen configuration                 │
│                         │                                                                                │
│                         │   Associated Clients : [x] Medical Devices  [ ] Aerospace  [ ] (others)        │
│                         │                                                                                │
├─────────────────────────┴────────────────────────────────────────────────────────────────────────────────┤
│                                               [ < Back ]  [ Next > ]             [ Finish ]  [ Cancel ]  │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Behavior when `KSG_COMPANY_DIR` is browsed to an existing location:**

- If `SpecGen/kicad_specgen_company.json` exists, load it and populate fields.
- If `SpecGen/kicad_specgen_users.json` exists, search for matching Worker ID and
  pre-populate user fields.
- If neither file exists, offer to create them with the entered data.

**Behavior when `KSG_COMPANY_DIR` points to a new (empty) location:**

```text
│   KSG_COMPANY_DIR : /Users/john/NewCompanyFolder                [ Browse... ]  │
│                     ✓ Folder found                                             │
│                     ✗ SpecGen/ subfolder not found                             │
│                                                                                │
│   [ Create SpecGen/ Folder Structure Here ]                                    │
```

**[ Edit Clients and Teams... ]** opens the Clients and Teams sub-dialog (§6.6.1).

---

#### 6.6.1 Clients and Teams Sub-Dialog

```text
┌────────────────────────────────────────────────────────────────────┐
│              Edit Clients and Teams                                │
├──────────────────────────┬─────────────────────────────────────────┤
│ CLIENTS                  │ SELECTED CLIENT                         │
│                          │                                         │
│  ▶ Medical Devices Inc   │  Client ID   : medical_devices          │
│    Aerospace Systems     │  Client Name : Medical Devices Inc      │
│    + Add Client          │  Root Path   : {KSG_COMPANY_DIR}/       │
│                          │               Clients/MedicalDevices    │
│                          │                                         │
│                          │  ── Teams / Groups ──────────────────── │
│                          │                                         │
│                          │   ▶ Hardware Team                       │
│                          │     Manufacturing Engineering           │
│                          │     + Add Team                          │
│                          │                                         │
│                          │  ── Selected Team ───────────────────── │
│                          │                                         │
│                          │   Team ID   : hardware                  │
│                          │   Team Name : Hardware Team             │
│                          │   Docs Path : {KSG_COMPANY_DIR}/        │
│                          │              Clients/MedicalDevices/    │
│                          │              hardware/docs              │
│                          │                                         │
│                          │  [ Add Team ] [ Remove Team ]           │
├──────────────────────────┴─────────────────────────────────────────┤
│  [ Add Client ] [ Remove Client ]         [ OK ] [ Cancel ]        │
└────────────────────────────────────────────────────────────────────┘
```

---

### 6.7 Phase 5B — Standalone User Configuration

When **Standalone / Local Workspace** was selected in Phase 4. The company name
defaults to "personal" and is editable.

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    KiCad SpecGen Setup Wizard                                            │
├─────────────────────────┬────────────────────────────────────────────────────────────────────────────────┤
│ PHASES                  │ PHASE 5 — USER CONFIGURATION  [Standalone / Local Mode]                        │
│                         │ ────────────────────────────────────────────────────────────────────────────── │
│   1. Platform       ✓   │                                                                                │
│   2. Dependencies   ✓   │ ── Local SpecGen Workspace Folder ──────────────────────────────────────────── │
│   3. Tool Detection ✓   │                                                                                │
│   4. Workspace Mode ✓   │   SpecGen will store your shared resources in a local folder.                  │
│ ▶ 5. Company & User     │                                                                                │
│   6. Tokens & Validate  │   KSG_COMPANY_DIR : ~/Library/Preferences/kicad/9.0/SpecGenData                │
│                         │                     (default — recommended for standalone)                     │
│ ─────────────────────── │                                               [ Change... ]                    │
│ Status:                 │                                                                                │
│  ✓ Platform detected    │ ── Workspace Identity ──────────────────────────────────────────────────────── │
│  ✓ Dependencies         │                                                                                │
│  ✓ Tools                │   Company Name : [ personal                          ]  (default; editable)    │
│  ✓ Workspace            │   Company ID   : [ personal                          ]  (auto; editable)       │
│  … Company              │                                                                                │
│  … Tokens               │ ── Your Identity ───────────────────────────────────────────────────────────── │
│                         │                                                                                │
│                         │   Display Name : [ My Name                           ]                         │
│                         │   Email        : [ (optional)                        ]                         │
│                         │   Worker ID    : [ local_user            ]  (auto-generated; can customize)    │
│                         │ ── What SpecGen Will Create ────────────────────────────────────────────────── │
│                         │                                                                                │
│                         │   ~/Library/Preferences/kicad/9.0/SpecGenData/                                 │
│                         │   └─ SpecGen/                                                                  │
│                         │      ├─ kicad_specgen_company.json  (minimal standalone config)                │
│                         │      ├─ kicad_specgen_users.json    (your user profile)                        │
│                         │      ├─ templates/                  (default templates copied from app)        │
│                         │      ├─ assets/                     (default assets copied from app)           │
│                         │      └─ Users/                                                                 │
│                         │         └─ local_user/                                                         │
│                         │            └─ common/                                                          │
│                         │                                                                                │
│                         │   Note: Clients and teams are not required in standalone mode.                 │
│                         │   You can add them later via the Configure tab.                            │
│                         │                                                                                │
├─────────────────────────┴────────────────────────────────────────────────────────────────────────────────┤
│                                               [ < Back ]  [ Next > ]             [ Finish ]  [ Cancel ]  │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Minimum standalone `kicad_specgen_company.json` generated:**

```json
{
  "schema_version": 1,
  "company": {
    "company_id": "personal",
    "name": "personal",
    "description": "Standalone SpecGen workspace"
  },
  "environments": {
    "standalone": {
      "type": "sandbox",
      "description": "Default standalone environment"
    }
  }
}
```

The company name and ID default to "personal" but may be changed to any value the
user chooses. The startup sequence always opens this file regardless of mode.

---

### 6.8 Phase 6 — Local Tokens and Validation

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    KiCad SpecGen Setup Wizard                                            │
├─────────────────────────┬────────────────────────────────────────────────────────────────────────────────┤
│ PHASES                  │ PHASE 6 — LOCAL TOKENS AND VALIDATION                                          │
│                         │ ────────────────────────────────────────────────────────────────────────────── │
│   1. Platform       ✓   │                                                                                │
│   2. Dependencies   ✓   │ ── Required Local Tokens ───────────────────────────────────────────────────── │
│   3. Tool Detection ✓   │                                                                                │
│   4. Workspace Mode ✓   │  Token                  Value                                      Status      │
│   5. Company & User ✓   │  ─────────────────────  ─────────────────────────────────────────  ──────────  │
│ ▶ 6. Tokens & Validate  │  KSG_APP_DIR            /Users/john/GitHub/kicad-specgen            ✓          │
│                         │  KSG_SYSTEM_CONFIG_DIR  ~/Library/Preferences/kicad/9.0             ✓          │
│ ─────────────────────── │  KSG_COMPANY_DIR        /Users/john/Engineering/CompanyRepo         ✓          │
│ Status:                 │  KSG_USER_SPECGEN_DIR   /Users/john/Engineering/CompanyRepo/        ✓          │
│  ✓ Platform detected    │                         SpecGen/Users/12345                                    │
│  ✓ Dependencies         │  KSG_USER_COMMON_DIR    /Users/john/Engineering/CompanyRepo/        ✓          │
│  ✓ Tools                │                         SpecGen/Users/12345/common                             │
│  ✓ Workspace            │                                                                                │
│  ✓ Company              │   [ Add Optional Token ]  [ Remove Selected ]  [ Browse... ]                   │
│  … Tokens               │                                                                                │
│                         │ ── Validation ──────────────────────────────────────────────────────────────── │
│                         │                                                                                │
│                         │   [ Run Validation ]                                                           │
│                         │                                                                                │
│                         │   ✓ kicad_specgen_local.json location is writable                              │
│                         │   ✓ All required KSG_* tokens are defined                                      │
│                         │   ✓ All token paths are absolute                                               │
│                         │   ✓ KSG_COMPANY_DIR exists                                                     │
│                         │   ✓ SpecGen/ folder exists under KSG_COMPANY_DIR                               │
│                         │   ✓ kicad_specgen_company.json is valid                                        │
│                         │   ✓ kicad_specgen_users.json is valid                                          │
│                         │   ✓ Active user found: John Smith (12345)                                      │
│                         │   ✓ kicad-cli found and working: KiCad 9.0.3                                   │
│                         │                                                                                │
│                         │ ── Ready to Save ───────────────────────────────────────────────────────────── │
│                         │                                                                                │
│                         │   kicad_specgen_local.json will be written to:                                 │
│                         │   ~/Library/Preferences/kicad/9.0/kicad_specgen_local.json                     │
│                         │                                                                                │
├─────────────────────────┴────────────────────────────────────────────────────────────────────────────────┤
│                                               [ < Back ]  [ Next > ]             [ Finish ]  [ Cancel ]  │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

**[ Finish ]** is enabled only when:

- All required tokens are present.
- All token values are absolute paths.
- No protected derived tokens appear in the token list.
- Validation passes with no errors (warnings are acceptable).

**After Finish:**

- Write `kicad_specgen_local.json` with `setup.setup_complete = true`.
- Write `kicad_specgen_company.json` if newly created or modified.
- Write `kicad_specgen_users.json` if newly created or modified.
- Show a "Setup Complete" confirmation and close the wizard.
- The main application proceeds with normal startup.

---

### 6.9 Setup Complete Confirmation

```text
┌──────────────────────────────────────────────────────────────────┐
│                    Setup Complete                                │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ✓  KiCad SpecGen has been configured successfully.              │
│                                                                  │
│  Configuration saved to:                                         │
│  ~/Library/Preferences/kicad/9.0/kicad_specgen_local.json        │
│                                                                  │
│  Active User      : John Smith (12345)                           │
│  Workspace Mode   : Shared / Repository                          │
│  Company          : Advanced Engineering                         │
│  kicad-cli        : KiCad 9.0.3  ✓                               │
│                                                                  │
│  You can review or update these settings at any time using       │
│  the Configure tab in the main application.                  │
│                                                                  │
│                   [ Open KiCad SpecGen ]                         │
└──────────────────────────────────────────────────────────────────┘
```

---

## 7. Headless / Text Mode Setup

When `--headless` is specified or no display is available, setup runs in text mode.

The same six phases execute sequentially. Each phase prints its results to stdout.
Required inputs are collected via stdin prompts.

```text
======================================================
  KiCad SpecGen Setup — Phase 1: Platform Detection
======================================================
  Operating System   : macOS 14.5
  Python Version     : 3.11.4
  KiCad Config Dir   : ~/Library/Preferences/kicad/9.0
  kicad_common.json  : found

  KiCad config version [9.0]: <enter>

======================================================
  KiCad SpecGen Setup — Phase 2: Dependencies
======================================================
  .venv location : {KSG_APP_DIR}/.venv
  Installing Stage 2 dependencies...
  [✓] .venv created at {KSG_APP_DIR}/.venv
  [✓] PySide6
  [✓] jsonschema
  [✓] jinja2
  Dependencies installed.

...and so on for each phase.

======================================================
  KiCad SpecGen Setup — Complete
======================================================
  Configuration written:
  ~/Library/Preferences/kicad/9.0/kicad_specgen_local.json

  Run 'python main.py' to start KiCad SpecGen.
```

---

## 8. Re-Run Behavior

When `setup.py` is run on a machine where setup has already completed:

```text
┌──────────────────────────────────────────────────────────────────┐
│  KiCad SpecGen Setup                                             │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Setup has already been run on this machine.                     │
│                                                                  │
│  Last run : 2026-06-03  Platform : macOS                         │
│  Active User : John Smith (12345)                                │
│                                                                  │
│  What would you like to do?                                      │
│                                                                  │
│   (•) Update dependencies only                                   │
│   ( ) Reconfigure workspace and tokens                           │
│   ( ) Full reconfigure (all phases)                              │
│                                                                  │
│                    [ Continue ]  [ Cancel ]                      │
└──────────────────────────────────────────────────────────────────┘
```

Pre-populate all fields from the existing configuration. The user modifies only
what needs to change.

---

## 9. Configure Tab

The Configure tab is specified in full — with all five subtab wireframes,
scope boundaries, file write rules, and acceptance criteria — in
**`SpecGen_Tab_Configure.md`**.

This section summarises only the relationship between the setup wizard and
the Configure tab.

### 9.1 Design Rationale

The Configure tab is a permanent sidebar page that provides full post-setup
configuration management without re-running `setup.py`. A developer opening
the application on a machine where setup has already completed should never
need to run `setup.py` again for routine changes.

`setup.py` is the correct path for:

```text
  — Fresh machine installation (Phase 1–2: .venv and dependencies)
  — Platform-specific tool detection on a new OS
  — Scripted / CI setup
```

The Configure tab is the correct path for:

```text
  — Changing KSG_* tokens
  — Switching active environment or active user
  — Updating user info
  — Editing company, client, and team data
  — Setting UI preferences (theme)
```

### 9.2 Sidebar Placement

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

The Configure tab is always enabled, even when no project is open and even
when setup is incomplete.

### 9.3 Subtabs

Five subtabs: Local Machine, Company & User, Environments, Preferences,
Validation. See `SpecGen_Tab_Configure.md` for full wireframes and behavior.

---

## 12. Menu Bar Reference

The authoritative menu bar specification is `SpecGen_GUI_Menus.md`.

Key decisions relevant to the setup process and Configure tab:

- `Edit → Local Tokens...` edits `kicad_specgen_local.json → tokens` only.
- `Edit → Configure` is a page switch to the Configure tab.
- `Configure` is not in the View menu.
- `Configure Environments...` is retired. It is replaced by `Local Tokens...`
  for token editing and the Configure tab for full environment management.

---

## 13. Module Impact

### New and Modified Modules

| Module | Change |
|---|---|
| `setup/setup.py` | Entry point with phase orchestration and GUI/headless dispatch |
| `setup/setup_macos.py` | macOS platform detection, kicad-cli search |
| `setup/setup_linux.py` | Linux platform detection, kicad-cli search |
| `setup/setup_windows.py` | Windows platform detection, kicad-cli search |
| `setup/setup_utils.py` | Shared: dependency install, venv creation, progress reporting |
| `ui/setup_wizard.py` | **New** — SetupWizardDialog (6-phase wizard with phase navigator) |
| `ui/tabs/configuration_tab.py` | **New** — ConfigurationTab (4 subtabs) |
| `ui/dialogs/clients_teams_dialog.py` | **New** — EditClientsTeamsDialog |
| `ui/dialogs/add_user_dialog.py` | **New** — AddEditUserDialog |
| `ui/dialogs/local_tokens_dialog.py` | **Renamed from** `configure_env_dialog.py`; scoped to tokens only |
| `services/config_service.py` | Add: `save_company_config`, `save_users_config`, `run_setup_validation` |
| `services/validation_service.py` | Add: `run_config_validation` (configuration-only validation separate from project validation) |
| `core/app_state.py` | Add: `setup_complete`, `venv_path`, `config_validation_result` fields |

---

## 14. Acceptance Criteria for Setup and Configuration Tab

### Setup Wizard

```text
✓ Setup Required banner appears on first run (no kicad_specgen_local.json).
✓ Setup Required banner appears when setup_complete = false.
✓ [ Run Setup Now ] opens the wizard.
✓ [ Defer — Limited Mode ] allows app to open; Configure tab is accessible.
✓ Phase navigator shows completed phases with ✓ and allows clicking back.
✓ Phase 1 detects OS and KiCad config dir correctly on macOS, Linux, Windows.
✓ Phase 2 creates .venv at {KSG_APP_DIR}/.venv and installs packages correctly.
✓ Phase 2 skips .venv creation if already inside an active {KSG_APP_DIR}/.venv.
✓ Phase 3 detects kicad-cli from the correct platform-specific ordered locations.
✓ Phase 3 allows manual Browse and Check of kicad-cli path.
✓ Phase 4 presents both workspace modes with clear descriptions.
✓ Phase 5A loads existing kicad_specgen_company.json when KSG_COMPANY_DIR is browsed.
✓ Phase 5A shows clients and teams loaded from company file.
✓ Phase 5B generates minimal standalone company file with company name "personal".
✓ Phase 5B company name is editable before saving.
✓ Phase 6 shows all five required tokens pre-populated.
✓ Phase 6 validates and shows per-check results.
✓ Finish button is disabled until Phase 6 validation passes.
✓ Finish writes kicad_specgen_local.json with setup_complete = true.
✓ Setup complete dialog shows summary and [ Open KiCad SpecGen ] button.
✓ Headless mode runs all six phases without GUI.
✓ --reconfigure pre-populates from existing configuration.
✓ --validate-only reports results without writing any files.
✓ .venv is not committed to the Git repository (.gitignore verified).
```

### Configuration Tab

```text
✓ Configure tab is always accessible in sidebar.
✓ Configure tab is accessible even when setup is incomplete.
✓ Local Machine subtab shows kicad_specgen_local.json values.
✓ .venv path {KSG_APP_DIR}/.venv is shown and status is indicated in Local Machine subtab.
✓ Token table shows all KSG_* tokens with status indicators.
✓ Add Token validates KSG_* naming rule before saving.
✓ Remove Token rejects removal of required tokens.
✓ Browse sets absolute path for selected token.
✓ Save Local Changes writes kicad_specgen_local.json after validation.
✓ Company & User subtab shows tree of company / clients / teams.
✓ Selecting a client shows its editable fields.
✓ User table shows all users with active status.
✓ Add User / Edit User / Deactivate User work correctly.
✓ Save Company/User Changes writes correct files.
✓ Environments subtab lists all environments from company file.
✓ Active environment dropdown shows and saves to kicad_specgen_local.json.
✓ Active user dropdown saves to kicad_specgen_local.json.
✓ Token priority note (USER → CLIENT → COMPANY → DEFAULT) is visible in Environments subtab.
✓ Validation subtab shows per-check results.
✓ Run Validation refreshes results without writing any files.
✓ [ Re-run Setup Wizard ] opens wizard in reconfigure mode, pre-populated.
✓ Status bar reflects current configuration state.
```

---

## 15. Pre-Coding Questions — Full Resolution

All ten questions are resolved in this section.

| # | Question | Resolution |
|---|---|---|
| Q1 | **Setup process:** Main app setup wizard inline, or separate `setup.py`? | **Both.** `setup.py` is the canonical entry point and handles all six phases, including `.venv` creation at `{KSG_APP_DIR}/.venv` and dependency installation. The main application detects missing or incomplete setup (`setup_complete = false`) and launches the same setup wizard GUI inline, beginning at Phase 3 (tool detection), since Phases 1–2 require `setup.py` to have already run for venv and dependency work. |
| Q2 | **Standalone mode — does `kicad_specgen_company.json` still exist?** | **Yes, always.** Standalone mode generates a minimal local `kicad_specgen_company.json` in `{KSG_COMPANY_DIR}/SpecGen/`. The company name defaults to "personal" and is editable. The startup sequence (step 5) always opens this file. There is no mode where it is absent. |
| Q3 | **Configure Environments dialog scope — Option A or B?** | **Option A** was a single dialog with two tabs (local tokens on Tab 1, environment definitions on Tab 2). **Option B** separates them into two distinct access paths. **Option B is chosen:** `Edit → Local Tokens...` is scoped strictly to `kicad_specgen_local.json` token editing. Full environment management (add/edit/remove environment definitions from `kicad_specgen_company.json`) belongs in the Configure tab Environments subtab. This keeps each file's ownership clear and prevents a single dialog from writing to two files with different portability rules. |
| Q4 | **New Project dialog — environment selection vs. inline creation?** | **Selection only.** The New Project dialog selects from existing environments in `kicad_specgen_company.json.environments`. Environment creation belongs in the Configure tab Environments subtab. Setup builds the database of available environments; each project picks from that database. The project makes the final selection, applying token priority order USER → CLIENT → COMPANY → DEFAULT at runtime. |
| Q5 | **`JOBSET_OUTPUT_DIR` derivation — `outputs[0]` or validate all?** | **Validate all, use first as representative.** When parsing `.kicad_jobset`, SpecGen checks that all output entries share the same root path. If they do not, a warning is shown in the Jobset Dashboard. The first output's `settings.output_path` is used as `JOBSET_OUTPUT_DIR`. This is handled at project open time by `kicad_jobset_parser.py`, not during setup. |
| Q6 | **Multiple `.kicad_pro` files in `KICAD_PROJECT_DIR`?** | **Auto-select by name, then prompt if ambiguous.** SpecGen first looks for a `.kicad_pro` whose base name matches the `.kicad_specgen` project name. If exactly one match is found, it is used silently. If no match or multiple matches exist, a selection prompt is shown. If none are found, a warning is shown and the user may browse. |
| Q7 | **`KSG_PROJECT_SPECGEN_DIR` vs. `SPECGEN_PROJECT_DIR`?** | **Keep `KSG_PROJECT_SPECGEN_DIR`.** The `KSG_` prefix correctly identifies this as a SpecGen-owned token and maintains namespace consistency with all other SpecGen tokens. Renaming would drop the ownership prefix and create an inconsistency. No change required. |
| Q8 | **Dirty state triggers for `.kicad_specgen`?** | **Any user-initiated edit to any section sets the dirty flag.** Sections that trigger dirty: `workspace`, `project`, `files`, `variables`, `jobset` (destinations, active jobset, stop_on_error), `report`, `fabrication`. The `ui` section (panel sizes, last active tab) does not trigger the dirty flag and is saved silently on close. The dirty flag is cleared on successful Save or Save As. |
| Q9 | **Jobset destination reconciliation when `.kicad_jobset` changes?** | **Merge with warnings.** When a new `.kicad_jobset` is selected: (a) destination IDs present in both old and new jobset are preserved with existing overrides; (b) new destination IDs are added with empty default overrides; (c) stale destination IDs (in `.kicad_specgen` but absent from the new jobset) are flagged `[stale]` in the Jobset Setup & Run table but are not silently deleted — the user removes them manually. Handled in Stage 2 by `jobset_service.py`. |
| Q10 | **Setup entry point?** | **`python setup.py`** run from `{KSG_APP_DIR}`. This is the canonical invocation documented in `getting_started.md` and in the main application's first-run prompt. |

---

*End of SpecGen Setup Process Specification.*
