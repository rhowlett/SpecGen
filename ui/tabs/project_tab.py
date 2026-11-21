# v0.1
################################################################################
#  Project   : SpecGen
#  File      : project_tab.py
#  Copyright : (c) 2026 brickChip and Richard Howlett. All rights reserved.
#  Author    : Richard Howlett <rhowlett@eenerd.com>
#  License   : PolyForm Noncommercial 1.0.0. Free for noncommercial use;
#              commercial use requires written permission from the owner.
#              Full terms in LICENSE at the project root.
#  Warranty  : None. Provided as is; the owner is not liable for any
#              damages arising from its use (No Liability, LICENSE).
#  SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
################################################################################

"""project_tab.py — Placeholder for Stage 2."""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class ProjectTab(QWidget):
    def __init__(self, app_state=None, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(
            "This workspace will be available in Stage 2."
        ))
