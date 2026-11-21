# v0.1
################################################################################
#  Project   : SpecGen
#  File      : company_user_subtab.py
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
company_user_subtab.py — Company & User subtab of the Configure tab.

Three sections: Company identity, Departments (tree + dialogs), Users (table).
Company writes go through config_service.save_company(). Department and user
edits open their own dialogs, which save immediately and then trigger a
populate() here.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFormLayout, QLineEdit, QGroupBox, QScrollArea,
    QTreeWidget, QTreeWidgetItem, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox,
)

from ui.tabs.configure.subtab_base import SubtabBase
from ui.widgets.path_field import PathField


class CompanyUserSubtab(SubtabBase):
    TITLE = "Company & User"
    ORDER = 20

    def __init__(self, app_state, config_service, validation_service,
                 parent=None) -> None:
        super().__init__(app_state, config_service, validation_service, parent)
        from ui.theme import make_section_heading

        # This subtab scrolls (it is tall), so its own layout holds a scroll area.
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        outer_layout.addWidget(scroll)
        inner = QWidget()
        scroll.setWidget(inner)
        layout = QVBoxLayout(inner)

        # ---- Company section ----
        layout.addWidget(make_section_heading("Company"))
        company_box = QGroupBox()
        cf = QFormLayout(company_box)
        self._co_name_edit    = QLineEdit()
        self._co_desc_edit    = QLineEdit()
        self._co_website_edit = QLineEdit()
        for fld in (self._co_name_edit, self._co_desc_edit, self._co_website_edit):
            fld.textChanged.connect(self.mark_dirty)
        cf.addRow("Company Name:", self._co_name_edit)
        cf.addRow("Description:",  self._co_desc_edit)
        cf.addRow("Website:",      self._co_website_edit)

        self._co_logo_field = PathField(mode="file", placeholder="Company logo image")
        self._co_logo_field.path_changed.connect(self.mark_dirty)
        cf.addRow("Logo:", self._co_logo_field)

        self._addr_street  = QLineEdit()
        self._addr_suite   = QLineEdit()
        self._addr_city    = QLineEdit()
        self._addr_state   = QLineEdit()
        self._addr_zip     = QLineEdit()
        self._addr_country = QLineEdit()
        for fld in (self._addr_street, self._addr_suite, self._addr_city,
                    self._addr_state, self._addr_zip, self._addr_country):
            fld.textChanged.connect(self.mark_dirty)
        cf.addRow("Street:",  self._addr_street)
        cf.addRow("Suite:",   self._addr_suite)
        cf.addRow("City:",    self._addr_city)
        cf.addRow("State:",   self._addr_state)
        cf.addRow("ZIP:",     self._addr_zip)
        cf.addRow("Country:", self._addr_country)
        layout.addWidget(company_box)

        # ---- Departments section ----
        layout.addWidget(make_section_heading("Departments"))
        self._dept_count_label = QLabel("0 department(s), 0 team(s) defined")
        layout.addWidget(self._dept_count_label)
        self._dept_tree = QTreeWidget()
        self._dept_tree.setHeaderLabels(["Department / Team", "Users"])
        self._dept_tree.setMinimumHeight(160)
        layout.addWidget(self._dept_tree)
        dept_btns = QHBoxLayout()
        self._btn_add_dept    = QPushButton("Add Department")
        self._btn_edit_dept   = QPushButton("Edit Selected Department")
        self._btn_remove_dept = QPushButton("Remove Selected Department")
        self._btn_add_dept.clicked.connect(self._add_department)
        self._btn_edit_dept.clicked.connect(self._edit_department)
        self._btn_remove_dept.clicked.connect(self._remove_department)
        dept_btns.addWidget(self._btn_add_dept)
        dept_btns.addWidget(self._btn_edit_dept)
        dept_btns.addWidget(self._btn_remove_dept)
        dept_btns.addStretch()
        layout.addLayout(dept_btns)

        # ---- Users section ----
        layout.addWidget(make_section_heading("Users"))
        self._users_count_label = QLabel("0 user(s) defined")
        layout.addWidget(self._users_count_label)
        self._users_table = QTableWidget(0, 7)
        self._users_table.setHorizontalHeaderLabels([
            "Worker ID", "Department", "Team", "Job Title",
            "Display Name", "Preferred + Family", "Worker Type",
        ])
        self._users_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._users_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows)
        self._users_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents)
        self._users_table.setMinimumHeight(160)
        layout.addWidget(self._users_table)
        user_btns = QHBoxLayout()
        self._btn_add_user  = QPushButton("Add User")
        self._btn_edit_user = QPushButton("Edit Selected User")
        self._btn_add_user.clicked.connect(self._open_add_user_dialog)
        self._btn_edit_user.clicked.connect(self._edit_selected_user)
        user_btns.addWidget(self._btn_add_user)
        user_btns.addWidget(self._btn_edit_user)
        user_btns.addStretch()
        layout.addLayout(user_btns)

        # ---- Save / Discard ----
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self._btn_save    = QPushButton("Save Company/User Changes")
        self._btn_discard = QPushButton("Discard Changes")
        self._btn_save.clicked.connect(self.on_save)
        self._btn_discard.clicked.connect(self.force_populate)
        btn_row.addWidget(self._btn_save)
        btn_row.addWidget(self._btn_discard)
        layout.addLayout(btn_row)
        layout.addStretch()

        self.register_save_button(self._btn_save)

    # ------------------------------------------------------------------
    # populate / save
    # ------------------------------------------------------------------

    def populate(self) -> None:
        company = self._state.company_config
        users   = self._state.users_config

        if company:
            for fld, val in (
                (self._co_name_edit,    company.company_name),
                (self._co_desc_edit,    company.company.get("description", "")),
                (self._co_website_edit, company.company_website),
            ):
                fld.blockSignals(True); fld.setText(val); fld.blockSignals(False)
            self._co_logo_field.set_path(company.company_logo)
            addr = company.company_address
            for fld, key in (
                (self._addr_street, "street1"), (self._addr_suite, "suite"),
                (self._addr_city, "city"), (self._addr_state, "state"),
                (self._addr_zip, "zip"), (self._addr_country, "country"),
            ):
                fld.blockSignals(True); fld.setText(addr.get(key, "")); fld.blockSignals(False)

        # Department tree
        self._dept_tree.clear()
        if company:
            user_list = users.users if users else []
            for dept_id, dept in sorted(company.departments.items()):
                d_item = QTreeWidgetItem([dept.get("name", dept_id), ""])
                d_item.setData(0, Qt.ItemDataRole.UserRole, ("dept", dept_id))
                teams = dept.get("teams", {})
                for team_id, team in sorted(teams.items()):
                    n_users = sum(1 for u in user_list
                                  if u.get("department") == dept_id
                                  and u.get("team") == team_id)
                    t_item = QTreeWidgetItem(
                        [f"  {team.get('name', team_id)}", str(n_users)])
                    t_item.setData(0, Qt.ItemDataRole.UserRole,
                                   ("team", dept_id, team_id))
                    d_item.addChild(t_item)
                self._dept_tree.addTopLevelItem(d_item)
                if len(teams) <= 1:
                    d_item.setExpanded(True)
            self._dept_count_label.setText(
                f"{company.department_count} department(s), "
                f"{company.team_count} team(s) defined")

        # Users table (sorted dept -> team -> family name)
        self._users_table.setRowCount(0)
        if users:
            def _sort_key(u):
                return (u.get("department", ""), u.get("team", ""),
                        u.get("family_name", ""))
            for u in sorted(users.users, key=_sort_key):
                row = self._users_table.rowCount()
                self._users_table.insertRow(row)
                dept_name = company.department_name(u.get("department", "")) if company else u.get("department", "")
                team_name = company.team_name(u.get("department", ""), u.get("team", "")) if company else u.get("team", "")
                pref_fam = f"{u.get('preferred_name','')} {u.get('family_name','')}".strip()
                cells = [
                    u.get("worker_id", ""), dept_name, team_name,
                    u.get("job_title", ""), u.get("display_name", ""),
                    pref_fam, u.get("worker_type", ""),
                ]
                for col, text in enumerate(cells):
                    item = QTableWidgetItem(text)
                    if col == 0:
                        item.setData(Qt.ItemDataRole.UserRole, u.get("worker_id", ""))
                    self._users_table.setItem(row, col, item)
            self._users_count_label.setText(f"{len(users.users)} user(s) defined")
        else:
            self._users_count_label.setText("0 user(s) defined")

    def on_save(self) -> None:
        company = self._state.company_config
        if not company:
            return
        company.company["name"]        = self._co_name_edit.text().strip()
        company.company["description"] = self._co_desc_edit.text().strip()
        company.company["website"]     = self._co_website_edit.text().strip()
        company.company["logo"]        = self._co_logo_field.path().strip()
        company.company["address"] = {
            "street1": self._addr_street.text().strip(),
            "suite":   self._addr_suite.text().strip(),
            "city":    self._addr_city.text().strip(),
            "state":   self._addr_state.text().strip(),
            "zip":     self._addr_zip.text().strip(),
            "country": self._addr_country.text().strip(),
        }
        try:
            self._cs.save_company(company)
            self.mark_clean()
        except Exception as e:
            QMessageBox.warning(self, "Save Failed", str(e))

    # ------------------------------------------------------------------
    # Department / user dialog handlers
    # ------------------------------------------------------------------

    def _add_department(self) -> None:
        from ui.dialogs.department_dialog import DepartmentDialog
        if not self._state.company_config:
            return
        if DepartmentDialog(self._state, self._cs, self).exec():
            self.populate()

    def _edit_department(self) -> None:
        from ui.dialogs.department_dialog import DepartmentDialog
        item = self._dept_tree.currentItem()
        if not item:
            return
        data = item.data(0, Qt.ItemDataRole.UserRole)
        dept_id = data[1] if data else None
        if not dept_id:
            return
        if DepartmentDialog(self._state, self._cs, self, dept_id=dept_id).exec():
            self.populate()

    def _remove_department(self) -> None:
        item = self._dept_tree.currentItem()
        if not item:
            return
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data or data[0] != "dept":
            QMessageBox.information(self, "Select a Department",
                                    "Select a department (not a team) to remove.")
            return
        dept_id = data[1]
        company = self._state.company_config
        users   = self._state.users_config
        assigned = [u for u in (users.users if users else [])
                    if u.get("department") == dept_id]
        if assigned:
            names = ", ".join(u.get("display_name", u.get("worker_id","")) for u in assigned)
            QMessageBox.warning(
                self, "Cannot Remove Department",
                f"This department has assigned users:\n\n{names}\n\n"
                "Reassign these users to a new department and team before "
                "removing this department.")
            return
        if QMessageBox.question(
                self, "Remove Department",
                f"Remove department '{company.department_name(dept_id)}'?"
        ) == QMessageBox.StandardButton.Yes:
            company.departments.pop(dept_id, None)
            self._cs.save_company(company)
            self.populate()

    def _open_add_user_dialog(self) -> None:
        from ui.dialogs.add_user_dialog import AddUserDialog
        AddUserDialog(self._state, self._cs, self).exec()
        self.populate()

    def _edit_selected_user(self) -> None:
        row = self._users_table.currentRow()
        if row < 0:
            return
        item = self._users_table.item(row, 0)
        worker_id = item.data(Qt.ItemDataRole.UserRole) if item else None
        if not worker_id:
            return
        from ui.dialogs.add_user_dialog import AddUserDialog
        AddUserDialog(self._state, self._cs, self, edit_worker_id=worker_id).exec()
        self.populate()
