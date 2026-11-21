# v0.1
################################################################################
#  Project   : SpecGen
#  File      : department_dialog.py
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
department_dialog.py — Add/edit a department and manage its teams.

A department contains teams keyed by team_id. Teams can be added, renamed,
and removed. Removing a team or department that has assigned users prompts to
reassign those users first (handled at the tab level for departments; team
removal warns here).
"""
from __future__ import annotations
import re
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QListWidget, QListWidgetItem, QPushButton, QLabel, QInputDialog,
    QDialogButtonBox, QMessageBox,
)


def _slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "_", text.strip().lower()).strip("_")
    return s or "item"


class DepartmentDialog(QDialog):
    def __init__(self, app_state, config_service, parent=None,
                 dept_id: str | None = None) -> None:
        super().__init__(parent)
        self._state = app_state
        self._cs    = config_service
        self._dept_id = dept_id
        self._mode = "edit" if dept_id else "add"
        self.setWindowTitle("Edit Department" if dept_id else "Add Department")
        self.setMinimumWidth(480)
        # Work on a copy of the teams dict
        company = app_state.company_config
        if dept_id and company:
            dept = company.get_department(dept_id) or {}
            self._name = dept.get("name", "")
            self._teams = {k: dict(v) for k, v in dept.get("teams", {}).items()}
        else:
            self._name = ""
            self._teams = {}
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self._name_edit = QLineEdit(self._name)
        form.addRow("Department Name:", self._name_edit)
        layout.addLayout(form)

        layout.addWidget(QLabel("Teams:"))
        self._team_list = QListWidget()
        self._refresh_team_list()
        layout.addWidget(self._team_list)

        team_btns = QHBoxLayout()
        self._btn_add_team    = QPushButton("Add Team")
        self._btn_rename_team = QPushButton("Rename Team")
        self._btn_remove_team = QPushButton("Remove Team")
        self._btn_add_team.clicked.connect(self._add_team)
        self._btn_rename_team.clicked.connect(self._rename_team)
        self._btn_remove_team.clicked.connect(self._remove_team)
        team_btns.addWidget(self._btn_add_team)
        team_btns.addWidget(self._btn_rename_team)
        team_btns.addWidget(self._btn_remove_team)
        team_btns.addStretch()
        layout.addLayout(team_btns)

        buttons = QDialogButtonBox()
        save = buttons.addButton("Save", QDialogButtonBox.ButtonRole.AcceptRole)
        cancel = buttons.addButton("Cancel", QDialogButtonBox.ButtonRole.RejectRole)
        save.clicked.connect(self._save)
        cancel.clicked.connect(self.reject)
        layout.addWidget(buttons)

    def _refresh_team_list(self) -> None:
        self._team_list.clear()
        for team_id, team in sorted(self._teams.items()):
            item = QListWidgetItem(f"{team.get('name', team_id)}  [{team_id}]")
            item.setData(Qt.ItemDataRole.UserRole, team_id)
            self._team_list.addItem(item)

    def _selected_team_id(self) -> str | None:
        item = self._team_list.currentItem()
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    def _add_team(self) -> None:
        name, ok = QInputDialog.getText(self, "Add Team", "Team name:")
        if not ok or not name.strip():
            return
        team_id = _slugify(name)
        base = team_id; n = 2
        while team_id in self._teams:
            team_id = f"{base}_{n}"; n += 1
        self._teams[team_id] = {"name": name.strip()}
        self._refresh_team_list()

    def _rename_team(self) -> None:
        team_id = self._selected_team_id()
        if not team_id:
            return
        current = self._teams[team_id].get("name", team_id)
        name, ok = QInputDialog.getText(self, "Rename Team", "Team name:", text=current)
        if not ok or not name.strip():
            return
        # Rename changes the display name only; team_id (and user refs) stay stable
        self._teams[team_id]["name"] = name.strip()
        self._refresh_team_list()

    def _remove_team(self) -> None:
        team_id = self._selected_team_id()
        if not team_id or not self._dept_id:
            if team_id:
                self._teams.pop(team_id, None)
                self._refresh_team_list()
            return
        # Check for users assigned to this dept+team
        users = self._state.users_config
        assigned = [u for u in (users.users if users else [])
                    if u.get("department") == self._dept_id
                    and u.get("team") == team_id]
        if assigned:
            names = ", ".join(u.get("display_name", u.get("worker_id","")) for u in assigned)
            QMessageBox.warning(
                self, "Cannot Remove Team",
                f"This team has assigned users:\n\n{names}\n\n"
                "Reassign these users to another team before removing this team.")
            return
        self._teams.pop(team_id, None)
        self._refresh_team_list()

    def _save(self) -> None:
        name = self._name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Name Required", "Department name is required.")
            return
        company = self._state.company_config
        if not company:
            self.reject(); return

        dept_id = self._dept_id or _slugify(name)
        if not self._dept_id:
            base = dept_id; n = 2
            while dept_id in company.departments:
                dept_id = f"{base}_{n}"; n += 1

        company.departments[dept_id] = {"name": name, "teams": self._teams}
        try:
            self._cs.save_company(company)
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Save Failed", str(e))
