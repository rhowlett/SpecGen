# v0.1
################################################################################
#  Project   : SpecGen
#  File      : missing_tokens_dialog.py
#  Copyright : (c) 2026 brickChip and Richard Howlett. All rights reserved.
#  Author    : Richard Howlett <rhowlett@eenerd.com>
#  License   : PolyForm Noncommercial 1.0.0. Free for noncommercial use;
#              commercial use requires written permission from the owner.
#              Full terms in LICENSE at the project root.
#  Warranty  : None. Provided as is; the owner is not liable for any
#              damages arising from its use (No Liability, LICENSE).
#  SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
################################################################################

"""missing_tokens_dialog.py — Stage 1 stub; full implementation in Stage 2."""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox


class MissingTokensDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Missing Tokens")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(
            "Token resolution requires an open project.\n"
            "Open a project to use this feature."
        ))
        btn = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        btn.rejected.connect(self.reject)
        layout.addWidget(btn)
