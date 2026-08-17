"""
file_ops.py — Atomic JSON write, timestamped backup, directory utilities.

Must Not Do: No config parsing. No token resolution. No GUI.
"""
from __future__ import annotations
import json, os, shutil
from datetime import datetime
from pathlib import Path


def write_json_atomic(path: Path, data: dict,
                      indent: int = 2, backup: bool = False) -> None:
    """
    Write data as JSON to path atomically via write-to-temp-then-rename.
    backup=True required when writing KiCad-owned files (kicad_common.json).
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.parent / (path.name + ".tmp")
    try:
        tmp.write_text(json.dumps(data, indent=indent, ensure_ascii=False), encoding="utf-8")
        if backup and path.exists():
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            shutil.copy2(path, path.parent / f"{path.stem}.bak_{ts}{path.suffix}")
        os.replace(tmp, path)
    except Exception:
        if tmp.exists():
            try: tmp.unlink()
            except OSError: pass
        raise


def read_json(path: Path) -> dict:
    """Read and parse JSON. Raises FileNotFoundError or json.JSONDecodeError."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def ensure_dir(path: Path) -> Path:
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def path_exists(path: str | Path | None) -> bool:
    return bool(path) and Path(path).exists()
