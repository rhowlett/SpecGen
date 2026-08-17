# KiCad SpecGen JSON Reference

## Table of Contents

Introduction to `kicad_specgen.json`
File location
File format
Configuration object
Top-level members
Tools object
Setup object
Last session object
Environment objects
Token definitions
Required stored tokens
Optional stored tokens
Protected derived tokens
Token resolution
Effective token table
Missing token handling
Default support files
Validation
Full example
Minimum valid configuration
Stage 1 requirements

---

# KiCad SpecGen JSON Reference Manual

This document describes the `kicad_specgen.json` configuration file used by KiCad SpecGen.

`kicad_specgen.json` is a local-machine JSON configuration file. It stores setup state, external tool paths, named environments, and local absolute path definitions for portable SpecGen tokens.

`kicad_specgen.json` is not the project report recipe. Project-specific state is stored in the project `.kicad_specgen` file.

---

## Software and Documentation Version

This reference is written for KiCad SpecGen Stage 1.

The intended KiCad target is KiCad 9.0 or later.

The intended Python target is Python 3.10 or later.

Schema version described in this document:

```text
1
```

---

# Introduction to `kicad_specgen.json`

KiCad SpecGen uses two local configuration files:

```text
kicad_common.json
kicad_specgen.json
```

`kicad_common.json` is owned by KiCad.

`kicad_specgen.json` is owned by KiCad SpecGen.

SpecGen may read KiCad environment variables from `kicad_common.json`, but SpecGen-specific setup information is stored in `kicad_specgen.json`.

The most important role of `kicad_specgen.json` is token definition.

SpecGen separates path data into two categories:

```text
Token definitions
  Absolute paths on the local machine.

Token references
  Portable tokenized paths used by project .kicad_specgen files.
```

Token definitions belong in:

```text
kicad_specgen.json
kicad_common.json
```

Token references belong in:

```text
<KiCad project folder>/specgen/<name>.kicad_specgen
```

Project `.kicad_specgen` files should not contain machine-specific absolute path definitions.

---

# File location

`kicad_specgen.json` is stored in the KiCad user configuration area, near `kicad_common.json`.

Typical locations:

```text
macOS:
  ~/Library/Preferences/kicad/kicad_specgen.json

Ubuntu/Linux:
  <KiCad user configuration folder>/kicad_specgen.json

Windows:
  <KiCad user configuration folder>/kicad_specgen.json
```

The exact platform location is resolved by the setup module.

The main application should not hard-code these paths.

---

# File format

`kicad_specgen.json` is a JSON file.

The file must contain a top-level JSON object.

Usage:

```text
kicad_specgen.json
  {
    "schema_version": INTEGER,
    "active_environment": ENVIRONMENT_NAME,
    "tools": TOOLS_OBJECT,
    "setup": SETUP_OBJECT,
    "last_session": LAST_SESSION_OBJECT,
    "environments": ENVIRONMENTS_OBJECT
  }
```

Required members:

```text
schema_version
active_environment
tools
setup
last_session
environments
```

Unknown top-level members should produce validation warnings.

---

# Configuration object

A complete `kicad_specgen.json` file has this general structure:

```json
{
  "schema_version": 1,
  "active_environment": "internal",

  "tools": {
    "kicad_cli": "/absolute/path/to/kicad-cli",
    "kicad_cli_source": "detected_macos_app",
    "kicad_version": "9.0.x"
  },

  "setup": {
    "setup_complete": true,
    "last_setup_run": "2026-05-30T12:34:56",
    "last_setup_platform": "macos",
    "dependency_stage": "stage1",
    "specgen_support_root": "/absolute/path/to/KiCad/SpecGen"
  },

  "last_session": {
    "environment": "internal",
    "specgen_project": "/absolute/path/to/project/specgen/release.kicad_specgen",
    "last_opened_at": "2026-05-30T14:10:00"
  },

  "environments": {
    "internal": {
      "mode": "repo",
      "description": "Internal engineering workspace",
      "tokens": {},
      "defaults": {},
      "validation": {}
    }
  }
}
```

---

# Top-level members

## `schema_version`

The `schema_version` member identifies the schema version of `kicad_specgen.json`.

Usage:

```text
"schema_version": INTEGER
```

Required value for this document:

```json
"schema_version": 1
```

If the schema version is missing, the file is invalid.

If the schema version is newer than the application supports, SpecGen must stop loading the file and show a clear error.

If the schema version is older than the application supports, SpecGen may offer to migrate the file.

---

## `active_environment`

The `active_environment` member stores the default named environment.

Usage:

```text
"active_environment": ENVIRONMENT_NAME
```

Example:

```json
"active_environment": "client_a"
```

The value must match a key in the `environments` object.

The active environment is used when:

```text
creating a new project .kicad_specgen file
opening a project file that does not specify an environment
resolving tokens during setup validation
showing the default Project tab environment
```

---

## `tools`

The `tools` object stores local external tool paths.

Usage:

```text
"tools": {
  "kicad_cli": PATH,
  "kicad_cli_source": SOURCE,
  "kicad_version": VERSION
}
```

Required members:

```text
kicad_cli
```

Optional members:

```text
kicad_cli_source
kicad_version
```

---

## `setup`

The `setup` object stores setup and bootstrap information.

Usage:

```text
"setup": {
  "setup_complete": BOOLEAN,
  "last_setup_run": TIMESTAMP,
  "last_setup_platform": PLATFORM,
  "dependency_stage": STAGE,
  "specgen_support_root": PATH
}
```

Required members:

```text
setup_complete
dependency_stage
specgen_support_root
```

Optional members:

```text
last_setup_run
last_setup_platform
```

---

## `last_session`

The `last_session` object stores the last opened SpecGen project file.

Usage:

```text
"last_session": {
  "environment": ENVIRONMENT_NAME,
  "specgen_project": PATH,
  "last_opened_at": TIMESTAMP
}
```

Required members:

```text
environment
specgen_project
```

Optional members:

```text
last_opened_at
```

---

## `environments`

The `environments` object stores named SpecGen environments.

Usage:

```text
"environments": {
  ENVIRONMENT_NAME: ENVIRONMENT_OBJECT
}
```

Each environment defines a set of local absolute paths for token resolution.

Example:

```json
"environments": {
  "internal": {
    "mode": "repo",
    "description": "Internal engineering workspace",
    "tokens": {
      "KSG_DIR": "/Users/example/Documents/GitHub",
      "KSG_WORKSPACE": "/Users/example/Documents/GitHub/advanced_engineering",
      "KSG_SPECGEN_DIR": "/Users/example/Library/Preferences/kicad/SpecGen",
      "KSG_SPECGEN_COMMON": "/Users/example/Library/Preferences/kicad/SpecGen/common"
    }
  }
}
```

---

# Tools object

The `tools` object stores external executable paths needed by SpecGen.

## `tools.kicad_cli`

The `kicad_cli` member stores the absolute path to `kicad-cli`.

Usage:

```text
"kicad_cli": PATH
```

Example:

```json
"kicad_cli": "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"
```

This value should be an absolute path.

On macOS, setup should check the standard KiCad application path:

```text
/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
```

If `kicad-cli` is found outside the shell `PATH`, setup should save the absolute path in `kicad_specgen.json`.

Creating a symbolic link is optional and should not be the default behavior.

---

## `tools.kicad_cli_source`

The `kicad_cli_source` member records how the `kicad-cli` path was found.

Usage:

```text
"kicad_cli_source": SOURCE
```

Recommended values:

```text
path
detected_macos_app
user_selected
missing
```

Example:

```json
"kicad_cli_source": "detected_macos_app"
```

---

## `tools.kicad_version`

The `kicad_version` member records the detected KiCad CLI version.

Usage:

```text
"kicad_version": VERSION
```

Example:

```json
"kicad_version": "9.0.x"
```

This value may be populated by running:

```text
kicad-cli version
```

The field is useful for diagnostics but should not be required to open the application.

---

# Setup object

The `setup` object stores bootstrap metadata.

## `setup.setup_complete`

The `setup_complete` member indicates whether setup has completed successfully.

Usage:

```text
"setup_complete": BOOLEAN
```

Example:

```json
"setup_complete": true
```

If this value is false or missing, the application may prompt the user to run setup or continue with limited functionality.

---

## `setup.last_setup_run`

The `last_setup_run` member stores the timestamp of the last setup run.

Usage:

```text
"last_setup_run": TIMESTAMP
```

Example:

```json
"last_setup_run": "2026-05-30T12:34:56"
```

---

## `setup.last_setup_platform`

The `last_setup_platform` member stores the platform setup module last used.

Usage:

```text
"last_setup_platform": PLATFORM
```

Recommended values:

```text
ubuntu
macos
windows
unknown
```

Example:

```json
"last_setup_platform": "macos"
```

---

## `setup.dependency_stage`

The `dependency_stage` member stores the dependency group last installed.

Usage:

```text
"dependency_stage": STAGE
```

Recommended values:

```text
stage1
stage2
report
fabrication
dev
full
```

Example:

```json
"dependency_stage": "stage1"
```

---

## `setup.specgen_support_root`

The `specgen_support_root` member stores the root folder for local SpecGen support files.

Usage:

```text
"specgen_support_root": PATH
```

Example:

```json
"specgen_support_root": "/Users/example/Library/Preferences/kicad/SpecGen"
```

This folder is used for default templates, common report files, and standalone support files.

---

# Last session object

The `last_session` object stores the last opened project `.kicad_specgen` file.

## `last_session.environment`

The `environment` member stores the environment used during the last session.

Usage:

```text
"environment": ENVIRONMENT_NAME
```

Example:

```json
"environment": "client_a"
```

The value should match a key in the `environments` object.

---

## `last_session.specgen_project`

The `specgen_project` member stores the absolute path to the last opened project `.kicad_specgen` file.

Usage:

```text
"specgen_project": PATH
```

Example:

```json
"specgen_project": "/Users/example/Projects/BoardA/specgen/release.kicad_specgen"
```

If no project has been opened yet, this may be an empty string:

```json
"specgen_project": ""
```

Opening this file restores the full SpecGen project state.

---

## `last_session.last_opened_at`

The `last_opened_at` member stores the timestamp of the last opened project.

Usage:

```text
"last_opened_at": TIMESTAMP
```

Example:

```json
"last_opened_at": "2026-05-30T14:10:00"
```

---

# Environment objects

Each named environment defines a group of token definitions.

Usage:

```text
"environments": {
  ENVIRONMENT_NAME: {
    "mode": MODE,
    "description": DESCRIPTION,
    "tokens": TOKEN_OBJECT,
    "defaults": DEFAULTS_OBJECT,
    "validation": VALIDATION_OBJECT
  }
}
```

Required members:

```text
mode
tokens
```

Optional members:

```text
description
defaults
validation
```

---

## Environment name

Environment names are user-facing identifiers.

Examples:

```text
internal
client_a
client_b
standalone_default
```

Environment names should be lowercase with underscores.

Recommended validation regex:

```text
^[a-z][a-z0-9_]*$
```

---

## `mode`

The `mode` member defines the environment type.

Usage:

```text
"mode": MODE
```

Allowed values:

```text
repo
standalone
```

### `repo`

Use `repo` for Git-managed workspaces.

A repo environment normally defines:

```text
KSG_DIR
KSG_WORKSPACE
KSG_SPECGEN_DIR
KSG_SPECGEN_COMMON
```

### `standalone`

Use `standalone` for independent KiCad projects that are not managed as part of a shared Git workspace.

A standalone environment normally defines:

```text
KSG_SPECGEN_DIR
KSG_SPECGEN_COMMON
```

---

## `description`

The `description` member gives a human-readable label.

Usage:

```text
"description": DESCRIPTION
```

Example:

```json
"description": "Client A isolated hardware workspace"
```

---

## `tokens`

The `tokens` member stores absolute local path definitions.

Usage:

```text
"tokens": {
  TOKEN_NAME: ABSOLUTE_PATH
}
```

Example:

```json
"tokens": {
  "KSG_DIR": "/Users/example/Documents/GitHub",
  "KSG_WORKSPACE": "/Users/example/Documents/GitHub/advanced_engineering",
  "KSG_SPECGEN_DIR": "/Users/example/Library/Preferences/kicad/SpecGen",
  "KSG_SPECGEN_COMMON": "/Users/example/Library/Preferences/kicad/SpecGen/common"
}
```

All paths in `tokens` must be absolute paths.

Token values should not contain token references.

Correct:

```json
"KSG_SPECGEN_COMMON": "/Users/example/Library/Preferences/kicad/SpecGen/common"
```

Avoid:

```json
"KSG_SPECGEN_COMMON": "{KSG_SPECGEN_DIR}/common"
```

---

## `defaults`

The `defaults` object stores default behavior for support-file handling.

Usage:

```text
"defaults": {
  "copy_missing_support_files": BOOLEAN,
  "overwrite_existing_support_files": BOOLEAN
}
```

Optional members:

```text
copy_missing_support_files
overwrite_existing_support_files
```

Example:

```json
"defaults": {
  "copy_missing_support_files": true,
  "overwrite_existing_support_files": false
}
```

---

## `validation`

The `validation` object stores environment validation behavior.

Usage:

```text
"validation": {
  "require_existing_paths": BOOLEAN,
  "allow_missing_optional_tokens": BOOLEAN
}
```

Optional members:

```text
require_existing_paths
allow_missing_optional_tokens
```

Example:

```json
"validation": {
  "require_existing_paths": true,
  "allow_missing_optional_tokens": false
}
```

---

# Token definitions

Token definitions are absolute local path values.

They are stored in:

```text
kicad_specgen.json
kicad_common.json
```

Token references are portable path strings used in project `.kicad_specgen` files.

Example token reference:

```text
{KSG_SPECGEN_COMMON}/report_style.css
```

Example token definition:

```json
"KSG_SPECGEN_COMMON": "/Users/example/Library/Preferences/kicad/SpecGen/common"
```

---

# Token naming rules

SpecGen reserves the `KSG_*` token namespace for portable KiCad SpecGen workflow paths.

Stored token names must follow:

```text
^KSG_[A-Z0-9_]+$
```

Rules:

```text
Token names must be uppercase.
Token names must start with KSG_.
Token names may contain letters, numbers, and underscores.
Token names must not contain spaces.
Token names should describe a folder or root path.
Token names should not describe a single normal report page.
```

---

# Required stored tokens

## Required for all environments

All environments must define:

```text
KSG_SPECGEN_DIR
KSG_SPECGEN_COMMON
```

### `KSG_SPECGEN_DIR`

Root folder for SpecGen default/support files.

Expected contents:

```text
default.kicad_specgen
default_template.kicad_jobset
common/
```

Example:

```json
"KSG_SPECGEN_DIR": "/Users/example/Library/Preferences/kicad/SpecGen"
```

---

### `KSG_SPECGEN_COMMON`

Root folder for common report assets.

Expected contents:

```text
report_style.css
bom_style.css
title_page.html
end_page.html
logos/
templates/
```

Example:

```json
"KSG_SPECGEN_COMMON": "/Users/example/Library/Preferences/kicad/SpecGen/common"
```

---

## Required for repo environments

Repo environments must define:

```text
KSG_DIR
KSG_WORKSPACE
KSG_SPECGEN_DIR
KSG_SPECGEN_COMMON
```

### `KSG_DIR`

Top-level directory where Git repositories are grouped.

Example:

```json
"KSG_DIR": "/Users/example/Documents/GitHub"
```

---

### `KSG_WORKSPACE`

Root of the active hardware workspace.

Example:

```json
"KSG_WORKSPACE": "/Users/example/Documents/GitHub/advanced_engineering"
```

This may contain project repositories, KiCad libraries, templates, shared documentation, and other engineering assets.

---

## Required for standalone environments

Standalone environments must define:

```text
KSG_SPECGEN_DIR
KSG_SPECGEN_COMMON
```

Standalone environments do not require:

```text
KSG_DIR
KSG_WORKSPACE
```

---

# Optional stored tokens

Named environments may define additional `KSG_*` tokens for company, client, or workflow-specific folders.

Examples:

```text
KSG_CLIENT_DOCS
KSG_CLIENT_ASSETS
KSG_COMPANY_DOCS
KSG_COMPANY_LOGOS
KSG_RELEASE_TEMPLATES
KSG_MECH_EXPORTS
KSG_SHARED_REPORTS
KSG_LIB
KSG_SYMBOLS
KSG_FOOTPRINTS
KSG_3DMODELS
KSG_TEMPLATES
```

Optional tokens should point to folders or root paths.

---

# Protected derived tokens

Some tokens are valid in project `.kicad_specgen` files but must not be stored in `kicad_specgen.json`.

These are derived by SpecGen when a project is opened.

Protected derived tokens:

```text
SPECGEN_PROJECT_FILE
KICAD_SPECGEN_DIR
KICAD_PROJECT_DIR
GIT_PROJECT_DIR
JOBSET_OUTPUT_DIR
FAB_OUTPUT_DIR
```

If these tokens are found inside an environment’s `tokens` object, validation should warn and ignore the stored value.

---

## `SPECGEN_PROJECT_FILE`

The opened project `.kicad_specgen` file.

Derived from the file the user opens.

Example:

```text
/Repo/projects/Power/kicad/BoardA/specgen/release.kicad_specgen
```

---

## `KICAD_SPECGEN_DIR`

The project-local `specgen/` folder that contains the opened `.kicad_specgen` file.

Derived as:

```text
KICAD_SPECGEN_DIR = parent directory of SPECGEN_PROJECT_FILE
```

Example:

```text
/Repo/projects/Power/kicad/BoardA/specgen
```

---

## `KICAD_PROJECT_DIR`

The KiCad project/design folder containing the active `.kicad_pro` file.

Derived as:

```text
KICAD_PROJECT_DIR = parent directory of KICAD_SPECGEN_DIR
```

Example:

```text
/Repo/projects/Power/kicad/BoardA
```

---

## `GIT_PROJECT_DIR`

The project Git repository root.

In repo mode, this is derived by running Git root detection from `KICAD_PROJECT_DIR`.

In standalone mode, this defaults to:

```text
GIT_PROJECT_DIR = KICAD_PROJECT_DIR
```

If Git root detection fails in repo mode, SpecGen should show a validation warning.

---

## `JOBSET_OUTPUT_DIR`

Root output folder for the selected jobset.

Usually derived as:

```text
{KICAD_PROJECT_DIR}/jobset_output/<jobset_name>
```

The actual path may depend on the selected `.kicad_jobset`.

---

## `FAB_OUTPUT_DIR`

Default fabrication output folder.

Usually derived as:

```text
{KICAD_PROJECT_DIR}/FAB/<jobset_name>
```

The project `.kicad_specgen` file may later define a different tokenized FAB output path.

---

# Token resolution

When resolving token references, SpecGen builds an effective token table.

Resolution order:

```text
1. KiCad environment variables from kicad_common.json
2. Selected named environment tokens from kicad_specgen.json
3. Protected derived runtime tokens
```

Later sources override earlier sources.

Therefore:

```text
kicad_specgen.json environment tokens override kicad_common.json tokens.
protected derived runtime tokens override both.
```

This guarantees that project-local tokens such as `KICAD_PROJECT_DIR` and `SPECGEN_PROJECT_FILE` always come from the opened project file, not from machine configuration.

---

# Effective token table

The Project tab should display an effective token table.

Recommended columns:

```text
Token
Resolved Path
Source
Status
Notes
```

Example:

```text
Token                  Resolved Path                                      Source                    Status  Notes
KSG_DIR                /Users/example/Documents/GitHub                    kicad_common.json          OK
KSG_WORKSPACE          /Users/example/Clients/ClientA/hardware            kicad_specgen:client_a     OK      Overrides KiCad
KSG_SPECGEN_DIR        /Users/example/Library/Preferences/kicad/SpecGen   kicad_specgen:client_a     OK
KSG_SPECGEN_COMMON     /Users/example/Library/Preferences/kicad/SpecGen/common kicad_specgen:client_a OK
KICAD_PROJECT_DIR      /Users/example/.../BoardA                          derived                   OK      Protected
GIT_PROJECT_DIR        /Users/example/.../client_project_repo              derived                   OK      Git root
KSG_CLIENT_DOCS        /Users/example/Clients/ClientA/docs                 kicad_specgen:client_a     OK
```

The Project tab may also show a read-only table of raw KiCad `kicad_common.json` environment variables.

---

# Missing token handling

If a project `.kicad_specgen` references a token that cannot be resolved, SpecGen must not silently continue.

It should report:

```text
missing token name
selected environment
all project settings or files that reference the token
suggested repair action
```

User options:

```text
Add token to selected environment
Pick replacement file or folder
Skip affected item
Cancel open or import
```

If the user chooses to add the token, SpecGen updates:

```text
kicad_specgen.json -> environments.<environment>.tokens.<TOKEN_NAME>
```

The project `.kicad_specgen` file should remain portable.

---

# Default support files

SpecGen default support files are found using:

```text
{KSG_SPECGEN_DIR}
```

Common report assets are found using:

```text
{KSG_SPECGEN_COMMON}
```

Expected default files:

```text
{KSG_SPECGEN_DIR}/default.kicad_specgen
{KSG_SPECGEN_DIR}/default_template.kicad_jobset
{KSG_SPECGEN_COMMON}/report_style.css
{KSG_SPECGEN_COMMON}/bom_style.css
{KSG_SPECGEN_COMMON}/title_page.html
{KSG_SPECGEN_COMMON}/end_page.html
```

When creating a new project config, SpecGen should offer:

```text
Use defaults by reference
Copy defaults into {KICAD_SPECGEN_DIR}
Skip defaults and leave blank entries
```

If copying and the destination file already exists, prompt:

```text
Overwrite
Rename
Cancel
```

---

# Validation

`kicad_specgen.json` validation should check:

```text
schema_version exists
schema_version is supported
active_environment exists
active_environment exists in environments
tools exists
tools.kicad_cli exists or is marked missing
setup exists
last_session exists
environments exists
each environment has mode
each environment mode is repo or standalone
each environment has tokens
stored token names follow ^KSG_[A-Z0-9_]+$
stored token values are absolute paths
required tokens exist for the environment mode
required token paths exist
protected derived tokens are not stored in environment tokens
last_session.specgen_project is empty or points to an existing .kicad_specgen file
```

Protected derived tokens:

```text
SPECGEN_PROJECT_FILE
KICAD_SPECGEN_DIR
KICAD_PROJECT_DIR
GIT_PROJECT_DIR
JOBSET_OUTPUT_DIR
FAB_OUTPUT_DIR
```

---

# Examples

## Full example

```json
{
  "schema_version": 1,
  "active_environment": "client_a",

  "tools": {
    "kicad_cli": "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli",
    "kicad_cli_source": "detected_macos_app",
    "kicad_version": "9.0.x"
  },

  "setup": {
    "setup_complete": true,
    "last_setup_run": "2026-05-30T12:34:56",
    "last_setup_platform": "macos",
    "dependency_stage": "stage1",
    "specgen_support_root": "/Users/example/Library/Preferences/kicad/SpecGen"
  },

  "last_session": {
    "environment": "client_a",
    "specgen_project": "/Users/example/Clients/ClientA/hardware/controller_project/projects/Power/kicad/BoardA/specgen/release.kicad_specgen",
    "last_opened_at": "2026-05-30T14:10:00"
  },

  "environments": {
    "internal": {
      "mode": "repo",
      "description": "Internal hardware workspace",
      "tokens": {
        "KSG_DIR": "/Users/example/Documents/GitHub",
        "KSG_WORKSPACE": "/Users/example/Documents/GitHub/advanced_engineering",
        "KSG_SPECGEN_DIR": "/Users/example/Library/Preferences/kicad/SpecGen",
        "KSG_SPECGEN_COMMON": "/Users/example/Library/Preferences/kicad/SpecGen/common",
        "KSG_COMPANY_DOCS": "/Users/example/Documents/GitHub/advanced_engineering/docs",
        "KSG_LIB": "/Users/example/Documents/GitHub/advanced_engineering/lib/kicad",
        "KSG_SYMBOLS": "/Users/example/Documents/GitHub/advanced_engineering/lib/kicad/symbols",
        "KSG_FOOTPRINTS": "/Users/example/Documents/GitHub/advanced_engineering/lib/kicad/footprints",
        "KSG_3DMODELS": "/Users/example/Documents/GitHub/advanced_engineering/lib/kicad/3dmodels",
        "KSG_TEMPLATES": "/Users/example/Documents/GitHub/advanced_engineering/lib/kicad/templates"
      },
      "defaults": {
        "copy_missing_support_files": true,
        "overwrite_existing_support_files": false
      },
      "validation": {
        "require_existing_paths": true,
        "allow_missing_optional_tokens": true
      }
    },

    "client_a": {
      "mode": "repo",
      "description": "Client A isolated hardware workspace",
      "tokens": {
        "KSG_DIR": "/Users/example/Clients/ClientA",
        "KSG_WORKSPACE": "/Users/example/Clients/ClientA/hardware",
        "KSG_SPECGEN_DIR": "/Users/example/Library/Preferences/kicad/SpecGen/client_a",
        "KSG_SPECGEN_COMMON": "/Users/example/Library/Preferences/kicad/SpecGen/client_a/common",
        "KSG_CLIENT_DOCS": "/Users/example/Clients/ClientA/docs",
        "KSG_CLIENT_ASSETS": "/Users/example/Clients/ClientA/assets"
      },
      "defaults": {
        "copy_missing_support_files": true,
        "overwrite_existing_support_files": false
      },
      "validation": {
        "require_existing_paths": true,
        "allow_missing_optional_tokens": false
      }
    },

    "standalone_default": {
      "mode": "standalone",
      "description": "Default standalone KiCad project environment",
      "tokens": {
        "KSG_SPECGEN_DIR": "/Users/example/Library/Preferences/kicad/SpecGen",
        "KSG_SPECGEN_COMMON": "/Users/example/Library/Preferences/kicad/SpecGen/common"
      },
      "defaults": {
        "copy_missing_support_files": true,
        "overwrite_existing_support_files": false
      },
      "validation": {
        "require_existing_paths": true,
        "allow_missing_optional_tokens": true
      }
    }
  }
}
```

---

## Minimum valid configuration

```json
{
  "schema_version": 1,
  "active_environment": "standalone_default",

  "tools": {
    "kicad_cli": "/absolute/path/to/kicad-cli",
    "kicad_cli_source": "user_selected"
  },

  "setup": {
    "setup_complete": true,
    "dependency_stage": "stage1",
    "specgen_support_root": "/absolute/path/to/KiCad/SpecGen"
  },

  "last_session": {
    "environment": "standalone_default",
    "specgen_project": ""
  },

  "environments": {
    "standalone_default": {
      "mode": "standalone",
      "description": "Default standalone KiCad project environment",
      "tokens": {
        "KSG_SPECGEN_DIR": "/absolute/path/to/KiCad/SpecGen",
        "KSG_SPECGEN_COMMON": "/absolute/path/to/KiCad/SpecGen/common"
      },
      "defaults": {
        "copy_missing_support_files": true,
        "overwrite_existing_support_files": false
      },
      "validation": {
        "require_existing_paths": true,
        "allow_missing_optional_tokens": true
      }
    }
  }
}
```

---

# Stage 1 requirements

Stage 1 should implement enough of `kicad_specgen.json` to support:

```text
setup bootstrap
kicad-cli discovery
kicad_specgen.json create, load, and save
named environment creation and editing
token validation
missing-token resolution
last-session restore
Project tab environment selector
Project tab effective token table
```

Stage 1 does not require:

```text
jobset execution
report rendering
FAB packaging
full recipe import or export
```
