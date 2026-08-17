"""
Regression tests: scan source files for retired names.
Per SpecGen_Terminology.md §16.
"""
import ast
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
SOURCE_DIRS = [ROOT / "core", ROOT / "services", ROOT / "ui", ROOT / "setup"]

RETIRED_NAMES = [
    "KICAD_SPECGEN_DIR",
    "KSG_SPECGEN_DIR",
    "KSG_DIR",
    "KSG_WORKSPACE",
    "KSG_SPECGEN_COMMON",
    "kicad_specgen.json",
    "Configure Environments",
    "ConfigureEnvironmentsDialog",
    "fabrication_tab",
    "JS Results",
]


def _scan_sources():
    findings = []
    for src_dir in SOURCE_DIRS:
        for py_file in src_dir.rglob("*.py"):
            text = py_file.read_text(encoding="utf-8", errors="replace")
            for name in RETIRED_NAMES:
                if name in text:
                    findings.append((py_file.relative_to(ROOT), name))
    return findings


def test_no_retired_names_in_source():
    findings = _scan_sources()
    if findings:
        msg = "\n".join(f"  {f}: contains '{n}'" for f, n in findings)
        raise AssertionError(f"Retired names found in source:\n{msg}")
