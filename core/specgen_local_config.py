"""
specgen_local_config.py — Load/validate/save kicad_specgen_local.json.
Returns typed LocalConfig dataclass. No token resolution. No GUI.
"""
from __future__ import annotations
import logging, re
from dataclasses import dataclass, field
from pathlib import Path
from core.file_ops import read_json, write_json_atomic
from core.migrations import (CURRENT_SCHEMA_VERSION, PROTECTED_TOKENS,
                              REQUIRED_LOCAL_TOKENS, migrate_local_config)

log = logging.getLogger(__name__)
TOKEN_RE = re.compile(r"^KSG_[A-Z0-9_]+$")
VALID_THEMES = {"system","light","dark","engineering_dark","ion_dark","ion_light"}


@dataclass
class LocalConfig:
    schema_version:     int            = 1
    active_user:        str            = ""
    active_environment: str            = ""
    tools:              dict           = field(default_factory=dict)
    tokens:             dict[str, str] = field(default_factory=dict)
    setup:              dict           = field(default_factory=dict)
    last_session:       dict           = field(default_factory=dict)
    recent_projects:    list[dict]     = field(default_factory=list)
    skipped_tokens:     list[str]      = field(default_factory=list)
    preferences:        dict           = field(default_factory=lambda: {"theme": "dark"})
    path:               Path | None    = field(default=None, repr=False, compare=False)

    @property
    def setup_complete(self) -> bool:
        return bool(self.setup.get("setup_complete", False))

    @property
    def theme(self) -> str:
        return self.preferences.get("theme", "dark")

    @property
    def kicad_cli_path(self) -> str:
        return self.tools.get("kicad_cli", "")


def load(path: Path) -> LocalConfig:
    """
    Load, migrate, and structurally validate kicad_specgen_local.json.

    Raises FileNotFoundError, json.JSONDecodeError, or
    core.schema_loader.SchemaError (structural validation failure).
    """
    from core.schema_loader import validate as _schema_validate
    raw = migrate_local_config(read_json(path))
    _schema_validate("local", raw)
    cfg = LocalConfig(
        schema_version     = raw.get("schema_version", 1),
        active_user        = raw.get("active_user", ""),
        active_environment = raw.get("active_environment", ""),
        tools              = raw.get("tools", {}),
        tokens             = raw.get("tokens", {}),
        setup              = raw.get("setup", {}),
        last_session       = raw.get("last_session", {}),
        recent_projects    = raw.get("recent_projects", []),
        skipped_tokens     = raw.get("skipped_tokens", []),
        preferences        = raw.get("preferences", {"theme": "dark"}),
        path               = Path(path),
    )
    log.info("local config loaded: %s", path)
    return cfg


def save(config: LocalConfig, path: Path | None = None) -> None:
    target = Path(path) if path else config.path
    if not target:
        raise ValueError("No path for local config save.")
    data = {
        "schema_version": config.schema_version,
        "active_user": config.active_user,
        "active_environment": config.active_environment,
        "tools": config.tools,
        "tokens": config.tokens,
        "setup": config.setup,
        "last_session": config.last_session,
        "recent_projects": config.recent_projects,
        "skipped_tokens": config.skipped_tokens,
        "preferences": config.preferences,
    }
    write_json_atomic(target, data)
    config.path = target
    log.info("local config saved: %s", target)


def create_minimal(path: Path, ksg_app_dir: str, ksg_system_config_dir: str,
                   ksg_company_dir: str, platform: str = "unknown") -> LocalConfig:
    """
    Bootstrap a fresh kicad_specgen_local.json during setup.

    Auto-detected tokens (APP_DIR, SYSTEM_CONFIG_DIR, COMPANY_DIR) are
    populated. The four writable-space tokens are left empty — the user
    configures them via the Configure tab. APP_DIR is read-only, so writable
    tokens must never default to a location inside it.
    """
    data = {
        "schema_version": CURRENT_SCHEMA_VERSION,
        "active_user": "", "active_environment": "",
        "tools": {},
        "tokens": {
            "KSG_APP_DIR":            ksg_app_dir,
            "KSG_SYSTEM_CONFIG_DIR":  ksg_system_config_dir,
            "KSG_COMPANY_DIR":        ksg_company_dir,
            "KSG_COMPANY_SPECGEN_DIR": "",
            "KSG_COMPANY_COMMON_DIR":  "",
            "KSG_USER_SPECGEN_DIR":    "",
            "KSG_USER_COMMON_DIR":     "",
        },
        "setup": {"setup_complete": False, "last_setup_platform": platform,
                  "dependency_stage": "stage1"},
        "last_session": {}, "recent_projects": [],
        "skipped_tokens": [], "preferences": {"theme": "dark"},
    }
    write_json_atomic(path, data)
    return load(path)


def validate_token_names(tokens: dict) -> list[str]:
    errors = []
    for name in tokens:
        if not TOKEN_RE.match(name):
            errors.append(f"Token '{name}' must match ^KSG_[A-Z0-9_]+$")
        if name in PROTECTED_TOKENS:
            errors.append(f"Token '{name}' is a protected runtime token.")
    return errors


def missing_required_tokens(tokens: dict) -> list[str]:
    return [t for t in REQUIRED_LOCAL_TOKENS if not tokens.get(t)]
