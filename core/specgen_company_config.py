# v0.1
################################################################################
#  Project   : SpecGen
#  File      : specgen_company_config.py
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
specgen_company_config.py — Load/validate/save kicad_specgen_company.json.
Returns typed CompanyConfig dataclass. No token resolution. No GUI.

Single-company model: company.name is the identifier (no company_id).

Structure:
  company        — name, description, website, address{}, logo
  departments    — { dept_id: { name, teams: { team_id: { name } } } }
  clients        — { client_id: { name, projects: { project_id: { name, status } } } }
  environments   — { env_id: { type, ... } }
"""
from __future__ import annotations
import logging
from dataclasses import dataclass, field
from pathlib import Path
from core.file_ops import read_json, write_json_atomic
from core.migrations import CURRENT_SCHEMA_VERSION, migrate_company_config

log = logging.getLogger(__name__)


@dataclass
class CompanyConfig:
    schema_version: int        = 1
    company:        dict       = field(default_factory=dict)
    departments:    dict       = field(default_factory=dict)  # keyed by dept_id
    clients:        dict       = field(default_factory=dict)  # keyed by client_id
    environments:   dict       = field(default_factory=dict)  # keyed by env_id
    paths:          dict       = field(default_factory=dict)
    templates:      dict       = field(default_factory=dict)
    assets:         dict       = field(default_factory=dict)
    path:           Path | None = field(default=None, repr=False, compare=False)

    # ----- company -----
    @property
    def company_name(self) -> str:
        return self.company.get("name", "")

    @property
    def company_website(self) -> str:
        return self.company.get("website", "")

    @property
    def company_logo(self) -> str:
        return self.company.get("logo", "")

    @property
    def company_address(self) -> dict:
        return self.company.get("address", {})

    # ----- departments / teams -----
    @property
    def department_count(self) -> int:
        return len(self.departments)

    @property
    def team_count(self) -> int:
        return sum(len(d.get("teams", {})) for d in self.departments.values())

    def get_department(self, dept_id: str) -> dict | None:
        return self.departments.get(dept_id)

    def get_team(self, dept_id: str, team_id: str) -> dict | None:
        dept = self.departments.get(dept_id)
        if not dept:
            return None
        return dept.get("teams", {}).get(team_id)

    def department_name(self, dept_id: str) -> str:
        d = self.departments.get(dept_id)
        return d.get("name", dept_id) if d else dept_id

    def team_name(self, dept_id: str, team_id: str) -> str:
        t = self.get_team(dept_id, team_id)
        return t.get("name", team_id) if t else team_id

    # ----- clients / projects -----
    @property
    def client_count(self) -> int:
        return len(self.clients)

    def get_client(self, client_id: str) -> dict | None:
        return self.clients.get(client_id)

    def get_project(self, client_id: str, project_id: str) -> dict | None:
        c = self.clients.get(client_id)
        if not c:
            return None
        return c.get("projects", {}).get(project_id)

    # ----- environments -----
    @property
    def environment_ids(self) -> list[str]:
        return list(self.environments.keys())

    def get_environment(self, env_id: str) -> dict | None:
        return self.environments.get(env_id)


def load(path: Path) -> CompanyConfig:
    """Load and migrate. Raises FileNotFoundError or json.JSONDecodeError."""
    from core.schema_loader import validate as _schema_validate
    raw = migrate_company_config(read_json(path))
    _schema_validate("company", raw)
    cfg = CompanyConfig(
        schema_version = raw.get("schema_version", 1),
        company        = raw.get("company", {}),
        departments    = raw.get("departments", {}),
        clients        = raw.get("clients", {}),
        environments   = raw.get("environments", {}),
        paths          = raw.get("paths", {}),
        templates      = raw.get("templates", {}),
        assets         = raw.get("assets", {}),
        path           = Path(path),
    )
    log.info("company config loaded: %s (company=%s)", path, cfg.company_name)
    return cfg


def save(config: CompanyConfig, path: Path | None = None) -> None:
    target = Path(path) if path else config.path
    if not target:
        raise ValueError("No path for company config save.")
    data = {
        "schema_version": config.schema_version,
        "company":        config.company,
        "departments":    config.departments,
        "clients":        config.clients,
        "environments":   config.environments,
        "paths":          config.paths,
        "templates":      config.templates,
        "assets":         config.assets,
    }
    write_json_atomic(target, data)
    config.path = target
    log.info("company config saved: %s", target)


def create_standalone(path: Path, company_name: str = "My Company") -> CompanyConfig:
    """Create a minimal standalone company config (single-company model)."""
    data = {
        "schema_version": CURRENT_SCHEMA_VERSION,
        "company": {
            "name":        company_name,
            "description": "",
            "website":     "",
            "address":     {},
            "logo":        "",
        },
        "departments": {},
        "clients":     {},
        "environments": {
            "default": {"type": "sandbox", "description": "Default environment"}
        },
        "paths": {}, "templates": {}, "assets": {},
    }
    write_json_atomic(path, data)
    return load(path)
