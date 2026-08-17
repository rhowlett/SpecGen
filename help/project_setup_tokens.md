# Project Setup and Tokens

## What are KSG_* Tokens?

Tokens are named absolute paths stored in `kicad_specgen_local.json` on your
local machine. They allow portable project files to reference files without
hard-coding absolute paths.

Example token reference:

```
{KSG_COMPANY_DIR}/SpecGen/templates/title_page.md
```

At runtime, `{KSG_COMPANY_DIR}` is replaced with the absolute path stored
in your local config.

## Required Tokens

| Token | Scope | Purpose |
|---|---|---|
| `KSG_APP_DIR` | Read-only | Root of this SpecGen repository (never written to) |
| `KSG_SYSTEM_CONFIG_DIR` | System | KiCad user config directory |
| `KSG_COMPANY_DIR` | Shared | Root of your company/personal shared folder |
| `KSG_COMPANY_SPECGEN_DIR` | Shared team | Shared SpecGen resources (templates, scaffolding) |
| `KSG_COMPANY_COMMON_DIR` | Shared team | Shared common assets (logos, images) |
| `KSG_USER_SPECGEN_DIR` | Individual | Your personal SpecGen resources |
| `KSG_USER_COMMON_DIR` | Individual | Your personal templates and assets |

## Writable-space rule

The four shared/individual tokens (`KSG_COMPANY_SPECGEN_DIR`,
`KSG_COMPANY_COMMON_DIR`, `KSG_USER_SPECGEN_DIR`, `KSG_USER_COMMON_DIR`) must
point to folders you can write to. Because `KSG_APP_DIR` is read-only, any of
these tokens pointing inside `KSG_APP_DIR` is flagged invalid (✗).

Setup leaves these four tokens empty. Set them in
**Configure → Local Machine** using the **Choose Folder** button. The folder
picker opens at the current value if one is already set.

## Token Priority (highest to lowest)

1. Protected runtime tokens (computed, not editable)
2. User config paths
3. Company config paths
4. Local `KSG_*` tokens
5. `kicad_common.json` environment vars

## Missing Tokens

If a token reference cannot be resolved, the Missing Tokens dialog appears.
Choose **Provide** to add the path, **Skip** to suppress for this session,
or **Remove** to delete the reference from the project file.

See **Configure Tab** for editing your tokens.
