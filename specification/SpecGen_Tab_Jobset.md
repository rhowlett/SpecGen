# Jobset Tab Dashboard Wireframe

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [File]   [Edit]   [View]   [Help]                                                                          │
├───────────────┬────────────────────────────────────────────────────────────────────────────────────────────┤
│ SIDEBAR       │                                                                                            │
│               │ ┌───────────────┬───────────────┬───────────────┬─────────────┐                            │
│ [Project]     │ │▶ Dashboard    │ Setup & Run   │ Results       │ Output Log  │                            │
│ [Variables]   │ └───────────────┴───────────────┴───────────────┴─────────────┘                            │
│▶[Jobset]      │ ┌────────────────────────────────────────────────────────────────────────────────────────┐ │
│ [Report]      │ │ JOBSET DASHBOARD                                                                       │ │
│ [Logs]        │ ├────────────────────────────────────────────────────────────────────────────────────────┤ │
│ ───────────── │ │ Active KiCad Project : {KICAD_PROJECT_DIR}/BoardA.kicad_pro                            │ │
│ [Configure]   │ │ Active Jobset        : {KSG_PROJECT_SPECGEN_DIR}/release_default.kicad_jobset          │ │
│               │ │ Output Root          : {JOBSET_OUTPUT_DIR}                                             │ │
│               │ │ kicad-cli            : /Applications/KiCad/KiCad.app/.../kicad-cli                     │ │
│               │ │ Last Run             : Success on 2026-06-03 14:32                                     │ │
│               │ └────────────────────────────────────────────────────────────────────────────────────────┘ │
│               │ ┌──────────────────────────────────────────────┬─────────────────────────────────────────┐ │
│               │ │ DESTINATION DETAILS                          │ VALIDATION / MESSAGES                   │ │
│               │ ├──────────────────────────────────────────────┼─────────────────────────────────────────┤ │
│               │ │ Selected ID       : bom_csv                  │ ⚠ BOM output exists but is older than   │ │
│               │ │ Output Folder     : jobset_output/release/bom│   the active .kicad_sch file.           │ │
│               │ │ Expected File     : *.csv                    │                                         │ │
│               │ │ Heading Override  : BOM                      │ ✓ Destination ID is valid.              │ │
│               │ │ Notes             : Used by Report + FAB     │ ✓ Output folder is writable.            │ │
│               │ └──────────────────────────────────────────────┴─────────────────────────────────────────┘ │
│               │                                                                                            │
│               │                                                                                            │
├───────────────┴────────────────────────────────────────────────────────────────────────────────────────────┤
│ STATUS: Project valid | Environment: client_a | Jobset ready | 5 selected destinations | Last run: Success │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## Setup & Run Subtab Layout

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [File]   [Edit]   [View]   [Help]                                                                          │
├───────────────┬────────────────────────────────────────────────────────────────────────────────────────────┤
│ SIDEBAR       │                                                                                            │
│               │ ┌───────────────┬───────────────┬───────────────┬─────────────┐                            │
│ [Project]     │ │ Dashboard     │▶ Setup & Run  │ Results       │ Output Log  │                            │
│ [Variables]   │ └───────────────┴───────────────┴───────────────┴─────────────┘                            │
│▶[Jobset]      │ ┌────────────────────────────────────────────────────────────────────────────────────────┐ │
│ [Report]      │ │ RUN CONTROLS                                                                           │ │
│ [Logs]        │ ├────────────────────────────────────────────────────────────────────────────────────────┤ │
│ ───────────── │ │ [Select Jobset...]                                                           [Run All] │ │
│ [Configure]   │ │ [Reload]                                                                [Run Selected] │ │
│               │ │                                                                                 [Stop] │ │
│               │ │ Options:                                                                               │ │
│               │ │ [x] Stop on error                                                                      │ │
│               │ │ [x] Clear log before run                                                               │ │
│               │ └────────────────────────────────────────────────────────────────────────────────────────┘ │
│               │ ┌────────────────────────────────────────────────────────────────────────────────────────┐ │
│               │ │ JOBSET                                                                                 │ │
│               │ │ Active Jobset: {KSG_PROJECT_SPECGEN_DIR}/release_default.kicad_jobset                  │ │
│               │ │ Active Output Folder : {KICAD_PROJECT_DIR}/{JOBSET_OUTPUT_DIR}                         │ │
│               │ ├─────┬──────────┬────────────────────┬──────────────────────┬────────────┬──────────────┤ │
│               │ │ Run │ Status   │ Destination ID     │ KiCad Description    │ Output     │ SpecGen      │ │
│               │ │     │          │                    │                      │ Type       │ Heading      │ │
│               │ ├─────┼──────────┼────────────────────┼──────────────────────┼────────────┼──────────────┤ │
│               │ │ [x] │ Ready    │ sch_pdf            │ Schematic PDF        │ PDF        │ Schematics   │ │
│               │ │ [x] │ Ready    │ erc_report         │ ERC Report           │ TXT        │ ERC Report   │ │
│               │ │ [x] │ Warning  │ bom_csv            │ Bill of Materials    │ CSV        │ BOM          │ │
│               │ │ [ ] │ Ready    │ pcb_layers_pdf     │ PCB Layer Plots      │ PDF        │ PCB Layers   │ │
│               │ │ [x] │ Ready    │ gerbers            │ Gerber Package       │ Gerber     │ Fabrication  │ │
│               │ │ [ ] │ Not Run  │ step_model         │ STEP 3D Model        │ STEP       │ 3D Model     │ │
│               │ └─────┴──────────┴────────────────────┴──────────────────────┴────────────┴──────────────┘ │
│               │ ┌────────────────────────────────────────────────────────────────────────────────────────┐ │
│               │ │ RUN STATUS                                                                             │ │
│               │ ├──────────────────────────────────────────────────────────────────────────────────────┬─┤ │
│               │ │ >kicad-cli                                                                           │^│ │
│               │ │ >output                                                                              │|│ │
│               │ │ >messages                                                                            │v│ │
│               │ └──────────────────────────────────────────────────────────────────────────────────────┴─┘ │
│               │                                                                                            │
│               │                                                                                            │
├───────────────┴────────────────────────────────────────────────────────────────────────────────────────────┤
│ STATUS: Project valid | Environment: client_a | Jobset ready | 5 selected destinations | Last run: Success │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## Results Subtab Layout

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [File]   [Edit]   [View]   [Help]                                                                          │
├───────────────┬────────────────────────────────────────────────────────────────────────────────────────────┤
│ SIDEBAR       │                                                                                            │
│               │ ┌───────────────┬───────────────┬───────────────┐                                          │
│ [Project]     │ │ Dashboard     │ Setup & Run   │▶ Results      │                                          │
│ [Variables]   │ └───────────────┴───────────────┴───────────────┘                                          │
│▶[Jobset]      │                                                                                            │
│ [Report]      │ ┌──────────────────────────────────────────────────┬┬────────────────────────────────────┐ │
│ [Logs]        │ │ GENERATED OUTPUT FILES                           ││ FILE PREVIEW                       │ │
│ ───────────── │ ├──────────────────────────────────────────────────┤├────────────────────────────────────┤ │
│ [Configure]   │ │ jobset_output/release_default/                   ││ Preview: BoardA-schematic.pdf      │ │
│               │ │ ├── sch/                                         ││┌─────────────────────────────────┐ │ │
│               │ │ │   ├── BoardA.pdf       PDF 2026-06-03  ✓ [View]│││                                 │ │ │
│               │ │ │   ├── BoardA.svg       SVG 2026-05-26  ⚠ [View]│││        PDF / IMAGE / TEXT       │ │ │
│               │ │ │   └── erc_report.txt   TXT 2026-06-03  ✓ [View]│││        PREVIEW AREA             │ │ │
│               │ │ ├── bom/                                         │││                                 │ │ │
│               │ │ │   └── bom.csv          CSV 2026-06-03  ✓ [View]││└─────────────────────────────────┘ │ │
│               │ │ ├── pcb/                                         ││                                    │ │
│               │ │ │   └── BoardA-F_Cu.pdf  PDF 2026-06-03  ✓ [View]││ File Metadata:                     │ │
│               │ │ ├── gerbers/                                     ││   Type: PDF                        │ │
│               │ │ │   └── BoardA-F_Cu.gbr  GBR 2026-06-03  ✓       ││   Size: 420 KB                     │ │
│               │ │ └── 3d/                                          ││   Modified: 2026-06-03 14:32       │ │
│               │ │     ├── BoardA_top.png   PDF 2026-06-03  ✓ [View]││   Used by Report: Yes              │ │
│               │ │     └── BoardA.step     STEP 2026-05-26  x       ││                                    │ │
│               │ └──────────────────────────────────────────────────┴┴────────────────────────────────────┘ │
│               │   ✓ - Jobset Successfully Generate                                                         │
│               │   ⚠ - Error Before Generating                                                              │
│               │   x - Not generated                                                                        │
│               │                                                                                            │
│               │                                                                                            │
├───────────────┴────────────────────────────────────────────────────────────────────────────────────────────┤
│ STATUS: Results refreshed | 18 files found | 1 warning | Output root: {JOBSET_OUTPUT_DIR}                  │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## Output Log Subtab Layout

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [File]   [Edit]   [View]   [Help]                                                                          │
├───────────────┬────────────────────────────────────────────────────────────────────────────────────────────┤
│ SIDEBAR       │                                                                                            │
│               │ ┌───────────────┬───────────────┬───────────────┬─────────────┐                            │
│ [Project]     │ │ Dashboard     │ Setup & Run   │ Results       │▶ Output Log │                            │
│ [Variables]   │ └───────────────┴───────────────┴───────────────┴─────────────┘                            │
│▶[Jobset]      │ ┌────────────────────────────────────────────────────────────────────────────────────────┐ │
│ [Report]      │ │ OUTPUT LOG                                                                             │ │
│ [Logs]        │ ├──────────────────────────────────────────────────────────────────────────────────────┬─┤ │
│ ───────────── │ │  2026-06-03 14:32:01  kicad-cli jobset run --file release_default.kicad_jobset ...   │^│ │
│ [Configure]   │ │  2026-06-03 14:32:01  ► Running: sch_pdf                                             │ │ │
│               │ │  2026-06-03 14:32:03  ✓ sch_pdf completed → sch/BoardA.pdf                           │ │ │
│               │ │  2026-06-03 14:32:03  ► Running: erc_report                                          │ │ │
│               │ │  2026-06-03 14:32:05  ✓ erc_report completed → sch/erc_report.txt                    │ │ │
│               │ │  2026-06-03 14:32:05  ► Running: bom_csv                                             │ │ │
│               │ │  2026-06-03 14:32:06  ✓ bom_csv completed → bom/bom.csv                              │ │ │
│               │ │  2026-06-03 14:32:06  ► Running: gerbers                                             │ │ │
│               │ │  2026-06-03 14:32:09  ✓ gerbers completed → gerbers/                                 │ │ │
│               │ │  2026-06-03 14:32:09  ─────────────────────────────────────────────────────────      │ │ │
│               │ │  2026-06-03 14:32:09  Run complete: 4 of 4 selected destinations succeeded.          │ │ │
│               │ │                                                                                      │v│ │
│               │ └──────────────────────────────────────────────────────────────────────────────────────┴─┘ │
│               │  [ Clear Log ]   [ Save Log... ]                                     [ Copy to Clipboard ] │
│               │                                                                                            │
│               │                                                                                            │
├───────────────┴────────────────────────────────────────────────────────────────────────────────────────────┤
│ STATUS: Last run: Success | 4/4 destinations | 2026-06-03 14:32:09 | Output: {JOBSET_OUTPUT_DIR}           │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

Notes:
- Timestamps are local machine time
- Each destination ID is shown before and after run
- ✓ = success, ✗ = failure, ⚠ = warning
- Log is cleared before each run if "Clear log before run" is checked in Setup & Run
- Log may be saved to `{KSG_PROJECT_SPECGEN_DIR}/logs/` via Save Log button
- This log feeds the Logs workspace page for persistence
