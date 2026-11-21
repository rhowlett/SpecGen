# v0.1
################################################################################
#  Project   : SpecGen
#  File      : specgen_user_config.py
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
specgen_user_config.py — Load/validate/save kicad_specgen_users.json.
Returns typed UsersConfig dataclass. No token resolution. No GUI.
"""
from __future__ import annotations
import logging
from dataclasses import dataclass, field
from pathlib import Path
from core.file_ops import read_json, write_json_atomic
from core.migrations import CURRENT_SCHEMA_VERSION, migrate_users_config

log = logging.getLogger(__name__)


@dataclass
class UsersConfig:
    schema_version: int        = 1
    users:          list[dict] = field(default_factory=list)
    path:           Path | None = field(default=None, repr=False, compare=False)

    def get_user(self, worker_id: str) -> dict | None:
        return next((u for u in self.users if u.get("worker_id") == worker_id), None)

    @property
    def worker_ids(self) -> list[str]:
        return [u.get("worker_id", "") for u in self.users]

    def display_name(self, worker_id: str) -> str:
        u = self.get_user(worker_id)
        return u.get("display_name", worker_id) if u else worker_id


def load(path: Path) -> UsersConfig:
    from core.schema_loader import validate as _schema_validate
    raw = migrate_users_config(read_json(path))
    _schema_validate("users", raw)
    cfg = UsersConfig(
        schema_version = raw.get("schema_version", 1),
        users          = raw.get("users", []),
        path           = Path(path),
    )
    log.info("users config loaded: %s (%d users)", path, len(cfg.users))
    return cfg


def save(config: UsersConfig, path: Path | None = None) -> None:
    target = Path(path) if path else config.path
    if not target:
        raise ValueError("No path for users config save.")
    data = {"schema_version": config.schema_version, "users": config.users}
    write_json_atomic(target, data)
    config.path = target
    log.info("users config saved: %s", target)


def create_empty(path: Path) -> UsersConfig:
    data = {"schema_version": CURRENT_SCHEMA_VERSION, "users": []}
    write_json_atomic(path, data)
    return load(path)


# ---------------------------------------------------------------------------
# User-folder derivation (documented convention)
# ---------------------------------------------------------------------------

def derive_user_dirs(company_dir: str, worker_id: str) -> tuple[str, str]:
    """
    Derive (KSG_USER_SPECGEN_DIR, KSG_USER_COMMON_DIR) from the company dir
    and worker_id using the documented convention:

        {KSG_COMPANY_DIR}/SpecGen/Users/<worker_id>/specgen
        {KSG_COMPANY_DIR}/SpecGen/Users/<worker_id>/common
    """
    base = Path(company_dir) / "SpecGen" / "Users" / worker_id
    return str(base / "specgen"), str(base / "common")


def create_user_folders(company_dir: str, worker_id: str) -> tuple[str, str]:
    """Create the user's specgen/ and common/ folders. Returns the two paths."""
    specgen_dir, common_dir = derive_user_dirs(company_dir, worker_id)
    Path(specgen_dir).mkdir(parents=True, exist_ok=True)
    Path(common_dir).mkdir(parents=True, exist_ok=True)
    log.info("created user folders for %s", worker_id)
    return specgen_dir, common_dir
