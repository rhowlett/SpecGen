# v0.1
################################################################################
#  Project   : SpecGen
#  File      : company_subtab.py
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
company_subtab.py — Company subtab of the Configure tab.

Company identity: name, description, website, logo, and postal address.
Writes go through config_service.save_company().

Split from the former company_user_subtab.py: this file owns only the company
identity section; departments and users live in user_subtab.py.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFormLayout, QLineEdit, QGroupBox, QScrollArea, QMessageBox,
)

from ui.tabs.configure.subtab_base import SubtabBase
from ui.widgets.path_field import PathField

# Minimum width (in characters) for company text inputs. Converted to pixels
# at build time using the field's font metrics so it holds across themes/DPI.
_MIN_INPUT_CHARS = 80


class CompanySubtab(SubtabBase):
    TITLE = "Company"
    ORDER = 20

    def __init__(self, app_state, config_service, validation_service,
                 parent=None) -> None:
        super().__init__(app_state, config_service, validation_service, parent)
        from ui.theme import make_section_heading

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        outer_layout.addWidget(scroll)
        inner = QWidget()
        scroll.setWidget(inner)
        layout = QVBoxLayout(inner)

        layout.addWidget(make_section_heading("Company"))
        company_box = QGroupBox()
        cf = QFormLayout(company_box)
        # Left-align the field labels (Company Name, Description, ...).
        cf.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        cf.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        cf.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)

        self._co_name_edit    = QLineEdit()
        self._co_desc_edit    = QLineEdit()
        self._co_website_edit = QLineEdit()
        for fld in (self._co_name_edit, self._co_desc_edit, self._co_website_edit):
            fld.textChanged.connect(self.mark_dirty)
        cf.addRow("Company Name:", self._co_name_edit)
        cf.addRow("Description:",  self._co_desc_edit)
        cf.addRow("Website:",      self._co_website_edit)

        self._co_logo_field = PathField(
            mode="file", placeholder="Company logo image",
            token_provider=lambda: self._state.resolved_tokens,
            anchor_token="KSG_COMPANY_DIR",
        )
        self._co_logo_field.path_changed.connect(self.mark_dirty)
        self._co_logo_field.anchor_violation.connect(self._warn_logo_outside_company)
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

        # Enforce an 80-character minimum width on every text input.
        self._apply_min_input_width()

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self._btn_save    = QPushButton("Save Company Changes")
        self._btn_discard = QPushButton("Discard Changes")
        self._btn_save.clicked.connect(self.on_save)
        self._btn_discard.clicked.connect(self.force_populate)
        btn_row.addWidget(self._btn_save)
        btn_row.addWidget(self._btn_discard)
        layout.addLayout(btn_row)
        layout.addStretch()

        self.register_save_button(self._btn_save)

    def _apply_min_input_width(self) -> None:
        """Set a minimum width of ~80 characters on all company text inputs."""
        fields = (
            self._co_name_edit, self._co_desc_edit, self._co_website_edit,
            self._addr_street, self._addr_suite, self._addr_city,
            self._addr_state, self._addr_zip, self._addr_country,
        )
        for fld in fields:
            char_w = fld.fontMetrics().averageCharWidth()
            fld.setMinimumWidth(char_w * _MIN_INPUT_CHARS)
        # PathField wraps a QLineEdit; widen the whole field too.
        self._co_logo_field.setMinimumWidth(
            self._co_name_edit.minimumWidth())

    # ------------------------------------------------------------------
    # populate / save
    # ------------------------------------------------------------------

    def populate(self) -> None:
        company = self._state.company_config
        if not company:
            return
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

    def _warn_logo_outside_company(self, selected_path: str) -> None:
        QMessageBox.warning(
            self, "Logo Outside Company Folder",
            "The selected logo is not inside the company folder "
            "(KSG_COMPANY_DIR):\n\n"
            f"{selected_path}\n\n"
            "The company logo should live in the shared company folder so it "
            "resolves for everyone. The path was stored as-is — move the file "
            "into KSG_COMPANY_DIR and re-select it, or set KSG_COMPANY_DIR "
            "first in the Local Machine subtab.")

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
