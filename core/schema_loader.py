"""
schema_loader.py — Load and cache JSON Schema validators for SpecGen configs.

The schema files live in the repo-root `schema/` folder (a sibling of core/,
ui/, specification/). This module finds that folder relative to the package,
loads each schema once, caches the compiled validator, and exposes a single
validate() entry point used by the config loaders.

Structural validation only. Semantic rules (e.g. "a writable token must not be
inside KSG_APP_DIR", "a user's team must exist in their department") are NOT
expressible in JSON Schema and remain in core/validators.py.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

log = logging.getLogger(__name__)

# Map a short logical name to its schema filename.
SCHEMA_FILES = {
    "local":   "kicad_specgen_local.schema.json",
    "company": "kicad_specgen_company.schema.json",
    "users":   "kicad_specgen_users.schema.json",
    "project": "specgen_project.schema.json",
    "kicad_common": "kicad_common.schema.json",
}


class SchemaError(Exception):
    """Raised when a config file fails structural schema validation."""

    def __init__(self, schema_name: str, message: str, path: list | None = None):
        self.schema_name = schema_name
        self.field_path = path or []
        super().__init__(message)


def schema_dir() -> Path:
    """Return the absolute path to the repo-root schema/ folder."""
    # core/schema_loader.py -> core/ -> <repo root>/schema
    return Path(__file__).resolve().parent.parent / "schema"


# Caches keyed by schema short-name
_SCHEMA_CACHE: dict[str, dict] = {}
_VALIDATOR_CACHE: dict[str, object] = {}


def load_schema(name: str) -> dict:
    """Load (and cache) the raw schema dict for *name*."""
    if name in _SCHEMA_CACHE:
        return _SCHEMA_CACHE[name]
    if name not in SCHEMA_FILES:
        raise KeyError(f"Unknown schema name: {name!r}")
    path = schema_dir() / SCHEMA_FILES[name]
    if not path.exists():
        raise FileNotFoundError(f"Schema file not found: {path}")
    schema = json.loads(path.read_text())
    _SCHEMA_CACHE[name] = schema
    return schema


def _get_validator(name: str):
    """Return a cached jsonschema Draft7Validator for *name*."""
    if name in _VALIDATOR_CACHE:
        return _VALIDATOR_CACHE[name]
    from jsonschema import Draft7Validator
    validator = Draft7Validator(load_schema(name))
    _VALIDATOR_CACHE[name] = validator
    return validator


def validate(name: str, data: dict) -> None:
    """
    Validate *data* against the named schema. Raises SchemaError on the first
    structural violation. Returns None on success.

    jsonschema must be installed (declared in requirements-stage1.txt). If it
    is somehow unavailable, validation is skipped with a warning rather than
    blocking the load — structural validation is a safety net, not a gate that
    should make the app unusable if the optional dependency is missing.
    """
    try:
        validator = _get_validator(name)
    except ImportError:
        log.warning("jsonschema not installed — skipping structural "
                    "validation of %s config", name)
        return

    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
    if errors:
        first = errors[0]
        raise SchemaError(name, first.message, list(first.path))


def clear_cache() -> None:
    """Clear cached schemas/validators (used by tests)."""
    _SCHEMA_CACHE.clear()
    _VALIDATOR_CACHE.clear()
