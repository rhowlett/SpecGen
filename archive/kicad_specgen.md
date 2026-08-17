# KiCad SpecGen - Report Generator
## Dependencies
Use only these libraries (all pip-installable):
- PySide6       # GUI Suport
- tomli_w       # system schema config save
- markdown      # render
- weasyprint    # render
- python-docx   # render
- cairosvg      # render
- pandas        # render
- Pillow        # render
- watchdog      # file system monitoring — auto-reload when source files change
- platformdirs  # cross-platform paths for saving user preferences/recent manifests
- jinja2        # for ALL template substitution (not manual string replace), so that filters, conditionals, and loops are available in templates.

## Requirements
- Python 3.10+
- Each renderer type should use the same report schema
- The block intermediate format must be well-typed using dataclasses
- Include basic error handling: missing files, unknown file types, invalid manifest keys should all produce clear error messages
- Add a dry-run flag that prints the file issues / unsupport format / etc... puts output in /tmp to view before overwriting

---

## High-Level Description

### ABOUT

A desktop GUI application (Python3.10+ using PySide6) for electronics design engineers using KiCad9+ on Ubuntu22+, Mac OS, and Windows 10+. It automates the final steps of a KiCad PCB design release: running the KiCad command-line tool jobset option to generate schematic PDFs, PCB plots, BOMs and drill reports; assembling all those outputs into a single polished release report in a selectable format; and packaging the FAB deliverables (Gerbers, drill files, pick-and-place) for board manufacture in a configurable file structure and file types. Work that previously required manually invoking kicad-cli, copying files, and stitching PDFs together is handled in one tool with a consistent configuration file.

---

## Workspace File System Description
KiCad9+ is a highly configurable and felxible EDA tool.  It has the abiliy to store files in multiple locations and multiple file types.  This felxibility can lead to multiple work flows so this application is tylored for a structured work flow using git as the distributed version-control for KiCad project management and KiCad environment variables.  This application lives within the git repo, that is a KiCad workspace framework for projects, libs, and tools, so updates are pulled at the time of project updates.  The repository described in the next section shows what is relavant to this application.

### The Repository Context
For this example, the tool lives inside the `advanced_engineering` repository. That repo is the single workspace for all EE hardware projects and has a fixed structure that the tool depends on:

```
<root>
  └── <path_to_git_base_dir>/                              ← EX: dirname $(git rev-parse --show-toplevel) 
      │
      ├── <specgen_repo_name>/                             ← the repo root <specgen_repo_name> = `kicad_specgen` ({REPO} token)
      │   │                                                  EX: <specgen_repo_name> = `<project_repo_name>`
      │   └── <path_to_scripts>/kicad_specgen/             ← this application (note this might be the same as <specgen_repo_name> or git Submodule)
      │                                                      EX: <path_to_scripts> = `tools/scripts`
      │
      ├── <kicad_lib_repo_name>/                           ← the kicad library repo root 
      │   │                                                  EX: <kicad_lib_repo_name> = `<project_repo_name>/libs/kicad/templates`
      │   └── <path_to_kicad_lib>/specgen/                 ← global templates
      │        ├── default.toml                            ← base configuration outline if not TOML is present for a project
      │        ├── report_style.css / bom_style.css        ← default report typography
      │        ├── title_page.html / end_page.html         ← default HTML page templates for first and last page of report
      │        └── default_template.kicad_jobset           ← default base job sequence that can be used for any project
      │
      └── <project_repo_name>/                             ← the repo root <git_repo_name> = `advanced_engineering` ({REPO} token)
          └── <path_to_project>/<Project>/                 ← one per PCB design
              │                                              EX: <path_to_project> = `projects/<ProjectType>/kicad`
              ├── *.kicad_pro / *.kicad_sch / *.kicad_pcb  ← KiCad design files, *.kicad_pro contains project text variables
              ├── specgen/                                 ← per-project config files
              │   ├── <config_file>.toml                   ← project TOML override (can be more than one for different configs)
              │   └── <jobset_name>.kicad_jobset           ← local project-specific job sequence (can be more than one for different configs)
              │
              ├── <documentation>/                         ← optional markdown, txt, csv, html, image content for report pages 
              │
              ├── jobset_output/<jobset_name>/             ← kicad-cli jobset file outputs (location defined in .kicad_jobset)
              │   ├── sch/                                 ← generated artefacts by type (folder name defined in the kicad_jobset file)
              │   ├── pcb/                                 ← generated artefacts by type (folder name defined in the kicad_jobset file)
              │   ├── gerbers/                             ← generated artefacts by type (folder name defined in the kicad_jobset file)
              │   ├── 3D/                                  ← generated artefacts by type (folder name defined in the kicad_jobset file)
              │   ├── report/                              ← report generator output 
              │   └── log/                                 ← report generator session logs
              │
              └── FAB/<jobset_name>/                       ← release package (configurable via this application)
                  ├── GERBER/<Project>.zip                 ← contains zip file of gerber folder
                  ├── REPORT/<Project>_report.pdf          ← report generator output
                  ├── DRILLMAP/
                  │   ├── <Project>.drl                    ← drill map for fab
                  │   └── <Project>-drl_map.pdf            ← visual grill map descirption
                  ├── <Project>-bom.xlsx                   ← report generator converted output from jobset <bom_file>.csv
                  ├── <Project>.step                       ← jobset 3D step <file>.step output
                  ├── <Project>-pickNplace.txt             ← jobset position <file>.txt output
                  └── README.txt                           ← FAB folder manafest and file descriptions
```
**Additional Path details**
* <path_to_projects>/repo/projects/<ProjectType>/kicad
  - Recomended structure: designed to force some organization
  - Users can put the project anywhere - The recomended structure should be advice to the user but not forced
  - The directory structure under the <Project> is enforced per the KiCad 9+ application
  - if the recomended structure is used, <ProjectType> can be parsed from the path with a description saved in the project TOML
* <path_to_project> is abitrary and can exist anywhere on the users system
  * <path_to_project> = <path_to_projects>/repo/projects/<ProjectType>/kicad if the recomended structure is used
* jobset_output/<jobset_name>
  - The jobset_output folder will be generated by the kicad-cli 
  - The jobset_output/<jobset_name> folder will be generated by the kicad-cli 

### Kicad Environment Variable
- `kicad_common.json`
  * At runtime from `kicad_common.json` (KiCad's own environment variable file OS specific location) in the environment:vars: section are path variables.  The ION_DIR is the path_to_git_base_dir and ION_WORKSPACE is ION_DIR/<git_repo_name> ION_SPECGEN is ION_WORKSPACE/libs/kicad/templates/specgen. All paths stored in TOML configuration files use the same token names as the prefix of the path so the same config works on any machine regardless of where the repo is cloned. EX: `{ION_*}/relative_path/file_name` 
  * If `kicad_common.json` doesn't exist, then a message asking to install kicad and setup kicad env variables.  
- `kicad_specgen.json`
  * In the same OS specific directory where the `kicad_common.json` file is stored, this application will create a file called `kicad_specgen.json` that will store the location of the last <config_file>.toml file that the application uses at [Save and Exit].
  * When the application is launched, if the `kicad_specgen.json` file doesn't exist or points to a file that doesn't exist, then the application notes the default file will be copied to the project folder and prompts the user to open a folder location for the project.  Once the project folder is selected, the {LIB}/default_template.kicad_jobset file is copied to the project folder specgen folder (application will create if it doesn't exist).

### Default Jobset Folder Structure
The kicad-cli program runs in the program folder where the .kicad_pro file is located, thus making the .kicad_jobset file portable to multiple projects.  The jobset contains the folder <jobset_name> which will generate in the project folder.  The jobset doesn't give full control over file names is all file export cases.  In most cases the jobset can define the output directory within the <jobset_name> folder.  Images types are generally svg and 3D renders in png format. Because of filenaming limitations, the user will use a direcotry structure to help identify the type of file.

Expected files in the <jobset_name> folder to generate the report and release package files:
<jonset_name>
 ├── <sch_dir>/
 │    ├── <Project>.pdf                  ← jobset pdf schematic ouput (kicad-cli uses this format for the file)
 │    ├── <Project>.svg                  ← jobset svg schematic ouput (kicad-cli uses this format for the file)
 │    ├── <erc_file>.txt                 ← jobset electrical rules check report ouput
 │    └── <bom_file>.csv                 ← jobset csv bill of materials output (convert to xlsx with template)
 ├── <pcb_dir>/<Project>-<layer>.pdf     ← jobset pdf pcb project layer(s) ouput
 │    ├── <file_name>-all.txt            ← jobset position <file>.txt output
 │    ├── <Project>.drl                  ← jobset fab drill map output (goes into the FAB gerber zip)
 │    └── <Project>-drl_map.pdf          ← jobset drill map pdf output
 ├── <gerber_dir>/
 │    ├── <Project>-job.grbjob           ← jobset output for kiCad Gerberview 
 │    └── <Project>-<layer>.<gerber_ext> ← jobset output of gerber pcb layers (F_cu, B_cu, In-X_cu, F_Mask, etc...)
 ├── <3d_dir>/
 │    ├── <3d_file>.step                 ← jobset 3D step file output
 │    └── <image_name_N>.png             ← jobset png image of 3D redering (top, bottom, side, etc...)
 ├── report/                             ← report generator output
 │    ├── <Project>-<jobset_name>.docx   ← report generator full report in MS word docx output
 │    ├── <Project>-<jobset_name>.md     ← report generator full report in markdown output
 │    ├── <Project>-<jobset_name>.html   ← report generator full report in html output
 │    └── <Project>-<jobset_name>.pdf    ← report generator full report in pdf output
 └── log/<Project>-<YYMMDD>.log          ← report generator session logs
  
---

## Proposed Application Framework
The framework should have a file structure that is extensable and consistant gui look and feel. This framework segragates functions into logic file names. 

```
main.py
  ├── documents/
  │     ├── help.md                     ← Help Info
  │     └── about.md                    ← Program About Info
  └── app.py  MainWindow
        ├── state.py                    ← single source of truth system schema (paths, files, variables, report schema, FAB schema)
        ├── kicad_env_parse.py          ← parse kicad_specgen/kicad_common.json for portable paths and populate system config schema
        ├── specgen_config_io.py        ← open/parse TOML, populate system config schema, and save state to present or new TOML file.
        ├── kicad_pro_parse.py          ← parse <project>.kicad_pro populate system config schema with project text variables
        ├── jobset_parse.py             ← open/parse jobset data and populate system config schema (populates available files schema) also defines the output folder <path_to_project>/<jobset_name_dir>
        ├── bom_parse.py                ← TODO - place holder for hand place report generator (refs/unique parts for handplace)
        ├── position_parse.py           ← TODO - place holder for hand place report generator (will fine  BOM part location)
        ├── svg_gen_parse.py            ← TODO - place holder for hand place report generator (will place indicator for BOM part)
        ├── theme.py                    ← EE dark QSS palette + colour constants
        ├── report_render
        │   ├── html_report_builders.py ← convert identified report files into pure HTML/content (inputs:html,txt,csv,md,svg,png)
        │   ├── docx_report_builder.py  ← convert html from html_report_builders to docx
        │   ├── md_report_builder.py    ← convert html from html_report_builders to md
        │   └── pdf_report_builder.py   ← convert html from html_report_builder to pdf using PyMuPDF PDF pipeline
        └── tabs/
              project_tab.py            ← paths, jobset, TOML, templates, environment
              variables_tab.py          ← kicad_pro vars, project info, custom vars
              jobset_tab.py             ← job list, run all/checked, session log
              js_result_tab.py          ← file preview of files in jobset output folder
              report_tab.py             ← FileRegistry UI, build trigger
              fab_tab.py                ← FAB manifest, jobset output file mapping & rename
              handbuild_tab.py          ← TODO - FileRegistry UI (csv, HTML, svg, txt, md), build trigger for create 
              logs_tab.py               ← log tail viewer
```

### Program Initialization
- User starts with main.py 
- Loads system schema
  - The program will check OS type for location of seed data in kicad_common.json and kicad_specgen.json.  
  - The program opens toml file
  - The program opens the .kicad_pro file
  - The program opens the jobset file
  - The program locates files in jobset folder
  - The program locates files in user defined folder(s)
- Generate workspace with tabs
  - starts on the project tab -> user takes over

### File definitions
- Kicad Env Vars
 * OS specific locations 
   * MacOS (need to look up)
   * Ubuntu (need to look up)
   * Windows (need to look up)
 * `kicad_common.json`
   * this is a read-only file
   * {{"environment": { "vars": { "<path_var>": "<absolute_path>", ... }}}}
 * `kicad_specgen.json`
   * this application creates and updates this file
   * {"last_session": { "toml": "<absolute_path>"}}
- Library Default Files
 * Repo location repo/lib/kicad/templates/specgen/
   * default.toml
     * this is a read-only file
     * base configuration 
     * copied into a project that doesn't have a TOML file in its specgen folder
       * if doesn't exist create folder --> <path_to_project>/<Project>/specgen/
       * copy to --> <path_to_project>/<Project>/specgen/<Project>.toml
   * report_style.css / bom_style.css
     * these are a read-only file
     * report typography
     * application will ask if the user want's to copy these too when default.toml is being copied
   * title_page.html / end_page.html
     * these are a read-only file
     * HTML page templates
     * application will ask if the user want's to copy these too when default.toml is being copied
   * default_template.kicad_jobset
     * this is a read-only file
     * base job sequence
     * application will ask if the user want's to copy this if <Project>.kicad_jobset doesn't exist when default.toml is being copied
       * copy to --> <path_to_project>/<Project>/specgen/<Project>.kicad_jobset
- Project Files 
 * Project location <path_to_projects>/repo/projects/<ProjectType>/kicad/<Project>/
   * one per PCB design ({project} token)
 * <Project>.kicad_pro KiCad main project file
   * this is a read-only file
 * <Project>.kicad_sch Kicad schematic file
   * this is a read-only file
 * <Project>.kicad_pcb KiCad pcb design files
   * this is a read-only file
 * <Project>/specgen/
   * per-project config files 
   * <config_file>.toml 
     * default is <Project>.toml
     * more than one toml file can exist with different configs for different reports
**TODO Finish updating toml file in /Users/Richard.Howlett/Documents/GitHub/advanced_engineering/projects/Ref_PowerBank_DCA/kicad/Ref_PowerBank_4S/specgen**
   * <jobset_name>.kicad_jobset
     * kicad-cli project-specific job sequence (output file structure and files) User Input
     * defines the file output location <jobset_name_dir> all jobset file folders use this as the base dir
   * report_style.css / bom_style.css
     * optional
     * report typography
   * title_page.html / end_page.html
     * optional
     * HTML page templates

---
**TODO**
---

**State flow:** 
- System Schema is the common data for all tabs.
  - The System Schema is populated at run time with the read-only kicad_common.json paths files that provide paths and variables 
    - This data are fixed/imutable/common no matter what TOML file is loaded
    - All of the kicad_common.json is saved in the System schema
    - The evironment vars contain paths to the kicad workspace, libs, and default specgen input files used for this application
    - These valuse are not saved to a TOML file since they are OS specific
  - The kicad_specgen.json contains the location for the last saved TOML file
    - If the file exist, this application opens that TOML file
    - If the application exit with save, the location of the saved TOML is also saved to the kicad_specgen.json 
    - These valuse are not saved to a TOML file since they are saved to the kicad_specgen.json
  - The 
  - It will change and update based on user inputs and manipulations
  - It can be reset by loading a new TOML file
  - It can be reset by starting a new TOML file
  - The file contains the last sessions system schema. 
- In the coarse of updating and running kicad_jobset files and updating  When a new TOML file is loaded it
- It holds the three identity fields (`ion_dir`, `program_name`, `project_name`) plus loaded data (`toml`, `kicad_pro_vars`, `jobset_path`). 
- All directory paths (`specgen_dir`, `output_dir`, `log_dir`, etc.) are computed `@property` values derived from the three identity fields — never stored as separate fields. 
- When a tab mutates state it emits `state_changed` → `MainWindow._broadcast_state()` calls `refresh_from_state()` on all seven tabs unconditionally. 
- There is one signal and one broadcast; no callbacks, no dirty sets.

**Configuration (toml):** The `.toml` file (TOML format) is the project configuration for this tool — it is separate from KiCad's own files. It stores the report page order, CSS and HTML template paths, company metadata, and user-defined template variables. Paths inside the TOML use `{ION_DIR}/…` tokens. The global `default.toml` in `libs/` provides defaults; each project can override it in `specgen/<Project>.toml`. The toml schema is a set of Python dataclasses (`TomlMeta`, `TomlVariables`, `TomlReport`, `TomlSch`, `TomlPcb`, `TomlFab`) serialised to TOML.

**report_render**
For pdf and docx output, support optional page_header and page_footer keys in the manifest that inject a repeating header/footer on every page, also supporting {{variable}} substitution and {{page}} / {{total_pages}} tokens.

---

## Color System

`theme.py` defines the EE dark palette and a set of named semantic colours used consistently across all tabs:

| Constant | Hex | Meaning |
|---|---|---|
| `CONST_CLR` | `#e8c44a` | Read-only constants — values from `.kicad_pro`, env vars, derived paths |
| `GRN_BTT` | `#3ddc84` | Run / go / success actions |
| `BLU_BTT` | `#4f8ef7` | Primary interactive actions |
| `AMB_BTT` | `#f5a623` | Warnings |
| `RED_BTT` | — | Remove / destructive actions |
| `TEXT_SEC` | `#8a90a8` | Dim / secondary / read-only labels |
---

---

## Tab-by-Tab Reference

**Tab Responsibilities**

| Tab | Owns | Produces |
|---|---|---|
| **Project** | Path parsing, TOML load/save, template file paths, KiCad env vars display | `AppState` identity fields, loaded `TomlData` |
| **Variables** | Release vars from `.kicad_pro`, project info (Company, Website, Description), custom `{{VAR}}` tokens | `TomlData.variables.custom`, `TomlMeta` company fields |
| **Jobset** | Job table from `.kicad_jobset`, run via `kicad-cli jobset run`, editable descriptions | Output files in `jobset_default/sch|pcb|fab|report/` |
| **JS Results** | 6-column tree of all output files, file preview panel | — (read-only view) |
| **Report** | FileRegistry UI (available ↔ in-report ordering), output path, build trigger | Final `report.pdf` |
| **Release Package** | FAB manifest, rename rules, gerber zip, README generation | `FAB/` release package |
| **Logs** | Live tail of session log file from `jobset_default/log/` | — (read-only) |

The project files aren't in the container — they're on your machine. I have everything I need from the session context and transcripts. Let me write the description from what I know of the code:Good — I have all the context I need. Here is the description:

### ⚙ Project tab

**Layout:** Two-column split. Left column holds the Project section and the KiCad Environment Variables section. Right column holds the Templates section.

**Function:** The entry point for every session. The user browses to a KiCad project folder; the tab parses the path, validates it against the known ION_DIR structure, loads the project's `.kicad_pro` variables, auto-loads the TOML configuration file, and populates the rest of the application. Until a valid project is selected, all other tabs show empty or placeholder state.

**Data gathered:**

| Field | What it is |
|---|---|
| project folder | Path to `<ION_DIR>/projects/<ProjectType>/kicad/<Project>` |
| Git repo | Derived from path — name of the repo folder (`advanced_engineering`) |
| Project | Derived from path — e.g. `Ref_PowerBank_DCA` |
| project | Derived from path — e.g. `Ref_PowerBank_4S` |
| KiCad env vars | All `environment:vars` entries from `kicad_common.json` (read-only), including `ION_DIR` / `GIT_DIR` |
| TOML config | Selected `.toml` file — project-specific or global library default |
| Jobset file | Selected `.kicad_jobset` — defines what kicad-cli jobs to run |
| Logo image | Path to company logo used on report title page |
| Report CSS | CSS file controlling report body typography |
| BOM CSS | CSS file controlling BOM table layout (landscape) |
| Title Page | HTML template for the report cover page |
| End Page | HTML template for the report closing page |

**Data location:**
- Path fields → `AppState.ion_dir`, `.program_name`, `.project_name` (in memory)
- TOML file paths → `AppState.toml` (TomlData dataclass)
- Jobset path → `AppState.jobset_path`
- Template paths → `TomlData.report.*_path` fields, stored as `{ION_DIR}/relative` tokens in `specgen/<Project>.toml`
- KiCad env vars → read-only from `~/Library/Preferences/kicad/kicad_common.json` (macOS) or platform equivalent

---

### 📊 Variables tab

**Layout:** Two-column split. Left column = Release Variables (read-only). Right column = Project Info group above Custom Template Variables table.

**Function:** Displays all variables available to HTML templates during report generation. No kicad-cli jobs are run from here — this tab is purely for viewing and editing the `{{VAR}}` token values that get substituted into `title_page.html` and `end_page.html`.

**Data gathered:**

| Section | Field | Editable |
|---|---|---|
| Release Variables | All `text_variables` from `.kicad_pro` — `DATE`, `REV`, `ION_PART`, etc. | No — read from KiCad file |
| Project Info | `COMPANY` → company name | Yes |
| Project Info | `COMPANY_WEBSITE` → company website | Yes |
| Project Info | `PROJECT` → project description | Yes |
| Custom Template Variables | User-defined `{{VAR_NAME}}` / value pairs | Yes — name and value |

**Data location:**
- Release variables → `AppState.kicad_pro_vars` dict (read from `.kicad_pro` `text_variables` section, never written back)
- Company name → `TomlData.meta.company_name`
- Company website → `TomlData.meta.company_website`
- Project description → `TomlData.meta.project_name`
- Custom variables → `TomlData.variables.custom` dict
- All persisted in `specgen/<Project>.toml` under `[meta]` and `[variables]`

---

### ▶ Jobset tab

**Layout:** Single-column. Top area: job table with run controls. Bottom area: live log panel.

**Function:** Reads the selected `.kicad_jobset` JSON file and displays each job as a row in the table. The user can run all jobs or only checked jobs. Each job invokes `kicad-cli jobset run` as a subprocess. The Description column is editable (double-click) so the user can label jobs with section titles that will appear in the report. A `Save Descriptions` button writes the edited descriptions back to the `.kicad_jobset` file.

**Data gathered:**

| Field | What it is |
|---|---|
| Job list | Parsed from `.kicad_jobset` JSON — type, output path, description |
| Run selection | Checkboxes per job — which jobs to run |
| Descriptions | Editable section titles (saved back to `.kicad_jobset`) |
| Output prefix | The output directory prefix (e.g. `jobset_default`) parsed from the first job's output path |

**Data location:**
- Job definitions → `<Project>/specgen/<name>.kicad_jobset` (JSON, read and partially written back)
- Output files → `<Project>/jobset_default/sch/`, `/pcb/`, `/fab/`, `/report/`
- Session log → `<Project>/jobset_default/log/session_<timestamp>.log`
- Output prefix → `AppState.jobset_output_prefix`

---

### 🔍 JS Results tab

**Layout:** Two-panel horizontal split. Left = 6-column file tree. Right = preview panel for the selected file.

**Function:** Read-only inspection of everything generated by the last jobset run. Files are shown in a tree grouped by type and subdirectory. Selecting a file opens a preview: PDFs render page-by-page, images display inline, text files show raw content. This tab helps the user verify outputs are correct before building the report.

**Data gathered:** None — read-only view.

**Data displayed:**

| Column | Content |
|---|---|
| Name | Filename |
| Type | File extension category (PDF, PNG, CSV, TXT, etc.) |
| Size | File size |
| Modified | Last-modified timestamp |
| Location | Subdirectory within the output tree |
| Status | Whether the file is included in the current report page order |

**Data location:**
- All data read live from `<Project>/jobset_default/` directory tree

---

### 📄 Report tab
TODO - still working on this / this will change significantly

**Layout:** Two-panel horizontal split. Left = Available files list. Right = In Report ordered list. Bottom bar = output path, build button, open PDF button.

**Function:** Controls what goes into the PDF report and in what order. Files produced by the jobset appear in the Available list; the user adds them to the In Report list and reorders them by dragging or using move buttons. Generated pages (Title Page, End Page) are always available as entries. Clicking Build Report PDF runs the pipeline and writes the output file.

**Data gathered:**

| Field | What it is |
|---|---|
| Page order | Ordered list of FileRecord entries — generated pages, markdown, PDFs, images, CSVs |
| Labels | Per-entry display label (can be edited; defaults to job description) |
| Output path | Where the final `report.pdf` is written |

**Data location:**
- Page order → `TomlData.report.page_order` list of `{kind, key, label}` dicts, stored with portable `{ION_DIR}/…` path tokens in `specgen/<Project>.toml` under `[report]`
- Output path → `TomlData.report.output_path`
- Built report → `<Project>/jobset_default/report/report.pdf`
- File records → `FileRegistry` in-memory store (populated by scanning jobset outputs + Background/)

---

### 📦 FAB tab
TODO - still working on this / this will change significantly

**Layout:** Single column. Top = manifest table of files to include. Bottom = controls for naming, zipping, and exporting.

**Function:** Packages the fabrication deliverables for the PCB manufacturer. The user selects which files to include (Gerbers, drill, pick-and-place, BOM, schematic PDF, final report) and configures the output naming convention. Files are renamed using the project name and revision. A README can be auto-generated. The result is a zip archive in the `FAB/` folder ready to send.

**Data gathered:**

| Field | What it is |
|---|---|
| Include Gerbers | Whether to bundle Gerber files |
| Include drill | Whether to include drill files |
| Include SCH PDF | Whether to include schematic PDF |
| Include BOM | Whether to include bill of materials |
| Include final report | Whether to include the assembled report PDF |
| Gerber zip name | Name of the output Gerber zip file |

**Data location:**
- Settings → `TomlData.fab.*` fields in `[fab]` section of `specgen/<Project>.toml`
- Input Gerbers → `<Project>/jobset_default/FAB/gerbers/`
- Output package → `<Project>/FAB/`

---

### 📋 Logs tab
TODO - still working on this

**Layout:** Single column. Top = path label showing the active log file. Bottom = scrolling text viewer.

**Function:** Live tail of the current session log file. As `kicad-cli` jobs run, their stdout/stderr is tee'd to the log file and this viewer scrolls to show new lines in real time. Report build output (from `report_builder.py`) is also appended here. Useful for diagnosing why a job failed or why a report section is missing.

**Data gathered:** None — read-only display.

**Data displayed:**
- Live content of `<Project>/jobset_default/log/session_<timestamp>.log`
- Report build progress lines (archive construction, Story render stats, stitch progress, final page count)

**Data location:**
- Log file → `AppState.paths.log_dir / session_<timestamp>.log` → `<Project>/jobset_default/log/`

---

## Data Dependency Map
TODO - still working on this
```
User browses project folder
          │
          ▼
   AppState (state.py)
   ├── ion_dir, program_name, project_name  ← parsed from path
   ├── kicad_pro_vars  ← read from .kicad_pro text_variables
   ├── toml            ← loaded from specgen/<Project>.toml
   └── jobset_path     ← selected from specgen/*.kicad_jobset

          │  state_changed signal
          ▼
   All 7 tabs call refresh_from_state()
   and read their data directly from AppState / AppState.toml

   Persisted on "Exit with Save":
   ├── specgen/<Project>.toml     ← meta, variables, report page order, FAB settings
   └── QSettings              ← last-used path, session restore on next launch
```
---
## Report Build Pipeline
TODO - still working on this

The PDF assembly pipeline in `report_builder.py` is a **streaming stitcher**. It walks the ordered `FileRegistry.in_report_records()` list and produces a sequence of in-memory PDF byte-strings that are stitched at the end by `pypdf`.

```
in_report_records()  (user-defined order)
  │
  ├── generated (title_page / end_page)  ──┐
  ├── Markdown (.md)                       ├─ html_group → one pymupdf.Story call
  ├── Plain text / ERC / DRC reports       │  using report_style.css + Archive(image_dirs)
  ├── PNG images                           │
  │                                        ┘ → pdf_bytes
  ├── CSV / BOM ──────────────────────────── landscape pymupdf.Story (bom_style.css)
  ├── SVG ─────────────────────────────────  normalise_svg() → pymupdf.open(filetype="svg")
  ├── PDF file ────────────────────────────  read bytes directly
  └── PDF directory ───────────────────────  each PDF in sorted order

pypdf.PdfWriter  ←  stitch all pdf_bytes  →  report.pdf
```

The key design decision is the **grouping rule**: consecutive HTML-renderable records accumulate into an `html_group` and are flushed as a single `pymupdf.Story` call when broken by a PDF, SVG, or CSV. This gives consistent typography across the title page, background document, and text reports that appear together.

**Content functions** (`content_builders.py`) — markdown→HTML, CSV→HTML table, `{{VAR}}` template substitution — are separated from the PyMuPDF renderer so they can be shared with a future `docx_builder.py` without any renderer dependency.
