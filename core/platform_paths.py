# v0.1
################################################################################
#  Project   : SpecGen
#  File      : platform_paths.py
#  Copyright : (c) 2026 brickChip and Richard Howlett. All rights reserved.
#  Author    : Richard Howlett <rhowlett@eenerd.com>
#  License   : PolyForm Noncommercial 1.0.0. Free for noncommercial use;
#              commercial use requires written permission from the owner.
#              Full terms in LICENSE at the project root.
#  Warranty  : None. Provided as is; the owner is not liable for any
#              damages arising from its use (No Liability, LICENSE).
#  SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
################################################################################

"""
platform_paths.py — OS detection and KICAD_COMMON_DIR resolution.

Must Not Do: No file I/O beyond path existence checks. No GUI.
"""
from __future__ import annotations
import os, re, sys
from pathlib import Path

PLATFORM_MACOS   = "macos"
PLATFORM_LINUX   = "linux"
PLATFORM_WINDOWS = "windows"


def detect_platform() -> str:
    if sys.platform == "darwin":   return PLATFORM_MACOS
    if sys.platform.startswith("win"): return PLATFORM_WINDOWS
    return PLATFORM_LINUX


def kicad_config_parent(platform: str) -> Path:
    """Parent folder containing versioned KiCad config subdirs."""
    if platform == PLATFORM_MACOS:
        return Path.home() / "Library" / "Preferences" / "kicad"
    if platform == PLATFORM_WINDOWS:
        appdata = os.environ.get("APPDATA", "")
        base = Path(appdata) if appdata else Path.home() / "AppData" / "Roaming"
        return base / "kicad"
    xdg = os.environ.get("XDG_CONFIG_HOME", "")
    return (Path(xdg) if xdg else Path.home() / ".config") / "kicad"


def detect_kicad_config_version(platform: str) -> str | None:
    """
    Scan kicad_config_parent for versioned subdirs matching d+.d+.
    Returns highest version, or None if none found.
    """
    parent = kicad_config_parent(platform)
    if not parent.exists():
        return None
    pattern = re.compile(r"^\d+\.\d+$")
    versions = [e.name for e in parent.iterdir()
                if e.is_dir() and pattern.match(e.name)]
    if not versions:
        return None
    versions.sort(key=lambda v: tuple(int(x) for x in v.split(".")), reverse=True)
    return versions[0]


def kicad_common_dir(platform: str, version: str) -> Path:
    return kicad_config_parent(platform) / version


def resolve_kicad_common_dir(platform: str | None = None,
                              version: str | None = None) -> tuple[Path, str]:
    """
    Resolve KICAD_COMMON_DIR. Returns (path, version_string).
    Raises ValueError if version cannot be detected and was not provided.
    """
    if platform is None:
        platform = detect_platform()
    if version is None:
        version = detect_kicad_config_version(platform)
        if version is None:
            raise ValueError(
                f"No KiCad config folder found under {kicad_config_parent(platform)}. "
                "Please enter the KiCad configuration version manually (e.g. '9.0')."
            )
    return kicad_common_dir(platform, version), version
