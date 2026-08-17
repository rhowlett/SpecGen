# KiCad SpecGen Menu Bar and Help System Requirements

## Purpose

This document defines the top menu bar contents for [File] in the KiCad SpecGen desktop application.

# File Menu

The File menu manages SpecGen project files and application session actions.

Pulldown File Menu behavior:

```text
┌───────────────────────────────────────┐
│ [File]                                │
├───────────────────────────────────────┤
│ New SpecGen Project...                │
│ Open SpecGen Project...               │
│ Open Recent                           │
│ Copy / Create From Existing Project...│
│ Save                                  │
│ Save As...                            │
│ Close Project                         │
│ ───────────────────────────────────── │
│ Exit                                  │
└───────────────────────────────────────┘
```

## `New SpecGen Project...`

Opens the New SpecGen Project dialog.

Purpose:

Copies the default {KSG_SPECGEN_DIR}/default.kicad_specgen to <KICAD_PROJECT_DIR>/specgen/<specgen_project_name>.kicad_specgen
Edits copyed <new_project_neam_string>.kicad_specgen environment section with user selection <environment>

Dialog box behavior:

```text
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              New SpecGen Project Dialog                                 │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ Select KiCad Project Folder:                                                            │
│  [ Select ] KiCad project folder                                                        │<KICAD_PROJECT_DIR>
│ Select Named Environment:                                                               │
│  [ <input_text_string> ] Enter NEW named environment OR                                 │<environment> wins if there is a text value (string can not be just spaces)
│  [ ] Standalone                                                                         │
│  [ Select ] Git Repository                                                              │if <enviroment> is NEW then newopen folder picker dialog to select a repo otherwise gray out
│  [ Select ] Environment Common Folder (don't select for default)                        │if <enviroment> is NEW then newopen folder picker dialog to select a KSG_SPECGEN_COMMON otherwise gray out
│  [ <pull_down_list_from kicad_specgen.json> ] Select named environment                  │<environment> seed with "internal"
│ New SpecGen Project Name:                                                               │
│  [ <input_text_string> ] Enter New SpecGen Project Name (default support files)         │<specgen_project_name> will seed with <project_folder> name if blank
│ ─────────────────────────────────────────────────────────────────────────────────────── │
│ Selected:                                                                               │
│ Selected KiCad Project Folder       : <KICAD_PROJECT_DIR>                               │
│ Selected SpecGen Project Name       : <specten_project_name>                            │
│ Selected Named Environment          : <environment>                                     │
│ Selected SpecGen Project Type       : < "Standalone" | "Repo" >                         │
│ Selected Repo Folder                : <                                                 │
│ Selected SpecGen Common File Folder :                                                   │
│ ─────────────────────────────────────────────────────────────────────────────────────── │
│  [ Create ]                                                                    [Cancel] │if <enviroment> is NEW then newopen folder picker dialog 
└─────────────────────────────────────────────────────────────────────────────────────────┘
TODO finish

```

Rules:

* The new file must use the `.kicad_specgen` extension.
* The file must be saved under `<KICAD_PROJECT_DIR>/specgen/`.
* The new project should use tokenized paths.
* The new project should not store local-machine absolute path definitions.

---

## `Open SpecGen Project...`

Opens a file picker for an existing `.kicad_specgen` file.

Purpose:

Open an existing SpecGen project and replaces the project state.

Rules:

* The selected file must have extension `.kicad_specgen`.
* The selected file should live under a `specgen/` folder.
* Opening the file restores the full SpecGen project state.
* The application should derive `KICAD_SPECGEN_DIR` and `KICAD_PROJECT_DIR` from the opened file location.
* The application should update `kicad_specgen.json -> last_session`.

---

## `Open Recent`

Displays recently opened SpecGen project files.

```text
Open Recent
  Recent project list
  Clear recent projects
```
Recent project paths are local-machine state and should be stored in `kicad_specgen.json`.

---

## `Copy / Create From Existing Project...`

Opens a wizard for creating a new SpecGen project from an existing project file.

Purpose:

Convenience flow for copying an existing `.kicad_specgen` recipe into another KiCad project.

The wizard should (similar layout to New SpecGen Project):

```text
Select source .kicad_specgen
Select destination KiCad project folder
Select destination <specgen_project_name> (seed with copied project name if not the same folder location otherwise blank)
Ask to Copy or reference support files (local specgen/ or link to source)
Rebind project-local paths
Validate unresolved tokens
Save <specgen_project_name>.kicad_specgen under destination specgen/ use [Create] [Cancel] buttons
Add a note that jobset output will not be copied, User must generate from local project
```
Generated jobset outputs should not be copied. They should be regenerated by running the Jobset tab.

---

## `Save`

Saves the active project `.kicad_specgen` file.

Rules:

* Save full project state. (update <specgen_project_name>.kicad_specgen
* Update dirty state.
* Update status bar.

---

## `Save As...`

Opens a Save As dialog.

Purpose:

Save the current SpecGen project state to another `.kicad_specgen` file.

Rules:

* Destination must remain under `<KICAD_PROJECT_DIR>/specgen/`.
* File extension must be `.kicad_specgen`.
* If the destination exists, prompt:

```text
Overwrite
Rename
Cancel
```

---

## `Close Project`

Closes the active SpecGen project.

If unsaved changes exist, prompt:

```text
Save
Discard
Cancel
```

---

## `Exit`

Closes the application.

If unsaved changes exist, prompt:

```text
Save
Discard
Cancel
```
