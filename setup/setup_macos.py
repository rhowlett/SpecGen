# v0.1
################################################################################
#  Project   : SpecGen
#  File      : setup_macos.py
#  Copyright : (c) 2026 brickChip and Richard Howlett. All rights reserved.
#  Author    : Richard Howlett <rhowlett@eenerd.com>
#  License   : PolyForm Noncommercial 1.0.0. Free for noncommercial use;
#              commercial use requires written permission from the owner.
#              Full terms in LICENSE at the project root.
#  Warranty  : None. Provided as is; the owner is not liable for any
#              damages arising from its use (No Liability, LICENSE).
#  SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
################################################################################

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
