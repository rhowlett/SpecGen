"""
validation_panel.py — Displays ValidationReport results with ✓ ⚠ ✗ icons.
Connects to app_state.validation_complete signal.
"""
from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton,
)


class ValidationPanel(QWidget):
    def __init__(self, app_state, validation_service, parent=None) -> None:
        super().__init__(parent)
        self._state  = app_state
        self._svc    = validation_service
        self._build_ui()
        app_state.validation_complete.connect(self._on_validation_complete)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        header = QHBoxLayout()
        self._summary = QLabel("Press Run Validation to check your configuration.")
        self._btn_run = QPushButton("Run Validation")
        self._btn_run.clicked.connect(self._run)
        header.addWidget(self._summary)
        header.addStretch()
        header.addWidget(self._btn_run)
        layout.addLayout(header)

        self._table = QTableWidget(0, 3)
        self._table.setHorizontalHeaderLabels(["Status", "Check", "Message"])
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setToolTipDuration(8000)
        layout.addWidget(self._table)

    def _run(self) -> None:
        self._svc.run_config_validation()

    def _on_validation_complete(self, report) -> None:
        self._table.setRowCount(0)
        status_icons = {"pass": "✓", "warn": "⚠", "fail": "✗"}
        for result in report.results:
            row = self._table.rowCount()
            self._table.insertRow(row)
            icon = QTableWidgetItem(status_icons.get(result.status, "?"))
            icon.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            check = QTableWidgetItem(result.check_id)
            msg   = QTableWidgetItem(result.message)
            if result.detail:
                msg.setToolTip(result.detail)
                check.setToolTip(result.detail)
            for item in (icon, check, msg):
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self._table.setItem(row, 0, icon)
            self._table.setItem(row, 1, check)
            self._table.setItem(row, 2, msg)
        overall = report.overall
        icon_map = {"pass": "✓ All checks passed",
                    "warn": f"⚠ {report.warnings} warning(s)",
                    "fail": f"✗ {report.failures} failure(s)"}
        self._summary.setText(
            f"{icon_map.get(overall, '')}  |  "
            f"{report.passed} passed, {report.warnings} warnings, {report.failures} failures"
        )
