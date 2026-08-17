"""
config_service.py — All writes to local/company/user config files.

All file writes go through this service. Dialogs and UI call config_service
methods; config_service handles file_ops, state update, and signal emission.
If the underlying save implementation changes, only this service needs updating.
"""
from __future__ import annotations
import logging
from datetime import datetime, timezone
from pathlib import Path

import core.specgen_local_config as local_mod
import core.specgen_company_config as company_mod
import core.specgen_user_config as users_mod
from core.token_resolver import build_token_table
from core.kicad_env import load_kicad_vars

log = logging.getLogger(__name__)


class ConfigService:
    def __init__(self, app_state) -> None:
        self._state = app_state

    # ------------------------------------------------------------------
    # Bootstrap / full reload
    # ------------------------------------------------------------------

    def load_all(self, local_path: Path) -> None:
        """
        Load local → company → users configs in correct order.
        Updates app_state and rebuilds token table.
        Called at startup and after Refresh.
        """
        # Local
        local_cfg = local_mod.load(local_path)
        self._state.set_local_config(local_cfg)

        # Company
        company_dir = Path(local_cfg.tokens.get("KSG_COMPANY_DIR", ""))
        company_path = company_dir / "SpecGen" / "kicad_specgen_company.json"
        if company_path.exists():
            company_cfg = company_mod.load(company_path)
            self._state.set_company_config(company_cfg)
        else:
            log.warning("Company config not found: %s", company_path)

        # Users
        users_path = company_dir / "SpecGen" / "kicad_specgen_users.json"
        if users_path.exists():
            users_cfg = users_mod.load(users_path)
            self._state.set_users_config(users_cfg)
        else:
            log.warning("Users config not found: %s", users_path)

        self._rebuild_tokens()

    # ------------------------------------------------------------------
    # Token operations
    # ------------------------------------------------------------------

    def save_local_tokens(self, new_tokens: dict[str, str]) -> None:
        """Write new KSG_* token dict to kicad_specgen_local.json."""
        cfg = self._state.local_config
        if not cfg:
            raise RuntimeError("Local config not loaded.")
        cfg.tokens = new_tokens
        local_mod.save(cfg)
        reloaded = local_mod.load(cfg.path)
        self._state.set_local_config(reloaded)
        self._state.set_dirty_local(False)
        self._rebuild_tokens()
        log.info("config_service: local tokens saved")

    def save_skipped_tokens(self, skipped: list[str]) -> None:
        cfg = self._state.local_config
        if not cfg:
            raise RuntimeError("Local config not loaded.")
        cfg.skipped_tokens = skipped
        local_mod.save(cfg)
        self._state.set_dirty_local(False)
        log.info("config_service: skipped_tokens saved (%d)", len(skipped))

    # ------------------------------------------------------------------
    # Tool / kicad-cli operations
    # ------------------------------------------------------------------

    def save_kicad_cli_path(self, cli_path: str, source: str = "user_configured",
                            version: str = "") -> None:
        cfg = self._state.local_config
        if not cfg:
            raise RuntimeError("Local config not loaded.")
        cfg.tools["kicad_cli"]        = cli_path
        cfg.tools["kicad_cli_source"] = source
        if version:
            cfg.tools["kicad_version"] = version
        local_mod.save(cfg)
        reloaded = local_mod.load(cfg.path)
        self._state.set_local_config(reloaded)
        self._state.set_dirty_local(False)
        log.info("config_service: kicad-cli path saved: %s", cli_path)

    # ------------------------------------------------------------------
    # Session / preferences
    # ------------------------------------------------------------------

    def save_active_session(self, active_user: str = "",
                            active_environment: str = "") -> None:
        cfg = self._state.local_config
        if not cfg:
            raise RuntimeError("Local config not loaded.")
        if active_user:
            cfg.active_user = active_user
        if active_environment:
            cfg.active_environment = active_environment
        local_mod.save(cfg)
        self._state.active_user        = cfg.active_user
        self._state.active_environment = cfg.active_environment
        self._state.set_dirty_local(False)

    def save_preferences(self, theme: str) -> None:
        cfg = self._state.local_config
        if not cfg:
            raise RuntimeError("Local config not loaded.")
        cfg.preferences["theme"] = theme
        local_mod.save(cfg)
        self._state.set_dirty_local(False)
        log.info("config_service: preferences saved (theme=%s)", theme)

    def save_session(self, geometry: dict, project_ref: dict | None = None) -> None:
        """
        Called from main_window.closeEvent() to persist last_session.
        geometry: {x, y, width, height}
        project_ref: {specgen_project, project_name, display_name,
                      kicad_project_dir, last_opened_at}
        """
        cfg = self._state.local_config
        if not cfg:
            return
        session = dict(project_ref or {})
        session["window_geometry"] = geometry
        if "last_opened_at" not in session:
            session["last_opened_at"] = datetime.now(timezone.utc).isoformat()
        cfg.last_session = session
        local_mod.save(cfg)
        log.info("config_service: last_session saved")

    # ------------------------------------------------------------------
    # Company / user operations
    # ------------------------------------------------------------------

    def save_company(self, company_cfg) -> None:
        """Write updated company config to disk and refresh state."""
        company_mod.save(company_cfg)
        reloaded = company_mod.load(company_cfg.path)
        self._state.set_company_config(reloaded)
        self._state.set_dirty_local(False)
        log.info("config_service: company config saved")

    def save_user(self, users_cfg) -> None:
        """Write updated users config to disk and refresh state."""
        users_mod.save(users_cfg)
        reloaded = users_mod.load(users_cfg.path)
        self._state.set_users_config(reloaded)
        self._state.set_dirty_local(False)
        log.info("config_service: users config saved")

    # ------------------------------------------------------------------
    # Project token reference removal (Stage 1 stub; move to project_service in Stage 2)
    # ------------------------------------------------------------------

    def remove_project_token_ref(self, token_name: str) -> None:
        """
        Remove a token reference from the open project file.
        Stage 1 stub — MissingTokensDialog is a Stage 2 full implementation.
        Move to project_service.remove_token_ref() in Stage 2.
        """
        log.warning(
            "remove_project_token_ref('%s') called — stub in Stage 1, "
            "no project file is open.", token_name
        )

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _rebuild_tokens(self) -> None:
        local_cfg   = self._state.local_config
        company_cfg = self._state.company_config
        users_cfg   = self._state.users_config

        kicad_vars: dict[str, str] = {}
        if local_cfg:
            sys_cfg_dir = local_cfg.tokens.get("KSG_SYSTEM_CONFIG_DIR", "")
            if sys_cfg_dir:
                kicad_vars = load_kicad_vars(Path(sys_cfg_dir))

        table = build_token_table(
            local_tokens   = local_cfg.tokens if local_cfg else {},
            kicad_vars     = kicad_vars,
            company_paths  = company_cfg.paths if company_cfg else {},
            user_paths     = {},
        )
        self._state.set_resolved_tokens(table)
        log.debug("config_service: token table rebuilt (%d tokens)", len(table))
