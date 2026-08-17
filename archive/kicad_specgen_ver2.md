# KiCad SpecGen - Current Architecture Understanding

## 1. Application model

KiCad "SpecGen" is a standalone Python application installed from a Git repo.

It runs in its own `.venv/` inside the SpecGen application repo.

It uses pip-installable packages only.

It does not depend on KiCad’s bundled Python environment or `pcbnew`.

KiCad integration is handled through:

* `kicad-cli`
* read-only parsing of KiCad JSON files
* read-only parsing of KiCad S-expression files where needed later

## 2. Setup model

The setup flow is part of Stage 1.

The top-level setup entry point is:

```text
setup.py
```

It detects the OS and dispatches to:

```text
setup_ubuntu.py
setup_macos.py
setup_windows.py
```

The setup scripts should share common utility modules with the GUI where practical. There should not be duplicate setup-only versions of token resolution, config parsing, logging, file copying, or KiCad environment validation.

Setup is normally run once, but it should be safe to rerun.

Setup responsibilities include:

* create/update `.venv/`
* install Stage 1 dependencies
* locate `kicad-cli`
* locate/read `kicad_common.json`
* locate/create/update `kicad_specgen.json`
* validate or create named SpecGen environments
* copy default SpecGen support files if missing
* back up `kicad_common.json` before modifying it
* log setup/bootstrap activity using shared logging helpers

On macOS, setup should assume kicad-cli is not in a shell path and is located in the Application folder here: /Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli

The SpecGen should prefer saving the absolute path in `kicad_specgen.json`

## 3. Stage files

Dependency and implementation stage docs are saved as Markdown requirement files.

Recommended files:

```text
requirements/
  stage1.md
  stage2.md
  report.md
  fabrication.md
  dev.md
  full.md
```

Each stage Markdown file includes both:

* dependency group
* stage deliverables and acceptance criteria

Current stage split:

```text
stage1.md       Project tab + Variables tab + basic Logs tab + setup bootstrap
stage2.md       Jobset tab + JS Results tab
report.md       Report generation and rendering pipeline
fabrication.md  FAB package generation
dev.md          Unit tests, fixtures, lint/type checks, developer tools
full.md         Full application install / all dependencies
```

## 4. Local machine files

### `kicad_common.json`

This file is owned by KiCad.

SpecGen can read it.

SpecGen may add missing `ION_*` variables during setup only if the user approves.

Before SpecGen writes to `kicad_common.json`, it must create a timestamped backup:

```text
kicad_common.json.bak_YYYYMMDD_HHMMSS
```

If existing `ION_*` variables differ from what the user selects in SpecGen, setup should not overwrite them automatically.

### `kicad_specgen.json`

This file is owned by SpecGen and stored in the same general KiCad user settings area as `kicad_common.json`.

It stores local-machine information, including:

* last opened SpecGen project file
* named SpecGen environments
* absolute local token definitions
* `kicad-cli` path
* standalone support folder location
* setup/bootstrap choices

This file may contain absolute paths because it is local to one user/machine.

Example shape:

```json
{
  "schema_version": 1,
  "active_environment": "client_a",
  "tools": {
    "kicad_cli": "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"
  },
  "last_session": {
    "environment": "client_a",
    "specgen_project": "/path/to/project/repo/path/to/board/specgen/release.kicad_specgen"
  },
  "environments": {
    "client_x": {
      "mode": "repo",
       "tokens": {
         "ION_PROJECT_DIR": "/absolute/path/to/client_x/project/git/repo"
         }
    "client_a": {
      "mode": "repo",
      "tokens": {
        "ION_DIR": "/absolute/path/to/specgen/app/repo/base",
        "ION_WORKSPACE": "/absolute/path/to/workspace",
        "ION_PROJECT_DIR": "/absolute/path/to/project/git/repo",
        "ION_SPECGEN_DIR": "/absolute/path/to/default/specgen/support/files",
        "ION_SPECGEN_COMMON": "/absolute/path/to/default/specgen/common/report/files", 
        "ION_CLIENT_DOCS": "/absolute/path/to/client/docs"
      }
    }
  }
}
```

## 5. Workspace modes

SpecGen supports two workflow modes:

```text
repo
standalone
```

### Repo mode

Repo mode is for shared/professional/multi-user projects.

The KiCad project is part of a Git-managed workspace.

The local machine path definitions live in:

```text
kicad_common.json
kicad_specgen.json
```

The project `<kicad_project_path>/specgen/<file>.kicad_specgen` file should not store absolute paths.

### Standalone mode

Standalone mode is for a KiCad project that is not part of a shared Git workspace.

In standalone mode, the project can still use tokenized paths, but it does not require `ION_DIR`, `ION_WORKSPACE`, or other repo-style tokens.

Standalone defaults and support files should live in a SpecGen folder under the KiCad user settings area unless the user selects another location.

## 6. Named environments

`kicad_specgen.json` supports multiple named environments.

This is important for professionals with multiple clients or separated workspaces.

Examples:

```text
internal
client_a
client_b
standalone_default
```

A named environment contains local absolute path definitions.

The project `.kicad_specgen` file selects an environment by name, but does not define the paths itself.

Example project config:

```toml
[workspace]
mode = "repo"
environment = "client_a"
```

## 7. Token model

There are two kinds of token data:

```text
Token definitions = absolute local paths
Token references  = portable paths used in project recipes
```

Token definitions belong only in:

```text
kicad_common.json
kicad_specgen.json
```

Token references belong in:

```text
<project>.kicad_specgen
```

The project `.kicad_specgen` file should contain token references only.

It should not contain machine-specific absolute path definitions.

## 8. Effective token resolution

TODO
SpecGen resolves tokens by merging sources in this order:

```text
1. Built-in computed tokens
2. KiCad tokens from kicad_common.json
3. Selected SpecGen named environment tokens from kicad_specgen.json
```

The selected SpecGen named environment overrides or supplements KiCad tokens.

The Project tab should show 2 effective token tables (kicad_common.json - readonly:

```text
Token              Resolved Path    Source
ION_DIR            /...             kicad_env
ION_WORKSPACE      /...             specgen_env:client_a
PROJECT_DIR        /...             specgen_env:client_a
SPECGEN_DIR        /...             specgen_env:client_a
```

If a token is unresolved, the Project tab should show a validation error and offer a way to add the missing token to the selected named environment in `kicad_specgen.json`.

```
Token              Resolved Path                         Source
SPECGEN_COMM       /...                                  kicad_env
ION_WORKSPACE      /...                                  specgen_env:client_a
PROJECT_DIR        /...                                  specgen_env:client_a
SPECGEN_DIR        /...                                  specgen_env:client_a
```

The 

## 9. Important token meanings

Current intended meanings:

```text
ION_DIR
  Base folder where the SpecGen application is installed from Git.

ION_WORKSPACE
  Workspace root used for shared/repo-based KiCad project work.

PROJECT_DIR
  The project Git repo root.

SPECGEN_DIR
  The location of default SpecGen support files used to seed a new project.
  This may be a shared folder, app-provided folder, or KiCad user settings SpecGen folder.

DESIGN_DIR / KICAD_PROJECT_DIR / BOARD_DIR
  Proposed name needed for the actual KiCad design folder that contains .kicad_pro.
  This name is not yet finalized.
```

Important correction:

`PROJECT_DIR` should not mean the folder containing `.kicad_pro` unless the Git repo root and KiCad design folder are the same.

We need a separate token/name for the KiCad design directory.

## 10. SpecGen project file

The `.kicad_specgen` file is the main SpecGen project/session file.

Opening a `.kicad_specgen` file is the same as opening a SpecGen project.

It contains the state for all tabs:

* Project tab
* Variables tab
* Jobset tab
* JS Results metadata
* Report recipe
* FAB recipe
* Logs/session references as needed

`kicad_specgen.json` stores the last opened `.kicad_specgen` file.

On app launch, SpecGen reads `kicad_specgen.json` and reopens the last `.kicad_specgen`.

## 11. Project config location

A SpecGen project config must live in the KiCad design’s local `specgen/` folder.

Current rule needing clarified token names:

```text
<actual KiCad design folder>/specgen/<name>.kicad_specgen
```

Because `PROJECT_DIR` means Git repo root, this should not be written as:

```text
<PROJECT_DIR>/specgen/<name>.kicad_specgen
```

unless the project Git repo root is also the KiCad design folder.

The config location determines the active KiCad design folder.

Proposed derived paths:

```text
SPECGEN_PROJECT_FILE = opened .kicad_specgen file
DESIGN_SPECGEN_DIR   = parent folder of SPECGEN_PROJECT_FILE
DESIGN_DIR           = parent folder of DESIGN_SPECGEN_DIR
```

Names still need final approval.

## 12. Project `.kicad_specgen` contents

The project `.kicad_specgen` file should store portable project state and tokenized references.

It should include:

* schema version
* workspace mode
* selected environment name
* KiCad design identity
* active `.kicad_pro` filename if needed
* active `.kicad_jobset` path or filename
* variable metadata
* custom variables
* jobset destination overrides
* report page order
* additional report file references
* report output settings
* FAB package settings

It should not store absolute machine-specific paths unless explicitly marked local-only.

## 13. KiCad design folder

The KiCad design folder is the folder containing the `.kicad_pro` file.

This folder is different from `PROJECT_DIR` when the project Git repo contains multiple designs or a deeper directory structure.

Example:

```text
PROJECT_DIR
  /Users/me/Documents/GitHub/client_project_repo

KiCad design folder
  /Users/me/Documents/GitHub/client_project_repo/projects/Power/kicad/BoardA

SpecGen project file
  /Users/me/Documents/GitHub/client_project_repo/projects/Power/kicad/BoardA/specgen/release.kicad_specgen
```

The token/name for the KiCad design folder name: 
KICAD_PROJECT_DIR

## 14. Default support files

Default SpecGen support files are used to seed a new project.

They live under `SPECGEN_DIR`.  These files are located in the SpecGen application folder in a folder called "common".

Examples:

```text
default.kicad_specgen
default_template.kicad_jobset
report_style.css
bom_style.css
title_page.html
end_page.html
```

The SpecGen application will prompt to Use Defaults in the  SPECGEN_DIR/common folder, Copy Default files to the local KICAD_PROJECT_DIR/specgen folder, or Skip to leave them as blank entries for the user to populate.

## 15. Jobset files

`.kicad_jobset` files are always portable between KiCad projects because their  outputs are relative to the KICAD_PROJECT_DIR.

Jobset file outputs are source files for the report but are unique to the kicad project in the KICAD_PROJECT_DIR and will be located in a subfolder(s) identified in the selected `.kicad_jobset` file.  These output files are generated by running the jobset from the Jobset tab. If these files exist, the jobset doesn't need to be run unless the user chooses to rerun the jobset or chooses a new jobset file, which will overwrite the output files or place them in a different location. 

SpecGen should treat `.kicad_jobset` as KiCad-owned input.

SpecGen should not modify `.kicad_jobset` by default.

SpecGen-specific jobset additional support data, such as report headings or descriptions, are stored in `.kicad_specgen`, keyed by the  jobset destination ID.

The  `.kicad_specgen` will only store one jobset data set that will get replaced if a new jobset file is selected.  When selecting a new jobset file, if there is data associated with the destination ID, the user should get a prompt that selecting a new jobset will loose the saved data and ask if they want to "Save As"  the present `.kicad_specgen` TOML file (Yes/No dialog).

## 16. Report recipe portability

Report recipes should be portable.

Generated jobset outputs should not be copied from another project.  They are generated when the user runs the jobset from the Jobset tab.

They should be regenerated by running the jobset against the active KiCad design.

Additional user-authored report files should use tokenized paths.

If copied from another project, user-authored files inside the old KiCad design folder should preserve the same design-relative directory structure.

Example:

```text
<OldDesignDir>/background/file.md
<NewDesignDir>/background/file.md
```

The recipe path should remain tokenized:

```text
{DESIGN_DIR}/background/file.md
```

Token name pending final decision.

External/shared files outside the design folder should be treated as environment/shared assets.

## 17. Missing token resolution

If a project `.kicad_specgen` references an `ION_*` token that does not exist on the current machine, SpecGen should not silently fail.

It should offer to:

* add the missing token to the selected named environment in `kicad_specgen.json`
* pick a replacement file or folder
* skip the affected item

Missing-token resolution should exist in both:

* setup
* Project tab validation/sync tools

## 18. Stage 1 scope

Stage 1 includes:

* setup bootstrap
* shared utilities
* Project tab
* Variables tab
* basic Logs tab
* logging framework
* config load/save
* token resolver
* named environments
* workspace mode handling
* validation framework

Stage 1 does not include:

* running jobsets
* rendering reports
* packaging FAB output
* full JS Results preview
* full import/copy recipe workflow

## 19. Basic Logs tab

The Logs tab in Stage 1 is simple.

It should show:

* timestamp
* level
* source
* message

It should be able to show application validation messages and state-change messages.

Later stages will add:

* jobset execution output
* report build output
* FAB package output

## 20. Current open naming issue

The biggest unresolved naming issue is the token/name for the actual KiCad design folder.

`PROJECT_DIR` is now defined as the project Git repo root.

`SPECGEN_DIR` is now defined as the default support files folder.

Therefore a new name is needed for:

```text
folder containing .kicad_pro
folder whose child specgen/ contains the .kicad_specgen files
folder where jobset_output/ and FAB/ will be created
```

Candidate names:

```text
DESIGN_DIR
KICAD_PROJECT_DIR
BOARD_DIR
```

Recommended: `KICAD_PROJECT_DIR`, because it matches KiCad terminology and is clearer than `DESIGN_DIR`.

