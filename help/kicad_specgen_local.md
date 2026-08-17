# Local Configuration Reference

**File location:** `{KSG_SYSTEM_CONFIG_DIR}/kicad_specgen_local.json`

This file stores machine-specific settings and absolute path token definitions.
It is never committed to a shared repository.

## Key sections

| Section | Purpose |
|---|---|
| `tokens` | KSG_* absolute path token definitions for this machine |
| `tools` | kicad-cli path, source, and version |
| `setup` | Setup state and dependency stage |
| `last_session` | Last opened project reference and window geometry |
| `recent_projects` | Up to 10 recently opened projects |
| `skipped_tokens` | Token names suppressed on this machine |
| `preferences` | UI preferences (theme) |

See **Project Setup and Tokens** for token concepts.
