"""about_dialog.py — About KiCad SpecGen dialog."""
from __future__ import annotations
import os, platform, sys
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout,
                                QLabel, QPushButton, QDialogButtonBox)
try:
    import PySide6
    PYSIDE6_VER = PySide6.__version__
except Exception:
    PYSIDE6_VER = "unknown"

try:
    from __version__ import __version__ as APP_VERSION
except ImportError:
    APP_VERSION = "development"


class AboutDialog(QDialog):
    def __init__(self, app_state, parent=None) -> None:
        super().__init__(parent)
        self._state = app_state
        self.setWindowTitle("About KiCad SpecGen")
        self.setFixedSize(420, 360)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>KiCad SpecGen</h2>"))

        form = QFormLayout()
        form.addRow("Version:",  QLabel(APP_VERSION))
        form.addRow("Python:",   QLabel(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"))
        form.addRow("PySide6:",  QLabel(PYSIDE6_VER))
        form.addRow("Platform:", QLabel(f"{platform.system()} {platform.release()}"))
        layout.addLayout(form)

        layout.addWidget(QLabel("─" * 48))

        local = self._state.local_config
        ksg_app = local.tokens.get("KSG_APP_DIR", "(not set)") if local else "(not set)"
        sys_cfg = local.tokens.get("KSG_SYSTEM_CONFIG_DIR", "(not set)") if local else "(not set)"
        form2 = QFormLayout()
        form2.addRow("KSG_APP_DIR:",          QLabel(ksg_app))
        form2.addRow("Local Config:",         QLabel(sys_cfg))

        # venv status ($SHARED_VENV when set, else KSG_APP_DIR/.venv)
        shared = os.environ.get("SHARED_VENV")
        venv_path = (Path(shared) if shared else
                     Path(ksg_app) / ".venv" if ksg_app != "(not set)" else None)
        venv_active = sys.prefix == str(venv_path) if venv_path else False
        venv_label = f"{venv_path}  {'✓ Active' if venv_active else '⚠ Not active'}"
        form2.addRow(".venv:", QLabel(venv_label))
        layout.addLayout(form2)

        layout.addWidget(QLabel("─" * 48))
        layout.addWidget(QLabel("© 2026 KiCad SpecGen Contributors"))
        layout.addStretch()

        btn = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        btn.accepted.connect(self.accept)
        layout.addWidget(btn)
