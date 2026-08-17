# Required KiCad SpecGen Configuration and Token Framework

## 1. Purpose

This document defines the required configuration files, token framework, file ownership rules, and file-open sequence for KiCad SpecGen.

This document is intended to be used as an implementation specification for building KiCad SpecGen with Python 3 and PySide6.

The configuration model is based on one core rule:

```text
Local absolute path token definitions live in kicad_specgen_local.json.

Company, user, and project configuration files use token references.

The application resolves token references during file open, validation, and runtime operation.
```

This rule keeps machine-specific paths out of shared company files and project files while still allowing each user to resolve the same shared configuration on their own machine.

---

## 2. User Types and Installation Model

KiCad SpecGen supports two primary user types while maintaining a common application framework.

A project must be capable of operating in either standalone mode or repository mode without requiring modifications to the user's workspace structure. The mode is determined by the environment configuration and project location rather than by changes to the project itself.

### 2.1 Hobby User

A hobby user typically:

* Uses a single machine.
* Works from one or more local project locations.
* May maintain personal templates, libraries, and report assets.
* May choose to separate projects while sharing common user resources.
* Installs the application locally and seeds or links projects with application-provided templates and support files.
* May operate entirely without a company repository.

### 2.2 Professional User

A professional user typically:

* Works for a company or organization.
* Supports one or more internal teams, groups, or departments.
* Supports one or more external clients.
* Maintains company-wide templates, libraries, documentation, and report assets.
* Maintains client-specific templates, libraries, documentation, and report assets.
* May work on internal company projects, client projects, or sandbox projects.
* May store projects, company resources, and client resources in separate repositories.
* May share common company configuration across multiple users.
* May synchronize company and client information through a shared company repository.

---

## 3. Application Installation Model

The SpecGen application itself is always installed from the official Git repository.

Requirements:

* The application is cloned from the SpecGen Git repository.
* The application may update itself from the Git repository.
* Users are not expected to push changes back to the application repository.
* All default templates, support files, examples, and bundled resources are maintained within the application repository.
* Application updates must not overwrite user, company, client, or project data.
* User, company, client, and project data must be stored separately from the application repository.

This separation ensures that application updates remain independent from company and project configuration.

---

## 4. Ownership Terminology

To eliminate ambiguity, the following terms have specific meanings throughout SpecGen.

### 4.1 User

The individual engineer, designer, employee, contractor, or hobby user using SpecGen.

Examples:

* John Smith
* Jane Doe
* Contractor A
* Hobby User A

### 4.2 Company

The organization, team, or personal shared-work root that owns shared SpecGen resources.

For a professional user, this is normally the user's company or organization.

For a hobby or standalone user, this may be a local personal SpecGen data folder.

Examples:

* Advanced Engineering
* ABC Electronics
* Internal R&D Organization
* Personal SpecGen Workspace

Company resources may include templates, logos, reusable report content, libraries, and shared configuration.

### 4.3 Client

An external organization for which the user's company performs work.

Examples:

* Client A
* Medical Devices Inc.
* Aerospace Systems Ltd.

Client resources belong to the external organization.

### 4.4 Client Group

A subdivision within a client organization.

Examples:

* Hardware Team
* Product Development Group
* Manufacturing Engineering
* Program Alpha Team

A user may perform work for multiple groups within the same client organization.

### 4.5 Project

The specific engineering effort being performed.

Examples:

* Motor Controller Rev B
* Sensor Gateway
* Production Test Fixture

Projects may belong to:

* The user's company.
* A client organization.
* A specific client group.
* A user's personal, sandbox, or experimental environment.

Recommended conceptual model:

```text
User
  └─ Company / Shared SpecGen Data Root
       ├─ Internal Team / Group
       │    └─ Project
       │
       └─ Client
            ├─ Client Group / Team
            │    └─ Project
            │
            └─ Client Group / Team
                 └─ Project
```

The token naming system shall make these ownership boundaries obvious to users configuring environments.

---

## 5. Configuration File Inventory

KiCad SpecGen uses the following configuration and input files.

| File                                 | Owner                       | Location                                     | Purpose                                                                                                             |
| ------------------------------------ | --------------------------- | -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `kicad_specgen_local.json`           | SpecGen local machine       | KiCad user configuration folder              | Stores local machine paths, tool paths, setup state, recent projects, active user, and active environment.          |
| `kicad_common.json`                  | KiCad                       | KiCad user configuration folder              | Optional read-only source of KiCad environment variables and user configuration.                                    |
| `SpecGen/kicad_specgen_company.json` | SpecGen shared/company data | Under `{KSG_COMPANY_DIR}/SpecGen/`           | Stores company, client, team, shared path references, shared templates, shared assets, and environment definitions. |
| `SpecGen/kicad_specgen_users.json`   | SpecGen shared/company data | Under `{KSG_COMPANY_DIR}/SpecGen/`           | Stores minimal user directory information used by SpecGen.                                                          |
| `<name>.kicad_specgen`               | SpecGen project             | Under `{KSG_PROJECT_SPECGEN_DIR}/` folder    | Stores project-specific SpecGen state and report/FAB recipe data using token references.                            |
| `<project>.kicad_pro`                | KiCad project               | Under `{KICAD_PROJECT_DIR}/` folder          | KiCad project file and source of KiCad text variables.                                                              |
| `<name>.kicad_jobset`                | KiCad jobset                | Ideally under `specgen/` or `common/` folder | Defines KiCad jobset destinations and generated output files.                                                       |

---

# 6. Token Framework

## 6.1 Token Definitions and Token References

SpecGen separates path data into two categories.

```text
Token definitions
  Absolute local paths stored in kicad_specgen_local.json.

Token references
  Portable paths stored in company, user, and project configuration files.
```

Example token definition in `kicad_specgen_local.json`:

```json
{
  "tokens": {
    "KSG_COMPANY_DIR": "/Users/john/Engineering/CompanyRepo"
  }
}
```

Example token reference in `kicad_specgen_company.json`:

```json
{
  "paths": {
    "company_templates": "{KSG_COMPANY_DIR}/SpecGen/templates"
  }
}
```

Example token reference in a project `.kicad_specgen` file:

```json
{
  "files": {
    "report_css": "{KSG_COMPANY_DIR}/SpecGen/assets/report_style.css" 
  }
}
```

Resolved result on this user’s machine:

```text
/Users/john/Engineering/CompanyRepo/SpecGen/assets/report_style.css
```

## 6.2 Token Storage Rule

Only `kicad_specgen_local.json` stores local absolute token definitions.

The following files shall use token references and shall not define local machine absolute token values:

* `SpecGen/kicad_specgen_company.json`
* `SpecGen/kicad_specgen_users.json`
* Project `.kicad_specgen` files

Absolute paths may appear in these files only when explicitly marked as local-only, non-portable data. Normal project and company paths should be tokenized.

## 6.3 Stored Token Naming Rule

Stored local tokens in `kicad_specgen_local.json` shall use the `KSG_*` namespace.

Recommended validation rule:

```text
^KSG_[A-Z0-9_]+$
```

All stored token values must be absolute paths.

## 6.4 Reserved Token Prefixes

Token names must clearly identify ownership and scope.

| Prefix          | Scope                                                  |
| --------------- | ------------------------------------------------------ |
| `KSG_USER_*`    | Individual user resources.                             |
| `KSG_COMPANY_*` | Company, organization, or standalone shared resources. |
| `KSG_CLIENT_*`  | External client resources.                             |
| `KSG_PROJECT_*` | SpecGen-owned project resources.                       |
| `KSG_APP_*`     | SpecGen application installation resources.            |
| `KSG_SYSTEM_*`  | OS-specific configuration resources.                   |
| `KICAD_*`       | KiCad-owned project and jobset resources.              |

## 6.5 Required Local Tokens

The following tokens are required in `kicad_specgen_local.json` for all installations.

| Token                   | Required For     | Description                                                                                                                                        |
| ----------------------- | ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| `KSG_APP_DIR`           | standalone, repo | Root folder of the installed SpecGen application repository. Used to find bundled defaults, examples, setup scripts, and application resources.    |
| `KSG_SYSTEM_CONFIG_DIR` | standalone, repo | OS-specific KiCad user configuration folder containing `kicad_specgen_local.json`.                                                                 |
| `KSG_COMPANY_DIR`       | standalone, repo | Root folder containing the shared or standalone `SpecGen/` data folder. May be a Git repository in repo mode or a local folder in standalone mode. |
| `KSG_USER_SPECGEN_DIR`  | standalone, repo | Root folder for user-owned SpecGen resources. Recommended location: `<KSG_COMPANY_DIR>/SpecGen/Users/<worker_id>/`.                                |
| `KSG_USER_COMMON_DIR`   | standalone, repo | User-owned shared templates, CSS, logos, report assets, and reusable resources. Recommended location: `<KSG_USER_SPECGEN_DIR>/common/`.            |

Recommended relationship:

```text
KSG_COMPANY_DIR
└─ SpecGen/
   └─ Users/
      └─ <worker_id>/
         ├─ common/
         ├─ reports/
         ├─ templates/
         └─ assets/
```

Recommended token expansion:

```text
KSG_USER_SPECGEN_DIR = <KSG_COMPANY_DIR>/SpecGen/Users/<worker_id>
KSG_USER_COMMON_DIR  = <KSG_USER_SPECGEN_DIR>/common
```

Values stored in `kicad_specgen_local.json` should still be absolute paths, not nested token references.

## 6.6 Optional Local Tokens

The local configuration may define additional absolute path tokens when needed.

Examples:

| Token                    | Description                                                  |
| ------------------------ | ------------------------------------------------------------ |
| `KSG_APP_COMMON_DIR`     | Optional explicit path to application-provided common files. |
| `KSG_USER_REPORTS_DIR`   | User-owned generated or reusable reports folder.             |
| `KSG_USER_TEMPLATES_DIR` | User-owned templates folder.                                 |
| `KSG_USER_ASSETS_DIR`    | User-owned images, logos, and reusable assets folder.        |
| `KSG_SYSTEM_LOG_DIR`     | Local machine log output folder.                             |
| `KSG_SYSTEM_CACHE_DIR`   | Local cache folder.                                          |

Optional tokens should point to folders or root paths, not individual normal report files.

## 6.7 Protected Derived Runtime Tokens

The following tokens are computed at runtime and must not be stored as token definitions in `kicad_specgen_local.json`.

| Token                     | Derived From                                 | Description                                                                                      |
| ------------------------- | -------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| `SPECGEN_PROJECT_FILE`    | Opened `.kicad_specgen` file                 | Absolute path to the active SpecGen project file.                                                |
| `KSG_PROJECT_SPECGEN_DIR` | Parent folder of `SPECGEN_PROJECT_FILE`      | Project-local `specgen/` folder containing the active `.kicad_specgen` file.                     |
| `KICAD_PROJECT_DIR`       | Parent folder of `KSG_PROJECT_SPECGEN_DIR`   | KiCad project folder containing the active `.kicad_pro`.                                         |
| `GIT_PROJECT_DIR`         | Git root discovered from `KICAD_PROJECT_DIR` | Git repository root for the active project. In standalone mode, defaults to `KICAD_PROJECT_DIR`. |
| `JOBSET_OUTPUT_DIR`       | Active `.kicad_jobset` output settings       | Root folder for generated jobset outputs.                                                        |
| `FAB_OUTPUT_DIR`          | Project/FAB settings and active jobset       | Root folder for fabrication package output.                                                      |

The project-local `specgen/` directory token is named:

```text
KSG_PROJECT_SPECGEN_DIR
```

This folder is owned by SpecGen, not KiCad.

## 6.8 Token Reference Format

Token references use braces:

```text
{TOKEN_NAME}/relative/path
```

Examples:

```text
{KSG_COMPANY_DIR}/SpecGen/templates/title_page.md
{KSG_USER_COMMON_DIR}/logos/default_logo.png
{KSG_PROJECT_SPECGEN_DIR}/release_default.kicad_jobset
{KICAD_PROJECT_DIR}/background/release_notes.md
{JOBSET_OUTPUT_DIR}/sch/BoardA.pdf
```

## 6.9 Missing Token Handling

If a token reference cannot be resolved, SpecGen shall show a Missing Tokens dialog.

The dialog shall show:

* Missing token name.
* File or setting where the token is used.
* Active environment.
* Suggested repair action.

User options:

* Add token to `kicad_specgen_local.json`.
* Pick a replacement file or folder.
* Skip the affected item.
* Cancel open/import.

If the user adds a token, SpecGen updates:

```text
kicad_specgen_local.json -> tokens.<TOKEN_NAME>
```

The project `.kicad_specgen` file shall remain portable and shall not be rewritten with an absolute path.

---

# 7. JSON Open and Token Resolution Sequence

SpecGen uses `kicad_specgen_local.json` as the only local-machine token definition file.

Company, user, and project configuration files store token references, not local absolute path definitions.

The application resolves files in this order:

```text
1. Start application. If steps 3 .. 6 fail, then exit and start the Setup application.

2. Locate the KiCad user configuration folder {KICAD_COMMON_DIR}.

3. Open:
   kicad_specgen_local.json

4. Load local absolute tokens:
   KSG_APP_DIR
   KSG_SYSTEM_CONFIG_DIR
   KSG_COMPANY_DIR
   KSG_USER_SPECGEN_DIR
   KSG_USER_COMMON_DIR

5. Use KSG_COMPANY_DIR to open:
   {KSG_COMPANY_DIR}/SpecGen/kicad_specgen_company.json

6. Use KSG_COMPANY_DIR to open:
   {KSG_COMPANY_DIR}/SpecGen/kicad_specgen_users.json

7. Open the last project .kicad_specgen file. If no last project present, then skip to step 14 and populate GUI empty

8. Derive protected project runtime tokens:
   SPECGEN_PROJECT_FILE
   KSG_PROJECT_SPECGEN_DIR
   KICAD_PROJECT_DIR
   GIT_PROJECT_DIR

9. Open and parse the project .kicad_specgen file.

10. Expand token references in company, user, and project configuration data.

11. Parse and validate the active KiCad project file.

12. Parse and validate the active .kicad_jobset file when needed.

13. Validate all resolved paths.

14. Populate the GUI.
```

This sequence avoids token precedence ambiguity. Local absolute token values come from `kicad_specgen_local.json`; other files use token references.

Protected derived runtime tokens are generated from the opened project and active jobset and are not user-editable local tokens.

---

# 8. File Chapter: `kicad_specgen_local.json`

## 8.1 Purpose

`kicad_specgen_local.json` is the local machine configuration file for KiCad SpecGen.

It stores:

* Local machine paths.
* Application installation paths.
* Setup state.
* Recent projects.
* Active user.
* Active environment.
* Local tool paths.
* Machine-specific preferences.
* Local absolute token definitions.

This file is required.

## 8.2 Location

`kicad_specgen_local.json` is stored in the same OS-specific configuration location used by KiCad for user configuration data.

Typical examples:

```text
Windows:
%APPDATA%\KiCad\9.0\kicad_specgen_local.json

Linux:
~/.config/kicad/9.0/kicad_specgen_local.json

macOS:
~/Library/Preferences/kicad/9.0/kicad_specgen_local.json
```

Where `9.0` is the KiCad configuration version.

## 8.3 Ownership

This file is owned by SpecGen and is local to one user and one machine.

It must never be treated as the company source of truth.

It may contain absolute paths.

It should not be committed into a shared company or project repository.

## 8.4 Required Contents

Required top-level sections:

| Section              | Purpose                                            |
| -------------------- | -------------------------------------------------- |
| `schema_version`     | Local config schema version.                       |
| `active_user`        | Current user ID from `kicad_specgen_users.json`.   |
| `active_environment` | Current environment ID from company configuration. |
| `tools`              | Local executable paths such as `kicad-cli`.        |
| `tokens`             | Local absolute path token definitions.             |
| `setup`              | Setup/bootstrap state.                             |
| `last_session`       | Last opened SpecGen project.                       |
| `recent_projects`    | Up to 10 recently opened SpecGen projects.         |

## 8.5 Recent Projects

`recent_projects` is local session state and belongs only in `kicad_specgen_local.json`.

Rules:

```text
Keep up to 10 entries.
Each entry must reference a unique absolute specgen_project path.
When a project is opened, move it to the top.
If the list grows beyond 10 entries, remove the oldest entry.
If a recent project file no longer exists, show a warning when selected.
Do not store recent projects in the project .kicad_specgen file.
```

## 8.6 Example

```json
{
  "schema_version": 1,
  "active_user": "12345",
  "active_environment": "medical_devices",

  "tools": {
    "kicad_cli": "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli",
    "kicad_cli_source": "detected_macos_app",
    "kicad_version": "9.0.x"
  },

  "tokens": {
    "KSG_APP_DIR": "/Users/john/Documents/GitHub/kicad-specgen",
    "KSG_SYSTEM_CONFIG_DIR": "/Users/john/Library/Preferences/kicad/9.0",
    "KSG_COMPANY_DIR": "/Users/john/Engineering/CompanyRepo",
    "KSG_USER_SPECGEN_DIR": "/Users/john/Engineering/CompanyRepo/SpecGen/Users/12345",
    "KSG_USER_COMMON_DIR": "/Users/john/Engineering/CompanyRepo/SpecGen/Users/12345/common"
  },

  "setup": {
    "setup_complete": true,
    "last_setup_run": "2026-06-03T14:32:00",
    "last_setup_platform": "macos",
    "dependency_stage": "stage1"
  },

  "last_session": {
    "environment": "medical_devices",
    "specgen_project": "/Users/john/Clients/MedicalDevices/BoardA/specgen/release.kicad_specgen",
    "last_opened_at": "2026-06-03T14:32:00"
  },

  "recent_projects": [
    {
      "environment": "medical_devices",
      "specgen_project": "/Users/john/Clients/MedicalDevices/BoardA/specgen/release.kicad_specgen",
      "display_name": "BoardA - Release",
      "last_opened_at": "2026-06-03T14:32:00"
    },
    {
      "environment": "sandbox",
      "specgen_project": "/Users/john/Sandbox/KiCad/TestFixture/specgen/test_fixture.kicad_specgen",
      "display_name": "TestFixture - Sandbox",
      "last_opened_at": "2026-05-29T09:15:00"
    }
  ]
}
```

## 8.7 Application Use

The application uses `kicad_specgen_local.json` to:

* Find `kicad-cli`.
* Locate the shared or standalone SpecGen data root.
* Open company and user configuration files.
* Restore the last opened project.
* Populate the File → Open Recent menu.
* Resolve local absolute path tokens.
* Save local setup and preference changes.
* Store machine-specific values that must not be written into project files.

---

# 9. File Chapter: `kicad_common.json`

## 9.1 Purpose

`kicad_common.json` is KiCad’s user configuration file.

SpecGen may read this file to inspect KiCad environment variables and configuration paths.

## 9.2 Ownership

This file is owned by KiCad.

SpecGen shall treat it as read-only during normal application operation.

SpecGen may modify this file during setup only if the user approves.

Before writing to `kicad_common.json`, SpecGen must create a timestamped backup:

```text
kicad_common.json.bak_YYYYMMDD_HHMMSS
```

## 9.3 Application Use

SpecGen may use `kicad_common.json` to:

* Display KiCad environment variables in the Project tab.
* Compare KiCad paths to SpecGen tokens.
* Help locate KiCad user configuration folders.
* Validate KiCad-related paths.

SpecGen-specific local path tokens belong in `kicad_specgen_local.json`.

---

# 10. File Chapter: `SpecGen/kicad_specgen_company.json`

## 10.1 Purpose

`kicad_specgen_company.json` stores shared company, client, team, template, asset, and environment information.

This file is the shared organizational configuration file.

It does not store local absolute path token definitions.

It stores token references that resolve through `kicad_specgen_local.json`.

## 10.2 Location

The file is located at:

```text
{KSG_COMPANY_DIR}/SpecGen/kicad_specgen_company.json
```

The resolved path is determined by expanding `KSG_COMPANY_DIR` from `kicad_specgen_local.json`.

## 10.3 Ownership

This file is owned by SpecGen.

For a professional workflow, this file may be stored in a Git repository shared by multiple users.

For a standalone workflow, this file may be stored in a local user folder.

SpecGen should be the authoritative writer for this file. Manual edits are not recommended and should be validated by SpecGen before use.

## 10.4 Required Contents

Recommended top-level sections:

| Section          | Purpose                                                 |
| ---------------- | ------------------------------------------------------- |
| `schema_version` | Company config schema version.                          |
| `company`        | Organization or standalone workspace identity.          |
| `paths`          | Shared path references using tokens.                    |
| `clients`        | External client definitions.                            |
| `internal_teams` | Internal company or personal project group definitions. |
| `environments`   | Logical environment definitions used by project files.  |
| `templates`      | Shared template references.                             |
| `assets`         | Shared logo, CSS, and reusable asset references.        |

## 10.5 Path Rules

Paths in this file should be token references.

Good:

```json
{
  "paths": {
    "company_templates": "{KSG_COMPANY_DIR}/SpecGen/templates"
  }
}
```

Avoid:

```json
{
  "paths": {
    "company_templates": "/Users/john/Engineering/CompanyRepo/SpecGen/templates"
  }
}
```

Absolute paths in this file make the company configuration non-portable across users and machines.

## 10.6 Example

```json
{
  "schema_version": 1,

  "company": {
    "company_id": "AE",
    "name": "Advanced Engineering",
    "description": "Engineering consulting and product development"
  },

  "paths": {
    "company_root": "{KSG_COMPANY_DIR}",
    "company_specgen": "{KSG_COMPANY_DIR}/SpecGen",
    "company_docs": "{KSG_COMPANY_DIR}/SpecGen/docs",
    "company_templates": "{KSG_COMPANY_DIR}/SpecGen/templates",
    "company_assets": "{KSG_COMPANY_DIR}/SpecGen/assets",
    "company_libraries": "{KSG_COMPANY_DIR}/path/to/kicad/libraries"
  },

  "clients": {
    "medical_devices": {
      "name": "Medical Devices Inc",
      "paths": {
        "client_root": "{KSG_COMPANY_DIR}/Clients/MedicalDevices",
        "client_docs": "{KSG_COMPANY_DIR}/Clients/MedicalDevices/docs",
        "client_assets": "{KSG_COMPANY_DIR}/Clients/MedicalDevices/assets"
      },
      "groups": {
        "hardware": {
          "name": "Hardware Team",
          "paths": {
            "group_docs": "{KSG_COMPANY_DIR}/Clients/MedicalDevices/hardware/docs"
          }
        },
        "manufacturing": {
          "name": "Manufacturing Engineering",
          "paths": {
            "group_docs": "{KSG_COMPANY_DIR}/Clients/MedicalDevices/manufacturing/docs"
          }
        }
      }
    },

    "aerospace_systems": {
      "name": "Aerospace Systems Ltd",
      "paths": {
        "client_root": "{KSG_COMPANY_DIR}/Programs/Aerospace",
        "client_docs": "{KSG_COMPANY_DIR}/Programs/Aerospace/docs",
        "client_assets": "{KSG_COMPANY_DIR}/Programs/Aerospace/assets"
      }
    }
  },

  "internal_teams": {
    "platform_development": {
      "name": "Platform Development",
      "paths": {
        "team_docs": "{KSG_COMPANY_DIR}/Internal/PlatformDevelopment/docs"
      }
    },
    "engineering_tools": {
      "name": "Engineering Tools",
      "paths": {
        "team_docs": "{KSG_COMPANY_DIR}/Internal/EngineeringTools/docs"
      }
    }
  },

  "environments": {
    "medical_devices": {
      "type": "client",
      "client": "medical_devices",
      "description": "Medical Devices client environment"
    },
    "medical_devices_hardware": {
      "type": "client_group",
      "client": "medical_devices",
      "group": "hardware",
      "description": "Medical Devices hardware team environment"
    },
    "internal_tools": {
      "type": "internal_project",
      "team": "engineering_tools",
      "description": "Internal engineering tools environment"
    },
    "sandbox": {
      "type": "sandbox",
      "description": "Local sandbox and experimental projects"
    }
  },

  "templates": {
    "default_title_page": "{KSG_COMPANY_DIR}/SpecGen/templates/title_page.md",
    "default_end_page": "{KSG_COMPANY_DIR}/SpecGen/templates/end_page.md"
  },

  "assets": {
    "default_report_css": "{KSG_COMPANY_DIR}/SpecGen/assets/report_style.css",
    "default_bom_css": "{KSG_COMPANY_DIR}/SpecGen/assets/bom_style.css",
    "default_logo": "{KSG_COMPANY_DIR}/SpecGen/assets/logos/company_logo.png"
  }
}
```

## 10.7 Application Use

The application uses `kicad_specgen_company.json` to:

* Populate environment choices.
* Identify company, client, and client-group metadata.
* Locate shared templates and assets.
* Populate default project configuration values.
* Validate project references.
* Provide report metadata and template defaults.

---

# 11. File Chapter: `SpecGen/kicad_specgen_users.json`

## 11.1 Purpose

`kicad_specgen_users.json` stores minimal user directory information used by SpecGen.

This file supports:

* User selection.
* Report attribution.
* Environment filtering.
* Basic permissions for shared SpecGen configuration.
* User-owned resource folders.

It is not intended to be a full HR database.

## 11.2 Location

The file is located at:

```text
{KSG_COMPANY_DIR}/SpecGen/kicad_specgen_users.json
```

## 11.3 Ownership

This file is owned by SpecGen.

For a professional workflow, it may be stored in a shared Git repository.

For a standalone workflow, it may be stored in a local user folder.

## 11.4 Recommended User Fields

Recommended user fields:

| Field            | Description                                                                       |
| ---------------- | --------------------------------------------------------------------------------- |
| `worker_id`      | Internal employee, contractor, or local user identifier.                          |
| `display_name`   | User-facing display name.                                                         |
| `preferred_name` | Preferred first name.                                                             |
| `family_name`    | Last/family name.                                                                 |
| `email`          | Work or preferred contact email.                                                  |
| `department`     | Department or organization group.                                                 |
| `team`           | Team name.                                                                        |
| `job_title`      | Role or title used in reports.                                                    |
| `worker_type`    | Optional classification such as `employee`, `contractor`, `external`, or `hobby`. |
| `active`         | Boolean indicating whether the user profile is active.                            |
| `is_admin`       | Boolean indicating whether the user can modify shared SpecGen configuration.      |
| `clients`        | Optional list of client IDs associated with the user.                             |
| `internal_teams` | Optional list of internal team IDs associated with the user.                      |
| `paths`          | Optional user path references using local tokens.                                 |

## 11.5 Example

```json
{
  "schema_version": 1,

  "users": [
    {
      "worker_id": "12345",
      "display_name": "John Smith",
      "preferred_name": "John",
      "family_name": "Smith",
      "email": "john.smith@advancedeng.com",
      "department": "Hardware Engineering",
      "team": "Power Electronics",
      "job_title": "Senior Electrical Engineer",
      "worker_type": "employee",
      "active": true,
      "is_admin": true,
      "clients": [
        "medical_devices",
        "aerospace_systems"
      ],
      "internal_teams": [
        "engineering_tools"
      ],
      "paths": {
        "user_common": "{KSG_USER_COMMON_DIR}",
        "user_templates": "{KSG_USER_SPECGEN_DIR}/templates",
        "user_reports": "{KSG_USER_SPECGEN_DIR}/reports",
        "user_assets": "{KSG_USER_SPECGEN_DIR}/assets"
      }
    },

    {
      "worker_id": "23456",
      "display_name": "Jane Doe",
      "preferred_name": "Jane",
      "family_name": "Doe",
      "email": "jane.doe@advancedeng.com",
      "department": "Product Development",
      "team": "Systems",
      "job_title": "Engineering Manager",
      "worker_type": "employee",
      "active": true,
      "is_admin": false,
      "clients": [
        "industrial_controls",
        "energy_systems"
      ],
      "internal_teams": [
        "platform_development"
      ],
      "paths": {
        "user_common": "{KSG_USER_COMMON_DIR}"
      }
    }
  ]
}
```

## 11.6 Application Use

The application uses `kicad_specgen_users.json` to:

* Identify the active user.
* Populate report author fields.
* Filter available client or internal environments.
* Determine whether the user can edit shared configuration.
* Locate user-specific templates and assets through token references.

---

# 12. File Chapter: Project `.kicad_specgen`

## 12.1 Purpose

The project `.kicad_specgen` file is the SpecGen project/session file.

Opening this file is equivalent to opening a SpecGen project.

It stores project-specific SpecGen state and recipe data.

It does not store local absolute token definitions.

## 12.2 Location

A project `.kicad_specgen` file must be stored under the KiCad project-local `specgen/` folder:

```text
<KICAD_PROJECT_DIR>/specgen/<name>.kicad_specgen
```

When opened, the application derives:

```text
SPECGEN_PROJECT_FILE     = opened .kicad_specgen file
KSG_PROJECT_SPECGEN_DIR  = parent folder of SPECGEN_PROJECT_FILE
KICAD_PROJECT_DIR        = parent folder of KSG_PROJECT_SPECGEN_DIR
```

## 12.3 Ownership

This file is owned by SpecGen and belongs to the KiCad project.

It may be committed with the KiCad project repository.

It should be portable between machines.

It should store token references, not local absolute path definitions.

## 12.4 Required Contents - Under Construction

Recommended top-level sections:

| Section         | Purpose                                           |
| --------------- | ------------------------------------------------- |
| `[workspace]`   | Selected environment and workspace mode.          |
| `[project]`     | Project metadata and KiCad project identity.      |
| `[files]`       | Tokenized project path references.                |
| `[variables]`   | Custom user/project variables.                    |
| `[jobset]`      | Active jobset reference and destination metadata. |
| `[report]`      | Report recipe, page order, output settings.       |
| `[fabrication]` | FAB package settings.                             |
| `[ui]`          | Optional project UI state.                        |

## 12.5 Example

```json
TODO - Change this from TOML to JSON, this example is not complete and lacks

schema_version = 1

[workspace]
mode = "repo"
environment = "medical_devices"

[project]
name = "BoardA"
display_name = "Medical Devices BoardA"
document_number = "AE-MD-BA-001"
revision = "Rev B"

[files]
jobset = "{KSG_PROJECT_SPECGEN_DIR}/release_default.kicad_jobset"
logo = "{KSG_COMPANY_DIR}/SpecGen/assets/logos/company_logo.png"
report_css = "{KSG_COMPANY_DIR}/SpecGen/assets/report_style.css"
bom_css = "{KSG_COMPANY_DIR}/SpecGen/assets/bom_style.css"
title_page = "{KSG_COMPANY_DIR}/SpecGen/templates/title_page.md"
end_page = "{KSG_COMPANY_DIR}/SpecGen/templates/end_page.md"
background_notes = "{KICAD_PROJECT_DIR}/background/release_notes.md"

[variables.custom]
TEST_LEVEL = "Engineering Release"
CUSTOMER_RELEASE = "true"

[jobset]
active_jobset = "{KSG_PROJECT_SPECGEN_DIR}/release_default.kicad_jobset"
stop_on_error = true

[jobset.destinations.sch_pdf]
selected = true
heading_override = "Schematics"
notes = "Used in report."

[jobset.destinations.bom_csv]
selected = true
heading_override = "Bill of Materials"
notes = "Used in Report and FAB package."

[report]
output = "{KICAD_PROJECT_DIR}/report/BoardA_release_report.pdf"

[report.pages]
order = [
  "title_page",
  "sch_pdf",
  "bom_csv",
  "end_page"
]

[fabrication]
output_dir = "{KICAD_PROJECT_DIR}/FAB/release_default"
create_zip = true
create_checksums = true
```

## 12.6 Application Use

The application uses the project `.kicad_specgen` file to:

* Open and restore a SpecGen project.
* Determine the selected environment.
* Locate the active jobset.
* Load project metadata.
* Load custom variables.
* Store jobset destination overrides.
* Store report recipe and page order.
* Store FAB packaging settings.
* Save reproducible project release configuration.

---

# 13. File Chapter: KiCad `.kicad_pro`

## 13.1 Purpose

The `.kicad_pro` file is the KiCad project file.

SpecGen reads this file to validate the KiCad project and extract project text variables.

## 13.2 Ownership

This file is owned by KiCad.

SpecGen shall not modify this file.

## 13.3 Application Use

SpecGen uses the `.kicad_pro` file to:

* Confirm the active KiCad project.
* Load read-only KiCad project text variables.
* Populate the Variables tab.
* Provide project data for report templates.
* Run `kicad-cli jobset run`.

---

# 14. File Chapter: KiCad `.kicad_jobset`

## 14.1 Purpose

The `.kicad_jobset` file defines KiCad jobset destinations and generated output files.

SpecGen uses this file to run KiCad output generation.

## 14.2 Location

A project’s active `.kicad_jobset` file is usually stored under:

```text
{KSG_PROJECT_SPECGEN_DIR}/<jobset_name>.kicad_jobset
```

It may also be selected from another tokenized path if the project configuration allows it.

## 14.3 Ownership

This file is owned by KiCad.

SpecGen shall treat it as read-only by default.

SpecGen-specific destination notes, heading overrides, and selections shall be stored in the project `.kicad_specgen` file, keyed by destination ID.

## 14.4 Application Use

SpecGen uses `.kicad_jobset` files to:

* Parse jobset destinations.
* Display destination IDs and descriptions.
* Run all destinations.
* Run selected destinations by destination ID when supported.
* Generate source output files for the Results, Report, and Fabrication workflows.
* Determine or validate jobset output folders.

---

# 15. Company/User Storage Structure

SpecGen uses a common root location for company, user, and shared SpecGen files.

The local token for this location is:

```text
KSG_COMPANY_DIR
```

`KSG_COMPANY_DIR` identifies the root location that contains the shared or standalone `SpecGen/` folder.

This location may be:

* A Git repository root in professional/repository mode.
* A local standalone folder in hobby/standalone mode.
* A shared company folder.
* A company-controlled repository checkout.
* A local personal SpecGen workspace.

Expected structure:

```text
<KSG_COMPANY_DIR>/
├─ path/to/kicad/libraries/
└─ SpecGen/
   ├─ kicad_specgen_company.json
   ├─ kicad_specgen_users.json
   ├─ docs/
   ├─ templates/
   ├─ assets/
   └─ Users/
      └─ <worker_id>/
         ├─ common/
         ├─ reports/
         ├─ templates/
         └─ assets/
```

In standalone mode, `KSG_COMPANY_DIR` may point to a local user-controlled folder.

Example:

```text
/Users/john/Library/Preferences/kicad/9.0/SpecGenData
```

In repo mode, `KSG_COMPANY_DIR` may point to a Git repository root.

Example:

```text
/Users/john/Engineering/CompanyRepo
```

---

# 16. Setup Process Requirements - TODO - Under Construction

## 16.1 Initial Setup Workflow

During setup, the user is asked to identify or create a SpecGen company/user storage location.

The setup process shall:

1. Locate the SpecGen application repository.
2. Locate the KiCad user configuration folder.
3. Locate or create `kicad_specgen_local.json`.
4. Ask whether an existing SpecGen company/user storage location exists.
5. Allow the user to browse to `KSG_COMPANY_DIR`.
6. Verify that the location contains or can contain a valid `SpecGen/` folder.
7. Load company information if available.
8. Load user information if available.
9. Populate setup fields automatically from discovered data.
10. Ask to Create, Remove, Update and Company and/or User and/or Client data
11. Create, remove, or update local machine configuration.

## 16.2 Existing Company/User Storage Location

If a valid `KSG_COMPANY_DIR` exists:

* Load `{KSG_COMPANY_DIR}/SpecGen/kicad_specgen_company.json`.
* Load `{KSG_COMPANY_DIR}/SpecGen/kicad_specgen_users.json`.
* Load any matching user profile.
* Populate company, client, team, and project information automatically.
* Populate user information automatically when available.
* Generate local machine configuration.
* Store `KSG_COMPANY_DIR` in `kicad_specgen_local.json`.

## 16.3 New Company/User Storage Location

If no company/user storage location exists, setup shall collect:

* Company or standalone workspace information.
* Optional client information.
* Optional team information.
* Minimal user information.
* Shared asset locations.
* Shared documentation locations.
* Template locations.

After collection, the user shall choose whether to:

```text
Create Shared SpecGen Storage
```

or:

```text
Use Standalone Local Storage
```

Requirements:

* Verify that the target location is writable.
* Create the required `SpecGen/` folder structure.
* Generate `kicad_specgen_company.json`.
* Generate `kicad_specgen_users.json`.
* Generate local machine configuration.

## 16.4 Deferred Setup

Users may skip portions of setup.

Company, client, team, and user information must remain editable through the application after setup completes.

---

# 17. Application Validation Requirements

Validation should produce clear user-facing messages.

Validation should not show raw stack traces for normal user errors.

Validation shall check:

```text
kicad_specgen_local.json exists or can be created
schema_version values are supported
required local tokens exist
local token values are absolute paths
KSG_COMPANY_DIR exists or can be created
SpecGen company/user files exist or can be created
active_user exists in kicad_specgen_users.json
active_environment exists in kicad_specgen_company.json
recent project paths are valid or can be reported missing
project .kicad_specgen file is under a specgen folder
KSG_PROJECT_SPECGEN_DIR can be derived
KICAD_PROJECT_DIR can be derived
active .kicad_pro exists
active .kicad_jobset exists when needed
project token references resolve
company token references resolve
user token references resolve
custom variable names are valid
```

Missing-token validation shall offer a repair path.

File-writing validation shall warn before overwrite.

If modifying `kicad_common.json`, SpecGen must create a timestamped backup first.

---

# 18. Implementation Requirements for AI-Assisted Development

The implementation shall keep configuration loading and token resolution centralized.

Required core modules:

```text
core/
  platform_paths.py
  specgen_local_config.py
  specgen_company_config.py
  specgen_user_config.py
  project_config.py
  token_resolver.py
  validators.py
  file_ops.py
  logging_utils.py
```

UI code shall not independently parse or resolve configuration files.

The GUI shall call shared services for:

* Loading config files.
* Saving config files.
* Resolving token references.
* Validating paths.
* Reporting missing tokens.
* Updating recent projects.
* Deriving project runtime tokens.

The application shall treat each configuration file according to its ownership rules.

Summary Summary of Files:

```text
kicad_specgen_local.json
  location:{KICAD_COMMON_DIR}/kicad_specgen_local.json
    Windows:
      Define Token:KICAD_COMMON_DIR=%APPDATA%\KiCad\9.0\kicad_specgen_local.json
    Linux:
      Define Token:KICAD_COMMON_DIR=~/.config/kicad/9.0/kicad_specgen_local.json
    macOS:
      Define Token:KICAD_COMMON_DIR=~/Library/Preferences/kicad/9.0/kicad_specgen_local.json
    Where 9.0 is the KiCad configuration version.
  Define Token:KSG_SPECGEN_LOCAL_FILE={KICAD_COMMON_DIR}/kicad_specgen_local.json
  File Format:JSON
  Owned by:SpecGen
  Short Description:
    Local machine state history and absolute path token definitions.

kicad_specgen_company.json
  location:{KSG_COMPANY_DIR}/SpecGen/kicad_specgen_company.json
  Define Token:KSG_SPECGEN_COMPANY_FILE={KSG_COMPANY_DIR}/SpecGen/kicad_specgen_company.json
  File Format:JSON
  Owned by:SpecGen
  Short Description:
    Shared company/client/team data and relative tokenized path references.
    EX: {KSG_COMPANY_COMMON}=assets/latest
    Where the absoulte path is {KSG_COMPANY_DIR}/{KSG_COMPANY_COMMON} 

kicad_specgen_users.json
  location:{KSG_COMPANY_DIR}/SpecGen/kicad_specgen_users.json 
  Define Token:KSG_USERS_FILE={KSG_COMPANY_DIR}/SpecGen/kicad_specgen_users.json
  File Format:JSON
  Owned by:SpecGen
  Short Description:
    Minimal user directory and workderId used to identify user path references.
    EX: workerId=1234
    KSG_USER_SPECGEN_DIR={KSG_COMPANY_DIR}/Users/1234
    KSG_USER_COMMON_DIR={KSG_USER_SPECGEN_DIR}/common

Project .kicad_pro
  location: {KICAD_PROJECT_DIR}/<project_name>.kicad_pro
  Define Token: KICAD_PROJECT_FILE={KICAD_PROJECT_DIR}/<project_name>.kicad_pro
  File Format:JSON
  Owned by:KiCad
  Short Description:
    The KiCad main project file that stores project-level settings including the text_variables section — key/value pairs such as REV, DATE, and PART_NUMBER — that are substituted into schematic, pcb layouts, and used by SpecGen as read-only token variables.

Project .kicad_specgen
  location: {KICAD_PROJECT_DIR}/specgen/<specgen_project>.kicad_specgen
  Define Token:SPECGEN_PROJECT_FILE={KSG_PROJECT_SPECGEN_DIR}/<specgen_project>.kicad_specgen
  File Format:JSON
  Owned by:SpecGen
  Short Description:
    Contains the SpecGen full project state: report recipes, report/FAB settings, and tokenized path report files, elements, and variables. 
    The idea is that if the KiCad Project is updated and then the user just needs to re-run the jobset and re-run the report generation (run all)
      If .kicad_jobset contains the same jobs and outputs to the same location, but has more jobs, the report generation can still run.
      If .kicad_jobset is missing jobs or outputs are in different locations, the report generation will not run, the setup needs to update and flag differences

kicad_common.json
  location: {KICAD_COMMON_DIR}/kicad_common.json
  Define Token:KICAD_COMMON_FILE={KICAD_COMMON_DIR}/kicad_common.json
  File Format:JSON
  Owned by:KiCad
  Short Description:
    KiCad application preferences file, storing global settings such as environment variable definitions, local file paths, and UI preferences that apply across all KiCad projects on the machine.

.kicad_jobset
  location: <any tokenized local path>/<relative path>/<jobset_name>.kicad_jobset
  File Format:JSON
  Owned by:KiCad
  Short Description:
    KiCad-owned jobset input, read-only by default. Defines an ordered sequence of kicad-cli export jobs — such as schematic PDF, PCB Gerbers, BOM, and DRC report — that are run together in a single command against a KiCad project.
    Outputs files in JOBSET_OUTPUT_DIR={KICAD_PROJECT_DIR}/{JOBSET_DIR}
    Where JOBSET_DIR is defined in the output section.  EX: 
    {
      "jobs": [...],
      "meta": {...},
      "outputs": [...
        {
          "settings": { "output_path": "{JOBSET_DIR}" },
        }
        ...
      ]
    }
```
