# v0.1
################################################################################
#  Project   : SpecGen
#  File      : new_project_dialog.py
#  Copyright : (c) 2026 brickChip and Richard Howlett. All rights reserved.
#  Author    : Richard Howlett <rhowlett@eenerd.com>
#  License   : PolyForm Noncommercial 1.0.0. Free for noncommercial use;
#              commercial use requires written permission from the owner.
#              Full terms in LICENSE at the project root.
#  Warranty  : None. Provided as is; the owner is not liable for any
#              damages arising from its use (No Liability, LICENSE).
#  SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
################################################################################

"""new_project_dialog.py — Stage 1 stub; full implementation in Stage 2."""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox


class NewProjectDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("New SpecGen Project")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(
            "New project creation will be available in Stage 2.\n\n"
            "To open an existing project, use File → Open SpecGen Project..."
        ))
        btn = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        btn.rejected.connect(self.reject)
        layout.addWidget(btn)
