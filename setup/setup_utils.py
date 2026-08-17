"""
setup_utils.py — Shared setup utilities: venv creation, dependency install,
progress reporting.
"""
from __future__ import annotations
import logging
import subprocess
import sys
from pathlib import Path

log = logging.getLogger(__name__)


def create_venv(app_dir: Path) -> Path:
    """Create .venv inside app_dir. Skip if already inside it."""
    venv_path = Path(app_dir) / ".venv"
    if venv_path.exists():
        log.info("setup_utils: .venv already exists at %s", venv_path)
        return venv_path
    log.info("setup_utils: creating .venv at %s", venv_path)
    result = subprocess.run(
        [sys.executable, "-m", "venv", str(venv_path)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"venv creation failed: {result.stderr}")
    return venv_path


def install_requirements(venv_path: Path, stage: str = "stage1") -> None:
    """Install requirements for the given stage into venv_path."""
    app_dir = venv_path.parent
    req_file = app_dir / "requirements" / f"requirements-{stage}.txt"
    if not req_file.exists():
        raise FileNotFoundError(f"Requirements file not found: {req_file}")

    pip = venv_path / "bin" / "pip"
    if not pip.exists():
        pip = venv_path / "Scripts" / "pip.exe"

    log.info("setup_utils: installing %s requirements from %s", stage, req_file)
    result = subprocess.run(
        [str(pip), "install", "-r", str(req_file)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"pip install failed: {result.stderr}")
    log.info("setup_utils: %s requirements installed", stage)


def verify_pyside6_version(min_version: tuple = (6, 4)) -> bool:
    """Return True if installed PySide6 meets minimum version."""
    try:
        import PySide6
        parts = tuple(int(x) for x in PySide6.__version__.split(".")[:2])
        return parts >= min_version
    except ImportError:
        return False


def find_kicad_cli_candidates(platform: str) -> list[str]:
    """Return a list of candidate kicad-cli paths for the given platform."""
    import shutil
    candidates: list[str] = []

    # Check PATH first
    found = shutil.which("kicad-cli")
    if found:
        candidates.append(found)

    if platform == "macos":
        bundle = "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"
        if bundle not in candidates:
            candidates.append(bundle)
    elif platform == "linux":
        for p in ("/usr/bin/kicad-cli", "/usr/local/bin/kicad-cli"):
            if p not in candidates:
                candidates.append(p)
    elif platform == "windows":
        import os
        pf = os.environ.get("PROGRAMFILES", r"C:\Program Files")
        win_path = rf"{pf}\KiCad\bin\kicad-cli.exe"
        if win_path not in candidates:
            candidates.append(win_path)

    return [c for c in candidates if Path(c).exists()]


def run_kicad_cli_version(cli_path: str) -> str | None:
    """Run kicad-cli --version and return the output, or None on failure."""
    try:
        result = subprocess.run(
            [cli_path, "--version"],
            capture_output=True, text=True, timeout=10,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Uninstall
# ---------------------------------------------------------------------------

def uninstall_local_config(local_config_path: Path) -> bool:
    """
    Remove only kicad_specgen_local.json (the local config file).
    Returns True if removed, False if it did not exist.
    """
    import logging
    log = logging.getLogger(__name__)
    p = Path(local_config_path)
    if p.exists():
        p.unlink()
        log.info("uninstall: removed local config %s", p)
        return True
    log.info("uninstall: local config not found %s", p)
    return False


def uninstall_full(app_dir: Path, local_config_path: Path) -> dict:
    """
    Full uninstall:
      - Remove kicad_specgen_local.json
      - Remove the entire KSG_APP_DIR tree

    Returns a dict summary: {"local_removed": bool, "app_dir_removed": bool}.
    Caller is responsible for confirming with the user BEFORE calling this.
    """
    import logging, shutil
    log = logging.getLogger(__name__)
    summary = {"local_removed": False, "app_dir_removed": False}

    summary["local_removed"] = uninstall_local_config(local_config_path)

    app = Path(app_dir)
    if app.exists() and app.is_dir():
        shutil.rmtree(app)
        log.info("uninstall: removed app dir %s", app)
        summary["app_dir_removed"] = True
    else:
        log.info("uninstall: app dir not found %s", app)

    return summary
