<!-- v0.1 -->
# SpecGen — change log

## Versioning rules
- Every source file carries a version tag on line 1 (`# v0.1`), or line 2 after a shebang.
- Any edit to a file bumps its Minor by one. Major only bumps when the owner declares one.
- Each change session gets one dated entry below: files touched, their new versions, and why.
- `PathMiner/pcb_trace_resistance.py` is a copy of PathMiner's tool and keeps PathMiner's
  own version tag (v0.12); it is not re-versioned here.

## 2026-11-20 — Baseline; license changed from MIT to PolyForm Noncommercial 1.0.0

Owner decision (2026-11-20): SpecGen is licensed under the PolyForm Noncommercial License
1.0.0, with an explicit no-warranty / no-liability statement, replacing the MIT License.
This is also the baseline entry: every owned source file is tagged v0.1 here. No behaviour
changed apart from the About dialog text.

| File | Version | Change |
|---|---|---|
| LICENSE | — | MIT License replaced: PolyForm Required Notice, commercial contact, no-warranty note, unmodified PolyForm Noncommercial 1.0.0 text |
| README.md | — | MIT "License" section replaced by the generated Copyright & License section (free noncommercial use, commercial use by permission, no warranty / no liability, entry points) |
| documents/change_log.md | v0.1 | New (this file) |
| __version__.py | v0.1 | Version tag and brickChip header added |
| app.py | v0.1 | Version tag and brickChip header added; entry-point banner (Launch the SpecGen GUI) |
| core/__init__.py | v0.1 | Version tag and brickChip header added |
| core/app_state.py | v0.1 | Version tag and brickChip header added |
| core/file_ops.py | v0.1 | Version tag and brickChip header added |
| core/kicad_env.py | v0.1 | Version tag and brickChip header added |
| core/logging_utils.py | v0.1 | Version tag and brickChip header added |
| core/migrations.py | v0.1 | Version tag and brickChip header added |
| core/platform_paths.py | v0.1 | Version tag and brickChip header added |
| core/schema_loader.py | v0.1 | Version tag and brickChip header added |
| core/specgen_company_config.py | v0.1 | Version tag and brickChip header added |
| core/specgen_local_config.py | v0.1 | Version tag and brickChip header added |
| core/specgen_user_config.py | v0.1 | Version tag and brickChip header added |
| core/token_resolver.py | v0.1 | Version tag and brickChip header added |
| core/validators.py | v0.1 | Version tag and brickChip header added |
| services/__init__.py | v0.1 | Version tag and brickChip header added |
| services/config_service.py | v0.1 | Version tag and brickChip header added |
| services/validation_service.py | v0.1 | Version tag and brickChip header added |
| setup/__init__.py | v0.1 | Version tag and brickChip header added |
| setup/setup.py | v0.1 | Version tag and brickChip header added; entry-point banner (setup / launch) |
| setup/setup_gui.py | v0.1 | Version tag and brickChip header added |
| setup/setup_linux.py | v0.1 | Version tag and brickChip header added |
| setup/setup_macos.py | v0.1 | Version tag and brickChip header added |
| setup/setup_seed_dialog.py | v0.1 | Version tag and brickChip header added |
| setup/setup_utils.py | v0.1 | Version tag and brickChip header added |
| setup/setup_windows.py | v0.1 | Version tag and brickChip header added |
| tests/__init__.py | v0.1 | Version tag and brickChip header added |
| tests/integration/__init__.py | v0.1 | Version tag and brickChip header added |
| tests/integration/test_config_service.py | v0.1 | Version tag and brickChip header added |
| tests/integration/test_setup_headless.py | v0.1 | Version tag and brickChip header added |
| tests/integration/test_validation_service.py | v0.1 | Version tag and brickChip header added |
| tests/regression/__init__.py | v0.1 | Version tag and brickChip header added |
| tests/regression/test_terminology.py | v0.1 | Version tag and brickChip header added |
| tests/smoke/__init__.py | v0.1 | Version tag and brickChip header added |
| tests/smoke/test_app_launch.py | v0.1 | Version tag and brickChip header added |
| tests/smoke/test_configuration_tab.py | v0.1 | Version tag and brickChip header added |
| tests/smoke/test_logs_tab.py | v0.1 | Version tag and brickChip header added |
| tests/unit/__init__.py | v0.1 | Version tag and brickChip header added |
| tests/unit/test_app_state.py | v0.1 | Version tag and brickChip header added |
| tests/unit/test_file_ops.py | v0.1 | Version tag and brickChip header added |
| tests/unit/test_logging_utils.py | v0.1 | Version tag and brickChip header added |
| tests/unit/test_migrations.py | v0.1 | Version tag and brickChip header added |
| tests/unit/test_platform_paths.py | v0.1 | Version tag and brickChip header added |
| tests/unit/test_schema_loader.py | v0.1 | Version tag and brickChip header added |
| tests/unit/test_specgen_company_config.py | v0.1 | Version tag and brickChip header added |
| tests/unit/test_specgen_local_config.py | v0.1 | Version tag and brickChip header added |
| tests/unit/test_specgen_user_config.py | v0.1 | Version tag and brickChip header added |
| tests/unit/test_token_resolver.py | v0.1 | Version tag and brickChip header added |
| tests/unit/test_validators.py | v0.1 | Version tag and brickChip header added |
| ui/__init__.py | v0.1 | Version tag and brickChip header added |
| ui/actions.py | v0.1 | Version tag and brickChip header added |
| ui/dialogs/__init__.py | v0.1 | Version tag and brickChip header added |
| ui/dialogs/about_dialog.py | v0.1 | Version tag and brickChip header added; About dialog shows © brickChip and Richard Howlett, the PolyForm summary and the no-warranty line (was "© 2026 KiCad SpecGen Contributors") |
| ui/dialogs/add_user_dialog.py | v0.1 | Version tag and brickChip header added |
| ui/dialogs/clients_teams_dialog.py | v0.1 | Version tag and brickChip header added |
| ui/dialogs/department_dialog.py | v0.1 | Version tag and brickChip header added |
| ui/dialogs/help_dialog.py | v0.1 | Version tag and brickChip header added |
| ui/dialogs/kicad_cli_dialog.py | v0.1 | Version tag and brickChip header added |
| ui/dialogs/local_tokens_dialog.py | v0.1 | Version tag and brickChip header added |
| ui/dialogs/missing_tokens_dialog.py | v0.1 | Version tag and brickChip header added |
| ui/dialogs/new_project_dialog.py | v0.1 | Version tag and brickChip header added |
| ui/main_window.py | v0.1 | Version tag and brickChip header added |
| ui/tabs/__init__.py | v0.1 | Version tag and brickChip header added |
| ui/tabs/configuration_tab.py | v0.1 | Version tag and brickChip header added |
| ui/tabs/configure/__init__.py | v0.1 | Version tag and brickChip header added |
| ui/tabs/configure/company_subtab.py | v0.1 | Version tag and brickChip header added |
| ui/tabs/configure/company_user_subtab.py | v0.1 | Version tag and brickChip header added |
| ui/tabs/configure/environments_subtab.py | v0.1 | Version tag and brickChip header added |
| ui/tabs/configure/local_machine_subtab.py | v0.1 | Version tag and brickChip header added |
| ui/tabs/configure/preferences_subtab.py | v0.1 | Version tag and brickChip header added |
| ui/tabs/configure/subtab_base.py | v0.1 | Version tag and brickChip header added |
| ui/tabs/configure/user_subtab.py | v0.1 | Version tag and brickChip header added |
| ui/tabs/configure/validation_subtab.py | v0.1 | Version tag and brickChip header added |
| ui/tabs/jobset_tab.py | v0.1 | Version tag and brickChip header added |
| ui/tabs/logs_tab.py | v0.1 | Version tag and brickChip header added |
| ui/tabs/project_tab.py | v0.1 | Version tag and brickChip header added |
| ui/tabs/report_tab.py | v0.1 | Version tag and brickChip header added |
| ui/tabs/variables_tab.py | v0.1 | Version tag and brickChip header added |
| ui/theme.py | v0.1 | Version tag and brickChip header added |
| ui/widgets/__init__.py | v0.1 | Version tag and brickChip header added |
| ui/widgets/log_viewer.py | v0.1 | Version tag and brickChip header added |
| ui/widgets/path_field.py | v0.1 | Version tag and brickChip header added |
| ui/widgets/token_table.py | v0.1 | Version tag and brickChip header added |
| ui/widgets/validation_panel.py | v0.1 | Version tag and brickChip header added |

Why: the brickChip standard (header on every owned source file, banner and
`BRICKCHIP-ENTRY-POINT` on entry points, README section, LICENSE at the root). All commits
in the repository are by the owner, so the owner can relicense. Copies obtained under the
MIT License before this change keep the MIT terms for whoever received them.

Not changed: `app.setOrganizationName("KiCad SpecGen Contributors")` in app.py. Qt uses it
to locate the saved settings, so renaming it would orphan existing user settings.
`PathMiner/pcb_trace_resistance.py` has no brickChip header (see the versioning rules);
`add_header.py check` reports it as MISSING for that reason.

Evidence: `add_header.py check .` → 1 problem, the PathMiner copy above (expected).
Python 3.12.3, `pip install -r requirements/requirements-dev.txt`, Qt offscreen:
pytest 110 passed before and after. `setup/setup.py --help` runs; About dialog rendered
offscreen with all three notice lines visible in its fixed 420×360 size.
