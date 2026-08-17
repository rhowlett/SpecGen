# KiCad SpecGen — Logs Tab Wireframe

> **Document role:** Primary wireframe specification for the Logs workspace
> tab — layout, log record structure, filter controls, log sources by stage,
> and persistence behavior.
> **Authority:** `SpecGen_Terminology.md`, `SpecGen_Stage_Plan.md`.
> **Companion documents:** `SpecGen_Tab_Jobset.md` (Output Log subtab feeds
> the Logs tab), `SpecGen_Application_Description.md` (logging_utils.py,
> log_viewer.py), `SpecGen_GUI_Menus.md` (Open Logs Folder, Refresh).
> **Status:** Approved — ready for Stage 1 implementation.

---

## Overview

The Logs tab (`[Logs]` in the sidebar) is the persistent application log
viewer. It collects and retains structured log records from all SpecGen
subsystems across the entire session. It is implemented in
`ui/tabs/logs_tab.py` (`LogsTab` class). Log records are emitted by
`logging_utils.py` and displayed using the `log_viewer.py` widget.

It is distinct from the **Output Log subtab** in the Jobset tab:

| | Logs tab (`[Logs]`) | Output Log (Jobset subtab) |
|---|---|---|
| **Purpose** | Session-wide structured application log | Live subprocess output from kicad-cli |
| **Content** | SpecGen events: config load, validation, token resolution, project open/save, errors | Raw stdout/stderr from kicad-cli runs |
| **Persistence** | Retained for the entire session | Cleared before each run (if option set) |
| **Stage available** | Stage 1 — fully functional from first launch | Stage 3 — live during jobset execution |
| **Feeds from** | All SpecGen core and service modules | jobset_service subprocess capture |
| **Cross-feed** | Output Log content feeds into Logs tab after each run | Does not read from Logs tab |

The Logs tab is always accessible — it is functional with no project open,
and it is one of only two fully functional Stage 1 workspace tabs
(the other is the Configure tab).

---

## Stage 1 Layout

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [File]   [Edit]   [View]   [Help]                                                                          │
├───────────────┬────────────────────────────────────────────────────────────────────────────────────────────┤
│ SIDEBAR       │                                                                                            │
│               │ APPLICATION LOGS                                                                           │
│ [Project]     │ ┌──────────────┬──────────────┬──────────────────────────────────────────────────────────┐ │
│ [Variables]   │ │ Level Filter │ Source Filter │ [ Clear Display ]       [ Export Log... ]   [ Refresh ] │ │
│ [Jobset]      │ │ All     ▼   │ All      ▼   │                                                          │ │
│ [Report]      │ └──────────────┴──────────────┴──────────────────────────────────────────────────────────┘ │
│               │ ┌──────────────────────────────────────────────────────────────────────────────────────┬─┐ │
│▶[Logs]        │ │ Timestamp              │ Level   │ Source            │ Message                       │^│ │
│ ───────────── │ ├────────────────────────┼─────────┼───────────────────┼───────────────────────────────┤ │ │
│ [Configure]   │ │ 2026-06-03 09:00:01   │ INFO    │ app               │ KiCad SpecGen 0.1.0 started   │ │ │
│               │ │ 2026-06-03 09:00:01   │ INFO    │ platform_paths    │ KICAD_COMMON_DIR resolved:    │ │ │
│               │ │                       │         │                   │ ~/Library/Preferences/kicad/9 │ │ │
│               │ │ 2026-06-03 09:00:02   │ INFO    │ specgen_local_cfg │ kicad_specgen_local.json      │ │ │
│               │ │                       │         │                   │ loaded successfully            │ │ │
│               │ │ 2026-06-03 09:00:02   │ INFO    │ token_resolver    │ Effective token table built:  │ │ │
│               │ │                       │         │                   │ 5 tokens resolved              │ │ │
│               │ │ 2026-06-03 09:00:02   │ INFO    │ specgen_company   │ kicad_specgen_company.json    │ │ │
│               │ │                       │         │                   │ loaded: 2 environments         │ │ │
│               │ │ 2026-06-03 09:00:03   │ INFO    │ project_config    │ Project restored from         │ │ │
│               │ │                       │         │                   │ last_session: BoardA           │ │ │
│               │ │ 2026-06-03 09:00:03   │ WARNING │ token_resolver    │ KSG_USER_COMMON_DIR:          │ │ │
│               │ │                       │         │                   │ directory is empty             │ │ │
│               │ │ 2026-06-03 09:00:03   │ INFO    │ validation_svc    │ Configuration validation:     │ │ │
│               │ │                       │         │                   │ 8 passed, 1 warning            │ │ │
│               │ │                                                                                      │ │ │
│               │ │                                                                                      │v│ │
│               │ └──────────────────────────────────────────────────────────────────────────────────────┴─┘ │
│               │  Showing 9 records  │  ⚠ 1 warning                                                        │
├───────────────┴────────────────────────────────────────────────────────────────────────────────────────────┤
│ STATUS: Session started 2026-06-03 09:00:01 | 9 log records | ⚠ 1 warning                                 │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Log Record Structure

Each log record is a structured object emitted by `logging_utils.py`. The
Logs tab display maps these fields to columns:

| Field | Column | Description |
|---|---|---|
| `timestamp` | Timestamp | ISO 8601 local time: `YYYY-MM-DD HH:MM:SS` |
| `level` | Level | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `source` | Source | Module or subsystem name (see §Log Sources below) |
| `message` | Message | Human-readable event description |
| `detail` | (tooltip) | Optional extended detail — shown in tooltip on row hover |
| `project` | (metadata) | Project name at the time of the record (for filtering in future stages) |

Long messages wrap within the Message column. The record row expands to fit.
The Timestamp, Level, and Source columns are fixed-width; Message expands.

### Level colour coding

Level text is coloured using the active theme's `--log-*` tokens:

| Level | Token | Display |
|---|---|---|
| `DEBUG` | `--log-text` (dimmed) | Grey — lowest priority, verbose detail |
| `INFO` | `--log-info` | Default text — normal events |
| `WARNING` | `--log-warning` | Amber / Gold — non-blocking issue |
| `ERROR` | `--log-error` | Red — blocking issue |
| `CRITICAL` | `--log-error` (bold) | Red bold — fatal or unrecoverable |

---

## Filter Controls

### Level Filter (dropdown)

```text
All         (default — shows all levels)
DEBUG
INFO
WARNING
ERROR
CRITICAL
WARNING+    (WARNING, ERROR, CRITICAL combined)
ERROR+      (ERROR, CRITICAL combined)
```

### Source Filter (dropdown)

Populated dynamically from the unique source values present in the current
session's log records. Always includes `All` as the default.

Example populated list:

```text
All
app
platform_paths
specgen_local_cfg
specgen_company
specgen_users
token_resolver
project_config
validation_svc
jobset_svc       (added in Stage 3)
report_svc       (added in Stage 4)
```

Both filters are applied simultaneously (AND logic). Changing either filter
updates the display immediately — no Apply button.

---

## Toolbar Actions

### `[ Clear Display ]`

Clears the Logs tab display for the current session. Does not delete any
log files on disk. A new `INFO` record is immediately appended:

```text
2026-06-03 14:32:10  INFO  app  Log display cleared by user.
```

This record persists even after a clear — it is the anchor for the new
session segment.

### `[ Export Log... ]`

Opens a Save File dialog. Exports all log records currently in the display
(respecting active filters) to a plain text file:

```text
Default filename: SpecGen_log_YYYYMMDD_HHMMSS.txt
Default location: {KSG_SYSTEM_LOG_DIR} if defined, else {KSG_APP_DIR}/logs/
```

Export format (plain text, one record per line):

```text
2026-06-03 09:00:01  INFO     app               KiCad SpecGen 0.1.0 started
2026-06-03 09:00:01  INFO     platform_paths    KICAD_COMMON_DIR resolved: ~/Library/...
2026-06-03 09:00:03  WARNING  token_resolver    KSG_USER_COMMON_DIR: directory is empty
```

### `[ Refresh ]`

Flushes any buffered log records from the logging service into the display.
Equivalent to View → Refresh for the Logs tab. Updates the record count
in the footer.

---

## Log Sources by Stage

### Stage 1 sources (always present)

| Source name | Module | Events logged |
|---|---|---|
| `app` | `app.py` | Application start, shutdown, theme change |
| `platform_paths` | `core/platform_paths.py` | KICAD_COMMON_DIR detection, platform info |
| `specgen_local_cfg` | `core/specgen_local_config.py` | Local config load, save, validation |
| `specgen_company` | `core/specgen_company_config.py` | Company config load, save |
| `specgen_users` | `core/specgen_user_config.py` | Users config load, save |
| `token_resolver` | `core/token_resolver.py` | Token table build, missing tokens, skipped tokens |
| `validation_svc` | `services/validation_service.py` | Validation run results (summary + per-check) |
| `config_svc` | `services/config_service.py` | Config save operations |
| `setup` | `setup/setup.py` | Setup phase completion, errors |
| `migrations` | `core/migrations.py` | Schema migration events |

### Stage 2 additions

| Source name | Module | Events logged |
|---|---|---|
| `project_config` | `core/project_config.py` | Project open, save, close, migrate |
| `kicad_pro` | `core/kicad_pro_parser.py` | .kicad_pro read, text variables found |
| `kicad_jobset` | `core/kicad_jobset_parser.py` | .kicad_jobset read, destinations found |
| `project_svc` | `services/project_service.py` | Project lifecycle events |
| `reconciliation` | `services/project_service.py` | Jobset/report reconciliation warnings |

### Stage 3 additions

| Source name | Module | Events logged |
|---|---|---|
| `jobset_svc` | `services/jobset_service.py` | Run start, destination results, run complete |

The Stage 3 jobset log is also the content that feeds from the Output Log
subtab. After each run, the Output Log content is appended to the Logs tab
as a batch of structured records with source `jobset_svc`.

### Stage 4 additions

| Source name | Module | Events logged |
|---|---|---|
| `report_svc` | `services/report_service.py` | Report render, PDF assemble, FAB ZIP build |

---

## `logging_utils.py` Implementation Notes

### `QtLogHandler` — logging bridge to the Qt main thread

The Python `logging` module calls handlers synchronously on the thread that
emits the log record. Passing log records directly to a Qt widget from any
non-main thread will crash PySide6. Stage 1 is single-threaded, but Stage 3
introduces subprocess threads and this must be handled correctly from the start.

The required pattern is a `logging.Handler` subclass that delivers records to
the Qt main thread via a Signal:

```python
class QtLogHandler(logging.Handler, QObject):
    """Routes Python log records to the Qt main thread via Signal."""

    record_emitted = Signal(str, str, str, str)
    # payload: (timestamp: str, level: str, source: str, message: str)

    def __init__(self):
        logging.Handler.__init__(self)
        QObject.__init__(self)

    def emit(self, record: logging.LogRecord) -> None:
        try:
            timestamp = self.formatTime(record, "%Y-%m-%d %H:%M:%S")
            level     = record.levelname          # "INFO", "WARNING", etc.
            source    = record.name               # module name e.g. "token_resolver"
            message   = record.getMessage()
            self.record_emitted.emit(timestamp, level, source, message)
        except Exception:
            self.handleError(record)
```

`logging_utils.py` creates the `QtLogHandler` singleton and attaches it to the
root logger:

```python
# logging_utils.py
_qt_handler: QtLogHandler | None = None

def get_qt_handler() -> QtLogHandler:
    global _qt_handler
    if _qt_handler is None:
        _qt_handler = QtLogHandler()
        _qt_handler.setLevel(logging.DEBUG)
        logging.getLogger().addHandler(_qt_handler)
    return _qt_handler
```

`LogsTab` connects to the handler's signal during `__init__`:

```python
# logs_tab.py
class LogsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        ...
        handler = logging_utils.get_qt_handler()
        handler.record_emitted.connect(self._on_record)

    def _on_record(self, timestamp: str, level: str,
                   source: str, message: str) -> None:
        # Append to in-memory buffer and update display
        ...
```

Because `record_emitted` is a Qt Signal and `LogsTab` lives on the main thread,
Qt automatically uses a `QueuedConnection` when `emit()` is called from a
non-main thread. This is thread-safe by construction.

### Within a session

Log records are held in memory for the entire application session. They
survive:

```text
Tab switches (navigating away from Logs and back)
Project open, save, and close
Refresh operations
```

They do not survive:

```text
Application exit — the in-memory buffer is not persisted to disk
                   unless the user explicitly uses [ Export Log... ]
```

### Cross-session

The Logs tab does not automatically restore the previous session's log on
startup. Each new session starts with a fresh in-memory buffer. The first
record is always:

```text
<timestamp>  INFO  app  KiCad SpecGen <version> started
```

If the user wants to retain logs across sessions, they use `[ Export Log... ]`
before closing, or they configure `KSG_SYSTEM_LOG_DIR` and rely on the Python
logging file handler that `logging_utils.py` sets up automatically.

### File logging (background)

`logging_utils.py` configures a Python `RotatingFileHandler` writing to:

```text
{KSG_SYSTEM_LOG_DIR}/specgen.log        (if KSG_SYSTEM_LOG_DIR is defined)
{KSG_APP_DIR}/logs/specgen.log          (fallback)
```

File logging runs independently of the Logs tab display. All records at
`DEBUG` level and above are written to the file; the Logs tab display starts
at `INFO` by default (user can change the filter to see `DEBUG`).

The log file is rotated at 5 MB with up to 3 backup files:

```text
specgen.log
specgen.log.1
specgen.log.2
specgen.log.3
```

---

## Output Log → Logs Tab Feed (Stage 3)

When a jobset run completes (Stage 3), the Output Log subtab content is
appended to the Logs tab as structured records:

```text
Source: jobset_svc
Level:  INFO for success lines, WARNING for warnings, ERROR for failures
```

This feed happens once per run — at run completion, not during live streaming.
The live stream remains in the Output Log subtab only. After the run, a
summary record appears in the Logs tab:

```text
<timestamp>  INFO  jobset_svc  Jobset run complete: 4/4 destinations succeeded.
                               Output: {JOBSET_OUTPUT_DIR}
```

If the run had failures:

```text
<timestamp>  ERROR  jobset_svc  Jobset run failed: 2/4 destinations succeeded.
                                Failed: gerbers, step_model
```

---

## Footer

The footer bar below the log table shows:

```text
Showing <N> records  │  ✓ <N> info  │  ⚠ <N> warnings  │  ✗ <N> errors
```

When a filter is active:

```text
Showing <N> of <total> records  │  Filter: WARNING+  │  Source: token_resolver
```

---

## Acceptance Criteria

```text
Stage 1

✓ Logs tab accessible from sidebar [Logs]
✓ Logs tab functional with no project open
✓ Application startup events appear in Logs tab within 1 second of launch
✓ Log table shows Timestamp, Level, Source, Message columns
✓ Long messages wrap within Message column; row expands to fit
✓ Level text coloured correctly per active theme --log-* tokens
✓ Level filter dropdown updates display immediately (no Apply)
✓ Source filter dropdown populates from unique sources in current session
✓ Source filter dropdown updates display immediately
✓ Both filters apply simultaneously (AND logic)
✓ [ Clear Display ] clears display and appends "Log display cleared" record
✓ [ Export Log... ] saves current display (respecting filters) to .txt file
✓ [ Refresh ] flushes buffered records into display
✓ Record count and warning/error summary shown in footer
✓ Log records survive tab switches and project open/close
✓ Each new session starts with app startup record
✓ Background file logging writes to KSG_SYSTEM_LOG_DIR or fallback
✓ View → Logs menu item switches to this tab

Stage 3

✓ jobset_svc source appears in Source filter after first jobset run
✓ Run summary record appended to Logs tab at run completion
✓ Run failure shows ERROR level record with failed destination names
✓ Output Log → Logs feed does not cause UI freeze
```

---

## Menu and Navigation Reference

The Logs tab layout and navigation follow the same conventions as all other
workspace tabs. The View menu, sidebar labels, and menu bar are defined in
`SpecGen_GUI_Menus.md` — the authoritative source for all menu structure.

Key points relevant to the Logs tab:

- `View → Logs` switches to this tab from any screen.
- `Help → Open Logs Folder` opens the folder containing the background log
  file (`KSG_SYSTEM_LOG_DIR` or `{KSG_APP_DIR}/logs/`) in the OS file manager.
- `View → Refresh` flushes buffered log records (equivalent to `[ Refresh ]`
  in the toolbar when Logs tab is active).

---

*End of KiCad SpecGen Logs Tab Wireframe.*
