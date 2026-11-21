# v0.1
################################################################################
#  Project   : SpecGen
#  File      : environments_subtab.py
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
environments_subtab.py — Environments subtab of the Configure tab.

Selects the active user and active environment for this machine. Writes go
through config_service.save_active_session().
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFormLayout, QComboBox, QMessageBox,
)

from ui.tabs.configure.subtab_base import SubtabBase


class EnvironmentsSubtab(SubtabBase):
    TITLE = "Environments"
    ORDER = 30

    def __init__(self, app_state, config_service, validation_service,
                 parent=None) -> None:
        super().__init__(app_state, config_service, validation_service, parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Active session identifiers (stored locally):"))

        form = QFormLayout()
        self._active_user_combo = QComboBox()
        self._active_env_combo  = QComboBox()
        self._active_user_combo.currentIndexChanged.connect(self.mark_dirty)
        self._active_env_combo.currentIndexChanged.connect(self.mark_dirty)
        form.addRow("Active User:",        self._active_user_combo)
        form.addRow("Active Environment:", self._active_env_combo)
        layout.addLayout(form)

        layout.addWidget(QLabel("\nEnvironment definitions (from company config):"))
        self._env_list_label = QLabel("No environments defined.")
        self._env_list_label.setWordWrap(True)
        layout.addWidget(self._env_list_label)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self._btn_save    = QPushButton("Save Environment Changes")
        self._btn_discard = QPushButton("Discard Changes")
        self._btn_save.clicked.connect(self.on_save)
        self._btn_discard.clicked.connect(self.force_populate)
        btn_row.addWidget(self._btn_save)
        btn_row.addWidget(self._btn_discard)
        layout.addLayout(btn_row)
        layout.addStretch()

        self.register_save_button(self._btn_save)

    def populate(self) -> None:
        self._active_user_combo.blockSignals(True)
        self._active_env_combo.blockSignals(True)
        self._active_user_combo.clear()
        self._active_env_combo.clear()

        users   = self._state.users_config
        company = self._state.company_config
        local   = self._state.local_config

        if users:
            for u in users.users:
                self._active_user_combo.addItem(
                    u.get("display_name", u.get("worker_id", "")),
                    u.get("worker_id", ""))
        if company:
            for env_id, e in company.environments.items():
                self._active_env_combo.addItem(
                    e.get("description", env_id) or env_id, env_id)
            self._env_list_label.setText(
                "\n".join(f"• {env_id} ({e.get('type','')})"
                          for env_id, e in company.environments.items())
                or "No environments defined.")
        if local:
            idx = self._active_user_combo.findData(local.active_user)
            if idx >= 0:
                self._active_user_combo.setCurrentIndex(idx)
            idx = self._active_env_combo.findData(local.active_environment)
            if idx >= 0:
                self._active_env_combo.setCurrentIndex(idx)

        self._active_user_combo.blockSignals(False)
        self._active_env_combo.blockSignals(False)

    def on_save(self) -> None:
        user = self._active_user_combo.currentData() or ""
        env  = self._active_env_combo.currentData() or ""
        try:
            self._cs.save_active_session(active_user=user, active_environment=env)
            self.mark_clean()
        except Exception as e:
            QMessageBox.warning(self, "Save Failed", str(e))
