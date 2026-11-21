# v0.1
################################################################################
#  Project   : SpecGen
#  File      : clients_teams_dialog.py
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
clients_teams_dialog.py — Client/project management.

NOTE: As of the department/team redesign, internal teams are managed inside
the Departments section of the Company & User tab (see department_dialog.py).
Client and project management belongs to the Environments tab work and uses
the company.clients.<client_id>.projects.<project_id> structure. This dialog
is a Stage-2 placeholder until the Environments tab is built.
"""
from __future__ import annotations
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox


class ClientsTeamsDialog(QDialog):
    def __init__(self, app_state=None, config_service=None, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Clients and Projects")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(
            "Internal teams are now managed in the Departments section of the\n"
            "Company & User tab. Client and project management will be available\n"
            "in the Environments tab (Stage 2)."
        ))
        btn = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        btn.rejected.connect(self.reject)
        btn.accepted.connect(self.accept)
        layout.addWidget(btn)
