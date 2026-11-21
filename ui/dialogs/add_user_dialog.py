# v0.1
################################################################################
#  Project   : SpecGen
#  File      : add_user_dialog.py
#  Copyright : (c) 2026 brickChip and Richard Howlett. All rights reserved.
#  Author    : Richard Howlett <rhowlett@eenerd.com>
#  License   : PolyForm Noncommercial 1.0.0. Free for noncommercial use;
#              commercial use requires written permission from the owner.
#              Full terms in LICENSE at the project root.
#  Warranty  : None. Provided as is; the owner is not liable for any
#              damages arising from its use (No Liability, LICENSE).
#  SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
################################################################################

"""add_user_dialog.py — Add or edit a user in kicad_specgen_users.json.

Department and Team are dropdowns referencing company.departments. Selecting a
department repopulates the team dropdown with that department's teams.
"""
from __future__ import annotations
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QComboBox, QCheckBox, QLabel, QDialogButtonBox, QMessageBox,
)

WORKER_TYPES = ["employee", "contractor", "external", "hobby"]


class AddUserDialog(QDialog):
    def __init__(self, app_state, config_service,
                 parent=None, edit_worker_id: str = "") -> None:
        super().__init__(parent)
        self._state          = app_state
        self._cs             = config_service
        self._edit_worker_id = edit_worker_id
        self._mode = "edit" if edit_worker_id else "add"
        self.setWindowTitle("Edit User" if self._mode == "edit" else "Add User")
        self.setMinimumWidth(540)
        self._build_ui()
        if self._mode == "edit":
            self._load_user(edit_worker_id)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form   = QFormLayout()

        self._worker_id  = QLineEdit()
        self._display    = QLineEdit()
        self._preferred  = QLineEdit()
        self._family     = QLineEdit()
        self._email      = QLineEdit()
        self._dept       = QComboBox()
        self._team       = QComboBox()
        self._job_title  = QLineEdit()
        self._wtype      = QComboBox()
        self._wtype.addItems(WORKER_TYPES)
        self._active     = QCheckBox(); self._active.setChecked(True)
        self._admin      = QCheckBox()

        # Populate department dropdown from company config
        company = self._state.company_config
        self._dept.addItem("(none)", "")
        if company:
            for dept_id, dept in sorted(company.departments.items()):
                self._dept.addItem(dept.get("name", dept_id), dept_id)
        self._dept.currentIndexChanged.connect(self._on_dept_changed)
        self._on_dept_changed()  # populate teams for initial selection

        if self._mode == "edit":
            self._worker_id.setReadOnly(True)

        form.addRow("Worker ID *:",    self._worker_id)
        form.addRow("Display Name *:", self._display)
        form.addRow("Preferred Name:", self._preferred)
        form.addRow("Family Name:",    self._family)
        form.addRow("Email:",          self._email)
        form.addRow("Department:",     self._dept)
        form.addRow("Team:",           self._team)
        form.addRow("Job Title:",      self._job_title)
        form.addRow("Worker Type:",    self._wtype)
        form.addRow("Active:",         self._active)
        form.addRow("Admin:",          self._admin)
        layout.addLayout(form)

        self._error = QLabel(); self._error.setVisible(False)
        layout.addWidget(self._error)

        buttons = QDialogButtonBox()
        save = buttons.addButton("Save", QDialogButtonBox.ButtonRole.AcceptRole)
        cancel = buttons.addButton("Cancel", QDialogButtonBox.ButtonRole.RejectRole)
        save.clicked.connect(self._save)
        cancel.clicked.connect(self.reject)
        layout.addWidget(buttons)

    def _on_dept_changed(self) -> None:
        """Repopulate the team dropdown for the selected department."""
        self._team.clear()
        self._team.addItem("(none)", "")
        company = self._state.company_config
        dept_id = self._dept.currentData()
        if company and dept_id:
            dept = company.get_department(dept_id)
            if dept:
                for team_id, team in sorted(dept.get("teams", {}).items()):
                    self._team.addItem(team.get("name", team_id), team_id)

    def _load_user(self, worker_id: str) -> None:
        users = self._state.users_config
        if not users:
            return
        u = users.get_user(worker_id)
        if not u:
            return
        self._worker_id.setText(u.get("worker_id", ""))
        self._display.setText(u.get("display_name", ""))
        self._preferred.setText(u.get("preferred_name", ""))
        self._family.setText(u.get("family_name", ""))
        self._email.setText(u.get("email", ""))
        # Department / team dropdowns
        di = self._dept.findData(u.get("department", ""))
        if di >= 0:
            self._dept.setCurrentIndex(di)
        self._on_dept_changed()
        ti = self._team.findData(u.get("team", ""))
        if ti >= 0:
            self._team.setCurrentIndex(ti)
        self._job_title.setText(u.get("job_title", ""))
        wi = self._wtype.findText(u.get("worker_type", "employee"))
        if wi >= 0:
            self._wtype.setCurrentIndex(wi)
        self._active.setChecked(u.get("active", True))
        self._admin.setChecked(u.get("is_admin", False))

    def _save(self) -> None:
        wid = self._worker_id.text().strip()
        dn  = self._display.text().strip()
        if not wid:
            self._show_error("Worker ID is required."); return
        if not dn:
            self._show_error("Display Name is required."); return
        users = self._state.users_config
        if not users:
            self._show_error("Users config not loaded."); return
        if self._mode == "add" and wid in users.worker_ids:
            self._show_error(f"Worker ID '{wid}' already exists."); return

        new_user = {
            "worker_id":      wid,
            "display_name":   dn,
            "preferred_name": self._preferred.text().strip(),
            "family_name":    self._family.text().strip(),
            "email":          self._email.text().strip(),
            "department":     self._dept.currentData() or "",
            "team":           self._team.currentData() or "",
            "job_title":      self._job_title.text().strip(),
            "worker_type":    self._wtype.currentText(),
            "active":         self._active.isChecked(),
            "is_admin":       self._admin.isChecked(),
            "client_assignments": [],
        }

        if self._mode == "edit":
            # preserve existing client_assignments
            existing = users.get_user(wid) or {}
            new_user["client_assignments"] = existing.get("client_assignments", [])
            users.users = [u if u.get("worker_id") != wid else new_user
                           for u in users.users]
        else:
            users.users.append(new_user)
            # Create the user's folders per the documented convention
            company_dir = ""
            if self._state.local_config:
                company_dir = self._state.local_config.tokens.get("KSG_COMPANY_DIR", "")
            if company_dir:
                from core.specgen_user_config import create_user_folders
                try:
                    create_user_folders(company_dir, wid)
                except Exception:
                    pass

        try:
            self._cs.save_user(users)
            self.accept()
        except Exception as e:
            self._show_error(str(e))

    def _show_error(self, msg: str) -> None:
        self._error.setText(msg)
        self._error.setVisible(True)
