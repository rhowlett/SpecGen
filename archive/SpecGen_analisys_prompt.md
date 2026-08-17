# Claude Prompt — KiCad SpecGen Architecture Realignment and Implementation Planning

You are acting as a senior Python/PySide6 application architect, technical documentation reviewer, and implementation planner.

I have an existing KiCad SpecGen project that is partially working, but the application has evolved over time. The current codebase does not yet have a fully consistent look and feel, and some areas of the GUI, configuration model, setup flow, and file handling no longer match the framework I want to standardize on.

I do not want vibe-coded fixes or quick patches.

I want this project to become professional, extensible, maintainable, and testable.

Your first task is not to write application code. Your first task is to analyze the attached documents, identify gaps, contradictions, outdated assumptions, missing requirements, and recommend a layered implementation plan.

## Primary source of truth

Treat the following file as the current desired foundation:

```text
SpecGen_File_Framework.md
```
This docuemnt contains TODO that are under construction areas needing to be addressed.

This document defines the current direction for:

* Configuration file ownership.
* Local versus shared configuration.
* Token definitions and token references.
* `kicad_specgen_local.json`.
* `kicad_specgen_company.json`.
* `kicad_specgen_users.json`.
* Project `.kicad_specgen` files.
* KiCad `.kicad_pro` and `.kicad_jobset` handling.
* File open and token resolution sequence.
* Required local tokens.
* Protected derived runtime tokens.
* Setup and validation responsibilities.

Use this file as the authority when other documents conflict with it.

## Supporting reference documents

The following documents are also provided. They are useful, but they may contain outdated names, gaps, contradictions, or assumptions that predate `SpecGen_File_Framework.md`.

```text
SpecGen_Pulldown_Menus.md
SpecGen_Jobset_Window.md
Help_JinJa.md
kicad_specgen_application_description.md
```

Use these files as supporting design references, not as final authority.

In particular:
* `SpecGen_Pulldown_Menus.md` 
  - It is a GUI/menu concept document.
  - It is also intended to be the primary method for presenting proposed UI pulldowns before implementation, providing visual confirmation and design validation prior to coding.
* `SpecGen_Jobset_Window.md` 
  - is a visual/wireframe reference for the Jobset workflow. 
  - It should be reviewed for consistency with the current token and file framework. 
  - It is also intended to be the primary method for presenting proposed UI wireframes before implementation, providing visual confirmation and design validation prior to coding.
* `Help_JinJa.md` 
  - It is an example of the Markdown-based help file style I want the application to support.
  - It is intended to be like a standard format for other help windows.
* `kicad_specgen_application_description.md` 
  - Describes the broader application concept, but contains older architecture assumptions.
It is likely that all these files contains older terms, missing information, and file names that need to be updated to match the current framework.

## Project context

KiCad SpecGen is a standalone Python desktop application for KiCad 9+.

The application should use:

```text
Python 3.10+
PySide6
JSON configuration files
Markdown help files
kicad-cli integration
centralized token resolution
centralized validation
centralized state/config services
```

The application should not depend on KiCad’s bundled Python environment or the `pcbnew` Python module.

KiCad integration should happen through:

```text
kicad-cli
read-only parsing of KiCad JSON files
read-only parsing of KiCad S-expression files where needed later
```

## Important current design decisions

Use these decisions unless the documents clearly show a conflict that needs to be flagged.

### Local configuration

The official local machine configuration file is:

```text
kicad_specgen_local.json
```

Do not use `kicad_specgen.json` for the local machine configuration in new documentation or implementation planning.

### Token model

Only `kicad_specgen_local.json` stores local absolute token definitions.

Company, user, and project files should use token references.

The core rule is:

```text
Local absolute path token definitions live in kicad_specgen_local.json.

Company, user, and project configuration files use token references.

The application resolves token references during file open, validation, and runtime operation.
```

### Required local tokens

The required local tokens are:

```text
KSG_APP_DIR
KSG_SYSTEM_CONFIG_DIR
KSG_COMPANY_DIR
KSG_USER_SPECGEN_DIR
KSG_USER_COMMON_DIR
```

### Protected derived runtime tokens

These are computed at runtime and must not be stored as local token definitions:

```text
SPECGEN_PROJECT_FILE
KSG_PROJECT_SPECGEN_DIR
KICAD_PROJECT_DIR
GIT_PROJECT_DIR
JOBSET_OUTPUT_DIR
FAB_OUTPUT_DIR
```

For KSG_PROJECT_SPECGEN_DIR, check if there are any issues with changes this to SPECGEN_PROJECT_DIR to be more consistant in naming.

### Important naming rule

Use:

```text
KSG_PROJECT_SPECGEN_DIR
```

Do not use the older name:

```text
KICAD_SPECGEN_DIR
```

The project-local `specgen/` folder is owned by SpecGen, not KiCad.

### Configuration files

The key files are:

```text
kicad_specgen_local.json
SpecGen/kicad_specgen_company.json
SpecGen/kicad_specgen_users.json
<project>/specgen/<name>.kicad_specgen
<project>.kicad_pro
<name>.kicad_jobset
kicad_common.json
```

### JSON preference

I want to use JSON configuration files where practical because KiCad increasingly uses JSON for many data sets.

Review any remaining TOML assumptions and identify where they conflict with the current JSON-oriented direction.

Do not silently convert everything to JSON without identifying consequences. If a file is currently defined as `.kicad_specgen`, determine whether it should be JSON content with a `.kicad_specgen` extension, and describe the implications.

## What I want from you

Analyze the documents and produce a professional architecture review and implementation plan.

Do not write production code yet.

I want you to identify what additional information must be created before clean implementation can proceed.

## Required analysis tasks

### 1. Read and classify all attached documents

For each attached file, identify:

* Purpose.
* Current usefulness.
* Whether it is source-of-truth or supporting/reference.
* Sections that appear current.
* Sections that are outdated or inconsistent.
* Missing information needed for implementation.

### 2. Identify terminology mismatches

Create a table of outdated or inconsistent terms.

Examples to check for:

```text
kicad_specgen.json
KICAD_SPECGEN_DIR
KSG_SPECGEN_DIR
KSG_SPECGEN_COMMON
KSG_COMPANY_REPO_DIR
KSG_DIR
PROJECT_DIR
JS Results as a separate sidebar tab
TOML assumptions for .kicad_specgen
```

For each mismatch, provide:

* Old term.
* Correct term.
* Where it appears.
* Why it matters.
* Recommended replacement.

### 3. Identify file framework gaps

Using `SpecGen_File_Framework.md` as the foundation, identify what still needs to be defined for each file:

```text
kicad_specgen_local.json
kicad_specgen_company.json
kicad_specgen_users.json
project .kicad_specgen
.kicad_pro
.kicad_jobset
kicad_common.json
Markdown help files
```

For each file, identify whether we still need:

* Full schema.
* Required fields.
* Optional fields.
* Validation rules.
* Example file.
* Read/write ownership rules.
* Migration rules.
* GUI editor/viewer requirements.
* Unit tests.

### 4. Review GUI architecture consistency

Compare the GUI concept documents against the current file framework.

Review:

```text
Top menu bar
Sidebar navigation
Main tabbed workspace
Project page
Variables page
Jobset page
Report page
Fabrication page
Logs page
Configure Environments dialog
Missing Tokens dialog
Markdown Help dialog
```

Identify:

* Which GUI areas are consistent with the framework.
* Which GUI areas need renaming or redesign.
* Which actions should write to local config.
* Which actions should write to project config.
* Which actions should only read KiCad-owned files.
* Which dialogs are Stage 1 versus later stages.

### 5. Review Jobset workflow

Use `SpecGen_Jobset_Window.md` as the visual reference.

Evaluate:

* Dashboard tab.
* Setup & Run tab.
* Results tab.
* Output Log tab.
* Whether JS Results should remain merged into Jobset.
* How `.kicad_jobset` should be selected.
* How destination IDs should be parsed and stored.
* What SpecGen may store in the project `.kicad_specgen`.
* What must not be written back to `.kicad_jobset`.
* How generated output files should be scanned and presented.

### 6. Review Help system requirements

Use `Help_JinJa.md` as the example help-file style.

Evaluate and recommend:

* Markdown help file structure.
* Required help topics.
* Markdown rendering requirements.
* Help dialog behavior.
* Where help files should live.
* How help content should be versioned with the application.
* Which help topics are required in Stage 1.

### 7. Recommend a layered architecture

Recommend a layered implementation architecture that prevents vibe coding.

The architecture should separate:

```text
core configuration models
file IO
token resolution
validation
application state
services/use cases
GUI widgets
dialogs
tabs/pages
render/report pipeline
jobset execution
FAB packaging
logging
tests
```

For each layer, describe:

* Responsibility.
* Inputs.
* Outputs.
* What it must not do.
* Example module names.

### 8. Recommend implementation stages

Create a systematic staged implementation plan.

Each stage must include:

* Scope.
* Files/modules to create or refactor.
* Acceptance criteria.
* Manual test steps.
* Automated test expectations.
* Risks.
* What not to implement yet.

The stages should avoid large rewrites without validation.

### 9. Recommend test strategy

Define the test strategy needed before implementation.

Include tests for:

* JSON schema loading.
* Token resolution.
* Missing token behavior.
* Recent projects list.
* Project open sequence.
* Company/user config loading.
* `.kicad_specgen` project loading.
* `.kicad_pro` text variable parsing.
* `.kicad_jobset` parsing.
* GUI smoke tests where practical.
* Help file loading/rendering.
* Migration/renaming checks for old terms.

### 10. Produce a gap list

Create a prioritized gap list with severity.

Use categories:

```text
Critical
High
Medium
Low
Future
```

For each gap, include:

* Description.
* Why it matters.
* Source document or area.
* Recommended next action.
* Whether it blocks implementation.

## Expected output format

Respond in this structure:

```text
1. Executive Summary

2. Source-of-Truth Assessment

3. Document-by-Document Review

4. Terminology and Naming Corrections

5. Configuration/File Framework Gaps

6. GUI Framework Gaps

7. Jobset Workflow Review

8. Help System Review

9. Recommended Layered Architecture

10. Recommended Implementation Stages

11. Testing Strategy

12. Prioritized Gap List

13. Questions That Must Be Answered Before Coding

14. Recommended Next Document to Write
```

## Important constraints

Do not begin rewriting the entire application.

Do not generate large amounts of code yet.

Do not patch individual GUI issues before the architecture is validated.

Do not invent behavior that affects persistence, file layout, or KiCad execution without marking it as an assumption.

When documentation conflicts, prefer `SpecGen_File_Framework.md` and explicitly list the conflict.

When the current codebase conflicts with the framework, identify the conflict and recommend a migration or refactor plan.

The goal is a clean, professional, extensible application foundation, not a quick working demo.

## Tone and quality bar

Act like a principal engineer reviewing a project before a major refactor.

Be direct, specific, and implementation-oriented.

Avoid vague advice.

Prefer tables, staged plans, and explicit acceptance criteria.

Call out contradictions and risky assumptions.

Focus on creating a clean architecture that can be implemented and tested systematically.

