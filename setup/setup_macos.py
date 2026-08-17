"""setup_macos.py — macOS-specific setup: kicad-cli detection."""
from __future__ import annotations
import logging
from setup.setup_utils import find_kicad_cli_candidates, run_kicad_cli_version

log = logging.getLogger(__name__)


def detect_kicad_cli() -> tuple[str, str]:
    """
    Detect kicad-cli on macOS.
    Returns (path, source_enum_value) or ("", "").
    """
    candidates = find_kicad_cli_candidates("macos")
    for path in candidates:
        version = run_kicad_cli_version(path)
        if version:
            log.info("setup_macos: found kicad-cli at %s (%s)", path, version)
            source = "detected_macos_app" if "KiCad.app" in path else "detected_linux_path"
            return path, source
    return "", ""
