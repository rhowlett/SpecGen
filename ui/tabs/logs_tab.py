"""
logs_tab.py — Logs workspace tab.

Subscribes to logging_utils.get_qt_handler().record_emitted.
Displays structured session-wide application log records.
"""
from __future__ import annotations
import logging
from PySide6.QtWidgets import QWidget, QVBoxLayout
from ui.widgets.log_viewer import LogViewerWidget

log = logging.getLogger(__name__)


class LogsTab(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        self._viewer = LogViewerWidget()
        layout.addWidget(self._viewer)
        self._connect_handler()
        log.info("LogsTab initialised")

    def _connect_handler(self) -> None:
        try:
            from core.logging_utils import get_qt_handler
            handler = get_qt_handler()
            handler.record_emitted.connect(self._on_record)
            log.debug("LogsTab: connected to QtLogHandler")
        except Exception as e:
            log.warning("LogsTab: could not connect to QtLogHandler: %s", e)

    def _on_record(self, timestamp: str, level: str,
                   source: str, message: str) -> None:
        self._viewer.append_record(timestamp, level, source, message)
