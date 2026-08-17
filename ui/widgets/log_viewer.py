"""
log_viewer.py — Structured log record display widget used by LogsTab.
"""
from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QComboBox, QLabel, QPushButton, QFileDialog, QHeaderView,
)

LEVEL_ORDER = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class LogViewerWidget(QWidget):
    """Displays structured log records with level and source filters."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._records: list[tuple[str, str, str, str]] = []
        self._sources: set[str] = set()
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Filter bar
        bar = QHBoxLayout()
        bar.addWidget(QLabel("Level:"))
        self._level_filter = QComboBox()
        self._level_filter.addItems(
            ["All", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL",
             "WARNING+", "ERROR+"])
        self._level_filter.currentTextChanged.connect(self._apply_filters)
        bar.addWidget(self._level_filter)

        bar.addWidget(QLabel("Source:"))
        self._source_filter = QComboBox()
        self._source_filter.addItem("All")
        self._source_filter.currentTextChanged.connect(self._apply_filters)
        bar.addWidget(self._source_filter)
        bar.addStretch()

        self._btn_clear  = QPushButton("Clear Display")
        self._btn_export = QPushButton("Export Log...")
        self._btn_refresh = QPushButton("Refresh")
        self._btn_clear.clicked.connect(self._clear)
        self._btn_export.clicked.connect(self._export)
        bar.addWidget(self._btn_clear)
        bar.addWidget(self._btn_export)
        bar.addWidget(self._btn_refresh)
        layout.addLayout(bar)

        # Table
        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(["Timestamp", "Level", "Source", "Message"])
        hdr = self._table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setWordWrap(True)
        layout.addWidget(self._table)

        # Footer
        self._footer = QLabel("0 records")
        layout.addWidget(self._footer)

    def append_record(self, timestamp: str, level: str,
                      source: str, message: str) -> None:
        self._records.append((timestamp, level, source, message))
        if source not in self._sources:
            self._sources.add(source)
            self._source_filter.addItem(source)
        self._add_row_if_visible(timestamp, level, source, message)
        self._update_footer()

    def _add_row_if_visible(self, ts: str, level: str,
                             source: str, message: str) -> None:
        if not self._passes_filter(level, source):
            return
        row = self._table.rowCount()
        self._table.insertRow(row)
        for col, text in enumerate((ts, level, source, message)):
            item = QTableWidgetItem(text)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self._table.setItem(row, col, item)

    def _passes_filter(self, level: str, source: str) -> bool:
        lf = self._level_filter.currentText()
        sf = self._source_filter.currentText()
        if sf != "All" and source != sf:
            return False
        if lf == "All":
            return True
        if lf == "WARNING+":
            return level in ("WARNING", "ERROR", "CRITICAL")
        if lf == "ERROR+":
            return level in ("ERROR", "CRITICAL")
        return level == lf

    def _apply_filters(self) -> None:
        self._table.setRowCount(0)
        for record in self._records:
            self._add_row_if_visible(*record)
        self._update_footer()

    def _update_footer(self) -> None:
        shown = self._table.rowCount()
        total = len(self._records)
        lf = self._level_filter.currentText()
        sf = self._source_filter.currentText()
        parts = [f"Showing {shown}" + (f" of {total}" if shown != total else "") + " records"]
        if lf != "All":    parts.append(f"Filter: {lf}")
        if sf != "All":    parts.append(f"Source: {sf}")
        self._footer.setText("  |  ".join(parts))

    def _clear(self) -> None:
        self._table.setRowCount(0)
        self._records.clear()
        from datetime import datetime
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.append_record(ts, "INFO", "app", "Log display cleared by user.")

    def _export(self) -> None:
        from datetime import datetime
        default = f"SpecGen_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        path, _ = QFileDialog.getSaveFileName(self, "Export Log", default,
                                               "Text files (*.txt)")
        if not path:
            return
        lines = [
            f"{ts}  {level:<8}  {src:<24}  {msg}"
            for ts, level, src, msg in self._records
            if self._passes_filter(level, src)
        ]
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
        except OSError as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Export Failed", str(e))
