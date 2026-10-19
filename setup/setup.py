"""
setup.py — Headless setup entry point.

Run: python setup/setup.py [--stage stage1] [--launch]

Six phases:
  1. Platform detection and KICAD_COMMON_DIR resolution
  2. .venv creation and dependency installation
  3. kicad-cli detection and configuration
  4. Company and user config bootstrap
  5. Write / update kicad_specgen_local.json
  6. Validation
"""
from __future__ import annotations
import argparse
import logging
import subprocess
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from core.logging_utils import configure_logging
from core.platform_paths import detect_platform, resolve_kicad_common_dir
from core.file_ops import ensure_dir
import core.specgen_local_config as local_mod
import core.specgen_company_config as company_mod
import core.specgen_user_config as users_mod
from setup.setup_utils import create_venv, install_requirements, venv_dir

configure_logging()
log = logging.getLogger("setup")


def run_setup(stage: str = "stage1", launch: bool = False,
              seed_tokens: dict | None = None) -> int:
    """
    Run all six setup phases. Returns 0 on success.

    seed_tokens (optional): a dict from FirstRunSeedDialog containing the
    user-chosen writable tokens (KSG_COMPANY_DIR, KSG_COMPANY_SPECGEN_DIR,
    KSG_COMPANY_COMMON_DIR, KSG_USER_SPECGEN_DIR, KSG_USER_COMMON_DIR) and
    active_user. When provided, these are written into the new local config
    instead of leaving the writable tokens empty.
    """
    log.info("=== KiCad SpecGen Setup ===")

    # Phase 1 — Platform detection
    log.info("Phase 1: Platform detection")
    platform = detect_platform()
    log.info("Platform: %s", platform)
    try:
        kicad_common, kicad_version = resolve_kicad_common_dir(platform)
    except ValueError as e:
        log.warning("KiCad config dir not found: %s", e)
        kicad_version = "9.0"
        from core.platform_paths import kicad_common_dir
        kicad_common = kicad_common_dir(platform, kicad_version)

    ensure_dir(kicad_common)
    log.info("KICAD_COMMON_DIR: %s", kicad_common)

    app_dir = _PROJECT_ROOT
    log.info("KSG_APP_DIR: %s", app_dir)

    # Phase 2 — .venv and dependencies
    log.info("Phase 2: Dependency installation")
    venv_ok = False
    try:
        venv = create_venv(app_dir)
        install_requirements(venv, stage, app_dir)
        venv_ok = True
    except Exception as e:
        log.error("Phase 2 failed: %s", e)
        log.warning("Continuing without .venv — dependencies may be missing.")

    # Phase 3 — kicad-cli detection
    log.info("Phase 3: kicad-cli detection")
    if platform == "macos":
        from setup.setup_macos import detect_kicad_cli
    elif platform == "linux":
        from setup.setup_linux import detect_kicad_cli
    else:
        from setup.setup_windows import detect_kicad_cli
    cli_path, cli_source = detect_kicad_cli()
    if cli_path:
        log.info("kicad-cli: %s (%s)", cli_path, cli_source)
    else:
        log.warning(
            "kicad-cli not found — configure manually via "
            "Edit → Configure kicad-cli..."
        )

    # Phase 4 — Company and user config bootstrap
    log.info("Phase 4: Company and user config bootstrap")
    if seed_tokens and seed_tokens.get("KSG_COMPANY_DIR"):
        # The first-run seed dialog already created the company/users files
        # in the chosen KSG_COMPANY_DIR. Nothing to bootstrap here.
        log.info("Using seeded company dir: %s", seed_tokens["KSG_COMPANY_DIR"])
    else:
        specgen_dir = app_dir / "SpecGen"
        ensure_dir(specgen_dir)
        company_path = specgen_dir / "kicad_specgen_company.json"
        users_path   = specgen_dir / "kicad_specgen_users.json"
        if not company_path.exists():
            company_mod.create_standalone(company_path)
            log.info("Created standalone company config: %s", company_path)
        if not users_path.exists():
            users_mod.create_empty(users_path)
            log.info("Created empty users config: %s", users_path)

    # Phase 5 — Write / update local config
    # Without a seed, writable-space tokens are left EMPTY for the user to
    # configure via the Configure tab. With a seed, the chosen tokens are
    # written. KSG_APP_DIR is read-only either way.
    log.info("Phase 5: Writing local config")
    local_path = kicad_common / "kicad_specgen_local.json"
    if local_path.exists():
        local_cfg = local_mod.load(local_path)
    else:
        ksg_company_dir = (seed_tokens.get("KSG_COMPANY_DIR")
                           if seed_tokens else None) or str(app_dir)
        local_cfg = local_mod.create_minimal(
            local_path,
            ksg_app_dir           = str(app_dir),
            ksg_system_config_dir = str(kicad_common),
            ksg_company_dir       = ksg_company_dir,
            platform              = platform,
        )
        # Apply the remaining seeded writable tokens, if any
        if seed_tokens:
            for tok in ("KSG_COMPANY_SPECGEN_DIR", "KSG_COMPANY_COMMON_DIR",
                        "KSG_USER_SPECGEN_DIR", "KSG_USER_COMMON_DIR"):
                if seed_tokens.get(tok):
                    local_cfg.tokens[tok] = seed_tokens[tok]
            if seed_tokens.get("active_user"):
                local_cfg.active_user = seed_tokens["active_user"]

    local_cfg.setup["setup_complete"]      = True
    local_cfg.setup["dependency_stage"]    = stage
    local_cfg.setup["last_setup_platform"] = platform
    if cli_path:
        local_cfg.tools["kicad_cli"]        = cli_path
        local_cfg.tools["kicad_cli_source"] = cli_source

    local_mod.save(local_cfg)
    log.info("Local config written: %s", local_path)

    # Phase 6 — Validate
    log.info("Phase 6: Validation")
    from core.validators import validate_local_config, ValidationReport
    report = ValidationReport()
    report.results.extend(validate_local_config(local_cfg, local_cfg.tokens))
    if report.failures:
        log.error("Validation: %d failure(s)", report.failures)
        for r in report.results:
            if r.status == "fail":
                log.error("  FAIL [%s]: %s", r.check_id, r.message)
    elif report.warnings:
        log.warning("Validation: %d warning(s)", report.warnings)
        for r in report.results:
            if r.status == "warn":
                log.warning("  WARN [%s]: %s", r.check_id, r.message)
    else:
        log.info("Validation: all checks passed")

    # Done
    log.info("=== Setup complete ===")
    log.info("")

    if not launch:
        log.info("Next steps:")
        if venv_ok:
            log.info("  1. Activate the virtual environment:")
            if platform == "windows":
                log.info("       %s\\Scripts\\activate", venv_dir(app_dir))
            else:
                log.info("       source %s/bin/activate", venv_dir(app_dir))
            log.info("  2. Run the application:")
            log.info("       python app.py")
        else:
            log.info("  Run the application:")
            log.info("       python app.py")
        if not cli_path:
            log.info("")
            log.info("  Note: configure kicad-cli via Edit → Configure kicad-cli...")
    else:
        _launch_app(app_dir, venv_ok, platform)

    return 0


def _launch_app(app_dir: Path, venv_ok: bool, platform: str) -> None:
    """Launch app.py, preferring the venv Python if available."""
    if venv_ok:
        if platform == "windows":
            python = venv_dir(app_dir) / "Scripts" / "python.exe"
        else:
            python = venv_dir(app_dir) / "bin" / "python"
    else:
        python = Path(sys.executable)

    app_script = app_dir / "app.py"
    if not app_script.exists():
        log.error("app.py not found at %s", app_script)
        return

    log.info("Launching: %s %s", python, app_script)
    try:
        # Use Popen so setup exits and the app runs independently
        subprocess.Popen([str(python), str(app_script)], cwd=str(app_dir))
    except Exception as e:
        log.error("Failed to launch app: %s", e)
        log.info("Launch manually: python app.py")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="KiCad SpecGen setup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python setup/setup.py                      # GUI setup (default)
  python setup/setup.py --headless           # terminal setup, print next steps
  python setup/setup.py --headless --launch  # terminal setup, launch app when done
  python setup/setup.py --stage stage4       # GUI setup, full install
  python setup/setup.py --uninstall          # GUI uninstall dialog
  python setup/setup.py --headless --uninstall-local   # remove local config only
  python setup/setup.py --headless --uninstall-full    # remove app directory
""",
    )
    parser.add_argument(
        "--stage", default="stage1",
        choices=["stage1", "stage2", "stage3", "stage4"],
        help="Highest dependency stage to install (default: stage1)",
    )
    parser.add_argument(
        "--headless", action="store_true", default=False,
        help="Run in terminal mode without the GUI (default: GUI)",
    )
    parser.add_argument(
        "--launch", action="store_true", default=False,
        help="Launch app.py automatically after headless setup completes",
    )
    parser.add_argument(
        "--uninstall", action="store_true", default=False,
        help="Open the GUI uninstall dialog",
    )
    parser.add_argument(
        "--uninstall-local", action="store_true", default=False,
        help="Headless: remove only kicad_specgen_local.json (with confirmation)",
    )
    parser.add_argument(
        "--uninstall-full", action="store_true", default=False,
        help="Headless: remove the entire app directory (with confirmation)",
    )
    args = parser.parse_args()

    # Headless uninstall paths
    if args.uninstall_local or args.uninstall_full:
        sys.exit(_headless_uninstall(full=args.uninstall_full))

    # GUI uninstall
    if args.uninstall:
        from setup.setup_gui import UninstallDialog
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance() or QApplication([])
        UninstallDialog().exec()
        sys.exit(0)

    # Setup
    if args.headless:
        sys.exit(run_setup(stage=args.stage, launch=args.launch))
    else:
        # GUI is the default
        try:
            from setup.setup_gui import run_gui
            sys.exit(run_gui(stage=args.stage))
        except ImportError as e:
            log.error("GUI unavailable (%s). Falling back to headless setup.", e)
            log.error("Install PySide6 first, or run: python setup/setup.py --headless")
            sys.exit(run_setup(stage=args.stage, launch=args.launch))


def _headless_uninstall(full: bool) -> int:
    """Headless uninstall with a typed terminal confirmation."""
    from core.platform_paths import detect_platform, resolve_kicad_common_dir
    app_dir = _PROJECT_ROOT
    platform = detect_platform()
    try:
        kc, _ = resolve_kicad_common_dir(platform)
    except ValueError:
        from core.platform_paths import kicad_common_dir
        kc = kicad_common_dir(platform, "9.0")
    local_path = kc / "kicad_specgen_local.json"

    if full:
        print(f"FULL UNINSTALL will permanently delete:")
        print(f"  - {local_path}")
        print(f"  - {app_dir}  (entire application directory)")
    else:
        print(f"LOCAL UNINSTALL will permanently delete:")
        print(f"  - {local_path}")
    print("Your KiCad project files are NOT affected.")
    answer = input("Type 'yes' to confirm: ").strip().lower()
    if answer != "yes":
        print("Uninstall cancelled.")
        return 1

    from setup.setup_utils import uninstall_local_config, uninstall_full
    if full:
        summary = uninstall_full(app_dir, local_path)
        print(f"Local config removed: {summary['local_removed']}")
        print(f"Application directory removed: {summary['app_dir_removed']}")
    else:
        removed = uninstall_local_config(local_path)
        print(f"Local config removed: {removed}")
    return 0


if __name__ == "__main__":
    main()
