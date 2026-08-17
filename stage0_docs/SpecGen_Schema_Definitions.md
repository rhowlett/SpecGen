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

### JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "kicad_specgen_local",
  "description": "Local machine configuration for KiCad SpecGen",
  "type": "object",
  "required": ["schema_version", "tokens"],
  "additionalProperties": false,
  "properties": {

    "schema_version": {
      "type": "integer",
      "description": "Schema version. Current: 1. Increment on breaking changes.",
      "enum": [1]
    },

    "active_user": {
      "type": "string",
      "description": "worker_id of the active user from kicad_specgen_users.json"
    },

    "active_environment": {
      "type": "string",
      "description": "Environment ID from kicad_specgen_company.json environments"
    },

    "tools": {
      "type": "object",
      "description": "Local tool paths",
      "properties": {
        "kicad_cli": {
          "type": "string",
          "description": "Absolute path to kicad-cli executable"
        },
        "kicad_cli_source": {
          "type": "string",
          "enum": ["detected_macos_app", "detected_linux_path", "detected_windows_path", "user_configured"],
          "description": "How kicad-cli was found: detected_macos_app (macOS app bundle), detected_linux_path (PATH or common Linux locations), detected_windows_path (Program Files or PATH), user_configured (manually set by user)"
        },
        "kicad_version": {
          "type": "string",
          "description": "KiCad version string, e.g. 9.0.x"
        }
      }
    },

    "tokens": {
      "type": "object",
      "description": "Local absolute path token definitions. Keys must match ^KSG_[A-Z0-9_]+$",
      "required": [
        "KSG_APP_DIR",
        "KSG_SYSTEM_CONFIG_DIR",
        "KSG_COMPANY_DIR",
        "KSG_USER_SPECGEN_DIR",
        "KSG_USER_COMMON_DIR"
      ],
      "properties": {
        "KSG_APP_DIR": {
          "type": "string",
          "description": "Root folder of the installed SpecGen application repository"
        },
        "KSG_SYSTEM_CONFIG_DIR": {
          "type": "string",
          "description": "OS KiCad user config folder containing kicad_specgen_local.json"
        },
        "KSG_COMPANY_DIR": {
          "type": "string",
          "description": "Root containing the shared SpecGen/ folder. May be a Git repo root."
        },
        "KSG_USER_SPECGEN_DIR": {
          "type": "string",
          "description": "User-owned SpecGen resource folder. Recommended: {KSG_COMPANY_DIR}/SpecGen/Users/<worker_id>"
        },
        "KSG_USER_COMMON_DIR": {
          "type": "string",
          "description": "User shared templates, CSS, logos. Recommended: {KSG_USER_SPECGEN_DIR}/common"
        }
      },
      "patternProperties": {
        "^KSG_[A-Z0-9_]+$": {
          "type": "string",
          "description": "Additional optional absolute path token"
        }
      },
      "additionalProperties": false
    },

    "setup": {
      "type": "object",
      "properties": {
        "setup_complete": { "type": "boolean" },
        "last_setup_run": { "type": "string", "format": "date-time" },
        "last_setup_platform": { "type": "string", "enum": ["macos", "linux", "windows"] },
        "dependency_stage": {
          "type": "string",
          "enum": ["stage1", "stage2", "stage3", "stage4"],
          "description": "Highest completed dependency stage. stage1: PySide6+jsonschema. stage2: adds Jinja2. stage3: no new packages. stage4: adds WeasyPrint."
        }
      }
    },

    "last_session": {
      "type": "object",
      "description": "State of the application at last clean exit. Written on every exit. Per-project state (active tab, environment) is in the .kicad_specgen file.",
      "properties": {
        "specgen_project": {
          "type": "string",
          "description": "Absolute path to the last opened .kicad_specgen file"
        },
        "project_name": {
          "type": "string",
          "description": "project.name cached from the last opened .kicad_specgen (for display without re-opening)"
        },
        "display_name": {
          "type": "string",
          "description": "project.display_name cached from the last opened .kicad_specgen (for display without re-opening)"
        },
        "kicad_project_dir": {
          "type": "string",
          "description": "Absolute path to KICAD_PROJECT_DIR at last session (for display without re-opening)"
        },
        "window_geometry": {
          "type": "object",
          "description": "Main window position and size at last exit. Machine-specific — correct to store here.",
          "properties": {
            "x":      { "type": "integer" },
            "y":      { "type": "integer" },
            "width":  { "type": "integer" },
            "height": { "type": "integer" }
          }
        },
        "last_opened_at": {
          "type": "string",
          "format": "date-time",
          "description": "Timestamp of the last project open event"
        }
      }
    },

    "recent_projects": {
      "type": "array",
      "description": "Up to 10 recently opened SpecGen projects, most recent first. Per-project state (environment, active tab) is in each .kicad_specgen file and is not duplicated here.",
      "maxItems": 10,
      "items": {
        "type": "object",
        "required": ["specgen_project"],
        "properties": {
          "specgen_project": {
            "type": "string",
            "description": "Absolute path to the .kicad_specgen file"
          },
          "project_name": {
            "type": "string",
            "description": "project.name cached from the .kicad_specgen file (for display without re-opening)"
          },
          "display_name": {
            "type": "string",
            "description": "project.display_name cached from the .kicad_specgen file (for display without re-opening)"
          },
          "kicad_project_dir": {
            "type": "string",
            "description": "Absolute path to KICAD_PROJECT_DIR (for display in Open Recent submenu)"
          },
          "last_opened_at": {
            "type": "string",
            "format": "date-time",
            "description": "Timestamp of the most recent open of this project"
          }
        }
      }
    },

    "skipped_tokens": {
      "type": "array",
      "description": "Token names suppressed on this machine via Missing Tokens dialog Skip option. Machine-local — does not affect other users. Cleared by the user from the Project tab.",
      "items": { "type": "string" }
    },

    "preferences": {
      "type": "object",
      "description": "User interface preferences. See SpecGen_GUI_Theme.md for theme specifications and colour palettes.",
      "properties": {
        "theme": {
          "type": "string",
          "enum": ["system", "light", "dark", "engineering_dark", "ion_dark", "ion_light"],
          "default": "dark",
          "description": "Active UI theme. system: OS-adaptive (resolves to light or dark at runtime). Default when absent or unrecognised: dark. See SpecGen_GUI_Theme.md for full palette specifications."
        }
      },
      "additionalProperties": false
    }

  }
}
```

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

### JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "kicad_specgen_company",
  "description": "Shared company/organization configuration for KiCad SpecGen",
  "type": "object",
  "required": ["schema_version", "company"],
  "additionalProperties": false,
  "properties": {

    "schema_version": {
      "type": "integer",
      "enum": [1]
    },

    "company": {
      "type": "object",
      "required": ["company_id", "name"],
      "properties": {
        "company_id": { "type": "string" },
        "name": { "type": "string" },
        "description": { "type": "string" }
      }
    },

    "paths": {
      "type": "object",
      "description": "Shared path references using token notation {TOKEN_NAME}/relative/path",
      "additionalProperties": { "type": "string" }
    },

    "clients": {
      "type": "object",
      "description": "External client definitions keyed by client_id",
      "additionalProperties": {
        "type": "object",
        "required": ["name"],
        "properties": {
          "name": { "type": "string" },
          "paths": {
            "type": "object",
            "additionalProperties": { "type": "string" }
          },
          "groups": {
            "type": "object",
            "additionalProperties": {
              "type": "object",
              "properties": {
                "name": { "type": "string" },
                "paths": {
                  "type": "object",
                  "additionalProperties": { "type": "string" }
                }
              }
            }
          }
        }
      }
    },

    "internal_teams": {
      "type": "object",
      "description": "Internal company team definitions",
      "additionalProperties": {
        "type": "object",
        "required": ["name"],
        "properties": {
          "name": { "type": "string" },
          "paths": {
            "type": "object",
            "additionalProperties": { "type": "string" }
          }
        }
      }
    },

    "environments": {
      "type": "object",
      "description": "Named environment definitions",
      "additionalProperties": {
        "type": "object",
        "required": ["type"],
        "properties": {
          "type": {
            "type": "string",
            "enum": ["client", "client_group", "internal_project", "sandbox"]
          },
          "client": { "type": "string" },
          "group": { "type": "string" },
          "team": { "type": "string" },
          "description": { "type": "string" }
        }
      }
    },

    "templates": {
      "type": "object",
      "description": "Shared template file token references",
      "additionalProperties": { "type": "string" }
    },

    "assets": {
      "type": "object",
      "description": "Shared asset token references (CSS, logos, etc.)",
      "additionalProperties": { "type": "string" }
    }
  }
}
```

### Validation Rules

| Rule | Description |
|---|---|
| No absolute paths allowed | All path values must use `{TOKEN_NAME}/...` notation |
| Token references must resolve | Each `{TOKEN}` in path values must exist in the effective token table |
| `company_id` must be non-empty | Used as identifier in reports |
| Environment `type` must be one of the enum values | Reject unknown types |

---

## 4. Schema: `kicad_specgen_users.json`

**Location:** `{KSG_COMPANY_DIR}/SpecGen/kicad_specgen_users.json`
**Owner:** SpecGen (company/shared)
**Format:** JSON
**Portable:** Yes — uses token references only

### JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "kicad_specgen_users",
  "type": "object",
  "required": ["schema_version", "users"],
  "additionalProperties": false,
  "properties": {

    "schema_version": {
      "type": "integer",
      "enum": [1]
    },

    "users": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["worker_id", "display_name", "active"],
        "properties": {
          "worker_id": { "type": "string" },
          "display_name": { "type": "string" },
          "preferred_name": { "type": "string" },
          "family_name": { "type": "string" },
          "email": { "type": "string", "format": "email" },
          "department": { "type": "string" },
          "team": { "type": "string" },
          "job_title": { "type": "string" },
          "worker_type": {
            "type": "string",
            "enum": ["employee", "contractor", "external", "hobby"]
          },
          "active": { "type": "boolean" },
          "is_admin": { "type": "boolean" },
          "clients": {
            "type": "array",
            "items": { "type": "string" }
          },
          "internal_teams": {
            "type": "array",
            "items": { "type": "string" }
          },
          "paths": {
            "type": "object",
            "description": "User path token references",
            "additionalProperties": { "type": "string" }
          }
        }
      }
    }
  }
}
```

### Validation Rules

| Rule | Description |
|---|---|
| `worker_id` must be unique | Reject duplicate worker_id values |
| `active_user` in local config must match a `worker_id` | Warn if user not found |
| `clients` entries must match `clients` keys in company file | Warn on mismatch |
| Path values must use token notation | No absolute paths in `paths` |

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

### JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "kicad_specgen_project",
  "description": "SpecGen project file. JSON format. Token references only — no absolute paths.",
  "type": "object",
  "required": ["schema_version", "workspace", "project"],
  "additionalProperties": false,
  "properties": {

    "schema_version": {
      "type": "integer",
      "enum": [1]
    },

    "workspace": {
      "type": "object",
      "required": ["mode", "environment"],
      "properties": {
        "mode": {
          "type": "string",
          "enum": ["repo", "standalone"],
          "description": "repo: project is in a Git-managed workspace. standalone: independent folder."
        },
        "environment": {
          "type": "string",
          "description": "Environment ID from kicad_specgen_company.json environments"
        }
      }
    },

    "project": {
      "type": "object",
      "required": ["name"],
      "description": "Project identity and metadata. All fields available as Jinja2 template variables.",
      "properties": {
        "name":           { "type": "string", "description": "Short project identifier, used in output filenames" },
        "display_name":   { "type": "string", "description": "Full human-readable project name for display and report cover" },
        "document_number":{ "type": "string" },
        "revision":       { "type": "string" },
        "description":    { "type": "string" },
        "engineer":       { "type": "string", "description": "Lead engineer name" },
        "company":        { "type": "string", "description": "Company or client name for this project" },
        "date":           { "type": "string", "description": "Release or document date" },
        "copyright":      { "type": "string" },
        "release_name":   { "type": "string", "description": "Release label e.g. Production Release v1.0" }
      }
    },

    "files": {
      "type": "object",
      "description": "Tokenized project support file references. All values must use {TOKEN_NAME}/... notation. Note: active jobset reference is in jobset.active_jobset, not here.",
      "properties": {
        "kicad_pro":    { "type": "string", "description": "Token reference to .kicad_pro file" },
        "logo":         { "type": "string", "description": "Token reference to logo image file" },
        "report_css":   { "type": "string", "description": "Token reference to report CSS stylesheet" },
        "bom_css":      { "type": "string", "description": "Token reference to BOM CSS stylesheet" },
        "title_page":   { "type": "string", "description": "Token reference to title page Markdown template" },
        "end_page":     { "type": "string", "description": "Token reference to end page Markdown template" }
      },
      "additionalProperties": { "type": "string" }
    },

    "variables": {
      "type": "object",
      "description": "Custom user/project variables available as Jinja2 template tokens",
      "properties": {
        "custom": {
          "type": "object",
          "description": "Key-value pairs. Keys must match ^[A-Z][A-Z0-9_]*$. Values are strings.",
          "additionalProperties": { "type": "string" }
        }
      }
    },

    "jobset": {
      "type": "object",
      "description": "Jobset state. SpecGen overrides stored here, never written back to .kicad_jobset.",
      "properties": {
        "active_jobset": {
          "type": "string",
          "description": "Token reference to the active .kicad_jobset file. Single authoritative jobset reference."
        },
        "stop_on_error": {
          "type": "boolean",
          "default": true,
          "description": "Halt run on first destination failure"
        },
        "clear_log_before_run": {
          "type": "boolean",
          "default": true,
          "description": "Clear the Output Log subtab before each run"
        },
        "destinations": {
          "type": "object",
          "description": "Per-destination-ID SpecGen overrides, keyed by destination ID from .kicad_jobset",
          "additionalProperties": {
            "type": "object",
            "properties": {
              "selected":         { "type": "boolean" },
              "heading_override": { "type": "string" },
              "notes":            { "type": "string" }
            }
          }
        },
        "last_run": {
          "type": "object",
          "description": "Result of the most recent jobset run. Written by SpecGen after each run.",
          "properties": {
            "timestamp":              { "type": "string", "format": "date-time" },
            "status":                 { "type": "string", "enum": ["success", "failure", "partial"] },
            "destinations_run":       { "type": "integer" },
            "destinations_succeeded": { "type": "integer" }
          }
        }
      }
    },

    "report": {
      "type": "object",
      "description": "Report recipe and output settings. See SpecGen_Tab_Report.md for full behavior.",
      "properties": {

        "output_dir": {
          "type": "string",
          "description": "Token reference to report output folder. Default: {JOBSET_OUTPUT_DIR}/report/"
        },

        "filename_template": {
          "type": "string",
          "description": "Filename template for the output PDF. Supports project metadata tokens.",
          "examples": ["{project_name}_{revision}_{date}_report.pdf"]
        },

        "cover": {
          "type": "object",
          "description": "Cover page configuration",
          "properties": {
            "template": { "type": "string", "description": "Token reference to cover page Markdown template" },
            "title":    { "type": "string", "description": "Cover page title. May use Jinja2 {{ variable }} syntax." },
            "subtitle": { "type": "string", "description": "Cover page subtitle. May use Jinja2 {{ variable }} syntax." },
            "logo":     { "type": "string", "description": "Token reference to logo image for cover page" }
          }
        },

        "pages": {
          "type": "object",
          "properties": {
            "order": {
              "type": "array",
              "description": "Ordered list of page/section identifiers for report assembly",
              "items": { "type": "string" }
            },
            "definitions": {
              "type": "object",
              "description": "Per-page configuration keyed by page identifier",
              "additionalProperties": {
                "type": "object",
                "required": ["source_type"],
                "properties": {
                  "source_type": {
                    "type": "string",
                    "enum": ["jobset", "markdown", "custom_pdf"],
                    "description": "jobset: from JOBSET_OUTPUT_DIR; markdown: Jinja2 template; custom_pdf: fixed PDF file"
                  },
                  "destination":       { "type": "string", "description": "Destination ID from .kicad_jobset (source_type=jobset)" },
                  "template":          { "type": "string", "description": "Token reference to .md template (source_type=markdown)" },
                  "source_file":       { "type": "string", "description": "Token reference to PDF file (source_type=custom_pdf)" },
                  "include":           { "type": "boolean", "default": true },
                  "section_label":     { "type": "string", "description": "Section heading shown in report for this page" },
                  "page_break_before": { "type": "boolean", "default": true }
                }
              }
            }
          }
        }
      }
    },

    "fabrication": {
      "type": "object",
      "description": "Fabrication ZIP package settings. See SpecGen_Tab_Report.md Fabrication subtab.",
      "properties": {

        "output_dir": {
          "type": "string",
          "description": "Token reference to FAB ZIP output folder. Default: {JOBSET_OUTPUT_DIR}/fab/"
        },

        "zip_filename_template": {
          "type": "string",
          "description": "Filename template for the fabrication ZIP. Supports project metadata tokens.",
          "examples": ["{project_name}_{revision}_{date}_fab.zip"]
        },

        "destinations": {
          "type": "object",
          "description": "Per-destination ZIP configuration keyed by destination ID from .kicad_jobset",
          "additionalProperties": {
            "type": "object",
            "properties": {
              "include":    { "type": "boolean", "description": "Whether to include this destination in the FAB ZIP" },
              "zip_folder": { "type": "string",  "description": "Folder path within the ZIP. Ex: gerbers/" }
            }
          }
        },

        "readme": {
          "type": "object",
          "description": "README file included in the FAB ZIP",
          "properties": {
            "include":  { "type": "boolean", "default": true },
            "template": { "type": "string",  "description": "Token reference to Jinja2 README Markdown template" },
            "filename": { "type": "string",  "default": "README.md" }
          }
        },

        "checksums": {
          "type": "object",
          "description": "Checksum file included in the FAB ZIP",
          "properties": {
            "include":   { "type": "boolean", "default": true },
            "algorithm": { "type": "string",  "enum": ["sha256", "md5", "sha1"], "default": "sha256" },
            "filename":  { "type": "string",  "default": "checksums.sha256" }
          }
        }
      }
    },

    "ui": {
      "type": "object",
      "description": "Optional project UI state (active tab, panel sizes). Does not set dirty flag. Not committed.",
      "additionalProperties": true
    }

  }
}
```

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
