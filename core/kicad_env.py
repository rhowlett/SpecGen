"""
kicad_env.py — Read environment.vars from kicad_common.json.
No writes during normal operation. No GUI.
"""
from __future__ import annotations
import logging
from pathlib import Path
from core.file_ops import read_json

log = logging.getLogger(__name__)


def load_kicad_vars(kicad_common_dir: Path) -> dict[str, str]:
    """
    Read environment.vars from kicad_common.json.
    Returns empty dict if file absent, vars section missing, or vars is null.
    These provide the lowest-priority token source.
    """
    path = Path(kicad_common_dir) / "kicad_common.json"
    if not path.exists():
        log.debug("kicad_env: kicad_common.json not found at %s", path)
        return {}
    try:
        data = read_json(path)
        # Advisory-only structural check against our PARTIAL read-only schema.
        # KiCad owns this file; we never reject or rewrite it. A mismatch is
        # logged at debug level and otherwise ignored.
        try:
            from core.schema_loader import validate as _schema_validate, SchemaError
            _schema_validate("kicad_common", data)
        except SchemaError as se:
            log.debug("kicad_env: kicad_common.json does not match partial "
                      "schema (advisory only): %s", se)
        except Exception:
            pass
        env   = data.get("environment") or {}
        vars_ = env.get("vars") or {}   # guard: vars can be null in KiCad 10+
        if not isinstance(vars_, dict):
            log.debug("kicad_env: vars is not a dict (%s) — skipping", type(vars_))
            return {}
        log.debug("kicad_env: loaded %d vars from %s", len(vars_), path)
        return {str(k): str(v) for k, v in vars_.items()}
    except Exception as e:
        log.warning("kicad_env: failed to read %s: %s", path, e)
        return {}
