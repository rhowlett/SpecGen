# KiCad SpecGen — Authoritative Specification Documents

This folder contains the **authoritative source documents** for KiCad SpecGen.
They are the single source of truth for the application's design, data
formats, terminology, and behavior.

## Governance rule

These documents are authoritative. The application code must conform to them,
not the other way around. Therefore:

> **Every code change must determine whether it affects any authoritative
> document, and if so, update that document in the same change.**

When code and a document disagree, the document wins — either the code is
corrected to match, or (if the change is intentional) the document is updated
first and the code follows. A change is not complete until the relevant
documents in this folder reflect it.

## Document index

### Foundational / cross-cutting

| Document | Purpose |
|---|---|
| `SpecGen_Terminology.md` | Canonical token, file, and label names; the organizational model (departments → teams, clients → projects). Living document. |
| `SpecGen_Schema_Definitions.md` | JSON schemas for all four config files (local, company, users, project). Living document. |
| `SpecGen_File_Framework.md` | Token model, file ownership, configuration loading, and startup sequence. |
| `SpecGen_Stage_Plan.md` | Stage scope, module breakdown, and tests. Living document. |
| `SpecGen_Progress.md` | Project progress and architecture record. Contains the AppState / ValidationResult contracts. |

### Setup & process

| Document | Purpose |
|---|---|
| `SpecGen_Setup_Process.md` | The six-phase setup process, platform detection, first-run seeding, and the setup Q&A. |

### Application & GUI

| Document | Purpose |
|---|---|
| `SpecGen_Application_Description.md` | Overall application architecture and sidebar layout. |
| `SpecGen_GUI_Menus.md` | Menu bar structure and actions. |
| `SpecGen_GUI_Dialogs.md` | Modal dialog wireframe specifications. |
| `SpecGen_GUI_Theme.md` | The six themes, the `specgen_section_heading` style, and the save-dirty button tokens. |

### Tab specifications

| Document | Purpose |
|---|---|
| `SpecGen_Tab_Configure.md` | Configure tab and its five subtabs. |
| `SpecGen_Tab_Logs.md` | Logs tab. |
| `SpecGen_Tab_Jobset.md` | Jobset tab dashboard (Stage 3). |
| `SpecGen_Tab_Report.md` | Report tab (Stage 4). |

### Help content

| Document | Purpose |
|---|---|
| `SpecGen_Help_Guide.md` | Help file authoring guide. |
| `SpecGen_Help_JinJa.md` | Using variables in documents with Jinja2 templates. |

## Living documents

The documents marked "Living document" above change most often as the design
evolves. The schema redesign that introduced the single-company model
(no `company_id`), the department → team and client → project hierarchies,
the seven required local tokens with the writable-space rule, and the theme
section-heading / save-dirty additions is reflected in:

- `SpecGen_Terminology.md`
- `SpecGen_Schema_Definitions.md`
- `SpecGen_GUI_Theme.md`
