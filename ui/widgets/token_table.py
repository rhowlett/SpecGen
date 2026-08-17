"""
token_table.py — Reusable token table widget.

Two modes: read-only (Configure subtab display) and edit (LocalTokensDialog).
"""
from __future__ import annotations
import re
from pathlib import Path
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QFileDialog, QLabel,
)

TOKEN_RE = re.compile(r"^KSG_[A-Z0-9_]+$")

REQUIRED_TOKENS = {
    "KSG_APP_DIR", "KSG_SYSTEM_CONFIG_DIR", "KSG_COMPANY_DIR",
    "KSG_COMPANY_SPECGEN_DIR", "KSG_COMPANY_COMMON_DIR",
    "KSG_USER_SPECGEN_DIR", "KSG_USER_COMMON_DIR",
}

WRITABLE_SPACE_TOKENS = {
    "KSG_COMPANY_SPECGEN_DIR", "KSG_COMPANY_COMMON_DIR",
    "KSG_USER_SPECGEN_DIR", "KSG_USER_COMMON_DIR",
}

from core.migrations import PROTECTED_TOKENS


class TokenTableWidget(QWidget):
    """Displays and optionally edits KSG_* tokens."""

    tokens_changed = Signal(dict)  # emitted when tokens are modified in edit mode

    def __init__(self, edit_mode: bool = False, parent=None) -> None:
        super().__init__(parent)
        self._edit_mode = edit_mode
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._table = QTableWidget(0, 3)
        self._table.setHorizontalHeaderLabels(["Token", "Value", "Status"])
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(
            QTableWidget.EditTrigger.DoubleClicked if self._edit_mode
            else QTableWidget.EditTrigger.NoEditTriggers
        )
        layout.addWidget(self._table)

        if self._edit_mode:
            btn_layout = QHBoxLayout()
            self._btn_add    = QPushButton("Add Token")
            self._btn_remove = QPushButton("Remove Selected")
            self._btn_browse = QPushButton("Choose Folder")
            self._btn_add.clicked.connect(self._add_token)
            self._btn_remove.clicked.connect(self._remove_selected)
            self._btn_browse.clicked.connect(self._browse_selected)
            btn_layout.addWidget(self._btn_add)
            btn_layout.addWidget(self._btn_remove)
            btn_layout.addWidget(self._btn_browse)
            btn_layout.addStretch()
            layout.addLayout(btn_layout)
            self._table.cellChanged.connect(self._on_cell_changed)

    def set_tokens(self, tokens: dict[str, str]) -> None:
        self._table.blockSignals(True)
        self._table.setRowCount(0)
        for name, value in sorted(tokens.items()):
            row = self._table.rowCount()
            self._table.insertRow(row)
            label = f"{'★ ' if name in REQUIRED_TOKENS else ''}{name}"
            name_item = QTableWidgetItem(label)
            name_item.setData(Qt.ItemDataRole.UserRole, name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            value_item = QTableWidgetItem(value)
            status = self._check_status(name, value)
            status_item = QTableWidgetItem(status)
            status_item.setFlags(status_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self._table.setItem(row, 0, name_item)
            self._table.setItem(row, 1, value_item)
            self._table.setItem(row, 2, status_item)
        self._table.blockSignals(False)

    def get_tokens(self) -> dict[str, str]:
        result = {}
        for row in range(self._table.rowCount()):
            name_item  = self._table.item(row, 0)
            value_item = self._table.item(row, 1)
            if name_item and value_item:
                name = name_item.data(Qt.ItemDataRole.UserRole) or name_item.text().lstrip("★ ")
                result[name] = value_item.text()
        return result

    def _app_dir(self) -> str:
        """Return the current KSG_APP_DIR value from the table, if any."""
        for row in range(self._table.rowCount()):
            name_item = self._table.item(row, 0)
            value_item = self._table.item(row, 1)
            if name_item and value_item:
                name = name_item.data(Qt.ItemDataRole.UserRole) or ""
                if name == "KSG_APP_DIR":
                    return value_item.text()
        return ""

    def _check_status(self, token_name: str, value: str) -> str:
        """
        Status icon for a token row:
          ✗ empty/invalid   ⚠ not found / not configured   ✓ exists
        Writable-space tokens inside KSG_APP_DIR are invalid (✗).
        """
        if not value:
            # Empty writable tokens are "not configured" (⚠), others are ✗
            return "⚠" if token_name in WRITABLE_SPACE_TOKENS else "✗"
        if token_name in WRITABLE_SPACE_TOKENS:
            app_dir = self._app_dir()
            if app_dir and self._is_inside(value, app_dir):
                return "✗"   # inside read-only APP_DIR — invalid
        if not Path(value).exists():
            return "⚠"
        return "✓"

    @staticmethod
    def _is_inside(path: str, parent: str) -> bool:
        try:
            p = Path(path).resolve()
            par = Path(parent).resolve()
            return p == par or par in p.parents
        except (OSError, ValueError):
            return False

    def _add_token(self) -> None:
        row = self._table.rowCount()
        self._table.insertRow(row)
        name_item   = QTableWidgetItem("KSG_NEW_TOKEN")
        name_item.setData(Qt.ItemDataRole.UserRole, "KSG_NEW_TOKEN")
        value_item  = QTableWidgetItem("")
        status_item = QTableWidgetItem("✗")
        status_item.setFlags(status_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self._table.setItem(row, 0, name_item)
        self._table.setItem(row, 1, value_item)
        self._table.setItem(row, 2, status_item)
        self._table.editItem(value_item)

    def _remove_selected(self) -> None:
        selected = self._table.selectedItems()
        if not selected:
            return
        row = self._table.currentRow()
        name_item = self._table.item(row, 0)
        if name_item:
            name = name_item.data(Qt.ItemDataRole.UserRole) or name_item.text()
            if name.lstrip("★ ") in REQUIRED_TOKENS:
                return  # cannot remove required tokens
        self._table.removeRow(row)
        self.tokens_changed.emit(self.get_tokens())

    def _browse_selected(self) -> None:
        row = self._table.currentRow()
        if row < 0:
            return
        value_item = self._table.item(row, 1)
        # Seed the dialog with the current value if it is a usable folder
        seed = ""
        if value_item and value_item.text():
            current = Path(value_item.text())
            if current.is_dir():
                seed = str(current)
            elif current.parent.is_dir():
                seed = str(current.parent)
        folder = QFileDialog.getExistingDirectory(self, "Choose Folder", seed)
        if folder and value_item:
            value_item.setText(folder)

    def _on_cell_changed(self, row: int, col: int) -> None:
        if col == 1:
            name_item   = self._table.item(row, 0)
            value_item  = self._table.item(row, 1)
            status_item = self._table.item(row, 2)
            if value_item and status_item:
                name = name_item.data(Qt.ItemDataRole.UserRole) if name_item else ""
                status_item.setText(self._check_status(name, value_item.text()))
        self.tokens_changed.emit(self.get_tokens())
