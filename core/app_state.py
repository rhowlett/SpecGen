# v0.1
################################################################################
#  Project   : SpecGen
#  File      : app_state.py
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
app_state.py — Observable in-memory application state.

AppState is a plain QObject subclass (NOT @dataclass — metaclass conflict).
UI components NEVER write to app_state fields. Only services do.
UI components connect to signals and read fields read-only.

Instantiated once in app.py, passed by reference to all services and tabs.
"""
from __future__ import annotations
from PySide6.QtCore import QObject, Signal


class AppState(QObject):
    config_reloaded     = Signal()        # after any config load/reload
    tokens_changed      = Signal()        # after token table rebuilt
    dirty_changed       = Signal()        # after any dirty flag changes
    validation_complete = Signal(object)  # payload: ValidationReport
    setup_state_changed = Signal(bool)    # payload: setup_complete bool

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)  # QObject.__init__ MUST be first

        self.local_config    = None   # LocalConfig | None
        self.company_config  = None   # CompanyConfig | None
        self.users_config    = None   # UsersConfig | None
        self.project_config  = None   # ProjectConfig | None  (Stage 2+)

        self.resolved_tokens: dict[str, str] = {}

        self.active_user:        str  = ""
        self.active_environment: str  = ""

        self.dirty_project: bool = False
        self.dirty_local:   bool = False

        self.setup_complete: bool = False

    # ------------------------------------------------------------------
    # Service-facing helpers — set field + emit correct signal
    # ------------------------------------------------------------------

    def set_local_config(self, cfg) -> None:
        self.local_config       = cfg
        self.active_user        = cfg.active_user        if cfg else ""
        self.active_environment = cfg.active_environment if cfg else ""
        self.setup_complete     = cfg.setup_complete     if cfg else False
        self.config_reloaded.emit()
        self.setup_state_changed.emit(self.setup_complete)

    def set_company_config(self, cfg) -> None:
        self.company_config = cfg
        self.config_reloaded.emit()

    def set_users_config(self, cfg) -> None:
        self.users_config = cfg
        self.config_reloaded.emit()

    def set_resolved_tokens(self, tokens: dict[str, str]) -> None:
        self.resolved_tokens = tokens
        self.tokens_changed.emit()

    def set_dirty_local(self, dirty: bool) -> None:
        if self.dirty_local != dirty:
            self.dirty_local = dirty
            self.dirty_changed.emit()

    def set_dirty_project(self, dirty: bool) -> None:
        if self.dirty_project != dirty:
            self.dirty_project = dirty
            self.dirty_changed.emit()
