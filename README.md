# KiCad SpecGen

KiCad SpecGen generates engineering specification documents from KiCad design
files, jobset outputs, and Jinja2 templates. It produces professional PDF
reports and fabrication packages from a reproducible, version-controlled
project configuration.

## Features

- Token-based portable project files — no hard-coded absolute paths
- Per-machine local configuration with shared company and user profiles
- kicad-cli integration for jobset execution (Stage 3)
- Jinja2 template rendering for specification documents (Stage 2+)
- PDF assembly and fabrication ZIP packaging (Stage 4)
- Six UI themes including engineering-focused dark themes

## Requirements

- Python 3.11 or later
- KiCad 9.0 or later (must have been run at least once to create its config directory)
- Git (recommended, for shared company configuration)

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-org/kicad-specgen.git
cd kicad-specgen
```

### 2. Run setup

Setup detects your platform, creates a `.venv` (or reuses `$SHARED_VENV` when set), installs Python dependencies,
locates `kicad-cli`, and writes the local configuration file to your KiCad
user config directory.

By default setup opens a **graphical window**. Click **Run Setup** to begin,
then **Launch Application** when it completes.

```bash
python setup/setup.py
```

To run setup in the terminal without the GUI:

```bash
python setup/setup.py --headless
```

To install only Stage 1 dependencies (GUI shell and config only):

```bash
python setup/setup.py --stage stage1
```

To install full dependencies through Stage 4 (includes Jinja2 and WeasyPrint):

```bash
python setup/setup.py --stage stage4
```

To run headless setup and launch the app immediately when done:

```bash
python setup/setup.py --headless --launch
```

Setup writes `kicad_specgen_local.json` to your KiCad user config directory:

| Platform | Location |
|---|---|
| macOS   | `~/Library/Preferences/kicad/<version>/kicad_specgen_local.json` |
| Linux   | `~/.config/kicad/<version>/kicad_specgen_local.json` |
| Windows | `%APPDATA%\kicad\<version>\kicad_specgen_local.json` |

Setup auto-detects `KSG_APP_DIR`, `KSG_SYSTEM_CONFIG_DIR`, and
`KSG_COMPANY_DIR`. The four writable-space tokens
(`KSG_COMPANY_SPECGEN_DIR`, `KSG_COMPANY_COMMON_DIR`, `KSG_USER_SPECGEN_DIR`,
`KSG_USER_COMMON_DIR`) are left **empty** for you to configure in the
Configure tab — they must point to folders you can write to, never inside the
read-only application directory.

### 3. Configure kicad-cli (if not auto-detected)

If setup could not find `kicad-cli` automatically, open the application and
use **Edit → Configure kicad-cli...** to set the path manually.

### 4. Activate the virtual environment

```bash
# macOS / Linux
source "${SHARED_VENV:-.venv}/bin/activate"

# Windows
.venv\Scripts\activate
```

## Running the Application

```bash
python app.py
```

On first launch the application opens directly to the **Configure** tab.
Use the **Validation** subtab to verify your configuration before opening
a project.

## Configuration

### Local machine tokens

Open **Edit → Local Tokens...** to view and edit your `KSG_*` token
definitions. These are absolute paths specific to this machine.

| Token | Purpose |
|---|---|
| `KSG_APP_DIR` | Root of this SpecGen repository |
| `KSG_SYSTEM_CONFIG_DIR` | KiCad user config directory |
| `KSG_COMPANY_DIR` | Root of your company/personal shared folder |
| `KSG_USER_SPECGEN_DIR` | Your personal SpecGen resources |
| `KSG_USER_COMMON_DIR` | Your shared templates and assets |

### Company and user configuration

Shared configuration lives in your `KSG_COMPANY_DIR`:

```
{KSG_COMPANY_DIR}/SpecGen/kicad_specgen_company.json
{KSG_COMPANY_DIR}/SpecGen/kicad_specgen_users.json
```

These files are portable (no absolute paths) and are safe to commit to a
shared repository.

## Running Tests

Install development dependencies first:

```bash
pip install -r requirements/requirements-dev.txt
```

### Unit tests (no display required)

```bash
pytest tests/unit/ tests/regression/ -v
```

### Integration tests

```bash
pytest tests/integration/ -v
```

### Smoke tests (require a display or `QT_QPA_PLATFORM=offscreen`)

```bash
# Linux CI / headless
QT_QPA_PLATFORM=offscreen pytest tests/smoke/ -v -m smoke

# macOS / Windows (display available)
pytest tests/smoke/ -v -m smoke
```

### All tests

```bash
QT_QPA_PLATFORM=offscreen pytest -v
```

## Uninstall

Open the uninstall dialog from the setup GUI (**Uninstall...** button) or
directly:

```bash
python setup/setup.py --uninstall
```

Two options are offered, each requiring confirmation:

- **Remove local configuration only** — deletes `kicad_specgen_local.json`.
  The application directory is kept.
- **Full uninstall** — deletes `kicad_specgen_local.json` and the entire
  `KSG_APP_DIR` application directory.

Headless equivalents (each prompts for typed confirmation):

```bash
python setup/setup.py --headless --uninstall-local
python setup/setup.py --headless --uninstall-full
```

Your KiCad project files are never affected — only SpecGen application data
is removed.

## Project Structure

```
kicad_specgen/
├── app.py                  # Application entry point
├── setup/
│   ├── setup.py            # Headless setup script
│   ├── setup_macos.py      # macOS kicad-cli detection
│   ├── setup_linux.py      # Linux kicad-cli detection
│   ├── setup_windows.py    # Windows kicad-cli detection
│   ├── setup_gui.py        # GUI setup window and uninstall dialog
│   └── setup_utils.py      # Shared setup utilities, uninstall helpers
├── core/                   # Pure Python — no PySide6, no subprocess
│   ├── platform_paths.py   # OS detection and KICAD_COMMON_DIR resolution
│   ├── file_ops.py         # Atomic JSON write, backup, directory utilities
│   ├── migrations.py       # Schema version migration
│   ├── app_state.py        # Observable in-memory application state
│   ├── specgen_local_config.py   # kicad_specgen_local.json loader/saver
│   ├── specgen_company_config.py # kicad_specgen_company.json loader/saver
│   ├── specgen_user_config.py    # kicad_specgen_users.json loader/saver
│   ├── kicad_env.py        # Read kicad_common.json environment vars
│   ├── token_resolver.py   # Build effective token table, resolve references
│   ├── validators.py       # Config validation, ValidationResult/Report types
│   └── logging_utils.py    # Structured logging with Qt bridge (QtLogHandler)
├── services/
│   ├── config_service.py   # All config file writes, state refresh, signal emit
│   └── validation_service.py # Aggregate validation, emit validation_complete
├── ui/
│   ├── main_window.py      # QMainWindow, sidebar, menus, status bar
│   ├── actions.py          # QAction definitions and keyboard shortcuts
│   ├── theme.py            # Theme application (6 themes)
│   ├── tabs/               # Workspace tabs
│   │   ├── configuration_tab.py  # 5-subtab Configure tab (Stage 1 complete)
│   │   ├── logs_tab.py           # Session log viewer
│   │   ├── project_tab.py        # Placeholder (Stage 2)
│   │   ├── variables_tab.py      # Placeholder (Stage 2)
│   │   ├── jobset_tab.py         # Placeholder (Stage 3)
│   │   └── report_tab.py         # Placeholder (Stage 4)
│   ├── dialogs/            # Modal dialogs
│   │   ├── about_dialog.py
│   │   ├── help_dialog.py
│   │   ├── kicad_cli_dialog.py
│   │   ├── local_tokens_dialog.py
│   │   ├── add_user_dialog.py
│   │   ├── clients_teams_dialog.py
│   │   ├── new_project_dialog.py  # Stub (Stage 2)
│   │   └── missing_tokens_dialog.py # Stub (Stage 2)
│   └── widgets/
│       ├── token_table.py      # Editable/read-only KSG_* token table
│       ├── validation_panel.py # ✓ ⚠ ✗ validation result display
│       ├── log_viewer.py       # Structured log record viewer with filters
│       └── path_field.py       # Text field with Browse button
├── help/                   # In-app Markdown help files
├── specification/          # Authoritative design documents (source of truth)
├── requirements/           # Staged dependency files
│   ├── requirements-stage1.txt  # PySide6, jsonschema
│   ├── requirements-stage2.txt  # + Jinja2
│   ├── requirements-stage3.txt  # (no new packages)
│   ├── requirements-stage4.txt  # + WeasyPrint
│   └── requirements-dev.txt     # + pytest, pytest-qt
├── tests/
│   ├── unit/               # Pure Python unit tests (no display)
│   ├── integration/        # Service-level integration tests
│   ├── smoke/              # GUI smoke tests (require display)
│   ├── regression/         # Terminology drift detection
│   └── fixtures/           # JSON test fixtures
└── pytest.ini
```

## Implementation Stages

| Stage | Scope | Status |
|---|---|---|
| 1 | Setup, config management, Configure tab, Logs tab | ✅ This release |
| 2 | Project and Variables tabs, kicad_pro parsing | Planned |
| 3 | Jobset execution, kicad-cli subprocess | Planned |
| 4 | Report rendering, PDF assembly, FAB ZIP | Planned |

## Specifications

The authoritative design documents live in the [`specification/`](specification/)
folder. They are the single source of truth for the application's design, data
formats, terminology, and behavior. See
[`specification/README.md`](specification/README.md) for the full index.

**Governance rule:** every code change must determine whether it affects any
authoritative document, and if so, update that document in the same change.
When code and a document disagree, the document wins. A change is not complete
until the relevant specifications reflect it.

## Contributing

1. Fork the repository and create a feature branch.
2. Run the full test suite before submitting a pull request.
3. Follow the layer boundary rules — UI never imports core directly,
   all writes go through services.
4. Keep `kicad_specgen_local.json` out of version control (it is in `.gitignore`).
5. Update the authoritative documents in `specification/` for any change that
   affects design, schema, terminology, or behavior.

## License

KiCad SpecGen is released under the MIT License. See [LICENSE](LICENSE) for details.
