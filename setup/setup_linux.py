"""setup_linux.py — Linux-specific setup: kicad-cli detection."""
from __future__ import annotations
import logging
from setup.setup_utils import find_kicad_cli_candidates, run_kicad_cli_version

log = logging.getLogger(__name__)


def detect_kicad_cli() -> tuple[str, str]:
    candidates = find_kicad_cli_candidates("linux")
    for path in candidates:
        version = run_kicad_cli_version(path)
        if version:
            log.info("setup_linux: found kicad-cli at %s (%s)", path, version)
            return path, "detected_linux_path"
    return "", ""
