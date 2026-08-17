# Logs

The **Logs** tab shows structured application log records for the current session.

## Difference from Output Log

| | Logs tab | Output Log (Jobset) |
|---|---|---|
| Content | SpecGen events | Raw kicad-cli output |
| Scope | Full session | Per jobset run |
| Stage | Stage 1 | Stage 3 |

## Filters

- **Level filter** — Show all records or filter by level. `WARNING+` shows
  warnings and above. `ERROR+` shows errors and critical only.
- **Source filter** — Filter by module name. Populated from sources seen
  in this session.

## Toolbar

- **Clear Display** — Clears the current display. Adds a "cleared" record.
  Does not delete log files on disk.
- **Export Log...** — Saves the current display (respecting filters) to a
  plain text file.
- **Refresh** — Flushes any buffered records into the display.

## Background Log File

Log records are also written to `{KSG_APP_DIR}/logs/specgen.log`.
Use **Help → Open Logs Folder** to open this folder in your file manager.
Logs rotate at 5 MB with up to 3 backup files.
