# v0.1
################################################################################
#  Project   : SpecGen
#  File      : preferences_subtab.py
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
preferences_subtab.py — Preferences subtab of the Configure tab.

Selects the active UI theme. Theme changes preview live and are persisted via
config_service.save_preferences().
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton,
    QFormLayout, QComboBox, QGroupBox, QMessageBox,
)

from ui.tabs.configure.subtab_base import SubtabBase


class PreferencesSubtab(SubtabBase):
    TITLE = "Preferences"
    ORDER = 40

    def __init__(self, app_state, config_service, validation_service,
                 parent=None) -> None:
        super().__init__(app_state, config_service, validation_service, parent)
        layout = QVBoxLayout(self)

        theme_box = QGroupBox("Theme")
        tf = QFormLayout(theme_box)
        self._theme_combo = QComboBox()
        self._theme_combo.addItems([
            "system", "light", "dark",
            "engineering_dark", "ion_dark", "ion_light",
        ])
        self._theme_combo.currentTextChanged.connect(self._preview_theme)
        tf.addRow("Active Theme:", self._theme_combo)
        layout.addWidget(theme_box)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self._btn_save    = QPushButton("Save Preferences")
        self._btn_discard = QPushButton("Discard")
        self._btn_save.clicked.connect(self.on_save)
        self._btn_discard.clicked.connect(self.force_populate)
        btn_row.addWidget(self._btn_save)
        btn_row.addWidget(self._btn_discard)
        layout.addLayout(btn_row)
        layout.addStretch()

        self.register_save_button(self._btn_save)

    def populate(self) -> None:
        cfg = self._state.local_config
        if cfg:
            idx = self._theme_combo.findText(cfg.theme)
            if idx >= 0:
                self._theme_combo.blockSignals(True)
                self._theme_combo.setCurrentIndex(idx)
                self._theme_combo.blockSignals(False)

    def _preview_theme(self, theme: str) -> None:
        from ui.theme import apply_theme
        apply_theme(theme)
        self.mark_dirty()

    def select_theme_view(self) -> None:
        """Helper for the View → Theme menu action to focus this subtab."""

    def on_save(self) -> None:
        theme = self._theme_combo.currentText()
        try:
            self._cs.save_preferences(theme)
            self.mark_clean()
        except Exception as e:
            QMessageBox.warning(self, "Save Failed", str(e))
