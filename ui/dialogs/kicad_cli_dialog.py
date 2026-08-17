"""kicad_cli_dialog.py — Configure kicad-cli path and verify version."""
from __future__ import annotations
import subprocess
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QGroupBox,
    QLabel, QPushButton, QHBoxLayout, QDialogButtonBox,
    QFileDialog, QMessageBox,
)
from ui.widgets.path_field import PathField


class KicadCliDialog(QDialog):
    def __init__(self, app_state, config_service, parent=None) -> None:
        super().__init__(parent)
        self._state = app_state
        self._cs    = config_service
        self._verified = False
        self._detected_version = ""
        self.setWindowTitle("Configure kicad-cli")
        self.setMinimumWidth(540)
        self._build_ui()
        self._load_current()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        form = QFormLayout()
        self._path_field = PathField(mode="file", placeholder="Path to kicad-cli executable")
        self._path_field.path_changed.connect(self._on_path_changed)
        self._source_label = QLabel()
        form.addRow("kicad-cli Path:", self._path_field)
        form.addRow("Source:",         self._source_label)
        layout.addLayout(form)

        check_box = QGroupBox("Version Check")
        check_layout = QVBoxLayout(check_box)
        self._version_label = QLabel("(run Check to verify)")
        check_layout.addWidget(self._version_label)
        layout.addWidget(check_box)

        self._warn_label = QLabel()
        self._warn_label.setVisible(False)
        layout.addWidget(self._warn_label)

        btn_row = QHBoxLayout()
        self._btn_check = QPushButton("Check")
        self._btn_check.clicked.connect(self._check)
        btn_row.addWidget(self._btn_check)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        buttons = QDialogButtonBox()
        self._btn_save   = buttons.addButton("Save",   QDialogButtonBox.ButtonRole.AcceptRole)
        self._btn_cancel = buttons.addButton("Cancel", QDialogButtonBox.ButtonRole.RejectRole)
        self._btn_save.clicked.connect(self._save)
        self._btn_cancel.clicked.connect(self.reject)
        layout.addWidget(buttons)

    def _load_current(self) -> None:
        local = self._state.local_config
        if local:
            self._path_field.set_path(local.kicad_cli_path)
            self._source_label.setText(local.tools.get("kicad_cli_source", ""))
            existing_ver = local.tools.get("kicad_version", "")
            if existing_ver:
                self._version_label.setText(f"✓ {existing_ver}")
                self._detected_version = existing_ver
                self._verified = True

    def _on_path_changed(self, _: str) -> None:
        self._verified = False
        self._detected_version = ""
        self._version_label.setText("(run Check to verify)")

    def _check(self) -> None:
        path = self._path_field.path()
        if not path:
            self._version_label.setText("✗ No path entered")
            return
        try:
            result = subprocess.run(
                [path, "--version"],
                capture_output=True, text=True, timeout=10,
            )
            output = (result.stdout + result.stderr).strip()
            if result.returncode == 0:
                self._version_label.setText(f"✓ {output}")
                self._detected_version = self._parse_version(output)
                self._verified = True
            else:
                self._version_label.setText(f"✗ {output or 'Non-zero exit code'}")
                self._verified = False
        except FileNotFoundError:
            self._version_label.setText("✗ File not found")
            self._verified = False
        except Exception as e:
            self._version_label.setText(f"✗ {e}")
            self._verified = False

    @staticmethod
    def _parse_version(output: str) -> str:
        """Extract a version string like '9.0.3' from kicad-cli --version output."""
        import re
        m = re.search(r"\d+\.\d+(?:\.\d+)?", output)
        return m.group(0) if m else output.strip()

    def _save(self) -> None:
        path = self._path_field.path()
        if not path or not Path(path).exists():
            QMessageBox.warning(self, "Invalid Path",
                                "The specified path does not exist on disk.")
            return
        if not self._verified:
            reply = QMessageBox.question(
                self, "Not Verified",
                "The path has not been verified with Check.\nSave anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        self._cs.save_kicad_cli_path(
            path, source="user_configured",
            version=getattr(self, "_detected_version", ""),
        )
        self.accept()
