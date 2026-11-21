# v0.1
################################################################################
#  Project   : SpecGen
#  File      : validation_subtab.py
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
validation_subtab.py — Validation subtab of the Configure tab.

Read-only: runs configuration validation and shows the results. There is no
save action, so this subtab never becomes dirty.
"""
from __future__ import annotations

from PySide6.QtWidgets import QVBoxLayout

from ui.tabs.configure.subtab_base import SubtabBase
from ui.widgets.validation_panel import ValidationPanel


class ValidationSubtab(SubtabBase):
    TITLE = "Validation"
    ORDER = 50

    def __init__(self, app_state, config_service, validation_service,
                 parent=None) -> None:
        super().__init__(app_state, config_service, validation_service, parent)
        layout = QVBoxLayout(self)
        self._panel = ValidationPanel(app_state, validation_service)
        layout.addWidget(self._panel)

    def populate(self) -> None:
        # Nothing to populate; the panel updates itself on validation_complete.
        pass
