"""
validators.py — Config validation returning structured ValidationResult objects.

Must Not Do: No file I/O. No GUI. No side effects.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal
from core.migrations import PROTECTED_TOKENS, REQUIRED_LOCAL_TOKENS

TOKEN_RE = re.compile(r"^KSG_[A-Z0-9_]+$")


# ---------------------------------------------------------------------------
# Result types (also used by validation_service and validation_panel)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ValidationResult:
    check_id: str
    status:   Literal["pass", "warn", "fail"]
    message:  str
    detail:   str | None = None
    source:   str = "config"


@dataclass
class ValidationReport:
    results: list[ValidationResult] = field(default_factory=list)

    @property
    def passed(self)   -> int: return sum(1 for r in self.results if r.status == "pass")
    @property
    def warnings(self) -> int: return sum(1 for r in self.results if r.status == "warn")
    @property
    def failures(self) -> int: return sum(1 for r in self.results if r.status == "fail")
    @property
    def overall(self)  -> Literal["pass", "warn", "fail"]:
        if self.failures: return "fail"
        if self.warnings: return "warn"
        return "pass"


# ---------------------------------------------------------------------------
# Individual validators
# ---------------------------------------------------------------------------

def validate_local_config(cfg, resolved_tokens: dict[str, str]) -> list[ValidationResult]:
    from core.migrations import WRITABLE_SPACE_TOKENS
    results: list[ValidationResult] = []
    R = lambda **kw: results.append(ValidationResult(**kw))

    app_dir = cfg.tokens.get("KSG_APP_DIR", "")

    # Required tokens present
    for tok in REQUIRED_LOCAL_TOKENS:
        val = cfg.tokens.get(tok, "")
        cid = f"token_{tok.lower()}"
        writable = tok in WRITABLE_SPACE_TOKENS

        if not val:
            # Empty writable tokens are "not configured" (warn), not a hard fail —
            # setup intentionally leaves them blank for the user to set via GUI.
            if writable:
                R(check_id=cid, status="warn",
                  message=f"{tok}: not configured",
                  detail="Set this folder in Configure → Local Machine.",
                  source="tokens")
            else:
                R(check_id=cid, status="fail",
                  message=f"{tok}: not set",
                  detail=f"Add {tok} via Edit → Local Tokens...", source="tokens")
            continue

        if not Path(val).is_absolute():
            R(check_id=cid, status="fail",
              message=f"{tok}: value is not an absolute path",
              detail=f"Value: {val}", source="tokens")
            continue

        # Writable-space rule: must not be inside KSG_APP_DIR
        if writable and app_dir and _is_inside(val, app_dir):
            R(check_id=cid, status="fail",
              message=f"{tok}: must not be inside KSG_APP_DIR (read-only)",
              detail=f"{val} is inside the application directory, which is "
                     "read-only. Choose a folder you can write to.",
              source="tokens")
            continue

        if not Path(val).exists():
            R(check_id=cid, status="warn",
              message=f"{tok}: path does not exist on disk",
              detail=f"Path: {val}", source="tokens")
        else:
            R(check_id=cid, status="pass",
              message=f"{tok}: {val}", source="tokens")

    # No protected tokens in local tokens
    for tok in cfg.tokens:
        if tok in PROTECTED_TOKENS:
            R(check_id="protected_token", status="fail",
              message=f"Protected token '{tok}' must not be in local tokens.",
              source="tokens")

    # Token name format
    for tok in cfg.tokens:
        if not TOKEN_RE.match(tok):
            R(check_id=f"token_name_{tok}", status="fail",
              message=f"Token '{tok}' does not match ^KSG_[A-Z0-9_]+$",
              source="tokens")

    # kicad-cli path
    cli = cfg.kicad_cli_path
    if not cli:
        R(check_id="kicad_cli_path", status="warn",
          message="kicad-cli: not configured",
          detail="Use Edit → Configure kicad-cli...", source="kicad")
    elif not Path(cli).exists():
        R(check_id="kicad_cli_path", status="fail",
          message=f"kicad-cli: path not found — {cli}",
          detail="Use Edit → Configure kicad-cli...", source="kicad")
    else:
        R(check_id="kicad_cli_path", status="pass",
          message=f"kicad-cli: {cli}", source="kicad")

    # Theme valid
    theme = cfg.theme
    from core.specgen_local_config import VALID_THEMES
    if theme not in VALID_THEMES:
        R(check_id="theme", status="warn",
          message=f"Unknown theme '{theme}' — falling back to 'dark'",
          source="config")
    else:
        R(check_id="theme", status="pass",
          message=f"theme: {theme}", source="config")

    return results


def _is_inside(path: str, parent: str) -> bool:
    """Return True if *path* is the same as or inside *parent*."""
    try:
        p = Path(path).resolve()
        par = Path(parent).resolve()
        return p == par or par in p.parents
    except (OSError, ValueError):
        return False


def validate_company_config(cfg) -> list[ValidationResult]:
    results: list[ValidationResult] = []
    R = lambda **kw: results.append(ValidationResult(**kw))

    if not cfg:
        R(check_id="company_config", status="fail",
          message="Company config not loaded", source="config")
        return results

    if not cfg.company_name:
        R(check_id="company_name", status="warn",
          message="Company name not set in company config", source="config")
    else:
        R(check_id="company_name", status="pass",
          message=f"company: {cfg.company_name}", source="config")

    # Logo must resolve inside KSG_COMPANY_DIR (token-based check)
    logo = cfg.company_logo
    if logo and "{KSG_COMPANY_DIR}" not in logo:
        R(check_id="company_logo", status="warn",
          message="Company logo should reference {KSG_COMPANY_DIR}",
          detail=f"Value: {logo}", source="config")

    R(check_id="departments", status="pass",
      message=f"{cfg.department_count} department(s), {cfg.team_count} team(s)",
      source="config")

    R(check_id="clients", status="pass",
      message=f"{cfg.client_count} client(s) defined", source="config")

    if not cfg.environments:
        R(check_id="environments", status="warn",
          message="No environments defined — create one in Configure → Environments",
          source="config")
    else:
        R(check_id="environments", status="pass",
          message=f"{len(cfg.environments)} environment(s) defined", source="config")

    return results


def validate_users_config(cfg, active_user: str, company_cfg=None) -> list[ValidationResult]:
    results: list[ValidationResult] = []
    R = lambda **kw: results.append(ValidationResult(**kw))

    if not cfg:
        R(check_id="users_config", status="warn",
          message="Users config not loaded", source="config")
        return results

    if active_user and not cfg.get_user(active_user):
        R(check_id="active_user", status="warn",
          message=f"active_user '{active_user}' not found in users config",
          detail="Update via Configure → Company & User", source="config")
    elif active_user:
        R(check_id="active_user", status="pass",
          message=f"active_user: {cfg.display_name(active_user)}", source="config")
    else:
        R(check_id="active_user", status="warn",
          message="No active user set",
          detail="Set via Configure → Company & User", source="config")

    # Department/team references must exist in company config
    if company_cfg:
        for u in cfg.users:
            wid  = u.get("worker_id", "")
            dept = u.get("department", "")
            team = u.get("team", "")
            if dept and not company_cfg.get_department(dept):
                R(check_id=f"user_dept_{wid}", status="warn",
                  message=f"User {wid}: department '{dept}' not found",
                  source="config")
            elif dept and team and not company_cfg.get_team(dept, team):
                R(check_id=f"user_team_{wid}", status="warn",
                  message=f"User {wid}: team '{team}' not in department '{dept}'",
                  source="config")

    return results
