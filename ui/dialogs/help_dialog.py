"""help_dialog.py — In-app help viewer using QTextBrowser."""
from __future__ import annotations
import logging
from pathlib import Path
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QTextBrowser,
                                QDialogButtonBox)

log = logging.getLogger(__name__)


class HelpDialog(QDialog):
    def __init__(self, help_file: str, title: str,
                 app_dir: str = "", parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"Help — {title}")
        self.setMinimumSize(900, 650)
        self.resize(1000, 700)
        self._app_dir = app_dir
        self._build_ui()
        self._load(help_file)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        self._browser = QTextBrowser()
        self._browser.setOpenExternalLinks(True)
        layout.addWidget(self._browser)
        btn = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        btn.accepted.connect(self.accept)
        layout.addWidget(btn)

    def _load(self, help_file: str) -> None:
        base = Path(self._app_dir) if self._app_dir else Path(__file__).parent.parent.parent
        path = base / help_file
        if path.exists():
            try:
                self._browser.setMarkdown(path.read_text(encoding="utf-8"))
                return
            except Exception as e:
                log.warning("HelpDialog: failed to render %s: %s", path, e)
        self._browser.setPlainText(
            f"Help file not found:\n{help_file}\n\n"
            "This help topic may not be available yet."
        )
